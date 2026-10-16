"""Tests de l'empaquetage PyInstaller (story 12.12) : plan de données, exclusions, mode gelé.

Aucun build réel : les ressources lourdes sont des fichiers factices dans `tmp_path`.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

from slmsp.core.canonique import sha256_fichier
from slmsp.core.config import dossier_modeles, racine_ecriture, racine_projet
from slmsp.index.config import dossier_index
from slmsp.inference.serveur import (
    charger_config_llamacpp,
    charger_config_modele,
    dossier_llamacpp,
    dossier_vendor,
)

DEPOT = Path(__file__).resolve().parents[2]


def _charger_script():
    chemin = DEPOT / "outils" / "construire_application.py"
    spec = importlib.util.spec_from_file_location("construire_application", chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules["construire_application"] = module
    spec.loader.exec_module(module)
    return module


CA = _charger_script()


@pytest.fixture
def ressources_factices(tmp_path: Path) -> dict[str, Path]:
    """Dépôt, vendor, models et index factices (octets quelconques, pas de vrai modèle)."""
    slug = "granite-4.0-1b"
    tag = charger_config_llamacpp().tag
    vendor = tmp_path / "vendor"
    bin_cpu = vendor / "llama.cpp" / tag / "bin-cpu"
    bin_cpu.mkdir(parents=True)
    for nom in (
        "llama-server.exe",
        "llama-cli.exe",
        "ggml.dll",
        "llama-server-impl.dll",
        "llama-bench-impl.dll",
    ):
        (bin_cpu / nom).write_bytes(b"<factice>")
    modeles = tmp_path / "models"
    for s in (slug, "bge-m3"):
        gguf = charger_config_modele(s).gguf
        cible = modeles / s / "gguf" / Path(gguf.fichier).name
        cible.parent.mkdir(parents=True)
        cible.write_bytes(b"<gguf-factice-" + s.encode() + b">")
    index = tmp_path / "index" / "20260926"
    index.mkdir(parents=True)
    (index / "a.bin").write_bytes(b"<a>")
    (index / "MANIFEST.json").write_text(
        json.dumps({"fichiers": {"a.bin": sha256_fichier(index / "a.bin")}}), encoding="utf-8"
    )
    # Copie réduite du dépôt : config (avec dossiers exclus), interface, ressources.
    racine = tmp_path / "depot"
    for rel in (
        "config/application.toml",
        "config/benchmarks/x.toml",
        "config/runs/x.toml",
        "config/prompts/generateur/g.md",
        "config/prompts/taches/Q.md",
        "src/slmsp/app/ui/index.html",
        "src/slmsp/app/ui/js/socle/app.js",
        "src/slmsp/app/ui/js/socle/pont-factice.js",
        "src/slmsp/app/ressources/licences-tierces.json",
        "src/slmsp/app/ressources/prenoms.txt",
        "src/slmsp/app/ressources/empreinte-application.txt",
    ):
        f = racine / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("<factice>", encoding="utf-8")
    return {"racine": racine, "vendor": vendor, "modeles": modeles, "index": tmp_path / "index"}


def _plan(r: dict[str, Path], **kw):
    return CA.construire_plan(
        r["racine"], vendor=r["vendor"], modeles=r["modeles"], index=r["index"], **kw
    )


def test_plan_exclusions(ressources_factices) -> None:
    plan = _plan(ressources_factices)
    destinations = {f.destination for f in plan.fichiers}
    assert not any(d.endswith("pont-factice.js") for d in destinations)
    assert "slmsp/app/ui/js/socle/app.js" in destinations
    assert "slmsp/app/ui/index.html" in destinations
    assert not any(d.startswith(("config/benchmarks", "config/runs")) for d in destinations)
    assert not any("generateur" in d for d in destinations)
    assert "config/prompts/taches/Q.md" in destinations
    assert not any(d.endswith(".env") for d in destinations)
    # Un seul exécutable llama.cpp, et pas les DLL des autres outils.
    exe = [d for d in destinations if d.endswith(".exe")]
    assert [Path(d).name for d in exe] == ["llama-server.exe"]
    assert any("bench-impl" in d for d in destinations)  # toutes les DLL de bin-cpu sont gardées
    assert not any(d.endswith("llama-cli.exe") for d in destinations)
    assert any(d.endswith("llama-server-impl.dll") for d in destinations)
    # L'empreinte est produite au build, jamais embarquée depuis les sources.
    assert not any(d.endswith("empreinte-application.txt") for d in destinations)


def test_plan_complet_et_donnees_pyinstaller(ressources_factices) -> None:
    plan = _plan(ressources_factices)
    tag = plan.tag
    destinations = {f.destination for f in plan.fichiers}
    assert f"vendor/llama.cpp/{tag}/bin-cpu/llama-server.exe" in destinations
    assert any(d.startswith("models/granite-4.0-1b/gguf/") for d in destinations)
    assert any(d.startswith("models/bge-m3/gguf/") for d in destinations)
    assert "index/20260926/MANIFEST.json" in destinations
    assert plan.index_version == "20260926"
    # `datas` : (fichier, dossier de destination), jamais le fichier lui-même.
    for source, dossier in plan.donnees():
        assert Path(source).is_file()
        assert not dossier.endswith((".json", ".gguf", ".exe"))


def test_plan_sans_modele(ressources_factices) -> None:
    plan = _plan(ressources_factices, sans_modele=True)
    destinations = {f.destination for f in plan.fichiers}
    assert plan.index_version is None
    assert not any(d.startswith(("models/", "index/")) for d in destinations)
    assert any("llama-server.exe" in d for d in destinations)


def test_ressource_manquante_echoue_avant_pyinstaller(ressources_factices) -> None:
    r = ressources_factices
    gguf = next((r["modeles"] / "bge-m3" / "gguf").iterdir())
    gguf.unlink()
    with pytest.raises(CA.ErreurBuild, match="ressource manquante"):
        _plan(r)


def test_empreinte_fausse_echoue(ressources_factices) -> None:
    plan = _plan(ressources_factices)
    with pytest.raises(CA.ErreurBuild, match="empreinte fausse"):
        CA.verifier_empreintes(plan)  # les GGUF factices ne portent pas le SHA-256 épinglé


def test_empreintes_correctes_passent(ressources_factices) -> None:
    plan = _plan(ressources_factices, sans_modele=True)
    for f in plan.fichiers:
        object.__setattr__(f, "sha256_attendu", None)
    CA.verifier_empreintes(plan)
    llama = next(f for f in plan.fichiers if f.source.name == "llama-server.exe")
    object.__setattr__(llama, "sha256_attendu", sha256_fichier(llama.source))
    CA.verifier_empreintes(plan)


def test_index_empreinte_fausse(ressources_factices) -> None:
    r = ressources_factices
    (r["index"] / "20260926" / "a.bin").write_bytes(b"<modifie>")
    plan = _plan(r)
    index = [f for f in plan.fichiers if f.composant.startswith("index:") and f.sha256_attendu]
    assert index
    with pytest.raises(CA.ErreurBuild, match="empreinte fausse"):
        CA.verifier_empreintes(CA.Plan(fichiers=index))


def test_taille_limite_detail_par_composant() -> None:
    assert CA.verifier_taille({"a": 1, "b": 2}) == 3
    with pytest.raises(CA.ErreurBuild) as info:
        CA.verifier_taille({"modele:x": 3_000_000_000, "index:1": 2_000_000_000, "petit": 1})
    message = str(info.value)
    assert "NFR-6" in message
    assert message.index("modele:x") < message.index("index:1")


def test_fermeture_runtime(tmp_path: Path) -> None:
    interne = tmp_path / "_internal"
    for nom in ("numpy", "pydantic", "torch", "anthropic-1.0.dist-info", "huggingface_hub"):
        (interne / nom).mkdir(parents=True)
    assert CA.fermeture_runtime(tmp_path) == ["huggingface_hub", "torch"]
    (interne / "torch").rmdir()
    (interne / "huggingface_hub").rmdir()
    assert CA.fermeture_runtime(tmp_path) == []


def test_empreinte_application(tmp_path: Path) -> None:
    exe = tmp_path / "AssistantSP.exe"
    exe.write_bytes(b"<exe-factice>")
    empreinte = CA.ecrire_empreinte(tmp_path, exe)
    fichier = tmp_path / "_internal" / "slmsp" / "app" / "ressources" / "empreinte-application.txt"
    assert fichier.read_text(encoding="utf-8").strip() == empreinte == sha256_fichier(exe)
    assert len(empreinte) == 64


def test_manifeste(ressources_factices, tmp_path: Path) -> None:
    plan = _plan(ressources_factices, sans_modele=True)
    manifeste = CA.ecrire_manifeste(tmp_path / "m.json", plan, total=10, runtime=5, empreinte="e")
    lu = json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))
    assert lu == manifeste
    assert lu["limite_octets"] == 4_000_000_000
    assert lu["composants"]["llama.cpp"] > 0
    assert lu["sans_modele"] is True


def test_licences_generees(tmp_path: Path) -> None:
    base = tmp_path / "base.json"
    base.write_text(
        json.dumps(
            {
                "statut": "provisoire",
                "composants": [
                    {"nom": "llama.cpp", "licence": "à vérifier", "source": None},
                    {"nom": "Granite", "licence": "à vérifier", "source": None},
                ],
            }
        ),
        encoding="utf-8",
    )
    tag = tmp_path / "tag"
    (tag / "src").mkdir(parents=True)
    (tag / "src" / "LICENSE").write_text("MIT License\n\nCopyright", encoding="utf-8")
    sortie = tmp_path / "out" / "licences-tierces.json"
    a_verifier = CA.generer_licences(base, tag, sortie)
    brut = json.loads(sortie.read_text(encoding="utf-8"))
    assert a_verifier == ["Granite"]
    assert brut["composants"][0]["licence"] == "MIT"
    assert brut["statut"] == "provisoire"


def test_spec_statique() -> None:
    spec = (DEPOT / "packaging" / "assistantsp.spec").read_text(encoding="utf-8")
    assert "COLLECT(" in spec
    assert "exclude_binaries=True" in spec  # onedir
    code = "".join(x for x in spec.splitlines(True) if not x.lstrip().startswith("#"))
    assert "onefile" not in code.lower()
    assert "a.binaries" in code and "a.zipfiles" not in code
    assert "EXCLUSIONS" in spec
    assert "SLMSP_PLAN_BUILD" in spec
    for lourd in ("torch", "transformers", "anthropic", "mistralai", "huggingface_hub"):
        assert lourd in CA.EXCLUSIONS
    for requis in ("numpy", "pydantic", "webview", "httpx"):
        assert requis not in CA.EXCLUSIONS
    lanceur = (DEPOT / "packaging" / "lanceur.py").read_text(encoding="utf-8")
    assert "slmsp.app.principal" in lanceur


def test_interface_reelle_sans_pont_factice() -> None:
    """L'interface réelle est embarquée en entier, sauf le pont factice (reports 12.4 et 12.6)."""
    ui = DEPOT / "src/slmsp/app/ui"
    assert (ui / "js/socle/pont-factice.js").is_file()
    fichiers = CA._fichiers_sous(
        ui, "slmsp/app/ui", "interface", garder=lambda p: p.name != CA.FICHIER_EXCLU
    )
    destinations = {f.destination for f in fichiers}
    assert "slmsp/app/ui/index.html" in destinations
    assert not any(d.endswith("pont-factice.js") for d in destinations)
    assert len(destinations) == sum(1 for p in ui.rglob("*") if p.is_file()) - 1


# --- Mode gelé (simulé) ---------------------------------------------------------------------


@pytest.fixture
def gele(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    meipass = tmp_path / "install" / "_internal"
    meipass.mkdir(parents=True)
    shutil.copytree(DEPOT / "config", meipass / "config", ignore=shutil.ignore_patterns("runs"))
    for var in ("SLMSP_RACINE", "SLMSP_VENDOR_DIR", "SLMSP_MODELS_DIR"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(meipass), raising=False)
    return meipass.resolve()


def test_chemins_geles_coherents_avec_le_plan(gele: Path, ressources_factices) -> None:
    """Chaque destination du plan se retrouve là où l'application la cherche une fois gelée."""
    plan = _plan(ressources_factices)
    assert racine_projet() == gele
    assert dossier_vendor() == gele / "vendor"
    assert dossier_llamacpp() == gele / "vendor" / "llama.cpp" / plan.tag
    assert dossier_modeles() == gele / "models"
    assert dossier_index() == gele / "index"
    destinations = {f.destination for f in plan.fichiers}
    assert f"vendor/llama.cpp/{plan.tag}/bin-cpu/llama-server.exe" in destinations
    gguf = charger_config_modele(plan.slug).gguf
    assert f"models/{plan.slug}/gguf/{Path(gguf.fichier).name}" in destinations
    assert (
        f"index/{plan.index_version}/MANIFEST.json" in destinations
        and (dossier_index() / plan.index_version).parent == gele / "index"
    )


def test_ecritures_hors_installation(gele: Path, tmp_path: Path) -> None:
    """`racine_ecriture` pointe vers les données, jamais sous `_MEIPASS` ni l'installation."""
    ecriture = racine_ecriture()
    assert ecriture == (tmp_path / "local" / "AssistantSP").resolve()
    assert gele not in ecriture.parents
    assert gele.parent not in ecriture.parents


def test_interface_et_ressources_sous_le_paquet() -> None:
    """Les destinations `slmsp/app/...` correspondent à `Path(__file__)` du paquet gelé."""
    from slmsp.app import principal
    from slmsp.app.pont import reglages

    src = DEPOT / "src"
    assert principal.dossier_interface().relative_to(src).as_posix() == "slmsp/app/ui"
    assert reglages.RESSOURCES.relative_to(src).as_posix() == CA.RESSOURCES


# --- Revue 12.12 ----------------------------------------------------------------------------


def _pyz_factice(travail: Path, modules: list[str]) -> None:
    from PyInstaller.archive.writers import ZlibArchiveWriter

    source = travail / "m.py"
    travail.mkdir(parents=True, exist_ok=True)
    source.write_text("x = 1\n", encoding="utf-8")
    code = {m: compile("x = 1", m, "exec") for m in modules}
    entrees = [(m, str(source), "PYMODULE") for m in modules]
    ZlibArchiveWriter(str(travail / "PYZ-00.pyz"), entrees, code)


def test_fermeture_runtime_lit_le_pyz_et_les_pyd(tmp_path: Path) -> None:
    dossier, travail = tmp_path / "dist", tmp_path / "travail"
    interne = dossier / "_internal"
    interne.mkdir(parents=True)
    (interne / "_tkinter.cp312-win_amd64.pyd").write_bytes(b"")
    _pyz_factice(travail, ["pydantic.main", "pandas.core.frame", "slmsp.app"])
    assert CA.fermeture_runtime(dossier, travail) == ["pandas", "tkinter"]
    # Sans PYZ, le contrôle échoue au lieu de passer à vide.
    with pytest.raises(CA.ErreurBuild, match="PYZ"):
        CA.fermeture_runtime(dossier, tmp_path / "vide")
    assert CA.fermeture_runtime(dossier) == ["tkinter"]


def test_bin_cpu_garde_toutes_les_dll_et_le_seul_serveur(tmp_path: Path) -> None:
    garde = CA._garder_bin_cpu
    assert garde(tmp_path / "llama-server.exe")
    assert not garde(tmp_path / "llama-bench.exe")
    assert garde(tmp_path / "ggml-base.dll") and garde(tmp_path / "llama-server-impl.dll")
    assert garde(tmp_path / "libomp140.x86_64.DLL")


def test_index_empreinte_nulle_refusee(ressources_factices) -> None:
    r = ressources_factices
    manifeste = r["index"] / "20260926" / "MANIFEST.json"
    manifeste.write_text(json.dumps({"fichiers": {"a.bin": None}}), encoding="utf-8")
    with pytest.raises(CA.ErreurBuild, match="empreinte absente ou invalide"):
        _plan(r)


def test_manifeste_fichiers_et_paquet_ecarte(tmp_path: Path) -> None:
    dossier = tmp_path / "AssistantSP"
    (dossier / "_internal").mkdir(parents=True)
    (dossier / "AssistantSP.exe").write_bytes(b"exe")
    (dossier / "_internal" / "x.dll").write_bytes(b"dll")
    chemin = tmp_path / "manifeste-fichiers.json"
    empreinte = CA.ecrire_manifeste_fichiers(dossier, chemin)
    contenu = json.loads(chemin.read_text(encoding="utf-8"))
    assert set(contenu) == {"AssistantSP.exe", "_internal/x.dll"}
    assert contenu["_internal/x.dll"] == sha256_fichier(dossier / "_internal" / "x.dll")
    assert empreinte == sha256_fichier(chemin)
    ancien = tmp_path / "AssistantSP-ECHEC"
    ancien.mkdir()
    ecarte = CA.ecarter_dossier(dossier)
    assert ecarte == ancien and not dossier.exists() and (ecarte / "AssistantSP.exe").is_file()


def test_var_dir_gele_sous_les_donnees_de_l_application(
    gele: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from slmsp.core.var import dossier_var

    monkeypatch.delenv("SLMSP_VAR_DIR", raising=False)
    attendu = (tmp_path / "local" / "AssistantSP" / "var").resolve()
    assert dossier_var() == attendu and attendu.is_dir()
    monkeypatch.setenv("SLMSP_VAR_DIR", str(tmp_path / "autre"))
    assert dossier_var() == (tmp_path / "autre").resolve()


def test_var_dir_non_gele_inchange(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from slmsp.core.var import dossier_var

    monkeypatch.delenv("SLMSP_VAR_DIR", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert dossier_var() == (tmp_path / "slmsp" / "var").resolve()
