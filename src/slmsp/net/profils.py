"""Profils de la passerelle et décision d'autorisation d'une requête (AD-4).

`evaluer` contrôle, dans cet ordre :

1. le Mode : en `hors-ligne-force`, tout est refusé ; en `hors-ligne-detecte`, seule la
   sonde (`GET <sonde.url>`) passe ;
2. la forme de l'URL : HTTPS seulement, port par défaut (443), ni adresse IP, ni
   identifiants dans l'URL ;
3. le profil : `assistant` (Liste blanche, correspondance exacte du nom d'hôte),
   `outillage` (règles de `config/reseau.toml`), `aucun` (tout refusé), `eval-distant`
   (règles de `config/reseau.toml`, sans Liste blanche : génération distante, story 17.1),
   `modele-externe` (une règle par fournisseur externe actif, calculée au lancement, sans
   Liste blanche, story 17.4).

Un nom d'hôte est normalisé (minuscules, point final retiré) avant toute comparaison.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final, Literal, get_args

import httpx2

from slmsp.core.ports import Mode, ModePort
from slmsp.core.schemas.journal_requetes import ProfilReseau

if TYPE_CHECKING:
    from slmsp.net.config import ConfigListeBlanche, ConfigReseau

PROFILS: Final[tuple[str, ...]] = get_args(ProfilReseau)
"""Profils connus de la passerelle."""

MODES: Final[frozenset[str]] = frozenset(get_args(Mode))

METHODES_LECTURE: Final = frozenset({"GET", "HEAD"})

StatutBloque = Literal["bloquee-liste", "bloquee-mode"]


@dataclass(frozen=True)
class Verdict:
    """Décision sur une requête : autorisée (`statut is None`) ou bloquée avec un motif."""

    statut: StatutBloque | None = None
    motif: str | None = None

    @property
    def autorise(self) -> bool:
        return self.statut is None


AUTORISE: Final = Verdict()
MODE_ILLISIBLE: Final = Verdict("bloquee-mode", "Mode inconnu ou illisible")


@dataclass(frozen=True)
class LectureMode:
    """Mode lu sur un `ModePort` ; `illisible` si la lecture a levé ou rendu une valeur
    hors `Mode` (la requête est alors refusée : fermeture par défaut)."""

    mode: Mode | None = None
    illisible: bool = False
    erreur: Exception | None = None


def lire_mode(port: ModePort | None) -> LectureMode:
    """Lit `port.mode_courant()` sans jamais lever ; `None` si aucun port n'est fourni."""
    if port is None:
        return LectureMode()
    try:
        valeur = port.mode_courant()
    except Exception as exc:
        return LectureMode(illisible=True, erreur=exc)
    if not isinstance(valeur, str) or valeur not in MODES:
        return LectureMode(illisible=True)
    return LectureMode(valeur)


@dataclass(frozen=True)
class Cible:
    """Éléments d'URL utiles à la décision (jamais l'URL complète)."""

    schema: str
    hote: str
    port: int | None
    chemin: str
    requete: str
    identifiants: bool


def normaliser_hote(hote: str) -> str:
    """Minuscules, crochets IPv6 et point final retirés."""
    hote = hote.strip().lower()
    if hote.startswith("[") and hote.endswith("]"):
        hote = hote[1:-1]
    if hote.endswith("."):
        hote = hote[:-1]
    return hote


def est_adresse_ip(hote: str) -> bool:
    """Vrai pour une adresse IPv4 ou IPv6, y compris les formes numériques abrégées.

    Un nom dont le dernier label n'est fait que de chiffres (`1.2.3`, `16843009`) est traité
    comme une adresse : aucun domaine de premier niveau n'est numérique, et certains
    résolveurs l'interprètent comme une IPv4.
    """
    hote = normaliser_hote(hote)
    if not hote:
        return False
    try:
        ipaddress.ip_address(hote.split("%", 1)[0])
    except ValueError:
        pass
    else:
        return True
    if ":" in hote:
        return True
    dernier = hote.rsplit(".", 1)[-1]
    return dernier.isdigit() or (dernier.startswith("0x") and len(dernier) > 2)


def analyser_url(url: Any) -> Cible:
    """Décompose `url` (chaîne ou `URL` de httpx/httpx2) ; lève `ValueError` si illisible."""
    if isinstance(url, str):
        try:
            url = httpx2.URL(url)
        except Exception as exc:  # httpx2.InvalidURL et assimilés
            raise ValueError("URL illisible") from exc
    raw_host = url.raw_host
    hote = raw_host.decode("ascii", errors="replace") if isinstance(raw_host, bytes) else raw_host
    return Cible(
        schema=str(url.scheme).lower(),
        hote=normaliser_hote(hote),
        port=url.port,
        chemin=url.path,
        requete=url.query.decode("ascii", errors="replace")
        if isinstance(url.query, bytes)
        else str(url.query),
        identifiants=bool(url.userinfo),
    )


def hote_de(url: Any) -> str:
    """Hôte normalisé de `url`, ou chaîne vide si l'URL est illisible."""
    try:
        return analyser_url(url).hote
    except ValueError:
        return ""


def _est_sonde(methode: str, cible: Cible, config: ConfigReseau) -> bool:
    sonde = analyser_url(config.sonde.url)
    return (
        methode == "GET"
        and cible.schema == sonde.schema
        and cible.hote == sonde.hote
        and cible.port == sonde.port
        and cible.chemin == sonde.chemin
        and cible.requete == sonde.requete
        and not cible.identifiants
    )


def _bloque_liste(motif: str) -> Verdict:
    return Verdict("bloquee-liste", motif)


def _forme(cible: Cible) -> Verdict:
    if cible.schema != "https":
        return _bloque_liste("HTTPS seulement")
    if cible.port is not None and cible.port != 443:
        return _bloque_liste("port autre que 443")
    if not cible.hote:
        return _bloque_liste("hôte absent")
    if est_adresse_ip(cible.hote):
        return _bloque_liste("adresse IP refusée")
    if cible.identifiants:
        return _bloque_liste("identifiants dans l'URL")
    return AUTORISE


def correspond_suffixe(hote: str, suffixe: str) -> bool:
    """Vrai si `hote` est `suffixe` ou l'un de ses sous-domaines (frontière de label)."""
    return hote == suffixe or hote.endswith("." + suffixe)


def evaluer(
    profil: str,
    methode: str,
    url: Any,
    *,
    mode: Mode | None,
    config: ConfigReseau,
    liste_blanche: ConfigListeBlanche,
) -> Verdict:
    """Décide si la requête `methode url` est permise pour `profil` dans `mode`.

    `mode` vaut `None` quand aucun `ModePort` n'est fourni (profils `outillage`, `aucun`) :
    seul le contrôle de profil s'applique alors. Lève `ValueError` pour un profil inconnu.
    """
    if profil not in PROFILS:
        raise ValueError(f"profil inconnu : {profil!r} (attendu : {', '.join(PROFILS)})")
    if mode is not None and (not isinstance(mode, str) or mode not in MODES):
        return MODE_ILLISIBLE
    methode = methode.upper()
    try:
        cible = analyser_url(url)
    except ValueError:
        cible = None

    if mode == "hors-ligne-force":
        return Verdict("bloquee-mode", "Mode hors ligne forcé")
    if mode == "hors-ligne-detecte" and (cible is None or not _est_sonde(methode, cible, config)):
        return Verdict("bloquee-mode", "Mode hors ligne détecté : seule la sonde passe")

    if cible is None:
        return _bloque_liste("URL illisible")
    forme = _forme(cible)
    if not forme.autorise:
        return forme

    if profil == "aucun":
        return _bloque_liste("profil aucun : toute requête est refusée")
    if profil == "assistant":
        if cible.hote in liste_blanche.hotes:
            return AUTORISE
        return _bloque_liste("hôte hors Liste blanche")

    regles = {
        "outillage": config.profils.outillage,
        "eval-distant": config.profils.eval_distant,
        "modele-externe": config.profils.modele_externe,
    }[profil]
    if (
        regles.liste_blanche_en_lecture
        and methode in METHODES_LECTURE
        and cible.hote in liste_blanche.hotes
    ):
        return AUTORISE
    for regle in regles.regles:
        if methode not in regle.methodes:
            continue
        if not (
            cible.hote in regle.hotes
            or any(correspond_suffixe(cible.hote, s) for s in regle.suffixes)
        ):
            continue
        if regle.chemins and cible.chemin not in regle.chemins:
            continue
        return AUTORISE
    return _bloque_liste(f"aucune règle du profil {profil} ne permet cette requête")
