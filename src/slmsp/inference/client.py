"""`LlmPort` sur `llama-server` : API compatible OpenAI en flux (SSE), par `net.client_local`.

Les messages sont transmis tels quels (AD-7 : le prompt est composé par le Harnais).

Protocoles d'outils (`protocole_outils` de `ConfigModele`) :

- `natif` : `tools` est transmis ; les `delta.tool_calls` fragmentés sont réassemblés par
  `index` et rendus en `AppelOutil` (arguments en objet JSON) ou `AppelNonConforme` ;
- `json-generique` : `tools` n'est pas transmis (le chat template ne le gère pas) ; la
  sortie est contrainte par `response_format` (`schema_json_generique`) puis reconvertie :
  `{"tool_calls": [...]}` donne des `AppelOutil`, `{"content": ...}` un `Jeton`, un JSON
  illisible un `Jeton` du texte brut. Décrire les outils dans le prompt reste l'affaire
  du Harnais ;
- `balises-tool-call` (SmolLM3) : `tools` est transmis et rendu par le template du tokenizer
  (AD-13), qui demande au modèle des appels `<tool_call>{"name", "arguments"}</tool_call>`
  dans le texte. Le template ne lit pas `message.tool_calls`, si bien que llama-server ne
  construit aucun parseur d'outils : le client analyse les balises du flux de texte (le texte
  hors balises reste en `Jeton`, émis au fil de l'eau) et réécrit les `tool_calls` des
  messages `assistant` de l'historique en balises dans `content`.

Le flux se termine par un seul `Fin` : `terminee` (`finish_reason` `stop`/`tool_calls`, ou
`[DONE]`), `longueur` (`length`) ou `interrompue` (flux coupé). `usage` porte
`prompt_tokens`, `completion_tokens`, `total_tokens` (s'ils sont reçus) et
`delai_premier_token_ms`.
"""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import Iterator, Mapping, Sequence
from typing import Any, Final

from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton
from slmsp.inference.processus import ErreurInference
from slmsp.net import client_local

OPTIONS_AUTORISEES: Final = frozenset(
    {"temperature", "seed", "max_tokens", "top_p", "top_k", "stop", "chat_template_kwargs"}
)
PROTOCOLES: Final = ("natif", "json-generique", "balises-tool-call")
BALISE_OUVRANTE: Final = "<tool_call>"
BALISE_FERMANTE: Final = "</tool_call>"
CLES_USAGE: Final = ("prompt_tokens", "completion_tokens", "total_tokens")
TAILLE_EXTRAIT: Final = 500
"""Caractères du corps d'une réponse HTTP en erreur cités dans `ErreurInference`."""

Evenement = Jeton | AppelOutil | AppelNonConforme | Fin


def _fonction(outil: Mapping[str, Any]) -> Mapping[str, Any]:
    fonction = outil.get("function") if isinstance(outil, Mapping) else None
    if not isinstance(fonction, Mapping) or not isinstance(fonction.get("name"), str):
        raise ValueError("outil attendu au format OpenAI : {type: function, function: {name}}")
    return fonction


def schema_json_generique(tools: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Schéma JSON de la sortie `json-generique` pour `tools` (format `tools` OpenAI).

    `anyOf` de `{"tool_calls": [{"name": <const>, "arguments": <paramètres>}, ...]}` et de
    `{"content": <chaîne>}`.
    """
    appels = []
    for outil in tools:
        fonction = _fonction(outil)
        parametres = fonction.get("parameters") or {"type": "object"}
        appels.append(
            {
                "type": "object",
                "properties": {"name": {"const": fonction["name"]}, "arguments": parametres},
                "required": ["name", "arguments"],
                "additionalProperties": False,
            }
        )
    if not appels:
        raise ValueError("schema_json_generique exige au moins un outil")
    return {
        "anyOf": [
            {
                "type": "object",
                "properties": {
                    "tool_calls": {"type": "array", "minItems": 1, "items": {"anyOf": appels}}
                },
                "required": ["tool_calls"],
                "additionalProperties": False,
            },
            {
                "type": "object",
                "properties": {"content": {"type": "string"}},
                "required": ["content"],
                "additionalProperties": False,
            },
        ]
    }


def appel_canonique(appel: AppelOutil) -> dict[str, Any]:
    """`AppelOutil` au format `tool_calls` canonique OpenAI (arguments en chaîne JSON)."""
    return {
        "id": appel.id,
        "type": "function",
        "function": {
            "name": appel.nom,
            "arguments": json.dumps(appel.arguments, ensure_ascii=False),
        },
    }


PREFIXE_ID: Final = "appel-"


def nouvel_identifiant() -> str:
    """Identifiant unique d'un appel d'outil sans id du serveur (`appel-<uuid4 hex>`)."""
    return f"{PREFIXE_ID}{uuid.uuid4().hex}"


def _appel(identifiant: str, nom: Any, arguments: Any, bruts: str) -> AppelOutil | AppelNonConforme:
    nom_lu = nom if isinstance(nom, str) and nom else None
    if nom_lu is None:
        return AppelNonConforme(nom=None, arguments_bruts=bruts, motif="nom d'outil absent")
    if not isinstance(arguments, dict):
        return AppelNonConforme(
            nom=nom_lu, arguments_bruts=bruts, motif="arguments : objet JSON attendu"
        )
    return AppelOutil(id=identifiant, nom=nom_lu, arguments=arguments)


def _appel_natif(cumul: Mapping[str, Any]) -> AppelOutil | AppelNonConforme:
    bruts = cumul["arguments"]
    try:
        arguments = json.loads(bruts) if bruts.strip() else {}
    except json.JSONDecodeError:
        nom = cumul["nom"] or None
        return AppelNonConforme(nom=nom, arguments_bruts=bruts, motif="arguments : JSON illisible")
    return _appel(cumul["id"] or nouvel_identifiant(), cumul["nom"], arguments, bruts)


def _sortie_json_generique(texte: str) -> list[Evenement]:
    try:
        sortie = json.loads(texte)
    except json.JSONDecodeError:
        return [Jeton(texte=texte)] if texte else []
    if isinstance(sortie, dict) and isinstance(sortie.get("tool_calls"), list):
        evenements: list[Evenement] = []
        for appel in sortie["tool_calls"]:
            appel = appel if isinstance(appel, dict) else {}
            arguments = appel.get("arguments")
            bruts = json.dumps(arguments, ensure_ascii=False)
            evenements.append(_appel(nouvel_identifiant(), appel.get("name"), arguments, bruts))
        return evenements
    if isinstance(sortie, dict) and isinstance(sortie.get("content"), str):
        return [Jeton(texte=sortie["content"])] if sortie["content"] else []
    return [Jeton(texte=texte)]


def _appel_balise(contenu: str, *, fermee: bool = True) -> AppelOutil | AppelNonConforme:
    """Appel lu entre `<tool_call>` et `</tool_call>` : `{"name": ..., "arguments": {...}}`."""
    try:
        objet = json.loads(contenu)
    except json.JSONDecodeError:
        motif = "<tool_call> : JSON illisible" + ("" if fermee else " (balise non fermée)")
        return AppelNonConforme(nom=None, arguments_bruts=contenu, motif=motif)
    if not isinstance(objet, dict):
        return AppelNonConforme(
            nom=None, arguments_bruts=contenu, motif="<tool_call> : objet JSON attendu"
        )
    arguments = objet.get("arguments")
    if isinstance(arguments, str):  # arguments en chaîne JSON (format OpenAI)
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            pass
    bruts = json.dumps(arguments, ensure_ascii=False)
    return _appel(nouvel_identifiant(), objet.get("name"), arguments, bruts)


def _prefixe_en_attente(texte: str, balise: str) -> int:
    """Longueur du plus long suffixe de `texte` qui commence `balise` (à retenir)."""
    for taille in range(min(len(texte), len(balise) - 1), 0, -1):
        if balise.startswith(texte[-taille:]):
            return taille
    return 0


class LecteurBalises:
    """Analyse incrémentale des `<tool_call>…</tool_call>` d'un flux de texte.

    Le texte hors balises est rendu en `Jeton` dès qu'il ne peut plus commencer une balise ;
    chaque balise fermée donne un `AppelOutil` ou un `AppelNonConforme`. `finir` rend le
    reste : une balise non fermée (arrêt sur `<|im_end|>` ou longueur) est analysée quand
    même, et son JSON illisible donne un `AppelNonConforme`.
    """

    def __init__(self) -> None:
        self._tampon = ""
        self._dans_appel = False

    def lire(self, morceau: str) -> list[Evenement]:
        self._tampon += morceau
        sortie: list[Evenement] = []
        while True:
            if self._dans_appel:
                fin = self._tampon.find(BALISE_FERMANTE)
                if fin < 0:
                    return sortie
                sortie.append(_appel_balise(self._tampon[:fin].strip()))
                self._tampon = self._tampon[fin + len(BALISE_FERMANTE) :]
                self._dans_appel = False
                continue
            debut = self._tampon.find(BALISE_OUVRANTE)
            if debut >= 0:
                if debut:
                    sortie.append(Jeton(texte=self._tampon[:debut]))
                self._tampon = self._tampon[debut + len(BALISE_OUVRANTE) :]
                self._dans_appel = True
                continue
            garde = _prefixe_en_attente(self._tampon, BALISE_OUVRANTE)
            emis = self._tampon[: len(self._tampon) - garde]
            if emis:
                sortie.append(Jeton(texte=emis))
            self._tampon = self._tampon[len(emis) :]
            return sortie

    def finir(self) -> list[Evenement]:
        reste, self._tampon = self._tampon, ""
        if self._dans_appel:
            self._dans_appel = False
            return [_appel_balise(reste.strip(), fermee=False)]
        return [Jeton(texte=reste)] if reste else []


def messages_balises(messages: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Messages où les `tool_calls` d'un tour `assistant` sont réécrits en balises.

    Le template de SmolLM3 ignore `tool_calls` : sans réécriture, l'appel disparaîtrait de
    l'historique rendu. Chaque appel devient `<tool_call>\n{"name", "arguments"}\n</tool_call>`
    (le format que le template prescrit au modèle), ajouté au `content`.
    """
    resultat: list[dict[str, Any]] = []
    for message in messages:
        copie = dict(message)
        appels = copie.get("tool_calls")
        if copie.get("role") == "assistant" and appels:
            blocs = []
            for appel in appels:
                fonction = appel.get("function") or {}
                arguments = fonction.get("arguments")
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        pass
                objet = json.dumps(
                    {"name": fonction.get("name"), "arguments": arguments}, ensure_ascii=False
                )
                blocs.append(f"{BALISE_OUVRANTE}\n{objet}\n{BALISE_FERMANTE}")
            contenu = copie.get("content") or ""
            copie["content"] = "\n".join(([contenu] if contenu else []) + blocs)
            del copie["tool_calls"]
        resultat.append(copie)
    return resultat


class ClientLlama:
    """`LlmPort` d'un `llama-server` de génération sur `127.0.0.1:<port>`.

    `taille_contexte` (tokens, `None` si inconnue) est la taille du contexte du serveur ;
    le Harnais la lit pour découper les comptes rendus longs (story 4.4). Ce n'est pas un
    membre de `LlmPort` : un port sans cet attribut est traité en un seul appel.
    """

    def __init__(
        self,
        port: int,
        *,
        protocole_outils: str = "natif",
        chat_template_kwargs: Mapping[str, Any] | None = None,
        taille_contexte: int | None = None,
        transport_interne: Any = None,
    ) -> None:
        if protocole_outils not in PROTOCOLES:
            raise ValueError(
                f"protocole d'outils inconnu : {protocole_outils!r} "
                f"(attendu : {', '.join(PROTOCOLES)})"
            )
        self.port = port
        self.protocole_outils = protocole_outils
        self.chat_template_kwargs = dict(chat_template_kwargs or {})
        self.taille_contexte = taille_contexte
        self._http = client_local(port, transport_interne=transport_interne)
        self._base = f"http://127.0.0.1:{port}"

    def fermer(self) -> None:
        self._http.close()

    def __enter__(self) -> ClientLlama:
        return self

    def __exit__(self, *exc: object) -> None:
        self.fermer()

    # -- Requêtes --

    def _post(self, chemin: str, corps: Mapping[str, Any]) -> Any:
        reponse = self._http.post(self._base + chemin, json=corps)
        if reponse.status_code != 200:
            raise ErreurInference(
                f"POST {chemin} : HTTP {reponse.status_code} : {reponse.text[:TAILLE_EXTRAIT]}"
            )
        return reponse.json()

    def _messages(self, messages: Sequence[Mapping[str, Any]]) -> list[Any]:
        if self.protocole_outils == "balises-tool-call":
            return messages_balises(messages)
        return list(messages)

    def _kwargs_template(self, options: Mapping[str, Any]) -> dict[str, Any]:
        return {**self.chat_template_kwargs, **(options.get("chat_template_kwargs") or {})}

    def compter_tokens(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None = None,
    ) -> int:
        """Tokens de l'entrée rendue par le chat template (`/apply-template`, `/tokenize`).

        Avec `json-generique`, `tools` n'est pas rendu par le template ; avec
        `balises-tool-call`, les `tool_calls` de l'historique sont réécrits (comme dans
        `generer`).
        """
        corps: dict[str, Any] = {"messages": self._messages(messages)}
        if tools and self.protocole_outils != "json-generique":
            corps["tools"] = list(tools)
        kwargs = self._kwargs_template({})
        if kwargs:
            corps["chat_template_kwargs"] = kwargs
        prompt = self._post("/apply-template", corps).get("prompt")
        if not isinstance(prompt, str):
            raise ErreurInference("/apply-template : champ `prompt` absent")
        tokens = self._post("/tokenize", {"content": prompt}).get("tokens")
        if not isinstance(tokens, list):
            raise ErreurInference("/tokenize : champ `tokens` absent")
        return len(tokens)

    def corps_generation(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Corps JSON de `/v1/chat/completions` ; lève `ValueError` pour une option inconnue."""
        options = dict(options or {})
        inconnues = sorted(set(options) - OPTIONS_AUTORISEES)
        if inconnues:
            raise ValueError(
                f"options inconnues : {', '.join(inconnues)} "
                f"(permises : {', '.join(sorted(OPTIONS_AUTORISEES))})"
            )
        corps: dict[str, Any] = {
            "messages": self._messages(messages),
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        for cle, valeur in options.items():
            if cle != "chat_template_kwargs":
                corps[cle] = valeur
        kwargs = self._kwargs_template(options)
        if kwargs:
            corps["chat_template_kwargs"] = kwargs
        if tools:
            if self.protocole_outils != "json-generique":
                corps["tools"] = list(tools)
            else:
                corps["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "reponse",
                        "strict": True,
                        "schema": schema_json_generique(tools),
                    },
                }
        return corps

    def generer(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Iterator[Evenement]:
        """Génère en flux : `Jeton`, `AppelOutil`/`AppelNonConforme`, puis un seul `Fin`.

        Les options sont vérifiées avant l'itération (`ValueError`). Un statut HTTP autre
        que 200 lève `ErreurInference` (statut et extrait du corps).
        """
        corps = self.corps_generation(messages, tools=tools, options=options)
        json_generique = bool(tools) and self.protocole_outils == "json-generique"
        balises = LecteurBalises() if self.protocole_outils == "balises-tool-call" else None
        return self._flux(corps, json_generique, balises)

    def _lignes(self, reponse: Any) -> Iterator[str]:
        """Lignes du flux ; une coupure de transport termine simplement l'itération."""
        lignes = reponse.iter_lines()
        while True:
            try:
                ligne = next(lignes)
            except StopIteration:
                return
            except Exception:  # connexion coupée ou délai dépassé : flux interrompu
                return
            yield ligne

    def _flux(
        self, corps: dict[str, Any], json_generique: bool, balises: LecteurBalises | None = None
    ) -> Iterator[Evenement]:
        debut = time.perf_counter()
        premier: float | None = None
        texte_json: list[str] = []
        appels: dict[int, dict[str, Any]] = {}
        raison_finale: str | None = None
        termine = False
        usage: dict[str, int] = {}

        with self._http.stream("POST", self._base + "/v1/chat/completions", json=corps) as reponse:
            if reponse.status_code != 200:
                reponse.read()
                raise ErreurInference(
                    f"POST /v1/chat/completions : HTTP {reponse.status_code} : "
                    f"{reponse.text[:TAILLE_EXTRAIT]}"
                )
            for ligne in self._lignes(reponse):
                if not ligne.startswith("data:"):
                    continue
                donnees = ligne[5:].strip()
                if donnees == "[DONE]":
                    termine = True
                    break
                try:
                    morceau = json.loads(donnees)
                except json.JSONDecodeError:
                    continue
                if not isinstance(morceau, dict):
                    continue
                if "error" in morceau:
                    raise ErreurInference(
                        f"/v1/chat/completions : erreur en flux : "
                        f"{json.dumps(morceau['error'], ensure_ascii=False)[:TAILLE_EXTRAIT]}"
                    )
                if isinstance(morceau.get("usage"), dict):
                    usage = {
                        cle: int(morceau["usage"][cle])
                        for cle in CLES_USAGE
                        if isinstance(morceau["usage"].get(cle), int)
                    }
                for choix in morceau.get("choices") or []:
                    delta = choix.get("delta") or {}
                    raisonnement = delta.get("reasoning_content")
                    if isinstance(raisonnement, str) and raisonnement and premier is None:
                        premier = time.perf_counter()  # raisonnement : compté, jamais émis
                    contenu = delta.get("content")
                    if isinstance(contenu, str) and contenu:
                        if premier is None:
                            premier = time.perf_counter()
                        if json_generique:
                            texte_json.append(contenu)
                        elif balises is not None:
                            yield from balises.lire(contenu)
                        else:
                            yield Jeton(texte=contenu)
                    for fragment in delta.get("tool_calls") or []:
                        if premier is None:
                            premier = time.perf_counter()
                        index = fragment.get("index", 0)
                        cumul = appels.setdefault(index, {"id": None, "nom": "", "arguments": ""})
                        if fragment.get("id"):
                            cumul["id"] = fragment["id"]
                        fonction = fragment.get("function") or {}
                        if fonction.get("name") and not cumul["nom"]:
                            cumul["nom"] = fonction["name"]
                        if isinstance(fonction.get("arguments"), str):
                            cumul["arguments"] += fonction["arguments"]
                    if choix.get("finish_reason"):
                        raison_finale = choix["finish_reason"]

        if json_generique:
            yield from _sortie_json_generique("".join(texte_json))
        if balises is not None:
            yield from balises.finir()
        for index in sorted(appels):
            yield _appel_natif(appels[index])

        if raison_finale == "length":
            raison = "longueur"
        elif raison_finale is not None or termine:
            raison = "terminee"
        else:
            raison = "interrompue"
        if premier is not None:
            usage["delai_premier_token_ms"] = round((premier - debut) * 1000)
        yield Fin(raison=raison, usage=usage or None)


__all__ = [
    "ClientLlama",
    "LecteurBalises",
    "OPTIONS_AUTORISEES",
    "PROTOCOLES",
    "appel_canonique",
    "messages_balises",
    "schema_json_generique",
]
