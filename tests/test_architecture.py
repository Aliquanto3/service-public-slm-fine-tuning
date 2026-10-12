"""Test d'architecture (AD-1, AD-2, AD-3 verrou 1, AD-4, AD-24).

Les sources sont lues par `ast.parse`, sans importer les modules. L'analyseur est
auto-testé sur des arbres synthétiques écrits dans `tmp_path` : un arbre propre et un
arbre fautif par règle. La configuration ruff (`TID251`) est vérifiée de la même façon.
"""

from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
SRC = RACINE / "src" / "slmsp"

# AD-1 : core (0) < net, budget (1a) < inference, index, mcp, mistral (1b) < harness, judge (2)
# < pipelines (3) < cli, app (4). Les modules racine (`slmsp/__init__.py`, `__main__.py`)
# sont au-dessus de tout.
COUCHES: dict[str, int] = {
    "core": 0,
    "net": 1,
    "budget": 1,
    "inference": 2,
    "index": 2,
    "mcp": 2,
    "mistral": 2,
    "harness": 3,
    "judge": 3,
    "fetch": 4,
    "indexation": 4,
    "evaluation": 4,
    "benchmarks": 4,
    "measure": 4,
    "data": 4,
    "train": 4,
    "compare": 4,
    "cli": 5,
    "app": 5,
}
COUCHE_RACINE = 6

# AD-2 : fermeture runtime et bibliothèques lourdes.
PAQUETS_RUNTIME = {"core", "net", "budget", "inference", "index", "mcp", "harness", "app"}
LOURDS = {
    "torch",
    "transformers",
    "trl",
    "peft",
    "bitsandbytes",
    "unsloth",
    "lm_eval",
    "bfcl_eval",
    "anthropic",
    "mistralai",
    "datasets",
    "duckdb",
    "pyarrow",
}
# AD-4 : clients HTTP réservés à `net`, publication interdite partout.
CLIENTS_HTTP = (
    "httpx",
    "httpx2",
    "requests",
    "urllib.request",
    "http.client",
    "urllib3",
    "aiohttp",
)
PUBLICATION = {
    "push_to_hub",
    "push_to_hub_merged",  # Unsloth
    "push_to_hub_gguf",  # Unsloth
    "upload_file",
    "upload_folder",
    "upload_large_folder",
    "create_commit",
    "create_repo",
}
# AD-24 : lectures de `data` et `train` seulement via `slmsp.core.artefacts.lire`.
LECTURE_CONTROLEE = {"data", "train"}
ATTRIBUTS_LECTURE = {"read_text", "read_bytes", "open"}
IMPORTS_LECTURE = {("json", "load"), ("io", "open"), ("builtins", "open")}

REGLES = {
    "couche",
    "lourd-runtime",
    "anthropic",
    "mistralai",
    "judge-depuis-data/train",
    "client-http",
    "lecture-data/train",
    "publication",
}


@dataclass(frozen=True)
class Violation:
    regle: str
    fichier: str
    ligne: int
    detail: str

    def __str__(self) -> str:
        return f"{self.fichier}:{self.ligne} [{self.regle}] {self.detail}"


@dataclass(frozen=True)
class _Import:
    noms: frozenset[str]  # noms pleinement qualifiés touchés par l'import
    internes: frozenset[str]  # modules du paquet analysé importés
    base: str
    alias: tuple[str, ...]
    ligne: int


@dataclass
class _Module:
    nom: str
    chemin: Path
    paquet: str | None
    arbre: ast.Module
    imports: list[_Import]


def _correspond(nom: str, cible: str) -> bool:
    return nom == cible or nom.startswith(cible + ".")


def _paquet(nom_module: str) -> str | None:
    parties = nom_module.split(".")
    return parties[1] if len(parties) > 1 else None


def _base_relative(noeud: ast.ImportFrom, nom_module: str, est_paquet: bool) -> str:
    if noeud.level == 0:
        return noeud.module or ""
    parties = nom_module.split(".")
    if not est_paquet:
        parties = parties[:-1]
    if noeud.level > 1:
        parties = parties[: len(parties) - (noeud.level - 1)]
    base = ".".join(parties)
    return f"{base}.{noeud.module}" if noeud.module else base


def _imports(
    arbre: ast.Module, nom_module: str, est_paquet: bool, racine: str, connus: set[str]
) -> list[_Import]:
    resultat = []
    for noeud in ast.walk(arbre):  # les imports locaux (dans une fonction) comptent
        if isinstance(noeud, ast.Import):
            for alias in noeud.names:
                internes = {alias.name} if _correspond(alias.name, racine) else set()
                resultat.append(
                    _Import(
                        frozenset({alias.name}), frozenset(internes), alias.name, (), noeud.lineno
                    )
                )
        elif isinstance(noeud, ast.ImportFrom):
            base = _base_relative(noeud, nom_module, est_paquet)
            alias = tuple(a.name for a in noeud.names)
            noms = {base} | {f"{base}.{a}" for a in alias if a != "*"}
            internes = set()
            if _correspond(base, racine):
                for a in alias:
                    internes.add(f"{base}.{a}" if f"{base}.{a}" in connus else base)
            resultat.append(
                _Import(frozenset(noms), frozenset(internes), base, alias, noeud.lineno)
            )
    return resultat


def _charger(racine_src: Path) -> dict[str, _Module]:
    racine = racine_src.name
    fichiers: dict[str, tuple[Path, bool, str | None]] = {}
    for chemin in sorted(racine_src.rglob("*.py")):
        if "__pycache__" in chemin.parts:
            continue
        relatif = chemin.relative_to(racine_src).with_suffix("").parts
        # Les modules à la racine (`slmsp/__init__.py`, `slmsp/__main__.py`) n'ont pas de paquet.
        paquet = relatif[0] if len(relatif) > 1 else None
        parties = [racine, *relatif]
        est_paquet = parties[-1] == "__init__"
        if est_paquet:
            parties = parties[:-1]
        fichiers[".".join(parties)] = (chemin, est_paquet, paquet)
    connus = set(fichiers)
    modules = {}
    for nom, (chemin, est_paquet, paquet) in fichiers.items():
        arbre = ast.parse(chemin.read_text(encoding="utf-8-sig"), filename=str(chemin))
        modules[nom] = _Module(
            nom, chemin, paquet, arbre, _imports(arbre, nom, est_paquet, racine, connus)
        )
    return modules


def _ancetres_et_soi(nom: str) -> list[str]:
    parties = nom.split(".")
    return [".".join(parties[:i]) for i in range(1, len(parties) + 1)]


def _fermeture_runtime(modules: dict[str, _Module]) -> set[str]:
    a_visiter = [nom for nom, m in modules.items() if m.paquet in PAQUETS_RUNTIME]
    vus: set[str] = set()
    while a_visiter:
        nom = a_visiter.pop()
        if nom in vus or nom not in modules:
            continue
        vus.add(nom)
        for imp in modules[nom].imports:
            for interne in imp.internes:
                # importer un sous-module exécute aussi les __init__ de ses paquets parents
                a_visiter.extend(n for n in _ancetres_et_soi(interne) if n in modules)
    return vus


def analyser(racine_src: Path) -> list[Violation]:
    """Analyse l'arbre `racine_src` (le dossier du paquet `slmsp`) et renvoie ses violations."""
    modules = _charger(racine_src)
    runtime = _fermeture_runtime(modules)
    violations: list[Violation] = []
    paquets_inconnus: set[str | None] = set()

    for m in modules.values():
        fichier = m.chemin.relative_to(racine_src.parent).as_posix()

        def signaler(regle: str, ligne: int, detail: str, fichier: str = fichier) -> None:
            violations.append(Violation(regle, fichier, ligne, detail))

        couche_source = COUCHE_RACINE if m.paquet is None else COUCHES.get(m.paquet)
        if couche_source is None:
            if m.paquet not in paquets_inconnus:
                paquets_inconnus.add(m.paquet)
                signaler("couche", 1, f"paquet `{m.paquet}` absent de la table des couches d'AD-1")
            continue

        for imp in m.imports:
            for interne in sorted(imp.internes):
                cible = modules[interne].paquet if interne in modules else _paquet(interne)
                couche_cible = COUCHE_RACINE if cible is None else COUCHES.get(cible, COUCHE_RACINE)
                if cible != m.paquet and couche_cible >= couche_source:
                    signaler("couche", imp.ligne, f"`{m.paquet}` importe `{interne}`")
                if m.paquet in LECTURE_CONTROLEE and cible == "judge":
                    signaler("judge-depuis-data/train", imp.ligne, f"import de `{interne}`")
            if m.nom in runtime and any(n.split(".")[0] in LOURDS for n in imp.noms):
                signaler(
                    "lourd-runtime", imp.ligne, f"`{imp.base}` atteint par la fermeture runtime"
                )
            if m.paquet != "judge" and any(_correspond(n, "anthropic") for n in imp.noms):
                signaler("anthropic", imp.ligne, "anthropic hors de slmsp/judge/")
            if m.paquet != "mistral" and any(_correspond(n, "mistralai") for n in imp.noms):
                signaler("mistralai", imp.ligne, "mistralai hors de slmsp/mistral/")
            if m.paquet != "net" and any(
                _correspond(n, client) for n in imp.noms for client in CLIENTS_HTTP
            ):
                signaler("client-http", imp.ligne, f"`{imp.base}` hors de slmsp/net/")
            if _correspond(imp.base, "huggingface_hub") and PUBLICATION & set(imp.alias):
                signaler(
                    "publication", imp.ligne, f"import de {sorted(PUBLICATION & set(imp.alias))}"
                )
            if m.paquet in LECTURE_CONTROLEE and any(
                (imp.base, a) in IMPORTS_LECTURE for a in imp.alias
            ):
                signaler("lecture-data/train", imp.ligne, f"import de lecture depuis `{imp.base}`")

        for noeud in ast.walk(m.arbre):
            if isinstance(noeud, ast.Attribute) and noeud.attr in PUBLICATION:
                signaler("publication", noeud.lineno, f"`.{noeud.attr}`")
            elif isinstance(noeud, ast.keyword) and noeud.arg == "push_to_hub":
                if not (isinstance(noeud.value, ast.Constant) and noeud.value.value is False):
                    signaler("publication", noeud.lineno, "push_to_hub différent de False")
            elif isinstance(noeud, ast.Call) and m.paquet in LECTURE_CONTROLEE:
                fonction = noeud.func
                if isinstance(fonction, ast.Name) and fonction.id == "open":
                    signaler("lecture-data/train", noeud.lineno, "open() hors de core.artefacts")
                elif isinstance(fonction, ast.Attribute) and (
                    fonction.attr in ATTRIBUTS_LECTURE
                    or (
                        fonction.attr == "load"
                        and isinstance(fonction.value, ast.Name)
                        and fonction.value.id == "json"
                    )
                ):
                    signaler(
                        "lecture-data/train",
                        noeud.lineno,
                        f"`.{fonction.attr}()` hors de core.artefacts",
                    )
    return violations


# --- Le vrai code -------------------------------------------------------------------------


def test_code_source_sans_violation() -> None:
    violations = analyser(SRC)
    assert not violations, "\n".join(map(str, violations))


def test_tous_les_paquets_ont_une_couche() -> None:
    paquets = {p.name for p in SRC.iterdir() if p.is_dir() and (p / "__init__.py").exists()}
    assert paquets == set(COUCHES)


# --- Auto-test sur des arbres synthétiques -------------------------------------------------


def _ecrire_arbre(racine: Path, fichiers: dict[str, str]) -> Path:
    paquet = racine / "slmsp"
    paquet.mkdir(parents=True)
    for relatif, contenu in fichiers.items():
        chemin = paquet / relatif
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(textwrap.dedent(contenu), encoding="utf-8")
    for dossier in [paquet, *(d for d in paquet.rglob("*") if d.is_dir())]:
        init = dossier / "__init__.py"
        if not init.exists():
            init.write_text("", encoding="utf-8")
    return paquet


ARBRE_PROPRE = {
    "__main__.py": "from slmsp.cli import main\n",
    "core/artefacts.py": """
        import json


        def lire(chemin, lecteur):
            with open(chemin, encoding="utf-8") as fichier:
                return json.load(fichier)
        """,
    "net/__init__.py": "import httpx\nfrom slmsp.core import artefacts\n",
    "budget/registre.py": "from slmsp.core.artefacts import lire\n",
    "inference/serveur.py": "from ..core.artefacts import lire\nfrom slmsp.net import client\n",
    "mistral/client.py": "import mistralai\n\nfrom slmsp.net import client\n",
    "judge/claude.py": "import anthropic\n\nfrom slmsp.net import client\n",
    "harness/prompts.py": "from slmsp.core.artefacts import lire\n",
    "harness/service.py": "from . import prompts\nfrom slmsp.inference import serveur\n",
    "data/generation.py": """
        from slmsp.core.artefacts import lire
        from slmsp.harness import prompts
        from slmsp.mistral import client


        def charger(chemin):
            return lire(chemin, lecteur="data")
        """,
    "train/run.py": """
        import torch

        from slmsp.core.artefacts import lire


        def config():
            return dict(push_to_hub=False, report_to="none")
        """,
    "evaluation/notation.py": "from slmsp.judge import claude\n",
    "fetch/hf.py": """
        import huggingface_hub


        def telecharger():
            return huggingface_hub.hf_hub_download("depot", "fichier")
        """,
    "app/ui.py": "from slmsp.harness import service\n",
    "cli/__init__.py": "import importlib\n\nfrom slmsp.evaluation import notation\n",
}


def test_arbre_synthetique_propre(tmp_path: Path) -> None:
    violations = analyser(_ecrire_arbre(tmp_path, ARBRE_PROPRE))
    assert not violations, "\n".join(map(str, violations))


CAS_FAUTIFS: dict[str, tuple[str, dict[str, str]]] = {
    "couche-vers-le-haut": ("couche", {"core/a.py": "from slmsp.harness import service\n"}),
    "couche-meme-niveau": ("couche", {"net/a.py": "import slmsp.budget\n"}),
    "couche-relative": ("couche", {"inference/a.py": "from ..mcp import outils\n"}),
    "couche-import-local": (
        "couche",
        {"index/a.py": "def f():\n    from slmsp.indexation import construction\n"},
    ),
    "couche-paquet-inconnu": ("couche", {"inconnu/a.py": "X = 1\n"}),
    "lourd-runtime-direct": ("lourd-runtime", {"harness/a.py": "import torch\n"}),
    "lourd-runtime-transitif": (
        "lourd-runtime",
        {
            "app/a.py": "from slmsp.compare import rapport\n",
            "compare/rapport.py": "def f():\n    import pyarrow\n",
        },
    ),
    "anthropic": ("anthropic", {"evaluation/a.py": "import anthropic\n"}),
    "anthropic-from": ("anthropic", {"compare/a.py": "from anthropic import Anthropic\n"}),
    "mistralai": ("mistralai", {"fetch/a.py": "from mistralai import Mistral\n"}),
    "judge-depuis-data": ("judge-depuis-data/train", {"data/a.py": "from slmsp.judge import x\n"}),
    "judge-depuis-train": ("judge-depuis-data/train", {"train/a.py": "import slmsp.judge.cache\n"}),
    "client-http-httpx": ("client-http", {"fetch/a.py": "import httpx\n"}),
    "client-http-httpx2": ("client-http", {"mcp/a.py": "import httpx2\n"}),
    "client-http-requests": ("client-http", {"data/a.py": "import requests\n"}),
    "client-http-urllib": ("client-http", {"core/a.py": "from urllib import request\n"}),
    "client-http-urlopen": ("client-http", {"judge/a.py": "from urllib.request import urlopen\n"}),
    "client-http-http-client": ("client-http", {"fetch/a.py": "from http import client\n"}),
    "client-http-urllib3": ("client-http", {"evaluation/a.py": "import urllib3\n"}),
    "client-http-aiohttp": ("client-http", {"compare/a.py": "import aiohttp\n"}),
    "lecture-open": (
        "lecture-data/train",
        {"data/a.py": "def f(chemin):\n    return open(chemin, encoding='utf-8').read()\n"},
    ),
    "lecture-read-text": (
        "lecture-data/train",
        {"train/a.py": "from pathlib import Path\n\nPath('x').read_text(encoding='utf-8')\n"},
    ),
    "lecture-read-bytes": (
        "lecture-data/train",
        {"data/a.py": "def f(chemin):\n    return chemin.read_bytes()\n"},
    ),
    "lecture-json-load": (
        "lecture-data/train",
        {"train/a.py": "import json\n\n\ndef f(fichier):\n    return json.load(fichier)\n"},
    ),
    "lecture-import-json-load": ("lecture-data/train", {"data/a.py": "from json import load\n"}),
    "publication-push-to-hub": (
        "publication",
        {"train/a.py": "def f(modele):\n    modele.push_to_hub('depot')\n"},
    ),
    "publication-push-to-hub-true": (
        "publication",
        {"train/a.py": "def f():\n    return dict(push_to_hub=True)\n"},
    ),
    "publication-upload-file": (
        "publication",
        {"fetch/a.py": "def f(api):\n    api.upload_file(path_or_fileobj='a')\n"},
    ),
    "publication-import": (
        "publication",
        {"judge/a.py": "from huggingface_hub import upload_folder\n"},
    ),
    "publication-unsloth-gguf": (
        "publication",
        {"train/a.py": "def f(modele):\n    modele.push_to_hub_gguf('depot')\n"},
    ),
}


def test_chaque_regle_a_un_cas_fautif() -> None:
    assert {regle for regle, _ in CAS_FAUTIFS.values()} == REGLES


@pytest.mark.parametrize(("regle", "fichiers"), CAS_FAUTIFS.values(), ids=CAS_FAUTIFS.keys())
def test_arbre_synthetique_fautif(tmp_path: Path, regle: str, fichiers: dict[str, str]) -> None:
    violations = analyser(_ecrire_arbre(tmp_path, fichiers))
    assert [v.regle for v in violations] == [regle], "\n".join(map(str, violations))


# --- Configuration ruff (TID251) -----------------------------------------------------------

CAS_RUFF: list[tuple[str, str, bool]] = [
    ("core", "import anthropic\n", True),
    ("evaluation", "from anthropic import Anthropic\n", True),
    ("judge", "import anthropic\n", False),
    ("core", "import mistralai\n", True),
    ("data", "from mistralai import Mistral\n", True),
    ("mistral", "import mistralai\n", False),
    ("core", "import httpx\n", True),
    ("mcp", "import httpx2\n", True),
    ("fetch", "import requests\n", True),
    ("core", "import urllib.request\n", True),
    ("harness", "from urllib.request import urlopen\n", True),
    ("core", "import http.client\n", True),
    ("fetch", "import urllib3\n", True),
    ("data", "import aiohttp\n", True),
    (
        "net",
        "import aiohttp\nimport http.client\nimport httpx\nimport httpx2\nimport requests\n"
        "import urllib.request\nimport urllib3\n",
        False,
    ),
    ("fetch", "from huggingface_hub import upload_file\n", True),
    ("fetch", "from huggingface_hub import create_repo\n", True),
    ("fetch", "from huggingface_hub import upload_folder\n", True),
    ("fetch", "from huggingface_hub import upload_large_folder\n", True),
    ("fetch", "from huggingface_hub import create_commit\n", True),
    ("fetch", "from huggingface_hub import hf_hub_download\n", False),
]


@pytest.fixture(scope="module")
def resultats_ruff(tmp_path_factory: pytest.TempPathFactory) -> dict[str, set[str]]:
    racine = tmp_path_factory.mktemp("ruff")
    shutil.copyfile(RACINE / "pyproject.toml", racine / "pyproject.toml")
    for i, (paquet, contenu, _) in enumerate(CAS_RUFF):
        chemin = racine / "src" / "slmsp" / paquet / f"cas_{i}.py"
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(contenu, encoding="utf-8")
    sortie = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--no-cache",
            "--select",
            "TID251",
            "--output-format",
            "json",
            "--exit-zero",
            ".",
        ],
        cwd=racine,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    codes: dict[str, set[str]] = {}
    for diagnostic in json.loads(sortie.stdout):
        codes.setdefault(Path(diagnostic["filename"]).name, set()).add(diagnostic["code"])
    return codes


@pytest.mark.parametrize(
    ("indice", "paquet", "contenu", "banni"),
    [(i, *cas) for i, cas in enumerate(CAS_RUFF)],
    ids=[f"{p}-{c.splitlines()[0]}" for p, c, _ in CAS_RUFF],
)
def test_ruff_tid251(
    resultats_ruff: dict[str, set[str]], indice: int, paquet: str, contenu: str, banni: bool
) -> None:
    signale = "TID251" in resultats_ruff.get(f"cas_{indice}.py", set())
    assert signale is banni
