"""Pont `js_api` (story 12.5, AD-23) : seule porte entre l'interface et `AssistantService`.

pywebview expose les méthodes publiques de `Pont` à l'interface (`window.pywebview.api`).
Contrat JSON, valable pour toutes les méthodes :

- réponse : `{"ok": true, ...}` ou `{"ok": false, "erreur": {"code": str, "message": str}}` ;
  le message n'inclut jamais le texte saisi (masqué) ;
- évènements : poussés par lots (liste) via `fenetre.evaluate_js("window.slmspRecevoir(<lot>)")`,
  au format `core.evenements.vers_dict`, plus `{"type": "pret"}` (`signaler_pret`) ;
- `appeler(nom, *args)` : appel générique ; `nom` est `envoyer`, `arreter`, `regenerer`,
  `nouvelle_conversation`, `ouvrir_lien`, ou `<domaine>.<methode>` (domaines : `mode`,
  `reglages`, `historique`, `retours`, `verification`).

L'interface pywebview n'est vue qu'à travers le port `Fenetre`.
"""

from __future__ import annotations

import inspect
import json
import logging
from collections.abc import Mapping, Sequence
from typing import Any, Final, Protocol

from slmsp.app.pont.conversation import Conversation, reponse_erreur
from slmsp.app.pont.erreurs import NonImplementee
from slmsp.app.pont.historique import PontHistorique
from slmsp.app.pont.mode import PontMode
from slmsp.app.pont.reglages import PontReglages
from slmsp.app.pont.retours import PontRetours
from slmsp.app.pont.verification import PontVerification
from slmsp.core.erreurs import SlmspError
from slmsp.harness.service import AssistantService
from slmsp.net.config import ConfigListeBlanche, charger_liste_blanche
from slmsp.net.profils import analyser_url

LOGGER: Final = logging.getLogger("slmsp.app.pont")
CODE_NON_IMPLEMENTEE: Final = "non-implementee"
CODE_INCONNUE: Final = "methode-inconnue"
CODE_LIEN_REFUSE: Final = "lien-refuse"
METHODES_DIRECTES: Final = frozenset(
    {"envoyer", "arreter", "regenerer", "nouvelle_conversation", "ouvrir_lien"}
)


class Fenetre(Protocol):
    """Port de la fenêtre (pywebview `Window`) : exécute du JavaScript dans l'interface."""

    def evaluate_js(self, script: str) -> Any: ...


class Pont:
    """Classe exposée en `js_api` ; délègue à un module par domaine."""

    def __init__(
        self,
        service: AssistantService,
        fenetre: Fenetre,
        liste_blanche: ConfigListeBlanche | None = None,
    ) -> None:
        # Attributs privés : pywebview n'expose pas les noms en `_`.
        self._fenetre = fenetre
        self._liste_blanche = liste_blanche  # lue dans `config/` au premier `ouvrir_lien`
        self._conversation = Conversation(service, self._pousser)
        self._domaines: dict[str, Any] = {
            "mode": PontMode(),
            "reglages": PontReglages(),
            "historique": PontHistorique(),
            "retours": PontRetours(),
            "verification": PontVerification(),
        }

    def _pousser(self, lot: list[dict[str, Any]]) -> None:
        self._fenetre.evaluate_js(f"window.slmspRecevoir({json.dumps(lot)})")

    def signaler_pret(self) -> None:
        """Pousse `{"type": "pret"}` : l'interface sort de l'état « Préparation… »."""
        self._pousser([{"type": "pret"}])

    def envoyer(
        self,
        tache: str,
        messages: Sequence[Mapping[str, Any]],
        options: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Lance la génération et rend la main : `{"ok": true}`. Les évènements suivent.

        Refus (`{"ok": false, ...}`) : `generation-en-cours` (une génération à la fois), ou
        `requete-invalide` (Tâche inconnue ou inactive, conversation invalide).
        """
        return self._conversation.envoyer(tache, messages, options)

    def arreter(self) -> dict[str, Any]:
        """Arrête la génération en cours : `{"ok": true, "en_cours": bool}`.

        L'itérateur est fermé, `Fin(raison="interrompue")` est poussé ; `llama-server`
        reste actif et réutilisable.
        """
        return self._conversation.arreter()

    def regenerer(self) -> dict[str, Any]:
        """Relance le dernier `envoyer` à l'identique. Refus : `rien-a-regenerer`."""
        return self._conversation.regenerer()

    def nouvelle_conversation(self) -> dict[str, Any]:
        """Oublie le dernier envoi (donc `regenerer`). Refus : `generation-en-cours`."""
        return self._conversation.nouvelle_conversation()

    def ouvrir_lien(self, url: str) -> dict[str, Any]:
        """Confie `url` au navigateur du système (Q1 : la WebView ne navigue jamais).

        Seule une URL `https` (port 443, sans identifiants) dont l'hôte figure exactement dans la
        Liste blanche est acceptée ; sinon `lien-refuse`. Bouchon : l'ouverture elle-même revient à
        la story 12.6 et répond `non-implementee` d'ici là (l'interface copie alors le lien).
        """
        if not self._lien_autorise(url):
            return reponse_erreur(CODE_LIEN_REFUSE, "Ce lien ne peut pas être ouvert.")
        return reponse_erreur(CODE_NON_IMPLEMENTEE, "ouvrir_lien : non implémentée")

    def _lien_autorise(self, url: object) -> bool:
        if not isinstance(url, str) or len(url) > 2048:
            return False
        try:
            cible = analyser_url(url)
        except ValueError:
            return False
        if cible.schema != "https" or cible.identifiants or cible.port not in (None, 443):
            return False
        if self._liste_blanche is None:
            try:
                self._liste_blanche = charger_liste_blanche()
            except SlmspError:
                LOGGER.error("ouvrir_lien : Liste blanche illisible")
                return False
        return cible.hote in self._liste_blanche.hotes

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        """Appelle `nom` (voir le docstring du module). Jamais d'exception vers l'interface."""
        try:
            domaine, _, methode = nom.partition(".")
            if methode:
                cible = self._domaines.get(domaine)
                if cible is None:
                    return reponse_erreur(CODE_INCONNUE, f"méthode inconnue : {nom}")
                return cible.appeler(methode, *args)
            if nom in METHODES_DIRECTES:
                cible_locale = getattr(self, nom)
                try:
                    inspect.signature(cible_locale).bind(*args)
                except TypeError:
                    return reponse_erreur(CODE_INCONNUE, f"arguments invalides pour {nom}")
                return cible_locale(*args)
            return reponse_erreur(CODE_INCONNUE, f"méthode inconnue : {nom}")
        except NonImplementee as exc:
            return reponse_erreur(CODE_NON_IMPLEMENTEE, str(exc))
        except Exception as exc:
            LOGGER.error("appel %s : %s", nom, type(exc).__name__)
            return reponse_erreur("erreur-interne", "Un problème est survenu.")


__all__ = ["Fenetre", "NonImplementee", "Pont"]
