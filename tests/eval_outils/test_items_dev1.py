"""Contrôles du jeu de développement dev1 (spec O4, story O4b ; revue).

Les contrôles des jeux v1.x (`test_items_*.py`) portent des constantes propres à v1.x
(identifiants, dates, composition, verbatim strict) : dev1 a ses propres contrôles ici.
Les textes réels de dev1 ont l'espacement et la ponctuation normalisés (README de
construction) : le verbatim est jugé après normalisation des blancs. Les contrôles contre les
sources lisent les instantanés parquet locaux (`SLMSP_EVAL_SOURCES`, sinon
`<racine>/data/raw/eval-sources`) et sont sautés sans eux.
"""

from __future__ import annotations

import difflib
import json
import os
import re
import unicodedata
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[2]
CONSTRUCTION = RACINE / "eval" / "construction" / "dev1"
CASSETTES = RACINE / "eval" / "cassettes"

pytestmark = pytest.mark.skipif(not CONSTRUCTION.is_dir(), reason="jeu dev1 absent")


def _items(code: str) -> list[dict]:
    chemin = CONSTRUCTION / f"{code}.jsonl"
    if not chemin.is_file():
        return []
    return [json.loads(x) for x in chemin.read_text(encoding="utf-8").splitlines() if x.strip()]


def _ids(items: list[dict]) -> list[str]:
    return [it["id"] for it in items]


def _blancs(texte: str) -> str:
    """Apostrophe droite, espaces fusionnées, sans espace avant la ponctuation."""
    texte = texte.replace("’", "'").replace("\xa0", " ").replace(" ", " ")
    texte = re.sub(r"\s+([.,;:!?)])", r"\1", texte)
    return re.sub(r"\s+", " ", texte).strip()


CO, LC, RD, RE, CT, Q = (_items(c) for c in ("CO", "LC", "RD", "RE", "CT", "Q"))


# --- Contrôles sans les sources --------------------------------------------------------------


@pytest.mark.parametrize("it", CO, ids=_ids(CO))
def test_co_fautes_appliquees_donnent_la_reference(it):
    """Les différences entre l'entrée et la référence sont exactement les fautes déclarées."""
    texte = it["entree"]["texte"]
    fautes = sorted(it["fautes"], key=lambda f: f["debut"])
    assert it["nb_fautes"] == len(fautes), it["id"]
    corrige = texte
    for f in reversed(fautes):
        assert texte[f["debut"] : f["fin"]] == f["erreur"], (it["id"], f)
        assert texte.count(f["contexte_fautif"]) == 1, (it["id"], f)
        corrige = corrige[: f["debut"]] + f["correction"] + corrige[f["fin"] :]
    for f1, f2 in zip(fautes, fautes[1:], strict=False):
        assert f1["fin"] <= f2["debut"], it["id"]
    assert corrige == it["texte_corrige_reference"], it["id"]


@pytest.mark.parametrize("it", LC, ids=_ids(LC))
def test_lc_termes_presents_dans_le_texte(it):
    """Chaque terme à conserver figure dans le texte (casse, accents et apostrophes près :
    les articles LEGI écrivent « Etat », « A titre »)."""

    def forme(x: str) -> str:
        decompose = unicodedata.normalize("NFD", _blancs(x).lower())
        return "".join(c for c in decompose if not unicodedata.combining(c))

    texte = forme(it["entree"]["texte"])
    absents = [t for t in it["termes_juridiques_a_conserver"] if forme(t) not in texte]
    assert absents == [], f"{it['id']} : termes absents de entree.texte : {absents}"


def test_rd_cassettes_501_a_520_toutes_citees():
    """Chaque dossier `RD-5xx` est cité par un item RD de dev1, et chaque cassette citée existe."""
    cites = set()
    for it in RD:
        for relatif in it["cassettes"]:
            chemin = (RACINE / "eval" / "jeu" / "dev1" / relatif).resolve()
            assert chemin.is_file(), (it["id"], relatif)
            cites.add(chemin)
    dossiers = {d.name for d in CASSETTES.glob("RD-*") if int(d.name.split("-")[1]) >= 501}
    assert dossiers == {it["id"] for it in RD} == {f"RD-{n}" for n in range(501, 521)}
    fichiers = {f.resolve() for d in dossiers for f in (CASSETTES / d).rglob("*") if f.is_file()}
    assert fichiers == cites


# --- Contrôles contre les instantanés des sources -------------------------------------------


@pytest.fixture(scope="module")
def sources():
    candidat = os.environ.get("SLMSP_EVAL_SOURCES")
    duckdb = pytest.importorskip("duckdb")
    dossier = Path(candidat) if candidat else RACINE / "data" / "raw" / "eval-sources"
    if not (dossier / "hf" / "AgentPublic").is_dir():
        if candidat:
            pytest.fail(f"SLMSP_EVAL_SOURCES ne contient pas hf/AgentPublic : {dossier}")
        pytest.skip("instantanés des sources absents (SLMSP_EVAL_SOURCES)")
    return duckdb.connect(), dossier / "hf" / "AgentPublic"


def _liste(parquets: list[Path]) -> str:
    assert parquets, "instantané parquet absent"
    return ", ".join("'" + p.resolve().as_posix().replace("'", "''") + "'" for p in parquets)


def _chunks(sources, doc_id: str, indices: list[int]) -> list[str]:
    connexion, dossier = sources
    liste = _liste(sorted((dossier / "service-public").rglob("*.parquet")))
    lignes = dict(
        connexion.execute(
            f"SELECT chunk_index, text FROM read_parquet([{liste}]) WHERE doc_id = ?", [doc_id]
        ).fetchall()
    )
    assert set(indices) <= set(lignes), (doc_id, indices)
    return [lignes[i] for i in indices]


def _doc(p: dict) -> str:
    return p.get("doc_id") or p["url"].rstrip("/").rsplit("/", 1)[-1]


EXTRAITS_Q = [
    (f"{it['id']}#{n}", p)
    for it in Q
    for n, p in enumerate(it["provenance"])
    if "chunks" in p and "extrait" in p
]


@pytest.mark.parametrize(("lieu", "p"), EXTRAITS_Q, ids=[x for x, _ in EXTRAITS_Q])
def test_q_extraits_dans_les_chunks(lieu, p, sources):
    textes = [_blancs(t) for t in _chunks(sources, _doc(p), p["chunks"])]
    segments = [s.strip() for s in p["extrait"].split(" […] ") if s.strip()]
    absents = [s for s in segments if not any(_blancs(s) in t for t in textes)]
    assert absents == [], f"{lieu} : segments absents des chunks cités : {absents}"


@pytest.mark.parametrize("it", RE, ids=_ids(RE))
def test_re_document_tire_des_chunks(it, sources):
    """Le document est la suite des chunks, sans ajout ni modification : seuls les
    recouvrements entre chunks et une fin de chunk incomplète peuvent être omis."""
    (p,) = it["provenance"]
    source = _blancs("\n".join(_chunks(sources, _doc(p), p["chunks"])))
    document = _blancs(it["entree"]["document"])
    ajouts = [
        document[i1:i2]
        for op, i1, i2, _, _ in difflib.SequenceMatcher(
            None, document, source, autojunk=False
        ).get_opcodes()
        if op in ("replace", "delete")
    ]
    assert ajouts == [], f"{it['id']} : texte absent de la source : {ajouts[:3]}"


CO_REELS = [it for it in CO if any(p.get("type") == "service-public" for p in it["provenance"])]


@pytest.mark.parametrize("it", CO_REELS, ids=_ids(CO_REELS))
def test_co_reel_reference_tiree_de_la_fiche(it, sources):
    """Référence = chunk de la fiche, à l'espacement près, aux coupures près et à quelques
    coquilles de la source corrigées (au plus 12 caractères ajoutés)."""
    (p,) = [p for p in it["provenance"] if p.get("type") == "service-public"]
    source = _blancs("\n".join(_chunks(sources, _doc(p), p["chunks"])))
    reference = _blancs(it["texte_corrige_reference"])
    ajoute = sum(
        i2 - i1
        for op, i1, i2, _, _ in difflib.SequenceMatcher(
            None, reference, source, autojunk=False
        ).get_opcodes()
        if op in ("replace", "delete")
    )
    assert ajoute <= 12, f"{it['id']} : {ajoute} caractères absents de la fiche"


CT_BASES = [it for it in CT if it.get("base_reglementaire")]


@pytest.mark.parametrize("it", CT_BASES, ids=_ids(CT_BASES))
def test_ct_articles_cites_verbatim(it, sources):
    connexion, dossier = sources
    articles = []
    for p in it["provenance"]:
        if p.get("type") != "legi":
            continue
        liste = _liste(sorted((dossier / "legi").rglob(f"{p['code']}/*.parquet")))
        lignes = connexion.execute(
            f"SELECT doc_id, text FROM read_parquet([{liste}]) "
            "WHERE status = 'VIGUEUR' AND list_contains(?, number)",
            [p["articles"]],
        ).fetchall()
        assert {r[0] for r in lignes} == {p["legiarti"]}, (it["id"], p["articles"])
        articles += [_blancs(r[1]) for r in lignes]
    assert articles, it["id"]
    texte = it["base_reglementaire"]["texte"]
    for segment in re.findall(r"«\s*(.*?)\s*»", texte, re.S) or [texte]:
        assert any(_blancs(segment) in a for a in articles), (it["id"], segment[:80])
    assert texte in it["entree"]["elements_connus"].get("texte_applicable", texte), it["id"]


REPLIS = [it for it in RD if it.get("mode") == "repli"]


@pytest.mark.parametrize("it", REPLIS, ids=_ids(REPLIS))
def test_rd_repli_reference_du_catalogue_local(it, sources):
    connexion, dossier = sources
    liste = _liste(sorted((dossier / "data-gouv-datasets-catalog").rglob("*.parquet")))
    jeu = it["reponse_reference"]["jeu_principal"]
    lignes = connexion.execute(
        f"SELECT chunk_id, title, organization, url FROM read_parquet([{liste}]) "
        "WHERE chunk_id = ?",
        [jeu["id"]],
    ).fetchall()
    assert (jeu["id"], jeu["titre"], jeu["producteur"], jeu["url"]) in lignes, it["id"]
    assert it["producteurs"] == [jeu["producteur"]], it["id"]
