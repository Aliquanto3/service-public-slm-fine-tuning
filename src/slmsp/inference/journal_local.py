"""Journal des générations du Modèle de base local, en ajout seul (story 9.7, D-nuit-A1-21).

Fichier `SLMSP_VAR_DIR/generations-locales.sqlite`, de même forme que le journal Mistral
(table `appels`, JSON canonique de la requête, corps brut de la réponse et SHA-256, déclencheurs
refusant toute mise à jour et toute suppression). `generateur = slm:<slug>`. Seul `data build
--preferences` l'alimente ; aucun appel réseau, aucune dépense.
"""

from __future__ import annotations

import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from slmsp.core.artefacts import NOM_JOURNAL_LOCAL
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.var import dossier_var, ouvrir_sqlite

USAGE_LOCAL: Final = "generation-locale"
PREFIXE_GENERATEUR: Final = "slm:"

_CREATION: Final = (
    """
    CREATE TABLE IF NOT EXISTS appels (
        appel_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        usage TEXT NOT NULL,
        generateur TEXT NOT NULL,
        requete TEXT NOT NULL,
        sha256_requete TEXT NOT NULL,
        reponse_brute BLOB,
        sha256_reponse TEXT,
        statut TEXT NOT NULL,
        horodatage TEXT NOT NULL
    )
    """,
    """
    CREATE TRIGGER IF NOT EXISTS appels_sans_mise_a_jour BEFORE UPDATE ON appels
    BEGIN SELECT RAISE(ABORT, 'journal local en ajout seul'); END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS appels_sans_suppression BEFORE DELETE ON appels
    BEGIN SELECT RAISE(ABORT, 'journal local en ajout seul'); END
    """,
)


class JournalLocal:
    """Journal SQLite en ajout seul des générations locales."""

    def __init__(self, chemin: str | Path | None = None) -> None:
        self.chemin = Path(chemin) if chemin is not None else dossier_var() / NOM_JOURNAL_LOCAL
        connexion = ouvrir_sqlite(self.chemin)
        try:
            for requete in _CREATION:
                connexion.execute(requete)
            connexion.commit()
        finally:
            connexion.close()

    def inscrire(
        self,
        *,
        session_id: str,
        slug: str,
        requete: Mapping[str, object],
        reponse: str | None,
        statut: str = "ok",
    ) -> str:
        """Ajoute un appel (`generateur = slm:<slug>`) et renvoie son `appel_id`."""
        canonique = json_canonique(dict(requete))
        brut = reponse.encode("utf-8") if reponse is not None else None
        appel_id = uuid.uuid4().hex
        connexion = ouvrir_sqlite(self.chemin)
        try:
            connexion.execute(
                "INSERT INTO appels (appel_id, session_id, usage, generateur, requete, "
                "sha256_requete, reponse_brute, sha256_reponse, statut, horodatage) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    appel_id,
                    session_id,
                    USAGE_LOCAL,
                    f"{PREFIXE_GENERATEUR}{slug}",
                    canonique.decode("utf-8"),
                    sha256_hex(canonique),
                    brut,
                    sha256_hex(brut) if brut is not None else None,
                    statut,
                    datetime.now(UTC).isoformat(),
                ),
            )
            connexion.commit()
        finally:
            connexion.close()
        return appel_id

    def lire(self, appel_id: str) -> dict[str, object] | None:
        """Ligne de `appel_id` sous forme de dictionnaire, ou `None`."""
        connexion = ouvrir_sqlite(self.chemin)
        try:
            curseur = connexion.execute("SELECT * FROM appels WHERE appel_id = ?", (appel_id,))
            ligne = curseur.fetchone()
            colonnes = [c[0] for c in curseur.description]
        finally:
            connexion.close()
        return dict(zip(colonnes, ligne, strict=True)) if ligne else None
