"""Orchestrateur de benchmarks : sélection, verrou GPU, run `bench`, un résultat par benchmark.

Chaque benchmark (et chaque variante avant/après quantification) est confié au moteur que
nomme sa configuration. Une erreur d'un benchmark ne stoppe pas les autres : le run se
termine en `partiel-erreur` (AC 7). Le run écrit `runs/bench/<run_id>/<benchmark>--<variante>.json`
(un `ResultatBench`) ; l'environnement figure dans `run.json`.
"""

from __future__ import annotations

import re
import time
from collections.abc import Callable, Sequence
from contextlib import nullcontext
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from slmsp.benchmarks.config import BenchmarkConfig, Cible, Quantification
from slmsp.benchmarks.moteurs import ContexteBench, SortieMoteur, charger_moteur, moteur_connu
from slmsp.core.artefacts import Run, nouveau_run
from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import ConfigurationInvalide, SlmspError
from slmsp.core.schemas.bench import ConfigurationExecution, ResultatBench, Variante
from slmsp.core.schemas.run import ModeleRef
from slmsp.core.var import verrou_gpu

TYPE_RUN = "bench"


@dataclass(frozen=True)
class Selection:
    """Un benchmark et les variantes à exécuter."""

    config: BenchmarkConfig
    variantes: list[Variante]


@dataclass
class RapportBench:
    """Issue d'un run `bench`."""

    run: Run
    statut: str
    resultats: list[ResultatBench] = field(default_factory=list)


def selectionner(
    configs: dict[str, BenchmarkConfig],
    *,
    socle: bool = False,
    noms: Sequence[str] = (),
    cible: Cible | None = None,
    quantification: Quantification | None = None,
) -> list[Selection]:
    """Benchmarks à lancer : le socle ou les `noms`, filtrés par cible et quantification.

    Lève `ConfigurationInvalide` pour un nom inconnu, un moteur inconnu, ou une sélection
    vide. Le filtre `quantification` restreint les variantes (`les-deux` : aucune
    restriction) ; un benchmark sans variante restante est écarté.
    """
    if socle == bool(noms):
        raise ConfigurationInvalide("donner --socle ou --benchmarks (l'un des deux, pas les deux)")
    if socle:
        choisis = [config for config in configs.values() if config.socle]
    else:
        inconnus = [nom for nom in noms if nom not in configs]
        if inconnus:
            raise ConfigurationInvalide(
                f"benchmark inconnu : {', '.join(inconnus)} (connus : {', '.join(configs)})"
            )
        choisis = [configs[nom] for nom in dict.fromkeys(noms)]
    sans_moteur = [f"{c.nom} (moteur {c.moteur})" for c in choisis if not moteur_connu(c.moteur)]
    if sans_moteur:
        raise ConfigurationInvalide(f"moteur inconnu : {', '.join(sans_moteur)}")
    selection = []
    for config in choisis:
        if cible is not None and config.cible != cible:
            continue
        variantes = config.variantes()
        if quantification in ("avant", "apres"):
            variantes = [v for v in variantes if v == quantification]
        if variantes:
            selection.append(Selection(config, variantes))
    if not selection:
        raise ConfigurationInvalide("aucun benchmark ne correspond à la sélection et aux filtres")
    return selection


def _jeu_version(config: BenchmarkConfig) -> str | None:
    versions = [f"{jeu.depot}@{jeu.revision}" for jeu in config.jeux if jeu.revision]
    return ", ".join(versions) or None


def _precision_gguf(config: BenchmarkConfig, variante: Variante, modele_ref: str) -> str | None:
    """Précision réelle du GGUF servi (`f16`, `bf16`, `q4_k_m`) ; None hors GGUF résolu.

    La variante `avant` d'un `base:<slug>` sert `[gguf_f16]`, parfois en BF16 : la clé de
    variante reste `avant`, la précision est consignée dans le résultat.
    """
    if config.cible != "gguf" or config.options.get("base_url"):
        return None
    quantification = "f16" if variante == "avant" else "q4_k_m"
    genre, slug = modele_ref.split(":", 1)
    if genre != "base":
        return quantification
    from slmsp.inference.serveur import charger_config_modele

    try:
        return charger_config_modele(slug).precision_gguf(quantification)
    except Exception:  # métadonnée seulement : l'erreur éventuelle vient du moteur
        return None


def _gpu_requis(selection: Sequence[Selection], variante_llamacpp: str) -> bool:
    """Cible `hf`, ou GGUF servi par la variante llama.cpp CUDA."""
    return any(s.config.cible == "hf" for s in selection) or (
        variante_llamacpp == "cuda" and any(s.config.cible == "gguf" for s in selection)
    )


def _slug(modele_ref: str) -> str:
    return re.sub(r"[^a-z0-9.-]", "-", modele_ref.split(":", 1)[1].lower())


def _executer_un(
    config: BenchmarkConfig, variante: Variante, contexte: ContexteBench
) -> ResultatBench:
    debut = time.monotonic()
    commun = {
        "run_id": contexte.run.run_id,
        "benchmark": config.nom,
        "moteur": config.moteur,
        "tache": config.tache,
        "modele_ref": contexte.modele_ref,
        "variante": variante,
        "cible": config.cible,
        "precision_gguf": _precision_gguf(config, variante, contexte.modele_ref),
    }

    def configuration(sortie: SortieMoteur | None = None) -> ConfigurationExecution:
        return ConfigurationExecution(
            fewshot=config.fewshot,
            limite=config.limite,
            seed=sortie.seed if sortie else None,
            batch_size=sortie.batch_size if sortie else None,
            options=config.options,
        )

    try:
        sortie: SortieMoteur = charger_moteur(config.moteur)(config, contexte)
    except Exception as exc:
        return ResultatBench(
            **commun,
            statut="erreur",
            configuration=configuration(),
            motif=f"{type(exc).__name__} : {exc}",
            jeu_version=_jeu_version(config),
            duree_s=time.monotonic() - debut,
        )
    return ResultatBench(
        **commun,
        configuration=configuration(sortie),
        statut="saute" if sortie.saute else "ok",
        motif=sortie.saute,
        scores=dict(sortie.scores),
        jeu_version=sortie.jeu_version or _jeu_version(config),
        outil=sortie.outil,
        outil_version=sortie.outil_version,
        details=sortie.details,
        duree_s=time.monotonic() - debut,
    )


def _tag_llamacpp(modele_ref: str, racine: Path, selection: Sequence[Selection]) -> str | None:
    """Tag llama.cpp des cibles GGUF (version réservée du modèle, sinon commune), pour
    `run.json` ; `None` sans cible GGUF ou si la configuration du modèle est introuvable (le
    moteur le signale alors)."""
    if not any(s.config.cible == "gguf" for s in selection):
        return None
    from slmsp.core.artefacts import ouvrir_run
    from slmsp.inference.serveur import charger_config_modele, config_llamacpp_modele

    genre, valeur = modele_ref.split(":", 1)
    try:
        if genre == "ft":
            base = ouvrir_run(valeur, racine=racine).manifeste.modele_ref or ""
            valeur = base.removeprefix("base:")
        return config_llamacpp_modele(charger_config_modele(valeur)).tag
    except (SlmspError, OSError, ValueError):
        return None


def lancer(
    modele_ref: str,
    selection: Sequence[Selection],
    *,
    racine: str | Path,
    variante_llamacpp: str = "cpu",
    affichage: Callable[[str], None] = lambda _ligne: None,
) -> RapportBench:
    """Exécute la sélection sous le verrou GPU si nécessaire et rend le rapport.

    Le verrou est pris sans attente (`RessourceOccupee` si le GPU est pris), avant
    l'ouverture du run. Les erreurs des moteurs sont consignées dans les résultats.
    """
    try:
        TypeAdapter(ModeleRef).validate_python(modele_ref)
    except ValidationError:
        raise ConfigurationInvalide(
            f"modèle invalide : {modele_ref!r} (attendu : base:<slug> ou ft:<run_id>)"
        ) from None
    racine = Path(racine).resolve()
    verrou = (
        verrou_gpu(commande=f"slmsp bench run --modele {modele_ref}")
        if _gpu_requis(selection, variante_llamacpp)
        else nullcontext()
    )
    with verrou:
        run = nouveau_run(
            TYPE_RUN,
            _slug(modele_ref),
            {
                "benchmarks": [s.config.nom for s in selection],
                "variantes": {s.config.nom: s.variantes for s in selection},
                "variante_llamacpp": variante_llamacpp,
            },
            racine=racine,
            modele_ref=modele_ref,
            llamacpp_tag=_tag_llamacpp(modele_ref, racine, selection),
        )
        rapport = RapportBench(run, "en_cours")
        contexte_base = {
            "modele_ref": modele_ref,
            "run": run,
            "racine": racine,
            "variante_llamacpp": variante_llamacpp,
        }
        try:
            for choix in selection:
                for variante in choix.variantes:
                    resultat = _executer_un(
                        choix.config, variante, ContexteBench(variante=variante, **contexte_base)
                    )
                    run.ecrire(
                        f"{choix.config.nom}--{variante}.json",
                        json_canonique(resultat.model_dump(mode="json")) + b"\n",
                    )
                    rapport.resultats.append(resultat)
                    affichage(
                        f"{resultat.statut:<7} {choix.config.nom} ({variante})"
                        + (f" : {resultat.motif}" if resultat.motif else "")
                    )
        except KeyboardInterrupt:
            run.terminer("interrompu", "arrêt demandé")
            raise
        except Exception as exc:
            run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
            raise
        erreurs = [r.benchmark for r in rapport.resultats if r.statut == "erreur"]
        rapport.statut = "partiel-erreur" if erreurs else "complet"
        run.terminer(rapport.statut, f"en erreur : {', '.join(erreurs)}" if erreurs else None)
    return rapport


__all__ = ["RapportBench", "Selection", "lancer", "selectionner"]
