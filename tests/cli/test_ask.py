"""`slmsp ask` : affichage, conversation, `--json`, `--journal`, hors ligne (story 4.5).

Ports factices (`tests/harness/factices.py`, chargé par chemin) et transport interne espion :
aucun serveur, aucun réseau. Les textes sont des mots aléatoires (D1.1).
"""

from __future__ import annotations

import functools
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx2  # noqa: TID251 (tests : transport interne espion)
import pytest

from slmsp.cli import CodeSortie, main
from slmsp.cli import _assemblage as assemblage
from slmsp.net.journal import JournalMemoire


def _factices() -> Any:
    nom = "harness_factices"
    if nom not in sys.modules:
        chemin = Path(__file__).resolve().parents[1] / "harness" / "factices.py"
        spec = importlib.util.spec_from_file_location(nom, chemin)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[nom] = module
        spec.loader.exec_module(module)
    return sys.modules[nom]


F = _factices()
MODELE = "base:granite-4.0-1b"
REPONSE = F.mots(12, "reponse") + " [1]"


class Transport:
    """Transport interne espion : compte les requêtes et répond 200."""

    def __init__(self) -> None:
        self.requetes: list[Any] = []

    def __call__(self, requete: Any) -> Any:
        self.requetes.append(requete)
        return httpx2.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": {}})


@pytest.fixture
def banc(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Remplace `assembler` par une version aux ports factices ; renvoie les doublures."""
    transport = Transport()
    journal = JournalMemoire()
    llm = F.FakeLlm(F.script(REPONSE))
    store = F.FakeVectorStore([F.passage(1, 0.9)])
    monkeypatch.setattr(
        assemblage,
        "assembler",
        functools.partial(
            assemblage.assembler,
            journal=journal,
            transport_interne=httpx2.MockTransport(transport),
            llm=llm,
            embedder=F.FakeEmbedder(),
            vector_store=store,
        ),
    )
    return SimpleNamespace(transport=transport, journal=journal, llm=llm, store=store)


def test_question_affiche_reponse_sources_et_avertissement(banc, capsys) -> None:
    code = main(["ask", "--modele", MODELE, "--hors-ligne", F.mots(5, "q")])
    sortie = capsys.readouterr().out
    assert code == CodeSortie.SUCCES
    assert REPONSE in sortie
    assert "Sources :" in sortie
    passage = banc.store.passages[0]
    assert passage.titre in sortie and passage.url in sortie and "2026-09-25" in sortie
    assert "Ne vaut pas avis juridique." in sortie


def test_conversation_ajoutee_et_reutilisee(banc, tmp_path, capsys) -> None:
    fichier = tmp_path / "conv.json"
    q1, q2 = F.mots(4, "q1"), F.mots(4, "q2")
    args = ["ask", "--modele", MODELE, "--hors-ligne", "--conversation", str(fichier)]
    assert main([*args, q1]) == CodeSortie.SUCCES
    echange = json.loads(fichier.read_text(encoding="utf-8"))
    assert [m["role"] for m in echange] == ["user", "assistant"]
    assert echange[0]["content"] == q1 and echange[1]["content"] == REPONSE
    assert main([*args, q2]) == CodeSortie.SUCCES
    assert len(json.loads(fichier.read_text(encoding="utf-8"))) == 4
    envoyes = json.dumps(banc.llm.appels[-1]["messages"], ensure_ascii=False)
    assert q1 in envoyes and q2 in envoyes
    capsys.readouterr()


def test_conversation_non_ecrivable_est_une_erreur_sans_trace(banc, tmp_path, capsys) -> None:
    fichier = tmp_path / "absent" / "conv.json"
    args = ["ask", "--modele", MODELE, "--hors-ligne", "--conversation", str(fichier)]
    assert main([*args, F.mots(3, "q")]) == CodeSortie.ERREUR
    assert "conversation non enregistrée" in capsys.readouterr().err


def test_json_emet_les_evenements_bruts(banc, capsys) -> None:
    assert main(["ask", "--modele", MODELE, "--hors-ligne", "--json", F.mots(3, "q")]) == 0
    lignes = [json.loads(ligne) for ligne in capsys.readouterr().out.splitlines()]
    types = [ligne["type"] for ligne in lignes]
    assert types[0] == "jeton" and types[-1] == "fin" and "sources" in types


def test_journal_affiche_les_requetes_sortantes(banc, capsys) -> None:
    code = main(["ask", "--modele", MODELE, "--hors-ligne", "--journal", F.mots(3, "q")])
    sortie = capsys.readouterr().out
    assert code == 0
    assert "Requêtes sortantes :" in sortie and "(aucune)" in sortie


def test_hors_ligne_n_appelle_jamais_le_transport(banc, capsys) -> None:
    """FR-10 : même pour RD, aucune requête, sonde comprise."""
    code = main(["ask", "--modele", MODELE, "--tache", "RD", "--hors-ligne", F.mots(4, "q")])
    assert code == 0
    assert banc.transport.requetes == []
    assert banc.journal.lister() == []
    capsys.readouterr()


def test_modele_invalide_est_une_erreur_d_usage(capsys) -> None:
    assert main(["ask", "--modele", "granite", "question"]) == CodeSortie.USAGE
    assert "base:<slug>" in capsys.readouterr().err


def test_tache_inconnue_et_question_vide_sont_des_erreurs(banc, capsys) -> None:
    assert main(["ask", "--modele", MODELE, "--tache", "ZZ", "question"]) != 0
    assert main(["ask", "--modele", MODELE, "  "]) == CodeSortie.USAGE
    capsys.readouterr()


@pytest.mark.lent
def test_reel_ask_de_bout_en_bout() -> None:
    """Vrai `llama-server`, GGUF Granite 1B et Index réel (hors ligne forcé, aucun réseau).

    Prérequis : ceux de `tests/harness/test_integration_question.py` (`SLMSP_VENDOR_DIR`,
    `SLMSP_MODELS_DIR`, `SLMSP_INDEX_RACINE`). Lancer avec `-m lent`.
    """
    chemin = Path(__file__).resolve().parents[1] / "harness" / "test_integration_question.py"
    spec = importlib.util.spec_from_file_location("ask_integration_question", chemin)
    assert spec is not None and spec.loader is not None
    question = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = question
    spec.loader.exec_module(question)
    racine = question.prerequis(question.GRANITE)
    from slmsp.core.evenements import Fin, Jeton

    with assemblage.assembler(
        f"base:{question.GRANITE}", hors_ligne=True, racine=racine, journal=JournalMemoire()
    ) as a:
        evenements = list(
            a.service.repondre(
                "Q",
                [{"role": "user", "content": question.QUESTION}],
                {"temperature": 0, "seed": 42, "max_tokens": 200},
            )
        )
    assert isinstance(evenements[-1], Fin)
    assert "".join(e.texte for e in evenements if isinstance(e, Jeton)).strip()
