"""Les six verrous AD-3 (« Claude ne génère aucune Donnée d'entraînement »), story 9.6.

Partie des verrous qui passe par le pipeline (extra `data` requis ; sans lui, ces tests
sont sautés avec un motif explicite). Les autres sont dans `test_verrous_ad3.py`. Chaque
verrou a ici un test rouge (le contournement est refusé ou détecté) et un test vert
(la voie légitime passe). Les contenus sont des jetons artificiels (D1.1) ; aucun appel d'API.
"""

from __future__ import annotations

import inspect
import json
from typing import Any

import pytest

pytest.importorskip(
    "mistralai", reason="verrous AD-3 du pipeline non vérifiés : `uv sync --extra data` requis"
)

from slmsp.core.artefacts import lire, nouveau_run  # noqa: E402
from slmsp.core.erreurs import (  # noqa: E402
    LectureInterdite,
    ManifesteInvalide,
    ProvenanceInvalide,
)
from slmsp.core.schemas.amorce import Amorce  # noqa: E402
from slmsp.core.var import dossier_var  # noqa: E402
from slmsp.data.build import rederiver_ligne  # noqa: E402
from slmsp.data.filter import lancer_filtre  # noqa: E402
from slmsp.data.validate import lancer_validation  # noqa: E402
from slmsp.mistral.generateur import Generateur  # noqa: E402

from .conftest import OUTILS_MCP  # noqa: E402
from .test_build import (  # noqa: E402
    PUBLIC,
    construire,
    contexte,
    pub,
    sessions,
    une_lc,
)
from .test_filter import (  # noqa: E402
    EmbedderFactice,
    items_vecteurs,
    journal_lecture,
    protection,
)

# --- Verrou 3 : requête prouvée -------------------------------------------------------------------


def test_verrou_3_pas_de_texte_libre() -> None:
    parametres = inspect.signature(Generateur.generer).parameters
    assert set(parametres) == {
        "self",
        "gabarit_id",
        "amorce_ids",
        "session_id",
        "tache",
        "messages_precedents",
    }


def test_verrou_3_message_assistant_non_prouve_refuse(monde: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("generique", "demande", ligne=1)])
    generateur = monde.generateur(seed, None)
    inventee = [{"role": "assistant", "content": "<reponse-inventee-factice>"}]
    with pytest.raises(ProvenanceInvalide):
        generateur.generer(
            "generique", ["generique.demande.jeu.1"], "session-v3", "generique", inventee
        )
    with pytest.raises(TypeError):
        generateur.generer(  # type: ignore[call-arg]
            "generique", ["generique.demande.jeu.1"], "s", "generique", texte="<libre-factice>"
        )
    assert monde.faux.corps == []  # rien n'est parti vers Mistral


def test_verrou_3_voie_legitime(monde: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("generique", "demande", ligne=1)])
    generation = monde.generateur(seed, None).generer(
        "generique", ["generique.demande.jeu.1"], "session-v3", "generique"
    )
    assert generation.messages[0]["role"] == "user" and len(monde.faux.corps) == 1


# --- Verrou 4 : réponse prouvée -------------------------------------------------------------------


def test_verrou_4_exemple_altere_d_un_octet(monde: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    from slmsp.data import build

    _, filtre = une_lc(monde)
    vrai = build.serialiser
    monkeypatch.setattr(build, "serialiser", lambda lignes: vrai(lignes).replace(b"0x", b"1x", 1))
    with pytest.raises(ProvenanceInvalide):
        construire(monde, filtre.run.run_id)
    assert not (monde.racine / "data" / "train").exists()


def test_verrou_4_appel_id_inconnu(monde: Any) -> None:
    generation, _ = une_lc(monde)
    (brut,) = sessions(generation)
    inconnu = brut.model_copy(update={"appel_ids": ["f" * 32]})
    with pytest.raises(ProvenanceInvalide):
        rederiver_ligne(contexte(monde, generation), inconnu)


def test_verrou_4_appel_de_validation_refuse(monde: Any) -> None:
    generation, _ = une_lc(monde)
    (brut,) = sessions(generation)
    corps = {
        "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "x"}}]
    }
    appel_id = monde.journal().inscrire(
        session_id="validation-v4",
        usage="validation",
        modele_demande="mistral-large-latest",
        modele_resolu="mistral-large-2512",
        requete={"messages": []},
        reponse_brute=json.dumps(corps).encode(),
        reservation_id=None,
        statut="ok",
        statut_http=200,
    )
    with pytest.raises(ProvenanceInvalide, match="validation"):
        rederiver_ligne(
            contexte(monde, generation), brut.model_copy(update={"appel_ids": [appel_id]})
        )


def test_verrou_4_appel_juge_second_refuse(monde: Any) -> None:
    from dataclasses import replace

    generation, _ = une_lc(monde)
    (brut,) = sessions(generation)
    ctx = contexte(monde, generation)
    ligne = ctx.lecteur.appel(brut.appel_ids[0])
    ctx.lecteur._lignes[ligne.appel_id] = replace(ligne, usage="juge-second")
    with pytest.raises(ProvenanceInvalide, match="juge-second"):
        rederiver_ligne(ctx, brut)


def test_verrou_4_voie_legitime(monde: Any) -> None:
    _, filtre = une_lc(monde)
    assert construire(monde, filtre.run.run_id).version == "v1"


# --- Verrou 5 : amorces et registre -----------------------------------------------------


def test_verrou_5_amorce_sans_origine_refusee(monde: Any) -> None:
    valeurs = monde.amorce("Q", "question", ligne=1, jeu=PUBLIC)
    for cle in ("jeu", "revision", "ligne"):
        sans = {k: v for k, v in valeurs.items() if k != cle}
        with pytest.raises(ValueError, match="amorce publique"):
            Amorce.model_validate(sans)
    mistral = {**valeurs, "auteur_contenu": "mistral"}
    with pytest.raises(ValueError):
        Amorce.model_validate(mistral)  # sans appel_id
    assert Amorce.model_validate(valeurs).auteur_contenu == "public"
    assert pub(monde, "Q", "question")["jeu"] == PUBLIC


# --- Verrou 6 : gabarits et verdicts ----------------------------------------------------


def test_verrou_6_aucun_chemin_de_verdict_en_entree(monde: Any) -> None:
    """Les entrées du pipeline sont des runs `data-*` : un run d'évaluation est refusé."""
    verdict = nouveau_run("eval-generation", "factice", {}, racine=monde.racine)
    verdict.terminer("complet")
    with pytest.raises(ManifesteInvalide):
        lancer_validation(
            racine=monde.racine,
            generate_run_id=verdict.run_id,
            journal=journal_lecture(),
            chemin_outils=OUTILS_MCP,
            consigner=lambda _ligne: None,
        )
    with pytest.raises(ManifesteInvalide):
        lancer_filtre(
            racine=monde.racine,
            validate_run_id=verdict.run_id,
            journal=journal_lecture(),
            protection=protection({}),
            vecteurs=items_vecteurs(),
            embedder=EmbedderFactice(),
            config=None,  # type: ignore[arg-type]
            consigner=lambda _ligne: None,
        )
    with pytest.raises(ManifesteInvalide):
        construire(monde, verdict.run_id)
    with pytest.raises(LectureInterdite):
        lire(dossier_var() / "verdicts.sqlite", "data", racine=monde.racine)
