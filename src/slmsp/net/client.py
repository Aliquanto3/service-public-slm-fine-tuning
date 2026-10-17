"""Fabrique unique des clients HTTP (AD-4) : `client(profil, ...)`, `client_local(port)`,
fabriques Hugging Face et `Passerelle` (implémentation de `NetGate`).

Tout client est créé avec `trust_env=False` (un proxy d'environnement court-circuiterait
le transport gardé) et un transport interne sans relance (`retries=0`). Les clients sont
destinés à être injectés dans les SDK : `streamable_http_client(url, http_client=...)`,
`huggingface_hub.set_client_factory(fabrique_hf)`, etc.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Final

import httpx2

from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import HoteBloque
from slmsp.core.ports import JournalRequetes, ModePort
from slmsp.core.schemas.journal_requetes import EntreeJournalRequetes
from slmsp.net.config import (
    ConfigListeBlanche,
    ConfigReseau,
    charger_config_reseau,
    charger_liste_blanche,
)
from slmsp.net.journal import JournalSqlite
from slmsp.net.profils import MODE_ILLISIBLE, PROFILS, evaluer, hote_de, lire_mode
from slmsp.net.relances import DelaisAppel, transport_echeance
from slmsp.net.transport import (
    LIBS,
    Garde,
    module_http,
    transport_garde,
    transport_interne_defaut,
    transport_local,
)

USAGES: Final = ("mcp", "sonde")


def _verifier_arguments(profil: str, lib: str, mode: ModePort | None, usage: str | None) -> None:
    if profil not in PROFILS:
        raise ValueError(f"profil inconnu : {profil!r} (attendu : {', '.join(PROFILS)})")
    if lib not in LIBS:
        raise ValueError(f"bibliothèque HTTP inconnue : {lib!r} (attendu : {', '.join(LIBS)})")
    if usage is not None and usage not in USAGES:
        raise ValueError(f"usage inconnu : {usage!r} (attendu : {', '.join(USAGES)} ou None)")
    if profil == "assistant" and mode is None:
        raise ValueError("le profil assistant exige un ModePort (`mode`)")
    if mode is not None and not isinstance(mode, ModePort):
        raise TypeError("`mode` doit implémenter ModePort (méthode mode_courant)")


def client(
    profil: str,
    lib: str = "httpx2",
    asynchrone: bool = False,
    mode: ModePort | None = None,
    journal: JournalRequetes | None = None,
    transport_interne: Any = None,
    *,
    usage: str | None = None,
    config: ConfigReseau | None = None,
    liste_blanche: ConfigListeBlanche | None = None,
    follow_redirects: bool = False,
    delais_appel: DelaisAppel | None = None,
) -> Any:
    """Client gardé de `lib` (`httpx2.Client`, `httpx2.AsyncClient`, ou leurs pendants httpx).

    `usage` choisit le délai (`mcp` : `delais.mcp`, `sonde` : `delais.sonde`, sinon
    `delais.defaut`). `delais_appel` impose à chaque requête des délais explicites de
    connexion, de lecture et une échéance totale (`slmsp.net.relances.TransportEcheance`,
    sous la garde), quels que soient ceux que demande le SDK appelant.
    `journal` vaut par défaut le `JournalSqlite` de `SLMSP_VAR_DIR` ;
    `config` et `liste_blanche` sont lus dans `config/` s'ils ne sont pas fournis.
    Lève `ValueError` pour un profil, une bibliothèque ou un usage inconnu, ou un profil
    `assistant` sans `mode`.
    """
    _verifier_arguments(profil, lib, mode, usage)
    module = module_http(lib)
    config = charger_config_reseau() if config is None else config
    liste_blanche = charger_liste_blanche() if liste_blanche is None else liste_blanche
    journal = JournalSqlite() if journal is None else journal
    garde = Garde(profil, mode, journal, config, liste_blanche)
    delai = {"mcp": config.delais.mcp, "sonde": config.delais.sonde}.get(
        usage or "", config.delais.defaut
    )
    timeout = module.Timeout(delai)
    if delais_appel is not None:
        interne = transport_interne
        if interne is None:
            interne = transport_interne_defaut(lib, asynchrone)
        transport_interne = transport_echeance(module, asynchrone, interne, delais_appel)
        timeout = module.Timeout(delais_appel.lecture, connect=delais_appel.connexion)
    classe = module.AsyncClient if asynchrone else module.Client
    return classe(
        transport=transport_garde(lib, asynchrone, garde, transport_interne),
        timeout=timeout,
        follow_redirects=follow_redirects,
        trust_env=False,
    )


def client_local(
    port: int,
    lib: str = "httpx2",
    asynchrone: bool = False,
    transport_interne: Any = None,
    *,
    config: ConfigReseau | None = None,
) -> Any:
    """Client limité à `http://127.0.0.1:<port>` (llama-server), sans journal.

    Lève `ValueError` si `port` n'est pas un entier de 1 à 65535.
    """
    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError(f"port invalide : {port!r} (entier de 1 à 65535 attendu)")
    if lib not in LIBS:
        raise ValueError(f"bibliothèque HTTP inconnue : {lib!r} (attendu : {', '.join(LIBS)})")
    module = module_http(lib)
    config = charger_config_reseau() if config is None else config
    classe = module.AsyncClient if asynchrone else module.Client
    return classe(
        transport=transport_local(lib, asynchrone, port, transport_interne),
        timeout=module.Timeout(config.delais.local),
        follow_redirects=False,
        trust_env=False,
    )


def fabrique_hf(
    *,
    journal: JournalRequetes | None = None,
    transport_interne: Any = None,
    config: ConfigReseau | None = None,
    liste_blanche: ConfigListeBlanche | None = None,
) -> httpx2.Client:
    """Fabrique sans argument obligatoire pour `huggingface_hub.set_client_factory`.

    Profil `outillage`, redirections suivies (chaque saut est recontrôlé).
    """
    return client(
        "outillage",
        journal=journal,
        transport_interne=transport_interne,
        config=config,
        liste_blanche=liste_blanche,
        follow_redirects=True,
    )


def fabrique_hf_async(
    *,
    journal: JournalRequetes | None = None,
    transport_interne: Any = None,
    config: ConfigReseau | None = None,
    liste_blanche: ConfigListeBlanche | None = None,
) -> httpx2.AsyncClient:
    """Pendant asynchrone de `fabrique_hf` (`huggingface_hub.set_async_client_factory`)."""
    return client(
        "outillage",
        asynchrone=True,
        journal=journal,
        transport_interne=transport_interne,
        config=config,
        liste_blanche=liste_blanche,
        follow_redirects=True,
    )


class Passerelle:
    """Implémentation de `NetGate` : configuration lue une fois, Mode et journal injectés."""

    def __init__(
        self,
        mode: ModePort | None = None,
        journal: JournalRequetes | None = None,
        *,
        config: ConfigReseau | None = None,
        liste_blanche: ConfigListeBlanche | None = None,
        lib: str = "httpx2",
    ) -> None:
        if lib not in LIBS:
            raise ValueError(f"bibliothèque HTTP inconnue : {lib!r} (attendu : {', '.join(LIBS)})")
        if mode is not None and not isinstance(mode, ModePort):
            raise TypeError("`mode` doit implémenter ModePort (méthode mode_courant)")
        self.mode = mode
        self.journal: JournalRequetes = JournalSqlite() if journal is None else journal
        self.config = charger_config_reseau() if config is None else config
        self.liste_blanche = charger_liste_blanche() if liste_blanche is None else liste_blanche
        self.lib = lib

    def client(
        self,
        profil: str,
        *,
        asynchrone: bool = False,
        usage: str | None = None,
        follow_redirects: bool = False,
        transport_interne: Any = None,
        delais_appel: DelaisAppel | None = None,
    ) -> Any:
        """Client gardé pour `profil`, partageant le Mode et le journal de la passerelle."""
        return client(
            profil,
            self.lib,
            asynchrone,
            self.mode,
            self.journal,
            transport_interne,
            usage=usage,
            config=self.config,
            liste_blanche=self.liste_blanche,
            follow_redirects=follow_redirects,
            delais_appel=delais_appel,
        )

    def verifier(
        self,
        profil: str,
        methode: str,
        url: str,
        *,
        outil: str | None = None,
        termes: Any = None,
    ) -> None:
        """Lève `HoteBloque` (et journalise le refus) si la requête serait refusée.

        Une requête permise n'est pas journalisée ici : elle le sera par le client qui
        l'émet.
        """
        if profil not in PROFILS:
            raise ValueError(f"profil inconnu : {profil!r} (attendu : {', '.join(PROFILS)})")
        if profil == "assistant" and self.mode is None:
            raise ValueError("le profil assistant exige un ModePort (`mode`)")
        lecture = lire_mode(self.mode)
        mode = lecture.mode
        if lecture.illisible:
            verdict = MODE_ILLISIBLE
        else:
            verdict = evaluer(
                profil,
                methode,
                url,
                mode=mode,
                config=self.config,
                liste_blanche=self.liste_blanche,
            )
        if verdict.statut is None:
            return
        if termes is not None and not isinstance(termes, str):
            try:
                termes = json_canonique(termes).decode("utf-8")
            except (ValueError, TypeError, RecursionError):
                termes = None
        hote = hote_de(url)
        self.journal.inscrire(
            EntreeJournalRequetes(
                horodatage=datetime.now(UTC),
                profil=profil,
                hote=hote,
                methode=methode.upper(),
                outil=outil,
                termes=termes,
                statut=verdict.statut,
                mode=mode,
            )
        )
        raise HoteBloque(
            f"Requête refusée ({verdict.motif}) : profil {profil}, "
            f"{methode.upper()} {hote or '<hôte illisible>'}"
        ) from lecture.erreur
