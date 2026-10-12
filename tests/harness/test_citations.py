"""`harness.citations` : URL, renvois `[n]` et sources citées (story 4.2, FR-5)."""

from __future__ import annotations

import dataclasses

import pytest
from harness_factices import mots, passage, url_factice

from slmsp.core.evenements import ResultatOutil, Source
from slmsp.harness.citations import (
    EXTRAIT_MAX,
    extraire_urls,
    extrait,
    normaliser_url,
    numeros_cites,
    sources_citees,
    urls_inventees,
)

URL_A = url_factice("a")
URL_B = url_factice("b")


def test_extraire_urls_ponctuation_et_doublons() -> None:
    texte = (
        f"({URL_A}). {mots(2, 'x')} « {URL_B} », [lien]({URL_A}) "
        f"www.{mots(1, 'w')}.example/p; <{URL_B}/q?x=1&y=2> https:// {URL_A}…"
    )
    assert extraire_urls(texte) == [
        URL_A,
        URL_B,
        f"www.{mots(1, 'w')}.example/p",
        f"{URL_B}/q?x=1&y=2",
    ]
    assert extraire_urls(mots(10, "rien")) == []


def test_normaliser_url() -> None:
    assert normaliser_url("HTTPS://WWW.Exemple.FR/a/b/") == "exemple.fr/a/b"
    assert normaliser_url("http://exemple.fr/a/b#section") == "exemple.fr/a/b"
    assert normaliser_url("www.exemple.fr/a%20b") == "exemple.fr/a b"
    assert normaliser_url("https://exemple.fr:443/a") == "exemple.fr/a"
    assert normaliser_url("https://exemple.fr:8080/a") == "exemple.fr:8080/a"
    assert normaliser_url("https://exemple.fr/a?x=1") != normaliser_url("https://exemple.fr/a")


def test_urls_inventees_sources_connues() -> None:
    p = passage(1, 0.9)
    dans_texte_passage = url_factice("dans-passage")
    p = p.__class__(**{**p.__dict__, "texte": f"{p.texte} {dans_texte_passage}"})
    outil = url_factice("outil")
    saisie = url_factice("saisie")
    inventee = url_factice("inventee")
    texte = (
        f"{p.url.replace('https://', 'http://')}/ {dans_texte_passage} {outil} {saisie} "
        f"{inventee} {inventee}/"
    )
    resultats = [ResultatOutil(id="a1", nom="search_datasets", resultat={"d": [{"u": outil}]})]
    assert urls_inventees(texte, [p], resultats, [f"{mots(3, 's')} {saisie}"]) == [inventee]
    assert urls_inventees(texte) == [
        p.url.replace("https://", "http://") + "/",
        dans_texte_passage,
        outil,
        saisie,
        inventee,
    ]


def test_urls_inventees_resultats_imbriques() -> None:
    resultats = [{"niveau": [{"plus": ("a", {URL_A: 1})}]}, f"texte {URL_B}", 42, None]
    assert urls_inventees(f"{URL_A} {URL_B}", resultats_outils=resultats) == []


@pytest.mark.parametrize(
    ("texte", "nb", "attendu"),
    [
        ("[1]", 3, [1]),
        ("a [3] b [1] c [3]", 3, [3, 1]),
        ("[1, 3]", 3, [1, 3]),
        ("[1; 2]", 3, [1, 2]),
        ("[2-4]", 5, [2, 3, 4]),
        ("[2–3]", 5, [2, 3]),
        ("[2-9]", 3, [2, 3]),
        ("[9]", 2, []),
        ("[0]", 2, []),
        ("[3-1]", 3, []),
        ("[a] [1a] [^1] [ 2 ]", 3, [2]),
        ("[2026]", 3, []),
        ("[1]", 0, []),
        ("[" + "9" * 5000 + "] [1]", 3, [1]),
        ("[1234567] [2, 1234567]", 3, []),
    ],
)
def test_numeros_cites(texte: str, nb: int, attendu: list[int]) -> None:
    assert numeros_cites(texte, nb) == attendu


def test_sources_citees() -> None:
    passages = [passage(1, 0.9), passage(2, 0.8), passage(3, 0.7)]
    sources = sources_citees("x [3] y [1] z [8]", passages)
    assert [s.numero for s in sources] == [3, 1]
    assert sources[0] == Source(
        numero=3,
        titre=passages[2].titre,
        url=passages[2].url,
        origine="index",
        date="2026-09-25",
        extrait=extrait(passages[2].texte),
    )
    assert sources_citees(mots(5, "rien"), passages) == []


def test_extrait() -> None:
    court = mots(3, "court")
    assert extrait(f"  {court}\n") == court
    long = mots(200, "long")
    coupe = extrait(long)
    assert len(coupe) <= EXTRAIT_MAX + 1 and coupe.endswith("…")
    assert long.startswith(coupe[:-1])
    assert not coupe[:-1].endswith(" ")


@pytest.mark.parametrize("url", ["https://Exemple.fr／a/", "https://[abc/x", "http://[::1/x"])
def test_normaliser_url_refusee_par_urlsplit(url: str) -> None:
    assert normaliser_url(url) == url.strip().lower().rstrip("/")
    p = dataclasses.replace(passage(1, 0.9), url=url)
    assert urls_inventees(f"{mots(3, 'x')} {URL_A}", [p]) == [URL_A]


def test_url_de_passage_a_parentheses_citee_telle_quelle() -> None:
    url = f"https://{mots(1, 'hote')}.example/page_({mots(1, 'p')})"
    p = dataclasses.replace(passage(1, 0.9), url=url)
    assert urls_inventees(f"{mots(3, 'voir')} {url} [1]", [p]) == []
