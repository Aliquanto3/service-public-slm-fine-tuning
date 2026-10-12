"""Second juge Mistral : renote l'échantillon du manifeste, sous budget et en cache (D1.1).

`JugeMistral.juger(demandes, echantillon)` ne garde que les demandes dont l'item figure dans
`echantillon` (`Echantillons.second_juge` du manifeste), dans l'ordre des demandes, puis :

1. construit le prompt du Juge principal (`construire_prompt`, même cécité que la story 5.4)
   et la clé du cache (`cle_verdict`, effort `<effort_cache>+<format_reponse>`) ;
   `ItemNonJugeable` avant tout appel ;
2. lit le cache de verdicts commun : un verdict connu n'est jamais redemandé ni réservé ;
3. appelle Mistral item par item par `ClientMistral.appeler` (usage `juge-second`, imputé à
   `mistral.juge`, journal du juge), avec `temperature` et un `response_format` JSON au
   schéma du Juge principal ; un `session_id` `juge-second-<uuid4 hex>` par appel à `juger`.

Deux sorties non conformes pour une même clé (JSON illisible, écart au schéma,
`finish_reason` d'interruption) donnent un verdict `invalide`, mis en cache. Sur
`BudgetEpuise`, les items restants sont `non-juge` (motif `budget`, « non rejugés ») sans
exception. Un refus 4xx est réglé à 0 et l'item passe `non-juge` ; 401 et 403 arrêtent
tous les appels restants. `ModeleMistralRefuse` remonte à l'appelant : c'est une
configuration à corriger, pas un aléa. Les scores et le kappa relèvent de la story 5.6.
"""

from __future__ import annotations

import uuid
from collections.abc import Collection, Sequence
from dataclasses import dataclass, field
from typing import Any, Final

from slmsp.budget.tarifs import UsageTokens
from slmsp.core.erreurs import BudgetEpuise, ConfigurationInvalide
from slmsp.core.items import ItemBase
from slmsp.core.schemas.verdict import Verdict
from slmsp.judge.cache import CacheVerdicts, cle_verdict
from slmsp.judge.claude import (
    ECHECS_MAX,
    ISSUE_ERREUR_API,
    ISSUE_INVALIDE,
    ISSUE_JUGE,
    ISSUE_NON_CONFORME,
    MOTIF_BUDGET,
    MOTIF_ERREUR_API,
    STATUTS_ARRET,
    DemandeJugement,
    RapportJugement,
    ResultatJugement,
    StatutJugement,
)
from slmsp.judge.config import ConfigSecondJuge
from slmsp.judge.grille import Grille
from slmsp.judge.prompt import (
    PromptJuge,
    SortieNonConforme,
    construire_prompt,
    estimer_tokens_entree,
    valider_selon_schema,
)
from slmsp.mistral.client import ClientMistral, ErreurApiMistral

MODE: Final = "direct"
PREFIXE_SESSION: Final = "juge-second-"
NOM_SCHEMA: Final = "verdict"
FINS_INTERROMPUES: Final = frozenset({"length", "model_length", "error"})
"""`finish_reason` d'une sortie interrompue, comptée comme non conforme."""


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

    issues: dict[str, _Issue] = field(default_factory=dict)
    couts: dict[str, float] = field(default_factory=dict)
    usages: dict[str, UsageTokens] = field(default_factory=dict)
    budget_epuise: bool = False
    arret_api: bool = False

    def imputer(self, cle: str, cout: float, usage: UsageTokens | None) -> None:
        self.couts[cle] = self.couts.get(cle, 0.0) + cout
        if usage is not None:
            precedent = self.usages.get(cle)
            self.usages[cle] = usage if precedent is None else precedent + usage


class JugeMistral:
    """Second juge : `juger(demandes, echantillon)` rend un verdict par item échantillonné."""

    def __init__(
        self,
        config: ConfigSecondJuge,
        client: ClientMistral,
        cache: CacheVerdicts,
        grille: Grille,
    ) -> None:
        if config.modele != client.config.modele:
            raise ConfigurationInvalide(
                f"second juge : modèle {config.modele!r} (juges.toml) différent du modèle "
                f"{client.config.modele!r} demandé par le client (mistral.toml)"
            )
        self.config = config
        self.client = client
        self.cache = cache
        self.grille = grille

    # --- point d'entrée -------------------------------------------------------------------

    def juger(
        self, demandes: Sequence[DemandeJugement], echantillon: Collection[str]
    ) -> RapportJugement:
        """Juge les demandes de l'échantillon (cache, puis appels directs) ; dans l'ordre.

        Les demandes hors échantillon sont ignorées (absentes du rapport). Lève
        `ItemNonJugeable` avant tout appel ; `BudgetEpuise` n'est jamais remontée
        (`budget_epuise` est alors vrai) ; `ModeleMistralRefuse` remonte.
        """
        retenus = set(echantillon)
        preparees = [self._preparer(d) for d in demandes if d.item.id in retenus]
        uniques: dict[str, _Preparee] = {}
        for preparee in preparees:
            uniques.setdefault(preparee.cle, preparee)  # doublons : une seule requête
        etat = _Etat()
        session_id = f"{PREFIXE_SESSION}{uuid.uuid4().hex}"
        for cle, preparee in uniques.items():
            en_cache = self.cache.lire(cle)
            if en_cache is not None:
                etat.issues[cle] = _Issue(
                    "invalide" if en_cache.verdict.invalide else "juge",
                    en_cache.verdict,
                    depuis_cache=True,
                    mode=en_cache.mode,
                )
                continue
            if etat.arret_api:  # clé refusée (401, 403) : plus aucun appel
                etat.issues[cle] = _Issue("non-juge", motif=MOTIF_ERREUR_API)
            elif etat.budget_epuise:
                etat.issues[cle] = _Issue("non-juge", motif=MOTIF_BUDGET)
            else:
                self._juger_un(preparee, session_id, etat)
        return self._rapport(preparees, etat)

    def _preparer(self, demande: DemandeJugement) -> _Preparee:
        prompt = construire_prompt(demande.item, demande.sortie, self.grille)
        cle = cle_verdict(
            demande.item, demande.sortie, prompt, self.config.modele, self.config.effort_cle
        )
        return _Preparee(demande.item, prompt, cle, estimer_tokens_entree(prompt))

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
        return RapportJugement(tuple(resultats), etat.budget_epuise, sum(etat.couts.values()))

    # --- appels ---------------------------------------------------------------------------

    def _format_reponse(self, prompt: PromptJuge) -> dict[str, Any]:
        if self.config.format_reponse == "json_object":
            return {"type": "json_object"}
        return {
            "type": "json_schema",
            "json_schema": {"name": NOM_SCHEMA, "schema": prompt.schema, "strict": True},
        }

    def _juger_un(self, preparee: _Preparee, session_id: str, etat: _Etat) -> None:
        item_id = preparee.item.id
        cle = preparee.cle
        while True:  # au plus ECHECS_MAX tentatives (compteur d'échecs persisté)
            try:
                reponse = self.client.appeler(
                    self.config.usage_budget,
                    session_id,
                    [{"role": "user", "content": preparee.prompt.texte}],
                    max_tokens=self.config.max_tokens,
                    tokens_entree_estimes=preparee.tokens_estimes,
                    temperature=self.config.temperature,
                    response_format=self._format_reponse(preparee.prompt),
                )
            except BudgetEpuise:
                etat.budget_epuise = True
                etat.issues[cle] = _Issue("non-juge", motif=MOTIF_BUDGET)
                return
            except ErreurApiMistral as exc:
                # 4xx : réglé à 0 (non facturé) ; 5xx ou réseau : compté au pire cas.
                refus = exc.statut_http is not None and 400 <= exc.statut_http < 500
                etat.imputer(cle, exc.cout_eur, None)
                self.cache.journaliser_appel(
                    cle=cle,
                    item_id=item_id,
                    mode=MODE,
                    lot_id=None,
                    usage=UsageTokens(0, 0) if refus else None,
                    cout_eur=exc.cout_eur,
                    issue=ISSUE_ERREUR_API,
                )
                etat.arret_api = etat.arret_api or exc.statut_http in STATUTS_ARRET
                etat.issues[cle] = _Issue("non-juge", mode=MODE, motif=MOTIF_ERREUR_API)
                return
            etat.imputer(cle, reponse.cout_eur, reponse.usage)
            try:
                if reponse.finish_reason in FINS_INTERROMPUES:
                    raise SortieNonConforme(
                        f"{item_id} : sortie interrompue (finish_reason {reponse.finish_reason})"
                    )
                verdict = valider_selon_schema(item_id, reponse.texte, preparee.prompt.schema)
            except SortieNonConforme as exc:
                nombre = self.cache.compter_echec(cle, item_id, str(exc))
                invalide = nombre >= ECHECS_MAX
                self.cache.journaliser_appel(
                    cle=cle,
                    item_id=item_id,
                    mode=MODE,
                    lot_id=None,
                    usage=reponse.usage,
                    cout_eur=reponse.cout_eur,
                    issue=ISSUE_INVALIDE if invalide else ISSUE_NON_CONFORME,
                )
                if not invalide:
                    continue  # second essai
                verdict = Verdict.invalide_pour(item_id)
                self._mettre_en_cache(cle, verdict)
                etat.issues[cle] = _Issue("invalide", verdict, mode=MODE)
                return
            self.cache.journaliser_appel(
                cle=cle,
                item_id=item_id,
                mode=MODE,
                lot_id=None,
                usage=reponse.usage,
                cout_eur=reponse.cout_eur,
                issue=ISSUE_JUGE,
            )
            self._mettre_en_cache(cle, verdict)
            etat.issues[cle] = _Issue("juge", verdict, mode=MODE)
            return

    def _mettre_en_cache(self, cle: str, verdict: Verdict) -> None:
        """Inscrit le verdict avec le coût et les tokens cumulés de ses tentatives."""
        cout, usage = self.cache.cumul_appels(cle)
        self.cache.ecrire(
            cle,
            verdict,
            modele=self.config.modele,
            effort=self.config.effort_cle,
            mode=MODE,
            cout_eur=cout,
            usage=usage,
        )
