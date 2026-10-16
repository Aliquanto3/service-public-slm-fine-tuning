"""Variante QLoRA Unsloth, en sous-processus isolé (story 10.5, AD-2, AD-18, FR-33).

`slmsp` n'importe jamais `unsloth` : `entrainer` écrit le jeu **déjà pré-tokenisé** par
`train.masque` (`input_ids` et `labels`, donc le masque de M1, jamais recalculés côté
Unsloth) et une configuration JSON, puis lance `envs/unsloth/entrainer.py` par
`uv run --frozen --project envs/unsloth` avec `env_sous_processus()`. Il archive dans le run
l'adaptateur (`adaptateur/`), les coûts (`couts.json`, `metriques.jsonl`, même
`MesuresCout` que les autres méthodes) et les pertes. L'appelant (`train.run`) tient le
`gpu.lock`. Cette variante mesure la vitesse : ce n'est pas une méthode comptée.

Énergie et VRAM NVML sont relevées ici, par le parent, sur la fenêtre d'entraînement que le
sous-processus rapporte (horloge murale) ; le débit, la durée et la VRAM torch viennent du
sous-processus. Pas de reprise sur checkpoint pour cette variante.
"""

from __future__ import annotations

import importlib
import json
import shutil
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Final

from slmsp.core.artefacts import ArtefactExistant, Run
from slmsp.core.config import env_sous_processus
from slmsp.core.erreurs import SlmspError
from slmsp.inference import processus
from slmsp.train.config import charger_config_couts
from slmsp.train.couts import (
    NOM_METRIQUES,
    EchantillonneurNvml,
    MesuresCout,
    ecrire_mesures,
    integrer_energie_wh,
)
from slmsp.train.environnement import (
    chemin_portable,
    commande_portable,
    deborde,
    dossier_travail_unsloth,
    json_sur,
    lire_resultat_unsloth,
    projet_unsloth,
)

NOM_SCRIPT: Final = "entrainer.py"
NOM_JEU: Final = "jeu-tokenise.json"
NOM_ENTREE: Final = "entree-unsloth.json"
NOM_JOURNAL: Final = "log-unsloth.txt"
NOM_LOG: Final = "log.jsonl"
DOSSIER_ADAPTATEUR: Final = "adaptateur"
DOSSIER_CHECKPOINTS: Final = "checkpoints"
FICHIERS_ADAPTATEUR: Final = ("adapter_config.json", "adapter_model.safetensors")
DELAI: Final = 6 * 3600.0
CHECKPOINTING_DEFAUT: Final = True
"""W4.5 : checkpointing standard ; `"unsloth"` déporte les activations en RAM CPU."""


class ErreurUnsloth(SlmspError):
    """Le sous-processus Unsloth a échoué ou n'a pas rendu un adaptateur complet."""


def commande(entree: Path, *, uv: str | None = None) -> list[str]:
    """`uv run --frozen --project envs/unsloth python envs/unsloth/entrainer.py <entree>`."""
    executable = uv or shutil.which("uv")
    if not executable:
        raise FileNotFoundError("exécutable uv introuvable dans le PATH")
    projet = projet_unsloth()
    return [
        executable,
        "run",
        "--frozen",
        "--project",
        str(projet),
        "python",
        str(projet / NOM_SCRIPT),
        str(entree),
    ]


def ecrire_jeu(chemin: Path, exemples: Sequence[Mapping[str, Sequence[int]]], pad_id: int) -> Path:
    """Jeu pré-tokenisé tel que produit par `chargement.pretokeniser` (ids et labels)."""
    contenu = {
        "pad_token_id": int(pad_id),
        "exemples": [
            {"input_ids": list(e["input_ids"]), "labels": list(e["labels"])} for e in exemples
        ],
    }
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(contenu, ensure_ascii=True), encoding="utf-8")
    return chemin


def construire_entree(
    run: Run,
    *,
    jeu: Path,
    dossier_poids: Path,
    arguments: Mapping[str, Any],
    longueur: int,
    graine: int,
    lora: Mapping[str, Any],
    pas_chauffe: int,
    checkpointing: bool | str = CHECKPOINTING_DEFAUT,
) -> dict[str, Any]:
    """Configuration JSON du sous-processus (chemins absolus : écrite sous `SLMSP_VAR_DIR`)."""
    return {
        "dossier_poids": str(dossier_poids),
        "jeu": str(jeu),
        "dossier_adaptateur": str(run.dossier / DOSSIER_ADAPTATEUR),
        "longueur": int(longueur),
        "graine": int(graine),
        "lora": dict(lora),
        "checkpointing": checkpointing,
        "pas_chauffe": int(pas_chauffe),
        "arguments": json_sur(dict(arguments)),
    }


def controler_quantification(quantification: Mapping[str, Any] | None) -> list[str]:
    """Avertissements si la quantification appliquée n'est pas nf4 avec double quantification.

    Le TRL + PEFT de M1 impose nf4, double quantification, calcul bf16 (`config_bnb`).
    """
    q = quantification or {}
    if not q:
        return ["quantification Unsloth non relevée : nf4 avec double quantification non prouvée"]
    avertissements = []
    if not q.get("load_in_4bit"):
        avertissements.append("Unsloth : load_in_4bit absent de la quantification appliquée")
    if q.get("bnb_4bit_quant_type") != "nf4":
        avertissements.append(f"Unsloth : quantification {q.get('bnb_4bit_quant_type')!r}, pas nf4")
    if not q.get("bnb_4bit_use_double_quant"):
        avertissements.append("Unsloth : double quantification absente (diffère de M1)")
    return avertissements


def mesures_depuis(
    resultat: Mapping[str, Any],
    *,
    periode: float,
    releves: Sequence[tuple[float, float | None, int | None]] = (),
    avertissements: Sequence[str] = (),
) -> MesuresCout:
    """`MesuresCout` d'un résultat du sous-processus, plus les relevés NVML du parent.

    Les relevés (horloge murale) sont limités à la fenêtre `debut_epoch`–`fin_epoch`.
    """
    debut, fin = resultat.get("debut_epoch"), resultat.get("fin_epoch")
    dedans = [r for r in releves if debut is None or fin is None or debut <= r[0] <= fin]
    puissances = [(t, w) for t, w, _ in dedans if w is not None]
    energie = integrer_energie_wh(puissances)
    moyenne = sum(w for _, w in puissances) / len(puissances) if puissances else None
    utilises = [u for _, _, u in dedans if u is not None]
    vram_nvml = max(utilises) if utilises else None
    alloue = resultat.get("max_memory_allocated")
    reserve = resultat.get("max_memory_reserved")
    sources = [v for v in (alloue, reserve, vram_nvml) if v is not None]
    notes = list(avertissements)
    if energie is None:
        notes.append("moins de deux relevés de puissance : énergie non mesurée")
    if resultat.get("debit_tokens_par_s") is None:
        notes.append("pas assez de pas après la chauffe : débit non publié")
    return MesuresCout(
        duree_s=float(resultat.get("duree_s") or 0.0),
        pas=int(resultat.get("pas") or 0),
        pas_chauffe=int(resultat.get("pas_chauffe") or 0),
        pas_mesures=max(0, int(resultat.get("pas") or 0) - int(resultat.get("pas_chauffe") or 0)),
        tokens_mesures=resultat.get("tokens_mesures"),
        duree_mesuree_s=resultat.get("duree_mesuree_s"),
        debit_tokens_par_s=resultat.get("debit_tokens_par_s"),
        vram_max_allocated_octets=alloue,
        vram_max_reserved_octets=reserve,
        vram_max_nvml_octets=vram_nvml,
        vram_max_octets=max(sources) if sources else None,
        energie_wh=energie,
        puissance_moyenne_w=moyenne,
        releves_nvml=len(dedans),
        periode_echantillonnage=periode,
        avertissements=notes,
    )


def _echantillonneur(periode: float, indice: int) -> EchantillonneurNvml | None:
    try:
        nvml = importlib.import_module("pynvml")
    except Exception:  # ImportError, mais aussi OSError (bibliothèque NVML introuvable)
        return None
    echantillonneur = EchantillonneurNvml(nvml, periode, indice, horloge=time.time)
    return echantillonneur if echantillonneur.ouvrir() else None


def entrainer(
    run: Run,
    *,
    exemples: Sequence[Mapping[str, Sequence[int]]],
    pad_id: int,
    dossier_poids: Path,
    arguments: Mapping[str, Any],
    longueur: int,
    graine: int,
    lora: Mapping[str, Any],
    checkpointing: bool | str = CHECKPOINTING_DEFAUT,
    racine: Path | None = None,
    executer: Callable[..., tuple[int, str]] | None = None,
    delai: float = DELAI,
    contexte: Mapping[str, Any] | None = None,
    nvml: bool = True,
) -> dict[str, Any]:
    """Entraîne dans `envs/unsloth` et archive adaptateur, coûts et pertes dans `run`.

    `arguments` : arguments `SFTConfig` complets (`methodes.arguments_entrainement`), dont
    `output_dir` sous `run/checkpoints/`. Lève `ErreurUnsloth` si le sous-processus échoue ou
    si l'adaptateur est incomplet, et `ArtefactExistant` si `adaptateur/` existe déjà.
    Renvoie un résumé (débit, VRAM, débordement, avertissements).
    """
    adaptateur = run.dossier / DOSSIER_ADAPTATEUR
    if adaptateur.exists():
        raise ArtefactExistant(f"{adaptateur} existe déjà : l'adaptateur n'est jamais écrasé")
    executer = executer or processus.executer
    config_couts = charger_config_couts()
    travail = dossier_travail_unsloth() / run.run_id
    travail.mkdir(parents=True, exist_ok=True)
    jeu = ecrire_jeu(travail / NOM_JEU, exemples, pad_id)
    entree = construire_entree(
        run,
        jeu=jeu,
        dossier_poids=dossier_poids,
        arguments=arguments,
        longueur=longueur,
        graine=graine,
        lora=lora,
        pas_chauffe=config_couts.pas_chauffe,
        checkpointing=checkpointing,
    )
    fichier = travail / NOM_ENTREE
    fichier.write_text(json.dumps(entree, ensure_ascii=True, indent=2), encoding="utf-8")
    portable = {
        **entree,
        "dossier_poids": chemin_portable(dossier_poids, racine=racine),
        "jeu": f"$SLMSP_VAR_DIR/unsloth/{run.run_id}/{NOM_JEU}",
        "dossier_adaptateur": DOSSIER_ADAPTATEUR,
        "arguments": {
            **entree["arguments"],
            "output_dir": chemin_portable(arguments["output_dir"], racine=run.dossier.parent),
        },
    }
    run.ecrire(NOM_ENTREE, json.dumps(portable, ensure_ascii=True, indent=2, sort_keys=True) + "\n")
    arguments_cmd = commande(fichier)
    run.ajouter_jsonl(
        NOM_LOG,
        {
            "evenement": "unsloth-demarrage",
            "commande": commande_portable(arguments_cmd, racine=racine),
        },
    )

    echantillonneur = _echantillonneur(
        config_couts.periode_echantillonnage, config_couts.indice_gpu
    )
    if not nvml:
        echantillonneur = None
    if echantillonneur is not None:
        echantillonneur.demarrer()
    try:
        code, sortie = executer(
            arguments_cmd,
            delai=delai,
            role="unsloth-entrainement",
            journal=run.dossier / NOM_JOURNAL,
            env=env_sous_processus(),
            cwd=travail,  # Unsloth écrit `unsloth_compiled_cache/` dans le dossier courant
        )
    finally:
        if echantillonneur is not None:
            echantillonneur.arreter()
    resultat = lire_resultat_unsloth(sortie)
    if code != 0 or resultat is None or not resultat.get("ok"):
        detail = (resultat or {}).get("erreur") or f"code {code} ; fin : {sortie[-1500:].strip()}"
        run.ajouter_jsonl(NOM_LOG, {"evenement": "unsloth-echec", "erreur": str(detail)[:2000]})
        raise ErreurUnsloth(f"entraînement Unsloth en échec : {detail}")
    manquants = [f for f in FICHIERS_ADAPTATEUR if not (adaptateur / f).is_file()]
    if manquants:
        raise ErreurUnsloth(f"adaptateur Unsloth incomplet : {', '.join(manquants)} absent(s)")

    avertissements = controler_quantification(resultat.get("quantification"))
    depasse = deborde(resultat.get("max_memory_reserved"), resultat.get("memoire_totale"))
    if depasse:
        avertissements.append("VRAM réservée au-delà du seuil de débordement (mémoire partagée)")
    for point in resultat.get("pertes") or []:
        run.ajouter_jsonl(NOM_METRIQUES, {"evenement": "perte", **point})
    releves = echantillonneur.instantane() if echantillonneur is not None else []
    mesures = mesures_depuis(
        resultat,
        periode=config_couts.periode_echantillonnage,
        releves=releves,
        avertissements=avertissements,
    )
    if contexte is None:
        ecrire_mesures(run, mesures)
    else:
        ecrire_mesures(run, mesures, contexte)
    run.ajouter_jsonl(NOM_LOG, {"evenement": "adaptateur", "dossier": DOSSIER_ADAPTATEUR})
    return {
        "debit_tokens_par_s": mesures.debit_tokens_par_s,
        "vram_max_octets": mesures.vram_max_octets,
        "debordement": depasse,
        "quantification": resultat.get("quantification"),
        "versions": resultat.get("versions"),
        "avertissements": mesures.avertissements,
    }
