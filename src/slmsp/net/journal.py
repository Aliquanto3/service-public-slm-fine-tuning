"""Journal des Requêtes sortantes (AD-4) : SQLite dans `SLMSP_VAR_DIR`, ou en mémoire.

La table `requetes` a exactement les 8 colonnes de `EntreeJournalRequetes` (hors
`schema_version`, porté par `PRAGMA user_version`) : ni URL complète, ni en-tête, ni corps
hors `termes`, ni secret.
"""

from __future__ import annotations

import json
import threading
from contextlib import closing
from datetime import datetime
from pathlib import Path
from typing import Any, Final

from slmsp.core.canonique import json_canonique
from slmsp.core.erreurs import SlmspError
from slmsp.core.schemas.journal_requetes import EntreeJournalRequetes
from slmsp.core.var import dossier_var, ouvrir_sqlite

NOM_JOURNAL: Final = "requetes-sortantes.sqlite"
VERSION_SCHEMA: Final = 1
COLONNES: Final = ("horodatage", "profil", "hote", "methode", "outil", "termes", "statut", "mode")

_CREATION = """
CREATE TABLE IF NOT EXISTS requetes (
    horodatage TEXT NOT NULL,
    profil TEXT NOT NULL,
    hote TEXT NOT NULL,
    methode TEXT NOT NULL,
    outil TEXT,
    termes TEXT,
    statut TEXT NOT NULL,
    mode TEXT
)
"""


class JournalSqlite:
    """Journal persistant ; une connexion par opération (WAL, `busy_timeout` 30 s)."""

    def __init__(self, chemin: str | Path | None = None) -> None:
        self.chemin = Path(chemin) if chemin is not None else dossier_var() / NOM_JOURNAL
        with closing(ouvrir_sqlite(self.chemin)) as connexion, connexion:
            (version,) = connexion.execute("PRAGMA user_version").fetchone()
            if version not in (0, VERSION_SCHEMA):
                raise SlmspError(
                    f"{self.chemin} : version de schéma {version} inattendue "
                    f"(attendu {VERSION_SCHEMA})"
                )
            connexion.execute(_CREATION)
            if version == 0:
                connexion.execute(f"PRAGMA user_version = {VERSION_SCHEMA}")

    def inscrire(self, entree: EntreeJournalRequetes) -> None:
        valeurs = (
            entree.horodatage.isoformat(),
            entree.profil,
            entree.hote,
            entree.methode,
            entree.outil,
            entree.termes,
            entree.statut,
            entree.mode,
        )
        with closing(ouvrir_sqlite(self.chemin)) as connexion, connexion:
            connexion.execute(
                f"INSERT INTO requetes ({', '.join(COLONNES)}) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                valeurs,
            )

    def lister(self, limite: int | None = None) -> list[EntreeJournalRequetes]:
        """Entrées du plus récent au plus ancien (`limite` premières si fournie)."""
        requete = f"SELECT {', '.join(COLONNES)} FROM requetes ORDER BY rowid DESC"
        parametres: tuple[Any, ...] = ()
        if limite is not None:
            if limite < 0:
                raise ValueError("limite doit être positive ou nulle")
            requete += " LIMIT ?"
            parametres = (limite,)
        with closing(ouvrir_sqlite(self.chemin)) as connexion:
            lignes = connexion.execute(requete, parametres).fetchall()
        return [
            EntreeJournalRequetes(
                **dict(zip(COLONNES, ligne, strict=True))
                | {"horodatage": datetime.fromisoformat(ligne[0])}
            )
            for ligne in lignes
        ]


class JournalMemoire:
    """Doublure en mémoire de `JournalRequetes`, pour les tests."""

    def __init__(self) -> None:
        self._entrees: list[EntreeJournalRequetes] = []
        self._verrou = threading.Lock()

    def inscrire(self, entree: EntreeJournalRequetes) -> None:
        with self._verrou:
            self._entrees.append(entree)

    def lister(self, limite: int | None = None) -> list[EntreeJournalRequetes]:
        """Entrées du plus récent au plus ancien."""
        if limite is not None and limite < 0:
            raise ValueError("limite doit être positive ou nulle")
        with self._verrou:
            entrees = list(reversed(self._entrees))
        return entrees if limite is None else entrees[:limite]


def extraire_appel_outil(contenu: bytes) -> tuple[str | None, str | None]:
    """`(outil, termes)` d'un corps JSON-RPC `tools/call`, sinon `(None, None)`.

    `termes` est le JSON canonique des `arguments` (ou `None` s'ils manquent ou ne sont pas
    sérialisables).
    """
    try:
        message = json.loads(contenu)
    except (ValueError, TypeError, RecursionError):
        return None, None
    if not isinstance(message, dict) or message.get("method") != "tools/call":
        return None, None
    params = message.get("params")
    if not isinstance(params, dict) or not isinstance(params.get("name"), str):
        return None, None
    outil = params["name"]
    if "arguments" not in params:
        return outil, None
    try:
        termes = json_canonique(params["arguments"]).decode("utf-8")
    except (ValueError, TypeError, RecursionError):
        termes = None
    return outil, termes
