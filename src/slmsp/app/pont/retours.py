"""Pont, domaine « Retours » : bouchon (story 12.5), à implémenter par la story 12.11.

Contrat JSON prévu (chaque méthode rend `{"ok": true, ...}` ou lève ; le pont convertit
l'exception en `{"ok": false, "erreur": {"code", "message"}}`) :
- `noter(conversation_id: str, message: int, jugement: "pouce_haut"|"pouce_bas",
  commentaire: str | None)` -> `{"ok": true}`.
- `lister()` -> `{"ok": true, "retours": [...]}`.

Toute méthode lève `NonImplementee` tant que la story propriétaire n'est pas faite.
"""

from __future__ import annotations

from typing import Any

from slmsp.app.pont.erreurs import NonImplementee


class PontRetours:
    """Bouchon : `appeler(nom, *args)` lève `NonImplementee`."""

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        raise NonImplementee(f"retours.{nom} : non implémentée")
