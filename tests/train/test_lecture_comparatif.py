"""Le Comparatif (story 11.1) lit un Run produit par le vrai code de `train run` (10.4)."""

from __future__ import annotations

from slmsp.compare.chargement import charger
from slmsp.compare.comparatif import charger_config, rendre_comparatif
from slmsp.train import run as module_run


def test_comparatif_lit_un_run_train_reel(projet, pile) -> None:
    projet.ecrire_jeu()
    for nom, methode in (("m1-qlora", "qlora"), ("m2-lora", "lora")):
        sorties: list[str] = []
        toml = projet.ecrire_toml(nom, methode=methode)
        code = module_run.executer(toml, racine=projet.racine, pile=pile, sortie=sorties.append)
        assert code == 0, sorties
    (projet.racine / "config").mkdir()
    (projet.racine / "config" / "comparatif.toml").write_text(_TOML, encoding="utf-8")
    donnees = charger(projet.racine, "campagne-test")
    assert sorted(e.methode for e in donnees.entrainements.values()) == ["lora", "qlora"]
    for entrainement in donnees.entrainements.values():
        assert entrainement.couts is not None and entrainement.couts.duree_s is not None
    rapport = rendre_comparatif(donnees, charger_config(projet.racine))
    assert "M1 (qlora" in rapport and "M2 (lora" in rapport
    assert "aucune évaluation intermédiaire archivée" in rapport


_TOML = """schema_version = 1
taches_prioritaires = ["Q", "RD", "CR", "LC"]
gain_min_points = 10.0
taches_gagnantes_min = 2
regression_max_points = 3.0
regression_benchmarks_max_points = 3.0
"""
