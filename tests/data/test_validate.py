"""Étape `validate` (story 9.5) : rejeu des traces, URL, valeurs et fidélité.

Les runs `generate` viennent du faux serveur Mistral et du port d'outils factices
(`tests/data/conftest.py`). Aucun appel réel. Les réponses sont des jetons constants ou
aléatoires `<…-factice-…>` (D1.1) ; les URL et valeurs sont fabriquées par le test.
"""

from __future__ import annotations

import json
import secrets
from typing import Any

import pytest

pytest.importorskip("mistralai")

from slmsp.core.erreurs import AppelNonConforme, BudgetEpuise, ManifesteInvalide  # noqa: E402
from slmsp.core.schemas.cassette import Cassette  # noqa: E402
from slmsp.core.var import dossier_var  # noqa: E402
from slmsp.data.validate import (  # noqa: E402
    ControleMistral,
    _Rejet,
    lancer_validation,
    statut_herite,
)
from slmsp.harness.taches import charger_taches  # noqa: E402
from slmsp.mistral.config import charger_mistral  # noqa: E402
from slmsp.mistral.journal import journal_pour  # noqa: E402

from .conftest import CONFIG, OUTILS_MCP, factice  # noqa: E402

TEXTE = "<reponse-factice>"
CR_CONFORME = "Participants\n<p>\nPoints abordés\n<p>\nDécisions\n<p>\nActions\n<p>"
"""Réponse CR factice qui porte les quatre titres de section (contrôle de structure, S5)."""


def journal_lecture() -> Any:
    return journal_pour("generation", charger_mistral(), dossier_var(), lecteur="data")


def valider(monde: Any, generation: Any, controle: Any = None) -> Any:
    return lancer_validation(
        racine=monde.racine,
        generate_run_id=generation.run.run_id,
        journal=journal_lecture(),
        controle=controle,
        chemin_outils=OUTILS_MCP,
        consigner=lambda _ligne: None,
    )


def motifs(resultat: Any) -> list[str]:
    return [r["motif"] for r in resultat.run.lire_jsonl("rejets.jsonl")]


def trace_rd(monde: Any, doublures: Any, final: str = TEXTE) -> Any:
    """Un run `generate` d'une session RD : un tour d'outils, puis la réponse `final`."""
    seed = monde.ecrire_seed([monde.amorce("RD", "demande", ligne=1)])
    appel = doublures.appel_outil("search_datasets", {"query": factice()})
    monde.faux.reponses = [{"appels": [appel]}, {"texte": final}]
    return monde.lancer({"RD": 1}, seed=seed)


def une_session(monde: Any, tache: str, emplacements: list[str], final: str, **amorce: Any) -> Any:
    seed = monde.ecrire_seed([monde.amorce(tache, e, ligne=1, **amorce) for e in emplacements])
    monde.faux.reponses = [{"texte": final}]
    return monde.lancer({tache: 1}, seed=seed)


# --- Rejeu des traces RD ----------------------------------------------------------------------


def test_trace_conforme_validee(monde: Any, doublures: Any) -> None:
    generation = trace_rd(monde, doublures)
    resultat = valider(monde, generation)
    assert resultat.statut == "complet"
    assert len(resultat.run.lire_jsonl("valides.jsonl")) == 1
    assert resultat.run.lire_jsonl("rejets.jsonl") == []
    assert resultat.rapport["taches"]["RD"] == {
        "exemples": 1,
        "retenus": 1,
        "rejets": {},
        "taux_rejet": 0.0,
    }
    assert resultat.run.manifeste.parents == [generation.run.run_id]
    assert len(monde.faux.corps) == 2  # validate n'appelle pas Mistral


def test_valides_reprennent_les_lignes_brutes(monde: Any, doublures: Any) -> None:
    generation = trace_rd(monde, doublures)
    resultat = valider(monde, generation)
    assert resultat.run.lire_jsonl("valides.jsonl") == generation.run.lire_jsonl("brut.jsonl")


def test_trace_divergente_quand_la_cassette_change(monde: Any, doublures: Any) -> None:
    generation = trace_rd(monde, doublures)
    (brut,) = generation.run.lire_jsonl("brut.jsonl")
    chemin = monde.racine / brut["cassettes"][0]
    cassette = Cassette.model_validate_json(chemin.read_bytes())
    reponse = json.loads(json.dumps(cassette.interactions[0].response))
    reponse["result"]["content"][0]["text"] = factice("autre")
    cassette.interactions[0].response = reponse
    chemin.write_text(cassette.model_dump_json(), encoding="utf-8")

    resultat = valider(monde, generation)
    assert motifs(resultat) == ["trace_divergente"]
    assert resultat.rapport["taches"]["RD"]["taux_rejet"] == 1.0
    assert resultat.run.lire_jsonl("valides.jsonl") == []


def test_trace_divergente_cassette_absente(monde: Any, doublures: Any) -> None:
    generation = trace_rd(monde, doublures)
    (brut,) = generation.run.lire_jsonl("brut.jsonl")
    (monde.racine / brut["cassettes"][0]).unlink()
    assert motifs(valider(monde, generation)) == ["trace_divergente"]


def test_appel_non_conforme(monde: Any, doublures: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    generation = trace_rd(monde, doublures)

    def refuser(*_args: Any, **_kwargs: Any) -> None:
        raise AppelNonConforme("appel hors schéma")

    monkeypatch.setattr("slmsp.mcp.bac_a_sable.valider_appel", refuser)
    resultat = valider(monde, generation)
    assert motifs(resultat) == ["appel_non_conforme"]
    assert resultat.rapport["taches"]["total"]["rejets"] == {"appel_non_conforme": 1}


# --- URL et valeurs ---------------------------------------------------------------------------


def test_url_inventee(monde: Any) -> None:
    url = f"https://exemple.invalid/{secrets.token_hex(4)}"
    generation = une_session(monde, "generique", ["demande"], f"{TEXTE} {url}")
    resultat = valider(monde, generation)
    assert motifs(resultat) == ["url_inventee"]
    assert url not in json.dumps(resultat.run.lire_jsonl("rejets.jsonl"))


def test_url_de_l_amorce_acceptee(monde: Any) -> None:
    url = f"https://exemple.invalid/{secrets.token_hex(4)}"
    generation = une_session(
        monde, "generique", ["demande"], f"{TEXTE} {url}", texte=f"{factice()} {url}"
    )
    assert motifs(valider(monde, generation)) == []


def test_url_d_un_passage_acceptee(monde: Any, doublures: Any) -> None:
    url = f"https://exemple.invalid/{secrets.token_hex(4)}"
    monde.recherche.passages = [doublures.passage(url)]
    generation = une_session(monde, "Q", ["question"], f"{TEXTE} [1] {url}")
    assert motifs(valider(monde, generation)) == []


def test_valeur_absente_et_valeur_presente(monde: Any) -> None:
    source = f"{factice()} 1234,5 euros"
    generation = une_session(monde, "LC", ["texte"], f"{TEXTE} 4321 euros", texte=source)
    assert motifs(valider(monde, generation)) == ["valeur_absente"]

    monde.faux.reponses = [{"texte": f"{TEXTE} 1 234,50 euros et 7 jours"}]
    seed = monde.ecrire_seed([monde.amorce("LC", "texte", ligne=2, texte=source)])
    generation = monde.lancer({"LC": 1}, seed=seed)
    assert motifs(valider(monde, generation)) == []  # même valeur, petit entier ignoré


def test_co_garde_les_valeurs_de_la_source(monde: Any) -> None:
    source = f"{factice()} 1234,5 euros le 2026"
    generation = une_session(monde, "CO", ["texte"], f"{TEXTE} 1234,5 euros", texte=source)
    assert motifs(valider(monde, generation)) == ["infidele"]  # 2026 perdu

    monde.faux.reponses = [{"texte": f"{TEXTE} 1234,5 euros le 2027"}]
    seed = monde.ecrire_seed([monde.amorce("CO", "texte", ligne=2, texte=source)])
    generation = monde.lancer({"CO": 1}, seed=seed)
    assert motifs(valider(monde, generation)) == ["valeur_absente"]

    monde.faux.reponses = [{"texte": f"{TEXTE} 2026 et 1 234,50 euros"}]
    seed = monde.ecrire_seed([monde.amorce("CO", "texte", ligne=3, texte=source)])
    generation = monde.lancer({"CO": 1}, seed=seed)
    assert motifs(valider(monde, generation)) == []


def test_ct_valeur_inventee(monde: Any) -> None:
    emplacements = ["type_courrier", "objet", "elements_connus"]
    generation = une_session(monde, "CT", emplacements, f"{TEXTE} 98765 euros")
    assert motifs(valider(monde, generation)) == ["valeur_absente"]


def test_statut_herite_du_parent() -> None:
    class Parent:
        run_id = "parent"

        def __init__(self, statut: str) -> None:
            self.statut = statut

        def statut_courant(self) -> str:
            return self.statut

    assert statut_herite(Parent("complet"), "complet", None) == ("complet", None)  # type: ignore[arg-type]
    assert statut_herite(Parent("partiel-budget"), "complet", None)[0] == "partiel-budget"  # type: ignore[arg-type]
    assert statut_herite(Parent("interrompu"), "complet", None)[0] == "partiel-erreur"  # type: ignore[arg-type]
    assert statut_herite(Parent("partiel-erreur"), "partiel-budget", "b") == ("partiel-budget", "b")  # type: ignore[arg-type]


def test_valeur_non_controlee_hors_taches_a_source(monde: Any) -> None:
    generation = une_session(monde, "generique", ["demande"], f"{TEXTE} 987654")
    assert motifs(valider(monde, generation)) == []


def test_valeur_d_un_passage_acceptee(monde: Any, doublures: Any) -> None:
    pas = doublures.passage()
    monde.recherche.passages = [pas.__class__(**{**pas.__dict__, "texte": f"{factice()} 2468 €"})]
    generation = une_session(monde, "Q", ["question"], f"{TEXTE} [1] 2468 euros")
    assert motifs(valider(monde, generation)) == []


# --- Fidélité ---------------------------------------------------------------------------------


class Controle:
    def __init__(self, fidele: bool) -> None:
        self.fidele = fidele
        self.appels: list[tuple[str, str, str]] = []

    def __call__(self, session_id: str, source: str, texte: str) -> tuple[bool, str]:
        self.appels.append((session_id, source, texte))
        return self.fidele, "controle factice"


def test_controle_de_fidelite_rejette(monde: Any) -> None:
    generation = une_session(monde, "LC", ["texte"], TEXTE)
    controle = Controle(False)
    resultat = valider(monde, generation, controle)
    assert motifs(resultat) == ["infidele"]
    assert len(controle.appels) == 1
    assert resultat.run.manifeste.config["controle_mistral"] is True


def test_controle_de_fidelite_cible_les_taches(monde: Any) -> None:
    generation = une_session(monde, "generique", ["demande"], TEXTE)
    controle = Controle(False)
    assert motifs(valider(monde, generation, controle)) == []
    assert controle.appels == []  # generique n'est pas contrôlée


def test_budget_epuise_pendant_le_controle(monde: Any) -> None:
    generation = une_session(monde, "RE", ["texte", "longueur_demandee"], TEXTE)

    def epuise(*_args: Any) -> tuple[bool, str]:
        raise BudgetEpuise("plafond")

    resultat = valider(monde, generation, epuise)
    assert resultat.statut == "partiel-budget"
    assert resultat.run.statut_courant() == "partiel-budget"
    assert resultat.rapport["non_jugees"] == 1


def test_controle_mistral_usage_validation_et_idempotence(monde: Any) -> None:
    controle = ControleMistral(
        monde.client(), journal_lecture(), dossier_gabarits=CONFIG / "prompts" / "generateur"
    )
    source, texte = factice("source"), factice("texte")
    monde.faux.reponses = [{"texte": "FIDELE"}, {"texte": "INFIDELE\n<affirmation-factice>"}]

    assert controle("lc-0001", source, texte)[0] is True
    requetes = len(monde.faux.corps)
    assert controle("lc-0001", source, texte)[0] is True  # relu au journal, pas repayé
    assert len(monde.faux.corps) == requetes
    assert source in monde.faux.corps[0]["messages"][0]["content"]
    assert texte in monde.faux.corps[0]["messages"][0]["content"]
    assert controle("lc-0002", source, factice("autre"))[0] is False
    assert {ligne["usage"] for ligne in monde.journal_lignes()} == {"validation"}


# --- Rapport et préalables --------------------------------------------------------------------


def test_rapport_par_tache_et_par_motif(monde: Any) -> None:
    url = f"https://exemple.invalid/{secrets.token_hex(4)}"
    seed = monde.ecrire_seed(
        [
            monde.amorce("generique", "demande", ligne=1),
            monde.amorce("generique", "demande", ligne=2),
            monde.amorce("generique", "demande", ligne=3),
            monde.amorce("LC", "texte", ligne=1),
        ]
    )
    monde.faux.reponses = [
        {"texte": TEXTE},
        {"texte": f"{TEXTE} {url}"},
        {"texte": f"{TEXTE} {url}"},
        {"texte": TEXTE},
    ]
    generation = monde.lancer({"generique": 3, "LC": 1}, seed=seed)
    taches = valider(monde, generation).rapport["taches"]
    assert taches["generique"] == {
        "exemples": 3,
        "retenus": 1,
        "rejets": {"url_inventee": 2},
        "taux_rejet": round(2 / 3, 6),
    }
    assert taches["LC"]["taux_rejet"] == 0.0
    assert taches["total"]["exemples"] == 4 and taches["total"]["retenus"] == 2


def test_run_d_un_autre_type_refuse(monde: Any) -> None:
    seed = monde.ecrire_seed([monde.amorce("generique", "demande", ligne=1)])
    with pytest.raises(ManifesteInvalide):
        lancer_validation(
            racine=monde.racine,
            generate_run_id=seed,
            journal=journal_lecture(),
            chemin_outils=OUTILS_MCP,
            consigner=lambda _ligne: None,
        )
    assert not (monde.racine / "runs" / "data-validate").exists()


# --- Longueur des résumés RE ----------------------------------------------------------------


def session_re(monde: Any, longueur: str, mots: int) -> Any:
    seed = monde.ecrire_seed(
        [
            monde.amorce("RE", "texte", ligne=1),
            monde.amorce("RE", "longueur_demandee", ligne=1, texte=longueur),
        ]
    )
    monde.faux.reponses = [{"texte": " ".join(["mot"] * mots)}]
    return monde.lancer({"RE": 1}, seed=seed)


@pytest.mark.parametrize(
    ("longueur", "mots", "rejet"),
    [
        ("courte", 80, False),
        ("courte", 81, True),
        ("moyenne", 81, False),
        ("moyenne", 201, True),
        ("detaillee", 400, False),
        ("detaillee", 401, True),
    ],
)
def test_re_au_dela_du_plafond_de_sa_longueur_rejete(
    monde: Any, longueur: str, mots: int, rejet: bool
) -> None:
    resultat = valider(monde, session_re(monde, longueur, mots))
    assert motifs(resultat) == (["longueur_depassee"] if rejet else [])
    if rejet:
        (ligne,) = resultat.run.lire_jsonl("rejets.jsonl")
        assert str(mots) in ligne["detail"]
        assert "mot mot" not in ligne["detail"]  # aucun texte généré dans le rejet


# -- Contrôle des valeurs : plafond RE et dates (correctif campagne 9.8) --


def _sources(texte: str, tache: str, source: str) -> None:
    from slmsp.data.validate import _controler_sources

    _controler_sources(texte, tache, [], [], [source])


@pytest.mark.parametrize(
    "texte",
    [
        "<titre>\n<résumé-factice> (80 mots max.)",
        "<résumé-factice> (199 mots)",
        "<résumé-factice> de 200 mots au plus",
    ],
)
def test_re_plafond_de_mots_et_annotation_admis(texte: str) -> None:
    _sources(texte, "RE", "<source-factice>")


def test_re_montant_invente_reste_rejete() -> None:
    from slmsp.data.validate import _Rejet

    with pytest.raises(_Rejet) as erreur:
        _sources("<résumé-factice> (80 mots max.) pour 1234 euros", "RE", "<source-factice> 99")
    assert erreur.value.motif == "valeur_absente"


def test_plafond_non_admis_hors_re() -> None:
    from slmsp.data.validate import _Rejet

    with pytest.raises(_Rejet):
        _sources("<réponse-factice> 80", "Q", "<source-factice>")


@pytest.mark.parametrize(
    ("source", "sortie"),
    [
        ("<s> 2021-04-20 <s>", "<r> le 20 avril 2021 <r>"),
        ("<s> 20 avril 2021 <s>", "<r> 20/04/2021 <r>"),
        ("<s> 05/11/2022 <s>", "<r> 5 novembre 2022 <r>"),
        ("<s> 1er mars 2020 <s>", "<r> 2020-03-01 <r>"),
    ],
)
def test_dates_normalisees_des_deux_cotes(source: str, sortie: str) -> None:
    _sources(sortie, "RD", source)


def test_date_inventee_rejetee() -> None:
    from slmsp.data.validate import _Rejet

    with pytest.raises(_Rejet):
        _sources("<r> le 21 avril 2021 <r>", "RD", "<s> 2021-04-20 <s>")


@pytest.mark.parametrize(
    "texte",
    [
        "<résumé-factice> Le montant est de 200 euros.",
        "<résumé-factice> Il y a 400 agents.",
        "<résumé-factice> (150 mots : soit 1234 euros) fin.",
        "<résumé-factice> (80 mots max.) puis 80 euros.",
    ],
)
def test_re_plafond_hors_annotation_rejete(texte: str) -> None:
    from slmsp.data.validate import _Rejet

    with pytest.raises(_Rejet) as erreur:
        _sources(texte, "RE", "<source-factice> 99 euros")
    assert erreur.value.motif == "valeur_absente"


def test_amorce_tronquee_rejetee(monde: Any) -> None:
    seed = monde.ecrire_seed([monde.scenario(finish_reason="length")])
    monde.faux.reponses = [{"texte": TEXTE}]
    generation = monde.lancer({"CR": 1}, seed=seed)
    resultat = valider(monde, generation)
    assert motifs(resultat) == ["amorce_tronquee"]
    assert resultat.rapport["taches"]["CR"]["rejets"] == {"amorce_tronquee": 1}
    assert resultat.run.lire_jsonl("valides.jsonl") == []


def test_amorce_mistral_saine_inchangee(monde: Any) -> None:
    seed = monde.ecrire_seed([monde.scenario()])
    monde.faux.reponses = [{"texte": TEXTE}, {"texte": CR_CONFORME}]
    generation = monde.lancer({"CR": 1}, seed=seed)
    resultat = valider(monde, generation)
    assert motifs(resultat) == []
    assert len(resultat.run.lire_jsonl("valides.jsonl")) == 1


def _alterer_brut(generation: Any, **champs: Any) -> None:
    """Réécrit l'unique ligne de `brut.jsonl` avec `champs` (session devenue non prouvable)."""
    chemin = generation.run.dossier / "brut.jsonl"
    (brut,) = generation.run.lire_jsonl("brut.jsonl")
    brut.update(champs)
    chemin.write_text(json.dumps(brut) + "\n", encoding="utf-8")


@pytest.mark.parametrize(
    ("champs", "motif"),
    [
        ({"amorce_ids": ["generique.demande.jeu.999999"]}, "amorce_invalide"),
        ({"appel_ids": ["f" * 32]}, "appel_invalide"),
    ],
)
def test_provenance_introuvable_rejetee_sans_erreur(
    monde: Any, champs: dict[str, Any], motif: str
) -> None:
    generation = une_session(monde, "generique", ["demande"], TEXTE)
    _alterer_brut(generation, **champs)
    resultat = valider(monde, generation)
    assert resultat.statut == "complet"  # session rejetée, run non interrompu
    assert motifs(resultat) == [motif]


def test_reponse_tronquee_rejetee(monde: Any) -> None:
    """Défense en profondeur : `generate` abandonne déjà une réponse tronquée, mais une session
    qui en référence une (run ancien, `brut.jsonl` altéré) est rejetée, comme `build` la refuse."""
    generation = une_session(monde, "generique", ["demande"], TEXTE)
    tronque = monde.scenario(finish_reason="length")["appel_id"]  # ligne `length` du journal
    _alterer_brut(generation, appel_ids=[tronque])
    resultat = valider(monde, generation)
    assert resultat.statut == "complet"
    assert motifs(resultat) == ["reponse_tronquee"]
    assert resultat.run.lire_jsonl("valides.jsonl") == []


# --- Refus de `build` vérifiés dès `validate` (F4) --------------------------------------------


def test_entree_refusee_par_la_tache(monde: Any) -> None:
    from slmsp.data.validate import LecteurGeneration, ouvrir_generation, valider_session

    generation = une_session(monde, "LC", ["texte"], TEXTE)
    lecteur = LecteurGeneration(
        ouvrir_generation(generation.run.run_id, monde.racine), journal_lecture(), monde.racine
    )
    (brut,) = lecteur.sessions()
    double = brut.model_copy(update={"amorce_ids": [*brut.amorce_ids, *brut.amorce_ids]})
    with pytest.raises(_Rejet) as exc:
        valider_session(lecteur, double, chemin_outils=OUTILS_MCP, taches=charger_taches())
    assert exc.value.motif == "entree_refusee"


def test_conversation_invalide(monde: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    from slmsp.core.messages import ConversationInvalide
    from slmsp.data import build

    def refuser(_messages: Any) -> None:
        raise ConversationInvalide("<conversation-factice>")

    monkeypatch.setattr(build, "valider_conversation", refuser)
    generation = une_session(monde, "generique", ["demande"], TEXTE)
    assert motifs(valider(monde, generation)) == ["conversation_invalide"]


def test_session_conforme_reste_retenue_avec_la_derivation(monde: Any) -> None:
    generation = une_session(monde, "generique", ["demande"], TEXTE)
    resultat = valider(monde, generation)
    assert motifs(resultat) == []
    assert len(resultat.run.lire_jsonl("valides.jsonl")) == 1
