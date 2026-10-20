"""Story O6b : régénération des cibles refusées avec leurs motifs (`generate --verifiee`).

Doublures de `tests/data/conftest.py` (Mistral) et du banc OpenRouter de `test_juge_donnees`,
aucun appel réel ; textes factices (D1). Le test D1 reconstruit la requête de régénération
depuis le seul gabarit de correction, les amorces de la session et le bloc rendu (phrases
fixes, extraits vérifiés) : toute autre chaîne le fait échouer ; aucun texte libre du juge.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("mistralai")

from slmsp.core.config import racine_projet  # noqa: E402
from slmsp.core.erreurs import ManifesteInvalide, ProvenanceInvalide  # noqa: E402
from slmsp.core.gabarits import valider_gabarit  # noqa: E402
from slmsp.core.schemas.amorce import Amorce  # noqa: E402
from slmsp.core.schemas.session_donnees import SessionBrute  # noqa: E402
from slmsp.data.build import construire_conversation  # noqa: E402
from slmsp.data.config import VerificationConfig  # noqa: E402
from slmsp.data.generation_verifiee import Verificateur  # noqa: E402
from slmsp.data.juge_donnees import PlafondEstimeDepasse  # noqa: E402
from slmsp.data.sessions import ResolveurPassages  # noqa: E402
from slmsp.data.validate import LecteurGeneration  # noqa: E402
from slmsp.harness.taches import charger_taches  # noqa: E402
from slmsp.mistral.generateur import (  # noqa: E402
    MotifCorrection,
    charger_plafonds_mots,
)

from .test_build import pub, reponse_cr  # noqa: E402
from .test_filter import journal_lecture, valider  # noqa: E402
from .test_generation_verifiee import BONNE, SOURCE, banc_factice  # noqa: E402
from .test_juge_donnees import juge, sortie  # noqa: E402

GABARITS = racine_projet() / "config" / "prompts" / "generateur"
REFUSEE = f"{BONNE} 98765 euros."
CONFIG = VerificationConfig(gain_km_min=-1e9)


def verificateur(j: Any = None, essais_max: int = 3, **kw: Any) -> Verificateur:
    return Verificateur(
        CONFIG, plafonds_mots={"LC": 150, "CR": 400}, juge=j, essais_max=essais_max, **kw
    )


def phrases() -> dict[str, str]:
    return dict(valider_gabarit(GABARITS / "corrections.md").emplacements)


def consigne(gabarit_id: str) -> str:
    chemin = GABARITS / f"{gabarit_id}.md"
    return valider_gabarit(chemin, cles_optionnelles=("max_tokens",)).consigne


def plafond(monde: Any, tache: str) -> str:
    return str(charger_plafonds_mots(monde.racine / "config" / "donnees.toml")[tache])


def lancer_lc(monde: Any, reponses: list[str], v: Verificateur, **kw: Any) -> Any:
    seed = kw.pop("seed", None) or monde.ecrire_seed([pub(monde, "LC", "texte", texte=SOURCE)])
    monde.faux.reponses = [{"texte": r} for r in reponses]
    return monde.lancer({"LC": 1}, seed=seed, verificateur=v, **kw)


def requete(monde: Any, rang: int) -> str:
    [message] = monde.faux.corps[rang]["messages"]
    assert message["role"] == "user"
    return str(message["content"])


# --- Boucle -----------------------------------------------------------------------------------


def test_refus_des_tests_puis_regeneration_retenue_et_prompt_d1(monde: Any) -> None:
    resultat = lancer_lc(monde, [REFUSEE, BONNE], verificateur())
    run = resultat.run
    assert resultat.statut == "complet" and len(monde.faux.corps) == 2
    [ligne] = run.lire_jsonl("verification.jsonl")
    assert ligne["issue"] == "retenue" and len(ligne["essais"]) == 2
    premier, second = ligne["essais"]
    assert premier["refus_par"] == "tests" and second["refus_par"] is None
    [brut] = run.lire_jsonl("brut.jsonl")
    assert brut["appel_ids"] == second["appel_ids"] != premier["appel_ids"]
    [corrections] = [
        a for a in run.lire_jsonl("amorces-derivees.jsonl") if a["auteur_contenu"] == "verification"
    ]
    assert corrections["amorce_id"].startswith(f"corr-{brut['session_id']}-e2-")
    assert corrections["amorce_id"] not in brut["amorce_ids"] + brut["amorces_derivees"]
    rapport = json.loads((run.dossier / "rapport.json").read_bytes())
    assert rapport["taches"]["LC"]["acceptees_apres_1_regeneration"] == 1

    # D1 : requête = gabarit de correction + amorce de la session + bloc des seuls éléments admis.
    [motif] = [m for m in premier["motifs"] if m["bloquant"]]
    assert motif["code"] == "valeur_absente" and motif["extraits"]
    assert all(e in REFUSEE for e in motif["extraits"])
    textes = phrases()
    cites = " ; ".join(f"« {e} »" for e in motif["extraits"])
    bloc = f"- {textes['valeur_absente']}\n  {textes['libelle_extraits']} : {cites}"
    assert corrections["texte"] == bloc
    attendu = (
        consigne("lc-correction")
        .replace("{texte}", SOURCE)
        .replace("{plafond_mots_tache}", plafond(monde, "LC"))
        .replace("{corrections}", bloc)
    )
    assert requete(monde, 1) == attendu
    assert monde.faux.corps[1]["messages"] == [{"role": "user", "content": attendu}]


def test_refus_du_juge_aucun_texte_libre_du_juge_envoye(monde: Any, tmp_path: Path) -> None:
    """Revue O6b (D1) : le motif du juge, même hors guillemets (« écrire plutôt … »,
    « remplacer X par Y »), n'entre dans aucune requête Mistral, octet par octet."""
    banc = banc_factice(tmp_path)
    refus = json.loads(sortie("LC", notes={"fidelite": 0, "termes": 1}))
    libre = "ecrire plutot : <reecriture-libre-factice>. remplacer Vous devez par <y-factice>"
    refus["criteres"]["fidelite"].update(
        motif=f"Le texte dit « Vous devez » mais il fallait « <cite-factice> ». {libre}",
        extraits=["Vous devez", "<extrait-absent-factice>"],
    )
    banc.faux.reponses.append({"texte": json.dumps(refus, ensure_ascii=False)})
    resultat = lancer_lc(monde, [BONNE, f"{BONNE} <v2>"], verificateur(juge(banc)))
    assert resultat.statut == "complet"
    [ligne] = resultat.run.lire_jsonl("verification.jsonl")
    assert [e["refus_par"] for e in ligne["essais"]] == ["juge", None]
    envoye = requete(monde, 1)
    textes = phrases()
    assert textes["juge_fidelite"] in envoye and "« Vous devez »" in envoye
    for fragment in ("cite-factice", "reecriture-libre-factice", "y-factice", "ecrire plutot"):
        assert fragment not in envoye
    assert "<extrait-absent-factice>" not in envoye
    brut = json.dumps(monde.faux.corps, ensure_ascii=False).encode("utf-8")
    assert libre.encode("utf-8") not in brut and b"reecriture-libre-factice" not in brut
    # Le motif reste consigné (verification.jsonl), jamais envoyé.
    assert any(libre in m["message"] for m in ligne["essais"][0]["motifs"])
    assert len(banc.faux.corps()) == 2


def test_trois_refus_session_ecartee(monde: Any) -> None:
    resultat = lancer_lc(monde, [REFUSEE, f"{REFUSEE} <2>", f"{REFUSEE} <3>"], verificateur())
    run = resultat.run
    assert resultat.statut == "complet" and len(monde.faux.corps) == 3
    assert run.lire_jsonl("brut.jsonl") == []
    [ecartee] = run.lire_jsonl("ecartees.jsonl")
    assert ecartee["essais"] == 3 and ecartee["codes"] == ["valeur_absente"]
    [abandon] = run.lire_jsonl("abandons.jsonl")
    assert abandon["motif"] == "verification_refusee"
    [ligne] = run.lire_jsonl("verification.jsonl")
    assert [e["essai"] for e in ligne["essais"]] == [1, 2, 3]
    corrections = [a["amorce_id"] for a in run.lire_jsonl("amorces-derivees.jsonl")]
    assert [c.split("-")[3] for c in corrections] == ["e2", "e3"]


def test_essais_max_un_ne_regenere_pas(monde: Any) -> None:
    resultat = lancer_lc(monde, [REFUSEE], verificateur(essais_max=1))
    assert len(monde.faux.corps) == 1 and resultat.run.lire_jsonl("brut.jsonl") == []


def test_regeneration_tronquee_ecarte_la_session(monde: Any) -> None:
    seed = monde.ecrire_seed([pub(monde, "LC", "texte", texte=SOURCE)])
    monde.faux.reponses = [{"texte": REFUSEE}, {"texte": "<x>", "finish_reason": "length"}]
    resultat = monde.lancer({"LC": 1}, seed=seed, verificateur=verificateur())
    [abandon] = resultat.run.lire_jsonl("abandons.jsonl")
    assert abandon["motif"] == "reponse_tronquee"
    [ecartee] = resultat.run.lire_jsonl("ecartees.jsonl")
    assert ecartee["refus_par"] == "regeneration" and ecartee["essais"] == 2


def test_rejeu_sans_nouvel_appel(monde: Any) -> None:
    seed = monde.ecrire_seed([pub(monde, "LC", "texte", texte=SOURCE)])
    premier = lancer_lc(monde, [REFUSEE, BONNE], verificateur(), seed=seed)
    appels = len(monde.faux.corps)
    rejeu = lancer_lc(monde, [], verificateur(), seed=seed)
    assert rejeu.statut == "complet" and len(monde.faux.corps) == appels
    [avant], [apres] = premier.run.lire_jsonl("brut.jsonl"), rejeu.run.lire_jsonl("brut.jsonl")
    assert apres["appel_ids"] == avant["appel_ids"] and apres["appels_nouveaux"] == 0


def test_estimation_compte_les_regenerations(monde: Any) -> None:
    lignes: list[str] = []
    seed = monde.ecrire_seed([pub(monde, "LC", "texte", texte=SOURCE)])
    with pytest.raises(PlafondEstimeDepasse):
        lancer_lc(monde, [BONNE], verificateur(), seed=seed, plafond_estime_mistral=0.0)
    lancer_lc(monde, [BONNE], verificateur(), seed=seed, consigner=lignes.append)
    assert any(ligne.startswith("estimation lc-correction : 2 appels") for ligne in lignes)


# --- CR : la transcription est gardée -------------------------------------------------------


def test_cr_regeneration_garde_la_transcription(monde: Any) -> None:
    seed = monde.ecrire_seed([pub(monde, "CR", "theme"), monde.scenario()])
    monde.faux.reponses = [{"texte": "<transcription-factice>"}, {"texte": "<cr-factice>"}]
    monde.faux.reponses.append({"texte": reponse_cr()})
    resultat = monde.lancer({"CR": 1}, seed=seed, verificateur=verificateur())
    assert resultat.statut == "complet" and len(monde.faux.corps) == 3
    [brut] = resultat.run.lire_jsonl("brut.jsonl")
    [ligne] = resultat.run.lire_jsonl("verification.jsonl")
    premier, second = ligne["essais"]
    assert brut["appel_ids"][0] == premier["appel_ids"][0] == second["appel_ids"][0]
    assert len(brut["appel_ids"]) == 2 and brut["appel_ids"][1] != premier["appel_ids"][1]
    assert len(brut["amorces_derivees"]) == 1
    envoye = requete(monde, 2)
    assert "<transcription-factice>" in envoye and phrases()["cr_sections_manquantes"] in envoye
    assert envoye.startswith(consigne("cr-correction").split("{plafond_mots_tache}", 1)[0])


# --- validate, build : session régénérée -----------------------------------------------------


def test_validate_et_build_acceptent_sans_le_bloc_de_corrections(monde: Any) -> None:
    resultat = lancer_lc(monde, [REFUSEE, BONNE], verificateur())
    assert valider(monde, resultat).run.lire_jsonl("rejets.jsonl") == []
    lecteur = LecteurGeneration(resultat.run, journal_lecture(), monde.racine)
    [brut] = lecteur.sessions()
    [ligne] = resultat.run.lire_jsonl("verification.jsonl")
    sans_regeneration = brut.model_copy(update={"appel_ids": ligne["essais"][0]["appel_ids"]})
    assert isinstance(sans_regeneration, SessionBrute)
    taches = charger_taches()
    _, regeneree = construire_conversation(lecteur, taches, brut)
    _, initiale = construire_conversation(lecteur, taches, sans_regeneration)
    assert regeneree[:-1] == initiale[:-1] and regeneree[-1]["content"] == BONNE
    [corrections] = [a for a in lecteur.amorces.values() if a.auteur_contenu == "verification"]
    texte = json.dumps(regeneree, ensure_ascii=False)
    assert corrections.texte not in texte and phrases()["valeur_absente"] not in texte


# --- Générateur : provenance de l'amorce de corrections -------------------------------------


def _generateur_apres_refus(monde: Any) -> tuple[Any, dict[str, Any], str]:
    seed = monde.ecrire_seed([pub(monde, "LC", "texte", texte=SOURCE)])
    resultat = lancer_lc(monde, [REFUSEE], verificateur(essais_max=1), seed=seed)
    [ligne] = resultat.run.lire_jsonl("verification.jsonl")
    [plan] = resultat.run.lire_jsonl("plan.jsonl")
    return monde.generateur(seed, ResolveurPassages()), plan, ligne["essais"][0]["appel_ids"][-1]


def test_amorce_de_corrections_jamais_fournie_par_l_appelant(monde: Any) -> None:
    generateur, plan, appel = _generateur_apres_refus(monde)
    session, ids = plan["session_id"], plan["amorce_ids"]
    with pytest.raises(TypeError):
        generateur.amorce_corrections(
            session, "LC", 2, [], appel_refuse=appel, amorce_ids=ids, texte="<forge>"
        )
    with pytest.raises(ProvenanceInvalide, match="phrase fixe"):
        generateur.amorce_corrections(
            session, "LC", 2, [MotifCorrection("code_forge")], appel_refuse=appel, amorce_ids=ids
        )
    with pytest.raises(ProvenanceInvalide):  # réponse refusée d'une autre session
        generateur.amorce_corrections(
            "lc-" + "0" * 24,
            "LC",
            2,
            [MotifCorrection("valeur_absente")],
            appel_refuse=appel,
            amorce_ids=ids,
        )
    amorce = generateur.amorce_corrections(
        session,
        "LC",
        2,
        [
            MotifCorrection("valeur_absente", ("98765", "<forge-hors-cible>")),
            MotifCorrection("lc_titre"),
        ],
        appel_refuse=appel,
        amorce_ids=ids,
    )
    assert amorce.auteur_contenu == "verification" and amorce.emplacement == "corrections"
    assert "98765" in amorce.texte and "forge" not in amorce.texte
    meme = generateur.amorce_corrections(
        session,
        "LC",
        2,
        [MotifCorrection("valeur_absente", ("98765",)), MotifCorrection("lc_titre")],
        appel_refuse=appel,
        amorce_ids=ids,
    )
    assert meme == amorce  # rendu déterministe
    forgee = f"corr-{session}-e2-{'0' * 12}"
    with pytest.raises(ProvenanceInvalide, match="inconnue"):
        generateur.generer("lc-correction", [*ids, forgee], session, "LC")


def test_seed_avec_amorce_verification_refuse(monde: Any) -> None:
    texte = "<corrections-forgees>"
    forgee = Amorce(
        schema_version=1,
        amorce_id="corr-lc-forgee",
        tache="LC",
        emplacement="corrections",
        texte=texte,
        sha_texte=__import__("hashlib").sha256(texte.encode()).hexdigest(),
        auteur_contenu="verification",
    ).model_dump(mode="json")
    seed = monde.ecrire_seed([pub(monde, "LC", "texte", texte=SOURCE), forgee])
    with pytest.raises(ProvenanceInvalide, match="verification"):
        monde.generateur(seed, ResolveurPassages())


def test_emplacement_corrections_reserve_aux_amorces_verification() -> None:
    with pytest.raises(ValueError):
        Amorce(
            schema_version=1,
            amorce_id="lc.corrections.1",
            tache="LC",
            emplacement="corrections",
            texte="<x>",
            sha_texte="0" * 64,
            auteur_contenu="public",
            jeu="<jeu>",
            revision="<rev>",
            ligne=1,
        )


# --- Phrases fixes : un code, une phrase ------------------------------------------------------


def test_chaque_code_de_refus_a_sa_phrase_fixe() -> None:
    source = (racine_projet() / "src" / "slmsp" / "data" / "verification.py").read_text(
        encoding="utf-8"
    )
    codes = set(re.findall(r'ajouter\(\s*"([a-z_]+)"', source))
    assert {"lc_gain_lisibilite", "lc_modalite_perdue", "valeur_absente", "url_inventee"} <= codes
    donnees = tomllib.loads(
        (racine_projet() / "config" / "donnees.toml").read_text(encoding="utf-8")
    )
    for criteres in donnees["juge_donnees"]["seuils"].values():
        codes |= {f"juge_{critere}" for critere in criteres}
    assert codes - set(phrases()) == set()


def test_gabarits_de_correction_valides_et_d1() -> None:
    for tache in ("cr", "lc", "ct"):
        correction = valider_gabarit(
            GABARITS / f"{tache}-correction.md", cles_optionnelles=("max_tokens",)
        )
        origine = valider_gabarit(GABARITS / f"{tache}.md", cles_optionnelles=("max_tokens",))
        assert set(correction.emplacements) == {*origine.emplacements, "corrections"}
        assert correction.consigne.startswith(origine.consigne)
    assert Path(GABARITS / "corrections.md").is_file()


# --- Jeu v17 : un run generate du seed parent complète un run du seed partiel ----------------


def test_completer_depuis_un_seed_partiel_qui_recopie_les_amorces(monde: Any) -> None:
    co = pub(monde, "CO", "texte", ligne=2)
    parent = monde.ecrire_seed([pub(monde, "LC", "texte", texte=SOURCE), co])
    monde.faux.reponses = [{"texte": "<co-factice>"}]
    source = monde.lancer({"CO": 1}, seed=parent)
    partiel = monde.ecrire_seed([pub(monde, "LC", "texte", ligne=3, texte=f"{SOURCE} <v17>"), co])
    appels = len(monde.faux.corps)
    resultat = lancer_lc(
        monde,
        [BONNE],
        verificateur(),
        seed=partiel,
        taches=["LC"],
        completer_depuis=source.run.run_id,
    )
    assert resultat.statut == "complet" and len(monde.faux.corps) == appels + 1
    taches = sorted(b["tache"] for b in resultat.run.lire_jsonl("brut.jsonl"))
    assert taches == ["CO", "LC"]
    assert valider(monde, resultat).run.lire_jsonl("rejets.jsonl") == []

    autre = monde.ecrire_seed([pub(monde, "LC", "texte", ligne=4), pub(monde, "CO", "texte", 2)])
    with pytest.raises(ManifesteInvalide, match="seed"):
        lancer_lc(
            monde, [], verificateur(), seed=autre, taches=["LC"], completer_depuis=source.run.run_id
        )


def test_completer_depuis_un_run_verifie_avec_juge(monde: Any, tmp_path: Path) -> None:
    banc = banc_factice(tmp_path)
    co = pub(monde, "CO", "texte", ligne=2)
    seed = monde.ecrire_seed([pub(monde, "LC", "texte", texte=SOURCE), co])
    monde.faux.reponses = [{"texte": BONNE}, {"texte": "<co-factice>"}]
    sans_juge = monde.lancer({"LC": 1, "CO": 1}, seed=seed, verificateur=verificateur())
    avec_juge = monde.lancer({"LC": 1, "CO": 1}, seed=seed, verificateur=verificateur(juge(banc)))
    assert avec_juge.statut == "complet"
    with pytest.raises(ManifesteInvalide, match="LC"):
        monde.lancer(
            {"LC": 1, "CO": 1},
            seed=seed,
            taches=["CO"],
            completer_depuis=sans_juge.run.run_id,
            verificateur=verificateur(),
        )
    complete = monde.lancer(
        {"LC": 1, "CO": 1},
        seed=seed,
        taches=["CO"],
        completer_depuis=avec_juge.run.run_id,
        verificateur=verificateur(),
    )
    assert sorted(b["tache"] for b in complete.run.lire_jsonl("brut.jsonl")) == ["CO", "LC"]


def test_v17_regenere_les_refusees_d_un_run_essais_un_sans_repayer(monde: Any) -> None:
    """Revue O6b : procédure v17. Les Tâches vérifiées sont toutes dans `--taches` ; une
    session refusée par un run source à un essai est rejouée (essai 1 relu du journal, sans
    appel), régénérée (essai 2), et les autres Tâches sont recopiées sans appel."""
    co = pub(monde, "CO", "texte", ligne=2)
    lc = pub(monde, "LC", "texte", texte=SOURCE)
    parent = monde.ecrire_seed([lc, co])
    monde.faux.reponses = [{"texte": REFUSEE}, {"texte": "<co-factice>"}]
    source = monde.lancer({"LC": 1, "CO": 1}, seed=parent, verificateur=verificateur(None, 1))
    [ecartee] = source.run.lire_jsonl("ecartees.jsonl")
    assert ecartee["tache"] == "LC" and ecartee["essais"] == 1
    partiel = monde.ecrire_seed([lc, co])
    appels = len(monde.faux.corps)
    resultat = lancer_lc(
        monde,
        [BONNE],
        verificateur(),
        seed=partiel,
        taches=["LC"],
        completer_depuis=source.run.run_id,
    )
    assert resultat.statut == "complet"
    assert len(monde.faux.corps) == appels + 1  # la seule correction est payée
    [ligne] = resultat.run.lire_jsonl("verification.jsonl")
    [avant] = source.run.lire_jsonl("verification.jsonl")
    assert [e["refus_par"] for e in ligne["essais"]] == ["tests", None]
    assert ligne["essais"][0]["appel_ids"] == avant["essais"][0]["appel_ids"]
    assert sorted(b["tache"] for b in resultat.run.lire_jsonl("brut.jsonl")) == ["CO", "LC"]


def test_completer_depuis_un_autre_seed_exige_le_meme_generateur(monde: Any) -> None:
    """Revue O6b : un run d'un autre seed d'un autre modèle du Générateur ne complète pas."""
    co = pub(monde, "CO", "texte", ligne=2)
    parent = monde.ecrire_seed([pub(monde, "LC", "texte", texte=SOURCE), co])
    monde.faux.reponses = [{"texte": "<co-factice>"}]
    source = monde.lancer({"CO": 1}, seed=parent)
    partiel = monde.ecrire_seed([pub(monde, "LC", "texte", ligne=3, texte=f"{SOURCE} <v17>"), co])
    monde.modele_generateur = "mistral-large-4"
    appels = len(monde.faux.corps)
    with pytest.raises(
        ManifesteInvalide, match="Générateur .mistral-large-latest., .mistral-large-4. attendu"
    ):
        lancer_lc(
            monde,
            [],
            verificateur(),
            seed=partiel,
            taches=["LC"],
            completer_depuis=source.run.run_id,
        )
    assert len(monde.faux.corps) == appels
