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

from slmsp.app.stockage import (
    DELAI_ANNULATION,
    LONGUEUR_TITRE,
    JournalApplication,
    Stockage,
    dossier_donnees,
)
from slmsp.core.erreurs import SlmspError
from slmsp.core.evenements import AppelOutil, Fin, ResultatOutil
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
    h = Horloge()
    s = _stockage(tmp_path, h)
    _conversation(s)
    identifiant, texte = _conversation(s)
    assert s.supprimer_conversation(identifiant)  # annulation en attente
    s.enregistrer_retour(
        tache="Q", question=_aleatoire(), reponse=_aleatoire(), sources=[], pouce="bas"
    )
    s.ecrire_reglage("plus_deplie", True)
    j = JournalApplication(s)
    j.inscrire(_entree(h.instant))
    s.effacer_historique()
    assert s.lister_conversations() == [] and s.lister_retours() == []
    assert s.lire_reglage("plus_deplie") is True and len(j.lister()) == 1
    # l'annulation en attente a ete oubliee : rien n'est restaure, dans le delai de 5 s
    assert not s.annuler_suppression(identifiant)
    assert s.lire_conversation(identifiant) is None
    # le contenu n'existe plus dans aucun fichier de la base
    for fichier in tmp_path.iterdir():
        assert texte.encode() not in fichier.read_bytes()


def test_vacuum_reduit_le_fichier(tmp_path: Path) -> None:
    s = _stockage(tmp_path)
    gros = "x" * 200_000
    for _ in range(5):
        s.enregistrer_conversation(tache="Q", messages=[{"role": "user", "content": gros}])
    avant = s.chemin.stat().st_size
    s.effacer_historique()
    assert s.chemin.stat().st_size < avant / 2


def test_contenu_oublie_a_l_echeance_sans_nouvelle_suppression(tmp_path: Path) -> None:
    h = Horloge()
    s = _stockage(tmp_path, h)
    identifiant, _ = _conversation(s)
    s.supprimer_conversation(identifiant)
    assert identifiant in s._supprimees
    h.monotone = DELAI_ANNULATION + 0.1
    s.lister_conversations()  # simple acces : la purge a lieu
    assert s._supprimees == {}


def test_annulation_n_ecrase_pas_une_conversation_reenregistree(tmp_path: Path) -> None:
    s = _stockage(tmp_path)
    identifiant, _ = _conversation(s)
    s.supprimer_conversation(identifiant)
    nouveau = _aleatoire()
    s.enregistrer_conversation(
        tache="Q", messages=[{"role": "user", "content": nouveau}], identifiant=identifiant
    )
    assert not s.annuler_suppression(identifiant)
    lue = s.lire_conversation(identifiant)
    assert lue is not None and lue["messages"][0]["content"] == nouveau


def test_contenu_non_ascii_et_titre_tronque(tmp_path: Path) -> None:
    s = _stockage(tmp_path)
    texte = "Éléonore à l'œuvre : 日本語 😀 " * 10
    identifiant = s.enregistrer_conversation(
        tache="Q", messages=[{"role": "user", "content": texte}], sources=[{"t": "é"}]
    )
    lue = s.lire_conversation(identifiant)
    assert lue is not None
    assert lue["messages"][0]["content"] == texte and lue["sources"] == [{"t": "é"}]
    assert lue["titre"] == " ".join(texte.split())[:LONGUEUR_TITRE]
    assert len(lue["titre"]) == LONGUEUR_TITRE
    s.enregistrer_retour(tache="Q", question="é", reponse="日本", sources=[], pouce="haut")
    assert s.lister_retours()[0]["reponse"] == "日本"


def test_emplacement_dans_le_profil_jamais_le_depot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "profil"))
    assert dossier_donnees() == tmp_path / "profil" / "AssistantSP"
    s = Stockage()
    assert s.chemin == tmp_path / "profil" / "AssistantSP" / "assistant.sqlite"
    assert s.chemin.is_file()
    assert Path(__file__).parents[2] not in s.chemin.parents


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
    # SQLite passe le fichier en WAL a l'ouverture (octets 18-19 de l'en-tete) : on verifie
    # le fond, c'est-a-dire ni table creee ni `user_version` modifiee.
    assert tables == [] and chemin.read_bytes()[:16] == avant[:16]
    connexion = sqlite3.connect(chemin)
    (version,) = connexion.execute("PRAGMA user_version").fetchone()
    connexion.close()
    assert version == 99


def _assembler_avec(journal: JournalApplication, code: str, llm: Any, requete: Any) -> list[Any]:
    import httpx2  # noqa: TID251 (tests : transport interne)

    from slmsp.cli._assemblage import assembler

    f: Any = _factices()
    transport = httpx2.MockTransport(requete)
    with assembler(
        "base:x",
        charger_taches().tache(code),
        journal=journal,
        transport_interne=transport,
        llm=llm,
        embedder=f.FakeEmbedder(),
        vector_store=f.FakeVectorStore(),
    ) as a:
        if code == "RD":
            a.service.outils = _OutilsViaPasserelle(a.passerelle, transport)
        messages = [{"role": "user", "content": "MARQUEUR-" + _aleatoire()}]
        return list(a.service.repondre(code, messages))


class _OutilsViaPasserelle:
    """`ToolPort` de test : l'appel passe par la vraie passerelle, qui ecrit au journal."""

    def __init__(self, passerelle: Any, transport: Any) -> None:
        self.passerelle, self.transport = passerelle, transport

    def lister_outils(self) -> list[dict[str, Any]]:
        from slmsp.mcp.outils import charger_outils

        return charger_outils()

    def appeler(self, nom: str, arguments: Any) -> dict[str, Any]:
        corps = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": nom, "arguments": dict(arguments)},
        }
        with self.passerelle.client("assistant", transport_interne=self.transport) as http:
            return http.post("https://mcp.data.gouv.fr/mcp", json=corps).json()


def test_document_temoin_aucune_requete_sortante_journal_vide(tmp_path: Path) -> None:
    f: Any = _factices()
    journal = JournalApplication(_stockage(tmp_path))
    llm = f.FakeLlm(f.script(f.mots(4, "sortie")))
    evenements = _assembler_avec(journal, "CR", llm, lambda r: pytest.fail("requete sortante"))
    assert isinstance(evenements[-1], Fin)
    assert journal.lister() == []


def test_requete_autorisee_inscrite_dans_le_journal_application(tmp_path: Path) -> None:
    import httpx2  # noqa: TID251 (tests : transport interne)

    f: Any = _factices()
    journal = JournalApplication(_stockage(tmp_path))
    termes = f.mots(2, "termes")
    appel = AppelOutil(id="c1", nom="search_datasets", arguments={"query": termes})
    llm = f.FakeLlm(
        [appel, Fin(raison="terminee", usage={"prompt_tokens": 1, "completion_tokens": 1})],
        f.script(f.mots(5, "finale")),
    )
    contenu = [{"type": "text", "text": f.mots(6, "resultat-outil")}]

    def repondre(requete: Any) -> Any:
        return httpx2.Response(
            200, json={"jsonrpc": "2.0", "id": 1, "result": {"content": contenu}}
        )

    evenements = _assembler_avec(journal, "RD", llm, repondre)
    assert any(isinstance(e, ResultatOutil) and not e.erreur for e in evenements), evenements
    (entree,) = [e for e in journal.lister() if e.outil == "search_datasets"]
    assert entree.hote == "mcp.data.gouv.fr"
    assert json.loads(entree.termes or "{}") == {"query": termes}
    # persiste : un nouveau Stockage sur le meme fichier relit l'entree
    relu = JournalApplication(Stockage(journal._stockage.chemin)).lister()
    assert [e.outil for e in relu] == [e.outil for e in journal.lister()]
