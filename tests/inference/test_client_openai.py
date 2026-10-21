"""Story 17.4 : client compatible OpenAI sans budget et composite hybride (secours local).

Aucun appel réel : `httpx2.MockTransport` sous la vraie passerelle (profil `modele-externe`).
Textes factices seulement (D1).
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from typing import Any

import httpx2  # noqa: TID251 (tests : transport factice)
import pytest
from pydantic import SecretStr

from slmsp.core.evenements import Fin, Jeton
from slmsp.inference.client_openai import ClientOpenAI, EchecAppel
from slmsp.inference.hybride import ClientHybride
from slmsp.net.client import Passerelle
from slmsp.net.config import avec_modele_externe, charger_config_reseau, charger_liste_blanche
from slmsp.net.journal import JournalMemoire

CLE = "<cle-factice-secrete>"
OPENROUTER = "https://openrouter.ai/api/v1"
OVH = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"
MISTRAL = "https://api.mistral.ai/v1"


def sse(texte: str = "<réponse-factice-1>", *, raisonnement: bool = False) -> bytes:
    lignes = [": OPENROUTER PROCESSING", ""]
    if raisonnement:
        choix = {"index": 0, "delta": {"reasoning": "<raisonnement-factice>"}}
        lignes += [f"data: {json.dumps({'choices': [choix]})}", ""]
    for morceau in (texte[:4], texte[4:]):
        choix = {"index": 0, "delta": {"content": morceau}}
        lignes += [f"data: {json.dumps({'choices': [choix]})}", ""]
    fin = {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
    lignes += [f"data: {json.dumps(fin)}", "", "data: [DONE]", ""]
    return "\n".join(lignes).encode("utf-8")


class Faux:
    """File de réponses : `int` (statut), `Exception` (levée), `"coupe"`, sinon flux SSE."""

    def __init__(self, *reponses: Any) -> None:
        self.reponses = list(reponses)
        self.requetes: list[Any] = []

    def corps(self) -> list[dict[str, Any]]:
        return [json.loads(r.content) for r in self.requetes]

    def __call__(self, requete: Any) -> Any:
        self.requetes.append(requete)
        spec = self.reponses.pop(0) if self.reponses else sse()
        if isinstance(spec, Exception):
            raise spec
        if isinstance(spec, int):
            return httpx2.Response(spec, json={"error": {"message": "<corps-erreur-factice>"}})
        if spec == "coupe":

            def flux() -> Iterator[bytes]:
                choix = {"index": 0, "delta": {"content": "<début-factice>"}}
                yield f"data: {json.dumps({'choices': [choix]})}\n\n".encode()
                raise httpx2.ReadError("coupure factice")

            return httpx2.Response(200, content=flux())
        return httpx2.Response(200, content=spec)


class Mode:
    def __init__(self, valeur: str = "connecte") -> None:
        self.valeur = valeur

    def mode_courant(self) -> str:
        return self.valeur


class Local:
    taille_contexte = 4096

    def __init__(self) -> None:
        self.appels = 0

    def generer(self, messages: Any, *, tools: Any = None, options: Any = None) -> Iterator[Any]:
        self.appels += 1
        return iter([Jeton(texte="<locale-factice>"), Fin(raison="terminee")])

    def compter_tokens(self, messages: Any, tools: Any = None) -> int:
        return 7


def client(
    faux: Faux,
    url: str = OPENROUTER,
    *,
    cle: str | None = CLE,
    mode: Mode | None = None,
    journal: JournalMemoire | None = None,
    parametres: dict[str, Any] | None = None,
    preset: str | None = None,
) -> ClientOpenAI:
    passerelle = Passerelle(
        mode or Mode(),
        journal if journal is not None else JournalMemoire(),
        config=avec_modele_externe(charger_config_reseau(), [OPENROUTER, MISTRAL, OVH]),
        liste_blanche=charger_liste_blanche(),
    )
    http = passerelle.client("modele-externe", transport_interne=httpx2.MockTransport(faux))
    return ClientOpenAI(
        http,
        url,
        "<modele-factice>",
        None if cle is None else SecretStr(cle),
        preset_nom=preset,
        parametres_supplementaires=parametres,
        dormir=lambda _s: None,
    )


MESSAGES = [{"role": "user", "content": "<question-factice>"}]


def test_corps_openrouter_et_hote_generique() -> None:
    faux = Faux()
    list(client(faux).generer(MESSAGES, options={"max_tokens": 9, "chat_template_kwargs": {}}))
    corps = faux.corps()[0]
    assert corps["provider"] == {"data_collection": "deny", "require_parameters": True}
    assert corps["reasoning"] == {"enabled": False}
    assert corps["max_tokens"] == 9 and corps["stream"] is True
    assert "chat_template_kwargs" not in corps
    assert faux.requetes[0].headers["Authorization"] == f"Bearer {CLE}"

    faux = Faux()
    c = client(faux, OVH, parametres={"reasoning_effort": "low", "provider": {"x": 1}})
    list(c.generer(MESSAGES, options={"temperature": 0.1}))
    corps = faux.corps()[0]
    assert "reasoning" not in corps and "chat_template_kwargs" not in corps
    assert corps["reasoning_effort"] == "low" and corps["temperature"] == 0.1
    # un paramètre supplémentaire ne lève pas le refus de collecte imposé sur OpenRouter
    faux = Faux()
    c = client(faux, parametres={"provider": {"data_collection": "allow"}}, preset="generique")
    list(c.generer(MESSAGES))
    assert faux.corps()[0]["provider"]["data_collection"] == "deny"
    with pytest.raises(ValueError, match="generique"):
        client(Faux(), OVH, parametres={"reasoning_effort": "low"}, preset="ovh")


OPTIONS = {"temperature": 0.2, "seed": 7, "top_k": 20, "top_p": 0.9, "max_tokens": 5}


@pytest.mark.parametrize(
    ("preset", "url", "present", "absent"),
    [
        ("openrouter", OPENROUTER, {"seed": 7, "top_k": 20}, {"random_seed"}),
        ("mistral", MISTRAL, {"random_seed": 7}, {"seed", "top_k", "provider", "reasoning"}),
        ("ovh", OVH, {}, {"seed", "random_seed", "top_k", "provider", "reasoning"}),
        ("generique", OVH, {}, {"seed", "random_seed", "top_k", "provider", "reasoning"}),
    ],
)
def test_corps_par_preset(preset: str, url: str, present: dict[str, Any], absent: set[str]) -> None:
    faux = Faux()
    list(client(faux, url, preset=preset).generer(MESSAGES, options=OPTIONS))
    corps = faux.corps()[0]
    assert {k: corps[k] for k in present} == present
    assert not absent & set(corps)
    assert corps["temperature"] == 0.2 and corps["top_p"] == 0.9 and corps["max_tokens"] == 5
    assert ("provider" in corps) is (preset == "openrouter")


def test_raisonnement_ignore_a_l_affichage() -> None:
    evenements = list(client(Faux(sse(raisonnement=True)), OVH).generer(MESSAGES))
    texte = "".join(e.texte for e in evenements if isinstance(e, Jeton))
    assert texte == "<réponse-factice-1>"
    assert isinstance(evenements[-1], Fin)


@pytest.mark.parametrize(
    ("reponses", "motif"),
    [
        ((401,), "http-401"),
        ((500, 500), "http-500"),
        ((httpx2.ConnectError("refus factice"),), "connexion"),
        ((httpx2.ReadTimeout("délai factice"),), "delai"),
    ],
)
def test_echec_code_court_sans_corps(reponses: tuple[Any, ...], motif: str) -> None:
    with pytest.raises(EchecAppel) as exc:
        list(client(Faux(*reponses)).generer(MESSAGES))
    assert exc.value.code == motif
    assert "<corps-erreur-factice>" not in str(exc.value) and CLE not in str(exc.value)


def test_cle_absente_aucune_requete() -> None:
    faux = Faux()
    with pytest.raises(EchecAppel, match="cle-absente"):
        list(client(faux, cle=None).generer(MESSAGES))
    assert faux.requetes == []


def test_url_http_refusee() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        ClientOpenAI(None, "http://openrouter.ai/api/v1", "m", None)
    with pytest.raises(ValueError, match="identifiants"):
        ClientOpenAI(None, "https://a:b@openrouter.ai/api/v1", "m", None)


# --- Composite hybride ----------------------------------------------------------------------


def hybride(faux: Faux, mode: Mode | None = None, **kw: Any) -> tuple[ClientHybride, Local]:
    local = Local()
    mode = mode or Mode()
    return ClientHybride(local, client(faux, mode=mode, **kw), mode, slug_local="slm"), local


@pytest.mark.parametrize(
    ("reponses", "motif"),
    [
        ((httpx2.ConnectError("x"),), "connexion"),
        ((401,), "http-401"),
        ((500, 500), "http-500"),
        ((httpx2.ReadTimeout("x"),), "delai"),
    ],
)
def test_secours_local_avant_premier_jeton(
    reponses: tuple[Any, ...], motif: str, caplog: pytest.LogCaptureFixture
) -> None:
    composite, local = hybride(Faux(*reponses))
    echange = composite.echange()
    with caplog.at_level(logging.INFO):
        evenements = list(echange.generer(MESSAGES))
    assert evenements[0] == Jeton(texte="<locale-factice>")
    assert echange.motif_secours == motif and echange.modele_repondant == "local:slm"
    assert local.appels == 1
    assert CLE not in caplog.text and "<question-factice>" not in caplog.text
    # tous les appels suivants de l'échange restent en local
    list(echange.generer(MESSAGES))
    assert local.appels == 2


def test_cle_absente_secours() -> None:
    composite, _ = hybride(Faux(), cle=None)
    echange = composite.echange()
    list(echange.generer(MESSAGES))
    assert echange.motif_secours == "cle-absente"


@pytest.mark.parametrize("valeur", ["hors-ligne-force", "hors-ligne-detecte"])
def test_hors_ligne_aucun_appel_externe(valeur: str) -> None:
    faux = Faux()
    composite, local = hybride(faux, Mode(valeur))
    echange = composite.echange()
    list(echange.generer(MESSAGES))
    assert faux.requetes == [] and local.appels == 1
    assert echange.motif_secours == "hors-ligne"


def test_externe_retenu_puis_coupure_leve() -> None:
    faux = Faux(sse(), "coupe")
    journal = JournalMemoire()
    composite, local = hybride(faux, journal=journal)
    echange = composite.echange()
    assert any(isinstance(e, Jeton) for e in echange.generer(MESSAGES))
    assert echange.modele_repondant == "externe:openrouter/<modele-factice>"
    with pytest.raises(EchecAppel):
        list(echange.generer(MESSAGES))
    assert local.appels == 0
    entrees = journal.lister()
    assert {e.profil for e in entrees} == {"modele-externe"}
    assert all(e.termes is None for e in entrees)


def test_coupure_apres_premier_jeton_du_premier_appel() -> None:
    composite, local = hybride(Faux("coupe"))
    echange = composite.echange()
    flux = echange.generer(MESSAGES)
    assert next(flux) == Jeton(texte="<début-factice>")
    with pytest.raises(EchecAppel):
        list(flux)
    assert local.appels == 0 and echange.externe_utilise


def test_forcer_local_et_contexte_local() -> None:
    faux = Faux()
    composite, local = hybride(faux)
    echange = composite.echange(forcer_local=True)
    list(echange.generer(MESSAGES))
    assert faux.requetes == [] and local.appels == 1
    assert echange.taille_contexte == 4096 and echange.compter_tokens(MESSAGES) == 7


# --- Cascade (amendement 14) ----------------------------------------------------------------


def cascade(*faux: Faux) -> tuple[ClientHybride, Local]:
    local = Local()
    mode = Mode()
    presets = (("openrouter", OPENROUTER), ("mistral", MISTRAL))
    externes = [
        client(f, url, mode=mode, preset=nom) for f, (nom, url) in zip(faux, presets, strict=True)
    ]
    return ClientHybride(local, externes, mode, slug_local="slm"), local


def test_cascade_premier_401_second_repond() -> None:
    premier, second = Faux(401), Faux()
    composite, local = cascade(premier, second)
    echange = composite.echange()
    evenements = list(echange.generer(MESSAGES))
    texte = "".join(e.texte for e in evenements if isinstance(e, Jeton))
    assert texte == "<réponse-factice-1>" and local.appels == 0
    assert echange.modele_repondant == "externe:mistral/<modele-factice>"
    assert echange.echecs == [("openrouter", "http-401")]
    assert echange.bandeau == "Réponse de mistral en secours (openrouter : http-401)"
    # le fournisseur retenu sert les appels suivants de l'échange
    list(echange.generer(MESSAGES))
    assert len(premier.requetes) == 1 and len(second.requetes) == 2


def test_cascade_tous_en_echec_local() -> None:
    composite, local = cascade(Faux(401), Faux(httpx2.ConnectError("x")))
    echange = composite.echange()
    assert list(echange.generer(MESSAGES))[0] == Jeton(texte="<locale-factice>")
    assert echange.modele_repondant == "local:slm" and local.appels == 1
    assert echange.motif_secours == "openrouter : http-401 ; mistral : connexion"
    assert echange.bandeau == (
        "Modèle externe indisponible (openrouter : http-401 ; mistral : connexion) :"
        " réponse du modèle local"
    )
