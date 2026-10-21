"""Traitement de la Question (Q) : réponse fondée sur l'Index local (FR-2, FR-3, FR-5).

Ordre du flux : `Jeton*`, `Sources` (passages cités par `[n]`, numérotés comme dans le
texte ; vide sans renvoi ni passage pertinent), `Avertissement(avis-juridique)`, puis
`Fin` avec `urls_inventees`. Sans passage au-dessus du seuil, le prompt le dit
(`AUCUN_PASSAGE`) et ce n'est pas une erreur. Les passages sont bornés au contexte du Modèle
par `harness.budget.borner_passages` (correctif F2).
"""

from __future__ import annotations

from collections.abc import Iterator

from slmsp.core.evenements import Evenement, Sources
from slmsp.harness.budget import borner_passages
from slmsp.harness.citations import sources_citees, urls_inventees
from slmsp.harness.dedoublonnage import dedoublonner_prefixes
from slmsp.harness.prompts import construire_messages
from slmsp.harness.taches import ContexteTache, avertissement, diffuser


def traiter(ctx: ContexteTache) -> Iterator[Evenement]:
    """Recherche, construction des messages, génération, sources et avertissement."""
    if ctx.recherche is None:
        raise RuntimeError("Question sans recherche dans l'Index local")
    question = ctx.entree
    if not isinstance(question, str):
        raise TypeError("Question : entrée texte attendue")
    passages = borner_passages(
        ctx,
        dedoublonner_prefixes(
            ctx.recherche.rechercher(question, k=ctx.config.question.passages),
            ctx.config.dedoublonnage.prefixe_min_caracteres,
        ),
        lambda liste: ctx.messages_pour(construire_messages(ctx.tache, question, liste)),
    )
    messages = ctx.messages_pour(construire_messages(ctx.tache, question, passages))
    texte, fin = yield from diffuser(ctx, messages)
    yield Sources(sources=sources_citees(texte, passages))
    alerte = avertissement(ctx.tache)
    if alerte is not None:
        yield alerte
    yield fin.model_copy(
        update={
            "urls_inventees": urls_inventees(
                texte, passages, ctx.resultats_outils, ctx.textes_saisis
            )
        }
    )
