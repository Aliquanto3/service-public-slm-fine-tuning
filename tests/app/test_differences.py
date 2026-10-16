"""Story 13.1 : différences par mots (FR-17). Textes factices, générés par le code de test."""

from __future__ import annotations

import time
import unicodedata

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


def _texte_factice(n: int, *, ponctuation: bool) -> list[str]:
    return [
        f"m{(i * 7919) % 1500}" + ("." if ponctuation and i % 15 == 14 else "") for i in range(n)
    ]


def _verifier_corrections_isolees(n: int, k: int, *, ponctuation: bool) -> float:
    mots = _texte_factice(n, ponctuation=ponctuation)
    corrige = list(mots)
    positions = [(t * n) // k + 3 for t in range(k)]
    for t, p in enumerate(positions):
        corrige[p] = f"CORRIGE{t}"
    avant, apres = " ".join(mots), " ".join(corrige)
    debut = time.perf_counter()
    segments = calculer(avant, apres)
    duree = time.perf_counter() - debut
    ajouts = [s["texte"].strip() for s in segments if s["type"] == "ajout"]
    suppressions = [s["texte"].strip() for s in segments if s["type"] == "suppression"]
    assert ajouts == [f"CORRIGE{t}" for t in range(k)]  # une correction = un ajout isolé
    assert len(suppressions) == k
    assert all(len(s.split()) == 1 for s in suppressions)
    assert _reconstruire(segments, {"egal", "suppression"}) == avant
    assert _reconstruire(segments, {"egal", "ajout"}) == apres
    return duree


def test_corrections_dispersees_texte_long_isolees_et_rapides() -> None:
    for n in (3_000, 5_000):
        for ponctuation in (True, False):
            assert _verifier_corrections_isolees(n, 30, ponctuation=ponctuation) < 1.0


def test_latence_bornee_pire_cas_repetitif() -> None:
    avant = " ".join(("a", "b", "c", "d", "e")[(i * 3) % 5] for i in range(6_000))
    apres = " ".join(("a", "b", "c", "d", "e")[(i * 7 + i // 5) % 5] for i in range(6_000))
    debut = time.perf_counter()
    segments = calculer(avant, apres)
    assert time.perf_counter() - debut < 3
    assert _reconstruire(segments, {"egal", "suppression"}) == avant


def test_marques_combinantes_et_emoji_zwj_restent_colles() -> None:
    zwj = chr(0x200D)
    famille = zwj.join(chr(c) for c in (0x1F468, 0x1F469, 0x1F467))
    drapeau = chr(0x1F1EB) + chr(0x1F1F7)
    e_marques, o_marques = "e" + chr(0x301) + chr(0x302), "o" + chr(0x301) + chr(0x302)
    segments = calculer(f"<a> {famille} {drapeau} fin", f"<a> {famille} {drapeau} fin2")
    assert segments[0]["type"] == "egal" and segments[0]["texte"].endswith(drapeau)
    assert {"type": "suppression", "texte": " fin"} in segments  # mot entier remplacé
    # une lettre accentuée modifiée : elle part entière, marques comprises
    seg = calculer(f"<a> {e_marques} <b>", f"<a> {o_marques} <b>")
    nfc = [unicodedata.normalize("NFC", e_marques), unicodedata.normalize("NFC", o_marques)]
    assert {"type": "suppression", "texte": " " + nfc[0]} in seg
    assert {"type": "ajout", "texte": " " + nfc[1]} in seg


def test_espaces_insecables_et_multiples_ne_sont_pas_des_corrections() -> None:
    nbsp, fine = chr(0xA0), chr(0x202F)
    avant = f"<a>{nbsp}<b>  <c>{fine}!"
    assert identiques(calculer(avant, "<a> <b> <c> !"))
    segments = calculer(f"<a>{nbsp}<b>", "<a> <x>")
    assert segments[0]["texte"].startswith(f"<a>{nbsp}")  # affichage de `avant` conservé
    assert not identiques(
        calculer("<a>" + chr(10) + "<b>", "<a> <b>")
    )  # un retour à la ligne compte
