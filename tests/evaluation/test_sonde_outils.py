"""Sonde de tool calling par modèle, H-TOOLS (story 8.2).

Harnais factice par protocole (le `FakeLlm` dépend de `modele.config.protocole_outils`
reçu par la fabrique) et Bac à sable réel sur les cassettes du calibrage copiées dans
`tmp_path`. Règle D1.1 : arguments et motifs sont des mots aléatoires (`mots`). Le test
réel (`lent` + `integration`) sonde Granite 1B sur RD-001.
"""

from __future__ import annotations

import functools
import importlib.util
import json
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from evaluation_factices import SLUG, FakeLlmDeterministe, harnais_factice
from harness_factices import mots

from slmsp.cli import main
from slmsp.core.erreurs import CodeSortie
from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton
from slmsp.core.items import lire_jeu
from slmsp.core.schemas.generation import Generation
from slmsp.evaluation import assemblage
from slmsp.evaluation.assemblage import ouvrir_harnais
from slmsp.evaluation.sonde_outils import (
    FICHIER_RECOMMANDATION,
    FICHIER_SONDE,
    ITEMS_SONDE,
    TYPE_RUN,
    evaluer,
    sonder,
)
from slmsp.inference.serveur import charger_config_modele

MODELE = f"base:{SLUG}"
NATIF = "natif"
JSON = "json-generique"


# --- Doublures ---------------------------------------------------------------------------------


def _premier_tour(messages: Sequence[Mapping[str, Any]], tools: Any) -> bool:
    return bool(tools) and not any(m.get("role") == "tool" for m in messages)


class FakeLlmSonde(FakeLlmDeterministe):
    """Au premier tour avec outils : `non_conformes` appels non conformes, puis l'appel
    `search_datasets` valide si `valide` ; sans outils, comme `FakeLlmDeterministe`."""

    def __init__(
        self,
        *,
        non_conformes: int = 0,
        valide: bool = True,
        lever: Callable[[Sequence[Mapping[str, Any]]], BaseException | None] | None = None,
    ) -> None:
        super().__init__(lever)
        self.non_conformes = non_conformes
        self.valide = valide

    def generer(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        tools: Sequence[Mapping[str, Any]] | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Iterator[Any]:
        if not _premier_tour(messages, tools) or (self.valide and not self.non_conformes):
            return super().generer(messages, tools=tools, options=options)
        self.appels.append({"messages": [dict(m) for m in messages], "tools": tools})
        erreur = self.lever(messages) if self.lever is not None else None
        graine = str(len(self.appels))

        def flux() -> Iterator[Any]:
            if erreur is not None:
                raise erreur
            yield Jeton(texte=mots(3, graine))
            for rang in range(self.non_conformes):
                yield AppelNonConforme(
                    nom="search_datasets",
                    arguments_bruts=mots(2, f"bruts-{rang}"),
                    motif=mots(2, f"motif-{rang}"),
                )
            if self.valide:
                yield AppelOutil(
                    id=f"appel-{graine}",
                    nom="search_datasets",
                    arguments={"query": mots(2, f"requete-{graine}")},
                )
            yield Fin(raison="terminee")

        return flux()


class FabriqueProtocoles:
    """Fabrique de Harnais factice : le `LlmPort` dépend du protocole imposé au modèle."""

    def __init__(self, llms: Mapping[str, Any]) -> None:
        self.llms = dict(llms)
        self.appels: list[tuple[Any, str, Path]] = []

    @property
    def protocoles(self) -> list[str]:
        return [modele.config.protocole_outils for modele, _, _ in self.appels]

    @contextmanager
    def __call__(self, modele: Any, variante: str, racine: Path) -> Iterator[Any]:
        self.appels.append((modele, variante, racine))
        yield harnais_factice(self.llms[modele.config.protocole_outils])


def lancer(depot: Path, fabrique: Any, **options: Any) -> Any:
    return sonder(MODELE, racine=depot, fabrique=fabrique, **options)


def lignes(run: Any) -> list[dict[str, Any]]:
    return run.lire_jsonl(FICHIER_SONDE)


def recommandation(run: Any) -> dict[str, Any]:
    return json.loads((run.dossier / FICHIER_RECOMMANDATION).read_text(encoding="utf-8"))


# --- Matrice I/O -------------------------------------------------------------------------------


def test_natif_valide_une_seule_passe(depot_eval: Path, modeles: Path) -> None:
    fabrique = FabriqueProtocoles({NATIF: FakeLlmSonde(), JSON: FakeLlmSonde()})
    rapport = lancer(depot_eval, fabrique)

    assert fabrique.protocoles == [NATIF]
    assert rapport.statut == "complet" and rapport.run.statut_courant() == "complet"
    assert (rapport.protocole_recommande, rapport.valide, rapport.motif) == (NATIF, True, None)
    assert recommandation(rapport.run)["connexions_bloquees"] == []
    contenu = lignes(rapport.run)
    assert [(ligne["protocole"], ligne["item_id"]) for ligne in contenu] == [
        (NATIF, "RD-001"),
        (NATIF, "RD-002"),
    ]
    for ligne in contenu:
        assert ligne["statut"] == "ok" and ligne["valide"] is True
        assert ligne["non_conformes"] == 0 and ligne["appels_valides"] == 1
        assert ligne["appariement"][0] == 0
        assert ligne["appels_produits"][0]["nom"] == "search_datasets"
        assert ligne["appels_produits"][0]["conforme"] is True
        assert set(ligne["appels_produits"][0]["arguments"]) == {"query"}
        Generation.model_validate(ligne["generation"])
    assert [ligne["appels_attendus"] for ligne in contenu] == [2, 3]

    reco = recommandation(rapport.run)
    assert reco["protocole_recommande"] == NATIF and reco["valide"] is True
    assert list(reco["protocoles"]) == [NATIF]
    natif = reco["protocoles"][NATIF]
    assert natif["verdict"] == "valide" and natif["items_valides"] == 2
    assert (natif["appels_valides"], natif["appels_attendus"]) == (2, 5)
    assert natif["taux_appels_valides"] == pytest.approx(0.4)


def test_natif_invalide_puis_json_valide(depot_eval: Path, modeles: Path) -> None:
    fabrique = FabriqueProtocoles(
        {NATIF: FakeLlmSonde(non_conformes=1, valide=False), JSON: FakeLlmSonde()}
    )
    rapport = lancer(depot_eval, fabrique)

    assert fabrique.protocoles == [NATIF, JSON]
    assert rapport.statut == "complet"
    assert (rapport.protocole_recommande, rapport.valide) == (JSON, True)
    contenu = lignes(rapport.run)
    assert [ligne["protocole"] for ligne in contenu] == [NATIF, NATIF, JSON, JSON]
    for ligne in contenu[:2]:
        assert ligne["valide"] is False and ligne["non_conformes"] == 1
        assert ligne["appels_valides"] == 0
        (appel,) = ligne["appels_produits"]
        assert appel["conforme"] is False and appel["nom"] == "search_datasets"
        assert appel["arguments_bruts"] and appel["motif"]
    assert all(ligne["valide"] for ligne in contenu[2:])

    reco = recommandation(rapport.run)
    assert reco["protocole_recommande"] == JSON
    assert reco["protocoles"][NATIF]["verdict"] == "invalide"
    assert reco["protocoles"][NATIF]["non_conformes"] == 2
    assert reco["protocoles"][JSON]["verdict"] == "valide"
    # Le TOML versionné n'est jamais réécrit.
    assert charger_config_modele(SLUG).protocole_outils == NATIF


def test_appel_valide_et_non_conforme_invalide(depot_eval: Path, modeles: Path) -> None:
    fabrique = FabriqueProtocoles(
        {NATIF: FakeLlmSonde(non_conformes=1), JSON: FakeLlmSonde(non_conformes=1)}
    )
    rapport = lancer(depot_eval, fabrique)
    contenu = lignes(rapport.run)
    assert all(ligne["appels_valides"] == 1 and not ligne["valide"] for ligne in contenu)
    assert [a["conforme"] for a in contenu[0]["appels_produits"]] == [False, True]


def test_aucun_protocole_valide_egalite_natif(depot_eval: Path, modeles: Path) -> None:
    llm = FakeLlmSonde(non_conformes=1, valide=False)
    rapport = lancer(depot_eval, FabriqueProtocoles({NATIF: llm, JSON: llm}))

    assert rapport.statut == "complet"
    assert (rapport.protocole_recommande, rapport.valide) == (NATIF, False)
    assert rapport.motif and "aucun protocole valide" in rapport.motif
    reco = recommandation(rapport.run)
    assert reco["valide"] is False and reco["protocole_recommande"] == NATIF
    assert reco["motif"] == rapport.motif
    assert {b["verdict"] for b in reco["protocoles"].values()} == {"invalide"}


def test_aucun_protocole_valide_meilleur_taux(depot_eval: Path, modeles: Path) -> None:
    fabrique = FabriqueProtocoles(
        {NATIF: FakeLlmSonde(valide=False), JSON: FakeLlmSonde(non_conformes=1)}
    )
    rapport = lancer(depot_eval, fabrique)
    assert (rapport.protocole_recommande, rapport.valide) == (JSON, False)
    reco = recommandation(rapport.run)
    assert reco["protocoles"][NATIF]["taux_appels_valides"] == 0
    assert reco["protocoles"][JSON]["taux_appels_valides"] == pytest.approx(0.4)


def test_item_en_erreur(depot_eval: Path, modeles: Path) -> None:
    def lever(_messages: Any) -> BaseException | None:
        return RuntimeError(mots(2, "panne"))

    fabrique = FabriqueProtocoles(
        {NATIF: FakeLlmSonde(non_conformes=1, lever=lever), JSON: FakeLlmSonde()}
    )
    rapport = lancer(depot_eval, fabrique)

    contenu = lignes(rapport.run)
    assert [ligne["statut"] for ligne in contenu] == ["erreur", "erreur", "ok", "ok"]
    assert not any(ligne["valide"] for ligne in contenu[:2])
    assert rapport.statut == "partiel-erreur"
    assert rapport.run.statut_courant() == "partiel-erreur"
    assert (rapport.protocole_recommande, rapport.valide) == (JSON, True)
    assert recommandation(rapport.run)["protocoles"][NATIF]["erreurs"] == 2


def test_interruption_hors_item(depot_eval: Path, modeles: Path) -> None:
    class Arret(Exception):
        pass

    def rapporter(ligne: Any, rang: int, total: int) -> None:
        raise Arret(mots(2, "arret"))

    fabrique = FabriqueProtocoles({NATIF: FakeLlmSonde(), JSON: FakeLlmSonde()})
    with pytest.raises(Arret):
        lancer(depot_eval, fabrique, rapporter=rapporter)
    (dossier,) = (depot_eval / "runs" / TYPE_RUN).iterdir()
    etats = (dossier / "etat.jsonl").read_text(encoding="utf-8").splitlines()
    assert json.loads(etats[-1])["statut"] == "interrompu"
    assert not (dossier / FICHIER_RECOMMANDATION).exists()


# --- Run ---------------------------------------------------------------------------------------


def test_run_json(depot_eval: Path, modeles: Path) -> None:
    fabrique = FabriqueProtocoles({NATIF: FakeLlmSonde(), JSON: FakeLlmSonde()})
    rapport = lancer(depot_eval, fabrique)
    brut = json.loads((rapport.run.dossier / "run.json").read_text(encoding="utf-8"))

    assert rapport.run.dossier.parent == depot_eval / "runs" / TYPE_RUN
    assert brut["type"] == TYPE_RUN and brut["modele_ref"] == MODELE
    assert brut["quantification"] == "q4_k_m" and brut["jeu_version"] == "calibrage"
    assert brut["variante_llamacpp"] == "cpu" and brut["llamacpp_tag"] == "b11429"
    assert brut["config"]["items"] == list(ITEMS_SONDE)
    assert brut["config"]["phase"] == "sonde-outils"
    assert brut["config"]["profil_reseau"] == "aucun"
    assert brut["config"]["options_llm"]["temperature"] == 0.0
    assert "items_jeu" in brut["entrees"] and "modele" in brut["entrees"]
    assert fabrique.appels[0][1] == "cpu"


def test_evaluer_lit_la_trace(depot_eval: Path) -> None:
    item = lire_jeu("calibrage", depot_eval).item("RD-001")
    bruts = mots(2, "bruts")
    generation = Generation(
        item_id="RD-001",
        tache="RD",
        statut="ok",
        sortie_canonique={
            "texte": "",
            "appels_outils": [{"nom": "get_dataset_info", "arguments": {"dataset_id": "x"}}],
        },
        trace=[
            {"type": "appel-non-conforme", "nom": None, "arguments_bruts": bruts, "motif": "m"},
            {
                "type": "appel-outil",
                "id": "a",
                "nom": "get_dataset_info",
                "arguments": {"dataset_id": "x"},
            },
            {"type": "fin", "raison": "terminee"},
        ],
        duree_ms=5,
    )
    ligne = evaluer(item, generation, JSON)
    assert ligne["protocole"] == JSON and ligne["duree_ms"] == 5
    assert ligne["appels_produits"] == [
        {"nom": None, "arguments_bruts": bruts, "motif": "m", "conforme": False},
        {"nom": "get_dataset_info", "arguments": {"dataset_id": "x"}, "conforme": True},
    ]
    assert (ligne["appels_attendus"], ligne["appels_valides"]) == (2, 1)
    assert ligne["appariement"] == [None, 0]
    assert ligne["non_conformes"] == 1 and ligne["valide"] is False


# --- Usage et CLI ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("options", "attendu"),
    [
        ({"items": ["ZZ-999"]}, "ZZ-999"),
        ({"items": ["Q-001"]}, "Q-001"),
        ({"variante": "tpu"}, "variante"),
    ],
)
def test_usage_sans_run(
    options: dict[str, Any], attendu: str, depot_eval: Path, modeles: Path
) -> None:
    fabrique = FabriqueProtocoles({})
    with pytest.raises(ValueError, match=attendu):
        lancer(depot_eval, fabrique, **options)
    assert fabrique.appels == []
    assert not (depot_eval / "runs").exists()


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["--modele", "pas-un-ref"],
        ["--modele", "ft:pas-un-run-id"],
        ["--modele", MODELE, "--items", "ZZ-001"],
        ["--modele", MODELE, "--items", "Q-001,RD-001"],
    ],
)
def test_cli_usage(
    arguments: list[str],
    depot_eval: Path,
    modeles: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fabrique = FabriqueProtocoles({})
    monkeypatch.setattr(assemblage, "ouvrir_harnais", fabrique)
    commande = ["eval", "sonde-outils", *arguments, "--racine", str(depot_eval)]
    assert main(commande) == CodeSortie.USAGE
    erreur = capsys.readouterr().err
    assert erreur.startswith("slmsp : eval sonde-outils : ") and "Traceback" not in erreur
    assert fabrique.appels == []
    assert not (depot_eval / "runs").exists()


@pytest.mark.parametrize(
    ("llms", "code", "recommande"),
    [
        ({NATIF: FakeLlmSonde(), JSON: FakeLlmSonde()}, CodeSortie.SUCCES, "natif (valide)"),
        (
            {NATIF: FakeLlmSonde(non_conformes=1, valide=False), JSON: FakeLlmSonde()},
            CodeSortie.SUCCES,
            "json-generique (valide)",
        ),
        (
            {NATIF: FakeLlmSonde(valide=False), JSON: FakeLlmSonde(valide=False)},
            CodeSortie.ERREUR,
            "natif (aucun protocole valide)",
        ),
    ],
)
def test_cli(
    llms: dict[str, Any],
    code: int,
    recommande: str,
    depot_eval: Path,
    modeles: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(assemblage, "ouvrir_harnais", FabriqueProtocoles(llms))
    commande = ["eval", "sonde-outils", "--modele", MODELE, "--racine", str(depot_eval)]
    assert main(commande) == code
    sortie = capsys.readouterr().out
    assert "[natif 1/2] RD-001" in sortie and "[natif 2/2] RD-002" in sortie
    assert "Protocole  " in sortie and "Verdict" in sortie
    assert f"Protocole recommandé : {recommande}" in sortie
    assert "Run : " in sortie and str(depot_eval / "runs" / TYPE_RUN) in sortie
    assert "Statut du run : complet" in sortie


def test_cli_item_en_erreur_code_1(
    depot_eval: Path,
    modeles: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    llm = FakeLlmSonde(lever=lambda _m: RuntimeError(mots(2, "panne")), non_conformes=1)
    monkeypatch.setattr(
        assemblage, "ouvrir_harnais", FabriqueProtocoles({NATIF: llm, JSON: FakeLlmSonde()})
    )
    commande = ["eval", "sonde-outils", "--modele", MODELE, "--racine", str(depot_eval)]
    assert main(commande) == CodeSortie.ERREUR
    sortie = capsys.readouterr().out
    assert "Statut du run : partiel-erreur" in sortie
    assert "Protocole recommandé : json-generique (valide)" in sortie


# --- Réel --------------------------------------------------------------------------------------


def _module_reel() -> ModuleType:
    """`test_generation_reel` (prérequis et racine de l'Index), chargé sous un autre nom."""
    nom = "evaluation_generation_reel"
    spec = importlib.util.spec_from_file_location(
        nom, Path(__file__).with_name("test_generation_reel.py")
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.lent
@pytest.mark.integration
def test_reel_sonde_granite_rd001(depot_eval: Path) -> None:
    index = _module_reel().prerequis()
    rapport = sonder(
        MODELE,
        items=["RD-001"],
        racine=depot_eval,
        fabrique=functools.partial(ouvrir_harnais, racine_index=index),
        rapporter=lambda ligne, rang, total: print(
            f"[{ligne['protocole']} {rang}/{total}] {ligne['item_id']} {ligne['statut']} "
            f"valide={ligne['valide']} appels={ligne['appels_produits']}"
        ),
    )
    print(f"\nrun : {rapport.run.dossier} ; recommandé {rapport.protocole_recommande}")
    assert rapport.statut in ("complet", "partiel-erreur")
    assert rapport.connexions_bloquees == []
    contenu = lignes(rapport.run)
    assert contenu[0]["protocole"] == NATIF and contenu[0]["item_id"] == "RD-001"
    assert rapport.protocole_recommande in (NATIF, JSON)
    assert (rapport.run.dossier / FICHIER_RECOMMANDATION).is_file()
