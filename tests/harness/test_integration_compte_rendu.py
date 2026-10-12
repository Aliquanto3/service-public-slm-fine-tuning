"""Test réel du compte rendu long : Granite 1B (CPU), contexte 4096, item CR-006 (story 4.4).

Marqué `lent` et `integration`, exclu par défaut. Lancer :
`SLMSP_VENDOR_DIR=<principal>/vendor SLMSP_MODELS_DIR=<principal>/models
uv run pytest tests/harness/test_integration_compte_rendu.py -m integration -s`.

CR-006 (jeu gelé `v1.0`, 5 480 mots, 195 paragraphes) dépasse le contexte de 4096 tokens :
il est découpé en morceaux (`CR-morceau`) puis fusionné (`CR-fusion`). Un espion autour
du client réel compte les appels de chaque variante. Le test est sauté si le binaire
llama.cpp ou le GGUF de Granite manque.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pytest

from slmsp.core.config import dossier_modeles
from slmsp.core.evenements import Fin, Jeton, Progression
from slmsp.core.items import lire_jeu, vers_requete
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.harness.config import charger_config_harnais
from slmsp.harness.prompts import entree_de_requete
from slmsp.harness.service import AssistantService
from slmsp.harness.taches import charger_taches
from slmsp.inference import serveur
from slmsp.inference.client import ClientLlama
from slmsp.inference.serveur import ServeurLlama

GRANITE = "granite-4.0-1b"
DEPOT, FICHIER = "ibm-granite/granite-4.0-1b", "granite-4.0-1b-Q4_K_M.gguf"
CONTEXTE = 4096
ITEM = "CR-006"


def config_granite() -> ConfigModele:
    return ConfigModele.model_validate(
        {
            "depot_hf": DEPOT,
            "revision": "0" * 40,
            "fichiers": [],
            "gguf": {"depot": "local", "fichier": FICHIER, "sha256": "0" * 64},
            "contexte": CONTEXTE,
            "protocole_outils": "natif",
        }
    )


def prerequis() -> None:
    dossier = serveur.dossier_llamacpp()
    if not (dossier / "bin-cpu" / "llama-server.exe").is_file():
        pytest.skip(f"llama.cpp absent sous {dossier} (définir SLMSP_VENDOR_DIR)")
    gguf = dossier_modeles() / GRANITE / "gguf" / FICHIER
    if not gguf.is_file():
        pytest.skip(f"modèle absent : {gguf} (SLMSP_MODELS_DIR)")


class EspionLlm:
    """`LlmPort` qui délègue au client réel et note le prompt système de chaque génération."""

    def __init__(self, client: ClientLlama) -> None:
        self.client = client
        self.taille_contexte = client.taille_contexte
        self.systemes: list[str] = []
        self.mesures = 0

    def generer(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Any:
        self.systemes.append(messages[0]["content"])
        return self.client.generer(messages, tools=tools, options=options)

    def compter_tokens(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None = None,
    ) -> int:
        self.mesures += 1
        return self.client.compter_tokens(messages, tools)


@pytest.mark.lent
@pytest.mark.integration
def test_reel_compte_rendu_long_granite() -> None:
    prerequis()
    table = charger_taches()
    config = charger_config_harnais()
    item = lire_jeu("v1.0").item(ITEM)
    entree = entree_de_requete(vers_requete(item))
    assert isinstance(entree, dict) and "transcription" in entree
    cr = table.tache("CR")
    consignes = {
        cr.prompt_pour("morceau").consigne: "morceau",
        cr.prompt_pour("fusion").consigne: "fusion",
        cr.prompt.consigne: "unique",
    }
    options: dict[str, Any] = {"temperature": 0, "seed": 42, "max_tokens": 300}

    with ServeurLlama(config_granite(), "cpu", slug=GRANITE) as generation:
        espion = EspionLlm(generation.client())
        assert espion.taille_contexte == CONTEXTE
        service = AssistantService(espion, None, None, None, None, config, taches=table)
        evenements = list(
            service.repondre(
                "CR",
                [{"role": "user", "content": entree["transcription"]}],
                options={**options, "entree": entree},
            )
        )

    genres = [consignes[s] for s in espion.systemes]
    progressions = [e for e in evenements if isinstance(e, Progression)]
    texte = "".join(e.texte for e in evenements if isinstance(e, Jeton))
    fin = evenements[-1]
    print(f"\nAppels : {genres} ; mesures de tokens : {espion.mesures}")
    for progression in progressions:
        print(f"  {progression.etape} ({progression.fait}/{progression.total})")
    print(f"Compte rendu ({len(texte.split())} mots) : {texte[:600]}…")
    print(f"Fin : {fin!r}")

    assert isinstance(fin, Fin), f"le flux se termine par {fin!r}"
    assert genres.count("morceau") >= 2
    assert genres[-1] == "fusion" and "unique" not in genres
    n = genres.count("morceau")
    parties = [p for p in progressions if p.etape.startswith("Partie ")]
    assert [p.etape for p in parties] == [f"Partie {i} sur {n}" for i in range(1, n + 1)]
    assert progressions[-1].etape == "Fusion des parties"
    assert texte.strip()
    assert fin.raison in ("terminee", "longueur")
    assert fin.usage is not None and fin.usage["prompt_tokens"] > CONTEXTE
