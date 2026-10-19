"""Cache des verdicts du Juge et journal de ses appels (`SLMSP_VAR_DIR/verdicts.sqlite`).

La clé d'un verdict combine les empreintes de l'item canonique, de la sortie canonique, de
la section de grille, du gabarit et du schéma, plus le modèle et l'effort : un verdict n'est
jamais redemandé ni réservé deux fois. Tables :

- `verdicts` : un verdict par clé (JSON), jamais réécrit ;
- `echecs` : nombre de sorties non conformes par clé ;
- `appels` : journal en ajout seul de chaque tentative payée (tokens, coût en euros, issue) ;
- `lots` et `lot_requetes` : lots batch locaux, avec leur `batch_id` Anthropic, persistés
  avant toute soumission ou attente, pour être relus après un arrêt.

Statuts d'un lot : `reserve` (persisté, pas encore créé chez Anthropic), `en_cours` (créé,
`batch_id` connu), `collecte`, `annule` (annulation confirmée), `abandonne` (création non
confirmée). Les écritures sont transactionnelles ; rien n'est jamais supprimé. Les verdicts
ne servent qu'au banc d'évaluation (AD-3 verrou 6) : ce module n'exporte rien vers `data` ni
`train`.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator, Mapping, Sequence
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Final, Literal

from slmsp.budget.tarifs import UsageTokens
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import SlmspError
from slmsp.core.items import ItemBase
from slmsp.core.schemas.verdict import Verdict
from slmsp.core.var import dossier_var, ouvrir_sqlite
from slmsp.judge.prompt import PromptJuge

NOM_CACHE: Final = "verdicts.sqlite"
VERSION_SCHEMA: Final = 1

StatutLot = Literal["reserve", "en_cours", "collecte", "annule", "abandonne"]
STATUTS_OUVERTS: Final = ("reserve", "en_cours")

_CREATION: Final = (
    """
    CREATE TABLE IF NOT EXISTS verdicts (
        cle TEXT PRIMARY KEY,
        item_id TEXT NOT NULL,
        modele TEXT NOT NULL,
        effort TEXT NOT NULL,
        mode TEXT,
        verdict TEXT NOT NULL,
        invalide INTEGER NOT NULL,
        cout_eur REAL NOT NULL,
        tokens_entree INTEGER NOT NULL,
        tokens_sortie INTEGER NOT NULL,
        tokens_ecriture_cache INTEGER NOT NULL,
        tokens_lecture_cache INTEGER NOT NULL,
        cree_le TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS echecs (
        cle TEXT PRIMARY KEY,
        item_id TEXT NOT NULL,
        nombre INTEGER NOT NULL,
        dernier_motif TEXT,
        maj_le TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS appels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cle TEXT NOT NULL,
        item_id TEXT NOT NULL,
        mode TEXT NOT NULL,
        lot_id TEXT,
        tokens_entree INTEGER,
        tokens_sortie INTEGER,
        tokens_ecriture_cache INTEGER,
        tokens_lecture_cache INTEGER,
        cout_eur REAL NOT NULL,
        issue TEXT NOT NULL,
        horodatage TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS lots (
        lot_id TEXT PRIMARY KEY,
        batch_id TEXT UNIQUE,
        modele TEXT NOT NULL,
        effort TEXT NOT NULL,
        statut TEXT NOT NULL,
        nb_retenu INTEGER,
        cree_le TEXT NOT NULL,
        soumis_le TEXT,
        maj_le TEXT NOT NULL,
        motif TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS lot_requetes (
        lot_id TEXT NOT NULL,
        rang INTEGER NOT NULL,
        custom_id TEXT NOT NULL,
        cle TEXT NOT NULL,
        item_id TEXT NOT NULL,
        schema TEXT NOT NULL,
        PRIMARY KEY (lot_id, custom_id)
    )
    """,
)


def _maintenant() -> str:
    return datetime.now().astimezone().isoformat()


def cle_verdict(
    item: ItemBase, sortie: Mapping[str, Any], prompt: PromptJuge, modele: str, effort: str
) -> str:
    """Clé du cache : SHA-256 du JSON canonique des empreintes et du couple modèle, effort.

    La sortie est réduite à sa forme canonique `{texte, appels_outils, sources}` (AD-12) :
    une autre clé n'entre pas dans l'empreinte ; une clé absente vaut `None` (texte) ou une
    liste vide.
    """
    canonique = {
        "texte": sortie.get("texte"),
        "appels_outils": sortie.get("appels_outils") or [],
        "sources": sortie.get("sources") or [],
    }
    return sha256_hex(
        json_canonique(
            {
                "item": sha256_hex(json_canonique(item.model_dump(mode="json"))),
                "sortie": sha256_hex(json_canonique(canonique)),
                "section": prompt.sha_section,
                "gabarit": prompt.sha_gabarit,
                "schema": prompt.sha_schema,
                "modele": modele,
                "effort": effort,
            }
        )
    )


@dataclass(frozen=True)
class VerdictEnCache:
    """Verdict lu dans le cache, avec le mode et le coût de l'appel qui l'a produit."""

    verdict: Verdict
    mode: str | None
    cout_eur: float
    usage: UsageTokens


@dataclass(frozen=True)
class RequeteLot:
    """Requête d'un lot : `custom_id` Anthropic, clé de cache, item et schéma de sortie."""

    custom_id: str
    cle: str
    item_id: str
    schema: dict[str, Any]


@dataclass(frozen=True)
class LotLocal:
    """Lot batch local (`lot_id` = identifiant de réservation au registre de budget)."""

    lot_id: str
    batch_id: str | None
    modele: str
    effort: str
    statut: str
    nb_retenu: int | None
    cree_le: str
    soumis_le: str | None


class CacheVerdicts:
    """Cache SQLite des verdicts, des échecs, des appels et des lots du Juge."""

    def __init__(self, chemin: str | Path | None = None) -> None:
        self.chemin = Path(chemin) if chemin is not None else dossier_var() / NOM_CACHE
        with self._transaction() as connexion:
            (version,) = connexion.execute("PRAGMA user_version").fetchone()
            if version not in (0, VERSION_SCHEMA):
                raise SlmspError(
                    f"{self.chemin} : version de schéma {version} inattendue "
                    f"(attendu {VERSION_SCHEMA})"
                )
            for requete in _CREATION:
                connexion.execute(requete)
            colonnes = {ligne[1] for ligne in connexion.execute("PRAGMA table_info(lots)")}
            if "motif" not in colonnes:  # migration additive des bases antérieures à INC-1
                connexion.execute("ALTER TABLE lots ADD COLUMN motif TEXT")
            if version == 0:
                connexion.execute(f"PRAGMA user_version = {VERSION_SCHEMA}")

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        connexion = ouvrir_sqlite(self.chemin)
        try:
            connexion.isolation_level = None
            connexion.row_factory = sqlite3.Row
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

    def _lire(self, requete: str, parametres: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        with closing(ouvrir_sqlite(self.chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            return connexion.execute(requete, parametres).fetchall()

    # --- verdicts -------------------------------------------------------------------------

    def lire(self, cle: str) -> VerdictEnCache | None:
        """Verdict de la clé `cle`, ou `None` s'il n'est pas en cache."""
        lignes = self._lire("SELECT * FROM verdicts WHERE cle = ?", (cle,))
        if not lignes:
            return None
        ligne = lignes[0]
        return VerdictEnCache(
            verdict=Verdict.model_validate_json(ligne["verdict"]),
            mode=ligne["mode"],
            cout_eur=ligne["cout_eur"],
            usage=UsageTokens(
                ligne["tokens_entree"],
                ligne["tokens_sortie"],
                ligne["tokens_ecriture_cache"],
                ligne["tokens_lecture_cache"],
            ),
        )

    def ecrire(
        self,
        cle: str,
        verdict: Verdict,
        *,
        modele: str,
        effort: str,
        mode: str | None,
        cout_eur: float,
        usage: UsageTokens | None,
    ) -> bool:
        """Inscrit le verdict de `cle` s'il n'y est pas déjà ; renvoie vrai s'il est inscrit."""
        usage = usage if usage is not None else UsageTokens(0, 0)
        with self._transaction() as connexion:
            curseur = connexion.execute(
                "INSERT OR IGNORE INTO verdicts (cle, item_id, modele, effort, mode, verdict, "
                "invalide, cout_eur, tokens_entree, tokens_sortie, tokens_ecriture_cache, "
                "tokens_lecture_cache, cree_le) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    cle,
                    verdict.id,
                    modele,
                    effort,
                    mode,
                    verdict.model_dump_json(),
                    int(verdict.invalide),
                    cout_eur,
                    usage.entree,
                    usage.sortie,
                    usage.ecriture_cache,
                    usage.lecture_cache,
                    _maintenant(),
                ),
            )
            return curseur.rowcount == 1

    # --- échecs ---------------------------------------------------------------------------

    def echecs(self, cle: str) -> int:
        """Nombre de sorties non conformes déjà comptées pour `cle`."""
        lignes = self._lire("SELECT nombre FROM echecs WHERE cle = ?", (cle,))
        return int(lignes[0]["nombre"]) if lignes else 0

    def compter_echec(self, cle: str, item_id: str, motif: str) -> int:
        """Compte une sortie non conforme de plus pour `cle` et renvoie le nouveau total."""
        with self._transaction() as connexion:
            connexion.execute(
                "INSERT INTO echecs (cle, item_id, nombre, dernier_motif, maj_le) "
                "VALUES (?, ?, 1, ?, ?) ON CONFLICT (cle) DO UPDATE SET "
                "nombre = nombre + 1, dernier_motif = excluded.dernier_motif, "
                "maj_le = excluded.maj_le",
                (cle, item_id, motif[:500], _maintenant()),
            )
            (nombre,) = connexion.execute(
                "SELECT nombre FROM echecs WHERE cle = ?", (cle,)
            ).fetchone()
            return int(nombre)

    # --- journal des appels ---------------------------------------------------------------

    def journaliser_appel(
        self,
        *,
        cle: str,
        item_id: str,
        mode: str,
        lot_id: str | None,
        usage: UsageTokens | None,
        cout_eur: float,
        issue: str,
    ) -> None:
        """Ajoute une tentative payée au journal `appels` (`usage` nul : compté au pire cas)."""
        compteurs: tuple[int | None, ...] = (
            (usage.entree, usage.sortie, usage.ecriture_cache, usage.lecture_cache)
            if usage is not None
            else (None, None, None, None)
        )
        with self._transaction() as connexion:
            connexion.execute(
                "INSERT INTO appels (cle, item_id, mode, lot_id, tokens_entree, tokens_sortie, "
                "tokens_ecriture_cache, tokens_lecture_cache, cout_eur, issue, horodatage) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (cle, item_id, mode, lot_id, *compteurs, cout_eur, issue, _maintenant()),
            )

    def appel_journalise(self, lot_id: str, cle: str) -> bool:
        """Vrai si le journal compte déjà une tentative de `cle` dans le lot `lot_id`."""
        lignes = self._lire(
            "SELECT 1 FROM appels WHERE lot_id = ? AND cle = ? LIMIT 1", (lot_id, cle)
        )
        return bool(lignes)

    def cumul_appels(self, cle: str) -> tuple[float, UsageTokens]:
        """Coût (EUR) et tokens cumulés de toutes les tentatives journalisées de `cle`."""
        (ligne,) = self._lire(
            "SELECT COALESCE(SUM(cout_eur), 0), COALESCE(SUM(tokens_entree), 0), "
            "COALESCE(SUM(tokens_sortie), 0), COALESCE(SUM(tokens_ecriture_cache), 0), "
            "COALESCE(SUM(tokens_lecture_cache), 0) FROM appels WHERE cle = ?",
            (cle,),
        )
        cout, *compteurs = tuple(ligne)
        return float(cout), UsageTokens(*(int(c) for c in compteurs))

    def appels(self) -> list[dict[str, Any]]:
        """Toutes les lignes du journal `appels`, dans l'ordre d'inscription."""
        return [dict(ligne) for ligne in self._lire("SELECT * FROM appels ORDER BY id")]

    # --- lots -----------------------------------------------------------------------------

    def creer_lot(
        self, lot_id: str, modele: str, effort: str, requetes: Sequence[RequeteLot]
    ) -> None:
        """Persiste un lot local `reserve` et ses requêtes, avant toute soumission."""
        maintenant = _maintenant()
        with self._transaction() as connexion:
            connexion.execute(
                "INSERT INTO lots (lot_id, batch_id, modele, effort, statut, nb_retenu, cree_le, "
                "soumis_le, maj_le) VALUES (?, NULL, ?, ?, 'reserve', NULL, ?, NULL, ?)",
                (lot_id, modele, effort, maintenant, maintenant),
            )
            connexion.executemany(
                "INSERT INTO lot_requetes (lot_id, rang, custom_id, cle, item_id, schema) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        lot_id,
                        rang,
                        r.custom_id,
                        r.cle,
                        r.item_id,
                        json_canonique(r.schema).decode("utf-8"),
                    )
                    for rang, r in enumerate(requetes)
                ],
            )

    def _maj_lot(self, lot_id: str, affectations: str, parametres: tuple[Any, ...]) -> None:
        with self._transaction() as connexion:
            curseur = connexion.execute(
                f"UPDATE lots SET {affectations}, maj_le = ? WHERE lot_id = ?",
                (*parametres, _maintenant(), lot_id),
            )
            if curseur.rowcount != 1:
                raise SlmspError(f"lot {lot_id} inconnu du cache de verdicts")

    def fixer_retenu(self, lot_id: str, nb_retenu: int) -> None:
        """Nombre de requêtes retenues par la réservation (les premières, par rang)."""
        self._maj_lot(lot_id, "nb_retenu = ?", (nb_retenu,))

    def marquer_soumis(self, lot_id: str, batch_id: str, soumis_le: datetime | None = None) -> None:
        """Inscrit le `batch_id` Anthropic du lot, sa date de soumission (avec fuseau) et le
        passe `en_cours`."""
        date = soumis_le.isoformat() if soumis_le is not None else _maintenant()
        self._maj_lot(lot_id, "batch_id = ?, statut = 'en_cours', soumis_le = ?", (batch_id, date))

    def changer_statut(self, lot_id: str, statut: StatutLot) -> None:
        """Change le statut du lot (`collecte`, `annule`, `abandonne`…)."""
        self._maj_lot(lot_id, "statut = ?", (statut,))

    def consigner_motif_lot(self, lot_id: str, motif: str) -> None:
        """Motif d'abandon du lot (détail de l'erreur de création), tronqué à 500 caractères."""
        self._maj_lot(lot_id, "motif = ?", (motif[:500],))

    def lot(self, lot_id: str) -> LotLocal | None:
        """Lot local `lot_id`, ou `None`."""
        lignes = self._lire(
            "SELECT lot_id, batch_id, modele, effort, statut, nb_retenu, cree_le, soumis_le "
            "FROM lots WHERE lot_id = ?",
            (lot_id,),
        )
        return LotLocal(*lignes[0]) if lignes else None

    def lots_ouverts(self) -> list[LotLocal]:
        """Lots `reserve` ou `en_cours`, par date de création, à reprendre avant tout lot neuf."""
        lignes = self._lire(
            "SELECT lot_id, batch_id, modele, effort, statut, nb_retenu, cree_le, soumis_le "
            "FROM lots WHERE statut IN (?, ?) ORDER BY cree_le, lot_id",
            STATUTS_OUVERTS,
        )
        return [LotLocal(*ligne) for ligne in lignes]

    def requetes_lot(self, lot_id: str, nb_retenu: int | None = None) -> list[RequeteLot]:
        """Requêtes du lot par rang ; seulement les `nb_retenu` premières si fourni."""
        lignes = self._lire(
            "SELECT custom_id, cle, item_id, schema FROM lot_requetes WHERE lot_id = ? "
            "ORDER BY rang",
            (lot_id,),
        )
        requetes = [
            RequeteLot(ligne["custom_id"], ligne["cle"], ligne["item_id"], json.loads(ligne[3]))
            for ligne in lignes
        ]
        return requetes if nb_retenu is None else requetes[:nb_retenu]
