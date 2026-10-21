"""Pont, domaine « Modèles » (story 17.5b) : comparatif des modèles, en lecture seule.

- `comparatif_modeles()` -> `{"ok": true, "comparatif": <contenu de comparatif-modeles.json>}`.
  Le fichier est embarqué dans l'interface (`ui/donnees/`, produit par `slmsp compare
  fiche-app`) ; aucun réseau. Absent, illisible ou de schéma inattendu : refus
  `comparatif-indisponible` avec un message court.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

from slmsp.app.pont.conversation import reponse_erreur
from slmsp.app.pont.erreurs import NonImplementee

METHODES: Final = frozenset({"comparatif_modeles"})
CODE_INDISPONIBLE: Final = "comparatif-indisponible"
SCHEMA_ATTENDU: Final = 1
FICHIER: Final = Path(__file__).resolve().parents[1] / "ui" / "donnees" / "comparatif-modeles.json"


class PontModeles:
    """Lit le comparatif embarqué ; `fichier` permet de le remplacer dans les tests."""

    def __init__(self, fichier: Path | None = None) -> None:
        self._fichier = fichier or FICHIER

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        if nom not in METHODES:
            raise NonImplementee(f"modeles.{nom} : méthode inconnue")
        return getattr(self, nom)(*args)

    def comparatif_modeles(self) -> dict[str, Any]:
        try:
            donnees = json.loads(self._fichier.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return reponse_erreur(CODE_INDISPONIBLE, "Le comparatif des modèles est absent.")
        except (OSError, ValueError):
            return reponse_erreur(CODE_INDISPONIBLE, "Le comparatif des modèles est illisible.")
        if (
            not isinstance(donnees, dict)
            or donnees.get("schema_version") != SCHEMA_ATTENDU
            or not isinstance(donnees.get("modeles"), list)
        ):
            return reponse_erreur(CODE_INDISPONIBLE, "Le comparatif des modèles n'est pas lisible.")
        return {"ok": True, "comparatif": donnees}
