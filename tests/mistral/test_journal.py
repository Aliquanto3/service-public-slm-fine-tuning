"""Journaux des appels Mistral : séparation par usage, ajout seul, liste d'accès d'AD-24."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

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


@pytest.mark.parametrize("lecteur", ["data", "train"])
def test_journal_du_juge_refuse_a_l_ouverture(lecteur: str) -> None:
    """Ouvert avec un `lecteur`, le journal du juge lève `LectureInterdite` sans être créé."""
    config = charger_mistral()
    with pytest.raises(LectureInterdite):
        journal_pour("juge-second", config, lecteur=lecteur)
    with pytest.raises(LectureInterdite):
        JournalMistral(
            dossier_var() / config.fichier_journal_juge, ("juge-second",), lecteur=lecteur
        )
    assert not (dossier_var() / config.fichier_journal_juge).exists()


@pytest.mark.parametrize("lecteur", ["data", "train"])
def test_journal_des_donnees_en_lecture_seule(lecteur: str) -> None:
    """Le journal des données s'ouvre pour `data` et `train`, en lecture seule."""
    config = charger_mistral()
    appel_id = inscrire(journal_pour("validation", config), "validation")
    lecture = journal_pour("validation", config, lecteur=lecteur)
    assert [ligne.appel_id for ligne in lecture.appels()] == [appel_id]
    assert lecture.lire(appel_id) is not None
    assert [ligne.appel_id for ligne in lecture.appels_session("session-test")] == [appel_id]
    with pytest.raises(UsageInterdit):
        inscrire(lecture, "validation")
    assert len(journal_pour("validation", config).appels()) == 1


def test_journal_hors_liste_d_acces_refuse(tmp_path: Path) -> None:
    """Un journal hors de `SLMSP_VAR_DIR` est refusé au lecteur `data`."""
    with pytest.raises(LectureInterdite):
        journal_pour("validation", charger_mistral(), tmp_path, lecteur="data")


# --- Schéma v2 (story 9.2) : méta de génération, jeton, migration -------------------------

META: dict[str, Any] = {
    "gabarit_id": "gabarit-factice",
    "version_gabarit": 1,
    "sha256_gabarit": "a" * 64,
    "amorce_ids": ["amorce-b", "amorce-a"],
}


def jeton_du_generateur() -> object:
    pytest.importorskip("mistralai")  # le Générateur importe le client, donc le SDK
    from slmsp.mistral.generateur import _JETON

    return _JETON


def inscrire_generation(journal: JournalMistral, **options: Any) -> str:
    valeurs: dict[str, Any] = {
        "session_id": "session-gen",
        "usage": "generation",
        "modele_demande": "mistral-large-latest",
        "modele_resolu": "mistral-large-2512",
        "requete": {"messages": [{"role": "user", "content": "<consigne-factice>"}]},
        "reponse_brute": b'{"ok":1}',
        "reservation_id": 3,
        "statut": "ok",
        "statut_http": 200,
        **META,
    }
    return journal.inscrire(**{**valeurs, **options})


def test_generation_avec_jeton_et_meta(tmp_path: Path) -> None:
    jeton = jeton_du_generateur()

    journal = journal_pour("generation", charger_mistral(), tmp_path)
    ligne = journal.lire(inscrire_generation(journal, jeton=jeton))
    assert ligne is not None
    assert ligne.gabarit_id == "gabarit-factice" and ligne.version_gabarit == 1
    assert ligne.sha256_gabarit == "a" * 64
    assert ligne.amorce_ids == '["amorce-b","amorce-a"]'  # ordre conservé, JSON canonique


@pytest.mark.parametrize("options", [{}, {"jeton": object()}, {"jeton": None}])
def test_generation_sans_jeton_refusee(tmp_path: Path, options: dict[str, Any]) -> None:
    journal = journal_pour("generation", charger_mistral(), tmp_path)
    with pytest.raises(UsageInterdit):
        inscrire_generation(journal, **options)
    assert journal.appels() == []


@pytest.mark.parametrize(
    "manque", ["gabarit_id", "version_gabarit", "sha256_gabarit", "amorce_ids"]
)
def test_generation_sans_meta_refusee(tmp_path: Path, manque: str) -> None:
    jeton = jeton_du_generateur()

    journal = journal_pour("generation", charger_mistral(), tmp_path)
    with pytest.raises(UsageInterdit):
        inscrire_generation(journal, jeton=jeton, **{manque: None})
    with pytest.raises(UsageInterdit):
        inscrire_generation(journal, jeton=jeton, amorce_ids=[])
    assert journal.appels() == []


@pytest.mark.parametrize("usage", ["validation", "juge-second"])
@pytest.mark.parametrize("champ", ["gabarit_id", "version_gabarit", "sha256_gabarit", "amorce_ids"])
def test_meta_refusee_hors_generation(tmp_path: Path, usage: str, champ: str) -> None:
    journal = journal_pour(usage, charger_mistral(), tmp_path)
    with pytest.raises(UsageInterdit):
        journal.inscrire(
            session_id="s",
            usage=usage,
            modele_demande="m",
            modele_resolu=None,
            requete={},
            reponse_brute=None,
            reservation_id=None,
            statut="ok",
            statut_http=200,
            **{champ: META[champ]},
        )
    assert journal.appels() == []


def test_appels_session(tmp_path: Path) -> None:
    jeton = jeton_du_generateur()

    journal = journal_pour("generation", charger_mistral(), tmp_path)
    premier = inscrire_generation(journal, jeton=jeton)
    inscrire_generation(journal, jeton=jeton, session_id="autre-session")
    second = inscrire(journal, "validation")
    assert [ligne.appel_id for ligne in journal.appels_session("session-gen")] == [premier]
    assert [ligne.appel_id for ligne in journal.appels_session("session-test")] == [second]
    assert journal.appels_session("inconnue") == []


_SCHEMA_V1 = """
CREATE TABLE appels (
    appel_id TEXT PRIMARY KEY, session_id TEXT NOT NULL, usage TEXT NOT NULL,
    modele_demande TEXT NOT NULL, modele_resolu TEXT, requete TEXT NOT NULL,
    sha256_requete TEXT NOT NULL, reponse_brute BLOB, sha256_reponse TEXT,
    reservation_id INTEGER, statut TEXT NOT NULL, statut_http INTEGER,
    horodatage TEXT NOT NULL
);
CREATE TRIGGER appels_sans_mise_a_jour BEFORE UPDATE ON appels
BEGIN SELECT RAISE(ABORT, 'journal Mistral en ajout seul'); END;
CREATE TRIGGER appels_sans_suppression BEFORE DELETE ON appels
BEGIN SELECT RAISE(ABORT, 'journal Mistral en ajout seul'); END;
INSERT INTO appels VALUES ('a1', 's1', 'validation', 'mistral-large-latest', NULL, '{}',
    'x', X'7B7D', 'y', 4, 'ok', 200, '2026-10-12T00:00:00+00:00');
PRAGMA user_version = 1;
"""


def test_migration_v1_vers_v2(tmp_path: Path) -> None:
    jeton = jeton_du_generateur()

    chemin = tmp_path / "appels-mistral.sqlite"
    with closing(sqlite3.connect(chemin)) as connexion:
        connexion.executescript(_SCHEMA_V1)
    journal = journal_pour("validation", charger_mistral(), tmp_path)
    with closing(sqlite3.connect(chemin)) as connexion:
        assert connexion.execute("PRAGMA user_version").fetchone() == (2,)
        colonnes = [c[1] for c in connexion.execute("PRAGMA table_info(appels)")]
    assert colonnes[-4:] == ["gabarit_id", "version_gabarit", "sha256_gabarit", "amorce_ids"]
    (ancienne,) = journal.appels()
    assert ancienne.appel_id == "a1" and ancienne.reponse_brute == b"{}"
    assert ancienne.gabarit_id is None and ancienne.amorce_ids is None
    inscrire_generation(journal, jeton=jeton)
    assert len(journal_pour("generation", charger_mistral(), tmp_path).appels()) == 2
    with closing(sqlite3.connect(chemin)) as connexion:  # toujours en ajout seul
        with pytest.raises(sqlite3.DatabaseError, match="ajout seul"):
            connexion.execute("DELETE FROM appels")


def test_version_inconnue_refusee(tmp_path: Path) -> None:
    from slmsp.core.erreurs import SlmspError

    chemin = tmp_path / "appels-mistral.sqlite"
    with closing(sqlite3.connect(chemin)) as connexion:
        connexion.execute("PRAGMA user_version = 3")
    with pytest.raises(SlmspError, match="version de schéma 3"):
        journal_pour("validation", charger_mistral(), tmp_path)
