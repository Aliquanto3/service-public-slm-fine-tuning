"""Pilote `slmsp fetch benchmarks` : jeux des benchmarks à leur révision épinglée (AD-28).

Les jeux sont déclarés par `config/benchmarks/*.toml` (`[[jeux]]`). Chaque fichier est lu
par l'URL `resolve/<revision>` et écrit sous
`<racine>/data/raw/benchmarks/<jeu>/<revision>/<nom du fichier>`. Un jeu sans révision ou
sans fichiers épinglés est signalé (`non-epingle`) et sauté ; un jeu à accès conditionnel
dont le téléchargement est refusé est signalé (`acces-conditionnel`), consigné et sauté.
"""

from __future__ import annotations

import tomllib
from collections.abc import Callable, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from pydantic import ValidationError

from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas.bench import JeuBench
from slmsp.fetch.hf import TelechargementEchoue, Telechargeur, url_hf


def lire_jeux(dossier: str | Path, benchmarks: Sequence[str] = ()) -> list[JeuBench]:
    """Jeux des benchmarks de `<dossier>/*.toml` (ceux de `benchmarks` si non vide).

    Un jeu partagé par plusieurs benchmarks n'est rendu qu'une fois. Lève
    `ConfigurationInvalide` pour un benchmark inconnu, un fichier illisible ou deux
    déclarations différentes d'un même jeu.
    """
    base = Path(dossier)
    if not base.is_dir():
        raise ConfigurationInvalide(f"dossier des benchmarks introuvable : {base}")
    fichiers = {chemin.stem: chemin for chemin in sorted(base.glob("*.toml"))}
    inconnus = [nom for nom in benchmarks if nom not in fichiers]
    if inconnus:
        raise ConfigurationInvalide(
            f"benchmark inconnu : {', '.join(inconnus)} (connus : {', '.join(fichiers)})"
        )
    jeux: dict[str, JeuBench] = {}
    for nom in benchmarks or fichiers:
        chemin = fichiers[nom]
        try:
            donnees = tomllib.loads(chemin.read_text(encoding="utf-8"))
            declares = [JeuBench.model_validate(jeu) for jeu in donnees.get("jeux", [])]
        except (OSError, tomllib.TOMLDecodeError, ValidationError) as exc:
            raise ConfigurationInvalide(f"{chemin} : {type(exc).__name__}") from None
        for jeu in declares:
            if jeux.setdefault(jeu.nom, jeu) != jeu:
                raise ConfigurationInvalide(f"{chemin} : le jeu {jeu.nom} est déclaré différemment")
    return list(jeux.values())


def dossier_jeu(racine: str | Path, jeu: JeuBench) -> Path:
    """`<racine>/data/raw/benchmarks/<jeu>/<revision>`."""
    return Path(racine) / "data" / "raw" / "benchmarks" / jeu.nom / str(jeu.revision)


def executer(
    telechargeur: Telechargeur,
    jeux: Sequence[JeuBench],
    racine: str | Path,
    *,
    consigner: Callable[[dict[str, Any]], None] = lambda _ligne: None,
) -> None:
    """Télécharge les jeux ; `consigner` reçoit une ligne par fichier, ou par jeu sauté."""

    def saute(jeu: JeuBench, statut: str, motif: str) -> None:
        consigner(
            {
                "jeu": jeu.nom,
                "depot": jeu.depot,
                "revision": jeu.revision,
                "acces": jeu.acces,
                "statut": statut,
                "motif": motif,
                "octets": 0,
                "destination": "",
            }
        )

    a_obtenir = []
    for jeu in jeux:
        if jeu.revision is None or not jeu.fichiers:
            saute(jeu, "non-epingle", "révision ou fichiers non épinglés dans la configuration")
        else:
            a_obtenir.append(jeu)
    telechargeur.verifier_espace_total(
        (dossier_jeu(racine, jeu) / PurePosixPath(f.chemin).name, f.taille)
        for jeu in a_obtenir
        for f in jeu.fichiers
    )
    for jeu in a_obtenir:
        dossier = dossier_jeu(racine, jeu)
        try:
            for fichier in jeu.fichiers:
                url = url_hf(jeu.depot, fichier.chemin, str(jeu.revision), type_depot="dataset")
                resultat = telechargeur.telecharger(
                    url,
                    dossier / PurePosixPath(fichier.chemin).name,
                    fichier.sha256,
                    fichier.taille,
                )
                consigner(
                    {
                        "jeu": jeu.nom,
                        "depot": jeu.depot,
                        "url": url,
                        "fichier": fichier.chemin,
                        "revision": jeu.revision,
                        "licence": jeu.licence,
                        "acces": jeu.acces,
                        "octets": resultat.octets,
                        "taille": resultat.taille,
                        "sha256": resultat.sha256,
                        "statut": resultat.statut,
                        "destination": str(resultat.destination),
                    }
                )
        except TelechargementEchoue as exc:
            if jeu.acces != "conditionnel":
                raise
            saute(jeu, "acces-conditionnel", str(exc).splitlines()[0])


__all__ = ["dossier_jeu", "executer", "lire_jeux"]
