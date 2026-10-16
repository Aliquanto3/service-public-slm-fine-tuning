"""Résolution d'un `ModeleRef` en GGUF et en configuration (story 5.3).

`SLMSP_MODELS_DIR` pointe un dossier de `tmp_path` ; les GGUF sont des octets quelconques
et le run d'export est factice (`nouveau_run("export", …)`).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from evaluation_factices import SLUG

from slmsp.core.artefacts import nouveau_run
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.evaluation.modele_ref import resoudre
from slmsp.inference.serveur import charger_config_modele


def _run_export(racine: Path, *, modele_ref: str | None = f"base:{SLUG}", statut="complet",
                type_run: str = "export", ggufs=("f16", "q4_k_m")) -> str:  # fmt: skip
    champs = {} if modele_ref is None else {"modele_ref": modele_ref}
    run = nouveau_run(type_run, f"ft-{SLUG}", {}, racine=racine, **champs)
    for quantification in ggufs:
        run.ecrire(f"modele-{quantification}.gguf", b"GGUF-factice")
    if statut is not None:
        run.terminer(statut)
    return run.manifeste.run_id


def test_base_q4_k_m(modeles: Path) -> None:
    resolu = resoudre(f"base:{SLUG}", "q4_k_m")
    config = charger_config_modele(SLUG)
    assert resolu.genre == "base"
    assert (resolu.slug, resolu.slug_run, resolu.quantification) == (SLUG, SLUG, "q4_k_m")
    assert resolu.gguf == modeles / SLUG / "gguf" / config.gguf.fichier
    assert resolu.config == config


def test_base_f16_absent_indique_la_commande_de_fetch(modeles: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match=f"fetch modeles {SLUG} --f16"):
        resoudre(f"base:{SLUG}", "f16")


def test_base_f16_present(modeles: Path) -> None:
    fichier = charger_config_modele(SLUG).gguf_f16.fichier
    (modeles / SLUG / "gguf" / fichier).write_bytes(b"GGUF-factice")
    resolu = resoudre(f"base:{SLUG}", "f16")
    assert resolu.quantification == "f16"
    assert resolu.gguf == modeles / SLUG / "gguf" / fichier


def test_base_f16_non_configure_refuse(modeles: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import slmsp.evaluation.modele_ref as module

    sans = charger_config_modele(SLUG).model_copy(update={"gguf_f16": None})
    monkeypatch.setattr(module, "charger_config_modele", lambda _slug: sans)
    with pytest.raises(ConfigurationInvalide, match="gguf_f16 absente"):
        resoudre(f"base:{SLUG}", "f16")


def test_base_gguf_absent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(tmp_path / "vide"))
    with pytest.raises(ConfigurationInvalide, match="GGUF absent"):
        resoudre(f"base:{SLUG}", "q4_k_m")


def test_base_config_absente(modeles: Path) -> None:
    with pytest.raises(ConfigurationInvalide):
        resoudre("base:modele-inconnu", "q4_k_m")


def test_modele_d_embedding_refuse(modeles: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="embedding"):
        resoudre("base:bge-m3", "q4_k_m")


def test_template_exporte_non_force(modeles: Path) -> None:
    assert charger_config_modele(SLUG).chat_template_force is False
    (modeles / SLUG / "chat_template.jinja").write_bytes(b"{{ x }}")
    with pytest.raises(ConfigurationInvalide, match="chat_template_force"):
        resoudre(f"base:{SLUG}", "q4_k_m")


@pytest.mark.parametrize("quantification", ["f16", "q4_k_m"])
def test_ft(quantification: str, tmp_path: Path, modeles: Path) -> None:
    run_id = _run_export(tmp_path)
    resolu = resoudre(f"ft:{run_id}", quantification, racine=tmp_path)
    assert resolu.genre == "ft"
    assert (resolu.slug, resolu.slug_run) == (SLUG, f"ft-{SLUG}")
    assert resolu.gguf == tmp_path / "runs" / "export" / run_id / f"modele-{quantification}.gguf"
    assert resolu.config.chat_template_force is False
    assert resolu.config.contexte == charger_config_modele(SLUG).contexte


def test_ft_ignore_le_template_exporte(tmp_path: Path, modeles: Path) -> None:
    (modeles / SLUG / "chat_template.jinja").write_bytes(b"{{ x }}")
    run_id = _run_export(tmp_path)
    assert resoudre(f"ft:{run_id}", "q4_k_m", racine=tmp_path).config.chat_template_force is False


@pytest.mark.parametrize(
    ("options", "motif"),
    [
        ({"statut": None}, "pas complet"),
        ({"statut": "interrompu"}, "pas complet"),
        ({"modele_ref": None}, "Modèle de base"),
        ({"modele_ref": "ft:20261012-120000-granite-4.0-1b-abcd"}, "Modèle de base"),
        ({"type_run": "train"}, "type"),
        ({"ggufs": ("f16",)}, "GGUF absent"),
    ],
)
def test_ft_refuse(options: dict, motif: str, tmp_path: Path, modeles: Path) -> None:
    run_id = _run_export(tmp_path, **options)
    with pytest.raises(ConfigurationInvalide, match=motif):
        resoudre(f"ft:{run_id}", "q4_k_m", racine=tmp_path)


def test_ft_run_absent(tmp_path: Path, modeles: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="illisible"):
        resoudre("ft:20261012-120000-granite-4.0-1b-abcd", "q4_k_m", racine=tmp_path)


@pytest.mark.parametrize(
    ("ref", "quantification"),
    [
        ("granite", "q4_k_m"),
        ("base:Granite", "q4_k_m"),
        ("ft:abc", "q4_k_m"),
        (f"base:{SLUG}", "q8_0"),
    ],
)
def test_usage_invalide(ref: str, quantification: str, modeles: Path) -> None:
    with pytest.raises(ValueError):
        resoudre(ref, quantification)
