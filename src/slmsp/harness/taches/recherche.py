"""Traitement de la Recherche de données (RD) : boucle d'outils, Modes et repli (FR-7 à FR-10).

MCP d'abord, puis l'Index en repli (AD-14). Mode : lu une fois au début (`ctx.mode` ou
`ctx.outils` absent : hors ligne).

- Mode connecté sans écart de schéma : les outils de `ctx.outils.lister_outils()`
  restreints à `tache.outils_autorises` sont passés au modèle (AD-8). Le premier tour est
  construit par `messages_connecte` (consigne de la Tâche et demande seule) : ni passages,
  ni recherche dans l'Index.
- Hors ligne, schéma dérivé, ou au premier repli : les messages sont reconstruits par
  `construire_messages` avec les passages du catalogue data.gouv (`passages_catalogue`),
  sans les tours d'outil précédents, et la génération se fait sans `tools`.

Le prompt vient toujours de `construire_messages` (AD-7) ; la boucle n'ajoute que les
tours d'outil : un message
`assistant` avec `tool_calls` (`appel_canonique`) et un message `tool` par appel, dont le
contenu est rendu par `contenu_resultat` (seule fonction de rendu, réutilisée par `data` et
`train`).

Par tour (au plus `config.outils.iterations_max`, puis une dernière génération sans
`tools`) : chaque `AppelOutil` du modèle est validé par `mcp.outils.valider_appel` ; s'il
est invalide il devient `AppelNonConforme` et n'est jamais envoyé. Un id d'appel déjà vu
dans la conversation est remplacé par `nouvel_identifiant()`. Avant chaque appel, le Mode
est re-sondé (`mode_avant_appel`) ; l'appel passe par `ToolPort.appeler` avec le délai
`config.outils.delai_appel_s`. `ResultatOutil.resultat` est le `result` (ou
`{"error": …}`) de la réponse JSON-RPC, copié tel quel ; l'`id` JSON-RPC n'entre pas dans
la trace.

Repli (FR-9) : délai dépassé, erreur HTTP, serveur injoignable, hôte bloqué, schéma
modifié, ou Mode perdu avant l'appel → `ResultatOutil(erreur=True)`, un seul évènement
`Repli(vers="index")` dont le motif dit « non vérifié en ligne », le détail au logger
`slmsp.harness` (classe et message, textes saisis masqués). Les appels restants du tour ne
sont pas envoyés (`ResultatOutil(erreur=True)`), puis une dernière génération sans outil
s'appuie sur les passages du catalogue. `Sources`, `urls_inventees` et l'avertissement
portent sur les passages effectivement fournis (aucun en connecté sans repli). Un schéma
dérivé connu du Mode
(`ecarts_schema`) donne le repli dès le début.

Ordre du flux : `[Repli]` (schéma dérivé), puis par tour `Jeton*`, `AppelOutil` ou
`AppelNonConforme`, puis par appel `ResultatOutil` (et `Repli` en cas de panne) ; enfin
`Sources`, `Avertissement(valeurs-mode-connecte)` si la réponse n'a pas été vérifiée en
ligne (hors ligne ou repli), et `Fin` avec `urls_inventees`. Le texte généré n'est jamais
réécrit et aucune valeur n'en est extraite.
"""

from __future__ import annotations

import copy
import dataclasses
import json
import logging
import re
import threading
from collections.abc import Generator, Iterator, Mapping, Sequence
from typing import Any, Final

from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import AppelNonConforme as AppelRefuse
from slmsp.core.erreurs import HoteBloque, SchemaOutilModifie
from slmsp.core.evenements import (
    AppelNonConforme,
    AppelOutil,
    Avertissement,
    Evenement,
    Fin,
    Repli,
    ResultatOutil,
    Source,
    Sources,
)
from slmsp.core.messages import valider_conversation
from slmsp.core.ports import Passage, ToolPort
from slmsp.harness.citations import (
    extraire_urls,
    normaliser_url,
    sources_citees,
    urls_inventees,
)
from slmsp.harness.modes import CONNECTE, ecarts_schema, mode_avant_appel, mode_courant
from slmsp.harness.prompts import construire_messages
from slmsp.harness.recherche_index import RechercheIndex
from slmsp.harness.service import masquer
from slmsp.harness.taches import ContexteTache, Tache, avertissement, diffuser
from slmsp.inference.client import appel_canonique, nouvel_identifiant
from slmsp.mcp.erreurs import DelaiDepasse, ErreurTransportMcp
from slmsp.mcp.outils import valider_appel

LOGGER: Final = logging.getLogger("slmsp.harness")

SOURCE_CATALOGUE: Final = "data-gouv-datasets-catalog"
"""`Passage.source` du catalogue data.gouv (`nom` de la source dans `config/index.toml`)."""

FACTEUR_RECHERCHE: Final = 4
"""Élargissement de la recherche (`k × FACTEUR`) avant le filtre sur le catalogue."""

LIBELLE_NON_VERIFIE: Final = "non vérifié en ligne"
"""Libellé fixe repris par la CLI et l'application (contenu dans chaque motif de repli)."""

MOTIF_PANNE: Final = (
    f"Résultat {LIBELLE_NON_VERIFIE} : data.gouv n'a pas répondu, "
    "la réponse s'appuie sur l'Index local."
)
MOTIF_MODE_PERDU: Final = (
    f"Résultat {LIBELLE_NON_VERIFIE} : le Mode connecté a été perdu, "
    "la réponse s'appuie sur l'Index local."
)
MOTIF_SCHEMA: Final = (
    f"Résultat {LIBELLE_NON_VERIFIE} : les outils de data.gouv ont changé, "
    "la réponse s'appuie sur l'Index local."
)

CODE_AVERTISSEMENT: Final = "valeurs-mode-connecte"
MESSAGE_AVERTISSEMENT: Final = (
    f"Résultat {LIBELLE_NON_VERIFIE} : les valeurs des jeux de données se consultent en "
    "Mode connecté ou par le lien du jeu de données."
)

MOTIF_NON_PROPOSE: Final = "outil non proposé pour cette Tâche"
"""Motif d'un appel conforme au schéma mais à un outil absent des `tools` du tour."""

TEXTE_ECHEC: Final = "Appel non abouti : data.gouv n'a pas répondu. Données non vérifiées en ligne."
"""Contenu du message `tool` d'un appel non abouti (phrase fixe, pas un exemple : D1.1)."""

_PANNES: Final = (ErreurTransportMcp, HoteBloque, SchemaOutilModifie)
_CLES_USAGE: Final = ("prompt_tokens", "completion_tokens", "total_tokens")
_TITRE_NUMEROTE: Final = re.compile(r"^\s*\d+\.\s+(\S.*?)\s*$")


# --- Passages du catalogue ----------------------------------------------------------------


def passages_catalogue(recherche: RechercheIndex | None, demande: str) -> list[Passage]:
    """Passages pertinents du catalogue data.gouv pour `demande`, au plus `recherche.k`.

    La recherche est élargie à `k × FACTEUR_RECHERCHE` passages (seuil de pertinence
    appliqué), puis filtrée sur `source == SOURCE_CATALOGUE`. Sans recherche : aucun passage.
    """
    if recherche is None:
        return []
    elargie = RechercheIndex(
        recherche.embedder,
        recherche.vector_store,
        recherche.k * FACTEUR_RECHERCHE,
        recherche.seuil,
    )
    passages = [p for p in elargie.rechercher(demande) if p.source == SOURCE_CATALOGUE]
    return passages[: recherche.k]


# --- Rendu des résultats -------------------------------------------------------------------


def _resultat_de(reponse: Any) -> tuple[Any, bool]:
    """`(resultat, erreur)` d'une réponse JSON-RPC, copiés tels quels."""
    if isinstance(reponse, Mapping) and "error" in reponse:
        return {"error": copy.deepcopy(reponse["error"])}, True
    if isinstance(reponse, Mapping) and "result" in reponse:
        resultat = copy.deepcopy(reponse["result"])
        erreur = not isinstance(resultat, Mapping) or bool(resultat.get("isError"))
        return resultat, erreur
    return copy.deepcopy(reponse), True


def contenu_resultat(reponse: Any) -> str:
    """Contenu du message `tool` d'un résultat d'outil (règle unique de rendu).

    `reponse` est une réponse JSON-RPC (`result` ou `error`), ou directement un
    `ResultatOutil.resultat` (`{"content": …}` ou `{"error": …}`). Le contenu est le texte
    des éléments `text` de `content`, joints par un saut de ligne (un autre élément est
    rendu en JSON compact) ; pour une erreur, son `message` (sinon l'erreur en JSON). Une
    réponse absente ou illisible donne `TEXTE_ECHEC`.
    """
    if isinstance(reponse, Mapping) and "result" in reponse and "content" not in reponse:
        reponse = reponse["result"]
    if isinstance(reponse, Mapping) and "error" in reponse and "content" not in reponse:
        erreur = reponse["error"]
        if isinstance(erreur, Mapping) and isinstance(erreur.get("message"), str):
            return erreur["message"]
        if isinstance(erreur, str) and erreur:
            return erreur
        return json.dumps(erreur, ensure_ascii=False, sort_keys=True)
    elements = reponse.get("content") if isinstance(reponse, Mapping) else None
    if not isinstance(elements, list):
        return TEXTE_ECHEC
    morceaux = []
    for element in elements:
        if isinstance(element, Mapping) and element.get("type") == "text":
            texte = element.get("text")
            morceaux.append(texte if isinstance(texte, str) else "")
        else:
            morceaux.append(json.dumps(element, ensure_ascii=False, sort_keys=True))
    return "\n".join(morceaux)


# --- Sources ---------------------------------------------------------------------------------


def _titre_dans(texte: str, url: str) -> str | None:
    """Titre du bloc (lignes non vides consécutives) de `texte` qui contient `url`."""
    for bloc in re.split(r"\n\s*\n", texte):
        if url not in bloc:
            continue
        for ligne in bloc.splitlines():
            trouve = _TITRE_NUMEROTE.match(ligne)
            if trouve:
                return trouve.group(1)
        return None
    return None


def sources_mcp(texte: str, resultats: Sequence[Any]) -> list[Source]:
    """Sources MCP : URL des résultats d'outils citées dans `texte`, dans l'ordre du texte.

    Le titre est la ligne numérotée (« 1. <titre> ») du bloc du résultat qui contient l'URL,
    sinon l'URL elle-même. Une URL n'apparaît qu'une fois.
    """
    connues: dict[str, tuple[str, str]] = {}
    for resultat in resultats:
        contenu = contenu_resultat(resultat)
        for url in extraire_urls(contenu):
            forme = normaliser_url(url)
            if forme not in connues:
                connues[forme] = (url, _titre_dans(contenu, url) or url)
    sources: list[Source] = []
    vues: set[str] = set()
    for url in extraire_urls(texte):
        forme = normaliser_url(url)
        if forme in vues or forme not in connues:
            continue
        vues.add(forme)
        url_resultat, titre = connues[forme]
        sources.append(Source(titre=titre, url=url_resultat, origine="mcp"))
    return sources


def sources_recherche(
    texte: str, passages: Sequence[Passage], resultats: Sequence[Any], non_verifie: bool
) -> list[Source]:
    """Passages cités `[n]` puis sources MCP citées ; sans citation et non vérifié en ligne,
    tous les passages du catalogue (le lien est toujours donné, FR-8)."""
    sources = [*sources_citees(texte, passages), *sources_mcp(texte, resultats)]
    if not sources and non_verifie:
        sources = sources_citees(
            "".join(f"[{numero}]" for numero in range(1, len(passages) + 1)), passages
        )
    return sources


# --- Appels d'outils ----------------------------------------------------------------------


def _appeler_avec_delai(
    outils: ToolPort, nom: str, arguments: Mapping[str, Any], delai: float
) -> Any:
    """`outils.appeler(nom, arguments)` ; lève `DelaiDepasse` au-delà de `delai` secondes.

    L'appel tourne dans un fil démon : au-delà du délai, sa réponse est abandonnée.
    """
    issue: dict[str, Any] = {}

    def executer() -> None:
        try:
            issue["reponse"] = outils.appeler(nom, dict(arguments))
        except BaseException as exc:  # relancée dans le fil appelant
            issue["erreur"] = exc

    fil = threading.Thread(target=executer, name=f"appel-outil-{nom}", daemon=True)
    fil.start()
    fil.join(delai)
    if fil.is_alive():
        raise DelaiDepasse(f"appel « {nom} » : délai de {delai:g} s dépassé")
    if "erreur" in issue:
        raise issue["erreur"]
    return issue.get("reponse")


def _arguments_bruts(arguments: Any) -> str:
    try:
        return json.dumps(arguments, ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError):
        return repr(arguments)


def _cumuler(usage: dict[str, int], fin: Fin) -> None:
    for cle, valeur in (fin.usage or {}).items():
        if cle in _CLES_USAGE:
            usage[cle] = usage.get(cle, 0) + valeur
        else:
            usage.setdefault(cle, valeur)


class _Boucle:
    """État d'une Recherche de données (un appel de `traiter`)."""

    def __init__(self, ctx: ContexteTache) -> None:
        self.ctx = ctx
        self.resultats: list[Any] = []
        self.repli = False
        self.deja_faits: dict[tuple[str, bytes], tuple[Any, bool]] = {}
        self.ids: set[str] = {
            appel.get("id")
            for message in ctx.historique
            for appel in (message.get("tool_calls") or ())
            if isinstance(appel, Mapping)
        }

    def journaliser(self, message: str, exc: BaseException | None = None) -> None:
        detail = f"{type(exc).__name__} : {exc}" if exc is not None else ""
        LOGGER.warning(
            "Tâche %s : %s",
            self.ctx.tache.code,
            masquer(f"{message} {detail}".strip(), self.ctx.textes_saisis),
        )

    def tour(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None,
        valides: list[AppelOutil],
    ) -> Generator[Evenement, None, tuple[str, Fin, int]]:
        """Une génération : relaie le flux, valide les appels ; renvoie `(texte, fin, refusés)`."""
        flux = diffuser(self.ctx, messages, tools)
        offerts = {(outil.get("function") or {}).get("name") for outil in tools or ()}
        refuses = 0
        try:
            while True:
                try:
                    evenement = next(flux)
                except StopIteration as arret:
                    texte, fin = arret.value
                    return texte, fin, refuses
                if isinstance(evenement, AppelOutil):
                    try:
                        valider_appel(evenement.nom, evenement.arguments)
                        if evenement.nom not in offerts:
                            raise AppelRefuse(MOTIF_NON_PROPOSE)
                    except AppelRefuse as exc:
                        details = getattr(exc, "details", None) or [str(exc)]
                        refuses += 1
                        yield AppelNonConforme(
                            nom=evenement.nom,
                            arguments_bruts=_arguments_bruts(evenement.arguments),
                            motif=" ; ".join(details),
                        )
                        continue
                    if evenement.id in self.ids:
                        evenement = evenement.model_copy(update={"id": nouvel_identifiant()})
                    self.ids.add(evenement.id)
                    valides.append(evenement)
                    yield evenement
                else:
                    if isinstance(evenement, AppelNonConforme):
                        refuses += 1
                    yield evenement
        finally:
            flux.close()

    def executer(self, appel: AppelOutil) -> Generator[Evenement, None, str]:
        """Exécute un appel validé ; renvoie le contenu de son message `tool`."""
        if self.repli:
            yield ResultatOutil(id=appel.id, nom=appel.nom, resultat=None, erreur=True)
            return TEXTE_ECHEC
        cle = (appel.nom, json_canonique(appel.arguments))
        if cle in self.deja_faits:
            # Appel identique déjà envoyé dans cette Recherche : résultat repris, sans envoi.
            resultat, erreur = self.deja_faits[cle]
            resultat = copy.deepcopy(resultat)
            yield ResultatOutil(id=appel.id, nom=appel.nom, resultat=resultat, erreur=erreur)
            return contenu_resultat(resultat)
        outils = self.ctx.outils
        mode = mode_avant_appel(self.ctx.mode) if outils is not None else None
        if outils is None or mode != CONNECTE:
            self.journaliser(f"appel « {appel.nom} » non envoyé : Mode {mode}")
            yield from self.replier(appel, MOTIF_MODE_PERDU)
            return TEXTE_ECHEC
        try:
            reponse = _appeler_avec_delai(
                outils, appel.nom, appel.arguments, self.ctx.config.outils.delai_appel_s
            )
        except _PANNES as exc:
            self.journaliser(f"appel « {appel.nom} » en échec", exc)
            yield from self.replier(appel, MOTIF_PANNE)
            return TEXTE_ECHEC
        resultat, erreur = _resultat_de(reponse)
        self.resultats.append(resultat)
        self.deja_faits[cle] = (copy.deepcopy(resultat), erreur)
        yield ResultatOutil(id=appel.id, nom=appel.nom, resultat=resultat, erreur=erreur)
        return contenu_resultat(resultat)

    def replier(self, appel: AppelOutil, motif: str) -> Iterator[Evenement]:
        yield ResultatOutil(id=appel.id, nom=appel.nom, resultat=None, erreur=True)
        self.repli = True
        yield Repli(motif=motif, vers="index")


def messages_connecte(
    tache: Tache, demande: str, tools: Sequence[Mapping[str, Any]] | None
) -> list[dict[str, Any]]:
    """Messages du premier tour en Mode connecté : consigne de la Tâche, demande seule.

    `construire_messages` (AD-7) sur une copie de la Tâche dont le prompt garde sa consigne
    mais n'a plus l'emplacement `passages` : l'entrée texte est rendue telle quelle. Ni
    `config/` ni le prompt chargé ne sont modifiés.
    """
    prompt = dataclasses.replace(
        tache.prompt,
        emplacements=tuple(nom for nom in tache.prompt.emplacements if nom != "passages"),
    )
    return construire_messages(dataclasses.replace(tache, prompt=prompt), demande, None, tools)


def _messages_index(ctx: ContexteTache, demande: str) -> tuple[list[Passage], list[dict[str, Any]]]:
    """Passages du catalogue et messages complets (prompt avec passages, sans `tools`)."""
    passages = passages_catalogue(ctx.recherche, demande)
    return passages, ctx.messages_pour(construire_messages(ctx.tache, demande, passages))


def traiter(ctx: ContexteTache) -> Iterator[Evenement]:
    """Recherche de données : passages du catalogue, boucle d'outils, sources et repli."""
    demande = ctx.entree
    if not isinstance(demande, str):
        raise TypeError("Recherche de données : entrée texte attendue")
    boucle = _Boucle(ctx)

    mode = mode_courant(ctx.mode) if ctx.outils is not None else None
    tools: list[dict[str, Any]] | None = None
    if mode == CONNECTE and ctx.outils is not None:
        ecarts = ecarts_schema(ctx.mode)
        if ecarts:
            boucle.journaliser("schéma des outils MCP modifié : " + " ; ".join(ecarts))
            boucle.repli = True
            yield Repli(motif=MOTIF_SCHEMA, vers="index")
        else:
            autorises = set(ctx.tache.outils_autorises)
            tools = [
                outil
                for outil in ctx.outils.lister_outils()
                if (outil.get("function") or {}).get("name") in autorises
            ] or None
    non_verifie = mode != CONNECTE

    passages: list[Passage] = []
    if tools:
        # MCP d'abord (AD-14) : premier tour sans passages ni recherche dans l'Index.
        messages = ctx.messages_pour(messages_connecte(ctx.tache, demande, tools))
    else:
        passages, messages = _messages_index(ctx, demande)
    textes: list[str] = []
    usage: dict[str, int] = {}
    tours = 0
    while True:
        offerts = (
            tools
            if tools and not boucle.repli and tours < ctx.config.outils.iterations_max
            else None
        )
        valides: list[AppelOutil] = []
        texte, fin, refuses = yield from boucle.tour(messages, offerts, valides)
        textes.append(texte)
        _cumuler(usage, fin)
        if offerts is None:
            break
        if not valides:
            if refuses and not texte.strip():
                # Appels tous refusés, sans texte : dernière génération sur l'Index, sans outil.
                passages, messages = _messages_index(ctx, demande)
                tools = None
                continue
            break
        tours += 1
        contenus = []
        for appel in valides:
            contenus.append((yield from boucle.executer(appel)))
        if boucle.repli:
            # Premier repli : la réponse est établie à partir de l'Index local, messages
            # reconstruits avec les passages du catalogue, sans les tours d'outil (FR-9).
            passages, messages = _messages_index(ctx, demande)
            tools = None
            continue
        messages = [
            *messages,
            {
                "role": "assistant",
                "content": texte or None,
                "tool_calls": [appel_canonique(appel) for appel in valides],
            },
            *(
                {"role": "tool", "tool_call_id": appel.id, "content": contenu}
                for appel, contenu in zip(valides, contenus, strict=True)
            ),
        ]
        valider_conversation(messages)

    texte_total = "\n".join(textes)
    # Aucun résultat d'outil obtenu : la réponse n'a pas été vérifiée en ligne.
    non_verifie = non_verifie or boucle.repli or not boucle.resultats
    yield Sources(sources=sources_recherche(texte_total, passages, boucle.resultats, non_verifie))
    if non_verifie:
        yield Avertissement(code=CODE_AVERTISSEMENT, message=MESSAGE_AVERTISSEMENT)
    alerte = avertissement(ctx.tache)
    if alerte is not None:
        yield alerte
    yield fin.model_copy(
        update={
            "usage": usage or None,
            "urls_inventees": urls_inventees(
                texte_total,
                passages,
                [*ctx.resultats_outils, *boucle.resultats],
                ctx.textes_saisis,
            ),
        }
    )


__all__ = [
    "CODE_AVERTISSEMENT",
    "FACTEUR_RECHERCHE",
    "LIBELLE_NON_VERIFIE",
    "MESSAGE_AVERTISSEMENT",
    "MOTIF_MODE_PERDU",
    "MOTIF_NON_PROPOSE",
    "MOTIF_PANNE",
    "MOTIF_SCHEMA",
    "SOURCE_CATALOGUE",
    "TEXTE_ECHEC",
    "contenu_resultat",
    "messages_connecte",
    "passages_catalogue",
    "sources_mcp",
    "sources_recherche",
    "traiter",
]
