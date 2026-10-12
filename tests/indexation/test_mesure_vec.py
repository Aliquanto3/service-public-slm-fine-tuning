"""Mesure H-VEC et `slmsp index mesurer` (story 2.3)."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import numpy as np
import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.artefacts import ouvrir_run
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ManifesteInvalide
from slmsp.core.schemas.mesure import ResultatMesure
from slmsp.core.schemas.run import RunManifest
from slmsp.index.config import charger_config_index
from slmsp.index.lecture import IndexLocal
from slmsp.indexation.mesure_vec import (
    NOM_RESULTAT,
    REPLI_H_VEC,
    mesurer_h_vec,
    percentiles,
    tirer_requetes,
    verdict_h_vec,
)

MIO = 1024**2


def test_percentiles() -> None:
    stats = percentiles(list(range(1, 101)))
    assert stats["p50_ms"] == pytest.approx(50.5)
    assert stats["p95_ms"] == pytest.approx(95.05)
    assert stats["moyenne_ms"] == pytest.approx(50.5) and stats["max_ms"] == 100.0
    with pytest.raises(ValueError):
        percentiles([])


@pytest.mark.parametrize(
    ("p95", "ram", "verdict"),
    [
        (300.0, 350.0, "confirmee"),
        (12.0, 10.0, "confirmee"),
        (300.1, 10.0, "infirmee"),
        (12.0, 350.5, "infirmee"),
    ],
)
def test_verdict(p95: float, ram: float, verdict: str) -> None:
    obtenu, repli = verdict_h_vec(p95, ram, 300, 350)
    assert obtenu == verdict
    assert repli == (REPLI_H_VEC if verdict == "infirmee" else None)


def test_resultat_infirme_sans_repli_refuse() -> None:
    champs = {
        "mesure": "h-vec",
        "hypothese": "H-VEC",
        "run_id": "20261012-104817-h-vec-c4eb",
        "mesure_le": "2026-10-12T10:49:17+02:00",
        "parametres": {},
        "valeurs": {"p95_ms": 400.0},
        "seuils": {"p95_ms": 300.0},
    }
    with pytest.raises(ValueError, match="repli"):
        ResultatMesure(verdict="infirmee", repli=None, **champs)
    assert ResultatMesure(verdict="infirmee", repli=REPLI_H_VEC, **champs).repli == REPLI_H_VEC
    assert ResultatMesure(verdict="confirmee", **champs).repli is None


def test_repli_mentionne_usearch() -> None:
    assert "usearch HNSW i8" in REPLI_H_VEC and "VectorStore" in REPLI_H_VEC
    assert REPLI_H_VEC.endswith("à faire")


def test_tirage_sans_remise_et_reproductible(fabrique_index) -> None:
    factice = fabrique_index((30, 20))
    with IndexLocal(factice.dossier) as index:
        premier = tirer_requetes(index, 25, 42)
        second = tirer_requetes(index, 25, 42)
        autre = tirer_requetes(index, 25, 43)
        tous = tirer_requetes(index, 500, 42)
    assert premier.dtype == np.float32 and premier.shape == (25, 1024)
    np.testing.assert_array_equal(premier, second)
    assert not np.array_equal(premier, autre)
    assert len({ligne.tobytes() for ligne in premier}) == 25
    assert tous.shape == (50, 1024)
    corpus = {ligne.tobytes() for ligne in factice.vecteurs}
    assert all(ligne.astype(np.float16).tobytes() in corpus for ligne in premier)


def _rss(*valeurs: int):
    suite = iter(valeurs)
    return lambda: next(suite)


def _config(requetes: int = 20):
    config = charger_config_index()
    return config.model_copy(
        update={
            "taille_bloc": 16,
            "mesure": config.mesure.model_copy(update={"requetes": requetes, "k": 5}),
        }
    )


def test_mesure_confirmee(fabrique_index) -> None:
    factice = fabrique_index((30, 20))
    resultat = mesurer_h_vec(
        factice.racine, None, _config(), rss=_rss(100 * MIO, 150 * MIO), pic=lambda: 400 * MIO
    )
    assert resultat.verdict == "confirmee" and resultat.repli is None
    assert resultat.mesure == "h-vec" and resultat.hypothese == "H-VEC"
    assert resultat.index_version == factice.version
    assert resultat.valeurs["ram_ajoutee_mo"] == pytest.approx(50.0)
    assert resultat.valeurs["rss_avant_mo"] == pytest.approx(100.0)
    assert (
        0 < resultat.valeurs["p50_ms"] <= resultat.valeurs["p95_ms"] <= resultat.valeurs["max_ms"]
    )
    assert resultat.seuils == {"p95_ms": 300.0, "ram_mo": 350.0}
    assert resultat.parametres["requetes"] == 20 and resultat.parametres["graine"] == 42
    assert resultat.parametres["nb_chunks"] == 50 and resultat.parametres["k"] == 5
    assert resultat.details["requetes_retrouvees_en_tete"] == 20
    assert resultat.details["pic_working_set_mo"] == pytest.approx(400.0)

    run = ouvrir_run(resultat.run_id, racine=factice.racine)
    assert run.dossier == factice.racine / "runs" / "measure" / resultat.run_id
    assert run.manifeste.type == "measure" and run.manifeste.index_version == factice.version
    assert run.manifeste.graine == 42
    assert "-h-vec-" in resultat.run_id
    assert run.statut_courant() == "complet"
    ecrit = ResultatMesure.model_validate_json((run.dossier / NOM_RESULTAT).read_bytes())
    assert ecrit == resultat


def test_mesure_infirmee_par_la_ram(fabrique_index) -> None:
    factice = fabrique_index((30, 20))
    resultat = mesurer_h_vec(
        factice.racine,
        factice.version,
        _config(),
        rss=_rss(100 * MIO, 451 * MIO),
        pic=lambda: None,
    )
    assert resultat.verdict == "infirmee" and resultat.repli == REPLI_H_VEC
    assert resultat.details["pic_working_set_mo"] is None


def test_mesure_rss_reel(fabrique_index) -> None:
    factice = fabrique_index((30, 20))
    resultat = mesurer_h_vec(factice.racine, None, _config(200))
    assert (
        resultat.parametres["requetes"] == 50 and resultat.parametres["requetes_demandees"] == 200
    )
    assert resultat.valeurs["rss_avant_mo"] > 0


def test_mesure_en_erreur_termine_le_run(fabrique_index) -> None:
    factice = fabrique_index((30, 20))

    def rss_en_panne() -> int:
        raise RuntimeError("psutil indisponible")

    with pytest.raises(RuntimeError, match="psutil"):
        mesurer_h_vec(factice.racine, None, _config(), rss=rss_en_panne)
    (dossier,) = (factice.racine / "runs" / "measure").iterdir()
    run = ouvrir_run(dossier.name, racine=factice.racine)
    assert run.statut_courant() == "partiel-erreur"
    assert not (dossier / NOM_RESULTAT).exists()


def test_mesure_sans_index(tmp_path: Path) -> None:
    with pytest.raises(ManifesteInvalide, match="aucun Index"):
        mesurer_h_vec(tmp_path, None, _config())
    with pytest.raises(ManifesteInvalide, match="inconnue"):
        mesurer_h_vec(tmp_path, "20260101", _config())
    assert not (tmp_path / "runs").exists()


def test_cli_mesurer(fabrique_index, capsys: pytest.CaptureFixture[str]) -> None:
    factice = fabrique_index((30, 20))
    code = main(["index", "mesurer", "--racine", str(factice.racine), "--version", factice.version])
    assert code == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert f"H-VEC sur l'Index {factice.version}" in sortie
    assert "p95" in sortie and "RAM ajoutée" in sortie
    (dossier,) = (factice.racine / "runs" / "measure").iterdir()
    manifeste = RunManifest.model_validate_json((dossier / "run.json").read_bytes())
    assert manifeste.index_version == factice.version
    resultat = json.loads((dossier / NOM_RESULTAT).read_text(encoding="utf-8"))
    for cle in ("p50_ms", "p95_ms", "ram_ajoutee_mo"):
        assert cle in resultat["valeurs"]
    assert resultat["verdict"] in ("confirmee", "infirmee")
    assert dossier.name in sortie


def test_cli_mesurer_sans_index(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["index", "mesurer", "--racine", str(tmp_path)])
    assert code == CodeSortie.MANIFESTE_INVALIDE
    assert "aucun Index" in capsys.readouterr().err


# --- Mesure réelle (lent) ----------------------------------------------------------------


def _racine_reelle() -> Path:
    valeur = os.environ.get("SLMSP_RACINE_REELLE", "").strip()
    if valeur:
        return Path(valeur).resolve()
    racine = racine_projet()
    parties = racine.parts
    if ".claude" in parties and "worktrees" in parties:
        return Path(*parties[: parties.index(".claude")])
    return racine


@pytest.mark.lent
def test_reel_mesure_h_vec(tmp_path: Path) -> None:
    """Mesure H-VEC sur une copie de l'Index réel (le run est écrit sous `tmp_path`)."""
    config = charger_config_index()
    source = _racine_reelle() / "index" / config.version()
    if not source.is_dir():
        pytest.skip(f"Index réel absent : {source}")
    shutil.copytree(source, tmp_path / "index" / config.version())
    resultat = mesurer_h_vec(tmp_path, config.version(), config)
    assert resultat.parametres["requetes"] == 200
    assert resultat.details["requetes_retrouvees_en_tete"] >= 190
    assert resultat.verdict in ("confirmee", "infirmee")
    print(json.dumps(resultat.model_dump(mode="json"), ensure_ascii=False, indent=2))
