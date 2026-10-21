"""`ClientLlama` (LlmPort) contre le serveur factice : flux SSE, outils, usage, erreurs."""

from __future__ import annotations

import json
import re
from types import SimpleNamespace
from typing import Any

import jsonschema
import pytest

from slmsp.core.erreurs import ContexteDepasse
from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton
from slmsp.core.ports import LlmPort
from slmsp.inference import client as client_module
from slmsp.inference.client import (
    ClientLlama,
    ContexteServeurDepasse,
    appel_canonique,
    est_depassement_contexte,
    schema_json_generique,
)
from slmsp.inference.processus import ErreurInference

MESSAGES = [
    {"role": "system", "content": "<système-factice>"},
    {"role": "user", "content": "<question-factice>"},
]
OUTILS = [
    {
        "type": "function",
        "function": {
            "name": "chercher",
            "description": "<description-factice>",
            "parameters": {
                "type": "object",
                "properties": {"q": {"type": "string"}},
                "required": ["q"],
            },
        },
    },
    {"type": "function", "function": {"name": "heure"}},
]


@pytest.fixture
def client(serveur_factice: Any) -> Any:
    with ClientLlama(serveur_factice.port) as instance:
        yield instance


def _appel(index: int, *, id: str | None = None, nom: str | None = None, args: str = "") -> dict:
    fragment: dict[str, Any] = {"index": index, "function": {"arguments": args}}
    if id is not None:
        fragment["id"] = id
        fragment["type"] = "function"
    if nom is not None:
        fragment["function"]["name"] = nom
    return fragment


def test_est_un_llmport(client: ClientLlama) -> None:
    assert isinstance(client, LlmPort)


def test_taille_contexte(client: ClientLlama, serveur_factice: Any) -> None:
    """Attribut optionnel lu par le Harnais (story 4.4), hors du `Protocol` `LlmPort`."""
    assert client.taille_contexte is None
    with ClientLlama(serveur_factice.port, taille_contexte=2048) as instance:
        assert instance.taille_contexte == 2048
        assert isinstance(instance, LlmPort)


def test_flux_texte(client: ClientLlama, serveur_factice: Any) -> None:
    evenements = list(
        client.generer(MESSAGES, tools=OUTILS, options={"temperature": 0, "seed": 42})
    )
    assert evenements[:-1] == [Jeton(texte="Bon"), Jeton(texte="jour")]
    fin = evenements[-1]
    assert isinstance(fin, Fin) and fin.raison == "terminee"
    assert fin.usage is not None
    assert {k: fin.usage[k] for k in ("prompt_tokens", "completion_tokens", "total_tokens")} == {
        "prompt_tokens": 7,
        "completion_tokens": 2,
        "total_tokens": 9,
    }
    assert fin.usage["delai_premier_token_ms"] >= 0
    (corps,) = serveur_factice.corps("/v1/chat/completions")
    assert corps["messages"] == MESSAGES  # transmis tels quels (AD-7)
    assert corps["temperature"] == 0 and corps["seed"] == 42
    assert corps["stream"] is True
    assert corps["stream_options"] == {"include_usage": True}
    assert corps["tools"] == OUTILS
    assert "response_format" not in corps


def test_options_transmises_et_kwargs_fusionnes(serveur_factice: Any) -> None:
    with ClientLlama(serveur_factice.port, chat_template_kwargs={"a": 1, "b": 1}) as client:
        options = {
            "max_tokens": 5,
            "top_p": 0.9,
            "top_k": 40,
            "stop": ["\n"],
            "chat_template_kwargs": {"b": 2},
        }
        list(client.generer(MESSAGES, options=options))
    (corps,) = serveur_factice.corps("/v1/chat/completions")
    assert corps["max_tokens"] == 5 and corps["top_p"] == 0.9 and corps["top_k"] == 40
    assert corps["stop"] == ["\n"]
    assert corps["chat_template_kwargs"] == {"a": 1, "b": 2}
    assert "tools" not in corps


def test_option_inconnue_refusee_avant_requete(client: ClientLlama, serveur_factice: Any) -> None:
    with pytest.raises(ValueError, match="frequency_penalty"):
        client.generer(MESSAGES, options={"frequency_penalty": 1})
    assert serveur_factice.requetes == []


def test_appels_natifs_fragmentes(client: ClientLlama, serveur_factice: Any, factice) -> None:
    serveur_factice.scenario.chat = [
        factice.morceau(tool_calls=[_appel(0, id="call_a", nom="chercher", args='{"q": ')]),
        factice.morceau(tool_calls=[_appel(1, id="call_b", nom="heure", args="")]),
        factice.morceau(tool_calls=[_appel(0, args='"impôts"}')]),
        factice.morceau(tool_calls=[_appel(2, id="call_c", nom="chercher", args="[1, 2]")]),
        factice.morceau(tool_calls=[_appel(3, id="call_d", nom="chercher", args="{cassé")]),
        factice.morceau(finish_reason="tool_calls"),
        factice.morceau_usage(),
        "[DONE]",
    ]
    evenements = list(client.generer(MESSAGES, tools=OUTILS))
    assert evenements[:-1] == [
        AppelOutil(id="call_a", nom="chercher", arguments={"q": "impôts"}),
        AppelOutil(id="call_b", nom="heure", arguments={}),
        AppelNonConforme(
            nom="chercher", arguments_bruts="[1, 2]", motif="arguments : objet JSON attendu"
        ),
        AppelNonConforme(
            nom="chercher", arguments_bruts="{cassé", motif="arguments : JSON illisible"
        ),
    ]
    assert evenements[-1].raison == "terminee"


def test_longueur(client: ClientLlama, serveur_factice: Any, factice) -> None:
    serveur_factice.scenario.chat = factice.flux_texte("a", "b", raison="length")
    *_, fin = client.generer(MESSAGES)
    assert fin.raison == "longueur"


def test_flux_coupe(client: ClientLlama, serveur_factice: Any, factice) -> None:
    serveur_factice.scenario.chat = [factice.morceau("a"), factice.morceau("b")]
    evenements = list(client.generer(MESSAGES))
    assert evenements[:-1] == [Jeton(texte="a"), Jeton(texte="b")]
    assert evenements[-1].raison == "interrompue"
    assert evenements[-1].usage == {
        "delai_premier_token_ms": evenements[-1].usage["delai_premier_token_ms"]
    }


def test_flux_coupe_sans_rien(client: ClientLlama, serveur_factice: Any) -> None:
    serveur_factice.scenario.chat = []
    assert list(client.generer(MESSAGES)) == [Fin(raison="interrompue", usage=None)]


def test_corps_coupe_en_plein_flux(client: ClientLlama, serveur_factice: Any, factice) -> None:
    """Content-Length jamais atteint : erreur de transport absorbée, flux interrompu."""
    serveur_factice.scenario.chat = [factice.morceau("a")]
    serveur_factice.scenario.corps_tronque = True
    evenements = list(client.generer(MESSAGES))
    assert evenements[0] == Jeton(texte="a")
    assert len(evenements) == 2
    assert isinstance(evenements[1], Fin) and evenements[1].raison == "interrompue"


def test_raisonnement_compte_pour_le_premier_token(
    client: ClientLlama, serveur_factice: Any, factice
) -> None:
    raisonnement = factice.morceau()
    raisonnement["choices"][0]["delta"]["reasoning_content"] = "<pensée>"
    serveur_factice.scenario.chat = [raisonnement, *factice.flux_texte("ok")]
    instants = iter([0.0, 0.25, 9.0])  # début, raisonnement, contenu
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(client_module, "time", SimpleNamespace(perf_counter=lambda: next(instants)))
        evenements = list(client.generer(MESSAGES))
    assert evenements[:-1] == [Jeton(texte="ok")]  # le raisonnement n'est pas émis
    assert evenements[-1].usage["delai_premier_token_ms"] == 250


@pytest.mark.parametrize("statut", [400, 500])
def test_http_erreur(client: ClientLlama, serveur_factice: Any, statut: int) -> None:
    serveur_factice.scenario.statut_chat = statut
    with pytest.raises(ErreurInference, match=f"HTTP {statut}.*requête refusée"):
        list(client.generer(MESSAGES))


def test_erreur_en_flux(client: ClientLlama, serveur_factice: Any, factice) -> None:
    serveur_factice.scenario.chat = [factice.morceau("a"), {"error": {"message": "contexte"}}]
    with pytest.raises(ErreurInference, match="contexte"):
        list(client.generer(MESSAGES))


# --- json-generique ----------------------------------------------------------------------------


@pytest.fixture
def client_json(serveur_factice: Any) -> Any:
    with ClientLlama(serveur_factice.port, protocole_outils="json-generique") as instance:
        yield instance


def _flux_json(factice, objet: Any) -> list[Any]:
    texte = objet if isinstance(objet, str) else json.dumps(objet, ensure_ascii=False)
    moitie = len(texte) // 2
    return factice.flux_texte(texte[:moitie], texte[moitie:])


def test_json_generique_requete(client_json: ClientLlama, serveur_factice: Any, factice) -> None:
    serveur_factice.scenario.chat = _flux_json(
        factice, {"tool_calls": [{"name": "chercher", "arguments": {"q": "x"}}]}
    )
    evenements = list(client_json.generer(MESSAGES, tools=OUTILS))
    (corps,) = serveur_factice.corps("/v1/chat/completions")
    assert "tools" not in corps
    assert corps["messages"] == MESSAGES
    format_reponse = corps["response_format"]
    assert format_reponse["type"] == "json_schema"
    assert format_reponse["json_schema"]["schema"] == schema_json_generique(OUTILS)
    (appel,) = evenements[:-1]
    assert isinstance(appel, AppelOutil)
    assert (appel.nom, appel.arguments) == ("chercher", {"q": "x"})
    assert re.fullmatch(r"appel-[0-9a-f]{32}", appel.id)
    assert evenements[-1].raison == "terminee"


def test_identifiants_uniques(
    client: ClientLlama, client_json: ClientLlama, serveur_factice: Any, factice
) -> None:
    """Ids générés (json-generique, natif sans id) uniques d'un tour à l'autre."""
    ids = []
    for _ in range(2):
        serveur_factice.scenario.chat = _flux_json(
            factice,
            {
                "tool_calls": [
                    {"name": "heure", "arguments": {}},
                    {"name": "heure", "arguments": {}},
                ]
            },
        )
        ids += [e.id for e in client_json.generer(MESSAGES, tools=OUTILS) if not isinstance(e, Fin)]
        serveur_factice.scenario.chat = [
            factice.morceau(tool_calls=[_appel(0, nom="heure", args="{}")]),
            factice.morceau(finish_reason="tool_calls"),
            "[DONE]",
        ]
        ids += [e.id for e in client.generer(MESSAGES, tools=OUTILS) if not isinstance(e, Fin)]
    assert len(ids) == 6 and len(set(ids)) == 6
    assert all(re.fullmatch(r"appel-[0-9a-f]{32}", i) for i in ids)


def test_json_generique_contenu(client_json: ClientLlama, serveur_factice: Any, factice) -> None:
    serveur_factice.scenario.chat = _flux_json(factice, {"content": "réponse"})
    evenements = list(client_json.generer(MESSAGES, tools=OUTILS))
    assert evenements[:-1] == [Jeton(texte="réponse")]


def test_json_generique_illisible(client_json: ClientLlama, serveur_factice: Any, factice) -> None:
    serveur_factice.scenario.chat = _flux_json(factice, "pas du json")
    evenements = list(client_json.generer(MESSAGES, tools=OUTILS))
    assert evenements[:-1] == [Jeton(texte="pas du json")]


def test_json_generique_sans_outils(
    client_json: ClientLlama, serveur_factice: Any, factice
) -> None:
    evenements = list(client_json.generer(MESSAGES))
    assert evenements[:-1] == [Jeton(texte="Bon"), Jeton(texte="jour")]
    (corps,) = serveur_factice.corps("/v1/chat/completions")
    assert "response_format" not in corps


def test_schema_json_generique_valide() -> None:
    schema = schema_json_generique(OUTILS)
    jsonschema.Draft202012Validator.check_schema(schema)
    valide = jsonschema.Draft202012Validator(schema)
    assert valide.is_valid({"tool_calls": [{"name": "chercher", "arguments": {"q": "a"}}]})
    assert valide.is_valid({"tool_calls": [{"name": "heure", "arguments": {}}]})
    assert valide.is_valid({"content": "texte"})
    assert not valide.is_valid({"tool_calls": [{"name": "inconnu", "arguments": {}}]})
    assert not valide.is_valid({"tool_calls": [{"name": "chercher", "arguments": {}}]})
    assert not valide.is_valid({"tool_calls": []})
    assert not valide.is_valid({"autre": 1})
    with pytest.raises(ValueError):
        schema_json_generique([{"name": "plat"}])


def test_appel_canonique() -> None:
    appel = AppelOutil(id="call_1", nom="chercher", arguments={"q": "impôts"})
    assert appel_canonique(appel) == {
        "id": "call_1",
        "type": "function",
        "function": {"name": "chercher", "arguments": '{"q": "impôts"}'},
    }


# --- compter_tokens -------------------------------------------------------------------------


def test_compter_tokens(client: ClientLlama, serveur_factice: Any) -> None:
    nombre = client.compter_tokens(MESSAGES, OUTILS)
    (gabarit,) = serveur_factice.corps("/apply-template")
    assert gabarit["messages"] == MESSAGES and gabarit["tools"] == OUTILS
    (tokenize,) = serveur_factice.corps("/tokenize")
    assert nombre == len(tokenize["content"].split())
    assert tokenize["content"].startswith("<|system|>")


def test_compter_tokens_transmet_les_kwargs(serveur_factice: Any) -> None:
    """Revue lot 3b, P4 : le compte porte sur le rendu que `generer` produira."""
    with ClientLlama(serveur_factice.port, chat_template_kwargs={"a": 1}) as client:
        client.compter_tokens(MESSAGES, OUTILS)
    (gabarit,) = serveur_factice.corps("/apply-template")
    assert gabarit["chat_template_kwargs"] == {"a": 1}


def test_compter_tokens_sans_kwargs(client: ClientLlama, serveur_factice: Any) -> None:
    client.compter_tokens(MESSAGES, OUTILS)
    (gabarit,) = serveur_factice.corps("/apply-template")
    assert "chat_template_kwargs" not in gabarit


def test_compter_tokens_json_generique_sans_outils(
    client_json: ClientLlama, serveur_factice: Any
) -> None:
    client_json.compter_tokens(MESSAGES, OUTILS)
    (gabarit,) = serveur_factice.corps("/apply-template")
    assert "tools" not in gabarit


def test_protocole_inconnu() -> None:
    with pytest.raises(ValueError, match="protocole"):
        ClientLlama(8080, protocole_outils="xml")


# --- balises-tool-call (SmolLM3) ----------------------------------------------------------------

BALISES = "balises-tool-call"


@pytest.fixture
def client_balises(serveur_factice: Any) -> Any:
    with ClientLlama(serveur_factice.port, protocole_outils=BALISES) as instance:
        yield instance


def _decouper(texte: str, taille: int) -> list[str]:
    return [texte[i : i + taille] for i in range(0, len(texte), taille)]


# Format observé (run eval-generation 20261016-193650-smollm3-3b-8a06, items RD) : appel en
# balises dans le texte, parfois suivi d'un résultat inventé, puis d'un autre appel ; valeurs
# factices.
SORTIE_BALISES = (
    '\n<tool_call>\n{"name": "chercher", "arguments": {"q": "<requete-factice>"}}\n</tool_call>'
    "\n\n<resultat-invente-factice>\n"
    '<tool_call>\n{"name": "heure", "arguments": {}}\n</tool_call>'
)


@pytest.mark.parametrize("taille", [1, 3, 7, len(SORTIE_BALISES)])
def test_balises_appel_et_texte(
    client_balises: ClientLlama, serveur_factice: Any, factice, taille: int
) -> None:
    serveur_factice.scenario.chat = factice.flux_texte(*_decouper(SORTIE_BALISES, taille))
    evenements = list(client_balises.generer(MESSAGES, tools=OUTILS))
    (corps,) = serveur_factice.corps("/v1/chat/completions")
    assert corps["tools"] == OUTILS and "response_format" not in corps
    assert corps["stop"] == ["</tool_call>"]
    appels = [e for e in evenements if isinstance(e, AppelOutil)]
    texte = "".join(e.texte for e in evenements if isinstance(e, Jeton))
    # Le texte qui suit le premier </tool_call> arrête le tour : ni résultat inventé émis, ni
    # second appel exécuté.
    assert [(a.nom, a.arguments) for a in appels] == [("chercher", {"q": "<requete-factice>"})]
    assert re.fullmatch(r"appel-[0-9a-f]{32}", appels[0].id)
    assert texte == "\n"
    assert len(evenements) == 3 and evenements[-1].raison == "terminee"


def test_balises_mots_d_arret(client_balises: ClientLlama, serveur_factice: Any, factice) -> None:
    """`</tool_call>` s'ajoute aux mots d'arrêt demandés, seulement avec des outils."""
    serveur_factice.scenario.chat = factice.flux_texte("ok")
    list(client_balises.generer(MESSAGES, tools=OUTILS, options={"stop": "<fin>"}))
    list(client_balises.generer(MESSAGES, tools=OUTILS, options={"stop": ["</tool_call>"]}))
    list(client_balises.generer(MESSAGES, options={"stop": ["<fin>"]}))
    arrets = [c.get("stop") for c in serveur_factice.corps("/v1/chat/completions")]
    assert arrets == [["<fin>", "</tool_call>"], ["</tool_call>"], ["<fin>"]]


def test_balises_arret_serveur(client_balises: ClientLlama, serveur_factice: Any, factice) -> None:
    """Arrêt de llama-server sur `</tool_call>` (balise retirée) : l'appel est lu."""
    serveur_factice.scenario.chat = factice.flux_texte(
        "Je cherche.\n<tool_call>\n", '{"name": "heure", "arguments": {}}\n'
    )
    (jeton, appel, fin) = list(client_balises.generer(MESSAGES, tools=OUTILS))
    assert jeton == Jeton(texte="Je cherche.\n") and appel.nom == "heure"
    assert fin.raison == "terminee"


def test_balises_appels_consecutifs(
    client_balises: ClientLlama, serveur_factice: Any, factice
) -> None:
    """Appels séparés par des blancs : tous lus ; le texte qui suit est ignoré."""
    sortie = (
        '<tool_call>{"name": "heure", "arguments": {}}</tool_call>\n \n'
        '<tool_call>{"name": "chercher", "arguments": {"q": "x"}}</tool_call>\n<invente>'
    )
    serveur_factice.scenario.chat = factice.flux_texte(*_decouper(sortie, 2))
    evenements = list(client_balises.generer(MESSAGES, tools=OUTILS))
    assert [(e.nom, e.arguments) for e in evenements[:-1]] == [
        ("heure", {}),
        ("chercher", {"q": "x"}),
    ]


def test_balises_appel_tronque_puis_appel_valide(
    client_balises: ClientLlama, serveur_factice: Any, factice
) -> None:
    sortie = '<tool_call>{"name": "he<tool_call>{"name": "heure", "arguments": {}}</tool_call>'
    serveur_factice.scenario.chat = factice.flux_texte(*_decouper(sortie, 3))
    (tronque, appel, _) = list(client_balises.generer(MESSAGES, tools=OUTILS))
    assert isinstance(tronque, AppelNonConforme) and "avant la suivante" in tronque.motif
    assert tronque.arguments_bruts == '{"name": "he'
    assert isinstance(appel, AppelOutil) and appel.nom == "heure"


@pytest.mark.parametrize("taille", [1, 4])
def test_balises_fermante_dans_une_chaine_json(
    client_balises: ClientLlama, serveur_factice: Any, factice, taille: int
) -> None:
    sortie = (
        '<tool_call>{"name": "chercher", "arguments": {"q": "a</tool_call>b \\" c"}}</tool_call>'
    )
    serveur_factice.scenario.chat = factice.flux_texte(*_decouper(sortie, taille))
    (appel, _) = list(client_balises.generer(MESSAGES, tools=OUTILS))
    assert isinstance(appel, AppelOutil) and appel.arguments == {"q": 'a</tool_call>b " c'}


def test_balises_plusieurs_appels_et_arguments_en_chaine(
    client_balises: ClientLlama, serveur_factice: Any, factice
) -> None:
    sortie = (
        '<tool_call>{"name": "heure", "arguments": {}}</tool_call>\n'
        '<tool_call>{"name": "chercher", "arguments": "{\\"q\\": \\"x\\"}"}</tool_call>'
    )
    serveur_factice.scenario.chat = factice.flux_texte(*_decouper(sortie, 5))
    evenements = list(client_balises.generer(MESSAGES, tools=OUTILS))
    assert [(e.nom, e.arguments) for e in evenements[:-1]] == [
        ("heure", {}),
        ("chercher", {"q": "x"}),
    ]


def test_balises_non_conformes(client_balises: ClientLlama, serveur_factice: Any, factice) -> None:
    sortie = (
        "<tool_call>pas du json</tool_call>"
        '<tool_call>{"arguments": {}}</tool_call>'
        '<tool_call>{"name": "heure", "arguments": [1]}</tool_call>'
    )
    serveur_factice.scenario.chat = factice.flux_texte(sortie)
    evenements = list(client_balises.generer(MESSAGES, tools=OUTILS))[:-1]
    assert all(isinstance(e, AppelNonConforme) for e in evenements)
    assert [e.motif for e in evenements] == [
        "<tool_call> : JSON illisible",
        "nom d'outil absent",
        "arguments : objet JSON attendu",
    ]
    assert evenements[0].arguments_bruts == "pas du json"


def test_balise_non_fermee(client_balises: ClientLlama, serveur_factice: Any, factice) -> None:
    """Arrêt avant `</tool_call>` : JSON complet accepté, JSON coupé non conforme."""
    serveur_factice.scenario.chat = factice.flux_texte(
        '<tool_call>\n{"name": "heure", "arguments": {}}\n'
    )
    (appel, fin) = list(client_balises.generer(MESSAGES, tools=OUTILS))
    assert isinstance(appel, AppelOutil) and appel.nom == "heure" and fin.raison == "terminee"

    serveur_factice.scenario.chat = factice.flux_texte('<tool_call>{"name": "he', raison="length")
    (appel, fin) = list(client_balises.generer(MESSAGES, tools=OUTILS))
    assert isinstance(appel, AppelNonConforme) and "non fermée" in appel.motif
    assert fin.raison == "longueur"


def test_balise_non_fermee_flux_interrompu(
    client_balises: ClientLlama, serveur_factice: Any, factice
) -> None:
    """Flux coupé avant `</tool_call>` : même un JSON complet n'est pas exécutable."""
    serveur_factice.scenario.chat = [
        factice.morceau('<tool_call>{"name": "heure", "arguments": {}}')
    ]
    (appel, fin) = list(client_balises.generer(MESSAGES, tools=OUTILS))
    assert fin.raison == "interrompue"
    assert isinstance(appel, AppelNonConforme) and "interrompu" in appel.motif


def test_balises_texte_sans_appel_et_debut_de_balise_inacheve(
    client_balises: ClientLlama, serveur_factice: Any, factice
) -> None:
    serveur_factice.scenario.chat = factice.flux_texte("a <to", " <tool", "_c")
    evenements = list(client_balises.generer(MESSAGES, tools=OUTILS))
    assert all(isinstance(e, Jeton) for e in evenements[:-1])
    assert "".join(e.texte for e in evenements[:-1]) == "a <to <tool_c"
    assert evenements[0] == Jeton(texte="a ")  # « <to » retenu tant qu'il peut ouvrir une balise


def test_balises_historique_reecrit(client_balises: ClientLlama, serveur_factice: Any) -> None:
    """Le template ignore `tool_calls` : l'appel passé est réécrit en balises dans `content`."""
    appel = AppelOutil(id="appel-1", nom="chercher", arguments={"q": "<requete-factice>"})
    historique = [
        *MESSAGES,
        {"role": "assistant", "content": "", "tool_calls": [appel_canonique(appel)]},
        {"role": "tool", "tool_call_id": "appel-1", "content": "<resultat-factice>"},
    ]
    list(client_balises.generer(historique, tools=OUTILS))
    client_balises.compter_tokens(historique, OUTILS)
    (corps,) = serveur_factice.corps("/v1/chat/completions")
    (gabarit,) = serveur_factice.corps("/apply-template")
    for envoye in (corps["messages"], gabarit["messages"]):
        assert envoye[:2] == MESSAGES and envoye[3] == historique[3]
        assert envoye[2] == {
            "role": "assistant",
            "content": '<tool_call>\n{"name": "chercher", "arguments": '
            '{"q": "<requete-factice>"}}\n</tool_call>',
        }
    assert gabarit["tools"] == OUTILS
    assert "tool_calls" in historique[2]  # l'original n'est pas modifié


def test_messages_balises_garde_le_contenu() -> None:
    message = {
        "role": "assistant",
        "content": "<texte-factice>",
        "tool_calls": [{"function": {"name": "heure", "arguments": "{}"}}],
    }
    (reecrit,) = client_module.messages_balises([message])
    assert reecrit["content"] == (
        '<texte-factice>\n<tool_call>\n{"name": "heure", "arguments": {}}\n</tool_call>'
    )


# --- Dépassement de contexte (correctif F2) ---------------------------------------------------

CORPS_CONTEXTE = (
    '{"error":{"code":400,"message":"the request exceeds the available context size, '
    'try increasing it","type":"exceed_context_size_error"}}'
)


def test_http_depassement_de_contexte(client: ClientLlama, serveur_factice: Any) -> None:
    serveur_factice.scenario.statut_chat = 400
    serveur_factice.scenario.corps_erreur = CORPS_CONTEXTE
    with pytest.raises(ContexteServeurDepasse, match="HTTP 400") as info:
        list(client.generer(MESSAGES))
    assert isinstance(info.value, ContexteDepasse)
    assert isinstance(info.value, ErreurInference)


def test_erreur_en_flux_de_contexte(client: ClientLlama, serveur_factice: Any, factice) -> None:
    erreur = {"error": {"message": "context size exceeded", "type": "exceed_context_size_error"}}
    serveur_factice.scenario.chat = [factice.morceau("a"), erreur]
    with pytest.raises(ContexteServeurDepasse):
        list(client.generer(MESSAGES))


@pytest.mark.parametrize(
    ("texte", "attendu"),
    [
        ("HTTP 400 : the request exceeds the available context size", True),
        ('{"type":"exceed_context_size_error"}', True),
        ("HTTP 400 : requête refusée", False),
        ("HTTP 500 : contexte", False),
        # Revue F2 : seul le type structuré ou le message précis comptent.
        ("context size", False),
        ("prompt tokens exceed context size", False),
        (CORPS_CONTEXTE, True),
        ({"type": "exceed_context_size_error", "message": "x"}, True),
        ({"type": "invalid_request_error", "message": "context size"}, False),
        ({"message": "the request exceeds the available context size"}, True),
        (None, False),
    ],
)
def test_est_depassement_contexte(texte: Any, attendu: bool) -> None:
    assert est_depassement_contexte(texte) is attendu


def test_http_400_sans_type_de_contexte_reste_erreur_inference(
    client: ClientLlama, serveur_factice: Any
) -> None:
    serveur_factice.scenario.statut_chat = 400
    serveur_factice.scenario.corps_erreur = (
        '{"error":{"code":400,"message":"context size","type":"invalid_request_error"}}'
    )
    with pytest.raises(ErreurInference) as info:
        list(client.generer(MESSAGES))
    assert not isinstance(info.value, ContexteServeurDepasse)


def test_grammaire_transmise_au_serveur(client: ClientLlama) -> None:
    """Vérification de Q (story 16.8) : `grammar` part telle quelle à llama-server."""
    corps = client.corps_generation(
        [{"role": "user", "content": "<question-factice>"}],
        options={"max_tokens": 4, "grammar": 'root ::= "oui" | "non"'},
    )
    assert corps["grammar"] == 'root ::= "oui" | "non"' and corps["max_tokens"] == 4
