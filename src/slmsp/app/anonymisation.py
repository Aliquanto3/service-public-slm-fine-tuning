"""Anonymisation de l'export des Retours (story 12.3, FR-20, décision Q5).

Fonction pure `anonymiser(texte) -> (texte_masque, comptes_par_motif)`. Expressions
régulières (NIR avec clé, e-mail, téléphone, IBAN avec modulo 97, adresse postale) et noms de
personnes (civilités, prénoms INSEE embarqués suivis d'un mot en majuscule). Aucun modèle,
aucune dépendance hors bibliothèque standard (AD-2). L'aperçu avant enregistrement reste le
filet de sécurité : l'heuristique des noms n'est pas exhaustive.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable
from functools import cache
from pathlib import Path

MASQUE = "[masqué]"
FICHIER_PRENOMS = Path(__file__).parent / "ressources" / "prenoms.txt"

ESPACES_INSECABLES = re.compile("[\u00a0\u202f]")  # usage courant en français (NIR, IBAN, tél.)

_MAJ = "A-ZÀ-ÖØ-Þ"
_MIN = "a-zà-öø-ÿ"

# -- NIR ---------------------------------------------------------------------------------

_NIR = re.compile(
    r"(?<!\w)[12](?:[ .]?\d{2}){2}[ .]?(?:\d{2}|2[AB])[ .]?\d{3}[ .]?\d{3}[ .]?\d{2}(?!\w)"
)


def nir_valide(candidat: str) -> bool:
    """Clé de contrôle d'un NIR (15 caractères ; Corse 2A/2B comptés 19/18)."""
    brut = re.sub(r"[ .]", "", candidat).upper()
    if len(brut) != 15:
        return False
    base = brut[:13].replace("2A", "19").replace("2B", "18")
    if not (base.isdigit() and brut[13:].isdigit()):
        return False
    return 97 - int(base) % 97 == int(brut[13:])


# -- IBAN --------------------------------------------------------------------------------

_IBAN = re.compile(r"(?<!\w)[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){2,7}(?: ?[A-Z0-9]{1,3})?(?!\w)")


def iban_valide(candidat: str) -> bool:
    """Contrôle modulo 97 (ISO 13616) d'un IBAN de 15 à 34 caractères."""
    brut = candidat.replace(" ", "").upper()
    if not 15 <= len(brut) <= 34 or not brut.isalnum():
        return False
    rotation = brut[4:] + brut[:4]
    return int("".join(str(int(c, 36)) for c in rotation)) % 97 == 1


def _iban_plus_long_valide(brut: str) -> str:
    """Plus long préfixe valide du candidat (les mots qui suivent ne sont pas masqués)."""
    while brut:
        if iban_valide(brut):
            return brut
        coupe = brut.rfind(" ")
        brut = brut[:coupe] if coupe > 0 else ""
    return ""


# -- autres motifs -----------------------------------------------------------------------

_EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_TEL_FR = re.compile(r"(?<![\w+])(?:(?:\+|00)33[ .-]?\(?0?\)?|0)[1-9](?:[ .-]?\d{2}){4}(?!\w)")
_TEL_INTERNATIONAL = re.compile(
    r"(?<![\w+])(?:\+|00)[1-9]\d{0,2}(?:[ .-]?\(?\d{1,4}\)?){2,6}(?!\w)"
)
_VOIES = (
    "rue|avenue|av\\.?|boulevard|bd|chemin|impasse|place|allée|allee|route|quai|cours|square|"
    "passage|voie|cité|résidence|lotissement|faubourg|esplanade|sentier|ruelle"
)
_ADRESSE = re.compile(
    rf"(?<!\w)\d{{1,4}}(?: ?(?:bis|ter|quater))?,? +(?:{_VOIES}) +[^\n,;]{{1,60}}?,? *"
    rf"\b\d{{5}}\b(?!\s*(?:€|\$|%|euros?\b|eur\b|dollars?\b))"
    rf"(?: +[{_MAJ}][\w'’-]*(?: +[{_MAJ}][\w'’-]*){{0,3}})?",
    re.IGNORECASE,
)
_MOT_NOM = rf"[{_MAJ}][{_MIN}{_MAJ}'’-]+"
_CIVILITE = re.compile(
    rf"(?<!\w)(?:M\.|MM\.|Mme|Mlle|Monsieur|Madame|Mademoiselle|Maître|Dr|Pr)(?![{_MIN}])"
    rf" +{_MOT_NOM}(?: +{_MOT_NOM}){{0,2}}"
)
_MOT = re.compile(rf"(?<![\w'’-])[{_MAJ}][{_MAJ}{_MIN}'’-]+")


def _plier(mot: str) -> str:
    """Minuscules sans accents, pour comparer aux prénoms."""
    decompose = unicodedata.normalize("NFD", mot.lower())
    return "".join(c for c in decompose if not unicodedata.combining(c))


def lire_prenoms(chemin: Path | None = None) -> frozenset[str]:
    """Prénoms (un par ligne, `#` commentaire) ; ensemble vide si le fichier est absent."""
    source = chemin or FICHIER_PRENOMS
    if not source.is_file():
        return frozenset()
    lignes = source.read_text(encoding="utf-8").splitlines()
    return frozenset(_plier(ligne.strip()) for ligne in lignes if ligne.strip() and ligne[0] != "#")


def prenoms_actifs(prenoms: frozenset[str] | None = None) -> bool:
    """Vrai si la détection Prénom Nom dispose d'une liste de prénoms non vide."""
    return bool(_prenoms_embarques() if prenoms is None else prenoms)


@cache
def _prenoms_embarques() -> frozenset[str]:
    return lire_prenoms()


def _remplacer(
    motif: re.Pattern[str], texte: str, valide: Callable[[str], bool] | None = None
) -> tuple[str, int]:
    compte = 0

    def _sub(m: re.Match[str]) -> str:
        nonlocal compte
        if valide is not None and not valide(m.group(0)):
            return m.group(0)
        compte += 1
        return MASQUE

    return motif.sub(_sub, texte), compte


def _masquer_iban(texte: str) -> tuple[str, int]:
    compte = 0

    def _sub(m: re.Match[str]) -> str:
        nonlocal compte
        valide = _iban_plus_long_valide(m.group(0))
        if not valide:
            return m.group(0)
        compte += 1
        return MASQUE + m.group(0)[len(valide) :]

    return _IBAN.sub(_sub, texte), compte


# Indicatifs pays admis pour un « 00 » sans séparateur (sinon un numéro de dossier « 00… »
# serait pris pour un téléphone).
_INDICATIFS_00 = ("32", "33", "34", "39", "41", "44", "49", "212", "213", "216", "352")
_INDICATIFS_00_UN_CHIFFRE = ("1", "7")  # ambigus : exigent la longueur exacte (00 + 1 + 10)


def _telephone_plausible(candidat: str) -> bool:
    chiffres = re.sub(r"\D", "", candidat)
    if not 8 <= len(chiffres) <= 15:
        return False
    if candidat.startswith("00") and candidat.isdigit():
        reste = chiffres[2:]
        if reste.startswith(_INDICATIFS_00_UN_CHIFFRE):
            return len(chiffres) == 13
        return reste.startswith(_INDICATIFS_00) and len(chiffres) >= 10
    return True


def _masquer_telephones(texte: str) -> tuple[str, int]:
    texte, n_fr = _remplacer(_TEL_FR, texte)
    texte, n_int = _remplacer(_TEL_INTERNATIONAL, texte, _telephone_plausible)
    return texte, n_fr + n_int


def _masquer_noms(texte: str, prenoms: frozenset[str]) -> tuple[str, int]:
    texte, compte = _remplacer(_CIVILITE, texte)
    if not prenoms:
        return texte, compte
    mots = list(_MOT.finditer(texte))
    zones: list[tuple[int, int]] = []
    i = 0
    while i < len(mots) - 1:
        a, b = mots[i], mots[i + 1]
        if texte[a.end() : b.start()] == " ":
            prenom_a = _plier(a.group(0)) in prenoms
            prenom_b = _plier(b.group(0)) in prenoms
            # « Prénom Nom » (mot suivant en majuscule initiale) ; « NOM Prénom ».
            nom_prenom = a.group(0).isupper() and len(a.group(0)) > 2 and prenom_b
            if (prenom_a and not prenom_b) or (nom_prenom and not b.group(0).isupper()):
                zones.append((a.start(), b.end()))
                i += 2
                continue
        i += 1
    for debut, fin in reversed(zones):
        texte = texte[:debut] + MASQUE + texte[fin:]
    return texte, compte + len(zones)


def anonymiser(texte: str, *, prenoms: frozenset[str] | None = None) -> tuple[str, dict[str, int]]:
    """Masque les données personnelles de `texte` ; rend aussi le nombre de masques par motif.

    Les espaces insécables (U+00A0, U+202F) sont ramenées à l'espace ASCII avant détection.
    `prenoms` remplace la liste INSEE embarquée (tests). L'ordre compte : les motifs les plus
    spécifiques (IBAN, NIR) passent avant le téléphone, qui couvre des suites de chiffres.
    """
    liste = _prenoms_embarques() if prenoms is None else prenoms
    texte = ESPACES_INSECABLES.sub(" ", texte)  # même longueur : seules les espaces changent
    comptes: dict[str, int] = {}
    etapes: list[tuple[str, Callable[[str], tuple[str, int]]]] = [
        ("iban", _masquer_iban),
        ("nir", lambda t: _remplacer(_NIR, t, nir_valide)),
        ("email", lambda t: _remplacer(_EMAIL, t)),
        ("adresse", lambda t: _remplacer(_ADRESSE, t)),
        ("telephone", _masquer_telephones),
        ("nom", lambda t: _masquer_noms(t, liste)),
    ]
    for motif, etape in etapes:
        texte, comptes[motif] = etape(texte)
    return texte, comptes
