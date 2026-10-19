"""`JugeClaude.estimer` (story INC-3) : estimation avant notation, sans réseau ni écriture."""

from __future__ import annotations

import dataclasses
import math
from types import SimpleNamespace
from typing import Any

import pytest

pytest.importorskip("anthropic")

from slmsp.budget.tarifs import (  # noqa: E402
    UsageTokens,  # noqa: E402
    cout_estime,
    cout_pire_cas,
)
from slmsp.core.schemas.verdict import Verdict  # noqa: E402
from slmsp.judge.cache import cle_verdict  # noqa: E402
from slmsp.judge.claude import (  # noqa: E402
    MIN_VERDICTS_SORTIE_MOYENNE,
    DemandeJugement,
    EstimationCout,
)
from slmsp.judge.prompt import construire_prompt, estimer_tokens_entree  # noqa: E402


def demandes(doublures: SimpleNamespace, items: dict[str, Any], *ids: str) -> list[Any]:
    return [DemandeJugement(items[i], doublures.sortie_factice()) for i in ids]


def semer(banc: Any, doublures: SimpleNamespace, nombre: int, sortie: int) -> None:
    """`nombre` verdicts factices en cache (modèle et effort du banc), `sortie` tokens chacun."""
    for rang in range(nombre):
        banc.cache.ecrire(
            f"cle-factice-{rang}",
            Verdict.invalide_pour("Q-001"),
            modele=doublures.MODELE,
            effort="medium",
            mode="batch",
            cout_eur=0.0,
            usage=UsageTokens(100, sortie),
        )


def attendu(
    banc: Any, doublures: SimpleNamespace, items: dict[str, Any], ids: list[str], sortie: int
):
    config = doublures.config_juge()
    tarifs = banc.registre.tarifs
    estime = pire = 0.0
    for identifiant in ids:
        prompt = construire_prompt(items[identifiant], doublures.sortie_factice(), banc.grille)
        tokens = estimer_tokens_entree(prompt)
        estime += cout_estime(tarifs, doublures.MODELE, "batch", tokens, sortie)
        pire += cout_pire_cas(
            tarifs,
            doublures.MODELE,
            "batch",
            tokens,
            config.max_tokens,
            banc.registre.config.majoration_entree,
        )
    return estime, pire


def test_repli_sur_max_tokens_sans_assez_de_verdicts(
    banc: Any, doublures: SimpleNamespace, items: Any
) -> None:
    juge = banc.juge()
    semer(banc, doublures, MIN_VERDICTS_SORTIE_MOYENNE - 1, 50)
    ids = ["Q-001", "LC-001", "CR-001"]
    estimation = juge.estimer(demandes(doublures, items, *ids))

    estime, pire = attendu(banc, doublures, items, ids, doublures.config_juge().max_tokens)
    assert isinstance(estimation, EstimationCout)
    assert (estimation.nb_demandes, estimation.nb_en_cache, estimation.nb_a_juger) == (3, 0, 3)
    assert estimation.cout_estime_eur == pytest.approx(estime)
    assert estimation.cout_pire_cas_eur == pytest.approx(pire)
    with pytest.raises(dataclasses.FrozenInstanceError):
        estimation.nb_demandes = 0  # type: ignore[misc]


def test_sortie_moyenne_du_cache_et_cache_partiel(
    banc: Any, doublures: SimpleNamespace, items: Any
) -> None:
    juge = banc.juge()
    semer(banc, doublures, MIN_VERDICTS_SORTIE_MOYENNE, 200)
    # Q-001 est déjà jugé (verdict en cache) : il coûte 0.
    prompt = construire_prompt(items["Q-001"], doublures.sortie_factice(), banc.grille)
    cle = cle_verdict(
        items["Q-001"], doublures.sortie_factice(), prompt, doublures.MODELE, "medium"
    )
    banc.cache.ecrire(
        cle,
        Verdict.invalide_pour("Q-001"),
        modele=doublures.MODELE,
        effort="medium",
        mode="batch",
        cout_eur=0.0,
        usage=UsageTokens(100, 200),
    )
    estimation = juge.estimer(demandes(doublures, items, "Q-001", "LC-001", "CR-001"))

    estime, pire = attendu(banc, doublures, items, ["LC-001", "CR-001"], 200)
    assert (estimation.nb_demandes, estimation.nb_en_cache, estimation.nb_a_juger) == (3, 1, 2)
    assert estimation.cout_estime_eur == pytest.approx(estime)
    assert estimation.cout_pire_cas_eur == pytest.approx(pire)
    assert estimation.cout_estime_eur < estimation.cout_pire_cas_eur


def test_moyenne_ignore_autre_effort(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    juge = banc.juge()
    for rang in range(MIN_VERDICTS_SORTIE_MOYENNE):
        banc.cache.ecrire(
            f"autre-{rang}",
            Verdict.invalide_pour("Q-001"),
            modele=doublures.MODELE,
            effort="high",
            mode="batch",
            cout_eur=0.0,
            usage=UsageTokens(100, 10),
        )
    estimation = juge.estimer(demandes(doublures, items, "LC-001"))
    estime, _ = attendu(banc, doublures, items, ["LC-001"], doublures.config_juge().max_tokens)
    assert estimation.cout_estime_eur == pytest.approx(estime)


def test_aucune_ecriture_ni_appel(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    juge = banc.juge()
    avant_cache = banc.cache.chemin.read_bytes()
    avant_registre = banc.registre.chemin.read_bytes() if banc.registre.chemin.exists() else b""
    juge.estimer(demandes(doublures, items, "Q-001", "LC-001"))

    assert banc.faux.requetes == []  # aucun appel réseau
    assert banc.faux.evenements == []  # aucune réservation ni collecte
    assert banc.lots() == [] and banc.cache.appels() == []
    assert banc.cache.chemin.read_bytes() == avant_cache
    apres = banc.registre.chemin.read_bytes() if banc.registre.chemin.exists() else b""
    assert apres == avant_registre


def test_mode_direct_tarif_direct(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    juge = banc.juge(mode_appel="direct")
    estimation = juge.estimer(demandes(doublures, items, "Q-001"))
    prompt = construire_prompt(items["Q-001"], doublures.sortie_factice(), banc.grille)
    attendu_direct = cout_estime(
        banc.registre.tarifs,
        doublures.MODELE,
        "direct",
        estimer_tokens_entree(prompt),
        doublures.config_juge().max_tokens,
    )
    assert estimation.cout_estime_eur == pytest.approx(attendu_direct)
    assert math.isfinite(estimation.cout_pire_cas_eur)


def test_cout_estime_valeurs_a_la_main(banc: Any, doublures: SimpleNamespace) -> None:
    """Oracle indépendant : tarifs du banc (batch 0,5 $/Mtok, direct 1 $/Mtok, taux 1)."""
    banc.juge()
    tarifs = banc.registre.tarifs
    assert cout_estime(tarifs, doublures.MODELE, "batch", 1_000_000, 2_000_000) == pytest.approx(
        1.5
    )
    assert cout_estime(tarifs, doublures.MODELE, "direct", 1_000_000, 2_000_000) == pytest.approx(
        3.0
    )


def test_pire_cas_egal_a_la_reservation_par_item(
    banc: Any, doublures: SimpleNamespace, items: Any
) -> None:
    """`cout_pire_cas_eur` vaut le montant que `reserver_lot` (INC-2) réserve pour ces items."""
    juge = banc.juge()
    ids = ["Q-001", "LC-001", "CR-001"]
    estimation = juge.estimer(demandes(doublures, items, *ids))
    tokens = [
        estimer_tokens_entree(construire_prompt(items[i], doublures.sortie_factice(), banc.grille))
        for i in ids
    ]
    retenu = banc.registre.reserver_lot(
        "lot-coherence",
        juge.poste,
        juge.sous_poste,
        doublures.MODELE,
        tokens,
        doublures.config_juge().max_tokens,
        len(tokens),
    )
    assert retenu == len(ids)
    reserve = sum(
        ligne.reserve_eur
        for ligne in banc.registre.etat().lignes
        if ligne.sous_poste is None and ligne.poste == juge.poste
    )
    assert estimation.cout_pire_cas_eur == pytest.approx(reserve)
