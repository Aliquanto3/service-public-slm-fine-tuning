"""`slmsp measure application` : mesure RAM de l'application installée (story 12.14)."""

from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.erreurs import RessourceOccupee
from slmsp.core.var import verrou_gpu
from slmsp.inference.mesures import FOURNISSEUR_LOCAL
from slmsp.measure.application import (
    CsvInvalide,
    InstanceDejaOuverte,
    _lire_mesures_csv,
    mesurer_application,
)
from slmsp.measure.config import charger_config_mesures
from slmsp.measure.protocole import verrou_mesure

CODE_ENFANT = (
    "import subprocess, sys, time\n"
    "enfant = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(2)'])\n"
    "b = bytearray(120 * 1024 * 1024)\n"
    "b[::4096] = b'x' * len(b[::4096])\n"
    "time.sleep(2)\n"
)
CODE_SORTIE_RAPIDE = "pass\n"


@pytest.fixture(autouse=True)
def var_isole(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SLMSP_VAR_DIR", str(tmp_path / "var"))


def _lancer_code(code: str):
    def lancer(_args, **_kwargs):
        return subprocess.Popen([sys.executable, "-c", code])

    return lancer


# --- cœur (`mesurer_application`) -----------------------------------------------------------


def test_nominal_le_pic_inclut_les_descendants(tmp_path: Path) -> None:
    config = charger_config_mesures()
    resultat = mesurer_application(
        "exe-factice",
        config,
        duree_s=0.3,
        racine=tmp_path,
        lancer=_lancer_code(CODE_ENFANT),
    )
    assert resultat.valeurs["ram_max_go"] > 0
    assert sum(resultat.details["repartition_pic_go"].values()) == pytest.approx(
        resultat.valeurs["ram_max_go"]
    )
    assert "nfr-2" not in resultat.conformite and "nfr-3" not in resultat.conformite
    assert resultat.valeurs["debit_tps_mediane"] is None


def test_instance_deja_ouverte_si_sortie_rapide(tmp_path: Path) -> None:
    config = charger_config_mesures()
    with pytest.raises(InstanceDejaOuverte):
        mesurer_application(
            "exe-factice",
            config,
            duree_s=2.0,
            racine=tmp_path,
            lancer=_lancer_code(CODE_SORTIE_RAPIDE),
        )


def test_exe_absent_est_une_erreur_d_usage_cli(tmp_path: Path) -> None:
    code = main(["measure", "application", "--exe", str(tmp_path / "inexistant.exe")])
    assert code == CodeSortie.USAGE


def test_verrou_tenu_leve_ressource_occupee() -> None:
    with verrou_gpu(commande="autre commande slmsp"), pytest.raises(RessourceOccupee):
        with verrou_mesure(commande="slmsp measure application"):
            pass


def test_seuil_depasse_porte_le_repli(tmp_path: Path) -> None:
    config = charger_config_mesures()
    config.seuils.ram_max_go = 0.0001
    config.seuils.ram_cible_go = 0.0001
    resultat = mesurer_application(
        "exe-factice",
        config,
        duree_s=0.3,
        racine=tmp_path,
        lancer=_lancer_code(CODE_ENFANT),
    )
    assert resultat.verdict == "infirmee"
    assert resultat.repli is not None
    for levier in ("contexte réduit", "cache KV en q4", "usearch en i8", "corpus restreint"):
        assert levier in resultat.repli


# --- lecture du CSV --------------------------------------------------------------------------

ENTETE = "horodatage;fournisseur;tokens_sortie;interrompu;duree_ms;premier_token_ms"


def test_csv_retient_les_lignes_locales_dans_la_fenetre(tmp_path: Path) -> None:
    debut = datetime(2026, 1, 1, tzinfo=UTC)
    fin = debut + timedelta(minutes=10)
    dans_fenetre = (debut + timedelta(minutes=1)).isoformat()
    hors_fenetre = (debut - timedelta(hours=1)).isoformat()
    lignes = [
        ENTETE,
        f"{dans_fenetre};{FOURNISSEUR_LOCAL};50;0;2000;500",
        f"{dans_fenetre};distant;50;0;2000;500",
        f"{dans_fenetre};{FOURNISSEUR_LOCAL};50;1;2000;500",
        f"{dans_fenetre};{FOURNISSEUR_LOCAL};50;0;2000;",
        f"{hors_fenetre};{FOURNISSEUR_LOCAL};50;0;2000;500",
    ]
    chemin = tmp_path / "mesures.csv"
    chemin.write_text("\r\n".join(lignes) + "\r\n", encoding="utf-8")
    debits, premiers = _lire_mesures_csv(chemin, debut, fin)
    assert debits == pytest.approx([50 / 1.5])
    assert premiers == pytest.approx([0.5])


def test_csv_retire_le_prefixe_apostrophe(tmp_path: Path) -> None:
    debut = datetime(2026, 1, 1, tzinfo=UTC)
    fin = debut + timedelta(minutes=10)
    horodatage = (debut + timedelta(minutes=1)).isoformat()
    chemin = tmp_path / "mesures.csv"
    # `cellule_sure` préfixe un texte qui commence par `=+-@` ; ici le fournisseur factice.
    chemin.write_text(
        f"{ENTETE}\r\n{horodatage};'{FOURNISSEUR_LOCAL};50;0;2000;500\r\n", encoding="utf-8"
    )
    debits, _ = _lire_mesures_csv(chemin, debut, fin)
    assert debits == pytest.approx([50 / 1.5])


def test_csv_sans_ligne_retenue_leve_csv_invalide(tmp_path: Path) -> None:
    chemin = tmp_path / "mesures.csv"
    chemin.write_text(f"{ENTETE}\r\n", encoding="utf-8")
    with pytest.raises(CsvInvalide):
        _lire_mesures_csv(
            chemin, datetime(2026, 1, 1, tzinfo=UTC), datetime(2026, 1, 2, tzinfo=UTC)
        )


def test_csv_illisible_leve_csv_invalide(tmp_path: Path) -> None:
    chemin = tmp_path / "absent.csv"
    with pytest.raises(CsvInvalide):
        _lire_mesures_csv(
            chemin, datetime(2026, 1, 1, tzinfo=UTC), datetime(2026, 1, 2, tzinfo=UTC)
        )


def test_avec_csv_calcule_debit_et_latence(tmp_path: Path) -> None:
    config = charger_config_mesures()
    # Assez après l'appel (création du run, lancement du processus) pour tomber à coup sûr
    # dans `[debut, fin]`, et largement avant la fin de la fenêtre de 3 s.
    horodatage = (datetime.now().astimezone() + timedelta(seconds=1)).isoformat()
    chemin = tmp_path / "mesures.csv"
    chemin.write_text(
        f"{ENTETE}\r\n{horodatage};{FOURNISSEUR_LOCAL};50;0;2000;500\r\n", encoding="utf-8"
    )
    code_longue_vie = CODE_ENFANT.replace("time.sleep(2)", "time.sleep(5)")
    resultat = mesurer_application(
        "exe-factice",
        config,
        duree_s=3.0,
        mesures_csv=chemin,
        racine=tmp_path,
        lancer=_lancer_code(code_longue_vie),
    )
    assert resultat.valeurs["debit_tps_mediane"] == pytest.approx(50 / 1.5)
    assert resultat.valeurs["premier_token_s_mediane"] == pytest.approx(0.5)
    assert "nfr-2" in resultat.conformite and "nfr-3" in resultat.conformite


# --- CLI ---------------------------------------------------------------------------------------


def test_cli_aide_affiche_les_options(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["measure", "application", "--help"]) == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert "--exe" in sortie and "--mesures-csv" in sortie and "--duree" in sortie


@pytest.mark.lent
def test_reel_measure_application() -> None:
    pytest.skip(
        "mesure réelle : `uv run slmsp measure application --exe <chemin>\\AssistantSP.exe`"
    )


# --- correctifs de revue -------------------------------------------------------------------


def test_csv_absent_a_la_fin_conserve_la_ram(tmp_path: Path) -> None:
    config = charger_config_mesures()
    with pytest.raises(CsvInvalide) as info:
        mesurer_application(
            "exe-factice",
            config,
            duree_s=0.3,
            mesures_csv=tmp_path / "jamais-exporte.csv",
            racine=tmp_path,
            lancer=_lancer_code(CODE_ENFANT),
        )
    resultat = info.value.resultat
    assert resultat is not None
    assert resultat.valeurs["ram_max_go"] > 0
    assert resultat.valeurs["debit_tps_mediane"] is None
    assert "erreur_csv" in resultat.details
    assert (tmp_path / "runs" / "measure" / resultat.run_id / "resultat.json").is_file()


def test_csv_horodatage_sans_fuseau_ou_nombre_invalide_ecarte(tmp_path: Path) -> None:
    debut = datetime(2026, 1, 1, tzinfo=UTC)
    fin = debut + timedelta(minutes=10)
    valide = (debut + timedelta(minutes=1)).isoformat()
    chemin = tmp_path / "mesures.csv"
    chemin.write_text(
        f"{ENTETE}\r\n2026-01-01T00:01:00;{FOURNISSEUR_LOCAL};50;0;2000;500\r\n"
        f"{valide};{FOURNISSEUR_LOCAL};abc;0;2000;500\r\n"
        f"{valide};{FOURNISSEUR_LOCAL};50;0;2000;500\r\n",
        encoding="utf-8",
    )
    debits, _ = _lire_mesures_csv(chemin, debut, fin)
    assert debits == pytest.approx([50 / 1.5])


def test_processus_deja_mort_devient_instance_deja_ouverte(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import psutil

    def absent(_pid: int) -> None:
        raise psutil.NoSuchProcess(_pid)

    monkeypatch.setattr("slmsp.measure.application.psutil.Process", absent)
    with pytest.raises(InstanceDejaOuverte):
        mesurer_application(
            "exe-factice",
            charger_config_mesures(),
            duree_s=0.3,
            racine=tmp_path,
            lancer=_lancer_code(CODE_SORTIE_RAPIDE),
        )


def test_cli_verrou_tenu_code_5(tmp_path: Path) -> None:
    exe = tmp_path / "AssistantSP.exe"
    exe.write_bytes(b"")
    with verrou_gpu(commande="autre commande slmsp"):
        code = main(["measure", "application", "--exe", str(exe), "--racine", str(tmp_path)])
    assert code == CodeSortie.RESSOURCE_OCCUPEE


def test_cli_csv_invalide_renvoie_usage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    exe = tmp_path / "AssistantSP.exe"
    exe.write_bytes(b"")

    def leve(*_a, **_k):
        raise CsvInvalide("aucune ligne retenue")

    monkeypatch.setattr("slmsp.measure.application.mesurer_application", leve)
    code = main(
        [
            "measure",
            "application",
            "--exe",
            str(exe),
            "--racine",
            str(tmp_path),
            "--mesures-csv",
            str(tmp_path / "export.csv"),
        ]
    )
    assert code == CodeSortie.USAGE


@pytest.mark.parametrize("cas", ["dossier-absent", "fichier-existant"])
def test_cli_chemin_csv_refuse_au_depart(tmp_path: Path, cas: str) -> None:
    exe = tmp_path / "AssistantSP.exe"
    exe.write_bytes(b"")
    if cas == "dossier-absent":
        csv_ = tmp_path / "absent" / "export.csv"
    else:
        csv_ = tmp_path / "export.csv"
        csv_.write_text("", encoding="utf-8")
    code = main(["measure", "application", "--exe", str(exe), "--mesures-csv", str(csv_)])
    assert code == CodeSortie.USAGE
