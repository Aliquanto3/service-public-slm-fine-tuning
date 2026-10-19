"""Doublures OpenRouter partagées (faux serveur, banc client), chargées par chemin.

Faux serveur en `httpx2.MockTransport`, derrière la garde réseau du profil `outillage` :
`POST /api/v1/chat/completions` et `GET /api/v1/models`. Aucun appel réel ; registre, tarifs
et journaux dans un dossier temporaire. Textes factices seulement (D1).
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx2  # noqa: TID251 (doublures : transport factice)

from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.registre import RegistreBudget
from slmsp.fournisseurs.client import (
    OPENROUTER,
    ClientCompatibleOpenAI,
    fabriquer_http,
    lire_cle,
)
from slmsp.fournisseurs.journal import JournalAppels
from slmsp.net.journal import JournalMemoire

MODELE = "deepseek/modele-factice"
CLE_FACTICE = "sk-or-factice-0000"
USAGE = (1000, 200)
COUT = (1000 + 200) / 1_000_000  # 1 $/M en entrée et en sortie, taux 1
TARIFS = f"""
schema_version = 1

[taux_usd_eur]
valeur = 1.0
date = 2026-10-19
source = "test"

[modeles."{MODELE}"]
devise = "USD"
date = 2026-10-19
source = "test"

[modeles."{MODELE}".modes.direct]
entree = 1.0
sortie = 1.0
"""


def texte_budgets(plafond: float = 10.0) -> str:
    return f"""
schema_version = 1
campagne_id = "campagne-test-tiers"
marge_eur = 0.0
majoration_entree = 1.0

[postes.openrouter]
plafond_eur = {plafond}

[imputations]
juge-tiers-openrouter = "openrouter"
generateur-openrouter = "openrouter"
"""


@dataclass
class FauxOpenRouter:
    """Faux serveur : réponse imposée par file (`int` = statut HTTP, dict = réponse 200)."""

    reponses: list[Any] = field(default_factory=list)
    texte_defaut: Callable[[dict[str, Any]], str] | None = None
    modeles: list[dict[str, Any]] = field(default_factory=list)
    requetes: list[Any] = field(default_factory=list)

    def corps(self) -> list[dict[str, Any]]:
        return [json.loads(r.content) for r in self.requetes if r.method == "POST"]

    def __call__(self, requete: Any) -> Any:
        self.requetes.append(requete)
        if requete.method == "GET":
            return httpx2.Response(200, json={"data": self.modeles})
        corps = json.loads(requete.content)
        spec = self.reponses.pop(0) if self.reponses else {}
        if isinstance(spec, int):
            return httpx2.Response(spec, json={"error": {"message": "<erreur-factice>"}})
        texte = spec.get("texte")
        if texte is None:
            texte = self.texte_defaut(corps) if self.texte_defaut else "<réponse-factice-1>"
        usage: dict[str, Any] = {
            "prompt_tokens": USAGE[0],
            "completion_tokens": USAGE[1],
            "total_tokens": sum(USAGE),
        }
        if "cost" in spec:
            usage["cost"] = spec["cost"]
        return httpx2.Response(
            200,
            json={
                "id": "gen-factice",
                "model": spec.get("model", MODELE),
                "usage": usage,
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": spec.get("finish_reason", "stop"),
                        "message": {"role": "assistant", "content": texte},
                    }
                ],
            },
        )


@dataclass
class Banc:
    dossier: Path
    faux: FauxOpenRouter
    registre: RegistreBudget
    journal: JournalAppels

    def client(self, *, avec_cle: bool = True, **config: Any) -> ClientCompatibleOpenAI:
        from dataclasses import replace

        fournisseur = replace(OPENROUTER, **({"reessais_max": 0} | config))
        http = fabriquer_http(
            fournisseur,
            transport_interne=httpx2.MockTransport(self.faux),
            journal_requetes=JournalMemoire(),
        )
        cle = lire_cle(fournisseur, self.dossier / ".env") if avec_cle else None
        return ClientCompatibleOpenAI(
            fournisseur, self.registre, http, cle, journal=self.journal, dormir=lambda _: None
        )

    def reservations(self) -> list[dict[str, Any]]:
        with closing(sqlite3.connect(self.registre.chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            return [dict(r) for r in connexion.execute("SELECT * FROM reservations ORDER BY id")]


def banc(dossier: Path, plafond: float = 10.0) -> Banc:
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / ".env").write_text(f"OPENROUTER_API_KEY={CLE_FACTICE}\n", encoding="utf-8")
    (dossier / "budgets.toml").write_text(texte_budgets(plafond), encoding="utf-8")
    (dossier / "tarifs.toml").write_text(TARIFS, encoding="utf-8")
    registre = RegistreBudget(
        charger_budgets(dossier / "budgets.toml"),
        charger_tarifs(dossier / "tarifs.toml"),
        dossier / "budget.sqlite",
    )
    return Banc(dossier, FauxOpenRouter(), registre, JournalAppels(dossier / "journal.sqlite"))
