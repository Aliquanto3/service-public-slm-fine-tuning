"""`slmsp data {seed, generate, validate, filter, build}` : pipeline des Données (AD-17).

Les étapes `seed` (9.3), `generate` (9.4), `validate`, `filter` (9.5) et `build` (9.6) sont
implémentées.

`seed [--racine DIR] [--facteur N] [--scenarios N] [--courriers {N,auto}]
[--taches T1,T2 --completer-depuis SEED_RUN_ID]` constitue
`runs/data-seed/<run_id>/` (`amorces.jsonl`, `comptes.json`) depuis les jeux publics de
`config/sources.toml`, déjà téléchargés sous `<racine>/data/raw/mediatech/` par
`slmsp fetch sources` (extra `data` : pyarrow). Les longueurs RE sont tirées dans
`[seed].re_longueurs` de `config/donnees.toml`. Les scénarios de réunion (`--scenarios N`)
et les amorces de courrier type (`--courriers N`, ou `auto` = volume CT x facteur) sont
générés par Mistral, opt-in (0 par défaut) : ils exigent le gel commité du Jeu d'évaluation
v1.1 (code 4 sinon). Les amorces CT d'une session déjà journalisée sont réutilisées sans
nouvel appel (relance idempotente). `--taches LC --completer-depuis SEED_RUN_ID` (seed
partiel, story O6b) ne tire que ces Tâches et recopie à l'identique les amorces des autres.

`generate (--depuis SEED_RUN_ID | --reprendre RUN_ID) [--racine DIR] [--surplus X]` produit
`runs/data-generate/<run_id>/` par le Générateur Mistral (`slmsp.data.generate`). Il exige
d'abord le gel commité du Jeu d'évaluation v1.0 (D1.3, code 4), puis les préalables Mistral
du jour (D1.2, code 1), avant toute écriture. Les passages des sessions Q viennent de l'Index
local (BGE-M3 démarré à la première recherche) ; les traces RD passent par `McpEnDirect`
(profil `outillage`). Appels Mistral payants : commande réservée à la campagne (9.8).
`--modele-generateur MODELE` remplace `modele_generateur` de `config/mistral.toml` (liste stable
ou préversion du Générateur ; à la reprise, défaut : le modèle du run). `--taches CR,CT,LC`
ne génère que ces Tâches ; `--completer-depuis GENERATE_RUN_ID` y ajoute, sans appel, les
sessions closes des autres Tâches d'un run du même seed (story S5). `--verifiee [--sans-juge]
[--essais-max N] [--plafond-estime-openrouter EUR]` vérifie chaque cible CR, LC, CT (contrôles
déterministes puis juge de données, `slmsp.data.generation_verifiee`, story O6a), régénère
une cible refusée avec ses motifs (gabarits `*-correction`, au plus `essais_max - 1` fois,
story O6b) puis écarte les refusées ; `--plafond-estime-mistral EUR` refuse un lancement plus
cher (0 : aucun appel Mistral nouveau). À la reprise, les réglages de vérification sont
relus du run.

`validate --depuis GENERATE_RUN_ID [--racine DIR] [--controle-mistral]` rejoue les traces RD
sur le Bac à sable et vérifie URL et valeurs de chaque exemple contre ses sources
(`slmsp.data.validate`) ; `--controle-mistral` ajoute un contrôle de fidélité des Tâches CR, LC
et RE par Mistral (`usage = validation`, appels payants, jamais le Juge Claude).
`juger (--depuis GENERATE_RUN_ID | --reprendre RUN_ID) [--taches CR,LC,CT] [--limite N]
[--plafond-estime EUR]` note les cibles candidates par le juge de données DeepSeek via OpenRouter
(`slmsp.data.juge_donnees`, story O1, appels payants, usage `juge-donnees-openrouter`) et écrit
`runs/data-juger/<run_id>/` ; jamais le Juge Claude, rien n'est lu sous `eval/`.
`filter --depuis VALIDATE_RUN_ID [--racine DIR]` retire doublons et fuites du Jeu d'évaluation
(v1.0, v1.1, calibrage) par n-grammes hachés et cosinus BGE-M3 (`slmsp.data.filter`). Chacune
imprime exemples et taux de rejet par motif et par Tâche (FR-30).
`build --depuis FILTER_RUN_ID --variante {diffusable,recherche} [--racine DIR]` refabrique chaque
ligne depuis les réponses Mistral journalisées, la compare octet par octet et écrit
`data/train/vN/{train.jsonl,MANIFEST.json}` (`slmsp.data.build`, une version n'est jamais réécrite).
`build --preferences --depuis BUILD_RUN_ID --modele base:SLUG [--llama {cpu,cuda}]` construit les
paires ORPO (chosen : exemple SFT ; rejected : génération du Modèle de base local, journalisée
dans `generations-locales.sqlite`) dans une nouvelle version `data/train/vN/preferences.jsonl`
(`slmsp.data.preferences`, dérogation FR-34 au MANIFEST).
`build --sous-ensemble --depuis BUILD_RUN_ID --taches T1,T2,...` garde, dans une nouvelle version
`data/train/vN/`, les seules lignes des Tâches demandées, copiées à l'identique
(`slmsp.data.sous_ensemble`, test M1 partiel).
`build --nettoyage --depuis BUILD_RUN_ID --modele base:SLUG` retire le préambule « Voici » des
cibles, écarte celles qui dépassent `max_tokens` de l'évaluation (tokenizer du modèle) et signale
les LC infidèles, dans une nouvelle version `data/train/vN/` (`slmsp.data.nettoyage`, story 9.9).

Codes de sortie : 0 run complet ; 1 erreur ou run partiel ; 3 budget Mistral épuisé ;
4 gel absent, provenance invalide ou manifeste incohérent.

`--racine` désigne la racine de `data/`, `eval/`, `runs/` (défaut : racine du projet) ;
les fichiers de `config/` suivent le code exécuté. Ce module n'importe pyarrow qu'à
l'exécution de `seed`.
"""

from __future__ import annotations

import argparse
import io
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import ExitStack
from datetime import date
from pathlib import Path
from typing import Any

from slmsp.core.config import racine_projet
from slmsp.core.erreurs import (
    CodeSortie,
    ConfigurationInvalide,
    ProvenanceInvalide,
    ReponseTronquee,
)
from slmsp.data.config import charger_config_donnees
from slmsp.data.licences import RegistreLicences
from slmsp.data.seed import (
    FACTEUR_DEFAUT,
    GABARIT_AMORCES_CT,
    GABARIT_SCENARIO,
    Decodeur,
    FabriqueCourrier,
    FabriqueScenario,
    FichierJeu,
    JeuPublic,
    construire_protection,
    executer_seed,
    versions_protegees,
)
from slmsp.fetch.config import ConfigSources, charger_config_sources
from slmsp.fetch.sources import dossier_jeu

TAILLE_LOT = 8192
"""Lignes décodées par lot de lecture parquet."""


def _entier_positif(valeur: str) -> int:
    try:
        nombre = int(valeur)
    except ValueError:
        raise argparse.ArgumentTypeError(f"entier attendu (reçu {valeur!r})") from None
    if nombre < 1:
        raise argparse.ArgumentTypeError("entier strictement positif attendu")
    return nombre


def _entier_positif_ou_nul(valeur: str) -> int:
    try:
        nombre = int(valeur)
    except ValueError:
        raise argparse.ArgumentTypeError(f"entier attendu (reçu {valeur!r})") from None
    if nombre < 0:
        raise argparse.ArgumentTypeError("entier positif ou nul attendu")
    return nombre


def _courriers(valeur: str) -> int | str:
    """`auto` ou entier positif ou nul (nombre d'appels Mistral pour les amorces CT)."""
    if valeur == "auto":
        return valeur
    return _entier_positif_ou_nul(valeur)


def _liste_taches(valeur: str) -> list[str]:
    from slmsp.data.generate import ORDRE_TACHES

    taches = [t.strip() for t in valeur.split(",") if t.strip()]
    inconnues = [t for t in taches if t not in ORDRE_TACHES]
    if not taches or inconnues:
        raise argparse.ArgumentTypeError(
            f"Tâches attendues parmi {', '.join(ORDRE_TACHES)} : {valeur!r}"
        )
    return taches


def _fraction(valeur: str) -> float:
    try:
        nombre = float(valeur)
    except ValueError:
        raise argparse.ArgumentTypeError(f"nombre attendu (reçu {valeur!r})") from None
    if not 0 <= nombre <= 1:
        raise argparse.ArgumentTypeError("nombre dans [0, 1] attendu")
    return nombre


def _taches_jugees(valeur: str) -> list[str]:
    from slmsp.data.juge_donnees import TACHES_JUGEES

    taches = [t.strip() for t in valeur.split(",") if t.strip()]
    if not taches or any(t not in TACHES_JUGEES for t in taches):
        raise argparse.ArgumentTypeError(
            f"Tâches attendues parmi {', '.join(TACHES_JUGEES)} : {valeur!r}"
        )
    return taches


def _euros(valeur: str) -> float:
    try:
        nombre = float(valeur)
    except ValueError:
        raise argparse.ArgumentTypeError(f"nombre attendu (reçu {valeur!r})") from None
    if not nombre > 0 or nombre == float("inf"):
        raise argparse.ArgumentTypeError("montant strictement positif attendu")
    return nombre


def _euros_ou_zero(valeur: str) -> float:
    try:
        nombre = float(valeur)
    except ValueError:
        raise argparse.ArgumentTypeError(f"nombre attendu (reçu {valeur!r})") from None
    if not 0 <= nombre < float("inf"):
        raise argparse.ArgumentTypeError("montant positif ou nul attendu")
    return nombre


def _essais(valeur: str) -> int:
    nombre = _entier_positif(valeur)
    if nombre > 3:
        raise argparse.ArgumentTypeError("entier de 1 à 3 attendu")
    return nombre


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `data` et ses actions."""
    parseur = sous_parseurs.add_parser(
        "data",
        help="pipeline des Données d'entraînement",
        description="Pipeline des Données : seed, generate, validate, filter, build.",
    )
    actions = parseur.add_subparsers(dest="action", metavar="<action>", required=True)

    p = actions.add_parser(
        "seed",
        help="constituer les amorces (jeux publics, scénarios Mistral) hors fuite",
        description="Étape seed : amorces publiques ou Mistral, exclusion anti-fuite.",
    )
    p.add_argument(
        "--racine",
        type=Path,
        default=None,
        help="racine de data/, eval/ et runs/ (défaut : racine du projet)",
    )
    p.add_argument(
        "--facteur",
        type=_entier_positif,
        default=FACTEUR_DEFAUT,
        metavar="N",
        help=f"amorces conservées par exemple visé (défaut : {FACTEUR_DEFAUT})",
    )
    p.add_argument(
        "--scenarios",
        type=_entier_positif_ou_nul,
        default=0,
        metavar="N",
        help="scénarios de réunion à faire écrire par Mistral (défaut : 0, aucun appel d'API)",
    )
    p.add_argument(
        "--courriers",
        type=_courriers,
        default=0,
        metavar="{N,auto}",
        help="appels Mistral pour les amorces de courrier type CT (auto : volume CT x "
        "facteur ; défaut : 0, aucun appel d'API)",
    )
    p.add_argument(
        "--taches",
        type=_liste_taches,
        default=None,
        metavar="T1,T2",
        help="seed partiel (avec --completer-depuis) : ne tirer que ces Tâches",
    )
    p.add_argument(
        "--completer-depuis",
        default=None,
        metavar="SEED_RUN_ID",
        help="avec --taches : recopier à l'identique les amorces des autres Tâches de ce seed",
    )
    p.set_defaults(func=_seed)

    c = actions.add_parser(
        "conditions",
        help="vérifier les conditions commerciales de Mistral (préalable D1.2)",
        description="GET de la page des conditions, SHA-256 ; identique : date du jour inscrite.",
    )
    c.add_argument("verbe", choices=["verifier"], help="verifier : relire la page des conditions")
    c.add_argument(
        "--verifier-seulement",
        action="store_true",
        help="ne rien écrire dans config/donnees.toml (compare seulement le SHA)",
    )
    c.set_defaults(func=_conditions)

    g = actions.add_parser(
        "generate",
        help="générer les exemples par Mistral (idempotent, traces d'outils enregistrées)",
        description="Étape generate : génération idempotente et traces d'outils.",
    )
    origine = g.add_mutually_exclusive_group(required=True)
    origine.add_argument("--depuis", metavar="SEED_RUN_ID", help="run data-seed à générer")
    origine.add_argument("--reprendre", metavar="RUN_ID", help="run data-generate à reprendre")
    g.add_argument(
        "--racine",
        type=Path,
        default=None,
        help="racine de data/, eval/ et runs/ (défaut : racine du projet)",
    )
    g.add_argument(
        "--surplus",
        type=_fraction,
        default=0.0,
        metavar="X",
        help="part de sessions planifiées en plus des volumes, dans [0, 1] (défaut : 0)",
    )
    g.add_argument(
        "--modele-generateur",
        default=None,
        metavar="MODELE",
        help="modèle Mistral du Générateur (défaut : modele_generateur de config/mistral.toml)",
    )
    g.add_argument(
        "--taches",
        type=_liste_taches,
        default=None,
        metavar="T1,T2",
        help="Tâches à générer, séparées par des virgules (nouveau run ; défaut : toutes)",
    )
    g.add_argument(
        "--completer-depuis",
        default=None,
        metavar="GENERATE_RUN_ID",
        help="avec --taches : reprendre sans appel les autres Tâches de ce run du même seed "
        "(ou d'un seed dont le seed courant recopie les amorces, seed partiel)",
    )
    g.add_argument(
        "--verifiee",
        action="store_true",
        help="génération vérifiée CR, LC, CT : contrôles déterministes puis juge de données "
        "(story O6a), régénération des cibles refusées (story O6b) puis écart",
    )
    g.add_argument(
        "--sans-juge",
        action="store_true",
        help="avec --verifiee : contrôles déterministes seuls, aucun appel OpenRouter (calibrage)",
    )
    g.add_argument(
        "--essais-max",
        type=_essais,
        default=None,
        metavar="N",
        help="avec --verifiee : essais par session, de 1 à 3 (défaut : [verification] "
        "essais_max) ; au-delà de 1, régénération des cibles refusées (story O6b)",
    )
    g.add_argument(
        "--plafond-estime-mistral",
        type=_euros_ou_zero,
        default=None,
        metavar="EUR",
        help="refuser le lancement si le coût Mistral pire cas estimé dépasse ce montant "
        "(0 : aucun appel Mistral nouveau admis)",
    )
    g.add_argument(
        "--plafond-estime-openrouter",
        type=_euros_ou_zero,
        default=None,
        metavar="EUR",
        help="avec --verifiee : refuser le lancement si le coût pire cas du juge le dépasse",
    )
    g.set_defaults(func=_generate)

    v = actions.add_parser(
        "validate",
        help="valider les exemples contre leurs sources et le Bac à sable",
        description="Étape validate : rejeu des traces, URL et valeurs, fidélité.",
    )
    v.add_argument("--depuis", required=True, metavar="GENERATE_RUN_ID", help="run data-generate")
    v.add_argument("--racine", type=Path, default=None, help="racine de data/, eval/ et runs/")
    v.add_argument(
        "--controle-mistral",
        action="store_true",
        help="contrôle de fidélité CR, LC, RE par Mistral (appels payants, usage validation)",
    )
    v.set_defaults(func=_validate)

    f = actions.add_parser(
        "filter",
        help="retirer doublons et fuites du Jeu d'évaluation",
        description="Étape filter : doublons, anti-fuite par n-grammes et cosinus BGE-M3.",
    )
    f.add_argument("--depuis", required=True, metavar="VALIDATE_RUN_ID", help="run data-validate")
    f.add_argument("--racine", type=Path, default=None, help="racine de data/, eval/ et runs/")
    f.set_defaults(func=_filter)

    j = actions.add_parser(
        "juger",
        help="noter les cibles candidates par le juge de données DeepSeek (OpenRouter)",
        description="Juge de données (story O1) : notes, extraits vérifiés, verdict par seuils.",
    )
    origine_j = j.add_mutually_exclusive_group(required=True)
    origine_j.add_argument("--depuis", metavar="GENERATE_RUN_ID", help="run data-generate")
    origine_j.add_argument("--reprendre", metavar="RUN_ID", help="run data-juger à reprendre")
    j.add_argument(
        "--taches",
        type=_taches_jugees,
        default=None,
        metavar="CR,LC,CT",
        help="Tâches jugées (défaut : CR, LC, CT)",
    )
    j.add_argument(
        "--limite",
        type=_entier_positif,
        default=None,
        metavar="N",
        help="au plus N candidats par Tâche (calibrage)",
    )
    j.add_argument(
        "--plafond-estime",
        type=_euros,
        default=None,
        metavar="EUR",
        help="refus avant tout appel si le coût pire cas estimé dépasse ce montant",
    )
    j.add_argument("--racine", type=Path, default=None, help="racine de data/, eval/ et runs/")
    j.set_defaults(func=_juger)

    b = actions.add_parser(
        "build",
        help="construire le jeu d'entraînement versionné (re-dérivation du journal)",
        description="Étape build : re-dérivation octet par octet, data/train/vN, MANIFEST.",
    )
    b.add_argument(
        "--depuis",
        required=True,
        metavar="RUN_ID",
        help="run data-filter ; avec --preferences, --nettoyage ou --sous-ensemble, "
        "run data-build du jeu SFT",
    )
    b.add_argument(
        "--variante",
        choices=["diffusable", "recherche"],
        help="diffusable : sources diffusables seules ; recherche : jeu marqué recherche "
        "(requis sans --preferences ni --nettoyage)",
    )
    b.add_argument(
        "--preferences",
        action="store_true",
        help="construire les paires ORPO (chosen : exemple SFT ; rejected : Modèle de base local)",
    )
    b.add_argument(
        "--nettoyage",
        action="store_true",
        help="nettoyer le jeu SFT : préambule « Voici » retiré, cibles trop longues écartées",
    )
    b.add_argument(
        "--sous-ensemble",
        action="store_true",
        help="restreindre le jeu SFT aux Tâches de --taches (lignes copiées à l'identique)",
    )
    b.add_argument(
        "--taches",
        metavar="T1,T2,...",
        help="Tâches gardées par --sous-ensemble (séparées par des virgules, ex. Q,RD,generique)",
    )
    b.add_argument(
        "--modele",
        metavar="base:SLUG",
        help="Modèle de base local (--preferences) ou tokenizer (--nettoyage)",
    )
    b.add_argument("--llama", choices=["cpu", "cuda"], default="cpu", help="variante llama.cpp")
    b.add_argument("--racine", type=Path, default=None, help="racine de data/, eval/ et runs/")
    b.set_defaults(func=_build)


# --- Lecture parquet et jeux -------------------------------------------------------------


def _decodeur_pyarrow() -> Decodeur:
    """Décodeur parquet (pyarrow) : `ParquetFile(BytesIO).iter_batches`, colonnes demandées.

    Lève `ConfigurationInvalide` si l'extra `data` n'est pas installé.
    """
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        raise ConfigurationInvalide(
            "pyarrow introuvable : installer l'extra `data` (uv sync --extra data)"
        ) from None

    def decoder(octets: bytes, colonnes: Sequence[str]) -> Iterator[Mapping[str, Any]]:
        try:
            fichier = pq.ParquetFile(io.BytesIO(octets))
            for lot in fichier.iter_batches(batch_size=TAILLE_LOT, columns=list(colonnes)):
                yield from lot.to_pylist()
        except (pa.ArrowException, KeyError) as exc:
            raise ConfigurationInvalide(
                f"parquet illisible ou colonne absente parmi {', '.join(colonnes)} "
                f"({type(exc).__name__})"
            ) from None

    return decoder


def _jeux_publics(config: ConfigSources, racine: Path) -> list[JeuPublic]:
    """Jeux de `config/sources.toml` convertis, fichiers sous `data/raw/mediatech/`."""
    return [
        JeuPublic(
            nom=jeu.nom,
            depot=jeu.depot,
            revision=jeu.revision,
            fichiers=tuple(
                FichierJeu(dossier_jeu(racine, jeu) / Path(fichier.chemin).name, fichier.sha256)
                for fichier in jeu.fichiers
            ),
        )
        for jeu in config.jeux
    ]


# --- Scénarios Mistral -------------------------------------------------------------------


def _fabrique_depuis(creer_generateur: Callable[[str], Any]) -> FabriqueScenario:
    """Fabrique de scénarios : `Generateur(seed_run_id).generer("scenario-reunion", [thème])`.

    Le texte de l'amorce est le contenu du message `assistant` de la réponse brute
    journalisée, celui que `Generateur` revérifie ensuite. Une réponse tronquée lève
    `ReponseTronquee` : `seed` écarte alors le scénario et le compte.
    """
    from slmsp.mistral.generateur import FINS_TRONQUEES, message_assistant, raison_de_fin

    def fabrique(seed_run_id: str, theme_id: str, session_id: str) -> tuple[str, str]:
        generation = creer_generateur(seed_run_id).generer(
            GABARIT_SCENARIO, [theme_id], session_id, "CR"
        )
        if raison_de_fin(generation.reponse_brute) in FINS_TRONQUEES:
            raise ReponseTronquee(f"appel {generation.appel_id} : réponse tronquée (length)")
        contenu = message_assistant(generation.reponse_brute).get("content")
        if not isinstance(contenu, str) or not contenu:
            raise ProvenanceInvalide(f"appel {generation.appel_id} : réponse sans contenu texte")
        return generation.appel_id, contenu

    return fabrique


def _fabrique_courriers_depuis(creer_generateur: Callable[[str], Any]) -> FabriqueCourrier:
    """Fabrique des amorces CT : réponse déjà journalisée pour la session (reprise sans
    appel), sinon `Generateur(seed_run_id).generer("amorces-ct", [sujet])`. Renvoie le contenu
    du message `assistant`, objet JSON que `slmsp.data.seed` découpe et vérifie (chaîne vide si
    la réponse n'a pas de texte : `seed` la compte en `schema_invalide` et poursuit). Une
    réponse tronquée, même déjà journalisée, lève `ReponseTronquee` : `seed` la compte en
    `tronques`."""
    from slmsp.mistral.generateur import FINS_TRONQUEES, message_assistant, raison_de_fin

    def fabrique(seed_run_id: str, sujet_id: str, session_id: str) -> tuple[str, str]:
        generateur = creer_generateur(seed_run_id)
        ligne = generateur.reponse_journalisee(GABARIT_AMORCES_CT, [sujet_id], session_id, "CT")
        if ligne is not None:
            appel_id, brut = ligne.appel_id, ligne.reponse_brute
        else:
            generation = generateur.generer(GABARIT_AMORCES_CT, [sujet_id], session_id, "CT")
            appel_id, brut = generation.appel_id, generation.reponse_brute
        if raison_de_fin(brut) in FINS_TRONQUEES:
            raise ReponseTronquee(f"appel {appel_id} : réponse tronquée (length)")
        try:
            contenu = message_assistant(brut).get("content")
        except ProvenanceInvalide:
            contenu = None  # réponse vide ou illisible : comptée en schéma invalide par seed
        return appel_id, contenu if isinstance(contenu, str) else ""

    return fabrique


def _createur_generateur(racine: Path) -> Callable[[str], Any]:
    """`seed_run_id -> Generateur` réel (appels Mistral payants) ; préalables D1.2 vérifiés
    dès maintenant."""
    from slmsp.budget.registre import RegistreBudget
    from slmsp.mistral.client import ClientMistral, fabriquer_sdk
    from slmsp.mistral.config import charger_mistral
    from slmsp.mistral.generateur import Generateur, charger_prealables

    config = charger_mistral()
    dossier = racine_projet() / "config"
    fichier_donnees = dossier / "donnees.toml"
    charger_prealables(fichier_donnees, modele=config.modele, aujourd_hui=date.today())
    client = ClientMistral(config, RegistreBudget(), fabriquer_sdk(config))

    def creer(seed_run_id: str) -> Generateur:
        return Generateur(
            seed_run_id,
            client=client,
            racine=racine,
            fichier_donnees=fichier_donnees,
            dossier_gabarits=dossier / "prompts" / "generateur",
        )

    return creer


def _fabrique_scenarios(racine: Path) -> FabriqueScenario:
    """Fabrique réelle de scénarios (appels Mistral payants)."""
    return _fabrique_depuis(_createur_generateur(racine))


def _fabrique_courriers(racine: Path) -> FabriqueCourrier:
    """Fabrique réelle des amorces CT (appels Mistral payants, reprise par le journal)."""
    return _fabrique_courriers_depuis(_createur_generateur(racine))


# --- seed --------------------------------------------------------------------------------


def _racine(args: argparse.Namespace) -> Path:
    return (args.racine if args.racine is not None else racine_projet()).resolve()


def _consigner(message: str) -> None:
    print(message, flush=True)


def _seed(args: argparse.Namespace) -> int:
    racine = _racine(args)
    if (args.taches is None) != (args.completer_depuis is None):
        print("slmsp : --taches et --completer-depuis vont ensemble", file=sys.stderr)
        return int(CodeSortie.ERREUR)
    decodeur = _decodeur_pyarrow()
    config_sources = charger_config_sources()
    config = charger_config_donnees()
    registre = RegistreLicences.charger(racine=racine)
    fabrique = fabrique_ct = None
    courriers = (
        config.volumes.CT * args.facteur if args.courriers == "auto" else int(args.courriers)
    )
    if args.scenarios > 0 or courriers > 0:
        from slmsp.evaluation.gel import jeu_gele_et_commite

        jeu_gele_et_commite("v1.1", racine)  # ManifesteInvalide (code 4) avant toute génération
    if args.scenarios > 0:
        fabrique = _fabrique_scenarios(racine)
    if courriers > 0:
        fabrique_ct = _fabrique_courriers(racine)
    protection = construire_protection(versions_protegees(racine), config, racine)
    try:
        resultat = executer_seed(
            racine=racine,
            jeux=_jeux_publics(config_sources, racine),
            registre=registre,
            config=config,
            protection=protection,
            decodeur=decodeur,
            facteur=args.facteur,
            nb_scenarios=args.scenarios,
            fabrique_scenarios=fabrique,
            nb_courriers=courriers,
            fabrique_courriers=fabrique_ct,
            consigner=_consigner,
            taches=args.taches,
            completer_depuis=args.completer_depuis,
        )
    except ProvenanceInvalide as exc:
        print(f"slmsp : {exc}", file=sys.stderr)
        return int(CodeSortie.MANIFESTE_INVALIDE)
    for tache, emplacements in resultat.comptes["taches"].items():
        for emplacement, compte in emplacements.items():
            print(
                f"{tache}/{emplacement} : {compte['conservees']}/{compte['cible']} amorces "
                f"({compte['exclus']} exclues par l'anti-fuite)"
            )
    scenarios = resultat.comptes["scenarios"]
    if scenarios["demandes"]:
        print(
            f"scénarios : {scenarios['produits']}/{scenarios['demandes']} "
            f"({scenarios['tronques']} tronqué(s) écarté(s))"
        )
    bilan_ct = resultat.comptes["courriers"]
    if bilan_ct["demandes"]:
        print(
            f"amorces CT : {bilan_ct['produits']} courrier(s) sur {bilan_ct['appels']} appel(s) "
            f"(schéma invalide {bilan_ct['schema_invalide']}, tronqués {bilan_ct['tronques']}, "
            f"doublons {bilan_ct['doublons']}, "
            f"anti-fuite {bilan_ct['exclus']})"
        )
    print(f"run {resultat.run_id} ({resultat.statut}) : {resultat.dossier}")
    if resultat.statut == "partiel-budget":
        return int(CodeSortie.BUDGET_EPUISE)
    return int(CodeSortie.SUCCES if resultat.statut == "complet" else CodeSortie.ERREUR)


# --- generate ----------------------------------------------------------------------------


class _RechercheParesseuse:
    """Recherche dans l'Index local : BGE-M3 et Index ouverts à la première recherche."""

    def __init__(self, racine: Path) -> None:
        self.racine = racine
        self._pile = ExitStack()
        self._recherche: Any = None
        self._version: str | None = None

    def _ouvrir(self) -> Any:
        if self._recherche is None:
            from slmsp.harness.recherche_index import depuis_config
            from slmsp.index.lecture import ouvrir_index
            from slmsp.inference.serveur import (
                ServeurLlama,
                charger_config_llamacpp,
                charger_config_modele,
            )

            serveur = self._pile.enter_context(
                ServeurLlama(
                    charger_config_modele("bge-m3"),
                    "cpu",
                    slug="bge-m3",
                    config_llamacpp=charger_config_llamacpp(),
                    prendre_verrou_gpu=False,
                    # Texte de groupe concaténé : troncature d'avant F1 (8176 tokens), pour que
                    # les passages retenus restent ceux des sessions déjà générées.
                    usage="texte_long",
                )
            )
            index = self._pile.enter_context(ouvrir_index(self.racine))
            self._recherche = depuis_config(serveur.embedder(), index)
            self._version = index.version
        return self._recherche

    @property
    def version(self) -> str:
        self._ouvrir()
        return str(self._version)

    def rechercher(self, requete: str) -> Any:
        return self._ouvrir().rechercher(requete)

    def fermer(self) -> None:
        self._pile.close()


def _conditions_perimees(fichier: Path) -> bool:
    import tomllib

    try:
        valeur = tomllib.loads(fichier.read_text(encoding="utf-8"))["mistral"][
            "conditions_verifiees_le"
        ]
    except KeyError:
        return False  # charger_prealables signalera la clé absente
    except (OSError, tomllib.TOMLDecodeError) as exc:
        from slmsp.mistral.conditions import ConditionsAVerifier

        raise ConditionsAVerifier(
            f"{fichier} illisible ({type(exc).__name__}) : génération bloquée"
        ) from None
    return valeur != date.today()


def _verifier_conditions(*, ecrire: bool = True) -> Any:
    from slmsp import net
    from slmsp.core.var import dossier_var
    from slmsp.mistral.conditions import verifier_conditions

    racine = racine_projet()
    resultat = verifier_conditions(
        racine / "config" / "donnees.toml",
        fabrique_client=lambda: net.client("outillage"),
        aujourd_hui=date.today(),
        ecrire=ecrire,
        journal=dossier_var() / "mistral-conditions.jsonl",
    )
    suite = "date du jour inscrite" if resultat.ecrit else "rien écrit"
    _consigner(f"conditions Mistral inchangées (SHA {resultat.sha_obtenu[:12]}…) : {suite}")
    return resultat


def _conditions(args: argparse.Namespace) -> int:
    _verifier_conditions(ecrire=not args.verifier_seulement)
    return 0


def _generate(args: argparse.Namespace) -> int:
    from slmsp.budget.registre import RegistreBudget
    from slmsp.core.items import identifiants_proteges
    from slmsp.data.generate import lancer_generation, modele_generateur_du_run, seed_du_run
    from slmsp.data.sessions import ResolveurPassages
    from slmsp.evaluation.gel import jeu_gele_et_commite
    from slmsp.mcp.direct import McpEnDirect
    from slmsp.mistral.client import ClientMistral, fabriquer_sdk
    from slmsp.mistral.config import charger_mistral
    from slmsp.mistral.generateur import Generateur, charger_prealables

    racine = _racine(args)
    gel = jeu_gele_et_commite("v1.0", racine)  # ManifesteInvalide (code 4) avant tout
    seed_run_id = args.depuis or seed_du_run(args.reprendre, racine=racine)
    if args.reprendre and (args.taches or args.completer_depuis):
        raise ConfigurationInvalide("--taches et --completer-depuis : nouveau run seulement")
    if args.completer_depuis and not args.taches:
        raise ConfigurationInvalide("--completer-depuis exige --taches")
    verifiee, sans_juge, essais_max = args.verifiee, args.sans_juge, args.essais_max
    if args.reprendre:
        from slmsp.core.artefacts import ouvrir_run

        if verifiee or sans_juge or essais_max is not None:
            raise ConfigurationInvalide(
                "--verifiee, --sans-juge et --essais-max : nouveau run seulement (relus du run)"
            )
        reglages = ouvrir_run(args.reprendre, racine=racine).manifeste.config.get("verification")
        if reglages is not None:
            verifiee, sans_juge = True, bool(reglages.get("sans_juge"))
            essais_max = reglages.get("essais_max")
    if not verifiee and (
        sans_juge or essais_max is not None or args.plafond_estime_openrouter is not None
    ):
        raise ConfigurationInvalide(
            "--sans-juge, --essais-max et --plafond-estime-openrouter exigent --verifiee"
        )
    modele = args.modele_generateur
    if modele is None and args.reprendre:
        modele = modele_generateur_du_run(args.reprendre, racine=racine)
    try:
        config_mistral = charger_mistral().pour_generateur(modele)
    except ValueError as exc:
        raise ConfigurationInvalide(f"config/mistral.toml : {exc}") from None
    preversion = config_mistral.preversion
    dossier = racine_projet() / "config"
    fichier_donnees = dossier / "donnees.toml"
    # Date des conditions périmée : vérification automatique (C9) ; bloque si la page a changé.
    if _conditions_perimees(fichier_donnees):
        _consigner("conditions Mistral non vérifiées aujourd'hui : vérification automatique")
        _verifier_conditions()
    # Préalables D1.2 (code 1) avant d'ouvrir le registre de budget ou le journal.
    charger_prealables(
        fichier_donnees,
        modele=config_mistral.modele,
        aujourd_hui=date.today(),
        preversions=() if preversion is None else (preversion,),
    )
    if preversion is not None:
        _consigner(f"Générateur sur la préversion {preversion} (MANIFEST : generateur_preversion)")
    config = charger_config_donnees()
    proteges = identifiants_proteges(versions_protegees(racine), racine=racine)
    passages = ResolveurPassages()
    client = ClientMistral(config_mistral, RegistreBudget(), fabriquer_sdk(config_mistral))
    generateur = Generateur(
        seed_run_id,
        client=client,
        racine=racine,
        fichier_donnees=fichier_donnees,
        dossier_gabarits=dossier / "prompts" / "generateur",
        fichier_outils=dossier / "outils-mcp.toml",
        rendre_passages=passages,
    )
    verificateur = (
        _verificateur(racine, config, sans_juge, essais_max, args.plafond_estime_openrouter)
        if verifiee
        else None
    )
    recherche = _RechercheParesseuse(racine)
    try:
        resultat = lancer_generation(
            racine=racine,
            volumes=config.volumes.par_tache(),
            generateur=generateur,
            passages=passages,
            ouvrir_outils=lambda: McpEnDirect("outillage"),
            proteges=proteges,
            seed_run_id=args.depuis,
            reprendre_run_id=args.reprendre,
            recherche=recherche,
            commit_gel=gel.commit_gel,
            surplus=args.surplus,
            chemin_outils=dossier / "outils-mcp.toml",
            consigner=_consigner,
            taches=args.taches,
            completer_depuis=args.completer_depuis,
            verificateur=verificateur,
            plafond_estime_mistral=args.plafond_estime_mistral,
        )
    finally:
        recherche.fermer()
    return _afficher_generation(resultat)


def _verificateur(
    racine: Path,
    config: Any,
    sans_juge: bool,
    essais_max: int | None,
    plafond_openrouter: float | None,
) -> Any:
    """Vérificateur O6a : contrôles déterministes, et juge de données sauf `sans_juge`."""
    from slmsp.data.generation_verifiee import Verificateur
    from slmsp.data.verification import TACHES_VERIFIEES

    juge = None
    if not sans_juge:
        from slmsp.budget.registre import RegistreBudget
        from slmsp.core.var import dossier_var
        from slmsp.data.juge_donnees import (
            JugeDonnees,
            charger_grilles,
            config_openrouter,
            indexer_cache,
        )
        from slmsp.fournisseurs.client import ClientCompatibleOpenAI, fabriquer_http, lire_cle
        from slmsp.fournisseurs.journal import NOM_JOURNAL_JUGE_DONNEES, JournalAppels

        fournisseur = config_openrouter(config.juge_donnees)
        client = ClientCompatibleOpenAI(
            fournisseur,
            RegistreBudget(),
            fabriquer_http(fournisseur),
            lire_cle(fournisseur),
            journal=JournalAppels(dossier_var() / NOM_JOURNAL_JUGE_DONNEES),
        )
        juge = JugeDonnees(
            config.juge_donnees,
            client,
            charger_grilles(TACHES_VERIFIEES),
            indexer_cache(racine),
        )
    try:
        return Verificateur(
            config.verification,
            plafonds_mots=config.generateur.plafonds_mots,
            juge=juge,
            essais_max=essais_max,
            plafond_estime_openrouter=plafond_openrouter,
        )
    except ValueError as exc:
        raise ConfigurationInvalide(f"--essais-max : {exc}") from None


def _afficher_generation(resultat: Any) -> int:
    for tache, ligne in resultat.bilan["taches"].items():
        abandons = sum(ligne["abandons"].values())
        print(
            f"{tache} : {ligne['completes']} complètes, {abandons} abandons, "
            f"{ligne['incidents']} incidents / {ligne['planifiees']} planifiées "
            f"({ligne['appels_nouveaux']} appels, {ligne['appels_reutilises']} réutilisés)"
        )
    print(f"dépense de cette invocation : {resultat.bilan['cout_eur']:.4f} €")
    rapport = resultat.run.dossier / "rapport.json"
    if rapport.is_file():
        import json

        verification = json.loads(rapport.read_bytes())
        for tache, bloc in verification["taches"].items():
            codes = ", ".join(f"{c} {n}" for c, n in bloc["codes_bloquants"].items())
            print(
                f"vérification {tache} : {bloc['verifiees'] - bloc['ecartees']}/"
                f"{bloc['verifiees']} retenues, {bloc['ecartees']} écartées "
                f"(tests {bloc['refus_tests']}, juge {bloc['refus_juge']}) ; "
                f"{codes or 'aucun refus'}"
            )
        print(f"juge de données : {verification['cout_openrouter_eur']:.4f} €")
    print(f"run {resultat.run.run_id} ({resultat.statut}) : {resultat.run.dossier}")
    if resultat.statut == "partiel-budget":
        return int(CodeSortie.BUDGET_EPUISE)
    return int(CodeSortie.SUCCES if resultat.statut == "complet" else CodeSortie.ERREUR)


# --- validate et filter ------------------------------------------------------------------


def _journal_lecture() -> Any:
    from slmsp.core.var import dossier_var
    from slmsp.mistral.config import charger_mistral
    from slmsp.mistral.journal import USAGE_GENERATION, journal_pour

    return journal_pour(USAGE_GENERATION, charger_mistral(), dossier_var(), lecteur="data")


def _afficher_rapport(rapport: Mapping[str, Any], run_id: str, statut: str, dossier: Path) -> int:
    for tache, ligne in rapport["taches"].items():
        motifs = ", ".join(f"{m} {n}" for m, n in ligne["rejets"].items()) or "aucun rejet"
        print(
            f"{tache} : {ligne['retenus']}/{ligne['exemples']} retenus, "
            f"taux de rejet {ligne['taux_rejet']:.1%} ({motifs})"
        )
    for tache, comptes in rapport.get("observations", {}).items():
        print(f"{tache} : observations {', '.join(f'{o} {n}' for o, n in comptes.items())}")
    print(f"run {run_id} ({statut}) : {dossier}")
    if statut == "partiel-budget":
        return int(CodeSortie.BUDGET_EPUISE)
    return int(CodeSortie.SUCCES if statut == "complet" else CodeSortie.ERREUR)


def _validate(args: argparse.Namespace) -> int:
    from slmsp.data.validate import ControleMistral, lancer_validation

    racine = _racine(args)
    journal = _journal_lecture()
    controle = None
    if args.controle_mistral:
        from slmsp.budget.registre import RegistreBudget
        from slmsp.mistral.client import ClientMistral, fabriquer_sdk
        from slmsp.mistral.config import charger_mistral
        from slmsp.mistral.generateur import charger_prealables

        config_mistral = charger_mistral()
        dossier = racine_projet() / "config"
        # Préalables D1.2 (code 1) avant d'ouvrir le registre de budget.
        charger_prealables(
            dossier / "donnees.toml", modele=config_mistral.modele, aujourd_hui=date.today()
        )
        client = ClientMistral(config_mistral, RegistreBudget(), fabriquer_sdk(config_mistral))
        controle = ControleMistral(
            client, journal, dossier_gabarits=dossier / "prompts" / "generateur"
        )
    resultat = lancer_validation(
        racine=racine,
        generate_run_id=args.depuis,
        journal=journal,
        controle=controle,
        chemin_outils=racine_projet() / "config" / "outils-mcp.toml",
        consigner=_consigner,
    )
    return _afficher_rapport(
        resultat.rapport, resultat.run.run_id, resultat.statut, resultat.run.dossier
    )


def _juger(args: argparse.Namespace) -> int:
    from slmsp.budget.registre import RegistreBudget
    from slmsp.core.var import dossier_var
    from slmsp.data.juge_donnees import (
        TACHES_JUGEES,
        JugeDonnees,
        candidats_depuis_generation,
        charger_grilles,
        config_du_run,
        config_openrouter,
        indexer_cache,
        lancer_jugement,
    )
    from slmsp.data.validate import LecteurGeneration, ouvrir_generation
    from slmsp.fournisseurs.client import ClientCompatibleOpenAI, fabriquer_http, lire_cle
    from slmsp.fournisseurs.journal import NOM_JOURNAL_JUGE_DONNEES, JournalAppels

    racine = _racine(args)
    depuis, taches, limite = args.depuis, args.taches, args.limite
    if args.reprendre is not None:
        config_run = config_du_run(args.reprendre, racine)
        depuis = config_run["depuis"]
        taches = taches or config_run.get("taches")
        limite = limite if limite is not None else config_run.get("limite")
    taches = list(taches or TACHES_JUGEES)
    config = charger_config_donnees().juge_donnees
    lecteur = LecteurGeneration(ouvrir_generation(depuis, racine), _journal_lecture(), racine)
    candidats, ecartees = candidats_depuis_generation(lecteur, taches)
    if ecartees:
        print(f"{ecartees} session(s) écartée(s) : source ou réponse introuvable")
    fournisseur = config_openrouter(config)
    client = ClientCompatibleOpenAI(
        fournisseur,
        RegistreBudget(),
        fabriquer_http(fournisseur),
        lire_cle(fournisseur),
        journal=JournalAppels(dossier_var() / NOM_JOURNAL_JUGE_DONNEES),
    )
    juge = JugeDonnees(config, client, charger_grilles(taches), indexer_cache(racine))
    resultat = lancer_jugement(
        racine=racine,
        juge=juge,
        candidats=candidats,
        depuis_run_id=depuis,
        taches=taches,
        limite=limite,
        plafond_estime_eur=args.plafond_estime,
        reprendre_run_id=args.reprendre,
        consigner=_consigner,
    )
    rapport = resultat.rapport
    for tache, ligne in rapport["taches"].items():
        criteres = ", ".join(f"{c} {t:.0%}" for c, t in ligne["taux_par_critere"].items())
        print(
            f"{tache} : {ligne['acceptes']}/{ligne['juges']} acceptés "
            f"({ligne['taux_acceptation']:.0%}), {ligne['invalides']} invalide(s), "
            f"{ligne['extraits_invalides']} extrait(s) invalide(s) ; {criteres}"
        )
    print(f"coût {rapport['cout_invocation_eur']:.4f} € (invocation)")
    print(f"run {resultat.run.run_id} ({resultat.statut}) : {resultat.run.dossier}")
    if resultat.statut == "partiel-budget":
        return int(CodeSortie.BUDGET_EPUISE)
    return int(CodeSortie.SUCCES if resultat.statut == "complet" else CodeSortie.ERREUR)


def _filter(args: argparse.Namespace) -> int:
    from slmsp.core.items import vecteurs_antifuite
    from slmsp.data.filter import lancer_filtre
    from slmsp.inference.serveur import (
        ServeurLlama,
        charger_config_llamacpp,
        charger_config_modele,
    )

    racine = _racine(args)
    config = charger_config_donnees()
    versions = versions_protegees(racine)
    protection = construire_protection(versions, config, racine)
    with ServeurLlama(
        charger_config_modele("bge-m3"),
        "cpu",
        slug="bge-m3",
        config_llamacpp=charger_config_llamacpp(),
        prendre_verrou_gpu=False,
        usage="texte_long",
    ) as serveur:
        embedder = serveur.embedder()
        resultat = lancer_filtre(
            racine=racine,
            validate_run_id=args.depuis,
            journal=_journal_lecture(),
            protection=protection,
            vecteurs=vecteurs_antifuite(versions, embedder, racine=racine),
            embedder=embedder,
            config=config,
            consigner=_consigner,
        )
    return _afficher_rapport(
        resultat.rapport, resultat.run.run_id, resultat.statut, resultat.run.dossier
    )


# --- build -------------------------------------------------------------------------------


def _preferences(args: argparse.Namespace, racine: Path) -> int:
    from slmsp.cli._assemblage import ModeleInvalide, slug_modele
    from slmsp.data.preferences import lancer_preferences
    from slmsp.inference.serveur import ServeurLlama, charger_config_modele

    if not args.modele or args.variante:
        print(
            "slmsp : --preferences exige --modele base:<slug> et exclut --variante", file=sys.stderr
        )
        return int(CodeSortie.USAGE)
    try:
        slug = slug_modele(args.modele)
    except ModeleInvalide as exc:
        print(f"slmsp : {exc}", file=sys.stderr)
        return int(CodeSortie.USAGE)
    config = charger_config_donnees()
    with ServeurLlama(charger_config_modele(slug), args.llama, slug=slug) as serveur:  # type: ignore[arg-type]
        resultat = lancer_preferences(
            racine=racine,
            build_run_id=args.depuis,
            modele=args.modele,
            llm=serveur.client(),
            config=config.preferences,
            consigner=_consigner,
        )
    for tache, nombre in resultat.rapport["comptes_par_tache"].items():
        print(f"{tache} : {nombre} paires")
    motifs = ", ".join(f"{m} {n}" for m, n in resultat.rapport["ecartees_par_motif"].items())
    print(f"écartées : {motifs or 'aucune'}")
    print(f"paires {resultat.version} : {resultat.dossier}")
    print(f"run {resultat.run.run_id} (complet) : {resultat.run.dossier}")
    return int(CodeSortie.SUCCES)


def _nettoyage(args: argparse.Namespace, racine: Path) -> int:
    from slmsp.cli._assemblage import ModeleInvalide, slug_modele
    from slmsp.data.nettoyage import lancer_nettoyage
    from slmsp.evaluation.config import charger_evaluation

    if not args.modele or args.variante or args.preferences:
        print(
            "slmsp : --nettoyage exige --modele base:<slug> et exclut --variante et --preferences",
            file=sys.stderr,
        )
        return int(CodeSortie.USAGE)
    try:
        slug_modele(args.modele)
    except ModeleInvalide as exc:
        print(f"slmsp : {exc}", file=sys.stderr)
        return int(CodeSortie.USAGE)
    resultat = lancer_nettoyage(
        racine=racine,
        build_run_id=args.depuis,
        modele=args.modele,
        plafond_tokens=charger_evaluation().generation.max_tokens,
        consigner=_consigner,
    )
    rapport = resultat.rapport
    print(
        "Tâche : avant → après (préambules retirés, gardés, seuls ; écartés longueur ; LC signalés)"
    )
    for tache, c in rapport["par_tache"].items():
        print(
            f"{tache} : {c['avant']} → {c['apres']} ({c['preambules_retires']}, "
            f"{c['preambule_garde']}, {c['preambule_seul']} ; {c['ecartes_longueur']} ; "
            f"{c['lc_signales']})"
        )
    print(f"jeu {resultat.version} ({rapport['nb_lignes']} lignes) : {resultat.dossier}")
    print(f"run {resultat.run.run_id} (complet) : {resultat.run.dossier}")
    return int(CodeSortie.SUCCES)


def _sous_ensemble(args: argparse.Namespace, racine: Path) -> int:
    from slmsp.core.erreurs import ManifesteInvalide
    from slmsp.data.sous_ensemble import lancer_sous_ensemble

    taches = [t.strip() for t in (args.taches or "").split(",") if t.strip()]
    if not taches or args.modele or args.variante or args.preferences or args.nettoyage:
        print(
            "slmsp : --sous-ensemble exige --taches et exclut --modele, --variante, "
            "--preferences et --nettoyage",
            file=sys.stderr,
        )
        return int(CodeSortie.USAGE)
    try:
        resultat = lancer_sous_ensemble(
            racine=racine, build_run_id=args.depuis, taches=taches, consigner=_consigner
        )
    except ManifesteInvalide as exc:
        print(f"slmsp : {exc}", file=sys.stderr)
        return int(CodeSortie.USAGE)
    print("Tâche : avant → après")
    for tache, c in resultat.rapport["par_tache"].items():
        print(f"{tache} : {c['avant']} → {c['apres']}")
    print(f"jeu {resultat.version} ({resultat.rapport['nb_lignes']} lignes) : {resultat.dossier}")
    print(f"run {resultat.run.run_id} (complet) : {resultat.run.dossier}")
    return int(CodeSortie.SUCCES)


def _build(args: argparse.Namespace) -> int:
    from slmsp.data.build import lancer_build
    from slmsp.harness.taches import charger_taches

    racine = _racine(args)
    if args.sous_ensemble:
        return _sous_ensemble(args, racine)
    if args.taches is not None:
        print("slmsp : --taches exige --sous-ensemble", file=sys.stderr)
        return int(CodeSortie.USAGE)
    if args.nettoyage:
        return _nettoyage(args, racine)
    if args.preferences:
        return _preferences(args, racine)
    if not args.variante or args.modele:
        print(
            "slmsp : build exige --variante (et n'accepte --modele qu'avec --preferences)",
            file=sys.stderr,
        )
        return int(CodeSortie.USAGE)
    resultat = lancer_build(
        racine=racine,
        filter_run_id=args.depuis,
        variante=args.variante,
        journal=_journal_lecture(),
        registre=RegistreLicences.charger(racine=racine),
        config=charger_config_donnees(),
        taches=charger_taches(),
        chemin_outils=racine_projet() / "config" / "outils-mcp.toml",
        consigner=_consigner,
    )
    for tache, nombre in resultat.rapport["comptes_par_tache"].items():
        print(f"{tache} : {nombre} lignes")
    motifs = ", ".join(f"{m} {n}" for m, n in resultat.rapport["rejets_par_motif"].items())
    print(f"rejets en amont : {motifs or 'aucun'}")
    print(f"échantillon de relecture : {resultat.rapport['echantillon_relecture']} lignes")
    print(f"jeu {resultat.version} ({args.variante}) : {resultat.dossier}")
    print(f"run {resultat.run.run_id} ({resultat.statut}) : {resultat.run.dossier}")
    if resultat.statut == "partiel-budget":
        return int(CodeSortie.BUDGET_EPUISE)
    return int(CodeSortie.SUCCES if resultat.statut == "complet" else CodeSortie.ERREUR)
