"""Moteur BFCL : `LlmPort` factice et vérificateur réel de `envs/bfcl` (chemins sans bfcl_eval)."""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from slmsp.benchmarks.config import BenchmarkConfig
from slmsp.benchmarks.moteurs import ContexteBench, bfcl, charger_moteur
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton

REVISION = "c" * 40
VERIFIER = Path(__file__).resolve().parents[2] / "envs" / "bfcl" / "verifier.py"
FONCTION = {
    "name": "outil.factice",
    "description": "<outil-factice>",
    "parameters": {
        "type": "dict",
        "properties": {"x": {"type": "float", "description": "<x>"}},
        "required": ["x"],
    },
}


def charger_verifier():
    spec = importlib.util.spec_from_file_location("verifier_bfcl", VERIFIER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LlmFactice:
    """Appelle `outil.factice`, sauf pour une question marquée `<hors-sujet>`."""

    def __init__(self, non_conforme=False):
        self.appels = []
        self.non_conforme = non_conforme

    def generer(self, messages, *, tools=None, options=None):
        self.appels.append({"messages": messages, "tools": tools, "options": options})
        if "<hors-sujet>" in messages[-1]["content"]:
            yield Jeton(texte="<pas-d-appel>")
        elif self.non_conforme:
            yield AppelNonConforme(nom=None, arguments_bruts="<brut>", motif="<motif-factice>")
        else:
            yield AppelOutil(id="1", nom="outil_factice", arguments={"x": 1})
        yield Fin(raison="terminee")


def config(**options) -> BenchmarkConfig:
    return BenchmarkConfig(
        nom="bfcl",
        moteur="bfcl",
        tache="bfcl_simple_multiple_irrelevance",
        cible="gguf",
        quantification="les-deux",
        options={"effectif": 2, **options},
        jeux=[{"nom": "bfcl", "depot": "gorilla-llm/bfcl", "revision": REVISION}],
    )


def contexte(tmp_path) -> ContexteBench:
    run = SimpleNamespace(dossier=tmp_path / "run", run_id="x")
    return ContexteBench("base:modele-factice", "avant", run, tmp_path, "cpu")  # type: ignore[arg-type]


def poser_jeu(tmp_path):
    dossier = tmp_path / "data" / "raw" / "benchmarks" / "bfcl" / REVISION
    dossier.mkdir(parents=True)
    for categorie in ("simple", "multiple", "irrelevance"):
        texte = "<hors-sujet>" if categorie == "irrelevance" else "<question-factice>"
        lignes = [
            {
                "id": f"{categorie}_{i}",
                "question": [[{"role": "user", "content": f"{texte} {i}"}]],
                "function": [FONCTION],
            }
            for i in range(3)
        ]
        (dossier / f"BFCL_v3_{categorie}.json").write_text(
            "\n".join(json.dumps(x) for x in lignes), encoding="utf-8"
        )
        if categorie != "irrelevance":
            (dossier / "possible_answer").mkdir(exist_ok=True)
            (dossier / "possible_answer" / f"BFCL_v3_{categorie}.json").write_text(
                "\n".join(json.dumps({"id": x["id"], "ground_truth": [{}]}) for x in lignes),
                encoding="utf-8",
            )


def sorties(tmp_path) -> dict:
    chemin = tmp_path / "run" / "bfcl" / "avant" / "sorties.json"
    return json.loads(chemin.read_text(encoding="utf-8"))


@pytest.fixture
def banc(tmp_path, monkeypatch):
    poser_jeu(tmp_path)
    # `bfcl_eval` est absent de l'environnement de test : le contrôle AST est remplacé
    # (vrai si le modèle appelle `outil.factice`).
    enveloppe = tmp_path / "verifier_factice.py"
    enveloppe.write_text(
        "import importlib.util, json, sys\n"
        "from pathlib import Path\n"
        f"spec = importlib.util.spec_from_file_location('v', r'{VERIFIER}')\n"
        "v = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(v)\n"
        "ok = lambda item, cat: ('outil.factice' in item['appels'][0], None)\n"
        "donnees = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))\n"
        "Path(sys.argv[2]).write_text(json.dumps(v.verifier(donnees, ok)), encoding='utf-8')\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(bfcl.VARIABLE_COMMANDE, f'"{sys.executable}" "{enveloppe}"')
    return tmp_path


def test_outils_natifs_convertis_et_noms_sans_point():
    (outil,) = bfcl.convertir_outils([FONCTION])
    assert outil["type"] == "function"
    assert outil["function"]["name"] == "outil_factice"
    parametres = outil["function"]["parameters"]
    assert parametres["type"] == "object"
    assert parametres["properties"]["x"]["type"] == "number"


def test_moyenne_exige_toutes_les_categories_attendues():
    bilan = {"precision": 1.0, "n_items": 2}
    complet = bfcl.analyser({"categories": {c: bilan for c in bfcl.CATEGORIES}})
    assert complet.scores["moyenne.precision"] == 1.0
    partiel = bfcl.analyser({"categories": {"simple": bilan, "multiple": bilan}})
    assert "moyenne.precision" not in partiel.scores
    sans_score = {c: bilan for c in bfcl.CATEGORIES} | {"simple": {"precision": None, "n_items": 0}}
    assert "moyenne.precision" not in bfcl.analyser({"categories": sans_score}).scores


def test_bout_en_bout_par_categorie(banc):
    llm = LlmFactice()
    sortie = bfcl.executer(config(), contexte(banc), llm=llm)
    assert sortie.saute is None
    assert sortie.outil == "bfcl-eval"
    assert sortie.scores["irrelevance.precision"] == 1.0
    assert sortie.scores["simple.precision"] == sortie.scores["moyenne.precision"] == 1.0
    assert sortie.scores["simple.precision"] == 1.0
    assert sortie.scores["multiple.n_items"] == 2
    assert all(a["tools"] and a["options"]["temperature"] == 0 for a in llm.appels)
    premier = sorties(banc)["categories"]["simple"][0]
    assert premier["appels"] == [{"outil.factice": {"x": 1}}]


def test_sous_echantillon_deterministe(banc):
    bfcl.executer(config(), contexte(banc), llm=LlmFactice())
    premiers = [i["id"] for i in sorties(banc)["categories"]["simple"]]
    bfcl.executer(config(), contexte(banc), llm=LlmFactice())
    seconds = [i["id"] for i in sorties(banc)["categories"]["simple"]]
    assert premiers == seconds and len(premiers) == 2


def test_appel_non_conforme_est_consigne_et_non_compte(banc):
    bfcl.executer(config(categories=["simple"]), contexte(banc), llm=LlmFactice(non_conforme=True))
    item = sorties(banc)["categories"]["simple"][0]
    assert item["appels"] == [] and item["non_conformes"] == ["<motif-factice>"]


def test_jeu_non_epingle_saute():
    sans = BenchmarkConfig(
        nom="bfcl",
        moteur="bfcl",
        tache="t",
        cible="gguf",
        quantification="les-deux",
        jeux=[{"nom": "bfcl", "depot": "gorilla-llm/bfcl"}],
    )
    ctx = ContexteBench("base:m", "avant", SimpleNamespace(dossier=Path("x")), Path("x"), "cpu")  # type: ignore[arg-type]
    assert "non épinglé" in bfcl.executer(sans, ctx).saute


def test_categorie_inconnue_refusee(banc):
    with pytest.raises(ConfigurationInvalide, match="catégories BFCL inconnues"):
        bfcl.executer(config(categories=["web"]), contexte(banc), llm=LlmFactice())


def test_verificateur_en_echec_leve(banc, monkeypatch):
    echec = banc / "echec.py"
    echec.write_text("raise SystemExit(3)\n", encoding="utf-8")
    monkeypatch.setenv(bfcl.VARIABLE_COMMANDE, f'"{sys.executable}" "{echec}"')
    with pytest.raises(bfcl.BfclEchoue, match="code 3"):
        bfcl.executer(config(categories=["irrelevance"]), contexte(banc), llm=LlmFactice())


def test_commande_par_defaut_isolee(monkeypatch):
    monkeypatch.delenv(bfcl.VARIABLE_COMMANDE, raising=False)
    commande = bfcl.commande_verificateur(Path("e.json"), Path("s.json"))
    assert commande[:5] == ["uv", "run", "--project", "envs/bfcl", "python"]
    assert commande[5] == "envs/bfcl/verifier.py"


def test_verifier_avec_controle_ast_injecte():
    verifier = charger_verifier()
    donnees = {
        "categories": {
            "simple": [
                {"id": "a", "appels": [{"f": {}}], "fonctions": [], "reponse": [{}]},
                {"id": "b", "appels": [{"f": {}}], "fonctions": [], "reponse": [{}]},
                {"id": "c", "appels": [], "fonctions": [], "reponse": [{}]},
            ]
        }
    }
    bilan = verifier.verifier(
        donnees, lambda item, cat: (item["id"] == "a", None if item["id"] == "a" else "<faux>")
    )["categories"]["simple"]
    assert bilan["n_items"] == 3 and bilan["n_corrects"] == 1
    assert bilan["precision"] == pytest.approx(1 / 3)
    assert bilan["erreurs"] == {"b": "<faux>", "c": "aucun appel émis"}


def test_moteur_enregistre():
    assert charger_moteur("bfcl") is bfcl.executer


def test_reponses_absentes_erreur_explicite(banc):
    (
        banc / "data/raw/benchmarks/bfcl" / REVISION / "possible_answer" / "BFCL_v3_simple.json"
    ).unlink()
    with pytest.raises(ConfigurationInvalide, match="réponses BFCL absentes"):
        bfcl.executer(config(categories=["simple"]), contexte(banc), llm=LlmFactice())


def test_erreur_propre_a_l_item_reste_par_item_et_environnement_echoue():
    verifier = charger_verifier()
    item = {"id": "a", "appels": [{"f": {}}], "fonctions": [], "reponse": [{}]}

    def propre(i, c):
        raise KeyError("x")

    def environnement(i, c):
        raise verifier.ErreurEnvironnement("signature")

    bilan = verifier.verifier({"categories": {"simple": [item]}}, propre)
    assert bilan["categories"]["simple"]["precision"] == 0.0
    with pytest.raises(verifier.ErreurEnvironnement):
        verifier.verifier({"categories": {"simple": [item]}}, environnement)
    with pytest.raises(verifier.ErreurEnvironnement, match="absente"):
        verifier.verifier({"categories": {"simple": [{**item, "reponse": None}]}})


def test_verdicts_perimes_supprimes(banc, monkeypatch):
    sortie_dir = banc / "run" / "bfcl" / "avant"
    sortie_dir.mkdir(parents=True)
    (sortie_dir / "verdicts.json").write_text("{}", encoding="utf-8")
    nul = banc / "nul.py"
    nul.write_text("raise SystemExit(0)", encoding="utf-8")
    monkeypatch.setenv(bfcl.VARIABLE_COMMANDE, f'"{sys.executable}" "{nul}"')
    with pytest.raises(bfcl.BfclEchoue, match="illisibles"):
        bfcl.executer(config(categories=["irrelevance"]), contexte(banc), llm=LlmFactice())


def test_parallele_conserve_l_ordre_et_les_parametres(banc):
    class LlmLent(LlmFactice):
        def generer(self, messages, *, tools=None, options=None):
            time.sleep(0.05 if "_0" in str(messages) or "0" in messages[-1]["content"] else 0.0)
            yield from super().generer(messages, tools=tools, options=options)

    attendu = None
    for parallele in (1, 4):
        llm = LlmLent()
        ctx = dataclasses.replace(contexte(banc), parallele=parallele)
        bfcl.executer(config(effectif=3), ctx, llm=llm)
        donnees = sorties(banc)["categories"]
        ids = [[x["id"] for x in lignes] for lignes in donnees.values()]
        assert ids == [[f"{c}_{i}" for i in range(3)] for c in donnees]
        assert all(a["options"] == llm.appels[0]["options"] for a in llm.appels)
        assert len(llm.appels) == 9
        if attendu is None:
            attendu = donnees
        assert donnees == attendu


class EnVol:
    """Compte les appels simultanés ; chaque appel dure `duree` secondes."""

    def __init__(self, duree=0.05):
        self.duree, self.courant, self.pic = duree, 0, 0
        self.verrou = threading.Lock()

    def __enter__(self):
        with self.verrou:
            self.courant += 1
            self.pic = max(self.pic, self.courant)
        time.sleep(self.duree)

    def __exit__(self, *exc):
        with self.verrou:
            self.courant -= 1


# Le jeu factice a 3 questions par catégorie : à N = 4, le pic est borné à 3.
@pytest.mark.parametrize(("parallele", "pic"), [(1, 1), (2, 2), (4, 3)])
def test_parallele_met_n_requetes_en_vol(banc, parallele, pic):
    en_vol = EnVol()

    class LlmCompte(LlmFactice):
        def generer(self, messages, *, tools=None, options=None):
            with en_vol:
                return list(super().generer(messages, tools=tools, options=options))

    ctx = dataclasses.replace(contexte(banc), parallele=parallele)
    sortie = bfcl.executer(config(effectif=4, categories=["simple"]), ctx, llm=LlmCompte())
    assert en_vol.pic == pic
    assert sortie.batch_size == "1"
