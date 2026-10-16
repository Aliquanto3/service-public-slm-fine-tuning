"""Débit, délai au premier token et protocole complet sur flux factices (story 6.4)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from slmsp.core.evenements import Erreur, Fin, Jeton
from slmsp.core.schemas.mesure import ResultatMesure
from slmsp.measure.config import ConfigMesures, SeuilsNfr
from slmsp.measure.debit import MesureEchouee, mediane_p95, mesurer_question
from slmsp.measure.protocole import mesurer


class Horloge:
    """Horloge contrôlée : chaque `avance` fait progresser le temps."""

    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t

    def avance(self, secondes: float) -> None:
        self.t += secondes


def _flux(horloge: Horloge, attente: float, jetons: int, pas: float, usage: int | None):
    horloge.avance(attente)
    for rang in range(jetons):
        yield Jeton(texte="<jeton-factice>")
        if rang < jetons - 1:
            horloge.avance(pas)
    yield Fin(raison="terminee", usage=None if usage is None else {"completion_tokens": usage})


def test_premier_token_et_debit() -> None:
    h = Horloge()
    # 2 s avant le premier jeton ; 10 jetons ensuite, 0,1 s chacun.
    m = mesurer_question(_flux(h, 2.0, 10, 0.1, None), h)
    assert m.premier_token_s == pytest.approx(2.0)
    assert m.tokens == 10 and m.tokens_estimes
    assert m.debit_tps == pytest.approx(10.0)


def test_usage_prime_sur_le_comptage_des_jetons() -> None:
    h = Horloge()
    m = mesurer_question(_flux(h, 1.0, 4, 0.5, 31), h)
    assert m.tokens == 31 and not m.tokens_estimes
    assert m.debit_tps == pytest.approx(20.0)


def test_erreur_et_flux_sans_jeton() -> None:
    with pytest.raises(MesureEchouee):
        mesurer_question([Erreur(code="x", message="<erreur-factice>")])
    with pytest.raises(MesureEchouee):
        mesurer_question([Fin(raison="terminee")])


def test_mediane_p95() -> None:
    assert mediane_p95([1.0, 2.0, 3.0]) == (2.0, pytest.approx(2.9))
    with pytest.raises(ValueError):
        mediane_p95([])


def _config(**seuils: float) -> ConfigMesures:
    base = {
        "ram_max_go": 5.0,
        "ram_cible_go": 4.0,
        "debit_min_tps": 8.0,
        "premier_token_max_s": 5.0,
        "taille_max_go": 4.0,
    }
    return ConfigMesures(
        schema_version=1,
        questions=["<question-factice-1>", "<question-factice-2>"],
        repetitions=3,
        echauffement=1,
        plafond_threads=2,
        periode_ms=100,
        seuils=SeuilsNfr(**{**base, **seuils}),
    )


class RamFactice:
    def __init__(self, octets: int) -> None:
        self.pic_octets = octets
        self.nb_echantillons = 7

    def __call__(self, **_kw: object) -> RamFactice:
        return self

    def __enter__(self) -> RamFactice:
        return self

    def __exit__(self, *_a: object) -> None:
        return None


def _lancer(tmp_path: Path, config: ConfigMesures, pas: float = 0.05) -> ResultatMesure:
    h = Horloge()
    questions: list[str] = []

    def repondre(question: str):
        questions.append(question)
        return _flux(h, 0.5, 20, pas, None)

    (tmp_path / "gguf.bin").write_bytes(b"x" * 1024)
    resultat = mesurer(
        repondre,
        config,
        modele="base:<modele-factice>",
        quantification="q4_k_m",
        serveurs=[{"role": "generation"}],
        composants={"gguf": tmp_path / "gguf.bin"},
        racine=tmp_path,
        echantillonneur=RamFactice(2 * 1024**3),
        horloge=h,
    )
    assert questions[:2] == ["<question-factice-1>", "<question-factice-2>"]
    assert len(questions) == 4  # échauffement + 3 répétitions
    return resultat


def test_protocole_conforme_ecrit_le_resultat(tmp_path: Path) -> None:
    resultat = _lancer(tmp_path, _config())
    assert resultat.verdict == "confirmee" and resultat.repli is None
    assert resultat.conformite == {
        "nfr-1": True,
        "nfr-1-cible": True,
        "nfr-2": True,
        "nfr-3": True,
        "nfr-6": True,
    }
    assert resultat.valeurs["ram_max_go"] == pytest.approx(2.0)
    assert resultat.valeurs["debit_tps_mediane"] == pytest.approx(20.0)
    assert resultat.valeurs["premier_token_s_p95"] == pytest.approx(0.5)
    assert resultat.environnement is not None
    assert "PC cible" in (resultat.avertissement or "")
    ecrit = tmp_path / "runs" / "measure" / resultat.run_id / "resultat.json"
    assert ResultatMesure.model_validate(json.loads(ecrit.read_text(encoding="utf-8")))


def test_protocole_hors_seuil_est_infirme_avec_repli(tmp_path: Path) -> None:
    resultat = _lancer(tmp_path, _config(ram_max_go=1.0, debit_min_tps=50.0))
    assert resultat.verdict == "infirmee"
    assert not resultat.conformite["nfr-1"] and not resultat.conformite["nfr-2"]
    assert resultat.conformite["nfr-3"]
    assert "nfr-1, nfr-2" in (resultat.repli or "")


def _valeurs(**v: float | None) -> dict[str, float | None]:
    base: dict[str, float | None] = {
        "ram_max_go": 5.0,
        "debit_tps_mediane": 8.0,
        "premier_token_s_p95": 4.9,
        "taille_installee_go": 4.0,
    }
    return {**base, **v}


def test_conformite_bornes_incluses_ou_exclues() -> None:
    from slmsp.measure.protocole import _conformite

    c = _conformite(_valeurs(), _config())
    assert c["nfr-1"] and not c["nfr-1-cible"] and c["nfr-2"] and c["nfr-3"] and c["nfr-6"]
    c = _conformite(_valeurs(premier_token_s_p95=5.0), _config())
    assert not c["nfr-3"]  # strictement inférieur
    c = _conformite(
        _valeurs(ram_max_go=5.01, debit_tps_mediane=7.99, taille_installee_go=4.01), _config()
    )
    assert not c["nfr-1"] and not c["nfr-2"] and not c["nfr-6"]
    c = _conformite(
        _valeurs(ram_max_go=None, debit_tps_mediane=None, premier_token_s_p95=None), _config()
    )
    assert not c["nfr-1"] and not c["nfr-2"] and not c["nfr-3"]


def test_composant_absent_leve(tmp_path: Path) -> None:
    from slmsp.measure.taille import taille_octets

    with pytest.raises(FileNotFoundError):
        taille_octets(tmp_path / "absent")


def test_plafonner_threads() -> None:
    from types import SimpleNamespace

    from slmsp.cli._assemblage import plafonner_threads

    class Cfg(SimpleNamespace):
        def model_copy(self, update: dict[str, int]) -> Cfg:
            return Cfg(**{**vars(self), **update})

    assert plafonner_threads(Cfg(threads=None), 4).threads == 4
    assert plafonner_threads(Cfg(threads=8), 4).threads == 4
    assert plafonner_threads(Cfg(threads=2), 4).threads == 2
    cfg = Cfg(threads=8)
    assert plafonner_threads(cfg, None) is cfg
