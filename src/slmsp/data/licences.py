"""Registre des licences : `data/registre-licences.toml` (FR-31, AD-3 verrou 5).

Toute source d'amorce ou de Donnée d'entraînement doit y figurer avec sa licence, son usage
admis et sa provenance :

- `usage` ∈ `USAGES` : `diffusable` (admise par les deux variantes), `recherche` (variante
  `recherche` seulement) ou `evaluation_seulement` (refusée par tout le pipeline) ;
- `auteur_contenu` ∈ {`public`, `mistral`, `anael`, `modele-base`} et `genere_par` ∈
  `GENERE_PAR_ADMIS`, cohérents entre eux (`modele-base` : sorties d'un Modèle de base local
  devenues cibles par sélection, story 15.3, identifiant `org/nom` de sa fiche HF).
  `claude`, `inconnu` ou une source distillée d'un modèle non autorisé lèvent
  `ProvenanceInvalide` au chargement. Ces listes sont un verrou (D1.1), pas un réglage.

Le fichier est lu par le lecteur contrôlé `slmsp.core.artefacts.lire` (AD-24). Un registre
malformé (TOML invalide, clé inconnue, id en double, usage hors liste) lève
`ConfigurationInvalide`. Les messages d'erreur citent les clés fautives et l'id de la
source, jamais les autres valeurs saisies.
"""

from __future__ import annotations

import json
import tomllib
from collections import Counter
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Annotated, Any, Final, Literal, get_args

from pydantic import ConfigDict, Field, StringConstraints, ValidationError

from slmsp.core.artefacts import lire
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import ConfigurationInvalide, ProvenanceInvalide, SourceSansLicence
from slmsp.core.schemas import SchemaBase, SousSchema
from slmsp.core.schemas.amorce import AuteurContenu

__all__ = [
    "AUTEURS_ADMIS",
    "CHEMIN_REGISTRE",
    "GENERE_PAR_ADMIS",
    "USAGES",
    "VARIANTES",
    "RegistreLicences",
    "SourceLicence",
    "UsageInterdit",
]

CHEMIN_REGISTRE: Final = "data/registre-licences.toml"
"""Chemin du registre, relatif à la racine du projet."""

Usage = Literal["diffusable", "recherche", "evaluation_seulement"]
Variante = Literal["diffusable", "recherche"]
GenerePar = Literal["humain", "mistral", "api-publique", "modele-base"]

USAGES: Final[tuple[str, ...]] = get_args(Usage)
VARIANTES: Final[tuple[str, ...]] = get_args(Variante)
AUTEURS_ADMIS: Final[frozenset[str]] = frozenset(get_args(AuteurContenu))

GENERE_PAR_ADMIS: Final[Mapping[str, frozenset[str]]] = MappingProxyType(
    {
        "humain": frozenset({"public", "anael"}),
        "mistral": frozenset({"mistral"}),
        "api-publique": frozenset({"public"}),
        "modele-base": frozenset({"modele-base"}),
    }
)
"""Générateurs admis et, pour chacun, les `auteur_contenu` compatibles (verrou D1.1)."""

_USAGES_PAR_VARIANTE: Final[Mapping[str, frozenset[str]]] = MappingProxyType(
    {
        "diffusable": frozenset({"diffusable"}),
        "recherche": frozenset({"diffusable", "recherche"}),
    }
)

MOTIF_ID: Final = r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$"

Texte = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class UsageInterdit(SourceSansLicence):
    """La source est inscrite au registre, mais son usage n'admet pas la variante demandée."""


class SourceLicence(SousSchema):
    """Une entrée `[[sources]]` du registre."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    id: Annotated[str, StringConstraints(pattern=MOTIF_ID)]
    licence: Texte
    usage: Usage
    auteur_contenu: AuteurContenu
    genere_par: GenerePar
    revision: Texte | None = None
    verifie_le: date | None = None
    notes: Texte | None = None


class _FichierRegistre(SchemaBase):
    model_config = ConfigDict(extra="forbid", strict=True)

    schema_version: Literal[1]
    sources: list[SourceLicence] = Field(min_length=1)


def _verifier_provenance(chemin: Path, sources: list[Any]) -> None:
    """Verrou 5 sur le TOML brut : `ProvenanceInvalide` avant toute validation de schéma."""
    for indice, source in enumerate(sources):
        if not isinstance(source, Mapping):
            continue  # forme refusée ensuite par le schéma (ConfigurationInvalide)
        ident = source.get("id")
        nom = ident if isinstance(ident, str) and ident else f"sources[{indice}]"
        auteur = source.get("auteur_contenu")
        genere_par = source.get("genere_par")
        if not isinstance(auteur, str) or auteur not in AUTEURS_ADMIS:
            raise ProvenanceInvalide(
                f"{chemin} : source {nom!r} : auteur_contenu absent ou non admis "
                f"(attendu : {', '.join(sorted(AUTEURS_ADMIS))})"
            )
        if not isinstance(genere_par, str) or genere_par not in GENERE_PAR_ADMIS:
            raise ProvenanceInvalide(
                f"{chemin} : source {nom!r} : genere_par absent ou non admis "
                f"(attendu : {', '.join(GENERE_PAR_ADMIS)})"
            )
        if auteur not in GENERE_PAR_ADMIS[genere_par]:
            raise ProvenanceInvalide(
                f"{chemin} : source {nom!r} : auteur_contenu {auteur!r} incohérent "
                f"avec genere_par {genere_par!r}"
            )


class RegistreLicences:
    """Registre des licences chargé et validé ; immuable."""

    def __init__(self, chemin: Path, octets: bytes, sources: list[SourceLicence]) -> None:
        self.chemin = chemin
        self._sha256 = sha256_hex(octets)
        self._sources: Mapping[str, SourceLicence] = MappingProxyType(
            {source.id: source for source in sorted(sources, key=lambda s: s.id)}
        )

    @classmethod
    def charger(
        cls, chemin: str | Path | None = None, *, racine: str | Path | None = None
    ) -> RegistreLicences:
        """Lit et valide le registre (défaut : `data/registre-licences.toml` de `racine`).

        Lève `ProvenanceInvalide` (verrou 5), `ConfigurationInvalide` (fichier absent,
        illisible ou malformé) ou `LectureInterdite` (chemin hors de la liste d'accès).
        """
        chemin = Path(chemin if chemin is not None else CHEMIN_REGISTRE)
        try:
            octets = lire(chemin, "data", racine=racine)
        except OSError as exc:
            raise ConfigurationInvalide(
                f"{chemin} : registre des licences illisible ({type(exc).__name__})"
            ) from None
        try:
            donnees = tomllib.loads(octets.decode("utf-8"))
        except UnicodeDecodeError:
            raise ConfigurationInvalide(f"{chemin} : TOML invalide : fichier non UTF-8") from None
        except tomllib.TOMLDecodeError as exc:
            raise ConfigurationInvalide(f"{chemin} : TOML invalide : {exc}") from None

        sources_brutes = donnees.get("sources")
        if isinstance(sources_brutes, list):
            _verifier_provenance(chemin, sources_brutes)
        try:
            fichier = _FichierRegistre.model_validate(donnees)
        except ValidationError as exc:
            lignes = []
            for erreur in exc.errors(include_url=False, include_input=False, include_context=False):
                cle = ".".join(str(partie) for partie in erreur["loc"]) or "(racine)"
                lignes.append(f"{chemin} : clé « {cle} » : {erreur['msg']}")
            raise ConfigurationInvalide("\n".join(lignes)) from None

        comptes = Counter(source.id for source in fichier.sources)
        doublons = sorted(ident for ident, nombre in comptes.items() if nombre > 1)
        if doublons:
            raise ConfigurationInvalide(f"{chemin} : id en double : {', '.join(doublons)}")
        return cls(chemin, octets, fichier.sources)

    @property
    def ids(self) -> tuple[str, ...]:
        """Identifiants des sources, triés."""
        return tuple(self._sources)

    @property
    def sha256(self) -> str:
        """SHA-256 des octets lus du registre."""
        return self._sha256

    def source(self, id_source: str) -> SourceLicence:
        """Entrée de `id_source` ; `SourceSansLicence` si elle est absente du registre."""
        try:
            return self._sources[id_source]
        except KeyError:
            raise SourceSansLicence(
                f"source {id_source!r} absente du registre des licences ({self.chemin})"
            ) from None

    def exiger(self, id_source: str, variante: str) -> SourceLicence:
        """Entrée de `id_source` si son usage admet `variante` (`diffusable` ou `recherche`).

        Lève `ValueError` pour une variante inconnue, `SourceSansLicence` si la source est
        absente, `UsageInterdit` si son usage ne l'admet pas (`evaluation_seulement` : jamais).
        """
        if variante not in _USAGES_PAR_VARIANTE:
            raise ValueError(f"variante inconnue : {variante!r} (attendu : {', '.join(VARIANTES)})")
        source = self.source(id_source)
        if source.usage not in _USAGES_PAR_VARIANTE[variante]:
            raise UsageInterdit(
                f"source {id_source!r} : usage {source.usage!r} "
                f"interdit dans la variante {variante!r}"
            )
        return source

    def source_modele_base(self, base: str) -> SourceLicence:
        """Entrée des sorties du Modèle de base `base` (`slm:<slug>`) : l'unique source
        `genere_par = "modele-base"` dont le nom (après « / ») vaut `<slug>` sans tenir compte
        de la casse. `SourceSansLicence` si aucune ou plusieurs."""
        slug = base.removeprefix("slm:").casefold()
        trouvees = [
            s
            for s in self._sources.values()
            if s.genere_par == "modele-base" and s.id.split("/", 1)[1].casefold() == slug
        ]
        if len(trouvees) != 1:
            raise SourceSansLicence(
                f"sorties {base!r} : {len(trouvees)} entrée(s) « modele-base » au registre des "
                f"licences ({self.chemin}), une attendue"
            )
        return trouvees[0]

    def instantane(self) -> dict[str, Any]:
        """Instantané JSON du registre (clés triées, sources triées par id) pour un MANIFEST."""
        contenu = {
            "schema_version": 1,
            "sha256": self._sha256,
            "sources": [s.model_dump(mode="json") for s in self._sources.values()],
        }
        return json.loads(json_canonique(contenu))
