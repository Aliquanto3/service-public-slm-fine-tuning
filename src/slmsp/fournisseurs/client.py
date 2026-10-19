"""Client compatible OpenAI (Chat Completions) : point d'appel sous budget, journalisé (S3).

`ClientCompatibleOpenAI.appeler(usage, session_id, messages, modele=…, max_tokens=…)` est
générique (messages → texte, usage, coût) et déroule, par tentative :

1. la réservation au pire cas (`RegistreBudget.reserver`, `max_tokens` en sortie) au poste
   de l'usage (`juge-tiers-openrouter`, plus tard `generateur-openrouter` pour S4) ;
2. un `POST <base_url>/chat/completions` par la passerelle réseau (profil `outillage`,
   délais explicites `DelaisAppel`), clé en en-tête `Authorization`, jamais journalisée ;
3. le journal de la tentative (`JournalAppels`), coût annoncé par le fournisseur compris
   (`usage.cost` d'OpenRouter, en USD) ;
4. le règlement : au coût réel du tarif (`tarifs.toml`) pour une réponse 200, à 0 pour une
   réponse d'erreur HTTP ou une requête bloquée avant l'envoi (`SlmspError`), au pire cas
   pour une erreur sans réponse HTTP ou une réponse 200 illisible.

Une tentative en échec transitoire (429, 500, 502, 503, 504, transport) est relancée
(`Retry-After`, sinon attente exponentielle avec gigue) dans les bornes de
`ConfigFournisseur` ; au-delà, `ErreurApiFournisseur` est levée. Chaque tentative a sa
réservation, réglée avant la suivante.

`lister_modeles()` fait un `GET <base_url>/models` (gratuit, sans budget ni génération).
"""

from __future__ import annotations

import json
import logging
import random
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from pydantic import SecretStr

from slmsp.budget.registre import RegistreBudget
from slmsp.budget.tarifs import UsageTokens
from slmsp.core.erreurs import SecretManquant, SlmspError
from slmsp.core.ports import JournalRequetes
from slmsp.core.secrets import secret
from slmsp.fournisseurs.journal import JournalAppels
from slmsp.net import client as client_reseau
from slmsp.net.relances import (
    DelaisAppel,
    attente_exponentielle,
    echeance_globale,
    erreur_transport,
    lire_retry_after,
    statut_transitoire,
)

__all__ = [
    "FOURNISSEURS",
    "OPENROUTER",
    "ClientCompatibleOpenAI",
    "ConfigFournisseur",
    "ErreurApiFournisseur",
    "ReponseChat",
    "fabriquer_http",
    "lire_cle",
]

MODE: Final = "direct"
"""Mode tarifaire : appels directs seulement."""
CLES_RESERVEES: Final = frozenset({"model", "messages", "max_tokens"})

_JOURNAL = logging.getLogger(__name__)


@dataclass(frozen=True)
class ConfigFournisseur:
    """Fournisseur compatible OpenAI : URL de base, nom du secret, délais et relances."""

    nom: str
    base_url: str
    nom_secret: str
    delai_appel: float = 300.0
    delai_connexion: float = 10.0
    delai_lecture: float = 300.0
    reessais_max: int = 3
    attente_base: float = 2.0
    attente_plafond: float = 60.0
    attente_totale_max: float = 300.0
    duree_totale_max_appel: float = 900.0

    def url(self, chemin: str) -> str:
        return f"{self.base_url.rstrip('/')}/{chemin.lstrip('/')}"

    def delais(self) -> DelaisAppel:
        return DelaisAppel(self.delai_connexion, self.delai_lecture, self.delai_appel)


OPENROUTER: Final = ConfigFournisseur(
    nom="openrouter", base_url="https://openrouter.ai/api/v1", nom_secret="OPENROUTER_API_KEY"
)
FOURNISSEURS: Final[Mapping[str, ConfigFournisseur]] = {"openrouter": OPENROUTER}


class ErreurApiFournisseur(SlmspError):
    """Échec d'un appel (refus HTTP, erreur serveur, réseau ou réponse illisible).

    `statut_http` vaut `None` sans réponse HTTP ; `cout_eur` est le montant compté au
    registre pour la dernière tentative ; `transitoire` : relançable ; `reessais` : nombre
    de réessais faits avant d'abandonner.
    """

    def __init__(
        self,
        message: str,
        statut_http: int | None,
        cout_eur: float,
        *,
        transitoire: bool = False,
        attente_serveur: float | None = None,
    ) -> None:
        super().__init__(message)
        self.statut_http = statut_http
        self.cout_eur = cout_eur
        self.transitoire = transitoire
        self.attente_serveur = attente_serveur
        self.reessais = 0


@dataclass(frozen=True)
class ReponseChat:
    """Réponse d'un appel réussi : texte, modèle résolu, tokens, coûts et journal."""

    texte: str
    modele_resolu: str
    finish_reason: str | None
    usage: UsageTokens
    cout_eur: float
    """Coût réglé au registre (tarif de `tarifs.toml`)."""
    cout_fournisseur_usd: float | None
    """Coût annoncé par le fournisseur (`usage.cost`), journalisé ; `None` s'il est absent."""
    appel_id: str
    reservation_id: int


def fabriquer_http(
    config: ConfigFournisseur,
    *,
    transport_interne: Any = None,
    journal_requetes: JournalRequetes | None = None,
) -> Any:
    """Client HTTP gardé du profil `outillage`, délais explicites de `config`, sans relance."""
    return client_reseau(
        "outillage",
        transport_interne=transport_interne,
        journal=journal_requetes,
        delais_appel=config.delais(),
    )


def lire_cle(config: ConfigFournisseur, fichier_env: str | Path | None = None) -> SecretStr:
    """Clé du fournisseur lue dans le `.env` ; `SecretManquant` (sans valeur) si absente."""
    return secret(config.nom_secret, fichier_env)


def _texte(corps: Mapping[str, Any]) -> tuple[str, str | None]:
    choix = corps["choices"]
    if not isinstance(choix, list) or not choix:
        raise ValueError("réponse sans choix")
    premier = choix[0]
    raison = premier.get("finish_reason")
    contenu = (premier.get("message") or {}).get("content")
    if isinstance(contenu, list):
        contenu = "".join(
            m.get("text", "") for m in contenu if isinstance(m, dict) and m.get("type") == "text"
        )
    return (contenu if isinstance(contenu, str) else ""), (None if raison is None else str(raison))


def _usage(corps: Mapping[str, Any]) -> tuple[UsageTokens, float | None]:
    """Tokens (sortie = raisonnement compris) et coût annoncé (`usage.cost`, USD)."""
    usage = corps.get("usage") or {}
    entree = int(usage.get("prompt_tokens") or 0)
    sortie = int(usage.get("completion_tokens") or 0)
    total = int(usage.get("total_tokens") or 0)
    # Prudence : certains fournisseurs comptent le raisonnement hors `completion_tokens`.
    sortie = max(sortie, total - entree)
    cout = usage.get("cost")
    cout_usd = float(cout) if isinstance(cout, int | float) and not isinstance(cout, bool) else None
    return UsageTokens(entree, sortie), cout_usd


def _entetes(config: ConfigFournisseur, cle: SecretStr | None, *, exiger: bool) -> dict[str, str]:
    if cle is None:
        if exiger:
            raise SecretManquant(
                f"secret « {config.nom_secret} » absent : appel {config.nom} refusé"
            )
        return {}
    return {"Authorization": f"Bearer {cle.get_secret_value()}"}


def lister_modeles(
    config: ConfigFournisseur, http: Any, cle: SecretStr | None
) -> list[dict[str, Any]]:
    """Modèles du fournisseur (`GET /models`, gratuit) ; `ErreurApiFournisseur` en cas d'échec."""
    try:
        reponse = http.get(config.url("models"), headers=_entetes(config, cle, exiger=False))
    except SlmspError:
        raise
    except Exception as exc:
        raise ErreurApiFournisseur(
            f"{config.nom} : liste des modèles sans réponse HTTP ({type(exc).__name__})", None, 0.0
        ) from None
    if reponse.status_code != 200:
        raise ErreurApiFournisseur(
            f"{config.nom} : liste des modèles, réponse HTTP {reponse.status_code}",
            reponse.status_code,
            0.0,
        )
    try:
        donnees = json.loads(reponse.content)["data"]
    except (ValueError, KeyError, TypeError):
        raise ErreurApiFournisseur(
            f"{config.nom} : liste des modèles illisible", 200, 0.0
        ) from None
    return [m for m in donnees if isinstance(m, dict) and isinstance(m.get("id"), str)]


class ClientCompatibleOpenAI:
    """Point d'appel d'une API Chat Completions compatible OpenAI : budget, journal, relances."""

    def __init__(
        self,
        config: ConfigFournisseur,
        registre: RegistreBudget,
        http: Any,
        cle: SecretStr | None,
        *,
        journal: JournalAppels,
        dormir: Callable[[float], None] = time.sleep,
        alea: Callable[[], float] = random.random,
        horloge: Callable[[], float] = time.monotonic,
    ) -> None:
        self.config = config
        self.registre = registre
        self.http = http
        self._cle = cle
        self.journal = journal
        self._dormir = dormir
        self._alea = alea
        self._horloge = horloge

    def lister_modeles(self) -> list[dict[str, Any]]:
        """Modèles du fournisseur (`GET /models`), sans budget (voir `lister_modeles`)."""
        return lister_modeles(self.config, self.http, self._cle)

    # --- appel générique ---------------------------------------------------------------------

    def appeler(
        self,
        usage: str,
        session_id: str,
        messages: Sequence[Mapping[str, Any]],
        *,
        modele: str,
        max_tokens: int,
        tokens_entree_estimes: int,
        parametres: Mapping[str, Any] | None = None,
    ) -> ReponseChat:
        """Un appel `chat/completions` de `modele` pour `usage` (voir le module).

        `parametres` complète le corps (`temperature`, `response_format`, `reasoning`…) sans
        pouvoir remplacer `model`, `messages` ni `max_tokens` (`ValueError`). Lève
        `SecretManquant` ou `ConfigurationInvalide` (usage inconnu) avant toute réservation,
        `BudgetEpuise` (rien n'est envoyé), `TarifInconnu`, et `ErreurApiFournisseur` après un
        échec journalisé, définitif ou transitoire au-delà des bornes de relance.
        """
        extra = dict(parametres or {})
        if CLES_RESERVEES & extra.keys():
            raise ValueError(f"paramètres réservés : {sorted(CLES_RESERVEES & extra.keys())}")
        entetes = _entetes(self.config, self._cle, exiger=True)
        self.registre.imputer(usage)  # ConfigurationInvalide avant tout envoi
        corps: dict[str, Any] = {
            "model": modele,
            "messages": [dict(m) for m in messages],
            "max_tokens": max_tokens,
            **extra,
        }
        debut = self._horloge()
        attente_cumulee = 0.0
        reessai = 0
        while True:
            restant = self.config.duree_totale_max_appel - (self._horloge() - debut)
            try:
                with echeance_globale(restant):
                    return self._tentative(usage, session_id, corps, entetes, tokens_entree_estimes)
            except ErreurApiFournisseur as exc:
                attente = self._attente(exc, reessai + 1, attente_cumulee, debut)
                if attente is None:
                    if reessai:
                        exc.reessais = reessai
                        exc.args = (f"{exc.args[0]} après {reessai} réessai(s)",)
                    raise
                reessai += 1
                attente_cumulee += attente
                _JOURNAL.warning(
                    "relance API %s : horodatage=%s usage=%s code=%s réessai=%d/%d attente=%.1fs",
                    self.config.nom,
                    datetime.now(UTC).isoformat(timespec="seconds"),
                    usage,
                    exc.statut_http if exc.statut_http is not None else "transport",
                    reessai,
                    self.config.reessais_max,
                    attente,
                )
                self._dormir(attente)

    def _attente(
        self, exc: ErreurApiFournisseur, reessai: int, attente_cumulee: float, debut: float
    ) -> float | None:
        config = self.config
        if not exc.transitoire or reessai > config.reessais_max:
            return None
        if exc.attente_serveur is not None:
            attente = max(exc.attente_serveur, config.attente_base)
        else:
            attente = attente_exponentielle(
                reessai, config.attente_base, config.attente_plafond, self._alea
            )
        if attente_cumulee + attente > config.attente_totale_max:
            return None
        ecoule = self._horloge() - debut
        if ecoule + attente + config.delai_appel > config.duree_totale_max_appel:
            return None
        return attente

    def _tentative(
        self,
        usage: str,
        session_id: str,
        corps: dict[str, Any],
        entetes: Mapping[str, str],
        tokens_entree_estimes: int,
    ) -> ReponseChat:
        modele = corps["model"]
        poste, sous_poste = self.registre.imputer(usage)
        reservation_id = self.registre.reserver(
            poste, sous_poste, modele, MODE, tokens_entree_estimes, corps["max_tokens"]
        )

        def inscrire(**champs: Any) -> str:
            return self.journal.inscrire(
                session_id=session_id,
                fournisseur=self.config.nom,
                usage=usage,
                modele_demande=modele,
                requete=corps,
                reservation_id=reservation_id,
                **champs,
            )

        try:
            reponse = self.http.post(
                self.config.url("chat/completions"), json=corps, headers=dict(entetes)
            )
        except BaseException as exc:
            try:
                inscrire(modele_resolu=None, reponse_brute=None, statut="erreur", statut_http=None)
            finally:
                # Une `SlmspError` (`HoteBloque`…) part avant tout envoi : rien n'est facturé.
                cout = self._regler_echec(reservation_id, not isinstance(exc, SlmspError))
            if not isinstance(exc, Exception) or isinstance(exc, SlmspError):
                raise
            raise ErreurApiFournisseur(
                f"API {self.config.nom} : échec sans réponse HTTP ({type(exc).__name__}, {usage})",
                None,
                cout,
                transitoire=erreur_transport(exc),
            ) from None

        brut = bytes(reponse.content)
        statut = int(reponse.status_code)
        if statut != 200:
            try:
                inscrire(
                    modele_resolu=None, reponse_brute=brut, statut="erreur", statut_http=statut
                )
            finally:
                cout = self._regler_echec(reservation_id, False)
            valeur = reponse.headers.get("Retry-After")
            raise ErreurApiFournisseur(
                f"API {self.config.nom} : réponse HTTP {statut} ({usage})",
                statut,
                cout,
                transitoire=statut_transitoire(statut),
                attente_serveur=lire_retry_after(valeur if isinstance(valeur, str) else None),
            )
        try:
            donnees = json.loads(brut)
            texte, raison = _texte(donnees)
            usage_tokens, cout_usd = _usage(donnees)
            modele_resolu = str(donnees.get("model") or "")
        except (ValueError, KeyError, TypeError, AttributeError):
            # Réponse 200 illisible : facturée d'usage inconnu, comptée au pire cas.
            try:
                inscrire(modele_resolu=None, reponse_brute=brut, statut="erreur", statut_http=200)
            finally:
                cout = self._regler_echec(reservation_id, True)
            raise ErreurApiFournisseur(
                f"API {self.config.nom} : réponse 200 illisible ({usage})", 200, cout
            ) from None
        try:
            appel_id = inscrire(
                modele_resolu=modele_resolu or None,
                reponse_brute=brut,
                statut="ok",
                statut_http=200,
                tokens=(usage_tokens.entree, usage_tokens.sortie),
                cout_fournisseur_usd=cout_usd,
            )
        finally:
            cout = self.registre.regulariser(reservation_id, usage_tokens)
        return ReponseChat(
            texte=texte,
            modele_resolu=modele_resolu,
            finish_reason=raison,
            usage=usage_tokens,
            cout_eur=cout,
            cout_fournisseur_usd=cout_usd,
            appel_id=appel_id,
            reservation_id=reservation_id,
        )

    def _regler_echec(self, reservation_id: int, facture: bool) -> float:
        if facture:
            return self.registre.compter_pire_cas(reservation_id)
        return self.registre.regulariser(reservation_id, UsageTokens(0, 0))


def nouvelle_session(prefixe: str) -> str:
    """Identifiant de session `<prefixe><uuid4 hex>`."""
    return f"{prefixe}{uuid.uuid4().hex}"


# --- vérification sans dépense -----------------------------------------------------------------

PREFIXES_VERIFICATION: Final = ("deepseek/", "z-ai/", "mistralai/", "moonshotai/", "xiaomi/")
"""Familles retenues dans `--verifier` (GPT et Gemini exclus, décision du 2026-10-19)."""
MOTIFS_VERIFICATION: Final = ("zhipu",)


def retenu(identifiant: str) -> bool:
    """Vrai si le modèle `identifiant` appartient à une famille retenue."""
    bas = identifiant.lower()
    return bas.startswith(PREFIXES_VERIFICATION) or any(m in bas for m in MOTIFS_VERIFICATION)


def _prix_mtok(valeur: Any) -> float | None:
    try:
        return round(float(valeur) * 1_000_000, 4)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class Verification:
    """Bilan de `--verifier` pour un fournisseur : clé, modèles retenus ou erreur."""

    fournisseur: str
    nom_secret: str
    cle_presente: bool
    modeles: tuple[dict[str, Any], ...] = ()
    erreur: str | None = None


def verifier(
    config: ConfigFournisseur,
    *,
    fichier_env: str | Path | None = None,
    transport_interne: Any = None,
    journal_requetes: JournalRequetes | None = None,
) -> Verification:
    """Clé présente ou absente (jamais levée ni affichée) et modèles retenus (`GET /models`).

    Aucune génération, aucune réservation : le registre n'est pas ouvert.
    """
    try:
        cle: SecretStr | None = lire_cle(config, fichier_env)
    except SecretManquant:
        cle = None
    http = fabriquer_http(
        config, transport_interne=transport_interne, journal_requetes=journal_requetes
    )
    try:
        bruts = lister_modeles(config, http, cle)
    except (ErreurApiFournisseur, SlmspError) as exc:
        return Verification(config.nom, config.nom_secret, cle is not None, erreur=str(exc))
    modeles = []
    for modele in sorted(bruts, key=lambda m: m["id"]):
        if not retenu(modele["id"]):
            continue
        prix = modele.get("pricing") or {}
        modeles.append(
            {
                "id": modele["id"],
                "entree_usd_mtok": _prix_mtok(prix.get("prompt")),
                "sortie_usd_mtok": _prix_mtok(prix.get("completion")),
                "contexte": modele.get("context_length"),
            }
        )
    return Verification(config.nom, config.nom_secret, cle is not None, tuple(modeles))
