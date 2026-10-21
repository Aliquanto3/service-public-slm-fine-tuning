"""Bootstrap apparié (story E1b) : deux runs de notation factices, aucun réseau.

Jeu v1.0 copié (`depot_eval`), juges factices : les verdicts sont des chaînes factices.
"""

from __future__ import annotations

import random
import shutil
from pathlib import Path
from typing import Any

import pytest
from evaluation_factices import ITEMS_8, JugeFactice, verdict_factice

from slmsp.cli import main
from slmsp.core.artefacts import nouveau_run
from slmsp.core.erreurs import CodeSortie
from slmsp.core.items import lire_jeu
from slmsp.core.schemas.generation import Generation
from slmsp.evaluation import bootstrap
from slmsp.evaluation import generation as phase_generation
from slmsp.evaluation.notation import Juges, noter
from slmsp.judge.cache import CacheVerdicts

TACHES = ("Q", "CR")
_FUSIONNER = bootstrap._fusionner  # avant le monkeypatch de `_factices`


def _noter(
    depot: Path,
    tmp_path: Path,
    nom: str,
    choix: Any,
    *,
    jeu_version: str = "v1.0",
    items: tuple[str, ...] = ITEMS_8,
    en_erreur: frozenset[str] = frozenset(),
) -> str:
    run = nouveau_run(
        phase_generation.TYPE_RUN,
        "granite-4.0-1b",
        {"phase": "generation", "items": list(items)},
        racine=depot,
        modele_ref="base:granite-4.0-1b",
        quantification="q4_k_m",
        variante_llamacpp="cpu",
        jeu_version=jeu_version,
    )
    jeu = lire_jeu(jeu_version, depot)
    for identifiant in items:
        run.ajouter_jsonl(
            phase_generation.FICHIER_GENERATIONS,
            Generation(
                item_id=identifiant,
                tache=jeu.item(identifiant).code,
                statut="erreur" if identifiant in en_erreur else "ok",
                sortie_canonique={"texte": f"<réponse-factice-{nom}-{identifiant}>"},
                trace=[{"type": "fin", "raison": "terminee"}],
                duree_ms=1,
            ),
        )
    run.terminer("complet")
    cache = CacheVerdicts(tmp_path / f"verdicts-{nom}-{jeu_version}.sqlite")
    juges = Juges(
        principal=JugeFactice(cache, "principal", fabriquer=lambda i: verdict_factice(i, choix)),
        second=JugeFactice(cache, "second"),
        cache=cache,
        description={"principal": {"modele": "factice"}},
    )
    return noter(run.run_id, juges=juges, racine=depot).run.run_id


@pytest.fixture
def notations(depot_eval: Path, tmp_path: Path) -> tuple[Path, str, str]:
    a = _noter(depot_eval, tmp_path, "a", min)
    b = _noter(depot_eval, tmp_path, "b", max)
    return depot_eval, a, b


def test_recalcul_identique_et_ecart_nul_avec_soi_meme(
    notations: tuple[Path, str, str],
) -> None:
    depot, a, _ = notations
    seuils = bootstrap.cfg.charger_evaluation().seuils
    charge = bootstrap.charger_run(a, depot, seuils)
    bootstrap.verifier_recalcul(charge)  # ne lève pas

    resultat = bootstrap.comparer_runs([a, a], racine=depot, tirages=50, graine=3)
    for ligne in resultat.comparaisons[0].lignes:
        assert ligne.ecart == 0
        assert ligne.ic is not None and ligne.ic.bas == ligne.ic.haut == 0
        assert ligne.p_positif == 0


def test_ic_contient_ecart_observe_et_graine_reproductible(
    notations: tuple[Path, str, str],
) -> None:
    depot, a, b = notations
    premier = bootstrap.comparer_runs([a, b], racine=depot, tirages=200, graine=5)
    second = bootstrap.comparer_runs([a, b], racine=depot, tirages=200, graine=5)
    assert premier == second
    lignes = {ligne.nom: ligne for ligne in premier.comparaisons[0].lignes}
    assert bootstrap.QUALITE in lignes
    for ligne in lignes.values():
        if ligne.ecart is None:
            continue
        assert ligne.ic is not None and ligne.ic.bas <= ligne.ecart <= ligne.ic.haut
        assert ligne.p_positif is not None and 0 <= ligne.p_positif <= 1
    assert premier.bruit_qualite[a] is not None


def test_recalcul_different_de_scores_json_refuse(notations: tuple[Path, str, str]) -> None:
    depot, a, _ = notations
    seuils = bootstrap.cfg.charger_evaluation().seuils
    charge = bootstrap.charger_run(a, depot, seuils)
    charge.principal.clear()  # verdicts absents : le recalcul s'écarte de scores.json
    with pytest.raises(bootstrap.ErreurRecalcul, match="scores.json"):
        bootstrap.verifier_recalcul(charge)


def test_cli_sortie_markdown(notations: tuple[Path, str, str], tmp_path: Path, capsys: Any) -> None:
    depot, a, b = notations
    sortie = tmp_path / "comparaison.md"
    code = main(
        [
            "eval",
            "comparer",
            "--runs",
            a,
            b,
            "--bootstrap",
            "20",
            "--sortie",
            str(sortie),
            "--racine",
            str(depot),
        ]
    )
    assert code == int(CodeSortie.SUCCES)
    texte = sortie.read_text(encoding="utf-8")
    assert "| Tâche |" in texte and "Bruit items" in texte
    assert texte.strip() in capsys.readouterr().out


class _Item:
    def __init__(self, identifiant: str, code: str) -> None:
        self.id, self.code = identifiant, code


class _RunFactice(bootstrap.RunCharge):
    """Run sans fichiers : score d'une Tâche = part d'items dont l'id est pair, ou None."""

    def __init__(
        self,
        nom: str,
        items: list[_Item],
        sans_score: tuple[str, ...] = (),
        *,
        jeu: str = "v1",
        juge: str = "claude",
        statut: str = "relu",
        version_harnais: int = 1,
    ) -> None:
        self.version_harnais, self.jeu_statut = version_harnais, statut
        self.run_id, self.items, self._sans = nom, items, sans_score  # type: ignore[assignment]
        attributs = {"taches": {}, "jeu_version": jeu, "juge_principal": juge, "jeu_statut": statut}
        self.scores = type("S", (), attributs)()  # type: ignore[assignment]

    def score(self, tache: str, items: Any, *, avec_second: bool) -> float | None:
        if tache in self._sans or not items:
            return None
        return 100 * sum(int(i.id[-1]) % 2 == 0 for i in items) / len(items)


def _items(codes: dict[str, int]) -> list[_Item]:
    return [_Item(f"{c}-{n:03d}", c) for c, k in codes.items() for n in range(k)]


def test_items_differents_et_tache_absente_avertis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap, "verifier_recalcul", lambda run: None)
    a = _RunFactice("a", _items({"Q": 6, "CR": 4}))
    b = _RunFactice("b", _items({"Q": 4}))
    resultat = bootstrap.comparer([a, b], tirages=30, graine=1)
    assert any("CR" in w and "retirée" in w for w in resultat.avertissements)
    assert any("Q" in w and "4 items communs" in w for w in resultat.avertissements)
    assert "Avertissement" in bootstrap.tableau_markdown(resultat)


def test_qualite_sur_taches_definies_partout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap, "verifier_recalcul", lambda run: None)
    a = _RunFactice("a", _items({"Q": 4, "CR": 4}))
    b = _RunFactice("b", _items({"Q": 4, "CR": 4}), sans_score=("CR",))
    resultat = bootstrap.comparer([a, b], tirages=30, graine=1)
    assert resultat.tirages_partiels == 30
    assert any("30/30" in w for w in resultat.avertissements)
    qualite = next(x for x in resultat.comparaisons[0].lignes if x.nom == bootstrap.QUALITE)
    q = next(x for x in resultat.comparaisons[0].lignes if x.nom == "Q")
    assert qualite.score_a == q.score_a  # Qualité d'A sur Q seul, comme B
    assert qualite.ecart == q.ecart
    assert qualite.n_valides == 30


@pytest.mark.parametrize(
    ("options", "motif"),
    [
        ({"jeu": "dev1"}, "jeux dev1, v1"),
        ({"juge": "glm"}, "juges principaux claude, glm"),
        ({"version_harnais": 2}, "versions de harnais 1, 2"),
    ],
)
def test_jeux_ou_juges_differents_refuses(
    monkeypatch: pytest.MonkeyPatch, options: dict[str, str], motif: str
) -> None:
    """Revue O4a : un écart de jeu ou de juge principal est refusé, sauf option explicite."""
    monkeypatch.setattr(bootstrap, "verifier_recalcul", lambda run: None)
    a = _RunFactice("a", _items({"Q": 4}))
    b = _RunFactice("b", _items({"Q": 4}), **options)
    with pytest.raises(ValueError, match=motif):
        bootstrap.comparer([a, b], tirages=5, graine=1)
    resultat = bootstrap.comparer([a, b], tirages=5, graine=1, autoriser_jeux_differents=True)
    assert any("différents" in w for w in resultat.avertissements)


def test_jeu_relu_llm_signale(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap, "verifier_recalcul", lambda run: None)
    runs = [
        _RunFactice(n, _items({"Q": 4}), jeu="dev1", juge="glm", statut="relu-llm")
        for n in ("a", "b")
    ]
    resultat = bootstrap.comparer(runs, tirages=5, graine=1)
    assert any("relu-llm" in w for w in resultat.avertissements)


def test_items_exclus_retires_avant_tirage(monkeypatch: pytest.MonkeyPatch) -> None:
    """Revue 17.5a : un item non noté d'un côté sort de l'ensemble commun des deux runs."""
    monkeypatch.setattr(bootstrap, "verifier_recalcul", lambda run: None)
    a = _RunFactice("a", _items({"Q": 6}))
    b = _RunFactice("b", _items({"Q": 6}))
    resultat = bootstrap.comparer([a, b], tirages=20, graine=1, exclus={"Q-000", "Q-002"})
    assert resultat.items_communs == {"Q": 4}
    assert any("4 items communs" in w for w in resultat.avertissements)
    assert resultat.observes[0]["Q"] == 25.0  # Q-001, Q-003, Q-004, Q-005 : un seul pair


# --- Story 16.5 : paires regroupées (jeux dev1 + dev2), sur runs factices ---


class _ItemCopiable(_Item):
    def model_copy(self, *, update: dict[str, Any]) -> _ItemCopiable:
        return _ItemCopiable(update["id"], self.code)


def _paire(jeu: str, n: int, **options: Any) -> tuple[bootstrap.RunCharge, bootstrap.RunCharge]:
    grille = options.pop("grille", None)

    def run(nom: str) -> _RunFactice:
        items = [_ItemCopiable(f"Q-{k:03d}", "Q") for k in range(n)]
        r = _RunFactice(f"{nom}_{jeu}", items, jeu=jeu, **options)  # type: ignore[arg-type]
        r.generations = r.controles = r.principal = r.second = {}
        r.grille_sha256, r.seuils = grille, None  # type: ignore[assignment]
        return r

    return run("a"), run("b")


def _fusion_factice(runs: Any, prefixes: Any) -> _RunFactice:
    items = [
        _ItemCopiable(p + i.id, i.code)
        for r, p in zip(runs, prefixes, strict=True)
        for i in r.items
    ]
    return _RunFactice("fusion", items, jeu=runs[0].scores.jeu_version)  # type: ignore[arg-type]


@pytest.fixture
def _factices(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bootstrap, "verifier_recalcul", lambda run: None)
    monkeypatch.setattr(bootstrap, "items_non_notes", lambda run: set())
    monkeypatch.setattr(bootstrap, "_fusionner", _fusion_factice)


@pytest.mark.usefixtures("_factices")
def test_regroupe_union_des_items_et_rapport_cote_a_cote() -> None:
    """Qualité regroupée = score sur l'union (pondéré par les items), pas la moyenne des jeux."""
    groupe = bootstrap.comparer_paires([_paire("dev1", 2), _paire("dev2", 6)], tirages=20)
    assert groupe.regroupe.items_communs == {"Q": 8}
    assert [r.items_communs for r in groupe.paires] == [{"Q": 2}, {"Q": 6}]
    # ids pairs : dev1 (Q-000, Q-001) 50 %, dev2 (Q-000..Q-005) 50 % ; union 50 %
    assert groupe.regroupe.observes[0]["Q"] == 100 * 4 / 8
    texte = bootstrap.tableau_markdown_groupe(groupe)
    assert "| Tâche | dev1 (paire 1) | dev2 (paire 2) | Regroupé |" in texte
    assert "## Regroupé" in texte


def test_tirage_stratifie_reste_dans_son_jeu() -> None:
    rng = random.Random(3)
    strates = {"a": "1", "b": "1", "c": "2", "d": "2", "e": "2"}
    for _ in range(50):
        tire = bootstrap._tirer_par_strate(rng, ["a", "b", "c", "d", "e"], strates)
        assert len(tire) == 5
        assert {strates[i] for i in tire[:2]} == {"1"}
        assert {strates[i] for i in tire[2:]} == {"2"}


@pytest.mark.usefixtures("_factices")
@pytest.mark.parametrize(
    ("options", "motif"),
    [
        ({"juge": "glm"}, "juges principaux"),
        ({"grille": "g" * 64}, "grilles du juge différentes"),
    ],
)
def test_regroupe_refuse_juges_ou_grilles_differents(options: dict[str, str], motif: str) -> None:
    with pytest.raises(ValueError, match=motif):
        bootstrap.comparer_paires(
            [
                _paire("dev1", 4, grille="h" * 64),
                _paire("dev2", 4, **({"grille": "h" * 64} | options)),
            ],
            tirages=5,
        )


@pytest.mark.usefixtures("_factices")
def test_regroupe_refuse_harnais_differents_dans_une_paire() -> None:
    a, _b = _paire("dev1", 4)
    _a2, b2 = _paire("dev1", 4, version_harnais=2)
    with pytest.raises(ValueError, match="versions de harnais"):
        bootstrap.comparer_paires([(a, b2), _paire("dev2", 4)], tirages=5)


@pytest.mark.usefixtures("_factices")
def test_une_seule_paire_refusee_par_le_regroupement() -> None:
    with pytest.raises(ValueError, match="deux paires"):
        bootstrap.comparer_paires([_paire("dev1", 4)], tirages=5)


def test_cli_paire_unique_equivaut_a_runs(notations: tuple[Path, str, str], capsys: Any) -> None:
    depot, a, b = notations
    base = ["--bootstrap", "20", "--racine", str(depot)]
    assert main(["eval", "comparer", "--runs", a, b, *base]) == int(CodeSortie.SUCCES)
    avec_runs = capsys.readouterr().out
    assert main(["eval", "comparer", "--paire", a, b, *base]) == int(CodeSortie.SUCCES)
    assert capsys.readouterr().out == avec_runs


def test_cli_paire_repetee_refusee(notations: tuple[Path, str, str], capsys: Any) -> None:
    """Un même jeu dans deux paires compterait ses items deux fois (IC trop étroit)."""
    depot, a, b = notations
    base = ["--bootstrap", "20", "--racine", str(depot)]
    code = main(["eval", "comparer", "--paire", a, b, "--paire", a, b, *base])
    assert code == int(CodeSortie.USAGE)
    assert "jeu v1.0 dans les paires 1 et 2" in capsys.readouterr().err
    assert main(["eval", "comparer", "--runs", a, "--paire", a, b, *base]) == int(CodeSortie.USAGE)


@pytest.mark.usefixtures("_factices")
@pytest.mark.parametrize("autoriser", [False, True])
def test_regroupe_refuse_harnais_differents_entre_paires_meme_autorise(autoriser: bool) -> None:
    with pytest.raises(ValueError, match="paires non regroupables : versions de harnais"):
        bootstrap.comparer_paires(
            [_paire("dev1", 4), _paire("dev2", 4, version_harnais=2)],
            tirages=5,
            autoriser_jeux_differents=autoriser,
        )


@pytest.mark.usefixtures("_factices")
def test_regroupe_refuse_un_jeu_dans_deux_paires_meme_autorise() -> None:
    with pytest.raises(ValueError, match="jeu dev1 dans les paires 1 et 2"):
        bootstrap.comparer_paires(
            [_paire("dev1", 4), _paire("dev1", 4)], tirages=5, autoriser_jeux_differents=True
        )


@pytest.mark.usefixtures("_factices")
def test_regroupe_relu_llm_si_l_un_des_jeux_l_est() -> None:
    relu_llm = bootstrap.cfg.STATUT_RELU_LLM
    groupe = bootstrap.comparer_paires(
        [_paire("v1", 4, statut="gele"), _paire("dev2", 4, statut=relu_llm)], tirages=5
    )
    assert not any("relu-llm" in w for w in groupe.paires[0].avertissements)
    assert any("relu-llm" in w for w in groupe.paires[1].avertissements)
    gele, relu = _paire("v1", 2, statut="gele"), _paire("dev2", 2, statut=relu_llm)
    assert _FUSIONNER([gele[0], relu[0]], ["0/", "1/"]).jeu_statut == relu_llm
    assert _FUSIONNER([gele[0], gele[1]], ["0/", "1/"]).jeu_statut == "gele"


def _items_par_tache(depot: Path, jeu_version: str) -> tuple[str, ...]:
    """Deux items par Tâche du jeu, dans l'ordre du jeu."""
    choisis: dict[str, list[str]] = {}
    for item in lire_jeu(jeu_version, depot).items:
        liste = choisis.setdefault(item.code, [])
        if len(liste) < 2:
            liste.append(item.id)
    return tuple(i for liste in choisis.values() for i in liste)


def test_regroupe_reel_dev1_dev2_stratifie_et_exclusions(
    depot_eval: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Runs réels sur dev1 et dev2 : union, exclusion appariée d'un item non noté, strates."""
    for jeu in ("dev1", "dev2"):
        source = bootstrap.racine_projet() / "eval" / "jeu" / jeu
        shutil.copytree(source, depot_eval / "eval" / "jeu" / jeu)
    items = {jeu: _items_par_tache(depot_eval, jeu) for jeu in ("dev1", "dev2")}
    cr_dev2 = next(i for i in items["dev2"] if i.startswith("CR-"))
    ids = {
        (nom, jeu): _noter(
            depot_eval,
            tmp_path,
            nom,
            choix,
            jeu_version=jeu,
            items=items[jeu],
            en_erreur=frozenset({cr_dev2}) if (nom, jeu) == ("b", "dev2") else frozenset(),
        )
        for nom, choix in (("a", min), ("b", max))
        for jeu in ("dev1", "dev2")
    }
    tires: list[list[str]] = []
    original = bootstrap._tirer_par_strate

    def espion(rng: Any, liste: Any, strates: Any) -> list[str]:
        tire = original(rng, liste, strates)
        tires.append(tire)
        for strate in set(strates.values()):
            effectif = sum(strates[i] == strate for i in liste)
            assert sum(strates[i] == strate for i in tire) == effectif
        return tire

    monkeypatch.setattr(bootstrap, "_tirer_par_strate", espion)
    groupe = bootstrap.comparer_paires_runs(
        [(ids["a", "dev1"], ids["b", "dev1"]), (ids["a", "dev2"], ids["b", "dev2"])],
        racine=depot_eval,
        tirages=30,
        graine=3,
    )
    assert groupe.jeux == ["dev1", "dev2"]
    assert len(tires) >= 30
    assert all({i.split("/")[0] for i in tire} <= {"0", "1"} for tire in tires)
    assert groupe.paires[1].items_communs["CR"] == 1  # item en erreur retiré des deux côtés
    for code, n in groupe.regroupe.items_communs.items():
        assert n == sum(p.items_communs.get(code, 0) for p in groupe.paires)
    assert any("relu-llm" in w for w in groupe.regroupe.avertissements)
    texte = bootstrap.tableau_markdown_groupe(groupe)
    assert "| Tâche | dev1 (paire 1) | dev2 (paire 2) | Regroupé |" in texte
