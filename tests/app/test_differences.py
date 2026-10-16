"""Story 13.1 : différences par mots (FR-17). Textes factices, générés par le code de test."""

from __future__ import annotations

import time

from slmsp.app.differences import LIMITE_PRODUIT, calculer, identiques
from slmsp.app.pont.redaction_outils import TAILLE_MAX, PontRedactionOutils


def _reconstruire(segments: list[dict], garder: set[str]) -> str:
    return "".join(s["texte"] for s in segments if s["type"] in garder)


def test_textes_identiques() -> None:
    segments = calculer("<mot-1> <mot-2>", "<mot-1> <mot-2>")
    assert identiques(segments)
    assert segments == [{"type": "egal", "texte": "<mot-1> <mot-2>"}]
    assert identiques(calculer("", ""))


def test_ajout_suppression_et_reconstruction() -> None:
    avant, apres = "<a> <b> <c> <d>", "<a> <x> <c> <d> <e>"
    segments = calculer(avant, apres)
    assert not identiques(segments)
    assert _reconstruire(segments, {"egal", "suppression"}) == avant
    assert _reconstruire(segments, {"egal", "ajout"}) == apres
    assert {"type": "suppression", "texte": "b"} in segments
    assert {"type": "ajout", "texte": "x"} in segments


def test_texte_vide_d_un_cote() -> None:
    assert calculer("", "<m>") == [{"type": "ajout", "texte": "<m>"}]
    assert calculer("<m>", "") == [{"type": "suppression", "texte": "<m>"}]


def test_unicode_equivalences_et_caracteres_speciaux() -> None:
    nfc, nfd = "café İstanbul", "café İstanbul"
    assert identiques(calculer(nfc, nfd))
    emoji = "<a> \U0001f600 ال <b>"
    segments = calculer(emoji, emoji + " <c>")
    assert _reconstruire(segments, {"egal", "ajout"}) == emoji + " <c>"
    assert _reconstruire(segments, {"egal", "suppression"}) == emoji


def test_retours_a_la_ligne_conserves() -> None:
    avant, apres = "<a>\n\n<b>", "<a>\n<b>"
    segments = calculer(avant, apres)
    assert _reconstruire(segments, {"egal", "suppression"}) == avant
    assert _reconstruire(segments, {"egal", "ajout"}) == apres


def test_texte_long_borne() -> None:
    n = 5_000
    avant = " ".join(f"<m{i}>" for i in range(n))
    apres = " ".join(f"<n{i}>" for i in range(n))  # aucun mot commun : pire cas
    assert (2 * n) * (2 * n) > LIMITE_PRODUIT
    debut = time.perf_counter()
    segments = calculer(avant, apres)
    assert time.perf_counter() - debut < 5
    assert _reconstruire(segments, {"egal", "suppression"}) == avant
    assert _reconstruire(segments, {"egal", "ajout"}) == apres


def test_texte_long_avec_petite_modification_reste_precis() -> None:
    mots = [f"<m{i}>" for i in range(20_000)]
    apres = [*mots[:10_000], "<ajout-factice>", *mots[10_000:]]
    segments = calculer(" ".join(mots), " ".join(apres))
    assert [s["type"] for s in segments] == ["egal", "ajout", "egal"]


def test_pont_differences() -> None:
    pont = PontRedactionOutils()
    r = pont.appeler("differences", "<a> <b>", "<a> <c>")
    assert r["ok"] is True
    assert r["identiques"] is False
    assert pont.appeler("differences", "<a>", "<a>")["identiques"] is True
    for args in [(1, "x"), ("x",), ("x", "y", "z"), ("x" * (TAILLE_MAX + 1), "y")]:
        assert pont.appeler("differences", *args)["erreur"]["code"] == "requete-invalide"
