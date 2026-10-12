"""Journaux des appels Mistral : séparation par usage, ajout seul, liste d'accès d'AD-24."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from slmsp.core.artefacts import chemin_autorise
from slmsp.core.canonique import sha256_hex
from slmsp.core.erreurs import LectureInterdite
from slmsp.core.var import dossier_var
from slmsp.mistral.config import charger_mistral
from slmsp.mistral.journal import JournalMistral, UsageInterdit, journal_pour


def inscrire(journal: JournalMistral, usage: str, brut: bytes | None = b'{"ok":1}') -> str:
    return journal.inscrire(
        session_id="session-test",
        usage=usage,
        modele_demande="mistral-large-latest",
        modele_resolu="mistral-large-2512",
        requete={"model": "mistral-large-latest", "messages": [{"role": "user", "content": "é"}]},
        reponse_brute=brut,
        reservation_id=7,
        statut="ok",
        statut_http=200,
    )


def test_journal_pour_route_par_usage(tmp_path: Path) -> None:
    config = charger_mistral()
    juge = journal_pour("juge-second", config, tmp_path)
    assert juge.chemin == tmp_path / "appels-mistral-juge.sqlite"
    assert juge.usages_admis == ("juge-second",)
    for usage in ("generation", "validation"):
        donnees = journal_pour(usage, config, tmp_path)
        assert donnees.chemin == tmp_path / "appels-mistral.sqlite"
        assert donnees.usages_admis == ("generation", "validation")
    with pytest.raises(UsageInterdit):
        journal_pour("autre", config, tmp_path)


def test_dossier_par_defaut_est_var() -> None:
    assert journal_pour("juge-second", charger_mistral()).chemin.parent == dossier_var()


@pytest.mark.parametrize(
    ("usage_journal", "usage_etranger"),
    [("juge-second", "validation"), ("juge-second", "generation"), ("validation", "juge-second")],
)
def test_usage_etranger_refuse(tmp_path: Path, usage_journal: str, usage_etranger: str) -> None:
    journal = journal_pour(usage_journal, charger_mistral(), tmp_path)
    with pytest.raises(UsageInterdit):
        inscrire(journal, usage_etranger)
    assert journal.appels() == []


def test_usages_admis_inconnus_refuses(tmp_path: Path) -> None:
    with pytest.raises(UsageInterdit):
        JournalMistral(tmp_path / "j.sqlite", ("autre",))
    with pytest.raises(UsageInterdit):
        JournalMistral(tmp_path / "j.sqlite", ())


def test_ligne_complete(tmp_path: Path) -> None:
    journal = journal_pour("juge-second", charger_mistral(), tmp_path)
    brut = '{"réponse": "brute"}\n'.encode()
    appel_id = inscrire(journal, "juge-second", brut)
    ligne = journal.lire(appel_id)
    assert ligne is not None
    assert len(appel_id) == 32 and int(appel_id, 16) >= 0
    assert ligne.session_id == "session-test"
    assert ligne.usage == "juge-second"
    assert ligne.modele_demande == "mistral-large-latest"
    assert ligne.modele_resolu == "mistral-large-2512"
    assert ligne.requete == (
        '{"messages":[{"content":"é","role":"user"}],"model":"mistral-large-latest"}'
    )
    assert ligne.reponse_brute == brut
    assert ligne.sha256_reponse == sha256_hex(brut)
    assert ligne.sha256_requete == sha256_hex(ligne.requete)
    assert ligne.reservation_id == 7
    assert ligne.statut == "ok" and ligne.statut_http == 200
    assert ligne.horodatage.endswith("+00:00")
    assert journal.lire("inconnu") is None


def test_reponse_absente(tmp_path: Path) -> None:
    journal = journal_pour("validation", charger_mistral(), tmp_path)
    ligne = journal.lire(inscrire(journal, "validation", None))
    assert ligne is not None
    assert ligne.reponse_brute is None and ligne.sha256_reponse is None


def test_statut_inconnu_refuse(tmp_path: Path) -> None:
    journal = journal_pour("validation", charger_mistral(), tmp_path)
    with pytest.raises(ValueError):
        journal.inscrire(
            session_id="s",
            usage="validation",
            modele_demande="m",
            modele_resolu=None,
            requete={},
            reponse_brute=None,
            reservation_id=None,
            statut="autre",  # type: ignore[arg-type]
            statut_http=None,
        )


def test_ajout_seul(tmp_path: Path) -> None:
    journal = journal_pour("juge-second", charger_mistral(), tmp_path)
    inscrire(journal, "juge-second")
    with closing(sqlite3.connect(journal.chemin)) as connexion:
        with pytest.raises(sqlite3.DatabaseError, match="ajout seul"):
            connexion.execute("UPDATE appels SET statut = 'erreur'")
        with pytest.raises(sqlite3.DatabaseError, match="ajout seul"):
            connexion.execute("DELETE FROM appels")
    assert len(journal.appels()) == 1


def test_reouverture_garde_les_lignes(tmp_path: Path) -> None:
    config = charger_mistral()
    inscrire(journal_pour("juge-second", config, tmp_path), "juge-second")
    inscrire(journal_pour("juge-second", config, tmp_path), "juge-second")
    assert len(journal_pour("juge-second", config, tmp_path).appels()) == 2


@pytest.mark.parametrize("lecteur", ["data", "train"])
def test_liste_d_acces(lecteur: str) -> None:
    """Le journal du juge est refusé à `data` et `train` ; celui des données est lisible."""
    config = charger_mistral()
    juge = journal_pour("juge-second", config)
    donnees = journal_pour("validation", config)
    with pytest.raises(LectureInterdite):
        chemin_autorise(juge.chemin, lecteur)
    assert chemin_autorise(donnees.chemin, lecteur) == donnees.chemin.resolve()
