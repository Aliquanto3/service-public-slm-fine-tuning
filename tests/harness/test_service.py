"""`AssistantService` : validation, flux, options, erreurs (story 4.2, AD-14, AD-7)."""

from __future__ import annotations

import dataclasses
import json
import logging
from types import MappingProxyType

import pytest
from harness_factices import (
    USAGE,
    FakeEmbedder,
    FakeLlm,
    FakeVectorStore,
    SpyModePort,
    SpyToolPort,
    jetons,
    mots,
    passage,
    script,
)

from slmsp.core.erreurs import SlmspError
from slmsp.core.evenements import (
    AppelNonConforme,
    AppelOutil,
    Avertissement,
    Erreur,
    Fin,
    Jeton,
    Sources,
    depuis_dict,
    vers_dict,
)
from slmsp.core.messages import ConversationInvalide, valider_conversation
from slmsp.harness import service as module_service
from slmsp.harness import taches as module_taches
from slmsp.harness.prompts import EntreeInvalide, construire_messages
from slmsp.harness.service import CODE_ERREUR, MASQUE, MESSAGE_ERREUR, AssistantService, masquer
from slmsp.harness.taches import (
    MOTIF_OUTIL_INATTENDU,
    ContexteTache,
    TableTaches,
    TacheInconnue,
    TacheIndisponible,
    diffuser,
    traitement,
)
from slmsp.harness.taches import question as module_question
from slmsp.harness.taches import redaction as module_redaction

TYPES = (Jeton, AppelOutil, AppelNonConforme, Sources, Avertissement, Fin, Erreur)


def user(texte: str) -> dict[str, str]:
    return {"role": "user", "content": texte}


def service(llm, table, config, *, passages=(), embedder=None, store=None, **autres):
    return AssistantService(
        llm,
        embedder if embedder is not None else FakeEmbedder(),
        store if store is not None else FakeVectorStore(passages),
        autres.pop("outils", SpyToolPort()),
        autres.pop("mode", SpyModePort()),
        config,
        taches=table,
        **autres,
    )


def sans_delai(evenements):
    """Évènements sérialisés, sans le délai au premier token (mesure de temps)."""
    sortie = []
    for evenement in evenements:
        donnees = vers_dict(evenement)
        if donnees["type"] == "fin" and donnees["usage"]:
            donnees["usage"].pop("delai_premier_token_ms", None)
        sortie.append(donnees)
    return sortie


# --- Sans état, types d'évènements ------------------------------------------------------


def test_deux_appels_meme_sortie(table, config_harnais) -> None:
    texte = mots(12, "sortie") + " [1]"
    llm = FakeLlm(script(texte))
    instance = service(llm, table, config_harnais, passages=[passage(1, 0.9)])
    conversation = [user(mots(5, "question"))]
    premier = list(instance.repondre(None, conversation))
    second = list(instance.repondre(None, conversation))
    assert sans_delai(premier) == sans_delai(second)
    assert llm.appels[0] == llm.appels[1]
    assert conversation == [user(mots(5, "question"))]  # la conversation n'est pas modifiée
    assert all(isinstance(e, TYPES) for e in premier)
    assert [depuis_dict(vers_dict(e)) for e in premier] == premier
    assert isinstance(premier[-1], Fin)


def test_tache_none_donne_question(table, config_harnais) -> None:
    llm = FakeLlm(script(mots(3, "x")))
    list(service(llm, table, config_harnais).repondre(None, [user(mots(4, "q"))]))
    assert llm.appels[0]["messages"][0]["content"] == table.tache("Q").prompt.consigne


def test_repondre_renvoie_un_generateur_paresseux(table, config_harnais) -> None:
    llm = FakeLlm(script(mots(3, "x")))
    store = FakeVectorStore([passage(1, 0.9)])
    flux = service(llm, table, config_harnais, store=store).repondre("Q", [user("abc")])
    assert llm.appels == [] and store.appels == []
    list(flux)
    assert len(llm.appels) == 1 and len(store.appels) == 1


# --- Options, usage, délai ----------------------------------------------------------------


def test_options_transmises_sans_entree_et_usage(table, config_harnais) -> None:
    llm = FakeLlm(script(mots(8, "lc")))
    texte = mots(20, "colle")
    options = {"temperature": 0, "seed": 7, "entree": {"texte": texte}}
    evenements = list(
        service(llm, table, config_harnais).repondre("LC", [user(texte)], options=options)
    )
    assert llm.appels[0]["options"] == {"temperature": 0, "seed": 7}
    assert options["entree"] == {"texte": texte}  # options de l'appelant intactes
    fin = evenements[-1]
    assert isinstance(fin, Fin)
    assert fin.usage is not None
    assert {k: fin.usage[k] for k in USAGE} == USAGE
    assert isinstance(fin.usage["delai_premier_token_ms"], int)
    assert fin.usage["delai_premier_token_ms"] >= 0


def test_sans_options_le_llm_recoit_none(table, config_harnais) -> None:
    llm = FakeLlm(script(mots(3, "x")))
    list(service(llm, table, config_harnais).repondre("NR", [user(mots(3, "d"))]))
    assert llm.appels[0]["options"] is None


def test_delai_mesure_par_le_service(table, config_harnais, monkeypatch) -> None:
    horloge = iter([10.0, 10.25])
    monkeypatch.setattr(module_service, "perf_counter", lambda: next(horloge))
    llm = FakeLlm(
        [Jeton(texte="a"), Jeton(texte="b"), Fin(raison="terminee", usage={"total_tokens": 3})]
    )
    fin = list(service(llm, table, config_harnais).repondre("NR", [user("abcd")]))[-1]
    assert fin.usage == {"total_tokens": 3, "delai_premier_token_ms": 250}


def test_sans_jeton_ni_usage(table, config_harnais) -> None:
    llm = FakeLlm([Fin(raison="terminee")])
    fin = list(service(llm, table, config_harnais).repondre("NR", [user("abcd")]))[-1]
    assert fin == Fin(raison="terminee")


# --- Conversation de plusieurs tours ------------------------------------------------------


def test_conversation_plusieurs_tours(table, config_harnais) -> None:
    llm = FakeLlm(script(mots(6, "r")))
    historique = [
        user(mots(4, "q1")),
        {"role": "assistant", "content": mots(9, "r1")},
        user(mots(4, "q2")),
        {"role": "assistant", "content": mots(9, "r2")},
    ]
    nouveau = mots(15, "colle")
    list(service(llm, table, config_harnais).repondre("CO", [*historique, user(nouveau)]))
    envoyes = llm.appels[0]["messages"]
    construits = construire_messages(table.tache("CO"), {"texte": nouveau})
    assert envoyes == [construits[0], *historique, construits[1]]
    assert len(valider_conversation(envoyes)) == 6
    assert llm.appels[0]["tools"] is None


def test_messages_pour_valide_la_conversation(table, config_harnais) -> None:
    ctx = ContexteTache(
        tache=table.tache("NR"),
        entree="x",
        historique=({"role": "tool", "tool_call_id": "absent", "content": "x"},),
        textes_saisis=(),
        llm=FakeLlm(),
        config=config_harnais,
    )
    with pytest.raises(ConversationInvalide):
        ctx.messages_pour(construire_messages(ctx.tache, "x"))


# --- Erreurs de l'appelant : levées au moment de l'appel ----------------------------------


@pytest.mark.parametrize(
    "messages",
    [
        [],
        [{"role": "system", "content": "abc"}, user("abc")],
        [user("abc"), {"role": "assistant", "content": "abc"}],
        [{"role": "inconnu", "content": "abc"}],
        [{"role": "tool", "tool_call_id": "a1", "content": "abc"}, user("abc")],
        "abc",
        None,
    ],
    ids=["vide", "system", "dernier-assistant", "role-inconnu", "tool-orphelin", "chaine", "none"],
)
def test_conversation_invalide_levee_tout_de_suite(table, config_harnais, messages) -> None:
    llm = FakeLlm()
    with pytest.raises(ConversationInvalide):
        service(llm, table, config_harnais).repondre("LC", messages)
    assert llm.appels == []


def test_tache_inconnue(table, config_harnais) -> None:
    with pytest.raises(TacheInconnue):
        service(FakeLlm(), table, config_harnais).repondre("ZZ", [user("abc")])


def test_rd_indisponible_avant_la_4_3(table, config_harnais) -> None:
    with pytest.raises(TacheIndisponible, match="recherche"):
        service(FakeLlm(), table, config_harnais).repondre("RD", [user("abc")])


def test_tache_inactive(table, config_harnais) -> None:
    taches = dict(table.taches)
    taches["LC"] = dataclasses.replace(taches["LC"], actif=False)
    inactive = TableTaches(taches=MappingProxyType(taches), code_defaut="Q")
    with pytest.raises(TacheIndisponible, match="inactive"):
        service(FakeLlm(), inactive, config_harnais).repondre("LC", [user("abc")])


def test_question_sans_index(table, config_harnais) -> None:
    instance = AssistantService(FakeLlm(), None, None, None, None, config_harnais, taches=table)
    with pytest.raises(TacheIndisponible, match="Index"):
        instance.repondre("Q", [user("abc")])
    list(instance.repondre("LC", [user("abc")]))  # la rédaction n'a pas besoin d'Index


@pytest.mark.parametrize(
    ("tache", "options"),
    [
        ("LC", {"entree": {"cle_inconnue": "abc"}}),
        ("LC", {"entree": {"texte": "   "}}),
        ("LC", {"entree": 3}),
        ("LC", {"entree": "abc"}),  # LC attend une entrée objet
        ("Q", {"entree": {"texte": "abc"}}),  # Q attend une entrée texte
        ("LC", ["pas", "un", "dict"]),
    ],
)
def test_entree_invalide_levee_tout_de_suite(table, config_harnais, tache, options) -> None:
    llm = FakeLlm()
    with pytest.raises(EntreeInvalide):
        service(llm, table, config_harnais).repondre(tache, [user("abc")], options=options)
    assert llm.appels == []


def test_entree_blanche(table, config_harnais) -> None:
    with pytest.raises(EntreeInvalide):
        service(FakeLlm(), table, config_harnais).repondre("NR", [user("   ")])


def test_erreurs_appelant_sont_slmsp(table, config_harnais) -> None:
    for erreur in (TacheIndisponible, TacheInconnue, EntreeInvalide, ConversationInvalide):
        assert issubclass(erreur, SlmspError)


# --- Entrée -------------------------------------------------------------------------------


def test_entree_objet_utilisee_telle_quelle(table, config_harnais) -> None:
    llm = FakeLlm(script(mots(4, "r")))
    entree = {"objet": mots(5, "objet"), "elements_connus": [mots(3, "e1"), mots(3, "e2")]}
    list(
        service(llm, table, config_harnais).repondre(
            "CT", [user(mots(2, "u"))], options={"entree": entree}
        )
    )
    assert llm.appels[0]["messages"] == construire_messages(table.tache("CT"), entree)


@pytest.mark.parametrize(("code", "cle"), [("LC", "texte"), ("CR", "notes"), ("CT", "objet")])
def test_entree_brute_tache_objet(table, config_harnais, code, cle) -> None:
    llm = FakeLlm(script(mots(4, "r")))
    texte = mots(10, f"brut-{code}")
    list(service(llm, table, config_harnais).repondre(code, [user(texte)]))
    assert llm.appels[0]["messages"] == construire_messages(table.tache(code), {cle: texte})


# --- Registre des traitements -------------------------------------------------------------


def test_registre_paresseux_et_repli(monkeypatch) -> None:
    assert traitement("Q") is module_question.traiter
    assert traitement("LC") is module_redaction.traiter
    assert traitement("CR") is module_redaction.traiter  # repli tant que la 4.4 manque
    assert traitement("Q") is traitement("Q")
    with pytest.raises(TacheInconnue):
        traitement("ZZ")
    modules = dict(module_taches.MODULES_TRAITEMENT)
    modules["LC"] = "module_absent"
    monkeypatch.setattr(module_taches, "MODULES_TRAITEMENT", MappingProxyType(modules))
    traitement.cache_clear()
    with pytest.raises(TacheIndisponible, match="module_absent"):
        traitement("LC")


def test_module_absent_leve_au_moment_de_l_appel(table, config_harnais, monkeypatch) -> None:
    modules = dict(module_taches.MODULES_TRAITEMENT)
    modules["CO"] = "module_absent"
    monkeypatch.setattr(module_taches, "MODULES_TRAITEMENT", MappingProxyType(modules))
    with pytest.raises(TacheIndisponible):
        service(FakeLlm(), table, config_harnais).repondre("CO", [user("abc")])


def test_contexte_redaction_sans_port_externe(table, config_harnais, monkeypatch) -> None:
    contextes: list[ContexteTache] = []

    def capturer(code):
        def traiter(ctx):
            contextes.append(ctx)
            yield Fin(raison="terminee")

        return traiter

    monkeypatch.setattr(module_service, "traitement", capturer)
    instance = service(FakeLlm(), table, config_harnais, passages=[passage(1, 0.9)])
    texte = mots(6, "ctx")
    list(instance.repondre("TR", [user(texte)], options={"seed": 1}))
    list(instance.repondre("Q", [user(texte)]))
    redaction, question = contextes
    assert redaction.recherche is None and redaction.outils is None and redaction.mode is None
    assert redaction.entree == {"texte": texte}
    assert dict(redaction.options_llm) == {"seed": 1}
    assert texte in redaction.textes_saisis
    assert question.recherche is instance.recherche
    assert question.outils is None and question.mode is None


# --- Erreurs d'exécution ------------------------------------------------------------------


def test_erreur_du_modele(table, config_harnais, caplog) -> None:
    secret = mots(6, "saisi-secret")
    llm = FakeLlm([*jetons(mots(3, "debut")), RuntimeError(f"panne en traitant {secret}")])
    with caplog.at_level(logging.ERROR, logger="slmsp.harness"):
        evenements = list(service(llm, table, config_harnais).repondre("LC", [user(secret)]))
    assert evenements[-1] == Erreur(code=CODE_ERREUR, message=MESSAGE_ERREUR)
    assert MESSAGE_ERREUR == "Un problème est survenu. Votre texte est conservé."
    assert not any(isinstance(e, Fin) for e in evenements)
    assert isinstance(evenements[0], Jeton)
    journal = caplog.text
    assert "RuntimeError" in journal and "panne en traitant" in journal
    assert MASQUE in journal
    assert secret not in journal
    assert "Traceback" not in journal and "_jouer" in journal  # pile, sans variables locales
    assert all(r.name == "slmsp.harness" for r in caplog.records)


def test_erreur_de_l_embedder(table, config_harnais, caplog) -> None:
    question = mots(5, "question-secrete")
    embedder = FakeEmbedder(erreur=OSError(f"embedder indisponible : {question!r}"))
    llm = FakeLlm()
    with caplog.at_level(logging.ERROR, logger="slmsp.harness"):
        evenements = list(
            service(llm, table, config_harnais, embedder=embedder).repondre("Q", [user(question)])
        )
    assert evenements == [Erreur(code=CODE_ERREUR, message=MESSAGE_ERREUR)]
    assert llm.appels == []
    assert "OSError" in caplog.text and question not in caplog.text


def test_flux_coupe_sans_fin(table, config_harnais) -> None:
    llm = FakeLlm(jetons(mots(4, "coupe")))
    evenements = list(service(llm, table, config_harnais).repondre("NR", [user("abcd")]))
    assert isinstance(evenements[-1], Fin) and evenements[-1].raison == "interrompue"


def test_traitement_sans_fin_ou_hors_evenements(table, config_harnais, monkeypatch) -> None:
    def sans_fin(code):
        def traiter(ctx):
            yield Jeton(texte="a")

        return traiter

    monkeypatch.setattr(module_service, "traitement", sans_fin)
    evenements = list(service(FakeLlm(), table, config_harnais).repondre("NR", [user("abcd")]))
    assert evenements == [Jeton(texte="a"), Erreur(code=CODE_ERREUR, message=MESSAGE_ERREUR)]

    def hors_type(code):
        def traiter(ctx):
            yield {"type": "jeton", "texte": "a"}

        return traiter

    monkeypatch.setattr(module_service, "traitement", hors_type)
    evenements = list(service(FakeLlm(), table, config_harnais).repondre("NR", [user("abcd")]))
    assert evenements == [Erreur(code=CODE_ERREUR, message=MESSAGE_ERREUR)]


def test_rien_apres_fin(table, config_harnais, monkeypatch) -> None:
    def bavard(code):
        def traiter(ctx):
            yield Fin(raison="terminee")
            yield Jeton(texte="apres")

        return traiter

    monkeypatch.setattr(module_service, "traitement", bavard)
    evenements = list(service(FakeLlm(), table, config_harnais).repondre("NR", [user("abcd")]))
    assert evenements == [Fin(raison="terminee")]


def test_appel_outil_inattendu(table, config_harnais) -> None:
    outils = SpyToolPort()
    llm = FakeLlm(
        [
            AppelOutil(id="a1", nom="search_datasets", arguments={"query": "abc"}),
            *jetons(mots(3, "x")),
            Fin(raison="terminee"),
        ]
    )
    evenements = list(
        service(llm, table, config_harnais, outils=outils).repondre("LC", [user("abcd")])
    )
    (refus,) = [e for e in evenements if isinstance(e, AppelNonConforme)]
    assert refus.nom == "search_datasets"
    assert refus.motif == MOTIF_OUTIL_INATTENDU
    assert refus.arguments_bruts == '{"query": "abc"}'
    assert not any(isinstance(e, AppelOutil) for e in evenements)
    assert outils.appels == [] and outils.gate.appels == []
    assert isinstance(evenements[-1], Fin)


def test_appel_non_conforme_du_modele_relaye(table, config_harnais) -> None:
    refus = AppelNonConforme(nom=None, arguments_bruts="{", motif="JSON invalide")
    llm = FakeLlm([refus, Fin(raison="terminee")])
    evenements = list(service(llm, table, config_harnais).repondre("NR", [user("abcd")]))
    assert evenements[0] == refus


# --- Masquage -----------------------------------------------------------------------------


def test_masquer() -> None:
    saisi = mots(4, "l1") + "\n" + mots(4, "l2")
    ligne = saisi.splitlines()[1]
    assert masquer(f"x {saisi} y", [saisi]) == f"x {MASQUE} y"
    assert masquer(f"x {ligne} y", [saisi]) == f"x {MASQUE} y"
    assert masquer(f"x {saisi!r} y", [saisi]) == f"x '{MASQUE}' y"
    assert masquer("abc", ["a"]) == "abc"  # fragment trop court : rien à masquer
    echappe = f'{mots(3, "j1")} "é" {mots(2, "j2")}'
    assert masquer(f"x {json.dumps(echappe)} y", [echappe]) == f'x "{MASQUE}" y'


def test_cles_de_l_entree_non_masquees(table, config_harnais, caplog) -> None:
    secret = mots(6, "secret-objet")
    llm = FakeLlm([RuntimeError(f"panne : texte manquant après {secret}")])
    with caplog.at_level(logging.ERROR, logger="slmsp.harness"):
        list(
            service(llm, table, config_harnais).repondre(
                "LC", [user(mots(2, "u"))], options={"entree": {"texte": secret}}
            )
        )
    assert "texte manquant" in caplog.text
    assert secret not in caplog.text


# --- Compléments : entrée texte par options, chemins d'échec, outils vides ---------------


def test_entree_texte_par_options(table, config_harnais) -> None:
    passages = [passage(1, 0.9), passage(2, 0.8)]
    embedder = FakeEmbedder()
    llm = FakeLlm(script(mots(4, "r")))
    affichee, entree = mots(5, "affichee"), mots(5, "entree-banc")
    instance = service(llm, table, config_harnais, passages=passages, embedder=embedder)
    list(instance.repondre("Q", [user(affichee)], options={"entree": entree, "seed": 1}))
    assert embedder.textes == [entree]
    ctx = ContexteTache(
        tache=table.tache("Q"),
        entree=entree,
        historique=(),
        textes_saisis=(),
        llm=llm,
        config=config_harnais,
    )
    attendus = ctx.messages_pour(construire_messages(table.tache("Q"), entree, passages))
    assert llm.appels[0]["messages"] == attendus
    assert llm.appels[0]["options"] == {"seed": 1}


def test_fermeture_du_flux_ferme_le_modele(table, config_harnais) -> None:
    llm = FakeLlm(script(mots(20, "long")))
    flux = service(llm, table, config_harnais).repondre("LC", [user("abcd")])
    assert isinstance(next(flux), Jeton)
    flux.close()
    assert llm.fermetures == 1


def test_erreur_du_vector_store(table, config_harnais) -> None:
    store = FakeVectorStore(erreur=OSError("index illisible"))
    llm = FakeLlm()
    instance = service(llm, table, config_harnais, store=store)
    evenements = list(instance.repondre("Q", [user("abcd")]))
    assert evenements == [Erreur(code=CODE_ERREUR, message=MESSAGE_ERREUR)]
    assert store.appels and llm.appels == []


def test_diffuser_liste_d_outils_vide(table, config_harnais) -> None:
    appel = AppelOutil(id="a1", nom="search_datasets", arguments={})
    llm = FakeLlm([appel, Fin(raison="terminee")])
    ctx = ContexteTache(
        tache=table.tache("NR"),
        entree="abcd",
        historique=(),
        textes_saisis=(),
        llm=llm,
        config=config_harnais,
    )
    (refus,) = list(diffuser(ctx, [user("abcd")], tools=[]))
    assert isinstance(refus, AppelNonConforme) and refus.motif == MOTIF_OUTIL_INATTENDU
    outil = {"type": "function", "function": {"name": "search_datasets"}}
    assert list(diffuser(ctx, [user("abcd")], tools=[outil])) == [appel]
