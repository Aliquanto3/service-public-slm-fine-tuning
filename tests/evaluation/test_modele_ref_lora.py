"""Référence `lora:<export_lora_run_id>[@<échelle>]` (story 15.6) : résolution, échelle
(consignée dans la référence et dans le run), refus, génération et `measure run`.

Le run d'export LoRA est factice (`nouveau_run("export-lora", …)`, GGUF d'octets factices).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pytest
from evaluation_factices import SLUG
from pydantic import TypeAdapter

from slmsp.cli import measure as cli_measure
from slmsp.core.artefacts import nouveau_run, ouvrir_run
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas.run import ModeleRef
from slmsp.evaluation.generation import lancer_generation
from slmsp.evaluation.modele_ref import composer_lora, echelle_lora_de, resoudre
from slmsp.inference.serveur import Lora, ServeurLlama, charger_config_modele

ID_FACTICE = "20261021-120000-lora-granite-4.0-1b-abcd"


def _run_lora(
    racine: Path,
    *,
    statut: str | None = "complet",
    fichier: bool = True,
    type_run: str = "export-lora",
    modele_ref: str | None = f"base:{SLUG}",
) -> str:
    champs = {} if modele_ref is None else {"modele_ref": modele_ref}
    run = nouveau_run(type_run, f"lora-{SLUG}", {}, racine=racine, **champs)
    if fichier:
        run.ecrire("adaptateur-lora.gguf", b"GGUF-lora-factice")
    if statut is not None:
        run.terminer(statut)
    return run.manifeste.run_id


def test_reference_valide_par_le_schema() -> None:
    adaptateur = TypeAdapter(ModeleRef)
    for ref in (f"lora:{ID_FACTICE}", f"lora:{ID_FACTICE}@0.5", f"lora:{ID_FACTICE}@1"):
        assert adaptateur.validate_python(ref) == ref
    for ref in (f"lora:{ID_FACTICE}@", f"lora:{ID_FACTICE}@-1", "lora:x", f"lora:{ID_FACTICE}@a"):
        with pytest.raises(ValueError):
            adaptateur.validate_python(ref)


@pytest.mark.parametrize(
    ("ref", "echelle", "attendu"),
    [
        (f"lora:{ID_FACTICE}", None, f"lora:{ID_FACTICE}@1"),
        (f"lora:{ID_FACTICE}", 0.5, f"lora:{ID_FACTICE}@0.5"),
        (f"lora:{ID_FACTICE}@0.5", None, f"lora:{ID_FACTICE}@0.5"),
        (f"lora:{ID_FACTICE}@0.5", 0.5, f"lora:{ID_FACTICE}@0.5"),
        (f"base:{SLUG}", None, f"base:{SLUG}"),
    ],
)
def test_composer_lora(ref: str, echelle: float | None, attendu: str) -> None:
    assert composer_lora(ref, echelle) == attendu


@pytest.mark.parametrize(
    ("ref", "echelle", "motif"),
    [
        (f"lora:{ID_FACTICE}@0.5", 0.7, "contradictoire"),
        (f"lora:{ID_FACTICE}", 0.0, "invalide"),
        (f"lora:{ID_FACTICE}", float("nan"), "invalide"),
        (f"lora:{ID_FACTICE}", 4.5, "<= 4"),
        (f"lora:{ID_FACTICE}", 1e-05, "décimales"),
        (f"lora:{ID_FACTICE}", 0.12345, "décimales"),
        (f"lora:{ID_FACTICE}@1e-05", None, "décimales"),
        (f"base:{SLUG}", 0.5, "réservé"),
    ],
)
def test_composer_lora_refuse(ref: str, echelle: float | None, motif: str) -> None:
    with pytest.raises(ValueError, match=motif):
        composer_lora(ref, echelle)


def test_echelle_lora_de() -> None:
    assert echelle_lora_de(f"lora:{ID_FACTICE}") == 1.0
    assert echelle_lora_de(f"lora:{ID_FACTICE}@0.25") == 0.25
    assert echelle_lora_de(f"base:{SLUG}") is None


def test_resolution_nominale(modeles: Path, tmp_path: Path) -> None:
    run_id = _run_lora(tmp_path)
    resolu = resoudre(f"lora:{run_id}@0.5", "q4_k_m", racine=tmp_path)
    config = charger_config_modele(SLUG)
    assert resolu.genre == "lora" and resolu.ref == f"lora:{run_id}@0.5"
    assert (resolu.slug, resolu.slug_run, resolu.quantification) == (SLUG, f"lora-{SLUG}", "q4_k_m")
    assert resolu.gguf == modeles / SLUG / "gguf" / config.gguf.fichier  # base officielle
    assert resolu.lora == tmp_path / "runs" / "export-lora" / run_id / "adaptateur-lora.gguf"
    assert resolu.echelle_lora == 0.5 and resolu.precision == "q4_k_m"
    assert resolu.config == config  # template de la base inchangé


def test_echelle_par_defaut_normalisee_dans_la_reference(modeles: Path, tmp_path: Path) -> None:
    run_id = _run_lora(tmp_path)
    resolu = resoudre(f"lora:{run_id}", "q4_k_m", racine=tmp_path)
    assert (resolu.ref, resolu.echelle_lora) == (f"lora:{run_id}@1", 1.0)


def test_f16_refuse(modeles: Path, tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="q4_k_m"):
        resoudre(f"lora:{_run_lora(tmp_path)}", "f16", racine=tmp_path)


@pytest.mark.parametrize(
    ("options", "motif"),
    [
        ({"type_run": "export"}, "pas 'export-lora'"),
        ({"statut": "partiel-erreur"}, "partiel-erreur"),
        ({"statut": "degrade"}, "degrade"),
        ({"fichier": False}, "LoRA GGUF absent"),
        ({"modele_ref": None}, "sans Modèle de base"),
    ],
)
def test_runs_refuses(modeles: Path, tmp_path: Path, options: dict[str, Any], motif: str) -> None:
    run_id = _run_lora(tmp_path, **options)
    with pytest.raises(ConfigurationInvalide, match=motif):
        resoudre(f"lora:{run_id}", "q4_k_m", racine=tmp_path)


def test_run_degrade_accepte_explicitement(modeles: Path, tmp_path: Path) -> None:
    run_id = _run_lora(tmp_path, statut="degrade")
    assert resoudre(f"lora:{run_id}", "q4_k_m", racine=tmp_path, accepter_degrade=True).lora


def test_run_introuvable(modeles: Path, tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="illisible"):
        resoudre(f"lora:{ID_FACTICE}", "q4_k_m", racine=tmp_path)


# --- Génération : l'échelle et l'adaptateur sont consignés dans le run -----------------------


def test_run_de_generation_consigne_echelle_et_adaptateur(
    depot_eval: Path, modeles: Path, fabrique: Any
) -> None:
    run_id = _run_lora(depot_eval)
    rapport = lancer_generation(
        f"lora:{run_id}@0.5",
        "q4_k_m",
        "v1.0",
        items=["Q-001"],
        racine=depot_eval,
        fabrique=fabrique,
    )
    brut = json.loads((rapport.run.dossier / "run.json").read_text(encoding="utf-8"))
    assert brut["modele_ref"] == f"lora:{run_id}@0.5"
    assert brut["config"]["lora"] == {"echelle": 0.5, "gguf": "adaptateur-lora.gguf"}
    assert brut["config"]["precision_gguf"] == "q4_k_m"
    assert brut["quantification"] == "q4_k_m"
    ((modele, _variante, _racine),) = fabrique.appels
    assert modele.echelle_lora == 0.5
    assert ouvrir_run(rapport.run.run_id, racine=depot_eval).statut_courant() == "complet"


def test_run_de_base_sans_cle_lora(depot_eval: Path, modeles: Path, fabrique: Any) -> None:
    rapport = lancer_generation(
        f"base:{SLUG}", "q4_k_m", "v1.0", items=["Q-001"], racine=depot_eval, fabrique=fabrique
    )
    assert "lora" not in rapport.run.manifeste.config


def test_harnais_reel_passe_le_lora_au_serveur(
    modeles: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`ouvrir_harnais` construit le serveur de génération avec `Lora(gguf, échelle)`."""
    from slmsp.evaluation import assemblage

    run_id = _run_lora(tmp_path)
    resolu = resoudre(f"lora:{run_id}@0.5", "q4_k_m", racine=tmp_path)
    construits: list[dict[str, Any]] = []

    class Arret(Exception):
        pass

    def faux(self: ServeurLlama, config: Any, variante: str, **options: Any) -> None:
        construits.append(options)
        raise Arret

    monkeypatch.setattr(ServeurLlama, "__init__", faux)
    with pytest.raises(Arret), assemblage.ouvrir_harnais(resolu, "cpu", tmp_path):
        pass
    assert construits[0]["lora"] == Lora(resolu.lora, 0.5)
    assert construits[0]["gguf"] == resolu.gguf


# --- measure run ------------------------------------------------------------------------------


def _args(modele: str, echelle: float | None) -> argparse.Namespace:
    return argparse.Namespace(modele=modele, echelle_lora=echelle)


def test_measure_resout_la_reference_lora(modeles: Path, tmp_path: Path) -> None:
    run_id = _run_lora(tmp_path)
    ref, servi, lora = cli_measure._modele_et_lora(_args(f"lora:{run_id}", 0.5), tmp_path)
    assert ref == f"lora:{run_id}@0.5"
    assert servi == f"base:{SLUG}"
    assert lora == Lora(tmp_path / "runs" / "export-lora" / run_id / "adaptateur-lora.gguf", 0.5)


def test_measure_base_inchange(tmp_path: Path) -> None:
    assert cli_measure._modele_et_lora(_args(f"base:{SLUG}", None), tmp_path) == (
        f"base:{SLUG}",
        f"base:{SLUG}",
        None,
    )


def test_measure_echelle_sans_lora_refusee(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="réservé"):
        cli_measure._modele_et_lora(_args(f"base:{SLUG}", 0.5), tmp_path)


# --- CLI eval run -----------------------------------------------------------------------------


def test_cli_eval_run_echelle_lora(
    depot_eval: Path, modeles: Path, fabrique: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    from slmsp.cli import main
    from slmsp.core.erreurs import CodeSortie
    from slmsp.evaluation import assemblage

    monkeypatch.setattr(assemblage, "ouvrir_harnais", fabrique)
    run_id = _run_lora(depot_eval)
    commande = ["eval", "run", "--phase", "generation", "--quantification", "q4_k_m"]
    commande += ["--jeu", "v1.0", "--items", "Q-001", "--racine", str(depot_eval)]
    assert main([*commande, "--modele", f"lora:{run_id}", "--echelle-lora", "0.5"]) == (
        CodeSortie.SUCCES
    )
    ((modele, _, _),) = fabrique.appels
    assert modele.ref == f"lora:{run_id}@0.5" and modele.echelle_lora == 0.5
    # Sans --echelle-lora : échelle 1.0 consignée ; échelle contradictoire ou hors lora : usage.
    assert main([*commande, "--modele", f"lora:{run_id}"]) == CodeSortie.SUCCES
    assert fabrique.appels[1][0].ref == f"lora:{run_id}@1"
    contradiction = [*commande, "--modele", f"lora:{run_id}@0.5", "--echelle-lora", "0.7"]
    assert main(contradiction) == CodeSortie.USAGE
    assert main([*commande, "--modele", f"base:{SLUG}", "--echelle-lora", "0.5"]) == (
        CodeSortie.USAGE
    )
    assert main([*commande, "--modele", f"lora:{run_id}", "--echelle-lora", "0"]) == (
        CodeSortie.USAGE
    )


def test_measure_compte_le_lora_parmi_les_composants(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from types import SimpleNamespace

    from slmsp.core.schemas.config_llamacpp import ConfigLlamacpp

    monkeypatch.setenv("SLMSP_VENDOR_DIR", str(tmp_path))
    (tmp_path / "llama.cpp" / "b1" / "bin-cpu").mkdir(parents=True)
    asset = {"nom": "a.zip", "sha256": "0" * 64}
    cfg = ConfigLlamacpp.model_validate(
        {"tag": "b1", "assets": {"cpu": asset, "cuda": asset, "cudart": asset}}
    )
    lora = Lora(tmp_path / "adaptateur-lora.gguf", 0.5)
    serveur = SimpleNamespace(
        role="generation", gguf=tmp_path / "base.gguf", lora=lora, config_llamacpp=cfg
    )
    assert cli_measure._composants([serveur], tmp_path, None)["lora"] == lora.gguf
