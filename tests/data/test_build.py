"""Étape `build` (story 9.6) : re-dérivation, jeu versionné, licences, échantillon.

Chaîne complète `generate → validate → filter → build` sur les doublures de
`tests/data/conftest.py`. Aucun appel réel ; les textes sont des jetons artificiels (D1.1).
"""

from __future__ import annotations

import json
from dataclasses import replace
from typing import Any

import pytest

pytest.importorskip("mistralai")

from slmsp.core.canonique import sha256_hex  # noqa: E402
from slmsp.core.config import racine_projet  # noqa: E402
from slmsp.core.erreurs import BudgetEpuise, ManifesteInvalide, ProvenanceInvalide  # noqa: E402
from slmsp.core.schemas.entrainement import (  # noqa: E402
    LigneEntrainement,
    ManifesteJeuEntrainement,
)
from slmsp.core.schemas.session_donnees import SessionBrute  # noqa: E402
from slmsp.data import build as module_build  # noqa: E402
from slmsp.data.build import (  # noqa: E402
    ContexteBuild,
    lancer_build,
    rederiver_ligne,
    sources_de,
    verifier_octets,
)
from slmsp.data.config import charger_config_donnees  # noqa: E402
from slmsp.data.licences import RegistreLicences, SourceSansLicence, UsageInterdit  # noqa: E402
from slmsp.data.validate import (  # noqa: E402
    LecteurGeneration,
    lancer_validation,
    ouvrir_generation,
)
from slmsp.harness.taches import charger_taches  # noqa: E402
from slmsp.mcp.outils import charger_outils  # noqa: E402

from .conftest import CONFIG, OUTILS_MCP  # noqa: E402
from .test_filter import filtrer, journal_lecture, phrase, valider  # noqa: E402

PUBLIC = "AgentPublic/service-public"
TACHES = ("Q", "RD", "CR", "LC", "CO", "RE", "CT", "generique")


def pub(monde: Any, tache: str, emplacement: str, ligne: int = 1, **champs: Any) -> dict[str, Any]:
    champs.setdefault("jeu", PUBLIC)
    return monde.amorce(tache, emplacement, ligne=ligne, **champs)


def reponse(prefixe: str) -> dict[str, str]:
    return {"texte": phrase(prefixe, 12)}


def chaine(
    monde: Any, amorces: list[dict[str, Any]], reponses: list[Any], volumes: dict[str, int]
) -> tuple[Any, Any]:
    """`generate → validate → filter` ; renvoie la génération et le résultat du filtre."""
    seed = monde.ecrire_seed(amorces)
    monde.faux.reponses = reponses
    generation = monde.lancer(volumes, seed=seed)
    return generation, filtrer(monde, valider(monde, generation))


def une_lc(monde: Any) -> tuple[Any, Any]:
    return chaine(monde, [pub(monde, "LC", "texte")], [reponse("lc")], {"LC": 1})


def construire(monde: Any, filtre_id: str, variante: str = "recherche", racine: Any = None) -> Any:
    return lancer_build(
        racine=racine or monde.racine,
        filter_run_id=filtre_id,
        variante=variante,
        journal=journal_lecture(),
        registre=RegistreLicences.charger(racine=racine_projet()),
        config=charger_config_donnees(CONFIG / "donnees.toml"),
        taches=charger_taches(),
        chemin_outils=OUTILS_MCP,
        consigner=lambda _ligne: None,
    )


def toutes_taches(monde: Any, doublures: Any) -> tuple[Any, Any]:
    monde.recherche.passages = [doublures.passage()]
    amorces = [
        pub(monde, "Q", "question"),
        pub(monde, "RD", "demande"),
        monde.scenario(),
        pub(monde, "LC", "texte"),
        pub(monde, "CO", "texte", texte=f"{phrase('co', 12)} fin"),
        pub(monde, "generique", "demande"),
        pub(monde, "RE", "texte", 5),
        pub(monde, "RE", "longueur_demandee", 5),
        *(pub(monde, "CT", e, 7) for e in ("type_courrier", "objet", "elements_connus")),
    ]
    appel = doublures.appel_outil("search_datasets", {"query": doublures.factice()})
    reponses = [
        reponse("q"),
        {"appels": [appel]},
        reponse("rd"),
        reponse("tr"),
        reponse("cr"),
        reponse("lc"),
        reponse("g"),
        reponse("ct"),
        reponse("re"),
        reponse("co"),
    ]
    return chaine(monde, amorces, reponses, dict.fromkeys(TACHES, 1))


def lignes_train(resultat: Any) -> list[LigneEntrainement]:
    octets = (resultat.dossier / "train.jsonl").read_bytes()
    return [LigneEntrainement.model_validate_json(ligne) for ligne in octets.splitlines()]


def contexte(monde: Any, generation: Any) -> ContexteBuild:
    lecteur = LecteurGeneration(
        ouvrir_generation(generation.run.run_id, monde.racine), journal_lecture(), monde.racine
    )
    return ContexteBuild(
        lecteur=lecteur,
        taches=charger_taches(),
        outils=charger_outils(OUTILS_MCP),
        registre=RegistreLicences.charger(racine=racine_projet()),
    )


def sessions(generation: Any) -> list[SessionBrute]:
    return [SessionBrute.model_validate(ligne) for ligne in generation.run.lire_jsonl("brut.jsonl")]


# --- Construction du jeu ------------------------------------------------------------------------


def test_build_toutes_les_taches(monde: Any, doublures: Any) -> None:
    _, filtre = toutes_taches(monde, doublures)
    assert len(filtre.run.lire_jsonl("retenus.jsonl")) == len(TACHES)
    resultat = construire(monde, filtre.run.run_id)

    assert resultat.statut == "complet" and resultat.version == "v1"
    assert resultat.dossier == monde.racine / "data" / "train" / "v1"
    lignes = {ligne.tache: ligne for ligne in lignes_train(resultat)}
    assert set(lignes) == set(TACHES)
    taches = charger_taches()
    for code, ligne in lignes.items():
        if code == "generique":
            assert ligne.messages[0]["role"] == "user"
        else:
            assert ligne.messages[0] == {
                "role": "system",
                "content": taches.tache(code).prompt.consigne,
            }
        assert ligne.messages[-1]["role"] == "assistant"
        assert ligne.meta.version_extracteur == 1
        assert ligne.meta.generateur == "mistral-large-2512"
        assert len(ligne.meta.source) == len(ligne.meta.licence)
    # Q : passages formatés par harness.prompts ; RD : trace d'outils et `tools` du fichier figé.
    assert "[1]" in lignes["Q"].messages[1]["content"]
    assert [m["role"] for m in lignes["RD"].messages[1:]] == [
        "user",
        "assistant",
        "tool",
        "assistant",
    ]
    assert [o["function"]["name"] for o in lignes["RD"].tools] == [
        o["function"]["name"] for o in charger_outils(OUTILS_MCP)
    ]
    assert lignes["Q"].tools == []
    assert "data.gouv/reponses-outils-mcp" in lignes["RD"].meta.source
    # CR : transcription = 1er appel, compte rendu = 2e ; CO : entrée = texte fautif de Mistral.
    assert phrase("tr", 12) in lignes["CR"].messages[1]["content"]
    assert lignes["CR"].messages[-1]["content"] == phrase("cr", 12)
    assert phrase("co", 12) in lignes["CO"].messages[1]["content"]
    assert lignes["CO"].messages[-1]["content"] == f"{phrase('co', 12)} fin"  # amorce publique


def test_manifest_et_run(monde: Any, doublures: Any) -> None:
    _, filtre = toutes_taches(monde, doublures)
    resultat = construire(monde, filtre.run.run_id)
    octets = (resultat.dossier / "train.jsonl").read_bytes()
    manifeste = ManifesteJeuEntrainement.model_validate_json(
        (resultat.dossier / "MANIFEST.json").read_bytes()
    )
    assert manifeste.sha256_train == sha256_hex(octets)
    assert manifeste.version == "v1" and manifeste.variante == "recherche"
    assert manifeste.nb_lignes == len(TACHES) == sum(manifeste.comptes_par_tache.values())
    assert manifeste.run_id == resultat.run.run_id
    assert manifeste.type_run == "data-build"
    assert manifeste.sha256_train == resultat.rapport["sha256_train"]
    assert manifeste.sha_outils_mcp == sha256_hex(OUTILS_MCP.read_bytes())
    assert {"traces-q", "traces-rd", "cr", "lc"} <= set(manifeste.sha_gabarits)
    assert {"Q", "RD", "CR", "LC", "CO", "RE", "CT"} == set(manifeste.sha_prompts)
    assert manifeste.registre["sha256"] == RegistreLicences.charger(racine=racine_projet()).sha256
    assert manifeste.modeles_generateurs == ["mistral-large-2512"]
    assert manifeste.conditions_mistral.url is not None
    assert resultat.run.manifeste.type == "data-build"
    assert resultat.run.manifeste.parents == [filtre.run.run_id]
    assert resultat.run.statut_courant() == "complet"


def test_une_version_n_est_jamais_reecrite(monde: Any) -> None:
    _, filtre = une_lc(monde)
    premier = construire(monde, filtre.run.run_id)
    avant = (premier.dossier / "train.jsonl").read_bytes()
    second = construire(monde, filtre.run.run_id)
    assert (premier.version, second.version) == ("v1", "v2")
    assert (premier.dossier / "train.jsonl").read_bytes() == avant
    assert (second.dossier / "train.jsonl").read_bytes() == avant
    (monde.racine / "data" / "train" / "v7").mkdir()  # N = plus grand N existant + 1
    assert construire(monde, filtre.run.run_id).version == "v8"


def test_run_d_un_autre_type_refuse(monde: Any) -> None:
    generation, _ = une_lc(monde)
    with pytest.raises(ManifesteInvalide, match="data-filter attendu"):
        construire(monde, generation.run.run_id)
    assert not (monde.racine / "data" / "train").exists()


# --- Licences et variantes ------------------------------------------------------------------------


def test_variante_diffusable_refuse_une_source_recherche(monde: Any) -> None:
    amorce = pub(monde, "LC", "texte", jeu="AgentPublic/retriever_dataset")
    _, filtre = chaine(monde, [amorce], [reponse("lc")], {"LC": 1})
    with pytest.raises(UsageInterdit):
        construire(monde, filtre.run.run_id, "diffusable")
    assert not (monde.racine / "data" / "train").exists()
    resultat = construire(monde, filtre.run.run_id, "recherche")
    assert json.loads((resultat.dossier / "MANIFEST.json").read_bytes())["variante"] == "recherche"
    assert resultat.run.manifeste.config["variante"] == "recherche"


def test_variante_diffusable_acceptee(monde: Any) -> None:
    _, filtre = une_lc(monde)
    resultat = construire(monde, filtre.run.run_id, "diffusable")
    manifeste = json.loads((resultat.dossier / "MANIFEST.json").read_bytes())
    assert manifeste["variante"] == "diffusable"


def test_source_absente_du_registre(monde: Any) -> None:
    amorce = pub(monde, "LC", "texte", jeu="jeu/inconnu-factice")
    _, filtre = chaine(monde, [amorce], [reponse("lc")], {"LC": 1})
    with pytest.raises(SourceSansLicence):
        construire(monde, filtre.run.run_id)


def test_variante_inconnue(monde: Any) -> None:
    _, filtre = une_lc(monde)
    with pytest.raises(ValueError, match="variante inconnue"):
        construire(monde, filtre.run.run_id, "autre")


# --- Provenance -----------------------------------------------------------------------------------


def test_appel_id_inconnu(monde: Any) -> None:
    generation, _ = une_lc(monde)
    (brut,) = sessions(generation)
    inconnu = brut.model_copy(update={"appel_ids": ["0" * 32]})
    with pytest.raises(ProvenanceInvalide, match="absent du journal"):
        rederiver_ligne(contexte(monde, generation), inconnu)


def test_appel_d_usage_validation(monde: Any) -> None:
    generation, _ = une_lc(monde)
    (brut,) = sessions(generation)
    corps = {
        "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "<x>"}}]
    }
    appel_id = monde.journal().inscrire(
        session_id="validation-factice",
        usage="validation",
        modele_demande="mistral-large-latest",
        modele_resolu="mistral-large-2512",
        requete={"messages": []},
        reponse_brute=json.dumps(corps).encode(),
        reservation_id=None,
        statut="ok",
        statut_http=200,
    )
    autre = brut.model_copy(update={"appel_ids": [appel_id]})
    with pytest.raises(ProvenanceInvalide, match="usage 'validation'"):
        rederiver_ligne(contexte(monde, generation), autre)


def test_appel_d_usage_juge_second(monde: Any) -> None:
    generation, _ = une_lc(monde)
    (brut,) = sessions(generation)
    ctx = contexte(monde, generation)
    ligne = ctx.lecteur.appel(brut.appel_ids[0])
    ctx.lecteur._lignes[brut.appel_ids[0]] = replace(ligne, usage="juge-second")
    with pytest.raises(ProvenanceInvalide, match="usage 'juge-second'"):
        rederiver_ligne(ctx, brut)


def test_amorce_publique_alteree(monde: Any) -> None:
    generation, _ = une_lc(monde)
    (brut,) = sessions(generation)
    ctx = contexte(monde, generation)
    amorce = ctx.lecteur.amorces[brut.amorce_ids[0]]
    ctx.lecteur.amorces[amorce.amorce_id] = amorce.model_copy(update={"texte": amorce.texte + "x"})
    with pytest.raises(ProvenanceInvalide, match="sha_texte"):
        rederiver_ligne(ctx, brut)


def test_exemple_altere_d_un_octet(monde: Any) -> None:
    generation, _ = une_lc(monde)
    ctx = contexte(monde, generation)
    liste = sessions(generation)
    octets = module_build.serialiser([rederiver_ligne(ctx, b) for b in liste])
    verifier_octets(octets, ctx, liste)  # sans altération : passe
    cible = phrase("lc", 12).encode()
    altere = octets.replace(cible, cible + b"a", 1)
    assert altere != octets
    with pytest.raises(ProvenanceInvalide, match="différente de sa re-dérivation"):
        verifier_octets(altere, ctx, liste)
    with pytest.raises(ProvenanceInvalide, match="ligne"):
        verifier_octets(octets + octets, ctx, liste)


def test_build_echoue_sans_rien_ecrire_si_une_ligne_est_alteree(
    monde: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, filtre = une_lc(monde)
    vrai = module_build.serialiser

    def altere(lignes: Any) -> bytes:
        return vrai(lignes).replace(b"lc0x", b"lc9x", 1)

    monkeypatch.setattr(module_build, "serialiser", altere)
    with pytest.raises(ProvenanceInvalide):
        construire(monde, filtre.run.run_id)
    assert not (monde.racine / "data" / "train").exists()
    (run_build,) = (monde.racine / "runs" / "data-build").iterdir()
    assert "partiel-erreur" in (run_build / "etat.jsonl").read_text(encoding="utf-8")


def test_resultat_d_outil_hors_cassette(monde: Any, doublures: Any) -> None:
    appel = doublures.appel_outil("search_datasets", {"query": doublures.factice()})
    generation, _ = chaine(
        monde, [pub(monde, "RD", "demande")], [{"appels": [appel]}, reponse("rd")], {"RD": 1}
    )
    (brut,) = sessions(generation)
    chemin = monde.racine / brut.cassettes[0]
    cassette = json.loads(chemin.read_bytes())
    cassette["interactions"][0]["response"]["result"]["content"][0]["text"] = "<autre-factice>"
    chemin.write_text(json.dumps(cassette), encoding="utf-8")
    with pytest.raises(ProvenanceInvalide, match="absent des cassettes"):
        rederiver_ligne(contexte(monde, generation), brut)


# --- Statut et échantillon ------------------------------------------------------------------------


def test_echantillon_de_relecture_dans_le_run(monde: Any) -> None:
    amorces = [pub(monde, "LC", "texte", i) for i in range(1, 6)]
    reponses = [reponse(f"l{i}") for i in range(1, 6)]
    _, filtre = chaine(monde, amorces, reponses, {"LC": 5})
    config = charger_config_donnees(CONFIG / "donnees.toml")
    resultat = construire(monde, filtre.run.run_id)
    echantillon = resultat.run.lire_jsonl("echantillon-relecture.jsonl")
    attendu = min(config.relecture.taille_echantillon, 5)
    assert len(echantillon) == attendu
    lignes = lignes_train(resultat)
    for entree in echantillon:
        rang = entree.pop("rang")
        assert LigneEntrainement.model_validate(entree) == lignes[rang]
    assert resultat.rapport["echantillon_relecture"] == attendu
    second = construire(monde, filtre.run.run_id)  # tirage reproductible : même graine
    assert [e["rang"] for e in second.run.lire_jsonl("echantillon-relecture.jsonl")] == [
        e["rang"] for e in resultat.run.lire_jsonl("echantillon-relecture.jsonl")
    ]


def test_statut_partiel_herite_du_parent(monde: Any) -> None:
    amorces = [pub(monde, "RE", e, i) for i in (1, 2) for e in ("texte", "longueur_demandee")]
    seed = monde.ecrire_seed(amorces)
    monde.faux.reponses = [reponse("re"), reponse("ri")]
    generation = monde.lancer({"RE": 2}, seed=seed)
    appels: list[str] = []

    def epuise(session_id: str, *_args: Any) -> tuple[bool, str]:
        if appels:
            raise BudgetEpuise("plafond")
        appels.append(session_id)
        return True, "ok"

    validation = lancer_validation(
        racine=monde.racine,
        generate_run_id=generation.run.run_id,
        journal=journal_lecture(),
        controle=epuise,
        chemin_outils=OUTILS_MCP,
        consigner=lambda _ligne: None,
    )
    filtre = filtrer(monde, validation)
    assert filtre.statut == "partiel-budget"
    resultat = construire(monde, filtre.run.run_id)
    assert resultat.statut == "partiel-budget"
    assert resultat.run.statut_courant() == "partiel-budget"
    manifeste = json.loads((resultat.dossier / "MANIFEST.json").read_bytes())
    assert manifeste["statut"] == "partiel-budget"


def test_jeu_construit_lu_par_train_run(monde: Any, doublures: Any) -> None:
    """Contrat 9.6 → 10.4 : `train.chargement.charger_jeu` accepte le jeu produit."""
    from slmsp.train import chargement

    _, filtre = toutes_taches(monde, doublures)
    resultat = construire(monde, filtre.run.run_id)
    jeu = chargement.charger_jeu(resultat.version, racine=monde.racine)
    assert jeu.ligne()["run_build"] == resultat.run.run_id
    assert jeu.sha256 == resultat.rapport["sha256_train"]
    assert len(jeu.lignes) == len(TACHES)
    assert {ligne.tache for ligne in jeu.lignes} == set(TACHES)


def test_longueur_config_exige_son_amorce_liee_dans_la_session() -> None:
    """Une amorce `config` ne compte aucune source mais doit voir son amorce liée dans la
    session (sinon `ProvenanceInvalide`)."""
    from types import SimpleNamespace

    from slmsp.core.schemas.amorce import Amorce

    longueur = Amorce(
        schema_version=1,
        amorce_id="re.longueur_demandee.1",
        tache="RE",
        emplacement="longueur_demandee",
        texte="moyenne",
        sha_texte=sha256_hex("moyenne"),
        auteur_contenu="config",
        lie_a="re.texte.1",
    )
    from slmsp.data.validate import LecteurGeneration

    lecteur = SimpleNamespace(amorces={longueur.amorce_id: longueur})
    lecteur.amorce_verifiee = lambda i: LecteurGeneration.amorce_verifiee(lecteur, i)  # type: ignore[arg-type]
    ctx = SimpleNamespace(lecteur=lecteur)

    def session(amorce_ids: list[str]) -> SessionBrute:
        return SessionBrute(
            session_id="re-" + "0" * 24,
            tache="RE",
            appel_ids=["a" * 32],
            amorce_ids=amorce_ids,
            appels_nouveaux=1,
            appels_reutilises=0,
        )

    with pytest.raises(ProvenanceInvalide, match="liée"):
        sources_de(ctx, session(["re.longueur_demandee.1", "re.texte.2"]))  # type: ignore[arg-type]
    ctx.lecteur.amorces["re.texte.1"] = Amorce(
        schema_version=1,
        amorce_id="re.texte.1",
        tache="RE",
        emplacement="texte",
        texte="<texte-factice>",
        sha_texte=sha256_hex("<texte-factice>"),
        auteur_contenu="public",
        jeu="jeu-factice",
        revision="r1",
        ligne=0,
    )
    session_liee = session(["re.longueur_demandee.1", "re.texte.1"])
    assert sources_de(ctx, session_liee) == sorted({"jeu-factice", "mistral/reponses-generateur"})  # type: ignore[arg-type]
