"""Moteur de traduction : `LlmPort` et chrF factices, jamais de serveur ni de sacrebleu réel."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from slmsp.benchmarks.config import BenchmarkConfig
from slmsp.benchmarks.moteurs import ContexteBench, charger_moteur, traduction
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.evenements import Fin, Jeton

REVISION = "b" * 40


class LlmFactice:
    def __init__(self):
        self.appels = []

    def generer(self, messages, *, tools=None, options=None):
        self.appels.append({"messages": messages, "tools": tools, "options": options})
        yield Jeton(texte="<traduction-")
        yield Jeton(texte="factice> ")
        yield Fin(raison="terminee")


def config(**options) -> BenchmarkConfig:
    return BenchmarkConfig(
        nom="traduction",
        moteur="traduction",
        tache="wmt14_flores",
        cible="gguf",
        quantification="les-deux",
        options={"wmt14_phrases": 2, "paires_flores": ["fr-es", "fr-ar"], **options},
        jeux=[
            {"nom": "wmt14", "depot": "wmt/wmt14", "revision": REVISION},
            {"nom": "flores-200", "depot": "facebook/flores", "acces": "conditionnel"},
        ],
    )


def contexte(tmp_path, variante="avant") -> ContexteBench:
    run = SimpleNamespace(dossier=tmp_path / "run", run_id="x")
    return ContexteBench("base:modele-factice", variante, run, tmp_path, "cpu")  # type: ignore[arg-type]


def poser(tmp_path, paire, n=3):
    dossier = tmp_path / "data" / "raw" / "benchmarks" / "wmt14" / REVISION
    dossier.mkdir(parents=True, exist_ok=True)
    lignes = [{"source": f"<source-{i}>", "reference": f"<ref-{i}>"} for i in range(n)]
    (dossier / f"{paire}.jsonl").write_text(
        "\n".join(json.dumps(x) for x in lignes) + "\n", encoding="utf-8"
    )


def chrf_factice(hypotheses, references):
    assert all(h == "<traduction-factice>" for h in hypotheses)
    return 42.0, "nrefs:1|case:mixed|eff:yes|nc:6|nw:0|space:no|version:factice"


def test_chrf_par_paire_avec_signature_et_prompt_tr(tmp_path):
    poser(tmp_path, "en-fr")
    poser(tmp_path, "fr-en")
    llm = LlmFactice()
    sortie = traduction.executer(config(), contexte(tmp_path), llm=llm, calculer=chrf_factice)
    assert sortie.saute is None
    assert sortie.scores == {
        "en-fr.chrf": 42.0,
        "en-fr.n_items": 2,
        "fr-en.chrf": 42.0,
        "fr-en.n_items": 2,
    }
    assert sortie.outil == "sacrebleu"
    assert set(sortie.details["signatures"]) == {"en-fr", "fr-en"}
    premier = llm.appels[0]
    assert premier["tools"] is None and premier["options"]["temperature"] == 0
    utilisateur = premier["messages"][1]["content"]
    assert "Langue source :\nanglais" in utilisateur
    assert "Langue cible :\nfrançais" in utilisateur
    assert "<source-0>" in utilisateur


def test_flores_conditionnel_indisponible_est_saute_et_consigne(tmp_path):
    poser(tmp_path, "en-fr")
    sortie = traduction.executer(
        config(paires_wmt14=["en-fr"]),
        contexte(tmp_path),
        llm=LlmFactice(),
        calculer=chrf_factice,
    )
    assert sortie.saute is None
    assert list(sortie.scores) == ["en-fr.chrf", "en-fr.n_items"]
    assert set(sortie.details["paires_sautees"]) == {"fr-es", "fr-ar"}
    assert "conditionnel" in sortie.details["paires_sautees"]["fr-es"]


def test_aucune_paire_disponible_saute_le_benchmark(tmp_path):
    sortie = traduction.executer(config(), contexte(tmp_path), llm=LlmFactice())
    assert sortie.saute is not None and "aucune paire disponible" in sortie.saute


def test_fichier_de_paire_absent_est_saute(tmp_path):
    poser(tmp_path, "en-fr")
    sortie = traduction.executer(
        config(), contexte(tmp_path), llm=LlmFactice(), calculer=chrf_factice
    )
    assert "fichier absent" in sortie.details["paires_sautees"]["fr-en"]


def test_modele_non_servable_saute(tmp_path, monkeypatch):
    poser(tmp_path, "en-fr")
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(tmp_path / "models"))
    sortie = traduction.executer(config(), contexte(tmp_path, "avant"))
    assert sortie.saute is not None and "non servable" in sortie.saute


def test_moteur_enregistre():
    assert charger_moteur("traduction") is traduction.executer


def test_chrf_sacrebleu_reel():
    pytest.importorskip("sacrebleu")
    score, signature = traduction.calculer_chrf(["le chat dort"], ["le chat dort"])
    assert score == pytest.approx(100.0)
    assert "nc:6" in signature


def test_paire_commune_a_wmt_et_flores_a_des_cles_distinctes(tmp_path):
    poser(tmp_path, "fr-en")
    flores = tmp_path / "data" / "raw" / "benchmarks" / "flores-200" / REVISION
    flores.mkdir(parents=True)
    (flores / "fr-en.jsonl").write_text('{"source": "<s>", "reference": "<r>"}\n', encoding="utf-8")
    cfg = config(paires_wmt14=["fr-en"], paires_flores=["fr-en"])
    cfg.jeux[1].revision = REVISION
    sortie = traduction.executer(cfg, contexte(tmp_path), llm=LlmFactice(), calculer=chrf_factice)
    assert sortie.scores["wmt14.fr-en.n_items"] == 2
    assert sortie.scores["flores-200.fr-en.n_items"] == 1


def test_langue_inconnue_refusee(tmp_path):
    with pytest.raises(ConfigurationInvalide, match="paire de traduction invalide"):
        traduction.executer(config(paires_wmt14=["en-xx"]), contexte(tmp_path), llm=LlmFactice())
