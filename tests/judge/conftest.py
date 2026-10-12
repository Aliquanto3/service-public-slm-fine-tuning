"""Doublures du Juge : faux serveur Anthropic, registre espion, configuration de test.

Le faux serveur est un gestionnaire de `httpx2.MockTransport` injecté comme transport
interne du client gardé (`slmsp.net.client`) : les requêtes passent donc par la garde
réseau du profil `outillage`. Il répond aux routes `POST /v1/messages`,
`POST /v1/messages/batches`, `GET /v1/messages/batches/{id}`,
`GET /v1/messages/batches/{id}/results` (JSONL) et `POST /v1/messages/batches/{id}/cancel`,
et enregistre chaque requête (méthode, chemin, corps brut). Aucun appel réel.

Tarifs de test : `claude-opus-5-5` à 1 $ (direct) et 0,5 $ (batch) par million de tokens,
en entrée comme en sortie, taux USD → EUR de 1 ; chaque réponse factice compte 1 000 tokens
d'entrée et 200 de sortie.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx2  # noqa: TID251 (tests du Juge : transport factice)
import pytest

from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.registre import RegistreBudget
from slmsp.core.config import racine_projet
from slmsp.core.items import Item, lire_items
from slmsp.judge.cache import CacheVerdicts
from slmsp.judge.config import ConfigJugePrincipal
from slmsp.judge.grille import Grille, charger_grille

MODELE = "claude-opus-5-5"
CLE_FACTICE = "sk-ant-factice-0000"
SENTINELLE_APPEL = "SENTINELLE-APPEL-OUTIL-7f3a"
SENTINELLE_SOURCE = "SENTINELLE-CLE-SOURCE-91c2"
SENTINELLE_SORTIE = "SENTINELLE-CLE-SORTIE-4d8e"
USAGE_FACTICE = (1000, 200)
ORIGINE = datetime(2026, 10, 12, tzinfo=UTC)
"""Instant 0 de l'horloge murale factice."""

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

[modeles."{MODELE}".modes.batch]
entree = 0.5
sortie = 0.5
"""


def texte_budgets(anthropic: float = 10.0) -> str:
    return f"""
schema_version = 1
campagne_id = "campagne-test"
marge_eur = 0.0
majoration_entree = 1.0

[postes.anthropic]
plafond_eur = {anthropic}

[postes.mistral]
plafond_eur = 30.0

[postes.mistral.sous_postes]
generation = 25.0
juge = 5.0

[imputations]
juge-principal = "anthropic"
juge-second = "mistral.juge"
"""


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "payant: appelle une API payante (jamais par défaut)")


class Crash(BaseException):
    """Arrêt brutal simulé (hors de la hiérarchie `Exception`, jamais rattrapé)."""


# --- Verdicts factices ------------------------------------------------------------------------


def verdict_conforme(schema: dict[str, Any], note: str = "max") -> dict[str, Any]:
    """Verdict conforme à `schema` : plus haute (ou plus basse) note, chaque `ref` une fois."""

    def generer(noeud: dict[str, Any]) -> Any:
        if "const" in noeud:
            return noeud["const"]
        if "enum" in noeud:
            return noeud["enum"][-1 if note == "max" else 0]
        if noeud.get("type") == "object":
            return {cle: generer(sous) for cle, sous in noeud["properties"].items()}
        if noeud.get("type") == "array":
            elements = noeud["items"]
            if elements.get("type") == "object" and "ref" in elements["properties"]:
                return [
                    {
                        "ref": ref,
                        "present": generer(elements["properties"]["present"]),
                        "justification": "<justification-factice>",
                    }
                    for ref in elements["properties"]["ref"]["enum"]
                ]
            return []
        return "<justification-factice>"

    return generer(schema)


def item_du_schema(params: dict[str, Any]) -> str:
    return params["output_config"]["format"]["schema"]["properties"]["id"]["const"]


# --- Faux serveur Anthropic -------------------------------------------------------------------


@dataclass
class LotFaux:
    identifiant: str
    requetes: list[dict[str, Any]]
    sondages: int = 0
    annule: bool = False
    sondages_apres_annulation: int = 0
    termine: bool = False


@dataclass
class FauxAnthropic:
    """Faux serveur Anthropic ; `evenements` est partagé avec le registre espion."""

    evenements: list[tuple[str, str]] = field(default_factory=list)
    requetes: list[tuple[str, str, bytes]] = field(default_factory=list)
    lots: dict[str, LotFaux] = field(default_factory=dict)
    directes: dict[str, list[Any]] = field(default_factory=dict)
    """Réponses directes par item : 500, {"texte": …} ou {"stop_reason": …} (sinon conforme)."""
    resultats_batch: dict[str, Any] = field(default_factory=dict)
    """Résultat batch par item : "errored", "expired", "canceled", {"texte": …}…"""
    sondages_avant_fin: int = 1
    jamais_fini: bool = False
    annulation_confirmee: bool = True
    sondages_annulation: int = 1
    reussies_avant_annulation: set[str] = field(default_factory=set)
    creation: Callable[[], Any] | None = None
    chemin_cache: Path | None = None
    batch_id_en_base_au_premier_get: dict[str, bool] = field(default_factory=dict)
    pannes: dict[str, int] = field(default_factory=dict)
    """Pannes par route (`retrieve`, `results`, `cancel`) : nombre de réponses 500 à rendre."""
    usages: dict[str, tuple[int, int]] = field(default_factory=dict)
    """Usage (entrée, sortie) par item, sinon `USAGE_FACTICE`."""

    def _panne(self, route: str) -> Any:
        restantes = self.pannes.get(route, 0)
        if restantes <= 0:
            return None
        self.pannes[route] = restantes - 1
        return httpx2.Response(500, json={"type": "error", "error": {"type": "api_error"}})

    # -- enregistrement --

    def corps(self) -> list[bytes]:
        return [corps for _, _, corps in self.requetes]

    def chemins(self) -> list[str]:
        return [f"{methode} {chemin}" for methode, chemin, _ in self.requetes]

    def compter(self, motif: str) -> int:
        return sum(1 for chemin in self.chemins() if chemin == motif)

    # -- réponses --

    def message(self, params: dict[str, Any], spec: Any = None) -> dict[str, Any]:
        spec = spec if isinstance(spec, dict) else {}
        texte = spec.get("texte")
        if texte is None:
            schema = params["output_config"]["format"]["schema"]
            texte = json.dumps(verdict_conforme(schema), ensure_ascii=False)
        entree, sortie = self.usages.get(item_du_schema(params), USAGE_FACTICE)
        return {
            "id": "msg_factice",
            "type": "message",
            "role": "assistant",
            "model": params["model"],
            "content": [{"type": "text", "text": texte}],
            "stop_reason": spec.get("stop_reason", "end_turn"),
            "stop_sequence": None,
            "usage": {
                "input_tokens": entree,
                "output_tokens": sortie,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
            },
        }

    def _etat_lot(self, lot: LotFaux) -> str:
        if lot.termine:
            return "ended"
        if lot.annule:
            if self.annulation_confirmee and lot.sondages_apres_annulation >= (
                self.sondages_annulation
            ):
                lot.termine = True
                return "ended"
            return "canceling"
        if not self.jamais_fini and lot.sondages >= self.sondages_avant_fin:
            lot.termine = True
            return "ended"
        return "in_progress"

    def _lot_json(self, lot: LotFaux, statut: str) -> dict[str, Any]:
        fini = statut == "ended"
        return {
            "id": lot.identifiant,
            "type": "message_batch",
            "processing_status": statut,
            "request_counts": {
                "processing": 0 if fini else len(lot.requetes),
                "succeeded": 0,
                "errored": 0,
                "canceled": 0,
                "expired": 0,
            },
            "created_at": "2026-10-12T00:00:00Z",
            "expires_at": "2026-10-13T00:00:00Z",
            "ended_at": "2026-10-12T01:00:00Z" if fini else None,
            "cancel_initiated_at": "2026-10-12T00:30:00Z" if lot.annule else None,
            "archived_at": None,
            "results_url": (
                f"https://api.anthropic.com/v1/messages/batches/{lot.identifiant}/results"
                if fini
                else None
            ),
        }

    def _resultat(self, lot: LotFaux, requete: dict[str, Any]) -> dict[str, Any]:
        item_id = item_du_schema(requete["params"])
        spec = self.resultats_batch.get(item_id)
        if lot.annule and item_id not in self.reussies_avant_annulation:
            spec = "canceled"
        if spec in ("expired", "canceled"):
            resultat: dict[str, Any] = {"type": spec}
        elif spec == "errored":
            resultat = {
                "type": "errored",
                "error": {"type": "error", "error": {"type": "api_error", "message": "x"}},
            }
        else:
            resultat = {"type": "succeeded", "message": self.message(requete["params"], spec)}
        return {"custom_id": requete["custom_id"], "result": resultat}

    def _batch_id_en_base(self, batch_id: str) -> bool:
        if self.chemin_cache is None:
            return False
        with closing(sqlite3.connect(self.chemin_cache)) as connexion:
            ligne = connexion.execute(
                "SELECT statut FROM lots WHERE batch_id = ?", (batch_id,)
            ).fetchone()
        return ligne is not None and ligne[0] == "en_cours"

    def __call__(self, requete: Any) -> Any:
        methode, chemin = requete.method, requete.url.path
        contenu = bytes(requete.content or b"")
        self.requetes.append((methode, chemin, contenu))
        self.evenements.append(("http", f"{methode} {chemin}"))
        corps = json.loads(contenu) if contenu else None
        parties = chemin.strip("/").split("/")
        if methode == "POST" and chemin == "/v1/messages":
            item_id = item_du_schema(corps)
            file = self.directes.get(item_id) or []
            spec = file.pop(0) if file else None
            if isinstance(spec, int):
                return httpx2.Response(
                    spec, json={"type": "error", "error": {"type": "api_error", "message": "x"}}
                )
            return httpx2.Response(200, json=self.message(corps, spec))
        if methode == "POST" and chemin == "/v1/messages/batches":
            if self.creation is not None:
                reponse = self.creation()
                if reponse is not None:
                    return reponse
            identifiant = f"msgbatch_{len(self.lots) + 1:04d}"
            lot = LotFaux(identifiant, corps["requests"])
            self.lots[identifiant] = lot
            return httpx2.Response(200, json=self._lot_json(lot, "in_progress"))
        if len(parties) >= 4 and parties[:3] == ["v1", "messages", "batches"]:
            lot = self.lots[parties[3]]
            panne = self._panne("retrieve" if len(parties) == 4 else parties[4])
            if panne is not None:
                return panne
            if methode == "GET" and len(parties) == 4:
                if lot.identifiant not in self.batch_id_en_base_au_premier_get:
                    self.batch_id_en_base_au_premier_get[lot.identifiant] = self._batch_id_en_base(
                        lot.identifiant
                    )
                lot.sondages += 1
                if lot.annule:
                    lot.sondages_apres_annulation += 1
                return httpx2.Response(200, json=self._lot_json(lot, self._etat_lot(lot)))
            if methode == "GET" and parties[4:] == ["results"]:
                lignes = [json.dumps(self._resultat(lot, r)) for r in lot.requetes]
                return httpx2.Response(
                    200,
                    content="\n".join(lignes).encode("utf-8"),
                    headers={"content-type": "application/binary"},
                )
            if methode == "POST" and parties[4:] == ["cancel"]:
                lot.annule = True
                return httpx2.Response(200, json=self._lot_json(lot, "canceling"))
        return httpx2.Response(404, json={"type": "error", "error": {"type": "not_found_error"}})


# --- Registre espion et horloge factice -------------------------------------------------------


class RegistreEspion(RegistreBudget):
    """`RegistreBudget` qui inscrit ses opérations dans la liste d'évènements partagée."""

    def __init__(self, evenements: list[tuple[str, str]], *args: Any, **kwargs: Any) -> None:
        self.evenements = evenements
        self.crash_collecte = False
        super().__init__(*args, **kwargs)

    def reserver_lot(self, batch_id: str, *args: Any, **kwargs: Any) -> int:
        self.evenements.append(("reserver_lot", batch_id))
        return super().reserver_lot(batch_id, *args, **kwargs)

    def collecter_lot(self, batch_id: str, usage: Any) -> float:
        self.evenements.append(("collecter_lot", batch_id))
        if self.crash_collecte:
            raise Crash("arrêt simulé avant la collecte du lot")
        return super().collecter_lot(batch_id, usage)

    def annuler_lot(self, batch_id: str, usage: Any = None) -> float:
        self.evenements.append(("annuler_lot", batch_id))
        return super().annuler_lot(batch_id, usage)


@dataclass
class Horloge:
    """Horloges factices (monotone et murale) : `attendre(s)` les avance de `s` secondes."""

    temps: float = 0.0
    attentes: list[float] = field(default_factory=list)
    crash_apres: int | None = None

    def __call__(self) -> float:
        return self.temps

    def maintenant(self) -> datetime:
        return ORIGINE + timedelta(seconds=self.temps)

    def attendre(self, secondes: float) -> None:
        self.attentes.append(secondes)
        if self.crash_apres is not None and len(self.attentes) > self.crash_apres:
            raise Crash("arrêt simulé pendant l'attente d'un lot")
        self.temps += secondes


# --- Fixtures ---------------------------------------------------------------------------------


@pytest.fixture(scope="session")
def grille() -> Grille:
    return charger_grille(racine_projet() / "eval" / "grille-juge-v1.md")


@pytest.fixture(scope="session")
def items() -> dict[str, Item]:
    """Items du calibrage (lecture seule), par identifiant faisant foi."""
    chemin = racine_projet() / "eval" / "calibrage" / "echantillon-calibrage.jsonl"
    return {item.id: item for item in lire_items(chemin, strict=False)}


def sortie_factice(texte: str = "<sortie-factice>") -> dict[str, Any]:
    """Sortie canonique factice, avec des sentinelles dans les clés non transmises."""
    return {
        "texte": texte,
        "appels_outils": [{"id": "a1", "nom": SENTINELLE_APPEL, "arguments": {"q": "x"}}],
        "sources": [
            {
                "titre": "Titre de source factice",
                "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F0000",
                "origine": "index",
                "extrait": SENTINELLE_SOURCE,
            }
        ],
        "cle_inconnue": SENTINELLE_SORTIE,
    }


def config_juge(**valeurs: Any) -> ConfigJugePrincipal:
    defauts: dict[str, Any] = {
        "modele": MODELE,
        "effort": "medium",
        "mode_appel": "batch",
        "max_tokens": 6000,
        "delai_max_lot": 3600,
        "intervalle_sondage": 60,
        "delai_annulation": 600,
        "delai_appel": 600,
        "usage_budget": "juge-principal",
        "grille": "eval/grille-juge-v1.md",
    }
    return ConfigJugePrincipal(**{**defauts, **valeurs})


@dataclass
class Banc:
    """Tout ce qu'il faut pour fabriquer des `JugeClaude` sur le même état."""

    dossier: Path
    faux: FauxAnthropic
    grille: Grille
    horloge: Horloge
    chemin_budgets: Path
    chemin_tarifs: Path
    chemin_env: Path
    plafond: float = 10.0
    registre: RegistreEspion | None = None
    cache: CacheVerdicts | None = None
    journal: Any = None

    def ouvrir_registre(self) -> RegistreEspion:
        self.chemin_budgets.write_text(texte_budgets(self.plafond), encoding="utf-8")
        return RegistreEspion(
            self.faux.evenements,
            charger_budgets(self.chemin_budgets),
            charger_tarifs(self.chemin_tarifs),
            self.dossier / "budget.sqlite",
        )

    def juge(self, **valeurs: Any) -> Any:
        """Nouveau `JugeClaude` (nouveau client) sur le même registre et le même cache."""
        from slmsp.judge.claude import JugeClaude, fabriquer_client
        from slmsp.net.journal import JournalMemoire

        config = config_juge(**valeurs)
        if self.registre is None:
            self.registre = self.ouvrir_registre()
        if self.cache is None:
            self.cache = CacheVerdicts(self.dossier / "verdicts.sqlite")
            self.faux.chemin_cache = self.cache.chemin
        self.journal = JournalMemoire()
        client = fabriquer_client(
            config,
            transport_interne=httpx2.MockTransport(self.faux),
            journal=self.journal,
            fichier_env=self.chemin_env,
        )
        return JugeClaude(
            config,
            self.registre,
            self.cache,
            client,
            self.grille,
            attendre=self.horloge.attendre,
            horloge=self.horloge,
            maintenant=self.horloge.maintenant,
        )

    def lignes_registre(self) -> list[dict[str, Any]]:
        assert self.registre is not None
        with closing(sqlite3.connect(self.registre.chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            return [dict(r) for r in connexion.execute("SELECT * FROM reservations ORDER BY id")]

    def lots(self) -> list[dict[str, Any]]:
        assert self.cache is not None
        with closing(sqlite3.connect(self.cache.chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            return [dict(r) for r in connexion.execute("SELECT * FROM lots ORDER BY cree_le")]


@pytest.fixture
def banc(tmp_path: Path, grille: Grille) -> Banc:
    dossier = tmp_path / "banc"
    dossier.mkdir()
    tarifs = dossier / "tarifs.toml"
    tarifs.write_text(TARIFS_TEST, encoding="utf-8")
    env = dossier / ".env"
    env.write_text(f"ANTHROPIC_API_KEY={CLE_FACTICE}\n", encoding="utf-8")
    return Banc(
        dossier=dossier,
        faux=FauxAnthropic(),
        grille=grille,
        horloge=Horloge(),
        chemin_budgets=dossier / "budgets.toml",
        chemin_tarifs=tarifs,
        chemin_env=env,
    )


@pytest.fixture(scope="session")
def doublures() -> SimpleNamespace:
    """Doublures importables par les modules de test (mode d'import `importlib`)."""
    return SimpleNamespace(
        Crash=Crash,
        config_juge=config_juge,
        sortie_factice=sortie_factice,
        verdict_conforme=verdict_conforme,
        MODELE=MODELE,
        CLE_FACTICE=CLE_FACTICE,
        SENTINELLES=(SENTINELLE_APPEL, SENTINELLE_SOURCE, SENTINELLE_SORTIE),
        USAGE_FACTICE=USAGE_FACTICE,
        texte_budgets=texte_budgets,
        TARIFS_TEST=TARIFS_TEST,
    )
