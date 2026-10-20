"""Nettoyage déterministe du jeu SFT : `data build --nettoyage` (story 9.9).

`lancer_nettoyage` lit le jeu SFT d'un run `data-build` (SHA revérifié contre son MANIFEST,
comme `preferences._jeu_sft`) et écrit une **nouvelle version** `data/train/vN/` :

1. préambule « Voici … » puis titre de tête (story 9.10 ; sauf CR et CT en version 3) retirés
   de la réponse cible
   (`core.nettoyage.nettoyer_cible`, version `VERSION_NETTOYAGE`) ;
2. cible de plus de `plafond_tokens` tokens (plafond de génération de l'évaluation, tokenizer
   du Modèle de base) **écartée**, jamais tronquée (motif `longueur`, `ecartes.jsonl`) ;
3. fidélité LC **signalée** : nombres, références juridiques et sigles de la source absents de
   la cible (rapport ; l'exemple reste).

Aucun texte n'est rédigé ni réécrit (D1), aucun appel réseau. `core.nettoyage.verifier_nettoyage`
prouve la transformation avant l'écriture du MANIFEST (`nettoyage`, relu par `train.chargement`).
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Final

from pydantic import ValidationError

from slmsp.core.artefacts import Run, lire, nouveau_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.config import dossier_modeles
from slmsp.core.erreurs import ConfigurationInvalide, ManifesteInvalide
from slmsp.core.nettoyage import (
    VERSION_NETTOYAGE,
    analyser_cible,
    cible_nettoyable,
    verifier_nettoyage,
)
from slmsp.core.schemas.entrainement import (
    TYPE_RUN_BUILD,
    Ecart,
    LigneEntrainement,
    ManifesteJeuEntrainement,
    Nettoyage,
)
from slmsp.data.build import _creer_version
from slmsp.data.preferences import _jeu_sft

__all__ = [
    "NOM_ECARTES",
    "ResultatNettoyage",
    "Tokeniseur",
    "elements_verifiables",
    "elements_manquants",
    "lancer_nettoyage",
    "tokeniseur_du_modele",
]

NOM_TRAIN: Final = "train.jsonl"
NOM_MANIFEST: Final = "MANIFEST.json"
NOM_ECARTES: Final = "ecartes.jsonl"
NOM_RAPPORT: Final = "rapport.json"
TACHE_HORS_PLANCHER: Final = "CR"
"""Seule Tâche qui peut sortir entièrement du jeu (toutes ses cibles dépassent le plafond)."""
PREFIXE_SOURCE_LC: Final = "Texte :\n"
PREFIXE_CONSIGNE: Final = "Consigne :\n"

_RE_REFERENCE: Final = re.compile(r"\b[Aa]rticles?\s+\d+(?:-\d+)*|\b[LRD]\.\s?\d+(?:-\d+)*")
_RE_NOMBRE: Final = re.compile(
    r"(?<![\d.,])(?:\d{1,3}(?:[ \u00a0\u202f.]\d{3})+|\d+)(?:,\d+)?(?!\d)"
)
"""Nombre entier ou décimal, milliers groupés par espace (U+00A0, U+202F) ou point : jamais
deux nombres distincts reliés (« 2023. 15 » donne « 2023 » et « 15 »)."""
_RE_SIGLE: Final = re.compile(r"\b[A-ZÀ-ÖØ-Þ]{2,}\b")
_RE_ESPACES: Final = re.compile(r"\s+")
_RE_POINT_MILLIERS: Final = re.compile(r"\.(?=\d{3}(?!\d))")


@dataclass(frozen=True)
class Tokeniseur:
    """Compteur de tokens d'une cible (sans tokens spéciaux) et SHA de son `tokenizer.json`."""

    compter: Callable[[str], int]
    sha256: str


@dataclass(frozen=True)
class ResultatNettoyage:
    """Run produit, version écrite et rapport."""

    run: Run
    version: str
    dossier: Path
    rapport: dict[str, Any]


def tokeniseur_du_modele(slug: str, *, racine: str | Path | None = None) -> Tokeniseur:
    """Tokenizer `models/<slug>/hf/tokenizer.json`, lu par le lecteur `train` (AD-24)."""
    chemin = dossier_modeles() / slug / "hf" / "tokenizer.json"
    try:
        octets = lire(chemin, "train", racine=racine)
    except FileNotFoundError:
        raise ConfigurationInvalide(f"tokenizer absent : {chemin}") from None
    try:
        from tokenizers import Tokenizer  # extra `train` (dépendance de transformers)
    except ImportError:
        raise ConfigurationInvalide(
            "paquet tokenizers absent : installer l'extra train (uv sync --extra train)"
        ) from None

    tokenizer = Tokenizer.from_str(octets.decode("utf-8"))
    return Tokeniseur(
        compter=lambda texte: len(tokenizer.encode(texte, add_special_tokens=False).ids),
        sha256=sha256_hex(octets),
    )


def _normaliser(element: str) -> str:
    """Forme comparable d'un élément : NFKC, apostrophe droite, sans espaces (U+00A0, U+202F
    compris), sans `,00` final ni point de milliers ; « Articles » ramené à « article »."""
    forme = unicodedata.normalize("NFKC", element).replace("\u2019", "'")
    forme = _RE_ESPACES.sub("", forme).removesuffix(",00")
    forme = _RE_POINT_MILLIERS.sub("", forme)
    if forme[:7].casefold() == "article":
        forme = "article" + forme[7:].casefold().removeprefix("s")
    return forme


def elements_verifiables(texte: str) -> list[str]:
    """Références juridiques, nombres (deux chiffres ou plus) et sigles de `texte`, en ordre.

    Les nombres sont cherchés hors des références (« L. 123-4 » ne donne pas « 123 »).
    """
    elements = [m.group().strip() for m in _RE_REFERENCE.finditer(texte)]
    reste = _RE_REFERENCE.sub(" ", texte)
    for m in _RE_NOMBRE.finditer(reste):
        if sum(c.isdigit() for c in m.group()) >= 2:
            elements.append(m.group())
    elements.extend(m.group() for m in _RE_SIGLE.finditer(texte))
    return list(dict.fromkeys(elements))


def elements_manquants(source: str, cible: str) -> list[str]:
    """Éléments vérifiables de `source` absents des éléments vérifiables de `cible`.

    Les deux côtés sont extraits, normalisés (`_normaliser`) et comparés élément à élément,
    jamais par sous-chaîne : « 1 500 » n'est pas trouvé dans « 11 500 », ni « article 1 »
    dans « article 12 ». Un signalement à relire, pas un filtre : un nombre écrit en lettres
    ou un sigle développé dans la cible y figure à tort.
    """
    presents = {_normaliser(e) for e in elements_verifiables(cible)}
    return [e for e in elements_verifiables(source) if _normaliser(e) not in presents]


def _source_lc(ligne: dict[str, Any]) -> str | None:
    messages = ligne.get("messages") or []
    contenu = messages[1].get("content") if len(messages) > 1 else None
    if not isinstance(contenu, str):
        return None
    if contenu.startswith(PREFIXE_CONSIGNE):  # consigne d'Agent (story O5) avant le texte
        debut = contenu.find("\n\n" + PREFIXE_SOURCE_LC)
        if debut >= 0:
            contenu = contenu[debut + 2 :]
    return contenu.removeprefix(PREFIXE_SOURCE_LC)


def lancer_nettoyage(
    *,
    racine: str | Path,
    build_run_id: str,
    modele: str,
    plafond_tokens: int,
    tokeniseur: Tokeniseur | None = None,
    consigner: Callable[[str], None] = print,
) -> ResultatNettoyage:
    """Construit `data/train/vN/train.jsonl` nettoyé depuis le jeu SFT du run `build_run_id`.

    `modele` : `base:<slug>` (tokenizer). `plafond_tokens` : `[generation].max_tokens` de
    `config/evaluation.toml`. Avant tout run : `ManifesteInvalide` (run absent, d'un autre
    type, sans jeu SFT, jeu déjà nettoyé ou restreint) ou `ProvenanceInvalide` (SHA altéré).
    Si une Tâche autre que CR tombe à 0 exemple, `ManifesteInvalide` : le run est clos
    `partiel-erreur` et rien n'est écrit sous `data/train/`.
    """
    slug = modele.removeprefix("base:") if modele.startswith("base:") else ""
    if not slug:
        raise ValueError(f"modèle {modele!r} : forme attendue base:<slug>")
    if plafond_tokens < 1:
        raise ValueError(f"plafond de tokens {plafond_tokens} : entier positif attendu")
    base = Path(racine).resolve()
    version_src, manifeste_src, octets = _jeu_sft(build_run_id, base)
    try:
        source = ManifesteJeuEntrainement.model_validate(manifeste_src)
    except ValidationError as exc:
        raise ManifesteInvalide(
            f"jeu {version_src} : MANIFEST de build SFT attendu ({exc})"
        ) from None
    if source.nettoyage is not None:
        raise ManifesteInvalide(f"jeu {version_src} : déjà nettoyé (repartir du jeu source)")
    if source.sous_ensemble is not None:
        raise ManifesteInvalide(
            f"jeu {version_src} : restreint à des Tâches (nettoyer le jeu source, puis restreindre)"
        )
    if source.selection is not None:
        raise ManifesteInvalide(
            f"jeu {version_src} : cibles sélectionnées, déjà nettoyées (repartir du jeu source)"
        )
    try:
        lignes = [json.loads(texte) for texte in octets.split(b"\n") if texte.strip()]
        for ligne in lignes:
            LigneEntrainement.model_validate(ligne)
    except (ValueError, ValidationError) as exc:
        raise ManifesteInvalide(f"jeu {version_src} : ligne SFT non conforme ({exc})") from None
    tokeniseur = tokeniseur or tokeniseur_du_modele(slug, racine=base)
    run = nouveau_run(
        TYPE_RUN_BUILD,
        "nettoyage",
        {
            "nettoyage": True,
            "version_nettoyage": VERSION_NETTOYAGE,
            "build_run_id": build_run_id,
            "jeu_source_version": version_src,
            "modele": modele,
            "plafond_tokens": plafond_tokens,
            "tokenizer_sha256": tokeniseur.sha256,
        },
        parents=[build_run_id],
        racine=base,
    )
    try:
        gardees, ecartes, rapport = _nettoyer(run, lignes, tokeniseur, plafond_tokens)
        avant = Counter(str(ligne["tache"]) for ligne in lignes)
        apres = Counter(str(ligne["tache"]) for ligne in gardees)
        vides = sorted(t for t in avant if t != TACHE_HORS_PLANCHER and not apres[t])
        if vides:
            raise ManifesteInvalide(
                f"Tâche(s) {', '.join(vides)} sans exemple après nettoyage "
                f"(plafond {plafond_tokens} tokens)"
            )
        contenu = b"".join(json_canonique(ligne) + b"\n" for ligne in gardees)
        verifier_nettoyage(contenu, octets, [e.rang for e in ecartes], VERSION_NETTOYAGE)
        version, dossier = _creer_version(base)
        (dossier / NOM_TRAIN).write_bytes(contenu)
        nettoyage = Nettoyage(
            version=VERSION_NETTOYAGE,
            depuis_build=build_run_id,
            depuis_version=version_src,
            sha256_train_source=sha256_hex(octets),
            plafond_tokens=plafond_tokens,
            tokenizer_sha256=tokeniseur.sha256,
            lc_signales=len(rapport["lc_signales"]),
            ecartes=ecartes,
        )
        manifeste = source.model_copy(
            update={
                "version": version,
                "run_id": run.run_id,
                "cree_le": date.today(),
                "sha256_train": sha256_hex(contenu),
                "nb_lignes": len(gardees),
                "comptes_par_tache": dict(sorted(apres.items())),
                "nettoyage": nettoyage,
            }
        )
        manifeste = ManifesteJeuEntrainement.model_validate(manifeste.model_dump(mode="json"))
        rapport = {
            "schema_version": 1,
            "version": version,
            "depuis_build": build_run_id,
            "depuis_version": version_src,
            "version_nettoyage": VERSION_NETTOYAGE,
            "modele": modele,
            "plafond_tokens": plafond_tokens,
            "tokenizer_sha256": tokeniseur.sha256,
            "sha256_train": manifeste.sha256_train,
            "nb_lignes_avant": len(lignes),
            "nb_lignes": len(gardees),
            **rapport,
        }
        run.ecrire(NOM_RAPPORT, json_canonique(rapport) + b"\n")
        # MANIFEST en dernier : sa présence signale une version complète.
        temporaire = dossier / f"{NOM_MANIFEST}.tmp"
        temporaire.write_bytes(json_canonique(manifeste.model_dump(mode="json")) + b"\n")
        temporaire.replace(dossier / NOM_MANIFEST)
    except KeyboardInterrupt:
        run.terminer("interrompu", "interruption clavier")
        raise
    except BaseException as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
        raise
    run.terminer("complet")
    consigner(
        f"nettoyage {version_src} → {version} : {len(lignes)} → {len(gardees)} lignes, "
        f"sha256 {manifeste.sha256_train}"
    )
    return ResultatNettoyage(run=run, version=version, dossier=dossier, rapport=rapport)


_COMPTES: Final = (
    "avant",
    "apres",
    "preambules_retires",
    "preambule_garde",
    "preambule_seul",
    "titres_retires",
    "ecartes_longueur",
    "lc_signales",
)
_STATUTS: Final = {
    "retire": "preambules_retires",
    "garde": "preambule_garde",
    "seul": "preambule_seul",
}


def _nettoyer(
    run: Run, lignes: list[dict[str, Any]], tokeniseur: Tokeniseur, plafond: int
) -> tuple[list[dict[str, Any]], list[Ecart], dict[str, Any]]:
    """Lignes gardées (cibles nettoyées), écarts et parties du rapport ; écrit `ecartes.jsonl`."""
    comptes: dict[str, Counter[str]] = defaultdict(Counter)
    signales: list[dict[str, Any]] = []
    gardees: list[dict[str, Any]] = []
    ecartes: list[Ecart] = []
    for rang, ligne in enumerate(lignes):
        tache = str(ligne["tache"])
        session_id = ligne["meta"]["session_id"]
        comptes[tache]["avant"] += 1
        cible = cible_nettoyable(ligne)
        if cible is not None:
            texte, statut, titre = analyser_cible(cible["content"], VERSION_NETTOYAGE, tache)
            if statut is not None:
                comptes[tache][_STATUTS[statut]] += 1
            comptes[tache]["titres_retires"] += titre
            cible["content"] = texte
            tokens = tokeniseur.compter(texte)
            if tokens > plafond:
                comptes[tache]["ecartes_longueur"] += 1
                ecartes.append(Ecart(rang=rang, motif="longueur", tokens=tokens))
                run.ajouter_jsonl(
                    NOM_ECARTES,
                    {"rang": rang, "session_id": session_id, "tache": tache, "tokens": tokens},
                )
                continue
            source = _source_lc(ligne) if tache == "LC" else None
            if source is not None:
                manquants = elements_manquants(source, texte)
                if manquants:
                    comptes[tache]["lc_signales"] += 1
                    signales.append(
                        {"rang": rang, "session_id": session_id, "manquants": manquants}
                    )
        comptes[tache]["apres"] += 1
        gardees.append(ligne)
    par_tache = {tache: {cle: comptes[tache][cle] for cle in _COMPTES} for tache in sorted(comptes)}
    return gardees, ecartes, {"par_tache": par_tache, "lc_signales": signales}
