"""Lecteur unique des items : modes souple et strict, cassettes, rendu (story 5.1, AD-11)."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from slmsp.core.erreurs import CodeSortie
from slmsp.core.items import (
    CODE_PAR_LIBELLE,
    CODES,
    LIBELLES,
    OUTILS_RD,
    ItemCO,
    ItemCT,
    ItemInvalide,
    ItemNR,
    ItemQ,
    ItemRD,
    ItemRE,
    RegleArgument,
    ReglesAppel,
    lire_items,
    lire_jeu,
    resoudre_cassettes,
    valider_item,
    vers_requete,
)
from slmsp.mcp.outils import OUTILS_AUTORISES

RACINE = Path(__file__).resolve().parents[2]
EVAL = RACINE / "eval"
PROVENANCE = [{"source": "<source-factice>", "consulte_le": "2026-10-12"}]


def item(code: str, numero: int = 1, **champs: Any) -> dict[str, Any]:
    """Item strict factice et valide de la Tâche `code`."""
    base: dict[str, Any] = {
        "id": f"{code}-{numero:03d}",
        "tache": LIBELLES[code],
        "difficulte": "facile",
        "theme": "social-autonomie" if code in ("Q", "RD", "LC", "RE") else "non-classe",
        "parametres": {},
        "provenance": copy.deepcopy(PROVENANCE),
        "licence_source": "<licence-factice>",
        "fictif": True,
        "version_item": 1,
    }
    propres: dict[str, dict[str, Any]] = {
        "Q": {
            "entree": "<entree-factice-q>",
            "reponse_reference": "<reponse-factice>",
            "elements_cles": ["<a>", "<b>", "<c>"],
            "sources_attendues": [],
            "sans_reponse": False,
        },
        "RD": {
            "entree": "<entree-factice-rd>",
            "appels_attendus": [
                {
                    "outil": "search_datasets",
                    "arguments": {"query": "<requete-factice>"},
                    "regles": {"arguments": {"query": {"contient_un_de": ["factice"]}}},
                }
            ],
            "cassettes": ["../../cassettes/RD-001/session.json"],
            "reponse_reference": "<reponse-factice>",
            "mode": "connecte",
        },
        "CR": {
            "entree": {"consigne": "<consigne>", "notes": "<notes-factices>"},
            "decisions_reference": ["<decision>"],
            "actions_reference": [
                {"action": "<action>", "responsable": "<qui>", "echeance": "<quand>"}
            ],
            "pieges": ["<piege>"],
        },
        "LC": {
            "entree": {"consigne": "<consigne>", "texte": "<texte-factice>"},
            "informations_a_conserver": ["<info>"],
            "termes_juridiques_a_conserver": ["<terme>"],
            "kandel_moles_entree": 42.0,
        },
        "CO": {
            "entree": {"consigne": "<consigne>", "texte": "un textte factice"},
            "fautes": [
                {
                    "debut": 3,
                    "fin": 9,
                    "erreur": "textte",
                    "correction": "texte",
                    "type": "orthographe",
                }
            ],
            "texte_corrige_reference": "un texte factice",
        },
        "RE": {
            "entree": {"consigne": "<consigne>", "document": "<document-factice>"},
            "points_cles_reference": ["<point>"],
            "longueur_demandee": "courte",
        },
        "CT": {
            "entree": {"consigne": "<consigne>", "objet": "<objet>"},
            "type_courrier": "<type-factice>",
            "elements_obligatoires": ["<element>"],
            "champs_a_laisser_en_emplacement": ["[Champ]"],
        },
        "NR": {
            "entree": "<entree-factice-nr>",
            "sous_type": "question",
            "reponse_reference": "<reponse-factice>",
        },
    }
    base.update(propres[code])
    base.update(champs)
    return base


def ecrire(chemin: Path, items: list[dict[str, Any]]) -> Path:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(
        "".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items), encoding="utf-8"
    )
    return chemin


def erreurs_strictes(tmp_path: Path, items: list[dict[str, Any]]) -> tuple[str, ...]:
    with pytest.raises(ItemInvalide) as exc:
        lire_items(ecrire(tmp_path / "items.jsonl", items), strict=True)
    return exc.value.erreurs


def _etat_eval() -> dict[str, str]:
    return {
        p.relative_to(EVAL).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(EVAL.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts
    }


# --- Tables ----------------------------------------------------------------------------------


def test_tables_des_codes() -> None:
    assert CODES == ("Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR")
    assert CODE_PAR_LIBELLE["Non-régression générale"] == "NR"
    assert all(CODE_PAR_LIBELLE[LIBELLES[code]] == code for code in CODES)


def test_outils_rd_identiques_a_mcp() -> None:
    assert OUTILS_RD == OUTILS_AUTORISES


@pytest.mark.parametrize("code", CODES)
def test_item_strict_valide_par_tache(code: str, tmp_path: Path) -> None:
    (lu,) = lire_items(ecrire(tmp_path / "i.jsonl", [item(code)]), strict=True)
    assert lu.code == code
    assert lu.id == f"{code}-001"


# --- Mode souple : calibrage réel ------------------------------------------------------------


def test_calibrage_lu_et_adapte_sans_rien_ecrire() -> None:
    avant = _etat_eval()
    jeu = lire_jeu("calibrage", RACINE)
    assert _etat_eval() == avant
    assert jeu.strict is False
    assert len(jeu.items) == 16
    ids = [i.id for i in jeu.items]
    assert {"RD-001", "RD-002", "RE-001", "RE-002"} <= set(ids)
    assert not any(i.startswith(("R-", "RS-")) for i in ids)
    assert all(i.version_item == 0 and i.theme == "non-classe" for i in jeu.items)
    assert all(i.parametres == {} for i in jeu.items)

    rd = jeu.item("RD-001")
    assert isinstance(rd, ItemRD)
    assert rd.cassettes == ["cassettes/R-001.json"]
    assert rd.mode == "connecte"
    assert rd.appels_attendus and rd.appels_attendus[0].regles is None

    q2 = jeu.item("Q-002")
    assert isinstance(q2, ItemQ) and q2.sans_reponse is True
    assert isinstance(jeu.item("Q-001"), ItemQ) and jeu.item("Q-001").sans_reponse is False

    re1 = jeu.item("RE-001")
    assert isinstance(re1, ItemRE) and re1.longueur_demandee
    assert isinstance(re1.entree, dict) and "longueur_demandee" not in re1.entree
    ct1 = jeu.item("CT-001")
    assert isinstance(ct1, ItemCT) and ct1.type_courrier == "demande de pièces"
    assert isinstance(ct1.entree, dict) and "type" not in ct1.entree

    # `fictif` déduit de la provenance : CR, CO, CT fictifs ; Q, RD, LC, RE réels.
    assert all(jeu.item(f"{c}-001").fictif for c in ("CR", "CO", "CT"))
    assert not any(jeu.item(f"{c}-001").fictif for c in ("Q", "RD", "LC", "RE"))


def test_calibrage_cassettes_resolues_sous_eval() -> None:
    jeu = lire_jeu("calibrage", RACINE)
    (chemin,) = resoudre_cassettes(jeu, jeu.item("RD-001"))
    assert chemin == (EVAL / "calibrage" / "cassettes" / "R-001.json").resolve()
    assert chemin.is_file()
    assert resoudre_cassettes(jeu, jeu.item("Q-001")) == []


def test_calibrage_refuse_en_strict() -> None:
    with pytest.raises(ItemInvalide):
        lire_items(EVAL / "calibrage" / "echantillon-calibrage.jsonl", strict=True)


def test_souple_ne_modifie_pas_l_objet_lu() -> None:
    brut = {
        **item("RD"),
        "id": "R-007",
        "cassette": "cassettes/x.json",
    }
    del brut["cassettes"], brut["mode"], brut["theme"], brut["version_item"]
    copie = copy.deepcopy(brut)
    lu = valider_item(brut, strict=False)
    assert brut == copie
    assert lu.id == "RD-007" and isinstance(lu, ItemRD)
    assert lu.cassettes == ["cassettes/x.json"] and lu.mode == "connecte"


@pytest.mark.parametrize(
    ("source", "fictif"),
    [
        ("Notes fictives rédigées pour l'évaluation", True),
        ("Avis aux usagers (texte fictif)", True),
        ("Demande d'agent rédigée pour l'évaluation (scénario)", True),
        ("Consigne rédigé pour l’évaluation", True),
        ("Fiche service-public F1344", False),
    ],
)
def test_souple_fictif_deduit(source: str, fictif: bool) -> None:
    brut = item("NR", provenance=[{"source": source, "consulte_le": "2026-10-12"}])
    del brut["fictif"]
    assert valider_item(brut, strict=False).fictif is fictif


# --- Mode strict -----------------------------------------------------------------------------


@pytest.mark.parametrize("champ", ["theme", "parametres", "fictif", "version_item"])
def test_strict_champ_commun_manquant(champ: str, tmp_path: Path) -> None:
    brut = item("Q", 3)
    del brut[champ]
    erreurs = erreurs_strictes(tmp_path, [brut])
    assert any(e.startswith(f"Q-003 : `{champ}` :") for e in erreurs), erreurs


def test_strict_message_cite_item_et_champ(tmp_path: Path) -> None:
    brut = item("Q", 3)
    del brut["theme"]
    with pytest.raises(ItemInvalide) as exc:
        lire_items(ecrire(tmp_path / "i.jsonl", [brut]), strict=True)
    assert "Q-003 : `theme` :" in str(exc.value)
    assert exc.value.code_sortie == CodeSortie.ERREUR


def test_strict_version_item_au_moins_1(tmp_path: Path) -> None:
    erreurs = erreurs_strictes(tmp_path, [item("Q", version_item=0)])
    assert any("`version_item`" in e for e in erreurs)


def test_strict_provenance_non_vide(tmp_path: Path) -> None:
    erreurs = erreurs_strictes(tmp_path, [item("NR", provenance=[])])
    assert any("`provenance`" in e for e in erreurs)


def test_strict_theme_spec_pour_les_taches_thematiques(tmp_path: Path) -> None:
    erreurs = erreurs_strictes(tmp_path, [item("LC", theme="non-classe")])
    assert any("LC-001 : `theme`" in e for e in erreurs)
    (cr,) = lire_items(ecrire(tmp_path / "cr.jsonl", [item("CR", theme="non-classe")]), strict=True)
    assert cr.theme == "non-classe"


def test_strict_rd_sans_regles(tmp_path: Path) -> None:
    brut = item("RD")
    del brut["appels_attendus"][0]["regles"]
    erreurs = erreurs_strictes(tmp_path, [brut])
    assert any(e.startswith("RD-001 : `appels_attendus.0.regles`") for e in erreurs), erreurs


@pytest.mark.parametrize("champ", ["mode", "cassettes", "appels_attendus"])
def test_strict_rd_champs_requis(champ: str, tmp_path: Path) -> None:
    brut = item("RD")
    del brut[champ]
    assert any(f"`{champ}`" in e for e in erreurs_strictes(tmp_path, [brut]))


def test_strict_rd_mode_inconnu(tmp_path: Path) -> None:
    assert any("`mode`" in e for e in erreurs_strictes(tmp_path, [item("RD", mode="local")]))


@pytest.mark.parametrize(
    ("code", "champ"),
    [
        ("Q", "reponse_reference"),
        ("Q", "elements_cles"),
        ("Q", "sources_attendues"),
        ("Q", "sans_reponse"),
        ("RD", "reponse_reference"),
        ("CR", "decisions_reference"),
        ("CR", "actions_reference"),
        ("CR", "pieges"),
        ("LC", "informations_a_conserver"),
        ("LC", "termes_juridiques_a_conserver"),
        ("LC", "kandel_moles_entree"),
        ("CO", "fautes"),
        ("CO", "texte_corrige_reference"),
        ("RE", "points_cles_reference"),
        ("RE", "longueur_demandee"),
        ("CT", "type_courrier"),
        ("CT", "elements_obligatoires"),
        ("CT", "champs_a_laisser_en_emplacement"),
    ],
)
def test_strict_champs_de_reference(code: str, champ: str, tmp_path: Path) -> None:
    brut = item(code)
    del brut[champ]
    erreurs = erreurs_strictes(tmp_path, [brut])
    assert any(e.startswith(f"{code}-001 : `{champ}`") for e in erreurs), erreurs
    # En souple, les champs de référence restent facultatifs.
    assert valider_item(brut, strict=False).id == f"{code}-001"


def test_strict_q_sans_reponse_exige_orientation(tmp_path: Path) -> None:
    erreurs = erreurs_strictes(tmp_path, [item("Q", sans_reponse=True)])
    assert any("`orientation_attendue`" in e for e in erreurs)
    ok = item("Q", sans_reponse=True, orientation_attendue="<orientation>")
    assert lire_items(ecrire(tmp_path / "ok.jsonl", [ok]), strict=True)


def test_strict_nr_reponse_ou_criteres(tmp_path: Path) -> None:
    brut = item("NR")
    del brut["reponse_reference"]
    assert any("NR-001" in e for e in erreurs_strictes(tmp_path, [brut]))
    brut["criteres"] = ["<critere>"]
    assert lire_items(ecrire(tmp_path / "ok.jsonl", [brut]), strict=True)


def test_strict_co_position_des_fautes(tmp_path: Path) -> None:
    brut = item("CO")
    brut["fautes"][0]["debut"] = 2
    erreurs = erreurs_strictes(tmp_path, [brut])
    assert any("CO-001 : `fautes.0`" in e for e in erreurs), erreurs


def test_cle_inconnue_refusee_en_strict_et_en_souple(tmp_path: Path) -> None:
    brut = {**item("RD"), "cassete": "x.json"}
    erreurs = erreurs_strictes(tmp_path, [brut])
    assert any("RD-001 : `cassete` : clé inconnue" in e for e in erreurs), erreurs
    with pytest.raises(ItemInvalide, match="cassete"):
        valider_item(brut, strict=False)


def test_cle_inconnue_imbriquee_refusee(tmp_path: Path) -> None:
    brut = item("RD")
    brut["appels_attendus"][0]["regles"]["inconnu"] = True
    assert any("appels_attendus.0.regles.inconnu" in e for e in erreurs_strictes(tmp_path, [brut]))


def test_cles_ouvertes_entree_et_provenance(tmp_path: Path) -> None:
    brut = item(
        "CR",
        entree={"consigne": "<c>", "transcription": "<t>", "nb_mots": 3, "autre": 1},
        provenance=[{"source": "<s>", "consulte_le": "2026-10-12T05:43:56+02:00", "x": [1]}],
    )
    assert lire_items(ecrire(tmp_path / "i.jsonl", [brut]), strict=True)


def test_provenance_date_iso_exigee(tmp_path: Path) -> None:
    brut = item("NR", provenance=[{"source": "<s>", "consulte_le": "12/10/2026"}])
    assert any("provenance.0.consulte_le" in e for e in erreurs_strictes(tmp_path, [brut]))
    brut = item("NR", provenance=[{"source": "<s>"}])
    assert any("provenance.0.consulte_le" in e for e in erreurs_strictes(tmp_path, [brut]))


def test_champs_declares_des_stories_7_2_et_7_4(tmp_path: Path) -> None:
    items = [
        item(
            "Q",
            amorce_usager="<amorce>",
            mention_obligatoire="<mention>",
            sans_reponse=True,
            orientation_attendue="<orientation>",
            verification_absence={"corpus": "<c>"},
        ),
        item("NR", 2, sous_type="consigne", criteres=["<c>"]),
        item("CR", type_reunion="<type>", participants_reference=["<p>"]),
        item("LC", version_texte=1),
        item("CO", nb_fautes=1, note_positions="<note>"),
        item("CT", valeurs_interdites=["<v>"], base_reglementaire={"article": "<a>"}),
        item("RD", criteres=["<c>"], valeurs_attendues=[1, 2], producteurs=["<p>"]),
    ]
    assert len(lire_items(ecrire(tmp_path / "i.jsonl", items), strict=True)) == len(items)


def test_nr_sous_type_ferme(tmp_path: Path) -> None:
    assert any("`sous_type`" in e for e in erreurs_strictes(tmp_path, [item("NR", sous_type="x")]))


def test_alias_non_regression_generale(tmp_path: Path) -> None:
    (lu,) = lire_items(
        ecrire(tmp_path / "i.jsonl", [item("NR", tache="Non-régression générale")]), strict=True
    )
    assert isinstance(lu, ItemNR) and lu.code == "NR"


def test_identifiant_et_tache_coherents(tmp_path: Path) -> None:
    erreurs = erreurs_strictes(
        tmp_path,
        [
            item("Q", id="NR-001"),
            item("RD", id="R-001"),
            item("Q", id="Q-1"),
            item("NR", tache="Inconnue"),
        ],
    )
    assert any("NR-001 : `id`" in e for e in erreurs)
    assert any("R-001 : `id`" in e for e in erreurs)
    assert any("Q-1 : `id`" in e for e in erreurs)
    assert any("`tache` : libellé inconnu" in e for e in erreurs)


def test_entree_typee_par_tache(tmp_path: Path) -> None:
    erreurs = erreurs_strictes(tmp_path, [item("Q", entree={"texte": "x"}), item("CR", entree="x")])
    assert any("Q-001 : `entree`" in e for e in erreurs)
    assert any("CR-001 : `entree`" in e for e in erreurs)


def test_toutes_les_erreurs_du_fichier_rassemblees(tmp_path: Path) -> None:
    sans_theme = item("Q", 1)
    del sans_theme["theme"]
    chemin = tmp_path / "i.jsonl"
    ecrire(chemin, [sans_theme, item("Q", 2, version_item=0), item("NR", 1)])
    with chemin.open("a", encoding="utf-8") as flux:
        flux.write("{pas du json\n")
    with pytest.raises(ItemInvalide) as exc:
        lire_items(chemin, strict=True)
    assert any(e.startswith("Q-001 :") for e in exc.value.erreurs)
    assert any(e.startswith("Q-002 :") for e in exc.value.erreurs)
    assert any(e.startswith("ligne 4 :") for e in exc.value.erreurs)
    assert not any(e.startswith("NR-001") for e in exc.value.erreurs)


def test_separateurs_unicode_dans_une_chaine(tmp_path: Path) -> None:
    texte = "<ligne-1> <ligne-2> <ligne-3>\x85<fin>\x0b\x0c"
    chemin = tmp_path / "i.jsonl"
    # ensure_ascii=False : les séparateurs Unicode sont écrits tels quels dans la ligne.
    lignes = [json.dumps(item("NR", entree=texte), ensure_ascii=False), json.dumps(item("Q"))]
    chemin.write_bytes(("\r\n".join(lignes) + "\r\n").encode("utf-8"))
    nr, q = lire_items(chemin, strict=True)
    assert nr.entree == texte and q.id == "Q-001"


@pytest.mark.parametrize(
    ("champ", "valeur"),
    [
        ("fictif", "yes"),
        ("fictif", 1),
        ("version_item", True),
        ("version_item", "2"),
        ("version_item", 1.0),
        ("sans_reponse", "false"),
        ("elements_cles", "<a>"),
    ],
)
def test_aucune_coercition(champ: str, valeur: Any, tmp_path: Path) -> None:
    erreurs = erreurs_strictes(tmp_path, [item("Q", **{champ: valeur})])
    assert any(e.startswith(f"Q-001 : `{champ}`") for e in erreurs), erreurs
    with pytest.raises(ItemInvalide):
        valider_item(item("Q", **{champ: valeur}), strict=False)


def test_aucune_coercition_des_positions(tmp_path: Path) -> None:
    brut = item("CO")
    brut["fautes"][0]["debut"] = "3"
    assert any("CO-001 : `fautes.0.debut`" in e for e in erreurs_strictes(tmp_path, [brut]))


@pytest.mark.parametrize(
    ("code", "champ", "valeur"),
    [
        ("Q", "reponse_reference", ""),
        ("Q", "reponse_reference", "   "),
        ("Q", "elements_cles", []),
        ("Q", "elements_cles", ["<a>", "<b>"]),
        ("Q", "elements_cles", ["<a>"] * 6),
        ("RD", "reponse_reference", ""),
        ("CO", "texte_corrige_reference", ""),
        ("CO", "fautes", []),
        ("RE", "points_cles_reference", []),
        ("RE", "longueur_demandee", ""),
        ("CT", "elements_obligatoires", []),
        ("CT", "type_courrier", ""),
        ("CR", "decisions_reference", []),
    ],
)
def test_strict_references_vides_refusees(
    code: str, champ: str, valeur: Any, tmp_path: Path
) -> None:
    erreurs = erreurs_strictes(tmp_path, [item(code, **{champ: valeur})])
    assert any(e.startswith(f"{code}-001 : `{champ}`") for e in erreurs), erreurs


def test_strict_listes_vides_permises(tmp_path: Path) -> None:
    items = [
        item("Q", sources_attendues=[]),
        item("RD", appels_attendus=[], cassettes=[]),
        item("CR", pieges=[]),
        item("NR", reponse_reference="", criteres=["<c>"]),
    ]
    assert len(lire_items(ecrire(tmp_path / "i.jsonl", items), strict=True)) == 4
    nr = item("NR", reponse_reference="")
    assert any("NR-001" in e for e in erreurs_strictes(tmp_path, [nr]))


@pytest.mark.parametrize("tache", [["Question"], {"a": 1}, 3, None])
@pytest.mark.parametrize("strict", [True, False])
def test_tache_non_textuelle(tache: Any, strict: bool) -> None:
    with pytest.raises(ItemInvalide, match="`tache` : libellé inconnu"):
        valider_item(item("Q", tache=tache), strict=strict)


def test_souple_longueur_demandee_remontee_pour_re_seulement() -> None:
    entree = {"consigne": "<c>", "texte": "<t>", "longueur_demandee": "courte"}
    lc = valider_item({**item("LC"), "entree": dict(entree)}, strict=False)
    assert isinstance(lc.entree, dict) and lc.entree["longueur_demandee"] == "courte"
    brut_re = item("RE", entree=dict(entree))
    del brut_re["longueur_demandee"]
    re_ = valider_item(brut_re, strict=False)
    assert isinstance(re_, ItemRE) and re_.longueur_demandee == "courte"


@pytest.mark.skipif(not (EVAL / "construction" / "v1.0").is_dir(), reason="brouillons v1.0 absents")
def test_brouillons_v1_0_reels_acceptes_en_strict() -> None:
    avant = _etat_eval()
    nombre = 0
    for chemin in sorted((EVAL / "construction" / "v1.0").glob("*.jsonl")):
        for ligne in chemin.read_text(encoding="utf-8").split("\n"):
            if ligne.strip():
                valider_item(json.loads(ligne), strict=True)
                nombre += 1
    assert nombre > 0
    assert _etat_eval() == avant


def test_identifiants_en_double(tmp_path: Path) -> None:
    erreurs = erreurs_strictes(tmp_path, [item("Q", 1), item("Q", 1)])
    assert any("identifiant en double" in e for e in erreurs)


# --- Règles des appels attendus ---------------------------------------------------------------


@pytest.mark.parametrize(
    "regle",
    [
        {"exact": "61556e1e9d6adb2df86eb0fc"},
        {"exact": None},
        {"contient_un_de": ["a", "b"]},
        {"optionnel": True},
        {"exact": 5, "optionnel": True},
        {"contient_un_de": ["a"], "optionnel": True},
        {"mot_entier_un_de": ["REI"]},
        {"contient_un_de": ["a"], "mot_entier_un_de": ["REI"], "optionnel": True},
    ],
)
def test_regle_argument_valide(regle: dict[str, Any]) -> None:
    RegleArgument.model_validate(regle)


@pytest.mark.parametrize(
    "regle",
    [
        {},
        {"optionnel": False},
        {"exact": 1, "contient_un_de": ["a"]},
        {"contient_un_de": []},
        {"mot_entier_un_de": []},
        {"exact": 1, "mot_entier_un_de": ["a"]},
        {"egal": 1},
    ],
)
def test_regle_argument_invalide(regle: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        RegleArgument.model_validate(regle)


def test_regle_argument_serialisation_sans_mot_entier() -> None:
    """Sans `mot_entier_un_de`, la forme sérialisée est celle d'avant la règle (v1.1)."""
    sans = RegleArgument.model_validate({"contient_un_de": ["a"]})
    assert sans.model_dump(mode="json") == {
        "exact": None,
        "contient_un_de": ["a"],
        "optionnel": False,
    }
    avec = RegleArgument.model_validate({"mot_entier_un_de": ["REI"]})
    assert avec.model_dump(mode="json")["mot_entier_un_de"] == ["REI"]


def test_regle_argument_relit_son_propre_dump() -> None:
    """`model_dump` écrit `exact: null` ; accolé à une liste, il ne compte pas comme `exact`."""
    for brut in ({"contient_un_de": ["a"]}, {"mot_entier_un_de": ["REI"]}, {"exact": 3}):
        regle = RegleArgument.model_validate(brut)
        relue = RegleArgument.model_validate(regle.model_dump())
        assert relue.a_exact is regle.a_exact
        assert relue.model_dump() == regle.model_dump()
    assert not RegleArgument.model_validate({"contient_un_de": ["a"], "exact": None}).a_exact
    assert RegleArgument.model_validate(
        {"exact": None}
    ).a_exact  # `exact: null` seul reste une règle
    with pytest.raises(ValueError, match="exclut"):
        RegleArgument.model_validate({"contient_un_de": ["a"], "exact": "x"})


EMPREINTE_DUMP_V1_0 = "80a820709e81f8efd217167b8083e4399b00f4e8c611a3a4d969e37d9ff9bd7a"
"""SHA-256 des `model_dump(mode="json")` canoniques des 225 items de `eval/jeu/v1.0`, calculé
avant l'ajout de `mot_entier_un_de` : la clé du cache des verdicts (`judge/cache.py`) en
dépend."""


def test_model_dump_v1_0_inchange() -> None:
    from slmsp.core.canonique import json_canonique

    jeu = lire_jeu("v1.0", RACINE)
    empreinte = hashlib.sha256()
    for it in jeu.items:
        empreinte.update(json_canonique(it.model_dump(mode="json")) + b"\n")
    assert len(jeu.items) == 225
    assert empreinte.hexdigest() == EMPREINTE_DUMP_V1_0


def test_regles_appel_defauts() -> None:
    regles = ReglesAppel.model_validate({})
    assert regles.optionnel is False and regles.ordre_libre is False and regles.arguments == {}


# --- Cassettes -------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "chemin", ["/abs/x.json", "C:/x.json", "..\\x.json", "", "a:b.json", "../x:flux.json"]
)
def test_cassettes_chemin_posix_relatif(chemin: str, tmp_path: Path) -> None:
    assert any(
        "`cassettes" in e for e in erreurs_strictes(tmp_path, [item("RD", cassettes=[chemin])])
    )


def test_resoudre_cassettes_sous_eval(tmp_path: Path) -> None:
    ecrire(
        tmp_path / "eval" / "jeu" / "v1.0" / "items.jsonl",
        [item("RD", 1), item("RD", 2, cassettes=["../../../hors.json"])],
    )
    jeu = lire_jeu("v1.0", tmp_path)
    (chemin,) = resoudre_cassettes(jeu, jeu.item("RD-001"))
    assert chemin == (tmp_path / "eval" / "cassettes" / "RD-001" / "session.json").resolve()
    with pytest.raises(ItemInvalide, match="RD-002"):
        resoudre_cassettes(jeu, jeu.item("RD-002"))


# --- lire_jeu --------------------------------------------------------------------------------


@pytest.mark.parametrize("version", ["1.0", "v1.0/../x", "", "V1"])
def test_lire_jeu_version_invalide(version: str, tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        lire_jeu(version, tmp_path)


def test_lire_jeu_strict(tmp_path: Path) -> None:
    ecrire(tmp_path / "eval" / "jeu" / "v1.0" / "items.jsonl", [item(c) for c in CODES])
    jeu = lire_jeu("v1.0", tmp_path)
    assert jeu.strict is True and len(jeu.items) == len(CODES)
    assert jeu.cle(jeu.items[0]) == "v1.0/Q-001"
    with pytest.raises(KeyError):
        jeu.item("Q-999")


def test_lire_jeu_fichier_vide(tmp_path: Path) -> None:
    """Un jeu sans item ne protégerait rien : refusé plutôt que lu comme vide."""
    chemin = tmp_path / "eval" / "jeu" / "v1.0" / "items.jsonl"
    chemin.parent.mkdir(parents=True)
    chemin.write_text("\n\n", encoding="utf-8")
    assert lire_items(chemin, strict=True) == []
    with pytest.raises(ItemInvalide, match="aucun item"):
        lire_jeu("v1.0", tmp_path)


def test_json_trop_profond_ou_entier_demesure_agrege(tmp_path: Path) -> None:
    chemin = tmp_path / "items.jsonl"
    chemin.write_text(
        "[" * 100_000 + "\n" + '{"id": ' + "9" * 5_000 + "}\n" + json.dumps(item("Q")) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ItemInvalide) as info:
        lire_items(chemin, strict=True)
    assert len(info.value.erreurs) == 2
    assert all("JSON illisible" in e and "ligne" in e for e in info.value.erreurs)


def test_lire_jeu_absent(tmp_path: Path) -> None:
    with pytest.raises(ItemInvalide, match="illisible"):
        lire_jeu("v9", tmp_path)


# --- vers_requete ----------------------------------------------------------------------------


def test_vers_requete_options_par_tache() -> None:
    rd = valider_item(item("RD", mode="repli", parametres={"p": [1]}), strict=True)
    requete = vers_requete(rd)
    assert requete.tache == "RD"
    assert requete.entree == "<entree-factice-rd>"
    assert requete.options == {"parametres": {"p": [1]}, "mode": "repli"}
    assert vers_requete(valider_item(item("RE"), strict=True)).options == {
        "parametres": {},
        "longueur_demandee": "courte",
    }
    assert vers_requete(valider_item(item("CT"), strict=True)).options == {
        "parametres": {},
        "type_courrier": "<type-factice>",
    }
    assert vers_requete(valider_item(item("Q"), strict=True)).options == {"parametres": {}}


def test_vers_requete_copie_profonde() -> None:
    co = valider_item(item("CO", parametres={"p": {"q": 1}}), strict=True)
    assert isinstance(co, ItemCO)
    requete = vers_requete(co)
    assert isinstance(requete.entree, dict)
    requete.entree["texte"] = "<modifie>"
    requete.options["parametres"]["p"]["q"] = 2
    assert isinstance(co.entree, dict) and co.entree["texte"] == "un textte factice"
    assert co.parametres == {"p": {"q": 1}}


def test_vers_requete_calibrage() -> None:
    jeu = lire_jeu("calibrage", RACINE)
    requetes = [vers_requete(i) for i in jeu.items]
    assert {r.tache for r in requetes} == set(CODES)
    assert vers_requete(jeu.item("CT-001")).options["type_courrier"] == "demande de pièces"
