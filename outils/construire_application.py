"""Construit le dossier exécutable de l'Assistant (story 12.12, FR-21, NFR-6, AD-23).

PyInstaller en `onedir` (jamais `onefile`, Q3). Le script vérifie d'abord les ressources
(présence, empreintes des GGUF, de `llama-server.exe` et de l'Index) et échoue avant PyInstaller
au moindre écart. Il génère ensuite `licences-tierces.json`, lance PyInstaller avec
`packaging/assistantsp.spec`, contrôle la fermeture runtime (aucune bibliothèque lourde), la
taille (<= 4 Go) et écrit `ressources/empreinte-application.txt` (SHA-256 de l'exécutable, Q4)
ainsi que `build/manifeste-application.json`.

Build complet (poste de dev, quelques Go, plusieurs minutes) :
    uv run --no-sync python outils/construire_application.py
(`--vendor`, `--modeles` et `--index` désignent les dossiers lourds, ignorés par git, du dépôt
principal quand on travaille dans un worktree.)
Runtime seul, sans Modèle ni Index (mesure de taille, démarrage) : ajouter `--sans-modele`.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

DEPOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEPOT / "src"))

from slmsp.core.canonique import sha256_fichier  # noqa: E402
from slmsp.core.config import racine_projet  # noqa: E402
from slmsp.core.schemas.config_application import charger_config_application  # noqa: E402
from slmsp.index.config import version_valide  # noqa: E402
from slmsp.inference.serveur import (  # noqa: E402
    charger_config_llamacpp,
    charger_config_modele,
)

NOM_APPLICATION = "AssistantSP"
LIMITE_OCTETS = 4_000_000_000  # NFR-6 : 4 Go (décimal, volontairement strict)
INTERNE = "_internal"  # dossier des ressources d'un `onedir` PyInstaller 6 (= sys._MEIPASS)
RESSOURCES = "slmsp/app/ressources"
FICHIER_EMPREINTE = "empreinte-application.txt"
FICHIER_LICENCES = "licences-tierces.json"
FICHIER_EXCLU = "pont-factice.js"  # 12.4, 12.6 : jamais dans l'application installée
LLAMA_SERVER = "llama-server.exe"

# AD-2 : fermeture runtime. Ces paquets ne doivent jamais entrer dans l'exécutable.
EXCLUSIONS = (
    "torch",
    "transformers",
    "trl",
    "peft",
    "bitsandbytes",
    "accelerate",
    "unsloth",
    "anthropic",
    "mistralai",
    "huggingface_hub",
    "datasets",
    "duckdb",
    "pyarrow",
    "pandas",
    "lm_eval",
    "sacrebleu",
    "nltk",
    "langdetect",
    "immutabledict",
    "playwright",
    "pytest",
    "tkinter",
    "matplotlib",
    "IPython",
)
# Sous `config/` : benchmarks et runs ne servent pas au runtime, les gabarits du Générateur
# (D1) non plus.
CONFIG_EXCLUE = ("benchmarks", "runs", "prompts/generateur")


class ErreurBuild(Exception):
    """Ressource manquante, empreinte fausse, taille dépassée : le build échoue."""


@dataclass(frozen=True)
class Fichier:
    source: Path
    destination: str  # chemin POSIX relatif à la racine des ressources (`_internal`)
    composant: str
    sha256_attendu: str | None = None

    @property
    def taille(self) -> int:
        return self.source.stat().st_size


@dataclass
class Plan:
    fichiers: list[Fichier] = field(default_factory=list)
    slug: str = ""
    variante: str = "cpu"
    tag: str = ""
    sans_modele: bool = False
    index_version: str | None = None

    def donnees(self) -> list[tuple[str, str]]:
        """Couples `(source, dossier de destination)` au format `datas` de PyInstaller."""
        return [(str(f.source), str(PurePosixPath(f.destination).parent)) for f in self.fichiers]

    def tailles(self) -> dict[str, int]:
        resultat: dict[str, int] = {}
        for f in self.fichiers:
            resultat[f.composant] = resultat.get(f.composant, 0) + f.taille
        return resultat


def _fichiers_sous(
    dossier: Path,
    destination: str,
    composant: str,
    *,
    ignorer: tuple[str, ...] = (),
    garder: Callable[[Path], bool] | None = None,
) -> list[Fichier]:
    """Tous les fichiers de `dossier` (récursif), moins les préfixes relatifs de `ignorer`."""
    resultat = []
    for chemin in sorted(p for p in dossier.rglob("*") if p.is_file()):
        relatif = chemin.relative_to(dossier).as_posix()
        if any(relatif == i or relatif.startswith(i + "/") for i in ignorer):
            continue
        if "__pycache__" in chemin.parts or (garder is not None and not garder(chemin)):
            continue
        resultat.append(Fichier(chemin, f"{destination}/{relatif}", composant))
    return resultat


def _exiger(chemin: Path, quoi: str) -> Path:
    if not chemin.exists():
        raise ErreurBuild(f"ressource manquante : {quoi} ({chemin})")
    return chemin


def _garder_bin_cpu(chemin: Path) -> bool:
    """`llama-server.exe` et ses DLL ; les autres outils llama.cpp (cli, bench…) sont exclus."""
    nom = chemin.name.lower()
    if nom.endswith(".exe"):
        return chemin.name == LLAMA_SERVER
    if nom.endswith("-impl.dll"):
        return nom == "llama-server-impl.dll"
    return True


def construire_plan(
    racine: Path,
    *,
    vendor: Path,
    modeles: Path,
    index: Path,
    sans_modele: bool = False,
    licences: Path | None = None,
) -> Plan:
    """Liste des fichiers à embarquer. Lève `ErreurBuild` si une ressource manque."""
    app = charger_config_application()
    llama = charger_config_llamacpp()
    plan = Plan(slug=app.modele, variante=app.variante, tag=llama.tag, sans_modele=sans_modele)
    if app.variante != "cpu":
        raise ErreurBuild("seule la variante llama.cpp `cpu` est embarquée (poste sans GPU)")

    config = _exiger(racine / "config", "config/")
    plan.fichiers += _fichiers_sous(config, "config", "config", ignorer=CONFIG_EXCLUE)

    ui = _exiger(racine / "src/slmsp/app/ui", "interface (app/ui)")
    plan.fichiers += _fichiers_sous(
        ui, "slmsp/app/ui", "interface", garder=lambda p: p.name != FICHIER_EXCLU
    )

    ressources = _exiger(racine / "src/slmsp/app/ressources", "app/ressources")
    plan.fichiers += _fichiers_sous(
        ressources,
        RESSOURCES,
        "ressources",
        garder=lambda p: p.name not in (FICHIER_LICENCES, FICHIER_EMPREINTE),
    )
    source_licences = licences or ressources / FICHIER_LICENCES
    plan.fichiers.append(
        Fichier(
            _exiger(source_licences, FICHIER_LICENCES),
            f"{RESSOURCES}/{FICHIER_LICENCES}",
            "ressources",
        )
    )

    bin_cpu = _exiger(vendor / "llama.cpp" / llama.tag / "bin-cpu", f"llama.cpp {llama.tag}")
    attendu = llama.binaires.get("bin-cpu/" + LLAMA_SERVER)
    for f in _fichiers_sous(
        bin_cpu, f"vendor/llama.cpp/{llama.tag}/bin-cpu", "llama.cpp", garder=_garder_bin_cpu
    ):
        sha = attendu if f.source.name == LLAMA_SERVER else None
        plan.fichiers.append(Fichier(f.source, f.destination, f.composant, sha))
    if not any(f.source.name == LLAMA_SERVER for f in plan.fichiers):
        raise ErreurBuild(f"{LLAMA_SERVER} absent de {bin_cpu}")

    if sans_modele:
        return plan

    for slug, composant in ((app.modele, f"modele:{app.modele}"), ("bge-m3", "embedding:bge-m3")):
        gguf = charger_config_modele(slug).gguf
        if gguf is None:
            raise ErreurBuild(f"config/modeles/{slug}.toml : section [gguf] absente")
        nom = PurePosixPath(gguf.fichier).name
        chemin = _exiger(modeles / slug / "gguf" / nom, f"GGUF {slug}")
        plan.fichiers.append(Fichier(chemin, f"models/{slug}/gguf/{nom}", composant, gguf.sha256))

    versions = (
        sorted(d.name for d in index.iterdir() if d.is_dir() and version_valide(d.name))
        if index.is_dir()
        else []
    )
    if not versions:
        raise ErreurBuild(f"aucun Index local `AAAAMMJJ` sous {index}")
    plan.index_version = versions[-1]
    dossier = index / plan.index_version
    manifeste = _exiger(dossier / "MANIFEST.json", "MANIFEST.json de l'Index")
    empreintes = json.loads(manifeste.read_text(encoding="utf-8")).get("fichiers", {})
    if not empreintes:
        raise ErreurBuild("MANIFEST.json de l'Index : aucune empreinte de fichier")
    composant = f"index:{plan.index_version}"
    plan.fichiers.append(Fichier(manifeste, f"index/{plan.index_version}/MANIFEST.json", composant))
    for nom, sha in sorted(empreintes.items()):
        chemin = _exiger(dossier / nom, f"fichier d'Index {nom}")
        plan.fichiers.append(Fichier(chemin, f"index/{plan.index_version}/{nom}", composant, sha))
    return plan


def verifier_empreintes(plan: Plan) -> None:
    """Compare les SHA-256 attendus (GGUF, Index, `llama-server.exe`). Échoue avant PyInstaller."""
    for f in plan.fichiers:
        if f.sha256_attendu is not None and sha256_fichier(f.source) != f.sha256_attendu:
            raise ErreurBuild(f"empreinte fausse : {f.source.name} ({f.composant})")


def verifier_taille(tailles: dict[str, int], limite: int = LIMITE_OCTETS) -> int:
    """Taille totale ; échoue avec le détail par composant si elle dépasse `limite`."""
    total = sum(tailles.values())
    if total > limite:
        detail = ", ".join(
            f"{nom} {taille / 1e6:.0f} Mo"
            for nom, taille in sorted(tailles.items(), key=lambda t: -t[1])
        )
        raise ErreurBuild(f"taille {total / 1e9:.2f} Go > {limite / 1e9:.1f} Go (NFR-6) : {detail}")
    return total


def fermeture_runtime(dossier: Path) -> list[str]:
    """Paquets exclus (AD-2) trouvés au premier niveau du dossier construit."""
    interne = dossier / INTERNE
    base = interne if interne.is_dir() else dossier
    presents = {entree.name.lower().split(".")[0] for entree in base.iterdir()}
    return sorted(e for e in EXCLUSIONS if e.lower() in presents)


def ecrire_empreinte(dossier: Path, exe: Path) -> str:
    """Écrit `empreinte-application.txt` (SHA-256 de l'exécutable) dans les ressources."""
    empreinte = sha256_fichier(exe)
    cible = dossier / INTERNE / RESSOURCES / FICHIER_EMPREINTE
    cible.parent.mkdir(parents=True, exist_ok=True)
    cible.write_text(empreinte + "\n", encoding="utf-8")
    return empreinte


def generer_licences(base: Path, vendor_tag: Path, destination: Path) -> list[str]:
    """Écrit `licences-tierces.json` à `destination` ; renvoie les composants « à vérifier ».

    Une licence n'est affirmée que si un fichier local l'atteste : `LICENSE` des sources
    llama.cpp, métadonnées installées de pywebview et de PyInstaller. Le reste garde « à vérifier ».
    """
    brut = json.loads(base.read_text(encoding="utf-8"))
    for c in brut["composants"]:
        attestation = _attester(c["nom"], vendor_tag)
        if attestation:
            c["licence"], c["source"] = attestation
    a_verifier = [c["nom"] for c in brut["composants"] if c["licence"].startswith("à vérifier")]
    brut["statut"] = "provisoire" if a_verifier else "généré au build"
    brut["note"] = (
        "Généré au build à partir de fichiers locaux. Les entrées « à vérifier » ne sont "
        "attestées par aucun fichier présent : à valider avant diffusion."
        if a_verifier
        else "Généré au build à partir de fichiers locaux."
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(brut, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return a_verifier


def _attester(nom: str, vendor_tag: Path) -> tuple[str, str] | None:
    if nom == "llama.cpp":
        fichier = vendor_tag / "src" / "LICENSE"
        if fichier.is_file() and fichier.read_text(encoding="utf-8").lstrip().startswith(
            "MIT License"
        ):
            return "MIT", "fichier:llama.cpp/src/LICENSE"
        return None
    paquet = {"pywebview": "pywebview", "PyInstaller": "pyinstaller"}.get(nom)
    if paquet is None:
        return None
    try:
        meta = importlib.metadata.metadata(paquet)
    except importlib.metadata.PackageNotFoundError:
        return None
    classes = [c for c in meta.get_all("Classifier") or [] if c.startswith("License ::")]
    if not classes:
        return None
    if paquet == "pyinstaller":
        return (
            "GPL-2.0 ou ultérieure, avec exception pour distribuer des programmes tiers",
            f"metadonnees:{paquet}",
        )
    return classes[0].split("::")[-1].strip(), f"metadonnees:{paquet}"


def ecrire_manifeste(
    chemin: Path,
    plan: Plan,
    *,
    total: int | None = None,
    runtime: int | None = None,
    empreinte: str | None = None,
    licences_a_verifier: list[str] | None = None,
) -> dict:
    """`build/manifeste-application.json` : tailles par composant, empreintes GGUF et Index."""
    manifeste = {
        "schema_version": 1,
        "application": NOM_APPLICATION,
        "modele": None if plan.sans_modele else plan.slug,
        "variante_llamacpp": plan.variante,
        "tag_llamacpp": plan.tag,
        "index_version": plan.index_version,
        "sans_modele": plan.sans_modele,
        "limite_octets": LIMITE_OCTETS,
        "taille_donnees_octets": sum(plan.tailles().values()),
        "taille_runtime_octets": runtime,
        "taille_totale_octets": total,
        "composants": dict(sorted(plan.tailles().items())),
        "empreintes": {f.destination: f.sha256_attendu for f in plan.fichiers if f.sha256_attendu},
        "empreinte_application": empreinte,
        "licences_a_verifier": licences_a_verifier or [],
    }
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(manifeste, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifeste


def taille_dossier(dossier: Path) -> int:
    return sum(p.stat().st_size for p in dossier.rglob("*") if p.is_file())


def lancer_pyinstaller(plan: Plan, sortie: Path) -> Path:
    """Écrit le plan de données puis lance PyInstaller sur le `.spec`. Renvoie le dossier."""
    plan_json = sortie / "plan-donnees.json"
    plan_json.write_text(json.dumps(plan.donnees(), indent=1), encoding="utf-8")
    cmd = [
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
        "--distpath", str(sortie / "dist"), "--workpath", str(sortie / "travail"),
        str(DEPOT / "packaging" / "assistantsp.spec"),
    ]  # fmt: skip
    env = {**os.environ, "SLMSP_PLAN_BUILD": str(plan_json)}
    resultat = subprocess.run(cmd, cwd=DEPOT, env=env, check=False)
    if resultat.returncode != 0:
        raise ErreurBuild(f"PyInstaller a échoué (code {resultat.returncode})")
    return sortie / "dist" / NOM_APPLICATION


def construire(args: argparse.Namespace) -> int:
    sortie = Path(args.sortie).resolve()
    sortie.mkdir(parents=True, exist_ok=True)
    vendor, modeles, index = Path(args.vendor), Path(args.modeles), Path(args.index)

    licences = sortie / "ressources" / FICHIER_LICENCES
    a_verifier = generer_licences(
        DEPOT / "src/slmsp/app/ressources" / FICHIER_LICENCES,
        vendor / "llama.cpp" / charger_config_llamacpp().tag,
        licences,
    )
    plan = construire_plan(
        DEPOT,
        vendor=vendor,
        modeles=modeles,
        index=index,
        sans_modele=args.sans_modele,
        licences=licences,
    )
    verifier_empreintes(plan)
    verifier_taille(
        plan.tailles()
    )  # les seules données dépassent la limite : stop avant PyInstaller

    dossier = lancer_pyinstaller(plan, sortie)
    exe = dossier / f"{NOM_APPLICATION}.exe"
    if not exe.is_file():
        raise ErreurBuild(f"exécutable absent : {exe}")
    lourds = fermeture_runtime(dossier)
    if lourds:
        raise ErreurBuild(f"fermeture runtime violée (AD-2) : {', '.join(lourds)}")
    empreinte = ecrire_empreinte(dossier, exe)
    total = taille_dossier(dossier)
    runtime = max(total - sum(plan.tailles().values()), 0)
    ecrire_manifeste(
        sortie / "manifeste-application.json",
        plan,
        total=total,
        runtime=runtime,
        empreinte=empreinte,
        licences_a_verifier=a_verifier,
    )
    verifier_taille({**plan.tailles(), "runtime": runtime})
    print(f"{dossier} : {total / 1e6:.0f} Mo, empreinte {empreinte}")  # noqa: T201
    return 0


def lire_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    racine = racine_projet()
    p = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    p.add_argument("--vendor", default=str(racine / "vendor"), help="dossier vendor/ (llama.cpp)")
    p.add_argument("--modeles", default=str(racine / "models"), help="dossier models/")
    p.add_argument("--index", default=str(racine / "index"), help="dossier index/")
    p.add_argument("--sortie", default=str(DEPOT / "build"), help="dossier de sortie (build/)")
    p.add_argument("--sans-modele", action="store_true", help="runtime seul, sans GGUF ni Index")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        return construire(lire_arguments(argv))
    except ErreurBuild as exc:
        print(f"ECHEC : {exc}", file=sys.stderr)  # noqa: T201
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
