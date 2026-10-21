"""Abstention de Q quand aucun passage ne répond (story 16.8, harnais v2).

Avant la réponse, un appel court au même modèle demande si les passages répondent à la
question. En local, la sortie est contrainte à `oui` ou `non` par une grammaire GBNF de
llama-server (`grammar`) ; un modèle externe ignore la grammaire (`OPTIONS_IGNOREES`) : sa
sortie, plafonnée à `max_tokens`, est lue strictement, et une sortie illisible vaut `oui`
(pas d'abstention à tort). L'appel passe par `ctx.llm.generer` : il est mesuré par
l'observateur d'appels et compté par le plafond de dépense comme tout appel (story 17.6).

Les textes fixes (consigne de vérification, phrase d'abstention, orientation) sont dans
`config/prompts/q-abstention.toml`, avec leur propre version : le prompt principal de Q
(`Q.md`) est inchangé. Ils n'entrent dans aucune donnée d'entraînement (D1).
"""

from __future__ import annotations

import functools
import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal

from pydantic import ConfigDict, Field

from slmsp.core.canonique import sha256_hex
from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.core.evenements import AppelOutil, Erreur, Fin, Jeton, VerificationPassages
from slmsp.core.ports import Passage
from slmsp.harness.prompts import construire_messages
from slmsp.harness.taches import ContexteTache, PromptTache, Tache

LOGGER: Final = logging.getLogger("slmsp.harness")

NOM_TEXTES: Final = "q-abstention.toml"
GRAMMAIRE_OUI_NON: Final = 'root ::= "oui" | "non"'
"""Grammaire GBNF de llama-server : la sortie vaut exactement `oui` ou `non`."""
SORTIE_MAX_CARACTERES: Final = 40
"""Caractères de la sortie brute consignés dans `VerificationPassages.sortie`."""

Verdict = Literal["oui", "non", "illisible"]


class _FichierTextes(ModeleConfig):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1]
    version: int = Field(ge=1)
    verification: str = Field(min_length=1)
    phrase: str = Field(min_length=1)
    orientation: str = Field(min_length=1)


@dataclass(frozen=True)
class TextesAbstention:
    """Textes fixes chargés : `tache` porte la consigne de vérification (emplacements
    `question` et `passages`, rendus comme pour Q par `construire_messages`)."""

    version: int
    tache: Tache
    reponse: str
    """Phrase d'abstention puis orientation, séparées par une ligne vide."""


def chemin_textes() -> Path:
    return racine_projet() / "config" / "prompts" / NOM_TEXTES


def charger_textes(chemin: str | Path | None = None) -> TextesAbstention:
    """Lit `config/prompts/q-abstention.toml` (ou `chemin`) ; `ConfigurationInvalide` sinon."""
    fichier = Path(chemin) if chemin is not None else chemin_textes()
    textes = charger_toml(fichier, _FichierTextes)
    consigne = textes.verification.strip()
    prompt = PromptTache(
        id="q-abstention",
        version=textes.version,
        tache="Q",
        consigne=consigne,
        emplacements=("question", "passages"),
        sha256=sha256_hex(fichier.read_bytes()),
    )
    tache = Tache(code="Q", libelle="Vérification des passages", actif=True, prompt=prompt)
    reponse = f"{textes.phrase.strip()}\n\n{textes.orientation.strip()}"
    return TextesAbstention(version=textes.version, tache=tache, reponse=reponse)


@functools.cache
def textes_defaut() -> TextesAbstention:
    return charger_textes()


def lire_verdict(sortie: str) -> Verdict:
    """Lecture stricte : `oui` ou `non` seuls (casse, espaces et point final tolérés)."""
    mot = sortie.strip().lower().rstrip(".").strip()
    if mot in ("oui", "non"):
        return mot  # type: ignore[return-value]
    return "illisible"


def verifier_passages(
    ctx: ContexteTache,
    question: str,
    passages: Sequence[Passage],
    textes: TextesAbstention | None = None,
) -> tuple[VerificationPassages, Fin | None]:
    """Appel de vérification ; renvoie le verdict et le `Fin` de l'appel (usage), s'il existe.

    Les jetons ne sont pas diffusés à l'Agent. Les options de décodage de l'appelant sont
    gardées (température, graine, chat template) ; `max_tokens` et `grammar` sont imposés.
    """
    textes = textes if textes is not None else textes_defaut()
    messages = ctx.messages_pour(construire_messages(textes.tache, question, passages))
    options = {
        **ctx.options_llm,
        "max_tokens": ctx.config.q_abstention.max_tokens,
        "grammar": GRAMMAIRE_OUI_NON,
    }
    flux = iter(ctx.llm.generer(messages, tools=None, options=options))
    morceaux: list[str] = []
    fin: Fin | None = None
    anomalie: str | None = None
    try:
        for evenement in flux:
            if isinstance(evenement, Jeton):
                morceaux.append(evenement.texte)
            elif isinstance(evenement, Erreur | AppelOutil):
                anomalie = evenement.type
                break
            elif isinstance(evenement, Fin):
                fin = evenement
                break
    finally:
        fermer = getattr(flux, "close", None)
        if callable(fermer):
            fermer()
    sortie = "".join(morceaux)
    if anomalie is not None:
        # Sans contenu (ni code ni message) : seul le type d'évènement est consigné.
        LOGGER.warning("vérification des passages interrompue (%s) : verdict illisible", anomalie)
        verdict: Verdict = "illisible"
    else:
        verdict = lire_verdict(sortie)
    return (
        VerificationPassages(
            verdict=verdict,
            abstention=verdict == "non",
            sortie=sortie[:SORTIE_MAX_CARACTERES],
        ),
        fin,
    )


__all__ = [
    "GRAMMAIRE_OUI_NON",
    "TextesAbstention",
    "charger_textes",
    "lire_verdict",
    "textes_defaut",
    "verifier_passages",
]
