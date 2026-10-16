"""Les six verrous AD-3 (« Claude ne génère aucune Donnée d'entraînement »), story 9.6.

Verrous qui ne dépendent pas de l'extra `data` : ils tournent toujours. Les verrous qui
passent par le pipeline (générateur Mistral, re-dérivation) sont dans
`test_verrous_ad3_pipeline.py` et exigent `uv sync --extra data`. Contenus : jetons
artificiels (D1.1) ; aucun appel d'API.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.core.artefacts import lire
from slmsp.core.erreurs import LectureInterdite, ProvenanceInvalide
from slmsp.core.gabarits import GabaritInvalide, valider_gabarit
from slmsp.core.var import dossier_var
from slmsp.data.licences import RegistreLicences

from ..test_architecture import ARBRE_PROPRE, _ecrire_arbre, analyser

# --- Verrou 1 : imports --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("paquet", "contenu"),
    [
        ("data", "import anthropic\n"),
        ("data", "from anthropic import Anthropic\n"),
        ("train", "import anthropic\n"),
        ("data", "from slmsp.judge import notation\n"),
        ("train", "import slmsp.judge.cache\n"),
    ],
)
def test_verrou_1_import_de_anthropic_ou_du_juge_detecte(
    tmp_path: Path, paquet: str, contenu: str
) -> None:
    arbre = _ecrire_arbre(tmp_path, {**ARBRE_PROPRE, f"{paquet}/synthetique.py": contenu})
    regles = {v.regle for v in analyser(arbre)}
    assert regles & {"anthropic", "judge-depuis-data/train"}


def test_verrou_1_arbre_propre_sans_violation(tmp_path: Path) -> None:
    assert analyser(_ecrire_arbre(tmp_path, ARBRE_PROPRE)) == []


# --- Verrou 2 : lectures -------------------------------------------------------------------------


@pytest.mark.parametrize(
    "relatif",
    [
        "eval/jeu/v1.1/items.jsonl",
        "runs/eval-generation/20261012-101500-granite-0a1f/generations.jsonl",
        "data/ecrit-a-la-main.jsonl",
        "data/train/v1/train.jsonl",
        "config/taches.toml",
    ],
)
def test_verrou_2_lecture_refusee(tmp_path: Path, relatif: str) -> None:
    chemin = tmp_path / relatif
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_bytes(b"<contenu-factice>")
    with pytest.raises(LectureInterdite):
        lire(relatif, "data", racine=tmp_path)


def test_verrou_2_cache_des_verdicts_refuse(tmp_path: Path) -> None:
    with pytest.raises(LectureInterdite):
        lire(dossier_var() / "verdicts.sqlite", "data", racine=tmp_path)


def test_verrou_2_lecture_autorisee(tmp_path: Path) -> None:
    (tmp_path / "data" / "raw").mkdir(parents=True)
    (tmp_path / "data" / "raw" / "x.bin").write_bytes(b"<contenu-factice>")
    assert lire("data/raw/x.bin", "data", racine=tmp_path) == b"<contenu-factice>"


# --- Verrou 5 : amorces et registre -----------------------------------------------------


@pytest.mark.parametrize("auteur", ["claude", "inconnu"])
def test_verrou_5_registre_refuse_l_auteur(tmp_path: Path, auteur: str) -> None:
    registre = tmp_path / "data" / "registre-licences.toml"
    registre.parent.mkdir(parents=True)
    registre.write_text(
        f"""schema_version = 1

[[sources]]
id = "org/jeu-factice"
licence = "<licence-factice>"
usage = "diffusable"
auteur_contenu = "{auteur}"
genere_par = "humain"
""",
        encoding="utf-8",
    )
    with pytest.raises(ProvenanceInvalide):
        RegistreLicences.charger(registre, racine=tmp_path)


# --- Verrou 6 : gabarits et verdicts ----------------------------------------------------


def _gabarit(consigne: str) -> str:
    return (
        "---\nid: g1\nversion: 1\ntache: Q\n---\n\n## Consigne\n\n"
        f"{consigne}\n\n## Emplacements\n\n- alpha : <description-factice>\n"
    )


@pytest.mark.parametrize(
    "consigne",
    [
        "<c> {alpha}\n\n```\n<sortie-factice>\n```",
        '<c> {alpha}\n\n{"cle": "<valeur-factice>"}',
        "<c> {alpha}\n\nExemple de réponse : <x>",
        "<c> {alpha}\n\nla réponse attendue : <x>",
    ],
)
def test_verrou_6_gabarit_avec_exemple_de_sortie_refuse(consigne: str) -> None:
    with pytest.raises(GabaritInvalide):
        valider_gabarit(_gabarit(consigne))


def test_verrou_6_gabarit_sans_exemple_accepte() -> None:
    assert valider_gabarit(_gabarit("<consigne-factice> {alpha}")).id == "g1"
