"""`slmsp data {seed, generate, validate, filter, build}` : pipeline des Données (AD-17).

Les étapes `seed` (9.3), `generate` (9.4), `validate`, `filter` (9.5) et `build` (9.6) sont
implémentées.

`seed [--racine DIR] [--facteur N] [--scenarios N] [--courriers {N,auto}]` constitue
`runs/data-seed/<run_id>/` (`amorces.jsonl`, `comptes.json`) depuis les jeux publics de
`config/sources.toml`, déjà téléchargés sous `<racine>/data/raw/mediatech/` par
`slmsp fetch sources` (extra `data` : pyarrow). Les longueurs RE sont tirées dans
`[seed].re_longueurs` de `config/donnees.toml`. Les scénarios de réunion (`--scenarios N`)
et les amorces de courrier type (`--courriers N`, ou `auto` = volume CT x facteur) sont
générés par Mistral, opt-in (0 par défaut) : ils exigent le gel commité du Jeu d'évaluation
v1.1 (code 4 sinon). Les amorces CT d'une session déjà journalisée sont réutilisées sans
nouvel appel (relance idempotente).

`generate (--depuis SEED_RUN_ID | --reprendre RUN_ID) [--racine DIR] [--surplus X]` produit
`runs/data-generate/<run_id>/` par le Générateur Mistral (`slmsp.data.generate`). Il exige
d'abord le gel commité du Jeu d'évaluation v1.0 (D1.3, code 4), puis les préalables Mistral
du jour (D1.2, code 1), avant toute écriture. Les passages des sessions Q viennent de l'Index
local (BGE-M3 démarré à la première recherche) ; les traces RD passent par `McpEnDirect`
(profil `outillage`). Appels Mistral payants : commande réservée à la campagne (9.8).

`validate --depuis GENERATE_RUN_ID [--racine DIR] [--controle-mistral]` rejoue les traces RD
sur le Bac à sable et vérifie URL et valeurs de chaque exemple contre ses sources
(`slmsp.data.validate`) ; `--controle-mistral` ajoute un contrôle de fidélité des Tâches CR, LC
et RE par Mistral (`usage = validation`, appels payants, jamais le Juge Claude).
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
    p.add_argument(
        "--courriers",
        type=_courriers,
        default=0,
        metavar="{N,auto}",
        help="appels Mistral pour les amorces de courrier type CT (auto : volume CT x "
        "facteur ; défaut : 0, aucun appel d'API)",
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

    b = actions.add_parser(
        "build",
        help="construire le jeu d'entraînement versionné (re-dérivation du journal)",
        description="Étape build : re-dérivation octet par octet, data/train/vN, MANIFEST.",
    )
    b.add_argument(
        "--depuis",
        required=True,
        metavar="RUN_ID",
        help="run data-filter ; avec --preferences ou --nettoyage, run data-build du jeu SFT",
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
    from slmsp.mistral.generateur import message_assistant, raison_de_fin

    def fabrique(seed_run_id: str, theme_id: str, session_id: str) -> tuple[str, str]:
        generation = creer_generateur(seed_run_id).generer(
            GABARIT_SCENARIO, [theme_id], session_id, "CR"
        )
        if raison_de_fin(generation.reponse_brute) == "length":
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
    from slmsp.mistral.generateur import message_assistant, raison_de_fin

    def fabrique(seed_run_id: str, sujet_id: str, session_id: str) -> tuple[str, str]:
        generateur = creer_generateur(seed_run_id)
        ligne = generateur.reponse_journalisee(GABARIT_AMORCES_CT, [sujet_id], session_id, "CT")
        if ligne is not None:
            appel_id, brut = ligne.appel_id, ligne.reponse_brute
        else:
            generation = generateur.generer(GABARIT_AMORCES_CT, [sujet_id], session_id, "CT")
            appel_id, brut = generation.appel_id, generation.reponse_brute
        if raison_de_fin(brut) == "length":
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


def _build(args: argparse.Namespace) -> int:
    from slmsp.data.build import lancer_build
    from slmsp.harness.taches import charger_taches

    racine = _racine(args)
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
