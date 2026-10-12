"""Format canonique des conversations (critère 9, story 1.3, AD-7)."""

from __future__ import annotations

import copy
from typing import Any

import pytest

from slmsp.core.erreurs import CodeSortie, SlmspError
from slmsp.core.messages import (
    ConversationInvalide,
    MessageAssistant,
    MessageOutil,
    MessageSysteme,
    MessageUtilisateur,
    valider_conversation,
    vers_dicts,
)


def _appel(id_: str = "appel-1", nom: str = "search_datasets", arguments: str = '{"q":"x"}'):
    return {"id": id_, "type": "function", "function": {"name": nom, "arguments": arguments}}


CONVERSATION: list[dict[str, Any]] = [
    {"role": "system", "content": "<consigne-factice>"},
    {"role": "user", "content": "<question-factice>"},
    {"role": "assistant", "content": None, "tool_calls": [_appel()]},
    {"role": "tool", "tool_call_id": "appel-1", "content": '{"resultats":[]}'},
    {"role": "assistant", "content": "<reponse-factice>"},
]


def test_conversation_valide() -> None:
    messages = valider_conversation(CONVERSATION)
    assert [type(m) for m in messages] == [
        MessageSysteme,
        MessageUtilisateur,
        MessageAssistant,
        MessageOutil,
        MessageAssistant,
    ]
    assert messages[2].tool_calls[0].function.name == "search_datasets"


def test_aller_retour_sans_none() -> None:
    dicts = vers_dicts(valider_conversation(CONVERSATION))
    attendu = copy.deepcopy(CONVERSATION)
    del attendu[2]["content"]
    assert dicts == attendu
    assert valider_conversation(dicts) == valider_conversation(CONVERSATION)


def test_messages_types_acceptes() -> None:
    messages = valider_conversation(CONVERSATION)
    assert valider_conversation(messages) == messages


def test_assistant_contenu_et_appels() -> None:
    messages = valider_conversation(
        [{"role": "assistant", "content": "je cherche", "tool_calls": [_appel()]}]
    )
    assert messages[0].content == "je cherche"


def test_outil_avec_nom() -> None:
    conversation = [*CONVERSATION[:3], {**CONVERSATION[3], "name": "search_datasets"}]
    assert valider_conversation(conversation)[3].name == "search_datasets"


def _avec(indice: int, message: dict[str, Any]) -> list[dict[str, Any]]:
    conversation = copy.deepcopy(CONVERSATION)
    conversation[indice] = message
    return conversation


@pytest.mark.parametrize(
    ("conversation", "indice"),
    [
        (_avec(0, {"role": "developer", "content": "x"}), 0),
        (_avec(1, {"role": "user"}), 1),
        (_avec(1, {"role": "user", "content": "x", "extra": 1}), 1),
        (_avec(1, {"content": "x"}), 1),
        (_avec(2, {"role": "assistant", "tool_calls": [_appel(arguments="pas du json")]}), 2),
        (_avec(2, {"role": "assistant", "tool_calls": [_appel(arguments="[1, 2]")]}), 2),
        (_avec(2, {"role": "assistant", "tool_calls": [_appel(arguments='"x"')]}), 2),
        (
            _avec(2, {"role": "assistant", "tool_calls": [{**_appel(), "type": "code"}]}),
            2,
        ),
        (_avec(2, {"role": "assistant", "tool_calls": [{"id": "a", "type": "function"}]}), 2),
        (_avec(2, {"role": "assistant", "content": None}), 2),
        (_avec(4, {"role": "assistant", "content": ""}), 4),
        (_avec(2, {"role": "assistant", "tool_calls": [_appel(arguments='{"x": NaN}')]}), 2),
        (
            _avec(2, {"role": "assistant", "tool_calls": [_appel(arguments='{"x": -Infinity}')]}),
            2,
        ),
        ([*CONVERSATION[:4], CONVERSATION[3]], 4),
        (_avec(2, {"role": "assistant"}), 2),
        (_avec(2, {"role": "assistant", "tool_calls": []}), 2),
        (_avec(3, {"role": "tool", "tool_call_id": "inconnu", "content": "{}"}), 3),
        (_avec(3, {"role": "tool", "content": "{}"}), 3),
        (
            [
                CONVERSATION[0],
                {"role": "tool", "tool_call_id": "appel-1", "content": "{}"},
                *CONVERSATION[2:],
            ],
            1,
        ),
        (
            [
                *CONVERSATION,
                {"role": "assistant", "tool_calls": [_appel()]},
            ],
            5,
        ),
        (
            [{"role": "assistant", "tool_calls": [_appel("x"), _appel("x")]}],
            0,
        ),
        (["pas un message"], 0),
    ],
)
def test_conversation_invalide(conversation: list[Any], indice: int) -> None:
    with pytest.raises(ConversationInvalide) as erreur:
        valider_conversation(conversation)
    assert f"message {indice}" in str(erreur.value)
    assert isinstance(erreur.value, SlmspError)
    assert erreur.value.code_sortie == CodeSortie.ERREUR


def test_conversation_vide() -> None:
    assert valider_conversation([]) == []
