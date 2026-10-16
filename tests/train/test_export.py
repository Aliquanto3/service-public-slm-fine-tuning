"""Export GGUF (story 10.6) : fusion, conversion F16, Q4_K_M, contrôles et CLI.

Pile d'entraînement, convertisseur et `llama-quantize` sont des doubles : aucun modèle réel,
aucun processus llama.cpp. Les GGUF écrits par les doubles n'ont qu'un en-tête de
métadonnées (format GGUF v3), avec un template factice.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.cli import export as cli_export
from slmsp.cli import main
from slmsp.core.artefacts import nouveau_run, ouvrir_run
from slmsp.core.erreurs import CodeSortie, ConfigurationInvalide, RessourceOccupee
from slmsp.core.var import verrou_gpu
from slmsp.evaluation import modele_ref, sonde_outils
from slmsp.inference import serveur
from slmsp.train import environnement
from slmsp.train import export as module_export

SLUG = "granite-4.0-1b"
TEMPLATE = "{# template-factice-export #}"
SHA_TEMPLATE = hashlib.sha256(TEMPLATE.encode()).hexdigest()


@pytest.fixture(autouse=True)
def _pythonutf8(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTHONUTF8", "1")  # `exporter` ne pose la variable que si absente


# --- GGUF minimal ------------------------------------------------------------------------


def _chaine(texte: str) -> bytes:
    donnees = texte.encode("utf-8")
    return struct.pack("<Q", len(donnees)) + donnees


def ecrire_gguf(chemin: Path, metadonnees: dict[str, Any]) -> Path:
    """En-tête GGUF v3 sans tenseur : chaînes (type 8) et entiers non signés (type 4)."""
    corps = b""
    for cle, valeur in metadonnees.items():
        corps += _chaine(cle)
        if isinstance(valeur, str):
            corps += struct.pack("<I", 8) + _chaine(valeur)
        else:
            corps += struct.pack("<I", 4) + struct.pack("<I", valeur)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_bytes(b"GGUF" + struct.pack("<IQQ", 3, 0, len(metadonnees)) + corps)
    return chemin


def meta(template: str = TEMPLATE, **autres: Any) -> dict[str, Any]:
    return {
        "general.architecture": "granite",
        "granite.block_count": 40,
        "tokenizer.ggml.pre": "pre-factice",
        "tokenizer.ggml.bos_token_id": 1,
        "tokenizer.ggml.eos_token_id": 2,
        "tokenizer.chat_template": template,
        **autres,
    }


# --- Pile simulée --------------------------------------------------------------------------


class Tenseur:
    def __init__(self, valeur: float, flottant: bool = True) -> None:
        self.valeur, self.flottant = valeur, flottant

    def is_floating_point(self) -> bool:
        return self.flottant

    def numel(self) -> int:
        return 1

    def abs(self) -> Tenseur:
        return Tenseur(abs(self.valeur))

    def max(self) -> float:
        return self.valeur

    def __float__(self) -> float:
        return self.valeur


class TorchFactice:
    float32, float16 = "float32", "float16"

    @staticmethod
    def isfinite(tenseur: Tenseur) -> SimpleNamespace:
        fini = tenseur.valeur == tenseur.valeur and abs(tenseur.valeur) != float("inf")
        return SimpleNamespace(all=lambda: fini)


class ModeleFactice:
    def __init__(self, pile: PileExport, poids: dict[str, Tenseur]) -> None:
        self.pile, self.poids, self.dtype = pile, poids, None

    def state_dict(self) -> dict[str, Tenseur]:
        return self.poids

    def to(self, dtype: str) -> ModeleFactice:
        self.dtype = dtype
        self.pile.ordre.append(f"to:{dtype}")
        return self

    def save_pretrained(self, dossier: str, *, safe_serialization: bool) -> None:
        assert safe_serialization and self.dtype == "float16"
        Path(dossier).mkdir(parents=True, exist_ok=True)
        (Path(dossier) / "model.safetensors").write_bytes(b"<poids-factices>")
        self.pile.ordre.append("save")


class PileExport:
    def __init__(self, poids: dict[str, Tenseur] | None = None) -> None:
        self.ordre: list[str] = []
        self.verrou_tenu: bool | None = None
        self.charge: dict[str, Any] = {}
        poids = poids if poids is not None else {"w": Tenseur(0.5), "ids": Tenseur(7, False)}
        pile = self

        def charger_modele(dossier: str, **options: Any) -> ModeleFactice:
            pile.charge = {"dossier": dossier, **options}
            pile.ordre.append(f"base:{options['torch_dtype']}")
            try:
                with verrou_gpu():
                    pile.verrou_tenu = False
            except RessourceOccupee:
                pile.verrou_tenu = True
            return ModeleFactice(pile, poids)

        def appliquer(modele: ModeleFactice, dossier: str) -> SimpleNamespace:
            pile.ordre.append(f"adaptateur:{Path(dossier).parent.name}")
            return SimpleNamespace(merge_and_unload=lambda: pile.ordre.append("merge") or modele)

        def tokenizer(dossier: str, **_options: Any) -> SimpleNamespace:
            def enregistrer(sortie: str) -> None:
                (Path(sortie) / "tokenizer_config.json").write_text("{}", encoding="utf-8")
                pile.ordre.append("tokenizer")

            return SimpleNamespace(chat_template=TEMPLATE, save_pretrained=enregistrer)

        self.torch = TorchFactice()
        self.transformers = SimpleNamespace(
            AutoModelForCausalLM=SimpleNamespace(from_pretrained=charger_modele),
            AutoTokenizer=SimpleNamespace(from_pretrained=tokenizer),
        )
        self.peft = SimpleNamespace(PeftModel=SimpleNamespace(from_pretrained=appliquer))
        self.trl = self.datasets = None


class Outils:
    """Doubles de `convertir_hf_vers_gguf` et `quantifier` : écrivent un GGUF minimal."""

    def __init__(self, template: str = TEMPLATE) -> None:
        self.template = template
        self.appels: list[tuple[str, dict[str, Any]]] = []

    def convertir(self, dossier_hf: Path, sortie: Path, **options: Any) -> Path:
        assert (Path(dossier_hf) / "model.safetensors").is_file()
        self.appels.append(("convertir", options))
        return ecrire_gguf(Path(sortie), meta(self.template))

    def quantifier(self, entree: Path, sortie: Path, type_q: str, **options: Any) -> Path:
        assert Path(entree).is_file()
        self.appels.append(("quantifier", {"type": type_q, **options}))
        return ecrire_gguf(Path(sortie), meta(self.template))


# --- Fixtures ------------------------------------------------------------------------------


def run_train(projet: Any, *, statut: str = "complet", adaptateur: bool = True, **cfg: Any) -> str:
    config = {"toml": {"modele": SLUG, "methode": "qlora", **cfg}}
    run = nouveau_run(
        "train", "m1-qlora", config, racine=projet.racine, chat_template_sha256=SHA_TEMPLATE
    )
    if adaptateur:
        dossier = run.dossier / "adaptateur"
        dossier.mkdir()
        (dossier / "adapter_config.json").write_text(
            json.dumps({"peft_type": "LORA", "r": 16, "target_modules": ["q_proj"]}),
            encoding="utf-8",
        )
        (dossier / "adapter_model.safetensors").write_bytes(b"<adaptateur-factice>")
    run.terminer(statut)
    return run.run_id


def gguf_officiel(projet: Any, **metadonnees: Any) -> Path:
    fichier = serveur.charger_config_modele(SLUG).gguf_pour("q4_k_m")
    assert fichier is not None
    chemin = projet.modeles / SLUG / "gguf" / PurePosixPath(fichier.fichier).name
    return ecrire_gguf(chemin, meta(**metadonnees))


def exporter(projet: Any, source: Any, outils: Outils, pile: PileExport, **options: Any) -> Any:
    return module_export.exporter(
        source,
        racine=projet.racine,
        pile=pile,
        convertir=outils.convertir,
        quantifier=outils.quantifier,
        sortie=lambda _m: None,
        **options,
    )


# --- Chaîne d'export -----------------------------------------------------------------------


def test_export_nominal(projet) -> None:
    train_id = run_train(projet)
    pile, outils = PileExport(), Outils()
    run = exporter(
        projet, module_export.source_depuis_run(train_id, racine=projet.racine), outils, pile
    )
    assert run.statut_courant() == "complet"
    assert run.dossier.parent == projet.racine / "runs" / "export"
    for nom in ("modele-f16.gguf", "modele-q4_k_m.gguf", "hf-f16/model.safetensors"):
        assert (run.dossier / nom).is_file()
    # Fusion en fp32 sur CPU, adaptateur fusionné, écriture F16, sous gpu.lock (CA4).
    assert pile.ordre == [
        "base:float32",
        "adaptateur:" + train_id,
        "merge",
        "to:float16",
        "save",
        "tokenizer",
    ]
    assert pile.charge["low_cpu_mem_usage"] and pile.charge["local_files_only"]
    assert pile.verrou_tenu is True
    # Conversion `f16` explicite, puis Q4_K_M sans imatrix en CPU (AD-6, outils du tag).
    assert outils.appels[0][1]["type_sortie"] == "f16"
    assert outils.appels[1][1]["type"] == "Q4_K_M" and outils.appels[1][1]["variante"] == "cpu"
    manifeste = run.manifeste
    assert manifeste.modele_ref == f"base:{SLUG}" and manifeste.parents == [train_id]
    assert manifeste.chat_template_sha256 == SHA_TEMPLATE
    assert manifeste.llamacpp_tag == serveur.charger_config_llamacpp().tag
    export = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))
    assert export["precisions"] == {"f16": "f16", "q4_k_m": "q4_k_m"}
    assert export["fusion"]["max_abs"] == 0.5 and export["fusion"]["tenseurs"] == 1
    # CA3 : `ft:<run_id>` résolu pour f16 et q4_k_m.
    for quantification in modele_ref.QUANTIFICATIONS:
        resolu = modele_ref.resoudre(f"ft:{run.run_id}", quantification, racine=projet.racine)
        assert resolu.gguf == run.dossier / f"modele-{quantification}.gguf"
        assert resolu.precision == quantification


def test_export_temoin_sans_adaptateur(projet) -> None:
    pile = PileExport()
    run = exporter(projet, module_export.source_temoin(SLUG), Outils(), pile)
    assert run.statut_courant() == "complet" and run.manifeste.parents == []
    assert "merge" not in pile.ordre and run.run_id.split("-", 2)[2].startswith("base-")
    assert run.manifeste.config["source"] == "temoin"


def test_espace_disque_verifie_au_dela_de_1_gio(projet, monkeypatch) -> None:
    (projet.modeles / SLUG / "hf" / "model.safetensors").write_bytes(b"x" * 100)
    demandes: list[int] = []
    monkeypatch.setattr(module_export, "SEUIL_VERIFICATION_ESPACE", 10)
    monkeypatch.setattr(
        module_export, "verifier_espace", lambda _c, octets: demandes.append(octets)
    )
    exporter(projet, module_export.source_temoin(SLUG), Outils(), PileExport())
    assert demandes == [240]


def test_gpu_occupe(projet) -> None:
    with verrou_gpu(commande="autre"), pytest.raises(RessourceOccupee):
        exporter(projet, module_export.source_temoin(SLUG), Outils(), PileExport())
    assert not (projet.racine / "runs" / "export").exists()


@pytest.mark.parametrize("valeur", [float("nan"), float("inf"), 70000.0])
def test_plage_f16_controlee(projet, valeur: float) -> None:
    pile = PileExport({"w": Tenseur(valeur)})
    with pytest.raises(ConfigurationInvalide, match="fusion"):
        exporter(projet, module_export.source_temoin(SLUG), Outils(), pile)
    (run,) = (projet.racine / "runs" / "export").iterdir()
    assert ouvrir_run(run.name, racine=projet.racine).statut_courant() == "partiel-erreur"


def test_echec_de_conversion_termine_le_run(projet) -> None:
    def echouer(*_a: Any, **_k: Any) -> Path:
        raise serveur.ErreurInference("convert_hf_to_gguf.py : échec (code 1)")

    with pytest.raises(serveur.ErreurInference):
        module_export.exporter(
            module_export.source_temoin(SLUG),
            racine=projet.racine,
            pile=PileExport(),
            convertir=echouer,
            sortie=lambda _m: None,
        )
    (run,) = (projet.racine / "runs" / "export").iterdir()
    assert ouvrir_run(run.name, racine=projet.racine).statut_courant() == "partiel-erreur"


# --- Source : run d'entraînement ---------------------------------------------------------


def test_source_refuse_un_run_incomplet(projet) -> None:
    with pytest.raises(ConfigurationInvalide, match="partiel-erreur"):
        module_export.source_depuis_run(
            run_train(projet, statut="partiel-erreur"), racine=projet.racine
        )


def test_source_refuse_un_adaptateur_absent(projet) -> None:
    with pytest.raises(ConfigurationInvalide, match="adaptateur incomplet"):
        module_export.source_depuis_run(run_train(projet, adaptateur=False), racine=projet.racine)


@pytest.mark.parametrize(
    ("config", "motif"),
    [
        ({"init_lora_weights": "pissa"}, "PiSSA"),
        ({"target_modules": ["q_proj", "embed_tokens"]}, "embeddings"),
        ({"modules_to_save": ["lm_head"]}, "embeddings"),
    ],
)
def test_adaptateur_refuse(projet, config: dict[str, Any], motif: str) -> None:
    train_id = run_train(projet)
    fichier = projet.racine / "runs" / "train" / train_id / "adaptateur" / "adapter_config.json"
    fichier.write_text(json.dumps({"peft_type": "LORA", **config}), encoding="utf-8")
    source = module_export.source_depuis_run(train_id, racine=projet.racine)
    with pytest.raises(ConfigurationInvalide, match=motif):
        exporter(projet, source, Outils(), PileExport())
    assert not (projet.racine / "runs" / "export").exists()


# --- Contrôles de format (cli.export) ---------------------------------------------------


def test_controle_template_et_metadonnees_conformes(projet) -> None:
    gguf_officiel(projet)
    source = module_export.source_depuis_run(run_train(projet), racine=projet.racine)
    run = exporter(
        projet, source, Outils(), PileExport(), controles=cli_export.controler_format(SLUG)
    )
    assert run.statut_courant() == "complet"
    controles = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))["controles"]
    assert controles["templates"] == {"f16": SHA_TEMPLATE, "q4_k_m": SHA_TEMPLATE}
    assert controles["bloquants"] == [] and controles["alertes"] == []
    assert controles["metadonnees"]["ecarts"] == {}


def test_template_embarque_different_bloquant(projet) -> None:
    source = module_export.source_depuis_run(run_train(projet), racine=projet.racine)
    outils = Outils(template="{# autre-template-factice #}")
    run = exporter(
        projet, source, outils, PileExport(), controles=cli_export.controler_format(SLUG)
    )
    assert run.statut_courant() == "partiel-erreur"
    with pytest.raises(ConfigurationInvalide, match="pas complet"):
        modele_ref.resoudre(f"ft:{run.run_id}", "q4_k_m", racine=projet.racine)


def test_metadonnees_differentes_en_alerte(projet) -> None:
    gguf_officiel(projet, **{"tokenizer.ggml.pre": "autre-pre"})
    run = exporter(
        projet,
        module_export.source_temoin(SLUG),
        Outils(),
        PileExport(),
        controles=cli_export.controler_format(SLUG),
    )
    assert run.statut_courant() == "complet"
    controles = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))["controles"]
    assert list(controles["metadonnees"]["ecarts"]) == ["tokenizer.ggml.pre"]
    assert "GGUF officiel" in controles["alertes"][0]


# --- CLI -------------------------------------------------------------------------------


@pytest.fixture
def cli(projet, monkeypatch) -> SimpleNamespace:
    outils, pile = Outils(), PileExport()
    monkeypatch.setattr(serveur, "convertir_hf_vers_gguf", outils.convertir)
    monkeypatch.setattr(serveur, "quantifier", outils.quantifier)
    monkeypatch.setattr(environnement, "charger_pile", lambda: pile)
    gguf_officiel(projet)
    return SimpleNamespace(outils=outils, pile=pile)


def _sonde_factice(valide: bool, appels: list[tuple[str, str]]) -> Any:
    def sonder(ref: str, *, variante: str, racine: Path) -> SimpleNamespace:
        appels.append((ref, variante))
        motif = None if valide else "aucun protocole valide"
        return SimpleNamespace(
            run=SimpleNamespace(run_id="20261016-120000-ft-sonde-abcd"),
            valide=valide,
            protocole_recommande="natif",
            statut="complet",
            motif=motif,
        )

    return sonder


@pytest.mark.parametrize(
    ("valide", "code"), [(True, CodeSortie.SUCCES), (False, CodeSortie.ERREUR)]
)
def test_cli_export_puis_sonde_sur_q4(projet, cli, monkeypatch, capsys, valide, code) -> None:
    appels: list[tuple[str, str]] = []
    monkeypatch.setattr(sonde_outils, "sonder", _sonde_factice(valide, appels))
    train_id = run_train(projet)
    commande = ["export", "--depuis", train_id, "--racine", str(projet.racine)]
    assert main(commande) == code
    (dossier,) = (projet.racine / "runs" / "export").iterdir()
    assert appels == [(f"ft:{dossier.name}", "cpu")]
    bilan = json.loads((dossier / "sonde-outils.json").read_text(encoding="utf-8"))
    assert bilan["items"] == ["RD-001", "RD-002"] and bilan["quantification"] == "q4_k_m"
    assert bilan["valide"] is valide
    sortie = capsys.readouterr().out
    assert f"ft:{dossier.name} f16" in sortie and f"ft:{dossier.name} q4_k_m" in sortie


def test_cli_temoin_sans_sonde(projet, cli, monkeypatch) -> None:
    monkeypatch.setattr(sonde_outils, "sonder", lambda *a, **k: pytest.fail("sonde lancée"))
    commande = ["export", "--base", SLUG, "--sans-sonde", "--racine", str(projet.racine)]
    assert main(commande) == CodeSortie.SUCCES


def test_cli_template_different(projet, cli, monkeypatch) -> None:
    cli.outils.template = "{# autre-template-factice #}"
    monkeypatch.setattr(sonde_outils, "sonder", lambda *a, **k: pytest.fail("sonde lancée"))
    train_id = run_train(projet)
    assert (
        main(["export", "--depuis", train_id, "--racine", str(projet.racine)]) == CodeSortie.ERREUR
    )


@pytest.mark.parametrize("arguments", [[], ["--depuis", "x", "--base", SLUG]])
def test_cli_usage(arguments: list[str]) -> None:
    assert main(["export", *arguments]) == CodeSortie.USAGE
