"""Pont, domaine « Vérification en ligne (FR-12) » : bouchon (story 12.5).

À implémenter par la story 13.5.

Contrat JSON prévu (chaque méthode rend `{"ok": true, ...}` ou lève ; le pont convertit
l'exception en `{"ok": false, "erreur": {"code", "message"}}`) :
- `verifier(url: str)` -> `{"ok": true, "resultat": {...}}` ; seule l'URL déjà citée est
  transmise, jamais la question ni la réponse.

Toute méthode lève `NonImplementee` tant que la story propriétaire n'est pas faite.
"""

from __future__ import annotations

from typing import Any

from slmsp.app.pont.erreurs import NonImplementee


class PontVerification:
    """Bouchon : `appeler(nom, *args)` lève `NonImplementee`."""

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        raise NonImplementee(f"verification.{nom} : non implémentée")
