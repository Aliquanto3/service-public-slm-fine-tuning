"""`ClientLlama` (LlmPort) contre le serveur factice : flux SSE, outils, usage, erreurs."""

from __future__ import annotations

import json
import re
from types import SimpleNamespace
from typing import Any

import jsonschema
import pytest

from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton
from slmsp.core.ports import LlmPort
from slmsp.inference import client as client_module
from slmsp.inference.client import ClientLlama, appel_canonique, schema_json_generique
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


def test_compter_tokens_json_generique_sans_outils(
    client_json: ClientLlama, serveur_factice: Any
) -> None:
    client_json.compter_tokens(MESSAGES, OUTILS)
    (gabarit,) = serveur_factice.corps("/apply-template")
    assert "tools" not in gabarit


def test_protocole_inconnu() -> None:
    with pytest.raises(ValueError, match="protocole"):
        ClientLlama(8080, protocole_outils="xml")
