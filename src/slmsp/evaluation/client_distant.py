"""`LlmPort` d'un modèle distant (story 17.1) : Chat Completions en flux SSE, sous budget.

`ClientDistant.generer` rend les mêmes évènements que `inference.client.ClientLlama`
(`Jeton`, `AppelOutil`/`AppelNonConforme`, un seul `Fin`), pour que la boucle d'évaluation
ne change pas. Par appel :

1. contrôle du plafond du run (`plafond_eur` : coût réel cumulé + coût pire cas de l'appel)
   puis réservation au registre (usage `eval-distant`, poste `openrouter`), tokens d'entrée
   estimés à `caractères de la requête ÷ 3` bornés par le `contexte` de la fiche (le
   registre applique sa majoration), sortie au pire cas = `max_tokens` ;
2. `POST /chat/completions` en flux par la passerelle (profil `eval-distant`), corps
   complété de `provider` (hébergeur épinglé, sans repli, collecte refusée, quantification),
   `reasoning` désactivé et `usage.include` ;
3. relances (au plus `RELANCES_MAX`, `Retry-After` respecté) sur 429/5xx **avant le premier
   octet** seulement ; chaque relance libère sa réservation puis en refait une ;
4. lecture du flux : commentaires SSE (`: OPENROUTER PROCESSING`) ignorés, `tool_calls`
   fragmentés réassemblés par `index`, hébergeur (`provider`) et modèle (`model`) renvoyés
   contrôlés contre la fiche ;
5. règlement au coût réel (`usage` renvoyé), au pire cas réservé sans usage connu.

Une erreur d'item (`ErreurDistante`, avec son `code`) laisse l'item en erreur ; une erreur
fatale (`BudgetEpuise`, `PlafondGenerationAtteint`, `SecretManquant`,
`ConfigurationInvalide`, `TarifInconnu`, `HoteBloque`) est mémorisée dans `erreur_fatale` :
le Harnais l'avale en `Erreur`, la boucle d'évaluation la relève et interrompt le run.
Chaque appel laisse un relevé (`vider`) : modèle, hébergeur effectif, quantification,
`finish_reason`, usage, coût, temps au premier token et débit mesurés côté client.
"""

from __future__ import annotations

import json
import math
import random
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from typing import Any, Final

from pydantic import SecretStr

from slmsp.budget.registre import RegistreBudget
from slmsp.budget.tarifs import UsageTokens, cout_pire_cas
from slmsp.core.erreurs import (
    BudgetEpuise,
    ConfigurationInvalide,
    HoteBloque,
    SecretManquant,
    SlmspError,
    TarifInconnu,
)
from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton
from slmsp.evaluation.modele_distant import ModeleDistant
from slmsp.inference.client_openai import (
    OPTIONS_IGNOREES,
    OPTIONS_TRANSMISES,
    TAILLE_EXTRAIT,
    EtatFlux,
    appel_natif,
    corps_reasoning,
    lignes_flux,
    lire_flux,
)
from slmsp.inference.client_openai import entier as _entier
from slmsp.net.relances import attente_exponentielle, lire_retry_after, statut_transitoire

USAGE_BUDGET: Final = "eval-distant"
MODE_TARIF: Final = "direct"
RELANCES_MAX: Final = 3
ATTENTE_BASE: Final = 2.0
ATTENTE_PLAFOND: Final = 60.0
CARACTERES_PAR_TOKEN: Final = 3
MAX_TOKENS_DEFAUT: Final = 1024
"""`max_tokens` d'un appel sans cette option (le Harnais la fixe toujours)."""

FATALES: Final = (
    BudgetEpuise,
    SecretManquant,
    ConfigurationInvalide,
    TarifInconnu,
    HoteBloque,
)

Evenement = Jeton | AppelOutil | AppelNonConforme | Fin


class PlafondGenerationAtteint(BudgetEpuise):
    """Le coût du run dépasserait `--plafond-generation` : run interrompu, reprenable."""


class ErreurDistante(SlmspError):
    """Échec d'un appel distant propre à l'item : `code` le nomme dans le run."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code} : {message}")
        self.code = code


class ClientDistant:
    """`LlmPort` d'un modèle distant (voir le module).

    `taille_contexte` vaut `None` : le Harnais rend les passages sans découpage ni mesure,
    `compter_tokens` n'est qu'une estimation (plafond des Tâches de réécriture).
    """

    taille_contexte: int | None = None

    def __init__(
        self,
        modele: ModeleDistant,
        registre: RegistreBudget,
        http: Any,
        cle: SecretStr,
        *,
        plafond_eur: float,
        cout_deja_eur: float = 0.0,
        dormir: Callable[[float], None] = time.sleep,
        alea: Callable[[], float] = random.random,
        horloge: Callable[[], float] = time.perf_counter,
    ) -> None:
        self.modele = modele
        self.fiche = modele.fiche
        self.registre = registre
        self.http = http
        self._cle = cle
        self.plafond_eur = plafond_eur
        self.cout_cumule_eur = cout_deja_eur
        self._dormir = dormir
        self._alea = alea
        self._horloge = horloge
        self.erreur_fatale: BaseException | None = None
        self.code_erreur: str | None = None
        self._releves: list[dict[str, Any]] = []
        self.poste, self.sous_poste = registre.verifier_usage(USAGE_BUDGET)

    # -- Suivi par item --

    def vider(self) -> tuple[list[dict[str, Any]], str | None]:
        """Relevés des appels et code d'erreur d'item depuis le dernier appel, remis à zéro."""
        releves, code = self._releves, self.code_erreur
        self._releves, self.code_erreur = [], None
        return releves, code

    def _fatale(self, exc: BaseException) -> BaseException:
        self.erreur_fatale = exc
        return exc

    def _item(self, code: str, message: str) -> ErreurDistante:
        self.code_erreur = code
        return ErreurDistante(code, message)

    # -- LlmPort --

    def compter_tokens(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None = None,
    ) -> int:
        """Estimation : caractères de `messages` (et `tools`) sérialisés ÷ 3."""
        texte = json.dumps({"messages": list(messages), "tools": list(tools or [])})
        return math.ceil(len(texte) / CARACTERES_PAR_TOKEN)

    def corps_generation(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Corps JSON de `/chat/completions` ; `ValueError` pour une option inconnue."""
        options = dict(options or {})
        inconnues = sorted(set(options) - OPTIONS_TRANSMISES - OPTIONS_IGNOREES)
        if inconnues:
            raise ValueError(f"options inconnues : {', '.join(inconnues)}")
        corps: dict[str, Any] = {
            "model": self.fiche.modele_id,
            "messages": [dict(m) for m in messages],
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        corps.update({cle: v for cle, v in options.items() if cle in OPTIONS_TRANSMISES})
        corps.setdefault("max_tokens", MAX_TOKENS_DEFAUT)
        if tools:
            corps["tools"] = list(tools)
        corps["provider"] = {
            "order": [self.fiche.hebergeur],
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "deny",
            "quantizations": [self.fiche.quantification],
        }
        corps["reasoning"] = corps_reasoning()
        corps["usage"] = {"include": True}
        return corps

    def tokens_entree_estimes(self, corps: Mapping[str, Any]) -> int:
        texte = json.dumps({"messages": corps["messages"], "tools": corps.get("tools") or []})
        return min(math.ceil(len(texte) / CARACTERES_PAR_TOKEN), self.fiche.contexte)

    def generer(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Iterator[Evenement]:
        corps = self.corps_generation(messages, tools=tools, options=options)
        return self._appel(corps)

    # -- Appel --

    def _reserver(self, corps: Mapping[str, Any], tokens_entree: int) -> int:
        if self.erreur_fatale is not None:
            raise self.erreur_fatale
        modele, max_tokens = self.fiche.modele_id, int(corps["max_tokens"])
        try:
            pire = cout_pire_cas(
                self.registre.tarifs,
                modele,
                MODE_TARIF,
                tokens_entree,
                max_tokens,
                self.registre.config.majoration_entree,
            )
            if self.cout_cumule_eur + pire > self.plafond_eur:
                raise PlafondGenerationAtteint(
                    f"plafond de génération du run atteint : {self.plafond_eur:.4f} € "
                    f"(dépensé {self.cout_cumule_eur:.4f} €, appel suivant au pire "
                    f"{pire:.4f} €) ; reprendre avec --reprendre et un plafond plus haut"
                )
            return self.registre.reserver(
                self.poste, self.sous_poste, modele, MODE_TARIF, tokens_entree, max_tokens
            )
        except FATALES as exc:
            raise self._fatale(exc) from None

    def _regler(self, reservation: int, usage: UsageTokens | None) -> float:
        if usage is None:
            cout = self.registre.compter_pire_cas(reservation)
        else:
            cout = self.registre.regulariser(reservation, usage)
        self.cout_cumule_eur += cout
        return cout

    def _appel(self, corps: dict[str, Any]) -> Iterator[Evenement]:
        tokens_entree = self.tokens_entree_estimes(corps)
        entetes = {"Authorization": f"Bearer {self._cle.get_secret_value()}"}
        url = self.modele.fournisseur.url("chat/completions")
        relances = 0
        while True:
            reservation = self._reserver(corps, tokens_entree)
            debut = self._horloge()
            try:
                contexte = self.http.stream("POST", url, json=corps, headers=entetes)
                reponse = contexte.__enter__()
            except BaseException as exc:
                # Une `SlmspError` (`HoteBloque`…) part avant tout envoi : rien n'est facturé ;
                # sinon la requête a pu partir : comptée au pire cas.
                cout = self._regler(reservation, _ZERO if isinstance(exc, SlmspError) else None)
                if isinstance(exc, HoteBloque):
                    raise self._fatale(exc) from None
                self._releve(None, None, None, None, cout, None, relances, "transport")
                if not isinstance(exc, Exception):
                    raise
                raise self._item(
                    "transport", f"échec sans réponse HTTP ({type(exc).__name__})"
                ) from None
            try:
                if reponse.status_code != 200:
                    statut = int(reponse.status_code)
                    self._regler(reservation, _ZERO)  # refus HTTP : rien n'est facturé
                    try:
                        reponse.read()
                        extrait = reponse.text[:TAILLE_EXTRAIT]
                    except Exception:
                        extrait = "(corps illisible)"
                    valeur = reponse.headers.get("Retry-After")
                    if statut_transitoire(statut) and relances < RELANCES_MAX:
                        relances += 1
                        attente = lire_retry_after(valeur if isinstance(valeur, str) else None)
                        if attente is None:
                            attente = attente_exponentielle(
                                relances, ATTENTE_BASE, ATTENTE_PLAFOND, self._alea
                            )
                        self._dormir(min(attente, ATTENTE_PLAFOND))
                        continue
                    code = f"http-{statut}"
                    self._releve(None, None, None, None, 0.0, None, relances, code)
                    raise self._item(code, f"HTTP {statut} : {extrait}")
                yield from self._lire(reponse, reservation, debut, relances)
                return
            finally:
                contexte.__exit__(None, None, None)

    def _lignes(self, reponse: Any) -> Iterator[str | None]:
        """Lignes du flux ; `None` final si le transport coupe le flux."""
        return lignes_flux(reponse)

    def _controle(self, champ: str, valeur: str) -> tuple[str, str] | None:
        """Hébergeur et modèle renvoyés contrôlés contre la fiche (`lire_flux`)."""
        if champ == "provider" and valeur != self.fiche.hebergeur:
            return (
                "hebergeur_inattendu",
                f"hébergeur {valeur!r} au lieu de {self.fiche.hebergeur!r}",
            )
        if champ == "model" and valeur != self.fiche.modele_id:
            return ("modele_inattendu", f"modèle {valeur!r} au lieu de {self.fiche.modele_id!r}")
        return None

    def _lire(
        self, reponse: Any, reservation: int, debut: float, relances: int
    ) -> Iterator[Evenement]:
        etat = EtatFlux()
        try:
            yield from lire_flux(reponse, etat, self._horloge, self._controle)
        except BaseException:
            # Lecture abandonnée (consommateur fermé, interruption) : réglée au pire cas.
            cout = self._regler(reservation, None)
            self._releve(
                etat.modele,
                etat.hebergeur,
                etat.raison_finale,
                etat.usage,
                cout,
                None,
                relances,
                "abandon",
            )
            raise
        premier, appels, raison_finale = etat.premier, etat.appels, etat.raison_finale
        termine, coupe, usage = etat.termine, etat.coupe, etat.usage
        hebergeur, modele, erreur = etat.hebergeur, etat.modele, etat.erreur
        fin = self._horloge()

        if erreur is None:
            if raison_finale == "error":
                erreur = ("erreur_flux", "finish_reason error")
            elif coupe or (raison_finale is None and not termine):
                erreur = ("flux_coupe", "flux interrompu avant sa fin")
            elif hebergeur is None:
                erreur = ("hebergeur_inattendu", "hébergeur non renvoyé par le fournisseur")
        tokens = self._usage(usage)
        cout = self._regler(reservation, tokens)
        delai = None if premier is None else round((premier - debut) * 1000)
        debit = None
        if tokens is not None and premier is not None and fin > premier:
            debit = round(tokens.sortie / (fin - premier), 2)
        self._releve(
            modele,
            hebergeur,
            raison_finale,
            usage,
            cout,
            (delai, debit),
            relances,
            None if erreur is None else erreur[0],
        )
        if erreur is not None:
            raise self._item(*erreur)
        for index in sorted(appels):
            yield appel_natif(appels[index])
        usage_fin: dict[str, int] = {}
        if tokens is not None:
            usage_fin = {
                "prompt_tokens": tokens.entree,
                "completion_tokens": tokens.sortie,
                "total_tokens": tokens.entree + tokens.sortie,
            }
        if delai is not None:
            usage_fin["delai_premier_token_ms"] = delai
        raison = "longueur" if raison_finale == "length" else "terminee"
        yield Fin(raison=raison, usage=usage_fin or None)

    @staticmethod
    def _usage(usage: Mapping[str, Any] | None) -> UsageTokens | None:
        if usage is None:
            return None
        entree = _entier(usage.get("prompt_tokens"))
        sortie = _entier(usage.get("completion_tokens"))
        if entree is None or sortie is None:
            return None
        total = _entier(usage.get("total_tokens")) or 0
        return UsageTokens(entree, max(sortie, total - entree))

    def _releve(
        self,
        modele: str | None,
        hebergeur: str | None,
        finish_reason: str | None,
        usage: Mapping[str, Any] | None,
        cout: float | None,
        mesures: tuple[int | None, float | None] | None,
        relances: int,
        erreur: str | None,
    ) -> None:
        delai, debit = mesures if mesures is not None else (None, None)
        self._releves.append(
            {
                "modele_id": self.fiche.modele_id,
                "modele_renvoye": modele,
                "hebergeur_epingle": self.fiche.hebergeur,
                "hebergeur_effectif": hebergeur,
                "quantification": self.fiche.quantification,
                "finish_reason": finish_reason,
                "usage": dict(usage) if usage is not None else None,
                "cout_eur": cout,
                "delai_premier_token_ms": delai,
                "debit_tokens_s": debit,
                "relances": relances,
                "statut": "ok" if erreur is None else "erreur",
                "erreur": erreur,
            }
        )


_ZERO: Final = UsageTokens(0, 0)


__all__ = [
    "FATALES",
    "MODE_TARIF",
    "USAGE_BUDGET",
    "ClientDistant",
    "ErreurDistante",
    "PlafondGenerationAtteint",
    "corps_reasoning",
]
