"""Chargement d'un Run : jeu construit, provenance, contraintes du modèle, pré-tokenisation.

Toutes les lectures passent par le lecteur contrôlé `train` (AD-24) : `data/train/<v>/`,
`models/` et, en lecture seule, le journal `appels-mistral.sqlite`. Le jeu n'est accepté que
si son `MANIFEST.json` déclare un run `data-build` et si le SHA-256 du fichier lu est celui du
MANIFEST ; chaque `appel_id` est recontrôlé contre le journal (`usage = generation`,
`statut = ok`). Sans jeu construit, `JeuAbsent` : aucun jeu de dépannage, jamais.

Contrat provisoire, en attendant `LigneEntrainement` et `ManifesteJeuEntrainement` de la
story 9.6 : MANIFEST `{version, type_run = "data-build", run_id, sha256_<fichier>}` ; lignes
`{messages, tools, tache, meta{appel_ids, …}}`. Les clés supplémentaires sont acceptées.
Paires ORPO (`preferences.jsonl`, story 9.7, provisoire) : `{prompt, chosen, rejected, tools,
tache, meta{appel_ids}}`, `prompt` étant la liste des messages avant la réponse, `chosen` et
`rejected` les messages de la réponse retenue et de la réponse rejetée.

La pré-tokenisation applique `train.masque` (implémentation unique) puis coupe `input_ids`
et `labels` **ensemble** à la longueur maximale ; un exemple sans aucun token supervisé
après coupe est écarté et compté.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

from slmsp.core.artefacts import (
    NOM_JOURNAL_MISTRAL,
    chemin_autorise,
    lire,
    ouvrir_sqlite_lecture,
)
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ConfigurationInvalide, ManifesteInvalide, SlmspError
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.core.schemas.run import MOTIF_RUN_ID
from slmsp.core.var import dossier_var
from slmsp.train import environnement
from slmsp.train.masque import IGNORE, calculer_masque
from slmsp.train.rendu import apply_chat_template

NOM_MANIFESTE_JEU: Final = "MANIFEST.json"
NOM_TRAIN: Final = "train.jsonl"
NOM_PREFERENCES: Final = "preferences.jsonl"
"""Paires ORPO (story 9.7, format provisoire)."""
TAILLE_REQUETE: Final = 500
"""`appel_id` par requête SQL (limite de variables de SQLite)."""


class JeuAbsent(SlmspError):
    """Aucun jeu construit pour la version demandée : le Run est consigné comme bloqué."""


class _Libre(BaseModel):
    model_config = ConfigDict(extra="allow")


class _Manifeste(_Libre):
    version: str
    type_run: Literal["data-build"]
    run_id: Annotated[str, StringConstraints(pattern=MOTIF_RUN_ID)]


class _Meta(_Libre):
    appel_ids: list[str] = Field(min_length=1)


class _Ligne(_Libre):
    messages: list[dict[str, Any]] = Field(min_length=2)
    tools: list[dict[str, Any]] | None = None
    tache: str
    meta: _Meta


class _Paire(_Libre):
    """Paire de préférence ORPO (format provisoire, story 9.7)."""

    prompt: list[dict[str, Any]] = Field(min_length=1)
    chosen: list[dict[str, Any]] = Field(min_length=1)
    rejected: list[dict[str, Any]] = Field(min_length=1)
    tools: list[dict[str, Any]] | None = None
    tache: str
    meta: _Meta


@dataclass
class Jeu:
    """Jeu construit et vérifié (`data/train/<version>/`)."""

    version: str
    fichier: str
    sha256: str
    manifeste: dict[str, Any]
    lignes: list[_Ligne] | list[_Paire] = field(repr=False)

    def ligne(self) -> dict[str, Any]:
        """Résumé consigné dans le run."""
        return {
            "version": self.version,
            "fichier": self.fichier,
            "sha256": self.sha256,
            "run_build": self.manifeste.get("run_id"),
            "exemples": len(self.lignes),
        }


def dossier_jeu(version: str, *, racine: str | Path | None = None) -> Path:
    """`<racine>/data/train/<version>/` (non résolu)."""
    base = Path(racine) if racine is not None else racine_projet()
    return base / "data" / "train" / version


def charger_jeu(version: str, *, racine: str | Path | None = None, fichier: str = NOM_TRAIN) -> Jeu:
    """Jeu `version` lu par le lecteur `train`, après contrôle du MANIFEST et du SHA-256.

    Lève `JeuAbsent` si le dossier, le MANIFEST ou le fichier manque, `ManifesteInvalide`
    si le MANIFEST n'est pas celui d'un run `data-build` de cette version, si le SHA diffère
    ou si une ligne n'est pas conforme, `LectureInterdite` hors de la liste d'accès.
    """
    dossier = chemin_autorise(dossier_jeu(version, racine=racine), "train", racine=racine)
    manifeste_chemin, donnees_chemin = dossier / NOM_MANIFESTE_JEU, dossier / fichier
    if not manifeste_chemin.is_file() or not donnees_chemin.is_file():
        raise JeuAbsent(
            f"aucun jeu construit sous {dossier} ({NOM_MANIFESTE_JEU} et {fichier} requis, "
            "produits par `slmsp data build`) ; aucun jeu de dépannage n'est utilisé"
        )
    try:
        brut_manifeste = json.loads(lire(manifeste_chemin, "train", racine=racine))
        manifeste = _Manifeste.model_validate(brut_manifeste)
    except (json.JSONDecodeError, UnicodeDecodeError, ValidationError) as exc:
        raise ManifesteInvalide(
            f"{manifeste_chemin} : MANIFEST invalide ou non issu d'un run data-build ({exc})"
        ) from None
    if manifeste.version != version:
        raise ManifesteInvalide(
            f"{manifeste_chemin} : version {manifeste.version!r} au lieu de {version!r}"
        )
    cle_sha = f"sha256_{Path(fichier).stem}"
    attendu = brut_manifeste.get(cle_sha)
    brut = lire(donnees_chemin, "train", racine=racine)
    sha = hashlib.sha256(brut).hexdigest()
    if attendu != sha:
        raise ManifesteInvalide(
            f"{donnees_chemin} : SHA-256 {sha} différent de « {cle_sha} » du MANIFEST ({attendu})"
        )
    schema = _Paire if fichier == NOM_PREFERENCES else _Ligne
    lignes: list[Any] = []
    for numero, texte in enumerate(brut.decode("utf-8").splitlines(), start=1):
        if not texte.strip():
            continue
        try:
            lignes.append(schema.model_validate_json(texte))
        except ValidationError as exc:
            raise ManifesteInvalide(
                f"{donnees_chemin}:{numero} : ligne non conforme ({exc})"
            ) from None
    if not lignes:
        raise ManifesteInvalide(f"{donnees_chemin} : jeu vide")
    return Jeu(version, fichier, sha, brut_manifeste, lignes)


def recontroler_appel_ids(
    lignes: Sequence[_Ligne | _Paire],
    *,
    journal: str | Path | None = None,
    racine: str | Path | None = None,
) -> int:
    """Vérifie chaque `appel_id` dans le journal Mistral ; renvoie le nombre d'appels vus.

    Lève `ManifesteInvalide` pour un journal absent, un `appel_id` inconnu, d'un `usage`
    autre que `generation` ou d'un `statut` autre que `ok`.
    """
    ids = sorted({a for ligne in lignes for a in ligne.meta.appel_ids})
    chemin = Path(journal) if journal is not None else dossier_var() / NOM_JOURNAL_MISTRAL
    if not chemin_autorise(chemin, "train", racine=racine).is_file():
        raise ManifesteInvalide(f"journal Mistral absent : {chemin} (appel_ids non vérifiables)")
    vus: dict[str, tuple[str, str]] = {}
    connexion = ouvrir_sqlite_lecture(chemin, "train", racine=racine)
    try:
        for debut in range(0, len(ids), TAILLE_REQUETE):
            lot = ids[debut : debut + TAILLE_REQUETE]
            marques = ", ".join("?" * len(lot))
            requete = f"SELECT appel_id, usage, statut FROM appels WHERE appel_id IN ({marques})"
            for appel_id, usage, statut in connexion.execute(requete, lot):
                vus[str(appel_id)] = (str(usage), str(statut))
    finally:
        connexion.close()
    inconnus = [a for a in ids if a not in vus]
    if inconnus:
        raise ManifesteInvalide(
            f"{len(inconnus)} appel_id absent(s) du journal Mistral (premier : {inconnus[0]})"
        )
    fautifs = [a for a, (usage, statut) in vus.items() if usage != "generation" or statut != "ok"]
    if fautifs:
        usage, statut = vus[fautifs[0]]
        raise ManifesteInvalide(
            f"{len(fautifs)} appel_id hors génération réussie (premier : {fautifs[0]}, "
            f"usage {usage}, statut {statut})"
        )
    return len(ids)


def controler_contraintes(
    config: Mapping[str, Any], slug: str, *, exclure_vision: bool
) -> dict[str, Any]:
    """Refuse Mamba, FP8 et un encodeur vision non exclu (`ConfigurationInvalide`).

    Complète `environnement.controler_config_modele` par `layers_block_type` (autre clé
    des hybrides Mamba). Avec `exclure_vision` (`config/modeles/<slug>.toml`), la partie
    vision est ignorée du contrôle et signalée comme exclue.
    """
    for sous in (config, config.get("text_config")):
        if not isinstance(sous, Mapping):
            continue
        blocs = sous.get("layers_block_type")
        if isinstance(blocs, list) and any("mamba" in str(b).lower() for b in blocs):
            raise ConfigurationInvalide(
                f"{slug} : couche Mamba dans `layers_block_type` (modèle hybride écarté)"
            )
    if "vision_config" in config and not exclure_vision:
        raise ConfigurationInvalide(
            f"{slug} : encodeur vision présent et non exclu (`exclure_vision = true` "
            f"requis dans config/modeles/{slug}.toml)"
        )
    texte = {cle: valeur for cle, valeur in config.items() if cle != "vision_config"}
    resume = environnement.controler_config_modele(texte, slug)
    resume["vision_config"] = "exclu" if "vision_config" in config else False
    return resume


def sha_chat_template(tokenizer: Any) -> str:
    """SHA-256 du chat template du tokenizer (texte UTF-8, ou JSON canonique d'un dict)."""
    modele = getattr(tokenizer, "chat_template", None)
    if not modele:
        raise ConfigurationInvalide("le tokenizer n'a pas de chat template")
    texte = modele if isinstance(modele, str) else json.dumps(modele, sort_keys=True)
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()


def pretokeniser(
    tokenizer: Any,
    lignes: Sequence[_Ligne],
    *,
    longueur_max: int,
    config_modele: ConfigModele,
) -> tuple[list[dict[str, list[int]]], dict[str, int]]:
    """`input_ids` et `labels` de chaque ligne, coupés ensemble à `longueur_max`.

    `tools` n'est transmis au template qu'avec le protocole `natif`. `ErreurMasque` est
    propagée : un masque non prouvé refuse le Run plutôt que d'entraîner sur un faux masque.
    """
    natif = config_modele.protocole_outils == "natif"
    exemples: list[dict[str, list[int]]] = []
    tronques = ecartes = 0
    for ligne in lignes:
        rendu = calculer_masque(
            tokenizer,
            ligne.messages,
            tools=ligne.tools if natif else None,
            config=config_modele,
        )
        ids, labels = rendu.input_ids[:longueur_max], rendu.labels[:longueur_max]
        tronques += len(rendu.input_ids) > longueur_max
        if all(etiquette == IGNORE for etiquette in labels):
            ecartes += 1
            continue
        exemples.append({"input_ids": ids, "labels": labels})
    stats = {
        "lignes": len(lignes),
        "retenus": len(exemples),
        "tronques": tronques,
        "ecartes_sans_supervision": ecartes,
        "tokens": sum(len(e["input_ids"]) for e in exemples),
        "tokens_supervises": sum(
            sum(etiquette != IGNORE for etiquette in e["labels"]) for e in exemples
        ),
    }
    return exemples, stats


def preparer_preferences(
    tokenizer: Any,
    paires: Sequence[_Paire],
    *,
    config_modele: ConfigModele,
) -> tuple[list[dict[str, str]], dict[str, int]]:
    """Paires `{prompt, chosen, rejected}` en texte, rendues par le chat template du Modèle.

    Le rendu est fait ici (`train.rendu`, `tools` avec le protocole `natif`,
    `chat_template_kwargs` du Modèle) : `ORPOTrainer` ne transmet ni l'un ni l'autre au
    template. Il reçoit donc des textes, qu'il tokenise et tronque lui-même à `max_length`.
    Lève `ManifesteInvalide` si le rendu complet ne commence pas par celui du prompt.
    """
    natif = config_modele.protocole_outils == "natif"
    exemples: list[dict[str, str]] = []
    for numero, paire in enumerate(paires, start=1):
        options: dict[str, Any] = {
            "tools": paire.tools if natif else None,
            "config": config_modele,
        }
        prompt = apply_chat_template(tokenizer, paire.prompt, add_generation_prompt=True, **options)
        exemple = {"prompt": prompt}
        for cle in ("chosen", "rejected"):
            complet = apply_chat_template(tokenizer, paire.prompt + getattr(paire, cle), **options)
            if not complet.startswith(prompt) or len(complet) == len(prompt):
                raise ManifesteInvalide(
                    f"paire {numero} : le rendu de « {cle} » ne prolonge pas celui du prompt"
                )
            exemple[cle] = complet[len(prompt) :]
        exemples.append(exemple)
    return exemples, {"lignes": len(paires), "retenus": len(exemples)}


@dataclass
class CollateurMasque:
    """Complète à droite : `pad_id` pour les ids, `IGNORE` pour les labels, masque 0."""

    pad_id: int
    torch: Any = None

    def __call__(self, exemples: Sequence[Mapping[str, Sequence[int]]]) -> dict[str, Any]:
        longueur = max(len(e["input_ids"]) for e in exemples)
        lots: dict[str, list[list[int]]] = {"input_ids": [], "labels": [], "attention_mask": []}
        for e in exemples:
            manque = longueur - len(e["input_ids"])
            lots["input_ids"].append(list(e["input_ids"]) + [self.pad_id] * manque)
            lots["labels"].append(list(e["labels"]) + [IGNORE] * manque)
            lots["attention_mask"].append([1] * len(e["input_ids"]) + [0] * manque)
        if self.torch is None:
            return dict(lots)
        return {
            cle: self.torch.tensor(valeur, dtype=self.torch.long) for cle, valeur in lots.items()
        }
