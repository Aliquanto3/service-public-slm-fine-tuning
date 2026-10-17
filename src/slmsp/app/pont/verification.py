"""Pont, domaine « Vérification en ligne (FR-12) » (contrat posé par la story 13.5).

Contrat JSON (le pont convertit toute exception en `{"ok": false, "erreur": {...}}`) :

- `verification.verifier(reponse: str, sources: list[dict])` ->
  `{"ok": true, "evenements": [<verification>, <sources>?]}`.
  - `reponse` : texte de la réponse Question affichée ; `sources` : la liste `sources` de
    l'évènement `Sources` de cette réponse (format `core.evenements.vers_dict`).
  - Ces deux valeurs restent sur le poste : elles servent à choisir l'URL déjà citée et à
    la comparaison locale. La seule Requête sortante est un GET de cette URL.
  - `evenements` : un évènement `verification` (url, titre, date_consultation, verdict
    `concordant`/`difference`/`indisponible`, phrase, extrait), puis, si la page a été
    lue, un évènement `sources` portant la page (`origine = "verification"`).
  - Refus : `requete-invalide` (arguments du mauvais type) ; `non-implementee` tant
    qu'aucun vérificateur n'est branché (le câblage dans `Pont` revient à la story 13.6,
    avec `harness.verification.Verificateur`).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from slmsp.app.pont.conversation import reponse_erreur
from slmsp.app.pont.erreurs import NonImplementee
from slmsp.core.evenements import Evenement, vers_dict

Verificateur = Callable[[str, Sequence[Mapping[str, Any]]], Sequence[Evenement]]


class PontVerification:
    """Délègue `verifier` au vérificateur injecté (`harness.verification.Verificateur`)."""

    def __init__(self, verificateur: Verificateur | None = None) -> None:
        self._verificateur = verificateur

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        if nom != "verifier" or self._verificateur is None:
            raise NonImplementee(f"verification.{nom} : non implémentée")
        if (
            len(args) != 2
            or not isinstance(args[0], str)
            or not isinstance(args[1], list)
            or not all(isinstance(s, Mapping) for s in args[1])
        ):
            return reponse_erreur("requete-invalide", "arguments invalides pour verifier")
        evenements = self._verificateur(args[0], args[1])
        return {"ok": True, "evenements": [vers_dict(e) for e in evenements]}
