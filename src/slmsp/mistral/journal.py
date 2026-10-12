"""Journal des appels Mistral, en ajout seul (AD-3 verrou 3, AD-24).

Deux fichiers de `SLMSP_VAR_DIR`, au même schéma de ligne :

- le journal des données (`fichier_journal_donnees`, `appels-mistral.sqlite`) reçoit les
  usages `generation` et `validation` ; les pipelines `data` et `train` peuvent le lire ;
- le journal du juge (`fichier_journal_juge`, `appels-mistral-juge.sqlite`) reçoit l'usage
  `juge-second` ; la liste d'accès de `slmsp.core.artefacts` le refuse à `data` et `train`,
  si bien que les textes d'évaluation envoyés au second juge ne leur sont jamais lisibles.

Chaque journal refuse les usages de l'autre (`UsageInterdit`). Une ligne porte l'appel
(`appel_id`, `session_id`, `usage`), les modèles demandé et résolu, la requête complète en
JSON canonique (corps HTTP, jamais d'en-tête ni de secret) et son SHA-256, le corps brut de
la réponse en octets et son SHA-256, la référence budget (`reservation_id`), le statut et
l'horodatage UTC. Des déclencheurs SQLite refusent toute mise à jour et toute suppression.
"""

from __future__ import annotations

import sqlite3
import uuid
from collections.abc import Iterator, Mapping
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Literal

from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import SlmspError
from slmsp.core.var import dossier_var, ouvrir_sqlite
from slmsp.mistral.config import ConfigMistral

USAGES: Final = ("generation", "juge-second", "validation")
USAGES_JUGE: Final = ("juge-second",)
USAGES_DONNEES: Final = ("generation", "validation")
STATUTS: Final = ("ok", "modele-refuse", "erreur")
VERSION_SCHEMA: Final = 1

StatutAppel = Literal["ok", "modele-refuse", "erreur"]

_CREATION: Final = (
    """
    CREATE TABLE IF NOT EXISTS appels (
        appel_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        usage TEXT NOT NULL,
        modele_demande TEXT NOT NULL,
        modele_resolu TEXT,
        requete TEXT NOT NULL,
        sha256_requete TEXT NOT NULL,
        reponse_brute BLOB,
        sha256_reponse TEXT,
        reservation_id INTEGER,
        statut TEXT NOT NULL,
        statut_http INTEGER,
        horodatage TEXT NOT NULL
    )
    """,
    """
    CREATE TRIGGER IF NOT EXISTS appels_sans_mise_a_jour BEFORE UPDATE ON appels
    BEGIN SELECT RAISE(ABORT, 'journal Mistral en ajout seul'); END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS appels_sans_suppression BEFORE DELETE ON appels
    BEGIN SELECT RAISE(ABORT, 'journal Mistral en ajout seul'); END
    """,
)


class UsageInterdit(SlmspError):
    """Usage inconnu, réservé (`generation` sans jeton du Générateur) ou étranger au journal."""


@dataclass(frozen=True)
class LigneAppel:
    """Une ligne du journal."""

    appel_id: str
    session_id: str
    usage: str
    modele_demande: str
    modele_resolu: str | None
    requete: str
    sha256_requete: str
    reponse_brute: bytes | None
    sha256_reponse: str | None
    reservation_id: int | None
    statut: str
    statut_http: int | None
    horodatage: str


class JournalMistral:
    """Journal SQLite en ajout seul, limité aux usages `usages_admis`."""

    def __init__(self, chemin: str | Path, usages_admis: tuple[str, ...] | list[str]) -> None:
        inconnus = [u for u in usages_admis if u not in USAGES]
        if inconnus or not usages_admis:
            raise UsageInterdit(f"usages de journal invalides : {list(usages_admis)!r}")
        self.chemin = Path(chemin)
        self.usages_admis = tuple(usages_admis)
        with self._transaction() as connexion:
            (version,) = connexion.execute("PRAGMA user_version").fetchone()
            if version not in (0, VERSION_SCHEMA):
                raise SlmspError(
                    f"{self.chemin} : version de schéma {version} inattendue "
                    f"(attendu {VERSION_SCHEMA})"
                )
            for requete in _CREATION:
                connexion.execute(requete)
            if version == 0:
                connexion.execute(f"PRAGMA user_version = {VERSION_SCHEMA}")

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        connexion = ouvrir_sqlite(self.chemin)
        try:
            connexion.isolation_level = None
            connexion.execute("BEGIN IMMEDIATE")
            try:
                yield connexion
            except BaseException:
                if connexion.in_transaction:
                    connexion.execute("ROLLBACK")
                raise
            connexion.execute("COMMIT")
        finally:
            connexion.close()

    def inscrire(
        self,
        *,
        session_id: str,
        usage: str,
        modele_demande: str,
        modele_resolu: str | None,
        requete: Mapping[str, Any],
        reponse_brute: bytes | None,
        reservation_id: int | None,
        statut: StatutAppel,
        statut_http: int | None,
    ) -> str:
        """Ajoute un appel et renvoie son `appel_id` (uuid4 hexadécimal).

        Lève `UsageInterdit` si `usage` n'est pas admis par ce journal, `ValueError` pour un
        statut inconnu.
        """
        if usage not in self.usages_admis:
            raise UsageInterdit(
                f"usage {usage!r} refusé par le journal {self.chemin.name} "
                f"(admis : {', '.join(self.usages_admis)})"
            )
        if statut not in STATUTS:
            raise ValueError(f"statut d'appel inconnu : {statut!r}")
        brut = bytes(reponse_brute) if reponse_brute is not None else None
        canonique = json_canonique(dict(requete))
        appel_id = uuid.uuid4().hex
        with self._transaction() as connexion:
            connexion.execute(
                "INSERT INTO appels (appel_id, session_id, usage, modele_demande, modele_resolu, "
                "requete, sha256_requete, reponse_brute, sha256_reponse, reservation_id, statut, "
                "statut_http, horodatage) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    appel_id,
                    session_id,
                    usage,
                    modele_demande,
                    modele_resolu,
                    canonique.decode("utf-8"),
                    sha256_hex(canonique),
                    brut,
                    sha256_hex(brut) if brut is not None else None,
                    reservation_id,
                    statut,
                    statut_http,
                    datetime.now(UTC).isoformat(),
                ),
            )
        return appel_id

    def _lignes(self, requete: str, parametres: tuple[Any, ...] = ()) -> list[LigneAppel]:
        with closing(ouvrir_sqlite(self.chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            lignes = connexion.execute(requete, parametres).fetchall()
        return [LigneAppel(**dict(ligne)) for ligne in lignes]

    def lire(self, appel_id: str) -> LigneAppel | None:
        """Ligne de l'appel `appel_id`, ou `None`."""
        lignes = self._lignes("SELECT * FROM appels WHERE appel_id = ?", (appel_id,))
        return lignes[0] if lignes else None

    def appels(self) -> list[LigneAppel]:
        """Toutes les lignes, dans l'ordre d'inscription."""
        return self._lignes("SELECT * FROM appels ORDER BY rowid")


def journal_pour(
    usage: str, config: ConfigMistral, dossier: str | Path | None = None
) -> JournalMistral:
    """Journal de `usage` : celui du juge pour `juge-second`, celui des données sinon.

    `dossier` vaut par défaut `SLMSP_VAR_DIR`. Lève `UsageInterdit` pour un usage inconnu.
    """
    base = Path(dossier) if dossier is not None else dossier_var()
    if usage in USAGES_JUGE:
        return JournalMistral(base / config.fichier_journal_juge, USAGES_JUGE)
    if usage in USAGES_DONNEES:
        return JournalMistral(base / config.fichier_journal_donnees, USAGES_DONNEES)
    raise UsageInterdit(f"usage Mistral inconnu : {usage!r} (attendu : {', '.join(USAGES)})")
