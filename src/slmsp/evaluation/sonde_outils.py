"""Sonde de tool calling par modèle (H-TOOLS, story 8.2) : run `eval-sonde`.

`sonder("base:<slug>")` passe les items RD-001 et RD-002 du calibrage (R-001 et R-002 de
H-TOOLS) par le Harnais d'évaluation de la phase génération (`generation.generer_item`,
Bac à sable sur les cassettes, `ModeFixe` connecté, profil réseau `aucun`, décodage de la
section `[generation]` de `config/evaluation.toml`), d'abord avec le protocole d'outils
`natif`. Si ce protocole échoue, une passe suivante relance les mêmes items en
`json-generique`, puis en `balises-tool-call` (ordre de `PROTOCOLES`), avec un Harnais rouvert
à chaque passe. Le
protocole est imposé sur une copie de la configuration du modèle : aucun TOML n'est réécrit.

Critère de validité d'un protocole : chaque item sondé a le statut `ok`, au moins un appel
attendu apparié (`controles.controle_rd`) et aucun appel non conforme (évènements
`appel-non-conforme` de la trace). Le taux d'appels valides (Σ `appels_valides` ÷
Σ `appels_attendus`) départage les protocoles quand aucun n'est valide (égalité : `natif`).

Fichiers du run : `sonde.jsonl` (une ligne par protocole × item) et `recommandation.json`
(bilan par protocole, protocole recommandé). Statut final : `complet`, `partiel-erreur`
(au moins un item en erreur) ou `interrompu` (exception hors item, relancée). Pas de reprise :
la sonde est courte et se relance.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Iterable, Sequence
from contextlib import ExitStack
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from slmsp.core.artefacts import Run, nouveau_run
from slmsp.core.canonique import json_canonique
from slmsp.core.items import VERSION_CALIBRAGE, ItemBase, ItemRD, Jeu, lire_jeu
from slmsp.core.schemas.generation import Generation
from slmsp.core.var import verrou_gpu
from slmsp.evaluation import config as cfg
from slmsp.evaluation.assemblage import (
    PROFIL_RESEAU,
    HarnaisEvaluation,
    ouvrir_harnais,
    sans_reseau,
)
from slmsp.evaluation.controles import controle_rd
from slmsp.evaluation.generation import (
    Fabrique,
    _entrees,
    _racine,
    _selection,
    _verifier_jeu,
    generer_item,
)
from slmsp.evaluation.modele_ref import ModeleResolu, resoudre
from slmsp.inference.client import PROTOCOLES
from slmsp.inference.serveur import VARIANTES

TYPE_RUN: Final = "eval-sonde"
FICHIER_SONDE: Final = "sonde.jsonl"
FICHIER_RECOMMANDATION: Final = "recommandation.json"
ITEMS_SONDE: Final = ("RD-001", "RD-002")
"""Items RD du calibrage sondés par défaut (R-001 et R-002 de H-TOOLS)."""
QUANTIFICATION: Final = "q4_k_m"
CRITERE: Final = (
    "chaque item : statut ok, au moins un appel attendu apparié, aucun appel non conforme"
)
TYPE_APPEL: Final = "appel-outil"
TYPE_NON_CONFORME: Final = "appel-non-conforme"

Rapporteur = Callable[[dict[str, Any], int, int], None]
"""`rapporter(ligne, rang, total)` après l'écriture de chaque ligne de `sonde.jsonl`
(rang à partir de 1 dans la passe du protocole)."""


@dataclass
class BilanProtocole:
    """Bilan d'une passe : effectifs, taux et verdict du protocole."""

    protocole: str
    items: int = 0
    items_valides: int = 0
    erreurs: int = 0
    non_conformes: int = 0
    appels_attendus: int = 0
    appels_valides: int = 0
    chat_template_sha256: str | None = None
    serveur: dict[str, Any] | None = None

    @property
    def taux_appels_valides(self) -> float | None:
        if not self.appels_attendus:
            return None
        return self.appels_valides / self.appels_attendus

    @property
    def valide(self) -> bool:
        return self.items > 0 and self.items_valides == self.items

    def ajouter(self, ligne: dict[str, Any]) -> None:
        self.items += 1
        self.items_valides += bool(ligne["valide"])
        self.erreurs += ligne["statut"] != "ok"
        self.non_conformes += ligne["non_conformes"]
        self.appels_attendus += ligne["appels_attendus"]
        self.appels_valides += ligne["appels_valides"]

    def vers_dict(self) -> dict[str, Any]:
        return {
            "items": self.items,
            "items_valides": self.items_valides,
            "taux_items_valides": self.items_valides / self.items if self.items else None,
            "appels_attendus": self.appels_attendus,
            "appels_valides": self.appels_valides,
            "taux_appels_valides": self.taux_appels_valides,
            "non_conformes": self.non_conformes,
            "erreurs": self.erreurs,
            "valide": self.valide,
            "verdict": "valide" if self.valide else "invalide",
            "chat_template_sha256": self.chat_template_sha256,
            "serveur": self.serveur,
        }


@dataclass
class RapportSonde:
    """Bilan de la sonde : run, passes, protocole recommandé et statut final."""

    run: Run
    bilans: dict[str, BilanProtocole] = field(default_factory=dict)
    protocole_recommande: str | None = None
    valide: bool = False
    motif: str | None = None
    statut: str = "en_cours"
    connexions_bloquees: list[str] = field(default_factory=list)


# --- Un item ----------------------------------------------------------------------------------


def _appels_produits(generation: Generation) -> list[dict[str, Any]]:
    """Appels de la trace, dans l'ordre : valides (arguments) et non conformes (bruts)."""
    produits: list[dict[str, Any]] = []
    for evenement in generation.trace:
        if evenement.get("type") == TYPE_APPEL:
            produits.append(
                {"nom": evenement["nom"], "arguments": evenement["arguments"], "conforme": True}
            )
        elif evenement.get("type") == TYPE_NON_CONFORME:
            produits.append(
                {
                    "nom": evenement["nom"],
                    "arguments_bruts": evenement["arguments_bruts"],
                    "motif": evenement["motif"],
                    "conforme": False,
                }
            )
    return produits


def evaluer(item: ItemRD, generation: Generation, protocole: str) -> dict[str, Any]:
    """Ligne de `sonde.jsonl` : appels produits, appariement (`controle_rd`) et validité."""
    produits = _appels_produits(generation)
    non_conformes = sum(1 for appel in produits if not appel["conforme"])
    controle = controle_rd(item, generation)
    valide = generation.statut == "ok" and non_conformes == 0 and controle["appels_valides"] >= 1
    return {
        "protocole": protocole,
        "item_id": item.id,
        "statut": generation.statut,
        "appels_produits": produits,
        "non_conformes": non_conformes,
        "appels_attendus": controle["appels_attendus"],
        "appels_valides": controle["appels_valides"],
        "appariement": controle["appariement"],
        "valide": valide,
        "duree_ms": generation.duree_ms,
        "generation": generation.model_dump(mode="json"),
    }


# --- Sonde ------------------------------------------------------------------------------------


def _selection_rd(jeu: Jeu, items: Iterable[str] | None) -> list[ItemRD]:
    selection = _selection(jeu, ITEMS_SONDE if items is None else items)
    autres = [item.id for item in selection if not isinstance(item, ItemRD)]
    if autres:
        raise ValueError(f"item(s) hors Recherche de données : {', '.join(autres)}")
    return [item for item in selection if isinstance(item, ItemRD)]


def _avec_protocole(modele: ModeleResolu, protocole: str) -> ModeleResolu:
    config = modele.config.model_copy(update={"protocole_outils": protocole})
    return dataclasses.replace(modele, config=config)


def recommander(bilans: dict[str, BilanProtocole]) -> tuple[str | None, bool, str | None]:
    """(protocole recommandé, valide, motif) : premier protocole valide dans l'ordre de
    `PROTOCOLES`, sinon le meilleur taux d'appels valides (égalité : le premier)."""
    sondes = [bilans[p] for p in PROTOCOLES if p in bilans]
    if not sondes:
        return None, False, "aucun protocole sondé"
    for bilan in sondes:
        if bilan.valide:
            return bilan.protocole, True, None
    meilleur = max(sondes, key=lambda b: b.taux_appels_valides or 0.0)  # max garde le 1er
    details = " ; ".join(
        f"{b.protocole} : {b.items_valides}/{b.items} item(s) valide(s), "
        f"{b.appels_valides}/{b.appels_attendus} appel(s) valide(s), "
        f"{b.non_conformes} non conforme(s), {b.erreurs} en erreur"
        for b in sondes
    )
    return meilleur.protocole, False, f"aucun protocole valide ({details}) : meilleur taux retenu"


def _nouveau_run(
    harnais: HarnaisEvaluation,
    jeu: Jeu,
    selection: Sequence[ItemBase],
    modele: ModeleResolu,
    variante: str,
    racine: Path,
    reglages: cfg.ConfigGeneration,
) -> Run:
    config = {
        "phase": "sonde-outils",
        "critere": CRITERE,
        "protocoles": list(PROTOCOLES),
        "protocole_toml": modele.config.protocole_outils,
        "options_llm": reglages.options_llm(),
        "items": [item.id for item in selection],
        "serveur": harnais.description,
        "chat_template_force": modele.config.chat_template_force,
        "profil_reseau": PROFIL_RESEAU,
    }
    return nouveau_run(
        TYPE_RUN,
        modele.slug_run,
        config,
        entrees=_entrees(jeu, modele, racine),
        graine=reglages.graine,
        racine=racine,
        modele_ref=modele.ref,
        quantification=modele.quantification,
        variante_llamacpp=variante,
        llamacpp_tag=harnais.llamacpp_tag,
        chat_template_sha256=harnais.chat_template_sha256,
        jeu_version=jeu.version,
        index_version=harnais.index_version,
    )


def sonder(
    modele_ref: str,
    *,
    jeu: str = VERSION_CALIBRAGE,
    items: Iterable[str] | None = None,
    variante: str = "cpu",
    racine: str | Path | None = None,
    fabrique: Fabrique = ouvrir_harnais,
    rapporter: Rapporteur | None = None,
    config: cfg.ConfigEvaluation | None = None,
) -> RapportSonde:
    """Sonde le tool calling de `modele_ref` (`base:<slug>`) : voir le module.

    `config` : réglages de `config/evaluation.toml` (défaut : lus dans le projet).
    Lève `ValueError` (usage : référence, variante, item inconnu ou hors RD) avant tout
    run, `ManifesteInvalide` (jeu gelé altéré), `ConfigurationInvalide` (modèle,
    `evaluation.toml`), `RessourceOccupee` (GPU).
    """
    base = _racine(racine)
    if variante not in VARIANTES:
        raise ValueError(f"variante inconnue : {variante!r} (attendu : {', '.join(VARIANTES)})")
    if not isinstance(modele_ref, str) or not modele_ref.startswith(("base:", "ft:")):
        raise ValueError(
            f"référence de modèle invalide : {modele_ref!r} "
            "(la sonde porte sur base:<slug> ou ft:<export_run_id>, story 10.6)"
        )
    _verifier_jeu(jeu, base)
    reglages = (config if config is not None else cfg.charger_evaluation()).generation
    options = reglages.options_llm()
    jeu_lu = lire_jeu(jeu, base)
    selection = _selection_rd(jeu_lu, items)
    modele = resoudre(modele_ref, QUANTIFICATION, racine=base)
    with ExitStack() as pile:
        if variante == "cuda":
            pile.enter_context(verrou_gpu(commande=f"slmsp eval sonde-outils {modele.ref} (cuda)"))
        rapport: RapportSonde | None = None
        try:
            for protocole in PROTOCOLES:
                with fabrique(_avec_protocole(modele, protocole), variante, base) as harnais:
                    if rapport is None:
                        rapport = RapportSonde(
                            run=_nouveau_run(
                                harnais, jeu_lu, selection, modele, variante, base, reglages
                            )
                        )
                    bilan = BilanProtocole(
                        protocole,
                        chat_template_sha256=harnais.chat_template_sha256,
                        serveur=harnais.description,
                    )
                    rapport.bilans[protocole] = bilan
                    with sans_reseau() as bloquees:
                        for rang, item in enumerate(selection, start=1):
                            generation = generer_item(harnais, jeu_lu, item, options)
                            ligne = evaluer(item, generation, protocole)
                            rapport.run.ajouter_jsonl(FICHIER_SONDE, ligne)
                            bilan.ajouter(ligne)
                            if rapporter is not None:
                                rapporter(ligne, rang, len(selection))
                    rapport.connexions_bloquees.extend(bloquees)
                if bilan.valide:
                    break
            if rapport is None:  # PROTOCOLES n'est jamais vide
                raise RuntimeError("sonde sans passe")
            _conclure(rapport, modele, jeu_lu, selection)
        except BaseException as exc:
            if rapport is not None and rapport.statut == "en_cours":
                rapport.statut = "interrompu"
                rapport.run.terminer("interrompu", motif=f"{type(exc).__name__} : {exc}"[:500])
            raise
    return rapport


def _conclure(
    rapport: RapportSonde, modele: ModeleResolu, jeu: Jeu, selection: Sequence[ItemBase]
) -> None:
    """Écrit `recommandation.json` et inscrit le statut final."""
    protocole, valide, motif = recommander(rapport.bilans)
    rapport.protocole_recommande, rapport.valide, rapport.motif = protocole, valide, motif
    recommandation = {
        "modele_ref": modele.ref,
        "slug": modele.slug,
        "jeu_version": jeu.version,
        "items": [item.id for item in selection],
        "critere": CRITERE,
        "protocole_toml": modele.config.protocole_outils,
        "protocoles": {p: b.vers_dict() for p, b in rapport.bilans.items()},
        "protocole_recommande": protocole,
        "valide": valide,
        "motif": motif,
        "connexions_bloquees": list(rapport.connexions_bloquees),
    }
    rapport.run.ecrire(FICHIER_RECOMMANDATION, json_canonique(recommandation) + b"\n")
    erreur = any(b.erreurs for b in rapport.bilans.values())
    statut = "partiel-erreur" if erreur else "complet"
    rapport.run.terminer(statut)
    rapport.statut = statut


__all__ = [
    "CRITERE",
    "FICHIER_RECOMMANDATION",
    "FICHIER_SONDE",
    "ITEMS_SONDE",
    "TYPE_RUN",
    "BilanProtocole",
    "RapportSonde",
    "evaluer",
    "recommander",
    "sonder",
]
