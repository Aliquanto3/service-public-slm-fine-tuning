"""Story 17.4 : le Harnais avec le composite hybride (bandeau de secours, coupure, local forcé).

Externe factice (aucun réseau) ; textes aléatoires ou factices (D1).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from harness_factices import (
    FakeEmbedder,
    FakeLlm,
    FakeVectorStore,
    SpyModePort,
    SpyToolPort,
    mots,
    passage,
    script,
)

from slmsp.core.evenements import Avertissement, Erreur, Fin, Jeton
from slmsp.harness.service import (
    CODE_EXTERNE_INDISPONIBLE,
    CODE_EXTERNE_INTERROMPU,
    AssistantService,
)
from slmsp.inference.client_openai import EchecAppel
from slmsp.inference.hybride import ClientHybride


class Externe:
    """`ClientOpenAI` factice : `echec` avant tout évènement, ou `coupe` après un jeton."""

    identifiant = "externe:hote.example/<modele-factice>"
    derniere_duree_ms = 5

    def __init__(self, *, echec: str | None = None, coupe: bool = False) -> None:
        self.echec = echec
        self.coupe = coupe
        self.appels = 0

    def generer(self, messages: Any, *, tools: Any = None, options: Any = None) -> Iterator[Any]:
        self.appels += 1

        def flux() -> Iterator[Any]:
            if self.echec:
                raise EchecAppel(self.echec)
            yield Jeton(texte="<externe-factice>")
            if self.coupe:
                raise EchecAppel("connexion")
            yield Fin(raison="terminee")

        return flux()


class Mode:
    def mode_courant(self) -> str:
        return "connecte"


def service(table: Any, config: Any, externe: Externe) -> tuple[AssistantService, FakeLlm]:
    local = FakeLlm(script(mots(5, "locale")))
    hybride = ClientHybride(local, externe, Mode(), slug_local="slm")  # type: ignore[arg-type]
    instance = AssistantService(
        hybride,
        FakeEmbedder(),
        FakeVectorStore([passage(1, 0.9)]),
        SpyToolPort(),
        SpyModePort(),
        config,
        taches=table,
    )
    return instance, local


QUESTION = [{"role": "user", "content": "<question-factice>"}]


def test_secours_local_avec_bandeau(table: Any, config_harnais: Any) -> None:
    instance, local = service(table, config_harnais, Externe(echec="http-401"))
    flux = instance.repondre("Q", QUESTION)
    evenements = list(flux)
    avertis = [e for e in evenements if getattr(e, "code", None) == CODE_EXTERNE_INDISPONIBLE]
    assert len(avertis) == 1 and isinstance(avertis[0], Avertissement)
    assert "(http-401)" in avertis[0].message and "modèle local" in avertis[0].message
    assert isinstance(evenements[-1], Fin) and local.appels
    assert flux.modele_repondant == "local:slm"


def test_externe_retenu_sans_bandeau(table: Any, config_harnais: Any) -> None:
    instance, local = service(table, config_harnais, Externe())
    flux = instance.repondre("Q", QUESTION)
    evenements = list(flux)
    assert not any(getattr(e, "code", None) == CODE_EXTERNE_INDISPONIBLE for e in evenements)
    assert flux.modele_repondant == "externe:hote.example/<modele-factice>"
    assert not local.appels


def test_coupure_apres_premier_jeton_erreur_dediee(table: Any, config_harnais: Any) -> None:
    instance, local = service(table, config_harnais, Externe(coupe=True))
    evenements = list(instance.repondre("Q", QUESTION))
    assert isinstance(evenements[-1], Erreur)
    assert evenements[-1].code == CODE_EXTERNE_INTERROMPU
    assert not local.appels


def test_forcer_local_retire_l_option(table: Any, config_harnais: Any) -> None:
    externe = Externe()
    instance, local = service(table, config_harnais, externe)
    flux = instance.repondre("Q", QUESTION, {"forcer_local": True})
    list(flux)
    assert externe.appels == 0 and local.appels
    assert "forcer_local" not in (local.appels[0]["options"] or {})
    assert flux.modele_repondant == "local:slm"


def test_sans_hybride_option_ignoree(table: Any, config_harnais: Any) -> None:
    local = FakeLlm(script(mots(5, "locale")))
    instance = AssistantService(
        local, FakeEmbedder(), FakeVectorStore([passage(1, 0.9)]), SpyToolPort(), SpyModePort(),
        config_harnais, taches=table,
    )  # fmt: skip
    flux = instance.repondre("Q", QUESTION, {"forcer_local": True})
    assert not hasattr(flux, "modele_repondant")
    assert isinstance(list(flux)[-1], Fin)
    assert "forcer_local" not in (local.appels[0]["options"] or {})


def test_cascade_bandeau_du_fournisseur_de_secours(table: Any, config_harnais: Any) -> None:
    """Amendement 14 : le premier fournisseur échoue, le second répond ; le bandeau le dit."""
    from types import SimpleNamespace

    premier, second = Externe(echec="http-401"), Externe()
    premier.preset = SimpleNamespace(nom="openrouter")  # type: ignore[attr-defined]
    second.preset = SimpleNamespace(nom="mistral")  # type: ignore[attr-defined]
    local = FakeLlm(script(mots(5, "locale")))
    instance = AssistantService(
        ClientHybride(local, [premier, second], Mode(), slug_local="slm"),  # type: ignore[list-item]
        FakeEmbedder(),
        FakeVectorStore([passage(1, 0.9)]),
        SpyToolPort(),
        SpyModePort(),
        config_harnais,
        taches=table,
    )
    flux = instance.repondre("Q", QUESTION)
    avertis = [e for e in flux if getattr(e, "code", None) == CODE_EXTERNE_INDISPONIBLE]
    assert [a.message for a in avertis] == ["Réponse de mistral en secours (openrouter : http-401)"]
    assert not local.appels


def test_verification_part_vers_le_modele_qui_a_repondu() -> None:
    """Revue 17.4 (amendement 6) : `pour(modele_repondant)` lie la vérification au modèle de
    la réponse, sans nouvelle cascade."""
    import pytest

    from slmsp.harness.verification import Verificateur

    local = FakeLlm(script(mots(3, "locale")))
    premier, second = Externe(echec="http-503"), Externe()
    second.identifiant = "externe:autre.example/<modele-factice>"  # type: ignore[misc]
    hybride = ClientHybride(local, [premier, second], Mode(), slug_local="slm")  # type: ignore[arg-type]
    list(hybride.pour(second.identifiant).generer(QUESTION))
    assert (premier.appels, second.appels) == (0, 1)
    sortie = list(hybride.pour("local:slm").generer(QUESTION))
    assert any(isinstance(e, Jeton) for e in sortie) and premier.appels == 0
    with pytest.raises(EchecAppel):  # fournisseur de la réponse en échec : pas d'autre
        list(hybride.pour(premier.identifiant).generer(QUESTION))
    assert second.appels == 1
    # inconnu : nouvel échange en cascade
    list(hybride.pour("externe:disparu/<modele-factice>").generer(QUESTION))
    assert second.appels == 2

    vus: list[Any] = []
    llm = type("L", (), {"pour": lambda self, m: vus.append(m) or local})()
    verificateur = Verificateur(passerelle=None, llm=llm)  # type: ignore[arg-type]
    verificateur("<réponse-factice>", [], modele_repondant="local:slm")
    assert vus == ["local:slm"]
