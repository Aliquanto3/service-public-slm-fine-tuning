"""Client Mistral : point d'appel unique, sous budget, journalisé, sans relance (AD-3, D1.2).

`ClientMistral.appeler(usage, ...)` déroule, dans cet ordre :

1. les contrôles : usage connu (`generation` refusé, réservé au `Generateur` de
   `slmsp.mistral.generateur` par un jeton de preuve et la méta de gabarit et d'amorces
   passée par `complements_journal`), modèle demandé dans la liste stable ;
2. la réservation au pire cas (`RegistreBudget.reserver`) au sous-poste de l'usage ;
3. un appel unique `chat.complete` (`retries=None`, aucune relance) ;
4. le journal de l'usage (requête canonique, corps brut de la réponse, SHA, référence
   budget) ;
5. la régularisation au coût réel (`regulariser`), à 0 pour un refus 4xx non facturé ou une
   requête bloquée avant l'envoi (`SlmspError`, dont `HoteBloque`), ou au pire cas
   (`compter_pire_cas`) pour une erreur sans usage (5xx, réseau) ;
6. le contrôle du modèle résolu (champ `model` de la réponse) : `ModeleMistralRefuse` s'il
   sort de la liste stable ou porte un motif interdit, l'appel restant journalisé et payé.

Réservation et coût se font au tarif du modèle demandé, seul tarifé dans `tarifs.toml`.

Le SDK n'est construit que par `fabriquer_sdk` : clients HTTP synchrone et asynchrone du
profil `outillage` (`slmsp.net`), URL de l'API fixée, aucune relance, aucun journal de
débogage du SDK (il écrirait les en-têtes, donc la clé).
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
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


class ModeleMistralRefuse(SlmspError):
    """Modèle demandé ou résolu hors de la liste stable, ou portant un motif interdit."""


class ErreurApiMistral(SlmspError):
    """Échec d'un appel à l'API Mistral (refus HTTP, erreur serveur ou réseau).

    `statut_http` vaut `None` sans réponse HTTP ; `cout_eur` est le montant compté au
    registre pour cette tentative (0 pour un refus 4xx, le pire cas sinon).
    """

    def __init__(self, message: str, statut_http: int | None, cout_eur: float) -> None:
        super().__init__(message)
        self.statut_http = statut_http
        self.cout_eur = cout_eur


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

    La clé est lue dans le `.env` (`SLMSP_ENV_FILE`, ou `fichier_env`) et n'apparaît dans
    aucun message. Lève `SecretManquant` si elle est absente.
    """
    cle = secret(NOM_SECRET, fichier_env)
    return Mistral(
        api_key=cle.get_secret_value(),
        server_url=URL_API,
        client=client_reseau(
            "outillage", transport_interne=transport_interne, journal=journal_requetes
        ),
        async_client=client_reseau(
            "outillage",
            asynchrone=True,
            transport_interne=transport_interne,
            journal=journal_requetes,
        ),
        retry_config=None,
        timeout_ms=_delai_ms(config),
        debug_logger=NoOpLogger(),
    )


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
    ) -> None:
        self.config = config
        self.registre = registre
        self.sdk = sdk
        self.dossier_journaux = dossier_journaux
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
        `ErreurApiMistral` après un échec journalisé ; `ModeleMistralRefuse` après un appel
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
    ) -> ReponseMistral:
        """`appeler`, avec le jeton du Générateur et la méta de sa ligne de journal.

        `complements_journal` porte `gabarit_id`, `version_gabarit`, `sha256_gabarit` et
        `amorce_ids`, exigés pour `generation` et refusés ailleurs (`UsageInterdit`, avant
        toute réservation).
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
            facture = not 400 <= statut < 500  # un refus 4xx n'est pas facturé
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
                f"API Mistral : réponse HTTP {statut} ({usage})", statut, cout
            ) from exc
        except BaseException as exc:
            try:
                if isinstance(exc, Exception):
                    inscrire(
                        modele_resolu=None, reponse_brute=None, statut="erreur", statut_http=None
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
            ) from exc

        texte, raison = _texte(reponse)
        usage_tokens = _usage(reponse)
        modele_resolu = str(getattr(reponse, "model", "") or "")
        refus = self.config.refus_modele(modele_resolu)
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
