"""Étape `filter` (story 9.5) : fuites du Jeu d'évaluation et doublons.

Jeu d'évaluation factice derrière la structure anti-fuite (empreintes et vecteurs fabriqués à la
main), embedder factice, runs `generate` et `validate` produits par les doublures de
`tests/data/conftest.py`. Aucun appel réel ; les textes sont des jetons artificiels (D1.1).
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

import numpy as np
import pytest

pytest.importorskip("mistralai")

from slmsp.core.erreurs import BudgetEpuise, ManifesteInvalide  # noqa: E402
from slmsp.core.items import VecteursAntifuite  # noqa: E402
from slmsp.core.var import dossier_var  # noqa: E402
from slmsp.data.config import charger_config_donnees  # noqa: E402
from slmsp.data.filter import lancer_filtre  # noqa: E402
from slmsp.data.seed import Protection, _empreintes_texte  # noqa: E402
from slmsp.data.validate import lancer_validation  # noqa: E402
from slmsp.mistral.config import charger_mistral  # noqa: E402
from slmsp.mistral.journal import journal_pour  # noqa: E402

from .conftest import CONFIG, OUTILS_MCP  # noqa: E402

DIM = 8
MARQUE = "<proche-factice>"


def phrase(prefixe: str, nombre: int) -> str:
    """`nombre` jetons artificiels distincts : n-grammes contrôlables."""
    return " ".join(f"{prefixe}{i}x" for i in range(nombre))


class EmbedderFactice:
    """Texte avec la marque : vecteur de l'item ; sinon vecteur pseudo-aléatoire orthogonal."""

    dimension = DIM

    def __init__(self) -> None:
        self.lots = 0

    def vectoriser(self, textes: Sequence[str]) -> Any:
        self.lots += 1
        lignes = []
        for texte in textes:
            if MARQUE in texte:
                v = np.zeros(DIM, np.float32)
                v[0] = 1.0
            else:
                graine = int.from_bytes(hashlib.sha256(texte.encode()).digest()[:4], "big")
                v = np.random.default_rng(graine).random(DIM).astype(np.float32)
                v[0] = 0.0
                v /= np.linalg.norm(v)
            lignes.append(v)
        return np.stack(lignes)


def protection(textes: dict[str, str], n: int = 5, seuil: float = 0.5) -> Protection:
    par_item = {cle: frozenset(_empreintes_texte(t, n)) for cle, t in textes.items()}
    index: dict[str, list[str]] = {}
    for cle, empreintes in par_item.items():
        for e in empreintes:
            index.setdefault(e, []).append(cle)
    return Protection(
        versions=("v1.0",),
        n_ngrammes=n,
        seuil=seuil,
        par_item=par_item,
        index={e: tuple(c) for e, c in index.items()},
    )


def items_vecteurs() -> VecteursAntifuite:
    matrice = np.zeros((1, DIM), np.float32)
    matrice[0, 0] = 1.0
    return VecteursAntifuite(cles=("v1.0/item#entree",), matrice=matrice)


def generer(monde: Any, textes: list[tuple[str, str]]) -> Any:
    """Un run `generate` de sessions `generique` : (texte d'amorce, réponse) par session."""
    seed = monde.ecrire_seed(
        [monde.amorce("generique", "demande", ligne=i, texte=a) for i, (a, _) in enumerate(textes)]
    )
    monde.faux.reponses = [{"texte": r} for _, r in textes]
    return monde.lancer({"generique": len(textes)}, seed=seed)


def valider(monde: Any, generation: Any) -> Any:
    return lancer_validation(
        racine=monde.racine,
        generate_run_id=generation.run.run_id,
        journal=journal_lecture(),
        chemin_outils=OUTILS_MCP,
        consigner=lambda _ligne: None,
    )


def journal_lecture() -> Any:
    return journal_pour("generation", charger_mistral(), dossier_var(), lecteur="data")


def filtrer(
    monde: Any, validation: Any, prot: Protection | None = None, embedder: Any = None
) -> Any:
    return lancer_filtre(
        racine=monde.racine,
        validate_run_id=validation.run.run_id,
        journal=journal_lecture(),
        protection=prot if prot is not None else protection({}),
        vecteurs=items_vecteurs(),
        embedder=embedder if embedder is not None else EmbedderFactice(),
        config=charger_config_donnees(CONFIG / "donnees.toml"),
        consigner=lambda _ligne: None,
    )


def motifs(resultat: Any) -> dict[str, str]:
    return {r["session_id"]: r["motif"] for r in resultat.run.lire_jsonl("rejets.jsonl")}


# --- Fuites -----------------------------------------------------------------------------------


def test_fuite_ngram_reponse_qui_reprend_un_item(monde: Any) -> None:
    item = phrase("item", 30)
    generation = generer(
        monde,
        [
            (phrase("a", 12), f"{phrase('p', 6)} {item} {phrase('q', 6)}"),
            (phrase("b", 12), phrase("c", 20)),
        ],
    )
    resultat = filtrer(monde, valider(monde, generation), protection({"v1.0/item": item}))
    assert sorted(motifs(resultat).values()) == ["fuite_ngram"]
    assert len(resultat.run.lire_jsonl("retenus.jsonl")) == 1


def test_fuite_ngram_entree_qui_reprend_un_item(monde: Any) -> None:
    item = phrase("item", 30)
    generation = generer(monde, [(item, phrase("c", 20))])
    resultat = filtrer(monde, valider(monde, generation), protection({"v1.0/item": item}))
    assert list(motifs(resultat).values()) == ["fuite_ngram"]


def test_fuite_cosinus_sans_recouvrement_de_mots(monde: Any) -> None:
    generation = generer(
        monde,
        [(phrase("a", 12), f"{MARQUE} {phrase('c', 10)}"), (phrase("b", 12), phrase("d", 20))],
    )
    resultat = filtrer(
        monde, valider(monde, generation), protection({"v1.0/item": phrase("z", 30)})
    )
    assert list(motifs(resultat).values()) == ["fuite_cosinus"]
    assert len(resultat.run.lire_jsonl("retenus.jsonl")) == 1


def test_aucun_texte_proche_rien_n_est_ecarte(monde: Any) -> None:
    generation = generer(
        monde, [(phrase("a", 12), phrase("c", 20)), (phrase("b", 12), phrase("d", 20))]
    )
    resultat = filtrer(monde, valider(monde, generation))
    assert resultat.statut == "complet"
    assert resultat.run.lire_jsonl("rejets.jsonl") == []
    assert resultat.rapport["taches"]["total"]["taux_rejet"] == 0.0


# --- Doublons ---------------------------------------------------------------------------------


def test_doublon_exact_et_quasi_doublon(monde: Any) -> None:
    entree, reponse = phrase("e", 40), phrase("r", 30)
    generation = generer(
        monde,
        [
            (entree, reponse),  # gardé : le premier
            (entree, reponse),  # doublon exact
            (entree, f"{phrase('r', 29)} autre"),  # quasi-doublon
            (entree, phrase("tout", 30)),  # réponse différente : gardé
        ],
    )
    resultat = filtrer(monde, valider(monde, generation))
    assert list(motifs(resultat).values()) == ["doublon", "doublon"]
    retenus = resultat.run.lire_jsonl("retenus.jsonl")
    bruts = generation.run.lire_jsonl("brut.jsonl")
    assert [r["session_id"] for r in retenus] == [bruts[0]["session_id"], bruts[3]["session_id"]]


# --- Rapport ----------------------------------------------------------------------------------


def test_rapport_taux_de_rejet_par_motif_et_par_tache(monde: Any) -> None:
    item = phrase("item", 30)
    entree = phrase("e", 40)
    generation = generer(
        monde,
        [
            (phrase("a", 12), item),
            (entree, phrase("r", 30)),
            (entree, phrase("r", 30)),
            (phrase("b", 12), phrase("d", 30)),
        ],
    )
    resultat = filtrer(monde, valider(monde, generation), protection({"v1.0/item": item}))
    assert resultat.rapport["taches"]["generique"] == {
        "exemples": 4,
        "retenus": 2,
        "rejets": {"doublon": 1, "fuite_ngram": 1},
        "taux_rejet": 0.5,
    }
    assert resultat.run.manifeste.parents == [resultat.run.manifeste.config["validate_run_id"]]
    assert resultat.run.statut_courant() == "complet"


def test_run_d_un_autre_type_refuse(monde: Any) -> None:
    generation = generer(monde, [(phrase("a", 12), phrase("c", 20))])
    with pytest.raises(ManifesteInvalide):
        lancer_filtre(
            racine=monde.racine,
            validate_run_id=generation.run.run_id,
            journal=journal_lecture(),
            protection=protection({}),
            vecteurs=items_vecteurs(),
            embedder=EmbedderFactice(),
            config=charger_config_donnees(CONFIG / "donnees.toml"),
            consigner=lambda _ligne: None,
        )
    assert not (monde.racine / "runs" / "data-filter").exists()


def test_validate_partiel_rend_filter_partiel(monde: Any) -> None:
    seed = monde.ecrire_seed(
        [monde.amorce("RE", e, ligne=1) for e in ("texte", "longueur_demandee")]
    )
    monde.faux.reponses = [{"texte": phrase("r", 12)}]
    generation = monde.lancer({"RE": 1}, seed=seed)

    def epuise(*_args: Any) -> tuple[bool, str]:
        raise BudgetEpuise("plafond")

    validation = lancer_validation(
        racine=monde.racine,
        generate_run_id=generation.run.run_id,
        journal=journal_lecture(),
        controle=epuise,
        chemin_outils=OUTILS_MCP,
        consigner=lambda _ligne: None,
    )
    assert validation.statut == "partiel-budget"
    resultat = filtrer(monde, validation)
    assert resultat.statut == "partiel-budget"
    assert resultat.run.statut_courant() == "partiel-budget"
    assert validation.run.run_id in resultat.rapport["motif"]


def test_aucun_exemple_valide(monde: Any) -> None:
    url = "https://exemple.invalid/inventee"
    generation = generer(monde, [(phrase("a", 12), f"{phrase('c', 5)} {url}")])
    resultat = filtrer(monde, valider(monde, generation))
    assert resultat.statut == "complet"
    assert resultat.rapport["taches"]["total"] == {
        "exemples": 0,
        "retenus": 0,
        "rejets": {},
        "taux_rejet": 0.0,
    }
