"""API unique d'enregistrement des cassettes MCP (AD-10) : `enregistrer(session, magasin)`.

Deux magasins séparés :

- `eval` : `eval/cassettes/<ITEM>/<session_id>.json`, refusé si l'item figure dans un
  manifeste gelé `eval/jeu/*/MANIFEST.json` (`ItemGele`) ;
- `data` : `data/cassettes/<session_id>.json`. Aucune fonction de ce magasin ne lit `eval/`
  (pas de fuite du Jeu d'évaluation vers l'entraînement).

Un fichier existant n'est jamais écrasé (`ArtefactExistant`, via `ecrire_cassette`).
`session_de_panne` construit sans réseau une session dont chaque appel est une panne simulée.
"""

from __future__ import annotations

import json
import re
import secrets
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Literal

from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ManifesteInvalide, SlmspError
from slmsp.core.schemas.cassette import Cassette, Interaction, Simulation, TypeSimulation
from slmsp.mcp.cassettes import ecrire_cassette
from slmsp.mcp.outils import charger_config, valider_appel

URL_SERVEUR: Final = "https://mcp.data.gouv.fr/mcp"
"""Point d'accès Streamable HTTP du serveur MCP data.gouv (seul transport admis)."""

Magasin = Literal["eval", "data"]
MAGASINS: Final[tuple[str, ...]] = ("eval", "data")

PREMIER_ID_APPEL: Final = 3
"""Numérotation des `id` JSON-RPC : 1 `initialize`, 2 `tools/list`, puis 3, 4… par appel."""

_IDENTIFIANT = re.compile(r"[A-Za-z0-9_.-]*[A-Za-z0-9_-]")
"""Identifiant de fichier : jamais de point final (ignoré par Windows)."""


class ItemGele(SlmspError):
    """L'item cité figure dans un manifeste gelé du Jeu d'évaluation : aucune écriture."""


@dataclass(frozen=True)
class SessionMcp:
    """Une session MCP prête à enregistrer : la cassette, son identifiant et l'item visé."""

    cassette: Cassette
    session_id: str
    item: str | None = None


def nouvel_identifiant_session() -> str:
    """Identifiant de session horodaté et unique (`AAAAMMJJTHHMMSSZ-<8 hex>`)."""
    return f"{datetime.now(UTC):%Y%m%dT%H%M%SZ}-{secrets.token_hex(4)}"


def _verifier_identifiant(valeur: Any, nature: str) -> str:
    if (
        not isinstance(valeur, str)
        or not _IDENTIFIANT.fullmatch(valeur)
        or ".." in valeur
        or valeur.strip(".") == ""
    ):
        raise ValueError(
            f"{nature} invalide : {valeur!r} (lettres, chiffres, « _ », « - » ou « . », "
            "sans « .. », point final ni séparateur de chemin)"
        )
    return valeur


def _chaines_et_cles(valeur: Any) -> Iterator[str]:
    if isinstance(valeur, str):
        yield valeur
    elif isinstance(valeur, Mapping):
        for cle, sous_valeur in valeur.items():
            if isinstance(cle, str):
                yield cle
            yield from _chaines_et_cles(sous_valeur)
    elif isinstance(valeur, list):
        for element in valeur:
            yield from _chaines_et_cles(element)


def verifier_item_libre(item: str, *, racine: str | Path | None = None) -> None:
    """Vérifie qu'aucun manifeste gelé `eval/jeu/*/MANIFEST.json` ne cite `item`.

    Un item est cité si une chaîne ou une clé du JSON égale son identifiant, si une
    chaîne contient `cassettes/<ITEM>/` ou se termine par `cassettes/<ITEM>`, sans tenir
    compte de la casse (les chemins Windows l'ignorent). Lève `ValueError` (identifiant fautif),
    `ManifesteInvalide` (manifeste illisible ou non JSON) ou `ItemGele`.
    """
    item = _verifier_identifiant(item, "identifiant d'item")
    base = Path(racine_projet() if racine is None else racine)
    cle_item = item.casefold()
    motif = f"cassettes/{cle_item}"
    for manifeste in sorted((base / "eval" / "jeu").glob("*/MANIFEST.json")):
        try:
            donnees = json.loads(manifeste.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ManifesteInvalide(
                f"{manifeste} : manifeste illisible ({type(exc).__name__}) : "
                f"impossible de vérifier que l'item {item} n'est pas gelé"
            ) from None
        for chaine in _chaines_et_cles(donnees):
            texte = chaine.replace("\\", "/").casefold()
            if texte == cle_item or f"{motif}/" in texte or texte.endswith(motif):
                raise ItemGele(
                    f"l'item {item} figure dans le manifeste gelé {manifeste} : "
                    "aucune cassette n'est écrite"
                )


def chemin_cassette(
    magasin: str,
    session_id: str,
    *,
    item: str | None = None,
    racine: str | Path | None = None,
) -> Path:
    """Chemin de la cassette d'une session dans `magasin` (sans rien lire ni écrire).

    Lève `ValueError` pour un magasin inconnu, un identifiant fautif, ou un item absent
    pour le magasin `eval`.
    """
    if magasin not in MAGASINS:
        raise ValueError(f"magasin inconnu : {magasin!r} (attendu : {', '.join(MAGASINS)})")
    session_id = _verifier_identifiant(session_id, "identifiant de session")
    base = Path(racine_projet() if racine is None else racine)
    if magasin == "data":
        return base / "data" / "cassettes" / f"{session_id}.json"
    if item is None:
        raise ValueError("le magasin eval exige un identifiant d'item")
    item = _verifier_identifiant(item, "identifiant d'item")
    return base / "eval" / "cassettes" / item / f"{session_id}.json"


def enregistrer(session: SessionMcp, magasin: str, *, racine: str | Path | None = None) -> Path:
    """Écrit la cassette de `session` dans `magasin` (`eval` ou `data`) et renvoie son chemin.

    `eval` vérifie d'abord que l'item n'est pas gelé (`ItemGele`, `ManifesteInvalide`) ;
    `data` ne lit jamais `eval/`. Lève `ValueError` (magasin ou identifiant fautif) et
    `ArtefactExistant` si le fichier existe déjà : rien n'est alors écrit.
    """
    if not isinstance(session, SessionMcp):
        raise TypeError(f"SessionMcp attendue (reçu {type(session).__name__})")
    chemin = chemin_cassette(magasin, session.session_id, item=session.item, racine=racine)
    if magasin == "eval":
        verifier_item_libre(session.item or "", racine=racine)
    return ecrire_cassette(session.cassette, chemin)


def requete_appel(id_: int, nom: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
    """Requête JSON-RPC `tools/call`, au format des cassettes du calibrage."""
    return {
        "jsonrpc": "2.0",
        "id": id_,
        "method": "tools/call",
        "params": {"name": nom, "arguments": dict(arguments)},
    }


def session_de_panne(
    appels: Sequence[tuple[str, Mapping[str, Any]]],
    type: TypeSimulation,
    *,
    statut: int | None = None,
    item: str | None = None,
    session_id: str | None = None,
    serveur: str = URL_SERVEUR,
    chemin_outils: str | Path | None = None,
) -> SessionMcp:
    """Session sans réseau dont chaque appel `(nom, arguments)` est une panne simulée.

    Tous les appels sont validés d'abord (`AppelNonConforme`) ; la cassette a un
    `initialize` nul et une interaction par appel, avec `simulation` et `response` nulle.
    Lève `ValueError` (identifiant fautif) ou `pydantic.ValidationError` (simulation
    incohérente, par exemple un `statut` hors `erreur_http`).
    """
    for nom, arguments in appels:
        valider_appel(nom, arguments, chemin=chemin_outils)
    session_id = nouvel_identifiant_session() if session_id is None else session_id
    _verifier_identifiant(session_id, "identifiant de session")
    if item is not None:
        _verifier_identifiant(item, "identifiant d'item")
    simulation = Simulation(type=type, statut=statut)
    cassette = Cassette(
        schema_version=1,
        server=serveur,
        recorded_at=datetime.now(UTC).replace(microsecond=0),
        initialize=None,
        tools_list_sha256=charger_config(chemin_outils).tools_list_sha256,
        interactions=[
            Interaction(
                request=requete_appel(PREMIER_ID_APPEL + rang, nom, arguments),
                response=None,
                simulation=simulation,
            )
            for rang, (nom, arguments) in enumerate(appels)
        ],
    )
    return SessionMcp(cassette=cassette, session_id=session_id, item=item)
