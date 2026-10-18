"""Orchestrateur de benchmarks : moteur factice enregistré par le test, aucun outil tiers."""

from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from slmsp.benchmarks import config as config_bench
from slmsp.benchmarks import moteurs, orchestrateur
from slmsp.benchmarks.moteurs import SortieMoteur
from slmsp.cli import main
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas.bench import ResultatBench
from slmsp.core.var import verrou_gpu

TOML = """
nom = "{nom}"
moteur = "{moteur}"
tache = "tache-{nom}"
fewshot = 3
limite = 10
cible = "{cible}"
quantification = "{quantification}"
socle = {socle}
"""


def ecrire(
    dossier: Path, nom: str, moteur="factice", cible="gguf", quantification="avant", socle="true"
) -> None:
    (dossier / f"{nom}.toml").write_text(
        TOML.format(
            nom=nom, moteur=moteur, cible=cible, quantification=quantification, socle=socle
        ),
        encoding="utf-8",
    )


@pytest.fixture
def banc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    dossier = tmp_path / "config-bench"
    dossier.mkdir()
    monkeypatch.setattr(config_bench, "dossier_benchmarks", lambda: dossier)
    appels: list[tuple[str, str]] = []

    def factice(config, contexte):
        appels.append((config.nom, contexte.variante))
        if config.nom.startswith("casse"):
            raise RuntimeError("panne factice")
        if config.nom.startswith("saute"):
            return SortieMoteur(saute="poids absents")
        return SortieMoteur(
            scores={"acc": 0.5}, outil="outil-factice", outil_version="9.9", details={"n": 3}
        )

    monkeypatch.setitem(moteurs._ENREGISTRES, "factice", factice)
    return SimpleNamespace(dossier=dossier, appels=appels, racine=tmp_path / "racine")


def lancer_cli(banc, *arguments: str) -> int:
    return main(
        ["bench", "run", "--modele", "base:modele-test", "--racine", str(banc.racine), *arguments]
    )


def dossier_run(banc) -> Path:
    (dossier,) = (banc.racine / "runs" / "bench").iterdir()
    return dossier


def etats(dossier: Path) -> list[str]:
    lignes = (dossier / "etat.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(ligne)["statut"] for ligne in lignes]


def test_liste_du_socle_versionne(capsys) -> None:
    assert main(["bench", "liste"]) == 0
    sortie = capsys.readouterr().out
    configs = config_bench.charger_benchmarks()
    assert {"french_bench_mc", "belebele_fra_latn", "global_mmlu_fr", "mcq_eval", "ifeval"} <= set(
        configs
    )
    assert configs["french_bench_mc"].fewshot == 3
    assert configs["global_mmlu_fr"].limite == 2000
    for ligne in sortie.splitlines()[1:]:
        assert any(ligne.startswith(nom) for nom in configs)
    assert "french_bench_mc" in sortie and "lm_eval" in sortie and "2000" in sortie
    assert all(moteurs.moteur_connu(c.moteur) for c in configs.values())
    assert all(c.socle for c in configs.values())


def test_nouveau_benchmark_sans_toucher_au_code(banc, capsys) -> None:
    ecrire(banc.dossier, "x", socle="false")
    assert lancer_cli(banc, "--benchmarks", "x") == 0
    assert banc.appels == [("x", "avant")]
    assert "complet" in capsys.readouterr().out


def test_moteur_inconnu_refuse(banc, capsys) -> None:
    ecrire(banc.dossier, "y", moteur="inexistant")
    assert lancer_cli(banc, "--benchmarks", "y") == 1
    assert "moteur inconnu : y (moteur inexistant)" in capsys.readouterr().err
    assert not (banc.racine / "runs").exists()


def test_benchmark_inconnu_et_selection_vide(banc, capsys) -> None:
    ecrire(banc.dossier, "x")
    assert lancer_cli(banc, "--benchmarks", "absent") == 1
    assert "benchmark inconnu : absent" in capsys.readouterr().err
    assert lancer_cli(banc, "--socle", "--cible", "hf") == 1
    assert "aucun benchmark" in capsys.readouterr().err


def test_moteur_livre_mais_module_absent_est_une_erreur_du_benchmark(
    banc, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(moteurs.MOTEURS, "fantome", "slmsp.benchmarks.moteurs.fantome")
    ecrire(banc.dossier, "reel", moteur="fantome")
    ecrire(banc.dossier, "ok")
    assert lancer_cli(banc, "--socle") == 1
    resultats = {
        p.name: json.loads(p.read_text(encoding="utf-8"))
        for p in dossier_run(banc).glob("*--*.json")
    }
    assert resultats["reel--avant.json"]["statut"] == "erreur"
    assert resultats["ok--avant.json"]["statut"] == "ok"


def test_archivage_du_run(banc) -> None:
    ecrire(banc.dossier, "ok", quantification="les-deux")
    assert lancer_cli(banc, "--socle") == 0
    dossier = dossier_run(banc)
    run = json.loads((dossier / "run.json").read_text(encoding="utf-8"))
    assert run["type"] == "bench" and run["modele_ref"] == "base:modele-test"
    assert "python" in run["environnement"] and "os" in run["environnement"]
    for variante in ("avant", "apres"):
        resultat = ResultatBench.model_validate_json(
            (dossier / f"ok--{variante}.json").read_text(encoding="utf-8")
        )
        assert resultat.run_id == run["run_id"] and resultat.variante == variante
        assert resultat.scores == {"acc": 0.5}
        assert (resultat.outil, resultat.outil_version) == ("outil-factice", "9.9")
        assert (resultat.configuration.fewshot, resultat.configuration.limite) == (3, 10)
        assert resultat.duree_s >= 0 and resultat.statut == "ok"
    assert etats(dossier) == ["en_cours", "complet"]


def test_filtre_de_quantification(banc) -> None:
    ecrire(banc.dossier, "ok", quantification="les-deux")
    assert lancer_cli(banc, "--socle", "--quantification", "apres") == 0
    assert banc.appels == [("ok", "apres")]


def test_un_echec_ne_stoppe_pas_les_autres(banc, capsys) -> None:
    ecrire(banc.dossier, "casse")
    ecrire(banc.dossier, "saute")
    ecrire(banc.dossier, "suite")
    assert lancer_cli(banc, "--socle") == 1
    assert [nom for nom, _ in banc.appels] == ["casse", "saute", "suite"]
    dossier = dossier_run(banc)
    casse = json.loads((dossier / "casse--avant.json").read_text(encoding="utf-8"))
    assert casse["statut"] == "erreur" and "panne factice" in casse["motif"]
    saute = json.loads((dossier / "saute--avant.json").read_text(encoding="utf-8"))
    assert saute["statut"] == "saute" and saute["motif"] == "poids absents"
    assert (dossier / "suite--avant.json").exists()
    assert etats(dossier)[-1] == "partiel-erreur"
    assert "partiel-erreur" in capsys.readouterr().out


def test_sauts_seuls_laissent_le_run_complet(banc) -> None:
    ecrire(banc.dossier, "saute")
    assert lancer_cli(banc, "--socle") == 0


@pytest.fixture
def verrou_espion(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    prises: list[str] = []

    @contextmanager
    def faux(**options):
        prises.append(options.get("commande", ""))
        yield Path("gpu.lock")

    monkeypatch.setattr(orchestrateur, "verrou_gpu", faux)
    return prises


def test_verrou_gpu_pour_la_cible_hf(banc, verrou_espion) -> None:
    ecrire(banc.dossier, "poids", cible="hf")
    assert lancer_cli(banc, "--socle") == 0
    assert len(verrou_espion) == 1 and "base:modele-test" in verrou_espion[0]


def test_pas_de_verrou_en_gguf_cpu_mais_verrou_en_cuda(banc, verrou_espion) -> None:
    ecrire(banc.dossier, "serveur", cible="gguf")
    assert lancer_cli(banc, "--socle") == 0
    assert verrou_espion == []
    assert lancer_cli(banc, "--socle", "--variante-llamacpp", "cuda") == 0
    assert len(verrou_espion) == 1


def test_gpu_occupe_refuse_sans_ouvrir_de_run(banc, capsys) -> None:
    ecrire(banc.dossier, "poids", cible="hf")
    with verrou_gpu():
        assert lancer_cli(banc, "--socle") == 5
    assert "GPU occupé" in capsys.readouterr().err
    assert banc.appels == [] and not (banc.racine / "runs").exists()


def test_hf_exige_avant_quantification(banc) -> None:
    ecrire(banc.dossier, "mauvais", cible="hf", quantification="apres")
    with pytest.raises(ConfigurationInvalide, match="avant quantification"):
        config_bench.charger_benchmarks()


def test_nom_different_du_fichier(banc) -> None:
    ecrire(banc.dossier, "a")
    (banc.dossier / "b.toml").write_text(
        (banc.dossier / "a.toml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    with pytest.raises(ConfigurationInvalide, match="différent du nom du fichier"):
        config_bench.charger_benchmarks()


def test_modele_invalide(banc, capsys) -> None:
    ecrire(banc.dossier, "x")
    assert main(["bench", "run", "--modele", "n-importe-quoi", "--socle"]) == 1
    assert "modèle invalide" in capsys.readouterr().err


def test_outil_tiers_recoit_l_environnement_assaini(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HF_TOKEN", "jeton-factice")
    monkeypatch.setenv("HF_HUB_OFFLINE", "0")
    termine = moteurs.lancer_outil(
        [sys.executable, "-c", "import json,os;print(json.dumps(dict(os.environ)))"]
    )
    env = json.loads(termine.stdout)
    assert env["HF_HUB_OFFLINE"] == "1" and env["HF_DATASETS_OFFLINE"] == "1"
    assert "HF_TOKEN" not in env
    assert env["HF_HOME"].endswith(".cache-hf")


def test_registre_paresseux_n_importe_pas_les_moteurs_reels() -> None:
    assert "lm_eval" not in sys.modules and "sacrebleu" not in sys.modules
    assert set(moteurs.MOTEURS) == {"lm_eval", "traduction", "bfcl"}


def test_exception_hors_moteur_termine_le_run(banc, monkeypatch: pytest.MonkeyPatch) -> None:
    ecrire(banc.dossier, "ok")
    monkeypatch.setitem(
        moteurs._ENREGISTRES, "factice", lambda *_: SortieMoteur(scores={"acc": float("nan")})
    )
    with pytest.raises(Exception):  # noqa: B017, PT011
        lancer_cli(banc, "--socle")
    assert etats(dossier_run(banc))[-1] == "partiel-erreur"


def test_precision_gguf_reelle_consignee(banc) -> None:
    """granite-4.0-1b ne publie qu'un BF16 : la variante `avant` le dit dans le résultat."""
    ecrire(banc.dossier, "ok", quantification="les-deux")
    ecrire(banc.dossier, "qcm", cible="hf", quantification="avant")
    arguments = ["bench", "run", "--modele", "base:granite-4.0-1b", "--socle"]
    assert main([*arguments, "--racine", str(banc.racine)]) == 0
    dossier = dossier_run(banc)

    def precision(nom: str) -> str | None:
        texte = (dossier / f"{nom}.json").read_text(encoding="utf-8")
        return ResultatBench.model_validate_json(texte).precision_gguf

    assert precision("ok--avant") == "bf16"
    assert precision("ok--apres") == "q4_k_m"
    assert precision("qcm--avant") is None


def _selection(cible: str) -> list:
    return [SimpleNamespace(config=SimpleNamespace(cible=cible))]


@pytest.mark.parametrize(
    ("modele_ref", "cible", "attendu"),
    [
        ("base:bonsai-2-4b", "gguf", "prism-b10777-e3de715"),  # version réservée
        ("base:granite-4.0-1b", "gguf", "b11429"),  # version commune, inchangée
        ("base:bonsai-2-4b", "hf", None),  # aucune cible GGUF : pas de llama.cpp
        ("base:modele-inconnu", "gguf", None),  # configuration absente : le moteur le dira
    ],
)
def test_tag_llamacpp_du_run(tmp_path: Path, modele_ref: str, cible: str, attendu) -> None:
    assert orchestrateur._tag_llamacpp(modele_ref, tmp_path, _selection(cible)) == attendu


def test_tag_llamacpp_consigne_dans_run_json(banc, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(orchestrateur, "_tag_llamacpp", lambda *_a: "prism-b10777-e3de715")
    ecrire(banc.dossier, "ok")
    assert lancer_cli(banc, "--socle") == 0
    run = json.loads((dossier_run(banc) / "run.json").read_text(encoding="utf-8"))
    assert run["llamacpp_tag"] == "prism-b10777-e3de715"


def test_parallele_consigne_dans_run_json_et_contexte(banc) -> None:
    vus = []
    moteurs._ENREGISTRES["factice"] = lambda config, contexte: (
        vus.append(contexte.parallele) or SortieMoteur(scores={"acc": 1.0})
    )
    ecrire(banc.dossier, "ok")
    assert lancer_cli(banc, "--socle", "--parallele", "4") == 0
    run = json.loads((dossier_run(banc) / "run.json").read_text(encoding="utf-8"))
    assert vus == [4] and run["config"]["parallele"] == 4


def test_parallele_defaut_a_un(banc) -> None:
    ecrire(banc.dossier, "ok")
    assert lancer_cli(banc, "--socle") == 0
    run = json.loads((dossier_run(banc) / "run.json").read_text(encoding="utf-8"))
    assert run["config"]["parallele"] == 1


@pytest.mark.parametrize("valeur", ["0", "-2", "abc"])
def test_parallele_invalide_refuse_par_la_cli(banc, valeur, capsys) -> None:
    ecrire(banc.dossier, "ok")
    assert lancer_cli(banc, "--socle", "--parallele", valeur) != 0
    assert "--parallele" in capsys.readouterr().err
    assert not (banc.racine / "runs").exists()


def test_parallele_invalide_refuse_par_lancer(banc) -> None:
    with pytest.raises(ConfigurationInvalide, match="parallele"):
        orchestrateur.lancer("base:modele-test", [], racine=banc.racine, parallele=0)
