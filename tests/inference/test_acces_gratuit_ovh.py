"""Story 17.4b : OVH AI Endpoints en accès gratuit sans clé (aucun réseau réel)."""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import httpx2  # noqa: TID251 (tests : transport factice)
import pytest
from pydantic import SecretStr

from slmsp.app.modele_externe import (
    Observabilite,
    client_externe,
    lecteur_cles,
    valider_entree,
    valider_reglage,
)
from slmsp.app.modele_externe import tester_connexion as connexion_testee
from slmsp.core.evenements import Fin, Jeton
from slmsp.inference.client_openai import ClientOpenAI, EchecAppel
from slmsp.inference.hybride import ClientHybride
from slmsp.inference.mesures import MesureAppel
from slmsp.net.client import Passerelle
from slmsp.net.config import avec_modele_externe, charger_config_reseau, charger_liste_blanche
from slmsp.net.journal import JournalMemoire

OVH = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"
MESSAGES = [{"role": "user", "content": "<question-factice>"}]
ENTREE = {"id": "c3", "preset": "ovh", "actif": True, "acces_gratuit": True}


def sse() -> bytes:
    choix = {"index": 0, "delta": {"content": "<réponse-factice-1>"}}
    fin = {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
    return (
        f"data: {json.dumps({'choices': [choix]})}\n\ndata: {json.dumps(fin)}\n\ndata: [DONE]\n"
    ).encode()


class Faux:
    """File de réponses : `int` (statut), `Exception`, sinon flux SSE ; en-têtes de débit."""

    def __init__(self, *reponses: Any, restant: int | None = 1, reset: int | None = 30) -> None:
        self.reponses = list(reponses)
        self.requetes: list[Any] = []
        self.entetes: dict[str, str] = {}
        if restant is not None:
            self.entetes["ratelimit-remaining"] = str(restant)
        if reset is not None:
            self.entetes["ratelimit-reset"] = str(reset)

    def __call__(self, requete: Any) -> Any:
        self.requetes.append(requete)
        spec = self.reponses.pop(0) if self.reponses else sse()
        if isinstance(spec, Exception):
            raise spec
        if isinstance(spec, int):
            return httpx2.Response(spec, json={"error": {"message": "<x>"}}, headers=self.entetes)
        return httpx2.Response(200, content=spec, headers=self.entetes)


class Mode:
    def mode_courant(self) -> str:
        return "connecte"


class Local:
    taille_contexte = 4096

    def generer(self, messages: Any, *, tools: Any = None, options: Any = None) -> Iterator[Any]:
        return iter([Jeton(texte="<locale-factice>"), Fin(raison="terminee")])

    def compter_tokens(self, messages: Any, tools: Any = None) -> int:
        return 7


class Observateur:
    def __init__(self) -> None:
        self.mesures: list[MesureAppel] = []

    def mesurer(self, mesure: MesureAppel) -> None:
        self.mesures.append(mesure)


class PlafondRefus:
    """Plafond qui refuserait toute réservation : une entrée gratuite n'y touche pas."""

    def __init__(self) -> None:
        self.reservations = 0

    def reserver(self, hote: str, modele: str, montant: float) -> Any:
        self.reservations += 1
        return None

    def regulariser(self, jeton: Any, cout: float) -> None:
        raise AssertionError("régularisation inattendue")


def passerelle() -> Passerelle:
    return Passerelle(
        Mode(),
        JournalMemoire(),
        config=avec_modele_externe(charger_config_reseau(), [OVH]),
        liste_blanche=charger_liste_blanche(),
    )


class Horloge:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t


def gratuit(faux: Faux, horloge: Any = None, **kw: Any) -> ClientOpenAI:
    http = passerelle().client("modele-externe", transport_interne=httpx2.MockTransport(faux))
    options = {"horloge": horloge} if horloge is not None else {}
    return ClientOpenAI(
        http,
        OVH,
        "<modele-factice>",
        None,
        preset_nom="ovh",
        acces_gratuit=True,
        dormir=lambda _s: None,
        **options,
        **kw,
    )


def test_sans_authorization_ni_cle() -> None:
    faux = Faux()
    # même une clé fournie n'est jamais envoyée
    http = passerelle().client("modele-externe", transport_interne=httpx2.MockTransport(faux))
    c = ClientOpenAI(
        http, OVH, "<m>", SecretStr("<cle-factice>"), preset_nom="ovh", acces_gratuit=True
    )
    texte = "".join(e.texte for e in c.generer(MESSAGES) if isinstance(e, Jeton))
    assert texte == "<réponse-factice-1>"
    assert "authorization" not in faux.requetes[0].headers
    assert json.loads(faux.requetes[0].content)["stream"] is True


def test_validation_option_reservee_a_ovh() -> None:
    assert valider_entree(ENTREE)["acces_gratuit"] is True
    assert valider_entree({**ENTREE, "acces_gratuit": False})["acces_gratuit"] is False
    assert valider_entree({"id": "c3", "preset": "ovh"})["acces_gratuit"] is False
    for preset in ("openrouter", "mistral", "generique"):
        with pytest.raises(ValueError, match="preset ovh seulement"):
            valider_entree(
                {
                    "id": "a1",
                    "preset": preset,
                    "url_base": OVH,
                    "modele": "m",
                    "acces_gratuit": True,
                }
            )
    with pytest.raises(ValueError, match="booléen"):
        valider_entree({**ENTREE, "acces_gratuit": "oui"})
    with pytest.raises(ValueError):
        ClientOpenAI(None, "https://openrouter.ai/api/v1", "m", None, acces_gratuit=True)


def test_aucune_cle_lue_pour_une_entree_gratuite() -> None:
    class Coffre:
        def lire(self, *_a: Any, **_k: Any) -> Any:
            raise AssertionError("clé lue")

    assert lecteur_cles(Coffre())(valider_entree(ENTREE)) is None


def test_saut_sans_appel_si_remaining_zero_puis_reprise() -> None:
    horloge = Horloge()
    faux = Faux(restant=0, reset=30)
    c = gratuit(faux, horloge)
    list(c.generer(MESSAGES))  # la réponse annonce 0 requête restante
    assert c.debit_restant == 0 and len(faux.requetes) == 1
    with pytest.raises(EchecAppel) as exc:
        list(c.generer(MESSAGES))
    assert exc.value.code == "debit-limite" and len(faux.requetes) == 1
    horloge.t += 31  # reset écoulé : l'appel repart
    list(c.generer(MESSAGES))
    assert len(faux.requetes) == 2


@pytest.mark.parametrize(
    "reponse",
    [429, httpx2.ConnectError("UNEXPECTED_EOF_WHILE_READING")],
    ids=["http-429", "coupure-tls"],
)
def test_429_et_coupure_tls_motif_debit_limite_sans_relance(reponse: Any) -> None:
    faux = Faux(reponse, restant=0, reset=30)
    attentes: list[float] = []
    c = gratuit(faux)
    c._dormir = attentes.append
    with pytest.raises(EchecAppel) as exc:
        list(c.generer(MESSAGES))
    assert exc.value.code == "debit-limite"
    assert len(faux.requetes) == 1 and attentes == []


def test_429_pose_debit_zero_et_reprise_ratelimit_reset_ou_60_s() -> None:
    horloge = Horloge()
    c = gratuit(Faux(429, restant=None, reset=None), horloge)
    with pytest.raises(EchecAppel):
        list(c.generer(MESSAGES))
    assert c.debit_restant == 0 and c._debit_reprise == horloge.t + 60
    c = gratuit(Faux(429, restant=5, reset=12), horloge)
    with pytest.raises(EchecAppel):
        list(c.generer(MESSAGES))
    assert c.debit_restant == 0 and c._debit_reprise == horloge.t + 12


@pytest.mark.parametrize(
    ("erreur", "code"),
    [
        (httpx2.ConnectError("refus de connexion"), "connexion"),
        (httpx2.ConnectTimeout("t"), "delai"),
    ],
    ids=["refus", "delai"],
)
def test_autres_erreurs_de_connexion_gardent_leur_code(erreur: Exception, code: str) -> None:
    c = gratuit(Faux(erreur))
    with pytest.raises(EchecAppel) as exc:
        list(c.generer(MESSAGES))
    assert exc.value.code == code


def test_hote_hors_preset_refuse_en_acces_gratuit() -> None:
    with pytest.raises(ValueError, match="hôte"):
        valider_entree({**ENTREE, "url_base": "https://api.openai.com/v1"})
    with pytest.raises(ValueError, match="hôte"):
        ClientOpenAI(
            None, "https://api.openai.com/v1", "m", None, preset_nom="ovh", acces_gratuit=True
        )
    assert valider_entree({**ENTREE, "url_base": OVH})["acces_gratuit"] is True


def test_flux_coupe_avant_le_premier_jeton() -> None:
    def vide() -> Iterator[bytes]:
        raise httpx2.ReadError("coupure factice")
        yield b""

    http = passerelle().client(
        "modele-externe",
        transport_interne=httpx2.MockTransport(lambda _r: httpx2.Response(200, content=vide())),
    )
    c = ClientOpenAI(http, OVH, "<m>", None, preset_nom="ovh", acces_gratuit=True)
    with pytest.raises(EchecAppel) as exc:
        list(c.generer(MESSAGES))
    assert exc.value.code == "debit-limite"


def test_cascade_vers_l_entree_suivante_et_local() -> None:
    faux = Faux(429, restant=0, reset=30)
    composite = ClientHybride(Local(), [gratuit(faux)], Mode(), slug_local="slm")
    echange = composite.echange()
    assert list(echange.generer(MESSAGES))[0] == Jeton(texte="<locale-factice>")
    assert echange.echecs == [("ovh", "debit-limite")]
    # deuxième échange : saut sans appel, même motif
    echange = composite.echange()
    list(echange.generer(MESSAGES))
    assert echange.echecs == [("ovh", "debit-limite")] and len(faux.requetes) == 1


def test_cout_zero_plafond_non_bloquant_et_mesures() -> None:
    observateur, plafond = Observateur(), PlafondRefus()
    suivi = Observabilite(observateur=observateur, plafond=plafond, tarif=lambda _e: None)
    entree = valider_entree(ENTREE)
    c = client_externe(
        entree,
        None,
        passerelle(),
        transport_interne=httpx2.MockTransport(Faux()),
        observabilite=suivi,
    )
    assert "".join(e.texte for e in c.generer(MESSAGES) if isinstance(e, Jeton))
    assert plafond.reservations == 0
    (mesure,) = observateur.mesures
    assert mesure.cout_eur == 0.0 and mesure.fournisseur == "ovh-gratuit"
    assert mesure.motif is None and mesure.tokens_sortie > 0
    # sans compteur de dépense (fail-closed pour les autres), l'entrée gratuite répond quand même
    c = client_externe(
        entree,
        None,
        passerelle(),
        transport_interne=httpx2.MockTransport(Faux()),
        observabilite=None,
    )
    assert list(c.generer(MESSAGES))


def test_test_de_connexion_sans_cle_affiche_le_debit() -> None:
    faux = Faux(restant=1)
    entree = valider_reglage([ENTREE])[0]
    r = connexion_testee(
        entree,
        None,
        passerelle(),
        transport_interne=httpx2.MockTransport(faux),
        observabilite=None,
    )
    assert r["reussi"] is True and r["debit_restant"] == 1
    assert "authorization" not in faux.requetes[0].headers
    refus = connexion_testee(
        entree,
        None,
        passerelle(),
        transport_interne=httpx2.MockTransport(Faux(429, restant=0)),
        observabilite=None,
    )
    assert refus["reussi"] is False and refus["motif"] == "debit-limite"
    assert refus["debit_restant"] == 0
