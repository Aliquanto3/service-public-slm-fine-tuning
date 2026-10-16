"""Stockage local de l'application (AD-23, story 12.2) : un seul fichier SQLite, dans le profil.

`%LOCALAPPDATA%\\AssistantSP\\assistant.sqlite` (WAL, `user_version`) porte les conversations,
les Retours, les réglages et le journal des Requêtes sortantes de l'application. Ce module
est le seul propriétaire de cette base : aucune autre story ne l'ouvre.

Suppression (FR-4, UX-DR17) : la ligne est effacée immédiatement de la base ; son contenu
reste seulement en mémoire du processus, 5 secondes, pour `annuler_suppression`. Il est oublié
à l'échéance par un minuteur (thread démon) et, par sécurité, à chaque accès au stockage.
Rien n'est conservé sur disque.
"""

from __future__ import annotations

import json
import os
import threading
import time
import uuid
from collections.abc import Callable, Iterator
from contextlib import closing, contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Final, Literal

from slmsp.core.erreurs import SlmspError
from slmsp.core.schemas.journal_requetes import EntreeJournalRequetes
from slmsp.core.var import ouvrir_sqlite

NOM_BASE: Final = "assistant.sqlite"
VERSION_SCHEMA: Final = 1
DELAI_ANNULATION: Final = 5.0
"""Secondes pendant lesquelles une conversation supprimée peut être restaurée (UX-DR17)."""
RETENTION_JOURNAL: Final = timedelta(days=30)
LONGUEUR_TITRE: Final = 60

REGLAGES_DEFAUT: Final[dict[str, Any]] = {
    "hors_ligne_force": False,
    "taille_texte": "normale",
    "fenetre": None,
    "plus_deplie": False,
}
"""Clés de réglage admises et leur valeur par défaut (valeurs stockées en JSON)."""

_CREATION = """
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    tache TEXT NOT NULL,
    titre TEXT NOT NULL,
    cree_le TEXT NOT NULL,
    modifie_le TEXT NOT NULL,
    messages TEXT NOT NULL,
    sources TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS retours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cree_le TEXT NOT NULL,
    tache TEXT NOT NULL,
    question TEXT NOT NULL,
    reponse TEXT NOT NULL,
    sources TEXT NOT NULL,
    pouce TEXT NOT NULL,
    commentaire TEXT
);
CREATE TABLE IF NOT EXISTS reglages (cle TEXT PRIMARY KEY, valeur TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS journal_requetes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    horodatage TEXT NOT NULL,
    profil TEXT NOT NULL,
    hote TEXT NOT NULL,
    methode TEXT NOT NULL,
    outil TEXT,
    termes TEXT,
    statut TEXT NOT NULL,
    mode TEXT
);
"""
_COLONNES_JOURNAL: Final = (
    "horodatage",
    "profil",
    "hote",
    "methode",
    "outil",
    "termes",
    "statut",
    "mode",
)


def dossier_donnees() -> Path:
    """`%LOCALAPPDATA%\\AssistantSP` (non créé ici)."""
    local = os.environ.get("LOCALAPPDATA", "").strip()
    base = Path(local) if local else Path.home() / "AppData" / "Local"
    return base / "AssistantSP"


def _maintenant() -> datetime:
    return datetime.now(UTC)


def _iso(instant: datetime) -> str:
    return instant.astimezone(UTC).isoformat()


class Stockage:
    """Conversations, Retours et réglages de l'application."""

    def __init__(
        self,
        chemin: str | Path | None = None,
        *,
        horloge: Callable[[], datetime] = _maintenant,
        monotone: Callable[[], float] = time.monotonic,
    ) -> None:
        self.chemin = Path(chemin) if chemin is not None else dossier_donnees() / NOM_BASE
        self._horloge = horloge
        self._monotone = monotone
        self._verrou = threading.Lock()
        self._supprimees: dict[str, tuple[float, dict[str, Any]]] = {}
        self._minuteurs: set[threading.Timer] = set()
        with self._connexion() as connexion:
            (version,) = connexion.execute("PRAGMA user_version").fetchone()
            if version not in (0, VERSION_SCHEMA):
                raise SlmspError(
                    f"{self.chemin} : version de schéma {version} inattendue "
                    f"(attendu {VERSION_SCHEMA}) ; la base n'a pas été modifiée"
                )
            connexion.executescript(_CREATION)
            if version == 0:
                connexion.execute(f"PRAGMA user_version = {VERSION_SCHEMA}")
        JournalApplication(self).purger()

    @contextmanager
    def _connexion(self) -> Iterator[Any]:
        with closing(ouvrir_sqlite(self.chemin)) as connexion, connexion:
            connexion.execute("PRAGMA secure_delete = ON")  # FR-4 : pages effacées, pas libérées
            yield connexion

    # -- conversations -------------------------------------------------------------------

    def enregistrer_conversation(
        self,
        *,
        tache: str,
        messages: list[dict[str, Any]],
        sources: list[dict[str, Any]] | None = None,
        identifiant: str | None = None,
        titre: str | None = None,
    ) -> str:
        """Crée la conversation, ou la remplace si `identifiant` existe ; renvoie son id.

        Le titre automatique est le début du premier message de l'Agent.
        """
        maintenant = _iso(self._horloge())
        identifiant = identifiant or uuid.uuid4().hex
        titre = titre or self._titre_automatique(messages)
        with self._connexion() as connexion:
            connexion.execute(
                "INSERT INTO conversations (id, tache, titre, cree_le, modifie_le, messages,"
                " sources) VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET"
                " tache = excluded.tache, titre = excluded.titre,"
                " modifie_le = excluded.modifie_le, messages = excluded.messages,"
                " sources = excluded.sources",
                (
                    identifiant,
                    tache,
                    titre,
                    maintenant,
                    maintenant,
                    json.dumps(messages, ensure_ascii=False),
                    json.dumps(sources or [], ensure_ascii=False),
                ),
            )
        return identifiant

    @staticmethod
    def _titre_automatique(messages: list[dict[str, Any]]) -> str:
        for message in messages:
            contenu = message.get("content")
            if message.get("role") == "user" and isinstance(contenu, str) and contenu.strip():
                return " ".join(contenu.split())[:LONGUEUR_TITRE]
        return "Sans titre"

    def lire_conversation(self, identifiant: str) -> dict[str, Any] | None:
        self._oublier_expirees()
        with self._connexion() as connexion:
            return self._lire(connexion, identifiant)

    @staticmethod
    def _lire(connexion: Any, identifiant: str) -> dict[str, Any] | None:
        ligne = connexion.execute(
            "SELECT id, tache, titre, cree_le, modifie_le, messages, sources"
            " FROM conversations WHERE id = ?",
            (identifiant,),
        ).fetchone()
        if ligne is None:
            return None
        cles = ("id", "tache", "titre", "cree_le", "modifie_le", "messages", "sources")
        valeurs = dict(zip(cles, ligne, strict=True))
        valeurs["messages"] = json.loads(valeurs["messages"])
        valeurs["sources"] = json.loads(valeurs["sources"])
        return valeurs

    def lister_conversations(self) -> list[dict[str, Any]]:
        """Conversations de la plus récente à la plus ancienne, sans les messages."""
        self._oublier_expirees()
        with self._connexion() as connexion:
            lignes = connexion.execute(
                "SELECT id, tache, titre, cree_le, modifie_le FROM conversations"
                " ORDER BY modifie_le DESC, rowid DESC"
            ).fetchall()
        cles = ("id", "tache", "titre", "cree_le", "modifie_le")
        return [dict(zip(cles, ligne, strict=True)) for ligne in lignes]

    def supprimer_conversation(self, identifiant: str) -> bool:
        """Efface la ligne tout de suite ; `annuler_suppression` la restaure sous 5 s."""
        with self._connexion() as connexion:
            connexion.execute("BEGIN IMMEDIATE")  # lecture et suppression d'un seul tenant
            conversation = self._lire(connexion, identifiant)
            if conversation is None:
                return False
            connexion.execute("DELETE FROM conversations WHERE id = ?", (identifiant,))
        with self._verrou:
            self._purger_annulations()
            self._supprimees[identifiant] = (self._monotone() + DELAI_ANNULATION, conversation)
            minuteur = threading.Timer(DELAI_ANNULATION, self._oublier_expirees)
            minuteur.daemon = True
            self._minuteurs.add(minuteur)
            minuteur.start()
        return True

    def annuler_suppression(self, identifiant: str) -> bool:
        """Restaure la conversation si moins de 5 s se sont écoulées ; sinon `False`.

        Si une conversation du même identifiant a été réenregistrée entre-temps, elle est
        conservée telle quelle (rien n'est écrasé) et le résultat est `False`.
        """
        with self._verrou:
            self._purger_annulations()
            entree = self._supprimees.pop(identifiant, None)
        if entree is None:
            return False
        c = entree[1]
        with self._connexion() as connexion:
            curseur = connexion.execute(
                "INSERT INTO conversations (id, tache, titre, cree_le, modifie_le,"
                " messages, sources) VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO NOTHING",
                (
                    c["id"],
                    c["tache"],
                    c["titre"],
                    c["cree_le"],
                    c["modifie_le"],
                    json.dumps(c["messages"], ensure_ascii=False),
                    json.dumps(c["sources"], ensure_ascii=False),
                ),
            )
            return curseur.rowcount == 1

    def _oublier_expirees(self) -> None:
        with self._verrou:
            self._purger_annulations()

    def _purger_annulations(self) -> None:
        """Oublie les contenus échus (appelé verrou pris)."""
        maintenant = self._monotone()
        for cle in [k for k, (limite, _) in self._supprimees.items() if limite <= maintenant]:
            del self._supprimees[cle]
        self._minuteurs = {m for m in self._minuteurs if m.is_alive()}

    # -- Retours -------------------------------------------------------------------------

    def enregistrer_retour(
        self,
        *,
        tache: str,
        question: str,
        reponse: str,
        sources: list[dict[str, Any]],
        pouce: Literal["haut", "bas"],
        commentaire: str | None = None,
    ) -> int:
        if pouce not in ("haut", "bas"):
            raise ValueError("pouce doit valoir 'haut' ou 'bas'")
        with self._connexion() as connexion:
            curseur = connexion.execute(
                "INSERT INTO retours (cree_le, tache, question, reponse, sources, pouce,"
                " commentaire) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    _iso(self._horloge()),
                    tache,
                    question,
                    reponse,
                    json.dumps(sources, ensure_ascii=False),
                    pouce,
                    commentaire,
                ),
            )
            return int(curseur.lastrowid or 0)

    def lister_retours(self) -> list[dict[str, Any]]:
        cles = ("id", "cree_le", "tache", "question", "reponse", "sources", "pouce", "commentaire")
        with self._connexion() as connexion:
            lignes = connexion.execute(
                "SELECT id, cree_le, tache, question, reponse, sources, pouce, commentaire"
                " FROM retours ORDER BY id"
            ).fetchall()
        retours = [dict(zip(cles, ligne, strict=True)) for ligne in lignes]
        for retour in retours:
            retour["sources"] = json.loads(retour["sources"])
        return retours

    # -- réglages ------------------------------------------------------------------------

    def lire_reglage(self, cle: str) -> Any:
        """Valeur enregistrée, sinon la valeur par défaut. Clé inconnue : `KeyError`."""
        defaut = REGLAGES_DEFAUT[cle]
        with self._connexion() as connexion:
            ligne = connexion.execute(
                "SELECT valeur FROM reglages WHERE cle = ?", (cle,)
            ).fetchone()
        return defaut if ligne is None else json.loads(ligne[0])

    def ecrire_reglage(self, cle: str, valeur: Any) -> None:
        if cle not in REGLAGES_DEFAUT:
            raise KeyError(f"réglage inconnu : {cle}")
        with self._connexion() as connexion:
            connexion.execute(
                "INSERT INTO reglages (cle, valeur) VALUES (?, ?)"
                " ON CONFLICT(cle) DO UPDATE SET valeur = excluded.valeur",
                (cle, json.dumps(valeur)),
            )

    # -- effacement ----------------------------------------------------------------------

    def effacer_historique(self) -> None:
        """Supprime conversations et Retours (réglages et journal conservés), puis `VACUUM`.

        La confirmation (UX-DR18) est demandée par l'interface avant cet appel.
        """
        with self._verrou:
            self._supprimees.clear()
            for minuteur in self._minuteurs:
                minuteur.cancel()
            self._minuteurs.clear()
        with self._connexion() as connexion:
            connexion.execute("DELETE FROM conversations")
            connexion.execute("DELETE FROM retours")
        with closing(ouvrir_sqlite(self.chemin)) as connexion:
            connexion.execute("VACUUM")


class JournalApplication:
    """Port `JournalRequetes` de l'application, dans la base du stockage (purge à 30 jours)."""

    def __init__(self, stockage: Stockage) -> None:
        self._stockage = stockage

    def purger(self) -> int:
        """Supprime les entrées de plus de 30 jours glissants ; renvoie leur nombre."""
        limite = _iso(self._stockage._horloge() - RETENTION_JOURNAL)
        with self._stockage._connexion() as connexion:
            return connexion.execute(
                "DELETE FROM journal_requetes WHERE horodatage < ?", (limite,)
            ).rowcount

    def inscrire(self, entree: EntreeJournalRequetes) -> None:
        valeurs = (
            _iso(entree.horodatage),
            entree.profil,
            entree.hote,
            entree.methode,
            entree.outil,
            entree.termes,
            entree.statut,
            entree.mode,
        )
        with self._stockage._connexion() as connexion:
            connexion.execute(
                "INSERT INTO journal_requetes (horodatage, profil, hote, methode, outil,"
                " termes, statut, mode) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                valeurs,
            )
        self.purger()

    def lister(self, limite: int | None = None) -> list[EntreeJournalRequetes]:
        """Entrées du plus récent au plus ancien."""
        requete = (
            "SELECT horodatage, profil, hote, methode, outil, termes, statut, mode"
            " FROM journal_requetes ORDER BY id DESC"
        )
        parametres: tuple[Any, ...] = ()
        if limite is not None:
            if limite < 0:
                raise ValueError("limite doit être positive ou nulle")
            requete += " LIMIT ?"
            parametres = (limite,)
        with self._stockage._connexion() as connexion:
            lignes = connexion.execute(requete, parametres).fetchall()
        return [
            EntreeJournalRequetes(
                **dict(zip(_COLONNES_JOURNAL, ligne, strict=True))
                | {"horodatage": datetime.fromisoformat(ligne[0])}
            )
            for ligne in lignes
        ]

    def effacer(self) -> None:
        """« Effacer le journal » : vide la table."""
        with self._stockage._connexion() as connexion:
            connexion.execute("DELETE FROM journal_requetes")
