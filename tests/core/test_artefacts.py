"""Runs immuables, reprise et espace disque (critères 1 à 4 et 7, story 1.3)."""

from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
import types
from collections import namedtuple
from datetime import datetime
from importlib import metadata
from pathlib import Path

import pytest

import slmsp.core.artefacts as artefacts
from slmsp.core.artefacts import (
    ArtefactExistant,
    EspaceInsuffisant,
    Run,
    ajouter_jsonl,
    empreinte_environnement,
    nouveau_run,
    ouvrir_run,
    reprendre,
    verifier_espace,
)
from slmsp.core.canonique import json_canonique, sha256_fichier
from slmsp.core.erreurs import ManifesteInvalide, SlmspError
from slmsp.core.schemas.run import EtatRun, RunManifest

MOTIF_RUN_ID = re.compile(r"^\d{8}-\d{6}-[a-z0-9.-]+-[0-9a-f]{4}$")
_FIXE = datetime(2026, 10, 12, 10, 15).astimezone()
CONFIG = {"modele": "granite-4.0-1b", "temperature": 0.0, "options": {"n": 3}}


@pytest.fixture
def racine(tmp_path: Path) -> Path:
    dossier = tmp_path / "projet"
    dossier.mkdir()
    return dossier


@pytest.fixture
def jeu(racine: Path) -> Path:
    chemin = racine / "entree.jsonl"
    chemin.write_bytes(b'{"id":"<item-factice-1>"}\n')
    return chemin


def _run(racine: Path, **champs) -> Run:
    return nouveau_run("eval-generation", "granite-4.0-1b", CONFIG, racine=racine, **champs)


def _octets(run: Run) -> bytes:
    return (run.dossier / "run.json").read_bytes()


# --- critère 1 : création ---------------------------------------------------------------


def test_nouveau_run_cree_dossier_et_manifeste(racine: Path, jeu: Path) -> None:
    run = nouveau_run(
        "eval-generation",
        "granite-4.0-1b",
        CONFIG,
        ["20261011-090000-seed-0000"],
        {"jeu": jeu},
        42,
        racine=racine,
        modele_ref="base:granite-4.0-1b",
        quantification="q4_k_m",
        variante_llamacpp="cpu",
        jeu_version="v1.0-provisoire",
        index_version="2026-10",
        couverture={"items": 3},
    )
    assert MOTIF_RUN_ID.match(run.run_id)
    assert "-granite-4.0-1b-" in run.run_id
    assert run.dossier == racine / "runs" / "eval-generation" / run.run_id
    brut = _octets(run)
    assert brut.endswith(b"\n") and b"\r" not in brut
    manifeste = RunManifest.model_validate_json(brut)
    assert manifeste == run.manifeste
    assert manifeste.type == "eval-generation" and manifeste.run_id == run.run_id
    assert manifeste.statut == "en_cours"
    assert manifeste.parents == ["20261011-090000-seed-0000"]
    assert manifeste.config == CONFIG and manifeste.graine == 42
    assert manifeste.entrees == {"jeu": sha256_fichier(jeu)}
    assert manifeste.modele_ref == "base:granite-4.0-1b"
    assert manifeste.quantification == "q4_k_m" and manifeste.variante_llamacpp == "cpu"
    assert manifeste.jeu_version == "v1.0-provisoire" and manifeste.index_version == "2026-10"
    assert manifeste.couverture == {"items": 3}
    assert manifeste.cree_le.tzinfo is not None
    env = manifeste.environnement
    assert env.os and env.cpu and env.python
    assert env.paquets["pydantic"] == metadata.version("pydantic")
    assert brut == json_canonique(json.loads(brut)) + b"\n"
    lignes = (run.dossier / "etat.jsonl").read_bytes().splitlines()
    assert len(lignes) == 1
    etat = EtatRun.model_validate_json(lignes[0])
    assert etat.statut == "en_cours" and etat.horodatage.tzinfo is not None
    assert run.statut_courant() == "en_cours"


def test_entree_relative_resolue_contre_racine(racine: Path, jeu: Path) -> None:
    run = nouveau_run("data-seed", "v1", {}, entrees={"jeu": "entree.jsonl"}, racine=racine)
    assert run.manifeste.entrees["jeu"] == sha256_fichier(jeu)


@pytest.mark.parametrize(
    ("type_run", "slug"),
    [
        ("eval-generation", "Mon Slug"),
        ("eval-generation", "a/b"),
        ("eval-generation", ""),
        ("../x", "granite"),
        ("Eval", "granite"),
        ("eval/x", "granite"),
        ("", "granite"),
    ],
)
def test_type_ou_slug_invalide(racine: Path, type_run: str, slug: str) -> None:
    with pytest.raises(ValueError):
        nouveau_run(type_run, slug, {}, racine=racine)
    assert not (racine / "runs").exists() or not any((racine / "runs").rglob("run.json"))


def test_champ_invalide_ne_cree_rien(racine: Path) -> None:
    with pytest.raises(ValueError):
        _run(racine, quantification="q8_0")
    with pytest.raises(ValueError):
        _run(racine, statut="complet")
    with pytest.raises(ValueError):
        nouveau_run("eval-generation", "granite", {"x": float("nan")}, racine=racine)
    with pytest.raises(ValueError):
        nouveau_run("eval-generation", "granite", {"x": float("inf")}, racine=racine)
    with pytest.raises(TypeError):
        nouveau_run("eval-generation", "granite", {"x": object()}, racine=racine)
    with pytest.raises(TypeError):
        nouveau_run("eval-generation", "granite", {"x": Path("p")}, racine=racine)
    with pytest.raises(ValueError):
        _run(racine, couverture={"taux": float("nan")})
    assert not (racine / "runs").exists()


def test_collision_run_id(racine: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tirages = iter(["aaaa", "aaaa", "bbbb"])
    monkeypatch.setattr(artefacts.secrets, "token_hex", lambda n: next(tirages))
    monkeypatch.setattr(artefacts, "_maintenant", lambda: _FIXE)
    premier = _run(racine)
    second = _run(racine)
    assert premier.run_id == "20261012-101500-granite-4.0-1b-aaaa"
    assert second.run_id == "20261012-101500-granite-4.0-1b-bbbb"
    assert RunManifest.model_validate_json(_octets(second)).run_id == second.run_id


def test_collision_persistante(racine: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(artefacts.secrets, "token_hex", lambda n: "cccc")
    monkeypatch.setattr(artefacts, "_maintenant", lambda: _FIXE)
    _run(racine)
    with pytest.raises(SlmspError, match="20 essais"):
        _run(racine)


# --- empreinte et git -------------------------------------------------------------------

_GIT = shutil.which("git")


def _git(racine: Path, *arguments: str) -> str:
    hooks = racine.parent / "hooks-vides"
    hooks.mkdir(exist_ok=True)
    resultat = subprocess.run(
        [
            "git",
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "-c",
            f"core.hooksPath={hooks}",
            *arguments,
        ],
        cwd=racine,
        capture_output=True,
        text=True,
        check=True,
    )
    return resultat.stdout.strip()


@pytest.mark.skipif(_GIT is None, reason="git absent")
def test_git_commit_et_modification(racine: Path) -> None:
    _git(racine, "init", "-q")
    suivi = racine / "suivi.txt"
    suivi.write_bytes(b"v1\n")
    _git(racine, "add", "suivi.txt")
    _git(racine, "commit", "-q", "-m", "init")
    head = _git(racine, "rev-parse", "HEAD")

    propre = empreinte_environnement(racine)
    assert propre.git_commit == head and propre.git_modifie is False

    (racine / "non-suivi.txt").write_bytes(b"x\n")
    seul_non_suivi = empreinte_environnement(racine)
    assert seul_non_suivi.git_commit == head and seul_non_suivi.git_modifie is False

    suivi.write_bytes(b"v2\n")
    run = _run(racine)
    lu = json.loads(_octets(run))
    assert lu["environnement"]["git_commit"] == head
    assert len(head) == 40
    assert lu["environnement"]["git_modifie"] is True


def test_hors_depot_git(racine: Path) -> None:
    env = empreinte_environnement(racine)
    assert env.git_commit is None and env.git_modifie is None


def test_git_absent(racine: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (racine / ".git").mkdir()

    def absent(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(artefacts.subprocess, "run", absent)
    env = empreinte_environnement(racine)
    assert env.git_commit is None and env.git_modifie is None


def test_nvml_absent(monkeypatch: pytest.MonkeyPatch, racine: Path) -> None:
    import builtins

    importer = builtins.__import__

    def sans_pynvml(nom, *args, **kwargs):
        if nom == "pynvml":
            raise ImportError(nom)
        return importer(nom, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", sans_pynvml)
    env = empreinte_environnement(racine)
    assert env.gpus == [] and env.pilote_nvidia is None and env.cuda is None


def _faux_pynvml(*, init_echoue: bool = False) -> types.ModuleType:
    module = types.ModuleType("pynvml")
    module.arrets = []  # type: ignore[attr-defined]

    def nvml_init() -> None:
        if init_echoue:
            raise RuntimeError("NVML indisponible")

    module.nvmlInit = nvml_init  # type: ignore[attr-defined]
    module.nvmlShutdown = lambda: module.arrets.append(True)  # type: ignore[attr-defined]
    module.nvmlDeviceGetCount = lambda: 1  # type: ignore[attr-defined]
    module.nvmlDeviceGetHandleByIndex = lambda i: f"poignee-{i}"  # type: ignore[attr-defined]
    module.nvmlDeviceGetName = lambda p: b"GPU factice"  # type: ignore[attr-defined]
    module.nvmlDeviceGetMemoryInfo = lambda p: types.SimpleNamespace(total=8 * 1024**3)  # type: ignore[attr-defined]
    module.nvmlSystemGetDriverVersion = lambda: b"600.00"  # type: ignore[attr-defined]
    module.nvmlSystemGetCudaDriverVersion = lambda: 12040  # type: ignore[attr-defined]
    return module


def test_nvml_factice(monkeypatch: pytest.MonkeyPatch, racine: Path) -> None:
    faux = _faux_pynvml()
    monkeypatch.setitem(sys.modules, "pynvml", faux)
    env = empreinte_environnement(racine)
    assert [(g.nom, g.memoire_octets) for g in env.gpus] == [("GPU factice", 8 * 1024**3)]
    assert env.pilote_nvidia == "600.00" and env.cuda == "12.4"
    assert faux.arrets == [True]


def test_nvml_init_en_echec(monkeypatch: pytest.MonkeyPatch, racine: Path) -> None:
    monkeypatch.setitem(sys.modules, "pynvml", _faux_pynvml(init_echoue=True))
    env = empreinte_environnement(racine)
    assert env.gpus == [] and env.pilote_nvidia is None and env.cuda is None


def test_paquets_normalises(racine: Path) -> None:
    paquets = empreinte_environnement(racine).paquets
    assert paquets and all(nom == nom.lower() and "_" not in nom for nom in paquets)
    assert paquets["pydantic"] == metadata.version("pydantic")


# --- critère 2 : écritures --------------------------------------------------------------


def test_ecrire_une_seule_fois(racine: Path) -> None:
    run = _run(racine)
    chemin = run.ecrire("scores.json", b'{"score":1}')
    assert chemin.read_bytes() == b'{"score":1}'
    with pytest.raises(ArtefactExistant):
        run.ecrire("scores.json", b'{"score":2}')
    assert chemin.read_bytes() == b'{"score":1}'
    run.ecrire("rapports/note.md", "é\n")
    assert (run.dossier / "rapports" / "note.md").read_bytes() == "é\n".encode()
    run.ecrire("b.bin", bytearray(b"ab"))
    run.ecrire("m.bin", memoryview(b"cd"))
    assert (run.dossier / "m.bin").read_bytes() == b"cd"


@pytest.mark.parametrize("contenu", [5, None, [1, 2], {"a": 1}])
def test_ecrire_type_refuse(racine: Path, contenu: object) -> None:
    run = _run(racine)
    with pytest.raises(TypeError):
        run.ecrire("n.bin", contenu)  # type: ignore[arg-type]
    assert not (run.dossier / "n.bin").exists()


@pytest.mark.parametrize(
    "nom",
    [
        "../x",
        "../../evil",
        "a/../../x",
        "",
        ".",
        "run.json",
        "etat.jsonl",
        "RUN.JSON",
        "run.json.",
        "run.json ",
        "run.json::$DATA",
        "etat.jsonl.",
        "etat.jsonl::$DATA",
        "sous/x.",
        "sous/x ",
        "a:b",
        "sous/../run.json",
    ],
)
def test_nom_hors_du_run(racine: Path, nom: str) -> None:
    run = _run(racine)
    avant = _octets(run)
    avant_etat = (run.dossier / "etat.jsonl").read_bytes()
    with pytest.raises(ValueError):
        run.ecrire(nom, b"x")
    with pytest.raises(ValueError):
        run.ajouter_jsonl(nom, {"a": 1})
    assert _octets(run) == avant
    assert (run.dossier / "etat.jsonl").read_bytes() == avant_etat


@pytest.mark.parametrize(
    "nom", ["run.json", "RUN.JSON", "run.json.", "run.json ", "run.json::$DATA"]
)
def test_ajouter_jsonl_module_refuse_run_json(racine: Path, nom: str) -> None:
    run = _run(racine)
    avant = _octets(run)
    with pytest.raises(ValueError):
        ajouter_jsonl(run.dossier / nom, {"a": 1})
    assert _octets(run) == avant


def test_nom_absolu_refuse(racine: Path, tmp_path: Path) -> None:
    run = _run(racine)
    with pytest.raises(ValueError):
        run.ecrire(str(tmp_path / "ailleurs.json"), b"x")
    assert not (tmp_path / "ailleurs.json").exists()


def test_ajouter_jsonl(racine: Path) -> None:
    run = _run(racine)
    avant = _octets(run)
    run.ajouter_jsonl("generations.jsonl", {"item_id": "Q-001", "texte": "é"})
    run.ajouter_jsonl(
        "generations.jsonl",
        EtatRun.model_validate_json((run.dossier / "etat.jsonl").read_bytes().splitlines()[0]),
    )
    brut = (run.dossier / "generations.jsonl").read_bytes()
    lignes = brut.split(b"\n")
    assert lignes[0] == json_canonique({"item_id": "Q-001", "texte": "é"})
    assert brut.endswith(b"\n") and b"\r" not in brut
    assert len(run.lire_jsonl("generations.jsonl")) == 2
    assert _octets(run) == avant


def test_ajouter_jsonl_refuse_run_json(racine: Path) -> None:
    run = _run(racine)
    with pytest.raises(ValueError):
        ajouter_jsonl(run.dossier / "run.json", {"a": 1})


def test_ligne_tronquee_ignoree_puis_isolee(racine: Path) -> None:
    run = _run(racine)
    chemin = run.dossier / "generations.jsonl"
    run.ajouter_jsonl("generations.jsonl", {"item_id": "Q-001"})
    with chemin.open("ab") as flux:
        flux.write(b'{"item_id":"Q-0')  # arrêt brutal en cours d'écriture
    assert run.lire_jsonl("generations.jsonl") == [{"item_id": "Q-001"}]
    run.ajouter_jsonl("generations.jsonl", {"item_id": "Q-002"})
    assert chemin.read_bytes().startswith(b'{"item_id":"Q-001"}\n{"item_id":"Q-0\n')
    assert run.lire_jsonl("generations.jsonl") == [{"item_id": "Q-001"}, {"item_id": "Q-002"}]


def test_aucune_suppression_ni_ecrasement_dans_le_module() -> None:
    interdits = {
        "unlink",
        "remove",
        "removedirs",
        "rmtree",
        "rmdir",
        "rename",
        "replace",
        "truncate",
        "ftruncate",
        "write_text",
        "write_bytes",
    }
    arbre = ast.parse(Path(artefacts.__file__).read_text(encoding="utf-8"))
    for noeud in ast.walk(arbre):
        if not isinstance(noeud, ast.Call):
            continue
        fonction = noeud.func
        nom = fonction.attr if isinstance(fonction, ast.Attribute) else getattr(fonction, "id", "")
        assert nom not in interdits, f"ligne {noeud.lineno} : appel à {nom}"
        if nom == "open":
            modes = [mot.value for mot in noeud.keywords if mot.arg == "mode"]
            modes += list(noeud.args)
            for mode in modes:
                if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
                    if re.fullmatch(r"[rwxabt+]+", mode.value):
                        assert "w" not in mode.value, f"ligne {noeud.lineno} : mode {mode.value}"


# --- critère 3 : fin de run -------------------------------------------------------------


@pytest.mark.parametrize(
    "statut", ["complet", "partiel-budget", "partiel-erreur", "interrompu", "degrade"]
)
def test_terminer(racine: Path, statut: str) -> None:
    run = _run(racine)
    avant = _octets(run)
    run.terminer(statut, motif="test")
    assert _octets(run) == avant
    lignes = (run.dossier / "etat.jsonl").read_bytes().splitlines()
    assert len(lignes) == 2
    assert EtatRun.model_validate_json(lignes[-1]).motif == "test"
    assert run.statut_courant() == statut
    assert ouvrir_run(run.run_id, racine=racine).statut_courant() == statut


@pytest.mark.parametrize("statut", ["en_cours", "fini", ""])
def test_terminer_refuse(racine: Path, statut: str) -> None:
    run = _run(racine)
    with pytest.raises(ValueError):
        run.terminer(statut)
    assert run.statut_courant() == "en_cours"


def test_statut_courant_ignore_ligne_invalide(racine: Path) -> None:
    run = _run(racine)
    run.terminer("interrompu")
    ajouter_jsonl(run.dossier / "etat.jsonl", {"statut": "inconnu"})
    assert run.statut_courant() == "interrompu"


# --- critère 4 : reprise ----------------------------------------------------------------


def test_reprendre(racine: Path) -> None:
    run = _run(racine)
    for item in ("Q-001", "Q-002", "Q-003"):
        run.ajouter_jsonl("generations.jsonl", {"item_id": item, "sortie": "<sortie-factice>"})
    run.terminer("interrompu")
    avant_manifeste = _octets(run)
    avant = (run.dossier / "generations.jsonl").read_bytes()

    repris, deja = reprendre(run.run_id, fichier="generations.jsonl", cle="item_id", racine=racine)
    assert deja == {"Q-001", "Q-002", "Q-003"}
    assert repris.dossier == run.dossier
    assert repris.statut_courant() == "en_cours"
    assert (run.dossier / "generations.jsonl").read_bytes() == avant
    assert _octets(run) == avant_manifeste
    etats = [
        EtatRun.model_validate_json(x)
        for x in (run.dossier / "etat.jsonl").read_bytes().splitlines()
    ]
    assert [e.statut for e in etats] == ["en_cours", "interrompu", "en_cours"]


def test_reprendre_fichier_absent(racine: Path) -> None:
    run = _run(racine)
    run.terminer("partiel-budget")
    _, deja = reprendre(run.run_id, racine=racine)
    assert deja == set()


def test_reprendre_fichier_invalide_n_ecrit_rien(racine: Path) -> None:
    run = _run(racine)
    run.terminer("interrompu")
    avant = (run.dossier / "etat.jsonl").read_bytes()
    with pytest.raises(ValueError):
        reprendre(run.run_id, fichier="../x.jsonl", racine=racine)
    assert (run.dossier / "etat.jsonl").read_bytes() == avant
    assert run.statut_courant() == "interrompu"


def test_reprendre_etat_tronque(racine: Path) -> None:
    run = _run(racine)
    run.ajouter_jsonl("resultats.jsonl", {"cle": "K-1"})
    run.terminer("interrompu")
    with (run.dossier / "etat.jsonl").open("ab") as flux:
        flux.write(b'{"schema_version":1,"statut":"comp')  # arrêt brutal
    assert run.statut_courant() == "interrompu"
    repris, deja = reprendre(run.run_id, racine=racine)
    assert deja == {"K-1"}
    assert repris.statut_courant() == "en_cours"
    lignes = (run.dossier / "etat.jsonl").read_bytes().split(b"\n")
    assert lignes[-3] == b'{"schema_version":1,"statut":"comp'
    assert EtatRun.model_validate_json(lignes[-2]).statut == "en_cours"


def test_reprendre_run_complet(racine: Path) -> None:
    run = _run(racine)
    run.terminer("complet")
    with pytest.raises(SlmspError, match="complet"):
        reprendre(run.run_id, racine=racine)
    assert run.statut_courant() == "complet"


@pytest.mark.parametrize("run_id", ["20991231-000000-inconnu-0000", "../x", "pas-un-id"])
def test_reprendre_run_inconnu(racine: Path, run_id: str) -> None:
    _run(racine)
    with pytest.raises(ManifesteInvalide):
        reprendre(run_id, racine=racine)


def test_ouvrir_run_manifeste_invalide(racine: Path) -> None:
    dossier = racine / "runs" / "eval-generation" / "20261012-101500-x-0000"
    dossier.mkdir(parents=True)
    (dossier / "run.json").write_bytes(b"{}")
    with pytest.raises(ManifesteInvalide):
        ouvrir_run("20261012-101500-x-0000", racine=racine)


def test_ouvrir_run_ambigu(racine: Path) -> None:
    run = _run(racine)
    shutil.copytree(run.dossier, racine / "runs" / "autre-type" / run.run_id)
    with pytest.raises(ManifesteInvalide, match="ambigu"):
        ouvrir_run(run.run_id, racine=racine)


def test_ouvrir_run_type_incoherent(racine: Path) -> None:
    run = _run(racine)
    autre = racine / "autre-racine"
    shutil.copytree(run.dossier, autre / "runs" / "data-seed" / run.run_id)
    with pytest.raises(ManifesteInvalide, match="incohérent"):
        ouvrir_run(run.run_id, racine=autre)


# --- critère 7 : espace disque ----------------------------------------------------------

_Usage = namedtuple("_Usage", "total used free")


def test_verifier_espace(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    mesures: list[Path] = []

    def faux_disk_usage(chemin):
        mesures.append(Path(chemin))
        return _Usage(10, 0, 5 * 1024**3)

    monkeypatch.setattr(artefacts.shutil, "disk_usage", faux_disk_usage)
    cible = tmp_path / "pas" / "encore" / "cree.bin"
    assert verifier_espace(cible, 1024**3) == 5 * 1024**3
    assert mesures == [tmp_path]
    with pytest.raises(EspaceInsuffisant) as erreur:
        verifier_espace(cible, 4 * 1024**3)
    message = str(erreur.value)
    assert str(5 * 1024**3) in message and str(4 * 1024**3) in message
    assert str(artefacts.SEUIL_ESPACE_LIBRE) in message
    assert verifier_espace(cible, 4 * 1024**3, seuil_octets=0) == 5 * 1024**3
    assert not (tmp_path / "pas").exists()


def test_verifier_espace_reel(tmp_path: Path) -> None:
    libre = verifier_espace(tmp_path / "a" / "b.bin", 0, seuil_octets=0)
    assert isinstance(libre, int) and libre >= 0


@pytest.mark.parametrize(("octets", "seuil"), [(-1, 0), (0, -1)])
def test_verifier_espace_negatif(tmp_path: Path, octets: int, seuil: int) -> None:
    with pytest.raises(ValueError):
        verifier_espace(tmp_path, octets, seuil_octets=seuil)


def test_seuil_par_defaut() -> None:
    assert artefacts.SEUIL_ESPACE_LIBRE == 2 * 1024**3
