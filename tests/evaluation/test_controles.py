"""Contrôles automatiques de la notation (story 5.6) : fonctions pures, sans réseau.

Les items viennent du jeu v1.0 et du calibrage lus en lecture seule (aucune écriture sous
`eval/`) ; les sorties sont des chaînes factices construites pour chaque cas.
"""

from __future__ import annotations

from typing import Any

import pytest

from slmsp.core.config import racine_projet
from slmsp.core.items import AppelAttendu, ItemCO, lire_jeu
from slmsp.core.schemas.generation import Generation
from slmsp.core.texte import kandel_moles
from slmsp.evaluation.config import charger_evaluation
from slmsp.evaluation.controles import (
    apparier_appels,
    appel_conforme,
    appliquer_equivalences,
    controle_co,
    controle_ct,
    controle_lc,
    controle_q,
    controle_rd,
    controle_re,
    controler,
)

V10 = lire_jeu("v1.0", racine_projet())
CALIBRAGE = lire_jeu("calibrage", racine_projet())
CONFIG = charger_evaluation()
EQUIVALENCES = CONFIG.co.equivalences
LONGUEURS = CONFIG.re.longueurs.model_dump()


def generation(
    item: Any,
    texte: str,
    *,
    appels: list[tuple[str, dict[str, Any]]] = (),  # type: ignore[assignment]
    sources: list[dict[str, Any]] = (),  # type: ignore[assignment]
    resultats: list[Any] = (),  # type: ignore[assignment]
) -> Generation:
    trace = [
        {"type": "resultat-outil", "id": f"r{i}", "nom": "search_datasets", "resultat": r}
        for i, r in enumerate(resultats)
    ]
    trace.append({"type": "fin", "raison": "terminee"})
    return Generation(
        item_id=item.id,
        tache=item.code,
        statut="ok",
        sortie_canonique={
            "texte": texte,
            "appels_outils": [{"nom": n, "arguments": a} for n, a in appels],
            "sources": sources,
        },
        trace=trace,
        duree_ms=1,
    )


# --- Q ----------------------------------------------------------------------------------------


def test_q_url_inventee_et_urls_connues() -> None:
    item = V10.item("Q-001")
    texte = (
        "Voir https://exemple.invalid/page-factice, https://www.service-public.gouv.fr/fiche-a/ "
        "et https://outil.invalid/resultat."
    )
    sortie = generation(
        item,
        texte,
        sources=[
            {"titre": "t", "url": "https://service-public.gouv.fr/fiche-a", "origine": "index"}
        ],
        resultats=[{"page": {"lien": "https://outil.invalid/resultat"}}],
    )
    assert controle_q(item, sortie) == {"urls_inventees": ["https://exemple.invalid/page-factice"]}
    assert controle_q(item, generation(item, "sans lien")) == {"urls_inventees": []}


# --- RD : appels -------------------------------------------------------------------------------


def appel_attendu(outil: str, arguments: dict[str, Any], **options: Any) -> AppelAttendu:
    return AppelAttendu(outil=outil, arguments={}, regles={"arguments": arguments, **options})


@pytest.mark.parametrize(
    ("valeur", "attendu"),
    [
        ("APA à domicile", True),
        ("aide apa", True),
        ("Floutée base", True),
        ("papa domicile", False),  # « apa » au milieu d'un mot
        ("autonomies", True),  # début de mot suffit
        ("", False),
    ],
)
def test_rd_contient_un_de_en_debut_de_mot(valeur: str, attendu: bool) -> None:
    regle = appel_attendu("search_datasets", {"query": {"contient_un_de": ["apa", "autonomie"]}})
    regle_floutee = appel_attendu("search_datasets", {"query": {"contient_un_de": ["floutée"]}})
    conforme = appel_conforme(regle, "search_datasets", {"query": valeur}) or appel_conforme(
        regle_floutee, "search_datasets", {"query": valeur}
    )
    assert conforme is attendu


def test_rd_regles_exact_optionnel_et_outil() -> None:
    regle = appel_attendu(
        "query_resource_data",
        {"filter_value": {"exact": "91"}, "filter_operator": {"optionnel": True, "exact": "exact"}},
    )
    assert appel_conforme(regle, "query_resource_data", {"filter_value": "91"})
    assert appel_conforme(
        regle, "query_resource_data", {"filter_value": "91", "filter_operator": "exact"}
    )
    assert not appel_conforme(regle, "query_resource_data", {"filter_value": 91})  # type
    assert not appel_conforme(
        regle, "query_resource_data", {"filter_value": "91", "filter_operator": "contains"}
    )
    assert not appel_conforme(regle, "get_dataset_info", {"filter_value": "91"})
    sans_regles = AppelAttendu(outil="search_datasets", arguments={"query": "x"})
    assert appel_conforme(sans_regles, "search_datasets", {"autre": 1})


def test_rd_appariement_ordre_et_optionnel() -> None:
    a = appel_attendu("search_datasets", {})
    b = appel_attendu("list_dataset_resources", {})
    c = appel_attendu("get_dataset_info", {}, optionnel=True)
    emis = [("list_dataset_resources", {}), ("search_datasets", {})]
    # Ordre de la liste : `b` doit suivre `a`, qui a pris l'indice 1.
    assert apparier_appels([a, b], emis) == [1, None]
    libre = appel_attendu("list_dataset_resources", {}, ordre_libre=True)
    assert apparier_appels([a, libre], emis) == [1, 0]
    assert apparier_appels([a, c], emis) == [1, None]


def test_rd_sans_appel_attendu() -> None:
    item = V10.item("RD-001").model_copy(update={"appels_attendus": None})
    controle = controle_rd(item, generation(item, "x", appels=[("search_datasets", {})]))
    assert controle["appels_attendus"] == 0 and controle["appels_valides"] == 0


def test_rd_controle_appels_valides_micro() -> None:
    item = V10.item("RD-010")  # trois appels attendus, valeurs numériques
    emis = [
        ("search_datasets", {"query": "bailleurs sociaux"}),
        ("list_dataset_resources", {"dataset_id": "5fa9901bdf2bbb37b61963e6"}),
        ("query_resource_data", {"resource_id": "mauvais"}),
    ]
    controle = controle_rd(item, generation(item, "rien", appels=emis))
    assert controle["appels_attendus"] == 3 and controle["appels_valides"] == 2
    assert controle["appariement"] == [0, 1, None]


# --- RD : réponse exacte -----------------------------------------------------------------------


def test_rd_reponse_exacte_par_identifiant_ou_url() -> None:
    item = V10.item("RD-001")
    identifiant = "62263312d650d1f5383e0c4f"
    url = "https://data.gouv.fr/datasets/beneficiaires-de-lapa-a-domicile-base-floutee-v1/"
    for texte in (f"jeu {identifiant}.", f"lien : {url}"):
        controle = controle_rd(item, generation(item, texte))
        assert controle["reponse_exacte"] is True and controle["litige"] is False


def test_rd_litige_titre_sans_identifiant() -> None:
    item = V10.item("RD-001")
    texte = "Le jeu « Bénéficiaires de l'APA à domicile : base floutée (V1) » existe."
    controle = controle_rd(item, generation(item, texte))
    assert controle["litige"] is True and controle["reponse_exacte"] is None
    absent = controle_rd(item, generation(item, "<texte-factice>"))
    assert absent["litige"] is False and absent["reponse_exacte"] is False


def test_rd_autres_jeux_cites_possibles() -> None:
    item = V10.item("RD-002")
    autre = item.reponse_reference["autres_jeux_cites_possibles"][0]["id"]
    assert controle_rd(item, generation(item, f"voir {autre}"))["reponse_exacte"] is True


def test_rd_valeurs_numeriques() -> None:
    item = V10.item("RD-010")  # Essonne : 2018, 67, 26, 113838
    complet = "En 2018 : 67 bailleurs (26 consolidés) et 113 838 logements."
    assert controle_rd(item, generation(item, complet))["reponse_exacte"] is True
    partiel = controle_rd(item, generation(item, "En 2018 : 67 bailleurs."))
    assert partiel["reponse_exacte"] is False
    assert set(partiel["valeurs_manquantes"]) == {"26", "113838"}


def test_rd_valeurs_des_colonnes_declarees() -> None:
    item = V10.item("RD-017")  # Caen : (2020, mois 1 à 3) → 134, 137, 75
    reponse = "Janvier 2020 : 134 cartes, février : 137, mars : 75."
    sans = controle_rd(item, generation(item, reponse))
    assert sans["reponse_exacte"] is False and set(sans["valeurs_manquantes"]) == {"1", "2", "3"}
    valeurs = {**item.valeurs_attendues, "colonnes": ["Nombre"]}
    declare = item.model_copy(update={"valeurs_attendues": valeurs})
    assert controle_rd(declare, generation(declare, reponse))["reponse_exacte"] is True
    partiel = controle_rd(declare, generation(declare, "Janvier : 134."))
    assert partiel["reponse_exacte"] is False
    assert set(partiel["valeurs_manquantes"]) == {"137", "75"}


def test_rd_calibrage_sans_regles_ni_identifiant() -> None:
    item = CALIBRAGE.item("RD-001")  # R-001 : jeu principal sans `id`, règles textuelles
    emis = [("search_datasets", {"query": "x"}), ("get_dataset_info", {"dataset_id": "y"})]
    url = "https://www.data.gouv.fr/datasets/geodae-base-nationale-des-defibrillateurs"
    controle = controle_rd(item, generation(item, url, appels=emis))
    assert controle["appels_valides"] == 2 and controle["reponse_exacte"] is True
    sans_reference = controle_rd(CALIBRAGE.item("RD-002"), generation(item, "208"))
    assert sans_reference["reponse_exacte"] is None and sans_reference["litige"] is False


# --- CO ----------------------------------------------------------------------------------------


def item_co() -> ItemCO:
    texte = "Les agent sont venu hier. Le service ferme à midi."
    return ItemCO.model_validate(
        {
            **V10.item("CO-001").model_dump(),
            "entree": {"consigne": "corrige", "texte": texte},
            "fautes": [
                {"debut": 4, "fin": 9, "erreur": "agent", "correction": "agents", "type": "accord"},
                {"debut": 15, "fin": 19, "erreur": "venu", "correction": "venus", "type": "accord"},
            ],
        }
    )


def test_co_fautes_corrigees_sans_modification() -> None:
    item = item_co()
    sortie = generation(item, "Les agents sont venus hier. Le service ferme à midi.")
    controle = controle_co(item, sortie, EQUIVALENCES)
    assert controle["corrigees"] == 2 and controle["rappel"] == 1.0
    assert controle["taux_hors_faute"] == 0.0


def test_co_faute_non_corrigee() -> None:
    item = item_co()
    controle = controle_co(
        item, generation(item, "Les agents sont venu hier. Le service ferme à midi."), EQUIVALENCES
    )
    assert controle["fautes_corrigees"] == [True, False] and controle["rappel"] == 0.5


def test_co_modifications_hors_faute() -> None:
    item = item_co()  # 10 mots
    sortie = "Les agents sont venus hier. Le bureau ferme à midi. Merci beaucoup."
    controle = controle_co(item, generation(item, sortie), EQUIVALENCES)
    assert controle["rappel"] == 1.0
    assert controle["mots_modifies_hors_faute"] == 1  # service → bureau
    assert controle["mots_inseres_hors_faute"] == 2  # ajout final, loin des fautes
    assert controle["taux_hors_faute"] == 0.3


def test_co_insertion_adjacente_a_une_faute_et_plafond() -> None:
    item = item_co()
    adjacente = controle_co(
        item,
        generation(item, "Les agents publics sont venus hier. Le service ferme à midi."),
        EQUIVALENCES,
    )
    assert adjacente["mots_inseres_hors_faute"] == 0 and adjacente["taux_hors_faute"] == 0.0
    # Bloc remplacé touchant les fautes : 8 mots hors faute modifiés, ajouts adjacents.
    remplace = controle_co(item, generation(item, "x " * 40), EQUIVALENCES)
    assert remplace["taux_hors_faute"] == 0.8 and remplace["rappel"] == 0.0
    ajout = "Les agents sont venus hier. Le service ferme à midi." + " mot" * 20
    plafond = controle_co(item, generation(item, ajout), EQUIVALENCES)
    assert plafond["mots_inseres_hors_faute"] == 20 and plafond["taux_hors_faute"] == 1.0


def test_co_equivalences_typographiques() -> None:
    assert appliquer_equivalences("l’« a »…", EQUIVALENCES) == 'l\'" a "...'
    texte = "L’agent dit « oui »… Les agent sont là."
    item = ItemCO.model_validate(
        {
            **V10.item("CO-001").model_dump(),
            "entree": {"consigne": "corrige", "texte": texte},
            "fautes": [
                {"debut": 25, "fin": 30, "erreur": "agent", "correction": "agents", "type": "a"}
            ],
        }
    )
    sortie = 'L\'agent dit " oui "... Les agents sont là.'
    controle = controle_co(item, generation(item, sortie), EQUIVALENCES)
    assert controle["rappel"] == 1.0 and controle["taux_hors_faute"] == 0.0


def test_co_faute_sur_deux_mots() -> None:
    item = V10.item("CO-001")
    texte = item.entree["texte"]
    corrige = texte
    for faute in sorted(item.fautes, key=lambda f: f.debut, reverse=True):
        corrige = corrige[: faute.debut] + faute.correction + corrige[faute.fin :]
    controle = controle_co(item, generation(item, corrige), EQUIVALENCES)
    assert controle["rappel"] == 1.0 and controle["taux_hors_faute"] == 0.0
    controle_brut = controle_co(item, generation(item, texte), EQUIVALENCES)
    assert controle_brut["rappel"] == 0.0 and controle_brut["taux_hors_faute"] == 0.0


# --- CT, RE, LC -------------------------------------------------------------------------------


def test_ct_emplacements() -> None:
    item = V10.item("CT-001")
    libelles = item.champs_a_laisser_en_emplacement
    complet = controle_ct(item, generation(item, " ".join(libelles)))
    assert complet["emplacements_reussis"] is True
    sans_crochets = " ".join(libelle.strip("[]") for libelle in libelles)
    partiel = controle_ct(item, generation(item, sans_crochets + " " + libelles[0]))
    assert partiel["emplacements_reussis"] is False
    assert partiel["emplacements"][libelles[0]] is True


def test_re_longueur() -> None:
    item = V10.item("RE-001")
    assert item.longueur_demandee == "courte"
    court = controle_re(item, generation(item, "mot " * 80), LONGUEURS)
    assert court == {
        "mots": 80, "longueur_demandee": "courte", "plafond_mots": 80, "respect_longueur": True,
    }  # fmt: skip
    assert controle_re(item, generation(item, "mot " * 81), LONGUEURS)["respect_longueur"] is False
    calibrage = CALIBRAGE.item("RE-002")  # « moyenne (150 à 200 mots) »
    assert controle_re(calibrage, generation(calibrage, "mot"), LONGUEURS)["plafond_mots"] == 200


def test_lc_kandel_moles() -> None:
    item = V10.item("LC-001")
    sortie = "Le RSA aide. Vous y avez droit."
    controle = controle_lc(item, generation(item, sortie))
    assert controle["km_entree"] == item.kandel_moles_entree
    assert controle["km_sortie"] == round(kandel_moles(sortie), 4)
    assert controle["gain_km"] == round(kandel_moles(sortie) - item.kandel_moles_entree, 4)
    calcule = item.model_copy(update={"kandel_moles_entree": None})
    attendu = round(kandel_moles(item.entree["texte"]), 4)
    assert controle_lc(calcule, generation(item, sortie))["km_entree"] == attendu
    assert controle_lc(item, generation(item, "…"))["gain_km"] is None


def test_controler_aiguillage() -> None:
    for identifiant in ("CR-001", "NR-001"):
        item = V10.item(identifiant)
        assert controler(item, generation(item, "x"), equivalences={}, longueurs={}) == {}


def test_co_espacement_de_la_ponctuation_tolere() -> None:
    texte = "Les agent sont là : venez « vite » !"
    item = ItemCO.model_validate(
        {
            **V10.item("CO-001").model_dump(),
            "entree": {"consigne": "corrige", "texte": texte},
            "fautes": [
                {"debut": 4, "fin": 9, "erreur": "agent", "correction": "agents", "type": "a"}
            ],
        }
    )
    sortie = "Les agents sont là: venez «vite»!"
    controle = controle_co(item, generation(item, sortie), EQUIVALENCES)
    assert controle["rappel"] == 1.0 and controle["taux_hors_faute"] == 0.0


def test_rd_identifiant_inclus_dans_un_plus_long_refuse() -> None:
    item = V10.item("RD-001")
    texte = "jeu 62263312d650d1f5383e0c4fab."
    assert controle_rd(item, generation(item, texte))["reponse_exacte"] is not True
