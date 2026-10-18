"""Fixtures des Runs d'entraînement (story 10.4) : projet temporaire, jeu factice, pile simulée.

Les contenus de conversation sont des chaînes factices manifestement artificielles (D1) :
aucune donnée d'entraînement n'est rédigée ici.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.core.var import dossier_var

SLUG = "granite-4.0-1b"
JETON = re.compile(r"<\|[a-z_]+\|>|\w+|\s+|[^\w\s]")


class TokenizerFactice:
    """Template de type ChatML ; un token = balise, mot, espaces ou ponctuation."""

    chat_template = "{# template-factice #}"
    eos_token = "<|end|>"

    def __init__(self) -> None:
        self.vocab: dict[str, int] = {"<|end|>": 0}
        self.pad_token: str | None = None
        self.appels_tools: list[Any] = []

    @property
    def pad_token_id(self) -> int:
        return self.vocab[self.pad_token or self.eos_token]

    def apply_chat_template(
        self, messages, *, tools=None, tokenize=False, add_generation_prompt=False, **kwargs
    ):
        self.appels_tools.append(tools)
        noms = ",".join(t["function"]["name"] for t in tools or [])
        sortie = f"<|tools|>{noms}<|end|>\n" if tools else ""
        for m in messages:
            sortie += f"<|{m['role']}|>" + (m.get("content") or "") + "<|end|>\n"
        return sortie + ("<|assistant|>" if add_generation_prompt else "")

    def __call__(self, texte, *, add_special_tokens=False, return_offsets_mapping=False):
        ids, positions = [], []
        for m in JETON.finditer(texte):
            positions.append((m.start(), m.end()))
            ids.append(self.vocab.setdefault(m.group(), len(self.vocab)))
        return {"input_ids": ids, "offset_mapping": positions}


def outils_factices() -> list[dict[str, Any]]:
    """Outils que l'inférence offre à la Tâche RD (`config/outils-mcp.toml`, ordre du fichier)."""
    from slmsp.harness.taches import charger_taches
    from slmsp.mcp.outils import charger_outils

    autorises = set(charger_taches().tache("RD").outils_autorises)
    return [o for o in charger_outils() if o["function"]["name"] in autorises]


def sha_outils_mcp() -> str:
    """SHA-256 de `config/outils-mcp.toml` du projet, comme dans le MANIFEST d'un build."""
    from slmsp.core.canonique import sha256_fichier
    from slmsp.core.config import racine_projet
    from slmsp.mcp.outils import NOM_CONFIG

    return sha256_fichier(racine_projet() / "config" / NOM_CONFIG)


def ligne_factice(numero: int, *, appel_id: str | None = None, mots: int = 1) -> dict[str, Any]:
    reponse = " ".join(f"<réponse-factice-{numero}-{i}>" for i in range(mots))
    return {
        "messages": [
            {"role": "system", "content": "<prompt-factice>"},
            {"role": "user", "content": f"<question-factice-{numero}>"},
            {"role": "assistant", "content": reponse},
        ],
        "tools": outils_factices(),
        "tache": "RD",
        "meta": {"appel_ids": [appel_id or f"appel-{numero}"], "session_id": f"s-{numero}"},
    }


def paire_factice(numero: int, *, appel_id: str | None = None) -> dict[str, Any]:
    """Paire de préférence ORPO factice (contrat `EntetePaire` de la story 9.7)."""
    return {
        "prompt": [
            {"role": "system", "content": "<prompt-factice>"},
            {"role": "user", "content": f"<question-factice-{numero}>"},
        ],
        "chosen": [{"role": "assistant", "content": f"<retenue-factice-{numero}>"}],
        "rejected": [{"role": "assistant", "content": f"<rejetee-factice-{numero}>"}],
        "tools": outils_factices(),
        "tache": "RD",
        "meta": {
            "appel_ids": [appel_id or f"appel-{numero}"],
            "appel_local_id": f"local-{numero}",
            "generateur_rejected": "slm:modele-factice",
        },
    }


@dataclass
class Projet:
    racine: Path
    modeles: Path

    def ecrire_jeu(
        self,
        version: str = "v1",
        lignes: list[dict[str, Any]] | None = None,
        *,
        fichier: str = "train.jsonl",
        manifeste: dict[str, Any] | None = None,
        usages: dict[str, tuple[str, str]] | None = None,
    ) -> Path:
        lignes = lignes if lignes is not None else [ligne_factice(i) for i in range(1, 4)]
        dossier = self.racine / "data" / "train" / version
        dossier.mkdir(parents=True, exist_ok=True)
        brut = "".join(json.dumps(ligne, ensure_ascii=False) + "\n" for ligne in lignes).encode()
        (dossier / fichier).write_bytes(brut)
        contenu = {
            "version": version,
            "type_run": "data-build",
            "run_id": f"20261016-120000-{version}-abcd",
            f"sha256_{Path(fichier).stem}": hashlib.sha256(brut).hexdigest(),
        }
        if any(ligne.get("tools") for ligne in lignes):  # écrit par `data build` (R7)
            contenu["sha_outils_mcp"] = sha_outils_mcp()
        contenu.update(manifeste or {})
        (dossier / "MANIFEST.json").write_text(json.dumps(contenu), encoding="utf-8")
        ids = {a for ligne in lignes for a in ligne["meta"]["appel_ids"]}
        self.ecrire_journal({a: ("generation", "ok") for a in ids} | (usages or {}))
        if fichier == "preferences.jsonl":
            self.ecrire_journal_local(lignes)
        return dossier

    def ecrire_journal_local(self, paires: list[dict[str, Any]]) -> Path:
        """`generations-locales.sqlite` conforme aux réponses rejetées des `paires`."""
        chemin = dossier_var() / "generations-locales.sqlite"
        with sqlite3.connect(chemin) as connexion:
            connexion.execute(
                "CREATE TABLE IF NOT EXISTS appels (appel_id TEXT PRIMARY KEY, usage TEXT, "
                "statut TEXT, generateur TEXT, sha256_reponse TEXT)"
            )
            connexion.executemany(
                "INSERT OR REPLACE INTO appels VALUES (?, ?, ?, ?, ?)",
                [
                    (
                        p["meta"]["appel_local_id"],
                        "generation-locale",
                        "ok",
                        p["meta"]["generateur_rejected"],
                        hashlib.sha256(p["rejected"][-1]["content"].encode()).hexdigest(),
                    )
                    for p in paires
                ],
            )
        connexion.close()
        return chemin

    def ecrire_journal(self, appels: dict[str, tuple[str, str]]) -> Path:
        chemin = dossier_var() / "appels-mistral.sqlite"
        with sqlite3.connect(chemin) as connexion:
            connexion.execute(
                "CREATE TABLE IF NOT EXISTS appels (appel_id TEXT PRIMARY KEY, usage TEXT, "
                "statut TEXT)"
            )
            connexion.executemany(
                "INSERT OR REPLACE INTO appels VALUES (?, ?, ?)",
                [(a, u, s) for a, (u, s) in appels.items()],
            )
        connexion.close()
        return chemin

    def ecrire_toml(self, nom: str = "m1-qlora", **valeurs: Any) -> Path:
        base: dict[str, Any] = {
            "campagne": "campagne-test",
            "modele": SLUG,
            "methode": "qlora",
            "jeu_version": "v1",
            "graine": 7,
            "longueur_max": 256,
        }
        base.update(valeurs)
        hp = base.pop("hyperparametres", {"pas_max": 4, "pas_sauvegarde": 2})
        lignes = [f"{cle} = {json.dumps(valeur)}" for cle, valeur in base.items()]
        lignes.append("[hyperparametres]")
        lignes += [f"{cle} = {json.dumps(valeur)}" for cle, valeur in hp.items()]
        chemin = self.racine / "config-runs" / f"{nom}.toml"
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
        return chemin


@pytest.fixture
def projet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Projet:
    racine = tmp_path / "racine"
    modeles = tmp_path / "models"
    poids = modeles / SLUG / "hf"
    poids.mkdir(parents=True)
    (poids / "config.json").write_text(
        json.dumps({"model_type": "granite", "vocab_size": 100, "logits_scaling": 8.0}),
        encoding="utf-8",
    )
    racine.mkdir()
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(modeles))
    return Projet(racine, modeles)


# --- Modèle multimodal simulé (story B2) ---------------------------------------------------


class Linear:
    """Nom de classe des couches linéaires que relève `environnement.cibles_lora`."""


class Embedding:
    pass


class Parametre:
    def __init__(self, nombre: int, *, entrainable: bool = False) -> None:
        self.nombre, self.requires_grad = nombre, entrainable

    def numel(self) -> int:
        return self.nombre


class ModeleMultimodalFactice:
    """Forme de `Qwen3_5ForConditionalGeneration` : `model.visual.*`, `model.language_model.*`
    et `lm_head`. `poser_lora` ajoute un paramètre LoRA entraînable par module ciblé (regex
    `target_modules` en `fullmatch`, comme PEFT ; `all-linear` : toutes les linéaires sauf
    `lm_head`)."""

    MODULES: dict[str, type] = {
        "model.visual.blocks.0.attn.qkv": Linear,
        "model.visual.merger.linear_fc1": Linear,
        "model.language_model.embed_tokens": Embedding,
        "model.language_model.layers.0.linear_attn.in_proj_qkv": Linear,
        "model.language_model.layers.0.linear_attn.out_proj": Linear,
        "model.language_model.layers.1.self_attn.q_proj": Linear,
        "model.language_model.layers.1.mlp.down_proj": Linear,
        "lm_head": Linear,
    }

    def __init__(self, **_kw: Any) -> None:
        self.config = SimpleNamespace(use_cache=True)
        self.parametres = {f"{nom}.weight": Parametre(10) for nom in self.MODULES}
        self.cibles: str | None = None

    def named_modules(self):
        yield "", self
        for nom, classe in self.MODULES.items():
            yield nom, classe()

    def named_parameters(self):
        return iter(list(self.parametres.items()))

    def enable_input_require_grads(self) -> None:
        pass

    def poser_lora(self, config: Any) -> None:
        cible = config.get("target_modules") if isinstance(config, dict) else None
        cible = cible or r".*language_model.*"
        for nom, classe in self.MODULES.items():
            if classe is not Linear:
                continue
            if cible == "all-linear" and nom == "lm_head":
                continue
            if cible == "all-linear" or re.fullmatch(cible, nom):
                self.parametres[f"{nom}.lora_A.weight"] = Parametre(2, entrainable=True)
        self.cibles = cible

    def save_pretrained(self, dossier: str) -> None:
        Path(dossier).mkdir(parents=True)
        for nom in ("adapter_config.json", "adapter_model.safetensors"):
            (Path(dossier) / nom).write_text("{}", encoding="utf-8")


CONFIG_QWEN35_FACTICE = {
    "model_type": "qwen3_5",
    "architectures": ["Qwen3_5ForConditionalGeneration"],
    "text_config": {
        "layer_types": ["linear_attention", "linear_attention", "full_attention"],
        "vocab_size": 100,
    },
    "vision_config": {"depth": 1},
}
"""Forme réelle de `config.json` de Qwen3.5 : `layer_types` sous `text_config`."""


# --- Pile simulée --------------------------------------------------------------------------


class OOM(Exception):
    pass


@dataclass
class PileFactice:
    """torch, transformers, peft, trl et datasets simulés ; `ordre` trace les appels."""

    ordre: list[str] = field(default_factory=list)
    lora: list[dict[str, Any]] = field(default_factory=list)
    appels_base: list[str] = field(default_factory=list)
    """`kbit` (prepare_model_for_kbit_training) et `grads` (enable_input_require_grads)."""
    trainers: list[Any] = field(default_factory=list)
    interrompre_apres: int | None = None
    """Le faux entraîneur lève `KeyboardInterrupt` après ce nombre de pas."""
    bitsandbytes: Any = field(default_factory=lambda: SimpleNamespace(nom="bnb-factice"))

    def __post_init__(self) -> None:
        pile = self
        self.torch = SimpleNamespace(
            bfloat16="bf16",
            float32="fp32",
            long="long",
            tensor=lambda valeur, dtype=None: valeur,
            cuda=SimpleNamespace(OutOfMemoryError=OOM, is_available=lambda: False),
        )

        class Modele:
            def __init__(self) -> None:
                self.config = SimpleNamespace(use_cache=True)

            def enable_input_require_grads(self) -> None:
                pile.appels_base.append("grads")

            def save_pretrained(self, dossier: str) -> None:
                Path(dossier).mkdir(parents=True)
                for nom in ("adapter_config.json", "adapter_model.safetensors"):
                    (Path(dossier) / nom).write_text("{}", encoding="utf-8")

        class Auto:
            @staticmethod
            def from_pretrained(dossier: str, **arguments: Any) -> Any:
                pile.ordre.append("modele")
                pile.arguments_modele = arguments
                return Modele()

        class AutoMultimodal:
            @staticmethod
            def from_pretrained(dossier: str, **arguments: Any) -> Any:
                pile.ordre.append("modele-multimodal")
                pile.arguments_modele = arguments
                return ModeleMultimodalFactice()

        class Tok:
            @staticmethod
            def from_pretrained(dossier: str, **arguments: Any) -> Any:
                return TokenizerFactice()

        class Callback:
            pass

        self.transformers = SimpleNamespace(
            AutoModelForCausalLM=Auto,
            AutoModelForImageTextToText=AutoMultimodal,
            AutoTokenizer=Tok,
            TrainerCallback=Callback,
            BitsAndBytesConfig=lambda **kw: ("bnb", kw),
            set_seed=lambda graine: pile.ordre.append(f"graine:{graine}"),
        )

        def get_peft_model(modele: Any, config: Any) -> Any:
            pile.ordre.append("adaptateur")
            if isinstance(modele, ModeleMultimodalFactice):
                modele.poser_lora(config)
            return modele

        def adaptateur_sft(modele: Any, chemin: str, **kw: Any) -> Any:
            pile.ordre.append(f"sft:{Path(chemin).parent.name}")
            if isinstance(modele, ModeleMultimodalFactice):
                modele.poser_lora(None)  # adaptateur SFT : `language_model` seul
            return modele

        def lora_config(**kw: Any) -> dict[str, Any]:
            pile.lora.append(kw)
            return kw

        self.peft = SimpleNamespace(
            LoraConfig=lora_config,
            get_peft_model=get_peft_model,
            prepare_model_for_kbit_training=lambda modele, **kw: (
                pile.appels_base.append("kbit") or modele
            ),
            PeftModel=SimpleNamespace(from_pretrained=adaptateur_sft),
        )

        class Trainer:
            def __init__(self, *, model, args, train_dataset, data_collator=None, **kw) -> None:
                self.model, self.args, self.jeu = model, args, train_dataset
                self.collateur, self.callbacks = data_collator, kw["callbacks"]
                pile.trainers.append(self)

            def train(self, resume_from_checkpoint: str | None = None) -> None:
                self.reprise = resume_from_checkpoint
                etat = SimpleNamespace(num_input_tokens_seen=0)
                for cb in self.callbacks:
                    cb.on_train_begin(self.args, etat, None)
                depart = (
                    int(resume_from_checkpoint.rsplit("-", 1)[1]) if resume_from_checkpoint else 0
                )
                for pas in range(depart + 1, self.args.max_steps + 1):
                    if pile.interrompre_apres is not None and pas > pile.interrompre_apres:
                        raise KeyboardInterrupt
                    etat.num_input_tokens_seen += 10
                    for cb in self.callbacks:
                        cb.on_step_end(self.args, etat, None)
                    if pas % self.args.save_steps == 0:
                        ckpt = Path(self.args.output_dir) / f"checkpoint-{pas}"
                        ckpt.mkdir(parents=True)
                        for nom in ("optimizer.pt", "scheduler.pt", "trainer_state.json"):
                            (ckpt / nom).write_text("{}", encoding="utf-8")
                for cb in self.callbacks:
                    cb.on_train_end(self.args, etat, None)

        self.trl = SimpleNamespace(SFTConfig=lambda **kw: SimpleNamespace(**kw), SFTTrainer=Trainer)
        self.orpo = SimpleNamespace(
            ORPOConfig=lambda **kw: SimpleNamespace(**kw), ORPOTrainer=Trainer
        )
        self.datasets = SimpleNamespace(Dataset=SimpleNamespace(from_list=list))


@pytest.fixture
def pile() -> PileFactice:
    return PileFactice()


@pytest.fixture
def factices() -> SimpleNamespace:
    """Accès aux fabriques factices (mode d'import `importlib` : pas d'import de conftest)."""
    return SimpleNamespace(
        Tokenizer=TokenizerFactice,
        ligne=ligne_factice,
        paire=paire_factice,
        ModeleMultimodal=ModeleMultimodalFactice,
        config_qwen35=CONFIG_QWEN35_FACTICE,
    )
