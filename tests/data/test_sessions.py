"""Sessions de l'étape `generate` (story 9.4) : un appel, Q, CR en deux temps, traces RD.

Faux serveur Mistral, port d'outils et Index factices (`tests/data/conftest.py`). Aucun appel
réel. Toutes les chaînes de contenu sont des jetons aléatoires (D1.1).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("mistralai")

from slmsp.core.items import IdentifiantsProteges  # noqa: E402
from slmsp.core.schemas.cassette import Cassette  # noqa: E402
from slmsp.harness.prompts import AUCUN_PASSAGE  # noqa: E402
from slmsp.mcp.direct import DelaiDepasse  # noqa: E402
from slmsp.mcp.outils import charger_outils  # noqa: E402

GENERIQUE = {"generique": 1}
RD = {"RD": 1}


def _abandon(monde: Any, resultat: Any) -> dict[str, Any]:
    assert monde.lignes(resultat, "brut.jsonl") == []
    (abandon,) = monde.lignes(resultat, "abandons.jsonl")
    return abandon


# --- Un appel -----------------------------------------------------------------------------------


def test_session_a_un_appel(monde: Any) -> None:
    graine = monde.amorce("generique", "demande", ligne=1)
    seed = monde.ecrire_seed([graine])
    resultat = monde.lancer(GENERIQUE, seed=seed)

    assert resultat.statut == "complet"
    (corps,) = monde.faux.corps
    assert graine["texte"] in corps["messages"][0]["content"]
    assert "tools" not in corps and "tool_choice" not in corps
    (brut,) = monde.lignes(resultat, "brut.jsonl")
    (ligne,) = monde.journal_lignes()
    assert brut["appel_ids"] == [ligne["appel_id"]]
    assert brut["amorce_ids"] == [graine["amorce_id"]]
    assert brut["cassettes"] == [] and brut["appels_nouveaux"] == 1
    assert brut["session_id"].startswith("generique-") and ligne["session_id"] == brut["session_id"]


def test_reponse_tronquee_abandonnee(monde: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("generique", "demande", ligne=1)])
    monde.faux.reponses = [{"finish_reason": "length"}]
    resultat = monde.lancer(GENERIQUE, seed=seed)
    assert _abandon(monde, resultat)["motif"] == "reponse_tronquee"
    assert resultat.statut == "complet"


def test_amorce_corrompue_abandon_et_session_suivante(monde: Any) -> None:
    fausse = monde.amorce("generique", "demande", ligne=1, sha="0" * 64)
    bonne = monde.amorce("generique", "demande", ligne=2)
    seed = monde.ecrire_seed([fausse, bonne])
    resultat = monde.lancer({"generique": 2}, seed=seed)

    assert _abandon_ou_brut(monde, resultat) == (["provenance_invalide"], 1)
    assert len(monde.faux.corps) == 1  # rien n'est parti pour l'amorce corrompue


def _abandon_ou_brut(monde: Any, resultat: Any) -> tuple[list[str], int]:
    motifs = [a["motif"] for a in monde.lignes(resultat, "abandons.jsonl")]
    return motifs, len(monde.lignes(resultat, "brut.jsonl"))


# --- Q : passages de l'Index ------------------------------------------------------------------


def test_q_passages_rendus_et_url_protegee_retiree(monde: Any, doublures: Any) -> None:
    gardes = [doublures.passage(), doublures.passage()]
    protege = doublures.passage(url="https://Protege.invalid/page/")
    monde.recherche.passages = [gardes[0], protege, gardes[1]]
    monde.proteges = IdentifiantsProteges(
        frozenset(), frozenset({"https://protege.invalid/page"}), frozenset(), frozenset()
    )
    question = monde.amorce("Q", "question", ligne=1)
    seed = monde.ecrire_seed([question])
    resultat = monde.lancer({"Q": 1}, seed=seed)

    assert monde.recherche.requetes == [question["texte"]]
    (corps,) = monde.faux.corps
    consigne = corps["messages"][0]["content"]
    assert question["texte"] in consigne
    assert all(p.texte in consigne and p.url in consigne for p in gardes)
    assert protege.texte not in consigne
    (brut,) = monde.lignes(resultat, "brut.jsonl")
    assert brut["passages"] == [p.chunk_id for p in gardes]
    assert brut["index_version"] == "index-factice"
    assert resultat.run.manifeste.index_version == "index-factice"
    assert resultat.bilan["comptes_plan"]["Q"]["passages_proteges"] == 1


def test_q_sans_passage(monde: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("Q", "question", ligne=1)])
    resultat = monde.lancer({"Q": 1}, seed=seed)
    (corps,) = monde.faux.corps
    assert AUCUN_PASSAGE in corps["messages"][0]["content"]
    (brut,) = monde.lignes(resultat, "brut.jsonl")
    assert brut["passages"] == []


# --- CR en deux temps ---------------------------------------------------------------------------


def test_cr_transcription_puis_compte_rendu(monde: Any) -> None:
    scenario = monde.scenario()
    seed = monde.ecrire_seed([scenario, monde.amorce("CR", "theme", ligne=1)])
    resultat = monde.lancer({"CR": 1}, seed=seed)

    premier, second = monde.faux.corps
    assert scenario["texte"] in premier["messages"][0]["content"]
    transcription = monde.journal_lignes()[-2]
    texte = json.loads(transcription["reponse_brute"])["choices"][0]["message"]["content"]
    assert texte in second["messages"][0]["content"]
    (brut,) = monde.lignes(resultat, "brut.jsonl")
    (derivee,) = monde.lignes(resultat, "amorces-derivees.jsonl")
    assert derivee["amorce_id"] == f"{brut['session_id']}.transcription"
    assert derivee["appel_id"] == transcription["appel_id"] == brut["appel_ids"][0]
    assert derivee["auteur_contenu"] == "mistral"
    assert brut["amorces_derivees"] == [derivee["amorce_id"]]
    assert brut["appel_ids"][1] == monde.journal_lignes()[-1]["appel_id"]
    assert resultat.bilan["comptes_plan"]["CR"]["amorces_ignorees"] == 1  # le thème


# --- RD : tours d'outils ------------------------------------------------------------------------


def _cassette(monde: Any, chemin: str) -> Cassette:
    return Cassette.model_validate_json((monde.racine / chemin).read_bytes())


def test_rd_plusieurs_tours(monde: Any, doublures: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("RD", "demande", ligne=1)])
    premier = doublures.appel_outil("search_datasets", {"query": doublures.factice("q")})
    second = doublures.appel_outil("get_dataset_info", {"dataset_id": doublures.factice("d")})
    monde.faux.reponses = [{"appels": [premier]}, {"appels": [second]}, {}]
    resultat = monde.lancer(RD, seed=seed)

    assert resultat.statut == "complet"
    corps = monde.faux.corps
    assert len(corps) == 3
    for requete in corps:
        assert requete["tools"] == charger_outils(doublures.OUTILS_MCP)
        assert requete["tool_choice"] == "auto"
    assert monde.outils.ouvertures == 1
    assert [nom for nom, _ in monde.outils.appels] == ["search_datasets", "get_dataset_info"]
    (brut,) = monde.lignes(resultat, "brut.jsonl")
    sid = brut["session_id"]
    assert brut["cassettes"] == [f"data/cassettes/{sid}.t1.json", f"data/cassettes/{sid}.t2.json"]
    t1, t2 = (_cassette(monde, c) for c in brut["cassettes"])
    assert [i.request["params"]["name"] for i in t1.interactions] == ["search_datasets"]
    assert [i.request["params"]["name"] for i in t2.interactions] == ["get_dataset_info"]
    # Dernière requête : user, assistant (appel), tool, assistant (appel), tool.
    messages = corps[2]["messages"]
    assert [m["role"] for m in messages] == ["user", "assistant", "tool", "assistant", "tool"]
    textes = [e["text"] for e in t2.interactions[0].response["result"]["content"]]
    assert messages[4]["content"] == "\n".join(textes)
    assert messages[4]["tool_call_id"] == second["id"]
    assert len(brut["appel_ids"]) == 3 and brut["appels_nouveaux"] == 3


@pytest.mark.parametrize(
    ("appel", "motif"),
    [
        (("outil_inconnu", {"query": "x"}), "appel_non_conforme"),
        (("search_datasets", {"inconnu": 1}), "appel_non_conforme"),
        (("search_datasets", "{pas du json"), "appel_non_conforme"),
        (("get_dataset_info", {"dataset_id": "id-protege"}), "fuite_identifiant"),
    ],
)
def test_rd_appel_refuse_avant_envoi(
    monde: Any, doublures: Any, appel: tuple[str, Any], motif: str
) -> None:
    monde.proteges = IdentifiantsProteges(
        frozenset(), frozenset(), frozenset({"id-protege"}), frozenset()
    )
    seed = monde.ecrire_seed([monde.amorce("RD", "demande", ligne=1)])
    monde.faux.reponses = [{"appels": [doublures.appel_outil(*appel)]}]
    resultat = monde.lancer(RD, seed=seed)

    assert _abandon(monde, resultat)["motif"] == motif
    assert monde.outils.appels == [] and monde.outils.ouvertures == 0
    assert not (monde.racine / "data" / "cassettes").exists()


def test_rd_tours_max(monde: Any, doublures: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("RD", "demande", ligne=1)])
    appels = [
        doublures.appel_outil("search_datasets", {"query": doublures.factice()}) for _ in "ab"
    ]
    monde.faux.reponses = [{"appels": [appels[0]]}, {"appels": [appels[1]]}]
    resultat = monde.lancer(RD, seed=seed, tours_outils_max=1)
    abandon = _abandon(monde, resultat)
    assert abandon["motif"] == "tours_max"
    assert len(monde.outils.appels) == 1 and len(abandon["cassettes"]) == 1


def test_rd_sans_appel_outil(monde: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("RD", "demande", ligne=1)])
    resultat = monde.lancer(RD, seed=seed)
    assert _abandon(monde, resultat)["motif"] == "sans_appel_outil"


def test_rd_erreur_outil_cassette_ecrite(monde: Any, doublures: Any) -> None:
    monde.outils.script = {"search_datasets": "erreur"}
    seed = monde.ecrire_seed([monde.amorce("RD", "demande", ligne=1)])
    monde.faux.reponses = [{"appels": [doublures.appel_outil("search_datasets", {"query": "x"})]}]
    resultat = monde.lancer(RD, seed=seed)
    abandon = _abandon(monde, resultat)
    assert abandon["motif"] == "erreur_outil"
    (chemin,) = abandon["cassettes"]
    assert "error" in _cassette(monde, chemin).interactions[0].response


def test_rd_panne_transport_incident_puis_reprise(monde: Any, doublures: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("RD", "demande", ligne=1)])
    appel = doublures.appel_outil("search_datasets", {"query": doublures.factice()})
    monde.outils.script = {"search_datasets": DelaiDepasse("délai factice")}
    monde.faux.reponses = [{"appels": [appel]}]
    resultat = monde.lancer(RD, seed=seed)

    assert resultat.statut == "partiel-erreur"
    assert monde.lignes(resultat, "brut.jsonl") == []
    assert monde.lignes(resultat, "abandons.jsonl") == []
    (incident,) = monde.lignes(resultat, "incidents.jsonl")
    assert incident["type"] == "DelaiDepasse"
    assert not (monde.racine / "data" / "cassettes").exists()

    monde.outils.script = {}
    reprise = monde.lancer(RD, reprendre=resultat.run.run_id)
    assert reprise.statut == "complet"
    assert len(monde.faux.corps) == 2  # A0 réutilisé, seule la réponse finale est payée
    (brut,) = monde.lignes(reprise, "brut.jsonl")
    assert brut["appels_reutilises"] == 1 and brut["appels_nouveaux"] == 1


def test_rd_cassette_existante_relue_et_incoherente(monde: Any, doublures: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("RD", "demande", ligne=1)])
    appel = doublures.appel_outil("search_datasets", {"query": doublures.factice()})
    monde.faux.reponses = [{"appels": [appel]}, {}]
    premier = monde.lancer(RD, seed=seed)
    (brut,) = monde.lignes(premier, "brut.jsonl")

    # Nouveau run sur le même seed : la cassette du tour est relue, l'outil n'est pas rappelé.
    second = monde.lancer(RD, seed=seed)
    assert len(monde.outils.appels) == 1 and len(monde.faux.corps) == 2
    (brut_2,) = monde.lignes(second, "brut.jsonl")
    assert brut_2["cassettes"] == brut["cassettes"] and brut_2["appels_reutilises"] == 2

    # Cassette du tour altérée (autre outil) : abandon `cassette_incoherente`.
    chemin = Path(monde.racine / brut["cassettes"][0])
    cassette = json.loads(chemin.read_text(encoding="utf-8"))
    cassette["interactions"][0]["request"]["params"]["name"] = "get_dataset_info"
    chemin.write_text(json.dumps(cassette), encoding="utf-8")
    troisieme = monde.lancer(RD, seed=seed)
    assert _abandon(monde, troisieme)["motif"] == "cassette_incoherente"
