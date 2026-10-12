"""`RegistreBudget` : réservation au pire cas et arrêt au plafond (D1.6, AD-5, AD-26).

Une base SQLite unique par machine, `SLMSP_VAR_DIR/budget.sqlite`, partagée par tous les
processus et toutes les copies de travail. Chaque tentative d'appel payant réserve d'abord
son coût pire cas dans une transaction `BEGIN IMMEDIATE` ; la réservation est refusée
(`BudgetEpuise`, code 3), sans rien écrire, si dépensé + réservé + coût + marge dépasse le
plafond du sous-poste (s'il existe) ou du poste. Après l'appel, la réservation est
régularisée au coût réel (`regulariser`) ou comptée au pire cas (`compter_pire_cas`).

États d'une ligne : `reservee` (comptée au montant réservé), `regularisee` (comptée au
coût réel), `pire-cas` (comptée au montant réservé, comme dépensé). Les totaux ne portent
que sur le `campagne_id` de `budgets.toml` : changer de campagne n'efface rien.

À l'ouverture, les réservations sans lot dont le processus est mort (PID et date de
création, via psutil) passent au pire cas avec le motif `orpheline`. Une réservation liée
à un `batch_id` reste ouverte jusqu'à `collecter_lot` ou `annuler_lot`.

Le module n'offre aucune remise à zéro ni suppression de ligne. Une connexion est ouverte
par opération (WAL, `busy_timeout` 30 s).
"""

from __future__ import annotations

import math
import os
import sqlite3
from collections.abc import Callable, Iterator
from contextlib import closing, contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Final

import psutil

from slmsp.budget.config import ConfigBudgets, ConfigTarifs, charger_budgets, charger_tarifs
from slmsp.budget.tarifs import UsageTokens, cout_pire_cas, cout_reel
from slmsp.core.erreurs import BudgetEpuise, ConfigurationInvalide, SlmspError
from slmsp.core.var import BUSY_TIMEOUT_MS, dossier_var, ouvrir_sqlite

NOM_REGISTRE: Final = "budget.sqlite"
VERSION_SCHEMA: Final = 1

RESERVEE: Final = "reservee"
REGULARISEE: Final = "regularisee"
PIRE_CAS: Final = "pire-cas"

MOTIF_ORPHELINE: Final = "orpheline"
MOTIF_ECHEC: Final = "echec"
MOTIF_LOT_ANNULE: Final = "lot-annule"
MOTIF_DEPASSEMENT: Final = "depassement-reservation"

TOLERANCE_CREATION: Final = 0.01
"""Écart toléré sur la date de création d'un processus (secondes), comme `inference`."""

TOLERANCE_EUR: Final = 1e-9
"""Tolérance d'arrondi des sommes flottantes (un milliardième d'euro)."""

_CREATION = """
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campagne_id TEXT NOT NULL,
    poste TEXT NOT NULL,
    sous_poste TEXT,
    modele TEXT NOT NULL,
    mode TEXT NOT NULL,
    pid INTEGER NOT NULL,
    creation_processus REAL NOT NULL,
    batch_id TEXT,
    nb_requetes INTEGER NOT NULL,
    etat TEXT NOT NULL,
    montant_reserve_eur REAL NOT NULL,
    montant_reel_eur REAL,
    motif TEXT,
    tokens_entree INTEGER,
    tokens_sortie INTEGER,
    tokens_ecriture_cache INTEGER,
    tokens_lecture_cache INTEGER,
    cree_le TEXT NOT NULL,
    regle_le TEXT
)
"""
_INDEX_LOTS = (
    "CREATE UNIQUE INDEX IF NOT EXISTS reservations_batch_id "
    "ON reservations (batch_id) WHERE batch_id IS NOT NULL"
)
_INDEX_CAMPAGNE = (
    "CREATE INDEX IF NOT EXISTS reservations_campagne ON reservations (campagne_id, poste)"
)


@dataclass(frozen=True)
class LigneEtat:
    """Situation d'un poste (`sous_poste` nul) ou d'un sous-poste, en euros."""

    poste: str
    sous_poste: str | None
    plafond_eur: float
    depense_eur: float
    reserve_eur: float
    reste_eur: float


@dataclass(frozen=True)
class Releve:
    """Relevé du registre pour la campagne courante."""

    campagne_id: str
    marge_eur: float
    lignes: tuple[LigneEtat, ...]

    def en_dict(self, decimales: int = 6) -> dict[str, Any]:
        """Dictionnaire sérialisable, montants arrondis à `decimales` (micro-euro)."""
        lignes = []
        for ligne in self.lignes:
            donnees = asdict(ligne)
            for cle, valeur in donnees.items():
                if isinstance(valeur, float):
                    donnees[cle] = round(valeur, decimales) + 0.0  # pas de -0.0
            lignes.append(donnees)
        return {
            "campagne_id": self.campagne_id,
            "marge_eur": round(self.marge_eur, decimales),
            "lignes": lignes,
        }


@dataclass(frozen=True)
class LotOuvert:
    """Lot batch dont la réservation attend sa collecte ou son annulation."""

    batch_id: str
    campagne_id: str
    poste: str
    sous_poste: str | None
    modele: str
    nb_requetes: int
    montant_reserve_eur: float
    pid: int
    cree_le: str


def _maintenant() -> str:
    return datetime.now().astimezone().isoformat()


_creation_courante: tuple[int, float] | None = None
"""`(pid, date de création)` de ce processus, recalculé si le PID change (fork)."""


def _creation_de_ce_processus() -> float:
    global _creation_courante
    pid = os.getpid()
    if _creation_courante is None or _creation_courante[0] != pid:
        _creation_courante = (pid, psutil.Process(pid).create_time())
    return _creation_courante[1]


def _processus_vivant(pid: int, creation: float) -> bool:
    """Vrai si le processus `pid` vit encore avec la même date de création.

    Processus disparu, PID recyclé ou zombie : mort. Accès refusé (autre compte, processus
    élevé) : la mort n'est pas prouvée, le processus est tenu pour vivant.
    """
    try:
        processus = psutil.Process(pid)
        if abs(processus.create_time() - creation) > TOLERANCE_CREATION:
            return False
        if processus.status() == psutil.STATUS_ZOMBIE:
            return False
    except (psutil.NoSuchProcess, ValueError):  # ZombieProcess dérive de NoSuchProcess
        return False
    except psutil.AccessDenied:
        return True
    return True


@contextmanager
def _transaction(chemin: Path) -> Iterator[sqlite3.Connection]:
    """Connexion propre à l'opération, dans une transaction `BEGIN IMMEDIATE`."""
    connexion = ouvrir_sqlite(chemin)
    try:
        connexion.isolation_level = None
        connexion.execute("BEGIN IMMEDIATE")
        try:
            yield connexion
        except BaseException:
            if connexion.in_transaction:  # SQLite a pu annuler la transaction de lui-même
                connexion.execute("ROLLBACK")
            raise
        connexion.execute("COMMIT")
    finally:
        connexion.close()


def _verifier_version(connexion: sqlite3.Connection, chemin: Path) -> int:
    (version,) = connexion.execute("PRAGMA user_version").fetchone()
    if version not in (0, VERSION_SCHEMA):
        raise SlmspError(
            f"{chemin} : version de schéma {version} inattendue (attendu {VERSION_SCHEMA})"
        )
    return version


def _totaux(
    connexion: sqlite3.Connection, campagne_id: str, poste: str, sous_poste: str | None
) -> tuple[float, float]:
    """`(dépensé, réservé)` de la campagne pour un poste ou un sous-poste."""
    requete = (
        "SELECT "
        f"COALESCE(SUM(CASE WHEN etat != '{RESERVEE}' THEN montant_reel_eur END), 0), "
        f"COALESCE(SUM(CASE WHEN etat = '{RESERVEE}' THEN montant_reserve_eur END), 0) "
        "FROM reservations WHERE campagne_id = ? AND poste = ?"
    )
    parametres: tuple[Any, ...] = (campagne_id, poste)
    if sous_poste is not None:
        requete += " AND sous_poste = ?"
        parametres += (sous_poste,)
    depense, reserve = connexion.execute(requete, parametres).fetchone()
    return float(depense), float(reserve)


def _calculer_releve(connexion: sqlite3.Connection | None, config: ConfigBudgets) -> Releve:
    lignes = []
    for poste, definition in config.postes.items():
        niveaux: list[tuple[str | None, float]] = [(None, definition.plafond_eur)]
        niveaux += list(definition.sous_postes.items())
        for sous_poste, plafond in niveaux:
            depense, reserve = (
                _totaux(connexion, config.campagne_id, poste, sous_poste)
                if connexion is not None
                else (0.0, 0.0)
            )
            lignes.append(
                LigneEtat(poste, sous_poste, plafond, depense, reserve, plafond - depense - reserve)
            )
    return Releve(config.campagne_id, config.marge_eur, tuple(lignes))


def releve(chemin: str | Path | None = None, config: ConfigBudgets | None = None) -> Releve:
    """Relevé en lecture seule : la base n'est ni créée, ni modifiée, ni régularisée.

    Base absente (ou encore vide) : plafonds et sommes nulles.
    """
    config = config if config is not None else charger_budgets()
    chemin = Path(chemin) if chemin is not None else dossier_var() / NOM_REGISTRE
    if not chemin.is_file():
        return _calculer_releve(None, config)
    uri = f"{chemin.resolve().as_uri()}?mode=ro"
    try:
        connexion = sqlite3.connect(uri, uri=True, timeout=BUSY_TIMEOUT_MS / 1000)
        with closing(connexion):
            connexion.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
            _verifier_version(connexion, chemin)
            table = connexion.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'reservations'"
            ).fetchone()
            return _calculer_releve(connexion if table else None, config)
    except sqlite3.Error as exc:
        raise SlmspError(f"{chemin} : registre de budget illisible ({exc})") from None


class RegistreBudget:
    """Registre de budget persistant, partagé par tous les processus de la machine."""

    def __init__(
        self,
        config: ConfigBudgets | None = None,
        tarifs: ConfigTarifs | None = None,
        chemin: str | Path | None = None,
    ) -> None:
        self.config = config if config is not None else charger_budgets()
        self.tarifs = tarifs if tarifs is not None else charger_tarifs()
        self.chemin = Path(chemin) if chemin is not None else dossier_var() / NOM_REGISTRE
        self.campagne_id = self.config.campagne_id
        with _transaction(self.chemin) as connexion:
            version = _verifier_version(connexion, self.chemin)
            connexion.execute(_CREATION)
            connexion.execute(_INDEX_LOTS)
            connexion.execute(_INDEX_CAMPAGNE)
            if version == 0:
                connexion.execute(f"PRAGMA user_version = {VERSION_SCHEMA}")
            self.orphelines_regularisees = self._regulariser_orphelines(connexion)

    # --- imputation et contrôle -----------------------------------------------------------

    def imputer(self, usage: str) -> tuple[str, str | None]:
        """`(poste, sous_poste)` d'un usage déclaré dans `budgets.toml` (`juge-second`…)."""
        cible = self.config.imputations.get(usage)
        if cible is None:
            raise ConfigurationInvalide(f"usage de budget inconnu : {usage!r} (budgets.toml)")
        poste, _, sous_poste = cible.partition(".")
        return poste, sous_poste or None

    def _plafonds(self, poste: str, sous_poste: str | None) -> list[tuple[str | None, float]]:
        """Niveaux contrôlés, sous-poste d'abord : `[(sous_poste, plafond), (None, plafond)]`."""
        definition = self.config.postes.get(poste)
        if definition is None:
            raise ConfigurationInvalide(f"poste de budget inconnu : {poste!r}")
        niveaux: list[tuple[str | None, float]] = []
        if sous_poste is not None:
            if sous_poste not in definition.sous_postes:
                raise ConfigurationInvalide(f"sous-poste de budget inconnu : {poste}.{sous_poste}")
            niveaux.append((sous_poste, definition.sous_postes[sous_poste]))
        elif definition.sous_postes:
            raise ConfigurationInvalide(
                f"le poste {poste} exige un sous-poste ({', '.join(definition.sous_postes)})"
            )
        niveaux.append((None, definition.plafond_eur))
        return niveaux

    def _disponible(
        self, connexion: sqlite3.Connection, poste: str, sous_poste: str | None
    ) -> tuple[float, str]:
        """Reste disponible (marge déduite) au niveau le plus contraint, et son détail."""
        meilleur: tuple[float, str] | None = None
        for niveau, plafond in self._plafonds(poste, sous_poste):
            depense, reserve = _totaux(connexion, self.campagne_id, poste, niveau)
            reste = plafond - depense - reserve - self.config.marge_eur
            nom = poste if niveau is None else f"{poste}.{niveau}"
            detail = (
                f"{nom} : plafond {plafond:.2f} €, dépensé {depense:.4f} €, "
                f"réservé {reserve:.4f} €, marge {self.config.marge_eur:.2f} €, "
                f"reste {max(reste, 0.0):.4f} €"
            )
            if meilleur is None or reste < meilleur[0]:
                meilleur = (reste, detail)
        assert meilleur is not None
        return meilleur

    def _controler(
        self, connexion: sqlite3.Connection, poste: str, sous_poste: str | None, cout: float
    ) -> None:
        for niveau, plafond in self._plafonds(poste, sous_poste):
            depense, reserve = _totaux(connexion, self.campagne_id, poste, niveau)
            if depense + reserve + cout + self.config.marge_eur > plafond + TOLERANCE_EUR:
                nom = poste if niveau is None else f"{poste}.{niveau}"
                reste = max(plafond - depense - reserve - self.config.marge_eur, 0.0)
                raise BudgetEpuise(
                    f"budget épuisé pour {nom} (campagne {self.campagne_id}) : "
                    f"plafond {plafond:.2f} €, dépensé {depense:.4f} €, réservé {reserve:.4f} €, "
                    f"marge {self.config.marge_eur:.2f} €, reste {reste:.4f} € ; "
                    f"coût pire cas demandé {cout:.4f} €"
                )

    def _inserer(
        self,
        connexion: sqlite3.Connection,
        *,
        poste: str,
        sous_poste: str | None,
        modele: str,
        mode: str,
        montant: float,
        nb_requetes: int = 1,
        batch_id: str | None = None,
    ) -> int:
        curseur = connexion.execute(
            "INSERT INTO reservations (campagne_id, poste, sous_poste, modele, mode, pid, "
            "creation_processus, batch_id, nb_requetes, etat, montant_reserve_eur, cree_le) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                self.campagne_id,
                poste,
                sous_poste,
                modele,
                mode,
                os.getpid(),
                _creation_de_ce_processus(),
                batch_id,
                nb_requetes,
                RESERVEE,
                montant,
                _maintenant(),
            ),
        )
        assert curseur.lastrowid is not None
        return curseur.lastrowid

    # --- réservation unitaire -------------------------------------------------------------

    def reserver(
        self,
        poste: str,
        sous_poste: str | None,
        modele: str,
        mode: str,
        tokens_entree_estimes: int,
        max_tokens: int,
        *,
        avec_cache: bool = False,
    ) -> int:
        """Réserve le coût pire cas d'une tentative et renvoie l'identifiant de réservation.

        Lève `ConfigurationInvalide` (poste ou sous-poste), `TarifInconnu` (modèle, mode ou
        cache) ou `BudgetEpuise` (plafond) ; dans ces trois cas, rien n'est écrit.
        """
        self._plafonds(poste, sous_poste)
        cout = cout_pire_cas(
            self.tarifs,
            modele,
            mode,
            tokens_entree_estimes,
            max_tokens,
            self.config.majoration_entree,
            avec_cache=avec_cache,
        )
        with _transaction(self.chemin) as connexion:
            self._controler(connexion, poste, sous_poste, cout)
            return self._inserer(
                connexion,
                poste=poste,
                sous_poste=sous_poste,
                modele=modele,
                mode=mode,
                montant=cout,
            )

    def _ligne_ouverte(
        self, connexion: sqlite3.Connection, condition: str, valeur: Any, quoi: str
    ) -> sqlite3.Row:
        connexion.row_factory = sqlite3.Row
        ligne = connexion.execute(
            f"SELECT * FROM reservations WHERE {condition} = ?", (valeur,)
        ).fetchone()
        if ligne is None:
            raise SlmspError(f"{quoi} inconnue du registre de budget")
        if ligne["etat"] != RESERVEE:
            raise SlmspError(f"{quoi} déjà réglée (état {ligne['etat']})")
        return ligne

    def _regler(
        self,
        connexion: sqlite3.Connection,
        ligne: sqlite3.Row,
        usage: UsageTokens | None,
        motif: str | None,
    ) -> float:
        if usage is None:
            etat, montant = PIRE_CAS, float(ligne["montant_reserve_eur"])
            compteurs: tuple[int | None, ...] = (None, None, None, None)
        else:
            etat = REGULARISEE
            montant = cout_reel(self.tarifs, ligne["modele"], ligne["mode"], usage)
            compteurs = (usage.entree, usage.sortie, usage.ecriture_cache, usage.lecture_cache)
            if motif is None and montant > ligne["montant_reserve_eur"] + TOLERANCE_EUR:
                motif = MOTIF_DEPASSEMENT  # coût réel gardé tel quel, mais signalé
        connexion.execute(
            "UPDATE reservations SET etat = ?, montant_reel_eur = ?, motif = ?, "
            "tokens_entree = ?, tokens_sortie = ?, tokens_ecriture_cache = ?, "
            "tokens_lecture_cache = ?, regle_le = ? WHERE id = ? AND etat = ?",
            (etat, montant, motif, *compteurs, _maintenant(), ligne["id"], RESERVEE),
        )
        return montant

    def _regler_unitaire(
        self, reservation_id: int, usage: UsageTokens | None, motif: str | None
    ) -> float:
        quoi = f"réservation {reservation_id}"
        with _transaction(self.chemin) as connexion:
            ligne = self._ligne_ouverte(connexion, "id", reservation_id, quoi)
            if ligne["batch_id"] is not None:
                raise SlmspError(
                    f"{quoi} liée au lot {ligne['batch_id']} : collecter_lot ou annuler_lot"
                )
            return self._regler(connexion, ligne, usage, motif)

    def regulariser(self, reservation_id: int, usage: UsageTokens) -> float:
        """Remplace la réservation par le coût réel de `usage` et renvoie ce coût (EUR).

        Lève `SlmspError` si la réservation est inconnue ou déjà réglée, `TarifInconnu` si
        `usage` compte du cache sans tarif de cache (la réservation reste alors ouverte).
        """
        return self._regler_unitaire(reservation_id, usage, None)

    def compter_pire_cas(self, reservation_id: int) -> float:
        """Compte la réservation au pire cas, comme dépensée (échec sans `usage`)."""
        return self._regler_unitaire(reservation_id, None, MOTIF_ECHEC)

    def executer_avec_relances[T](
        self,
        appel: Callable[[], tuple[T, UsageTokens | None]],
        tentatives: int,
        poste: str,
        sous_poste: str | None,
        modele: str,
        mode: str,
        tokens_entree_estimes: int,
        max_tokens: int,
        *,
        avec_cache: bool = False,
    ) -> T:
        """Exécute `appel` jusqu'à `tentatives` fois, une réservation par tentative.

        `appel()` renvoie `(résultat, usage)` ; un `usage` nul compte la tentative au pire
        cas. Une tentative qui lève est comptée au pire cas ; une `SlmspError` (dont
        `BudgetEpuise` à la réservation) n'est jamais retentée. Après la dernière tentative,
        la dernière exception est relevée. Un retour qui n'est pas un couple, ou une
        régularisation impossible, compte la tentative au pire cas et lève sans relance.

        Les clients des SDK payants sont construits avec `max_retries=0` (D-nuit-A1-20) :
        les relances se font ici seulement, avec une réservation par tentative.
        """
        if isinstance(tentatives, bool) or not isinstance(tentatives, int) or tentatives < 1:
            raise ValueError("tentatives doit être un entier supérieur ou égal à 1")
        derniere: Exception | None = None
        for _ in range(tentatives):
            reservation_id = self.reserver(
                poste,
                sous_poste,
                modele,
                mode,
                tokens_entree_estimes,
                max_tokens,
                avec_cache=avec_cache,
            )
            try:
                retour = appel()
            except BaseException as exc:
                secondaire = self._compter_pire_cas_garde(reservation_id)
                if secondaire is not None:
                    raise exc from secondaire
                if not isinstance(exc, Exception) or isinstance(exc, SlmspError):
                    raise
                derniere = exc
                continue
            try:
                resultat, usage = retour
            except (TypeError, ValueError) as exc:
                erreur = TypeError("appel() doit renvoyer le couple (résultat, usage)")
                secondaire = self._compter_pire_cas_garde(reservation_id)
                raise erreur from (secondaire if secondaire is not None else exc)
            if usage is None:
                self.compter_pire_cas(reservation_id)
                return resultat
            try:
                self.regulariser(reservation_id, usage)
            except Exception as exc:
                secondaire = self._compter_pire_cas_garde(reservation_id)
                if secondaire is not None:
                    raise exc from secondaire
                raise
            return resultat
        assert derniere is not None
        raise derniere

    def _compter_pire_cas_garde(self, reservation_id: int) -> Exception | None:
        """`compter_pire_cas` sans masquer l'erreur en cours : renvoie son échec éventuel."""
        try:
            self.compter_pire_cas(reservation_id)
        except Exception as secondaire:
            return secondaire
        return None

    # --- lots batch -----------------------------------------------------------------------

    def _cout_requete_lot(
        self, modele: str, tokens_entree_estimes: int, max_tokens: int, avec_cache: bool
    ) -> float:
        return cout_pire_cas(
            self.tarifs,
            modele,
            "batch",
            tokens_entree_estimes,
            max_tokens,
            self.config.majoration_entree,
            avec_cache=avec_cache,
        )

    def _taille_max(
        self, connexion: sqlite3.Connection, poste: str, sous_poste: str | None, unitaire: float
    ) -> int:
        disponible, _ = self._disponible(connexion, poste, sous_poste)
        if disponible + TOLERANCE_EUR < unitaire:
            return 0
        return max(math.floor((disponible + TOLERANCE_EUR) / unitaire), 0)

    def taille_max_lot(
        self,
        poste: str,
        sous_poste: str | None,
        modele: str,
        tokens_entree_estimes: int,
        max_tokens: int,
        *,
        avec_cache: bool = False,
    ) -> int:
        """Nombre maximal de requêtes d'un lot qui tient sous le reste disponible (tarif batch)."""
        self._plafonds(poste, sous_poste)
        unitaire = self._cout_requete_lot(modele, tokens_entree_estimes, max_tokens, avec_cache)
        with closing(ouvrir_sqlite(self.chemin)) as connexion:
            return self._taille_max(connexion, poste, sous_poste, unitaire)

    def reserver_lot(
        self,
        batch_id: str,
        poste: str,
        sous_poste: str | None,
        modele: str,
        tokens_entree_estimes: int,
        max_tokens: int,
        nb_requetes: int,
        *,
        avec_cache: bool = False,
    ) -> int:
        """Réserve un lot au pire cas, au tarif batch, et renvoie le nombre de requêtes retenu.

        Le nombre retenu vaut `min(nb_requetes, taille maximale)` ; `batch_id` (choisi par
        l'appelant) est persisté avant toute soumission. Lève `BudgetEpuise` si aucune
        requête ne tient, `SlmspError` si `batch_id` est déjà connu du registre.
        """
        if not isinstance(batch_id, str) or not batch_id.strip():
            raise ValueError("batch_id doit être une chaîne non vide")
        if isinstance(nb_requetes, bool) or not isinstance(nb_requetes, int) or nb_requetes < 1:
            raise ValueError("nb_requetes doit être un entier supérieur ou égal à 1")
        self._plafonds(poste, sous_poste)
        unitaire = self._cout_requete_lot(modele, tokens_entree_estimes, max_tokens, avec_cache)
        with _transaction(self.chemin) as connexion:
            deja = connexion.execute(
                "SELECT etat FROM reservations WHERE batch_id = ?", (batch_id,)
            ).fetchone()
            if deja is not None:
                raise SlmspError(f"lot {batch_id} déjà inscrit au registre (état {deja[0]})")
            retenu = min(nb_requetes, self._taille_max(connexion, poste, sous_poste, unitaire))
            if retenu < 1:
                _, detail = self._disponible(connexion, poste, sous_poste)
                raise BudgetEpuise(
                    f"budget épuisé pour le lot {batch_id} (campagne {self.campagne_id}) : "
                    f"{detail} ; coût pire cas d'une requête {unitaire:.4f} €"
                )
            self._controler(connexion, poste, sous_poste, retenu * unitaire)
            self._inserer(
                connexion,
                poste=poste,
                sous_poste=sous_poste,
                modele=modele,
                mode="batch",
                montant=retenu * unitaire,
                nb_requetes=retenu,
                batch_id=batch_id,
            )
            return retenu

    def collecter_lot(self, batch_id: str, usage: UsageTokens) -> float:
        """Régularise le lot au coût réel de `usage` (cumul du lot) et renvoie ce coût."""
        with _transaction(self.chemin) as connexion:
            ligne = self._ligne_ouverte(connexion, "batch_id", batch_id, f"lot {batch_id}")
            return self._regler(connexion, ligne, usage, None)

    def annuler_lot(self, batch_id: str, usage: UsageTokens | None = None) -> float:
        """Règle un lot dont l'annulation est confirmée par le fournisseur.

        Avec `usage` (requêtes facturées avant l'annulation), le lot est régularisé au coût
        réel ; sans `usage`, il reste compté au pire cas (motif `lot-annule`).
        """
        with _transaction(self.chemin) as connexion:
            ligne = self._ligne_ouverte(connexion, "batch_id", batch_id, f"lot {batch_id}")
            return self._regler(connexion, ligne, usage, MOTIF_LOT_ANNULE)

    def lots_ouverts(self) -> list[LotOuvert]:
        """Lots encore réservés, toutes campagnes, à relire avant toute relance (AD-26)."""
        with closing(ouvrir_sqlite(self.chemin)) as connexion:
            lignes = connexion.execute(
                "SELECT batch_id, campagne_id, poste, sous_poste, modele, nb_requetes, "
                "montant_reserve_eur, pid, cree_le FROM reservations "
                "WHERE batch_id IS NOT NULL AND etat = ? ORDER BY id",
                (RESERVEE,),
            ).fetchall()
        return [LotOuvert(*ligne) for ligne in lignes]

    # --- relevé et orphelines -------------------------------------------------------------

    def etat(self) -> Releve:
        """Relevé de la campagne courante (plafond, dépensé, réservé, reste)."""
        with closing(ouvrir_sqlite(self.chemin)) as connexion:
            return _calculer_releve(connexion, self.config)

    def _regulariser_orphelines(self, connexion: sqlite3.Connection) -> tuple[int, ...]:
        lignes = connexion.execute(
            "SELECT id, pid, creation_processus FROM reservations "
            "WHERE etat = ? AND batch_id IS NULL",
            (RESERVEE,),
        ).fetchall()
        orphelines = tuple(
            identifiant
            for identifiant, pid, creation in lignes
            if not _processus_vivant(pid, creation)
        )
        maintenant = _maintenant()
        for identifiant in orphelines:
            connexion.execute(
                "UPDATE reservations SET etat = ?, montant_reel_eur = montant_reserve_eur, "
                "motif = ?, regle_le = ? WHERE id = ? AND etat = ?",
                (PIRE_CAS, MOTIF_ORPHELINE, maintenant, identifiant, RESERVEE),
            )
        return orphelines
