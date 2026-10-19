"""Nettoyage déterministe du jeu SFT (story 9.9) : préambule, longueur, fidélité LC, provenance.

Tous les textes sont des jetons artificiels (`<reponse-factice-1>`, `Voici <x>`), jamais du
contenu rédigé (D1.1). Le tokenizer des tests compte les mots ; aucun modèle réel, aucun appel.
"""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from datetime import date
from pathlib import Path
from typing import Any

import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.artefacts import nouveau_run, ouvrir_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import ConfigurationInvalide, ManifesteInvalide, ProvenanceInvalide
from slmsp.core.evenements import Fin, Jeton
from slmsp.core.nettoyage import analyser_preambule, nettoyer_cible, verifier_nettoyage
from slmsp.core.schemas.entrainement import LigneEntrainement, MetaLigne
from slmsp.data.config import PreferencesDonnees
from slmsp.data.nettoyage import (
    NOM_ECARTES,
    Tokeniseur,
    elements_manquants,
    lancer_nettoyage,
    tokeniseur_du_modele,
)
from slmsp.data.preferences import lancer_preferences
from slmsp.train.chargement import charger_jeu
from slmsp.train.run import verifier_campagne

SHA = "a" * 64
MOTS = Tokeniseur(compter=lambda texte: len(texte.split()), sha256="b" * 64)


# --- Préambule ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("texte", "attendu", "statut"),
    [
        ("**Voici <x>**\n\n<corps>", "<corps>", "retire"),
        ("Voici <x> :\n\n<corps>", "<corps>", "retire"),
        ("**Voici <x> :**\r\n\r\n<corps>", "<corps>", "retire"),
        ("\n\nVoici <x> :\n<corps>", "<corps>", "retire"),
        ("## Voici <x> :\n<corps>\n\n<suite>", "<corps>\n\n<suite>", "retire"),
        ("Voici <x> :", "Voici <x> :", "seul"),
        ("Voici <x> :\n\n  \n", "Voici <x> :\n\n  \n", "seul"),
        ("Voici <x> [<y>](https://<z>) :\n\n<corps>", None, "garde"),
        ("Voici <x> http<y> :\n<corps>", None, "garde"),
        ("Voici <x>, <y>.\n<corps>", None, "garde"),
        ("<x>. Voici <y>", None, None),
        ("voici <x> :\n<corps>", None, None),
        ("\ufeffVoici <x> :\n<corps>", "<corps>", "retire"),
        ("", None, None),
    ],
)
def test_preambule(texte: str, attendu: str | None, statut: str | None) -> None:
    assert analyser_preambule(texte) == (texte if attendu is None else attendu, statut)
    assert nettoyer_cible(texte) == (texte if attendu is None else attendu)


# --- Jeu source de fixture ----------------------------------------------------------------------


def ligne(numero: int, tache: str, cible: str, *, entree: str = "<question-factice>") -> Any:
    return LigneEntrainement(
        messages=[
            {"role": "system", "content": "<prompt-factice>"},
            {"role": "user", "content": entree},
            {"role": "assistant", "content": cible},
        ],
        tache=tache,
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
    ).model_dump(mode="json")


def manifeste(version: str, run_id: str, octets: bytes, comptes: dict[str, int]) -> dict[str, Any]:
    return {
        "version": version,
        "type_run": "data-build",
        "run_id": run_id,
        "schema_version": 1,
        "variante": "diffusable",
        "cree_le": "2026-10-18",
        "statut": "complet",
        "filter_run_id": "20261017-151827-filter-e914",
        "validate_run_id": "20261017-151827-validate-e914",
        "generate_run_id": "20261017-131435-generate-08b2",
        "sha256_train": sha256_hex(octets),
        "nb_lignes": sum(comptes.values()),
        "comptes_par_tache": comptes,
        "rejets_par_motif": {},
        "registre": {},
        "sha_gabarits": {"<gabarit>": SHA},
        "sha_prompts": {},
        "sha_outils_mcp": SHA,
        "conditions_mistral": {"verifiees_le": None, "url": None, "sha256": None},
        "modeles_generateurs": ["<modele-factice>"],
        "version_extracteur": 1,
        "mode_outils": "connecte",
    }


def ecrire_source(racine: Path, lignes: Sequence[dict[str, Any]]) -> tuple[str, bytes]:
    """Run `data-build` terminé et `data/train/v1/` ; renvoie le run et les octets du jeu."""
    run = nouveau_run("data-build", "build", {}, racine=racine)
    run.terminer("complet")
    octets = b"".join(json_canonique(item) + b"\n" for item in lignes)
    dossier = racine / "data" / "train" / "v1"
    dossier.mkdir(parents=True)
    (dossier / "train.jsonl").write_bytes(octets)
    comptes: dict[str, int] = {}
    for item in lignes:
        comptes[item["tache"]] = comptes.get(item["tache"], 0) + 1
    (dossier / "MANIFEST.json").write_bytes(
        json_canonique(manifeste("v1", run.run_id, octets, comptes))
    )
    return run.run_id, octets


SOURCE_LC = "Texte :\n<source-factice> 1 500 € <x> article L. 123-4 <y> CAF 7"
JEU = [
    ligne(1, "Q", "Voici <x> :\n\n<reponse-factice-1>"),
    ligne(2, "RD", "Voici <x> [<y>](https://<z>) :\n\n<reponse-factice-2>"),
    ligne(3, "CR", "<mot> " * 6),
    ligne(4, "LC", "**Voici <x>**\n\n<reponse-factice-4> CAF", entree=SOURCE_LC),
    ligne(5, "LC", "<reponse-factice-5> 1500 € L.123-4 CAF", entree=SOURCE_LC),
    ligne(6, "Q", "Voici <x> :"),
]


def nettoyer(racine: Path, run_id: str, plafond: int = 5) -> Any:
    return lancer_nettoyage(
        racine=racine,
        build_run_id=run_id,
        modele="base:slug-factice",
        plafond_tokens=plafond,
        tokeniseur=MOTS,
        consigner=lambda _m: None,
    )


def lire_lignes(chemin: Path) -> list[dict[str, Any]]:
    return [json.loads(t) for t in chemin.read_text("utf-8").splitlines()]


def test_nominal_preambule_longueur_lc_et_manifeste(tmp_path: Path) -> None:
    run_id, octets = ecrire_source(tmp_path, JEU)
    resultat = nettoyer(tmp_path, run_id)

    assert resultat.version == "v2"
    lignes = lire_lignes(resultat.dossier / "train.jsonl")
    assert [x["tache"] for x in lignes] == ["Q", "RD", "LC", "LC", "Q"]
    cibles = [x["messages"][-1]["content"] for x in lignes]
    assert cibles[0] == "<reponse-factice-1>"
    assert cibles[1].startswith("Voici <x> [<y>]")
    assert cibles[2] == "<reponse-factice-4> CAF"
    assert cibles[4] == "Voici <x> :"
    assert [x["messages"][:-1] for x in lignes] == [
        JEU[i]["messages"][:-1] for i in (0, 1, 3, 4, 5)
    ]

    par_tache = resultat.rapport["par_tache"]
    assert par_tache["CR"] == {
        "avant": 1,
        "apres": 0,
        "preambules_retires": 0,
        "preambule_garde": 0,
        "preambule_seul": 0,
        "ecartes_longueur": 1,
        "lc_signales": 0,
    }
    assert par_tache["Q"]["preambules_retires"] == 1 and par_tache["Q"]["preambule_seul"] == 1
    assert par_tache["RD"]["preambule_garde"] == 1
    assert par_tache["LC"]["preambules_retires"] == 1 and par_tache["LC"]["lc_signales"] == 1
    assert resultat.rapport["lc_signales"] == [
        {"rang": 3, "session_id": JEU[3]["meta"]["session_id"], "manquants": ["L. 123-4", "1 500"]}
    ]
    assert lire_lignes(resultat.run.dossier / NOM_ECARTES) == [
        {"rang": 2, "session_id": JEU[2]["meta"]["session_id"], "tache": "CR", "tokens": 6}
    ]

    brut = json.loads((resultat.dossier / "MANIFEST.json").read_bytes())
    assert brut["nettoyage"] == {
        "version": 1,
        "depuis_build": run_id,
        "depuis_version": "v1",
        "sha256_train_source": sha256_hex(octets),
        "plafond_tokens": 5,
        "tokenizer_sha256": "b" * 64,
        "lc_signales": 1,
        "ecartes": [{"rang": 2, "motif": "longueur", "tokens": 6}],
    }
    assert brut["comptes_par_tache"] == {"LC": 2, "Q": 2, "RD": 1}
    assert brut["filter_run_id"] == "20261017-151827-filter-e914"
    assert ouvrir_run(resultat.run.run_id, racine=tmp_path).statut_courant() == "complet"

    jeu = charger_jeu("v2", racine=tmp_path)
    assert len(jeu.lignes) == 5
    verifier_nettoyage((resultat.dossier / "train.jsonl").read_bytes(), octets, [2])


def test_plafond_exact_garde_plafond_plus_un_ecarte(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(
        tmp_path, [ligne(1, "Q", "<m> " * 5), ligne(2, "Q", "<m> " * 6), ligne(3, "CR", "<m>")]
    )
    resultat = nettoyer(tmp_path, run_id, plafond=5)
    assert resultat.rapport["par_tache"]["Q"]["apres"] == 1
    assert resultat.rapport["par_tache"]["Q"]["ecartes_longueur"] == 1


def test_tache_hors_cr_videe_refusee_sans_version(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, [ligne(1, "Q", "<m> " * 9), ligne(2, "RD", "<m>")])
    with pytest.raises(ManifesteInvalide, match="Q"):
        nettoyer(tmp_path, run_id)
    assert not (tmp_path / "data" / "train" / "v2").exists()
    runs = [p.name for p in (tmp_path / "runs" / "data-build").iterdir() if p.name != run_id]
    assert ouvrir_run(runs[0], racine=tmp_path).statut_courant() == "partiel-erreur"


def test_jeu_deja_nettoye_refuse(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU)
    resultat = nettoyer(tmp_path, run_id)
    with pytest.raises(ManifesteInvalide, match="déjà nettoyé"):
        nettoyer(tmp_path, resultat.run.run_id)


def test_fidelite_lc_normalisee() -> None:
    source = "<x> 1 500,00 € <y> l’article 12 <z> UE 3"
    assert elements_manquants(source, "<x> 1 500 € Article 12 UE") == []
    assert elements_manquants(source, "<x>") == ["article 12", "1 500,00", "UE"]
    assert elements_manquants("<x> 1.500 € <y> Articles 12", "<x> 1 500 € <y> article 12") == []


@pytest.mark.parametrize(
    ("source", "cible", "manquant"),
    [
        ("<x> 1 500 €", "<x> 11 500 €", "1 500"),
        ("<x> article 1 <y>", "<x> article 12 <y>", "article 1"),
        ("<x> L. 12 <y>", "<x> L. 123 <y>", "L. 12"),
        ("<x> 2023. 15 <y>", "<x> 2023 <y>", "15"),
        ("<x> CB <y>", "<x> CBX <y>", "CB"),
        ("<x> 45 <y>", "<x> 145 <y>", "45"),
    ],
)
def test_fidelite_lc_sans_sous_chaine(source: str, cible: str, manquant: str) -> None:
    assert elements_manquants(source, cible) == [manquant]


# --- Provenance ---------------------------------------------------------------------------------


def _alterer(chemin: Path, ancien: bytes, nouveau: bytes) -> None:
    """Réécrit `train.jsonl` et met à jour son SHA au MANIFEST (seule la chaîne le refuse)."""
    octets = chemin.read_bytes().replace(ancien, nouveau, 1)
    assert octets != chemin.read_bytes()
    chemin.write_bytes(octets)
    manifeste_chemin = chemin.parent / "MANIFEST.json"
    brut = json.loads(manifeste_chemin.read_bytes())
    brut["sha256_train"] = sha256_hex(octets)
    manifeste_chemin.write_bytes(json_canonique(brut))


@pytest.mark.parametrize(
    ("ancien", "nouveau"),
    [
        (b"<reponse-factice-1>", b"<reponse-factice-9>"),  # cible
        (b"<prompt-factice>", b"<prompt-factice!>"),  # autre message
    ],
)
def test_ligne_alteree_refusee(tmp_path: Path, ancien: bytes, nouveau: bytes) -> None:
    run_id, octets = ecrire_source(tmp_path, JEU)
    resultat = nettoyer(tmp_path, run_id)
    chemin = resultat.dossier / "train.jsonl"
    _alterer(chemin, ancien, nouveau)
    with pytest.raises(ProvenanceInvalide):
        verifier_nettoyage(chemin.read_bytes(), octets, [2])
    with pytest.raises(ProvenanceInvalide):
        charger_jeu("v2", racine=tmp_path)


def test_ordre_change_refuse() -> None:
    source = b"".join(json_canonique(x) + b"\n" for x in JEU[:2])
    nettoyees = [json_canonique(x) for x in JEU[:2]]
    nettoyees[0] = json_canonique(
        {
            **JEU[0],
            "messages": [
                *JEU[0]["messages"][:-1],
                {"role": "assistant", "content": "<reponse-factice-1>"},
            ],
        }
    )
    verifier_nettoyage(b"\n".join(nettoyees), source, [])
    with pytest.raises(ProvenanceInvalide):
        verifier_nettoyage(b"\n".join(reversed(nettoyees)), source, [])


def test_ligne_retiree_sans_ecart_declare_refusee(tmp_path: Path) -> None:
    run_id, octets = ecrire_source(tmp_path, JEU)
    resultat = nettoyer(tmp_path, run_id)
    chemin = resultat.dossier / "train.jsonl"
    lignes = chemin.read_bytes().splitlines(keepends=True)
    _alterer(chemin, lignes[1], b"")  # RD retirée en silence
    with pytest.raises(ProvenanceInvalide, match="gardées"):
        verifier_nettoyage(chemin.read_bytes(), octets, [2])
    with pytest.raises(ProvenanceInvalide):
        charger_jeu("v2", racine=tmp_path)
    # déclarer l'écart ne suffit pas : il doit dépasser le plafond (schéma `Nettoyage`)
    manifeste_chemin = resultat.dossier / "MANIFEST.json"
    brut = json.loads(manifeste_chemin.read_bytes())
    brut["nettoyage"]["ecartes"].insert(0, {"rang": 1, "motif": "longueur", "tokens": 3})
    manifeste_chemin.write_bytes(json_canonique(brut))
    with pytest.raises(ManifesteInvalide, match="plafond_tokens"):
        charger_jeu("v2", racine=tmp_path)


@pytest.mark.parametrize("rangs", [[2, 2], [99], [-1]])
def test_rangs_ecartes_invalides_refuses(rangs: list[int]) -> None:
    source = b"".join(json_canonique(x) + b"\n" for x in JEU)
    with pytest.raises(ProvenanceInvalide, match="rangs"):
        verifier_nettoyage(b"", source, rangs)


def test_version_de_nettoyage_inconnue_refusee(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU)
    resultat = nettoyer(tmp_path, run_id)
    manifeste_chemin = resultat.dossier / "MANIFEST.json"
    brut = json.loads(manifeste_chemin.read_bytes())
    brut["nettoyage"]["version"] = 2
    manifeste_chemin.write_bytes(json_canonique(brut))
    with pytest.raises(ManifesteInvalide, match="version 2"):
        charger_jeu("v2", racine=tmp_path)


def test_source_alteree_refusee_au_chargement(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU)
    nettoyer(tmp_path, run_id)
    source = tmp_path / "data" / "train" / "v1" / "train.jsonl"
    source.write_bytes(source.read_bytes() + b"\n")
    with pytest.raises(ManifesteInvalide, match="sha256_train_source"):
        charger_jeu("v2", racine=tmp_path)


# --- Suites : préférences sur le jeu nettoyé, campagne ------------------------------------------


class LlmFactice:
    def generer(
        self, messages: Sequence[Any], *, tools: Any = None, options: Any = None
    ) -> Iterator[Any]:
        yield Jeton(texte="<rejet-factice>")
        yield Fin(raison="terminee")

    def compter_tokens(self, messages: Sequence[Any], tools: Any = None) -> int:
        return 0


def test_preferences_sur_jeu_nettoye(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU)
    nettoye = nettoyer(tmp_path, run_id)
    paires = lancer_preferences(
        racine=tmp_path,
        build_run_id=nettoye.run.run_id,
        modele="base:slug-factice",
        llm=LlmFactice(),
        config=PreferencesDonnees(graine=7, temperature=0.5, max_tokens=64),
        consigner=lambda _m: None,
    )
    assert paires.version == "v3"
    jeu = charger_jeu("v3", racine=tmp_path, fichier="preferences.jsonl")
    assert len(jeu.lignes) == 5
    assert jeu.manifeste["jeu_sft_version"] == "v2"


def test_campagne_du_jeu_source_ne_se_reprend_pas_sur_le_jeu_nettoye(tmp_path: Path) -> None:
    run_id, _ = ecrire_source(tmp_path, JEU)
    nettoye = nettoyer(tmp_path, run_id)
    nouveau_run(
        "train", "m1", {"campagne": "c", "invariants": {"jeu_build": run_id}}, racine=tmp_path
    )
    assert verifier_campagne("c", {"jeu_build": run_id}, racine=tmp_path)
    with pytest.raises(ConfigurationInvalide, match="jeu_build"):
        verifier_campagne("c", {"jeu_build": nettoye.run.run_id}, racine=tmp_path)


# --- Tokenizer et CLI ---------------------------------------------------------------------------


def test_tokeniseur_du_modele_lu_sous_models(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pytest.importorskip("tokenizers")
    from tokenizers import Tokenizer
    from tokenizers.models import WordLevel
    from tokenizers.pre_tokenizers import WhitespaceSplit

    tokenizer = Tokenizer(WordLevel({"<a>": 0, "<inconnu>": 1}, unk_token="<inconnu>"))
    tokenizer.pre_tokenizer = WhitespaceSplit()
    dossier = tmp_path / "models" / "slug-factice" / "hf"
    dossier.mkdir(parents=True)
    (dossier / "tokenizer.json").write_text(tokenizer.to_str(), encoding="utf-8")
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(tmp_path / "models"))
    lu = tokeniseur_du_modele("slug-factice", racine=tmp_path)
    assert lu.compter("<a> <b> <a>") == 3
    assert lu.sha256 == sha256_hex((dossier / "tokenizer.json").read_bytes())
    with pytest.raises(ConfigurationInvalide, match="tokenizer absent"):
        tokeniseur_du_modele("autre-factice", racine=tmp_path)


@pytest.mark.parametrize(
    "options",
    [
        [],
        ["--modele", "slug-factice"],
        ["--modele", "base:slug-factice", "--variante", "diffusable"],
        ["--modele", "base:slug-factice", "--preferences"],
    ],
)
def test_cli_nettoyage_usage(options: list[str]) -> None:
    assert main(["data", "build", "--nettoyage", "--depuis", "x", *options]) == CodeSortie.USAGE


def test_cli_nettoyage_nominal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import slmsp.data.nettoyage as module
    from slmsp.evaluation.config import charger_evaluation

    run_id, _ = ecrire_source(tmp_path, JEU)
    monkeypatch.setattr(module, "tokeniseur_du_modele", lambda slug, *, racine=None: MOTS)
    code = main(
        [
            "data",
            "build",
            "--nettoyage",
            "--depuis",
            run_id,
            "--modele",
            "base:slug-factice",
            "--racine",
            str(tmp_path),
        ]
    )
    assert code == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert "Q : 2 → 2 (1, 0, 1 ; 0 ; 0)" in sortie and "jeu v2" in sortie
    jeu = charger_jeu("v2", racine=tmp_path)
    plafond = charger_evaluation().generation.max_tokens  # lu, pas recopié
    assert jeu.manifeste["nettoyage"]["plafond_tokens"] == plafond


def test_tokenizers_absent_erreur_claire(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    dossier = tmp_path / "models" / "slug-factice" / "hf"
    dossier.mkdir(parents=True)
    (dossier / "tokenizer.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(tmp_path / "models"))
    importer = builtins.__import__

    def sans_tokenizers(nom: str, *args: Any, **kwargs: Any) -> Any:
        if nom == "tokenizers":
            raise ImportError(nom)
        return importer(nom, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", sans_tokenizers)
    with pytest.raises(ConfigurationInvalide, match="extra train"):
        tokeniseur_du_modele("slug-factice", racine=tmp_path)
