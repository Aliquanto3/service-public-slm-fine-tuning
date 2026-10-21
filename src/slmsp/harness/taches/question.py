"""Traitement de la Question (Q) : réponse fondée sur l'Index local (FR-2, FR-3, FR-5).

Ordre du flux : `Jeton*`, `Sources` (passages cités par `[n]`, numérotés comme dans le
texte ; vide sans renvoi ni passage pertinent), `Avertissement(avis-juridique)`, puis
`Fin` avec `urls_inventees`. Sans passage au-dessus du seuil, le prompt le dit
(`AUCUN_PASSAGE`) et ce n'est pas une erreur. Les passages sont bornés au contexte du Modèle
par `harness.budget.borner_passages` (correctif F2).

Abstention (story 16.8, `[q_abstention] actif`) : un appel de vérification précède la
réponse (`harness.abstention`) et son verdict est émis (`VerificationPassages`). Sur `oui`
ou `illisible`, le flux ci-dessus suit, inchangé ; sur `non`, la réponse est le texte fixe
d'abstention, sans `Sources`, puis l'avertissement et `Fin`. Désactivée, Q est inchangée.
"""

from __future__ import annotations

from collections.abc import Iterator

from slmsp.core.evenements import Evenement, Fin, Jeton, Sources
from slmsp.harness.abstention import textes_defaut, verifier_passages
from slmsp.harness.budget import borner_passages
from slmsp.harness.citations import sources_citees, urls_inventees
from slmsp.harness.dedoublonnage import dedoublonner_prefixes
from slmsp.harness.prompts import construire_messages
from slmsp.harness.taches import ContexteTache, avertissement, diffuser
from slmsp.harness.taches.compte_rendu import CLES_USAGE_NON_CUMULEES


def _cumuler_usage(*usages: dict[str, int] | None) -> dict[str, int] | None:
    """Somme des usages connus clé à clé ; `None` si aucun n'est connu."""
    connus = [u for u in usages if u is not None]
    if not connus:
        return None
    total: dict[str, int] = {}
    for usage in connus:
        for cle, valeur in usage.items():
            if cle in CLES_USAGE_NON_CUMULEES:
                total.setdefault(cle, valeur)
                continue
            total[cle] = total.get(cle, 0) + valeur
    return total


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
    fin_verification: Fin | None = None
    if ctx.config.q_abstention.actif:
        textes = textes_defaut()
        verdict, fin_verification = verifier_passages(ctx, question, passages, textes)
        yield verdict
        if verdict.abstention:
            yield Jeton(texte=textes.reponse)
            yield Sources(sources=[])
            alerte = avertissement(ctx.tache)
            if alerte is not None:
                yield alerte
            usage = fin_verification.usage if fin_verification is not None else None
            coupee = fin_verification is not None and fin_verification.raison == "longueur"
            yield Fin(raison="longueur" if coupee else "terminee", usage=usage)
            return
    messages = ctx.messages_pour(construire_messages(ctx.tache, question, passages))
    texte, fin = yield from diffuser(ctx, messages)
    yield Sources(sources=sources_citees(texte, passages))
    alerte = avertissement(ctx.tache)
    if alerte is not None:
        yield alerte
    usage = _cumuler_usage(fin.usage, fin_verification.usage if fin_verification else None)
    yield fin.model_copy(
        update={
            "usage": usage,
            "urls_inventees": urls_inventees(
                texte, passages, ctx.resultats_outils, ctx.textes_saisis
            ),
        }
    )
