"""Juges tiers : avis comparatif sur un run `eval-notation`, hors score officiel (story S3).

`noter_tiers(depuis, juge=…)` :

1. ouvre le run de notation `depuis` (lecture seule, jamais réécrit), son run de génération
   parent et le jeu (manifeste revérifié hors calibrage) ;
2. retient les items des Tâches `taches` (défaut CR, LC, CT, RE) au verdict principal valide,
   avec la sortie canonique notée (mêmes demandes, même prompt que le Juge principal) ;
3. estime le coût avant tout run (usage de budget, poste et tarif vérifiés : une erreur de
   configuration ne laisse pas de run `interrompu`) ; avec `plafond_estime_eur`, refuse
   avant tout run et tout appel si le coût estimé dépasse le plafond ;
4. crée `runs/eval-juges-tiers/<id>/` (`run.json`, `etat.jsonl`), fait juger, écrit
   `verdicts.jsonl` (juge `tiers`) et `accords.json` : par Tâche et par critère de kappa
   (`evaluation.scores.CRITERES_KAPPA`), effectif commun, accord brut et kappa de Cohen
   pour les paires tiers/principal, tiers/second, principal/second ; sous `EFFECTIF_MIN`
   paires, statut « non concluant » sans kappa. `desaccords` liste les items où trois juges
   ou plus notent un critère sans unanimité.

Statut final : `partiel-budget` si le budget s'est épuisé, `partiel-erreur` si un item est
non jugé pour une autre raison, `complet` sinon. Seule `ouvrir_juge_tiers` assemble les
objets réels (imports paresseux).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Final, Protocol

from pydantic import ValidationError

from slmsp.core.artefacts import Run, nouveau_run, ouvrir_run
from slmsp.core.canonique import json_canonique
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ManifesteInvalide, SlmspError
from slmsp.core.items import VERSION_CALIBRAGE, ItemBase, lire_jeu
from slmsp.core.schemas.verdict import Verdict
from slmsp.evaluation import notation
from slmsp.evaluation.gel import verifier_manifeste
from slmsp.evaluation.scores import CRITERES_KAPPA, Jugement, kappa_cohen, note

TYPE_RUN: Final = "eval-juges-tiers"
FICHIER_VERDICTS: Final = "verdicts.jsonl"
FICHIER_ACCORDS: Final = "accords.json"
TACHES_DEFAUT: Final = ("CR", "LC", "CT", "RE")
EFFECTIF_MIN: Final = 10
STATUTS_NOTATION: Final = ("complet", "partiel-erreur", "partiel-budget")
JUGE_TIERS: Final = "tiers"
JUGES: Final = (JUGE_TIERS, notation.JUGE_PRINCIPAL, notation.JUGE_SECOND)
NON_CONCLUANT: Final = "non concluant"
CONCLUANT: Final = "concluant"

Rapporteur = Callable[[str], None]


class JugeTiersProto(Protocol):
    """Juge injecté : `juger(demandes)`, `estimer(demandes)` et `description()`."""

    def juger(self, demandes: Sequence[Any]) -> Any: ...

    def estimer(self, demandes: Sequence[Any]) -> Any: ...

    def description(self) -> dict[str, Any]: ...


@dataclass
class RapportTiers:
    run: Run
    statut: str
    accords: dict[str, Any]
    demandes: int
    depuis_cache: int
    budget_epuise: bool
    cout_session_eur: float


@dataclass(frozen=True)
class _Preparation:
    notation_run: Run
    selection: list[ItemBase]
    demandes: list[notation.Demande]
    jugements: dict[str, dict[str, Jugement]]


# --- Lecture du run de notation -------------------------------------------------------------


def _jugements_notation(run: Run) -> dict[str, dict[str, Jugement]]:
    jugements: dict[str, dict[str, Jugement]] = {
        notation.JUGE_PRINCIPAL: {},
        notation.JUGE_SECOND: {},
    }
    for rang, ligne in enumerate(run.lire_jsonl(notation.FICHIER_VERDICTS), 1):
        juge = ligne.get("juge")
        if juge not in jugements:
            continue
        try:
            verdict = (
                None if ligne.get("verdict") is None else Verdict.model_validate(ligne["verdict"])
            )
        except ValidationError:
            raise ManifesteInvalide(
                f"run {run.run_id} : ligne {rang} de {notation.FICHIER_VERDICTS} invalide"
            ) from None
        jugements[juge][ligne["item_id"]] = Jugement(
            statut=ligne["statut"], verdict=verdict, cle=ligne.get("cle"), motif=ligne.get("motif")
        )
    return jugements


def preparer(depuis: str, taches: Sequence[str], base: Path) -> _Preparation:
    """Demandes au juge tiers depuis le run de notation `depuis` (lecture seule)."""
    run = ouvrir_run(depuis, racine=base)
    if run.type != notation.TYPE_RUN:
        raise ManifesteInvalide(f"run {depuis} de type {run.type!r}, pas {notation.TYPE_RUN!r}")
    statut = run.statut_courant()
    if statut not in STATUTS_NOTATION:
        raise SlmspError(
            f"run de notation {depuis} au statut {statut!r} : refusé "
            f"(attendu : {', '.join(STATUTS_NOTATION)})"
        )
    inconnues = [t for t in taches if t not in CRITERES_KAPPA]
    if inconnues or not taches:
        raise ValueError(
            f"tâches invalides : {list(taches)} (attendu parmi {list(CRITERES_KAPPA)})"
        )
    jeu_version = run.manifeste.jeu_version
    generation = run.manifeste.config.get("run_generation")
    if jeu_version is None or not isinstance(generation, str):
        raise ManifesteInvalide(f"run {depuis} : run.json sans jeu_version ou run_generation")
    if jeu_version != VERSION_CALIBRAGE:
        verifier_manifeste(jeu_version, base)
    jeu = lire_jeu(jeu_version, base)
    generations = notation._generations(ouvrir_run(generation, racine=base))
    jugements = _jugements_notation(run)
    principal = jugements[notation.JUGE_PRINCIPAL]
    selection = [
        item
        for item in jeu.items
        if item.code in taches
        and item.id in generations
        and generations[item.id].statut == "ok"
        and (j := principal.get(item.id)) is not None
        and j.valide
    ]
    demandes = [
        notation.Demande(item, generations[item.id].sortie_canonique.model_dump(mode="json"))
        for item in selection
    ]
    return _Preparation(run, selection, demandes, jugements)


# --- Accords --------------------------------------------------------------------------------


def _paire(
    a: Mapping[str, Jugement], b: Mapping[str, Jugement], items: Sequence[ItemBase], critere: str
) -> list[tuple[Any, Any]]:
    paires = []
    for item in items:
        ja, jb = a.get(item.id), b.get(item.id)
        if ja is None or jb is None or not ja.valide or not jb.valide:
            continue
        assert ja.verdict is not None and jb.verdict is not None
        na, nb = note(ja.verdict, critere), note(jb.verdict, critere)
        if na is not None and nb is not None:
            paires.append((na, nb))
    return paires


def calculer_accords(
    items: Sequence[ItemBase],
    jugements: Mapping[str, Mapping[str, Jugement]],
    taches: Sequence[str],
    effectif_min: int = EFFECTIF_MIN,
) -> dict[str, Any]:
    """Accords par Tâche, critère et paire de juges, puis items sans unanimité (≥ 3 juges)."""
    noms = [j for j in JUGES if j in jugements]
    resultat: dict[str, Any] = {"effectif_min": effectif_min, "taches": {}, "desaccords": []}
    for tache in taches:
        items_tache = [i for i in items if i.code == tache]
        criteres: dict[str, Any] = {}
        for critere, (categories, pondere) in CRITERES_KAPPA.get(tache, {}).items():
            paires_juges: dict[str, Any] = {}
            for a, b in combinations(noms, 2):
                paires = _paire(jugements[a], jugements[b], items_tache, critere)
                n = len(paires)
                accord = sum(x == y for x, y in paires) / n if n else None
                kappa: float | None = None
                if n >= effectif_min:
                    try:
                        kappa = kappa_cohen(paires, categories, pondere)
                    except ValueError:
                        kappa = None
                paires_juges[f"{a}/{b}"] = {
                    "effectif": n,
                    "accord_brut": None if accord is None else round(accord, 4),
                    "kappa": None if kappa is None else round(kappa, 4),
                    "statut": CONCLUANT if n >= effectif_min else NON_CONCLUANT,
                }
            criteres[critere] = paires_juges
            for item in items_tache:
                notes = {}
                for nom in noms:
                    j = jugements[nom].get(item.id)
                    if j is not None and j.valide and j.verdict is not None:
                        valeur = note(j.verdict, critere)
                        if valeur is not None:
                            notes[nom] = valeur
                if len(notes) >= 3 and len(set(notes.values())) > 1:
                    resultat["desaccords"].append(
                        {"item_id": item.id, "tache": tache, "critere": critere, "notes": notes}
                    )
        resultat["taches"][tache] = {"effectif_items": len(items_tache), "criteres": criteres}
    return resultat


def tableau_accords(accords: Mapping[str, Any]) -> str:
    """Tableau texte des accords (une ligne par Tâche, critère et paire)."""
    lignes = ["Tâche  Critère               Paire               n   accord  kappa"]
    for tache, bloc in accords["taches"].items():
        for critere, paires in bloc["criteres"].items():
            for paire, valeurs in paires.items():
                accord = valeurs["accord_brut"]
                kappa = valeurs["kappa"]
                lignes.append(
                    f"{tache:<6} {critere:<21} {paire:<19} {valeurs['effectif']:>3}  "
                    f"{'—' if accord is None else f'{accord:.2f}':>6}  "
                    f"{valeurs['statut'] if kappa is None else f'{kappa:.2f}'}"
                )
    lignes.append(f"Items sans unanimité (≥ 3 juges) : {len(accords['desaccords'])}")
    return "\n".join(lignes)


# --- Phase ----------------------------------------------------------------------------------


def noter_tiers(
    depuis: str,
    *,
    juge: JugeTiersProto,
    nom_juge: str,
    taches: Sequence[str] = TACHES_DEFAUT,
    racine: str | Path | None = None,
    plafond_estime_eur: float | None = None,
    rapporter: Rapporteur | None = None,
) -> RapportTiers:
    """Fait juger les items de `depuis` par `juge` dans un nouveau run (voir le module)."""
    dire = rapporter or (lambda _message: None)
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    prep = preparer(depuis, list(taches), base)
    # Toujours avant le run : poste, imputation et tarif inconnus lèvent ici, sans run créé.
    estimation = juge.estimer(prep.demandes)
    if plafond_estime_eur is not None:
        resume = (
            f"coût estimé {estimation.cout_estime_eur:.2f} € (pire cas "
            f"{estimation.cout_pire_cas_eur:.2f} €), {estimation.nb_a_juger} item(s) à juger, "
            f"{estimation.nb_en_cache} en cache"
        )
        if estimation.cout_estime_eur > plafond_estime_eur:
            raise SlmspError(
                f"juges tiers refusés : {resume}, au-dessus du plafond de "
                f"{plafond_estime_eur:.2f} € ; aucun run créé, aucun appel fait"
            )
        dire(f"Estimation : {resume} (plafond {plafond_estime_eur:.2f} €).")
    source = prep.notation_run
    run = nouveau_run(
        TYPE_RUN,
        f"{nom_juge}-{notation._slug(depuis)}"[:80],
        {
            "phase": "juges-tiers",
            "run_notation": depuis,
            "juge": juge.description(),
            "taches": list(taches),
            "items": [item.id for item in prep.selection],
        },
        parents=[depuis],
        entrees={
            "verdicts_notation": source.dossier / notation.FICHIER_VERDICTS,
            "juges": racine_projet() / "config" / "juges.toml",
        },
        racine=base,
        modele_ref=source.manifeste.modele_ref,
        quantification=source.manifeste.quantification,
        jeu_version=source.manifeste.jeu_version,
    )
    try:
        dire(f"Juge tiers {nom_juge} : {len(prep.demandes)} demande(s).")
        issue = notation._juger(lambda: juge.juger(prep.demandes), prep.demandes)
        for item in prep.selection:
            jugement = issue.jugements.get(item.id)
            if jugement is not None:
                run.ajouter_jsonl(
                    FICHIER_VERDICTS, notation._ligne_verdict(item, JUGE_TIERS, jugement)
                )
        if not issue.jugements:
            run.ecrire(FICHIER_VERDICTS, b"")
        jugements = {JUGE_TIERS: issue.jugements, **prep.jugements}
        accords = calculer_accords(prep.selection, jugements, list(taches))
        run.ecrire(FICHIER_ACCORDS, json_canonique(accords) + b"\n")
        non_juges = any(
            j.statut == "non-juge" and j.motif != notation.MOTIF_BUDGET
            for j in issue.jugements.values()
        )
        if issue.budget_epuise:
            statut = "partiel-budget"
        elif non_juges:
            statut = "partiel-erreur"
        else:
            statut = "complet"
    except BaseException as exc:
        run.terminer("interrompu", motif=f"{type(exc).__name__} : {exc}"[:500])
        raise
    run.terminer(statut)
    return RapportTiers(
        run=run,
        statut=statut,
        accords=accords,
        demandes=len(prep.demandes),
        depuis_cache=issue.depuis_cache,
        budget_epuise=issue.budget_epuise,
        cout_session_eur=issue.cout_eur,
    )


def ouvrir_juge_tiers(
    nom: str, racine: str | Path | None = None, *, rejouer_invalides: bool = False
) -> Any:
    """Assemble le juge tiers réel `nom` (`[juges_tiers.<nom>]` de `juges.toml`).

    Lève `ValueError` pour un nom absent de `juges.toml`, `SecretManquant` si la clé du
    fournisseur manque (sans valeur affichée), `ConfigurationInvalide` pour une config.
    """
    from slmsp.budget.registre import RegistreBudget
    from slmsp.core.var import dossier_var
    from slmsp.fournisseurs.client import (
        FOURNISSEURS,
        ClientCompatibleOpenAI,
        fabriquer_http,
        lire_cle,
    )
    from slmsp.fournisseurs.journal import NOM_JOURNAL_JUGES_TIERS, JournalAppels
    from slmsp.judge.cache import CacheVerdicts
    from slmsp.judge.config import charger_juges
    from slmsp.judge.grille import charger_grille
    from slmsp.judge.tiers import JugeTiers

    config = charger_juges()
    tiers = config.juges_tiers.get(nom)
    if tiers is None:
        connus = ", ".join(sorted(config.juges_tiers)) or "aucun"
        raise ValueError(f"juge tiers inconnu : {nom!r} (juges.toml, connus : {connus})")
    fournisseur = FOURNISSEURS[tiers.fournisseur]
    cle = lire_cle(fournisseur)
    base = Path(racine) if racine is not None else None
    client = ClientCompatibleOpenAI(
        fournisseur,
        RegistreBudget(),
        fabriquer_http(fournisseur),
        cle,
        journal=JournalAppels(dossier_var() / NOM_JOURNAL_JUGES_TIERS),
    )
    grille = charger_grille(config.principal.chemin_grille(base))
    return JugeTiers(
        nom, tiers, client, CacheVerdicts(), grille, rejouer_invalides=rejouer_invalides
    )
