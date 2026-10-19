"""`slmsp bench cache-hf` : snapshot_download, load_dataset et contrôle hors ligne simulés."""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.benchmarks import cache_hf as jeux_hf
from slmsp.cli import main
from slmsp.core.erreurs import ConfigurationInvalide

REV_A = "a" * 40
REV_B = "b" * 40
DEPOT_A = "Org/jeu-a"
DEPOT_B = "Org/jeu-b"


def toml_pins(nom: str, pins: dict[str, str]) -> str:
    lignes = "\n".join(f'"{depot}" = "{rev}"' for depot, rev in pins.items())
    return (
        f'nom = "{nom}"\nmoteur = "lm_eval"\ntache = "t"\ncible = "hf"\n'
        f'quantification = "avant"\n\n[options.jeux_hf]\n{lignes}\n'
    )


@pytest.fixture
def dossier(tmp_path: Path) -> Path:
    base = tmp_path / "benchmarks"
    base.mkdir()
    (base / "a.toml").write_text(toml_pins("a", {DEPOT_A: REV_A}), encoding="utf-8")
    (base / "b.toml").write_text(toml_pins("b", {DEPOT_B: REV_B, DEPOT_A: REV_A}), encoding="utf-8")
    return base


class Doublures:
    """Faux `snapshot_download`, `load_dataset` et contrôle hors ligne, sur un cache factice."""

    def __init__(self, hf_home: Path) -> None:
        self.hf_home = hf_home
        self.telechargements: list[tuple[str, str]] = []
        self.chargements: list[tuple[str, str]] = []
        self.lisibles: set[str] = set()  # dépôts relisibles hors ligne
        self.cache_datasets_ok = True

    def telecharger(self, depot: str, revision: str) -> None:
        self.telechargements.append((depot, revision))
        snapshot = jeux_hf.dossier_depot(self.hf_home, depot) / "snapshots" / revision
        snapshot.mkdir(parents=True, exist_ok=True)
        (snapshot / "fichier-factice").write_text("<contenu-factice>", encoding="utf-8")

    def charger(self, depot: str, revision: str, noms) -> int:
        self.chargements.append((depot, revision))
        if self.cache_datasets_ok:
            self.lisibles.add(depot)
        return len(noms)

    def verifier(self, pins, configs):
        return {d: None if d in self.lisibles else "DatasetNotFoundError : absent" for d in pins}


@pytest.fixture
def faux(tmp_path: Path) -> Doublures:
    return Doublures(tmp_path / "cache-hf")


def executer(faux: Doublures, pins: dict[str, str]) -> list[dict]:
    lignes: list[dict] = []
    jeux_hf.executer(
        pins,
        faux.hf_home,
        consigner=lignes.append,
        telecharger=faux.telecharger,
        charger=faux.charger,
        verifier=faux.verifier,
    )
    return lignes


def test_telecharge_ecrit_refs_main_et_charge(faux: Doublures) -> None:
    lignes = executer(faux, {DEPOT_A: REV_A, DEPOT_B: REV_B})
    assert [ligne["statut"] for ligne in lignes] == ["installe", "installe"]
    assert faux.telechargements == [(DEPOT_A, REV_A), (DEPOT_B, REV_B)]
    assert faux.chargements == faux.telechargements
    refs = jeux_hf.dossier_depot(faux.hf_home, DEPOT_A) / "refs" / "main"
    assert refs.read_text(encoding="utf-8") == REV_A


def test_idempotence_rien_n_est_retelecharge(faux: Doublures) -> None:
    executer(faux, {DEPOT_A: REV_A})
    faux.telechargements.clear()
    faux.chargements.clear()
    lignes = executer(faux, {DEPOT_A: REV_A})
    assert [ligne["statut"] for ligne in lignes] == ["deja-present"]
    assert faux.telechargements == [] and faux.chargements == []


def test_refs_main_corrige_sans_retelecharger_le_snapshot(faux: Doublures) -> None:
    executer(faux, {DEPOT_A: REV_A})
    refs = jeux_hf.dossier_depot(faux.hf_home, DEPOT_A) / "refs" / "main"
    refs.write_text("c" * 40, encoding="utf-8")
    faux.telechargements.clear()
    lignes = executer(faux, {DEPOT_A: REV_A})
    assert lignes[0]["statut"] == "installe"
    assert faux.telechargements == [(DEPOT_A, REV_A)]  # idempotent côté huggingface_hub
    assert refs.read_text(encoding="utf-8") == REV_A


def test_controle_hors_ligne_en_echec_est_explicite(faux: Doublures) -> None:
    faux.cache_datasets_ok = False
    with pytest.raises(jeux_hf.CacheHorsLigneInvalide, match=r"illisible hors ligne.*Org/jeu-a"):
        executer(faux, {DEPOT_A: REV_A})


def test_lire_pins_dedoublonne_et_filtre(dossier: Path) -> None:
    assert jeux_hf.lire_pins(dossier) == {DEPOT_A: REV_A, DEPOT_B: REV_B}
    assert jeux_hf.lire_pins(dossier, [DEPOT_B]) == {DEPOT_B: REV_B}


def test_jeu_absent_de_la_config(dossier: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="absent de .options.jeux_hf.*Org/inconnu"):
        jeux_hf.lire_pins(dossier, ["Org/inconnu"])


def test_deux_revisions_pour_un_depot(dossier: Path) -> None:
    (dossier / "c.toml").write_text(toml_pins("c", {DEPOT_A: REV_B}), encoding="utf-8")
    with pytest.raises(ConfigurationInvalide, match="deux révisions"):
        jeux_hf.lire_pins(dossier)


def test_commande_journalise_le_run(faux, dossier, monkeypatch, tmp_path, capsys) -> None:
    import json

    from slmsp.benchmarks import config as config_bench

    monkeypatch.setenv("SLMSP_MODELS_DIR", str(tmp_path / "models"))
    monkeypatch.setattr(config_bench, "dossier_benchmarks", lambda: dossier)
    monkeypatch.setattr(jeux_hf, "_telecharger", faux.telecharger)
    monkeypatch.setattr(jeux_hf, "_charger", faux.charger)
    monkeypatch.setattr(jeux_hf, "verifier_hors_ligne", faux.verifier)
    monkeypatch.setattr(
        jeux_hf, "preparer", jeux_hf.dossier_cache
    )  # sans toucher à huggingface_hub
    faux.hf_home = (tmp_path / "models").resolve() / ".cache-hf"
    racine = tmp_path / "racine"
    assert main(["bench", "cache-hf", "--racine", str(racine)]) == 0
    (run,) = (racine / "runs" / "fetch").iterdir()
    lignes = [
        json.loads(ligne)
        for ligne in (run / "fichiers.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert {ligne["depot"] for ligne in lignes} == {DEPOT_A, DEPOT_B}
    etats = (run / "etat.jsonl").read_text(encoding="utf-8")
    assert '"complet"' in etats
    assert "lisible(s) hors ligne" in capsys.readouterr().out
    assert main(["bench", "cache-hf", "Org/inconnu", "--racine", str(racine)]) != 0
    assert "absent de [options.jeux_hf]" in capsys.readouterr().err


def test_controle_hors_ligne_lit_le_resultat_du_sous_processus(monkeypatch) -> None:
    from types import SimpleNamespace

    sortie = SimpleNamespace(
        stdout='bruit\nRESULTAT={"Org/jeu-a": null, "Org/jeu-b": "X : absent"}\n', stderr=""
    )
    appels = []
    monkeypatch.setattr(
        jeux_hf.subprocess, "run", lambda *a, **k: appels.append(k["env"]) or sortie
    )
    resultat = jeux_hf.verifier_hors_ligne({DEPOT_A: REV_A, DEPOT_B: REV_B}, {})
    assert resultat == {"Org/jeu-a": None, "Org/jeu-b": "X : absent"}
    assert appels[0]["HF_DATASETS_OFFLINE"] == "1" and appels[0]["HF_HUB_OFFLINE"] == "1"
    hf_home = appels[0]["HF_HOME"]
    assert appels[0]["HF_HUB_CACHE"] == str(Path(hf_home) / "hub")
    assert appels[0]["HF_DATASETS_CACHE"] == str(Path(hf_home) / "datasets")


def test_controle_hors_ligne_sans_resultat_echoue_clairement(monkeypatch) -> None:
    from types import SimpleNamespace

    sortie = SimpleNamespace(stdout="", stderr="Traceback\nModuleNotFoundError: datasets")
    monkeypatch.setattr(jeux_hf.subprocess, "run", lambda *a, **k: sortie)
    resultat = jeux_hf.verifier_hors_ligne({DEPOT_A: REV_A}, {DEPOT_A: ["default"]})
    assert "ModuleNotFoundError" in resultat[DEPOT_A]


def test_script_de_controle_charge_comme_lm_eval_sans_revision(monkeypatch) -> None:
    """Exécute le vrai script avec un `datasets` factice : aucune `revision`, bonnes configs."""
    import json
    import sys
    from types import ModuleType

    appels: list[tuple] = []
    faux_datasets = ModuleType("datasets")
    faux_datasets.load_dataset = lambda *a, **k: appels.append((a, k))  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "datasets", faux_datasets)
    sorties: list[str] = []
    monkeypatch.setattr(sys, "argv", ["-c", json.dumps({DEPOT_A: ["x", "default"], DEPOT_B: []})])
    monkeypatch.setattr(
        "builtins.print", lambda *a, **k: sorties.append(" ".join(str(v) for v in a))
    )
    exec(jeux_hf._SCRIPT_CONTROLE, {"__name__": "__main__"})
    assert appels == [((DEPOT_A, "x"), {}), ((DEPOT_A, None), {})]
    resultat = json.loads(sorties[-1].removeprefix("RESULTAT="))
    assert resultat[DEPOT_A] is None
    assert "aucune configuration" in resultat[DEPOT_B]


def test_executer_transmet_les_configurations_et_refuse_une_liste_vide(faux: Doublures) -> None:
    recu: list = []
    jeux_hf.executer(
        {DEPOT_A: REV_A},
        faux.hf_home,
        {DEPOT_A: ["c1", "c2"]},
        telecharger=faux.telecharger,
        charger=lambda d, r, noms: recu.append(list(noms)) or faux.charger(d, r, noms),
        verifier=faux.verifier,
    )
    assert recu == [["c1", "c2"]]
    with pytest.raises(ConfigurationInvalide, match="aucune configuration"):
        jeux_hf.executer({DEPOT_A: REV_A}, faux.hf_home, {DEPOT_A: []}, verifier=faux.verifier)


def test_refs_main_absent_si_le_chargement_echoue(faux: Doublures) -> None:
    def echec(*_a) -> int:
        raise RuntimeError("réseau coupé")

    with pytest.raises(RuntimeError):
        jeux_hf.executer(
            {DEPOT_A: REV_A},
            faux.hf_home,
            telecharger=faux.telecharger,
            charger=echec,
            verifier=faux.verifier,
        )
    refs = jeux_hf.dossier_depot(faux.hf_home, DEPOT_A) / "refs" / "main"
    assert not refs.exists()


def _ecrire_c(dossier: Path, liste: str) -> None:
    corps = (
        toml_pins("c", {"Org/jeu-c": REV_A}) + f'\n[options.configs_hf]\n"Org/jeu-c" = {liste}\n'
    )
    (dossier / "c.toml").write_text(corps, encoding="utf-8")


def test_lire_configs_defaut_et_liste_vide(dossier: Path) -> None:
    _ecrire_c(dossier, '["u", "v"]')
    assert jeux_hf.lire_configs(dossier, [DEPOT_A, "Org/jeu-c"]) == {
        DEPOT_A: ["default"],
        "Org/jeu-c": ["u", "v"],
    }
    _ecrire_c(dossier, "[]")
    with pytest.raises(ConfigurationInvalide, match="liste non vide"):
        jeux_hf.lire_configs(dossier, ["Org/jeu-c"])


def test_configs_reelles_du_depot() -> None:
    from slmsp.benchmarks import config as config_bench

    dossier_reel = config_bench.dossier_benchmarks()
    pins = jeux_hf.lire_pins(dossier_reel)
    configs = jeux_hf.lire_configs(dossier_reel, list(pins))
    assert len(configs["cais/mmlu"]) == 57
    assert not {"all", "auxiliary_train"} & set(configs["cais/mmlu"])
    assert configs["facebook/belebele"] == ["fra_Latn"]
    assert configs["CohereLabs/Global-MMLU-Lite"] == ["fr"]
    assert configs["jannalu/crows_pairs_multilingual"] == ["french"]
    assert configs["google/IFEval"] == ["default"]


def test_snapshot_partiel_est_repris(faux: Doublures) -> None:
    partiel = jeux_hf.dossier_depot(faux.hf_home, DEPOT_A) / "snapshots" / REV_A
    partiel.mkdir(parents=True)
    (partiel / "debut.parquet").write_text("<tronque>", encoding="utf-8")
    lignes = executer(faux, {DEPOT_A: REV_A})
    assert lignes[0]["statut"] == "installe"
    assert faux.telechargements == [(DEPOT_A, REV_A)]  # snapshot_download complète le reste
