"""Concurrence entre processus réels sur le même registre (story 1.5, critère 6).

Deux sous-processus ouvrent le registre, signalent qu'ils sont prêts, puis attendent un
fichier de départ pour réserver en même temps. Aucun appel d'API.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_CONCURRENT = """
import pathlib, sys, time
from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.registre import RegistreBudget
from slmsp.core.erreurs import BudgetEpuise

budgets, tarifs, depart, euros, repetitions = sys.argv[1:6]
registre = RegistreBudget(charger_budgets(budgets), charger_tarifs(tarifs))
print("pret", flush=True)
signal = pathlib.Path(depart)
while not signal.exists():
    time.sleep(0.002)
for _ in range(int(repetitions)):
    try:
        registre.reserver("mistral", "juge", "m-test", "direct", 0, round(float(euros) * 1e6))
        print("reserve", flush=True)
    except BudgetEpuise:
        print("epuise", flush=True)
"""


def _lancer_deux(fichiers, tmp_path: Path, euros: float, repetitions: int) -> list[list[str]]:
    depart = tmp_path / "depart"
    processus = [
        subprocess.Popen(
            [
                sys.executable,
                "-c",
                SCRIPT_CONCURRENT,
                str(fichiers.budgets),
                str(fichiers.tarifs),
                str(depart),
                str(euros),
                str(repetitions),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            env=dict(os.environ),  # même SLMSP_VAR_DIR que le test
        )
        for _ in range(2)
    ]
    try:
        for proc in processus:
            assert proc.stdout is not None
            ligne = proc.stdout.readline().strip()
            if ligne != "pret":
                proc.wait(timeout=60)
                raise AssertionError(f"sous-processus non prêt : {ligne!r} {proc.stderr.read()}")
        depart.write_text("go", encoding="utf-8")
        sorties = []
        for proc in processus:
            sortie, erreur = proc.communicate(timeout=120)
            assert proc.returncode == 0, erreur
            sorties.append(sortie.split())
        return sorties
    finally:
        for proc in processus:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=10)


def test_critere_6_un_seul_des_deux_processus_recoit_budget_epuise(
    config_test, tmp_path: Path
) -> None:
    fichiers = config_test()  # mistral.juge : 5 €
    sorties = _lancer_deux(fichiers, tmp_path, euros=3.0, repetitions=1)
    resultats = sorted(resultat for sortie in sorties for resultat in sortie)
    assert resultats == ["epuise", "reserve"]
    juge = next(ligne for ligne in fichiers.ouvrir().etat().lignes if ligne.sous_poste == "juge")
    assert juge.depense_eur + juge.reserve_eur == pytest.approx(3.0)
    assert juge.depense_eur + juge.reserve_eur <= juge.plafond_eur


def test_critere_6_rafales_concurrentes_jamais_au_dessus_du_plafond(
    config_test, tmp_path: Path, lignes
) -> None:
    fichiers = config_test()  # mistral.juge : 5 € ; 16 réservations de 0,30 € tiennent
    sorties = _lancer_deux(fichiers, tmp_path, euros=0.3, repetitions=20)
    resultats = [resultat for sortie in sorties for resultat in sortie]
    assert resultats.count("reserve") == 16
    assert resultats.count("epuise") == 24
    # Les deux processus sont morts : leurs réservations passent au pire cas à l'ouverture.
    registre = fichiers.ouvrir()
    assert len(lignes(registre)) == 16
    juge = next(ligne for ligne in registre.etat().lignes if ligne.sous_poste == "juge")
    assert juge.depense_eur + juge.reserve_eur == pytest.approx(4.8)
    assert juge.depense_eur + juge.reserve_eur <= juge.plafond_eur
