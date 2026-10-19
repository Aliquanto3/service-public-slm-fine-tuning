"""Juge principal Claude : appels directs et Batch API, sous budget et en cache (AD-3, AD-12).

`JugeClaude.juger(demandes)` déroule, dans cet ordre :

1. la construction des prompts et des clés de cache (`ItemNonJugeable` avant tout appel) ;
2. la reprise des lots laissés ouverts par un run précédent : un lot `reserve` (création
   non confirmée) est soldé au pire cas et abandonné, ses items rejugés ; un lot `en_cours`
   est relu (`GET`), puis collecté, ou annulé au-delà de `delai_max_lot` ;
3. la lecture du cache : un verdict connu n'est jamais redemandé ni réservé ;
4. en mode `batch`, les lots : lot local `slmsp-juge-<uuid4 hex>` persisté, réservation au
   pire cas au tarif batch (`reserver_lot`), création, `batch_id` Anthropic persisté avant
   toute attente, sondage, puis collecte (`collecter_lot`) ou annulation confirmée
   (`annuler_lot`) ;
5. les appels directs (mode `direct`, restes de lot, second essai d'une sortie non
   conforme), chacun par `RegistreBudget.executer_avec_relances` avec une seule tentative.

Deux sorties non conformes pour une même clé (JSON illisible, écart au schéma, `stop_reason`
`refusal` ou `max_tokens`) donnent un verdict `invalide`, mis en cache. Sur `BudgetEpuise`,
les items restants sont marqués `non-juge` (motif `budget`) sans exception. Un refus 4xx
(direct ou création de lot) n'est pas facturé : il est réglé à 0. 401 et 403 (motif
`erreur-api`) et 429 (motif `limite-debit`) arrêtent tous les appels restants du run, sans
relance. Chaque tentative payée est journalisée par item dans la table `appels` du cache
(tokens et coût en euros).

Requête au Juge : `model`, `max_tokens`, un seul message `user` et `output_config`
(`effort`, `format` JSON schema), sans `temperature`, `top_p`, `top_k`, `thinking`,
`fallbacks` ni `system` (D-nuit-A1-5). Le client `anthropic` n'est construit que par
`fabriquer_client` : client HTTP du profil `outillage`, `max_retries=0`.
"""

from __future__ import annotations

import logging
import re
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Literal

import anthropic

from slmsp.budget.registre import RegistreBudget
from slmsp.budget.tarifs import UsageTokens, cout_pire_cas, cout_reel
from slmsp.core.erreurs import BudgetEpuise, SlmspError
from slmsp.core.items import ItemBase
from slmsp.core.ports import JournalRequetes
from slmsp.core.schemas.verdict import Verdict
from slmsp.core.secrets import secret
from slmsp.judge.cache import CacheVerdicts, LotLocal, RequeteLot, cle_verdict
from slmsp.judge.config import ConfigJugePrincipal
from slmsp.judge.grille import Grille
from slmsp.judge.prompt import (
    PromptJuge,
    SortieNonConforme,
    construire_prompt,
    estimer_tokens_entree,
    valider_selon_schema,
)
from slmsp.net import client as client_reseau

URL_API: Final = "https://api.anthropic.com"
NOM_SECRET: Final = "ANTHROPIC_API_KEY"
PREFIXE_LOT: Final = "slmsp-juge-"
ECHECS_MAX: Final = 2
"""Sorties non conformes au-delà desquelles le verdict est `invalide`."""
ERREURS_SONDAGE_TOLEREES: Final = 3
"""Erreurs consécutives du relevé d'un lot tolérées ; la suivante laisse le lot ouvert."""
STATUTS_ARRET: Final = frozenset({401, 403})
"""Refus d'authentification : plus aucun appel dans ce run."""
STATUT_LIMITE_DEBIT: Final = 429
"""Limite de débit : plus aucun appel dans ce run (aucune relance)."""

MOTIF_BUDGET: Final = "budget"
MOTIF_ERREUR_API: Final = "erreur-api"
MOTIF_ERREUR_CREATION_LOT: Final = "erreur-creation-lot"
LONGUEUR_MESSAGE_ERREUR: Final = 500
LOGGER: Final = logging.getLogger(__name__)
MOTIF_LIMITE_DEBIT: Final = "limite-debit"
MOTIF_LOT_NON_ANNULE: Final = "lot-non-annule"

ISSUE_JUGE: Final = "juge"
ISSUE_NON_CONFORME: Final = "non-conforme"
ISSUE_INVALIDE: Final = "invalide"
ISSUE_ERREUR_API: Final = "erreur-api"
ISSUE_ERREUR_CREATION_LOT: Final = "erreur-creation-lot"

StatutJugement = Literal["juge", "invalide", "non-juge"]


def motif_arret(statut: int | None) -> str | None:
    """Motif d'arrêt du run pour un refus HTTP `statut`, ou `None` s'il n'arrête rien."""
    if statut in STATUTS_ARRET:
        return MOTIF_ERREUR_API
    if statut == STATUT_LIMITE_DEBIT:
        return MOTIF_LIMITE_DEBIT
    return None


_MOTIF_CLE_API: Final = re.compile(r"sk-ant-[A-Za-z0-9_-]+")


def detail_erreur_creation(exc: BaseException, statut: int | None) -> str:
    """Type, statut HTTP et message (cause comprise) d'une erreur, sans en-têtes ni clé.

    Toute clé `sk-ant-…` est masquée ; le détail final est tronqué à 500 caractères.
    """
    message = str(getattr(exc, "message", None) or exc)
    detail = f"{type(exc).__name__} statut={statut} {message}"
    if exc.__cause__ is not None:  # le SDK enveloppe les erreurs réseau
        detail += f" cause={type(exc.__cause__).__name__} {exc.__cause__}"
    return _MOTIF_CLE_API.sub("sk-ant-***", detail)[:LONGUEUR_MESSAGE_ERREUR]


def fabriquer_client(
    config: ConfigJugePrincipal,
    transport_interne: Any = None,
    journal: JournalRequetes | None = None,
    fichier_env: str | Path | None = None,
) -> anthropic.Anthropic:
    """Client `anthropic` sur le client HTTP gardé du profil `outillage`, sans relance.

    La clé est lue dans le `.env` (`SLMSP_ENV_FILE`, ou `fichier_env`) et n'apparaît dans
    aucun message. Lève `SecretManquant` si elle est absente.
    """
    cle = secret(NOM_SECRET, fichier_env)
    return anthropic.Anthropic(
        api_key=cle.get_secret_value(),
        base_url=URL_API,
        http_client=client_reseau(
            "outillage", transport_interne=transport_interne, journal=journal
        ),
        max_retries=0,
        timeout=config.delai_appel,
    )


@dataclass(frozen=True)
class DemandeJugement:
    """Item à juger et sortie canonique de l'Assistant (`texte`, `appels_outils`, `sources`).

    Ni le modèle évalué ni la méthode ne figurent dans une demande (Juge aveugle).
    """

    item: ItemBase
    sortie: Mapping[str, Any]


@dataclass(frozen=True)
class ResultatJugement:
    """Résultat d'une demande : verdict, coût de cet appel à `juger` et mode de l'appel."""

    item_id: str
    cle: str
    statut: StatutJugement
    verdict: Verdict | None
    depuis_cache: bool
    cout_eur: float
    tokens: UsageTokens | None
    mode: str | None
    motif: str | None = None


@dataclass(frozen=True)
class RapportJugement:
    """Résultats dans l'ordre des demandes, arrêt sur budget et coût total de l'appel."""

    resultats: tuple[ResultatJugement, ...]
    budget_epuise: bool
    cout_total_eur: float


@dataclass(frozen=True)
class _Preparee:
    item: ItemBase
    prompt: PromptJuge
    cle: str
    tokens_estimes: int


@dataclass
class _Issue:
    statut: StatutJugement
    verdict: Verdict | None = None
    depuis_cache: bool = False
    mode: str | None = None
    motif: str | None = None


@dataclass
class _Etat:
    """État d'un appel à `juger`."""

    uniques: dict[str, _Preparee]
    issues: dict[str, _Issue] = field(default_factory=dict)
    couts: dict[str, float] = field(default_factory=dict)
    usages: dict[str, UsageTokens] = field(default_factory=dict)
    directs: list[str] = field(default_factory=list)
    budget_epuise: bool = False
    arret: str | None = None
    """Motif d'arrêt du run (401, 403, 429) : plus aucun appel."""
    cout_hors_items: float = 0.0

    def demandee(self, cle: str) -> bool:
        return cle in self.uniques and cle not in self.issues

    def vers_direct(self, cle: str) -> None:
        if self.demandee(cle) and cle not in self.directs:
            self.directs.append(cle)

    def imputer(self, cle: str, cout: float, usage: UsageTokens | None) -> None:
        if cle not in self.uniques:  # lot repris : payé dans cet appel, hors demandes
            self.cout_hors_items += cout
            return
        self.couts[cle] = self.couts.get(cle, 0.0) + cout
        if usage is not None:
            precedent = self.usages.get(cle)
            self.usages[cle] = usage if precedent is None else precedent + usage

    def resoudre(self, cle: str, issue: _Issue) -> None:
        if self.demandee(cle):
            self.issues[cle] = issue


@dataclass(frozen=True)
class _Refus:
    """Refus 4xx de l'API : non facturé par Anthropic, réservation régularisée à 0."""

    statut: int


@dataclass(frozen=True)
class _Suivi:
    termine: bool
    annule: bool = False
    motif: str | None = None


def _usage(message: Any) -> UsageTokens:
    usage = message.usage
    return UsageTokens(
        int(getattr(usage, "input_tokens", 0) or 0),
        int(getattr(usage, "output_tokens", 0) or 0),
        int(getattr(usage, "cache_creation_input_tokens", 0) or 0),
        int(getattr(usage, "cache_read_input_tokens", 0) or 0),
    )


def _verdict_du_message(message: Any, item_id: str, schema: Mapping[str, Any]) -> Verdict:
    """Verdict validé d'un message ; `SortieNonConforme` si refus, troncature ou écart."""
    raison = getattr(message, "stop_reason", None)
    if raison in ("refusal", "max_tokens"):
        raise SortieNonConforme(f"{item_id} : sortie interrompue (stop_reason {raison})")
    texte = "".join(
        getattr(bloc, "text", "")
        for bloc in getattr(message, "content", None) or []
        if getattr(bloc, "type", None) == "text"
    )
    return valider_selon_schema(item_id, texte, schema)


class JugeClaude:
    """Juge principal : `juger(demandes)` rend un verdict par demande, sous budget."""

    def __init__(
        self,
        config: ConfigJugePrincipal,
        registre: RegistreBudget,
        cache: CacheVerdicts,
        client: Any,
        grille: Grille,
        *,
        attendre: Callable[[float], None] = time.sleep,
        horloge: Callable[[], float] = time.monotonic,
        maintenant: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.config = config
        self.registre = registre
        self.cache = cache
        self.client = client
        self.grille = grille
        self.attendre = attendre
        self.horloge = horloge
        self.maintenant = maintenant
        self.poste, self.sous_poste = registre.imputer(config.usage_budget)

    # --- point d'entrée -------------------------------------------------------------------

    def juger(self, demandes: Sequence[DemandeJugement]) -> RapportJugement:
        """Juge chaque demande (cache, lots, appels directs) ; résultats dans l'ordre.

        Lève `ItemNonJugeable` avant tout appel si une demande porte sur un item non
        jugeable. `BudgetEpuise` n'est jamais remontée : `budget_epuise` est alors vrai.
        """
        preparees = [self._preparer(demande) for demande in demandes]
        uniques: dict[str, _Preparee] = {}
        for preparee in preparees:
            uniques.setdefault(preparee.cle, preparee)  # doublons : une seule requête
        etat = _Etat(uniques=uniques)

        self._reprendre_lots(etat)
        a_juger = self._lire_cache(etat)
        if self.config.mode_appel == "batch":
            self._juger_par_lots(a_juger, etat)
        else:
            for cle in a_juger:
                etat.vers_direct(cle)
        self._juger_en_direct(etat)
        return self._rapport(preparees, etat)

    def _preparer(self, demande: DemandeJugement) -> _Preparee:
        prompt = construire_prompt(demande.item, demande.sortie, self.grille)
        cle = cle_verdict(
            demande.item, demande.sortie, prompt, self.config.modele, self.config.effort
        )
        return _Preparee(demande.item, prompt, cle, estimer_tokens_entree(prompt))

    def _lire_cache(self, etat: _Etat) -> list[str]:
        a_juger = []
        for cle in etat.uniques:
            if cle in etat.issues or cle in etat.directs:
                continue
            en_cache = self.cache.lire(cle)
            if en_cache is not None:
                etat.resoudre(
                    cle,
                    _Issue(
                        "invalide" if en_cache.verdict.invalide else "juge",
                        en_cache.verdict,
                        depuis_cache=True,
                        mode=en_cache.mode,
                    ),
                )
            else:
                a_juger.append(cle)
        return a_juger

    def _rapport(self, preparees: list[_Preparee], etat: _Etat) -> RapportJugement:
        resultats = []
        vues: set[str] = set()
        for p in preparees:
            issue = etat.issues.get(p.cle) or _Issue("non-juge", motif="non-traite")
            sans_cout = issue.depuis_cache or p.cle in vues  # doublon : coût porté une fois
            vues.add(p.cle)
            resultats.append(
                ResultatJugement(
                    item_id=p.item.id,
                    cle=p.cle,
                    statut=issue.statut,
                    verdict=issue.verdict,
                    depuis_cache=issue.depuis_cache,
                    cout_eur=0.0 if sans_cout else etat.couts.get(p.cle, 0.0),
                    tokens=None if sans_cout else etat.usages.get(p.cle),
                    mode=issue.mode,
                    motif=issue.motif,
                )
            )
        total = sum(etat.couts.values()) + etat.cout_hors_items
        return RapportJugement(tuple(resultats), etat.budget_epuise, total)

    # --- requêtes -------------------------------------------------------------------------

    def _parametres(self, prompt: PromptJuge) -> dict[str, Any]:
        """Corps d'une requête au Juge (identique en direct et en batch)."""
        return {
            "model": self.config.modele,
            "max_tokens": self.config.max_tokens,
            "messages": [{"role": "user", "content": prompt.texte}],
            "output_config": {
                "effort": self.config.effort,
                "format": {"type": "json_schema", "schema": prompt.schema},
            },
        }

    def _lot_ouvert_au_registre(self, lot_id: str) -> bool:
        return any(lot.batch_id == lot_id for lot in self.registre.lots_ouverts())

    # --- reprise --------------------------------------------------------------------------

    def _reprendre_lots(self, etat: _Etat) -> None:
        for lot in self.cache.lots_ouverts():
            requetes = self.cache.requetes_lot(lot.lot_id, lot.nb_retenu)
            if lot.statut == "reserve" or lot.batch_id is None:
                # Création non confirmée : le lot reste compté au pire cas, ses items
                # sont rejugés (ils ne sont pas en cache).
                if self._lot_ouvert_au_registre(lot.lot_id):
                    etat.cout_hors_items += self.registre.annuler_lot(lot.lot_id)
                self.cache.changer_statut(lot.lot_id, "abandonne")
                continue
            self._achever_lot(lot, requetes, etat)

    # --- lots -----------------------------------------------------------------------------

    def _juger_par_lots(self, a_juger: list[str], etat: _Etat) -> None:
        restantes = list(a_juger)
        while restantes:
            if etat.budget_epuise or etat.arret is not None:
                break
            lot_id = f"{PREFIXE_LOT}{uuid.uuid4().hex}"
            requetes = [
                RequeteLot(
                    custom_id=f"r{rang:05d}",
                    cle=cle,
                    item_id=etat.uniques[cle].item.id,
                    schema=etat.uniques[cle].prompt.schema,
                )
                for rang, cle in enumerate(restantes)
            ]
            self.cache.creer_lot(lot_id, self.config.modele, self.config.effort, requetes)
            estimes = max(etat.uniques[cle].tokens_estimes for cle in restantes)
            try:
                retenu = self.registre.reserver_lot(
                    lot_id,
                    self.poste,
                    self.sous_poste,
                    self.config.modele,
                    estimes,
                    self.config.max_tokens,
                    len(requetes),
                )
            except BudgetEpuise:
                self.cache.changer_statut(lot_id, "abandonne")
                etat.budget_epuise = True
                break
            except BaseException:
                self.cache.changer_statut(lot_id, "abandonne")
                raise
            self.cache.fixer_retenu(lot_id, retenu)
            soumises, restantes = requetes[:retenu], restantes[retenu:]
            try:
                cree = self.client.messages.batches.create(
                    requests=[
                        {
                            "custom_id": r.custom_id,
                            "params": self._parametres(etat.uniques[r.cle].prompt),
                        }
                        for r in soumises
                    ]
                )
            except Exception as exc:
                # Refus 4xx : rien n'est créé ni facturé, réglé à 0 ; 401, 403 et 429 arrêtent
                # le run. Toute autre erreur : création non confirmée, pire cas.
                statut = exc.status_code if isinstance(exc, anthropic.APIStatusError) else None
                refus = statut is not None and 400 <= statut < 500
                usage = UsageTokens(0, 0) if refus else None
                etat.cout_hors_items += self.registre.annuler_lot(lot_id, usage)
                self.cache.changer_statut(lot_id, "abandonne")
                arret = motif_arret(statut) if refus else None
                etat.arret = etat.arret or arret
                detail = detail_erreur_creation(exc, statut)
                LOGGER.warning("création du lot %s en erreur : %s", lot_id, detail)
                self._tracer_erreur_creation(lot_id, detail, soumises)
                for r in soumises:
                    etat.resoudre(
                        r.cle,
                        _Issue("non-juge", mode="batch", motif=arret or MOTIF_ERREUR_CREATION_LOT),
                    )
                continue
            self.cache.marquer_soumis(lot_id, cree.id, self.maintenant())
            lot = self.cache.lot(lot_id)
            assert lot is not None
            self._achever_lot(lot, soumises, etat)
        for cle in restantes:
            etat.resoudre(cle, _Issue("non-juge", motif=etat.arret or MOTIF_BUDGET))

    def _tracer_erreur_creation(self, lot_id: str, detail: str, soumises: list[RequeteLot]) -> None:
        """Trace persistante d'un échec de création, qui ne fait jamais échouer la notation.

        Le détail va une fois dans `lots.motif` ; chaque requête du lot reçoit une ligne `appels`
        d'issue `erreur-creation-lot` (valeur fermée). Coût 0 sur ces lignes : le coût du lot
        (pire cas ou 0) reste imputé au registre de budget, et `cumul_appels` ne le compte pas
        deux fois.
        """
        try:
            self.cache.consigner_motif_lot(lot_id, detail)
            for r in soumises:
                self.cache.journaliser_appel(
                    cle=r.cle,
                    item_id=r.item_id,
                    mode="batch",
                    lot_id=lot_id,
                    usage=None,
                    cout_eur=0.0,
                    issue=ISSUE_ERREUR_CREATION_LOT,
                )
        except Exception:
            LOGGER.exception("trace de l'erreur de création du lot %s impossible", lot_id)

    def _ecoule(self, lot: LotLocal, debut: float) -> float:
        """Secondes écoulées depuis `soumis_le` (horloge murale), sinon depuis `debut`."""
        if lot.soumis_le:
            soumis = datetime.fromisoformat(lot.soumis_le)
            if soumis.tzinfo is not None:
                return (self.maintenant() - soumis).total_seconds()
        return self.horloge() - debut

    def _suivre(self, lot_local: LotLocal) -> _Suivi:
        """Sonde le lot jusqu'à `ended`, et l'annule au-delà de `delai_max_lot`.

        Le délai court depuis la soumission persistée (`soumis_le`), y compris pour un lot
        repris après un arrêt. Un lot déjà en annulation (`canceling` ou
        `cancel_initiated_at`) attend la confirmation sans nouvelle demande d'annulation.
        `ERREURS_SONDAGE_TOLEREES` erreurs consécutives du relevé sont tolérées.
        """
        assert lot_local.batch_id is not None
        batch_id = lot_local.batch_id
        lots = self.client.messages.batches
        debut = self.horloge()
        debut_annulation: float | None = None
        erreurs = 0
        while True:
            try:
                lot = lots.retrieve(batch_id)
            except Exception:
                erreurs += 1
                if erreurs > ERREURS_SONDAGE_TOLEREES:
                    return _Suivi(False, motif=MOTIF_ERREUR_API)
                self.attendre(self.config.intervalle_sondage)
                continue
            erreurs = 0
            if lot.processing_status == "ended":
                # Une annulation demandée par un run précédent compte aussi (lot repris).
                annule = debut_annulation is not None or lot.cancel_initiated_at is not None
                return _Suivi(True, annule=annule)
            if debut_annulation is None:
                if lot.processing_status == "canceling" or lot.cancel_initiated_at is not None:
                    debut_annulation = self.horloge()  # annulation déjà demandée
                elif self._ecoule(lot_local, debut) >= self.config.delai_max_lot:
                    try:
                        lot = lots.cancel(batch_id)
                    except Exception:
                        return _Suivi(False, motif=MOTIF_LOT_NON_ANNULE)
                    debut_annulation = self.horloge()
                    if lot.processing_status == "ended":
                        return _Suivi(True, annule=True)
            elif self.horloge() - debut_annulation >= self.config.delai_annulation:
                return _Suivi(False, motif=MOTIF_LOT_NON_ANNULE)
            self.attendre(self.config.intervalle_sondage)

    def _achever_lot(self, lot: LotLocal, requetes: list[RequeteLot], etat: _Etat) -> None:
        """Suit un lot `en_cours` jusqu'à sa collecte ou son annulation confirmée."""
        assert lot.batch_id is not None
        suivi = self._suivre(lot)
        resultats: dict[str, Any] = {}
        if suivi.termine:
            try:
                for reponse in self.client.messages.batches.results(lot.batch_id):
                    resultats[reponse.custom_id] = reponse
            except Exception:
                suivi = _Suivi(False, motif=MOTIF_ERREUR_API)
        if not suivi.termine:
            # Lot laissé ouvert (statut `en_cours`) : relu au prochain appel.
            for r in requetes:
                etat.resoudre(r.cle, _Issue("non-juge", mode="batch", motif=suivi.motif))
            return
        usage_lot = UsageTokens(0, 0)
        for requete in requetes:
            reponse = resultats.get(requete.custom_id)
            if reponse is None or reponse.result.type != "succeeded":
                etat.vers_direct(requete.cle)  # errored, expired, canceled : non facturé
                continue
            message = reponse.result.message
            usage = _usage(message)
            usage_lot = usage_lot + usage
            self._traiter_message(requete, message, usage, lot, etat)
        if self._lot_ouvert_au_registre(lot.lot_id):
            if suivi.annule:
                self.registre.annuler_lot(lot.lot_id, usage_lot)
            else:
                self.registre.collecter_lot(lot.lot_id, usage_lot)
        self.cache.changer_statut(lot.lot_id, "annule" if suivi.annule else "collecte")

    def _traiter_message(
        self,
        requete: RequeteLot,
        message: Any,
        usage: UsageTokens,
        lot: LotLocal,
        etat: _Etat,
    ) -> None:
        en_cache = self.cache.lire(requete.cle)
        if en_cache is None and self.cache.appel_journalise(lot.lot_id, requete.cle):
            # Lot repris après un arrêt pendant la collecte : sortie non conforme déjà
            # comptée ; orientée comme au premier passage (second essai direct).
            etat.vers_direct(requete.cle)
            return
        if en_cache is not None:  # lot repris après une écriture déjà faite
            etat.resoudre(
                requete.cle,
                _Issue(
                    "invalide" if en_cache.verdict.invalide else "juge",
                    en_cache.verdict,
                    mode=en_cache.mode,
                ),
            )
            return
        cout = cout_reel(self.registre.tarifs, lot.modele, "batch", usage)
        etat.imputer(requete.cle, cout, usage)
        try:
            verdict = _verdict_du_message(message, requete.item_id, requete.schema)
        except SortieNonConforme as exc:
            self._echec(requete.cle, requete.item_id, str(exc), "batch", lot, usage, cout, etat)
            return
        self.cache.journaliser_appel(
            cle=requete.cle,
            item_id=requete.item_id,
            mode="batch",
            lot_id=lot.lot_id,
            usage=usage,
            cout_eur=cout,
            issue=ISSUE_JUGE,
        )
        self._mettre_en_cache(requete.cle, verdict, "batch", lot.modele, lot.effort)
        etat.resoudre(requete.cle, _Issue("juge", verdict, mode="batch"))

    def _echec(
        self,
        cle: str,
        item_id: str,
        motif: str,
        mode: str,
        lot: LotLocal | None,
        usage: UsageTokens,
        cout: float,
        etat: _Etat,
    ) -> bool:
        """Compte une sortie non conforme ; vrai si le verdict devient `invalide`."""
        nombre = self.cache.compter_echec(cle, item_id, motif)
        invalide = nombre >= ECHECS_MAX
        self.cache.journaliser_appel(
            cle=cle,
            item_id=item_id,
            mode=mode,
            lot_id=lot.lot_id if lot is not None else None,
            usage=usage,
            cout_eur=cout,
            issue=ISSUE_INVALIDE if invalide else ISSUE_NON_CONFORME,
        )
        if invalide:
            verdict = Verdict.invalide_pour(item_id)
            modele = lot.modele if lot is not None else self.config.modele
            effort = lot.effort if lot is not None else self.config.effort
            self._mettre_en_cache(cle, verdict, mode, modele, effort)
            etat.resoudre(cle, _Issue("invalide", verdict, mode=mode))
        else:
            etat.vers_direct(cle)
        return invalide

    def _mettre_en_cache(
        self, cle: str, verdict: Verdict, mode: str, modele: str, effort: str
    ) -> None:
        """Inscrit le verdict avec le coût et les tokens cumulés de toutes ses tentatives
        journalisées dans `appels`, runs précédents compris."""
        cout, usage = self.cache.cumul_appels(cle)
        self.cache.ecrire(
            cle, verdict, modele=modele, effort=effort, mode=mode, cout_eur=cout, usage=usage
        )

    # --- appels directs -------------------------------------------------------------------

    def _juger_en_direct(self, etat: _Etat) -> None:
        indice = 0
        while indice < len(etat.directs):  # `directs` peut s'allonger (second essai)
            cle = etat.directs[indice]
            indice += 1
            if not etat.demandee(cle):
                continue
            if etat.arret is not None:  # 401, 403 ou 429 : plus aucun appel
                etat.resoudre(cle, _Issue("non-juge", motif=etat.arret))
                continue
            if etat.budget_epuise:
                etat.resoudre(cle, _Issue("non-juge", motif=MOTIF_BUDGET))
                continue
            self._juger_un_direct(etat.uniques[cle], etat)

    def _juger_un_direct(self, preparee: _Preparee, etat: _Etat) -> None:
        params = self._parametres(preparee.prompt)
        item_id = preparee.item.id

        def appel() -> tuple[Any, UsageTokens]:
            try:
                message = self.client.messages.create(**params)
            except anthropic.APIStatusError as exc:
                if 400 <= exc.status_code < 500:  # refus non facturé : réglé à 0
                    return _Refus(exc.status_code), UsageTokens(0, 0)
                raise
            return message, _usage(message)

        while etat.demandee(preparee.cle):
            try:
                message = self.registre.executer_avec_relances(
                    appel,
                    1,
                    self.poste,
                    self.sous_poste,
                    self.config.modele,
                    "direct",
                    preparee.tokens_estimes,
                    self.config.max_tokens,
                )
            except BudgetEpuise:
                etat.budget_epuise = True
                etat.resoudre(preparee.cle, _Issue("non-juge", motif=MOTIF_BUDGET))
                return
            except SlmspError:
                raise  # configuration ou tarif : aucune requête n'est partie
            except Exception:
                # Tentative comptée au pire cas par le registre ; on passe à l'item suivant.
                pire = cout_pire_cas(
                    self.registre.tarifs,
                    self.config.modele,
                    "direct",
                    preparee.tokens_estimes,
                    self.config.max_tokens,
                    self.registre.config.majoration_entree,
                )
                etat.imputer(preparee.cle, pire, None)
                self.cache.journaliser_appel(
                    cle=preparee.cle,
                    item_id=item_id,
                    mode="direct",
                    lot_id=None,
                    usage=None,
                    cout_eur=pire,
                    issue=ISSUE_ERREUR_API,
                )
                etat.resoudre(
                    preparee.cle, _Issue("non-juge", mode="direct", motif=MOTIF_ERREUR_API)
                )
                return
            if isinstance(message, _Refus):
                self.cache.journaliser_appel(
                    cle=preparee.cle,
                    item_id=item_id,
                    mode="direct",
                    lot_id=None,
                    usage=UsageTokens(0, 0),
                    cout_eur=0.0,
                    issue=ISSUE_ERREUR_API,
                )
                etat.imputer(preparee.cle, 0.0, None)
                arret = motif_arret(message.statut)
                etat.arret = etat.arret or arret
                etat.resoudre(
                    preparee.cle,
                    _Issue("non-juge", mode="direct", motif=arret or MOTIF_ERREUR_API),
                )
                return
            usage = _usage(message)
            cout = cout_reel(self.registre.tarifs, self.config.modele, "direct", usage)
            etat.imputer(preparee.cle, cout, usage)
            try:
                verdict = _verdict_du_message(message, item_id, preparee.prompt.schema)
            except SortieNonConforme as exc:
                if self._echec(preparee.cle, item_id, str(exc), "direct", None, usage, cout, etat):
                    return
                continue  # second essai direct
            self.cache.journaliser_appel(
                cle=preparee.cle,
                item_id=item_id,
                mode="direct",
                lot_id=None,
                usage=usage,
                cout_eur=cout,
                issue=ISSUE_JUGE,
            )
            self._mettre_en_cache(
                preparee.cle, verdict, "direct", self.config.modele, self.config.effort
            )
            etat.resoudre(preparee.cle, _Issue("juge", verdict, mode="direct"))
