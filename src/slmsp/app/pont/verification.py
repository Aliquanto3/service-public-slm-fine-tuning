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
    qu'aucun vérificateur n'est branché (câblé par l'application, story 13.6, avec
    `harness.verification.Verificateur`) ; `generation-en-cours` quand une réponse se génère
    (le Modèle embarqué n'est pas appelé en parallèle) ; `verification-en-cours` quand une
    autre vérification est déjà en cours (une à la fois).
  - Le Mode est contrôlé à l'ouverture de la requête par la passerelle : un passage en
    hors ligne forcé pendant une vérification déjà partie n'interrompt pas la requête en
    cours (délai et taille bornés), mais l'interface en ignore le résultat.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from slmsp.app.pont.conversation import reponse_erreur
from slmsp.app.pont.erreurs import NonImplementee
from slmsp.core.evenements import Evenement, vers_dict
from slmsp.harness.verification import REPONSE_MAX_CARACTERES
from slmsp.inference.mesures import contexte_mesure

SOURCES_MAX = 100
"""Nombre maximal de sources reçues ; au-delà, `requete-invalide`."""

Verificateur = Callable[[str, Sequence[Mapping[str, Any]]], Sequence[Evenement]]


def _modele_valide(valeur: Any) -> bool:
    from slmsp.app.pont.historique import MAX_MODELE

    return valeur is None or (isinstance(valeur, str) and 0 < len(valeur) <= MAX_MODELE)


class PontVerification:
    """Délègue `verifier` au vérificateur injecté (`harness.verification.Verificateur`)."""

    def __init__(
        self,
        verificateur: Verificateur | None = None,
        occupe: Callable[[], bool] | None = None,
    ) -> None:
        self._verificateur = verificateur
        self._occupe = occupe  # vrai quand une génération utilise le Modèle embarqué
        self._une_a_la_fois = threading.Lock()

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        if nom != "verifier" or self._verificateur is None:
            raise NonImplementee(f"verification.{nom} : non implémentée")
        if (
            len(args) not in (2, 3)
            or not isinstance(args[0], str)
            or not isinstance(args[1], list)
            or not all(isinstance(s, Mapping) for s in args[1])
            or len(args[0]) > REPONSE_MAX_CARACTERES
            or len(args[1]) > SOURCES_MAX
            or (len(args) == 3 and not _modele_valide(args[2]))
        ):
            return reponse_erreur("requete-invalide", "arguments invalides pour verifier")
        if self._occupe is not None and self._occupe():
            return reponse_erreur("generation-en-cours", "Une réponse est en cours.")
        if not self._une_a_la_fois.acquire(blocking=False):
            return reponse_erreur("verification-en-cours", "Une vérification est en cours.")
        try:
            # Mesure des appels de la vérification (story 17.6) : Tâche `verification`.
            with contexte_mesure(tache="verification"):
                if len(args) == 3 and args[2] is not None:
                    # Même fournisseur que la réponse vérifiée (story 17.4, amendement 6).
                    evenements = self._verificateur(args[0], args[1], modele_repondant=args[2])
                else:
                    evenements = self._verificateur(args[0], args[1])
                rendus = [vers_dict(e) for e in evenements]
        finally:
            self._une_a_la_fois.release()
        return {"ok": True, "evenements": rendus}
