"""Découpage des textes longs (story 4.4) : fonctions pures de `harness.decoupage`.

Règle D1.1 : aucun texte rédigé ; les textes sont des mots aléatoires (`mots`). La mesure
de test compte les mots (comme `FakeLlm.compter_tokens`), plus un surcoût fixe qui joue le
rôle du prompt de morceau.
"""

from __future__ import annotations

import random

import pytest
from harness_factices import mots

from slmsp.harness.decoupage import decouper, empaqueter, paragraphes, regrouper

SURCOUT = 37


def mesure(texte: str) -> int:
    return SURCOUT + len(texte.split())


def texte_long(nb_mots: int, graine: str, taille: tuple[int, int] = (20, 80)) -> list[str]:
    """Paragraphes de mots aléatoires totalisant au moins `nb_mots` mots."""
    hasard = random.Random(graine)
    blocs: list[str] = []
    total = 0
    while total < nb_mots:
        k = hasard.randint(*taille)
        blocs.append(mots(k, f"{graine}-{len(blocs)}"))
        total += k
    return blocs


def sans_chevauchement(morceaux: list[str]) -> list[str]:
    """Mots des morceaux, chaque paragraphe repris du morceau précédent retiré."""
    resultat: list[str] = []
    precedent: list[str] = []
    for morceau in morceaux:
        blocs = paragraphes(morceau)
        while blocs and precedent and blocs[0] in precedent:
            blocs = blocs[1:]
        resultat.extend(" ".join(blocs).split())
        precedent = paragraphes(morceau)
    return resultat


# --- paragraphes ---------------------------------------------------------------------------


def test_paragraphes_separes_par_ligne_vide() -> None:
    a, b, c, d = (mots(4, f"p{i}") for i in range(4))
    texte = f"\n  {a}\n{b}  \n\n\n{c}\r\n \t \r\n{d}\n\n   \n"
    assert paragraphes(texte) == [f"{a}\n{b}", c, d]
    assert paragraphes("") == [] and paragraphes(" \n\n \n") == []


def test_ligne_vide_avec_blancs_unicode() -> None:
    a, b, c = (mots(4, f"u{i}") for i in range(3))
    texte = f"{a}\n \n{b}\n  \t\n\n{c}"
    assert paragraphes(texte) == [a, b, c]


# --- regrouper / empaqueter --------------------------------------------------------------


def test_regrouper_glouton() -> None:
    unites = [mots(k, f"u{i}") for i, k in enumerate((3, 3, 3, 9, 2, 2))]
    groupes = regrouper(unites, lambda t: len(t.split()), 7, joint="\n\n")
    assert groupes == [unites[0:2], unites[2:3], unites[3:4], unites[4:6]]
    assert [u for g in groupes for u in g] == unites
    assert regrouper([], len, 3, joint=" ") == []


def test_empaqueter_mesure_le_groupe() -> None:
    vus: list[tuple[int, ...]] = []

    def mesurer(groupe):
        vus.append(tuple(groupe))
        return sum(groupe)

    assert empaqueter([1, 2, 3, 4], mesurer, 5) == [[1, 2], [3], [4]]
    assert vus == [(1, 2), (1, 2, 3), (3, 4)]


@pytest.mark.parametrize("budget", [0, -3])
def test_budget_invalide(budget: int) -> None:
    with pytest.raises(ValueError, match="budget"):
        regrouper(["a"], len, budget, joint=" ")
    with pytest.raises(ValueError, match="budget"):
        decouper(mots(5, "x"), len, budget)
    with pytest.raises(ValueError, match="chevauchement"):
        decouper(mots(5, "x"), len, 10, -1)


# --- decouper -------------------------------------------------------------------------------


@pytest.mark.parametrize("chevauchement", [0, 1, 2])
def test_decoupage_long_sans_troncature(chevauchement: int) -> None:
    blocs = texte_long(6500, f"long-{chevauchement}")
    texte = "\n\n".join(blocs)
    budget = 900
    morceaux = decouper(texte, mesure, budget, chevauchement)

    assert len(morceaux) > 5
    assert all(mesure(m) <= budget for m in morceaux)
    for morceau in morceaux:  # coupé entre paragraphes
        assert all(bloc in blocs for bloc in paragraphes(morceau))
    assert sans_chevauchement(morceaux) == texte.split()
    if chevauchement:
        for avant, apres in zip(morceaux, morceaux[1:], strict=False):
            repris = paragraphes(avant)[-chevauchement:]
            assert paragraphes(apres)[: len(repris)] == repris
    else:
        assert " ".join(morceaux).split() == texte.split()


def test_deterministe() -> None:
    texte = "\n\n".join(texte_long(6000, "stable"))
    assert decouper(texte, mesure, 700, 1) == decouper(texte, mesure, 700, 1)


def test_texte_court_un_seul_morceau() -> None:
    texte = "\n\n".join(texte_long(100, "court"))
    assert decouper(texte, mesure, 500, 1) == ["\n\n".join(paragraphes(texte))]
    assert decouper("  \n\n ", mesure, 500, 1) == []


def test_chevauchement_reduit_pour_avancer() -> None:
    blocs = [mots(6, f"r{i}") for i in range(3)]
    morceaux = decouper("\n\n".join(blocs), lambda t: len(t.split()), 10, 1)
    assert morceaux == blocs  # la reprise de r0 empêcherait d'ajouter r1 : elle tombe à 0

    blocs = [mots(4, f"q{i}") for i in range(4)]
    morceaux = decouper("\n\n".join(blocs), lambda t: len(t.split()), 10, 1)
    assert morceaux == ["\n\n".join(blocs[i : i + 2]) for i in range(3)]


def test_chevauchement_limite_aux_unites_nouvelles() -> None:
    blocs = [mots(4, f"n{i}") for i in range(4)]
    morceaux = decouper("\n\n".join(blocs), lambda t: len(t.split()), 8, 3)
    # Chaque morceau n'apporte qu'une unité nouvelle : on n'en reprend qu'une.
    assert morceaux == ["\n\n".join(blocs[i : i + 2]) for i in range(3)]


def test_paragraphe_enorme_redecoupe_en_phrases() -> None:
    phrases = [mots(15, f"ph{i}") + "." for i in range(40)]
    texte = " ".join(phrases)
    morceaux = decouper(texte, mesure, SURCOUT + 50, 0)
    assert len(morceaux) > 1
    assert all(mesure(m) <= SURCOUT + 50 for m in morceaux)
    assert " ".join(morceaux).split() == texte.split()
    for morceau in morceaux:  # coupé entre phrases
        assert morceau.rstrip().endswith(".")


def test_paragraphe_enorme_sans_ponctuation_redecoupe_en_mots() -> None:
    texte = mots(1200, "bloc")
    morceaux = decouper(texte, mesure, SURCOUT + 100, 1)
    assert len(morceaux) >= 12
    assert all(mesure(m) <= SURCOUT + 100 for m in morceaux)
    assert sans_chevauchement(morceaux) == texte.split()


def test_paragraphe_enorme_redecoupe_en_lignes() -> None:
    lignes = [mots(30, f"l{i}") for i in range(10)]
    texte = "\n".join(lignes)
    morceaux = decouper(texte, lambda t: len(t.split()), 65, 0)
    assert morceaux == ["\n".join(lignes[i : i + 2]) for i in range(0, 10, 2)]


def test_mot_isole_trop_grand_garde_tel_quel() -> None:
    geant = "x" * 40
    texte = f"{mots(3, 'a')} {geant} {mots(3, 'b')}"
    morceaux = decouper(texte, len, 30, 0)
    assert geant in morceaux
    assert " ".join(morceaux).split() == texte.split()
    assert all(len(m) <= 30 for m in morceaux if m != geant)
