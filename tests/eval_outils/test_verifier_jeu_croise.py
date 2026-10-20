"""Outil `eval/outils/verifier_jeu_croise.py` (story O4a) : disjonction et vérification croisée.

Fixtures factices (mots `mot0`, `<texte-factice>`…), aucun réseau : l'appelant des juges est un
faux injecté. Aucun fichier de `eval/jeu/` n'est lu ni écrit : tout vit dans `tmp_path`.
"""

from __future__ import annotations

import importlib.util
import json
import socket
import sys
from pathlib import Path
from typing import Any

import pytest

RACINE = Path(__file__).resolve().parents[2]
OUTIL = RACINE / "eval" / "outils" / "verifier_jeu_croise.py"


def _charger() -> Any:
    spec = importlib.util.spec_from_file_location("verifier_jeu_croise_test", OUTIL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


vjc = _charger()


@pytest.fixture(autouse=True)
def _sans_reseau(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuser(*_a: Any, **_k: Any) -> Any:
        raise AssertionError("aucun accès réseau attendu")

    monkeypatch.setattr(socket, "socket", refuser)


def mots(prefixe: str, n: int) -> str:
    return " ".join(f"{prefixe}{i}" for i in range(n))


def item(identifiant: str, texte: str, url: str = "https://exemple.invalide/a") -> dict[str, Any]:
    return {
        "id": identifiant,
        "tache": identifiant.split("-")[0],
        "entree": {"consigne": "<consigne-factice>", "texte": texte},
        "provenance": [{"source": "<source-factice>", "url": url}],
    }


def ecrire(chemin: Path, lignes: list[dict[str, Any]]) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text("".join(json.dumps(x) + "\n" for x in lignes), encoding="utf-8")


def exemple(texte: str) -> dict[str, Any]:
    return {
        "messages": [
            {"role": "user", "content": texte},
            {"role": "assistant", "content": "<reponse-factice>"},
        ],
        "meta": {"source": "<source-factice>"},
    }


@pytest.fixture
def depot(tmp_path: Path) -> Path:
    ecrire(
        tmp_path / "eval/jeu/v1.0/items.jsonl",
        [item("Q-001", mots("a", 30), "https://exemple.invalide/v10")],
    )
    ecrire(
        tmp_path / "eval/jeu/v1.1/items.jsonl",
        [item("Q-002", mots("b", 30), "https://exemple.invalide/v11/")],
    )
    ecrire(tmp_path / "data/train/v3/train.jsonl", [exemple(mots("c", 30))])
    return tmp_path


def conflits(depot: Path, items: list[dict[str, Any]]) -> list[str]:
    return vjc.controler_disjonction(items, depot, n=5, seuil=0.5)


def test_jeu_disjoint(depot: Path) -> None:
    assert conflits(depot, [item("RD-501", mots("z", 30), "https://exemple.invalide/neuf")]) == []


def test_item_duplique_de_v11_refuse(depot: Path) -> None:
    sortie = conflits(depot, [item("Q-501", mots("b", 30), "https://exemple.invalide/autre")])
    assert any("v1.1/Q-002" in c and "texte identique" in c for c in sortie)
    assert any("recouvrement" in c for c in sortie)


def test_meme_url_refusee_a_la_barre_finale_et_a_la_casse_pres(depot: Path) -> None:
    sortie = conflits(depot, [item("Q-501", mots("z", 30), "HTTPS://Exemple.invalide/v11")])
    assert sortie == ["Q-501 : URL source déjà utilisée par v1.1/Q-002"]


def test_recouvrement_d_un_jeu_d_entrainement_refuse(depot: Path) -> None:
    sortie = conflits(depot, [item("Q-501", mots("c", 12) + " " + mots("zz", 5))])
    assert any("data/train/v3#1" in c and "recouvrement" in c for c in sortie)


def test_recouvrement_sous_le_seuil_accepte(depot: Path) -> None:
    texte = mots("c", 6) + " " + mots("y", 30)  # 2 n-grammes communs sur 32
    assert conflits(depot, [item("Q-501", texte, "https://exemple.invalide/neuf")]) == []


def test_identifiant_deja_pris_ou_en_double(depot: Path) -> None:
    sortie = conflits(
        depot,
        [
            item("Q-001", mots("m", 20), "https://exemple.invalide/1"),
            item("RD-501", mots("n", 20), "https://exemple.invalide/2"),
            item("RD-501", mots("o", 20), "https://exemple.invalide/3"),
        ],
    )
    assert "Q-001 : identifiant déjà pris par v1.0/Q-001" in sortie
    assert "RD-501 : identifiant en double dans le jeu" in sortie


def test_seuils_lus_dans_la_config(depot: Path) -> None:
    assert vjc.seuils(depot) == (5, 0.5)  # sans config : défauts
    config = depot / "config" / "donnees.toml"
    config.parent.mkdir()
    config.write_text("[anti_fuite]\nn_ngrammes = 3\nseuil_jaccard = 0.25\n", encoding="utf-8")
    assert vjc.seuils(depot) == (3, 0.25)


def test_commande_disjonction_code_de_sortie(
    depot: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    neuf = item("Q-501", mots("z", 30), "https://exemple.invalide/n")
    ecrire(depot / "eval/jeu/dev1/items.jsonl", [neuf])
    assert vjc.main(["disjonction", "--version", "dev1", "--racine", str(depot)]) == 0
    assert "disjoint" in capsys.readouterr().out
    ecrire(depot / "eval/jeu/dev1/items.jsonl", [item("Q-501", mots("a", 30))])
    assert vjc.main(["disjonction", "--version", "dev1", "--racine", str(depot)]) == 1
    assert "CONFLIT Q-501" in capsys.readouterr().out


def test_version_non_dev_refusee(depot: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert vjc.main(["disjonction", "--version", "v1.1", "--racine", str(depot)]) == 2
    assert "devN" in capsys.readouterr().err


# --- Vérification croisée --------------------------------------------------------------------


def verdict(coherent: bool = True, ambigu: bool = False, absent: bool = False) -> str:
    return json.dumps(
        {
            "coherent": coherent,
            "ambigu": ambigu,
            "fait_absent_de_la_source": absent,
            "remarque": "<remarque-factice>",
        }
    )


def identifiant_du(prompt: str) -> str:
    return json.loads(prompt.split("ITEM :\n", 1)[1])["id"]


def appelant(reponses: dict[tuple[str, str], str | Exception]) -> Any:
    def appeler(juge: str, prompt: str) -> str:
        reponse = reponses.get((juge, identifiant_du(prompt)), verdict())
        if isinstance(reponse, Exception):
            raise reponse
        return reponse

    return appeler


ITEMS = [item(f"Q-50{i}", mots("q", 8) + str(i)) for i in range(1, 5)]


def test_decision_un_seul_grief_suffit() -> None:
    lignes = vjc.verifier_items(
        ITEMS,
        ["deepseek", "glm"],
        appelant(
            {
                ("deepseek", "Q-502"): verdict(ambigu=True),
                ("glm", "Q-503"): verdict(coherent=False),
                ("glm", "Q-504"): verdict(absent=True),
            }
        ),
    )
    decisions = {x["item_id"]: x["decision"] for x in lignes}
    assert decisions == {"Q-501": "retenu", "Q-502": "rejete", "Q-503": "rejete", "Q-504": "rejete"}
    assert lignes[1]["motifs"] == ["deepseek : ambigu"]
    assert lignes[2]["motifs"] == ["glm : incohérent"]


def test_sortie_illisible_ou_erreur_d_appel_laisse_l_item_incomplet(
    capsys: pytest.CaptureFixture[str],
) -> None:
    lignes = vjc.verifier_items(
        ITEMS[:2],
        ["deepseek", "glm"],
        appelant(
            {
                ("glm", "Q-501"): "pas du json",
                ("deepseek", "Q-502"): TimeoutError("<delai-factice>"),
            }
        ),
    )
    assert [x["decision"] for x in lignes] == ["incomplet", "incomplet"]
    assert "Q-502 : deepseek : TimeoutError" in capsys.readouterr().err


@pytest.mark.parametrize(
    "texte",
    [
        '{"coherent": true}',
        '{"coherent": "oui", "ambigu": false, "fait_absent_de_la_source": false}',
        "",
        "{",
    ],
)
def test_lire_verdict_refuse_les_sorties_incompletes(texte: str) -> None:
    assert vjc.lire_verdict(texte) is None


def test_lire_verdict_tolere_du_texte_autour() -> None:
    lu = vjc.lire_verdict("Voici : " + verdict() + " fin")
    assert lu == {
        "coherent": True,
        "ambigu": False,
        "fait_absent_de_la_source": False,
        "remarque": "<remarque-factice>",
    }


def test_rapport_taux_de_rejet() -> None:
    lignes = vjc.verifier_items(
        ITEMS, ["deepseek", "glm"], appelant({("glm", "Q-502"): verdict(ambigu=True)})
    )
    rapport = vjc.rapport_rejets(lignes)
    assert rapport["global"] == {
        "total": 4,
        "retenus": 3,
        "rejetes": 1,
        "incomplets": 0,
        "taux_rejet": 0.25,
    }
    assert rapport["par_tache"]["Q"]["taux_rejet"] == 0.25


def test_commande_verifier_ajout_seul_et_reprise(depot: Path) -> None:
    ecrire(depot / "eval/construction/dev1/Q.jsonl", ITEMS)
    appels: list[tuple[str, str]] = []
    reponses: dict[tuple[str, str], str | Exception] = {
        ("glm", "Q-503"): TimeoutError("<delai-factice>")
    }
    base = appelant(reponses)

    def appeler(juge: str, prompt: str) -> str:
        appels.append((juge, identifiant_du(prompt)))
        return base(juge, prompt)

    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 1  # Q-503 incomplet
    verdicts = depot / "eval/construction/dev1/verdicts-croises.jsonl"
    assert len(verdicts.read_text(encoding="utf-8").splitlines()) == 4
    assert len(appels) == 8

    reponses.clear()  # le juge répond cette fois : seul Q-503 est rejoué
    appels.clear()
    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 0
    assert {i for _, i in appels} == {"Q-503"}
    courants = vjc.verdicts_courants(verdicts)
    assert {v["decision"] for v in courants.values()} == {"retenu"}
    assert len(verdicts.read_text(encoding="utf-8").splitlines()) == 5  # ajout seul
    rapport = json.loads(
        (depot / "eval/construction/dev1/rapport-verification-croisee.json").read_text(
            encoding="utf-8"
        )
    )
    assert rapport["global"]["retenus"] == 4 and rapport["juges"] == ["deepseek", "glm"]


def test_deux_juges_au_moins(depot: Path, capsys: pytest.CaptureFixture[str]) -> None:
    ecrire(depot / "eval/construction/dev1/Q.jsonl", ITEMS)
    argv = ["verifier", "--version", "dev1", "--racine", str(depot), "--juges", "glm"]
    assert vjc.main(argv) == 2
    assert "deux juges" in capsys.readouterr().err


def test_prompt_sans_exemple_de_reponse_cible() -> None:
    prompt = vjc.prompt_verification(ITEMS[0])
    assert prompt.count('"coherent"') == 1  # la clé demandée, aucun exemple de verdict
    assert ITEMS[0]["id"] in prompt


# --- Revue O4a ---------------------------------------------------------------------------------


def test_sources_attendues_des_q_comptent_comme_url(depot: Path) -> None:
    ancien = item("Q-003", mots("p", 30), "https://exemple.invalide/prov")
    ancien["sources_attendues"] = ["https://exemple.invalide/attendue/"]
    ecrire(depot / "eval/jeu/v1.1/items.jsonl", [ancien])
    neuf = item("Q-501", mots("z", 30), "https://exemple.invalide/neuf")
    neuf["sources_attendues"] = ["https://Exemple.invalide/attendue"]
    sortie = conflits(depot, [neuf])
    assert sortie == ["Q-501 : URL source déjà utilisée par v1.1/Q-003"]


def test_amorce_d_un_run_seed_recouverte_refusee(depot: Path) -> None:
    ecrire(
        depot / "runs/data-seed/20261017-000000-seed-abcd/amorces.jsonl",
        [{"amorce_id": "q.factice.0", "texte": "<amorce> factice a b"}],
    )
    sortie = conflits(depot, [item("Q-501", "<amorce> factice a b", "https://exemple.invalide/n")])
    assert any("runs/data-seed/20261017-000000-seed-abcd/q.factice.0" in c for c in sortie)
    assert any("texte identique" in c for c in sortie)


def test_texte_court_identique_detecte(depot: Path) -> None:
    ecrire(
        depot / "eval/jeu/v1.1/items.jsonl",
        [item("Q-002", "mot1 mot2 mot3", "https://exemple.invalide/v11")],
    )
    sortie = conflits(depot, [item("Q-501", "mot1 mot2 mot3", "https://exemple.invalide/n")])
    assert any("texte identique à v1.1/Q-002" in c for c in sortie)


def test_item_modifie_reverifie(depot: Path) -> None:
    items = [dict(x) for x in ITEMS[:2]]
    ecrire(depot / "eval/construction/dev1/Q.jsonl", items)
    appels: list[str] = []

    def appeler(juge: str, prompt: str) -> str:
        appels.append(identifiant_du(prompt))
        return verdict()

    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 0
    appels.clear()
    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 0
    assert appels == []  # inchangés : rien à rejouer
    items[1] = {**items[1], "entree": {"consigne": "<c>", "texte": mots("modifie", 9)}}
    ecrire(depot / "eval/construction/dev1/Q.jsonl", items)
    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 0
    assert set(appels) == {items[1]["id"]}


def test_type_de_courrier_commun_ignore(depot: Path) -> None:
    """Le type CT (vocabulaire fermé) n'est ni un texte identique ni un recouvrement (O4b)."""
    ct = lambda i, t: {  # noqa: E731
        "id": i,
        "tache": "CT",
        "entree": {"type": "accusé de réception", "consigne": "<c>", "objet": t},
        "provenance": [{"source": "<s>"}],
    }
    ecrire(depot / "eval/jeu/v1.1/items.jsonl", [ct("CT-001", mots("d", 12))])
    assert vjc.controler_disjonction([ct("CT-501", mots("e", 12))], depot) == []


def test_document_source_sans_url_refuse(depot: Path) -> None:
    """Fiche, article LEGI ou ligne de corpus déjà cités : refus même sans `url` (revue O4b)."""
    ancien = {
        "id": "Q-001",
        "tache": "Q",
        "entree": {"question": mots("f", 12)},
        "provenance": [
            {"url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F123"},
            {"url": "https://huggingface.co/datasets/x/resolve/abc/corpus%26A.xlsx", "ligne": 7},
            {"legiarti": "LEGIARTI000001"},
        ],
    }
    ecrire(depot / "eval/jeu/v1.1/items.jsonl", [ancien])

    def nouveau(i: str, source: dict) -> dict:
        return {"id": i, "tache": "Q", "entree": {"question": mots(i, 12)}, "provenance": [source]}

    conflits = vjc.controler_disjonction(
        [
            nouveau("Q-501", {"doc_id": "F123"}),
            nouveau("Q-502", {"fichier": "corpus&A.xlsx", "ligne": 7}),
            nouveau("Q-503", {"legiarti": "LEGIARTI000001"}),
            nouveau("Q-504", {"fichier": "corpus&A.xlsx", "ligne": 8}),
        ],
        depot,
    )
    assert sorted(c.split(" ")[0] for c in conflits if "document source" in c) == [
        "Q-501",
        "Q-502",
        "Q-503",
    ]


def test_preferences_dans_la_disjonction(depot: Path) -> None:
    """`data/train/v*/preferences.jsonl` (prompt, chosen, rejected) est comparé (revue O4b)."""
    texte = mots("p", 30)
    paire = {
        "prompt": [{"role": "user", "content": texte}],
        "chosen": [{"role": "assistant", "content": "<réponse-factice-1>"}],
        "rejected": [{"role": "assistant", "content": "<réponse-factice-2>"}],
    }
    ecrire(depot / "data/train/v9/preferences.jsonl", [paire])
    item = {"id": "Q-501", "tache": "Q", "entree": {"question": texte}, "provenance": []}
    conflits = vjc.controler_disjonction([item], depot)
    assert any("data/train/v9/preferences#1" in c for c in conflits), conflits
