"""Doublures de l'adaptateur Mistral : faux serveur, registre et tarifs de test.

Le faux serveur est un gestionnaire de `httpx2.MockTransport` injecté comme transport interne
des clients gardés (`slmsp.net.client`, profil `outillage`) : les requêtes passent par la
garde réseau. Il répond à `POST /v1/chat/completions`, enregistre chaque requête (méthode,
chemin, corps brut) et chaque corps servi. Aucun appel réel.

Tarifs de test : `mistral-large-latest` à 1 $ par million de tokens en entrée comme en
sortie, taux USD → EUR de 1 ; chaque réponse factice compte 1 000 tokens d'entrée et 200 de
sortie (coût réel 0,0012 €).
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx2  # noqa: TID251 (tests de l'adaptateur : transport factice)
import pytest

from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.registre import RegistreBudget
from slmsp.mistral.config import ConfigMistral, charger_mistral

MODELE = "mistral-large-latest"
MODELE_RESOLU = "mistral-large-2512"
CLE_FACTICE = "cle-mistral-factice-5e1b"
USAGE_FACTICE = (1000, 200)

TARIFS_TEST = f"""
schema_version = 1

[taux_usd_eur]
valeur = 1.0
date = 2026-10-12
source = "test"

[modeles."{MODELE}"]
devise = "USD"
date = 2026-10-12
source = "test"

[modeles."{MODELE}".modes.direct]
entree = 1.0
sortie = 1.0
"""


def texte_budgets(juge: float = 5.0, generation: float = 25.0) -> str:
    return f"""
schema_version = 1
campagne_id = "campagne-test"
marge_eur = 0.0
majoration_entree = 1.0

[postes.anthropic]
plafond_eur = 10.0

[postes.mistral]
plafond_eur = 30.0

[postes.mistral.sous_postes]
generation = {generation}
juge = {juge}

[imputations]
generation = "mistral.generation"
validation = "mistral.generation"
juge-second = "mistral.juge"
juge-principal = "anthropic"
"""


@dataclass
class FauxMistral:
    """Faux serveur Mistral. `reponses` : file de réponses, consommée une par requête.

    Une réponse vaut un statut HTTP (`int`), un couple (statut, en-têtes), une exception à
    lever (transport en panne), ou un dictionnaire (`texte`, `model`, `finish_reason`) ;
    file vide : réponse conforme.
    `texte_par_defaut` fabrique le texte à partir du corps JSON de la requête.
    """

    reponses: list[Any] = field(default_factory=list)
    requetes: list[tuple[str, str, bytes]] = field(default_factory=list)
    servis: list[bytes] = field(default_factory=list)
    modele_resolu: str = MODELE_RESOLU
    texte_par_defaut: Callable[[dict[str, Any]], str] = lambda corps: "<verdict-factice>"

    def corps(self) -> list[dict[str, Any]]:
        return [json.loads(c) for _, _, c in self.requetes]

    def _servir(
        self, statut: int, contenu: dict[str, Any], en_tetes: dict[str, str] | None = None
    ) -> Any:
        brut = json.dumps(contenu, ensure_ascii=False, indent=1).encode("utf-8")
        self.servis.append(brut)
        en_tetes = {"content-type": "application/json", **(en_tetes or {})}
        return httpx2.Response(statut, content=brut, headers=en_tetes)

    def __call__(self, requete: Any) -> Any:
        contenu = bytes(requete.content or b"")
        self.requetes.append((requete.method, requete.url.path, contenu))
        if requete.method != "POST" or requete.url.path != "/v1/chat/completions":
            return self._servir(404, {"detail": "route inconnue"})
        corps = json.loads(contenu)
        spec = self.reponses.pop(0) if self.reponses else None
        if isinstance(spec, BaseException):
            raise spec
        if isinstance(spec, tuple):  # (statut, en-têtes) : Retry-After…
            statut, en_tetes = spec
            erreur = {"object": "error", "message": "<erreur-factice>"}
            return self._servir(statut, erreur, en_tetes)
        if isinstance(spec, int):
            return self._servir(spec, {"object": "error", "message": "<erreur-factice>"})
        spec = spec if isinstance(spec, dict) else {}
        entree, sortie = USAGE_FACTICE
        return self._servir(
            200,
            {
                "id": "cmpl-factice",
                "object": "chat.completion",
                "model": spec.get("model", self.modele_resolu),
                "created": 1760227200,
                "usage": {
                    "prompt_tokens": entree,
                    "completion_tokens": sortie,
                    "total_tokens": entree + sortie,
                },
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": spec.get("finish_reason", "stop"),
                        "message": {
                            "role": "assistant",
                            "content": spec.get("texte", self.texte_par_defaut(corps)),
                        },
                    }
                ],
            },
        )


@dataclass
class BancMistral:
    """Configuration, registre, faux serveur et dossier des journaux d'un test."""

    dossier: Path
    config: ConfigMistral
    faux: FauxMistral
    chemin_env: Path
    plafond_juge: float = 5.0
    attentes: list[float] = field(default_factory=list)
    """Attentes demandées entre deux tentatives (aucune attente réelle en test)."""

    def registre(self) -> RegistreBudget:
        budgets = self.dossier / "budgets.toml"
        budgets.write_text(texte_budgets(self.plafond_juge), encoding="utf-8")
        tarifs = self.dossier / "tarifs.toml"
        tarifs.write_text(TARIFS_TEST, encoding="utf-8")
        return RegistreBudget(
            charger_budgets(budgets), charger_tarifs(tarifs), self.dossier / "budget.sqlite"
        )

    def sdk(self, config: ConfigMistral | None = None) -> Any:
        from slmsp.mistral.client import fabriquer_sdk
        from slmsp.net.journal import JournalMemoire

        return fabriquer_sdk(
            config or self.config,
            transport_interne=httpx2.MockTransport(self.faux),
            journal_requetes=JournalMemoire(),
            fichier_env=self.chemin_env,
        )

    def client(
        self,
        config: ConfigMistral | None = None,
        registre: Any = None,
        dormir: Callable[[float], None] | None = None,
        horloge: Callable[[], float] | None = None,
    ) -> Any:
        from slmsp.mistral.client import ClientMistral

        config = config or self.config
        options = {} if horloge is None else {"horloge": horloge}
        return ClientMistral(
            config,
            registre if registre is not None else self.registre(),
            self.sdk(config),
            dossier_journaux=self.dossier,
            dormir=dormir or self.attentes.append,
            alea=lambda: 1.0,
            **options,
        )

    def lignes_registre(self) -> list[dict[str, Any]]:
        chemin = self.dossier / "budget.sqlite"
        if not chemin.exists():
            return []
        with closing(sqlite3.connect(chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            return [dict(r) for r in connexion.execute("SELECT * FROM reservations ORDER BY id")]

    def lignes_journal(self, nom: str) -> list[dict[str, Any]]:
        chemin = self.dossier / nom
        if not chemin.exists():
            return []
        with closing(sqlite3.connect(chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            return [dict(r) for r in connexion.execute("SELECT * FROM appels ORDER BY rowid")]


@pytest.fixture
def banc(tmp_path: Path) -> BancMistral:
    dossier = tmp_path / "banc"
    dossier.mkdir()
    env = dossier / ".env"
    env.write_text(f"MISTRAL_API_KEY={CLE_FACTICE}\n", encoding="utf-8")
    return BancMistral(
        dossier=dossier, config=charger_mistral(), faux=FauxMistral(), chemin_env=env
    )


@pytest.fixture(scope="session")
def doublures() -> SimpleNamespace:
    """Constantes et doublures importables par les modules de test (mode `importlib`)."""
    return SimpleNamespace(
        MODELE=MODELE,
        MODELE_RESOLU=MODELE_RESOLU,
        CLE_FACTICE=CLE_FACTICE,
        USAGE_FACTICE=USAGE_FACTICE,
        FauxMistral=FauxMistral,
        texte_budgets=texte_budgets,
    )
