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

Schéma v2 (story 9.2) : une ligne `generation` porte aussi le gabarit (`gabarit_id`,
`version_gabarit`, `sha256_gabarit`) et les `amorce_ids` (liste en JSON canonique). Seul le
Générateur (`slmsp.mistral.generateur`) peut l'écrire : `inscrire(usage="generation")`
exige son jeton de preuve (`_JETON`) et ces quatre champs ; tout autre usage les refuse. Un
journal v1 existant est migré en place (`ALTER TABLE ADD COLUMN`, lignes conservées).
"""

from __future__ import annotations

import importlib
import sqlite3
import uuid
from collections.abc import Iterator, Mapping, Sequence
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
USAGE_GENERATION: Final = "generation"
STATUTS: Final = ("ok", "modele-refuse", "erreur")
VERSION_SCHEMA: Final = 2
MODULE_GENERATEUR: Final = "slmsp.mistral.generateur"

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
        horodatage TEXT NOT NULL,
        gabarit_id TEXT,
        version_gabarit INTEGER,
        sha256_gabarit TEXT,
        amorce_ids TEXT
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

_MIGRATION_V2: Final = (
    "ALTER TABLE appels ADD COLUMN gabarit_id TEXT",
    "ALTER TABLE appels ADD COLUMN version_gabarit INTEGER",
    "ALTER TABLE appels ADD COLUMN sha256_gabarit TEXT",
    "ALTER TABLE appels ADD COLUMN amorce_ids TEXT",
)
"""Passage du schéma v1 (story 5.5) au v2 : colonnes ajoutées, lignes conservées."""


class UsageInterdit(SlmspError):
    """Usage inconnu, réservé (`generation` sans jeton du Générateur) ou étranger au journal."""


def jeton_generateur() -> object | None:
    """Jeton de preuve du Générateur (`slmsp.mistral.generateur._JETON`), s'il existe.

    Le module est importé à la demande : `import slmsp.mistral.journal` ne charge pas
    `mistralai`. Un `ModuleNotFoundError` sur un autre nom (dépendance absente) est relevé.
    """
    try:
        module = importlib.import_module(MODULE_GENERATEUR)
    except ModuleNotFoundError as exc:
        if exc.name == MODULE_GENERATEUR:
            return None
        raise
    return getattr(module, "_JETON", None)


def _meta_generation_valide(
    gabarit_id: Any, version_gabarit: Any, sha256_gabarit: Any, amorce_ids: Any
) -> bool:
    return (
        isinstance(gabarit_id, str)
        and bool(gabarit_id)
        and isinstance(version_gabarit, int)
        and not isinstance(version_gabarit, bool)
        and version_gabarit >= 1
        and isinstance(sha256_gabarit, str)
        and len(sha256_gabarit) == 64
        and amorce_ids is not None
        and not isinstance(amorce_ids, (str, bytes))
        and len(amorce_ids) > 0
        and all(isinstance(i, str) and i for i in amorce_ids)
    )


def controler_inscription(
    usage: str,
    *,
    jeton: object | None = None,
    gabarit_id: str | None = None,
    version_gabarit: int | None = None,
    sha256_gabarit: str | None = None,
    amorce_ids: Sequence[str] | None = None,
) -> None:
    """Refuse (`UsageInterdit`) une ligne `generation` sans le jeton du Générateur ou sans sa
    méta (gabarit, `amorce_ids` non vide), et une ligne d'un autre usage qui porte cette méta.

    Le client l'appelle aussi avant toute réservation : un refus ne coûte rien.
    """
    meta = (gabarit_id, version_gabarit, sha256_gabarit, amorce_ids)
    if usage != USAGE_GENERATION:
        if any(valeur is not None for valeur in meta):
            raise UsageInterdit(
                f"usage {usage!r} : gabarit et amorce_ids réservés à l'usage « generation »"
            )
        return
    if jeton is None or jeton is not jeton_generateur():
        raise UsageInterdit(
            "usage « generation » réservé au Générateur (story 9.2) : jeton de preuve absent"
        )
    if not _meta_generation_valide(*meta):
        raise UsageInterdit(
            "usage « generation » : gabarit_id, version_gabarit, sha256_gabarit et "
            "amorce_ids (liste non vide) requis"
        )


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
    gabarit_id: str | None = None
    version_gabarit: int | None = None
    sha256_gabarit: str | None = None
    amorce_ids: str | None = None
    """Identifiants des amorces, liste en JSON canonique (`generation` seulement)."""


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
            if version not in (0, 1, VERSION_SCHEMA):
                raise SlmspError(
                    f"{self.chemin} : version de schéma {version} inattendue "
                    f"(attendu {VERSION_SCHEMA})"
                )
            if version == 1:
                for requete in _MIGRATION_V2:
                    connexion.execute(requete)
            for requete in _CREATION:
                connexion.execute(requete)
            if version != VERSION_SCHEMA:
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
        jeton: object | None = None,
        gabarit_id: str | None = None,
        version_gabarit: int | None = None,
        sha256_gabarit: str | None = None,
        amorce_ids: Sequence[str] | None = None,
    ) -> str:
        """Ajoute un appel et renvoie son `appel_id` (uuid4 hexadécimal).

        Lève `UsageInterdit` si `usage` n'est pas admis par ce journal, si une ligne
        `generation` n'a pas le jeton du Générateur ou sa méta, ou si un autre usage porte
        cette méta (`controler_inscription`) ; `ValueError` pour un statut inconnu. Rien
        n'est écrit dans ces cas.
        """
        if usage not in self.usages_admis:
            raise UsageInterdit(
                f"usage {usage!r} refusé par le journal {self.chemin.name} "
                f"(admis : {', '.join(self.usages_admis)})"
            )
        controler_inscription(
            usage,
            jeton=jeton,
            gabarit_id=gabarit_id,
            version_gabarit=version_gabarit,
            sha256_gabarit=sha256_gabarit,
            amorce_ids=amorce_ids,
        )
        if statut not in STATUTS:
            raise ValueError(f"statut d'appel inconnu : {statut!r}")
        brut = bytes(reponse_brute) if reponse_brute is not None else None
        canonique = json_canonique(dict(requete))
        amorces = None if amorce_ids is None else json_canonique(list(amorce_ids)).decode("utf-8")
        appel_id = uuid.uuid4().hex
        with self._transaction() as connexion:
            connexion.execute(
                "INSERT INTO appels (appel_id, session_id, usage, modele_demande, modele_resolu, "
                "requete, sha256_requete, reponse_brute, sha256_reponse, reservation_id, statut, "
                "statut_http, horodatage, gabarit_id, version_gabarit, sha256_gabarit, "
                "amorce_ids) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                    gabarit_id,
                    version_gabarit,
                    sha256_gabarit,
                    amorces,
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

    def appels_session(self, session_id: str) -> list[LigneAppel]:
        """Lignes de la session `session_id`, dans l'ordre d'inscription."""
        return self._lignes(
            "SELECT * FROM appels WHERE session_id = ? ORDER BY rowid", (session_id,)
        )


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
