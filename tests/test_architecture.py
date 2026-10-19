"""Test d'architecture (AD-1, AD-2, AD-3 verrous 1 et 3, AD-4, AD-24).

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
    "fournisseurs": 2,
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
    "publication": 4,
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
# AD-24 : lectures de `data` et `train` seulement via `slmsp.core.artefacts` (`lire`,
# `ouvrir_sqlite_lecture`). Lecteurs interdits : module qualifié -> fonctions.
LECTURE_CONTROLEE = {"data", "train"}
ATTRIBUTS_LECTURE = {"read_text", "read_bytes", "open"}
LECTEURS_INTERDITS: dict[str, frozenset[str]] = {
    "json": frozenset({"load"}),
    "io": frozenset({"open"}),
    "builtins": frozenset({"open"}),
    "pickle": frozenset({"load"}),
    "tomllib": frozenset({"load"}),
    "sqlite3": frozenset({"connect"}),
    "duckdb": frozenset(
        {"connect", "sql", "query", "read_csv", "read_json", "read_parquet", "from_parquet"}
    ),
    "pyarrow.parquet": frozenset({"read_table", "read_pandas", "ParquetFile", "ParquetDataset"}),
    "pyarrow.dataset": frozenset({"dataset"}),
    "pyarrow.csv": frozenset({"read_csv", "open_csv"}),
    "pyarrow.json": frozenset({"read_json"}),
    "numpy": frozenset({"load", "loadtxt", "genfromtxt", "fromfile"}),
    "pandas": frozenset({"read_csv", "read_json", "read_parquet", "read_pickle"}),
    "slmsp.core.var": frozenset({"ouvrir_sqlite"}),
}
IMPORTS_LECTURE = {
    (module, f) for module, fonctions in LECTEURS_INTERDITS.items() for f in fonctions
}
# AD-24 : le journal du second juge n'est jamais lisible par `data` ni `train`. Tout journal
# Mistral qu'ils ouvrent porte un `lecteur` (liste d'accès appliquée à l'ouverture).
NOMS_JOURNAL_JUGE = {"USAGES_JUGE", "fichier_journal_juge"}
USAGE_JUGE = "juge-second"
OUVERTURES_JOURNAL = {"journal_pour", "JournalMistral"}
# AD-3 verrou 3 : le jeton de preuve et `_appeler` ne sortent pas du Générateur.
JETON = "_JETON"
MODULES_JETON = {"slmsp.mistral.generateur", "slmsp.mistral.journal"}
APPEL_PRIVE = "_appeler"
MODULES_APPEL_PRIVE = {"slmsp.mistral.client", "slmsp.mistral.generateur"}
# AD-3 verrou 1 : `eval/outils/` échappe à ruff (TID251) ; ses imports de SDK sont vérifiés ici.
OUTILS = RACINE / "eval" / "outils"
SDK_RESERVES = {"anthropic": "slmsp/judge/", "mistralai": "slmsp/mistral/"}

# AD-4, AD-10 : aucun client MCP créé hors passerelle. Le transport Streamable HTTP ne
# s'importe que dans `slmsp/mcp/` et reçoit toujours `http_client=` (client de `net`).
MCP_INTERDITS = (
    "mcp.client.sse",
    "mcp.client.session_group",
    "mcp.ClientSessionGroup",
    "mcp.shared._httpx_utils",
    "mcp.Client",
    "mcp.client.Client",
    "mcp.client.client",
    "mcp.client.stdio",
    "mcp.stdio_client",
)
MCP_NOMS_INTERDITS = {"create_mcp_http_client", "ClientSessionGroup"}
MCP_STREAMABLE = "mcp.client.streamable_http"
MCP_FABRIQUE_STREAMABLE = "streamable_http_client"

REGLES = {
    "couche",
    "lourd-runtime",
    "anthropic",
    "mistralai",
    "judge-depuis-data/train",
    "client-http",
    "lecture-data/train",
    "journal-juge-depuis-data/train",
    "jeton-generateur",
    "publication",
    "client-mcp",
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


def _alias_modules(arbre: ast.Module, nom_module: str, est_paquet: bool) -> dict[str, str]:
    """Nom local -> nom qualifié, pour tous les imports du module (relatifs compris)."""
    alias: dict[str, str] = {}
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Import):
            for a in noeud.names:
                if a.asname:
                    alias[a.asname] = a.name
                else:
                    alias[a.name.split(".")[0]] = a.name.split(".")[0]
        elif isinstance(noeud, ast.ImportFrom):
            base = _base_relative(noeud, nom_module, est_paquet)
            for a in noeud.names:
                if a.name != "*":
                    alias[a.asname or a.name] = f"{base}.{a.name}"
    return alias


def _module_appele(fonction: ast.Attribute, alias: dict[str, str]) -> str | None:
    """Module qualifié de l'appel `m.f(...)` (`m` résolu par les alias), sinon `None`."""
    racine, attributs = _chaine(fonction)
    if racine is None:
        return None
    return ".".join([alias.get(racine, racine), *attributs[:-1]])


def _constats_journal_et_jeton(m: _Module) -> list[tuple[str, int, str]]:
    """Règles `journal-juge-depuis-data/train` et `jeton-generateur`."""
    constats: list[tuple[str, int, str]] = []
    controle = m.paquet in LECTURE_CONTROLEE
    for imp in m.imports:
        if controle and NOMS_JOURNAL_JUGE & set(imp.alias):
            constats.append(("journal-juge-depuis-data/train", imp.ligne, f"import de {imp.alias}"))
        if m.nom not in MODULES_JETON and JETON in imp.alias:
            constats.append(("jeton-generateur", imp.ligne, f"import de {JETON}"))
    for noeud in ast.walk(m.arbre):
        if isinstance(noeud, ast.Attribute):
            if controle and noeud.attr in NOMS_JOURNAL_JUGE:
                constats.append(
                    ("journal-juge-depuis-data/train", noeud.lineno, f"`.{noeud.attr}`")
                )
            if noeud.attr == JETON and m.nom not in MODULES_JETON:
                constats.append(("jeton-generateur", noeud.lineno, f"`.{JETON}`"))
            if noeud.attr == APPEL_PRIVE and m.nom not in MODULES_APPEL_PRIVE:
                constats.append(("jeton-generateur", noeud.lineno, f"`.{APPEL_PRIVE}`"))
        elif isinstance(noeud, ast.Constant) and isinstance(noeud.value, str):
            if controle and noeud.value == USAGE_JUGE:
                constats.append(("journal-juge-depuis-data/train", noeud.lineno, repr(USAGE_JUGE)))
            if noeud.value == JETON and m.nom not in MODULES_JETON:
                constats.append(("jeton-generateur", noeud.lineno, repr(JETON)))
        elif controle and isinstance(noeud, ast.Call):
            fonction = noeud.func
            if isinstance(fonction, ast.Name):
                nom: str | None = fonction.id
            elif isinstance(fonction, ast.Attribute):
                nom = fonction.attr
            else:
                nom = None
            if nom in OUVERTURES_JOURNAL and not any(k.arg == "lecteur" for k in noeud.keywords):
                constats.append(
                    ("journal-juge-depuis-data/train", noeud.lineno, f"{nom}() sans lecteur=")
                )
    return constats


def analyser_outils(dossier: Path) -> list[Violation]:
    """Imports de `anthropic` et `mistralai` sous `dossier` (`eval/outils/`)."""
    violations: list[Violation] = []
    for chemin in sorted(dossier.rglob("*.py")):
        if "__pycache__" in chemin.parts:
            continue
        fichier = chemin.relative_to(dossier.parent).as_posix()
        arbre = ast.parse(chemin.read_text(encoding="utf-8-sig"), filename=str(chemin))
        for noeud in ast.walk(arbre):
            if isinstance(noeud, ast.Import):
                noms = [a.name for a in noeud.names]
            elif isinstance(noeud, ast.ImportFrom) and noeud.level == 0 and noeud.module:
                noms = [noeud.module]
            else:
                continue
            for nom in noms:
                for sdk, dossier_permis in SDK_RESERVES.items():
                    if _correspond(nom, sdk):
                        violations.append(
                            Violation(sdk, fichier, noeud.lineno, f"{sdk} hors de {dossier_permis}")
                        )
    return violations


def _mcp_interdit(nom: str) -> bool:
    return any(_correspond(nom, interdit) for interdit in MCP_INTERDITS)


def _alias_mcp(arbre: ast.Module) -> dict[str, str]:
    """Nom local -> nom qualifié, pour les imports du SDK `mcp`."""
    alias: dict[str, str] = {}
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Import):
            for a in noeud.names:
                if _correspond(a.name, "mcp"):
                    if a.asname:
                        alias[a.asname] = a.name
                    else:
                        alias[a.name.split(".")[0]] = a.name.split(".")[0]
        elif isinstance(noeud, ast.ImportFrom) and noeud.level == 0 and noeud.module:
            if _correspond(noeud.module, "mcp"):
                for a in noeud.names:
                    if a.name != "*":
                        alias[a.asname or a.name] = f"{noeud.module}.{a.name}"
    return alias


def _chaine(noeud: ast.expr) -> tuple[str | None, list[str]]:
    """Racine (nom) et attributs d'une chaîne `a.b.c`."""
    attributs: list[str] = []
    while isinstance(noeud, ast.Attribute):
        attributs.insert(0, noeud.attr)
        noeud = noeud.value
    return (noeud.id if isinstance(noeud, ast.Name) else None), attributs


def _constats_client_mcp(m: _Module) -> list[tuple[int, str]]:
    """Règle `client-mcp` : imports, références et appels de `streamable_http_client`."""
    constats: list[tuple[int, str]] = []
    for imp in m.imports:
        # Un nom interdit réexporté (`from mcp.client.streamable_http import
        # create_mcp_http_client`) est signalé quel que soit le module source.
        interdits = sorted(n for n in imp.noms if _mcp_interdit(n)) or sorted(
            MCP_NOMS_INTERDITS & set(imp.alias)
        )
        if interdits:
            constats.append((imp.ligne, f"import de {interdits[0]}"))
        elif m.paquet != "mcp" and any(_correspond(n, MCP_STREAMABLE) for n in imp.noms):
            constats.append((imp.ligne, f"import de {MCP_STREAMABLE} hors de slmsp/mcp/"))
    alias = _alias_mcp(m.arbre)
    internes = {id(noeud.value) for noeud in ast.walk(m.arbre) if isinstance(noeud, ast.Attribute)}
    for noeud in ast.walk(m.arbre):
        if isinstance(noeud, ast.Attribute) and id(noeud) not in internes:
            racine, attributs = _chaine(noeud)
            qualifie = alias.get(racine or "")
            if qualifie is not None and _mcp_interdit(qualifie):
                continue  # déjà signalé à l'import
            complet = ".".join([qualifie, *attributs]) if qualifie else None
            if (complet and _mcp_interdit(complet)) or MCP_NOMS_INTERDITS & set(attributs):
                constats.append((noeud.lineno, f"référence à {complet or '.'.join(attributs)}"))
        elif isinstance(noeud, ast.Call):
            fonction = noeud.func
            if isinstance(fonction, ast.Name):
                cible = alias.get(fonction.id, fonction.id)
                est_fabrique = cible.split(".")[-1] == MCP_FABRIQUE_STREAMABLE
            else:
                est_fabrique = (
                    isinstance(fonction, ast.Attribute) and fonction.attr == MCP_FABRIQUE_STREAMABLE
                )
            if not est_fabrique:
                continue
            client_http = [k.value for k in noeud.keywords if k.arg == "http_client"]
            if not client_http or (
                isinstance(client_http[0], ast.Constant) and client_http[0].value is None
            ):
                constats.append((noeud.lineno, f"{MCP_FABRIQUE_STREAMABLE} sans http_client="))
    return constats


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

        for ligne, detail in _constats_client_mcp(m):
            signaler("client-mcp", ligne, detail)

        for regle, ligne, detail in _constats_journal_et_jeton(m):
            signaler(regle, ligne, detail)

        alias = _alias_modules(m.arbre, m.nom, m.chemin.name == "__init__.py")
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
                    or fonction.attr
                    in LECTEURS_INTERDITS.get(_module_appele(fonction, alias) or "", frozenset())
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


def test_outils_d_evaluation_sans_sdk_reserve() -> None:
    violations = analyser_outils(OUTILS)
    assert not violations, "\n".join(map(str, violations))


@pytest.mark.parametrize(
    ("contenu", "regle"),
    [
        ("import anthropic\n", "anthropic"),
        ("from anthropic import Anthropic\n", "anthropic"),
        ("import mistralai.client\n", "mistralai"),
        ("from mistralai.client import Mistral\n", "mistralai"),
        ("import urllib.request\nimport json\n", None),
    ],
)
def test_outils_synthetiques(tmp_path: Path, contenu: str, regle: str | None) -> None:
    outils = tmp_path / "eval" / "outils"
    outils.mkdir(parents=True)
    (outils / "outil.py").write_text(contenu, encoding="utf-8")
    assert [v.regle for v in analyser_outils(outils)] == ([regle] if regle else [])


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
    "mcp/direct.py": """
        import mcp.types as types
        from mcp import ClientSession
        from mcp.client import streamable_http
        from mcp.client.session import ClientSession as Session
        from mcp.client.streamable_http import streamable_http_client

        from slmsp.net import client


        def ouvrir(url):
            http = client("outillage", asynchrone=True, usage="mcp")
            streamable_http.streamable_http_client(url, http_client=http)
            return streamable_http_client(url, http_client=http, terminate_on_close=False)
        """,
    "mistral/client.py": """
        import mistralai

        from slmsp.net import client


        class ClientMistral:
            def appeler(self, usage):
                return self._appeler(usage, jeton=None)
        """,
    "mistral/journal.py": """
        def jeton(module):
            return getattr(module, "_JETON", None)
        """,
    "mistral/generateur.py": """
        _JETON = object()


        def generer(client):
            return client._appeler("generation", jeton=_JETON)
        """,
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
    "data/provenance.py": """
        import json as j

        from slmsp.core.artefacts import ouvrir_sqlite_lecture
        from slmsp.mistral.journal import journal_pour


        def appels(config):
            return journal_pour("generation", config, lecteur="data").appels()


        def decoder(texte):
            return j.loads(texte)
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
    "lecture-json-alias": (
        "lecture-data/train",
        {"data/a.py": "import json as j\n\n\ndef f(fichier):\n    return j.load(fichier)\n"},
    ),
    "lecture-sqlite3": (
        "lecture-data/train",
        {"data/a.py": "import sqlite3\n\nsqlite3.connect('var/appels-mistral.sqlite')\n"},
    ),
    "lecture-duckdb-alias": (
        "lecture-data/train",
        {"train/a.py": "import duckdb as d\n\nd.read_parquet('data/x.parquet')\n"},
    ),
    "lecture-import-duckdb": ("lecture-data/train", {"data/a.py": "from duckdb import sql\n"}),
    "lecture-pyarrow-parquet": (
        "lecture-data/train",
        {"data/a.py": "import pyarrow.parquet as pq\n\npq.read_table('data/x.parquet')\n"},
    ),
    "lecture-pyarrow-from": (
        "lecture-data/train",
        {"train/a.py": "from pyarrow import parquet\n\nparquet.read_table('x')\n"},
    ),
    "lecture-numpy": (
        "lecture-data/train",
        {"train/a.py": "import numpy as np\n\nnp.load('x.npy')\n"},
    ),
    "lecture-pickle": (
        "lecture-data/train",
        {"data/a.py": "import pickle\n\n\ndef f(flux):\n    return pickle.load(flux)\n"},
    ),
    "lecture-tomllib": (
        "lecture-data/train",
        {"data/a.py": "import tomllib\n\n\ndef f(flux):\n    return tomllib.load(flux)\n"},
    ),
    "lecture-ouvrir-sqlite": (
        "lecture-data/train",
        {"data/a.py": "from slmsp.core.var import ouvrir_sqlite\n"},
    ),
    "lecture-ouvrir-sqlite-module": (
        "lecture-data/train",
        {"train/a.py": "from ..core import var\n\nvar.ouvrir_sqlite('x')\n"},
    ),
    "journal-juge-usages": (
        "journal-juge-depuis-data/train",
        {"data/a.py": "from slmsp.mistral.journal import USAGES_JUGE\n"},
    ),
    "journal-juge-usage-litteral": (
        "journal-juge-depuis-data/train",
        {"train/a.py": "USAGE = 'juge-second'\n"},
    ),
    "journal-juge-fichier": (
        "journal-juge-depuis-data/train",
        {"data/a.py": "def f(config):\n    return config.fichier_journal_juge\n"},
    ),
    "journal-sans-lecteur": (
        "journal-juge-depuis-data/train",
        {
            "data/a.py": "from slmsp.mistral.journal import journal_pour\n\n\n"
            "def f(usage, config):\n    return journal_pour(usage, config).appels()\n"
        },
    ),
    "journal-classe-sans-lecteur": (
        "journal-juge-depuis-data/train",
        {
            "train/a.py": "from slmsp.mistral import journal\n\n\n"
            "def f(chemin, usages):\n    return journal.JournalMistral(chemin, usages)\n"
        },
    ),
    "jeton-import": (
        "jeton-generateur",
        {"data/a.py": "from slmsp.mistral.generateur import _JETON\n"},
    ),
    "jeton-attribut": (
        "jeton-generateur",
        {"evaluation/a.py": "import slmsp.mistral.generateur as g\n\nJETON = g._JETON\n"},
    ),
    "jeton-getattr": (
        "jeton-generateur",
        {"mistral/a.py": "def f(module):\n    return getattr(module, '_JETON')\n"},
    ),
    "jeton-appel-prive": (
        "jeton-generateur",
        {"harness/a.py": "def f(client):\n    return client._appeler('generation')\n"},
    ),
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
    "client-mcp-sse": ("client-mcp", {"mcp/a.py": "from mcp.client.sse import sse_client\n"}),
    "client-mcp-sse-paquet": ("client-mcp", {"harness/a.py": "from mcp.client import sse\n"}),
    "client-mcp-sse-attribut": (
        "client-mcp",
        {"mcp/a.py": "import mcp.client\n\nmcp.client.sse.sse_client(url)\n"},
    ),
    "client-mcp-session-group": (
        "client-mcp",
        {"cli/a.py": "from mcp import ClientSessionGroup\n"},
    ),
    "client-mcp-session-group-module": (
        "client-mcp",
        {"mcp/a.py": "import mcp.client.session_group\n"},
    ),
    "client-mcp-session-group-attribut": (
        "client-mcp",
        {"mcp/a.py": "import mcp\n\nmcp.ClientSessionGroup()\n"},
    ),
    "client-mcp-httpx-utils": (
        "client-mcp",
        {"mcp/a.py": "import mcp.shared._httpx_utils as u\n\nu.create_mcp_http_client()\n"},
    ),
    "client-mcp-create-attribut": (
        "client-mcp",
        {"mcp/a.py": "import mcp.shared as s\n\ns._httpx_utils.create_mcp_http_client()\n"},
    ),
    "client-mcp-client": ("client-mcp", {"cli/a.py": "from mcp import Client\n"}),
    "client-mcp-client-paquet": ("client-mcp", {"mcp/a.py": "from mcp.client import Client\n"}),
    "client-mcp-client-module": ("client-mcp", {"mcp/a.py": "from mcp.client import client\n"}),
    "client-mcp-client-attribut": (
        "client-mcp",
        {"mcp/a.py": "import mcp\n\nmcp.Client(serveur)\n"},
    ),
    "client-mcp-client-alias": (
        "client-mcp",
        {"mcp/a.py": "import mcp.client as c\n\nc.client.Client(serveur)\n"},
    ),
    "client-mcp-streamable-hors-mcp": (
        "client-mcp",
        {"harness/a.py": "from mcp.client.streamable_http import streamable_http_client\n"},
    ),
    "client-mcp-streamable-module-hors-mcp": (
        "client-mcp",
        {"app/a.py": "import mcp.client.streamable_http\n"},
    ),
    "client-mcp-streamable-sans-http-client": (
        "client-mcp",
        {
            "mcp/a.py": "from mcp.client.streamable_http import streamable_http_client\n\n"
            "streamable_http_client('https://mcp.data.gouv.fr/mcp')\n"
        },
    ),
    "client-mcp-streamable-alias": (
        "client-mcp",
        {
            "mcp/a.py": "from mcp.client.streamable_http import streamable_http_client as s\n\n"
            "s(url, terminate_on_close=False)\n"
        },
    ),
    "client-mcp-streamable-none": (
        "client-mcp",
        {
            "mcp/a.py": "from mcp.client import streamable_http as s\n\n"
            "s.streamable_http_client(url, http_client=None)\n"
        },
    ),
    "client-mcp-create-reexporte": (
        "client-mcp",
        {
            "mcp/a.py": "from mcp.client.streamable_http import create_mcp_http_client\n\n"
            "create_mcp_http_client()\n"
        },
    ),
    "client-mcp-stdio": ("client-mcp", {"mcp/a.py": "from mcp import stdio_client\n"}),
    "client-mcp-stdio-module": (
        "client-mcp",
        {"harness/a.py": "from mcp.client.stdio import stdio_client\n"},
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
    ("mcp", "import mcp.client.sse\n", True),
    ("harness", "from mcp.client.sse import sse_client\n", True),
    ("mcp", "from mcp.client import sse\n", True),
    ("mcp", "from mcp.client.session_group import ClientSessionGroup\n", True),
    ("cli", "from mcp import ClientSessionGroup\n", True),
    ("mcp", "from mcp.shared._httpx_utils import create_mcp_http_client\n", True),
    ("mcp", "from mcp import Client\n", True),
    ("mcp", "from mcp.client import Client\n", True),
    ("mcp", "from mcp.client.client import Client\n", True),
    ("mcp", "from mcp.client import client\n", True),
    ("mcp", "from mcp import ClientSession\n", False),
    ("mcp", "from mcp.client.session import ClientSession\n", False),
    ("mcp", "from mcp.client.streamable_http import streamable_http_client\n", False),
    ("mcp", "from mcp.client.streamable_http import create_mcp_http_client\n", True),
    ("mcp", "from mcp.client.stdio import stdio_client\n", True),
    ("harness", "from mcp import stdio_client\n", True),
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
