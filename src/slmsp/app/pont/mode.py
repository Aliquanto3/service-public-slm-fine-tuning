"""Pont, domaine « Mode connecté et hors ligne » : bouchon (story 12.5).

À implémenter par la story 12.9.

Contrat JSON prévu (chaque méthode rend `{"ok": true, ...}` ou lève ; le pont convertit
l'exception en `{"ok": false, "erreur": {"code", "message"}}`) :
- `etat()` -> `{"ok": true, "mode": "connecte"|"hors_ligne", "force": bool}`.
- `forcer_hors_ligne(actif: bool)` -> `{"ok": true, "mode": ...}`.
- `journal(limite: int | None)` -> `{"ok": true, "entrees": [{horodatage, profil, hote,
  methode, outil, termes, statut, mode}]}`.

Toute méthode lève `NonImplementee` tant que la story propriétaire n'est pas faite.
"""

from __future__ import annotations

from typing import Any

from slmsp.app.pont.erreurs import NonImplementee


class PontMode:
    """Bouchon : `appeler(nom, *args)` lève `NonImplementee`."""

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        raise NonImplementee(f"mode.{nom} : non implémentée")
