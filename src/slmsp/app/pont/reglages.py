"""Pont, domaine « Réglages et À propos » (story 12.10, FR-6, FR-11, FR-23).

Chaque méthode rend `{"ok": true, ...}` ou lève ; le pont convertit l'exception en
`{"ok": false, "erreur": {"code", "message"}}`. Contrat :

- `lire()` -> `{"ok": true, "reglages": {"taille_texte": 100|112|125|137|150,
  "hors_ligne_force": bool}}`.
- `ecrire(cle, valeur)` -> `{"ok": true}`. Seule `taille_texte` est modifiable ici (un des cinq
  crans) ; le Mode se règle par `mode.forcer_hors_ligne`. Autre clé ou valeur : `reglage-invalide`.
- `langues_traduction()` -> `{"ok": true, "langues": ["en", "es", ...]}` : codes de
  `config/application.toml` (`langues_traduction`, Q9), proposés par la vue Traduction.
- `modeles()` -> `{"ok": true, "modeles": [{"slug", "nom"}], "actif": slug, "choisi": slug}` (story
  12.15) : modèles embarqués, modèle en cours d'exécution, modèle qui sera actif au prochain
  démarrage. `ecrire("modele", slug)` l'enregistre (slug non embarqué : `reglage-invalide`) ; il
  n'y a pas de redémarrage à chaud.
- `effacer_historique()` -> `{"ok": true}` : vide conversations et Retours (réglages et journal
  conservés). La confirmation de 5 s (UX-DR18) est tenue par l'interface.
- `a_propos()` -> `{"ok": true, "application": {"version": str|None, "empreinte": str|None},
  "modele": {"slug", "depot", "fichier", "sha256_attendu"} | None, "index": {"version",
  "date_snapshot", "nb_chunks"} | None, "liste_blanche": [hôte], "licences": {"statut", "note",
  "composants": [{"nom", "licence"}]}, "hors_passerelle": [{"composant", "detail"}],
  "mentions": {"avertissement_juridique", "mise_a_jour", "donnees"}}`. Une information absente
  vaut `null` (l'interface l'affiche proprement). Fichiers relus à chaque appel : une Liste blanche
  modifiée sans recompilation apparaît à la relance.

Fournisseurs externes (story 17.4, amendement 14), appliqués au démarrage suivant :

- `fournisseurs_externes()` -> `{"ok": true, "fournisseurs": [{id, preset, url_base, modele,
  actif, parametres_supplementaires, cle_enregistree}], "presets": [{nom, libelle, url_base,
  modeles, parametres_libres}], "max": 3, "en_cours": {tete, preset, hote, modele, secours} |
  null}`. Les clés ne sont jamais renvoyées.
- `ecrire("fournisseurs_externes", [entrées])` : 3 au plus, dans l'ordre d'essai, URL HTTPS
  seulement, sans identifiants ; sinon `reglage-invalide` (message court). Les clés des entrées
  retirées, et celles d'une entrée dont l'hôte ou le preset a changé, sont effacées. Rend
  `{"ok": true, "fournisseurs": [...]}` (valeurs normalisées).
- `enregistrer_cle(id, cle, valeurs?)` (chiffrée par DPAPI, un fichier par entrée, liée à
  l'hôte et au preset de `valeurs`, à défaut de l'entrée enregistrée `id`) et
  `effacer_cle(id)` -> `{"ok": true, "cle_enregistree": bool}`. `cle_enregistree` est vrai
  seulement pour une clé liée à l'hôte et au preset de l'entrée.
- `tester_modele_externe(valeurs)` -> `{"ok": true, "reussi": bool, "latence_ms" | "motif",
  "hote"}` : une requête de 1 token avec les valeurs d'une entrée du formulaire (`cle` du champ,
  sinon la clé enregistrée pour son `id`), sans relancer l'application. Motif : code court,
  jamais un corps de réponse ; `cle-autre-hote` (sans requête) si la clé enregistrée est liée
  à un autre hôte ou preset que celui du formulaire.

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
    from slmsp.app.cle_externe import CoffreCles
    from slmsp.app.stockage import Stockage

TesterExterne = Callable[[dict[str, Any], Any], dict[str, Any]]
"""`(entrée validée, clé SecretStr | None)` -> résultat de `modele_externe.tester_connexion`."""

LOGGER: Final = logging.getLogger("slmsp.app.pont.reglages")
CRANS_TAILLE: Final = (100, 112, 125, 137, 150)
RESSOURCES: Final = Path(__file__).resolve().parents[1] / "ressources"
FICHIER_LICENCES: Final = "licences-tierces.json"
FICHIER_EMPREINTE: Final = "empreinte-application.txt"  # produit au build (12.12), optionnel
METHODES: Final = frozenset(
    {
        "lire",
        "ecrire",
        "effacer_historique",
        "a_propos",
        "langues_traduction",
        "modeles",
        "fournisseurs_externes",
        "enregistrer_cle",
        "effacer_cle",
        "tester_modele_externe",
    }
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


def _liaison(entree: dict[str, Any]) -> dict[str, str]:
    from slmsp.app.modele_externe import liaison

    return liaison(entree)


class PontReglages:
    """Réglages persistants (via `Stockage`) et rubrique « À propos »."""

    def __init__(
        self,
        stockage: Stockage | None = None,
        racine: Path | None = None,
        ressources: Path | None = None,
        version: Callable[[], str | None] | None = None,
        apres_effacement: Callable[[], None] | None = None,
        modele_actif: str | None = None,
        *,
        coffre: CoffreCles | None = None,
        tester: TesterExterne | None = None,
        modele_externe: dict[str, Any] | None = None,
    ) -> None:
        self._modele_actif = modele_actif
        self._coffre = coffre
        self._tester = tester
        # {tete, preset, hote, modele, secours} si un fournisseur est actif depuis le démarrage
        self._externe_en_cours = modele_externe
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
        if cle == "modele":
            return self._choisir_modele(valeur)
        if cle == "fournisseurs_externes":
            return self._ecrire_externe(valeur)
        if cle != "taille_texte" or not _est_cran(valeur):
            return {
                "ok": False,
                "erreur": {"code": CODE_INVALIDE, "message": "Ce réglage n'est pas modifiable."},
            }
        stock.ecrire_reglage(cle, valeur)
        return {"ok": True}

    def _choisir_modele(self, valeur: Any) -> dict[str, Any]:
        from slmsp.core.schemas.config_application import charger_config_application

        if (
            not isinstance(valeur, str)
            or valeur not in charger_config_application().modeles_embarques
        ):
            return {
                "ok": False,
                "erreur": {"code": CODE_INVALIDE, "message": "Ce modèle n'est pas embarqué."},
            }
        self._stock().ecrire_reglage("modele", valeur)
        return {"ok": True}

    # -- Fournisseurs externes (story 17.4) ----------------------------------------------

    @staticmethod
    def _refus(message: str) -> dict[str, Any]:
        return {"ok": False, "erreur": {"code": CODE_INVALIDE, "message": message}}

    def _ecrire_externe(self, valeur: Any) -> dict[str, Any]:
        from slmsp.app.modele_externe import CLE_REGLAGE, valider_reglage

        try:
            entrees = valider_reglage(valeur)
        except ValueError as exc:
            return self._refus(f"Fournisseurs externes : {exc}.")
        if any(e["preset"] == "generique" and e["actif"] and not e["tarif"] for e in entrees):
            # Story 17.6, amendement 8 : sans tarif, le plafond ne peut pas s'appliquer.
            return self._refus(
                "Fournisseurs externes : tarif obligatoire pour un hôte compatible OpenAI."
            )
        self._stock().ecrire_reglage(CLE_REGLAGE, entrees)
        if self._coffre is not None:
            self._coffre.ne_garder_que(e["id"] for e in entrees)
            for e in entrees:
                self._coffre.effacer_si_autre_hote(e["id"], **_liaison(e))
        return {"ok": True, "fournisseurs": self._avec_cles(entrees)}

    def _cle_enregistree(self, entree: dict[str, Any]) -> bool:
        return (
            self._coffre is not None
            and self._coffre.etat(entree["id"], **_liaison(entree)) == "liee"
        )

    def _avec_cles(self, entrees: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [{**e, "cle_enregistree": self._cle_enregistree(e)} for e in entrees]

    def _entree_pour_cle(self, identifiant: Any, valeurs: Any) -> dict[str, Any] | None:
        """Entrée à laquelle lier la clé : `valeurs` du formulaire (même `id`), à défaut
        l'entrée enregistrée ; `None` si aucune."""
        from slmsp.app.modele_externe import lire_reglage, valider_entree

        if isinstance(valeurs, dict):
            valeurs = {k: v for k, v in valeurs.items() if k != "cle"}
            try:
                entree = valider_entree({**valeurs, "actif": True})
            except ValueError:
                return None
            return entree if entree["id"] == identifiant else None
        return next((e for e in lire_reglage(self._stock()) if e["id"] == identifiant), None)

    def fournisseurs_externes(self) -> dict[str, Any]:
        from slmsp.app.modele_externe import MAX_FOURNISSEURS, lire_reglage, presets_vue

        en_cours = self._externe_en_cours
        return {
            "ok": True,
            "fournisseurs": self._avec_cles(lire_reglage(self._stock())),
            "presets": presets_vue(),
            "max": MAX_FOURNISSEURS,
            "en_cours": dict(en_cours) if en_cours else None,
        }

    def enregistrer_cle(self, identifiant: Any, cle: Any, valeurs: Any = None) -> dict[str, Any]:
        if self._coffre is None:
            raise NonImplementee("reglages : coffre de clé indisponible")
        entree = self._entree_pour_cle(identifiant, valeurs)
        if entree is None:
            return self._refus("Fournisseur à compléter avant d'enregistrer la clé.")
        try:
            self._coffre.enregistrer(identifiant, cle, **_liaison(entree))
        except ValueError:
            return self._refus("Clé invalide.")
        except OSError as exc:
            LOGGER.error("clé du fournisseur non enregistrée : %s", type(exc).__name__)
            return self._refus("La clé n'a pas pu être enregistrée.")
        return {"ok": True, "cle_enregistree": self._cle_enregistree(entree)}

    def effacer_cle(self, identifiant: Any) -> dict[str, Any]:
        if self._coffre is not None:
            self._coffre.effacer(identifiant)
        return {
            "ok": True,
            "cle_enregistree": self._coffre is not None and self._coffre.presente(identifiant),
        }

    def tester_modele_externe(self, valeurs: Any) -> dict[str, Any]:
        from pydantic import SecretStr

        from slmsp.app.modele_externe import valider_entree

        if self._tester is None:
            raise NonImplementee("reglages : test du modèle externe indisponible")
        if not isinstance(valeurs, dict):
            return self._refus("Fournisseur externe : objet attendu.")
        valeurs = dict(valeurs)
        saisie = valeurs.pop("cle", None)
        try:
            entree = valider_entree({**valeurs, "actif": True})
        except ValueError as exc:
            return self._refus(f"Fournisseur externe : {exc}.")
        if entree.get("acces_gratuit"):
            cle: SecretStr | None = None  # accès gratuit : aucune clé lue ni envoyée
        elif isinstance(saisie, str) and saisie.strip():
            cle = SecretStr(saisie.strip())
        elif self._coffre is None:
            cle = None
        else:
            # Une clé enregistrée ne part jamais vers un autre hôte que le sien.
            lie = _liaison(entree)
            if self._coffre.etat(entree["id"], **lie) == "autre-hote":
                return {"ok": True, "reussi": False, "motif": "cle-autre-hote", "hote": lie["hote"]}
            cle = self._coffre.lire(entree["id"], **lie)
        return {"ok": True, **self._tester(entree, cle)}

    def modeles(self) -> dict[str, Any]:
        from slmsp.app.modele_actif import resoudre_modele_actif
        from slmsp.core.schemas.config_application import charger_config_application

        config = charger_config_application()
        choisi = resoudre_modele_actif(config, self._stock().lire_reglage("modele"))
        return {
            "ok": True,
            "modeles": [{"slug": s, "nom": s} for s in config.modeles_embarques],
            "actif": self._modele_actif or choisi,
            "choisi": choisi,
        }

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
            "modele_externe": dict(self._externe_en_cours) if self._externe_en_cours else None,
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

            config = charger_config_application()
            slug = self._modele_actif or config.modele
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
