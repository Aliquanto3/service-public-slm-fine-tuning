"""Contrat aval des paires ORPO : production (story 9.7) -> `charger_jeu` -> `preparer_preferences`.

Aucun transformers réel : tokenizer factice de `conftest.py`. Contenus factices (D1).
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from slmsp.core.artefacts import nouveau_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import ManifesteInvalide
from slmsp.core.evenements import Fin, Jeton
from slmsp.core.schemas.entrainement import LigneEntrainement, MetaLigne
from slmsp.data.config import PreferencesDonnees
from slmsp.data.preferences import lancer_preferences
from slmsp.inference.journal_local import JournalLocal
from slmsp.inference.serveur import charger_config_modele
from slmsp.train import chargement

SLUG = "granite-4.0-1b"


class LlmScripte:
    def __init__(self) -> None:
        self.n = 0

    def generer(self, messages: Any, *, tools: Any = None, options: Any = None) -> Any:
        self.n += 1
        yield Jeton(texte=f"<rejetee-factice-{self.n}>")
        yield Fin(raison="terminee")

    def compter_tokens(self, messages: Any, tools: Any = None) -> int:
        return 0


def ecrire_jeu_sft(racine: Path, nombre: int) -> tuple[str, list[str]]:
    run = nouveau_run("data-build", "build", {}, racine=racine)
    run.terminer("complet")
    lignes = [
        LigneEntrainement(
            messages=[
                {"role": "system", "content": "<prompt-factice>"},
                {"role": "user", "content": f"<question-factice-{i}>"},
                {"role": "assistant", "content": f"<reponse-factice-{i}>"},
            ],
            tache="Q",
            meta=MetaLigne(
                generateur="<modele-factice>",
                appel_ids=[f"{i:032x}"],
                session_id=f"q-{i:024x}",
                version_gabarit={"<gabarit-factice>": 1},
                version_extracteur=1,
                source=["<source-factice>"],
                licence=["<licence-factice>"],
                date=date(2026, 10, 16),
            ),
        )
        for i in range(1, nombre + 1)
    ]
    octets = b"".join(json_canonique(ligne.model_dump(mode="json")) + b"\n" for ligne in lignes)
    dossier = racine / "data" / "train" / "v1"
    dossier.mkdir(parents=True)
    (dossier / "train.jsonl").write_bytes(octets)
    manifeste = {
        "version": "v1",
        "type_run": "data-build",
        "run_id": run.run_id,
        "variante": "diffusable",
        "sha256_train": sha256_hex(octets),
    }
    (dossier / "MANIFEST.json").write_text(json.dumps(manifeste), encoding="utf-8")
    return run.run_id, [a for ligne in lignes for a in ligne.meta.appel_ids]


def test_paires_produites_lues_par_le_chargeur(projet, factices) -> None:
    build, appels = ecrire_jeu_sft(projet.racine, 3)
    resultat = lancer_preferences(
        racine=projet.racine,
        build_run_id=build,
        modele=f"base:{SLUG}",
        llm=LlmScripte(),
        config=PreferencesDonnees(),
        consigner=lambda _m: None,
    )
    # Le journal Mistral du jeu SFT : les `appel_ids` des paires sont ceux des réponses choisies.
    projet.ecrire_journal({a: ("generation", "ok") for a in appels})

    jeu = chargement.charger_jeu(
        resultat.version, racine=projet.racine, fichier=chargement.NOM_PREFERENCES
    )
    assert len(jeu.lignes) == 3
    assert jeu.manifeste["derogation_fr34"].startswith("Dérogation FR-34")
    assert chargement.recontroler_appel_ids(jeu.lignes, racine=projet.racine) == 3
    assert chargement.recontroler_rejected(jeu.lignes, racine=projet.racine) == 3

    exemples, stats = chargement.preparer_preferences(
        factices.Tokenizer(), jeu.lignes, config_modele=charger_config_modele(SLUG)
    )
    assert stats == {"lignes": 3, "retenus": 3}
    for i, exemple in enumerate(exemples, start=1):
        assert exemple["chosen"].startswith(f"<reponse-factice-{i}>")
        assert exemple["rejected"].startswith(f"<rejetee-factice-{i}>")
        assert exemple["prompt"].endswith("<|assistant|>")


@pytest.mark.parametrize("alteration", ["inconnu", "texte", "generateur"])
def test_rejected_non_journalise_refuse(projet, alteration: str) -> None:
    """Revue 9.7 : une paire dont le rejected n'est pas celui du journal local est refusée."""
    build, _ = ecrire_jeu_sft(projet.racine, 2)
    resultat = lancer_preferences(
        racine=projet.racine,
        build_run_id=build,
        modele=f"base:{SLUG}",
        llm=LlmScripte(),
        config=PreferencesDonnees(),
        consigner=lambda _m: None,
    )
    chemin = resultat.dossier / chargement.NOM_PREFERENCES
    paires = [json.loads(t) for t in chemin.read_text("utf-8").splitlines()]
    if alteration == "inconnu":
        paires[0]["meta"]["appel_local_id"] = "f" * 32
    elif alteration == "texte":
        paires[0]["rejected"][0]["content"] = "<rejetee-inventee>"
    else:
        paires[0]["meta"]["generateur_rejected"] = "slm:autre-modele"
    octets = b"".join(json_canonique(p) + b"\n" for p in paires)
    chemin.write_bytes(octets)
    manifeste_chemin = resultat.dossier / "MANIFEST.json"
    manifeste = json.loads(manifeste_chemin.read_text("utf-8"))
    manifeste["sha256_preferences"] = sha256_hex(octets)
    manifeste_chemin.write_text(json.dumps(manifeste), encoding="utf-8")

    jeu = chargement.charger_jeu(
        resultat.version, racine=projet.racine, fichier=chargement.NOM_PREFERENCES
    )
    with pytest.raises(ManifesteInvalide, match="paire 1"):
        chargement.recontroler_rejected(jeu.lignes, racine=projet.racine)


def test_rejected_sans_journal_local_refuse(projet) -> None:
    build, _ = ecrire_jeu_sft(projet.racine, 1)
    resultat = lancer_preferences(
        racine=projet.racine,
        build_run_id=build,
        modele=f"base:{SLUG}",
        llm=LlmScripte(),
        config=PreferencesDonnees(),
        consigner=lambda _m: None,
        journal=JournalLocal(projet.racine / "autre.sqlite"),
    )
    jeu = chargement.charger_jeu(
        resultat.version, racine=projet.racine, fichier=chargement.NOM_PREFERENCES
    )
    with pytest.raises(ManifesteInvalide, match="journal local absent"):
        chargement.recontroler_rejected(jeu.lignes, racine=projet.racine)
