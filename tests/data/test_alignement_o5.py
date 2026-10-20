"""Alignement entraînement / évaluation (story O5) : consignes d'Agent, longueur des sources LC.

Chaînes factices uniquement (D1.1) : aucune consigne ni aucun texte du Jeu d'évaluation.
"""

from __future__ import annotations

import difflib
import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("mistralai")

from slmsp.core.erreurs import ConfigurationInvalide  # noqa: E402
from slmsp.data.build import consigne_agent, construire_conversation, rederiver_ligne  # noqa: E402
from slmsp.data.config import (  # noqa: E402
    AlignementDonnees,
    LongueurSourcesLC,
    charger_config_donnees,
)
from slmsp.data.nettoyage import _source_lc  # noqa: E402
from slmsp.data.seed import REGLES, RegleAmorce, _valeurs_regle, regles_alignees  # noqa: E402

from .test_build import contexte, sessions, une_lc  # noqa: E402

CONSIGNES = ["<consigne-factice-1>", "<consigne-factice-2>", "<consigne-factice-3>"]
SCRIPT = Path(__file__).resolve().parents[2] / "outils" / "comparer_entrainement_evaluation.py"


def _alignement(**champs: Any) -> AlignementDonnees:
    return AlignementDonnees(consignes_agent={"LC": CONSIGNES}, **champs)


def test_config_reelle_porte_les_consignes_et_la_longueur_lc() -> None:
    cfg = charger_config_donnees().alignement
    assert set(cfg.consignes_agent) == {"LC", "CR", "CT", "RE", "CO"}
    assert 3 <= len(cfg.consignes_agent["LC"]) <= 5
    assert cfg.longueur_sources_lc is not None
    assert cfg.longueur_sources_lc.tolerance == pytest.approx(0.3)


def test_config_refuse_tache_inconnue_et_liste_vide() -> None:
    with pytest.raises(ValueError, match="tâche inconnue"):
        AlignementDonnees(consignes_agent={"Q": ["<c>"]})
    with pytest.raises(ValueError, match="au moins une"):
        AlignementDonnees(consignes_agent={"LC": []})


def test_bornes_en_mots() -> None:
    cible = LongueurSourcesLC(mediane_mots=100, tolerance=0.3)
    assert (cible.mots_min, cible.mots_max) == (70, 130)


def test_consigne_tiree_par_graine_et_stable() -> None:
    cfg = _alignement(graine=1)
    assert consigne_agent(cfg, "LC", "s-1") == consigne_agent(cfg, "LC", "s-1")
    assert consigne_agent(cfg, "CR", "s-1") is None
    tirees = {consigne_agent(cfg, "LC", f"s-{i}") for i in range(40)}
    assert tirees == set(CONSIGNES)
    autre = _alignement(graine=2)
    assert [consigne_agent(cfg, "LC", f"s-{i}") for i in range(40)] != [
        consigne_agent(autre, "LC", f"s-{i}") for i in range(40)
    ]


def test_build_rend_la_consigne_comme_a_l_evaluation(monde: Any) -> None:
    generation, _ = une_lc(monde)
    (brut,) = sessions(generation)
    ctx = contexte(monde, generation)
    sans = rederiver_ligne(ctx, brut).messages[1]["content"]
    assert sans.startswith("Texte :\n")
    from dataclasses import replace

    avec_ctx = replace(ctx, alignement=_alignement())
    avec = rederiver_ligne(avec_ctx, brut).messages[1]["content"]
    consigne = consigne_agent(avec_ctx.alignement, "LC", brut.session_id)
    assert avec == f"Consigne :\n{consigne}\n\n{sans}"
    # Alignement vide ou absent : mêmes messages qu'avant O5 (aucune consigne ajoutée).
    vide = replace(ctx, alignement=AlignementDonnees())
    _, messages_avant = construire_conversation(ctx.lecteur, ctx.taches, brut, None)
    assert rederiver_ligne(vide, brut).messages == messages_avant
    # Deux contextes distincts, même configuration : même consigne tirée.
    autre_ctx = replace(contexte(monde, generation), alignement=_alignement())
    assert rederiver_ligne(autre_ctx, brut).messages == rederiver_ligne(avec_ctx, brut).messages


def test_nettoyage_retrouve_la_source_lc_avec_consigne() -> None:
    base = "<source-factice> 1 500 €"
    ligne = {"messages": [{"role": "system"}, {"role": "user", "content": f"Texte :\n{base}"}]}
    avec = {
        "messages": [
            {"role": "system"},
            {"role": "user", "content": f"Consigne :\n<c>\n\nTexte :\n{base}"},
        ]
    }
    assert _source_lc(ligne) == base
    assert _source_lc(avec) == base


def test_regles_alignees_ne_touchent_que_lc() -> None:
    cfg = AlignementDonnees(longueur_sources_lc=LongueurSourcesLC(mediane_mots=10, tolerance=0.5))
    alignees = regles_alignees(REGLES, cfg)
    for avant, apres in zip(REGLES, alignees, strict=True):
        if (avant.tache, avant.emplacement) == ("LC", "texte"):
            assert (apres.mots_min, apres.mots_max) == (5, 15)
            assert apres.longueur_min == avant.longueur_min  # plancher en caractères conservé
            assert apres.longueur_max >= avant.longueur_max
        else:
            assert apres == avant
    assert regles_alignees(REGLES, AlignementDonnees()) == tuple(REGLES)


def test_filtre_en_mots_sans_troncature() -> None:
    regle = RegleAmorce("j", "text", "LC", "texte", 1, 10_000, mots_min=3, mots_max=5)
    courts, ok, longs = "<a> <b>", "<a> <b> <c> <d>", "<a> <b> <c> <d> <e> <f>"
    for texte, garde in ((courts, False), (ok, True), (longs, False)):
        trouves = [t for _, t, _ in _valeurs_regle(regle, {"text": texte})]
        assert trouves == ([texte] if garde else [])


def _outil() -> Any:
    spec = importlib.util.spec_from_file_location("comparer_o5", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_outil_de_comparaison_sur_fixtures_factices(tmp_path: Path) -> None:
    outil = _outil()
    train = tmp_path / "v0" / "train.jsonl"
    items = tmp_path / "jeu" / "items.jsonl"
    train.parent.mkdir()
    items.parent.mkdir()
    lignes = [
        {
            "tache": "LC",
            "messages": [
                {"role": "system", "content": "<s>"},
                {"role": "user", "content": "Texte :\n" + " ".join(["<m>"] * 10)},
                {"role": "assistant", "content": " ".join(["<r>"] * 4)},
            ],
        }
    ]
    elements = [
        {"id": "LC-001", "entree": {"consigne": "<c> <c>", "texte": " ".join(["<m>"] * 30)}}
    ]
    train.write_text("\n".join(json.dumps(x) for x in lignes), encoding="utf-8")
    items.write_text("\n".join(json.dumps(x) for x in elements), encoding="utf-8")
    sortie = tmp_path / "rapport.md"
    assert outil.main(["--train", str(train), "--items", str(items), "--sortie", str(sortie)]) == 0
    ligne_lc = next(
        x for x in sortie.read_text(encoding="utf-8").splitlines() if x.startswith("| LC")
    )
    assert "| Consigne / Texte |" in ligne_lc
    assert "| Texte |" in ligne_lc
    assert "| 30 (n=1) | 10 (n=1) | 3.0 |" in ligne_lc
    assert "<c>" not in sortie.read_text(encoding="utf-8")


def test_config_invalide_levee_en_configuration_invalide(tmp_path: Path) -> None:
    source = (Path(__file__).resolve().parents[2] / "config" / "donnees.toml").read_text(
        encoding="utf-8"
    )
    mauvais = tmp_path / "donnees.toml"
    mauvais.write_text(source.replace("mediane_mots = 278", "mediane_mots = 0"), encoding="utf-8")
    with pytest.raises(ConfigurationInvalide):
        charger_config_donnees(mauvais)


RACINE = Path(__file__).resolve().parents[2]


def _consignes_evaluation() -> list[str]:
    """Consignes d'items du Jeu d'évaluation (lecture seule, jamais recopiées)."""
    consignes = []
    for version in ("v1.0", "v1.1"):
        chemin = RACINE / "eval" / "jeu" / version / "items.jsonl"
        if not chemin.is_file():
            pytest.skip(f"Jeu d'évaluation {version} absent")
        for ligne in chemin.read_text(encoding="utf-8").splitlines():
            entree = json.loads(ligne).get("entree") if ligne.strip() else None
            if isinstance(entree, dict) and isinstance(entree.get("consigne"), str):
                consignes.append(entree["consigne"].casefold())
    return consignes


def test_consignes_de_config_eloignees_du_jeu_d_evaluation() -> None:
    """Aucune consigne de la config ne ressemble à une consigne d'item (ratio < 0,6, ni préfixe)."""
    evaluation = _consignes_evaluation()
    assert evaluation
    for tache, variantes in charger_config_donnees().alignement.consignes_agent.items():
        for consigne in variantes:
            c = consigne.casefold()
            racine = c.rstrip(" .")
            for e in evaluation:
                assert not e.startswith(racine) and not c.startswith(e.rstrip(" .")), tache
                m = difflib.SequenceMatcher(None, c, e, autojunk=False)
                if m.real_quick_ratio() >= 0.6 and m.quick_ratio() >= 0.6:
                    assert m.ratio() < 0.6, tache
