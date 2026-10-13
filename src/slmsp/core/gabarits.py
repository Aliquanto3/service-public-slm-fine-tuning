"""Validation structurelle des gabarits de prompt (AD-3 verrou 6, D1.1, D-nuit-A2-8).

Un gabarit est un fichier Markdown fait d'un front-matter simple puis de deux sections :

    ---
    id: <identifiant>
    version: <entier >= 1>
    tache: <code>
    ---

    ## Consigne
    <consignes rédigées par le projet>

    ## Emplacements
    - <nom> : <description>

La validation est une liste blanche : tout ce qui pourrait porter un exemple de sortie
(bloc de code, JSON, citation, ligne de dialogue, mot « exemple », jeton de chat) est
refusé. `valider_gabarit` rassemble toutes les fautes avant de lever `GabaritInvalide`.
Ce module est en couche 0 : il n'importe que `core`.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Final

from slmsp.core.canonique import sha256_hex
from slmsp.core.erreurs import SlmspError

LONGUEUR_MAX: Final = 4000
"""Longueur maximale d'un gabarit, en caractères (fins de ligne normalisées en LF)."""

TITRE_CONSIGNE: Final = "## Consigne"
TITRE_EMPLACEMENTS: Final = "## Emplacements"

_RE_CLE = re.compile(r"[a-z_][a-z0-9_]*")
_RE_VERSION = re.compile(r"[1-9][0-9]*")
_RE_EMPLACEMENT = re.compile(r"- ([a-z_]+) : (\S.*)")
_RE_TITRE = re.compile(r" {0,3}#")
_RE_SOULIGNEMENT = re.compile(r" {0,3}(=+|-{2,}|\*{3,}|_{3,})\s*")
_RE_CLOTURE_TILDE = re.compile(r" {0,3}~~~")
_RE_IDENTIFIANT = re.compile(r"\{[a-z_]+\}")

# Motifs comparés sur le texte sans accent et en minuscules.
_MOTS_INTERDITS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    ("« exemple »", re.compile(r"exempl")),
    ("« example »", re.compile(r"exampl")),
    ("« par ex »", re.compile(r"\bpar ex\b")),
    ("« e.g. »", re.compile(r"\be\s*\.\s*g\b")),
    ("« few-shot »", re.compile(r"few\s*-?\s*shots?")),
    ("« réponse type »", re.compile(r"\breponses?[\s-]+types?\b")),
    ("« modèle de réponse »", re.compile(r"\bmodeles? de reponses?\b")),
    ("« voici »", re.compile(r"\bvoici\b")),
    ("« réponse attendue »", re.compile(r"\b(?:reponse|sortie)s?\s+attendues?\b")),
    ("« i.e. »", re.compile(r"\bi\s*\.\s*e\b")),
    ("« p. ex. »", re.compile(r"\bp\s*\.\s*ex\b")),
    ("« ex. »", re.compile(r"\bex\s*\.")),
)
_ROLES = (
    "question|reponse|q|r|utilisateur|assistant|agent|usager|systeme|system|"
    "entree|sortie|user|input|output"
)
_RE_DIALOGUE = re.compile(rf"\s*(?:[-*+]\s+|\d+[.)]\s+)?[*_«\s]*(?:{_ROLES})[*_»\s]*:")
_RE_JETON_CHAT = re.compile(
    r"<\||\|>|\[/?inst\]|<<\s*/?sys\s*>>|</?s>|<(?:start|end)_of_turn>|<bos>|<eos>"
)


class GabaritInvalide(SlmspError):
    """Gabarit non conforme ; `fautes` liste toutes les fautes relevées."""

    def __init__(self, message: str, fautes: Sequence[str] = ()):
        super().__init__(message)
        self.fautes: tuple[str, ...] = tuple(fautes)


@dataclass(frozen=True)
class GabaritValide:
    """Gabarit conforme.

    `consigne` est le texte de la section « Consigne », sans lignes vides en tête ni en
    fin ; `emplacements` associe chaque nom déclaré à sa description, dans l'ordre du
    fichier ; `sha256` est l'empreinte des octets du fichier (ou du texte en UTF-8).
    """

    id: str
    version: int
    front_matter: Mapping[str, str]
    consigne: str
    emplacements: Mapping[str, str]
    sha256: str


def _sans_accent(texte: str) -> str:
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c)).casefold()


def _decode_en_json(ligne: str) -> bool:
    try:
        json.loads(ligne)
    except (ValueError, RecursionError):
        return False
    return True


def _indentation_interdite(ligne: str) -> bool:
    """Ligne non vide indentée d'au moins 4 colonnes, ou dont l'indentation a une tabulation."""
    if not ligne.strip():
        return False
    tete = ligne[: len(ligne) - len(ligne.lstrip(" \t"))]
    return "\t" in tete or len(tete) >= 4


def _verifier_contenu(lignes: list[str], fautes: list[str]) -> None:
    """Règles de contenu, appliquées à toutes les lignes du fichier.

    Les tests de forme (backtick, accolade, JSON, citation) portent sur la ligne en NFKC,
    pour que les formes pleine chasse (« ｀ », « ＞ », « ｛ ») ne les contournent pas. Un
    caractère de format invisible (catégorie Unicode `Cf`, espace de largeur nulle…) est
    refusé : il couperait un mot interdit sans le rendre illisible pour le modèle.
    """
    for numero, ligne in enumerate(lignes, start=1):
        lieu = f"ligne {numero}"
        pliee = unicodedata.normalize("NFKC", ligne)
        if any(unicodedata.category(c) == "Cf" for c in ligne):
            fautes.append(f"{lieu} : caractère de format invisible interdit")
        if "`" in pliee:
            fautes.append(f"{lieu} : caractère backtick interdit (bloc ou code en ligne)")
        if _indentation_interdite(ligne):
            fautes.append(f"{lieu} : bloc indenté (4 espaces ou tabulation) interdit")
        if _RE_CLOTURE_TILDE.match(pliee):
            fautes.append(f"{lieu} : bloc de code « ~~~ » interdit")
        if "{" in _RE_IDENTIFIANT.sub("", pliee) or "}" in _RE_IDENTIFIANT.sub("", pliee):
            fautes.append(f"{lieu} : accolade interdite hors emplacement {{identifiant}}")
        if pliee.strip() and _decode_en_json(pliee.strip()):
            fautes.append(f"{lieu} : ligne qui se décode en JSON")
        if pliee.lstrip().startswith(">"):
            fautes.append(f"{lieu} : citation « > » interdite")
        normalisee = _sans_accent(ligne)
        for libelle, motif in _MOTS_INTERDITS:
            if motif.search(normalisee):
                fautes.append(f"{lieu} : mot interdit {libelle}")
        if _RE_JETON_CHAT.search(normalisee):
            fautes.append(f"{lieu} : jeton de chat interdit")
    # Un mot interdit coupé par un retour à la ligne (« few- » puis « shot ») : repéré sur le
    # texte aplati, seulement s'il n'est trouvé sur aucune ligne prise seule.
    normalisees = [_sans_accent(ligne) for ligne in lignes]
    aplati = " ".join(normalisees)
    for libelle, motif in _MOTS_INTERDITS:
        if motif.search(aplati) and not any(motif.search(ligne) for ligne in normalisees):
            fautes.append(f"mot interdit {libelle} coupé par un retour à la ligne")


def _lire_front_matter(
    lignes: list[str],
    cles_requises: Sequence[str],
    cles_optionnelles: Sequence[str],
    fautes: list[str],
) -> tuple[dict[str, str], int | None]:
    """Front-matter et indice de la première ligne du corps (`None` si absent)."""
    if not lignes or lignes[0] != "---":
        fautes.append("front-matter absent : la première ligne doit être « --- »")
        return {}, None
    try:
        fin = lignes.index("---", 1)
    except ValueError:
        fautes.append("front-matter non fermé : ligne « --- » de fin absente")
        return {}, None
    front: dict[str, str] = {}
    admises = set(cles_requises) | set(cles_optionnelles)
    for numero in range(1, fin):
        ligne = lignes[numero]
        lieu = f"ligne {numero + 1}"
        cle, separateur, valeur = ligne.partition(":")
        cle, valeur = cle.strip(), valeur.strip()
        if not separateur or not _RE_CLE.fullmatch(cle):
            fautes.append(f"{lieu} : front-matter : ligne « cle: valeur » attendue")
            continue
        if cle in front:
            fautes.append(f"{lieu} : front-matter : clé « {cle} » en double")
            continue
        if cle not in admises:
            fautes.append(f"{lieu} : front-matter : clé « {cle} » non admise")
        if not valeur:
            fautes.append(f"{lieu} : front-matter : clé « {cle} » sans valeur")
        front[cle] = valeur
    for cle in cles_requises:
        if cle not in front:
            fautes.append(f"front-matter : clé « {cle} » manquante")
    if "version" in front and front["version"] and not _RE_VERSION.fullmatch(front["version"]):
        fautes.append("front-matter : « version » doit être un entier supérieur ou égal à 1")
    return front, fin + 1


def _lire_corps(lignes: list[str], debut: int, fautes: list[str]) -> tuple[str, dict[str, str]]:
    """Section « Consigne » et emplacements déclarés."""
    titres: list[tuple[int, str]] = []
    for indice in range(debut, len(lignes)):
        ligne = lignes[indice]
        if _RE_TITRE.match(ligne):
            titres.append((indice, ligne.rstrip()))
        elif _RE_SOULIGNEMENT.fullmatch(ligne):
            fautes.append(f"ligne {indice + 1} : soulignement ou séparateur interdit")
    if [titre for _, titre in titres] != [TITRE_CONSIGNE, TITRE_EMPLACEMENTS]:
        trouves = ", ".join(f"ligne {indice + 1}" for indice, _ in titres) or "aucun"
        fautes.append(
            f"corps : titres attendus « {TITRE_CONSIGNE} » puis « {TITRE_EMPLACEMENTS} » "
            f"seulement (trouvés : {trouves})"
        )
        return "", {}
    (i_consigne, _), (i_emplacements, _) = titres
    for indice in range(debut, i_consigne):
        if lignes[indice].strip():
            fautes.append(f"ligne {indice + 1} : texte hors section")
    lignes_consigne = lignes[i_consigne + 1 : i_emplacements]
    for decalage, ligne in enumerate(lignes_consigne):
        if _RE_DIALOGUE.match(_sans_accent(ligne)):
            fautes.append(f"ligne {i_consigne + 2 + decalage} : ligne de dialogue interdite")
    consigne = "\n".join(lignes_consigne).strip("\n")
    if not consigne.strip():
        fautes.append("section « Consigne » vide")
    emplacements: dict[str, str] = {}
    for indice in range(i_emplacements + 1, len(lignes)):
        ligne = lignes[indice]
        if not ligne.strip():
            continue
        lieu = f"ligne {indice + 1}"
        correspondance = _RE_EMPLACEMENT.fullmatch(ligne.rstrip())
        if correspondance is None:
            fautes.append(f"{lieu} : emplacement « - nom : description » attendu, nom en [a-z_]+")
            continue
        nom, description = correspondance.groups()
        if nom in emplacements:
            fautes.append(f"{lieu} : emplacement « {nom} » en double")
            continue
        if _RE_DIALOGUE.match(_sans_accent(description)):
            fautes.append(f"{lieu} : ligne de dialogue interdite")
        emplacements[nom] = description
    if not emplacements:
        fautes.append("section « Emplacements » vide")
    return consigne, emplacements


def valider_gabarit(
    source: Path | str,
    *,
    cles_requises: Sequence[str] = ("id", "version", "tache"),
    cles_optionnelles: Sequence[str] = (),
    longueur_max: int = LONGUEUR_MAX,
) -> GabaritValide:
    """Valide un gabarit (`Path` vers le fichier, ou son texte) et le renvoie analysé.

    Lève `GabaritInvalide` avec la liste de toutes les fautes. Le message ne recopie
    jamais le contenu du gabarit, seulement les numéros de ligne et la règle violée.
    """
    nom = str(source) if isinstance(source, Path) else "gabarit"
    if isinstance(source, Path):
        try:
            octets = source.read_bytes()
        except OSError as exc:
            raise GabaritInvalide(
                f"{nom} : gabarit illisible ({type(exc).__name__})",
                [f"fichier illisible ({type(exc).__name__})"],
            ) from None
        try:
            texte = octets.decode("utf-8")
        except UnicodeDecodeError:
            raise GabaritInvalide(f"{nom} : gabarit non UTF-8", ["fichier non UTF-8"]) from None
    else:
        texte = source
        octets = texte.encode("utf-8")
    texte = texte.removeprefix("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    lignes = texte.split("\n")
    if lignes and lignes[-1] == "":
        lignes.pop()

    fautes: list[str] = []
    if len(texte) > longueur_max:
        fautes.append(f"longueur {len(texte)} caractères, au-delà du maximum {longueur_max}")
    front, debut = _lire_front_matter(lignes, cles_requises, cles_optionnelles, fautes)
    consigne, emplacements = ("", {}) if debut is None else _lire_corps(lignes, debut, fautes)
    _verifier_contenu(lignes, fautes)
    if fautes:
        raise GabaritInvalide(
            f"{nom} : gabarit non conforme ({len(fautes)} faute(s)) :\n- " + "\n- ".join(fautes),
            fautes,
        )
    return GabaritValide(
        id=front.get("id", ""),
        version=int(front["version"]) if "version" in front else 0,
        front_matter=MappingProxyType(dict(front)),
        consigne=consigne,
        emplacements=MappingProxyType(emplacements),
        sha256=sha256_hex(octets),
    )
