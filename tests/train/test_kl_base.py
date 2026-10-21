"""Régularisation KL vers la base (story 16.6a) : perte, masque, entraîneur, config, run."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.core.artefacts import ouvrir_run
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.train import kl_base, methodes
from slmsp.train import run as module_run
from slmsp.train.config import RunConfig
from slmsp.train.masque import IGNORE

torch = pytest.importorskip("torch")


def _config(methode: str = "qlora", **hp: object) -> RunConfig:
    return RunConfig.model_validate(
        {
            "campagne": "c",
            "modele": "m",
            "methode": methode,
            "jeu_version": "v1",
            "graine": 5,
            "longueur_max": 128,
            "hyperparametres": hp,
            **({"sft_run_id": "20261016-120000-m1-abcd"} if methode == "orpo" else {}),
        }
    )


# --- Perte : KL par token sur le masque de la réponse ----------------------------------------


def test_kl_nulle_quand_eleve_egal_base() -> None:
    logits = torch.randn(2, 5, 7)
    labels = torch.tensor([[IGNORE, IGNORE, 3, 4, 1], [IGNORE, 2, 2, IGNORE, IGNORE]])
    somme, n = kl_base.somme_kl(torch, logits, logits.clone(), labels)
    assert n == 5 and float(somme) == pytest.approx(0.0, abs=1e-7)


def test_masque_respecte() -> None:
    """Seules les positions t dont le label t + 1 est supervisé comptent (décalage causal)."""
    torch.manual_seed(0)
    base = torch.randn(1, 4, 6)
    labels = torch.tensor([[IGNORE, IGNORE, 5, IGNORE]])  # seule la position 1 compte
    eleve = base.clone()
    eleve[0, 0] += 3.0  # position 0 → label 1 ignoré
    eleve[0, 2:] += 3.0  # position 2 → label 3 ignoré ; position 3 sans label suivant
    somme, n = kl_base.somme_kl(torch, eleve, base, labels)
    assert n == 1 and float(somme) == pytest.approx(0.0, abs=1e-7)
    eleve[0, 1, 0] += 3.0  # position supervisée
    somme, _ = kl_base.somme_kl(torch, eleve, base, labels)
    log_p, log_q = torch.log_softmax(eleve[0, 1], -1), torch.log_softmax(base[0, 1], -1)
    attendu = float((log_p.exp() * (log_p - log_q)).sum())
    assert float(somme) == pytest.approx(attendu, rel=1e-5) and attendu > 0


def test_temperature_adoucit_et_multiplie_par_t_carre() -> None:
    torch.manual_seed(1)
    eleve, base = torch.randn(1, 3, 5), torch.randn(1, 3, 5)
    labels = torch.tensor([[IGNORE, 1, 2]])
    t2, _ = kl_base.somme_kl(torch, eleve, base, labels, temperature=2.0)
    t1, _ = kl_base.somme_kl(torch, eleve / 2, base / 2, labels)
    assert float(t2) == pytest.approx(4 * float(t1), rel=1e-5)


# --- Entraîneur : perte totale, base sans adaptateur, journal ---------------------------------


def _modele_peft():
    transformers = pytest.importorskip("transformers")
    peft = pytest.importorskip("peft")
    torch.manual_seed(0)
    config = transformers.LlamaConfig(
        vocab_size=32,
        hidden_size=16,
        intermediate_size=32,
        num_hidden_layers=1,
        num_attention_heads=2,
        num_key_value_heads=2,
    )
    modele = transformers.LlamaForCausalLM(config)
    lora = peft.LoraConfig(r=2, lora_alpha=4, target_modules="all-linear", task_type="CAUSAL_LM")
    return peft.get_peft_model(modele, lora)


class _BaseFactice:
    """Tient lieu de `SFTTrainer` : entropie croisée du modèle, `log` enregistré."""

    def __init__(self, *, model: Any, model_accepts_loss_kwargs: bool = False, **kw: Any) -> None:
        self.model, self.model_accepts_loss_kwargs = model, model_accepts_loss_kwargs
        self.state = SimpleNamespace(global_step=3)
        self.logs: list[dict[str, float]] = []

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        sorties = model(**inputs)
        return (sorties.loss, sorties) if return_outputs else sorties.loss

    def log(self, logs: dict[str, float], start_time: float | None = None) -> None:
        self.logs.append(logs)


def _entraineur(modele: Any, poids: float = 0.5, **kw: Any) -> Any:
    lignes: list[dict[str, Any]] = []
    classe = kl_base.classe_entraineur_kl(_BaseFactice, torch)
    entraineur = classe(model=modele, kl_base=poids, journal=lignes.append, **kw)
    return entraineur, lignes


def _entrees() -> dict[str, Any]:
    ids = torch.tensor([[1, 2, 3, 4, 5, 6]])
    labels = torch.tensor([[IGNORE, IGNORE, IGNORE, 4, 5, 6]])
    return {"input_ids": ids, "attention_mask": torch.ones_like(ids), "labels": labels}


def test_kl_nulle_avec_adaptateur_neuf() -> None:
    """`lora_B` nul à l'initialisation : élève = base, perte = entropie croisée."""
    modele = _modele_peft()
    entraineur, _ = _entraineur(modele)
    perte = entraineur.compute_loss(modele, _entrees())
    entropie = modele(**_entrees()).loss
    assert float(perte.detach()) == pytest.approx(float(entropie.detach()), abs=1e-6)
    assert entraineur._lots_kl[0][1] == pytest.approx(0.0, abs=1e-6)


def test_kl_positive_et_base_sans_gradient_apres_deplacement_de_l_adaptateur() -> None:
    modele = _modele_peft()
    with torch.no_grad():
        for nom, p in modele.named_parameters():
            if "lora_B" in nom:
                p.normal_(0, 0.5)
    entraineur, lignes = _entraineur(modele, poids=2.0)
    perte = entraineur.compute_loss(modele, _entrees())
    entropie, kl = entraineur._lots_kl[0]
    assert kl > 0 and float(perte) == pytest.approx(entropie + 2.0 * kl, rel=1e-5)
    perte.backward()
    gradients = [p.grad for n, p in modele.named_parameters() if "lora_" in n]
    assert all(g is not None for g in gradients)
    assert all(p.grad is None for n, p in modele.named_parameters() if "lora_" not in n)
    # La base est bien lue sans adaptateur : l'adaptateur reste actif ensuite.
    with modele.disable_adapter():
        base = modele(**_entrees()).logits
    assert not torch.allclose(base, modele(**_entrees()).logits)

    entraineur.log({"loss": float(perte), "learning_rate": 1e-4})
    assert entraineur.logs[-1]["kl"] == pytest.approx(kl)
    assert entraineur.logs[-1]["entropie_croisee"] == pytest.approx(entropie)
    assert lignes == [
        {
            "evenement": "perte",
            "pas": 3,
            "perte": pytest.approx(float(perte)),
            "entropie_croisee": pytest.approx(entropie),
            "kl": pytest.approx(kl),
            "kl_base": 2.0,
        }
    ]
    assert not entraineur._lots_kl  # moyenne remise à zéro après chaque `log`


def test_normalisation_par_num_items_quand_le_modele_les_recoit() -> None:
    """Comme l'entropie croisée du `Trainer` : somme / tokens du pas d'accumulation."""
    modele = _modele_peft()
    with torch.no_grad():
        for nom, p in modele.named_parameters():
            if "lora_B" in nom:
                p.normal_(0, 0.5)
    seul, _ = _entraineur(modele, poids=1.0)
    perte_seule = seul.compute_loss(modele, _entrees())
    accumule, _ = _entraineur(modele, poids=1.0, model_accepts_loss_kwargs=True)
    perte_accumulee = accumule.compute_loss(modele, _entrees(), num_items_in_batch=6)
    # Base factice : entropie croisée en moyenne locale ; seule la KL change de dénominateur.
    _, kl = seul._lots_kl[0]
    assert float(perte_seule) - float(perte_accumulee) == pytest.approx(kl - kl * 3 / 6, rel=1e-4)
    assert accumule._lots_kl[0][1] == pytest.approx(kl)  # journal : moyenne par token


def _deplacer_adaptateur(modele: Any) -> None:
    with torch.no_grad():
        for nom, p in modele.named_parameters():
            if "lora_B" in nom:
                p.normal_(0, 0.5)


def test_kl_par_tranches_egale_le_calcul_non_decoupe_valeur_et_gradient() -> None:
    """Revue 16.6a : tranches de 2 tokens (dernière incomplète) contre logits pleins."""
    modele = _modele_peft()
    _deplacer_adaptateur(modele)
    entrees = _entrees()
    entrees["labels"] = torch.tensor([[IGNORE, 2, IGNORE, 4, 5, 6]])  # 4 tokens de réponse
    causal = kl_base.modele_causal(modele)
    sans = {c: v for c, v in entrees.items() if c != "labels"}

    with torch.no_grad(), modele.disable_adapter():
        logits_base = modele(**sans).logits
        etats_base = causal.base_model(**sans)[0]
    attendu, n_attendu = kl_base.somme_kl(
        torch, modele(**sans).logits, logits_base, entrees["labels"], temperature=2.0
    )
    attendu.backward()
    grad_attendu = {n: p.grad.clone() for n, p in modele.named_parameters() if p.grad is not None}
    modele.zero_grad()

    somme, n = kl_base.somme_kl_par_tranches(
        torch,
        causal.base_model(**sans)[0],
        etats_base,
        entrees["labels"],
        kl_base.projection_logits(torch, causal),
        temperature=2.0,
        taille=3,
    )
    somme.backward()
    assert n == n_attendu == 4 and float(somme) == pytest.approx(float(attendu), rel=1e-5)
    assert float(somme) > 0 and grad_attendu
    for nom, grad in grad_attendu.items():
        assert torch.allclose(dict(modele.named_parameters())[nom].grad, grad, atol=1e-6), nom


def test_kl_par_tranches_sans_token_de_reponse() -> None:
    etats = torch.randn(1, 3, 4)
    labels = torch.full((1, 3), IGNORE)
    somme, n = kl_base.somme_kl_par_tranches(torch, etats, etats, labels, lambda h: h)
    assert n == 0 and float(somme) == 0.0


def test_projection_applique_les_echelles_de_la_config() -> None:
    tete = torch.nn.Linear(2, 3, bias=False)
    config = SimpleNamespace(logit_scale=2.0, logits_scaling=4.0, final_logit_softcapping=None)
    modele = SimpleNamespace(get_output_embeddings=lambda: tete, config=config)
    h = torch.randn(5, 2)
    projete = kl_base.projection_logits(torch, modele)(h)
    assert torch.allclose(projete, tete(h) * 2.0 / 4.0)
    config.final_logit_softcapping = 1.5
    attendu = 1.5 * torch.tanh(tete(h) * 0.5 / 1.5)
    assert torch.allclose(kl_base.projection_logits(torch, modele)(h), attendu)


def test_pas_de_journal_kl_en_evaluation() -> None:
    modele = _modele_peft()
    entraineur, _ = _entraineur(modele)
    modele.eval()
    entraineur.compute_loss(modele, _entrees())
    assert entraineur._lots_kl == []
    modele.train()
    entraineur.compute_loss(modele, _entrees())
    assert len(entraineur._lots_kl) == 1


def test_log_sans_perte_transmis_tel_quel() -> None:
    entraineur, lignes = _entraineur(_modele_peft())
    entraineur.log({"train_runtime": 1.0})
    assert entraineur.logs == [{"train_runtime": 1.0}] and lignes == []


# --- Configuration, arguments, choix de l'entraîneur ------------------------------------------


def test_defauts_et_refus_hors_qlora() -> None:
    hp = _config().hyperparametres
    assert (hp.kl_base, hp.kl_temperature) == (0.0, 1.0)
    assert _config(kl_base=0.1).hyperparametres.kl_base == 0.1
    for methode in ("orpo", "qlora-unsloth", "lora", "dora"):
        with pytest.raises(ValueError, match="kl_base > 0 n'est permis qu'avec methode = qlora"):
            _config(methode, kl_base=0.1)
    for valeur in ({"kl_base": -0.1}, {"kl_temperature": 0}):
        with pytest.raises(ValueError):
            _config(**valeur)


def test_arguments_identiques_avec_et_sans_kl(tmp_path: Path) -> None:
    plan = methodes.plan_methode("qlora")
    sans = methodes.arguments_entrainement(
        _config(), plan, dossier_checkpoints=tmp_path, nb_exemples=4
    )
    explicite = methodes.arguments_entrainement(
        _config(kl_base=0.0, kl_temperature=1.0), plan, dossier_checkpoints=tmp_path, nb_exemples=4
    )
    avec = methodes.arguments_entrainement(
        _config(kl_base=0.1), plan, dossier_checkpoints=tmp_path, nb_exemples=4
    )
    assert "loss_type" not in sans and sans == explicite
    assert avec == sans  # revue 16.6a : la KL garde l'entropie croisée `chunked_nll`


def _creer(pile, plan, **kw):
    return methodes.creer_entraineur(
        pile, plan, modele="m", tokenizer="t", jeu=[], collateur="c",
        arguments={"max_steps": 1}, callbacks=[], **kw,
    )  # fmt: skip


def test_kl_nulle_garde_le_sft_trainer_tel_quel(pile) -> None:
    plan = methodes.plan_methode("qlora")
    assert type(_creer(pile, plan)) is pile.trl.SFTTrainer
    assert type(_creer(pile, plan, kl=0.0, kl_temperature=2.0)) is pile.trl.SFTTrainer
    lignes: list[Any] = []
    avec = _creer(pile, plan, kl=0.2, kl_temperature=2.0, journal=lignes.append)
    assert isinstance(avec, pile.trl.SFTTrainer) and type(avec) is not pile.trl.SFTTrainer
    assert (avec.kl_base, avec.kl_temperature, avec._journal) == (0.2, 2.0, lignes.append)
    with pytest.raises(ConfigurationInvalide, match="methode = qlora"):
        _creer(pile, methodes.plan_methode("orpo"), kl=0.2)


# --- Run : configuration résolue, manifeste ---------------------------------------------------


def test_run_sans_kl_config_resolue_inchangee(projet, pile) -> None:
    projet.ecrire_jeu()
    toml = projet.ecrire_toml()
    assert module_run.executer(toml, racine=projet.racine, pile=pile, sortie=lambda _m: None) == 0
    (dossier,) = (projet.racine / "runs" / "train").iterdir()
    hp = ouvrir_run(dossier.name, racine=projet.racine).manifeste.config["toml"]["hyperparametres"]
    assert "kl_base" not in hp and "kl_temperature" not in hp
    assert type(pile.trainers[-1]) is pile.trl.SFTTrainer


def test_run_avec_kl_consigne_au_manifeste(projet, pile) -> None:
    projet.ecrire_jeu()
    toml = projet.ecrire_toml(
        hyperparametres={"pas_max": 4, "pas_sauvegarde": 2, "kl_base": 0.25, "kl_temperature": 2.0}
    )
    assert module_run.executer(toml, racine=projet.racine, pile=pile, sortie=lambda _m: None) == 0
    (dossier,) = (projet.racine / "runs" / "train").iterdir()
    run = ouvrir_run(dossier.name, racine=projet.racine)
    hp = run.manifeste.config["toml"]["hyperparametres"]
    assert (hp["kl_base"], hp["kl_temperature"]) == (0.25, 2.0)
    entraineur = pile.trainers[-1]
    assert entraineur.kl_base == 0.25
    demarrage = json.loads((dossier / "entrainement.jsonl").read_text(encoding="utf-8"))
    assert demarrage["arguments"]["loss_type"] == "nll"  # Granite factice, pas la KL
    entraineur._journal({"evenement": "perte", "pas": 1, "kl": 0.0})  # journal → metriques
    assert {"evenement": "perte", "pas": 1, "kl": 0.0} in run.lire_jsonl("metriques.jsonl")


def test_run_unsloth_avec_kl_refuse(projet, pile) -> None:
    projet.ecrire_jeu()
    toml = projet.ecrire_toml(
        "m1-unsloth", methode="qlora-unsloth", hyperparametres={"pas_max": 2, "kl_base": 0.1}
    )
    with pytest.raises(ConfigurationInvalide, match="methode = qlora"):
        module_run.executer(toml, racine=projet.racine, pile=pile, sortie=lambda _m: None)


# --- Test réel : SFTTrainer de TRL, deux pas sur CPU ------------------------------------------


@pytest.mark.lent
def test_sft_trainer_reel_journalise_kl_et_entropie(tmp_path: Path) -> None:
    trl = pytest.importorskip("trl")
    datasets = pytest.importorskip("datasets")
    transformers = pytest.importorskip("transformers")
    from slmsp.train.chargement import CollateurMasque  # noqa: PLC0415

    modele = _modele_peft()
    exemples = [
        {"input_ids": [1, 2, 3, 4, 5, 6], "labels": [IGNORE, IGNORE, IGNORE, 4, 5, 6]},
        {"input_ids": [7, 8, 9, 10], "labels": [IGNORE, IGNORE, 9, 10]},
    ]
    arguments = methodes.arguments_entrainement(
        _config(kl_base=0.5, pas_max=2, accumulation=2),
        methodes.plan_methode("qlora"),
        dossier_checkpoints=tmp_path,
        nb_exemples=2,
        cpu=True,
    )
    from tokenizers import Tokenizer, models  # noqa: PLC0415

    vocab = {f"t{i}": i for i in range(32)}
    tokenizer = transformers.PreTrainedTokenizerFast(
        tokenizer_object=Tokenizer(models.WordLevel(vocab, unk_token="t31")),
        unk_token="t31",
        pad_token="t0",
        eos_token="t31",
    )
    lignes: list[dict[str, Any]] = []
    pile = SimpleNamespace(trl=trl, torch=torch, transformers=transformers)
    entraineur = methodes.creer_entraineur(
        pile,
        methodes.plan_methode("qlora"),
        modele=modele,
        tokenizer=tokenizer,
        jeu=datasets.Dataset.from_list(exemples),
        collateur=CollateurMasque(tokenizer.pad_token_id, torch=torch),
        arguments=arguments,
        kl=0.5,
        journal=lignes.append,
    )
    entraineur.train()
    assert [ligne["pas"] for ligne in lignes] == [1, 2]
    premier = lignes[0]
    assert premier["kl"] == pytest.approx(0.0, abs=1e-6)  # adaptateur neuf au pas 1
    assert premier["perte"] == pytest.approx(premier["entropie_croisee"], rel=1e-3)
    assert lignes[1]["kl"] > 0
