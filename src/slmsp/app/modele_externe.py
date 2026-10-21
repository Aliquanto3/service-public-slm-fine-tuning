"""Fournisseurs externes de l'application (story 17.4) : réglage, client hybride, test.

Réglage `fournisseurs_externes` (table `reglages`, amendement 14) : liste ordonnée de
`MAX_FOURNISSEURS` entrées au plus, `{id, preset, url_base, modele, actif,
parametres_supplementaires}` ; l'ordre est l'ordre d'essai. Vide par défaut, appliqué au
démarrage suivant. Une entrée active au moins : le `LlmPort` du service devient un
`ClientHybride` (cascade dans l'ordre, modèle local en secours) dont les clients externes
passent par une passerelle au profil `modele-externe` (une règle par entrée active : `POST
<url_base>/chat/completions`). Aucune entrée active : rien n'est construit, aucune requête
nouvelle.

Story 17.6 : `tarif` (`{entree, sortie}`, euros par million de tokens) et `usage_flux` (demander
l'usage en fin de flux) ne valent que pour le preset `generique` ; les autres presets prennent
leur tarif dans `config/tarifs.toml`. Chaque client externe reçoit l'observateur des appels, le
compteur de dépense (plafond) et son tarif ; sans tarif, il est sauté (`tarif-inconnu`).
"""

from __future__ import annotations

import copy
import logging
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Final

from pydantic import SecretStr

from slmsp.app.cle_externe import id_valide
from slmsp.inference.client_openai import (
    DELAIS_EXTERNE,
    ClientOpenAI,
    EchecAppel,
    motif_exception,
    valider_parametres,
    valider_url_base,
    verifier_hote_gratuit,
)
from slmsp.inference.fournisseurs import PRESETS, preset
from slmsp.inference.hybride import ClientHybride
from slmsp.inference.mesures import ObservateurAppels, PlafondPort, Tarif, contexte_mesure
from slmsp.net.client import Passerelle
from slmsp.net.config import avec_modele_externe
from slmsp.net.profils import hote_de

LOGGER: Final = logging.getLogger("slmsp.app.modele_externe")
CLE_REGLAGE: Final = "fournisseurs_externes"
MAX_FOURNISSEURS: Final = 3
LONGUEUR_MAX_MODELE: Final = 200
PROFIL: Final = "modele-externe"
MESSAGE_TEST: Final = "Test de connexion."
CHAMPS: Final = frozenset(
    {"id", "preset", "url_base", "modele", "actif", "parametres_supplementaires", "tarif"}
    | {"usage_flux", "acces_gratuit"}
)
TARIF_MAX: Final = 1000.0
"""Tarif saisi au plus (euros par million de tokens) : garde-fou contre une faute de frappe."""
TACHE_TEST: Final = "test-connexion"

LecteurCle = Callable[[dict[str, Any]], SecretStr | None]
"""Entrée -> sa clé déchiffrée si elle est liée à l'hôte et au preset de l'entrée, sinon `None`."""


def liaison(entree: dict[str, Any]) -> dict[str, str]:
    """Couple auquel la clé d'une entrée est liée : `{hote, preset}`."""
    return {"hote": hote_de(entree["url_base"]), "preset": entree["preset"]}


def lecteur_cles(coffre: Any) -> LecteurCle:
    """`LecteurCle` sur un `CoffreCles` : jamais une clé liée à un autre hôte ou preset, et
    aucune clé lue pour une entrée en accès gratuit (story 17.4b)."""
    return lambda entree: (
        None if entree.get("acces_gratuit") else coffre.lire(entree["id"], **liaison(entree))
    )


def valider_entree(valeur: Any) -> dict[str, Any]:
    """Entrée normalisée ; `ValueError` (message court, sans la valeur saisie) sinon.

    URL et modèle vides prennent ceux du preset (préremplissage).
    """
    if not isinstance(valeur, dict):
        raise ValueError("fournisseur : objet attendu")
    if set(valeur) - CHAMPS:
        raise ValueError("fournisseur : clé inconnue")
    if not id_valide(valeur.get("id")):
        raise ValueError("fournisseur : identifiant invalide")
    choisi = preset(valeur.get("preset"))
    actif = valeur.get("actif", False)
    if not isinstance(actif, bool):
        raise ValueError("actif : booléen attendu")
    url_base = valeur.get("url_base") or choisi.url_base
    if url_base is None:
        raise ValueError("URL attendue")
    url_base = valider_url_base(url_base)
    modele = valeur.get("modele") or (choisi.modeles[0] if choisi.modeles else None)
    if (
        not isinstance(modele, str)
        or not modele.strip()
        or len(modele) > LONGUEUR_MAX_MODELE
        or any(c.isspace() for c in modele.strip())
    ):
        raise ValueError("modèle : identifiant attendu")
    parametres = valider_parametres(valeur.get("parametres_supplementaires") or {})
    if parametres and not choisi.parametres_libres:
        raise ValueError("paramètres supplémentaires : preset generique seulement")
    tarif = valider_tarif(valeur.get("tarif"))
    if tarif is not None and not choisi.parametres_libres:
        raise ValueError("tarif : preset generique seulement")
    usage_flux = valeur.get("usage_flux", False)
    if not isinstance(usage_flux, bool):
        raise ValueError("usage_flux : booléen attendu")
    acces_gratuit = valeur.get("acces_gratuit", False)
    if not isinstance(acces_gratuit, bool):
        raise ValueError("acces_gratuit : booléen attendu")
    if acces_gratuit:
        verifier_hote_gratuit(url_base, choisi.nom)
    return {
        "id": valeur["id"],
        "preset": choisi.nom,
        "url_base": url_base,
        "modele": modele.strip(),
        "actif": actif,
        "parametres_supplementaires": parametres,
        "tarif": tarif,
        "usage_flux": usage_flux and choisi.parametres_libres,
        "acces_gratuit": acces_gratuit,
    }


def valider_tarif(valeur: Any) -> dict[str, float] | None:
    """`{entree, sortie}` en euros par million de tokens (0 à `TARIF_MAX`), ou `None`."""
    if valeur is None:
        return None
    if not isinstance(valeur, dict) or set(valeur) != {"entree", "sortie"}:
        raise ValueError("tarif : {entree, sortie} attendu")
    tarif: dict[str, float] = {}
    for cle in ("entree", "sortie"):
        nombre = valeur[cle]
        if (
            isinstance(nombre, bool)
            or not isinstance(nombre, (int, float))
            or not 0 <= nombre <= TARIF_MAX
        ):
            raise ValueError(f"tarif : {cle} entre 0 et {TARIF_MAX:g} € par million de tokens")
        tarif[cle] = float(nombre)
    return tarif


def tarif_saisi(entree: dict[str, Any]) -> Tarif | None:
    """Tarif saisi dans les Paramètres (preset `generique`), sinon `None`."""
    tarif = entree.get("tarif")
    return Tarif(tarif["entree"], tarif["sortie"]) if isinstance(tarif, dict) else None


def valider_reglage(valeur: Any) -> list[dict[str, Any]]:
    """Liste normalisée (ordre conservé, identifiants uniques) ; `ValueError` sinon."""
    if not isinstance(valeur, list):
        raise ValueError("liste attendue")
    if len(valeur) > MAX_FOURNISSEURS:
        raise ValueError(f"{MAX_FOURNISSEURS} fournisseurs au plus")
    entrees = [valider_entree(v) for v in valeur]
    if len({e["id"] for e in entrees}) != len(entrees):
        raise ValueError("fournisseur : identifiant en double")
    return entrees


def lire_reglage(stockage: Any) -> list[dict[str, Any]]:
    """Réglage enregistré, normalisé ; un réglage illisible vaut le défaut (aucun fournisseur)."""
    try:
        return valider_reglage(copy.deepcopy(stockage.lire_reglage(CLE_REGLAGE)))
    except (ValueError, KeyError):
        LOGGER.warning("réglage fournisseurs_externes illisible : aucun fournisseur")
        return []


def actifs(entrees: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    return [e for e in entrees if e.get("actif")]


def libelle(entree: dict[str, Any]) -> str:
    """`<preset>/<modèle>` (indicateur de Mode, À propos, Historique)."""
    return f"{entree['preset']}/{entree['modele']}"


def passerelle_dediee(passerelle: Passerelle, url_bases: Sequence[str]) -> Passerelle:
    """Copie de `passerelle` (même Mode, journal, Liste blanche) dont le profil
    `modele-externe` n'a qu'une règle par URL ; la passerelle fournie n'est pas modifiée."""
    return Passerelle(
        passerelle.mode,
        passerelle.journal,
        config=avec_modele_externe(passerelle.config, list(url_bases)),
        liste_blanche=passerelle.liste_blanche,
        lib=passerelle.lib,
    )


@dataclass(frozen=True)
class Observabilite:
    """Ce que reçoit chaque client externe (story 17.6) : observateur des appels, plafond de
    dépense et résolution du tarif d'une entrée (`None` : tarif inconnu)."""

    observateur: ObservateurAppels | None = None
    plafond: PlafondPort | None = None
    tarif: Callable[[dict[str, Any]], Tarif | None] = tarif_saisi


class _PlafondFerme:
    """Plafond sans compteur : toute réservation est refusée (appel jamais envoyé)."""

    def reserver(self, hote: str, modele: str, montant: float) -> None:
        return None

    def regulariser(self, jeton: Any, cout: float) -> None:
        return None


PLAFOND_FERME: Final = _PlafondFerme()


def client_externe(
    entree: dict[str, Any],
    cle: SecretStr | None,
    dediee: Passerelle,
    *,
    transport_interne: Any = None,
    observabilite: Observabilite | None = None,
    **options: Any,
) -> ClientOpenAI:
    """`ClientOpenAI` de l'entrée, dont le client HTTP passe par la passerelle `dediee`."""
    http = dediee.client(PROFIL, transport_interne=transport_interne, delais_appel=DELAIS_EXTERNE)
    if entree.get("acces_gratuit"):
        # Accès gratuit : coût 0, pas de réservation (tarif nul posé par le client).
        options.setdefault("observateur", getattr(observabilite, "observateur", None))
        options["plafond"] = None
        options["tarif"] = None
    elif observabilite is not None and observabilite.plafond is not None:
        options.setdefault("observateur", observabilite.observateur)
        options.setdefault("plafond", observabilite.plafond)
        options.setdefault("tarif", observabilite.tarif(entree))
    else:
        # Fail-closed (revue 17.6) : sans compteur de dépense, aucun appel externe ne part.
        options.setdefault("observateur", getattr(observabilite, "observateur", None))
        options["plafond"] = PLAFOND_FERME
        options["tarif"] = None
    return ClientOpenAI(
        http,
        entree["url_base"],
        entree["modele"],
        cle,
        preset_nom=entree["preset"],
        parametres_supplementaires=entree["parametres_supplementaires"],
        usage_flux=bool(entree.get("usage_flux")),
        acces_gratuit=bool(entree.get("acces_gratuit")),
        **options,
    )


def brancher_hybride(
    assemblage: Any,
    slug_local: str,
    entrees: Sequence[dict[str, Any]],
    cles: LecteurCle,
    *,
    transport_interne: Any = None,
    observabilite: Observabilite | None = None,
) -> dict[str, Any] | None:
    """Remplace le `LlmPort` du service par un `ClientHybride` si une entrée est active.

    Rend `{tete, preset, hote, modele, secours}` (indicateur de Mode, À propos), ou `None`
    (rien n'est changé).
    """
    retenues = actifs(entrees)
    if not retenues:
        return None
    service = assemblage.service
    dediee = passerelle_dediee(assemblage.passerelle, [e["url_base"] for e in retenues])
    externes = [
        client_externe(
            e, cles(e), dediee, transport_interne=transport_interne, observabilite=observabilite
        )
        for e in retenues
    ]
    service.llm = ClientHybride(service.llm, externes, service.mode, slug_local=slug_local)
    tete = retenues[0]
    LOGGER.info(
        "fournisseurs externes actifs : %s (+%d en secours)", libelle(tete), len(retenues) - 1
    )
    return {
        "tete": libelle(tete),
        "preset": tete["preset"],
        "hote": hote_de(tete["url_base"]),
        "modele": tete["modele"],
        "secours": len(retenues) - 1,
    }


def tester_connexion(
    entree: dict[str, Any],
    cle: SecretStr | None,
    passerelle: Passerelle,
    *,
    transport_interne: Any = None,
    horloge: Callable[[], float] = time.perf_counter,
    observabilite: Observabilite | None = None,
) -> dict[str, Any]:
    """Une requête de 1 token de sortie vers l'entrée : `{reussi: True, latence_ms}` ou
    `{reussi: False, motif}` (code court). Profil ponctuel limité à cette requête ; ne lève pas.

    Story 17.6 (amendement 4) : l'appel est mesuré (Tâche `test-connexion`) et compté dans le
    plafond ; il est refusé (`plafond-atteint`, `tarif-inconnu`) comme un autre appel.
    """
    debut = horloge()
    client: ClientOpenAI | None = None
    try:
        dediee = passerelle_dediee(passerelle, [entree["url_base"]])
        client = client_externe(
            entree,
            cle,
            dediee,
            transport_interne=transport_interne,
            observabilite=observabilite,
            relances_max=0,
        )
        with contexte_mesure(tache=TACHE_TEST):
            for _ in client.generer(
                [{"role": "user", "content": MESSAGE_TEST}], options={"max_tokens": 1}
            ):
                pass
    except EchecAppel as exc:
        motif = exc.code
    except ValueError:
        motif = "reponse-invalide"
    except Exception as exc:
        motif = motif_exception(exc)
    else:
        latence = round((horloge() - debut) * 1000)
        LOGGER.info("test du fournisseur %s : réussi (%d ms)", entree["preset"], latence)
        return {
            "reussi": True,
            "latence_ms": latence,
            "hote": hote_de(entree["url_base"]),
            **_debit(client),
        }
    LOGGER.info("test du fournisseur %s : échec (%s)", entree["preset"], motif)
    return {"reussi": False, "motif": motif, "hote": hote_de(entree["url_base"]), **_debit(client)}


def _debit(client: ClientOpenAI | None) -> dict[str, Any]:
    """`{debit_restant}` si l'entrée est en accès gratuit et que le débit est connu."""
    restant = client.debit_restant if client is not None else None
    return {} if restant is None else {"debit_restant": restant}


def presets_vue() -> list[dict[str, Any]]:
    return [p.vue() for p in PRESETS.values()]


__all__ = [
    "CLE_REGLAGE",
    "MAX_FOURNISSEURS",
    "Observabilite",
    "actifs",
    "brancher_hybride",
    "client_externe",
    "lecteur_cles",
    "liaison",
    "libelle",
    "lire_reglage",
    "presets_vue",
    "tarif_saisi",
    "tester_connexion",
    "valider_entree",
    "valider_reglage",
    "valider_tarif",
]
