"""Jeu de développement `dev1` (story O4a, spec O4) : version, gel `relu-llm`, juge par jeu.

Fixtures factices uniquement (chaînes `<…-factice…>`), aucun appel réel. Les fabriques d'items
viennent de `test_gel` ; le jeu v1.1 réel n'est jamais modifié (SHA du manifeste vérifié).
"""

from __future__ import annotations

import hashlib
import importlib.util
import re
import sys
from itertools import cycle
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.cli import main
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import CodeSortie, ConfigurationInvalide
from slmsp.core.items import CODES, MOTIF_VERSION, chemins_jeu, valider_item
from slmsp.core.schemas.manifeste_jeu import ManifesteJeu
from slmsp.core.schemas.scores import Scores
from slmsp.data.config import charger_config_donnees
from slmsp.data.seed import construire_protection, versions_protegees
from slmsp.evaluation import config as cfg
from slmsp.evaluation import notation
from slmsp.evaluation.gel import JeuNonConforme, ecarts_composition, gel, verifier_manifeste
from slmsp.judge.config import ConfigJuges, charger_juges


def _charger_test_gel() -> Any:
    spec = importlib.util.spec_from_file_location(
        "test_gel_pour_dev", Path(__file__).with_name("test_gel.py")
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_gel = _charger_test_gel()
depot = _gel.depot  # fixture réutilisée : dépôt git factice avec grille, cassette et config
ecrire_items, etat, item = _gel.ecrire_items, _gel.etat, _gel.item

SHA_MANIFESTE_V11 = "076edff2ef41c1e965318d52028f5f35937bf9d56702735a756eed0dfefbe762"


def jeu_dev() -> list[dict[str, Any]]:
    """160 items factices conformes à `CIBLES_DEV`, numérotés à partir de 501."""
    cibles = cfg.CIBLES_JEU_DEV
    total = sum(sum(cibles.taches[c]) for c in cfg.TACHES_THEMATIQUES)
    themes = iter([t for t, p in cfg.PARTS_THEMES.items() for _ in range(round(p * total))])
    producteurs = cycle([f"<producteur-{i}>" for i in range(cibles.rd_producteurs)])
    items: list[dict[str, Any]] = []
    for code in CODES:
        numero = 0
        for difficulte, cible in zip(
            ("facile", "moyen", "difficile"), cibles.taches[code], strict=True
        ):
            for _ in range(cible):
                numero += 1
                brut = item(code, 500 + numero, difficulte=difficulte)
                if code in cfg.TACHES_THEMATIQUES:
                    brut["theme"] = next(themes)
                if code == "Q" and numero <= cibles.q_sans_reponse:
                    brut.update(sans_reponse=True, orientation_attendue="<orientation>")
                if code == "Q" and numero > 10:
                    brut["amorce_usager"] = "<amorce>"
                    brut["provenance"].append(
                        {"source": "AgentPublic/sp_questions_corpus", "consulte_le": "2026-10-12"}
                    )
                if code == "RD":
                    brut["producteurs"] = [next(producteurs)]
                    if numero <= cibles.rd_valeurs:
                        brut["valeurs_attendues"] = [numero]
                    if numero > 20 - cibles.rd_repli:
                        brut["mode"] = "repli"
                if code == "CR" and numero <= cibles.cr_longues:
                    brut["entree"]["transcription"] = "mot " * (cfg.SEUIL_CR_LONGUE_MOTS + 1)
                items.append(brut)
    return items


# --- Version et cibles -----------------------------------------------------------------------


@pytest.mark.parametrize("version", ["dev1", "dev12", "v1.0", "v1.1", "v2"])
def test_motif_version_admet(version: str) -> None:
    assert re.fullmatch(MOTIF_VERSION, version)


@pytest.mark.parametrize("version", ["dev", "dev1.1", "Dev1", "devx", "calibrage", "v1.1.2"])
def test_motif_version_refuse(version: str) -> None:
    assert not re.fullmatch(MOTIF_VERSION, version)


def test_chemins_jeu_dev(tmp_path: Path) -> None:
    dossier, items, strict = chemins_jeu("dev1", tmp_path)
    assert dossier == tmp_path / "eval" / "jeu" / "dev1" and strict
    assert items.name == "items.jsonl"


def test_cibles_dev() -> None:
    assert sum(sum(c) for c in cfg.CIBLES_DEV.values()) == 160
    assert set(cfg.CIBLES_DEV) == set(CODES)
    assert all(c == (7, 7, 6) for c in cfg.CIBLES_DEV.values())
    assert cfg.cibles_jeu("dev1") is cfg.CIBLES_JEU_DEV
    assert cfg.cibles_jeu("v1.1") is cfg.CIBLES_V1 and cfg.cibles_jeu("v1.0") is cfg.CIBLES_V1
    assert cfg.CIBLES_V1.taches is cfg.CIBLES and cfg.CIBLES_V1.exactes
    assert cfg.CIBLES_JEU_DEV.cr_longues == 4 and cfg.CIBLES_JEU_DEV.rd_producteurs == 3
    assert "relu-llm" in cfg.STATUTS_GEL and "relu-llm" in cfg.STATUTS_BLOQUANTS


def jeu_dev_valides() -> list[Any]:
    return [valider_item(brut, strict=True) for brut in jeu_dev()]


def test_jeu_dev_conforme_sans_ecart() -> None:
    items = jeu_dev_valides()
    assert len(items) == 160
    assert ecarts_composition(items, "dev1") == []


def test_jeu_dev_compare_a_v11_donne_des_ecarts() -> None:
    assert ecarts_composition(jeu_dev_valides(), "v1.1")  # 160 items contre 225 visés


# --- Gel `relu-llm` --------------------------------------------------------------------------


def test_gel_relu_llm_d_un_jeu_dev_conforme(depot: Path) -> None:
    ecrire_items(depot, jeu_dev(), "dev1")
    manifeste = gel("dev1", "relu-llm", 5, depot)
    assert manifeste.statut == "relu-llm" and manifeste.version == "dev1"
    assert manifeste.ecarts == [] and manifeste.nb_items == 160
    assert (
        ManifesteJeu.model_validate_json(
            (depot / "eval" / "jeu" / "dev1" / "MANIFEST.json").read_bytes()
        ).statut
        == "relu-llm"
    )
    assert verifier_manifeste("dev1", depot).statut == "relu-llm"


def test_gel_relu_llm_refuse_un_ecart_de_composition(depot: Path) -> None:
    items = [i for i in jeu_dev() if i["id"] != "CR-520"]  # 19 CR
    assert sum(i["id"].startswith("CR-") for i in items) == 19
    ecrire_items(depot, items, "dev1")
    avant = etat(depot)
    with pytest.raises(JeuNonConforme, match=r"statut relu-llm.*CR"):
        gel("dev1", "relu-llm", 5, depot)
    assert etat(depot) == avant


def test_gel_relu_d_une_version_vn_garde_la_composition_de_v11(depot: Path) -> None:
    """Les cibles dépendent de la version : 160 items sous `v1.0` restent un écart bloquant."""
    ecrire_items(depot, jeu_dev(), "v1.0")
    with pytest.raises(JeuNonConforme, match="statut relu"):
        gel("v1.0", "relu", 5, depot)


def test_gel_statut_inconnu_cite_les_statuts() -> None:
    with pytest.raises(ValueError, match="relu-llm"):
        gel("dev1", "autre", 5, Path("."))


def test_gel_cli_accepte_dev1_et_relu_llm(depot: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ecrire_items(depot, jeu_dev(), "dev1")
    code = main(
        ["eval", "gel", "--version", "dev1", "--statut", "relu-llm", "--graine", "5",
         "--racine", str(depot)]
    )  # fmt: skip
    assert code == int(CodeSortie.SUCCES)
    assert "dev1 gelé (relu-llm)" in capsys.readouterr().out


def test_gel_cli_refuse_une_version_invalide(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["eval", "gel", "--version", "dev", "--verifier-seulement"])
    assert code == int(CodeSortie.USAGE)
    assert "devN" in capsys.readouterr().err


def test_manifeste_v11_inchange() -> None:
    chemin = racine_projet() / "eval" / "jeu" / "v1.1" / "MANIFEST.json"
    octets = chemin.read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(octets).hexdigest() == SHA_MANIFESTE_V11


# --- Juge principal par jeu ------------------------------------------------------------------


def test_config_juges_par_jeu() -> None:
    config = charger_juges()
    assert config.jeux["dev1"].juge_principal == "glm"
    assert config.jeux["dev1"].second_juge is False
    assert "glm" in config.juges_tiers


def test_config_juge_principal_inconnu_refuse() -> None:
    donnees = charger_juges().model_dump()
    donnees["jeux"] = {"dev1": {"juge_principal": "inconnu"}}
    with pytest.raises(ValueError, match="juge tiers inconnu"):
        ConfigJuges.model_validate(donnees)


def test_config_jeux_n_accepte_que_les_jeux_dev() -> None:
    donnees = charger_juges().model_dump()
    donnees["jeux"] = {"v1.1": {"juge_principal": "glm"}}
    with pytest.raises(ValueError, match="jeux"):
        ConfigJuges.model_validate(donnees)


def _sdk_mistral_interdit(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    import slmsp.mistral.client as module_mistral

    appels: list[str] = []

    def refuser(_config: Any) -> Any:
        appels.append("mistral")
        raise AssertionError("le second juge Mistral ne doit pas être construit")

    monkeypatch.setattr(module_mistral, "fabriquer_sdk", refuser)
    return appels


def test_ouvrir_juges_dev1_route_vers_le_juge_tiers(monkeypatch: pytest.MonkeyPatch) -> None:
    import slmsp.evaluation.juges_tiers as module_tiers

    cache = object()
    tiers = SimpleNamespace(
        cache=cache,
        grille=object(),
        description=lambda: {"nom": "glm", "modele": "<modele-factice>"},
    )
    demandes: list[tuple[str, Any]] = []

    def ouvrir(nom: str, racine: Any = None) -> Any:
        demandes.append((nom, racine))
        return tiers

    monkeypatch.setattr(module_tiers, "ouvrir_juge_tiers", ouvrir)
    appels_mistral = _sdk_mistral_interdit(monkeypatch)
    juges = notation.ouvrir_juges(racine_projet(), None, "dev1")
    assert juges.principal is tiers and juges.cache is cache
    assert juges.second is None and appels_mistral == []
    assert juges.nom_principal == "glm"
    assert demandes == [("glm", racine_projet())]
    assert juges.description == {"principal": {"nom": "glm", "modele": "<modele-factice>"}}


def test_ouvrir_juges_v11_garde_claude_et_mistral(monkeypatch: pytest.MonkeyPatch) -> None:
    import slmsp.evaluation.juges_tiers as module_tiers
    import slmsp.judge.claude as module_claude
    import slmsp.mistral.client as module_mistral

    class Crochets:
        def register_before_request_hook(self, crochet: Any) -> None: ...

        def register_after_success_hook(self, crochet: Any) -> None: ...

    sdk = SimpleNamespace(sdk_configuration=SimpleNamespace(_hooks=Crochets()))
    monkeypatch.setattr(module_claude, "fabriquer_client", lambda config: object())
    monkeypatch.setattr(module_mistral, "fabriquer_sdk", lambda config: sdk)
    monkeypatch.setattr(
        module_tiers, "ouvrir_juge_tiers", lambda *a, **k: pytest.fail("juge tiers ouvert")
    )
    for jeu in (None, "v1.1", "dev2"):  # dev2 : pas de section [jeux.dev2]
        juges = notation.ouvrir_juges(racine_projet(), None, jeu)
        assert juges.nom_principal == "claude" and juges.second is not None
        assert juges.principal.cache is juges.cache is juges.second.cache


def test_jeu_du_run_lit_le_jeu_du_run_de_generation(tmp_path: Path) -> None:
    from slmsp.core.artefacts import nouveau_run

    run = nouveau_run("eval-generation", "x", {}, racine=tmp_path, jeu_version="dev1")
    assert notation.jeu_du_run(run.run_id, tmp_path) == "dev1"


def test_mode_juge_refuse_pour_un_jeu_a_juge_tiers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Revue O4a : `--mode-juge` ne s'applique qu'à Claude ; jamais ignoré en silence."""
    import slmsp.evaluation.juges_tiers as module_tiers

    monkeypatch.setattr(
        module_tiers, "ouvrir_juge_tiers", lambda *a, **k: pytest.fail("juge tiers ouvert")
    )
    with pytest.raises(ValueError, match="--mode-juge sans objet"):
        notation.ouvrir_juges(racine_projet(), "batch", "dev1")


def test_reprise_avec_un_autre_jeu_refusee_avant_les_juges(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Revue O4a : `--reprendre` d'un run dev1 avec `--jeu v1.1` ne change pas de juge."""
    from slmsp.cli import main
    from slmsp.core.artefacts import nouveau_run
    from slmsp.core.erreurs import CodeSortie

    run = nouveau_run("eval-generation", "x", {}, racine=tmp_path, jeu_version="dev1")
    monkeypatch.setattr(notation, "ouvrir_juges", lambda *a, **k: pytest.fail("juges ouverts"))
    commande = ["eval", "run", "--phase", "toutes", "--reprendre", run.run_id]
    code = main([*commande, "--jeu", "v1.1", "--racine", str(tmp_path)])
    assert code == CodeSortie.USAGE


# --- Scores ----------------------------------------------------------------------------------


def test_scores_juge_principal_defaut_claude() -> None:
    contenu = {
        "run_generation": "<run>",
        "jeu_version": "v1.1",
        "jeu_statut": "relu",
        "version_texte": 1,
        "taches": {},
        "cout_juge_total_eur": 0.0,
    }
    assert Scores.model_validate(contenu).juge_principal == "claude"
    assert Scores.model_validate({**contenu, "juge_principal": "glm"}).juge_principal == "glm"


# --- Anti-fuite : `dev*` protégé -------------------------------------------------------------


def test_versions_protegees_inclut_dev(tmp_path: Path) -> None:
    assert versions_protegees(tmp_path) == ("v1.0", "v1.1")
    for version in ("dev2", "dev10", "dev1"):
        ecrire_items(tmp_path, [item("NR", 501)], version)
    (tmp_path / "eval" / "jeu" / "dev3").mkdir()  # sans items.jsonl : ignoré
    (tmp_path / "eval" / "jeu" / "brouillon").mkdir()
    assert versions_protegees(tmp_path) == ("v1.0", "v1.1", "dev1", "dev2", "dev10")


def test_protection_ecarte_une_amorce_recouvrant_dev1(tmp_path: Path) -> None:
    mots = " ".join(f"mot{i}" for i in range(12))
    for version in ("v1.0", "v1.1"):
        ecrire_items(
            tmp_path, [item("NR", 1, entree="<consigne-autre-factice-un-deux-trois>")], version
        )
    ecrire_items(tmp_path, [item("NR", 501, entree=mots)], "dev1")
    protection = construire_protection(
        versions_protegees(tmp_path), charger_config_donnees(), tmp_path
    )
    assert "dev1" in protection.versions
    assert "recouvrement_ngrammes" in protection.motifs(" ".join(mots.split()[:8]))
    assert protection.motifs("<texte-sans-rapport-factice> un deux trois quatre cinq six") == []


def test_construire_protection_sans_dev_inchange(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide):
        construire_protection(("dev1",), charger_config_donnees(), tmp_path)
