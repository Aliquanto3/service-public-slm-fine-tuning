"""Pont, domaine « Outils de rédaction » (story 13.1, FR-17).

Chaque méthode rend `{"ok": true, ...}` ou lève ; le pont convertit l'exception en
`{"ok": false, "erreur": {"code", "message"}}`. Aucun réseau, aucun modèle : calcul local.

- `differences(avant: str, apres: str)` -> `{"ok": true, "identiques": bool,
  "segments": [{"type": "egal"|"ajout"|"suppression", "texte": str}, ...]}`. Différences par
  mots (voir `slmsp.app.differences`). Refus `requete-invalide` si un argument n'est pas une
  chaîne ou dépasse `TAILLE_MAX` caractères.
- `emplacements(texte: str, champs_non_fournis: list[str])` -> `{"ok": true, "segments":
  [{"type": "texte"|"emplacement", "texte": str}, ...], "champs_en_valeur": [str, ...]}` (story
  13.3). `champs_non_fournis` : parmi `objet`, `type_courrier`, `elements_connus` ;
  seul `objet` a une ligne d'intitulé contrôlable. `champs_en_valeur` liste ceux dont la ligne
  porte une valeur au lieu d'un emplacement.
  Refus `requete-invalide` si les arguments ont un autre type.
"""

from __future__ import annotations

from typing import Any, Final

from slmsp.app.differences import calculer, identiques
from slmsp.app.pont.conversation import reponse_erreur
from slmsp.app.pont.erreurs import NonImplementee
from slmsp.harness.emplacements import champ_rendu_par_une_valeur, segmenter

TAILLE_MAX: Final = 500_000
INTITULES: Final = {"objet": "Objet"}
"""Champ non fourni -> intitulé de la ligne du courrier à contrôler."""


class PontRedactionOutils:
    """Délègue `differences` à `slmsp.app.differences`, `emplacements` à `harness.emplacements`."""

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        if nom == "emplacements":
            return self._emplacements(*args)
        if nom != "differences":
            raise NonImplementee(f"redaction_outils.{nom} : non implémentée")
        if len(args) != 2 or not all(isinstance(x, str) and len(x) <= TAILLE_MAX for x in args):
            return reponse_erreur("requete-invalide", "Les deux textes doivent être des chaînes.")
        segments = calculer(args[0], args[1])
        return {"ok": True, "identiques": identiques(segments), "segments": segments}

    @staticmethod
    def _emplacements(*args: Any) -> dict[str, Any]:
        if (
            len(args) != 2
            or not isinstance(args[0], str)
            or len(args[0]) > TAILLE_MAX
            or not isinstance(args[1], list)
            or not all(isinstance(c, str) for c in args[1])
        ):
            return reponse_erreur(
                "requete-invalide", "Un texte et la liste des champs non fournis sont attendus."
            )
        texte, absents = args
        en_valeur = [
            c for c in absents if c in INTITULES and champ_rendu_par_une_valeur(texte, INTITULES[c])
        ]
        return {"ok": True, "segments": segmenter(texte), "champs_en_valeur": en_valeur}
