"""Recherche de données (RD) : boucle d'outils en Mode connecté et hors ligne (story 4.3).

Le `ToolPort` est le Bac à sable MCP sur les cassettes du calibrage (R-001, R-002), en
lecture seule ; le modèle est `FakeLlm` (mots aléatoires, D1.1), ou `ClientLlama` en
`json-generique` sur un transport factice qui sert du SSE.
"""

from __future__ import annotations

import dataclasses
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import httpx2  # noqa: TID251 (tests : transports factices)
import pytest
from harness_factices import (
    USAGE,
    FakeEmbedder,
    FakeLlm,
    FakeVectorStore,
    SpyToolPort,
    mots,
    passage,
    script,
    url_factice,
)

from slmsp.core.evenements import (
    AppelNonConforme,
    AppelOutil,
    Avertissement,
    Erreur,
    Fin,
    Jeton,
    Repli,
    ResultatOutil,
    Sources,
)
from slmsp.harness.modes import ModeFixe
from slmsp.harness.service import AssistantService
from slmsp.harness.taches import MOTIF_OUTIL_INATTENDU
from slmsp.harness.taches.recherche import (
    CODE_AVERTISSEMENT,
    FACTEUR_RECHERCHE,
    MOTIF_NON_PROPOSE,
    SOURCE_CATALOGUE,
    TEXTE_ECHEC,
    contenu_resultat,
    messages_connecte,
    sources_mcp,
)
from slmsp.inference.client import ClientLlama, appel_canonique
from slmsp.mcp.bac_a_sable import BacASable
from slmsp.mcp.cassettes import lire_cassette
from slmsp.mcp.outils import charger_outils

RACINE = Path(__file__).resolve().parents[2]
CALIBRAGE = RACINE / "eval" / "calibrage" / "cassettes"
R001 = CALIBRAGE / "R-001.json"
R002 = CALIBRAGE / "R-002.json"


class Enregistreur:
    """`ToolPort` qui enregistre chaque appel puis le délègue au Bac à sable."""

    def __init__(self, interne: Any) -> None:
        self.interne = interne
        self.appels: list[tuple[str, dict[str, Any]]] = []

    def lister_outils(self) -> list[dict[str, Any]]:
        return self.interne.lister_outils()

    def appeler(self, nom: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        self.appels.append((nom, dict(arguments)))
        return self.interne.appeler(nom, arguments)


def interaction(chemin: Path, rang: int) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """(outil, arguments, réponse JSON-RPC) de l'interaction `tools/call` de rang `rang`."""
    appels = [i for i in lire_cassette(chemin).interactions if i.request["method"] == "tools/call"]
    requete, reponse = appels[rang].request, appels[rang].response
    assert reponse is not None
    return requete["params"]["name"], requete["params"]["arguments"], reponse


def catalogue(numero: int, score: float) -> Any:
    return dataclasses.replace(passage(numero, score), source=SOURCE_CATALOGUE)


def appel(id_: str, nom: str, arguments: dict[str, Any]) -> AppelOutil:
    return AppelOutil(id=id_, nom=nom, arguments=arguments)


def tour_outils(*appels: AppelOutil) -> list[Any]:
    return [*appels, Fin(raison="terminee", usage=dict(USAGE))]


def service(table, config, llm, *, passages=(), outils=None, mode=None):
    store = FakeVectorStore(passages)
    instance = AssistantService(llm, FakeEmbedder(), store, outils, mode, config, taches=table)
    return instance, store


def repondre(table, config, llm, *, demande=None, **kw) -> list[Any]:
    instance, _ = service(table, config, llm, **kw)
    demande = demande if demande is not None else mots(7, "demande")
    return list(instance.repondre("RD", [{"role": "user", "content": demande}]))


def types(evenements: list[Any]) -> list[str]:
    """Types d'évènements, jetons consécutifs fusionnés."""
    resultat: list[str] = []
    for evenement in evenements:
        nom = type(evenement).__name__
        if nom == "Jeton" and resultat and resultat[-1] == "Jeton":
            continue
        resultat.append(nom)
    return resultat


def texte_de(evenements: list[Any]) -> str:
    return "".join(e.texte for e in evenements if isinstance(e, Jeton))


# --- Mode connecté -------------------------------------------------------------------------


def test_connecte_appel_valide(table, config_harnais) -> None:
    nom, arguments, reponse = interaction(R001, 0)
    url = re.search(r"https://\S+", reponse["result"]["content"][0]["text"]).group(0)
    seuil = config_harnais.recherche.seuil_pertinence
    passages = [catalogue(1, seuil + 0.2), catalogue(2, seuil + 0.1)]
    texte = f"{mots(6, 'a')} {url} {mots(4, 'b')} [2]."
    llm = FakeLlm(tour_outils(appel("c1", nom, arguments)), script(texte))
    outils = Enregistreur(BacASable([R001]))

    instance, store = service(
        table, config_harnais, llm, passages=passages, outils=outils, mode=ModeFixe("connecte")
    )
    demande = mots(7, "demande")
    evenements = list(instance.repondre("RD", [{"role": "user", "content": demande}]))

    assert types(evenements) == ["AppelOutil", "ResultatOutil", "Jeton", "Sources", "Fin"]
    appel_emis, resultat = evenements[0], evenements[1]
    assert appel_emis == appel("c1", nom, arguments)
    assert resultat == ResultatOutil(id="c1", nom=nom, resultat=reponse["result"], erreur=False)
    assert outils.appels == [(nom, arguments)]
    assert texte_de(evenements) == texte

    premier, second = llm.appels
    # MCP d'abord : premier tour sans passages, l'Index n'est pas interrogé.
    assert store.appels == []
    systeme, user = premier["messages"]
    assert user == {"role": "user", "content": demande}
    assert systeme["content"] == table.tache("RD").prompt.consigne
    assert premier["messages"] == messages_connecte(table.tache("RD"), demande, charger_outils())
    assert premier["tools"] == charger_outils()
    assert second["tools"] == charger_outils()
    roles = [m["role"] for m in second["messages"]]
    assert roles == ["system", "user", "assistant", "tool"]
    assert second["messages"][:2] == premier["messages"]
    assistant, outil = second["messages"][2:]
    assert assistant == {
        "role": "assistant",
        "content": None,
        "tool_calls": [appel_canonique(appel_emis)],
    }
    assert outil == {"role": "tool", "tool_call_id": "c1", "content": contenu_resultat(reponse)}
    assert outil["content"] == reponse["result"]["content"][0]["text"]

    (sources,) = [e for e in evenements if isinstance(e, Sources)]
    (mcp,) = sources.sources  # aucun passage fourni : le renvoi [2] ne désigne rien
    assert (mcp.url, mcp.origine) == (url, "mcp")
    assert mcp.titre != url and mcp.titre in outil["content"]
    fin = evenements[-1]
    assert isinstance(fin, Fin) and fin.urls_inventees == []
    assert fin.usage["prompt_tokens"] == 2 * USAGE["prompt_tokens"]
    assert not any(isinstance(e, (Avertissement, Repli, Erreur)) for e in evenements)


def test_url_inventee_signalee(table, config_harnais) -> None:
    nom, arguments, _ = interaction(R001, 0)
    inventee = url_factice("inventee")
    llm = FakeLlm(tour_outils(appel("c1", nom, arguments)), script(f"{mots(3, 'x')} {inventee}"))
    evenements = repondre(
        table, config_harnais, llm, outils=BacASable([R001]), mode=ModeFixe("connecte")
    )
    assert evenements[-1].urls_inventees == [inventee]


def test_appels_dans_l_ordre(table, config_harnais) -> None:
    premiers = [interaction(R002, rang) for rang in range(3)]
    llm = FakeLlm(
        tour_outils(*(appel(f"c{i}", n, a) for i, (n, a, _) in enumerate(premiers[:2]))),
        tour_outils(appel("c2", premiers[2][0], premiers[2][1])),
        script(mots(5, "fin")),
    )
    outils = Enregistreur(BacASable([R002]))
    evenements = repondre(table, config_harnais, llm, outils=outils, mode=ModeFixe("connecte"))
    assert types(evenements) == [
        "AppelOutil",
        "AppelOutil",
        "ResultatOutil",
        "ResultatOutil",
        "AppelOutil",
        "ResultatOutil",
        "Jeton",
        "Sources",
        "Fin",
    ]
    assert outils.appels == [(n, a) for n, a, _ in premiers]
    resultats = [e for e in evenements if isinstance(e, ResultatOutil)]
    assert [r.id for r in resultats] == ["c0", "c1", "c2"]
    assert [r.resultat for r in resultats] == [rep["result"] for _, _, rep in premiers]
    roles = [m["role"] for m in llm.appels[2]["messages"]]
    assert roles == ["system", "user", "assistant", "tool", "tool", "assistant", "tool"]


def test_query_resource_data_resultat_exact(table, config_harnais) -> None:
    nom, arguments, reponse = interaction(R002, 2)
    assert nom == "query_resource_data"
    llm = FakeLlm(tour_outils(appel("q1", nom, arguments)), script(mots(4, "v")))
    evenements = repondre(
        table, config_harnais, llm, outils=BacASable([R002]), mode=ModeFixe("connecte")
    )
    (resultat,) = [e for e in evenements if isinstance(e, ResultatOutil)]
    assert resultat.resultat == reponse["result"]
    assert not resultat.erreur


def test_appel_non_conforme_jamais_envoye(table, config_harnais) -> None:
    nom, arguments, _ = interaction(R001, 0)
    faux = appel("c9", nom, {**arguments, "champ_factice": mots(1, "f")})
    llm = FakeLlm(tour_outils(faux), script(mots(5, "r")))
    outils = Enregistreur(BacASable([R001]))
    evenements = repondre(table, config_harnais, llm, outils=outils, mode=ModeFixe("connecte"))

    assert types(evenements) == ["AppelNonConforme", "Jeton", "Sources", "Avertissement", "Fin"]
    refus = evenements[0]
    assert refus.nom == nom and "champ_factice" in refus.motif
    assert json.loads(refus.arguments_bruts) == faux.arguments
    assert outils.appels == []
    assert llm.appels[1]["tools"] is None  # appels tous refusés : dernière génération


def test_appel_non_conforme_parmi_valides(table, config_harnais) -> None:
    nom, arguments, reponse = interaction(R001, 0)
    llm = FakeLlm(
        tour_outils(appel("c1", "outil_factice", {}), appel("c2", nom, arguments)),
        script(mots(3, "s")),
    )
    outils = Enregistreur(BacASable([R001]))
    evenements = repondre(table, config_harnais, llm, outils=outils, mode=ModeFixe("connecte"))
    assert types(evenements)[:3] == ["AppelNonConforme", "AppelOutil", "ResultatOutil"]
    assert "outil non exposé" in evenements[0].motif
    assert outils.appels == [(nom, arguments)]
    assistant = llm.appels[1]["messages"][2]
    assert [c["id"] for c in assistant["tool_calls"]] == ["c2"]


def test_plafond_d_iterations(table, config_harnais) -> None:
    nom, arguments, _ = interaction(R001, 0)
    llm = FakeLlm(tour_outils(appel("c1", nom, arguments)))  # le même tour, sans fin
    outils = Enregistreur(BacASable([R001]))
    evenements = repondre(table, config_harnais, llm, outils=outils, mode=ModeFixe("connecte"))

    maximum = config_harnais.outils.iterations_max
    assert len(llm.appels) == maximum + 1
    assert all(a["tools"] == charger_outils() for a in llm.appels[:maximum])
    assert llm.appels[maximum]["tools"] is None
    assert len(outils.appels) == 1  # appel identique : résultat repris, envoyé une seule fois
    resultats = [e for e in evenements if isinstance(e, ResultatOutil)]
    assert len(resultats) == maximum
    assert all(r.resultat == resultats[0].resultat for r in resultats)
    # Ids dupliqués d'un tour à l'autre : renommés, uniques dans la conversation.
    ids = [r.id for r in resultats]
    assert ids[0] == "c1" and len(set(ids)) == maximum
    assert all(re.fullmatch(r"appel-[0-9a-f]{32}", i) for i in ids[1:])
    emis = [e.id for e in evenements if isinstance(e, AppelOutil)]
    assert emis == ids
    # La dernière génération n'a plus d'outil : l'appel devient non conforme, jamais exécuté.
    dernier = [e for e in evenements if isinstance(e, AppelNonConforme)]
    assert [e.motif for e in dernier] == [MOTIF_OUTIL_INATTENDU]
    assert isinstance(evenements[-1], Fin)


def test_ids_dupliques_dans_un_tour(table, config_harnais) -> None:
    nom, arguments, _ = interaction(R001, 0)
    llm = FakeLlm(
        tour_outils(appel("c1", nom, arguments), appel("c1", nom, arguments)),
        script(mots(2, "d")),
    )
    evenements = repondre(
        table, config_harnais, llm, outils=BacASable([R001]), mode=ModeFixe("connecte")
    )
    ids = [e.id for e in evenements if isinstance(e, ResultatOutil)]
    assert ids[0] == "c1" and ids[1] != "c1" and len(set(ids)) == 2
    outils_msgs = [m for m in llm.appels[1]["messages"] if m["role"] == "tool"]
    assert [m["tool_call_id"] for m in outils_msgs] == ids


def test_ids_de_l_historique_evites(table, config_harnais) -> None:
    nom, arguments, reponse = interaction(R001, 0)
    llm = FakeLlm(tour_outils(appel("c1", nom, arguments)), script(mots(2, "h")))
    instance, _ = service(
        table, config_harnais, llm, outils=BacASable([R001]), mode=ModeFixe("connecte")
    )
    historique = [
        {"role": "user", "content": mots(4, "u1")},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [appel_canonique(appel("c1", nom, arguments))],
        },
        {"role": "tool", "tool_call_id": "c1", "content": contenu_resultat(reponse)},
        {"role": "assistant", "content": mots(3, "a1")},
        {"role": "user", "content": mots(4, "u2")},
    ]
    evenements = list(instance.repondre("RD", historique))
    (resultat,) = [e for e in evenements if isinstance(e, ResultatOutil)]
    assert resultat.id != "c1"
    assert not any(isinstance(e, Erreur) for e in evenements)


# --- Passages du catalogue -------------------------------------------------------------------


def test_passages_du_catalogue_seulement(table, config_harnais) -> None:
    seuil = config_harnais.recherche.seuil_pertinence
    k = config_harnais.recherche.k
    fiches = [passage(10 + i, seuil + 0.4) for i in range(3)]  # service-public, mieux classées
    jeux = [catalogue(i, seuil + 0.3 - i / 100) for i in range(k + 2)]
    sous_seuil = catalogue(99, seuil - 0.1)
    llm = FakeLlm(script(mots(4, "p")))
    instance, store = service(
        table, config_harnais, llm, passages=[*fiches, *jeux, sous_seuil], mode=None
    )
    list(instance.repondre("RD", [{"role": "user", "content": mots(5, "q")}]))
    assert store.appels == [k * FACTEUR_RECHERCHE]
    contenu = llm.appels[0]["messages"][1]["content"]
    assert all(p.url in contenu for p in jeux[:k])
    assert not any(p.url in contenu for p in [*fiches, *jeux[k:], sous_seuil])


# --- Hors ligne ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("outils", "mode"),
    [
        ("espion", ModeFixe("hors-ligne-detecte")),
        ("espion", ModeFixe("hors-ligne-force")),
        ("espion", None),
        (None, ModeFixe("connecte")),
    ],
    ids=["detecte", "force", "sans-mode", "sans-outils"],
)
def test_hors_ligne(table, config_harnais, outils, mode) -> None:
    seuil = config_harnais.recherche.seuil_pertinence
    passages = [catalogue(1, seuil + 0.2), catalogue(2, seuil + 0.1)]
    espion = SpyToolPort() if outils == "espion" else None
    llm = FakeLlm(script(mots(9, "h")))
    evenements = repondre(table, config_harnais, llm, passages=passages, outils=espion, mode=mode)
    assert types(evenements) == ["Jeton", "Sources", "Avertissement", "Fin"]
    (generation,) = llm.appels
    assert generation["tools"] is None
    if espion is not None:
        assert espion.appels == [] and espion.gate.appels == []
    sources = evenements[-3].sources
    assert [s.url for s in sources] == [p.url for p in passages]  # le lien est toujours donné
    assert [s.numero for s in sources] == [1, 2]
    alerte = evenements[-2]
    assert alerte.code == CODE_AVERTISSEMENT and "non vérifié en ligne" in alerte.message
    assert evenements[-1].urls_inventees == []


def test_hors_ligne_appel_du_modele_refuse(table, config_harnais) -> None:
    nom, arguments, _ = interaction(R001, 0)
    espion = SpyToolPort()
    llm = FakeLlm([appel("c1", nom, arguments), *script(mots(3, "z"))])
    evenements = repondre(
        table, config_harnais, llm, outils=espion, mode=ModeFixe("hors-ligne-detecte")
    )
    assert types(evenements)[0] == "AppelNonConforme"
    assert evenements[0].motif == MOTIF_OUTIL_INATTENDU
    assert espion.appels == []


# --- Sources MCP et rendu du message tool --------------------------------------------------


def test_contenu_resultat() -> None:
    _, _, reponse = interaction(R001, 0)
    texte = reponse["result"]["content"][0]["text"]
    assert contenu_resultat(reponse) == contenu_resultat(reponse["result"]) == texte
    deux = {"content": [{"type": "text", "text": "a"}, {"type": "image", "data": "x"}]}
    assert contenu_resultat(deux) == 'a\n{"data": "x", "type": "image"}'
    erreur = {"jsonrpc": "2.0", "id": 3, "error": {"code": -32602, "message": "<m>"}}
    assert contenu_resultat(erreur) == contenu_resultat({"error": erreur["error"]}) == "<m>"
    assert contenu_resultat(None) == TEXTE_ECHEC
    assert contenu_resultat({"autre": 1}) == TEXTE_ECHEC


def test_sources_mcp_titre_ou_url() -> None:
    a, b = url_factice("a"), url_factice("b")
    resultat = {
        "content": [
            {"type": "text", "text": f"{mots(3, 't')}\n\n1. {mots(2, 'titre')}\n   URL: {a}\n"},
            {"type": "text", "text": f"{mots(2, 'x')}\nURL: {b}"},
        ]
    }
    texte = f"{b} {a} {a}/ {url_factice('c')}"
    sources = sources_mcp(texte, [resultat])
    assert [(s.titre, s.url, s.origine) for s in sources] == [
        (b, b, "mcp"),
        (mots(2, "titre"), a, "mcp"),
    ]


# --- json-generique --------------------------------------------------------------------------


class ServeurSse:
    """Transport factice de `llama-server` : une réponse SSE `json-generique` par requête."""

    def __init__(self, *sorties: Any) -> None:
        self.sorties = list(sorties)
        self.corps: list[dict[str, Any]] = []

    def repondre(self, requete: httpx2.Request) -> httpx2.Response:
        self.corps.append(json.loads(requete.content))
        sortie = self.sorties[min(len(self.corps), len(self.sorties)) - 1]
        texte = json.dumps(sortie, ensure_ascii=False)
        moitie = len(texte) // 2
        morceaux = [
            {"choices": [{"index": 0, "delta": {"content": partie}, "finish_reason": None}]}
            for partie in (texte[:moitie], texte[moitie:])
        ]
        morceaux.append({"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]})
        morceaux.append({"choices": [], "usage": USAGE})
        corps = "".join(f"data: {json.dumps(m, ensure_ascii=False)}\n\n" for m in morceaux)
        corps += "data: [DONE]\n\n"
        return httpx2.Response(
            200,
            content=corps.encode("utf-8"),
            headers={"content-type": "text/event-stream"},
            request=requete,
        )


def test_json_generique_boucle_inchangee(table, config_harnais) -> None:
    nom, arguments, reponse = interaction(R001, 0)
    texte = mots(6, "jg")
    serveur = ServeurSse(
        {"tool_calls": [{"name": nom, "arguments": arguments}]}, {"content": texte}
    )
    client = ClientLlama(
        8077,
        protocole_outils="json-generique",
        transport_interne=httpx2.MockTransport(serveur.repondre),
    )
    with client:
        evenements = repondre(
            table, config_harnais, client, outils=BacASable([R001]), mode=ModeFixe("connecte")
        )

    assert types(evenements) == ["AppelOutil", "ResultatOutil", "Jeton", "Sources", "Fin"]
    appel_emis, resultat = evenements[0], evenements[1]
    assert (appel_emis.nom, appel_emis.arguments) == (nom, arguments)
    assert re.fullmatch(r"appel-[0-9a-f]{32}", appel_emis.id)
    assert resultat.id == appel_emis.id and resultat.resultat == reponse["result"]
    assert texte_de(evenements) == texte
    assert evenements[-1].urls_inventees == []

    premier, second = serveur.corps
    for corps in serveur.corps:
        assert "tools" not in corps
        assert corps["response_format"]["type"] == "json_schema"
    assert [m["role"] for m in second["messages"]] == ["system", "user", "assistant", "tool"]
    assert second["messages"][2]["tool_calls"] == [appel_canonique(appel_emis)]
    assert second["messages"][3]["content"] == contenu_resultat(reponse)

    # Mêmes évènements qu'en natif (à l'id d'appel près).
    natif = FakeLlm(tour_outils(appel(appel_emis.id, nom, arguments)), script(texte))
    attendus = repondre(
        table, config_harnais, natif, outils=BacASable([R001]), mode=ModeFixe("connecte")
    )
    assert [type(e) for e in evenements if not isinstance(e, (Jeton, Fin))] == [
        type(e) for e in attendus if not isinstance(e, (Jeton, Fin))
    ]
    assert [e for e in evenements if not isinstance(e, (Jeton, Fin))] == [
        e for e in attendus if not isinstance(e, (Jeton, Fin))
    ]


# --- Revue : outils offerts, avertissement, refus, appels répétés, erreurs --------------------


class SousEnsemble(Enregistreur):
    """`ToolPort` qui ne liste qu'une partie des outils exposés."""

    def __init__(self, interne: Any, noms: set[str]) -> None:
        super().__init__(interne)
        self.noms = noms

    def lister_outils(self) -> list[dict[str, Any]]:
        return [t for t in self.interne.lister_outils() if t["function"]["name"] in self.noms]


class Repondeur:
    """`ToolPort` qui renvoie toujours une copie de `reponse` et compte les envois."""

    def __init__(self, reponse: dict[str, Any]) -> None:
        self.reponse = reponse
        self.appels: list[tuple[str, dict[str, Any]]] = []

    def lister_outils(self) -> list[dict[str, Any]]:
        return charger_outils()

    def appeler(self, nom: str, arguments: Mapping[str, Any]) -> dict[str, Any]:
        self.appels.append((nom, dict(arguments)))
        return json.loads(json.dumps(self.reponse))


def catalogue_fourni(config_harnais) -> list[Any]:
    seuil = config_harnais.recherche.seuil_pertinence
    return [catalogue(1, seuil + 0.2), catalogue(2, seuil + 0.1)]


def test_outil_expose_mais_non_propose(table, config_harnais) -> None:
    outils = SousEnsemble(BacASable([R001]), {"search_datasets"})
    hors = appel("c1", "get_dataset_info", {"dataset_id": mots(1, "d")})
    llm = FakeLlm(tour_outils(hors), script(mots(4, "r")))
    evenements = repondre(
        table,
        config_harnais,
        llm,
        passages=catalogue_fourni(config_harnais),
        outils=outils,
        mode=ModeFixe("connecte"),
    )
    assert [t["function"]["name"] for t in llm.appels[0]["tools"]] == ["search_datasets"]
    refus = evenements[0]
    assert isinstance(refus, AppelNonConforme) and refus.motif == MOTIF_NON_PROPOSE
    assert outils.appels == []
    assert not any(isinstance(e, (AppelOutil, ResultatOutil)) for e in evenements)


def test_connecte_sans_appel_avertit(table, config_harnais) -> None:
    outils = Enregistreur(BacASable([R001]))
    llm = FakeLlm(script(mots(6, "t")))
    evenements = repondre(table, config_harnais, llm, outils=outils, mode=ModeFixe("connecte"))
    assert types(evenements) == ["Jeton", "Sources", "Avertissement", "Fin"]
    assert evenements[-2].code == CODE_AVERTISSEMENT
    assert outils.appels == []
    assert llm.appels[0]["tools"] == charger_outils()


def test_appels_tous_refuses_derniere_generation_sur_l_index(table, config_harnais) -> None:
    nom, arguments, _ = interaction(R001, 0)
    faux = appel("c9", nom, {**arguments, "champ_factice": mots(1, "f")})
    passages = catalogue_fourni(config_harnais)
    llm = FakeLlm(tour_outils(faux), script(mots(5, "r")))
    outils = Enregistreur(BacASable([R001]))
    instance, store = service(
        table, config_harnais, llm, passages=passages, outils=outils, mode=ModeFixe("connecte")
    )
    evenements = list(instance.repondre("RD", [{"role": "user", "content": mots(5, "q")}]))
    dernier = llm.appels[1]
    assert dernier["tools"] is None
    assert [m["role"] for m in dernier["messages"]] == ["system", "user"]
    assert all(p.url in dernier["messages"][1]["content"] for p in passages)
    assert len(store.appels) == 1 and outils.appels == []
    assert types(evenements)[-3:] == ["Sources", "Avertissement", "Fin"]


def test_texte_des_tours_separe(table, config_harnais) -> None:
    nom, arguments, reponse = interaction(R001, 0)
    url = re.search(r"https://\S+", reponse["result"]["content"][0]["text"]).group(0)
    llm = FakeLlm(
        [Jeton(texte=url), *tour_outils(appel("c1", nom, arguments))], script(mots(1, "x"))
    )
    evenements = repondre(
        table, config_harnais, llm, outils=BacASable([R001]), mode=ModeFixe("connecte")
    )
    assert evenements[-1].urls_inventees == []


def test_appel_identique_envoye_une_fois(table, config_harnais) -> None:
    nom, arguments, reponse = interaction(R001, 0)
    llm = FakeLlm(
        tour_outils(appel("c1", nom, arguments)),
        tour_outils(appel("c2", nom, dict(reversed(list(arguments.items()))))),
        script(mots(3, "f")),
    )
    outils = Enregistreur(BacASable([R001]))
    sondes: list[int] = []

    class Mode:
        def mode_courant(self) -> str:
            return "connecte"

        def sonder(self) -> str:
            sondes.append(1)
            return "connecte"

    evenements = repondre(table, config_harnais, llm, outils=outils, mode=Mode())
    resultats = [e for e in evenements if isinstance(e, ResultatOutil)]
    assert [r.id for r in resultats] == ["c1", "c2"]
    assert [r.resultat for r in resultats] == [reponse["result"]] * 2
    assert all(not r.erreur for r in resultats)
    assert len(outils.appels) == 1 and sondes == [1]


@pytest.mark.parametrize(
    "reponse",
    [
        {"jsonrpc": "2.0", "id": 3, "error": {"code": -32602, "message": mots(4, "err")}},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "result": {"content": [{"type": "text", "text": mots(4, "ko")}], "isError": True},
        },
    ],
    ids=["error", "isError"],
)
def test_resultat_en_erreur_sans_repli(table, config_harnais, reponse) -> None:
    nom, arguments, _ = interaction(R001, 0)
    llm = FakeLlm(tour_outils(appel("c1", nom, arguments)), script(mots(3, "s")))
    outils = Repondeur(reponse)
    evenements = repondre(table, config_harnais, llm, outils=outils, mode=ModeFixe("connecte"))
    (resultat,) = [e for e in evenements if isinstance(e, ResultatOutil)]
    attendu = {"error": reponse["error"]} if "error" in reponse else reponse["result"]
    assert resultat.erreur and resultat.resultat == attendu
    assert not any(isinstance(e, Repli) for e in evenements)
    assert llm.appels[1]["tools"] == charger_outils()
    message_outil = llm.appels[1]["messages"][-1]
    assert message_outil["role"] == "tool"
    assert message_outil["content"] == contenu_resultat(reponse)


@pytest.mark.parametrize("brut", [None, [1, 2]], ids=["null", "liste"])
def test_result_non_objet_en_erreur(table, config_harnais, brut) -> None:
    nom, arguments, _ = interaction(R001, 0)
    llm = FakeLlm(tour_outils(appel("c1", nom, arguments)), script(mots(3, "s")))
    outils = Repondeur({"jsonrpc": "2.0", "id": 3, "result": brut})
    evenements = repondre(table, config_harnais, llm, outils=outils, mode=ModeFixe("connecte"))
    (sortie,) = [e for e in evenements if isinstance(e, ResultatOutil)]
    assert sortie.erreur and sortie.resultat == brut
    assert llm.appels[1]["messages"][-1]["content"] == TEXTE_ECHEC


def test_appel_non_conforme_de_l_adaptateur(table, config_harnais) -> None:
    passages = catalogue_fourni(config_harnais)
    motif = mots(3, "motif")
    llm = FakeLlm(
        [AppelNonConforme(nom=None, arguments_bruts="{", motif=motif), Fin(raison="terminee")],
        script(mots(4, "r")),
    )
    outils = Enregistreur(BacASable([R001]))
    evenements = repondre(
        table, config_harnais, llm, passages=passages, outils=outils, mode=ModeFixe("connecte")
    )
    assert evenements[0] == AppelNonConforme(nom=None, arguments_bruts="{", motif=motif)
    assert outils.appels == []
    dernier = llm.appels[1]
    assert dernier["tools"] is None
    assert all(p.url in dernier["messages"][-1]["content"] for p in passages)
    assert types(evenements)[-3:] == ["Sources", "Avertissement", "Fin"]
