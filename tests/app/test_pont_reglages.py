"""Story 12.10 : domaine `reglages` du pont (réglages, effacement, « À propos »)."""

from __future__ import annotations

import json
import tomllib
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from slmsp.app.pont.erreurs import NonImplementee
from slmsp.app.pont.reglages import PontReglages
from slmsp.app.stockage import Stockage
from slmsp.core.schemas.manifeste_index import ManifesteIndex, SourceManifeste

HEX = "a" * 64


@pytest.fixture
def stockage(tmp_path: Path) -> Stockage:
    return Stockage(tmp_path / "a.sqlite")


def _racine(tmp_path: Path, hotes: list[str], version: str | None = "20260101") -> Path:
    racine = tmp_path / "racine"
    (racine / "config").mkdir(parents=True)
    (racine / "config" / "liste-blanche.toml").write_text(
        "hotes = [" + ", ".join(f'"{h}"' for h in hotes) + "]\n", encoding="utf-8"
    )
    if version:
        dossier = racine / "index" / version
        dossier.mkdir(parents=True)
        manifeste = ManifesteIndex(
            version=version,
            date_snapshot=date(2026, 1, 1),
            cree_le=datetime(2026, 1, 2, tzinfo=UTC),
            modele_embedding="<embedding-factice>",
            colonne_vecteurs="<colonne-factice>",
            dimension=4,
            nb_chunks=7,
            sources=[
                SourceManifeste(
                    nom="<source-factice>",
                    jeu="<jeu-factice>",
                    revision="b" * 40,
                    date_snapshot=date(2026, 1, 1),
                    nb_chunks=7,
                    nb_ecartes=0,
                    parquet={"<fichier-factice>": HEX},
                )
            ],
            fichiers={"<fichier-factice>": HEX},
        )
        (dossier / "MANIFEST.json").write_text(manifeste.model_dump_json(), encoding="utf-8")
    return racine


def test_lire_defaut_et_ecrire_taille(stockage: Stockage) -> None:
    pont = PontReglages(stockage)
    assert pont.appeler("lire")["reglages"] == {"taille_texte": 100, "hors_ligne_force": False}
    assert pont.appeler("ecrire", "taille_texte", 125) == {"ok": True}
    assert PontReglages(stockage).lire()["reglages"]["taille_texte"] == 125


@pytest.mark.parametrize(
    ("cle", "valeur"),
    [
        ("taille_texte", 130),
        ("taille_texte", True),
        ("taille_texte", 112.0),
        ("taille_texte", "125"),
        ("fenetre", 100),
    ],
)
def test_ecrire_refuse_cle_ou_valeur_invalide(stockage: Stockage, cle: str, valeur: object) -> None:
    reponse = PontReglages(stockage).ecrire(cle, valeur)
    assert reponse["ok"] is False
    assert reponse["erreur"]["code"] == "reglage-invalide"
    assert stockage.lire_reglage("taille_texte") == "normale"


def test_effacer_historique_vide_le_stockage(stockage: Stockage) -> None:
    stockage.enregistrer_conversation(tache="Q", messages=[{"role": "user", "content": "<x>"}])
    stockage.ecrire_reglage("taille_texte", 137)
    assert PontReglages(stockage).appeler("effacer_historique") == {"ok": True}
    assert stockage.lister_conversations() == []
    assert stockage.lire_reglage("taille_texte") == 137  # les réglages restent


def test_sans_stockage_et_methode_inconnue() -> None:
    with pytest.raises(NonImplementee):
        PontReglages().appeler("lire")
    with pytest.raises(NonImplementee):
        PontReglages().appeler("inconnue")


def test_a_propos_complet(tmp_path: Path) -> None:
    racine = _racine(tmp_path, ["a.example", "b.example"])
    ressources = tmp_path / "res"
    ressources.mkdir()
    (ressources / "licences-tierces.json").write_text(
        json.dumps({"statut": "provisoire", "composants": [{"nom": "<c>", "licence": "<l>"}]}),
        encoding="utf-8",
    )
    (ressources / "empreinte-application.txt").write_text(HEX + "\n", encoding="utf-8")
    r = PontReglages(racine=racine, ressources=ressources, version=lambda: "9.9.9").a_propos()
    assert r["ok"] is True
    assert r["application"] == {"version": "9.9.9", "empreinte": HEX}
    assert r["index"] == {"version": "20260101", "date_snapshot": "2026-01-01", "nb_chunks": 7}
    assert r["liste_blanche"] == ["a.example", "b.example"]
    assert r["licences"]["composants"] == [{"nom": "<c>", "licence": "<l>"}]
    assert r["modele"]["slug"] == "minicpm5-2b"
    assert len(r["modele"]["sha256_attendu"]) == 64
    assert r["mentions"]["avertissement_juridique"] == "Ne vaut pas avis juridique."
    assert any("WebView2" in e["composant"] for e in r["hors_passerelle"])


def test_a_propos_liste_blanche_relue_a_chaque_appel(tmp_path: Path) -> None:
    racine = _racine(tmp_path, ["a.example"])
    pont = PontReglages(racine=racine)
    assert pont.a_propos()["liste_blanche"] == ["a.example"]
    (racine / "config" / "liste-blanche.toml").write_text(
        'hotes = ["a.example", "c.example"]\n', encoding="utf-8"
    )
    assert pont.a_propos()["liste_blanche"] == ["a.example", "c.example"]


def test_a_propos_valeurs_absentes_sans_erreur(tmp_path: Path) -> None:
    racine = _racine(tmp_path, ["a.example"], version=None)
    (racine / "config" / "liste-blanche.toml").write_text("invalide = [", encoding="utf-8")
    vide = tmp_path / "vide"
    vide.mkdir()
    r = PontReglages(racine=racine, ressources=vide, version=lambda: None).a_propos()
    assert r["ok"] is True
    assert r["application"] == {"version": None, "empreinte": None}
    assert r["index"] is None
    assert r["liste_blanche"] == []
    assert r["licences"] == {"statut": None, "note": None, "composants": []}


def test_a_propos_manifeste_corrompu_ignore(tmp_path: Path) -> None:
    racine = _racine(tmp_path, ["a.example"])
    (racine / "index" / "20260101" / "MANIFEST.json").write_text("{", encoding="utf-8")
    assert PontReglages(racine=racine).a_propos()["index"] is None


def test_licences_versionnees_confrontees_au_depot() -> None:
    racine = Path(__file__).resolve().parents[2]
    licences = PontReglages().a_propos()["licences"]
    assert licences["statut"] == "provisoire"
    brut = json.loads(
        (racine / "src/slmsp/app/ressources/licences-tierces.json").read_text(encoding="utf-8")
    )
    registre = {
        s["id"]: s
        for s in tomllib.loads((racine / "data/registre-licences.toml").read_text("utf-8"))[
            "sources"
        ]
    }
    pyproject = (racine / "pyproject.toml").read_text(encoding="utf-8")
    noms = {c["nom"] for c in brut["composants"]}
    for attendu in ("llama.cpp", "Granite", "BGE-M3", "pywebview", "PyInstaller", "WebView2"):
        assert any(attendu in n for n in noms), attendu
    assert "pywebview" in pyproject and "pyinstaller" in pyproject
    sourcees = 0
    for c in brut["composants"]:
        if c["source"] is None:  # aucune attestation dans le dépôt : jamais présenté comme certain
            assert c["licence"].startswith("à vérifier"), c["nom"]
            continue
        sourcees += 1
        source = registre[c["source"].removeprefix("registre:")]
        assert source["licence"] == "etalab-2.0"
        assert "Etalab 2.0" in c["licence"] and "attribution" in c["licence"]
    ids = {c["source"] for c in brut["composants"]}
    assert {
        "registre:AgentPublic/service-public",
        "registre:AgentPublic/data-gouv-datasets-catalog",
    } <= ids
    # le pont expose bien ce contenu
    assert {c["nom"] for c in licences["composants"]} == noms
    assert sourcees == 2


def test_effacer_historique_oublie_le_dernier_envoi(stockage: Stockage) -> None:
    oublies: list[bool] = []
    pont = PontReglages(stockage, apres_effacement=lambda: oublies.append(True))
    pont.effacer_historique()
    assert oublies == [True]


def test_langues_traduction_lues_dans_la_configuration(stockage: Stockage) -> None:
    """Story 13.4 : les langues de la vue Traduction viennent de `config/application.toml`."""
    from slmsp.core.schemas.config_application import charger_config_application

    reponse = PontReglages(stockage).appeler("langues_traduction")
    assert reponse == {"ok": True, "langues": charger_config_application().langues_traduction}
