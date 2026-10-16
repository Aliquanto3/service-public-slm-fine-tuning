"""Pont, domaine « Réglages et À propos » (story 12.10, FR-6, FR-11, FR-23).

Chaque méthode rend `{"ok": true, ...}` ou lève ; le pont convertit l'exception en
`{"ok": false, "erreur": {"code", "message"}}`. Contrat :

- `lire()` -> `{"ok": true, "reglages": {"taille_texte": 100|112|125|137|150,
  "hors_ligne_force": bool}}`.
- `ecrire(cle, valeur)` -> `{"ok": true}`. Seule `taille_texte` est modifiable ici (un des cinq
  crans) ; le Mode se règle par `mode.forcer_hors_ligne`. Autre clé ou valeur : `reglage-invalide`.
- `langues_traduction()` -> `{"ok": true, "langues": ["en", "es", ...]}` : codes de
  `config/application.toml` (`langues_traduction`, Q9), proposés par la vue Traduction.
- `effacer_historique()` -> `{"ok": true}` : vide conversations et Retours (réglages et journal
  conservés). La confirmation de 5 s (UX-DR18) est tenue par l'interface.
- `a_propos()` -> `{"ok": true, "application": {"version": str|None, "empreinte": str|None},
  "modele": {"slug", "depot", "fichier", "sha256_attendu"} | None, "index": {"version",
  "date_snapshot", "nb_chunks"} | None, "liste_blanche": [hôte], "licences": {"statut", "note",
  "composants": [{"nom", "licence"}]}, "hors_passerelle": [{"composant", "detail"}],
  "mentions": {"avertissement_juridique", "mise_a_jour", "donnees"}}`. Une information absente
  vaut `null` (l'interface l'affiche proprement). Fichiers relus à chaque appel : une Liste blanche
  modifiée sans recompilation apparaît à la relance.

Les libellés des mentions sont des propositions, à valider par Anaël.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from importlib import metadata
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from slmsp.app.pont.erreurs import NonImplementee
from slmsp.core.erreurs import SlmspError

if TYPE_CHECKING:
    from slmsp.app.stockage import Stockage

LOGGER: Final = logging.getLogger("slmsp.app.pont.reglages")
CRANS_TAILLE: Final = (100, 112, 125, 137, 150)
RESSOURCES: Final = Path(__file__).resolve().parents[1] / "ressources"
FICHIER_LICENCES: Final = "licences-tierces.json"
FICHIER_EMPREINTE: Final = "empreinte-application.txt"  # produit au build (12.12), optionnel
METHODES: Final = frozenset(
    {"lire", "ecrire", "effacer_historique", "a_propos", "langues_traduction"}
)
CODE_INVALIDE: Final = "reglage-invalide"

# Libellés proposés (à valider par Anaël ; Q1, Q6, UX-DR22).
AVERTISSEMENT_JURIDIQUE: Final = "Ne vaut pas avis juridique."
MENTION_MISE_A_JOUR: Final = (
    "Cette application ne se met jamais à jour toute seule : une nouvelle version s'installe "
    "à la main."
)
MENTION_DONNEES: Final = (
    "Vos conversations restent sur cet ordinateur. Rien n'est envoyé sans votre action."
)
HORS_PASSERELLE: Final = (
    {
        "composant": "Microsoft Edge WebView2",
        "detail": (
            "Composant de Windows qui affiche l'interface. Il dépend de Microsoft et n'est pas "
            "contrôlé par cette application : il peut contacter des serveurs Microsoft pour son "
            "propre fonctionnement, hors de la liste ci-dessus."
        ),
    },
)


def _taille(valeur: Any) -> int:
    """Cran enregistré ; « normale » (valeur par défaut du stockage) et l'inconnu valent 100."""
    ok = _est_cran(valeur)
    return int(valeur) if ok else CRANS_TAILLE[0]


def _lire_json(chemin: Path) -> Any:
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _est_cran(valeur: Any) -> bool:
    """Entier strict : ni booléen ni flottant (`112.0`)."""
    return type(valeur) is int and valeur in CRANS_TAILLE


def _version_application() -> str | None:
    try:
        return metadata.version("slmsp")
    except metadata.PackageNotFoundError:
        return None


class PontReglages:
    """Réglages persistants (via `Stockage`) et rubrique « À propos »."""

    def __init__(
        self,
        stockage: Stockage | None = None,
        racine: Path | None = None,
        ressources: Path | None = None,
        version: Callable[[], str | None] | None = None,
        apres_effacement: Callable[[], None] | None = None,
    ) -> None:
        self._apres_effacement = apres_effacement
        self._stockage = stockage
        self._racine = racine
        self._ressources = ressources or RESSOURCES
        self._version = version or _version_application

    def _stock(self) -> Stockage:
        if self._stockage is None:
            raise NonImplementee("reglages : stockage indisponible")
        return self._stockage

    def lire(self) -> dict[str, Any]:
        stock = self._stock()
        return {
            "ok": True,
            "reglages": {
                "taille_texte": _taille(stock.lire_reglage("taille_texte")),
                "hors_ligne_force": bool(stock.lire_reglage("hors_ligne_force")),
            },
        }

    def ecrire(self, cle: str, valeur: Any) -> dict[str, Any]:
        stock = self._stock()
        if cle != "taille_texte" or not _est_cran(valeur):
            return {
                "ok": False,
                "erreur": {"code": CODE_INVALIDE, "message": "Ce réglage n'est pas modifiable."},
            }
        stock.ecrire_reglage(cle, valeur)
        return {"ok": True}

    def langues_traduction(self) -> dict[str, Any]:
        from slmsp.core.schemas.config_application import charger_config_application

        return {"ok": True, "langues": list(charger_config_application().langues_traduction)}

    def effacer_historique(self) -> dict[str, Any]:
        self._stock().effacer_historique()
        if self._apres_effacement is not None:
            self._apres_effacement()  # `regenerer` ne doit pas rejouer l'envoi effacé
        return {"ok": True}

    # -- À propos ------------------------------------------------------------------------

    def a_propos(self) -> dict[str, Any]:
        return {
            "ok": True,
            "application": {"version": self._version(), "empreinte": self._empreinte()},
            "modele": self._modele(),
            "index": self._index(),
            "liste_blanche": self._liste_blanche(),
            "licences": self._licences(),
            "hors_passerelle": [dict(e) for e in HORS_PASSERELLE],
            "mentions": {
                "avertissement_juridique": AVERTISSEMENT_JURIDIQUE,
                "mise_a_jour": MENTION_MISE_A_JOUR,
                "donnees": MENTION_DONNEES,
            },
        }

    def _empreinte(self) -> str | None:
        try:
            texte = (self._ressources / FICHIER_EMPREINTE).read_text(encoding="utf-8").strip()
        except OSError:
            return None
        return texte or None

    def _modele(self) -> dict[str, Any] | None:
        try:
            from slmsp.core.schemas.config_application import charger_config_application
            from slmsp.inference.serveur import charger_config_modele

            slug = charger_config_application().modele
            gguf = charger_config_modele(slug).gguf
        except SlmspError as exc:
            LOGGER.error("à propos, modèle : %s", type(exc).__name__)
            return None
        return {
            "slug": slug,
            "depot": gguf.depot if gguf else None,
            "fichier": gguf.fichier if gguf else None,
            "sha256_attendu": gguf.sha256 if gguf else None,
        }

    def _index(self) -> dict[str, Any] | None:
        from slmsp.index.config import dossier_index, version_valide
        from slmsp.index.lecture import lire_manifeste

        base = dossier_index(self._racine)
        try:
            versions = sorted(
                (d.name for d in base.iterdir() if d.is_dir() and version_valide(d.name)),
                reverse=True,
            )
        except OSError:
            return None
        for version in versions:
            try:
                manifeste = lire_manifeste(base / version)
            except SlmspError:
                continue
            return {
                "version": manifeste.version,
                "date_snapshot": manifeste.date_snapshot.isoformat(),
                "nb_chunks": manifeste.nb_chunks,
            }
        return None

    def _liste_blanche(self) -> list[str]:
        from slmsp.net.config import charger_liste_blanche, chemin_config

        chemin = (
            chemin_config("liste-blanche.toml")
            if self._racine is None
            else self._racine / "config" / "liste-blanche.toml"
        )
        try:
            return list(charger_liste_blanche(chemin).hotes)
        except SlmspError as exc:
            LOGGER.error("à propos, Liste blanche : %s", type(exc).__name__)
            return []

    def _licences(self) -> dict[str, Any]:
        brut = _lire_json(self._ressources / FICHIER_LICENCES)
        composants = brut.get("composants") if isinstance(brut, dict) else None
        if not isinstance(brut, dict) or not isinstance(composants, list):
            return {"statut": None, "note": None, "composants": []}
        propres = [
            {"nom": str(c.get("nom", "")), "licence": str(c.get("licence", ""))}
            for c in composants
            if isinstance(c, dict) and c.get("nom")
        ]
        return {"statut": brut.get("statut"), "note": brut.get("note"), "composants": propres}

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        if nom not in METHODES:
            raise NonImplementee(f"reglages.{nom} : méthode inconnue")
        return getattr(self, nom)(*args)


__all__ = ["CRANS_TAILLE", "PontReglages"]
