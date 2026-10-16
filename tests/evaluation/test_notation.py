"""Phase notation du banc (story 5.6) : run `eval-notation`, juges factices, sans réseau.

Les runs de génération sont fabriqués dans une copie du jeu v1.0 gelé (`depot_eval`) avec
des sorties factices ; le cache de verdicts réel vit dans `tmp_path`. Une ligne de la
matrice I/O de la spec par test.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import pytest
from evaluation_factices import (
    ITEMS_8,
    Fabrique,
    FakeLlmDeterministe,
    JugeFactice,
    verdict_factice,
)

from slmsp.cli import main
from slmsp.core.artefacts import Run, nouveau_run, ouvrir_run
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import CodeSortie, ManifesteInvalide, SlmspError
from slmsp.core.items import lire_jeu
from slmsp.core.schemas.generation import Generation
from slmsp.core.schemas.scores import Scores
from slmsp.evaluation import assemblage, notation
from slmsp.evaluation import generation as phase_generation
from slmsp.evaluation.gel import lire_manifeste
from slmsp.evaluation.notation import (
    FICHIER_CONTROLES,
    FICHIER_RELECTURE,
    FICHIER_SCORES,
    FICHIER_VERDICTS,
    TYPE_RUN,
    Juges,
    noter,
)
from slmsp.evaluation.relecture import NOM_VALIDATION, charger_scores, relecture_validee
from slmsp.judge.cache import CacheVerdicts

MODELE = "base:granite-4.0-1b"
TITRE_RD_001 = "Bénéficiaires de l'APA à domicile : base floutée (V1)"


def fabriquer_generation(
    depot: Path,
    items: Iterable[str] = ITEMS_8,
    *,
    jeu: str = "v1.0",
    textes: Mapping[str, str] | None = None,
    erreurs: Iterable[str] = (),
    statut: str | None = "complet",
) -> Run:
    """Run `eval-generation` fabriqué : une ligne par item, sortie factice."""
    items = list(items)
    erreurs = set(erreurs)
    textes = dict(textes or {})
    run = nouveau_run(
        phase_generation.TYPE_RUN,
        "granite-4.0-1b",
        {"phase": "generation", "items": items},
        racine=depot,
        modele_ref=MODELE,
        quantification="q4_k_m",
        variante_llamacpp="cpu",
        jeu_version=jeu,
    )
    lu = lire_jeu(jeu, depot)
    for identifiant in items:
        item = lu.item(identifiant)
        en_erreur = identifiant in erreurs
        fin = (
            {"type": "erreur", "code": "x", "message": "<erreur-factice>"}
            if en_erreur
            else {"type": "fin", "raison": "terminee"}
        )
        run.ajouter_jsonl(
            phase_generation.FICHIER_GENERATIONS,
            Generation(
                item_id=identifiant,
                tache=item.code,
                statut="erreur" if en_erreur else "ok",
                sortie_canonique={
                    "texte": textes.get(identifiant, f"<sortie-factice-{identifiant}>")
                },
                trace=[fin],
                duree_ms=1,
            ),
        )
    if statut is not None:
        run.terminer(statut)
    return run


@pytest.fixture
def cache(tmp_path: Path) -> CacheVerdicts:
    return CacheVerdicts(tmp_path / "verdicts.sqlite")


def juges_factices(cache: CacheVerdicts, **options: Any) -> Juges:
    return Juges(
        principal=JugeFactice(cache, "principal", **options),
        second=JugeFactice(cache, "second"),
        cache=cache,
        description={"principal": {"modele": "factice"}},
    )


def verdicts(run: Run) -> list[dict[str, Any]]:
    return run.lire_jsonl(FICHIER_VERDICTS)


def runs_notation(depot: Path) -> list[Path]:
    dossier = depot / "runs" / TYPE_RUN
    return sorted(dossier.iterdir()) if dossier.exists() else []


# --- Nominal -----------------------------------------------------------------------------------


def test_nominal_huit_taches(depot_eval: Path, cache: CacheVerdicts) -> None:
    parent = fabriquer_generation(depot_eval)
    juges = juges_factices(cache)
    rapport = noter(parent.run_id, juges=juges, racine=depot_eval)

    run = rapport.run
    assert rapport.statut == "complet" and run.statut_courant() == "complet"
    assert run.type == TYPE_RUN and run.manifeste.parents == [parent.run_id]
    assert run.run_id.split("-")[2:-1] == parent.run_id.split("-")[2:-1]  # même slug
    assert run.manifeste.modele_ref == MODELE and run.manifeste.jeu_version == "v1.0"
    for nom in (FICHIER_CONTROLES, FICHIER_VERDICTS, FICHIER_SCORES, FICHIER_RELECTURE):
        assert (run.dossier / nom).is_file(), nom

    # Principal : Tâches jugées seulement (RD sans litige, CO jamais) ; second : l'échantillon.
    jugees = {"Q-001", "CR-001", "LC-001", "RE-001", "CT-001", "NR-001"}
    assert sorted(juges.principal.recus) == sorted(jugees)
    echantillon = set(lire_manifeste("v1.0", depot_eval).echantillons.second_juge)
    assert juges.second.recus == [i for i in ITEMS_8 if i in echantillon] == ["Q-001"]
    lignes = verdicts(run)
    assert {(ligne["item_id"], ligne["juge"]) for ligne in lignes} == {
        *((i, "principal") for i in juges.principal.recus),
        ("Q-001", "second"),
    }
    assert set(lignes[0]) == {"item_id", "tache", "juge", "statut", "motif", "cle", "verdict"}

    controles = {c["item_id"]: c for c in run.lire_jsonl(FICHIER_CONTROLES)}
    assert set(controles) == set(ITEMS_8)
    scores = Scores.model_validate_json((run.dossier / FICHIER_SCORES).read_bytes())
    assert set(scores.taches) == {"Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR"}
    assert scores.run_generation == parent.run_id and scores.jeu_statut == "provisoire"
    assert scores.manifeste_sha256 is not None
    assert all(t.manifeste_sha256 == scores.manifeste_sha256 for t in scores.taches.values())
    assert scores.cout_juge_total_eur == pytest.approx(7 * 0.0125)
    assert scores.taches["Q"].kappa.effectif == 1
    brut = (run.dossier / FICHIER_SCORES).read_bytes()
    assert brut.endswith(b"}\n") and run.run_id.encode() not in brut

    relecture = (run.dossier / FICHIER_RELECTURE).read_text(encoding="utf-8")
    assert "## CO-001" in relecture and "## NR-001" in relecture and "## Q-001" not in relecture
    assert "<justification-factice>" in relecture


def test_generation_incomplete_refusee(depot_eval: Path, cache: CacheVerdicts) -> None:
    for statut in (None, "interrompu", "partiel-budget"):
        parent = fabriquer_generation(depot_eval, ["Q-001"], statut=statut)
        with pytest.raises(SlmspError, match="notation refusée"):
            noter(parent.run_id, juges=juges_factices(cache), racine=depot_eval)
    assert runs_notation(depot_eval) == []


def test_parent_d_un_autre_type(depot_eval: Path, cache: CacheVerdicts) -> None:
    autre = nouveau_run("bench", "x", {}, racine=depot_eval)
    with pytest.raises(ManifesteInvalide, match="eval-generation"):
        noter(autre.run_id, juges=juges_factices(cache), racine=depot_eval)


def test_jeu_altere_code_4(depot_eval: Path, cache: CacheVerdicts) -> None:
    parent = fabriquer_generation(depot_eval, ["Q-001"])
    items = depot_eval / "eval" / "jeu" / "v1.0" / "items.jsonl"
    items.write_bytes(items.read_bytes() + b"\n")
    juges = juges_factices(cache)
    with pytest.raises(ManifesteInvalide):
        noter(parent.run_id, juges=juges, racine=depot_eval)
    assert juges.principal.recus == [] and runs_notation(depot_eval) == []


def test_item_en_erreur(depot_eval: Path, cache: CacheVerdicts) -> None:
    parent = fabriquer_generation(depot_eval, erreurs=["NR-001", "CO-001"], statut="partiel-erreur")
    juges = juges_factices(cache)
    rapport = noter(parent.run_id, juges=juges, racine=depot_eval)
    assert rapport.statut == "partiel-erreur"
    assert "NR-001" not in juges.principal.recus
    nr = rapport.scores.taches["NR"]
    assert nr.score is None and nr.effectifs.en_erreur == 1 and nr.effectifs.notes == 0
    assert rapport.scores.taches["CO"].effectifs.en_erreur == 1
    assert {c["item_id"] for c in rapport.run.lire_jsonl(FICHIER_CONTROLES)} == set(ITEMS_8) - {
        "NR-001",
        "CO-001",
    }


def test_rd_litige_juge(depot_eval: Path, cache: CacheVerdicts) -> None:
    textes = {"RD-001": f"Voir le jeu « {TITRE_RD_001} »."}
    parent = fabriquer_generation(depot_eval, ["RD-001", "RD-002"], textes=textes)
    juges = juges_factices(cache, fabriquer=lambda item: verdict_factice(item, libelle_correct=1))
    rapport = noter(parent.run_id, juges=juges, racine=depot_eval)
    assert juges.principal.recus == ["RD-001"]  # RD-002 sans litige : jamais jugé
    rd = rapport.scores.taches["RD"]
    assert rd.composantes["reponse_exacte"] == 50.0  # litige tranché à 1, RD-002 faux
    assert rd.effectifs.juges == 1 and rd.rapportes == {"litiges": 1}


def test_rd_litige_sans_verdict_exclu(depot_eval: Path, cache: CacheVerdicts) -> None:
    textes = {"RD-001": f"Voir « {TITRE_RD_001} »."}
    parent = fabriquer_generation(depot_eval, ["RD-001"], textes=textes)
    juges = juges_factices(cache, invalides=["RD-001"])
    rapport = noter(parent.run_id, juges=juges, racine=depot_eval)
    rd = rapport.scores.taches["RD"]
    assert rd.composantes["reponse_exacte"] is None and rd.effectifs.invalides == 1


def test_verdict_invalide(depot_eval: Path, cache: CacheVerdicts) -> None:
    parent = fabriquer_generation(depot_eval, ["NR-001", "NR-002"])
    juges = juges_factices(cache, invalides=["NR-001"])
    rapport = noter(parent.run_id, juges=juges, racine=depot_eval)
    nr = rapport.scores.taches["NR"]
    assert nr.effectifs.invalides == 1 and nr.effectifs.notes == 1 and nr.score == 100.0
    assert rapport.statut == "complet"
    ligne = next(v for v in verdicts(rapport.run) if v["item_id"] == "NR-001")
    assert ligne["statut"] == "invalide" and ligne["verdict"]["invalide"] is True


def test_budget_epuise(depot_eval: Path, cache: CacheVerdicts) -> None:
    parent = fabriquer_generation(depot_eval, ["NR-001", "NR-002", "NR-003"])
    juges = juges_factices(cache, budget_apres=1)
    rapport = noter(parent.run_id, juges=juges, racine=depot_eval)
    assert rapport.statut == "partiel-budget" and rapport.budget_epuise
    nr = rapport.scores.taches["NR"]
    assert nr.effectifs.non_juges == 2 and nr.effectifs.notes == 1
    lignes = [v for v in verdicts(rapport.run) if v["statut"] == "non-juge"]
    assert {v["motif"] for v in lignes} == {"budget"}


def test_budget_epuise_leve_par_le_juge(depot_eval: Path, cache: CacheVerdicts) -> None:
    from slmsp.core.erreurs import BudgetEpuise

    class JugeRuine:
        def juger(self, demandes: Any, echantillon: Any = None) -> Any:
            raise BudgetEpuise("plafond")

    parent = fabriquer_generation(depot_eval, ["Q-001", "NR-001"])
    juges = Juges(principal=JugeRuine(), second=JugeRuine(), cache=cache)
    rapport = noter(parent.run_id, juges=juges, racine=depot_eval)
    assert rapport.statut == "partiel-budget"
    assert rapport.scores.taches["Q"].effectifs.non_juges == 1
    assert rapport.scores.taches["Q"].kappa.effectif == 0


@pytest.mark.parametrize("motif", ["erreur-api", "limite-debit"])
def test_non_juge_hors_budget_partiel_erreur(
    motif: str, depot_eval: Path, cache: CacheVerdicts
) -> None:
    parent = fabriquer_generation(depot_eval, ["NR-001", "NR-002"])
    juges = juges_factices(cache, non_juges={"NR-001": motif})
    rapport = noter(parent.run_id, juges=juges, racine=depot_eval)
    assert rapport.statut == "partiel-erreur" and not rapport.budget_epuise
    assert rapport.run.statut_courant() == "partiel-erreur"
    nr = rapport.scores.taches["NR"]
    assert nr.effectifs.non_juges == 1 and nr.effectifs.notes == 1 and nr.score == 100.0
    ligne = next(v for v in verdicts(rapport.run) if v["item_id"] == "NR-001")
    assert (ligne["statut"], ligne["motif"], ligne["verdict"]) == ("non-juge", motif, None)


def test_second_juge_limite_debit_hors_kappa(depot_eval: Path, cache: CacheVerdicts) -> None:
    echantillon = lire_manifeste("v1.0", depot_eval).echantillons.second_juge
    cible = next(i for i in echantillon if i.split("-")[0] in ("Q", "NR", "LC", "CT"))
    parent = fabriquer_generation(depot_eval, [cible])
    juges = Juges(
        principal=JugeFactice(cache, "principal"),
        second=JugeFactice(cache, "second", non_juges={cible: "limite-debit"}),
        cache=cache,
    )
    rapport = noter(parent.run_id, juges=juges, racine=depot_eval)
    assert rapport.statut == "partiel-erreur" and rapport.demandes_second == 1
    tache = rapport.scores.taches[cible.split("-")[0]]
    assert tache.kappa.effectif == 0 and tache.effectifs.second_juge == 0
    assert tache.effectifs.juges == 1 and tache.effectifs.non_juges == 0
    assert [(v["juge"], v["motif"]) for v in verdicts(rapport.run)] == [
        ("principal", None),
        ("second", "limite-debit"),
    ]


def test_item_non_jugeable_partiel_erreur(
    depot_eval: Path, cache: CacheVerdicts, monkeypatch: pytest.MonkeyPatch
) -> None:
    from slmsp.judge.prompt import ItemNonJugeable

    schema = notation.schema_sortie

    def schema_sans_cr(item: Any) -> Any:
        if item.id == "CR-001":
            raise ItemNonJugeable("CR sans référence d'éléments")
        return schema(item)

    monkeypatch.setattr(notation, "schema_sortie", schema_sans_cr)
    parent = fabriquer_generation(depot_eval, ["CR-001", "NR-001"])
    juges = juges_factices(cache)
    rapport = noter(parent.run_id, juges=juges, racine=depot_eval)
    assert rapport.statut == "partiel-erreur" and juges.principal.recus == ["NR-001"]
    assert rapport.scores.taches["CR"].effectifs.non_juges == 1
    ligne = next(v for v in verdicts(rapport.run) if v["item_id"] == "CR-001")
    assert (ligne["statut"], ligne["motif"]) == ("non-juge", "non-jugeable")


def test_juge_qui_leve_interrompt_le_run(depot_eval: Path, cache: CacheVerdicts) -> None:
    class JugeEnPanne:
        def juger(self, demandes: Any, echantillon: Any = None) -> Any:
            raise RuntimeError("<panne-factice>")

    parent = fabriquer_generation(depot_eval, ["NR-001"])
    juges = Juges(principal=JugeEnPanne(), second=None, cache=cache)
    with pytest.raises(RuntimeError, match="panne-factice"):
        noter(parent.run_id, juges=juges, racine=depot_eval)
    (dossier,) = runs_notation(depot_eval)
    run = ouvrir_run(dossier.name, racine=depot_eval)
    assert run.statut_courant() == "interrompu"
    dernier = (run.dossier / "etat.jsonl").read_text(encoding="utf-8").splitlines()[-1]
    assert "RuntimeError" in json.loads(dernier)["motif"]


def test_fichiers_presents_sans_controle_ni_verdict(depot_eval: Path, cache: CacheVerdicts) -> None:
    parent = fabriquer_generation(
        depot_eval, ["NR-001"], erreurs=["NR-001"], statut="partiel-erreur"
    )
    rapport = noter(parent.run_id, juges=juges_factices(cache), racine=depot_eval)
    assert rapport.statut == "partiel-erreur"
    for nom in (FICHIER_CONTROLES, FICHIER_VERDICTS):
        assert (rapport.run.dossier / nom).read_bytes() == b"", nom
    assert (rapport.run.dossier / FICHIER_SCORES).is_file()
    assert (rapport.run.dossier / FICHIER_RELECTURE).is_file()


def test_ouvrir_juges_surcharge_le_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    from types import SimpleNamespace

    import slmsp.judge.claude as module_claude
    import slmsp.mistral.client as module_mistral
    from slmsp.judge.config import charger_juges

    class Crochets:
        def register_before_request_hook(self, crochet: Any) -> None: ...

        def register_after_success_hook(self, crochet: Any) -> None: ...

    sdk = SimpleNamespace(sdk_configuration=SimpleNamespace(_hooks=Crochets()))
    clients: list[Any] = []
    monkeypatch.setattr(module_claude, "fabriquer_client", lambda config: clients.append(config))
    monkeypatch.setattr(module_mistral, "fabriquer_sdk", lambda config: sdk)

    configure = charger_juges().principal.mode_appel
    autre = "direct" if configure == "batch" else "batch"
    juges = notation.ouvrir_juges(racine_projet(), autre)
    assert juges.principal.config.mode_appel == autre == clients[-1].mode_appel
    assert juges.description["principal"]["mode_appel"] == autre
    assert juges.second is not None and juges.second.client.sdk is sdk
    assert juges.principal.cache is juges.cache is juges.second.cache
    assert notation.ouvrir_juges(racine_projet()).principal.config.mode_appel == configure
    with pytest.raises(ValueError, match="mode d'appel inconnu"):
        notation.ouvrir_juges(racine_projet(), "lot")


def test_cache_plein_scores_identiques(depot_eval: Path, cache: CacheVerdicts) -> None:
    parent = fabriquer_generation(depot_eval)
    premier = juges_factices(cache)
    un = noter(parent.run_id, juges=premier, racine=depot_eval)
    second = juges_factices(cache)
    deux = noter(parent.run_id, juges=second, racine=depot_eval)
    assert premier.principal.appels_payants == 6 and premier.second.appels_payants == 1
    assert second.principal.appels_payants == 0 and second.second.appels_payants == 0
    assert deux.depuis_cache == 7 and deux.cout_session_eur == 0.0
    assert un.run.run_id != deux.run.run_id
    octets_un = (un.run.dossier / FICHIER_SCORES).read_bytes()
    assert octets_un == (deux.run.dossier / FICHIER_SCORES).read_bytes()


def test_relecture_validee(depot_eval: Path, cache: CacheVerdicts) -> None:
    parent = fabriquer_generation(depot_eval, ["NR-001"])
    run = noter(parent.run_id, juges=juges_factices(cache), racine=depot_eval).run
    assert not relecture_validee(run.dossier)
    assert not charger_scores(run.dossier).taches["NR"].statuts.verdicts_relus
    for contenu in ('{"date": "hier"}', "[]", "pas du json", '{"relu_par": "x"}'):
        (run.dossier / NOM_VALIDATION).write_text(contenu, encoding="utf-8")
        assert not relecture_validee(run.dossier)
    (run.dossier / NOM_VALIDATION).write_text('{"date": "2026-10-13"}', encoding="utf-8")
    assert relecture_validee(run.dossier)
    assert charger_scores(run.dossier).taches["NR"].statuts.verdicts_relus
    (run.dossier / NOM_VALIDATION).write_text(
        '{"date": "2026-10-13T09:30:00+02:00"}', encoding="utf-8"
    )
    assert relecture_validee(run.dossier)
    # Out-File / Set-Content -Encoding utf8 de PowerShell 5.1 écrivent un BOM.
    (run.dossier / NOM_VALIDATION).write_bytes(b'\xef\xbb\xbf{"date": "2026-10-13"}')
    assert relecture_validee(run.dossier)


def test_calibrage_sans_manifeste(depot_eval: Path, cache: CacheVerdicts) -> None:
    parent = fabriquer_generation(depot_eval, ["Q-001", "NR-001"], jeu="calibrage")
    rapport = noter(parent.run_id, juges=juges_factices(cache), racine=depot_eval)
    assert rapport.scores.jeu_statut == "calibrage" and rapport.scores.manifeste_sha256 is None
    assert rapport.scores.taches["Q"].statuts.jeu_statut == "calibrage"
    assert "items_jeu" in rapport.run.manifeste.entrees


# --- Imports -----------------------------------------------------------------------------------


def _imports(chemin: Path) -> list[tuple[str, str | None]]:
    """(module importé, fonction englobante ou None) de chaque import du fichier."""
    arbre = ast.parse(chemin.read_text(encoding="utf-8"))
    trouves: list[tuple[str, str | None]] = []

    def visiter(noeud: ast.AST, fonction: str | None) -> None:
        for enfant in ast.iter_child_nodes(noeud):
            courante = enfant.name if isinstance(enfant, ast.FunctionDef) else fonction
            if isinstance(enfant, ast.ImportFrom) and enfant.module:
                trouves.append((enfant.module, fonction))
            elif isinstance(enfant, ast.Import):
                trouves.extend((alias.name, fonction) for alias in enfant.names)
            visiter(enfant, courante)

    visiter(arbre, None)
    return trouves


def test_imports_des_juges_reels_confines() -> None:
    source = racine_projet() / "src" / "slmsp" / "evaluation"
    for module, fonction in _imports(source / "notation.py"):
        if module.startswith(("slmsp.judge.claude", "slmsp.judge.second", "slmsp.mistral")):
            assert fonction == "ouvrir_juges", module
        assert not module.startswith(("anthropic", "mistralai")), module
    for nom in ("controles.py", "scores.py", "relecture.py"):
        for module, _ in _imports(source / nom):
            assert not module.startswith(
                ("anthropic", "mistralai", "slmsp.judge.claude", "slmsp.judge.second")
            ), (nom, module)
    code = (
        "import sys, slmsp.evaluation.controles, slmsp.evaluation.scores, "
        "slmsp.evaluation.notation, slmsp.evaluation.relecture; "
        "print(sorted(m for m in ('anthropic', 'mistralai') if m in sys.modules))"
    )
    sortie = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True, timeout=120
    )
    assert sortie.stdout.strip() == "[]"


# --- CLI ---------------------------------------------------------------------------------------


@pytest.fixture
def juges_cli(monkeypatch: pytest.MonkeyPatch, cache: CacheVerdicts) -> list[Any]:
    ouverts: list[Any] = []

    def ouvrir(racine: Any = None, mode_appel: Any = None) -> Juges:
        ouverts.append((racine, mode_appel))
        return juges_factices(cache)

    monkeypatch.setattr(notation, "ouvrir_juges", ouvrir)
    return ouverts


def test_cli_notation(
    depot_eval: Path, juges_cli: list[Any], capsys: pytest.CaptureFixture[str]
) -> None:
    parent = fabriquer_generation(depot_eval)
    commande = ["eval", "run", "--phase", "notation", "--depuis", parent.run_id]
    code = main([*commande, "--mode-juge", "direct", "--racine", str(depot_eval)])
    assert code == CodeSortie.SUCCES
    assert juges_cli == [(depot_eval, "direct")]
    sortie = capsys.readouterr().out
    assert "Run de notation : " in sortie and "Statut du run : complet" in sortie
    for code_tache in ("Q ", "RD ", "CO ", "NR "):
        assert f"\n{code_tache}" in sortie
    assert "non relu" in sortie
    (run,) = runs_notation(depot_eval)
    assert ouvrir_run(run.name, racine=depot_eval).manifeste.parents == [parent.run_id]


def test_cli_notation_partielle_code_1(depot_eval: Path, juges_cli: list[Any]) -> None:
    parent = fabriquer_generation(depot_eval, erreurs=["NR-001"], statut="partiel-erreur")
    commande = ["eval", "run", "--phase", "notation", "--depuis", parent.run_id]
    assert main([*commande, "--racine", str(depot_eval)]) == CodeSortie.ERREUR


def test_cli_notation_erreur_api_code_1(
    depot_eval: Path,
    cache: CacheVerdicts,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    juges = juges_factices(cache, non_juges={"NR-001": "erreur-api"})
    monkeypatch.setattr(notation, "ouvrir_juges", lambda racine=None, mode_appel=None: juges)
    parent = fabriquer_generation(depot_eval, ["NR-001", "NR-002"])
    commande = ["eval", "run", "--phase", "notation", "--depuis", parent.run_id]
    assert main([*commande, "--racine", str(depot_eval)]) == CodeSortie.ERREUR
    assert "Statut du run : partiel-erreur" in capsys.readouterr().out


@pytest.mark.parametrize(
    "arguments",
    [
        ["--phase", "notation"],
        ["--phase", "notation", "--depuis", "20261012-155024-x-0cdc", "--reprendre", "x"],
        ["--phase", "notation", "--depuis", "20261012-155024-x-0cdc", "--jeu", "v1.0"],
        ["--phase", "generation", "--depuis", "20261012-155024-x-0cdc"],
        ["--phase", "generation", "--mode-juge", "direct", "--jeu", "v1.0"],
        ["--phase", "toutes", "--jeu", "v1.0"],
    ],
)
def test_cli_usage_notation(
    arguments: list[str],
    depot_eval: Path,
    juges_cli: list[Any],
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["eval", "run", *arguments, "--racine", str(depot_eval)]) == CodeSortie.USAGE
    assert "Traceback" not in capsys.readouterr().err
    assert juges_cli == [] and runs_notation(depot_eval) == []


def test_cli_notation_jeu_altere_code_4(depot_eval: Path, juges_cli: list[Any]) -> None:
    parent = fabriquer_generation(depot_eval, ["Q-001"])
    items = depot_eval / "eval" / "jeu" / "v1.0" / "items.jsonl"
    items.write_bytes(items.read_bytes() + b"\n")
    commande = ["eval", "run", "--phase", "notation", "--depuis", parent.run_id]
    assert main([*commande, "--racine", str(depot_eval)]) == CodeSortie.MANIFESTE_INVALIDE


def test_cli_toutes(
    depot_eval: Path,
    modeles: Path,
    juges_cli: list[Any],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(assemblage, "ouvrir_harnais", Fabrique())
    commande = [
        "eval", "run", "--modele", MODELE, "--quantification", "q4_k_m", "--jeu", "v1.0",
        "--items", ",".join(ITEMS_8), "--racine", str(depot_eval),
    ]  # fmt: skip
    assert main(commande) == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert "[8/8]" in sortie and "Run de notation : " in sortie
    (run,) = runs_notation(depot_eval)
    scores = json.loads((run / FICHIER_SCORES).read_text(encoding="utf-8"))
    assert len(scores["taches"]) == 8


def test_cli_toutes_apres_generation_partiel_erreur(
    depot_eval: Path,
    modeles: Path,
    juges_cli: list[Any],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """W1 : un item en erreur n'empêche pas la notation ; la commande sort en code 1."""
    entree = lire_jeu("v1.0", depot_eval).item("NR-001").entree

    def lever(messages: Any) -> BaseException | None:
        if any(entree in str(m.get("content")) for m in messages):
            return RuntimeError("<panne-factice>")
        return None

    monkeypatch.setattr(assemblage, "ouvrir_harnais", Fabrique(FakeLlmDeterministe(lever)))
    commande = [
        "eval", "run", "--modele", MODELE, "--quantification", "q4_k_m", "--jeu", "v1.0",
        "--items", ",".join(ITEMS_8), "--racine", str(depot_eval),
    ]  # fmt: skip
    assert main(commande) == CodeSortie.ERREUR
    assert "Run de notation : " in capsys.readouterr().out
    (run,) = runs_notation(depot_eval)
    assert ouvrir_run(run.name, racine=depot_eval).statut_courant() != "en_cours"
    assert juges_cli != []


def test_second_juge_seulement_apres_verdict_principal_valide(
    depot_eval: Path, cache: CacheVerdicts
) -> None:
    echantillon = lire_manifeste("v1.0", depot_eval).echantillons.second_juge
    cible = next(i for i in echantillon if i.split("-")[0] in ("Q", "NR", "LC", "CT"))
    parent = fabriquer_generation(depot_eval, [cible])
    juges = juges_factices(cache, invalides=[cible])
    rapport = noter(parent.run_id, juges=juges, racine=depot_eval)
    assert rapport.demandes_second == 0
    assert [v["juge"] for v in verdicts(rapport.run)] == ["principal"]
