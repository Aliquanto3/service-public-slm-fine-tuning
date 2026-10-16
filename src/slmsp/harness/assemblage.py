"""Racine de composition partagée de l'Assistant, CLI et application (AD-1, AD-4, AD-14).

Entorse à AD-1, consignée en AD-23 (Q10) : la racine de composition vit dans `harness`
(couche 3), sous `cli` et `app` (couche 5), que les deux importent sans se connaître.

`assembler` construit le `AssistantService` à partir des adaptateurs : serveurs
`llama-server` (génération, et embedding quand la Tâche cite des passages), Index local,
journal des Requêtes sortantes, Mode (`ModeSonde`, ou hors ligne forcé), passerelle réseau
et outils MCP. Chaque adaptateur peut être injecté (tests : ports factices et transport
interne espion) ; sinon le vrai est créé et fermé à la sortie du bloc `with`.

- La sonde `GET /health` n'a lieu qu'à la première lecture du Mode : une Tâche de rédaction
  ne lit jamais le Mode, elle n'émet donc aucune requête.
- En hors ligne forcé (FR-10), aucun outil n'est fourni : le transport interne n'est jamais
  appelé, sonde comprise.
- Les outils MCP (`OutilsParesseux`) n'ouvrent leur session qu'au premier appel, après la
  sonde du Mode ; `lister_outils` ne fait aucune requête.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator, Mapping
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.ports import EmbedderPort, JournalRequetes, LlmPort, ToolPort, VectorStore
from slmsp.harness.config import charger_config_harnais
from slmsp.harness.modes import ModeFixe, ModeSonde
from slmsp.harness.service import AssistantService
from slmsp.harness.taches import Tache, charger_taches
from slmsp.net.client import Passerelle
from slmsp.net.journal import JournalMemoire, JournalSqlite

PREFIXE_BASE = "base:"


class ModeleInvalide(ValueError):
    """`--modele` mal formé (seul `base:<slug>` existe avant l'Epic 10)."""


def slug_modele(modele: str) -> str:
    """Slug de `base:<slug>` ; `ModeleInvalide` sinon."""
    slug = modele[len(PREFIXE_BASE) :] if modele.startswith(PREFIXE_BASE) else ""
    if not slug:
        raise ModeleInvalide(f"modèle {modele!r} : forme attendue base:<slug>")
    return slug


class OutilsParesseux:
    """`ToolPort` MCP dont la session s'ouvre au premier `appeler` (après la sonde du Mode)."""

    def __init__(self, **options: Any) -> None:
        self._options = options
        self._direct: Any = None
        self._verrou = threading.Lock()

    def _ouvrir(self) -> Any:
        from slmsp.mcp.direct import McpEnDirect

        with self._verrou:
            if self._direct is None:
                direct = McpEnDirect("assistant", **self._options)
                direct.__enter__()
                self._direct = direct
            return self._direct

    def lister_outils(self) -> list[dict[str, Any]]:
        from slmsp.mcp.outils import charger_outils

        return charger_outils(self._options.get("chemin_outils"))

    def appeler(self, nom: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        return self._ouvrir().appeler(nom, arguments)

    def fermer(self) -> None:
        with self._verrou:
            direct, self._direct = self._direct, None
        if direct is not None:
            direct.__exit__(None, None, None)


@dataclass
class Assemblage:
    """Résultat de `assembler` : le service et les pièces que la CLI affiche ou inspecte."""

    service: AssistantService
    journal: JournalRequetes
    mode: ModeSonde | ModeFixe
    passerelle: Passerelle
    serveurs: list[Any] = field(default_factory=list)
    """`ServeurLlama` démarrés par l'assemblage (provenance : `description()`)."""


def plafonner_threads(config_modele: Any, threads: int | None) -> Any:
    """Config du Modèle avec threads plafonnés à `threads` (None : inchangée)."""
    if threads is None:
        return config_modele
    courant = config_modele.threads
    return config_modele.model_copy(
        update={"threads": threads if courant is None else min(courant, threads)}
    )


def avec_contexte(config_modele: Any, contexte: int | None) -> Any:
    """Config du Modèle avec le contexte `contexte` (None : inchangée).

    Lève `ConfigurationInvalide` hors de 1 .. contexte du Modèle (ou si non entier).
    """
    if contexte is None:
        return config_modele
    maximum = config_modele.contexte
    if isinstance(contexte, bool) or not isinstance(contexte, int) or not 0 < contexte <= maximum:
        raise ConfigurationInvalide(
            f"contexte {contexte!r} invalide : entier de 1 à {maximum} (contexte du Modèle)"
        )
    return config_modele.model_copy(update={"contexte": contexte})


@contextmanager
def assembler(
    modele: str,
    tache: Tache | None = None,
    *,
    hors_ligne: bool = False,
    variante: str = "cpu",
    racine: Path | None = None,
    journal: JournalRequetes | None = None,
    transport_interne: Any = None,
    llm: LlmPort | None = None,
    embedder: EmbedderPort | None = None,
    vector_store: VectorStore | None = None,
    outils: ToolPort | None = None,
    threads: int | None = None,
    contexte: int | None = None,
) -> Iterator[Assemblage]:
    """Assemble l'Assistant pour `modele` (`base:<slug>`) et la Tâche `tache` (Q par défaut).

    `transport_interne` est transmis à la sonde et aux outils MCP. Les serveurs ne sont
    démarrés que pour les ports non injectés ; l'embedder et l'Index seulement si le prompt
    de la Tâche a un emplacement `passages`. `threads` plafonne ceux des deux serveurs
    (jamais au-dessus de la valeur de leur configuration). `contexte` remplace le contexte du
    seul serveur de génération (mesure à contexte réduit) ; l'appelant l'a validé.
    """
    slug = slug_modele(modele)
    table = charger_taches()
    fiche = tache if tache is not None else table.defaut
    config = charger_config_harnais()
    serveurs: list[Any] = []

    def plafonner(config_modele: Any) -> Any:
        return plafonner_threads(config_modele, threads)

    with ExitStack() as pile:
        if "passages" in fiche.prompt.emplacements and vector_store is None:
            from slmsp.index.lecture import ouvrir_index

            vector_store = pile.enter_context(ouvrir_index(racine))  # échec avant les serveurs
        if journal is None:
            # Hors ligne forcé, aucune requête n'est émise : pas de fichier SQLite à ouvrir.
            journal = JournalMemoire() if hors_ligne else JournalSqlite()
        mode = ModeSonde(
            config.modes,
            hors_ligne_force=hors_ligne,
            journal=journal,
            transport_interne=transport_interne,
        )
        passerelle = Passerelle(mode, journal)
        if llm is None:
            from slmsp.inference.serveur import ServeurLlama, charger_config_modele

            serveur = pile.enter_context(
                ServeurLlama(
                    avec_contexte(plafonner(charger_config_modele(slug)), contexte),
                    variante,
                    slug=slug,
                )  # type: ignore[arg-type]
            )
            serveurs.append(serveur)
            llm = serveur.client()
        if "passages" in fiche.prompt.emplacements:
            if embedder is None:
                from slmsp.inference.serveur import ServeurLlama, charger_config_modele

                embedding = pile.enter_context(
                    ServeurLlama(
                        plafonner(charger_config_modele("bge-m3")),
                        "cpu",
                        slug="bge-m3",
                    )
                )
                serveurs.append(embedding)
                embedder = embedding.embedder()
        else:
            embedder = vector_store = None
        if fiche.outils_autorises and not hors_ligne and outils is None:
            paresseux = OutilsParesseux(
                mode=mode, journal=journal, transport_interne=transport_interne
            )
            pile.callback(paresseux.fermer)
            outils = paresseux
        if hors_ligne:
            outils = None
        service = AssistantService(llm, embedder, vector_store, outils, mode, config, taches=table)
        yield Assemblage(service, journal, mode, passerelle, serveurs)


__all__ = [
    "Assemblage",
    "ModeleInvalide",
    "OutilsParesseux",
    "assembler",
    "slug_modele",
]
