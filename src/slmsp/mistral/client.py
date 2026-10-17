"""Client Mistral : point d'appel unique, sous budget, journalisé, relances bornées (AD-3).

`ClientMistral.appeler(usage, ...)` déroule, dans cet ordre :

1. les contrôles : usage connu (`generation` refusé, réservé au `Generateur` de
   `slmsp.mistral.generateur` par un jeton de preuve et la méta de gabarit et d'amorces
   passée par `complements_journal`), modèle demandé dans la liste stable ;
2. la réservation au pire cas (`RegistreBudget.reserver`) au sous-poste de l'usage ;
3. un appel `chat.complete` (`retries=None` : aucune relance du SDK), sous les délais
   explicites de `config/mistral.toml` imposés par la passerelle réseau ;
4. le journal de l'usage (requête canonique, corps brut de la réponse, SHA, référence
   budget) ;
5. la régularisation au coût réel (`regulariser`), à 0 pour une réponse d'erreur HTTP non
   facturée (4xx, 429, 5xx) ou une requête bloquée avant l'envoi (`SlmspError`, dont
   `HoteBloque`), ou au pire cas (`compter_pire_cas`) pour une erreur sans réponse HTTP
   (réseau, délai dépassé : on ne sait pas si le serveur a traité la requête) ;
6. le contrôle du modèle résolu (champ `model` de la réponse) : `ModeleMistralRefuse` s'il
   sort de la liste stable ou porte un motif interdit, l'appel restant journalisé et payé.

Les étapes 2 à 5 forment une tentative. Une tentative en échec transitoire (HTTP 429, 500,
502, 503, 504, erreur de transport ou délai dépassé) est relancée après une attente
(`Retry-After`, au moins `attente_base`, sinon exponentielle avec gigue), dans les bornes
`reessais_max`, `attente_totale_max` et `duree_totale_max_appel` (appel entier, tentatives
et attentes comprises) ; au-delà, `ErreurApiMistral` est levée. Chaque tentative a sa propre
réservation, réglée (et journalisée) avant la suivante : rien n'est compté deux fois.
Chaque relance est consignée (journal `slmsp.mistral.client` : horodatage, code, attente),
sans corps ni en-tête.

Réservation et coût se font au tarif du modèle demandé, seul tarifé dans `tarifs.toml`.

Le SDK n'est construit que par `fabriquer_sdk` : clients HTTP synchrone et asynchrone du
profil `outillage` (`slmsp.net`), URL de l'API fixée, aucune relance, aucun journal de
débogage du SDK (il écrirait les en-têtes, donc la clé).
"""

from __future__ import annotations

import json
import logging
import random
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from mistralai.client import Mistral
from mistralai.client.errors import MistralError
from mistralai.client.utils.logger import NoOpLogger

from slmsp.budget.registre import RegistreBudget
from slmsp.budget.tarifs import UsageTokens
from slmsp.core.erreurs import SlmspError
from slmsp.core.ports import JournalRequetes
from slmsp.core.secrets import secret
from slmsp.mistral import journal as journal_mistral
from slmsp.mistral.config import ConfigMistral
from slmsp.mistral.journal import USAGES, UsageInterdit, journal_pour
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
    "ClientMistral",
    "ErreurApiMistral",
    "ModeleMistralRefuse",
    "ReponseMistral",
    "UsageInterdit",
    "fabriquer_sdk",
]

URL_API: Final = "https://api.mistral.ai"
NOM_SECRET: Final = "MISTRAL_API_KEY"
MODULE_GENERATEUR: Final = journal_mistral.MODULE_GENERATEUR
USAGE_GENERATION: Final = "generation"
CLES_COMPLEMENTS: Final = ("gabarit_id", "version_gabarit", "sha256_gabarit", "amorce_ids")
"""Méta admise dans `complements_journal` (ligne `generation` du journal)."""
MODE: Final = "direct"
"""Mode tarifaire : appels directs seulement (aucun mode batch Mistral)."""

_JOURNAL = logging.getLogger(__name__)


class ModeleMistralRefuse(SlmspError):
    """Modèle demandé ou résolu hors de la liste stable, ou portant un motif interdit."""


class ErreurApiMistral(SlmspError):
    """Échec d'un appel à l'API Mistral (refus HTTP, erreur serveur ou réseau).

    `statut_http` vaut `None` sans réponse HTTP ; `cout_eur` est le montant compté au
    registre pour la dernière tentative (0 pour une réponse d'erreur HTTP, le pire cas sans
    réponse HTTP).
    `transitoire` : l'échec est relançable (429, 5xx passagère, transport) ;
    `attente_serveur` : attente demandée par `Retry-After` ; `reessais` : nombre de
    réessais faits avant d'abandonner.
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
class ReponseMistral:
    """Réponse d'un appel réussi : texte, modèle résolu, tokens, coût réel et journal."""

    texte: str
    modele_resolu: str
    finish_reason: str | None
    usage: UsageTokens
    cout_eur: float
    appel_id: str
    reservation_id: int


def fabriquer_sdk(
    config: ConfigMistral,
    transport_interne: Any = None,
    journal_requetes: JournalRequetes | None = None,
    fichier_env: str | Path | None = None,
) -> Mistral:
    """SDK `mistralai` sur les clients HTTP gardés du profil `outillage`, sans relance.

    Les délais de connexion, de lecture et l'échéance totale de `config` sont imposés à
    chaque requête par la passerelle réseau (`delais_appel`).

    La clé est lue dans le `.env` (`SLMSP_ENV_FILE`, ou `fichier_env`) et n'apparaît dans
    aucun message. Lève `SecretManquant` si elle est absente.
    """
    cle = secret(NOM_SECRET, fichier_env)
    delais = delais_appel(config)
    return Mistral(
        api_key=cle.get_secret_value(),
        server_url=URL_API,
        client=client_reseau(
            "outillage",
            transport_interne=transport_interne,
            journal=journal_requetes,
            delais_appel=delais,
        ),
        async_client=client_reseau(
            "outillage",
            asynchrone=True,
            transport_interne=transport_interne,
            journal=journal_requetes,
            delais_appel=delais,
        ),
        retry_config=None,
        timeout_ms=_delai_ms(config),
        debug_logger=NoOpLogger(),
    )


def delais_appel(config: ConfigMistral) -> DelaisAppel:
    """Délais explicites d'une tentative : connexion, lecture, total (`delai_appel`)."""
    return DelaisAppel(config.delai_connexion, config.delai_lecture, config.delai_appel)


def _delai_ms(config: ConfigMistral) -> int:
    return max(1, round(config.delai_appel * 1000))


def _jeton_generateur() -> object | None:
    """Jeton de preuve du Générateur (`slmsp.mistral.generateur._JETON`), s'il existe.

    Délègue à `slmsp.mistral.journal.jeton_generateur`, qui contrôle aussi l'inscription.
    """
    return journal_mistral.jeton_generateur()


class _Capture:
    """Hooks du SDK : corps de la requête envoyée et corps brut de la réponse reçue."""

    def __init__(self) -> None:
        self.requete: bytes | None = None
        self.reponse: bytes | None = None

    def reinitialiser(self) -> None:
        self.requete = None
        self.reponse = None

    def before_request(self, hook_ctx: Any, request: Any) -> Any:
        try:
            contenu = request.content
        except Exception:  # corps en flux : la requête canonique retombe sur les paramètres
            contenu = None
        self.requete = bytes(contenu) if isinstance(contenu, (bytes, bytearray)) else None
        return request

    def after_success(self, hook_ctx: Any, response: Any) -> Any:
        self.reponse = bytes(response.content)
        return response


def _texte(reponse: Any) -> tuple[str, str | None]:
    """Texte du premier choix (chaîne ou morceaux `text`) et sa `finish_reason`."""
    choix = getattr(reponse, "choices", None) or []
    if not choix:
        return "", None
    premier = choix[0]
    raison = getattr(premier, "finish_reason", None)
    raison = None if raison is None else str(getattr(raison, "value", raison))
    message = getattr(premier, "message", None)
    contenu = getattr(message, "content", None)
    if isinstance(contenu, str):
        return contenu, raison
    morceaux = []
    for morceau in contenu or []:
        texte = getattr(morceau, "text", None)
        if isinstance(texte, str):
            morceaux.append(texte)
    return "".join(morceaux), raison


def _usage(reponse: Any) -> UsageTokens:
    usage = getattr(reponse, "usage", None)
    return UsageTokens(
        int(getattr(usage, "prompt_tokens", 0) or 0),
        int(getattr(usage, "completion_tokens", 0) or 0),
    )


def _retry_after(exc: MistralError) -> float | None:
    try:
        valeur = exc.raw_response.headers.get("Retry-After")
    except Exception:
        return None
    return lire_retry_after(valeur if isinstance(valeur, str) else None)


def _corps_erreur(exc: MistralError) -> bytes | None:
    try:
        contenu = exc.raw_response.content
    except Exception:
        return None
    return bytes(contenu) if isinstance(contenu, (bytes, bytearray)) else None


class ClientMistral:
    """Point d'appel unique de l'API Mistral : budget, journal, modèle résolu vérifié."""

    def __init__(
        self,
        config: ConfigMistral,
        registre: RegistreBudget,
        sdk: Mistral,
        *,
        dossier_journaux: str | Path | None = None,
        dormir: Callable[[float], None] = time.sleep,
        alea: Callable[[], float] = random.random,
        horloge: Callable[[], float] = time.monotonic,
    ) -> None:
        self.config = config
        self.registre = registre
        self.sdk = sdk
        self.dossier_journaux = dossier_journaux
        self._dormir = dormir
        self._alea = alea
        self._horloge = horloge
        self._capture = _Capture()
        hooks = sdk.sdk_configuration.__dict__["_hooks"]
        hooks.register_before_request_hook(self._capture)
        hooks.register_after_success_hook(self._capture)

    def appeler(
        self,
        usage: str,
        session_id: str,
        messages: Sequence[Mapping[str, Any]],
        *,
        max_tokens: int,
        tokens_entree_estimes: int,
        temperature: float | None = None,
        response_format: Mapping[str, Any] | None = None,
    ) -> ReponseMistral:
        """Un appel `chat.complete` pour `usage` (`juge-second`, `validation`).

        Lève `UsageInterdit` (usage inconnu ou `generation`) ou `ModeleMistralRefuse`
        (modèle demandé) avant toute réservation ; `BudgetEpuise` (rien n'est envoyé) ;
        `ErreurApiMistral` après un échec journalisé, définitif ou transitoire au-delà des
        bornes de relance ; `ModeleMistralRefuse` après un appel
        journalisé et payé dont le modèle résolu est refusé.
        """
        return self._appeler(
            usage,
            session_id,
            messages,
            max_tokens=max_tokens,
            tokens_entree_estimes=tokens_entree_estimes,
            temperature=temperature,
            response_format=response_format,
            jeton=None,
        )

    def _controler(self, usage: str, jeton: object | None, complements: Mapping[str, Any]) -> None:
        if usage not in USAGES:
            raise UsageInterdit(f"usage Mistral inconnu : {usage!r} (attendu : {USAGES})")
        if usage == USAGE_GENERATION and (jeton is None or jeton is not _jeton_generateur()):
            raise UsageInterdit(
                "usage « generation » réservé au Générateur (story 9.2) : appel refusé"
            )
        # Méta du journal (gabarit, amorce_ids) contrôlée avant toute réservation : un refus
        # du journal après l'appel laisserait un appel payé sans ligne.
        journal_mistral.controler_inscription(usage, jeton=jeton, **complements)
        refus = self.config.refus_modele(self.config.modele)
        if refus is not None:
            raise ModeleMistralRefuse(
                f"modèle demandé {self.config.modele!r} refusé ({refus}) : config/mistral.toml"
            )

    def _appeler(
        self,
        usage: str,
        session_id: str,
        messages: Sequence[Mapping[str, Any]],
        *,
        max_tokens: int,
        tokens_entree_estimes: int,
        temperature: float | None = None,
        response_format: Mapping[str, Any] | None = None,
        jeton: object | None = None,
        complements_journal: Mapping[str, Any] | None = None,
        tools: Sequence[Mapping[str, Any]] | None = None,
        tool_choice: str | None = None,
    ) -> ReponseMistral:
        """`appeler`, avec le jeton du Générateur et la méta de sa ligne de journal.

        `complements_journal` porte `gabarit_id`, `version_gabarit`, `sha256_gabarit` et
        `amorce_ids`, exigés pour `generation` et refusés ailleurs (`UsageInterdit`, avant
        toute réservation). `tools` (format OpenAI) et `tool_choice` sont envoyés quand ils
        sont fournis (traces RD du Générateur, AD-8) : le corps journalisé les porte.
        """
        complements = dict(complements_journal or {})
        inconnues = set(complements) - set(CLES_COMPLEMENTS)
        if inconnues:
            raise UsageInterdit(f"compléments de journal inconnus : {sorted(inconnues)}")
        self._controler(usage, jeton, complements)
        journal = journal_pour(usage, self.config, self.dossier_journaux)
        modele = self.config.modele
        parametres: dict[str, Any] = {
            "model": modele,
            "messages": [dict(m) for m in messages],
            "max_tokens": max_tokens,
        }
        if temperature is not None:
            parametres["temperature"] = temperature
        if response_format is not None:
            parametres["response_format"] = dict(response_format)
        if tools is not None:
            parametres["tools"] = [dict(outil) for outil in tools]
        if tool_choice is not None:
            parametres["tool_choice"] = tool_choice
        debut = self._horloge()
        attente_cumulee = 0.0
        reessai = 0
        while True:
            restant = self.config.duree_totale_max_appel - (self._horloge() - debut)
            try:
                # L'échéance globale ramène chaque tentative au temps qui reste à l'appel.
                with echeance_globale(restant):
                    return self._tentative(
                        usage,
                        session_id,
                        journal,
                        parametres,
                        tokens_entree_estimes=tokens_entree_estimes,
                        jeton=jeton,
                        complements=complements,
                    )
            except ErreurApiMistral as exc:
                attente = self._attente(exc, reessai + 1, attente_cumulee, debut)
                if attente is None:
                    if reessai:
                        exc.reessais = reessai
                        exc.args = (f"{exc.args[0]} après {reessai} réessai(s)",)
                    raise
                reessai += 1
                attente_cumulee += attente
                _JOURNAL.warning(
                    "relance API Mistral : horodatage=%s usage=%s code=%s réessai=%d/%d "
                    "attente=%.1fs source=%s",
                    datetime.now(UTC).isoformat(timespec="seconds"),
                    usage,
                    exc.statut_http if exc.statut_http is not None else "transport",
                    reessai,
                    self.config.reessais_max,
                    attente,
                    "retry-after" if exc.attente_serveur is not None else "exponentielle",
                )
                self._dormir(attente)

    def _attente(
        self, exc: ErreurApiMistral, reessai: int, attente_cumulee: float, debut: float
    ) -> float | None:
        """Attente avant le réessai n° `reessai`, ou `None` s'il ne doit pas avoir lieu.

        Un `Retry-After` nul, négatif ou daté du passé est porté à `attente_base` (jamais de
        relance sans pause). Le réessai n'a lieu que si l'attente cumulée reste dans
        `attente_totale_max` et si, après l'attente, une tentative complète (`delai_appel`)
        tient encore dans `duree_totale_max_appel`.
        """
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
        journal: Any,
        parametres: dict[str, Any],
        *,
        tokens_entree_estimes: int,
        jeton: object | None,
        complements: Mapping[str, Any],
    ) -> ReponseMistral:
        """Une tentative : réservation, appel, journal, règlement, modèle résolu."""
        modele = parametres["model"]
        max_tokens = parametres["max_tokens"]
        poste, sous_poste = self.registre.imputer(usage)
        reservation_id = self.registre.reserver(
            poste, sous_poste, modele, MODE, tokens_entree_estimes, max_tokens
        )

        def inscrire(**champs: Any) -> str:
            return journal.inscrire(
                session_id=session_id,
                usage=usage,
                modele_demande=modele,
                reservation_id=reservation_id,
                requete=self._requete_envoyee(parametres),
                jeton=jeton,
                **complements,
                **champs,
            )

        self._capture.reinitialiser()
        try:
            reponse = self.sdk.chat.complete(
                **parametres, retries=None, timeout_ms=_delai_ms(self.config)
            )
        except MistralError as exc:
            statut = exc.status_code
            # Une réponse d'erreur HTTP (refus 4xx, 429 comme échec serveur 5xx) n'est pas
            # facturée par Mistral : réglée à 0 (5xx : décision à confirmer par Anaël).
            facture = not 400 <= statut < 600
            try:
                inscrire(
                    modele_resolu=None,
                    reponse_brute=_corps_erreur(exc),
                    statut="erreur",
                    statut_http=statut,
                )
            finally:
                cout = self._regler_echec(reservation_id, facture)
            raise ErreurApiMistral(
                f"API Mistral : réponse HTTP {statut} ({usage})",
                statut,
                cout,
                transitoire=statut_transitoire(statut),
                attente_serveur=_retry_after(exc),
            ) from exc
        except BaseException as exc:
            # Toute issue laisse une ligne, interruption comprise (AD-3 verrou 3). Une réponse
            # 200 que le SDK n'a pas su lire garde son corps brut, capturé par le hook.
            brut = self._capture.reponse
            try:
                inscrire(
                    modele_resolu=None,
                    reponse_brute=brut,
                    statut="erreur",
                    statut_http=200 if brut is not None else None,
                )
            finally:
                # Une `SlmspError` (`HoteBloque` de la garde réseau…) part avant tout envoi :
                # rien n'est facturé. Toute autre exception est comptée au pire cas.
                cout = self._regler_echec(reservation_id, not isinstance(exc, SlmspError))
            if not isinstance(exc, Exception) or isinstance(exc, SlmspError):
                raise
            raise ErreurApiMistral(
                f"API Mistral : échec sans réponse HTTP ({type(exc).__name__}, {usage})",
                None,
                cout,
                transitoire=erreur_transport(exc),
            ) from exc

        try:
            texte, raison = _texte(reponse)
            usage_tokens = _usage(reponse)
            modele_resolu = str(getattr(reponse, "model", "") or "")
            refus = self.config.refus_modele(modele_resolu)
        except BaseException:
            # Réponse 200 illisible : appel facturé d'usage inconnu, journalisé et compté au
            # pire cas ; aucune réservation ne reste ouverte.
            try:
                inscrire(
                    modele_resolu=None,
                    reponse_brute=self._capture.reponse,
                    statut="erreur",
                    statut_http=200,
                )
            finally:
                self._regler_echec(reservation_id, True)
            raise
        try:
            appel_id = inscrire(
                modele_resolu=modele_resolu or None,
                reponse_brute=self._capture.reponse,
                statut="ok" if refus is None else "modele-refuse",
                statut_http=200,
            )
        finally:
            cout = self.registre.regulariser(reservation_id, usage_tokens)
        if refus is not None:
            raise ModeleMistralRefuse(
                f"modèle résolu {modele_resolu!r} refusé ({refus}) ; appel {appel_id} "
                "journalisé et régularisé"
            )
        return ReponseMistral(
            texte=texte,
            modele_resolu=modele_resolu,
            finish_reason=raison,
            usage=usage_tokens,
            cout_eur=cout,
            appel_id=appel_id,
            reservation_id=reservation_id,
        )

    def _requete_envoyee(self, parametres: Mapping[str, Any]) -> dict[str, Any]:
        """Corps JSON effectivement envoyé (capturé), sinon les paramètres de l'appel."""
        if self._capture.requete is not None:
            try:
                corps = json.loads(self._capture.requete)
            except ValueError:
                corps = None
            if isinstance(corps, dict):
                return corps
        return dict(parametres)

    def _regler_echec(self, reservation_id: int, facture: bool) -> float:
        if facture:
            return self.registre.compter_pire_cas(reservation_id)
        return self.registre.regulariser(reservation_id, UsageTokens(0, 0))
