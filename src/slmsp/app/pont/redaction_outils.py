"""Pont, domaine « Outils de rédaction » (story 13.1, FR-17).

Chaque méthode rend `{"ok": true, ...}` ou lève ; le pont convertit l'exception en
`{"ok": false, "erreur": {"code", "message"}}`. Aucun réseau, aucun modèle : calcul local.

- `differences(avant: str, apres: str)` -> `{"ok": true, "identiques": bool,
  "segments": [{"type": "egal"|"ajout"|"suppression", "texte": str}, ...]}`. Différences par
  mots (voir `slmsp.app.differences`). Refus `requete-invalide` si un argument n'est pas une
  chaîne ou dépasse `TAILLE_MAX` caractères.
"""

from __future__ import annotations

from typing import Any, Final

from slmsp.app.differences import calculer, identiques
from slmsp.app.pont.conversation import reponse_erreur
from slmsp.app.pont.erreurs import NonImplementee

TAILLE_MAX: Final = 500_000


class PontRedactionOutils:
    """Délègue `differences` à `slmsp.app.differences`."""

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        if nom != "differences":
            raise NonImplementee(f"redaction_outils.{nom} : non implémentée")
        if len(args) != 2 or not all(isinstance(x, str) and len(x) <= TAILLE_MAX for x in args):
            return reponse_erreur("requete-invalide", "Les deux textes doivent être des chaînes.")
        segments = calculer(args[0], args[1])
        return {"ok": True, "identiques": identiques(segments), "segments": segments}
