"""Sous-commande `slmsp eval` : gel du jeu, génération, notation et sonde d'outils.

    slmsp eval gel --version v1.0 --verifier-seulement [--racine DIR]
    slmsp eval gel --version v1.0 --statut provisoire --graine 7 [--date-reference AAAA-MM-JJ]
        [--racine DIR]
    slmsp eval run --modele base:granite-4.0-1b --quantification q4_k_m --jeu v1.0
        [--phase generation|toutes] [--variante cpu|cuda] [--items ID,ID…] [--racine DIR]
        [--mode-juge batch|direct] [--plafond-estime EUR]
    slmsp eval run --phase generation --reprendre RUN_ID [--racine DIR]
    slmsp eval run --phase notation --depuis RUN_ID [--mode-juge batch|direct]
        [--plafond-estime EUR] [--racine DIR]
    slmsp eval juges-tiers --verifier
    slmsp eval juges-tiers --depuis RUN_NOTATION --juge NOM [--taches CR,LC,CT,RE]
        [--rejouer-invalides]
        [--plafond-estime EUR] [--racine DIR]
    slmsp eval comparer --runs NOTATION_A NOTATION_B [...] [--bootstrap 2000] [--graine 7]
        [--sortie FICHIER.md] [--racine DIR]
    slmsp eval composer --route TACHE=NOTATION_RUN [--route …] --defaut NOTATION_RUN
        [--marque deja-consulte] [--racine DIR]
    slmsp eval sonde-outils --modele base:<slug> [--jeu calibrage] [--items RD-001,RD-002]
        [--variante cpu|cuda] [--racine DIR]

`--verifier-seulement` n'écrit rien et sort en 0 sans erreur bloquante (les écarts de
composition sont listés). Le gel écrit `eval/jeu/<version>/MANIFEST.json` et
`eval/revue/echantillon-revue-<version>.md`, et refuse si l'un des deux existe.
`--date-reference AAAA-MM-JJ` inscrit l'ancre de date des références dans le manifeste ;
elle est refusée (code 2, rien n'est écrit) si elle est mal formée, postérieure à la date
du gel, ou donnée avec `--verifier-seulement`.

`run --phase generation` (story 5.3) : une ligne de progression par item, puis le chemin du
run, son statut et la durée moyenne par item. `run --phase notation --depuis RUN_ID`
(story 5.6) : note le run de génération `RUN_ID` (contrôles automatiques, Juge principal,
second juge sur l'échantillon, formules de la grille) dans un run `eval-notation`, puis
affiche le tableau des Scores de Tâche (« non relu » tant que la relecture n'est pas
validée). Pas de `--reprendre` pour la notation : la relancer suffit, le cache des verdicts
évite tout double paiement. `--mode-juge` surcharge le `mode_appel` de `juges.toml`.
`--plafond-estime EUR` (réel > 0, notation ou toutes) : estime le coût du Juge principal
avant de créer le run (verdicts en cache à 0, sortie moyenne du cache, tarif du mode) ;
au-dessus du plafond, code 1 sans run ni appel ; sinon l'estimation est affichée.
Le second juge (Mistral) n'est pas estimé. Avec `--phase toutes`, le contrôle a lieu après
la génération locale (gratuite) : un refus laisse le run de génération, à noter ensuite
par `--phase notation --depuis RUN_ID`.
`--phase toutes` (défaut) enchaîne la génération (ou sa reprise) et la notation du run
produit s'il est `complet` ou `partiel-erreur`.

`sonde-outils` (story 8.2, H-TOOLS) : passe les items RD en protocole d'outils `natif`, puis
en `json-generique`, puis en `balises-tool-call`, jusqu'au premier valide ; une ligne par
item, le tableau par protocole, le protocole recommandé et le run `eval-sonde`. Code 0 si
un protocole est valide et le run `complet`, 1 sinon (aucun protocole valide, ou item en erreur).

`juges-tiers` (story S3) : avis comparatif d'un juge tiers OpenRouter (`[juges_tiers.<nom>]`
de `juges.toml`) sur un run `eval-notation`, sans toucher au score officiel ni au run source ;
nouveau run `eval-juges-tiers` (`verdicts.jsonl`, `accords.json`), puis tableau des accords.
`--verifier` affiche la présence de la clé et les modèles des familles retenues avec leur
prix (`GET /models`, gratuit), sans génération ; code 0, 1 si la liste est inaccessible.

`comparer` (story E1b) : bootstrap apparié des scores de runs `eval-notation` (lecture seule,
aucun appel au juge) ; le premier run est la référence A. Tableau Markdown par Tâche et
Qualité : écart B − A, IC 95 %, P(écart > 0), et bruit items de la Qualité de chaque run.

`composer` (story 15.1) : run `eval-notation` composé, lisible tel quel par `comparer` : chaque
Tâche reprend les verdicts et le Score de Tâche du run routé (`--route CR=RUN`), sinon du run
`--defaut`. Lecture seule des sources, aucun appel. Sources `complet` ou `partiel-erreur` (le
run composé prend le moins bon statut et liste les sources partielles). Refus (code 2, rien
d'écrit) pour un autre statut, ou si les sources diffèrent par le jeu et ses items, la grille,
le juge principal ou les prompts de Tâche. `--marque deja-consulte` consigne que la
composition a été choisie en ayant vu ses scores. Le Comparatif ignore les runs composés.

Code 0 si le dernier run est `complet`, 1 s'il est `partiel-erreur` ou `partiel-budget`, 2
pour une erreur d'usage, 4 si le jeu est altéré ou si le run repris diffère de la demande.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections.abc import Callable
from datetime import date, datetime
from pathlib import Path
from typing import Any, Final

from slmsp.core.erreurs import CodeSortie


def _aide(parseur: argparse.ArgumentParser) -> Callable[[argparse.Namespace], int]:
    def executer(_args: argparse.Namespace) -> int:
        parseur.print_help(sys.stderr)
        return int(CodeSortie.USAGE)

    return executer


def _usage(message: str) -> int:
    print(f"slmsp : eval gel : {message}", file=sys.stderr)
    return int(CodeSortie.USAGE)


MOTIF_DATE: Final = r"[0-9]{4}-[0-9]{2}-[0-9]{2}"
"""Forme exigée de `--date-reference` (AAAA-MM-JJ)."""


def _date_reference(valeur: str, maintenant: datetime) -> date | str:
    """Date de `--date-reference`, ou le message d'erreur d'usage."""
    if not re.fullmatch(MOTIF_DATE, valeur):
        return f"date de référence invalide : {valeur!r} (attendu : AAAA-MM-JJ)"
    try:
        jour = date.fromisoformat(valeur)
    except ValueError:
        return f"date de référence invalide : {valeur!r} (attendu : AAAA-MM-JJ)"
    if jour > maintenant.date():
        return (
            f"date de référence {valeur} postérieure à la date du gel "
            f"({maintenant.date().isoformat()})"
        )
    return jour


def executer_gel(args: argparse.Namespace) -> int:
    """`slmsp eval gel` : vérification seule, ou gel complet."""
    from slmsp.core.items import MOTIF_VERSION
    from slmsp.evaluation.gel import JeuNonConforme, gel, verifier_jeu

    if not re.fullmatch(MOTIF_VERSION, args.version):
        return _usage(f"version de jeu invalide : {args.version!r} (attendu : vN, vN.M ou devN)")
    racine = Path(args.racine) if args.racine is not None else None
    if args.verifier_seulement:
        if args.statut is not None or args.graine is not None:
            return _usage("--verifier-seulement exclut --statut et --graine")
        if args.date_reference is not None:
            return _usage("--verifier-seulement exclut --date-reference")
        rapport = verifier_jeu(args.version, racine)
        print(rapport.texte())
        if rapport.erreurs:
            raise JeuNonConforme(
                f"jeu {args.version} non conforme : {len(rapport.erreurs)} erreur(s) bloquante(s)",
                rapport.erreurs,
            )
        return int(CodeSortie.SUCCES)
    if args.statut is None or args.graine is None:
        return _usage("--statut et --graine sont requis (ou --verifier-seulement)")
    maintenant = datetime.now().astimezone()
    date_reference = None
    if args.date_reference is not None:
        lue = _date_reference(args.date_reference, maintenant)
        if isinstance(lue, str):
            return _usage(lue)
        date_reference = lue
    manifeste = gel(
        args.version,
        args.statut,
        args.graine,
        racine,
        maintenant=maintenant,
        date_reference=date_reference,
    )
    print(f"Jeu {manifeste.version} gelé ({manifeste.statut}) : {manifeste.nb_items} items.")
    print(f"Fichiers empreints : {len(manifeste.fichiers)}.")
    print(
        f"Échantillons (graine {manifeste.echantillons.graine}) : second juge "
        f"{len(manifeste.echantillons.second_juge)}, relecture "
        f"{len(manifeste.echantillons.relecture)}."
    )
    if manifeste.date_reference is not None:
        print(f"Date de référence : {manifeste.date_reference.isoformat()}.")
    print(f"Écarts de composition inscrits : {len(manifeste.ecarts)}.")
    for ecart in manifeste.ecarts:
        print(f"- {ecart}")
    print(
        f"Écrits : eval/jeu/{manifeste.version}/MANIFEST.json et "
        f"eval/revue/echantillon-revue-{manifeste.version}.md (à commiter)."
    )
    return int(CodeSortie.SUCCES)


PHASES: Final = ("generation", "notation", "toutes")


def _reel_positif(valeur: str) -> float:
    try:
        nombre = float(valeur)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{valeur!r} n'est pas un nombre") from None
    if not math.isfinite(nombre) or nombre <= 0:
        raise argparse.ArgumentTypeError("doit être un réel strictement positif")
    return nombre


def _usage_run(message: str) -> int:
    print(f"slmsp : eval run : {message}", file=sys.stderr)
    return int(CodeSortie.USAGE)


def _items(valeur: str | None) -> list[str] | None:
    if valeur is None:
        return None
    return [identifiant.strip() for identifiant in valeur.split(",") if identifiant.strip()]


def _rapporter(generation: Any, rang: int, total: int) -> None:
    tronquee = " tronquée" if generation.tronquee else ""
    print(
        f"[{rang}/{total}] {generation.item_id} {generation.statut}{tronquee} "
        f"({generation.duree_ms} ms)",
        flush=True,
    )


def _manquants(args: argparse.Namespace) -> list[str]:
    return [
        option
        for option, valeur in (
            ("--modele", args.modele),
            ("--quantification", args.quantification),
            ("--jeu", args.jeu),
        )
        if valeur is None
    ]


def _generation(args: argparse.Namespace, racine: Path | None) -> Any:
    """Lance ou reprend la phase génération ; rend le rapport, ou un code d'usage (int)."""
    from slmsp.evaluation import assemblage
    from slmsp.evaluation.generation import lancer_generation, reprendre_generation

    try:
        if args.reprendre is not None:
            if args.items is not None:
                return _usage_run("--items est fixé par le run repris")
            return reprendre_generation(
                args.reprendre,
                racine=racine,
                fabrique=assemblage.ouvrir_harnais,
                rapporter=_rapporter,
                modele_ref=args.modele,
                quantification=args.quantification,
                jeu=args.jeu,
                variante=args.variante,
            )
        manquants = _manquants(args)
        if manquants:
            return _usage_run(f"{', '.join(manquants)} requis (ou --reprendre RUN_ID)")
        return lancer_generation(
            args.modele,
            args.quantification,
            args.jeu,
            variante=args.variante or "cpu",
            items=_items(args.items),
            racine=racine,
            fabrique=assemblage.ouvrir_harnais,
            rapporter=_rapporter,
        )
    except ValueError as exc:
        return _usage_run(str(exc))


def _afficher_generation(rapport: Any) -> None:
    moyenne = rapport.duree_moyenne_ms
    print(f"Run : {rapport.run.dossier}")
    print(
        f"Statut du run : {rapport.statut} (cette session : {rapport.ok} ok, "
        f"{rapport.erreur} en erreur, {rapport.sautes} déjà présent(s))"
    )
    if rapport.tronquees:
        print(f"Sorties tronquées au plafond max_tokens (cette session) : {rapport.tronquees}")
    print(
        "Durée moyenne par item (cette session) : "
        + ("sans objet" if moyenne is None else f"{moyenne:.0f} ms")
    )


def _nombre(valeur: float | None, decimales: int) -> str:
    return "—" if valeur is None else f"{valeur:.{decimales}f}"


COLONNES: Final = (
    ("Tâche", 5),
    ("Score", 7),
    ("Notés", 5),
    ("Jugés", 5),
    ("Invalides", 9),
    ("Non jugés", 9),
    ("En erreur", 9),
    ("2nd juge", 8),
    ("Kappa", 6),
)


def tableau_scores(scores: Any) -> str:
    """Tableau texte des Scores de Tâche : score, effectifs, kappa et statuts."""
    from slmsp.evaluation.scores import CRITERES_KAPPA

    lignes = ["  ".join(titre.ljust(largeur) for titre, largeur in COLONNES) + "  Statuts"]
    for code, score in scores.taches.items():
        effectifs = score.effectifs
        statuts = [score.statuts.jeu_statut]
        statuts.append("relu" if score.statuts.verdicts_relus else "non relu")
        if score.statuts.fragile:
            statuts.append("fragile")
        elif code in CRITERES_KAPPA and score.kappa.valeur is None:
            statuts.append("kappa non calculé")
        if score.statuts.plafonne_lc:
            statuts.append("plafonné LC")
        valeurs = (
            code,
            _nombre(score.score, 1),
            effectifs.notes,
            effectifs.juges,
            effectifs.invalides,
            effectifs.non_juges,
            effectifs.en_erreur,
            effectifs.second_juge,
            _nombre(score.kappa.valeur, 2),
        )
        cellules = [
            str(valeur).ljust(largeur)
            for valeur, (_, largeur) in zip(valeurs, COLONNES, strict=True)
        ]
        lignes.append("  ".join(cellules) + "  " + ", ".join(statuts))
    return "\n".join(lignes)


def _afficher_notation(rapport: Any) -> None:
    scores = rapport.scores
    print(f"Run de notation : {rapport.run.dossier}")
    print(
        f"Statut du run : {rapport.statut} (Juge principal : {rapport.demandes_principal} "
        f"demande(s), second juge : {rapport.demandes_second}, {rapport.depuis_cache} depuis le "
        f"cache ; coût de cette session {rapport.cout_session_eur:.4f} €)"
    )
    print(
        f"Scores de Tâche (jeu {scores.jeu_version}, {scores.jeu_statut}) ; coût cumulé du Juge "
        f"{scores.cout_juge_total_eur:.4f} € :"
    )
    print(tableau_scores(scores))


def _code(statut: str) -> int:
    return int(CodeSortie.SUCCES if statut == "complet" else CodeSortie.ERREUR)


def _rapporter_notation(message: str) -> None:
    print(message, flush=True)


def _phase_notation(args: argparse.Namespace, racine: Path | None) -> int:
    from slmsp.evaluation import notation

    if args.depuis is None:
        return _usage_run("--depuis RUN_ID requis pour --phase notation")
    if args.reprendre is not None:
        return _usage_run(
            "pas de --reprendre pour la notation : la relancer suffit (cache des verdicts)"
        )
    inutiles = [
        option
        for option, valeur in (
            ("--modele", args.modele),
            ("--quantification", args.quantification),
            ("--jeu", args.jeu),
            ("--variante", args.variante),
            ("--items", args.items),
        )
        if valeur is not None
    ]
    if inutiles:
        return _usage_run(f"{', '.join(inutiles)} sans objet pour --phase notation")
    try:
        jeu = notation.jeu_du_run(args.depuis, racine)
        juges = notation.ouvrir_juges(racine, args.mode_juge, jeu)
    except ValueError as exc:
        return _usage_run(str(exc))
    rapport = notation.noter(
        args.depuis,
        juges=juges,
        racine=racine,
        rapporter=_rapporter_notation,
        plafond_estime_eur=args.plafond_estime,
    )
    _afficher_notation(rapport)
    return _code(rapport.statut)


def executer_run(args: argparse.Namespace) -> int:
    """`slmsp eval run` : génération (lancement ou reprise), notation, ou les deux."""
    from slmsp.evaluation import modele_ref, notation

    racine = Path(args.racine) if args.racine is not None else None
    try:
        if args.modele is not None:
            args.modele = modele_ref.composer_lora(args.modele, args.echelle_lora)
        elif args.echelle_lora is not None:
            return _usage_run("--echelle-lora exige --modele lora:<EXPORT_LORA_RUN_ID>")
    except ValueError as exc:
        return _usage_run(str(exc))
    if args.phase == "notation":
        return _phase_notation(args, racine)
    if args.depuis is not None:
        return _usage_run("--depuis ne vaut que pour --phase notation")
    juges = None
    if args.phase == "toutes":
        manquants = _manquants(args) if args.reprendre is None else []
        if manquants:
            return _usage_run(f"{', '.join(manquants)} requis (ou --reprendre RUN_ID)")
        try:
            jeu = args.jeu
            if args.reprendre is not None:
                jeu = notation.jeu_du_run(args.reprendre, racine)
                if args.jeu is not None and args.jeu != jeu:
                    return _usage_run(
                        f"--jeu {args.jeu} différent du jeu du run repris ({jeu}) : "
                        "les juges dépendent du jeu"
                    )
            juges = notation.ouvrir_juges(racine, args.mode_juge, jeu)  # avant toute génération
        except ValueError as exc:
            return _usage_run(str(exc))
    elif args.mode_juge is not None:
        return _usage_run("--mode-juge sans objet pour --phase generation")
    elif args.plafond_estime is not None:
        return _usage_run("--plafond-estime sans objet pour --phase generation")
    rapport = _generation(args, racine)
    if isinstance(rapport, int):
        return rapport
    _afficher_generation(rapport)
    if juges is None:
        return _code(rapport.statut)
    if rapport.statut not in notation.STATUTS_PARENT:
        print(f"Notation non lancée : génération au statut {rapport.statut}.", file=sys.stderr)
        return int(CodeSortie.ERREUR)
    resultat = notation.noter(
        rapport.run.run_id,
        juges=juges,
        racine=racine,
        rapporter=_rapporter_notation,
        plafond_estime_eur=args.plafond_estime,
    )
    _afficher_notation(resultat)
    return _code(resultat.statut)


def _usage_sonde(message: str) -> int:
    print(f"slmsp : eval sonde-outils : {message}", file=sys.stderr)
    return int(CodeSortie.USAGE)


def _rapporter_sonde(ligne: dict[str, Any], rang: int, total: int) -> None:
    print(
        f"[{ligne['protocole']} {rang}/{total}] {ligne['item_id']} {ligne['statut']} : "
        f"{ligne['appels_valides']}/{ligne['appels_attendus']} appel(s) attendu(s) apparié(s), "
        f"{ligne['non_conformes']} non conforme(s) → "
        f"{'valide' if ligne['valide'] else 'invalide'} ({ligne['duree_ms']} ms)",
        flush=True,
    )


COLONNES_SONDE: Final = (
    ("Protocole", 14),
    ("Items valides", 13),
    ("Appels valides", 14),
    ("Taux", 5),
    ("Non conformes", 13),
    ("En erreur", 9),
)


def tableau_sonde(bilans: Any) -> str:
    """Tableau texte des passes de la sonde : effectifs, taux et verdict par protocole."""
    lignes = ["  ".join(titre.ljust(largeur) for titre, largeur in COLONNES_SONDE) + "  Verdict"]
    for protocole, bilan in bilans.items():
        valeurs = (
            protocole,
            f"{bilan.items_valides}/{bilan.items}",
            f"{bilan.appels_valides}/{bilan.appels_attendus}",
            _nombre(bilan.taux_appels_valides, 2),
            bilan.non_conformes,
            bilan.erreurs,
        )
        cellules = [
            str(valeur).ljust(largeur)
            for valeur, (_, largeur) in zip(valeurs, COLONNES_SONDE, strict=True)
        ]
        lignes.append("  ".join(cellules) + "  " + ("valide" if bilan.valide else "invalide"))
    return "\n".join(lignes)


def executer_sonde(args: argparse.Namespace) -> int:
    """`slmsp eval sonde-outils` : protocoles d'outils `natif`, `json-generique`, `balises-…`."""
    from slmsp.evaluation import assemblage
    from slmsp.evaluation.sonde_outils import sonder

    if args.modele is None:
        return _usage_sonde("--modele base:<slug> requis")
    racine = Path(args.racine) if args.racine is not None else None
    try:
        rapport = sonder(
            args.modele,
            jeu=args.jeu,
            items=_items(args.items),
            variante=args.variante,
            racine=racine,
            fabrique=assemblage.ouvrir_harnais,
            rapporter=_rapporter_sonde,
        )
    except ValueError as exc:
        return _usage_sonde(str(exc))
    print(tableau_sonde(rapport.bilans))
    verdict = "valide" if rapport.valide else "aucun protocole valide"
    print(f"Protocole recommandé : {rapport.protocole_recommande} ({verdict})")
    if rapport.motif:
        print(f"Motif : {rapport.motif}")
    print(f"Run : {rapport.run.dossier}")
    print(f"Statut du run : {rapport.statut}")
    if rapport.valide and rapport.statut == "complet":
        return int(CodeSortie.SUCCES)
    return int(CodeSortie.ERREUR)


def _entier_positif(valeur: str) -> int:
    try:
        nombre = int(valeur)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{valeur!r} n'est pas un entier") from None
    if nombre < 1:
        raise argparse.ArgumentTypeError("doit être un entier au moins égal à 1")
    return nombre


def executer_comparer(args: argparse.Namespace) -> int:
    """`slmsp eval comparer` : bootstrap apparié des scores de runs de notation."""
    from slmsp.evaluation import bootstrap

    try:
        resultat = bootstrap.comparer_runs(
            args.runs,
            racine=args.racine,
            tirages=args.bootstrap,
            graine=args.graine,
            autoriser_jeux_differents=args.autoriser_jeux_differents,
        )
    except ValueError as exc:
        print(f"slmsp : eval comparer : {exc}", file=sys.stderr)
        return int(CodeSortie.USAGE)
    tableau = bootstrap.tableau_markdown(resultat)
    print(tableau)
    if args.sortie is not None:
        Path(args.sortie).write_text(tableau, encoding="utf-8", newline="\n")
    return int(CodeSortie.SUCCES)


def _route(valeur: str) -> tuple[str, str]:
    tache, separateur, run_id = valeur.partition("=")
    if not separateur or not tache or not run_id:
        raise argparse.ArgumentTypeError(f"{valeur!r} : forme attendue TACHE=NOTATION_RUN_ID")
    return tache, run_id


def executer_composer(args: argparse.Namespace) -> int:
    """`slmsp eval composer` : run de notation composé par routage de Tâche."""
    from slmsp.core.erreurs import SlmspError
    from slmsp.evaluation import composition

    route = dict(args.route)
    if len(route) != len(args.route):
        print("slmsp : eval composer : une Tâche est routée deux fois", file=sys.stderr)
        return int(CodeSortie.USAGE)
    try:
        run = composition.composer(route, args.defaut, marque=args.marque, racine=args.racine)
    except composition.ErreurComposition as exc:
        print(f"slmsp : eval composer : {exc}", file=sys.stderr)
        return int(CodeSortie.USAGE)
    except SlmspError as exc:
        print(f"slmsp : eval composer : {exc}", file=sys.stderr)
        return int(exc.code_sortie)
    print(f"Run composé : {run.run_id} ({run.dossier}), statut {run.statut_courant()}")
    return int(CodeSortie.SUCCES)


def _usage_tiers(message: str) -> int:
    print(f"slmsp : eval juges-tiers : {message}", file=sys.stderr)
    return int(CodeSortie.USAGE)


def _afficher_verification(bilan: Any) -> None:
    cle = "présente" if bilan.cle_presente else "absente"
    print(f"{bilan.fournisseur} : clé {bilan.nom_secret} {cle}")
    if bilan.erreur is not None:
        print(f"  liste des modèles inaccessible : {bilan.erreur}")
        return
    print(f"  {len(bilan.modeles)} modèle(s) des familles retenues (USD par million de tokens) :")
    for modele in bilan.modeles:
        print(
            f"  {modele['id']:<55} entrée {_nombre(modele['entree_usd_mtok'], 3):>8}  "
            f"sortie {_nombre(modele['sortie_usd_mtok'], 3):>8}  contexte {modele['contexte']}"
        )


def executer_juges_tiers(args: argparse.Namespace) -> int:
    """`slmsp eval juges-tiers` : vérification sans dépense, ou avis d'un juge tiers."""
    if args.verifier:
        if args.depuis is not None or args.juge is not None:
            return _usage_tiers("--verifier ne prend ni --depuis ni --juge")
        from slmsp.fournisseurs.client import FOURNISSEURS, verifier

        bilans = [verifier(config) for config in FOURNISSEURS.values()]
        for bilan in bilans:
            _afficher_verification(bilan)
        return int(CodeSortie.ERREUR if any(b.erreur for b in bilans) else CodeSortie.SUCCES)
    if args.depuis is None or args.juge is None:
        return _usage_tiers("--depuis RUN_ID et --juge NOM requis (ou --verifier)")
    from slmsp.evaluation import juges_tiers

    taches = _items(args.taches) or list(juges_tiers.TACHES_DEFAUT)
    racine = Path(args.racine) if args.racine is not None else None
    try:
        juge = juges_tiers.ouvrir_juge_tiers(
            args.juge, racine, rejouer_invalides=args.rejouer_invalides
        )
    except ValueError as exc:
        return _usage_tiers(str(exc))
    try:
        rapport = juges_tiers.noter_tiers(
            args.depuis,
            juge=juge,
            nom_juge=args.juge,
            taches=taches,
            racine=racine,
            plafond_estime_eur=args.plafond_estime,
            rapporter=_rapporter_notation,
        )
    except ValueError as exc:
        return _usage_tiers(str(exc))
    print(juges_tiers.tableau_accords(rapport.accords))
    print(
        f"Run : {rapport.run.dossier} ({rapport.statut}) ; {rapport.demandes} demande(s), "
        f"{rapport.depuis_cache} en cache ; coût de la session {rapport.cout_session_eur:.4f} €"
    )
    return _code(rapport.statut)


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `eval` et ses sous-commandes au parseur de `slmsp`."""
    parseur = sous_parseurs.add_parser(
        "eval",
        help="Jeu d'évaluation : gel, génération, notation et sonde d'outils",
        description="Jeu d'évaluation : gel, génération, notation et sonde d'outils.",
    )
    actions = parseur.add_subparsers(dest="eval_commande", metavar="<action>")
    parseur.set_defaults(func=_aide(parseur))

    gel = actions.add_parser(
        "gel",
        help="vérifier et geler une version du Jeu d'évaluation",
        description="Vérifie le jeu (items, cassettes, composition) et le gèle par manifeste.",
    )
    gel.add_argument("--version", required=True, help="version du jeu (vN, vN.M ou devN)")
    gel.add_argument(
        "--verifier-seulement",
        action="store_true",
        help="vérifier sans rien écrire (code 0 sans erreur bloquante)",
    )
    gel.add_argument(
        "--statut",
        choices=("provisoire", "relu", "relu-llm"),
        help="statut du gel (relu-llm : jeu de développement, jamais une mesure finale)",
    )
    gel.add_argument("--graine", type=int, help="graine des échantillons (second juge, relecture)")
    gel.add_argument(
        "--date-reference",
        metavar="AAAA-MM-JJ",
        help="ancre de date des références, inscrite dans le manifeste (au plus la date du gel)",
    )
    gel.add_argument("--racine", help="racine du dépôt (défaut : racine du projet)")
    gel.set_defaults(func=executer_gel)

    run = actions.add_parser(
        "run",
        help="évaluer un modèle sur le Jeu d'évaluation (génération, notation)",
        description=(
            "Évalue un modèle sur le Jeu d'évaluation : génération sans réseau, puis notation "
            "(contrôles automatiques, juges, Scores de Tâche)."
        ),
    )
    run.add_argument(
        "--modele",
        help="modèle évalué : base:<slug>, ft:<export_run_id> ou lora:<export_lora_run_id>",
    )
    run.add_argument(
        "--echelle-lora",
        type=_reel_positif,
        metavar="ECHELLE",
        help="avec lora:<id> : échelle de --lora-scaled sur la base q4_k_m (défaut 1.0) ; "
        "consignée dans la référence du run (lora:<id>@<échelle>) et dans son manifeste",
    )
    run.add_argument("--quantification", choices=("f16", "q4_k_m"), help="quantification")
    run.add_argument("--jeu", help="version du jeu (vN, vN.M, devN ou calibrage)")
    run.add_argument("--variante", choices=("cpu", "cuda"), help="variante llama.cpp (cpu)")
    run.add_argument(
        "--phase",
        choices=PHASES,
        default="toutes",
        help="phase à exécuter (défaut : toutes = génération puis notation)",
    )
    run.add_argument("--items", help="identifiants d'items séparés par des virgules")
    run.add_argument("--reprendre", metavar="RUN_ID", help="reprendre ce run en ajout seul")
    run.add_argument(
        "--depuis", metavar="RUN_ID", help="run de génération à noter (--phase notation)"
    )
    run.add_argument(
        "--mode-juge",
        choices=("batch", "direct"),
        help="mode d'appel du Juge principal (défaut : celui de juges.toml)",
    )
    run.add_argument(
        "--plafond-estime",
        type=_reel_positif,
        metavar="EUR",
        help="refuser la notation si le coût estimé du Juge principal dépasse ce plafond (EUR)",
    )
    run.add_argument("--racine", help="racine du dépôt (défaut : racine du projet)")
    run.set_defaults(func=executer_run)

    tiers = actions.add_parser(
        "juges-tiers",
        help="avis comparatif d'un juge tiers OpenRouter sur un run de notation (hors score)",
        description=(
            "Fait noter par un juge tiers OpenRouter les items jugés d'un run eval-notation et "
            "mesure son accord avec le Juge principal et le second juge (hors score officiel)."
        ),
    )
    tiers.add_argument(
        "--verifier",
        action="store_true",
        help="clé présente ou absente et modèles disponibles (gratuit, aucune génération)",
    )
    tiers.add_argument("--depuis", metavar="RUN_ID", help="run eval-notation à comparer")
    tiers.add_argument("--juge", metavar="NOM", help="section [juges_tiers.<NOM>] de juges.toml")
    tiers.add_argument("--taches", help="Tâches séparées par des virgules (défaut : CR,LC,CT,RE)")
    tiers.add_argument(
        "--plafond-estime",
        type=_reel_positif,
        metavar="EUR",
        help="refuser si le coût estimé du juge tiers dépasse ce plafond (EUR)",
    )
    tiers.add_argument(
        "--rejouer-invalides",
        action="store_true",
        help="rejuger les items dont le verdict en cache est `invalide` (payant)",
    )
    tiers.add_argument("--racine", help="racine du dépôt (défaut : racine du projet)")
    tiers.set_defaults(func=executer_juges_tiers)

    comparer = actions.add_parser(
        "comparer",
        help="bootstrap apparié des scores de runs de notation (bruit d'items, lecture seule)",
        description=(
            "Rééchantillonne les items de chaque Tâche (mêmes items pour tous les runs) et "
            "donne l'écart B − A, son IC 95 % et le bruit items de la Qualité. Aucun appel "
            "au juge."
        ),
    )
    comparer.add_argument(
        "--runs", nargs="+", required=True, metavar="RUN_NOTATION", help="A (référence), puis B…"
    )
    comparer.add_argument("--bootstrap", type=_entier_positif, default=2000, help="tirages")
    comparer.add_argument("--graine", type=int, default=7, help="graine du rééchantillonnage")
    comparer.add_argument("--sortie", metavar="FICHIER", help="écrire aussi le tableau Markdown")
    comparer.add_argument(
        "--autoriser-jeux-differents",
        action="store_true",
        help="comparer malgré des jeux ou des juges principaux différents (avertissement)",
    )
    comparer.add_argument("--racine", help="racine du dépôt (défaut : racine du projet)")
    comparer.set_defaults(func=executer_comparer)

    composer = actions.add_parser(
        "composer",
        help="composer un run de notation par routage de Tâche (lecture seule, aucun appel)",
        description=(
            "Crée un run eval-notation où chaque Tâche reprend les verdicts et le Score de "
            "Tâche du run routé, sinon du run par défaut ; lisible par `eval comparer`."
        ),
    )
    composer.add_argument(
        "--route",
        action="append",
        type=_route,
        default=[],
        metavar="TACHE=RUN_NOTATION",
        help="Tâche routée vers un run de notation (répétable)",
    )
    composer.add_argument(
        "--defaut", required=True, metavar="RUN_NOTATION", help="run des autres Tâches"
    )
    composer.add_argument(
        "--marque",
        choices=("deja-consulte",),
        help="consigne que la composition a été choisie après consultation des scores",
    )
    composer.add_argument("--racine", help="racine du dépôt (défaut : racine du projet)")
    composer.set_defaults(func=executer_composer)

    sonde = actions.add_parser(
        "sonde-outils",
        help=(
            "sonder le tool calling d'un candidat (H-TOOLS) : natif, json-generique, "
            "balises-tool-call"
        ),
        description=(
            "Passe les items RD du calibrage par le Harnais d'évaluation en protocole d'outils "
            "natif, puis json-generique, puis balises-tool-call, jusqu'au premier valide, et "
            "recommande un protocole."
        ),
    )
    sonde.add_argument("--modele", help="candidat sondé : base:<slug>")
    sonde.add_argument("--jeu", default="calibrage", help="version du jeu (défaut : calibrage)")
    sonde.add_argument("--items", help="items RD séparés par des virgules (défaut : RD-001,RD-002)")
    sonde.add_argument(
        "--variante", choices=("cpu", "cuda"), default="cpu", help="variante llama.cpp (cpu)"
    )
    sonde.add_argument("--racine", help="racine du dépôt (défaut : racine du projet)")
    sonde.set_defaults(func=executer_sonde)
