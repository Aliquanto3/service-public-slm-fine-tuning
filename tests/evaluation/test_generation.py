"""Phase génération du banc, sans réseau (story 5.3).

Harnais factice (`FakeLlmDeterministe`, `FakeEmbedder`, `FakeVectorStore`) et Bac à sable
réel sur une copie du jeu v1.0 gelé dans `tmp_path`. Aucun `llama-server` n'est lancé.
"""

from __future__ import annotations

import json
import socket
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from evaluation_factices import (
    ITEMS_8,
    SHA_TEMPLATE,
    Fabrique,
    FakeLlmDeterministe,
    harnais_factice,
)
from harness_factices import mots

from slmsp.cli import main
from slmsp.core.artefacts import nouveau_run, ouvrir_run
from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import (
    CodeSortie,
    ConfigurationInvalide,
    HoteBloque,
    ManifesteInvalide,
    RessourceOccupee,
    SchemaOutilModifie,
    SlmspError,
)
from slmsp.core.evenements import Erreur, Fin, Jeton
from slmsp.core.items import lire_jeu
from slmsp.core.schemas.generation import Generation
from slmsp.core.var import verrou_gpu
from slmsp.evaluation import assemblage
from slmsp.evaluation.assemblage import MODES_RD, PROFIL_RESEAU, sans_reseau
from slmsp.evaluation.config import ConfigGeneration, charger_evaluation
from slmsp.evaluation.generation import (
    CODE_ERREUR_EVALUATION,
    FICHIER_GENERATIONS,
    TYPE_RUN,
    generer_item,
    lancer_generation,
    options_llm,
    reprendre_generation,
    tronquee,
)
from slmsp.harness.prompts import construire_messages
from slmsp.mcp.bac_a_sable import BacASable
from slmsp.mcp.outils import charger_outils

MODELE = "base:granite-4.0-1b"
CIBLE_DISTANTE = ("192.0.2.1", 443)
OPTIONS_5_3 = {"temperature": 0.0, "seed": 42, "max_tokens": 1024}
"""Décodage des anciennes constantes de la story 5.3 : valeurs par défaut inchangées (W2)."""


def lancer(depot: Path, fabrique: Any, items=ITEMS_8, **options: Any):
    return lancer_generation(
        MODELE, "q4_k_m", "v1.0", items=items, racine=depot, fabrique=fabrique, **options
    )


def lignes(run: Any) -> list[Generation]:
    return [Generation.model_validate(ligne) for ligne in run.lire_jsonl(FICHIER_GENERATIONS)]


def par_id(run: Any) -> dict[str, Generation]:
    return {g.item_id: g for g in lignes(run)}


def etats(run: Any) -> list[tuple[str, str | None]]:
    contenu = (run.dossier / "etat.jsonl").read_text(encoding="utf-8")
    return [(e["statut"], e.get("motif")) for e in map(json.loads, contenu.splitlines())]


# --- Nominal -----------------------------------------------------------------------------------


def test_nominal_huit_items(depot_eval: Path, modeles: Path, fabrique: Fabrique) -> None:
    rapport = lancer(depot_eval, fabrique)

    assert (rapport.ok, rapport.erreur, rapport.sautes, rapport.statut) == (8, 0, 0, "complet")
    run = ouvrir_run(rapport.run.manifeste.run_id, racine=depot_eval)
    assert run.dossier.parent == depot_eval / "runs" / TYPE_RUN
    assert run.statut_courant() == "complet"
    generations = lignes(run)
    assert [g.item_id for g in generations] == [
        item.id for item in lire_jeu("v1.0", depot_eval).items if item.id in ITEMS_8
    ]
    assert all(g.statut == "ok" for g in generations)
    assert {g.tache for g in generations} == {"Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR"}
    assert len(rapport.durees_ms) == 8 and rapport.duree_moyenne_ms is not None
    ((modele, variante, racine),) = fabrique.appels
    assert (modele.ref, modele.slug, variante, racine) == (
        MODELE,
        "granite-4.0-1b",
        "cpu",
        depot_eval.resolve(),
    )


def test_run_json(depot_eval: Path, modeles: Path, fabrique: Fabrique) -> None:
    run = lancer(depot_eval, fabrique).run
    brut = json.loads((run.dossier / "run.json").read_text(encoding="utf-8"))

    assert brut["type"] == TYPE_RUN
    assert brut["modele_ref"] == MODELE
    assert brut["quantification"] == "q4_k_m"
    assert brut["variante_llamacpp"] == "cpu"
    assert brut["llamacpp_tag"] == "b11429"
    assert brut["chat_template_sha256"] == SHA_TEMPLATE
    assert brut["jeu_version"] == "v1.0"
    assert brut["index_version"] == "factice"
    assert brut["graine"] == 42
    config = brut["config"]
    assert config["options_llm"] == OPTIONS_5_3
    assert config["items"] == [g.item_id for g in lignes(run)]
    assert config["serveur"] == {"generation": {"factice": True}, "embedding": {"factice": True}}
    assert config["chat_template_force"] is False
    assert config["profil_reseau"] == PROFIL_RESEAU == "aucun"
    assert config["version_harnais"] == 2
    assert set(brut["entrees"]) == {"manifeste_jeu", "outils_mcp", "taches", "harnais", "modele"}


def test_sortie_canonique_et_trace(depot_eval: Path, modeles: Path) -> None:
    llm = FakeLlmDeterministe()
    run = lancer(depot_eval, Fabrique(llm)).run
    generations = par_id(run)

    for generation in generations.values():
        sortie = generation.sortie_canonique.model_dump(mode="json")
        assert set(sortie) == {"texte", "appels_outils", "sources"}
        assert "duree" not in json.dumps(sortie) and "delai" not in json.dumps(sortie)
        assert generation.sortie_canonique.texte.strip()
        types = [e["type"] for e in generation.trace]
        assert types[-1] == "fin"
        assert all(
            not (a == "jeton" and b == "jeton") for a, b in zip(types, types[1:], strict=False)
        ), "jetons consécutifs non fusionnés"
        texte_trace = "".join(e["texte"] for e in generation.trace if e["type"] == "jeton")
        assert texte_trace == generation.sortie_canonique.texte

    rd = generations["RD-001"]
    (appel,) = rd.sortie_canonique.appels_outils
    assert appel.nom == "search_datasets" and set(appel.arguments) == {"query"}
    types = [e["type"] for e in rd.trace]
    assert "appel-outil" in types and "resultat-outil" in types
    # Requête aléatoire : « appel non prévu » signalé par le Bac à sable, à sa place.
    assert types.index("avertissement") < types.index("resultat-outil")
    assert rd.trace[types.index("avertissement")]["code"] == "appel-non-prevu"

    # Seules les options de décodage vont au LlmPort (ni parametres, ni mode, ni entree).
    assert llm.appels and all(a["options"] == OPTIONS_5_3 for a in llm.appels)
    assert all(g.tronquee is False for g in generations.values())


def test_entree_objet_rendue_dans_le_message_user(depot_eval: Path, modeles: Path) -> None:
    from slmsp.harness.prompts import entree_de_requete
    from slmsp.harness.taches import charger_taches

    llm = FakeLlmDeterministe()
    lancer(depot_eval, Fabrique(llm), items=["CT-001"])
    item = lire_jeu("v1.0", depot_eval).item("CT-001")
    from slmsp.core.items import vers_requete

    attendus = construire_messages(
        charger_taches().tache("CT"), entree_de_requete(vers_requete(item))
    )
    (appel,) = llm.appels
    assert appel["messages"] == attendus


# --- Manifeste ---------------------------------------------------------------------------------


def _alterer(depot: Path) -> None:
    chemin = depot / "eval" / "jeu" / "v1.0" / "items.jsonl"
    donnees = bytearray(chemin.read_bytes())
    donnees[10] = ord("#") if donnees[10] != ord("#") else ord("@")
    chemin.write_bytes(bytes(donnees))


def test_manifeste_altere(depot_eval: Path, modeles: Path, fabrique: Fabrique) -> None:
    _alterer(depot_eval)
    with pytest.raises(ManifesteInvalide):
        lancer(depot_eval, fabrique)
    assert fabrique.appels == []
    assert not (depot_eval / "runs").exists()


def test_manifeste_verifie_avant_le_modele(
    depot_eval: Path, fabrique: Fabrique, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Le manifeste passe avant la résolution du modèle (ici impossible : aucun GGUF)."""
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(depot_eval / "absent"))
    _alterer(depot_eval)
    with pytest.raises(ManifesteInvalide):
        lancer(depot_eval, fabrique)


def test_cli_manifeste_altere_code_4(
    depot_eval: Path, modeles: Path, fabrique: Fabrique, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(assemblage, "ouvrir_harnais", fabrique)
    _alterer(depot_eval)
    code = main(
        ["eval", "run", "--modele", MODELE, "--quantification", "q4_k_m", "--jeu", "v1.0",
         "--phase", "generation", "--racine", str(depot_eval)]
    )  # fmt: skip
    assert code == CodeSortie.MANIFESTE_INVALIDE
    assert fabrique.appels == [] and not (depot_eval / "runs").exists()


def test_calibrage_sans_manifeste(depot_eval: Path, modeles: Path, fabrique: Fabrique) -> None:
    rapport = lancer_generation(
        MODELE,
        "q4_k_m",
        "calibrage",
        items=["Q-001", "RD-001"],
        racine=depot_eval,
        fabrique=fabrique,
    )
    assert rapport.statut == "complet"
    assert rapport.run.manifeste.jeu_version == "calibrage"
    assert "items_jeu" in rapport.run.manifeste.entrees
    rd = par_id(rapport.run)["RD-001"]
    assert rd.tache == "RD" and any(e["type"] == "resultat-outil" for e in rd.trace)


# --- Erreurs d'item ----------------------------------------------------------------------------


def test_item_en_echec(depot_eval: Path, modeles: Path) -> None:
    entree = lire_jeu("v1.0", depot_eval).item("NR-001").entree

    def lever(messages: Any) -> BaseException | None:
        if any(entree in str(m.get("content")) for m in messages):
            return RuntimeError(mots(3, "panne"))
        return None

    rapport = lancer(depot_eval, Fabrique(FakeLlmDeterministe(lever)))
    generations = par_id(rapport.run)

    assert (rapport.ok, rapport.erreur, rapport.statut) == (7, 1, "partiel-erreur")
    assert rapport.run.statut_courant() == "partiel-erreur"
    nr = generations["NR-001"]
    assert nr.statut == "erreur" and nr.trace[-1]["type"] == "erreur"
    assert nr.tronquee is None  # flux coupé avant tout `Fin` : troncature inconnue
    assert all(g.statut == "ok" for i, g in generations.items() if i != "NR-001")


def test_erreur_avant_flux_entree_invalide(depot_eval: Path) -> None:
    jeu = lire_jeu("v1.0", depot_eval)
    item = jeu.item("NR-001").model_copy(update={"entree": "   "})
    generation = generer_item(harnais_factice(), jeu, item)
    assert generation.statut == "erreur"
    assert generation.trace[-1]["type"] == "erreur"
    assert generation.trace[-1]["code"] == CODE_ERREUR_EVALUATION
    assert "EntreeInvalide" in generation.trace[-1]["message"]
    assert generation.sortie_canonique.texte == ""


def test_erreur_avant_flux_bac_a_sable(
    depot_eval: Path, modeles: Path, fabrique: Fabrique, monkeypatch: pytest.MonkeyPatch
) -> None:
    def refuser(*_args: Any, **_kwargs: Any) -> Any:
        raise SchemaOutilModifie("cassette refusée, empreinte des outils différente")

    monkeypatch.setattr(assemblage, "BacASable", refuser)
    rapport = lancer(depot_eval, fabrique)
    generations = par_id(rapport.run)

    assert rapport.statut == "partiel-erreur" and rapport.erreur == 1
    rd = generations["RD-001"]
    assert rd.statut == "erreur"
    assert rd.trace == [
        {
            "type": "erreur",
            "code": CODE_ERREUR_EVALUATION,
            "message": "SchemaOutilModifie : cassette refusée, empreinte des outils différente",
        }
    ]
    assert all(g.statut == "ok" for i, g in generations.items() if i != "RD-001")


# --- Reprise -----------------------------------------------------------------------------------


class Interruption(Exception):
    pass


def _interrompre_apres(n: int):
    def rapporter(generation: Generation, rang: int, total: int) -> None:
        if rang == n:
            raise Interruption(mots(2, "arret"))

    return rapporter


def _run_interrompu(depot: Path, fabrique: Fabrique) -> str:
    with pytest.raises(Interruption):
        lancer(depot, fabrique, rapporter=_interrompre_apres(3))
    (dossier,) = (depot / "runs" / TYPE_RUN).iterdir()
    return dossier.name


def test_reprise(depot_eval: Path, modeles: Path, fabrique: Fabrique) -> None:
    run_id = _run_interrompu(depot_eval, fabrique)
    run = ouvrir_run(run_id, racine=depot_eval)
    assert run.statut_courant() == "interrompu"
    assert len(lignes(run)) == 3

    vus: list[str] = []
    rapport = reprendre_generation(
        run_id,
        racine=depot_eval,
        fabrique=fabrique,
        rapporter=lambda g, rang, total: vus.append(g.item_id),
    )

    assert (rapport.ok, rapport.sautes, rapport.statut) == (5, 3, "complet")
    assert rapport.run.dossier == run.dossier
    generations = lignes(run)
    assert len(generations) == 8 and len({g.item_id for g in generations}) == 8
    assert vus == [g.item_id for g in generations[3:]]
    assert [s for s, _ in etats(run)] == ["en_cours", "interrompu", "en_cours", "complet"]
    assert etats(run)[2] == ("en_cours", "reprise")

    with pytest.raises(SlmspError, match="déjà complet"):
        reprendre_generation(run_id, racine=depot_eval, fabrique=fabrique)


def test_reprise_garde_les_erreurs_anterieures(depot_eval: Path, modeles: Path) -> None:
    llm = FakeLlmDeterministe()
    llm.lever = lambda messages: RuntimeError(mots(3, "panne")) if len(llm.appels) == 1 else None
    fabrique = Fabrique(llm)  # seul le tout premier appel échoue : premier item en erreur
    run_id = _run_interrompu(depot_eval, fabrique)
    run = ouvrir_run(run_id, racine=depot_eval)
    assert [g.statut for g in lignes(run)] == ["erreur", "ok", "ok"]

    rapport = reprendre_generation(run_id, racine=depot_eval, fabrique=fabrique)
    assert (rapport.ok, rapport.erreur, rapport.sautes) == (5, 0, 3)  # session sans erreur
    assert rapport.statut == "partiel-erreur" and run.statut_courant() == "partiel-erreur"


def test_reprise_refusee(depot_eval: Path, modeles: Path, fabrique: Fabrique) -> None:
    run_id = _run_interrompu(depot_eval, fabrique)
    with pytest.raises(ManifesteInvalide, match="modele_ref"):
        reprendre_generation(
            run_id, racine=depot_eval, fabrique=fabrique, modele_ref="base:qwen-4b"
        )
    with pytest.raises(ManifesteInvalide, match="chat template"):
        reprendre_generation(run_id, racine=depot_eval, fabrique=Fabrique(sha_template="cd" * 32))

    @contextmanager
    def autre_index(modele: Any, variante: str, racine: Path) -> Iterator[Any]:
        with fabrique(modele, variante, racine) as harnais:
            harnais.index_version = "autre-index"
            yield harnais

    with pytest.raises(ManifesteInvalide, match="index_version"):
        reprendre_generation(run_id, racine=depot_eval, fabrique=autre_index)
    autre = nouveau_run("export", "granite-4.0-1b", {}, racine=depot_eval)
    with pytest.raises(ManifesteInvalide, match="type"):
        reprendre_generation(autre.manifeste.run_id, racine=depot_eval, fabrique=fabrique)
    # Aucune des reprises refusées n'a rien écrit.
    run = ouvrir_run(run_id, racine=depot_eval)
    assert len(lignes(run)) == 3
    assert [s for s, _ in etats(run)] == ["en_cours", "interrompu"]


def test_reprise_manifeste_altere(depot_eval: Path, modeles: Path, fabrique: Fabrique) -> None:
    run_id = _run_interrompu(depot_eval, fabrique)
    _alterer(depot_eval)
    with pytest.raises(ManifesteInvalide):
        reprendre_generation(run_id, racine=depot_eval, fabrique=fabrique)
    assert len(fabrique.appels) == 1


def test_cli_reprise(
    depot_eval: Path,
    modeles: Path,
    fabrique: Fabrique,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_id = _run_interrompu(depot_eval, fabrique)
    monkeypatch.setattr(assemblage, "ouvrir_harnais", fabrique)
    base = ["eval", "run", "--phase", "generation", "--reprendre", run_id]
    racine = ["--racine", str(depot_eval)]

    assert main([*base, "--modele", "base:qwen-4b", *racine]) == CodeSortie.MANIFESTE_INVALIDE
    assert main([*base, "--items", "Q-001", *racine]) == CodeSortie.USAGE
    capsys.readouterr()
    assert main([*base, "--modele", MODELE, "--jeu", "v1.0", *racine]) == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert "[4/8]" in sortie and "[3/8]" not in sortie
    assert "Statut du run : complet" in sortie
    assert main([*base, *racine]) == CodeSortie.ERREUR  # déjà complet


# --- Sans réseau -------------------------------------------------------------------------------


def test_sans_reseau_bloque_et_restaure() -> None:
    avant = (socket.socket.connect, socket.socket.connect_ex, socket.getaddrinfo)
    with sans_reseau() as bloquees:
        with pytest.raises(HoteBloque, match="profil réseau aucun"):
            socket.create_connection(CIBLE_DISTANTE, timeout=1)
        with pytest.raises(HoteBloque, match="profil réseau aucun"):
            socket.getaddrinfo("example.org", 443)
        prise = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            with pytest.raises(HoteBloque):
                prise.connect(CIBLE_DISTANTE)
            with pytest.raises(HoteBloque):
                prise.connect_ex(CIBLE_DISTANTE)
        finally:
            prise.close()
        assert socket.getaddrinfo("127.0.0.1", 80)
        assert socket.getaddrinfo("localhost", 80)
    assert len(bloquees) == 4
    assert (socket.socket.connect, socket.socket.connect_ex, socket.getaddrinfo) == avant


def test_sans_reseau_restaure_apres_exception() -> None:
    avant = socket.socket.connect
    with pytest.raises(RuntimeError), sans_reseau():
        raise RuntimeError("x")
    assert socket.socket.connect is avant


class _OutilsReseau:
    """`ToolPort` qui tente une connexion distante à chaque appel."""

    def __init__(self, *_args: Any, **_kwargs: Any) -> None:
        pass

    def lister_outils(self) -> list[dict[str, Any]]:
        return charger_outils()

    def appeler(self, nom: str, arguments: Mapping[str, Any], **_kwargs: Any) -> Any:
        with socket.create_connection(CIBLE_DISTANTE, timeout=1):
            raise AssertionError("connexion établie")


def _espionner_sockets(monkeypatch: pytest.MonkeyPatch) -> list[Any]:
    vus: list[Any] = []
    connect, connect_ex, getaddrinfo = (
        socket.socket.connect,
        socket.socket.connect_ex,
        socket.getaddrinfo,
    )

    def espion_connect(self, adresse, *args, **kwargs):
        vus.append(adresse)
        return connect(self, adresse, *args, **kwargs)

    def espion_connect_ex(self, adresse, *args, **kwargs):
        vus.append(adresse)
        return connect_ex(self, adresse, *args, **kwargs)

    def espion_getaddrinfo(hote, *args, **kwargs):
        vus.append(hote)
        return getaddrinfo(hote, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", espion_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", espion_connect_ex)
    monkeypatch.setattr(socket, "getaddrinfo", espion_getaddrinfo)
    return vus


def test_outil_qui_tente_le_reseau_replie(
    depot_eval: Path, modeles: Path, fabrique: Fabrique, monkeypatch: pytest.MonkeyPatch
) -> None:
    vus = _espionner_sockets(monkeypatch)
    monkeypatch.setattr(assemblage, "BacASable", _OutilsReseau)
    rapport = lancer(depot_eval, fabrique, items=["RD-001"])

    (rd,) = lignes(rapport.run)
    types = [e["type"] for e in rd.trace]
    assert rd.statut == "ok" and "repli" in types  # panne MCP : repli sur l'Index
    assert rapport.connexions_bloquees and "192.0.2.1" in rapport.connexions_bloquees[0]
    assert all(assemblage.hote_local(v) or assemblage.adresse_locale(v) for v in vus)


def test_run_complet_sans_connexion_sortante(
    depot_eval: Path, modeles: Path, fabrique: Fabrique, monkeypatch: pytest.MonkeyPatch
) -> None:
    """FakeLlm et Bac à sable réel : zéro tentative de connexion sortante."""
    vus = _espionner_sockets(monkeypatch)
    rapport = lancer(depot_eval, fabrique, items=[*ITEMS_8, "RD-005"])
    assert rapport.statut == "complet"
    assert rapport.connexions_bloquees == []
    assert all(assemblage.hote_local(v) or assemblage.adresse_locale(v) for v in vus)


# --- Modes RD ----------------------------------------------------------------------------------


def test_modes_rd(depot_eval: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert MODES_RD == {
        "connecte": "connecte",
        "repli": "connecte",
        "hors-ligne": "hors-ligne-force",
    }
    appels: list[str] = []
    appeler = BacASable.appeler

    def espion(self, nom, arguments, **kwargs):
        appels.append(nom)
        return appeler(self, nom, arguments, **kwargs)

    monkeypatch.setattr(BacASable, "appeler", espion)
    jeu = lire_jeu("v1.0", depot_eval)

    llm = FakeLlmDeterministe()
    item = jeu.item("RD-001").model_copy(update={"mode": "hors-ligne"})
    hors_ligne = generer_item(harnais_factice(llm), jeu, item)
    assert hors_ligne.statut == "ok" and appels == []
    assert all(a["tools"] is None for a in llm.appels)
    codes = [e.get("code") for e in hors_ligne.trace if e["type"] == "avertissement"]
    assert "valeurs-mode-connecte" in codes
    assert hors_ligne.sortie_canonique.appels_outils == []

    connecte = generer_item(harnais_factice(), jeu, jeu.item("RD-001"))
    assert appels == ["search_datasets"]
    assert not any(e["type"] == "repli" for e in connecte.trace)

    repli = generer_item(harnais_factice(), jeu, jeu.item("RD-005"))
    assert jeu.item("RD-005").mode == "repli"
    assert any(e["type"] == "repli" for e in repli.trace)


# --- GPU ---------------------------------------------------------------------------------------


class _LlmVerrou(FakeLlmDeterministe):
    """Vérifie, à chaque génération, que le verrou GPU est détenu par le run."""

    def __init__(self) -> None:
        super().__init__()
        self.verrou_detenu: list[bool] = []

    def generer(self, messages, *, tools=None, options=None):
        try:
            with verrou_gpu():
                self.verrou_detenu.append(False)
        except RessourceOccupee:
            self.verrou_detenu.append(True)
        return super().generer(messages, tools=tools, options=options)


def test_cuda_prend_le_verrou_gpu(depot_eval: Path, modeles: Path) -> None:
    llm = _LlmVerrou()
    fabrique = Fabrique(llm)
    rapport = lancer(depot_eval, fabrique, items=["Q-001", "NR-001"], variante="cuda")

    assert rapport.statut == "complet"
    assert llm.verrou_detenu and all(llm.verrou_detenu)
    assert rapport.run.manifeste.variante_llamacpp == "cuda"
    assert fabrique.appels[0][1] == "cuda"
    with verrou_gpu():  # rendu à la fin du run
        pass


def test_cpu_ne_prend_pas_le_verrou(depot_eval: Path, modeles: Path) -> None:
    llm = _LlmVerrou()
    lancer(depot_eval, Fabrique(llm), items=["Q-001"])
    assert llm.verrou_detenu == [False]


# --- Reproductibilité --------------------------------------------------------------------------


def test_deux_runs_identiques(depot_eval: Path, modeles: Path) -> None:
    items = [*ITEMS_8, "RD-005"]
    premier = par_id(lancer(depot_eval, Fabrique(), items=items).run)
    second = par_id(lancer(depot_eval, Fabrique(), items=items).run)
    assert premier.keys() == second.keys() == set(items)
    for identifiant in items:
        assert json_canonique(
            premier[identifiant].sortie_canonique.model_dump(mode="json")
        ) == json_canonique(second[identifiant].sortie_canonique.model_dump(mode="json"))


# --- Usage et CLI ------------------------------------------------------------------------------


def test_items_inconnus(depot_eval: Path, modeles: Path, fabrique: Fabrique) -> None:
    with pytest.raises(ValueError, match="ZZ-999"):
        lancer(depot_eval, fabrique, items=["Q-001", "ZZ-999"])
    with pytest.raises(ValueError, match="variante"):
        lancer(depot_eval, fabrique, variante="tpu")
    assert fabrique.appels == []


@pytest.mark.parametrize("phase", [None, "notation", "toutes"])
def test_cli_phase_notation_ou_toutes(
    phase: str | None,
    depot_eval: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Story 5.6 : `notation` exige `--depuis` ; `toutes` ouvre les juges avant la génération."""
    from slmsp.core.erreurs import SecretManquant
    from slmsp.evaluation import notation

    def refuser(*_args: Any, **_options: Any) -> Any:
        raise SecretManquant("clé d'API absente")

    monkeypatch.setattr(notation, "ouvrir_juges", refuser)
    arguments = ["eval", "run", "--modele", MODELE, "--quantification", "q4_k_m", "--jeu", "v1.0"]
    if phase is not None:
        arguments += ["--phase", phase]
    code = main([*arguments, "--racine", str(depot_eval)])
    if phase == "notation":
        assert code == CodeSortie.USAGE
        assert "--depuis RUN_ID requis" in capsys.readouterr().err
    else:
        assert code == CodeSortie.ERREUR
        assert "clé d'API absente" in capsys.readouterr().err
    assert not (depot_eval / "runs").exists()


@pytest.mark.parametrize(
    "arguments",
    [
        ["--quantification", "q4_k_m", "--jeu", "v1.0"],
        ["--modele", MODELE, "--quantification", "q4_k_m", "--jeu", "v1.0", "--items", "ZZ-001"],
        ["--modele", "pas-un-ref", "--quantification", "q4_k_m", "--jeu", "v1.0"],
    ],
)
def test_cli_usage(
    arguments: list[str],
    depot_eval: Path,
    modeles: Path,
    fabrique: Fabrique,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(assemblage, "ouvrir_harnais", fabrique)
    commande = ["eval", "run", "--phase", "generation", *arguments, "--racine", str(depot_eval)]
    assert main(commande) == CodeSortie.USAGE
    assert "Traceback" not in capsys.readouterr().err
    assert fabrique.appels == []


def test_cli_nominal_et_partiel(
    depot_eval: Path,
    modeles: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    commande = [
        "eval", "run", "--modele", MODELE, "--quantification", "q4_k_m", "--jeu", "v1.0",
        "--phase", "generation", "--items", ",".join(ITEMS_8), "--racine", str(depot_eval),
    ]  # fmt: skip
    monkeypatch.setattr(assemblage, "ouvrir_harnais", Fabrique())
    assert main(commande) == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert "[1/8]" in sortie and "[8/8]" in sortie
    assert "Run : " in sortie and str(depot_eval / "runs" / TYPE_RUN) in sortie
    assert (
        "Statut du run : complet" in sortie
        and "Durée moyenne par item (cette session) : " in sortie
    )

    monkeypatch.setattr(
        assemblage, "ouvrir_harnais", Fabrique(FakeLlmDeterministe(lambda m: RuntimeError("x")))
    )
    assert main(commande) == CodeSortie.ERREUR
    assert "Statut du run : partiel-erreur" in capsys.readouterr().out


# --- Schéma ------------------------------------------------------------------------------------


def test_schema_generation() -> None:
    valide = {
        "item_id": "Q-001",
        "tache": "Q",
        "statut": "ok",
        "sortie_canonique": {"texte": "a", "appels_outils": [], "sources": []},
        "trace": [{"type": "jeton", "texte": "a"}, {"type": "fin", "raison": "terminee"}],
        "duree_ms": 0,
    }
    assert Generation.model_validate(valide).schema_version == 1
    # Ligne écrite avant W2 (sans `tronquee`) : toujours lisible, troncature inconnue.
    assert Generation.model_validate(valide).tronquee is None
    assert Generation.model_validate({**valide, "tronquee": True}).tronquee is True
    for modif in (
        {"trace": [{"type": "inconnu"}]},
        {"duree_ms": -1},
        {"statut": "partiel"},
        {"tache": "R"},
        {"sortie_canonique": {"texte": "a", "duree_ms": 3}},
    ):
        with pytest.raises(ValueError):
            Generation.model_validate({**valide, **modif})


# --- Réglages de décodage et troncature (report W2) ---------------------------------------------


def _toml_evaluation(dossier: Path, generation: str | None) -> Path:
    """`evaluation.toml` minimal, avec la section `[generation]` donnée (ou sans elle)."""
    texte = (
        "schema_version = 1\n[co]\n[re.longueurs]\ncourte = 80\nmoyenne = 200\ndetaillee = 400\n"
        "[seuils]\nkappa_fragile = 0.6\ngain_km_min = 10.0\nplafond_lc = 50.0\n"
    )
    if generation is not None:
        texte += "[generation]\n" + generation + "\n"
    chemin = dossier / "evaluation.toml"
    chemin.write_text(texte, encoding="utf-8")
    return chemin


def _avec_generation(**reglages: Any) -> Any:
    return charger_evaluation().model_copy(update={"generation": ConfigGeneration(**reglages)})


def test_reglages_par_defaut_inchanges(tmp_path: Path) -> None:
    assert charger_evaluation().generation == ConfigGeneration()
    assert options_llm() == ConfigGeneration().options_llm() == OPTIONS_5_3
    # Section absente : mêmes défauts ; clé absente : défaut de la clé.
    assert charger_evaluation(_toml_evaluation(tmp_path, None)).generation == ConfigGeneration()
    partiel = charger_evaluation(_toml_evaluation(tmp_path, "max_tokens = 2048"))
    assert options_llm(partiel) == {**OPTIONS_5_3, "max_tokens": 2048}


@pytest.mark.parametrize(
    "ligne",
    [
        "max_tokens = 0",
        "max_tokens = 1024.0",
        "graine = -1",
        'graine = "42"',
        "graine = true",
        "temperature = -0.5",
        "temperature = nan",
        "top_p = 0.9",
    ],
)
def test_reglages_invalides(tmp_path: Path, ligne: str) -> None:
    with pytest.raises(ConfigurationInvalide):
        charger_evaluation(_toml_evaluation(tmp_path, ligne))


def test_reglages_configures_transmis_et_inscrits(depot_eval: Path, modeles: Path) -> None:
    llm = FakeLlmDeterministe()
    rapport = lancer(depot_eval, Fabrique(llm), config=_avec_generation(graine=7, max_tokens=64))

    attendu = {"temperature": 0.0, "seed": 7, "max_tokens": 64}
    assert llm.appels and all(a["options"] == attendu for a in llm.appels)
    brut = json.loads((rapport.run.dossier / "run.json").read_text(encoding="utf-8"))
    assert brut["graine"] == 7 and brut["config"]["options_llm"] == attendu


def test_reprise_refusee_si_decodage_different(
    depot_eval: Path, modeles: Path, fabrique: Fabrique
) -> None:
    run_id = _run_interrompu(depot_eval, fabrique)
    with pytest.raises(ManifesteInvalide, match="décodage"):
        reprendre_generation(
            run_id, racine=depot_eval, fabrique=fabrique, config=_avec_generation(max_tokens=2048)
        )
    run = ouvrir_run(run_id, racine=depot_eval)
    assert len(lignes(run)) == 3 and run.statut_courant() == "interrompu"
    # Mêmes valeurs, données explicitement : la reprise passe.
    rapport = reprendre_generation(
        run_id, racine=depot_eval, fabrique=fabrique, config=_avec_generation()
    )
    assert rapport.statut == "complet"


def test_tronquee() -> None:
    assert tronquee([Jeton(texte="a"), Fin(raison="longueur")]) is True
    assert tronquee([Fin(raison="terminee")]) is False
    assert tronquee([Fin(raison="interrompue")]) is False
    assert tronquee([Jeton(texte="a"), Erreur(code="x", message="y")]) is None


def test_sortie_tronquee_reste_ok(depot_eval: Path, modeles: Path) -> None:
    """`finish_reason` `length` (Fin `longueur`) : statut `ok`, `tronquee` vrai, compté."""
    llm = FakeLlmDeterministe(raison=lambda messages, options: "longueur")
    rapport = lancer(depot_eval, Fabrique(llm), items=("CR-001", "RE-001", "Q-001"))

    assert (rapport.ok, rapport.erreur, rapport.tronquees) == (3, 0, 3)
    assert rapport.statut == "complet"
    for generation in lignes(rapport.run):
        assert generation.statut == "ok" and generation.tronquee is True
        assert generation.trace[-1]["type"] == "fin"
        assert generation.trace[-1]["raison"] == "longueur"


def test_cr_tronque_sur_un_seul_appel(depot_eval: Path, modeles: Path) -> None:
    """CR : la raison la plus grave des appels l'emporte, un seul appel coupé suffit."""
    llm = FakeLlmDeterministe()
    llm.raison = lambda messages, options: "longueur" if len(llm.appels) == 1 else "terminee"
    rapport = lancer(depot_eval, Fabrique(llm), items=("CR-001",))

    (generation,) = lignes(rapport.run)
    assert generation.statut == "ok" and generation.tronquee is True
    assert rapport.tronquees == 1
