"""Profils, Liste blanche et Mode (critères 2, 3, 5 et 6 de la story 1.4) et configuration."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from slmsp.core.erreurs import ConfigurationInvalide, HoteBloque
from slmsp.net.config import (
    ConfigListeBlanche,
    ConfigReseau,
    charger_config_reseau,
    charger_liste_blanche,
)
from slmsp.net.profils import est_adresse_ip, evaluer, normaliser_hote

VARIANTES = [
    pytest.param(False, "httpx2", id="sync-httpx2"),
    pytest.param(True, "httpx2", id="async-httpx2"),
    pytest.param(False, "httpx", id="sync-httpx"),
    pytest.param(True, "httpx", id="async-httpx"),
]


def _bloquee(emission, statut: str, *, profil: str, methode: str, hote: str) -> None:
    assert isinstance(emission.erreur, HoteBloque), emission.erreur
    assert emission.erreur.code_sortie == 1
    message = str(emission.erreur)
    assert profil in message and methode in message and hote in message
    assert emission.compteur.appels == 0
    (entree,) = emission.journal.lister()
    assert entree.statut == statut
    assert (entree.profil, entree.methode, entree.hote) == (profil, methode, hote)


def _envoyee(emission, *, hote: str, mode: str | None) -> None:
    assert emission.erreur is None, emission.erreur
    assert emission.reponse.status_code == 200
    assert emission.compteur.appels == 1
    (entree,) = emission.journal.lister()
    assert (entree.statut, entree.hote, entree.mode) == ("envoyee", hote, mode)


# --- Critère 2 : profil assistant et Liste blanche ----------------------------------------


@pytest.mark.parametrize(("asynchrone", "lib"), VARIANTES)
@pytest.mark.parametrize(
    ("methode", "url", "hote"),
    [
        ("GET", "https://www.data.gouv.fr/x", "www.data.gouv.fr"),
        ("POST", "https://MCP.DATA.GOUV.FR./mcp", "mcp.data.gouv.fr"),
        ("GET", "https://www.legifrance.gouv.fr:443/loda", "www.legifrance.gouv.fr"),
        ("DELETE", "https://mcp.data.gouv.fr/mcp", "mcp.data.gouv.fr"),
    ],
)
def test_assistant_liste_blanche(emettre, asynchrone, lib, methode, url, hote) -> None:
    emission = emettre("assistant", methode, url, asynchrone=asynchrone, lib=lib)
    _envoyee(emission, hote=hote, mode="connecte")


@pytest.mark.parametrize(("asynchrone", "lib"), VARIANTES)
@pytest.mark.parametrize(
    ("url", "hote"),
    [
        ("https://mcp.data.gouv.fr.exemple.com/mcp", "mcp.data.gouv.fr.exemple.com"),
        ("https://evil-data.gouv.fr/", "evil-data.gouv.fr"),
        ("https://data.gouv.fr/", "data.gouv.fr"),
        ("https://1.2.3.4/", "1.2.3.4"),
        ("https://[::1]/", "::1"),
        ("http://www.data.gouv.fr/", "www.data.gouv.fr"),
        ("https://www.data.gouv.fr:8443/", "www.data.gouv.fr"),
        ("https://mcp.data.gouv.fr@evil.com/", "evil.com"),
    ],
)
def test_assistant_hors_liste(emettre, asynchrone, lib, url, hote) -> None:
    emission = emettre("assistant", "GET", url, asynchrone=asynchrone, lib=lib)
    _bloquee(emission, "bloquee-liste", profil="assistant", methode="GET", hote=hote)
    assert emission.journal.lister()[0].mode == "connecte"


# --- Critère 3 : Mode ------------------------------------------------------------------------


@pytest.mark.parametrize(("asynchrone", "lib"), VARIANTES)
@pytest.mark.parametrize(
    ("methode", "url", "hote"),
    [
        ("GET", "https://mcp.data.gouv.fr/health", "mcp.data.gouv.fr"),
        ("POST", "https://mcp.data.gouv.fr/mcp", "mcp.data.gouv.fr"),
        ("GET", "https://evil.com/", "evil.com"),
    ],
)
def test_hors_ligne_force(emettre, asynchrone, lib, methode, url, hote) -> None:
    emission = emettre(
        "assistant", methode, url, mode="hors-ligne-force", asynchrone=asynchrone, lib=lib
    )
    _bloquee(emission, "bloquee-mode", profil="assistant", methode=methode, hote=hote)
    assert emission.journal.lister()[0].mode == "hors-ligne-force"


@pytest.mark.parametrize("profil", ["outillage", "aucun"])
def test_hors_ligne_force_tous_profils(emettre, profil) -> None:
    emission = emettre(profil, "GET", "https://huggingface.co/x", mode="hors-ligne-force")
    _bloquee(emission, "bloquee-mode", profil=profil, methode="GET", hote="huggingface.co")


@pytest.mark.parametrize(("asynchrone", "lib"), VARIANTES)
def test_hors_ligne_detecte_sonde_seule(emettre, asynchrone, lib) -> None:
    sonde = emettre(
        "assistant",
        "GET",
        "https://mcp.data.gouv.fr/health",
        mode="hors-ligne-detecte",
        asynchrone=asynchrone,
        lib=lib,
    )
    _envoyee(sonde, hote="mcp.data.gouv.fr", mode="hors-ligne-detecte")
    for methode, url in [
        ("GET", "https://www.data.gouv.fr/x"),
        ("POST", "https://mcp.data.gouv.fr/health"),
        ("GET", "https://mcp.data.gouv.fr/health?x=1"),
        ("GET", "https://mcp.data.gouv.fr/healthz"),
    ]:
        autre = emettre(
            "assistant", methode, url, mode="hors-ligne-detecte", asynchrone=asynchrone, lib=lib
        )
        _bloquee(autre, "bloquee-mode", profil="assistant", methode=methode, hote=autre_hote(url))


def autre_hote(url: str) -> str:
    return url.split("/")[2]


class _ModeQuiLeve:
    def mode_courant(self) -> str:
        raise RuntimeError("sonde en panne")


@pytest.mark.parametrize(("asynchrone", "lib"), VARIANTES)
@pytest.mark.parametrize("source", ["inconnu", None, 3, "leve"])
def test_mode_illisible_ferme(
    doublures, config_reseau, liste_blanche, asynchrone, lib, source
) -> None:
    """Un `ModePort` qui lève ou rend une valeur hors `Mode` bloque la requête."""
    from slmsp.net import client
    from slmsp.net.journal import JournalMemoire

    module = doublures.module_lib(lib)
    if source == "leve":
        mode = _ModeQuiLeve()
    else:
        mode = doublures.ModeDouble()
        mode.mode = source
    compteur = doublures.Compteur(module=module)
    journal = JournalMemoire()
    garde = client(
        "assistant",
        lib,
        asynchrone,
        mode,
        journal,
        module.MockTransport(compteur),
        config=config_reseau,
        liste_blanche=liste_blanche,
    )
    url = "https://mcp.data.gouv.fr/health"
    with pytest.raises(HoteBloque, match="Mode inconnu ou illisible") as info:
        if asynchrone:
            import asyncio

            async def envoyer() -> None:
                async with garde:
                    await garde.get(url)

            asyncio.run(envoyer())
        else:
            with garde:
                garde.get(url)
    if source == "leve":
        assert isinstance(info.value.__cause__, RuntimeError)
    assert compteur.appels == 0
    (entree,) = journal.lister()
    assert (entree.statut, entree.mode, entree.hote) == ("bloquee-mode", None, "mcp.data.gouv.fr")


@pytest.mark.parametrize("mode", ["inconnu", 3])
def test_evaluer_mode_hors_literal(config_reseau, liste_blanche, mode) -> None:
    verdict = evaluer(
        "assistant",
        "GET",
        "https://www.data.gouv.fr/",
        mode=mode,
        config=config_reseau,
        liste_blanche=liste_blanche,
    )
    assert (verdict.statut, verdict.motif) == ("bloquee-mode", "Mode inconnu ou illisible")


# --- Critère 5 : profil outillage -------------------------------------------------------------

LECTURE_OUTILLAGE = [
    "https://huggingface.co/api/models/x",
    "https://cas-bridge.xethub.hf.co/x",
    "https://cdn-lfs.huggingface.co/x",
    "https://pypi.org/simple/x/",
    "https://files.pythonhosted.org/packages/x",
    "https://github.com/ggml-org/llama.cpp/releases",
    "https://objects.githubusercontent.com/x",
    "https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b1",
    "https://download.pytorch.org/whl/cu130",
    "https://www.service-public.gouv.fr/particuliers",
    "https://mcp.data.gouv.fr/health",
]


@pytest.mark.parametrize("methode", ["GET", "HEAD"])
@pytest.mark.parametrize("url", LECTURE_OUTILLAGE)
def test_outillage_lecture(emettre, methode, url) -> None:
    emission = emettre("outillage", methode, url, mode=None)
    _envoyee(emission, hote=autre_hote(url), mode=None)


@pytest.mark.parametrize(("asynchrone", "lib"), VARIANTES)
def test_outillage_page_mistral(emettre, asynchrone, lib) -> None:
    url = "https://legal.mistral.ai/terms/commercial-terms-of-service"
    emission = emettre("outillage", "GET", url, mode=None, asynchrone=asynchrone, lib=lib)
    _envoyee(emission, hote="legal.mistral.ai", mode=None)


@pytest.mark.parametrize(
    "url",
    [
        "https://api.mistral.ai/v1/chat/completions",
        "https://api.anthropic.com/v1/messages",
        "https://mcp.data.gouv.fr/mcp",
    ],
)
def test_outillage_post(emettre, url) -> None:
    emission = emettre("outillage", "POST", url, mode=None, json={"x": 1})
    _envoyee(emission, hote=autre_hote(url), mode=None)


@pytest.mark.parametrize(("asynchrone", "lib"), VARIANTES)
@pytest.mark.parametrize(
    ("methode", "url"),
    [
        ("POST", "https://huggingface.co/api/repos/create"),
        ("GET", "https://api.mistral.ai/v1/models"),
        ("GET", "https://legal.mistral.ai/terms/autre-page"),
        ("HEAD", "https://legal.mistral.ai/terms/commercial-terms-of-service"),
        ("GET", "https://evil-huggingface.co/x"),
        ("GET", "https://huggingface.co.evil.com/x"),
        ("GET", "http://huggingface.co/x"),
        ("GET", "https://1.2.3.4/x"),
        ("POST", "https://www.data.gouv.fr/x"),
        ("DELETE", "https://huggingface.co/x"),
        ("DELETE", "https://api.mistral.ai/v1/files/x"),
        ("DELETE", "https://mcp.data.gouv.fr/mcp"),
        ("DELETE", "https://github.com/x"),
    ],
)
def test_outillage_refus(emettre, asynchrone, lib, methode, url) -> None:
    emission = emettre("outillage", methode, url, mode=None, asynchrone=asynchrone, lib=lib)
    _bloquee(emission, "bloquee-liste", profil="outillage", methode=methode, hote=autre_hote(url))
    assert emission.journal.lister()[0].mode is None


# --- Critère 6 : profil aucun ----------------------------------------------------------------


@pytest.mark.parametrize(("asynchrone", "lib"), VARIANTES)
@pytest.mark.parametrize(
    ("methode", "url"),
    [
        ("GET", "https://www.data.gouv.fr/x"),
        ("GET", "https://huggingface.co/x"),
        ("POST", "https://api.mistral.ai/v1/chat/completions"),
        ("GET", "https://mcp.data.gouv.fr/health"),
    ],
)
def test_aucun(emettre, asynchrone, lib, methode, url) -> None:
    emission = emettre("aucun", methode, url, mode=None, asynchrone=asynchrone, lib=lib)
    _bloquee(emission, "bloquee-liste", profil="aucun", methode=methode, hote=autre_hote(url))


# --- Décision pure ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("brut", "attendu"),
    [
        ("MCP.DATA.GOUV.FR.", "mcp.data.gouv.fr"),
        (" www.Data.gouv.fr ", "www.data.gouv.fr"),
        ("[::1]", "::1"),
    ],
)
def test_normaliser_hote(brut, attendu) -> None:
    assert normaliser_hote(brut) == attendu


@pytest.mark.parametrize(
    ("hote", "ip"),
    [
        ("1.2.3.4", True),
        ("::1", True),
        ("[::ffff:1.2.3.4]", True),
        ("16843009", True),
        ("1.2.3", True),
        ("0x7f000001", True),
        ("www.data.gouv.fr", False),
        ("1password.com", False),
        ("", False),
    ],
)
def test_est_adresse_ip(hote, ip) -> None:
    assert est_adresse_ip(hote) is ip


def test_ordre_mode_avant_liste(config_reseau, liste_blanche) -> None:
    verdict = evaluer(
        "assistant",
        "GET",
        "https://evil.com/",
        mode="hors-ligne-force",
        config=config_reseau,
        liste_blanche=liste_blanche,
    )
    assert verdict.statut == "bloquee-mode"


def test_url_illisible(config_reseau, liste_blanche) -> None:
    verdict = evaluer(
        "assistant",
        "GET",
        "https://exa mple.com:99999/",
        mode="connecte",
        config=config_reseau,
        liste_blanche=liste_blanche,
    )
    assert verdict.statut == "bloquee-liste"


def test_profil_inconnu(config_reseau, liste_blanche) -> None:
    with pytest.raises(ValueError, match="profil inconnu"):
        evaluer(
            "admin",
            "GET",
            "https://www.data.gouv.fr/",
            mode=None,
            config=config_reseau,
            liste_blanche=liste_blanche,
        )


# --- Configuration ----------------------------------------------------------------------------


def test_vrais_fichiers(config_reseau: ConfigReseau, liste_blanche: ConfigListeBlanche) -> None:
    assert len(liste_blanche.hotes) == 8
    assert set(liste_blanche.hotes) == {
        "mcp.data.gouv.fr",
        "www.data.gouv.fr",
        "www.service-public.gouv.fr",
        "www.service-public.fr",
        "www.legifrance.gouv.fr",
        "entreprendre.service-public.gouv.fr",
        "entreprendre.service-public.fr",
        "lannuaire.service-public.fr",
    }
    delais = config_reseau.delais
    assert (delais.defaut, delais.mcp, delais.sonde, delais.local) == (30, 10, 3, 600)
    assert config_reseau.sonde.url == "https://mcp.data.gouv.fr/health"
    assert config_reseau.profils.aucun.regles == []


RESEAU_MINIMAL = """
    [sonde]
    url = "https://sonde.exemple.fr/health"

    [profils.outillage]
    [[profils.outillage.regles]]
    nom = "exemple"
    methodes = ["GET"]
    hotes = ["Depot.Exemple.FR."]
    """


def _ecrire(dossier: Path, contenu: str) -> Path:
    chemin = dossier / "config.toml"
    chemin.write_text(textwrap.dedent(contenu), encoding="utf-8")
    return chemin


def test_fichiers_de_tmp_path(tmp_path: Path) -> None:
    config = charger_config_reseau(_ecrire(tmp_path, RESEAU_MINIMAL))
    assert config.delais.mcp == 10 and config.delais.sonde == 3
    assert config.profils.outillage.regles[0].hotes == ["depot.exemple.fr"]
    blanche = charger_liste_blanche(_ecrire(tmp_path, 'hotes = ["Seul.Exemple.FR."]'))
    assert blanche.hotes == ["seul.exemple.fr"]
    for profil, url, autorise in [
        ("assistant", "https://seul.exemple.fr/x", True),
        ("assistant", "https://www.data.gouv.fr/x", False),
        ("outillage", "https://depot.exemple.fr/x", True),
        ("outillage", "https://huggingface.co/x", False),
    ]:
        verdict = evaluer(profil, "GET", url, mode="connecte", config=config, liste_blanche=blanche)
        assert verdict.autorise is autorise, (profil, url)


@pytest.mark.parametrize(
    "ajout",
    [
        "inconnue = 1\n",
        "[delais]\nmcp = 0\n",
        "[delais]\nmcp = inf\n",
        "[delais]\ndefaut = nan\n",
        "[delais]\nlocal = -1\n",
        '[[profils.outillage.regles]]\nnom = "tld"\nmethodes = ["GET"]\nsuffixes = ["co"]\n',
        '[[profils.outillage.regles]]\nnom = "tld"\nmethodes = ["GET"]\nsuffixes = ["FR."]\n',
        '[[profils.outillage.regles]]\nnom = "ip"\nmethodes = ["GET"]\nhotes = ["1.2.3.4"]\n',
        '[[profils.outillage.regles]]\nnom = "joker"\nmethodes = ["GET"]\nsuffixes = ["*.x"]\n',
        '[[profils.outillage.regles]]\nnom = "m"\nmethodes = ["FETCH"]\nhotes = ["a.fr"]\n',
        '[[profils.outillage.regles]]\nnom = "vide"\nmethodes = ["GET"]\n',
        '[[profils.outillage.regles]]\nnom = "c"\nmethodes = ["GET"]\nhotes = ["a.fr"]\n'
        'chemins = ["sans-barre"]\n',
        '[profils.aucun]\n[[profils.aucun.regles]]\nnom = "r"\nmethodes = ["GET"]\n'
        'hotes = ["a.fr"]\n',
        "[profils.aucun]\nliste_blanche_en_lecture = true\n",
    ],
)
def test_config_reseau_invalide(tmp_path: Path, ajout: str) -> None:
    contenu = textwrap.dedent(RESEAU_MINIMAL) + "\n" + ajout
    if ajout.startswith("inconnue"):
        contenu = ajout + contenu
    with pytest.raises(ConfigurationInvalide):
        charger_config_reseau(_ecrire(tmp_path, contenu))


@pytest.mark.parametrize(
    "sonde", ["http://sonde.exemple.fr/health", "https://1.2.3.4/health", "https://a.fr:8443/"]
)
def test_sonde_invalide(tmp_path: Path, sonde: str) -> None:
    contenu = textwrap.dedent(RESEAU_MINIMAL).replace("https://sonde.exemple.fr/health", sonde)
    with pytest.raises(ConfigurationInvalide):
        charger_config_reseau(_ecrire(tmp_path, contenu))


@pytest.mark.parametrize(
    "contenu",
    [
        'hotes = ["1.2.3.4"]',
        'hotes = ["*.data.gouv.fr"]',
        'hotes = ["[::1]"]',
        "hotes = []",
        'hotes = ["a.fr"]\nautre = 1',
    ],
)
def test_liste_blanche_invalide(tmp_path: Path, contenu: str) -> None:
    with pytest.raises(ConfigurationInvalide):
        charger_liste_blanche(_ecrire(tmp_path, contenu))


def test_config_absente(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide):
        charger_config_reseau(tmp_path / "absent.toml")
