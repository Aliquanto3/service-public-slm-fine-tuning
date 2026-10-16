"""Langues de la Tâche TR, source unique : code ISO -> nom français de l'entrée du gabarit.

Lue par le banc de traduction (`benchmarks.moteurs.traduction`) et par la validation de
`config/application.toml` (`langues_traduction`, vue Traduction de l'application).
"""

from __future__ import annotations

LANGUES: dict[str, str] = {
    "en": "anglais",
    "fr": "français",
    "es": "espagnol",
    "ar": "arabe",
    "pt": "portugais",
    "de": "allemand",
}

__all__ = ["LANGUES"]
