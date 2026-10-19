"""Story 12.15 : modèle actif (réglage `modele`) et choix dans le pont Réglages."""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.app.modele_actif import gguf_present, resoudre_modele_actif
from slmsp.app.pont.reglages import CODE_INVALIDE, PontReglages
from slmsp.app.stockage import Stockage
from slmsp.core.schemas.config_application import charger_config_application
from slmsp.inference.serveur import charger_config_modele

AUTRE = "granite-4.0-350m"


@pytest.fixture
def config():
    c = charger_config_application()
    assert AUTRE in c.modeles_embarques and c.modele != AUTRE
    return c


def _poser_gguf(dossier: Path, slug: str) -> None:
    nom = Path(charger_config_modele(slug).gguf.fichier).name
    cible = dossier / slug / "gguf" / nom
    cible.parent.mkdir(parents=True)
    cible.write_bytes(b"<gguf-factice>")


def test_reglage_valide(config, tmp_path: Path) -> None:
    _poser_gguf(tmp_path, AUTRE)
    assert resoudre_modele_actif(config, AUTRE, tmp_path) == AUTRE


def test_reglage_absent(config, tmp_path: Path) -> None:
    assert resoudre_modele_actif(config, None, tmp_path) == config.modele


def test_reglage_hors_liste(config, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level("WARNING"):
        assert resoudre_modele_actif(config, "qwen-4b", tmp_path) == config.modele
        assert resoudre_modele_actif(config, 42, tmp_path) == config.modele
    assert "ignoré" in caplog.text


def test_gguf_absent(config, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level("WARNING"):
        assert resoudre_modele_actif(config, AUTRE, tmp_path) == config.modele
    assert "absent" in caplog.text


def test_pont_ecrit_le_choix(tmp_path: Path, config) -> None:
    stock = Stockage(tmp_path / "a.sqlite")
    pont = PontReglages(stock, modele_actif=config.modele)
    assert pont.ecrire("modele", AUTRE) == {"ok": True}
    assert stock.lire_reglage("modele") == AUTRE


def test_pont_refuse_un_modele_non_embarque(tmp_path: Path) -> None:
    stock = Stockage(tmp_path / "a.sqlite")
    r = PontReglages(stock).ecrire("modele", "qwen-4b")
    assert r["ok"] is False and r["erreur"]["code"] == CODE_INVALIDE
    assert stock.lire_reglage("modele") is None


def test_pont_liste_les_modeles(tmp_path: Path, config) -> None:
    stock = Stockage(tmp_path / "a.sqlite")
    r = PontReglages(stock, modele_actif=config.modele).modeles()
    assert [m["slug"] for m in r["modeles"]] == config.modeles_embarques
    assert r["actif"] == config.modele and r["choisi"] == config.modele


def test_template_force_absent(config, tmp_path: Path) -> None:
    """Un modèle à `chat_template_force` sans son template n'est pas retenu (12.15, revue)."""
    slug = "minicpm5-2b"
    assert charger_config_modele(slug).chat_template_force
    _poser_gguf(tmp_path, slug)
    assert not gguf_present(slug, tmp_path)
    (tmp_path / slug / "chat_template.jinja").write_text("<t>", encoding="utf-8")
    assert gguf_present(slug, tmp_path)
