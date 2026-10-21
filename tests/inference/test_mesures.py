"""Story 17.6 : mesure de chaque appel LLM et plafond de dépense dans `ClientOpenAI`.

Aucun appel réel : `httpx2.MockTransport` sous la vraie passerelle. Textes factices (D1).
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import httpx2  # noqa: TID251 (tests : transport factice)
import pytest
from pydantic import SecretStr

from slmsp.core.evenements import Fin, Jeton
from slmsp.inference.client import ClientLlama
from slmsp.inference.client_openai import ClientOpenAI, EchecAppel, valider_parametres
from slmsp.inference.fournisseurs import PRESETS, ajouts_requete
from slmsp.inference.hybride import ClientHybride
from slmsp.inference.mesures import MesureAppel, Tarif, contexte_mesure
from slmsp.net.client import Passerelle
from slmsp.net.config import avec_modele_externe, charger_config_reseau, charger_liste_blanche
from slmsp.net.journal import JournalMemoire

OVH = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1"
MESSAGES = [{"role": "user", "content": "<question-factice>"}]
TARIF = Tarif(1.0, 2.0)  # € par million de tokens


def sse(texte: str = "<réponse-factice-1>", usage: dict[str, int] | None = None) -> bytes:
    lignes = []
    for morceau in (texte[:4], texte[4:]):
        choix = {"index": 0, "delta": {"content": morceau}}
        lignes += [f"data: {json.dumps({'choices': [choix]})}", ""]
    fin: dict[str, Any] = {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
    if usage is not None:
        fin["usage"] = usage
    lignes += [f"data: {json.dumps(fin)}", "", "data: [DONE]", ""]
    return "\n".join(lignes).encode("utf-8")


class Faux:
    def __init__(self, *reponses: Any) -> None:
        self.reponses = list(reponses)
        self.requetes: list[Any] = []

    def __call__(self, requete: Any) -> Any:
        self.requetes.append(requete)
        spec = self.reponses.pop(0) if self.reponses else sse()
        if isinstance(spec, int):
            return httpx2.Response(spec, json={"error": {"message": "<erreur-factice>"}})
        return httpx2.Response(200, content=spec)


class Observateur:
    def __init__(self) -> None:
        self.mesures: list[MesureAppel] = []

    def mesurer(self, mesure: MesureAppel) -> None:
        self.mesures.append(mesure)


class Plafond:
    """Plafond en mémoire : `cumul` et `plafond` en euros."""

    def __init__(self, plafond: float) -> None:
        self.plafond = plafond
        self.cumul = 0.0
        self.reservations: list[float] = []

    def reserver(self, hote: str, modele: str, montant: float) -> Any:
        if self.cumul + montant > self.plafond:
            return None
        self.cumul += montant
        self.reservations.append(montant)
        return montant

    def regulariser(self, jeton: Any, cout: float) -> None:
        self.cumul += cout - jeton


def client(faux: Faux, **options: Any) -> ClientOpenAI:
    passerelle = Passerelle(
        type("Mode", (), {"mode_courant": lambda self: "connecte"})(),
        JournalMemoire(),
        config=avec_modele_externe(charger_config_reseau(), [OVH]),
        liste_blanche=charger_liste_blanche(),
    )
    http = passerelle.client("modele-externe", transport_interne=httpx2.MockTransport(faux))
    return ClientOpenAI(
        http,
        OVH,
        "Qwen3.6-27B",
        SecretStr("<cle-factice>"),
        preset_nom="ovh",
        dormir=lambda _s: None,
        **options,
    )


def test_usage_present_mesure_cout_et_contexte() -> None:
    obs = Observateur()
    c = client(Faux(sse(usage={"prompt_tokens": 1000, "completion_tokens": 500})), observateur=obs)
    with contexte_mesure(echange="<e1>", tache="Q"):
        evenements = list(c.generer(MESSAGES))
    assert isinstance(evenements[-1], Fin)
    (m,) = obs.mesures
    assert (m.tokens_entree, m.tokens_sortie, m.estime, m.interrompu) == (1000, 500, False, False)
    assert (m.echange, m.tache, m.fournisseur, m.hote) == ("<e1>", "Q", "ovh", c.hote)
    assert m.cout_eur is None  # aucun tarif fourni
    c2 = client(Faux(sse(usage={"prompt_tokens": 1000, "completion_tokens": 500})))
    c2.observateur, c2.tarif = obs, TARIF
    list(c2.generer(MESSAGES))
    assert obs.mesures[-1].cout_eur == pytest.approx((1000 * 1.0 + 500 * 2.0) / 1e6)


def test_usage_absent_estime() -> None:
    obs = Observateur()
    list(client(Faux(sse("<abcdef>")), observateur=obs, tarif=TARIF).generer(MESSAGES))
    (m,) = obs.mesures
    assert m.estime and m.tokens_sortie == 4  # 8 caractères ÷ 2,5, arrondi au-dessus
    assert m.tokens_entree > 0 and m.cout_eur is not None


def test_usage_absent_raisonnement_compte() -> None:
    """Revue 17.6 : le raisonnement (jamais émis) compte dans l'estimation de la sortie."""
    raisonnement = {"index": 0, "delta": {"reasoning": "<pensee-12>"}}
    contenu = {"index": 0, "delta": {"reasoning_content": "<p2>", "content": "<abcdef>"}}
    fin = {"choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
    corps = "\n\n".join(
        f"data: {json.dumps(m)}" for m in ({"choices": [raisonnement]}, {"choices": [contenu]}, fin)
    )
    obs = Observateur()
    faux = Faux((corps + "\n\ndata: [DONE]\n\n").encode("utf-8"))
    list(client(faux, observateur=obs, tarif=TARIF).generer(MESSAGES))
    (m,) = obs.mesures
    # 11 + 4 caractères de raisonnement + 8 de contenu = 23 ÷ 2,5 = 9,2 -> 10
    assert m.estime and m.tokens_sortie == 10


def test_mesure_ecrite_avant_fin_et_flux_interrompu() -> None:
    obs = Observateur()
    flux = client(Faux(), observateur=obs).generer(MESSAGES)
    for e in flux:
        if isinstance(e, Fin):
            assert len(obs.mesures) == 1  # déjà écrite quand `Fin` sort
    obs2 = Observateur()
    flux = client(Faux(), observateur=obs2, tarif=TARIF).generer(MESSAGES)
    assert isinstance(next(flux), Jeton)
    flux.close()  # arrêt par l'Agent
    (m,) = obs2.mesures
    assert m.interrompu and m.estime and m.motif == "interrompu" and m.cout_eur > 0


def test_echec_http_mesure_sans_cout() -> None:
    obs = Observateur()
    with pytest.raises(EchecAppel):
        list(client(Faux(400), observateur=obs, tarif=TARIF).generer(MESSAGES))
    (m,) = obs.mesures
    assert (m.motif, m.tokens_entree, m.cout_eur, m.interrompu) == ("http-400", 0, 0.0, False)


def test_plafond_pire_cas_par_tentative_et_regularisation() -> None:
    plafond = Plafond(1.0)
    c = client(
        Faux(503, sse(usage={"prompt_tokens": 10, "completion_tokens": 5})),
        plafond=plafond,
        tarif=TARIF,
        relances_max=1,
    )
    list(c.generer(MESSAGES, options={"max_tokens": 100}))
    # Deux tentatives : pire cas × 2 puis × 1 ; la première rendue, la seconde régularisée.
    assert len(plafond.reservations) == 2
    assert plafond.reservations[0] == pytest.approx(2 * plafond.reservations[1])
    assert plafond.cumul == pytest.approx((10 * 1.0 + 5 * 2.0) / 1e6)


def test_plafond_atteint_et_tarif_inconnu_sautes() -> None:
    obs = Observateur()
    faux = Faux()
    c = client(faux, plafond=Plafond(0.0), tarif=TARIF, observateur=obs)
    with pytest.raises(EchecAppel) as exc:
        list(c.generer(MESSAGES))
    assert exc.value.code == "plafond-atteint" and faux.requetes == []
    assert obs.mesures[0].motif == "plafond-atteint" and obs.mesures[0].cout_eur == 0.0
    c = client(faux, plafond=Plafond(10.0))
    with pytest.raises(EchecAppel) as exc:
        list(c.generer(MESSAGES))
    assert exc.value.code == "tarif-inconnu" and faux.requetes == []


def test_cascade_plafond_puis_local() -> None:
    class Local:
        taille_contexte = 4096

        def generer(self, *a: Any, **k: Any) -> Iterator[Any]:
            return iter([Jeton(texte="<locale-factice>"), Fin(raison="terminee")])

        def compter_tokens(self, *a: Any) -> int:
            return 1

    externe = client(Faux(), plafond=Plafond(0.0), tarif=TARIF)
    echange = ClientHybride(Local(), [externe], None, slug_local="<slug>").echange()
    textes = [e.texte for e in echange.generer(MESSAGES) if isinstance(e, Jeton)]
    assert textes == ["<locale-factice>"]
    assert echange.motif_secours == "plafond-atteint"


def test_usage_demande_par_preset_et_cles_interdites() -> None:
    assert ajouts_requete(PRESETS["openrouter"], "openrouter.ai", {})["usage"] == {"include": True}
    ovh = ajouts_requete(PRESETS["ovh"], "h", {})
    assert ovh["stream_options"] == {"include_usage": True}
    assert "stream_options" not in ajouts_requete(PRESETS["mistral"], "api.mistral.ai", {})
    assert "usage" not in ajouts_requete(PRESETS["mistral"], "api.mistral.ai", {})
    assert "stream_options" not in ajouts_requete(PRESETS["generique"], "h", {})
    generique = ajouts_requete(PRESETS["generique"], "h", {}, usage_flux=True)
    assert generique["stream_options"] == {"include_usage": True}
    for cle in ("n", "max_tokens", "max_completion_tokens", "max_output_tokens"):
        with pytest.raises(ValueError):
            valider_parametres({cle: 2})


def test_client_llama_mesure_locale() -> None:
    """Le flux local est mesuré à 0 € (usage du serveur, sinon estimation)."""
    llama = ClientLlama.__new__(ClientLlama)
    obs = Observateur()
    llama.observateur, llama.modele_mesure = obs, "<slug>"

    def flux(*_a: Any) -> Iterator[Any]:
        yield Jeton(texte="<abc>")
        yield Fin(raison="terminee", usage={"prompt_tokens": 4, "completion_tokens": 2})

    llama._flux_serveur = flux  # type: ignore[method-assign]
    list(llama._flux({"messages": MESSAGES}, False))
    (m,) = obs.mesures
    assert (m.fournisseur, m.modele, m.tokens_entree, m.tokens_sortie) == ("local", "<slug>", 4, 2)
    assert m.cout_eur == 0.0 and not m.estime


def test_tarif_pire_cas() -> None:
    # 30 caractères -> ÷ 2,5 = 12 tokens -> × 1,25 = 15 ; 100 tokens de sortie ; 2 tentatives.
    assert Tarif(1.0, 2.0).pire_cas(30, 100, 2) == pytest.approx(2 * (15 + 200) / 1e6)
