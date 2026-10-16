"""Pont, domaine « Mode connecté et hors ligne » (story 12.9, FR-10, FR-11, FR-38).

Chaque méthode rend `{"ok": true, ...}` ou lève ; le pont convertit l'exception en
`{"ok": false, "erreur": {"code", "message"}}`. Contrat final :

- `etat()` -> `{"ok": true, "mode": "connecte"|"hors_ligne", "hors_ligne": bool,
  "force": bool, "detail": "connecte"|"hors-ligne-detecte"|"hors-ligne-force"}`. Lire l'état
  peut déclencher la sonde du Mode (période échue) ; sauf hors ligne forcé, où rien ne sort.
- `forcer_hors_ligne(actif: bool)` -> même forme que `etat()`. Persiste `hors_ligne_force`
  dans le stockage ; `forcer(True)` coupe tout réseau, sonde comprise.
- `journal(limite: int | None)` -> `{"ok": true, "entrees": [{horodatage (ISO), profil, hote,
  methode, outil, termes, statut, mode}]}`, du plus récent au plus ancien (30 jours glissants).
- `effacer_journal()` -> `{"ok": true}`.

Poussée : à chaque changement de Mode observé (lecture, forçage), `{"type": "mode", "mode",
"hors_ligne", "force"}` part vers l'interface (`window.slmspRecevoir`), qui émet sur le bus
`evenement:mode`, puis `mode:change {hors_ligne}`. `rafraichir()` peut être appelé après une
sonde pour pousser un changement.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Final

from slmsp.app.pont.erreurs import NonImplementee

if TYPE_CHECKING:
    from slmsp.app.stockage import JournalApplication, Stockage
    from slmsp.core.ports import ModePort

CONNECTE: Final = "connecte"
HORS_LIGNE: Final = "hors_ligne"
FORCE: Final = "hors-ligne-force"
CLE_REGLAGE: Final = "hors_ligne_force"
METHODES: Final = frozenset({"etat", "forcer_hors_ligne", "journal", "effacer_journal"})


class PontMode:
    """État du Mode et journal des Requêtes sortantes.

    `mode` : port `ModePort` (avec `forcer` si le Mode est forçable). `stockage` : réglage
    persistant et journal ; sans lui, le forçage vaut pour la session et le journal est vide.
    `pousser` : reçoit un lot d'évènements.
    """

    def __init__(
        self,
        mode: ModePort | None = None,
        stockage: Stockage | None = None,
        pousser: Callable[[list[dict[str, Any]]], None] | None = None,
    ) -> None:
        self._mode = mode
        self._stockage = stockage
        self._pousser = pousser
        self._verrou = threading.Lock()
        self._dernier: tuple[str, bool] | None = None
        self._force_session = False
        self._journal: JournalApplication | None = None
        if stockage is not None:
            from slmsp.app.stockage import JournalApplication

            self._journal = JournalApplication(stockage)
            if stockage.lire_reglage(CLE_REGLAGE):
                self._appliquer_force(True)

    def _forcable(self) -> Callable[[bool], Any] | None:
        return getattr(self._mode, "forcer", None)

    def _appliquer_force(self, actif: bool) -> None:
        self._force_session = actif
        forcer = self._forcable()
        if forcer is not None:
            forcer(actif)

    def _detail(self) -> str:
        if self._mode is None:
            return FORCE if self._force_session else "hors-ligne-detecte"
        return str(self._mode.mode_courant())

    def _etat(self) -> dict[str, Any]:
        detail = self._detail()
        hors_ligne = detail != CONNECTE
        return {
            "mode": HORS_LIGNE if hors_ligne else CONNECTE,
            "hors_ligne": hors_ligne,
            "force": detail == FORCE,
            "detail": detail,
        }

    def rafraichir(self) -> dict[str, Any]:
        """Lit le Mode et pousse `{"type": "mode", ...}` s'il a changé depuis la dernière fois."""
        etat = self._etat()
        cle = (etat["mode"], etat["force"])
        with self._verrou:
            change = cle != self._dernier
            self._dernier = cle
        if change and self._pousser is not None:
            self._pousser(
                [
                    {
                        "type": "mode",
                        "mode": etat["mode"],
                        "hors_ligne": etat["hors_ligne"],
                        "force": etat["force"],
                    }
                ]
            )
        return {"ok": True, **etat}

    def etat(self) -> dict[str, Any]:
        return self.rafraichir()

    def forcer_hors_ligne(self, actif: bool) -> dict[str, Any]:
        actif = bool(actif)
        if self._stockage is not None:
            self._stockage.ecrire_reglage(CLE_REGLAGE, actif)
        self._appliquer_force(actif)
        return self.rafraichir()

    def journal(self, limite: int | None = None) -> dict[str, Any]:
        if self._journal is None:
            return {"ok": True, "entrees": []}
        entrees = [
            e.model_dump(mode="json", exclude={"schema_version"})
            for e in self._journal.lister(limite)
        ]
        return {"ok": True, "entrees": entrees}

    def effacer_journal(self) -> dict[str, Any]:
        if self._journal is not None:
            self._journal.effacer()
        return {"ok": True}

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        if nom not in METHODES:
            raise NonImplementee(f"mode.{nom} : méthode inconnue")
        return getattr(self, nom)(*args)
