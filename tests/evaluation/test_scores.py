"""Formules des Scores de Tâche (story 5.6) : un test par Tâche, verdicts aux ancrages.

Les verdicts sont fabriqués (`verdict_factice`, justifications factices) sur des items réels
du jeu v1.0 lus en lecture seule ; les contrôles automatiques sont fournis à la main.
"""

from __future__ import annotations

from typing import Any

import pytest
from evaluation_factices import verdict_factice

from slmsp.core.config import racine_projet
from slmsp.core.items import lire_jeu
from slmsp.core.schemas.generation import Generation
from slmsp.core.schemas.scores import Scores
from slmsp.evaluation.config import charger_evaluation
from slmsp.evaluation.scores import Jugement, calculer_scores, score_tache

V10 = lire_jeu("v1.0", racine_projet())
SEUILS = charger_evaluation().seuils
SHA = "cd" * 32


def items(code: str, n: int) -> list[Any]:
    return [i for i in V10.items if i.code == code][:n]


def generation(item: Any, statut: str = "ok") -> Generation:
    fin = (
        {"type": "fin", "raison": "terminee"}
        if statut == "ok"
        else {"type": "erreur", "code": "x", "message": "<erreur-factice>"}
    )
    return Generation(
        item_id=item.id,
        tache=item.code,
        statut=statut,
        sortie_canonique={"texte": "<sortie-factice>"},
        trace=[fin],
        duree_ms=1,
    )


def juge(item: Any, **notes: Any) -> Jugement:
    return Jugement("juge", verdict_factice(item, **notes), cle=f"cle-{item.id}")


def calculer(
    code: str,
    de_la_tache: list[Any],
    principal: dict[str, Jugement],
    controles: dict[str, dict[str, Any]] | None = None,
    *,
    second: dict[str, Jugement] | None = None,
    erreurs: tuple[str, ...] = (),
) -> Any:
    return score_tache(
        code,
        de_la_tache,
        generations={
            i.id: generation(i, "erreur" if i.id in erreurs else "ok") for i in de_la_tache
        },
        controles=controles or {},
        principal=principal,
        second=second or {},
        seuils=SEUILS,
        jeu_statut="provisoire",
        manifeste_sha256=SHA,
        cout_eur=0.0123456789,
    )


def test_q_items_reussis() -> None:
    a, b, c = items("Q", 3)
    sans = V10.item("Q-014")
    assert sans.sans_reponse and not a.sans_reponse
    principal = {
        a.id: juge(a, exactitude=2, pertinence_source=1),  # réussi
        b.id: juge(b, exactitude=2, pertinence_source=1),  # URL inventée : échec
        c.id: juge(c, exactitude=1, pertinence_source=1),  # échec
        sans.id: juge(sans, exactitude=0, pertinence_source=0, cas_sans_reponse=1),  # réussi
    }
    controles = {i.id: {"urls_inventees": []} for i in (a, c, sans)}
    controles[b.id] = {"urls_inventees": ["https://exemple.invalid"]}
    score = calculer("Q", [a, b, c, sans], principal, controles)
    assert score.score == 50.0 and score.composantes == {"reussis": 50.0}
    assert score.rapportes == {"items_avec_url_inventee": 1}
    assert score.effectifs.notes == 4 and score.effectifs.juges == 4
    assert score.cout_juge_eur == 0.012346 and score.manifeste_sha256 == SHA
    assert score.statuts.jeu_statut == "provisoire" and not score.statuts.verdicts_relus


def test_rd_appel_valide_et_reponse_exacte() -> None:
    a, b, c = items("RD", 3)
    controles = {
        a.id: {"appels_attendus": 3, "appels_valides": 2, "reponse_exacte": True},
        b.id: {"appels_attendus": 1, "appels_valides": 1, "reponse_exacte": None, "litige": True},
        c.id: {"appels_attendus": 2, "appels_valides": 0, "reponse_exacte": None, "litige": True},
    }
    principal = {
        b.id: juge(b, libelle_correct=1),
        c.id: Jugement("invalide", None, cle="cle"),  # litige sans verdict : exclu
    }
    score = calculer("RD", [a, b, c], principal, controles)
    assert score.composantes == {"appel_valide": 50.0, "reponse_exacte": 100.0}
    assert score.score == 75.0
    assert score.effectifs.juges == 1 and score.effectifs.invalides == 1
    assert score.rapportes == {"litiges": 2}
    assert score.kappa.valeur is None


def test_rd_sans_appel_attendu_hors_denominateur() -> None:
    a, b = items("RD", 2)
    controles = {
        a.id: {"appels_attendus": 0, "appels_valides": 0, "reponse_exacte": False},
        b.id: {"appels_attendus": 2, "appels_valides": 1, "reponse_exacte": True},
    }
    score = calculer("RD", [a, b], {}, controles)
    assert score.composantes == {"appel_valide": 50.0, "reponse_exacte": 50.0}


def test_cr_couverture_et_invention() -> None:
    a, b = items("CR", 2)
    principal = {
        a.id: juge(a, presence_elements=1, absence_invention=1, structure=0),
        b.id: juge(b, presence_elements=0.5, absence_invention=0, structure=1),
    }
    score = calculer("CR", [a, b], principal)
    assert score.composantes == {"couverture": 75.0, "sans_invention": 50.0}
    assert score.score == 62.5 and score.rapportes == {"structure": 50.0}


def test_lc_fidelite_termes_et_plafond() -> None:
    a, b = items("LC", 2)
    principal = {
        a.id: juge(a, fidelite=2, termes_juridiques=1, clarte_percue=4),
        b.id: juge(b, fidelite=1, termes_juridiques=1, clarte_percue=2),
    }
    gains = {a.id: {"gain_km": 15.0}, b.id: {"gain_km": 7.0}}
    score = calculer("LC", [a, b], principal, gains)
    assert score.score == 50.0 and not score.statuts.plafonne_lc
    assert score.rapportes == {"gain_km_moyen": 11.0, "clarte_percue_moyenne": 3.0}
    reussis = {i: juge(x, fidelite=2, termes_juridiques=1) for i, x in ((a.id, a), (b.id, b))}
    faibles = {a.id: {"gain_km": 5.0}, b.id: {"gain_km": 7.0}}
    plafonne = calculer("LC", [a, b], reussis, faibles)
    assert plafonne.composantes == {"fidelite_et_termes": 100.0}
    assert plafonne.score == 50.0 and plafonne.statuts.plafonne_lc


def test_co_rappel_et_hors_faute() -> None:
    a, b = items("CO", 2)
    controles = {
        a.id: {"rappel": 1.0, "taux_hors_faute": 0.0},
        b.id: {"rappel": 0.5, "taux_hors_faute": 0.2},
    }
    score = calculer("CO", [a, b], {}, controles)
    assert score.score == 70.0 and score.composantes == {"rappel_x_hors_faute": 70.0}
    assert score.rapportes == {"rappel_moyen": 75.0, "taux_hors_faute_moyen": 10.0}
    assert score.effectifs.juges == 0 and score.kappa.valeur is None


def test_re_fideles_et_couverture() -> None:
    a, b = items("RE", 2)
    principal = {
        a.id: juge(a, fidelite=1, presence_elements=1),
        b.id: juge(b, fidelite=0, presence_elements=0),
    }
    controles = {a.id: {"respect_longueur": True}, b.id: {"respect_longueur": False}}
    score = calculer("RE", [a, b], principal, controles)
    assert score.composantes == {"fideles": 50.0, "couverture": 50.0}
    assert score.score == 50.0 and score.rapportes == {"respect_longueur": 50.0}


def test_ct_conformite_et_emplacements() -> None:
    a, b = items("CT", 2)
    principal = {a.id: juge(a, conformite=2), b.id: juge(b, conformite=1)}
    controles = {a.id: {"emplacements_reussis": True}, b.id: {"emplacements_reussis": False}}
    score = calculer("CT", [a, b], principal, controles)
    assert score.composantes == {"conformite": 75.0, "emplacements": 50.0}
    assert score.score == 62.5


def test_nr_exacts_et_arrondi() -> None:
    a, b, c = items("NR", 3)
    principal = {a.id: juge(a, exactitude=1), b.id: juge(b, exactitude=0), c.id: juge(c)}
    score = calculer("NR", [a, b, c], principal)
    assert score.score == 66.6667


def test_exclusions_et_effectifs() -> None:
    a, b, c, d, e = items("NR", 5)
    principal = {
        a.id: juge(a, exactitude=1),
        b.id: Jugement("invalide", None),
        c.id: Jugement("non-juge", None, motif="budget"),
        # d : en erreur à la génération, jamais jugé
        e.id: juge(e, exactitude=0),
    }
    second = {a.id: juge(a, exactitude=1), e.id: juge(e, exactitude=0)}
    score = calculer("NR", [a, b, c, d, e], principal, second=second, erreurs=(d.id,))
    assert score.score == 50.0
    effectifs = score.effectifs
    assert (effectifs.notes, effectifs.juges, effectifs.invalides) == (2, 2, 1)
    assert (effectifs.non_juges, effectifs.en_erreur, effectifs.second_juge) == (1, 1, 2)
    assert score.kappa.effectif == 2 and score.kappa.valeur == 1.0
    assert not score.statuts.fragile


def test_fragile_et_tache_sans_item_note() -> None:
    a, b, c = items("NR", 3)
    principal = {a.id: juge(a, exactitude=1), b.id: juge(b, exactitude=0), c.id: juge(c)}
    second = {a.id: juge(a, exactitude=0), b.id: juge(b, exactitude=1), c.id: juge(c)}
    fragile = calculer("NR", [a, b, c], principal, second=second)
    assert fragile.kappa.valeur is not None and fragile.kappa.valeur < SEUILS.kappa_fragile
    assert fragile.statuts.fragile
    vide = calculer("NR", [a], {a.id: Jugement("invalide", None)})
    assert vide.score is None and vide.composantes == {"exacts": None}


def test_calculer_scores_entete_et_couts() -> None:
    q, nr = V10.item("Q-001"), V10.item("NR-001")
    scores = calculer_scores(
        items=[nr, q],
        generations={i.id: generation(i) for i in (q, nr)},
        controles={q.id: {"urls_inventees": []}},
        principal={q.id: juge(q), nr.id: juge(nr)},
        second={},
        seuils=SEUILS,
        run_generation="20261012-155024-granite-4.0-1b-0cdc",
        jeu_version="v1.0",
        jeu_statut="provisoire",
        manifeste_sha256=SHA,
        modele_ref="base:granite-4.0-1b",
        quantification="q4_k_m",
        couts={q.id: 0.1, nr.id: 0.2000004},
    )
    assert list(scores.taches) == ["Q", "NR"]  # ordre de SPEC §2
    assert scores.taches["Q"].score == 100.0 and scores.taches["NR"].score == 100.0
    assert scores.cout_juge_total_eur == 0.3 and scores.taches["NR"].cout_juge_eur == 0.2
    assert Scores.model_validate_json(scores.model_dump_json()) == scores


@pytest.mark.parametrize("code", ["Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR"])
def test_chaque_tache_porte_tous_les_champs(code: str) -> None:
    (item,) = items(code, 1)
    principal = {} if code in ("RD", "CO") else {item.id: juge(item)}
    score = calculer(code, [item], principal)
    champs = set(score.model_dump())
    assert {
        "tache", "score", "composantes", "effectifs", "statuts", "kappa", "cout_juge_eur",
        "manifeste_sha256",
    } <= champs  # fmt: skip
