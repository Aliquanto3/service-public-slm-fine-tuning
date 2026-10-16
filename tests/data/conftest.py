"""Doublures de l'étape `generate` (story 9.4) : faux serveur Mistral, port d'outils, Index.

Aucun appel réel : le faux serveur Mistral est un `httpx2.MockTransport` injecté dans les
clients gardés de `slmsp.net` ; le port d'outils et la recherche dans l'Index sont des objets
Python. Toutes les chaînes de contenu (amorces, réponses, résultats d'outils, passages) sont
des jetons aléatoires `<…-factice-xxxx>` produits ici (D1.1) : aucun texte n'est rédigé.

Tarifs de test : 1 $ par million de tokens en entrée comme en sortie, taux 1 ; chaque réponse
compte 1 000 tokens d'entrée et 200 de sortie (0,0012 €).
"""

from __future__ import annotations

import json
import secrets
import sqlite3
from collections.abc import Iterator
from contextlib import closing
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import httpx2  # noqa: TID251 (transport factice de l'adaptateur Mistral)
import pytest

from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.registre import RegistreBudget
from slmsp.core.artefacts import nouveau_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.config import racine_projet
from slmsp.core.items import IdentifiantsProteges
from slmsp.core.ports import Passage
from slmsp.core.schemas.cassette import Cassette, Interaction
from slmsp.core.var import dossier_var
from slmsp.mcp.enregistrement import SessionMcp, requete_appel
from slmsp.mcp.outils import charger_config
from slmsp.mistral.config import charger_mistral
from slmsp.mistral.journal import journal_pour
from slmsp.net.journal import JournalMemoire

# `mistralai` (extra `data`) n'est importé qu'à l'usage : `test_seed.py` et les autres tests
# de ce dossier n'en dépendent pas.

JOUR = date(2026, 10, 12)
MODELE_RESOLU = "mistral-large-2512"
CONFIG = racine_projet() / "config"
OUTILS_MCP = CONFIG / "outils-mcp.toml"
DONNEES = """
[mistral]
conditions_verifiees_le = 2026-10-12
modeles_stables = ["mistral-large-latest", "mistral-large-2512"]
"""
TARIFS = """
schema_version = 1

[taux_usd_eur]
valeur = 1.0
date = 2026-10-12
source = "test"

[modeles."mistral-large-latest"]
devise = "USD"
date = 2026-10-12
source = "test"

[modeles."mistral-large-latest".modes.direct]
entree = 1.0
sortie = 1.0
"""


def budgets(generation: float) -> str:
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
juge = 5.0

[imputations]
generation = "mistral.generation"
validation = "mistral.generation"
juge-second = "mistral.juge"
juge-principal = "anthropic"
"""


def factice(prefixe: str = "texte") -> str:
    return f"<{prefixe}-factice-{secrets.token_hex(4)}>"


def appel_outil(nom: str, arguments: Any) -> dict[str, Any]:
    """Appel d'outil au format de l'API (arguments en JSON, sauf chaîne brute fournie)."""
    brut = arguments if isinstance(arguments, str) else json.dumps(arguments)
    return {
        "id": secrets.token_hex(5),
        "type": "function",
        "function": {"name": nom, "arguments": brut},
        "index": 0,
    }


@dataclass
class FauxMistral:
    """Faux serveur Mistral scriptable. `reponses` : une spécification par requête.

    Une spécification vaut un statut HTTP (`int`), une exception à lever, ou un dictionnaire
    (`texte`, `appels` : liste d'`appel_outil`, `finish_reason`, `model`) ; file vide :
    réponse texte aléatoire.
    """

    reponses: list[Any] = field(default_factory=list)
    corps: list[dict[str, Any]] = field(default_factory=list)

    def __call__(self, requete: Any) -> Any:
        corps = json.loads(bytes(requete.content or b"{}"))
        self.corps.append(corps)
        spec = self.reponses.pop(0) if self.reponses else {}
        if isinstance(spec, BaseException):
            raise spec
        if isinstance(spec, int):
            return self._servir(spec, {"object": "error", "message": factice("erreur")})
        message: dict[str, Any] = {"role": "assistant", "content": spec.get("texte", factice())}
        if spec.get("appels"):
            message["tool_calls"] = spec["appels"]
            message["content"] = spec.get("texte", "")
        fin = spec.get("finish_reason", "tool_calls" if spec.get("appels") else "stop")
        return self._servir(
            200,
            {
                "id": "cmpl-factice",
                "object": "chat.completion",
                "model": spec.get("model", MODELE_RESOLU),
                "created": 1760227200,
                "usage": {"prompt_tokens": 1000, "completion_tokens": 200, "total_tokens": 1200},
                "choices": [{"index": 0, "finish_reason": fin, "message": message}],
            },
        )

    @staticmethod
    def _servir(statut: int, contenu: dict[str, Any]) -> Any:
        brut = json.dumps(contenu, ensure_ascii=False).encode("utf-8")
        return httpx2.Response(statut, content=brut, headers={"content-type": "application/json"})

    def gabarits(self) -> list[str]:
        """Première ligne de consigne de chaque requête (identifie le gabarit envoyé)."""
        return [c["messages"][0]["content"].split("\n", 1)[0] for c in self.corps]


@dataclass
class FauxOutils:
    """Port d'outils factice (protocole `SessionOutils`) : résultats texte aléatoires.

    `script` : par nom d'outil, `"erreur"` (réponse JSON-RPC `error`) ou une exception à
    lever. `appels` liste les appels reçus, `ouvertures` les connexions ouvertes.
    """

    script: dict[str, Any] = field(default_factory=dict)
    appels: list[tuple[str, dict[str, Any]]] = field(default_factory=list)
    ouvertures: int = 0
    _interactions: list[Interaction] = field(default_factory=list)

    def __call__(self) -> FauxOutils:
        self._interactions = []
        return self

    def __enter__(self) -> FauxOutils:
        self.ouvertures += 1
        return self

    def __exit__(self, *_exc: object) -> None:
        return None

    def appeler(self, nom: str, arguments: Any) -> dict[str, Any]:
        self.appels.append((nom, dict(arguments)))
        prevu = self.script.get(nom)
        if isinstance(prevu, BaseException):
            raise prevu
        id_ = 3 + len(self._interactions)
        if prevu == "erreur":
            reponse = {"jsonrpc": "2.0", "id": id_, "error": {"code": -1, "message": factice()}}
        else:
            contenu = [{"type": "text", "text": factice("resultat")} for _ in range(2)]
            reponse = {"jsonrpc": "2.0", "id": id_, "result": {"content": contenu}}
        requete = requete_appel(id_, nom, arguments)
        self._interactions.append(Interaction(request=requete, response=reponse))
        return reponse

    def session(self, *, item: str | None = None, session_id: str | None = None) -> SessionMcp:
        cassette = Cassette(
            schema_version=1,
            server="serveur-factice",
            recorded_at=datetime(2026, 10, 12, tzinfo=UTC),
            initialize=None,
            tools_list_sha256=charger_config(OUTILS_MCP).tools_list_sha256,
            interactions=list(self._interactions),
        )
        return SessionMcp(cassette=cassette, session_id=session_id or "inutilise", item=item)


@dataclass
class FausseRecherche:
    """Recherche factice dans l'Index : `passages` renvoyés à chaque requête."""

    passages: list[Passage] = field(default_factory=list)
    version: str = "index-factice"
    requetes: list[str] = field(default_factory=list)

    def rechercher(self, requete: str) -> list[Passage]:
        self.requetes.append(requete)
        return list(self.passages)


def passage(url: str | None = None) -> Passage:
    return Passage(
        chunk_id=secrets.token_hex(6),
        doc_id=secrets.token_hex(6),
        source="source-factice",
        titre=factice("titre"),
        url=url or f"https://exemple.invalid/{secrets.token_hex(4)}",
        texte=factice("passage"),
        date_snapshot=None,
        score=0.9,
    )


@dataclass
class Monde:
    """Racine de test, seed, faux serveurs et lancement de `generate`."""

    racine: Path
    faux: FauxMistral
    outils: FauxOutils
    recherche: FausseRecherche
    proteges: IdentifiantsProteges
    plafond: float = 25.0
    jours: list[date] = field(default_factory=lambda: [JOUR])

    # --- Seed --------------------------------------------------------------------------

    def amorce(
        self,
        tache: str,
        emplacement: str,
        *,
        ligne: int | None = None,
        texte: str | None = None,
        sha: str | None = None,
        **champs: Any,
    ) -> dict[str, Any]:
        texte = texte if texte is not None else factice("amorce")
        ligne = ligne if ligne is not None else secrets.randbelow(10**6)
        valeurs = {
            "schema_version": 1,
            "amorce_id": f"{tache.lower()}.{emplacement}.jeu.{ligne}",
            "tache": tache,
            "emplacement": emplacement,
            "texte": texte,
            "sha_texte": sha or sha256_hex(texte),
            "auteur_contenu": "public",
            "jeu": "jeu-factice",
            "revision": "rev-factice",
            "ligne": ligne,
        }
        valeurs.update(champs)
        return valeurs

    def scenario(self) -> dict[str, Any]:
        """Amorce CR `scenario` d'auteur Mistral, journalisée comme le ferait le seed."""
        texte = factice("scenario")
        brut = json.dumps(
            {
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": texte},
                    }
                ]
            }
        ).encode()
        from slmsp.mistral.generateur import _JETON

        appel_id = self.journal().inscrire(
            session_id=f"seed-{secrets.token_hex(4)}",
            usage="generation",
            modele_demande="mistral-large-latest",
            modele_resolu=MODELE_RESOLU,
            requete={"messages": []},
            reponse_brute=brut,
            reservation_id=None,
            statut="ok",
            statut_http=200,
            jeton=_JETON,
            gabarit_id="scenario-reunion",
            version_gabarit=1,
            sha256_gabarit="0" * 64,
            amorce_ids=["cr.theme.jeu.1"],
        )
        return {
            "schema_version": 1,
            "amorce_id": f"cr.scenario.{secrets.token_hex(4)}",
            "tache": "CR",
            "emplacement": "scenario",
            "texte": texte,
            "sha_texte": sha256_hex(texte),
            "auteur_contenu": "mistral",
            "appel_id": appel_id,
        }

    def ecrire_seed(self, amorces: list[dict[str, Any]], statut: str = "complet") -> str:
        run = nouveau_run("data-seed", "seed", {}, racine=self.racine)
        run.ecrire("amorces.jsonl", b"".join(json_canonique(a) + b"\n" for a in amorces))
        if statut != "en_cours":
            run.terminer(statut)
        return run.run_id

    # --- Générateur et lancement -------------------------------------------------------

    def journal(self) -> Any:
        return journal_pour("generation", charger_mistral(), dossier_var())

    def client(self) -> Any:
        from slmsp.mistral.client import ClientMistral, fabriquer_sdk

        dossier = dossier_var()
        (dossier / "budgets.toml").write_text(budgets(self.plafond), encoding="utf-8")
        (dossier / "tarifs.toml").write_text(TARIFS, encoding="utf-8")
        registre = RegistreBudget(
            charger_budgets(dossier / "budgets.toml"),
            charger_tarifs(dossier / "tarifs.toml"),
            dossier / "budget.sqlite",
        )
        env = dossier / ".env"
        env.write_text("MISTRAL_API_KEY=cle-mistral-factice\n", encoding="utf-8")
        config = charger_mistral()
        sdk = fabriquer_sdk(
            config,
            transport_interne=httpx2.MockTransport(self.faux),
            journal_requetes=JournalMemoire(),
            fichier_env=env,
        )
        return ClientMistral(config, registre, sdk)

    def aujourd_hui(self) -> date:
        return self.jours.pop(0) if len(self.jours) > 1 else self.jours[0]

    def generateur(self, seed_run_id: str, passages: Any) -> Any:
        from slmsp.mistral.generateur import Generateur

        return Generateur(
            seed_run_id,
            client=self.client(),
            racine=self.racine,
            fichier_donnees=self.racine / "config" / "donnees.toml",
            dossier_gabarits=CONFIG / "prompts" / "generateur",
            fichier_outils=OUTILS_MCP,
            rendre_passages=passages,
            aujourd_hui=self.aujourd_hui,
        )

    def lancer(
        self,
        volumes: dict[str, int],
        *,
        seed: str | None = None,
        reprendre: str | None = None,
        **options: Any,
    ) -> Any:
        """Une invocation de `generate` (Générateur neuf, comme un nouveau processus)."""
        from slmsp.data.generate import lancer_generation, seed_du_run
        from slmsp.data.sessions import ResolveurPassages

        passages = ResolveurPassages()
        if reprendre is not None:
            seed = seed_du_run(reprendre, racine=self.racine)
        assert seed is not None
        return lancer_generation(
            racine=self.racine,
            volumes=volumes,
            generateur=self.generateur(seed, passages),
            passages=passages,
            ouvrir_outils=self.outils,
            proteges=self.proteges,
            seed_run_id=None if reprendre is not None else seed,
            reprendre_run_id=reprendre,
            recherche=self.recherche,
            chemin_outils=OUTILS_MCP,
            consigner=lambda _ligne: None,
            **options,
        )

    # --- Lecture des résultats ---------------------------------------------------------

    def lignes(self, resultat: Any, nom: str) -> list[dict[str, Any]]:
        return resultat.run.lire_jsonl(nom)

    def journal_lignes(self) -> list[dict[str, Any]]:
        chemin = dossier_var() / "appels-mistral.sqlite"
        if not chemin.exists():
            return []
        with closing(sqlite3.connect(chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            return [dict(r) for r in connexion.execute("SELECT * FROM appels ORDER BY rowid")]

    def reservations(self) -> list[dict[str, Any]]:
        chemin = dossier_var() / "budget.sqlite"
        if not chemin.exists():
            return []
        with closing(sqlite3.connect(chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            return [dict(r) for r in connexion.execute("SELECT * FROM reservations ORDER BY id")]

    def statuts(self, run: Any) -> list[str]:
        texte = (run.dossier / "etat.jsonl").read_text(encoding="utf-8")
        return [json.loads(ligne)["statut"] for ligne in texte.splitlines() if ligne]


@pytest.fixture
def monde(tmp_path: Path) -> Iterator[Monde]:
    pytest.importorskip("mistralai")
    racine = tmp_path / "racine"
    (racine / "config").mkdir(parents=True)
    (racine / "config" / "donnees.toml").write_text(DONNEES, encoding="utf-8")
    yield Monde(
        racine=racine.resolve(),
        faux=FauxMistral(),
        outils=FauxOutils(),
        recherche=FausseRecherche(),
        proteges=IdentifiantsProteges(frozenset(), frozenset(), frozenset(), frozenset()),
    )


@pytest.fixture(scope="session")
def doublures() -> Any:
    """Fonctions utilitaires importables par les modules de test (mode `importlib`)."""
    from types import SimpleNamespace

    return SimpleNamespace(
        factice=factice,
        appel_outil=appel_outil,
        passage=passage,
        JOUR=JOUR,
        OUTILS_MCP=OUTILS_MCP,
    )
