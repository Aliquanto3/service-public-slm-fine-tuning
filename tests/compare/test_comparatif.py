"""Comparatif (story 11.1) : contenu, chemin no-go, vues, régénération, imports."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from slmsp.cli import main
from slmsp.compare.chargement import JeuDeveloppement, JeuMelange, charger
from slmsp.compare.comparatif import charger_config, evaluer_sm1, rendre_comparatif

from .conftest import (
    EXPORT_M1,
    M1,
    ecrire_bench,
    ecrire_entrainement,
    ecrire_notation,
    ecrire_run,
    run_id,
)

ATTENDU = Path(__file__).parent / "fixtures" / "comparatif-attendu.md"


def _rendu(racine: Path, **kw: str) -> str:
    return rendre_comparatif(charger(racine, "camp-test", **kw), charger_config(racine))


def test_instantane(campagne_complete: Path) -> None:
    assert _rendu(campagne_complete) == ATTENDU.read_text(encoding="utf-8")


def test_gain_cout_benchmarks_et_sm1(campagne_complete: Path) -> None:
    rapport = _rendu(campagne_complete)
    assert "| Q | 40.0 | 52.0 | +12.0 | 51.0 | +11.0 |" in rapport
    assert "| arc | acc = 49.0 | -1.0 | acc = 48.5 | -0.5 |" in rapport
    assert "3600 s" in rapport and "4.00 Go" in rapport and "250.5 Wh" in rapport
    donnees = charger(campagne_complete, "camp-test")
    sm1 = evaluer_sm1(donnees, charger_config(campagne_complete), M1)
    assert sm1.verdict == "satisfait" and sm1.quantification == "q4_k_m"
    assert "candidat au Modèle embarqué" in rapport


def test_derogation_orpo_et_vues(campagne_complete: Path) -> None:
    rapport = _rendu(campagne_complete)
    assert "Dérogation au protocole : M4 (ORPO)" in rapport
    assert "(hors protocole)" in rapport
    assert "Point de comparaison : 1500 tokens" in rapport
    assert "Point de comparaison : 900 s" in rapport
    assert "Méthode et limites" in rapport and "non relus" in rapport


def test_vue_a_completer_sans_evaluation_intermediaire(racine: Path) -> None:
    ecrire_entrainement(racine, M1, "qlora", couts={"duree_s": 10.0})
    rapport = _rendu(racine)
    assert rapport.count("à compléter : aucune évaluation intermédiaire archivée.") == 2


def test_methode_sans_evaluation_marquee_a_completer(campagne_complete: Path) -> None:
    ecrire_entrainement(campagne_complete, run_id("20261001-150000", "m2-lora", "5555"), "lora")
    rapport = _rendu(campagne_complete)
    assert "| M2 (lora, run 20261001-150000-m2-lora-5555) | à compléter |" in rapport


def test_chemin_no_go_sans_aucun_modele_fine_tune(racine: Path) -> None:
    ecrire_notation(
        racine, run_id("20261001-090000", "base-granite"), "base:granite",
        {"Q": 40.0, "RD": 50.0, "CR": 30.0, "LC": 45.0}, quantification="q4_k_m",
    )  # fmt: skip
    rapport = _rendu(racine)
    assert "chemin no-go" in rapport
    assert "Meilleure Baseline livrable : `base:granite (q4_k_m)`" in rapport
    assert "5 Go (cible 4 Go, NFR-1) : non vérifié" in rapport
    assert "non mesuré" in rapport


def test_no_go_sans_baseline_ni_run(racine: Path) -> None:
    rapport = _rendu(racine)
    assert "Meilleure Baseline livrable : indéterminée" in rapport


def test_baseline_no_go_exige_couverture_complete_et_quantification_livrable(
    racine: Path,
) -> None:
    ecrire_notation(
        racine, run_id("20261001-090000", "base-a"), "base:a", {"Q": 90.0},
        quantification="q4_k_m",
    )  # fmt: skip
    ecrire_notation(
        racine, run_id("20261001-090100", "base-c", "1111"), "base:c",
        {"Q": 99.0, "RD": 99.0, "CR": 99.0, "LC": 99.0}, quantification="f16",
    )  # fmt: skip
    ecrire_notation(
        racine, run_id("20261001-090200", "base-b", "2222"), "base:b",
        {"Q": 80.0, "RD": 80.0, "CR": 80.0, "LC": 80.0}, quantification="q4_k_m",
    )  # fmt: skip
    rapport = _rendu(racine)
    assert "Meilleure Baseline livrable : `base:b (q4_k_m)` (moyenne 80.0" in rapport


def test_baselines_par_quantification_sans_composite(racine: Path) -> None:
    ecrire_notation(
        racine, run_id("20261001-090000", "base-g"), "base:granite", {"Q": 70.0},
        quantification="f16",
    )  # fmt: skip
    ecrire_notation(
        racine, run_id("20261001-090100", "base-g", "1111"), "base:granite", {"Q": 60.0},
        quantification="q4_k_m",
    )  # fmt: skip
    donnees = charger(racine, "camp-test")
    assert donnees.baselines[("base:granite", "f16")].taches["Q"].score == 70.0
    assert donnees.baselines[("base:granite", "q4_k_m")].taches["Q"].score == 60.0
    assert "| Q | 70.0 | base:granite (f16) |" in _rendu(racine)


def test_indetermine_suspend_la_recommandation(racine: Path) -> None:
    ecrire_entrainement(racine, M1, "qlora")
    rapport = _rendu(racine)
    assert "**Recommandation suspendue.**" in rapport
    assert "**Recommandation (chemin no-go).**" not in rapport


def test_no_go_quand_toutes_les_methodes_sont_non_satisfaites(racine: Path) -> None:
    ecrire_notation(
        racine, run_id("20261001-090000", "base-granite"), "base:granite",
        {"Q": 40.0, "RD": 50.0, "CR": 30.0, "LC": 45.0, "NR": 60.0}, quantification="q4_k_m",
    )  # fmt: skip
    ecrire_entrainement(racine, M1, "qlora")
    ecrire_run(racine, "export", EXPORT_M1, parents=(M1,))
    ecrire_notation(
        racine, run_id("20261001-130000", "ft-q4", "2222"), f"ft:{EXPORT_M1}",
        {"Q": 41.0, "NR": 50.0}, quantification="q4_k_m",
    )  # fmt: skip
    rapport = _rendu(racine)
    assert "**Recommandation (chemin no-go).**" in rapport
    assert "Meilleure Baseline livrable : `base:granite (q4_k_m)`" in rapport


def test_benchmark_sans_metrique_configuree_non_comparable(campagne_complete: Path) -> None:
    for i, (ref, valeur) in enumerate((("base:granite", 0.5), (f"ft:{EXPORT_M1}", 0.1))):
        ecrire_bench(
            campagne_complete, run_id("20261001-141000", "bench-x", f"77{i}0"), ref,
            "inconnu", "apres", valeur,
        )  # fmt: skip
    rapport = _rendu(campagne_complete)
    assert "| inconnu | métrique non configurée | non comparable |" in rapport
    sm1 = evaluer_sm1(
        charger(campagne_complete, "camp-test"), charger_config(campagne_complete), M1
    )
    assert sm1.verdict == "indéterminé"
    assert "Benchmarks non comparables : inconnu" in sm1.raisons


def test_statut_du_jeu_rapporte(campagne_complete: Path) -> None:
    assert "(statut : relu)" in _rendu(campagne_complete)


def test_modele_fine_tune_insuffisant_donne_no_go(campagne_complete: Path) -> None:
    ecrire_notation(
        campagne_complete, run_id("20261002-130100", "ft-q4", "6666"), f"ft:{EXPORT_M1}",
        {"Q": 41.0, "RD": 62.0, "CR": 33.0, "LC": 46.0, "NR": 58.0}, quantification="q4_k_m",
    )  # fmt: skip
    rapport = _rendu(campagne_complete)
    assert "| non satisfait |" in rapport
    # M4 n'a aucune évaluation : SM-1 indéterminé, le no-go n'est pas encore établi.
    assert "**Recommandation suspendue.**" in rapport and "M4" in rapport


def test_run_non_complet_exclu_et_signale(campagne_complete: Path) -> None:
    ecrire_run(
        campagne_complete, "train", run_id("20261001-160000", "m3-dora", "7777"),
        statut="interrompu", config={"campagne": "camp-test", "methode": "dora"},
    )  # fmt: skip
    donnees = charger(campagne_complete, "camp-test")
    assert "20261001-160000-m3-dora-7777" not in donnees.entrainements
    assert "statut interrompu" in rendre_comparatif(donnees, charger_config(campagne_complete))


def test_notation_la_plus_recente_par_generation(campagne_complete: Path) -> None:
    ecrire_notation(
        campagne_complete, run_id("20261001-090000", "base-granite", "9999"), "base:granite",
        {"Q": 1.0}, quantification="q4_k_m", generation="g-ancienne",
    )  # fmt: skip
    ecrire_notation(
        campagne_complete, run_id("20261003-090000", "base-granite", "9998"), "base:granite",
        {"Q": 41.0}, quantification="q4_k_m", generation="g-ancienne",
    )  # fmt: skip
    donnees = charger(campagne_complete, "camp-test")
    assert donnees.baselines[("base:granite", "q4_k_m")].taches["Q"].score == 41.0


def test_deux_versions_du_jeu_jamais_melangees(campagne_complete: Path) -> None:
    ecrire_notation(
        campagne_complete, run_id("20261004-090000", "base-granite", "8888"), "base:granite",
        {"Q": 70.0}, jeu="v1.0",
    )  # fmt: skip
    with pytest.raises(JeuMelange):
        charger(campagne_complete, "camp-test")
    donnees = charger(campagne_complete, "camp-test", jeu="v1.1")
    assert donnees.jeu_version == "v1.1"
    assert donnees.baselines[("base:granite", "q4_k_m")].taches["Q"].score == 40.0


def test_notation_relu_llm_refusee_au_comparatif(campagne_complete: Path) -> None:
    ecrire_notation(
        campagne_complete, run_id("20261004-090000", "base-granite", "7777"), "base:granite",
        {"Q": 55.0}, jeu="dev1", jeu_statut="relu-llm",
    )  # fmt: skip
    with pytest.raises(JeuDeveloppement, match="relu-llm"):
        charger(campagne_complete, "camp-test")
    with pytest.raises(JeuDeveloppement, match="dev1"):
        charger(campagne_complete, "camp-test", jeu="dev1")
    # le jeu final reste lisible : la notation de dev n'est retenue nulle part
    assert charger(campagne_complete, "camp-test", jeu="v1.1").jeu_version == "v1.1"


def test_notation_v10_provisoire_toujours_acceptee(campagne_complete: Path) -> None:
    ecrire_notation(
        campagne_complete, run_id("20261004-090000", "base-granite", "6666"), "base:granite",
        {"Q": 65.0}, jeu="v1.0", jeu_statut="provisoire",
    )  # fmt: skip
    donnees = charger(campagne_complete, "camp-test", jeu="v1.0")
    assert donnees.jeu_statuts == ("provisoire",)


def test_cli_ecrit_le_rapport_et_regenere_a_l_octet_pres(
    campagne_complete: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    argv = ["compare", "comparatif", "--campagne", "camp-test", "--racine", str(campagne_complete)]
    assert main(argv) == 0
    assert main(argv) == 0
    rapports = sorted((campagne_complete / "runs" / "compare").glob("*/comparatif.md"))
    assert len(rapports) == 2
    assert rapports[0].read_bytes() == rapports[1].read_bytes()
    assert rapports[0].read_text(encoding="utf-8") == ATTENDU.read_text(encoding="utf-8")
    assert "comparatif :" in capsys.readouterr().out


def test_cli_jeux_melanges_code_usage(
    campagne_complete: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ecrire_notation(
        campagne_complete, run_id("20261004-090000", "base-granite", "8888"), "base:granite",
        {"Q": 70.0}, jeu="v1.0",
    )  # fmt: skip
    argv = ["compare", "comparatif", "--campagne", "camp-test", "--racine", str(campagne_complete)]
    assert main(argv) == 2
    assert "--jeu" in capsys.readouterr().err
    assert not (campagne_complete / "runs" / "compare").exists()


def test_donnees_inconnues_ne_sont_pas_inventees(racine: Path) -> None:
    ecrire_entrainement(racine, M1, "qlora")
    (racine / "runs" / "train" / M1 / "couts.json").write_text(json.dumps({}), encoding="utf-8")
    rapport = _rendu(racine)
    assert "| non mesuré | non mesuré | non mesuré | non mesuré |" in rapport


def test_compare_n_importe_pas_les_modules_interdits() -> None:
    interdits = {"inference", "judge", "mistral", "net"}
    sources = list((Path(__file__).parents[2] / "src" / "slmsp" / "compare").glob("*.py"))
    sources.append(Path(__file__).parents[2] / "src" / "slmsp" / "cli" / "compare.py")
    for source in sources:
        for noeud in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
            if isinstance(noeud, ast.ImportFrom) and noeud.module:
                parties = noeud.module.split(".")
            elif isinstance(noeud, ast.Import):
                parties = noeud.names[0].name.split(".")
            else:
                continue
            assert not (parties[0] == "slmsp" and len(parties) > 1 and parties[1] in interdits), (
                source
            )


def test_sens_cible_compare_la_distance_a_l_ideal() -> None:
    from pydantic import ValidationError

    from slmsp.compare.comparatif import MetriqueBenchmark, _comparable

    conf = MetriqueBenchmark(metrique="b.pct", echelle=100.0, sens="cible", cible=50.0)
    assert _comparable(55.0, conf) > _comparable(40.0, conf)  # 5 points de l'idéal > 10
    with pytest.raises(ValidationError):
        MetriqueBenchmark(metrique="b.pct", sens="cible")
    with pytest.raises(ValidationError):
        MetriqueBenchmark(metrique="b.pct", sens="haut", cible=50.0)


def test_notation_distante_exclue_avec_motif(campagne_complete: Path) -> None:
    """Story 17.1 : un run `distant:` est écarté explicitement, pas en silence."""
    identifiant = run_id("20261004-090000", "distant-qwen", "9997")
    ecrire_notation(
        campagne_complete, identifiant, "distant:qwen3.6-27b", {"Q": 50.0}, generation="g-d",
    )  # fmt: skip
    donnees = charger(campagne_complete, "camp-test")
    assert ("eval-notation", identifiant, "modele-distant") in {
        (e.type, e.run_id, e.motif) for e in donnees.exclus
    }
    assert all(ref != "distant:qwen3.6-27b" for ref, _ in donnees.baselines)


def test_kl_vers_la_base_affichee(campagne_complete: Path) -> None:
    """Story 16.6a : poids et température du terme KL à côté de la méthode ; rien sinon."""
    identifiant = run_id("20261001-150000", "m1-kl", "5555")
    config = {
        "campagne": "camp-test",
        "toml": {
            "methode": "qlora",
            "hyperparametres": {"kl_base": 0.25, "kl_temperature": 1.0},
        },
        "plan": {"methode": "qlora"},
    }
    ecrire_run(campagne_complete, "train", identifiant, config=config, modele_ref="base:granite")
    rendu = _rendu(campagne_complete)
    assert f"(qlora, KL base 0.25, T 1, run {identifiant})" in rendu
    assert f"(qlora, run {M1})" in rendu
