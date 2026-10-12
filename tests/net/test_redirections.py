"""Redirections : chaque saut est revérifié et journalisé (critère 7 de la story 1.4)."""

from __future__ import annotations

import pytest

from slmsp.core.erreurs import HoteBloque

VARIANTES = [
    pytest.param(False, "httpx2", id="sync-httpx2"),
    pytest.param(True, "httpx2", id="async-httpx2"),
    pytest.param(False, "httpx", id="sync-httpx"),
    pytest.param(True, "httpx", id="async-httpx"),
]


def _chaine(doublures, lib: str, sauts: dict[str, str]):
    """Compteur qui répond 302 vers `sauts[hote]`, 200 sinon."""
    module = doublures.module_lib(lib)

    def repondre(requete):
        cible = sauts.get(requete.url.host)
        if cible is None:
            return module.Response(200, request=requete)
        return module.Response(302, headers={"Location": cible}, request=requete)

    return doublures.Compteur(repondre=repondre, module=module)


@pytest.mark.parametrize(("asynchrone", "lib"), VARIANTES)
def test_saut_vers_hote_non_autorise(emettre, doublures, asynchrone, lib) -> None:
    compteur = _chaine(
        doublures,
        lib,
        {
            "www.service-public.fr": "https://www.service-public.gouv.fr/particuliers",
            "www.service-public.gouv.fr": "https://evil.com/vol",
        },
    )
    emission = emettre(
        "assistant",
        "GET",
        "https://www.service-public.fr/",
        asynchrone=asynchrone,
        lib=lib,
        compteur=compteur,
        follow_redirects=True,
    )
    assert isinstance(emission.erreur, HoteBloque)
    assert "evil.com" in str(emission.erreur)
    assert compteur.appels == 2
    assert [(e.hote, e.statut) for e in reversed(emission.journal.lister())] == [
        ("www.service-public.fr", "envoyee"),
        ("www.service-public.gouv.fr", "envoyee"),
        ("evil.com", "bloquee-liste"),
    ]


@pytest.mark.parametrize(("asynchrone", "lib"), VARIANTES)
def test_saut_vers_http_bloque(emettre, doublures, asynchrone, lib) -> None:
    compteur = _chaine(doublures, lib, {"www.data.gouv.fr": "http://www.data.gouv.fr/x"})
    emission = emettre(
        "assistant",
        "GET",
        "https://www.data.gouv.fr/",
        asynchrone=asynchrone,
        lib=lib,
        compteur=compteur,
        follow_redirects=True,
    )
    assert isinstance(emission.erreur, HoteBloque)
    assert compteur.appels == 1
    assert [e.statut for e in emission.journal.lister()] == ["bloquee-liste", "envoyee"]


@pytest.mark.parametrize(("asynchrone", "lib"), VARIANTES)
def test_sauts_autorises_outillage(emettre, doublures, asynchrone, lib) -> None:
    compteur = _chaine(
        doublures,
        lib,
        {
            "huggingface.co": "https://cas-bridge.xethub.hf.co/x?X-Amz-Signature=secret",
            "cas-bridge.xethub.hf.co": "https://cdn-lfs.huggingface.co/y",
        },
    )
    emission = emettre(
        "outillage",
        "GET",
        "https://huggingface.co/m/resolve/main/model.safetensors",
        mode=None,
        asynchrone=asynchrone,
        lib=lib,
        compteur=compteur,
        follow_redirects=True,
    )
    assert emission.erreur is None
    assert emission.reponse.status_code == 200
    assert compteur.appels == 3
    entrees = list(reversed(emission.journal.lister()))
    assert [(e.hote, e.statut) for e in entrees] == [
        ("huggingface.co", "envoyee"),
        ("cas-bridge.xethub.hf.co", "envoyee"),
        ("cdn-lfs.huggingface.co", "envoyee"),
    ]
    assert all("secret" not in e.model_dump_json() for e in entrees)


@pytest.mark.parametrize(("asynchrone", "lib"), VARIANTES)
def test_saut_bloque_en_mode_force(emettre, doublures, asynchrone, lib) -> None:
    """Le Mode est relu à chaque saut."""
    mode = doublures.ModeDouble("connecte")

    def repondre(requete):
        mode.mode = "hors-ligne-force"
        return doublures.module_lib(lib).Response(
            302, headers={"Location": "https://www.data.gouv.fr/b"}, request=requete
        )

    from slmsp.net import client
    from slmsp.net.journal import JournalMemoire

    module = doublures.module_lib(lib)
    compteur = doublures.Compteur(repondre=repondre, module=module)
    journal = JournalMemoire()
    garde = client(
        "assistant",
        lib,
        asynchrone,
        mode,
        journal,
        module.MockTransport(compteur),
        follow_redirects=True,
    )
    with pytest.raises(HoteBloque):
        if asynchrone:
            import asyncio

            async def envoyer() -> None:
                async with garde:
                    await garde.get("https://www.data.gouv.fr/a")

            asyncio.run(envoyer())
        else:
            with garde:
                garde.get("https://www.data.gouv.fr/a")
    assert compteur.appels == 1
    assert [(e.statut, e.mode) for e in journal.lister()] == [
        ("bloquee-mode", "hors-ligne-force"),
        ("envoyee", "connecte"),
    ]


def test_sans_suivi_des_redirections(emettre, doublures) -> None:
    compteur = _chaine(doublures, "httpx2", {"www.data.gouv.fr": "https://evil.com/"})
    emission = emettre("assistant", "GET", "https://www.data.gouv.fr/", compteur=compteur)
    assert emission.erreur is None
    assert emission.reponse.status_code == 302
    assert compteur.appels == 1
    assert [e.statut for e in emission.journal.lister()] == ["envoyee"]
