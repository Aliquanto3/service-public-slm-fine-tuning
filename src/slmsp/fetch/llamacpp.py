"""Pilote `slmsp fetch llamacpp` : binaires et sources du tag figé (AD-6, AD-28).

La release est lue par l'API GitHub (taille et `digest` de chaque asset, recoupé avec
`config/llamacpp.toml`), puis les quatre archives sont téléchargées par le moteur sous
`vendor/llama.cpp/<tag>/archives/` et extraites :

- `cpu` → `bin-cpu/` ; `cuda` et `cudart` → `bin-cuda/` ;
- sources → `src/`, sans le dossier racine unique de l'archive (`llama.cpp-<tag>/`).

L'extraction n'écrase rien : un fichier déjà présent au même contenu (taille et CRC-32)
est sauté, un fichier différent lève `ArchiveInvalide`. Les membres hostiles (chemin
absolu, lecteur, `..`, lien symbolique, doublon) font refuser l'archive avant toute
écriture. Une archive extraite reçoit un marqueur `<archive>.extrait.json` ; avec ce
marqueur, elle n'est pas rouverte. Aucun binaire n'est lancé (le contrôle `--version`
revient à `slmsp.inference.serveur`, story 2.2).
"""

from __future__ import annotations

import shutil
import stat
import zipfile
import zlib
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Final

from slmsp.core.artefacts import verifier_espace
from slmsp.core.canonique import json_canonique, sha256_fichier
from slmsp.core.schemas.config_llamacpp import ConfigLlamacpp
from slmsp.fetch.config import ConfigTelechargement, chemin_config
from slmsp.fetch.hf import (
    ArchiveInvalide,
    ResultatFichier,
    ShaInvalide,
    TelechargementEchoue,
    Telechargeur,
    horodatage,
    renommer_sans_ecraser,
)

URL_API_RELEASE: Final = "https://api.github.com/repos/{depot}/releases/tags/{tag}"
URL_SOURCES: Final = "https://github.com/{depot}/archive/refs/tags/{tag}.zip"
EN_TETES_API: Final = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
SUFFIXE_MARQUEUR: Final = ".extrait.json"

# Archive → dossier d'extraction (relatif à vendor/llama.cpp/<tag>/), dossier racine retiré.
EXTRACTIONS: Final = (
    ("cpu", "bin-cpu", False),
    ("cuda", "bin-cuda", False),
    ("cudart", "bin-cuda", False),
    ("sources", "src", True),
)


@dataclass(frozen=True)
class ArchivePrevue:
    """Archive à télécharger : clé (`cpu`, `cuda`, `cudart`, `sources`), URL, empreinte."""

    cle: str
    nom: str
    url: str
    sha256: str
    taille: int | None


def dossier_tag(racine: str | Path, config: ConfigLlamacpp) -> Path:
    """`<racine>/vendor/llama.cpp/<tag>`."""
    return Path(racine) / "vendor" / "llama.cpp" / config.tag


def lire_release(telechargeur: Telechargeur, config: ConfigLlamacpp) -> list[ArchivePrevue]:
    """Assets de la release du tag, recoupés avec la configuration.

    Lève `TelechargementEchoue` pour un asset absent ou une réponse illisible, et
    `ShaInvalide` si le `digest` publié diffère du SHA-256 de la configuration.
    """
    url = URL_API_RELEASE.format(depot=config.depot, tag=config.tag)
    reponse = telechargeur.requete("GET", url, headers=EN_TETES_API)
    try:
        donnees = reponse.json()
        publies = {asset["name"]: asset for asset in donnees["assets"]}
    except (ValueError, KeyError, TypeError):
        raise TelechargementEchoue(f"GET {url} : réponse de l'API GitHub illisible") from None
    archives = []
    for cle, asset in config.assets.items():
        publie = publies.get(asset.nom)
        if not isinstance(publie, Mapping) or not isinstance(
            publie.get("browser_download_url"), str
        ):
            raise TelechargementEchoue(f"asset {asset.nom} absent de la release {config.tag}")
        digest = publie.get("digest")
        if isinstance(digest, str) and digest.startswith("sha256:"):
            if digest.removeprefix("sha256:").lower() != asset.sha256:
                raise ShaInvalide(
                    f"asset {asset.nom} : digest publié {digest} différent du SHA-256 "
                    f"de la configuration ({asset.sha256})"
                )
        taille = publie.get("size")
        archives.append(
            ArchivePrevue(
                cle,
                asset.nom,
                publie["browser_download_url"],
                asset.sha256,
                taille if isinstance(taille, int) and taille >= 0 else None,
            )
        )
    return archives


def archive_sources(config: ConfigLlamacpp) -> ArchivePrevue:
    """Archive des sources du tag (taille inconnue : générée à la demande par GitHub)."""
    url = URL_SOURCES.format(depot=config.depot, tag=config.tag)
    return ArchivePrevue("sources", config.sources.nom, url, config.sources.sha256, None)


# --- Extraction ------------------------------------------------------------------------


def _relatif_membre(info: zipfile.ZipInfo) -> PurePosixPath:
    nom = info.filename.replace("\\", "/")
    mode = (info.external_attr >> 16) & 0o170000
    if mode == stat.S_IFLNK:
        raise ArchiveInvalide(f"membre {info.filename!r} : lien symbolique refusé")
    if not nom or nom.startswith("/") or ":" in nom:
        raise ArchiveInvalide(f"membre {info.filename!r} : chemin absolu refusé")
    parties = [partie for partie in nom.split("/") if partie not in ("", ".")]
    if not parties or any(partie == ".." for partie in parties):
        raise ArchiveInvalide(f"membre {info.filename!r} : chemin hors de la cible refusé")
    if any(partie != partie.rstrip(". ") for partie in parties):
        raise ArchiveInvalide(f"membre {info.filename!r} : nom ambigu sous Windows refusé")
    return PurePosixPath(*parties)


def membres_valides(
    archive: zipfile.ZipFile, cible: Path, *, retirer_racine: bool
) -> list[tuple[zipfile.ZipInfo, PurePosixPath]]:
    """Fichiers de l'archive et leur chemin relatif sous `cible`, contrôlés avant écriture.

    Lève `ArchiveInvalide` pour un membre absolu, avec `..`, un lien, un doublon, ou (avec
    `retirer_racine`) une archive sans dossier racine unique.
    """
    membres = [(info, _relatif_membre(info)) for info in archive.infolist()]
    if retirer_racine:
        racines = {relatif.parts[0] for _, relatif in membres}
        if len(racines) != 1:
            raise ArchiveInvalide("archive des sources sans dossier racine unique")
        membres = [
            (info, PurePosixPath(*relatif.parts[1:]))
            for info, relatif in membres
            if len(relatif.parts) > 1
        ]
    base = cible.resolve()
    fichiers = []
    vus: set[str] = set()
    for info, relatif in membres:
        if not (base / relatif).resolve().is_relative_to(base):
            raise ArchiveInvalide(f"membre {info.filename!r} : chemin hors de la cible refusé")
        if info.is_dir():
            continue
        cle = relatif.as_posix().lower()
        if cle in vus:
            raise ArchiveInvalide(f"membre {info.filename!r} : doublon dans l'archive")
        vus.add(cle)
        fichiers.append((info, relatif))
    return fichiers


def _crc32(chemin: Path, taille_bloc: int) -> int:
    valeur = 0
    with chemin.open("rb") as flux:
        while bloc := flux.read(taille_bloc):
            valeur = zlib.crc32(bloc, valeur)
    return valeur


def _identique(chemin: Path, info: zipfile.ZipInfo, taille_bloc: int) -> bool:
    return (
        chemin.is_file()
        and chemin.stat().st_size == info.file_size
        and _crc32(chemin, taille_bloc) == info.CRC
    )


def chemin_marqueur(archive: Path) -> Path:
    """Marqueur d'extraction : `<archive>.extrait.json`."""
    return archive.with_name(archive.name + SUFFIXE_MARQUEUR)


def extraire(
    archive: str | Path,
    cible: str | Path,
    config: ConfigTelechargement,
    *,
    sha256: str,
    retirer_racine: bool = False,
) -> dict[str, Any]:
    """Extrait `archive` (déjà vérifiée par `sha256`) sous `cible`, sans rien écraser.

    Vérifie l'espace libre d'abord (au moins `taille × facteur_extraction`, plus
    `marge_espace`). Renvoie le résumé inscrit au marqueur (`statut` : `extrait` ou
    `deja-extrait`). Lève `ArchiveInvalide` ou `EspaceInsuffisant`.
    """
    archive, cible = Path(archive), Path(cible)
    marqueur = chemin_marqueur(archive)
    if marqueur.exists():
        return {"archive": archive.name, "cible": str(cible), "statut": "deja-extrait"}
    try:
        with zipfile.ZipFile(archive) as zf:
            membres = membres_valides(zf, cible, retirer_racine=retirer_racine)
            octets = max(
                sum(info.file_size for info, _ in membres),
                int(archive.stat().st_size * config.facteur_extraction),
            )
            verifier_espace(cible, octets, seuil_octets=config.marge_espace)
            ecrits = deja = 0
            for info, relatif in membres:
                chemin = cible.joinpath(*relatif.parts)
                if chemin.exists():
                    if not _identique(chemin, info, config.taille_bloc):
                        raise ArchiveInvalide(
                            f"{chemin} existe avec un autre contenu que {info.filename} "
                            f"({archive.name}) : rien n'est écrasé"
                        )
                    deja += 1
                    continue
                chemin.parent.mkdir(parents=True, exist_ok=True)
                temporaire = chemin.with_name(f"{chemin.name}.extraction-{horodatage()}")
                with zf.open(info) as entree, temporaire.open("xb") as sortie:
                    shutil.copyfileobj(entree, sortie, config.taille_bloc)
                renommer_sans_ecraser(temporaire, chemin)
                ecrits += 1
    except zipfile.BadZipFile as exc:
        raise ArchiveInvalide(f"{archive.name} : archive zip illisible ({exc})") from None
    resume = {
        "archive": archive.name,
        "sha256": sha256,
        "cible": str(cible),
        "fichiers": len(membres),
        "ecrits": ecrits,
        "deja_presents": deja,
        "extrait_le": datetime.now().astimezone().isoformat(),
    }
    with marqueur.open("xb") as flux:
        flux.write(json_canonique(resume) + b"\n")
    return {**resume, "statut": "extrait"}


def verifier_binaires(base: Path, binaires: Mapping[str, str], taille_bloc: int) -> int:
    """Contrôle les SHA-256 de `binaires` (chemins relatifs à `base`) ; renvoie leur nombre."""
    for relatif, attendu in binaires.items():
        chemin = base.joinpath(
            *chemin_config(relatif.replace("\\", "/"), "llamacpp : binaires").split("/")
        )
        if not chemin.is_file():
            raise ShaInvalide(f"binaire attendu absent après extraction : {relatif}")
        present = sha256_fichier(chemin, taille_bloc)
        if present != attendu:
            raise ShaInvalide(f"binaire {relatif} : SHA-256 {present} au lieu de {attendu}")
    return len(binaires)


# --- Pilote ----------------------------------------------------------------------------


def executer(
    telechargeur: Telechargeur,
    config: ConfigLlamacpp,
    racine: str | Path,
    *,
    consigner: Callable[[dict[str, Any]], None] = lambda _ligne: None,
    consigner_extraction: Callable[[dict[str, Any]], None] = lambda _ligne: None,
) -> list[ResultatFichier]:
    """Télécharge, vérifie et extrait le tag de `config` sous `<racine>/vendor/llama.cpp/`.

    L'API GitHub n'est interrogée que si une archive des binaires manque. `consigner`
    reçoit une ligne par archive, `consigner_extraction` une ligne par extraction.
    """
    base = dossier_tag(racine, config)
    archives = base / "archives"
    if all((archives / asset.nom).exists() for asset in config.assets.values()):
        prevues = [
            ArchivePrevue(
                cle,
                asset.nom,
                f"https://github.com/{config.depot}/releases/download/{config.tag}/{asset.nom}",
                asset.sha256,
                None,
            )
            for cle, asset in config.assets.items()
        ]
    else:
        prevues = lire_release(telechargeur, config)
    prevues.append(archive_sources(config))

    # Archives, plus l'estimation de leur extraction (taille × facteur) rattachée au dossier
    # cible : le contrôle avant téléchargement couvre toute l'écriture de la commande.
    facteur = telechargeur.config.facteur_extraction
    dossiers = {cle: dossier for cle, dossier, _ in EXTRACTIONS}
    telechargeur.verifier_espace_total(
        [(archives / p.nom, p.taille) for p in prevues]
        + [
            (base / dossiers[p.cle], None if p.taille is None else int(p.taille * facteur))
            for p in prevues
        ]
    )
    resultats: dict[str, ResultatFichier] = {}
    for prevue in prevues:
        resultat = telechargeur.telecharger(
            prevue.url, archives / prevue.nom, prevue.sha256, prevue.taille
        )
        resultats[prevue.cle] = resultat
        consigner(
            {
                "depot": config.depot,
                "url": prevue.url,
                "fichier": prevue.nom,
                "revision": config.tag,
                "octets": resultat.octets,
                "taille": resultat.taille,
                "sha256": resultat.sha256,
                "statut": resultat.statut,
                "destination": str(resultat.destination),
                "source": None if resultat.source is None else str(resultat.source),
            }
        )

    for cle, dossier, retirer_racine in EXTRACTIONS:
        resultat = resultats[cle]
        resume = extraire(
            resultat.destination,
            base / dossier,
            telechargeur.config,
            sha256=resultat.sha256,
            retirer_racine=retirer_racine,
        )
        consigner_extraction(resume)
    nombre = verifier_binaires(base, config.binaires, telechargeur.config.taille_bloc)
    if nombre:
        consigner_extraction({"binaires_verifies": nombre, "cible": str(base)})
    return list(resultats.values())


__all__ = [
    "ArchivePrevue",
    "archive_sources",
    "dossier_tag",
    "executer",
    "extraire",
    "lire_release",
    "membres_valides",
    "verifier_binaires",
]
