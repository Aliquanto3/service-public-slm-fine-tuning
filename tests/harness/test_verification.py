"""Vérification en ligne d'une page officielle (story 13.5, FR-12).

Aucun appel réseau réel (transport `httpx2.MockTransport`), aucun modèle lancé (faux LLM).
Les textes sont des chaînes aléatoires produites par le test (D1.1).
"""

from __future__ import annotations

import secrets
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from typing import Any

import httpx2  # noqa: TID251 (tests : transports factices)
import pytest

from slmsp.app.pont.verification import PontVerification
from slmsp.core.evenements import Fin, Jeton, Source, Sources, Verification, depuis_dict, vers_dict
from slmsp.harness.config import ConfigVerification, charger_config_harnais
from slmsp.harness.modes import ModeFixe
from slmsp.harness.verification import (
    OUTIL_JOURNAL,
    Verificateur,
    charger_prompt,
    choisir_source,
    extraire_texte,
    lire_comparaison,
    verifier,
)
from slmsp.net.client import Passerelle
from slmsp.net.journal import JournalMemoire

HOTE = "www.service-public.gouv.fr"
URL = f"https://{HOTE}/particuliers/vosdroits/F0000"
DATE = datetime(2026, 10, 17, 9, 30, tzinfo=UTC)


def _alea() -> str:
    return f"factice-{secrets.token_hex(6)}"


class FauxLlm:
    """Rend `sortie` en jetons ; mémorise les messages reçus."""

    def __init__(self, sortie: str = "CONCORDANT\nphrase") -> None:
        self.sortie = sortie
        self.appels: list[list[dict[str, Any]]] = []

    def generer(self, messages: Any, *, tools: Any = None, options: Any = None) -> Iterator[Any]:
        self.appels.append(list(messages))
        yield Jeton(texte=self.sortie)
        yield Fin(raison="terminee")

    def compter_tokens(self, messages: Any, tools: Any = None) -> int:
        return 0


def _page(titre: str, corps: str) -> bytes:
    return (
        f"<html><head><title>{titre}</title><script>var x = '{_alea()}';</script>"
        f"<style>p {{ color: red }}</style></head><body><nav>menu</nav>"
        f"<main><h1>{titre}</h1><p>{corps}</p></main><footer>pied</footer></body></html>"
    ).encode()


def _transport(
    traiter: Callable[[httpx2.Request], httpx2.Response],
) -> tuple[httpx2.MockTransport, list[httpx2.Request]]:
    vues: list[httpx2.Request] = []

    def repondre(requete: httpx2.Request) -> httpx2.Response:
        vues.append(requete)
        return traiter(requete)

    return httpx2.MockTransport(repondre), vues


def _html(contenu: bytes, statut: int = 200) -> Callable[[httpx2.Request], httpx2.Response]:
    return lambda _r: httpx2.Response(
        statut, content=contenu, headers={"content-type": "text/html; charset=utf-8"}
    )


def _sources(url: str = URL) -> list[dict[str, Any]]:
    return [
        vers_dict(Source(numero=2, titre="t2", url=url, origine="index")),
        vers_dict(Source(numero=3, titre="t3", url=f"https://{HOTE}/autre", origine="index")),
    ]


def _verifier(
    transport: httpx2.MockTransport,
    mode: str = "connecte",
    llm: FauxLlm | None = None,
    reponse: str = "texte [2] et [3]",
    sources: list[dict[str, Any]] | None = None,
    config: ConfigVerification | None = None,
) -> tuple[list[Any], JournalMemoire, FauxLlm]:
    journal = JournalMemoire()
    passerelle = Passerelle(ModeFixe(mode), journal)
    llm = llm or FauxLlm()
    evenements = verifier(
        reponse,
        sources if sources is not None else _sources(),
        None,
        passerelle,
        llm,
        config=config,
        horloge=lambda: DATE,
        transport_interne=transport,
    )
    return evenements, journal, llm


# --- Choix de la source ------------------------------------------------------------------


def test_choisit_la_source_index_la_mieux_classee_citee() -> None:
    sources = [
        Source(numero=3, titre="a", url="https://x/3", origine="index"),
        Source(numero=1, titre="b", url="https://x/1", origine="index"),
        Source(titre="c", url="https://x/mcp", origine="mcp"),
        {"numero": "illisible"},
    ]
    assert choisir_source("voir [3] puis [1]", sources).url == "https://x/1"  # type: ignore[union-attr]
    assert choisir_source("voir [3]", sources).url == "https://x/3"  # type: ignore[union-attr]
    assert choisir_source("aucun renvoi", sources) is None
    assert choisir_source("[1]", [Source(titre="c", url="u", origine="mcp")]) is None


# --- AC1 : Mode hors ligne ---------------------------------------------------------------


@pytest.mark.parametrize("mode", ["hors-ligne-force", "hors-ligne-detecte"])
def test_mode_hors_ligne_refuse_avant_toute_connexion(mode: str) -> None:
    transport, vues = _transport(_html(_page("t", "c")))
    evenements, journal, llm = _verifier(transport, mode=mode)
    assert vues == [] and llm.appels == []
    (ev,) = evenements
    assert isinstance(ev, Verification) and ev.verdict == "indisponible"
    (entree,) = journal.lister()
    assert entree.statut == "bloquee-mode" and entree.outil == OUTIL_JOURNAL


# --- AC2 : une seule requête, rien de saisi au journal -----------------------------------


def test_seule_requete_un_get_de_l_url_citee_sans_texte_saisi() -> None:
    marqueur = _alea()
    transport, vues = _transport(_html(_page("Titre", f"contenu {_alea()}")))
    evenements, journal, llm = _verifier(transport, reponse=f"{marqueur} selon [2]")
    assert [(r.method, str(r.url)) for r in vues] == [("GET", URL)]
    assert marqueur not in vues[0].url.query.decode() and vues[0].content == b""
    (entree,) = journal.lister()
    assert entree.statut == "envoyee" and entree.methode == "GET" and entree.hote == HOTE
    assert entree.outil == OUTIL_JOURNAL and entree.termes == f'{{"url":"{URL}"}}'
    assert marqueur not in entree.model_dump_json()
    # La réponse ne sert qu'à la comparaison locale.
    assert marqueur in llm.appels[0][1]["content"]
    assert isinstance(evenements[0], Verification) and evenements[0].verdict == "concordant"


# --- AC3 : Liste blanche et redirections -------------------------------------------------


def test_url_hors_liste_blanche_bloquee() -> None:
    transport, vues = _transport(_html(_page("t", "c")))
    evenements, journal, _ = _verifier(
        transport, sources=_sources("https://hors-liste.invalid/page")
    )
    assert vues == []
    assert evenements[0].verdict == "indisponible"
    assert [e.statut for e in journal.lister()] == ["bloquee-liste"]


def test_redirection_hors_liste_blanche_bloquee() -> None:
    def traiter(requete: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(302, headers={"location": "https://ailleurs.invalid/x"})

    transport, vues = _transport(traiter)
    evenements, journal, llm = _verifier(transport)
    assert len(vues) == 1 and llm.appels == []
    assert evenements[0].verdict == "indisponible"
    assert sorted(e.statut for e in journal.lister()) == ["bloquee-liste", "envoyee"]


# --- AC4 : page récupérée ----------------------------------------------------------------


def test_page_concordante_evenement_et_source_ajoutee() -> None:
    titre, corps = _alea(), _alea()
    transport, _ = _transport(_html(_page(titre, corps)))
    evenements, _, llm = _verifier(transport, llm=FauxLlm(f"**Concordant**\n{_alea()}"))
    verif, sources = evenements
    assert isinstance(verif, Verification) and isinstance(sources, Sources)
    assert (verif.url, verif.titre, verif.verdict) == (URL, titre, "concordant")
    assert verif.date_consultation == "2026-10-17T09:30:00+00:00"
    assert sources.sources[0].origine == "verification" and sources.sources[0].url == URL
    contenu = llm.appels[0][1]["content"]
    assert corps in contenu and "var x" not in contenu and "menu" not in contenu
    assert depuis_dict(vers_dict(verif)) == verif


def test_difference_avec_extrait_retrouve_dans_la_page() -> None:
    corps = f"{_alea()} {_alea()}"
    phrase = _alea()
    transport, _ = _transport(_html(_page("t", corps)))
    evenements, _, _ = _verifier(transport, llm=FauxLlm(f"DIFFÉRENCE\n{phrase}\n« {corps} »"))
    assert (evenements[0].verdict, evenements[0].phrase) == ("difference", phrase)
    assert evenements[0].extrait == corps


def test_extrait_absent_de_la_page_ecarte() -> None:
    transport, _ = _transport(_html(_page("t", _alea())))
    evenements, _, _ = _verifier(transport, llm=FauxLlm(f"DIFFERENCE\nx\n{_alea()}"))
    assert evenements[0].verdict == "difference" and evenements[0].extrait is None


def test_sortie_illisible_du_modele_indisponible() -> None:
    transport, _ = _transport(_html(_page("t", "c")))
    evenements, _, _ = _verifier(transport, llm=FauxLlm(_alea()))
    assert [e.verdict for e in evenements] == ["indisponible"]


# --- AC5 : délai, statut, format et taille -----------------------------------------------


def test_delai_depasse_indisponible_sans_relance() -> None:
    def traiter(requete: httpx2.Request) -> httpx2.Response:
        raise httpx2.ReadTimeout("délai", request=requete)

    transport, vues = _transport(traiter)
    evenements, journal, llm = _verifier(transport)
    assert len(vues) == 1 and llm.appels == []
    assert evenements[0].verdict == "indisponible"
    assert [e.statut for e in journal.lister()] == ["echouee"]


@pytest.mark.parametrize(
    "reponse",
    [
        httpx2.Response(404, content=b"<p>x</p>", headers={"content-type": "text/html"}),
        httpx2.Response(200, content=b"%PDF", headers={"content-type": "application/pdf"}),
        httpx2.Response(200, content=b"<p>" + b"a" * 200 + b"</p>",
                        headers={"content-type": "text/html"}),
        httpx2.Response(200, content=b"<script>x</script>", headers={"content-type": "text/html"}),
    ],
    ids=["statut", "format", "taille", "vide"],
)  # fmt: skip
def test_page_inexploitable_indisponible(reponse: httpx2.Response) -> None:
    transport, _ = _transport(lambda _r: reponse)
    config = ConfigVerification(taille_max_octets=100)
    evenements, _, llm = _verifier(transport, config=config)
    assert [e.verdict for e in evenements] == ["indisponible"] and llm.appels == []


def test_desactivee_ou_sans_source_aucune_requete() -> None:
    transport, vues = _transport(_html(_page("t", "c")))
    off, journal, _ = _verifier(transport, config=ConfigVerification(active=False))
    sans, _, _ = _verifier(transport, reponse="sans renvoi")
    assert vues == [] and journal.lister() == []
    assert off[0].verdict == sans[0].verdict == "indisponible"
    assert sans[0].url is None


# --- Extraction, prompt, configuration ---------------------------------------------------


def test_extraction_sans_main_et_entites() -> None:
    page = extraire_texte(
        "<title> A &amp; B </title><body><p>un&nbsp;deux</p><br><div>trois<p>quatre</body>"
    )
    assert page.titre == "A & B"
    assert page.texte.split("\n") == ["un deux", "trois", "quatre"]


def test_lire_comparaison_vide() -> None:
    assert lire_comparaison("", "x").verdict == "indisponible"


def test_prompt_ve_valide_et_config() -> None:
    tache = charger_prompt()
    assert tache.prompt.emplacements == ("texte", "document")
    assert charger_config_harnais().verification == ConfigVerification()


# --- Pont (contrat pour la story 13.6) ---------------------------------------------------


def test_pont_verifier_rend_les_evenements() -> None:
    transport, _ = _transport(_html(_page("t", "c")))
    passerelle = Passerelle(ModeFixe("connecte"), JournalMemoire())
    verificateur = Verificateur(passerelle, FauxLlm())

    def appel(reponse: str, sources: Any) -> list[Any]:
        return verifier(reponse, sources, None, passerelle, verificateur.llm,
                        transport_interne=transport)  # fmt: skip

    pont = PontVerification(appel)
    resultat = pont.appeler("verifier", "voir [2]", _sources())
    assert resultat["ok"] is True
    assert [e["type"] for e in resultat["evenements"]] == ["verification", "sources"]
    assert pont.appeler("verifier", 1, [])["erreur"]["code"] == "requete-invalide"
