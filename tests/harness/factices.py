"""Doublures des ports pour les tests du Harnais (story 4.2).

Règle D1.1 : aucun texte rédigé. Les sorties de `FakeLlm` et les textes de test sont des
mots aléatoires générés dans le test (`mots`). Les espions (`SpyToolPort`, `SpyModePort`,
`SpyNetGate`) enregistrent l'appel puis échouent : une Tâche de rédaction ne doit jamais
les toucher.
"""

from __future__ import annotations

import copy
import random
import string
from collections.abc import Iterator, Mapping, Sequence
from typing import Any

import numpy as np

from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton
from slmsp.core.ports import Mode, Passage


def mots(n: int, graine: int | str) -> str:
    """`n` mots aléatoires de lettres minuscules, reproductibles par la graine."""
    hasard = random.Random(str(graine))
    return " ".join(
        "".join(hasard.choices(string.ascii_lowercase, k=hasard.randint(3, 9))) for _ in range(n)
    )


def url_factice(graine: int | str) -> str:
    """URL aléatoire sur un hôte factice."""
    return f"https://{mots(1, f'h{graine}')}.example/{mots(1, f'p{graine}')}"


def passage(numero: int, score: float, *, graine: int | str | None = None) -> Passage:
    """Passage factice aléatoire (titre, URL, texte)."""
    graine = numero if graine is None else graine
    return Passage(
        chunk_id=f"c{numero}",
        doc_id=f"d{numero}",
        source="service-public",
        titre=mots(3, f"titre-{graine}"),
        url=url_factice(f"passage-{graine}"),
        texte=mots(40, f"texte-{graine}"),
        date_snapshot="2026-09-25",
        score=score,
    )


def jetons(texte: str, taille: int = 7) -> list[Jeton]:
    """Découpe `texte` en jetons de `taille` caractères."""
    return [Jeton(texte=texte[i : i + taille]) for i in range(0, len(texte), taille)]


USAGE = {"prompt_tokens": 11, "completion_tokens": 7, "total_tokens": 18}


def script(texte: str, *, usage: Mapping[str, int] | None = None) -> list[Any]:
    """Script de `FakeLlm` : jetons de `texte` puis `Fin(terminee)` avec un usage."""
    return [*jetons(texte), Fin(raison="terminee", usage=dict(usage or USAGE))]


class FakeLlm:
    """`LlmPort` scripté : chaque appel à `generer` joue le script suivant (le dernier se répète).

    Un élément de script qui est une exception est levé à cet endroit du flux. Chaque appel
    enregistre `messages`, `tools` et `options` (copies). `fermetures` compte les flux fermés
    avant leur fin (`close`).
    """

    def __init__(self, *scripts: Sequence[Any]) -> None:
        self.scripts = [list(s) for s in scripts] or [script("")]
        self.appels: list[dict[str, Any]] = []
        self.fermetures = 0

    def generer(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Iterator[Jeton | AppelOutil | AppelNonConforme | Fin]:
        self.appels.append(
            {
                "messages": copy.deepcopy([dict(m) for m in messages]),
                "tools": copy.deepcopy(tools),
                "options": copy.deepcopy(dict(options)) if options is not None else None,
            }
        )
        return self._jouer(self.scripts[min(len(self.appels), len(self.scripts)) - 1])

    def _jouer(self, elements: list[Any]) -> Iterator[Any]:
        try:
            for element in elements:
                if isinstance(element, BaseException):
                    raise element
                yield element
        except GeneratorExit:
            self.fermetures += 1
            raise

    def compter_tokens(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None = None,
    ) -> int:
        return sum(len(str(m.get("content") or "").split()) for m in messages)


class FakeEmbedder:
    """`EmbedderPort` déterministe ; enregistre les textes ; peut lever `erreur`."""

    def __init__(self, dimension: int = 4, erreur: BaseException | None = None) -> None:
        self._dimension = dimension
        self.erreur = erreur
        self.textes: list[str] = []

    @property
    def dimension(self) -> int:
        return self._dimension

    def vectoriser(self, textes: Sequence[str]) -> np.ndarray:
        self.textes.extend(textes)
        if self.erreur is not None:
            raise self.erreur
        matrice = np.ones((len(textes), self._dimension), dtype=np.float32)
        return matrice / np.linalg.norm(matrice, axis=1, keepdims=True)


class FakeVectorStore:
    """`VectorStore` qui renvoie ses passages par score décroissant ; enregistre `k`."""

    def __init__(
        self, passages: Sequence[Passage] = (), erreur: BaseException | None = None
    ) -> None:
        self.passages = list(passages)
        self.erreur = erreur
        self.appels: list[int] = []

    def rechercher(self, vecteur: np.ndarray, k: int) -> list[Passage]:
        self.appels.append(k)
        if self.erreur is not None:
            raise self.erreur
        return sorted(self.passages, key=lambda p: -p.score)[:k]


class _Espion:
    def __init__(self) -> None:
        self.appels: list[str] = []

    def _echouer(self, nom: str) -> Any:
        self.appels.append(nom)
        raise AssertionError(f"{type(self).__name__}.{nom} ne doit pas être appelé")


class SpyNetGate(_Espion):
    """`NetGate` qui échoue s'il est appelé."""

    def client(self, profil: str) -> Any:
        return self._echouer("client")

    def verifier(self, profil, methode, url, *, outil=None, termes=None) -> None:
        self._echouer("verifier")


class SpyToolPort(_Espion):
    """`ToolPort` qui échoue s'il est appelé (il passerait par `gate`)."""

    def __init__(self, gate: SpyNetGate | None = None) -> None:
        super().__init__()
        self.gate = gate if gate is not None else SpyNetGate()

    def lister_outils(self) -> list[dict[str, Any]]:
        return self._echouer("lister_outils")

    def appeler(self, nom: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        return self._echouer("appeler")


class SpyModePort(_Espion):
    """`ModePort` qui échoue s'il est appelé."""

    def mode_courant(self) -> Mode:
        return self._echouer("mode_courant")
