"""Pont, domaine « Observabilité » (story 17.6) : mesures des appels, plafonds, export CSV.

- `synthese()` -> `{ok, synthese}` : totaux du jour et du mois (UTC) par modèle et par
  fournisseur, consommation des plafonds, derniers appels (aucun contenu) ;
- `methode()` -> `{ok, methode}` : hypothèses et sources des estimations ;
- `reglages()` -> `{ok, plafonds: [{hote, libelle, plafond_eur}], puissance_cpu_w, defaut}` ;
- `ecrire_plafond(hote, euros)` (0 = fournisseur désactivé), `ecrire_puissance(watts)` : pris
  en compte dès l'appel suivant ;
- `exporter_csv()` -> `{ok, enregistre, nom}` : mesures en CSV (cellules protégées contre les
  formules, aucun champ de contenu).

`details(echange)` (appelé par la conversation) rend la ligne « Détails » d'une réponse.
"""

from __future__ import annotations

import logging
import math
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from slmsp.app.observabilite import (
    PLAFOND_DEFAUT,
    PLAFOND_MAX,
    PUISSANCE_MAX_W,
    PUISSANCE_MIN_W,
    details_echange,
    exporter_csv,
    lire_plafonds,
    methode,
    synthese,
)
from slmsp.app.pont.conversation import reponse_erreur
from slmsp.app.pont.erreurs import NonImplementee

if TYPE_CHECKING:
    from slmsp.app.stockage import Stockage

LOGGER: Final = logging.getLogger("slmsp.app.pont.observabilite")
METHODES: Final = frozenset(
    {"synthese", "methode", "reglages", "ecrire_plafond", "ecrire_puissance", "exporter_csv"}
)
CODE_INVALIDE: Final = "reglage-invalide"
NOM_EXPORT: Final = "mesures-appels.csv"


def _nombre(valeur: Any) -> float | None:
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
        return None
    return float(valeur) if math.isfinite(valeur) else None


class PontObservabilite:
    def __init__(
        self,
        stockage: Stockage | None,
        observabilite: Any = None,
        choisir_fichier: Callable[[str], str | None] | None = None,
        *,
        fournisseurs: Callable[[], list[dict[str, Any]]] = list,
    ) -> None:
        self._stockage = stockage
        self._observabilite = observabilite
        self._choisir = choisir_fichier
        self._fournisseurs = fournisseurs

    def appeler(self, nom: str, *args: Any) -> dict[str, Any]:
        if nom not in METHODES:
            raise NonImplementee(f"observabilite.{nom} : méthode inconnue")
        return getattr(self, nom)(*args)

    def _stock(self) -> Stockage:
        if self._stockage is None:
            raise NonImplementee("observabilite : stockage indisponible")
        return self._stockage

    def details(self, echange: str) -> dict[str, Any] | None:
        return details_echange(self._stock().lister_mesures(echange=echange))

    def synthese(self) -> dict[str, Any]:
        return {"ok": True, "synthese": synthese(self._stock(), self._fournisseurs())}

    def methode(self) -> dict[str, Any]:
        observateur = getattr(self._observabilite, "observateur", None)
        return {"ok": True, "methode": methode(getattr(observateur, "impacts", None))}

    def reglages(self) -> dict[str, Any]:
        stock = self._stock()
        plafonds = lire_plafonds(stock)
        observateur = getattr(self._observabilite, "observateur", None)
        puissance = observateur.puissance_cpu() if observateur is not None else None
        return {
            "ok": True,
            "plafonds": [
                {**f, "plafond_eur": plafonds.get(f["hote"], PLAFOND_DEFAUT)}
                for f in self._fournisseurs()
            ],
            "plafond_defaut": PLAFOND_DEFAUT,
            "puissance_cpu_w": puissance,
        }

    def ecrire_plafond(self, hote: Any, euros: Any) -> dict[str, Any]:
        stock = self._stock()
        valeur = _nombre(euros)
        hotes = {f["hote"] for f in self._fournisseurs()}
        if not isinstance(hote, str) or hote not in hotes:
            return reponse_erreur(CODE_INVALIDE, "Fournisseur inconnu.")
        if valeur is None or not 0 <= valeur <= PLAFOND_MAX:
            return reponse_erreur(
                CODE_INVALIDE, f"Plafond : montant entre 0 et {PLAFOND_MAX:g} € attendu."
            )
        plafonds = lire_plafonds(stock)
        plafonds[hote] = round(valeur, 2)
        stock.ecrire_reglage("plafonds_depense", plafonds)
        return {"ok": True, "plafond_eur": plafonds[hote]}

    def ecrire_puissance(self, watts: Any) -> dict[str, Any]:
        valeur = _nombre(watts)
        if valeur is None or not PUISSANCE_MIN_W <= valeur <= PUISSANCE_MAX_W:
            return reponse_erreur(
                CODE_INVALIDE,
                f"Puissance : entre {PUISSANCE_MIN_W:g} et {PUISSANCE_MAX_W:g} W attendue.",
            )
        self._stock().ecrire_reglage("puissance_cpu_w", valeur)
        return {"ok": True, "puissance_cpu_w": valeur}

    def exporter_csv(self) -> dict[str, Any]:
        from slmsp.app.stockage import COLONNES_MESURE

        stock = self._stock()
        if self._choisir is None:
            return reponse_erreur("dialogue-indisponible", "Le choix du fichier est indisponible.")
        choisi = self._choisir(NOM_EXPORT)
        if not choisi:
            return {"ok": True, "enregistre": False, "nom": None}
        chemin = Path(choisi)
        if chemin.exists():
            return reponse_erreur(
                "fichier-existant", "Un fichier porte déjà ce nom. Choisissez un autre nom."
            )
        texte = exporter_csv(stock.lister_mesures(), COLONNES_MESURE)
        try:
            with chemin.open("x", encoding="utf-8-sig", newline="") as fichier:
                fichier.write(texte)
        except OSError as exc:
            LOGGER.error("export CSV : %s", type(exc).__name__)
            return reponse_erreur("ecriture-impossible", "Le fichier n'a pas pu être enregistré.")
        return {"ok": True, "enregistre": True, "nom": chemin.name}


__all__ = ["PontObservabilite"]
