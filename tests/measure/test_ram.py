"""Échantillonneur RAM : arbre de processus factice (enfant Python qui alloue) (story 6.4)."""

from __future__ import annotations

import subprocess
import sys
import time

import psutil

from slmsp.measure.ram import EchantillonneurRam, somme_arbre

ALLOCATION_MO = 150
CODE_ENFANT = (
    f"b = bytearray({ALLOCATION_MO} * 1024 * 1024)\n"
    "b[::4096] = b'x' * len(b[::4096])\n"
    "print('pret', flush=True)\n"
    "input()\n"
)


def test_le_pic_inclut_les_descendants() -> None:
    enfant = subprocess.Popen(
        [sys.executable, "-c", CODE_ENFANT],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert enfant.stdout is not None and enfant.stdout.readline().strip() == "pret"
        racine = psutil.Process()
        seul = racine.memory_info().rss
        with EchantillonneurRam(racine, periode_s=0.02) as ram:
            time.sleep(0.15)
        assert ram.nb_echantillons >= 3
        assert ram.pic_octets >= seul + ALLOCATION_MO * 1024**2 * 0.8
        assert ram.pic_octets >= somme_arbre(racine) * 0.8
    finally:
        enfant.kill()
        enfant.wait()


def test_le_pic_est_le_maximum_des_echantillons() -> None:
    valeurs = iter([10, 50, 30, 20, 20, 20, 20, 20, 20, 20])
    with EchantillonneurRam(periode_s=0.01, lire=lambda _p: next(valeurs, 5)) as ram:
        time.sleep(0.05)
    assert ram.pic_octets == 50


def test_processus_disparu_vaut_zero() -> None:
    processus = subprocess.Popen([sys.executable, "-c", "input()"], stdin=subprocess.PIPE)
    vu = psutil.Process(processus.pid)
    processus.kill()
    processus.wait()
    assert somme_arbre(vu) == 0
