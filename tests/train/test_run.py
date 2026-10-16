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
from slmsp.core.artefacts import ouvrir_run
from slmsp.core.erreurs import CodeSortie, ConfigurationInvalide, LectureInterdite, RessourceOccupee
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


def test_reprise_refusee_si_la_config_change(projet, pile) -> None:
    projet.ecrire_jeu()
    run_id = _executer(projet, pile, projet.ecrire_toml())
    modifie = projet.ecrire_toml(hyperparametres={"pas_max": 9, "pas_sauvegarde": 2})
    with pytest.raises(ConfigurationInvalide, match="configuration résolue diffère"):
        module_run.executer(modifie, racine=projet.racine, pile=pile, reprendre_run=run_id)


def test_gpu_occupe(projet, pile) -> None:
    projet.ecrire_jeu()
    with verrou_gpu(commande="autre"), pytest.raises(RessourceOccupee):
        module_run.executer(projet.ecrire_toml(), racine=projet.racine, pile=pile)
    assert not (projet.racine / "runs" / "train").exists()


def test_orpo_lecture_de_l_adaptateur_sft_interdite(projet, pile, factices) -> None:
    projet.ecrire_jeu(lignes=[factices.paire(i) for i in range(1, 3)], fichier="preferences.jsonl")
    toml = projet.ecrire_toml("m4-orpo", methode="orpo", sft_run_id="20261016-120000-m1-qlora-abcd")
    with pytest.raises(LectureInterdite, match="adaptateur"):
        module_run.executer(toml, racine=projet.racine, pile=pile)


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
    monkeypatch.setattr(module_run, "chemin_autorise", lambda chemin, *a, **kw: chemin)
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
            "tache": "tache-factice",
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
