"""Contrôles automatiques de la notation (story 5.6), fonctions pures par Tâche.

Chaque `controle_<tache>(item, generation, …)` rend un `dict` JSON, écrit tel quel dans
`controles.jsonl` et lu par `slmsp.evaluation.scores`. Aucun appel réseau, aucune écriture.

- **Q** : URL inventées du texte (`harness.citations.urls_inventees`). Sont connues les
  sources de la sortie, les résultats `resultat-outil` de la trace et les textes de l'entrée
  (`textes_entree`) ; les passages complets ne sont pas dans la génération.
- **RD** : appel valide par appariement glouton des appels attendus aux appels émis (même
  outil, `regles` satisfaites, ordre de la liste sauf `ordre_libre` ; `contient_un_de` en
  début de mot et `mot_entier_un_de` en mot entier, combinés en « ou ») ; un appel attendu
  `optionnel` est hors comptes ; sans `regles` (calibrage), l'outil seul compte. Réponse
  exacte : avec `valeurs_attendues.lignes`, toutes leurs valeurs numériques (des seules
  `valeurs_attendues.colonnes` si la liste est donnée) figurent parmi
  `extraire_nombres(texte)` ; sinon l'identifiant **ou** l'URL normalisée du jeu principal
  (ou d'un jeu de `autres_jeux_cites_possibles`) figure dans le texte. Litige : le titre
  normalisé d'un de ces jeux est dans le texte sans identifiant ni URL (le Juge tranche).
- **CO** : alignement par mots (`difflib.SequenceMatcher`, `autojunk=False`) après les
  équivalences typographiques de la config. Une faute est corrigée si le segment de sortie
  aligné sur ses mots égale le texte source de ces mots, fautes remplacées par leur
  correction. Taux hors faute = (mots source hors faute modifiés ou supprimés + mots insérés
  non adjacents à une faute) ÷ mots du texte, plafonné à 1.
- **CT** : chaque libellé de `champs_a_laisser_en_emplacement` figure tel quel (crochets
  compris). Les `valeurs_interdites`, descriptives, restent au Juge.
- **RE** : mots de la sortie, plafond de la longueur demandée, respect.
- **LC** : Kandel-Moles de l'entrée (`kandel_moles_entree`, sinon calculé), de la sortie et
  gain (sortie − entrée).
- **CR**, **NR** : aucun contrôle automatique (dict vide).
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal
from difflib import SequenceMatcher
from typing import Any, Final

from slmsp.core.items import (
    AppelAttendu,
    ItemBase,
    ItemCO,
    ItemCT,
    ItemLC,
    ItemQ,
    ItemRD,
    ItemRE,
    RegleArgument,
    textes_entree,
)
from slmsp.core.schemas.generation import Generation
from slmsp.core.texte import compter_mots, extraire_nombres, kandel_moles, normaliser
from slmsp.harness.citations import extraire_urls, normaliser_url, urls_inventees

DECIMALES: Final = 4
"""Arrondi des valeurs décimales des contrôles (taux, indices)."""

_MOT: Final = re.compile(r"\S+")


def _arrondi(valeur: float | None) -> float | None:
    return None if valeur is None else round(valeur, DECIMALES)


def _texte(generation: Generation) -> str:
    return generation.sortie_canonique.texte


def _resultats_outils(generation: Generation) -> list[Any]:
    return [
        evenement.get("resultat")
        for evenement in generation.trace
        if evenement.get("type") == "resultat-outil"
    ]


# --- Q --------------------------------------------------------------------------------------


def controle_q(item: ItemQ, generation: Generation) -> dict[str, Any]:
    """URL du texte absentes des sources, des résultats d'outils et de l'entrée."""
    sources = [s.model_dump(mode="json") for s in generation.sortie_canonique.sources]
    inventees = urls_inventees(
        _texte(generation),
        resultats_outils=[*sources, *_resultats_outils(generation)],
        textes_fournis=textes_entree(item),
    )
    return {"urls_inventees": inventees}


# --- RD -------------------------------------------------------------------------------------


def _debut_de_mot(fragment: str, valeur: str) -> bool:
    """`fragment` normalisé apparaît en début de mot dans `valeur` normalisée (spec 7.3)."""
    motif = r"(?:^| )" + re.escape(normaliser(fragment))
    return re.search(motif, normaliser(valeur)) is not None


def _mot_entier(mot: str, valeur: str) -> bool:
    """`mot` normalisé apparaît comme mot entier (ou suite de mots entiers) dans `valeur`
    normalisée : bordé d'une espace ou du bord du texte (« rei » dans « fichier rei 2024 »,
    pas dans « reims »)."""
    forme = normaliser(mot)
    if not forme:
        return False
    motif = r"(?:^| )" + re.escape(forme) + r"(?: |$)"
    return re.search(motif, normaliser(valeur)) is not None


def _argument_conforme(regle: RegleArgument, present: bool, valeur: Any) -> bool:
    if not present:
        return regle.optionnel
    if regle.a_exact:
        return valeur == regle.exact and type(valeur) is type(regle.exact)
    if regle.contient_un_de is not None or regle.mot_entier_un_de is not None:
        return isinstance(valeur, str) and (
            any(_debut_de_mot(fragment, valeur) for fragment in regle.contient_un_de or ())
            or any(_mot_entier(mot, valeur) for mot in regle.mot_entier_un_de or ())
        )
    return regle.optionnel


def appel_conforme(attendu: AppelAttendu, nom: str, arguments: Mapping[str, Any]) -> bool:
    """L'appel émis `nom(arguments)` satisfait-il l'appel attendu ?

    Même outil, puis chaque règle d'argument (`exact` : égalité et même type ;
    `contient_un_de` : un fragment en début de mot, ou `mot_entier_un_de` : un mot entier,
    les deux en « ou » ; absent : admis si `optionnel`). Sans `regles` (calibrage), l'outil
    seul compte.
    """
    if nom != attendu.outil:
        return False
    if attendu.regles is None:
        return True
    return all(
        _argument_conforme(regle, cle in arguments, arguments.get(cle))
        for cle, regle in attendu.regles.arguments.items()
    )


def apparier_appels(
    attendus: Sequence[AppelAttendu], emis: Sequence[tuple[str, Mapping[str, Any]]]
) -> list[int | None]:
    """Appariement glouton : pour chaque appel attendu, l'indice de l'appel émis retenu.

    Les appels attendus sont parcourus dans l'ordre ; chacun prend le premier appel émis
    conforme et non encore pris, situé après le dernier appel apparié (sauf `ordre_libre`,
    qui cherche depuis le début). Un appel attendu `optionnel` n'est pas apparié (`None`).
    """
    pris: set[int] = set()
    curseur = 0
    resultat: list[int | None] = []
    for attendu in attendus:
        regles = attendu.regles
        if regles is not None and regles.optionnel:
            resultat.append(None)
            continue
        debut = 0 if regles is not None and regles.ordre_libre else curseur
        trouve = next(
            (
                i
                for i in range(debut, len(emis))
                if i not in pris and appel_conforme(attendu, *emis[i])
            ),
            None,
        )
        resultat.append(trouve)
        if trouve is not None:
            pris.add(trouve)
            if regles is None or not regles.ordre_libre:
                curseur = trouve + 1
    return resultat


def _jeux_references(item: ItemRD) -> list[Mapping[str, Any]]:
    reference = item.reponse_reference
    if not isinstance(reference, Mapping):
        return []
    jeux: list[Mapping[str, Any]] = []
    principal = reference.get("jeu_principal")
    if isinstance(principal, Mapping):
        jeux.append(principal)
    for autre in reference.get("autres_jeux_cites_possibles") or []:
        if isinstance(autre, Mapping):
            jeux.append(autre)
    return jeux


def _valeurs_numeriques(valeurs_attendues: Any) -> list[Decimal] | None:
    """Valeurs numériques des `lignes` attendues (seulement des `colonnes` si elles sont
    listées) ; `None` sans lignes."""
    if not isinstance(valeurs_attendues, Mapping):
        return None
    lignes = valeurs_attendues.get("lignes")
    if not isinstance(lignes, list):
        return None
    colonnes = valeurs_attendues.get("colonnes")
    nombres: list[Decimal] = []
    for ligne in lignes:
        if not isinstance(ligne, Mapping):
            cellules: Iterable[Any] = [ligne]
        elif isinstance(colonnes, list):
            cellules = [ligne.get(colonne) for colonne in colonnes]
        else:
            cellules = ligne.values()
        for cellule in cellules:
            if isinstance(cellule, bool) or cellule is None:
                continue
            nombres.extend(extraire_nombres(str(cellule)))
    return nombres


def _contient_titre(titre: str, texte_normalise: str) -> bool:
    forme = normaliser(titre)
    if not forme:
        return False
    return re.search(r"(?:^| )" + re.escape(forme) + r"(?: |$)", texte_normalise) is not None


def controle_rd(item: ItemRD, generation: Generation) -> dict[str, Any]:
    """Appel valide (appariement) et réponse exacte (valeurs, identifiant ou URL du jeu)."""
    sortie = generation.sortie_canonique
    texte = sortie.texte
    attendus = list(item.appels_attendus or [])
    emis = [(appel.nom, appel.arguments) for appel in sortie.appels_outils]
    appariement = apparier_appels(attendus, emis)
    comptes = [
        (attendu, indice)
        for attendu, indice in zip(attendus, appariement, strict=True)
        if not (attendu.regles is not None and attendu.regles.optionnel)
    ]
    controle: dict[str, Any] = {
        "appels_attendus": len(comptes),
        "appels_valides": sum(1 for _, indice in comptes if indice is not None),
        "appariement": appariement,
        "reponse_exacte": None,
        "litige": False,
        "methode": None,
    }
    valeurs = _valeurs_numeriques(item.valeurs_attendues)
    if valeurs:
        presents = set(extraire_nombres(texte))
        manquantes = [v for v in valeurs if v not in presents]
        controle.update(
            reponse_exacte=not manquantes,
            methode="valeurs",
            valeurs_manquantes=[str(v) for v in manquantes],
        )
        return controle
    jeux = _jeux_references(item)
    if not jeux:
        controle["methode"] = "sans-reference"
        return controle
    urls = {normaliser_url(url) for url in extraire_urls(texte)}
    for jeu in jeux:
        identifiant = jeu.get("id")
        url = jeu.get("url")
        if (
            isinstance(identifiant, str)
            and identifiant
            and re.search(rf"(?<![\w-]){re.escape(identifiant)}(?![\w-])", texte)
        ) or (isinstance(url, str) and url and normaliser_url(url) in urls):
            controle.update(reponse_exacte=True, methode="identifiant")
            return controle
    normalise = normaliser(texte)
    litige = any(
        isinstance(jeu.get("titre"), str) and _contient_titre(jeu["titre"], normalise)
        for jeu in jeux
    )
    controle.update(reponse_exacte=None if litige else False, litige=litige, methode="identifiant")
    return controle


# --- CO -------------------------------------------------------------------------------------


def appliquer_equivalences(texte: str, equivalences: Mapping[str, str]) -> str:
    """Remplace chaque motif de `equivalences` par sa forme commune (motifs longs d'abord)."""
    for motif in sorted(equivalences, key=lambda m: (-len(m), m)):
        texte = texte.replace(motif, equivalences[motif])
    return texte


_PONCTUATION: Final = frozenset(':;!?."«»…')
"""Caractères d'un jeton de ponctuation isolé, recollé à un mot voisin (espacement toléré)."""


def _mots_avec_positions(
    texte: str, equivalences: Mapping[str, str] | None = None
) -> list[tuple[int, int]]:
    """Mots séparés par des blancs ; un jeton fait seulement de ponctuation est recollé au
    mot précédent, sauf un guillemet ouvrant (`«`, ou `"` de rang pair après les
    équivalences), recollé au mot suivant : l'espacement typographique de la ponctuation
    (« mot : » / « mot: », « « oui » » / « «oui» ») ne compte pas comme une modification."""
    spans: list[tuple[int, int]] = []
    ouvrant: int | None = None
    guillemets = 0
    for m in _MOT.finditer(texte):
        jeton = appliquer_equivalences(m.group(0), equivalences or {})
        ponctuation = set(jeton) <= _PONCTUATION
        est_ouvrant = ponctuation and (
            jeton.startswith("«") or (jeton.startswith('"') and guillemets % 2 == 0)
        )
        guillemets += jeton.count('"')
        debut = m.start() if ouvrant is None else ouvrant
        if est_ouvrant:
            ouvrant = debut
            continue
        ouvrant = None
        if ponctuation and spans and debut == m.start():
            spans[-1] = (spans[-1][0], m.end())
        else:
            spans.append((debut, m.end()))
    if ouvrant is not None:
        spans.append((ouvrant, len(texte.rstrip())))
    return spans


def _mots(texte: str, equivalences: Mapping[str, str]) -> list[str]:
    """Mots comparés : après les équivalences typographiques, sans blanc interne."""
    return [
        re.sub(r"\s+", "", appliquer_equivalences(texte[a:b], equivalences))
        for a, b in _mots_avec_positions(texte, equivalences)
    ]


def _correspondances(
    opcodes: Iterable[tuple[str, int, int, int, int]],
) -> list[tuple[str, int, int, int, int]]:
    """Découpe les remplacements de même longueur en paires mot à mot."""
    blocs: list[tuple[str, int, int, int, int]] = []
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "replace" and i2 - i1 == j2 - j1:
            blocs.extend(
                ("replace", i1 + k, i1 + k + 1, j1 + k, j1 + k + 1) for k in range(i2 - i1)
            )
        else:
            blocs.append((tag, i1, i2, j1, j2))
    return blocs


def controle_co(
    item: ItemCO, generation: Generation, equivalences: Mapping[str, str]
) -> dict[str, Any]:
    """Fautes corrigées, rappel, modifications hors faute et taux hors faute."""
    entree = item.entree if isinstance(item.entree, Mapping) else {}
    source = entree.get("texte")
    fautes = list(item.fautes or [])
    if not isinstance(source, str):
        return {"fautes": len(fautes), "corrigees": 0, "rappel": None, "taux_hors_faute": None}
    spans = _mots_avec_positions(source, equivalences)
    mots_source = _mots(source, equivalences)
    mots_sortie = _mots(_texte(generation), equivalences)
    # Mots source de chaque faute (chevauchement de [debut, fin)).
    mots_faute: list[set[int]] = [
        {i for i, (a, b) in enumerate(spans) if a < faute.fin and faute.debut < b}
        for faute in fautes
    ]
    dans_faute = set().union(*mots_faute) if mots_faute else set()
    opcodes = SequenceMatcher(None, mots_source, mots_sortie, autojunk=False).get_opcodes()
    blocs = _correspondances(opcodes)

    corrigees: list[bool] = []
    for indices in mots_faute:
        if not indices:
            corrigees.append(False)
            continue
        touches = [b for b in blocs if b[0] != "insert" and any(b[1] <= i < b[2] for i in indices)]
        i1 = min(b[1] for b in touches)
        i2 = max(b[2] for b in touches)
        j1 = min(b[3] for b in touches)
        j2 = max(b[4] for b in touches)
        debut, fin = spans[i1][0], spans[i2 - 1][1]
        attendu = source[debut:fin]
        for faute in sorted(fautes, key=lambda f: f.debut, reverse=True):
            if debut <= faute.debut and faute.fin <= fin:
                decale_debut, decale_fin = faute.debut - debut, faute.fin - debut
                attendu = attendu[:decale_debut] + faute.correction + attendu[decale_fin:]
        attendu_mots = _mots(attendu, equivalences)
        corrigees.append(mots_sortie[j1:j2] == attendu_mots)

    modifies = 0
    inseres = 0
    for tag, i1, i2, j1, j2 in blocs:
        hors = [i for i in range(i1, i2) if i not in dans_faute]
        if tag == "equal":
            continue
        if tag == "insert":
            voisins = {i1 - 1, i1}
            if not voisins & dans_faute:
                inseres += j2 - j1
            continue
        if tag == "delete":
            modifies += len(hors)
            continue
        # replace (paire mot à mot ou bloc de longueurs différentes) : les mots source hors
        # faute sont modifiés ; les mots ajoutés ne comptent que si le bloc ne touche aucune
        # faute (sinon ils lui sont adjacents).
        modifies += len(hors)
        if j2 - j1 > i2 - i1 and len(hors) == i2 - i1:
            inseres += (j2 - j1) - (i2 - i1)
    nb_mots = len(mots_source)
    taux = min(1.0, (modifies + inseres) / nb_mots) if nb_mots else None
    rappel = sum(corrigees) / len(fautes) if fautes else None
    return {
        "fautes": len(fautes),
        "corrigees": sum(corrigees),
        "fautes_corrigees": corrigees,
        "rappel": _arrondi(rappel),
        "mots_texte": nb_mots,
        "mots_modifies_hors_faute": modifies,
        "mots_inseres_hors_faute": inseres,
        "taux_hors_faute": _arrondi(taux),
    }


# --- CT, RE, LC -----------------------------------------------------------------------------


def controle_ct(item: ItemCT, generation: Generation) -> dict[str, Any]:
    """Présence de chaque libellé d'emplacement, tel quel (crochets compris)."""
    texte = _texte(generation)
    libelles = item.champs_a_laisser_en_emplacement
    if libelles is None:
        return {"emplacements": {}, "emplacements_reussis": None}
    presents = {libelle: libelle in texte for libelle in libelles}
    return {"emplacements": presents, "emplacements_reussis": all(presents.values())}


def _cle_longueur(longueur: str | None) -> str | None:
    if not longueur:
        return None
    premier = normaliser(longueur).split()
    if not premier:
        return None
    decompose = unicodedata.normalize("NFD", premier[0])
    return "".join(c for c in decompose if not unicodedata.combining(c))


def controle_re(
    item: ItemRE, generation: Generation, longueurs: Mapping[str, int]
) -> dict[str, Any]:
    """Mots de la sortie, plafond de la longueur demandée et respect (rapporté)."""
    mots = compter_mots(_texte(generation))
    cle = _cle_longueur(item.longueur_demandee)
    plafond = longueurs.get(cle) if cle is not None else None
    return {
        "mots": mots,
        "longueur_demandee": item.longueur_demandee,
        "plafond_mots": plafond,
        "respect_longueur": None if plafond is None else mots <= plafond,
    }


def _kandel_moles(texte: Any) -> float | None:
    if not isinstance(texte, str):
        return None
    try:
        return kandel_moles(texte)
    except ValueError:
        return None


def controle_lc(item: ItemLC, generation: Generation) -> dict[str, Any]:
    """Kandel-Moles de l'entrée et de la sortie, et gain (sortie − entrée)."""
    entree = item.kandel_moles_entree
    if entree is None:
        texte_entree = item.entree.get("texte") if isinstance(item.entree, Mapping) else None
        entree = _kandel_moles(texte_entree)
    sortie = _kandel_moles(_texte(generation))
    gain = None if entree is None or sortie is None else sortie - entree
    return {
        "km_entree": _arrondi(entree),
        "km_sortie": _arrondi(sortie),
        "gain_km": _arrondi(gain),
    }


# --- Toutes Tâches --------------------------------------------------------------------------


def controler(
    item: ItemBase,
    generation: Generation,
    *,
    equivalences: Mapping[str, str],
    longueurs: Mapping[str, int],
) -> dict[str, Any]:
    """Contrôle automatique de `item` selon sa Tâche (dict vide pour CR et NR)."""
    if isinstance(item, ItemQ):
        return controle_q(item, generation)
    if isinstance(item, ItemRD):
        return controle_rd(item, generation)
    if isinstance(item, ItemCO):
        return controle_co(item, generation, equivalences)
    if isinstance(item, ItemCT):
        return controle_ct(item, generation)
    if isinstance(item, ItemRE):
        return controle_re(item, generation, longueurs)
    if isinstance(item, ItemLC):
        return controle_lc(item, generation)
    return {}


__all__ = [
    "apparier_appels",
    "appel_conforme",
    "appliquer_equivalences",
    "controle_co",
    "controle_ct",
    "controle_lc",
    "controle_q",
    "controle_rd",
    "controle_re",
    "controler",
]
