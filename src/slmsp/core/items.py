"""Lecteur unique des items du Jeu d'évaluation, rendu en requête et API anti-fuite (AD-11, AD-24).

Seule voie de lecture des items : le banc, le Juge et le pipeline `data` passent tous par ce
module. Deux modes de lecture :

- **strict** (versions `vN`, `vN.M`) : schéma fermé par Tâche, champs communs exigés
  (`theme`, `parametres`, `fictif`, `version_item` ≥ 1, `provenance` non vide) et champs de
  référence de SPEC §3 ; RD exige `appels_attendus[].regles`, `mode` et `cassettes`.
- **souple** (calibrage) : adapte à la lecture le format de l'échantillon de calibrage
  (`R`→`RD`, `RS`→`RE`, `cassette`→`cassettes`…) et pose les défauts, sans rien écrire.

Dans les deux modes, une clé inconnue d'un item est refusée ; les clés de `entree` et de
`provenance[]` restent ouvertes. Toutes les erreurs d'un fichier sont rassemblées dans une
seule `ItemInvalide`, chacune citant l'item et le champ.

Format `regles` d'un appel attendu (RD, fixé ici, suivi par la story 7.3) :
`{"optionnel": bool, "ordre_libre": bool, "arguments": {<nom>: {"exact": <valeur>} |
{"contient_un_de": [str, …]} | {"mot_entier_un_de": [str, …]} | {"optionnel": true}}}`,
`optionnel` combinable avec `exact`, `contient_un_de` ou `mot_entier_un_de` ;
`contient_un_de` (fragment en début de mot) et `mot_entier_un_de` (mot entier, v1.1) se
combinent en « ou ». Une règle sans `mot_entier_un_de` se sérialise sans cette clé.

API anti-fuite : le pipeline `data` ne voit le jeu que par des empreintes de n-grammes
hachés (`empreintes_antifuite`), des vecteurs (`vecteurs_antifuite`) et des identifiants
protégés (`identifiants_proteges`), jamais par le texte d'un item.

Ce module n'importe que `slmsp.core` (couche 0).
"""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import TYPE_CHECKING, Any, ClassVar, Final, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializerFunctionWrapHandler,
    ValidationError,
    field_validator,
    model_serializer,
    model_validator,
)

from slmsp.core.canonique import sha256_hex
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import SlmspError
from slmsp.core.texte import VERSION_TEXTE, ngrammes, normaliser

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray

    from slmsp.core.ports import EmbedderPort

# --- Tables faisant foi (SPEC §2, §7 bis) ---------------------------------------------------

CODES: Final[tuple[str, ...]] = ("Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR")
"""Codes de Tâche faisant foi, dans l'ordre de SPEC §2."""

LIBELLES: Final[Mapping[str, str]] = {
    "Q": "Question",
    "RD": "Recherche de données",
    "CR": "Compte rendu",
    "LC": "Langage clair",
    "CO": "Correction",
    "RE": "Résumé",
    "CT": "Courrier type",
    "NR": "Non-régression",
}
"""Code → libellé de `tache`."""

ALIAS_LIBELLES: Final[Mapping[str, str]] = {"Non-régression générale": "NR"}
"""Libellés acceptés en plus de `LIBELLES` (SPEC §2 écrit « Non-régression générale »)."""

CODE_PAR_LIBELLE: Final[Mapping[str, str]] = {
    **{libelle: code for code, libelle in LIBELLES.items()},
    **ALIAS_LIBELLES,
}
"""Libellé de `tache` (alias compris) → code."""

CODES_CALIBRAGE: Final[Mapping[str, str]] = {"R": "RD", "RS": "RE"}
"""Préfixes d'identifiant du calibrage → code faisant foi (mode souple seulement)."""

DIFFICULTES: Final[tuple[str, ...]] = ("facile", "moyen", "difficile")

THEMES: Final[tuple[str, ...]] = (
    "social-autonomie",
    "etat-civil-papiers",
    "travail-emploi",
    "collectivites",
    "famille-education-sante",
    "fiscalite-locale",
)
"""Slugs des thèmes de SPEC §2 (obligatoires en strict pour Q, RD, LC et RE)."""

THEME_NON_CLASSE: Final = "non-classe"
CODES_THEMATIQUES: Final[tuple[str, ...]] = ("Q", "RD", "LC", "RE")
CODES_ENTREE_TEXTE: Final[tuple[str, ...]] = ("Q", "RD", "NR")
"""Tâches dont l'`entree` est un texte ; les autres ont un objet à clés nommées."""

MODES_RD: Final[tuple[str, ...]] = ("connecte", "hors-ligne", "repli")

OUTILS_RD: Final[tuple[str, ...]] = (
    "search_datasets",
    "get_dataset_info",
    "list_dataset_resources",
    "query_resource_data",
    "get_resource_info",
)
"""Outils MCP admis dans `appels_attendus` (copie de `slmsp.mcp.outils.OUTILS_AUTORISES`,
que `core` ne peut pas importer ; un test vérifie l'égalité)."""

MOTIF_VERSION: Final = r"^v[0-9]+(?:\.[0-9]+)?$"
VERSION_CALIBRAGE: Final = "calibrage"

_MOTIF_ID = re.compile(r"^(?P<code>[A-Z]+)-(?P<numero>[0-9]{3,})$")
_MOTIF_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_MOTIF_FICTIF = re.compile(r"fictif|fictive|r[ée]dig[ée]e?s? pour l['’]évaluation", re.IGNORECASE)

N_DEFAUT: Final = 5
"""Taille par défaut des n-grammes anti-fuite (mots normalisés)."""

LONGUEUR_EMPREINTE: Final = 16
"""Les empreintes de n-grammes sont des SHA-256 tronqués à 16 caractères hexadécimaux."""


class ItemInvalide(SlmspError):
    """Un ou plusieurs items d'un fichier sont illisibles ou non conformes au schéma.

    `erreurs` rassemble toutes les erreurs du fichier, chacune au format
    « <id> : `<champ>` : <message> ».
    """

    def __init__(self, message: str, erreurs: Sequence[str] = ()):
        super().__init__(message)
        self.erreurs: tuple[str, ...] = tuple(erreurs)


# --- Modèles ---------------------------------------------------------------------------------


class _Ferme(BaseModel):
    # `strict` : aucune coercition (`"yes"` n'est pas un booléen, `"3"` pas un entier).
    model_config = ConfigDict(extra="forbid", strict=True)


class Provenance(BaseModel):
    """Une source consultée ; clés ouvertes, seule `consulte_le` (date ISO) est exigée."""

    model_config = ConfigDict(extra="allow")

    consulte_le: str
    source: str | None = None
    url: str | None = None

    @field_validator("consulte_le")
    @classmethod
    def _date_iso(cls, valeur: str) -> str:
        try:
            date.fromisoformat(valeur)
        except ValueError:
            try:
                datetime.fromisoformat(valeur)
            except ValueError:
                raise ValueError("date ou date-heure ISO attendue") from None
        return valeur


class RegleArgument(_Ferme):
    """Règle d'un argument : `exact`, `contient_un_de` et/ou `mot_entier_un_de`, ou
    `optionnel` seul.

    `contient_un_de` : un fragment en début de mot ; `mot_entier_un_de` : un mot (ou une
    suite de mots) entier, bordé d'une espace ou du bord du texte, après normalisation
    (« REI » accepte « fichier REI 2024 », refuse « Reims »). Les deux listes se combinent
    en « ou ».
    """

    exact: Any = None
    contient_un_de: list[str] | None = Field(default=None, min_length=1)
    mot_entier_un_de: list[str] | None = Field(default=None, min_length=1)
    optionnel: bool = False

    @model_validator(mode="after")
    def _une_regle(self) -> Self:
        a_exact = "exact" in self.model_fields_set
        a_liste = self.contient_un_de is not None or self.mot_entier_un_de is not None
        if a_exact and a_liste:
            raise ValueError("`exact` exclut `contient_un_de` et `mot_entier_un_de`")
        if not (a_exact or a_liste or self.optionnel):
            raise ValueError(
                "règle vide : `exact`, `contient_un_de`, `mot_entier_un_de` ou "
                "`optionnel: true` attendu"
            )
        return self

    @model_serializer(mode="wrap")
    def _sans_mot_entier_vide(self, handler: SerializerFunctionWrapHandler) -> dict[str, Any]:
        # Sans la règle, la forme sérialisée reste celle d'avant son ajout : le
        # `model_dump` d'un item, donc la clé du cache des verdicts, ne change pas.
        donnees = handler(self)
        if self.mot_entier_un_de is None:
            donnees.pop("mot_entier_un_de", None)
        return donnees

    @property
    def a_exact(self) -> bool:
        return "exact" in self.model_fields_set


class ReglesAppel(_Ferme):
    """Règles lisibles par machine d'un appel attendu (format fixé par la story 5.1)."""

    optionnel: bool = False
    ordre_libre: bool = False
    arguments: dict[str, RegleArgument] = Field(default_factory=dict)


class AppelAttendu(_Ferme):
    """Appel d'outil attendu d'un item RD ; `regle` est la description textuelle du calibrage."""

    outil: Literal[OUTILS_RD]  # type: ignore[valid-type]
    arguments: dict[str, Any] = Field(default_factory=dict)
    regles: ReglesAppel | None = None
    regle: str | None = None


class Faute(_Ferme):
    """Faute d'un item CO, repérée par ses indices de caractères dans `entree.texte`."""

    debut: int = Field(ge=0)
    fin: int = Field(ge=0)
    erreur: str
    correction: str
    type: str
    contexte_fautif: str | None = None

    @model_validator(mode="after")
    def _intervalle(self) -> Self:
        if self.fin <= self.debut:
            raise ValueError("`fin` doit être strictement supérieure à `debut`")
        return self


class ActionReference(_Ferme):
    """Action attendue d'un compte rendu."""

    action: str
    responsable: str
    echeance: str


class ItemBase(_Ferme):
    """Champs communs à toutes les Tâches (SPEC §3)."""

    code: ClassVar[str]
    champs_reference: ClassVar[tuple[str, ...]] = ()
    """Champs de référence exigés en mode strict (SPEC §3)."""
    champs_texte_reference: ClassVar[tuple[str, ...]] = ()
    """Champs de référence textuels pris par l'anti-fuite."""

    id: str
    tache: str
    difficulte: Literal["facile", "moyen", "difficile"]
    theme: str
    entree: str | dict[str, Any]
    parametres: dict[str, Any]
    provenance: list[Provenance]
    licence_source: str | None = None
    fictif: bool
    version_item: int = Field(ge=0)

    @field_validator("id")
    @classmethod
    def _id_du_code(cls, valeur: str) -> str:
        m = _MOTIF_ID.fullmatch(valeur)
        if m is None or m["code"] not in CODES or int(m["numero"]) < 1:
            raise ValueError(f"identifiant attendu `<CODE>-NNN` (codes {', '.join(CODES)})")
        if m["code"] != cls.code:
            raise ValueError(f"le code de l'identifiant diffère de celui de `tache` ({cls.code})")
        return valeur

    @field_validator("theme")
    @classmethod
    def _theme_slug(cls, valeur: str) -> str:
        if not _MOTIF_SLUG.fullmatch(valeur):
            raise ValueError("slug attendu (minuscules, chiffres et tirets)")
        return valeur

    @field_validator("entree")
    @classmethod
    def _entree_typee(cls, valeur: str | dict[str, Any]) -> str | dict[str, Any]:
        if cls.code in CODES_ENTREE_TEXTE and not isinstance(valeur, str):
            raise ValueError(f"texte attendu pour la Tâche {cls.code}")
        if cls.code not in CODES_ENTREE_TEXTE and not isinstance(valeur, dict):
            raise ValueError(f"objet attendu pour la Tâche {cls.code}")
        return valeur


class ItemQ(ItemBase):
    code: ClassVar[str] = "Q"
    champs_reference = ("reponse_reference", "elements_cles", "sources_attendues", "sans_reponse")
    champs_texte_reference = ("reponse_reference", "elements_cles", "orientation_attendue")

    tache: Literal["Question"]
    entree: str
    amorce_usager: str | None = None
    reponse_reference: str | None = None
    elements_cles: list[str] | None = None
    sources_attendues: list[str] | None = None
    sans_reponse: bool = False
    orientation_attendue: str | None = None
    mention_obligatoire: str | None = None
    verification_absence: dict[str, Any] | None = None


class ItemRD(ItemBase):
    code: ClassVar[str] = "RD"
    champs_reference = ("appels_attendus", "cassettes", "reponse_reference", "mode")
    champs_texte_reference = ("reponse_reference", "valeurs_attendues", "criteres")

    tache: Literal["Recherche de données"]
    entree: str
    appels_attendus: list[AppelAttendu] | None = None
    cassettes: list[str] = Field(default_factory=list)
    reponse_reference: str | dict[str, Any] | None = None
    valeurs_attendues: Any = None
    mode: Literal["connecte", "hors-ligne", "repli"]
    criteres: list[str] | None = None
    producteurs: list[str] | None = None
    producteur: str | None = None

    @field_validator("cassettes")
    @classmethod
    def _chemins_relatifs(cls, chemins: list[str]) -> list[str]:
        for chemin in chemins:
            if (
                not chemin
                or "\\" in chemin
                or ":" in chemin
                or PurePosixPath(chemin).is_absolute()
                or PureWindowsPath(chemin).drive
            ):
                raise ValueError(f"chemin POSIX relatif au dossier du jeu attendu : {chemin!r}")
        return chemins


class ItemCR(ItemBase):
    code: ClassVar[str] = "CR"
    champs_reference = ("decisions_reference", "actions_reference", "pieges")
    champs_texte_reference = (
        "participants_reference",
        "decisions_reference",
        "actions_reference",
        "pieges",
    )

    tache: Literal["Compte rendu"]
    entree: dict[str, Any]
    type_reunion: str | None = None
    participants_reference: list[str] | None = None
    decisions_reference: list[str] | None = None
    actions_reference: list[ActionReference] | None = None
    pieges: list[str] | None = None


class ItemLC(ItemBase):
    code: ClassVar[str] = "LC"
    champs_reference = (
        "informations_a_conserver",
        "termes_juridiques_a_conserver",
        "kandel_moles_entree",
    )
    champs_texte_reference = ("informations_a_conserver", "termes_juridiques_a_conserver")

    tache: Literal["Langage clair"]
    entree: dict[str, Any]
    informations_a_conserver: list[str] | None = None
    termes_juridiques_a_conserver: list[str] | None = None
    kandel_moles_entree: float | None = None
    version_texte: int | None = None


class ItemCO(ItemBase):
    code: ClassVar[str] = "CO"
    champs_reference = ("fautes", "texte_corrige_reference")
    champs_texte_reference = ("texte_corrige_reference",)

    tache: Literal["Correction"]
    entree: dict[str, Any]
    fautes: list[Faute] | None = None
    texte_corrige_reference: str | None = None
    nb_fautes: int | None = Field(default=None, ge=0)
    note_positions: str | None = None


class ItemRE(ItemBase):
    code: ClassVar[str] = "RE"
    champs_reference = ("points_cles_reference", "longueur_demandee")
    champs_texte_reference = ("points_cles_reference",)

    tache: Literal["Résumé"]
    entree: dict[str, Any]
    points_cles_reference: list[str] | None = None
    longueur_demandee: str | None = None


class ItemCT(ItemBase):
    code: ClassVar[str] = "CT"
    champs_reference = ("type_courrier", "elements_obligatoires", "champs_a_laisser_en_emplacement")
    champs_texte_reference = (
        "elements_obligatoires",
        "champs_a_laisser_en_emplacement",
        "valeurs_interdites",
    )

    tache: Literal["Courrier type"]
    entree: dict[str, Any]
    type_courrier: str | None = None
    elements_obligatoires: list[str] | None = None
    champs_a_laisser_en_emplacement: list[str] | None = None
    valeurs_interdites: list[str] | None = None
    base_reglementaire: dict[str, Any] | None = None


class ItemNR(ItemBase):
    code: ClassVar[str] = "NR"
    champs_texte_reference = ("reponse_reference", "criteres")

    tache: Literal["Non-régression", "Non-régression générale"]
    entree: str
    sous_type: Literal["question", "consigne"] | None = None
    reponse_reference: str | None = None
    criteres: list[str] | None = None


Item = ItemQ | ItemRD | ItemCR | ItemLC | ItemCO | ItemRE | ItemCT | ItemNR
"""Un item lu, de la classe de sa Tâche."""

MODELES: Final[Mapping[str, type[ItemBase]]] = {
    modele.code: modele
    for modele in (ItemQ, ItemRD, ItemCR, ItemLC, ItemCO, ItemRE, ItemCT, ItemNR)
}
"""Code → modèle pydantic de la Tâche."""


def numero_id(identifiant: str) -> tuple[str, int]:
    """Clé de tri naturel d'un identifiant : (`code`, numéro) ; RD-010 après RD-009."""
    m = _MOTIF_ID.fullmatch(identifiant)
    return (m["code"], int(m["numero"])) if m else (identifiant, -1)


# --- Lecture ---------------------------------------------------------------------------------


def _adapter_souple(brut: dict[str, Any]) -> dict[str, Any]:
    """Adapte un item du calibrage au schéma (copie ; l'original n'est pas modifié)."""
    item = copy.deepcopy(brut)
    identifiant = item.get("id")
    if isinstance(identifiant, str):
        m = _MOTIF_ID.fullmatch(identifiant)
        if m and m["code"] in CODES_CALIBRAGE:
            item["id"] = f"{CODES_CALIBRAGE[m['code']]}-{m['numero']}"
    tache = item.get("tache")
    code = CODE_PAR_LIBELLE.get(tache) if isinstance(tache, str) else None
    if "cassette" in item and "cassettes" not in item:
        cassette = item.pop("cassette")
        item["cassettes"] = [cassette] if isinstance(cassette, str) else cassette
    if item.get("comportement_attendu") == "absence_de_source":
        item.pop("comportement_attendu")
        item.setdefault("sans_reponse", True)
    entree = item.get("entree")
    if isinstance(entree, dict):
        if code == "RE" and "longueur_demandee" in entree and "longueur_demandee" not in item:
            item["longueur_demandee"] = entree.pop("longueur_demandee")
        if code == "CT" and "type" in entree and "type_courrier" not in item:
            item["type_courrier"] = entree.pop("type")
    if code == "RD":
        item.setdefault("mode", "connecte")
    item.setdefault("version_item", 0)
    item.setdefault("theme", THEME_NON_CLASSE)
    item.setdefault("parametres", {})
    if "fictif" not in item:
        provenance = item.get("provenance")
        item["fictif"] = isinstance(provenance, list) and any(
            isinstance(p, dict)
            and isinstance(p.get("source"), str)
            and _MOTIF_FICTIF.search(p["source"]) is not None
            for p in provenance
        )
    return item


def _present(brut: Mapping[str, Any], champ: str) -> bool:
    valeur = brut.get(champ)
    return valeur is not None and not (isinstance(valeur, str) and not valeur.strip())


_LISTES_NON_VIDES: Final = frozenset(
    {"points_cles_reference", "elements_obligatoires", "decisions_reference", "fautes"}
)
"""Références exigées non vides en mode strict (les autres listes peuvent être vides)."""
ELEMENTS_CLES_MIN: Final = 3
ELEMENTS_CLES_MAX: Final = 5


def _controles_stricts(item: ItemBase, brut: Mapping[str, Any]) -> list[tuple[str, str]]:
    """Règles du mode strict au-delà du schéma : (champ, message)."""
    erreurs: list[tuple[str, str]] = []
    if item.version_item < 1:
        erreurs.append(("version_item", "entier ≥ 1 attendu en mode strict"))
    if not item.provenance:
        erreurs.append(("provenance", "liste non vide attendue"))
    if item.code in CODES_THEMATIQUES and item.theme not in THEMES:
        erreurs.append(("theme", f"l'un des thèmes de SPEC §2 attendu ({', '.join(THEMES)})"))
    for champ in item.champs_reference:
        if not _present(brut, champ):
            erreurs.append((champ, "champ de référence requis (non vide) en mode strict"))
        elif champ in _LISTES_NON_VIDES and not brut[champ]:
            erreurs.append((champ, "liste non vide attendue en mode strict"))
    if isinstance(item, ItemQ) and item.elements_cles is not None:
        if not ELEMENTS_CLES_MIN <= len(item.elements_cles) <= ELEMENTS_CLES_MAX:
            erreurs.append(
                ("elements_cles", f"{ELEMENTS_CLES_MIN} à {ELEMENTS_CLES_MAX} éléments attendus")
            )
    if isinstance(item, ItemQ) and item.sans_reponse and not item.orientation_attendue:
        erreurs.append(("orientation_attendue", "requis quand `sans_reponse` est vrai"))
    if isinstance(item, ItemRD):
        for i, appel in enumerate(item.appels_attendus or []):
            if appel.regles is None:
                erreurs.append(
                    (f"appels_attendus.{i}.regles", "règles lisibles par machine requises")
                )
    if isinstance(item, ItemCO) and isinstance(item.entree, dict):
        texte = item.entree.get("texte")
        if not isinstance(texte, str):
            erreurs.append(("entree.texte", "texte requis pour repérer les fautes"))
        else:
            for i, faute in enumerate(item.fautes or []):
                if faute.fin > len(texte) or texte[faute.debut : faute.fin] != faute.erreur:
                    erreurs.append((f"fautes.{i}", "`entree.texte[debut:fin]` diffère de `erreur`"))
    if isinstance(item, ItemNR) and not (
        _present(brut, "reponse_reference") or _present(brut, "criteres")
    ):
        erreurs.append(("reponse_reference", "`reponse_reference` ou `criteres` requis"))
    return erreurs


_MESSAGES: Final[Mapping[str, str]] = {
    "missing": "champ requis",
    "extra_forbidden": "clé inconnue",
}


def _messages_validation(exc: ValidationError) -> list[tuple[str, str]]:
    lignes = []
    for erreur in exc.errors(include_url=False, include_input=False, include_context=False):
        champ = ".".join(str(partie) for partie in erreur["loc"]) or "(item)"
        message = _MESSAGES.get(erreur["type"], erreur["msg"])
        lignes.append((champ, message.removeprefix("Value error, ")))
    return lignes


def valider_item(brut: Any, *, strict: bool) -> Item:
    """Valide un item (objet JSON déjà décodé) ; lève `ItemInvalide` avec toutes ses erreurs."""
    erreurs = _erreurs_item(brut, strict=strict, lieu="item")
    if isinstance(erreurs, list):
        raise ItemInvalide("item invalide :\n" + "\n".join(f"- {e}" for e in erreurs), erreurs)
    return erreurs


def _erreurs_item(brut: Any, *, strict: bool, lieu: str) -> Item | list[str]:
    if not isinstance(brut, dict):
        return [f"{lieu} : `(item)` : objet JSON attendu"]
    donnees = brut if strict else _adapter_souple(brut)
    nom = donnees.get("id") if isinstance(donnees.get("id"), str) else lieu
    tache = donnees.get("tache")
    code = CODE_PAR_LIBELLE.get(tache) if isinstance(tache, str) else None
    if code is None:
        connus = ", ".join(CODE_PAR_LIBELLE)
        return [f"{nom} : `tache` : libellé inconnu {tache!r} (connus : {connus})"]
    try:
        item = MODELES[code].model_validate(donnees)
    except ValidationError as exc:
        return [f"{nom} : `{champ}` : {message}" for champ, message in _messages_validation(exc)]
    if strict:
        stricts = _controles_stricts(item, donnees)
        if stricts:
            return [f"{nom} : `{champ}` : {message}" for champ, message in stricts]
    return item  # type: ignore[return-value]


def lire_items(chemin: str | Path, *, strict: bool) -> list[Item]:
    """Lit un fichier JSONL d'items (UTF-8, une ligne par item, lignes vides ignorées).

    Lève `ItemInvalide` si le fichier est illisible ou si un item au moins est invalide ;
    l'exception rassemble toutes les erreurs du fichier (identifiants en double compris).
    """
    chemin = Path(chemin)
    try:
        texte = chemin.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ItemInvalide(f"{chemin} : fichier d'items illisible ({type(exc).__name__})") from None
    except UnicodeDecodeError:
        raise ItemInvalide(f"{chemin} : fichier d'items non UTF-8") from None
    items: list[Item] = []
    erreurs: list[str] = []
    vus: dict[tuple[str, int], str] = {}
    # Coupure sur LF seulement : U+2028, U+0085… peuvent figurer dans une chaîne JSON.
    for numero, ligne in enumerate(texte.split("\n"), start=1):
        ligne = ligne.removesuffix("\r")
        if not ligne.strip():
            continue
        lieu = f"ligne {numero}"
        try:
            brut = json.loads(ligne)
        except json.JSONDecodeError as exc:
            erreurs.append(f"{lieu} : `(item)` : JSON illisible ({exc.msg})")
            continue
        resultat = _erreurs_item(brut, strict=strict, lieu=lieu)
        if isinstance(resultat, list):
            erreurs.extend(resultat)
            continue
        cle = numero_id(resultat.id)
        if cle in vus:
            erreurs.append(f"{resultat.id} : `id` : identifiant en double ({vus[cle]} et {lieu})")
            continue
        vus[cle] = lieu
        items.append(resultat)
    if erreurs:
        raise ItemInvalide(
            f"{chemin} : {len(erreurs)} erreur(s) dans les items :\n"
            + "\n".join(f"- {e}" for e in erreurs),
            erreurs,
        )
    return items


@dataclass(frozen=True)
class Jeu:
    """Un Jeu d'évaluation lu : version, dossier et items (ordre du fichier)."""

    version: str
    racine: Path
    dossier: Path
    chemin_items: Path
    strict: bool
    items: tuple[Item, ...]

    def item(self, identifiant: str) -> Item:
        """L'item d'identifiant `identifiant` ; lève `KeyError` s'il n'existe pas."""
        for item in self.items:
            if item.id == identifiant:
                return item
        raise KeyError(identifiant)

    def cle(self, item: ItemBase) -> str:
        """Clé anti-fuite de l'item : `<version>/<id>`."""
        return f"{self.version}/{item.id}"


def chemins_jeu(version: str, racine: str | Path | None = None) -> tuple[Path, Path, bool]:
    """(dossier du jeu, fichier d'items, mode strict) de la version `version`.

    `calibrage` → `eval/calibrage/echantillon-calibrage.jsonl` (souple) ; `vN` ou `vN.M`
    → `eval/jeu/<version>/items.jsonl` (strict). Lève `ValueError` pour une autre version.
    """
    base = Path(racine) if racine is not None else racine_projet()
    if version == VERSION_CALIBRAGE:
        dossier = base / "eval" / "calibrage"
        return dossier, dossier / "echantillon-calibrage.jsonl", False
    if not isinstance(version, str) or not re.fullmatch(MOTIF_VERSION, version):
        raise ValueError(f"version de jeu invalide : {version!r} (attendu : vN, vN.M ou calibrage)")
    dossier = base / "eval" / "jeu" / version
    return dossier, dossier / "items.jsonl", True


def lire_jeu(version: str, racine: str | Path | None = None) -> Jeu:
    """Lit le jeu `version` (`calibrage` en mode souple, `vN[.M]` en mode strict).

    Ne vérifie pas le manifeste (rôle de `slmsp.evaluation.gel`) et n'écrit rien.
    """
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    dossier, chemin, strict = chemins_jeu(version, base)
    items = lire_items(chemin, strict=strict)
    return Jeu(
        version=version,
        racine=base,
        dossier=dossier,
        chemin_items=chemin,
        strict=strict,
        items=tuple(items),
    )


def resoudre_cassettes(jeu: Jeu, item: ItemBase) -> list[Path]:
    """Chemins absolus des cassettes d'un item RD (liste vide pour les autres Tâches).

    Les chemins sont relatifs au dossier du jeu et doivent se résoudre sous
    `<racine>/eval/` ; sinon `ItemInvalide`. L'existence des fichiers n'est pas vérifiée.
    """
    if not isinstance(item, ItemRD):
        return []
    base_eval = (jeu.racine / "eval").resolve()
    chemins: list[Path] = []
    for relatif in item.cassettes:
        resolu = (jeu.dossier / PurePosixPath(relatif)).resolve()
        if not resolu.is_relative_to(base_eval):
            raise ItemInvalide(
                f"{item.id} : `cassettes` : {relatif!r} sort de {base_eval}",
                [f"{item.id} : `cassettes` : chemin hors de eval/"],
            )
        chemins.append(resolu)
    return chemins


# --- Rendu -----------------------------------------------------------------------------------


@dataclass(frozen=True)
class RequeteTache:
    """Requête de Tâche rendue depuis un item ; le rendu en messages relève de la story 4.1.

    `options` porte `parametres` et, selon la Tâche, `mode` (RD), `longueur_demandee` (RE)
    ou `type_courrier` (CT). `entree` et `options` sont des copies profondes.
    """

    tache: str
    entree: str | dict[str, Any]
    options: dict[str, Any] = field(default_factory=dict)


def vers_requete(item: ItemBase) -> RequeteTache:
    """Requête de Tâche de `item` (copies profondes : l'item n'est jamais modifié)."""
    options: dict[str, Any] = {"parametres": copy.deepcopy(item.parametres)}
    if isinstance(item, ItemRD):
        options["mode"] = item.mode
    elif isinstance(item, ItemRE) and item.longueur_demandee is not None:
        options["longueur_demandee"] = item.longueur_demandee
    elif isinstance(item, ItemCT) and item.type_courrier is not None:
        options["type_courrier"] = item.type_courrier
    return RequeteTache(tache=item.code, entree=copy.deepcopy(item.entree), options=options)


# --- API anti-fuite --------------------------------------------------------------------------


def _feuilles_texte(valeur: Any) -> Iterator[str]:
    if isinstance(valeur, str):
        yield valeur
    elif isinstance(valeur, BaseModel):
        yield from _feuilles_texte(valeur.model_dump())
    elif isinstance(valeur, Mapping):
        for sous in valeur.values():
            yield from _feuilles_texte(sous)
    elif isinstance(valeur, (list, tuple)):
        for sous in valeur:
            yield from _feuilles_texte(sous)


def textes_entree(item: ItemBase) -> list[str]:
    """Textes de l'entrée de l'item (chaînes de `entree`), puis `amorce_usager` s'il existe."""
    textes = list(_feuilles_texte(item.entree))
    if isinstance(item, ItemQ) and item.amorce_usager:
        textes.append(item.amorce_usager)
    return [t for t in textes if t.strip()]


def textes_reference(item: ItemBase) -> list[str]:
    """Textes des champs de référence de l'item (sans `mention_obligatoire` ni provenance)."""
    textes: list[str] = []
    for champ in item.champs_texte_reference:
        textes.extend(_feuilles_texte(getattr(item, champ, None)))
    if isinstance(item, ItemCO):
        textes.extend(faute.correction for faute in item.fautes or [])
    return [t for t in textes if t.strip()]


def _empreinte_ngramme(gramme: tuple[str, ...]) -> str:
    return sha256_hex(" ".join(gramme))[:LONGUEUR_EMPREINTE]


@dataclass(frozen=True)
class EmpreintesAntifuite:
    """N-grammes normalisés et hachés de chaque item, par clé `<version>/<id>`."""

    n: int
    version_texte: int
    par_item: Mapping[str, frozenset[str]]
    algorithme: str = f"sha256[:{LONGUEUR_EMPREINTE}] de ' '.join(n-gramme normalisé)"

    def toutes(self) -> frozenset[str]:
        """Union des empreintes de tous les items."""
        return frozenset().union(*self.par_item.values()) if self.par_item else frozenset()


@dataclass(frozen=True)
class VecteursAntifuite:
    """Vecteurs d'entrée (`#entree`) et de référence (`#reference`) par clé `<version>/<id>`."""

    cles: tuple[str, ...]
    matrice: NDArray[np.float32]


@dataclass(frozen=True)
class IdentifiantsProteges:
    """Identifiants que les Données d'entraînement ne doivent pas reprendre."""

    amorces_sha256: frozenset[str]
    """SHA-256 de `normaliser(amorce_usager)` des items Q."""
    urls: frozenset[str]
    """URL citées en provenance (et `sources_attendues` des Q)."""
    dataset_ids: frozenset[str]
    resource_ids: frozenset[str]


Versions = str | Jeu | Iterable[str | Jeu]
"""Jeux visés par l'API anti-fuite : versions (`"v1.0"`, `"calibrage"`), lues en interne,
ou objets `Jeu` déjà lus."""


def _items(versions: Versions, racine: str | Path | None) -> Iterator[tuple[Jeu, Item]]:
    liste = [versions] if isinstance(versions, (str, Jeu)) else list(versions)
    for version in liste:
        jeu = version if isinstance(version, Jeu) else lire_jeu(version, racine)
        for item in jeu.items:
            yield jeu, item


def _empreintes_texte(texte: str, n: int) -> Iterator[str]:
    grammes = ngrammes(texte, n)
    if not grammes:
        # Texte plus court que n mots : son tuple entier de jetons normalisés.
        jetons = tuple(normaliser(texte).split())
        grammes = [jetons] if jetons else []
    for gramme in grammes:
        yield _empreinte_ngramme(gramme)


def empreintes_antifuite(
    versions: Versions, n: int = N_DEFAUT, *, racine: str | Path | None = None
) -> EmpreintesAntifuite:
    """Empreintes des n-grammes (`core.texte.ngrammes`) de l'entrée, de l'amorce et des
    références de chaque item, hachées en SHA-256 tronqué à 16 hex. Un texte de moins de
    `n` mots donne l'empreinte de son tuple entier de jetons. Aucun texte renvoyé."""
    if n < 1:
        raise ValueError(f"n doit valoir au moins 1 (reçu {n})")
    par_item: dict[str, frozenset[str]] = {}
    for jeu, item in _items(versions, racine):
        empreintes = {
            empreinte
            for texte in textes_entree(item) + textes_reference(item)
            for empreinte in _empreintes_texte(texte, n)
        }
        par_item[jeu.cle(item)] = frozenset(empreintes)
    return EmpreintesAntifuite(n=n, version_texte=VERSION_TEXTE, par_item=par_item)


def vecteurs_antifuite(
    versions: Versions, embedder: EmbedderPort, *, racine: str | Path | None = None
) -> VecteursAntifuite:
    """Vecteurs de l'entrée de chaque item et de sa référence si elle existe.

    Clés `<version>/<id>#entree` et `<version>/<id>#reference`, dans l'ordre des lignes de
    la matrice. Un seul appel à `embedder.vectoriser`.
    """
    import numpy as np

    cles: list[str] = []
    textes: list[str] = []
    for jeu, item in _items(versions, racine):
        entree = textes_entree(item)
        if entree:
            cles.append(f"{jeu.cle(item)}#entree")
            textes.append("\n".join(entree))
        reference = textes_reference(item)
        if reference:
            cles.append(f"{jeu.cle(item)}#reference")
            textes.append("\n".join(reference))
    if not textes:
        return VecteursAntifuite(cles=(), matrice=np.zeros((0, embedder.dimension), np.float32))
    matrice = np.asarray(embedder.vectoriser(textes), dtype=np.float32)
    attendu = (len(textes), embedder.dimension)
    if matrice.ndim != 2 or matrice.shape != attendu:
        raise ValueError(f"l'embedder a renvoyé une matrice {matrice.shape}, attendu {attendu}")
    return VecteursAntifuite(cles=tuple(cles), matrice=matrice)


_CLES_DATASET: Final = ("dataset_id",)
_CLES_RESOURCE: Final = ("resource_id",)


def identifiants_proteges(
    versions: Versions, *, racine: str | Path | None = None
) -> IdentifiantsProteges:
    """Empreintes des amorces, URL de provenance, `dataset_id` et `resource_id` du jeu."""
    amorces: set[str] = set()
    urls: set[str] = set()
    datasets: set[str] = set()
    ressources: set[str] = set()
    for _, item in _items(versions, racine):
        for provenance in item.provenance:
            if provenance.url:
                urls.add(provenance.url)
        if isinstance(item, ItemQ):
            amorce = normaliser(item.amorce_usager or "")
            if amorce:
                amorces.add(sha256_hex(amorce))
            urls.update(u for u in item.sources_attendues or [] if u)
        if isinstance(item, ItemRD):
            for appel in item.appels_attendus or []:
                valeurs: dict[str, list[Any]] = {}
                for nom, valeur in appel.arguments.items():
                    valeurs.setdefault(nom, []).append(valeur)
                if appel.regles is not None:
                    for nom, regle in appel.regles.arguments.items():
                        if regle.a_exact:
                            valeurs.setdefault(nom, []).append(regle.exact)
                for nom, liste in valeurs.items():
                    cible = (
                        datasets
                        if nom in _CLES_DATASET
                        else (ressources if nom in _CLES_RESOURCE else None)
                    )
                    if cible is not None:
                        cible.update(
                            str(v)
                            for v in liste
                            if isinstance(v, (str, int)) and not isinstance(v, bool) and v != ""
                        )
    return IdentifiantsProteges(
        amorces_sha256=frozenset(amorces),
        urls=frozenset(urls),
        dataset_ids=frozenset(datasets),
        resource_ids=frozenset(ressources),
    )


__all__ = [
    "ALIAS_LIBELLES",
    "CODES",
    "CODES_THEMATIQUES",
    "CODE_PAR_LIBELLE",
    "DIFFICULTES",
    "LIBELLES",
    "MODELES",
    "MODES_RD",
    "OUTILS_RD",
    "THEMES",
    "THEME_NON_CLASSE",
    "ActionReference",
    "AppelAttendu",
    "EmpreintesAntifuite",
    "Faute",
    "IdentifiantsProteges",
    "Item",
    "ItemBase",
    "ItemCO",
    "ItemCR",
    "ItemCT",
    "ItemInvalide",
    "ItemLC",
    "ItemNR",
    "ItemQ",
    "ItemRD",
    "ItemRE",
    "Jeu",
    "Provenance",
    "RegleArgument",
    "ReglesAppel",
    "RequeteTache",
    "VecteursAntifuite",
    "chemins_jeu",
    "empreintes_antifuite",
    "identifiants_proteges",
    "lire_items",
    "lire_jeu",
    "numero_id",
    "resoudre_cassettes",
    "textes_entree",
    "textes_reference",
    "valider_item",
    "vecteurs_antifuite",
    "vers_requete",
]
