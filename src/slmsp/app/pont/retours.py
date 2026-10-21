"""Pont, domaine « Retours » (story 12.11, FR-19, FR-20).

Chaque méthode rend `{"ok": true, ...}` ou un refus `{"ok": false, "erreur": {"code",
"message"}}`. Contrat :

- `noter(conversation_id, message, jugement, commentaire)` -> `{"ok": true}`. `message` est
  l'indice, dans la conversation enregistrée, d'un message de l'Assistant ; `jugement` vaut
  `"pouce_haut"` ou `"pouce_bas"` ; `commentaire` (facultatif, pouce bas seulement, 2000
  caractères au plus). La question est le message de l'Agent qui précède ; les sources sont
  celles du message noté (à défaut, celles de la conversation s'il s'agit de sa dernière réponse).
  Un nouveau Retour invalide l'aperçu d'export. Refus :
  `conversation-introuvable`, `message-invalide`, `jugement-invalide`.
- `lister()` -> `{"ok": true, "retours": [{id, cree_le, tache, pouce, commentaire}], "nombre": int}`
  (sans le texte des échanges).
- `apercu_export()` -> `{"ok": true, "nombre", "nom_fichier", "apercu", "avertissements": [str],
  "masques": {motif: nombre}}` : construit l'export anonymisé (story 12.3) sans rien écrire et le
  garde en mémoire, avec la liste des Retours qu'il contient. Refus : `aucun-retour`.
- `exporter()` -> `{"ok": true, "enregistre": bool, "nom": str | null}` : ouvre « Enregistrer
  sous » (proposition `retours-assistant-AAAA-MM-JJ.json`) puis écrit l'aperçu validé, sans le
  recalculer. Annulation du dialogue : `enregistre: false`. Refus : `apercu-requis`,
  `apercu-perime` (les Retours ont changé depuis l'aperçu : nouveau Retour, historique effacé),
  `dialogue-indisponible`, `fichier-existant` (jamais d'écrasement : la confirmation du dialogue
  système n'est pas garantie), `ecriture-impossible`. Aucune Requête sortante.
"""

from __future__ import annotations

import dataclasses
import re
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from slmsp.app.export_retours import Export, apercu, construire_export, ecrire
from slmsp.app.pont.conversation import reponse_erreur
from slmsp.app.pont.erreurs import NonImplementee
from slmsp.app.pont.historique import MAX_MODELE, identifiant_valide
from slmsp.core.erreurs import SlmspError

if TYPE_CHECKING:
    from slmsp.app.stockage import Stockage

METHODES: Final = frozenset({"noter", "lister", "apercu_export", "exporter"})
JUGEMENTS: Final = {"pouce_haut": "haut", "pouce_bas": "bas"}
MAX_COMMENTAIRE: Final = 2000
MOTIF_MODELE: Final = re.compile(r"(local|externe):\S+")
"""`modele_repondant` admis (story 17.4) ; toute autre valeur est ignorée."""
# Port du dialogue « Enregistrer sous » : reçoit le nom proposé, rend le chemin choisi ou None.
ChoisirFichier = Callable[[str], str | None]


def modele_repondant_valide(valeur: Any) -> str | None:
    """`local:<…>` ou `externe:<…>` (sans espace, `MAX_MODELE` caractères au plus), sinon `None`."""
    if isinstance(valeur, str) and len(valeur) <= MAX_MODELE and MOTIF_MODELE.fullmatch(valeur):
        return valeur
    return None


class PontRetours:
    """Retours (pouces) et export anonymisé, au-dessus de `Stockage`."""

    def __init__(
        self, stockage: Stockage | None = None, choisir_fichier: ChoisirFichier | None = None
    ) -> None:
        self._stockage = stockage
        self._choisir = choisir_fichier
        self._export: Export | None = None
        self._ids_export: list[str] = []  # Retours contenus dans l'aperçu

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        if nom not in METHODES:
            raise NonImplementee(f"retours.{nom} : méthode inconnue")
        if self._stockage is None:
            return reponse_erreur("stockage-indisponible", "Les retours ne sont pas disponibles.")
        return getattr(self, nom)(*args)

    def noter(
        self, conversation_id: str, message: int, jugement: str, commentaire: str | None = None
    ) -> dict[str, Any]:
        assert self._stockage is not None
        if jugement not in JUGEMENTS:
            return reponse_erreur("jugement-invalide", "Jugement inconnu.")
        c = (
            self._stockage.lire_conversation(conversation_id)
            if identifiant_valide(conversation_id)
            else None
        )
        if c is None:
            return reponse_erreur("conversation-introuvable", "Cette conversation n'existe plus.")
        messages = c["messages"]
        if (
            not isinstance(message, int)
            or isinstance(message, bool)
            or not 0 <= message < len(messages)
            or messages[message].get("role") != "assistant"
        ):
            return reponse_erreur("message-invalide", "Cette réponse est introuvable.")
        question = next(
            (m["content"] for m in reversed(messages[:message]) if m.get("role") == "user"), ""
        )
        note = messages[message]
        sources = note.get("sources")
        if not isinstance(sources, list):
            dernier = max(i for i, m in enumerate(messages) if m.get("role") == "assistant")
            sources = c["sources"] if message == dernier else []
        texte = commentaire.strip()[:MAX_COMMENTAIRE] if isinstance(commentaire, str) else ""
        pouce = JUGEMENTS[jugement]
        self._stockage.enregistrer_retour(
            tache=c["tache"],
            question=question,
            reponse=note["content"],
            sources=sources,
            pouce=pouce,  # type: ignore[arg-type]
            commentaire=texte if pouce == "bas" and texte else None,
            modele_repondant=modele_repondant_valide(note.get("modele_repondant")),
        )
        self._export = None  # l'aperçu relu ne contient pas ce Retour
        return {"ok": True}

    def lister(self) -> dict[str, Any]:
        assert self._stockage is not None
        retours = [
            {k: r[k] for k in ("id", "cree_le", "tache", "pouce", "commentaire")}
            for r in self._stockage.lister_retours()
        ]
        return {"ok": True, "retours": retours, "nombre": len(retours)}

    def _ids_retours(self) -> list[str]:
        assert self._stockage is not None
        return [r["id"] for r in self._stockage.lister_retours()]

    def apercu_export(self) -> dict[str, Any]:
        ids = self._ids_retours()
        nombre = len(ids)
        if nombre == 0:
            self._export = None
            return reponse_erreur("aucun-retour", "Vous n'avez encore donné aucun retour.")
        assert self._stockage is not None
        export = construire_export(self._stockage)
        self._export = export
        self._ids_export = ids
        return {
            "ok": True,
            "nombre": nombre,
            "nom_fichier": export.nom_fichier,
            "apercu": apercu(export),
            "avertissements": list(export.avertissements),
            "masques": dict(export.comptes),
        }

    def exporter(self) -> dict[str, Any]:
        export = self._export
        if export is None:
            return reponse_erreur("apercu-requis", "Relisez l'aperçu avant d'enregistrer.")
        if self._ids_retours() != self._ids_export:
            self._export = None
            return reponse_erreur("apercu-perime", "Vos retours ont changé : relisez l'aperçu.")
        if self._choisir is None:
            return reponse_erreur("dialogue-indisponible", "Le choix du fichier est indisponible.")
        choisi = self._choisir(export.nom_fichier)
        if not choisi:
            return {"ok": True, "enregistre": False, "nom": None}
        chemin = Path(choisi)
        if chemin.exists():
            return reponse_erreur(
                "fichier-existant", "Un fichier porte déjà ce nom. Choisissez un autre nom."
            )
        try:
            ecrire(
                dataclasses.replace(export, nom_fichier=chemin.name),
                chemin.parent,
                confirme=True,
            )
        except (OSError, SlmspError):
            return reponse_erreur("ecriture-impossible", "Le fichier n'a pas pu être enregistré.")
        return {"ok": True, "enregistre": True, "nom": chemin.name}
