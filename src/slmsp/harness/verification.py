"""Vérification en ligne d'une page officielle (FR-12, story 13.5, Q7).

`verifier(reponse, sources, passerelle, llm)` contrôle une réponse déjà produite sur
la page officielle qu'elle cite :

1. Choix de la page : la source de l'Index local la mieux classée (plus petit `numero`)
   parmi celles que la réponse cite par un renvoi `[n]` et, si `dans_index` est fourni, dont
   l'URL figure réellement dans l'Index (les sources viennent de l'appelant). La requête et
   le fragment de l'URL sont retirés avant l'envoi. Aucune recherche sur le site :
   la seule Requête sortante est un GET de cette URL, déjà citée. Ni la question, ni la
   réponse, ni aucun texte saisi ne sortent du poste (FR-38).
2. Récupération par la passerelle unique (AD-4) : profil `assistant` (Liste blanche par
   correspondance exacte, HTTPS), GET seul, redirections suivies mais chaque saut
   recontrôlé (une redirection hors Liste blanche est bloquée, `MAX_REDIRECTIONS` au plus),
   délai et taille bornés, sans relance. Le Mode est toujours celui de la passerelle :
   l'appelant ne peut pas le remplacer, et le Mode hors ligne (forcé ou détecté) refuse la
   requête avant toute connexion (`bloquee-mode`). L'entrée du journal porte
   `outil = "verification-page"` et
   `termes = {"url": <url>}`.
3. Extraction du texte principal par `html.parser` de la bibliothèque standard : rien
   n'est exécuté ; scripts, styles et éléments non textuels sont ignorés ; le contenu de
   `<main>` ou `<article>` est préféré s'il existe.
4. Comparaison locale par le Modèle embarqué, avec le prompt `config/prompts/taches/VE.md`
   (consignes seulement, D1.1). La réponse et la page sont encadrées par des délimiteurs,
   neutralisés dans leur contenu ; la page est une donnée, jamais une instruction. La phrase
   affichée est un libellé fixe dérivé du verdict, jamais le texte libre du modèle.

Le résultat est une liste d'évènements : un `Verification` (toujours), suivi d'un
`Sources` portant la page consultée quand elle a été récupérée.
"""

from __future__ import annotations

import re
import time
import unicodedata
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, Literal
from urllib.parse import urlsplit, urlunsplit

from pydantic import ValidationError

from slmsp.core.canonique import json_canonique
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import HoteBloque
from slmsp.core.evenements import Evenement, Jeton, Source, Sources, Verification
from slmsp.core.gabarits import GabaritInvalide, valider_gabarit
from slmsp.core.ports import JournalRequetes, LlmPort
from slmsp.harness.citations import numeros_cites
from slmsp.harness.config import ConfigVerification
from slmsp.harness.prompts import construire_messages
from slmsp.harness.taches import PromptTache, Tache
from slmsp.net.client import Passerelle, client

OUTIL_JOURNAL: Final = "verification-page"
"""Valeur de `outil` dans le journal des Requêtes sortantes."""

NOM_PROMPT: Final = "VE.md"
TYPES_HTML: Final = ("text/html", "application/xhtml+xml")

MAX_REDIRECTIONS: Final = 3
REPONSE_MAX_CARACTERES: Final = 20_000
"""Taille maximale de la réponse à vérifier (au-delà : `indisponible`, ou refus du pont)."""
PHRASE_MAX_CARACTERES: Final = 300
EXTRAIT_MIN_CARACTERES: Final = 12
EXTRAIT_MAX_CARACTERES: Final = 500
DEBUT_REPONSE: Final = "<<<REPONSE>>>"
FIN_REPONSE: Final = "<<<FIN_REPONSE>>>"
DEBUT_PAGE: Final = "<<<PAGE>>>"
FIN_PAGE: Final = "<<<FIN_PAGE>>>"
_RE_DELIMITEUR = re.compile(r"<{3,}|>{3,}")

Verdict = Literal["concordant", "difference", "indisponible"]

PHRASES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "desactivee": "La vérification en ligne est désactivée.",
        "sans-source": "Aucune page officielle citée ne peut être vérifiée.",
        "bloquee": "La page officielle ne peut pas être consultée depuis ce poste.",
        "echec": "La page officielle n'a pas répondu.",
        "statut": "La page officielle n'est pas accessible pour le moment.",
        "format": "La page officielle n'est pas une page web lisible.",
        "taille": "La page officielle est trop volumineuse pour être vérifiée.",
        "vide": "Le texte de la page officielle n'a pas pu être lu.",
        "comparaison": "La comparaison avec la page officielle n'a pas abouti.",
        "reponse": "La réponse est trop longue pour être vérifiée.",
        "concordant": "La page officielle confirme la réponse.",
        "difference": "La page officielle diffère de la réponse.",
    }
)


class _Indisponible(Exception):
    """Arrêt de la vérification avec le verdict `indisponible` ; `cle` indexe `PHRASES`."""

    def __init__(self, cle: str) -> None:
        super().__init__(cle)
        self.cle = cle


# --- Choix de la page --------------------------------------------------------------------


def _vers_source(brute: Source | Mapping[str, Any]) -> Source | None:
    if isinstance(brute, Source):
        return brute
    if not isinstance(brute, Mapping):
        return None
    try:
        return Source.model_validate(dict(brute))
    except ValidationError:
        return None


def url_sans_requete(url: str) -> str | None:
    """`url` sans requête (`?…`), fragment (`#…`) ni identifiants ; `None` si illisible."""
    try:
        morceaux = urlsplit(url)
        hote = morceaux.hostname
        port = morceaux.port
    except ValueError:
        return None
    if not morceaux.scheme or not hote:
        return None
    if ":" in hote:  # IPv6
        hote = f"[{hote}]"
    netloc = hote if port is None else f"{hote}:{port}"
    return urlunsplit((morceaux.scheme, netloc, morceaux.path, "", ""))


def _admise(url: str, dans_index: Callable[[str], bool] | None) -> bool:
    if dans_index is None:
        return True
    try:
        return bool(dans_index(url))
    except Exception:  # Index illisible : dans le doute, la source n'est pas vérifiée
        return False


def choisir_source(
    reponse: str,
    sources: Sequence[Source | Mapping[str, Any]],
    dans_index: Callable[[str], bool] | None = None,
) -> Source | None:
    """Source de l'Index la mieux classée (plus petit `numero`) que `reponse` cite par `[n]`.

    Les sources illisibles, sans `numero`, d'une autre origine ou, si `dans_index` est
    fourni, dont l'URL est absente de l'Index sont ignorées. L'URL rendue est sans requête
    ni fragment. `None` si aucune ne convient. La Liste blanche n'est pas contrôlée ici :
    la passerelle le fait.
    """
    candidates = []
    for brute in sources:
        s = _vers_source(brute)
        if s is None or s.origine != "index" or s.numero is None:
            continue
        nette = url_sans_requete(s.url)
        if nette is None or not _admise(s.url, dans_index):
            continue
        candidates.append(s.model_copy(update={"url": nette}))
    if not candidates or not isinstance(reponse, str):
        return None
    cites = set(numeros_cites(reponse, max(s.numero or 0 for s in candidates)))
    retenues = [s for s in candidates if s.numero in cites]
    return min(retenues, key=lambda s: s.numero or 0) if retenues else None


# --- Journal étiqueté --------------------------------------------------------------------


@dataclass(frozen=True)
class _JournalEtiquete:
    """Journal qui porte `outil` et `termes` sur chaque entrée de la vérification."""

    interne: JournalRequetes
    termes: str

    def inscrire(self, entree: Any) -> None:
        self.interne.inscrire(
            entree.model_copy(update={"outil": OUTIL_JOURNAL, "termes": self.termes})
        )

    def lister(self, limite: int | None = None) -> list[Any]:
        return self.interne.lister(limite)


# --- Extraction du texte -----------------------------------------------------------------

_IGNORES: Final = frozenset(
    {"script", "style", "noscript", "template", "svg", "math", "iframe", "object", "head"}
)
_PRINCIPAUX: Final = frozenset({"main", "article"})
_BLOCS: Final = frozenset(
    {
        "address", "article", "aside", "blockquote", "br", "dd", "div", "dl", "dt",
        "figcaption", "footer", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr", "li",
        "main", "nav", "ol", "p", "pre", "section", "table", "td", "th", "tr", "ul",
    }
)  # fmt: skip
_VIDES: Final = frozenset({"br", "hr", "img", "input", "meta", "link", "wbr", "source"})
_RE_ESPACES = re.compile(r"[ \t\f\v ]+")


class _Extracteur(HTMLParser):
    """Collecte le titre et le texte visible ; ne suit et n'exécute rien."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.titre: list[str] = []
        self.tout: list[str] = []
        self.principal: list[str] = []
        self._pile: list[str] = []
        self._ignore = 0
        self._dans_titre = False
        self._principal = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _VIDES:
            if tag in _BLOCS:
                self._ecrire("\n")
            return
        if tag == "title":
            self._dans_titre = True
        self._pile.append(tag)
        if tag in _IGNORES:
            self._ignore += 1
        if tag in _PRINCIPAUX:
            self._principal += 1
        if tag in _BLOCS:
            self._ecrire("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._dans_titre = False
        if tag not in self._pile:
            return
        while self._pile:  # balises non fermées : on dépile jusqu'à la balise fermée
            ouverte = self._pile.pop()
            if ouverte in _IGNORES:
                self._ignore -= 1
            if ouverte in _PRINCIPAUX:
                self._principal -= 1
            if ouverte == tag:
                break
        if tag in _BLOCS:
            self._ecrire("\n")

    def handle_data(self, data: str) -> None:
        if self._dans_titre:
            self.titre.append(data)
            return
        if self._ignore:
            return
        self._ecrire(data)

    def _ecrire(self, texte: str) -> None:
        if self._ignore:
            return
        self.tout.append(texte)
        if self._principal:
            self.principal.append(texte)


def _normaliser(morceaux: Sequence[str]) -> str:
    lignes = (_RE_ESPACES.sub(" ", ligne).strip() for ligne in "".join(morceaux).splitlines())
    return "\n".join(ligne for ligne in lignes if ligne)


@dataclass(frozen=True)
class PageExtraite:
    """Titre (vide s'il est absent) et texte principal d'une page HTML."""

    titre: str
    texte: str


def extraire_texte(html: str) -> PageExtraite:
    """Titre et texte principal de `html` (contenu de `<main>`/`<article>` s'il existe)."""
    extracteur = _Extracteur()
    try:
        extracteur.feed(html)
        extracteur.close()
    except Exception:  # pragma: no cover - html.parser est tolérant ; garde-fou
        pass
    principal = _normaliser(extracteur.principal)
    texte = principal or _normaliser(extracteur.tout)
    titre = _RE_ESPACES.sub(" ", " ".join("".join(extracteur.titre).split())).strip()
    return PageExtraite(titre, texte)


# --- Récupération ------------------------------------------------------------------------

_RE_CHARSET = re.compile(r"charset\s*=\s*[\"']?([A-Za-z0-9._:-]+)", re.IGNORECASE)


def _decoder(contenu: bytes, type_contenu: str) -> str:
    trouve = _RE_CHARSET.search(type_contenu)
    encodage = trouve.group(1) if trouve else "utf-8"
    try:
        return contenu.decode(encodage, errors="replace")
    except LookupError:
        return contenu.decode("utf-8", errors="replace")


def _recuperer(
    url: str,
    passerelle: Passerelle,
    config: ConfigVerification,
    transport_interne: Any,
) -> str:
    """Texte HTML de `url` ; lève `_Indisponible` sinon."""
    if passerelle.mode is None:  # le profil assistant exige un Mode : rien ne sort
        raise _Indisponible("bloquee")
    journal = _JournalEtiquete(passerelle.journal, json_canonique({"url": url}).decode("utf-8"))
    debut = time.monotonic()
    try:
        with client(
            "assistant",
            passerelle.lib,
            False,
            passerelle.mode,
            journal,
            transport_interne,
            config=passerelle.config,
            liste_blanche=passerelle.liste_blanche,
            follow_redirects=True,
        ) as http:
            http.max_redirects = MAX_REDIRECTIONS
            with http.stream(
                "GET", url, timeout=config.delai_s, headers={"Accept-Encoding": "identity"}
            ) as reponse:
                if reponse.status_code != 200:
                    raise _Indisponible("statut")
                type_contenu = reponse.headers.get("content-type", "")
                if type_contenu.split(";", 1)[0].strip().lower() not in TYPES_HTML:
                    raise _Indisponible("format")
                annonce = reponse.headers.get("content-length", "")
                if annonce.isdigit() and int(annonce) > config.taille_max_octets:
                    raise _Indisponible("taille")
                morceaux: list[bytes] = []
                taille = 0
                for morceau in reponse.iter_bytes():
                    taille += len(morceau)
                    if taille > config.taille_max_octets:
                        raise _Indisponible("taille")
                    if time.monotonic() - debut > config.delai_s:
                        raise _Indisponible("echec")
                    morceaux.append(morceau)
    except _Indisponible:
        raise
    except HoteBloque:
        raise _Indisponible("bloquee") from None
    except Exception:  # délai, connexion, protocole : aucune relance
        raise _Indisponible("echec") from None
    return _decoder(b"".join(morceaux), type_contenu)


# --- Comparaison -------------------------------------------------------------------------


def charger_prompt(chemin: str | Path | None = None) -> Tache:
    """Tâche interne « VE » portant le prompt validé `VE.md` (lève `GabaritInvalide`)."""
    fichier = (
        Path(chemin)
        if chemin is not None
        else racine_projet() / "config" / "prompts" / "taches" / NOM_PROMPT
    )
    gabarit = valider_gabarit(fichier)
    prompt = PromptTache(
        id=gabarit.id,
        version=gabarit.version,
        tache="VE",
        consigne=gabarit.consigne,
        emplacements=tuple(gabarit.emplacements),
        sha256=gabarit.sha256,
    )
    return Tache(code="VE", libelle="Vérification en ligne", actif=True, prompt=prompt)


def _sans_accent(texte: str) -> str:
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c))


def _compacter(texte: str) -> str:
    return " ".join(texte.split()).casefold()


def encadrer(texte: str, debut: str, fin: str) -> str:
    """`texte` entre `debut` et `fin`, après neutralisation de tout `<<<`/`>>>` qu'il contient."""
    return f"{debut}\n{_RE_DELIMITEUR.sub(' ', texte).strip()}\n{fin}"


@dataclass(frozen=True)
class Comparaison:
    """Verdict lu dans la sortie du Modèle embarqué."""

    verdict: Verdict
    phrase: str | None
    extrait: str | None


def lire_comparaison(sortie: str, texte_page: str) -> Comparaison:
    """Analyse la sortie du modèle (mot-clé, phrase, passage différent).

    Un mot-clé absent ou inconnu donne `indisponible`. Le passage n'est retenu que s'il
    figure dans le texte de la page (espaces et casse ignorés) : jamais d'extrait inventé.
    """
    lignes = [ligne.strip() for ligne in sortie.splitlines() if ligne.strip()]
    if not lignes:
        return Comparaison("indisponible", None, None)
    mot = _sans_accent(lignes[0]).strip(" *_#.:").upper()
    if mot.startswith("CONCORDANT"):
        verdict: Verdict = "concordant"
    elif mot.startswith("DIFFERENCE"):
        verdict = "difference"
    else:
        return Comparaison("indisponible", None, None)
    phrase = lignes[1] if len(lignes) > 1 else None
    if phrase is not None and len(phrase) > PHRASE_MAX_CARACTERES:
        phrase = None
    extrait = None
    if verdict == "difference" and len(lignes) > 2:
        candidat = lignes[2].strip(" «»\"'")
        if EXTRAIT_MIN_CARACTERES <= len(candidat) <= EXTRAIT_MAX_CARACTERES and _compacter(
            candidat
        ) in _compacter(texte_page):
            extrait = candidat
    return Comparaison(verdict, phrase, extrait)


def _comparer(
    reponse: str, texte_page: str, llm: LlmPort, tache: Tache, config: ConfigVerification
) -> Comparaison:
    messages = construire_messages(
        tache,
        {
            "texte": encadrer(reponse, DEBUT_REPONSE, FIN_REPONSE),
            "document": encadrer(texte_page[: config.caracteres_max_page], DEBUT_PAGE, FIN_PAGE),
        },
    )
    options = {"temperature": 0.0, "max_tokens": config.max_tokens}
    try:
        sortie = "".join(
            e.texte for e in llm.generer(messages, options=options) if isinstance(e, Jeton)
        )
    except Exception:
        raise _Indisponible("comparaison") from None
    return lire_comparaison(sortie, texte_page)


# --- Point d'entrée ----------------------------------------------------------------------


def verifier(
    reponse: str,
    sources: Sequence[Source | Mapping[str, Any]],
    passerelle: Passerelle,
    llm: LlmPort,
    *,
    dans_index: Callable[[str], bool] | None = None,
    config: ConfigVerification | None = None,
    tache: Tache | None = None,
    horloge: Callable[[], datetime] | None = None,
    transport_interne: Any = None,
) -> list[Evenement]:
    """Vérifie `reponse` sur la page officielle citée ; voir le docstring du module.

    Le Mode est celui de la passerelle, sans dérogation possible. `dans_index(url)` dit si
    une URL figure dans l'Index local (par ex. `IndexLocal.contient_url`) ; sans lui, les
    sources de l'appelant ne sont pas recoupées. `tache` porte le prompt `VE.md` (chargé
    par défaut). Ne lève pas : toute impossibilité donne `indisponible`.
    """
    config = config if config is not None else ConfigVerification()
    maintenant = (horloge or (lambda: datetime.now(UTC)))()
    date = maintenant.astimezone(UTC).isoformat(timespec="seconds")
    trop_longue = not isinstance(reponse, str) or len(reponse) > REPONSE_MAX_CARACTERES
    source = None if trop_longue else choisir_source(reponse, sources, dans_index)

    def indisponible(cle: str) -> list[Evenement]:
        return [
            Verification(
                url=source.url if source else None,
                titre=source.titre if source else None,
                date_consultation=date,
                verdict="indisponible",
                phrase=PHRASES[cle],
            )
        ]

    if not config.active:
        return indisponible("desactivee")
    if trop_longue:
        return indisponible("reponse")
    if source is None:
        return indisponible("sans-source")
    try:
        try:
            tache = tache if tache is not None else charger_prompt()
        except GabaritInvalide:
            raise _Indisponible("comparaison") from None
        html = _recuperer(source.url, passerelle, config, transport_interne)
        page = extraire_texte(html)
        if not page.texte:
            raise _Indisponible("vide")
        comparaison = _comparer(reponse, page.texte, llm, tache, config)
    except _Indisponible as exc:
        return indisponible(exc.cle)
    titre = page.titre or source.titre
    if comparaison.verdict == "indisponible":
        return indisponible("comparaison")
    return [
        Verification(
            url=source.url,
            titre=titre,
            date_consultation=date,
            verdict=comparaison.verdict,
            phrase=PHRASES[comparaison.verdict],  # libellé fixe : jamais le texte du modèle
            extrait=comparaison.extrait,
        ),
        Sources(
            sources=[
                Source(
                    titre=titre,
                    url=source.url,
                    origine="verification",
                    date=date,
                    extrait=comparaison.extrait,
                )
            ]
        ),
    ]


@dataclass(frozen=True)
class Verificateur:
    """`verifier` lié à ses dépendances : ce que le pont (story 13.6) appelle.

    `verificateur(reponse, sources)` rend la liste d'évènements de `verifier`.
    """

    passerelle: Passerelle
    llm: LlmPort
    dans_index: Callable[[str], bool] | None = None
    config: ConfigVerification | None = None

    def __call__(
        self, reponse: str, sources: Sequence[Source | Mapping[str, Any]]
    ) -> list[Evenement]:
        return verifier(
            reponse,
            sources,
            self.passerelle,
            self.llm,
            dans_index=self.dans_index,
            config=self.config,
        )


__all__ = [
    "MAX_REDIRECTIONS",
    "OUTIL_JOURNAL",
    "PHRASES",
    "REPONSE_MAX_CARACTERES",
    "Comparaison",
    "PageExtraite",
    "Verificateur",
    "charger_prompt",
    "choisir_source",
    "encadrer",
    "extraire_texte",
    "lire_comparaison",
    "url_sans_requete",
    "verifier",
]
