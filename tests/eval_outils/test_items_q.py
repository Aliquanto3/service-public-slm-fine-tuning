"""Verbatim des extraits de fiche des items Question (Q), jeux v1.0 et v1.1. Aucun réseau.

Chaque segment de `provenance[].extrait` (segments séparés par « […] ») doit figurer mot pour
mot dans le texte des `chunks` cités de la fiche, lu dans l'instantané parquet service-public
(`SLMSP_EVAL_SOURCES`, sinon `<racine>/data/raw/eval-sources`) avec duckdb. Comble le report de
la story 7.6 (extraits Q non confrontés au parquet) et couvre Q-042 et Q-068 à Q-070 (v1.1).
"""

from __future__ import annotations

import json
import os
import socket
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[2]
VERSIONS = tuple(v for v in ("v1.0", "v1.1") if (RACINE / "eval" / "construction" / v).is_dir())
SEPARATEUR = " […] "


def _extraits() -> list[tuple[str, str, dict]]:
    paires = []
    for version in VERSIONS:
        chemin = RACINE / "eval" / "construction" / version / "Q.jsonl"
        for ligne in chemin.read_text(encoding="utf-8").splitlines():
            if not ligne.strip():
                continue
            it = json.loads(ligne)
            for n, p in enumerate(it["provenance"]):
                if "chunks" in p and "extrait" in p:
                    paires.append((version, f"{it['id']}#{n}", p))
    return paires


EXTRAITS = _extraits()


@pytest.fixture(autouse=True)
def sans_reseau(monkeypatch):
    def interdit(*_a, **_k):
        raise AssertionError("connexion réseau interdite dans les tests")

    monkeypatch.setattr(socket.socket, "connect", interdit)
    monkeypatch.setattr(socket.socket, "connect_ex", interdit)
    monkeypatch.setattr(socket, "create_connection", interdit)
    monkeypatch.setattr(socket, "getaddrinfo", interdit)


@pytest.fixture(scope="module")
def chunks_par_fiche():
    candidat = os.environ.get("SLMSP_EVAL_SOURCES")
    if candidat:
        try:
            import duckdb
        except ImportError:
            pytest.fail("SLMSP_EVAL_SOURCES est défini mais duckdb est absent")
    else:
        duckdb = pytest.importorskip("duckdb")
    dossier = Path(candidat) if candidat else RACINE / "data" / "raw" / "eval-sources"
    parquets = sorted((dossier / "hf" / "AgentPublic" / "service-public").rglob("*.parquet"))
    if not parquets:
        if candidat:
            pytest.fail(f"SLMSP_EVAL_SOURCES ne contient pas le parquet service-public : {dossier}")
        pytest.skip("instantanés des sources absents (SLMSP_EVAL_SOURCES)")
    fiches = sorted({p["url"].rstrip("/").rsplit("/", 1)[-1] for _, _, p in EXTRAITS})
    liste = ", ".join("'" + c.resolve().as_posix().replace("'", "''") + "'" for c in parquets)
    lignes = (
        duckdb.connect()
        .execute(
            "SELECT doc_id, chunk_index, url, text, chunk_text "
            f"FROM read_parquet([{liste}]) WHERE list_contains(?, doc_id)",
            [fiches],
        )
        .fetchall()
    )
    par_fiche: dict[str, dict[int, tuple]] = {}
    for doc_id, index, url, text, chunk_text in lignes:
        par_fiche.setdefault(doc_id, {})[index] = (url, text or "", chunk_text or "")
    return par_fiche


def test_extraits_reperes():
    assert len({version for version, _, _ in EXTRAITS}) == len(VERSIONS)
    ids = {lieu.split("#")[0] for version, lieu, _ in EXTRAITS if version == "v1.1"}
    assert {"Q-042", "Q-068", "Q-069", "Q-070"} <= ids or "v1.1" not in VERSIONS


@pytest.mark.parametrize(
    ("version", "lieu", "p"), EXTRAITS, ids=[f"{v}-{lieu}" for v, lieu, _ in EXTRAITS]
)
def test_extrait_verbatim(version, lieu, p, chunks_par_fiche):
    doc = p["url"].rstrip("/").rsplit("/", 1)[-1]
    chunks = chunks_par_fiche.get(doc, {})
    assert set(p["chunks"]) <= set(chunks), f"{lieu} : chunks absents du parquet ({doc})"
    assert {chunks[c][0] for c in p["chunks"]} == {p["url"]}, f"{lieu} : URL différente"
    textes = [t for c in p["chunks"] for t in chunks[c][1:]]
    segments = [s.strip() for s in p["extrait"].split(SEPARATEUR) if s.strip()]
    assert segments, f"{lieu} : extrait sans segment non vide"
    absents = [s for s in segments if not any(s in t for t in textes)]
    assert absents == [], f"{lieu} : segments absents des chunks cités : {absents}"
