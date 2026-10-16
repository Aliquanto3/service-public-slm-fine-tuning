"""`slmsp data {seed, generate, validate, filter, build}` : pipeline des Données (AD-17).

Les étapes `seed` (story 9.3) et `generate` (story 9.4) sont implémentées ; les trois
autres répondent « commande non implémentée » (code 2) en attendant leurs stories.

`seed [--racine DIR] [--facteur N] [--scenarios N]` constitue `runs/data-seed/<run_id>/`
(`amorces.jsonl`, `comptes.json`) depuis les jeux publics de `config/sources.toml`, déjà
téléchargés sous `<racine>/data/raw/mediatech/` par `slmsp fetch sources` (extra `data` :
pyarrow). Les scénarios de réunion Mistral sont opt-in : `--scenarios N` (0 par défaut)
exige le gel commité du Jeu d'évaluation v1.1 (code 4 sinon) et fait appel à Mistral.

`generate (--depuis SEED_RUN_ID | --reprendre RUN_ID) [--racine DIR] [--surplus X]` produit
`runs/data-generate/<run_id>/` par le Générateur Mistral (`slmsp.data.generate`). Il exige
d'abord le gel commité du Jeu d'évaluation v1.0 (D1.3, code 4), puis les préalables Mistral
du jour (D1.2, code 1), avant toute écriture. Les passages des sessions Q viennent de l'Index
local (BGE-M3 démarré à la première recherche) ; les traces RD passent par `McpEnDirect`
(profil `outillage`). Appels Mistral payants : commande réservée à la campagne (9.8).

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
from slmsp.core.erreurs import CodeSortie, ConfigurationInvalide, ProvenanceInvalide
from slmsp.data.config import charger_config_donnees
from slmsp.data.licences import RegistreLicences
from slmsp.data.seed import (
    FACTEUR_DEFAUT,
    GABARIT_SCENARIO,
    Decodeur,
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

ETAPES_A_VENIR: dict[str, str] = {
    "validate": "validation contre les sources et le Bac à sable",
    "filter": "doublons et fuites du Jeu d'évaluation",
    "build": "jeu versionné et verrous AD-3",
}


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


def _fraction(valeur: str) -> float:
    try:
        nombre = float(valeur)
    except ValueError:
        raise argparse.ArgumentTypeError(f"nombre attendu (reçu {valeur!r})") from None
    if not 0 <= nombre <= 1:
        raise argparse.ArgumentTypeError("nombre dans [0, 1] attendu")
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
    p.set_defaults(func=_seed)

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
    g.set_defaults(func=_generate)

    for nom, aide in ETAPES_A_VENIR.items():
        autre = actions.add_parser(nom, help=aide, description=aide)
        autre.set_defaults(func=_non_implementee(nom))


def _non_implementee(nom: str) -> Callable[[argparse.Namespace], int]:
    def executer(_args: argparse.Namespace) -> int:
        print(f"slmsp : commande non implémentée : data {nom}", file=sys.stderr)
        return int(CodeSortie.USAGE)

    return executer


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
    journalisée, celui que `Generateur` revérifie ensuite.
    """
    from slmsp.mistral.generateur import message_assistant

    def fabrique(seed_run_id: str, theme_id: str, session_id: str) -> tuple[str, str]:
        generation = creer_generateur(seed_run_id).generer(
            GABARIT_SCENARIO, [theme_id], session_id, "CR"
        )
        contenu = message_assistant(generation.reponse_brute).get("content")
        if not isinstance(contenu, str) or not contenu:
            raise ProvenanceInvalide(f"appel {generation.appel_id} : réponse sans contenu texte")
        return generation.appel_id, contenu

    return fabrique


def _fabrique_scenarios(racine: Path) -> FabriqueScenario:
    """Fabrique réelle (appels Mistral payants) ; préalables D1.2 vérifiés dès maintenant."""
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

    return _fabrique_depuis(creer)


# --- seed --------------------------------------------------------------------------------


def _racine(args: argparse.Namespace) -> Path:
    return (args.racine if args.racine is not None else racine_projet()).resolve()


def _consigner(message: str) -> None:
    print(message, flush=True)


def _seed(args: argparse.Namespace) -> int:
    racine = _racine(args)
    decodeur = _decodeur_pyarrow()
    config_sources = charger_config_sources()
    config = charger_config_donnees()
    registre = RegistreLicences.charger(racine=racine)
    fabrique = None
    if args.scenarios > 0:
        from slmsp.evaluation.gel import jeu_gele_et_commite

        jeu_gele_et_commite("v1.1", racine)  # ManifesteInvalide (code 4) avant toute génération
        fabrique = _fabrique_scenarios(racine)
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
            consigner=_consigner,
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
        print(f"scénarios : {scenarios['produits']}/{scenarios['demandes']}")
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


def _generate(args: argparse.Namespace) -> int:
    from slmsp.budget.registre import RegistreBudget
    from slmsp.core.items import identifiants_proteges
    from slmsp.data.generate import lancer_generation, seed_du_run
    from slmsp.data.sessions import ResolveurPassages
    from slmsp.evaluation.gel import jeu_gele_et_commite
    from slmsp.mcp.direct import McpEnDirect
    from slmsp.mistral.client import ClientMistral, fabriquer_sdk
    from slmsp.mistral.config import charger_mistral
    from slmsp.mistral.generateur import Generateur, charger_prealables

    racine = _racine(args)
    gel = jeu_gele_et_commite("v1.0", racine)  # ManifesteInvalide (code 4) avant tout
    seed_run_id = args.depuis or seed_du_run(args.reprendre, racine=racine)
    config_mistral = charger_mistral()
    dossier = racine_projet() / "config"
    fichier_donnees = dossier / "donnees.toml"
    # Préalables D1.2 (code 1) avant d'ouvrir le registre de budget ou le journal.
    charger_prealables(fichier_donnees, modele=config_mistral.modele, aujourd_hui=date.today())
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
        )
    finally:
        recherche.fermer()
    return _afficher_generation(resultat)


def _afficher_generation(resultat: Any) -> int:
    for tache, ligne in resultat.bilan["taches"].items():
        abandons = sum(ligne["abandons"].values())
        print(
            f"{tache} : {ligne['completes']} complètes, {abandons} abandons, "
            f"{ligne['incidents']} incidents / {ligne['planifiees']} planifiées "
            f"({ligne['appels_nouveaux']} appels, {ligne['appels_reutilises']} réutilisés)"
        )
    print(f"dépense de cette invocation : {resultat.bilan['cout_eur']:.4f} €")
    print(f"run {resultat.run.run_id} ({resultat.statut}) : {resultat.run.dossier}")
    if resultat.statut == "partiel-budget":
        return int(CodeSortie.BUDGET_EPUISE)
    return int(CodeSortie.SUCCES if resultat.statut == "complet" else CodeSortie.ERREUR)
