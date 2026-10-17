"""Harnais d'évaluation : serveurs, Index, Bac à sable et Mode par item, profil `aucun`.

`ouvrir_harnais(modele, variante, racine)` monte le Harnais complet du banc : un
`llama-server` de génération (le modèle évalué, dans la variante demandée) et un
`llama-server` d'embedding (`bge-m3`, toujours en `cpu`), tous deux sans prendre le verrou
GPU (l'appelant le détient pour tout le run en `cuda`), puis l'Index local de `racine`.
Le SHA-256 du chat template **réellement servi** est relevé par `GET /props`.

`HarnaisEvaluation.service(item, jeu, signaler)` rend un `AssistantService` frais par
item : pour la Recherche de données seulement, un `BacASable` sur les cassettes de l'item
et un `ModeFixe` selon son mode (`MODES_RD`) ; les autres Tâches n'ont ni outil ni Mode.

`sans_reseau()` rend le profil réseau `aucun` effectif pour le code Python du processus :
`socket.connect`, `connect_ex` et `getaddrinfo` vers une cible hors boucle locale lèvent
`HoteBloque` avant tout envoi. Les autres voies (`gethostbyname`, `sendto` UDP sans
connexion, `ConnectEx` de la boucle asyncio Proactor, extensions C, processus enfants
comme `llama-server`) ne sont pas couvertes : aucun port du Harnais d'évaluation ne les
emprunte.
"""

from __future__ import annotations

import hashlib
import ipaddress
import socket
from collections.abc import Callable, Iterator, Mapping
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from slmsp.core.config import racine_projet
from slmsp.core.erreurs import HoteBloque
from slmsp.core.evenements import Evenement
from slmsp.core.items import ItemBase, ItemRD, Jeu, resoudre_cassettes
from slmsp.core.ports import EmbedderPort, LlmPort, VectorStore
from slmsp.evaluation.modele_ref import ModeleResolu
from slmsp.harness.config import ConfigHarnais, charger_config_harnais
from slmsp.harness.modes import ModeFixe
from slmsp.harness.service import AssistantService
from slmsp.harness.taches import TableTaches, charger_taches
from slmsp.index.lecture import ouvrir_index
from slmsp.inference.processus import ErreurInference
from slmsp.inference.serveur import (
    ServeurLlama,
    Variante,
    charger_config_llamacpp,
    charger_config_modele,
    config_llamacpp_modele,
)
from slmsp.mcp.bac_a_sable import BacASable
from slmsp.net import client_local

MODES_RD: Final[Mapping[str, str]] = {
    "connecte": "connecte",
    "repli": "connecte",  # la cassette `simulation` déclenche le repli
    "hors-ligne": "hors-ligne-force",
}
"""Mode de l'item RD → Mode du `ModeFixe` du Harnais."""

SLUG_EMBEDDING: Final = "bge-m3"
PROFIL_RESEAU: Final = "aucun"
DELAI_PROPS: Final = 30.0
"""Délai de `GET /props` (secondes)."""

_NOMS_LOCAUX: Final = frozenset({"localhost"})


@dataclass
class HarnaisEvaluation:
    """Ports partagés du banc et empreintes du serveur, pour tout un run."""

    llm: LlmPort
    embedder: EmbedderPort | None
    vector_store: VectorStore | None
    config: ConfigHarnais
    taches: TableTaches
    description: dict[str, Any]
    chat_template_sha256: str
    index_version: str
    llamacpp_tag: str
    chemin_outils: Path | None = field(default=None)
    """Remplace `config/outils-mcp.toml` pour le Bac à sable (tests)."""

    def service(
        self, item: ItemBase, jeu: Jeu, signaler: Callable[[Evenement], None] | None = None
    ) -> AssistantService:
        """`AssistantService` frais pour `item` (Bac à sable et Mode pour RD seulement).

        Lève `SchemaOutilModifie` ou `CassetteInvalide` si une cassette de l'item est
        refusée par le Bac à sable.
        """
        outils = mode = None
        if isinstance(item, ItemRD):
            outils = BacASable(
                resoudre_cassettes(jeu, item), chemin_outils=self.chemin_outils, signaler=signaler
            )
            mode = ModeFixe(MODES_RD[item.mode])
        return AssistantService(
            self.llm,
            self.embedder,
            self.vector_store,
            outils,
            mode,
            self.config,
            taches=self.taches,
        )


def sha256_texte(texte: str) -> str:
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()


def lire_props(port: int) -> dict[str, Any]:
    """`GET /props` du `llama-server` local de `port` (passerelle `net`)."""
    with client_local(port) as http:
        reponse = http.get(f"http://127.0.0.1:{port}/props", timeout=DELAI_PROPS)
        reponse.raise_for_status()
        props = reponse.json()
    if not isinstance(props, dict):
        raise ErreurInference("/props : objet JSON attendu")
    return props


@contextmanager
def ouvrir_harnais(
    modele: ModeleResolu,
    variante: Variante = "cpu",
    racine: str | Path | None = None,
    *,
    racine_index: str | Path | None = None,
) -> Iterator[HarnaisEvaluation]:
    """Harnais d'évaluation réel (voir le module), arrêté à la sortie du bloc.

    Les configurations (`harnais.toml`, `taches.toml`, `llamacpp.toml`, `modeles/`) sont
    celles du projet ; l'Index est celui de `racine_index` (défaut : `racine`). Lève
    `ConfigurationInvalide`, `ErreurInference` (serveur, `/props` sans chat template) ou
    `ManifesteInvalide` (Index absent ou incohérent).
    """
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    config = charger_config_harnais()
    taches = charger_taches()
    # Le modèle évalué peut exiger sa propre version (`llamacpp` de sa configuration, ex.
    # Bonsai) ; l'embedding reste sur la version commune.
    config_llamacpp = config_llamacpp_modele(modele.config)
    config_llamacpp_embedding = charger_config_llamacpp()
    config_embedding = charger_config_modele(SLUG_EMBEDDING)
    with ExitStack() as pile:
        generation = pile.enter_context(
            ServeurLlama(
                modele.config,
                variante,
                slug=modele.slug,
                gguf=modele.gguf,
                config_llamacpp=config_llamacpp,
                prendre_verrou_gpu=False,
            )
        )
        embedding = pile.enter_context(
            ServeurLlama(
                config_embedding,
                "cpu",
                slug=SLUG_EMBEDDING,
                config_llamacpp=config_llamacpp_embedding,
                prendre_verrou_gpu=False,
            )
        )
        index = pile.enter_context(
            ouvrir_index(base if racine_index is None else Path(racine_index))
        )
        template = lire_props(generation.port).get("chat_template")
        if not isinstance(template, str) or not template:
            raise ErreurInference("/props : chat_template absent du serveur de génération")
        yield HarnaisEvaluation(
            llm=generation.client(),
            embedder=embedding.embedder(),
            vector_store=index,
            config=config,
            taches=taches,
            description={
                "generation": generation.description(),
                "embedding": embedding.description(),
            },
            chat_template_sha256=sha256_texte(template),
            index_version=index.version,
            llamacpp_tag=config_llamacpp.tag,
        )


# --- Profil réseau `aucun` --------------------------------------------------------------------


def _hote(valeur: Any) -> str:
    if isinstance(valeur, bytes):
        valeur = valeur.decode("ascii", errors="replace")
    return str(valeur).strip().strip("[]").rstrip(".").lower()


def _ip_locale(hote: str) -> bool | None:
    """Vrai/faux pour une IP littérale (bouclage ou non), `None` pour un nom."""
    try:
        ip = ipaddress.ip_address(hote.split("%", 1)[0])
    except ValueError:
        return None
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return ip.is_loopback


def adresse_locale(adresse: Any) -> bool:
    """Vrai si `adresse` (argument de `socket.connect`) désigne la boucle locale."""
    if isinstance(adresse, (str, bytes)):
        return True  # socket AF_UNIX : chemin local
    if not isinstance(adresse, tuple) or not adresse:
        return False
    hote = _hote(adresse[0])
    return hote in _NOMS_LOCAUX or bool(_ip_locale(hote))


def hote_local(hote: Any) -> bool:
    """Vrai si la résolution de `hote` reste sur la boucle locale (aucune requête DNS)."""
    if hote is None:
        return True
    hote = _hote(hote)
    return hote in ("", *_NOMS_LOCAUX) or bool(_ip_locale(hote))


@contextmanager
def sans_reseau() -> Iterator[list[str]]:
    """Profil réseau `aucun` pour tout le processus, le temps du bloc.

    Remplace `socket.socket.connect`, `socket.socket.connect_ex` et `socket.getaddrinfo` :
    toute cible hors boucle locale lève `HoteBloque` avant tout envoi. Rend la liste des
    cibles refusées. Les fonctions d'origine sont restaurées à la sortie.
    """
    bloquees: list[str] = []
    connect = socket.socket.connect
    connect_ex = socket.socket.connect_ex
    getaddrinfo = socket.getaddrinfo

    def refuser(cible: Any) -> HoteBloque:
        bloquees.append(repr(cible))
        return HoteBloque(f"connexion refusée, profil réseau {PROFIL_RESEAU} : {cible!r}")

    def garde_connect(self: socket.socket, adresse: Any, *args: Any, **kwargs: Any) -> Any:
        if not adresse_locale(adresse):
            raise refuser(adresse)
        return connect(self, adresse, *args, **kwargs)

    def garde_connect_ex(self: socket.socket, adresse: Any, *args: Any, **kwargs: Any) -> Any:
        if not adresse_locale(adresse):
            raise refuser(adresse)
        return connect_ex(self, adresse, *args, **kwargs)

    def garde_getaddrinfo(hote: Any, *args: Any, **kwargs: Any) -> Any:
        if not hote_local(hote):
            raise refuser(hote)
        return getaddrinfo(hote, *args, **kwargs)

    socket.socket.connect = garde_connect  # type: ignore[method-assign]
    socket.socket.connect_ex = garde_connect_ex  # type: ignore[method-assign]
    socket.getaddrinfo = garde_getaddrinfo  # type: ignore[assignment]
    try:
        yield bloquees
    finally:
        socket.socket.connect = connect  # type: ignore[method-assign]
        socket.socket.connect_ex = connect_ex  # type: ignore[method-assign]
        socket.getaddrinfo = getaddrinfo  # type: ignore[assignment]


__all__ = [
    "MODES_RD",
    "PROFIL_RESEAU",
    "SLUG_EMBEDDING",
    "HarnaisEvaluation",
    "adresse_locale",
    "hote_local",
    "lire_props",
    "ouvrir_harnais",
    "sans_reseau",
]
