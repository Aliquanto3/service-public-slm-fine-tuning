"""`JugeClaude` contre un faux serveur Anthropic (aucun appel réel) : une ligne de test par
ligne de la matrice I/O de la story 5.4 et par critère d'acceptation."""

from __future__ import annotations

import dataclasses
import json
import subprocess
import sys
from types import SimpleNamespace
from typing import Any

import pytest

pytest.importorskip("anthropic")

import httpx2  # noqa: E402, TID251 (transport factice)

from slmsp.budget.config import charger_tarifs  # noqa: E402
from slmsp.budget.tarifs import UsageTokens, cout_pire_cas, cout_reel  # noqa: E402
from slmsp.core.config import racine_projet  # noqa: E402
from slmsp.core.erreurs import ConfigurationInvalide, SecretManquant  # noqa: E402
from slmsp.judge.cache import RequeteLot, cle_verdict  # noqa: E402
from slmsp.judge.claude import DemandeJugement, fabriquer_client  # noqa: E402
from slmsp.judge.config import charger_juges  # noqa: E402
from slmsp.judge.prompt import (  # noqa: E402
    ItemNonJugeable,
    construire_prompt,
    estimer_tokens_entree,
)
from slmsp.net.config import charger_config_reseau, charger_liste_blanche  # noqa: E402
from slmsp.net.profils import evaluer  # noqa: E402

CLES_REQUETE = {"model", "max_tokens", "messages", "output_config"}


def demandes(doublures: SimpleNamespace, items: dict[str, Any], *ids: str) -> list[Any]:
    return [DemandeJugement(items[i], doublures.sortie_factice()) for i in ids]


def corps_json(banc: Any, motif: str) -> list[dict[str, Any]]:
    return [
        json.loads(corps)
        for (methode, chemin, corps) in banc.faux.requetes
        if f"{methode} {chemin}" == motif
    ]


# --- Configuration ----------------------------------------------------------------------------


def test_config_juges_du_depot() -> None:
    config = charger_juges()
    principal = config.principal
    assert principal.modele == "claude-opus-5-5"
    assert principal.effort == "medium"
    assert principal.mode_appel == "batch"
    assert principal.max_tokens == 6000
    assert (principal.delai_max_lot, principal.intervalle_sondage) == (3600, 60)
    assert (principal.delai_annulation, principal.delai_appel) == (600, 600)
    assert principal.usage_budget == "juge-principal"
    assert principal.chemin_grille().is_file()


def test_config_juges_invalide(tmp_path: Any) -> None:
    chemin = tmp_path / "juges.toml"
    chemin.write_text(
        'schema_version = 1\n[principal]\nmodele = "m"\neffort = "enorme"\n', encoding="utf-8"
    )
    with pytest.raises(ConfigurationInvalide):
        charger_juges(chemin)


def test_import_du_paquet_sans_anthropic() -> None:
    code = (
        "import sys\n"
        "import slmsp.judge, slmsp.judge.config, slmsp.judge.grille, slmsp.judge.prompt\n"
        "import slmsp.judge.cache\n"
        "assert 'anthropic' not in sys.modules, 'anthropic importé'\n"
    )
    subprocess.run([sys.executable, "-c", code], check=True, cwd=racine_projet())


# --- Client -----------------------------------------------------------------------------------


def test_client_profil_outillage_sans_relance(banc: Any, doublures: SimpleNamespace) -> None:
    juge = banc.juge()
    client = juge.client
    assert client.max_retries == 0
    assert client.timeout == 600
    assert str(client.base_url).rstrip("/") == "https://api.anthropic.com"
    # Le client HTTP est celui de la passerelle : un hôte hors règle est refusé.
    with pytest.raises(Exception, match="refusée"):
        client._client.get("https://api.mistral.ai/v1/models")


def test_secret_absent_des_journaux(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    juge = banc.juge(mode_appel="direct")
    juge.juger(demandes(doublures, items, "Q-001"))
    assert banc.faux.requetes
    entrees = banc.journal.lister()
    assert entrees and all(doublures.CLE_FACTICE not in e.model_dump_json() for e in entrees)
    assert all(doublures.CLE_FACTICE.encode() not in corps for corps in banc.faux.corps())


def test_secret_manquant(tmp_path: Any) -> None:
    vide = tmp_path / "vide.env"
    vide.write_text("AUTRE=1\n", encoding="utf-8")
    with pytest.raises(SecretManquant) as erreur:
        fabriquer_client(charger_juges().principal, fichier_env=vide)
    assert "ANTHROPIC_API_KEY" in str(erreur.value)


# --- Matrice : batch nominal ------------------------------------------------------------------


def test_batch_nominal(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    juge = banc.juge()
    rapport = juge.juger(demandes(doublures, items, "Q-001", "LC-001", "CR-001"))

    assert [r.item_id for r in rapport.resultats] == ["Q-001", "LC-001", "CR-001"]
    assert all(r.statut == "juge" and not r.depuis_cache for r in rapport.resultats)
    assert all(r.mode == "batch" and r.verdict is not None for r in rapport.resultats)
    assert banc.faux.compter("POST /v1/messages/batches") == 1
    assert banc.faux.compter("POST /v1/messages") == 0

    # Réservation avant la création ; collecte après.
    evenements = banc.faux.evenements
    reserve = evenements.index(next(e for e in evenements if e[0] == "reserver_lot"))
    cree = evenements.index(("http", "POST /v1/messages/batches"))
    collecte = evenements.index(next(e for e in evenements if e[0] == "collecter_lot"))
    assert reserve < cree < collecte
    lot_id = evenements[reserve][1]
    assert lot_id.startswith("slmsp-juge-") and len(lot_id) == len("slmsp-juge-") + 32

    # `batch_id` Anthropic en base (lot `en_cours`) avant le premier GET.
    assert banc.faux.batch_id_en_base_au_premier_get == {"msgbatch_0001": True}
    (lot,) = banc.lots()
    assert lot["batch_id"] == "msgbatch_0001" and lot["statut"] == "collecte"
    assert lot["lot_id"] == lot_id and lot["soumis_le"]

    # Collecte avec la somme des usages ; trois verdicts en cache.
    (ligne,) = banc.lignes_registre()
    assert ligne["batch_id"] == lot_id and ligne["etat"] == "regularisee"
    assert (ligne["tokens_entree"], ligne["tokens_sortie"]) == (3000, 600)
    assert all(banc.cache.lire(r.cle) is not None for r in rapport.resultats)
    cout_item = cout_reel(banc.registre.tarifs, doublures.MODELE, "batch", UsageTokens(1000, 200))
    assert all(r.cout_eur == pytest.approx(cout_item) for r in rapport.resultats)
    assert rapport.cout_total_eur == pytest.approx(3 * cout_item)
    assert not rapport.budget_epuise


def test_journal_des_appels_par_item(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    juge = banc.juge()
    rapport = juge.juger(demandes(doublures, items, "Q-001", "NR-001"))
    appels = banc.cache.appels()
    assert [a["item_id"] for a in appels] == ["Q-001", "NR-001"]
    cout = cout_reel(banc.registre.tarifs, doublures.MODELE, "batch", UsageTokens(1000, 200))
    for appel, resultat in zip(appels, rapport.resultats, strict=True):
        assert appel["cle"] == resultat.cle
        assert (appel["tokens_entree"], appel["tokens_sortie"]) == doublures.USAGE_FACTICE
        assert appel["cout_eur"] == pytest.approx(cout)
        assert appel["mode"] == "batch" and appel["issue"] == "juge" and appel["lot_id"]
        assert appel["horodatage"]


def test_lot_trop_grand_pour_le_budget(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    """La réservation ne retient qu'une partie du lot ; le reste part dans un lot suivant."""
    config = doublures.config_juge()
    prompt = construire_prompt(items["Q-001"], doublures.sortie_factice(), banc.grille)
    unitaire = cout_pire_cas(
        charger_tarifs(banc.chemin_tarifs),
        doublures.MODELE,
        "batch",
        estimer_tokens_entree(prompt),
        config.max_tokens,
        1.0,
    )
    banc.plafond = unitaire * 1.5
    juge = banc.juge()
    sorties = [doublures.sortie_factice(f"<sortie-factice-{i}>") for i in range(2)]
    rapport = juge.juger([DemandeJugement(items["Q-001"], s) for s in sorties])
    # Un lot d'une requête, collecté au coût réel, libère le budget du lot suivant.
    assert [r.statut for r in rapport.resultats] == ["juge", "juge"]
    assert not rapport.budget_epuise
    lots = corps_json(banc, "POST /v1/messages/batches")
    assert [len(lot["requests"]) for lot in lots] == [1, 1]
    assert [lg["nb_requetes"] for lg in banc.lignes_registre()] == [1, 1]


# --- Matrice : cache plein et doublons --------------------------------------------------------


def test_cache_plein(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    demandees = demandes(doublures, items, "Q-001", "LC-001", "CR-001")
    banc.juge().juger(demandees)
    requetes, lignes = len(banc.faux.requetes), len(banc.lignes_registre())

    rapport = banc.juge().juger(demandees)  # nouveau Juge, même cache et même registre
    assert len(banc.faux.requetes) == requetes
    assert len(banc.lignes_registre()) == lignes
    assert all(r.depuis_cache and r.cout_eur == 0 for r in rapport.resultats)
    assert all(r.statut == "juge" and r.verdict is not None for r in rapport.resultats)
    assert rapport.cout_total_eur == 0


def test_cache_plein_en_direct(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    demandees = demandes(doublures, items, "NR-001")
    banc.juge(mode_appel="direct").juger(demandees)
    requetes, lignes = len(banc.faux.requetes), len(banc.lignes_registre())
    rapport = banc.juge(mode_appel="direct").juger(demandees)
    assert (len(banc.faux.requetes), len(banc.lignes_registre())) == (requetes, lignes)
    assert rapport.resultats[0].depuis_cache


def test_doublon_dans_l_appel(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    juge = banc.juge()
    rapport = juge.juger(demandes(doublures, items, "Q-001", "Q-001"))
    (corps,) = corps_json(banc, "POST /v1/messages/batches")
    assert len(corps["requests"]) == 1
    premier, second = rapport.resultats
    assert_doublon(premier, second)
    assert rapport.cout_total_eur == pytest.approx(sum(r.cout_eur for r in rapport.resultats))


def assert_doublon(premier: Any, second: Any) -> None:
    """Même verdict ; coût et tokens portés par la première occurrence seulement."""
    assert premier.cout_eur > 0 and premier.tokens is not None
    assert second.cout_eur == 0.0 and second.tokens is None
    assert dataclasses.replace(second, cout_eur=premier.cout_eur, tokens=premier.tokens) == premier


def test_doublon_en_direct(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    rapport = banc.juge(mode_appel="direct").juger(demandes(doublures, items, "NR-001", "NR-001"))
    assert banc.faux.compter("POST /v1/messages") == 1
    assert_doublon(*rapport.resultats)
    assert rapport.cout_total_eur == pytest.approx(sum(r.cout_eur for r in rapport.resultats))


# --- Matrice : reprise après un arrêt ---------------------------------------------------------


def test_relance_apres_crash(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.sondages_avant_fin = 2
    banc.horloge.crash_apres = 0  # arrêt pendant la première attente du lot
    demandees = demandes(doublures, items, "Q-001", "RE-001")
    with pytest.raises(doublures.Crash):
        banc.juge().juger(demandees)
    (lot,) = banc.lots()
    assert lot["statut"] == "en_cours" and lot["batch_id"] == "msgbatch_0001"
    assert banc.lignes_registre()[0]["etat"] == "reservee"

    banc.horloge.crash_apres = None
    debut = len(banc.faux.requetes)
    rapport = banc.juge().juger(demandees)
    reprise = banc.faux.chemins()[debut:]
    assert reprise[0] == "GET /v1/messages/batches/msgbatch_0001"  # relu avant tout
    assert "POST /v1/messages/batches" not in reprise
    assert "POST /v1/messages" not in reprise
    assert all(r.statut == "juge" and not r.depuis_cache for r in rapport.resultats)
    assert banc.lots()[0]["statut"] == "collecte"
    assert banc.lignes_registre()[0]["etat"] == "regularisee"


def test_reprise_avant_creation_d_un_lot(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    """Un lot repris qui ne concerne pas les demandes est relu avant le nouveau lot."""
    banc.faux.sondages_avant_fin = 2
    banc.horloge.crash_apres = 0
    with pytest.raises(doublures.Crash):
        banc.juge().juger(demandes(doublures, items, "Q-001"))
    banc.horloge.crash_apres = None
    debut = len(banc.faux.requetes)
    rapport = banc.juge().juger(demandes(doublures, items, "NR-002"))
    reprise = banc.faux.chemins()[debut:]
    assert reprise[0] == "GET /v1/messages/batches/msgbatch_0001"
    assert reprise.index("POST /v1/messages/batches") > reprise.index(
        "GET /v1/messages/batches/msgbatch_0001/results"
    )
    assert rapport.resultats[0].statut == "juge"
    # Le verdict du lot repris est journalisé une fois et en cache.
    assert len([a for a in banc.cache.appels() if a["item_id"] == "Q-001"]) == 1
    sortie = doublures.sortie_factice()
    prompt = construire_prompt(items["Q-001"], sortie, banc.grille)
    cle_q = cle_verdict(items["Q-001"], sortie, prompt, doublures.MODELE, "medium")
    en_cache = banc.cache.lire(cle_q)
    assert en_cache is not None and en_cache.verdict.id == "Q-001"
    # Le coût du lot repris (hors demandes) entre dans le total de l'appel.
    cout = cout_reel(
        banc.registre.tarifs, doublures.MODELE, "batch", UsageTokens(*doublures.USAGE_FACTICE)
    )
    assert rapport.resultats[0].cout_eur == pytest.approx(cout)
    assert rapport.cout_total_eur == pytest.approx(2 * cout)


def test_lot_reserve_non_cree(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    def crash() -> None:
        raise doublures.Crash("arrêt avant la confirmation de création")

    banc.faux.creation = crash
    demandees = demandes(doublures, items, "Q-001", "CT-001")
    with pytest.raises(doublures.Crash):
        banc.juge().juger(demandees)
    (lot,) = banc.lots()
    assert lot["statut"] == "reserve" and lot["batch_id"] is None

    banc.faux.creation = None
    rapport = banc.juge().juger(demandees)
    lots = banc.lots()
    assert [lot["statut"] for lot in lots] == ["abandonne", "collecte"]
    premiere, seconde = banc.lignes_registre()
    assert premiere["batch_id"] == lots[0]["lot_id"]
    assert premiere["etat"] == "pire-cas" and premiere["motif"] == "lot-annule"
    assert seconde["etat"] == "regularisee"
    assert ("annuler_lot", lots[0]["lot_id"]) in banc.faux.evenements
    assert all(r.statut == "juge" for r in rapport.resultats)  # items rejugés
    assert rapport.cout_total_eur > sum(r.cout_eur for r in rapport.resultats)


def test_creation_de_lot_en_erreur(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.creation = lambda: httpx2.Response(500, json={"type": "error"})
    rapport = banc.juge().juger(demandes(doublures, items, "Q-001"))
    (resultat,) = rapport.resultats
    assert resultat.statut == "non-juge" and resultat.motif == "erreur-api"
    assert banc.lots()[0]["statut"] == "abandonne"
    assert banc.lignes_registre()[0]["etat"] == "pire-cas"
    assert banc.faux.compter("POST /v1/messages") == 0


# --- Matrice : délai de lot dépassé -----------------------------------------------------------


def test_delai_de_lot_depasse(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.jamais_fini = True
    banc.faux.reussies_avant_annulation = {"Q-001"}
    juge = banc.juge(delai_max_lot=120, intervalle_sondage=60, delai_annulation=600)
    rapport = juge.juger(demandes(doublures, items, "Q-001", "LC-001", "NR-001"))

    chemins = banc.faux.chemins()
    assert chemins.count("POST /v1/messages/batches/msgbatch_0001/cancel") == 1
    annulation = chemins.index("POST /v1/messages/batches/msgbatch_0001/cancel")
    assert "GET /v1/messages/batches/msgbatch_0001" in chemins[annulation + 1 :]
    assert banc.faux.compter("POST /v1/messages") == 2  # restes en appels directs
    assert [r.statut for r in rapport.resultats] == ["juge", "juge", "juge"]
    assert [r.mode for r in rapport.resultats] == ["batch", "direct", "direct"]

    (lot,) = banc.lots()
    assert lot["statut"] == "annule"
    ligne = next(lg for lg in banc.lignes_registre() if lg["batch_id"] == lot["lot_id"])
    assert ligne["etat"] == "regularisee" and ligne["motif"] == "lot-annule"
    assert (ligne["tokens_entree"], ligne["tokens_sortie"]) == doublures.USAGE_FACTICE
    assert ("annuler_lot", lot["lot_id"]) in banc.faux.evenements
    assert banc.horloge.temps >= 120


def test_annulation_non_confirmee(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.jamais_fini = True
    banc.faux.annulation_confirmee = False
    juge = banc.juge(delai_max_lot=120, intervalle_sondage=60, delai_annulation=120)
    rapport = juge.juger(demandes(doublures, items, "Q-001", "LC-001"))
    assert all(r.statut == "non-juge" and r.motif == "lot-non-annule" for r in rapport.resultats)
    assert banc.faux.compter("POST /v1/messages") == 0
    (lot,) = banc.lots()
    assert lot["statut"] == "en_cours"  # laissé ouvert
    assert banc.lignes_registre()[0]["etat"] == "reservee"

    # Annulation confirmée plus tard : le lot est relu et soldé (annulé, sans réussite),
    # aucun lot neuf n'est créé et les items annulés passent en appels directs.
    banc.faux.annulation_confirmee = True
    rapport = banc.juge(delai_max_lot=120, intervalle_sondage=60).juger(
        demandes(doublures, items, "Q-001", "LC-001")
    )
    assert banc.lots()[0]["statut"] == "annule"
    ligne = banc.lignes_registre()[0]
    assert ligne["etat"] == "regularisee" and ligne["motif"] == "lot-annule"
    assert ligne["montant_reel_eur"] == 0
    assert banc.faux.compter("POST /v1/messages/batches") == 1
    assert [r.mode for r in rapport.resultats] == ["direct", "direct"]
    assert all(r.statut == "juge" for r in rapport.resultats)


# --- Matrice : sorties non conformes ----------------------------------------------------------


def test_sortie_non_conforme_deux_fois_batch(
    banc: Any, doublures: SimpleNamespace, items: Any
) -> None:
    banc.faux.resultats_batch["Q-001"] = {"texte": "pas du JSON"}
    banc.faux.directes["Q-001"] = [{"texte": json.dumps({"id": "Q-001"})}]
    rapport = banc.juge().juger(demandes(doublures, items, "Q-001", "NR-001"))
    q, nr = rapport.resultats
    assert q.statut == "invalide" and q.verdict is not None and q.verdict.invalide
    assert nr.statut == "juge"
    assert banc.faux.compter("POST /v1/messages") == 1  # nouvel essai direct
    assert banc.cache.echecs(q.cle) == 2
    en_cache = banc.cache.lire(q.cle)
    assert en_cache is not None and en_cache.verdict.invalide
    issues = [(a["mode"], a["issue"]) for a in banc.cache.appels() if a["item_id"] == "Q-001"]
    assert issues == [("batch", "non-conforme"), ("direct", "invalide")]
    usage = UsageTokens(*doublures.USAGE_FACTICE)
    tarifs = banc.registre.tarifs
    attendu = cout_reel(tarifs, doublures.MODELE, "batch", usage) + cout_reel(
        tarifs, doublures.MODELE, "direct", usage
    )
    assert q.cout_eur == pytest.approx(attendu)
    assert en_cache.cout_eur == pytest.approx(attendu)
    # Redemandé : invalide depuis le cache, sans appel.
    requetes = len(banc.faux.requetes)
    rapport = banc.juge().juger(demandes(doublures, items, "Q-001"))
    assert rapport.resultats[0].statut == "invalide" and rapport.resultats[0].depuis_cache
    assert len(banc.faux.requetes) == requetes


@pytest.mark.parametrize(
    "mauvaises",
    [
        [{"texte": "{"}, {"texte": "[]"}],
        [{"stop_reason": "refusal"}, {"stop_reason": "max_tokens"}],
        [{"texte": json.dumps({"id": "NR-001", "criteres": {}, "inventions": [], "x": 1})}] * 2,
    ],
    ids=["json-invalide", "refus-et-troncature", "hors-schema"],
)
def test_sortie_non_conforme_deux_fois_direct(
    banc: Any, doublures: SimpleNamespace, items: Any, mauvaises: list[Any]
) -> None:
    banc.faux.directes["NR-001"] = list(mauvaises)
    rapport = banc.juge(mode_appel="direct").juger(demandes(doublures, items, "NR-001"))
    (resultat,) = rapport.resultats
    assert resultat.statut == "invalide" and resultat.mode == "direct"
    assert banc.faux.compter("POST /v1/messages") == 2
    assert banc.cache.echecs(resultat.cle) == 2
    assert [lg["etat"] for lg in banc.lignes_registre()] == ["regularisee", "regularisee"]


def test_sortie_non_conforme_une_fois(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.directes["NR-001"] = [{"texte": "{"}]
    rapport = banc.juge(mode_appel="direct").juger(demandes(doublures, items, "NR-001"))
    (resultat,) = rapport.resultats
    assert resultat.statut == "juge" and not resultat.verdict.invalide
    assert banc.cache.echecs(resultat.cle) == 1
    assert resultat.tokens == UsageTokens(2000, 400)


# --- Matrice : budget épuisé ------------------------------------------------------------------


@pytest.mark.parametrize("mode", ["batch", "direct"])
def test_budget_epuise(banc: Any, doublures: SimpleNamespace, items: Any, mode: str) -> None:
    banc.plafond = 0.0001
    rapport = banc.juge(mode_appel=mode).juger(demandes(doublures, items, "Q-001", "NR-001"))
    assert rapport.budget_epuise
    assert all(r.statut == "non-juge" and r.motif == "budget" for r in rapport.resultats)
    assert banc.faux.requetes == []
    assert banc.lignes_registre() == []


def test_budget_epuise_en_cours_de_route(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    config = doublures.config_juge()
    prompt = construire_prompt(items["NR-001"], doublures.sortie_factice("<a>"), banc.grille)
    pire = cout_pire_cas(
        charger_tarifs(banc.chemin_tarifs),
        doublures.MODELE,
        "direct",
        estimer_tokens_entree(prompt),
        config.max_tokens,
        1.0,
    )
    usage = UsageTokens(*doublures.USAGE_FACTICE)
    reel = cout_reel(charger_tarifs(banc.chemin_tarifs), doublures.MODELE, "direct", usage)
    banc.plafond = pire + reel / 2
    sorties = [doublures.sortie_factice("<a>"), doublures.sortie_factice("<b>")]
    rapport = banc.juge(mode_appel="direct").juger(
        [DemandeJugement(items["NR-001"], s) for s in sorties]
    )
    assert [r.statut for r in rapport.resultats] == ["juge", "non-juge"]
    assert rapport.resultats[1].motif == "budget" and rapport.budget_epuise
    assert banc.faux.compter("POST /v1/messages") == 1


# --- Matrice : erreurs d'API et résultats de lot en échec -------------------------------------


def test_erreur_api_directe(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.directes["Q-001"] = [500]
    rapport = banc.juge(mode_appel="direct").juger(demandes(doublures, items, "Q-001", "NR-001"))
    q, nr = rapport.resultats
    assert q.statut == "non-juge" and q.motif == "erreur-api"
    assert nr.statut == "juge"  # on continue
    premiere, seconde = banc.lignes_registre()
    assert premiere["etat"] == "pire-cas" and premiere["motif"] == "echec"
    assert seconde["etat"] == "regularisee"
    (appel,) = [a for a in banc.cache.appels() if a["item_id"] == "Q-001"]
    assert appel["issue"] == "erreur-api" and appel["tokens_entree"] is None
    assert appel["cout_eur"] == pytest.approx(premiere["montant_reel_eur"])
    assert q.cout_eur == pytest.approx(premiere["montant_reel_eur"])
    assert banc.cache.lire(q.cle) is None


def test_resultats_de_lot_en_echec(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.resultats_batch.update(
        {"Q-001": "errored", "LC-001": "expired", "NR-001": "canceled"}
    )
    rapport = banc.juge().juger(demandes(doublures, items, "Q-001", "LC-001", "NR-001", "CT-001"))
    assert [r.statut for r in rapport.resultats] == ["juge"] * 4
    assert [r.mode for r in rapport.resultats] == ["direct", "direct", "direct", "batch"]
    assert banc.faux.compter("POST /v1/messages") == 3
    assert all(banc.cache.echecs(r.cle) == 0 for r in rapport.resultats)
    ligne = next(lg for lg in banc.lignes_registre() if lg["batch_id"])
    assert (ligne["tokens_entree"], ligne["tokens_sortie"]) == doublures.USAGE_FACTICE


# --- Matrice : items non jugeables ------------------------------------------------------------


@pytest.mark.parametrize("mode", ["batch", "direct"])
def test_item_non_jugeable_avant_tout_appel(
    banc: Any, doublures: SimpleNamespace, items: Any, mode: str
) -> None:
    juge = banc.juge(mode_appel=mode)
    cr_vide = items["CR-001"].model_copy(
        update={"decisions_reference": None, "actions_reference": []}
    )
    re_vide = items["RE-001"].model_copy(update={"points_cles_reference": []})
    for item in (items["CO-001"], cr_vide, re_vide):
        with pytest.raises(ItemNonJugeable):
            juge.juger(
                [
                    DemandeJugement(items["Q-001"], doublures.sortie_factice()),
                    DemandeJugement(item, doublures.sortie_factice()),
                ]
            )
    assert banc.faux.requetes == []
    assert banc.lignes_registre() == []


# --- Matrice : profil réseau ------------------------------------------------------------------


def test_regle_reseau_suivi_des_lots() -> None:
    config, liste = charger_config_reseau(), charger_liste_blanche()

    def autorise(methode: str, url: str) -> bool:
        return evaluer(
            "outillage", methode, url, mode=None, config=config, liste_blanche=liste
        ).autorise

    assert autorise("GET", "https://api.anthropic.com/v1/messages/batches/x")
    assert autorise("GET", "https://api.anthropic.com/v1/messages/batches/x/results")
    assert autorise("POST", "https://api.anthropic.com/v1/messages/batches")
    assert not autorise("GET", "https://api.mistral.ai/v1/models")
    assert not autorise("DELETE", "https://api.anthropic.com/v1/messages/batches/x")
    assert not autorise("GET", "https://api.anthropic.com.exemple.org/v1/messages")
    assert any(
        r.nom == "anthropic-lots" and r.methodes == ["GET"] for r in config.profils.outillage.regles
    )


# --- Critère : requêtes sans température ni contenu non autorisé ------------------------------


@pytest.mark.parametrize("mode", ["batch", "direct"])
def test_requetes_aveugles_et_sans_temperature(
    banc: Any, doublures: SimpleNamespace, items: Any, mode: str
) -> None:
    banc.juge(mode_appel=mode).juger(demandes(doublures, items, "Q-001", "CR-001", "RE-001"))
    corps = [c for c in banc.faux.corps() if c]
    assert corps
    for brut in corps:
        for interdit in ("temperature", "top_p", "top_k", "thinking", "fallbacks", '"system"'):
            assert interdit.encode() not in brut
        for sentinelle in doublures.SENTINELLES:
            assert sentinelle.encode() not in brut
    if mode == "direct":
        params = corps_json(banc, "POST /v1/messages")
    else:
        (lot,) = corps_json(banc, "POST /v1/messages/batches")
        params = [r["params"] for r in lot["requests"]]
        assert set(lot) == {"requests"}
        assert all(set(r) == {"custom_id", "params"} for r in lot["requests"])
    assert len(params) == 3
    for p in params:
        assert set(p) == CLES_REQUETE
        assert p["model"] == doublures.MODELE and p["max_tokens"] == 6000
        assert len(p["messages"]) == 1 and p["messages"][0]["role"] == "user"
        assert p["output_config"]["effort"] == "medium"
        assert p["output_config"]["format"]["type"] == "json_schema"
        assert "Titre de source factice" in p["messages"][0]["content"]


# --- Suivi d'un lot en panne ------------------------------------------------------------------


def assert_lot_laisse_ouvert(banc: Any, rapport: Any, motif: str) -> None:
    assert all(r.statut == "non-juge" and r.motif == motif for r in rapport.resultats)
    assert banc.faux.compter("POST /v1/messages") == 0
    (lot,) = banc.lots()
    assert lot["statut"] == "en_cours"
    (ligne,) = banc.lignes_registre()
    assert ligne["etat"] == "reservee"


def test_releve_de_lot_en_panne(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.pannes["retrieve"] = 4  # une erreur de plus que la tolérance
    demandees = demandes(doublures, items, "Q-001", "NR-001")
    rapport = banc.juge().juger(demandees)
    assert_lot_laisse_ouvert(banc, rapport, "erreur-api")
    assert banc.horloge.attentes == [60, 60, 60]

    rapport = banc.juge().juger(demandees)  # relu et soldé plus tard
    assert all(r.statut == "juge" and r.mode == "batch" for r in rapport.resultats)
    assert banc.lots()[0]["statut"] == "collecte"
    assert banc.lignes_registre()[0]["etat"] == "regularisee"


def test_releve_de_lot_erreurs_tolerees(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.pannes["retrieve"] = 3
    rapport = banc.juge().juger(demandes(doublures, items, "Q-001"))
    assert rapport.resultats[0].statut == "juge"
    assert banc.lots()[0]["statut"] == "collecte"


def test_resultats_de_lot_en_panne(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.pannes["results"] = 1
    demandees = demandes(doublures, items, "Q-001", "NR-001")
    rapport = banc.juge().juger(demandees)
    assert_lot_laisse_ouvert(banc, rapport, "erreur-api")

    rapport = banc.juge().juger(demandees)
    assert all(r.statut == "juge" and r.mode == "batch" for r in rapport.resultats)
    assert banc.lots()[0]["statut"] == "collecte"
    assert banc.lignes_registre()[0]["etat"] == "regularisee"


def test_annulation_en_panne(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.jamais_fini = True
    banc.faux.pannes["cancel"] = 1
    demandees = demandes(doublures, items, "Q-001", "NR-001")
    rapport = banc.juge(delai_max_lot=120, intervalle_sondage=60).juger(demandees)
    assert_lot_laisse_ouvert(banc, rapport, "lot-non-annule")

    # Plus tard : délai dépassé depuis la soumission, annulation dès le premier relevé.
    debut = len(banc.faux.requetes)
    rapport = banc.juge(delai_max_lot=120, intervalle_sondage=60).juger(demandees)
    reprise = banc.faux.chemins()[debut:]
    assert reprise[:2] == [
        "GET /v1/messages/batches/msgbatch_0001",
        "POST /v1/messages/batches/msgbatch_0001/cancel",
    ]
    assert banc.lots()[0]["statut"] == "annule"
    assert banc.lignes_registre()[0]["etat"] == "regularisee"
    assert all(r.statut == "juge" and r.mode == "direct" for r in rapport.resultats)


# --- Délai mesuré depuis la soumission --------------------------------------------------------


def test_lot_repris_annule_selon_la_soumission(
    banc: Any, doublures: SimpleNamespace, items: Any
) -> None:
    banc.faux.jamais_fini = True
    banc.horloge.crash_apres = 0
    demandees = demandes(doublures, items, "Q-001")
    with pytest.raises(doublures.Crash):
        banc.juge().juger(demandees)
    assert banc.lots()[0]["soumis_le"].startswith("2026-10-12T00:00:00")

    banc.horloge.crash_apres = None
    banc.horloge.temps = 4000  # au-delà de delai_max_lot (3600 s) depuis la soumission
    attentes, debut = len(banc.horloge.attentes), len(banc.faux.requetes)
    rapport = banc.juge().juger(demandees)
    reprise = banc.faux.chemins()[debut:]
    assert reprise[:2] == [
        "GET /v1/messages/batches/msgbatch_0001",
        "POST /v1/messages/batches/msgbatch_0001/cancel",
    ]
    assert len(banc.horloge.attentes) - attentes == 1  # seulement l'attente de confirmation
    assert banc.lots()[0]["statut"] == "annule"
    assert rapport.resultats[0].statut == "juge" and rapport.resultats[0].mode == "direct"


def test_lot_deja_en_annulation_sans_nouvel_ordre(
    banc: Any, doublures: SimpleNamespace, items: Any
) -> None:
    banc.faux.jamais_fini = True
    banc.faux.annulation_confirmee = False
    demandees = demandes(doublures, items, "Q-001")
    config = {"delai_max_lot": 120, "intervalle_sondage": 60, "delai_annulation": 120}
    banc.juge(**config).juger(demandees)
    assert banc.faux.compter("POST /v1/messages/batches/msgbatch_0001/cancel") == 1

    # Lot repris en `canceling` : on attend la confirmation, sans nouvelle annulation.
    attentes = len(banc.horloge.attentes)
    rapport = banc.juge(**config).juger(demandees)
    assert banc.faux.compter("POST /v1/messages/batches/msgbatch_0001/cancel") == 1
    assert rapport.resultats[0].motif == "lot-non-annule"
    assert len(banc.horloge.attentes) - attentes == 2  # 120 s d'attente de confirmation

    banc.faux.annulation_confirmee = True
    rapport = banc.juge(**config).juger(demandees)
    assert banc.faux.compter("POST /v1/messages/batches/msgbatch_0001/cancel") == 1
    assert banc.lots()[0]["statut"] == "annule"


# --- Reprise après un arrêt pendant la collecte -----------------------------------------------


def test_reprise_apres_crash_pendant_la_collecte(
    banc: Any, doublures: SimpleNamespace, items: Any
) -> None:
    banc.faux.resultats_batch["NR-001"] = {"texte": "{"}  # non conforme
    demandees = demandes(doublures, items, "Q-001", "NR-001")
    juge = banc.juge()
    banc.registre.crash_collecte = True
    with pytest.raises(doublures.Crash):
        juge.juger(demandees)
    banc.registre.crash_collecte = False

    rapport = banc.juge().juger(demandees)  # aucune exception
    q, nr = rapport.resultats
    assert q.statut == "juge" and q.cout_eur == 0
    assert nr.statut == "juge" and nr.mode == "direct"  # second essai, pas `invalide`
    assert banc.cache.echecs(nr.cle) == 1
    (lot,) = banc.lots()
    assert lot["statut"] == "collecte"
    lignes_lot = [a["item_id"] for a in banc.cache.appels() if a["lot_id"] == lot["lot_id"]]
    assert sorted(lignes_lot) == ["NR-001", "Q-001"]  # une ligne par item
    assert [(lg["batch_id"] is not None, lg["etat"]) for lg in banc.lignes_registre()] == [
        (True, "regularisee"),
        (False, "regularisee"),  # le second essai direct de NR-001
    ]


def test_reprise_lot_reserve_sans_ligne_registre(
    banc: Any, doublures: SimpleNamespace, items: Any
) -> None:
    juge = banc.juge()
    requete = RequeteLot("r00000", "cle-orpheline", "Q-001", {"type": "object"})
    banc.cache.creer_lot("slmsp-juge-orphelin", doublures.MODELE, "medium", [requete])
    rapport = juge.juger(demandes(doublures, items, "Q-001"))
    assert banc.cache.lot("slmsp-juge-orphelin").statut == "abandonne"
    assert rapport.resultats[0].statut == "juge"
    assert all(lg["batch_id"] != "slmsp-juge-orphelin" for lg in banc.lignes_registre())


# --- Refus 4xx non facturés -------------------------------------------------------------------


def test_refus_400_non_facture(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.directes["Q-001"] = [400]
    rapport = banc.juge(mode_appel="direct").juger(demandes(doublures, items, "Q-001", "NR-001"))
    q, nr = rapport.resultats
    assert q.statut == "non-juge" and q.motif == "erreur-api" and q.cout_eur == 0
    assert nr.statut == "juge"
    premiere = banc.lignes_registre()[0]
    assert premiere["etat"] == "regularisee" and premiere["montant_reel_eur"] == 0
    (appel,) = [a for a in banc.cache.appels() if a["item_id"] == "Q-001"]
    assert appel["issue"] == "erreur-api" and appel["cout_eur"] == 0


def test_refus_401_arrete_le_run(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    banc.faux.directes["Q-001"] = [401]
    rapport = banc.juge(mode_appel="direct").juger(
        demandes(doublures, items, "Q-001", "NR-001", "LC-001")
    )
    assert banc.faux.compter("POST /v1/messages") == 1
    assert all(r.statut == "non-juge" and r.motif == "erreur-api" for r in rapport.resultats)
    (ligne,) = banc.lignes_registre()
    assert ligne["montant_reel_eur"] == 0


# --- Coût cumulé d'un verdict invalide sur plusieurs runs -------------------------------------


def test_invalide_cout_cumule_sur_plusieurs_runs(
    banc: Any, doublures: SimpleNamespace, items: Any
) -> None:
    banc.faux.directes["NR-001"] = [{"texte": "{"}, 500]
    banc.juge(mode_appel="direct").juger(demandes(doublures, items, "NR-001"))
    banc.faux.directes["NR-001"] = [{"texte": "{"}]
    rapport = banc.juge(mode_appel="direct").juger(demandes(doublures, items, "NR-001"))
    (resultat,) = rapport.resultats
    assert resultat.statut == "invalide"
    appels = [a for a in banc.cache.appels() if a["cle"] == resultat.cle]
    assert [a["issue"] for a in appels] == ["non-conforme", "erreur-api", "invalide"]
    en_cache = banc.cache.lire(resultat.cle)
    assert en_cache.cout_eur == pytest.approx(sum(a["cout_eur"] for a in appels))
    assert en_cache.usage == UsageTokens(2000, 400)


# --- Budget épuisé en cours de route ----------------------------------------------------------


def pire_cas_batch(banc: Any, doublures: SimpleNamespace, item: Any, sortie: Any) -> tuple:
    prompt = construire_prompt(item, sortie, banc.grille)
    estimes = estimer_tokens_entree(prompt)
    tarifs = charger_tarifs(banc.chemin_tarifs)
    return cout_pire_cas(tarifs, doublures.MODELE, "batch", estimes, 6000, 1.0), estimes


def test_budget_epuise_au_second_essai_direct(
    banc: Any, doublures: SimpleNamespace, items: Any
) -> None:
    unitaire, _ = pire_cas_batch(banc, doublures, items["Q-001"], doublures.sortie_factice())
    banc.plafond = unitaire * 1.5  # le lot tient, pas l'appel direct (tarif double)
    banc.faux.resultats_batch["Q-001"] = {"texte": "{"}
    rapport = banc.juge().juger(demandes(doublures, items, "Q-001"))
    (resultat,) = rapport.resultats
    assert resultat.statut == "non-juge" and resultat.motif == "budget"
    assert rapport.budget_epuise
    assert banc.faux.compter("POST /v1/messages") == 0


def test_lot_partiel_puis_budget_epuise(banc: Any, doublures: SimpleNamespace, items: Any) -> None:
    sorties = [doublures.sortie_factice(f"<sortie-factice-{i}>") for i in range(3)]
    unitaire, estimes = pire_cas_batch(banc, doublures, items["Q-001"], sorties[0])
    banc.plafond = unitaire * 1.5
    banc.faux.usages["Q-001"] = (estimes, 6000)  # coût réel = pire cas : rien n'est libéré
    rapport = banc.juge().juger([DemandeJugement(items["Q-001"], s) for s in sorties])
    assert [r.statut for r in rapport.resultats] == ["juge", "non-juge", "non-juge"]
    assert [r.motif for r in rapport.resultats[1:]] == ["budget", "budget"]
    assert rapport.budget_epuise
    (lot,) = corps_json(banc, "POST /v1/messages/batches")
    assert len(lot["requests"]) == 1
