"""Juge tiers OpenRouter : avis comparatif, hors score officiel (story S3).

`JugeTiers.juger(demandes)` rend un verdict par demande, dans l'ordre :

1. prompt et schéma du Juge principal (`construire_prompt`), pour que l'accord mesure le
   juge et non le prompt ; clé du cache `cle_verdict` (modèle + gabarit + item + sortie,
   effort `ConfigJugeTiers.effort_cle`) ; `ItemNonJugeable` avant tout appel ;
2. cache de verdicts commun : un verdict connu n'est ni redemandé ni réservé ;
3. un appel par item (`ClientCompatibleOpenAI.appeler`, usage `juge-tiers-<fournisseur>`),
   réservation au pire cas de cet item, régularisation après l'appel.

La sortie est lue avec tolérance (`extraire_json` : bloc de code ou texte autour). Deux
sorties non conformes donnent un verdict `invalide` mis en cache si l'écart est au schéma ;
si la dernière ne contient aucun JSON lisible, l'item reste `non-juge` (motif
`sortie-illisible`), sans cache, rejouable. Une sortie interrompue (`finish_reason` de
longueur) n'est **pas** mise en cache ni comptée comme échec : l'item reste `non-juge`
(motif `sortie-interrompue`), rejouable avec un `max_tokens` plus grand. Sur `BudgetEpuise`,
les items restants sont
`non-juge` (motif `budget`). 401, 403 et 429 arrêtent les appels restants.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, Final

from slmsp.budget.tarifs import UsageTokens, cout_estime, cout_pire_cas
from slmsp.core.erreurs import BudgetEpuise
from slmsp.core.items import ItemBase
from slmsp.core.schemas.verdict import Verdict
from slmsp.fournisseurs.client import (
    MODE,
    ClientCompatibleOpenAI,
    ErreurApiFournisseur,
    nouvelle_session,
)
from slmsp.judge.cache import CacheVerdicts, cle_verdict
from slmsp.judge.claude import (
    ECHECS_MAX,
    ISSUE_ERREUR_API,
    ISSUE_INVALIDE,
    ISSUE_JUGE,
    ISSUE_NON_CONFORME,
    MOTIF_BUDGET,
    MOTIF_ERREUR_API,
    DemandeJugement,
    EstimationCout,
    RapportJugement,
    ResultatJugement,
    StatutJugement,
    motif_arret,
)
from slmsp.judge.config import ConfigJugeTiers
from slmsp.judge.grille import Grille
from slmsp.judge.prompt import (
    PromptJuge,
    SortieNonConforme,
    construire_prompt,
    estimer_tokens_entree,
    valider_selon_schema,
)

PREFIXE_SESSION: Final = "juge-tiers-"
NOM_SCHEMA: Final = "verdict"
MOTIF_INTERROMPUE: Final = "sortie-interrompue"
ISSUE_INTERROMPUE: Final = "interrompue"
MOTIF_ILLISIBLE: Final = "sortie-illisible"
FINS_INTERROMPUES: Final = frozenset({"length", "max_tokens", "model_length"})
"""`finish_reason` d'une sortie coupée par la longueur (comparés en minuscules)."""


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
    motif: str | None = None


@dataclass
class _Etat:
    issues: dict[str, _Issue] = field(default_factory=dict)
    couts: dict[str, float] = field(default_factory=dict)
    usages: dict[str, UsageTokens] = field(default_factory=dict)
    budget_epuise: bool = False
    arret: str | None = None

    def imputer(self, cle: str, cout: float, usage: UsageTokens | None) -> None:
        self.couts[cle] = self.couts.get(cle, 0.0) + cout
        if usage is not None:
            precedent = self.usages.get(cle)
            self.usages[cle] = usage if precedent is None else precedent + usage


def _objet_equilibre(texte: str, debut: int) -> str | None:
    """Objet JSON `{…}` commençant à `debut` (accolades équilibrées, chaînes comprises)."""
    profondeur, dans_chaine, echappe = 0, False, False
    for position in range(debut, len(texte)):
        car = texte[position]
        if dans_chaine:
            if echappe:
                echappe = False
            elif car == "\\":
                echappe = True
            elif car == '"':
                dans_chaine = False
        elif car == '"':
            dans_chaine = True
        elif car == "{":
            profondeur += 1
        elif car == "}":
            profondeur -= 1
            if profondeur == 0:
                return texte[debut : position + 1]
    return None


def extraire_json(texte: str) -> str | None:
    """Texte JSON d'un verdict, toléré dans un bloc de code ou entouré de texte.

    Sortie entière si elle se lit telle quelle ; sinon premier objet `{…}` lisible ; `None`
    si aucun. Propre au juge tiers : le Juge principal garde sa lecture stricte.
    """
    brut = texte.strip()
    try:
        json.loads(brut)
        return brut
    except ValueError:
        pass
    debut = brut.find("{")
    while debut != -1:
        candidat = _objet_equilibre(brut, debut)
        if candidat is not None:
            try:
                json.loads(candidat)
                return candidat
            except ValueError:
                pass
        debut = brut.find("{", debut + 1)
    return None


class JugeTiers:
    """Juge tiers : `juger(demandes)` et `estimer(demandes)` (voir le module)."""

    def __init__(
        self,
        nom: str,
        config: ConfigJugeTiers,
        client: ClientCompatibleOpenAI,
        cache: CacheVerdicts,
        grille: Grille,
    ) -> None:
        self.nom = nom
        self.config = config
        self.client = client
        self.cache = cache
        self.grille = grille

    def description(self) -> dict[str, Any]:
        """Modèle et réglages, inscrits dans la config du run."""
        return {
            "nom": self.nom,
            "fournisseur": self.config.fournisseur,
            "modele": self.config.modele,
            "effort": self.config.effort_cle,
            "max_tokens": self.config.max_tokens,
        }

    def _preparer(self, demande: DemandeJugement) -> _Preparee:
        prompt = construire_prompt(demande.item, demande.sortie, self.grille)
        cle = cle_verdict(
            demande.item, demande.sortie, prompt, self.config.modele, self.config.effort_cle
        )
        return _Preparee(demande.item, prompt, cle, estimer_tokens_entree(prompt))

    def _uniques(self, demandes: Sequence[DemandeJugement]) -> tuple[list[_Preparee], dict]:
        preparees = [self._preparer(d) for d in demandes]
        uniques: dict[str, _Preparee] = {}
        for preparee in preparees:
            uniques.setdefault(preparee.cle, preparee)
        return preparees, uniques

    # --- estimation ---------------------------------------------------------------------------

    def estimer(self, demandes: Sequence[DemandeJugement]) -> EstimationCout:
        """Coût estimé sans appel ni écriture : cache à 0, doublons comptés une fois.

        Vérifie d'abord l'usage de budget (imputation, poste, sous-poste) : une configuration
        absente lève `ConfigurationInvalide` avant tout run ; un tarif absent, `TarifInconnu`.
        """
        registre = self.client.registre
        registre.verifier_usage(self.config.usage_budget)
        _, uniques = self._uniques(demandes)
        a_juger = [p for cle, p in uniques.items() if self.cache.lire(cle) is None]
        modele = self.config.modele
        estime = sum(
            cout_estime(
                registre.tarifs, modele, MODE, p.tokens_estimes, self.config.sortie_estimation
            )
            for p in a_juger
        )
        pire = sum(
            cout_pire_cas(
                registre.tarifs,
                modele,
                MODE,
                p.tokens_estimes,
                self.config.max_tokens,
                registre.config.majoration_entree,
            )
            for p in a_juger
        )
        return EstimationCout(
            nb_demandes=len(uniques),
            nb_en_cache=len(uniques) - len(a_juger),
            nb_a_juger=len(a_juger),
            cout_estime_eur=estime,
            cout_pire_cas_eur=pire,
        )

    # --- jugement -----------------------------------------------------------------------------

    def juger(self, demandes: Sequence[DemandeJugement]) -> RapportJugement:
        """Juge les demandes (cache, puis appels directs), dans l'ordre des demandes."""
        preparees, uniques = self._uniques(demandes)
        etat = _Etat()
        session_id = nouvelle_session(PREFIXE_SESSION)
        for cle, preparee in uniques.items():
            en_cache = self.cache.lire(cle)
            if en_cache is not None:
                etat.issues[cle] = _Issue(
                    "invalide" if en_cache.verdict.invalide else "juge",
                    en_cache.verdict,
                    depuis_cache=True,
                )
            elif etat.arret is not None:
                etat.issues[cle] = _Issue("non-juge", motif=etat.arret)
            elif etat.budget_epuise:
                etat.issues[cle] = _Issue("non-juge", motif=MOTIF_BUDGET)
            else:
                self._juger_un(preparee, session_id, etat)
        resultats = []
        vues: set[str] = set()
        for p in preparees:
            issue = etat.issues.get(p.cle) or _Issue("non-juge", motif="non-traite")
            sans_cout = issue.depuis_cache or p.cle in vues
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
                    mode=None if issue.depuis_cache else MODE,
                    motif=issue.motif,
                )
            )
        return RapportJugement(tuple(resultats), etat.budget_epuise, sum(etat.couts.values()))

    def _parametres(self, prompt: PromptJuge) -> dict[str, Any]:
        config = self.config
        parametres: dict[str, Any] = {}
        if config.temperature is not None:
            parametres["temperature"] = config.temperature
        if config.effort_raisonnement is not None:
            parametres["reasoning"] = {"effort": config.effort_raisonnement}
        if config.format_reponse == "json_object":
            parametres["response_format"] = {"type": "json_object"}
        else:
            parametres["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": NOM_SCHEMA, "schema": prompt.schema, "strict": True},
            }
        # OpenRouter : n'aiguiller que vers un hébergeur qui accepte tous ces paramètres.
        parametres["provider"] = {"require_parameters": True}
        return parametres

    def _journaliser(
        self, cle: str, item_id: str, usage: UsageTokens | None, cout: float, issue: str
    ) -> None:
        self.cache.journaliser_appel(
            cle=cle,
            item_id=item_id,
            mode=MODE,
            lot_id=None,
            usage=usage,
            cout_eur=cout,
            issue=issue,
        )

    def _juger_un(self, preparee: _Preparee, session_id: str, etat: _Etat) -> None:
        item_id, cle = preparee.item.id, preparee.cle
        while True:  # au plus ECHECS_MAX sorties non conformes (compteur persisté)
            try:
                reponse = self.client.appeler(
                    self.config.usage_budget,
                    session_id,
                    [{"role": "user", "content": preparee.prompt.texte}],
                    modele=self.config.modele,
                    max_tokens=self.config.max_tokens,
                    tokens_entree_estimes=preparee.tokens_estimes,
                    parametres=self._parametres(preparee.prompt),
                )
            except BudgetEpuise:
                etat.budget_epuise = True
                etat.issues[cle] = _Issue("non-juge", motif=MOTIF_BUDGET)
                return
            except ErreurApiFournisseur as exc:
                refus = exc.statut_http is not None and 400 <= exc.statut_http < 500
                etat.imputer(cle, exc.cout_eur, None)
                self._journaliser(
                    cle,
                    item_id,
                    UsageTokens(0, 0) if refus else None,
                    exc.cout_eur,
                    ISSUE_ERREUR_API,
                )
                arret = motif_arret(exc.statut_http) if refus else None
                etat.arret = etat.arret or arret
                etat.issues[cle] = _Issue("non-juge", motif=arret or MOTIF_ERREUR_API)
                return
            etat.imputer(cle, reponse.cout_eur, reponse.usage)
            if (reponse.finish_reason or "").lower() in FINS_INTERROMPUES:
                self._journaliser(cle, item_id, reponse.usage, reponse.cout_eur, ISSUE_INTERROMPUE)
                etat.issues[cle] = _Issue("non-juge", motif=MOTIF_INTERROMPUE)
                return  # ni cache ni échec compté : rejouable
            texte = extraire_json(reponse.texte)
            try:
                if texte is None:
                    raise SortieNonConforme(f"{item_id} : aucun objet JSON dans la sortie")
                verdict = valider_selon_schema(item_id, texte, preparee.prompt.schema)
            except SortieNonConforme as exc:
                invalide = self.cache.compter_echec(cle, item_id, str(exc)) >= ECHECS_MAX
                self._journaliser(
                    cle,
                    item_id,
                    reponse.usage,
                    reponse.cout_eur,
                    ISSUE_INVALIDE if invalide else ISSUE_NON_CONFORME,
                )
                if not invalide:
                    continue
                if texte is None:
                    # Sortie sans JSON lisible : ni cache ni verdict durable, rejouable.
                    etat.issues[cle] = _Issue("non-juge", motif=MOTIF_ILLISIBLE)
                    return
                verdict = Verdict.invalide_pour(item_id)
                self._mettre_en_cache(cle, verdict)
                etat.issues[cle] = _Issue("invalide", verdict)
                return
            self._journaliser(cle, item_id, reponse.usage, reponse.cout_eur, ISSUE_JUGE)
            self._mettre_en_cache(cle, verdict)
            etat.issues[cle] = _Issue("juge", verdict)
            return

    def _mettre_en_cache(self, cle: str, verdict: Verdict) -> None:
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
