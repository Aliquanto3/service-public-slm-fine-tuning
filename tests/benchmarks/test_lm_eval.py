"""Moteur lm-eval : sous-processus remplacé par un faux exécutable, jamais de `lm_eval` réel."""

from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from slmsp.benchmarks.config import BenchmarkConfig
from slmsp.benchmarks.moteurs import ContexteBench, charger_moteur, lm_eval
from slmsp.benchmarks.taches_lmeval.agentpublic_mcq import utils
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas.bench import JeuBench

FIXTURES = Path(__file__).parent / "fixtures"
FAUX = FIXTURES / "lm_eval_factice.py"
REVISION = "a" * 40


def config(tache="tache_factice", cible="hf", **extra) -> BenchmarkConfig:
    donnees = {
        "nom": "bench_factice",
        "moteur": "lm_eval",
        "tache": tache,
        "fewshot": 3,
        "limite": 2000,
        "cible": cible,
        "quantification": "avant" if cible == "hf" else "les-deux",
        **extra,
    }
    return BenchmarkConfig(**donnees)


@pytest.fixture
def banc(tmp_path, monkeypatch) -> SimpleNamespace:
    modeles = tmp_path / "models"
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(modeles))
    journal = tmp_path / "journal.json"
    monkeypatch.setenv("LM_EVAL_FACTICE_JOURNAL", str(journal))
    monkeypatch.setattr(lm_eval, "commande_lm_eval", lambda: [sys.executable, str(FAUX)])

    def contexte(modele_ref="base:modele-factice", variante="avant") -> ContexteBench:
        run = SimpleNamespace(dossier=tmp_path / "run", run_id="x")
        return ContexteBench(modele_ref, variante, run, tmp_path, "cpu")  # type: ignore[arg-type]

    def appel() -> dict:
        return json.loads(journal.read_text(encoding="utf-8"))

    return SimpleNamespace(modeles=modeles, tmp=tmp_path, contexte=contexte, appel=appel)


def poser_poids(banc, nom="hf-bf16") -> Path:
    dossier = banc.modeles / "modele-factice" / nom
    dossier.mkdir(parents=True)
    (dossier / "config.json").write_text("{}", encoding="utf-8")
    return dossier


def option(argv: list[str], nom: str) -> str:
    return argv[argv.index(nom) + 1]


def test_analyse_metrique_valeur_erreur_standard_items_version():
    donnees = json.loads((FIXTURES / "sortie_lm_eval.json").read_text(encoding="utf-8"))
    sortie = lm_eval.analyser(donnees)
    assert sortie.scores == {
        "tache_factice.acc": 0.5,
        "tache_factice.acc_stderr": 0.05,
        "tache_factice.acc_norm": 0.25,
        "tache_factice.acc_norm_stderr": None,
        "tache_factice.prompt_level_strict_acc": 0.125,
        "tache_factice.prompt_level_strict_acc_stderr": None,
        "tache_factice.n_items": 8,
    }
    assert sortie.outil == "lm-eval"
    assert sortie.outil_version == "0.0.0-factice"
    assert sortie.details["taches"]["tache_factice"]["n_items"] == 8


def test_analyse_refuse_sortie_sans_resultats():
    with pytest.raises(lm_eval.LmEvalEchoue, match="results"):
        lm_eval.analyser({"versions": {}})


def test_hf_lance_les_poids_hf_avec_fewshot_limite_et_hors_ligne(banc):
    poids = poser_poids(banc)
    sortie = lm_eval.executer(config(), banc.contexte())
    argv = banc.appel()["argv"]
    assert sortie.saute is None
    assert option(argv, "--model") == "hf"
    assert option(argv, "--model_args") == f"pretrained={poids},dtype=bfloat16"
    assert option(argv, "--tasks") == "tache_factice"
    assert option(argv, "--num_fewshot") == "3"
    assert option(argv, "--limit") == "2000"
    assert Path(option(argv, "--include_path")).name == "taches_lmeval"
    env = banc.appel()["env"]
    assert env["HF_HUB_OFFLINE"] == env["HF_DATASETS_OFFLINE"] == "1"
    assert sortie.scores["tache_factice.acc"] == 0.5


def poser_cache_hf(banc, depot, revision):
    dossier = banc.modeles / ".cache-hf" / "hub" / f"datasets--{depot.replace('/', '--')}"
    (dossier / "snapshots" / revision).mkdir(parents=True)


def test_cache_hf_hors_pin_leve_avant_le_lancement(banc):
    poser_poids(banc)
    pins = {"jeux_hf": {"cais/mmlu": REVISION}}
    with pytest.raises(ConfigurationInvalide, match="absent"):
        lm_eval.executer(config(options=pins), banc.contexte())
    poser_cache_hf(banc, "cais/mmlu", "b" * 40)
    with pytest.raises(ConfigurationInvalide, match="b{40}"):
        lm_eval.executer(config(options=pins), banc.contexte())
    poser_cache_hf(banc, "cais/mmlu", REVISION)
    assert lm_eval.executer(config(options=pins), banc.contexte()).saute is None


def test_hf_prefere_hf_bf16_puis_hf(banc):
    poser_poids(banc, "hf")
    assert lm_eval.dossier_poids_hf("modele-factice").name == "hf"
    poser_poids(banc, "hf-bf16")
    assert lm_eval.dossier_poids_hf("modele-factice").name == "hf-bf16"


def test_qcm_saute_sans_poids_hf_avec_motif(banc):
    sortie = lm_eval.executer(config(), banc.contexte("base:ministral-3-8b"))
    assert sortie.saute is not None
    assert "poids HF absents" in sortie.saute
    assert "ministral-3-8b" in sortie.saute


def test_qcm_saute_pour_un_modele_affine(banc):
    sortie = lm_eval.executer(config(), banc.contexte("ft:20260101T000000-abcdef"))
    assert sortie.saute is not None


def test_mcq_eval_saute_si_jeu_non_epingle_ou_absent(banc):
    poser_poids(banc)
    sans_revision = config("agentpublic_mcq", jeux=[JeuBench(nom="mcq-eval", depot="A/B")])
    assert "non épinglé" in lm_eval.executer(sans_revision, banc.contexte()).saute
    epingle = config(
        "agentpublic_mcq", jeux=[JeuBench(nom="mcq-eval", depot="A/B", revision=REVISION)]
    )
    assert "absent" in lm_eval.executer(epingle, banc.contexte()).saute


def test_mcq_eval_lit_le_jeu_local_sans_reseau(banc):
    poser_poids(banc)
    jeu = banc.tmp / "data" / "raw" / "benchmarks" / "mcq-eval" / REVISION
    jeu.mkdir(parents=True)
    epingle = config(
        "agentpublic_mcq", jeux=[JeuBench(nom="mcq-eval", depot="A/B", revision=REVISION)]
    )
    lm_eval.executer(epingle, banc.contexte())
    appel = banc.appel()
    assert appel["env"]["SLMSP_MCQ_EVAL_DIR"] == str(jeu)
    assert appel["env"]["HF_DATASETS_OFFLINE"] == "1"


def test_ifeval_passe_par_local_chat_completions_vers_127_0_0_1(banc, monkeypatch):
    vu = []

    @contextmanager
    def faux_serveur(cfg, contexte):
        vu.append(contexte.variante)
        yield lm_eval.url_chat(8123), "modele-factice"

    monkeypatch.setattr(lm_eval, "serveur_llama", faux_serveur)
    cfg = config("ifeval", cible="gguf", fewshot=0, limite=None)
    for variante in ("avant", "apres"):
        sortie = lm_eval.executer(cfg, banc.contexte(variante=variante))
        argv = banc.appel()["argv"]
        assert option(argv, "--model") == "local-chat-completions"
        assert "base_url=http://127.0.0.1:8123/v1/chat/completions" in option(argv, "--model_args")
        assert "--apply_chat_template" in argv
        assert "--limit" not in argv
        assert banc.appel()["env"]["OPENAI_API_KEY"]
        assert sortie.saute is None
    assert vu == ["avant", "apres"]


def test_ifeval_base_url_deja_servi_ne_demarre_pas_de_serveur(banc):
    cfg = config(
        "ifeval", cible="gguf", options={"base_url": "http://127.0.0.1:9/v1/chat/completions"}
    )
    lm_eval.executer(cfg, banc.contexte())
    assert ":9/v1" in option(banc.appel()["argv"], "--model_args")


def test_ifeval_saute_si_le_gguf_de_la_variante_n_existe_pas(banc, monkeypatch):
    def refuse(*_a, **_k):
        raise ConfigurationInvalide("aucun GGUF F16 de base")

    monkeypatch.setattr(lm_eval, "resoudre_gguf", refuse)
    sortie = lm_eval.executer(config("ifeval", cible="gguf"), banc.contexte())
    assert "F16" in sortie.saute


def test_echec_du_sous_processus_leve_avec_la_queue_de_stderr(banc, monkeypatch):
    poser_poids(banc)
    monkeypatch.setenv("LM_EVAL_FACTICE_ECHEC", "1")
    with pytest.raises(lm_eval.LmEvalEchoue, match="code 3.*echec factice"):
        lm_eval.executer(config(), banc.contexte())


def test_sortie_json_absente_leve(banc, monkeypatch):
    poser_poids(banc)
    monkeypatch.setenv("LM_EVAL_FACTICE_SANS_SORTIE", "1")
    with pytest.raises(lm_eval.LmEvalEchoue, match="results"):
        lm_eval.executer(config(), banc.contexte())


def test_le_registre_charge_le_moteur_sans_importer_lm_eval():
    assert charger_moteur("lm_eval") is lm_eval.executer
    assert "lm_eval" not in sys.modules


# -- Tâche personnalisée MCQ-eval --


def test_yaml_de_la_tache_est_declare_hors_ligne():
    chemin = lm_eval.DOSSIER_TACHES / "agentpublic_mcq" / "agentpublic_mcq.yaml"
    texte = chemin.read_text(encoding="utf-8")
    assert "task: agentpublic_mcq" in texte
    assert "custom_dataset: !function utils.charger_jeu" in texte
    assert "output_type: multiple_choice" in texte
    assert "dataset_path" not in texte  # aucune référence au Hub


@pytest.mark.parametrize(
    ("ligne", "attendu"),
    [
        (
            {"question": "<q1>", "choices": ["<a>", "<b>"], "answer": 1},
            {"question": "<q1>", "choix": ["<a>", "<b>"], "reponse": 1},
        ),
        (
            {"question": "<q2>", "A": "<a>", "B": "<b>", "C": "<c>", "reponse": "C"},
            {"question": "<q2>", "choix": ["<a>", "<b>", "<c>"], "reponse": 2},
        ),
    ],
)
def test_normaliser_ligne(ligne, attendu):
    assert utils.normaliser_ligne(ligne) == attendu


def test_normaliser_ligne_refuse_reponse_hors_choix_ou_colonne_absente():
    with pytest.raises(ValueError):
        utils.normaliser_ligne({"question": "<q>", "choix": ["<a>"], "answer": 5})
    with pytest.raises(ValueError, match="choix"):
        utils.normaliser_ligne({"question": "<q>", "answer": 0})


def test_lire_lignes_jsonl_et_csv(tmp_path):
    (tmp_path / "a.jsonl").write_text(
        json.dumps({"question": "<q1>", "choix": ["<a>", "<b>"], "answer": "A"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "b.csv").write_text("question,A,B,answer\n<q2>,<a>,<b>,1\n", encoding="utf-8")
    (tmp_path / "LISEZMOI.md").write_text("ignoré", encoding="utf-8")
    lignes = utils.lire_lignes(tmp_path)
    assert [ligne["question"] for ligne in lignes] == ["<q1>", "<q2>"]
    assert [ligne["reponse"] for ligne in lignes] == [0, 1]
    with pytest.raises(FileNotFoundError):
        utils.lire_lignes(tmp_path / "vide")


def test_charger_jeu_exige_la_variable(monkeypatch):
    monkeypatch.delenv(utils.VARIABLE_DOSSIER, raising=False)
    with pytest.raises(RuntimeError, match=utils.VARIABLE_DOSSIER):
        utils.charger_jeu()


def test_resoudre_gguf_base_avant_exige_le_f16_telecharge(banc):
    with pytest.raises(ConfigurationInvalide, match="fetch modeles granite-4.0-1b --f16"):
        lm_eval.resoudre_gguf(banc.contexte("base:granite-4.0-1b", "avant"))
    from slmsp.inference.serveur import charger_config_modele

    gguf = banc.modeles / "granite-4.0-1b" / "gguf"
    gguf.mkdir(parents=True)
    (gguf / charger_config_modele("granite-4.0-1b").gguf_f16.fichier).write_bytes(b"x")
    slug, _config, chemin = lm_eval.resoudre_gguf(banc.contexte("base:granite-4.0-1b", "avant"))
    assert (slug, chemin.parent) == ("granite-4.0-1b", gguf)


def test_resoudre_gguf_base_avant_sans_gguf_f16_configure(banc, monkeypatch):
    import slmsp.inference.serveur as serveur

    sans = serveur.charger_config_modele("granite-4.0-1b").model_copy(update={"gguf_f16": None})
    monkeypatch.setattr(serveur, "charger_config_modele", lambda _slug: sans)
    with pytest.raises(ConfigurationInvalide, match="gguf_f16 absente"):
        lm_eval.resoudre_gguf(banc.contexte("base:granite-4.0-1b", "avant"))


def test_resoudre_gguf_base_apres_exige_le_fichier(banc):
    with pytest.raises(ConfigurationInvalide, match="GGUF absent"):
        lm_eval.resoudre_gguf(banc.contexte("base:granite-4.0-1b", "apres"))
    gguf = banc.modeles / "granite-4.0-1b" / "gguf"
    gguf.mkdir(parents=True)
    from slmsp.inference.serveur import charger_config_modele

    (gguf / charger_config_modele("granite-4.0-1b").gguf.fichier).write_bytes(b"x")
    slug, _config, chemin = lm_eval.resoudre_gguf(banc.contexte("base:granite-4.0-1b", "apres"))
    assert slug == "granite-4.0-1b"
    assert chemin.parent == gguf


@pytest.mark.gpu
@pytest.mark.lent
def test_reel_lm_eval_hf():
    pytest.skip("exécution réelle de lm_eval (extra bench, GPU) : à lancer à la main")


def test_base_url_non_locale_refusee(banc):
    cfg = config("ifeval", cible="gguf", options={"base_url": "http://exemple.org:9/v1/chat"})
    sortie = lm_eval.executer(cfg, banc.contexte())
    assert "127.0.0.1" in sortie.saute
    assert not banc.tmp.joinpath("journal.json").exists()


def test_analyser_tolere_sections_non_standard():
    donnees = {
        "results": {"t": {"acc,none": 0.5, "acc_stderr,none": "N/A"}, "g": "x"},
        "n-samples": None,
        "versions": [],
    }
    sortie = lm_eval.analyser(donnees)
    assert sortie.scores["t.acc"] == 0.5
    assert sortie.scores["t.acc_stderr"] is None
    with pytest.raises(lm_eval.LmEvalEchoue):
        lm_eval.analyser([])  # type: ignore[arg-type]


def test_graine_et_lot_dans_arguments_et_sortie() -> None:
    from slmsp.benchmarks.config import BenchmarkConfig
    from slmsp.benchmarks.moteurs.lm_eval import arguments_communs, arguments_hf, graine, taille_lot

    config = BenchmarkConfig(
        nom="t",
        moteur="lm_eval",
        tache="t",
        cible="hf",
        quantification="avant",
        options={"seed": 7, "batch_size": "4"},
    )
    assert graine(config) == 7
    assert taille_lot(config) == "4"
    args = arguments_communs(config, Path("x"))
    assert args[args.index("--seed") + 1] == "7"
    assert arguments_hf(Path("p"), "4")[-1] == "4"


def _classeur(chemin: Path, feuille: str, lignes: list[list[str]]) -> None:
    """Classeur xlsx minimal (chaînes en ligne), valeurs factices."""
    import zipfile
    from xml.sax.saxutils import escape

    def cellule(i: int, j: int, texte: str) -> str:
        return f'<c r="{chr(65 + j)}{i + 1}" t="inlineStr"><is><t>{escape(texte)}</t></is></c>'

    corps = "".join(
        f"<row>{''.join(cellule(i, j, t) for j, t in enumerate(ligne))}</row>"
        for i, ligne in enumerate(lignes)
    )
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    with zipfile.ZipFile(chemin, "w") as z:
        z.writestr(
            "xl/workbook.xml",
            f'<workbook xmlns="{ns}" xmlns:r="{rel}"><sheets>'
            f'<sheet name="{feuille}" sheetId="1" r:id="rId1"/></sheets></workbook>',
        )
        z.writestr(
            "xl/_rels/workbook.xml.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>',
        )
        z.writestr(
            "xl/worksheets/sheet1.xml",
            f'<worksheet xmlns="{ns}"><sheetData>{corps}</sheetData></worksheet>',
        )


def test_mcq_lit_la_feuille_xlsx_du_jeu_reel(tmp_path):
    entete = ["Question", "A", "B", "C", "D", "E", "Number_best_rep"]
    _classeur(
        tmp_path / "jeu.xlsx",
        utils.FEUILLE_XLSX,
        [
            entete,
            ["<q1>", "A. <a1>", "B. <b1>", "C. <c1>", "D. <d1>", "E. <e1>", "E"],
            ["<q2>", "A. <a2>", "B. <b2>", "", "", "E. <e2>", "Z"],
        ],
    )
    with pytest.raises(ValueError, match=r"ligne 3.*illisible"):
        utils.lire_lignes(tmp_path)
    _classeur(
        tmp_path / "jeu.xlsx",
        utils.FEUILLE_XLSX,
        [
            entete,
            ["<q1>", "A. <a1>", "B. <b1>", "C. <c1>", "D. <d1>", "E. <e1>", "E"],
            ["<q2>", "A. <a2>", "B. <b2>", "", "", "E. <e2>", "E (la B aussi)"],
        ],
    )
    _classeur(tmp_path / "autre.xlsx", "Sheet1", [["x"], ["y"]])
    lignes = utils.lire_lignes(tmp_path)
    assert lignes[0] == {
        "question": "<q1>",
        "choix": ["<a1>", "<b1>", "<c1>", "<d1>", "<e1>"],
        "reponse": 4,
    }
    assert lignes[1]["choix"] == ["<a2>", "<b2>", "<e2>"]
    assert lignes[1]["reponse"] == 2
    assert len(lignes) == 2


def test_env_outil_force_utf8_et_hf_hors_ligne():
    from slmsp.benchmarks.moteurs import env_outil

    env = env_outil({"HF_TOKEN": "<jeton-factice>"})
    assert env["PYTHONUTF8"] == "1"
    assert env["HF_HUB_OFFLINE"] == "1"
    assert "HF_TOKEN" not in env


@pytest.mark.parametrize(
    ("contenu", "attendu"),
    [
        ('{"architectures": ["Mistral3ForConditionalGeneration"]}', "hf-mistral3"),
        ('{"architectures": ["Qwen3ForCausalLM"]}', "hf"),
        ("{}", "hf"),
        ('{"architectures": "Mistral3ForConditionalGeneration"}', "hf"),
        ("pas du json", "hf"),
        ('{"architectures": [["X"], {"a": 1}]}', "hf"),
        ('﻿{"architectures": ["Mistral3ForConditionalGeneration"]}', "hf-mistral3"),
    ],
)
def test_modele_hf_selon_l_architecture(tmp_path, contenu, attendu):
    (tmp_path / "config.json").write_text(contenu, encoding="utf-8")
    assert lm_eval.modele_hf(tmp_path) == attendu


def test_modele_hf_sans_config_json(tmp_path):
    assert lm_eval.modele_hf(tmp_path) == "hf"


def test_hf_mistral3_lance_l_adaptateur_dedie(banc):
    poids = poser_poids(banc)
    (poids / "config.json").write_text(
        '{"architectures": ["Mistral3ForConditionalGeneration"]}', encoding="utf-8"
    )
    assert lm_eval.executer(config(), banc.contexte()).saute is None
    argv = banc.appel()["argv"]
    assert option(argv, "--model") == "hf-mistral3"
    assert option(argv, "--model_args") == f"pretrained={poids},dtype=bfloat16"
