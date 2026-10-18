"""Paires de préférence ORPO (story 9.7, FR-34, D-nuit-A1-21).

Jeu SFT synthétique et `LlmPort` scripté : tous les textes sont des chaînes artificielles
(`<reponse-factice-1>`), jamais du contenu rédigé (D1.1). Aucun appel d'API, aucun modèle réel.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator, Sequence
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.artefacts import nouveau_run, ouvrir_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import ManifesteInvalide, ProvenanceInvalide
from slmsp.core.evenements import AppelOutil, Fin, Jeton
from slmsp.core.schemas.entrainement import (
    DEROGATION_ORPO,
    LigneEntrainement,
    ManifestePreferences,
    MetaLigne,
    PairePreference,
)
from slmsp.core.var import dossier_var
from slmsp.data.config import PreferencesDonnees, charger_config_donnees
from slmsp.data.preferences import lancer_preferences, normaliser
from slmsp.inference.client import ContexteServeurDepasse, ErreurInference
from slmsp.inference.journal_local import NOM_JOURNAL_LOCAL, JournalLocal

SLUG = "granite-4.0-1b"


class LlmScripte:
    """`LlmPort` minimal : une réponse (texte ou événements) par appel ; trace des options."""

    def __init__(self, *reponses: Any) -> None:
        self.reponses = list(reponses)
        self.appels: list[dict[str, Any]] = []

    def generer(
        self, messages: Sequence[Any], *, tools: Any = None, options: Any = None
    ) -> Iterator[Any]:
        self.appels.append({"messages": list(messages), "tools": tools, "options": dict(options)})
        reponse = self.reponses[min(len(self.appels), len(self.reponses)) - 1]
        if isinstance(reponse, str):
            reponse = [Jeton(texte=reponse)] if reponse else []
        yield from reponse
        yield Fin(raison="terminee")

    def compter_tokens(self, messages: Sequence[Any], tools: Any = None) -> int:
        return 0


OUTILS = [{"type": "function", "function": {"name": "<outil-factice>"}}]


def ligne_sft(numero: int) -> LigneEntrainement:
    return LigneEntrainement(
        messages=[
            {"role": "system", "content": "<prompt-factice>"},
            {"role": "user", "content": f"<question-factice-{numero}>"},
            {"role": "assistant", "content": f"<reponse-factice-{numero}>"},
        ],
        tools=OUTILS,
        tache="Q",
        meta=MetaLigne(
            generateur="<modele-factice>",
            appel_ids=[f"{numero:032x}"],
            session_id=f"q-{numero:024x}",
            version_gabarit={"<gabarit-factice>": 1},
            version_extracteur=1,
            source=["<source-factice>"],
            licence=["<licence-factice>"],
            date=date(2026, 10, 16),
        ),
    )


def ecrire_jeu_sft(racine: Path, nombre: int = 3, *, sha_altere: bool = False) -> str:
    """Run `data-build` terminé et `data/train/v1/{train.jsonl, MANIFEST.json}` ; renvoie le run."""
    run = nouveau_run("data-build", "build", {}, racine=racine)
    run.terminer("complet")
    octets = b"".join(
        json_canonique(ligne_sft(i).model_dump(mode="json")) + b"\n" for i in range(1, nombre + 1)
    )
    dossier = racine / "data" / "train" / "v1"
    dossier.mkdir(parents=True)
    (dossier / "train.jsonl").write_bytes(octets)
    manifeste = {
        "version": "v1",
        "type_run": "data-build",
        "run_id": run.run_id,
        "variante": "diffusable",
        "sha256_train": "0" * 64 if sha_altere else sha256_hex(octets),
    }
    (dossier / "MANIFEST.json").write_text(json.dumps(manifeste), encoding="utf-8")
    return run.run_id


CONFIG = PreferencesDonnees(graine=7, temperature=0.5, max_tokens=64)


def lancer(racine: Path, build_run: str, llm: LlmScripte, **options: Any) -> Any:
    return lancer_preferences(
        racine=racine,
        build_run_id=build_run,
        modele=f"base:{SLUG}",
        llm=llm,
        config=CONFIG,
        consigner=lambda _m: None,
        **options,
    )


def lignes(chemin: Path) -> list[dict[str, Any]]:
    return [json.loads(t) for t in chemin.read_text("utf-8").splitlines()]


def test_nominal_chosen_sft_rejected_local(tmp_path: Path) -> None:
    build = ecrire_jeu_sft(tmp_path)
    llm = LlmScripte(*[f"<rejetee-factice-{i}>" for i in (1, 2, 3)])
    resultat = lancer(tmp_path, build, llm)

    assert resultat.version == "v2"
    assert (tmp_path / "data" / "train" / "v1" / "train.jsonl").is_file()  # v1 inchangée
    paires = lignes(resultat.dossier / "preferences.jsonl")
    assert len(paires) == 3
    for i, paire in enumerate(paires, start=1):
        PairePreference.model_validate(paire)
        assert paire["chosen"] == [{"role": "assistant", "content": f"<reponse-factice-{i}>"}]
        assert paire["rejected"] == [{"role": "assistant", "content": f"<rejetee-factice-{i}>"}]
        assert [m["role"] for m in paire["prompt"]] == ["system", "user"]
        assert paire["meta"]["generateur_rejected"] == f"slm:{SLUG}"
    # Graine et température viennent de la configuration ; le prompt exclut la réponse choisie.
    assert [a["options"]["seed"] for a in llm.appels] == [7, 8, 9]
    assert {a["options"]["temperature"] for a in llm.appels} == {0.5}
    # Revue 9.7 : le Modèle de base reçoit les outils de l'exemple, comme au rendu ORPO.
    assert all(a["tools"] == OUTILS and len(a["messages"]) == 2 for a in llm.appels)
    assert all(paire["tools"] == OUTILS for paire in paires)


def test_generations_journalisees(tmp_path: Path) -> None:
    build = ecrire_jeu_sft(tmp_path, 2)
    resultat = lancer(tmp_path, build, LlmScripte("<rejetee-factice-1>", "<rejetee-factice-2>"))
    journal = JournalLocal()
    assert journal.chemin == dossier_var() / NOM_JOURNAL_LOCAL
    paires = lignes(resultat.dossier / "preferences.jsonl")
    for paire in paires:
        ligne = journal.lire(paire["meta"]["appel_local_id"])
        assert ligne is not None
        assert ligne["generateur"] == f"slm:{SLUG}"
        assert ligne["reponse_brute"].decode() == paire["rejected"][0]["content"]
        assert ligne["sha256_reponse"] == sha256_hex(ligne["reponse_brute"])
    with sqlite3.connect(journal.chemin) as connexion:  # ajout seul
        with pytest.raises(sqlite3.DatabaseError, match="ajout seul"):
            connexion.execute("UPDATE appels SET statut = 'x'")
        with pytest.raises(sqlite3.DatabaseError, match="ajout seul"):
            connexion.execute("DELETE FROM appels")
    connexion.close()


def test_paires_identiques_apres_normalisation_ecartees_et_comptees(tmp_path: Path) -> None:
    build = ecrire_jeu_sft(tmp_path, 4)
    llm = LlmScripte(
        "  <REPONSE-factice-1>\n",  # même texte à la casse et aux espaces près
        "<rejetee-factice-2>",
        "",  # génération vide
        [AppelOutil(id="a", nom="<outil-factice>", arguments={})],
    )
    resultat = lancer(tmp_path, build, llm)
    assert resultat.rapport["nb_paires"] == 1
    assert resultat.rapport["ecartees_par_motif"] == {"identique": 1, "non_texte": 1, "vide": 1}
    ecartees = ouvrir_run(resultat.run.run_id, racine=tmp_path).lire_jsonl("ecartees.jsonl")
    assert [e["rang"] for e in ecartees] == [0, 2, 3]
    assert normaliser("A  b") == normaliser("a B")


def test_manifest_decrit_la_derogation_sans_verdict(tmp_path: Path) -> None:
    build = ecrire_jeu_sft(tmp_path, 2)
    resultat = lancer(tmp_path, build, LlmScripte("<rejetee-factice-1>", "<rejetee-factice-2>"))
    brut = (resultat.dossier / "MANIFEST.json").read_bytes()
    manifeste = ManifestePreferences.model_validate_json(brut)
    assert manifeste.derogation_fr34 == DEROGATION_ORPO
    assert "dérogation fr-34" in manifeste.derogation_fr34.lower()
    assert manifeste.utilise_verdicts_juge is False
    assert manifeste.build_run_id == build and manifeste.jeu_sft_version == "v1"
    assert manifeste.sha256_preferences == sha256_hex(
        (resultat.dossier / "preferences.jsonl").read_bytes()
    )
    assert manifeste.run_id == resultat.run.run_id
    assert (manifeste.graine, manifeste.temperature, manifeste.max_tokens) == (7, 0.5, 64)
    assert ouvrir_run(resultat.run.run_id, racine=tmp_path).statut_courant() == "complet"


def test_aucune_paire_retenue_ne_cree_pas_de_version(tmp_path: Path) -> None:
    build = ecrire_jeu_sft(tmp_path, 2)
    with pytest.raises(ManifesteInvalide, match="aucune paire retenue"):
        lancer(tmp_path, build, LlmScripte("<reponse-factice-1>", "<reponse-factice-2>"))
    assert not (tmp_path / "data" / "train" / "v2").exists()
    (run_id,) = [p.name for p in (tmp_path / "runs" / "data-build").iterdir() if p.name != build]
    assert ouvrir_run(run_id, racine=tmp_path).statut_courant() == "partiel-erreur"


def test_jeu_sft_altere_refuse(tmp_path: Path) -> None:
    build = ecrire_jeu_sft(tmp_path, sha_altere=True)
    with pytest.raises(ProvenanceInvalide, match="SHA-256"):
        lancer(tmp_path, build, LlmScripte("<rejetee-factice-1>"))


def test_run_d_un_autre_type_refuse(tmp_path: Path) -> None:
    autre = nouveau_run("data-filter", "autre", {}, racine=tmp_path)
    autre.terminer("complet")
    with pytest.raises(ManifesteInvalide, match="data-build attendu"):
        lancer(tmp_path, autre.run_id, LlmScripte("<rejetee-factice-1>"))


def test_modele_mal_forme(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="base:<slug>"):
        lancer_preferences(
            racine=tmp_path,
            build_run_id="x",
            modele=SLUG,
            llm=LlmScripte(),
            config=CONFIG,
        )


def test_configuration_reelle_des_preferences() -> None:
    config = charger_config_donnees().preferences
    assert (config.graine, config.temperature, config.max_tokens) == (42, 0.8, 1024)


def test_cli_preferences_usage() -> None:
    assert main(["data", "build", "--preferences", "--depuis", "x"]) == CodeSortie.USAGE
    assert (
        main(["data", "build", "--preferences", "--depuis", "x", "--modele", SLUG])
        == CodeSortie.USAGE
    )
    assert (
        main(
            [
                "data",
                "build",
                "--depuis",
                "x",
                "--variante",
                "diffusable",
                "--modele",
                f"base:{SLUG}",
            ]
        )
        == CodeSortie.USAGE
    )


def test_generations_tronquees_ou_interrompues_ecartees(tmp_path: Path) -> None:
    """Revue 9.7 : une génération coupée par `max_tokens` ou interrompue n'est pas un rejected."""
    build = ecrire_jeu_sft(tmp_path, 4)
    llm = LlmScripte(
        [Jeton(texte="<rejetee-factice-1>"), Fin(raison="longueur")],
        [Jeton(texte="<rejetee-factice-2>"), Fin(raison="interrompue")],
        "<rejetee-factice-3>",
        [Jeton(texte="<rejetee-factice-4>")],  # Fin "terminee" ajoutée par LlmScripte
    )
    resultat = lancer(tmp_path, build, llm)
    assert resultat.rapport["nb_paires"] == 2
    assert resultat.rapport["ecartees_par_motif"] == {"interrompue": 1, "tronquee": 1}
    statuts = {
        JournalLocal().lire(p["meta"]["appel_local_id"])["statut"]  # type: ignore[index]
        for p in lignes(resultat.dossier / "preferences.jsonl")
    }
    assert statuts == {"ok"}


def test_flux_sans_fin_ecarte(tmp_path: Path) -> None:
    class SansFin(LlmScripte):
        def generer(self, messages: Any, *, tools: Any = None, options: Any = None) -> Any:
            yield Jeton(texte="<rejetee-factice>")

    build = ecrire_jeu_sft(tmp_path, 1)
    with pytest.raises(ManifesteInvalide, match="interrompue"):
        lancer(tmp_path, build, SansFin())


def test_echec_d_ecriture_clot_le_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Revue 9.7 : une erreur à l'écriture de la version ne laisse pas le run `en_cours`."""
    import slmsp.data.preferences as module

    def echec(*_a: Any, **_k: Any) -> Any:
        raise OSError("disque plein simulé")

    monkeypatch.setattr(module, "_creer_version", echec)
    build = ecrire_jeu_sft(tmp_path, 1)
    with pytest.raises(OSError, match="disque plein"):
        lancer(tmp_path, build, LlmScripte("<rejetee-factice-1>"))
    (run_id,) = [p.name for p in (tmp_path / "runs" / "data-build").iterdir() if p.name != build]
    assert ouvrir_run(run_id, racine=tmp_path).statut_courant() == "partiel-erreur"


def test_run_de_paires_refuse_comme_source(tmp_path: Path) -> None:
    """Revue 9.7 : un run de paires (data-build sans train.jsonl) n'est pas un jeu SFT."""
    build = ecrire_jeu_sft(tmp_path, 1)
    resultat = lancer(tmp_path, build, LlmScripte("<rejetee-factice-1>"))
    with pytest.raises(ManifesteInvalide, match="jeu SFT attendu"):
        lancer(tmp_path, resultat.run.run_id, LlmScripte("<rejetee-factice-1>"))


class LlmContexte(LlmScripte):
    """Lève `erreur` à l'appel `rang_erreur` (1-based), sinon répond comme `LlmScripte`."""

    def __init__(self, rang_erreur: int, erreur: Exception, *reponses: Any) -> None:
        super().__init__(*reponses)
        self.rang_erreur = rang_erreur
        self.erreur = erreur

    def generer(
        self, messages: Sequence[Any], *, tools: Any = None, options: Any = None
    ) -> Iterator[Any]:
        if len(self.appels) + 1 == self.rang_erreur:
            self.appels.append({})
            raise self.erreur
        yield from super().generer(messages, tools=tools, options=options)


def test_requete_hors_contexte_ecartee_et_suivantes_generees(tmp_path: Path) -> None:
    build = ecrire_jeu_sft(tmp_path, 3)
    llm = LlmContexte(
        2, ContexteServeurDepasse("HTTP 400 <exceed_context_size_error-factice>"), "<rejetee-1>"
    )
    resultat = lancer(tmp_path, build, llm)
    assert resultat.rapport["nb_paires"] == 2
    assert resultat.rapport["ecartees_par_motif"] == {"contexte": 1}
    ecartees = ouvrir_run(resultat.run.run_id, racine=tmp_path).lire_jsonl("ecartees.jsonl")
    assert ecartees == [{"rang": 1, "motif": "contexte"}]
    manifeste = json.loads((resultat.dossier / "MANIFEST.json").read_text("utf-8"))
    assert manifeste["ecartees_par_motif"] == {"contexte": 1}


def test_autre_erreur_http_arrete_le_build(tmp_path: Path) -> None:
    build = ecrire_jeu_sft(tmp_path, 3)
    llm = LlmContexte(2, ErreurInference("HTTP 500 : <erreur-factice>"), "<rejetee-1>")
    with pytest.raises(ErreurInference, match="500"):
        lancer(tmp_path, build, llm)
