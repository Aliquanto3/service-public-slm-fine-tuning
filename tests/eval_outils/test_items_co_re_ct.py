"""Items Correction (CO), Résumé (RE) et Courrier type (CT) des jeux v1.0 et v1.1 (story 7.5).

Aucun réseau. Les brouillons `eval/construction/<version>/{CO,RE,CT}.jsonl` et leurs verdicts
sont lus tels quels. Un CO « réel » est un texte de fiche service-public (provenance de type
`service-public`) où des fautes ont été injectées : `fictif: false` en v1.0, `fictif: true`
depuis v1.1 (arbitrage G4), d'où une sélection par la provenance et non par `fictif`.
Les contrôles de verbatim lisent les instantanés parquet locaux (`SLMSP_EVAL_SOURCES`, sinon
`<racine>/data/raw/eval-sources`) avec duckdb ; ils sont ignorés si l'un ou l'autre manque.
Le contrôle par le lecteur strict (`slmsp.core.items`) est ignoré hors de l'environnement du
projet (lancement `--no-project`).
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
VERSIONS = tuple(v for v in ("v1.0", "v1.1") if (RACINE / "eval" / "construction" / v).is_dir())
CALIBRAGE = RACINE / "eval" / "calibrage" / "echantillon-calibrage.jsonl"
CONSULTE_LE = "2026-10-12"
RE_SHA40 = re.compile(r"[0-9a-f]{40}")
CODES = ("CO", "RE", "CT")
REPARTITION = {"facile": 5, "moyen": 5, "difficile": 5}


def _charger(nom: str, chemin: Path):
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules[nom] = module
    spec.loader.exec_module(module)
    return module


cj = _charger("construire_jeu_items_co_re_ct", OUTIL)
tx = _charger("slmsp_core_texte_items_co_re_ct", TEXTE)


def _construction(version: str) -> Path:
    return RACINE / "eval" / "construction" / version


def _items(version: str, code: str) -> list[dict]:
    chemin = _construction(version) / f"{code}.jsonl"
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    return [json.loads(ligne) for ligne in lignes if ligne.strip()]


PAR_VERSION = {(v, c): _items(v, c) for v in VERSIONS for c in CODES}
CO = [(v, it) for v in VERSIONS for it in PAR_VERSION[(v, "CO")]]
RE = [(v, it) for v in VERSIONS for it in PAR_VERSION[(v, "RE")]]
CT = [(v, it) for v in VERSIONS for it in PAR_VERSION[(v, "CT")]]


def co_reel(it: dict) -> bool:
    """CO tiré d'une fiche réelle (fautes injectées), quel que soit `fictif`."""
    return any(p.get("type") == "service-public" for p in it["provenance"])


def _fictif_co_reel(version: str) -> bool:
    return version != "v1.0"  # arbitrage G4 : textes réels modifiés, donc fictifs


@pytest.fixture(autouse=True)
def sans_reseau(monkeypatch):
    def interdit(*_a, **_k):
        raise AssertionError("connexion réseau interdite dans les tests")

    monkeypatch.setattr(socket.socket, "connect", interdit)
    monkeypatch.setattr(socket.socket, "connect_ex", interdit)
    monkeypatch.setattr(socket, "create_connection", interdit)
    monkeypatch.setattr(socket, "getaddrinfo", interdit)


def _ids(paires: list[tuple[str, dict]]) -> list[str]:
    return [f"{v}-{it['id']}" for v, it in paires]


def _retenus(version: str, items: list[dict]) -> list[dict]:
    """Items dont le dernier verdict n'est pas `rejete` (un remplacé reste dans le brouillon)."""
    verdicts, _ = cj.derniers_verdicts(_construction(version))
    return [it for it in items if verdicts.get(it["id"], {}).get("verdict") != "rejete"]


# ---------------------------------------------------------------------------
# Fichiers
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("code", CODES)
def test_fichier_jsonl_utf8_lf_un_item_par_ligne(version, code):
    # Avec core.autocrlf, la copie de travail peut être en CRLF : on normalise CRLF seulement.
    chemin = _construction(version) / f"{code}.jsonl"
    texte = chemin.read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert "\r" not in texte, f"{code}.jsonl : retour chariot isolé"
    assert texte.endswith("\n")
    for n, ligne in enumerate(texte.split("\n")[:-1], 1):
        it = json.loads(ligne)
        assert ligne == json.dumps(it, ensure_ascii=False), f"{code}.jsonl:{n} non canonique"
    ids = [it["id"] for it in PAR_VERSION[(version, code)]]
    assert ids == [f"{code}-{i:03d}" for i in range(1, len(ids) + 1)], ids


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("code", CODES)
def test_champs_communs(version, code):
    for it in PAR_VERSION[(version, code)]:
        assert cj.anomalies_item(code, it) == [], it["id"]
        attendus = (1,) if version == "v1.0" else (1, 2)
        assert it["version_item"] in attendus and it["parametres"] == {}, it["id"]
        assert it["theme"] in cj.THEMES, it["id"]
        assert it["provenance"], it["id"]
        for p in it["provenance"]:
            assert p["consulte_le"] == CONSULTE_LE, it["id"]
        assert isinstance(it["licence_source"], str) and it["licence_source"].strip(), it["id"]


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("code", CODES)
def test_composition_par_difficulte(version, code):
    items = _retenus(version, PAR_VERSION[(version, code)])
    assert len(items) == 15
    assert Counter(it["difficulte"] for it in items) == REPARTITION


def _provenance_service_public(it: dict, p: dict) -> None:
    assert p["type"] == "service-public", it["id"]
    assert re.fullmatch(r"F[0-9]+", p["doc_id"]), it["id"]
    assert p["chunks"] and all(type(c) is int for c in p["chunks"]), it["id"]
    assert p["url"].startswith("https://") and p["url"].endswith("/" + p["doc_id"]), it["id"]
    assert p["depot"] == "AgentPublic/service-public", it["id"]
    assert RE_SHA40.fullmatch(p["revision"]), it["id"]


# ---------------------------------------------------------------------------
# Correction (CO)
# ---------------------------------------------------------------------------
FAUTES_PAR_DIFFICULTE = {"facile": (5, 7), "moyen": (7, 10), "difficile": (10, 14)}


@pytest.mark.parametrize(("version", "it"), CO, ids=_ids(CO))
def test_positions_co(version, it):
    entree = it["entree"]
    assert set(entree) == {"consigne", "texte", "nb_mots"}, it["id"]
    texte = entree["texte"]
    assert entree["nb_mots"] == tx.compter_mots(texte), it["id"]
    fautes = it["fautes"]
    assert it["nb_fautes"] == len(fautes), it["id"]
    mini, maxi = FAUTES_PAR_DIFFICULTE[it["difficulte"]]
    assert mini <= len(fautes) <= maxi, (it["id"], len(fautes))
    for i, f in enumerate(fautes):
        assert set(f) == {"debut", "fin", "erreur", "correction", "type", "contexte_fautif"}
        assert texte[f["debut"] : f["fin"]] == f["erreur"], f"{it['id']} : fautes[{i}]"
        assert f["erreur"] != f["correction"], f"{it['id']} : fautes[{i}]"
        contexte = f["contexte_fautif"]
        assert f["erreur"] in contexte, f"{it['id']} : fautes[{i}]"
        assert texte.count(contexte) == 1, f"{it['id']} : fautes[{i}] contexte non unique"
        position = texte.index(contexte)
        assert position <= f["debut"] and f["fin"] <= position + len(contexte), (
            f"{it['id']} : fautes[{i}] contexte qui n'englobe pas [debut, fin)"
        )
    tries = sorted(fautes, key=lambda f: f["debut"])
    for f1, f2 in zip(tries, tries[1:], strict=False):
        assert f1["fin"] <= f2["debut"], f"{it['id']} : fautes qui se chevauchent"
    corrige = texte
    for f in reversed(tries):
        corrige = corrige[: f["debut"]] + f["correction"] + corrige[f["fin"] :]
    assert corrige == it["texte_corrige_reference"], f"{it['id']} : correction ≠ référence"
    assert it["note_positions"], it["id"]


@pytest.mark.parametrize("version", VERSIONS)
def test_composition_co(version):
    items = PAR_VERSION[(version, "CO")]
    reels = [it for it in items if co_reel(it)]
    assert len(reels) >= 5, [it["id"] for it in reels]
    for it in reels:
        (p,) = it["provenance"]
        _provenance_service_public(it, p)
        assert len(p["chunks"]) == 1, it["id"]
        assert it["fictif"] is _fictif_co_reel(version), it["id"]
    for it in items:
        if not co_reel(it):
            assert it["fictif"] is True, it["id"]
            assert all("fictif" in p["source"] for p in it["provenance"]), it["id"]
    sources = [it["provenance"][0]["doc_id"] for it in reels]
    assert len(sources) == len(set(sources)), "une fiche différente par item CO réel"


# ---------------------------------------------------------------------------
# Résumé (RE)
# ---------------------------------------------------------------------------
LIMITES_RE = {"courte": "80 mots", "moyenne": "200 mots", "detaillee": "400 mots"}
MOTS_POINTS_CLES = {"courte": 60, "moyenne": 170, "detaillee": 400}
"""Total des points clés bout à bout : un résumé conforme à la longueur peut tous les couvrir."""
MOTS_DOCUMENT = {"facile": (250, 650), "moyen": (500, 1000), "difficile": (900, 1700)}


@pytest.mark.parametrize(("version", "it"), RE, ids=_ids(RE))
def test_structure_re(version, it):
    assert it["fictif"] is False
    entree = it["entree"]
    assert set(entree) == {"consigne", "document", "nb_mots"}, it["id"]
    assert entree["nb_mots"] == tx.compter_mots(entree["document"]), it["id"]
    mini, maxi = MOTS_DOCUMENT[it["difficulte"]]
    assert mini <= entree["nb_mots"] <= maxi, (it["id"], entree["nb_mots"])
    assert it["longueur_demandee"] in cj.LONGUEURS_RE, it["id"]
    assert LIMITES_RE[it["longueur_demandee"]] in entree["consigne"], it["id"]
    points = it["points_cles_reference"]
    assert 3 <= len(points) <= 9, it["id"]
    assert all(isinstance(p, str) and p.strip() for p in points), it["id"]
    total = sum(tx.compter_mots(point) for point in points)
    assert total <= MOTS_POINTS_CLES[it["longueur_demandee"]], (it["id"], total)
    (p,) = it["provenance"]
    _provenance_service_public(it, p)


def _fiches_citees(*chemins: Path) -> set[str]:
    textes = " ".join(c.read_text(encoding="utf-8") for c in chemins)
    return set(re.findall(r"\bF[0-9]+\b", textes))


@pytest.mark.parametrize("version", VERSIONS)
def test_composition_re(version):
    RE = PAR_VERSION[(version, "RE")]
    assert Counter(it["longueur_demandee"] for it in RE) == {
        "courte": 5,
        "moyenne": 5,
        "detaillee": 5,
    }
    assert Counter(it["theme"] for it in RE) == {
        "social-autonomie": 5,
        "etat-civil-papiers": 2,
        "travail-emploi": 2,
        "collectivites": 2,
        "famille-education-sante": 2,
        "fiscalite-locale": 2,
    }
    fiches = [it["provenance"][0]["doc_id"] for it in RE]
    assert len(fiches) == len(set(fiches)), "une fiche différente par item RE"
    construction = _construction(version)
    deja = _fiches_citees(construction / "Q.jsonl", construction / "LC.jsonl", CALIBRAGE)
    assert set(fiches) & deja == set(), "fiches déjà citées par Q, LC ou le calibrage"


def test_sources_hors_calibrage():
    calibrage = _fiches_citees(CALIBRAGE)
    for _, it in CO + RE + CT:
        for p in it["provenance"]:
            assert p.get("doc_id") not in calibrage, it["id"]
    objets_calibrage = {
        json.loads(ligne)["entree"]["objet"]
        for ligne in CALIBRAGE.read_text(encoding="utf-8").splitlines()
        if ligne.strip() and json.loads(ligne)["tache"] == "Courrier type"
    }
    assert objets_calibrage, "scénarios CT du calibrage introuvables"
    assert {it["entree"]["objet"] for _, it in CT}.isdisjoint(objets_calibrage)
    articles_calibrage = set(re.findall(r"LEGIARTI[0-9]+", CALIBRAGE.read_text(encoding="utf-8")))
    assert articles_calibrage, "articles LEGI du calibrage introuvables"
    for _, it in CT:
        cites = {p.get("legiarti") for p in it["provenance"]}
        cites.add((it.get("base_reglementaire") or {}).get("legiarti"))
        assert cites.isdisjoint(articles_calibrage), it["id"]


# ---------------------------------------------------------------------------
# Courrier type (CT)
# ---------------------------------------------------------------------------
TYPES_CT = {
    "accusé de réception": 4,
    "demande de pièces": 4,
    "convocation": 4,
    "réponse d'information": 3,
}


def _valeurs(connus: dict) -> list[str]:
    valeurs: list[str] = []
    for v in connus.values():
        valeurs += v if isinstance(v, list) else [v]
    return valeurs


@pytest.mark.parametrize(("version", "it"), CT, ids=_ids(CT))
def test_structure_ct(version, it):
    assert it["fictif"] is True
    entree = it["entree"]
    assert set(entree) == {"type", "objet", "elements_connus", "consigne"}, it["id"]
    assert it["type_courrier"] == entree["type"], it["id"]
    assert it["type_courrier"] in TYPES_CT, it["id"]
    assert isinstance(entree["elements_connus"], dict) and entree["elements_connus"], it["id"]
    assert it["elements_obligatoires"] and it["valeurs_interdites"], it["id"]
    valeurs = _valeurs(entree["elements_connus"])
    assert all(isinstance(v, str) and v.strip() for v in valeurs), it["id"]
    emplacements = it["champs_a_laisser_en_emplacement"]
    assert emplacements and len(set(emplacements)) == len(emplacements), it["id"]
    for e in emplacements:
        assert re.fullmatch(r"\[[^\[\]]+\]", e), (it["id"], e)
        assert not [v for v in valeurs if v in e], (it["id"], e)
    base = it.get("base_reglementaire")
    if base is not None:
        assert base["texte"].strip() and base["url"].startswith("https://"), it["id"]
        reelles = [p for p in it["provenance"] if p.get("type") in ("legi", "service-public")]
        assert len(reelles) == 1, it["id"]
        (p,) = reelles
        assert p["url"] == base["url"] and RE_SHA40.fullmatch(p["revision"]), it["id"]
        if p["type"] == "legi":
            assert p["legiarti"] == base["legiarti"] and p["url"].endswith(p["legiarti"])
            assert p["code"].startswith("legi_") and p["articles"], it["id"]
            assert p["depot"] == "AgentPublic/legi", it["id"]
        else:
            _provenance_service_public(it, p)
            assert p["doc_id"] == base["fiche"] and p["chunks"] == base["chunks"], it["id"]
    else:
        assert all(p.get("type") is None for p in it["provenance"]), it["id"]


@pytest.mark.parametrize("version", VERSIONS)
def test_composition_ct(version):
    retenus = _retenus(version, PAR_VERSION[(version, "CT")])
    assert Counter(it["type_courrier"] for it in retenus) == TYPES_CT
    assert sum(1 for it in retenus if it.get("base_reglementaire")) >= 4
    assert len({it["entree"]["objet"] for it in retenus}) == len(retenus), "objets en double"


# ---------------------------------------------------------------------------
# Lecteur strict (slmsp.core.items)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("code", CODES)
def test_lecteur_strict(version, code):
    items_mod = pytest.importorskip("slmsp.core.items")
    erreurs = []
    for it in PAR_VERSION[(version, code)]:
        try:
            items_mod.valider_item(it, strict=True)
        except items_mod.ItemInvalide as exc:
            erreurs += list(exc.erreurs)
    assert erreurs == [], erreurs


# ---------------------------------------------------------------------------
# Verbatim (instantanés locaux)
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


@pytest.fixture(scope="module")
def sources():
    if os.environ.get("SLMSP_EVAL_SOURCES"):
        try:
            import duckdb
        except ImportError:
            pytest.fail("SLMSP_EVAL_SOURCES est défini mais duckdb est absent")
    else:
        duckdb = pytest.importorskip("duckdb")
    dossier = _dossier_sources()
    if dossier is None:
        pytest.skip("instantanés des sources absents (SLMSP_EVAL_SOURCES)")
    return duckdb.connect(), dossier


def _chunks(sources, p: dict) -> str:
    connexion, dossier = sources
    parquets = sorted((dossier / "hf" / "AgentPublic" / "service-public").rglob("*.parquet"))
    assert parquets, "parquet service-public absent des instantanés"
    liste = ", ".join(_sql_chemin(c) for c in parquets)
    lignes = connexion.execute(
        f"SELECT chunk_index, url, text FROM read_parquet([{liste}]) WHERE doc_id = ?",
        [p["doc_id"]],
    ).fetchall()
    par_index = {r[0]: r for r in lignes}
    assert set(p["chunks"]) <= set(par_index), p["source"]
    assert {par_index[c][1] for c in p["chunks"]} == {p["url"]}, p["source"]
    return "\n".join(par_index[c][2] for c in p["chunks"])


def _article(sources, p: dict) -> str:
    connexion, dossier = sources
    parquets = sorted((dossier / "hf" / "AgentPublic" / "legi").rglob(f"{p['code']}/*.parquet"))
    assert parquets, f"parquet LEGI absent des instantanés : {p['code']}"
    liste = ", ".join(_sql_chemin(c) for c in parquets)
    lignes = connexion.execute(
        f"SELECT doc_id, text FROM read_parquet([{liste}]) "
        "WHERE status = 'VIGUEUR' AND list_contains(?, number)",
        [p["articles"]],
    ).fetchall()
    assert lignes and {r[0] for r in lignes} == {p["legiarti"]}, p["source"]
    return "\n".join(r[1] for r in lignes)


def _revisions(dossier: Path) -> dict[str, str]:
    index = dossier / "INDEX.json"
    if not index.is_file():
        return {}
    return {
        f.get("depot"): f.get("revision")
        for f in json.loads(index.read_text(encoding="utf-8"))["fichiers"]
        if "/service-public/" in f.get("chemin", "") or "/legi/" in f.get("chemin", "")
    }


def _verifier_revision(sources, it: dict, p: dict) -> None:
    revisions = _revisions(sources[1])
    if revisions:  # INDEX présent : le dépôt doit y figurer, avec la même révision
        assert revisions.get(p["depot"]) == p["revision"], (it["id"], p["depot"])


@pytest.mark.parametrize(("version", "it"), RE, ids=_ids(RE))
def test_verbatim_re(version, it, sources):
    (p,) = it["provenance"]
    assert it["entree"]["document"] == _chunks(sources, p), f"{it['id']} : document non verbatim"
    _verifier_revision(sources, it, p)


CO_REELS = [(v, it) for v, it in CO if co_reel(it)]


@pytest.mark.parametrize(("version", "it"), CO_REELS, ids=_ids(CO_REELS))
def test_verbatim_co_reel(version, it, sources):
    (p,) = it["provenance"]
    assert it["texte_corrige_reference"] == _chunks(sources, p), f"{it['id']} : non verbatim"
    _verifier_revision(sources, it, p)


CT_BASES = [(v, it) for v, it in CT if it.get("base_reglementaire")]


@pytest.mark.parametrize(("version", "it"), CT_BASES, ids=_ids(CT_BASES))
def test_verbatim_base_ct(version, it, sources):
    base = it["base_reglementaire"]
    (p,) = [p for p in it["provenance"] if p.get("type") in ("legi", "service-public")]
    if p["type"] == "legi":
        article = _article(sources, p)
        if "extrait" in base:
            assert base["texte"] in article, f"{it['id']} : extrait non verbatim"
        else:
            assert base["texte"] == article, f"{it['id']} : article non verbatim ou tronqué"
    else:
        assert base["texte"] == _chunks(sources, p), f"{it['id']} : fiche non verbatim"
    _verifier_revision(sources, it, p)


# ---------------------------------------------------------------------------
# Composition (outil) et verdicts de la double vérification
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("version", VERSIONS)
def test_commande_composition(capsys, version):
    assert cj.cmd_composition(RACINE, version) == 0
    sortie = capsys.readouterr().out
    for code, libelle in (("CO", "Correction"), ("RE", "Résumé"), ("CT", "Courrier type")):
        ligne = f"| {code} ({libelle}) | 15 / 15 (0) | 5 / 5 (0) | 5 / 5 (0) | 5 / 5 (0) |"
        assert ligne in sortie, sortie
    anomalies = sortie.split("## Anomalies de structure", 1)[1]
    assert not re.search(r"\b(CO|RE|CT)-[0-9]", anomalies), anomalies
    for code in CODES:
        assert f"{code}.jsonl" not in anomalies, anomalies


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("code", CODES)
def test_verdicts_acceptes(version, code):
    chemin = _construction(version) / "verification" / f"{code}.jsonl"
    assert chemin.is_file(), f"verdicts absents : {chemin}"
    for n, ligne in enumerate(chemin.read_text(encoding="utf-8").splitlines(), 1):
        if not ligne.strip():
            continue
        v = json.loads(ligne)
        assert v["verdict"] in cj.VERDICTS, (code, n)
        assert cj.RE_DATE_ISO.fullmatch(v["verifie_le"]), (code, n)
        if v["verdict"] == "rejete":
            assert v.get("motif") in cj.MOTIFS, (code, n)
    verdicts, erreurs = cj.derniers_verdicts(_construction(version))
    assert [e for e in erreurs if e.startswith(f"{code}.jsonl")] == []
    # Un item rejeté puis remplacé (CT-003 par CT-016) reste dans le brouillon, exclu.
    items = PAR_VERSION[(version, code)]
    sans_verdict = [it["id"] for it in items if it["id"] not in verdicts]
    assert sans_verdict == [], f"{code} non vérifiés : {sans_verdict}"
    non_acceptes = [
        it["id"]
        for it in _retenus(version, items)
        if verdicts.get(it["id"], {}).get("verdict") != "accepte"
    ]
    assert non_acceptes == [], f"{code} non vérifiés ou rejetés : {non_acceptes}"
