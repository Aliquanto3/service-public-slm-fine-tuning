"""Vérification, gel et contrôle du Jeu d'évaluation (SPEC §5.4, §6 ; AD-11, AD-25).

- `verifier_jeu` : items stricts, cassettes RD existantes et lisibles, empreinte
  `tools_list_sha256` conforme à `config/outils-mcp.toml`, arguments des appels attendus
  connus de l'outil, `valeurs_attendues.colonnes` présentes dans les lignes, puis
  composition comparée à SPEC §2. N'écrit rien.
- `gel` : vérifie, tire les deux échantillons (second juge, relecture) avec la graine,
  écrit l'export de revue puis `MANIFEST.json`, chacun par création exclusive.
- `verifier_manifeste` : recalcule les empreintes des fichiers listés.
- `jeu_gele_et_commite` : empreintes, puis suivi git, absence de modification et
  ascendance du commit qui a ajouté le manifeste (préalable à toute génération de Données
  d'entraînement).

Seuls `gel` (nouvelle version) et `slmsp mcp record` écrivent sous `eval/`.
"""

from __future__ import annotations

import json
import math
import random
import re
import subprocess
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from fractions import Fraction
from pathlib import Path
from typing import Final

from pydantic import ValidationError

from slmsp.core.artefacts import ArtefactExistant
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.config import env_sous_processus, racine_projet
from slmsp.core.erreurs import ConfigurationInvalide, ManifesteInvalide, SlmspError
from slmsp.core.items import (
    CODES,
    DIFFICULTES,
    LIBELLES,
    MOTIF_VERSION,
    Item,
    ItemCR,
    ItemInvalide,
    ItemQ,
    ItemRD,
    Jeu,
    lire_jeu,
    numero_id,
    resoudre_cassettes,
)
from slmsp.core.schemas.manifeste_jeu import (
    REGLE_EMPREINTE,
    Echantillons,
    FichierManifeste,
    ManifesteJeu,
)
from slmsp.core.texte import compter_mots
from slmsp.evaluation import config as cfg
from slmsp.mcp.cassettes import lire_cassette
from slmsp.mcp.erreurs import CassetteInvalide
from slmsp.mcp.outils import charger_config

DELAI_GIT: Final = 30.0
"""Délai maximal de chaque appel `git` (secondes)."""


class JeuNonConforme(SlmspError):
    """Le jeu ne peut pas être gelé : erreurs bloquantes (ou écarts en statut `relu`)."""

    def __init__(self, message: str, erreurs: Sequence[str] = ()):
        super().__init__(message)
        self.erreurs: tuple[str, ...] = tuple(erreurs)


# --- Empreintes ------------------------------------------------------------------------------


def sha256_lf(chemin: str | Path) -> str:
    """SHA-256 du contenu de `chemin` après normalisation des fins de ligne (CRLF → LF)."""
    return sha256_hex(Path(chemin).read_bytes().replace(b"\r\n", b"\n"))


def _relatif(chemin: Path, racine: Path) -> str:
    return chemin.resolve().relative_to(racine.resolve()).as_posix()


# --- Vérification ----------------------------------------------------------------------------


@dataclass
class RapportVerification:
    """Résultat de `verifier_jeu` : erreurs bloquantes et écarts de composition."""

    version: str
    racine: Path
    jeu: Jeu | None = None
    erreurs: list[str] = field(default_factory=list)
    ecarts: list[str] = field(default_factory=list)
    cassettes: list[Path] = field(default_factory=list)

    @property
    def items(self) -> tuple[Item, ...]:
        return self.jeu.items if self.jeu is not None else ()

    def composition(self) -> dict[str, dict[str, int]]:
        """Code → difficulté → nombre d'items (Tâches absentes comprises, à 0)."""
        comptes = Counter((item.code, item.difficulte) for item in self.items)
        return {code: {d: comptes[(code, d)] for d in DIFFICULTES} for code in CODES}

    def texte(self) -> str:
        """Rapport lisible, en texte brut."""
        lignes = [f"Jeu {self.version} : {len(self.items)} items stricts acceptés."]
        if self.items:
            par_code = Counter(item.code for item in self.items)
            lignes.append(
                "Items par Tâche : " + ", ".join(f"{c} {par_code[c]}" for c in CODES) + "."
            )
        lignes.append(f"Cassettes vérifiées : {len(self.cassettes)}.")
        lignes.append(f"Erreurs bloquantes : {len(self.erreurs)}.")
        lignes += [f"- {e}" for e in self.erreurs]
        lignes.append(f"Écarts de composition avec SPEC §2 : {len(self.ecarts)}.")
        lignes += [f"- {e}" for e in self.ecarts]
        return "\n".join(lignes)


def _erreurs_colonnes(item: ItemRD) -> list[str]:
    """`valeurs_attendues.colonnes` : liste non vide de noms présents dans une des `lignes`."""
    valeurs = item.valeurs_attendues
    if not isinstance(valeurs, Mapping) or "colonnes" not in valeurs:
        return []
    colonnes = valeurs["colonnes"]
    champ = f"{item.id} : `valeurs_attendues.colonnes`"
    if (
        not isinstance(colonnes, list)
        or not colonnes
        or not all(isinstance(c, str) for c in colonnes)
    ):
        return [f"{champ} : liste non vide de noms de colonnes attendue"]
    lignes = valeurs.get("lignes")
    connues = {
        cle
        for ligne in (lignes if isinstance(lignes, list) else [])
        if isinstance(ligne, Mapping)
        for cle in ligne
    }
    return [f"{champ} : colonne absente des lignes : {c}" for c in colonnes if c not in connues]


def _verifier_rd(rapport: RapportVerification, jeu: Jeu, racine: Path) -> None:
    rd = [item for item in jeu.items if isinstance(item, ItemRD)]
    if not rd:
        return
    chemin_config = cfg.chemin_config_outils(racine)
    try:
        config = charger_config(chemin_config)
    except ConfigurationInvalide as exc:
        rapport.erreurs.append(f"config des outils MCP invalide : {exc}")
        return
    proprietes = {
        outil.nom: set((outil.parametres.get("properties") or {}).keys()) for outil in config.outils
    }
    vues: set[Path] = set()
    for item in rd:
        rapport.erreurs.extend(_erreurs_colonnes(item))
        try:
            chemins = resoudre_cassettes(jeu, item)
        except ItemInvalide as exc:
            rapport.erreurs.extend(exc.erreurs or [str(exc)])
            continue
        if not chemins and item.mode != "hors-ligne":
            rapport.erreurs.append(f"{item.id} : `cassettes` : aucune cassette (mode {item.mode})")
        for relatif, chemin in zip(item.cassettes, chemins, strict=True):
            if not chemin.is_file():
                rapport.erreurs.append(f"{item.id} : `cassettes` : cassette absente : {relatif}")
                continue
            try:
                cassette = lire_cassette(chemin)
            except CassetteInvalide as exc:
                rapport.erreurs.append(f"{item.id} : `cassettes` : {exc}")
                continue
            if cassette.tools_list_sha256 != config.tools_list_sha256:
                rapport.erreurs.append(
                    f"{item.id} : `cassettes` : {relatif} : `tools_list_sha256` différent de "
                    f"{chemin_config.name}"
                )
            if chemin not in vues:
                vues.add(chemin)
                rapport.cassettes.append(chemin)
        for i, appel in enumerate(item.appels_attendus or []):
            connues = proprietes.get(appel.outil)
            if connues is None:
                rapport.erreurs.append(
                    f"{item.id} : `appels_attendus.{i}.outil` : outil absent de "
                    f"{chemin_config.name} : {appel.outil}"
                )
                continue
            noms = set(appel.arguments) | set(appel.regles.arguments if appel.regles else ())
            for nom in sorted(noms - connues):
                rapport.erreurs.append(
                    f"{item.id} : `appels_attendus.{i}.arguments` : argument inconnu de "
                    f"{appel.outil} : {nom}"
                )


def _ecart(libelle: str, reel: int, cible: int, *, minimum: bool = False) -> str | None:
    if (reel >= cible) if minimum else (reel == cible):
        return None
    attendu = f"≥ {cible}" if minimum else str(cible)
    return f"{libelle} : {reel} (attendu {attendu})"


def producteurs_rd(item: ItemRD) -> list[str]:
    """Producteurs d'un item RD : `producteurs`, sinon `producteur`, sinon
    `reponse_reference.jeu_principal.producteur` (même règle que l'outil de construction)."""
    if item.producteurs:
        return [p for p in item.producteurs if p]
    if item.producteur:
        return [item.producteur]
    reference = item.reponse_reference
    principal = reference.get("jeu_principal") if isinstance(reference, dict) else None
    if isinstance(principal, dict) and principal.get("producteur"):
        return [str(principal["producteur"])]
    return []


def amorce_reelle(item: ItemQ) -> bool:
    """Vrai si l'item Q vient d'une amorce réelle d'un corpus AgentPublic."""
    if not (item.amorce_usager and item.amorce_usager.strip()):
        return False
    for provenance in item.provenance:
        donnees = provenance.model_dump()
        for champ in ("source", "url", "depot"):
            valeur = donnees.get(champ)
            if isinstance(valeur, str) and any(c in valeur for c in cfg.CORPUS_AMORCES):
                return True
    return False


def _mots_hors_consigne(valeur: object) -> int:
    if isinstance(valeur, str):
        return compter_mots(valeur)
    if isinstance(valeur, dict):
        return sum(_mots_hors_consigne(v) for k, v in valeur.items() if k != "consigne")
    if isinstance(valeur, list):
        return sum(_mots_hors_consigne(v) for v in valeur)
    return 0


def ecarts_composition(items: Sequence[Item], version: str = "v1.1") -> list[str]:
    """Écarts de `items` avec la composition visée de `version` (liste vide si conforme).

    SPEC §2 pour `vN`, `CIBLES_DEV` (spec O4) pour `devN`.
    """
    cibles = cfg.cibles_jeu(version)
    ecarts: list[str | None] = []
    comptes = Counter((item.code, item.difficulte) for item in items)
    for code in CODES:
        for difficulte, cible in zip(DIFFICULTES, cibles.taches[code], strict=True):
            ecarts.append(_ecart(f"{code} {difficulte}", comptes[(code, difficulte)], cible))
    q = [item for item in items if isinstance(item, ItemQ)]
    rd = [item for item in items if isinstance(item, ItemRD)]
    cr = [item for item in items if isinstance(item, ItemCR)]
    minimum = not cibles.exactes
    ecarts.append(
        _ecart(
            "Q sans réponse",
            sum(item.sans_reponse for item in q),
            cibles.q_sans_reponse,
            minimum=minimum,
        )
    )
    cible_amorces = math.ceil(cibles.q_part_amorces * sum(cibles.taches["Q"]))
    ecarts.append(
        _ecart(
            "Q issus d'amorces réelles",
            sum(amorce_reelle(item) for item in q),
            cible_amorces,
            minimum=True,
        )
    )
    ecarts.append(
        _ecart(
            "RD demandes de valeurs",
            sum(bool(item.valeurs_attendues) for item in rd),
            cibles.rd_valeurs,
            minimum=minimum,
        )
    )
    ecarts.append(
        _ecart(
            "RD cas de repli",
            sum(item.mode == "repli" for item in rd),
            cibles.rd_repli,
            minimum=minimum,
        )
    )
    producteurs = {p for item in rd for p in producteurs_rd(item)}
    ecarts.append(
        _ecart("RD producteurs distincts", len(producteurs), cibles.rd_producteurs, minimum=True)
    )
    longues = sum(_mots_hors_consigne(item.entree) > cfg.SEUIL_CR_LONGUE_MOTS for item in cr)
    ecarts.append(
        _ecart(
            f"CR de plus de {cfg.SEUIL_CR_LONGUE_MOTS} mots",
            longues,
            cibles.cr_longues,
            minimum=minimum,
        )
    )
    total_cible = sum(sum(cibles.taches[c]) for c in cfg.TACHES_THEMATIQUES)
    themes = Counter(item.theme for item in items if item.code in cfg.TACHES_THEMATIQUES)
    for theme, part in cfg.PARTS_THEMES.items():
        cible = round(part * total_cible)
        ecarts.append(
            _ecart(f"thème {theme} ({', '.join(cfg.TACHES_THEMATIQUES)})", themes[theme], cible)
        )
    return [e for e in ecarts if e is not None]


def _version_gelable(version: str) -> None:
    if not isinstance(version, str) or not re.fullmatch(MOTIF_VERSION, version):
        raise ValueError(f"version de jeu invalide : {version!r} (attendu : vN, vN.M ou devN)")


def verifier_jeu(version: str, racine: str | Path | None = None) -> RapportVerification:
    """Vérifie le jeu `version` sans rien écrire (voir le module)."""
    _version_gelable(version)
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    rapport = RapportVerification(version=version, racine=base)
    chemin_items = cfg.dossier_jeu(base, version) / cfg.NOM_ITEMS
    if not chemin_items.is_file():
        rapport.erreurs.append(f"fichier d'items absent : {chemin_items}")
        return rapport
    try:
        rapport.jeu = lire_jeu(version, base)
    except ItemInvalide as exc:
        rapport.erreurs.extend(exc.erreurs or [str(exc)])
        return rapport
    _verifier_rd(rapport, rapport.jeu, base)
    rapport.ecarts = ecarts_composition(rapport.items, version)
    return rapport


# --- Échantillons ----------------------------------------------------------------------------


def _taille(n: int, part: Fraction, minimum: int) -> int:
    return min(n, max(minimum, math.ceil(part * n)))


def _tirer(
    nom: str, strates: dict[str, list[str]], graine: int, part: Fraction, minimum: int
) -> list[str]:
    retenus: list[str] = []
    for strate in sorted(strates):
        identifiants = sorted(strates[strate], key=numero_id)
        k = _taille(len(identifiants), part, minimum)
        tirage = random.Random(f"{graine}:{nom}:{strate}")
        retenus.extend(tirage.sample(identifiants, k))
    return sorted(retenus, key=numero_id)


def jeu_sans_second_juge(jeu: str | None) -> bool:
    """Vrai pour tout jeu de développement (`dev*`) : le second juge Mistral n'y tourne jamais."""
    return jeu is not None and jeu.startswith("dev")


def tirer_echantillons(
    items: Iterable[Item], graine: int, *, second_juge: bool = True
) -> Echantillons:
    """Échantillons du second juge et de la relecture, déterministes pour une graine.

    Second juge : par Tâche jugée présente, `min(n, max(3, ceil(n / 5)))` items. Relecture :
    par strate Tâche × difficulté, `min(n, max(1, ceil(n / 5)))`. Chaque strate est tirée
    par `random.Random(f"{graine}:{nom}:{strate}")` sur ses identifiants triés. Avec
    `second_juge=False` (jeux `dev*`, story 15.4), l'échantillon du second juge est vide ; la
    relecture est inchangée.
    """
    items = list(items)
    par_tache: dict[str, list[str]] = {}
    par_strate: dict[str, list[str]] = {}
    for item in items:
        if item.code in cfg.TACHES_JUGEES:
            par_tache.setdefault(item.code, []).append(item.id)
        par_strate.setdefault(f"{item.code}/{item.difficulte}", []).append(item.id)
    return Echantillons(
        graine=graine,
        second_juge=(
            _tirer("second_juge", par_tache, graine, cfg.PART_SECOND_JUGE, cfg.MIN_SECOND_JUGE)
            if second_juge
            else []
        ),
        relecture=_tirer("relecture", par_strate, graine, cfg.PART_RELECTURE, cfg.MIN_RELECTURE),
    )


# --- Gel -------------------------------------------------------------------------------------


def rendre_revue(manifeste: ManifesteJeu, jeu: Jeu) -> str:
    """Export Markdown de l'échantillon de relecture (SPEC §5.4)."""
    par_id = {item.id: item for item in jeu.items}
    ids = manifeste.echantillons.relecture
    lignes = [
        f"# Échantillon de relecture du Jeu d'évaluation {manifeste.version}",
        "",
        f"- Statut du gel : `{manifeste.statut}`",
        f"- Gelé le : {manifeste.cree_le.isoformat()}",
        f"- Graine : {manifeste.echantillons.graine}",
        f"- Items : {len(ids)} sur {manifeste.nb_items} ({float(cfg.PART_RELECTURE * 100):g} % "
        f"stratifié Tâche × difficulté, au moins {cfg.MIN_RELECTURE} par strate)",
        "",
        "Les scores restent « non relus » tant que la relecture n'est pas validée (FR-25).",
        "",
    ]
    for identifiant in ids:
        item = par_id[identifiant]
        lignes += [
            f"## {item.id} — {LIBELLES[item.code]} ({item.difficulte}, thème `{item.theme}`)",
            "",
            "- [ ] Relu",
            "- Remarques :",
            "",
            "```json",
            json.dumps(
                item.model_dump(mode="json", exclude_none=True), ensure_ascii=False, indent=1
            ),
            "```",
            "",
        ]
    return "\n".join(lignes)


def _ecrire_exclusif(chemin: Path, donnees: bytes) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    try:
        with chemin.open("xb") as flux:
            flux.write(donnees)
    except FileExistsError:
        raise ArtefactExistant(f"{chemin} existe déjà : un gel n'est jamais réécrit") from None


def _retenu_par_tous(ligne: Mapping[str, object]) -> bool:
    """Décision `retenu` et, pour au moins deux juges, un verdict sans aucun grief."""
    juges = ligne.get("juges")
    if ligne.get("decision") != "retenu" or not isinstance(juges, Mapping) or len(juges) < 2:
        return False
    return all(
        isinstance(v, Mapping)
        and v.get("coherent") is True
        and v.get("ambigu") is False
        and v.get("fait_absent_de_la_source") is False
        for v in juges.values()
    )


def ecarts_verdicts_croises(chemin_items: Path, chemin_verdicts: Path) -> list[str]:
    """Items sans dernier verdict croisé « retenu » par les juges sur leur empreinte courante
    (JSON canonique de la ligne d'`items.jsonl`) et avec la consigne courante (gel `relu-llm`,
    revue O4c). Liste vide : tous retenus."""
    if not chemin_verdicts.is_file():
        return [f"verdicts croisés absents : {chemin_verdicts}"]
    derniers: dict[str, Mapping[str, object]] = {}
    for rang, ligne in enumerate(chemin_verdicts.read_text(encoding="utf-8").splitlines(), 1):
        if not ligne.strip():
            continue
        try:
            valeur = json.loads(ligne)
        except json.JSONDecodeError:
            return [f"{chemin_verdicts} ligne {rang} : JSON invalide"]
        if isinstance(valeur, dict) and "item_id" in valeur:
            derniers[str(valeur["item_id"])] = valeur
    ecarts: list[str] = []
    for ligne in chemin_items.read_text(encoding="utf-8").splitlines():
        if not ligne.strip():
            continue
        item = json.loads(ligne)
        identifiant = str(item.get("id"))
        verdict = derniers.get(identifiant)
        if verdict is None:
            motif = "aucun verdict croisé"
        elif verdict.get("item_sha256") != sha256_hex(json_canonique(item)):
            motif = "verdict croisé d'une version antérieure de l'item"
        elif verdict.get("version_prompt") != cfg.VERSION_CONSIGNE_CROISEE:
            motif = (
                f"verdict croisé de la consigne {verdict.get('version_prompt')!r} "
                f"(attendu {cfg.VERSION_CONSIGNE_CROISEE})"
            )
        elif not _retenu_par_tous(verdict):
            motifs = verdict.get("motifs")
            detail = "; ".join(str(m) for m in motifs) if isinstance(motifs, list) else ""
            motif = f"contre-vérification croisée {verdict.get('decision')!r}" + (
                f" ({detail})" if detail else ""
            )
        else:
            continue
        ecarts.append(f"{identifiant} : {motif}")
    return ecarts


def gel(
    version: str,
    statut: str,
    graine: int,
    racine: str | Path | None = None,
    *,
    maintenant: datetime | None = None,
    date_reference: date | None = None,
) -> ManifesteJeu:
    """Gèle le jeu `version` : écrit l'export de revue puis `MANIFEST.json`.

    `date_reference` (facultative) est l'ancre de date des références, inscrite dans le
    manifeste ; elle ne peut pas être postérieure à la date du gel (`ValueError`, rien
    n'est écrit). Lève `ArtefactExistant` si le manifeste ou l'export existe déjà,
    `JeuNonConforme` sur une erreur bloquante (ou un écart de composition en statut `relu`).
    """
    if statut not in cfg.STATUTS_GEL:
        raise ValueError(
            f"statut de gel inconnu : {statut!r} (attendu : {', '.join(cfg.STATUTS_GEL)})"
        )
    if isinstance(graine, bool) or not isinstance(graine, int):
        raise ValueError(f"graine entière attendue (reçu {graine!r})")
    cree_le = maintenant or datetime.now().astimezone()
    if date_reference is not None:
        if isinstance(date_reference, datetime) or not isinstance(date_reference, date):
            raise ValueError(f"date de référence attendue (reçu {date_reference!r})")
        if date_reference > cree_le.date():
            raise ValueError(
                f"date de référence {date_reference.isoformat()} postérieure à la date du gel "
                f"({cree_le.date().isoformat()})"
            )
    _version_gelable(version)
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    chemin_manifeste = cfg.chemin_manifeste(base, version)
    chemin_revue = cfg.chemin_revue(base, version)
    for chemin in (chemin_manifeste, chemin_revue):
        if chemin.exists():
            raise ArtefactExistant(f"{chemin} existe déjà : gel refusé")

    rapport = verifier_jeu(version, base)
    bloquants = list(rapport.erreurs)
    if statut in cfg.STATUTS_BLOQUANTS:
        bloquants += [f"écart de composition (statut {statut}) : {e}" for e in rapport.ecarts]
    if statut == cfg.STATUT_RELU_LLM and rapport.jeu is not None:
        bloquants += ecarts_verdicts_croises(
            rapport.jeu.chemin_items, cfg.chemin_verdicts_croises(base, version)
        )
    grille = cfg.chemin_grille(base)
    if not grille.is_file():
        bloquants.append(f"grille du Juge absente : {grille}")
    if bloquants or rapport.jeu is None:
        raise JeuNonConforme(
            f"gel de {version} refusé : {len(bloquants)} erreur(s) bloquante(s) :\n"
            + "\n".join(f"- {e}" for e in bloquants),
            bloquants,
        )

    jeu = rapport.jeu
    fichiers = [
        FichierManifeste(
            chemin=_relatif(jeu.chemin_items, base),
            role="items",
            sha256=sha256_lf(jeu.chemin_items),
        )
    ]
    for cassette in sorted(rapport.cassettes, key=lambda c: _relatif(c, base)):
        fichiers.append(
            FichierManifeste(
                chemin=_relatif(cassette, base), role="cassette", sha256=sha256_lf(cassette)
            )
        )
    fichiers.append(
        FichierManifeste(chemin=_relatif(grille, base), role="grille", sha256=sha256_lf(grille))
    )
    manifeste = ManifesteJeu(
        version=version,
        statut=statut,  # type: ignore[arg-type]
        cree_le=cree_le,
        regle_empreinte=REGLE_EMPREINTE,
        fichiers=fichiers,
        nb_items=len(jeu.items),
        composition=rapport.composition(),
        ecarts=rapport.ecarts,
        echantillons=tirer_echantillons(
            jeu.items, graine, second_juge=not jeu_sans_second_juge(version)
        ),
        date_reference=date_reference,
    )
    revue = rendre_revue(manifeste, jeu).encode("utf-8")
    contenu = json_canonique(manifeste.model_dump(mode="json")) + b"\n"
    _ecrire_exclusif(chemin_revue, revue)
    try:
        _ecrire_exclusif(chemin_manifeste, contenu)
    except BaseException:
        # Sans manifeste, l'export orphelin bloquerait toute nouvelle tentative de gel.
        chemin_revue.unlink(missing_ok=True)
        raise
    return manifeste


# --- Contrôles du gel ------------------------------------------------------------------------


def lire_manifeste(version: str, racine: str | Path | None = None) -> ManifesteJeu:
    """Lit `eval/jeu/<version>/MANIFEST.json` ; lève `ManifesteInvalide` s'il est absent,
    illisible, invalide ou d'une autre version."""
    _version_gelable(version)
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    chemin = cfg.chemin_manifeste(base, version)
    try:
        brut = chemin.read_bytes()
    except OSError as exc:
        raise ManifesteInvalide(
            f"manifeste du jeu {version} absent ou illisible : {chemin} ({type(exc).__name__})"
        ) from None
    try:
        manifeste = ManifesteJeu.model_validate_json(brut)
    except ValidationError as exc:
        champs = sorted({".".join(str(p) for p in e["loc"]) or "(racine)" for e in exc.errors()})
        raise ManifesteInvalide(f"{chemin} : manifeste invalide ({', '.join(champs)})") from None
    if manifeste.version != version:
        raise ManifesteInvalide(f"{chemin} : version {manifeste.version!r} au lieu de {version!r}")
    return manifeste


def verifier_manifeste(version: str, racine: str | Path | None = None) -> ManifesteJeu:
    """Recalcule l'empreinte de chaque fichier listé par le manifeste de `version`.

    Lève `ManifesteInvalide` (code 4) si le manifeste est invalide, s'il ne liste pas
    d'items, ou si un fichier est absent, hors de `eval/` ou modifié.
    """
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    manifeste = lire_manifeste(version, base)
    base_eval = (base / "eval").resolve()
    ecarts: list[str] = []
    if not any(f.role == "items" for f in manifeste.fichiers):
        ecarts.append("aucun fichier d'items listé")
    for fichier in manifeste.fichiers:
        chemin = (base / fichier.chemin).resolve()
        if not chemin.is_relative_to(base_eval):
            ecarts.append(f"{fichier.chemin} : hors de eval/")
        elif not chemin.is_file():
            ecarts.append(f"{fichier.chemin} : fichier absent")
        elif sha256_lf(chemin) != fichier.sha256:
            ecarts.append(f"{fichier.chemin} : empreinte SHA-256 différente du manifeste")
    if ecarts:
        raise ManifesteInvalide(
            f"jeu {version} altéré depuis le gel :\n" + "\n".join(f"- {e}" for e in ecarts)
        )
    return manifeste


@dataclass(frozen=True)
class JeuGele:
    """Jeu gelé, intact et commité : manifeste et commit qui a ajouté le manifeste."""

    manifeste: ManifesteJeu
    commit_gel: str


def _git(racine: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-c", "core.quotepath=off", *arguments],
            cwd=racine,
            env=env_sous_processus(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=DELAI_GIT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise ManifesteInvalide(
            f"git indisponible ({type(exc).__name__}) : gel invérifiable"
        ) from None


def jeu_gele_et_commite(version: str, racine: str | Path | None = None) -> JeuGele:
    """Vérifie que le jeu `version` est gelé, intact et commité dans l'historique de `HEAD`.

    Contrôles : empreintes (`verifier_manifeste`) ; manifeste et fichiers listés suivis dans
    `HEAD` ; `git diff --quiet HEAD --` sur ces seuls chemins ; commit d'ajout du manifeste
    ancêtre de `HEAD`. Lève `ManifesteInvalide` sinon.
    """
    base = (Path(racine) if racine is not None else racine_projet()).resolve()
    manifeste = verifier_manifeste(version, base)
    chemin_manifeste = _relatif(cfg.chemin_manifeste(base, version), base)
    chemins = [chemin_manifeste, *(f.chemin for f in manifeste.fichiers)]

    racine_git = _git(base, "rev-parse", "--show-toplevel")
    if racine_git.returncode != 0:
        raise ManifesteInvalide(f"{base} n'est pas un dépôt git : gel du jeu {version} non commité")
    depot = Path(racine_git.stdout.strip()).resolve()
    if depot != base:
        # Chemins relatifs à la racine du dépôt git.
        chemins = [_relatif(base / c, depot) for c in chemins]
        chemin_manifeste = chemins[0]

    suivis = _git(depot, "ls-tree", "-r", "--name-only", "HEAD", "--", *chemins)
    if suivis.returncode != 0:
        raise ManifesteInvalide(f"jeu {version} non commité (HEAD illisible)")
    presents = {ligne.strip() for ligne in suivis.stdout.splitlines() if ligne.strip()}
    absents = [c for c in chemins if c not in presents]
    if absents:
        raise ManifesteInvalide(
            f"jeu {version} non commité : fichiers absents de HEAD : " + ", ".join(absents)
        )

    diff = _git(depot, "diff", "--quiet", "HEAD", "--", *chemins)
    if diff.returncode != 0:
        raise ManifesteInvalide(
            f"jeu {version} modifié depuis le dernier commit (git diff HEAD non vide)"
        )

    ajouts = _git(depot, "log", "--all", "--diff-filter=A", "--format=%H", "--", chemin_manifeste)
    commits = [ligne.strip() for ligne in ajouts.stdout.splitlines() if ligne.strip()]
    if ajouts.returncode != 0 or not commits:
        raise ManifesteInvalide(f"jeu {version} : commit d'ajout du manifeste introuvable")
    for commit in commits:
        if _git(depot, "merge-base", "--is-ancestor", commit, "HEAD").returncode == 0:
            break
    else:
        raise ManifesteInvalide(f"jeu {version} : le commit de gel n'est pas un ancêtre de HEAD")
    # Le manifeste de HEAD doit être celui du commit de gel (jamais réécrit depuis).
    blobs = [
        _git(depot, "rev-parse", f"{reference}:{chemin_manifeste}")
        for reference in (commit, "HEAD")
    ]
    if any(b.returncode != 0 for b in blobs) or blobs[0].stdout.strip() != blobs[1].stdout.strip():
        raise ManifesteInvalide(
            f"jeu {version} : manifeste réécrit depuis le commit de gel {commit[:12]}"
        )
    return JeuGele(manifeste=manifeste, commit_gel=commit)


__all__ = [
    "JeuGele",
    "JeuNonConforme",
    "RapportVerification",
    "amorce_reelle",
    "ecarts_composition",
    "gel",
    "jeu_gele_et_commite",
    "lire_manifeste",
    "producteurs_rd",
    "rendre_revue",
    "sha256_lf",
    "jeu_sans_second_juge",
    "tirer_echantillons",
    "verifier_jeu",
    "verifier_manifeste",
]
