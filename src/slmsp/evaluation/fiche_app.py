"""Données du comparatif des modèles pour l'application (story 17.5a).

`construire_fiche` lit en lecture seule des runs déjà archivés (notation, génération distante,
mesure du poste) selon `config/comparatif-app.toml` et produit un JSON figé, embarqué dans
l'application : aucun réseau, aucun modèle. Le bootstrap apparié et le bruit items sont ceux
d'`eval comparer` (`slmsp.evaluation.bootstrap`), jamais recalculés autrement.
"""

from __future__ import annotations

import json
import math
import statistics
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final, Literal, Self

from pydantic import model_validator

from slmsp.budget.config import ConfigTarifs, charger_tarifs
from slmsp.core.artefacts import _git, ouvrir_run
from slmsp.core.config import ModeleConfig, charger_toml
from slmsp.core.erreurs import SlmspError
from slmsp.core.schemas import SchemaBase, SousSchema
from slmsp.core.schemas.scores import Scores
from slmsp.evaluation import bootstrap
from slmsp.evaluation import config as cfg

NOM_APPELS: Final = "appels-distants.jsonl"
NOM_MESURE: Final = "resultat.json"
NOM_CONFIG: Final = "comparatif-app.toml"
MENTION_POSTE: Final = "coût matériel et énergie non chiffrés"
TIRAGES: Final = 2000
GRAINE: Final = 7
STATUTS_NOTATION: Final = ("complet",)
"""Seul un run de notation complet est retenu (spec 17.5a)."""


class ErreurFicheApp(SlmspError):
    """Entrée du comparatif inutilisable (run manquant, incomplet ou non comparable)."""


class EntreeApp(ModeleConfig):
    """Un modèle du comparatif."""

    id: str
    libelle: str
    emplacement: Literal["poste", "cloud"]
    run_notation: str
    run_generation: str | None = None
    run_mesure: str | None = None
    licence: str
    hebergement: str
    note: str = ""

    @model_validator(mode="after")
    def _coherente(self) -> Self:
        if self.emplacement == "cloud" and self.run_generation is None:
            raise ValueError(f"{self.id} : un modèle cloud exige run_generation")
        if self.emplacement == "poste" and self.run_generation is not None:
            raise ValueError(f"{self.id} : run_generation est réservé au cloud")
        if self.emplacement == "cloud" and self.run_mesure is not None:
            raise ValueError(f"{self.id} : run_mesure est réservé au poste")
        return self


class ConfigFicheApp(ModeleConfig):
    """`config/comparatif-app.toml`."""

    schema_version: Literal[1]
    reference: str
    modeles: list[EntreeApp]

    @model_validator(mode="after")
    def _reference_presente(self) -> Self:
        ids = [m.id for m in self.modeles]
        if len(set(ids)) != len(ids):
            raise ValueError("identifiants de modèles en double")
        if self.reference not in ids:
            raise ValueError(f"référence {self.reference!r} absente des modèles")
        if len(ids) < 2:
            raise ValueError("au moins un modèle en plus de la référence")
        notations = [m.run_notation for m in self.modeles]
        if len(set(notations)) != len(notations):
            raise ValueError("un même run de notation cité pour deux modèles")
        return self


class Ecart(SousSchema):
    ecart: float
    ic_bas: float
    ic_haut: float
    p_positif: float


class EcartsReference(SousSchema):
    qualite: Ecart | None
    taches: dict[str, Ecart]


class QualiteApp(SousSchema):
    score: float
    bruit_items: float | None
    taches: dict[str, float]


class PrixMtok(SousSchema):
    modele_id: str
    devise: Literal["USD"]
    entree: float
    sortie: float
    date_releve: str


class CoutApp(SousSchema):
    cout_api_eur: float | None
    """0 pour le poste ; `None` pour le cloud (le coût est alors par 1 000 demandes)."""
    eur_pour_1000_demandes: float | None
    prix_mtok: PrixMtok | None
    mention: str


class VitesseApp(SousSchema):
    origine: Literal["poste", "cloud"]
    debit_tokens_s: float | None
    premier_token_ms: float | None
    ram_max_go: float | None
    machine: str | None
    appels: int | None = None
    """Cloud : nombre d'appels réussis dont les médianes sont tirées."""
    mention: str = ""


class RunsApp(SousSchema):
    notation: str
    generation: str | None
    mesure: str | None
    date_notation: str


class ModeleFiche(SousSchema):
    id: str
    libelle: str
    emplacement: Literal["poste", "cloud"]
    reference: bool
    licence: str
    hebergement: str
    note: str
    qualite: QualiteApp
    ecart_reference: EcartsReference | None
    cout: CoutApp
    vitesse: VitesseApp | None
    runs: RunsApp


class BootstrapApp(SousSchema):
    tirages: int
    graine: int
    niveau_ic: float


class FicheApp(SchemaBase):
    """Contenu de `comparatif-modeles.json`."""

    schema_version: Literal[1] = 1
    genere_le: str
    commit: str | None
    jeu_version: str
    jeu_statut: str
    juge_principal: str
    items_par_tache: dict[str, int]
    reference: str
    bootstrap: BootstrapApp
    avertissements: list[str]
    modeles: list[ModeleFiche]


def charger_config(chemin: Path) -> ConfigFicheApp:
    return charger_toml(chemin, ConfigFicheApp)


def _run_complet(
    run_id: str, racine: Path, type_attendu: str, statuts: tuple[str, ...] = ("complet",)
) -> Any:
    try:
        run = ouvrir_run(run_id, racine=racine)
    except SlmspError as exc:
        raise ErreurFicheApp(f"run {run_id} introuvable ou invalide : {exc}") from exc
    if run.type != type_attendu:
        raise ErreurFicheApp(f"run {run_id} de type {run.type!r}, attendu {type_attendu!r}")
    if run.statut_courant() not in statuts:
        raise ErreurFicheApp(f"run {run_id} non complet (statut {run.statut_courant()})")
    return run


def _ecart(ligne: bootstrap.LigneComparaison) -> Ecart | None:
    if ligne.ecart is None or ligne.ic is None or ligne.p_positif is None:
        return None
    return Ecart(
        ecart=round(ligne.ecart, 2),
        ic_bas=round(ligne.ic.bas, 2),
        ic_haut=round(ligne.ic.haut, 2),
        p_positif=round(ligne.p_positif, 3),
    )


def _arrondi(valeur: float | None, chiffres: int = 2) -> float | None:
    return None if valeur is None else round(valeur, chiffres)


def _nombre(valeur: Any) -> float | None:
    """Nombre fini positif ou nul, sinon None (bool, texte, NaN écartés)."""
    if isinstance(valeur, bool) or not isinstance(valeur, int | float):
        return None
    return float(valeur) if math.isfinite(valeur) and valeur >= 0 else None


def _cloud(
    entree: EntreeApp, racine: Path, tarifs: ConfigTarifs, items_notes: int
) -> tuple[CoutApp, VitesseApp, str]:
    assert entree.run_generation is not None
    run = _run_complet(entree.run_generation, racine, "eval-generation")
    try:
        appels = run.lire_jsonl(NOM_APPELS)
    except (OSError, ValueError) as exc:
        raise ErreurFicheApp(f"run {entree.run_generation} : {NOM_APPELS} illisible") from exc
    appels = [a for a in appels if isinstance(a, dict)]
    if not appels:
        raise ErreurFicheApp(f"run {entree.run_generation} : {NOM_APPELS} absent ou vide")
    reussis = [a for a in appels if a.get("statut") == "ok"]
    if not reussis:
        raise ErreurFicheApp(f"run {entree.run_generation} : aucun appel réussi")
    if items_notes < 1:
        raise ErreurFicheApp(f"{entree.id} : aucun item noté, coût par demande indéfini")
    # Tous les appels facturés (relances, rejeux et appels d'outils compris), réussis ou non.
    couts = [c for a in appels if (c := _nombre(a.get("cout_eur"))) is not None]
    if not couts:
        raise ErreurFicheApp(f"run {entree.run_generation} : aucun coût dans {NOM_APPELS}")
    modeles = {a.get("modele_id") for a in reussis}
    modele_id = next(iter(modeles))
    if len(modeles) != 1 or not isinstance(modele_id, str):
        raise ErreurFicheApp(
            f"run {entree.run_generation} : modele_id absent ou multiple "
            f"({sorted(map(str, modeles))})"
        )
    tarif = tarifs.modeles.get(modele_id)
    if tarif is None or "direct" not in tarif.modes:
        raise ErreurFicheApp(f"aucun tarif direct pour {modele_id!r} dans tarifs.toml")
    prix = PrixMtok(
        modele_id=modele_id,
        devise=tarif.devise,
        entree=tarif.modes["direct"].entree,
        sortie=tarif.modes["direct"].sortie,
        date_releve=tarif.date.isoformat(),
    )
    delais = [d for a in reussis if (d := _nombre(a.get("delai_premier_token_ms")))]
    debits = [d for a in reussis if (d := _nombre(a.get("debit_tokens_s")))]
    cout = CoutApp(
        cout_api_eur=None,
        eur_pour_1000_demandes=_arrondi(sum(couts) / items_notes * 1000),
        prix_mtok=prix,
        mention=(
            f"coût réel par demande, relances et appels d'outils compris : {len(couts)} appels "
            f"facturés pour {items_notes} demandes notées ; génération seule, juge non compris"
        ),
    )
    vitesse = VitesseApp(
        origine="cloud",
        debit_tokens_s=_arrondi(statistics.median(debits)) if debits else None,
        premier_token_ms=_arrondi(statistics.median(delais), 0) if delais else None,
        ram_max_go=None,
        machine="poste de développement, via le réseau",
        appels=len(reussis),
        mention=(
            f"médianes sur les {len(reussis)} appels réussis du run (relances et appels d'outils "
            "compris), mesurées depuis le poste de développement"
        ),
    )
    return cout, vitesse, entree.run_generation


def _poste(entree: EntreeApp, racine: Path) -> tuple[CoutApp, VitesseApp | None]:
    cout = CoutApp(
        cout_api_eur=0.0, eur_pour_1000_demandes=None, prix_mtok=None, mention=MENTION_POSTE
    )
    if entree.run_mesure is None:
        return cout, None
    run = _run_complet(entree.run_mesure, racine, "measure")
    try:
        resultat = json.loads((run.dossier / NOM_MESURE).read_text(encoding="utf-8"))
        valeurs = resultat["valeurs"]
        env = resultat["environnement"]
        params = resultat["parametres"]
        premier = _nombre(valeurs["premier_token_s_mediane"])
        debit = _nombre(valeurs["debit_tps_mediane"])
        ram = _nombre(valeurs["ram_max_go"])
        if not (isinstance(env, dict) and isinstance(params, dict)):
            raise TypeError("environnement ou parametres non conformes")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ErreurFicheApp(f"run {entree.run_mesure} : {NOM_MESURE} illisible ({exc})") from exc
    if premier is None or debit is None or ram is None:
        raise ErreurFicheApp(f"run {entree.run_mesure} : valeurs manquantes dans {NOM_MESURE}")
    mesure = params.get("modele")
    if isinstance(mesure, str) and mesure.split(":")[-1] != entree.id:
        raise ErreurFicheApp(
            f"{entree.id} : la mesure {entree.run_mesure} porte sur {mesure!r}, pas sur ce modèle"
        )
    machine = (
        f"{env.get('cpu')} ; {env.get('nb_coeurs')} cœurs ; {env.get('os')} ; "
        f"CPU, {params.get('plafond_threads')} threads, {params.get('quantification')}"
    )
    return cout, VitesseApp(
        origine="poste",
        debit_tokens_s=_arrondi(debit),
        premier_token_ms=_arrondi(premier * 1000, 0),
        ram_max_go=_arrondi(ram),
        machine=machine,
    )


def _scores(run: Any) -> Scores:
    try:
        return Scores.model_validate_json((run.dossier / "scores.json").read_bytes())
    except (OSError, ValueError) as exc:
        raise ErreurFicheApp(f"run {run.run_id} : scores.json illisible") from exc


@dataclass
class _QualiteModele:
    """Qualité d'un modèle : observée, bruit items et, hors référence, lignes de l'écart."""

    observes: dict[str, float]
    bruit: float | None
    lignes: dict[str, bootstrap.LigneComparaison] | None
    non_notes: int
    items_notes: int


@dataclass
class _Qualites:
    modeles: list[_QualiteModele]
    items_par_tache: dict[str, int]
    avertissements: list[str]


def _bootstrap(ids: Sequence[str], racine: Path, tirages: int, graine: int) -> _Qualites:
    """Bootstrap apparié d'`eval comparer`, une paire (référence, modèle) à la fois.

    Les items non notés dans l'un des deux runs sont retirés de l'ensemble commun avant tirage,
    pour que l'écart porte sur les mêmes items des deux côtés.
    """
    seuils = cfg.charger_evaluation().seuils
    try:
        charges = [bootstrap.charger_run(i, racine, seuils) for i in ids]
        exclus = [bootstrap.items_non_notes(c) for c in charges]
        ref = bootstrap.comparer([charges[0]], tirages=tirages, graine=graine, exclus=exclus[0])
        resultats = [ref] + [
            bootstrap.comparer(
                [charges[0], c], tirages=tirages, graine=graine, exclus=exclus[0] | exclus[b]
            )
            for b, c in enumerate(charges[1:], 1)
        ]
    except ValueError as exc:
        raise ErreurFicheApp(str(exc)) from exc
    modeles: list[_QualiteModele] = []
    avertissements: list[str] = []
    for b, res in enumerate(resultats):
        rang = min(b, 1)
        if len(res.observes) <= rang or bootstrap.QUALITE not in res.observes[rang]:
            raise ErreurFicheApp(f"run {ids[b]} : Qualité non calculable sur les items communs")
        lignes = None if b == 0 else {g.nom: g for g in res.comparaisons[0].lignes}
        modeles.append(
            _QualiteModele(
                res.observes[rang],
                res.bruit_qualite[ids[b]],
                lignes,
                len(exclus[b]),
                len(charges[b].items) - len(exclus[b]),
            )
        )
        retires = exclus[0] | exclus[b]
        if b and retires:
            avertissements.append(
                f"Écart de {ids[b]} à la référence : {len(retires)} item(s) non noté(s) dans "
                "l'un des deux runs, retiré(s) de l'appariement."
            )
        avertissements += [a for a in res.avertissements if a not in avertissements]
    items = {code: len(liste) for code, liste in charges[0].par_tache().items()}
    return _Qualites(modeles, items, avertissements)


def _avertissements(bruits: list[float], jeu_statut: str, juge: str, items: int) -> list[str]:
    plage = (
        f"±{min(bruits):.1f} à ±{max(bruits):.1f}".replace(".", ",") if bruits else "non calculé"
    )
    return [
        f"Jeu de développement : {items} items fictifs rédigés pour le projet (statut {jeu_statut})"
        ", pas une mesure sur des demandes réelles.",
        f"Notes attribuées par le juge {juge} ; elles ne se comparent qu'entre modèles notés "
        "sur le même jeu par le même juge.",
        f"Bruit d'items : {plage} points sur la Qualité (IC 95 %) ; un écart plus petit que son "
        "IC n'est pas distinguable du bruit.",
        "Vitesses du poste : mesurées sur la machine de développement, pas sur le PC cible.",
        "Vitesses du cloud : mesurées depuis le poste de développement, elles dépendent du réseau "
        "et de la charge de l'hébergeur.",
        "Coûts : API seulement ; coût matériel et énergie du poste non chiffrés.",
    ]


def construire_fiche(
    config: ConfigFicheApp,
    racine: Path,
    *,
    tarifs: ConfigTarifs | None = None,
    tirages: int = TIRAGES,
    graine: int = GRAINE,
    commit: str | None = None,
    maintenant: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> FicheApp:
    """Assemble le comparatif ; `ErreurFicheApp` si un run manque ou n'est pas comparable."""
    racine = Path(racine).resolve()
    tarifs = tarifs if tarifs is not None else charger_tarifs(racine / "config" / "tarifs.toml")
    ordre = sorted(config.modeles, key=lambda m: m.id != config.reference)  # référence en tête
    runs = {
        m.id: _run_complet(m.run_notation, racine, "eval-notation", STATUTS_NOTATION) for m in ordre
    }
    for m in ordre:
        if m.run_generation is not None:
            lie = runs[m.id].manifeste.config.get("run_generation")
            if lie != m.run_generation:
                raise ErreurFicheApp(
                    f"{m.id} : la notation {m.run_notation} porte sur {lie}, "
                    f"pas sur {m.run_generation}"
                )
    qualites = _bootstrap([m.run_notation for m in ordre], racine, tirages, graine)
    tete = _scores(runs[ordre[0].id])
    fiches: list[ModeleFiche] = []
    for rang, m in enumerate(ordre):
        q = qualites.modeles[rang]
        ecarts: EcartsReference | None = None
        if q.lignes is not None:
            ecarts = EcartsReference(
                qualite=_ecart(q.lignes[bootstrap.QUALITE])
                if bootstrap.QUALITE in q.lignes
                else None,
                taches={
                    k: e
                    for k, g in q.lignes.items()
                    if k != bootstrap.QUALITE and (e := _ecart(g)) is not None
                },
            )
        if m.emplacement == "cloud":
            notes = q.items_notes
            cout, vitesse, generation = _cloud(m, racine, tarifs, notes)
        else:
            (cout, vitesse), generation = _poste(m, racine), None
        fiches.append(
            ModeleFiche(
                id=m.id,
                libelle=m.libelle,
                emplacement=m.emplacement,
                reference=rang == 0,
                licence=m.licence,
                hebergement=m.hebergement,
                note=m.note,
                qualite=QualiteApp(
                    score=round(q.observes[bootstrap.QUALITE], 1),
                    bruit_items=_arrondi(q.bruit, 1),
                    taches={
                        k: round(v, 1) for k, v in q.observes.items() if k != bootstrap.QUALITE
                    },
                ),
                ecart_reference=ecarts,
                cout=cout,
                vitesse=vitesse,
                runs=RunsApp(
                    notation=m.run_notation,
                    generation=generation,
                    mesure=m.run_mesure,
                    date_notation=runs[m.id].manifeste.cree_le.date().isoformat(),
                ),
            )
        )
    exclus = [
        f"{m.libelle} : {q.non_notes} item(s) non noté(s) (erreur du juge ou de génération), "
        "exclus de son score."
        for m, q in zip(ordre, qualites.modeles, strict=True)
        if q.non_notes
    ]
    bruits = [q.bruit for q in qualites.modeles if q.bruit is not None]
    items = sum(qualites.items_par_tache.values())
    return FicheApp(
        genere_le=maintenant().isoformat(timespec="seconds"),
        commit=commit,
        jeu_version=tete.jeu_version,
        jeu_statut=tete.jeu_statut,
        juge_principal=tete.juge_principal,
        items_par_tache=qualites.items_par_tache,
        reference=config.reference,
        bootstrap=BootstrapApp(tirages=tirages, graine=graine, niveau_ic=0.95),
        avertissements=[
            *_avertissements(bruits, tete.jeu_statut, tete.juge_principal, items),
            *exclus,
            *(_libelles(a, ordre) for a in qualites.avertissements),
        ],
        modeles=fiches,
    )


def _libelles(texte: str, ordre: Sequence[EntreeApp]) -> str:
    """Remplace les identifiants de runs de notation par les libellés lisibles."""
    for m in ordre:
        texte = texte.replace(m.run_notation, m.libelle)
    return texte


def commit_de(chemin: Path) -> str | None:
    sortie = _git(chemin if chemin.is_dir() else chemin.parent, "rev-parse", "HEAD")
    return sortie.strip() if sortie else None


def ecrire_fiche(fiche: FicheApp, sortie: Path) -> None:
    sortie.parent.mkdir(parents=True, exist_ok=True)
    texte = json.dumps(fiche.model_dump(mode="json"), ensure_ascii=False, indent=2)
    sortie.write_text(texte + "\n", encoding="utf-8", newline="\n")
