"""Observabilité de l'application (story 17.6) : mesures, coût, impact, plafond de dépense.

- `ObservateurApplication` : reçoit la `MesureAppel` de chaque appel LLM (local ou externe),
  y ajoute l'impact environnemental estimé et l'écrit dans `mesures_appels` (aucun texte de
  demande ou de réponse, aucune clé).
- `CompteurDepense` : `PlafondPort` des clients externes. Cumul par (mois UTC, hôte, modèle)
  dans `cumuls_depense` (jamais effacé par l'effacement de l'historique) ; plafond mensuel par
  hôte, lu à chaque appel dans le réglage `plafonds_depense` (2 € par défaut, 0 = désactivé).
  Réservation et régularisation sous un verrou de processus et une transaction SQLite.
- Coût : tarif de `config/tarifs.toml` (seule source de prix, en USD convertis au taux
  `taux_usd_eur`) ou, pour le preset `generique`, tarif saisi dans les Paramètres. Local :
  0 € (« pas de coût d'API »). Modèle sans tarif : coût inconnu (`None`), jamais 0.
- Impact (`config/impacts.toml`) : phase d'usage d'EcoLogits, page « Methodology > LLM
  inference » (https://ecologits.ai/latest/methodology/llm_inference/, relevée le 2026-10-21),
  réimplémentée (pas de dépendance à `ecologits`, amendement 7). Externe, par appel :

      f_E       = alpha_E × exp(beta_E × B) × P_actifs + gamma_E         (Wh / token, B = 64)
      E_gpu     = tokens_sortie × f_E                                     (Wh)
      ΔT        = durée mesurée de l'appel ; repli : tokens_sortie × f_L,
                  f_L = alpha_L × P_actifs + beta_L × B + gamma_L         (s / token)
      M         = facteur_memoire × P_totaux × bits / 8                   (Go)
      n_gpu     = puissance de 2 ≥ ⌈M / memoire_go⌉
      E_horsgpu = ΔT / 3600 × puissance_serveur × n_gpu / gpus_par_serveur / B   (Wh)
      E         = PUE × (E_horsgpu + n_gpu × E_gpu)
      CO2e      = E / 1000 × intensité de la zone de l'hébergeur         (g)

  Valeur centrale : P_actifs, ΔT mesurée (sinon modélisée), PUE nominal. Fourchette : basse
  avec `parametres_actifs_bas`, min(ΔT mesurée, modélisée) et `pue_bas` ; haute avec
  `parametres_actifs_haut`, max(ΔT mesurée, modélisée) et `pue_haut`. Fabrication du matériel
  hors périmètre. Local : puissance CPU moyenne (réglable, 25 W par défaut) × durée de l'appel,
  au mix France ; fourchette ×`facteur_bas` à ×`facteur_haut` (poste non instrumenté).
  Paramètres du modèle ou zone inconnus : impact « non estimé » (`None`).
"""

from __future__ import annotations

import csv
import io
import logging
import math
import threading
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Literal

from pydantic import Field

from slmsp.app.modele_externe import Observabilite, tarif_saisi
from slmsp.core.config import ModeleConfig, charger_toml, racine_projet
from slmsp.inference.mesures import FOURNISSEUR_LOCAL, MesureAppel, Tarif

if TYPE_CHECKING:
    from slmsp.app.stockage import Stockage
    from slmsp.budget.config import ConfigTarifs

LOGGER: Final = logging.getLogger("slmsp.app.observabilite")
NOM_IMPACTS: Final = "impacts.toml"
PLAFOND_DEFAUT: Final = 2.0
"""Plafond mensuel par défaut d'un fournisseur externe, en euros (amendement 8)."""
PLAFOND_MAX: Final = 10_000.0
PUISSANCE_MIN_W: Final = 1.0
PUISSANCE_MAX_W: Final = 500.0
MOTIFS_SAUT: Final = frozenset({"plafond-atteint", "tarif-inconnu"})
TAILLE_DERNIERS: Final = 20
CARACTERES_FORMULE: Final = ("=", "+", "-", "@", "\t", "\r")
MENTION_LOCAL: Final = "pas de coût d'API ; matériel et énergie du poste non facturés"


# --- Configuration des impacts ------------------------------------------------------------


class ParametresGpu(ModeleConfig):
    energie_alpha_wh: float = Field(ge=0)
    energie_beta: float
    energie_gamma_wh: float = Field(ge=0)
    latence_alpha_s: float = Field(ge=0)
    latence_beta_s: float = Field(ge=0)
    latence_gamma_s: float = Field(ge=0)
    taille_lot: int = Field(gt=0)
    memoire_go: float = Field(gt=0)
    bits: int = Field(gt=0)
    facteur_memoire: float = Field(gt=0)
    puissance_serveur_kw: float = Field(ge=0)
    gpus_par_serveur: int = Field(gt=0)


class Zone(ModeleConfig):
    libelle: str
    intensite_g_kwh: float = Field(ge=0)
    source: str


class Hebergeur(ModeleConfig):
    zone: str
    pue: float = Field(ge=1)
    pue_bas: float = Field(ge=1)
    pue_haut: float = Field(ge=1)
    note: str = ""


class ParametresModele(ModeleConfig):
    parametres_totaux: float = Field(gt=0)
    parametres_actifs: float = Field(gt=0)
    parametres_actifs_bas: float | None = Field(default=None, gt=0)
    parametres_actifs_haut: float | None = Field(default=None, gt=0)
    note: str = ""

    @property
    def actifs_bas(self) -> float:
        return min(self.parametres_actifs_bas or self.parametres_actifs, self.parametres_actifs)

    @property
    def actifs_haut(self) -> float:
        return max(self.parametres_actifs_haut or self.parametres_actifs, self.parametres_actifs)


class ParametresLocal(ModeleConfig):
    puissance_cpu_w: float = Field(gt=0)
    zone: str
    facteur_bas: float = Field(gt=0)
    facteur_haut: float = Field(gt=0)


class ConfigImpacts(ModeleConfig):
    """Contenu de `config/impacts.toml`."""

    schema_version: Literal[1]
    version_methode: str
    gpu: ParametresGpu
    zones: dict[str, Zone]
    hebergeurs: dict[str, Hebergeur]
    modeles: dict[str, ParametresModele]
    local: ParametresLocal


def charger_impacts(chemin: str | Path | None = None) -> ConfigImpacts:
    """Lit `impacts.toml` (défaut : `<racine>/config/impacts.toml`)."""
    return charger_toml(
        chemin if chemin is not None else racine_projet() / "config" / NOM_IMPACTS, ConfigImpacts
    )


@dataclass(frozen=True)
class Impact:
    """Énergie (Wh) et émissions (g CO2e) estimées, valeur centrale et fourchette."""

    energie_wh: float
    energie_wh_bas: float
    energie_wh_haut: float
    co2e_g: float
    co2e_g_bas: float
    co2e_g_haut: float

    def colonnes(self) -> dict[str, float]:
        return dict(self.__dict__)


def _impact(config: ConfigImpacts, zone: str, bas: float, central: float, haut: float) -> Impact:
    intensite = config.zones[zone].intensite_g_kwh
    return Impact(
        central,
        bas,
        haut,
        central / 1000 * intensite,
        bas / 1000 * intensite,
        haut / 1000 * intensite,
    )


def energie_gpu_par_token(gpu: ParametresGpu, actifs: float) -> float:
    """f_E d'EcoLogits : énergie GPU par token de sortie (Wh), `actifs` en milliards."""
    return (
        gpu.energie_alpha_wh * math.exp(gpu.energie_beta * gpu.taille_lot) * actifs
        + gpu.energie_gamma_wh
    )


def latence_par_token(gpu: ParametresGpu, actifs: float) -> float:
    """f_L d'EcoLogits : latence par token de sortie (s), repli sans durée mesurée."""
    return gpu.latence_alpha_s * actifs + gpu.latence_beta_s * gpu.taille_lot + gpu.latence_gamma_s


def nombre_gpu(gpu: ParametresGpu, totaux: float) -> int:
    """Puissance de 2 ≥ ⌈mémoire du modèle / mémoire d'un GPU⌉ (EcoLogits)."""
    memoire = gpu.facteur_memoire * totaux * gpu.bits / 8
    requis = max(1, math.ceil(memoire / gpu.memoire_go))
    return 1 << (requis - 1).bit_length()


def impact_externe(
    config: ConfigImpacts, preset: str, modele: str, tokens_sortie: int, duree_ms: int
) -> Impact | None:
    """Impact d'un appel externe (formules du module) ; `None` si non estimable."""
    hebergeur = config.hebergeurs.get(preset) or config.hebergeurs.get("generique")
    parametres = config.modeles.get(modele)
    if hebergeur is None or parametres is None or hebergeur.zone not in config.zones:
        return None
    g = config.gpu
    n_gpu = nombre_gpu(g, parametres.parametres_totaux)
    tokens = max(0, tokens_sortie)
    mesuree = max(0, duree_ms or 0) / 1000

    def energie(actifs: float, borne: Callable[[float, float], float], pue: float) -> float:
        modelisee = tokens * latence_par_token(g, actifs)
        latence = borne(mesuree, modelisee) if mesuree > 0 else modelisee
        hors_gpu = (
            latence / 3600 * g.puissance_serveur_kw * 1000 * n_gpu / g.gpus_par_serveur
        ) / g.taille_lot
        return pue * (hors_gpu + n_gpu * tokens * energie_gpu_par_token(g, actifs))

    def mesuree_seule(m: float, _modelisee: float) -> float:
        return m

    return _impact(
        config,
        hebergeur.zone,
        energie(parametres.actifs_bas, min, hebergeur.pue_bas),
        energie(parametres.parametres_actifs, mesuree_seule, hebergeur.pue),
        energie(parametres.actifs_haut, max, hebergeur.pue_haut),
    )


def impact_local(config: ConfigImpacts, puissance_w: float, duree_ms: int) -> Impact | None:
    """Impact d'un appel local : puissance CPU × durée, au mix de `local.zone`."""
    local = config.local
    if local.zone not in config.zones:
        return None
    central = puissance_w * max(0, duree_ms) / 1000 / 3600
    return _impact(
        config, local.zone, central * local.facteur_bas, central, central * local.facteur_haut
    )


# --- Tarifs --------------------------------------------------------------------------------


def tarif_config(tarifs: ConfigTarifs | None, modele: str) -> Tarif | None:
    """Tarif `direct` de `modele` dans `config/tarifs.toml`, converti en euros ; sinon `None`."""
    if tarifs is None:
        return None
    fiche = tarifs.modeles.get(modele)
    mode = fiche.modes.get("direct") if fiche is not None else None
    if mode is None:
        return None
    taux = tarifs.taux_usd_eur.valeur
    return Tarif(mode.entree * taux, mode.sortie * taux)


def resolveur_tarifs(tarifs: ConfigTarifs | None) -> Any:
    """`entree -> Tarif | None` : tarif saisi (preset `generique`), sinon `config/tarifs.toml`."""

    def tarif(entree: dict[str, Any]) -> Tarif | None:
        return tarif_saisi(entree) or (
            None if entree.get("preset") == "generique" else tarif_config(tarifs, entree["modele"])
        )

    return tarif


def charger_tarifs_application() -> ConfigTarifs | None:
    """`config/tarifs.toml`, ou `None` s'il est illisible (tout fournisseur sera sauté)."""
    from slmsp.budget.config import charger_tarifs

    try:
        return charger_tarifs()
    except Exception as exc:
        LOGGER.error("tarifs illisibles : fournisseurs externes sautés (%s)", type(exc).__name__)
        return None


# --- Observateur et compteur ---------------------------------------------------------------


def mois_utc(instant: datetime) -> str:
    return instant.strftime("%Y-%m")


class ObservateurApplication:
    """`ObservateurAppels` de l'application (voir le module)."""

    def __init__(self, stockage: Stockage, impacts: ConfigImpacts | None) -> None:
        self._stockage = stockage
        self.impacts = impacts

    def puissance_cpu(self) -> float:
        """Puissance CPU moyenne du poste (réglage), sinon celle de `impacts.toml`, sinon 25 W."""
        valeur = self._stockage.lire_reglage("puissance_cpu_w")
        if isinstance(valeur, (int, float)) and not isinstance(valeur, bool) and valeur > 0:
            return float(valeur)
        return self.impacts.local.puissance_cpu_w if self.impacts is not None else 25.0

    def impact(self, mesure: MesureAppel) -> Impact | None:
        if self.impacts is None or (mesure.motif in MOTIFS_SAUT):
            return None
        if mesure.local:
            return impact_local(self.impacts, self.puissance_cpu(), mesure.duree_ms)
        return impact_externe(
            self.impacts, mesure.fournisseur, mesure.modele, mesure.tokens_sortie, mesure.duree_ms
        )

    def mesurer(self, mesure: MesureAppel) -> None:
        impact = self.impact(mesure)
        valeurs: dict[str, Any] = {
            "echange": mesure.echange,
            "tache": mesure.tache,
            "fournisseur": mesure.fournisseur,
            "hote": mesure.hote,
            "modele": mesure.modele,
            "tokens_entree": mesure.tokens_entree,
            "tokens_sortie": mesure.tokens_sortie,
            "estime": mesure.estime,
            "interrompu": mesure.interrompu,
            "duree_ms": mesure.duree_ms,
            "premier_token_ms": mesure.premier_token_ms,
            "cout_eur": mesure.cout_eur,
            "motif": mesure.motif,
        }
        if impact is not None:
            valeurs.update(impact.colonnes())
        self._stockage.inscrire_mesure(valeurs)


def lire_plafonds(stockage: Stockage) -> dict[str, float]:
    """Réglage `plafonds_depense` normalisé (`{hote: euros}`) ; illisible : `{}`."""
    try:
        brut = stockage.lire_reglage("plafonds_depense")
    except Exception:
        return {}
    if not isinstance(brut, dict):
        return {}
    return {
        str(h): float(v)
        for h, v in brut.items()
        if isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= PLAFOND_MAX
    }


class CompteurDepense:
    """`PlafondPort` (voir le module). Jeton de réservation : `(mois, hôte, modèle, montant)`."""

    def __init__(self, stockage: Stockage) -> None:
        self._stockage = stockage
        self._verrou = threading.Lock()

    def plafond(self, hote: str) -> float:
        return lire_plafonds(self._stockage).get(hote, PLAFOND_DEFAUT)

    def reserver(
        self, hote: str, modele: str, montant: float
    ) -> tuple[str, str, str, float] | None:
        with self._verrou:
            mois = mois_utc(self._stockage.maintenant())
            if not self._stockage.reserver_depense(mois, hote, modele, montant, self.plafond(hote)):
                LOGGER.warning("plafond de dépense atteint pour %s", hote)
                return None
            return (mois, hote, modele, montant)

    def regulariser(self, jeton: tuple[str, str, str, float], cout: float) -> None:
        mois, hote, modele, montant = jeton
        with self._verrou:
            self._stockage.ajuster_depense(mois, hote, modele, max(0.0, cout) - montant)


def brancher_observabilite(service: Any, slug: str, stockage: Stockage) -> Observabilite:
    """Branche l'observateur sur le client local du service (`observateur`, `modele_mesure`)
    et rend ce que recevront les clients externes. Aucune erreur ne bloque le démarrage."""
    try:
        impacts: ConfigImpacts | None = charger_impacts()
    except Exception as exc:
        LOGGER.error("impacts illisibles : impact non estimé (%s)", type(exc).__name__)
        impacts = None
    observateur = ObservateurApplication(stockage, impacts)
    local = getattr(service, "llm", None)
    if local is not None:
        try:
            local.observateur = observateur
            local.modele_mesure = slug
        except Exception as exc:
            LOGGER.error("mesure du modèle local non branchée (%s)", type(exc).__name__)
    return Observabilite(
        observateur=observateur,
        plafond=CompteurDepense(stockage),
        tarif=resolveur_tarifs(charger_tarifs_application()),
    )


# --- Agrégats ------------------------------------------------------------------------------


def _somme(valeurs: Iterable[Any]) -> float | None:
    """Somme ; `None` si une valeur manque (coût ou impact inconnu)."""
    total = 0.0
    for v in valeurs:
        if v is None:
            return None
        total += float(v)
    return total


def _arrondi(valeur: float | None, chiffres: int = 6) -> float | None:
    return None if valeur is None else round(valeur, chiffres)


def resumer(mesures: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Totaux d'un ensemble de mesures (sauts exclus des tokens, coûts et impacts)."""
    appels = [m for m in mesures if m.get("motif") not in MOTIFS_SAUT]
    duree = sum(int(m["duree_ms"] or 0) for m in appels)
    sortie = sum(int(m["tokens_sortie"] or 0) for m in appels)
    return {
        "appels": len(appels),
        "sauts": len(mesures) - len(appels),
        "tokens_entree": sum(int(m["tokens_entree"] or 0) for m in appels),
        "tokens_sortie": sortie,
        "estime": any(m.get("estime") for m in appels),
        "interrompus": sum(1 for m in appels if m.get("interrompu")),
        "duree_ms": duree,
        "cout_eur": _arrondi(_somme(m.get("cout_eur") for m in appels)),
        "energie_wh": _arrondi(_somme(m.get("energie_wh") for m in appels)),
        "energie_wh_bas": _arrondi(_somme(m.get("energie_wh_bas") for m in appels)),
        "energie_wh_haut": _arrondi(_somme(m.get("energie_wh_haut") for m in appels)),
        "co2e_g": _arrondi(_somme(m.get("co2e_g") for m in appels)),
        "co2e_g_bas": _arrondi(_somme(m.get("co2e_g_bas") for m in appels)),
        "co2e_g_haut": _arrondi(_somme(m.get("co2e_g_haut") for m in appels)),
        "debit_tokens_s": round(sortie / (duree / 1000), 1) if duree > 0 else None,
    }


def details_echange(mesures: Sequence[Mapping[str, Any]]) -> dict[str, Any] | None:
    """Ligne « Détails » d'une réponse : totaux de ses appels, modèles et fournisseurs."""
    if not mesures:
        return None
    ordre = list(reversed(mesures))  # du premier au dernier appel
    resume = resumer(ordre)
    resume["modeles"] = list(dict.fromkeys(m["modele"] for m in ordre))
    resume["local"] = all(m["fournisseur"] == FOURNISSEUR_LOCAL for m in ordre)
    resume["motifs"] = sorted({m["motif"] for m in ordre if m.get("motif")})
    if resume["local"]:
        resume["mention_cout"] = MENTION_LOCAL
    return resume


def agreger(mesures: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Totaux par (fournisseur, modèle), du plus utilisé au moins utilisé."""
    groupes: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for m in mesures:
        groupes.setdefault((m["fournisseur"], m["modele"]), []).append(m)
    lignes = [
        {"fournisseur": f, "modele": modele, **resumer(groupe)}
        for (f, modele), groupe in groupes.items()
    ]
    return sorted(lignes, key=lambda x: (-x["appels"], x["fournisseur"], x["modele"]))


def synthese(stockage: Stockage, fournisseurs: Sequence[Mapping[str, Any]] = ()) -> dict[str, Any]:
    """Contenu de l'onglet « Observabilité » : totaux du jour et du mois (UTC), consommation
    des plafonds (hôtes des fournisseurs configurés et hôtes déjà facturés ce mois-ci),
    derniers appels (sans contenu)."""
    maintenant = stockage.maintenant()
    debut_mois = maintenant.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    debut_jour = maintenant.replace(hour=0, minute=0, second=0, microsecond=0)
    mesures_mois = stockage.lister_mesures(depuis=debut_mois.isoformat())
    jour = [m for m in mesures_mois if m["horodatage"] >= debut_jour.isoformat()]
    mois = mois_utc(maintenant)
    cumuls = stockage.cumuls_depense(mois)
    plafonds = lire_plafonds(stockage)
    hotes: dict[str, str] = {}
    for f in fournisseurs:
        hotes.setdefault(str(f["hote"]), str(f.get("libelle") or f["hote"]))
    for hote in cumuls:
        hotes.setdefault(hote, hote)
    sauts: dict[str, int] = {}
    for m in mesures_mois:
        if m.get("motif") in MOTIFS_SAUT and m.get("hote"):
            sauts[m["hote"]] = sauts.get(m["hote"], 0) + 1
    return {
        "mois": mois,
        "jour": maintenant.date().isoformat(),
        "totaux_jour": resumer(jour),
        "totaux_mois": resumer(mesures_mois),
        "par_modele_jour": agreger(jour),
        "par_modele_mois": agreger(mesures_mois),
        "plafonds": [
            {
                "hote": hote,
                "libelle": libelle,
                "cumul_eur": round(cumuls.get(hote, 0.0), 6),
                "plafond_eur": plafonds.get(hote, PLAFOND_DEFAUT),
                "sauts": sauts.get(hote, 0),
            }
            for hote, libelle in hotes.items()
        ],
        "derniers": stockage.lister_mesures(limite=TAILLE_DERNIERS),
    }


# --- Export CSV ----------------------------------------------------------------------------


def cellule_sure(valeur: Any) -> Any:
    """Cellule protégée contre l'injection de formule (amendement 9) : apostrophe devant un
    texte qui commence par `=`, `+`, `-`, `@`, une tabulation ou un retour chariot."""
    if isinstance(valeur, str) and valeur.startswith(CARACTERES_FORMULE):
        return "'" + valeur
    return valeur


def exporter_csv(mesures: Sequence[Mapping[str, Any]], colonnes: Sequence[str]) -> str:
    """CSV (séparateur `;`, pour Excel en français) des mesures, du plus ancien au plus récent."""
    tampon = io.StringIO()
    ecrivain = csv.writer(tampon, delimiter=";", lineterminator="\r\n")
    ecrivain.writerow(colonnes)
    for m in reversed(list(mesures)):
        ecrivain.writerow([cellule_sure(m.get(c)) for c in colonnes])
    return tampon.getvalue()


# --- Méthode (aide de l'interface) ---------------------------------------------------------


def methode(impacts: ConfigImpacts | None) -> dict[str, Any]:
    """Hypothèses et sources affichées par le lien « Méthode »."""
    if impacts is None:
        return {"disponible": False}
    g = impacts.gpu
    return {
        "disponible": True,
        "version": impacts.version_methode,
        "formules": [
            "Externe (EcoLogits, phase d'usage, ecologits.ai/latest/methodology/"
            "llm_inference, relevé le 2026-10-21) : énergie GPU par token de sortie f_E = "
            f"{g.energie_alpha_wh:g} × exp({g.energie_beta:g} × {g.taille_lot}) × milliards de "
            f"paramètres actifs + {g.energie_gamma_wh:g} Wh (lot de {g.taille_lot}) ; nombre de "
            f"GPU de {g.memoire_go:g} Go = puissance de 2 couvrant {g.facteur_memoire:g} × "
            f"paramètres totaux × {g.bits} bits ; serveur hors GPU {g.puissance_serveur_kw:g} kW "
            f"pour {g.gpus_par_serveur} GPU, partagé par le lot, pendant la durée mesurée de "
            "l'appel (repli : latence modélisée f_L) ; le tout multiplié par le PUE de "
            "l'hébergeur.",
            "Fourchette : PUE bas et haut, latence mesurée ou modélisée, et paramètres actifs "
            "bas et haut quand ils ne sont pas connus.",
            "Paramètres des modèles : "
            + " ; ".join(
                f"{nom} : {p.parametres_totaux:g} Md au total, "
                + (
                    f"{p.actifs_bas:g} à {p.actifs_haut:g} Md actifs"
                    if p.actifs_bas != p.actifs_haut
                    else f"{p.parametres_actifs:g} Md actifs"
                )
                + (f" ({p.note})" if p.note else "")
                for nom, p in impacts.modeles.items()
            )
            + ".",
            "Émissions = énergie × intensité carbone de l'électricité de la zone de l'hébergeur.",
            f"Local : puissance moyenne du processeur ({impacts.local.puissance_cpu_w:g} W par "
            "défaut, réglable) × durée de l'appel, au mix électrique de la France ; poste non "
            f"instrumenté, fourchette ×{impacts.local.facteur_bas:g} à "
            f"×{impacts.local.facteur_haut:g}.",
            "Seule la phase d'usage est estimée : les impacts de fabrication du matériel sont "
            "hors périmètre. Les valeurs sont des estimations, pas des mesures.",
        ],
        "zones": [
            {
                "code": code,
                "libelle": z.libelle,
                "intensite_g_kwh": z.intensite_g_kwh,
                "source": z.source,
            }
            for code, z in impacts.zones.items()
        ],
        "hebergeurs": [
            {"preset": nom, "zone": h.zone, "pue": h.pue, "note": h.note}
            for nom, h in impacts.hebergeurs.items()
        ],
        "cout": [
            "Coût externe = tokens × tarif du modèle (config/tarifs.toml, en dollars convertis "
            "au taux fixe prudent de 1 USD = 1 EUR), ou tarif saisi pour un hôte générique.",
            f"Modèle local : 0 € ({MENTION_LOCAL}).",
            "Faute d'usage renvoyé par le fournisseur, les tokens sont estimés (caractères ÷ 2,5) "
            "et marqués « estimé ».",
        ],
        "plafond": [
            f"Plafond mensuel par fournisseur, {PLAFOND_DEFAUT:g} € par défaut (0 = désactivé), "
            "mois civil en temps universel (UTC).",
            "Avant chaque appel, le coût pire cas (entrée estimée majorée de 25 % et longueur "
            "maximale de sortie, relances comprises) est réservé ; s'il dépasse le plafond, "
            "l'appel n'est pas envoyé et le fournisseur suivant, puis le modèle local, répond.",
            "Le cumul repose sur l'horloge du poste : il n'est pas infalsifiable.",
        ],
    }


__all__ = [
    "PLAFOND_DEFAUT",
    "CompteurDepense",
    "ConfigImpacts",
    "Impact",
    "ObservateurApplication",
    "agreger",
    "brancher_observabilite",
    "cellule_sure",
    "charger_impacts",
    "charger_tarifs_application",
    "details_echange",
    "exporter_csv",
    "energie_gpu_par_token",
    "impact_externe",
    "impact_local",
    "latence_par_token",
    "lire_plafonds",
    "methode",
    "mois_utc",
    "nombre_gpu",
    "resolveur_tarifs",
    "resumer",
    "synthese",
    "tarif_config",
]
