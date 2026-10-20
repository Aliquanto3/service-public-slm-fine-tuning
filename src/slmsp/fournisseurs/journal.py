"""Journal SQLite des appels aux fournisseurs compatibles OpenAI, en ajout seul (AD-3 verrou 3).

Une ligne par tentative : appel, session, fournisseur, usage, modèles demandé et résolu,
requête en JSON canonique (corps seul, jamais d'en-tête ni de clé) et son SHA-256, corps brut
de la réponse et son SHA-256, référence budget, statut, code HTTP, coût annoncé par le
fournisseur (`usage.cost` d'OpenRouter, en USD, s'il est présent) et horodatage UTC. Des
déclencheurs refusent toute mise à jour et toute suppression.

Le fichier est choisi par l'appelant. Celui des juges tiers (`appels-juges-tiers.sqlite`,
`SLMSP_VAR_DIR`) est hors de la liste d'accès des lecteurs `data` et `train` (AD-24) : les
textes d'évaluation n'y fuient pas.
"""

from __future__ import annotations

import sqlite3
import uuid
from collections.abc import Iterator, Mapping
from contextlib import closing, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Literal

from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.var import ouvrir_sqlite

NOM_JOURNAL_JUGES_TIERS: Final = "appels-juges-tiers.sqlite"
NOM_JOURNAL_JUGE_DONNEES: Final = "appels-juge-donnees.sqlite"
"""Journal du juge de données (story O1), distinct de celui des juges tiers."""
STATUTS: Final = ("ok", "erreur")

StatutAppel = Literal["ok", "erreur"]

_CREATION: Final = (
    """
    CREATE TABLE IF NOT EXISTS appels (
        appel_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        fournisseur TEXT NOT NULL,
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
        tokens_entree INTEGER,
        tokens_sortie INTEGER,
        cout_fournisseur_usd REAL,
        horodatage TEXT NOT NULL
    )
    """,
    """
    CREATE TRIGGER IF NOT EXISTS appels_sans_mise_a_jour BEFORE UPDATE ON appels
    BEGIN SELECT RAISE(ABORT, 'journal des fournisseurs en ajout seul'); END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS appels_sans_suppression BEFORE DELETE ON appels
    BEGIN SELECT RAISE(ABORT, 'journal des fournisseurs en ajout seul'); END
    """,
)


class JournalAppels:
    """Journal en ajout seul des appels d'un client compatible OpenAI."""

    def __init__(self, chemin: str | Path) -> None:
        self.chemin = Path(chemin)
        with self._transaction() as connexion:
            for requete in _CREATION:
                connexion.execute(requete)

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
        fournisseur: str,
        usage: str,
        modele_demande: str,
        modele_resolu: str | None,
        requete: Mapping[str, Any],
        reponse_brute: bytes | None,
        reservation_id: int | None,
        statut: StatutAppel,
        statut_http: int | None,
        tokens: tuple[int, int] | None = None,
        cout_fournisseur_usd: float | None = None,
    ) -> str:
        """Ajoute une tentative et renvoie son `appel_id` (uuid4 hexadécimal)."""
        if statut not in STATUTS:
            raise ValueError(f"statut d'appel inconnu : {statut!r}")
        brut = bytes(reponse_brute) if reponse_brute is not None else None
        canonique = json_canonique(dict(requete))
        appel_id = uuid.uuid4().hex
        entree, sortie = tokens if tokens is not None else (None, None)
        with self._transaction() as connexion:
            connexion.execute(
                "INSERT INTO appels (appel_id, session_id, fournisseur, usage, modele_demande, "
                "modele_resolu, requete, sha256_requete, reponse_brute, sha256_reponse, "
                "reservation_id, statut, statut_http, tokens_entree, tokens_sortie, "
                "cout_fournisseur_usd, horodatage) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    appel_id,
                    session_id,
                    fournisseur,
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
                    entree,
                    sortie,
                    cout_fournisseur_usd,
                    datetime.now(UTC).isoformat(),
                ),
            )
        return appel_id

    def reussis(self, usage: str, modele_demande: str) -> dict[str, dict[str, Any]]:
        """Dernier appel `ok` de `usage` et `modele_demande` par SHA-256 de requête : `appel_id`,
        `session_id`, `reponse_brute`, `sha256_reponse` (reprise sans second paiement)."""
        with closing(ouvrir_sqlite(self.chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            lignes = connexion.execute(
                "SELECT appel_id, session_id, sha256_requete, reponse_brute, sha256_reponse "
                "FROM appels WHERE statut = 'ok' AND usage = ? AND modele_demande = ? "
                "ORDER BY rowid",
                (usage, modele_demande),
            ).fetchall()
        return {str(ligne["sha256_requete"]): dict(ligne) for ligne in lignes}

    def appels(self) -> list[dict[str, Any]]:
        """Toutes les lignes, dans l'ordre d'inscription."""
        with closing(ouvrir_sqlite(self.chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            lignes = connexion.execute("SELECT * FROM appels ORDER BY rowid").fetchall()
        return [dict(ligne) for ligne in lignes]
