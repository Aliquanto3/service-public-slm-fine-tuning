"""Traitement des Tâches de rédaction : CR court, LC, CO, RE, CT, NR, TR (FR-38).

Aucun outil n'est passé au modèle (`tools=None`), aucune recherche dans l'Index, aucun
appel à `ToolPort`, au Mode ni au réseau : un texte collé ne quitte jamais le poste. Ordre
du flux : `Jeton*`, l'avertissement de la table s'il existe (TR : traduction
automatique ; jamais l'avertissement juridique), puis `Fin` avec `urls_inventees`.
"""

from __future__ import annotations

from collections.abc import Iterator

from slmsp.core.evenements import Evenement
from slmsp.harness.citations import urls_inventees
from slmsp.harness.prompts import construire_messages
from slmsp.harness.taches import ContexteTache, avertissement, diffuser


def traiter(ctx: ContexteTache) -> Iterator[Evenement]:
    """Construction des messages sans passage ni outil, génération, avertissement éventuel."""
    messages = ctx.messages_pour(construire_messages(ctx.tache, ctx.entree))
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
