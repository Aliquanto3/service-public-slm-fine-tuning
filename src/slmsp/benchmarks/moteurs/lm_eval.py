"""Moteur lm-eval (AD-16) : QCM sur poids HF avant quantification, ifeval contre `llama-server`.

`lm_eval` tourne toujours en sous-processus (jamais importé ici : extra `bench`), avec
`env_outil()` (HF hors ligne, sans secret). Deux backends :

- cible `hf` : `--model hf` sur `<models>/<slug>/hf-bf16` ou `hf` ; sauté si les deux sont
  absents (modèle GGUF seul, ex. Ministral 3 8B). Une architecture qu'`AutoModelForCausalLM`
  ne charge pas prend l'adaptateur lm-eval dédié (`MODELES_PAR_ARCHITECTURE`, lu dans le
  `config.json` des poids : `Mistral3ForConditionalGeneration` → `hf-mistral3`) ;
- cible `gguf` : `--model local-chat-completions` vers le `llama-server` du GGUF, sur
  `127.0.0.1` (serveur démarré ici, ou `options.base_url` s'il est déjà servi).

La sortie JSON de lm-eval devient un `SortieMoteur` : une entrée `<tache>.<métrique>` par
valeur, `<tache>.<métrique>_stderr` pour l'erreur standard, `<tache>.n_items`.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from importlib import metadata
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlsplit

from slmsp.benchmarks.moteurs import ContexteBench, SortieMoteur, lancer_outil
from slmsp.core.config import dossier_modeles
from slmsp.core.erreurs import ConfigurationInvalide

if TYPE_CHECKING:
    from slmsp.benchmarks.config import BenchmarkConfig

DOSSIERS_HF = ("hf-bf16", "hf")
DOSSIER_TACHES = Path(__file__).resolve().parent.parent / "taches_lmeval"
VARIABLE_COMMANDE = "SLMSP_LM_EVAL_CMD"
"""Remplace `python -m lm_eval` (tests, autre environnement) ; découpée comme une ligne shell."""
VARIABLE_JEU_MCQ = "SLMSP_MCQ_EVAL_DIR"
TACHE_MCQ = "agentpublic_mcq"
ENV_API_LOCALE = {"OPENAI_API_KEY": "sans-objet-llama-server-local"}
"""`local-chat-completions` exige une clé ; `llama-server` local l'ignore."""
SEED_DEFAUT = 1234
"""Graine commune (python, numpy, torch, few-shot) si `options.seed` est absent."""
BATCH_DEFAUT = "auto"
HOTE = "127.0.0.1"
HOTES_LOCAUX = frozenset({"127.0.0.1", "localhost", "::1"})
MODELE_HF_DEFAUT = "hf"
MODELES_PAR_ARCHITECTURE = {"Mistral3ForConditionalGeneration": "hf-mistral3"}
"""Adaptateurs lm-eval des architectures multimodales évaluées en texte seul (lm-eval 0.4.13 :
`lm_eval/models/mistral3.py` charge `Mistral3ForConditionalGeneration`, backend causal)."""


class LmEvalEchoue(RuntimeError):
    """Code de sortie non nul de `lm_eval`, ou sortie JSON absente ou illisible."""


# -- Lancement --


def commande_lm_eval() -> list[str]:
    brute = os.environ.get(VARIABLE_COMMANDE, "").strip()
    return shlex.split(brute, posix=os.name != "nt") if brute else [sys.executable, "-m", "lm_eval"]


def dossier_poids_hf(slug: str) -> Path | None:
    """`<models>/<slug>/hf-bf16` ou `hf` s'il existe et n'est pas vide, sinon `None`."""
    for nom in DOSSIERS_HF:
        dossier = dossier_modeles() / slug / nom
        if dossier.is_dir() and any(dossier.iterdir()):
            return dossier
    return None


def modele_hf(poids: Path) -> str:
    """Modèle lm-eval des poids : adaptateur dédié selon `architectures`, sinon `hf`."""
    try:
        donnees = json.loads((poids / "config.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return MODELE_HF_DEFAUT
    architectures = donnees.get("architectures") if isinstance(donnees, dict) else None
    for architecture in architectures if isinstance(architectures, list) else []:
        if isinstance(architecture, str) and architecture in MODELES_PAR_ARCHITECTURE:
            return MODELES_PAR_ARCHITECTURE[architecture]
    return MODELE_HF_DEFAUT


def graine(config: BenchmarkConfig) -> int:
    return int(config.options.get("seed", SEED_DEFAUT))


def lot_modele(slug: str) -> int | None:
    """`lm_eval_batch_size` de `config/modeles/<slug>.toml`, `None` si absent ou config illisible."""
    from slmsp.inference.serveur import charger_config_modele

    try:
        return charger_config_modele(slug).lm_eval_batch_size
    except ConfigurationInvalide:
        return None


def taille_lot(config: BenchmarkConfig, slug: str | None = None) -> str:
    """Priorité : `options.batch_size` du benchmark > `lm_eval_batch_size` du modèle > `auto`."""
    if "batch_size" in config.options:
        return str(config.options["batch_size"])
    parametre = lot_modele(slug) if slug else None
    return str(parametre) if parametre is not None else BATCH_DEFAUT


def arguments_communs(config: BenchmarkConfig, sortie: Path) -> list[str]:
    """Options communes : tâche, few-shot, graine, limite, sortie, tâches personnalisées."""
    arguments = [
        "--tasks",
        config.tache,
        "--num_fewshot",
        str(config.fewshot),
        "--seed",
        str(graine(config)),
        "--output_path",
        str(sortie),
        "--include_path",
        str(DOSSIER_TACHES),
    ]
    if config.limite is not None:
        arguments += ["--limit", str(config.limite)]
    return arguments


def arguments_hf(poids: Path, batch_size: str = BATCH_DEFAUT) -> list[str]:
    return [
        "--model",
        modele_hf(poids),
        "--model_args",
        f"pretrained={poids},dtype=bfloat16",
        "--device",
        "cuda:0",
        "--batch_size",
        batch_size,
    ]


def arguments_serveur(url: str, modele: str) -> list[str]:
    """Backend `local-chat-completions` vers `url` (`http://127.0.0.1:<port>/v1/...`)."""
    return [
        "--model",
        "local-chat-completions",
        "--model_args",
        f"model={modele},base_url={url},num_concurrent=1,max_retries=3,tokenized_requests=False",
        "--apply_chat_template",
    ]


def url_chat(port: int) -> str:
    return f"http://{HOTE}:{port}/v1/chat/completions"


# -- Analyse de la sortie JSON --


def trouver_sortie(dossier: Path) -> Path:
    """Fichier `results*.json` le plus récent sous `dossier` (lm-eval crée un sous-dossier)."""
    candidats = sorted(dossier.rglob("results*.json"), key=lambda p: p.stat().st_mtime)
    if not candidats:
        raise LmEvalEchoue(f"aucune sortie results*.json de lm_eval sous {dossier}")
    return candidats[-1]


def _nombre(valeur: Any) -> float | int | None:
    if isinstance(valeur, bool) or not isinstance(valeur, int | float):
        return None
    return valeur


def _nb_items(n_samples: Mapping[str, Any], tache: str) -> int | None:
    entree = n_samples.get(tache)
    if isinstance(entree, Mapping):
        valeur = entree.get("effective", entree.get("original"))
        return int(valeur) if isinstance(valeur, int | float) else None
    return None


def version_lm_eval(donnees: Mapping[str, Any]) -> str | None:
    """Version de lm-eval : celle de la sortie, sinon celle du paquet installé (sans l'importer)."""
    version = donnees.get("lm_eval_version")
    if isinstance(version, str) and version:
        return version
    try:
        return metadata.version("lm_eval")
    except metadata.PackageNotFoundError:
        return None


def analyser(donnees: Mapping[str, Any]) -> SortieMoteur:
    """Sortie JSON de lm-eval -> `SortieMoteur` (métrique, valeur, erreur standard, items).

    Clés lm-eval `<métrique>,<filtre>` : le filtre `none` est omis du nom. Les entrées
    sans valeur numérique (`alias`, `N/A`) sont ignorées ; une erreur standard `N/A` est
    consignée `None`.
    """
    if not isinstance(donnees, Mapping):
        raise LmEvalEchoue("sortie lm_eval : objet JSON attendu")
    resultats = donnees.get("results")
    if not isinstance(resultats, Mapping) or not resultats:
        raise LmEvalEchoue("sortie lm_eval sans section `results`")
    n_samples = donnees.get("n-samples")
    n_samples = n_samples if isinstance(n_samples, Mapping) else {}
    versions = donnees.get("versions")
    versions = versions if isinstance(versions, Mapping) else {}
    scores: dict[str, float | int | None] = {}
    taches: dict[str, Any] = {}
    for tache, mesures in resultats.items():
        metriques: dict[str, Any] = {}
        if not isinstance(mesures, Mapping):
            continue
        for cle, valeur in mesures.items():
            nom, _, filtre = cle.partition(",")
            if nom == "alias" or nom.endswith("_stderr"):
                continue
            nombre = _nombre(valeur)
            if nombre is None:
                continue
            nom_complet = nom if filtre in ("", "none") else f"{nom},{filtre}"
            erreur = _nombre(mesures.get(f"{nom}_stderr,{filtre}" if filtre else f"{nom}_stderr"))
            scores[f"{tache}.{nom_complet}"] = nombre
            scores[f"{tache}.{nom_complet}_stderr"] = erreur
            metriques[nom_complet] = {"valeur": nombre, "erreur_standard": erreur}
        nb = _nb_items(n_samples, tache)
        if nb is not None:
            scores[f"{tache}.n_items"] = nb
        taches[tache] = {
            "metriques": metriques,
            "n_items": nb,
            "version_tache": versions.get(tache),
        }
    version = version_lm_eval(donnees)
    versions_taches = ", ".join(f"{t}@v{v}" for t, v in versions.items() if v is not None)
    return SortieMoteur(
        scores=scores,
        outil="lm-eval",
        outil_version=version,
        jeu_version=f"lm-eval {versions_taches}" if versions_taches else None,
        details={"taches": taches, "lm_eval_version": version},
    )


# -- Exécution --


def _jeu_mcq(config: BenchmarkConfig, contexte: ContexteBench) -> tuple[Path | None, str | None]:
    """Dossier du jeu local MCQ-eval, ou un motif de saut."""
    if not config.jeux:
        return None, "jeu MCQ-eval non déclaré dans la configuration du benchmark"
    jeu = config.jeux[0]
    if not jeu.revision:
        return None, f"jeu {jeu.nom} non épinglé (voir `slmsp fetch benchmarks`)"
    dossier = contexte.dossier_jeux / jeu.nom / str(jeu.revision)
    if not dossier.is_dir():
        return None, f"jeu {jeu.nom} absent : {dossier} (`slmsp fetch benchmarks`)"
    return dossier, None


def verifier_cache_hf(config: BenchmarkConfig) -> None:
    """Le cache HF local contient chaque révision épinglée dans `options.jeux_hf`.

    lm_eval tourne hors ligne et lit ce cache : un jeu absent ou d'une autre révision fausserait
    la mesure en silence. `ConfigurationInvalide` explicite en cas d'écart.
    """
    pins = config.options.get("jeux_hf", {})
    hub = dossier_modeles() / ".cache-hf" / "hub"
    for depot, revision in pins.items():
        snapshots = hub / f"datasets--{depot.replace('/', '--')}" / "snapshots"
        if (snapshots / str(revision)).is_dir():
            continue
        presentes = sorted(p.name for p in snapshots.iterdir()) if snapshots.is_dir() else []
        raise ConfigurationInvalide(
            f"cache HF : jeu {depot} attendu à la révision {revision}, "
            f"présent : {', '.join(presentes) or 'absent'} ({hub})"
        )


INDICES_HORS_LIGNE = ("offline", "couldn't reach", "cannot find", "connectionerror", "not found")


LIGNE_ERREUR = re.compile(
    r"traceback|error|exception|\b[45]\d\d\b|killed|out of memory|oom|fatal|failed|abort",
    re.IGNORECASE,
)
LIGNE_PROGRESSION = re.compile(r"\d+%\||\d+/\d+ \[|it/s\]|s/it\]")
MAX_LIGNES_MOTIF = 25
MAX_CARACTERES_MOTIF = 2500


def ecrire_journal(dossier: Path, fin: Any) -> Path:
    """Écrit stdout et stderr complets du sous-processus (`stdout.log`, `stderr.log`)."""
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "stdout.log").write_text(fin.stdout or "", encoding="utf-8")
    journal = dossier / "stderr.log"
    journal.write_text(fin.stderr or "", encoding="utf-8")
    return journal


def extraire_erreurs(stderr: str, stdout: str = "") -> str:
    """Lignes d'erreur réelles (trace Python, Error, HTTP 4xx/5xx) sans barres de progression.

    Sans ligne d'erreur, repli sur les dernières lignes hors progression, puis sur la fin brute.
    """
    lignes: list[str] = []
    for brut in (stderr + "\n" + stdout).replace("\r", "\n").splitlines():
        ligne = brut.strip()
        if ligne and not LIGNE_PROGRESSION.search(ligne):
            lignes.append(ligne)
    retenues: list[str] = []
    en_trace = False
    for ligne in lignes:
        if ligne.startswith("Traceback"):
            en_trace = True
            retenues.append(ligne)
        elif en_trace:
            retenues.append(ligne)
            if not ligne.startswith(("File ", "raise ")) and LIGNE_ERREUR.search(ligne):
                en_trace = False
        elif LIGNE_ERREUR.search(ligne):
            retenues.append(ligne)
    choisies = (retenues or lignes)[-MAX_LIGNES_MOTIF:]
    texte = "\n".join(dict.fromkeys(choisies))
    if not texte:
        texte = (stderr or stdout or "").strip()
    return texte[-MAX_CARACTERES_MOTIF:]


def _lancer(
    commande: list[str],
    dossier_sortie: Path,
    env: Mapping[str, str],
    config: BenchmarkConfig,
    lot: str = "1",
) -> SortieMoteur:
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    fin = lancer_outil(commande, env_supplementaire=env)
    journal = ecrire_journal(dossier_sortie, fin)
    if fin.returncode != 0:
        queue = extraire_erreurs(fin.stderr or "", fin.stdout or "")
        indice = ""
        if not LIGNE_ERREUR.search(queue):
            indice = (
                " [aucune ligne d'erreur dans stderr : sortie sans trace, donc processus tué de "
                "l'extérieur (garde mémoire, mémoire saturée) plutôt qu'erreur lm-eval]"
            )
        if any(m in queue.lower() for m in INDICES_HORS_LIGNE) and not config.jeux:
            indice = (
                " [jeu ou ressource introuvable hors ligne : ce benchmark n'épingle aucun jeu "
                "(`[[jeux]]`), lm_eval lit le cache HF local ; le remplir avant (HF_HOME)]"
            )
        raise LmEvalEchoue(
            f"lm_eval a échoué (code {fin.returncode}) : {queue}{indice} "
            f"[journal complet : {journal}]"
        )
    chemin = trouver_sortie(dossier_sortie)
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LmEvalEchoue(f"sortie lm_eval illisible ({chemin}) : {exc}") from exc
    sortie = analyser(donnees)
    sortie.details["sortie_json"] = str(chemin)
    sortie.seed = graine(config)
    sortie.batch_size = lot
    return sortie


def resoudre_gguf(contexte: ContexteBench) -> tuple[str, Any, Path]:
    """`(slug, ConfigModele, GGUF)` de la variante ; `ConfigurationInvalide` si introuvable.

    `base:<slug>` : GGUF q4_k_m (`apres`) ou `gguf_f16` (`avant`, `fetch modeles --f16`).
    `ft:<export>` : GGUF `modele-f16.gguf` ou `modele-q4_k_m.gguf` du run d'export.
    """
    from slmsp.core.artefacts import ouvrir_run
    from slmsp.inference.serveur import charger_config_modele

    quantification = "f16" if contexte.variante == "avant" else "q4_k_m"
    genre, valeur = contexte.modele_ref.split(":", 1)
    if genre == "base":
        config = charger_config_modele(valeur)
        fichier = config.gguf_pour(quantification)
        if fichier is None:
            raise ConfigurationInvalide(
                f"aucun GGUF F16 de base pour {contexte.modele_ref} "
                "(section gguf_f16 absente de la configuration du modèle)"
            )
        gguf = dossier_modeles() / valeur / "gguf" / Path(fichier.fichier).name
        if quantification == "f16" and not gguf.is_file():
            raise ConfigurationInvalide(
                f"GGUF F16 de base absent : {gguf} (`slmsp fetch modeles {valeur} --f16`)"
            )
        slug = valeur
    else:
        run = ouvrir_run(valeur, racine=contexte.racine)
        base = run.manifeste.modele_ref or ""
        if not base.startswith("base:"):
            raise ConfigurationInvalide(f"run d'export {valeur} sans modèle de base")
        slug = base.removeprefix("base:")
        config = charger_config_modele(slug).model_copy(update={"chat_template_force": False})
        gguf = run.dossier / f"modele-{quantification}.gguf"
    if not gguf.is_file():
        raise ConfigurationInvalide(f"GGUF absent : {gguf}")
    return slug, config, gguf


@contextmanager
def serveur_llama(config: BenchmarkConfig, contexte: ContexteBench) -> Iterator[tuple[str, str]]:
    """Démarre `llama-server` pour le GGUF de la variante ; rend `(url, nom_modele)`.

    `options.base_url` (serveur déjà lancé) évite le démarrage. Le verrou GPU est celui de
    l'orchestrateur (`prendre_verrou_gpu=False`).
    """
    from slmsp.inference.serveur import ServeurLlama

    url = config.options.get("base_url")
    if url:
        if urlsplit(str(url)).hostname not in HOTES_LOCAUX:
            raise ConfigurationInvalide(f"options.base_url doit viser 127.0.0.1 : {url}")
        yield str(url), contexte.modele_ref
        return
    slug, modele_config, gguf = resoudre_gguf(contexte)
    serveur = ServeurLlama(
        modele_config,
        contexte.variante_llamacpp,  # type: ignore[arg-type]
        slug=slug,
        gguf=gguf,
        prendre_verrou_gpu=False,
    )
    with serveur:
        yield url_chat(serveur.port), slug


def executer(config: BenchmarkConfig, contexte: ContexteBench) -> SortieMoteur:
    """Lance la tâche lm-eval du benchmark ; saute (avec motif) si le modèle ne s'y prête pas."""
    sortie = contexte.run.dossier / "lm_eval" / f"{config.nom}--{contexte.variante}"
    env: dict[str, str] = {}
    if config.tache == TACHE_MCQ:
        jeu, motif = _jeu_mcq(config, contexte)
        if jeu is None:
            return SortieMoteur(saute=motif)
        env[VARIABLE_JEU_MCQ] = str(jeu)
    if config.cible == "hf":
        if not contexte.modele_ref.startswith("base:"):
            return SortieMoteur(saute="QCM sur poids HF : seuls les modèles base:<slug> sont gérés")
        slug = contexte.modele_ref.split(":", 1)[1]
        poids = dossier_poids_hf(slug)
        if poids is None:
            return SortieMoteur(
                saute=f"poids HF absents ({slug} : ni hf-bf16 ni hf) : GGUF seul, QCM sautés"
            )
        verifier_cache_hf(config)
        lot = taille_lot(config, slug)
        commande = [
            *commande_lm_eval(),
            *arguments_hf(poids, lot),
            *arguments_communs(config, sortie),
        ]
        return _lancer(commande, sortie, env, config, lot)
    verifier_cache_hf(config)
    try:
        with serveur_llama(config, contexte) as (url, nom):
            commande = [
                *commande_lm_eval(),
                *arguments_serveur(url, nom),
                *arguments_communs(config, sortie),
            ]
            return _lancer(commande, sortie, {**env, **ENV_API_LOCALE}, config)
    except ConfigurationInvalide as exc:
        return SortieMoteur(saute=f"modèle non servable ({contexte.variante}) : {exc}")


__all__ = ["LmEvalEchoue", "analyser", "executer"]
