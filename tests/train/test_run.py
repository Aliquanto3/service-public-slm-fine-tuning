"""`slmsp train run` (story 10.4) : campagne, verrou, checkpoints, reprise, coûts.

Pile simulée (conftest) pour les tests unitaires ; le test réel sur un modèle minuscule à
poids aléatoires est marqué `lent` et sauté sans l'extra `train`. Contenus factices (D1).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

from slmsp.cli import main
from slmsp.core.artefacts import nouveau_run, ouvrir_run
from slmsp.core.erreurs import CodeSortie, ConfigurationInvalide, RessourceOccupee
from slmsp.core.var import verrou_gpu
from slmsp.train import run as module_run


def _executer(projet, pile, toml: Path, **kw) -> str:
    sorties: list[str] = []
    code = module_run.executer(toml, racine=projet.racine, pile=pile, sortie=sorties.append, **kw)
    assert code == 0, sorties
    return sorties[0].split()[1]


def _json(chemin: Path) -> dict:
    return json.loads(chemin.read_text(encoding="utf-8"))


def test_deux_methodes_meme_campagne(projet, pile) -> None:
    projet.ecrire_jeu()
    m1 = _executer(projet, pile, projet.ecrire_toml("m1-qlora", methode="qlora"))
    m2 = _executer(projet, pile, projet.ecrire_toml("m2-lora", methode="lora"))
    runs = [ouvrir_run(i, racine=projet.racine) for i in (m1, m2)]
    assert [r.statut_courant() for r in runs] == ["complet", "complet"]
    configs = [r.manifeste.config for r in runs]
    assert [c["plan"]["methode"] for c in configs] == ["qlora", "lora"]
    assert configs[0]["invariants"] == configs[1]["invariants"]
    assert {k for k in configs[0]["toml"] if configs[0]["toml"][k] != configs[1]["toml"][k]} == {
        "methode"
    }
    for run in runs:
        dossier = run.dossier
        assert run.manifeste.chat_template_sha256 and run.manifeste.jeu_version == "v1"
        assert (dossier / "checkpoints" / "checkpoint-2").is_dir()
        assert (dossier / "adaptateur" / "adapter_config.json").is_file()
        couts = _json(dossier / "couts.json")
        assert couts["graine"] == 7 and couts["config"] == run.manifeste.config
        assert "environnement" in couts and couts["pas"] == 4
        arguments = run.lire_jsonl("entrainement.jsonl")[0]["arguments"]
        assert "save_total_limit" not in arguments and arguments["report_to"] == "none"
        assert not Path(arguments["output_dir"]).is_absolute()
        assert _json(dossier / "jeu.json")["retenus"] == 3
    assert m1.split("-", 2)[2].startswith("m1-qlora-")


def test_graine_avant_modele_et_adaptateur_neuf(projet, pile) -> None:
    projet.ecrire_jeu()
    _executer(projet, pile, projet.ecrire_toml("m1-qlora"))
    _executer(projet, pile, projet.ecrire_toml("m3-dora", methode="dora"))
    assert pile.ordre == ["graine:7", "modele", "adaptateur"] * 2
    assert pile.lora[1]["use_dora"] is True and "use_dora" not in pile.lora[0]


@pytest.mark.parametrize(("cle", "valeur"), [("graine", 8), ("longueur_max", 512)])
def test_campagne_refuse_un_invariant_different(projet, pile, cle: str, valeur: int) -> None:
    projet.ecrire_jeu()
    _executer(projet, pile, projet.ecrire_toml("m1-qlora"))
    with pytest.raises(ConfigurationInvalide, match=f"« {cle} » diffère"):
        module_run.executer(
            projet.ecrire_toml("m2-lora", methode="lora", **{cle: valeur}),
            racine=projet.racine,
            pile=pile,
        )
    autre = projet.ecrire_toml("m2-autre", methode="lora", campagne="autre", **{cle: valeur})
    _executer(projet, pile, autre)


def test_jeu_absent_consigne_bloque(projet, pile) -> None:
    sorties: list[str] = []
    code = module_run.executer(
        projet.ecrire_toml(), racine=projet.racine, pile=pile, sortie=sorties.append
    )
    assert code == 1 and pile.ordre == []
    (dossier,) = (projet.racine / "runs" / "train").iterdir()
    etat = [
        json.loads(ligne)
        for ligne in (dossier / "etat.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert etat[-1]["statut"] == "partiel-erreur"
    assert etat[-1]["motif"].startswith("bloqué : aucun jeu construit")
    toml = ouvrir_run(dossier.name, racine=projet.racine).manifeste.config["toml"]
    assert "precision_base" not in toml  # absente au défaut, comme dans un run lancé


def test_reprise_sur_le_dernier_checkpoint(projet, pile) -> None:
    projet.ecrire_jeu()
    toml = projet.ecrire_toml(hyperparametres={"pas_max": 6, "pas_sauvegarde": 2})
    pile.interrompre_apres = 4
    with pytest.raises(KeyboardInterrupt):
        module_run.executer(toml, racine=projet.racine, pile=pile, sortie=lambda _m: None)
    (dossier,) = (projet.racine / "runs" / "train").iterdir()
    run = ouvrir_run(dossier.name, racine=projet.racine)
    assert run.statut_courant() == "interrompu"
    assert (dossier / "couts.json").is_file() and not (dossier / "adaptateur").exists()

    pile.interrompre_apres = None
    assert _executer(projet, pile, toml, reprendre_run=run.run_id) == run.run_id
    assert pile.trainers[-1].reprise.endswith("checkpoint-4")
    assert _json(dossier / "couts-2.json")["segment"] == 2
    assert run.statut_courant() == "complet"
    assert [ligne["checkpoint_depart"] for ligne in run.lire_jsonl("entrainement.jsonl")] == [
        None,
        "checkpoint-4",
    ]
    with pytest.raises(Exception, match="déjà complet"):
        module_run.executer(toml, racine=projet.racine, pile=pile, reprendre_run=run.run_id)


def test_decoupage_par_defaut_absent_de_la_config_resolue(projet, pile) -> None:
    """Un run antérieur au découpage par tour (sans la clé) reste reprenable."""
    projet.ecrire_jeu()
    toml = projet.ecrire_toml(hyperparametres={"pas_max": 6, "pas_sauvegarde": 2})
    pile.interrompre_apres = 4
    with pytest.raises(KeyboardInterrupt):
        module_run.executer(toml, racine=projet.racine, pile=pile, sortie=lambda _m: None)
    (dossier,) = (projet.racine / "runs" / "train").iterdir()
    config = ouvrir_run(dossier.name, racine=projet.racine).manifeste.config
    assert "decoupage_masque" not in config["invariants"]
    assert "decoupage_masque" not in config["modele"]
    assert set(config["invariants"]) == set(module_run.CLES_INVARIANTS) - {
        "decoupage_masque",
        "precision_base",
    }
    pile.interrompre_apres = None
    assert _executer(projet, pile, toml, reprendre_run=dossier.name) == dossier.name


def test_invariants_portent_le_decoupage_par_tour(projet) -> None:
    toml = projet.ecrire_toml()
    from slmsp.train.config import charger_run_config

    config = charger_run_config(toml)
    empreinte = {"mode": "par-tour", "bloc_amorce": "<b>"}
    avec = module_run.invariants(
        config, jeu_build="b", chat_template_sha256="s", decoupage_masque=empreinte
    )
    sans = module_run.invariants(config, jeu_build="b", chat_template_sha256="s")
    assert avec == {**sans, "decoupage_masque": empreinte} and "decoupage_masque" not in sans


def test_invariant_precision_base_et_retrocompatibilite(projet, pile) -> None:
    from slmsp.train.config import charger_run_config

    defaut = charger_run_config(projet.ecrire_toml("m1-defaut"))
    bf16 = charger_run_config(projet.ecrire_toml("m1-bf16", precision_base="bf16"))
    sans = module_run.invariants(defaut, jeu_build="b", chat_template_sha256="s")
    avec = module_run.invariants(bf16, jeu_build="b", chat_template_sha256="s")
    assert "precision_base" not in sans  # run d'avant : clé absente = fp32-kbit
    assert avec == {**sans, "precision_base": "bf16"}


def test_campagne_refuse_une_precision_base_differente(projet, pile) -> None:
    projet.ecrire_jeu()
    _executer(projet, pile, projet.ecrire_toml("m1-defaut"))  # run sans la clé
    with pytest.raises(ConfigurationInvalide, match="« precision_base » diffère"):
        module_run.executer(
            projet.ecrire_toml("m3-bf16", methode="dora", precision_base="bf16"),
            racine=projet.racine,
            pile=pile,
        )


def test_run_bf16_archive_la_precision_et_se_reprend(projet, pile) -> None:
    projet.ecrire_jeu()
    toml = projet.ecrire_toml(
        precision_base="bf16", hyperparametres={"pas_max": 6, "pas_sauvegarde": 2}
    )
    pile.interrompre_apres = 4
    with pytest.raises(KeyboardInterrupt):
        module_run.executer(toml, racine=projet.racine, pile=pile, sortie=lambda _m: None)
    (dossier,) = (projet.racine / "runs" / "train").iterdir()
    config = ouvrir_run(dossier.name, racine=projet.racine).manifeste.config
    assert config["invariants"]["precision_base"] == "bf16"
    assert config["toml"]["precision_base"] == "bf16"
    assert pile.appels_base == ["grads"]
    pile.interrompre_apres = None
    assert _executer(projet, pile, toml, reprendre_run=dossier.name) == dossier.name
    assert pile.appels_base == ["grads", "grads"]


def test_run_defaut_appelle_prepare_kbit_et_omet_la_cle(projet, pile) -> None:
    projet.ecrire_jeu()
    _executer(projet, pile, projet.ecrire_toml())
    assert pile.appels_base == ["kbit"]
    (dossier,) = (projet.racine / "runs" / "train").iterdir()
    config = ouvrir_run(dossier.name, racine=projet.racine).manifeste.config
    assert "precision_base" not in config["toml"]


def test_reprise_refusee_si_la_config_change(projet, pile) -> None:
    projet.ecrire_jeu()
    run_id = _executer(projet, pile, projet.ecrire_toml())
    modifie = projet.ecrire_toml(hyperparametres={"pas_max": 9, "pas_sauvegarde": 2})
    with pytest.raises(ConfigurationInvalide, match="configuration résolue diffère"):
        module_run.executer(modifie, racine=projet.racine, pile=pile, reprendre_run=run_id)


def test_modele_non_entrainable_refuse(projet, pile, monkeypatch) -> None:
    reel = module_run.charger_config_modele

    def non_entrainable(slug: str):
        return reel(slug).model_copy(update={"entrainable": False})

    monkeypatch.setattr(module_run, "charger_config_modele", non_entrainable)
    with pytest.raises(ConfigurationInvalide, match="non entraînable"):
        module_run.executer(projet.ecrire_toml(), racine=projet.racine, pile=pile)
    assert pile.ordre == [] and not (projet.racine / "runs").exists()


@pytest.mark.parametrize("slug", ["qwen3.5-2b", "qwen3.5-0.8b"])
def test_hybrides_gated_deltanet_refuses(projet, pile, slug: str) -> None:
    """Décision D8 : les Qwen3.5 hybrides sont réservés à la Baseline (fiches réelles)."""
    with pytest.raises(ConfigurationInvalide, match="non entraînable"):
        module_run.executer(projet.ecrire_toml(modele=slug), racine=projet.racine, pile=pile)
    assert pile.ordre == [] and not (projet.racine / "runs").exists()


def test_gpu_occupe(projet, pile) -> None:
    projet.ecrire_jeu()
    with verrou_gpu(commande="autre"), pytest.raises(RessourceOccupee):
        module_run.executer(projet.ecrire_toml(), racine=projet.racine, pile=pile)
    assert not (projet.racine / "runs" / "train").exists()


def _run_sft(projet, statut: str, *, type_run: str = "train", adaptateur: bool = True) -> str:
    run = nouveau_run(type_run, "m1-qlora", {}, racine=projet.racine)
    if adaptateur:
        (run.dossier / "adaptateur").mkdir()
        for nom in module_run.FICHIERS_ADAPTATEUR:
            (run.dossier / "adaptateur" / nom).write_text("{}", encoding="utf-8")
    run.terminer(statut)
    return run.run_id


@pytest.mark.parametrize(
    ("statut", "type_run", "adaptateur", "motif"),
    [
        (None, "train", True, "run illisible"),
        ("complet", "train", False, "adaptateur SFT absent"),
        ("partiel-erreur", "train", True, "run SFT partiel-erreur, pas complet"),
        ("interrompu", "train", True, "run SFT interrompu, pas complet"),
        ("complet", "export", True, "pas train"),
    ],
)
def test_orpo_exige_un_sft_complet(projet, pile, factices, statut, type_run, adaptateur, motif):
    """AD-24 étendu (A1) : l'adaptateur SFT est lisible, d'un run `train` complet et entier."""
    projet.ecrire_jeu(lignes=[factices.paire(i) for i in range(1, 3)], fichier="preferences.jsonl")
    sft = (
        "20261016-120000-m1-qlora-abcd"
        if statut is None
        else _run_sft(projet, statut, type_run=type_run, adaptateur=adaptateur)
    )
    toml = projet.ecrire_toml("m4-orpo", methode="orpo", sft_run_id=sft)
    with pytest.raises(ConfigurationInvalide, match=motif):
        module_run.executer(toml, racine=projet.racine, pile=pile)
    assert pile.trainers == []


def test_cli_jeu_absent(projet, capsys: pytest.CaptureFixture[str]) -> None:
    toml = projet.ecrire_toml()
    assert main(["train", "run", "--config", str(toml), "--racine", str(projet.racine)]) == 1
    assert "bloqué" in capsys.readouterr().out


def test_cli_config_obligatoire() -> None:
    assert main(["train", "run"]) == CodeSortie.USAGE


def test_dernier_checkpoint(tmp_path: Path) -> None:
    assert module_run.dernier_checkpoint(tmp_path / "absent") is None
    for nom in ("checkpoint-9", "checkpoint-10", "checkpoint-11", "checkpoint-x", "autre"):
        (tmp_path / nom).mkdir()
        if nom != "checkpoint-11":  # sauvegarde interrompue : pas de trainer_state.json
            for fichier in module_run.FICHIERS_CHECKPOINT:
                (tmp_path / nom / fichier).write_text("{}", encoding="utf-8")
    assert module_run.dernier_checkpoint(tmp_path).name == "checkpoint-10"


def test_cli_reprendre_sans_valeur(projet) -> None:
    toml = projet.ecrire_toml()
    assert main(["train", "run", "--config", str(toml), "--reprendre"]) == CodeSortie.USAGE


def test_reprise_apres_adaptateur_sauvegarde(projet, pile, monkeypatch) -> None:
    projet.ecrire_jeu()
    toml = projet.ecrire_toml()
    terminer = module_run.Run.terminer

    def arret(self, statut, *args, **kw):
        if statut == "complet":
            raise KeyboardInterrupt  # arrêt entre save_pretrained et la fin du run
        return terminer(self, statut, *args, **kw)

    monkeypatch.setattr(module_run.Run, "terminer", arret)
    with pytest.raises(KeyboardInterrupt):
        module_run.executer(toml, racine=projet.racine, pile=pile, sortie=lambda _m: None)
    monkeypatch.setattr(module_run.Run, "terminer", terminer)
    (dossier,) = (projet.racine / "runs" / "train").iterdir()
    entraines = len(pile.trainers)
    assert _executer(projet, pile, toml, reprendre_run=dossier.name) == dossier.name
    assert len(pile.trainers) == entraines  # aucun réentraînement
    assert ouvrir_run(dossier.name, racine=projet.racine).statut_courant() == "complet"


def test_orpo_meme_campagne_que_sft(projet, pile, factices, monkeypatch) -> None:
    """M4 lit `preferences.jsonl` du même build que M1 : la campagne l'accepte."""
    dossier = projet.ecrire_jeu()
    m1 = _executer(projet, pile, projet.ecrire_toml("m1-qlora"))
    sha_train = hashlib.sha256((dossier / "train.jsonl").read_bytes()).hexdigest()
    projet.ecrire_jeu(
        lignes=[factices.paire(i) for i in range(1, 3)],
        fichier="preferences.jsonl",
        manifeste={"sha256_train": sha_train},
    )
    monkeypatch.setitem(sys.modules, "trl.experimental.orpo", pile.orpo)
    toml = projet.ecrire_toml("m4-orpo", methode="orpo", sft_run_id=m1)
    m4 = _executer(projet, pile, toml)
    entraineur = pile.trainers[-1]
    assert entraineur.collateur is None and entraineur.args.beta == 0.1
    (exemple, _) = entraineur.jeu
    assert set(exemple) == {"prompt", "chosen", "rejected"}
    assert exemple["prompt"].endswith("<|assistant|>")
    assert exemple["chosen"].startswith("<retenue-factice-1>")
    assert exemple["rejected"].startswith("<rejetee-factice-1>")
    assert f"sft:{m1}" in pile.ordre
    config = ouvrir_run(m4, racine=projet.racine).manifeste.config
    assert (
        config["invariants"] == ouvrir_run(m1, racine=projet.racine).manifeste.config["invariants"]
    )


# --- Test réel : modèle minuscule à poids aléatoires, deux pas sur CPU ------------------------


@pytest.mark.lent
def test_run_reel_modele_minuscule(projet) -> None:
    for nom in ("torch", "transformers", "peft", "trl", "datasets", "tokenizers"):
        pytest.importorskip(nom)
    import transformers  # noqa: PLC0415
    from tokenizers import Tokenizer, models, pre_tokenizers  # noqa: PLC0415

    from slmsp.train import environnement  # noqa: PLC0415

    poids = projet.modeles / "granite-4.0-1b" / "hf"
    vocab = {f"t{i}": i for i in range(200)} | {"<unk>": 200, "<pad>": 201}
    brut = Tokenizer(models.WordLevel(vocab, unk_token="<unk>"))
    brut.pre_tokenizer = pre_tokenizers.Whitespace()
    tokenizer = transformers.PreTrainedTokenizerFast(
        tokenizer_object=brut, unk_token="<unk>", pad_token="<pad>", eos_token="<unk>"
    )
    tokenizer.chat_template = (
        "{% for m in messages %}{{ m['role'] }} {{ m['content'] }} {% endfor %}"
        "{% if add_generation_prompt %}assistant {% endif %}"
    )
    tokenizer.save_pretrained(str(poids))
    config = transformers.LlamaConfig(
        vocab_size=202,
        hidden_size=16,
        intermediate_size=32,
        num_hidden_layers=1,
        num_attention_heads=2,
        num_key_value_heads=2,
    )
    transformers.LlamaForCausalLM(config).save_pretrained(str(poids))
    lignes = []
    for i in range(1, 5):
        ligne = {
            "messages": [
                {"role": "system", "content": "t1 t2"},
                {"role": "user", "content": f"t{i} t3"},
                {"role": "assistant", "content": f"t{10 + i} t{20 + i}"},
            ],
            "tache": "RD",
            "meta": {"appel_ids": [f"appel-{i}"]},
        }
        lignes.append(ligne)
    projet.ecrire_jeu(lignes=lignes)
    toml = projet.ecrire_toml(
        "m2-lora",
        methode="lora",
        hyperparametres={"pas_max": 2, "pas_sauvegarde": 1, "accumulation": 1},
    )
    code = module_run.executer(
        toml, racine=projet.racine, pile=environnement.charger_pile(), cpu=True
    )
    assert code == 0
    (dossier,) = (projet.racine / "runs" / "train").iterdir()
    assert (dossier / "checkpoints" / "checkpoint-2").is_dir()
    assert (dossier / "adaptateur").is_dir() and (dossier / "couts.json").is_file()


# --- Hybrides Gated DeltaNet : noyaux fla (story B1) -----------------------------------------

CONFIG_HYBRIDE = {
    "model_type": "qwen3_5",
    "architectures": ["FauxQwen35ForConditionalGeneration"],
    "vocab_size": 100,
    "text_config": {"layer_types": ["linear_attention", "linear_attention", "full_attention"]},
}


def _hybride(projet, pile, monkeypatch, *, chunk: str, fla_installe: bool = True) -> None:
    """Fiche factice à couches `linear_attention` (les fiches Qwen3.5 restent non entraînables)."""
    (projet.modeles / "granite-4.0-1b" / "hf" / "config.json").write_text(
        json.dumps(CONFIG_HYBRIDE), encoding="utf-8"
    )
    origine = "fla.ops.gated_delta_rule" if chunk == "fla" else "transformers.models.qwen3_5"

    def implementation(*_a, **_k) -> None:
        return None

    implementation.__module__ = origine

    def enveloppe(*args, **kwargs):
        return implementation(*args, **kwargs)

    module = type(sys)("faux_modeling_qwen35_run")
    module.torch_chunk_gated_delta_rule = enveloppe
    module.causal_conv1d_fn = enveloppe
    monkeypatch.setitem(sys.modules, module.__name__, module)
    pile.transformers.FauxQwen35ForConditionalGeneration = type(
        "FauxQwen35ForConditionalGeneration", (), {"__module__": module.__name__}
    )
    monkeypatch.setattr(
        module_run.environnement,
        "noyaux_gdn_disponibles",
        lambda: {"fla": fla_installe, "triton": fla_installe},
    )


def test_run_hybride_refuse_sans_fla_avant_verrou(projet, pile, monkeypatch) -> None:
    projet.ecrire_jeu()
    _hybride(projet, pile, monkeypatch, chunk="fla", fla_installe=False)

    def charger_pile_interdit():
        raise AssertionError("pile chargée avant le refus")

    monkeypatch.setattr(module_run.environnement, "charger_pile", charger_pile_interdit)
    with pytest.raises(ConfigurationInvalide, match=r"--extra gdn"):
        module_run.executer(projet.ecrire_toml(), racine=projet.racine, pile=None)
    assert pile.ordre == [] and not (projet.racine / "runs").exists()


def test_run_hybride_refuse_si_repli_sans_option(projet, pile, monkeypatch) -> None:
    projet.ecrire_jeu()
    _hybride(projet, pile, monkeypatch, chunk="torch")
    with pytest.raises(ConfigurationInvalide, match="repli torch"):
        module_run.executer(projet.ecrire_toml(), racine=projet.racine, pile=pile)
    assert pile.trainers == [] and not (projet.racine / "runs").exists()


def test_run_hybride_repli_torch_alerte(projet, pile, monkeypatch) -> None:
    projet.ecrire_jeu()
    _hybride(projet, pile, monkeypatch, chunk="torch", fla_installe=False)
    run_id = _executer(projet, pile, projet.ecrire_toml(repli_torch=True))
    run = ouvrir_run(run_id, racine=projet.racine)
    noyaux = _json(run.dossier / "noyaux.json")
    assert (
        noyaux["chunk_gated_delta_rule"] == "torch" and "chunk_gated_delta_rule" in noyaux["replis"]
    )
    evenements = [ligne["evenement"] for ligne in run.lire_jsonl("log.jsonl")]
    assert "noyaux" in evenements and "alerte" in evenements
    assert run.manifeste.config["toml"]["repli_torch"] is True


def test_run_noyaux_hors_run_json_et_invariants(projet, pile, monkeypatch) -> None:
    projet.ecrire_jeu()
    _hybride(projet, pile, monkeypatch, chunk="fla")
    run_id = _executer(projet, pile, projet.ecrire_toml())
    run = ouvrir_run(run_id, racine=projet.racine)
    assert _json(run.dossier / "noyaux.json")["chunk_gated_delta_rule"] == "fla"
    evenements = [ligne["evenement"] for ligne in run.lire_jsonl("log.jsonl")]
    assert "noyaux" in evenements and "alerte" not in evenements
    config = run.manifeste.config
    assert "repli_torch" not in config["toml"]  # absente au défaut
    assert "noyaux" not in json.dumps(config)
    assert not any("noyaux" in cle for cle in module_run.CLES_INVARIANTS)


def test_reprise_run_anterieur_sans_repli_torch(projet, pile, monkeypatch) -> None:
    projet.ecrire_jeu()
    toml = projet.ecrire_toml()
    terminer = module_run.Run.terminer

    def arret(self, statut, *args, **kw):
        if statut == "complet":
            raise KeyboardInterrupt
        return terminer(self, statut, *args, **kw)

    monkeypatch.setattr(module_run.Run, "terminer", arret)
    with pytest.raises(KeyboardInterrupt):
        module_run.executer(toml, racine=projet.racine, pile=pile, sortie=lambda _m: None)
    monkeypatch.setattr(module_run.Run, "terminer", terminer)
    (dossier,) = (projet.racine / "runs" / "train").iterdir()
    # Un run créé avant B1 n'a pas la clé : la config résolue d'aujourd'hui doit le reprendre.
    assert (
        "repli_torch" not in ouvrir_run(dossier.name, racine=projet.racine).manifeste.config["toml"]
    )
    assert _executer(projet, pile, toml, reprendre_run=dossier.name) == dossier.name
