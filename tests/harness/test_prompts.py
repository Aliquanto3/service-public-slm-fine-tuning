"""Construction unique des messages (story 4.1, AD-7).

Toutes les entrées et tous les passages sont des chaînes factices générées ici.
"""

from __future__ import annotations

import ast
import copy
import inspect
from pathlib import Path
from typing import Any

import pytest

from slmsp.core.canonique import json_canonique
from slmsp.core.items import RequeteTache, lire_items, vers_requete
from slmsp.core.messages import valider_conversation
from slmsp.core.ports import Passage
from slmsp.harness import prompts
from slmsp.harness.prompts import (
    AUCUN_PASSAGE,
    LIBELLES_CLES,
    ORDRE_CLES,
    EntreeInvalide,
    construire_messages,
    entree_de_requete,
    formater_passages,
)
from slmsp.harness.taches import EMPLACEMENTS, TableTaches, charger_taches
from slmsp.mcp.outils import charger_outils


@pytest.fixture(scope="module")
def table() -> TableTaches:
    return charger_taches()


def _passage(i: int, date: str | None = "<date-factice>") -> Passage:
    return Passage(
        chunk_id=f"<chunk-{i}>",
        doc_id=f"<doc-{i}>",
        source="<source-factice>",
        titre=f"<titre-factice-{i}>",
        url=f"https://factice.invalid/<url-{i}>",
        texte=f"<texte-factice-{i}>",
        date_snapshot=date,
        score=0.5,
    )


def _f(n: int) -> str:
    return f"<texte-factice-{n}>"


# --- Entrée texte -----------------------------------------------------------------------------


def test_question_avec_passages(table: TableTaches) -> None:
    q = table.tache("Q")
    messages = construire_messages(q, _f(0), [_passage(1), _passage(2)], None)
    valider_conversation(messages)
    assert messages[0] == {"role": "system", "content": q.prompt.consigne}
    assert messages[1] == {
        "role": "user",
        "content": (
            "Passages de l'Index local :\n"
            "[1] <titre-factice-1>\nURL : https://factice.invalid/<url-1>\n"
            "Date : <date-factice>\n<texte-factice-1>\n\n"
            "[2] <titre-factice-2>\nURL : https://factice.invalid/<url-2>\n"
            "Date : <date-factice>\n<texte-factice-2>\n\n"
            "Question :\n<texte-factice-0>"
        ),
    }


@pytest.mark.parametrize("passages", [None, []])
def test_question_sans_passage(table: TableTaches, passages: list[Passage] | None) -> None:
    messages = construire_messages(table.tache("Q"), _f(0), passages)
    assert messages[1]["content"] == (
        "Passages de l'Index local :\n"
        "Aucun passage pertinent n'a été trouvé dans l'Index local.\n\n"
        "Question :\n<texte-factice-0>"
    )


def test_recherche_de_donnees_avec_outils(table: TableTaches) -> None:
    rd = table.tache("RD")
    outils = charger_outils()
    messages = construire_messages(rd, _f(0), [_passage(1)], outils)
    valider_conversation(messages)
    contenu = messages[1]["content"]
    assert contenu.endswith("\n\nDemande :\n<texte-factice-0>")
    for outil in outils:
        assert outil["function"]["name"] not in contenu
        assert outil["function"]["name"] not in messages[0]["content"]
    assert construire_messages(rd, _f(0), None, ["search_datasets"]) == construire_messages(
        rd, _f(0)
    )


def test_non_regression_verbatim(table: TableTaches) -> None:
    entree = "  <texte-factice-1>\n\n<texte-factice-2>  "
    messages = construire_messages(table.tache("NR"), entree)
    assert messages[1] == {"role": "user", "content": entree}
    assert messages[0]["content"] == table.tache("NR").prompt.consigne


def test_formater_passages() -> None:
    assert formater_passages([]) == AUCUN_PASSAGE
    assert formater_passages(None) == AUCUN_PASSAGE
    bloc = formater_passages([_passage(1, None), _passage(2), _passage(3)])
    assert bloc.split("\n\n")[0] == (
        "[1] <titre-factice-1>\nURL : https://factice.invalid/<url-1>\n"
        "Date : non précisée\n<texte-factice-1>"
    )
    assert [ligne[:3] for ligne in bloc.split("\n\n")] == ["[1]", "[2]", "[3]"]


# --- Entrée objet -----------------------------------------------------------------------------


def test_entree_objet_ordre_fixe_et_nb_mots_ignore(table: TableTaches) -> None:
    entree = {"texte": _f(2), "nb_mots": 12, "consigne": _f(1)}
    messages = construire_messages(table.tache("LC"), entree)
    valider_conversation(messages)
    assert messages[1]["content"] == "Consigne :\n<texte-factice-1>\n\nTexte :\n<texte-factice-2>"
    assert construire_messages(table.tache("CO"), entree)[1] == messages[1]


def test_compte_rendu_notes_ou_transcription(table: TableTaches) -> None:
    cr = table.tache("CR")
    notes = construire_messages(cr, {"consigne": _f(1), "notes": _f(2), "nb_mots": 3})
    assert notes[1]["content"] == "Consigne :\n<texte-factice-1>\n\nNotes :\n<texte-factice-2>"
    transcription = construire_messages(cr, {"transcription": _f(3)})
    assert transcription[1]["content"] == "Transcription :\n<texte-factice-3>"


def test_courrier_type_valeurs_imbriquees(table: TableTaches) -> None:
    entree = {
        "elements_connus": {
            "zeta_cle": _f(3),
            "alpha_cle": [_f(4), _f(5)],
            "beta": True,
            "gamma": 7,
            "delta": {"sous_cle": False, "liste": [1.5, {"x_y": _f(6)}]},
        },
        "objet": _f(2),
        "type_courrier": _f(1),
        "consigne": _f(0),
    }
    messages = construire_messages(table.tache("CT"), entree)
    valider_conversation(messages)
    assert messages[1]["content"] == (
        "Consigne :\n<texte-factice-0>\n\n"
        "Type de courrier :\n<texte-factice-1>\n\n"
        "Objet :\n<texte-factice-2>\n\n"
        "Éléments connus :\n"
        "- alpha cle :\n  - <texte-factice-4>\n  - <texte-factice-5>\n"
        "- beta : oui\n"
        "- delta :\n  - liste :\n    - 1.5\n    -\n      - x y : <texte-factice-6>\n"
        "  - sous cle : non\n"
        "- gamma : 7\n"
        "- zeta cle : <texte-factice-3>"
    )


def test_resume_et_traduction(table: TableTaches) -> None:
    re_ = construire_messages(
        table.tache("RE"), {"document": _f(2), "longueur_demandee": _f(1), "consigne": _f(0)}
    )
    assert re_[1]["content"] == (
        "Consigne :\n<texte-factice-0>\n\nLongueur demandée :\n<texte-factice-1>\n\n"
        "Document :\n<texte-factice-2>"
    )
    tr = construire_messages(
        table.tache("TR"),
        {"texte": _f(3), "langue_cible": _f(2), "langue_source": _f(1), "consigne": _f(0)},
    )
    assert tr[1]["content"] == (
        "Consigne :\n<texte-factice-0>\n\nLangue source :\n<texte-factice-1>\n\n"
        "Langue cible :\n<texte-factice-2>\n\nTexte :\n<texte-factice-3>"
    )


def test_variantes_cr(table: TableTaches) -> None:
    cr = table.tache("CR")
    morceau = construire_messages(
        cr, {"consigne": _f(0), "partie": _f(1), "notes": _f(2)}, variante="morceau"
    )
    assert morceau[0]["content"] == cr.prompt_pour("morceau").consigne
    assert morceau[1]["content"] == (
        "Consigne :\n<texte-factice-0>\n\nPartie :\n<texte-factice-1>\n\nNotes :\n<texte-factice-2>"
    )
    fusion = construire_messages(cr, {"parties": [_f(1), _f(2)]}, variante="fusion")
    assert fusion[0]["content"] == cr.prompt_pour("fusion").consigne
    assert fusion[1]["content"] == "Parties :\n- <texte-factice-1>\n- <texte-factice-2>"
    with pytest.raises(EntreeInvalide, match="variante"):
        construire_messages(cr, {"notes": _f(1)}, variante="autre")
    with pytest.raises(EntreeInvalide, match="parties"):
        construire_messages(cr, {"parties": [_f(1)]})


# --- Erreurs ----------------------------------------------------------------------------------


def test_cle_inconnue_ou_non_declaree(table: TableTaches) -> None:
    with pytest.raises(EntreeInvalide, match="« autre » inconnue"):
        construire_messages(table.tache("LC"), {"autre": "x"})
    with pytest.raises(EntreeInvalide, match="« notes » non déclarée"):
        construire_messages(table.tache("LC"), {"notes": "x"})
    with pytest.raises(EntreeInvalide, match="« type » inconnue"):
        construire_messages(table.tache("CT"), {"type": "x"})


@pytest.mark.parametrize(
    ("code", "entree"),
    [("Q", {"question": "x"}), ("NR", {"demande": "x"}), ("CR", "x"), ("LC", "x"), ("TR", "x")],
)
def test_type_d_entree_inattendu(table: TableTaches, code: str, entree: Any) -> None:
    with pytest.raises(EntreeInvalide, match="attendue"):
        construire_messages(table.tache(code), entree)


def test_entree_objet_vide_ou_valeur_non_prise_en_charge(table: TableTaches) -> None:
    with pytest.raises(EntreeInvalide, match="sans aucune clé de contenu"):
        construire_messages(table.tache("LC"), {"nb_mots": 3})
    with pytest.raises(EntreeInvalide, match="sans aucune clé de contenu"):
        construire_messages(table.tache("LC"), {"consigne": _f(0)})
    with pytest.raises(EntreeInvalide, match="sans aucune clé de contenu"):
        construire_messages(table.tache("CT"), {"consigne": _f(0), "type_courrier": _f(1)})
    with pytest.raises(EntreeInvalide, match="NoneType"):
        construire_messages(table.tache("LC"), {"texte": None})


@pytest.mark.parametrize("code", ["Q", "RD", "NR"])
@pytest.mark.parametrize("entree", ["", "   ", "\n\t\n"])
def test_entree_texte_blanche(table: TableTaches, code: str, entree: str) -> None:
    with pytest.raises(EntreeInvalide, match="entrée texte vide"):
        construire_messages(table.tache(code), entree)


@pytest.mark.parametrize(
    ("code", "entree"),
    [
        ("LC", {"texte": ""}),
        ("LC", {"texte": "  \n "}),
        ("LC", {"texte": _f(1), "consigne": ""}),
        ("CT", {"objet": _f(1), "elements_connus": {}}),
        ("CT", {"objet": _f(1), "elements_connus": {"a": []}}),
        ("CT", {"objet": _f(1), "elements_connus": {"a": [_f(2), " "]}}),
        ("CT", {"objet": _f(1), "elements_connus": {"a": {"b": {}}}}),
        ("CR", {"notes": _f(1), "transcription": []}),
    ],
)
def test_valeur_vide_a_tout_niveau(table: TableTaches, code: str, entree: Any) -> None:
    with pytest.raises(EntreeInvalide, match="valeur vide"):
        construire_messages(table.tache(code), entree)


def test_texte_multiligne_imbrique(table: TableTaches) -> None:
    entree = {
        "objet": f"{_f(0)}\n{_f(1)}",
        "elements_connus": {
            "a": f"{_f(2)}\n{_f(3)}",
            "b": [f"{_f(4)}\n{_f(5)}\n\n{_f(6)}", {"c": f"{_f(7)}\n{_f(8)}"}],
        },
    }
    messages = construire_messages(table.tache("CT"), entree)
    assert messages[1]["content"] == (
        "Objet :\n<texte-factice-0>\n<texte-factice-1>\n\n"
        "Éléments connus :\n"
        "- a : <texte-factice-2>\n  <texte-factice-3>\n"
        "- b :\n"
        "  - <texte-factice-4>\n    <texte-factice-5>\n\n    <texte-factice-6>\n"
        "  -\n"
        "    - c : <texte-factice-7>\n      <texte-factice-8>"
    )


# --- Items réels du dépôt ---------------------------------------------------------------------

_RACINE = Path(__file__).resolve().parents[2]
_FICHIERS_ITEMS = [
    _RACINE / "eval" / "calibrage" / "echantillon-calibrage.jsonl",
    *sorted((_RACINE / "eval" / "construction" / "v1.0").glob("*.jsonl")),
]


@pytest.mark.parametrize("chemin", _FICHIERS_ITEMS, ids=lambda c: c.name)
def test_items_reels_passent_construire_messages(table: TableTaches, chemin: Path) -> None:
    if not chemin.is_file():
        pytest.skip(f"{chemin.name} absent")
    items = lire_items(chemin, strict=False)
    assert items
    for item in items:
        requete = vers_requete(item)
        messages = construire_messages(table.tache(requete.tache), entree_de_requete(requete))
        assert len(valider_conversation(messages)) == 2, item.id


def test_passages_sur_tache_sans_emplacement(table: TableTaches) -> None:
    with pytest.raises(EntreeInvalide, match="passages"):
        construire_messages(table.tache("LC"), {"texte": "x"}, [_passage(1)])
    with pytest.raises(EntreeInvalide, match="passages"):
        construire_messages(table.tache("NR"), "x", [_passage(1)])
    assert construire_messages(table.tache("LC"), {"texte": "x"}, [])


def test_outil_hors_outils_autorises(table: TableTaches) -> None:
    outil = charger_outils()[0]
    with pytest.raises(EntreeInvalide, match="non autorisé"):
        construire_messages(table.tache("CR"), {"notes": "x"}, None, [outil])
    with pytest.raises(EntreeInvalide, match="non autorisé"):
        construire_messages(table.tache("Q"), "x", None, ["search_datasets"])
    with pytest.raises(EntreeInvalide, match="mal formé"):
        construire_messages(table.tache("RD"), "x", None, [{"type": "function"}])
    assert construire_messages(table.tache("CR"), {"notes": "x"}, None, [])


# --- Pureté et contrat ------------------------------------------------------------------------


def test_purete_json_canonique(table: TableTaches) -> None:
    entree = {"consigne": _f(1), "elements_connus": {"b": [_f(2)], "a": _f(3)}, "objet": _f(4)}
    copie = copy.deepcopy(entree)
    premier = json_canonique(construire_messages(table.tache("CT"), entree))
    second = json_canonique(construire_messages(table.tache("CT"), copy.deepcopy(entree)))
    assert premier == second
    assert entree == copie
    passages = [_passage(1), _passage(2)]
    assert json_canonique(construire_messages(table.tache("Q"), _f(0), passages)) == json_canonique(
        construire_messages(table.tache("Q"), _f(0), list(passages))
    )


def test_construire_messages_ne_lit_aucun_fichier(
    table: TableTaches, monkeypatch: pytest.MonkeyPatch
) -> None:
    def interdit(*_: Any, **__: Any) -> Any:
        raise AssertionError("lecture de fichier interdite")

    monkeypatch.setattr("builtins.open", interdit)
    monkeypatch.setattr(Path, "read_text", interdit)
    monkeypatch.setattr(Path, "read_bytes", interdit)
    for code in ("Q", "RD", "NR"):
        construire_messages(table.tache(code), _f(0))
    construire_messages(table.tache("CT"), {"objet": _f(0)})


def test_toute_tache_produit_une_conversation_valide(table: TableTaches) -> None:
    for code in table.codes:
        tache = table.tache(code)
        for variante in (None, *tache.variantes):
            prompt = tache.prompt_pour(variante)
            if prompt.entree_texte:
                entree: Any = _f(0)
            else:
                entree = {nom: _f(i) for i, nom in enumerate(prompt.emplacements)}
            messages = construire_messages(tache, entree, variante=variante)
            assert len(valider_conversation(messages)) == 2
            assert messages[0]["role"] == "system" and messages[1]["role"] == "user"


def test_vocabulaire_coherent() -> None:
    assert set(ORDRE_CLES) | {"question", "demande", "passages"} == set(EMPLACEMENTS)
    assert set(LIBELLES_CLES) == set(EMPLACEMENTS) - {"passages"}
    assert len(set(ORDRE_CLES)) == len(ORDRE_CLES)


def test_regle_documentee_dans_le_module() -> None:
    doc = prompts.__doc__ or ""
    assert "Règle unique de rendu" in doc
    assert "nb_mots" in doc and "ORDRE_CLES" in doc and "formater_passages" in doc


def test_harness_n_importe_que_core_et_mcp() -> None:
    for module in (prompts, inspect.getmodule(charger_taches)):
        arbre = ast.parse(Path(inspect.getfile(module)).read_text(encoding="utf-8"))
        for noeud in ast.walk(arbre):
            if (
                isinstance(noeud, ast.ImportFrom)
                and noeud.module
                and noeud.module.startswith("slmsp")
            ):
                assert noeud.module.split(".")[1] in {"core", "mcp", "harness"}


# --- Requête de Tâche -------------------------------------------------------------------------


def test_entree_de_requete(table: TableTaches) -> None:
    requete = RequeteTache(
        tache="RE",
        entree={"consigne": _f(0), "document": _f(1), "nb_mots": 4},
        options={"parametres": {}, "longueur_demandee": _f(2)},
    )
    entree = entree_de_requete(requete)
    assert entree == {
        "consigne": _f(0),
        "document": _f(1),
        "nb_mots": 4,
        "longueur_demandee": _f(2),
    }
    assert "longueur_demandee" not in requete.entree
    assert (
        "Longueur demandée :\n<texte-factice-2>"
        in construire_messages(table.tache("RE"), entree)[1]["content"]
    )

    ct = RequeteTache(
        tache="CT", entree={"objet": _f(1)}, options={"parametres": {}, "type_courrier": _f(0)}
    )
    assert entree_de_requete(ct) == {"objet": _f(1), "type_courrier": _f(0)}
    deja = RequeteTache(
        tache="CT", entree={"type_courrier": _f(3)}, options={"type_courrier": _f(0)}
    )
    assert entree_de_requete(deja) == {"type_courrier": _f(3)}
    texte = RequeteTache(tache="Q", entree=_f(0), options={"parametres": {}})
    assert entree_de_requete(texte) == _f(0)
