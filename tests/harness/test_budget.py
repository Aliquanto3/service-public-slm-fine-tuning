"""Budget de prompt et erreur de contexte dédiée (correctif F2).

`LlmBudget` est un `FakeLlm` doté de `taille_contexte` qui compte ses mesures ; un token vaut
un mot (`FakeLlm.compter_tokens`). Textes aléatoires (`mots`), aucun texte rédigé (D1.1).
"""

from __future__ import annotations

import logging
import math
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

from slmsp.core.erreurs import ContexteDepasse
from slmsp.core.evenements import Erreur, Fin, Sources
from slmsp.harness.budget import BUDGET_MIN, MARQUE_COUPE
from slmsp.harness.config import ConfigGeneration
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


# --- Revue F2 : bornes, repli, réécriture, résultats d'outils -------------------------------


class LlmSansMesure(LlmBudget):
    """`/apply-template` en échec : la mesure lève."""

    def compter_tokens(self, messages: Any, tools: Any = None) -> int:
        self.mesures += 1
        raise RuntimeError("apply-template indisponible")


def service_de(table, config, llm, liste=(), **kw) -> AssistantService:
    return AssistantService(
        llm, FakeEmbedder(), FakeVectorStore(list(liste)), kw.get("outils", SpyToolPort()),
        kw.get("mode", SpyModePort()), config, taches=table,
    )  # fmt: skip


def test_mesure_en_echec_repli_sans_budget(table, config_harnais, caplog) -> None:
    question, liste = mots(6, "q"), passages(5)
    llm = LlmSansMesure(script(mots(4, "r")), taille_contexte=10_000)
    with caplog.at_level(logging.WARNING, logger="slmsp.harness"):
        evenements = repondre(table, config_harnais, llm, liste, question)
    assert isinstance(evenements[-1], Fin)
    assert llm.appels[0]["messages"] == construire_messages(table.tache("Q"), question, liste)
    assert "sans budget" in caplog.text and "apply-template" not in caplog.text


def test_max_tokens_qui_ne_laisse_rien_au_prompt_erreur_claire(
    table, config_harnais, caplog
) -> None:
    question = mots(6, "q")
    llm = LlmBudget(script(mots(4, "r")), taille_contexte=2048)
    with caplog.at_level(logging.WARNING, logger="slmsp.harness"):
        evenements = repondre(
            table, config_harnais, llm, passages(2), question, {"max_tokens": 2048}
        )
    assert evenements == [Erreur(code=CODE_CONTEXTE, message=MESSAGE_CONTEXTE)]
    assert llm.appels == [] and llm.mesures == 0
    assert "max_tokens 2048" in caplog.text


def test_eviction_lineaire_nombre_de_mesures(table, config_harnais) -> None:
    question, liste = mots(6, "q"), passages(5)
    taille = tokens(table, question, liste[:4]) + reserve(config_harnais)
    llm = LlmBudget(script(mots(4, "r")), taille_contexte=taille)
    repondre(table, config_harnais, llm, liste, question)
    assert llm.mesures == 2  # tout, puis sans le cinquième


def test_reecriture_plafond_proportionnel(table, config_harnais) -> None:
    llm = LlmBudget(script(mots(4, "r")), taille_contexte=None)
    texte = mots(2000, "tr")
    list(
        service_de(table, config_harnais, llm).repondre("TR", [{"role": "user", "content": texte}])
    )
    generation = config_harnais.generation
    prompt = FakeLlm().compter_tokens(llm.appels[0]["messages"])
    attendu = math.ceil(generation.facteur_reecriture * prompt) + generation.marge_reecriture
    assert attendu > generation.max_tokens
    assert llm.appels[0]["options"] == {"max_tokens": attendu}


def test_reecriture_texte_court_plafond_par_defaut(table, config_harnais) -> None:
    llm = LlmBudget(script(mots(4, "r")), taille_contexte=None)
    contenu = mots(5, "co")
    list(
        service_de(table, config_harnais, llm).repondre(
            "CO", [{"role": "user", "content": contenu}]
        )
    )
    assert llm.appels[0]["options"] == {"max_tokens": config_harnais.generation.max_tokens}


def test_reecriture_plafond_borne_par_le_contexte(table, config_harnais) -> None:
    texte = mots(2000, "tr")
    sonde = LlmBudget(script(""), taille_contexte=None)
    list(
        service_de(table, config_harnais, sonde).repondre(
            "TR", [{"role": "user", "content": texte}]
        )
    )
    prompt = FakeLlm().compter_tokens(sonde.appels[0]["messages"])
    llm = LlmBudget(script(mots(4, "r")), taille_contexte=prompt + 100)
    list(
        service_de(table, config_harnais, llm).repondre("TR", [{"role": "user", "content": texte}])
    )
    assert llm.appels[0]["options"] == {"max_tokens": 100}
    plein = LlmBudget(script(mots(4, "r")), taille_contexte=prompt)
    flux = service_de(table, config_harnais, plein).repondre(
        "TR", [{"role": "user", "content": texte}]
    )
    assert list(flux) == [Erreur(code=CODE_CONTEXTE, message=MESSAGE_CONTEXTE)]
    assert plein.appels == []


def test_plafond_par_tache_prioritaire(table, config_harnais) -> None:
    generation = ConfigGeneration(par_tache={"RE": 300, "TR": 2000})
    config = config_harnais.model_copy(update={"generation": generation})
    for code, attendu in (("RE", 300), ("TR", 2000), ("NR", generation.max_tokens)):
        llm = LlmBudget(script(mots(4, "r")), taille_contexte=None)
        list(
            service_de(table, config, llm).repondre(
                code, [{"role": "user", "content": mots(9, code)}]
            )
        )
        assert llm.appels[0]["options"] == {"max_tokens": attendu}, code


def test_resultats_d_outils_bornes_au_contexte(table, config_harnais) -> None:
    from slmsp.harness.budget import borner_resultats
    from slmsp.harness.taches import ContexteTache

    llm = LlmBudget(taille_contexte=None)
    base = [{"role": "system", "content": mots(10, "s")}, {"role": "user", "content": mots(5, "u")}]
    contenus = [mots(400, "r1"), mots(200, "r2")]

    def construire(liste):
        return [*base, *({"role": "tool", "content": c} for c in liste)]

    budget = 15 + 120
    llm.taille_contexte = budget + reserve(config_harnais)
    ctx = ContexteTache(
        tache=table.tache("RD"), entree="", historique=(), textes_saisis=(), llm=llm,
        config=config_harnais,
    )  # fmt: skip
    bornes = borner_resultats(ctx, contenus, construire, None)
    assert FakeLlm().compter_tokens(construire(bornes)) <= budget
    for borne, contenu in zip(bornes, contenus, strict=True):
        assert borne.endswith(MARQUE_COUPE) and borne.removesuffix(MARQUE_COUPE) in contenu
    # Tout tient : inchangé ; même le prompt sans résultat dépasse : erreur dédiée.
    llm.taille_contexte = 10_000
    assert borner_resultats(ctx, contenus, construire, None) == contenus
    llm.taille_contexte = 10 + reserve(config_harnais) + BUDGET_MIN
    with pytest.raises(ContexteDepasse):
        borner_resultats(ctx, contenus, lambda liste: [*base] * 10, None)


def test_boucle_rd_tronque_le_resultat_d_outil(table, config_harnais) -> None:
    from pathlib import Path

    from slmsp.core.evenements import AppelOutil
    from slmsp.harness.modes import ModeFixe
    from slmsp.harness.taches.recherche import messages_connecte
    from slmsp.mcp.bac_a_sable import BacASable
    from slmsp.mcp.cassettes import lire_cassette
    from slmsp.mcp.outils import charger_outils

    r001 = Path(__file__).resolve().parents[2] / "eval" / "calibrage" / "cassettes" / "R-001.json"
    requete = next(
        i.request for i in lire_cassette(r001).interactions if i.request["method"] == "tools/call"
    )
    appel = AppelOutil(
        id="c1", nom=requete["params"]["name"], arguments=requete["params"]["arguments"]
    )
    demande = mots(7, "demande")
    premier = messages_connecte(table.tache("RD"), demande, charger_outils())
    budget = FakeLlm().compter_tokens(premier) + 8
    llm = LlmBudget(
        [appel, Fin(raison="terminee", usage={"total_tokens": 1})],
        script(mots(4, "r")),
        taille_contexte=budget + reserve(config_harnais),
    )
    instance = service_de(
        table, config_harnais, llm, outils=BacASable([r001]), mode=ModeFixe("connecte")
    )
    evenements = list(instance.repondre("RD", [{"role": "user", "content": demande}]))
    assert isinstance(evenements[-1], Fin)
    second = llm.appels[1]["messages"]
    assert FakeLlm().compter_tokens(second) <= budget
    assert second[-1]["role"] == "tool" and second[-1]["content"].endswith(MARQUE_COUPE.strip())
