"""Runs immuables, reprise, lecteur contrôlé et espace disque (AD-21, AD-24, AD-25, AD-26).

Runs. Chaque exécution écrit dans `<racine>/runs/<type>/<run_id>/`. `run.json`
(`RunManifest`) est écrit une fois, par création exclusive, et jamais réécrit ; le statut
évolue par ajout de lignes `EtatRun` dans `etat.jsonl`. Aucune fonction de ce module ne
supprime, ne renomme, ne remplace ni ne tronque un fichier : les fichiers s'ouvrent en
création exclusive (`"xb"`) ou en ajout (`"ab"`, `"a+b"`), jamais en `"w"`.

JSONL : UTF-8, LF, une ligne = `json_canonique(obj) + b"\\n"`. Une ligne qui n'est pas du
JSON valide est un fragment laissé par un arrêt brutal en cours d'écriture : elle est
ignorée à la lecture, jamais réécrite ; l'ajout suivant commence sur une nouvelle ligne.
Un fichier JSONL n'a qu'un seul écrivain à la fois : aucun verrou entre processus.

Lecteur contrôlé (AD-24, D-nuit-A2-18). `data` et `train` ne lisent des fichiers que par
`lire`, `lire_texte` ou `ouvrir_sqlite_lecture`, qui résolvent le chemin (liens et `..`)
puis appliquent un refus explicite (`eval/`, `runs/eval/`, `runs/eval-*`, cache des
verdicts) et enfin la liste d'accès du lecteur. Les bases de comparaison sont résolues
elles aussi (jonctions, liens). La comparaison des chemins ignore la casse sous Windows.
"""

from __future__ import annotations

import json
import os
import platform
import re
import secrets
import shutil
import sqlite3
import subprocess
from collections.abc import Iterable, Mapping
from datetime import datetime
from importlib import metadata
from pathlib import Path
from typing import Any, Final, Literal

from pydantic import BaseModel, ValidationError

from slmsp.core.canonique import json_canonique, sha256_fichier
from slmsp.core.config import dossier_modeles, env_sous_processus, racine_projet
from slmsp.core.erreurs import LectureInterdite, ManifesteInvalide, SlmspError
from slmsp.core.schemas.run import (
    MOTIF_RUN_ID,
    MOTIF_TYPE,
    STATUTS_FINAUX,
    Environnement,
    EtatRun,
    Gpu,
    RunManifest,
    Statut,
)
from slmsp.core.var import BUSY_TIMEOUT_MS, dossier_var

SEUIL_ESPACE_LIBRE: Final = 2 * 1024**3
"""Espace libre à garder en plus de l'écriture prévue (2 Gio) ; l'appelant le surcharge."""

NOM_MANIFESTE: Final = "run.json"
NOM_ETAT: Final = "etat.jsonl"
NOM_JOURNAL_MISTRAL: Final = "appels-mistral.sqlite"
NOM_CACHE_VERDICTS: Final = "verdicts.sqlite"
NOM_JOURNAL_LOCAL: Final = "generations-locales.sqlite"
"""Journal des générations du Modèle de base local (story 9.7), lisible par `train`."""
"""Cache des verdicts du Juge (`slmsp.judge.cache.NOM_CACHE`), refusé à `data` et `train`."""
ESSAIS_RUN_ID: Final = 20
DELAI_GIT: Final = 10.0
"""Délai maximal de chaque appel `git` de l'empreinte (secondes)."""

Lecteur = Literal["data", "train"]
LECTEURS: Final = ("data", "train")

_MOTIF_SLUG = re.compile(r"[a-z0-9.-]+")
_MOTIF_TYPE = re.compile(MOTIF_TYPE)
_MOTIF_RUN_ID = re.compile(MOTIF_RUN_ID)
_NOMS_RESERVES = frozenset({NOM_MANIFESTE, NOM_ETAT})
_CHAMPS_IMPOSES = frozenset(
    {"schema_version", "type", "run_id", "cree_le", "statut", "environnement", "entrees"}
)


class ArtefactExistant(SlmspError):
    """Écriture refusée : le fichier existe déjà (un artefact n'est jamais réécrit)."""


class EspaceInsuffisant(SlmspError):
    """Espace disque libre insuffisant pour l'écriture prévue."""


# --- JSONL --------------------------------------------------------------------------------


def _en_json(obj: Any) -> Any:
    return obj.model_dump(mode="json") if isinstance(obj, BaseModel) else obj


def _nom_normalise(nom: str) -> str:
    """Nom tel que Windows l'ouvre : sans flux `:…`, sans points ni espaces finaux."""
    return nom.split(":", 1)[0].rstrip(". ").lower()


def ajouter_jsonl(chemin: str | Path, obj: Any) -> None:
    """Ajoute `obj` (dict JSON ou modèle pydantic) en une ligne canonique à la fin de `chemin`.

    Le fichier est ouvert en ajout seul ; il est créé s'il manque. Si la dernière ligne
    existante est tronquée (sans LF final), un LF est d'abord ajouté pour l'isoler. Un seul
    écrivain par fichier : aucun verrou n'est pris entre processus.
    """
    chemin = Path(chemin)
    if _nom_normalise(chemin.name) == NOM_MANIFESTE:
        raise ValueError(f"{chemin} : `{NOM_MANIFESTE}` n'accepte aucun ajout")
    ligne = json_canonique(_en_json(obj)) + b"\n"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("a+b") as flux:
        flux.seek(0, os.SEEK_END)
        if flux.tell() > 0:
            flux.seek(-1, os.SEEK_END)
            if flux.read(1) != b"\n":
                ligne = b"\n" + ligne
        flux.write(ligne)
        flux.flush()


def _lire_lignes_jsonl(chemin: Path) -> list[Any]:
    try:
        with chemin.open("rb") as flux:
            brut = flux.read()
    except FileNotFoundError:
        return []
    objets: list[Any] = []
    for ligne in brut.split(b"\n"):
        if not ligne.strip():
            continue
        try:
            objets.append(json.loads(ligne.decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue  # fragment d'une écriture interrompue
    return objets


# --- Empreinte de l'environnement ------------------------------------------------------


def _gpus_nvml() -> tuple[list[Gpu], str | None, str | None]:
    try:
        import pynvml
    except Exception:
        return [], None, None
    try:
        pynvml.nvmlInit()
    except Exception:
        return [], None, None
    try:
        gpus: list[Gpu] = []
        for indice in range(pynvml.nvmlDeviceGetCount()):
            poignee = pynvml.nvmlDeviceGetHandleByIndex(indice)
            nom = pynvml.nvmlDeviceGetName(poignee)
            if isinstance(nom, bytes):
                nom = nom.decode("utf-8", errors="replace")
            memoire = int(pynvml.nvmlDeviceGetMemoryInfo(poignee).total)
            gpus.append(Gpu(nom=str(nom), memoire_octets=memoire))
        pilote = pynvml.nvmlSystemGetDriverVersion()
        if isinstance(pilote, bytes):
            pilote = pilote.decode("utf-8", errors="replace")
        version_cuda = int(pynvml.nvmlSystemGetCudaDriverVersion())
        cuda = f"{version_cuda // 1000}.{version_cuda % 1000 // 10}"
        return gpus, str(pilote), cuda
    except Exception:
        return [], None, None
    finally:
        try:
            pynvml.nvmlShutdown()
        except Exception:
            pass


def _paquets_installes() -> dict[str, str]:
    paquets: dict[str, str] = {}
    for distribution in metadata.distributions():
        nom = distribution.metadata["Name"]
        if not nom:
            continue
        paquets[re.sub(r"[-_.]+", "-", nom).lower()] = distribution.version
    return dict(sorted(paquets.items()))


def _git(racine: Path, *arguments: str) -> str | None:
    try:
        resultat = subprocess.run(
            ["git", *arguments],
            cwd=racine,
            env=env_sous_processus(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=DELAI_GIT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return resultat.stdout if resultat.returncode == 0 else None


def empreinte_environnement(racine: str | Path | None = None) -> Environnement:
    """Empreinte de la machine (OS, CPU, GPU, pilote, CUDA, paquets) et du dépôt `racine`.

    NVML absent ou en erreur : `gpus=[]`, `pilote_nvidia=None`, `cuda=None`. `racine` sans
    `.git`, `git` absent ou en échec : `git_commit=None`, `git_modifie=None`.
    """
    racine = Path(racine) if racine is not None else racine_projet()
    gpus, pilote, cuda = _gpus_nvml()
    git_commit: str | None = None
    git_modifie: bool | None = None
    if (racine / ".git").exists():
        sortie = _git(racine, "rev-parse", "HEAD")
        if sortie is not None and sortie.strip():
            git_commit = sortie.strip()
            etat = _git(racine, "status", "--porcelain", "--untracked-files=no")
            git_modifie = bool(etat.strip()) if etat is not None else None
    return Environnement(
        os=platform.platform(),
        machine=platform.machine(),
        cpu=platform.processor() or platform.machine(),
        nb_coeurs=os.cpu_count(),
        python=platform.python_version(),
        gpus=gpus,
        pilote_nvidia=pilote,
        cuda=cuda,
        paquets=_paquets_installes(),
        git_commit=git_commit,
        git_modifie=git_modifie,
    )


# --- Runs -----------------------------------------------------------------------------


def _maintenant() -> datetime:
    return datetime.now().astimezone()


def _ligne_etat(statut: Statut, motif: str | None) -> EtatRun:
    return EtatRun(horodatage=_maintenant(), statut=statut, pid=os.getpid(), motif=motif)


class Run:
    """Dossier de run ouvert : écritures exclusives, ajouts JSONL, statut en ajout."""

    def __init__(self, dossier: Path, manifeste: RunManifest) -> None:
        self.dossier = Path(dossier)
        self.manifeste = manifeste

    @property
    def run_id(self) -> str:
        return self.manifeste.run_id

    @property
    def type(self) -> str:
        return self.manifeste.type

    def __repr__(self) -> str:
        return f"Run({self.type}/{self.run_id})"

    def _chemin(self, nom: str) -> Path:
        relatif = Path(nom)
        if (
            not nom
            or not relatif.parts
            or relatif.is_absolute()
            or relatif.drive
            or relatif.root
            or any(partie in ("", ".", "..") for partie in relatif.parts)
            or any(partie.endswith((".", " ")) or ":" in partie for partie in relatif.parts)
        ):
            raise ValueError(f"nom de fichier hors du run refusé : {nom!r}")
        if _nom_normalise(relatif.parts[0]) in _NOMS_RESERVES:
            raise ValueError(f"{nom!r} est réservé au run (manifeste ou état)")
        chemin = self.dossier / relatif
        base = self.dossier.resolve()
        resolu = chemin.resolve()
        if not resolu.is_relative_to(base):
            raise ValueError(f"nom de fichier hors du run refusé : {nom!r}")
        if any(_egal(resolu, base / reserve) for reserve in _NOMS_RESERVES):
            raise ValueError(f"{nom!r} est réservé au run (manifeste ou état)")
        return chemin

    def ecrire(self, nom: str, contenu: bytes | bytearray | memoryview | str) -> Path:
        """Crée le fichier `nom` du run ; lève `ArtefactExistant` s'il existe déjà."""
        if not isinstance(contenu, (bytes, bytearray, memoryview, str)):
            raise TypeError(
                f"contenu attendu : bytes, bytearray, memoryview ou str (reçu {type(contenu)})"
            )
        chemin = self._chemin(nom)
        donnees = contenu.encode("utf-8") if isinstance(contenu, str) else bytes(contenu)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        try:
            with chemin.open("xb") as flux:
                flux.write(donnees)
        except FileExistsError:
            raise ArtefactExistant(
                f"{chemin} existe déjà : un artefact n'est jamais réécrit"
            ) from None
        return chemin

    def ajouter_jsonl(self, nom: str, obj: Any) -> None:
        """Ajoute `obj` en une ligne à la fin du fichier JSONL `nom` du run."""
        ajouter_jsonl(self._chemin(nom), obj)

    def lire_jsonl(self, nom: str) -> list[Any]:
        """Lignes JSON du fichier `nom` du run (fichier absent : liste vide)."""
        return _lire_lignes_jsonl(self._chemin(nom))

    def terminer(self, statut: str, motif: str | None = None) -> None:
        """Inscrit un statut final dans `etat.jsonl`, sans toucher à `run.json`."""
        if statut not in STATUTS_FINAUX:
            attendus = ", ".join(sorted(STATUTS_FINAUX))
            raise ValueError(f"statut de fin inconnu : {statut!r} (attendu : {attendus})")
        ajouter_jsonl(self.dossier / NOM_ETAT, _ligne_etat(statut, motif))

    def statut_courant(self) -> Statut:
        """Dernier statut valide d'`etat.jsonl` (celui de `run.json` si aucun)."""
        statut: Statut = self.manifeste.statut
        for ligne in _lire_lignes_jsonl(self.dossier / NOM_ETAT):
            try:
                statut = EtatRun.model_validate(ligne).statut
            except ValidationError:
                continue
        return statut


def _racine(racine: str | Path | None) -> Path:
    return (Path(racine) if racine is not None else racine_projet()).resolve()


def nouveau_run(
    type: str,
    slug: str,
    config: Mapping[str, Any],
    parents: Iterable[str] = (),
    entrees: Mapping[str, str | Path] | None = None,
    graine: int | None = None,
    *,
    racine: str | Path | None = None,
    **champs: Any,
) -> Run:
    """Crée `<racine>/runs/<type>/<run_id>/` avec `run.json` et une ligne `en_cours`.

    `entrees` associe un nom logique au chemin d'un fichier lu (relatif à `racine`), dont
    le SHA-256 est inscrit. `champs` reçoit les autres champs facultatifs de `RunManifest`
    (`modele_ref`, `quantification`, `jeu_version`, `couverture`…). Lève `ValueError` pour
    un type, un slug ou un champ invalide, `SlmspError` après `ESSAIS_RUN_ID` collisions.
    """
    if not isinstance(type, str) or not _MOTIF_TYPE.fullmatch(type):
        raise ValueError(f"type de run invalide : {type!r} (attendu : {MOTIF_TYPE})")
    if not isinstance(slug, str) or not _MOTIF_SLUG.fullmatch(slug):
        raise ValueError(f"slug invalide : {slug!r} (attendu : ^[a-z0-9.-]+$)")
    imposes = _CHAMPS_IMPOSES & champs.keys()
    if imposes:
        raise ValueError(f"champs fixés par nouveau_run : {', '.join(sorted(imposes))}")
    # JSON strict avant tout : NaN, infini ou objet non JSON lèvent ValueError ou TypeError.
    json_canonique(dict(config))
    if champs.get("couverture") is not None:
        json_canonique(champs["couverture"])
    racine = _racine(racine)
    empreintes = {
        nom: sha256_fichier(chemin if Path(chemin).is_absolute() else racine / chemin)
        for nom, chemin in (entrees or {}).items()
    }
    cree_le = _maintenant()

    def tirer_run_id() -> str:
        return f"{cree_le:%Y%m%d-%H%M%S}-{slug}-{secrets.token_hex(2)}"

    manifeste = RunManifest(
        type=type,
        run_id=tirer_run_id(),
        cree_le=cree_le,
        parents=list(parents),
        config=dict(config),
        graine=graine,
        environnement=empreinte_environnement(racine),
        entrees=empreintes,
        **champs,
    )

    dossier_type = racine / "runs" / type
    dossier_type.mkdir(parents=True, exist_ok=True)
    for _ in range(ESSAIS_RUN_ID):
        dossier = dossier_type / manifeste.run_id
        try:
            dossier.mkdir(exist_ok=False)
            break
        except FileExistsError:
            manifeste = manifeste.model_copy(update={"run_id": tirer_run_id()})
    else:
        raise SlmspError(
            f"impossible de créer un dossier de run unique sous {dossier_type} "
            f"après {ESSAIS_RUN_ID} essais"
        )
    contenu = json_canonique(manifeste.model_dump(mode="json")) + b"\n"
    with (dossier / NOM_MANIFESTE).open("xb") as flux:
        flux.write(contenu)
    ajouter_jsonl(dossier / NOM_ETAT, _ligne_etat("en_cours", None))
    return Run(dossier, manifeste)


def ouvrir_run(run_id: str, *, racine: str | Path | None = None) -> Run:
    """Ouvre le run `run_id` existant ; lève `ManifesteInvalide` s'il est absent ou invalide."""
    if not isinstance(run_id, str) or not _MOTIF_RUN_ID.fullmatch(run_id):
        raise ManifesteInvalide(f"run_id invalide : {run_id!r}")
    racine = _racine(racine)
    trouves = sorted((racine / "runs").glob(f"*/{run_id}/{NOM_MANIFESTE}"))
    if not trouves:
        raise ManifesteInvalide(f"run introuvable : {run_id} (sous {racine / 'runs'})")
    if len(trouves) > 1:
        raise ManifesteInvalide(f"run_id ambigu : {run_id} ({len(trouves)} dossiers)")
    chemin = trouves[0]
    try:
        with chemin.open("rb") as flux:
            manifeste = RunManifest.model_validate_json(flux.read())
    except (OSError, ValidationError) as exc:
        raise ManifesteInvalide(f"{chemin} : manifeste illisible ou invalide ({exc})") from None
    if manifeste.run_id != run_id or manifeste.type != chemin.parent.parent.name:
        raise ManifesteInvalide(f"{chemin} : run_id ou type incohérent avec le dossier")
    return Run(chemin.parent, manifeste)


def reprendre(
    run_id: str,
    *,
    fichier: str = "resultats.jsonl",
    cle: str = "cle",
    racine: str | Path | None = None,
) -> tuple[Run, set[str]]:
    """Reprend le run `run_id` en ajout seul (AD-26).

    Inscrit `en_cours` dans `etat.jsonl` et renvoie le run avec l'ensemble des valeurs de
    `cle` (en chaînes) déjà présentes dans `fichier` (absent : ensemble vide). Lève
    `SlmspError` si le run est `complet`, `ManifesteInvalide` s'il est introuvable.
    """
    run = ouvrir_run(run_id, racine=racine)
    if run.statut_courant() == "complet":
        raise SlmspError(f"run {run_id} déjà complet : rien à reprendre")
    run._chemin(fichier)  # ValueError avant toute écriture
    ajouter_jsonl(run.dossier / NOM_ETAT, _ligne_etat("en_cours", "reprise"))
    deja = {
        str(ligne[cle])
        for ligne in run.lire_jsonl(fichier)
        if isinstance(ligne, dict) and cle in ligne
    }
    return run, deja


# --- Lecteur contrôlé ---------------------------------------------------------------------


def _cle(chemin: Path) -> Path:
    return Path(os.path.normcase(str(chemin)))


def _sous(chemin: Path, base: Path) -> bool:
    return _cle(chemin).is_relative_to(_cle(base))


def _egal(chemin: Path, cible: Path) -> bool:
    return _cle(chemin) == _cle(cible)


def _premier_niveau_runs(chemin: Path, racine: Path) -> str | None:
    runs = (racine / "runs").resolve()
    if not _sous(chemin, runs) or _egal(chemin, runs):
        return None
    return _cle(chemin).relative_to(_cle(runs)).parts[0]


def chemin_autorise(chemin: str | Path, lecteur: str, *, racine: str | Path | None = None) -> Path:
    """Chemin résolu de `chemin` s'il est lisible par `lecteur` (AD-24).

    Un chemin relatif est résolu contre `racine` (défaut : racine du projet), puis liens et
    `..` sont résolus, ainsi que chaque base de comparaison (une jonction `data/raw` vers le
    dépôt principal reste lisible). Refus explicite d'abord (`eval/`, `runs/eval/`,
    `runs/eval-*`, cache des verdicts), puis liste d'accès du lecteur. Lève `ValueError`
    pour un lecteur inconnu et `LectureInterdite` (message citant le chemin résolu et le
    lecteur) sinon.
    """
    if lecteur not in LECTEURS:
        raise ValueError(f"lecteur inconnu : {lecteur!r} (attendu : {', '.join(LECTEURS)})")
    racine = _racine(racine)
    brut = Path(chemin)
    resolu = (brut if brut.is_absolute() else racine / brut).resolve()
    var = dossier_var()
    journal = (var / NOM_JOURNAL_MISTRAL).resolve()

    def refuser(raison: str) -> LectureInterdite:
        return LectureInterdite(f"lecture interdite au lecteur « {lecteur} » : {resolu} ({raison})")

    def base(relatif: str) -> Path:
        return (racine / relatif).resolve()

    niveau_runs = _premier_niveau_runs(resolu, racine)
    if _sous(resolu, base("eval")):
        raise refuser("Jeu d'évaluation")
    if niveau_runs is not None and (niveau_runs == "eval" or niveau_runs.startswith("eval-")):
        raise refuser("run d'évaluation")
    if _egal(resolu, (var / NOM_CACHE_VERDICTS).resolve()):
        raise refuser("cache des verdicts")

    if lecteur == "data":
        autorise = (
            any(
                _sous(resolu, base(sous))
                for sous in ("data/raw", "data/cassettes", "config/prompts", "index")
            )
            or (niveau_runs is not None and niveau_runs.startswith("data-"))
            or _egal(resolu, base("config/outils-mcp.toml"))
            or _egal(resolu, base("data/registre-licences.toml"))
            or _egal(resolu, journal)
        )
    else:
        autorise = (
            _sous(resolu, base("data/train"))
            or _sous(resolu, dossier_modeles().resolve())
            or _egal(resolu, journal)
            or _egal(resolu, (var / NOM_JOURNAL_LOCAL).resolve())
        )
    if not autorise:
        raise refuser("hors de la liste d'accès")
    return resolu


def lire(chemin: str | Path, lecteur: str, *, racine: str | Path | None = None) -> bytes:
    """Octets du fichier `chemin` si `lecteur` y a droit (voir `chemin_autorise`)."""
    with chemin_autorise(chemin, lecteur, racine=racine).open("rb") as flux:
        return flux.read()


def lire_texte(
    chemin: str | Path,
    lecteur: str,
    *,
    racine: str | Path | None = None,
    encodage: str = "utf-8",
) -> str:
    """Texte du fichier `chemin` (UTF-8 par défaut) si `lecteur` y a droit."""
    return lire(chemin, lecteur, racine=racine).decode(encodage)


def ouvrir_sqlite_lecture(
    chemin: str | Path, lecteur: str, *, racine: str | Path | None = None
) -> sqlite3.Connection:
    """Ouvre la base `chemin` en lecture seule (URI `mode=ro`) si `lecteur` y a droit."""
    resolu = chemin_autorise(chemin, lecteur, racine=racine)
    connexion = sqlite3.connect(
        f"{resolu.as_uri()}?mode=ro", uri=True, timeout=BUSY_TIMEOUT_MS / 1000
    )
    try:
        connexion.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
    except BaseException:
        connexion.close()
        raise
    return connexion


# --- Espace disque ----------------------------------------------------------------------


def verifier_espace(
    chemin: str | Path, octets: int, *, seuil_octets: int = SEUIL_ESPACE_LIBRE
) -> int:
    """Vérifie qu'il reste `octets + seuil_octets` libres là où `chemin` sera écrit.

    Mesure le premier parent existant de `chemin`. Renvoie l'espace libre en octets ; lève
    `EspaceInsuffisant` (libre, demandé et seuil cités) sinon.
    """
    if octets < 0 or seuil_octets < 0:
        raise ValueError("octets et seuil_octets doivent être positifs ou nuls")
    cible = Path(chemin).absolute()
    while not cible.exists() and cible.parent != cible:
        cible = cible.parent
    libre = shutil.disk_usage(cible).free
    if libre < octets + seuil_octets:
        raise EspaceInsuffisant(
            f"espace disque insuffisant sous {cible} : {libre} octets libres, "
            f"{octets} octets demandés, seuil de {seuil_octets} octets"
        )
    return libre


__all__ = [
    "ArtefactExistant",
    "EspaceInsuffisant",
    "Run",
    "SEUIL_ESPACE_LIBRE",
    "ajouter_jsonl",
    "chemin_autorise",
    "empreinte_environnement",
    "lire",
    "lire_texte",
    "nouveau_run",
    "ouvrir_run",
    "ouvrir_sqlite_lecture",
    "reprendre",
    "verifier_espace",
]
