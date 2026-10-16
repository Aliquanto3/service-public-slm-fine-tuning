"""Erreurs du pont (story 12.5)."""

from __future__ import annotations

from slmsp.core.erreurs import SlmspError


class NonImplementee(SlmspError):
    """Méthode du pont déclarée d'avance, dont la story propriétaire n'est pas encore faite."""
