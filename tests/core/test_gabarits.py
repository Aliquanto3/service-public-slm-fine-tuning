"""Validateur structurel des gabarits de prompt (story 4.1, AD-3 verrou 6, D1.1).

Les gabarits de test sont fabriqués ici avec des chaînes factices ; aucun ne ressemble à
un vrai prompt.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from slmsp.core.erreurs import SlmspError
from slmsp.core.gabarits import LONGUEUR_MAX, GabaritInvalide, GabaritValide, valider_gabarit


def _gabarit(
    consigne: str = "<consigne-factice-1>",
    emplacements: str = "- alpha : <description-factice-1>",
    front: str = "id: g1\nversion: 1\ntache: Q",
) -> str:
    return f"---\n{front}\n---\n\n## Consigne\n\n{consigne}\n\n## Emplacements\n\n{emplacements}\n"


def _fautes(texte: str, **options: object) -> tuple[str, ...]:
    with pytest.raises(GabaritInvalide) as info:
        valider_gabarit(texte, **options)  # type: ignore[arg-type]
    return info.value.fautes


def test_gabarit_valide_texte() -> None:
    texte = _gabarit(
        consigne="<consigne-factice-1>\n\n- <puce-factice-1>\n- <puce-factice-2> {alpha}",
        emplacements="- alpha : <description-factice-1>\n- beta_gamma : <description-factice-2>",
    )
    gabarit = valider_gabarit(texte)
    assert isinstance(gabarit, GabaritValide)
    assert gabarit.id == "g1"
    assert gabarit.version == 1
    assert dict(gabarit.front_matter) == {"id": "g1", "version": "1", "tache": "Q"}
    assert gabarit.consigne == (
        "<consigne-factice-1>\n\n- <puce-factice-1>\n- <puce-factice-2> {alpha}"
    )
    assert list(gabarit.emplacements) == ["alpha", "beta_gamma"]
    assert gabarit.emplacements["beta_gamma"] == "<description-factice-2>"
    assert gabarit.sha256 == hashlib.sha256(texte.encode("utf-8")).hexdigest()


def test_gabarit_valide_fichier_et_empreinte_des_octets(tmp_path: Path) -> None:
    chemin = tmp_path / "g1.md"
    octets = _gabarit().replace("\n", "\r\n").encode("utf-8")
    chemin.write_bytes(octets)
    gabarit = valider_gabarit(chemin)
    assert gabarit.sha256 == hashlib.sha256(octets).hexdigest()
    assert gabarit.consigne == "<consigne-factice-1>"


def test_fichier_illisible_ou_non_utf8(tmp_path: Path) -> None:
    with pytest.raises(GabaritInvalide, match="illisible"):
        valider_gabarit(tmp_path / "absent.md")
    chemin = tmp_path / "latin1.md"
    chemin.write_bytes(_gabarit(consigne="<consigne-factice-é>").encode("latin-1"))
    with pytest.raises(GabaritInvalide, match="UTF-8"):
        valider_gabarit(chemin)


def test_erreur_derive_de_slmsp_error() -> None:
    assert issubclass(GabaritInvalide, SlmspError)


# --- Front-matter -----------------------------------------------------------------------------


def test_front_matter_absent() -> None:
    texte = "## Consigne\n\n<consigne-factice-1>\n\n## Emplacements\n\n- alpha : <d>\n"
    assert any("front-matter absent" in faute for faute in _fautes(texte))


def test_front_matter_non_ferme() -> None:
    assert any("non fermé" in f for f in _fautes("---\nid: g1\nversion: 1\ntache: Q\n"))


@pytest.mark.parametrize(
    ("front", "attendu"),
    [
        ("id: g1\nversion: 1", "« tache » manquante"),
        ("id: g1\nversion: 1\ntache: Q\nautre: x", "« autre » non admise"),
        ("id: g1\nid: g2\nversion: 1\ntache: Q", "« id » en double"),
        ("id: g1\nversion: 0\ntache: Q", "entier"),
        ("id: g1\nversion: un\ntache: Q", "entier"),
        ("id: g1\nversion: 1\ntache:", "« tache » sans valeur"),
        ("id g1\nversion: 1\ntache: Q", "cle: valeur"),
    ],
)
def test_front_matter_fautif(front: str, attendu: str) -> None:
    assert any(attendu in faute for faute in _fautes(_gabarit(front=front)))


def test_cles_parametrables() -> None:
    texte = _gabarit(front="id: g1\nversion: 2\nsource: s1")
    gabarit = valider_gabarit(texte, cles_requises=("id", "version"), cles_optionnelles=("source",))
    assert gabarit.version == 2
    assert gabarit.front_matter["source"] == "s1"


# --- Corps ------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "texte",
    [
        "---\nid: g1\nversion: 1\ntache: Q\n---\n\n## Consigne\n\n<c>\n",
        "---\nid: g1\nversion: 1\ntache: Q\n---\n\n"
        "## Emplacements\n\n- a : <d>\n\n## Consigne\n\n<c>\n",
        _gabarit(consigne="<c>\n\n## Exemples\n\n<c2>"),
        _gabarit(consigne="<c>\n\n### Sous-titre factice"),
        _gabarit(consigne="# Titre factice\n\n<c>"),
    ],
)
def test_titres_hors_liste_blanche(texte: str) -> None:
    assert any("titres attendus" in faute for faute in _fautes(texte))


def test_texte_hors_section_et_separateur() -> None:
    texte = _gabarit().replace("\n## Consigne", "<hors-section>\n## Consigne")
    assert any("hors section" in faute for faute in _fautes(texte))
    assert any("séparateur" in f for f in _fautes(_gabarit(consigne="<c>\n\n---\n\n<c2>")))


@pytest.mark.parametrize("soulignement", ["===", "***", "___", "--", "-----"])
def test_soulignements_et_separateurs(soulignement: str) -> None:
    fautes = _fautes(_gabarit(consigne=f"<c>\n{soulignement}\n\n<c2>"))
    assert any("séparateur" in faute for faute in fautes), fautes


def test_titres_fautifs_cites_par_numero_de_ligne_seulement() -> None:
    fautes = _fautes(_gabarit(consigne="<c>\n\n## <titre-secret-factice>"))
    (faute,) = (f for f in fautes if "titres attendus" in f)
    assert "<titre-secret-factice>" not in faute
    assert "ligne 7" in faute and "ligne 11" in faute


def test_ligne_de_crochets_tres_profonde() -> None:
    fautes = _fautes(_gabarit(consigne="[" * 100_000))
    assert fautes


def test_bom_et_fins_de_ligne_cr(tmp_path: Path) -> None:
    chemin = tmp_path / "g1.md"
    octets = (chr(0xFEFF) + _gabarit().replace("\n", "\r")).encode("utf-8")
    chemin.write_bytes(octets)
    gabarit = valider_gabarit(chemin)
    assert gabarit.id == "g1"
    assert gabarit.consigne == "<consigne-factice-1>"
    assert gabarit.sha256 == hashlib.sha256(octets).hexdigest()


def test_consigne_et_emplacements_vides() -> None:
    fautes = _fautes(_gabarit(consigne="", emplacements=""))
    assert "section « Consigne » vide" in fautes
    assert "section « Emplacements » vide" in fautes


@pytest.mark.parametrize(
    "emplacements",
    ["- Alpha : <d>", "- alpha: <d>", "alpha : <d>", "- alpha-beta : <d>", "- alpha :"],
)
def test_emplacement_mal_forme(emplacements: str) -> None:
    fautes = _fautes(_gabarit(emplacements=emplacements))
    assert any("emplacement « - nom : description »" in faute for faute in fautes)


def test_emplacement_en_double() -> None:
    fautes = _fautes(_gabarit(emplacements="- alpha : <d1>\n- alpha : <d2>"))
    assert any("en double" in faute for faute in fautes)


def test_longueur_maximale() -> None:
    texte = _gabarit(consigne="x" * LONGUEUR_MAX)
    assert any("longueur" in faute for faute in _fautes(texte))
    assert valider_gabarit(_gabarit(consigne="x" * 100), longueur_max=4000)
    assert any("longueur" in f for f in _fautes(_gabarit(), longueur_max=20))


# --- Contenu (D1.1) ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("consigne", "attendu"),
    [
        ("<c>\n\n```\n<code-factice>\n```", "backtick"),
        ("<c> `x`", "backtick"),
        ("<c>\n\n    <bloc-indente-factice>", "bloc indenté"),
        ("<c>\n\n\t<bloc-tabule-factice>", "bloc indenté"),
        ('<c> {"cle": 1}', "accolade"),
        ("<c> { alpha }", "accolade"),
        ("<c> }", "accolade"),
        ('["x", "y"]', "JSON"),
        ('"<chaine-factice>"', "JSON"),
        ("1234", "JSON"),
        ("> <citation-factice>", "citation"),
        ("Exemple de sortie factice.", "exemple"),
        ("<c> des EXEMPLES factices", "exemple"),
        ("<c> an example", "example"),
        ("<c>, par ex. <x>", "par ex"),
        ("<c>, e.g. <x>", "e.g."),
        ("<c> few-shot", "few-shot"),
        ("<c> fewshot", "few-shot"),
        ("<c> une réponse type", "réponse type"),
        ("<c> un MODÈLE DE RÉPONSE", "modèle de réponse"),
        ("Voici <c>", "voici"),
        ("<c> <|im_start|>", "jeton de chat"),
        ("<c> [INST]", "jeton de chat"),
        ("<c> [/INST]", "jeton de chat"),
        ("<c> <<SYS>>", "jeton de chat"),
        ("<c> </s>", "jeton de chat"),
        ("<c> <start_of_turn>", "jeton de chat"),
        ("<c> <end_of_turn>", "jeton de chat"),
        ("<c> <bos>", "jeton de chat"),
        ("<c> <eos>", "jeton de chat"),
        ("<c>\n\n~~~\n<code-factice>\n~~~", "~~~"),
        ("<c>\n\n     <bloc-cinq-espaces>", "bloc indenté"),
        ("<c>\n\n \t<bloc-espace-tabulation>", "bloc indenté"),
        ("<c> la réponse attendue", "réponse attendue"),
        ("<c> des SORTIES ATTENDUES", "réponse attendue"),
        ("<c>, i.e. <x>", "i.e."),
        ("<c>, p. ex. <x>", "p. ex."),
        ("<c> (ex. <x>)", "ex."),
    ],
)
def test_contenu_interdit(consigne: str, attendu: str) -> None:
    fautes = _fautes(_gabarit(consigne=consigne))
    assert any(attendu in faute for faute in fautes), fautes


@pytest.mark.parametrize(
    "ligne",
    [
        "Question : <x>",
        "Réponse : <x>",
        "reponse: <x>",
        "Q : <x>",
        "R: <x>",
        "Utilisateur : <x>",
        "Assistant : <x>",
        "Agent : <x>",
        "Usager : <x>",
        "Système : <x>",
        "Entrée : <x>",
        "Sortie : <x>",
        "User: <x>",
        "Input : <x>",
        "Output : <x>",
        "- Question : <x>",
        "**Réponse** : <x>",
        "1. Assistant : <x>",
        "_Réponse_ : <x>",
        "« Q » : <x>",
        "«Question» : <x>",
    ],
)
def test_ligne_de_dialogue(ligne: str) -> None:
    fautes = _fautes(_gabarit(consigne=f"<c>\n{ligne}"))
    assert any("dialogue" in faute for faute in fautes), fautes


def test_dialogue_dans_une_description_d_emplacement() -> None:
    fautes = _fautes(_gabarit(emplacements="- alpha : Réponse : <x>"))
    assert any("dialogue" in faute for faute in fautes)


def test_mots_proches_admis() -> None:
    consigne = (
        "La question de l'Agent appelle une réponse claire.\n"
        "- Questions ouvertes : <x>\n- L'usager reçoit le texte.\n- Le type de courrier."
    )
    gabarit = valider_gabarit(_gabarit(consigne=consigne, emplacements="- question : <d>"))
    assert list(gabarit.emplacements) == ["question"]


def test_toutes_les_fautes_sont_listees() -> None:
    texte = _gabarit(
        consigne="Exemple :\n\n```\n{}\n```\n> <x>\nQuestion : <x>",
        front="id: g1\nversion: 0",
    )
    with pytest.raises(GabaritInvalide) as info:
        valider_gabarit(texte)
    fautes = info.value.fautes
    for attendu in ("tache", "entier", "exemple", "backtick", "JSON", "citation", "dialogue"):
        assert any(attendu in faute for faute in fautes), (attendu, fautes)
    assert str(len(fautes)) in str(info.value)
