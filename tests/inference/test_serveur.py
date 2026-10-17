"""`ServeurLlama`, binaires, `version`, conversion et quantification.

Les tests unitaires remplacent `llama-server` par `serveur_factice.py` (même protocole
HTTP) et `vendor/` par un dossier factice. Les tests réels (`lent`, `integration`)
lancent les vrais binaires du tag sur Granite 1B et BGE-M3 en CPU.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import psutil
import pytest

from slmsp.core.artefacts import ArtefactExistant
from slmsp.core.config import env_sous_processus
from slmsp.core.erreurs import ConfigurationInvalide, RessourceOccupee
from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.core.var import verrou_gpu
from slmsp.inference import processus, serveur
from slmsp.inference.processus import ErreurInference
from slmsp.inference.serveur import ServeurLlama

PY = sys.executable
FACTICE = Path(__file__).resolve().parent / "serveur_factice.py"
SLUG = "modele-essai"
FICHIER_GGUF = "modele-essai-Q4_K_M.gguf"


def config_modele(**maj: Any) -> ConfigModele:
    base: dict[str, Any] = {
        "depot_hf": "org/modele-essai",
        "revision": "0" * 40,
        "fichiers": [],
        "gguf": {"depot": "org/modele-essai-GGUF", "fichier": FICHIER_GGUF, "sha256": "0" * 64},
        "contexte": 4096,
        "protocole_outils": "natif",
    }
    return ConfigModele.model_validate({**base, **maj})


EMBEDDING = {"embedding": True, "pooling": "cls"}


@pytest.fixture
def modeles(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """`SLMSP_MODELS_DIR` factice avec le GGUF et le chat template du modèle d'essai."""
    dossier = tmp_path / "models"
    (dossier / SLUG / "gguf").mkdir(parents=True)
    (dossier / SLUG / "gguf" / FICHIER_GGUF).write_bytes(b"GGUF factice")
    (dossier / SLUG / "chat_template.jinja").write_text("{{ messages }}", encoding="utf-8")
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(dossier))
    return dossier.resolve()


@pytest.fixture
def lancements(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Espionne `processus.lancer` (arguments, options, processus rendu)."""
    appels: list[dict[str, Any]] = []
    original = processus.lancer

    def espion(arguments: list[str], **options: Any) -> processus.ProcessusGere:
        appel = {"arguments": list(arguments), **options}
        appels.append(appel)
        appel["gere"] = original(arguments, **options)
        return appel["gere"]

    monkeypatch.setattr(processus, "lancer", espion)
    return appels


def _factice(monkeypatch: pytest.MonkeyPatch, *options: str) -> None:
    """Remplace le binaire par le serveur factice (les arguments llama sont ignorés)."""
    monkeypatch.setattr(ServeurLlama, "programme", lambda self: [PY, str(FACTICE), *options])


def _entrees() -> list[dict[str, Any]]:
    return [
        json.loads(chemin.read_text(encoding="utf-8"))
        for chemin in sorted(processus.dossier_pids().glob("*.json"))
    ]


# --- Arguments --------------------------------------------------------------------------------


def test_arguments_generation(vendor_factice, modeles: Path) -> None:
    config = config_modele(
        threads=4,
        cache_kv="q8_0",
        reasoning="off",
        chat_template_kwargs={"enable_thinking": False},
        chat_template_force=True,
    )
    instance = ServeurLlama(config, "cpu", slug=SLUG, config_llamacpp=vendor_factice.config)
    assert instance.arguments(5555) == [
        str((vendor_factice.tag / "bin-cpu" / "llama-server.exe").resolve()),
        "--host",
        "127.0.0.1",
        "--port",
        "5555",
        "-m",
        str(modeles / SLUG / "gguf" / FICHIER_GGUF),
        "-c",
        "4096",
        "-ctk",
        "q8_0",
        "-ctv",
        "q8_0",
        "--parallel",
        "1",
        "--no-webui",
        "-t",
        "4",
        "--jinja",
        "--reasoning",
        "off",
        "--chat-template-kwargs",
        '{"enable_thinking": false}',
        "--chat-template-file",
        str(modeles / SLUG / "chat_template.jinja"),
    ]


def test_arguments_minimaux_et_cuda(vendor_factice, modeles: Path) -> None:
    instance = ServeurLlama(
        config_modele(reasoning="auto"), "cuda", slug=SLUG, config_llamacpp=vendor_factice.config
    )
    arguments = instance.arguments(6000)
    assert arguments[0] == str((vendor_factice.tag / "bin-cuda" / "llama-server.exe").resolve())
    assert arguments[9:16] == ["-ctk", "f16", "-ctv", "f16", "--parallel", "1", "--no-webui"]
    assert arguments[16:] == ["--jinja", "--reasoning", "auto"]
    assert "-t" not in arguments
    assert "--chat-template-kwargs" not in arguments
    assert "--chat-template-file" not in arguments


def test_arguments_embedding(vendor_factice, modeles: Path, tmp_path: Path) -> None:
    gguf = tmp_path / "bge.gguf"
    instance = ServeurLlama(
        config_modele(**EMBEDDING), gguf=gguf, config_llamacpp=vendor_factice.config
    )
    arguments = instance.arguments(7000)
    assert arguments[5:7] == ["-m", str(gguf)]
    assert arguments[-7:] == ["--embedding", "--pooling", "cls", "-b", "4096", "-ub", "4096"]
    assert "--jinja" not in arguments and "--reasoning" not in arguments
    assert instance.role == "embedding"


@pytest.mark.parametrize(
    ("usage", "micro_lot", "attendu"),
    [
        ("passage", {"passage": 1024, "texte_long": 4096}, "1024"),
        ("texte_long", {"passage": 1024, "texte_long": 4096}, "4096"),
        ("texte_long", {"passage": 1024}, "4096"),
    ],
)
def test_arguments_embedding_par_usage(
    vendor_factice, tmp_path: Path, usage: str, micro_lot: dict[str, int], attendu: str
) -> None:
    """`-c`, `-b` et `-ub` suivent le micro-lot de l'usage (absent : le contexte, 4096)."""
    instance = ServeurLlama(
        config_modele(**EMBEDDING, micro_lot=micro_lot),
        gguf=tmp_path / "bge.gguf",
        config_llamacpp=vendor_factice.config,
        usage=usage,  # type: ignore[arg-type]
    )
    arguments = instance.arguments(7000)
    assert arguments[7:9] == ["-c", attendu]
    assert arguments[-4:] == ["-b", attendu, "-ub", attendu]
    instance._port = 7000  # embedder() sans démarrage : la troncature suit le micro-lot
    assert instance.embedder().contexte_max == int(attendu) == instance.micro_lot
    description = instance.description()
    assert (description["usage"], description["micro_lot"]) == (usage, int(attendu))
    assert description["contexte"] == int(attendu)
    instance.embedder().fermer()


def test_micro_lot_generation_refuse(vendor_factice, tmp_path: Path) -> None:
    instance = ServeurLlama(
        config_modele(), gguf=tmp_path / "m.gguf", config_llamacpp=vendor_factice.config
    )
    assert instance.arguments(7000)[7:9] == ["-c", "4096"]
    with pytest.raises(ValueError, match="embedding"):
        _ = instance.micro_lot


@pytest.mark.parametrize(
    ("maj", "message"),
    [
        ({"micro_lot": {"passage": 1024}}, "réservé"),
        ({**EMBEDDING, "micro_lot": {"passage": 8192}}, "hors de"),
        ({**EMBEDDING, "micro_lot": {"passage": 0}}, "hors de"),
        ({**EMBEDDING, "micro_lot": {"inconnu": 1024}}, "micro_lot"),
    ],
)
def test_micro_lot_invalide(maj: dict[str, Any], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        config_modele(**maj)


@pytest.mark.parametrize("slug", ["bge-m3", "bge-m3-f16"])
def test_micro_lot_bge_m3(slug: str) -> None:
    """Le passage tient le plus long chunk service-public (1 163 tokens, 2026-10-17) et
    reste sous le texte long ; `data filter` garde le contexte entier."""
    config = serveur.charger_config_modele(slug)
    assert config.micro_lot_pour("texte_long") == config.contexte
    assert 1163 + 16 <= config.micro_lot_pour("passage") < config.micro_lot_pour("texte_long")


def test_parametres_invalides(vendor_factice) -> None:
    with pytest.raises(ValueError, match="slug ou gguf"):
        ServeurLlama(config_modele())
    with pytest.raises(ValueError, match="chat_template_force"):
        ServeurLlama(config_modele(chat_template_force=True), gguf="m.gguf")
    with pytest.raises(ValueError, match="variante"):
        ServeurLlama(config_modele(), "rocm", gguf="m.gguf")  # type: ignore[arg-type]


# --- Binaires ---------------------------------------------------------------------------------


def test_dossier_vendor_par_defaut(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SLMSP_VENDOR_DIR", raising=False)
    from slmsp.core.config import racine_projet

    assert serveur.dossier_vendor() == (racine_projet() / "vendor").resolve()


def test_binaire_absent(vendor_factice, modeles: Path, lancements: list) -> None:
    (vendor_factice.tag / "bin-cpu" / "llama-server.exe").unlink()
    with pytest.raises(ConfigurationInvalide, match="absent"):
        ServeurLlama(config_modele(), slug=SLUG, config_llamacpp=vendor_factice.config).demarrer()
    assert lancements == []


def test_sha_faux(vendor_factice, modeles: Path, lancements: list) -> None:
    (vendor_factice.tag / "bin-cpu" / "llama-server.exe").write_bytes(b"altere")
    with pytest.raises(ConfigurationInvalide, match="SHA-256"):
        ServeurLlama(config_modele(), slug=SLUG, config_llamacpp=vendor_factice.config).demarrer()
    assert lancements == []


def test_sha_faux_dll_de_la_variante(vendor_factice, modeles: Path, lancements: list) -> None:
    assert "bin-cuda/ggml-cuda.dll" in vendor_factice.config.binaires
    (vendor_factice.tag / "bin-cuda" / "ggml-cuda.dll").write_bytes(b"altere")
    with pytest.raises(ConfigurationInvalide, match="(?s)ggml-cuda.dll.*SHA-256"):
        ServeurLlama(
            config_modele(), "cuda", slug=SLUG, config_llamacpp=vendor_factice.config
        ).demarrer()
    with pytest.raises(ConfigurationInvalide, match="ggml-cuda.dll"):
        serveur.binaire("llama-server", "cuda", config=vendor_factice.config)
    serveur.binaire("llama-server", "cpu", config=vendor_factice.config)  # autre variante
    assert lancements == []


def test_sha_verifie_une_fois(vendor_factice, monkeypatch: pytest.MonkeyPatch) -> None:
    calculs: list[Path] = []
    original = serveur.sha256_fichier
    monkeypatch.setattr(serveur, "sha256_fichier", lambda c: calculs.append(c) or original(c))
    for _ in range(3):
        serveur.binaire("llama-server", "cpu", config=vendor_factice.config)
    # Chaque fichier listé de bin-cpu/ (llama-server, llama-quantize) : une seule fois.
    assert sorted(c.name for c in calculs) == ["llama-quantize.exe", "llama-server.exe"]


def test_gguf_absent(vendor_factice, modeles: Path, lancements: list) -> None:
    (modeles / SLUG / "gguf" / FICHIER_GGUF).unlink()
    with pytest.raises(ConfigurationInvalide, match="GGUF absent"):
        ServeurLlama(config_modele(), slug=SLUG, config_llamacpp=vendor_factice.config).demarrer()
    assert lancements == []


# --- Cycle de vie avec le serveur factice ------------------------------------------------------


def test_demarrer_generer_arreter(
    vendor_factice, modeles: Path, lancements: list, monkeypatch: pytest.MonkeyPatch
) -> None:
    _factice(monkeypatch)
    with ServeurLlama(config_modele(), slug=SLUG, config_llamacpp=vendor_factice.config) as s:
        (appel,) = lancements
        assert appel["env"] == env_sous_processus()
        assert appel["role"] == "generation" and appel["port"] == s.port
        assert appel["arguments"][:2] == [PY, str(FACTICE)]
        assert appel["arguments"][2:6] == ["--host", "127.0.0.1", "--port", str(s.port)]
        (entree,) = _entrees()
        assert entree["pid"] == s.pid and entree["port"] == s.port
        evenements = list(s.client().generer([{"role": "user", "content": "<factice>"}]))
        assert s.client().taille_contexte == s.config.contexte == 4096
        assert evenements[:2] == [Jeton(texte="Bon"), Jeton(texte="jour")]
        assert isinstance(evenements[-1], Fin)
        description = s.description()
        assert description["variante"] == "cpu"
        assert description["tag_llamacpp"] == vendor_factice.config.tag
        assert description["gguf"] == FICHIER_GGUF
        assert description["arguments"][:2] == ["--host", "127.0.0.1"]
        with pytest.raises(ValueError):
            s.embedder()
        gere = appel["gere"]
    assert not gere.vivant
    assert _entrees() == []
    with pytest.raises(ErreurInference):
        _ = s.port


def test_demarrage_rate_processus_mort(
    vendor_factice, modeles: Path, lancements: list, monkeypatch: pytest.MonkeyPatch
) -> None:
    _factice(monkeypatch, "--mourir")
    instance = ServeurLlama(config_modele(), slug=SLUG, config_llamacpp=vendor_factice.config)
    with pytest.raises(ErreurInference, match="(?s)mort au démarrage.*mort volontaire"):
        instance.demarrer()
    assert _entrees() == []
    assert not instance.demarre
    # Le journal reste désigné après l'échec : c'est là qu'il sert (revue lot 3b, P2).
    assert instance.journal is not None
    assert "mort volontaire" in instance.journal.read_text(encoding="utf-8")


def test_demarrage_rate_sante(
    vendor_factice, modeles: Path, lancements: list, monkeypatch: pytest.MonkeyPatch
) -> None:
    _factice(monkeypatch, "--sante", "503")
    instance = ServeurLlama(
        # 5 s : sous la charge de la suite complète, le factice met parfois plus de 2 s à
        # écrire « écoute sur » dans le journal.
        config_modele(),
        slug=SLUG,
        config_llamacpp=vendor_factice.config,
        delai_demarrage=5,
    )
    debut = time.monotonic()
    with pytest.raises(ErreurInference, match="(?s)pas prêt.*écoute sur"):
        instance.demarrer()
    assert time.monotonic() - debut < 30
    assert not lancements[0]["gere"].vivant
    assert _entrees() == []
    assert instance.journal is not None and instance.journal.is_file()


def test_deux_instances(
    vendor_factice, modeles: Path, lancements: list, monkeypatch: pytest.MonkeyPatch
) -> None:
    _factice(monkeypatch)
    config = vendor_factice.config
    with (
        ServeurLlama(config_modele(), slug=SLUG, config_llamacpp=config) as generation,
        ServeurLlama(config_modele(**EMBEDDING), slug=SLUG, config_llamacpp=config) as embedding,
    ):
        assert generation.port != embedding.port
        entrees = _entrees()
        assert sorted(e["role"] for e in entrees) == ["embedding", "generation"]
        assert {e["port"] for e in entrees} == {generation.port, embedding.port}
        matrice = embedding.embedder().vectoriser(["a"])
        assert matrice.shape == (1, 1024)
        with pytest.raises(ValueError):
            embedding.client()
    assert _entrees() == []


def test_cuda_tient_le_verrou_gpu(
    vendor_factice, modeles: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _factice(monkeypatch)
    with ServeurLlama(config_modele(), "cuda", slug=SLUG, config_llamacpp=vendor_factice.config):
        with pytest.raises(RessourceOccupee):
            with verrou_gpu():
                pass
    with verrou_gpu():
        pass


def test_demarrer_nettoie_les_orphelins(
    vendor_factice, modeles: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mort = subprocess.Popen([PY, "-c", "pass"], creationflags=processus.CREATE_NO_WINDOW)
    creation = psutil.Process(mort.pid).create_time()
    mort.wait(60)
    perimee = processus.EntreePid(
        pid=mort.pid,
        port=1,
        role="generation",
        parent_pid=mort.pid,
        parent_creation=creation,
        creation=creation,
    )
    chemin = processus.inscrire(perimee)
    _factice(monkeypatch)
    with ServeurLlama(config_modele(), slug=SLUG, config_llamacpp=vendor_factice.config):
        assert not chemin.exists()
    lignes = (processus.dossier_pids() / processus.NOM_NETTOYAGE).read_text(encoding="utf-8")
    actions = [json.loads(ligne) for ligne in lignes.splitlines()]
    assert [(a["action"], a["entree"]["pid"]) for a in actions] == [("disparu", mort.pid)]


def test_cuda_demarrage_rate_rend_le_verrou(
    vendor_factice, modeles: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _factice(monkeypatch, "--mourir")
    with pytest.raises(ErreurInference):
        ServeurLlama(
            config_modele(), "cuda", slug=SLUG, config_llamacpp=vendor_factice.config
        ).demarrer()
    with verrou_gpu():
        pass


def test_cuda_verrou_deja_tenu_par_l_appelant(
    vendor_factice, modeles: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _factice(monkeypatch)
    with verrou_gpu():
        with pytest.raises(RessourceOccupee):
            ServeurLlama(
                config_modele(), "cuda", slug=SLUG, config_llamacpp=vendor_factice.config
            ).demarrer()
        with ServeurLlama(
            config_modele(),
            "cuda",
            slug=SLUG,
            config_llamacpp=vendor_factice.config,
            prendre_verrou_gpu=False,
        ) as instance:
            assert instance.demarre
    assert _entrees() == []


# --- version, conversion, quantification ----------------------------------------------------


def test_version(vendor_factice, monkeypatch: pytest.MonkeyPatch) -> None:
    appels: list[list[str]] = []

    def executer(arguments, **options):
        appels.append([str(a) for a in arguments])
        return 0, "version: 0.6.0-dev (build 11429, commit d81235049)\nbuilt with MSVC\n"

    monkeypatch.setattr(processus, "executer", executer)
    assert serveur.version("cuda", config=vendor_factice.config) == "b11429"
    assert appels == [
        [str((vendor_factice.tag / "bin-cuda" / "llama-server.exe").resolve()), "--version"]
    ]
    monkeypatch.setattr(processus, "executer", lambda arguments, **options: (1, "illisible"))
    with pytest.raises(ErreurInference, match="build"):
        serveur.version("cpu", config=vendor_factice.config)


def test_commande_conversion(
    vendor_factice, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FAUX_API_KEY", "secret")
    monkeypatch.setenv("PYTHONPATH", "ancien")
    tag = vendor_factice.tag.resolve()
    commande = serveur.commande_conversion(
        tmp_path / "hf", tmp_path / "sortie.gguf", config=vendor_factice.config
    )
    assert commande.arguments == [
        PY,
        str(tag / "src" / "convert_hf_to_gguf.py"),
        str(tmp_path / "hf"),
        "--outfile",
        str(tmp_path / "sortie.gguf"),
        "--outtype",
        "bf16",
    ]
    attendu = env_sous_processus()
    assert "FAUX_API_KEY" not in commande.env
    assert commande.env.pop("PYTHONPATH") == f"{tag / 'src' / 'gguf-py'}{os.pathsep}ancien"
    attendu.pop("PYTHONPATH")
    assert commande.env == attendu


def test_commande_quantification(vendor_factice, tmp_path: Path) -> None:
    commande = serveur.commande_quantification(
        tmp_path / "e.gguf", tmp_path / "s.gguf", "Q4_K_M", config=vendor_factice.config
    )
    assert commande.arguments == [
        str((vendor_factice.tag / "bin-cpu" / "llama-quantize.exe").resolve()),
        str(tmp_path / "e.gguf"),
        str(tmp_path / "s.gguf"),
        "Q4_K_M",
    ]
    assert commande.env == env_sous_processus()


def test_quantifier(vendor_factice, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    appels: list[list[str]] = []

    def executer(arguments, **options):
        appels.append(list(arguments))
        assert options["env"] == env_sous_processus()
        Path(arguments[2]).write_bytes(b"quantifie")
        return 0, ""

    monkeypatch.setattr(processus, "executer", executer)
    sortie = tmp_path / "s.gguf"
    resultat = serveur.quantifier(
        tmp_path / "e.gguf", sortie, "Q4_K_M", config=vendor_factice.config
    )
    assert resultat == sortie and sortie.read_bytes() == b"quantifie"
    assert appels[0][2] == str(tmp_path / "s.gguf.part")
    assert not (tmp_path / "s.gguf.part").exists()

    with pytest.raises(ArtefactExistant):
        serveur.quantifier(tmp_path / "e.gguf", sortie, "Q4_K_M", config=vendor_factice.config)
    assert len(appels) == 1


def test_quantifier_echec(vendor_factice, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(processus, "executer", lambda arguments, **options: (1, "panne"))
    sortie = tmp_path / "s.gguf"
    with pytest.raises(ErreurInference, match="(?s)llama-quantize.*panne"):
        serveur.quantifier(tmp_path / "e.gguf", sortie, "Q4_K_M", config=vendor_factice.config)
    assert not sortie.exists()


def test_convertir(vendor_factice, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    appels: list[list[str]] = []

    def executer(arguments, **options):
        appels.append(list(arguments))
        Path(arguments[arguments.index("--outfile") + 1]).write_bytes(b"gguf")
        return 0, ""

    monkeypatch.setattr(processus, "executer", executer)
    sortie = tmp_path / "m.gguf"
    (tmp_path / "m.gguf.part").write_bytes(b"reste")
    with pytest.raises(ArtefactExistant):
        serveur.convertir_hf_vers_gguf(tmp_path / "hf", sortie, config=vendor_factice.config)
    assert appels == []
    (tmp_path / "m.gguf.part").unlink()
    serveur.convertir_hf_vers_gguf(tmp_path / "hf", sortie, config=vendor_factice.config)
    assert sortie.read_bytes() == b"gguf"
    with pytest.raises(ArtefactExistant):
        serveur.convertir_hf_vers_gguf(tmp_path / "hf", sortie, config=vendor_factice.config)
    assert len(appels) == 1


# --- Tests réels -------------------------------------------------------------------------------

GRANITE = "granite-4.0-1b"


def config_granite(**maj: Any) -> ConfigModele:
    return config_modele(
        depot_hf="ibm-granite/granite-4.0-1b",
        gguf={"depot": "local", "fichier": "granite-4.0-1b-Q4_K_M.gguf", "sha256": "0" * 64},
        contexte=4096,
        **maj,
    )


@pytest.mark.lent
@pytest.mark.integration
@pytest.mark.parametrize("variante", ["cpu", "cuda"])
def test_reel_version(vendor_reel: Path, variante: str) -> None:
    assert serveur.version(variante) == serveur.charger_config_llamacpp().tag == "b11429"


@pytest.mark.lent
@pytest.mark.integration
def test_reel_generation_granite(vendor_reel: Path, modeles_reels: Path) -> None:
    messages = [{"role": "user", "content": "Écris une phrase sur la mer."}]
    debut = time.perf_counter()
    with ServeurLlama(config_granite(), "cpu", slug=GRANITE) as instance:
        pret = time.perf_counter() - debut
        client = instance.client()
        compte = client.compter_tokens(messages)
        debut = time.perf_counter()
        evenements = list(
            client.generer(messages, options={"temperature": 0, "seed": 42, "max_tokens": 32})
        )
        duree = time.perf_counter() - debut
    jetons = [e for e in evenements if isinstance(e, Jeton)]
    fin = evenements[-1]
    assert jetons and isinstance(fin, Fin) and fin.raison in ("terminee", "longueur")
    assert fin.usage is not None
    assert {"prompt_tokens", "completion_tokens", "total_tokens", "delai_premier_token_ms"} <= set(
        fin.usage
    )
    assert compte == fin.usage["prompt_tokens"]
    generation = duree - fin.usage["delai_premier_token_ms"] / 1000
    debit = fin.usage["completion_tokens"] / generation if generation > 0 else float("inf")
    print(
        f"\nGranite 1B CPU : prêt en {pret:.1f} s, premier token "
        f"{fin.usage['delai_premier_token_ms']} ms, {fin.usage['completion_tokens']} tokens, "
        f"débit {debit:.1f} tokens/s : {''.join(j.texte for j in jetons)!r}"
    )


@pytest.mark.lent
@pytest.mark.integration
def test_reel_json_generique_granite(vendor_reel: Path, modeles_reels: Path) -> None:
    outils = [
        {
            "type": "function",
            "function": {
                "name": "meteo",
                "parameters": {
                    "type": "object",
                    "properties": {"ville": {"type": "string"}},
                    "required": ["ville"],
                },
            },
        }
    ]
    messages = [
        {
            "role": "system",
            "content": 'Outil disponible : meteo(ville). Réponds en JSON : {"tool_calls": '
            '[{"name": ..., "arguments": {...}}]} ou {"content": ...}.',
        },
        {"role": "user", "content": "Quel temps fait-il à Lyon ?"},
    ]
    config = config_granite(protocole_outils="json-generique")
    with ServeurLlama(config, "cpu", slug=GRANITE) as instance:
        evenements = list(
            instance.client().generer(
                messages, tools=outils, options={"temperature": 0, "seed": 42, "max_tokens": 64}
            )
        )
    sorties = evenements[:-1]
    print(f"\nGranite 1B json-generique : {sorties}")
    assert sorties
    assert all(isinstance(e, AppelOutil | Jeton | AppelNonConforme) for e in sorties)


@pytest.mark.lent
@pytest.mark.integration
def test_reel_embedding_bge(vendor_reel: Path, modeles_reels: Path) -> None:
    config = serveur.charger_config_modele("bge-m3")
    with ServeurLlama(config, "cpu", slug="bge-m3") as instance:
        embedder = instance.embedder()
        matrice = embedder.vectoriser(["Bonjour", "Impôt sur le revenu", "Bonjour"])
        # Bien au-delà du micro-lot par défaut de 512 tokens (environ 2 000 tokens).
        long = embedder.vectoriser([" ".join(f"mot{i} administration" for i in range(600))])
    assert long.shape == (1, 1024)
    np.testing.assert_allclose(np.linalg.norm(long, axis=1), 1.0, rtol=1e-5)
    assert matrice.shape == (3, 1024) and matrice.dtype == np.float32
    np.testing.assert_allclose(np.linalg.norm(matrice, axis=1), 1.0, rtol=1e-5)
    np.testing.assert_allclose(matrice[0], matrice[2], atol=1e-5)
    assert float(matrice[0] @ matrice[1]) < 0.99


@pytest.mark.lent
@pytest.mark.integration
def test_reel_deux_instances(vendor_reel: Path, modeles_reels: Path) -> None:
    with (
        ServeurLlama(config_granite(), "cpu", slug=GRANITE) as generation,
        ServeurLlama(serveur.charger_config_modele("bge-m3"), "cpu", slug="bge-m3") as embedding,
    ):
        assert generation.port != embedding.port
        entrees = _entrees()
        assert sorted(e["role"] for e in entrees) == ["embedding", "generation"]
        assert {e["pid"] for e in entrees} == {generation.pid, embedding.pid}
    assert _entrees() == []


# --- Version de llama.cpp par modèle (décision d'Anaël du 2026-10-17, Bonsai) ---------------


def test_version_llamacpp_par_modele() -> None:
    """Bonsai a sa version réservée ; tous les autres modèles gardent la version commune."""
    commune = serveur.charger_config_llamacpp()
    assert commune.tag == "b11429"
    dossier = Path(__file__).parents[2] / "config" / "modeles"
    reservees = {}
    for fichier in sorted(dossier.glob("*.toml")):
        config = serveur.charger_config_modele(fichier.stem)
        tag = serveur.config_llamacpp_modele(config).tag
        if config.llamacpp is None:
            assert tag == commune.tag, fichier.stem
        else:
            reservees[fichier.stem] = tag
    assert reservees == {"bonsai-2-4b": "prism-b10777-e3de715"}


def test_version_llamacpp_absente_refusee() -> None:
    with pytest.raises(ConfigurationInvalide):
        serveur.config_llamacpp_modele(config_modele(llamacpp="b1"))


def test_champ_llamacpp_valide() -> None:
    assert config_modele().llamacpp is None
    assert config_modele(llamacpp="prism-b10777-e3de715").llamacpp == "prism-b10777-e3de715"
    with pytest.raises(ValueError):
        config_modele(llamacpp="../b11429")


def test_serveur_version_reservee_par_defaut(modeles: Path) -> None:
    """Sans `config_llamacpp` explicite, le serveur prend la version du modèle, consignée
    dans sa description (`tag_llamacpp` de run.json)."""
    s = ServeurLlama(config_modele(llamacpp="prism-b10777-e3de715"), slug=SLUG)
    assert s.config_llamacpp.tag == "prism-b10777-e3de715"
    assert s.description()["tag_llamacpp"] == "prism-b10777-e3de715"
    defaut = ServeurLlama(config_modele(), slug=SLUG)
    assert defaut.description()["tag_llamacpp"] == serveur.charger_config_llamacpp().tag


def test_serveur_version_explicite_incoherente(modeles: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="exige llama.cpp"):
        ServeurLlama(
            config_modele(llamacpp="prism-b10777-e3de715"),
            slug=SLUG,
            config_llamacpp=serveur.charger_config_llamacpp(),
        )


def test_binaire_version_reservee(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Les binaires d'une version réservée sont cherchés sous `vendor/llama.cpp/<tag>/`."""
    config = serveur.charger_config_llamacpp("prism-b10777-e3de715")
    monkeypatch.setenv("SLMSP_VENDOR_DIR", str(tmp_path))
    assert serveur.dossier_llamacpp(config) == (tmp_path / "llama.cpp" / config.tag).resolve()
    with pytest.raises(ConfigurationInvalide, match="prism-b10777-e3de715"):
        serveur.binaire("llama-server", "cpu", config=config)
