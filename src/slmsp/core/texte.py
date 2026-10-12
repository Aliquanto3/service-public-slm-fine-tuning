"""Fonctions de texte partagées : normalisation, mots, phrases, nombres, n-grammes, Kandel-Moles.

Source unique des calculs de texte (AD-29) : le banc (scores LC, RE, CO, RD), l'API anti-fuite
(n-grammes normalisés) et l'outil de construction du jeu (Epic 7) importent ce module, et
personne ne recode ces règles ailleurs.

Le module n'importe que la bibliothèque standard, jamais `slmsp` ni un paquet tiers :
l'outil de l'Epic 7 le charge par chemin de fichier, en `--no-project`.

Deux unités coexistent : les mots (`compter_mots`, `kandel_moles`) sont les jetons séparés
par des blancs, donc « l'usager » compte pour 1 mot, alors que `ngrammes` travaille sur
`normaliser(texte).split()`, où « l'usager » donne 2 jetons.

Règle de version : toute modification d'une règle impose d'incrémenter `VERSION_TEXTE` ;
le test le vérifie sur un corpus de référence.
"""

from __future__ import annotations

import re
import unicodedata
from decimal import Decimal
from itertools import groupby

__all__ = [
    "VERSION_TEXTE",
    "compter_mots",
    "decouper_phrases",
    "extraire_nombres",
    "kandel_moles",
    "ngrammes",
    "normaliser",
    "syllabes",
]

VERSION_TEXTE: int = 1

_VOYELLES = frozenset("aeiouyàâäéèêëîïôöùûüÿæœ")

# Coupure de phrase : un blanc précédé de `.`, `!`, `?` ou `…` (répétés ou non).
_FIN_DE_PHRASE = re.compile(r"(?<=[.!?…])\s+")

# Nombres à la française. Le chiffre de tête ne doit pas être collé à une lettre ou à un
# chiffre (`[^\W_]` = caractère alphanumérique) ; le signe n'est pris que s'il n'est pas
# collé à un caractère de mot (`\w`). Un chiffre qui suit « <chiffre>. » ou « <chiffre>, »
# n'ouvre jamais un nombre : la queue de « v2.5 » ou de « 1.234.567 » n'est pas reprise.
_SEPARATEURS_MILLIERS = " \u00a0\u202f\u2009"
_NOMBRE = re.compile(
    r"(?:(?<!\w)(?P<signe>[-\u2212]))?"
    r"(?<![^\W_])"
    r"(?<![0-9][.,])"
    r"(?:"
    # « 1.234,56 » : point séparateur de milliers, seulement devant une virgule décimale.
    r"(?P<points>[0-9]{1,3}(?:\.[0-9]{3})+,[0-9]+)"
    # « 1 234,56 » : espace (ou NBSP, espace fine, espace fine insécable) entre groupes de 3.
    rf"|(?P<groupes>[0-9]{{1,3}}(?:[{_SEPARATEURS_MILLIERS}][0-9]{{3}}(?![0-9]))+"
    r"(?:[,.][0-9]+)?)"
    # « 25 », « 12,50 », « 3.5 ».
    r"|(?P<simple>[0-9]+(?:[,.][0-9]+)?)"
    r")"
)


def normaliser(texte: str) -> str:
    """Normalise un texte pour les comparaisons et les n-grammes (version 1).

    Règle : NFKC, minuscules, NFKC à nouveau ; tout caractère de catégorie Unicode `P*`
    (ponctuation) devient une espace ; les espaces sont fusionnées et les bords supprimés.
    La fonction est idempotente : `normaliser(normaliser(x)) == normaliser(x)`.
    """
    texte = unicodedata.normalize("NFKC", unicodedata.normalize("NFKC", texte).lower())
    texte = "".join(" " if unicodedata.category(c).startswith("P") else c for c in texte)
    return " ".join(texte.split())


def _est_mot(jeton: str) -> bool:
    return any(c.isalnum() for c in jeton)


def _mots(texte: str) -> list[str]:
    return [jeton for jeton in texte.split() if _est_mot(jeton)]


def compter_mots(texte: str) -> int:
    """Compte les mots d'un texte (version 1).

    Règle : un mot est un jeton séparé par des blancs (`str.split()`, donc espace insécable
    comprise) qui contient au moins un caractère alphanumérique. « l'usager » et
    « porte-monnaie » comptent pour un mot ; « € » ou « – » seuls ne comptent pas.
    """
    return len(_mots(texte))


def decouper_phrases(texte: str) -> list[str]:
    """Découpe un texte en phrases (version 1).

    Règle : coupure après `.`, `!`, `?` ou `…` (répétés ou non) suivis d'un blanc ou de la
    fin du texte, et à chaque saut de ligne (`str.splitlines`). Chaque phrase est rendue sans
    ses blancs de bord. Une phrase sans mot (au sens de `compter_mots`) est ignorée. Les
    abréviations (« M. ») coupent : limite assumée.
    """
    phrases: list[str] = []
    for ligne in texte.splitlines():
        for morceau in _FIN_DE_PHRASE.split(ligne):
            morceau = morceau.strip()
            if _mots(morceau):
                phrases.append(morceau)
    return phrases


def extraire_nombres(texte: str) -> list[Decimal]:
    """Extrait les nombres écrits à la française, dans l'ordre du texte (version 1).

    Règles :
    - chiffres ASCII seulement ; virgule décimale ;
    - séparateur de milliers = espace, U+00A0, U+202F ou U+2009 entre groupes de 3 chiffres
      (« 1 234,56 » donne 1234.56) ;
    - point = séparateur de milliers seulement devant une virgule décimale (« 1.234,56 »),
      sinon point décimal (« 3.5 ») ; un point final sans chiffre n'est pas pris (« 25. »
      donne 25) ;
    - signe `-` ou `−` (U+2212) seulement s'il n'est pas collé à un caractère de mot avant
      (« 2020-2021 » donne 2020 et 2021, « -3,5 % » donne -3.5) ;
    - un nombre collé à une lettre ou à un chiffre avant (« R2D2 ») est ignoré, partie
      décimale comprise (« v2.5 » et « A1,5 » ne donnent rien) ;
    - un chiffre qui suit « <chiffre>. » ou « <chiffre>, » n'ouvre pas de nouveau nombre :
      « 1.234.567 » (sans virgule décimale) ne donne que 1.234 (limite assumée) ;
    - les symboles autour (€, %) sont ignorés. La valeur garde ses décimales (« 12,50 »
      donne `Decimal("12.50")`).
    """
    nombres: list[Decimal] = []
    for m in _NOMBRE.finditer(texte):
        if m["points"] is not None:
            chiffres = m["points"].replace(".", "").replace(",", ".")
        elif m["groupes"] is not None:
            chiffres = m["groupes"].replace(",", ".")
            for separateur in _SEPARATEURS_MILLIERS:
                chiffres = chiffres.replace(separateur, "")
        else:
            chiffres = m["simple"].replace(",", ".")
        signe = "-" if m["signe"] is not None else ""
        nombres.append(Decimal(signe + chiffres))
    return nombres


def syllabes(mot: str) -> int:
    """Compte les syllabes d'un jeton, de façon approximative mais unique (version 1).

    Règle : le jeton (mis en NFC) est découpé en segments de lettres (tout caractère qui
    n'est pas une lettre sépare). Dans chaque segment en minuscules, on compte les groupes
    maximaux de voyelles `aeiouyàâäéèêëîïôöùûüÿæœ`. Règle du e muet final : si le segment se
    termine par `e` ou `es` (e sans accent) précédé d'une consonne et compte plus d'un groupe,
    on retire 1. Total du jeton = somme des segments, minimum 1 (un nombre comme « 2026 »
    vaut 1). Ni règle « qu », ni « -ent » verbal, ni diérèse : AD-29 demande une seule
    syllabation partout, pas une syllabation parfaite.
    """
    total = 0
    for est_lettre, caracteres in groupby(unicodedata.normalize("NFC", mot), str.isalpha):
        if est_lettre:
            total += _syllabes_segment("".join(caracteres).lower())
    return max(total, 1)


def _syllabes_segment(segment: str) -> int:
    groupes = sum(1 for est_voyelle, _ in groupby(segment, lambda c: c in _VOYELLES) if est_voyelle)
    if groupes > 1:
        radical = segment[:-2] if segment.endswith("es") else segment[:-1]
        if segment.endswith(("e", "es")) and radical and radical[-1] not in _VOYELLES:
            groupes -= 1
    return groupes


def kandel_moles(texte: str) -> float:
    """Indice de lisibilité de Kandel-Moles (version 1), valeur brute non arrondie.

    Formule : 207 − 1,015 × (mots ÷ phrases) − 73,6 × (syllabes ÷ mots), sur les totaux du
    texte. Mots selon `compter_mots`, phrases selon `decouper_phrases`, syllabes = somme de
    `syllabes` sur chaque mot. Plus l'indice est haut, plus le texte est lisible.

    Lève `ValueError` si le texte ne contient aucun mot.
    """
    mots = _mots(texte)
    if not mots:
        raise ValueError("kandel_moles : le texte ne contient aucun mot.")
    nb_phrases = len(decouper_phrases(texte))
    nb_syllabes = sum(syllabes(mot) for mot in mots)
    return 207 - 1.015 * (len(mots) / nb_phrases) - 73.6 * (nb_syllabes / len(mots))


def ngrammes(texte: str, n: int) -> list[tuple[str, ...]]:
    """N-grammes de mots consécutifs du texte normalisé (version 1).

    Règle : n-grammes de `normaliser(texte).split()`, dans l'ordre, doublons conservés ;
    liste vide s'il y a moins de `n` jetons. Lève `ValueError` si `n < 1`.
    """
    if n < 1:
        raise ValueError(f"ngrammes : n doit valoir au moins 1 (reçu {n}).")
    jetons = normaliser(texte).split()
    return [tuple(jetons[i : i + n]) for i in range(len(jetons) - n + 1)]
