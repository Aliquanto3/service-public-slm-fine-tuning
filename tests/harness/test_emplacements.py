"""Story 13.3 : emplacements d'un courrier type. Chaînes factices (D1)."""

from __future__ import annotations

from slmsp.app.pont.redaction_outils import PontRedactionOutils
from slmsp.harness.emplacements import (
    champ_rendu_par_une_valeur,
    detecter,
    libelles_presents,
    segmenter,
)


def test_segments_redonnent_le_texte() -> None:
    texte = "<a> [<champ-1>] <b>\n[<champ-2>]"
    segments = segmenter(texte)
    assert "".join(s["texte"] for s in segments) == texte
    assert detecter(texte) == ["[<champ-1>]", "[<champ-2>]"]


def test_pas_d_emplacement_vide_imbrique_ou_multiligne() -> None:
    assert detecter("[] [  ] [a [b]] [x\ny]") == ["[b]"]
    assert detecter("sans crochets") == []
    assert segmenter("") == []


def test_libelle_trop_long_n_est_pas_un_emplacement() -> None:
    assert detecter("[" + "x" * 121 + "]") == []


def test_libelles_presents_tels_quels() -> None:
    assert libelles_presents("<a> [<c1>]", ["[<c1>]", "[<c2>]"]) == {
        "[<c1>]": True,
        "[<c2>]": False,
    }


def test_champ_rendu_par_une_valeur() -> None:
    assert champ_rendu_par_une_valeur("Objet : <valeur>", "Objet")
    assert champ_rendu_par_une_valeur("**objet** : <valeur>", "Objet")
    assert champ_rendu_par_une_valeur("Objet : <valeur>", "objet")
    assert not champ_rendu_par_une_valeur("Objet : [<à compléter>]", "Objet")
    assert champ_rendu_par_une_valeur("Objet : valeur [<date>]", "Objet")
    assert champ_rendu_par_une_valeur("- Objet : valeur", "Objet")
    assert champ_rendu_par_une_valeur("* **Objet** : valeur", "Objet")
    assert not champ_rendu_par_une_valeur("- Objet : [<à compléter>]", "Objet")
    assert not champ_rendu_par_une_valeur("Objet :", "Objet")
    assert not champ_rendu_par_une_valeur("<aucune ligne>", "Objet")
    assert not champ_rendu_par_une_valeur("Référence : <valeur>", "Objet")


def test_pont_emplacements() -> None:
    pont = PontRedactionOutils()
    texte = "Objet : <valeur>\n[<champ>]"
    r = pont.appeler("emplacements", texte, ["objet", "elements_connus"])
    assert r["ok"] and r["champs_en_valeur"] == ["objet"]
    assert [s["type"] for s in r["segments"]] == ["texte", "emplacement"]
    assert pont.appeler("emplacements", texte, [])["champs_en_valeur"] == []
    for faux in (("x",), (1, []), ("x", "y"), ("x", [1])):
        r = pont.appeler("emplacements", *faux)
        assert r["ok"] is False and r["erreur"]["code"] == "requete-invalide"
