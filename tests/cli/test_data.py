"""`slmsp data seed` de bout en bout, sur des jeux parquet factices (story 9.3, AD-17).

Les jeux sont de vrais fichiers parquet (pyarrow, extra `data`) écrits dans `tmp_path` ; la
configuration des sources, la protection anti-fuite et la fabrique de scénarios sont
remplacées par des doublures. Aucun appel d'API, aucun réseau. Tous les textes sont des
chaînes artificielles (`<question-factice-1>`, `<scenario-factice-1>`) produites par le test.
"""

from __future__ import annotations

import json
import secrets
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")

from slmsp.cli import CodeSortie, main  # noqa: E402
from slmsp.cli import data as cli_data  # noqa: E402
from slmsp.core.artefacts import ouvrir_run  # noqa: E402
from slmsp.core.canonique import sha256_hex  # noqa: E402
from slmsp.core.erreurs import BudgetEpuise, ManifesteInvalide, ProvenanceInvalide  # noqa: E402
from slmsp.data.seed import Protection  # noqa: E402
from slmsp.fetch.config import ConfigSources  # noqa: E402

REVISION = "c" * 40
TOML_REGISTRE = """schema_version = 1

[[sources]]
id = "Org/service-public"
licence = "licence-factice"
usage = "diffusable"
auteur_contenu = "public"
genere_par = "humain"

[[sources]]
id = "Org/catalogue"
licence = "licence-factice"
usage = "diffusable"
auteur_contenu = "public"
genere_par = "humain"

[[sources]]
id = "Org/piaf"
licence = "licence-factice"
usage = "recherche"
auteur_contenu = "public"
genere_par = "humain"

[[sources]]
id = "mistral/reponses-generateur"
licence = "licence-factice"
usage = "diffusable"
auteur_contenu = "mistral"
genere_par = "mistral"
"""


def ecrire_parquet(racine: Path, nom: str, colonnes: dict[str, list[Any]]) -> dict[str, Any]:
    dossier = racine / "data" / "raw" / "mediatech" / nom / REVISION
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / f"{nom}.parquet"
    pq.write_table(pa.table(colonnes), chemin)
    octets = chemin.read_bytes()
    return {
        "chemin": f"data/{nom}/{nom}.parquet",
        "sha256": sha256_hex(octets),
        "taille": len(octets),
    }


@pytest.fixture
def monde(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "registre-licences.toml").write_text(TOML_REGISTRE, encoding="utf-8")
    nb = 6
    questions = [
        [
            {
                "sid": f"s{i}",
                "url": f"https://exemple.invalide/{i}",
                "question": f"<question-factice-{i}-{k}>",
            }
            for k in range(2)
        ]
        for i in range(nb)
    ]
    fichiers = {
        "service-public": ecrire_parquet(
            tmp_path,
            "service-public",
            {
                "title": [f"<theme-factice-{i}>" for i in range(nb)],
                "text": [f"<texte-factice-{i}> " + "x" * 400 for i in range(nb)],
                "related_questions": [json.dumps(q) for q in questions],
                "url": [f"https://exemple.invalide/fiche-{i}" for i in range(nb)],
                "doc_id": [f"doc-{i}" for i in range(nb)],
                "chunk_id": [f"chunk-{i}" for i in range(nb)],
                "colonne_inutile": ["<inutile-factice>"] * nb,
            },
        ),
        "data-gouv-datasets-catalog": ecrire_parquet(
            tmp_path,
            "data-gouv-datasets-catalog",
            {
                "title": [f"<jeu-factice-{i}>" for i in range(nb)],
                "url": [f"https://exemple.invalide/jeu-{i}" for i in range(nb)],
                "doc_id": [f"jeu-doc-{i}" for i in range(nb)],
                "chunk_id": [f"jeu-chunk-{i}" for i in range(nb)],
            },
        ),
        "piaf": ecrire_parquet(
            tmp_path,
            "piaf",
            {"question": [f"<demande-factice-{i}>" for i in range(nb)], "id": list(range(nb))},
        ),
    }
    depots = {
        "service-public": "Org/service-public",
        "data-gouv-datasets-catalog": "Org/catalogue",
        "piaf": "Org/piaf",
    }
    config = ConfigSources.model_validate(
        {
            "jeux": [
                {
                    "nom": nom,
                    "depot": depots[nom],
                    "revision": REVISION,
                    "licence": "licence-factice",
                    "fichiers": [fichier],
                }
                for nom, fichier in fichiers.items()
            ]
        }
    )
    monkeypatch.setattr(cli_data, "charger_config_sources", lambda: config)
    monkeypatch.setattr(
        cli_data, "construire_protection", lambda versions, config, racine: Protection.vide()
    )
    return SimpleNamespace(racine=tmp_path, config=config, fichiers=fichiers)


def dossiers_seed(racine: Path) -> list[Path]:
    dossier = racine / "runs" / "data-seed"
    return sorted(dossier.iterdir()) if dossier.exists() else []


def amorces(dossier: Path) -> list[dict[str, Any]]:
    texte = (dossier / "amorces.jsonl").read_text("utf-8")
    return [json.loads(ligne) for ligne in texte.splitlines() if ligne]


def test_seed_de_bout_en_bout(monde: SimpleNamespace, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["data", "seed", "--racine", str(monde.racine), "--facteur", "2"])
    sortie = capsys.readouterr()
    assert code == CodeSortie.SUCCES, sortie.err
    [dossier] = dossiers_seed(monde.racine)
    assert {p.name for p in dossier.iterdir()} >= {"amorces.jsonl", "comptes.json"}
    assert ouvrir_run(dossier.name, racine=monde.racine).statut_courant() == "complet"
    lignes = amorces(dossier)
    par_groupe: dict[str, int] = {}
    for ligne in lignes:
        par_groupe[f"{ligne['tache']}/{ligne['emplacement']}"] = (
            par_groupe.get(f"{ligne['tache']}/{ligne['emplacement']}", 0) + 1
        )
    assert par_groupe == {
        "Q/question": 12,  # 6 fiches x 2 questions, sous la cible
        "RD/demande": 6,
        "CR/theme": 6,
        "LC/texte": 6,
        "CO/texte": 6,
        "generique/demande": 6,
    }  # RE/texte : aucun texte assez long
    assert all(ligne["auteur_contenu"] == "public" for ligne in lignes)
    assert {ligne["jeu"] for ligne in lignes} <= {"Org/service-public", "Org/catalogue", "Org/piaf"}
    assert "run" in sortie.out and "complet" in sortie.out
    assert "Q/question : 12/200 amorces" in sortie.out  # volume Q x facteur 2


def test_amorces_relues_dans_les_jeux(monde: SimpleNamespace) -> None:
    from slmsp.data.seed import verifier_amorces

    assert main(["data", "seed", "--racine", str(monde.racine)]) == CodeSortie.SUCCES
    [dossier] = dossiers_seed(monde.racine)
    jeux = cli_data._jeux_publics(monde.config, monde.racine)
    relues = verifier_amorces(monde.racine, dossier.name, jeux, cli_data._decodeur_pyarrow())
    assert len(relues) == len(amorces(dossier))


def test_jeu_non_telecharge_code_1(
    monde: SimpleNamespace, capsys: pytest.CaptureFixture[str]
) -> None:
    (monde.racine / "data" / "raw" / "mediatech" / "piaf" / REVISION / "piaf.parquet").unlink()
    assert main(["data", "seed", "--racine", str(monde.racine)]) == CodeSortie.ERREUR
    assert "slmsp fetch sources" in capsys.readouterr().err
    assert dossiers_seed(monde.racine) == []


def test_sha_different_code_4(monde: SimpleNamespace, capsys: pytest.CaptureFixture[str]) -> None:
    chemin = monde.racine / "data" / "raw" / "mediatech" / "piaf" / REVISION / "piaf.parquet"
    chemin.write_bytes(chemin.read_bytes() + b"x")
    assert main(["data", "seed", "--racine", str(monde.racine)]) == CodeSortie.MANIFESTE_INVALIDE
    assert "SHA-256" in capsys.readouterr().err
    [dossier] = dossiers_seed(monde.racine)
    assert ouvrir_run(dossier.name, racine=monde.racine).statut_courant() == "partiel-erreur"


def test_source_evaluation_seulement_code_1(
    monde: SimpleNamespace, capsys: pytest.CaptureFixture[str]
) -> None:
    registre = monde.racine / "data" / "registre-licences.toml"
    registre.write_text(
        TOML_REGISTRE.replace('usage = "recherche"', 'usage = "evaluation_seulement"'),
        encoding="utf-8",
    )
    assert main(["data", "seed", "--racine", str(monde.racine)]) == CodeSortie.ERREUR
    assert "evaluation_seulement" in capsys.readouterr().err
    assert dossiers_seed(monde.racine) == []


def test_sans_scenario_ni_mistral_ni_gel(
    monde: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
) -> None:
    def interdit(*_args: Any, **_kwargs: Any) -> Any:
        raise AssertionError("aucun appel Mistral ni contrôle de gel sans --scenarios")

    monkeypatch.setattr(cli_data, "_fabrique_scenarios", interdit)
    monkeypatch.setattr("slmsp.evaluation.gel.jeu_gele_et_commite", interdit)
    assert main(["data", "seed", "--racine", str(monde.racine)]) == CodeSortie.SUCCES


def test_scenarios_refuses_sans_gel_code_4(
    monde: SimpleNamespace, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def non_gele(version: str, racine: Path) -> None:
        assert version == "v1.1"
        raise ManifesteInvalide("jeu v1.1 non commité")

    def interdit(*_args: Any) -> Any:
        raise AssertionError("pas de fabrique Mistral sans gel")

    monkeypatch.setattr("slmsp.evaluation.gel.jeu_gele_et_commite", non_gele)
    monkeypatch.setattr(cli_data, "_fabrique_scenarios", interdit)
    code = main(["data", "seed", "--racine", str(monde.racine), "--scenarios", "2"])
    assert code == CodeSortie.MANIFESTE_INVALIDE
    assert "non commité" in capsys.readouterr().err
    assert dossiers_seed(monde.racine) == []


class Fabrique:
    def __init__(self, budget: int | None = None) -> None:
        self.appels = 0
        self.budget = budget

    def __call__(self, seed_run_id: str, theme_id: str, session_id: str) -> tuple[str, str]:
        if self.budget is not None and self.appels >= self.budget:
            raise BudgetEpuise("plafond factice")
        self.appels += 1
        return secrets.token_hex(16), f"<scenario-factice-{self.appels}>"


def test_scenarios_avec_gel(monde: SimpleNamespace, monkeypatch: pytest.MonkeyPatch) -> None:
    fabrique = Fabrique()
    monkeypatch.setattr("slmsp.evaluation.gel.jeu_gele_et_commite", lambda version, racine: None)
    monkeypatch.setattr(cli_data, "_fabrique_scenarios", lambda racine: fabrique)
    code = main(["data", "seed", "--racine", str(monde.racine), "--scenarios", "2"])
    assert code == CodeSortie.SUCCES
    [dossier] = dossiers_seed(monde.racine)
    scenarios = [a for a in amorces(dossier) if a["emplacement"] == "scenario"]
    assert [a["texte"] for a in scenarios] == ["<scenario-factice-1>", "<scenario-factice-2>"]
    assert all(a["auteur_contenu"] == "mistral" and a["appel_id"] for a in scenarios)
    assert fabrique.appels == 2


def test_budget_epuise_code_3(
    monde: SimpleNamespace, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("slmsp.evaluation.gel.jeu_gele_et_commite", lambda version, racine: None)
    monkeypatch.setattr(cli_data, "_fabrique_scenarios", lambda racine: Fabrique(budget=1))
    code = main(["data", "seed", "--racine", str(monde.racine), "--scenarios", "3"])
    assert code == CodeSortie.BUDGET_EPUISE
    [dossier] = dossiers_seed(monde.racine)
    assert ouvrir_run(dossier.name, racine=monde.racine).statut_courant() == "partiel-budget"
    assert sum(a["emplacement"] == "scenario" for a in amorces(dossier)) == 1
    assert "partiel-budget" in capsys.readouterr().out


@pytest.mark.parametrize("option", [["--facteur", "0"], ["--scenarios", "-1"], ["--facteur", "x"]])
def test_arguments_invalides_code_2(option: list[str]) -> None:
    assert main(["data", "seed", *option]) == CodeSortie.USAGE


@pytest.mark.parametrize("etape", ["generate", "validate", "filter", "build"])
def test_etapes_a_venir_non_implementees(etape: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["data", etape]) == CodeSortie.USAGE
    assert f"non implémentée : data {etape}" in capsys.readouterr().err


def test_data_sans_action_code_2() -> None:
    assert main(["data"]) == CodeSortie.USAGE


# --- Décodeur parquet et fabrique de scénarios ------------------------------------------------


def test_decodeur_pyarrow_colonnes_et_lots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli_data, "TAILLE_LOT", 2)
    fichier = tmp_path / "jeu.parquet"
    pq.write_table(
        pa.table(
            {
                "question": [f"<question-factice-{i}>" for i in range(5)],
                "autre": list(range(5)),
                "liste": [[{"question": f"<q-{i}>"}] for i in range(5)],
            }
        ),
        fichier,
    )
    decodeur = cli_data._decodeur_pyarrow()
    lignes = list(decodeur(fichier.read_bytes(), ["question", "liste"]))
    assert [ligne["question"] for ligne in lignes] == [f"<question-factice-{i}>" for i in range(5)]
    assert set(lignes[0]) == {"question", "liste"}  # seules les colonnes demandées
    assert lignes[3]["liste"] == [{"question": "<q-3>"}]


def test_decodeur_sans_pyarrow(monkeypatch: pytest.MonkeyPatch) -> None:
    import sys

    from slmsp.core.erreurs import ConfigurationInvalide

    monkeypatch.setitem(sys.modules, "pyarrow.parquet", None)
    with pytest.raises(ConfigurationInvalide, match="extra `data`"):
        cli_data._decodeur_pyarrow()


def test_fabrique_depuis_le_generateur(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("mistralai")
    appels: list[tuple[Any, ...]] = []

    class Generation:
        def __init__(self, brut: bytes) -> None:
            self.appel_id = "a" * 32
            self.reponse_brute = brut

    class Generateur:
        def __init__(self, seed_run_id: str, brut: bytes) -> None:
            self.seed_run_id = seed_run_id
            self.brut = brut

        def generer(self, gabarit_id: str, amorce_ids: list[str], session_id: str, tache: str):
            appels.append((self.seed_run_id, gabarit_id, amorce_ids, session_id, tache))
            return Generation(self.brut)

    def reponse(contenu: Any) -> bytes:
        message = {"role": "assistant", "content": contenu}
        return json.dumps({"choices": [{"index": 0, "message": message}]}).encode()

    fabrique = cli_data._fabrique_depuis(
        lambda seed: Generateur(seed, reponse("<scenario-factice-9>"))
    )
    assert fabrique("seed-1", "cr.theme.service-public.4", "session-1") == (
        "a" * 32,
        "<scenario-factice-9>",
    )
    assert appels == [
        ("seed-1", "scenario-reunion", ["cr.theme.service-public.4"], "session-1", "CR")
    ]
    sans_contenu = cli_data._fabrique_depuis(lambda seed: Generateur(seed, reponse("")))
    with pytest.raises(ProvenanceInvalide):
        sans_contenu("seed-1", "cr.theme.x.1", "session-2")
