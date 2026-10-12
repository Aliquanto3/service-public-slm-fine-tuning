"""Format canonique des conversations : messages OpenAI validés (AD-7).

Rôles admis : `system`, `user`, `assistant`, `tool`. Un message `assistant` porte un
`content`, des `tool_calls` structurés (`id`, `type = function`, `function.name`,
`function.arguments` en JSON objet), ou les deux. Un message `tool` répond à un appel
antérieur de la conversation par son `tool_call_id`.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    field_validator,
    model_validator,
)

from slmsp.core.erreurs import SlmspError


class ConversationInvalide(SlmspError):
    """Conversation non conforme au format canonique (le message cite l'index fautif)."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _refuser_constante(constante: str) -> Any:
    raise ValueError(f"arguments contient {constante}, hors JSON strict")


class Fonction(_Strict):
    """Fonction appelée : nom et arguments sérialisés en JSON (objet)."""

    name: str = Field(min_length=1)
    arguments: str

    @field_validator("arguments")
    @classmethod
    def _arguments_objet_json(cls, valeur: str) -> str:
        try:
            decode = json.loads(valeur, parse_constant=_refuser_constante)
        except json.JSONDecodeError:
            raise ValueError("arguments n'est pas du JSON valide") from None
        if not isinstance(decode, dict):
            raise ValueError("arguments doit être un objet JSON")
        return valeur


class AppelFonction(_Strict):
    """Entrée de `tool_calls`."""

    id: str = Field(min_length=1)
    type: Literal["function"]
    function: Fonction


class MessageSysteme(_Strict):
    role: Literal["system"]
    content: str


class MessageUtilisateur(_Strict):
    role: Literal["user"]
    content: str


class MessageAssistant(_Strict):
    role: Literal["assistant"]
    content: str | None = None
    tool_calls: Annotated[list[AppelFonction], Field(min_length=1)] | None = None

    @model_validator(mode="after")
    def _contenu_ou_appels(self) -> MessageAssistant:
        if not self.content and not self.tool_calls:
            raise ValueError("message assistant sans content ni tool_calls")
        return self


class MessageOutil(_Strict):
    role: Literal["tool"]
    tool_call_id: str = Field(min_length=1)
    content: str
    name: str | None = None


Message = Annotated[
    MessageSysteme | MessageUtilisateur | MessageAssistant | MessageOutil,
    Field(discriminator="role"),
]

_ADAPTATEUR: TypeAdapter[Message] = TypeAdapter(Message)


def _resume(exc: ValidationError) -> str:
    parties = []
    for erreur in exc.errors(include_url=False, include_input=False, include_context=False):
        lieu = ".".join(str(partie) for partie in erreur["loc"])
        parties.append(f"{lieu} : {erreur['msg']}" if lieu else erreur["msg"])
    return " ; ".join(parties)


def valider_conversation(messages: Iterable[Any]) -> list[Message]:
    """Valide une conversation (dicts ou messages typés) et renvoie les messages typés.

    Lève `ConversationInvalide` (citant l'index du message) pour un rôle inconnu, un
    `tool_calls` mal formé, un `id` d'appel dupliqué, ou un `tool_call_id` qui ne désigne
    aucun appel antérieur.
    """
    valides: list[Message] = []
    appels: set[str] = set()
    repondus: set[str] = set()
    for indice, brut in enumerate(messages):
        try:
            message = _ADAPTATEUR.validate_python(brut)
        except ValidationError as exc:
            raise ConversationInvalide(f"message {indice} invalide : {_resume(exc)}") from None
        if isinstance(message, MessageAssistant):
            for appel in message.tool_calls or ():
                if appel.id in appels:
                    raise ConversationInvalide(
                        f"message {indice} invalide : id d'appel dupliqué {appel.id!r}"
                    )
                appels.add(appel.id)
        elif isinstance(message, MessageOutil):
            if message.tool_call_id not in appels:
                raise ConversationInvalide(
                    f"message {indice} invalide : tool_call_id {message.tool_call_id!r} "
                    "ne désigne aucun appel antérieur"
                )
            if message.tool_call_id in repondus:
                raise ConversationInvalide(
                    f"message {indice} invalide : l'appel {message.tool_call_id!r} "
                    "a déjà reçu une réponse"
                )
            repondus.add(message.tool_call_id)
        valides.append(message)
    return valides


def vers_dicts(messages: Sequence[Message]) -> list[dict[str, Any]]:
    """Dicts au format OpenAI, sans les champs `None`."""
    return [message.model_dump(mode="json", exclude_none=True) for message in messages]
