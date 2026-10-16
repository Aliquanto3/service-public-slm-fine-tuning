from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.core.items import N_DEFAUT, empreintes_texte
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


@pytest.mark.parametrize(
    "texte, attendu",
    [
        ("Ce modèle est certifié ISO 42001, non certifié par un tiers.", ["certifi", "ISO 42001"]),
        ("# Modèle certifié\n\nTexte neutre.", ["certifi"]),
        ("Modèle certifie par l'État.", ["certifie"]),
        ("Pleine conformité au RGPD.", ["conformité"]),
        ("Un modèle attesté.", ["attesté"]),
        ("Une attestation officielle.", ["attestation"]),
        ("Modèle homologué.", ["homologué"]),
        ("Il est labellisé.", ["labellis"]),
        ("This model is certified.", ["certified"]),
    ],
)
def test_formulation_interdite_citee_precisement(texte: str, attendu: list[str]) -> None:
    constats = controles.controle_formulations(texte, CONFIG)
    assert constats, texte
    for morceau in attendu:
        assert any(morceau in c for c in constats), (texte, morceau, constats)


def test_mention_admise_ne_masque_que_sa_propre_occurrence() -> None:
    texte = "Ce modèle est certifié ISO 42001, non certifié par un tiers."
    constats = controles.controle_formulations(texte, CONFIG)
    assert len(constats) == 2  # « certifié » puis « ISO 42001 », pas la mention admise


def test_titre_de_non_certification_admis() -> None:
    assert controles.controle_formulations("## Non-certification\n", CONFIG) == []


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
    protegees = frozenset(empreintes_texte(phrase, N_DEFAUT))
    (tmp_path / "README.md").write_text(f"Intro.\n{phrase}\n", encoding="utf-8")
    assert controles.controle_fuite(tmp_path, protegees)
    (constat,) = controles.controle_fuite(tmp_path, protegees)
    assert constat == "README.md : texte du Jeu d'évaluation détecté"


def test_fuite_liste_vide_refusee(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("rien\n", encoding="utf-8")
    (constat,) = controles.controle_fuite(tmp_path, frozenset())
    assert "aucune empreinte" in constat


def test_fuite_seuil_sur_le_fichier_entier(tmp_path: Path) -> None:
    # Une empreinte commune par ligne : aucune ligne n'atteint le seuil, le fichier oui.
    n = controles.MIN_EMPREINTES_COMMUNES
    lignes = [f"<a{i}> <b{i}> <c{i}> <d{i}> <e{i}>" for i in range(n)]
    protegees = frozenset(e for ligne in lignes for e in empreintes_texte(ligne, N_DEFAUT))
    (tmp_path / "notes.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    assert controles.controle_fuite(tmp_path, protegees)


def test_suffixes_hors_liste_controles_et_binaires_ignores(tmp_path: Path) -> None:
    phrase = "<mot1> <mot2> <mot3> <mot4> <mot5> <mot6> <mot7> <mot8>"
    protegees = frozenset(empreintes_texte(phrase, N_DEFAUT))
    (tmp_path / "donnees.jsonl").write_text(phrase + "\n", encoding="utf-8")
    (tmp_path / "table.csv").write_text(phrase + "\n", encoding="utf-8")
    (tmp_path / "sans-suffixe").write_text("MISTRAL_API_KEY=<valeur-factice>\n", encoding="utf-8")
    (tmp_path / "m.gguf").write_bytes(b"GGUF\x00" + phrase.encode())
    (tmp_path / "autre.bin").write_bytes(b"\x00\x01" + phrase.encode())
    fuites = controles.controle_fuite(tmp_path, protegees)
    assert sorted(c.split(" :")[0] for c in fuites) == ["donnees.jsonl", "table.csv"]
    (secret,) = controles.controle_secrets(tmp_path, CONFIG)
    assert "sans-suffixe" in secret


def test_sommes_incoherentes(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("x", encoding="utf-8")
    (tmp_path / "SHA256SUMS").write_text("0" * 64 + "  a.txt\n", encoding="utf-8")
    assert controles.controle_sommes(tmp_path)
