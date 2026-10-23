"""`slmsp measure application` : mesure de l'application installée (FR-26, NFR-1 à NFR-3, H-RAM).

Lance l'exécutable (`AssistantSP.exe`, onedir : processus racine de pywebview, WebView2 et des
deux `llama-server`), échantillonne la RAM de tout son arbre de processus (`EchantillonneurRam`,
`racine=` le processus lancé) pendant qu'Anaël l'utilise, et écrit
`runs/measure/<run_id>/resultat.json` (slug `application`). Débit et délai au premier jeton sont
lus, en option, dans un export CSV des mesures de l'application (`--mesures-csv`), jamais dans sa
base SQLite (AD-23) : ce module n'importe ni `slmsp.app` ni `slmsp.cli` (AD-1, couches 4 et 5).

La mesure se termine à la sortie du processus lancé, à `duree_s` écoulées (défaut 900 s) ou sur
Ctrl+C (fin normale de la fenêtre de mesure, pas une interruption) ; l'application n'est jamais
tuée, seul l'échantillonnage s'arrête. Le protocole manuel (capture réseau NFR-7, consignation)
est dans `docs/recette-pc-cible.md`.
"""

from __future__ import annotations

import csv
import io
import subprocess
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import psutil

from slmsp.core.artefacts import empreinte_environnement, nouveau_run
from slmsp.core.canonique import json_canonique
from slmsp.core.config import racine_ecriture
from slmsp.core.schemas.mesure import ResultatMesure
from slmsp.inference.mesures import FOURNISSEUR_LOCAL
from slmsp.measure.config import ConfigMesures
from slmsp.measure.debit import mediane_p95
from slmsp.measure.ram import EchantillonneurRam, repartition_par_nom

MESURE: Final = "application"
HYPOTHESE: Final = "H-RAM"
NOM_RESULTAT: Final = "resultat.json"
GO: Final = 1024**3
DUREE_DEFAUT_S: Final = 900.0
SORTIE_RAPIDE_S: Final = 5.0
"""Sortie du processus lancé avant ce délai = instance déjà ouverte, pas une fermeture voulue."""
PAS_ATTENTE_S: Final = 0.5
COLONNES_CSV: Final = (
    "horodatage",
    "fournisseur",
    "tokens_sortie",
    "interrompu",
    "duree_ms",
    "premier_token_ms",
)
AVERTISSEMENT: Final = (
    "À consigner dans docs/recette-pc-cible.md ; vérifier que la machine est le PC cible "
    "(empreinte)."
)
REPLI: Final = (
    "contexte réduit, cache KV en q4, usearch en i8, embedding plus léger, corpus restreint "
    "(addendum §D) ; à étudier, non implémenté"
)


class InstanceDejaOuverte(RuntimeError):
    """Le processus lancé est sorti en moins de `SORTIE_RAPIDE_S` : une instance tournait déjà."""


class CsvInvalide(RuntimeError):
    """Le CSV des mesures est illisible, mal formé ou ne contient aucune ligne retenue."""


def _demarquer(valeur: str) -> str:
    """Retire le préfixe `'` que `cellule_sure` pose devant un texte commençant par `=+-@`."""
    return valeur[1:] if valeur.startswith("'") else valeur


def _lire_mesures_csv(
    chemin: Path, debut: datetime, fin: datetime
) -> tuple[list[float], list[float]]:
    """(débits tps, délais au premier jeton en s) des lignes locales de la fenêtre de mesure.

    Écarte les lignes `interrompu`, sans `premier_token_ms`, d'un autre fournisseur ou hors de
    la fenêtre `[debut, fin]`. Lève `CsvInvalide` si le fichier est illisible, mal formé ou sans
    ligne retenue.
    """
    try:
        texte = chemin.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise CsvInvalide(f"{chemin} : illisible ({exc})") from exc
    lignes = list(csv.reader(io.StringIO(texte), delimiter=";"))
    if not lignes:
        raise CsvInvalide(f"{chemin} : fichier vide")
    entete, *corps = lignes
    try:
        index = {nom: entete.index(nom) for nom in COLONNES_CSV}
    except ValueError as exc:
        raise CsvInvalide(f"{chemin} : en-tête sans la colonne {exc}") from exc
    debits: list[float] = []
    premiers: list[float] = []
    for ligne in corps:
        if len(ligne) != len(entete):
            continue
        valeurs = {nom: _demarquer(ligne[i]) for nom, i in index.items()}
        if valeurs["fournisseur"] != FOURNISSEUR_LOCAL:
            continue
        if valeurs["interrompu"] not in ("0", "", "False"):
            continue
        if not valeurs["premier_token_ms"] or not valeurs["duree_ms"]:
            continue
        try:
            horodatage = datetime.fromisoformat(valeurs["horodatage"])
        except ValueError:
            continue
        if not (debut <= horodatage <= fin):
            continue
        premier_token_ms = float(valeurs["premier_token_ms"])
        duree_generation_s = (float(valeurs["duree_ms"]) - premier_token_ms) / 1000
        tokens_sortie = float(valeurs["tokens_sortie"] or 0)
        if duree_generation_s <= 0 or tokens_sortie <= 0:
            continue
        debits.append(tokens_sortie / duree_generation_s)
        premiers.append(premier_token_ms / 1000)
    if not debits:
        raise CsvInvalide(
            f"{chemin} : aucune ligne retenue (fournisseur local, fenêtre de mesure, "
            "non interrompue, avec premier_token_ms)"
        )
    return debits, premiers


def _attendre_fin(
    processus: subprocess.Popen[Any], duree_s: float, horloge: Callable[[], float]
) -> bool:
    """Attend la sortie du processus, `duree_s` écoulées ou Ctrl+C. Renvoie `True` si sorti tôt
    (< `SORTIE_RAPIDE_S`, signe d'une instance déjà ouverte)."""
    debut = horloge()
    try:
        while True:
            ecoule = horloge() - debut
            if processus.poll() is not None:
                return ecoule < SORTIE_RAPIDE_S
            if ecoule >= duree_s:
                return False
            time.sleep(min(PAS_ATTENTE_S, duree_s - ecoule))
    except KeyboardInterrupt:
        # Ctrl+C = fin normale de la fenêtre de mesure (boundary) : pas une instance déjà ouverte.
        return False


class _LectureArbre:
    """`lire` de l'échantillonneur : renvoie le total (compatible `EchantillonneurRam`) et
    garde la répartition par nom du dernier total au moins aussi grand que le pic courant."""

    def __init__(self) -> None:
        self.repartition_au_pic: dict[str, int] = {}
        self._pic = 0

    def __call__(self, racine: psutil.Process) -> int:
        repartition = repartition_par_nom(racine)
        total = sum(repartition.values())
        if total >= self._pic:
            self._pic = total
            self.repartition_au_pic = repartition
        return total


def _conformite(valeurs: dict[str, float | None], config: ConfigMesures) -> dict[str, bool]:
    seuils = config.seuils
    conformite = {
        "nfr-1": valeurs["ram_max_go"] <= seuils.ram_max_go,
        "nfr-1-cible": valeurs["ram_max_go"] <= seuils.ram_cible_go,
    }
    if valeurs["debit_tps_mediane"] is not None:
        conformite["nfr-2"] = valeurs["debit_tps_mediane"] >= seuils.debit_min_tps
    if valeurs["premier_token_s_p95"] is not None:
        conformite["nfr-3"] = valeurs["premier_token_s_p95"] < seuils.premier_token_max_s
    return conformite


def mesurer_application(
    exe: str | Path,
    config: ConfigMesures,
    *,
    duree_s: float = DUREE_DEFAUT_S,
    mesures_csv: str | Path | None = None,
    racine: str | Path | None = None,
    lancer: Callable[..., subprocess.Popen[Any]] = subprocess.Popen,
    horloge: Callable[[], float] = time.monotonic,
    echantillonneur: Callable[..., EchantillonneurRam] = EchantillonneurRam,
) -> ResultatMesure:
    """Lance `exe`, échantillonne la RAM de son arbre, lit `mesures_csv` s'il est fourni, et
    écrit le run `application` (slug `mesure`, hypothèse `H-RAM`).

    `racine` est la racine d'écriture des runs (défaut : `racine_ecriture()`), pas le processus
    lancé — qui est, lui, échantillonné par `echantillonneur(racine=<processus>, ...)`.
    Lève `InstanceDejaOuverte` si le processus lancé sort en moins de `SORTIE_RAPIDE_S`
    (une instance de l'application tournait déjà) et `CsvInvalide` si `mesures_csv` est
    illisible, mal formé ou sans ligne retenue. En cas d'erreur, le run est `partiel-erreur`.
    """
    racine_ecr = (Path(racine) if racine is not None else racine_ecriture()).resolve()
    parametres: dict[str, Any] = {
        "exe": str(exe),
        "duree_s": duree_s,
        "mesures_csv": str(mesures_csv) if mesures_csv is not None else None,
        "periode_ms": config.periode_ms,
    }
    seuils = config.seuils.model_dump()
    run = nouveau_run(
        "measure",
        MESURE,
        {"hypothese": HYPOTHESE, **parametres, "seuils": seuils},
        racine=racine_ecr,
    )
    try:
        debut = datetime.now().astimezone()
        processus = lancer([str(exe)])
        processus_racine = psutil.Process(processus.pid)
        lecture = _LectureArbre()
        with echantillonneur(
            racine=processus_racine, periode_s=config.periode_ms / 1000, lire=lecture
        ) as ram:
            sorti_tot = _attendre_fin(processus, duree_s, horloge)
        fin = datetime.now().astimezone()
        if sorti_tot:
            raise InstanceDejaOuverte(
                f"l'instance lancée ({exe}) s'est fermée en moins de {SORTIE_RAPIDE_S:g} s : "
                "fermer l'Assistant déjà ouvert puis relancer"
            )
        repartition_go = {nom: octets / GO for nom, octets in lecture.repartition_au_pic.items()}
        ram_max_go = ram.pic_octets / GO
        debit_med = premier_med = premier_p95 = None
        if mesures_csv is not None:
            debits, premiers = _lire_mesures_csv(Path(mesures_csv), debut, fin)
            debit_med = mediane_p95(debits)[0]
            premier_med, premier_p95 = mediane_p95(premiers)
        valeurs: dict[str, float | None] = {
            "ram_max_go": ram_max_go,
            "debit_tps_mediane": debit_med,
            "premier_token_s_mediane": premier_med,
            "premier_token_s_p95": premier_p95,
        }
        conformite = _conformite(valeurs, config)
        exigences = [n for n in ("nfr-1", "nfr-2", "nfr-3") if n in conformite]
        echecs = [n for n in exigences if not conformite[n]]
        resultat = ResultatMesure(
            mesure=MESURE,
            hypothese=HYPOTHESE,
            run_id=run.run_id,
            mesure_le=datetime.now().astimezone(),
            parametres=parametres,
            valeurs=valeurs,
            seuils=seuils,
            verdict="infirmee" if echecs else "confirmee",
            repli=f"{REPLI} (hors seuil : {', '.join(echecs)})" if echecs else None,
            details={
                "echantillons_ram": ram.nb_echantillons,
                "repartition_pic_go": repartition_go,
                "fenetre_mesure": [debut.isoformat(), fin.isoformat()],
                "unite": "Go = 1024³ octets ; ram = pic de la somme des working sets de l'arbre",
            },
            conformite=conformite,
            environnement=empreinte_environnement(racine_ecr),
            avertissement=AVERTISSEMENT,
        )
        run.ecrire(NOM_RESULTAT, json_canonique(resultat.model_dump(mode="json")) + b"\n")
    except Exception as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
        raise
    run.terminer("complet")
    return resultat
