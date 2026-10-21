"""Question (Q) fondée sur l'Index local : sources, avertissement, URL inventées (story 4.2)."""

from __future__ import annotations

from harness_factices import (
    FakeEmbedder,
    FakeLlm,
    FakeVectorStore,
    SpyModePort,
    SpyToolPort,
    mots,
    passage,
    script,
    url_factice,
)

from slmsp.core.evenements import Avertissement, Fin, Jeton, Source, Sources
from slmsp.harness.citations import extrait
from slmsp.harness.prompts import AUCUN_PASSAGE, construire_messages
from slmsp.harness.service import AssistantService


def repondre(table, config, llm, passages, question, *, embedder=None, outils=None, mode=None):
    store = FakeVectorStore(passages)
    embedder = embedder if embedder is not None else FakeEmbedder()
    instance = AssistantService(
        llm,
        embedder,
        store,
        outils if outils is not None else SpyToolPort(),
        mode if mode is not None else SpyModePort(),
        config,
        taches=table,
    )
    evenements = list(instance.repondre("Q", [{"role": "user", "content": question}]))
    return evenements, store, embedder


def source(numero: int, p) -> Source:
    return Source(
        numero=numero,
        titre=p.titre,
        url=p.url,
        origine="index",
        date=p.date_snapshot,
        extrait=extrait(p.texte),
    )


def test_question_avec_passages(table, config_harnais) -> None:
    seuil = config_harnais.recherche.seuil_pertinence
    passages = [passage(1, seuil + 0.3), passage(2, seuil + 0.2), passage(3, seuil + 0.1)]
    texte = f"{mots(8, 'a')} [1]. {mots(6, 'b')} [3] {mots(4, 'c')} [1]."
    llm = FakeLlm(script(texte))
    outils, mode = SpyToolPort(), SpyModePort()
    question = mots(6, "question")
    evenements, store, embedder = repondre(
        table, config_harnais, llm, passages, question, outils=outils, mode=mode
    )

    types = [type(e) for e in evenements]
    nb_jetons = types.count(Jeton)
    assert nb_jetons > 1
    assert types == [Jeton] * nb_jetons + [Sources, Avertissement, Fin]
    assert "".join(e.texte for e in evenements[:nb_jetons]) == texte
    sources, alerte, fin = evenements[nb_jetons:]
    assert sources == Sources(sources=[source(1, passages[0]), source(3, passages[2])])
    assert alerte == Avertissement(code="avis-juridique", message="Ne vaut pas avis juridique.")
    assert fin.raison == "terminee" and fin.urls_inventees == []

    assert embedder.textes == [question]
    assert store.appels == [config_harnais.question.passages]  # k propre à Q (16.2)
    appel = llm.appels[0]
    assert appel["tools"] is None
    assert appel["messages"] == construire_messages(table.tache("Q"), question, passages)
    assert outils.appels == [] and mode.appels == []


def test_question_sans_passage_pertinent(table, config_harnais) -> None:
    seuil = config_harnais.recherche.seuil_pertinence
    passages = [passage(1, seuil - 0.01), passage(2, seuil - 0.2)]
    llm = FakeLlm(script(mots(10, "sans") + " [1]"))
    evenements, _, _ = repondre(table, config_harnais, llm, passages, mots(4, "q"))
    assert AUCUN_PASSAGE in llm.appels[0]["messages"][1]["content"]
    assert passages[0].url not in llm.appels[0]["messages"][1]["content"]
    assert [type(e) for e in evenements[-3:]] == [Sources, Avertissement, Fin]
    assert evenements[-3] == Sources(sources=[])
    assert evenements[-1].raison == "terminee"


def test_passage_au_seuil_est_pertinent(table, config_harnais) -> None:
    seuil = config_harnais.recherche.seuil_pertinence
    passages = [passage(1, seuil)]
    llm = FakeLlm(script("[1]"))
    evenements, _, _ = repondre(table, config_harnais, llm, passages, mots(4, "q"))
    assert evenements[-3] == Sources(sources=[source(1, passages[0])])


def test_citation_hors_plage_ignoree(table, config_harnais) -> None:
    passages = [passage(1, 0.9), passage(2, 0.8)]
    llm = FakeLlm(script(f"{mots(5, 'x')} [9] {mots(3, 'y')} [2]"))
    evenements, _, _ = repondre(table, config_harnais, llm, passages, mots(4, "q"))
    assert evenements[-3] == Sources(sources=[source(2, passages[1])])


def test_reponse_sans_renvoi_donne_sources_vides(table, config_harnais) -> None:
    llm = FakeLlm(script(mots(12, "sans-renvoi")))
    evenements, _, _ = repondre(table, config_harnais, llm, [passage(1, 0.9)], mots(4, "q"))
    assert evenements[-3] == Sources(sources=[])


def test_url_inventee_signalee_texte_intact(table, config_harnais) -> None:
    passages = [passage(1, 0.9), passage(2, 0.8)]
    inventee = url_factice("inventee")
    dans_question = url_factice("question")
    texte = (
        f"{mots(5, 'u')} {passages[0].url}/ [1], {dans_question} "
        f"et {inventee}. {mots(3, 'v')} {inventee}"
    )
    llm = FakeLlm(script(texte))
    question = f"{mots(4, 'q')} {dans_question}"
    evenements, _, _ = repondre(table, config_harnais, llm, passages, question)
    assert "".join(e.texte for e in evenements if isinstance(e, Jeton)) == texte
    assert evenements[-1].urls_inventees == [inventee]


def test_fin_du_modele_conservee(table, config_harnais) -> None:
    llm = FakeLlm([Jeton(texte="[1]"), Fin(raison="longueur", usage={"total_tokens": 5})])
    evenements, _, _ = repondre(table, config_harnais, llm, [passage(1, 0.9)], mots(4, "q"))
    fin = evenements[-1]
    assert isinstance(fin, Fin) and fin.raison == "longueur"
    assert fin.usage["total_tokens"] == 5 and "delai_premier_token_ms" in fin.usage


def test_url_d_un_resultat_d_outil_de_l_historique(table, config_harnais) -> None:
    connue = url_factice("outil")
    llm = FakeLlm(script(f"{mots(3, 'r')} {connue}"))
    conversation = [
        {"role": "user", "content": mots(3, "q1")},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "a1",
                    "type": "function",
                    "function": {"name": "search_datasets", "arguments": "{}"},
                }
            ],
        },
        {"role": "tool", "tool_call_id": "a1", "content": f'{{"data": [{{"url": "{connue}"}}]}}'},
        {"role": "assistant", "content": mots(4, "r1")},
        {"role": "user", "content": mots(3, "q2")},
    ]
    instance = AssistantService(
        llm,
        FakeEmbedder(),
        FakeVectorStore([passage(1, 0.9)]),
        SpyToolPort(),
        SpyModePort(),
        config_harnais,
        taches=table,
    )
    evenements = list(instance.repondre("Q", conversation))
    assert evenements[-1].urls_inventees == []
    assert llm.appels[0]["messages"][1:-1] == conversation[:-1]
