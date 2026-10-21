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


# --- Story 15.5 (dev2) ------------------------------------------------------------------------


def test_dev2_disjoint_de_dev1_mais_pas_de_lui_meme(depot: Path) -> None:
    """Les autres jeux `devN` assemblés entrent dans la référence ; le jeu contrôlé en est exclu."""
    ecrire(
        depot / "eval/jeu/dev1/items.jsonl",
        [item("Q-501", mots("g", 30), "https://exemple.invalide/dev1")],
    )
    copie = item("Q-601", mots("g", 30), "https://exemple.invalide/dev1")
    sortie = vjc.controler_disjonction([copie], depot, version="dev2")
    assert any("dev1/Q-501" in c and "URL" in c for c in sortie), sortie
    assert any("dev1/Q-501" in c and "texte identique" in c for c in sortie), sortie
    neuf = item("Q-602", mots("h", 30), "https://exemple.invalide/dev2")
    ecrire(depot / "eval/jeu/dev2/items.jsonl", [neuf])
    assert vjc.controler_disjonction([neuf], depot, version="dev2") == []
    assert vjc.versions_reference(depot, exclure="dev2") == ["v1.0", "v1.1", "dev1"]


def test_disjonction_contre_une_autre_racine(
    depot: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--reference` : items lus dans le worktree, jeux de référence lus dans le dépôt principal."""
    worktree = tmp_path / "wt"
    ecrire(
        worktree / "eval/construction/dev2/Q.jsonl",
        [item("Q-601", mots("b", 30), "https://exemple.invalide/autre")],
    )
    code = vjc.main(
        ["disjonction", "--version", "dev2", "--racine", str(worktree), "--reference", str(depot)]
    )
    assert code == 1
    assert "v1.1/Q-002" in capsys.readouterr().out


# --- Story O4c ---------------------------------------------------------------------------------


def test_parametres_du_juge_transmis() -> None:
    """Sans `reasoning`, GLM raisonnait jusqu'à `max_tokens` : la config du juge est transmise."""
    from slmsp.judge.config import ConfigJugeTiers

    config = ConfigJugeTiers(
        modele="<modele-factice>", temperature=0.0, max_tokens=8000, effort_raisonnement="low"
    )
    parametres = vjc.parametres_appel(config)
    assert parametres["reasoning"] == {"effort": "low"}
    assert parametres["temperature"] == 0.0
    schema = parametres["response_format"]["json_schema"]
    assert schema["strict"] is True and schema["schema"] is vjc.SCHEMA_VERDICT
    assert parametres["provider"] == {"require_parameters": True}
    objet = ConfigJugeTiers(modele="<m>", max_tokens=10, format_reponse="json_object")
    assert vjc.parametres_appel(objet)["response_format"] == {"type": "json_object"}
    assert "reasoning" not in vjc.parametres_appel(objet)


def test_relance_corrective_apres_sortie_vide() -> None:
    prompts: list[str] = []

    def appeler(juge: str, prompt: str) -> str:
        prompts.append(prompt)
        return "" if len(prompts) == 1 else verdict()

    lignes = vjc.verifier_items(ITEMS[:1], ["deepseek"], appeler)
    assert lignes[0]["decision"] == "retenu"
    assert len(prompts) == 2 and prompts[1].startswith("Ta réponse précédente")
    assert identifiant_du(prompts[1]) == ITEMS[0]["id"]  # consigne d'origine incluse


def test_relance_bornee() -> None:
    appels: list[str] = []

    def appeler(juge: str, prompt: str) -> str:
        appels.append(juge)
        return "{}"

    lignes = vjc.verifier_items(ITEMS[:1], ["deepseek", "glm"], appeler)
    assert lignes[0]["decision"] == "incomplet"
    assert len(appels) == 2 * (vjc.RELANCES_MAX + 1)


def test_incomplet_rejoue_seulement_le_juge_manquant(depot: Path) -> None:
    ecrire(depot / "eval/construction/dev1/Q.jsonl", ITEMS[:1])
    appels: list[str] = []
    panne = {"glm": True}

    def appeler(juge: str, prompt: str) -> str:
        appels.append(juge)
        if juge == "glm" and panne["glm"]:
            raise TimeoutError("<delai-factice>")
        return verdict()

    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 1
    panne["glm"] = False
    appels.clear()
    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 0
    assert appels == ["glm"]


def test_verdict_d_une_ancienne_consigne_non_repris(depot: Path) -> None:
    ecrire(depot / "eval/construction/dev1/Q.jsonl", ITEMS[:1])
    ancien = {
        "item_id": ITEMS[0]["id"],
        "item_sha256": vjc.empreinte_item(ITEMS[0]),
        "tache": "Q",
        "juges": {"deepseek": json.loads(verdict(ambigu=True)), "glm": None},
        "decision": "incomplet",
        "motifs": ["glm : pas de verdict valide"],
    }
    ecrire(depot / "eval/construction/dev1/verdicts-croises.jsonl", [ancien])
    appels: list[str] = []

    def appeler(juge: str, prompt: str) -> str:
        appels.append(juge)
        return verdict()

    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 0
    assert appels == ["deepseek", "glm"]


def test_contestation_sans_effet_rejet_maintenu(depot: Path) -> None:
    """Revue O4c : plus de voie d'appel ; seul un item corrigé est revérifié."""
    ecrire(depot / "eval/construction/dev1/Q.jsonl", ITEMS[:2])
    reponses: dict[tuple[str, str], str | Exception] = {
        ("deepseek", ITEMS[0]["id"]): verdict(ambigu=True)
    }
    appels: list[str] = []
    base = appelant(reponses)

    def appeler(juge: str, prompt: str) -> str:
        appels.append(identifiant_du(prompt))
        return base(juge, prompt)

    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 0
    ecrire(
        depot / "eval/construction/dev1/contestations.jsonl",
        [
            {
                "item_id": ITEMS[0]["id"],
                "item_sha256": vjc.empreinte_item(ITEMS[0]),
                "justification": "<justification-factice>",
            }
        ],
    )
    appels.clear()
    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 0
    assert appels == []  # la contestation ne relance rien
    corrige = [{**ITEMS[0], "version_item": 2}, ITEMS[1]]
    ecrire(depot / "eval/construction/dev1/Q.jsonl", corrige)
    reponses.clear()
    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 0
    assert appels == [ITEMS[0]["id"]] * 2  # l'item corrigé, par les deux juges
    courant = vjc.verdicts_courants(depot / "eval/construction/dev1/verdicts-croises.jsonl")
    assert courant[ITEMS[0]["id"]]["decision"] == "retenu"


def test_tout_verdict_d_une_autre_consigne_est_refait(depot: Path) -> None:
    """Revue O4c : un retenu ou un rejeté d'une consigne antérieure n'est pas repris."""
    ecrire(depot / "eval/construction/dev1/Q.jsonl", ITEMS[:2])
    anciens = [
        {
            "item_id": it["id"],
            "item_sha256": vjc.empreinte_item(it),
            "tache": "Q",
            "juges": {"deepseek": json.loads(verdict()), "glm": json.loads(verdict())},
            "decision": decision,
            "motifs": [],
            "version_prompt": vjc.VERSION_PROMPT - 1,
        }
        for it, decision in zip(ITEMS[:2], ("retenu", "rejete"), strict=True)
    ]
    ecrire(depot / "eval/construction/dev1/verdicts-croises.jsonl", anciens)
    appels: list[str] = []

    def appeler(juge: str, prompt: str) -> str:
        appels.append(identifiant_du(prompt))
        return verdict()

    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 0
    assert sorted(appels) == sorted([ITEMS[0]["id"], ITEMS[1]["id"]] * 2)
    courants = vjc.verdicts_courants(depot / "eval/construction/dev1/verdicts-croises.jsonl")
    assert {v["version_prompt"] for v in courants.values()} == {vjc.VERSION_PROMPT}


def test_consigne_neutre_sans_incitation_a_retenir() -> None:
    prompt = vjc.prompt_verification(ITEMS[0])
    assert "points_cles_reference" in prompt and "fictif" in prompt
    for incitation in ("ne rendent pas", "n'est pas un défaut", "parmi d'autres"):
        assert incitation not in prompt


def test_disjonction_incomplete_sans_train_ni_seed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Un worktree sans `data/train` ni `runs/data-seed` ne se déclare pas « disjoint »."""
    ecrire(tmp_path / "eval/jeu/v1.0/items.jsonl", [item("Q-001", mots("a", 30))])
    ecrire(tmp_path / "eval/jeu/dev2/items.jsonl", [item("Q-601", mots("z", 30))])
    assert vjc.main(["disjonction", "--version", "dev2", "--racine", str(tmp_path)]) == 1
    sortie = capsys.readouterr().out
    assert "INCOMPLET" in sortie
    assert "disjoint" not in sortie.replace("INCOMPLET", "")


def test_calibrage_dans_la_reference(depot: Path) -> None:
    ecrire(
        depot / "eval/calibrage/echantillon-calibrage.jsonl",
        [item("Q-301", mots("k", 30), "https://exemple.invalide/calib")],
    )
    reference, lus = vjc.construire_reference(depot, 5)
    assert "calibrage" in lus
    copie = item("Q-701", mots("k", 30), "https://exemple.invalide/calib")
    sortie = vjc.controler_disjonction([copie], depot, version="dev2")
    assert any("calibrage/Q-301" in c for c in sortie), sortie


# --- Story 16.1a : revérification forcée -----------------------------------------------------


def test_forcer_rappelle_et_le_plus_recent_fait_foi(depot: Path) -> None:
    ecrire(depot / "eval/construction/dev1/Q.jsonl", ITEMS[:2])
    cible = ITEMS[1]["id"]
    rejet = {("glm", cible): verdict(coherent=False)}
    appels: list[tuple[str, str]] = []

    def appeler(juge: str, prompt: str) -> str:
        appels.append((juge, identifiant_du(prompt)))
        return appelant(rejet)(juge, prompt)

    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 0
    chemin = depot / "eval/construction/dev1/verdicts-croises.jsonl"
    assert vjc.verdicts_courants(chemin)[cible]["decision"] == "rejete"

    appels.clear()  # sans --forcer : reprise, aucun appel
    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler) == 0
    assert appels == []

    rejet.clear()  # forcé : les deux juges sont rappelés pour cet item seul
    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler, forcer=[cible]) == 0
    assert sorted(appels) == [("deepseek", cible), ("glm", cible)]
    lignes = [json.loads(x) for x in chemin.read_text(encoding="utf-8").splitlines()]
    assert len(lignes) == 3  # ancien verdict conservé
    assert lignes[1]["decision"] == "rejete" and "force" not in lignes[1]
    assert lignes[2]["decision"] == "retenu" and lignes[2]["force"] is True
    assert lignes[2]["horodatage"]
    assert vjc.verdicts_courants(chemin)[cible]["decision"] == "retenu"


def test_forcer_reprend_un_item_retire_du_jeu_assemble(depot: Path) -> None:
    ecrire(depot / "eval/construction/dev1/Q.jsonl", ITEMS[:2])
    ecrire(depot / "eval/jeu/dev1/items.jsonl", ITEMS[:1])  # ITEMS[1] retiré à l'assemblage
    cible = ITEMS[1]["id"]
    appels: list[tuple[str, str]] = []

    def appeler(juge: str, prompt: str) -> str:
        appels.append((juge, identifiant_du(prompt)))
        return verdict()

    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler, forcer=[cible]) == 0
    assert ("deepseek", cible) in appels and ("glm", cible) in appels


def test_forcer_identifiant_inconnu_refuse_avant_appel(
    depot: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ecrire(depot / "eval/construction/dev1/Q.jsonl", ITEMS[:2])
    appels: list[str] = []

    def appeler(juge: str, prompt: str) -> str:
        appels.append(juge)
        return verdict()

    argv = ["verifier", "--version", "dev1", "--racine", str(depot), "--forcer", "Q-999"]
    with pytest.raises(vjc.ErreurOutil, match="Q-999"):
        vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler, forcer=["Q-999"])
    assert appels == []
    assert vjc.main(argv) == 2
    assert "Q-999" in capsys.readouterr().err


def test_forcer_echec_ne_remplace_pas_un_rejet(
    depot: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    ecrire(depot / "eval/construction/dev1/Q.jsonl", ITEMS[:2])
    cible = ITEMS[1]["id"]
    assert (
        vjc.cmd_verifier(
            depot, "dev1", ["deepseek", "glm"], appelant({("glm", cible): verdict(coherent=False)})
        )
        == 0
    )
    chemin = depot / "eval/construction/dev1/verdicts-croises.jsonl"
    avant = chemin.read_text(encoding="utf-8")

    panne = appelant({("glm", cible): RuntimeError("panne")})
    assert vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], panne, forcer=[cible]) == 1
    assert chemin.read_text(encoding="utf-8") == avant  # rien d'écrit
    assert vjc.verdicts_courants(chemin)[cible]["decision"] == "rejete"
    assert cible in capsys.readouterr().err


def test_forcer_deja_fait_pas_de_rappel_sauf_forcer_encore(depot: Path) -> None:
    ecrire(depot / "eval/construction/dev1/Q.jsonl", ITEMS[:2])
    cible = ITEMS[1]["id"]
    appels: list[str] = []

    def appeler(juge: str, prompt: str) -> str:
        appels.append(juge)
        return verdict()

    vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler)
    appels.clear()
    vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler, forcer=[cible])
    assert len(appels) == 2
    appels.clear()
    vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler, forcer=[cible])
    assert appels == []  # relance après succès : 0 appel
    vjc.cmd_verifier(
        depot, "dev1", ["deepseek", "glm"], appeler, forcer=[cible], forcer_encore=True
    )
    assert len(appels) == 2


def test_forcer_ecrit_au_fil_de_l_eau_et_strip(depot: Path) -> None:
    ecrire(depot / "eval/construction/dev1/Q.jsonl", ITEMS[:2])
    chemin = depot / "eval/construction/dev1/verdicts-croises.jsonl"

    def appeler(juge: str, prompt: str) -> str:
        if identifiant_du(prompt) == ITEMS[1]["id"]:
            raise KeyboardInterrupt  # interruption pendant le 2e item
        return verdict()

    with pytest.raises(KeyboardInterrupt):
        vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], appeler)
    assert [json.loads(x)["item_id"] for x in chemin.read_text(encoding="utf-8").splitlines()] == [
        ITEMS[0]["id"]
    ]
    appels: list[str] = []

    def ok(juge: str, prompt: str) -> str:
        appels.append(identifiant_du(prompt))
        return verdict()

    vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], ok)
    appels.clear()
    vjc.cmd_verifier(depot, "dev1", ["deepseek", "glm"], ok, forcer=[f" {ITEMS[0]['id']} "])
    assert appels == [ITEMS[0]["id"]] * 2
