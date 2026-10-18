"""Moteur de traduction (AD-16, FR-18) : chrF sacrebleu sur WMT14 et FLORES-200.

Chaque paire `src-tgt` lit `<jeu>/<revision>/<src>-<tgt>.jsonl` (lignes `{"source", "reference"}`)
sous `data/raw/benchmarks/`, ou, à défaut, les fichiers parquet du jeu tels que `slmsp fetch` les
dépose : WMT14 `<autre>-en/test-00000-of-00001.parquet` (colonne `translation`, un fichier pour les
deux sens) et FLORES-200 `data/language/<code>/devtest-00000-of-00001.parquet` (colonne `sentence`,
alignée par ligne ; format lu d'après la fiche du jeu, accès conditionnel non vérifié).
La traduction est générée par `LlmPort.generer` avec le prompt de la Tâche TR
(`construire_messages`, AD-7), température 0. Une paire dont le jeu est absent,
non épinglé ou à accès conditionnel non obtenu est sautée et consignée (AC 2) ; sans aucune
paire, le benchmark est sauté.

Options : `wmt14_phrases` (sous-échantillon, 500 par défaut), `paires_wmt14` (défaut
`["en-fr", "fr-en"]`), `paires_flores`. Scores : `<paire>.chrf`, `<paire>.n_items` et
`moyenne_wmt.chrf` (moyenne simple des paires WMT14 mesurées) et `moyenne.chrf` (moyenne de
toutes les paires demandées, seulement si aucune n'est sautée : jamais une moyenne de composition
variable). `details.paires_mesurees` / `paires_demandees` consignent la composition ;
`details.signatures` archive la signature sacrebleu de chaque paire.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from contextlib import ExitStack
from importlib import metadata
from pathlib import Path
from typing import TYPE_CHECKING, Any

from slmsp.benchmarks.moteurs import ContexteBench, SortieMoteur, appliquer_ordonne
from slmsp.benchmarks.moteurs.llm import llm_gguf
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.evenements import Jeton
from slmsp.core.langues import LANGUES

if TYPE_CHECKING:
    from slmsp.benchmarks.config import BenchmarkConfig
    from slmsp.core.ports import LlmPort

PAIRES_WMT14_DEFAUT = ("en-fr", "fr-en")
PHRASES_WMT14_DEFAUT = 500
CODES_FLORES = {
    "fr": "fra_Latn",
    "es": "spa_Latn",
    "ar": "arb_Arab",
    "pt": "por_Latn",
    "de": "deu_Latn",
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


def _lire_parquet(chemin: Path, colonne: str) -> list[Any]:
    import pyarrow as pa
    import pyarrow.parquet as pq

    try:
        return pq.read_table(chemin, columns=[colonne]).column(colonne).to_pylist()
    except (pa.ArrowException, OSError, KeyError) as exc:
        raise ConfigurationInvalide(
            f"fichier parquet illisible ou sans colonne `{colonne}` : {chemin} ({exc!r})"
        ) from exc


def charger_paire(jeu: str, dossier: Path, paire: str, limite: int | None) -> list[tuple[str, str]]:
    """`(source, référence)` d'une paire : `<paire>.jsonl` s'il existe, sinon le parquet du jeu.

    Lève `FileNotFoundError` (nom du fichier attendu) si rien n'est lisible.
    """
    jsonl = dossier / f"{paire}.jsonl"
    if jsonl.is_file():
        return lire_paire(jsonl, limite)
    source, cible = paire.split("-")
    if jeu == "wmt14":
        autre = cible if source == "en" else source
        parquet = dossier / f"{autre}-en" / "test-00000-of-00001.parquet"
        if not parquet.is_file():
            raise FileNotFoundError(str(parquet))
        lignes = _lire_parquet(parquet, "translation")
        try:
            phrases = [(str(ligne[source]), str(ligne[cible])) for ligne in lignes]
        except (KeyError, TypeError) as exc:
            raise ConfigurationInvalide(
                f"WMT14 : colonne `translation` sans les langues {source}/{cible} ({exc!r})"
            ) from exc
    elif jeu == "flores-200":
        fichiers = []
        for langue in (source, cible):
            code = CODES_FLORES.get(langue, langue)
            fichier = dossier / "data" / "language" / code / "devtest-00000-of-00001.parquet"
            if not fichier.is_file():
                raise FileNotFoundError(str(fichier))
            fichiers.append(fichier)
        phrases = list(
            zip(
                map(str, _lire_parquet(fichiers[0], "sentence")),
                map(str, _lire_parquet(fichiers[1], "sentence")),
                strict=True,
            )
        )
    else:
        raise FileNotFoundError(str(jsonl))
    return phrases[:limite] if limite is not None else phrases


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
    cles_wmt: set[str] = set()
    chrf_wmt: list[float] = []
    sautees: dict[str, str] = {}
    demandees = paires_demandees(config)
    for _, paire in demandees:
        langues = paire.split("-")
        if len(langues) != 2 or any(langue not in LANGUES for langue in langues):
            raise ConfigurationInvalide(f"paire de traduction invalide : {paire!r}")
    doublons = {p for _, p in demandees if sum(1 for _, q in demandees if q == p) > 1}
    for jeu, paire in demandees:
        cle = f"{jeu}.{paire}" if paire in doublons else paire
        if jeu == "wmt14":
            cles_wmt.add(cle)
        dossier, motif = _dossier_jeu(config, contexte, jeu)
        if dossier is not None:
            limite = config.limite or (limite_wmt if jeu == "wmt14" else None)
            try:
                a_traiter.append((cle, charger_paire(jeu, dossier, paire, limite)))
            except FileNotFoundError as exc:
                motif = f"fichier absent : {exc}"
        if motif:
            sautees[cle] = motif
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
            hypotheses = appliquer_ordonne(
                lambda s, llm=llm, de=source, vers=cible: traduire(llm, tache, de, vers, s[0]),
                phrases,
                contexte.parallele,
            )
            score, signature = calculer(hypotheses, [r for _, r in phrases])
            scores[f"{cle}.chrf"] = score
            if cle in cles_wmt:
                chrf_wmt.append(score)
            scores[f"{cle}.n_items"] = len(phrases)
            signatures[cle] = signature
    cles_demandees = [f"{j}.{p}" if p in doublons else p for j, p in demandees]
    if chrf_wmt:
        scores["moyenne_wmt.chrf"] = sum(chrf_wmt) / len(chrf_wmt)  # métrique du Comparatif
    if not sautees:  # composition complète seulement : sinon pas d'agrégat trompeur
        chrfs = [v for k, v in scores.items() if k.endswith(".chrf") and v is not None]
        scores["moyenne.chrf"] = sum(chrfs) / len(chrfs)
    return SortieMoteur(
        scores=scores,
        outil="sacrebleu",
        outil_version=_version_sacrebleu(),
        seed=SEED_DEFAUT,
        batch_size=str(contexte.parallele),
        details={
            "signatures": signatures,
            "paires_sautees": sautees,
            "paires_mesurees": [c for c, _ in a_traiter],
            "paires_demandees": cles_demandees,
        },
    )


__all__ = [
    "calculer_chrf",
    "charger_paire",
    "executer",
    "lire_paire",
    "paires_demandees",
    "traduire",
]
