"""Candidats multiples pour la sélection des cibles : `data candidats` (story 15.2, O2).

Pour chaque ligne du jeu SFT d'un run `data-build` (`train.jsonl`, SHA-256 revérifié contre le
MANIFEST, comme `data build --preferences`), le run produit **plusieurs candidats de cible** :

- `mistral:<appel_id>` : la cible existante de la ligne (dernier appel Mistral de la session),
  sans nouvel appel ;
- `slm:<appel_local_id>` : une sortie du Modèle de base local par température, générée sur
  **exactement la conversation d'entraînement** de la ligne (messages avant la cible et outils,
  comme `preferences.py`), graine `graine + rang` consignée, journalisée dans
  `generations-locales.sqlite` ;
- `openrouter:<appel_id>` : une sortie du second générateur autorisé (DeepSeek), pour les
  Tâches de `deepseek_taches` seulement, via le client OpenRouter (usage `generateur-openrouter`,
  budget réservé avant chaque appel), journalisée dans `appels-generateur-openrouter.sqlite`.

Tâches : CR et LC seulement (`TACHES_CANDIDATES`) ; RE n'a pas de grille de jugement de données
et n'a donc pas de candidats (décision du 20/10). Texte jugé = texte appris : tout candidat passe
par `cible_apprise` (règle de nettoyage du build, story 9.9) avant d'être jugé, et un candidat
que le nettoyage écarterait (vide, plus long que le plafond) n'est pas candidat.

Contrat de sortie (`spec-o3-selection.md`) : `candidats.jsonl`, une ligne par candidat, **aucun
texte** : `session_id` (session `data-generate` d'origine), `candidat_id`, `source` (`mistral`,
`slm:<slug>`, `openrouter:<modèle>`), `tache`, `temperature`, `graine` (nuls pour Mistral), plus
`cle` (clé de reprise) et `rang`. Le texte est relu dans son journal (`texte_candidat`).

Une sortie tronquée, interrompue (tout `finish_reason` OpenRouter autre que `stop`), vide,
non textuelle, hors contexte ou trop longue est journalisée mais **jamais candidate** (C2) :
elle va dans `ecartes.jsonl` avec son motif et sa clé, et la reprise ne la regénère pas. Le run
est idempotent et reprenable : `reprendre_run_id` refuse des réglages divergents du run, saute
toute clé déjà présente dans `candidats.jsonl` ou `ecartes.jsonl` et relit dans le journal
OpenRouter un appel déjà payé pour la même requête (aucun second paiement).
Aucun texte n'est rédigé ici (D1) : les prompts sont ceux du jeu SFT.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from pydantic import ValidationError

from slmsp.budget.tarifs import cout_pire_cas
from slmsp.core.artefacts import (
    NOM_JOURNAL_GENERATEUR_OPENROUTER,
    NOM_JOURNAL_LOCAL,
    Run,
    nouveau_run,
    ouvrir_run,
    ouvrir_sqlite_lecture,
    reprendre,
)
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import BudgetEpuise, ManifesteInvalide, SlmspError
from slmsp.core.nettoyage import VERSION_NETTOYAGE, nettoyer_cible
from slmsp.core.ports import LlmPort
from slmsp.core.schemas.entrainement import LigneEntrainement
from slmsp.core.var import dossier_var
from slmsp.data.config import CandidatsDonnees
from slmsp.data.juge_donnees import (
    CARACTERES_PAR_TOKEN,
    FINS_INTERROMPUES,
    MARGE_TOKENS,
    Candidat,
    PlafondEstimeDepasse,
    source_session,
)
from slmsp.data.nettoyage import Tokeniseur, tokeniseur_du_modele
from slmsp.data.preferences import _exiger_sans_selection, _generer, _jeu_sft
from slmsp.fournisseurs.client import MODE, ClientCompatibleOpenAI, ErreurApiFournisseur
from slmsp.fournisseurs.client import _texte as texte_reponse
from slmsp.inference.journal_local import JournalLocal

__all__ = [
    "NOM_CANDIDATS",
    "NOM_ECARTES",
    "NOM_RAPPORT",
    "SOURCES_JUGE_CROISE",
    "TACHES_CANDIDATES",
    "TYPE_RUN",
    "RegleCible",
    "ResultatCandidats",
    "candidats_depuis_run",
    "cible_apprise",
    "config_candidats",
    "lancer_candidats",
    "regle_cible",
]

TYPE_RUN: Final = "data-candidats"
NOM_CANDIDATS: Final = "candidats.jsonl"
NOM_ECARTES: Final = "ecartes.jsonl"
NOM_RAPPORT: Final = "rapport.json"
TACHES_CANDIDATES: Final = ("CR", "LC")
"""Tâches dont la cible est sélectionnée parmi des candidats (plan méthodologie v2, E4) ; RE
exclue faute de grille de jugement de données (décision du 20/10)."""
SOURCES_JUGE_CROISE: Final = ("openrouter:deepseek/",)
"""Sources qu'un juge croisé (`data juger --juge kimi`) note par défaut : seules à exiger un
juge d'une autre famille que DeepSeek ; la sélection (15.3) prend le minimum des deux."""


@dataclass(frozen=True)
class ResultatCandidats:
    run: Run
    statut: str
    rapport: dict[str, Any]


def _lignes_sft(octets: bytes, version: str) -> list[LigneEntrainement]:
    try:
        return [
            LigneEntrainement.model_validate_json(texte)
            for texte in octets.decode("utf-8").splitlines()
            if texte.strip()
        ]
    except ValidationError as exc:
        raise ManifesteInvalide(f"jeu {version} : ligne SFT non conforme ({exc})") from None


def _generate_run_id(build_run_id: str, base: Path) -> str:
    """`generate_run_id` du run `data-build` `build_run_id`, en remontant `build_run_id` ou le
    premier parent (un run `nettoyage` ou `sous-ensemble` pointe vers son build d'origine)."""
    courant = build_run_id
    for _ in range(6):
        run = ouvrir_run(courant, racine=base)
        config = run.manifeste.config
        if config.get("generate_run_id"):
            return str(config["generate_run_id"])
        suivant = config.get("build_run_id") or (run.manifeste.parents or [None])[0]
        if not suivant:
            break
        courant = str(suivant)
    raise ManifesteInvalide(f"run {build_run_id} : aucun run data-generate d'origine retrouvé")


def _ligne_candidat(
    ligne: LigneEntrainement,
    rang: int,
    *,
    cle: str,
    candidat_id: str,
    source: str,
    temperature: float | None,
    graine: int | None,
) -> dict[str, Any]:
    return {
        "session_id": ligne.meta.session_id,
        "candidat_id": candidat_id,
        "source": source,
        "tache": ligne.tache,
        "temperature": temperature,
        "graine": graine,
        "cle": cle,
        "rang": rang,
    }


def _tokens_entree(prompt: Sequence[dict[str, Any]]) -> int:
    brut = json_canonique(list(prompt)).decode("utf-8")
    return math.ceil(len(brut) / CARACTERES_PAR_TOKEN) + MARGE_TOKENS


def _estimer_openrouter(
    client: ClientCompatibleOpenAI,
    config: CandidatsDonnees,
    prompts: Iterable[Sequence[dict[str, Any]]],
) -> float:
    """Coût pire cas (€) des appels OpenRouter prévus ; vérifie d'abord l'usage de budget."""
    registre = client.registre
    registre.verifier_usage(config.usage_budget)
    return sum(
        cout_pire_cas(
            registre.tarifs,
            config.modele_openrouter,
            MODE,
            _tokens_entree(prompt),
            config.max_tokens_openrouter,
            registre.config.majoration_entree,
        )
        for prompt in prompts
    )


@dataclass(frozen=True)
class RegleCible:
    """Règle de nettoyage du texte appris (story 9.9), relue du build ou par défaut.

    `appliquee` : le jeu SFT du build est déjà nettoyé par cette règle (cible Mistral gardée
    telle quelle au moment des candidats). `modele` : `base:<slug>` du tokenizer du plafond.
    """

    version: int
    plafond_tokens: int
    modele: str
    appliquee: bool

    def config(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "plafond_tokens": self.plafond_tokens,
            "modele": self.modele,
            "appliquee": self.appliquee,
        }

    @classmethod
    def depuis_config(cls, config: Any) -> RegleCible:
        if not isinstance(config, dict):
            raise ManifesteInvalide("run data-candidats sans règle de nettoyage (`nettoyage`)")
        return cls(
            int(config["version"]),
            int(config["plafond_tokens"]),
            str(config["modele"]),
            bool(config["appliquee"]),
        )


def regle_cible(build_run_id: str, base: Path, slug: str, plafond_defaut: int) -> RegleCible:
    """Règle du premier run `nettoyage` de la chaîne de `build_run_id` ; sinon règle courante
    (`VERSION_NETTOYAGE`, plafond `plafond_defaut`, tokenizer `base:<slug>`), non appliquée."""
    courant: str | None = build_run_id
    for _ in range(6):
        if not courant:
            break
        manifeste = ouvrir_run(courant, racine=base).manifeste
        config = manifeste.config
        if config.get("nettoyage") is True:
            return RegleCible(
                int(config["version_nettoyage"]),
                int(config["plafond_tokens"]),
                str(config["modele"]),
                True,
            )
        courant = config.get("build_run_id") or (manifeste.parents or [None])[0]
    return RegleCible(VERSION_NETTOYAGE, plafond_defaut, f"base:{slug}", False)


def cible_apprise(
    texte: str,
    tache: str,
    regle: RegleCible,
    compter: Callable[[str], int] | None = None,
) -> tuple[str, str | None]:
    """`(texte appris, motif d'exclusion)` d'un candidat brut, toutes sources confondues.

    Le texte jugé est celui qui serait appris : `nettoyer_cible` de la règle du build
    (préambule « Voici », titre de tête). Motif `vide` (rien après nettoyage) ou `longueur`
    (plus de `regle.plafond_tokens` tokens, si `compter` est fourni : la ligne aurait été
    écartée par `build --nettoyage`) ; `None` si le candidat est recevable. La sélection
    (story 15.3) écrit la cible avec cette même fonction.
    """
    propre = nettoyer_cible(texte, regle.version, tache)
    if not propre.strip():
        return propre, "vide"
    if compter is not None and compter(propre) > regle.plafond_tokens:
        return propre, "longueur"
    return propre, None


def _config_run(
    *,
    build_run_id: str,
    version_sft: str,
    generate_run_id: str,
    taches: Sequence[str],
    cle_slm: str,
    temperatures: Sequence[float],
    config: CandidatsDonnees,
    deepseek_taches: Sequence[str],
    regle: RegleCible,
    tokenizer_sha256: str,
) -> dict[str, Any]:
    return {
        "build_run_id": build_run_id,
        "jeu_sft_version": version_sft,
        "generate_run_id": generate_run_id,
        "taches": sorted(taches),
        "base": cle_slm,
        "temperatures": [float(t) for t in temperatures],
        "graine": config.graine,
        "max_tokens": config.max_tokens,
        "deepseek_taches": sorted(deepseek_taches),
        "modele_openrouter": config.modele_openrouter if deepseek_taches else None,
        "temperature_openrouter": config.temperature_openrouter,
        "max_tokens_openrouter": config.max_tokens_openrouter,
        "effort_raisonnement_openrouter": config.effort_raisonnement,
        "nettoyage": regle.config(),
        "tokenizer_sha256": tokenizer_sha256,
    }


def _exiger_meme_config(run: Run, attendue: Mapping[str, Any]) -> None:
    """Refuse la reprise si un réglage du run diffère de `attendue` (clés, graines, texte)."""
    stockee = run.manifeste.config
    ecarts = [cle for cle, valeur in attendue.items() if stockee.get(cle) != valeur]
    if ecarts:
        detail = ", ".join(f"{c} : {stockee.get(c)!r} ≠ {attendue[c]!r}" for c in ecarts)
        raise ManifesteInvalide(f"reprise de {run.run_id} refusée, réglages divergents ({detail})")


def lancer_candidats(
    *,
    racine: str | Path,
    build_run_id: str,
    taches: Sequence[str],
    slug: str,
    temperatures: Sequence[float],
    llm: LlmPort,
    config: CandidatsDonnees,
    plafond_tokens: int,
    deepseek_taches: Sequence[str] = (),
    client: ClientCompatibleOpenAI | None = None,
    journal: JournalLocal | None = None,
    tokeniseur: Tokeniseur | None = None,
    plafond_estime_eur: float | None = None,
    reprendre_run_id: str | None = None,
    consigner: Callable[[str], None] = print,
) -> ResultatCandidats:
    """Produit `runs/data-candidats/<run_id>/candidats.jsonl` (voir le module).

    `plafond_tokens` : plafond du texte appris si le build n'est pas nettoyé (sinon celui du
    run `nettoyage`). Lève `ManifesteInvalide` (jeu SFT absent, altéré, sans ligne des Tâches
    demandées, ou reprise aux réglages divergents) et `PlafondEstimeDepasse` (coût OpenRouter
    pire cas au-dessus de `plafond_estime_eur`) avant tout run et tout appel. Statut
    `partiel-budget` (`BudgetEpuise`) ou `partiel-erreur` (API OpenRouter) : les candidats
    écrits restent valides, la reprise complète le reste.
    """
    if deepseek_taches and client is None:
        raise ValueError("deepseek_taches exige un client OpenRouter")
    sans_grille = sorted(set(taches) - set(TACHES_CANDIDATES))
    if sans_grille:
        raise ValueError(
            f"Tâche(s) {', '.join(sans_grille)} sans candidats : aucune grille de jugement de "
            f"données (attendu parmi {', '.join(TACHES_CANDIDATES)})"
        )
    base = Path(racine).resolve()
    version_sft, manifeste_sft, octets = _jeu_sft(build_run_id, base)
    _exiger_sans_selection(version_sft, manifeste_sft, "candidats")
    lignes = _lignes_sft(octets, version_sft)
    voulues = [(rang, ligne) for rang, ligne in enumerate(lignes) if ligne.tache in taches]
    if not voulues:
        raise ManifesteInvalide(f"jeu {version_sft} : aucune ligne des Tâches {list(taches)}")
    generate_run_id = _generate_run_id(build_run_id, base)
    regle = regle_cible(build_run_id, base, slug, plafond_tokens)
    tokeniseur = tokeniseur or tokeniseur_du_modele(regle.modele.removeprefix("base:"), racine=base)
    journal = journal if journal is not None else JournalLocal()
    modele_or = config.modele_openrouter
    source_or = f"openrouter:{modele_or}"
    cle_slm = f"slm:{slug}"
    config_run = _config_run(
        build_run_id=build_run_id,
        version_sft=version_sft,
        generate_run_id=generate_run_id,
        taches=taches,
        cle_slm=cle_slm,
        temperatures=temperatures,
        config=config,
        deepseek_taches=deepseek_taches,
        regle=regle,
        tokenizer_sha256=tokeniseur.sha256,
    )
    deja: set[str] = set()
    if reprendre_run_id is not None:
        run_precedent = ouvrir_run(reprendre_run_id, racine=base)
        if run_precedent.type != TYPE_RUN:
            raise ManifesteInvalide(f"run {reprendre_run_id} : type {TYPE_RUN} attendu")
        _exiger_meme_config(run_precedent, config_run)
        deja = {
            str(ligne["cle"])
            for nom in (NOM_CANDIDATS, NOM_ECARTES)
            for ligne in run_precedent.lire_jsonl(nom)
            if isinstance(ligne, dict) and "cle" in ligne
        }
    pour_openrouter = [
        (rang, ligne)
        for rang, ligne in voulues
        if ligne.tache in deepseek_taches
        and f"{ligne.meta.session_id}|{source_or}" not in deja
        and not ligne.tools
    ]
    payes: dict[str, dict[str, Any]] = {}
    if pour_openrouter and client is not None and reprendre_run_id is not None:
        # Appels déjà facturés et journalisés mais non écrits (run interrompu) : relus, pas repayés.
        payes = client.journal.reussis(config.usage_budget, modele_or) if client.journal else {}
    a_payer = [
        (rang, ligne)
        for rang, ligne in pour_openrouter
        if _sha_requete(config, rang, ligne) not in payes
    ]
    cout_estime = 0.0
    if a_payer and client is not None:
        cout_estime = _estimer_openrouter(
            client, config, (ligne.messages[:-1] for _, ligne in a_payer)
        )
        consigner(
            f"Estimation OpenRouter : {len(a_payer)} appel(s) {modele_or}, "
            f"pire cas {cout_estime:.2f} €."
        )
        if plafond_estime_eur is not None and cout_estime > plafond_estime_eur:
            raise PlafondEstimeDepasse(
                f"candidats refusés : pire cas {cout_estime:.2f} € au-dessus du plafond de "
                f"{plafond_estime_eur:.2f} € ; aucun run créé, aucun appel fait"
            )
    if reprendre_run_id is not None:
        run, _ = reprendre(reprendre_run_id, fichier=NOM_CANDIDATS, cle="cle", racine=base)
    else:
        run = nouveau_run(
            TYPE_RUN,
            "candidats",
            config_run,
            parents=[build_run_id],
            graine=config.graine,
            racine=base,
        )
    comptes: Counter[tuple[str, str]] = Counter()
    ecartes: Counter[str] = Counter()
    etat = {"statut": "complet", "motif": None, "cout": 0.0}

    def ecrire(ligne: dict[str, Any]) -> None:
        run.ajouter_jsonl(NOM_CANDIDATS, ligne)
        comptes[(ligne["tache"], ligne["source"].split(":")[0])] += 1

    def ecarter(
        ligne: LigneEntrainement, rang: int, cle: str, source: str, motif: str, **plus: Any
    ) -> None:
        ecartes[motif] += 1
        run.ajouter_jsonl(
            NOM_ECARTES,
            {
                "cle": cle,
                "session_id": ligne.meta.session_id,
                "tache": ligne.tache,
                "source": source,
                "rang": rang,
                "motif": motif,
                **plus,
            },
        )

    def recevable(texte: str, ligne: LigneEntrainement) -> str | None:
        return cible_apprise(texte, ligne.tache, regle, tokeniseur.compter)[1]

    try:
        for rang, ligne in voulues:
            sid = ligne.meta.session_id
            prompt = ligne.messages[:-1]
            cle_mistral = f"{sid}|mistral"
            if ligne.meta.appel_ids and cle_mistral not in deja:
                cible = ligne.messages[-1].get("content")
                motif_m = None if regle.appliquee else recevable(str(cible or ""), ligne)
                if not isinstance(cible, str):
                    motif_m = "non_texte"
                if motif_m is not None:
                    ecarter(ligne, rang, cle_mistral, "mistral", motif_m)
                else:
                    ecrire(
                        _ligne_candidat(
                            ligne,
                            rang,
                            cle=cle_mistral,
                            candidat_id=f"mistral:{ligne.meta.appel_ids[-1]}",
                            source="mistral",
                            temperature=None,
                            graine=None,
                        )
                    )
            for temperature in temperatures:
                cle = f"{sid}|{cle_slm}|{temperature}"
                if cle in deja:
                    continue
                options = {
                    "temperature": temperature,
                    "seed": config.graine + rang,
                    "max_tokens": config.max_tokens,
                }
                texte, motif = _generer(llm, prompt, ligne.tools, options)
                appel_id = journal.inscrire(
                    session_id=sid,
                    slug=slug,
                    requete={
                        "messages": prompt,
                        "tools": ligne.tools,
                        "options": options,
                        "rang": rang,
                    },
                    reponse=texte,
                    statut="ok" if motif is None else motif.replace("_", "-"),
                )
                if motif is None and texte is None:
                    motif = "non_texte"
                if motif is None:
                    motif = recevable(str(texte), ligne)
                if motif is not None:
                    ecarter(ligne, rang, cle, cle_slm, motif, appel_local_id=appel_id)
                    continue
                ecrire(
                    _ligne_candidat(
                        ligne,
                        rang,
                        cle=cle,
                        candidat_id=f"slm:{appel_id}",
                        source=cle_slm,
                        temperature=temperature,
                        graine=options["seed"],
                    )
                )
        if pour_openrouter and client is not None:
            _candidats_openrouter(
                client,
                config,
                pour_openrouter,
                payes,
                source_or,
                recevable,
                ecrire,
                ecarter,
                etat,
            )
    except KeyboardInterrupt:
        run.terminer("interrompu", "interruption clavier")
        raise
    except BaseException as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
        raise
    rapport: dict[str, Any] = {
        "schema_version": 1,
        "jeu_sft_version": version_sft,
        "candidats": {f"{t}/{s}": n for (t, s), n in sorted(comptes.items())},
        "ecartes_par_motif": dict(sorted(ecartes.items())),
        "cout_openrouter_eur": etat["cout"],
        "cout_openrouter_estime_pire_cas_eur": cout_estime,
        "statut": etat["statut"],
        "motif": etat["motif"],
    }
    run.ajouter_jsonl("bilan.jsonl", rapport)
    if etat["statut"] == "complet":
        run.ecrire(NOM_RAPPORT, json_canonique(rapport) + b"\n")
    run.terminer(etat["statut"], etat["motif"])
    consigner(
        f"candidats : {sum(comptes.values())} écrits, {sum(ecartes.values())} écartés "
        f"{dict(ecartes)} ; statut {etat['statut']}"
    )
    return ResultatCandidats(run, etat["statut"], rapport)


def _parametres_openrouter(config: CandidatsDonnees, rang: int) -> dict[str, Any]:
    parametres: dict[str, Any] = {"temperature": config.temperature_openrouter}
    if config.effort_raisonnement is not None:
        parametres["reasoning"] = {"effort": config.effort_raisonnement}
    return {**parametres, "seed": config.graine + rang}


def _sha_requete(config: CandidatsDonnees, rang: int, ligne: LigneEntrainement) -> str:
    """SHA-256 du corps que `ClientCompatibleOpenAI.appeler` journalisera pour cette ligne."""
    corps = {
        "model": config.modele_openrouter,
        "messages": [dict(m) for m in ligne.messages[:-1]],
        "max_tokens": config.max_tokens_openrouter,
        **_parametres_openrouter(config, rang),
    }
    return sha256_hex(json_canonique(corps))


def _reponse_relue(ligne: Mapping[str, Any]) -> tuple[str, str | None] | None:
    """`(texte, finish_reason)` d'un appel journalisé `ok`, SHA revérifié ; `None` sinon."""
    brut = _corps_verifie("ok", ligne.get("reponse_brute"), ligne.get("sha256_reponse"))
    if brut is None:
        return None
    try:
        return texte_reponse(json.loads(brut))
    except (ValueError, KeyError, TypeError, AttributeError):
        return None


def _candidats_openrouter(
    client: ClientCompatibleOpenAI,
    config: CandidatsDonnees,
    cibles: Sequence[tuple[int, LigneEntrainement]],
    payes: Mapping[str, Mapping[str, Any]],
    source: str,
    recevable: Callable[[str, LigneEntrainement], str | None],
    ecrire: Callable[[dict[str, Any]], None],
    ecarter: Callable[..., None],
    etat: dict[str, Any],
) -> None:
    """Appels OpenRouter en parallèle ; chaque résultat est écrit dès son arrivée.

    Un appel déjà journalisé `ok` pour la même requête (`payes`, run interrompu) est relu sans
    nouvel appel. Après `BudgetEpuise` ou une erreur d'API, les appels non lancés sont annulés
    (statut `partiel-budget` ou `partiel-erreur`), ceux en cours sont écrits ; toute autre
    exception annule aussi les appels non lancés avant de remonter.
    """

    def traiter(
        rang: int, ligne: LigneEntrainement, appel_id: str, texte: str, fin: str | None
    ) -> None:
        cle = f"{ligne.meta.session_id}|{source}"
        raison = (fin or "").lower()
        if raison != "stop":
            motif = "tronquee" if raison in FINS_INTERROMPUES else "interrompue"
            ecarter(ligne, rang, cle, source, motif, appel_id=appel_id, finish_reason=fin)
            return
        motif = recevable(texte, ligne)
        if motif is not None:
            ecarter(ligne, rang, cle, source, motif, appel_id=appel_id)
            return
        ecrire(
            _ligne_candidat(
                ligne,
                rang,
                cle=cle,
                candidat_id=f"openrouter:{appel_id}",
                source=source,
                temperature=config.temperature_openrouter,
                graine=config.graine + rang,
            )
        )

    def appeler(rang: int, ligne: LigneEntrainement) -> Any:
        prompt = ligne.messages[:-1]
        return client.appeler(
            config.usage_budget,
            ligne.meta.session_id,
            prompt,
            modele=config.modele_openrouter,
            max_tokens=config.max_tokens_openrouter,
            tokens_entree_estimes=_tokens_entree(prompt),
            parametres=_parametres_openrouter(config, rang),
        )

    a_appeler: list[tuple[int, LigneEntrainement]] = []
    for rang, ligne in cibles:
        deja_paye = payes.get(_sha_requete(config, rang, ligne))
        relue = _reponse_relue(deja_paye) if deja_paye is not None else None
        if deja_paye is None or relue is None:
            a_appeler.append((rang, ligne))
        else:
            traiter(rang, ligne, str(deja_paye["appel_id"]), *relue)
    if not a_appeler:
        return
    with ThreadPoolExecutor(max_workers=config.appels_paralleles) as pool:
        futurs: dict[Future[Any], tuple[int, LigneEntrainement]] = {
            pool.submit(appeler, rang, ligne): (rang, ligne) for rang, ligne in a_appeler
        }
        try:
            for futur in as_completed(futurs):
                if futur.cancelled():
                    continue
                rang, ligne = futurs[futur]
                try:
                    reponse = futur.result()
                except BudgetEpuise as exc:
                    if etat["statut"] == "complet":
                        etat["statut"], etat["motif"] = "partiel-budget", str(exc)
                    _annuler(futurs)
                    continue
                except ErreurApiFournisseur as exc:
                    etat["cout"] += exc.cout_eur
                    if etat["statut"] == "complet":
                        etat["statut"] = "partiel-erreur"
                        etat["motif"] = f"{type(exc).__name__} : {exc}"
                    _annuler(futurs)
                    continue
                etat["cout"] += reponse.cout_eur
                traiter(rang, ligne, reponse.appel_id, reponse.texte, reponse.finish_reason)
        except BaseException:
            _annuler(futurs)  # rien de plus n'est envoyé ; les appels en cours restent journalisés
            raise


def _annuler(futurs: Iterable[Future[Any]]) -> None:
    for futur in futurs:
        futur.cancel()


# --- Relecture du texte d'un candidat (jugement) ------------------------------------------


def config_candidats(run_id: str, racine: str | Path) -> dict[str, Any]:
    """Config d'un run `data-candidats` (`generate_run_id`, `taches`, `base`…)."""
    run = ouvrir_run(run_id, racine=racine)
    if run.type != TYPE_RUN:
        raise ManifesteInvalide(f"run {run_id} : type {run.type!r}, {TYPE_RUN} attendu")
    return dict(run.manifeste.config)


def _corps_verifie(statut: str, brut: bytes | None, sha: str | None) -> bytes | None:
    """Corps brut d'un appel journalisé s'il est `ok` et de SHA-256 conforme, sinon `None`."""
    if statut != "ok" or brut is None:
        return None
    corps = bytes(brut)
    return corps if sha256_hex(corps) == sha else None


def texte_candidat(connexions: dict[str, Any], racine: Path, candidat_id: str) -> str | None:
    """Texte d'un candidat `slm:` ou `openrouter:` relu dans son journal (lecture seule, lecteur
    `data`), octets revérifiés (SHA-256) ; `None` si l'appel est absent, non `ok` ou altéré."""
    genre, _, appel_id = candidat_id.partition(":")
    nom = NOM_JOURNAL_LOCAL if genre == "slm" else NOM_JOURNAL_GENERATEUR_OPENROUTER
    if genre not in ("slm", "openrouter"):
        return None
    if genre not in connexions:
        chemin = dossier_var() / nom
        if not chemin.is_file():
            return None
        connexions[genre] = ouvrir_sqlite_lecture(chemin, "data", racine=racine)
    connexion = connexions[genre]
    ligne = connexion.execute(
        "SELECT statut, reponse_brute, sha256_reponse FROM appels WHERE appel_id = ?",
        (appel_id,),
    ).fetchone()
    if ligne is None:
        return None
    brut = _corps_verifie(*ligne)
    if brut is None:
        return None
    if genre == "slm":
        return brut.decode("utf-8")
    try:
        contenu = json.loads(brut)["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        return None
    return contenu if isinstance(contenu, str) else None


def candidats_depuis_run(
    run_id: str,
    lecteur: Any,
    taches: Iterable[str],
    *,
    racine: str | Path,
    sources: Sequence[str] | None = None,
) -> tuple[list[Candidat], dict[str, int]]:
    """Candidats de `candidats.jsonl` pour `taches`, texte relu dans leur journal puis passé par
    `cible_apprise` (règle du run : texte jugé = texte appris), source relue dans la session
    `data-generate` d'origine (`LecteurGeneration`). `sources` : préfixes de `source` retenus
    (`SOURCES_JUGE_CROISE` pour le juge croisé) ; `None` : toutes.

    Renvoie aussi les comptes d'écartés : `hors_taches` (Tâche sans grille de données),
    `autre_source` (hors `sources`), `source_introuvable`, `texte_introuvable` (journal absent,
    appel non `ok` ou SHA altéré), `vide` (rien après nettoyage).
    """
    base = Path(racine).resolve()
    run = ouvrir_run(run_id, racine=base)
    if run.type != TYPE_RUN:
        raise ManifesteInvalide(f"run {run_id} : type {run.type!r}, {TYPE_RUN} attendu")
    regle = RegleCible.depuis_config(run.manifeste.config.get("nettoyage"))
    voulues = set(taches)
    sessions = {brut.session_id: brut for brut in lecteur.sessions()}
    sources_lues: dict[str, str] = {}
    candidats: list[Candidat] = []
    ecartes: Counter[str] = Counter()
    connexions: dict[str, Any] = {}
    try:
        for ligne in run.lire_jsonl(NOM_CANDIDATS):
            if not isinstance(ligne, dict):
                continue
            tache, sid, cid = ligne.get("tache"), ligne.get("session_id"), ligne.get("candidat_id")
            if tache not in voulues:
                ecartes["hors_taches"] += 1
                continue
            if sources is not None and not str(ligne.get("source")).startswith(tuple(sources)):
                ecartes["autre_source"] += 1
                continue
            brut = sessions.get(str(sid))
            if brut is None:
                ecartes["source_introuvable"] += 1
                continue
            if sid not in sources_lues:
                try:
                    sources_lues[sid] = source_session(lecteur, brut)
                except (SlmspError, KeyError):
                    sources_lues[sid] = ""
            texte: str | None
            if str(cid).startswith("mistral:"):
                try:
                    texte = lecteur.reponse_finale(brut)
                except (SlmspError, KeyError):
                    texte = None
            else:
                texte = texte_candidat(connexions, base, str(cid))
            if not sources_lues[sid]:
                ecartes["source_introuvable"] += 1
            elif not texte:
                ecartes["texte_introuvable"] += 1
            elif (appris := cible_apprise(texte, str(tache), regle))[1] is not None:
                ecartes[str(appris[1])] += 1
            else:
                candidats.append(
                    Candidat(str(cid), str(sid), str(tache), sources_lues[sid], appris[0])
                )
    finally:
        for connexion in connexions.values():
            connexion.close()
    return candidats, dict(ecartes)
