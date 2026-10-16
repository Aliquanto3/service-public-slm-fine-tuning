"""État partagé de la machine : `SLMSP_VAR_DIR`, SQLite et verrou GPU (AD-27, D-nuit-A2-8).

`SLMSP_VAR_DIR` (défaut `%LOCALAPPDATA%\\slmsp\\var\\`) est hors dépôt et unique par
machine, partagé par toutes les copies de travail. Aucune fonction de ce module ne
supprime un fichier.

Verrou GPU : `gpu.lock` est permanent. Le détenteur verrouille un octet à l'offset
`OFFSET_VERROU` (hors du contenu) par un verrou d'octets du système (`msvcrt.locking`
sous Windows, `fcntl.lockf` ailleurs) et réécrit en tête le JSON `pid`, `commande`,
`depuis`, lu par les candidats refusés. Le système libère le verrou à la mort du
détenteur : un PID mort est récupéré sans nettoyage.
"""

from __future__ import annotations

import errno
import json
import os
import sqlite3
import sys
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import RessourceOccupee, SlmspError

BUSY_TIMEOUT_MS = 30_000
"""`busy_timeout` de toutes les bases SQLite (AD-27)."""

NOM_VERROU_GPU = "gpu.lock"
OFFSET_VERROU = 1024 * 1024
"""Octet verrouillé dans `gpu.lock`, au-delà du contenu (1 Mio)."""

INTERVALLE_ATTENTE = 0.1
"""Pause entre deux tentatives quand `verrou_gpu(attendre=True)` (secondes)."""

_TAILLE_LECTURE = 8192
_LONGUEUR_COMMANDE = 1000  # 1000 caractères UTF-8 (4 octets au plus) tiennent en lecture
_ERRNOS_OCCUPE = {errno.EACCES, errno.EAGAIN, errno.EDEADLK}

# Ré-entrée refusée dans le processus : sous Windows, un second handle attendrait sans fin ;
# ailleurs, `fcntl` accepterait puis la fermeture interne lâcherait le verrou externe.
_garde_processus = threading.Lock()
_detenu_par_ce_processus = False


def dossier_var() -> Path:
    """Dossier `SLMSP_VAR_DIR`, sinon `%LOCALAPPDATA%\\slmsp\\var` ; créé s'il manque."""
    valeur = os.environ.get("SLMSP_VAR_DIR", "").strip()
    if valeur:
        dossier = Path(valeur)
    else:
        local = os.environ.get("LOCALAPPDATA", "").strip()
        base = Path(local) if local else Path.home() / "AppData" / "Local"
        dossier = base / "slmsp" / "var"
    dossier.mkdir(parents=True, exist_ok=True)
    return dossier.resolve()


def _activer_wal(connexion: sqlite3.Connection) -> str:
    """Passe en WAL ; le basculement concurrent ignore `busy_timeout` : on réessaie.

    Deux processus qui ouvrent une base neuve en même temps peuvent recevoir
    `database is locked` immédiatement sur ce PRAGMA. Une fois la base en WAL,
    le PRAGMA est un no-op ; la nouvelle tentative suffit donc.
    """
    fin = time.monotonic() + BUSY_TIMEOUT_MS / 1000
    while True:
        try:
            (mode,) = connexion.execute("PRAGMA journal_mode = WAL").fetchone()
            return str(mode)
        except sqlite3.OperationalError as exc:
            if "locked" not in str(exc) and "busy" not in str(exc):
                raise
            if time.monotonic() >= fin:
                raise
            time.sleep(0.01)


def ouvrir_sqlite(chemin: str | Path) -> sqlite3.Connection:
    """Ouvre la base `chemin` en mode WAL avec un `busy_timeout` de 30 000 ms."""
    chemin = Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    connexion = sqlite3.connect(chemin, timeout=BUSY_TIMEOUT_MS / 1000)
    try:
        connexion.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
        mode = _activer_wal(connexion)
        if str(mode).lower() != "wal":
            raise SlmspError(f"{chemin} : mode WAL refusé par SQLite (mode {mode})")
    except BaseException:
        connexion.close()
        raise
    return connexion


if sys.platform == "win32":
    import msvcrt

    def _verrouiller(fd: int) -> bool:
        os.lseek(fd, OFFSET_VERROU, os.SEEK_SET)
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            if exc.errno in _ERRNOS_OCCUPE:
                return False
            raise
        return True

    def _deverrouiller(fd: int) -> None:
        os.lseek(fd, OFFSET_VERROU, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)

else:
    import fcntl

    def _verrouiller(fd: int) -> bool:
        try:
            fcntl.lockf(fd, fcntl.LOCK_EX | fcntl.LOCK_NB, 1, OFFSET_VERROU, os.SEEK_SET)
        except OSError as exc:
            if exc.errno in _ERRNOS_OCCUPE:
                return False
            raise
        return True

    def _deverrouiller(fd: int) -> None:
        fcntl.lockf(fd, fcntl.LOCK_UN, 1, OFFSET_VERROU, os.SEEK_SET)


def _lire_detenteur(fd: int) -> tuple[int | None, str | None]:
    os.lseek(fd, 0, os.SEEK_SET)
    brut = os.read(fd, _TAILLE_LECTURE)
    try:
        contenu = json.loads(brut.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, None  # contenu en cours d'écriture ou absent
    if not isinstance(contenu, dict):
        return None, None
    pid = contenu.get("pid")
    commande = contenu.get("commande")
    return (
        pid if isinstance(pid, int) else None,
        commande if isinstance(commande, str) else None,
    )


def _ecrire_detenteur(fd: int, commande: str) -> None:
    contenu = json_canonique(
        {
            "pid": os.getpid(),
            "commande": commande[:_LONGUEUR_COMMANDE],
            "depuis": datetime.now().astimezone().isoformat(),
        }
    )
    os.ftruncate(fd, 0)
    os.lseek(fd, 0, os.SEEK_SET)
    os.write(fd, contenu)
    os.fsync(fd)


def _occupe(chemin: Path, fd: int, delai: float | None) -> RessourceOccupee:
    pid, commande = _lire_detenteur(fd)
    detenteur = f"PID {pid}" if pid is not None else "détenteur inconnu"
    if commande:
        detenteur += f" ({commande})"
    message = f"GPU occupé : verrou {chemin} détenu par {detenteur}"
    if delai is not None:
        message += f" ; délai d'attente de {delai:g} s dépassé"
    return RessourceOccupee(message, pid=pid, commande=commande)


@contextmanager
def verrou_gpu(
    attendre: bool = False, delai: float | None = None, commande: str | None = None
) -> Iterator[Path]:
    """Prend le verrou exclusif `gpu.lock` de `SLMSP_VAR_DIR` pour la durée du bloc.

    Sans attente, lève aussitôt `RessourceOccupee` (avec le PID et la commande du
    détenteur) si le verrou est pris. Avec attente, réessaie jusqu'à la libération, ou
    jusqu'à `delai` secondes (`None` : sans limite) puis lève `RessourceOccupee`.
    `commande` est inscrite dans le verrou (défaut : la ligne de commande courante).
    Renvoie le chemin du fichier de verrou. Une seconde demande dans le même processus,
    pendant que le verrou est détenu, lève aussitôt `RessourceOccupee` (sans attente).
    """
    global _detenu_par_ce_processus
    chemin = dossier_var() / NOM_VERROU_GPU
    with _garde_processus:
        if _detenu_par_ce_processus:
            raise RessourceOccupee(
                f"GPU occupé : verrou {chemin} déjà détenu par ce processus (PID {os.getpid()})",
                pid=os.getpid(),
            )
        _detenu_par_ce_processus = True
    try:
        drapeaux = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0)
        fd = os.open(chemin, drapeaux, 0o666)
        try:
            echeance = None if delai is None else time.monotonic() + delai
            while not _verrouiller(fd):
                if not attendre or (echeance is not None and time.monotonic() >= echeance):
                    raise _occupe(chemin, fd, delai if attendre else None)
                time.sleep(INTERVALLE_ATTENTE)
            try:
                _ecrire_detenteur(fd, commande or " ".join(sys.argv))
                yield chemin
            finally:
                _deverrouiller(fd)
        finally:
            os.close(fd)
    finally:
        with _garde_processus:
            _detenu_par_ce_processus = False
