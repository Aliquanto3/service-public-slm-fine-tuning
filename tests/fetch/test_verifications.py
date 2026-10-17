"""Contrôles D7 des Modèles de base candidats (`slmsp.fetch.verifications`, story 8.1).

Sans réseau ni binaire : `config.json` de fixture, GGUF synthétique écrit par le test,
serveur `llama-server` remplacé par une doublure injectée.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import struct
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from slmsp.cli import main
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.fetch import verifications
from slmsp.fetch.config import charger_config_modele
from slmsp.fetch.verifications import (
    CANDIDATS,
    GgufInvalide,
    lire_metadonnees_gguf,
    template_hf,
    verifier_chat_template,
    verifier_config_hf,
    verifier_modele,
    verifier_serveur,
)
from slmsp.inference.processus import ErreurInference

FIXTURES = Path(__file__).resolve().parent / "fixtures"
REV = "a" * 40
GGUF_NOM = "m-Q4_K_M.gguf"
TEMPLATE_HF = "{% for m in messages %}<|{{ m.role }}|>{{ m.content }}\n{% endfor %}"
TEMPLATE_AUTRE = "{% for m in messages %}[{{ m.role }}] {{ m.content }}{% endfor %}"


def sha(texte: str) -> str:
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()


# --- GGUF synthétique -----------------------------------------------------------------------


def _chaine(texte: str) -> bytes:
    donnees = texte.encode("utf-8")
    return struct.pack("<Q", len(donnees)) + donnees


def _valeur(type_: int, valeur: Any) -> bytes:
    formats = {0: "<B", 1: "<b", 2: "<H", 3: "<h", 4: "<I", 5: "<i", 6: "<f", 7: "<?"}
    formats.update({10: "<Q", 11: "<q", 12: "<d"})
    if type_ in formats:
        return struct.pack(formats[type_], valeur)
    if type_ == 8:
        return _chaine(valeur)
    type_elements, elements = valeur
    corps = b"".join(_valeur(type_elements, e) for e in elements)
    return struct.pack("<IQ", type_elements, len(elements)) + corps


def ecrire_gguf(
    chemin: Path, paires: list[tuple[str, int, Any]], *, version: int = 3, magie: bytes = b"GGUF"
) -> Path:
    """En-tête GGUF : `paires` = (clé, type, valeur) ; tableau : (type, [éléments])."""
    corps = b"".join(_chaine(cle) + struct.pack("<I", t) + _valeur(t, v) for cle, t, v in paires)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_bytes(magie + struct.pack("<IQQ", version, 7, len(paires)) + corps + b"\0" * 64)
    return chemin


def gguf_modele(chemin: Path, template: str | None) -> Path:
    paires: list[tuple[str, int, Any]] = [
        ("general.architecture", 8, "granite"),
        ("granite.context_length", 4, 131072),
        ("tokenizer.ggml.tokens", 9, (8, [f"tok{i}" for i in range(500)])),
        ("tokenizer.ggml.scores", 9, (6, [0.5] * 500)),
    ]
    if template is not None:
        paires.append(("tokenizer.chat_template", 8, template))
    return ecrire_gguf(chemin, paires)


def test_lecteur_gguf_scalaires_chaines_tableaux(tmp_path: Path) -> None:
    chemin = ecrire_gguf(
        tmp_path / "s.gguf",
        [
            ("general.architecture", 8, "granite"),
            ("u8", 0, 7),
            ("i8", 1, -3),
            ("u16", 2, 65000),
            ("i16", 3, -2),
            ("u32", 4, 4_000_000_000),
            ("i32", 5, -5),
            ("f32", 6, 1.5),
            ("bool", 7, True),
            ("tokenizer.ggml.tokens", 9, (8, ["a", "bé", "c"] * 1000)),
            ("tableau.entiers", 9, (5, list(range(100)))),
            ("tableau.tableaux", 9, (9, [(4, [1, 2]), (4, [3])])),
            ("u64", 10, 2**40),
            ("i64", 11, -(2**40)),
            ("f64", 12, 0.25),
            ("tokenizer.chat_template", 8, TEMPLATE_HF),
            ("tableau.voulu", 9, (8, ["x", "y"])),
        ],
    )
    voulues = [
        "general.architecture",
        "u8",
        "i8",
        "u16",
        "i16",
        "u32",
        "i32",
        "f32",
        "bool",
        "u64",
        "i64",
        "f64",
        "tokenizer.chat_template",
        "tableau.voulu",
        "absente",
    ]
    valeurs = lire_metadonnees_gguf(chemin, voulues)
    assert valeurs == {
        "general.architecture": "granite",
        "u8": 7,
        "i8": -3,
        "u16": 65000,
        "i16": -2,
        "u32": 4_000_000_000,
        "i32": -5,
        "f32": 1.5,
        "bool": True,
        "u64": 2**40,
        "i64": -(2**40),
        "f64": 0.25,
        "tokenizer.chat_template": TEMPLATE_HF,
        "tableau.voulu": ["x", "y"],
    }
    assert lire_metadonnees_gguf(chemin, ["tableau.tableaux"]) == {
        "tableau.tableaux": [[1, 2], [3]]
    }


def test_lecteur_gguf_s_arrete_des_que_les_cles_sont_lues(tmp_path: Path) -> None:
    # Après la clé voulue, une paire de type inconnu : jamais atteinte.
    chemin = ecrire_gguf(
        tmp_path / "a.gguf",
        [("general.architecture", 8, "qwen3"), ("tokenizer.chat_template", 8, "t")],
    )
    donnees = chemin.read_bytes().rstrip(b"\0") + _chaine("piege") + struct.pack("<I", 99)
    chemin.write_bytes(donnees[:4] + struct.pack("<IQQ", 3, 0, 3) + donnees[24:])
    assert lire_metadonnees_gguf(chemin, ["tokenizer.chat_template"]) == {
        "tokenizer.chat_template": "t"
    }
    with pytest.raises(GgufInvalide, match="type de valeur GGUF inconnu : 99"):
        lire_metadonnees_gguf(chemin, ["absente"])


def test_lecteur_gguf_refuse_un_en_tete_invalide(tmp_path: Path) -> None:
    with pytest.raises(GgufInvalide, match="magie"):
        lire_metadonnees_gguf(ecrire_gguf(tmp_path / "a.gguf", [], magie=b"GGML"), ["x"])
    with pytest.raises(GgufInvalide, match="version GGUF 1"):
        lire_metadonnees_gguf(ecrire_gguf(tmp_path / "b.gguf", [], version=1), ["x"])
    tronque = tmp_path / "c.gguf"
    tronque.write_bytes(b"GGUF\x03\x00")
    with pytest.raises(GgufInvalide, match="fin de fichier"):
        lire_metadonnees_gguf(tronque, ["x"])


def test_gguf_v2_accepte(tmp_path: Path) -> None:
    chemin = ecrire_gguf(tmp_path / "v2.gguf", [("general.name", 8, "v2")], version=2)
    assert lire_metadonnees_gguf(chemin, ["general.name"]) == {"general.name": "v2"}


# --- Configuration HF -----------------------------------------------------------------------


def config_modele(**maj: Any) -> ConfigModele:
    base: dict[str, Any] = {
        "depot_hf": "org/modele",
        "revision": REV,
        "fichiers": ["config.json"],
        "gguf": {
            "depot": "org/modele-GGUF",
            "fichier": GGUF_NOM,
            "sha256": "0" * 64,
            "revision": "b" * 40,
            "source": "officielle",
        },
        "contexte": 8192,
        "protocole_outils": "natif",
    }
    return ConfigModele.model_validate({**base, **maj})


def dossier_hf(tmp_path: Path, fixture: str | None = None, **contenu: Any) -> Path:
    dossier = tmp_path / "models" / "m" / "hf"
    dossier.mkdir(parents=True, exist_ok=True)
    if fixture is not None:
        shutil.copy(FIXTURES / f"config-{fixture}.json", dossier / "config.json")
    else:
        (dossier / "config.json").write_text(json.dumps(contenu), encoding="utf-8")
    return dossier


def statuts(controles: list[verifications.Controle]) -> dict[str, str]:
    return {c.controle: c.statut for c in controles}


def test_dense(tmp_path: Path) -> None:
    controles = verifier_config_hf("m", config_modele(), dossier_hf(tmp_path, "dense"))
    assert statuts(controles) == {"dense": "ok", "fp8": "ok", "vision": "ok"}
    assert controles[0].valeurs["layer_types"] == {"attention": 4}


def test_hybride_ecarte_en_nommant_les_couches(tmp_path: Path) -> None:
    (dense, fp8, vision) = verifier_config_hf("m", config_modele(), dossier_hf(tmp_path, "hybride"))
    assert (dense.statut, fp8.statut, vision.statut) == ("echec", "ok", "ok")
    assert "5 couche(s) sur 6 hors attention" in dense.detail
    assert "0 (mamba)" in dense.detail and "5 (mamba)" in dense.detail
    assert "3 (" not in dense.detail
    assert verifications.ecartes([dense, fp8, vision]) == {"m": [f"dense : {dense.detail}"]}


@pytest.mark.parametrize(
    ("contenu", "attendu"),
    [
        ({"text_config": {"layer_types": ["full_attention", "sliding_attention"]}}, "ok"),
        ({"text_config": {"layer_types": ["full_attention", "mamba"]}}, "echec"),
        ({"model_type": "qwen3"}, "ok"),
    ],
)
def test_dense_text_config_ou_absent(tmp_path: Path, contenu: dict, attendu: str) -> None:
    controles = verifier_config_hf("m", config_modele(), dossier_hf(tmp_path, **contenu))
    assert controles[0].statut == attendu


def test_fp8(tmp_path: Path) -> None:
    controles = verifier_config_hf("m", config_modele(), dossier_hf(tmp_path, "fp8"))
    assert statuts(controles) == {"dense": "ok", "fp8": "echec", "vision": "ok"}
    assert "quantization_config présent (fp8)" in controles[1].detail


@pytest.mark.parametrize(
    "contenu",
    [
        {"torch_dtype": "float8_e4m3fn"},
        {"dtype": "float8_e5m2"},
        {"text_config": {"dtype": "float8_e4m3fn"}},
        {"text_config": {"quantization_config": {"quant_method": "fp8"}}},
    ],
)
def test_fp8_par_dtype(tmp_path: Path, contenu: dict) -> None:
    controles = verifier_config_hf("m", config_modele(), dossier_hf(tmp_path, **contenu))
    assert controles[1].statut == "echec"


def test_vision(tmp_path: Path) -> None:
    dossier = dossier_hf(tmp_path, "vision")
    (_, _, vision) = verifier_config_hf("m", config_modele(), dossier)
    assert vision.statut == "echec" and "inscrire exclure_vision = true" in vision.detail
    (_, _, vision) = verifier_config_hf("m", config_modele(exclure_vision=True), dossier)
    assert vision.statut == "ok" and vision.valeurs["model_type"] == "pixtral"


def test_config_json_absent(tmp_path: Path) -> None:
    dossier = tmp_path / "vide"
    dossier.mkdir()
    controles = verifier_config_hf("m", config_modele(), dossier)
    assert set(statuts(controles).values()) == {"echec"}


# --- Chat template --------------------------------------------------------------------------


def preparer_template(
    tmp_path: Path, hf: str | None, gguf: str | None, *, fichier_jinja: bool = True
) -> tuple[Path, Path]:
    base = tmp_path / "models" / "m"
    (base / "hf").mkdir(parents=True, exist_ok=True)
    if hf is not None and fichier_jinja:
        (base / "hf" / "chat_template.jinja").write_bytes(hf.encode("utf-8"))
    return base, gguf_modele(base / "gguf" / GGUF_NOM, gguf)


def test_template_identique(tmp_path: Path) -> None:
    base, gguf = preparer_template(tmp_path, TEMPLATE_HF, TEMPLATE_HF)
    controle = verifier_chat_template("m", config_modele(), base, gguf)
    assert controle.statut == "ok"
    assert controle.valeurs["sha256_hf"] == controle.valeurs["sha256_gguf"] == sha(TEMPLATE_HF)
    assert not (base / "chat_template.jinja").exists()


def test_template_identique_avec_force_exporte(tmp_path: Path) -> None:
    """Revue lot 3b, P3 : `chat_template_force` exige le fichier exporté, même identique."""
    base, gguf = preparer_template(tmp_path, TEMPLATE_HF, TEMPLATE_HF)
    controle = verifier_chat_template("m", config_modele(chat_template_force=True), base, gguf)
    assert controle.statut == "ok"
    assert "superflu" in controle.detail
    assert controle.valeurs["issue_export"] == "cree"
    assert (base / "chat_template.jinja").read_bytes() == TEMPLATE_HF.encode("utf-8")


def test_template_different_sans_force(tmp_path: Path) -> None:
    base, gguf = preparer_template(tmp_path, TEMPLATE_HF, TEMPLATE_AUTRE)
    controle = verifier_chat_template("m", config_modele(), base, gguf)
    assert controle.statut == "echec"
    assert "inscrire chat_template_force = true" in controle.detail
    assert (base / "chat_template.jinja").read_bytes() == TEMPLATE_HF.encode("utf-8")
    assert controle.valeurs["issue_export"] == "cree"
    assert not (base / "chat_template.jinja.part").exists()


def test_template_different_avec_force(tmp_path: Path) -> None:
    base, gguf = preparer_template(tmp_path, TEMPLATE_HF, TEMPLATE_AUTRE)
    config = config_modele(chat_template_force=True)
    controle = verifier_chat_template("m", config, base, gguf)
    assert controle.statut == "ok"
    assert (base / "chat_template.jinja").read_bytes() == TEMPLATE_HF.encode("utf-8")
    # Relance : le fichier identique est gardé tel quel.
    assert verifier_chat_template("m", config, base, gguf).valeurs["issue_export"] == "identique"


def test_template_absent_du_gguf(tmp_path: Path) -> None:
    base, gguf = preparer_template(tmp_path, TEMPLATE_HF, None)
    controle = verifier_chat_template("m", config_modele(chat_template_force=True), base, gguf)
    assert controle.statut == "ok" and "absent du GGUF" in controle.detail
    assert controle.valeurs["sha256_gguf"] is None


def test_export_en_conflit_laisse_le_fichier_intact(tmp_path: Path) -> None:
    base, gguf = preparer_template(tmp_path, TEMPLATE_HF, TEMPLATE_AUTRE)
    (base / "chat_template.jinja").write_text("autre contenu", encoding="utf-8")
    controle = verifier_chat_template("m", config_modele(chat_template_force=True), base, gguf)
    assert controle.statut == "echec" and "laissé intact" in controle.detail
    assert (base / "chat_template.jinja").read_text(encoding="utf-8") == "autre contenu"


def test_template_hf_depuis_tokenizer_config(tmp_path: Path) -> None:
    dossier = tmp_path / "hf"
    dossier.mkdir()
    assert template_hf(dossier) is None
    config = dossier / "tokenizer_config.json"
    config.write_text(json.dumps({"chat_template": TEMPLATE_HF}), encoding="utf-8")
    assert template_hf(dossier) == TEMPLATE_HF
    liste = [{"name": "tool_use", "template": "x"}, {"name": "default", "template": "d"}]
    config.write_text(json.dumps({"chat_template": liste}), encoding="utf-8")
    assert template_hf(dossier) == "d"
    (dossier / "chat_template.jinja").write_text("prioritaire", encoding="utf-8")
    assert template_hf(dossier) == "prioritaire"


def test_template_hf_introuvable(tmp_path: Path) -> None:
    base, gguf = preparer_template(tmp_path, None, TEMPLATE_HF)
    controle = verifier_chat_template("m", config_modele(), base, gguf)
    assert controle.statut == "echec" and "aucun template" in controle.detail


@pytest.mark.parametrize(
    "maj", [{"fichiers": []}, {"fichiers": [], "embedding": True, "pooling": "cls"}]
)
def test_sans_poids_hf(tmp_path: Path, maj: dict) -> None:
    controles = verifier_modele("m", config_modele(**maj), tmp_path, sans_serveur=True)
    assert statuts(controles) == {
        "dense": "sans-objet",
        "fp8": "sans-objet",
        "vision": "sans-objet",
        "chat_template": "sans-objet",
        "serveur": "sans-objet",
    }


# --- Serveur --------------------------------------------------------------------------------


class ServeurDouble:
    """Doublure de `ServeurLlama` : gestionnaire de contexte, `port`, `journal`."""

    def __init__(self, erreur: BaseException | None = None) -> None:
        self.erreur = erreur
        self.appels: list[tuple[Any, ...]] = []
        self.ouvert = False
        self.port = 43210
        self.journal = Path("journal-llama.log")

    def __call__(self, config: ConfigModele, variante: str, *, slug: str) -> ServeurDouble:
        self.appels.append((config, variante, slug))
        return self

    def __enter__(self) -> ServeurDouble:
        if self.erreur is not None:
            raise self.erreur
        self.ouvert = True
        return self

    def __exit__(self, *exc: object) -> None:
        self.ouvert = False


PROPS = {
    "modalities": {"vision": False, "audio": False},
    "default_generation_settings": {"n_ctx": 8192},
    "build_info": "b11429-abcdef",
    "chat_template": TEMPLATE_HF,
}


def test_serveur_ok_et_props(tmp_path: Path) -> None:
    double = ServeurDouble()
    ports: list[int] = []

    def lire_props(port: int) -> dict[str, Any]:
        assert double.ouvert
        ports.append(port)
        return PROPS

    config = config_modele(exclure_vision=True)
    controle = verifier_serveur("m", config, double, lire_props=lire_props)
    assert controle.statut == "ok" and "texte seul" in controle.detail
    assert double.appels == [(config, "cpu", "m")] and ports == [43210]
    assert not double.ouvert
    assert controle.valeurs["modalities"] == {"vision": False, "audio": False}
    assert controle.valeurs["n_ctx"] == 8192
    assert controle.valeurs["sha256_chat_template"] == sha(TEMPLATE_HF)


def test_serveur_echec_avec_fin_du_journal() -> None:
    erreur = ErreurInference("llama-server (generation) mort au démarrage ; fin du journal :\nE")
    controle = verifier_serveur(
        "m", config_modele(), ServeurDouble(erreur), lire_props=lambda _port: PROPS
    )
    assert controle.statut == "echec"
    assert controle.detail.startswith("ErreurInference : llama-server")
    assert controle.detail.endswith("fin du journal :\nE")
    assert controle.valeurs["journal"] == "journal-llama.log"


def test_serveur_vision_chargee_malgre_exclusion() -> None:
    props = {**PROPS, "modalities": {"vision": True}}
    controle = verifier_serveur(
        "m", config_modele(exclure_vision=True), ServeurDouble(), lire_props=lambda _p: props
    )
    assert controle.statut == "echec" and "projecteur" in controle.detail


def test_verifier_modele_ordre_des_controles(tmp_path: Path) -> None:
    base, _ = preparer_template(tmp_path, TEMPLATE_HF, TEMPLATE_HF)
    shutil.copy(FIXTURES / "config-dense.json", base / "hf" / "config.json")
    controles = verifier_modele(
        "m",
        config_modele(),
        tmp_path / "models",
        fabrique=ServeurDouble(),
        lire_props=lambda _p: PROPS,
    )
    assert [c.controle for c in controles] == list(verifications.CONTROLES)
    assert {c.statut for c in controles} == {"ok"}
    assert {c.modele for c in controles} == {"m"}
    assert controles[-1].valeurs["template_servi_conforme"] is True


def test_template_force_ignore_par_le_serveur() -> None:
    props = {**PROPS, "chat_template": TEMPLATE_AUTRE}  # le serveur sert le template du GGUF
    controle = verifier_serveur(
        "m",
        config_modele(chat_template_force=True),
        ServeurDouble(),
        lire_props=lambda _p: props,
        sha256_hf=sha(TEMPLATE_HF),
        sha256_gguf=sha(TEMPLATE_AUTRE),
    )
    assert controle.statut == "echec"
    assert controle.detail == "template forcé ignoré par llama-server"
    assert controle.valeurs["sha256_template_attendu"] == sha(TEMPLATE_HF)
    assert controle.valeurs["template_servi_conforme"] is False


@pytest.mark.parametrize("force", [True, False])
def test_template_transforme_par_le_serveur_reste_ok(force: bool) -> None:
    props = {**PROPS, "chat_template": "template réécrit par llama.cpp"}
    controle = verifier_serveur(
        "m",
        config_modele(chat_template_force=force),
        ServeurDouble(),
        lire_props=lambda _p: props,
        sha256_hf=sha(TEMPLATE_HF),
        sha256_gguf=sha(TEMPLATE_AUTRE),
    )
    assert controle.statut == "ok"
    servi = sha("template réécrit par llama.cpp")
    assert f"template servi transformé par llama-server (sha {servi})" in controle.detail
    assert controle.valeurs["sha256_template_attendu"] == sha(
        TEMPLATE_HF if force else TEMPLATE_AUTRE
    )
    assert controle.valeurs["template_servi_conforme"] is False


def test_gguf_seul_le_serveur_compare_au_template_du_gguf(tmp_path: Path) -> None:
    gguf_modele(tmp_path / "models" / "m" / "gguf" / GGUF_NOM, TEMPLATE_AUTRE)
    props = {**PROPS, "chat_template": TEMPLATE_AUTRE}
    controles = verifier_modele(
        "m",
        config_modele(fichiers=[]),
        tmp_path / "models",
        fabrique=ServeurDouble(),
        lire_props=lambda _p: props,
    )
    assert controles[3].statut == "sans-objet"
    assert controles[3].valeurs == {"sha256_gguf": sha(TEMPLATE_AUTRE)}
    assert controles[4].statut == "ok"
    assert controles[4].valeurs["template_servi_conforme"] is True


def test_lire_props_sur_un_serveur_http_local() -> None:
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class Gestionnaire(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 (API de http.server)
            corps = json.dumps(PROPS).encode("utf-8")
            self.send_response(200 if self.path == "/props" else 404)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(corps)))
            self.end_headers()
            self.wfile.write(corps)

        def log_message(self, *_args: Any) -> None:
            pass

    serveur = HTTPServer(("127.0.0.1", 0), Gestionnaire)
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    try:
        assert verifications._lire_props(serveur.server_address[1]) == PROPS
    finally:
        serveur.shutdown()
        serveur.server_close()


def test_fabrique_par_defaut_et_chemins_de_serveur_llama(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from slmsp.core.config import dossier_modeles
    from slmsp.inference.serveur import ServeurLlama

    assert verifications._fabrique_par_defaut() is ServeurLlama
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(tmp_path / "models"))
    base, gguf = preparer_template(tmp_path, TEMPLATE_HF, TEMPLATE_AUTRE)
    config = config_modele(chat_template_force=True)
    controles = verifier_modele("m", config, dossier_modeles(), sans_serveur=True)
    serveur = ServeurLlama(config, "cpu", slug="m")  # jamais démarré
    assert controles[3].valeurs["export"] == str(serveur.chat_template)
    assert serveur.chat_template is not None and serveur.chat_template.is_file()
    assert serveur.gguf == dossier_modeles() / "m" / "gguf" / GGUF_NOM
    assert serveur.gguf.resolve() == gguf.resolve()


def test_gguf_en_sous_dossier_meme_chemin_pour_fetch_controles_et_serveur(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Revue lot 3b, P1 : `gguf.fichier` avec un sous-dossier du dépôt."""
    from slmsp.core.config import dossier_modeles
    from slmsp.fetch import modeles
    from slmsp.inference.serveur import ServeurLlama

    monkeypatch.setenv("SLMSP_MODELS_DIR", str(tmp_path / "models"))
    base, gguf = preparer_template(tmp_path, TEMPLATE_HF, TEMPLATE_HF)
    config = config_modele(
        gguf={
            "depot": "org/modele-GGUF",
            "fichier": f"Q4_K_M/{GGUF_NOM}",
            "sha256": "0" * 64,
            "revision": "b" * 40,
            "source": "officielle",
        }
    )
    # Destination de `fetch modeles` (fichier présent : aucune requête).
    destination = modeles._gguf(None, config, base).destination  # type: ignore[arg-type]
    serveur = ServeurLlama(config, "cpu", slug="m")  # jamais démarré
    assert destination == serveur.gguf == dossier_modeles() / "m" / "gguf" / GGUF_NOM
    assert serveur.gguf.resolve() == gguf.resolve()
    controles = verifier_modele("m", config, dossier_modeles(), sans_serveur=True)
    assert controles[3].valeurs["sha256_gguf"] == sha(TEMPLATE_HF)


@pytest.mark.parametrize(
    "contenu",
    [
        {"layer_types": ["full_attention", "couche_inconnue", "full_attention"]},
        {"layer_types": ["attention"] * 2, "text_config": {"layer_types": ["attention", "mamba"]}},
    ],
)
def test_dense_liste_fermee_et_toutes_les_sous_configs(tmp_path: Path, contenu: dict) -> None:
    (dense, _, _) = verifier_config_hf("m", config_modele(), dossier_hf(tmp_path, **contenu))
    assert dense.statut == "echec"
    assert "1 couche(s) sur" in dense.detail and "variante hybride écartée" in dense.detail


GATED_DELTANET = {"layer_types": ["linear_attention"] * 3 + ["full_attention"]}
"""Motif Qwen3.5 (3 couches Gated DeltaNet pour 1 d'attention complète), sous text_config."""


def test_dense_admet_gated_deltanet_non_entrainable(tmp_path: Path) -> None:
    dossier = dossier_hf(tmp_path, text_config=GATED_DELTANET)
    (dense, _, _) = verifier_config_hf("m", config_modele(entrainable=False), dossier)
    assert dense.statut == "ok"
    assert "hybride Gated DeltaNet admis pour l'inférence, non entraînable" in dense.detail
    assert dense.valeurs["layer_types"] == {"linear_attention": 3, "full_attention": 1}
    assert verifications.ecartes([dense]) == {}


def test_dense_gated_deltanet_exige_entrainable_false(tmp_path: Path) -> None:
    dossier = dossier_hf(tmp_path, text_config=GATED_DELTANET)
    (dense, _, _) = verifier_config_hf("m", config_modele(), dossier)
    assert dense.statut == "echec"
    assert "3 couche(s) linear_attention sur 4" in dense.detail
    assert "inscrire entrainable = false" in dense.detail


@pytest.mark.parametrize("intrus", ["mamba", "couche_inconnue"])
def test_dense_hybride_mixte_ecarte_meme_non_entrainable(tmp_path: Path, intrus: str) -> None:
    dossier = dossier_hf(tmp_path, layer_types=["linear_attention", intrus, "full_attention"])
    (dense, _, _) = verifier_config_hf("m", config_modele(entrainable=False), dossier)
    assert dense.statut == "echec"
    assert f"1 ({intrus})" in dense.detail and "linear_attention)" not in dense.detail


def test_mamba_ecarte_meme_non_entrainable(tmp_path: Path) -> None:
    dossier = dossier_hf(tmp_path, "hybride")
    (dense, _, _) = verifier_config_hf("m", config_modele(entrainable=False), dossier)
    assert dense.statut == "echec" and "variante hybride écartée" in dense.detail


@pytest.mark.parametrize(
    ("contenu", "attendu"),
    [
        ({"llm_config": {"layer_types": ["attention", "mamba"]}}, "llm_config.1 (mamba)"),
        (
            {"thinker_config": {"text_config": {"layer_types": ["attention", "mamba"]}}},
            "thinker_config.text_config.1 (mamba)",
        ),
        ({"layers_block_type": ["attention", "mamba"]}, "layers_block_type.1 (mamba)"),
        ({"text_config": {"block_types": ["mamba", "attention"]}}, "block_types.0 (mamba)"),
    ],
)
def test_dense_toutes_sous_configs_et_cles_connues(
    tmp_path: Path, contenu: dict, attendu: str
) -> None:
    """Revue : une couche Mamba hors de `text_config` ou sous une autre clé n'est pas dense."""
    dossier = dossier_hf(tmp_path, **contenu)
    (dense, _, _) = verifier_config_hf("m", config_modele(entrainable=False), dossier)
    assert dense.statut == "echec" and attendu in dense.detail


@pytest.mark.parametrize(
    "contenu",
    [
        {"hybrid_override_pattern": "M-M-M*-"},  # motif Nemotron-H en chaîne
        {"llm_config": {"layer_types": "attention"}},
        {"layer_types": []},
    ],
)
def test_dense_format_inconnu_ecarte_par_prudence(tmp_path: Path, contenu: dict) -> None:
    (dense, _, _) = verifier_config_hf("m", config_modele(), dossier_hf(tmp_path, **contenu))
    assert dense.statut == "echec" and "format non reconnu" in dense.detail


def test_dense_gated_deltanet_sous_llm_config(tmp_path: Path) -> None:
    dossier = dossier_hf(tmp_path, llm_config=GATED_DELTANET, vision_config={"depth": 2})
    assert verifier_config_hf("m", config_modele(), dossier)[0].statut == "echec"
    (dense, _, _) = verifier_config_hf("m", config_modele(entrainable=False), dossier)
    assert dense.statut == "ok" and "llm_config.layer_types" in dense.detail


def test_dense_cles_mamba_hors_types_de_couche_restent_denses(tmp_path: Path) -> None:
    """Granite 4.0 1B (`granitemoehybrid` dense) porte des hyperparamètres `mamba_*`."""
    dossier = dossier_hf(tmp_path, layer_types=["attention"] * 4, mamba_d_state=256)
    (dense, _, _) = verifier_config_hf("m", config_modele(), dossier)
    assert dense.statut == "ok" and dense.detail.startswith("4 couches d'attention")


def test_export_oserror_donne_conflit_sans_part(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    chemin = tmp_path / "m" / "chat_template.jinja"

    def rename(*_args: Any) -> None:
        raise PermissionError("accès refusé")

    monkeypatch.setattr(verifications.os, "rename", rename)
    assert verifications.exporter_template(chemin, TEMPLATE_HF) == "conflit"
    assert not chemin.exists()
    assert not chemin.with_name("chat_template.jinja.part").exists()


def test_export_vers_un_dossier_donne_conflit(tmp_path: Path) -> None:
    chemin = tmp_path / "chat_template.jinja"
    chemin.mkdir()
    assert verifications.exporter_template(chemin, TEMPLATE_HF) == "conflit"
    assert chemin.is_dir()


# --- Configurations versionnées -------------------------------------------------------------


def test_cinq_candidats_dans_l_ordre_d4() -> None:
    assert CANDIDATS == (
        "granite-4.0-1b",
        "ministral-3-3b",
        "smollm3-3b",
        "qwen-4b",
        "ministral-3-8b",
    )


@pytest.mark.parametrize("slug", CANDIDATS)
def test_toml_candidat(slug: str) -> None:
    config = charger_config_modele(slug)
    assert len(config.revision) == 40
    assert set(config.sha256_fichiers) == set(config.fichiers)
    assert config.gguf.revision is not None and config.gguf.source is not None
    assert config.gguf.fichier.endswith("Q4_K_M.gguf")
    assert (config.contexte, config.cache_kv, config.reasoning) == (8192, "f16", "off")
    assert config.protocole_outils in ("natif", "json-generique", "balises-tool-call")
    assert not config.embedding


def test_toml_particularites() -> None:
    granite = charger_config_modele("granite-4.0-1b")
    assert granite.depot_hf == "ibm-granite/granite-4.0-1b" and len(granite.fichiers) == 9
    assert granite.gguf.depot == "ibm-granite/granite-4.0-1b-GGUF"
    assert granite.lm_eval_batch_size == 2  # portable de 6 Go de VRAM, jamais `auto`
    ministral = charger_config_modele("ministral-3-3b")
    assert ministral.depot_hf.endswith("-BF16") and ministral.exclure_vision
    assert len(ministral.fichiers) == 13
    smollm = charger_config_modele("smollm3-3b")
    assert smollm.chat_template_kwargs == {"enable_thinking": False}
    assert smollm.gguf.depot == "ggml-org/SmolLM3-3B-GGUF"
    qwen = charger_config_modele("qwen-4b")
    assert qwen.depot_hf == "Qwen/Qwen3-4B-Instruct-2507"
    assert qwen.gguf.source == "communautaire" and "tokenizer_config.json" in qwen.fichiers
    huit = charger_config_modele("ministral-3-8b")
    assert huit.fichiers == [] and huit.exclure_vision
    assert huit.depot_hf == huit.gguf.depot and huit.gguf.revision == huit.revision


MODELES_OCTOBRE = ("qwen3.5-2b", "bonsai-2-4b", "minicpm-v-4.7-1b")
"""Modèles de base ajoutés le 2026-10-17 (hors CANDIDATS D4)."""


@pytest.mark.parametrize("slug", MODELES_OCTOBRE)
def test_toml_modeles_octobre(slug: str) -> None:
    config = charger_config_modele(slug)
    assert len(config.revision) == 40 and config.gguf.revision is not None
    assert set(config.sha256_fichiers) == set(config.fichiers)
    assert (config.contexte, config.cache_kv, config.reasoning) == (8192, "f16", "off")
    assert config.chat_template_kwargs == {"enable_thinking": False}
    assert config.exclure_vision and not config.embedding
    assert config.entrainable == (slug not in ("bonsai-2-4b", "qwen3.5-2b"))


def test_toml_modeles_octobre_particularites() -> None:
    bonsai = charger_config_modele("bonsai-2-4b")
    assert bonsai.fichiers == [] and bonsai.gguf.fichier.endswith("-Q2_0.gguf")
    assert bonsai.gguf_f16 is None
    qwen = charger_config_modele("qwen3.5-2b")
    assert qwen.gguf.source == "communautaire" and qwen.chat_template_force
    assert qwen.gguf.fichier.endswith("Q4_K_M.gguf") and qwen.gguf_f16 is not None
    minicpm = charger_config_modele("minicpm-v-4.7-1b")
    assert minicpm.gguf.source == "officielle" and minicpm.gguf.fichier.endswith("Q4_K_M.gguf")
    assert minicpm.gguf_f16 is not None and minicpm.gguf_f16.precision == "f16"


MODELES_MOINS_2B = ("eurollm-1.7b", "qwen3.5-0.8b")
"""Candidats de moins de 2B ajoutés le 2026-10-17 (hors CANDIDATS D4)."""


@pytest.mark.parametrize("slug", MODELES_MOINS_2B)
def test_toml_modeles_moins_2b(slug: str) -> None:
    config = charger_config_modele(slug)
    assert len(config.revision) == 40 and config.gguf.revision is not None
    assert set(config.sha256_fichiers) == set(config.fichiers)
    assert (config.cache_kv, config.reasoning) == ("f16", "off")
    assert config.gguf.fichier.lower().endswith("q4_k_m.gguf")
    assert config.gguf.source == "communautaire"
    assert config.exclure_vision == (slug == "qwen3.5-0.8b")
    assert config.entrainable == (slug != "qwen3.5-0.8b") and not config.embedding
    assert config.lm_eval_batch_size == 2


def test_toml_modeles_moins_2b_particularites() -> None:
    euro = charger_config_modele("eurollm-1.7b")
    assert euro.contexte == 4096 and euro.chat_template_force
    assert euro.gguf_f16 is not None and euro.gguf_f16.precision == "f16"
    qwen = charger_config_modele("qwen3.5-0.8b")
    assert qwen.contexte == 8192 and qwen.chat_template_force
    assert qwen.chat_template_kwargs == {"enable_thinking": False}
    assert qwen.gguf_f16 is not None and qwen.gguf_f16.precision == "bf16"


# --- Schéma ---------------------------------------------------------------------------------


def test_schema_tag_conversion() -> None:
    gguf = {"depot": "moi/conv", "fichier": "m.gguf", "sha256": "0" * 64}
    ConfigModele.model_validate(
        {
            **config_modele().model_dump(),
            "gguf": {**gguf, "source": "conversion", "tag_conversion": "b11429"},
        }
    )
    for invalide in ({"source": "conversion"}, {"source": "officielle", "tag_conversion": "b1"}):
        with pytest.raises(ValidationError, match="tag_conversion"):
            ConfigModele.model_validate(
                {**config_modele().model_dump(), "gguf": {**gguf, **invalide}}
            )


def test_schema_sha256_fichiers_inclus_dans_fichiers() -> None:
    with pytest.raises(ValidationError, match="absents de `fichiers`"):
        config_modele(sha256_fichiers={"autre.json": "0" * 64})
    with pytest.raises(ValidationError):
        config_modele(sha256_fichiers={"config.json": "pas un sha"})


def test_schema_revision_gguf_du_meme_depot() -> None:
    gguf = {"depot": "org/modele", "fichier": "m.gguf", "sha256": "0" * 64, "revision": "b" * 40}
    with pytest.raises(ValidationError, match="gguf.revision"):
        config_modele(gguf=gguf)


# --- CLI ------------------------------------------------------------------------------------


def toml_candidat(rev_gguf: str, sha_gguf: str, sha_fichiers: dict[str, str]) -> str:
    lignes = "\n".join(f'"{nom}" = "{valeur}"' for nom, valeur in sha_fichiers.items())
    noms = ", ".join(f'"{nom}"' for nom in sha_fichiers)
    return f"""
schema_version = 1
depot_hf = "org/modele"
revision = "{REV}"
fichiers = [{noms}]
contexte = 4096
protocole_outils = "natif"
chat_template_force = true

[sha256_fichiers]
{lignes}

[gguf]
depot = "org/modele-GGUF"
revision = "{rev_gguf}"
fichier = "{GGUF_NOM}"
sha256 = "{sha_gguf}"
source = "officielle"
"""


def preparer_candidat(cli: Any, slug: str, fixture: str) -> None:
    base = cli.models / slug
    (base / "hf").mkdir(parents=True)
    shutil.copy(FIXTURES / f"config-{fixture}.json", base / "hf" / "config.json")
    (base / "hf" / "chat_template.jinja").write_bytes(TEMPLATE_HF.encode("utf-8"))
    gguf = gguf_modele(base / "gguf" / GGUF_NOM, TEMPLATE_AUTRE)
    shas = {
        nom: hashlib.sha256((base / "hf" / nom).read_bytes()).hexdigest()
        for nom in ("chat_template.jinja", "config.json")
    }
    (cli.config / "modeles" / f"{slug}.toml").write_text(
        toml_candidat("b" * 40, hashlib.sha256(gguf.read_bytes()).hexdigest(), shas),
        encoding="utf-8",
    )


@pytest.mark.parametrize("arguments", [[], ["--candidats", "granite-4.0-1b"]])
def test_cli_usage(cli: Any, capsys: Any, arguments: list[str]) -> None:
    code = main(["fetch", "modeles", *arguments, "--racine", str(cli.racine)])
    assert code == 2
    assert "--candidats" in capsys.readouterr().err
    assert not (cli.racine / "runs").exists()


def test_cli_candidats_de_bout_en_bout(
    banc: Any, outils: Any, cli: Any, capsys: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(verifications, "CANDIDATS", ("dense-a", "hybride-b"))
    preparer_candidat(cli, "dense-a", "dense")
    preparer_candidat(cli, "hybride-b", "hybride")
    double = ServeurDouble()
    monkeypatch.setattr(verifications, "_fabrique_par_defaut", lambda: double)
    monkeypatch.setattr(verifications, "_lire_props", lambda _port: PROPS)

    code = main(["fetch", "modeles", "--candidats", "--racine", str(cli.racine)])

    assert code == 1
    assert banc.serveur.requetes == []  # tout est présent, SHA connus : aucune requête
    run = outils.lire_run(cli.racine)
    assert run.statuts == ["en_cours", "complet"]
    assert run.manifeste["config"]["slugs"] == ["dense-a", "hybride-b"]
    assert run.manifeste["config"]["candidats"] is True
    assert [(f["modele"], f["genre"], f["statut"]) for f in run.fichiers] == [
        ("dense-a", "gguf", "deja-present"),
        ("dense-a", "hf", "deja-present"),
        ("dense-a", "hf", "deja-present"),
        ("hybride-b", "gguf", "deja-present"),
        ("hybride-b", "hf", "deja-present"),
        ("hybride-b", "hf", "deja-present"),
    ]
    assert run.fichiers[0]["revision"] == "b" * 40
    assert [(c["modele"], c["controle"], c["statut"]) for c in run.controles] == [
        ("dense-a", "dense", "ok"),
        ("dense-a", "fp8", "ok"),
        ("dense-a", "vision", "ok"),
        ("dense-a", "chat_template", "ok"),
        ("dense-a", "serveur", "ok"),
        ("hybride-b", "dense", "echec"),
        ("hybride-b", "fp8", "ok"),
        ("hybride-b", "vision", "ok"),
        ("hybride-b", "chat_template", "ok"),
        ("hybride-b", "serveur", "ok"),
    ]
    assert [appel[1:] for appel in double.appels] == [("cpu", "dense-a"), ("cpu", "hybride-b")]
    assert (cli.models / "dense-a" / "chat_template.jinja").read_text(
        encoding="utf-8"
    ) == TEMPLATE_HF
    sortie = capsys.readouterr()
    assert "modèle écarté : hybride-b : dense : 5 couche(s) sur 6 hors attention" in sortie.err
    assert "dense-a" not in sortie.err
    assert "modèle(s) écarté(s) : 1" in sortie.out


def test_cli_sans_serveur(
    banc: Any, outils: Any, cli: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    preparer_candidat(cli, "dense-a", "dense")

    def interdit() -> Any:
        raise AssertionError("aucun serveur avec --sans-serveur")

    monkeypatch.setattr(verifications, "_fabrique_par_defaut", interdit)
    code = main(["fetch", "modeles", "dense-a", "--sans-serveur", "--racine", str(cli.racine)])
    assert code == 0
    run = outils.lire_run(cli.racine)
    assert run.controles[-1]["controle"] == "serveur"
    assert run.controles[-1]["statut"] == "sans-objet"
    assert run.manifeste["config"]["sans_serveur"] is True


# --- Réseau ---------------------------------------------------------------------------------

TAILLES_GGUF = {
    "granite-4.0-1b": 1_023_645_440,
    "ministral-3-3b": 2_147_023_008,
    "smollm3-3b": 1_915_305_312,
    "qwen-4b": 2_497_281_120,
    "ministral-3-8b": 5_198_911_904,
}
"""Tailles des GGUF épinglés (commentaire `[gguf]` des TOML, relevées le 2026-10-12)."""


@pytest.mark.reseau
@pytest.mark.parametrize("slug", CANDIDATS)
def test_candidat_reel_conforme(slug: str) -> None:
    """Réseau : `X-Linked-Etag` et taille du GGUF à `gguf.revision`, et etag d'un fichier
    LFS de `fichiers`, conformes à la configuration (HEAD seulement)."""
    from slmsp.fetch.config import charger_config_fetch
    from slmsp.fetch.hf import Telechargeur, client_hf, jeton_hf, url_hf

    config = charger_config_modele(slug)
    assert config.gguf.revision is not None
    lfs = next((f for f in config.fichiers if f.endswith(".safetensors")), None)
    with client_hf(jeton_hf()) as client:
        telechargeur = Telechargeur(client, charger_config_fetch())
        meta = telechargeur.metadonnees_hf(
            url_hf(config.gguf.depot, config.gguf.fichier, config.gguf.revision)
        )
        assert (meta.taille, meta.sha256) == (TAILLES_GGUF[slug], config.gguf.sha256)
        assert meta.commit == config.gguf.revision
        if lfs is not None:
            meta_lfs = telechargeur.metadonnees_hf(url_hf(config.depot_hf, lfs, config.revision))
            assert meta_lfs.sha256 == config.sha256_fichiers[lfs]
            assert meta_lfs.commit == config.revision


MODELES_OCTOBRE_2 = ("minicpm5-2b", "minicpm5-1b", "gemma-4-e2b")
"""Modèles de base ajoutés le 2026-10-17, seconde campagne (hors CANDIDATS D4)."""


@pytest.mark.parametrize("slug", MODELES_OCTOBRE_2)
def test_toml_modeles_octobre_2(slug: str) -> None:
    config = charger_config_modele(slug)
    assert len(config.revision) == 40 and config.gguf.revision is not None
    assert set(config.sha256_fichiers) == set(config.fichiers)
    assert (config.contexte, config.cache_kv, config.reasoning) == (8192, "f16", "off")
    assert config.chat_template_kwargs == {"enable_thinking": False}
    assert config.gguf.source == "officielle" and config.entrainable
    assert config.exclure_vision == (slug == "gemma-4-e2b")


def test_toml_modeles_octobre_2_particularites() -> None:
    for slug in ("minicpm5-2b", "minicpm5-1b"):
        config = charger_config_modele(slug)
        assert config.gguf.fichier.endswith("-Q4_K_M.gguf")
        assert config.gguf_f16 is not None and config.gguf_f16.precision == "f16"
    assert charger_config_modele("minicpm5-2b").chat_template_force
    gemma = charger_config_modele("gemma-4-e2b")
    assert gemma.gguf.fichier == "gemma-4-E2B_q4_0-it.gguf" and gemma.gguf_f16 is None
