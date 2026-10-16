"""Sous-commande `slmsp ask` : interroger l'Assistant complet (FR-1, FR-38, AD-14).

    slmsp ask --modele base:<slug> [--tache Q] [--hors-ligne] [--conversation f.json]
              [--json] [--journal] [--variante cpu|cuda] "question"

La réponse s'affiche au fil de l'eau, suivie des sources numérotées (titre, URL, date de
l'Index), de l'avertissement de la Tâche et, pour RD, des résultats d'outils rendus par
`contenu_resultat` (jamais depuis le texte généré). `--conversation` relit puis complète
un fichier JSON de messages `user`/`assistant` (seul l'échange final y est ajouté, sans
tours d'outil). `--json` émet les évènements bruts, un par ligne. `--journal` affiche les
Requêtes sortantes de cette exécution (heure, hôte, termes, statut). Les messages
d'avancement et d'erreur vont sur stderr.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from slmsp.core.erreurs import CodeSortie
from slmsp.core.evenements import (
    AppelNonConforme,
    Avertissement,
    Erreur,
    Evenement,
    Fin,
    Jeton,
    Progression,
    Repli,
    ResultatOutil,
    Sources,
    vers_dict,
)

CODES_TACHE = ("Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR", "TR")


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `ask` au parseur de `slmsp`."""
    parseur = sous_parseurs.add_parser(
        "ask",
        help="interroger l'Assistant",
        description="Interroge l'Assistant : réponse en flux, sources et avertissement.",
    )
    parseur.add_argument("question", help="question ou texte à traiter")
    parseur.add_argument("--modele", required=True, help="modèle : base:<slug>")
    parseur.add_argument("--tache", default="Q", help=f"Tâche ({', '.join(CODES_TACHE)}), Q défaut")
    parseur.add_argument("--hors-ligne", action="store_true", help="Mode hors ligne forcé")
    parseur.add_argument("--conversation", type=Path, help="fichier JSON de la conversation")
    parseur.add_argument("--json", action="store_true", help="émettre les évènements bruts")
    parseur.add_argument("--journal", action="store_true", help="afficher les Requêtes sortantes")
    parseur.add_argument("--variante", choices=("cpu", "cuda"), default="cpu")
    parseur.set_defaults(func=_ask)


def _erreur(message: str, code: CodeSortie = CodeSortie.USAGE) -> int:
    print(f"slmsp : {message}", file=sys.stderr)
    return int(code)


def lire_conversation(chemin: Path | None) -> list[dict[str, Any]]:
    """Messages du fichier (liste vide s'il n'existe pas) ; `ValueError` s'il est mal formé."""
    if chemin is None or not chemin.exists():
        return []
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    if not isinstance(donnees, list) or not all(isinstance(m, dict) for m in donnees):
        raise ValueError(f"{chemin} : liste de messages attendue")
    return donnees


def ecrire_conversation(chemin: Path, messages: list[dict[str, Any]]) -> None:
    """Écrit la conversation par remplacement atomique."""
    temporaire = chemin.with_name(chemin.name + ".tmp")
    temporaire.write_text(
        json.dumps(messages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporaire, chemin)


def ligne_source(source: Any) -> str:
    numero = f"[{source.numero}] " if source.numero is not None else "- "
    date = f" ({source.date})" if source.date else ""
    return f"{numero}{source.titre} : {source.url}{date}"


def ligne_journal(entree: Any) -> str:
    heure = entree.horodatage.astimezone().strftime("%H:%M:%S")
    termes = f" termes={entree.termes}" if entree.termes else ""
    return f"{heure} {entree.hote} {entree.methode}{termes} {entree.statut}"


def _afficher(evenement: Evenement, resultats: list[ResultatOutil]) -> None:
    if isinstance(evenement, Jeton):
        print(evenement.texte, end="", flush=True)
    elif isinstance(evenement, ResultatOutil):
        resultats.append(evenement)
    elif isinstance(evenement, Progression):
        total = f" sur {evenement.total}" if evenement.total else ""
        print(f"\n{evenement.etape} {evenement.fait}{total}", file=sys.stderr)
    elif isinstance(evenement, Repli):
        print(f"\n{evenement.motif}", file=sys.stderr)
    elif isinstance(evenement, AppelNonConforme):
        print(
            f"\nAppel d'outil non conforme ({evenement.nom}) : {evenement.motif}", file=sys.stderr
        )


def _ask(args: argparse.Namespace) -> int:
    from slmsp.cli._assemblage import ModeleInvalide, assembler
    from slmsp.harness.taches import charger_taches
    from slmsp.harness.taches.recherche import contenu_resultat

    if not args.question.strip():
        return _erreur("question vide")
    try:
        fiche = charger_taches().tache(args.tache.upper())
        historique = lire_conversation(args.conversation)
    except (ValueError, OSError) as exc:
        return _erreur(str(exc))
    debut = datetime.now(UTC)
    messages = [*historique, {"role": "user", "content": args.question}]
    texte: list[str] = []
    resultats: list[ResultatOutil] = []
    sources: Sources | None = None
    avertissements: list[Avertissement] = []
    fin: Fin | None = None
    code = CodeSortie.SUCCES
    try:
        with assembler(
            args.modele,
            fiche,
            hors_ligne=args.hors_ligne,
            variante=args.variante,
        ) as assemblage:
            for evenement in assemblage.service.repondre(fiche, messages):
                if args.json:
                    print(json.dumps(vers_dict(evenement), ensure_ascii=False), flush=True)
                else:
                    _afficher(evenement, resultats)
                if isinstance(evenement, Jeton):
                    texte.append(evenement.texte)
                elif isinstance(evenement, Sources):
                    sources = evenement
                elif isinstance(evenement, Avertissement):
                    avertissements.append(evenement)
                elif isinstance(evenement, Fin):
                    fin = evenement
                elif isinstance(evenement, Erreur):
                    print(f"\nslmsp : {evenement.message}", file=sys.stderr)
                    code = CodeSortie.ERREUR
            journal = [e for e in assemblage.journal.lister() if e.horodatage >= debut]
    except ModeleInvalide as exc:
        return _erreur(str(exc))
    if not args.json:
        print()
        for resultat in resultats:
            if not resultat.erreur:
                print(f"\nRésultat {resultat.nom} :\n{contenu_resultat(resultat.resultat)}")
        if sources is not None and sources.sources:
            print("\nSources :")
            for source in sources.sources:
                print(ligne_source(source))
        for avertissement in avertissements:
            print(f"\n{avertissement.message}")
        if fin is not None and fin.urls_inventees:
            print("\nURL absentes des sources : " + ", ".join(fin.urls_inventees))
    if args.journal:
        print("\nRequêtes sortantes :", file=sys.stderr if args.json else sys.stdout)
        for entree in reversed(journal):
            print(ligne_journal(entree), file=sys.stderr if args.json else sys.stdout)
        if not journal:
            print("(aucune)", file=sys.stderr if args.json else sys.stdout)
    if code == CodeSortie.SUCCES and fin is not None and args.conversation is not None:
        reponse = {"role": "assistant", "content": "".join(texte)}
        try:
            ecrire_conversation(args.conversation, [*messages, reponse])
        except OSError as exc:
            return _erreur(f"conversation non enregistrée : {exc}", CodeSortie.ERREUR)
    return int(code)
