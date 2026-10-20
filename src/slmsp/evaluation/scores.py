"""Scores de Tâche et kappa entre juges : seule implémentation des formules de la grille.

Le Juge note des critères ; il ne calcule jamais de score. `calculer_scores` applique les
formules de `eval/grille-juge-v1.md` aux items `ok` dont le verdict est valide (Tâches
jugées) ou dont le contrôle automatique est calculable (RD, CO). Les autres items sont
exclus et comptés (`invalides`, `non_juges`, `en_erreur`).

- **Q** : réussi ⇔ exactitude 2 ∧ pertinence 1 ∧ aucune URL inventée ; pour un item sans
  réponse, ⇔ `cas_sans_reponse` = 1. Score = % réussis.
- **RD** : moyenne de « appel valide » (micro-moyenne des appels attendus appariés, items
  sans appel attendu hors dénominateur) et de « réponse exacte » (% ; un litige est tranché
  par `libelle_correct` du Juge, et exclu sans verdict valide).
- **CR** : moyenne de (rappel moyen × 100) et (% `absence_invention` = 1) ; rappel = moyenne
  des `present` (0,5 = action incomplète). `structure` est rapportée.
- **LC** : % (fidélité 2 ∧ termes 1) ; si le gain moyen de Kandel-Moles est sous
  `gain_km_min`, score = min(score, `plafond_lc`) et `plafonne_lc`.
- **CO** : moyenne de rappel × (1 − taux hors faute), × 100.
- **RE** : moyenne de (% fidèles) et (rappel moyen × 100) ; la longueur est rapportée.
- **CT** : moyenne de (conformité moyenne ÷ 2 × 100) et (% d'emplacements réussis).
- **NR** : % exactitude 1.

Une composante sans effectif vaut `None` ; le score est la moyenne des composantes
disponibles, `None` si aucune. Kappa de Cohen entre Juge principal et second juge :
quadratique pour les critères ordinaux, simple pour les binaires, aucun sur les rappels
(`presence_elements`) ; kappa de Tâche = minimum des kappas calculables ; `fragile` sous
`kappa_fragile`. RD et CO n'ont pas de kappa.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Final

from slmsp.core.items import CODES, ItemBase, ItemQ
from slmsp.core.schemas.generation import Generation
from slmsp.core.schemas.scores import Effectifs, KappaTache, Scores, ScoreTache, StatutsTache
from slmsp.core.schemas.verdict import ElementPresent, NoteCritere, Verdict
from slmsp.core.texte import VERSION_TEXTE
from slmsp.evaluation.config import Seuils

DECIMALES_SCORE: Final = 4
DECIMALES_COUT: Final = 6
SEUIL_ACCORD_ATTENDU: Final = 1e-12
"""Désaccord attendu sous lequel le kappa n'est pas calculable (accord attendu = 1)."""

CRITERES_KAPPA: Final[Mapping[str, Mapping[str, tuple[tuple[int, ...], bool]]]] = {
    "Q": {
        "exactitude": ((0, 1, 2), True),
        "pertinence_source": ((0, 1), False),
        "cas_sans_reponse": ((0, 1), False),
    },
    "CR": {"absence_invention": ((0, 1), False), "structure": ((0, 1), False)},
    "LC": {
        "fidelite": ((0, 1, 2), True),
        "termes_juridiques": ((0, 1), False),
        "clarte_percue": ((1, 2, 3, 4, 5), True),
    },
    "RE": {"fidelite": ((0, 1), False)},
    "CT": {"conformite": ((0, 1, 2), True)},
    "NR": {"exactitude": ((0, 1), False)},
}
"""Tâche → critère → (catégories, pondéré). `presence_elements` n'a pas de kappa."""


@dataclass(frozen=True)
class Jugement:
    """Issue d'un juge pour un item : `juge`, `invalide` ou `non-juge`, et son verdict."""

    statut: str
    verdict: Verdict | None = None
    cle: str | None = None
    motif: str | None = None

    @property
    def valide(self) -> bool:
        return self.statut == "juge" and self.verdict is not None and not self.verdict.invalide


# --- Outils ----------------------------------------------------------------------------------


def _arrondi(valeur: float | None, decimales: int = DECIMALES_SCORE) -> float | None:
    return None if valeur is None else round(valeur, decimales)


def _moyenne(valeurs: Iterable[float | None]) -> float | None:
    retenues = [v for v in valeurs if v is not None]
    return sum(retenues) / len(retenues) if retenues else None


def _pourcentage(succes: Iterable[bool | None]) -> float | None:
    retenus = [s for s in succes if s is not None]
    return 100 * sum(retenus) / len(retenus) if retenus else None


def note(verdict: Verdict, critere: str) -> float | None:
    """Note d'un critère simple du verdict (`None` s'il est absent)."""
    valeur = verdict.criteres.get(critere)
    return valeur.note if isinstance(valeur, NoteCritere) else None


def rappel_elements(verdict: Verdict) -> float | None:
    """Moyenne des `present` de `presence_elements` (`None` sans élément)."""
    elements = verdict.criteres.get("presence_elements")
    if not isinstance(elements, list) or not elements:
        return None
    return sum(e.present for e in elements if isinstance(e, ElementPresent)) / len(elements)


# --- Kappa -----------------------------------------------------------------------------------


def kappa_cohen(
    paires: Sequence[tuple[Any, Any]], categories: Sequence[Any], pondere: bool = False
) -> float | None:
    """Kappa de Cohen de `paires` (note juge 1, note juge 2) sur `categories` ordonnées.

    Pondéré : poids quadratiques `((i − j) / (k − 1))²` ; sinon poids 0 sur la diagonale, 1
    ailleurs. `None` si moins de 2 paires ou si l'accord attendu vaut 1. Lève `ValueError`
    pour une note hors des catégories.
    """
    if len(paires) < 2:
        return None
    rang = {categorie: i for i, categorie in enumerate(categories)}
    k = len(categories)
    n = len(paires)
    observe = [[0.0] * k for _ in range(k)]
    for a, b in paires:
        if a not in rang or b not in rang:
            raise ValueError(f"note hors des catégories {list(categories)} : ({a}, {b})")
        observe[rang[a]][rang[b]] += 1 / n
    lignes = [sum(observe[i]) for i in range(k)]
    colonnes = [sum(observe[i][j] for i in range(k)) for j in range(k)]

    def poids(i: int, j: int) -> float:
        if pondere:
            return ((i - j) / (k - 1)) ** 2 if k > 1 else 0.0
        return 0.0 if i == j else 1.0

    desaccord_observe = sum(poids(i, j) * observe[i][j] for i in range(k) for j in range(k))
    desaccord_attendu = sum(
        poids(i, j) * lignes[i] * colonnes[j] for i in range(k) for j in range(k)
    )
    if desaccord_attendu <= SEUIL_ACCORD_ATTENDU:
        return None
    return 1 - desaccord_observe / desaccord_attendu


def kappa_tache(
    tache: str,
    items: Sequence[ItemBase],
    principal: Mapping[str, Jugement],
    second: Mapping[str, Jugement],
) -> KappaTache:
    """Kappa par critère et kappa de Tâche (minimum) sur les items jugés valides deux fois."""
    criteres = CRITERES_KAPPA.get(tache)
    if not criteres:
        return KappaTache()
    doubles = [
        (principal[item.id].verdict, second[item.id].verdict)
        for item in items
        if item.id in principal
        and item.id in second
        and principal[item.id].valide
        and second[item.id].valide
    ]
    par_critere: dict[str, float | None] = {}
    for critere, (categories, pondere) in criteres.items():
        paires = []
        for v1, v2 in doubles:
            assert v1 is not None and v2 is not None
            a, b = note(v1, critere), note(v2, critere)
            if a is not None and b is not None:
                paires.append((a, b))
        if critere == "cas_sans_reponse" and not paires:
            continue  # aucun item sans réponse dans l'échantillon
        par_critere[critere] = _arrondi(kappa_cohen(paires, categories, pondere))
    calculables = [v for v in par_critere.values() if v is not None]
    return KappaTache(
        valeur=min(calculables) if calculables else None,
        par_critere=par_critere,
        effectif=len(doubles),
    )


# --- Formules par Tâche ------------------------------------------------------------------------


@dataclass
class _Tri:
    """Items d'une Tâche répartis selon leur issue."""

    ok: list[ItemBase]
    en_erreur: int = 0
    valides: list[tuple[ItemBase, Verdict]] | None = None
    juges: int = 0
    invalides: int = 0
    non_juges: int = 0


def _trier(
    items: Sequence[ItemBase],
    generations: Mapping[str, Generation],
    principal: Mapping[str, Jugement],
    soumis: Iterable[ItemBase] | None = None,
) -> _Tri:
    ok = [item for item in items if item.id in generations and generations[item.id].statut == "ok"]
    tri = _Tri(ok=ok, en_erreur=len(items) - len(ok), valides=[])
    assert tri.valides is not None
    for item in ok if soumis is None else soumis:
        jugement = principal.get(item.id)
        if jugement is None or jugement.statut == "non-juge":
            tri.non_juges += 1
        elif jugement.valide:
            assert jugement.verdict is not None
            tri.juges += 1
            tri.valides.append((item, jugement.verdict))
        else:
            tri.invalides += 1
    return tri


def _score(composantes: Mapping[str, float | None]) -> float | None:
    return _moyenne(composantes.values())


def _q(
    tri: _Tri, controles: Mapping[str, Mapping[str, Any]]
) -> tuple[dict[str, float | None], dict[str, Any], int]:
    reussis = []
    urls = 0
    for item, verdict in tri.valides or []:
        inventees = controles.get(item.id, {}).get("urls_inventees") or []
        urls += bool(inventees)
        if isinstance(item, ItemQ) and item.sans_reponse:
            reussis.append(note(verdict, "cas_sans_reponse") == 1)
        else:
            reussis.append(
                note(verdict, "exactitude") == 2
                and note(verdict, "pertinence_source") == 1
                and not inventees
            )
    return {"reussis": _pourcentage(reussis)}, {"items_avec_url_inventee": urls}, len(reussis)


def _rd(
    tri: _Tri,
    controles: Mapping[str, Mapping[str, Any]],
    principal: Mapping[str, Jugement],
) -> tuple[dict[str, float | None], dict[str, Any], int]:
    attendus = valides = 0
    exactes: list[bool] = []
    notes = 0
    litiges = 0
    for item in tri.ok:
        controle = controles.get(item.id, {})
        compte = False
        if controle.get("appels_attendus"):
            attendus += controle["appels_attendus"]
            valides += controle.get("appels_valides", 0)
            compte = True
        exacte = controle.get("reponse_exacte")
        if controle.get("litige"):
            litiges += 1
            jugement = principal.get(item.id)
            if jugement is not None and jugement.valide and jugement.verdict is not None:
                exacte = note(jugement.verdict, "libelle_correct") == 1
        if exacte is not None:
            exactes.append(bool(exacte))
            compte = True
        notes += compte
    composantes = {
        "appel_valide": 100 * valides / attendus if attendus else None,
        "reponse_exacte": _pourcentage(exactes),
    }
    return composantes, {"litiges": litiges}, notes


def _cr(tri: _Tri) -> tuple[dict[str, float | None], dict[str, Any], int]:
    rappels, sans_invention, structure = [], [], []
    for _, verdict in tri.valides or []:
        rappel = rappel_elements(verdict)
        rappels.append(None if rappel is None else 100 * rappel)
        sans_invention.append(note(verdict, "absence_invention") == 1)
        valeur = note(verdict, "structure")
        structure.append(None if valeur is None else valeur == 1)
    composantes = {"couverture": _moyenne(rappels), "sans_invention": _pourcentage(sans_invention)}
    return composantes, {"structure": _arrondi(_pourcentage(structure))}, len(sans_invention)


def _lc(
    tri: _Tri, controles: Mapping[str, Mapping[str, Any]], seuils: Seuils
) -> tuple[dict[str, float | None], dict[str, Any], int, bool]:
    reussis, gains, clartes = [], [], []
    for item, verdict in tri.valides or []:
        reussis.append(note(verdict, "fidelite") == 2 and note(verdict, "termes_juridiques") == 1)
        gains.append(controles.get(item.id, {}).get("gain_km"))
        clartes.append(note(verdict, "clarte_percue"))
    gain = _moyenne(gains)
    rapportes = {
        "gain_km_moyen": _arrondi(gain),
        "clarte_percue_moyenne": _arrondi(_moyenne(clartes)),
    }
    composantes: dict[str, float | None] = {"fidelite_et_termes": _pourcentage(reussis)}
    plafonne = composantes["fidelite_et_termes"] is not None and (
        gain is not None and gain < seuils.gain_km_min
    )
    return composantes, rapportes, len(reussis), plafonne


def _co(
    tri: _Tri, controles: Mapping[str, Mapping[str, Any]]
) -> tuple[dict[str, float | None], dict[str, Any], int]:
    scores, rappels, taux = [], [], []
    for item in tri.ok:
        controle = controles.get(item.id, {})
        rappel, hors = controle.get("rappel"), controle.get("taux_hors_faute")
        if rappel is None or hors is None:
            continue
        scores.append(100 * rappel * (1 - hors))
        rappels.append(100 * rappel)
        taux.append(100 * hors)
    composantes = {"rappel_x_hors_faute": _moyenne(scores)}
    rapportes = {
        "rappel_moyen": _arrondi(_moyenne(rappels)),
        "taux_hors_faute_moyen": _arrondi(_moyenne(taux)),
    }
    return composantes, rapportes, len(scores)


def _re(
    tri: _Tri, controles: Mapping[str, Mapping[str, Any]]
) -> tuple[dict[str, float | None], dict[str, Any], int]:
    fideles, rappels, respect = [], [], []
    for item, verdict in tri.valides or []:
        fideles.append(note(verdict, "fidelite") == 1)
        rappel = rappel_elements(verdict)
        rappels.append(None if rappel is None else 100 * rappel)
        respect.append(controles.get(item.id, {}).get("respect_longueur"))
    composantes = {"fideles": _pourcentage(fideles), "couverture": _moyenne(rappels)}
    return composantes, {"respect_longueur": _arrondi(_pourcentage(respect))}, len(fideles)


def _ct(
    tri: _Tri, controles: Mapping[str, Mapping[str, Any]]
) -> tuple[dict[str, float | None], dict[str, Any], int]:
    conformites, emplacements = [], []
    for item, verdict in tri.valides or []:
        conformite = note(verdict, "conformite")
        conformites.append(None if conformite is None else conformite / 2 * 100)
        emplacements.append(controles.get(item.id, {}).get("emplacements_reussis"))
    composantes = {"conformite": _moyenne(conformites), "emplacements": _pourcentage(emplacements)}
    return composantes, {}, len(conformites)


def _nr(tri: _Tri) -> tuple[dict[str, float | None], dict[str, Any], int]:
    exacts = [note(verdict, "exactitude") == 1 for _, verdict in tri.valides or []]
    return {"exacts": _pourcentage(exacts)}, {}, len(exacts)


# --- Assemblage ------------------------------------------------------------------------------


def score_tache(
    tache: str,
    items: Sequence[ItemBase],
    *,
    generations: Mapping[str, Generation],
    controles: Mapping[str, Mapping[str, Any]],
    principal: Mapping[str, Jugement],
    second: Mapping[str, Jugement],
    seuils: Seuils,
    jeu_statut: str,
    manifeste_sha256: str | None,
    cout_eur: float = 0.0,
) -> ScoreTache:
    """Score, composantes, effectifs, statuts et kappa d'une Tâche (items de cette Tâche)."""
    plafonne = False
    if tache == "RD":
        tri = _trier(items, generations, principal, soumis=())
        litiges = [i for i in tri.ok if controles.get(i.id, {}).get("litige")]
        tri_litiges = _trier(items, generations, principal, soumis=litiges)
        tri.juges, tri.invalides, tri.non_juges = (
            tri_litiges.juges,
            tri_litiges.invalides,
            tri_litiges.non_juges,
        )
        composantes, rapportes, notes = _rd(tri, controles, principal)
    elif tache == "CO":
        tri = _trier(items, generations, principal, soumis=())
        composantes, rapportes, notes = _co(tri, controles)
    else:
        tri = _trier(items, generations, principal)
        if tache == "Q":
            composantes, rapportes, notes = _q(tri, controles)
        elif tache == "CR":
            composantes, rapportes, notes = _cr(tri)
        elif tache == "LC":
            composantes, rapportes, notes, plafonne = _lc(tri, controles, seuils)
        elif tache == "RE":
            composantes, rapportes, notes = _re(tri, controles)
        elif tache == "CT":
            composantes, rapportes, notes = _ct(tri, controles)
        elif tache == "NR":
            composantes, rapportes, notes = _nr(tri)
        else:
            raise ValueError(f"Tâche inconnue : {tache!r}")
    score = _score(composantes)
    if plafonne and score is not None:
        score = min(score, seuils.plafond_lc)
    kappa = kappa_tache(tache, tri.ok, principal, second)
    ok_ids = {item.id for item in tri.ok}
    second_valides = sum(1 for i, j in second.items() if i in ok_ids and j.valide)
    return ScoreTache(
        tache=tache,  # type: ignore[arg-type]
        score=_arrondi(score) if notes else None,
        composantes={nom: _arrondi(valeur) for nom, valeur in composantes.items()},
        rapportes=rapportes,
        effectifs=Effectifs(
            notes=notes,
            juges=tri.juges,
            invalides=tri.invalides,
            non_juges=tri.non_juges,
            en_erreur=tri.en_erreur,
            second_juge=second_valides,
        ),
        statuts=StatutsTache(
            jeu_statut=jeu_statut,
            verdicts_relus=False,
            fragile=kappa.valeur is not None and kappa.valeur < seuils.kappa_fragile,
            plafonne_lc=plafonne,
        ),
        kappa=kappa,
        cout_juge_eur=round(cout_eur, DECIMALES_COUT),
        manifeste_sha256=manifeste_sha256,
    )


def calculer_scores(
    *,
    items: Sequence[ItemBase],
    generations: Mapping[str, Generation],
    controles: Mapping[str, Mapping[str, Any]],
    principal: Mapping[str, Jugement],
    second: Mapping[str, Jugement],
    seuils: Seuils,
    run_generation: str,
    jeu_version: str,
    jeu_statut: str,
    manifeste_sha256: str | None = None,
    modele_ref: str | None = None,
    quantification: str | None = None,
    couts: Mapping[str, float] | None = None,
    juge_principal: str = "claude",
) -> Scores:
    """Scores de chaque Tâche présente parmi `items` (ordre des codes de SPEC §2).

    `couts` donne le coût du Juge par item (euros, toutes tentatives journalisées des clés
    retenues, Juge principal et second juge).
    """
    couts = couts or {}
    taches: dict[str, ScoreTache] = {}
    for code in CODES:
        de_la_tache = [item for item in items if item.code == code]
        if not de_la_tache:
            continue
        taches[code] = score_tache(
            code,
            de_la_tache,
            generations=generations,
            controles=controles,
            principal=principal,
            second=second,
            seuils=seuils,
            jeu_statut=jeu_statut,
            manifeste_sha256=manifeste_sha256,
            cout_eur=sum(couts.get(item.id, 0.0) for item in de_la_tache),
        )
    return Scores(
        run_generation=run_generation,
        modele_ref=modele_ref,
        quantification=quantification,  # type: ignore[arg-type]
        jeu_version=jeu_version,
        jeu_statut=jeu_statut,
        juge_principal=juge_principal,
        manifeste_sha256=manifeste_sha256,
        version_texte=VERSION_TEXTE,
        taches=taches,
        cout_juge_total_eur=round(sum(couts.values()), DECIMALES_COUT),
    )


__all__ = [
    "CRITERES_KAPPA",
    "Jugement",
    "calculer_scores",
    "kappa_cohen",
    "kappa_tache",
    "note",
    "rappel_elements",
    "score_tache",
]
