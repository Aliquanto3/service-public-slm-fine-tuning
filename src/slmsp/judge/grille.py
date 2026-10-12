"""Lecture de la grille du Juge (`eval/grille-juge-v1.md`, lecture seule).

La grille est découpée en sections de niveau 2 (`## …`). La section envoyée au Juge pour
une Tâche est la section « Principes communs » suivie de la section de la Tâche (`## Q : …`),
titres compris. Le gabarit du prompt est la citation (`> `) de la section « Prompt du Juge
(gabarit) », sans les marqueurs de citation ; il doit porter les cinq placeholders de
`PLACEHOLDERS`. Chaque texte envoyé est identifié par son SHA-256 (clé du cache de verdicts).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from slmsp.core.canonique import sha256_hex
from slmsp.core.erreurs import ConfigurationInvalide

TITRE_PRINCIPES: Final = "Principes communs"
PREFIXE_GABARIT: Final = "Prompt du Juge"

PLACEHOLDERS: Final[tuple[str, ...]] = (
    "{tache}",
    "{section de la Tâche}",
    "{entree}",
    "{champs de référence}",
    "{sortie}",
)
"""Placeholders exigés dans le gabarit du prompt."""

_TITRE_TACHE = re.compile(r"^(?P<code>[A-Z]+) : ")


@dataclass(frozen=True)
class SectionGrille:
    """Texte de grille envoyé au Juge pour la Tâche `code` et son SHA-256."""

    code: str
    texte: str
    sha256: str


@dataclass(frozen=True)
class Grille:
    """Grille lue : version, sections par code de Tâche et gabarit du prompt."""

    chemin: Path
    version: str
    principes: str
    sections: Mapping[str, str]
    gabarit: str
    sha_gabarit: str

    def section(self, code: str) -> SectionGrille:
        """Principes communs + section de la Tâche `code` ; `ConfigurationInvalide` si absente."""
        propre = self.sections.get(code)
        if propre is None:
            raise ConfigurationInvalide(f"{self.chemin} : aucune section pour la Tâche {code!r}")
        texte = f"{self.principes}\n\n{propre}"
        return SectionGrille(code=code, texte=texte, sha256=sha256_hex(texte))


def _front_matter(lignes: list[str], chemin: Path) -> tuple[str, int]:
    """Version du front-matter et indice de la première ligne après lui."""
    if not lignes or lignes[0].strip() != "---":
        raise ConfigurationInvalide(f"{chemin} : front-matter absent")
    version: str | None = None
    for indice in range(1, len(lignes)):
        ligne = lignes[indice]
        if ligne.strip() == "---":
            if not version:
                raise ConfigurationInvalide(f"{chemin} : clé `version` absente du front-matter")
            return version, indice + 1
        cle, separateur, valeur = ligne.partition(":")
        if separateur and cle.strip() == "version":
            version = valeur.strip().strip("'\"")
    raise ConfigurationInvalide(f"{chemin} : front-matter non fermé")


def _sections(lignes: list[str]) -> list[tuple[str, str]]:
    """`(titre, texte)` de chaque section `## …` (titre compris), hors blocs de code."""
    sections: list[tuple[str, list[str]]] = []
    dans_code = False
    for ligne in lignes:
        if ligne.lstrip().startswith("```"):
            dans_code = not dans_code
        if not dans_code and ligne.startswith("## "):
            sections.append((ligne[3:].strip(), [ligne]))
        elif not dans_code and ligne.startswith("# "):
            sections.append(("", []))  # titre de document : clôt la section précédente
        elif sections:
            sections[-1][1].append(ligne)
    return [(titre, "\n".join(corps).strip()) for titre, corps in sections if titre]


def _gabarit(texte: str, chemin: Path) -> str:
    citation: list[str] = []
    for ligne in texte.splitlines()[1:]:
        if ligne.startswith(">"):
            citation.append(ligne[2:] if ligne.startswith("> ") else ligne[1:])
        elif citation and ligne.strip():
            break
    gabarit = "\n".join(citation).strip()
    if not gabarit:
        raise ConfigurationInvalide(f"{chemin} : gabarit du prompt (citation `> `) absent")
    manquants = [p for p in PLACEHOLDERS if p not in gabarit]
    if manquants:
        raise ConfigurationInvalide(
            f"{chemin} : placeholder(s) absent(s) du gabarit : {', '.join(manquants)}"
        )
    return gabarit


def charger_grille(chemin: str | Path) -> Grille:
    """Lit la grille `chemin`.

    Lève `ConfigurationInvalide` si le fichier est illisible, si le front-matter, la section
    « Principes communs », le gabarit ou l'un de ses placeholders manque.
    """
    chemin = Path(chemin)
    try:
        texte = chemin.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ConfigurationInvalide(
            f"{chemin} : grille du Juge illisible ({type(exc).__name__})"
        ) from None
    except UnicodeDecodeError:
        raise ConfigurationInvalide(f"{chemin} : grille du Juge non UTF-8") from None
    lignes = texte.replace("\r\n", "\n").split("\n")
    version, debut = _front_matter(lignes, chemin)
    principes: str | None = None
    gabarit: str | None = None
    sections: dict[str, str] = {}
    for titre, corps in _sections(lignes[debut:]):
        if titre == TITRE_PRINCIPES:
            if principes is not None:
                raise ConfigurationInvalide(f"{chemin} : section « {TITRE_PRINCIPES} » en double")
            principes = corps
        elif titre.startswith(PREFIXE_GABARIT):
            if gabarit is not None:
                raise ConfigurationInvalide(f"{chemin} : gabarit du prompt en double")
            gabarit = _gabarit(corps, chemin)
        elif (m := _TITRE_TACHE.match(titre)) is not None:
            if m["code"] in sections:
                raise ConfigurationInvalide(f"{chemin} : section de la Tâche {m['code']} en double")
            sections[m["code"]] = corps
    if principes is None:
        raise ConfigurationInvalide(f"{chemin} : section « {TITRE_PRINCIPES} » absente")
    if gabarit is None:
        raise ConfigurationInvalide(f"{chemin} : section « {PREFIXE_GABARIT} (gabarit) » absente")
    return Grille(
        chemin=chemin,
        version=version,
        principes=principes,
        sections=sections,
        gabarit=gabarit,
        sha_gabarit=sha256_hex(gabarit),
    )
