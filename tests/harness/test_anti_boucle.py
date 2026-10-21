"""Garde-fou anti-boucle du décodage (story 16.3). Fixtures factices seulement (D1)."""

from __future__ import annotations

import pytest
from harness_factices import FakeLlm, jetons
from pydantic import ValidationError

from slmsp.core.evenements import Fin, Jeton, Sources
from slmsp.harness.anti_boucle import (
    RAISON_BOUCLE,
    DetecteurBoucle,
    borner_boucles,
    point_de_coupure,
)
from slmsp.harness.config import ConfigAntiBoucle, charger_config_harnais

CONFIG = ConfigAntiBoucle(
    actif=True, repetitions_ligne_max=3, fenetre_mots=20, taille_ngramme=4, part_ngrammes_max=0.8
)
FIN = Fin(raison="terminee", usage={"completion_tokens": 9})


def texte_de(evenements) -> str:
    return "".join(e.texte for e in evenements if isinstance(e, Jeton))


def varie(n: int) -> str:
    """`n` lignes factices toutes différentes."""
    return "".join(f"<ligne-factice-{i}> <mot-{i}-a> <mot-{i}-b>\n" for i in range(n))


# --- Sorties qui ne bouclent pas : identiques -------------------------------------------


@pytest.mark.parametrize("taille", [1, 3, 7, 1000])
def test_sortie_sans_boucle_relayee_a_l_identique(taille) -> None:
    flux = [*jetons(varie(30) + "<fin-factice>", taille), FIN]
    assert list(borner_boucles(iter(flux), CONFIG)) == flux


def test_lignes_repetees_jusqu_au_seuil_gardees() -> None:
    texte = "<entete-factice>\n" + "<ligne-repetee>\n\n" * 3 + "<suite-factice>\n"
    flux = [*jetons(texte, 4), FIN]
    assert list(borner_boucles(iter(flux), CONFIG)) == flux


def test_lignes_sans_alphanumerique_ignorees() -> None:
    texte = "<a-factice>\n" + "| --- | --- |\n" * 10 + "***\n" * 10
    assert point_de_coupure(texte, CONFIG) is None


@pytest.mark.parametrize("separateur", ["| --- | --- | --- |", "........ ........", "---"])
def test_separateurs_ignores_par_les_ngrammes(separateur) -> None:
    # Assez de mots pour remplir la fenêtre : seuls les mots alphanumériques comptent.
    texte = "<a-factice>\n" + (separateur + "\n") * 60
    assert point_de_coupure(texte, CONFIG) is None


def formulaire() -> str:
    """Structure d'un formulaire (emplacements répétés, pointillés, tableau), jetons factices."""
    entete = varie(6)
    adresses = "".join(
        f"<champ-adresse-factice> : [<emplacement-factice>]\n<entre-factice-{i}>\n"
        for i in range(10)
    )
    personnes = (
        "<champ-nom-factice> : ........\n<champ-signature-factice> : ........\n"
        "<champ-date-factice> : ..../..../........\n"
    ) * 12
    tableau = "| <col-a-factice> | <col-b-factice> |\n| --- | --- |\n" + (
        "| <cellule-factice> | ........ |\n" * 12
    )
    return entete + adresses + personnes + tableau + varie(4)


@pytest.mark.parametrize("taille", [1, 7, 10_000])
def test_formulaire_non_coupe_avec_la_config_du_projet(taille) -> None:
    config = charger_config_harnais().anti_boucle
    flux = [*jetons(formulaire(), taille), FIN]
    assert list(borner_boucles(iter(flux), config)) == flux


def test_boucle_de_bloc_coupee_avec_la_config_du_projet() -> None:
    # Bloc de 7 lignes répété 12 fois (lignes sous le seuil) : coupé par les n-grammes.
    bloc = "".join(f"**[<emplacement-factice-{i}> <mot-a> <mot-b> <mot-c>]**\n\n" for i in range(7))
    texte = varie(3) + bloc * 12
    assert point_de_coupure(texte, charger_config_harnais().anti_boucle) is not None


@pytest.mark.parametrize("fin_de_ligne", ["\r\n", "  \n", " \t\r\n"])
def test_ligne_de_trop_jamais_emise_avec_blancs_de_fin(fin_de_ligne) -> None:
    texte = "<entete-factice>\n" + ("<emplacement-factice>" + fin_de_ligne) * 6
    sortie = list(borner_boucles(iter([*jetons(texte, 1), FIN]), CONFIG))
    assert sortie[-1] == Fin(raison=RAISON_BOUCLE)
    assert texte_de(sortie) == "<entete-factice>\n" + ("<emplacement-factice>" + fin_de_ligne) * 3


def test_flux_sans_fin_rend_les_jetons_retenus() -> None:
    flux = [Jeton(texte="<l-factice>\n" * 3), Jeton(texte="<l-fac")]
    assert list(borner_boucles(iter(flux), CONFIG)) == flux


def test_autres_evenements_conserves_dans_l_ordre() -> None:
    sources = Sources(sources=[])
    flux = [Jeton(texte="<x-factice>\n<y"), sources, Jeton(texte="-factice>"), FIN]
    assert list(borner_boucles(iter(flux), CONFIG)) == flux


def test_inactif_relaie_meme_une_boucle() -> None:
    flux = [*jetons("<boucle-factice>\n" * 20, 5), FIN]
    inactif = CONFIG.model_copy(update={"actif": False})
    assert list(borner_boucles(iter(flux), inactif)) == flux


# --- Boucles : coupure avant la répétition ----------------------------------------------


@pytest.mark.parametrize("taille", [1, 2, 5, 17, 10_000])
def test_ligne_repetee_coupee_avant_la_repetition_de_trop(taille) -> None:
    debut = "<entete-factice>\n"
    texte = debut + "<emplacement-factice>\n" * 12
    sortie = list(borner_boucles(iter([*jetons(texte, taille), FIN]), CONFIG))
    assert sortie[-1] == Fin(raison=RAISON_BOUCLE)
    assert texte_de(sortie) == debut + "<emplacement-factice>\n" * 3
    assert point_de_coupure(texte, CONFIG) == len(debut + "<emplacement-factice>\n" * 3)


def test_ligne_comparee_sans_blancs_de_bord() -> None:
    texte = "<l-factice>\n  <l-factice>\n<l-factice>  \n\t<l-factice>\n"
    assert point_de_coupure(texte, CONFIG) == texte.index("\t")


def test_jetons_retenus_rendus_intacts_quand_la_ligne_diverge() -> None:
    debut = "<l-factice>\n" * 3
    flux = [Jeton(texte=debut), Jeton(texte="<l-fac"), Jeton(texte="tice-autre>\n"), FIN]
    sortie = list(borner_boucles(iter(flux), CONFIG))
    assert sortie == flux


def test_boucle_sans_saut_de_ligne_coupee_par_les_ngrammes() -> None:
    texte = "<debut-factice>\n" + "<a> <b> " * 40
    sortie = list(borner_boucles(iter([*jetons(texte, 6), FIN]), CONFIG))
    assert sortie[-1].raison == RAISON_BOUCLE
    emis = texte_de(sortie)
    assert texte.startswith(emis) and len(emis) < len(texte)


def test_ngrammes_sous_le_seuil_non_coupes() -> None:
    texte = " ".join(f"<mot-factice-{i}>" for i in range(200)) + "\n"
    assert point_de_coupure(texte, CONFIG) is None


def test_detecteur_incremental_egal_au_bloc() -> None:
    texte = varie(4) + "<r-factice> <s>\n" * 9 + varie(3)
    detecteur = DetecteurBoucle(CONFIG)
    coupures = [detecteur.ajouter(c) for c in texte]
    premiere = next(c for c in coupures if c is not None)
    assert premiere == point_de_coupure(texte, CONFIG)
    assert detecteur.ajouter("<apres>") == premiere


def test_flux_ferme_apres_coupure_par_le_service(table) -> None:
    from slmsp.harness.service import AssistantService

    config = charger_config_harnais()
    config = config.model_copy(update={"anti_boucle": CONFIG})
    llm = FakeLlm([*jetons("<ligne-factice>\n" * 50, 3), FIN])
    service = AssistantService(llm, None, None, None, None, config, taches=table)
    entree = {"consigne": "<c>", "type_courrier": "<t>", "objet": "<o>", "elements_connus": "<e>"}
    sortie = list(service.repondre("CT", [{"role": "user", "content": "<u>"}], {"entree": entree}))
    assert isinstance(sortie[-1], Fin) and sortie[-1].raison == RAISON_BOUCLE
    assert texte_de(sortie) == "<ligne-factice>\n" * 3
    assert llm.fermetures == 1


# --- Configuration ----------------------------------------------------------------------


def test_section_absente_inactive() -> None:
    assert ConfigAntiBoucle().actif is False


def test_fenetre_plus_grande_que_le_ngramme() -> None:
    with pytest.raises(ValidationError):
        ConfigAntiBoucle(fenetre_mots=4, taille_ngramme=4)


def test_config_du_projet_active() -> None:
    config = charger_config_harnais().anti_boucle
    assert config.actif is True
    assert config.repetitions_ligne_max >= 1 and 0 < config.part_ngrammes_max <= 1
