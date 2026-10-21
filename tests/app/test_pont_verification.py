"""Domaine `verification` du pont (stories 13.5 et 13.6) : bornes d'entrée, une vérification à la
fois, refus pendant une génération. Le câblage réel est testé dans `test_principal.py`."""

from __future__ import annotations

import threading
from typing import Any

import pytest

from slmsp.app.pont.verification import SOURCES_MAX, PontVerification
from slmsp.core.evenements import Source, Verification, vers_dict
from slmsp.harness.verification import REPONSE_MAX_CARACTERES

URL = "https://www.service-public.gouv.fr/particuliers/vosdroits/F0000"
SOURCE = vers_dict(Source(numero=1, titre="<titre-factice-1>", url=URL, origine="index"))


def _verdict() -> Verification:
    return Verification(
        url=URL,
        titre="t",
        date_consultation="2026-10-17T09:30:00+00:00",
        verdict="indisponible",
        phrase="p",
        extrait=None,
    )


def test_bornes_acceptees_et_refusees_sans_appeler_le_verificateur() -> None:
    appels: list[tuple[str, int]] = []

    def verificateur(reponse: str, sources: Any) -> list[Any]:
        appels.append((reponse, len(sources)))
        return [_verdict()]

    domaine = PontVerification(verificateur)
    pile = "x" * REPONSE_MAX_CARACTERES
    assert domaine.appeler("verifier", pile, [SOURCE] * SOURCES_MAX)["ok"] is True
    assert appels == [(pile, SOURCES_MAX)]
    for args in (
        (pile + "x", [SOURCE]),
        ("<réponse-factice>", [SOURCE] * (SOURCES_MAX + 1)),
        ("<réponse-factice>", ["pas-un-objet"]),
        ("<réponse-factice>", "pas-une-liste"),
        (b"octets", [SOURCE]),
        ("<réponse-factice>",),
    ):
        refus = domaine.appeler("verifier", *args)
        assert refus["ok"] is False and refus["erreur"]["code"] == "requete-invalide"
    assert len(appels) == 1


def test_une_verification_a_la_fois() -> None:
    entree, libre = threading.Event(), threading.Event()
    resultats: list[dict[str, Any]] = []

    def verificateur(reponse: str, sources: Any) -> list[Any]:
        entree.set()
        assert libre.wait(5)
        return [_verdict()]

    domaine = PontVerification(verificateur)
    fil = threading.Thread(
        target=lambda: resultats.append(domaine.appeler("verifier", "<r> [1]", [SOURCE]))
    )
    fil.start()
    assert entree.wait(5)
    second = domaine.appeler("verifier", "<r> [1]", [SOURCE])
    assert second["erreur"]["code"] == "verification-en-cours"
    libre.set()
    fil.join(5)
    assert resultats[0]["ok"] is True
    assert domaine.appeler("verifier", "<r> [1]", [SOURCE])["ok"] is True  # verrou relâché


def test_exception_du_verificateur_relache_le_verrou() -> None:
    etat = {"leve": True}

    def verificateur(reponse: str, sources: Any) -> list[Any]:
        if etat["leve"]:
            raise RuntimeError("boom")
        return []

    domaine = PontVerification(verificateur)
    with pytest.raises(RuntimeError):
        domaine.appeler("verifier", "<r>", [SOURCE])
    etat["leve"] = False
    assert domaine.appeler("verifier", "<r>", [SOURCE])["ok"] is True


def test_refus_tant_qu_une_generation_est_en_cours() -> None:
    occupe = {"v": True}
    appels: list[str] = []
    domaine = PontVerification(
        lambda r, s: appels.append(r) or [_verdict()], occupe=lambda: occupe["v"]
    )
    refus = domaine.appeler("verifier", "<r> [1]", [SOURCE])
    assert refus["ok"] is False and refus["erreur"]["code"] == "generation-en-cours"
    assert appels == []
    occupe["v"] = False
    assert domaine.appeler("verifier", "<r> [1]", [SOURCE])["ok"] is True


def test_modele_repondant_transmis_au_verificateur() -> None:
    """Story 17.4 (revue) : la vérification part vers le modèle qui a répondu."""
    recus: list[Any] = []

    def verificateur(reponse: str, sources: Any, *, modele_repondant: Any = None) -> list[Any]:
        recus.append(modele_repondant)
        return [_verdict()]

    domaine = PontVerification(verificateur)
    assert domaine.appeler("verifier", "<réponse-factice>", [SOURCE], "externe:m/x")["ok"] is True
    assert domaine.appeler("verifier", "<réponse-factice>", [SOURCE], None)["ok"] is True
    assert recus == ["externe:m/x", None]
    for modele in (3, "", "x" * 400):
        refus = domaine.appeler("verifier", "<réponse-factice>", [SOURCE], modele)
        assert refus["erreur"]["code"] == "requete-invalide"
