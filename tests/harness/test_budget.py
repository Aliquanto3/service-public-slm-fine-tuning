"""Budget de prompt et erreur de contexte dédiée (correctif F2).

`LlmBudget` est un `FakeLlm` doté de `taille_contexte` qui compte ses mesures ; un token vaut
un mot (`FakeLlm.compter_tokens`). Textes aléatoires (`mots`), aucun texte rédigé (D1.1).
"""

from __future__ import annotations

import logging
from typing import Any

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

from slmsp.core.evenements import Erreur, Fin, Sources
from slmsp.harness.budget import MARQUE_COUPE
from slmsp.harness.prompts import construire_messages
from slmsp.harness.service import CODE_CONTEXTE, MESSAGE_CONTEXTE, AssistantService
from slmsp.inference.client import ContexteServeurDepasse

SEUIL_OK = 0.9


class LlmBudget(FakeLlm):
    def __init__(self, *scripts: Any, taille_contexte: int | None) -> None:
        super().__init__(*scripts)
        if taille_contexte is not None:
            self.taille_contexte = taille_contexte
        self.mesures = 0

    def compter_tokens(self, messages: Any, tools: Any = None) -> int:
        self.mesures += 1
        return super().compter_tokens(messages, tools)


def passages(n: int) -> list:
    return [passage(i, SEUIL_OK - i / 100) for i in range(1, n + 1)]


def tokens(table, question: str, liste: list) -> int:
    return FakeLlm().compter_tokens(construire_messages(table.tache("Q"), question, liste))


def repondre(table, config, llm, liste, question, options=None) -> list:
    instance = AssistantService(
        llm,
        FakeEmbedder(),
        FakeVectorStore(liste),
        SpyToolPort(),
        SpyModePort(),
        config,
        taches=table,
    )
    return list(instance.repondre("Q", [{"role": "user", "content": question}], options))


def reserve(config) -> int:
    return config.generation.max_tokens


def test_tout_tient_comportement_inchange(table, config_harnais) -> None:
    question, liste = mots(6, "q"), passages(5)
    taille = tokens(table, question, liste) + reserve(config_harnais)
    llm = LlmBudget(script(mots(4, "r")), taille_contexte=taille)
    evenements = repondre(table, config_harnais, llm, liste, question)
    assert isinstance(evenements[-1], Fin)
    assert llm.appels[0]["messages"] == construire_messages(table.tache("Q"), question, liste)
    assert llm.mesures == 1


def test_sans_taille_contexte_aucune_mesure(table, config_harnais) -> None:
    question, liste = mots(6, "q"), passages(5)
    llm = LlmBudget(script(mots(4, "r")), taille_contexte=None)
    repondre(table, config_harnais, llm, liste, question)
    assert llm.appels[0]["messages"] == construire_messages(table.tache("Q"), question, liste)
    assert llm.mesures == 0


def test_passages_les_moins_bien_classes_retires(table, config_harnais) -> None:
    question, liste = mots(6, "q"), passages(5)
    taille = tokens(table, question, liste[:3]) + reserve(config_harnais)
    llm = LlmBudget(script(f"{mots(4, 'r')} [3]."), taille_contexte=taille)
    evenements = repondre(table, config_harnais, llm, liste, question)
    attendus = construire_messages(table.tache("Q"), question, liste[:3])
    assert llm.appels[0]["messages"] == attendus
    (sources,) = [e for e in evenements if isinstance(e, Sources)]
    assert [(s.numero, s.url) for s in sources.sources] == [(3, liste[2].url)]


def test_max_tokens_de_l_appelant_fixe_la_reserve(table, config_harnais) -> None:
    question, liste = mots(6, "q"), passages(5)
    taille = tokens(table, question, liste) + 50
    llm = LlmBudget(script(mots(4, "r")), taille_contexte=taille)
    repondre(table, config_harnais, llm, liste, question, {"max_tokens": 50})
    assert llm.appels[0]["messages"] == construire_messages(table.tache("Q"), question, liste)
    assert llm.appels[0]["options"] == {"max_tokens": 50}


def test_troncature_du_premier_passage_en_dernier_recours(table, config_harnais) -> None:
    question, liste = mots(6, "q"), passages(2)
    budget = tokens(table, question, []) + 20  # un passage complet en demande plus de 40
    llm = LlmBudget(script(mots(4, "r")), taille_contexte=budget + reserve(config_harnais))
    repondre(table, config_harnais, llm, liste, question)
    messages = llm.appels[0]["messages"]
    assert FakeLlm().compter_tokens(messages) <= budget
    contenu = messages[-1]["content"]
    assert liste[0].url in contenu and liste[1].url not in contenu
    assert MARQUE_COUPE.strip() in contenu
    debut = " ".join(liste[0].texte.split()[:3])
    assert debut in contenu and liste[0].texte not in contenu


def test_prompt_sans_passage_trop_long_erreur_dediee(table, config_harnais, caplog) -> None:
    question, liste = mots(6, "q"), passages(3)
    taille = tokens(table, question, []) - 1 + reserve(config_harnais)
    llm = LlmBudget(script(mots(4, "r")), taille_contexte=taille)
    with caplog.at_level(logging.WARNING, logger="slmsp.harness"):
        evenements = repondre(table, config_harnais, llm, liste, question)
    assert evenements == [Erreur(code=CODE_CONTEXTE, message=MESSAGE_CONTEXTE)]
    assert llm.appels == []
    assert "ContexteDepasse" in caplog.text and "sans passage" in caplog.text
    assert question not in caplog.text


def test_refus_du_serveur_pour_contexte_erreur_dediee(table, config_harnais, caplog) -> None:
    question = mots(6, "q")
    refus = ContexteServeurDepasse("HTTP 400 : exceed_context_size_error")
    llm = LlmBudget([refus], taille_contexte=None)
    with caplog.at_level(logging.WARNING, logger="slmsp.harness"):
        evenements = repondre(table, config_harnais, llm, passages(1), question)
    assert evenements == [Erreur(code=CODE_CONTEXTE, message=MESSAGE_CONTEXTE)]
    assert "ContexteServeurDepasse" in caplog.text
    assert "Traceback" not in caplog.text and 'File "' not in caplog.text
