"""`AssistantService` : point d'entrée unique du Harnais (AD-14, AD-7, FR-1).

Le service est sans état : l'appelant fournit et conserve toute la conversation
(`messages`, sans `system`, terminée par un message `user`). `repondre` valide tout de
suite la Tâche, la conversation, les options et l'entrée, et lève `SlmspError` pour une
erreur de l'appelant ; il renvoie ensuite un générateur d'évènements de
`core.evenements`. Le traitement de la Tâche (`harness.taches`, chargé paresseusement)
ne s'exécute qu'à l'itération.

Entrée de la Tâche : `options["entree"]` (chaîne ou dict, utilisé tel quel, cas du banc)
ou, à défaut, le contenu du dernier message `user` ; pour une Tâche à entrée objet, il
remplit le premier emplacement de contenu du prompt (`CLES_CONTENU`). `entree` est retiré
des options transmises au `LlmPort`.

Erreurs d'exécution (modèle, embedder, Index) : un évènement `Erreur` sans détail clôt
le flux ; le détail part au logger `slmsp.harness`, avec la classe de l'exception, son
message aux textes saisis masqués et la pile sans variables locales. Un dépassement du
contexte du Modèle (`ContexteDepasse`, levée par le budget de prompt ou par le client
llama-server) donne `Erreur(contexte-depasse)`, journalisée en avertissement sans pile ;
toute autre exception donne `Erreur(erreur-interne)`.

Longueur de sortie (correctif F2) : sans `max_tokens` dans les options, le service le fixe à
`config.compte_rendu.reserve_sortie_tokens` pour le compte rendu, à
`config.generation.par_tache[code]` s'il existe, à un plafond proportionnel au prompt pour
les Tâches de réécriture (`generation.reecriture`, calculé par `redaction`), à
`config.generation.max_tokens` sinon (`max_tokens_par_defaut`). Le flux se termine
toujours par un `Fin` ou un `Erreur`. Le délai au premier token (`delai_premier_token_ms`
de `Fin.usage`) est mesuré depuis le début de l'itération : il compte la recherche et les
mesures du budget de prompt (`harness.budget`).
"""

from __future__ import annotations

import copy
import json
import logging
import traceback
from collections.abc import Iterator, Mapping, Sequence
from time import perf_counter
from types import MappingProxyType
from typing import Any, Final

from slmsp.core.erreurs import ContexteDepasse
from slmsp.core.evenements import (
    AppelNonConforme,
    AppelOutil,
    Avertissement,
    Erreur,
    Evenement,
    Fin,
    Jeton,
    Progression,
    Repli,
    ResultatOutil,
    Sources,
)
from slmsp.core.messages import (
    ConversationInvalide,
    MessageSysteme,
    MessageUtilisateur,
    valider_conversation,
    vers_dicts,
)
from slmsp.core.ports import EmbedderPort, LlmPort, ModePort, ToolPort, VectorStore
from slmsp.harness.citations import chaines
from slmsp.harness.config import ConfigHarnais, charger_config_harnais
from slmsp.harness.prompts import CLES_CONTENU, EntreeInvalide, construire_messages
from slmsp.harness.recherche_index import RechercheIndex
from slmsp.harness.taches import (
    MODULES_TRAITEMENT,
    ContexteTache,
    TableTaches,
    Tache,
    TacheIndisponible,
    Traitement,
    charger_taches,
    traitement,
)

LOGGER: Final = logging.getLogger("slmsp.harness")

CODE_ERREUR: Final = "erreur-interne"
MESSAGE_ERREUR: Final = "Un problème est survenu. Votre texte est conservé."
CODE_CONTEXTE: Final = "contexte-depasse"
MESSAGE_CONTEXTE: Final = (
    "La demande est trop longue pour le modèle. Raccourcissez le texte ou commencez une "
    "nouvelle conversation. Votre texte est conservé."
)
CLE_MAX_TOKENS: Final = "max_tokens"
MODULE_COMPTE_RENDU: Final = "compte_rendu"
MASQUE: Final = "<texte saisi masqué>"
LONGUEUR_MIN_MASQUE: Final = 4
"""Les fragments saisis plus courts ne sont pas masqués (ils ne révèlent rien)."""

CLE_ENTREE: Final = "entree"

_TYPES_EVENEMENTS: Final = (
    Jeton,
    AppelOutil,
    ResultatOutil,
    AppelNonConforme,
    Sources,
    Avertissement,
    Progression,
    Repli,
    Fin,
    Erreur,
)


def masquer(texte: str, textes_saisis: Sequence[str]) -> str:
    """Remplace dans `texte` chaque texte saisi (et chacune de ses lignes) par `MASQUE`.

    Les formes échappées par `repr` et par `json.dumps` sont masquées aussi.
    """
    fragments: set[str] = set()
    for saisi in textes_saisis:
        for fragment in (saisi, *saisi.splitlines()):
            fragment = fragment.strip()
            if len(fragment) >= LONGUEUR_MIN_MASQUE:
                fragments.add(fragment)
                fragments.add(repr(fragment)[1:-1])
                fragments.add(json.dumps(fragment)[1:-1])
    for fragment in sorted(fragments, key=len, reverse=True):
        texte = texte.replace(fragment, MASQUE)
    return texte


class AssistantService:
    """Harnais de l'Assistant : `repondre(tache, messages, options)` → évènements.

    Les ports sont injectés par la racine de composition. `outils` et `mode` ne sont
    transmis qu'aux Tâches qui déclarent des outils (RD, story 4.3) ; la recherche dans
    l'Index (`embedder` et `vector_store`) ne sert qu'aux Tâches dont le prompt prévoit
    des passages.
    """

    def __init__(
        self,
        llm: LlmPort,
        embedder: EmbedderPort | None,
        vector_store: VectorStore | None,
        outils: ToolPort | None = None,
        mode: ModePort | None = None,
        config: ConfigHarnais | None = None,
        *,
        taches: TableTaches | None = None,
    ) -> None:
        self.llm = llm
        self.outils = outils
        self.mode = mode
        self.config = config if config is not None else charger_config_harnais()
        self.taches = taches if taches is not None else charger_taches()
        self.recherche = (
            RechercheIndex(
                embedder,
                vector_store,
                self.config.recherche.k,
                self.config.recherche.seuil_pertinence,
            )
            if embedder is not None and vector_store is not None
            else None
        )

    # --- Validation (au moment de l'appel) ---------------------------------------------

    def _tache(self, tache: str | Tache | None) -> Tache:
        if tache is None:
            fiche = self.taches.defaut
        elif isinstance(tache, Tache):
            fiche = tache
        else:
            fiche = self.taches.tache(tache)
        if not fiche.actif:
            raise TacheIndisponible(f"Tâche {fiche.code} inactive")
        return fiche

    @staticmethod
    def _conversation(messages: Any) -> list[dict[str, Any]]:
        if isinstance(messages, (str, bytes, Mapping)) or messages is None:
            raise ConversationInvalide("conversation attendue : liste de messages")
        liste = list(messages)
        if not liste:
            raise ConversationInvalide("conversation vide")
        valides = valider_conversation(liste)
        for indice, message in enumerate(valides):
            if isinstance(message, MessageSysteme):
                raise ConversationInvalide(
                    f"message {indice} invalide : le message system est composé par le Harnais"
                )
        if not isinstance(valides[-1], MessageUtilisateur):
            raise ConversationInvalide("le dernier message doit être un message user")
        return vers_dicts(valides)

    @staticmethod
    def _options(options: Mapping[str, Any] | None) -> dict[str, Any]:
        if options is None:
            return {}
        if not isinstance(options, Mapping):
            raise EntreeInvalide("options : dict attendu")
        return dict(options)

    @staticmethod
    def _entree(
        fiche: Tache, dernier: Mapping[str, Any], options: Mapping[str, Any]
    ) -> str | dict[str, Any]:
        if CLE_ENTREE in options:
            entree = options[CLE_ENTREE]
            if isinstance(entree, str):
                return entree
            if isinstance(entree, Mapping):
                return copy.deepcopy(dict(entree))
            raise EntreeInvalide(f"Tâche {fiche.code} : « entree » doit être un texte ou un dict")
        contenu = dernier["content"]
        if fiche.prompt.entree_texte:
            return contenu
        cle = next((nom for nom in fiche.prompt.emplacements if nom in CLES_CONTENU), None)
        if cle is None:  # pragma: no cover - garde-fou : tout prompt objet a un contenu
            raise EntreeInvalide(f"Tâche {fiche.code} : aucun emplacement de contenu")
        return {cle: contenu}

    # --- Point d'entrée -----------------------------------------------------------------

    def repondre(
        self,
        tache: str | Tache | None = None,
        messages: Sequence[Mapping[str, Any]] = (),
        options: Mapping[str, Any] | None = None,
    ) -> Iterator[Evenement]:
        """Évènements de la réponse à la conversation `messages` pour la Tâche `tache`.

        `tache` vaut Q (`defaut` de la table) si `None`. Lève tout de suite
        `TacheInconnue`, `TacheIndisponible` (Tâche inactive, module de traitement
        absent, Index absent), `ConversationInvalide` (vide, avec `system`, dernier
        message non `user`, forme invalide) ou `EntreeInvalide`.
        """
        fiche = self._tache(tache)
        traiter = traitement(fiche.code)
        conversation = self._conversation(messages)
        brutes = self._options(options)
        entree = self._entree(fiche, conversation[-1], brutes)
        # Validation de l'entrée par la construction unique (AD-7) : même règle, même erreur.
        construire_messages(fiche, entree)
        avec_passages = "passages" in fiche.prompt.emplacements
        if avec_passages and self.recherche is None:
            raise TacheIndisponible(f"Tâche {fiche.code} : aucun Index local fourni")
        avec_outils = bool(fiche.outils_autorises)
        saisis = [m["content"] for m in conversation if m["role"] == "user"]
        saisis.extend(chaines(entree, cles=False))
        brutes.pop(CLE_ENTREE, None)
        defaut = self.max_tokens_par_defaut(fiche)
        if defaut is not None:
            brutes.setdefault(CLE_MAX_TOKENS, defaut)
        ctx = ContexteTache(
            tache=fiche,
            entree=entree,
            historique=tuple(conversation[:-1]),
            textes_saisis=tuple(dict.fromkeys(saisis)),
            llm=self.llm,
            config=self.config,
            options_llm=MappingProxyType(brutes),
            recherche=self.recherche if avec_passages else None,
            outils=self.outils if avec_outils else None,
            mode=self.mode if avec_outils else None,
        )
        return self._flux(traiter, ctx)

    def max_tokens_par_defaut(self, fiche: Tache) -> int | None:
        """`max_tokens` posé quand l'appelant n'en fixe pas.

        Réserve du compte rendu pour CR ; `generation.par_tache[code]` s'il existe ; `None`
        pour une Tâche de `generation.reecriture` (plafond proportionnel au prompt, calculé
        par le traitement) ; sinon `generation.max_tokens`.
        """
        generation = self.config.generation
        if MODULES_TRAITEMENT.get(fiche.code) == MODULE_COMPTE_RENDU:
            return self.config.compte_rendu.reserve_sortie_tokens
        if fiche.code in generation.par_tache:
            return generation.par_tache[fiche.code]
        if fiche.code in generation.reecriture:
            return None
        return generation.max_tokens

    # --- Flux -----------------------------------------------------------------------------

    def _flux(self, traiter: Traitement, ctx: ContexteTache) -> Iterator[Evenement]:
        debut = perf_counter()
        premier: float | None = None
        flux: Iterator[Evenement] | None = None
        try:
            flux = traiter(ctx)
            for evenement in flux:
                if not isinstance(evenement, _TYPES_EVENEMENTS):
                    raise TypeError(f"évènement hors core.evenements : {type(evenement).__name__}")
                if isinstance(evenement, Jeton) and premier is None:
                    premier = perf_counter()
                if isinstance(evenement, Fin):
                    yield self._avec_delai(evenement, debut, premier)
                    return
                yield evenement
                if isinstance(evenement, Erreur):
                    return
            raise RuntimeError("traitement terminé sans évènement Fin")
        except ContexteDepasse as exc:
            self._journaliser(exc, ctx, pile=False)
            yield Erreur(code=CODE_CONTEXTE, message=MESSAGE_CONTEXTE)
        except Exception as exc:
            self._journaliser(exc, ctx)
            yield Erreur(code=CODE_ERREUR, message=MESSAGE_ERREUR)
        finally:
            fermer = getattr(flux, "close", None)
            if callable(fermer):
                fermer()

    @staticmethod
    def _avec_delai(fin: Fin, debut: float, premier: float | None) -> Fin:
        usage = dict(fin.usage or {})
        if premier is not None:
            usage["delai_premier_token_ms"] = round((premier - debut) * 1000)
        return fin.model_copy(update={"usage": usage or None})

    @staticmethod
    def _journaliser(exc: Exception, ctx: ContexteTache, *, pile: bool = True) -> None:
        message = masquer(str(exc), ctx.textes_saisis)
        if not pile:
            LOGGER.warning("Tâche %s : %s : %s", ctx.tache.code, type(exc).__name__, message)
            return
        trace = "".join(traceback.format_tb(exc.__traceback__))
        LOGGER.error(
            "Tâche %s : %s : %s\n%s", ctx.tache.code, type(exc).__name__, message, trace.rstrip()
        )


__all__ = [
    "CODE_CONTEXTE",
    "CODE_ERREUR",
    "MESSAGE_CONTEXTE",
    "MESSAGE_ERREUR",
    "AssistantService",
    "masquer",
]
