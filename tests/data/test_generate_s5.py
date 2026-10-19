"""Story S5 : `generate` par Tâche (`taches`, `completer_depuis`), Générateur en préversion,
MANIFEST du jeu (`generateur_preversion`). Doublures de `tests/data/conftest.py`, aucun appel
réel ; textes factices (D1)."""

from __future__ import annotations

from typing import Any

import pytest

pytest.importorskip("mistralai")

from slmsp.core.erreurs import ManifesteInvalide  # noqa: E402
from slmsp.core.schemas.entrainement import ManifesteJeuEntrainement  # noqa: E402
from slmsp.data.generate import modele_generateur_du_run  # noqa: E402

from .test_build import construire, pub, reponse  # noqa: E402
from .test_filter import filtrer, valider  # noqa: E402


def deux_taches(monde: Any) -> str:
    return monde.ecrire_seed([pub(monde, "LC", "texte"), pub(monde, "CO", "texte", 2)])


def test_taches_limite_le_plan(monde: Any) -> None:
    seed = deux_taches(monde)
    monde.faux.reponses = [reponse("lc")]
    resultat = monde.lancer({"LC": 1, "CO": 1}, seed=seed, taches=["LC"])
    assert resultat.statut == "complet"
    assert [s["tache"] for s in resultat.run.lire_jsonl("plan.jsonl")] == ["LC"]
    assert len(monde.faux.corps) == 1
    config = resultat.run.manifeste.config
    assert config["taches"] == ["LC"] and config["completer_depuis"] is None
    assert config["modele_generateur"] == "mistral-large-latest"
    assert config["generateur_preversion"] is False


def test_taches_invalides(monde: Any) -> None:
    seed = deux_taches(monde)
    with pytest.raises(ValueError, match="Tâches inconnues"):
        monde.lancer({"LC": 1}, seed=seed, taches=["XX"])
    with pytest.raises(ValueError, match="exige taches"):
        monde.lancer({"LC": 1}, seed=seed, completer_depuis="20261019-000000-generate-0000")


def test_completer_depuis_reprend_les_autres_taches_sans_appel(monde: Any) -> None:
    seed = deux_taches(monde)
    monde.faux.reponses = [reponse("lc"), reponse("co")]
    source = monde.lancer({"LC": 1, "CO": 1}, seed=seed)
    assert source.statut == "complet" and len(monde.faux.corps) == 2
    (co,) = [b for b in source.run.lire_jsonl("brut.jsonl") if b["tache"] == "CO"]

    monde.modele_generateur = "mistral-large-4"
    monde.faux.reponses = [{**reponse("lc4"), "model": "mistral-large-4-2610"}]
    compose = monde.lancer(
        {"LC": 1, "CO": 1}, seed=seed, taches=["LC"], completer_depuis=source.run.run_id
    )
    assert compose.statut == "complet"
    assert len(monde.faux.corps) == 3  # une seule session neuve : LC (session_id du modèle)
    plan = compose.run.lire_jsonl("plan.jsonl")
    assert [(s["tache"], s["rang"]) for s in plan] == [("LC", 0), ("CO", 1)]
    bruts = compose.run.lire_jsonl("brut.jsonl")
    assert [b for b in bruts if b["tache"] == "CO"] == [co]
    config = compose.run.manifeste.config
    assert config["comptes_plan"]["CO"] == {
        "planifiees": 1,
        "reprises": 1,
        "non_closes_source": 0,
    }
    assert config["modele_generateur"] == "mistral-large-4"
    assert config["generateur_preversion"] is True
    assert compose.run.manifeste.parents == [seed, source.run.run_id]
    assert modele_generateur_du_run(compose.run.run_id, racine=monde.racine) == "mistral-large-4"

    # Chaîne aval inchangée : validate, filter puis build sur le run composé.
    filtre = filtrer(monde, valider(monde, compose))
    resultat = construire(monde, filtre.run.run_id)
    manifeste = ManifesteJeuEntrainement.model_validate_json(
        (resultat.dossier / "MANIFEST.json").read_bytes()
    )
    assert manifeste.comptes_par_tache == {"CO": 1, "LC": 1}
    assert manifeste.modeles_generateurs == ["mistral-large-2512", "mistral-large-4-2610"]
    assert manifeste.generateur_preversion is True


def test_completer_depuis_compte_les_sessions_non_closes(monde: Any) -> None:
    seed = deux_taches(monde)
    monde.faux.reponses = [reponse("lc"), 500]
    source = monde.lancer({"LC": 1, "CO": 1}, seed=seed)
    assert source.statut == "partiel-erreur"
    monde.faux.reponses = [reponse("lc")]
    compose = monde.lancer(
        {"LC": 1, "CO": 1}, seed=seed, taches=["LC"], completer_depuis=source.run.run_id
    )
    comptes = compose.run.manifeste.config["comptes_plan"]["CO"]
    assert comptes == {"planifiees": 0, "reprises": 0, "non_closes_source": 1}


def test_manifeste_sans_preversion_inchange(monde: Any) -> None:
    seed = monde.ecrire_seed([pub(monde, "LC", "texte")])
    monde.faux.reponses = [reponse("lc")]
    generation = monde.lancer({"LC": 1}, seed=seed)
    resultat = construire(monde, filtrer(monde, valider(monde, generation)).run.run_id)
    brut = (resultat.dossier / "MANIFEST.json").read_text(encoding="utf-8")
    assert "generateur_preversion" not in brut


def test_completer_depuis_un_autre_seed_refuse(monde: Any) -> None:
    seed = deux_taches(monde)
    monde.faux.reponses = [reponse("co")]
    source = monde.lancer({"CO": 1}, seed=seed)
    autre = deux_taches(monde)
    with pytest.raises(ManifesteInvalide, match="seed"):
        monde.lancer({"LC": 1}, seed=autre, taches=["LC"], completer_depuis=source.run.run_id)


def test_reprise_avec_un_autre_modele_refusee(monde: Any) -> None:
    seed = deux_taches(monde)
    monde.faux.reponses = [500]
    run = monde.lancer({"LC": 1}, seed=seed).run
    assert run.statut_courant() == "partiel-erreur"
    monde.modele_generateur = "mistral-large-4"
    with pytest.raises(ManifesteInvalide, match="reprise refusée"):
        monde.lancer({"LC": 1}, reprendre=run.run_id)


def test_resolu_hors_preversion_refuse(monde: Any) -> None:
    seed = monde.ecrire_seed([pub(monde, "LC", "texte")])
    monde.modele_generateur = "mistral-large-4"
    monde.faux.reponses = [{**reponse("lc"), "model": "mistral-large-5"}]
    resultat = monde.lancer({"LC": 1}, seed=seed)
    assert resultat.statut == "partiel-erreur"
    assert "ModeleMistralRefuse" in (resultat.bilan["motif"] or "")
