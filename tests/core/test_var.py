"""`SLMSP_VAR_DIR`, SQLite et verrou GPU (critères 6 à 8, story 1.2).

Le verrou GPU est éprouvé contre un second processus Python réel (`sys.executable`).
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import psutil
import pytest

import slmsp.core.var as module_var
from slmsp.core.erreurs import CodeSortie, RessourceOccupee, SlmspError
from slmsp.core.var import dossier_var, ouvrir_sqlite, verrou_gpu

COMMANDE_DETENTEUR = "slmsp-test detenteur"

# Le processus détenteur prend le verrou, annonce son PID puis attend une ligne sur stdin.
SCRIPT_DETENTEUR = f"""
import os, sys
from slmsp.core.var import verrou_gpu
with verrou_gpu(commande={COMMANDE_DETENTEUR!r}):
    print("pret", os.getpid(), flush=True)
    sys.stdin.readline()
print("libere", flush=True)
"""


# --- dossier_var --------------------------------------------------------------------------


def test_dossier_var_par_defaut(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SLMSP_VAR_DIR", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))
    dossier = dossier_var()
    assert dossier == (tmp_path / "Local" / "slmsp" / "var").resolve()
    assert dossier.is_dir()


def test_dossier_var_variable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cible = tmp_path / "partage" / "var"
    monkeypatch.setenv("SLMSP_VAR_DIR", str(cible))
    assert dossier_var() == cible.resolve()
    assert cible.is_dir()
    assert dossier_var() == cible.resolve()  # idempotent


def test_var_ne_supprime_aucun_fichier() -> None:
    interdits = {"unlink", "remove", "rmtree", "rmdir", "removedirs"}
    arbre = ast.parse(Path(module_var.__file__).read_text(encoding="utf-8"))
    appels = []
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Call):
            fonction = noeud.func
            nom = fonction.attr if isinstance(fonction, ast.Attribute) else None
            if isinstance(fonction, ast.Name):
                nom = fonction.id
            if nom in interdits:
                appels.append(f"ligne {noeud.lineno} : {nom}")
    assert appels == []


# --- SQLite -------------------------------------------------------------------------------


def test_ouvrir_sqlite_wal_et_busy_timeout(tmp_path: Path) -> None:
    chemin = tmp_path / "sous-dossier" / "base.sqlite"
    connexion = ouvrir_sqlite(chemin)
    try:
        assert connexion.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        assert connexion.execute("PRAGMA busy_timeout").fetchone()[0] == 30_000
        connexion.execute("CREATE TABLE t (x INTEGER)")
        connexion.commit()
    finally:
        connexion.close()
    # Une seconde ouverture retrouve le mode WAL et fixe à nouveau le délai.
    connexion = ouvrir_sqlite(str(chemin))
    try:
        assert connexion.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        assert connexion.execute("PRAGMA busy_timeout").fetchone()[0] == 30_000
    finally:
        connexion.close()


def test_ouvrir_sqlite_wal_refuse() -> None:
    with pytest.raises(SlmspError, match="WAL"):
        ouvrir_sqlite(":memory:")


# --- verrou GPU : même processus ------------------------------------------------------------


@pytest.mark.parametrize("attendre", [False, True])
def test_verrou_gpu_reentree_refusee(attendre: bool) -> None:
    with verrou_gpu(commande="externe") as chemin:
        debut = time.monotonic()
        with pytest.raises(RessourceOccupee, match="ce processus") as info:
            with verrou_gpu(attendre=attendre, delai=None):
                pytest.fail("ré-entrée acceptée")
        assert time.monotonic() - debut < 2
        assert info.value.pid == os.getpid()
        # Le verrou externe tient toujours : le contenu n'a pas été réécrit.
        contenu = json.loads(chemin.read_bytes()[:4096].decode("utf-8"))
        assert contenu["commande"] == "externe"
    with verrou_gpu():  # le drapeau est remis à zéro à la libération
        pass


def test_verrou_gpu_commande_longue_tronquee() -> None:
    with verrou_gpu(commande="é" * 5000) as chemin:
        contenu = json.loads(chemin.read_bytes().decode("utf-8"))
    assert contenu["commande"] == "é" * 1000


def test_verrou_gpu_contenu_et_fichier_permanent() -> None:
    with verrou_gpu(commande="slmsp train test") as chemin:
        assert chemin == dossier_var() / "gpu.lock"
        contenu = json.loads(chemin.read_bytes()[:4096].decode("utf-8"))
        assert contenu["pid"] == os.getpid()
        assert contenu["commande"] == "slmsp train test"
        assert "T" in contenu["depuis"]
    assert chemin.is_file()  # jamais supprimé
    with verrou_gpu():  # reprise après libération
        pass
    assert chemin.is_file()


def test_verrou_gpu_fichier_residuel_recupere() -> None:
    """Un `gpu.lock` laissé par un PID mort, sans verrou d'octets, est récupéré aussitôt."""
    chemin = dossier_var() / "gpu.lock"
    chemin.write_bytes(json.dumps({"pid": 999_999_999, "commande": "ancien"}).encode())
    debut = time.monotonic()
    with verrou_gpu(commande="nouveau"):
        contenu = json.loads(chemin.read_bytes()[:4096].decode("utf-8"))
    assert time.monotonic() - debut < 2
    assert (contenu["pid"], contenu["commande"]) == (os.getpid(), "nouveau")


# --- verrou GPU : second processus ----------------------------------------------------------


class Detenteur:
    def __init__(self) -> None:
        self.processus = subprocess.Popen(
            [sys.executable, "-c", SCRIPT_DETENTEUR],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            env=dict(os.environ),  # même SLMSP_VAR_DIR que le test
        )
        ligne = self.processus.stdout.readline() if self.processus.stdout else ""
        if not ligne.startswith("pret "):
            erreur = self.processus.stderr.read() if self.processus.stderr else ""
            raise AssertionError(f"le détenteur n'a pas pris le verrou : {ligne!r} {erreur}")
        self.pid = int(ligne.split()[1])

    def liberer(self) -> None:
        if self.processus.poll() is None and self.processus.stdin:
            self.processus.stdin.write("fin\n")
            self.processus.stdin.flush()

    def tuer(self) -> None:
        try:
            interpreteur = psutil.Process(self.pid)
            interpreteur.kill()
            interpreteur.wait(timeout=10)
        except psutil.NoSuchProcess:
            pass
        self.processus.kill()
        self.processus.wait(timeout=10)

    def fermer(self) -> None:
        try:
            self.liberer()
            self.processus.communicate(timeout=10)
        except (subprocess.TimeoutExpired, OSError, ValueError):
            self.tuer()


@pytest.fixture
def detenteur() -> Iterator[Detenteur]:
    proc = Detenteur()
    yield proc
    proc.fermer()


def test_verrou_occupe_sans_attente(detenteur: Detenteur) -> None:
    debut = time.monotonic()
    with pytest.raises(RessourceOccupee) as info:
        with verrou_gpu():
            pytest.fail("verrou obtenu alors qu'un autre processus le détient")
    assert time.monotonic() - debut < 2
    exc = info.value
    assert exc.code_sortie == CodeSortie.RESSOURCE_OCCUPEE
    assert exc.pid == detenteur.pid
    assert exc.commande == COMMANDE_DETENTEUR
    assert str(detenteur.pid) in str(exc)
    assert COMMANDE_DETENTEUR in str(exc)


def test_verrou_occupe_avec_attente_obtenu_a_la_liberation(detenteur: Detenteur) -> None:
    minuterie = threading.Timer(0.5, detenteur.liberer)
    minuterie.start()
    try:
        debut = time.monotonic()
        with verrou_gpu(attendre=True, delai=30, commande="attente") as chemin:
            attente = time.monotonic() - debut
            contenu = json.loads(chemin.read_bytes()[:4096].decode("utf-8"))
    finally:
        minuterie.cancel()
    assert attente >= 0.4
    assert (contenu["pid"], contenu["commande"]) == (os.getpid(), "attente")


def test_verrou_occupe_delai_depasse(detenteur: Detenteur) -> None:
    debut = time.monotonic()
    with pytest.raises(RessourceOccupee, match="délai") as info:
        with verrou_gpu(attendre=True, delai=0.5):
            pytest.fail("verrou obtenu alors qu'un autre processus le détient")
    assert 0.5 <= time.monotonic() - debut < 5
    assert info.value.pid == detenteur.pid


def test_verrou_detenteur_tue_recupere(detenteur: Detenteur) -> None:
    detenteur.tuer()  # aucune sortie propre : le système libère le verrou d'octets
    chemin = dossier_var() / "gpu.lock"
    residuel = json.loads(chemin.read_bytes()[:4096].decode("utf-8"))
    assert residuel["pid"] == detenteur.pid  # contenu résiduel du mort
    with verrou_gpu(commande="successeur"):
        contenu = json.loads(chemin.read_bytes()[:4096].decode("utf-8"))
    assert (contenu["pid"], contenu["commande"]) == (os.getpid(), "successeur")
