"""Relances bornées du client Mistral sur 429, 5xx transitoires et erreurs de transport :
attentes (`Retry-After`, exponentielle), bornes, budget (une réservation par tentative,
réglée avant la suivante), journal des appels et journal des relances. Faux serveur, aucune
attente réelle (`banc.attentes`)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime
from types import SimpleNamespace
from typing import Any

import httpx2  # noqa: TID251 (tests de l'adaptateur : transport factice)
import pytest

pytest.importorskip("mistralai")

from slmsp.mistral.client import ErreurApiMistral, ReponseMistral  # noqa: E402

JOURNAL_JUGE = "appels-mistral-juge.sqlite"
MESSAGES = [{"role": "user", "content": "<prompt-factice>"}]
COUT_FACTICE = (1000 + 200) / 1_000_000
PIRE_CAS = (2000 + 4000) / 1_000_000  # majoration 1, tarifs 1 $/M


def appeler(client: Any) -> ReponseMistral:
    return client.appeler(
        "juge-second", "session-test", MESSAGES, max_tokens=4000, tokens_entree_estimes=2000
    )


def config(banc: Any, **valeurs: Any) -> Any:
    return banc.config.model_copy(update=valeurs)


def test_429_avec_retry_after_puis_succes(banc: Any) -> None:
    date = format_datetime(datetime.now(UTC) + timedelta(seconds=20), usegmt=True)
    banc.faux.reponses.extend([(429, {"Retry-After": "3"}), (429, {"Retry-After": date})])
    reponse = appeler(banc.client())
    assert reponse.texte == "<verdict-factice>"
    assert len(banc.faux.requetes) == 3
    assert banc.attentes[0] == 3.0 and 15.0 <= banc.attentes[1] <= 20.0
    lignes = banc.lignes_registre()
    assert [(r["etat"], r["montant_reel_eur"]) for r in lignes] == [
        ("regularisee", 0.0),
        ("regularisee", 0.0),
        ("regularisee", pytest.approx(COUT_FACTICE)),
    ]
    journal = banc.lignes_journal(JOURNAL_JUGE)
    assert [(j["statut"], j["statut_http"]) for j in journal] == [
        ("erreur", 429),
        ("erreur", 429),
        ("ok", 200),
    ]
    assert [j["reservation_id"] for j in journal] == [r["id"] for r in lignes]
    assert reponse.reservation_id == lignes[-1]["id"]


def test_429_sans_retry_after_attente_exponentielle_puis_abandon(banc: Any) -> None:
    banc.faux.reponses.extend([429] * 6)
    with pytest.raises(ErreurApiMistral, match=r"HTTP 429 \(juge-second\) après 5 réessai") as e:
        appeler(banc.client())
    assert e.value.statut_http == 429 and e.value.reessais == 5 and e.value.cout_eur == 0
    assert banc.attentes == [2.0, 4.0, 8.0, 16.0, 32.0]  # alea du banc : 1.0
    assert len(banc.faux.requetes) == 6
    lignes = banc.lignes_registre()
    assert len(lignes) == 6
    assert all(r["etat"] == "regularisee" and r["montant_reel_eur"] == 0 for r in lignes)


def test_attente_totale_bornee(banc: Any) -> None:
    banc.faux.reponses.extend([(429, {"Retry-After": "400"})] * 3)
    with pytest.raises(ErreurApiMistral) as erreur:
        appeler(banc.client(config(banc, attente_totale_max=600)))
    assert banc.attentes == [400.0]  # la seconde attente dépasserait 600 s au total
    assert erreur.value.reessais == 1
    assert len(banc.faux.requetes) == 2


def test_reessais_max_configurable(banc: Any) -> None:
    banc.faux.reponses.extend([503] * 3)
    with pytest.raises(ErreurApiMistral) as erreur:
        appeler(banc.client(config(banc, reessais_max=2, attente_base=1, attente_plafond=1)))
    assert erreur.value.reessais == 2 and banc.attentes == [1.0, 1.0]
    assert len(banc.faux.requetes) == 3


@pytest.mark.parametrize("statut", [500, 502, 503, 504])
def test_5xx_transitoire_puis_succes(banc: Any, statut: int) -> None:
    banc.faux.reponses.append(statut)
    appeler(banc.client())
    premier, second = banc.lignes_registre()
    assert premier["etat"] == "regularisee" and premier["montant_reel_eur"] == 0
    assert second["etat"] == "regularisee"
    assert second["montant_reel_eur"] == pytest.approx(COUT_FACTICE)


@pytest.mark.parametrize("statut", [400, 401, 403, 404, 422, 501])
def test_echec_definitif_sans_relance(banc: Any, statut: int) -> None:
    banc.faux.reponses.append(statut)
    with pytest.raises(ErreurApiMistral) as erreur:
        appeler(banc.client())
    assert erreur.value.reessais == 0 and not erreur.value.transitoire
    assert len(banc.faux.requetes) == 1 and banc.attentes == []


def test_appel_bloque_releve_comme_transitoire_puis_borne(banc: Any) -> None:
    banc.faux.reponses.extend([httpx2.ReadTimeout("délai total dépassé (factice)")] * 3)
    with pytest.raises(ErreurApiMistral, match="échec sans réponse HTTP") as erreur:
        appeler(banc.client(config(banc, reessais_max=2)))
    assert erreur.value.statut_http is None and erreur.value.transitoire
    assert erreur.value.reessais == 2
    assert [r["etat"] for r in banc.lignes_registre()] == ["pire-cas"] * 3


def test_erreur_de_transport_puis_succes(banc: Any) -> None:
    banc.faux.reponses.append(httpx2.ConnectError("connexion refusée (factice)"))
    assert appeler(banc.client()).texte == "<verdict-factice>"
    assert len(banc.lignes_registre()) == 2


def test_reservation_liberee_avant_la_suivante(banc: Any) -> None:
    """Un plafond qui ne tient qu'une réservation pire cas : les réessais passent quand
    même, la réservation d'un 429 étant réglée (à 0) avant la suivante."""
    banc.plafond_juge = PIRE_CAS * 1.5
    banc.faux.reponses.extend([429, 429, 429])
    registre = banc.registre()
    appeler(banc.client(registre=registre))
    assert len(banc.lignes_registre()) == 4
    assert all(r["etat"] != "reservee" for r in banc.lignes_registre())
    assert sum(r["montant_reel_eur"] for r in banc.lignes_registre()) == pytest.approx(COUT_FACTICE)


def test_relance_consignee_sans_donnee_sensible(
    banc: Any, doublures: SimpleNamespace, caplog: pytest.LogCaptureFixture
) -> None:
    banc.faux.reponses.append((429, {"Retry-After": "7"}))
    with caplog.at_level(logging.WARNING, logger="slmsp.mistral.client"):
        appeler(banc.client())
    (enregistrement,) = [r for r in caplog.records if r.name == "slmsp.mistral.client"]
    message = enregistrement.getMessage()
    assert "code=429" in message and "attente=7.0s" in message
    assert "source=retry-after" in message and "horodatage=" in message
    assert "réessai=1/5" in message
    for interdit in (doublures.CLE_FACTICE, "<prompt-factice>", "<erreur-factice>"):
        assert interdit not in message


def test_idempotence_inchangee_par_les_lignes_en_erreur(banc: Any) -> None:
    """Les tentatives en échec laissent des lignes `erreur` : seule la ligne `ok` porte la
    réponse réutilisable (les reprises de `generate`/`seed` filtrent sur `statut = ok`)."""
    banc.faux.reponses.extend([429, 503])
    appeler(banc.client())
    statuts = [j["statut"] for j in banc.lignes_journal(JOURNAL_JUGE)]
    assert statuts.count("ok") == 1 and statuts[-1] == "ok"


@pytest.mark.parametrize("valeur", ["0", "-5", "passee"])
def test_retry_after_anormal_porte_a_attente_base(banc: Any, valeur: str) -> None:
    """`Retry-After` nul, négatif ou daté du passé : jamais de relance sans pause."""
    if valeur == "passee":
        valeur = format_datetime(datetime.now(UTC) - timedelta(minutes=5), usegmt=True)
    banc.faux.reponses.extend([(429, {"Retry-After": valeur})] * 2)
    appeler(banc.client(config(banc, attente_base=3, attente_plafond=3)))
    assert banc.attentes == [3.0, 3.0]
    assert len(banc.faux.requetes) == 3


def test_duree_totale_de_l_appel_bornee(banc: Any) -> None:
    """Un réessai n'est tenté que si une tentative complète tient encore dans
    `duree_totale_max_appel`, attentes comprises."""
    instant = [0.0]

    def dormir(attente: float) -> None:
        banc.attentes.append(attente)
        instant[0] += attente

    banc.faux.reponses.extend([(429, {"Retry-After": "50"})] * 4)
    reglage = config(banc, duree_totale_max_appel=300, delai_appel=180)
    with pytest.raises(ErreurApiMistral, match="après 2 réessai") as erreur:
        appeler(banc.client(reglage, dormir=dormir, horloge=lambda: instant[0]))
    assert banc.attentes == [50.0, 50.0]  # 100 + 50 + 180 > 300 : pas de troisième réessai
    assert erreur.value.reessais == 2 and len(banc.faux.requetes) == 3


def test_echeance_globale_transmise_a_la_tentative(banc: Any) -> None:
    """Chaque tentative est ramenée au temps restant de l'appel (délai de lecture imposé)."""
    vus: list[float] = []

    def espion(requete: Any) -> Any:
        vus.append(requete.extensions["timeout"]["read"])
        return banc.faux(requete)

    reglage = config(banc, duree_totale_max_appel=40, delai_appel=180, delai_lecture=180)
    from slmsp.mistral.client import ClientMistral, fabriquer_sdk
    from slmsp.net.journal import JournalMemoire

    sdk = fabriquer_sdk(
        reglage,
        transport_interne=httpx2.MockTransport(espion),
        journal_requetes=JournalMemoire(),
        fichier_env=banc.chemin_env,
    )
    client = ClientMistral(reglage, banc.registre(), sdk, dossier_journaux=banc.dossier)
    appeler(client)
    assert len(vus) == 1 and 39.0 <= vus[0] <= 40.0


def test_reponse_200_illisible_reservation_reglee(
    banc: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Une exception après un 200 (usage illisible) ne laisse aucune réservation ouverte."""
    from slmsp.mistral import client as module_client

    def illisible(reponse: Any) -> Any:
        raise ValueError("usage illisible (factice)")

    monkeypatch.setattr(module_client, "_usage", illisible)
    with pytest.raises(ValueError, match="usage illisible"):
        appeler(banc.client())
    (reservation,) = banc.lignes_registre()
    assert reservation["etat"] == "pire-cas"
    (ligne,) = banc.lignes_journal(JOURNAL_JUGE)
    assert ligne["statut"] == "erreur" and ligne["statut_http"] == 200
    assert ligne["reponse_brute"] is not None


def test_interruption_pendant_l_appel(banc: Any) -> None:
    banc.faux.reponses.append(KeyboardInterrupt())
    with pytest.raises(KeyboardInterrupt):
        appeler(banc.client())
    (reservation,) = banc.lignes_registre()
    assert reservation["etat"] == "pire-cas"  # issue inconnue : pire cas, rien d'ouvert
    assert len(banc.lignes_journal(JOURNAL_JUGE)) == 1


def test_interruption_pendant_l_attente(banc: Any) -> None:
    def interrompre(attente: float) -> None:
        raise KeyboardInterrupt

    banc.faux.reponses.append(429)
    with pytest.raises(KeyboardInterrupt):
        appeler(banc.client(dormir=interrompre))
    (reservation,) = banc.lignes_registre()
    assert reservation["etat"] == "regularisee" and reservation["montant_reel_eur"] == 0
    assert len(banc.faux.requetes) == 1
