"""Contrôle transversal du Jeu d'évaluation v1.0 (story 7.6). Aucun réseau.

Lit en lecture seule les brouillons `eval/construction/v1.0/` (8 Tâches), leurs verdicts et
le calibrage. Si le jeu est gelé (`eval/jeu/v1.0/MANIFEST.json`), contrôle aussi le manifeste,
`items.jsonl` et l'export JSONL de l'échantillon de revue.
"""

from __future__ import annotations

import importlib.util
import json
import re
import socket
import sys
from collections import Counter
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[2]
OUTIL = RACINE / "eval" / "outils" / "construire_jeu.py"
VERSION = "v1.0"
CONSTRUCTION = RACINE / "eval" / "construction" / VERSION
CALIBRAGE = RACINE / "eval" / "calibrage" / "echantillon-calibrage.jsonl"
JEU = RACINE / "eval" / "jeu" / VERSION
EXPORT_REVUE = RACINE / "eval" / "revue" / f"echantillon-revue-{VERSION}.jsonl"
PHRASE_EMPLACEMENTS = (
    "Laisse les informations non fournies en emplacement, avec exactement ces libellés : "
)
CHAMPS_SOURCES = ("provenance", "sources_attendues", "base_reglementaire")
RE_SOURCE = re.compile(r"\b(?:F[0-9]+|LEGIARTI[0-9]+)\b")
RE_ARTICLE = re.compile(r"\b([LRD])\.? ?([0-9]+(?:-[0-9]+)+)\b")


def _charger():
    spec = importlib.util.spec_from_file_location("construire_jeu_jeu_v1", OUTIL)
    module = importlib.util.module_from_spec(spec)
    sys.modules["construire_jeu_jeu_v1"] = module
    spec.loader.exec_module(module)
    return module


cj = _charger()
BROUILLONS, ERREURS_BROUILLONS = cj.lire_brouillons(CONSTRUCTION)
VERDICTS, ERREURS_VERDICTS = cj.derniers_verdicts(CONSTRUCTION)
RETENUS = sorted(
    (it for _, _, it in BROUILLONS if VERDICTS.get(it["id"], {}).get("verdict") != "rejete"),
    key=lambda it: cj.cle_id(it["id"]),
)
CT_RETENUS = [it for it in RETENUS if it["id"].startswith("CT-")]


@pytest.fixture(autouse=True)
def sans_reseau(monkeypatch):
    def interdit(*_a, **_k):
        raise AssertionError("connexion réseau interdite dans les tests")

    monkeypatch.setattr(socket.socket, "connect", interdit)
    monkeypatch.setattr(socket.socket, "connect_ex", interdit)
    monkeypatch.setattr(socket, "create_connection", interdit)
    monkeypatch.setattr(socket, "getaddrinfo", interdit)


# ---------------------------------------------------------------------------
# Identifiants, verdicts, composition
# ---------------------------------------------------------------------------
def test_identifiants_uniques_et_coherents():
    assert ERREURS_BROUILLONS == []
    assert cj.erreurs_identifiants(BROUILLONS) == []
    for code, n, it in BROUILLONS:
        attendues = {cj.TACHES[code]} | cj.ALIAS_TACHES.get(code, set())
        lieu = f"{code}.jsonl:{n} {it['id']}"
        assert it.get("tache") in attendues, f"{lieu} : tâche {it.get('tache')!r}"


def test_verdicts_complets():
    assert ERREURS_VERDICTS == []
    ids = {it["id"] for _, _, it in BROUILLONS}
    assert sorted(ids - set(VERDICTS), key=cj.cle_id) == [], "items sans verdict"
    assert sorted(set(VERDICTS) - ids, key=cj.cle_id) == [], "verdicts sans brouillon"
    non_acceptes = [it["id"] for it in RETENUS if VERDICTS[it["id"]]["verdict"] != "accepte"]
    assert non_acceptes == []


def test_composition_aux_cibles():
    assert len(RETENUS) == sum(sum(c) for c in cj.CIBLES.values()) == 225
    par_strate = Counter((it["id"].split("-")[0], it["difficulte"]) for it in RETENUS)
    for code, cibles in cj.CIBLES.items():
        reel = tuple(par_strate[(code, d)] for d in cj.DIFFICULTES)
        assert reel == cibles, f"{code} : {reel} au lieu de {cibles}"
    q = [it for it in RETENUS if it["id"].startswith("Q-")]
    assert sum(1 for it in q if it.get("sans_reponse") is True) == cj.CIBLE_Q_SANS_REPONSE
    assert sum(1 for it in q if cj.amorce_reelle(it)) >= cj.CIBLE_Q_PART_AMORCES * len(q)
    # Thèmes (Q, RD, LC, RE) : mêmes cibles que `composition` (42/21/21/21/21/14 sur 140).
    total_cible = sum(sum(cj.CIBLES[c]) for c in cj.CODES_THEMATIQUES)
    thematiques = [it for it in RETENUS if it["id"].split("-")[0] in cj.CODES_THEMATIQUES]
    assert len(thematiques) == total_cible == 140
    reel = Counter(it.get("theme") for it in thematiques)
    cibles = {t: round(part * total_cible) for t, part in cj.THEMES.items()}
    assert sorted(cibles.values()) == [14, 21, 21, 21, 21, 42]
    assert dict(reel) == cibles


# ---------------------------------------------------------------------------
# Courrier type : libellés exacts des emplacements dans la consigne
# ---------------------------------------------------------------------------
def test_ct_retenus():
    assert len(CT_RETENUS) == sum(cj.CIBLES["CT"])


@pytest.mark.parametrize("it", CT_RETENUS, ids=[it["id"] for it in CT_RETENUS])
def test_ct_aligne(it):
    consigne = it["entree"]["consigne"]
    libelles = it["champs_a_laisser_en_emplacement"]
    absents = [e for e in libelles if e not in consigne]
    assert absents == [], f"{it['id']} : libellés absents de la consigne : {absents}"
    phrase = PHRASE_EMPLACEMENTS + ", ".join(libelles) + "."
    assert consigne.endswith(" " + phrase), f"{it['id']} : phrase des libellés absente ou inexacte"


# ---------------------------------------------------------------------------
# Sources du calibrage
# ---------------------------------------------------------------------------
def _articles_cites(it: dict) -> set[str]:
    """Articles cités (« L. 112-3 » -> « L112-3 ») par les champs de source, hors texte recopié
    de la base (`texte`, `extrait`), qui peut mentionner d'autres articles sans les citer."""
    base = it.get("base_reglementaire")
    if isinstance(base, dict):
        base = {k: v for k, v in base.items() if k not in ("texte", "extrait")}
    champs = [it.get("provenance"), it.get("sources_attendues"), base]
    return {a + n for a, n in RE_ARTICLE.findall(json.dumps(champs, ensure_ascii=False))}


def _calibrage() -> list[dict]:
    lignes = CALIBRAGE.read_text(encoding="utf-8").splitlines()
    return [json.loads(ligne) for ligne in lignes if ligne.strip()]


def _sources_calibrage() -> set[str]:
    """Fiches F…, LEGIARTI… et articles cités par le calibrage."""
    sources = set(RE_SOURCE.findall(CALIBRAGE.read_text(encoding="utf-8")))
    for it in _calibrage():
        sources |= _articles_cites(it)
    return sources


def test_sources_calibrage_reperees():
    sources = _sources_calibrage()
    prefixes = {re.sub(r"[0-9]+$", "", s) for s in sources if not RE_ARTICLE.fullmatch(s)}
    assert prefixes == {"F", "LEGIARTI"}, prefixes
    assert {"L112-3", "R112-5", "L112-6"} <= sources, sources


@pytest.mark.parametrize("code", cj.CODES)
def test_aucune_source_du_calibrage(code):
    calibrage = _sources_calibrage()
    fautifs = []
    for it in RETENUS:
        if not it["id"].startswith(code + "-"):
            continue
        cites = json.dumps([it.get(c) for c in CHAMPS_SOURCES], ensure_ascii=False)
        communes = sorted((set(RE_SOURCE.findall(cites)) | _articles_cites(it)) & calibrage)
        fautifs += [f"{it['id']} cite {s}" for s in communes]
    assert fautifs == [], fautifs


# ---------------------------------------------------------------------------
# Jeu gelé (si le manifeste existe)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def manifeste():
    if not (JEU / "MANIFEST.json").is_file():
        pytest.skip(f"jeu {VERSION} non gelé : {JEU / 'MANIFEST.json'} absent")
    from slmsp.evaluation.gel import verifier_manifeste  # un échec d'import doit échouer

    return verifier_manifeste(VERSION, RACINE)


def _lignes(chemin: Path) -> list[str]:
    texte = chemin.read_bytes().decode("utf-8").replace("\r\n", "\n")
    return [ligne for ligne in texte.split("\n") if ligne.strip()]


def test_items_geles_egaux_aux_retenus(manifeste):
    geles = [json.loads(ligne) for ligne in _lignes(JEU / "items.jsonl")]
    assert [it["id"] for it in geles] == [it["id"] for it in RETENUS]
    assert geles == RETENUS
    assert manifeste.nb_items == len(RETENUS)


def test_export_revue_couvre_l_echantillon(manifeste):
    if not EXPORT_REVUE.is_file():
        pytest.skip(f"export de revue absent : {EXPORT_REVUE}")
    par_id = {json.loads(ligne)["id"]: ligne for ligne in _lignes(JEU / "items.jsonl")}
    lignes = _lignes(EXPORT_REVUE)
    assert [json.loads(ligne)["id"] for ligne in lignes] == manifeste.echantillons.relecture
    assert lignes == [par_id[i] for i in manifeste.echantillons.relecture]
    for nom in (f"echantillon-revue-{VERSION}.md", f"echantillon-revue-{VERSION}-lecture.md"):
        assert (EXPORT_REVUE.parent / nom).is_file(), f"export de revue absent : {nom}"
