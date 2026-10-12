"""Sous-processus gérés : Job Object, registre `pids/` et nettoyage des orphelins (AD-27).

Tout sous-processus de `slmsp.inference` (llama-server, llama-quantize, conversion) est
lancé par `lancer` ou `executer` :

- environnement `env_sous_processus()` par défaut (aucun secret) ;
- `CREATE_NO_WINDOW`, et sortie redirigée vers un fichier (jamais un tube non lu) ;
- créé suspendu, assigné à un Job Object `KILL_ON_JOB_CLOSE`, puis repris : aucune
  fenêtre de course où l'enfant (ou ses propres enfants) échapperait au job. Le handle du
  job n'est pas héritable et seul ce processus le détient : sa fermeture (par `arreter`,
  ou par la mort de ce processus) tue tout l'arbre ;
- inscrit dans `SLMSP_VAR_DIR/pids/<pid>.json` (`EntreePid`) jusqu'à son arrêt.

Identité d'un processus du registre : PID et date de création (psutil). Un PID recyclé
n'est donc jamais tué. `nettoyer_orphelins` tue une entrée vivante dont le parent est mort
(cas d'un parent tué hors Windows, ou d'un job qui n'aurait pas pu être fermé), retire les
entrées dont le processus a disparu, et consigne chaque action dans `pids/nettoyage.jsonl`.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import IO, Any, Final

import psutil

from slmsp.core.artefacts import ajouter_jsonl
from slmsp.core.config import env_sous_processus
from slmsp.core.erreurs import SlmspError
from slmsp.core.var import dossier_var

WINDOWS: Final = sys.platform == "win32"

CREATE_NO_WINDOW: Final = 0x08000000
CREATE_SUSPENDED: Final = 0x00000004
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE: Final = 0x00002000
_JOB_OBJECT_EXTENDED_LIMIT_INFORMATION: Final = 9

NOM_PIDS: Final = "pids"
NOM_NETTOYAGE: Final = "nettoyage.jsonl"

DELAI_ARRET: Final = 10.0
"""Attente maximale de la fin d'un processus après sa terminaison (secondes)."""

TOLERANCE_CREATION: Final = 0.01
"""Écart maximal entre deux lectures de la date de création d'un même processus (s)."""

TAILLE_FIN_JOURNAL: Final = 4000
"""Nombre de caractères de fin de journal cités dans un message d'erreur."""


class ErreurInference(SlmspError):
    """Échec d'un processus llama.cpp ou d'une requête au serveur (statut, extrait)."""


# --- Job Object (Windows) -------------------------------------------------------------------


def _kernel32() -> Any:
    import ctypes
    from ctypes import wintypes

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    k32.CreateJobObjectW.restype = wintypes.HANDLE
    k32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
    ]
    k32.SetInformationJobObject.restype = wintypes.BOOL
    k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    k32.AssignProcessToJobObject.restype = wintypes.BOOL
    k32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    k32.TerminateJobObject.restype = wintypes.BOOL
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    k32.CloseHandle.restype = wintypes.BOOL
    return k32


def _ntdll() -> Any:
    import ctypes
    from ctypes import wintypes

    nt = ctypes.WinDLL("ntdll")
    nt.NtResumeProcess.argtypes = [wintypes.HANDLE]
    nt.NtResumeProcess.restype = ctypes.c_long
    return nt


def _erreur_windows(fonction: str) -> OSError:
    import ctypes

    code = ctypes.get_last_error()
    return OSError(code, f"{fonction} a échoué : {ctypes.FormatError(code).strip()}")


def _structure_limites() -> Any:
    import ctypes
    from ctypes import wintypes

    class LimitesBase(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class CompteursIo(ctypes.Structure):
        _fields_ = [
            (nom, ctypes.c_uint64)
            for nom in (
                "ReadOperationCount",
                "WriteOperationCount",
                "OtherOperationCount",
                "ReadTransferCount",
                "WriteTransferCount",
                "OtherTransferCount",
            )
        ]

    class LimitesEtendues(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", LimitesBase),
            ("IoInfo", CompteursIo),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    return LimitesEtendues


class JobObject:
    """Job Object anonyme `KILL_ON_JOB_CLOSE` (handle non héritable)."""

    def __init__(self) -> None:
        import ctypes

        self._k32 = _kernel32()
        handle = self._k32.CreateJobObjectW(None, None)
        if not handle:
            raise _erreur_windows("CreateJobObjectW")
        self._handle: int | None = handle
        limites = _structure_limites()()
        limites.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self._k32.SetInformationJobObject(
            handle,
            _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limites),
            ctypes.sizeof(limites),
        ):
            erreur = _erreur_windows("SetInformationJobObject")
            self.fermer()
            raise erreur

    @property
    def ouvert(self) -> bool:
        return self._handle is not None

    def assigner(self, handle_processus: int) -> None:
        """Assigne le processus (handle) au job ; lève `OSError` en cas d'échec."""
        if self._handle is None:
            raise ValueError("Job Object déjà fermé")
        if not self._k32.AssignProcessToJobObject(self._handle, int(handle_processus)):
            raise _erreur_windows("AssignProcessToJobObject")

    def terminer(self, code: int = 1) -> None:
        """Termine tous les processus du job (le job reste ouvert)."""
        if self._handle is not None:
            self._k32.TerminateJobObject(self._handle, code)

    def fermer(self) -> None:
        """Ferme le handle : les processus encore dans le job sont tués."""
        if self._handle is not None:
            handle, self._handle = self._handle, None
            self._k32.CloseHandle(handle)


def reprendre_processus(handle_processus: int) -> None:
    """Reprend un processus créé suspendu (`NtResumeProcess`)."""
    statut = _ntdll().NtResumeProcess(int(handle_processus))
    if statut != 0:
        raise OSError(f"NtResumeProcess a échoué (NTSTATUS 0x{statut & 0xFFFFFFFF:08X})")


# --- Registre pids/ -------------------------------------------------------------------------


@dataclass(frozen=True)
class EntreePid:
    """Entrée `pids/<pid>.json` : processus lancé, son port et son parent."""

    pid: int
    port: int | None
    role: str
    parent_pid: int
    parent_creation: float
    creation: float
    commande: list[str] = field(default_factory=list)
    demarre_le: str = ""

    @classmethod
    def depuis_dict(cls, donnees: Any) -> EntreePid:
        """Relit une entrée ; lève `ValueError` si elle est incomplète ou mal typée."""
        if not isinstance(donnees, dict):
            raise ValueError("entrée pids/ : objet JSON attendu")
        try:
            entree = cls(
                pid=donnees["pid"],
                port=donnees.get("port"),
                role=donnees["role"],
                parent_pid=donnees["parent_pid"],
                parent_creation=donnees["parent_creation"],
                creation=donnees["creation"],
                commande=list(donnees.get("commande") or []),
                demarre_le=str(donnees.get("demarre_le") or ""),
            )
        except (KeyError, TypeError) as exc:
            raise ValueError(f"entrée pids/ incomplète : {exc}") from None
        entiers = (entree.pid, entree.parent_pid)
        if not all(isinstance(v, int) and not isinstance(v, bool) for v in entiers):
            raise ValueError("entrée pids/ : pid et parent_pid entiers attendus")
        if not all(isinstance(v, int | float) for v in (entree.creation, entree.parent_creation)):
            raise ValueError("entrée pids/ : dates de création numériques attendues")
        return entree


def dossier_pids() -> Path:
    """`SLMSP_VAR_DIR/pids/`, créé s'il manque."""
    dossier = dossier_var() / NOM_PIDS
    dossier.mkdir(parents=True, exist_ok=True)
    return dossier


def chemin_entree(pid: int) -> Path:
    return dossier_pids() / f"{pid}.json"


def inscrire(entree: EntreePid) -> Path:
    """Écrit `pids/<pid>.json` par remplacement atomique (jamais lu à moitié écrit)."""
    chemin = chemin_entree(entree.pid)
    temporaire = chemin.with_name(f"{chemin.name}.{os.getpid()}.tmp")
    temporaire.write_text(json.dumps(asdict(entree), ensure_ascii=False), encoding="utf-8")
    os.replace(temporaire, chemin)
    return chemin


def _retirer(chemin: Path) -> None:
    try:
        chemin.unlink(missing_ok=True)
    except OSError:
        pass  # entrée en cours de remplacement : le prochain nettoyage la traitera


def _date_creation(pid: int) -> float:
    return psutil.Process(pid).create_time()


_creation_courante: float | None = None


def _creation_de_ce_processus() -> float:
    global _creation_courante
    if _creation_courante is None:
        _creation_courante = _date_creation(os.getpid())
    return _creation_courante


def processus_identique(pid: int, creation: float) -> psutil.Process | None:
    """Le processus `pid` s'il vit encore avec la même date de création, sinon `None`."""
    try:
        processus = psutil.Process(pid)
        if abs(processus.create_time() - creation) > TOLERANCE_CREATION:
            return None
        if processus.status() == psutil.STATUS_ZOMBIE:
            return None
    except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
        return None
    return processus


def _tuer_arbre(processus: psutil.Process, delai: float = DELAI_ARRET) -> None:
    try:
        descendants = processus.children(recursive=True)
    except psutil.Error:
        descendants = []
    cibles = [processus, *descendants]
    for cible in cibles:
        try:
            cible.kill()
        except psutil.Error:
            pass
    psutil.wait_procs(cibles, timeout=delai)


def _maintenant() -> str:
    return datetime.now().astimezone().isoformat()


def nettoyer_orphelins() -> list[dict[str, Any]]:
    """Traite le registre `pids/` et renvoie les lignes consignées dans `nettoyage.jsonl`.

    - processus disparu (ou PID recyclé) : entrée retirée, action `disparu` ;
    - processus vivant dont le parent est mort : arbre tué, entrée retirée, `arrete` ;
    - entrée illisible : retirée, `illisible` ;
    - processus vivant dont le parent vit : laissé tel quel (rien n'est consigné).
    """
    dossier = dossier_pids()
    lignes: list[dict[str, Any]] = []
    for chemin in sorted(dossier.glob("*.json")):
        try:
            brut = chemin.read_text(encoding="utf-8")
        except OSError:
            continue  # disparu ou remplacé entre-temps
        entree: EntreePid | None
        try:
            entree = EntreePid.depuis_dict(json.loads(brut))
        except ValueError:
            entree, action = None, "illisible"
        else:
            enfant = processus_identique(entree.pid, entree.creation)
            if enfant is None:
                action = "disparu"
            elif processus_identique(entree.parent_pid, entree.parent_creation) is not None:
                continue
            else:
                _tuer_arbre(enfant)
                action = "arrete"
        ligne = {
            "horodatage": _maintenant(),
            "action": action,
            "fichier": chemin.name,
            "entree": asdict(entree) if entree is not None else None,
        }
        _retirer(chemin)
        ajouter_jsonl(dossier / NOM_NETTOYAGE, ligne)
        lignes.append(ligne)
    return lignes


# --- Lancement ------------------------------------------------------------------------------


class ProcessusGere:
    """Sous-processus lancé par `lancer` : job, entrée `pids/` et journal."""

    def __init__(
        self,
        popen: subprocess.Popen[bytes],
        job: JobObject | None,
        entree: EntreePid,
        chemin_entree: Path,
        journal: Path | None,
    ) -> None:
        self.popen = popen
        self.job = job
        self.entree = entree
        self.chemin_entree = chemin_entree
        self.journal = journal
        self._arrete = False

    def __repr__(self) -> str:
        return f"ProcessusGere(pid={self.pid}, role={self.entree.role!r}, vivant={self.vivant})"

    @property
    def pid(self) -> int:
        return self.popen.pid

    @property
    def vivant(self) -> bool:
        return self.popen.poll() is None

    @property
    def code_retour(self) -> int | None:
        return self.popen.poll()

    def attendre(self, delai: float | None = None) -> int | None:
        """Attend la fin du processus ; renvoie son code, ou `None` si `delai` expire."""
        try:
            return self.popen.wait(timeout=delai)
        except subprocess.TimeoutExpired:
            return None

    def arreter(self, delai: float = DELAI_ARRET) -> int | None:
        """Tue l'arbre du processus, ferme le job et retire l'entrée `pids/` (idempotent)."""
        if self._arrete:
            return self.popen.returncode
        try:
            if self.vivant:
                if self.job is not None:
                    self.job.terminer()
                else:
                    self.popen.terminate()
                if self.attendre(delai) is None:
                    self.popen.kill()
                    self.attendre(delai)
        finally:
            if self.job is not None:
                self.job.fermer()
            _retirer(self.chemin_entree)
            self._arrete = True
        return self.popen.returncode


def _lancer(
    arguments: Sequence[str | os.PathLike[str]],
    sortie: IO[bytes],
    *,
    role: str,
    port: int | None,
    journal: Path | None,
    env: Mapping[str, str] | None,
    cwd: str | os.PathLike[str] | None,
) -> ProcessusGere:
    commande = [os.fspath(argument) for argument in arguments]
    if not commande:
        raise ValueError("commande vide")
    environnement = env_sous_processus() if env is None else dict(env)
    drapeaux = CREATE_NO_WINDOW | CREATE_SUSPENDED if WINDOWS else 0
    popen = subprocess.Popen(
        commande,
        stdin=subprocess.DEVNULL,
        stdout=sortie,
        stderr=subprocess.STDOUT,
        env=environnement,
        cwd=cwd,
        creationflags=drapeaux,
        close_fds=True,
    )
    job: JobObject | None = None
    chemin: Path | None = None
    try:
        if WINDOWS:
            job = JobObject()
            job.assigner(popen._handle)  # type: ignore[attr-defined]
        entree = EntreePid(
            pid=popen.pid,
            port=port,
            role=role,
            parent_pid=os.getpid(),
            parent_creation=_creation_de_ce_processus(),
            creation=_date_creation(popen.pid),
            commande=commande,
            demarre_le=_maintenant(),
        )
        chemin = inscrire(entree)
        if WINDOWS:
            reprendre_processus(popen._handle)  # type: ignore[attr-defined]
    except BaseException:
        popen.kill()
        popen.wait()
        if job is not None:
            job.fermer()
        if chemin is not None:
            _retirer(chemin)
        raise
    return ProcessusGere(popen, job, entree, chemin, journal)


def lancer(
    arguments: Sequence[str | os.PathLike[str]],
    *,
    role: str,
    port: int | None = None,
    journal: str | os.PathLike[str],
    env: Mapping[str, str] | None = None,
    cwd: str | os.PathLike[str] | None = None,
) -> ProcessusGere:
    """Lance `arguments` dans un Job Object, sortie (stdout et stderr) ajoutée à `journal`.

    `env` vaut `env_sous_processus()` par défaut. Le processus est inscrit dans `pids/`
    avec `role` et `port` jusqu'à `arreter`.
    """
    chemin_journal = Path(journal)
    chemin_journal.parent.mkdir(parents=True, exist_ok=True)
    with chemin_journal.open("ab") as sortie:
        return _lancer(
            arguments, sortie, role=role, port=port, journal=chemin_journal, env=env, cwd=cwd
        )


def lire_fin(chemin: str | os.PathLike[str], caracteres: int = TAILLE_FIN_JOURNAL) -> str:
    """Fin du fichier `chemin` (texte UTF-8, erreurs remplacées) ; vide s'il est illisible."""
    try:
        with Path(chemin).open("rb") as flux:
            flux.seek(0, os.SEEK_END)
            taille = flux.tell()
            flux.seek(max(0, taille - caracteres * 4))
            texte = flux.read().decode("utf-8", errors="replace")
    except OSError:
        return ""
    return texte[-caracteres:]


def executer(
    arguments: Sequence[str | os.PathLike[str]],
    *,
    delai: float | None = None,
    role: str = "commande",
    journal: str | os.PathLike[str] | None = None,
    env: Mapping[str, str] | None = None,
    cwd: str | os.PathLike[str] | None = None,
) -> tuple[int, str]:
    """Exécute `arguments` jusqu'à sa fin et renvoie `(code, sortie)`.

    Même cadre que `lancer` (job, `pids/`, `env_sous_processus()`). La sortie va dans
    `journal` (ajout) s'il est donné, sinon dans un fichier temporaire ; `sortie` est le
    texte écrit pendant cette exécution. `delai` dépassé : l'arbre est tué et
    `ErreurInference` est levée avec la fin de la sortie.
    """
    if journal is not None:
        Path(journal).parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile() if journal is None else Path(journal).open("a+b") as flux:
        flux.seek(0, os.SEEK_END)
        debut = flux.tell()
        processus = _lancer(
            arguments,
            flux,
            role=role,
            port=None,
            journal=None if journal is None else Path(journal),
            env=env,
            cwd=cwd,
        )
        try:
            code = processus.attendre(delai)
        finally:
            processus.arreter()
        flux.seek(debut)
        sortie = flux.read().decode("utf-8", errors="replace")
    if code is None:
        raise ErreurInference(
            f"{Path(os.fspath(arguments[0])).name} : délai de {delai:g} s dépassé, "
            f"processus arrêté ; fin de la sortie :\n{sortie[-TAILLE_FIN_JOURNAL:]}"
        )
    return code, sortie


__all__ = [
    "CREATE_NO_WINDOW",
    "DELAI_ARRET",
    "EntreePid",
    "ErreurInference",
    "JobObject",
    "ProcessusGere",
    "chemin_entree",
    "dossier_pids",
    "executer",
    "inscrire",
    "lancer",
    "lire_fin",
    "nettoyer_orphelins",
    "processus_identique",
]
