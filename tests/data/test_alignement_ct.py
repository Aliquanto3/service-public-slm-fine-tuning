"""Prompts CT alignés sur leur cible (`data build --aligner-ct`, story 16.3).

Tous les textes, la formulation comprise, sont des jetons artificiels (D1) ; aucun appel.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.alignement_ct import aligner_jeu, extraire_libelles, verifier_alignement
from slmsp.core.canonique import sha256_hex
from slmsp.core.erreurs import ManifesteInvalide, ProvenanceInvalide
from slmsp.data import alignement_ct
from slmsp.data.alignement_ct import lancer_alignement_ct
from slmsp.data.config import charger_config_donnees
from slmsp.train.chargement import charger_jeu

from .test_nettoyage import ecrire_source, ligne, nettoyer

FORMULATION = "<formulation-factice> {libelles} <fin-formulation>"
ORIGINE = "<origine-factice>"
ENTREE_CT = "Consigne :\n<consigne-factice>\n\nType de courrier :\n<type-factice>"
CIBLE_CT = "**[<lib-a>]**\n<corps-factice> [<lib-b>] [<lib-a>]\n[<lib-c>]"


def jeu() -> list[dict[str, Any]]:
    return [
        ligne(1, "Q", "<reponse-factice-1> [<pas-ct>]"),
        ligne(2, "CT", CIBLE_CT, entree=ENTREE_CT),
        ligne(3, "CT", "<reponse-factice-3>", entree=ENTREE_CT),  # sans libellé
        ligne(4, "LC", "<reponse-factice-4>"),
    ]


def aligner(racine: Path, run_id: str, formulation: str = FORMULATION) -> Any:
    return lancer_alignement_ct(
        racine=racine,
        build_run_id=run_id,
        formulation=formulation,
        origine_formulation=ORIGINE,
        origines_admises=[ORIGINE],
        consigner=lambda _m: None,
    )


def lignes_brutes(chemin: Path) -> list[bytes]:
    return [t for t in chemin.read_bytes().split(b"\n") if t]


def test_extraction_des_libelles_ordre_et_doublons() -> None:
    assert extraire_libelles(CIBLE_CT) == ["[<lib-a>]", "[<lib-b>]", "[<lib-c>]"]
    assert extraire_libelles("<sans-libelle> [\n] [[<x>]]") == ["[<x>]"]


def test_prompt_attendu_et_lignes_non_ct_inchangees(tmp_path: Path) -> None:
    run_id, octets = ecrire_source(tmp_path, jeu())
    resultat = aligner(tmp_path, run_id)

    assert resultat.version == "v2"
    source = lignes_brutes(tmp_path / "data" / "train" / "v1" / "train.jsonl")
    sortie = lignes_brutes(resultat.dossier / "train.jsonl")
    assert [sortie[i] for i in (0, 2, 3)] == [source[i] for i in (0, 2, 3)]
    alignee = json.loads(sortie[1])
    assert alignee["messages"][1]["content"] == (
        "Consigne :\n<consigne-factice> <formulation-factice> [<lib-a>], [<lib-b>], [<lib-c>] "
        "<fin-formulation>\n\nType de courrier :\n<type-factice>"
    )
    origine = json.loads(source[1])
    assert alignee["messages"][2] == origine["messages"][2]  # cible inchangée
    assert alignee["messages"][0] == origine["messages"][0]
    assert alignee["meta"] == origine["meta"]
    assert resultat.rapport["lignes_modifiees"] == 1 and resultat.rapport["lignes_ct"] == 2


def test_manifeste_et_chargement(tmp_path: Path) -> None:
    run_id, octets = ecrire_source(tmp_path, jeu())
    resultat = aligner(tmp_path, run_id)
    brut = json.loads((resultat.dossier / "MANIFEST.json").read_bytes())
    assert brut["alignement_ct"] == {
        "depuis_build": run_id,
        "depuis_version": "v1",
        "sha256_train_source": sha256_hex(octets),
        "formulation": FORMULATION,
        "origine_formulation": ORIGINE,
        "lignes_modifiees": 1,
        "comptes_source": {"CT": 2, "LC": 1, "Q": 1},
    }
    assert brut["nb_lignes"] == 4 and brut["comptes_par_tache"] == {"CT": 2, "LC": 1, "Q": 1}
    assert brut["sha256_train"] == sha256_hex((resultat.dossier / "train.jsonl").read_bytes())
    assert len(charger_jeu("v2", racine=tmp_path).lignes) == 4


def test_deterministe(tmp_path: Path) -> None:
    run_id, octets = ecrire_source(tmp_path, jeu())
    premier = aligner(tmp_path, run_id)
    second = aligner(tmp_path, run_id)
    assert (premier.dossier / "train.jsonl").read_bytes() == (
        second.dossier / "train.jsonl"
    ).read_bytes()


def test_chaine_depuis_un_jeu_nettoye(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, jeu())
    nettoye = nettoyer(tmp_path, run_id, plafond=50)
    resultat = aligner(tmp_path, nettoye.run.run_id)
    brut = json.loads((resultat.dossier / "MANIFEST.json").read_bytes())
    assert "nettoyage" not in brut and "nettoyage_source" in brut["alignement_ct"]
    assert len(charger_jeu(resultat.version, racine=tmp_path).lignes) == 4


def test_ligne_modifiee_refusee_au_chargement(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, jeu())
    resultat = aligner(tmp_path, run_id)
    train = resultat.dossier / "train.jsonl"
    train.write_bytes(train.read_bytes().replace(b'<lib-c>]"', b'<lib-x>]"', 1))
    manifeste = resultat.dossier / "MANIFEST.json"
    brut = json.loads(manifeste.read_bytes())
    brut["sha256_train"] = sha256_hex(train.read_bytes())
    manifeste.write_text(json.dumps(brut), "utf-8")
    with pytest.raises(ProvenanceInvalide):
        charger_jeu("v2", racine=tmp_path)


def test_verification_refuse_une_autre_formulation() -> None:
    source = b"".join(json.dumps(x).encode() + b"\n" for x in jeu())
    aligne, modifiees = aligner_jeu(source, FORMULATION)
    verifier_alignement(aligne, source, FORMULATION, modifiees)
    with pytest.raises(ProvenanceInvalide):
        verifier_alignement(aligne, source, "<autre> {libelles}", modifiees)


@pytest.mark.parametrize(
    "formulation", ["", "<sans-emplacement>", "{libelles} {x}", "{libelles}\n<deux-lignes>"]
)
def test_formulation_invalide_refusee_sans_version(tmp_path: Path, formulation: str) -> None:
    run_id, _ = ecrire_source(tmp_path, jeu())
    with pytest.raises(ManifesteInvalide):
        aligner(tmp_path, run_id, formulation)
    assert not (tmp_path / "data" / "train" / "v2").exists()


def test_refus_origine_vide_deja_aligne_et_sans_ct(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, jeu())
    with pytest.raises(ManifesteInvalide, match="origine"):
        lancer_alignement_ct(
            racine=tmp_path, build_run_id=run_id, formulation=FORMULATION, origine_formulation=" "
        )
    resultat = aligner(tmp_path, run_id)
    with pytest.raises(ManifesteInvalide, match="déjà aligné"):
        aligner(tmp_path, resultat.run.run_id)
    autre = tmp_path / "autre"
    run_sans, _ = ecrire_source(autre, [ligne(1, "Q", "<r>"), ligne(2, "CT", "<sans-libelle>")])
    with pytest.raises(ManifesteInvalide, match="aucune ligne CT"):
        aligner(autre, run_sans)


def test_ligne_ct_sans_consigne_refusee(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, [ligne(1, "CT", CIBLE_CT, entree="<sans-consigne>")])
    with pytest.raises(ManifesteInvalide, match="Consigne"):
        aligner(tmp_path, run_id)


@pytest.mark.parametrize(
    "options",
    [
        [],
        ["--formulation-fichier", "f.txt"],
        ["--origine-formulation", "<o>"],
        ["--formulation-fichier", "f.txt", "--origine-formulation", "<o>", "--nettoyage"],
        ["--formulation-fichier", "f.txt", "--origine-formulation", "<o>", "--taches", "CT"],
    ],
)
def test_cli_usage(options: list[str]) -> None:
    assert main(["data", "build", "--aligner-ct", "--depuis", "x", *options]) == CodeSortie.USAGE


def test_cli_options_sans_aligner_ct() -> None:
    code = main(["data", "build", "--depuis", "x", "--origine-formulation", "<o>"])
    assert code == CodeSortie.USAGE


def test_origine_hors_liste_fermee_refusee_sans_version(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, jeu())
    for admises in ([], ["<autre-origine-factice>"], None):  # None : config du projet, vide
        with pytest.raises(ManifesteInvalide, match="origines_admises"):
            lancer_alignement_ct(
                racine=tmp_path,
                build_run_id=run_id,
                formulation=FORMULATION,
                origine_formulation=ORIGINE,
                origines_admises=admises,
                consigner=lambda _m: None,
            )
    assert not (tmp_path / "data" / "train" / "v2").exists()


def test_config_du_projet_sans_origine_admise() -> None:
    assert charger_config_donnees().alignement_ct.origines_admises == []


def _cli(tmp_path: Path, run_id: str) -> int:
    fichier = tmp_path / "formulation.txt"
    fichier.write_text(FORMULATION + "\n", encoding="utf-8")
    return main(
        [
            "data",
            "build",
            "--aligner-ct",
            "--depuis",
            run_id,
            "--formulation-fichier",
            str(fichier),
            "--origine-formulation",
            ORIGINE,
            "--racine",
            str(tmp_path),
        ]
    )


def test_cli_refuse_tant_que_la_liste_fermee_est_vide(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, jeu())
    assert _cli(tmp_path, run_id) == CodeSortie.USAGE
    assert not (tmp_path / "data" / "train" / "v2").exists()


def test_cli_nominal(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    reelle = charger_config_donnees()
    bloc = reelle.alignement_ct.model_copy(update={"origines_admises": [ORIGINE]})
    admise = reelle.model_copy(update={"alignement_ct": bloc})
    monkeypatch.setattr(alignement_ct, "charger_config_donnees", lambda: admise)
    run_id, _ = ecrire_source(tmp_path, jeu())
    code = _cli(tmp_path, run_id)
    assert code == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert "lignes CT alignées : 1/2" in sortie and "jeu v2 (4 lignes)" in sortie
