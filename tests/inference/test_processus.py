"""Processus gérés : Job Object, registre `pids/`, orphelins (AD-27).

`sys.executable` est le lanceur du venv, qui démarre lui-même l'interpréteur de base : les
« enfants » de ces tests sont donc déjà des arbres de deux processus.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import psutil
import pytest

from slmsp.inference import processus
from slmsp.inference.processus import EntreePid, ErreurInference

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Job Object : Windows seul")

PY = sys.executable
DORMIR = [PY, "-c", "import time; time.sleep(120)"]


def _attendre(condition, delai: float = 15.0) -> bool:
    echeance = time.monotonic() + delai
    while time.monotonic() < echeance:
        if condition():
            return True
        time.sleep(0.05)
    return condition()


def _mort(pid: int, creation: float) -> bool:
    return processus.processus_identique(pid, creation) is None


def _descendants(pid: int) -> list[psutil.Process]:
    try:
        return psutil.Process(pid).children(recursive=True)
    except psutil.NoSuchProcess:
        return []


def test_lancer_inscrit_journalise_et_arrete(tmp_path: Path) -> None:
    journal = tmp_path / "journal.log"
    gere = processus.lancer(
        [PY, "-c", "import time; print('bonjour', flush=True); time.sleep(120)"],
        role="essai",
        port=1234,
        journal=journal,
    )
    try:
        assert gere.vivant and gere.code_retour is None
        entree = json.loads(processus.chemin_entree(gere.pid).read_text(encoding="utf-8"))
        assert entree["pid"] == gere.pid
        assert entree["port"] == 1234 and entree["role"] == "essai"
        assert entree["parent_pid"] == os.getpid()
        assert entree["commande"][0] == PY
        assert _attendre(lambda: "bonjour" in journal.read_text(encoding="utf-8"))
        petits_enfants = _descendants(gere.pid)
        assert petits_enfants  # interpréteur de base lancé par le lanceur du venv
    finally:
        gere.arreter()
    assert not gere.vivant and gere.code_retour is not None
    assert not processus.chemin_entree(gere.pid).exists()
    assert _attendre(lambda: not any(p.is_running() for p in petits_enfants))
    assert gere.arreter() == gere.code_retour  # idempotent


def test_lancer_environnement_sans_secret(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FAUX_API_KEY", "valeur-secrete")
    monkeypatch.setenv("SLMSP_ESSAI", "visible")
    script = "import os; print(os.environ.get('FAUX_API_KEY'), os.environ.get('SLMSP_ESSAI'))"
    code, sortie = processus.executer([PY, "-c", script], delai=60)
    assert code == 0
    assert sortie.split() == ["None", "visible"]


def test_executer_code_et_sortie(tmp_path: Path) -> None:
    journal = tmp_path / "outil.log"
    journal.write_text("avant\n", encoding="utf-8")
    code, sortie = processus.executer(
        [PY, "-c", "import sys; print('ligne'); sys.exit(3)"], delai=60, journal=journal
    )
    assert code == 3
    assert sortie.strip() == "ligne"
    assert journal.read_text(encoding="utf-8").splitlines() == ["avant", "ligne"]
    assert list(processus.dossier_pids().glob("*.json")) == []


def test_executer_delai_depasse(tmp_path: Path) -> None:
    debut = time.monotonic()
    with pytest.raises(ErreurInference, match="délai"):
        processus.executer(
            [PY, "-c", "import time; print('attente', flush=True); time.sleep(120)"], delai=2
        )
    assert time.monotonic() - debut < 30
    assert list(processus.dossier_pids().glob("*.json")) == []


def test_arreter_tue_les_petits_enfants(tmp_path: Path) -> None:
    fichier = tmp_path / "petit.pid"
    script = textwrap.dedent(
        f"""
        import subprocess, sys, time
        p = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
        open({str(fichier)!r}, "w").write(str(p.pid))
        time.sleep(120)
        """
    )
    gere = processus.lancer([PY, "-c", script], role="essai", journal=tmp_path / "j.log")
    try:
        assert _attendre(lambda: fichier.exists() and fichier.read_text().strip() != "")
        petit = psutil.Process(int(fichier.read_text()))
        assert petit.is_running()
    finally:
        gere.arreter()
    assert _attendre(lambda: not petit.is_running())


def test_parent_tue_enfant_tue(tmp_path: Path) -> None:
    """Le parent Python meurt brutalement : le Job Object tue son enfant."""
    sortie = tmp_path / "pids.json"
    script = textwrap.dedent(
        f"""
        import json, os, sys, time
        from slmsp.inference import processus
        gere = processus.lancer(
            [sys.executable, "-c", "import time; time.sleep(300)"],
            role="enfant",
            journal={str(tmp_path / "enfant.log")!r},
        )
        with open({str(sortie)!r} + ".tmp", "w") as f:
            json.dump({{"parent": os.getpid(), "enfant": gere.pid}}, f)
        os.replace({str(sortie)!r} + ".tmp", {str(sortie)!r})
        time.sleep(300)
        """
    )
    lanceur = subprocess.Popen(
        [PY, "-c", script],
        env={**os.environ},
        creationflags=processus.CREATE_NO_WINDOW,
    )
    try:
        assert _attendre(sortie.exists, 60), "le parent n'a pas lancé son enfant"
        pids = json.loads(sortie.read_text())
        parent = psutil.Process(pids["parent"])
        enfant = psutil.Process(pids["enfant"])
        arbre = [enfant, *enfant.children(recursive=True)]
        assert all(p.is_running() for p in arbre)
        entree = processus.chemin_entree(enfant.pid)
        assert entree.exists()

        parent.kill()  # TerminateProcess : aucun code de nettoyage ne s'exécute
        assert _attendre(lambda: not any(p.is_running() for p in arbre)), "enfant survivant"

        # L'entrée reste (parent tué) : le nettoyage la retire comme disparue.
        assert entree.exists()
        lignes = processus.nettoyer_orphelins()
        assert [ligne["action"] for ligne in lignes] == ["disparu"]
        assert not entree.exists()
    finally:
        lanceur.kill()
        lanceur.wait(30)


def _processus_mort() -> tuple[int, float]:
    """PID et date de création d'un processus terminé."""
    p = subprocess.Popen([PY, "-c", "pass"], creationflags=processus.CREATE_NO_WINDOW)
    creation = psutil.Process(p.pid).create_time()
    p.wait(60)
    return p.pid, creation


def _entree(pid: int, creation: float, parent: tuple[int, float]) -> EntreePid:
    return EntreePid(
        pid=pid,
        port=4321,
        role="orphelin",
        parent_pid=parent[0],
        parent_creation=parent[1],
        creation=creation,
        commande=["llama-server"],
        demarre_le="2026-10-12T00:00:00+02:00",
    )


def _journal_nettoyage() -> list[dict]:
    chemin = processus.dossier_pids() / processus.NOM_NETTOYAGE
    return [json.loads(ligne) for ligne in chemin.read_text(encoding="utf-8").splitlines()]


def test_nettoyer_orphelin_vivant_sans_parent() -> None:
    orphelin = subprocess.Popen(DORMIR, creationflags=processus.CREATE_NO_WINDOW)
    try:
        assert _attendre(lambda: bool(_descendants(orphelin.pid)))
        petits = _descendants(orphelin.pid)
        creation = psutil.Process(orphelin.pid).create_time()
        processus.inscrire(_entree(orphelin.pid, creation, _processus_mort()))

        lignes = processus.nettoyer_orphelins()

        assert [ligne["action"] for ligne in lignes] == ["arrete"]
        assert lignes[0]["entree"]["pid"] == orphelin.pid
        assert orphelin.wait(30) is not None
        assert _attendre(lambda: not any(p.is_running() for p in petits))
        assert not processus.chemin_entree(orphelin.pid).exists()
        assert _journal_nettoyage() == lignes
    finally:
        orphelin.kill()
        orphelin.wait(30)


def test_nettoyer_entree_perimee_et_pid_recycle() -> None:
    mort = _processus_mort()
    processus.inscrire(_entree(*mort, parent=mort))
    vivant = subprocess.Popen(DORMIR, creationflags=processus.CREATE_NO_WINDOW)
    try:
        # PID vivant mais date de création différente : PID recyclé, jamais tué.
        recycle = _entree(vivant.pid, 1.0, parent=mort)
        processus.inscrire(recycle)

        lignes = processus.nettoyer_orphelins()

        assert sorted(ligne["action"] for ligne in lignes) == ["disparu", "disparu"]
        assert vivant.poll() is None
        assert list(processus.dossier_pids().glob("*.json")) == []
    finally:
        vivant.kill()
        vivant.wait(30)


def test_nettoyer_laisse_un_processus_dont_le_parent_vit(tmp_path: Path) -> None:
    gere = processus.lancer(DORMIR, role="actif", journal=tmp_path / "j.log")
    try:
        (processus.dossier_pids() / "illisible.json").write_text("{pas du json", encoding="utf-8")
        lignes = processus.nettoyer_orphelins()
        assert [ligne["action"] for ligne in lignes] == ["illisible"]
        assert gere.vivant
        assert processus.chemin_entree(gere.pid).exists()
    finally:
        gere.arreter()


@pytest.mark.parametrize(
    "modification",
    [
        {"pid": "12"},  # psutil.Process("12") lèverait TypeError
        {"parent_pid": True},
        {"creation": "hier"},
        {"role": None, "pid": 12.0},
    ],
)
def test_nettoyer_entree_mal_typee(modification: dict) -> None:
    """Revue lot 3b, P5 : JSON valide mais mal typé → `illisible`, sans exception."""
    entree = {
        "pid": 12,
        "port": None,
        "role": "x",
        "parent_pid": 13,
        "parent_creation": 1.0,
        "creation": 2.0,
    }
    chemin = processus.dossier_pids() / "mal-type.json"
    chemin.write_text(json.dumps({**entree, **modification}), encoding="utf-8")
    lignes = processus.nettoyer_orphelins()
    assert [ligne["action"] for ligne in lignes] == ["illisible"]
    assert not chemin.exists()


def test_nettoyer_entree_incomplete() -> None:
    chemin = processus.dossier_pids() / "incomplete.json"
    chemin.write_text(json.dumps({"pid": 12, "role": "x", "creation": 2.0}), encoding="utf-8")
    assert [ligne["action"] for ligne in processus.nettoyer_orphelins()] == ["illisible"]
    assert not chemin.exists()


def test_lancer_commande_introuvable(tmp_path: Path) -> None:
    with pytest.raises(OSError):
        processus.lancer([str(tmp_path / "absent.exe")], role="x", journal=tmp_path / "j.log")
    assert list(processus.dossier_pids().glob("*.json")) == []


def test_executer_cree_le_dossier_du_journal(tmp_path: Path) -> None:
    journal = tmp_path / "absent" / "sous" / "outil.log"
    code, sortie = processus.executer([PY, "-c", "print('ok')"], delai=60, journal=journal)
    assert (code, sortie.strip()) == (0, "ok")
    assert journal.read_text(encoding="utf-8").strip() == "ok"


def test_lancer_annule_si_la_reprise_echoue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Échec après la création : enfant suspendu tué, job fermé, entrée retirée."""
    enfants: list[subprocess.Popen] = []
    popen = subprocess.Popen

    def espion(*args, **kwargs):
        enfants.append(popen(*args, **kwargs))
        return enfants[-1]

    def reprise_impossible(handle: int) -> None:
        raise OSError("reprise impossible")

    monkeypatch.setattr(processus.subprocess, "Popen", espion)
    monkeypatch.setattr(processus, "reprendre_processus", reprise_impossible)
    with pytest.raises(OSError, match="reprise impossible"):
        processus.lancer(DORMIR, role="x", journal=tmp_path / "j.log")
    (enfant,) = enfants
    assert enfant.poll() is not None
    assert list(processus.dossier_pids().glob("*.json")) == []
