"""Ports du Harnais (critère 8, story 1.3)."""

from __future__ import annotations

import dataclasses
from collections.abc import Iterator
from typing import Any, get_args

import numpy as np
import pytest

from slmsp.core import ports
from slmsp.core.evenements import Fin, Jeton
from slmsp.core.ports import (
    EmbedderPort,
    JournalRequetes,
    LlmPort,
    Mode,
    ModePort,
    NetGate,
    Passage,
    ToolPort,
    VectorStore,
)

PASSAGE = Passage(
    chunk_id="c1",
    doc_id="d1",
    source="service-public",
    titre="<titre-factice>",
    url="https://www.service-public.gouv.fr/x",
    texte="<texte-factice>",
    date_snapshot="2026-10-01",
    score=0.5,
)


class LlmFactice:
    def generer(self, messages, *, tools=None, options=None) -> Iterator[Jeton | Fin]:
        yield Jeton(texte="<jeton-factice>")
        yield Fin(raison="terminee")

    def compter_tokens(self, messages, tools=None) -> int:
        return len(messages)


class EmbedderFactice:
    dimension = 4

    def vectoriser(self, textes):
        return np.zeros((len(textes), self.dimension), dtype=np.float32)


class StoreFactice:
    def rechercher(self, vecteur, k):
        return [PASSAGE][:k]


class OutilsFactices:
    def lister_outils(self) -> list[dict[str, Any]]:
        return []

    def appeler(self, nom, arguments) -> dict[str, Any]:
        return {}


class PasserelleFactice:
    def client(self, profil):
        return None

    def verifier(self, profil, methode, url, *, outil=None, termes=None) -> None:
        return None


class ModeFactice:
    def mode_courant(self) -> Mode:
        return "hors-ligne-force"


class JournalFactice:
    def __init__(self) -> None:
        self.entrees: list[Any] = []

    def inscrire(self, entree) -> None:
        self.entrees.append(entree)

    def lister(self, limite=None) -> list[Any]:
        return self.entrees[:limite]


@pytest.mark.parametrize(
    ("protocole", "doublure"),
    [
        (LlmPort, LlmFactice()),
        (EmbedderPort, EmbedderFactice()),
        (VectorStore, StoreFactice()),
        (ToolPort, OutilsFactices()),
        (NetGate, PasserelleFactice()),
        (ModePort, ModeFactice()),
        (JournalRequetes, JournalFactice()),
    ],
)
def test_doublure_satisfait_le_protocole(protocole: type, doublure: object) -> None:
    assert isinstance(doublure, protocole)
    assert not isinstance(object(), protocole)


def test_ports_attendus() -> None:
    for nom in (
        "LlmPort",
        "EmbedderPort",
        "VectorStore",
        "ToolPort",
        "NetGate",
        "ModePort",
        "JournalRequetes",
    ):
        assert hasattr(ports, nom), nom
    assert set(get_args(Mode)) == {"connecte", "hors-ligne-detecte", "hors-ligne-force"}


def test_doublure_incomplete_refusee() -> None:
    class SansCompteur:
        def generer(self, messages, *, tools=None, options=None):
            return iter(())

    assert not isinstance(SansCompteur(), LlmPort)


def test_passage_fige() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        PASSAGE.score = 1.0  # type: ignore[misc]
    assert [champ.name for champ in dataclasses.fields(Passage)] == [
        "chunk_id",
        "doc_id",
        "source",
        "titre",
        "url",
        "texte",
        "date_snapshot",
        "score",
    ]


def test_flux_de_la_doublure() -> None:
    evenements = list(LlmFactice().generer([{"role": "user", "content": "<q>"}], tools=[]))
    assert evenements[-1] == Fin(raison="terminee")
    assert EmbedderFactice().vectoriser(["a", "b"]).shape == (2, 4)
