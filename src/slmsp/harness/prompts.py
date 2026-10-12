"""Construction unique des messages d'une Tâche (AD-7).

`construire_messages` est la seule fonction qui compose un prompt : le service, les
traitements de Tâche, le banc, `data` et `train` l'appellent tous. Elle est pure (aucune
lecture de fichier, aucun état) : la même entrée donne le même JSON canonique.

Sortie : `[system, user]` au format OpenAI. `system` porte la « Consigne » du prompt de la
Tâche (ou de sa variante). Les outils ne sont jamais rendus dans le texte : ils vont au chat
template par `tools` ; `construire_messages` vérifie seulement qu'ils sont autorisés.

Règle unique de rendu du message `user` :

- Entrée texte (prompt qui déclare `question` ou `demande`) :
  - sans emplacement `passages`, l'entrée est rendue telle quelle ;
  - avec `passages`, le message vaut « Passages de l'Index local : », un saut de ligne,
    le bloc de `formater_passages`, une ligne vide, puis « <Libellé> :\\n<entrée> », où le
    libellé est celui de l'emplacement texte (`LIBELLES_CLES`). Sans passage, le bloc est
    la phrase fixe `AUCUN_PASSAGE`.
- Entrée objet (dict à clés nommées) : on garde les clés présentes de `ORDRE_CLES`, dans
  cet ordre fixe. Chaque clé donne une section « <Libellé> :\\n<valeur> » ; les sections
  sont jointes par une ligne vide. Une chaîne est rendue telle quelle, un nombre par
  `str`, un booléen par « oui » ou « non ». Une liste donne une ligne « - élément » par
  élément ; un dict, une ligne « - clé : valeur » par clé triée (underscores remplacés
  par des espaces). Les valeurs imbriquées sont indentées de 2 espaces sous une ligne
  « - clé : » (dict) ou « - » (liste) ; les lignes suivantes d'un texte multiligne
  imbriqué sont indentées de 2 espaces, au niveau du texte de l'élément. La clé
  `nb_mots`, une métadonnée, est ignorée. Toute autre clé, ou une clé absente des
  emplacements du prompt, lève `EntreeInvalide`.
- Synonymes (`SYNONYMES_CLES`) : la clé `type` (items CT du jeu gelé) est admise
  seulement si le prompt la déclare ; elle est rendue exactement comme `type_courrier`
  (même libellé, même place). `type` et `type_courrier` ensemble lèvent `EntreeInvalide`.
- Entrées vides refusées (`EntreeInvalide`) : entrée texte blanche, valeur vide (chaîne
  blanche, liste ou dict vide) à tout niveau, entrée objet sans aucune clé de
  `CLES_CONTENU`.

Passages (`formater_passages`) : numérotés `[1]`, `[2]`… dans l'ordre reçu, chacun sur
quatre lignes au moins : « [i] <titre> », « URL : <url> », « Date : <date du snapshot> »
(« non précisée » si absente), puis le texte du passage ; séparés par une ligne vide.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Final

from slmsp.core.erreurs import SlmspError
from slmsp.core.messages import ConversationInvalide, valider_conversation
from slmsp.core.ports import Passage
from slmsp.harness.taches import EMPLACEMENTS_TEXTE, Tache, VarianteInconnue

if TYPE_CHECKING:
    from slmsp.core.items import RequeteTache

ORDRE_CLES: Final[tuple[str, ...]] = (
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
"""Ordre fixe des sections d'une entrée objet."""

LIBELLES_CLES: Final[Mapping[str, str]] = {
    "question": "Question",
    "demande": "Demande",
    "consigne": "Consigne",
    "type_courrier": "Type de courrier",
    "objet": "Objet",
    "elements_connus": "Éléments connus",
    "longueur_demandee": "Longueur demandée",
    "langue_source": "Langue source",
    "langue_cible": "Langue cible",
    "partie": "Partie",
    "notes": "Notes",
    "transcription": "Transcription",
    "texte": "Texte",
    "document": "Document",
    "parties": "Parties",
}
"""Libellé de section de chaque clé d'entrée."""

SYNONYMES_CLES: Final[Mapping[str, str]] = {"type": "type_courrier"}
"""Clé d'entrée admise → clé canonique de `ORDRE_CLES`, dont elle prend le rendu."""

CLES_IGNOREES: Final[frozenset[str]] = frozenset({"nb_mots"})
"""Métadonnées d'une entrée objet, jamais rendues."""

CLES_CONTENU: Final[tuple[str, ...]] = (
    "objet",
    "elements_connus",
    "notes",
    "transcription",
    "texte",
    "document",
    "parties",
)
"""Une entrée objet porte au moins une de ces clés : sans elle, le prompt est inutilisable."""

CLES_OPTIONS: Final[tuple[str, ...]] = ("longueur_demandee", "type_courrier")
"""Clés que `core.items.vers_requete` place dans `options` et qui reviennent dans l'entrée."""

ENTETE_PASSAGES: Final = "Passages de l'Index local :"
AUCUN_PASSAGE: Final = "Aucun passage pertinent n'a été trouvé dans l'Index local."
DATE_INCONNUE: Final = "non précisée"


class EntreeInvalide(SlmspError):
    """Entrée, passages, outils ou variante incompatibles avec la Tâche."""


def formater_passages(passages: Sequence[Passage] | None) -> str:
    """Bloc des passages numérotés `[1]`, `[2]`… ; `AUCUN_PASSAGE` si la liste est vide."""
    if not passages:
        return AUCUN_PASSAGE
    blocs = []
    for numero, passage in enumerate(passages, start=1):
        date = passage.date_snapshot or DATE_INCONNUE
        blocs.append(
            f"[{numero}] {passage.titre}\nURL : {passage.url}\nDate : {date}\n{passage.texte}"
        )
    return "\n\n".join(blocs)


def _indenter(ligne: str) -> str:
    return "  " + ligne if ligne else ligne


def _element(prefixe: str, texte: str) -> list[str]:
    """Ligne « prefixe + texte » ; les lignes suivantes d'un texte multiligne sont indentées."""
    premiere, *suite = texte.split("\n")
    return [prefixe + premiere, *(_indenter(ligne) for ligne in suite)]


def _lignes_valeur(valeur: Any, chemin: str) -> list[str]:
    """Lignes d'une valeur imbriquée (élément de liste ou valeur de dict)."""
    if isinstance(valeur, (list, dict)) and not valeur:
        raise EntreeInvalide(f"« {chemin} » : valeur vide")
    if isinstance(valeur, list):
        lignes: list[str] = []
        for element in valeur:
            if isinstance(element, (list, dict)):
                lignes.append("-")
                lignes.extend(_indenter(ligne) for ligne in _lignes_valeur(element, chemin))
            else:
                lignes.extend(_element("- ", _scalaire(element, chemin)))
        return lignes
    if isinstance(valeur, dict):
        lignes = []
        for cle in sorted(valeur):
            if not isinstance(cle, str):
                raise EntreeInvalide(f"« {chemin} » : clé non textuelle")
            nom = cle.replace("_", " ")
            sous_valeur = valeur[cle]
            if isinstance(sous_valeur, (list, dict)):
                lignes.append(f"- {nom} :")
                lignes.extend(_indenter(ligne) for ligne in _lignes_valeur(sous_valeur, chemin))
            else:
                lignes.extend(_element(f"- {nom} : ", _scalaire(sous_valeur, chemin)))
        return lignes
    return [_scalaire(valeur, chemin)]


def _scalaire(valeur: Any, chemin: str) -> str:
    if isinstance(valeur, str):
        if not valeur.strip():
            raise EntreeInvalide(f"« {chemin} » : valeur vide")
        return valeur
    if isinstance(valeur, bool):
        return "oui" if valeur else "non"
    if isinstance(valeur, (int, float)):
        return str(valeur)
    raise EntreeInvalide(
        f"« {chemin} » : valeur de type {type(valeur).__name__} non prise en charge"
    )


def _canoniser(
    entree: Mapping[str, Any], emplacements: tuple[str, ...], code: str
) -> Mapping[str, Any]:
    """`entree` où chaque synonyme déclaré par le prompt prend le nom de sa clé canonique."""
    presents = [cle for cle in SYNONYMES_CLES if cle in entree]
    if not presents:
        return entree
    canonique = dict(entree)
    for cle in presents:
        cible = SYNONYMES_CLES[cle]
        if cle not in emplacements:
            raise EntreeInvalide(
                f"Tâche {code} : clé d'entrée « {cle} » non déclarée par le prompt"
            )
        if cible in entree:
            raise EntreeInvalide(
                f"Tâche {code} : clés d'entrée « {cle} » et « {cible} » en conflit"
            )
        canonique[cible] = canonique.pop(cle)
    return canonique


def _rendre_objet(entree: Mapping[str, Any], emplacements: tuple[str, ...], code: str) -> str:
    entree = _canoniser(entree, emplacements, code)
    for cle in entree:
        if cle in CLES_IGNOREES:
            continue
        if cle not in ORDRE_CLES:
            raise EntreeInvalide(f"Tâche {code} : clé d'entrée « {cle} » inconnue")
        if cle not in emplacements:
            raise EntreeInvalide(
                f"Tâche {code} : clé d'entrée « {cle} » non déclarée par le prompt"
            )
    if not any(cle in entree for cle in CLES_CONTENU):
        raise EntreeInvalide(
            f"Tâche {code} : entrée objet sans aucune clé de contenu ({', '.join(CLES_CONTENU)})"
        )
    sections = []
    for cle in ORDRE_CLES:
        if cle in entree:
            valeur = entree[cle]
            corps = "\n".join(_lignes_valeur(valeur, cle))
            sections.append(f"{LIBELLES_CLES[cle]} :\n{corps}")
    return "\n\n".join(sections)


def _noms_outils(outils: Sequence[Any] | None) -> list[str]:
    noms = []
    for outil in outils or ():
        if isinstance(outil, str):
            noms.append(outil)
            continue
        fonction = outil.get("function") if isinstance(outil, Mapping) else None
        nom = fonction.get("name") if isinstance(fonction, Mapping) else None
        if not isinstance(nom, str):
            raise EntreeInvalide("outil mal formé : nom ou dict « tools » OpenAI attendu")
        noms.append(nom)
    return noms


def construire_messages(
    tache: Tache,
    entree: str | Mapping[str, Any],
    passages: Sequence[Passage] | None = None,
    outils: Sequence[Mapping[str, Any] | str] | None = None,
    *,
    variante: str | None = None,
) -> list[dict[str, Any]]:
    """Messages `[system, user]` de la Tâche, selon la règle unique du module.

    `outils` (dicts `tools` d'OpenAI ou noms) ne sont pas rendus : ils doivent seulement
    figurer dans `tache.outils_autorises` (FR-38). Lève `EntreeInvalide` pour une entrée du
    mauvais type, une clé inconnue ou non déclarée, des passages sur une Tâche qui ne les
    prévoit pas, un outil non autorisé ou une variante inconnue.
    """
    try:
        prompt = tache.prompt_pour(variante)
    except VarianteInconnue as exc:
        raise EntreeInvalide(str(exc)) from None
    code = tache.code
    interdits = [nom for nom in _noms_outils(outils) if nom not in tache.outils_autorises]
    if interdits:
        raise EntreeInvalide(f"Tâche {code} : outil(s) non autorisé(s) : {', '.join(interdits)}")
    if passages and "passages" not in prompt.emplacements:
        raise EntreeInvalide(f"Tâche {code} : le prompt « {prompt.id} » ne prévoit pas de passages")

    if prompt.entree_texte:
        if not isinstance(entree, str):
            raise EntreeInvalide(f"Tâche {code} : entrée texte attendue")
        if not entree.strip():
            raise EntreeInvalide(f"Tâche {code} : entrée texte vide")
        if "passages" in prompt.emplacements:
            (nom_texte,) = (nom for nom in prompt.emplacements if nom in EMPLACEMENTS_TEXTE)
            contenu = (
                f"{ENTETE_PASSAGES}\n{formater_passages(passages)}\n\n"
                f"{LIBELLES_CLES[nom_texte]} :\n{entree}"
            )
        else:
            contenu = entree
    else:
        if not isinstance(entree, Mapping):
            raise EntreeInvalide(f"Tâche {code} : entrée objet (clés nommées) attendue")
        contenu = _rendre_objet(entree, prompt.emplacements, code)

    messages = [
        {"role": "system", "content": prompt.consigne},
        {"role": "user", "content": contenu},
    ]
    try:
        valider_conversation(messages)
    except ConversationInvalide as exc:  # pragma: no cover - garde-fou de forme
        raise EntreeInvalide(str(exc)) from None
    return messages


def entree_de_requete(requete: RequeteTache) -> str | dict[str, Any]:
    """Entrée prête pour `construire_messages`, depuis une `RequeteTache` de `core.items`.

    Une entrée objet reçoit `longueur_demandee` (RE) et `type_courrier` (CT) depuis les
    options, sauf si elle les porte déjà, directement ou par un synonyme (`type`). L'entrée
    est copiée : la requête n'est jamais modifiée.
    """
    entree = copy.deepcopy(requete.entree)
    if isinstance(entree, dict):
        for cle in CLES_OPTIONS:
            synonymes = [nom for nom, cible in SYNONYMES_CLES.items() if cible == cle]
            if any(nom in entree for nom in synonymes):
                continue
            if cle in requete.options and cle not in entree:
                entree[cle] = copy.deepcopy(requete.options[cle])
    return entree
