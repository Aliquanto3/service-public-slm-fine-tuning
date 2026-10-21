"""Cœur d'un client compatible OpenAI en flux SSE, sans budget (stories 17.1 et 17.4).

Deux usages :

- `lire_flux` (et `EtatFlux`, `appel_natif`, `lignes_flux`) : lecture d'un flux
  `POST /chat/completions` : commentaires SSE (`: OPENROUTER PROCESSING`) ignorés, `tool_calls`
  fragmentés réassemblés par `index`, deltas de raisonnement (`reasoning`,
  `reasoning_content`) comptés comme activité mais jamais émis, `finish_reason`, `usage`,
  hébergeur (`provider`) et modèle (`model`) relevés. `evaluation.client_distant.ClientDistant`
  l'enveloppe avec son budget et ses contrôles d'hébergeur.
- `ClientOpenAI` : `LlmPort` de l'application (mode hybride, story 17.4), sans registre ni
  fiche. Relances sur 429/5xx **avant le premier octet** seulement. Tout échec lève
  `EchecAppel` avec un code court (`MOTIFS`) : jamais le corps de la réponse, jamais la clé.
  Story 17.6 : chaque appel remet une `MesureAppel` à son observateur (écrite avant `Fin`, ou
  dans un `finally` pour un appel en échec ou interrompu) ; avec un plafond, le coût pire cas
  est réservé avant **chaque** tentative HTTP (`plafond-atteint` sinon ; `tarif-inconnu` sans
  tarif) puis régularisé au coût mesuré ou estimé.

Ce module n'importe ni `slmsp.budget` ni `slmsp.evaluation` (embarqué dans l'application).
"""

from __future__ import annotations

import json
import logging
import random
import ssl
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Final

from pydantic import SecretStr

from slmsp.core.erreurs import HoteBloque, SlmspError
from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton
from slmsp.inference.fournisseurs import (
    HOTE_OPENROUTER,
    PRESET_DEFAUT,
    ajouts_requete,
    corps_reasoning,
    preset,
)
from slmsp.inference.mesures import (
    MesureAppel,
    ObservateurAppels,
    PlafondPort,
    Tarif,
    caracteres_entree,
    estimer_tokens,
    notifier,
    usage_tokens,
)
from slmsp.net.profils import analyser_url, est_adresse_ip
from slmsp.net.relances import (
    DelaisAppel,
    attente_exponentielle,
    lire_retry_after,
    statut_transitoire,
)

Evenement = Jeton | AppelOutil | AppelNonConforme | Fin
LOGGER: Final = logging.getLogger("slmsp.inference.client_openai")

TAILLE_EXTRAIT: Final = 300
OPTIONS_TRANSMISES: Final = frozenset(
    {"temperature", "seed", "max_tokens", "top_p", "top_k", "stop"}
)
OPTIONS_IGNOREES: Final = frozenset({"chat_template_kwargs"})
"""Options du chat template local, sans objet pour une API (jamais transmises : OVH refuse)."""
MAX_TOKENS_DEFAUT: Final = 1024
DELAIS_EXTERNE: Final = DelaisAppel(connexion=10.0, lecture=60.0, total=300.0)
CLES_INTERDITES: Final = frozenset(
    {
        "model",
        "messages",
        "tools",
        "stream",
        "n",
        "max_tokens",
        "max_completion_tokens",
        "max_output_tokens",
    }
)
"""Clés que `parametres_supplementaires` ne peut pas remplacer (longueur et nombre de réponses :
le pire cas du plafond repose sur `max_tokens`)."""
TAILLE_MAX_PARAMETRES: Final = 2048

MOTIFS: Final = frozenset(
    {
        "delai",
        "connexion",
        "cle-absente",
        "hors-ligne",
        "reponse-invalide",
        "plafond-atteint",
        "tarif-inconnu",
        "debit-limite",
    }
)
"""Codes d'échec courts, plus `http-<statut>`. `debit-limite` : accès gratuit OVH (story 17.4b),
2 requêtes par minute : entrée sautée sans appel, HTTP 429 ou coupure avant le premier jeton."""
SUFFIXE_GRATUIT: Final = "-gratuit"
"""Suffixe du fournisseur d'une mesure en accès gratuit (`ovh-gratuit`)."""


def verifier_hote_gratuit(url_base: str, preset_nom: str) -> None:
    """Accès gratuit (sans clé) : l'hôte doit être exactement celui du preset ; `ValueError`."""
    modele = preset(preset_nom)
    if not modele.acces_gratuit or modele.url_base is None:
        raise ValueError("accès gratuit : preset ovh seulement")
    if analyser_url(url_base).hote != analyser_url(modele.url_base).hote:
        raise ValueError("accès gratuit : hôte du preset seulement")


def _entete_entier(entetes: Any, nom: str) -> int | None:
    """Entier d'un en-tête (sans casse) ou `None` ; jamais de levée."""
    try:
        for cle in (nom, nom.title()):
            valeur = entetes.get(cle)
            if valeur is not None:
                return int(float(str(valeur).strip()))
    except Exception:
        return None
    return None


def entier(valeur: Any) -> int | None:
    return valeur if isinstance(valeur, int) and not isinstance(valeur, bool) else None


def appel_natif(cumul: Mapping[str, Any]) -> AppelOutil | AppelNonConforme:
    """Appel d'outil réassemblé (`id`, `nom`, `arguments` bruts, `index`)."""
    bruts = cumul["arguments"]
    nom = cumul["nom"] or None
    try:
        arguments = json.loads(bruts) if bruts.strip() else {}
    except json.JSONDecodeError:
        return AppelNonConforme(nom=nom, arguments_bruts=bruts, motif="arguments : JSON illisible")
    if nom is None:
        return AppelNonConforme(nom=None, arguments_bruts=bruts, motif="nom d'outil absent")
    if not isinstance(arguments, dict):
        return AppelNonConforme(
            nom=nom, arguments_bruts=bruts, motif="arguments : objet JSON attendu"
        )
    identifiant = cumul["id"] or f"appel-{cumul['index']}"
    return AppelOutil(id=identifiant, nom=nom, arguments=arguments)


def lignes_flux(reponse: Any) -> Iterator[str | None]:
    """Lignes du flux ; `None` final si le transport coupe le flux."""
    lignes = reponse.iter_lines()
    while True:
        try:
            yield next(lignes)
        except StopIteration:
            return
        except Exception:
            yield None
            return


@dataclass
class EtatFlux:
    """Ce que la lecture d'un flux a relevé (rempli par `lire_flux`)."""

    premier: float | None = None
    appels: dict[int, dict[str, Any]] = field(default_factory=dict)
    raison_finale: str | None = None
    termine: bool = False
    coupe: bool = False
    usage: dict[str, Any] | None = None
    hebergeur: str | None = None
    modele: str | None = None
    erreur: tuple[str, str] | None = None
    """`(code, message)` : `erreur_flux`, `flux_invalide`, ou celui d'un `controle`."""
    caracteres_raisonnement: int = 0
    """Taille du raisonnement reçu (jamais émis) : compté dans l'estimation sans usage."""

    def appels_natifs(self) -> list[AppelOutil | AppelNonConforme]:
        return [appel_natif(self.appels[i]) for i in sorted(self.appels)]


Controle = Callable[[str, str], tuple[str, str] | None]
"""`controle(champ, valeur)` (`provider` ou `model`) : erreur `(code, message)` ou `None`."""


def lire_flux(
    reponse: Any,
    etat: EtatFlux,
    horloge: Callable[[], float],
    controle: Controle | None = None,
) -> Iterator[Jeton]:
    """Émet les `Jeton` du flux et remplit `etat` (voir le module).

    Une erreur de lecture (morceau mal formé) est consignée dans `etat.erreur`, jamais levée ;
    une `BaseException` (consommateur fermé) traverse.
    """
    try:
        for ligne in lignes_flux(reponse):
            if ligne is None:
                etat.coupe = True
                break
            if not ligne.startswith("data:"):
                continue  # ligne vide ou commentaire SSE (`: OPENROUTER PROCESSING`)
            donnees = ligne[5:].strip()
            if donnees == "[DONE]":
                etat.termine = True
                break
            try:
                morceau = json.loads(donnees)
            except json.JSONDecodeError:
                continue
            if not isinstance(morceau, dict):
                continue
            if isinstance(morceau.get("usage"), dict):
                etat.usage = morceau["usage"]
            if isinstance(morceau.get("provider"), str):
                etat.hebergeur = morceau["provider"]
                if controle is not None and (erreur := controle("provider", etat.hebergeur)):
                    etat.erreur = erreur
                    break
            if isinstance(morceau.get("model"), str):
                etat.modele = morceau["model"]
                if controle is not None and (erreur := controle("model", etat.modele)):
                    etat.erreur = erreur
                    break
            if "error" in morceau:
                extrait = json.dumps(morceau["error"], ensure_ascii=False)[:TAILLE_EXTRAIT]
                etat.erreur = ("erreur_flux", f"erreur en flux : {extrait}")
                break
            for choix in morceau.get("choices") or []:
                if not isinstance(choix, dict):
                    continue
                delta = choix.get("delta") or {}
                if not isinstance(delta, dict):
                    raise TypeError("delta non objet")
                raisonnement = delta.get("reasoning") or delta.get("reasoning_content")
                if isinstance(raisonnement, str):
                    etat.caracteres_raisonnement += len(raisonnement)
                if etat.premier is None and raisonnement:
                    etat.premier = horloge()  # raisonnement : compté, jamais émis
                contenu = delta.get("content")
                if isinstance(contenu, str) and contenu:
                    if etat.premier is None:
                        etat.premier = horloge()
                    yield Jeton(texte=contenu)
                for fragment in delta.get("tool_calls") or []:
                    if etat.premier is None:
                        etat.premier = horloge()
                    if not isinstance(fragment, dict):
                        raise TypeError("fragment tool_calls non objet")
                    index = entier(fragment.get("index", 0))
                    if index is None:
                        raise TypeError("index tool_calls non entier")
                    cumul = etat.appels.setdefault(
                        index, {"index": index, "id": None, "nom": "", "arguments": ""}
                    )
                    if isinstance(fragment.get("id"), str) and fragment["id"]:
                        cumul["id"] = fragment["id"]
                    fonction = fragment.get("function") or {}
                    if not isinstance(fonction, dict):
                        raise TypeError("function non objet")
                    nom = fonction.get("name")
                    if isinstance(nom, str) and nom and not cumul["nom"]:
                        cumul["nom"] = nom
                    if isinstance(fonction.get("arguments"), str):
                        cumul["arguments"] += fonction["arguments"]
                if choix.get("finish_reason"):
                    etat.raison_finale = str(choix["finish_reason"])
    except Exception as exc:
        etat.erreur = ("flux_invalide", f"morceau SSE illisible ({type(exc).__name__} : {exc})")


# --- Client de l'application -------------------------------------------------------------


class EchecAppel(SlmspError):
    """Échec d'un appel au modèle externe : `code` court (`MOTIFS` ou `http-<statut>`).

    Le message ne contient que le code : ni corps de réponse, ni clé, ni texte saisi.
    """

    def __init__(self, code: str) -> None:
        super().__init__(f"modèle externe : {code}")
        self.code = code


def motif_exception(exc: BaseException) -> str:
    """Code court d'une exception de transport."""
    if isinstance(exc, HoteBloque):
        return "hors-ligne"
    if isinstance(exc, TimeoutError) or any(
        "Timeout" in classe.__name__ for classe in type(exc).__mro__
    ):
        return "delai"
    return "connexion"


def _coupure_tls(exc: BaseException) -> bool:
    """Vrai pour une coupure TLS ou EOF (cause comprise) ; refus, DNS et délai : faux."""
    vus = 0
    courant: BaseException | None = exc
    while courant is not None and vus < 5:
        if isinstance(courant, (ssl.SSLError, EOFError)):
            return True
        noms = {classe.__name__ for classe in type(courant).__mro__}
        if noms & {"ReadError", "RemoteProtocolError"} or "EOF" in str(courant):
            return True
        courant = courant.__cause__ or courant.__context__
        vus += 1
    return False


def valider_url_base(url_base: Any) -> str:
    """`url_base` HTTPS (port 443), nom d'hôte sans identifiants, ni requête ni fragment.

    Rend l'URL sans `/` final ; lève `ValueError` (message sans l'URL : elle peut porter un
    secret mal placé).
    """
    if not isinstance(url_base, str) or not url_base.strip() or len(url_base) > 512:
        raise ValueError("URL attendue")
    try:
        cible = analyser_url(url_base.strip())
    except ValueError:
        raise ValueError("URL illisible") from None
    if cible.schema != "https":
        raise ValueError("HTTPS seulement")
    if cible.port not in (None, 443):
        raise ValueError("port 443 seulement")
    if cible.identifiants:
        raise ValueError("identifiants interdits dans l'URL")
    if not cible.hote or est_adresse_ip(cible.hote):
        raise ValueError("nom d'hôte attendu")
    if cible.requete or "#" in url_base:
        raise ValueError("ni requête ni fragment dans l'URL")
    return url_base.strip().rstrip("/")


def valider_parametres(parametres: Any) -> dict[str, Any]:
    """`parametres_supplementaires` : objet JSON ≤ 2 Ko, sans clé de `CLES_INTERDITES`."""
    if parametres is None:
        return {}
    if not isinstance(parametres, dict):
        raise ValueError("paramètres supplémentaires : objet JSON attendu")
    interdites = sorted(set(parametres) & CLES_INTERDITES)
    if interdites:
        raise ValueError(f"paramètres supplémentaires : clés interdites ({', '.join(interdites)})")
    try:
        texte = json.dumps(parametres, ensure_ascii=False)
    except (TypeError, ValueError):
        raise ValueError("paramètres supplémentaires : JSON invalide") from None
    if len(texte.encode("utf-8")) > TAILLE_MAX_PARAMETRES:
        raise ValueError("paramètres supplémentaires : 2 Ko au plus")
    return json.loads(texte)


def chemin_completions(url_base: str) -> str:
    """Chemin exact de `POST <url_base>/chat/completions`."""
    return analyser_url(url_base.rstrip("/") + "/chat/completions").chemin


class ClientOpenAI:
    """`LlmPort` d'un endpoint compatible OpenAI (voir le module).

    `http` : client gardé par la passerelle (profil `modele-externe`, délais `DELAIS_EXTERNE`).
    `taille_contexte` vaut `None` : le composite hybride expose celle du modèle local.
    """

    taille_contexte: int | None = None

    def __init__(
        self,
        http: Any,
        url_base: str,
        modele: str,
        cle: SecretStr | None,
        *,
        preset_nom: str | None = None,
        parametres_supplementaires: Mapping[str, Any] | None = None,
        relances_max: int = 1,
        attente_plafond: float = 5.0,
        dormir: Callable[[float], None] = time.sleep,
        alea: Callable[[], float] = random.random,
        horloge: Callable[[], float] = time.perf_counter,
        observateur: ObservateurAppels | None = None,
        plafond: PlafondPort | None = None,
        tarif: Tarif | None = None,
        usage_flux: bool = False,
        acces_gratuit: bool = False,
    ) -> None:
        self.http = http
        self.url_base = valider_url_base(url_base)
        self.hote = analyser_url(self.url_base).hote
        self.modele = modele
        self._cle = cle
        if preset_nom is None:
            preset_nom = "openrouter" if self.hote == HOTE_OPENROUTER else PRESET_DEFAUT
        self.preset = preset(preset_nom)
        self.parametres = valider_parametres(dict(parametres_supplementaires or {}))
        if self.parametres and not self.preset.parametres_libres:
            raise ValueError("paramètres supplémentaires : preset generique seulement")
        self.relances_max = relances_max
        self.attente_plafond = attente_plafond
        self._dormir = dormir
        self._alea = alea
        self._horloge = horloge
        self.derniere_duree_ms: int | None = None
        self.observateur = observateur
        self.acces_gratuit = acces_gratuit
        if acces_gratuit:
            verifier_hote_gratuit(self.url_base, self.preset.nom)
        # Accès gratuit : coût 0, aucune réservation sur le plafond (pire cas 0).
        self.plafond = None if acces_gratuit else plafond
        self.tarif = Tarif(0.0, 0.0) if acces_gratuit else tarif
        self.usage_flux = usage_flux
        self.debit_restant: int | None = None
        """Dernier `ratelimit-remaining` reçu (accès gratuit), sinon `None`."""
        self._debit_reprise: float | None = None
        """Instant (horloge du client) où le débit se renouvelle, si connu."""

    @property
    def fournisseur_mesure(self) -> str:
        return self.preset.nom + (SUFFIXE_GRATUIT if self.acces_gratuit else "")

    def _noter_debit(self, entetes: Any) -> None:
        """Mémorise `ratelimit-remaining` et `ratelimit-reset` (secondes) d'une réponse."""
        restant = _entete_entier(entetes, "ratelimit-remaining")
        if restant is None:
            return
        self.debit_restant = restant
        reset = _entete_entier(entetes, "ratelimit-reset")
        self._debit_reprise = self._horloge() + max(0, reset) if reset is not None else None

    def _noter_429(self, entetes: Any) -> None:
        """429 : débit épuisé jusqu'à `ratelimit-reset` (60 s si absent)."""
        reset = _entete_entier(entetes, "ratelimit-reset")
        self.debit_restant = 0
        self._debit_reprise = self._horloge() + (60 if reset is None else max(0, reset))

    def _debit_epuise(self) -> bool:
        """Vrai si le dernier `remaining` vaut 0 et que le `reset` n'est pas écoulé."""
        return (
            self.debit_restant == 0
            and self._debit_reprise is not None
            and self._horloge() < self._debit_reprise
        )

    @property
    def identifiant(self) -> str:
        """`externe:<preset>/<modèle>` (traçabilité de l'Historique)."""
        return f"externe:{self.preset.nom}/{self.modele}"

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
        corps: dict[str, Any] = dict(self.parametres)
        corps.update(
            {
                "model": self.modele,
                "messages": [dict(m) for m in messages],
                "stream": True,
            }
        )
        # Options, graine et ajouts du preset ; imposés après les paramètres supplémentaires :
        # aucun ne lève le refus de collecte d'OpenRouter.
        corps.update(ajouts_requete(self.preset, self.hote, options, usage_flux=self.usage_flux))
        corps.setdefault("max_tokens", MAX_TOKENS_DEFAUT)
        if tools:
            corps["tools"] = list(tools)
        return corps

    def compter_tokens(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None = None,
    ) -> int:
        """Estimation grossière (caractères ÷ 3) ; le composite compte avec le modèle local."""
        texte = json.dumps({"messages": list(messages), "tools": list(tools or [])})
        return -(-len(texte) // 3)

    def generer(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Iterator[Evenement]:
        corps = self.corps_generation(messages, tools=tools, options=options)
        return self._appel(corps)

    def _appel(self, corps: dict[str, Any]) -> Iterator[Evenement]:
        if self.acces_gratuit:
            entetes: dict[str, str] = {}  # accès anonyme : jamais d'`Authorization`
        elif self._cle is None or not self._cle.get_secret_value():
            raise EchecAppel("cle-absente")
        else:
            entetes = {"Authorization": f"Bearer {self._cle.get_secret_value()}"}
        url = self.url_base + "/chat/completions"
        suivi = _Suivi(caracteres_entree(corps))
        max_tokens = entier(corps.get("max_tokens")) or MAX_TOKENS_DEFAUT
        debut = self._horloge()
        relances = 0
        try:
            if self.acces_gratuit and self._debit_epuise():
                self._mesurer(debut)
                suivi.motif = "debit-limite"  # sauté sans appel : le reset n'est pas écoulé
                raise EchecAppel(suivi.motif)
            while True:
                if self.plafond is not None:
                    self._reserver(max_tokens, relances, suivi)
                try:
                    contexte = self.http.stream("POST", url, json=corps, headers=entetes)
                    reponse = contexte.__enter__()
                except Exception as exc:
                    self._mesurer(debut)
                    suivi.motif = motif_exception(exc)
                    if self.acces_gratuit and _coupure_tls(exc):
                        suivi.motif = "debit-limite"  # coupure TLS/EOF : limite de débit d'OVH
                    raise EchecAppel(suivi.motif) from None
                try:
                    if self.acces_gratuit:
                        self._noter_debit(reponse.headers)
                    if reponse.status_code != 200:
                        statut = int(reponse.status_code)
                        if self.acces_gratuit and statut == 429:
                            self._mesurer(debut)  # pas de relance ni d'attente
                            self._noter_429(reponse.headers)
                            suivi.motif = "debit-limite"
                            raise EchecAppel(suivi.motif)
                        valeur = reponse.headers.get("Retry-After")
                        if statut_transitoire(statut) and relances < self.relances_max:
                            relances += 1
                            attente = lire_retry_after(valeur if isinstance(valeur, str) else None)
                            if attente is None:
                                attente = attente_exponentielle(
                                    relances, 1.0, self.attente_plafond, self._alea
                                )
                            self._dormir(min(attente, self.attente_plafond))
                            continue
                        self._mesurer(debut)
                        suivi.motif = f"http-{statut}"
                        raise EchecAppel(suivi.motif)
                    suivi.ouvert = True
                    for evenement in self._lire(reponse, debut, suivi):
                        if isinstance(evenement, Fin):
                            self._clore(suivi, debut)  # mesure écrite avant que `Fin` sorte
                        yield evenement
                    return
                finally:
                    contexte.__exit__(None, None, None)
        finally:
            if not suivi.clos:
                if suivi.ouvert and suivi.motif is None:
                    suivi.motif = "interrompu"  # flux fermé par le consommateur (arrêt)
                self._clore(suivi, debut)

    def _reserver(self, max_tokens: int, relances: int, suivi: _Suivi) -> None:
        """Réserve le pire cas de la tentative et des relances restantes ; lève sinon.

        La réservation d'une tentative précédente (refusée avant tout token) est rendue.
        """
        assert self.plafond is not None
        if suivi.reservation is not None:
            jeton, suivi.reservation = suivi.reservation, None
            self.plafond.regulariser(jeton, 0.0)
        if self.tarif is None:
            suivi.motif = "tarif-inconnu"
            raise EchecAppel(suivi.motif)
        montant = self.tarif.pire_cas(
            suivi.caracteres_entree, max_tokens, 1 + self.relances_max - relances
        )
        suivi.reservation = self.plafond.reserver(self.hote, self.modele, montant)
        if suivi.reservation is None:
            suivi.motif = "plafond-atteint"
            raise EchecAppel(suivi.motif)

    def _clore(self, suivi: _Suivi, debut: float) -> None:
        """Écrit la mesure (une seule fois) et régularise la réservation au coût retenu.

        Réponse complète : usage renvoyé, sinon estimation (caractères ÷ 2,5). Flux ouvert puis
        coupé, en erreur ou arrêté : estimation, `interrompu`. Aucune réponse (refus, HTTP,
        connexion) : 0 token, 0 €.
        """
        if suivi.clos:
            return
        suivi.clos = True
        self._mesurer(debut)
        tokens: tuple[int, int] | None = (0, 0)
        estime = False
        if suivi.ouvert:
            tokens = usage_tokens(suivi.usage) if suivi.motif is None else None
            estime = tokens is None
            if tokens is None:
                tokens = (
                    estimer_tokens(suivi.caracteres_entree),
                    estimer_tokens(suivi.total_sortie()),
                )
        assert tokens is not None
        cout = self.tarif.cout(*tokens) if self.tarif is not None else None
        if suivi.reservation is not None and self.plafond is not None:
            jeton, suivi.reservation = suivi.reservation, None
            try:
                self.plafond.regulariser(jeton, cout or 0.0)
            except Exception as exc:
                LOGGER.error("régularisation du plafond impossible (%s)", type(exc).__name__)
        notifier(
            self.observateur,
            MesureAppel(
                fournisseur=self.fournisseur_mesure,
                hote=self.hote,
                modele=self.modele,
                tokens_entree=tokens[0],
                tokens_sortie=tokens[1],
                estime=estime,
                interrompu=suivi.ouvert and suivi.motif is not None,
                duree_ms=self.derniere_duree_ms or 0,
                premier_token_ms=suivi.premier_ms,
                cout_eur=cout,
                motif=suivi.motif,
            ),
        )

    def _mesurer(self, debut: float) -> None:
        self.derniere_duree_ms = round((self._horloge() - debut) * 1000)

    def _lire(self, reponse: Any, debut: float, suivi: _Suivi) -> Iterator[Evenement]:
        etat = EtatFlux()
        suivi.etat = etat  # raisonnement et appels d'outils comptés même si le flux est coupé

        def premier() -> None:
            if suivi.premier_ms is None and etat.premier is not None:
                suivi.premier_ms = round((etat.premier - debut) * 1000)

        for jeton in lire_flux(reponse, etat, self._horloge):
            suivi.caracteres_sortie += len(jeton.texte)
            premier()
            yield jeton
        self._mesurer(debut)
        premier()
        if etat.erreur is not None or etat.raison_finale == "error":
            suivi.motif = "reponse-invalide"
            raise EchecAppel(suivi.motif)
        if etat.coupe or (etat.raison_finale is None and not etat.termine):
            suivi.motif = "connexion"
            if self.acces_gratuit and etat.premier is None:
                suivi.motif = "debit-limite"  # coupé avant le premier jeton
            raise EchecAppel(suivi.motif)
        yield from etat.appels_natifs()
        usage: dict[str, int] = {}
        if isinstance(etat.usage, dict):
            for cle in ("prompt_tokens", "completion_tokens", "total_tokens"):
                valeur = entier(etat.usage.get(cle))
                if valeur is not None:
                    usage[cle] = valeur
        suivi.usage = usage or None
        raison = "longueur" if etat.raison_finale == "length" else "terminee"
        yield Fin(raison=raison, usage=usage or None)


@dataclass
class _Suivi:
    """Ce qu'un appel a relevé pour sa mesure : des tailles, jamais de texte."""

    caracteres_entree: int
    caracteres_sortie: int = 0
    premier_ms: int | None = None
    usage: dict[str, int] | None = None
    ouvert: bool = False
    """Statut 200 reçu : le fournisseur a commencé à répondre (et peut facturer)."""
    motif: str | None = None
    reservation: Any = None
    clos: bool = False
    etat: EtatFlux | None = None

    def total_sortie(self) -> int:
        """Caractères de sortie : texte émis, raisonnement (jamais émis) et appels d'outils."""
        total = self.caracteres_sortie
        if self.etat is not None:
            total += self.etat.caracteres_raisonnement + sum(
                len(a["nom"]) + len(a["arguments"]) for a in self.etat.appels.values()
            )
        return total


__all__ = [
    "DELAIS_EXTERNE",
    "HOTE_OPENROUTER",
    "MOTIFS",
    "ClientOpenAI",
    "EchecAppel",
    "EtatFlux",
    "appel_natif",
    "chemin_completions",
    "corps_reasoning",
    "lignes_flux",
    "lire_flux",
    "motif_exception",
    "valider_parametres",
    "valider_url_base",
]
