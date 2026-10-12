"""Citations : renvois `[n]` et URL du texte généré (AD-14, FR-5, D-nuit-A2-17).

Seule fonction de vérification des URL du projet : le Harnais et le banc (story 5.3)
l'appellent tous deux. Le texte généré n'est jamais réécrit : une URL inconnue est
seulement signalée (`Fin.urls_inventees`).

- `extraire_urls` : URL `http(s)://…` ou `www.…` du texte, dans l'ordre, sans doublon ; la
  ponctuation finale (point, virgule, guillemet…) n'en fait pas partie.
- `normaliser_url` : forme de comparaison. Schéma ignoré, hôte en minuscules sans `www.`
  ni port par défaut, chemin décodé sans `/` final, fragment retiré, requête conservée.
- `urls_inventees` : URL du texte dont la forme normalisée ne figure dans aucune source
  connue. Sont connues les URL et les URL citées dans le titre ou le texte des passages,
  les URL de toutes les chaînes des résultats d'outils (parcours récursif des dicts,
  listes et modèles), et les URL des textes saisis par l'Agent.
- `numeros_cites` : renvois `[n]`, `[n, m]`, `[n-m]` (et `;` ou tiret demi-cadratin), dans
  la plage `1..nb`, dans l'ordre de première apparition. Un numéro hors plage est ignoré.
- `sources_citees` : un `Source` (avec son `numero`) par passage cité, dans cet ordre.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Any, Final
from urllib.parse import unquote, urlsplit

from pydantic import BaseModel

from slmsp.core.evenements import Source
from slmsp.core.ports import Passage

EXTRAIT_MAX: Final = 300
"""Longueur maximale (caractères) de l'extrait d'une source."""

_MOTIF_URL = re.compile(r"(?:https?://|www\.)[^\s<>\"'`(){}\[\]«»|\\^]+", re.IGNORECASE)
_PONCTUATION_FINALE = ".,;:!?…’'\"*_~"
_MOTIF_RENVOI = re.compile(
    r"\[\s*(\d{1,6}(?:\s*[-–]\s*\d{1,6})?(?:\s*[,;]\s*\d{1,6}(?:\s*[-–]\s*\d{1,6})?)*)\s*\]"
)
_PORTS_DEFAUT = {"80", "443"}


def extraire_urls(texte: str) -> list[str]:
    """URL du texte, dans l'ordre d'apparition, sans doublon exact."""
    urls: list[str] = []
    for brute in _MOTIF_URL.findall(texte):
        url = brute.rstrip(_PONCTUATION_FINALE)
        if url.lower() in ("http://", "https://", "www.") or url in urls:
            continue
        urls.append(url)
    return urls


def normaliser_url(url: str) -> str:
    """Forme de comparaison d'une URL (voir le module).

    Une URL que `urlsplit` refuse (crochet non fermé, caractère pleine chasse dans l'hôte…)
    donne sa forme brute en minuscules, sans espaces ni `/` final : jamais d'exception.
    """
    url = url.strip()
    if url.lower().startswith("www."):
        url = "https://" + url
    try:
        parties = urlsplit(url)
    except ValueError:
        return url.lower().rstrip("/")
    hote = (parties.hostname or "").lower().rstrip(".")
    hote = hote.removeprefix("www.")
    try:
        port = parties.port
    except ValueError:
        port = None
    if port is not None and str(port) not in _PORTS_DEFAUT:
        hote = f"{hote}:{port}"
    chemin = unquote(parties.path).rstrip("/")
    requete = f"?{parties.query}" if parties.query else ""
    return f"{hote}{chemin}{requete}"


def chaines(valeur: Any, *, cles: bool = True) -> Iterator[str]:
    """Toutes les chaînes d'une valeur : dicts (clés si `cles`, et valeurs), listes, modèles."""
    if isinstance(valeur, str):
        yield valeur
    elif isinstance(valeur, BaseModel):
        yield from chaines(valeur.model_dump(mode="json"), cles=cles)
    elif isinstance(valeur, Mapping):
        for cle, sous_valeur in valeur.items():
            if cles:
                yield from chaines(cle)
            yield from chaines(sous_valeur, cles=cles)
    elif isinstance(valeur, (list, tuple, set, frozenset)):
        for element in valeur:
            yield from chaines(element, cles=cles)


def _urls_connues(
    passages: Iterable[Passage], resultats_outils: Iterable[Any], textes_fournis: Iterable[str]
) -> set[str]:
    connues: set[str] = set()
    for passage in passages:
        connues.add(normaliser_url(passage.url))
        # Une URL de passage à parenthèses est coupée par `extraire_urls` dans le texte généré.
        connues.update(normaliser_url(url) for url in extraire_urls(passage.url))
        for texte in (passage.titre, passage.texte):
            connues.update(normaliser_url(url) for url in extraire_urls(texte))
    for chaine in (*chaines(list(resultats_outils)), *chaines(list(textes_fournis))):
        connues.update(normaliser_url(url) for url in extraire_urls(chaine))
    return connues


def urls_inventees(
    texte: str,
    passages: Iterable[Passage] = (),
    resultats_outils: Iterable[Any] = (),
    textes_fournis: Iterable[str] = (),
) -> list[str]:
    """URL du texte absentes des passages, des résultats d'outils et des textes saisis.

    Les URL sont rendues telles qu'écrites dans le texte (première occurrence de chaque
    forme normalisée).
    """
    connues = _urls_connues(passages, resultats_outils, textes_fournis)
    inventees: list[str] = []
    vues: set[str] = set()
    for url in extraire_urls(texte):
        forme = normaliser_url(url)
        if forme in connues or forme in vues:
            continue
        vues.add(forme)
        inventees.append(url)
    return inventees


def numeros_cites(texte: str, nb: int) -> list[int]:
    """Numéros `[n]` cités dans `1..nb`, dans l'ordre de première apparition."""
    numeros: list[int] = []
    for groupe in _MOTIF_RENVOI.findall(texte):
        for element in re.split(r"\s*[,;]\s*", groupe.strip()):
            bornes = re.split(r"\s*[-–]\s*", element)
            debut, fin = int(bornes[0]), int(bornes[-1])
            if debut > fin:
                continue
            for numero in range(max(debut, 1), min(fin, nb) + 1):
                if numero not in numeros:
                    numeros.append(numero)
    return numeros


def extrait(texte: str, longueur: int = EXTRAIT_MAX) -> str:
    """Début du texte, espaces réduits, coupé sur une limite de mot (« … » si coupé)."""
    compact = " ".join(texte.split())
    if len(compact) <= longueur:
        return compact
    coupe = compact[:longueur].rsplit(" ", 1)[0] or compact[:longueur]
    return coupe.rstrip() + "…"


def sources_citees(texte: str, passages: Sequence[Passage]) -> list[Source]:
    """Sources des passages cités par `[n]` dans le texte, numérotées comme dans le texte."""
    sources = []
    for numero in numeros_cites(texte, len(passages)):
        passage = passages[numero - 1]
        sources.append(
            Source(
                numero=numero,
                titre=passage.titre,
                url=passage.url,
                origine="index",
                date=passage.date_snapshot,
                extrait=extrait(passage.texte),
            )
        )
    return sources


__all__ = [
    "EXTRAIT_MAX",
    "chaines",
    "extrait",
    "extraire_urls",
    "normaliser_url",
    "numeros_cites",
    "sources_citees",
    "urls_inventees",
]
