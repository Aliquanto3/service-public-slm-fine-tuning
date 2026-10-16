"""Ré-export de `slmsp.harness.assemblage` (compatibilité, story 12.1, Q10).

La racine de composition est partagée avec l'application : elle vit dans `harness`.
`JournalSqlite` reste exposé pour les tests qui le remplacent par un espion.
"""

from __future__ import annotations

from slmsp.harness.assemblage import (
    PREFIXE_BASE,
    Assemblage,
    ModeleInvalide,
    OutilsParesseux,
    assembler,
    plafonner_threads,
    slug_modele,
)
from slmsp.net.journal import JournalSqlite

__all__ = [
    "PREFIXE_BASE",
    "Assemblage",
    "JournalSqlite",
    "ModeleInvalide",
    "OutilsParesseux",
    "assembler",
    "plafonner_threads",
    "slug_modele",
]
