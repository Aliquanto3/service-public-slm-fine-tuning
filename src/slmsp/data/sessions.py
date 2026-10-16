"""Exécution d'une session de génération de l'étape `generate` (story 9.4, AD-17, AD-26).

Une session (`SessionPlanifiee`) est exécutée selon sa Tâche :

- **un appel** (Q, LC, CO, RE, CT, generique) : le gabarit de la Tâche, rempli par les
  amorces du seed ; pour Q, l'emplacement `passages` vient du `ResolveurPassages` injecté
  dans le Générateur (passages retenus au plan, formatés par `harness.prompts`) ;
- **CR en deux temps** : `transcription-cr` sur le scénario, puis la transcription devient
  une amorce dérivée (`Generateur.deriver_amorce`, consignée dans `amorces-derivees.jsonl`)
  et `cr` produit le compte rendu ;
- **RD** : tant que Mistral émet des `tool_calls`, chaque tour est contrôlé en entier
  (`valider_appel` contre `config/outils-mcp.toml`, identifiants protégés du Jeu
  d'évaluation) avant tout envoi, exécuté par le port d'outils (`McpEnDirect` profil
  `outillage`) et enregistré par `mcp.enregistrer(…, "data")` sous
  `data/cassettes/<session_id>.t<k>.json` ; les résultats repartent au Générateur en
  messages `assistant` et `tool` qu'il revérifie (verrou 3).

**Aucun appel n'est repayé** : avant chaque appel, le journal Mistral (lecteur `data`) est
parcouru à la recherche d'une ligne `generation`/`ok` d'un modèle stable, de même gabarit
(identifiant, version, SHA), mêmes amorces et mêmes messages précédents ; sa réponse est
alors réutilisée. Un tour d'outils dont la cassette existe déjà est relu, jamais rejoué.

Ce module ne contient aucun texte : il ne manipule que des identifiants et des réponses
journalisées (D1.1). Les pannes de transport MCP lèvent `IncidentOutils` (session réessayée
à la reprise) ; les fins sans exemple deviennent une `AbandonSession` avec son motif.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import AbstractContextManager, ExitStack
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final, Protocol

from pydantic import ValidationError

from slmsp.core.artefacts import Run, lire
from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import AppelNonConforme, HoteBloque, ProvenanceInvalide
from slmsp.core.items import IdentifiantsProteges
from slmsp.core.ports import Passage
from slmsp.core.schemas.cassette import Cassette
from slmsp.core.schemas.session_donnees import (
    AbandonSession,
    PassagePlan,
    RefGabarit,
    SessionBrute,
    SessionPlanifiee,
)
from slmsp.harness.prompts import formater_passages
from slmsp.harness.taches.recherche import contenu_resultat
from slmsp.mcp.enregistrement import SessionMcp, chemin_cassette, enregistrer
from slmsp.mcp.erreurs import ErreurTransportMcp
from slmsp.mcp.outils import valider_appel
from slmsp.mistral.generateur import (
    TACHES_OUTILLEES,
    Generateur,
    message_assistant,
    raison_de_fin,
)
from slmsp.mistral.journal import USAGE_GENERATION, JournalMistral, LigneAppel

__all__ = [
    "Abandon",
    "Compteur",
    "ContexteSessions",
    "ExecuteurSessions",
    "IncidentOutils",
    "ResolveurPassages",
    "SessionOutils",
    "passage_depuis_plan",
]

TOURS_OUTILS_MAX: Final = 4
"""Tours d'outils admis par session RD avant l'abandon `tours_max`."""
NOM_AMORCES_DERIVEES: Final = "amorces-derivees.jsonl"
EMPLACEMENT_TRANSCRIPTION: Final = "transcription"
ARGUMENTS_IDENTIFIANTS: Final = ("dataset_id", "resource_id")


class SessionOutils(Protocol):
    """Port d'outils d'une session RD (`McpEnDirect` ouvert, ou doublure de test)."""

    def appeler(self, nom: str, arguments: Mapping[str, Any]) -> dict[str, Any]: ...

    def session(self, *, item: str | None = None, session_id: str | None = None) -> SessionMcp: ...


OuvrirOutils = Callable[[], AbstractContextManager[SessionOutils]]


class Abandon(Exception):
    """Fin de session sans exemple ; `motif` parmi `MOTIFS_ABANDON`."""

    def __init__(self, motif: str, detail: str) -> None:
        super().__init__(detail)
        self.motif = motif
        self.detail = detail


class IncidentOutils(Exception):
    """Panne de transport MCP : la session sera réessayée à la reprise."""

    def __init__(self, cause: BaseException) -> None:
        super().__init__(str(cause) or type(cause).__name__)
        self.type = type(cause).__name__


def passage_depuis_plan(passage: PassagePlan) -> Passage:
    return Passage(**passage.model_dump())


class ResolveurPassages:
    """Rendu des passages par session, injecté dans le Générateur (`rendre_passages`).

    Rempli depuis le plan : aucune recherche n'a lieu pendant la génération ni à la reprise.
    """

    def __init__(self) -> None:
        self._passages: dict[str, tuple[Passage, ...]] = {}

    def definir(self, session_id: str, passages: Sequence[Passage]) -> None:
        self._passages[session_id] = tuple(passages)

    def __call__(self, session_id: str) -> str:
        if session_id not in self._passages:
            raise ProvenanceInvalide(f"session {session_id!r} : passages absents du plan")
        return formater_passages(self._passages[session_id])


@dataclass
class Compteur:
    """Ce qu'une session a produit ou dépensé, même interrompue."""

    appel_ids: list[str] = field(default_factory=list)
    cassettes: list[str] = field(default_factory=list)
    amorces_derivees: list[str] = field(default_factory=list)
    nouveaux: int = 0
    reutilises: int = 0
    cout_eur: float = 0.0


@dataclass
class ContexteSessions:
    """Dépendances communes aux sessions d'un run."""

    generateur: Generateur
    journal: JournalMistral
    """Journal Mistral ouvert en lecture (`lecteur="data"`)."""
    racine: Path
    run: Run
    ouvrir_outils: OuvrirOutils
    proteges: IdentifiantsProteges
    chemin_outils: Path
    tours_outils_max: int = TOURS_OUTILS_MAX
    index_version: str | None = None


def _projection(messages: Sequence[Any]) -> bytes:
    """Messages réduits à ce qui fait leur identité : `content` et appels d'outil
    (`id`, nom, arguments décodés) d'un `assistant`, (`tool_call_id`, `content`) d'un
    `tool`. Les champs ajoutés par le SDK à la sérialisation sont ignorés."""
    projetes: list[Any] = []
    for message in messages:
        if not isinstance(message, Mapping):
            projetes.append(None)
            continue
        role = message.get("role")
        if role == "assistant":
            appels = []
            for appel in message.get("tool_calls") or ():
                fonction = appel.get("function") if isinstance(appel, Mapping) else None
                fonction = fonction if isinstance(fonction, Mapping) else {}
                arguments = fonction.get("arguments")
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except ValueError:
                        pass
                appels.append([appel.get("id"), fonction.get("name"), arguments])
            projetes.append(["assistant", message.get("content") or None, appels])
        elif role == "tool":
            projetes.append(["tool", message.get("tool_call_id"), message.get("content")])
        else:
            projetes.append([role, message.get("content")])
    return json_canonique(projetes)


def _chaines(valeur: Any) -> Iterator[str]:
    if isinstance(valeur, str):
        yield valeur
    elif isinstance(valeur, Mapping):
        for sous in valeur.values():
            yield from _chaines(sous)
    elif isinstance(valeur, list):
        for sous in valeur:
            yield from _chaines(sous)


class ExecuteurSessions:
    """Exécute les sessions d'un run (voir le module)."""

    def __init__(self, contexte: ContexteSessions) -> None:
        self.ctx = contexte
        self._derivees = {
            ligne.get("amorce_id")
            for ligne in contexte.run.lire_jsonl(NOM_AMORCES_DERIVEES)
            if isinstance(ligne, dict)
        }
        self._ids_proteges = contexte.proteges.dataset_ids | contexte.proteges.resource_ids

    # --- Session ---------------------------------------------------------------------------

    def executer(
        self, session: SessionPlanifiee, compteur: Compteur
    ) -> SessionBrute | AbandonSession:
        """Exécute `session` ; `compteur` reflète les appels et cassettes, même en cas
        d'exception (`BudgetEpuise`, `ErreurApiMistral`, `IncidentOutils`…, propagées)."""
        try:
            if session.tache in TACHES_OUTILLEES:
                self._trace_outils(session, compteur)
            elif len(session.gabarits) == 2:
                self._deux_temps(session, compteur)
            else:
                self._appel_final(session, compteur, session.gabarits[0], session.amorce_ids)
        except Abandon as abandon:
            motif, detail = abandon.motif, abandon.detail
        except (ProvenanceInvalide, AppelNonConforme) as exc:
            motif, detail = "provenance_invalide", str(exc)
        else:
            return SessionBrute(
                session_id=session.session_id,
                tache=session.tache,
                appel_ids=compteur.appel_ids,
                amorce_ids=session.amorce_ids,
                amorces_derivees=compteur.amorces_derivees,
                cassettes=compteur.cassettes,
                passages=(
                    None
                    if session.passages is None
                    else [passage.chunk_id for passage in session.passages]
                ),
                index_version=self.ctx.index_version if session.passages is not None else None,
                appels_nouveaux=compteur.nouveaux,
                appels_reutilises=compteur.reutilises,
            )
        return AbandonSession(
            session_id=session.session_id,
            tache=session.tache,
            motif=motif,  # type: ignore[arg-type]
            detail=detail,
            appel_ids=compteur.appel_ids,
            cassettes=compteur.cassettes,
        )

    def _appel_final(
        self,
        session: SessionPlanifiee,
        compteur: Compteur,
        gabarit: RefGabarit,
        amorce_ids: Sequence[str],
    ) -> dict[str, Any]:
        message = self._obtenir(session, compteur, gabarit, amorce_ids, [])
        if "tool_calls" in message or "content" not in message:
            raise Abandon("sans_contenu", f"gabarit {gabarit.id} : réponse sans contenu texte seul")
        return message

    def _deux_temps(self, session: SessionPlanifiee, compteur: Compteur) -> None:
        """CR : transcription, amorce dérivée, puis compte rendu (dernier appel = final)."""
        premier, second = session.gabarits
        self._appel_final(session, compteur, premier, session.amorce_ids)
        derivee = self.ctx.generateur.deriver_amorce(
            compteur.appel_ids[-1],
            amorce_id=f"{session.session_id}.{EMPLACEMENT_TRANSCRIPTION}",
            tache=session.tache,
            emplacement=EMPLACEMENT_TRANSCRIPTION,
        )
        if derivee.amorce_id not in self._derivees:
            self.ctx.run.ajouter_jsonl(NOM_AMORCES_DERIVEES, derivee.model_dump(mode="json"))
            self._derivees.add(derivee.amorce_id)
        compteur.amorces_derivees.append(derivee.amorce_id)
        self._appel_final(session, compteur, second, [derivee.amorce_id])

    # --- Appel (réutilisé ou nouveau) -------------------------------------------------------

    def _reutilisable(
        self,
        session: SessionPlanifiee,
        gabarit: RefGabarit,
        amorce_ids: Sequence[str],
        precedents: Sequence[Mapping[str, Any]],
    ) -> tuple[LigneAppel, dict[str, Any]] | None:
        """Première ligne du journal de la session qui répond déjà à cet appel."""
        stables = self.ctx.generateur.prealables.modeles_stables
        ids = json_canonique(list(amorce_ids)).decode("utf-8")
        cible = _projection(precedents)
        if not self.ctx.journal.chemin.is_file():  # aucun appel encore journalisé
            return None
        for ligne in self.ctx.journal.appels_session(session.session_id):
            if (
                ligne.usage != USAGE_GENERATION
                or ligne.statut != "ok"
                or ligne.modele_resolu not in stables
                or (ligne.gabarit_id, ligne.version_gabarit, ligne.sha256_gabarit)
                != (gabarit.id, gabarit.version, gabarit.sha256)
                or ligne.amorce_ids != ids
            ):
                continue
            try:
                messages = json.loads(ligne.requete)["messages"]
                message = message_assistant(ligne.reponse_brute)
            except (ValueError, KeyError, TypeError, ProvenanceInvalide):
                continue
            if not isinstance(messages, list) or len(messages) != 1 + len(precedents):
                continue
            if _projection(messages[1:]) == cible:
                return ligne, message
        return None

    def _obtenir(
        self,
        session: SessionPlanifiee,
        compteur: Compteur,
        gabarit: RefGabarit,
        amorce_ids: Sequence[str],
        precedents: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        trouve = self._reutilisable(session, gabarit, amorce_ids, precedents)
        if trouve is not None:
            ligne, message = trouve
            appel_id, fin = ligne.appel_id, raison_de_fin(ligne.reponse_brute)
            compteur.reutilises += 1
        else:
            actuel = self.ctx.generateur.gabarit(gabarit.id, session.tache)
            if (actuel.version, actuel.sha256) != (gabarit.version, gabarit.sha256):
                raise ProvenanceInvalide(f"gabarit {gabarit.id} modifié depuis le plan")
            generation = self.ctx.generateur.generer(
                gabarit.id, list(amorce_ids), session.session_id, session.tache, precedents or None
            )
            compteur.nouveaux += 1
            compteur.cout_eur += generation.reponse.cout_eur
            appel_id, fin = generation.appel_id, generation.reponse.finish_reason
            message = message_assistant(generation.reponse_brute)
        compteur.appel_ids.append(appel_id)
        if fin == "length":
            raise Abandon("reponse_tronquee", f"appel {appel_id} : réponse tronquée (length)")
        return message

    # --- RD : tours d'outils ---------------------------------------------------------------

    def _trace_outils(self, session: SessionPlanifiee, compteur: Compteur) -> None:
        gabarit = session.gabarits[0]
        precedents: list[dict[str, Any]] = []
        tour = 0
        with ExitStack() as pile:
            ouverts: list[Any] = []  # [port, nombre d'appels déjà exécutés sur la connexion]
            while True:
                message = self._obtenir(session, compteur, gabarit, session.amorce_ids, precedents)
                appels = message.get("tool_calls")
                if not appels:
                    if tour == 0:
                        raise Abandon("sans_appel_outil", "réponse finale sans aucun appel d'outil")
                    return
                tour += 1
                if tour > self.ctx.tours_outils_max:
                    raise Abandon(
                        "tours_max", f"plus de {self.ctx.tours_outils_max} tours d'outils"
                    )
                decodes = self._controler(appels)
                identifiant = f"{session.session_id}.t{tour}"
                chemin = chemin_cassette("data", identifiant, racine=self.ctx.racine)
                relatif = chemin.relative_to(self.ctx.racine).as_posix()
                if chemin.is_file():
                    reponses = self._relire(chemin, decodes)
                else:
                    reponses = self._executer(pile, ouverts, identifiant, decodes)
                compteur.cassettes.append(relatif)
                for reponse in reponses:
                    if not isinstance(reponse, Mapping) or "result" not in reponse:
                        raise Abandon("erreur_outil", f"tour {tour} : réponse d'outil en erreur")
                precedents = [
                    *precedents,
                    message,
                    *(
                        {
                            "role": "tool",
                            "tool_call_id": appel_id,
                            "name": nom,
                            "content": contenu_resultat(reponse),
                        }
                        for (appel_id, nom, _), reponse in zip(decodes, reponses, strict=True)
                    ),
                ]

    def _controler(self, appels: Sequence[Any]) -> list[tuple[str, str, dict[str, Any]]]:
        """Appels décodés et validés, tous avant le moindre envoi."""
        decodes: list[tuple[str, str, dict[str, Any]]] = []
        for appel in appels:
            fonction = appel.get("function") if isinstance(appel, Mapping) else None
            if not isinstance(fonction, Mapping) or not isinstance(appel.get("id"), str):
                raise Abandon("appel_non_conforme", "appel d'outil mal formé")
            nom, arguments = fonction.get("name"), fonction.get("arguments")
            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except ValueError:
                    raise Abandon("appel_non_conforme", f"{nom} : JSON illisible") from None
            if not isinstance(nom, str) or not isinstance(arguments, dict):
                raise Abandon("appel_non_conforme", "appel d'outil sans nom ou sans objet")
            try:
                valider_appel(nom, arguments, chemin=self.ctx.chemin_outils)
            except AppelNonConforme as exc:
                raise Abandon("appel_non_conforme", str(exc)) from None
            decodes.append((appel["id"], nom, arguments))
        for _, nom, arguments in decodes:
            if any(valeur in self._ids_proteges for valeur in _chaines(arguments)):
                raise Abandon(
                    "fuite_identifiant", f"{nom} : identifiant du Jeu d'évaluation en argument"
                )
        return decodes

    def _relire(
        self, chemin: Path, decodes: Sequence[tuple[str, str, dict[str, Any]]]
    ) -> list[dict[str, Any]]:
        """Réponses d'un tour déjà enregistré, si la cassette répond appel par appel."""
        try:
            cassette = Cassette.model_validate_json(lire(chemin, "data", racine=self.ctx.racine))
        except (OSError, ValidationError):
            raise Abandon("cassette_incoherente", f"{chemin.name} illisible") from None
        interactions = [i for i in cassette.interactions if i.request.get("method") == "tools/call"]
        if len(interactions) != len(decodes):
            raise Abandon("cassette_incoherente", f"{chemin.name} : nombre d'appels différent")
        reponses = []
        for (_, nom, arguments), interaction in zip(decodes, interactions, strict=True):
            params = interaction.request.get("params")
            params = params if isinstance(params, Mapping) else {}
            if (
                params.get("name") != nom
                or json_canonique(params.get("arguments", {})) != json_canonique(arguments)
                or interaction.response is None
            ):
                raise Abandon("cassette_incoherente", f"{chemin.name} : appel différent")
            reponses.append(interaction.response)
        return reponses

    def _executer(
        self,
        pile: ExitStack,
        ouverts: list[Any],
        identifiant: str,
        decodes: Sequence[tuple[str, str, dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        """Exécute un tour sur la connexion de la session (ouverte au premier tour exécuté)
        et enregistre son segment de cassette `<session_id>.t<k>.json`."""
        try:
            if not ouverts:
                ouverts.extend([pile.enter_context(self.ctx.ouvrir_outils()), 0])
            port, debut = ouverts
            reponses = [port.appeler(nom, arguments) for _, nom, arguments in decodes]
        except (ErreurTransportMcp, HoteBloque) as exc:
            raise IncidentOutils(exc) from exc
        enregistre = port.session(session_id=identifiant)
        segment = enregistre.cassette.model_copy(
            update={"interactions": enregistre.cassette.interactions[debut:]}
        )
        enregistrer(
            SessionMcp(cassette=segment, session_id=identifiant), "data", racine=self.ctx.racine
        )
        ouverts[1] = debut + len(decodes)
        return reponses
