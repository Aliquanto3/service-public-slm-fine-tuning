"""Kappa de Cohen entre juges (story 5.6) : simple, quadratique, non calculable, par Tâche."""

from __future__ import annotations

import pytest
from evaluation_factices import verdict_factice

from slmsp.core.config import racine_projet
from slmsp.core.items import lire_jeu
from slmsp.evaluation.scores import Jugement, kappa_cohen, kappa_tache

V10 = lire_jeu("v1.0", racine_projet())


def test_accord_parfait() -> None:
    paires = [(0, 0), (1, 1), (2, 2), (1, 1)]
    assert kappa_cohen(paires, (0, 1, 2)) == pytest.approx(1.0)
    assert kappa_cohen(paires, (0, 1, 2), pondere=True) == pytest.approx(1.0)


def test_desaccord_total() -> None:
    assert kappa_cohen([(0, 1), (1, 0)], (0, 1)) == pytest.approx(-1.0)


def test_pondere_calcule_a_la_main() -> None:
    # n = 4 ; observé : (0,0) (1,2) (2,2) (2,1) ; marges lignes = colonnes = (1/4, 1/4, 1/2).
    # Poids quadratiques ((i − j) / 2)² : w01 = w12 = 1/4, w02 = 1.
    # Désaccord observé = 2 × 1/4 × 1/4 = 0,125.
    # Désaccord attendu = 2 × (1/4 × 1/16 + 1 × 1/8 + 1/4 × 1/8) = 0,34375.
    paires = [(0, 0), (1, 2), (2, 2), (2, 1)]
    assert kappa_cohen(paires, (0, 1, 2), pondere=True) == pytest.approx(1 - 0.125 / 0.34375)
    # Simple : désaccord observé 0,5 ; attendu 1 − (1/16 + 1/16 + 1/4) = 0,625.
    assert kappa_cohen(paires, (0, 1, 2)) == pytest.approx(1 - 0.5 / 0.625)


def test_non_calculable() -> None:
    assert kappa_cohen([], (0, 1)) is None
    assert kappa_cohen([(1, 1)], (0, 1)) is None  # moins de 2 paires
    assert kappa_cohen([(1, 1), (1, 1), (1, 1)], (0, 1)) is None  # accord attendu = 1
    with pytest.raises(ValueError, match="catégories"):
        kappa_cohen([(3, 1), (1, 1)], (0, 1))


def test_kappa_tache_minimum_et_effectif() -> None:
    items = [i for i in V10.items if i.code == "NR"][:4]
    notes_principal = [1, 0, 1, 0]
    notes_second = [1, 0, 0, 0]
    principal = {
        i.id: Jugement("juge", verdict_factice(i, exactitude=n))
        for i, n in zip(items, notes_principal, strict=True)
    }
    second = {
        i.id: Jugement("juge", verdict_factice(i, exactitude=n))
        for i, n in zip(items, notes_second, strict=True)
    }
    second[items[3].id] = Jugement("invalide", None)  # exclu de l'effectif
    kappa = kappa_tache("NR", items, principal, second)
    attendu = kappa_cohen([(1, 1), (0, 0), (1, 0)], (0, 1))
    assert kappa.effectif == 3
    assert kappa.par_critere == {"exactitude": round(attendu, 4)}
    assert kappa.valeur == round(attendu, 4)


def test_kappa_tache_lc_minimum_des_criteres() -> None:
    items = [i for i in V10.items if i.code == "LC"][:3]
    principal = {
        i.id: Jugement("juge", verdict_factice(i, fidelite=f, termes_juridiques=1, clarte_percue=c))
        for i, f, c in zip(items, (2, 1, 0), (5, 3, 1), strict=True)
    }
    second = {
        i.id: Jugement("juge", verdict_factice(i, fidelite=f, termes_juridiques=1, clarte_percue=c))
        for i, f, c in zip(items, (2, 1, 0), (1, 3, 5), strict=True)
    }
    kappa = kappa_tache("LC", items, principal, second)
    assert kappa.par_critere["fidelite"] == pytest.approx(1.0)
    assert kappa.par_critere["termes_juridiques"] is None  # accord attendu = 1
    assert kappa.par_critere["clarte_percue"] < 0
    assert kappa.valeur == kappa.par_critere["clarte_percue"]


def test_sans_kappa_pour_rd_et_co() -> None:
    for tache in ("RD", "CO"):
        kappa = kappa_tache(tache, [], {}, {})
        assert kappa.valeur is None and kappa.par_critere == {} and kappa.effectif == 0
