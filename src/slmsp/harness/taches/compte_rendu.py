"""Traitement des comptes rendus (CR) : appel unique, ou découpage et fusion (FR-13, story 4.4).

Budget : `taille_contexte − reserve_sortie_tokens`. `taille_contexte` est l'attribut
optionnel du `LlmPort` (`ClientLlama` le reçoit de `ServeurLlama.client()`) ; la réserve
et le chevauchement viennent de `ctx.config.compte_rendu`. Tous les messages sont
construits par `construire_messages` (AD-7) et mesurés par `LlmPort.compter_tokens` tels
qu'ils sont envoyés.

- Chemin court : sans `taille_contexte`, ou quand les messages de l'appel unique (prompt
  CR et historique) tiennent dans le budget, on délègue à `redaction.traiter` (flux de la
  story 4.2). C'est aussi le repli quand le découpage ne peut rien apporter (budget nul,
  contenu non textuel, un seul mot ne tient pas) : l'appel unique est tenté et l'erreur
  du serveur reste visible ; rien n'est tronqué.
- Chemin long : chaque clé de contenu (`notes`, `transcription`, dans l'ordre de
  `ORDRE_CLES`) est découpée séparément par `harness.decoupage.decouper`, mesurée sur les
  messages `CR-morceau` complets (partie rendue « 9999 sur 9999 », borne haute). Chaque
  morceau i est précédé de `Progression("Partie i sur n", fait=i-1, total=n)` et passe par
  la variante `morceau`, sans historique ; sa synthèse est consommée sans être diffusée
  (seuls les `AppelNonConforme` sont relayés). Une synthèse blanche est ignorée ; toutes
  blanches : erreur (le service émet `Erreur`). Si les synthèses ne tiennent pas dans une
  fusion, elles sont fusionnées par groupes (variante `fusion`, sans historique, précédées
  de `Progression("Fusion intermédiaire j sur m")`), jusqu'à tenir ou jusqu'à ce qu'aucun
  regroupement ne soit possible. Enfin `Progression("Fusion des parties", fait=n,
  total=n)` puis la fusion finale, avec l'historique, dont les `Jeton` sont diffusés.
  Chaque appel du chemin long reçoit `max_tokens = min(max_tokens de l'appelant,
  reserve_sortie_tokens)`, pour que la sortie tienne dans la réserve du budget. `Fin`
  porte la raison la plus grave de tous les appels (`interrompue` > `longueur` >
  `terminee`), l'usage cumulé de tous les appels (sans `delai_premier_token_ms`, propre à
  chaque appel ; le service le recalcule) et `urls_inventees`.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Generator, Iterator, Mapping, Sequence
from types import MappingProxyType
from typing import Any, Final

from slmsp.core.erreurs import SlmspError
from slmsp.core.evenements import Evenement, Fin, Jeton, Progression
from slmsp.harness.citations import urls_inventees
from slmsp.harness.decoupage import decouper, empaqueter
from slmsp.harness.prompts import CLES_IGNOREES, ORDRE_CLES, construire_messages
from slmsp.harness.taches import ContexteTache, avertissement, diffuser, redaction

CLES_DECOUPEES: Final[tuple[str, ...]] = tuple(
    cle for cle in ORDRE_CLES if cle in ("notes", "transcription")
)
"""Clés de contenu découpées, dans l'ordre de `ORDRE_CLES`."""

VARIANTE_MORCEAU: Final = "morceau"
VARIANTE_FUSION: Final = "fusion"
PARTIE_MESURE: Final = "9999 sur 9999"
"""Rang rendu pendant la mesure d'un morceau : `n` est inconnu avant le découpage."""
ETAPE_FUSION: Final = "Fusion des parties"
CLES_USAGE_NON_CUMULEES: Final[frozenset[str]] = frozenset({"delai_premier_token_ms"})
"""Clés d'usage propres à un appel, jamais additionnées."""
GRAVITE_RAISON: Final[Mapping[str, int]] = MappingProxyType(
    {"terminee": 0, "longueur": 1, "boucle": 1, "interrompue": 2}
)
"""Gravité des raisons de `Fin` : la plus grave de tous les appels l'emporte."""


class SynthesesVides(SlmspError):
    """Le modèle n'a rendu aucune synthèse non blanche : rien à fusionner."""


def _partie(i: int, n: int) -> str:
    return f"{i} sur {n}"


def _silencieux(
    flux: Generator[Evenement, None, tuple[str, Fin]],
) -> Generator[Evenement, None, tuple[str, Fin]]:
    """Relaie `flux` sans ses `Jeton` et renvoie sa valeur de retour."""
    try:
        while True:
            try:
                evenement = next(flux)
            except StopIteration as fin:
                resultat: tuple[str, Fin] = fin.value
                return resultat
            if not isinstance(evenement, Jeton):
                yield evenement
    finally:
        flux.close()


def _usage_cumule(fins: Sequence[Fin]) -> dict[str, int] | None:
    total: dict[str, int] = {}
    for fin in fins:
        for cle, valeur in (fin.usage or {}).items():
            if cle not in CLES_USAGE_NON_CUMULEES:
                total[cle] = total.get(cle, 0) + valeur
    return total or None


def _raison(fins: Sequence[Fin]) -> str:
    return max((fin.raison for fin in fins), key=GRAVITE_RAISON.__getitem__)


def _plafonne(ctx: ContexteTache) -> ContexteTache:
    """`ctx` dont les appels sont plafonnés à la réserve de sortie (`max_tokens`)."""
    reserve = ctx.config.compte_rendu.reserve_sortie_tokens
    demande = ctx.options_llm.get("max_tokens")
    plafond = min(demande, reserve) if isinstance(demande, int) and demande > 0 else reserve
    options = MappingProxyType({**ctx.options_llm, "max_tokens": plafond})
    return dataclasses.replace(ctx, options_llm=options)


def _budget(ctx: ContexteTache) -> int | None:
    taille = getattr(ctx.llm, "taille_contexte", None)
    if not isinstance(taille, int) or isinstance(taille, bool):
        return None
    return taille - ctx.config.compte_rendu.reserve_sortie_tokens


def traiter(ctx: ContexteTache) -> Iterator[Evenement]:
    """Compte rendu en un appel s'il tient dans le contexte, sinon par morceaux puis fusion."""
    plan = _plan(ctx)
    if plan is None:
        yield from redaction.traiter(ctx)
    else:
        yield from _par_morceaux(_plafonne(ctx), *plan)


def _plan(ctx: ContexteTache) -> tuple[int, dict[str, Any], list[tuple[str, str]]] | None:
    """`(budget, base, [(clé, morceau)…])` du chemin long, ou `None` pour l'appel unique."""
    budget = _budget(ctx)
    entree = ctx.entree
    if budget is None or budget <= 0 or not isinstance(entree, Mapping):
        return None
    unique = ctx.messages_pour(construire_messages(ctx.tache, entree))
    if ctx.llm.compter_tokens(unique) <= budget:
        return None
    contenus = {cle: entree[cle] for cle in CLES_DECOUPEES if cle in entree}
    if not contenus or not all(isinstance(v, str) for v in contenus.values()):
        return None
    base = {
        cle: valeur
        for cle, valeur in entree.items()
        if cle not in CLES_DECOUPEES and cle not in CLES_IGNOREES
    }

    def mesureur(cle: str) -> Callable[[str], int]:
        def mesurer(texte: str) -> int:
            entree_morceau = {**base, "partie": PARTIE_MESURE, cle: texte}
            return ctx.llm.compter_tokens(
                construire_messages(ctx.tache, entree_morceau, variante=VARIANTE_MORCEAU)
            )

        return mesurer

    chevauchement = ctx.config.compte_rendu.chevauchement_paragraphes
    plan: list[tuple[str, str]] = []
    for cle, texte in contenus.items():
        mesurer = mesureur(cle)
        if mesurer(texte.split()[0]) > budget:  # même un mot seul ne tient pas
            return None
        plan.extend((cle, morceau) for morceau in decouper(texte, mesurer, budget, chevauchement))
    return budget, base, plan


def _par_morceaux(
    ctx: ContexteTache, budget: int, base: Mapping[str, Any], plan: Sequence[tuple[str, str]]
) -> Iterator[Evenement]:
    """Synthèses silencieuses des morceaux, fusions intermédiaires, fusion finale diffusée."""
    fins: list[Fin] = []
    n = len(plan)
    syntheses: list[str] = []
    for i, (cle, morceau) in enumerate(plan, start=1):
        yield Progression(etape=f"Partie {i} sur {n}", fait=i - 1, total=n)
        messages = construire_messages(
            ctx.tache, {**base, "partie": _partie(i, n), cle: morceau}, variante=VARIANTE_MORCEAU
        )
        texte, fin = yield from _silencieux(diffuser(ctx, messages, tools=None))
        fins.append(fin)
        if texte.strip():
            syntheses.append(texte.strip())
    if not syntheses:
        raise SynthesesVides(f"Tâche {ctx.tache.code} : aucune synthèse de partie non vide")

    def messages_fusion(parties: Sequence[str]) -> list[dict[str, Any]]:
        return construire_messages(
            ctx.tache, {**base, "parties": list(parties)}, variante=VARIANTE_FUSION
        )

    def mesurer_finale(parties: Sequence[str]) -> int:
        return ctx.llm.compter_tokens(ctx.messages_pour(messages_fusion(parties)))

    def mesurer_groupe(parties: Sequence[str]) -> int:
        return ctx.llm.compter_tokens(messages_fusion(parties))

    while len(syntheses) > 1 and mesurer_finale(syntheses) > budget:
        groupes = empaqueter(syntheses, mesurer_groupe, budget)
        if len(groupes) >= len(syntheses):
            break  # aucun regroupement possible : la fusion finale est tentée telle quelle
        a_fusionner = [g for g in groupes if len(g) > 1]
        suivantes: list[str] = []
        j = 0
        for groupe in groupes:
            if len(groupe) == 1:
                suivantes.append(groupe[0])
                continue
            j += 1
            yield Progression(
                etape=f"Fusion intermédiaire {j} sur {len(a_fusionner)}",
                fait=j - 1,
                total=len(a_fusionner),
            )
            texte, fin = yield from _silencieux(diffuser(ctx, messages_fusion(groupe), tools=None))
            fins.append(fin)
            if texte.strip():
                suivantes.append(texte.strip())
        if not suivantes:
            raise SynthesesVides(f"Tâche {ctx.tache.code} : aucune fusion intermédiaire non vide")
        syntheses = suivantes

    yield Progression(etape=ETAPE_FUSION, fait=n, total=n)
    texte, fin = yield from diffuser(ctx, ctx.messages_pour(messages_fusion(syntheses)), tools=None)
    fins.append(fin)
    alerte = avertissement(ctx.tache)
    if alerte is not None:
        yield alerte
    yield fin.model_copy(
        update={
            "raison": _raison(fins),
            "usage": _usage_cumule(fins),
            "urls_inventees": urls_inventees(
                texte, resultats_outils=ctx.resultats_outils, textes_fournis=ctx.textes_saisis
            ),
        }
    )
