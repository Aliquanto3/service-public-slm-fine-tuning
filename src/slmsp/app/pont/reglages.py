"""Pont, domaine « Réglages » : bouchon (story 12.5), à implémenter par la story 12.10.

Contrat JSON prévu (chaque méthode rend `{"ok": true, ...}` ou lève ; le pont convertit
l'exception en `{"ok": false, "erreur": {"code", "message"}}`) :
- `lire()` -> `{"ok": true, "reglages": {cle: valeur}}`.
- `ecrire(cle: str, valeur)` -> `{"ok": true}`.
- `a_propos()` -> `{"ok": true, "version": str, "modele": str}`.

Toute méthode lève `NonImplementee` tant que la story propriétaire n'est pas faite.
"""

from __future__ import annotations

from typing import Any

from slmsp.app.pont.erreurs import NonImplementee


class PontReglages:
    """Bouchon : `appeler(nom, *args)` lève `NonImplementee`."""

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        raise NonImplementee(f"reglages.{nom} : non implémentée")
