"""Stockage local de l'application (story 12.2) : SQLite dans `tmp_path`, contenus aléatoires."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from slmsp.app.stockage import DELAI_ANNULATION, JournalApplication, Stockage
from slmsp.core.erreurs import SlmspError
from slmsp.core.evenements import Fin
from slmsp.core.schemas.journal_requetes import EntreeJournalRequetes
from slmsp.harness.taches import charger_taches


def _factices() -> Any:
    """Doublures du Harnais (`tests/harness/factices.py`), chargées par chemin."""
    chemin = Path(__file__).parents[1] / "harness" / "factices.py"
    spec = importlib.util.spec_from_file_location("factices_harnais_app", chemin)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Horloge:
    def __init__(self) -> None:
        self.instant = datetime(2026, 1, 1, tzinfo=UTC)
        self.monotone = 0.0

    def __call__(self) -> datetime:
        return self.instant


def _aleatoire() -> str:
    return uuid.uuid4().hex


def _stockage(tmp_path: Path, horloge: Horloge | None = None) -> Stockage:
    h = horloge or Horloge()
    return Stockage(tmp_path / "assistant.sqlite", horloge=h, monotone=lambda: h.monotone)


def _entree(instant: datetime, hote: str = "h.example") -> EntreeJournalRequetes:
    return EntreeJournalRequetes(
        horodatage=instant, profil="assistant", hote=hote, methode="POST", statut="envoyee"
    )


def _conversation(s: Stockage) -> tuple[str, str]:
    texte = _aleatoire()
    identifiant = s.enregistrer_conversation(
        tache="Q", messages=[{"role": "user", "content": texte}], sources=[]
    )
    return identifiant, texte


def test_conversation_aller_retour_et_titre(tmp_path: Path) -> None:
    s = _stockage(tmp_path)
    identifiant, texte = _conversation(s)
    lue = s.lire_conversation(identifiant)
    assert lue is not None and lue["titre"] == texte[:60]
    assert lue["messages"] == [{"role": "user", "content": texte}]
    assert [c["id"] for c in s.lister_conversations()] == [identifiant]


def test_suppression_immediate_puis_annulation_sous_5_s(tmp_path: Path) -> None:
    h = Horloge()
    s = _stockage(tmp_path, h)
    identifiant, _ = _conversation(s)
    assert s.supprimer_conversation(identifiant)
    assert s.lire_conversation(identifiant) is None  # disparue de la base
    h.monotone = DELAI_ANNULATION - 0.1
    assert s.annuler_suppression(identifiant)
    assert s.lire_conversation(identifiant) is not None


def test_annulation_refusee_apres_5_s(tmp_path: Path) -> None:
    h = Horloge()
    s = _stockage(tmp_path, h)
    identifiant, texte = _conversation(s)
    s.supprimer_conversation(identifiant)
    h.monotone = DELAI_ANNULATION + 0.1
    assert not s.annuler_suppression(identifiant)
    assert s.lire_conversation(identifiant) is None
    assert not s.supprimer_conversation("inconnue")
    # le contenu n'a jamais de copie sur disque
    for fichier in tmp_path.iterdir():
        assert texte.encode() not in fichier.read_bytes()


def test_purge_du_journal_a_30_jours_a_l_ouverture_et_a_l_inscription(tmp_path: Path) -> None:
    h = Horloge()
    s = _stockage(tmp_path, h)
    j = JournalApplication(s)
    j.inscrire(_entree(h.instant - timedelta(days=31), "ancien.example"))
    # l'inscription d'une entrée purge aussi les plus anciennes
    j.inscrire(_entree(h.instant, "recent.example"))
    assert [e.hote for e in j.lister()] == ["recent.example"]
    # à l'ouverture : on vieillit l'horloge
    h.instant += timedelta(days=31)
    s2 = Stockage(s.chemin, horloge=h)
    assert JournalApplication(s2).lister() == []


def test_effacer_le_journal_vide_la_table(tmp_path: Path) -> None:
    h = Horloge()
    j = JournalApplication(_stockage(tmp_path, h))
    j.inscrire(_entree(h.instant))
    j.inscrire(_entree(h.instant))
    assert len(j.lister(limite=1)) == 1 and len(j.lister()) == 2
    j.effacer()
    assert j.lister() == []


def test_reglage_relu_apres_redemarrage(tmp_path: Path) -> None:
    s = _stockage(tmp_path)
    assert s.lire_reglage("hors_ligne_force") is False
    s.ecrire_reglage("hors_ligne_force", True)
    assert _stockage(tmp_path).lire_reglage("hors_ligne_force") is True
    with pytest.raises(KeyError):
        s.ecrire_reglage("inconnu", 1)


def test_effacer_historique_conversations_et_retours(tmp_path: Path) -> None:
    s = _stockage(tmp_path)
    identifiant, _ = _conversation(s)
    s.supprimer_conversation(_conversation(s)[0])
    s.enregistrer_retour(
        tache="Q", question=_aleatoire(), reponse=_aleatoire(), sources=[], pouce="bas"
    )
    s.ecrire_reglage("plus_deplie", True)
    s.effacer_historique()
    assert s.lister_conversations() == [] and s.lister_retours() == []
    assert s.lire_reglage("plus_deplie") is True
    assert not s.annuler_suppression(identifiant)


def test_retour_enregistre(tmp_path: Path) -> None:
    s = _stockage(tmp_path)
    question = _aleatoire()
    s.enregistrer_retour(
        tache="Q",
        question=question,
        reponse="r",
        sources=[{"u": 1}],
        pouce="haut",
        commentaire="c",
    )
    (retour,) = s.lister_retours()
    assert retour["question"] == question and retour["sources"] == [{"u": 1}]
    with pytest.raises(ValueError):
        s.enregistrer_retour(tache="Q", question="q", reponse="r", sources=[], pouce="x")  # type: ignore[arg-type]


def test_version_de_schema_inconnue_sans_ecrasement(tmp_path: Path) -> None:
    chemin = tmp_path / "assistant.sqlite"
    connexion = sqlite3.connect(chemin)
    connexion.execute("PRAGMA user_version = 99")
    connexion.close()
    avant = chemin.read_bytes()
    with pytest.raises(SlmspError, match="version de schéma 99"):
        Stockage(chemin)
    connexion = sqlite3.connect(chemin)
    tables = connexion.execute("SELECT name FROM sqlite_master").fetchall()
    connexion.close()
    assert tables == [] and chemin.read_bytes()[:16] == avant[:16]


def test_document_temoin_avec_journal_application(tmp_path: Path) -> None:
    import httpx2  # noqa: TID251 (tests : transport interne)

    from slmsp.cli._assemblage import assembler

    f: Any = _factices()
    journal = JournalApplication(_stockage(tmp_path))
    marqueur = "MARQUEUR-" + _aleatoire()
    llm = f.FakeLlm(f.script(f.mots(4, "sortie")))
    with assembler(
        "base:x",
        charger_taches().tache("CR"),
        journal=journal,
        transport_interne=httpx2.MockTransport(lambda r: pytest.fail("requête sortante")),
        llm=llm,
        embedder=f.FakeEmbedder(),
        vector_store=f.FakeVectorStore(),
    ) as a:
        evenements = list(a.service.repondre("CR", [{"role": "user", "content": marqueur}]))
    assert isinstance(evenements[-1], Fin)
    assert marqueur in json.dumps(llm.appels[0]["messages"])
    assert journal.lister() == []
