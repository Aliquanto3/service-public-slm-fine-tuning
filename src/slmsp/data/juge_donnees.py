"""Juge de données : notation des candidats d'entraînement par DeepSeek (story O1).

Le juge de données note une cible candidate (réponse Mistral journalisée ; plus tard, sortie
locale) contre la **source** de sa session, selon la grille de données de la Tâche
(`config/prompts/juge-donnees/<tache>.md`, SHA consigné). Le Juge du test (Claude)
n'intervient jamais, et rien n'est lu sous `eval/` : toutes les lectures passent par
`core.artefacts.lire` (lecteur `data`).

Règles :

- **D1** : la sortie est structurée (notes, listes, motifs courts, extraits) ; le schéma
  n'a aucun champ de réponse réécrite, et un champ inconnu est refusé. Les extraits sont des
  citations contrôlées comme sous-chaînes du candidat ou de la source après normalisation
  (espaces, espaces insécables, apostrophes et guillemets typographiques, casse inchangée) ;
  un extrait non retrouvé est retiré et compté (`extraits_invalides`).
- **Couches** : seuls `slmsp.fournisseurs.client`, `.journal` et `.lecture` sont utilisés
  (`data` n'importe pas `slmsp.judge`, AD-1).
- **Verdict** recalculé par le code avec les seuils `[juge_donnees.seuils.<TACHE>]` (note
  `>=` seuil) ; celui du modèle (`verdict_modele`) n'est qu'informatif. CR : `couverture` =
  rappel des décisions et actions (partielle = 1/2 ; 0 et motif `couverture-non-evaluable`
  si le juge n'en extrait aucune). Une sortie non conforme après une relance corrective donne
  `invalide` (ni accepté, ni mis en cache) ; une sortie interrompue (`finish_reason` de
  longueur) donne `non-juge`.
- **Cache** par empreinte `sha256(modèle, effort, version du prompt, SHA de la grille,
  schéma et critères, source, candidat)`, indexé sur les lignes `verdicts.jsonl` des runs
  `data-*` existants (`indexer_cache`) : un verdict connu n'est ni redemandé ni réservé, et
  son verdict est recalculé avec les seuils courants.

Contrat de bibliothèque (réutilisé par O6) : `JugeDonnees.juger_candidat(tache, source,
candidat) -> VerdictDonnees`, sans écriture de run (l'appelant écrit `VerdictDonnees.ligne()`).
`BudgetEpuise` et `ErreurApiFournisseur` sont propagées à l'appelant.

`lancer_jugement` produit `runs/data-juger/<run_id>/` : `verdicts.jsonl` (une ligne par
candidat jugé), `bilan.jsonl` (une ligne par invocation), `rapport.json` (run `complet`
seulement) ; statut `complet`, `partiel-budget` (`BudgetEpuise`, reprise par
`reprendre_run_id`), `partiel-erreur` (erreur d'API, candidats non jugés) ou `interrompu`.
Une sortie interrompue est consignée dans `interruptions.jsonl` ; après `INTERRUPTIONS_MAX`
interruptions, le candidat n'est plus redemandé à la reprise (`interrompu-plafond`).
"""

from __future__ import annotations

import dataclasses
import json
import math
import re
import threading
import unicodedata
from collections import Counter, deque
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, StrictInt, ValidationError

from slmsp.budget.tarifs import cout_estime, cout_pire_cas
from slmsp.core.artefacts import Run, lire, nouveau_run, ouvrir_run, reprendre
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import BudgetEpuise, ManifesteInvalide, SlmspError
from slmsp.data.config import CRITERES_JUGE_DONNEES, JugeDonneesConfig
from slmsp.fournisseurs.client import (
    MODE,
    OPENROUTER,
    ClientCompatibleOpenAI,
    ConfigFournisseur,
    ErreurApiFournisseur,
    nouvelle_session,
)
from slmsp.fournisseurs.lecture import extraire_json

__all__ = [
    "source_session",
    "TACHES_JUGEES",
    "TYPE_RUN",
    "Candidat",
    "EstimationJuge",
    "FileOrdonnee",
    "GrilleDonnees",
    "JugementAnnule",
    "JugeDonnees",
    "PlafondEstimeDepasse",
    "ResultatJugementDonnees",
    "VerdictDonnees",
    "candidats_depuis_generation",
    "charger_grilles",
    "config_openrouter",
    "indexer_cache",
    "juger_en_parallele",
    "lancer_jugement",
    "normaliser_extrait",
    "schema_sortie",
]

TYPE_RUN: Final = "data-juger"
NOM_VERDICTS: Final = "verdicts.jsonl"
NOM_BILAN: Final = "bilan.jsonl"
NOM_RAPPORT: Final = "rapport.json"
NOM_INTERRUPTIONS: Final = "interruptions.jsonl"
INTERRUPTIONS_MAX: Final = 2
"""Au-delà, un candidat toujours interrompu n'est plus redemandé à la reprise (plafond)."""
MOTIF_PLAFOND_INTERRUPTIONS: Final = "interrompu-plafond"
LONGUEUR_EXTRAIT_MIN: Final = 5
"""Longueur minimale (normalisée) d'un extrait : une citation triviale (« le ») est rejetée."""
MOTIF_COUVERTURE_NON_EVALUABLE: Final = "couverture-non-evaluable"
VERSION_PROMPT: Final = 2
"""Version du cadre du prompt (placement de la source et du candidat), dans la clé du cache.
v2 : source et candidat entre balises à identifiant dérivé de leur contenu (revue O1)."""
TACHES_JUGEES: Final = ("CR", "LC", "CT")
"""Tâches de l'étage 1 (RE et CO : option étage 2)."""
DOSSIER_GRILLES: Final = Path("config") / "prompts" / "juge-donnees"
PREFIXE_SESSION: Final = "juge-donnees-"
NOM_SCHEMA: Final = "verdict_donnees"
LONGUEUR_MOTIF: Final = 300
CARACTERES_PAR_TOKEN: Final = 3
MARGE_TOKENS: Final = 100
TENTATIVES_MAX: Final = 2
"""Une sortie non conforme est redemandée une fois (relance corrective qui rappelle l'écart),
puis le verdict est `invalide`."""
RELANCE_CORRECTIVE: Final = (
    "Ta sortie précédente n'est pas conforme : {ecart}. Rends uniquement l'objet JSON complet "
    "demandé, avec tous les critères et toutes les listes du schéma, sans autre texte."
)
"""Consigne d'outillage de la relance (aucune réponse ni exemple, D1) ; `ecart` est le motif
produit par le code (`SortieNonConforme`), jamais un extrait de texte."""
FINS_INTERROMPUES: Final = frozenset({"length", "max_tokens", "model_length"})
MOTIF_INTERROMPUE: Final = "sortie-interrompue"
LISTES_PAR_TACHE: Final[dict[str, tuple[str, ...]]] = {
    "CR": ("decisions", "actions"),
    "LC": ("ajouts",),
    "CT": (),
}
"""Listes de la sortie par Tâche : CR, éléments marqués ; LC, ajouts (chaînes)."""
LISTES_MARQUEES: Final = frozenset({"decisions", "actions"})

Verdict = Literal["accepte", "refuse", "invalide", "non-juge"]
"""`accepte`, `refuse` (seuils), `invalide` (sortie non conforme), `non-juge` (interrompue)."""


class PlafondEstimeDepasse(SlmspError):
    """Coût pire cas estimé au-dessus de `--plafond-estime` : aucun run, aucun appel."""


def config_openrouter(config: JugeDonneesConfig) -> ConfigFournisseur:
    """Fournisseur OpenRouter aux délais de `[juge_donnees]` (raisonnement long de DeepSeek)."""
    return dataclasses.replace(
        OPENROUTER,
        delai_lecture=config.delai_lecture,
        delai_appel=config.delai_appel,
        duree_totale_max_appel=config.duree_totale_max_appel,
    )


class SortieNonConforme(ValueError):
    """Sortie du juge illisible ou hors du schéma de la Tâche."""


# --- Schéma de sortie --------------------------------------------------------------------


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Critere(_Strict):
    note: StrictInt
    motif: str
    extraits: list[str]


class Element(_Strict):
    intitule: str
    statut: Literal["presente", "partielle", "absente"]


class Listes(_Strict):
    decisions: list[Element] | None = None
    actions: list[Element] | None = None
    ajouts: list[str] | None = None


class SortieJuge(_Strict):
    """Sortie du juge : aucun champ de texte réécrit (D1), champ inconnu refusé."""

    criteres: dict[str, Critere]
    listes: Listes
    verdict_modele: Literal["accepte", "refuse"]


def _objet(proprietes: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": dict(proprietes),
        "required": list(proprietes),
        "additionalProperties": False,
    }


def schema_sortie(tache: str) -> dict[str, Any]:
    """Schéma JSON strict de la sortie du juge pour `tache` (envoyé en `response_format`)."""
    critere = _objet(
        {
            "note": {"type": "integer"},
            "motif": {"type": "string"},
            "extraits": {"type": "array", "items": {"type": "string"}},
        }
    )
    element = _objet(
        {
            "intitule": {"type": "string"},
            "statut": {"type": "string", "enum": ["presente", "partielle", "absente"]},
        }
    )
    listes = {
        nom: {
            "type": "array",
            "items": element if nom in LISTES_MARQUEES else {"type": "string"},
        }
        for nom in LISTES_PAR_TACHE[tache]
    }
    return _objet(
        {
            "criteres": _objet({nom: critere for nom in CRITERES_JUGE_DONNEES[tache]}),
            "listes": _objet(listes),
            "verdict_modele": {"type": "string", "enum": ["accepte", "refuse"]},
        }
    )


def _lire_sortie(tache: str, texte: str) -> SortieJuge:
    """Sortie validée pour `tache` ; lève `SortieNonConforme`."""
    brut = extraire_json(texte)
    if brut is None:
        raise SortieNonConforme("aucun objet JSON dans la sortie")
    try:
        donnees = json.loads(brut)
        # Motif long : tronqué plutôt que refusé (information seule, jamais une cible).
        for critere in (donnees.get("criteres") or {}).values():
            if isinstance(critere, dict) and isinstance(critere.get("motif"), str):
                critere["motif"] = critere["motif"][:LONGUEUR_MOTIF]
        sortie = SortieJuge.model_validate(donnees)
    except (ValueError, AttributeError, ValidationError) as exc:
        raise SortieNonConforme(f"sortie hors schéma ({type(exc).__name__})") from None
    attendus = CRITERES_JUGE_DONNEES[tache]
    if set(sortie.criteres) != set(attendus):
        raise SortieNonConforme("critères différents de ceux de la Tâche")
    for nom, critere in sortie.criteres.items():
        if not 0 <= critere.note <= attendus[nom]:
            raise SortieNonConforme(f"note {nom} hors de [0, {attendus[nom]}]")
    if sortie.listes.model_fields_set != set(LISTES_PAR_TACHE[tache]) or any(
        getattr(sortie.listes, nom) is None for nom in LISTES_PAR_TACHE[tache]
    ):
        raise SortieNonConforme("listes différentes de celles de la Tâche")
    return sortie


# --- Extraits ----------------------------------------------------------------------------

_EQUIVALENTS: Final = str.maketrans(
    {
        " ": " ",
        " ": " ",
        " ": " ",
        " ": " ",
        "’": "'",
        "‘": "'",
        "ʼ": "'",
        "“": '"',
        "”": '"',
        "„": '"',
        "«": '"',
        "»": '"',
    }
)
_ESPACES: Final = re.compile(r"\s+")


def normaliser_extrait(texte: str) -> str:
    """Forme comparée des extraits : NFC, espaces et typographie unifiés, casse inchangée."""
    texte = unicodedata.normalize("NFC", texte).translate(_EQUIVALENTS)
    texte = re.sub(r'"\s+', '"', texte)
    texte = re.sub(r'\s+"', '"', texte)
    return _ESPACES.sub(" ", texte).strip()


def _filtrer_extraits(extraits: Iterable[str], *textes: str) -> tuple[list[str], int]:
    normes = [normaliser_extrait(t) for t in textes]
    gardes, rejetes = [], 0
    for extrait in extraits:
        norme = normaliser_extrait(extrait)
        if len(norme) >= LONGUEUR_EXTRAIT_MIN and any(norme in texte for texte in normes):
            gardes.append(extrait)
        else:
            rejetes += 1
    return gardes, rejetes


# --- Verdict -----------------------------------------------------------------------------


def _couverture(listes: Mapping[str, Any]) -> float:
    """Rappel des décisions et actions ; 0 (non évaluable, donc refus) si le juge n'en extrait
    aucune : un juge qui omet tout ne doit pas faire accepter le candidat."""
    elements = [*listes.get("decisions", []), *listes.get("actions", [])]
    if not elements:
        return 0.0
    poids = {"presente": 1.0, "partielle": 0.5}
    return sum(poids.get(e["statut"], 0.0) for e in elements) / len(elements)


def _notes(tache: str, criteres: Mapping[str, int], listes: Mapping[str, Any]) -> dict[str, float]:
    notes = {nom: float(note) for nom, note in criteres.items()}
    if tache == "CR":
        notes["couverture"] = _couverture(listes)
    return notes


def _decider(seuils: Mapping[str, float], notes: Mapping[str, float]) -> Verdict:
    return "accepte" if all(notes.get(c, 0.0) >= s for c, s in seuils.items()) else "refuse"


@dataclass(frozen=True)
class VerdictDonnees:
    """Verdict d'un candidat : notes, listes, motifs, extraits vérifiés, verdict recalculé."""

    tache: str
    cle: str
    verdict: Verdict
    notes: dict[str, float] = field(default_factory=dict)
    listes: dict[str, Any] = field(default_factory=dict)
    motifs: dict[str, str] = field(default_factory=dict)
    extraits: dict[str, list[str]] = field(default_factory=dict)
    extraits_invalides: int = 0
    verdict_modele: str | None = None
    cout_eur: float = 0.0
    depuis_cache: bool = False
    motif: str | None = None
    """Raison d'un verdict `invalide` ou `non-juge`."""
    appel_ids: tuple[str, ...] = ()
    """Appels du journal `appels-juge-donnees.sqlite` (vide si le verdict vient du cache)."""

    def ligne(self) -> dict[str, Any]:
        """Ligne JSON de `verdicts.jsonl` (sans `session_id` ni `candidat_id`, ajoutés par
        l'appelant)."""
        return {
            "tache": self.tache,
            "cle": self.cle,
            "verdict": self.verdict,
            "notes": self.notes,
            "listes": self.listes,
            "motifs": self.motifs,
            "extraits": self.extraits,
            "extraits_invalides": self.extraits_invalides,
            "verdict_modele": self.verdict_modele,
            "cout_eur": self.cout_eur,
            "depuis_cache": self.depuis_cache,
            "motif": self.motif,
            "appel_ids": list(self.appel_ids),
        }


# --- Grilles et cache --------------------------------------------------------------------


@dataclass(frozen=True)
class GrilleDonnees:
    """Grille de données d'une Tâche : texte (emplacements `{source}`, `{candidat}`) et SHA."""

    tache: str
    texte: str
    sha256: str


def charger_grilles(
    taches: Iterable[str] = TACHES_JUGEES, *, racine: str | Path | None = None
) -> dict[str, GrilleDonnees]:
    """Grilles `config/prompts/juge-donnees/<tache>.md` lues par `core.artefacts.lire`."""
    base = Path(racine) if racine is not None else racine_projet()
    grilles = {}
    for tache in taches:
        octets = lire(base / DOSSIER_GRILLES / f"{tache.lower()}.md", "data", racine=base)
        texte = octets.decode("utf-8")
        if "{source}" not in texte or "{candidat}" not in texte:
            raise SlmspError(f"grille {tache} : emplacements {{source}} et {{candidat}} requis")
        grilles[tache] = GrilleDonnees(tache, texte, sha256_hex(octets))
    return grilles


def indexer_cache(racine: str | Path) -> dict[str, dict[str, Any]]:
    """Index du cache : lignes jugées (`accepte`, `refuse`) des `verdicts.jsonl` des runs
    `data-*`, lues par `core.artefacts.lire` (aucune base SQLite, AD-24)."""
    base = Path(racine).resolve()
    index: dict[str, dict[str, Any]] = {}
    for chemin in sorted((base / "runs").glob(f"data-*/*/{NOM_VERDICTS}")):
        for brute in lire(chemin, "data", racine=base).split(b"\n"):
            try:
                ligne = json.loads(brute.decode("utf-8"))
            except (UnicodeDecodeError, ValueError):
                continue
            if (
                isinstance(ligne, dict)
                and ligne.get("verdict") in ("accepte", "refuse")
                and isinstance(ligne.get("cle"), str)
                and isinstance(ligne.get("notes"), dict)
            ):
                index[ligne["cle"]] = ligne
    return index


# --- Juge --------------------------------------------------------------------------------


@dataclass(frozen=True)
class EstimationJuge:
    """Coût estimé avant tout appel : cache à 0, doublons comptés une fois."""

    nb_candidats: int
    nb_en_cache: int
    nb_a_juger: int
    cout_estime_eur: float
    cout_pire_cas_eur: float


class JugementAnnule(SlmspError):
    """Jugement non lancé : une erreur (budget, API) a arrêté la file avant son tour."""


class FileOrdonnee:
    """Appels menés par `paralleles` threads, résultats rendus dans l'ordre de soumission.

    À 1 (ou sans pool), chaque appel est fait au moment où `resultats` atteint son tour : le
    comportement reste celui d'une boucle séquentielle. Une erreur d'appel arrête la file : les
    appels non commencés lèvent `JugementAnnule`, ceux en cours vont à leur terme (déjà payés,
    leur résultat est rendu). Seul le thread appelant écrit : l'ordre des fichiers est celui
    de la soumission. Le registre de budget et le journal des appels ouvrent une connexion
    SQLite par opération (`BEGIN IMMEDIATE`, WAL) : sûrs entre threads.
    """

    def __init__(self, paralleles: int) -> None:
        if paralleles < 1:
            raise ValueError("paralleles ≥ 1 attendu")
        self._pool = (
            ThreadPoolExecutor(max_workers=paralleles, thread_name_prefix="juge-donnees")
            if paralleles > 1
            else None
        )
        self._arret = threading.Event()
        self._file: deque[tuple[Any, Future[Any] | Callable[[], Any] | None]] = deque()

    def _garde(self, appel: Callable[[], Any]) -> Callable[[], Any]:
        def execution() -> Any:
            if self._arret.is_set():
                raise JugementAnnule("jugement non lancé après une erreur")
            try:
                return appel()
            except BaseException:
                self._arret.set()
                raise

        return execution

    def soumettre(self, etiquette: Any, appel: Callable[[], Any] | None) -> None:
        """`appel` (sans argument) à faire ; `None` : rien à appeler, résultat `None`."""
        if appel is None:
            self._file.append((etiquette, None))
        elif self._pool is None:
            self._file.append((etiquette, self._garde(appel)))
        else:
            self._file.append((etiquette, self._pool.submit(self._garde(appel))))

    def __len__(self) -> int:
        return len(self._file)

    def resultats(self, *, attendre: bool = False) -> Iterator[tuple[Any, Any, Exception | None]]:
        """`(etiquette, résultat, erreur)` dans l'ordre de soumission, tant que la tête est
        prête (ou jusqu'au bout avec `attendre`) ; `erreur` : l'exception de l'appel (résultat
        `None`). Une interruption (`KeyboardInterrupt`) est propagée."""
        while self._file:
            etiquette, travail = self._file[0]
            if isinstance(travail, Future) and not travail.done():
                if not attendre:
                    return
                while not travail.done():  # attente interruptible (Ctrl-C sous Windows)
                    wait([travail], timeout=1.0)
            self._file.popleft()
            try:
                if travail is None:
                    valeur = None
                elif isinstance(travail, Future):
                    valeur = travail.result()
                else:
                    valeur = travail()
            except Exception as exc:
                yield etiquette, None, exc
            else:
                yield etiquette, valeur, None

    def arreter(self) -> None:
        """Plus aucun appel lancé ; ceux en cours vont à leur terme."""
        self._arret.set()

    def fermer(self, *, attendre: bool = True) -> None:
        if self._pool is not None:
            self._pool.shutdown(wait=attendre, cancel_futures=True)


def juger_en_parallele(
    juge: JugeDonnees,
    demandes: Iterable[tuple[Any, str, str, str]],
    paralleles: int | None = None,
) -> Iterator[tuple[Any, VerdictDonnees | BaseException]]:
    """Juge `(etiquette, tache, source, candidat)` sur `paralleles` threads (défaut :
    `[juge_donnees] appels_paralleles`) ; rend `(etiquette, verdict ou erreur)` dans l'ordre
    des demandes. Après une erreur, les demandes non lancées rendent `JugementAnnule`."""
    file = FileOrdonnee(paralleles or juge.config.appels_paralleles)
    try:
        for etiquette, tache, source, candidat in demandes:
            file.soumettre(
                etiquette,
                lambda t=tache, s=source, c=candidat: juge.juger_candidat(t, s, c),
            )
        for etiquette, verdict, erreur in file.resultats(attendre=True):
            yield etiquette, verdict if erreur is None else erreur
    except BaseException:
        file.arreter()
        file.fermer(attendre=False)
        raise
    file.fermer()


class JugeDonnees:
    """Juge de données : `juger_candidat` et `estimer` (voir le module)."""

    def __init__(
        self,
        config: JugeDonneesConfig,
        client: ClientCompatibleOpenAI,
        grilles: Mapping[str, GrilleDonnees],
        cache: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self.config = config
        self.client = client
        self.grilles = dict(grilles)
        self.cache: dict[str, dict[str, Any]] = cache if cache is not None else {}
        self.session_id = nouvelle_session(PREFIXE_SESSION)
        self.cout_total = 0.0
        """Coût de tous les appels faits, y compris ceux d'un verdict qui a levé ensuite."""
        self._verrou = threading.Lock()
        """`juger_candidat` est appelé depuis plusieurs threads (`juger_en_parallele`)."""

    def description(self) -> dict[str, Any]:
        """Modèle, réglages, version du prompt et SHA des grilles, inscrits dans le run."""
        return {
            "modele": self.config.modele,
            "effort": self.config.effort_cle,
            "max_tokens": self.config.max_tokens,
            "version_prompt": VERSION_PROMPT,
            "grilles": {t: g.sha256 for t, g in sorted(self.grilles.items())},
            "seuils": self.config.seuils,
        }

    def _grille(self, tache: str) -> GrilleDonnees:
        grille = self.grilles.get(tache)
        if grille is None:
            raise SlmspError(f"Tâche {tache!r} sans grille de données")
        return grille

    def cle(self, tache: str, source: str, candidat: str) -> str:
        """Empreinte du cache (modèle, effort, version du prompt, grille, schéma et critères,
        source, candidat)."""
        return sha256_hex(
            json_canonique(
                [
                    self.config.modele,
                    self.config.effort_cle,
                    VERSION_PROMPT,
                    self._grille(tache).sha256,
                    sha256_hex(json_canonique(schema_sortie(tache))),
                    CRITERES_JUGE_DONNEES[tache],
                    source,
                    candidat,
                ]
            )
        )

    def prompt(self, tache: str, source: str, candidat: str) -> str:
        """Grille de la Tâche, emplacements remplis en une passe (aucun remplacement imbriqué).

        Source et candidat sont placés entre balises dont l'identifiant dérive de leur contenu :
        un texte ne peut pas fermer sa propre balise (injection depuis une sortie Mistral), et
        la grille déclare ce contenu comme une donnée, jamais une instruction."""
        jeton = sha256_hex(json_canonique([source, candidat]))[:16]
        valeurs = {
            "source": f"<source-{jeton}>\n{source}\n</source-{jeton}>",
            "candidat": f"<candidat-{jeton}>\n{candidat}\n</candidat-{jeton}>",
        }
        return re.sub(
            r"\{(source|candidat)\}", lambda m: valeurs[m.group(1)], self._grille(tache).texte
        )

    def tokens_entree(self, tache: str, prompt: str) -> int:
        """Estimation prudente : ⌈caractères (prompt et schéma) / 3⌉ + marge."""
        schema = json_canonique(schema_sortie(tache)).decode("utf-8")
        return math.ceil((len(prompt) + len(schema)) / CARACTERES_PAR_TOKEN) + MARGE_TOKENS

    def estimer(self, demandes: Sequence[tuple[str, str, str]]) -> EstimationJuge:
        """Coût de `(tache, source, candidat)` sans appel ; vérifie d'abord l'usage de budget."""
        registre = self.client.registre
        registre.verifier_usage(self.config.usage_budget)
        uniques: dict[str, int] = {}
        for tache, source, candidat in demandes:
            cle = self.cle(tache, source, candidat)
            if cle not in uniques:
                uniques[cle] = self.tokens_entree(tache, self.prompt(tache, source, candidat))
        a_juger = [t for cle, t in uniques.items() if cle not in self.cache]
        modele = self.config.modele
        estime = sum(
            cout_estime(registre.tarifs, modele, MODE, t, self.config.sortie_estimation)
            for t in a_juger
        )
        # Pire cas : chaque candidat peut être redemandé une fois (sortie non conforme).
        pire = TENTATIVES_MAX * sum(
            cout_pire_cas(
                registre.tarifs,
                modele,
                MODE,
                t,
                self.config.max_tokens,
                registre.config.majoration_entree,
            )
            for t in a_juger
        )
        return EstimationJuge(len(uniques), len(uniques) - len(a_juger), len(a_juger), estime, pire)

    def _parametres(self, tache: str) -> dict[str, Any]:
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
                "json_schema": {"name": NOM_SCHEMA, "schema": schema_sortie(tache), "strict": True},
            }
        parametres["provider"] = {"require_parameters": True}
        return parametres

    def _depuis_cache(self, tache: str, cle: str, ligne: Mapping[str, Any]) -> VerdictDonnees:
        notes = {str(k): float(v) for k, v in ligne["notes"].items()}
        return VerdictDonnees(
            tache=tache,
            cle=cle,
            verdict=_decider(self.config.seuils[tache], notes),
            notes=notes,
            listes=dict(ligne.get("listes") or {}),
            motifs=dict(ligne.get("motifs") or {}),
            extraits={k: list(v) for k, v in (ligne.get("extraits") or {}).items()},
            extraits_invalides=int(ligne.get("extraits_invalides") or 0),
            verdict_modele=ligne.get("verdict_modele"),
            depuis_cache=True,
            motif=ligne.get("motif"),
        )

    def juger_candidat(self, tache: str, source: str, candidat: str) -> VerdictDonnees:
        """Verdict du candidat (voir le module). Lève `BudgetEpuise`, `ErreurApiFournisseur`."""
        if tache not in CRITERES_JUGE_DONNEES:
            raise SlmspError(f"Tâche {tache!r} hors du juge de données")
        cle = self.cle(tache, source, candidat)
        connu = self.cache.get(cle)
        if connu is not None:
            return self._depuis_cache(tache, cle, connu)
        prompt = self.prompt(tache, source, candidat)
        tokens = self.tokens_entree(tache, prompt)
        cout, appels, erreur = 0.0, [], ""
        messages: list[dict[str, str]] = [{"role": "user", "content": prompt}]
        for _ in range(TENTATIVES_MAX):
            reponse = self.client.appeler(
                self.config.usage_budget,
                self.session_id,
                messages,
                modele=self.config.modele,
                max_tokens=self.config.max_tokens,
                tokens_entree_estimes=tokens,
                parametres=self._parametres(tache),
            )
            cout += reponse.cout_eur
            with self._verrou:
                self.cout_total += reponse.cout_eur
            appels.append(reponse.appel_id)
            if (reponse.finish_reason or "").lower() in FINS_INTERROMPUES:
                return VerdictDonnees(
                    tache,
                    cle,
                    "non-juge",
                    cout_eur=cout,
                    motif=MOTIF_INTERROMPUE,
                    appel_ids=tuple(appels),
                )
            try:
                sortie = _lire_sortie(tache, reponse.texte)
            except SortieNonConforme as exc:
                erreur = str(exc)
                # Relance corrective : la sortie fautive et l'écart constaté par le code.
                correction = RELANCE_CORRECTIVE.format(ecart=erreur)
                messages = [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": reponse.texte},
                    {"role": "user", "content": correction},
                ]
                tokens += math.ceil((len(reponse.texte) + len(correction)) / CARACTERES_PAR_TOKEN)
                continue
            verdict = self._verdict(tache, cle, sortie, source, candidat, cout, tuple(appels))
            with self._verrou:
                self.cache[cle] = verdict.ligne()
            return verdict
        return VerdictDonnees(
            tache, cle, "invalide", cout_eur=cout, motif=erreur, appel_ids=tuple(appels)
        )

    def _verdict(
        self,
        tache: str,
        cle: str,
        sortie: SortieJuge,
        source: str,
        candidat: str,
        cout: float,
        appels: tuple[str, ...],
    ) -> VerdictDonnees:
        listes: dict[str, Any] = {
            nom: [
                e.model_dump() if isinstance(e, Element) else e
                for e in getattr(sortie.listes, nom) or []
            ]
            for nom in LISTES_PAR_TACHE[tache]
        }
        extraits: dict[str, list[str]] = {}
        invalides = 0
        for nom, critere in sortie.criteres.items():
            extraits[nom], rejetes = _filtrer_extraits(critere.extraits, candidat, source)
            invalides += rejetes
        notes = _notes(tache, {n: c.note for n, c in sortie.criteres.items()}, listes)
        motif = None
        if tache == "CR" and not (listes.get("decisions") or listes.get("actions")):
            motif = MOTIF_COUVERTURE_NON_EVALUABLE
        return VerdictDonnees(
            tache=tache,
            cle=cle,
            verdict=_decider(self.config.seuils[tache], notes),
            notes=notes,
            listes=listes,
            motifs={n: c.motif for n, c in sortie.criteres.items()},
            extraits=extraits,
            extraits_invalides=invalides,
            verdict_modele=sortie.verdict_modele,
            cout_eur=cout,
            motif=motif,
            appel_ids=appels,
        )


# --- Candidats d'un run data-generate ----------------------------------------------------


@dataclass(frozen=True)
class Candidat:
    """Un candidat à juger : `candidat_id` (`mistral:<appel_id>` ou `slm:<appel_local_id>`)."""

    candidat_id: str
    session_id: str
    tache: str
    source: str
    texte: str


def source_session(lecteur: Any, brut: Any) -> str:
    """Source par Tâche : CR, la transcription seule ; LC, le texte ; CT, les amorces
    (`LecteurGeneration`, `SessionBrute` ; réutilisée par la génération vérifiée, O6a)."""
    if brut.tache == "CR":
        contenu = lecteur.message(brut.appel_ids[0]).get("content")
        return contenu if isinstance(contenu, str) else ""
    amorces = [lecteur.amorces[a] for a in [*brut.amorce_ids, *brut.amorces_derivees]]
    if brut.tache == "LC":
        textes = [a.texte for a in amorces if a.emplacement == "texte"] or [
            a.texte for a in amorces
        ]
        return "\n\n".join(textes)
    return "\n".join(f"{a.emplacement} : {a.texte}" for a in amorces)


def candidats_depuis_generation(
    lecteur: Any, taches: Iterable[str] = TACHES_JUGEES
) -> tuple[list[Candidat], int]:
    """Candidats des sessions de `brut.jsonl` (`LecteurGeneration`) pour `taches`, et nombre
    de sessions écartées (source ou réponse introuvable, CR sans transcription)."""
    voulues = set(taches)
    candidats, ecartees = [], 0
    for brut in lecteur.sessions():
        if brut.tache not in voulues:
            continue
        if brut.tache == "CR" and len(brut.appel_ids) < 2:
            ecartees += 1
            continue
        try:
            texte = lecteur.reponse_finale(brut)
            source = source_session(lecteur, brut)
        except (SlmspError, KeyError):
            ecartees += 1
            continue
        if not source:
            ecartees += 1
            continue
        candidats.append(
            Candidat(f"mistral:{brut.appel_ids[-1]}", brut.session_id, brut.tache, source, texte)
        )
    return candidats, ecartees


def limiter(candidats: Sequence[Candidat], limite: int | None) -> list[Candidat]:
    """Au plus `limite` candidats par Tâche, dans l'ordre (tous si `None`)."""
    if limite is None:
        return list(candidats)
    vus: Counter[str] = Counter()
    gardes = []
    for candidat in candidats:
        if vus[candidat.tache] < limite:
            vus[candidat.tache] += 1
            gardes.append(candidat)
    return gardes


# --- Run ---------------------------------------------------------------------------------


@dataclass(frozen=True)
class ResultatJugementDonnees:
    run: Run
    statut: str
    rapport: dict[str, Any]
    estimation: EstimationJuge


def rapport_depuis(
    lignes: Iterable[Mapping[str, Any]], non_juges: Mapping[str, int]
) -> dict[str, Any]:
    """Taux d'acceptation par Tâche et par critère (part des candidats notés qui atteignent le
    seuil du critère), extraits invalides, invalides, non jugés et coût."""
    blocs: dict[str, dict[str, Any]] = {}
    atteints: dict[str, Counter[str]] = {}
    notes_par_tache: Counter[str] = Counter()
    cout = 0.0
    for ligne in lignes:
        tache = str(ligne.get("tache"))
        bloc = blocs.setdefault(
            tache,
            {"juges": 0, "acceptes": 0, "refuses": 0, "invalides": 0, "extraits_invalides": 0},
        )
        bloc["juges"] += 1
        verdict = str(ligne.get("verdict"))
        bloc[{"accepte": "acceptes", "refuse": "refuses"}.get(verdict, "invalides")] += 1
        bloc["extraits_invalides"] += int(ligne.get("extraits_invalides") or 0)
        cout += float(ligne.get("cout_eur") or 0.0)
        if verdict not in ("accepte", "refuse"):
            continue
        notes_par_tache[tache] += 1
        compte = atteints.setdefault(tache, Counter())
        notes = ligne.get("notes") or {}
        for critere, seuil in (ligne.get("seuils") or {}).items():
            compte[critere] += int(float(notes.get(critere, 0.0)) >= float(seuil))
    for tache, bloc in blocs.items():
        bloc["taux_acceptation"] = bloc["acceptes"] / bloc["juges"]
        notes = notes_par_tache[tache]
        bloc["taux_par_critere"] = {
            c: n / notes for c, n in sorted(atteints.get(tache, Counter()).items())
        }
    return {
        "schema_version": 1,
        "taches": dict(sorted(blocs.items())),
        "non_juges": dict(sorted(non_juges.items())),
        "cout_eur": cout,
    }


def config_du_run(run_id: str, racine: str | Path) -> dict[str, Any]:
    """Config d'un run `data-juger` à reprendre (`depuis`, `taches`, `limite`)."""
    run = ouvrir_run(run_id, racine=racine)
    if run.type != TYPE_RUN:
        raise ManifesteInvalide(f"run {run_id} : type {run.type!r}, {TYPE_RUN} attendu")
    return dict(run.manifeste.config)


def lancer_jugement(
    *,
    racine: str | Path,
    juge: JugeDonnees,
    candidats: Sequence[Candidat],
    depuis_run_id: str,
    taches: Sequence[str] = TACHES_JUGEES,
    limite: int | None = None,
    plafond_estime_eur: float | None = None,
    reprendre_run_id: str | None = None,
    config_run: Mapping[str, Any] | None = None,
    consigner: Callable[[str], None] = print,
) -> ResultatJugementDonnees:
    """Juge `candidats` dans un run `data-juger` nouveau ou repris (voir le module).

    Lève `PlafondEstimeDepasse` avant tout run et tout appel si le coût pire cas estimé
    dépasse `plafond_estime_eur`. `config_run` s'ajoute à la config du run (origine, juge).
    Chaque verdict porte `juge` (identifiant du modèle) : la sélection joint par
    `(session_id, candidat_id)` et peut ainsi distinguer deux juges.
    """
    base = Path(racine).resolve()
    retenus = limiter([c for c in candidats if c.tache in taches], limite)
    deja: set[str] = set()
    interruptions: Counter[str] = Counter()
    if reprendre_run_id is not None:
        precedent = ouvrir_run(reprendre_run_id, racine=base)
        deja = {
            str(ligne["candidat_id"])
            for ligne in precedent.lire_jsonl(NOM_VERDICTS)
            if isinstance(ligne, dict) and "candidat_id" in ligne
        }
        interruptions.update(
            str(ligne["candidat_id"])
            for ligne in precedent.lire_jsonl(NOM_INTERRUPTIONS)
            if isinstance(ligne, dict) and "candidat_id" in ligne
        )
    non_juges: Counter[str] = Counter()
    a_juger = []
    for c in retenus:
        if c.candidat_id in deja:
            continue
        if interruptions[c.candidat_id] >= INTERRUPTIONS_MAX:
            non_juges[MOTIF_PLAFOND_INTERRUPTIONS] += 1
            continue
        a_juger.append(c)
    estimation = juge.estimer([(c.tache, c.source, c.texte) for c in a_juger])
    resume = (
        f"{estimation.nb_a_juger} candidat(s) à juger, {estimation.nb_en_cache} en cache ; "
        f"coût estimé {estimation.cout_estime_eur:.2f} €, pire cas "
        f"{estimation.cout_pire_cas_eur:.2f} €"
    )
    if plafond_estime_eur is not None and estimation.cout_pire_cas_eur > plafond_estime_eur:
        raise PlafondEstimeDepasse(
            f"juge de données refusé : {resume}, au-dessus du plafond de "
            f"{plafond_estime_eur:.2f} € ; aucun run créé, aucun appel fait"
        )
    consigner(f"Estimation : {resume}.")
    if reprendre_run_id is not None:
        run, _ = reprendre(reprendre_run_id, fichier=NOM_VERDICTS, cle="candidat_id", racine=base)
    else:
        run = nouveau_run(
            TYPE_RUN,
            "juger",
            {
                "depuis": depuis_run_id,
                "taches": list(taches),
                "limite": limite,
                "juge": juge.description(),
                **(config_run or {}),
            },
            parents=[depuis_run_id],
            racine=base,
        )
    statut, motif = "complet", None
    cout_depart = juge.cout_total
    demandes = ((c, c.tache, c.source, c.texte) for c in a_juger)
    try:
        # Jugements en parallèle (`appels_paralleles`), verdicts écrits dans l'ordre ; après une
        # erreur de budget ou d'API, les jugements non lancés sont annulés, ceux en cours écrits.
        for candidat, verdict in juger_en_parallele(juge, demandes):
            if isinstance(verdict, JugementAnnule):
                continue
            if isinstance(verdict, BudgetEpuise):
                if statut == "complet":
                    statut, motif = "partiel-budget", str(verdict)
                continue
            if isinstance(verdict, ErreurApiFournisseur):
                if statut == "complet":
                    statut, motif = "partiel-erreur", f"{type(verdict).__name__} : {verdict}"
                continue
            if isinstance(verdict, BaseException):
                raise verdict
            if verdict.verdict == "non-juge":
                non_juges[verdict.motif or "non-juge"] += 1
                run.ajouter_jsonl(
                    NOM_INTERRUPTIONS,
                    {
                        "candidat_id": candidat.candidat_id,
                        "cle": verdict.cle,
                        "motif": verdict.motif,
                        "cout_eur": verdict.cout_eur,
                        "appel_ids": list(verdict.appel_ids),
                    },
                )
                continue
            run.ajouter_jsonl(
                NOM_VERDICTS,
                {
                    "session_id": candidat.session_id,
                    "candidat_id": candidat.candidat_id,
                    "juge": juge.config.modele,
                    **verdict.ligne(),
                    "seuils": juge.config.seuils[candidat.tache],
                },
            )
    except KeyboardInterrupt:
        run.terminer("interrompu", "interruption clavier")
        raise
    except BaseException as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
        raise
    if statut == "complet" and non_juges:
        statut = "partiel-erreur"
        motif = f"{sum(non_juges.values())} candidat(s) non jugé(s), rejouables par reprise"
    # Coût de tous les appels de l'invocation, y compris une 1re tentative dont la relance a levé.
    cout_invocation = juge.cout_total - cout_depart
    rapport = rapport_depuis(run.lire_jsonl(NOM_VERDICTS), non_juges)
    rapport.update({"statut": statut, "motif": motif, "cout_invocation_eur": cout_invocation})
    run.ajouter_jsonl(NOM_BILAN, rapport)
    if statut == "complet":
        run.ecrire(NOM_RAPPORT, json_canonique(rapport) + b"\n")
    run.terminer(statut, motif)
    return ResultatJugementDonnees(run, statut, rapport, estimation)
