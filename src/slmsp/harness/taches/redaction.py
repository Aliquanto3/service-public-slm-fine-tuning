"""Traitement des Tâches de rédaction : CR court, LC, CO, RE, CT, NR, TR (FR-38).

Aucun outil n'est passé au modèle (`tools=None`), aucune recherche dans l'Index, aucun
appel à `ToolPort`, au Mode ni au réseau : un texte collé ne quitte jamais le poste. Ordre
du flux : `Jeton*`, l'avertissement de la table s'il existe (TR : traduction
automatique ; jamais l'avertissement juridique), puis `Fin` avec `urls_inventees`.

Tâches de réécriture (`config.generation.reecriture`, CO et TR) sans `max_tokens` de
l'appelant : plafond proportionnel au prompt mesuré (`harness.budget.plafond_reecriture`,
correctif F2), pour qu'un long texte ne soit pas coupé au plafond commun.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Iterator
from types import MappingProxyType

from slmsp.core.evenements import Evenement
from slmsp.harness.budget import plafond_reecriture
from slmsp.harness.citations import urls_inventees
from slmsp.harness.prompts import construire_messages
from slmsp.harness.taches import ContexteTache, avertissement, diffuser

CLE_MAX_TOKENS = "max_tokens"


def traiter(ctx: ContexteTache) -> Iterator[Evenement]:
    """Construction des messages sans passage ni outil, génération, avertissement éventuel."""
    messages = ctx.messages_pour(construire_messages(ctx.tache, ctx.entree))
    if CLE_MAX_TOKENS not in ctx.options_llm and ctx.tache.code in ctx.config.generation.reecriture:
        options = {**ctx.options_llm, CLE_MAX_TOKENS: plafond_reecriture(ctx, messages)}
        ctx = dataclasses.replace(ctx, options_llm=MappingProxyType(options))
    texte, fin = yield from diffuser(ctx, messages, tools=None)
    alerte = avertissement(ctx.tache)
    if alerte is not None:
        yield alerte
    yield fin.model_copy(
        update={
            "urls_inventees": urls_inventees(
                texte, resultats_outils=ctx.resultats_outils, textes_fournis=ctx.textes_saisis
            )
        }
    )
