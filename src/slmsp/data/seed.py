"""Étape `seed` : amorces publiques ou Mistral, exclusion anti-fuite (story 9.3, FR-29, AD-3).

Une amorce est un texte inséré tel quel dans un emplacement d'un gabarit du Générateur
(`slmsp.mistral.generateur`). Ce module en constitue l'ensemble `amorces.jsonl` d'un run
`data-seed`, selon le verrou 5 d'AD-3 : une amorce est soit une ligne d'un jeu public
relue sur disque (`jeu`, `revision`, `ligne`, `sha_texte`), soit une réponse Mistral
journalisée (`appel_id`). Aucun paramètre ne désigne un fichier d'amorces : les seules
entrées sont la table de règles `REGLES` et les jeux de `config/sources.toml`, épinglés par
révision et SHA-256 (le CLI les convertit en `JeuPublic`).

- **Licences** : chaque jeu utilisé passe `RegistreLicences.exiger(depot, "recherche")`
  avant la création du run (`UsageInterdit` pour `evaluation_seulement`,
  `SourceSansLicence` si absent).
- **Lectures (AD-24)** : les octets d'un jeu sont lus par `core.artefacts.lire`, leur SHA-256
  est contrôlé contre la configuration, puis un `Decodeur` injecté les décode (la vraie
  implémentation, qui utilise pyarrow, vit dans `slmsp.cli.data`).
- **Anti-fuite** : le Jeu d'évaluation n'est vu que par `core.items` (`Protection`). Un
  candidat est exclu, avec son motif, s'il reprend une `amorce_usager` (SHA du texte
  normalisé), une URL de provenance, un `dataset_id` ou un `resource_id`, ou si son
  recouvrement de n-grammes hachés avec un item atteint le seuil. Le recouvrement est le
  coefficient d'inclusion `|A ∩ B| / min(|A|, |B|)`, au moins égal au Jaccard donc plus
  prudent.
- **Sélection déterministe** : candidats dédoublonnés par texte normalisé, bornés en
  longueur, triés par SHA-256 de `<tache>.<emplacement>\\0<texte normalisé>`, examinés dans
  cet ordre jusqu'à `volumes[tache] x facteur` amorces conservées.
- **Scénarios** (opt-in, `nb_scenarios > 0`) : pour les premiers thèmes `CR/theme` conservés,
  une fabrique injectée appelle Mistral et renvoie `(appel_id, texte)` ; l'amorce
  `CR/scenario` correspondante porte `auteur_contenu = "mistral"` et cet `appel_id`.
- **Courriers types** (opt-in, `nb_courriers > 0`, décision A2b) : pour les premiers sujets
  `CT/sujet` conservés, une fabrique injectée appelle Mistral sur le gabarit `amorces-ct`
  (consignes seules, D1.1) et renvoie `(appel_id, contenu)`. Le contenu est un objet JSON dont
  les clés `type_courrier`, `objet` et `elements_connus` deviennent trois amorces `mistral`
  de même `appel_id` (un groupe pour `generate`), après contrôle du schéma, déduplication
  par objet normalisé et anti-fuite de chaque valeur.
- **Longueurs RE** : chaque texte `RE/texte` conservé reçoit une amorce `config`
  `RE/longueur_demandee` (`<n> mots`, `lie_a` = l'amorce du texte), `n` tiré par graine dans
  `[seed].re_longueurs_mots` de `config/donnees.toml` : un paramètre, pas un contenu.

Le run `data-seed` contient `amorces.jsonl` (écrit en ajout) et `comptes.json`.
`verifier_amorces` relit un `amorces.jsonl` : schéma (provenance complète), `sha_texte`,
ligne publique relue dans le jeu. L'`appel_id` d'une amorce Mistral est contrôlé au journal
par le Générateur lors de son utilisation.
"""

from __future__ import annotations

import json
import random
import re
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Final

from pydantic import ValidationError

from slmsp.core.artefacts import Run, lire, nouveau_run
from slmsp.core.canonique import sha256_hex
from slmsp.core.erreurs import (
    BudgetEpuise,
    ConfigurationInvalide,
    ProvenanceInvalide,
)
from slmsp.core.items import (
    LONGUEUR_EMPREINTE,
    chemins_jeu,
    empreintes_antifuite,
    identifiants_proteges,
)
from slmsp.core.schemas.amorce import Amorce, texte_de_reponse
from slmsp.core.schemas.run import MOTIF_RUN_ID
from slmsp.core.texte import ngrammes, normaliser
from slmsp.data.config import ConfigDonnees
from slmsp.data.licences import RegistreLicences

__all__ = [
    "COLONNES_IDENTIFIANTS",
    "FACTEUR_DEFAUT",
    "MOTIFS_EXCLUSION",
    "REGLES",
    "SANS_SOURCE_PUBLIQUE",
    "VERSIONS_OBLIGATOIRES",
    "Decodeur",
    "FabriqueCourrier",
    "FabriqueScenario",
    "FichierJeu",
    "JeuPublic",
    "Protection",
    "RegleAmorce",
    "ResultatSeed",
    "construire_protection",
    "session_courrier",
    "executer_seed",
    "verifier_amorces",
    "versions_protegees",
]

TYPE_RUN: Final = "data-seed"
NOM_AMORCES: Final = "amorces.jsonl"
NOM_COMPTES: Final = "comptes.json"
FACTEUR_DEFAUT: Final = 3
"""Amorces conservées par exemple visé : marge pour les rejets des étapes suivantes."""

VERSIONS_OBLIGATOIRES: Final = ("v1.0", "v1.1")
VERSION_CALIBRAGE: Final = "calibrage"

MOTIFS_EXCLUSION: Final = (
    "amorce_usager",
    "provenance_url",
    "dataset_id",
    "resource_id",
    "recouvrement_ngrammes",
)
"""Motifs d'exclusion d'un candidat (étape `seed`), dans l'ordre de leur contrôle."""

THEME: Final = ("CR", "theme")
SCENARIO: Final = ("CR", "scenario")
GABARIT_SCENARIO: Final = "scenario-reunion"
"""Gabarit du Générateur qui produit un scénario de réunion (utilisé par le CLI)."""

SUJET_CT: Final = ("CT", "sujet")
GABARIT_AMORCES_CT: Final = "amorces-ct"
"""Gabarit du Générateur qui produit les amorces d'un courrier type (utilisé par le CLI)."""
CHAMPS_CT: Final[tuple[tuple[str, int, int], ...]] = (
    ("type_courrier", 3, 200),
    ("objet", 10, 300),
    ("elements_connus", 20, 3000),
)
"""Clés de l'objet JSON renvoyé par Mistral (emplacements du gabarit `ct`) et bornes de
longueur, en caractères."""
LONGUEUR_RE: Final = ("RE", "longueur_demandee")
TEXTE_RE: Final = ("RE", "texte")

SANS_SOURCE_PUBLIQUE: Final[tuple[tuple[str, str], ...]] = (
    ("Q", "passages"),
    ("CT", "type_courrier"),
    ("CT", "objet"),
    ("CT", "elements_connus"),
)
"""Emplacements de gabarit sans source publique retenue (listés dans `comptes.json`) ; ceux
de CT sont remplis par Mistral quand `nb_courriers > 0`."""


# --- Jeux et règles -----------------------------------------------------------------------


@dataclass(frozen=True)
class FichierJeu:
    """Fichier d'un jeu public : chemin sur disque (sous `data/raw/`) et SHA-256 épinglé."""

    chemin: Path
    sha256: str


@dataclass(frozen=True)
class JeuPublic:
    """Jeu public épinglé : `nom` (dossier sous `data/raw/mediatech/`), dépôt, révision."""

    nom: str
    depot: str
    revision: str
    fichiers: tuple[FichierJeu, ...]


@dataclass(frozen=True)
class RegleAmorce:
    """Règle fixe : colonne d'un jeu -> (Tâche, emplacement), bornée en longueur (caractères).

    Si `sous_cle` est renseigné, la colonne contient une liste d'objets (éventuellement en
    JSON) et chaque valeur de `sous_cle` est un candidat.
    """

    jeu: str
    colonne: str
    tache: str
    emplacement: str
    longueur_min: int
    longueur_max: int
    sous_cle: str | None = None


REGLES: Final[tuple[RegleAmorce, ...]] = (
    RegleAmorce("service-public", "related_questions", "Q", "question", 15, 300, "question"),
    RegleAmorce("data-gouv-datasets-catalog", "title", "RD", "demande", 10, 200),
    RegleAmorce("service-public", "title", "CR", "theme", 10, 200),
    RegleAmorce("service-public", "text", "LC", "texte", 300, 1500),
    RegleAmorce("service-public", "text", "CO", "texte", 150, 800),
    RegleAmorce("service-public", "text", "RE", "texte", 800, 4000),
    RegleAmorce("piaf", "question", "generique", "demande", 10, 300),
    RegleAmorce("service-public", "title", "CT", "sujet", 10, 200),
)
"""Table de règles (aucun texte d'amorce : seulement des noms de colonnes et des bornes)."""

COLONNES_IDENTIFIANTS: Final[Mapping[str, tuple[str, ...]]] = {
    "service-public": ("url", "doc_id", "chunk_id"),
    "data-gouv-datasets-catalog": ("url", "doc_id", "chunk_id"),
}
"""Colonnes d'identification lues pour l'exclusion par identifiant, par jeu (défaut : aucune)."""

_COLONNES_URL: Final = ("url",)
_COLONNES_ID: Final = ("doc_id", "chunk_id")

Decodeur = Callable[[bytes, Sequence[str]], Iterable[Mapping[str, Any]]]
"""`(octets d'un fichier parquet, colonnes) -> lignes`, chaque ligne étant `{colonne: valeur}`.
Injecté : `slmsp.data` ne décode pas le parquet lui-même (AD-24)."""

FabriqueScenario = Callable[[str, str, str], tuple[str, str]]
"""`(seed_run_id, amorce_id du thème, session_id) -> (appel_id, texte du scénario)`."""

FabriqueCourrier = Callable[[str, str, str], tuple[str, str]]
"""`(seed_run_id, amorce_id du sujet, session_id) -> (appel_id, contenu JSON de la réponse)`.
La session est stable d'un run à l'autre (`session_courrier`) : la fabrique réutilise une
réponse déjà journalisée au lieu de rappeler Mistral."""


def session_courrier(sujet: Amorce) -> str:
    """Session Mistral d'un sujet CT, stable d'un run à l'autre (reprise sans nouvel appel)."""
    return "seed-ct-" + sha256_hex(f"{sujet.amorce_id}\0{sujet.sha_texte}")[:24]


# --- Protection anti-fuite ----------------------------------------------------------------


def versions_protegees(racine: str | Path) -> tuple[str, ...]:
    """`("v1.0", "v1.1")`, plus `"calibrage"` si son échantillon existe sous `racine`."""
    versions = VERSIONS_OBLIGATOIRES
    if chemins_jeu(VERSION_CALIBRAGE, racine)[1].is_file():
        versions = (*versions, VERSION_CALIBRAGE)
    return versions


def _empreintes_texte(texte: str, n: int) -> Iterator[str]:
    """Mêmes empreintes que `core.items.empreintes_antifuite` pour un texte (pas de texte
    rendu) : SHA-256 tronqué de chaque n-gramme ; moins de `n` mots : tuple entier."""
    grammes = ngrammes(texte, n)
    if not grammes:
        jetons = tuple(normaliser(texte).split())
        grammes = [jetons] if jetons else []
    for gramme in grammes:
        yield sha256_hex(" ".join(gramme))[:LONGUEUR_EMPREINTE]


def _url_canonique(url: str) -> str:
    """URL sans fragment ni barre finale, en minuscules (comparaison d'identifiants)."""
    return url.strip().split("#", 1)[0].rstrip("/").lower()


@dataclass(frozen=True)
class Protection:
    """Ce que les amorces ne doivent pas reprendre du Jeu d'évaluation (sans aucun texte)."""

    versions: tuple[str, ...]
    n_ngrammes: int
    seuil: float
    amorces_sha256: frozenset[str] = frozenset()
    urls: frozenset[str] = frozenset()
    dataset_ids: frozenset[str] = frozenset()
    resource_ids: frozenset[str] = frozenset()
    par_item: Mapping[str, frozenset[str]] = field(default_factory=dict)
    index: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    """Index inversé : empreinte de n-gramme -> clés `<version>/<id>` des items."""

    @classmethod
    def vide(cls, n_ngrammes: int = 5, seuil: float = 0.5) -> Protection:
        """Protection sans aucun item (tests)."""
        return cls(versions=(), n_ngrammes=n_ngrammes, seuil=seuil)

    @property
    def nb_items(self) -> int:
        return len(self.par_item)

    def recouvrement(self, texte: str) -> float:
        """Plus grand coefficient d'inclusion `|A ∩ B| / min(|A|, |B|)` avec un item."""
        empreintes = set(_empreintes_texte(texte, self.n_ngrammes))
        if not empreintes:
            return 0.0
        communs: Counter[str] = Counter()
        for empreinte in empreintes:
            for cle in self.index.get(empreinte, ()):
                communs[cle] += 1
        meilleur = 0.0
        for cle, nombre in communs.items():
            taille = min(len(empreintes), len(self.par_item[cle]))
            meilleur = max(meilleur, nombre / taille)
        return meilleur

    def motifs(self, texte: str, *, urls: Iterable[str] = (), ids: Iterable[str] = ()) -> list[str]:
        """Motifs d'exclusion d'un candidat (liste vide : il peut être conservé)."""
        motifs: list[str] = []
        if sha256_hex(normaliser(texte)) in self.amorces_sha256:
            motifs.append("amorce_usager")
        if any(_url_canonique(url) in self.urls for url in urls):
            motifs.append("provenance_url")
        valeurs = list(ids)
        if any(valeur in self.dataset_ids for valeur in valeurs):
            motifs.append("dataset_id")
        if any(valeur in self.resource_ids for valeur in valeurs):
            motifs.append("resource_id")
        if self.recouvrement(texte) >= self.seuil:
            motifs.append("recouvrement_ngrammes")
        return motifs


def construire_protection(
    versions: Iterable[str], config: ConfigDonnees, racine: str | Path
) -> Protection:
    """Protection des jeux `versions` (lus par `core.items`, rien d'autre).

    `config.anti_fuite` donne `n_ngrammes` et `seuil_jaccard`. Lève `ConfigurationInvalide`
    si le fichier d'items d'une version est absent.
    """
    versions = tuple(versions)
    for version in versions:
        if not chemins_jeu(version, racine)[1].is_file():
            raise ConfigurationInvalide(
                f"Jeu d'évaluation {version} introuvable : anti-fuite impossible"
            )
    n = config.anti_fuite.n_ngrammes
    identifiants = identifiants_proteges(versions, racine=racine)
    empreintes = empreintes_antifuite(versions, n, racine=racine)
    index: dict[str, list[str]] = {}
    for cle, grammes in empreintes.par_item.items():
        for empreinte in grammes:
            index.setdefault(empreinte, []).append(cle)
    return Protection(
        versions=versions,
        n_ngrammes=n,
        seuil=config.anti_fuite.seuil_jaccard,
        amorces_sha256=identifiants.amorces_sha256,
        urls=frozenset(_url_canonique(u) for u in identifiants.urls),
        dataset_ids=identifiants.dataset_ids,
        resource_ids=identifiants.resource_ids,
        par_item=dict(empreintes.par_item),
        index={empreinte: tuple(cles) for empreinte, cles in index.items()},
    )


# --- Lecture des jeux ---------------------------------------------------------------------


def _colonnes(jeu: JeuPublic, regles: Iterable[RegleAmorce]) -> tuple[str, ...]:
    colonnes = {r.colonne for r in regles if r.jeu == jeu.nom}
    colonnes.update(COLONNES_IDENTIFIANTS.get(jeu.nom, ()))
    return tuple(sorted(colonnes))


def _lignes_jeu(
    racine: Path, jeu: JeuPublic, colonnes: Sequence[str], decodeur: Decodeur
) -> Iterator[tuple[int, Mapping[str, Any]]]:
    """Lignes `(numéro, valeurs)` d'un jeu ; le numéro compte à travers tous ses fichiers.

    Chaque fichier est lu par `core.artefacts.lire` puis son SHA-256 est contrôlé.
    """
    numero = 0
    for fichier in jeu.fichiers:
        try:
            octets = lire(fichier.chemin, "data", racine=racine)
        except OSError:
            raise ConfigurationInvalide(
                f"jeu {jeu.nom} : fichier {fichier.chemin.name} illisible ou absent"
            ) from None
        if sha256_hex(octets) != fichier.sha256:
            raise ProvenanceInvalide(
                f"jeu {jeu.nom} : fichier {fichier.chemin.name} différent du SHA-256 épinglé"
            )
        for ligne in decodeur(octets, colonnes):
            yield numero, ligne
            numero += 1


@dataclass(frozen=True)
class _Candidat:
    cle: str
    regle: RegleAmorce
    jeu: JeuPublic
    ligne: int
    k: int | None
    texte: str
    urls: tuple[str, ...]
    ids: tuple[str, ...]


def _texte_valide(valeur: Any) -> str | None:
    return valeur.strip() if isinstance(valeur, str) and valeur.strip() else None


def _valeurs_regle(
    regle: RegleAmorce, ligne: Mapping[str, Any]
) -> list[tuple[int | None, str, str | None]]:
    """Candidats `(k, texte, url de l'élément)` de `ligne` selon `regle`, longueur contrôlée."""
    valeur = ligne.get(regle.colonne)
    bruts: list[tuple[int | None, str | None, str | None]] = []
    if regle.sous_cle is None:
        bruts.append((None, _texte_valide(valeur), None))
    else:
        elements = valeur
        if isinstance(elements, (str, bytes)):
            try:
                elements = json.loads(elements)
            except ValueError:
                elements = None
        if isinstance(elements, list):
            for k, element in enumerate(elements):
                if isinstance(element, Mapping):
                    bruts.append(
                        (
                            k,
                            _texte_valide(element.get(regle.sous_cle)),
                            _texte_valide(element.get("url")),
                        )
                    )
    return [
        (k, texte, url)
        for k, texte, url in bruts
        if texte is not None and regle.longueur_min <= len(texte) <= regle.longueur_max
    ]


def _identifiants_ligne(ligne: Mapping[str, Any]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    urls = [u for c in _COLONNES_URL if (u := _texte_valide(ligne.get(c))) is not None]
    ids: list[str] = []
    for colonne in _COLONNES_ID:
        valeur = ligne.get(colonne)
        if isinstance(valeur, (str, int)) and not isinstance(valeur, bool) and str(valeur) != "":
            ids.append(str(valeur))
    return tuple(urls), tuple(ids)


def _amorce_id(regle: RegleAmorce, jeu: JeuPublic, ligne: int, k: int | None) -> str:
    base = f"{regle.tache.lower()}.{regle.emplacement}.{jeu.nom}.{ligne}"
    return base if k is None else f"{base}.{k}"


def _amorce_publique(candidat: _Candidat) -> Amorce:
    regle = candidat.regle
    return Amorce(
        schema_version=1,
        amorce_id=_amorce_id(regle, candidat.jeu, candidat.ligne, candidat.k),
        tache=regle.tache,
        emplacement=regle.emplacement,
        texte=candidat.texte,
        sha_texte=sha256_hex(candidat.texte),
        auteur_contenu="public",
        jeu=candidat.jeu.depot,
        revision=candidat.jeu.revision,
        ligne=candidat.ligne,
    )


# --- Exécution ----------------------------------------------------------------------------


@dataclass(frozen=True)
class ResultatSeed:
    """Bilan d'un run `data-seed`."""

    run_id: str
    dossier: Path
    statut: str
    comptes: Mapping[str, Any]


def _chemin_absolu(racine: Path, chemin: Path) -> Path:
    return chemin if chemin.is_absolute() else racine / chemin


def _verifier_regles(
    regles: Sequence[RegleAmorce], jeux: Mapping[str, JeuPublic], volumes: Mapping[str, int]
) -> None:
    for regle in regles:
        if regle.jeu not in jeux:
            raise ConfigurationInvalide(f"règle d'amorce : jeu {regle.jeu!r} absent des sources")
        if regle.tache not in volumes:
            raise ConfigurationInvalide(f"règle d'amorce : tâche {regle.tache!r} sans volume")
        if not 1 <= regle.longueur_min <= regle.longueur_max:
            raise ConfigurationInvalide(
                f"règle d'amorce {regle.tache}/{regle.emplacement} : bornes de longueur invalides"
            )


def _config_run(
    *,
    jeux: Sequence[JeuPublic],
    regles: Sequence[RegleAmorce],
    config: ConfigDonnees,
    protection: Protection,
    registre: RegistreLicences,
    facteur: int,
    nb_scenarios: int,
    nb_courriers: int,
) -> dict[str, Any]:
    utilises = {r.jeu for r in regles}
    return {
        "facteur": facteur,
        "nb_scenarios": nb_scenarios,
        "nb_courriers": nb_courriers,
        "seed": config.seed.model_dump(mode="json"),
        "volumes": config.volumes.par_tache(),
        "protection": {
            "versions": list(protection.versions),
            "n_ngrammes": protection.n_ngrammes,
            "seuil": protection.seuil,
            "nb_items": protection.nb_items,
        },
        "registre_sha256": registre.sha256,
        "jeux": [
            {
                "nom": jeu.nom,
                "depot": jeu.depot,
                "revision": jeu.revision,
                "fichiers": [fichier.sha256 for fichier in jeu.fichiers],
            }
            for jeu in jeux
            if jeu.nom in utilises
        ],
        "regles": [asdict(regle) for regle in regles],
    }


def _ecrire_amorce(run: Run, amorce: Amorce) -> None:
    run.ajouter_jsonl(NOM_AMORCES, amorce.model_dump(mode="json", exclude_none=True))


def _ecrire_comptes(run: Run, comptes: Mapping[str, Any]) -> None:
    run.ecrire(
        NOM_COMPTES, json.dumps(comptes, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


def executer_seed(
    *,
    racine: str | Path,
    jeux: Sequence[JeuPublic],
    registre: RegistreLicences,
    config: ConfigDonnees,
    protection: Protection,
    decodeur: Decodeur,
    regles: Sequence[RegleAmorce] = REGLES,
    facteur: int = FACTEUR_DEFAUT,
    nb_scenarios: int = 0,
    fabrique_scenarios: FabriqueScenario | None = None,
    nb_courriers: int = 0,
    fabrique_courriers: FabriqueCourrier | None = None,
    consigner: Callable[[str], None] | None = None,
) -> ResultatSeed:
    """Constitue `runs/data-seed/<run_id>/{amorces.jsonl, comptes.json}`.

    Avant le run : licences (`UsageInterdit`, `SourceSansLicence`) et présence des fichiers
    (`ConfigurationInvalide`) ; aucun run n'est créé en cas d'échec. Pendant le run : un
    SHA-256 différent lève `ProvenanceInvalide` (run `partiel-erreur`). `BudgetEpuise`
    pendant les scénarios donne un run `partiel-budget` dont les amorces déjà écrites sont
    conservées (le résultat est renvoyé, rien n'est levé). `nb_scenarios > 0` exige
    `fabrique_scenarios` ; sans scénario, la fabrique n'est jamais appelée. De même,
    `nb_courriers > 0` exige `fabrique_courriers`, appelée au plus `nb_courriers` fois.
    """
    if not isinstance(facteur, int) or isinstance(facteur, bool) or facteur < 1:
        raise ValueError(f"facteur doit être un entier positif (reçu {facteur!r})")
    if not isinstance(nb_scenarios, int) or isinstance(nb_scenarios, bool) or nb_scenarios < 0:
        raise ValueError(f"nb_scenarios doit être un entier positif ou nul (reçu {nb_scenarios!r})")
    if nb_scenarios > 0 and fabrique_scenarios is None:
        raise ValueError("nb_scenarios > 0 exige une fabrique de scénarios")
    if not isinstance(nb_courriers, int) or isinstance(nb_courriers, bool) or nb_courriers < 0:
        raise ValueError(f"nb_courriers doit être un entier positif ou nul (reçu {nb_courriers!r})")
    if nb_courriers > 0 and fabrique_courriers is None:
        raise ValueError("nb_courriers > 0 exige une fabrique de courriers")
    consigner = consigner or (lambda _message: None)
    base = Path(racine).resolve()
    par_nom = {jeu.nom: jeu for jeu in jeux}
    volumes = config.volumes.par_tache()
    _verifier_regles(regles, par_nom, volumes)

    # Licences, puis présence des fichiers : avant tout run.
    utilises = [jeu for jeu in jeux if any(r.jeu == jeu.nom for r in regles)]
    for jeu in utilises:
        registre.exiger(jeu.depot, "recherche")
    if nb_scenarios > 0 or nb_courriers > 0:
        registre.exiger("mistral/reponses-generateur", "recherche")
    for jeu in utilises:
        for fichier in jeu.fichiers:
            if not _chemin_absolu(base, fichier.chemin).is_file():
                raise ConfigurationInvalide(
                    f"jeu {jeu.nom} non téléchargé : {fichier.chemin.name} absent "
                    "(lancer `slmsp fetch sources`)"
                )

    entrees: dict[str, str | Path] = {"registre-licences": registre.chemin}
    for jeu in utilises:
        for numero, fichier in enumerate(jeu.fichiers):
            entrees[f"{jeu.nom}-{numero}"] = _chemin_absolu(base, fichier.chemin)
    run = nouveau_run(
        TYPE_RUN,
        "seed",
        _config_run(
            jeux=jeux,
            regles=regles,
            config=config,
            protection=protection,
            registre=registre,
            facteur=facteur,
            nb_scenarios=nb_scenarios,
            nb_courriers=nb_courriers,
        ),
        entrees=entrees,
        racine=base,
    )
    consigner(f"run {run.run_id}")
    try:
        comptes = _remplir(
            run,
            base=base,
            utilises=utilises,
            regles=regles,
            volumes=volumes,
            protection=protection,
            decodeur=decodeur,
            facteur=facteur,
            nb_scenarios=nb_scenarios,
            fabrique=fabrique_scenarios,
            longueurs_re=tuple(config.seed.re_longueurs_mots),
            graine=config.seed.graine,
            nb_courriers=nb_courriers,
            fabrique_courriers=fabrique_courriers,
            consigner=consigner,
        )
    except KeyboardInterrupt:
        run.terminer("interrompu", "KeyboardInterrupt")
        raise
    except Exception as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {str(exc)[:200]}")
        raise
    statut = comptes["statut"]
    _ecrire_comptes(run, comptes)
    run.terminer(statut, "BudgetEpuise" if statut == "partiel-budget" else None)
    return ResultatSeed(run.run_id, run.dossier, statut, comptes)


def _remplir(
    run: Run,
    *,
    base: Path,
    utilises: Sequence[JeuPublic],
    regles: Sequence[RegleAmorce],
    volumes: Mapping[str, int],
    protection: Protection,
    decodeur: Decodeur,
    facteur: int,
    nb_scenarios: int,
    fabrique: FabriqueScenario | None,
    longueurs_re: Sequence[int],
    graine: int,
    nb_courriers: int,
    fabrique_courriers: FabriqueCourrier | None,
    consigner: Callable[[str], None],
) -> dict[str, Any]:
    """Collecte, sélection et écriture des amorces ; renvoie le contenu de `comptes.json`."""
    groupes: dict[tuple[str, str], dict[str, _Candidat]] = {}
    for regle in regles:
        groupes.setdefault((regle.tache, regle.emplacement), {})

    # 1. Collecte : un seul passage sur chaque jeu, toutes ses règles appliquées.
    for jeu in utilises:
        regles_jeu = [r for r in regles if r.jeu == jeu.nom]
        colonnes = _colonnes(jeu, regles_jeu)
        consigner(f"lecture du jeu {jeu.nom}")
        for numero, ligne in _lignes_jeu(base, jeu, colonnes, decodeur):
            urls_ligne, ids = _identifiants_ligne(ligne)
            for regle in regles_jeu:
                for k, texte, url in _valeurs_regle(regle, ligne):
                    norme = normaliser(texte)
                    if not norme:
                        continue
                    groupe = groupes[(regle.tache, regle.emplacement)]
                    empreinte_norme = sha256_hex(norme)
                    if empreinte_norme in groupe:
                        continue
                    groupe[empreinte_norme] = _Candidat(
                        cle=sha256_hex(f"{regle.tache}.{regle.emplacement}\0{norme}"),
                        regle=regle,
                        jeu=jeu,
                        ligne=numero,
                        k=k,
                        texte=texte,
                        urls=(*urls_ligne, *((url,) if url else ())),
                        ids=ids,
                    )

    # 2. Sélection déterministe et écriture en ajout.
    taches: dict[str, dict[str, Any]] = {}
    conservees: dict[tuple[str, str], list[Amorce]] = {}
    for groupe_cle, candidats in groupes.items():
        tache, emplacement = groupe_cle
        cible = volumes[tache] * facteur
        exclusions = dict.fromkeys(MOTIFS_EXCLUSION, 0)
        retenues: list[Amorce] = []
        examines = exclus = 0
        for candidat in sorted(
            candidats.values(),
            key=lambda c: (c.cle, c.jeu.nom, c.ligne, -1 if c.k is None else c.k),
        ):
            if len(retenues) >= cible:
                break
            examines += 1
            motifs = protection.motifs(candidat.texte, urls=candidat.urls, ids=candidat.ids)
            if motifs:
                exclus += 1
                for motif in motifs:
                    exclusions[motif] += 1
                continue
            amorce = _amorce_publique(candidat)
            _ecrire_amorce(run, amorce)
            retenues.append(amorce)
        conservees[groupe_cle] = retenues
        taches.setdefault(tache, {})[emplacement] = {
            "cible": cible,
            "conservees": len(retenues),
            "manque": max(cible - len(retenues), 0),
            "candidats": len(candidats),
            "examines": examines,
            "exclus": exclus,
            "exclusions": exclusions,
            "jeux": sorted({c.jeu.depot for c in candidats.values()}),
        }
        consigner(f"{tache}/{emplacement} : {len(retenues)}/{cible} amorces, {exclus} exclues")

    # 3. Scénarios Mistral (opt-in).
    scenarios = _scenarios(
        run,
        themes=conservees.get(THEME, []),
        nb_scenarios=nb_scenarios,
        fabrique=fabrique,
        protection=protection,
        consigner=consigner,
    )
    # 4. Longueurs RE (paramètre de configuration tiré par graine).
    longueurs = _longueurs_re(run, conservees.get(TEXTE_RE, []), longueurs_re, graine)
    # 5. Amorces CT par Mistral (opt-in).
    courriers = _courriers(
        run,
        sujets=conservees.get(SUJET_CT, []),
        nb_courriers=nb_courriers,
        fabrique=fabrique_courriers,
        protection=protection,
        consigner=consigner,
    )
    epuise = scenarios.pop("budget_epuise") | courriers.pop("budget_epuise")
    statut = "partiel-budget" if epuise else "complet"
    return {
        "schema_version": 1,
        "run_id": run.run_id,
        "statut": statut,
        "facteur": facteur,
        "protection": {
            "versions": list(protection.versions),
            "n_ngrammes": protection.n_ngrammes,
            "seuil": protection.seuil,
            "nb_items": protection.nb_items,
        },
        "taches": taches,
        "scenarios": scenarios,
        "courriers": courriers,
        "longueurs_re": longueurs,
        "sans_source_publique": [
            {"tache": tache, "emplacement": emplacement}
            for tache, emplacement in SANS_SOURCE_PUBLIQUE
        ],
    }


def _scenarios(
    run: Run,
    *,
    themes: Sequence[Amorce],
    nb_scenarios: int,
    fabrique: FabriqueScenario | None,
    protection: Protection,
    consigner: Callable[[str], None],
) -> dict[str, Any]:
    bilan: dict[str, Any] = {
        "demandes": nb_scenarios,
        "themes_disponibles": len(themes),
        "produits": 0,
        "exclus": 0,
        "exclusions": dict.fromkeys(MOTIFS_EXCLUSION, 0),
        "budget_epuise": False,
    }
    if nb_scenarios == 0 or fabrique is None:
        return bilan
    prefixe = f"{THEME[0].lower()}.{THEME[1]}."
    for numero, theme in enumerate(themes[:nb_scenarios], start=1):
        session_id = f"{run.run_id}-scenario-{numero:03d}"
        try:
            appel_id, texte = fabrique(run.run_id, theme.amorce_id, session_id)
        except BudgetEpuise:
            bilan["budget_epuise"] = True
            consigner("budget épuisé : scénarios interrompus")
            break
        motifs = protection.motifs(texte)
        if motifs:
            bilan["exclus"] += 1
            for motif in motifs:
                bilan["exclusions"][motif] += 1
            continue
        suffixe = theme.amorce_id.removeprefix(prefixe)
        try:
            amorce = Amorce(
                schema_version=1,
                amorce_id=f"{SCENARIO[0].lower()}.{SCENARIO[1]}.{suffixe}",
                tache=SCENARIO[0],
                emplacement=SCENARIO[1],
                texte=texte,
                sha_texte=sha256_hex(texte),
                auteur_contenu="mistral",
                appel_id=appel_id,
            )
        except ValidationError:
            raise ProvenanceInvalide(
                f"scénario du thème {theme.amorce_id!r} : réponse de la fabrique non conforme"
            ) from None
        _ecrire_amorce(run, amorce)
        bilan["produits"] += 1
    consigner(f"scénarios : {bilan['produits']}/{nb_scenarios}")
    return bilan


def _longueurs_re(
    run: Run, textes: Sequence[Amorce], longueurs: Sequence[int], graine: int
) -> dict[str, Any]:
    """Une amorce `config` `RE/longueur_demandee` par texte RE, tirée par graine."""
    tirees: Counter[int] = Counter()
    for texte in textes:
        mots = random.Random(f"{graine}\0{texte.amorce_id}").choice(list(longueurs))
        valeur = f"{mots} mots"
        suffixe = texte.amorce_id.removeprefix(f"{TEXTE_RE[0].lower()}.{TEXTE_RE[1]}.")
        _ecrire_amorce(
            run,
            Amorce(
                schema_version=1,
                amorce_id=f"{LONGUEUR_RE[0].lower()}.{LONGUEUR_RE[1]}.{suffixe}",
                tache=LONGUEUR_RE[0],
                emplacement=LONGUEUR_RE[1],
                texte=valeur,
                sha_texte=sha256_hex(valeur),
                auteur_contenu="config",
                lie_a=texte.amorce_id,
            ),
        )
        tirees[mots] += 1
    return {
        "produites": sum(tirees.values()),
        "par_longueur": {str(mots): n for mots, n in sorted(tirees.items())},
    }


def _champs_courrier(contenu: str) -> dict[str, str] | None:
    """Valeurs des clés de `CHAMPS_CT` dans l'objet JSON de `contenu`, bornes comprises."""
    valeurs: dict[str, str] = {}
    for champ, minimum, maximum in CHAMPS_CT:
        valeur = texte_de_reponse(contenu, champ)
        if valeur is None or not minimum <= len(valeur) <= maximum:
            return None
        valeurs[champ] = valeur
    return valeurs


def _courriers(
    run: Run,
    *,
    sujets: Sequence[Amorce],
    nb_courriers: int,
    fabrique: FabriqueCourrier | None,
    protection: Protection,
    consigner: Callable[[str], None],
) -> dict[str, Any]:
    """Amorces CT d'au plus `nb_courriers` appels Mistral, un par sujet conservé."""
    bilan: dict[str, Any] = {
        "demandes": nb_courriers,
        "sujets_disponibles": len(sujets),
        "appels": 0,
        "produits": 0,
        "schema_invalide": 0,
        "doublons": 0,
        "exclus": 0,
        "exclusions": dict.fromkeys(MOTIFS_EXCLUSION, 0),
        "budget_epuise": False,
    }
    if nb_courriers == 0 or fabrique is None:
        return bilan
    prefixe = f"{SUJET_CT[0].lower()}.{SUJET_CT[1]}."
    objets_vus: set[str] = set()
    for sujet in sujets[:nb_courriers]:
        try:
            appel_id, contenu = fabrique(run.run_id, sujet.amorce_id, session_courrier(sujet))
        except BudgetEpuise:
            bilan["budget_epuise"] = True
            consigner("budget épuisé : amorces CT interrompues")
            break
        bilan["appels"] += 1
        valeurs = _champs_courrier(contenu)
        if valeurs is None:
            bilan["schema_invalide"] += 1
            continue
        objet = sha256_hex(normaliser(valeurs["objet"]))
        if objet in objets_vus:
            bilan["doublons"] += 1
            continue
        motifs = {motif for valeur in valeurs.values() for motif in protection.motifs(valeur)}
        if motifs:
            bilan["exclus"] += 1
            for motif in motifs:
                bilan["exclusions"][motif] += 1
            continue
        objets_vus.add(objet)
        suffixe = sujet.amorce_id.removeprefix(prefixe)
        try:
            amorces = [
                Amorce(
                    schema_version=1,
                    amorce_id=f"{SUJET_CT[0].lower()}.{champ}.{suffixe}",
                    tache=SUJET_CT[0],
                    emplacement=champ,
                    texte=valeur,
                    sha_texte=sha256_hex(valeur),
                    auteur_contenu="mistral",
                    appel_id=appel_id,
                )
                for champ, valeur in valeurs.items()
            ]
        except ValidationError:
            raise ProvenanceInvalide(
                f"courrier du sujet {sujet.amorce_id!r} : réponse de la fabrique non conforme"
            ) from None
        for amorce in amorces:
            _ecrire_amorce(run, amorce)
        bilan["produits"] += 1
    consigner(f"amorces CT : {bilan['produits']} courrier(s) sur {bilan['appels']} appel(s)")
    return bilan


# --- Vérification -------------------------------------------------------------------------


def verifier_amorces(
    racine: str | Path,
    run_id: str,
    jeux: Sequence[JeuPublic],
    decodeur: Decodeur,
    *,
    regles: Sequence[RegleAmorce] = REGLES,
) -> list[Amorce]:
    """Relit `runs/data-seed/<run_id>/amorces.jsonl` et le confronte aux jeux sur disque.

    Contrôles : schéma `Amorce` (provenance complète), `sha_texte`, unicité des
    identifiants, refus de `anael` ; pour une amorce publique, le jeu et la révision sont
    ceux d'un `JeuPublic`, une règle couvre sa Tâche et son emplacement, et son texte est
    exactement un candidat de la règle à la `ligne` du jeu (octets relus, SHA-256 vérifié).
    Lève `ProvenanceInvalide` au moindre écart.
    """
    base = Path(racine).resolve()
    if not isinstance(run_id, str) or not re.fullmatch(MOTIF_RUN_ID, run_id):
        raise ProvenanceInvalide("identifiant de run seed invalide")
    chemin = base / "runs" / TYPE_RUN / run_id / NOM_AMORCES
    try:
        contenu = lire(chemin, "data", racine=base).decode("utf-8")
    except (OSError, UnicodeDecodeError):
        raise ProvenanceInvalide(f"artefact seed {run_id} illisible") from None

    amorces: list[Amorce] = []
    vus: set[str] = set()
    for numero, ligne in enumerate(contenu.split("\n"), start=1):
        if not ligne.strip():
            continue
        try:
            amorce = Amorce.model_validate_json(ligne)
        except ValidationError:
            raise ProvenanceInvalide(
                f"artefact seed {run_id} : ligne {numero} non conforme au schéma Amorce"
            ) from None
        if amorce.amorce_id in vus:
            raise ProvenanceInvalide(f"amorce {amorce.amorce_id!r} en double")
        vus.add(amorce.amorce_id)
        if sha256_hex(amorce.texte) != amorce.sha_texte:
            raise ProvenanceInvalide(f"amorce {amorce.amorce_id!r} : sha_texte faux")
        if amorce.auteur_contenu == "anael":
            raise ProvenanceInvalide(
                f"amorce {amorce.amorce_id!r} : auteur_contenu « anael » refusé"
            )
        amorces.append(amorce)
    for amorce in amorces:
        if amorce.auteur_contenu == "config" and amorce.lie_a not in vus:
            raise ProvenanceInvalide(f"amorce {amorce.amorce_id!r} : amorce liée absente")

    attendues: dict[str, dict[int, list[Amorce]]] = {}
    for amorce in amorces:
        if amorce.auteur_contenu != "public":
            continue
        jeu = next(
            (j for j in jeux if j.depot == amorce.jeu and j.revision == amorce.revision), None
        )
        if jeu is None or not any(
            r.jeu == jeu.nom and (r.tache, r.emplacement) == (amorce.tache, amorce.emplacement)
            for r in regles
        ):
            raise ProvenanceInvalide(
                f"amorce {amorce.amorce_id!r} : aucun jeu ni aucune règle ne la couvre"
            )
        attendues.setdefault(jeu.nom, {}).setdefault(amorce.ligne or 0, []).append(amorce)

    for jeu in jeux:
        voulues = attendues.get(jeu.nom)
        if not voulues:
            continue
        regles_jeu = [r for r in regles if r.jeu == jeu.nom]
        restantes = {ligne: list(liste) for ligne, liste in voulues.items()}
        for numero, valeurs in _lignes_jeu(base, jeu, _colonnes(jeu, regles_jeu), decodeur):
            if numero not in restantes:
                continue
            for amorce in restantes.pop(numero):
                if not any(
                    texte == amorce.texte
                    for regle in regles_jeu
                    if (regle.tache, regle.emplacement) == (amorce.tache, amorce.emplacement)
                    for _, texte, _ in _valeurs_regle(regle, valeurs)
                ):
                    raise ProvenanceInvalide(
                        f"amorce {amorce.amorce_id!r} : texte différent de la ligne {numero} "
                        f"du jeu {jeu.nom}"
                    )
            if not restantes:
                break
        if restantes:
            raise ProvenanceInvalide(
                f"jeu {jeu.nom} : ligne(s) {sorted(restantes)} introuvable(s) pour les amorces"
            )
    return amorces
