"""Pilote `slmsp fetch sources` : parquet du corpus MediaTech (AD-28, D3).

Chaque fichier de `config/sources.toml` est lu par l'URL `resolve/<revision>` du dépôt
de jeu de données (jamais par le datasets-server) et écrit sous
`<racine>/data/raw/mediatech/<jeu>/<revision>/<nom du fichier>`. Taille et SHA-256 viennent
de la configuration : aucune requête de métadonnées n'est nécessaire.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.fetch.config import ConfigSources, FichierSource, JeuSource
from slmsp.fetch.hf import ResultatFichier, Telechargeur, url_hf


def dossier_jeu(racine: str | Path, jeu: JeuSource) -> Path:
    """`<racine>/data/raw/mediatech/<jeu>/<revision>`."""
    return Path(racine) / "data" / "raw" / "mediatech" / jeu.nom / jeu.revision


def choisir_jeux(config: ConfigSources, noms: Sequence[str] = ()) -> list[JeuSource]:
    """Jeux nommés dans `noms` (tous si vide) ; lève `ConfigurationInvalide` pour un inconnu."""
    if not noms:
        return list(config.jeux)
    connus = {jeu.nom: jeu for jeu in config.jeux}
    inconnus = [nom for nom in noms if nom not in connus]
    if inconnus:
        raise ConfigurationInvalide(
            f"jeu inconnu : {', '.join(inconnus)} (connus : {', '.join(connus)})"
        )
    return [connus[nom] for nom in dict.fromkeys(noms)]


def planifier(
    config: ConfigSources, racine: str | Path, noms: Sequence[str] = ()
) -> list[tuple[JeuSource, FichierSource, Path, str]]:
    """`(jeu, fichier, destination, url)` de chaque fichier à obtenir.

    Lève `ConfigurationInvalide` si deux fichiers d'un même jeu ont le même nom.
    """
    plan = []
    for jeu in choisir_jeux(config, noms):
        dossier = dossier_jeu(racine, jeu)
        vus: set[str] = set()
        for fichier in jeu.fichiers:
            nom = PurePosixPath(fichier.chemin).name
            if nom.lower() in vus:
                raise ConfigurationInvalide(
                    f"jeu {jeu.nom} : deux fichiers portent le nom {nom} ; "
                    "ils s'écraseraient sous le même dossier"
                )
            vus.add(nom.lower())
            url = url_hf(jeu.depot, fichier.chemin, jeu.revision, type_depot="dataset")
            plan.append((jeu, fichier, dossier / nom, url))
    return plan


def executer(
    telechargeur: Telechargeur,
    config: ConfigSources,
    racine: str | Path,
    *,
    jeux: Sequence[str] = (),
    consigner: Callable[[dict[str, Any]], None] = lambda _ligne: None,
) -> list[ResultatFichier]:
    """Télécharge les fichiers des jeux choisis ; `consigner` reçoit une ligne par fichier."""
    plan = planifier(config, racine, jeux)
    telechargeur.verifier_espace_total((destination, f.taille) for _, f, destination, _ in plan)
    resultats = []
    for jeu, fichier, destination, url in plan:
        resultat = telechargeur.telecharger(url, destination, fichier.sha256, fichier.taille)
        resultats.append(resultat)
        consigner(
            {
                "jeu": jeu.nom,
                "depot": jeu.depot,
                "url": url,
                "fichier": fichier.chemin,
                "revision": jeu.revision,
                "licence": jeu.licence,
                "octets": resultat.octets,
                "taille": resultat.taille,
                "sha256": resultat.sha256,
                "statut": resultat.statut,
                "destination": str(resultat.destination),
                "source": None if resultat.source is None else str(resultat.source),
            }
        )
    return resultats


__all__ = ["choisir_jeux", "dossier_jeu", "executer", "planifier"]
