"""Moteur de téléchargement et partie Hugging Face (story 2.1, matrice des cas)."""

from __future__ import annotations

import ast
import os
from datetime import UTC, datetime
from pathlib import Path

import httpx2  # noqa: TID251 (tests : exceptions du transport factice)
import pytest

from slmsp import net
from slmsp.core.artefacts import EspaceInsuffisant
from slmsp.core.erreurs import HoteBloque
from slmsp.fetch import hf
from slmsp.fetch.hf import (
    ShaInvalide,
    TelechargementEchoue,
    chemin_part,
    erreur_transport,
    lire_retry_after,
    url_hf,
)

URL = "https://huggingface.co/datasets/org/jeu/resolve/" + "a" * 40 + "/data/f.parquet"
CONTENU = bytes(range(256)) * 3  # 768 octets


def _fichiers(dossier: Path) -> list[str]:
    if not dossier.exists():
        return []
    return sorted(p.relative_to(dossier).as_posix() for p in dossier.rglob("*") if p.is_file())


# --- Nominal, idempotence, conflit ---------------------------------------------------------


def test_nominal(banc, outils, tmp_path: Path) -> None:
    banc.serveur.servir(URL, CONTENU)
    destination = tmp_path / "sortie" / "f.parquet"
    resultat = banc.telechargeur().telecharger(URL, destination, outils.sha(CONTENU), len(CONTENU))
    assert resultat.statut == "telecharge"
    assert resultat.octets == len(CONTENU) == resultat.taille
    assert resultat.sha256 == outils.sha(CONTENU)
    assert destination.read_bytes() == CONTENU
    assert _fichiers(tmp_path / "sortie") == ["f.parquet"]
    assert [(e.profil, e.hote, e.methode, e.statut) for e in banc.journal.lister()] == [
        ("outillage", "huggingface.co", "GET", "envoyee")
    ]


def test_idempotence_sans_requete(banc, outils, tmp_path: Path) -> None:
    destination = tmp_path / "f.parquet"
    destination.write_bytes(CONTENU)
    resultat = banc.telechargeur().telecharger(URL, destination, outils.sha(CONTENU))
    assert resultat.statut == "deja-present"
    assert resultat.octets == 0
    assert banc.serveur.requetes == []


def test_conflit_fichier_final_au_mauvais_sha(banc, outils, tmp_path: Path) -> None:
    destination = tmp_path / "f.parquet"
    destination.write_bytes(b"autre contenu")
    banc.serveur.servir(URL, CONTENU)
    with pytest.raises(ShaInvalide, match="rien n'est écrit"):
        banc.telechargeur().telecharger(URL, destination, outils.sha(CONTENU), len(CONTENU))
    assert destination.read_bytes() == b"autre contenu"
    assert _fichiers(tmp_path) == ["f.parquet"]
    assert banc.serveur.requetes == []


def test_sha_attendu_invalide(banc, tmp_path: Path) -> None:
    with pytest.raises(ShaInvalide):
        banc.telechargeur().telecharger(URL, tmp_path / "f", "pas-un-sha")


# --- Reprise ----------------------------------------------------------------------------


def test_reprise_par_range(banc, outils, tmp_path: Path) -> None:
    banc.serveur.servir(URL, CONTENU)
    destination = tmp_path / "f.parquet"
    chemin_part(destination).write_bytes(CONTENU[:100])
    resultat = banc.telechargeur().telecharger(URL, destination, outils.sha(CONTENU), len(CONTENU))
    (requete,) = banc.serveur.requetes
    assert requete.headers["Range"] == "bytes=100-"
    assert resultat.octets == len(CONTENU) - 100
    assert destination.read_bytes() == CONTENU
    assert not chemin_part(destination).exists()


def test_reprise_refusee_par_un_200(banc, outils, tmp_path: Path) -> None:
    banc.serveur.servir(URL, CONTENU, ignorer_range=True)
    destination = tmp_path / "f.parquet"
    chemin_part(destination).write_bytes(CONTENU[:100])
    with pytest.raises(TelechargementEchoue, match="reprise refusée"):
        banc.telechargeur().telecharger(URL, destination, outils.sha(CONTENU), len(CONTENU))
    assert chemin_part(destination).read_bytes() == CONTENU[:100]
    assert not destination.exists()


def test_part_deja_complet_sans_requete(banc, outils, tmp_path: Path) -> None:
    destination = tmp_path / "f.parquet"
    chemin_part(destination).write_bytes(CONTENU)
    resultat = banc.telechargeur().telecharger(URL, destination, outils.sha(CONTENU), len(CONTENU))
    assert resultat.statut == "telecharge" and resultat.octets == 0
    assert destination.read_bytes() == CONTENU
    assert banc.serveur.requetes == []


def test_part_complet_taille_inconnue_416(banc, outils, tmp_path: Path) -> None:
    banc.serveur.servir(URL, CONTENU, pannes=[("statut", 416, {})])
    destination = tmp_path / "f.parquet"
    chemin_part(destination).write_bytes(CONTENU)
    resultat = banc.telechargeur().telecharger(URL, destination, outils.sha(CONTENU))
    (requete,) = banc.serveur.requetes
    assert requete.headers["Range"] == f"bytes={len(CONTENU)}-"
    assert resultat.statut == "telecharge" and resultat.octets == 0
    assert destination.read_bytes() == CONTENU
    assert not chemin_part(destination).exists()


def test_content_range_decale(banc, outils, tmp_path: Path) -> None:
    banc.serveur.servir(
        URL, CONTENU, pannes=[("statut", 206, {"Content-Range": "bytes 50-767/768"})]
    )
    destination = tmp_path / "f.parquet"
    chemin_part(destination).write_bytes(CONTENU[:100])
    with pytest.raises(TelechargementEchoue, match="Content-Range incohérent"):
        banc.telechargeur().telecharger(URL, destination, outils.sha(CONTENU), len(CONTENU))
    assert chemin_part(destination).read_bytes() == CONTENU[:100]
    assert not destination.exists()


# --- Relances ---------------------------------------------------------------------------


def test_retry_after_plafonne(banc, outils, tmp_path: Path) -> None:
    banc.serveur.servir(
        URL,
        CONTENU,
        pannes=[
            ("statut", 429, {"Retry-After": "100000"}),
            ("statut", 503, {"Retry-After": "inf"}),
        ],
    )
    banc.telechargeur().telecharger(URL, tmp_path / "f", outils.sha(CONTENU))
    assert banc.attentes == [8.0, 2.0]  # plafond attente_max, puis `inf` ignoré


def test_erreur_locale_non_relancee(banc, outils, tmp_path: Path, monkeypatch) -> None:
    banc.serveur.servir(URL, CONTENU)
    original = Path.open

    def ouvrir(chemin, mode="r", *args, **kwargs):
        if str(chemin).endswith(".part") and "a" in mode:
            raise PermissionError("accès refusé")
        return original(chemin, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", ouvrir)
    with pytest.raises(PermissionError):
        banc.telechargeur().telecharger(URL, tmp_path / "f", outils.sha(CONTENU))
    assert len(banc.serveur.requetes) == 1
    assert banc.attentes == []


def test_relances_429_500_et_coupure(banc, outils, tmp_path: Path) -> None:
    banc.serveur.servir(
        URL,
        CONTENU,
        # La coupure survient après 2 blocs de 7 octets écrits.
        pannes=[("statut", 429, {"Retry-After": "3"}), 500, ("coupe", 14)],
    )
    destination = tmp_path / "f.parquet"
    resultat = banc.telechargeur().telecharger(URL, destination, outils.sha(CONTENU), len(CONTENU))
    assert destination.read_bytes() == CONTENU
    assert banc.attentes == [3.0, 2.0, 4.0]  # Retry-After respecté, puis 1 × 2^(n-1)
    assert [r.headers.get("Range") for r in banc.serveur.requetes] == [
        None,
        None,
        None,
        "bytes=14-",
    ]
    assert resultat.octets == len(CONTENU)
    assert [e.statut for e in reversed(banc.journal.lister())] == ["envoyee"] * 4


def test_attente_plafonnee(banc, outils, tmp_path: Path) -> None:
    banc.serveur.servir(URL, CONTENU, pannes=[502, 503, 504, 500])
    config = outils.reglages(essais=5, attente_initiale=3.0, attente_max=5.0)
    banc.telechargeur(config).telecharger(URL, tmp_path / "f", outils.sha(CONTENU))
    assert banc.attentes == [3.0, 5.0, 5.0, 5.0]


def test_essais_epuises(banc, outils, tmp_path: Path) -> None:
    banc.serveur.servir(URL, CONTENU, pannes=[503] * 4)
    destination = tmp_path / "f.parquet"
    with pytest.raises(TelechargementEchoue, match="4 essais"):
        banc.telechargeur().telecharger(URL, destination, outils.sha(CONTENU), len(CONTENU))
    assert len(banc.attentes) == 3
    assert _fichiers(tmp_path) == []


def test_statut_inattendu_sans_relance(banc, outils, tmp_path: Path) -> None:
    with pytest.raises(TelechargementEchoue, match="404"):
        banc.telechargeur().telecharger(URL, tmp_path / "f", outils.sha(CONTENU))
    assert len(banc.serveur.requetes) == 1
    assert banc.attentes == []


# --- SHA faux, hôte refusé ----------------------------------------------------------------


def test_sha_faux_met_de_cote_le_part(banc, outils, tmp_path: Path) -> None:
    banc.serveur.servir(URL, b"contenu altere")
    destination = tmp_path / "f.parquet"
    with pytest.raises(ShaInvalide, match="non créé"):
        banc.telechargeur().telecharger(URL, destination, outils.sha(CONTENU))
    (mis_de_cote,) = _fichiers(tmp_path)
    assert mis_de_cote.startswith("f.parquet.sha-invalide-")
    assert (tmp_path / mis_de_cote).read_bytes() == b"contenu altere"
    assert not destination.exists()
    assert not chemin_part(destination).exists()


def test_redirection_hors_regles_outillage(banc, outils, tmp_path: Path) -> None:
    banc.serveur.servir(URL, redirection="https://evil.example.com/vol")
    destination = tmp_path / "sortie" / "f.parquet"
    with pytest.raises(HoteBloque, match="evil.example.com"):
        banc.telechargeur().telecharger(URL, destination, outils.sha(CONTENU))
    assert not (tmp_path / "sortie").exists()
    assert [(e.hote, e.statut) for e in reversed(banc.journal.lister())] == [
        ("huggingface.co", "envoyee"),
        ("evil.example.com", "bloquee-liste"),
    ]


def test_redirection_vers_le_cdn_hf(banc, outils, tmp_path: Path) -> None:
    cdn = "https://cas-bridge.xethub.hf.co/xet/objet"
    banc.serveur.servir(URL, redirection=cdn)
    banc.serveur.servir(cdn, CONTENU)
    resultat = banc.telechargeur().telecharger(URL, tmp_path / "f", outils.sha(CONTENU))
    assert resultat.statut == "telecharge"
    assert [e.hote for e in reversed(banc.journal.lister())] == [
        "huggingface.co",
        "cas-bridge.xethub.hf.co",
    ]


# --- Espace disque ------------------------------------------------------------------------


def test_espace_insuffisant(banc, outils, tmp_path: Path) -> None:
    telechargeur = banc.telechargeur(outils.reglages(marge_espace=10**18))
    with pytest.raises(EspaceInsuffisant):
        telechargeur.verifier_espace_total([(tmp_path / "a", 10), (tmp_path / "b", 5)])
    assert banc.serveur.requetes == []


def test_espace_sous_le_seuil_non_verifie(banc, outils, tmp_path: Path) -> None:
    present = tmp_path / "present"
    present.write_bytes(b"x")
    chemin_part(tmp_path / "b").write_bytes(b"123")
    telechargeur = banc.telechargeur(
        outils.reglages(seuil_verification_espace=100, marge_espace=10**18)
    )
    total = telechargeur.verifier_espace_total(
        [(tmp_path / "a", 10), (tmp_path / "b", 5), (present, 50), (tmp_path / "c", None)]
    )
    assert total == 12  # 10 + (5 - 3), fichier présent et taille inconnue exclus


# --- Réutilisation locale -------------------------------------------------------------------


def test_reutilisation_par_lien(banc, outils, tmp_path: Path) -> None:
    local = tmp_path / "local" / "sous" / "copie.parquet"
    local.parent.mkdir(parents=True)
    local.write_bytes(CONTENU)
    (tmp_path / "local" / "meme-taille").write_bytes(bytes(len(CONTENU)))
    destination = tmp_path / "sortie" / "f.parquet"
    telechargeur = banc.telechargeur(reutiliser=[tmp_path / "local"])
    resultat = telechargeur.telecharger(URL, destination, outils.sha(CONTENU), len(CONTENU))
    assert resultat.statut == "reutilise"
    assert resultat.source == local
    assert resultat.octets == 0
    assert os.path.samefile(destination, local)
    assert banc.serveur.requetes == []


def test_reutilisation_par_copie(banc, outils, tmp_path: Path, monkeypatch) -> None:
    local = tmp_path / "local" / "copie.parquet"
    local.parent.mkdir()
    local.write_bytes(CONTENU)

    def lien_impossible(*_args) -> None:
        raise OSError("liens durs non pris en charge")

    monkeypatch.setattr(hf.os, "link", lien_impossible)
    destination = tmp_path / "sortie" / "f.parquet"
    telechargeur = banc.telechargeur(reutiliser=[tmp_path / "local"])
    resultat = telechargeur.telecharger(URL, destination, outils.sha(CONTENU), len(CONTENU))
    assert resultat.statut == "reutilise"
    assert destination.read_bytes() == CONTENU
    assert not os.path.samefile(destination, local)
    assert _fichiers(tmp_path / "sortie") == ["f.parquet"]


def test_sans_fichier_identique_on_telecharge(banc, outils, tmp_path: Path) -> None:
    (tmp_path / "local").mkdir()
    (tmp_path / "local" / "autre").write_bytes(bytes(len(CONTENU)))
    banc.serveur.servir(URL, CONTENU)
    telechargeur = banc.telechargeur(reutiliser=[tmp_path / "local"])
    resultat = telechargeur.telecharger(URL, tmp_path / "f", outils.sha(CONTENU), len(CONTENU))
    assert resultat.statut == "telecharge"


# --- Hugging Face -----------------------------------------------------------------------


def test_preparer_hf(monkeypatch, tmp_path: Path) -> None:
    pytest.importorskip("huggingface_hub")
    from huggingface_hub.utils import _http

    monkeypatch.setenv("SLMSP_MODELS_DIR", str(tmp_path / "models"))
    monkeypatch.delenv("HF_HUB_DISABLE_TELEMETRY", raising=False)
    assert hf.preparer_hf() is True
    assert os.environ["HF_HOME"] == str((tmp_path / "models").resolve() / ".cache-hf")
    assert os.environ["HF_HUB_DISABLE_TELEMETRY"] == "1"
    assert _http._GLOBAL_CLIENT_FACTORY is net.fabrique_hf
    assert _http._GLOBAL_ASYNC_CLIENT_FACTORY is net.fabrique_hf_async


def test_preparer_hf_sans_huggingface_hub(monkeypatch, tmp_path: Path) -> None:
    import builtins

    original = builtins.__import__

    def importer(nom, *args, **kwargs):
        if nom == "huggingface_hub":
            raise ImportError(nom)
        return original(nom, *args, **kwargs)

    monkeypatch.setenv("SLMSP_MODELS_DIR", str(tmp_path))
    monkeypatch.setattr(builtins, "__import__", importer)
    assert hf.preparer_hf() is False
    assert os.environ["HF_HOME"] == str(tmp_path.resolve() / ".cache-hf")


def test_client_hf_porte_le_jeton_seul(banc, outils, tmp_path: Path) -> None:
    cdn = "https://cas-bridge.xethub.hf.co/xet/objet"
    banc.serveur.servir(URL, redirection=cdn)
    banc.serveur.servir(cdn, CONTENU)
    client = hf.client_hf(
        "jeton-factice",
        journal=banc.journal,
        transport_interne=httpx2.MockTransport(banc.serveur),
    )
    telechargeur = hf.Telechargeur(client, outils.reglages(), attendre=banc.attentes.append)
    telechargeur.telecharger(URL, tmp_path / "f", outils.sha(CONTENU))
    premiere, seconde = banc.serveur.requetes
    assert premiere.headers["Authorization"] == "Bearer jeton-factice"
    assert "Authorization" not in seconde.headers  # retiré hors de huggingface.co
    assert "Authorization" not in hf.client_hf(None).headers


def test_jeton_hf(monkeypatch, tmp_path: Path) -> None:
    env = tmp_path / ".env"
    monkeypatch.setenv("SLMSP_ENV_FILE", str(env))
    assert hf.jeton_hf() is None  # fichier absent : accès anonyme
    env.write_text("HF_TOKEN=\n", encoding="utf-8")
    assert hf.jeton_hf() is None
    env.write_text("HF_TOKEN=hf_factice\n", encoding="utf-8")
    assert hf.jeton_hf() == "hf_factice"
    assert hf.en_tetes_hf("hf_factice") == {"Authorization": "Bearer hf_factice"}
    assert hf.en_tetes_hf(None) == {}


def test_metadonnees_hf_sans_redirection(banc, outils) -> None:
    empreinte = outils.sha(CONTENU)
    banc.serveur.servir(
        URL,
        statut_head=302,
        en_tetes_head={
            "Location": "https://cas-bridge.xethub.hf.co/x",
            "X-Linked-Size": "768",
            "X-Linked-Etag": f'"{empreinte}"',
            "X-Repo-Commit": "b" * 40,
            "Content-Length": "1234",
        },
    )
    meta = banc.telechargeur().metadonnees_hf(URL)
    assert (meta.taille, meta.sha256, meta.commit) == (768, empreinte, "b" * 40)
    assert [r.method for r in banc.serveur.requetes] == ["HEAD"]


def test_metadonnees_hf_fichier_non_lfs(banc) -> None:
    banc.serveur.servir(URL, en_tetes_head={"Content-Length": "42", "ETag": '"' + "c" * 40 + '"'})
    meta = banc.telechargeur().metadonnees_hf(URL)
    assert (meta.taille, meta.sha256, meta.commit) == (42, None, None)


def test_metadonnees_hf_relance(banc) -> None:
    fichier = banc.serveur.servir(URL, statut_head=503)
    with pytest.raises(TelechargementEchoue, match="4 essais"):
        banc.telechargeur().metadonnees_hf(URL)
    assert fichier.statut_head == 503 and len(banc.serveur.requetes) == 4


def test_url_hf() -> None:
    assert url_hf("org/jeu", "data/a b.parquet", "c" * 40, type_depot="dataset") == (
        "https://huggingface.co/datasets/org/jeu/resolve/" + "c" * 40 + "/data/a%20b.parquet"
    )
    assert url_hf("org/modele", "m.gguf", "main") == (
        "https://huggingface.co/org/modele/resolve/main/m.gguf"
    )


def test_lire_retry_after() -> None:
    maintenant = datetime(2026, 10, 12, 12, 0, 0, tzinfo=UTC)
    assert lire_retry_after(None) is None
    assert lire_retry_after("7") == 7.0
    assert lire_retry_after("-3") == 0.0
    assert lire_retry_after("Mon, 12 Oct 2026 12:00:30 GMT", maintenant) == 30.0
    assert lire_retry_after("n'importe quoi") is None
    assert lire_retry_after("inf") is None
    assert lire_retry_after("nan") is None


def test_erreur_transport() -> None:
    requete = httpx2.Request("GET", URL)
    assert erreur_transport(httpx2.ConnectError("x", request=requete))
    assert erreur_transport(httpx2.ReadTimeout("x", request=requete))
    assert erreur_transport(ConnectionResetError())
    assert erreur_transport(TimeoutError())
    assert not erreur_transport(OSError(28, "disque plein"))
    assert not erreur_transport(PermissionError())
    assert not erreur_transport(ValueError())
    assert not erreur_transport(httpx2.TooManyRedirects("x", request=requete))


# --- Garde-fous du code -----------------------------------------------------------------

INTERDITS = {
    "hf_hub_download",
    "snapshot_download",
    "subprocess",
    "system",
    "startfile",
    "Popen",
    "spawnv",
}


def test_fetch_sans_hf_hub_download_ni_sous_processus() -> None:
    dossier = Path(hf.__file__).parent
    for chemin in [*dossier.glob("*.py"), dossier.parent / "cli" / "fetch.py"]:
        arbre = ast.parse(chemin.read_text(encoding="utf-8"))
        for noeud in ast.walk(arbre):
            noms: set[str] = set()
            if isinstance(noeud, ast.Name):
                noms.add(noeud.id)
            elif isinstance(noeud, ast.Attribute):
                noms.add(noeud.attr)
            elif isinstance(noeud, (ast.Import, ast.ImportFrom)):
                noms.update(alias.name.split(".")[0] for alias in noeud.names)
                if isinstance(noeud, ast.ImportFrom) and noeud.module:
                    noms.add(noeud.module.split(".")[0])
            assert not noms & INTERDITS, f"{chemin.name}:{noeud.lineno} {noms & INTERDITS}"
        assert "datasets-server.huggingface.co" not in chemin.read_text(encoding="utf-8")
