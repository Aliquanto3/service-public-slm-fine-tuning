"""Sélection des cibles parmi des candidats notés : `data build --selection` (story 15.3, O3).

`lancer_selection` lit un run `data-candidats` (story 15.2 : `candidats.jsonl`, aucun texte),
un ou plusieurs runs `data-juger` sur ce run (`verdicts.jsonl`) et le jeu SFT d'origine des
candidats (SHA revérifié contre son MANIFEST), puis écrit une **nouvelle version**
`data/train/vN/` (MANIFEST v2, bloc `selection`) :

- Tâches de `taches` (CR, LC) : chaque ligne prend le **meilleur candidat accepté** ; sans
  candidat accepté, elle est écartée (motif compté, aucun repli sur la ligne d'origine) ;
- Tâches de `retirees` (RE) : absentes ;
- autres Tâches : ligne d'origine copiée à l'octet près.

Règles (spec O3 amendée le 20/10) :

1. Sources de cible : `mistral` et la base locale du run de candidats (`slm:<slug>`)
   seulement ; un candidat `openrouter:*` est ignoré et compté ; toute autre source fait
   échouer avant tout run. Un juge n'est jamais une source de cible.
2. Acceptation : verdict `accepte` du juge de données principal (`juge`, DeepSeek), toutes
   notes au moins à leur seuil (seuils lus dans la config du run de jugement, puis
   réappliqués ici aux notes) ; le `verdict_modele` n'est jamais lu. Un candidat sans
   verdict, ou au verdict `invalide`, est ignoré et compté. Runs sources (candidats,
   jugements) `complet` exigés, sauf `accepter_partiel` (candidats sans verdict comptés par
   Tâche au MANIFEST).
3. Score : moyenne (poids égaux) des critères normalisés sur [0, 1] : la grille note chaque
   critère de 0 (min explicite) à sa note maximale de `CRITERES_JUGE_DONNEES`, `couverture`
   (calculée) de 0 à 1 ; égalité : base locale, puis Mistral, puis la température la plus
   basse, la graine, et l'identifiant du candidat.
4. Cible Mistral gagnante : ligne d'origine copiée (sa cible est déjà la cible Mistral
   nettoyée). Cible locale : relue dans `generations-locales.sqlite` (lecteur `data`, lecture
   seule), recoupée (session, `generateur`, `usage`, statut `ok`, SHA-256 de la réponse,
   conversation de la requête = entrée de la ligne), passée par `cible_apprise` **avec**
   `compter` ; ligne v2 (`meta.cible`, source et licence du Registre).
5. Licences : les sorties de la base doivent avoir une entrée `modele-base` au Registre, et
   toute source du jeu doit admettre la variante, sinon échec avant tout run.
6. Ligne sans aucun candidat : écartée (`sans_candidat`) ; candidats tous refusés ou
   ignorés : écartée (`aucun_accepte`). Moins de `CR_MIN` lignes CR retenues : échec (rien
   sous `data/train/`) ; aucune ligne LC : avertissement au MANIFEST.

Aucun texte n'est rédigé ici (D1) : cibles relues dans les journaux, entrées du jeu SFT.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Final

from pydantic import ValidationError

from slmsp.core.artefacts import (
    NOM_JOURNAL_LOCAL,
    Run,
    nouveau_run,
    ouvrir_run,
    ouvrir_sqlite_lecture,
)
from slmsp.core.canonique import json_canonique, sha256_fichier, sha256_hex
from slmsp.core.erreurs import ManifesteInvalide, ProvenanceInvalide
from slmsp.core.schemas.entrainement import (
    TYPE_RUN_BUILD,
    BilanSelection,
    CibleLigne,
    LigneEntrainement,
    ManifesteJeuEntrainement,
    MetaLigne,
    Selection,
)
from slmsp.core.selection import verifier_selection
from slmsp.core.var import dossier_var
from slmsp.data.build import VARIANTES, _creer_version
from slmsp.data.candidats import NOM_CANDIDATS, TACHES_CANDIDATES, RegleCible, cible_apprise
from slmsp.data.candidats import TYPE_RUN as TYPE_RUN_CANDIDATS
from slmsp.data.config import CRITERES_CALCULES, CRITERES_JUGE_DONNEES
from slmsp.data.juge_donnees import NOM_VERDICTS
from slmsp.data.juge_donnees import TYPE_RUN as TYPE_RUN_JUGER
from slmsp.data.licences import RegistreLicences
from slmsp.data.nettoyage import Tokeniseur, tokeniseur_du_modele
from slmsp.data.preferences import _jeu_sft
from slmsp.inference.journal_local import USAGE_LOCAL

__all__ = [
    "CR_MIN",
    "NOM_DETAIL",
    "ResultatSelection",
    "Verdict",
    "lancer_selection",
    "score",
]

NOM_TRAIN: Final = "train.jsonl"
NOM_MANIFEST: Final = "MANIFEST.json"
NOM_RAPPORT: Final = "rapport.json"
NOM_DETAIL: Final = "selection.jsonl"
CR_MIN: Final = 30
"""Lignes CR retenues en dessous desquelles le build est refusé (amendement 3 du 20/10)."""
SOURCE_MISTRAL: Final = "mistral"
PREFIXE_IGNORE: Final = "openrouter:"
"""Candidats ignorés cette nuit (amendement 1) : aucune cible DeepSeek."""
_DECIMALES: Final = 9


@dataclass(frozen=True)
class ResultatSelection:
    """Run produit, version écrite et rapport."""

    run: Run
    version: str
    dossier: Path
    rapport: dict[str, Any]


@dataclass(frozen=True)
class Verdict:
    """Verdict retenu d'un candidat : accepté et score dans [0, 1], notes du juge."""

    accepte: bool
    score: float
    notes: dict[str, float]


def score(tache: str, notes: Mapping[str, Any]) -> float | None:
    """Moyenne des critères de `tache` normalisés sur [0, 1] ; `None` si une note manque, n'est
    pas un nombre ou sort de son échelle (0 à la note maximale, [0, 1] pour un critère
    calculé)."""
    echelles = {nom: float(maxi) for nom, maxi in CRITERES_JUGE_DONNEES[tache].items()}
    echelles.update(dict.fromkeys(CRITERES_CALCULES.get(tache, ()), 1.0))
    valeurs = []
    for nom, maxi in sorted(echelles.items()):
        note = notes.get(nom)
        if isinstance(note, bool) or not isinstance(note, int | float) or not 0 <= note <= maxi:
            return None
        valeurs.append(float(note) / maxi)
    return round(sum(valeurs) / len(valeurs), _DECIMALES)


# --- Entrées ------------------------------------------------------------------------------


def _run_termine(run_id: str, type_run: str, base: Path, *, accepter_partiel: bool) -> Run:
    """Run source fini : `complet` exigé ; avec `accepter_partiel`, tout statut final admis
    (jamais `en_cours`)."""
    run = ouvrir_run(run_id, racine=base)
    if run.type != type_run:
        raise ManifesteInvalide(f"run {run_id} : type {run.type!r}, {type_run} attendu")
    statut = run.statut_courant()
    if statut == "en_cours":
        raise ManifesteInvalide(f"run {run_id} encore en cours")
    if statut != "complet" and not accepter_partiel:
        raise ManifesteInvalide(
            f"run {run_id} : statut {statut!r}, « complet » attendu (--accepter-partiel pour "
            "l'admettre, candidats sans verdict comptés au MANIFEST)"
        )
    return run


def _verdicts(
    runs: Sequence[Run], candidats_run_id: str, juge: str
) -> tuple[Run, dict[tuple[str, str], dict[str, Any]]]:
    """Run du juge principal et ses verdicts indexés par `(session_id, candidat_id)`.

    Refus : run sur un autre run de candidats, deux runs du même juge, aucun run du juge
    principal. Les runs des autres juges (Kimi) sont acceptés et consignés : leurs verdicts ne
    portent que sur les candidats OpenRouter, ignorés cette nuit.
    """
    modeles: Counter[str] = Counter()
    principal: Run | None = None
    for run in runs:
        config = run.manifeste.config
        if config.get("depuis") != candidats_run_id:
            raise ManifesteInvalide(
                f"run {run.run_id} : jugement de {config.get('depuis')!r}, "
                f"{candidats_run_id} attendu"
            )
        modele = str((config.get("juge") or {}).get("modele"))
        modeles[modele] += 1
        if modeles[modele] > 1:
            raise ManifesteInvalide(f"deux runs de jugement du même juge {modele!r}")
        if modele == juge:
            principal = run
    if principal is None:
        raise ManifesteInvalide(f"aucun run de jugement du juge de données {juge!r}")
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for ligne in principal.lire_jsonl(NOM_VERDICTS):
        if isinstance(ligne, dict) and "session_id" in ligne and "candidat_id" in ligne:
            index.setdefault((str(ligne["session_id"]), str(ligne["candidat_id"])), ligne)
    return principal, index


def _sha_verdicts(run: Run) -> str:
    """SHA-256 de `verdicts.jsonl` (celui d'un fichier vide si le run n'a rien jugé)."""
    chemin = run.dossier / NOM_VERDICTS
    return sha256_fichier(chemin) if chemin.is_file() else sha256_hex(b"")


def _verdict(
    ligne: Mapping[str, Any] | None, tache: str, seuils: Mapping[str, Any]
) -> Verdict | str:
    """Verdict retenu, ou motif d'ignorance (`sans_verdict`, `verdict_invalide`,
    `notes_invalides`)."""
    if ligne is None:
        return "sans_verdict"
    if ligne.get("verdict") not in ("accepte", "refuse") or ligne.get("tache") != tache:
        return "verdict_invalide"
    notes = ligne.get("notes")
    valeur = score(tache, notes) if isinstance(notes, dict) else None
    if valeur is None or not seuils:
        return "notes_invalides"
    accepte = ligne["verdict"] == "accepte" and all(
        isinstance(notes.get(c), int | float) and notes[c] >= s for c, s in seuils.items()
    )
    return Verdict(accepte, valeur, {k: float(v) for k, v in sorted(notes.items())})


def _cle(candidat: Mapping[str, Any], verdict: Verdict) -> tuple[Any, ...]:
    """Ordre de préférence : score décroissant, base, Mistral, température, graine, id."""
    return (
        -verdict.score,
        0 if str(candidat["source"]).startswith("slm:") else 1,
        float(candidat.get("temperature") or 0.0),
        int(candidat.get("graine") or 0),
        str(candidat["candidat_id"]),
    )


# --- Cible locale ---------------------------------------------------------------------------


def _cible_locale(
    connexion: Any,
    ligne: LigneEntrainement,
    candidat: Mapping[str, Any],
    base_slm: str,
    regle: RegleCible,
    tokeniseur: Tokeniseur,
) -> tuple[str, str]:
    """`(texte appris, jour)` du candidat `slm:` gagnant, recoupé dans le journal local."""
    appel_id = str(candidat["candidat_id"]).removeprefix("slm:")
    trouve = connexion.execute(
        "SELECT session_id, usage, generateur, requete, reponse_brute, sha256_reponse, statut, "
        "horodatage FROM appels WHERE appel_id = ?",
        (appel_id,),
    ).fetchone()
    if trouve is None:
        raise ProvenanceInvalide(f"candidat {candidat['candidat_id']} absent du journal local")
    session_id, usage, generateur, requete, brut, sha, statut, horodatage = trouve
    try:
        messages = json.loads(requete)["messages"]
    except (ValueError, KeyError, TypeError):
        messages = None
    if (
        session_id != ligne.meta.session_id
        or usage != USAGE_LOCAL
        or generateur != base_slm
        or statut != "ok"
        or brut is None
        or sha256_hex(bytes(brut)) != sha
        or messages != ligne.messages[:-1]
    ):
        raise ProvenanceInvalide(
            f"candidat {candidat['candidat_id']} : journal local non conforme (session, usage, "
            "générateur, statut, SHA de la réponse ou conversation)"
        )
    texte, motif = cible_apprise(
        bytes(brut).decode("utf-8"), ligne.tache, regle, tokeniseur.compter
    )
    if motif is not None:
        raise ProvenanceInvalide(f"candidat {candidat['candidat_id']} : cible refusée ({motif})")
    return texte, str(horodatage)[:10]


def _ligne_v2(
    ligne: LigneEntrainement,
    texte: str,
    jour: str,
    candidat: Mapping[str, Any],
    base_slm: str,
    registre: RegistreLicences,
    id_base: str,
) -> LigneEntrainement:
    sources = sorted({*ligne.meta.source, id_base})
    try:
        return LigneEntrainement(
            schema_version=2,
            messages=[*ligne.messages[:-1], {"role": "assistant", "content": texte}],
            tools=ligne.tools,
            tache=ligne.tache,
            meta=MetaLigne(
                generateur=base_slm,
                appel_ids=ligne.meta.appel_ids[:-1],
                session_id=ligne.meta.session_id,
                version_gabarit=ligne.meta.version_gabarit,
                version_extracteur=ligne.meta.version_extracteur,
                source=sources,
                licence=[registre.source(s).licence for s in sources],
                date=date.fromisoformat(jour),
                cible=CibleLigne(
                    source=base_slm,
                    appel_local_id=str(candidat["candidat_id"]).removeprefix("slm:"),
                ),
            ),
        )
    except (ValidationError, ValueError) as exc:
        raise ProvenanceInvalide(f"ligne {ligne.meta.session_id} non conforme : {exc}") from None


# --- Étape ---------------------------------------------------------------------------------


def lancer_selection(
    *,
    racine: str | Path,
    candidats_run_id: str,
    verdicts_run_ids: Sequence[str],
    taches: Collection[str],
    retirer: Collection[str],
    variante: str,
    registre: RegistreLicences,
    juge: str,
    tokeniseur: Tokeniseur | None = None,
    cr_min: int = CR_MIN,
    accepter_partiel: bool = False,
    consigner: Callable[[str], None] = print,
) -> ResultatSelection:
    """Construit `data/train/vN/` à cibles sélectionnées (voir le module).

    Avant tout run : `ValueError` (variante inconnue), `ManifesteInvalide` (Tâches, runs
    absents, d'un autre type, en cours, non `complet` sans `accepter_partiel`, ou incohérents,
    source de candidat non autorisée,
    tokenizer différent de celui des candidats), `SourceSansLicence` / `UsageInterdit`
    (Registre). Pendant le run, `ProvenanceInvalide` (journal local) ou `ManifesteInvalide`
    (moins de `cr_min` lignes CR) clôt le run en `partiel-erreur` sans rien écrire sous
    `data/train/`.
    """
    if variante not in VARIANTES:
        raise ValueError(f"variante inconnue : {variante!r} (attendu : {', '.join(VARIANTES)})")
    voulues, retirees = sorted(set(taches)), sorted(set(retirer))
    if not voulues or not set(voulues) <= set(TACHES_CANDIDATES):
        raise ManifesteInvalide(
            f"Tâches sélectionnées {', '.join(voulues) or '(aucune)'} : parmi "
            f"{', '.join(TACHES_CANDIDATES)} attendues"
        )
    if set(voulues) & set(retirees):
        raise ManifesteInvalide("une Tâche ne peut être à la fois sélectionnée et retirée")
    if not verdicts_run_ids:
        raise ManifesteInvalide("au moins un run de jugement (--verdicts) attendu")
    base = Path(racine).resolve()

    run_candidats = _run_termine(
        candidats_run_id, TYPE_RUN_CANDIDATS, base, accepter_partiel=accepter_partiel
    )
    config_c = run_candidats.manifeste.config
    base_slm = str(config_c.get("base"))
    absentes = [t for t in voulues if t not in (config_c.get("taches") or [])]
    if absentes:
        raise ManifesteInvalide(
            f"run {candidats_run_id} : aucun candidat pour la Tâche {', '.join(absentes)}"
        )
    regle = RegleCible.depuis_config(config_c.get("nettoyage"))
    build_run_id = str(config_c.get("build_run_id"))
    version_src, manifeste_src, octets = _jeu_sft(build_run_id, base)
    try:
        source_manifeste = ManifesteJeuEntrainement.model_validate(manifeste_src)
        lignes = [
            LigneEntrainement.model_validate_json(t) for t in octets.split(b"\n") if t.strip()
        ]
    except ValidationError as exc:
        raise ManifesteInvalide(f"jeu {version_src} : jeu SFT non conforme ({exc})") from None
    if source_manifeste.sous_ensemble is not None or source_manifeste.selection is not None:
        raise ManifesteInvalide(
            f"jeu {version_src} : restreint ou déjà sélectionné (repartir du jeu source)"
        )
    tokeniseur = tokeniseur or tokeniseur_du_modele(regle.modele.removeprefix("base:"), racine=base)
    if tokeniseur.sha256 != config_c.get("tokenizer_sha256"):
        raise ManifesteInvalide(
            f"tokenizer {tokeniseur.sha256} différent de celui des candidats "
            f"({config_c.get('tokenizer_sha256')})"
        )
    runs_juges = [
        _run_termine(r, TYPE_RUN_JUGER, base, accepter_partiel=accepter_partiel)
        for r in verdicts_run_ids
    ]
    partiels = sorted(
        r.run_id for r in (run_candidats, *runs_juges) if r.statut_courant() != "complet"
    )
    principal, verdicts = _verdicts(runs_juges, candidats_run_id, juge)
    description = principal.manifeste.config.get("juge") or {}
    seuils_juge: Mapping[str, Any] = description.get("seuils") or {}

    # Candidats : sources autorisées, indexés par session.
    ignores: Counter[str] = Counter()
    sans_verdict: Counter[str] = Counter()
    par_session: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidat in run_candidats.lire_jsonl(NOM_CANDIDATS):
        if not isinstance(candidat, dict) or candidat.get("tache") not in voulues:
            ignores["hors_taches"] += 1
            continue
        source, cid = str(candidat.get("source")), str(candidat.get("candidat_id"))
        if source.startswith(PREFIXE_IGNORE):
            ignores["source_openrouter"] += 1
            continue
        if not (
            (source == SOURCE_MISTRAL and cid.startswith("mistral:"))
            or (source == base_slm and cid.startswith("slm:"))
        ):
            raise ManifesteInvalide(
                f"candidat {cid} : source {source!r} non autorisée comme cible "
                f"(autorisées : {SOURCE_MISTRAL}, {base_slm})"
            )
        par_session[str(candidat.get("session_id"))].append(candidat)

    # Licences : avant tout run.
    gardees = [ligne for ligne in lignes if ligne.tache not in retirees]
    entree_base = registre.source_modele_base(base_slm)
    for id_source in sorted({s for ligne in gardees for s in ligne.meta.source} | {entree_base.id}):
        registre.exiger(id_source, variante)

    entrees = {
        "candidats": run_candidats.dossier / NOM_CANDIDATS,
        **{
            f"verdicts-{r.run_id}": r.dossier / NOM_VERDICTS
            for r in runs_juges
            if (r.dossier / NOM_VERDICTS).is_file()
        },
    }
    run = nouveau_run(
        TYPE_RUN_BUILD,
        "selection",
        {
            "selection": True,
            "build_run_id": build_run_id,
            "jeu_source_version": version_src,
            "candidats_run_id": candidats_run_id,
            "verdicts_run_ids": list(verdicts_run_ids),
            "juge": juge,
            "taches": voulues,
            "retirees": retirees,
            "variante": variante,
            "base": base_slm,
            "registre_sha256": registre.sha256,
            "accepter_partiel": accepter_partiel,
        },
        parents=[build_run_id, candidats_run_id, *verdicts_run_ids],
        entrees=entrees,
        racine=base,
    )
    connexion = None
    try:
        run.ecrire(NOM_DETAIL, b"")
        sorties: list[bytes] = []
        bilans: dict[str, dict[str, Any]] = {
            t: {"source": 0, "gagnants": Counter(), "ecartees": Counter(), "scores": []}
            for t in voulues
        }
        lignes_brutes = [t for t in octets.split(b"\n") if t.strip()]
        for rang, (brute, ligne) in enumerate(zip(lignes_brutes, lignes, strict=True)):
            if ligne.tache in retirees:
                continue
            if ligne.tache not in voulues:
                sorties.append(brute)
                continue
            bilan = bilans[ligne.tache]
            bilan["source"] += 1
            notes: list[tuple[dict[str, Any], Verdict]] = []
            candidats_ligne = par_session.pop(ligne.meta.session_id, [])
            for candidat in candidats_ligne:
                if candidat.get("tache") != ligne.tache:
                    ignores["tache_differente"] += 1
                    continue
                verdict = _verdict(
                    verdicts.get((ligne.meta.session_id, str(candidat["candidat_id"]))),
                    ligne.tache,
                    seuils_juge.get(ligne.tache) or {},
                )
                if isinstance(verdict, str):
                    ignores[verdict] += 1
                    if verdict == "sans_verdict":
                        sans_verdict[ligne.tache] += 1
                elif verdict.accepte:
                    notes.append((candidat, verdict))
                else:
                    ignores["refuse"] += 1
            detail: dict[str, Any] = {
                "rang": rang,
                "session_id": ligne.meta.session_id,
                "tache": ligne.tache,
                "acceptes": len(notes),
            }
            if not notes:
                motif = "aucun_accepte" if candidats_ligne else "sans_candidat"
                bilan["ecartees"][motif] += 1
                run.ajouter_jsonl(NOM_DETAIL, {**detail, "ecartee": motif})
                continue
            candidat, verdict = min(notes, key=lambda paire: _cle(*paire))
            cid = str(candidat["candidat_id"])
            if candidat["source"] == SOURCE_MISTRAL:
                if not ligne.meta.appel_ids or cid != f"mistral:{ligne.meta.appel_ids[-1]}":
                    raise ProvenanceInvalide(
                        f"candidat {cid} : pas la cible Mistral de la session "
                        f"{ligne.meta.session_id}"
                    )
                sorties.append(brute)
            else:
                if connexion is None:
                    connexion = ouvrir_sqlite_lecture(
                        dossier_var() / NOM_JOURNAL_LOCAL, "data", racine=base
                    )
                texte, jour = _cible_locale(connexion, ligne, candidat, base_slm, regle, tokeniseur)
                nouvelle = _ligne_v2(
                    ligne, texte, jour, candidat, base_slm, registre, entree_base.id
                )
                sorties.append(json_canonique(nouvelle.model_dump(mode="json")))
            bilan["gagnants"][str(candidat["source"])] += 1
            bilan["scores"].append(verdict.score)
            run.ajouter_jsonl(
                NOM_DETAIL,
                {
                    **detail,
                    "gagnant": cid,
                    "source": candidat["source"],
                    "temperature": candidat.get("temperature"),
                    "score": verdict.score,
                    "notes": verdict.notes,
                },
            )
        ignores["session_hors_jeu"] += sum(len(c) for c in par_session.values())

        retenues = {t: sum(b["gagnants"].values()) for t, b in bilans.items()}
        if "CR" in voulues and retenues["CR"] < cr_min:
            raise ManifesteInvalide(
                f"sélection : {retenues['CR']} ligne(s) CR retenue(s), au moins {cr_min} attendues"
            )
        avertissements = [f"Tâche {t} : aucune ligne retenue" for t in voulues if not retenues[t]]
        if partiels:
            avertissements.append(
                f"runs sources non complets admis (--accepter-partiel) : {', '.join(partiels)} ; "
                f"candidats sans verdict par Tâche : {dict(sorted(sans_verdict.items()))}"
            )
        if not sorties:
            raise ManifesteInvalide("sélection : jeu vide")
        contenu = b"".join(ligne + b"\n" for ligne in sorties)
        verifier_selection(contenu, octets, voulues, retirees)

        version, dossier = _creer_version(base)
        (dossier / NOM_TRAIN).write_bytes(contenu)
        comptes = Counter(str(json.loads(t)["tache"]) for t in sorties)
        par_tache = {
            t: BilanSelection(
                lignes_source=b["source"],
                retenues=retenues[t],
                gagnants=dict(sorted(b["gagnants"].items())),
                part_base=(
                    round(b["gagnants"][base_slm] / retenues[t], _DECIMALES)
                    if retenues[t]
                    else None
                ),
                score_moyen=(
                    round(sum(b["scores"]) / len(b["scores"]), _DECIMALES) if b["scores"] else None
                ),
                ecartees=dict(sorted(b["ecartees"].items())),
            )
            for t, b in sorted(bilans.items())
        }
        bloc = Selection(
            depuis_build=build_run_id,
            depuis_version=version_src,
            sha256_train_source=sha256_hex(octets),
            nettoyage_source=source_manifeste.nettoyage,
            candidats_run_id=candidats_run_id,
            sha256_candidats=sha256_fichier(run_candidats.dossier / NOM_CANDIDATS),
            verdicts={r.run_id: _sha_verdicts(r) for r in runs_juges},
            juge=juge,
            sha_grilles=dict(sorted((description.get("grilles") or {}).items())),
            base=base_slm,
            version_nettoyage=regle.version,
            tokenizer_sha256=tokeniseur.sha256,
            taches=voulues,
            retirees=retirees,
            par_tache=par_tache,
            candidats_ignores=dict(sorted((k, v) for k, v in ignores.items() if v)),
            sha256_detail=sha256_fichier(run.dossier / NOM_DETAIL),
            runs_partiels=partiels,
            sans_verdict_par_tache=dict(sorted(sans_verdict.items())),
            avertissements=avertissements,
        )
        manifeste = source_manifeste.model_copy(
            update={
                "schema_version": 2,
                "version": version,
                "run_id": run.run_id,
                "cree_le": date.today(),
                "variante": variante,
                "sha256_train": sha256_hex(contenu),
                "nb_lignes": len(sorties),
                "comptes_par_tache": dict(sorted(comptes.items())),
                "registre": registre.instantane(),
                "nettoyage": None,
                "selection": bloc,
            }
        )
        manifeste = ManifesteJeuEntrainement.model_validate(manifeste.model_dump(mode="json"))
        rapport = {
            "schema_version": 1,
            "version": version,
            "variante": variante,
            "depuis_build": build_run_id,
            "depuis_version": version_src,
            "sha256_train": manifeste.sha256_train,
            "nb_lignes_avant": len(lignes),
            "nb_lignes": manifeste.nb_lignes,
            "comptes_par_tache": manifeste.comptes_par_tache,
            "par_tache": {t: b.model_dump(mode="json") for t, b in par_tache.items()},
            "candidats_ignores": bloc.candidats_ignores,
            "avertissements": avertissements,
        }
        run.ecrire(NOM_RAPPORT, json_canonique(rapport) + b"\n")
        # MANIFEST en dernier : sa présence signale une version complète.
        temporaire = dossier / f"{NOM_MANIFEST}.tmp"
        temporaire.write_bytes(json_canonique(manifeste.model_dump(mode="json")) + b"\n")
        temporaire.replace(dossier / NOM_MANIFEST)
    except KeyboardInterrupt:
        run.terminer("interrompu", "interruption clavier")
        raise
    except BaseException as exc:
        run.terminer("partiel-erreur", f"{type(exc).__name__} : {exc}")
        raise
    finally:
        if connexion is not None:
            connexion.close()
    run.terminer("complet")
    consigner(
        f"sélection {version_src} → {version} ({variante}) : {len(lignes)} → "
        f"{manifeste.nb_lignes} lignes, sha256 {manifeste.sha256_train}"
    )
    return ResultatSelection(run=run, version=version, dossier=dossier, rapport=rapport)
