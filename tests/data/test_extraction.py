"""Extracteur pur des réponses brutes (story 9.6) : contenu tel quel, refus des cas ambigus.

Les réponses sont fabriquées ici avec des jetons aléatoires (D1.1) : aucun texte rédigé.
"""

from __future__ import annotations

import json
import secrets
from typing import Any

import pytest

pytest.importorskip("mistralai")

from slmsp.core.erreurs import ProvenanceInvalide, ReponseTronquee  # noqa: E402
from slmsp.data.extraction import VERSION_EXTRACTEUR, extraire_contenu, extraire_message  # noqa: E402


def brut(message: dict[str, Any], fin: str = "stop") -> bytes:
    corps = {"choices": [{"index": 0, "finish_reason": fin, "message": message}]}
    return json.dumps(corps).encode()


def jeton() -> str:
    return f"<extrait-factice-{secrets.token_hex(4)}>"


def test_version_entiere_positive() -> None:
    assert isinstance(VERSION_EXTRACTEUR, int) and VERSION_EXTRACTEUR >= 1


def test_contenu_inchange_espaces_compris() -> None:
    texte = f"  {jeton()}\n\n{jeton()} \n"
    assert extraire_contenu(brut({"role": "assistant", "content": texte})) == texte


def test_pure_meme_entree_meme_sortie() -> None:
    entree = brut({"role": "assistant", "content": jeton()})
    assert extraire_contenu(entree) == extraire_contenu(bytes(entree))
    assert extraire_contenu(entree) == extraire_contenu(entree.decode())


def test_message_garde_les_appels_d_outils() -> None:
    appel = {
        "id": "a1",
        "index": 0,
        "function": {"name": "outil-factice", "arguments": "{}"},
    }
    message = extraire_message(brut({"role": "assistant", "content": "", "tool_calls": [appel]}))
    assert message["tool_calls"] == [
        {"id": "a1", "type": "function", "function": {"name": "outil-factice", "arguments": "{}"}}
    ]
    with pytest.raises(ProvenanceInvalide, match="contenu texte seul"):
        extraire_contenu(brut({"role": "assistant", "content": "", "tool_calls": [appel]}))


@pytest.mark.parametrize(
    "mauvais",
    [
        None,
        b"pas du json",
        b'{"choices": []}',
        brut({"role": "assistant", "content": ""}),
        brut({"role": "user", "content": jeton()}),
        brut({"role": "assistant", "content": jeton()}, fin="length"),
    ],
)
def test_refus(mauvais: Any) -> None:
    with pytest.raises(ProvenanceInvalide):
        extraire_contenu(mauvais)


def test_tronquee_sans_texte_est_une_reponse_tronquee() -> None:
    mauvais = brut(
        {"role": "assistant", "content": [{"type": "thinking", "thinking": []}]}, "length"
    )
    with pytest.raises(ReponseTronquee):
        extraire_message(mauvais)
