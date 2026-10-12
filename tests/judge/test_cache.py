"""Cache des verdicts : clé, verdicts, échecs, journal des appels et lots."""

from __future__ import annotations

import dataclasses
import inspect
import sqlite3
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.budget.tarifs import UsageTokens
from slmsp.core.schemas.verdict import Verdict
from slmsp.judge import cache as module_cache
from slmsp.judge.cache import CacheVerdicts, RequeteLot, cle_verdict
from slmsp.judge.grille import Grille
from slmsp.judge.prompt import construire_prompt


def verdict(identifiant: str = "Q-001") -> Verdict:
    return Verdict(
        id=identifiant,
        criteres={"exactitude": {"note": 2, "justification": "<justification-factice>"}},
        inventions=[],
        confiance="haute",
    )


def test_chemin_par_defaut_dans_var_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SLMSP_VAR_DIR", str(tmp_path / "var"))
    cache = CacheVerdicts()
    assert cache.chemin == (tmp_path / "var").resolve() / "verdicts.sqlite"
    assert cache.chemin.is_file()


def test_cle_verdict(items: dict[str, Any], grille: Grille, doublures: SimpleNamespace) -> None:
    item = items["Q-001"]
    sortie = doublures.sortie_factice()
    prompt = construire_prompt(item, sortie, grille)
    base = cle_verdict(item, sortie, prompt, "m", "medium")
    assert len(base) == 64
    assert base == cle_verdict(item, dict(sortie), prompt, "m", "medium")  # stable
    variantes = [
        cle_verdict(items["Q-002"], sortie, prompt, "m", "medium"),
        cle_verdict(item, {**sortie, "texte": "autre"}, prompt, "m", "medium"),
        cle_verdict(item, sortie, dataclasses.replace(prompt, sha_section="0" * 64), "m", "medium"),
        cle_verdict(item, sortie, dataclasses.replace(prompt, sha_gabarit="0" * 64), "m", "medium"),
        cle_verdict(item, sortie, dataclasses.replace(prompt, sha_schema="0" * 64), "m", "medium"),
        cle_verdict(item, sortie, prompt, "autre", "medium"),
        cle_verdict(item, sortie, prompt, "m", "high"),
    ]
    assert len({base, *variantes}) == len(variantes) + 1


def test_cle_sur_la_sortie_canonique(
    items: dict[str, Any], grille: Grille, doublures: SimpleNamespace
) -> None:
    item = items["Q-001"]
    sortie = doublures.sortie_factice()
    prompt = construire_prompt(item, sortie, grille)
    base = cle_verdict(item, sortie, prompt, "m", "medium")
    # Une clé hors de {texte, appels_outils, sources} n'entre pas dans l'empreinte.
    assert cle_verdict(item, {**sortie, "autre": 1}, prompt, "m", "medium") == base
    sans_inconnue = {k: v for k, v in sortie.items() if k != "cle_inconnue"}
    assert cle_verdict(item, sans_inconnue, prompt, "m", "medium") == base
    # `appels_outils` en fait partie, même s'il n'est jamais envoyé au Juge.
    autres_appels = {**sortie, "appels_outils": []}
    assert cle_verdict(item, autres_appels, prompt, "m", "medium") != base
    # Clés absentes : `None` pour le texte, liste vide pour les autres.
    assert cle_verdict(item, {"texte": "t"}, prompt, "m", "medium") == cle_verdict(
        item, {"texte": "t", "appels_outils": [], "sources": None}, prompt, "m", "medium"
    )


def test_verdicts(tmp_path: Path) -> None:
    cache = CacheVerdicts(tmp_path / "v.sqlite")
    assert cache.lire("c1") is None
    usage = UsageTokens(10, 2)
    assert cache.ecrire(
        "c1", verdict(), modele="m", effort="medium", mode="batch", cout_eur=0.5, usage=usage
    )
    lu = cache.lire("c1")
    assert lu is not None and lu.verdict == verdict() and lu.mode == "batch"
    assert lu.cout_eur == 0.5 and lu.usage == usage
    # Jamais réécrit.
    assert not cache.ecrire(
        "c1",
        Verdict.invalide_pour("Q-001"),
        modele="m",
        effort="medium",
        mode="direct",
        cout_eur=1.0,
        usage=None,
    )
    assert cache.lire("c1").verdict == verdict()
    # Persistant entre deux ouvertures.
    assert CacheVerdicts(tmp_path / "v.sqlite").lire("c1").verdict == verdict()


def test_echecs(tmp_path: Path) -> None:
    cache = CacheVerdicts(tmp_path / "v.sqlite")
    assert cache.echecs("c") == 0
    assert cache.compter_echec("c", "Q-001", "JSON illisible") == 1
    assert cache.compter_echec("c", "Q-001", "écart") == 2
    assert CacheVerdicts(tmp_path / "v.sqlite").echecs("c") == 2


def test_journal_des_appels(tmp_path: Path) -> None:
    cache = CacheVerdicts(tmp_path / "v.sqlite")
    cache.journaliser_appel(
        cle="c",
        item_id="Q-001",
        mode="direct",
        lot_id=None,
        usage=UsageTokens(10, 2, 1, 3),
        cout_eur=0.25,
        issue="juge",
    )
    cache.journaliser_appel(
        cle="c", item_id="Q-001", mode="direct", lot_id=None, usage=None, cout_eur=1, issue="x"
    )
    premier, second = cache.appels()
    assert (premier["tokens_entree"], premier["tokens_sortie"]) == (10, 2)
    assert (premier["tokens_ecriture_cache"], premier["tokens_lecture_cache"]) == (1, 3)
    assert premier["cout_eur"] == 0.25 and premier["horodatage"]
    assert second["tokens_entree"] is None and second["issue"] == "x"


def test_cycle_d_un_lot(tmp_path: Path) -> None:
    cache = CacheVerdicts(tmp_path / "v.sqlite")
    requetes = [
        RequeteLot("r00000", "c1", "Q-001", {"type": "object"}),
        RequeteLot("r00001", "c2", "NR-001", {"type": "object", "x": [1]}),
    ]
    cache.creer_lot("slmsp-juge-1", "m", "medium", requetes)
    (lot,) = cache.lots_ouverts()
    assert (lot.statut, lot.batch_id, lot.nb_retenu) == ("reserve", None, None)
    assert cache.requetes_lot("slmsp-juge-1") == requetes
    cache.fixer_retenu("slmsp-juge-1", 1)
    assert cache.requetes_lot("slmsp-juge-1", 1) == requetes[:1]
    cache.marquer_soumis("slmsp-juge-1", "msgbatch_1")
    lot = cache.lot("slmsp-juge-1")
    assert lot is not None and lot.statut == "en_cours" and lot.batch_id == "msgbatch_1"
    assert lot.soumis_le
    cache.changer_statut("slmsp-juge-1", "collecte")
    assert cache.lots_ouverts() == []
    assert cache.lot("slmsp-juge-1").statut == "collecte"
    with pytest.raises(Exception, match="inconnu"):
        cache.changer_statut("slmsp-juge-absent", "annule")


def test_aucune_suppression() -> None:
    source = inspect.getsource(module_cache).upper()
    assert "DELETE" not in source and "DROP" not in source


def test_version_de_schema_inattendue(tmp_path: Path) -> None:
    chemin = tmp_path / "v.sqlite"
    with closing(sqlite3.connect(chemin)) as connexion:
        connexion.execute("PRAGMA user_version = 99")
    with pytest.raises(Exception, match="version de schéma"):
        CacheVerdicts(chemin)
