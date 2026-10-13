"""Fixtures de la phase génération du banc (story 5.3).

`tests/harness/factices.py` est chargé sous le nom `harness_factices`, comme dans
`tests/harness/conftest.py`. Règle D1.1 : `FakeLlmDeterministe` produit des mots
aléatoires (`mots`), jamais un texte rédigé. Le Jeu d'évaluation (v1.0 gelé, cassettes,
grille, calibrage) est copié dans `tmp_path` : les originaux ne sont jamais modifiés.
Le marqueur `integration` (avec `lent`) désigne le test réel sur Granite 1B.

Story 5.6 : `JugeFactice` et `verdict_factice` doublent les juges de la notation sur le cache
de verdicts réel (dans `tmp_path`) ; les justifications sont des chaînes factices.
"""

from __future__ import annotations

import hashlib
import importlib.util
import shutil
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

NOM_FACTICES = "harness_factices"
RACINE = Path(__file__).resolve().parents[2]
SLUG = "granite-4.0-1b"
SHA_TEMPLATE = "ab" * 32
ITEMS_8 = ("Q-001", "RD-001", "CR-001", "LC-001", "CO-001", "RE-001", "CT-001", "NR-001")
"""Un item par Tâche du jeu v1.0."""


def _charger_factices() -> ModuleType:
    if NOM_FACTICES in sys.modules:
        return sys.modules[NOM_FACTICES]
    spec = importlib.util.spec_from_file_location(
        NOM_FACTICES, RACINE / "tests" / "harness" / "factices.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[NOM_FACTICES] = module
    spec.loader.exec_module(module)
    return module


factices = _charger_factices()


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "integration: exécute les vrais binaires llama.cpp et modèles (avec `lent`)"
    )
    config.addinivalue_line("markers", "payant: appelle une API payante (jamais par défaut)")


def _empreinte(messages: Sequence[Mapping[str, Any]]) -> str:
    h = hashlib.sha256()
    for message in messages:
        h.update(str(message.get("role")).encode("utf-8") + b"\x00")
        h.update(str(message.get("content")).encode("utf-8") + b"\x01")
    return h.hexdigest()


class FakeLlmDeterministe:
    """`LlmPort` déterministe : mots aléatoires semés par le SHA des `(role, content)`.

    Avec `tools` et sans message `tool` dans la conversation (premier tour de la Recherche
    de données), émet un `AppelOutil` `search_datasets` à requête aléatoire. `lever(messages)`
    peut rendre une exception, levée au milieu du flux. `raison(messages, options)` donne la
    raison du `Fin` (défaut : `terminee`). Enregistre chaque appel.
    """

    def __init__(
        self,
        lever: Callable[[Sequence[Mapping[str, Any]]], BaseException | None] | None = None,
        raison: Callable[[Sequence[Mapping[str, Any]], Mapping[str, Any]], str] | None = None,
    ) -> None:
        self.lever = lever
        self.raison = raison
        self.appels: list[dict[str, Any]] = []

    def generer(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Iterator[Any]:
        from slmsp.core.evenements import AppelOutil, Fin, Jeton

        self.appels.append(
            {
                "messages": [dict(m) for m in messages],
                "tools": tools,
                "options": dict(options) if options is not None else None,
            }
        )
        graine = _empreinte(messages)
        erreur = self.lever(messages) if self.lever is not None else None
        raison = self.raison(messages, options or {}) if self.raison is not None else "terminee"

        def flux() -> Iterator[Any]:
            texte = factices.mots(12, graine)
            yield Jeton(texte=texte[:10])
            if erreur is not None:
                raise erreur
            yield Jeton(texte=texte[10:])
            if tools and not any(m.get("role") == "tool" for m in messages):
                yield AppelOutil(
                    id=f"appel-{graine[:12]}",
                    nom="search_datasets",
                    arguments={"query": factices.mots(2, f"requete-{graine}")},
                )
            yield Fin(raison=raison, usage=dict(factices.USAGE))

        return flux()

    def compter_tokens(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None = None,
    ) -> int:
        return sum(len(str(m.get("content") or "").split()) for m in messages)


def passages_factices() -> list[Any]:
    """Passages factices : trois de service-public, deux du catalogue data.gouv."""
    import dataclasses

    passages = [factices.passage(n, 0.9 - n / 100) for n in range(1, 4)]
    passages += [
        dataclasses.replace(factices.passage(n, 0.8 - n / 100), source="data-gouv-datasets-catalog")
        for n in range(4, 6)
    ]
    return passages


def harnais_factice(llm: Any | None = None) -> Any:
    from slmsp.evaluation.assemblage import HarnaisEvaluation
    from slmsp.harness.config import charger_config_harnais
    from slmsp.harness.taches import charger_taches

    return HarnaisEvaluation(
        llm=llm if llm is not None else FakeLlmDeterministe(),
        embedder=factices.FakeEmbedder(),
        vector_store=factices.FakeVectorStore(passages_factices()),
        config=charger_config_harnais(),
        taches=charger_taches(),
        description={"generation": {"factice": True}, "embedding": {"factice": True}},
        chat_template_sha256=SHA_TEMPLATE,
        index_version="factice",
        llamacpp_tag="b11429",
    )


class Fabrique:
    """Fabrique de Harnais factice ; enregistre ses appels `(modele, variante, racine)`."""

    def __init__(self, llm: Any | None = None, sha_template: str = SHA_TEMPLATE) -> None:
        self.llm = llm
        self.sha_template = sha_template
        self.appels: list[tuple[Any, str, Path]] = []

    @contextmanager
    def __call__(self, modele: Any, variante: str, racine: Path) -> Iterator[Any]:
        self.appels.append((modele, variante, racine))
        harnais = harnais_factice(self.llm)
        harnais.chat_template_sha256 = self.sha_template
        yield harnais


@pytest.fixture
def fabrique() -> Fabrique:
    return Fabrique()


@pytest.fixture
def depot_eval(tmp_path: Path) -> Path:
    """Racine temporaire avec une copie de `eval/` (jeu v1.0, cassettes, grille, calibrage)."""
    racine = tmp_path / "depot"
    source = RACINE / "eval"
    cible = racine / "eval"
    shutil.copytree(source / "jeu" / "v1.0", cible / "jeu" / "v1.0")
    shutil.copytree(source / "cassettes", cible / "cassettes")
    shutil.copytree(source / "calibrage", cible / "calibrage")
    shutil.copyfile(source / "grille-juge-v1.md", cible / "grille-juge-v1.md")
    return racine


@pytest.fixture
def modeles(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """`SLMSP_MODELS_DIR` temporaire avec un GGUF factice de Granite 1B."""
    from slmsp.inference.serveur import charger_config_modele

    dossier = tmp_path / "modeles"
    gguf = dossier / SLUG / "gguf" / charger_config_modele(SLUG).gguf.fichier
    gguf.parent.mkdir(parents=True)
    gguf.write_bytes(b"GGUF-factice")
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(dossier))
    return dossier


# --- Juges factices (story 5.6) -----------------------------------------------------------------

JUSTIFICATION = "<justification-factice>"


def verdict_factice(item: Any, choisir: Callable[[Sequence[Any]], Any] = max, **notes: Any) -> Any:
    """Verdict valide fabriqué depuis le schéma de sortie de l'item (aucun texte rédigé).

    Chaque note vaut `choisir(valeurs admises)` (défaut : la meilleure), sauf les critères
    forcés par `notes` (`presence_elements` : une valeur appliquée à chaque référence).
    """
    from slmsp.core.schemas.verdict import Verdict
    from slmsp.judge.prompt import schema_sortie

    proprietes = schema_sortie(item)["properties"]["criteres"]["properties"]
    criteres: dict[str, Any] = {}
    for nom, propriete in proprietes.items():
        if propriete["type"] == "array":
            sous = propriete["items"]["properties"]
            valeur = notes.get(nom, choisir(sous["present"]["enum"]))
            criteres[nom] = [
                {"ref": ref, "present": valeur, "justification": JUSTIFICATION}
                for ref in sous["ref"]["enum"]
            ]
        else:
            valeur = notes.get(nom, choisir(propriete["properties"]["note"]["enum"]))
            criteres[nom] = {"note": valeur, "justification": JUSTIFICATION}
    return Verdict(id=item.id, criteres=criteres, inventions=[], confiance="haute")


@dataclass(frozen=True)
class ResultatFactice:
    item_id: str
    cle: str
    statut: str
    verdict: Any
    depuis_cache: bool
    cout_eur: float
    motif: str | None = None


@dataclass(frozen=True)
class RapportFactice:
    resultats: tuple[ResultatFactice, ...]
    budget_epuise: bool
    cout_total_eur: float


class JugeFactice:
    """Juge factice sur le cache réel : verdict fabriqué, coût journalisé, jamais de réseau.

    `juger(demandes)` (principal) ou `juger(demandes, echantillon)` (second). Un verdict en
    cache n'est jamais redemandé (`appels_payants` n'augmente pas). `budget_apres=n` épuise
    le budget après `n` appels payants ; `invalides` force des verdicts `invalide` ;
    `non_juges` (item → motif) rend `non-juge` sans appel (`erreur-api`, `limite-debit`) ;
    `fabriquer(item)` remplace `verdict_factice`.
    """

    def __init__(
        self,
        cache: Any,
        nom: str = "principal",
        *,
        fabriquer: Callable[[Any], Any] | None = None,
        cout: float = 0.0125,
        budget_apres: int | None = None,
        invalides: Sequence[str] = (),
        non_juges: Mapping[str, str] | None = None,
    ) -> None:
        self.cache = cache
        self.nom = nom
        self.fabriquer = fabriquer or verdict_factice
        self.cout = cout
        self.budget_apres = budget_apres
        self.invalides = set(invalides)
        self.non_juges = dict(non_juges or {})
        self.appels_payants = 0
        self.recus: list[str] = []

    def juger(self, demandes: Sequence[Any], echantillon: Any = None) -> RapportFactice:
        from slmsp.core.canonique import json_canonique, sha256_hex
        from slmsp.core.schemas.verdict import Verdict

        retenues = [d for d in demandes if echantillon is None or d.item.id in set(echantillon)]
        resultats: list[ResultatFactice] = []
        budget = False
        total = 0.0
        for demande in retenues:
            item = demande.item
            self.recus.append(item.id)
            cle = sha256_hex(
                json_canonique(
                    {"juge": self.nom, "item": item.id, "sortie": demande.sortie.get("texte")}
                )
            )
            if item.id in self.non_juges:
                motif = self.non_juges[item.id]
                resultats.append(ResultatFactice(item.id, cle, "non-juge", None, False, 0.0, motif))
                continue
            en_cache = self.cache.lire(cle)
            if en_cache is not None:
                verdict = en_cache.verdict
                statut = "invalide" if verdict.invalide else "juge"
                resultats.append(ResultatFactice(item.id, cle, statut, verdict, True, 0.0))
                continue
            if budget or (
                self.budget_apres is not None and self.appels_payants >= self.budget_apres
            ):
                budget = True
                resultats.append(
                    ResultatFactice(item.id, cle, "non-juge", None, False, 0.0, "budget")
                )
                continue
            self.appels_payants += 1
            if item.id in self.invalides:
                verdict = Verdict.invalide_pour(item.id)
            else:
                verdict = self.fabriquer(item)
            self.cache.journaliser_appel(
                cle=cle,
                item_id=item.id,
                mode="direct",
                lot_id=None,
                usage=None,
                cout_eur=self.cout,
                issue="juge",
            )
            self.cache.ecrire(
                cle, verdict, modele=self.nom, effort="factice", mode="direct",
                cout_eur=self.cout, usage=None,
            )  # fmt: skip
            total += self.cout
            statut = "invalide" if verdict.invalide else "juge"
            resultats.append(ResultatFactice(item.id, cle, statut, verdict, False, self.cout))
        return RapportFactice(tuple(resultats), budget, total)


# Les tests importent ces doublures par `from evaluation_factices import ...` (mode importlib).
sys.modules.setdefault("evaluation_factices", sys.modules[__name__])
