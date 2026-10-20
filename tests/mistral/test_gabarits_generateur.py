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
    "amorces-ct",
    # Story O6b : régénération (gabarits de correction et phrases fixes par code de motif).
    "cr-correction",
    "lc-correction",
    "ct-correction",
    "corrections",
)
TACHES = ("Q", "RD", "CR", "LC", "CO", "RE", "CT", "generique", "validation", "verification")
INTERDITS = ("?", "«", "»", '"', "“", "”")
RE_EMPLACEMENT = re.compile(r"\{([a-z_]+)\}")
CORRECTIONS = ("cr-correction", "lc-correction", "ct-correction")
PHRASES_CORRECTIONS = "corrections"


def test_jeu_de_gabarits_complet() -> None:
    assert sorted(p.stem for p in DOSSIER.iterdir()) == sorted(GABARITS)
    assert all(p.suffix == ".md" for p in DOSSIER.iterdir())


@pytest.mark.parametrize("nom", GABARITS)
def test_gabarit_conforme(nom: str) -> None:
    chemin = DOSSIER / f"{nom}.md"
    gabarit = valider_gabarit(chemin, cles_optionnelles=("max_tokens",))
    assert gabarit.id == nom
    assert gabarit.version >= 1
    assert gabarit.front_matter["tache"] in TACHES
    if "max_tokens" in gabarit.front_matter:
        assert int(gabarit.front_matter["max_tokens"]) >= 1
    if nom == PHRASES_CORRECTIONS:  # phrases fixes par code : déclarées, jamais des emplacements
        assert RE_EMPLACEMENT.findall(gabarit.consigne) == []
        return
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


PLAFONNES = ("traces-q", "traces-rd", "cr", "lc", "ct", "generique")


@pytest.mark.parametrize("nom", PLAFONNES)
def test_consignes_de_longueur_et_de_forme(nom: str) -> None:
    """Story 9.10 : consigne de longueur sur l'emplacement réservé, consigne de forme, version
    incrémentée et `max_tokens` resserré (1 600 pour CR, 800 sinon)."""
    gabarit = valider_gabarit(DOSSIER / f"{nom}.md", cles_optionnelles=("max_tokens",))
    assert "plafond_mots_tache" in gabarit.emplacements
    longueur = (
        "- Ta réponse finale à l'Agent ne dépasse pas {plafond_mots_tache} mots."
        if nom == "traces-rd"
        else "- Ta réponse ne dépasse pas {plafond_mots_tache} mots."
    )
    assert gabarit.consigne.count(longueur) == 1
    forme = {
        "cr": "- Commence directement par le titre de la section Participants : pas de titre",
        "ct": "- Commence directement par le bloc de l'expéditeur : pas de titre",
    }.get(nom, "- Commence directement par le contenu : pas de titre")
    assert gabarit.consigne.count(forme) == 1
    assert gabarit.version == (3 if nom in ("traces-rd", *REFONDUS_S5) else 2)
    assert int(gabarit.front_matter["max_tokens"]) == (1600 if nom == "cr" else 800)


REFONDUS_S5 = ("cr", "ct", "lc")
CONSIGNES_S5 = {
    "cr": (
        "- Organise le compte rendu en quatre sections, dans cet ordre, chacune ouverte par son "
        "titre seul sur sa ligne : Participants, Points abordés, Décisions, Actions.",
        "Un point discuté sans décision n'y figure pas et n'est jamais présenté comme décidé.",
        "chacune avec son responsable et son échéance quand la transcription les donne",
    ),
    "ct": (
        "avec ces blocs dans cet ordre : expéditeur, destinataire, lieu et date, objet, "
        "références, formule d'appel, corps, formule de politesse, signature.",
        "est remplacée par un emplacement entre crochets qui nomme le champ à compléter. Ne "
        "donne jamais de valeur inventée à la place.",
    ),
    "lc": (
        "- Reprends tous les montants, toutes les dates, toutes les durées et toutes les "
        "références du texte, avec leurs valeurs exactes.",
        "- N'ajoute aucune information absente du texte",
        "- Garde les termes juridiques du texte : explique-les en quelques mots, sans les "
        "remplacer.",
        "- Écris des phrases courtes avec des mots courants",
    ),
}


@pytest.mark.parametrize("nom", REFONDUS_S5)
def test_consignes_s5(nom: str) -> None:
    """Story S5 : consignes de structure (CR, CT) et de fidélité (LC), sans amorce ni exemple
    (aucun crochet ni emplacement d'exemple dans le gabarit, D1)."""
    gabarit = valider_gabarit(DOSSIER / f"{nom}.md", cles_optionnelles=("max_tokens",))
    for consigne in CONSIGNES_S5[nom]:
        assert gabarit.consigne.count(consigne) == 1, consigne
    texte = (DOSSIER / f"{nom}.md").read_text(encoding="utf-8")
    assert "[" not in texte and "]" not in texte
    if nom == "cr":
        assert "pas de titre ni d'intertitre en première ligne" not in gabarit.consigne


@pytest.mark.parametrize("nom", ("re",))
def test_consigne_de_forme_re(nom: str) -> None:
    """Story 9.11 : consigne de forme dans le gabarit RE, version 2, longueur inchangée."""
    gabarit = valider_gabarit(DOSSIER / f"{nom}.md", cles_optionnelles=("max_tokens",))
    assert gabarit.consigne.count("- Commence directement par le contenu : pas de titre") == 1
    assert "{plafond_mots}" in gabarit.consigne
    assert gabarit.version == 2
    assert int(gabarit.front_matter["max_tokens"]) == 1500


def test_date_de_mise_a_jour_rd_conditionnelle() -> None:
    """Story 9.12 : la date n'est demandée que si elle figure au résultat d'outil, version 3."""
    gabarit = valider_gabarit(DOSSIER / "traces-rd.md", cles_optionnelles=("max_tokens",))
    assert (
        "- Pour chaque jeu de données cité, donne son titre et son lien tels qu'ils figurent "
        "dans le résultat d'outil, et son producteur et sa date de dernière mise à jour "
        "seulement s'ils y figurent."
    ) in gabarit.consigne
    assert "son titre, son producteur, sa date de dernière mise à jour et son lien" not in (
        gabarit.consigne
    )
    assert "son titre, son producteur et son lien" not in gabarit.consigne
    assert gabarit.version == 3


@pytest.mark.parametrize("nom", CORRECTIONS)
def test_gabarits_de_correction_gardent_la_consigne_et_le_plafond(nom: str) -> None:
    """Story O6b : consigne de la Tâche inchangée, plafond de mots, emplacement corrections."""
    gabarit = valider_gabarit(DOSSIER / f"{nom}.md", cles_optionnelles=("max_tokens",))
    origine = valider_gabarit(
        DOSSIER / f"{nom.removesuffix('-correction')}.md", cles_optionnelles=("max_tokens",)
    )
    assert gabarit.consigne.startswith(origine.consigne)
    assert set(gabarit.emplacements) == {*origine.emplacements, "corrections"}
    assert gabarit.front_matter["max_tokens"] == origine.front_matter["max_tokens"]


@pytest.mark.parametrize("nom", sorted(set(GABARITS) - set(PLAFONNES) - set(CORRECTIONS)))
def test_autres_gabarits_sans_plafond_de_tache(nom: str) -> None:
    gabarit = valider_gabarit(DOSSIER / f"{nom}.md", cles_optionnelles=("max_tokens",))
    assert "plafond_mots_tache" not in gabarit.emplacements
