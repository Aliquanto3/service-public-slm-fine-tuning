"""Moteur de téléchargement unique de `slmsp fetch` (AD-28, AD-21, AD-4).

Moteur. `Telechargeur.telecharger(url, destination, sha256, taille)` écrit dans
`<destination>.part`, reprend un `.part` existant par `Range: bytes=N-`, relance sur 429,
500 à 504 et erreur de transport (attente exponentielle, `Retry-After` respecté), vérifie
le SHA-256 puis renomme le `.part` en fichier final. Aucun fichier n'est supprimé ni
écrasé :

- fichier final présent au bon SHA : sauté sans requête (`deja-present`) ;
- fichier final présent avec un autre SHA : `ShaInvalide`, rien n'est écrit ;
- `.part` complet au mauvais SHA : renommé `<nom>.sha-invalide-<horodatage>`, `ShaInvalide`,
  fichier final non créé ;
- fichier local de même taille et de même SHA dans un dossier `reutiliser` : lié en dur
  (copie à défaut) au lieu d'être téléchargé (`reutilise`).

Le client HTTP est injecté ; il vient toujours de `slmsp.net` (profil `outillage`). Chaque
requête figure donc au journal des requêtes de la passerelle, et chaque fichier au run
`fetch` de l'appelant (dépôt, fichier, révision, octets, SHA) : cette trace au niveau de
l'appel tient lieu de journal des transferts hf-xet, que ce moteur n'emploie jamais.

Hugging Face. Pas de `hf_hub_download` : il écrit le fichier final avant tout contrôle et
transfère par hf-xet hors du client gardé. `preparer_hf()` pose `HF_HOME`, coupe la
télémétrie et injecte `net.fabrique_hf` dans `huggingface_hub` s'il est installé ;
`client_hf(jeton)` est le seul client qui porte `HF_TOKEN`.

`fetch` n'importe aucun client HTTP (TID251) : une erreur de transport se reconnaît à une
classe `TransportError` d'un module `httpx*` dans son MRO, ou à `ConnectionError` et
`TimeoutError` ; toute autre `OSError` (écriture locale) remonte sans relance.
"""

from __future__ import annotations

import os
import re
import shutil
import time
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Literal
from urllib.parse import quote

from slmsp import net
from slmsp.core.artefacts import verifier_espace
from slmsp.core.canonique import sha256_fichier
from slmsp.core.config import appliquer_environnement_impose, dossier_modeles
from slmsp.core.erreurs import SecretManquant, SlmspError
from slmsp.core.secrets import secret
from slmsp.fetch.config import ConfigTelechargement
from slmsp.net.relances import erreur_transport, lire_retry_after

HOTE_HF: Final = "https://huggingface.co"
STATUTS_TRANSITOIRES: Final = frozenset({429, 500, 502, 503, 504})
STATUTS_REDIRECTION: Final = frozenset({301, 302, 303, 307, 308})
SUFFIXE_PART: Final = ".part"
MARQUE_SHA_INVALIDE: Final = ".sha-invalide-"

Statut = Literal["telecharge", "deja-present", "reutilise"]

_MOTIF_SHA256 = re.compile(r"[0-9a-f]{64}")
_MOTIF_COMMIT = re.compile(r"[0-9a-f]{40}")
_MOTIF_CONTENT_RANGE = re.compile(r"bytes\s+(\d+)-(\d+)/(\d+|\*)", re.IGNORECASE)


class TelechargementEchoue(SlmspError):
    """Téléchargement impossible : essais épuisés, statut HTTP inattendu, reprise refusée."""


class ShaInvalide(SlmspError):
    """Empreinte SHA-256 différente de celle attendue (ou introuvable)."""


class ArchiveInvalide(SlmspError):
    """Archive illisible, hostile (chemin absolu, `..`, lien) ou en conflit à l'extraction."""


class _Transitoire(Exception):
    """Réponse 429 ou 5xx : la requête sera relancée."""

    def __init__(self, motif: str, attente_serveur: float | None) -> None:
        super().__init__(motif)
        self.motif = motif
        self.attente_serveur = attente_serveur


def horodatage() -> str:
    """Horodatage UTC compact, à la microseconde, pour nommer un fichier sans collision."""
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")


def chemin_part(destination: str | Path) -> Path:
    """Fichier partiel d'un téléchargement : `<destination>.part`."""
    destination = Path(destination)
    return destination.with_name(destination.name + SUFFIXE_PART)


def _taille(chemin: Path) -> int:
    try:
        return chemin.stat().st_size
    except FileNotFoundError:
        return 0


def renommer_sans_ecraser(source: Path, destination: Path) -> None:
    """Renomme `source` en `destination` ; lève `FileExistsError` si `destination` existe."""
    if destination.exists():
        raise FileExistsError(f"{destination} existe déjà : rien n'est écrasé")
    os.rename(source, destination)


def mettre_de_cote(chemin: Path, nom_final: str) -> Path:
    """Renomme `chemin` en `<nom_final>.sha-invalide-<horodatage>` (jamais effacé)."""
    cible = chemin.with_name(f"{nom_final}{MARQUE_SHA_INVALIDE}{horodatage()}")
    renommer_sans_ecraser(chemin, cible)
    return cible


@dataclass(frozen=True)
class ResultatFichier:
    """Issue du téléchargement d'un fichier."""

    url: str
    destination: Path
    statut: Statut
    octets: int
    """Octets transférés par cet appel (0 si déjà présent ou réutilisé)."""
    taille: int
    sha256: str
    source: Path | None = None
    """Fichier local réutilisé (`reutilise` seulement)."""


@dataclass(frozen=True)
class MetadonneesHf:
    """En-têtes d'un `HEAD` sans redirection sur une URL `resolve` de Hugging Face."""

    taille: int | None
    sha256: str | None
    """`X-Linked-Etag` d'un fichier LFS (SHA-256), `None` pour un fichier non LFS."""
    commit: str | None
    """`X-Repo-Commit` : commit résolu de la révision demandée."""


def _entier(valeur: str | None) -> int | None:
    if valeur is None:
        return None
    try:
        entier = int(valeur.strip())
    except ValueError:
        return None
    return entier if entier >= 0 else None


def _etag_sha256(valeur: str | None) -> str | None:
    if valeur is None:
        return None
    valeur = valeur.strip()
    if valeur.startswith("W/"):
        valeur = valeur[2:]
    valeur = valeur.strip('"').lower()
    return valeur if _MOTIF_SHA256.fullmatch(valeur) else None


class Telechargeur:
    """Moteur de téléchargement : client injecté, configuration, dossiers réutilisables.

    `attendre` (par défaut `time.sleep`) est appelé entre deux essais ; les tests le
    remplacent pour ne pas attendre.
    """

    def __init__(
        self,
        client: Any,
        config: ConfigTelechargement,
        *,
        reutiliser: Sequence[str | Path] = (),
        attendre: Callable[[float], None] = time.sleep,
    ) -> None:
        self.client = client
        self.config = config
        self.reutiliser = [Path(dossier) for dossier in reutiliser]
        self.attendre = attendre
        self._index_local: dict[int, list[Path]] | None = None
        self._empreintes: dict[Path, str] = {}

    # --- Relances ----------------------------------------------------------------------

    def _attente(self, echecs: int, attente_serveur: float | None) -> float:
        if attente_serveur is not None:
            return min(self.config.attente_max, attente_serveur)
        return min(self.config.attente_max, self.config.attente_initiale * 2 ** (echecs - 1))

    def avec_relances[T](self, description: str, action: Callable[[], T]) -> T:
        """Exécute `action`, relancée sur 429, 5xx et erreur de transport.

        Lève `TelechargementEchoue` après `essais` échecs ; toute autre erreur (dont
        `HoteBloque`) remonte telle quelle.
        """
        echecs = 0
        while True:
            try:
                return action()
            except _Transitoire as exc:
                motif, attente_serveur = exc.motif, exc.attente_serveur
            except Exception as exc:
                if isinstance(exc, SlmspError) or not erreur_transport(exc):
                    raise
                motif, attente_serveur = f"erreur de transport {type(exc).__name__}", None
            echecs += 1
            if echecs >= self.config.essais:
                raise TelechargementEchoue(
                    f"{description} : échec après {echecs} essais ({motif})"
                ) from None
            self.attendre(self._attente(echecs, attente_serveur))

    @staticmethod
    def _transitoire(reponse: Any) -> _Transitoire | None:
        if reponse.status_code not in STATUTS_TRANSITOIRES:
            return None
        return _Transitoire(
            f"HTTP {reponse.status_code}", lire_retry_after(reponse.headers.get("Retry-After"))
        )

    def requete(
        self,
        methode: str,
        url: str,
        *,
        statuts_ok: Iterable[int] = (200,),
        **options: Any,
    ) -> Any:
        """Requête lue en entier, avec relances ; lève `TelechargementEchoue` hors `statuts_ok`."""
        attendus = frozenset(statuts_ok)

        def action() -> Any:
            reponse = self.client.request(methode, url, **options)
            transitoire = self._transitoire(reponse)
            if transitoire is not None:
                raise transitoire
            if reponse.status_code not in attendus:
                raise TelechargementEchoue(
                    f"{methode} {url} : statut HTTP inattendu {reponse.status_code}"
                )
            return reponse

        return self.avec_relances(f"{methode} {url}", action)

    def metadonnees_hf(self, url: str) -> MetadonneesHf:
        """`HEAD` sans redirection sur une URL `resolve` : taille, `X-Linked-Etag`, commit."""
        reponse = self.requete(
            "HEAD", url, statuts_ok={200, *STATUTS_REDIRECTION}, follow_redirects=False
        )
        en_tetes = reponse.headers
        taille = _entier(en_tetes.get("X-Linked-Size"))
        if taille is None and reponse.status_code == 200:
            taille = _entier(en_tetes.get("Content-Length"))
        commit = (en_tetes.get("X-Repo-Commit") or "").strip().lower()
        return MetadonneesHf(
            taille=taille,
            sha256=_etag_sha256(en_tetes.get("X-Linked-Etag")),
            commit=commit if _MOTIF_COMMIT.fullmatch(commit) else None,
        )

    # --- Espace disque -----------------------------------------------------------------

    def verifier_espace_total(self, prevus: Iterable[tuple[str | Path, int | None]]) -> int:
        """Vérifie l'espace libre avant une série de téléchargements.

        `prevus` liste `(destination, taille attendue)`. Le total restant (taille moins
        `.part` déjà reçu, fichiers finals présents exclus) est renvoyé ; s'il dépasse
        `seuil_verification_espace`, `verifier_espace` est appelé pour chaque volume avec
        `marge_espace` (lève `EspaceInsuffisant`). Une taille inconnue compte pour 0.
        """
        par_volume: dict[str, tuple[Path, int]] = {}
        total = 0
        for destination, taille in prevus:
            destination = Path(destination)
            if taille is None or destination.exists():
                continue
            reste = max(0, taille - _taille(chemin_part(destination)))
            total += reste
            volume = destination.absolute().anchor.lower()
            premier, cumul = par_volume.get(volume, (destination, 0))
            par_volume[volume] = (premier, cumul + reste)
        if total > self.config.seuil_verification_espace:
            for destination, octets in par_volume.values():
                verifier_espace(destination, octets, seuil_octets=self.config.marge_espace)
        return total

    # --- Réutilisation locale ------------------------------------------------------------

    def _index(self) -> dict[int, list[Path]]:
        if self._index_local is None:
            index: dict[int, list[Path]] = {}
            for dossier in self.reutiliser:
                for racine, _dossiers, fichiers in os.walk(dossier):
                    for nom in sorted(fichiers):
                        if nom.endswith(SUFFIXE_PART) or MARQUE_SHA_INVALIDE in nom:
                            continue
                        chemin = Path(racine) / nom
                        try:
                            taille = chemin.stat().st_size
                        except OSError:
                            continue
                        index.setdefault(taille, []).append(chemin)
            self._index_local = index
        return self._index_local

    def trouver_local(self, sha256: str, taille: int | None) -> Path | None:
        """Fichier des dossiers `reutiliser` de taille `taille` et d'empreinte `sha256`."""
        if not self.reutiliser or taille is None:
            return None
        for candidat in self._index().get(taille, []):
            empreinte = self._empreintes.get(candidat)
            if empreinte is None:
                try:
                    empreinte = sha256_fichier(candidat, self.config.taille_bloc)
                except OSError:
                    continue
                self._empreintes[candidat] = empreinte
            if empreinte == sha256:
                return candidat
        return None

    def _reutiliser(
        self, url: str, source: Path, destination: Path, sha256: str, taille: int
    ) -> ResultatFichier:
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(source, destination)
        except OSError:
            copie = destination.with_name(f"{destination.name}.copie-{horodatage()}")
            with source.open("rb") as entree, copie.open("xb") as sortie:
                shutil.copyfileobj(entree, sortie, self.config.taille_bloc)
            empreinte = sha256_fichier(copie, self.config.taille_bloc)
            if empreinte != sha256:
                mise_de_cote = mettre_de_cote(copie, destination.name)
                raise ShaInvalide(
                    f"copie de {source} : SHA-256 {empreinte} au lieu de {sha256} "
                    f"(copie conservée sous {mise_de_cote.name})"
                ) from None
            renommer_sans_ecraser(copie, destination)
        return ResultatFichier(url, destination, "reutilise", 0, taille, sha256, source)

    # --- Téléchargement ------------------------------------------------------------------

    def telecharger(
        self,
        url: str,
        destination: str | Path,
        sha256: str,
        taille: int | None = None,
    ) -> ResultatFichier:
        """Télécharge `url` vers `destination`, vérifié par `sha256` (et `taille` si connue).

        Lève `ShaInvalide`, `TelechargementEchoue`, ou `HoteBloque` (redirection refusée).
        """
        if not _MOTIF_SHA256.fullmatch(sha256 or ""):
            raise ShaInvalide(f"{url} : SHA-256 attendu invalide ou absent ({sha256!r})")
        destination = Path(destination)
        if destination.exists():
            present = sha256_fichier(destination, self.config.taille_bloc)
            if present != sha256:
                raise ShaInvalide(
                    f"{destination} existe avec le SHA-256 {present} au lieu de {sha256} : "
                    "rien n'est écrit"
                )
            return ResultatFichier(
                url, destination, "deja-present", 0, destination.stat().st_size, sha256
            )
        source = self.trouver_local(sha256, taille)
        if source is not None and taille is not None:
            return self._reutiliser(url, source, destination, sha256, taille)
        part = chemin_part(destination)
        octets = self._transferer(url, part, taille)
        if not part.exists():  # fichier vide attendu : aucun octet reçu
            part.parent.mkdir(parents=True, exist_ok=True)
            part.open("ab").close()
        recu = sha256_fichier(part, self.config.taille_bloc)
        taille_recue = part.stat().st_size
        if recu != sha256 or (taille is not None and taille_recue != taille):
            mise_de_cote = mettre_de_cote(part, destination.name)
            raise ShaInvalide(
                f"{url} : {taille_recue} octets reçus, SHA-256 {recu} au lieu de {sha256} ; "
                f"fichier conservé sous {mise_de_cote}, {destination.name} non créé"
            )
        renommer_sans_ecraser(part, destination)
        return ResultatFichier(url, destination, "telecharge", octets, taille_recue, sha256)

    def _transferer(self, url: str, part: Path, taille: int | None) -> int:
        transferes = 0

        def passe() -> None:
            nonlocal transferes
            deja = _taille(part)
            if taille is not None and deja >= taille:
                return  # complet (ou trop long) : le contrôle du SHA tranche
            en_tetes = {"Range": f"bytes={deja}-"} if deja else {}
            with self.client.stream("GET", url, headers=en_tetes) as reponse:
                code = reponse.status_code
                transitoire = self._transitoire(reponse)
                if transitoire is not None:
                    raise transitoire
                if deja and code == 416:
                    return  # plage au-delà de la fin : le `.part` est complet
                if deja and code == 200:
                    raise TelechargementEchoue(
                        f"GET {url} : reprise refusée (200 au lieu de 206 pour "
                        f"`Range: bytes={deja}-`) ; {part.name} conservé"
                    )
                if code == 206:
                    plage = _MOTIF_CONTENT_RANGE.match(reponse.headers.get("Content-Range", ""))
                    if plage is None or int(plage.group(1)) != deja:
                        raise TelechargementEchoue(
                            f"GET {url} : Content-Range incohérent pour une reprise à {deja} "
                            f"octets ; {part.name} conservé"
                        )
                elif code != 200:
                    raise TelechargementEchoue(f"GET {url} : statut HTTP inattendu {code}")
                part.parent.mkdir(parents=True, exist_ok=True)
                with part.open("ab") as flux:
                    for bloc in reponse.iter_bytes(self.config.taille_bloc):
                        flux.write(bloc)
                        transferes += len(bloc)

        self.avec_relances(f"GET {url}", passe)
        return transferes


# --- Hugging Face ----------------------------------------------------------------------


def preparer_hf() -> bool:
    """Prépare `huggingface_hub` avant tout import : `HF_HOME`, télémétrie, client gardé.

    Pose `HF_HOME=<dossier_modeles()>/.cache-hf` et les variables de `ENV_IMPOSE`
    (`HF_HUB_DISABLE_TELEMETRY=1`), puis, si `huggingface_hub` est importable, lui
    injecte `net.fabrique_hf`. Renvoie vrai si la fabrique a été posée.
    """
    os.environ["HF_HOME"] = str(dossier_modeles() / ".cache-hf")
    appliquer_environnement_impose()
    try:
        import huggingface_hub
    except ImportError:
        return False
    huggingface_hub.set_client_factory(net.fabrique_hf)
    huggingface_hub.set_async_client_factory(net.fabrique_hf_async)
    return True


def url_hf(
    depot: str,
    chemin: str,
    revision: str,
    *,
    type_depot: Literal["model", "dataset"] = "model",
) -> str:
    """URL `resolve/<revision>` d'un fichier (jamais le datasets-server)."""
    prefixe = "datasets/" if type_depot == "dataset" else ""
    return (
        f"{HOTE_HF}/{prefixe}{quote(depot, safe='/')}/resolve/"
        f"{quote(revision, safe='')}/{quote(chemin, safe='/')}"
    )


def jeton_hf() -> str | None:
    """`HF_TOKEN` du fichier `.env`, ou `None` s'il est absent ou vide (accès anonyme)."""
    try:
        valeur = secret("HF_TOKEN").get_secret_value().strip()
    except SecretManquant:
        return None
    return valeur or None


def en_tetes_hf(jeton: str | None) -> dict[str, str]:
    """En-tête `Authorization` du client HF (vide sans jeton)."""
    return {"Authorization": f"Bearer {jeton}"} if jeton else {}


def client_hf(jeton: str | None, **options: Any) -> Any:
    """Client Hugging Face de `net.fabrique_hf`, seul porteur de `HF_TOKEN`.

    `options` est transmis à `net.fabrique_hf` (journal, transport interne des tests).
    Le client gardé retire `Authorization` à toute redirection vers un autre hôte.
    """
    client = net.fabrique_hf(**options)
    client.headers.update(en_tetes_hf(jeton))
    return client


__all__ = [
    "ArchiveInvalide",
    "MetadonneesHf",
    "ResultatFichier",
    "ShaInvalide",
    "TelechargementEchoue",
    "Telechargeur",
    "chemin_part",
    "client_hf",
    "en_tetes_hf",
    "erreur_transport",
    "jeton_hf",
    "lire_retry_after",
    "preparer_hf",
    "url_hf",
]
