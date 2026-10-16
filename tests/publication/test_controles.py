from __future__ import annotations

from pathlib import Path

from slmsp.core.items import N_DEFAUT, _empreintes_texte
from slmsp.publication import controles
from slmsp.publication.config import charger_config

DEPOT = Path(__file__).resolve().parents[2]
CONFIG = charger_config(DEPOT)


def test_certification_refusee() -> None:
    for texte in (
        "Modèle certifié par un organisme.",
        "Conforme à ISO 42001.",
        "Démarche ISO/IEC 42001 en cours.",
    ):
        assert controles.controle_formulations(texte, CONFIG), texte


def test_non_certification_explicite_admise() -> None:
    texte = CONFIG.mention_non_certification + "\nCe modèle n'est pas certifié ISO 42001."
    assert controles.controle_formulations(texte, CONFIG) == []


def test_mention_ne_protege_pas_une_autre_phrase() -> None:
    texte = "Aucune certification n'est revendiquée. Le modèle est certifié ISO 42001."
    assert controles.controle_formulations(texte, CONFIG)


def test_fichiers_eval_et_train_refuses(tmp_path: Path) -> None:
    for relatif in ("eval/jeu/items.jsonl", "data/train/x.jsonl", ".env", "ok/.env.local"):
        cible = tmp_path / relatif
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_text("<factice>", encoding="utf-8")
    constats = controles.controle_fichiers(tmp_path)
    assert len(constats) == 4


def test_source_sous_eval_refusee(tmp_path: Path) -> None:
    assert controles.controle_chemin_source(tmp_path / "eval" / "jeu" / "a.md", tmp_path)
    assert controles.controle_chemin_source(tmp_path / "data" / "train" / "a", tmp_path)
    assert controles.controle_chemin_source(tmp_path / "runs" / "a", tmp_path) == []


def test_secret_detecte(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("MISTRAL_API_KEY=<valeur-factice>\n", encoding="utf-8")
    assert controles.controle_secrets(tmp_path, CONFIG)


def test_fuite_detectee_par_ngrammes(tmp_path: Path) -> None:
    phrase = "<mot1> <mot2> <mot3> <mot4> <mot5> <mot6> <mot7> <mot8>"
    protegees = frozenset(_empreintes_texte(phrase, N_DEFAUT))
    (tmp_path / "README.md").write_text(f"Intro.\n{phrase}\n", encoding="utf-8")
    assert controles.controle_fuite(tmp_path, protegees)
    assert controles.controle_fuite(tmp_path, frozenset()) == []


def test_sommes_incoherentes(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    (tmp_path / "SHA256SUMS").write_text("0" * 64 + "  a.txt\n", encoding="utf-8")
    assert controles.controle_sommes(tmp_path)
