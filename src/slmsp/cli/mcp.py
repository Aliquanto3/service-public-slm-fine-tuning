"""Sous-commande `slmsp mcp` : enregistrement de cassettes et sonde du serveur MCP (AD-10).

- `slmsp mcp record --item <ID> --appels <fichier.json> [--simulation <type>
  [--statut <code>]] [--session <id>]` : profil `outillage`. Tous les appels sont validés
  et l'item vérifié libre (aucun manifeste gelé ne le cite) avant toute connexion. Avec
  `--simulation`, la cassette de panne est écrite sans aucune requête. La cassette va dans
  `eval/cassettes/<ITEM>/<session>.json` et n'écrase jamais un fichier existant.
- `slmsp mcp sante` : `GET /health` (délai `delais.sonde`) ; code 0 si joignable, 1 sinon.

Le fichier d'appels est une liste JSON d'objets `{"nom": <outil>, "arguments": {...}}`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, get_args

from slmsp.core.artefacts import ArtefactExistant
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import CodeSortie
from slmsp.core.schemas.cassette import TypeSimulation
from slmsp.mcp import enregistrement
from slmsp.mcp.direct import McpEnDirect, sonder_sante
from slmsp.mcp.outils import valider_appel

CLES_APPEL = frozenset({"nom", "arguments"})


class _FichierAppelsInvalide(Exception):
    """Fichier d'appels illisible ou mal formé (code 2, message sans trace)."""


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `mcp` et ses actions `record` et `sante` au parseur de `slmsp`."""
    aide = "client MCP en direct et enregistrement de cassettes"
    parseur = sous_parseurs.add_parser("mcp", help=aide, description=aide)
    actions = parseur.add_subparsers(dest="action_mcp", metavar="<action>", title="actions")

    record = actions.add_parser(
        "record",
        help="enregistrer une cassette d'item du Jeu d'évaluation (profil outillage)",
        description="Enregistre une session MCP dans eval/cassettes/<ITEM>/<session>.json.",
    )
    record.add_argument("--item", required=True, help="identifiant de l'item (ex. RD-007)")
    record.add_argument(
        "--appels",
        required=True,
        type=Path,
        help='fichier JSON : liste de {"nom": <outil>, "arguments": {...}}',
    )
    record.add_argument(
        "--simulation",
        choices=get_args(TypeSimulation),
        help="écrire une cassette de panne simulée, sans aucune requête réseau",
    )
    record.add_argument("--statut", type=int, help="statut HTTP de la simulation erreur_http")
    record.add_argument("--session", dest="session_id", help="identifiant de session imposé")
    record.set_defaults(func=_record)

    sante = actions.add_parser(
        "sante",
        help="sonder GET /health du serveur MCP data.gouv",
        description="Sonde de santé du serveur MCP (délai delais.sonde de config/reseau.toml).",
    )
    sante.set_defaults(func=_sante)

    def sans_action(_args: argparse.Namespace) -> int:
        parseur.print_help(sys.stderr)
        return int(CodeSortie.USAGE)

    parseur.set_defaults(func=sans_action)


def _erreur_usage(message: str) -> int:
    print(f"slmsp : {message}", file=sys.stderr)
    return int(CodeSortie.USAGE)


def _lire_appels(chemin: Path) -> list[tuple[str, dict[str, Any]]]:
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except OSError as exc:
        raise _FichierAppelsInvalide(
            f"{chemin} : fichier d'appels illisible ({type(exc).__name__})"
        ) from None
    except UnicodeDecodeError:
        raise _FichierAppelsInvalide(f"{chemin} : fichier d'appels non UTF-8") from None
    except json.JSONDecodeError as exc:
        raise _FichierAppelsInvalide(
            f"{chemin} : JSON invalide (ligne {exc.lineno}, colonne {exc.colno})"
        ) from None
    if not isinstance(donnees, list) or not donnees:
        raise _FichierAppelsInvalide(f"{chemin} : une liste d'appels non vide est attendue")
    appels = []
    for rang, appel in enumerate(donnees, start=1):
        if not isinstance(appel, dict):
            raise _FichierAppelsInvalide(f"{chemin} : appel n° {rang} : objet JSON attendu")
        inconnues = sorted(set(appel) - CLES_APPEL)
        if inconnues:
            raise _FichierAppelsInvalide(
                f"{chemin} : appel n° {rang} : clé inconnue {', '.join(inconnues)} "
                f"(clés permises : {', '.join(sorted(CLES_APPEL))})"
            )
        nom = appel.get("nom")
        arguments = appel.get("arguments", {})
        if not isinstance(nom, str):
            raise _FichierAppelsInvalide(f"{chemin} : appel n° {rang} : « nom » textuel attendu")
        if not isinstance(arguments, dict):
            raise _FichierAppelsInvalide(
                f"{chemin} : appel n° {rang} : « arguments » doit être un objet JSON"
            )
        appels.append((nom, arguments))
    return appels


def _record(args: argparse.Namespace) -> int:
    if args.statut is not None and args.simulation != "erreur_http":
        return _erreur_usage("--statut n'est permis qu'avec --simulation erreur_http")
    if args.statut is not None and not 100 <= args.statut <= 599:
        return _erreur_usage(f"--statut {args.statut} : statut HTTP de 100 à 599 attendu")
    try:
        appels = _lire_appels(args.appels)
    except _FichierAppelsInvalide as exc:
        return _erreur_usage(str(exc))

    # Tout est vérifié avant la moindre connexion : appels, identifiants, item, fichier.
    for nom, arguments in appels:
        valider_appel(nom, arguments)
    racine = racine_projet()
    session_id = (
        args.session_id
        if args.session_id is not None
        else enregistrement.nouvel_identifiant_session()
    )
    try:
        chemin = enregistrement.chemin_cassette("eval", session_id, item=args.item, racine=racine)
    except ValueError as exc:
        return _erreur_usage(str(exc))
    enregistrement.verifier_item_libre(args.item, racine=racine)
    if chemin.exists():
        raise ArtefactExistant(f"{chemin} existe déjà : une cassette n'est jamais réécrite")

    if args.simulation is not None:
        session = enregistrement.session_de_panne(
            appels, args.simulation, statut=args.statut, item=args.item, session_id=session_id
        )
    else:
        with McpEnDirect("outillage") as client:
            for nom, arguments in appels:
                reponse = client.appeler(nom, arguments)
                if "error" in reponse:
                    erreur = reponse["error"]
                    print(
                        f"slmsp : {nom} : erreur JSON-RPC {erreur.get('code')} "
                        f"({erreur.get('message')}), enregistrée",
                        file=sys.stderr,
                    )
            session = client.session(item=args.item, session_id=session_id)

    ecrit = enregistrement.enregistrer(session, "eval", racine=racine)
    nombre = len(session.cassette.interactions)
    print(f"cassette écrite : {ecrit} ({nombre} interaction{'s' if nombre > 1 else ''})")
    return int(CodeSortie.SUCCES)


def _sante(_args: argparse.Namespace) -> int:
    resultat = sonder_sante()
    if resultat.joignable:
        print(f"{resultat.url} : joignable ({resultat.detail})")
        return int(CodeSortie.SUCCES)
    print(f"slmsp : {resultat.url} : injoignable ({resultat.detail})", file=sys.stderr)
    return int(CodeSortie.ERREUR)
