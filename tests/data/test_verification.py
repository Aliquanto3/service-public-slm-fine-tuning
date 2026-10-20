"""Story O6a : contrôles déterministes des cibles CR, LC, CT (`slmsp.data.verification`).

Fonctions pures, aucun appel. Textes factices (D1) : seules les marques que les contrôles
lisent (titres de section, marqueurs de modalité, blocs de courrier) sont écrites en clair.
"""

from __future__ import annotations

from typing import Any

import pytest

from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.data.config import VerificationConfig
from slmsp.data.validate import _controler_sources, _controler_structure, _Rejet
from slmsp.data.verification import Motif, refusee, verifier_cible

NEUTRE = VerificationConfig(gain_km_min=-1e9, non_bloquants=["nom_absent"])
"""Gain de lisibilité neutralisé : chaque test LC ne regarde que son contrôle."""

CR = (
    "Participants\n- <participant-factice>, Durandil\n- Mme Éloïse\n"
    "Points abordés\n- Budget <point-factice>\n"
    "Décisions\n- <decision-factice>\n"
    "Actions\n- <action-factice>\n"
)
TRANSCRIPTION = "<transcription-factice> durandil <x> madame eloise"
CT = (
    "<expediteur-factice>\n<destinataire-factice>\n\n[Ville], le [date]\n\n"
    "Objet : <objet-factice>\n\nRéférences : [référence]\n\nMadame, Monsieur,\n\n"
    "<corps-factice>\n\nVeuillez agréer, Madame, Monsieur, mes salutations.\n\n[Signature]\n"
)
AMORCES_CT = "type_courrier : <type-factice>\nobjet : <objet-factice>\nelements_connus : <e>"


def codes(
    tache: str, cible: str, source: str, config: VerificationConfig = NEUTRE, **kw: Any
) -> dict[str, bool]:
    fournis = kw.pop("fournis", [source])
    motifs = verifier_cible(tache, cible, source=source, fournis=fournis, config=config, **kw)
    assert all(isinstance(m, Motif) for m in motifs)
    return {m.code: m.bloquant for m in motifs}


# --- CR ------------------------------------------------------------------------------------


def test_cr_conforme_sans_motif_pieges_de_noms() -> None:
    # Nom présent en minuscule dans la transcription, « Mme » pour « Madame », accents ignorés,
    # mot capitalisé après une puce : aucun nom absent.
    assert codes("CR", CR, TRANSCRIPTION) == {}


def test_cr_nom_absent_non_bloquant_par_defaut_puis_bloquant() -> None:
    cible = CR.replace("Durandil", "Valmoreau")
    assert codes("CR", cible, TRANSCRIPTION) == {"nom_absent": False}
    stricte = VerificationConfig(non_bloquants=[])
    motifs = verifier_cible("CR", cible, source=TRANSCRIPTION, fournis=[], config=stricte)
    assert [(m.code, m.bloquant, m.extraits) for m in motifs] == [
        ("nom_absent", True, ("Valmoreau",))
    ]
    assert refusee(motifs)


def test_cr_mot_apres_point_ou_deux_points_ignore() -> None:
    cible = CR.replace("<decision-factice>", "<d>. Validation : Report <x>")
    assert codes("CR", cible, TRANSCRIPTION) == {}


def test_cr_sections_manquantes_desordre_et_actions_vide() -> None:
    assert codes("CR", CR.replace("Décisions", "<titre>"), TRANSCRIPTION) == {
        "cr_sections_manquantes": True
    }
    desordre = CR.replace("Points abordés", "<tmp>").replace("Décisions", "Points abordés")
    assert codes("CR", desordre.replace("<tmp>", "Décisions"), TRANSCRIPTION) == {
        "cr_sections_desordre": True
    }
    vide = CR.split("Actions")[0] + "Actions :\n- \n"
    assert codes("CR", vide, TRANSCRIPTION) == {"cr_actions_vide": True}


def test_cr_plafond_de_mots() -> None:
    assert codes("CR", CR, TRANSCRIPTION, plafonds_mots={"CR": 5}) == {"cr_plafond_mots": True}
    assert codes("CR", CR, TRANSCRIPTION, plafonds_mots={"CR": 400}) == {}


def test_cr_valeur_absente_avec_extrait() -> None:
    motifs = verifier_cible(
        "CR",
        CR.replace("<action-factice>", "<a> 4321 euros"),
        source=TRANSCRIPTION,
        fournis=[TRANSCRIPTION],
        config=NEUTRE,
    )
    assert [(m.code, m.bloquant, m.extraits) for m in motifs] == [
        ("valeur_absente", True, ("4321",))
    ]


# --- LC ------------------------------------------------------------------------------------


def test_lc_classe_lemmatisee_vous_devez_pour_le_demandeur_doit() -> None:
    assert codes("LC", "Vous devez <x-factice>.", "Le demandeur doit <x-factice>.") == {}


def test_lc_classe_perdue_bloquante_extrait_de_la_source() -> None:
    motifs = verifier_cible(
        "LC",
        "Vous devez <x-factice>.",
        source="Si <y-factice>, le demandeur doit <x-factice>.",
        fournis=["<f>"],
        config=NEUTRE,
    )
    assert [(m.code, m.bloquant, m.extraits) for m in motifs] == [
        ("lc_modalite_perdue", True, ("Si",))
    ]


def test_lc_baisse_du_nombre_non_bloquante() -> None:
    source = "Le demandeur doit <x>. Il doit aussi <y>."
    assert codes("LC", "Vous devez <x> et <y>.", source) == {"lc_modalite_reduite": False}


def test_lc_conseil_ajoute_et_titre() -> None:
    assert codes("LC", "Vous devez <x>. N'hésitez pas à <y>.", "Le demandeur doit <x>.") == {
        "lc_conseil_ajoute": True
    }
    assert codes("LC", "# <titre-factice>\nVous devez <x>.", "Le demandeur doit <x>.") == {
        "lc_titre": True
    }


def test_lc_valeur_perdue_et_ajoutee() -> None:
    assert codes("LC", "Vous devez <x>.", "Le demandeur doit <x> sous 45 jours.") == {
        "lc_valeur_perdue": True
    }
    en_lettres = "Vous devez <x> sous quarante-cinq jours."
    assert codes("LC", en_lettres, "Il doit <x> sous 45 jours.") == {}
    assert codes("LC", "Vous devez <x> sous 46 jours.", "Le demandeur doit <x>.") == {
        "valeur_absente": True
    }


def test_lc_gain_de_lisibilite() -> None:
    longue = "Conformément aux dispositions réglementaires applicables, l'administration procède."
    courte = "On vous aide. Tout va vite."
    config = VerificationConfig(non_bloquants=["nom_absent"])
    assert "lc_gain_lisibilite" not in codes("LC", courte, longue, config)
    assert codes("LC", longue, courte, config)["lc_gain_lisibilite"] is True
    # Défaut du dépôt (2026-10-20) : le gain par item n'est plus bloquant.
    assert codes("LC", longue, courte, VerificationConfig())["lc_gain_lisibilite"] is False


# --- CT ------------------------------------------------------------------------------------


def test_ct_conforme() -> None:
    assert codes("CT", CT, AMORCES_CT) == {}


def test_ct_bloc_absent_ou_hors_ordre() -> None:
    sans_ref = CT.replace("Références : [référence]\n\n", "")
    assert codes("CT", sans_ref, AMORCES_CT) == {"ct_blocs": True}
    inverse = CT.replace("[Ville], le [date]\n\n", "").replace(
        "[Signature]\n", "[Signature]\n\n[Ville], le [date]\n"
    )
    motifs = verifier_cible("CT", inverse, source=AMORCES_CT, fournis=[], config=NEUTRE)
    assert [(m.code, "hors d'ordre : lieu_date" in m.message) for m in motifs] == [
        ("ct_blocs", True)
    ]


def test_ct_format_de_validate_et_emplacement_non_bloquant() -> None:
    sans_objet = CT.replace("Objet : <objet-factice>\n\n", "")
    assert codes("CT", sans_objet, AMORCES_CT) == {"ct_format_incomplet": True, "ct_blocs": True}
    sans_crochets = CT.replace("[Ville], le [date]", "<lieu>, le 3 mars 2026").replace(
        "[référence]", "<ref>"
    )
    sans_crochets = sans_crochets.replace("[Signature]", "La <signataire>")
    resultat = codes("CT", sans_crochets, AMORCES_CT + " 3 mars 2026")
    assert resultat == {"ct_sans_emplacement": False}


def test_ct_nom_hors_crochets_seulement() -> None:
    avec_nom = CT.replace("<corps-factice>", "<corps> [Nom du Demandeur] et Valmoreau")
    assert codes("CT", avec_nom, AMORCES_CT) == {"nom_absent": False}


# --- Cohérence avec validate -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("tache", "cible", "source"),
    [("CR", CR, TRANSCRIPTION), ("LC", "Vous devez <x>.", "Il doit <x>."), ("CT", CT, AMORCES_CT)],
)
def test_cible_acceptee_jamais_rejetee_par_validate(tache: str, cible: str, source: str) -> None:
    assert not refusee(verifier_cible(tache, cible, source=source, fournis=[source], config=NEUTRE))
    try:
        _controler_sources(cible, tache, [], [], [source])
        _controler_structure(cible, tache, [source])
    except _Rejet as rejet:  # pragma: no cover - échec du test
        pytest.fail(f"validate rejette une cible acceptée : {rejet.motif}")


def test_tache_non_verifiee_refusee() -> None:
    with pytest.raises(ValueError):
        verifier_cible("Q", "<x>", source="<s>", fournis=[], config=NEUTRE)


# --- Configuration -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    "reglage",
    [
        {"non_bloquants": ["valeur_absente"]},
        {"non_bloquants": ["code_inconnu"]},
        {"ct_blocs": {"objet": "("}},
        {"lc_marqueurs": {"condition": []}},
    ],
)
def test_config_refusee(reglage: dict[str, Any]) -> None:
    with pytest.raises((ValueError, ConfigurationInvalide)):
        VerificationConfig(**reglage)


def test_config_du_depot_egale_aux_defauts() -> None:
    from slmsp.data.config import charger_config_donnees

    assert charger_config_donnees().verification == VerificationConfig()


def test_ct_blocs_en_gras_et_references_sans_deux_points() -> None:
    # Formes relevées au calibrage v14 : titres en gras, bloc de références entre crochets.
    gras = (
        CT.replace("[Ville], le [date]", "**[Ville], le [date]**")
        .replace("Références : [référence]", "**[Références]**\n[référence]")
        .replace("Madame, Monsieur,", "**Madame,**")
    )
    assert codes("CT", gras, AMORCES_CT) == {}


# --- Revue O6a -----------------------------------------------------------------------------


@pytest.mark.parametrize("ligne", ["Signature [nom]", "Signature", "**Signature :** [nom]"])
def test_ct_signature_en_toutes_lettres(ligne: str) -> None:
    assert codes("CT", CT.replace("[Signature]", ligne), AMORCES_CT) == {}


def test_cr_puce_actions_dans_points_abordes_sans_faux_desordre() -> None:
    cible = CR.replace("- Budget <point-factice>\n", "- Budget <point-factice>\n* Actions <x>\n")
    assert codes("CR", cible, TRANSCRIPTION) == {}
