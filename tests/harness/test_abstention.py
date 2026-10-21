"""Abstention de Q quand aucun passage ne répond (story 16.8). Textes factices (D1)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from harness_factices import (
    FakeEmbedder,
    FakeLlm,
    FakeVectorStore,
    SpyModePort,
    SpyToolPort,
    mots,
    passage,
    script,
)

from slmsp.core.evenements import (
    AppelOutil,
    Avertissement,
    Erreur,
    Fin,
    Jeton,
    Sources,
    VerificationPassages,
)
from slmsp.harness.abstention import (
    GRAMMAIRE_OUI_NON,
    charger_textes,
    lire_verdict,
    textes_defaut,
    verifier_passages,
)
from slmsp.harness.config import ConfigQAbstention
from slmsp.harness.prompts import construire_messages
from slmsp.harness.service import AssistantService
from slmsp.harness.taches import ContexteTache
from slmsp.inference.client import ClientLlama


def repondre(table, config, llm, passages, question, *, outils=None, mode=None):
    instance = AssistantService(
        llm,
        FakeEmbedder(),
        FakeVectorStore(passages),
        outils if outils is not None else SpyToolPort(),
        mode if mode is not None else SpyModePort(),
        config,
        taches=table,
    )
    evenements = list(instance.repondre("Q", [{"role": "user", "content": question}]))
    return evenements, None, None


@pytest.fixture
def config_actif(config_harnais):
    return config_harnais.model_copy(
        update={"q_abstention": ConfigQAbstention(actif=True, max_tokens=4)}
    )


def _passages(config) -> list[Any]:
    seuil = config.recherche.seuil_pertinence
    return [passage(1, seuil + 0.3), passage(2, seuil + 0.2)]


def test_desactivee_par_defaut_comportement_inchange(table, config_harnais) -> None:
    assert config_harnais.q_abstention.actif is False
    texte = f"{mots(5, 'a')} [1]."
    llm = FakeLlm(script(texte))
    evenements, _, _ = repondre(table, config_harnais, llm, _passages(config_harnais), "q")
    assert len(llm.appels) == 1
    assert not any(isinstance(e, VerificationPassages) for e in evenements)


def test_verdict_non_abstention_fixe(table, config_actif) -> None:
    llm = FakeLlm(script("non"), script("<réponse-factice-1>"))
    question = mots(6, "question")
    passages = _passages(config_actif)
    evenements, _, _ = repondre(table, config_actif, llm, passages, question)

    assert len(llm.appels) == 1  # aucune génération de réponse
    verdict, jeton, sources, alerte, fin = evenements
    assert verdict == VerificationPassages(verdict="non", abstention=True, sortie="non")
    assert jeton == Jeton(texte=textes_defaut().reponse)
    assert sources == Sources(sources=[])
    assert isinstance(alerte, Avertissement) and alerte.code == "avis-juridique"
    assert isinstance(fin, Fin) and fin.raison == "terminee" and fin.urls_inventees == []
    appel = llm.appels[0]
    assert appel["tools"] is None
    assert appel["options"]["grammar"] == GRAMMAIRE_OUI_NON
    assert appel["options"]["max_tokens"] == 4
    assert appel["messages"] == construire_messages(textes_defaut().tache, question, passages)


@pytest.mark.parametrize("sortie", ["oui", "<sortie-factice-illisible>"])
def test_verdict_oui_ou_illisible_flux_inchange(
    table, config_harnais, config_actif, sortie
) -> None:
    texte = f"{mots(8, 'a')} [1]. {mots(4, 'b')} [2]."
    question = mots(6, "question")
    passages = _passages(config_harnais)
    temoin, _, _ = repondre(table, config_harnais, FakeLlm(script(texte)), passages, question)
    llm = FakeLlm(script(sortie), script(texte))
    evenements, _, _ = repondre(table, config_actif, llm, passages, question)

    verdict, *suite = evenements
    attendu = "oui" if sortie == "oui" else "illisible"
    assert verdict.verdict == attendu and verdict.abstention is False
    # octet pour octet, hors usage : celui de la vérification s'ajoute à celui de la réponse
    *corps, fin = suite
    *corps_temoin, fin_temoin = temoin
    assert corps == corps_temoin
    assert fin.model_copy(update={"usage": None}) == fin_temoin.model_copy(update={"usage": None})
    assert fin.usage == {cle: 2 * v for cle, v in fin_temoin.usage.items()}
    assert len(llm.appels) == 2
    assert llm.appels[1]["messages"] == construire_messages(table.tache("Q"), question, passages)
    assert "grammar" not in (llm.appels[1]["options"] or {})


@pytest.mark.parametrize(
    ("sortie", "verdict"),
    [
        ("oui", "oui"),
        ("Non", "non"),
        (" non.\n", "non"),
        ("OUI", "oui"),
        ("non, mais", "illisible"),
        ("", "illisible"),
        ("<sortie-factice>", "illisible"),
    ],
)
def test_lecture_stricte(sortie: str, verdict: str) -> None:
    assert lire_verdict(sortie) == verdict


def _llama(corps_recus: list[dict[str, Any]], sortie: str) -> tuple[ClientLlama, list[Any]]:
    """`ClientLlama` sans serveur : le flux est simulé, l'observateur réel (story 17.6)."""
    llama = ClientLlama.__new__(ClientLlama)
    llama.protocole_outils, llama.chat_template_kwargs = "natif", {}
    mesures: list[Any] = []
    llama.observateur = type("Obs", (), {"mesurer": lambda self, m: mesures.append(m)})()
    llama.modele_mesure = "<slug>"

    def flux(corps: dict[str, Any], *_a: Any) -> Iterator[Any]:
        corps_recus.append(corps)
        yield Jeton(texte=sortie)
        yield Fin(raison="terminee", usage={"prompt_tokens": 30, "completion_tokens": 1})

    llama._flux_serveur = flux  # type: ignore[method-assign]
    return llama, mesures


def test_grammaire_envoyee_en_local_et_appel_mesure(table, config_actif) -> None:
    corps: list[dict[str, Any]] = []
    llama, mesures = _llama(corps, "non")
    ctx = ContexteTache(
        tache=table.tache("Q"),
        entree="q",
        historique=(),
        textes_saisis=("q",),
        llm=llama,
        config=config_actif,
        options_llm={"temperature": 0.0, "max_tokens": 1024},
    )
    verdict, fin = verifier_passages(ctx, "<question-factice>", _passages(config_actif))
    assert verdict.verdict == "non" and fin is not None and fin.usage
    (envoye,) = corps
    assert envoye["grammar"] == GRAMMAIRE_OUI_NON
    assert envoye["max_tokens"] == 4 and envoye["temperature"] == 0.0
    (mesure,) = mesures
    assert (mesure.fournisseur, mesure.tokens_entree, mesure.tokens_sortie) == ("local", 30, 1)


def test_textes_fixes_versionnes_hors_prompt_q(table) -> None:
    textes = charger_textes()
    assert textes.version >= 1
    assert textes.tache.prompt.emplacements == ("question", "passages")
    assert textes.tache.prompt.sha256 != table.tache("Q").prompt.sha256
    assert table.tache("Q").prompt.version == 1  # prompt principal de Q inchangé
    assert "http" not in textes.reponse  # aucune URL : jamais comptée inventée


def test_service_accepte_l_evenement(table, config_actif) -> None:
    llm = FakeLlm(script("non"))
    evenements, _, _ = repondre(
        table, config_actif, llm, [], "q", outils=SpyToolPort(), mode=SpyModePort()
    )
    assert isinstance(evenements[0], VerificationPassages)
    assert isinstance(evenements[-1], Fin)


def test_non_cumule_l_usage_et_la_coupure_de_verification(table, config_actif) -> None:
    coupee = [*script("non")[:-1], Fin(raison="longueur", usage={"prompt_tokens": 7})]
    evenements, _, _ = repondre(table, config_actif, FakeLlm(coupee), _passages(config_actif), "q")
    fin = evenements[-1]
    assert fin.raison == "longueur" and fin.usage["prompt_tokens"] == 7


@pytest.mark.parametrize(
    "anomalie", [Erreur(code="x", message="<m>"), AppelOutil(id="1", nom="o", arguments={})]
)
def test_erreur_ou_appel_outil_pendant_verification_est_illisible(
    table, config_actif, anomalie, caplog
) -> None:
    texte = f"{mots(5, 'a')} [1]."
    llm = FakeLlm([Jeton(texte="non"), anomalie], script(texte))
    with caplog.at_level("WARNING", logger="slmsp.harness"):
        evenements, _, _ = repondre(table, config_actif, llm, _passages(config_actif), "q")
    verdict = evenements[0]
    assert verdict.verdict == "illisible" and verdict.abstention is False
    assert len(llm.appels) == 2  # la réponse est générée
    assert any("vérification" in r.getMessage() for r in caplog.records)
    assert "<m>" not in caplog.text
