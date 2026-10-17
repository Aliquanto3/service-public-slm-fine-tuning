"""Protocole de mesure FR-26 : RAM, débit, délai au premier token, taille installée.

`mesurer` pose `echauffement + repetitions` Questions à l'Assistant (fonction `repondre`
fournie par l'appelant, qui l'assemble comme `slmsp ask`), sous l'échantillonneur RAM, puis
écrit `runs/measure/<run_id>/resultat.json` (`ResultatMesure`, slug `h-ram`). Ce module
n'importe jamais `slmsp.cli` (AD-1) ; l'exclusivité (`verrou_mesure`) est prise par l'appelant
avant de démarrer les serveurs.

Conformité : NFR-1 pic de RAM ≤ `ram_max_go` (la cible `ram_cible_go` est consignée à part),
NFR-2 débit médian ≥ `debit_min_tps`, NFR-3 p95 du délai au premier token < `premier_token_max_s`,
NFR-6 taille installée ≤ `taille_max_go`. La machine de développement n'est pas le PC cible.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable, Iterator, Mapping
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Final

from slmsp.core.artefacts import empreinte_environnement, nouveau_run
from slmsp.core.canonique import json_canonique
from slmsp.core.config import racine_ecriture
from slmsp.core.evenements import Evenement
from slmsp.core.schemas.mesure import ResultatMesure
from slmsp.core.var import verrou_gpu
from slmsp.harness.service import CODE_CONTEXTE
from slmsp.measure.config import ConfigMesures
from slmsp.measure.debit import MesureEchouee, MesureQuestion, mediane_p95, mesurer_question
from slmsp.measure.ram import EchantillonneurRam
from slmsp.measure.taille import tailles_composants

MESURE: Final = "h-ram"
HYPOTHESE: Final = "H-RAM"
NOM_RESULTAT: Final = "resultat.json"
GO: Final = 1024**3
AVERTISSEMENT: Final = (
    "Mesure faite sur la machine de développement, qui n'est pas le PC cible : les seuils "
    "NFR-1 à NFR-3 et NFR-6 sont à reconfirmer sur le PC cible."
)
REPLI: Final = (
    "réduire le contexte, la quantification ou le Modèle de base (candidat plus petit) ; "
    "à étudier, non implémenté"
)


@contextmanager
def verrou_mesure() -> Iterator[Path]:
    """Exclusivité de la mesure : tient `gpu.lock` sans attente (AD-27).

    Lève `RessourceOccupee` (code 5) si une autre commande `slmsp` le détient.
    """
    with verrou_gpu(commande="slmsp measure run") as chemin:
        yield chemin


class ContexteInsuffisant(MesureEchouee):
    """Le prompt du protocole ne tient pas dans le contexte demandé (jamais tronqué)."""


def est_erreur_de_contexte(message: str) -> bool:
    """Le message d'erreur signale-t-il un dépassement de contexte ?

    Cas nominal (correctif F2) : l'évènement `Erreur` du Harnais porte le code
    `contexte-depasse` (`CODE_CONTEXTE`), que `mesurer_question` place en tête du message.
    Repli : sous-chaîne `context` insensible à la casse, sur un texte brut de llama-server
    (« exceeds the available context size »…). En cas de doute la mesure échoue quand même
    (erreur d'origine relancée), seul le message est moins explicite.
    """
    return message.startswith(CODE_CONTEXTE) or "context" in message.lower()


def _verifier_contexte(mesure: MesureQuestion, contexte: int) -> bool:
    """Refuse si le prompt (ou prompt + réponse) remplit le contexte : risque de troncature.

    Le Harnais borne le prompt à `contexte − max_tokens` et la réponse à `max_tokens`
    (correctif F2) : la somme ne dépasse donc pas le contexte. L'égalité, ambiguë (réponse
    coupée par `max_tokens` ou par le contexte), reste refusée.

    Retourne False si le serveur n'a pas renvoyé `usage.prompt_tokens` : la vérification n'a
    alors pas pu se faire (à signaler, jamais à taire).
    """
    if mesure.prompt_tokens is None:
        return False
    if mesure.prompt_tokens + mesure.tokens >= contexte:
        raise ContexteInsuffisant(
            f"contexte {contexte} trop petit : le prompt du protocole fait "
            f"{mesure.prompt_tokens} tokens et la réponse {mesure.tokens} ; augmenter --contexte"
        )
    return True


def _conformite(valeurs: dict[str, float | None], config: ConfigMesures) -> dict[str, bool]:
    seuils = config.seuils
    ram, debit = valeurs["ram_max_go"], valeurs["debit_tps_mediane"]
    return {
        "nfr-1": ram is not None and ram <= seuils.ram_max_go,
        "nfr-1-cible": ram is not None and ram <= seuils.ram_cible_go,
        "nfr-2": debit is not None and debit >= seuils.debit_min_tps,
        "nfr-3": (valeurs["premier_token_s_p95"] or float("inf")) < seuils.premier_token_max_s,
        "nfr-6": (valeurs["taille_installee_go"] or 0.0) <= seuils.taille_max_go,
    }


def mesurer(
    repondre: Callable[[str], Iterable[Evenement]],
    config: ConfigMesures,
    *,
    modele: str,
    quantification: str | None = None,
    serveurs: list[dict[str, Any]] | None = None,
    composants: Mapping[str, Path] | None = None,
    racine: str | Path | None = None,
    index_version: str | None = None,
    contexte: int | None = None,
    verifier_contexte: bool = False,
    max_tokens: int | None = None,
    echantillonneur: Callable[..., EchantillonneurRam] = EchantillonneurRam,
    horloge: Callable[[], float] = time.perf_counter,
) -> ResultatMesure:
    """Mesure l'Assistant servi par `repondre(question)` et écrit le run `h-ram`.

    `contexte` est le contexte effectif (consigné). `max_tokens` est le plafond de sortie
    effectif des Questions (consigné) : depuis le correctif F2 (`generation.max_tokens`), les
    réponses sont plafonnées, ce qui rend débit et tokens non comparables aux runs antérieurs
    sans plafond. Le délai au premier token compte aussi les mesures du budget de prompt.
    `verifier_contexte` (contexte imposé par l'appelant) refuse un prompt qui ne tient pas ;
    sinon aucune vérification n'est ajoutée.
    En cas d'erreur, le run est terminé `partiel-erreur` et l'erreur relancée.
    """
    racine = (Path(racine) if racine is not None else racine_ecriture()).resolve()
    parametres: dict[str, Any] = {
        "modele": modele,
        "quantification": quantification,
        "questions": list(config.questions),
        "repetitions": config.repetitions,
        "echauffement": config.echauffement,
        "plafond_threads": config.plafond_threads,
        "periode_ms": config.periode_ms,
        "serveurs": serveurs or [],
    }
    if contexte is not None:
        parametres["contexte"] = contexte
    if max_tokens is not None:
        parametres["max_tokens"] = max_tokens
    seuils = config.seuils.model_dump()
    run = nouveau_run(
        "measure",
        MESURE,
        {"hypothese": HYPOTHESE, **parametres, "seuils": seuils},
        racine=racine,
        index_version=index_version,
        quantification=quantification,
    )
    try:
        questions = config.questions
        mesures: list[MesureQuestion] = []
        verifie = verifier_contexte and contexte is not None
        with echantillonneur(periode_s=config.periode_ms / 1000) as ram:
            for rang in range(config.echauffement + config.repetitions):
                question = questions[rang % len(questions)]
                try:
                    mesure = mesurer_question(repondre(question), horloge)
                except MesureEchouee as exc:
                    if verifier_contexte and est_erreur_de_contexte(str(exc)):
                        raise ContexteInsuffisant(
                            f"contexte {contexte} trop petit pour le prompt du protocole "
                            f"({exc}) ; augmenter --contexte"
                        ) from exc
                    raise
                if verifier_contexte and contexte is not None:
                    verifie = _verifier_contexte(mesure, contexte) and verifie
                if rang >= config.echauffement:
                    mesures.append(mesure)
        premiers = [m.premier_token_s for m in mesures]
        debits = [m.debit_tps for m in mesures if m.debit_tps is not None]
        premier_med, premier_p95 = mediane_p95(premiers)
        debit_med = mediane_p95(debits)[0] if debits else None
        tailles = tailles_composants(composants or {})
        valeurs: dict[str, float | None] = {
            "ram_max_go": ram.pic_octets / GO,
            "debit_tps_mediane": debit_med,
            "debit_tps_min": min(debits) if debits else None,
            "premier_token_s_mediane": premier_med,
            "premier_token_s_p95": premier_p95,
            "taille_installee_go": sum(tailles.values()) / GO,
        }
        conformite = _conformite(valeurs, config)
        exigences = ("nfr-1", "nfr-2", "nfr-3", "nfr-6")
        echecs = [n for n in exigences if not conformite[n]]
        resultat = ResultatMesure(
            mesure=MESURE,
            hypothese=HYPOTHESE,
            run_id=run.run_id,
            mesure_le=datetime.now().astimezone(),
            index_version=index_version,
            parametres=parametres,
            valeurs=valeurs,
            seuils=seuils,
            verdict="infirmee" if echecs else "confirmee",
            repli=f"{REPLI} (hors seuil : {', '.join(echecs)})" if echecs else None,
            details={
                "echantillons_ram": ram.nb_echantillons,
                "tailles_octets": tailles,
                "contexte_effectif": contexte,
                # "verifie" | "non-verifiee" (serveur sans usage.prompt_tokens) | "non-demandee"
                "verification_contexte": (
                    "non-demandee"
                    if not verifier_contexte
                    else "verifie"
                    if verifie
                    else "non-verifiee"
                ),
                "tokens_par_repetition": [m.tokens for m in mesures],
                "tokens_estimes_par_jetons": any(m.tokens_estimes for m in mesures),
                "unite": "Go = 1024³ octets ; ram = pic de la somme des working sets de l'arbre",
            },
            conformite=conformite,
            environnement=empreinte_environnement(racine),
            avertissement=AVERTISSEMENT,
        )
        run.ecrire(NOM_RESULTAT, json_canonique(resultat.model_dump(mode="json")) + b"\n")
    except KeyboardInterrupt:
        run.terminer("interrompu", "arrêt demandé")
        raise
    except Exception as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
        raise
    run.terminer("complet")
    return resultat
