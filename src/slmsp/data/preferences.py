"""Paires de préférence ORPO : `data build --preferences` (story 9.7, FR-34, D-nuit-A1-21).

`lancer_preferences` lit le jeu SFT d'un run `data-build` (`data/train/vN/train.jsonl`, SHA-256
revérifié contre le MANIFEST) et, pour chaque exemple, fait de sa dernière réponse `assistant`
la réponse `chosen`. La réponse `rejected` est une génération du Modèle de base local
(`LlmPort`, graine et température de `[preferences]` dans `config/donnees.toml`), journalisée
dans `SLMSP_VAR_DIR/generations-locales.sqlite` (`generateur = slm:<slug>`).

Sont écartées et comptées : les paires dont les deux réponses sont identiques après
normalisation (`identique`), une génération vide (`vide`), une génération qui n'est pas du texte
(appel d'outil, `non_texte`), une génération tronquée par `max_tokens` (`tronquee`) ou
interrompue (`interrompue`, flux coupé ou sans `Fin`), une conversation invalide
(`conversation_invalide`) et un `chosen` sans texte (`chosen_sans_texte`).

Le résultat est une **nouvelle version** `data/train/vN/` (une version n'est jamais réécrite)
qui contient `preferences.jsonl` et un `MANIFEST.json` (`ManifestePreferences`, contrat lu par
`train.chargement` : `sha256_preferences`) décrivant la dérogation FR-34. Aucun verdict du Juge
n'est lu ni utilisé. Les prompts sont ceux du jeu SFT : aucun texte n'est rédigé ici (D1.1) ;
le modèle local reçoit la conversation et les outils de l'exemple SFT (`tools`, traités selon
le protocole du Modèle par le client, comme au rendu de `train.chargement`).
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Final

from pydantic import ValidationError

from slmsp.core.artefacts import Run, lire, nouveau_run, ouvrir_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import ManifesteInvalide, ProvenanceInvalide
from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton
from slmsp.core.messages import ConversationInvalide, valider_conversation
from slmsp.core.ports import LlmPort
from slmsp.core.schemas.entrainement import (
    DEROGATION_ORPO,
    TYPE_RUN_BUILD,
    EnteteManifesteJeu,
    LigneEntrainement,
    ManifestePreferences,
    MetaPaire,
    PairePreference,
)
from slmsp.data.build import _creer_version
from slmsp.data.config import PreferencesDonnees
from slmsp.inference.journal_local import JournalLocal

__all__ = [
    "NOM_ECARTEES",
    "NOM_MANIFEST",
    "NOM_PREFERENCES",
    "ResultatPreferences",
    "lancer_preferences",
    "normaliser",
]

NOM_PREFERENCES: Final = "preferences.jsonl"
NOM_MANIFEST: Final = "MANIFEST.json"
NOM_ECARTEES: Final = "ecartees.jsonl"
NOM_RAPPORT: Final = "rapport.json"
_RE_VERSION: Final = re.compile(r"v[0-9]+")
_RE_ESPACES: Final = re.compile(r"\s+")


@dataclass(frozen=True)
class ResultatPreferences:
    """Run produit, version écrite et rapport."""

    run: Run
    version: str
    dossier: Path
    rapport: dict[str, Any]


def normaliser(texte: str) -> str:
    """Forme comparée de deux réponses : NFKC, minuscules, espaces repliés."""
    return _RE_ESPACES.sub(" ", unicodedata.normalize("NFKC", texte)).strip().casefold()


def _jeu_sft(build_run_id: str, base: Path) -> tuple[str, dict[str, Any], bytes]:
    """Version, MANIFEST et octets de `train.jsonl` du run `data-build` `build_run_id`."""
    run = ouvrir_run(build_run_id, racine=base)
    if run.type != TYPE_RUN_BUILD:
        raise ManifesteInvalide(f"run {build_run_id} : type {run.type!r}, {TYPE_RUN_BUILD} attendu")
    if run.statut_courant() == "en_cours":
        raise ManifesteInvalide(f"run {build_run_id} encore en cours")
    train = base / "data" / "train"
    for dossier in sorted(train.iterdir()) if train.is_dir() else []:
        manifeste_chemin = dossier / NOM_MANIFEST
        if not _RE_VERSION.fullmatch(dossier.name) or not manifeste_chemin.is_file():
            continue
        brut = json.loads(lire(manifeste_chemin, "train", racine=base))
        if brut.get("run_id") != build_run_id:
            continue
        EnteteManifesteJeu.model_validate(brut)
        attendu = brut.get("sha256_train")
        if attendu is None or not (dossier / "train.jsonl").is_file():
            raise ManifesteInvalide(f"{manifeste_chemin} : jeu SFT attendu (sha256_train absent)")
        octets = lire(dossier / "train.jsonl", "train", racine=base)
        if sha256_hex(octets) != attendu:
            raise ProvenanceInvalide(f"{dossier / 'train.jsonl'} : SHA-256 différent du MANIFEST")
        return dossier.name, brut, octets
    raise ManifesteInvalide(f"aucun jeu data/train/vN issu du run {build_run_id}")


def _texte(reponse: dict[str, Any]) -> str | None:
    contenu = reponse.get("content")
    return contenu if isinstance(contenu, str) and contenu.strip() else None


_MOTIFS_FIN: Final = {"longueur": "tronquee", "interrompue": "interrompue"}


def _generer(
    llm: LlmPort,
    prompt: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None,
    options: dict[str, Any],
) -> tuple[str | None, str | None]:
    """`(texte, motif)` d'une génération locale.

    `texte` est `None` pour un appel d'outil (motif `non_texte`) ; `motif` vaut `tronquee`
    (`Fin` de raison `longueur`) ou `interrompue` (raison `interrompue`, ou flux sans `Fin`),
    `None` pour une génération terminée normalement.
    """
    morceaux: list[str] = []
    for evenement in llm.generer(prompt, tools=tools, options=options):
        if isinstance(evenement, Jeton):
            morceaux.append(evenement.texte)
        elif isinstance(evenement, AppelOutil | AppelNonConforme):
            return None, "non_texte"
        elif isinstance(evenement, Fin):
            return "".join(morceaux), _MOTIFS_FIN.get(evenement.raison)
    return "".join(morceaux), "interrompue"


def lancer_preferences(
    *,
    racine: str | Path,
    build_run_id: str,
    modele: str,
    llm: LlmPort,
    config: PreferencesDonnees,
    journal: JournalLocal | None = None,
    consigner: Callable[[str], None] = print,
) -> ResultatPreferences:
    """Construit `data/train/vN/preferences.jsonl` depuis le jeu SFT du run `build_run_id`.

    `modele` : `base:<slug>` (journalisé comme `slm:<slug>`). Avant tout run, `ManifesteInvalide`
    (run absent, d'un autre type, en cours, ou sans jeu SFT) ou `ProvenanceInvalide` (SHA du jeu
    altéré). Sans aucune paire retenue, le run est clos `partiel-erreur` et rien n'est écrit
    sous `data/train/`.
    """
    slug = modele.removeprefix("base:") if modele.startswith("base:") else ""
    if not slug:
        raise ValueError(f"modèle {modele!r} : forme attendue base:<slug>")
    base = Path(racine).resolve()
    version_sft, manifeste_sft, octets = _jeu_sft(build_run_id, base)
    try:
        lignes = [
            LigneEntrainement.model_validate_json(texte)
            for texte in octets.decode("utf-8").splitlines()
            if texte.strip()
        ]
    except ValidationError as exc:
        raise ManifesteInvalide(f"jeu {version_sft} : ligne SFT non conforme ({exc})") from None
    journal = journal if journal is not None else JournalLocal()
    run = nouveau_run(
        TYPE_RUN_BUILD,
        "preferences",
        {
            "build_run_id": build_run_id,
            "jeu_sft_version": version_sft,
            "modele": modele,
            "generateur": f"slm:{slug}",
            "graine": config.graine,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "tools_rejected": "outils de l'exemple SFT",
        },
        parents=[build_run_id],
        graine=config.graine,
        racine=base,
    )
    paires: list[PairePreference] = []
    ecartees: Counter[str] = Counter()
    try:
        for rang, ligne in enumerate(lignes):
            prompt, chosen = ligne.messages[:-1], [ligne.messages[-1]]
            texte_choisi = _texte(chosen[0])
            generation: str | None = None
            appel_id = ""
            motif: str | None = None
            if texte_choisi is None:
                motif = "chosen_sans_texte"
            else:
                options = {
                    "temperature": config.temperature,
                    "seed": config.graine + rang,
                    "max_tokens": config.max_tokens,
                }
                generation, motif = _generer(llm, prompt, ligne.tools, options)
                appel_id = journal.inscrire(
                    session_id=ligne.meta.session_id,
                    slug=slug,
                    requete={
                        "messages": prompt,
                        "tools": ligne.tools,
                        "options": options,
                        "rang": rang,
                    },
                    reponse=generation,
                    statut="ok" if motif is None else motif.replace("_", "-"),
                )
                if motif is not None or generation is None:
                    motif = motif or "non_texte"
                elif not generation.strip():
                    motif = "vide"
                elif normaliser(generation) == normaliser(texte_choisi):
                    motif = "identique"
                else:
                    try:
                        valider_conversation(
                            [*prompt, {"role": "assistant", "content": generation}]
                        )
                    except ConversationInvalide:
                        motif = "conversation_invalide"
            if motif is not None or generation is None:
                motif = motif or "non_texte"
                ecartees[motif] += 1
                run.ajouter_jsonl(NOM_ECARTEES, {"rang": rang, "motif": motif})
                continue
            paires.append(
                PairePreference(
                    prompt=prompt,
                    chosen=chosen,
                    rejected=[{"role": "assistant", "content": generation}],
                    tools=ligne.tools,
                    tache=ligne.tache,
                    meta=MetaPaire(
                        appel_ids=ligne.meta.appel_ids,
                        session_id=ligne.meta.session_id,
                        generateur_rejected=f"slm:{slug}",
                        appel_local_id=appel_id,
                        source=ligne.meta.source,
                        licence=ligne.meta.licence,
                    ),
                )
            )
        if not paires:
            raise ManifesteInvalide(f"jeu {version_sft} : aucune paire retenue ({dict(ecartees)})")
        version, dossier, rapport = _ecrire_version(
            base,
            run,
            paires,
            ecartees,
            build_run_id=build_run_id,
            version_sft=version_sft,
            manifeste_sft=manifeste_sft,
            modele=modele,
            slug=slug,
            config=config,
        )
    except KeyboardInterrupt:
        run.terminer("interrompu", "interruption clavier")
        raise
    except BaseException as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
        raise
    run.terminer("complet")
    consigner(
        f"paires {version} : {len(paires)} paires, {sum(ecartees.values())} écartées, "
        f"sha256 {rapport['sha256_preferences']}"
    )
    return ResultatPreferences(run=run, version=version, dossier=dossier, rapport=rapport)


def _ecrire_version(
    base: Path,
    run: Run,
    paires: list[PairePreference],
    ecartees: Counter[str],
    *,
    build_run_id: str,
    version_sft: str,
    manifeste_sft: dict[str, Any],
    modele: str,
    slug: str,
    config: PreferencesDonnees,
) -> tuple[str, Path, dict[str, Any]]:
    """Écrit `vN/{preferences.jsonl, MANIFEST.json}` puis le rapport du run.

    Le MANIFEST est écrit en dernier (fichier temporaire puis renommage) : une `vN` sans
    MANIFEST n'est pas lisible par `train.chargement`, et toute erreur close le run
    `partiel-erreur` chez l'appelant.
    """
    contenu = b"".join(json_canonique(p.model_dump(mode="json")) + b"\n" for p in paires)
    version, dossier = _creer_version(base)
    (dossier / NOM_PREFERENCES).write_bytes(contenu)
    sha_preferences = sha256_hex(contenu)
    comptes = dict(sorted(Counter(p.tache for p in paires).items()))
    manifeste = ManifestePreferences(
        version=version,
        run_id=run.run_id,
        variante=manifeste_sft["variante"],
        cree_le=date.today(),
        build_run_id=build_run_id,
        jeu_sft_version=version_sft,
        sha256_train=manifeste_sft["sha256_train"],
        sha_outils_mcp=manifeste_sft.get("sha_outils_mcp"),
        sha256_preferences=sha_preferences,
        nb_paires=len(paires),
        comptes_par_tache=comptes,
        ecartees_par_motif=dict(sorted(ecartees.items())),
        modele=modele,
        generateur_rejected=f"slm:{slug}",
        graine=config.graine,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        derogation_fr34=DEROGATION_ORPO,
    )
    temporaire = dossier / f"{NOM_MANIFEST}.tmp"
    temporaire.write_bytes(json_canonique(manifeste.model_dump(mode="json")) + b"\n")
    temporaire.replace(dossier / NOM_MANIFEST)
    rapport = {
        "schema_version": 1,
        "version": version,
        "jeu_sft_version": version_sft,
        "nb_paires": len(paires),
        "comptes_par_tache": comptes,
        "ecartees_par_motif": manifeste.ecartees_par_motif,
        "sha256_preferences": sha_preferences,
    }
    run.ecrire(NOM_RAPPORT, json_canonique(rapport) + b"\n")
    return version, dossier, rapport
