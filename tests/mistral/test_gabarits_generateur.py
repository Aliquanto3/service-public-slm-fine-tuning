"""Gabarits du générateur (`config/prompts/generateur/`) : verrous structurels (AD-3 verrou 6).

Chaque gabarit passe la liste blanche de `core.gabarits`, ne contient que des consignes et des
emplacements `{nom}`, et aucune question, réponse ou amorce rédigée (D1.1) : ni « ? », ni
guillemets, ni emplacement non déclaré.
"""

from __future__ import annotations

import re

import pytest

from slmsp.core.canonique import sha256_hex
from slmsp.core.config import racine_projet
from slmsp.core.gabarits import valider_gabarit

DOSSIER = racine_projet() / "config" / "prompts" / "generateur"
GABARITS = (
    "traces-q",
    "traces-rd",
    "scenario-reunion",
    "transcription-cr",
    "cr",
    "lc",
    "co",
    "re",
    "ct",
    "generique",
    "validation",
)
TACHES = ("Q", "RD", "CR", "LC", "CO", "RE", "CT", "generique", "validation")
INTERDITS = ("?", "«", "»", '"', "“", "”")
RE_EMPLACEMENT = re.compile(r"\{([a-z_]+)\}")


def test_jeu_de_gabarits_complet() -> None:
    assert sorted(p.stem for p in DOSSIER.iterdir()) == sorted(GABARITS)
    assert all(p.suffix == ".md" for p in DOSSIER.iterdir())


@pytest.mark.parametrize("nom", GABARITS)
def test_gabarit_conforme(nom: str) -> None:
    chemin = DOSSIER / f"{nom}.md"
    gabarit = valider_gabarit(chemin, cles_optionnelles=("max_tokens",))
    assert gabarit.id == nom
    assert gabarit.version == 1
    assert gabarit.front_matter["tache"] in TACHES
    if "max_tokens" in gabarit.front_matter:
        assert int(gabarit.front_matter["max_tokens"]) >= 1
    assert set(RE_EMPLACEMENT.findall(gabarit.consigne)) == set(gabarit.emplacements)


@pytest.mark.parametrize("nom", GABARITS)
def test_gabarit_sans_texte_redige(nom: str) -> None:
    """Ni question, ni citation, ni emplacement hors de la section des déclarations."""
    texte = (DOSSIER / f"{nom}.md").read_text(encoding="utf-8")
    for caractere in INTERDITS:
        assert caractere not in texte, f"{nom} : caractère {caractere!r} interdit"
    gabarit = valider_gabarit(DOSSIER / f"{nom}.md", cles_optionnelles=("max_tokens",))
    assert set(RE_EMPLACEMENT.findall(texte)) <= set(gabarit.emplacements)


def test_validation_reservee() -> None:
    gabarit = valider_gabarit(DOSSIER / "validation.md", cles_optionnelles=("max_tokens",))
    assert gabarit.front_matter["tache"] == "validation"


def test_sha_des_octets() -> None:
    for nom in GABARITS:
        chemin = DOSSIER / f"{nom}.md"
        gabarit = valider_gabarit(chemin, cles_optionnelles=("max_tokens",))
        assert gabarit.sha256 == sha256_hex(chemin.read_bytes())
