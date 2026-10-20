"""Export LoRA GGUF (story 15.6) : conversion de l'adaptateur sans fusion, refus et CLI.

Le convertisseur et la sonde de chargement sont des doubles : aucun processus llama.cpp. Le
LoRA GGUF écrit par le double n'a qu'un en-tête de métadonnées (format GGUF v3).
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path, PurePosixPath
from typing import Any

import pytest

from slmsp.cli import export as cli_export
from slmsp.cli import main
from slmsp.core.artefacts import nouveau_run, ouvrir_run
from slmsp.core.erreurs import CodeSortie, ConfigurationInvalide
from slmsp.evaluation import modele_ref
from slmsp.inference import serveur
from slmsp.train import export as module_export

SLUG = "granite-4.0-1b"
TEMPLATE = "{# template-factice-export #}"
SHA_TEMPLATE = hashlib.sha256(TEMPLATE.encode()).hexdigest()


def ecrire_gguf(chemin: Path, metadonnees: dict[str, Any]) -> Path:
    """En-tête GGUF v3 sans tenseur : chaînes (type 8) et entiers non signés (type 4)."""

    def chaine(texte: str) -> bytes:
        donnees = texte.encode("utf-8")
        return struct.pack("<Q", len(donnees)) + donnees

    corps = b""
    for cle, valeur in metadonnees.items():
        corps += chaine(cle)
        if isinstance(valeur, str):
            corps += struct.pack("<I", 8) + chaine(valeur)
        else:
            corps += struct.pack("<I", 4) + struct.pack("<I", valeur)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_bytes(b"GGUF" + struct.pack("<IQQ", 3, 0, len(metadonnees)) + corps)
    return chemin


def run_train(projet: Any) -> str:
    config = {"toml": {"modele": SLUG, "methode": "qlora"}}
    run = nouveau_run(
        "train", "m1-qlora", config, racine=projet.racine, chat_template_sha256=SHA_TEMPLATE
    )
    dossier = run.dossier / "adaptateur"
    dossier.mkdir()
    (dossier / "adapter_config.json").write_text(
        json.dumps({"peft_type": "LORA", "r": 16, "lora_alpha": 32, "target_modules": ["q_proj"]}),
        encoding="utf-8",
    )
    (dossier / "adapter_model.safetensors").write_bytes(b"<adaptateur-factice>")
    run.terminer("complet")
    return run.run_id


def gguf_officiel(projet: Any) -> Path:
    fichier = serveur.charger_config_modele(SLUG).gguf_pour("q4_k_m")
    assert fichier is not None
    chemin = projet.modeles / SLUG / "gguf" / PurePosixPath(fichier.fichier).name
    return ecrire_gguf(chemin, {"general.architecture": "granite", "granite.block_count": 40})


@pytest.fixture(autouse=True)
def _pythonutf8(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTHONUTF8", "1")


class Convertisseur:
    """Double de `convertir_lora_vers_gguf` : écrit un en-tête de LoRA GGUF."""

    def __init__(self, **metadonnees: Any) -> None:
        self.metadonnees = {
            "general.type": "adapter",
            "general.architecture": "granite",
            "adapter.type": "lora",
            "adapter.lora.alpha": 32,
            **metadonnees,
        }
        self.appels: list[tuple[Path, Path, Path, dict[str, Any]]] = []

    def __call__(self, adaptateur: Path, base: Path, sortie: Path, **options: Any) -> Path:
        self.appels.append((Path(adaptateur), Path(base), Path(sortie), options))
        return ecrire_gguf(Path(sortie), self.metadonnees)


def ecrire_config(projet: Any, train_id: str, **config: Any) -> None:
    dossier = projet.racine / "runs" / "train" / train_id / "adaptateur"
    contenu = {"peft_type": "LORA", "r": 16, "lora_alpha": 32, "target_modules": ["q_proj"]}
    (dossier / "adapter_config.json").write_text(
        json.dumps({**contenu, **config}), encoding="utf-8"
    )


def exporter_lora(projet: Any, train_id: str, convertisseur: Convertisseur, **options: Any) -> Any:
    source = module_export.source_depuis_run(train_id, racine=projet.racine)
    options.setdefault("controles", cli_export.controler_lora(SLUG))
    return module_export.exporter_lora(
        source,
        racine=projet.racine,
        convertir=convertisseur,
        sortie=lambda _m: None,
        **options,
    )


def test_export_lora_nominal(projet) -> None:
    gguf_officiel(projet)
    train_id = run_train(projet)
    convertisseur = Convertisseur()
    run = exporter_lora(projet, train_id, convertisseur)
    assert run.statut_courant() == "complet"
    assert run.dossier.parent == projet.racine / "runs" / "export-lora"
    assert (run.dossier / module_export.NOM_LORA).is_file()
    ((adaptateur, base, sortie, options),) = convertisseur.appels
    assert adaptateur == projet.racine / "runs" / "train" / train_id / "adaptateur"
    assert base == projet.modeles / SLUG / "hf"
    assert sortie == run.dossier / module_export.NOM_LORA
    assert options["type_sortie"] == "f16" and options["delai"] > 0
    manifeste = ouvrir_run(run.run_id, racine=projet.racine).manifeste
    assert manifeste.modele_ref == f"base:{SLUG}"
    assert manifeste.parents == [train_id]
    export = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))
    assert export["fichiers"] == {"lora": module_export.NOM_LORA}
    assert export["adaptateur"]["r"] == 16 and export["adaptateur"]["lora_alpha"] == 32
    assert export["controles"]["bloquants"] == []
    assert len(export["sha256"]["lora"]) == 64


@pytest.mark.parametrize(
    ("config", "motif"),
    [
        ({"use_dora": True}, "DoRA"),
        ({"use_rslora": True}, "rsLoRA"),
        ({"peft_type": "ADALORA"}, "non convertible"),
        ({"init_lora_weights": "pissa"}, "PiSSA"),
        ({"modules_to_save": ["lm_head"]}, "embeddings"),
        ({"alpha_pattern": {"q_proj": 64}}, "alpha_pattern"),
    ],
)
def test_adaptateur_non_convertible_refuse_avant_tout_run(
    projet, config: dict[str, Any], motif: str
) -> None:
    train_id = run_train(projet)
    ecrire_config(projet, train_id, **config)
    convertisseur = Convertisseur()
    with pytest.raises(ConfigurationInvalide, match=motif):
        exporter_lora(projet, train_id, convertisseur)
    assert convertisseur.appels == []
    assert not (projet.racine / "runs" / "export-lora").exists()


def test_rank_pattern_accepte(projet) -> None:
    """llama.cpp lit le rang de chaque tenseur : un rank_pattern reste fidèle."""
    gguf_officiel(projet)
    train_id = run_train(projet)
    ecrire_config(projet, train_id, rank_pattern={"q_proj": 8}, alpha_pattern={})
    assert exporter_lora(projet, train_id, Convertisseur()).statut_courant() == "complet"


def test_gabarit_de_la_base_compare_a_l_entrainement(projet) -> None:
    chemin = gguf_officiel(projet)
    run = exporter_lora(projet, run_train(projet), Convertisseur())
    export = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))
    assert any("gabarit servi" in a for a in export["controles"]["alertes"])
    assert export["controles"]["metadonnees"]["chat_template_sha256_entrainement"] == SHA_TEMPLATE
    # Même gabarit dans le GGUF de la base : aucune alerte.
    ecrire_gguf(chemin, {"general.architecture": "granite", "tokenizer.chat_template": TEMPLATE})
    run = exporter_lora(projet, run_train(projet), Convertisseur())
    export = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))
    assert export["controles"]["alertes"] == []
    assert export["controles"]["metadonnees"]["chat_template_sha256_servi"] == SHA_TEMPLATE


def test_architecture_differente_de_la_base_bloquante(projet) -> None:
    gguf_officiel(projet)
    run = exporter_lora(
        projet, run_train(projet), Convertisseur(**{"general.architecture": "llama"})
    )
    assert run.statut_courant() == "partiel-erreur"
    export = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))
    assert "architecture du LoRA" in export["controles"]["bloquants"][0]
    with pytest.raises(ConfigurationInvalide, match="partiel-erreur"):
        modele_ref.resoudre(f"lora:{run.run_id}", "q4_k_m", racine=projet.racine)


def test_gguf_qui_n_est_pas_un_lora_bloquant(projet) -> None:
    gguf_officiel(projet)
    run = exporter_lora(projet, run_train(projet), Convertisseur(**{"general.type": "model"}))
    assert run.statut_courant() == "partiel-erreur"


def test_base_absente_alerte_sans_bloquer(projet) -> None:
    run = exporter_lora(projet, run_train(projet), Convertisseur())
    assert run.statut_courant() == "complet"
    export = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))
    assert "compatibilité non vérifiée" in export["controles"]["alertes"][0]


def test_echec_de_conversion_termine_le_run(projet) -> None:
    def echoue(*_a: Any, **_k: Any) -> Path:
        raise RuntimeError("convertisseur en échec")

    source = module_export.source_depuis_run(run_train(projet), racine=projet.racine)
    with pytest.raises(RuntimeError):
        module_export.exporter_lora(
            source, racine=projet.racine, convertir=echoue, controles=lambda *_: {}
        )
    (dossier,) = (projet.racine / "runs" / "export-lora").iterdir()
    assert ouvrir_run(dossier.name, racine=projet.racine).statut_courant() == "partiel-erreur"


def test_temoin_refuse(projet) -> None:
    with pytest.raises(ConfigurationInvalide, match="un seul adaptateur"):
        module_export.exporter_lora(
            module_export.source_temoin(SLUG),
            racine=projet.racine,
            convertir=Convertisseur(),
            controles=lambda *_: {},
        )


# --- CLI -------------------------------------------------------------------------------


@pytest.fixture
def cli(projet, monkeypatch) -> Any:
    convertisseur = Convertisseur()
    monkeypatch.setattr(serveur, "convertir_lora_vers_gguf", convertisseur)
    gguf_officiel(projet)
    return convertisseur


def _sonde(valide: bool, appels: list[Any]) -> Any:
    def sonder(base: Path, lora: Path, slug: str, variante: str) -> dict[str, Any]:
        appels.append((base.name, lora.name, slug, variante))
        return {
            "valide": valide,
            "echelle": 1.0 if valide else None,
            "motif": None if valide else "x",
        }

    return sonder


@pytest.mark.parametrize(
    ("valide", "code"), [(True, CodeSortie.SUCCES), (False, CodeSortie.ERREUR)]
)
def test_cli_export_lora_puis_sonde(projet, cli, monkeypatch, capsys, valide, code) -> None:
    appels: list[Any] = []
    monkeypatch.setattr(cli_export, "sonder_lora", _sonde(valide, appels))
    train_id = run_train(projet)
    commande = ["export", "lora", "--depuis", train_id, "--variante", "cpu"]
    assert main([*commande, "--racine", str(projet.racine)]) == code
    (dossier,) = (projet.racine / "runs" / "export-lora").iterdir()
    assert [(a[1], a[2], a[3]) for a in appels] == [("adaptateur-lora.gguf", SLUG, "cpu")]
    assert f"lora:{dossier.name}" in capsys.readouterr().out
    bilan = json.loads((dossier / "sonde-lora.json").read_text(encoding="utf-8"))
    assert bilan["valide"] is valide and bilan["variante"] == "cpu" and bilan["lancee"] is True
    statut = ouvrir_run(dossier.name, racine=projet.racine).statut_courant()
    assert statut == ("complet" if valide else "degrade")
    if not valide:
        with pytest.raises(ConfigurationInvalide, match="degrade"):
            modele_ref.resoudre(f"lora:{dossier.name}", "q4_k_m", racine=projet.racine)


def test_cli_export_lora_sans_sonde(projet, cli, monkeypatch) -> None:
    monkeypatch.setattr(cli_export, "sonder_lora", lambda *a, **k: pytest.fail("sonde lancée"))
    commande = ["export", "lora", "--depuis", run_train(projet), "--sans-sonde"]
    assert main([*commande, "--racine", str(projet.racine)]) == CodeSortie.SUCCES
    (dossier,) = (projet.racine / "runs" / "export-lora").iterdir()
    bilan = json.loads((dossier / "sonde-lora.json").read_text(encoding="utf-8"))
    assert bilan["lancee"] is False and bilan["valide"] is None


def test_cli_export_lora_sans_base_consigne_la_sonde_non_lancee(
    projet, cli, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(cli_export, "sonder_lora", lambda *a, **k: pytest.fail("sonde lancée"))
    monkeypatch.setattr(cli_export, "gguf_officiel", lambda _slug: None)
    commande = ["export", "lora", "--depuis", run_train(projet)]
    assert main([*commande, "--racine", str(projet.racine)]) == CodeSortie.SUCCES
    (dossier,) = (projet.racine / "runs" / "export-lora").iterdir()
    bilan = json.loads((dossier / "sonde-lora.json").read_text(encoding="utf-8"))
    assert bilan["lancee"] is False and "absent" in bilan["motif"]
    assert "compatibilité non vérifiée" in capsys.readouterr().err


@pytest.mark.parametrize(
    "arguments",
    [["lora"], ["lora", "--base", SLUG], ["lora", "--depuis", "x", "--dry-run"]],
)
def test_cli_export_lora_usage(arguments: list[str]) -> None:
    assert main(["export", *arguments]) == CodeSortie.USAGE


def test_sonder_lora_lit_l_echelle_servie(tmp_path: Path) -> None:
    class Serveur:
        port = 1

        def __init__(self, config: Any, variante: str, **options: Any) -> None:
            self.options = options
            appels.append((variante, options))

        def __enter__(self) -> Serveur:
            return self

        def __exit__(self, *_exc: object) -> None:
            return None

    class Client:
        def get(self, url: str, timeout: float) -> Any:
            assert url.endswith("/lora-adapters")
            return type("R", (), {"status_code": 200, "json": lambda _s: reponse})()

        def close(self) -> None:
            return None

    appels: list[Any] = []
    reponse: list[dict[str, Any]] = [{"id": 0, "path": "a.gguf", "scale": 1.0}]
    bilan = cli_export.sonder_lora(
        tmp_path / "base.gguf",
        tmp_path / "a.gguf",
        SLUG,
        "cpu",
        fabrique=Serveur,
        http=lambda _port: Client(),
    )
    assert bilan["valide"] is True
    ((variante, options),) = appels
    assert variante == "cpu" and options["lora"].echelle == 1.0
    reponse.clear()
    assert (
        cli_export.sonder_lora(
            tmp_path / "base.gguf",
            tmp_path / "a.gguf",
            SLUG,
            "cpu",
            fabrique=Serveur,
            http=lambda _port: Client(),
        )["valide"]
        is False
    )
