"""Tests de eval/outils/construire_jeu.py (story 7.1). Aucun appel réseau."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
import socket
import sys
from pathlib import Path

import pytest

OUTIL = Path(__file__).resolve().parents[2] / "eval" / "outils" / "construire_jeu.py"


def _charger():
    spec = importlib.util.spec_from_file_location("construire_jeu", OUTIL)
    module = importlib.util.module_from_spec(spec)
    sys.modules["construire_jeu"] = module
    spec.loader.exec_module(module)
    return module


cj = _charger()
SHA_REV = "a" * 40


@pytest.fixture(autouse=True)
def sans_reseau(monkeypatch):
    def interdit(*_a, **_k):
        raise AssertionError("connexion réseau interdite dans les tests")

    monkeypatch.setattr(socket.socket, "connect", interdit)
    monkeypatch.setattr(socket.socket, "connect_ex", interdit)
    monkeypatch.setattr(socket, "create_connection", interdit)
    monkeypatch.setattr(socket, "getaddrinfo", interdit)


class FauxReponse:
    def __init__(self, statut=200, corps=b"", entetes=None):
        self.status = statut
        self.headers = entetes or {}
        self._flux = io.BytesIO(corps)

    def read(self, n=-1):
        return self._flux.read(n)

    def close(self):
        pass


class FauxOuvreur:
    """Routes : URL -> liste de réponses servies dans l'ordre (la dernière se répète)."""

    def __init__(self, routes):
        self.routes = {u: list(r) if isinstance(r, list) else [r] for u, r in routes.items()}
        self.appels: list[tuple[str, str]] = []

    def __call__(self, req, delai):
        self.appels.append((req.get_method(), req.full_url))
        file = self.routes.get(req.full_url)
        if not file:
            return FauxReponse(404)
        rep = file.pop(0) if len(file) > 1 else file[0]
        if isinstance(rep, Exception):
            raise rep
        return FauxReponse(rep.status, rep._flux.getvalue(), rep.headers)


def client(routes, attentes=None, tentatives=3):
    attentes = [] if attentes is None else attentes
    return cj.ClientHTTP(
        ouvreur=FauxOuvreur(routes), dormir=attentes.append, tentatives=tentatives, attente=1.0
    )


# ---------------------------------------------------------------------------
# Imports (AST)
# ---------------------------------------------------------------------------
def test_imports_stdlib_au_niveau_module_et_aucun_module_du_projet():
    arbre = ast.parse(OUTIL.read_text(encoding="utf-8"))
    autorises_a_l_usage = {"duckdb", "openpyxl"}
    stdlib = set(sys.stdlib_module_names) | {"__future__"}

    def racines(noeud):
        if isinstance(noeud, ast.Import):
            return [a.name.split(".")[0] for a in noeud.names]
        if isinstance(noeud, ast.ImportFrom):
            assert noeud.level == 0, "import relatif interdit"
            return [noeud.module.split(".")[0]]
        return []

    niveau_module = [r for n in arbre.body for r in racines(n)]
    partout = [r for n in ast.walk(arbre) for r in racines(n)]
    assert niveau_module and all(r in stdlib for r in niveau_module), niveau_module
    assert all(r in stdlib | autorises_a_l_usage for r in partout), partout
    assert not any(r == "slmsp" for r in partout)


# ---------------------------------------------------------------------------
# Contrôle d'hôte
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/x",
        "http://huggingface.co/x",
        "https://huggingface.co:8443/x",
        "https://user@huggingface.co/x",
        "https://huggingface.co.example.com/x",
        "https://evilhuggingface.co/x",
        "https://data.gouv.fr/x",
        "file:///etc/passwd",
    ],
)
def test_hote_refuse_avant_toute_connexion(url):
    c = client({})
    with pytest.raises(cj.HoteRefuse):
        c.lire(url)
    assert c.ouvreur.appels == []


def test_hote_refuse_avec_l_ouvreur_reel_sans_toucher_au_socket():
    # Le socket est interdit par la fixture : HoteRefuse doit être levé avant lui.
    with pytest.raises(cj.HoteRefuse):
        cj.ClientHTTP(dormir=lambda s: None).lire("https://example.com/x")


def test_methode_post_refusee():
    with pytest.raises(cj.RequeteRefusee):
        cj.verifier_requete("https://huggingface.co/api", "POST")


@pytest.mark.parametrize(
    "url",
    [
        "https://huggingface.co/datasets/x",
        "https://cas-bridge.xethub.hf.co/x",
        "https://cdn-lfs.huggingface.co/x",
        "https://www.service-public.gouv.fr/particuliers/vosdroits/F1344",
        "https://mcp.data.gouv.fr/health",
    ],
)
def test_hotes_autorises(url):
    cj.verifier_requete(url, "GET")


def test_redirection_vers_hote_refuse_controlee_a_chaque_saut(tmp_path):
    depart = "https://huggingface.co/x"
    c = client({depart: FauxReponse(302, entetes={"Location": "https://example.com/y"})})
    with pytest.raises(cj.HoteRefuse):
        c.telecharger(depart, tmp_path / "f.bin")
    assert c.ouvreur.appels == [("GET", depart)]
    assert not (tmp_path / "f.bin").exists()


def test_redirection_relative_et_cdn_suivies(tmp_path):
    depart = "https://huggingface.co/datasets/d/resolve/s/f.bin"
    routes = {
        depart: FauxReponse(307, entetes={"Location": "/api/resolve-cache/f.bin"}),
        "https://huggingface.co/api/resolve-cache/f.bin": FauxReponse(
            302, entetes={"Location": "https://cas-bridge.xethub.hf.co/f?sig=1"}
        ),
        "https://cas-bridge.xethub.hf.co/f?sig=1": FauxReponse(200, b"donnees"),
    }
    c = client(routes)
    info = c.telecharger(depart, tmp_path / "f.bin")
    assert (tmp_path / "f.bin").read_bytes() == b"donnees"
    assert info["sha256"] == hashlib.sha256(b"donnees").hexdigest()
    assert len(c.ouvreur.appels) == 3


# ---------------------------------------------------------------------------
# Reprises, fichiers présents, INDEX
# ---------------------------------------------------------------------------
def test_reprise_apres_deux_503(tmp_path):
    url = "https://huggingface.co/f.bin"
    attentes: list[float] = []
    c = client({url: [FauxReponse(503), FauxReponse(503), FauxReponse(200, b"ok")]}, attentes)
    index = cj.charger_index(tmp_path)
    statut, _ = cj.instantane(
        c,
        tmp_path,
        index,
        url,
        tmp_path / "hf" / "f.bin",
        depot="d/x",
        revision=SHA_REV,
        force=False,
    )
    assert statut == "téléchargé"
    assert (tmp_path / "hf" / "f.bin").read_bytes() == b"ok"
    assert not (tmp_path / "hf" / "f.bin.part").exists()
    assert attentes == [1.0, 2.0]
    entree = json.loads((tmp_path / "INDEX.json").read_text(encoding="utf-8"))["fichiers"][0]
    assert entree["chemin"] == "hf/f.bin" and entree["url"] == url and entree["revision"] == SHA_REV
    assert entree["sha256"] == hashlib.sha256(b"ok").hexdigest() and entree["taille"] == 2
    assert len(entree["consulte_le"]) == 10


def test_reprise_sur_erreur_reseau_puis_succes(tmp_path):
    url = "https://huggingface.co/f.bin"
    c = client({url: [ConnectionResetError("coupure"), FauxReponse(200, b"ok")]})
    c.telecharger(url, tmp_path / "f.bin")
    assert (tmp_path / "f.bin").read_bytes() == b"ok"


def test_echec_apres_n_tentatives(tmp_path):
    url = "https://huggingface.co/f.bin"
    attentes: list[float] = []
    c = client({url: FauxReponse(503)}, attentes, tentatives=3)
    with pytest.raises(cj.ErreurTelechargement):
        c.telecharger(url, tmp_path / "f.bin")
    assert len(c.ouvreur.appels) == 3 and attentes == [1.0, 2.0]
    assert not (tmp_path / "f.bin").exists()


def test_404_sans_reprise(tmp_path):
    c = client({})
    with pytest.raises(cj.ErreurHTTP):
        c.telecharger("https://huggingface.co/absent", tmp_path / "f.bin")
    assert len(c.ouvreur.appels) == 1


def test_fichier_deja_present_jamais_retelecharge(tmp_path):
    cible = tmp_path / "hf" / "f.bin"
    cible.parent.mkdir(parents=True)
    cible.write_bytes(b"ancien")
    c = client({"https://huggingface.co/f.bin": FauxReponse(200, b"nouveau")})
    index = cj.charger_index(tmp_path)
    statut, _ = cj.instantane(
        c,
        tmp_path,
        index,
        "https://huggingface.co/f.bin",
        cible,
        depot="d/x",
        revision=SHA_REV,
        force=False,
    )
    assert statut.startswith("déjà présent") and c.ouvreur.appels == []
    assert cible.read_bytes() == b"ancien"
    entrees = json.loads((tmp_path / "INDEX.json").read_text(encoding="utf-8"))["fichiers"]
    assert entrees[0]["sha256"] == hashlib.sha256(b"ancien").hexdigest()
    # Second passage : l'entrée est conservée telle quelle.
    avant = (tmp_path / "INDEX.json").read_bytes()
    cj.instantane(
        c,
        tmp_path,
        cj.charger_index(tmp_path),
        "https://huggingface.co/f.bin",
        cible,
        depot="d/x",
        revision=SHA_REV,
        force=False,
    )
    assert (tmp_path / "INDEX.json").read_bytes() == avant and c.ouvreur.appels == []


def _routes_questions(corps_sp=b"xlsx-sp", corps_ia=b"xlsx-ia", taille_sp=None):
    routes = {}
    for depot, nom, corps in (
        ("AgentPublic/sp_questions_corpus", "gpt_corpus-20kq&A.xlsx", corps_sp),
        (
            "AgentPublic/assistant_ia_questions_corpus",
            "evaluation_qo_assistant_ia_v1.xlsx",
            corps_ia,
        ),
    ):
        routes[f"https://huggingface.co/api/datasets/{depot}/revision/main"] = FauxReponse(
            200, json.dumps({"sha": SHA_REV}).encode()
        )
        arbre = [
            {"type": "file", "path": "README.md", "size": 3},
            {
                "type": "file",
                "path": nom,
                "size": taille_sp if (taille_sp and corps is corps_sp) else len(corps),
                "lfs": {"oid": hashlib.sha256(corps).hexdigest(), "size": len(corps)},
            },
        ]
        routes[f"https://huggingface.co/api/datasets/{depot}/tree/{SHA_REV}"] = FauxReponse(
            200, json.dumps(arbre).encode()
        )
        quoted = nom.replace("&", "%26")
        routes[f"https://huggingface.co/datasets/{depot}/resolve/{SHA_REV}/{quoted}"] = FauxReponse(
            200, corps
        )
    return routes


def test_sources_epingle_la_revision_et_remplit_l_index(tmp_path, capsys):
    c = client(_routes_questions())
    rc = cj.main(["sources", "--dest", str(tmp_path), "--quoi", "questions"], client=c)
    assert rc == 0
    f = tmp_path / "hf" / "AgentPublic" / "sp_questions_corpus" / "gpt_corpus-20kq&A.xlsx"
    assert f.read_bytes() == b"xlsx-sp"
    entrees = json.loads((tmp_path / "INDEX.json").read_text(encoding="utf-8"))["fichiers"]
    assert len(entrees) == 2
    for e in entrees:
        assert f"/resolve/{SHA_REV}/" in e["url"] and e["revision"] == SHA_REV
        assert e["sha256"] == cj.sha256_fichier(tmp_path / e["chemin"])
        assert e["consulte_le"]
    assert "# Instantanés des sources" in capsys.readouterr().out
    # Relance : rien n'est retéléchargé.
    n = len(c.ouvreur.appels)
    cj.main(["sources", "--dest", str(tmp_path), "--quoi", "questions"], client=c)
    assert not any("/resolve/" in u for _, u in c.ouvreur.appels[n:])


def test_sources_taille_inattendue_ne_cree_pas_le_fichier(tmp_path):
    c = client(_routes_questions(taille_sp=999))
    rc = cj.main(["sources", "--dest", str(tmp_path), "--quoi", "questions"], client=c)
    assert rc != 0
    assert not (
        tmp_path / "hf" / "AgentPublic" / "sp_questions_corpus" / "gpt_corpus-20kq&A.xlsx"
    ).exists()


def test_sources_page_hors_liste_blanche_refusee(tmp_path, capsys):
    c = client({})
    rc = cj.main(["sources", "--dest", str(tmp_path), "--page", "https://example.com/x"], client=c)
    assert rc != 0 and c.ouvreur.appels == []
    assert "HoteRefuse" in capsys.readouterr().err
    rc = cj.main(
        ["sources", "--dest", str(tmp_path), "--page", "https://huggingface.co/x"], client=c
    )
    assert rc != 0 and c.ouvreur.appels == []


def test_sources_page_liste_blanche(tmp_path):
    url = "https://www.service-public.fr/particuliers/vosdroits/F1344"
    finale = "https://www.service-public.gouv.fr/particuliers/vosdroits/F1344"
    c = client(
        {
            url: FauxReponse(301, entetes={"Location": finale}),
            finale: FauxReponse(200, "<html>é</html>".encode()),
        }
    )
    assert cj.main(["sources", "--dest", str(tmp_path), "--page", url], client=c) == 0
    cible = (
        tmp_path / "pages" / "www.service-public.fr" / "particuliers" / "vosdroits" / "F1344.html"
    )
    assert cible.exists()
    e = json.loads((tmp_path / "INDEX.json").read_text(encoding="utf-8"))["fichiers"][0]
    assert e["url"] == url and e["url_finale"] == finale and e["revision"] is None


def test_selection_legi_codes():
    sel = cj.selections(["legi"], ["crpa", "code_du_travail"])
    assert [s[2] for s in sel] == [
        "data/legi-latest/legi_code_des_relations_entre_le_public_et_l_administration",
        "data/legi-latest/legi_code_du_travail",
    ]
    with pytest.raises(cj.ErreurOutil):
        cj.selections(["legi"], ["../x"])


# ---------------------------------------------------------------------------
# Fiche
# ---------------------------------------------------------------------------
def _sp_json(dest: Path, doc_id: str):
    rows = [
        {
            "doc_id": doc_id,
            "chunk_index": i,
            "title": "Carte d'identité",
            "url": f"https://x/{doc_id}",
            "text": f"texte {i}",
        }
        for i in (2, 0, 1)
    ]
    (dest / "hf").mkdir(parents=True, exist_ok=True)
    (dest / "hf" / f"sp_{doc_id}.json").write_text(json.dumps({"rows": rows}), encoding="utf-8")


def test_fiche_repli_json(tmp_path, capsys):
    _sp_json(tmp_path, "F1344")
    assert cj.main(["fiche", "F1344", "--dest", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("# Carte d'identité\n\nhttps://x/F1344")
    assert out.index("## Chunk 0") < out.index("## Chunk 1") < out.index("## Chunk 2")


def test_fiche_absente(tmp_path):
    assert cj.main(["fiche", "F9999", "--dest", str(tmp_path)]) != 0


def test_fiche_parquet_local(tmp_path, capsys):
    duckdb = pytest.importorskip("duckdb")
    dossier = tmp_path / "hf" / "AgentPublic" / "service-public" / "latest" / "train"
    dossier.mkdir(parents=True)
    cible = (dossier / "0000.parquet").as_posix()
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE t AS SELECT * FROM (VALUES ('F1', 1, 'Titre', 'https://u/F1', 'deux'), "
        "('F1', 0, 'Titre', 'https://u/F1', 'un'), ('F2', 0, 'Autre', 'https://u/F2', 'x')) "
        "v(doc_id, chunk_index, title, url, text)"
    )
    con.execute(f"COPY t TO '{cible}' (FORMAT PARQUET)")
    con.close()
    assert cj.main(["fiche", "F1", "--dest", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "# Titre" in out and out.index("un") < out.index("deux") and "Autre" not in out


# ---------------------------------------------------------------------------
# Assembler
# ---------------------------------------------------------------------------
def _item(identifiant, **extra):
    code = identifiant.split("-")[0]
    base = {
        "id": identifiant,
        "tache": cj.TACHES[code],
        "difficulte": "facile",
        "entree": "Question é ?" if code in ("Q", "RD", "NR") else {"texte": "x"},
        "provenance": [
            {"url": "https://www.service-public.gouv.fr/x", "consulte_le": "2026-10-12"}
        ],
        "licence_source": "Etalab-2.0",
        "fictif": False,
        "version_item": 1,
        "parametres": {},
    }
    base.update(extra)
    return base


def _brouillon(racine: Path, code: str, items, version="v1.0"):
    d = racine / "eval" / "construction" / version
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{code}.jsonl").write_text(
        "".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items), encoding="utf-8"
    )


def _verif(racine: Path, code: str, lignes, version="v1.0"):
    d = racine / "eval" / "construction" / version / "verification"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{code}.jsonl").write_text(
        "".join(
            (ligne if isinstance(ligne, str) else json.dumps(ligne)) + "\n" for ligne in lignes
        ),
        encoding="utf-8",
    )


def _sortie(racine: Path) -> Path:
    return racine / "eval" / "jeu" / "v1.0" / "items.jsonl"


def test_assembler_trie_utf8_lf(tmp_path):
    _brouillon(tmp_path, "Q", [_item("Q-010"), _item("Q-002"), _item("Q-001")])
    _brouillon(tmp_path, "NR", [_item("NR-002"), _item("NR-001")])
    _brouillon(tmp_path, "RD", [_item("RD-010"), _item("RD-009")])
    assert cj.main(["assembler", "--version", "v1.0", "--racine", str(tmp_path)]) == 0
    brut = _sortie(tmp_path).read_bytes()
    assert b"\r" not in brut and "é".encode() in brut
    ids = [json.loads(ligne)["id"] for ligne in brut.decode("utf-8").splitlines()]
    assert ids == ["NR-001", "NR-002", "Q-001", "Q-002", "Q-010", "RD-009", "RD-010"]


def test_assembler_doublon_echoue_sans_ecrire(tmp_path, capsys):
    _brouillon(tmp_path, "Q", [_item("Q-001"), _item("Q-001")])
    assert cj.main(["assembler", "--racine", str(tmp_path)]) != 0
    assert not _sortie(tmp_path).exists()
    assert "dupliqué : Q-001" in capsys.readouterr().err


@pytest.mark.parametrize(
    "code, identifiant",
    [("RD", "R-001"), ("Q", "NR-001"), ("Q", "Q-1"), ("RE", "RS-001"), ("Q", "Q-000")],
)
def test_assembler_id_mal_forme(tmp_path, capsys, code, identifiant):
    _brouillon(tmp_path, code, [_item("Q-001") | {"id": identifiant}])
    assert cj.main(["assembler", "--racine", str(tmp_path)]) != 0
    assert not _sortie(tmp_path).exists()
    assert identifiant in capsys.readouterr().err


def test_assembler_exclut_les_items_rejetes(tmp_path, capsys):
    _brouillon(tmp_path, "Q", [_item("Q-001"), _item("Q-002"), _item("Q-003")])
    _verif(
        tmp_path,
        "Q",
        [
            {
                "id": "Q-001",
                "verdict": "rejete",
                "motif": "ambigu",
                "detail": "",
                "verifie_le": "2026-10-12",
            },
            {"id": "Q-001", "verdict": "accepte", "verifie_le": "2026-10-12"},
            {
                "id": "Q-002",
                "verdict": "rejete",
                "motif": "fait_absent_source",
                "detail": "montant",
                "verifie_le": "2026-10-12",
            },
        ],
    )
    assert cj.main(["assembler", "--racine", str(tmp_path)]) == 0
    ids = [
        json.loads(ligne)["id"]
        for ligne in _sortie(tmp_path).read_text(encoding="utf-8").splitlines()
    ]
    assert ids == ["Q-001", "Q-003"]
    out = capsys.readouterr().out
    assert "`Q-002` : fait_absent_source" in out


def test_assembler_refuse_un_jeu_gele(tmp_path):
    _brouillon(tmp_path, "Q", [_item("Q-001")])
    _sortie(tmp_path).parent.mkdir(parents=True)
    (_sortie(tmp_path).parent / "MANIFEST.json").write_text("{}", encoding="utf-8")
    assert cj.main(["assembler", "--racine", str(tmp_path)]) != 0
    assert not _sortie(tmp_path).exists()


def test_tri_naturel():
    assert sorted(["RD-010", "RD-009", "RD-100"], key=cj.cle_id) == ["RD-009", "RD-010", "RD-100"]


# ---------------------------------------------------------------------------
# Composition, rejets
# ---------------------------------------------------------------------------
def test_composition_brouillons_partiels(tmp_path, capsys):
    q_amorce = _item(
        "Q-001",
        theme="social-autonomie",
        reponse_reference="r",
        elements_cles=["a", "b", "c"],
        sources_attendues=["https://www.service-public.gouv.fr/x"],
        sans_reponse=False,
        amorce_usager="ma carte est-elle gratuite ?",
        provenance=[
            {
                "url": "https://huggingface.co/datasets/AgentPublic/sp_questions_corpus",
                "consulte_le": "2026-10-12",
            }
        ],
    )
    q_sans = _item(
        "Q-002",
        difficulte="moyen",
        theme="fiscalite-locale",
        reponse_reference="r",
        elements_cles=["a", "b", "c"],
        sources_attendues=[],
        sans_reponse=True,
    )
    rd = _item(
        "RD-001",
        theme="collectivites",
        appels_attendus=[{"outil": "search_datasets", "regles": {}}],
        mode="repli",
        cassettes=[],
        reponse_reference={"jeu_principal": {"producteur": "INSEE"}},
        valeurs_attendues={"n": 1},
    )
    texte = "Le chat sont noir."
    co = _item(
        "CO-001",
        entree={"texte": texte},
        texte_corrige_reference="Le chat est noir.",
        fautes=[
            {"debut": 8, "fin": 12, "erreur": "sont", "correction": "est", "type": "accord"},
            {"debut": 0, "fin": 2, "erreur": "La", "correction": "Le", "type": "x"},
        ],
    )
    _brouillon(tmp_path, "Q", [q_amorce, q_sans])
    _brouillon(tmp_path, "RD", [rd])
    _brouillon(tmp_path, "CO", [co])
    assert cj.main(["composition", "--racine", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "| Q (Question) | 2 / 60 (-58) | 1 / 20 (-19) | 1 / 25 (-24) | 0 / 15 (-15) |" in out
    assert "| Q sans réponse | 8 | 1 | -7 |" in out
    assert "| Q sans réponse avec `orientation_attendue` | 1 | 0 | -1 |" in out
    assert (
        "| Q issus d'amorces réelles | ≥ 50 % (≥ 30 sur 60) | 1 (50% des Q présents) | -29 |" in out
    )
    assert "| RD cas de repli | 4 | 1 | -3 |" in out
    assert "| INSEE | 1 |" in out
    assert "| `social-autonomie` | 1 | 0 | 0 | 0 | 1 |" in out
    assert "`Q-002` : `sans_reponse` sans `orientation_attendue`" in out
    assert "`CO-001` : `fautes[1]` : position fausse" in out
    assert "`fautes[0]`" not in out
    assert "`RD-001` : champs manquants" not in out


def test_composition_signale_champs_manquants_et_lignes_illisibles(tmp_path, capsys):
    d = tmp_path / "eval" / "construction" / "v1.0"
    d.mkdir(parents=True)
    (d / "LC.jsonl").write_text(
        json.dumps({"id": "LC-001", "tache": "Langage clair"}) + "\n{pas du json\n",
        encoding="utf-8",
    )
    assert cj.main(["composition", "--racine", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "LC.jsonl:2 : JSON illisible" in out
    assert "`LC-001` : champs manquants" in out and "`kandel_moles_entree`" in out


def test_rejets_par_tache_et_motif(tmp_path, capsys):
    _verif(
        tmp_path,
        "Q",
        [
            {"id": "Q-001", "verdict": "rejete", "motif": "ambigu"},
            {"id": "Q-001", "verdict": "accepte"},
            {"id": "Q-002", "verdict": "accepte"},
            "{ligne cassée",
            {"id": "Q-003", "verdict": "rejete", "motif": "url_morte_ou_differente"},
        ],
    )
    _verif(tmp_path, "RD", [{"id": "RD-001", "verdict": "rejete", "motif": "inventé"}])
    assert cj.main(["rejets", "--racine", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "| Q | 3 | 4 | 2 | 50.0% |" in out
    assert "| RD | 1 | 1 | 1 | 100.0% |" in out
    assert "| `ambigu` | 1 | 0 | 1 |" in out
    assert "| `autre` | 0 | 1 | 1 |" in out
    assert "Q.jsonl:4 : JSON illisible" in out
    assert "motif inconnu 'inventé'" in out


def test_rejets_sans_verification(tmp_path, capsys):
    assert cj.main(["rejets", "--racine", str(tmp_path)]) == 0
    assert "Aucune vérification" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Correctifs de revue
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("code", [301, 302, 303, 307, 308])
def test_ouvreur_reel_ne_suit_pas_les_redirections(code):
    import urllib.response

    # Modules HTTP repris de l'outil (exclu de TID251), sans import direct dans les tests.
    ur, hc = cj.urllib.request, cj.http.client
    appels = []

    class FauxHTTPS(ur.BaseHandler):
        handler_order = 100

        def https_open(self, req):
            appels.append(req.full_url)
            entetes = hc.HTTPMessage()
            entetes["Location"] = "https://example.com/ailleurs"
            rep = urllib.response.addinfourl(io.BytesIO(b""), entetes, req.full_url, code)
            rep.msg = "redirection"
            return rep

    opener = ur.build_opener(ur.ProxyHandler({}), cj._SansRedirection, FauxHTTPS())
    rep = opener.open("https://huggingface.co/x", timeout=1)
    assert rep.status == code and appels == ["https://huggingface.co/x"]


def test_429_avec_retry_after(tmp_path):
    url = "https://huggingface.co/f.bin"
    attentes: list[float] = []
    c = client(
        {url: [FauxReponse(429, entetes={"Retry-After": "5"}), FauxReponse(200, b"ok")]}, attentes
    )
    c.telecharger(url, tmp_path / "f.bin")
    assert (tmp_path / "f.bin").read_bytes() == b"ok" and attentes == [5.0]


def test_sources_oid_lfs_faux_ne_cree_pas_le_fichier(tmp_path):
    routes = _routes_questions()
    url_arbre = (
        f"https://huggingface.co/api/datasets/AgentPublic/sp_questions_corpus/tree/{SHA_REV}"
    )
    arbre = json.loads(routes[url_arbre]._flux.getvalue())
    arbre[1]["lfs"]["oid"] = "0" * 64
    routes[url_arbre] = FauxReponse(200, json.dumps(arbre).encode())
    assert (
        cj.main(["sources", "--dest", str(tmp_path), "--quoi", "questions"], client=client(routes))
        != 0
    )
    assert not (
        tmp_path / "hf" / "AgentPublic" / "sp_questions_corpus" / "gpt_corpus-20kq&A.xlsx"
    ).exists()


def test_sources_force_archive_l_ancien_instantane(tmp_path):
    assert (
        cj.main(
            ["sources", "--dest", str(tmp_path), "--quoi", "questions"],
            client=client(_routes_questions()),
        )
        == 0
    )
    assert (
        cj.main(
            ["sources", "--dest", str(tmp_path), "--quoi", "questions", "--force"],
            client=client(_routes_questions(corps_sp=b"xlsx-sp-v2")),
        )
        == 0
    )
    dossier = tmp_path / "hf" / "AgentPublic" / "sp_questions_corpus"
    assert (dossier / "gpt_corpus-20kq&A.xlsx").read_bytes() == b"xlsx-sp-v2"
    sha12 = hashlib.sha256(b"xlsx-sp").hexdigest()[:12]
    archive = dossier / f"gpt_corpus-20kq&A.ancien-{sha12}.xlsx"
    assert archive.read_bytes() == b"xlsx-sp"
    index = json.loads((tmp_path / "INDEX.json").read_text(encoding="utf-8"))
    entrees = {e["chemin"]: e for e in index["fichiers"]}
    rel = "hf/AgentPublic/sp_questions_corpus/gpt_corpus-20kq&A.xlsx"
    assert entrees[rel]["sha256"] == hashlib.sha256(b"xlsx-sp-v2").hexdigest()
    ancienne = entrees[archive.relative_to(tmp_path).as_posix()]
    assert (
        ancienne["sha256"] == hashlib.sha256(b"xlsx-sp").hexdigest()
        and ancienne["remplace_par"] == rel
    )


def test_sources_fichier_present_de_taille_differente(tmp_path, capsys):
    cible = tmp_path / "hf" / "AgentPublic" / "sp_questions_corpus" / "gpt_corpus-20kq&A.xlsx"
    cible.parent.mkdir(parents=True)
    cible.write_bytes(b"tronque")
    c = client(_routes_questions())
    assert cj.main(["sources", "--dest", str(tmp_path), "--quoi", "questions"], client=c) != 0
    assert cible.read_bytes() == b"tronque" and "--force" in capsys.readouterr().err
    assert not any("/resolve/" in u for _, u in c.ouvreur.appels)


def test_sources_fichier_present_de_sha_different(tmp_path):
    cible = tmp_path / "hf" / "AgentPublic" / "sp_questions_corpus" / "gpt_corpus-20kq&A.xlsx"
    cible.parent.mkdir(parents=True)
    cible.write_bytes(b"xlsx-XX")  # même taille que b"xlsx-sp", contenu différent
    assert (
        cj.main(
            ["sources", "--dest", str(tmp_path), "--quoi", "questions"],
            client=client(_routes_questions()),
        )
        != 0
    )
    assert cible.read_bytes() == b"xlsx-XX"


def test_instantane_refuse_un_chemin_hors_dest(tmp_path):
    dest = tmp_path / "d"
    dest.mkdir()
    c = client({})
    with pytest.raises(cj.ErreurOutil):
        cj.instantane(
            c,
            dest,
            cj.charger_index(dest),
            "https://huggingface.co/x",
            dest / ".." / "x.bin",
            depot="d/x",
            revision=SHA_REV,
            force=False,
        )
    assert c.ouvreur.appels == []


def test_collision_de_pages(tmp_path):
    base = "https://www.service-public.gouv.fr/a"
    c = client({base: FauxReponse(200, b"a"), base + "/": FauxReponse(200, b"b")})
    assert cj.main(["sources", "--dest", str(tmp_path), "--page", base], client=c) == 0
    assert cj.main(["sources", "--dest", str(tmp_path), "--page", base + "/"], client=c) != 0


def test_arbre_lien_suivant_relatif():
    p1 = f"https://huggingface.co/api/datasets/d/x/tree/{SHA_REV}/dos?recursive=true"
    p2 = f"https://huggingface.co/api/datasets/d/x/tree/{SHA_REV}/dos?cursor=2"
    c = client(
        {
            p1: FauxReponse(
                200,
                json.dumps([{"type": "file", "path": "dos/a"}]).encode(),
                {"Link": f'</api/datasets/d/x/tree/{SHA_REV}/dos?cursor=2>; rel="next"'},
            ),
            p2: FauxReponse(
                200,
                json.dumps(
                    [{"type": "file", "path": "dos/b"}, {"type": "directory", "path": "s"}]
                ).encode(),
            ),
        }
    )
    assert [e["path"] for e in cj.arbre_hf(c, "d/x", SHA_REV, "dos")] == ["dos/a", "dos/b"]


def test_json_invalide_devient_erreur_outil(tmp_path):
    c = client({"https://huggingface.co/api/x": FauxReponse(200, b"<html>")})
    with pytest.raises(cj.ErreurOutil):
        c.lire_json("https://huggingface.co/api/x")
    (tmp_path / "INDEX.json").write_text("{cassé", encoding="utf-8")
    with pytest.raises(cj.ErreurOutil):
        cj.charger_index(tmp_path)
    (tmp_path / "INDEX.json").write_text("[]", encoding="utf-8")
    with pytest.raises(cj.ErreurOutil):
        cj.charger_index(tmp_path)


def test_fiche_titre_et_url_nuls(tmp_path, capsys):
    (tmp_path / "hf").mkdir()
    (tmp_path / "hf" / "sp_F1.json").write_text(
        json.dumps(
            {"rows": [{"doc_id": "F1", "chunk_index": 0, "title": None, "url": None, "text": None}]}
        ),
        encoding="utf-8",
    )
    assert cj.main(["fiche", "F1", "--dest", str(tmp_path)]) == 0
    assert capsys.readouterr().out.startswith("# F1\n")


def test_fiche_parquet_sans_colonne_attendue(tmp_path):
    duckdb = pytest.importorskip("duckdb")
    dossier = tmp_path / "hf" / "AgentPublic" / "service-public"
    dossier.mkdir(parents=True)
    con = duckdb.connect()
    con.execute(
        f"COPY (SELECT 'F1' AS doc_id) TO '{(dossier / 'x.parquet').as_posix()}' (FORMAT PARQUET)"
    )
    con.close()
    assert cj.main(["fiche", "F1", "--dest", str(tmp_path)]) == 2


def test_assembler_verdict_inconnu_bloque(tmp_path, capsys):
    _brouillon(tmp_path, "Q", [_item("Q-001"), _item("Q-002")])
    _verif(
        tmp_path,
        "Q",
        [
            {"id": "Q-001", "verdict": "rejete", "motif": "ambigu"},
            {"id": "Q-001", "verdict": "rejeté"},
        ],
    )
    assert cj.main(["assembler", "--racine", str(tmp_path)]) == 2
    assert not _sortie(tmp_path).exists()
    assert "verdict inconnu 'rejeté'" in capsys.readouterr().err


def test_assembler_verification_illisible_bloque(tmp_path):
    _brouillon(tmp_path, "Q", [_item("Q-001")])
    _verif(tmp_path, "Q", ["{cassé"])
    assert cj.main(["assembler", "--racine", str(tmp_path)]) == 2
    assert not _sortie(tmp_path).exists()


def test_assembler_bom_accepte(tmp_path):
    d = tmp_path / "eval" / "construction" / "v1.0"
    d.mkdir(parents=True)
    (d / "Q.jsonl").write_text(json.dumps(_item("Q-001")) + "\n", encoding="utf-8-sig")
    assert cj.main(["assembler", "--racine", str(tmp_path)]) == 0


def test_assembler_doublon_numerique(tmp_path, capsys):
    _brouillon(tmp_path, "Q", [_item("Q-001"), _item("Q-0001")])
    assert cj.main(["assembler", "--racine", str(tmp_path)]) == 2
    assert "dupliqué : Q-001" in capsys.readouterr().err


@pytest.mark.parametrize("identifiant", ["Q-001\n", "Q-١٢٣"])
def test_id_avec_saut_de_ligne_ou_chiffres_unicode(identifiant):
    assert cj.erreurs_identifiants([("Q", 1, {"id": identifiant})])


def test_assembler_tous_rejetes(tmp_path):
    _brouillon(tmp_path, "Q", [_item("Q-001")])
    _verif(tmp_path, "Q", [{"id": "Q-001", "verdict": "rejete", "motif": "ambigu"}])
    assert cj.main(["assembler", "--racine", str(tmp_path)]) == 2
    assert not _sortie(tmp_path).exists()


def test_assembler_force_malgre_manifest_et_couverture(tmp_path, capsys):
    _brouillon(tmp_path, "Q", [_item("Q-001"), _item("Q-002")])
    _verif(
        tmp_path,
        "Q",
        [{"id": "Q-001", "verdict": "accepte"}, {"id": "Q-009", "verdict": "accepte"}],
    )
    _sortie(tmp_path).parent.mkdir(parents=True)
    (_sortie(tmp_path).parent / "MANIFEST.json").write_text("{}", encoding="utf-8")
    assert cj.main(["assembler", "--racine", str(tmp_path), "--force"]) == 0
    assert _sortie(tmp_path).exists()
    out = capsys.readouterr().out
    assert (
        "Items sans verdict : 1 (`Q-002`)" in out and "Verdicts sans brouillon : 1 (`Q-009`)" in out
    )


def test_assembler_version_hors_dossier(tmp_path):
    _brouillon(tmp_path, "Q", [_item("Q-001")])
    assert cj.main(["assembler", "--version", "../../x", "--racine", str(tmp_path)]) == 2
    assert not list(tmp_path.rglob("items.jsonl"))


def test_composition_exclut_les_rejetes_et_liste_les_non_verifies(tmp_path, capsys):
    _brouillon(tmp_path, "Q", [_item("Q-001"), _item("Q-002"), _item("Q-003")])
    _verif(
        tmp_path,
        "Q",
        [
            {"id": "Q-001", "verdict": "rejete", "motif": "ambigu"},
            {"id": "Q-002", "verdict": "accepte"},
        ],
    )
    assert cj.main(["composition", "--racine", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "2 items retenus, 1 exclus" in out and "Items sans verdict : 1 (`Q-003`)" in out


def test_composition_rd_et_cr(tmp_path, capsys):
    _brouillon(
        tmp_path,
        "RD",
        [
            _item("RD-001", producteurs=["INSEE", "DREES"], valeurs_attendues={"n": 1}),
            _item("RD-002", producteur="INSEE"),
        ],
    )
    _brouillon(
        tmp_path,
        "CR",
        [
            _item("CR-001", entree={"consigne": "mot " * 5000, "transcription": "mot " * 3000}),
            _item("CR-002", entree={"consigne": "c", "transcription": "mot " * 4001}),
        ],
    )
    assert cj.main(["composition", "--racine", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "| RD demandes de valeurs | 5 | 1 | -4 |" in out
    assert "| RD producteurs distincts | ≥ 6 | 2 | -4 |" in out
    assert "| INSEE | 2 |" in out and "| DREES | 1 |" in out
    assert "| CR transcriptions > 4000 mots | 5 | 1 | -4 |" in out


def test_rejets_sans_verdict_valide(tmp_path, capsys):
    _verif(tmp_path, "Q", ["{cassé", {"id": "Q-001", "verdict": "peut-être"}])
    assert cj.main(["rejets", "--racine", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Aucun verdict valide." in out and "## Par motif" not in out


# -- une anomalie par branche -------------------------------------------------
FAUTE_OK = {"debut": 8, "fin": 12, "erreur": "sont", "correction": "est", "type": "accord"}


def _valide(code):
    pv = [{"url": "https://www.service-public.gouv.fr/x", "consulte_le": "2026-10-12"}]
    if code == "Q":
        return _item(
            "Q-001",
            provenance=pv,
            theme="social-autonomie",
            reponse_reference="r",
            elements_cles=["a", "b", "c"],
            sources_attendues=["https://www.service-public.gouv.fr/x"],
            sans_reponse=False,
        )
    if code == "RD":
        return _item(
            "RD-001",
            theme="collectivites",
            appels_attendus=[{"outil": "search_datasets", "regles": {}}],
            mode="connecte",
            cassettes=[],
            reponse_reference="r",
        )
    if code == "RE":
        return _item(
            "RE-001",
            theme="travail-emploi",
            entree={"document": "d"},
            points_cles_reference=["p"],
            longueur_demandee="courte",
        )
    return _item(
        "CO-001",
        entree={"texte": "Le chat sont noir."},
        fautes=[dict(FAUTE_OK)],
        texte_corrige_reference="Le chat est noir.",
    )


@pytest.mark.parametrize("code", ["Q", "RD", "RE", "CO"])
def test_items_valides_sans_anomalie(code):
    assert cj.anomalies_item(code, _valide(code)) == []


def _sans(champ):
    return lambda it: it.pop(champ)


@pytest.mark.parametrize(
    "code, modif, attendu",
    [
        ("Q", {"tache": "Questions"}, "`tache`"),
        ("Q", {"difficulte": "dur"}, "`difficulte` invalide"),
        ("Q", {"theme": "sport"}, "`theme` hors SPEC"),
        ("Q", {"entree": {"x": 1}}, "`entree` doit être un texte"),
        ("CO", {"entree": "texte"}, "`entree` doit être un objet"),
        ("Q", {"fictif": "non"}, "`fictif`"),
        ("Q", {"provenance": []}, "liste non vide"),
        (
            "Q",
            {"provenance": [{"url": "u", "consulte_le": "12/10/2026"}]},
            "`consulte_le` au format ISO",
        ),
        ("Q", {"elements_cles": ["a"]}, "3 à 5"),
        ("Q", {"sources_attendues": ["https://example.com/x"]}, "hors Liste blanche"),
        (
            "Q",
            {
                "amorce_usager": "x",
                "provenance": [
                    {"source": "autre", "consulte_le": "2026-10-12", "note": "sp_questions_corpus"}
                ],
            },
            "corpus AgentPublic",
        ),
        ("Q", {"sans_reponse": "non"}, "`sans_reponse` doit être un booléen"),
        ("Q", {"version_item": 2}, "`version_item`"),
        ("Q", _sans("parametres"), "`parametres`"),
        ("RD", {"mode": "offline"}, "`mode` invalide"),
        ("RD", {"appels_attendus": [{"outil": "get_metrics", "regles": {}}]}, "outil hors"),
        ("RD", {"appels_attendus": [{"outil": "search_datasets"}]}, "sans objet `regles`"),
        ("RE", {"longueur_demandee": "longue"}, "`longueur_demandee`"),
        (
            "CO",
            {
                "fautes": [
                    dict(FAUTE_OK),
                    {"debut": 9, "fin": 12, "erreur": "ont", "correction": "x", "type": "t"},
                ]
            },
            "chevauchent",
        ),
        ("CO", {"texte_corrige_reference": "autre"}, "ne donne pas"),
        ("CO", {"fautes": []}, "non vide"),
        ("CO", {"fautes": [FAUTE_OK | {"debut": True}]}, "position fausse"),
        (
            "CO",
            {"fautes": [{"debut": -1, "fin": 12, "erreur": "sont", "correction": "est"}]},
            "position fausse",
        ),
    ],
)
def test_anomalie_par_branche(code, modif, attendu):
    it = _valide(code)
    if callable(modif):
        modif(it)
    else:
        it.update(modif)
    anomalies = cj.anomalies_item(code, it)
    assert any(attendu in a for a in anomalies), anomalies
