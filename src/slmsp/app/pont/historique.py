"""Pont, domaine « Historique » : bouchon (story 12.5), à implémenter par la story 12.11.

Contrat JSON prévu (chaque méthode rend `{"ok": true, ...}` ou lève ; le pont convertit
l'exception en `{"ok": false, "erreur": {"code", "message"}}`) :
- `lister()` -> `{"ok": true, "conversations": [{id, titre, tache, date}]}`.
- `ouvrir(id: str)` -> `{"ok": true, "conversation": {id, titre, tache, messages}}`.
- `supprimer(id: str)`, `annuler_suppression(id: str)`, `tout_effacer()` -> `{"ok": true}`.

Toute méthode lève `NonImplementee` tant que la story propriétaire n'est pas faite.
"""

from __future__ import annotations

from typing import Any

from slmsp.app.pont.erreurs import NonImplementee


class PontHistorique:
    """Bouchon : `appeler(nom, *args)` lève `NonImplementee`."""

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        raise NonImplementee(f"historique.{nom} : non implémentée")
