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

Ce module n'importe ni `slmsp.budget` ni `slmsp.evaluation` (embarqué dans l'application).
"""

from __future__ import annotations

import json
import random
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
from slmsp.net.profils import analyser_url, est_adresse_ip
from slmsp.net.relances import (
    DelaisAppel,
    attente_exponentielle,
    lire_retry_after,
    statut_transitoire,
)

Evenement = Jeton | AppelOutil | AppelNonConforme | Fin

TAILLE_EXTRAIT: Final = 300
OPTIONS_TRANSMISES: Final = frozenset(
    {"temperature", "seed", "max_tokens", "top_p", "top_k", "stop"}
)
OPTIONS_IGNOREES: Final = frozenset({"chat_template_kwargs"})
"""Options du chat template local, sans objet pour une API (jamais transmises : OVH refuse)."""
MAX_TOKENS_DEFAUT: Final = 1024
DELAIS_EXTERNE: Final = DelaisAppel(connexion=10.0, lecture=60.0, total=300.0)
CLES_INTERDITES: Final = frozenset({"model", "messages", "tools", "stream"})
"""Clés que `parametres_supplementaires` ne peut pas remplacer."""
TAILLE_MAX_PARAMETRES: Final = 2048

MOTIFS: Final = frozenset({"delai", "connexion", "cle-absente", "hors-ligne", "reponse-invalide"})
"""Codes d'échec courts, plus `http-<statut>`."""


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
                if etat.premier is None and (
                    delta.get("reasoning") or delta.get("reasoning_content")
                ):
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
        corps.update(ajouts_requete(self.preset, self.hote, options))
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
        if self._cle is None or not self._cle.get_secret_value():
            raise EchecAppel("cle-absente")
        entetes = {"Authorization": f"Bearer {self._cle.get_secret_value()}"}
        url = self.url_base + "/chat/completions"
        debut = self._horloge()
        relances = 0
        while True:
            try:
                contexte = self.http.stream("POST", url, json=corps, headers=entetes)
                reponse = contexte.__enter__()
            except Exception as exc:
                self._mesurer(debut)
                raise EchecAppel(motif_exception(exc)) from None
            try:
                if reponse.status_code != 200:
                    statut = int(reponse.status_code)
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
                    raise EchecAppel(f"http-{statut}")
                yield from self._lire(reponse, debut)
                return
            finally:
                contexte.__exit__(None, None, None)

    def _mesurer(self, debut: float) -> None:
        self.derniere_duree_ms = round((self._horloge() - debut) * 1000)

    def _lire(self, reponse: Any, debut: float) -> Iterator[Evenement]:
        etat = EtatFlux()
        yield from lire_flux(reponse, etat, self._horloge)
        self._mesurer(debut)
        if etat.erreur is not None or etat.raison_finale == "error":
            raise EchecAppel("reponse-invalide")
        if etat.coupe or (etat.raison_finale is None and not etat.termine):
            raise EchecAppel("connexion")
        yield from etat.appels_natifs()
        usage: dict[str, int] = {}
        if isinstance(etat.usage, dict):
            for cle in ("prompt_tokens", "completion_tokens", "total_tokens"):
                valeur = entier(etat.usage.get(cle))
                if valeur is not None:
                    usage[cle] = valeur
        raison = "longueur" if etat.raison_finale == "length" else "terminee"
        yield Fin(raison=raison, usage=usage or None)


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
