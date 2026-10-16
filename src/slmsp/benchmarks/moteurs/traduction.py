"""Moteur de traduction (AD-16, FR-18) : chrF sacrebleu sur WMT14 et FLORES-200.

Chaque paire `src-tgt` lit `<jeu>/<revision>/<src>-<tgt>.jsonl` (lignes `{"source", "reference"}`)
sous `data/raw/benchmarks/`. La traduction est générée par `LlmPort.generer` avec le prompt de
la Tâche TR (`construire_messages`, AD-7), température 0. Une paire dont le jeu est absent,
non épinglé ou à accès conditionnel non obtenu est sautée et consignée (AC 2) ; sans aucune
paire, le benchmark est sauté.

Options : `wmt14_phrases` (sous-échantillon, 500 par défaut), `paires_wmt14` (défaut
`["en-fr", "fr-en"]`), `paires_flores`. Scores : `<paire>.chrf` et `<paire>.n_items` ;
`details.signatures` archive la signature sacrebleu de chaque paire.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from contextlib import ExitStack
from importlib import metadata
from pathlib import Path
from typing import TYPE_CHECKING, Any

from slmsp.benchmarks.moteurs import ContexteBench, SortieMoteur
from slmsp.benchmarks.moteurs.llm import llm_gguf
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.evenements import Jeton

if TYPE_CHECKING:
    from slmsp.benchmarks.config import BenchmarkConfig
    from slmsp.core.ports import LlmPort

PAIRES_WMT14_DEFAUT = ("en-fr", "fr-en")
PHRASES_WMT14_DEFAUT = 500
LANGUES = {
    "en": "anglais",
    "fr": "français",
    "es": "espagnol",
    "ar": "arabe",
    "pt": "portugais",
    "de": "allemand",
}
OPTIONS_GENERATION = {"temperature": 0, "seed": 1234, "max_tokens": 512}
SEED_DEFAUT = 1234

Calculer = Callable[[Sequence[str], Sequence[str]], tuple[float, str]]


def calculer_chrf(hypotheses: Sequence[str], references: Sequence[str]) -> tuple[float, str]:
    """chrF (0 à 100) et signature sacrebleu, sur un corpus à une référence par phrase."""
    from sacrebleu.metrics import CHRF

    metrique = CHRF()
    score = metrique.corpus_score(list(hypotheses), [list(references)])
    return float(score.score), str(metrique.get_signature())


def lire_paire(chemin: Path, limite: int | None) -> list[tuple[str, str]]:
    """`(source, référence)` des `limite` premières lignes non vides (ordre du fichier)."""
    phrases: list[tuple[str, str]] = []
    with chemin.open(encoding="utf-8") as flux:
        for ligne in flux:
            if not ligne.strip():
                continue
            donnees = json.loads(ligne)
            phrases.append((str(donnees["source"]), str(donnees["reference"])))
            if limite is not None and len(phrases) >= limite:
                break
    return phrases


def _dossier_jeu(
    config: BenchmarkConfig, contexte: ContexteBench, nom: str
) -> tuple[Path | None, str | None]:
    jeu = next((j for j in config.jeux if j.nom == nom), None)
    if jeu is None:
        return None, f"jeu {nom} non déclaré dans la configuration"
    if not jeu.revision:
        return None, f"jeu {nom} non épinglé (accès {jeu.acces}) : `slmsp fetch benchmarks`"
    dossier = contexte.dossier_jeux / jeu.nom / str(jeu.revision)
    if not dossier.is_dir():
        return None, f"jeu {nom} absent (accès {jeu.acces}) : {dossier}"
    return dossier, None


def paires_demandees(config: BenchmarkConfig) -> list[tuple[str, str]]:
    """`(jeu, paire)` : WMT14 puis FLORES-200, dans l'ordre de la configuration."""
    wmt = config.options.get("paires_wmt14", list(PAIRES_WMT14_DEFAUT))
    flores = config.options.get("paires_flores", [])
    return [("wmt14", p) for p in wmt] + [("flores-200", p) for p in flores]


def traduire(llm: LlmPort, tache: Any, source: str, cible: str, texte: str) -> str:
    """Traduction d'un texte par le prompt de la Tâche TR, via `LlmPort.generer`."""
    from slmsp.harness.prompts import construire_messages

    inconnues = [c for c in (source, cible) if c not in LANGUES]
    if inconnues:
        raise ConfigurationInvalide(f"langue de traduction inconnue : {', '.join(inconnues)}")
    messages = construire_messages(
        tache, {"langue_source": LANGUES[source], "langue_cible": LANGUES[cible], "texte": texte}
    )
    flux = llm.generer(messages, options=OPTIONS_GENERATION)
    return "".join(e.texte for e in flux if isinstance(e, Jeton)).strip()


def _version_sacrebleu() -> str | None:
    try:
        return metadata.version("sacrebleu")
    except metadata.PackageNotFoundError:
        return None


def executer(
    config: BenchmarkConfig,
    contexte: ContexteBench,
    *,
    llm: LlmPort | None = None,
    calculer: Calculer | None = None,
) -> SortieMoteur:
    """ChrF par paire de langues ; `llm` et `calculer` sont injectables (tests)."""
    from slmsp.harness.taches import charger_taches

    calculer = calculer or calculer_chrf
    limite_wmt = int(config.options.get("wmt14_phrases", PHRASES_WMT14_DEFAUT))
    a_traiter: list[tuple[str, list[tuple[str, str]]]] = []
    sautees: dict[str, str] = {}
    demandees = paires_demandees(config)
    for _, paire in demandees:
        langues = paire.split("-")
        if len(langues) != 2 or any(langue not in LANGUES for langue in langues):
            raise ConfigurationInvalide(f"paire de traduction invalide : {paire!r}")
    doublons = {p for _, p in demandees if sum(1 for _, q in demandees if q == p) > 1}
    for jeu, paire in demandees:
        cle = f"{jeu}.{paire}" if paire in doublons else paire
        dossier, motif = _dossier_jeu(config, contexte, jeu)
        fichier = dossier / f"{paire}.jsonl" if dossier else None
        if fichier is not None and not fichier.is_file():
            motif = f"fichier absent : {fichier}"
        if motif or fichier is None:
            sautees[cle] = motif or "fichier absent"
            continue
        limite = config.limite or (limite_wmt if jeu == "wmt14" else None)
        a_traiter.append((cle, lire_paire(fichier, limite)))
    if not a_traiter:
        detail = "; ".join(f"{p} ({m})" for p, m in sautees.items())
        return SortieMoteur(saute=f"aucune paire disponible : {detail}")
    tache = charger_taches().tache("TR")
    scores: dict[str, float | int | None] = {}
    signatures: dict[str, str] = {}
    with ExitStack() as pile:
        if llm is None:
            try:
                llm = pile.enter_context(llm_gguf(config, contexte))
            except ConfigurationInvalide as exc:
                return SortieMoteur(saute=f"modèle non servable ({contexte.variante}) : {exc}")
        for cle, phrases in a_traiter:
            source, cible = cle.rsplit(".", 1)[-1].split("-")
            hypotheses = [traduire(llm, tache, source, cible, s) for s, _ in phrases]
            score, signature = calculer(hypotheses, [r for _, r in phrases])
            scores[f"{cle}.chrf"] = score
            scores[f"{cle}.n_items"] = len(phrases)
            signatures[cle] = signature
    return SortieMoteur(
        scores=scores,
        outil="sacrebleu",
        outil_version=_version_sacrebleu(),
        seed=SEED_DEFAUT,
        batch_size="1",
        details={"signatures": signatures, "paires_sautees": sautees},
    )


__all__ = ["calculer_chrf", "executer", "lire_paire", "paires_demandees", "traduire"]
