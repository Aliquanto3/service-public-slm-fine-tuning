"""Items Compte rendu (CR) et Langage clair (LC) du jeu v1.0 (story 7.4). Aucun appel réseau.

Les brouillons `eval/construction/v1.0/{CR,LC}.jsonl` et leurs verdicts sont lus tels quels.
Le contrôle du verbatim LC lit les instantanés parquet locaux (`SLMSP_EVAL_SOURCES`, sinon
`<racine>/data/raw/eval-sources`) avec duckdb ; il est ignoré si l'un ou l'autre manque.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import socket
import sys
from collections import Counter
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[2]
OUTIL = RACINE / "eval" / "outils" / "construire_jeu.py"
TEXTE = RACINE / "src" / "slmsp" / "core" / "texte.py"
CONSTRUCTION = RACINE / "eval" / "construction" / "v1.0"
CONSULTE_LE = "2026-10-12"
RE_SHA40 = re.compile(r"[0-9a-f]{40}")


def _charger(nom: str, chemin: Path):
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom] = module
    spec.loader.exec_module(module)
    return module


cj = _charger("construire_jeu_items_cr_lc", OUTIL)
tx = _charger("slmsp_core_texte_items_cr_lc", TEXTE)


def _items(code: str) -> list[dict]:
    chemin = CONSTRUCTION / f"{code}.jsonl"
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    return [json.loads(ligne) for ligne in lignes if ligne.strip()]


CR = _items("CR")
LC = _items("LC")


@pytest.fixture(autouse=True)
def sans_reseau(monkeypatch):
    def interdit(*_a, **_k):
        raise AssertionError("connexion réseau interdite dans les tests")

    monkeypatch.setattr(socket.socket, "connect", interdit)
    monkeypatch.setattr(socket.socket, "connect_ex", interdit)
    monkeypatch.setattr(socket, "create_connection", interdit)
    monkeypatch.setattr(socket, "getaddrinfo", interdit)


# ---------------------------------------------------------------------------
# Fichiers
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("code", ["CR", "LC"])
def test_fichier_jsonl_utf8_lf_un_item_par_ligne(code):
    # Le dépôt n'a pas de .gitattributes : avec core.autocrlf, la copie de travail peut être
    # en CRLF alors que le blob versionné est en LF. On normalise CRLF, et seulement lui.
    texte = (CONSTRUCTION / f"{code}.jsonl").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert "\r" not in texte, f"{code}.jsonl : retour chariot isolé"
    assert texte.endswith("\n")
    for n, ligne in enumerate(texte.split("\n")[:-1], 1):
        it = json.loads(ligne)
        assert ligne == json.dumps(it, ensure_ascii=False), f"{code}.jsonl:{n} non canonique"
    ids = [it["id"] for it in _items(code)]
    assert ids == [f"{code}-{i:03d}" for i in range(1, len(ids) + 1)], ids


# ---------------------------------------------------------------------------
# Structure CR
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("it", CR, ids=[it["id"] for it in CR])
def test_structure_cr(it):
    assert cj.anomalies_item("CR", it) == [], it["id"]
    assert it["tache"] == "Compte rendu"
    assert it["fictif"] is True
    assert it["version_item"] == 1
    entree = it["entree"]
    cles = set(entree) - {"consigne", "nb_mots"}
    assert len(cles) == 1 and cles <= {"notes", "transcription"}, (it["id"], set(entree))
    (cle,) = cles
    assert isinstance(entree["consigne"], str) and entree["consigne"].strip()
    assert entree["nb_mots"] == tx.compter_mots(entree[cle]), it["id"]
    assert it["participants_reference"], it["id"]
    assert it["decisions_reference"], it["id"]
    assert len(it["pieges"]) >= 3, it["id"]
    assert it["actions_reference"], it["id"]
    for i, action in enumerate(it["actions_reference"]):
        for champ in ("action", "responsable", "echeance"):
            valeur = action.get(champ)
            assert isinstance(valeur, str) and valeur.strip(), (it["id"], i, champ)
    for p in it["provenance"]:
        assert p["consulte_le"] == CONSULTE_LE, it["id"]


def test_composition_cr():
    assert Counter(it["difficulte"] for it in CR) == {"facile": 8, "moyen": 10, "difficile": 7}
    longues = [it["id"] for it in CR if cj._nb_mots(it["entree"]) > cj.SEUIL_CR_LONGUE_MOTS]
    assert len(longues) >= 5, longues
    for it in CR:
        if it["id"] in longues:
            assert "transcription" in it["entree"], it["id"]
            assert it["difficulte"] == "difficile", it["id"]
            assert it["entree"]["nb_mots"] > cj.SEUIL_CR_LONGUE_MOTS, it["id"]
    assert len({it["type_reunion"] for it in CR}) == len(CR), "types de réunion en double"


# ---------------------------------------------------------------------------
# Structure LC
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("it", LC, ids=[it["id"] for it in LC])
def test_structure_lc(it):
    assert cj.anomalies_item("LC", it) == [], it["id"]
    assert it["tache"] == "Langage clair"
    assert it["fictif"] is False
    assert it["version_item"] == 1
    entree = it["entree"]
    assert set(entree) == {"consigne", "texte", "nb_mots"}, it["id"]
    assert entree["nb_mots"] == tx.compter_mots(entree["texte"]), it["id"]
    assert it["informations_a_conserver"] and it["termes_juridiques_a_conserver"], it["id"]
    prov0 = it["provenance"][0]
    assert prov0["type"] in ("service-public", "legi"), it["id"]
    for p in it["provenance"]:
        assert p["consulte_le"] == CONSULTE_LE, it["id"]
        assert RE_SHA40.fullmatch(p.get("revision", "")), it["id"]
        assert p.get("url", "").startswith("https://"), it["id"]
        if p["type"] == "service-public":
            assert re.fullmatch(r"[A-Z]+[0-9]+", p["doc_id"]), it["id"]
            assert p["chunks"] and all(type(c) is int for c in p["chunks"]), it["id"]
        else:
            assert p["type"] == "legi", it["id"]
            assert p["code"].startswith("legi_") and p["articles"], it["id"]
            assert re.fullmatch(r"LEGIARTI[0-9]+", p.get("legiarti", "")), it["id"]
            assert p["url"].endswith(p["legiarti"]), it["id"]


@pytest.mark.parametrize("it", LC, ids=[it["id"] for it in LC])
def test_termes_juridiques_dans_le_texte(it):
    texte = it["entree"]["texte"].lower()
    absents = [t for t in it["termes_juridiques_a_conserver"] if t.lower() not in texte]
    assert absents == [], f"{it['id']} : termes absents de entree.texte : {absents}"


@pytest.mark.parametrize("it", LC, ids=[it["id"] for it in LC])
def test_kandel_moles_recalcule(it):
    assert it["version_texte"] == tx.VERSION_TEXTE, it["id"]
    recalcul = tx.kandel_moles(it["entree"]["texte"])
    assert abs(recalcul - it["kandel_moles_entree"]) <= 0.005, (it["id"], recalcul)


def test_composition_lc():
    assert Counter(it["difficulte"] for it in LC) == {"facile": 8, "moyen": 10, "difficile": 7}
    assert Counter(it["theme"] for it in LC) == {
        "social-autonomie": 7,
        "etat-civil-papiers": 4,
        "travail-emploi": 4,
        "collectivites": 4,
        "famille-education-sante": 4,
        "fiscalite-locale": 2,
    }
    sources = Counter(
        (p["type"], p.get("doc_id") or p.get("legiarti") or p["url"])
        for it in LC
        for p in it["provenance"]
    )
    assert [s for s, n in sources.items() if n > 1] == [], "une source différente par item"


def test_lc_hors_calibrage():
    """Ni la fiche F34440 ni les articles CRPA L112-3, R112-5 et L112-6 du calibrage."""
    for it in LC:
        for p in it["provenance"]:
            assert p.get("doc_id") != "F34440", it["id"]
            if "relations_entre_le_public" in p.get("code", ""):
                assert not {"L112-3", "R112-5", "L112-6"} & set(p["articles"]), it["id"]


# ---------------------------------------------------------------------------
# Verbatim LC (instantanés locaux)
# ---------------------------------------------------------------------------
def _dossier_sources() -> Path | None:
    candidat = os.environ.get("SLMSP_EVAL_SOURCES")
    dossier = Path(candidat) if candidat else RACINE / "data" / "raw" / "eval-sources"
    if (dossier / "hf" / "AgentPublic").is_dir():
        return dossier
    if candidat:
        pytest.fail(f"SLMSP_EVAL_SOURCES ne contient pas hf/AgentPublic : {dossier}")
    return None


def _sql_chemin(chemin: Path) -> str:
    return "'" + chemin.resolve().as_posix().replace("'", "''") + "'"


def _textes_source(duckdb, sources: Path, p: dict) -> list[str]:
    hf = sources / "hf" / "AgentPublic"
    if p["type"] == "service-public":
        parquets = sorted((hf / "service-public").rglob("*.parquet"))
        assert parquets, "parquet service-public absent des instantanés"
        liste = ", ".join(_sql_chemin(c) for c in parquets)
        lignes = duckdb.execute(
            "SELECT chunk_index, title, url, text, chunk_text, context "
            f"FROM read_parquet([{liste}]) WHERE doc_id = ?",
            [p["doc_id"]],
        ).fetchall()
        lignes = [r for r in lignes if r[0] in p["chunks"]]
        assert {r[0] for r in lignes} == set(p["chunks"]), p["source"]
        assert {r[2] for r in lignes} == {p["url"]}, p["source"]
        textes = []
        for _, titre, _, text, chunk_text, contexte in lignes:
            textes += [titre or "", text or "", chunk_text or "", *(contexte or [])]
        return textes
    parquets = sorted((hf / "legi").rglob(f"{p['code']}/*.parquet"))
    assert parquets, f"parquet LEGI absent des instantanés : {p['code']}"
    liste = ", ".join(_sql_chemin(c) for c in parquets)
    lignes = duckdb.execute(
        f"SELECT doc_id, number, text, chunk_text FROM read_parquet([{liste}]) "
        "WHERE status = 'VIGUEUR' AND list_contains(?, number)",
        [p["articles"]],
    ).fetchall()
    assert {r[1] for r in lignes} == set(p["articles"]), p["source"]
    if p.get("legiarti"):
        assert {r[0] for r in lignes} == {p["legiarti"]}, p["source"]
        assert p["url"].endswith(p["legiarti"]), p["source"]
    return [t for r in lignes for t in (r[2] or "", r[3] or "")]


@pytest.mark.parametrize("it", LC, ids=[it["id"] for it in LC])
def test_verbatim_lc(it):
    duckdb = pytest.importorskip("duckdb")
    sources = _dossier_sources()
    if sources is None:
        pytest.skip("instantanés des sources absents (SLMSP_EVAL_SOURCES)")
    connexion = duckdb.connect()
    textes = []
    for p in it["provenance"]:
        textes += _textes_source(connexion, sources, p)
    hors_source = [
        ligne.strip()
        for ligne in it["entree"]["texte"].split("\n")
        if ligne.strip() and not any(ligne.strip() in t for t in textes)
    ]
    assert hors_source == [], f"{it['id']} : lignes absentes des sources citées : {hors_source}"
    index = sources / "INDEX.json"
    if index.is_file():
        revisions = {
            f.get("depot"): f.get("revision")
            for f in json.loads(index.read_text(encoding="utf-8"))["fichiers"]
            if "/service-public/" in f.get("chemin", "") or "/legi/" in f.get("chemin", "")
        }
        for p in it["provenance"]:
            depot = "AgentPublic/" + ("service-public" if p["type"] == "service-public" else "legi")
            assert revisions.get(depot) == p["revision"], (it["id"], depot)


# ---------------------------------------------------------------------------
# Composition (outil) et verdicts de la double vérification
# ---------------------------------------------------------------------------
def test_commande_composition(capsys):
    assert cj.cmd_composition(RACINE, "v1.0") == 0
    sortie = capsys.readouterr().out
    assert "| CR (Compte rendu) | 25 / 25 (0) | 8 / 8 (0) | 10 / 10 (0) | 7 / 7 (0) |" in sortie
    assert "| LC (Langage clair) | 25 / 25 (0) | 8 / 8 (0) | 10 / 10 (0) | 7 / 7 (0) |" in sortie
    m = re.search(r"\| CR transcriptions > 4000 mots \| 5 \| ([0-9]+) \|", sortie)
    assert m and int(m.group(1)) >= 5, sortie
    anomalies = sortie.split("## Anomalies de structure", 1)[1]
    assert not re.search(r"\b(CR|LC)-[0-9]", anomalies), anomalies
    assert "CR.jsonl" not in anomalies and "LC.jsonl" not in anomalies, anomalies


@pytest.mark.parametrize("code", ["CR", "LC"])
def test_verdicts_acceptes(code):
    chemin = CONSTRUCTION / "verification" / f"{code}.jsonl"
    assert chemin.is_file(), f"verdicts absents : {chemin}"
    for n, ligne in enumerate(chemin.read_text(encoding="utf-8").splitlines(), 1):
        if not ligne.strip():
            continue
        v = json.loads(ligne)
        assert v["verdict"] in cj.VERDICTS, (code, n)
        assert cj.RE_DATE_ISO.fullmatch(v["verifie_le"]), (code, n)
        if v["verdict"] == "rejete":
            assert v.get("motif") in cj.MOTIFS, (code, n)
    verdicts, erreurs = cj.derniers_verdicts(CONSTRUCTION)
    assert [e for e in erreurs if e.startswith(f"{code}.jsonl")] == []
    items = CR if code == "CR" else LC
    non_acceptes = [
        it["id"] for it in items if verdicts.get(it["id"], {}).get("verdict") != "accepte"
    ]
    assert non_acceptes == [], f"{code} non vérifiés ou rejetés : {non_acceptes}"
