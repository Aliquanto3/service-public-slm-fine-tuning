"""Table des Tâches et prompts de Tâche (AD-14, AD-7, D1.1).

`config/taches.toml` déclare les 9 Tâches : libellé, activation, prompt système, outils
autorisés, avertissement et variantes de prompt. Chaque prompt de
`config/prompts/taches/` est validé par `core.gabarits.valider_gabarit` au chargement :
`id` égal au nom du fichier, `tache` égal au code, emplacements pris dans `EMPLACEMENTS`.
Seule la section « Consigne » part au modèle ; les emplacements déclarent les clés
d'entrée admises par le Harnais (`harness.prompts`).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Final, Literal

from pydantic import Field

from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.core.erreurs import ConfigurationInvalide, SlmspError
from slmsp.core.gabarits import GabaritInvalide, valider_gabarit
from slmsp.mcp.outils import OUTILS_AUTORISES

CODES_TACHES: Final[tuple[str, ...]] = ("Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR", "TR")
"""Les 9 codes de Tâche de `config/taches.toml`."""

EMPLACEMENTS_TEXTE: Final[tuple[str, ...]] = ("question", "demande")
"""Emplacements d'une entrée texte (Q, RD, NR) : l'entrée est une chaîne."""

EMPLACEMENTS: Final[tuple[str, ...]] = (
    *EMPLACEMENTS_TEXTE,
    "passages",
    "consigne",
    "type_courrier",
    "objet",
    "elements_connus",
    "longueur_demandee",
    "langue_source",
    "langue_cible",
    "partie",
    "notes",
    "transcription",
    "texte",
    "document",
    "parties",
)
"""Vocabulaire fermé des emplacements admis dans un prompt de Tâche."""

NOM_CONFIG: Final = "taches.toml"


class TacheInconnue(SlmspError):
    """Code de Tâche absent de la table."""


class VarianteInconnue(SlmspError):
    """Variante de prompt non déclarée pour la Tâche."""


class _ConfigTache(ModeleConfig):
    libelle: str = Field(min_length=1)
    actif: bool
    prompt: str = Field(min_length=1)
    outils_autorises: list[str] = Field(default_factory=list)
    avertissement: str | None = None
    variantes: dict[str, str] = Field(default_factory=dict)


class _ConfigTaches(ModeleConfig):
    schema_version: Literal[1]
    defaut: str
    taches: dict[str, _ConfigTache]


@dataclass(frozen=True)
class PromptTache:
    """Prompt système d'une Tâche, validé.

    `consigne` est le texte envoyé comme message `system` ; `emplacements` liste les
    clés d'entrée admises, dans l'ordre du fichier.
    """

    id: str
    version: int
    tache: str
    consigne: str
    emplacements: tuple[str, ...]
    sha256: str

    @property
    def entree_texte(self) -> bool:
        """Vrai si l'entrée est une chaîne (emplacement `question` ou `demande`)."""
        return any(nom in EMPLACEMENTS_TEXTE for nom in self.emplacements)


@dataclass(frozen=True)
class Tache:
    """Une Tâche de la table, avec son prompt et ses variantes."""

    code: str
    libelle: str
    actif: bool
    prompt: PromptTache
    outils_autorises: tuple[str, ...] = ()
    avertissement: str | None = None
    variantes: Mapping[str, PromptTache] = field(default_factory=lambda: MappingProxyType({}))

    def prompt_pour(self, variante: str | None = None) -> PromptTache:
        """Prompt de la variante (`None` : prompt principal).

        Lève `VarianteInconnue` si la variante n'est pas déclarée.
        """
        if variante is None:
            return self.prompt
        try:
            return self.variantes[variante]
        except KeyError:
            connues = ", ".join(sorted(self.variantes)) or "aucune"
            raise VarianteInconnue(
                f"Tâche {self.code} : variante « {variante} » inconnue (connues : {connues})"
            ) from None


@dataclass(frozen=True)
class TableTaches:
    """Table des Tâches chargée depuis `config/taches.toml`."""

    taches: Mapping[str, Tache]
    code_defaut: str

    @property
    def codes(self) -> tuple[str, ...]:
        return tuple(self.taches)

    @property
    def defaut(self) -> Tache:
        """Tâche par défaut (Question)."""
        return self.taches[self.code_defaut]

    def tache(self, code: str) -> Tache:
        """Tâche de code `code` ; lève `TacheInconnue` si le code est absent."""
        try:
            return self.taches[code]
        except KeyError:
            raise TacheInconnue(
                f"Tâche « {code} » inconnue (connues : {', '.join(self.taches)})"
            ) from None


def _charger_prompt(
    dossier: Path, nom_fichier: str, code: str, fautes: list[str]
) -> PromptTache | None:
    lieu = f"Tâche {code} : prompt « {nom_fichier} »"
    if Path(nom_fichier).name != nom_fichier or not nom_fichier.endswith(".md"):
        fautes.append(f"{lieu} : nom de fichier .md attendu, sans dossier")
        return None
    chemin = dossier / nom_fichier
    try:
        gabarit = valider_gabarit(chemin)
    except GabaritInvalide as exc:
        fautes.extend(f"{lieu} : {faute}" for faute in exc.fautes)
        return None
    attendu = nom_fichier.removesuffix(".md")
    if gabarit.id != attendu:
        fautes.append(f"{lieu} : « id » doit valoir « {attendu} » (nom du fichier)")
    if gabarit.front_matter.get("tache") != code:
        fautes.append(f"{lieu} : « tache » doit valoir « {code} »")
    noms = tuple(gabarit.emplacements)
    hors = [nom for nom in noms if nom not in EMPLACEMENTS]
    if hors:
        fautes.append(f"{lieu} : emplacement(s) hors vocabulaire : {', '.join(hors)}")
    textes = [nom for nom in noms if nom in EMPLACEMENTS_TEXTE]
    if textes and (len(textes) > 1 or not set(noms) <= {*EMPLACEMENTS_TEXTE, "passages"}):
        fautes.append(
            f"{lieu} : une entrée texte déclare un seul emplacement parmi "
            f"{', '.join(EMPLACEMENTS_TEXTE)}, plus éventuellement « passages »"
        )
    if not textes and "passages" in noms:
        fautes.append(f"{lieu} : « passages » n'est admis qu'avec une entrée texte")
    return PromptTache(
        id=gabarit.id,
        version=gabarit.version,
        tache=code,
        consigne=gabarit.consigne,
        emplacements=noms,
        sha256=gabarit.sha256,
    )


def charger_taches(
    chemin: str | Path | None = None, dossier_prompts: str | Path | None = None
) -> TableTaches:
    """Charge et valide la table des Tâches et tous ses prompts.

    `chemin` vaut `config/taches.toml` par défaut ; `dossier_prompts` vaut
    `<dossier de chemin>/prompts/taches`. Lève `ConfigurationInvalide` en listant toutes
    les fautes : code manquant ou en trop, `defaut` inconnu, outil non autorisé, prompt
    non conforme.
    """
    fichier = Path(chemin) if chemin is not None else racine_projet() / "config" / NOM_CONFIG
    dossier = (
        Path(dossier_prompts)
        if dossier_prompts is not None
        else fichier.parent / "prompts" / "taches"
    )
    config = charger_toml(fichier, _ConfigTaches)
    fautes: list[str] = []
    manquants = [code for code in CODES_TACHES if code not in config.taches]
    if manquants:
        fautes.append(f"code(s) de Tâche manquant(s) : {', '.join(manquants)}")
    en_trop = [code for code in config.taches if code not in CODES_TACHES]
    if en_trop:
        fautes.append(f"code(s) de Tâche inconnu(s) : {', '.join(en_trop)}")
    if config.defaut not in CODES_TACHES:
        fautes.append(f"« defaut » : Tâche « {config.defaut} » inconnue")

    taches: dict[str, Tache] = {}
    for code in CODES_TACHES:
        brut = config.taches.get(code)
        if brut is None:
            continue
        interdits = [nom for nom in brut.outils_autorises if nom not in OUTILS_AUTORISES]
        if interdits:
            fautes.append(f"Tâche {code} : outil(s) non autorisé(s) : {', '.join(interdits)}")
        if len(set(brut.outils_autorises)) != len(brut.outils_autorises):
            fautes.append(f"Tâche {code} : outil en double dans « outils_autorises »")
        prompt = _charger_prompt(dossier, brut.prompt, code, fautes)
        variantes = {
            nom: _charger_prompt(dossier, nom_fichier, code, fautes)
            for nom, nom_fichier in sorted(brut.variantes.items())
        }
        if prompt is None or any(v is None for v in variantes.values()):
            continue
        taches[code] = Tache(
            code=code,
            libelle=brut.libelle,
            actif=brut.actif,
            prompt=prompt,
            outils_autorises=tuple(brut.outils_autorises),
            avertissement=brut.avertissement,
            variantes=MappingProxyType({nom: v for nom, v in variantes.items() if v is not None}),
        )
    if fautes:
        raise ConfigurationInvalide(f"{fichier} :\n- " + "\n- ".join(fautes))
    return TableTaches(taches=MappingProxyType(taches), code_defaut=config.defaut)
