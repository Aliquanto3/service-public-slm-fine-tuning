"""Pont, domaine « Historique » (story 12.11, FR-4).

Chaque méthode rend `{"ok": true, ...}` ou un refus `{"ok": false, "erreur": {"code",
"message"}}` (le texte des conversations n'entre jamais dans un message d'erreur). Contrat :

- `lister()` -> `{"ok": true, "conversations": [{id, titre, tache, date}]}` : de la plus récente à
  la plus ancienne ; `date` est l'instant ISO 8601 (UTC) de la dernière modification, l'interface
  groupe par jour local.
- `ouvrir(id)` -> `{"ok": true, "conversation": {id, titre, tache, messages, sources}}`.
  Refus : `conversation-introuvable`.
- `enregistrer(tache, messages, sources, id | null)` -> `{"ok": true, "id": str}` : crée la
  conversation au premier échange, la remplace aux suivants. `messages` : liste de
  `{role: "user"|"assistant", content: str}`. Un `id` inconnu (supprimée entre-temps) crée une
  nouvelle conversation. Refus : `conversation-invalide`.
- `supprimer(id)` -> `{"ok": true, "supprimee": bool}` : sans confirmation, effacée tout de suite.
- `annuler_suppression(id)` -> `{"ok": true, "restauree": bool}` : possible pendant 5 s.

L'effacement de tout l'historique reste `reglages.effacer_historique` (story 12.10).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from slmsp.app.pont.conversation import reponse_erreur
from slmsp.app.pont.erreurs import NonImplementee

if TYPE_CHECKING:
    from slmsp.app.stockage import Stockage

METHODES: Final = frozenset({"lister", "ouvrir", "enregistrer", "supprimer", "annuler_suppression"})
ROLES: Final = frozenset({"user", "assistant"})
MAX_MESSAGES: Final = 400
MAX_CONTENU: Final = 500_000
MAX_SOURCES: Final = 200
CODE_INTROUVABLE: Final = "conversation-introuvable"
CODE_INVALIDE: Final = "conversation-invalide"
CODE_INDISPONIBLE: Final = "stockage-indisponible"


def _identifiant_valide(valeur: object) -> bool:
    return isinstance(valeur, str) and 0 < len(valeur) <= 64 and valeur.isalnum()


def _messages_valides(messages: object) -> bool:
    return (
        isinstance(messages, list)
        and 0 < len(messages) <= MAX_MESSAGES
        and all(
            isinstance(m, dict)
            and m.get("role") in ROLES
            and isinstance(m.get("content"), str)
            and len(m["content"]) <= MAX_CONTENU
            for m in messages
        )
    )


class PontHistorique:
    """Historique des conversations, au-dessus de `Stockage` (seul propriétaire de la base)."""

    def __init__(self, stockage: Stockage | None = None) -> None:
        self._stockage = stockage

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        if nom not in METHODES:
            raise NonImplementee(f"historique.{nom} : méthode inconnue")
        if self._stockage is None:
            return reponse_erreur(CODE_INDISPONIBLE, "L'historique n'est pas disponible.")
        return getattr(self, nom)(*args)

    def lister(self) -> dict[str, Any]:
        assert self._stockage is not None
        return {
            "ok": True,
            "conversations": [
                {"id": c["id"], "titre": c["titre"], "tache": c["tache"], "date": c["modifie_le"]}
                for c in self._stockage.lister_conversations()
            ],
        }

    def ouvrir(self, identifiant: str) -> dict[str, Any]:
        assert self._stockage is not None
        c = self._stockage.lire_conversation(identifiant) if isinstance(identifiant, str) else None
        if c is None:
            return reponse_erreur(CODE_INTROUVABLE, "Cette conversation n'existe plus.")
        cles = ("id", "titre", "tache", "messages", "sources")
        return {"ok": True, "conversation": {k: c[k] for k in cles}}

    def enregistrer(
        self, tache: str, messages: list[Any], sources: list[Any] | None = None, id: Any = None
    ) -> dict[str, Any]:
        assert self._stockage is not None
        sources = [] if sources is None else sources
        if (
            not isinstance(tache, str)
            or not 0 < len(tache) <= 16
            or not _messages_valides(messages)
            or not isinstance(sources, list)
            or len(sources) > MAX_SOURCES
            or not all(isinstance(s, dict) for s in sources)
            or (id is not None and not _identifiant_valide(id))
        ):
            return reponse_erreur(CODE_INVALIDE, "Conversation invalide.")
        existant = id if id is not None and self._stockage.lire_conversation(id) else None
        nouveau = self._stockage.enregistrer_conversation(
            tache=tache, messages=messages, sources=sources, identifiant=existant
        )
        return {"ok": True, "id": nouveau}

    def supprimer(self, identifiant: str) -> dict[str, Any]:
        assert self._stockage is not None
        faite = isinstance(identifiant, str) and self._stockage.supprimer_conversation(identifiant)
        return {"ok": True, "supprimee": bool(faite)}

    def annuler_suppression(self, identifiant: str) -> dict[str, Any]:
        assert self._stockage is not None
        faite = isinstance(identifiant, str) and self._stockage.annuler_suppression(identifiant)
        return {"ok": True, "restauree": bool(faite)}
