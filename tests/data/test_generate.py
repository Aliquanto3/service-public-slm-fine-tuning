"""Étape `generate` (story 9.4) : plan, ordre de dépense, idempotence, reprise, arrêts.

Faux serveur Mistral, port d'outils et Index factices (`tests/data/conftest.py`). Aucun appel
réel. Toutes les chaînes de contenu sont des jetons aléatoires (D1.1).
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest

pytest.importorskip("mistralai")

from slmsp.core.canonique import sha256_hex  # noqa: E402
from slmsp.core.erreurs import ManifesteInvalide, SlmspError  # noqa: E402
from slmsp.core.gabarits import valider_gabarit  # noqa: E402
from slmsp.data.generate import CHAINES, ORDRE_TACHES  # noqa: E402
from slmsp.data.sessions import TOURS_OUTILS_MAX  # noqa: E402

TOUTES = dict.fromkeys(ORDRE_TACHES, 1)


def _seed_complet(monde: Any, doublures: Any) -> str:
    """Une session possible par Tâche (RE et CT : amorces d'une même ligne publique)."""
    amorces = [
        monde.amorce("Q", "question", ligne=1),
        monde.amorce("RD", "demande", ligne=1),
        monde.scenario(),
        monde.amorce("LC", "texte", ligne=1),
        monde.amorce("CO", "texte", ligne=1),
        monde.amorce("generique", "demande", ligne=1),
        monde.amorce("RE", "texte", ligne=5),
        monde.amorce("RE", "longueur_demandee", ligne=5),
        *(monde.amorce("CT", e, ligne=7) for e in ("type_courrier", "objet", "elements_connus")),
    ]
    return monde.ecrire_seed(amorces)


def _scripter_rd(monde: Any, doublures: Any) -> None:
    """Q d'abord (1 appel), puis RD : un tour d'outils et une réponse finale."""
    appel = doublures.appel_outil("search_datasets", {"query": doublures.factice()})
    monde.faux.reponses = [{}, {"appels": [appel]}, {}]


def _premieres_lignes(gabarit_id: str) -> str:
    gabarit = valider_gabarit(
        doublures_gabarits() / f"{gabarit_id}.md", cles_optionnelles=("max_tokens",)
    )
    return gabarit.consigne.split("\n", 1)[0]


def doublures_gabarits() -> Any:
    from slmsp.core.config import racine_projet

    return racine_projet() / "config" / "prompts" / "generateur"


# --- Plan et ordre de dépense -----------------------------------------------------------------


def test_ordre_des_requetes_et_plan(monde: Any, doublures: Any) -> None:
    seed = _seed_complet(monde, doublures)
    _scripter_rd(monde, doublures)
    resultat = monde.lancer(TOUTES, seed=seed)

    assert resultat.statut == "complet"
    attendu = [
        "traces-q",
        "traces-rd",
        "traces-rd",
        "transcription-cr",
        "cr",
        "lc",
        "generique",
        "ct",
        "re",
        "co",
    ]
    assert monde.faux.gabarits() == [_premieres_lignes(g) for g in attendu]
    plan = monde.lignes(resultat, "plan.jsonl")
    assert [s["tache"] for s in plan] == list(ORDRE_TACHES)
    assert [s["rang"] for s in plan] == list(range(len(ORDRE_TACHES)))
    assert [[g["id"] for g in s["gabarits"]] for s in plan] == [
        list(CHAINES[t]) for t in ORDRE_TACHES
    ]
    assert len(monde.lignes(resultat, "brut.jsonl")) == len(ORDRE_TACHES)
    manifeste = resultat.run.manifeste
    assert manifeste.type == "data-generate" and manifeste.parents == [seed]
    assert {"amorces", "outils-mcp", "gabarit-traces-rd", "gabarit-cr"} <= set(manifeste.entrees)
    (bilan,) = monde.lignes(resultat, "bilan.jsonl")
    assert bilan["statut"] == "complet"
    assert bilan["cout_eur"] == pytest.approx(0.0012 * 10)
    assert bilan["taches"]["RD"]["appels_nouveaux"] == 2
    assert monde.statuts(resultat.run)[-1] == "complet"


def test_groupes_incomplets_deficit_et_surplus(monde: Any) -> None:
    amorces = [
        monde.amorce("RE", "texte", ligne=1),  # sans longueur_demandee : incomplet
        *(monde.amorce("generique", "demande", ligne=n) for n in range(1, 4)),
    ]
    seed = monde.ecrire_seed(amorces)
    resultat = monde.lancer({"RE": 2, "generique": 2}, seed=seed, surplus=0.5)
    comptes = resultat.bilan["comptes_plan"]
    assert comptes["RE"] == {
        "planifiees": 0,
        "cible": 3,
        "deficit": 3,
        "amorces_incompletes": 1,
        "amorces_ignorees": 0,
        "amorces_protegees": 0,
        "passages_proteges": 0,
    }
    assert comptes["generique"]["planifiees"] == 3 and comptes["generique"]["deficit"] == 0
    assert resultat.statut == "complet"


# --- Idempotence et reprise ------------------------------------------------------------------


def test_nouveau_run_sur_le_meme_seed_ne_paie_rien(monde: Any, doublures: Any) -> None:
    seed = _seed_complet(monde, doublures)
    _scripter_rd(monde, doublures)
    premier = monde.lancer(TOUTES, seed=seed)
    requetes, reservations = len(monde.faux.corps), monde.reservations()

    second = monde.lancer(TOUTES, seed=seed)
    assert second.statut == "complet" and second.run.run_id != premier.run.run_id
    assert len(monde.faux.corps) == requetes
    assert monde.reservations() == reservations
    assert monde.outils.ouvertures == 1
    bruts = monde.lignes(second, "brut.jsonl")
    assert sum(b["appels_reutilises"] for b in bruts) == requetes
    assert all(b["appels_nouveaux"] == 0 for b in bruts)
    assert [b["appel_ids"] for b in bruts] == [
        b["appel_ids"] for b in monde.lignes(premier, "brut.jsonl")
    ]
    assert second.bilan["cout_eur"] == 0


def test_reprise_apres_arret_brutal_en_pleine_session(monde: Any, doublures: Any) -> None:
    seed = monde.ecrire_seed(
        [monde.amorce("generique", "demande", ligne=1), monde.amorce("RD", "demande", ligne=1)]
    )
    appel = doublures.appel_outil("search_datasets", {"query": doublures.factice()})
    # RD passe avant generique : A0 (appel d'outil) journalisé, cassette t1 écrite, puis arrêt.
    monde.faux.reponses = [{"appels": [appel]}, KeyboardInterrupt()]
    with pytest.raises(KeyboardInterrupt):
        monde.lancer({"RD": 1, "generique": 1}, seed=seed)
    (run_id,) = [d.name for d in (monde.racine / "runs" / "data-generate").iterdir()]
    assert len(monde.outils.appels) == 1

    reprise = monde.lancer({"RD": 1, "generique": 1}, reprendre=run_id)
    assert reprise.statut == "complet"
    assert len(monde.outils.appels) == 1  # tour 1 relu dans sa cassette
    bruts = {b["tache"]: b for b in monde.lignes(reprise, "brut.jsonl")}
    assert bruts["RD"]["appels_reutilises"] == 1 and bruts["RD"]["appels_nouveaux"] == 1
    assert monde.statuts(reprise.run) == ["en_cours", "interrompu", "en_cours", "complet"]

    with pytest.raises(SlmspError):
        monde.lancer({"RD": 1, "generique": 1}, reprendre=run_id)


def test_reprise_saute_les_sessions_closes(monde: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("generique", "demande", ligne=n) for n in (1, 2, 3)])
    monde.faux.reponses = [{"finish_reason": "length"}, {}, 500]
    resultat = monde.lancer({"generique": 3}, seed=seed)
    assert resultat.statut == "partiel-erreur"
    assert len(monde.faux.corps) == 3

    reprise = monde.lancer({"generique": 3}, reprendre=resultat.run.run_id)
    assert reprise.statut == "complet"
    assert len(monde.faux.corps) == 4  # seule la troisième session est rejouée
    assert len(monde.lignes(reprise, "brut.jsonl")) == 2
    assert [a["motif"] for a in monde.lignes(reprise, "abandons.jsonl")] == ["reponse_tronquee"]


def test_reprise_incoherente_refusee(monde: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("generique", "demande", ligne=1)])
    monde.faux.reponses = [500]
    resultat = monde.lancer({"generique": 1}, seed=seed)
    amorces = monde.racine / "runs" / "data-seed" / seed / "amorces.jsonl"
    amorces.write_bytes(amorces.read_bytes() + b"\n")
    etats = monde.statuts(resultat.run)

    with pytest.raises(ManifesteInvalide, match="amorces"):
        monde.lancer({"generique": 1}, reprendre=resultat.run.run_id)
    assert monde.statuts(resultat.run) == etats
    assert len(monde.faux.corps) == 1


def test_amorce_usager_protegee_ecartee_avant_tout_appel(monde: Any, doublures: Any) -> None:
    from slmsp.core.items import IdentifiantsProteges
    from slmsp.core.texte import normaliser

    texte = doublures.factice()
    seed = monde.ecrire_seed(
        [
            monde.amorce("generique", "demande", ligne=1, texte=texte),
            monde.amorce("generique", "demande", ligne=2),
        ]
    )
    monde.proteges = IdentifiantsProteges(
        frozenset({sha256_hex(normaliser(texte))}), frozenset(), frozenset(), frozenset()
    )
    resultat = monde.lancer({"generique": 2}, seed=seed)
    comptes = resultat.bilan["comptes_plan"]["generique"]
    assert comptes["amorces_protegees"] == 1 and comptes["planifiees"] == 1
    assert len(monde.faux.corps) == 1


def test_reprise_sans_plan_refusee(monde: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("generique", "demande", ligne=1)])
    monde.faux.reponses = [500]
    resultat = monde.lancer({"generique": 1}, seed=seed)
    (resultat.run.dossier / "plan.jsonl").unlink()  # arrêt avant l'écriture du plan
    etats = monde.statuts(resultat.run)

    with pytest.raises(ManifesteInvalide, match="plan.jsonl"):
        monde.lancer({"generique": 1}, reprendre=resultat.run.run_id)
    assert monde.statuts(resultat.run) == etats
    assert len(monde.faux.corps) == 1


@pytest.mark.parametrize("statut", ["en_cours", "partiel-erreur"])
def test_seed_non_complet_refuse(monde: Any, statut: str) -> None:
    seed = monde.ecrire_seed([monde.amorce("generique", "demande", ligne=1)], statut=statut)
    with pytest.raises(ManifesteInvalide):
        monde.lancer({"generique": 1}, seed=seed)
    assert not (monde.racine / "runs" / "data-generate").exists()
    assert monde.faux.corps == []


# --- Arrêts --------------------------------------------------------------------------------


def test_budget_epuise_arret_propre(monde: Any) -> None:
    monde.plafond = 0.0015  # une réservation au pire cas passe, pas la deuxième (max_tokens 800)
    seed = monde.ecrire_seed([monde.amorce("generique", "demande", ligne=n) for n in (1, 2, 3)])
    resultat = monde.lancer({"generique": 3}, seed=seed)

    assert resultat.statut == "partiel-budget"
    assert len(monde.faux.corps) == 1
    assert len(monde.lignes(resultat, "brut.jsonl")) == 1
    assert monde.statuts(resultat.run)[-1] == "partiel-budget"
    (bilan,) = monde.lignes(resultat, "bilan.jsonl")
    assert bilan["statut"] == "partiel-budget" and bilan["taches"]["generique"]["completes"] == 1


@pytest.mark.parametrize(
    ("reponse", "cause"),
    [(500, "ErreurApiMistral"), ({"model": "mistral-large-2411"}, "ModeleMistralRefuse")],
)
def test_erreur_mistral_arret_immediat(monde: Any, reponse: Any, cause: str) -> None:
    seed = monde.ecrire_seed([monde.amorce("generique", "demande", ligne=n) for n in (1, 2)])
    monde.faux.reponses = [reponse]
    resultat = monde.lancer({"generique": 2}, seed=seed)
    assert resultat.statut == "partiel-erreur"
    assert cause in resultat.bilan["motif"]
    assert len(monde.faux.corps) == 1
    assert monde.lignes(resultat, "brut.jsonl") == []


def test_changement_de_jour(monde: Any, doublures: Any) -> None:
    monde.jours = [doublures.JOUR, doublures.JOUR, doublures.JOUR + timedelta(days=1)]
    seed = monde.ecrire_seed([monde.amorce("generique", "demande", ligne=n) for n in (1, 2)])
    resultat = monde.lancer({"generique": 2}, seed=seed)
    assert resultat.statut == "partiel-erreur"
    assert "conditions Mistral à revérifier" in resultat.bilan["motif"]
    assert len(monde.faux.corps) == 1


# --- Estimation avant dépense (story 9.10) ----------------------------------------------------


def _estimations(lignes: list[tuple[str, int]]) -> dict[str, tuple[int, int]]:
    """{gabarit : (appels, appels faits au moment de l'affichage)} des lignes d'estimation."""
    resultat = {}
    for ligne, faits in lignes:
        if ligne.startswith("estimation ") and not ligne.startswith("estimation totale"):
            gabarit_id = ligne.split()[1]
            resultat[gabarit_id] = (int(ligne.split(" : ")[1].split()[0]), faits)
    return resultat


def test_estimation_affichee_avant_le_premier_appel(monde: Any, doublures: Any) -> None:
    seed = _seed_complet(monde, doublures)
    _scripter_rd(monde, doublures)
    lignes: list[tuple[str, int]] = []
    monde.lancer(TOUTES, seed=seed, consigner=lambda m: lignes.append((m, len(monde.faux.corps))))
    estimations = _estimations(lignes)
    assert {g: n for g, (n, _) in estimations.items()} == {
        "traces-q": 1,
        "traces-rd": TOURS_OUTILS_MAX + 1,
        "transcription-cr": 1,
        "cr": 1,
        "lc": 1,
        "generique": 1,
        "ct": 1,
        "re": 1,
        "co": 1,
    }
    assert all(faits == 0 for _, faits in estimations.values())
    (totale,) = [m for m, faits in lignes if m.startswith("estimation totale") and faits == 0]
    assert f"{TOURS_OUTILS_MAX + 9} appels" in totale and "€" in totale
    (rd,) = [m for m, _ in lignes if m.startswith("estimation traces-rd")]
    assert "max_tokens 800" in rd
    (cr,) = [m for m, _ in lignes if m.startswith("estimation cr ")]
    assert "max_tokens 1600" in cr


def test_estimation_en_reprise_deduit_le_journal(monde: Any, doublures: Any) -> None:
    seed = monde.ecrire_seed(
        [monde.amorce("generique", "demande", ligne=1), monde.amorce("RD", "demande", ligne=1)]
    )
    appel = doublures.appel_outil("search_datasets", {"query": doublures.factice()})
    monde.faux.reponses = [{"appels": [appel]}, KeyboardInterrupt()]
    with pytest.raises(KeyboardInterrupt):
        monde.lancer({"RD": 1, "generique": 1}, seed=seed)
    (run_id,) = [d.name for d in (monde.racine / "runs" / "data-generate").iterdir()]

    lignes: list[tuple[str, int]] = []
    monde.lancer(
        {"RD": 1, "generique": 1},
        reprendre=run_id,
        consigner=lambda m: lignes.append((m, 0)),
    )
    # Un appel RD déjà journalisé n'est pas compté ; la session generique reste entière.
    assert {g: n for g, (n, _) in _estimations(lignes).items()} == {
        "traces-rd": TOURS_OUTILS_MAX,
        "generique": 1,
    }
