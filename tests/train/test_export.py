"""Export GGUF (story 10.6) : fusion, conversion F16, Q4_K_M, contrôles et CLI.

Pile d'entraînement, convertisseur et `llama-quantize` sont des doubles : aucun modèle réel,
aucun processus llama.cpp. Les GGUF écrits par les doubles n'ont qu'un en-tête de
métadonnées (format GGUF v3), avec un template factice.
"""

from __future__ import annotations

import functools
import hashlib
import json
import os
import struct
import sys
from collections.abc import Sequence
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.cli import export as cli_export
from slmsp.cli import main
from slmsp.core.artefacts import nouveau_run, ouvrir_run
from slmsp.core.erreurs import (
    CodeSortie,
    ConfigurationInvalide,
    LectureInterdite,
    RessourceOccupee,
)
from slmsp.core.var import verrou_gpu
from slmsp.evaluation import modele_ref, sonde_outils
from slmsp.inference import serveur
from slmsp.train import environnement
from slmsp.train import export as module_export

SLUG = "granite-4.0-1b"
SLUG_MM = "qwen3.5-0.8b"
MODULE_LORA_LANGAGE = "base_model.model.model.language_model.layers.0.self_attn.q_proj"
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
    def __init__(
        self,
        poids: dict[str, Tenseur] | None = None,
        modules_lora: Sequence[str] = (MODULE_LORA_LANGAGE,),
    ) -> None:
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
            return SimpleNamespace(
                merge_and_unload=lambda: pile.ordre.append("merge") or modele,
                named_modules=lambda: [(f"{m}.lora_A.default", None) for m in modules_lora],
            )

        def charger_conditionnelle(dossier: str, **options: Any) -> ModeleFactice:
            pile.ordre.append("classe:conditionnelle")
            return charger_modele(dossier, **options)

        def tokenizer(dossier: str, **_options: Any) -> SimpleNamespace:
            def enregistrer(sortie: str) -> None:
                (Path(sortie) / "tokenizer_config.json").write_text("{}", encoding="utf-8")
                pile.ordre.append("tokenizer")

            return SimpleNamespace(chat_template=TEMPLATE, save_pretrained=enregistrer)

        self.torch = TorchFactice()
        self.transformers = SimpleNamespace(
            AutoModelForCausalLM=SimpleNamespace(from_pretrained=charger_modele),
            AutoModelForImageTextToText=SimpleNamespace(from_pretrained=charger_conditionnelle),
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
    options.setdefault("controles", cli_export.controler_format(SLUG))
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
            controles=cli_export.controler_format(SLUG),
            sortie=lambda _m: None,
        )
    (run,) = (projet.racine / "runs" / "export").iterdir()
    assert ouvrir_run(run.name, racine=projet.racine).statut_courant() == "partiel-erreur"


def test_controles_obligatoires(projet) -> None:
    """CA2 : sans contrôle du template embarqué, aucun export ne peut finir `complet`."""
    with pytest.raises(TypeError, match="controles"):
        module_export.exporter(  # type: ignore[call-arg]
            module_export.source_temoin(SLUG), racine=projet.racine, pile=PileExport()
        )
    assert not (projet.racine / "runs" / "export").exists()


def test_delai_des_outils_proportionne_aux_poids(projet) -> None:
    outils = Outils()
    exporter(projet, module_export.source_temoin(SLUG), outils, PileExport())
    attendu = [module_export.DELAI_MIN_OUTIL] * 2
    assert [options["delai"] for _, options in outils.appels] == attendu
    # Base de 8 Gio : au-delà du plancher, proportionnel (débit minimal de 2 Mio/s).
    octets = 8 * 1024**3
    assert module_export.delai_outils(octets) == octets / module_export.DEBIT_MIN_OUTIL > 3600
    assert module_export.delai_outils(0) == module_export.DELAI_MIN_OUTIL
    outils = Outils()
    run = exporter(projet, module_export.source_temoin(SLUG), outils, PileExport(), delai=12.5)
    assert [options["delai"] for _, options in outils.appels] == [12.5, 12.5]
    assert run.manifeste.config["delai_outils_s"] == 12.5
    with pytest.raises(ConfigurationInvalide, match="délai"):
        exporter(projet, module_export.source_temoin(SLUG), Outils(), PileExport(), delai=0)


def test_delai_depasse_libere_le_verrou(projet) -> None:
    """Un outil bloqué est tué à l'échéance : run `partiel-erreur`, `gpu.lock` libéré."""

    def bloque(*_a: Any, delai: float, **_k: Any) -> Path:
        raise serveur.ErreurInference(f"llama-quantize : délai de {delai:g} s dépassé")

    outils = Outils()
    with pytest.raises(serveur.ErreurInference, match="délai de 3 s"):
        module_export.exporter(
            module_export.source_temoin(SLUG),
            racine=projet.racine,
            pile=PileExport(),
            convertir=outils.convertir,
            quantifier=bloque,
            controles=cli_export.controler_format(SLUG),
            delai=3,
            sortie=lambda _m: None,
        )
    (run,) = (projet.racine / "runs" / "export").iterdir()
    assert ouvrir_run(run.name, racine=projet.racine).statut_courant() == "partiel-erreur"
    with verrou_gpu(commande="suivant"):
        pass


def test_lanceurs_reels_recoivent_env_sous_processus_et_delai(projet, monkeypatch) -> None:
    """CA4 : par les vrais lanceurs de `serveur` (llama.cpp factice), chaque sous-processus
    reçoit `env_sous_processus()` (sans secret, `PYTHONUTF8=1`) et le délai de l'export."""
    reelle = serveur.charger_config_llamacpp()
    vendor = projet.racine / "vendor"
    tag = vendor / "llama.cpp" / reelle.tag
    binaires = {}
    for relatif in ("bin-cpu/llama-quantize.exe", "src/convert_hf_to_gguf.py"):
        (tag / relatif).parent.mkdir(parents=True, exist_ok=True)
        (tag / relatif).write_bytes(b"factice")
        binaires[relatif] = hashlib.sha256(b"factice").hexdigest()
    (tag / "src" / "gguf-py").mkdir()
    monkeypatch.setenv("SLMSP_VENDOR_DIR", str(vendor))
    monkeypatch.setenv("FAUX_API_KEY", "secret-factice")
    monkeypatch.delenv("PYTHONUTF8", raising=False)
    monkeypatch.setattr(serveur, "_empreintes_verifiees", set())
    config = reelle.model_copy(update={"binaires": binaires})
    lancements: list[tuple[list[str], dict[str, Any]]] = []

    def executer(arguments: list[str], **options: Any) -> tuple[int, str]:
        lancements.append((list(arguments), options))
        sortie = arguments[arguments.index("--outfile") + 1] if "--outfile" in arguments else None
        ecrire_gguf(Path(sortie or arguments[2]), meta())
        return 0, ""

    monkeypatch.setattr(serveur.processus, "executer", executer)
    run = module_export.exporter(
        module_export.source_temoin(SLUG),
        racine=projet.racine,
        pile=PileExport(),
        convertir=functools.partial(serveur.convertir_hf_vers_gguf, config=config),
        quantifier=functools.partial(serveur.quantifier, config=config),
        controles=cli_export.controler_format(SLUG),
        delai=77,
        sortie=lambda _m: None,
    )
    assert run.statut_courant() == "complet"
    assert len(lancements) == 2
    for _arguments, options in lancements:
        assert options["delai"] == 77
        assert "FAUX_API_KEY" not in options["env"] and options["env"]["PYTHONUTF8"] == "1"
    (conversion, _), (quantification, _) = lancements
    assert conversion[conversion.index("--outtype") + 1] == "f16"
    assert quantification[-1] == "Q4_K_M" and "bin-cpu" in quantification[0]


# --- Source : run d'entraînement ---------------------------------------------------------


def test_source_refuse_un_run_incomplet(projet) -> None:
    with pytest.raises(ConfigurationInvalide, match="partiel-erreur"):
        module_export.source_depuis_run(
            run_train(projet, statut="partiel-erreur"), racine=projet.racine
        )


def test_source_refuse_un_adaptateur_absent(projet) -> None:
    with pytest.raises(ConfigurationInvalide, match="adaptateur incomplet"):
        module_export.source_depuis_run(run_train(projet, adaptateur=False), racine=projet.racine)


def test_source_refuse_un_poids_lie_hors_liste(projet) -> None:
    """`adapter_model.safetensors` passe par le lecteur : un lien vers `eval/` est refusé."""
    train_id = run_train(projet)
    cible = projet.racine / "eval" / "secret.safetensors"
    cible.parent.mkdir(parents=True, exist_ok=True)
    cible.write_bytes(b"x")
    adaptateur = projet.racine / "runs" / "train" / train_id / "adaptateur"
    poids = adaptateur / "adapter_model.safetensors"
    poids.unlink()
    try:
        os.symlink(cible, poids)
    except (OSError, NotImplementedError):
        pytest.skip("création de lien symbolique refusée par le système")
    with pytest.raises(LectureInterdite):
        module_export.source_depuis_run(train_id, racine=projet.racine)


def test_chaque_fichier_de_l_adaptateur_passe_par_le_lecteur(projet, monkeypatch) -> None:
    train_id = run_train(projet)
    vus: list[str] = []
    autorise = module_export.chemin_autorise

    def espion(chemin: Any, lecteur: str, **options: Any) -> Path:
        vus.append(Path(chemin).name)
        return autorise(chemin, lecteur, **options)

    monkeypatch.setattr(module_export, "chemin_autorise", espion)
    module_export.adaptateur_du_run(train_id, racine=projet.racine)
    assert vus == ["adaptateur", *module_export.FICHIERS_ADAPTATEUR]


@pytest.mark.skipif(sys.platform != "win32", reason="jonction NTFS : Windows seulement")
def test_source_refuse_un_adaptateur_en_jonction(projet) -> None:
    import _winapi

    train_id = run_train(projet, adaptateur=False)
    cible = projet.racine / "eval" / "jeu"
    cible.mkdir(parents=True, exist_ok=True)
    for nom in module_export.FICHIERS_ADAPTATEUR:
        (cible / nom).write_bytes(b"{}")
    lien = projet.racine / "runs" / "train" / train_id / "adaptateur"
    _winapi.CreateJunction(str(cible), str(lien))
    with pytest.raises(LectureInterdite):
        module_export.source_depuis_run(train_id, racine=projet.racine)


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


def test_gguf_officiel_illisible_en_alerte(projet) -> None:
    gguf_officiel(projet).write_bytes(b"pas un GGUF")
    run = exporter(projet, module_export.source_temoin(SLUG), Outils(), PileExport())
    assert run.statut_courant() == "complet"
    controles = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))["controles"]
    assert controles["bloquants"] == []
    assert "non comparées" in controles["alertes"][0]


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
    # Sonde non valide : `degrade`, et l'évaluation refuse `ft:` sans choix explicite.
    statut = ouvrir_run(dossier.name, racine=projet.racine).statut_courant()
    assert statut == ("complet" if valide else "degrade")
    if not valide:
        with pytest.raises(ConfigurationInvalide, match="degrade"):
            modele_ref.resoudre(f"ft:{dossier.name}", "q4_k_m", racine=projet.racine)
        resolu = modele_ref.resoudre(
            f"ft:{dossier.name}", "q4_k_m", racine=projet.racine, accepter_degrade=True
        )
        assert resolu.gguf == dossier / "modele-q4_k_m.gguf"


def test_cli_transmet_le_delai(projet, cli, monkeypatch) -> None:
    commande = ["export", "--base", SLUG, "--sans-sonde", "--delai", "42", "--racine"]
    assert main([*commande, str(projet.racine)]) == CodeSortie.SUCCES
    assert [options["delai"] for _, options in cli.outils.appels] == [42.0, 42.0]


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


# --- Export multimodal (story B3) --------------------------------------------------------------

FICHIERS_PRE = ("chat_template.jinja", "preprocessor_config.json", "video_preprocessor_config.json")
VISION_VIDE = {"tenseurs": 1, "ecarts": [], "absents": [], "mtp_ignores": 0, "bloquants": []}


def base_multimodale(projet: Any, *, mtp: int | None = 1) -> Path:
    """Poids factices de `SLUG_MM` avec les fichiers du préprocesseur (tête MTP sous
    `text_config` si `mtp` est donné)."""
    base = projet.modeles / SLUG_MM / "hf"
    base.mkdir(parents=True)
    config = {"model_type": "qwen3_5"}
    if mtp is not None:
        config["text_config"] = {"mtp_num_hidden_layers": mtp}
    (base / "config.json").write_text(json.dumps(config), encoding="utf-8")
    (base / "model.safetensors").write_bytes(b"<poids-base-factices>")
    for nom in FICHIERS_PRE:
        (base / nom).write_text(f"<{nom}-factice>", encoding="utf-8")
    return base


@pytest.fixture
def vision_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Le contrôle de vision lit des safetensors : les fusions factices n'en écrivent pas."""
    monkeypatch.setattr(module_export, "controler_vision_inchangee", lambda b, f: VISION_VIDE)


def exporter_mm(projet: Any, source: Any, outils: Outils, pile: PileExport) -> Any:
    return exporter(projet, source, outils, pile, controles=cli_export.controler_format(SLUG_MM))


def test_fusion_multimodale_classe_conditionnelle(projet, vision_ok) -> None:
    base_multimodale(projet)
    train_id = run_train(projet, modele=SLUG_MM)
    pile = PileExport()
    source = module_export.source_depuis_run(train_id, racine=projet.racine)
    run = exporter_mm(projet, source, Outils(), pile)
    assert run.statut_courant() == "complet"
    assert pile.ordre[:4] == [
        "classe:conditionnelle",
        "base:float32",
        "adaptateur:" + train_id,
        "merge",
    ]
    assert run.manifeste.config["multimodal"] == "geler-vision"


def test_fusion_temoin_multimodal(projet, vision_ok) -> None:
    base_multimodale(projet)
    pile = PileExport()
    run = exporter_mm(projet, module_export.source_temoin(SLUG_MM), Outils(), pile)
    assert run.statut_courant() == "complet"
    assert "classe:conditionnelle" in pile.ordre and "merge" not in pile.ordre
    assert (run.dossier / "mmproj-f16.gguf").is_file()


def test_fusion_copie_preprocessor(projet, tmp_path) -> None:
    base = base_multimodale(projet)
    sortie = tmp_path / "hf-f16"
    module_export.fusionner(PileExport(), base, [], sortie, multimodal="geler-vision")
    for nom in FICHIERS_PRE:
        assert (sortie / nom).read_text(encoding="utf-8") == f"<{nom}-factice>"
    (base / "preprocessor_config.json").unlink()
    with pytest.raises(ConfigurationInvalide, match="preprocessor_config"):
        module_export.fusionner(
            PileExport(), base, [], tmp_path / "autre", multimodal="geler-vision"
        )


def test_copie_preprocesseur_garde_le_template_du_tokenizer(tmp_path) -> None:
    base, sortie = tmp_path / "base", tmp_path / "sortie"
    base.mkdir()
    sortie.mkdir()
    (base / "preprocessor_config.json").write_text("{}", encoding="utf-8")
    (base / "chat_template.jinja").write_text("base", encoding="utf-8")
    (sortie / "chat_template.jinja").write_text("tokenizer", encoding="utf-8")
    copies = module_export.copier_preprocesseur(base, sortie)
    assert (sortie / "chat_template.jinja").read_text(encoding="utf-8") == "tokenizer"
    assert "preprocessor_config.json" in copies and "chat_template.jinja" not in copies


@pytest.mark.parametrize(
    ("config", "attendu"),
    [
        ({"text_config": {"mtp_num_hidden_layers": 1}}, True),
        ({"mtp_num_hidden_layers": 2}, True),
        ({"text_config": {"mtp_num_hidden_layers": 0}}, False),
        ({"model_type": "qwen3_5"}, False),
        ({"mtp_num_hidden_layers": True}, False),
    ],
)
def test_a_tete_mtp(projet, config: dict[str, Any], attendu: bool) -> None:
    dossier = projet.modeles / "mtp-test" / "hf"
    dossier.mkdir(parents=True)
    (dossier / "config.json").write_text(json.dumps(config), encoding="utf-8")
    assert module_export.a_tete_mtp(dossier / "absent", dossier, racine=projet.racine) is attendu


def test_export_multimodal_sans_tete_mtp_pas_de_no_mtp(projet, vision_ok) -> None:
    base_multimodale(projet, mtp=None)
    outils = Outils()
    run = exporter_mm(projet, module_export.source_temoin(SLUG_MM), outils, PileExport())
    assert run.statut_courant() == "complet"
    assert "sans_mtp" not in outils.appels[0][1]
    assert run.manifeste.config["conversion"]["sans_mtp"] is False


def test_regex_adaptateur_visee_vision_refusee_avant_tout_run(projet, vision_ok) -> None:
    base_multimodale(projet)
    train_id = run_train(projet, modele=SLUG_MM)
    fichier = projet.racine / "runs" / "train" / train_id / "adaptateur" / "adapter_config.json"
    fichier.write_text(
        json.dumps({"peft_type": "LORA", "r": 16, "target_modules": r".*visual.*\.qkv$"}),
        encoding="utf-8",
    )
    source = module_export.source_depuis_run(train_id, racine=projet.racine)
    pile = PileExport()
    with pytest.raises(ConfigurationInvalide, match="regex"):
        exporter_mm(projet, source, Outils(), pile)
    assert not (projet.racine / "runs" / "export").exists() and pile.ordre == []


def test_fusion_dense_sans_preprocessor(projet, tmp_path) -> None:
    sortie = tmp_path / "hf-f16"
    module_export.fusionner(PileExport(), projet.modeles / SLUG / "hf", [], sortie)
    assert not any((sortie / nom).exists() for nom in FICHIERS_PRE)


# Contrôle de la vision : vrais safetensors minuscules.


def _ecrire(dossier: Path, tenseurs: dict[str, Any]) -> Path:
    safetensors_torch = pytest.importorskip("safetensors.torch")
    dossier.mkdir(parents=True, exist_ok=True)
    safetensors_torch.save_file(tenseurs, str(dossier / "model.safetensors"))
    return dossier


def _vision(tmp_path: Path, modifier: Any = None) -> tuple[Path, Path]:
    torch = pytest.importorskip("torch")
    generateur = torch.Generator().manual_seed(0)
    visuel = torch.randn(4, 4, generator=generateur).to(torch.bfloat16)
    langage = torch.randn(4, 4, generator=generateur)
    base = _ecrire(
        tmp_path / "base",
        {
            "model.visual.blocks.0.w": visuel,
            "model.visual.merger.b": visuel.clone(),
            "model.language_model.w": langage.to(torch.bfloat16),
            "mtp.layers.0.w": langage.to(torch.bfloat16),
        },
    )
    fusionne = {
        "model.visual.blocks.0.w": visuel.to(torch.float16),
        "model.visual.merger.b": visuel.clone().to(torch.float16),
        "model.language_model.w": (langage + 0.5).to(torch.float16),
    }
    if modifier is not None:
        modifier(fusionne)
    return base, _ecrire(tmp_path / "fusionne", fusionne)


def test_vision_inchangee_ok(tmp_path) -> None:
    base, fusionne = _vision(tmp_path)
    bilan = module_export.controler_vision_inchangee(base, fusionne)
    assert bilan["bloquants"] == [] and bilan["tenseurs"] == 2 and bilan["ecarts"] == []


def test_vision_modifiee_bloquante(tmp_path) -> None:
    def modifier(t: dict[str, Any]) -> None:
        t["model.visual.merger.b"] = t["model.visual.merger.b"] + 1

    base, fusionne = _vision(tmp_path, modifier)
    bilan = module_export.controler_vision_inchangee(base, fusionne)
    assert bilan["ecarts"] == ["model.visual.merger.b"] and bilan["bloquants"]


def test_vision_absente_bloquante(tmp_path) -> None:
    base, fusionne = _vision(tmp_path, lambda t: t.pop("model.visual.blocks.0.w"))
    bilan = module_export.controler_vision_inchangee(base, fusionne)
    assert bilan["absents"] == ["model.visual.blocks.0.w"] and bilan["bloquants"]


def test_mtp_absent_admis(tmp_path) -> None:
    base, fusionne = _vision(tmp_path)  # `mtp.*` dans la base seulement
    bilan = module_export.controler_vision_inchangee(base, fusionne)
    assert bilan["mtp_ignores"] == 1 and bilan["bloquants"] == []


def test_vision_modifiee_arrete_l_export_avant_la_conversion(projet, monkeypatch) -> None:
    base_multimodale(projet)
    bilan = {"tenseurs": 2, "ecarts": ["model.visual.w"], "absents": [], "bloquants": ["écart"]}
    monkeypatch.setattr(module_export, "controler_vision_inchangee", lambda b, f: bilan)
    outils = Outils()
    run = exporter_mm(projet, module_export.source_temoin(SLUG_MM), outils, PileExport())
    assert run.statut_courant() == "partiel-erreur" and outils.appels == []
    export = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))
    assert export["vision"]["ecarts"] == ["model.visual.w"]


@pytest.mark.parametrize(
    "module",
    [
        "base_model.model.model.visual.blocks.0.attn.qkv",
        "base_model.model.lm_head",
        "base_model.model.model.language_model.embed_tokens",
    ],
)
def test_adaptateur_regex_hors_language_model_refuse(projet, vision_ok, module: str) -> None:
    base_multimodale(projet)
    train_id = run_train(projet, modele=SLUG_MM)
    fichier = projet.racine / "runs" / "train" / train_id / "adaptateur" / "adapter_config.json"
    regex = r".*language_model.*\.(q_proj|k_proj)$"
    fichier.write_text(
        json.dumps({"peft_type": "LORA", "r": 16, "target_modules": regex}), encoding="utf-8"
    )
    source = module_export.source_depuis_run(train_id, racine=projet.racine)
    # La regex en chaîne est acceptée telle quelle ; le contrôle porte sur le modèle PEFT chargé.
    assert module_export.controler_adaptateur(fichier.parent, racine=projet.racine)["r"] == 16
    pile = PileExport(modules_lora=[MODULE_LORA_LANGAGE, module])
    with pytest.raises(ConfigurationInvalide, match="hors de"):
        exporter_mm(projet, source, Outils(), pile)


def test_export_multimodal_produit_mmproj(projet, vision_ok) -> None:
    base = base_multimodale(projet)
    train_id = run_train(projet, modele=SLUG_MM)
    outils = Outils()
    source = module_export.source_depuis_run(train_id, racine=projet.racine)
    run = exporter_mm(projet, source, outils, PileExport())
    assert run.statut_courant() == "complet"
    texte, quantification, mmproj = outils.appels
    assert texte[0] == "convertir" and texte[1]["sans_mtp"] is True and "mmproj" not in texte[1]
    assert quantification[0] == "quantifier"
    assert mmproj[1]["mmproj"] is True and "sans_mtp" not in mmproj[1]
    assert mmproj[1]["type_sortie"] == "f16"
    export = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))
    assert export["fichiers"] == {
        "f16": "modele-f16.gguf",
        "q4_k_m": "modele-q4_k_m.gguf",
        "mmproj": "mmproj-f16.gguf",
        "hf": "hf-f16",
    }
    assert export["multimodal"] == "geler-vision" and export["vision"]["bloquants"] == []
    assert export["llamacpp_tag"] == serveur.charger_config_llamacpp().tag
    for cle in ("f16", "q4_k_m", "mmproj"):
        contenu = (run.dossier / export["fichiers"][cle]).read_bytes()
        assert export["sha256"][cle] == hashlib.sha256(contenu).hexdigest()
    # Les lecteurs de `export.json` ne changent pas.
    for q in modele_ref.QUANTIFICATIONS:
        assert modele_ref.resoudre(f"ft:{run.run_id}", q, racine=projet.racine).precision == q
    assert module_export.octets_prevus(base, multimodal="geler-vision") > (
        module_export.octets_prevus(base)
    )


def test_export_dense_inchange(projet) -> None:
    """Non-régression : un modèle dense (sans `multimodal`) garde la chaîne d'origine."""
    train_id = run_train(projet)
    pile, outils = PileExport(), Outils()
    source = module_export.source_depuis_run(train_id, racine=projet.racine)
    run = exporter(projet, source, outils, pile)
    assert pile.ordre == [
        "base:float32",
        "adaptateur:" + train_id,
        "merge",
        "to:float16",
        "save",
        "tokenizer",
    ]
    assert [a[0] for a in outils.appels] == ["convertir", "quantifier"]
    # Ni `--mmproj` ni `--no-mtp` : les options passées à la conversion sont celles d'avant B3.
    assert set(outils.appels[0][1]) == {"type_sortie", "python", "delai", "journal"}
    export = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))
    assert set(export) == {
        "fichiers",
        "precisions",
        "chat_template_sha256_attendu",
        "fusion",
        "controles",
    }
    assert export["fichiers"] == {
        "f16": "modele-f16.gguf",
        "q4_k_m": "modele-q4_k_m.gguf",
        "hf": "hf-f16",
    }
    config = run.manifeste.config
    assert "multimodal" not in config and config["conversion"] == {"outtype": "f16"}
    assert not (run.dossier / "mmproj-f16.gguf").exists()
    assert not (run.dossier / "sonde-vision.json").exists()


# Sonde vision.


class ServeurVisionFactice:
    def __init__(self, *, vision: bool = True, reponse: str = "<réponse-factice>") -> None:
        self.vision, self.reponse = vision, reponse
        self.requetes: list[tuple[Any, ...]] = []
        self.options: dict[str, Any] = {}
        self.port = 12345

    def __call__(self, config: Any, variante: str, **options: Any) -> ServeurVisionFactice:
        self.options = {"variante": variante, **options}
        return self

    def __enter__(self) -> ServeurVisionFactice:
        return self

    def __exit__(self, *exc: object) -> None:
        pass

    def http(self, port: int) -> SimpleNamespace:
        def get(url: str, **_o: Any) -> SimpleNamespace:
            self.requetes.append(("GET", url))
            return SimpleNamespace(json=lambda: {"modalities": {"vision": self.vision}})

        def post(url: str, *, json: Any, **_o: Any) -> SimpleNamespace:
            self.requetes.append(("POST", url, json))
            corps = {"choices": [{"message": {"content": self.reponse}}]}
            return SimpleNamespace(status_code=200, json=lambda: corps, text="")

        return SimpleNamespace(get=get, post=post, close=lambda: None)


def test_png_synthetique_valide() -> None:
    import zlib

    png = cli_export.png_uni(8, 4)
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    idat = png.index(b"IDAT")
    taille = int.from_bytes(png[idat - 4 : idat], "big")
    assert len(zlib.decompress(png[idat + 4 : idat + 4 + taille])) == 4 * (1 + 8 * 3)


@pytest.mark.parametrize(
    ("factice", "valide"),
    [
        (ServeurVisionFactice(), True),
        (ServeurVisionFactice(vision=False), False),
        (ServeurVisionFactice(reponse="  "), False),
    ],
)
def test_sonde_vision_unitaire(tmp_path, factice, valide) -> None:
    bilan = cli_export.sonder_vision(
        tmp_path / "q.gguf", tmp_path / "m.gguf", SLUG_MM, fabrique=factice, http=factice.http
    )
    assert bilan["valide"] is valide
    assert factice.options["mmproj"] == tmp_path / "m.gguf"
    assert factice.options["variante"] == "cpu"
    if valide:
        contenu = factice.requetes[-1][2]["messages"][0]["content"]
        assert contenu[1]["image_url"]["url"].startswith("data:image/png;base64,")


def test_sonde_vision_serveur_en_panne(tmp_path) -> None:
    def fabrique(*_a: Any, **_k: Any) -> Any:
        raise serveur.ErreurInference("llama-server mort au démarrage")

    bilan = cli_export.sonder_vision(tmp_path / "q", tmp_path / "m", SLUG_MM, fabrique=fabrique)
    assert bilan["valide"] is False and "mort au démarrage" in bilan["motif"]


def _sonde_vision_factice(valide: bool, appels: list[Path]) -> Any:
    def sonde(gguf: Path, mmproj: Path, slug: str) -> dict[str, Any]:
        appels.append(mmproj)
        return {
            "valide": valide,
            "modalite_vision": valide,
            "reponse_non_vide": valide,
            "motif": None if valide else "pas de vision",
        }

    return sonde


@pytest.mark.parametrize("valide", [True, False])
def test_sonde_vision_cli(projet, cli, monkeypatch, vision_ok, valide) -> None:
    base_multimodale(projet)
    monkeypatch.setattr(sonde_outils, "sonder", _sonde_factice(True, []))
    appels: list[Path] = []
    monkeypatch.setattr(cli_export, "sonder_vision", _sonde_vision_factice(valide, appels))
    train_id = run_train(projet, modele=SLUG_MM)
    code = main(["export", "--depuis", train_id, "--racine", str(projet.racine)])
    (dossier,) = (projet.racine / "runs" / "export").iterdir()
    assert appels == [dossier / "mmproj-f16.gguf"]
    bilan = json.loads((dossier / "sonde-vision.json").read_text(encoding="utf-8"))
    assert bilan["valide"] is valide
    statut = ouvrir_run(dossier.name, racine=projet.racine).statut_courant()
    assert (code, statut) == ((0, "complet") if valide else (1, "degrade"))


def test_cli_sans_sonde_saute_la_vision(projet, cli, monkeypatch, vision_ok) -> None:
    base_multimodale(projet)
    monkeypatch.setattr(cli_export, "sonder_vision", lambda *a: pytest.fail("sonde lancée"))
    commande = ["export", "--base", SLUG_MM, "--sans-sonde", "--racine", str(projet.racine)]
    assert main(commande) == CodeSortie.SUCCES


def test_cli_dense_sans_sonde_vision(projet, cli, monkeypatch) -> None:
    monkeypatch.setattr(sonde_outils, "sonder", _sonde_factice(True, []))
    monkeypatch.setattr(cli_export, "sonder_vision", lambda *a: pytest.fail("sonde lancée"))
    assert main(["export", "--base", SLUG, "--racine", str(projet.racine)]) == CodeSortie.SUCCES
