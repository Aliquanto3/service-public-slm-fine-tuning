"""Lots batch : réservation, taille maximale, collecte et annulation (story 1.5, critère 8).

Modèle factice `m-test` : 0,5 $ par million de tokens en batch, 1 USD = 1 EUR ; une requête
de `max_tokens = 1_000_000` sans entrée coûte donc 0,50 € au pire cas. Aucun appel d'API.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing

import pytest

from slmsp.budget.registre import RegistreBudget
from slmsp.budget.tarifs import UsageTokens
from slmsp.core.erreurs import BudgetEpuise, SlmspError, TarifInconnu

MILLION = 1_000_000


def lot(registre: RegistreBudget, batch_id: str, nb: int, poste="anthropic", sous_poste=None):
    return registre.reserver_lot(batch_id, poste, sous_poste, "m-test", 0, MILLION, nb)


def test_critere_8_taille_max_sous_le_reste(registre) -> None:
    assert registre.taille_max_lot("anthropic", None, "m-test", 0, MILLION) == 20
    assert registre.taille_max_lot("mistral", "juge", "m-test", 0, MILLION) == 10
    registre.reserver("anthropic", None, "m-test", "direct", 0, 3 * MILLION)
    assert registre.taille_max_lot("anthropic", None, "m-test", 0, MILLION) == 14


def test_critere_8_taille_max_avec_marge(config_test) -> None:
    registre = config_test(marge=0.5).ouvrir()
    assert registre.taille_max_lot("anthropic", None, "m-test", 0, MILLION) == 19


def test_critere_8_taille_max_bornee_par_le_poste(config_test, lignes) -> None:
    # mistral 28 € dont 24 € déjà réservés sur generation : 4 € restent au poste, alors
    # que le sous-poste juge en laisse 5 €. Le poste borne donc le lot à 8 requêtes.
    registre = config_test(mistral=28.0).ouvrir()
    registre.reserver("mistral", "generation", "m-test", "direct", 0, 24 * MILLION)
    assert registre.taille_max_lot("mistral", "juge", "m-test", 0, MILLION) == 8
    assert lot(registre, "lot-juge", 10, poste="mistral", sous_poste="juge") == 8
    assert lignes(registre)[-1]["montant_reserve_eur"] == pytest.approx(4.0)


def test_lots_ouverts_toutes_campagnes(config_test) -> None:
    # Les deux campagnes sont inscrites avant le lot : la nouvelle s'ouvre sans refus.
    ancienne = config_test(campagne="ancienne").ouvrir()
    nouvelle = config_test(campagne="nouvelle").ouvrir()
    lot(ancienne, "lot-ancien", 2)
    (ouvert,) = nouvelle.lots_ouverts()
    assert (ouvert.batch_id, ouvert.campagne_id) == ("lot-ancien", "ancienne")


def test_critere_8_reserver_lot_persiste_le_batch_id(registre, lignes) -> None:
    assert lot(registre, "lot-1", 50) == 20
    # Persisté et validé avant le retour : visible d'une autre connexion, avant toute attente.
    with closing(sqlite3.connect(registre.chemin)) as connexion:
        ligne = connexion.execute(
            "SELECT batch_id, mode, nb_requetes, etat, montant_reserve_eur FROM reservations"
        ).fetchone()
    assert ligne[:4] == ("lot-1", "batch", 20, "reservee")
    assert ligne[4] == pytest.approx(10.0)
    (ouvert,) = registre.lots_ouverts()
    assert (ouvert.batch_id, ouvert.nb_requetes, ouvert.poste) == ("lot-1", 20, "anthropic")
    assert ouvert.montant_reserve_eur == pytest.approx(10.0)
    assert ouvert.campagne_id == "campagne-test"
    assert lignes(registre)[0]["batch_id"] == "lot-1"


def test_reserver_lot_sous_la_taille_max(registre) -> None:
    assert lot(registre, "lot-1", 4) == 4
    assert lot(registre, "lot-2", 100) == 16


def test_reserver_lot_au_tarif_batch(registre, lignes) -> None:
    registre.reserver_lot("lot-1", "anthropic", None, "m-test", 1000, 1000, 3)
    (ligne,) = lignes(registre)
    assert ligne["montant_reserve_eur"] == pytest.approx(3 * (1000 * 0.5 + 1000 * 0.5) / MILLION)


def test_reserver_lot_aucune_requete_ne_tient(registre, lignes) -> None:
    lot(registre, "lot-1", 20)
    with pytest.raises(BudgetEpuise, match="lot-2"):
        lot(registre, "lot-2", 1)
    assert len(lignes(registre)) == 1


def test_reserver_lot_sous_poste(registre) -> None:
    assert lot(registre, "lot-juge", 50, poste="mistral", sous_poste="juge") == 10
    with pytest.raises(BudgetEpuise):
        registre.reserver("mistral", "juge", "m-test", "direct", 0, 1)
    assert lot(registre, "lot-gen", 5, poste="mistral", sous_poste="generation") == 5


def test_reserver_lot_batch_id_deja_utilise(registre, lignes) -> None:
    lot(registre, "lot-1", 2)
    with pytest.raises(SlmspError, match="déjà inscrit"):
        lot(registre, "lot-1", 2)
    registre.collecter_lot("lot-1", UsageTokens(10, 10))
    with pytest.raises(SlmspError, match="déjà inscrit"):
        lot(registre, "lot-1", 2)
    assert len(lignes(registre)) == 1


def test_reserver_lot_tarif_batch_inconnu(registre, lignes) -> None:
    with pytest.raises(TarifInconnu):
        registre.reserver_lot("lot-1", "anthropic", None, "m-sans-cache", 0, 10, 1)
    assert lignes(registre) == []


@pytest.mark.parametrize(("batch_id", "nb"), [("", 1), ("  ", 1), ("lot", 0)])
def test_reserver_lot_parametres_invalides(registre, batch_id: str, nb: int) -> None:
    with pytest.raises(ValueError):
        lot(registre, batch_id, nb)


def test_collecter_lot_au_cout_reel(registre, lignes) -> None:
    lot(registre, "lot-1", 10)
    usage = UsageTokens(entree=2 * MILLION, sortie=MILLION, lecture_cache=MILLION)
    cout = registre.collecter_lot("lot-1", usage)
    assert cout == pytest.approx(2 * 0.5 + 0.5 + 0.05)
    (ligne,) = lignes(registre)
    assert (ligne["etat"], ligne["motif"]) == ("regularisee", None)
    assert registre.lots_ouverts() == []
    # 10 € - 1,55 € dépensés = 8,45 € : 16 requêtes de 0,50 €.
    assert registre.taille_max_lot("anthropic", None, "m-test", 0, MILLION) == 16
    with pytest.raises(SlmspError, match="déjà réglée"):
        registre.collecter_lot("lot-1", usage)
    with pytest.raises(SlmspError, match="inconnue"):
        registre.collecter_lot("lot-absent", usage)


def test_annuler_lot_sans_usage_reste_au_pire_cas(registre, lignes) -> None:
    lot(registre, "lot-1", 4)
    assert registre.annuler_lot("lot-1") == pytest.approx(2.0)
    (ligne,) = lignes(registre)
    assert (ligne["etat"], ligne["motif"]) == ("pire-cas", "lot-annule")
    assert registre.lots_ouverts() == []


def test_annuler_lot_avec_usage_partiel(registre, lignes) -> None:
    lot(registre, "lot-1", 4)
    assert registre.annuler_lot("lot-1", UsageTokens(0, MILLION)) == pytest.approx(0.5)
    (ligne,) = lignes(registre)
    assert (ligne["etat"], ligne["motif"]) == ("regularisee", "lot-annule")


def test_lot_non_reglable_comme_reservation_unitaire(registre, lignes) -> None:
    lot(registre, "lot-1", 2)
    identifiant = lignes(registre)[0]["id"]
    with pytest.raises(SlmspError, match="collecter_lot"):
        registre.regulariser(identifiant, UsageTokens(1, 1))
    with pytest.raises(SlmspError, match="collecter_lot"):
        registre.compter_pire_cas(identifiant)


def test_lot_d_un_pid_mort_reste_ouvert(registre, lignes, modifier) -> None:
    lot(registre, "lot-1", 2)
    modifier(registre, "UPDATE reservations SET pid = ?, creation_processus = 1.0", (999_999_999,))
    rouvert = RegistreBudget(registre.config, registre.tarifs)
    assert rouvert.orphelines_regularisees == ()
    assert lignes(rouvert)[0]["etat"] == "reservee"
    assert [ouvert.batch_id for ouvert in rouvert.lots_ouverts()] == ["lot-1"]
    assert rouvert.collecter_lot("lot-1", UsageTokens(10, 10)) > 0


def test_lot_heterogene_reserve_la_somme_des_pires_cas(registre, lignes) -> None:
    # Une requête longue (2 M tokens d'entrée : 1,5 €) et trois courtes (0,5 €) : 3 €, et non
    # 4 x 1,5 € comme avec le maximum du lot.
    tokens = [2 * MILLION, 0, 0, 0]
    assert registre.taille_max_lot("anthropic", None, "m-test", tokens, MILLION) == 4
    assert registre.reserver_lot("lot-h", "anthropic", None, "m-test", tokens, MILLION, 4) == 4
    (ligne,) = lignes(registre)
    assert ligne["montant_reserve_eur"] == pytest.approx(3.0)
    assert ligne["nb_requetes"] == 4


def test_lot_heterogene_prefixe_au_bon_rang(registre, lignes) -> None:
    # Disponible 10 € : 0,5 + 0,5 + 1,5 + 0,5 x 15 = 10,0 € pour 18 requêtes sur 20 ; la
    # 19e (0,5 €) ne tient plus.
    tokens = [0, 0, 2 * MILLION] + [0] * 17
    assert registre.taille_max_lot("anthropic", None, "m-test", tokens, MILLION) == 18
    assert registre.reserver_lot("lot-p", "anthropic", None, "m-test", tokens, MILLION, 20) == 18
    (ligne,) = lignes(registre)
    assert ligne["montant_reserve_eur"] == pytest.approx(10.0)


def test_lot_heterogene_premiere_requete_trop_chere(registre, lignes) -> None:
    # La première requête vaut 10,5 € > 10 € disponibles : le lot est refusé, même si les
    # suivantes tiendraient.
    tokens = [20 * MILLION, 0, 0]
    assert registre.taille_max_lot("anthropic", None, "m-test", tokens, MILLION) == 0
    with pytest.raises(BudgetEpuise, match="10.5000"):
        registre.reserver_lot("lot-x", "anthropic", None, "m-test", tokens, MILLION, 3)
    assert lignes(registre) == []


def test_lot_heterogene_longueur_incoherente(registre) -> None:
    with pytest.raises(ValueError, match="par requête"):
        registre.reserver_lot("lot-y", "anthropic", None, "m-test", [0, 0], MILLION, 3)
