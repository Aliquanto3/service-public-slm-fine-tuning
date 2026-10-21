"""Régularisation KL vers la base (auto-distillation, story 16.6a).

Perte = entropie croisée + `kl_base` × KL(élève ‖ base), par token de réponse (même masque
que le SFT : labels différents de `IGNORE`, décalés d'une position comme la perte causale).
La distribution de la base vient du même modèle, adaptateur désactivé (`disable_adapter` de
PEFT) et sans gradient : aucune copie des poids. Avec `kl_temperature` = T, les deux
distributions sont adoucies par T et la KL est multipliée par T² (convention de Hinton :
l'ordre de grandeur du gradient ne dépend pas de T).

La KL est normalisée comme l'entropie croisée du `Trainer` : par `num_items_in_batch` (tokens
de réponse de tout le pas d'accumulation) quand le modèle le reçoit, sinon par les tokens du
micro-lot (le `Trainer` divise alors la perte par le nombre de micro-lots). L'entropie croisée
et la KL, moyennées par token, sont journalisées à chaque `log` de l'entraînement
(`metriques.jsonl`, événement `perte`). `kl_base = 0` n'utilise jamais ce module
(`methodes.creer_entraineur`).

Mémoire (revue 16.6a) : les logits pleins (longueur × vocabulaire) ne sont jamais
matérialisés. L'entropie croisée reste celle du `SFTTrainer` (`chunked_nll` par défaut, comme
sans KL). La KL part des états cachés du dernier bloc : ceux de l'élève sont capturés pendant
la passe de l'entropie croisée (crochet sur le tronc), ceux de la base viennent d'une passe du
seul tronc, sans `lm_head`. Elle se calcule par tranches de `TAILLE_TRANCHE` tokens de réponse,
chaque tranche sous `torch.utils.checkpoint` (logits recalculés au backward), comme
`chunked_nll` de TRL.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, Final

from slmsp.train.masque import IGNORE

Journal = Callable[[Mapping[str, Any]], None]

TAILLE_TRANCHE: Final = 256
"""Tokens de réponse par tranche de KL (valeur de `chunked_nll` de TRL) : pic transitoire de
quelques tenseurs `TAILLE_TRANCHE` × vocabulaire en float32 (~134 Mo chacun à 130 k)."""

CLES_HORS_TRONC: Final = frozenset({"labels", "shift_labels", "num_items_in_batch"})
"""Entrées du `compute_loss` que la passe du tronc de la base ne reçoit pas."""


def somme_kl(
    torch: Any, logits: Any, logits_base: Any, labels: Any, *, temperature: float = 1.0
) -> tuple[Any, int]:
    """Somme de KL(élève ‖ base) sur les tokens de réponse, et nombre de ces tokens.

    Position t des logits → label t + 1 (décalage causal) ; seules les positions dont le label
    n'est pas `IGNORE` comptent. Calcul en float32 sur ces seules positions. Référence non
    découpée de `somme_kl_par_tranches` (tests) : l'entraîneur n'a jamais les logits pleins.
    """
    masque = labels[..., 1:] != IGNORE
    eleve = logits[..., :-1, :][masque].float() / temperature
    base = logits_base[..., :-1, :][masque].float() / temperature
    log_p = torch.log_softmax(eleve, dim=-1)
    log_q = torch.log_softmax(base, dim=-1)
    kl = torch.nn.functional.kl_div(log_q, log_p, log_target=True, reduction="sum")
    return kl * (temperature**2), int(masque.sum())


def projection_logits(torch: Any, modele: Any) -> Callable[[Any], Any]:
    """États cachés (N, H) → logits float32 (N, V) du modèle causal `modele` (sans PEFT) :
    son propre `lm_head`, puis les mises à l'échelle de sa configuration (`logit_scale` ou
    `output_multiplier`, puis `final_logit_softcapping`, ordre de TRL) ; `logits_scaling`
    (Granite) divise les logits comme le `forward` du modèle."""
    tete = modele.get_output_embeddings()
    config = modele.config
    if hasattr(config, "get_text_config"):
        config = config.get_text_config()
    echelle = getattr(config, "logit_scale", None)
    if echelle is None:
        echelle = getattr(config, "output_multiplier", None)
    echelle = 1.0 if echelle is None else float(echelle)
    division = getattr(config, "logits_scaling", None)
    division = 1.0 if division is None else float(division)
    plafond = getattr(config, "final_logit_softcapping", None)

    def projeter(etats: Any) -> Any:
        logits = tete(etats).float()
        if echelle != 1.0:
            logits = logits * echelle
        if division != 1.0:
            logits = logits / division
        if plafond is not None:
            logits = plafond * torch.tanh(logits / plafond)
        return logits

    return projeter


def somme_kl_par_tranches(
    torch: Any,
    etats: Any,
    etats_base: Any,
    labels: Any,
    projeter: Callable[[Any], Any],
    *,
    temperature: float = 1.0,
    taille: int = TAILLE_TRANCHE,
) -> tuple[Any, int]:
    """Même somme que `somme_kl`, depuis les états cachés (B, S, H) de l'élève et de la base :
    positions de réponse seules, `taille` tokens par tranche, chaque tranche sous
    `torch.utils.checkpoint` (ses logits ne vivent que pendant sa passe avant ou arrière)."""
    masque = labels[..., 1:] != IGNORE
    n = int(masque.sum())
    if n == 0:
        return etats.new_zeros((), dtype=torch.float32), 0
    eleve = etats[..., :-1, :][masque]
    base = etats_base[..., :-1, :][masque].detach()

    def tranche(h: Any, hb: Any) -> Any:
        log_p = torch.log_softmax(projeter(h) / temperature, dim=-1)
        with torch.no_grad():
            log_q = torch.log_softmax(projeter(hb) / temperature, dim=-1)
        return torch.nn.functional.kl_div(log_q, log_p, log_target=True, reduction="sum")

    somme = etats.new_zeros((), dtype=torch.float32)
    for debut in range(0, n, taille):
        fin = debut + taille
        somme = somme + torch.utils.checkpoint.checkpoint(
            tranche, eleve[debut:fin], base[debut:fin], use_reentrant=False
        )
    return somme * (temperature**2), n


def modele_causal(modele: Any) -> Any:
    """Modèle causal nu sous l'enveloppe PEFT (`get_base_model`), s'il y en a une."""
    return modele.get_base_model() if hasattr(modele, "get_base_model") else modele


def classe_entraineur_kl(base: type, torch: Any) -> type:
    """Sous-classe de `base` (`SFTTrainer`) dont la perte ajoute le terme KL vers la base."""

    class EntraineurKL(base):  # type: ignore[misc, valid-type]
        def __init__(
            self,
            *args: Any,
            kl_base: float,
            kl_temperature: float = 1.0,
            journal: Journal | None = None,
            **kwargs: Any,
        ) -> None:
            super().__init__(*args, **kwargs)
            self.kl_base, self.kl_temperature, self._journal = kl_base, kl_temperature, journal
            self._lots_kl: list[tuple[float, float]] = []

        def _deballer(self, model: Any) -> Any:
            accelerateur = getattr(self, "accelerator", None)
            return accelerateur.unwrap_model(model) if accelerateur is not None else model

        def compute_loss(
            self,
            model: Any,
            inputs: dict[str, Any],
            return_outputs: bool = False,
            num_items_in_batch: Any = None,
        ) -> Any:
            labels = inputs["labels"]
            entrees = {c: v for c, v in inputs.items() if c not in CLES_HORS_TRONC}
            peft = self._deballer(model)
            causal = modele_causal(peft)
            tronc = causal.base_model  # décodeur sans `lm_head` (le tronc de `chunked_nll`)
            captures: list[Any] = []

            def capturer(_module: Any, _args: Any, sortie: Any) -> None:
                captures.append(sortie[0])

            crochet = tronc.register_forward_hook(capturer)
            try:
                perte_ce, sorties = super().compute_loss(
                    model, inputs, return_outputs=True, num_items_in_batch=num_items_in_batch
                )
            finally:
                crochet.remove()
            if len(captures) != 1:
                raise RuntimeError(
                    f"KL vers la base : {len(captures)} passe(s) du tronc pendant l'entropie "
                    "croisée, une attendue"
                )
            with torch.no_grad(), peft.disable_adapter():
                etats_base = tronc(**{**entrees, "use_cache": False})[0]
            somme, n = somme_kl_par_tranches(
                torch,
                captures[0],
                etats_base,
                labels,
                projection_logits(torch, causal),
                temperature=self.kl_temperature,
            )
            del etats_base
            captures.clear()
            par_pas = bool(getattr(self, "model_accepts_loss_kwargs", False))
            denominateur = num_items_in_batch if par_pas and num_items_in_batch is not None else n
            denominateur = max(float(denominateur), 1.0)
            perte = perte_ce + self.kl_base * (somme / denominateur)
            if n > 0 and bool(getattr(self.model, "training", True)):  # pas l'évaluation
                self._lots_kl.append(
                    (float(perte_ce.detach()) * denominateur / n, float(somme.detach()) / n)
                )
            return (perte, sorties) if return_outputs else perte

        def log(self, logs: dict[str, float], *args: Any, **kwargs: Any) -> None:
            if self._lots_kl and "loss" in logs:
                ce = sum(c for c, _ in self._lots_kl) / len(self._lots_kl)
                kl = sum(k for _, k in self._lots_kl) / len(self._lots_kl)
                self._lots_kl.clear()
                logs = {**logs, "entropie_croisee": ce, "kl": kl}
                if self._journal is not None:
                    etat = getattr(self, "state", None)
                    self._journal(
                        {
                            "evenement": "perte",
                            "pas": int(getattr(etat, "global_step", 0)),
                            "perte": float(logs["loss"]),
                            "entropie_croisee": ce,
                            "kl": kl,
                            "kl_base": self.kl_base,
                        }
                    )
            super().log(logs, *args, **kwargs)

    return EntraineurKL
