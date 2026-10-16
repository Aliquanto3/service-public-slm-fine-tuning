"""Rendu d'une conversation par le chat template officiel (story 10.2, AD-7, AD-6).

Une seule voie de rendu pour l'entraînement : `tokenizer.apply_chat_template(messages,
tools=...)` avec les `chat_template_kwargs` de `config/modeles/<slug>.toml`, les mêmes que
ceux transmis à `llama-server --jinja` à l'inférence. `transformers` n'est importé que dans
`charger_tokenizer` : les tests unitaires tournent sans l'extra `train`, avec un tokenizer
factice.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from slmsp.core.artefacts import chemin_autorise
from slmsp.core.config import appliquer_environnement_impose
from slmsp.core.schemas.config_modele import ConfigModele


def kwargs_template(config: ConfigModele | None) -> dict[str, Any]:
    """`chat_template_kwargs` du Modèle (copie), `{}` sans configuration."""
    return dict(config.chat_template_kwargs) if config is not None else {}


def apply_chat_template(
    tokenizer: Any,
    messages: Sequence[Mapping[str, Any]],
    *,
    tools: Sequence[Mapping[str, Any]] | None = None,
    config: ConfigModele | None = None,
    add_generation_prompt: bool = False,
) -> str:
    """Texte rendu par le chat template officiel (`tokenize=False`).

    `add_generation_prompt` ajoute l'amorce du tour `assistant` (utilisé par le masque pour
    borner le début d'un tour). `tools` vient de `config/outils-mcp.toml` ; avec le protocole
    `json-generique`, l'appelant ne le transmet pas (le template ne le rend pas).
    """
    texte = tokenizer.apply_chat_template(
        [dict(m) for m in messages],
        tools=[dict(t) for t in tools] if tools else None,
        tokenize=False,
        add_generation_prompt=add_generation_prompt,
        **kwargs_template(config),
    )
    if not isinstance(texte, str):
        raise TypeError(f"apply_chat_template a rendu {type(texte).__name__}, pas un texte")
    return texte


def charger_tokenizer(dossier: str | Path) -> Any:
    """Tokenizer Hugging Face (rapide) d'un dossier `<SLMSP_MODELS_DIR>/<slug>/hf/`.

    Le dossier est validé par `chemin_autorise(..., "train")`. Importe `transformers`
    (extra `train`) ici seulement.
    """
    chemin = chemin_autorise(dossier, "train")
    appliquer_environnement_impose()
    from transformers import AutoTokenizer  # noqa: PLC0415

    return AutoTokenizer.from_pretrained(str(chemin), use_fast=True, local_files_only=True)
