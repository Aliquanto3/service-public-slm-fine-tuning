"""Conversation du pont (story 12.5) : un fil de travail consomme `AssistantService.repondre`.

Une génération à la fois. Les évènements (`core.evenements.vers_dict`) sont poussés par lots :
tout évènement autre qu'un `Jeton` vide le lot, les `Jeton` s'accumulent jusqu'à
`JETONS_PAR_LOT` ou `DELAI_LOT_S`. `arreter()` est effectif tout de suite, même si le LLM
ne rend aucun jeton : il pousse `Fin(raison="interrompue")`, libère l'état (un nouvel `envoyer`
est accepté) et lève le drapeau de la génération. Le fil de cette génération, éventuellement
bloqué dans `next(flux)`, ignore ses évènements tardifs (aucun push après l'arrêt) et ferme
l'itérateur à son réveil (jamais depuis un autre fil : un générateur en cours d'exécution ne se
ferme pas). `llama-server` n'est pas touché. Le texte saisi n'est
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
        self._verrou = threading.Lock()  # état (génération active, dernier envoi)
        self._envoi = threading.RLock()  # sérialise les poussées et l'arrêt (ordre des évènements)
        self._fil: threading.Thread | None = None
        self._courant: threading.Event | None = None  # drapeau d'arrêt de la génération active
        self._dernier: Envoi | None = None

    def _actif(self) -> bool:
        return self._courant is not None

    def generation_en_cours(self) -> bool:
        """Vrai tant qu'une réponse se génère (la vérification FR-12 attend, story 13.6)."""
        with self._verrou:
            return self._actif()

    def _emettre(self, arret: threading.Event, lot: list[dict[str, Any]]) -> None:
        """Pousse `lot` si la génération n'est pas arrêtée ; `Fin`/`Erreur` libère l'état."""
        with self._envoi:
            if arret.is_set():
                return
            if any(e.get("type") in ("fin", "erreur") for e in lot):
                with self._verrou:
                    if self._courant is arret:
                        self._courant = None  # libre avant la poussée : `envoyer` suit `Fin`
            self._pousser(lot)

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
                entree = options.get("entree")
                if isinstance(entree, Mapping):
                    saisis.extend(str(v) for v in entree.values() if isinstance(v, str))
                elif entree is not None:
                    saisis.append(str(entree))
                return reponse_erreur(CODE_REFUS, masquer(str(exc), saisis))
            except Exception as exc:
                LOGGER.error("Tâche %s : refus %s", tache, type(exc).__name__)
                return reponse_erreur(CODE_REFUS, "Requête invalide.")
            self._dernier = envoi
            arret = threading.Event()
            self._courant = arret
            self._fil = threading.Thread(
                target=self._consommer, args=(flux, arret, tache), daemon=True
            )
            self._fil.start()
        return {"ok": True}

    def arreter(self) -> dict[str, Any]:
        with self._envoi:
            with self._verrou:
                arret = self._courant
                self._courant = None
            actif = arret is not None
            if arret is not None:
                arret.set()
                try:
                    self._pousser([vers_dict(Fin(raison="interrompue"))])
                except Exception as exc:
                    LOGGER.error("arrêt : évènement non remis (%s)", type(exc).__name__)
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

    def oublier_dernier(self) -> None:
        """Oublie le dernier envoi (après l'effacement de l'historique)."""
        with self._verrou:
            self._dernier = None

    # --- Fil de travail ------------------------------------------------------------------

    def _consommer(self, flux: Any, arret: threading.Event, tache: str) -> None:
        lot: list[dict[str, Any]] = []
        debut_lot = time.monotonic()

        def vider() -> None:
            nonlocal lot, debut_lot
            if lot:
                envoi, lot = lot, []
                self._emettre(arret, envoi)
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
            vider()
        except Exception as exc:
            LOGGER.error("Tâche %s : échec du fil %s", tache, type(exc).__name__)
            try:
                self._emettre(arret, [vers_dict(Erreur(code=CODE_ERREUR, message=MESSAGE_ERREUR))])
            except Exception:
                LOGGER.error("Tâche %s : évènement d'erreur non remis", tache)
        finally:
            with self._verrou:
                if self._courant is arret:
                    self._courant = None
            fermer = getattr(flux, "close", None)
            if callable(fermer):
                fermer()
