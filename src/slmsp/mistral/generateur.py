"""Générateur Mistral prouvé : seule source de Données d'entraînement (D1.1, D1.2, AD-3).

`Generateur.generer(gabarit_id, amorce_ids, session_id, tache, messages_precedents=None)`
n'accepte aucun texte libre (verrou 3) :

- le gabarit est résolu par son identifiant dans `config/prompts/generateur/` et validé par
  `slmsp.core.gabarits` (verrou 6) ; son SHA-256 est celui des octets du fichier ;
- les amorces sont résolues par leur identifiant dans l'artefact `seed`
  (`runs/data-seed/<run_id>/amorces.jsonl`, lu par `core.artefacts.lire`), leur `sha_texte`
  est recalculé et leur provenance vérifiée (verrou 5 : ligne publique, ou réponse Mistral
  journalisée et `ok` dont le contenu est exactement le texte ; `anael` refusé) ;
- un message `assistant` précédent n'est admis que s'il égale, en JSON canonique normalisé,
  une réponse `generation`/`ok` journalisée de la même session ; un message `tool` que s'il
  vient d'une cassette de la même session : `data/cassettes/<session_id>.json` ou les
  segments `<session_id>.t1.json`, `<session_id>.t2.json`… (un par tour d'outils, 9.4).

Extensions de la story 9.4, toujours sans texte libre :

- une Tâche outillée (`RD`) reçoit à chaque appel les outils de `config/outils-mcp.toml`
  (format `tools` d'OpenAI, `tool_choice = "auto"`, AD-8), lus par le Générateur lui-même ;
- l'emplacement `passages` est réservé : aucune amorce ne le remplit, sa valeur est le
  rendu `rendre_passages(session_id)` injecté à la construction (passages de l'Index
  retenus au plan de `generate` et formatés par `harness.prompts`) ;
- `deriver_amorce(appel_id, …)` fait d'une réponse journalisée de la session une amorce
  `mistral` (transcription du CR en deux temps).

La requête vaut `[{"role": "user", "content": consigne_rendue}] + messages_precedents` :
aucun autre texte n'y entre. L'appel passe par `ClientMistral._appeler` avec le jeton de
preuve `_JETON`, seul moyen d'écrire une ligne `generation` au journal
`appels-mistral.sqlite` (requête complète, gabarit et son SHA, `amorce_ids`, réponse brute).

Préalables (D1.2) : la table `[mistral]` de `config/donnees.toml` doit porter
`conditions_verifiees_le` égale au jour même et `modeles_stables` contenant le modèle
demandé ; sinon `PrealableNonSatisfait` à la construction. Un modèle résolu hors de
`modeles_stables` lève `ModeleMistralRefuse` après l'appel, qui reste journalisé.
"""

from __future__ import annotations

import copy
import json
import math
import re
import tomllib
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Final

from pydantic import BaseModel, ConfigDict, Field, StrictInt, ValidationError

from slmsp.core.artefacts import lire
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.config import plafonds_re_evaluation, racine_projet
from slmsp.core.erreurs import ConfigurationInvalide, ProvenanceInvalide, SlmspError
from slmsp.core.gabarits import GabaritInvalide, GabaritValide, valider_gabarit
from slmsp.core.messages import ConversationInvalide, valider_conversation
from slmsp.core.schemas.amorce import Amorce, texte_mistral_conforme
from slmsp.core.schemas.cassette import Cassette
from slmsp.core.schemas.run import MOTIF_RUN_ID
from slmsp.mistral.client import ClientMistral, ModeleMistralRefuse, ReponseMistral
from slmsp.mistral.journal import USAGE_GENERATION, JournalMistral, LigneAppel, journal_pour

__all__ = [
    "Generateur",
    "Generation",
    "PrealableNonSatisfait",
    "PrealablesGeneration",
    "charger_plafonds_mots",
    "charger_prealables",
    "message_assistant",
    "raison_de_fin",
]

_JETON: Final = object()
"""Jeton de preuve : seul ce module peut faire écrire une ligne `generation` au journal."""

TACHES: Final = ("Q", "RD", "CR", "LC", "CO", "RE", "CT", "generique")
"""Tâches générables. Le gabarit `validation` (tâche `validation`) est réservé à la story 9.5."""

MAX_TOKENS_DEFAUT: Final = 2048
CARACTERES_PAR_TOKEN: Final = 3
CLES_OPTIONNELLES_GABARIT: Final = ("max_tokens",)
NOM_AMORCES: Final = "amorces.jsonl"
TYPE_RUN_SEED: Final = "data-seed"
TACHES_OUTILLEES: Final = frozenset({"RD"})
"""Tâches dont chaque appel porte les outils de `config/outils-mcp.toml` (AD-8)."""
TOOL_CHOICE: Final = "auto"
EMPLACEMENT_PASSAGES: Final = "passages"
"""Emplacement réservé : rempli par le rendu injecté des passages de l'Index, jamais par une
amorce."""
EMPLACEMENT_PLAFOND: Final = "plafond_mots"
"""Emplacement réservé : plafond de mots du résumé RE, dérivé de l'amorce `longueur_demandee`
par `[re.longueurs]` de `config/evaluation.toml` (consigne de forme seulement, D1.1). Jamais
rempli par une amorce ; le message de l'exemple d'entraînement garde le mot nu du Jeu."""
EMPLACEMENT_PLAFOND_TACHE: Final = "plafond_mots_tache"
"""Emplacement réservé (story 9.10) : plafond de mots de la réponse cible de la Tâche du
gabarit, lu dans `[generateur.plafonds_mots]` de `config/donnees.toml` (consigne de longueur
seulement, D1.1). Jamais rempli par une amorce, jamais recopié dans un exemple d'entraînement
(les messages SFT sont reconstruits par `data.build`, sans la consigne du gabarit)."""
EMPLACEMENTS_RESERVES: Final = frozenset(
    {EMPLACEMENT_PASSAGES, EMPLACEMENT_PLAFOND, EMPLACEMENT_PLAFOND_TACHE}
)

_RE_GABARIT_ID = re.compile(r"[a-z0-9-]+")
_RE_SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
_RE_RUN_ID = re.compile(MOTIF_RUN_ID)
_RE_EMPLACEMENT = re.compile(r"\{([a-z_]+)\}")
_RE_ENTIER = re.compile(r"[1-9][0-9]*")


class PrealableNonSatisfait(SlmspError):
    """Préalable de génération absent ou périmé (D1.2) : le Générateur refuse de démarrer."""


class _MistralDonnees(BaseModel):
    """Table `[mistral]` de `config/donnees.toml` (story 9.1) ; autres clés ignorées."""

    model_config = ConfigDict(extra="ignore")

    conditions_verifiees_le: date
    modeles_stables: list[str] = Field(min_length=1)


class _FichierDonnees(BaseModel):
    model_config = ConfigDict(extra="ignore")

    mistral: _MistralDonnees


class _GenerateurDonnees(BaseModel):
    """Table `[generateur]` de `config/donnees.toml` (story 9.10) ; autres clés ignorées.

    Modèle strict de référence : `slmsp.data.config.GenerateurDonnees` (couche supérieure)."""

    model_config = ConfigDict(extra="ignore")

    plafonds_mots: dict[str, Annotated[StrictInt, Field(gt=0)]] = Field(default_factory=dict)


class _FichierGenerateur(BaseModel):
    model_config = ConfigDict(extra="ignore")

    generateur: _GenerateurDonnees = Field(default_factory=_GenerateurDonnees)


@dataclass(frozen=True)
class PrealablesGeneration:
    """Préalables lus et vérifiés : date de vérification des conditions, liste stable."""

    fichier: Path
    conditions_verifiees_le: date
    modeles_stables: tuple[str, ...]


def charger_prealables(
    fichier: str | Path, *, modele: str, aujourd_hui: date
) -> PrealablesGeneration:
    """Lit la table `[mistral]` de `fichier` et vérifie les préalables D1.2.

    Lève `PrealableNonSatisfait` si le fichier ou la table manque ou est invalide, si
    `conditions_verifiees_le` n'est pas `aujourd_hui`, ou si `modele` n'est pas dans
    `modeles_stables`.
    """
    chemin = Path(fichier)
    try:
        donnees = tomllib.loads(chemin.read_bytes().decode("utf-8"))
    except OSError as exc:
        raise PrealableNonSatisfait(
            f"{chemin} : préalables de génération illisibles ({type(exc).__name__})"
        ) from None
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise PrealableNonSatisfait(f"{chemin} : TOML invalide ({type(exc).__name__})") from None
    try:
        table = _FichierDonnees.model_validate(donnees).mistral
    except ValidationError as exc:
        cles = sorted({".".join(str(p) for p in e["loc"]) for e in exc.errors()})
        raise PrealableNonSatisfait(
            f"{chemin} : table [mistral] absente ou invalide ({', '.join(cles)})"
        ) from None
    if table.conditions_verifiees_le != aujourd_hui:
        raise PrealableNonSatisfait(
            f"{chemin} : conditions Mistral vérifiées le {table.conditions_verifiees_le}, "
            f"pas aujourd'hui ({aujourd_hui}) : génération refusée"
        )
    if modele not in table.modeles_stables:
        raise PrealableNonSatisfait(
            f"{chemin} : modèle {modele!r} absent de modeles_stables : génération refusée"
        )
    return PrealablesGeneration(
        fichier=chemin,
        conditions_verifiees_le=table.conditions_verifiees_le,
        modeles_stables=tuple(table.modeles_stables),
    )


def charger_plafonds_mots(fichier: str | Path) -> dict[str, int]:
    """Plafonds de mots par Tâche de `[generateur.plafonds_mots]` de `fichier` (vide si la
    table manque). Lève `ConfigurationInvalide` si le fichier est illisible, si une valeur
    n'est pas un entier strictement positif ou si une clé n'est pas une Tâche générable."""
    chemin = Path(fichier)
    try:
        donnees = tomllib.loads(chemin.read_bytes().decode("utf-8"))
        table = _FichierGenerateur.model_validate(donnees).generateur.plafonds_mots
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, ValidationError) as exc:
        raise ConfigurationInvalide(
            f"{chemin} : table [generateur.plafonds_mots] illisible ou invalide "
            f"({type(exc).__name__})"
        ) from None
    inconnues = sorted(set(table) - set(TACHES))
    if inconnues:
        raise ConfigurationInvalide(
            f"{chemin} : [generateur.plafonds_mots] : tâche(s) inconnue(s) {', '.join(inconnues)}"
        )
    return dict(table)


def _normaliser_appels(appels: list[Any]) -> list[Any]:
    """Appels d'outil réduits à `id`, `type` (`function` par défaut) et `function{name,
    arguments}` : l'API ajoute `index`, absent du format canonique (`core.messages`)."""
    normalises: list[Any] = []
    for appel in appels:
        fonction = appel.get("function") if isinstance(appel, Mapping) else None
        if not isinstance(fonction, Mapping):
            normalises.append(appel)  # forme inconnue : laissée telle quelle, refusée ensuite
            continue
        normalises.append(
            {
                "id": appel.get("id"),
                "type": appel.get("type") or "function",
                "function": {"name": fonction.get("name"), "arguments": fonction.get("arguments")},
            }
        )
    return normalises


def _normaliser_assistant(message: Mapping[str, Any]) -> dict[str, Any]:
    """Message `assistant` sans `content` vide ni `tool_calls` vide, appels d'outil réduits
    (`_normaliser_appels`) ; toute autre clé est gardée et empêche donc l'égalité."""
    normalise = dict(message)
    for cle in ("content", "tool_calls"):
        if cle in normalise and not normalise[cle]:
            del normalise[cle]
    if isinstance(normalise.get("tool_calls"), list):
        normalise["tool_calls"] = _normaliser_appels(normalise["tool_calls"])
    return normalise


def message_assistant(brut: bytes | str | None) -> dict[str, Any]:
    """Message `assistant` d'une réponse brute Mistral (`choices[0].message`).

    Garde `role`, `content` s'il est une chaîne non vide et `tool_calls` s'il est une liste
    non vide (appels réduits à `id`, `type`, `function{name, arguments}`). Lève
    `ProvenanceInvalide` si le corps n'est pas une réponse lisible ou si le message n'a ni
    contenu ni appel d'outil.
    """
    if brut is None:
        raise ProvenanceInvalide("réponse brute absente du journal")
    try:
        corps = json.loads(brut)
        message = corps["choices"][0]["message"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise ProvenanceInvalide("réponse brute illisible : choices[0].message absent") from None
    if not isinstance(message, Mapping) or message.get("role") != "assistant":
        raise ProvenanceInvalide("réponse brute : message assistant attendu")
    resultat: dict[str, Any] = {"role": "assistant"}
    contenu = message.get("content")
    if isinstance(contenu, str) and contenu:
        resultat["content"] = contenu
    appels = message.get("tool_calls")
    if isinstance(appels, list) and appels:
        resultat["tool_calls"] = _normaliser_appels(appels)
    if len(resultat) == 1:
        raise ProvenanceInvalide("réponse brute sans contenu ni appel d'outil")
    return resultat


def raison_de_fin(brut: bytes | str | None) -> str | None:
    """`choices[0].finish_reason` d'une réponse brute Mistral (`None` si absente ou illisible)."""
    if brut is None:
        return None
    try:
        raison = json.loads(brut)["choices"][0].get("finish_reason")
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        return None
    return raison if isinstance(raison, str) else None


@dataclass(frozen=True)
class Generation:
    """Résultat d'un appel du Générateur, tel que journalisé."""

    appel_id: str
    session_id: str
    tache: str
    gabarit_id: str
    version_gabarit: int
    sha256_gabarit: str
    amorce_ids: tuple[str, ...]
    messages: tuple[Mapping[str, Any], ...]
    reponse: ReponseMistral
    reponse_brute: bytes


def _textes_resultat(resultat: Any) -> list[str]:
    """Formes admises du `content` d'un message `tool` pour un `result` MCP : JSON canonique,
    ou textes des éléments `text` joints sans séparateur ou par un saut de ligne (règle de
    `harness.taches.recherche.contenu_resultat`, reprise par `data.sessions`)."""
    formes = [json_canonique(resultat).decode("utf-8")]
    if isinstance(resultat, Mapping) and isinstance(resultat.get("content"), list):
        morceaux = resultat["content"]
        if all(isinstance(m, Mapping) and isinstance(m.get("text"), str) for m in morceaux):
            formes.append("".join(m["text"] for m in morceaux))
            formes.append("\n".join(m["text"] for m in morceaux))
    return formes


def _outils_openai(donnees: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Entrées `[[outils]]` de `config/outils-mcp.toml` au format `tools` d'OpenAI, dans
    l'ordre du fichier (même projection que `slmsp.mcp.outils.charger_outils`, que la
    couche `mistral` ne peut pas importer)."""
    entrees = donnees.get("outils")
    if not isinstance(entrees, list) or not entrees:
        raise ConfigurationInvalide("outils-mcp.toml : table [[outils]] absente ou vide")
    outils: list[dict[str, Any]] = []
    for entree in entrees:
        if not isinstance(entree, Mapping) or not all(
            isinstance(entree.get(cle), typ)
            for cle, typ in (("nom", str), ("description", str), ("parametres", Mapping))
        ):
            raise ConfigurationInvalide("outils-mcp.toml : outil sans nom, description ou schéma")
        outils.append(
            {
                "type": "function",
                "function": {
                    "name": entree["nom"],
                    "description": entree["description"],
                    "parameters": copy.deepcopy(dict(entree["parametres"])),
                },
            }
        )
    return outils


class Generateur:
    """Générateur Mistral : gabarit et amorces résolus par identifiant, appel journalisé."""

    def __init__(
        self,
        seed_run_id: str,
        *,
        client: ClientMistral,
        racine: str | Path | None = None,
        fichier_donnees: str | Path | None = None,
        dossier_gabarits: str | Path | None = None,
        fichier_outils: str | Path | None = None,
        rendre_passages: Callable[[str], str] | None = None,
        aujourd_hui: Callable[[], date] = date.today,
    ) -> None:
        if not isinstance(seed_run_id, str) or not _RE_RUN_ID.fullmatch(seed_run_id):
            raise ProvenanceInvalide("identifiant de run seed invalide")
        self.client = client
        self.racine = Path(racine) if racine is not None else racine_projet()
        self.fichier_donnees = (
            Path(fichier_donnees)
            if fichier_donnees is not None
            else self.racine / "config" / "donnees.toml"
        )
        self.dossier_gabarits = (
            Path(dossier_gabarits)
            if dossier_gabarits is not None
            else self.racine / "config" / "prompts" / "generateur"
        )
        self.fichier_outils = (
            Path(fichier_outils)
            if fichier_outils is not None
            else self.racine / "config" / "outils-mcp.toml"
        )
        self._rendre_passages = rendre_passages
        self._outils: list[dict[str, Any]] | None = None
        self._aujourd_hui = aujourd_hui
        self.prealables = charger_prealables(
            self.fichier_donnees, modele=client.config.modele, aujourd_hui=aujourd_hui()
        )
        self.seed_run_id = seed_run_id
        self._amorces = self._charger_amorces(seed_run_id)
        self.plafonds_mots = charger_plafonds_mots(self.fichier_donnees)

    # --- Chargements ---------------------------------------------------------------------

    def _charger_amorces(self, seed_run_id: str) -> dict[str, Amorce]:
        chemin = self.racine / "runs" / TYPE_RUN_SEED / seed_run_id / NOM_AMORCES
        try:
            texte = lire(chemin, "data", racine=self.racine).decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ProvenanceInvalide(
                f"artefact seed {seed_run_id} illisible ({type(exc).__name__})"
            ) from None
        amorces: dict[str, Amorce] = {}
        for numero, ligne in enumerate(texte.split("\n"), start=1):
            if not ligne.strip():
                continue
            try:
                amorce = Amorce.model_validate_json(ligne)
            except ValidationError:
                raise ProvenanceInvalide(
                    f"artefact seed {seed_run_id} : ligne {numero} non conforme au schéma Amorce"
                ) from None
            if amorce.amorce_id in amorces:
                raise ProvenanceInvalide(
                    f"artefact seed {seed_run_id} : amorce {amorce.amorce_id!r} en double"
                )
            amorces[amorce.amorce_id] = amorce
        return amorces

    def _journal(self) -> JournalMistral:
        return journal_pour(USAGE_GENERATION, self.client.config, self.client.dossier_journaux)

    def _gabarit(self, gabarit_id: Any, tache: str) -> tuple[GabaritValide, int]:
        if not isinstance(gabarit_id, str) or not _RE_GABARIT_ID.fullmatch(gabarit_id):
            raise GabaritInvalide("identifiant de gabarit invalide (attendu : [a-z0-9-]+)")
        chemin = self.dossier_gabarits / f"{gabarit_id}.md"
        if not chemin.is_file():
            raise GabaritInvalide(f"gabarit {gabarit_id!r} introuvable")
        gabarit = valider_gabarit(chemin, cles_optionnelles=CLES_OPTIONNELLES_GABARIT)
        if gabarit.id != gabarit_id:
            raise GabaritInvalide(f"gabarit {gabarit_id!r} : front-matter id différent")
        if gabarit.front_matter.get("tache") != tache:
            raise GabaritInvalide(f"gabarit {gabarit_id!r} : tâche différente de {tache!r}")
        brut = gabarit.front_matter.get("max_tokens")
        if brut is None:
            max_tokens = MAX_TOKENS_DEFAUT
        elif _RE_ENTIER.fullmatch(brut):
            max_tokens = int(brut)
        else:
            raise GabaritInvalide(f"gabarit {gabarit_id!r} : max_tokens entier positif attendu")
        utilises = set(_RE_EMPLACEMENT.findall(gabarit.consigne))
        if utilises != set(gabarit.emplacements):
            raise GabaritInvalide(
                f"gabarit {gabarit_id!r} : emplacements de la consigne et déclarés différents"
            )
        if EMPLACEMENT_PLAFOND_TACHE in gabarit.emplacements and tache not in self.plafonds_mots:
            raise GabaritInvalide(
                f"gabarit {gabarit_id!r} : « plafond_mots_tache » sans valeur pour la tâche "
                f"{tache!r} dans [generateur.plafonds_mots] de {self.fichier_donnees.name}"
            )
        return gabarit, max_tokens

    def max_tokens(self, gabarit_id: str, tache: str) -> int:
        """`max_tokens` du gabarit `gabarit_id` (défaut `MAX_TOKENS_DEFAUT`), avec les
        contrôles de `generer` ; lève `GabaritInvalide`."""
        return self._gabarit(gabarit_id, tache)[1]

    def gabarit(self, gabarit_id: str, tache: str) -> GabaritValide:
        """Gabarit `gabarit_id` validé pour `tache` (identifiant, version, SHA, emplacements),
        avec les contrôles de `generer` ; lève `GabaritInvalide`."""
        return self._gabarit(gabarit_id, tache)[0]

    def outils(self) -> list[dict[str, Any]]:
        """Outils envoyés aux Tâches outillées : `[[outils]]` de `fichier_outils` au format
        `tools` d'OpenAI (copies). Lève `ConfigurationInvalide` si le fichier est illisible."""
        if self._outils is None:
            try:
                donnees = tomllib.loads(self.fichier_outils.read_bytes().decode("utf-8"))
            except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
                raise ConfigurationInvalide(
                    f"{self.fichier_outils} : outils illisibles ({type(exc).__name__})"
                ) from None
            self._outils = _outils_openai(donnees)
        return copy.deepcopy(self._outils)

    # --- Contrôles -----------------------------------------------------------------------

    def _resoudre_amorces(
        self, amorce_ids: Any, tache: str, gabarit: GabaritValide
    ) -> tuple[tuple[str, ...], dict[str, str]]:
        """Identifiants contrôlés et valeur de chaque emplacement (amorces jointes)."""
        if isinstance(amorce_ids, (str, bytes)) or not isinstance(amorce_ids, Sequence):
            raise ProvenanceInvalide("amorce_ids : liste d'identifiants attendue")
        ids = tuple(amorce_ids)
        if not ids:
            raise ProvenanceInvalide("amorce_ids vide")
        if len(set(ids)) != len(ids):
            raise ProvenanceInvalide("amorce_ids : identifiant en double")
        journal: JournalMistral | None = None
        groupes: dict[str, list[str]] = {}
        for amorce_id in ids:
            amorce = self._amorces.get(amorce_id) if isinstance(amorce_id, str) else None
            if amorce is None:
                raise ProvenanceInvalide("amorce inconnue de l'artefact seed")
            if amorce.tache != tache:
                raise ProvenanceInvalide(f"amorce {amorce_id!r} : tâche différente de {tache!r}")
            if amorce.emplacement in (EMPLACEMENT_PLAFOND, EMPLACEMENT_PLAFOND_TACHE):
                raise ProvenanceInvalide(
                    f"amorce {amorce_id!r} : l'emplacement « {amorce.emplacement} » est dérivé "
                    "de la configuration"
                )
            if amorce.emplacement == EMPLACEMENT_PASSAGES:
                raise ProvenanceInvalide(
                    f"amorce {amorce_id!r} : l'emplacement « passages » est réservé aux "
                    "passages de l'Index"
                )
            if sha256_hex(amorce.texte) != amorce.sha_texte:
                raise ProvenanceInvalide(f"amorce {amorce_id!r} : sha_texte faux")
            if amorce.auteur_contenu == "anael":
                raise ProvenanceInvalide(
                    f"amorce {amorce_id!r} : auteur_contenu « anael » refusé (décision différée)"
                )
            if amorce.auteur_contenu == "mistral":
                journal = journal or self._journal()
                self._verifier_amorce_mistral(amorce, journal)
            if amorce.auteur_contenu == "config" and amorce.lie_a not in ids:
                raise ProvenanceInvalide(
                    f"amorce {amorce_id!r} : paramètre sans son amorce liée dans l'appel"
                )
            if amorce.emplacement not in gabarit.emplacements:
                raise GabaritInvalide(
                    f"amorce {amorce_id!r} : emplacement {amorce.emplacement!r} non déclaré "
                    f"par le gabarit {gabarit.id!r}"
                )
            groupes.setdefault(amorce.emplacement, []).append(amorce.texte)
        manquants = [
            nom
            for nom in gabarit.emplacements
            if nom not in groupes and nom not in EMPLACEMENTS_RESERVES
        ]
        if manquants:
            raise GabaritInvalide(
                f"gabarit {gabarit.id!r} : emplacement(s) sans amorce : {', '.join(manquants)}"
            )
        return ids, {nom: "\n\n".join(textes) for nom, textes in groupes.items()}

    def _ligne_admise(self, ligne: LigneAppel | None) -> bool:
        """Ligne `generation`/`ok` dont le modèle résolu est dans `modeles_stables` (un appel
        refusé par `ModeleMistralRefuse` reste journalisé `ok` mais n'est jamais réutilisé)."""
        return (
            ligne is not None
            and ligne.usage == USAGE_GENERATION
            and ligne.statut == "ok"
            and ligne.modele_resolu in self.prealables.modeles_stables
        )

    def _verifier_amorce_mistral(self, amorce: Amorce, journal: JournalMistral) -> None:
        ligne = journal.lire(amorce.appel_id or "")
        if ligne is None or not self._ligne_admise(ligne):
            raise ProvenanceInvalide(
                f"amorce {amorce.amorce_id!r} : appel Mistral absent du journal, non « ok » "
                "ou d'un modèle hors modeles_stables"
            )
        contenu = message_assistant(ligne.reponse_brute).get("content")
        if not texte_mistral_conforme(contenu, amorce):
            raise ProvenanceInvalide(
                f"amorce {amorce.amorce_id!r} : texte différent de la réponse journalisée"
            )

    def reponse_journalisee(
        self, gabarit_id: str, amorce_ids: Sequence[str], session_id: str, tache: str
    ) -> LigneAppel | None:
        """Première ligne admise du journal de `session_id` pour ce gabarit (identifiant,
        version, SHA) et ces amorces, sans message précédent : la reprise la réutilise au
        lieu d'appeler Mistral. `None` s'il n'y en a pas."""
        gabarit = self._gabarit(gabarit_id, tache)[0]
        journal = self._journal()
        if not journal.chemin.is_file():
            return None
        ids = json_canonique(list(amorce_ids)).decode("utf-8")
        for ligne in journal.appels_session(session_id):
            if (
                self._ligne_admise(ligne)
                and (ligne.gabarit_id, ligne.version_gabarit, ligne.sha256_gabarit)
                == (gabarit.id, gabarit.version, gabarit.sha256)
                and ligne.amorce_ids == ids
                and ligne.reponse_brute is not None
            ):
                return ligne
        return None

    def deriver_amorce(
        self, appel_id: str, *, amorce_id: str, tache: str, emplacement: str
    ) -> Amorce:
        """Amorce `mistral` tirée de la réponse journalisée `appel_id`, connue ensuite de
        `generer` (CR en deux temps : la transcription devient l'amorce du compte rendu).

        L'appel doit être `generation`/`ok` d'un modèle stable, non tronqué, et sa réponse un
        contenu texte sans appel d'outil. Idempotent pour un même `amorce_id` et le même
        texte ; lève `ProvenanceInvalide` sinon (rien n'est enregistré).
        """
        if emplacement == EMPLACEMENT_PASSAGES:
            raise ProvenanceInvalide("l'emplacement « passages » est réservé à l'Index")
        ligne = self._journal().lire(appel_id) if isinstance(appel_id, str) else None
        if ligne is None or not self._ligne_admise(ligne):
            raise ProvenanceInvalide(
                "amorce dérivée : appel absent du journal, non « ok » ou d'un modèle hors "
                "modeles_stables"
            )
        message = message_assistant(ligne.reponse_brute)
        texte = message.get("content")
        if "tool_calls" in message or not isinstance(texte, str):
            raise ProvenanceInvalide(f"amorce dérivée de {appel_id} : contenu texte seul attendu")
        if raison_de_fin(ligne.reponse_brute) == "length":
            raise ProvenanceInvalide(f"amorce dérivée de {appel_id} : réponse tronquée")
        try:
            amorce = Amorce(
                schema_version=1,
                amorce_id=amorce_id,
                tache=tache,
                emplacement=emplacement,
                texte=texte,
                sha_texte=sha256_hex(texte),
                auteur_contenu="mistral",
                appel_id=appel_id,
            )
        except ValidationError:
            raise ProvenanceInvalide("amorce dérivée non conforme au schéma Amorce") from None
        existante = self._amorces.get(amorce.amorce_id)
        if existante is not None and existante != amorce:
            raise ProvenanceInvalide(
                f"amorce {amorce.amorce_id!r} déjà connue avec une autre provenance"
            )
        self._amorces[amorce.amorce_id] = amorce
        return amorce

    def _precedents(
        self, messages: Sequence[Mapping[str, Any]] | None, session_id: str
    ) -> list[dict[str, Any]]:
        if messages is None:
            return []
        if isinstance(messages, (str, bytes)) or not isinstance(messages, Sequence):
            raise ProvenanceInvalide("messages_precedents : liste de messages attendue")
        reponses: set[bytes] | None = None
        cassettes: list[Cassette] | None = None
        admis: list[dict[str, Any]] = []
        appels: dict[Any, Mapping[str, Any]] = {}  # appels d'outil des assistants admis
        for indice, message in enumerate(messages):
            if not isinstance(message, Mapping):
                raise ProvenanceInvalide(f"message précédent {indice} : objet attendu")
            role = message.get("role")
            if role == "assistant":
                if reponses is None:
                    reponses = self._reponses_session(session_id)
                normalise = _normaliser_assistant(message)
                if json_canonique(normalise) not in reponses:
                    raise ProvenanceInvalide(
                        f"message précédent {indice} : réponse assistant non journalisée "
                        "dans cette session"
                    )
                admis.append(normalise)
                for appel in normalise.get("tool_calls") or ():
                    if isinstance(appel, Mapping) and isinstance(appel.get("id"), str):
                        appels[appel["id"]] = appel
            elif role == "tool":
                appel = appels.get(message.get("tool_call_id"))
                if appel is None:
                    raise ProvenanceInvalide(
                        f"message précédent {indice} : tool_call_id sans appel d'outil admis"
                    )
                if cassettes is None:
                    cassettes = self._cassettes(session_id)
                if not any(self._resultat_de_cassette(message, appel, c) for c in cassettes):
                    raise ProvenanceInvalide(
                        f"message précédent {indice} : résultat d'outil absent de la cassette "
                        "de cette session"
                    )
                admis.append(dict(message))
            else:
                raise ProvenanceInvalide(
                    f"message précédent {indice} : rôle {role!r} refusé (assistant ou tool)"
                )
        return admis

    def _reponses_session(self, session_id: str) -> set[bytes]:
        reponses: set[bytes] = set()
        for ligne in self._journal().appels_session(session_id):
            if self._ligne_admise(ligne):
                reponses.add(json_canonique(self._message_journalise(ligne)))
        return reponses

    @staticmethod
    def _message_journalise(ligne: LigneAppel) -> dict[str, Any]:
        try:
            return message_assistant(ligne.reponse_brute)
        except ProvenanceInvalide:
            return {}

    def _cassettes(self, session_id: str) -> list[Cassette]:
        """Cassettes de la session : `<session_id>.json` s'il existe, puis les segments
        `<session_id>.t1.json`, `.t2.json`… jusqu'au premier absent."""
        dossier = self.racine / "data" / "cassettes"
        chemins = []
        if (dossier / f"{session_id}.json").is_file():
            chemins.append(dossier / f"{session_id}.json")
        tour = 1
        while (dossier / f"{session_id}.t{tour}.json").is_file():
            chemins.append(dossier / f"{session_id}.t{tour}.json")
            tour += 1
        if not chemins:
            raise ProvenanceInvalide(f"cassette de la session {session_id!r} absente")
        cassettes = []
        for chemin in chemins:
            try:
                octets = lire(chemin, "data", racine=self.racine)
            except OSError:
                raise ProvenanceInvalide(f"cassette {chemin.name} illisible") from None
            try:
                cassettes.append(Cassette.model_validate_json(octets))
            except ValidationError:
                raise ProvenanceInvalide(f"cassette {chemin.name} invalide") from None
        return cassettes

    @staticmethod
    def _resultat_de_cassette(
        message: Mapping[str, Any], appel: Mapping[str, Any], cassette: Cassette
    ) -> bool:
        """Vrai si une interaction `tools/call` de la cassette répond à `appel` (même nom de
        fonction, mêmes arguments une fois décodés) avec exactement le `content` du message."""
        contenu = message.get("content")
        if not isinstance(contenu, str):
            return False
        fonction = appel.get("function")
        if not isinstance(fonction, Mapping):
            return False
        nom = fonction.get("name")
        arguments = fonction.get("arguments")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except ValueError:
                return False
        if message.get("name") is not None and message.get("name") != nom:
            return False
        for interaction in cassette.interactions:
            requete, reponse = interaction.request, interaction.response
            if requete.get("method") != "tools/call" or not isinstance(reponse, Mapping):
                continue
            if "result" not in reponse:
                continue
            params = requete.get("params")
            if not isinstance(params, Mapping) or params.get("name") != nom:
                continue
            if params.get("arguments", {}) != arguments:  # MCP : `arguments` facultatif
                continue
            if contenu in _textes_resultat(reponse["result"]):
                return True
        return False

    # --- Appel ---------------------------------------------------------------------------

    @staticmethod
    def _plafond_mots(valeurs: Mapping[str, str], gabarit_id: str) -> str:
        """Plafond de mots de la `longueur_demandee` de l'appel (clés de `[re.longueurs]`)."""
        plafond = plafonds_re_evaluation().get(valeurs.get("longueur_demandee", ""))
        if plafond is None:
            raise GabaritInvalide(
                f"gabarit {gabarit_id!r} : « plafond_mots » exige une amorce longueur_demandee "
                "connue de [re.longueurs]"
            )
        return str(plafond)

    def generer(
        self,
        gabarit_id: str,
        amorce_ids: Sequence[str],
        session_id: str,
        tache: str,
        messages_precedents: Sequence[Mapping[str, Any]] | None = None,
    ) -> Generation:
        """Appelle Mistral sur le gabarit `gabarit_id` rempli par les amorces `amorce_ids`.

        Lève, avant tout appel : `GabaritInvalide` (identifiant, fichier, tâche, emplacements),
        `ProvenanceInvalide` (amorces, messages précédents, session). Après l'appel :
        `ModeleMistralRefuse` si le modèle résolu sort de `modeles_stables` (appel journalisé),
        et les erreurs du client (`BudgetEpuise`, `ErreurApiMistral`). `PrealableNonSatisfait`
        si le jour a changé depuis la vérification des conditions Mistral (D1.2).
        """
        aujourd_hui = self._aujourd_hui()
        if self.prealables.conditions_verifiees_le != aujourd_hui:
            raise PrealableNonSatisfait(
                f"conditions Mistral vérifiées le {self.prealables.conditions_verifiees_le}, "
                f"pas aujourd'hui ({aujourd_hui}) : génération refusée"
            )
        if tache not in TACHES:
            raise GabaritInvalide(f"tâche {tache!r} non générable (attendu : {', '.join(TACHES)})")
        if not isinstance(session_id, str) or not _RE_SESSION_ID.fullmatch(session_id):
            raise ProvenanceInvalide("session_id invalide (attendu : [A-Za-z0-9][A-Za-z0-9_-]*)")
        gabarit, max_tokens = self._gabarit(gabarit_id, tache)
        ids, valeurs = self._resoudre_amorces(amorce_ids, tache, gabarit)
        if EMPLACEMENT_PASSAGES in gabarit.emplacements:
            if self._rendre_passages is None:
                raise ProvenanceInvalide(
                    f"gabarit {gabarit.id!r} : emplacement « passages » sans rendu de "
                    "passages injecté"
                )
            rendu = self._rendre_passages(session_id)
            if not isinstance(rendu, str) or not rendu:
                raise ProvenanceInvalide(f"session {session_id!r} : rendu des passages vide")
            valeurs[EMPLACEMENT_PASSAGES] = rendu
        if EMPLACEMENT_PLAFOND in gabarit.emplacements:
            valeurs[EMPLACEMENT_PLAFOND] = self._plafond_mots(valeurs, gabarit.id)
        if EMPLACEMENT_PLAFOND_TACHE in gabarit.emplacements:
            valeurs[EMPLACEMENT_PLAFOND_TACHE] = str(self.plafonds_mots[tache])
        consigne = _RE_EMPLACEMENT.sub(lambda m: valeurs[m.group(1)], gabarit.consigne)
        requete = [
            {"role": "user", "content": consigne},
            *self._precedents(messages_precedents, session_id),
        ]
        try:
            valider_conversation(requete)
        except ConversationInvalide as exc:
            raise ProvenanceInvalide(f"requête du générateur invalide : {exc}") from None
        outils = self.outils() if tache in TACHES_OUTILLEES else None
        caracteres = sum(len(json_canonique(m).decode("utf-8")) for m in requete)
        if outils is not None:
            caracteres += len(json_canonique(outils).decode("utf-8"))
        reponse = self.client._appeler(
            USAGE_GENERATION,
            session_id,
            requete,
            max_tokens=max_tokens,
            tokens_entree_estimes=math.ceil(caracteres / CARACTERES_PAR_TOKEN),
            jeton=_JETON,
            complements_journal={
                "gabarit_id": gabarit.id,
                "version_gabarit": gabarit.version,
                "sha256_gabarit": gabarit.sha256,
                "amorce_ids": list(ids),
            },
            tools=outils,
            tool_choice=TOOL_CHOICE if outils is not None else None,
        )
        if reponse.modele_resolu not in self.prealables.modeles_stables:
            raise ModeleMistralRefuse(
                f"modèle résolu {reponse.modele_resolu!r} absent de modeles_stables "
                f"({self.prealables.fichier.name}) ; appel {reponse.appel_id} journalisé"
            )
        ligne = self._journal().lire(reponse.appel_id)
        if ligne is None or ligne.reponse_brute is None:
            raise ProvenanceInvalide(
                f"appel {reponse.appel_id} : réponse brute introuvable au journal"
            )
        return Generation(
            appel_id=reponse.appel_id,
            session_id=session_id,
            tache=tache,
            gabarit_id=gabarit.id,
            version_gabarit=gabarit.version,
            sha256_gabarit=gabarit.sha256,
            amorce_ids=ids,
            messages=tuple(requete),
            reponse=reponse,
            reponse_brute=ligne.reponse_brute,
        )
