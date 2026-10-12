"""Tâches de rédaction : aucun outil, aucun port externe, avertissement TR (story 4.2, FR-38)."""

from __future__ import annotations

import pytest
from harness_factices import (
    FakeEmbedder,
    FakeLlm,
    FakeVectorStore,
    SpyModePort,
    SpyNetGate,
    SpyToolPort,
    mots,
    script,
    url_factice,
)

from slmsp.core.evenements import Avertissement, Fin, Jeton, Sources
from slmsp.harness.prompts import construire_messages
from slmsp.harness.service import AssistantService

REDACTION = ("CR", "LC", "CO", "RE", "CT", "NR", "TR")


def instance(table, config, llm):
    gate = SpyNetGate()
    ports = {
        "embedder": FakeEmbedder(),
        "store": FakeVectorStore(),
        "outils": SpyToolPort(gate),
        "mode": SpyModePort(),
        "gate": gate,
    }
    service = AssistantService(
        llm,
        ports["embedder"],
        ports["store"],
        ports["outils"],
        ports["mode"],
        config,
        taches=table,
    )
    return service, ports


@pytest.mark.parametrize("code", REDACTION)
def test_redaction_sans_outil_ni_port_externe(table, config_harnais, code) -> None:
    texte = mots(10, f"sortie-{code}")
    llm = FakeLlm(script(texte))
    service, ports = instance(table, config_harnais, llm)
    colle = mots(30, f"colle-{code}")
    evenements = list(service.repondre(code, [{"role": "user", "content": colle}]))

    assert llm.appels[0]["tools"] is None
    assert ports["outils"].appels == [] and ports["mode"].appels == []
    assert ports["gate"].appels == []
    assert ports["embedder"].textes == [] and ports["store"].appels == []
    assert not any(isinstance(e, Sources) for e in evenements)
    alertes = [e for e in evenements if isinstance(e, Avertissement)]
    assert all(a.code != "avis-juridique" for a in alertes)

    types = [type(e) for e in evenements]
    nb_jetons = types.count(Jeton)
    attendu = [Avertissement] if code == "TR" else []
    assert types == [Jeton] * nb_jetons + attendu + [Fin]
    assert "".join(e.texte for e in evenements[:nb_jetons]) == texte
    assert evenements[-1].urls_inventees == []


def test_avertissement_traduction(table, config_harnais) -> None:
    llm = FakeLlm(script(mots(5, "tr")))
    service, _ = instance(table, config_harnais, llm)
    evenements = list(service.repondre("TR", [{"role": "user", "content": mots(9, "src")}]))
    assert evenements[-2] == Avertissement(
        code="traduction-automatique", message="Traduction automatique, à vérifier."
    )


def test_tr_entree_objet_complete(table, config_harnais) -> None:
    llm = FakeLlm(script(mots(5, "tr")))
    service, _ = instance(table, config_harnais, llm)
    entree = {"langue_source": "fr", "langue_cible": "en", "texte": mots(12, "a-traduire")}
    list(
        service.repondre(
            "TR", [{"role": "user", "content": entree["texte"]}], options={"entree": entree}
        )
    )
    assert llm.appels[0]["messages"] == construire_messages(table.tache("TR"), entree)


def test_nr_entree_texte(table, config_harnais) -> None:
    llm = FakeLlm(script(mots(5, "nr")))
    service, _ = instance(table, config_harnais, llm)
    demande = mots(7, "demande")
    list(service.repondre("NR", [{"role": "user", "content": demande}]))
    assert llm.appels[0]["messages"] == construire_messages(table.tache("NR"), demande)


def test_url_du_texte_colle_non_signalee(table, config_harnais) -> None:
    collee = url_factice("collee")
    inventee = url_factice("inventee")
    llm = FakeLlm(script(f"{mots(4, 'r')} {collee} {mots(2, 's')} {inventee}"))
    service, _ = instance(table, config_harnais, llm)
    colle = f"{mots(10, 'texte')} {collee} {mots(3, 'fin')}"
    evenements = list(service.repondre("LC", [{"role": "user", "content": colle}]))
    assert evenements[-1].urls_inventees == [inventee]


def test_url_de_l_entree_objet_non_signalee(table, config_harnais) -> None:
    connue = url_factice("element")
    llm = FakeLlm(script(f"{mots(4, 'r')} {connue}"))
    service, _ = instance(table, config_harnais, llm)
    entree = {"objet": mots(3, "objet"), "elements_connus": [f"{mots(2, 'e')} {connue}"]}
    evenements = list(
        service.repondre(
            "CT", [{"role": "user", "content": mots(2, "u")}], options={"entree": entree}
        )
    )
    assert evenements[-1].urls_inventees == []
