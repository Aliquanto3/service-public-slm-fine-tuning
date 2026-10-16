"""Conversation du pont (story 12.5) : un fil de travail consomme `AssistantService.repondre`.

Une génération à la fois. Les évènements (`core.evenements.vers_dict`) sont poussés par lots :
tout évènement autre qu'un `Jeton` vide le lot, les `Jeton` s'accumulent jusqu'à
`JETONS_PAR_LOT` ou `DELAI_LOT_S`. `arreter()` rend la main tout de suite ; le fil ferme
l'itérateur dès le prochain évènement (jamais depuis un autre fil : un générateur en cours
d'exécution ne se ferme pas) puis pousse `Fin(raison="interrompue")`. Le texte saisi n'est
jamais journalisé (AD-23) : seuls la classe d'exception et la Tâche partent au logger.
"""

from __future__ import annotations

import copy
import logging
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Final

from slmsp.core.erreurs import SlmspError
from slmsp.core.evenements import Erreur, Fin, Jeton, vers_dict
from slmsp.harness.service import CODE_ERREUR, MESSAGE_ERREUR, AssistantService, masquer

LOGGER: Final = logging.getLogger("slmsp.app.pont")
JETONS_PAR_LOT: Final = 16
DELAI_LOT_S: Final = 0.04
CODE_EN_COURS: Final = "generation-en-cours"
CODE_RIEN: Final = "rien-a-regenerer"
CODE_REFUS: Final = "requete-invalide"

Pousser = Callable[[list[dict[str, Any]]], None]
Envoi = tuple[str, list[dict[str, Any]], dict[str, Any]]


def reponse_erreur(code: str, message: str) -> dict[str, Any]:
    """Réponse JSON d'un refus."""
    return {"ok": False, "erreur": {"code": code, "message": message}}


class Conversation:
    """État d'envoi du pont : dernier envoi (pour `regenerer`) et génération en cours."""

    def __init__(self, service: AssistantService, pousser: Pousser) -> None:
        self._service = service
        self._pousser = pousser
        self._verrou = threading.Lock()
        self._fil: threading.Thread | None = None
        self._arret = threading.Event()
        self._dernier: Envoi | None = None

    def _actif(self) -> bool:
        return self._fil is not None and self._fil.is_alive()

    def attendre(self, delai: float | None = None) -> None:
        """Attend la fin du fil courant (tests)."""
        fil = self._fil
        if fil is not None:
            fil.join(delai)

    def envoyer(
        self,
        tache: str,
        messages: Sequence[Mapping[str, Any]],
        options: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        copie = [dict(m) for m in messages]
        return self._lancer((tache, copy.deepcopy(copie), dict(options or {})))

    def _lancer(self, envoi: Envoi) -> dict[str, Any]:
        tache, messages, options = envoi
        with self._verrou:
            if self._actif():
                return reponse_erreur(CODE_EN_COURS, "Une réponse est déjà en cours.")
            try:
                flux = self._service.repondre(tache, copy.deepcopy(messages), dict(options))
            except SlmspError as exc:
                saisis = [str(m.get("content", "")) for m in messages]
                return reponse_erreur(CODE_REFUS, masquer(str(exc), saisis))
            except Exception as exc:
                LOGGER.error("Tâche %s : refus %s", tache, type(exc).__name__)
                return reponse_erreur(CODE_REFUS, "Requête invalide.")
            self._dernier = envoi
            self._arret = threading.Event()
            self._fil = threading.Thread(
                target=self._consommer, args=(flux, self._arret, tache), daemon=True
            )
            self._fil.start()
        return {"ok": True}

    def arreter(self) -> dict[str, Any]:
        with self._verrou:
            actif = self._actif()
            if actif:
                self._arret.set()
        return {"ok": True, "en_cours": actif}

    def regenerer(self) -> dict[str, Any]:
        with self._verrou:
            envoi = self._dernier
        if envoi is None:
            return reponse_erreur(CODE_RIEN, "Aucune réponse à régénérer.")
        return self._lancer(envoi)

    def nouvelle_conversation(self) -> dict[str, Any]:
        with self._verrou:
            if self._actif():
                return reponse_erreur(CODE_EN_COURS, "Une réponse est en cours.")
            self._dernier = None
        return {"ok": True}

    # --- Fil de travail ------------------------------------------------------------------

    def _consommer(self, flux: Any, arret: threading.Event, tache: str) -> None:
        lot: list[dict[str, Any]] = []
        debut_lot = time.monotonic()

        def vider() -> None:
            nonlocal lot, debut_lot
            if lot:
                envoi, lot = lot, []
                self._pousser(envoi)
            debut_lot = time.monotonic()

        try:
            for evenement in flux:
                if arret.is_set():
                    break
                lot.append(vers_dict(evenement))
                plein = len(lot) >= JETONS_PAR_LOT or time.monotonic() - debut_lot >= DELAI_LOT_S
                if not isinstance(evenement, Jeton) or plein:
                    vider()
                if isinstance(evenement, (Fin, Erreur)):
                    return
            if arret.is_set():
                vider()
                self._pousser([vers_dict(Fin(raison="interrompue"))])
            else:
                vider()
        except Exception as exc:
            LOGGER.error("Tâche %s : échec du fil %s", tache, type(exc).__name__)
            try:
                self._pousser([vers_dict(Erreur(code=CODE_ERREUR, message=MESSAGE_ERREUR))])
            except Exception:
                LOGGER.error("Tâche %s : évènement d'erreur non remis", tache)
        finally:
            fermer = getattr(flux, "close", None)
            if callable(fermer):
                fermer()
