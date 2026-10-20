"""Contrôles déterministes des cibles CR, LC, CT (story O6a, méthodologie v2).

Fonctions pures, sans lecture ni écriture. Deux usages :

- **`validate`** appelle les contrôles partagés (`valeurs_absentes`, `valeurs_perdues`,
  `sections_cr_manquantes`, `ct_format_manques`, `ct_a_emplacement`, `lc_valeurs_perdues`) :
  son comportement est inchangé, la règle n'existe qu'ici ;
- **`verifier_cible`** rend la liste des `Motif` d'une cible (génération vérifiée,
  `slmsp.data.generation_verifiee`). Un motif **bloquant** refuse la cible ; un motif non
  bloquant est seulement consigné (verification.jsonl, rapport). Les codes partagés avec `validate`
  (`CODES_VALIDATE`) sont toujours bloquants : une cible acceptée ici n'est jamais rejetée
  ensuite par `validate`.

Les `extraits` d'un motif sont des sous-chaînes exactes de la cible ou de la source (jamais un
texte rédigé par l'outillage, D1). Règles par Tâche (`[verification]` de `donnees.toml`) :

- **CR** (source : la transcription) : quatre sections dans l'ordre, plafond de mots, section
  Actions non vide, valeurs et URL présentes dans les sources, noms propres ;
- **LC** (source : le texte) : classes de modalité et de condition gardées (présence par
  classe, `lc_marqueurs`), valeurs ni ajoutées ni perdues, aucune formule de conseil ajoutée,
  aucun titre en première ligne, gain de Kandel-Moles au moins `gain_km_min` ;
- **CT** (source : les amorces) : objet et politesse (règle de `validate`), blocs détectables
  dans l'ordre (`ct_blocs`), valeurs, noms propres hors crochets ; sans emplacement entre
  crochets : motif non bloquant.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from functools import lru_cache
from typing import Any, Final

from slmsp.core.ports import Passage
from slmsp.core.texte import compter_mots, extraire_nombres, kandel_moles
from slmsp.data.config import CODES_VALIDATE, VerificationConfig
from slmsp.harness.citations import extraire_urls, urls_inventees

__all__ = [
    "SECTIONS_CR",
    "TACHES_A_VALEURS",
    "TACHES_VALEURS_CONSERVEES",
    "TACHES_VERIFIEES",
    "Motif",
    "a_section",
    "ct_a_emplacement",
    "ct_format_manques",
    "dates",
    "lc_valeurs_perdues",
    "nombres_en_lettres",
    "nombres_notables",
    "refusee",
    "sans_urls",
    "sections_cr_manquantes",
    "valeurs_absentes",
    "valeurs_perdues",
    "verifier_cible",
]

TACHES_VERIFIEES: Final = ("CR", "LC", "CT")
TACHES_A_VALEURS: Final = frozenset({"Q", "RD", "CR", "LC", "RE", "CT", "CO"})
"""Tâches dont la réponse doit rester appuyée par des valeurs de sa source."""
TACHES_VALEURS_CONSERVEES: Final = frozenset({"CO"})
"""Tâches dont la sortie doit garder toutes les valeurs notables de sa source."""
ENTIER_IGNORE_MAX: Final = 9
SECTIONS_CR: Final = ("Participants", "Points abordés", "Décisions", "Actions")
"""Titres des quatre sections d'un compte rendu (grille CR, story S5)."""


@dataclass(frozen=True)
class Motif:
    """Motif d'un contrôle : `code`, critère de la grille, bloquant ou non, message et extraits
    (sous-chaînes exactes de la cible ou de la source)."""

    code: str
    critere: str
    bloquant: bool
    message: str
    extraits: tuple[str, ...] = field(default_factory=tuple)

    def ligne(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "critere": self.critere,
            "bloquant": self.bloquant,
            "message": self.message,
            "extraits": list(self.extraits),
        }


def refusee(motifs: Iterable[Motif]) -> bool:
    """Vrai si l'un des motifs est bloquant."""
    return any(m.bloquant for m in motifs)


# --- Valeurs (règle de `validate`) -----------------------------------------------------------


def nombres_notables(texte: str) -> set[Decimal]:
    """Nombres du texte en valeur absolue, hors entiers de 0 à `ENTIER_IGNORE_MAX`."""
    return {
        abs(n)
        for n in extraire_nombres(texte)
        if not (n == n.to_integral_value() and abs(n) <= ENTIER_IGNORE_MAX)
    }


def sans_urls(texte: str) -> str:
    for url in extraire_urls(texte):
        texte = texte.replace(url, " ")
    return texte


_MOIS: Final = {
    mois: numero
    for numero, mois in enumerate(
        (
            "janvier février mars avril mai juin juillet août septembre octobre novembre décembre"
        ).split(),
        start=1,
    )
}
_DATE: Final = re.compile(
    r"(?<![\w.,/-])(?:"
    r"(?P<iso_a>\d{4})-(?P<iso_m>\d{1,2})-(?P<iso_j>\d{1,2})"
    r"|(?P<num_j>\d{1,2})[/.-](?P<num_m>\d{1,2})[/.-](?P<num_a>\d{4})"
    r"|(?P<lit_j>\d{1,2})(?:er)?\s+(?P<lit_m>[A-Za-zéèêûôîàç]+)\s+(?P<lit_a>\d{4})"
    r")(?![\w,/-]|\.\d)",
    re.IGNORECASE,
)
_ANNOTATION_MOTS: Final = re.compile(
    r"(?<![\w,.])(?:\d{1,3}(?:[    ]\d{3})+|\d+)\s*mots?\b", re.IGNORECASE
)
"""Compte de mots écrit par le générateur (« (80 mots max.) », « de 200 mots au plus ») :
seul le nombre suivi de « mots » est retiré ; le reste d'une parenthèse reste contrôlé."""
_NOMBRE: Final = re.compile(r"\d+(?:[.,    ]\d+)*")


def dates(texte: str) -> list[tuple[re.Match[str], tuple[int, int, int]]]:
    """Dates du texte (ISO, jj/mm/aaaa, « 20 avril 2021 ») avec leur forme (année, mois, jour)."""
    trouvees = []
    for m in _DATE.finditer(texte):
        if m["iso_a"]:
            a, mois, j = m["iso_a"], m["iso_m"], m["iso_j"]
        elif m["num_a"]:
            a, mois, j = m["num_a"], m["num_m"], m["num_j"]
        else:
            mois = str(_MOIS.get(m["lit_m"].lower(), 0))
            a, j = m["lit_a"], m["lit_j"]
        if 1 <= int(mois) <= 12 and 1 <= int(j) <= 31:
            trouvees.append((m, (int(a), int(mois), int(j))))
    return trouvees


def retirer_dates_connues(texte: str, connues: set[tuple[int, int, int]]) -> str:
    """Retire du texte les dates déjà présentes (sous une autre forme) dans les sources."""
    for m, forme in reversed(dates(texte)):
        if forme in connues:
            texte = texte[: m.start()] + " " + texte[m.end() :]
    return texte


def valeurs_absentes(
    texte: str,
    tache: str,
    passages: Sequence[Passage],
    outils: Sequence[str],
    fournis: Sequence[str],
) -> set[Decimal]:
    """Nombres notables de `texte` absents des sources (dates reformulées admises ; pour RE, le
    compte de mots recopié du gabarit ignoré). Vide pour une Tâche hors `TACHES_A_VALEURS`."""
    if tache not in TACHES_A_VALEURS:
        return set()
    connus: set[Decimal] = set()
    dates_connues: set[tuple[int, int, int]] = set()
    for source in (*(p.titre for p in passages), *(p.texte for p in passages), *outils, *fournis):
        connus |= {abs(n) for n in extraire_nombres(source)}
        dates_connues |= {forme for _, forme in dates(source)}
    controle = texte
    if tache == "RE":
        # Le compte de mots recopié du gabarit (« (80 mots max.) ») n'est pas une valeur du
        # résumé ; un plafond écrit comme valeur libre (« 200 euros ») reste contrôlé.
        controle = _ANNOTATION_MOTS.sub(" ", controle)
    return nombres_notables(retirer_dates_connues(sans_urls(controle), dates_connues)) - connus


def valeurs_perdues(texte: str, fournis: Sequence[str]) -> set[Decimal]:
    """Nombres notables des sources absents de `texte` (règle de fidélité de CO)."""
    perdues: set[Decimal] = set().union(*(nombres_notables(sans_urls(f)) for f in fournis))
    return perdues - nombres_notables(sans_urls(texte))


_UNITES: Final = (
    "zéro un deux trois quatre cinq six sept huit neuf dix onze douze treize quatorze quinze "
    "seize dix-sept dix-huit dix-neuf"
).split()
_DIZAINES: Final = {"vingt": 20, "trente": 30, "quarante": 40, "cinquante": 50, "soixante": 60}


def _table_nombres_en_lettres() -> dict[str, int]:
    """Nombres en lettres courants : 0 à 69, 70 à 99 (soixante-dix, quatre-vingts…), centaines
    et milliers simples (cent, deux cents… neuf cents, mille)."""
    table = {mot: n for n, mot in enumerate(_UNITES)}
    for mot, d in _DIZAINES.items():
        table[mot] = d
        table[f"{mot} et un"] = table[f"{mot}-et-un"] = d + 1
        for u in range(2, 10):
            table[f"{mot}-{_UNITES[u]}"] = d + u
    for u in range(10, 20):
        table[f"soixante-{_UNITES[u]}"] = 60 + u
    table["soixante et onze"] = table["soixante-et-onze"] = 71
    table["quatre-vingts"] = table["quatre-vingt"] = 80
    for u in range(1, 20):
        table[f"quatre-vingt-{_UNITES[u]}"] = 80 + u
    table["cent"] = 100
    for u in range(2, 10):
        table[f"{_UNITES[u]} cents"] = table[f"{_UNITES[u]}-cents"] = 100 * u
    table["mille"] = 1000
    return table


_NOMBRES_EN_LETTRES: Final = _table_nombres_en_lettres()
_RE_NOMBRE_EN_LETTRES: Final = re.compile(
    r"(?<![^\W_])(?:"
    + "|".join(re.escape(m) for m in sorted(_NOMBRES_EN_LETTRES, key=len, reverse=True))
    + r")(?![^\W_]|-)",
    re.IGNORECASE,
)


def nombres_en_lettres(texte: str) -> set[Decimal]:
    """Nombres écrits en lettres courants, pour ne pas tenir pour perdue une valeur de l'entrée
    LC reprise en lettres (« 15 jours » → « quinze jours »)."""
    return {
        Decimal(_NOMBRES_EN_LETTRES[m.group(0).casefold()])
        for m in _RE_NOMBRE_EN_LETTRES.finditer(texte)
    }


def lc_valeurs_perdues(
    texte: str, fournis: Sequence[str]
) -> tuple[set[Decimal], set[tuple[int, int, int]]]:
    """Nombres notables et dates de l'entrée LC absents de la sortie (chiffres ou lettres)."""
    sortie = sans_urls(texte)
    source = sans_urls("\n".join(fournis))
    nombres = nombres_notables(source) - nombres_notables(sortie) - nombres_en_lettres(sortie)
    perdues = {f for _, f in dates(source)} - {f for _, f in dates(sortie)}
    return nombres, perdues


# --- Structure (règle de `validate`) ---------------------------------------------------------

RE_OBJET: Final = re.compile(r"^[#*_\s]*objet\b[^\n:]{0,40}:", re.IGNORECASE | re.MULTILINE)
"""Ligne d'objet : « Objet : », « **Objet** : », « Objet du courrier : »…"""
RE_POLITESSE: Final = re.compile(
    r"\b(?:agr[ée]er|salutations|consid[ée]ration|sentiments|cordialement|respectueusement)\b",
    re.IGNORECASE,
)
RE_EMPLACEMENT: Final = re.compile(r"\[[^\[\]\n]*[^\W\d_][^\[\]\n]*\](?!\()")
"""Emplacement entre crochets qui nomme un champ (au moins une lettre), hors lien Markdown."""


def _re_section(titre: str) -> re.Pattern[str]:
    return re.compile(rf"^[#*_\s\d.)]*{re.escape(titre)}(?![^\W_])", re.IGNORECASE | re.MULTILINE)


def a_section(texte: str, titre: str) -> bool:
    """Vrai si une ligne de `texte` commence par `titre` (marques `#`, `*`, `_`, numérotation
    et casse ignorées), quelle que soit la suite du titre."""
    return _re_section(titre).search(texte) is not None


def sections_cr_manquantes(texte: str) -> list[str]:
    return [s for s in SECTIONS_CR if not a_section(texte, s)]


def ct_format_manques(texte: str) -> list[str]:
    """Blocs exigés par `validate` absents d'un CT : « objet », « formule de politesse »."""
    manques = []
    if RE_OBJET.search(texte) is None:
        manques.append("objet")
    if RE_POLITESSE.search(texte) is None:
        manques.append("formule de politesse")
    return manques


def ct_a_emplacement(texte: str) -> bool:
    return RE_EMPLACEMENT.search(texte) is not None


# --- Contrôles de la vérification --------------------------------------------------------------


def _sans_accents(texte: str) -> str:
    decompose = unicodedata.normalize("NFD", texte.casefold())
    return "".join(c for c in decompose if not unicodedata.combining(c))


_MOT: Final = re.compile(r"[^\W\d_][\w-]*")
_DEBUT_DE_LIGNE: Final = re.compile(r"[\s#*_>\-•·–—\d.)(\[]*")
_MARQUES: Final = " \t*_"
_CROCHETS: Final = re.compile(r"\[[^\[\]\n]*\]")


def _noms_absents(cible: str, source: str, exceptions: frozenset[str]) -> list[str]:
    """Mots capitalisés de `cible` absents de `source` (casse et accents ignorés), hors début
    de ligne, hors mot après `.`, `!`, `?`, `:`, puce ou numéro, hors exceptions."""
    source_norm = _sans_accents(source)
    absents: list[str] = []
    for ligne in cible.splitlines():
        for m in _MOT.finditer(ligne):
            mot = m.group(0)
            if not mot[0].isupper() or len(mot) < 2:
                continue
            avant = ligne[: m.start()]
            if _DEBUT_DE_LIGNE.fullmatch(avant):
                continue
            if avant.rstrip(_MARQUES)[-1:] in (".", "!", "?", ":"):
                continue
            norm = _sans_accents(mot)
            if norm in exceptions or mot in absents:
                continue
            if re.search(rf"(?<!\w){re.escape(norm)}(?!\w)", source_norm) is None:
                absents.append(mot)
    return absents


def _extraits_nombres(texte: str, valeurs: set[Decimal]) -> tuple[str, ...]:
    """Sous-chaînes de `texte` qui portent l'une des `valeurs`."""
    extraits: list[str] = []
    for m in _NOMBRE.finditer(texte):
        if {abs(n) for n in extraire_nombres(m.group(0))} & valeurs and m.group(0) not in extraits:
            extraits.append(m.group(0))
    return tuple(extraits)


@lru_cache(maxsize=64)
def _compiler(expressions: tuple[str, ...], multiligne: bool = False) -> re.Pattern[str]:
    drapeaux = re.IGNORECASE | (re.MULTILINE if multiligne else 0)
    return re.compile("|".join(f"(?:{e})" for e in expressions), drapeaux)


class _Collecte:
    """Motifs d'une cible ; le caractère bloquant suit `non_bloquants` (sauf `CODES_VALIDATE`)."""

    def __init__(self, config: VerificationConfig) -> None:
        self.non_bloquants = frozenset(config.non_bloquants) - CODES_VALIDATE
        self.motifs: list[Motif] = []

    def ajouter(
        self,
        code: str,
        critere: str,
        message: str,
        extraits: Iterable[str] = (),
        *,
        bloquant: bool = True,
    ) -> None:
        bloquant = bloquant and code not in self.non_bloquants
        self.motifs.append(Motif(code, critere, bloquant, message, tuple(extraits)))


def _controles_communs(
    c: _Collecte, tache: str, cible: str, fournis: Sequence[str], passages: Sequence[Passage]
) -> None:
    inventees = urls_inventees(cible, passages, (), fournis)
    if inventees:
        c.ajouter("url_inventee", "exactitude", f"{len(inventees)} URL absente(s)", inventees)
    absentes = valeurs_absentes(cible, tache, passages, (), fournis)
    if absentes:
        c.ajouter(
            "valeur_absente",
            "exactitude",
            f"{len(absentes)} valeur(s) absente(s) des sources",
            _extraits_nombres(cible, absentes),
        )


def _controles_noms(c: _Collecte, cible: str, source: str, config: VerificationConfig) -> None:
    exceptions = frozenset(_sans_accents(e) for e in config.exceptions_noms)
    absents = _noms_absents(cible, source, exceptions)
    if absents:
        message = f"{len(absents)} nom(s) absent(s) de la source"
        c.ajouter("nom_absent", "exactitude", message, absents)


def _titre_section(texte: str, titre: str) -> re.Match[str] | None:
    """Titre de section : de préférence une ligne qui ne porte que le titre (marques,
    deux-points, parenthèse), pour qu'une puce « Actions de … » d'une autre section ne soit
    pas prise pour lui (revue O6a) ; sinon la première ligne qui commence par le titre."""
    for m in _re_section(titre).finditer(texte):
        fin = texte.find("\n", m.end())
        reste = texte[m.end() : len(texte) if fin < 0 else fin]
        if re.fullmatch(r"[\s:*_#]*(?:\([^)\n]*\))?[\s:*_#]*", reste):
            return m
    return _re_section(titre).search(texte)


def _controles_cr(
    c: _Collecte, cible: str, transcription: str, config: VerificationConfig, plafond: int | None
) -> None:
    manquantes = sections_cr_manquantes(cible)
    if manquantes:
        message = f"sections absentes : {', '.join(manquantes)}"
        c.ajouter("cr_sections_manquantes", "structure", message)
    else:
        trouvees = [_titre_section(cible, s) for s in SECTIONS_CR]
        positions = [m.start() for m in trouvees if m is not None]
        if positions != sorted(positions):
            c.ajouter("cr_sections_desordre", "structure", "sections hors de l'ordre attendu")
        debut = _titre_section(cible, "Actions")
        assert debut is not None
        suite = cible[debut.end() :]
        if re.search(r"[^\W\d_]{2,}", suite) is None:
            c.ajouter("cr_actions_vide", "couverture", "section Actions vide")
    if plafond is not None and (mots := compter_mots(cible)) > plafond:
        c.ajouter("cr_plafond_mots", "concision", f"{mots} mots pour un plafond de {plafond}")
    _controles_noms(c, cible, transcription, config)


def _premiere_ligne_titre(cible: str) -> str | None:
    lignes = [ligne for ligne in cible.splitlines() if ligne.strip()]
    if not lignes:
        return None
    premiere = lignes[0].strip()
    if premiere.startswith("#") or re.fullmatch(r"\*\*[^*]+\*\*\s*:?", premiere):
        return lignes[0]
    courte = compter_mots(premiere) <= 10 and premiere[-1] not in ".!?:;…,»)"
    return lignes[0] if courte and len(lignes) > 1 else None


def _controles_lc(
    c: _Collecte, cible: str, source: str, fournis: Sequence[str], config: VerificationConfig
) -> None:
    nombres, perdues = lc_valeurs_perdues(cible, fournis)
    if nombres or perdues:
        entree = "\n".join(fournis)
        extraits = list(_extraits_nombres(entree, nombres))
        extraits += [m.group(0) for m, forme in dates(entree) if forme in perdues]
        c.ajouter(
            "lc_valeur_perdue",
            "fidelite",
            f"{len(nombres)} nombre(s) et {len(perdues)} date(s) de l'entrée perdus",
            extraits,
        )
    perdues_classes, reduites = [], []
    extraits_classes: list[str] = []
    for classe, expressions in config.lc_marqueurs.items():
        motif = _compiler(tuple(expressions))
        dans_source = [m.group(0) for m in motif.finditer(source)]
        if not dans_source:
            continue
        dans_cible = len(motif.findall(cible))
        if dans_cible == 0:
            perdues_classes.append(classe)
            extraits_classes.append(dans_source[0])
        elif dans_cible < len(dans_source):
            reduites.append(classe)
    if perdues_classes:
        c.ajouter(
            "lc_modalite_perdue",
            "fidelite",
            f"classe(s) absente(s) de la cible : {', '.join(perdues_classes)}",
            extraits_classes,
        )
    if reduites:
        c.ajouter(
            "lc_modalite_reduite",
            "fidelite",
            f"moins de marqueurs que la source : {', '.join(reduites)}",
            bloquant=False,
        )
    conseil = _compiler(tuple(config.lc_conseils))
    ajoutes = [m.group(0) for m in conseil.finditer(cible) if conseil.search(source) is None]
    if ajoutes:
        message = "formule de conseil absente de la source"
        c.ajouter("lc_conseil_ajoute", "fidelite", message, ajoutes)
    titre = _premiere_ligne_titre(cible)
    if titre is not None:
        c.ajouter("lc_titre", "structure", "titre en première ligne", [titre])
    try:
        gain = kandel_moles(cible) - kandel_moles(source)
    except ValueError:
        gain = float("-inf")
    if gain < config.gain_km_min:
        c.ajouter(
            "lc_gain_lisibilite",
            "lisibilite",
            f"gain de Kandel-Moles {gain:.1f} sous le minimum {config.gain_km_min:g}",
        )


def _plus_longue_suite(positions: Mapping[str, Sequence[int]]) -> set[str]:
    """Plus grand ensemble de blocs trouvés dans l'ordre de `positions` (une occurrence choisie
    par bloc, positions strictement croissantes) : les autres blocs trouvés sont hors d'ordre."""
    etats: dict[int, tuple[int, tuple[str, ...]]] = {0: (-1, ())}  # taille : (fin, blocs)
    for nom, trouvees in positions.items():
        for taille, (fin, blocs) in sorted(etats.items(), reverse=True):
            suivante = next((p for p in trouvees if p > fin), None)
            meilleure = etats.get(taille + 1)
            if suivante is not None and (meilleure is None or suivante < meilleure[0]):
                etats[taille + 1] = (suivante, (*blocs, nom))
    return set(etats[max(etats)][1])


def _controles_ct(c: _Collecte, cible: str, amorces: str, config: VerificationConfig) -> None:
    manques = ct_format_manques(cible)
    if manques:
        c.ajouter("ct_format_incomplet", "conformite", f"absents : {', '.join(manques)}")
    positions = {
        nom: [m.start() for m in _compiler((expression,), multiligne=True).finditer(cible)]
        for nom, expression in config.ct_blocs.items()
    }
    absents = [nom for nom, trouvees in positions.items() if not trouvees]
    ordonnes = _plus_longue_suite(positions)
    desordre = [nom for nom, trouvees in positions.items() if trouvees and nom not in ordonnes]
    if absents or desordre:
        detail = "; ".join(
            texte
            for texte in (
                f"absents : {', '.join(absents)}" if absents else "",
                f"hors d'ordre : {', '.join(desordre)}" if desordre else "",
            )
            if texte
        )
        c.ajouter("ct_blocs", "conformite", detail)
    if not ct_a_emplacement(cible):
        message = "aucun emplacement entre crochets"
        c.ajouter("ct_sans_emplacement", "conformite", message, bloquant=False)
    hors_crochets = _CROCHETS.sub(lambda m: " " * len(m.group(0)), cible)
    _controles_noms(c, hors_crochets, amorces, config)


def verifier_cible(
    tache: str,
    cible: str,
    *,
    source: str,
    fournis: Sequence[str],
    config: VerificationConfig,
    plafonds_mots: Mapping[str, int] | None = None,
    passages: Sequence[Passage] = (),
) -> list[Motif]:
    """Motifs des contrôles déterministes de `cible` (Tâche CR, LC ou CT).

    `source` : texte de référence de la Tâche (CR : transcription ; LC : texte ; CT : amorces) ;
    `fournis` : sources des valeurs et URL, comme `validate` (textes d'amorces, plus la
    transcription pour CR).
    """
    if tache not in TACHES_VERIFIEES:
        raise ValueError(f"Tâche {tache!r} non vérifiée ({', '.join(TACHES_VERIFIEES)} attendues)")
    c = _Collecte(config)
    _controles_communs(c, tache, cible, fournis, passages)
    if tache == "CR":
        plafond = (plafonds_mots or {}).get("CR")
        _controles_cr(c, cible, source, config, plafond)
    elif tache == "LC":
        _controles_lc(c, cible, source, fournis, config)
    else:
        _controles_ct(c, cible, source, config)
    return c.motifs
