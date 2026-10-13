"""Contrôle transversal du Jeu d'évaluation, versions v1.0 et v1.1 (story 7.6, v1.1). Aucun réseau.

Lit en lecture seule les brouillons `eval/construction/<version>/` (8 Tâches), leurs verdicts
et le calibrage. Si la version est assemblée (`eval/jeu/<version>/items.jsonl`), contrôle que
le fichier contient exactement les items retenus ; si elle est gelée (`MANIFEST.json`),
contrôle aussi le manifeste et l'export JSONL de l'échantillon de revue. Pour v1.1 :
`version_item` incrémenté sur les seuls items modifiés depuis v1.0, verdicts en ajout seul et
export des changements fidèle.
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
VERSIONS = tuple(v for v in ("v1.0", "v1.1") if (RACINE / "eval" / "construction" / v).is_dir())
CALIBRAGE = RACINE / "eval" / "calibrage" / "echantillon-calibrage.jsonl"
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


class Version:
    """Brouillons, verdicts et items retenus d'une version (lecture seule)."""

    def __init__(self, version: str):
        self.version = version
        self.construction = RACINE / "eval" / "construction" / version
        self.jeu = RACINE / "eval" / "jeu" / version
        self.export_revue = RACINE / "eval" / "revue" / f"echantillon-revue-{version}.jsonl"
        self.brouillons, self.erreurs_brouillons = cj.lire_brouillons(self.construction)
        self.verdicts, self.erreurs_verdicts = cj.derniers_verdicts(self.construction)
        self.retenus = sorted(
            (
                it
                for _, _, it in self.brouillons
                if self.verdicts.get(it["id"], {}).get("verdict") != "rejete"
            ),
            key=lambda it: cj.cle_id(it["id"]),
        )


JEUX = {v: Version(v) for v in VERSIONS}
CT_RETENUS = [(v, it) for v in VERSIONS for it in JEUX[v].retenus if it["id"].startswith("CT-")]
ASSEMBLEES = [v for v in VERSIONS if (JEUX[v].jeu / "items.jsonl").is_file()]
GELEES = [v for v in VERSIONS if (JEUX[v].jeu / "MANIFEST.json").is_file()]


@pytest.fixture(autouse=True)
def sans_reseau(monkeypatch):
    def interdit(*_a, **_k):
        raise AssertionError("connexion réseau interdite dans les tests")

    monkeypatch.setattr(socket.socket, "connect", interdit)
    monkeypatch.setattr(socket.socket, "connect_ex", interdit)
    monkeypatch.setattr(socket, "create_connection", interdit)
    monkeypatch.setattr(socket, "getaddrinfo", interdit)


def test_versions_lues():
    assert "v1.0" in VERSIONS and "v1.0" in GELEES


# ---------------------------------------------------------------------------
# Identifiants, verdicts, composition
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("version", VERSIONS)
def test_identifiants_uniques_et_coherents(version):
    j = JEUX[version]
    assert j.erreurs_brouillons == []
    assert cj.erreurs_identifiants(j.brouillons) == []
    for code, n, it in j.brouillons:
        attendues = {cj.TACHES[code]} | cj.ALIAS_TACHES.get(code, set())
        lieu = f"{code}.jsonl:{n} {it['id']}"
        assert it.get("tache") in attendues, f"{lieu} : tâche {it.get('tache')!r}"


@pytest.mark.parametrize("version", VERSIONS)
def test_verdicts_complets(version):
    j = JEUX[version]
    assert j.erreurs_verdicts == []
    ids = {it["id"] for _, _, it in j.brouillons}
    assert sorted(ids - set(j.verdicts), key=cj.cle_id) == [], "items sans verdict"
    assert sorted(set(j.verdicts) - ids, key=cj.cle_id) == [], "verdicts sans brouillon"
    non_acceptes = [it["id"] for it in j.retenus if j.verdicts[it["id"]]["verdict"] != "accepte"]
    assert non_acceptes == []


@pytest.mark.parametrize("version", VERSIONS)
def test_composition_aux_cibles(version):
    retenus = JEUX[version].retenus
    assert len(retenus) == sum(sum(c) for c in cj.CIBLES.values()) == 225
    par_strate = Counter((it["id"].split("-")[0], it["difficulte"]) for it in retenus)
    for code, cibles in cj.CIBLES.items():
        reel = tuple(par_strate[(code, d)] for d in cj.DIFFICULTES)
        assert reel == cibles, f"{code} : {reel} au lieu de {cibles}"
    q = [it for it in retenus if it["id"].startswith("Q-")]
    assert sum(1 for it in q if it.get("sans_reponse") is True) == cj.CIBLE_Q_SANS_REPONSE
    assert sum(1 for it in q if cj.amorce_reelle(it)) >= cj.CIBLE_Q_PART_AMORCES * len(q)
    # Thèmes (Q, RD, LC, RE) : mêmes cibles que `composition` (42/21/21/21/21/14 sur 140).
    total_cible = sum(sum(cj.CIBLES[c]) for c in cj.CODES_THEMATIQUES)
    thematiques = [it for it in retenus if it["id"].split("-")[0] in cj.CODES_THEMATIQUES]
    assert len(thematiques) == total_cible == 140
    reel = Counter(it.get("theme") for it in thematiques)
    cibles = {t: round(part * total_cible) for t, part in cj.THEMES.items()}
    assert sorted(cibles.values()) == [14, 21, 21, 21, 21, 42]
    assert dict(reel) == cibles


# ---------------------------------------------------------------------------
# Courrier type : libellés exacts des emplacements dans la consigne
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("version", VERSIONS)
def test_ct_retenus(version):
    assert sum(1 for v, _ in CT_RETENUS if v == version) == sum(cj.CIBLES["CT"])


@pytest.mark.parametrize(
    ("version", "it"), CT_RETENUS, ids=[f"{v}-{it['id']}" for v, it in CT_RETENUS]
)
def test_ct_aligne(version, it):
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


@pytest.mark.parametrize("version", VERSIONS)
@pytest.mark.parametrize("code", cj.CODES)
def test_aucune_source_du_calibrage(version, code):
    calibrage = _sources_calibrage()
    fautifs = []
    for it in JEUX[version].retenus:
        if not it["id"].startswith(code + "-"):
            continue
        cites = json.dumps([it.get(c) for c in CHAMPS_SOURCES], ensure_ascii=False)
        communes = sorted((set(RE_SOURCE.findall(cites)) | _articles_cites(it)) & calibrage)
        fautifs += [f"{it['id']} cite {s}" for s in communes]
    assert fautifs == [], fautifs


# ---------------------------------------------------------------------------
# Jeu assemblé et jeu gelé
# ---------------------------------------------------------------------------
def _lignes(chemin: Path) -> list[str]:
    texte = chemin.read_bytes().decode("utf-8").replace("\r\n", "\n")
    return [ligne for ligne in texte.split("\n") if ligne.strip()]


@pytest.mark.parametrize("version", ASSEMBLEES)
def test_items_assembles_egaux_aux_retenus(version):
    j = JEUX[version]
    assembles = [json.loads(ligne) for ligne in _lignes(j.jeu / "items.jsonl")]
    assert [it["id"] for it in assembles] == [it["id"] for it in j.retenus]
    assert assembles == j.retenus


@pytest.mark.parametrize("version", GELEES)
def test_manifeste_et_export_revue(version):
    from slmsp.evaluation.gel import verifier_manifeste  # un échec d'import doit échouer

    j = JEUX[version]
    manifeste = verifier_manifeste(version, RACINE)
    assert manifeste.nb_items == len(j.retenus)
    if version != "v1.0":
        assert manifeste.statut == "relu"
        assert manifeste.date_reference is not None
    if not j.export_revue.is_file():
        pytest.fail(f"export de revue absent : {j.export_revue}")
    par_id = {json.loads(ligne)["id"]: ligne for ligne in _lignes(j.jeu / "items.jsonl")}
    lignes = _lignes(j.export_revue)
    assert [json.loads(ligne)["id"] for ligne in lignes] == manifeste.echantillons.relecture
    assert lignes == [par_id[i] for i in manifeste.echantillons.relecture]
    for nom in (f"echantillon-revue-{version}.md", f"echantillon-revue-{version}-lecture.md"):
        assert (j.export_revue.parent / nom).is_file(), f"export de revue absent : {nom}"


# ---------------------------------------------------------------------------
# v1.1 : version_item, ajout seul et export des changements
# ---------------------------------------------------------------------------
MODIFIES_V1_1 = {
    "Q-042",
    "CR-006",
    "CR-021",
    "RD-010",
    "RD-017",
    "RD-019",
    "RD-023",
    "RD-030",
    "RD-031",
    "RD-039",
    "CO-001",
    "CO-002",
    "CO-006",
    "CO-007",
    "CO-011",
    "CO-012",
}
"""Items modifiés par les arbitrages A, F, G1, G2 et G4 (eval/revue/arbitrages-v1.1.md)."""
NOUVEAUX_V1_1 = {"Q-068", "Q-069", "Q-070"}
RETIRES_V1_1 = {"Q-044", "Q-046", "Q-050"}


@pytest.fixture(scope="module")
def v1_1():
    if "v1.1" not in JEUX:
        pytest.fail("brouillons v1.1 absents")
    return JEUX["v1.0"], JEUX["v1.1"]


def test_v1_1_version_item(v1_1):
    v10, v11 = v1_1
    anciens = {it["id"]: it for it in v10.retenus}
    nouveaux = {it["id"]: it for it in v11.retenus}
    assert set(nouveaux) - set(anciens) == NOUVEAUX_V1_1
    assert set(anciens) - set(nouveaux) == RETIRES_V1_1
    modifies = {i for i in anciens.keys() & nouveaux.keys() if anciens[i] != nouveaux[i]}
    assert modifies == MODIFIES_V1_1
    for identifiant in modifies:
        assert nouveaux[identifiant]["version_item"] == anciens[identifiant]["version_item"] + 1
    for identifiant in NOUVEAUX_V1_1:
        it = nouveaux[identifiant]
        assert it["version_item"] == 1 and it["theme"] == "collectivites"
        assert it["sans_reponse"] is False
        assert all("entreprendre.service-public.gouv.fr" in u for u in it["sources_attendues"])
    for identifiant in RETIRES_V1_1:
        verdict = v11.verdicts[identifiant]
        assert verdict["verdict"] == "rejete" and verdict["motif"] == "autre"
        assert "arbitrage E" in verdict["detail"]
    difficultes = sorted(nouveaux[i]["difficulte"] for i in NOUVEAUX_V1_1)
    assert difficultes == sorted(anciens[i]["difficulte"] for i in RETIRES_V1_1)


def test_v1_1_brouillons_et_verdicts_en_ajout_seul(v1_1):
    """Aucun brouillon ni verdict v1.0 supprimé ou réécrit : v1.1 les prolonge."""
    v10, v11 = v1_1
    assert {it["id"] for _, _, it in v10.brouillons} <= {it["id"] for _, _, it in v11.brouillons}
    for code in cj.CODES:
        ancien = _lignes(v10.construction / "verification" / f"{code}.jsonl")
        nouveau = _lignes(v11.construction / "verification" / f"{code}.jsonl")
        assert nouveau[: len(ancien)] == ancien, f"verification/{code}.jsonl réécrit"


def test_v1_1_verdicts_ajoutes_pour_les_items_touches(v1_1):
    """Chaque item nouveau ou modifié en v1.1 (par rapport à `eval/jeu/v1.0/items.jsonl`) a
    son dernier verdict ajouté après les lignes héritées de v1.0, et ce verdict est
    `accepte` : un ancien `accepte` de v1.0 ne suffit pas."""
    v10, v11 = v1_1
    geles = {
        json.loads(ligne)["id"]: json.loads(ligne) for ligne in _lignes(v10.jeu / "items.jsonl")
    }
    touches = [it["id"] for it in v11.retenus if it["id"] not in geles or geles[it["id"]] != it]
    assert set(touches) == MODIFIES_V1_1 | NOUVEAUX_V1_1
    fautifs = []
    for identifiant in touches:
        code = identifiant.split("-")[0]
        heritees = len(_lignes(v10.construction / "verification" / f"{code}.jsonl"))
        lignes = [
            json.loads(lg) for lg in _lignes(v11.construction / "verification" / f"{code}.jsonl")
        ]
        rangs = [n for n, v in enumerate(lignes) if v.get("id") == identifiant]
        if not rangs or rangs[-1] < heritees or lignes[rangs[-1]]["verdict"] != "accepte":
            fautifs.append(identifiant)
    assert fautifs == [], f"verdict v1.1 absent, hérité de v1.0 ou non accepté : {fautifs}"


def test_v1_1_export_des_changements(v1_1):
    export = RACINE / "eval" / "revue" / "changements-v1.0-v1.1.jsonl"
    if "v1.1" not in ASSEMBLEES or not export.is_file():
        pytest.fail(f"v1.1 non assemblé ou export des changements absent : {export}")
    lignes = [json.loads(ligne) for ligne in _lignes(export)]
    statuts = {lg["id"]: lg["statut"] for lg in lignes}
    attendus = (
        dict.fromkeys(MODIFIES_V1_1, "modifie")
        | dict.fromkeys(NOUVEAUX_V1_1, "nouveau")
        | dict.fromkeys(RETIRES_V1_1, "retire")
    )
    assert statuts == attendus
    reference = cj.lire_items_jeu(RACINE / "eval" / "jeu" / "v1.0" / "items.jsonl")
    version = cj.lire_items_jeu(RACINE / "eval" / "jeu" / "v1.1" / "items.jsonl")
    attendu = cj.comparer_jeux(reference, version, v1_1[1].verdicts)
    assert lignes == json.loads(json.dumps(attendu, ensure_ascii=False))
    assert export.with_suffix(".md").is_file()
