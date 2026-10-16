"""Moteur lm-eval (AD-16) : QCM sur poids HF avant quantification, ifeval contre `llama-server`.

`lm_eval` tourne toujours en sous-processus (jamais importé ici : extra `bench`), avec
`env_outil()` (HF hors ligne, sans secret). Deux backends :

- cible `hf` : `--model hf` sur `<models>/<slug>/hf-bf16` ou `hf` ; sauté si les deux sont
  absents (modèle GGUF seul, ex. Ministral 3 8B) ;
- cible `gguf` : `--model local-chat-completions` vers le `llama-server` du GGUF, sur
  `127.0.0.1` (serveur démarré ici, ou `options.base_url` s'il est déjà servi).

La sortie JSON de lm-eval devient un `SortieMoteur` : une entrée `<tache>.<métrique>` par
valeur, `<tache>.<métrique>_stderr` pour l'erreur standard, `<tache>.n_items`.
"""

from __future__ import annotations

import json
import os
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


def graine(config: BenchmarkConfig) -> int:
    return int(config.options.get("seed", SEED_DEFAUT))


def taille_lot(config: BenchmarkConfig) -> str:
    return str(config.options.get("batch_size", BATCH_DEFAUT))


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
        "hf",
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


INDICES_HORS_LIGNE = ("offline", "couldn't reach", "cannot find", "connectionerror", "not found")


def _lancer(
    commande: list[str], dossier_sortie: Path, env: Mapping[str, str], config: BenchmarkConfig
) -> SortieMoteur:
    dossier_sortie.mkdir(parents=True, exist_ok=True)
    fin = lancer_outil(commande, env_supplementaire=env)
    if fin.returncode != 0:
        queue = (fin.stderr or fin.stdout or "").strip()[-600:]
        indice = ""
        if any(m in queue.lower() for m in INDICES_HORS_LIGNE) and not config.jeux:
            indice = (
                " [jeu ou ressource introuvable hors ligne : ce benchmark n'épingle aucun jeu "
                "(`[[jeux]]`), lm_eval lit le cache HF local ; le remplir avant (HF_HOME)]"
            )
        raise LmEvalEchoue(f"lm_eval a échoué (code {fin.returncode}) : {queue}{indice}")
    chemin = trouver_sortie(dossier_sortie)
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LmEvalEchoue(f"sortie lm_eval illisible ({chemin}) : {exc}") from exc
    sortie = analyser(donnees)
    sortie.details["sortie_json"] = str(chemin)
    sortie.seed = graine(config)
    sortie.batch_size = taille_lot(config) if config.cible == "hf" else "1"
    return sortie


def resoudre_gguf(contexte: ContexteBench) -> tuple[str, Any, Path]:
    """`(slug, ConfigModele, GGUF)` de la variante ; `ConfigurationInvalide` si introuvable.

    `base:<slug>` : seul le GGUF q4_k_m (variante `apres`) existe. `ft:<export>` : GGUF
    `modele-f16.gguf` ou `modele-q4_k_m.gguf` du run d'export.
    """
    from slmsp.core.artefacts import ouvrir_run
    from slmsp.inference.serveur import charger_config_modele

    quantification = "f16" if contexte.variante == "avant" else "q4_k_m"
    genre, valeur = contexte.modele_ref.split(":", 1)
    if genre == "base":
        if quantification != "q4_k_m":
            raise ConfigurationInvalide(f"aucun GGUF F16 de base pour {contexte.modele_ref}")
        config = charger_config_modele(valeur)
        gguf = dossier_modeles() / valeur / "gguf" / config.gguf.fichier
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
        commande = [
            *commande_lm_eval(),
            *arguments_hf(poids, taille_lot(config)),
            *arguments_communs(config, sortie),
        ]
        return _lancer(commande, sortie, env, config)
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
