"""Étape `build` : jeu d'entraînement versionné, re-dérivé du journal (story 9.6, AD-3, FR-29/31).

`lancer_build` produit `runs/data-build/<run_id>/` et `data/train/vN/` à partir d'un run
`data-filter` (`retenus.jsonl`). Chaque ligne de `train.jsonl` est refabriquée à partir des
réponses brutes du journal Mistral (`usage = generation` seulement) par `data.extraction`, avec
pour seules transformations : le prompt de la Tâche (`config/prompts/taches/`, SHA consigné),
les passages formatés par `harness.prompts.construire_messages`, et les messages `tool` des
cassettes de la même session. Les octets à écrire sont ensuite revérifiés ligne à ligne par
une nouvelle re-dérivation (`verifier_octets`) : la moindre différence lève `ProvenanceInvalide`
et rien n'est écrit sous `data/train/`.

Mise en forme par Tâche (messages après le prompt système) :

- Q : question de l'amorce et passages du plan, réponse Mistral ; RD : demande de l'amorce,
  puis tours d'outils (messages `assistant` journalisés et `tool` vérifiés contre les
  cassettes) et réponse finale ; `tools` vient de `config/outils-mcp.toml` ;
- CR : transcription (1er appel) en entrée, compte rendu (2e appel) en sortie ;
- LC, RE, CT : amorces nommées par leur emplacement en entrée, réponse Mistral en sortie ;
- CO : texte fautif de Mistral en entrée, texte public de l'amorce (SHA vérifié) en sortie ;
- generique : sans prompt de Tâche, la demande de l'amorce puis la réponse Mistral.

Variante `diffusable` : toute source (amorces, réponses Mistral, résultats d'outils) doit avoir
l'usage `diffusable` au Registre des licences, sinon le build échoue avant tout run ;
`recherche` accepte aussi les sources `recherche` et marque le jeu comme tel. Une version
`vN` existante n'est jamais réécrite : le suivant prend `max(N) + 1`.

Aucun texte n'est rédigé ici (D1.1) : tout vient du journal, des amorces vérifiées par SHA et
des cassettes.
"""

from __future__ import annotations

import json
import random
import re
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Final

from pydantic import ValidationError

from slmsp.core.artefacts import Run, lire, nouveau_run, ouvrir_run
from slmsp.core.canonique import json_canonique, sha256_fichier, sha256_hex
from slmsp.core.erreurs import ManifesteInvalide, ProvenanceInvalide, SlmspError
from slmsp.core.messages import ConversationInvalide, valider_conversation
from slmsp.core.schemas.amorce import Amorce
from slmsp.core.schemas.cassette import Cassette
from slmsp.core.schemas.entrainement import (
    TYPE_RUN_BUILD,
    ConditionsMistral,
    LigneEntrainement,
    ManifesteJeuEntrainement,
    MetaLigne,
)
from slmsp.core.schemas.session_donnees import SessionBrute
from slmsp.data.config import ConfigDonnees
from slmsp.data.extraction import VERSION_EXTRACTEUR, extraire_contenu, extraire_message
from slmsp.data.filter import NOM_RETENUS
from slmsp.data.filter import TYPE_RUN as TYPE_RUN_FILTER
from slmsp.data.licences import RegistreLicences
from slmsp.data.validate import (
    NOM_RAPPORT,
    NOM_REJETS,
    LecteurGeneration,
    ouvrir_generation,
    statut_herite,
)
from slmsp.harness.prompts import EntreeInvalide, construire_messages
from slmsp.harness.taches import TableTaches
from slmsp.harness.taches.recherche import messages_connecte
from slmsp.mcp.outils import charger_outils
from slmsp.mistral.generateur import Generateur
from slmsp.mistral.journal import JournalMistral, LigneAppel

__all__ = [
    "NOM_ECHANTILLON",
    "NOM_MANIFEST",
    "NOM_TRAIN",
    "SOURCE_MISTRAL",
    "SOURCE_OUTILS",
    "TYPE_RUN",
    "VARIANTES",
    "ContexteBuild",
    "DerivationRefusee",
    "ResultatBuild",
    "construire_conversation",
    "lancer_build",
    "rederiver_ligne",
    "serialiser",
    "verifier_octets",
]

TYPE_RUN: Final = TYPE_RUN_BUILD
NOM_TRAIN: Final = "train.jsonl"
NOM_MANIFEST: Final = "MANIFEST.json"
NOM_ECHANTILLON: Final = "echantillon-relecture.jsonl"
VARIANTES: Final = ("diffusable", "recherche")
SOURCE_MISTRAL: Final = "mistral/reponses-generateur"
SOURCE_OUTILS: Final = "data.gouv/reponses-outils-mcp"
TACHES_TEXTE: Final = {"Q": "question", "RD": "demande"}
"""Tâches à entrée texte et emplacement de l'amorce qui la porte."""
MODE_OUTILS: Final = "connecte"
"""Début de conversation des Tâches à outils : celui du Mode connecté (consigné au MANIFEST)."""
_RE_VERSION: Final = re.compile(r"v([0-9]+)")


class DerivationRefusee(ProvenanceInvalide):
    """Session que la re-dérivation refuse, avec le motif que `validate` consigne (F4).

    Les refus qui ne dépendent ni de la licence ni de la variante sont vérifiés dès `validate`
    par `construire_conversation` ; `build` les rencontre avec le même code.
    """

    def __init__(self, motif: str, detail: str) -> None:
        super().__init__(detail)
        self.motif = motif
        self.detail = detail


@dataclass(frozen=True)
class ContexteBuild:
    """Ce que la re-dérivation lit : journal et run `generate` (via le lecteur), Tâches, outils."""

    lecteur: LecteurGeneration
    taches: TableTaches
    outils: Sequence[Mapping[str, Any]]
    registre: RegistreLicences


@dataclass(frozen=True)
class ResultatBuild:
    """Run produit, statut final, version écrite et rapport."""

    run: Run
    statut: str
    version: str
    dossier: Path
    rapport: dict[str, Any]


# --- Re-dérivation d'une ligne -----------------------------------------------------------------


def _amorce(ctx: ContexteBuild, amorce_id: str) -> Amorce:
    """Amorce du seed dont le texte est vérifié (SHA, ou réponse journalisée si Mistral),
    règle partagée avec `validate`."""
    return ctx.lecteur.amorce_verifiee(amorce_id)


def _cassettes(lecteur: LecteurGeneration, brut: SessionBrute) -> list[Cassette]:
    cassettes = []
    for chemin in brut.cassettes:
        try:
            octets = lire(lecteur.racine / chemin, "data", racine=lecteur.racine)
            cassettes.append(Cassette.model_validate_json(octets))
        except (OSError, ValidationError, SlmspError):
            raise DerivationRefusee(
                "outil_hors_cassette", f"cassette {Path(chemin).name} illisible"
            ) from None
    return cassettes


def _tours_outils(
    lecteur: LecteurGeneration, brut: SessionBrute, lignes: Sequence[LigneAppel]
) -> list[dict[str, Any]]:
    """Messages `assistant` journalisés et `tool` des cassettes de la session RD."""
    cassettes = _cassettes(lecteur, brut)
    messages: list[dict[str, Any]] = []
    for position, ligne in enumerate(lignes):
        message = extraire_message(ligne.reponse_brute)
        messages.append(message)
        appels = message.get("tool_calls")
        if not appels:
            continue
        if position + 1 >= len(lignes):
            raise DerivationRefusee(
                "conversation_invalide", "dernier appel de la session avec des appels d'outils"
            )
        try:
            requete = json.loads(lignes[position + 1].requete)["messages"]
        except (ValueError, KeyError, TypeError):
            raise DerivationRefusee(
                "outil_hors_cassette", "requête journalisée illisible"
            ) from None
        recus = {
            m.get("tool_call_id"): m
            for m in requete
            if isinstance(m, Mapping) and m.get("role") == "tool"
        }
        for appel in appels:
            retour = recus.get(appel.get("id") if isinstance(appel, Mapping) else None)
            if retour is None or not any(
                Generateur._resultat_de_cassette(retour, appel, c) for c in cassettes
            ):
                raise DerivationRefusee(
                    "outil_hors_cassette",
                    f"appel d'outil {appel.get('id') if isinstance(appel, Mapping) else '?'} : "
                    "résultat absent des cassettes de la session",
                )
            messages.append(dict(retour))
    return messages


def _entree(
    brut: SessionBrute, amorces: Sequence[Amorce], lignes: Sequence[LigneAppel]
) -> str | dict[str, str]:
    """Entrée de la Tâche pour `construire_messages`, depuis les amorces et les réponses."""
    tache = brut.tache
    if tache in TACHES_TEXTE:
        textes = [a.texte for a in amorces if a.emplacement == TACHES_TEXTE[tache]]
        if len(textes) != 1:
            raise DerivationRefusee(
                "entree_refusee",
                f"Tâche {tache} : une amorce « {TACHES_TEXTE[tache]} » attendue ({len(textes)})",
            )
        return textes[0]
    if tache == "CR":
        if len(lignes) != 2:
            raise DerivationRefusee(
                "entree_refusee", "Tâche CR : transcription puis compte rendu attendus"
            )
        return {"transcription": extraire_contenu(lignes[0].reponse_brute)}
    if tache == "CO":
        return {"texte": extraire_contenu(lignes[-1].reponse_brute)}
    entree: dict[str, str] = {}
    for amorce in amorces:
        if amorce.emplacement in entree:
            raise DerivationRefusee(
                "entree_refusee", f"Tâche {tache} : emplacement {amorce.emplacement} en double"
            )
        entree[amorce.emplacement] = amorce.texte
    return entree


def _sortie(brut: SessionBrute, amorces: Sequence[Amorce], lignes: Sequence[LigneAppel]) -> str:
    if brut.tache == "CO":
        textes = [a.texte for a in amorces if a.emplacement == "texte"]
        if len(textes) != 1:
            raise DerivationRefusee("entree_refusee", "Tâche CO : une amorce « texte » attendue")
        return textes[0]
    return extraire_contenu(lignes[-1].reponse_brute)


def _exiger_amorce_liee(amorce: Amorce, brut: SessionBrute) -> None:
    if amorce.lie_a not in brut.amorce_ids:
        raise DerivationRefusee(
            "entree_refusee",
            f"amorce {amorce.amorce_id} : paramètre sans son amorce liée dans la session",
        )


def sources_de(ctx: ContexteBuild, brut: SessionBrute) -> list[str]:
    """Sources du Registre dont dépend la session (amorces, réponses Mistral, outils)."""
    ids = {SOURCE_MISTRAL}
    for amorce_id in [*brut.amorce_ids, *brut.amorces_derivees]:
        amorce = _amorce(ctx, amorce_id)
        if amorce.auteur_contenu == "config":
            _exiger_amorce_liee(amorce, brut)
            continue  # paramètre tiré par graine : aucune source de contenu
        ids.add(amorce.jeu if amorce.auteur_contenu == "public" and amorce.jeu else SOURCE_MISTRAL)
    if brut.cassettes:
        ids.add(SOURCE_OUTILS)
    return sorted(ids)


def construire_conversation(
    lecteur: LecteurGeneration, taches: TableTaches, brut: SessionBrute
) -> tuple[list[LigneAppel], list[dict[str, Any]]]:
    """Appels et messages de la session, sans licence ni variante.

    Règle commune à `build` et à `validate` (F4). Tout refus propre à la session est une
    `DerivationRefusee` (motif `entree_refusee`, `outil_hors_cassette` ou
    `conversation_invalide`) ; les refus de provenance (appel, amorce) restent des
    `ProvenanceInvalide`, que `validate` a déjà contrôlés avant.
    """
    lignes = [lecteur.appel_generation(appel_id) for appel_id in brut.appel_ids]
    amorces = [lecteur.amorce_verifiee(amorce_id) for amorce_id in brut.amorce_ids]
    for amorce_id in brut.amorces_derivees:
        derivee = lecteur.amorce_verifiee(amorce_id)
        if derivee.auteur_contenu == "config":
            _exiger_amorce_liee(derivee, brut)
    entree = _entree(brut, amorces, lignes)
    if brut.tache == "generique":
        if not isinstance(entree, dict) or set(entree) != {"demande"}:
            raise DerivationRefusee(
                "entree_refusee", "Tâche generique : une amorce « demande » attendue"
            )
        debut: list[dict[str, Any]] = [{"role": "user", "content": entree["demande"]}]
    else:
        tache = taches.tache(brut.tache)
        try:
            if tache.outils_autorises:
                # Tâche à outils : début du Mode connecté (demande seule), le seul mode du
                # Harnais qui envoie `tools` ; même fonction que l'inférence (AD-6, AD-7).
                if not isinstance(entree, str):
                    raise EntreeInvalide(f"Tâche {brut.tache} : entrée texte attendue")
                debut = messages_connecte(tache, entree, None)
            else:
                debut = construire_messages(
                    tache,
                    entree,
                    lecteur.passages(brut) or None if brut.tache == "Q" else None,
                )
        except (EntreeInvalide, SlmspError) as exc:
            raise DerivationRefusee(
                "entree_refusee", f"Tâche {brut.tache} : entrée refusée : {exc}"
            ) from None
    if brut.tache == "RD":
        suite = _tours_outils(lecteur, brut, lignes)
        if suite[-1].get("role") != "assistant" or "tool_calls" in suite[-1]:
            raise DerivationRefusee(
                "conversation_invalide", "Tâche RD : réponse finale sans appel d'outil attendue"
            )
    else:
        suite = [{"role": "assistant", "content": _sortie(brut, amorces, lignes)}]
    messages = [*debut, *suite]
    try:
        valider_conversation(messages)
    except ConversationInvalide as exc:
        raise DerivationRefusee("conversation_invalide", f"conversation invalide : {exc}") from None
    return lignes, messages


def outils_de_ligne(ctx: ContexteBuild, code: str) -> list[dict[str, Any]]:
    """`tools` d'une ligne : ceux de `outils_autorises`, dans l'ordre du fichier d'outils.

    Même condition que le début de conversation (`construire_conversation`) et même filtre
    que l'inférence en Mode connecté (`harness.taches.recherche.traiter`).
    """
    if code == "generique":
        return []
    autorises = set(ctx.taches.tache(code).outils_autorises)
    return [dict(o) for o in ctx.outils if (o.get("function") or {}).get("name") in autorises]


def rederiver_ligne(ctx: ContexteBuild, brut: SessionBrute) -> LigneEntrainement:
    """Ligne d'entraînement de `brut`, refabriquée du journal et des amorces vérifiées.

    Lève `ProvenanceInvalide` (appel absent ou d'un autre usage, amorce falsifiée, résultat
    d'outil hors cassette, entrée incompatible avec la Tâche) ou une erreur de licence.
    """
    lignes, messages = construire_conversation(ctx.lecteur, ctx.taches, brut)

    versions: dict[str, int] = {}
    for ligne in lignes:
        if ligne.gabarit_id is None or ligne.version_gabarit is None:
            raise ProvenanceInvalide(f"appel {ligne.appel_id} : gabarit non journalisé")
        versions[ligne.gabarit_id] = ligne.version_gabarit
    sources = sources_de(ctx, brut)
    licences = [ctx.registre.source(source).licence for source in sources]
    modeles = sorted({ligne.modele_resolu or ligne.modele_demande for ligne in lignes})
    try:
        return LigneEntrainement(
            messages=messages,
            tools=outils_de_ligne(ctx, brut.tache),
            tache=brut.tache,
            meta=MetaLigne(
                generateur="+".join(modeles),
                appel_ids=list(brut.appel_ids),
                session_id=brut.session_id,
                version_gabarit=versions,
                version_extracteur=VERSION_EXTRACTEUR,
                source=sources,
                licence=licences,
                date=date.fromisoformat(lignes[-1].horodatage[:10]),
            ),
        )
    except (ValidationError, ValueError) as exc:
        raise ProvenanceInvalide(f"ligne {brut.session_id} non conforme : {exc}") from None


def serialiser(lignes: Sequence[LigneEntrainement]) -> bytes:
    """`train.jsonl` : une ligne de JSON canonique par exemple, LF final."""
    return b"".join(json_canonique(ligne.model_dump(mode="json")) + b"\n" for ligne in lignes)


def verifier_octets(octets: bytes, ctx: ContexteBuild, sessions: Sequence[SessionBrute]) -> None:
    """Compare octet par octet `octets` à une nouvelle re-dérivation des `sessions`.

    Lève `ProvenanceInvalide` si le nombre de lignes, l'une d'elles (altérée d'un octet) ou
    leur ordre diffère de ce que le journal et les amorces donnent.
    """
    recues = octets.split(b"\n")
    if recues and recues[-1] == b"":
        recues.pop()
    if len(recues) != len(sessions):
        raise ProvenanceInvalide(
            f"{len(recues)} ligne(s) pour {len(sessions)} exemple(s) retenu(s)"
        )
    for brut, recue in zip(sessions, recues, strict=True):
        attendue = json_canonique(rederiver_ligne(ctx, brut).model_dump(mode="json"))
        if recue != attendue:
            raise ProvenanceInvalide(
                f"session {brut.session_id} : ligne différente de sa re-dérivation"
            )


# --- Étape ---------------------------------------------------------------------------------------


def _numero_suivant(train: Path) -> int:
    existants = [
        int(m.group(1)) for dossier in train.iterdir() if (m := _RE_VERSION.fullmatch(dossier.name))
    ]
    return max(existants, default=0) + 1


def _creer_version(base: Path) -> tuple[str, Path]:
    """Crée `data/train/vN/` (N = plus grand N existant + 1) ; ne réécrit jamais une version."""
    train = base / "data" / "train"
    train.mkdir(parents=True, exist_ok=True)
    numero = _numero_suivant(train)
    while True:
        dossier = train / f"v{numero}"
        try:
            dossier.mkdir()
        except FileExistsError:
            numero += 1
            continue
        return f"v{numero}", dossier


def _ouvrir_filtre(filter_run_id: str, base: Path) -> tuple[Run, str, str]:
    filtre = ouvrir_run(filter_run_id, racine=base)
    if filtre.type != TYPE_RUN_FILTER:
        raise ManifesteInvalide(
            f"run {filter_run_id} : type {filtre.type!r}, {TYPE_RUN_FILTER} attendu"
        )
    if filtre.statut_courant() == "en_cours":
        raise ManifesteInvalide(f"run {filter_run_id} encore en cours")
    validate_id = filtre.manifeste.config.get("validate_run_id")
    generate_id = filtre.manifeste.config.get("generate_run_id")
    if not isinstance(validate_id, str) or not isinstance(generate_id, str):
        raise ManifesteInvalide(f"run {filter_run_id} : runs validate et generate parents inconnus")
    return filtre, validate_id, generate_id


def _rejets_amont(base: Path, *run_ids: str) -> dict[str, int]:
    motifs: Counter[str] = Counter()
    for run_id in run_ids:
        for ligne in ouvrir_run(run_id, racine=base).lire_jsonl(NOM_REJETS):
            if isinstance(ligne, Mapping) and isinstance(ligne.get("motif"), str):
                motifs[ligne["motif"]] += 1
    return dict(sorted(motifs.items()))


def lancer_build(
    *,
    racine: str | Path,
    filter_run_id: str,
    variante: str,
    journal: JournalMistral,
    registre: RegistreLicences,
    config: ConfigDonnees,
    taches: TableTaches,
    chemin_outils: Path,
    consigner: Callable[[str], None] = print,
) -> ResultatBuild:
    """Construit `data/train/vN/` depuis le run `data-filter` `filter_run_id`.

    Avant tout run et toute écriture : `ManifesteInvalide` (run absent, d'un autre type, en
    cours, ou sans exemple retenu), `SourceSansLicence`/`UsageInterdit` (variante), `ValueError`
    (variante inconnue). Pendant le run, `ProvenanceInvalide` (AC 1 et 2) clôt le run en
    `partiel-erreur` sans rien écrire sous `data/train/`. Un parent `filter` partiel rend le
    build partiel (`statut_herite`).
    """
    if variante not in VARIANTES:
        raise ValueError(f"variante inconnue : {variante!r} (attendu : {', '.join(VARIANTES)})")
    base = Path(racine).resolve()
    filtre, validate_id, generate_id = _ouvrir_filtre(filter_run_id, base)
    generation = ouvrir_generation(generate_id, base)
    lecteur = LecteurGeneration(generation, journal, base)
    try:
        sessions = [SessionBrute.model_validate(ligne) for ligne in filtre.lire_jsonl(NOM_RETENUS)]
    except ValidationError:
        raise ManifesteInvalide(f"run {filter_run_id} : {NOM_RETENUS} illisible") from None
    if not sessions:
        raise ManifesteInvalide(f"run {filter_run_id} : aucun exemple retenu à construire")
    ctx = ContexteBuild(
        lecteur=lecteur, taches=taches, outils=charger_outils(chemin_outils), registre=registre
    )

    # Licences : toute source absente du Registre, ou d'un usage refusé, fait échouer.
    sources: set[str] = set()
    for brut in sessions:
        sources.update(sources_de(ctx, brut))
    for source in sorted(sources):
        registre.exiger(source, variante)

    entrees = {"retenus": filtre.dossier / NOM_RETENUS, "outils-mcp": chemin_outils}
    run = nouveau_run(
        TYPE_RUN,
        "build",
        {
            "filter_run_id": filter_run_id,
            "validate_run_id": validate_id,
            "generate_run_id": generate_id,
            "variante": variante,
            "version_extracteur": VERSION_EXTRACTEUR,
            "registre_sha256": registre.sha256,
            "relecture": config.relecture.model_dump(mode="json"),
        },
        parents=[filter_run_id],
        entrees=entrees,
        racine=base,
    )
    try:
        lignes = [rederiver_ligne(ctx, brut) for brut in sessions]
        octets = serialiser(lignes)
        verifier_octets(octets, ctx, sessions)
    except KeyboardInterrupt:
        run.terminer("interrompu", "interruption clavier")
        raise
    except BaseException as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
        raise

    version, dossier = _creer_version(base)
    (dossier / NOM_TRAIN).write_bytes(octets)
    sha_train = sha256_fichier(dossier / NOM_TRAIN)
    if sha_train != sha256_hex(octets):
        raise ProvenanceInvalide(
            f"{dossier / NOM_TRAIN} : octets écrits différents des octets vérifiés"
        )

    statut, motif = statut_herite(filtre, "complet", None)
    comptes = dict(sorted(Counter(ligne.tache for ligne in lignes).items()))
    sha_gabarits: dict[str, str] = {}
    for brut in sessions:
        for appel_id in brut.appel_ids:
            ligne_appel = lecteur.appel(appel_id)
            assert ligne_appel.gabarit_id is not None and ligne_appel.sha256_gabarit is not None
            sha_gabarits[ligne_appel.gabarit_id] = ligne_appel.sha256_gabarit
    sha_prompts = {
        taches.tache(tache).prompt.id: taches.tache(tache).prompt.sha256
        for tache in comptes
        if tache != "generique"
    }
    mistral = config.mistral
    manifeste = ManifesteJeuEntrainement(
        version=version,
        variante=variante,  # type: ignore[arg-type]
        cree_le=date.today(),
        statut=statut,  # type: ignore[arg-type]
        run_id=run.run_id,
        filter_run_id=filter_run_id,
        validate_run_id=validate_id,
        generate_run_id=generate_id,
        sha256_train=sha_train,
        nb_lignes=len(lignes),
        comptes_par_tache=comptes,
        rejets_par_motif=_rejets_amont(base, validate_id, filter_run_id),
        registre=registre.instantane(),
        sha_gabarits=dict(sorted(sha_gabarits.items())),
        sha_prompts=dict(sorted(sha_prompts.items())),
        sha_outils_mcp=sha256_fichier(chemin_outils),
        conditions_mistral=ConditionsMistral(
            verifiees_le=mistral.conditions_verifiees_le,
            url=mistral.conditions_url,
            sha256=mistral.conditions_sha256,
        ),
        modeles_generateurs=sorted(
            {m for ligne in lignes for m in ligne.meta.generateur.split("+")}
        ),
        version_extracteur=VERSION_EXTRACTEUR,
        mode_outils=MODE_OUTILS,
    )
    (dossier / NOM_MANIFEST).write_bytes(json_canonique(manifeste.model_dump(mode="json")) + b"\n")

    # Échantillon de relecture humaine, non bloquant : tirage reproductible (graine du config).
    taille = min(config.relecture.taille_echantillon, len(lignes))
    for rang in sorted(random.Random(config.relecture.graine).sample(range(len(lignes)), taille)):
        run.ajouter_jsonl(NOM_ECHANTILLON, {"rang": rang, **lignes[rang].model_dump(mode="json")})
    rapport = {
        "schema_version": 1,
        "statut": statut,
        "motif": motif,
        "version": version,
        "variante": variante,
        "sha256_train": sha_train,
        "nb_lignes": len(lignes),
        "comptes_par_tache": comptes,
        "rejets_par_motif": manifeste.rejets_par_motif,
        "echantillon_relecture": taille,
    }
    run.ecrire(NOM_RAPPORT, json_canonique(rapport) + b"\n")
    run.terminer(statut, motif)
    consigner(f"build {version} ({variante}) : {len(lignes)} lignes, sha256 {sha_train}")
    return ResultatBuild(run=run, statut=statut, version=version, dossier=dossier, rapport=rapport)
