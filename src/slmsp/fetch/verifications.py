"""Contrôles D7 des Modèles de base candidats (story 8.1).

Pour chaque modèle de génération, après `slmsp fetch modeles` :

- `dense` : toutes les couches de `config.json` (`layer_types` et les autres clés de
  `CLES_TYPES_COUCHE`, dans toutes les sous-configurations) sont des couches d'attention ;
  un type de couche inconnu, ou une clé de format non reconnu, écarte le modèle.
  Les couches `linear_attention` (hybride Gated DeltaNet) et `mamba` (Granite 4.0 H, révision
  D8 du 2026-10-18) sont admises pour l'inférence et la Baseline, si la fiche porte
  `entrainable = false` ;
- `fp8` : aucune `quantization_config`, aucun `dtype`/`torch_dtype` en `float8` ;
- `vision` : un `vision_config` exige `exclure_vision = true` ;
- `chat_template` : le template du tokenizer HF et celui du GGUF
  (`tokenizer.chat_template`) sont comparés par SHA-256. S'ils diffèrent, le template HF est
  exporté sous `<models>/<slug>/chat_template.jinja` (jamais par-dessus un fichier
  différent) et la configuration doit porter `chat_template_force = true` ;
- `serveur` : `llama-server` (variante `cpu`, sans projecteur) démarre sur le GGUF et
  répond à `/health` ; `/props` est relevé (modalités, contexte, template).

Un modèle sans poids HF (`fichiers = []`) ou d'embedding a les quatre premiers contrôles
`sans-objet`. Un modèle écarté l'est avec son motif ; rien n'est réécrit dans la
configuration versionnée : la vérification signale, la story inscrit.

Les métadonnées GGUF sont lues à la main (`lire_metadonnees_gguf`), sans le paquet `gguf`.
"""

from __future__ import annotations

import hashlib
import json
import os
import struct
from collections import Counter, deque
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Final, Literal

from slmsp.core.erreurs import SlmspError
from slmsp.core.schemas.config_modele import ConfigModele

# Aligné sur le registre des Modèles de base de D8 le 2026-10-17 (décision d'Anaël) : il remplace
# l'ordre D4 initial (ministral-3-3b, smollm3-3b, qwen-4b, ministral-3-8b, écartés par la
# règle de taille). D'abord les candidats au fine-tuning, puis les « Baseline seulement »
# (eurollm-1.7b depuis le 2026-10-18, puis les Qwen).
CANDIDATS: tuple[str, ...] = (
    "granite-4.0-1b",
    "granite-4.0-350m",
    "minicpm5-1b",
    "minicpm5-2b",
    "eurollm-1.7b",
    "granite-4.0-h-350m",
    "granite-4.0-h-1b",
    "qwen3.5-0.8b",
    "qwen3.5-2b",
)
"""Modèles de base candidats (`fetch modeles --candidats`), dans l'ordre du registre de D8 :
candidats au fine-tuning, puis Baseline seulement (`entrainable = false`)."""

CONTROLES: Final = ("dense", "fp8", "vision", "chat_template", "serveur")

Statut = Literal["ok", "echec", "sans-objet"]

NOM_TEMPLATE: Final = "chat_template.jinja"
CLE_TEMPLATE_GGUF: Final = "tokenizer.chat_template"
COUCHES_DENSES: Final = frozenset({"attention", "full_attention", "sliding_attention"})
"""Types de couche d'attention du contrôle `dense` (liste fermée)."""
COUCHES_INFERENCE_SEULE: Final = frozenset({"linear_attention", "mamba"})
"""Couches hybrides admises pour l'inférence seulement (Gated DeltaNet, décision D8 ; Mamba,
révision D8 du 2026-10-18, llama.cpp les servant sous Windows) : la fiche doit porter
`entrainable = false`, sauf `linear_attention` seul, entraînable avec les noyaux fla (extra
`gdn`, la garde vit dans `train`). Tout autre type écarte le modèle."""
FAMILLES_HYBRIDES: Final = {"linear_attention": "Gated DeltaNet", "mamba": "Mamba"}
"""Libellé de famille de chaque type de `COUCHES_INFERENCE_SEULE` (détail du contrôle `dense`)."""
CLES_TYPES_COUCHE: Final = (
    "layer_types",
    "layers_block_type",
    "layer_block_types",
    "block_types",
    "hybrid_override_pattern",
)
"""Clés connues des types de couche (Qwen, Gemma, Granite 4.0 H, Jamba, Nemotron-H…),
cherchées dans toutes les sous-configurations : une valeur qui n'est pas une liste non vide
(motif en chaîne, par exemple) écarte le modèle par prudence."""
DELAI_PROPS: Final = 30.0


@dataclass(frozen=True)
class Controle:
    """Résultat d'un contrôle : une ligne de `controles.jsonl`."""

    modele: str
    controle: str
    statut: Statut
    detail: str
    valeurs: dict[str, Any] = field(default_factory=dict)

    def ligne(self) -> dict[str, Any]:
        return asdict(self)


def ecartes(controles: Iterable[Controle]) -> dict[str, list[str]]:
    """Modèles écartés (au moins un contrôle en échec) → motifs, dans l'ordre reçu."""
    motifs: dict[str, list[str]] = {}
    for controle in controles:
        if controle.statut == "echec":
            motifs.setdefault(controle.modele, []).append(
                f"{controle.controle} : {controle.detail}"
            )
    return motifs


# --- Lecteur GGUF ----------------------------------------------------------------------------


class GgufInvalide(SlmspError):
    """En-tête GGUF illisible (magie, version, type de valeur ou longueur hors bornes)."""


MAGIE_GGUF: Final = b"GGUF"
VERSIONS_GGUF: Final = (2, 3)
TAILLE_MAX_CHAINE: Final = 1 << 30

_SCALAIRES: Final[dict[int, str]] = {
    0: "<B",  # uint8
    1: "<b",  # int8
    2: "<H",  # uint16
    3: "<h",  # int16
    4: "<I",  # uint32
    5: "<i",  # int32
    6: "<f",  # float32
    7: "<?",  # bool
    10: "<Q",  # uint64
    11: "<q",  # int64
    12: "<d",  # float64
}
_CHAINE: Final = 8
_TABLEAU: Final = 9


def _lire(flux: BinaryIO, n: int) -> bytes:
    donnees = flux.read(n)
    if len(donnees) != n:
        raise GgufInvalide(f"fin de fichier inattendue ({len(donnees)} octets sur {n})")
    return donnees


def _entier(flux: BinaryIO, format_: str) -> int:
    return int(struct.unpack(format_, _lire(flux, struct.calcsize(format_)))[0])


def _longueur_chaine(flux: BinaryIO) -> int:
    n = _entier(flux, "<Q")
    if n > TAILLE_MAX_CHAINE:
        raise GgufInvalide(f"chaîne de {n} octets : hors bornes")
    return n


def _chaine(flux: BinaryIO) -> str:
    return _lire(flux, _longueur_chaine(flux)).decode("utf-8", errors="replace")


def _valeur(flux: BinaryIO, type_: int, garder: bool) -> Any:
    """Lit (ou saute, si `garder` est faux) une valeur de type `type_`."""
    if type_ in _SCALAIRES:
        format_ = _SCALAIRES[type_]
        donnees = _lire(flux, struct.calcsize(format_))
        return struct.unpack(format_, donnees)[0] if garder else None
    if type_ == _CHAINE:
        if garder:
            return _chaine(flux)
        flux.seek(_longueur_chaine(flux), os.SEEK_CUR)
        return None
    if type_ == _TABLEAU:
        type_elements = _entier(flux, "<I")
        n = _entier(flux, "<Q")
        if not garder and type_elements in _SCALAIRES:
            flux.seek(n * struct.calcsize(_SCALAIRES[type_elements]), os.SEEK_CUR)
            return None
        elements = [_valeur(flux, type_elements, garder) for _ in range(n)]
        return elements if garder else None
    raise GgufInvalide(f"type de valeur GGUF inconnu : {type_}")


def lire_metadonnees_gguf(chemin: str | os.PathLike[str], cles: Iterable[str]) -> dict[str, Any]:
    """Valeurs des clés `cles` de l'en-tête GGUF (v2 ou v3) de `chemin`.

    Les autres valeurs, tableaux compris, sont sautées ; la lecture s'arrête dès que toutes
    les clés demandées sont lues. Une clé absente du fichier est absente du résultat.
    Lève `GgufInvalide` si l'en-tête est illisible.
    """
    voulues = set(cles)
    trouvees: dict[str, Any] = {}
    with open(chemin, "rb", buffering=1 << 20) as flux:
        if _lire(flux, 4) != MAGIE_GGUF:
            raise GgufInvalide(f"{chemin} : magie GGUF absente")
        version = _entier(flux, "<I")
        if version not in VERSIONS_GGUF:
            raise GgufInvalide(f"{chemin} : version GGUF {version} non prise en charge")
        _entier(flux, "<Q")  # nombre de tenseurs
        n_kv = _entier(flux, "<Q")
        for _ in range(n_kv):
            if not voulues - trouvees.keys():
                break
            cle = _chaine(flux)
            type_ = _entier(flux, "<I")
            garder = cle in voulues
            valeur = _valeur(flux, type_, garder)
            if garder:
                trouvees[cle] = valeur
    return trouvees


# --- Configuration HF -----------------------------------------------------------------------


def _sans_poids_hf(config: ConfigModele) -> bool:
    return config.embedding or not config.fichiers


def _sous_configs(donnees: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    """La racine puis toutes les sous-configurations dict, à toute profondeur (`text_config`,
    `llm_config`, `language_config`…) : le contrôle ne suppose pas le nom de la
    sous-configuration du modèle texte."""
    configs: list[tuple[str, dict[str, Any]]] = []
    file: deque[tuple[str, dict[str, Any]]] = deque([("", donnees)])
    while file:
        prefixe, sous = file.popleft()
        configs.append((prefixe, sous))
        file.extend((f"{prefixe}{cle}.", v) for cle, v in sous.items() if isinstance(v, dict))
    return configs


def _controle_dense(slug: str, donnees: dict[str, Any], config: ConfigModele) -> Controle:
    sources: list[str] = []
    illisibles: list[str] = []
    comptes: Counter[str] = Counter()
    autres: list[str] = []
    lineaires: Counter[str] = Counter()
    total = 0
    for prefixe, sous in _sous_configs(donnees):
        for cle in CLES_TYPES_COUCHE:
            brut = sous.get(cle)
            if brut is None:
                continue
            if not isinstance(brut, list) or not brut:
                illisibles.append(f"{prefixe}{cle}")
                continue
            types = [str(t) for t in brut]
            sources.append(f"{prefixe}{cle}")
            comptes.update(types)
            total += len(types)
            lineaires.update(t for t in types if t in COUCHES_INFERENCE_SEULE)
            marque = prefixe if cle == "layer_types" else f"{prefixe}{cle}."
            autres += [
                f"{marque}{i} ({t})"
                for i, t in enumerate(types)
                if t not in COUCHES_DENSES and t not in COUCHES_INFERENCE_SEULE
            ]
    if illisibles:
        return Controle(
            slug,
            "dense",
            "echec",
            f"{', '.join(illisibles)} : liste de types de couche attendue, format non reconnu "
            "(modèle écarté par prudence)",
            {"source": ", ".join(illisibles)},
        )
    if not sources:
        return Controle(slug, "dense", "ok", "aucune clé de types de couche : modèle dense", {})
    valeurs = {"layer_types": dict(comptes), "source": ", ".join(sources)}
    if autres:
        liste = ", ".join(autres[:12])
        suite = f" et {len(autres) - 12} autres" if len(autres) > 12 else ""
        return Controle(
            slug,
            "dense",
            "echec",
            f"{len(autres)} couche(s) sur {total} hors attention : {liste}{suite} ; "
            "variante hybride écartée",
            valeurs,
        )
    if lineaires:
        nombre = sum(lineaires.values())
        types_hybrides = "+".join(sorted(lineaires))
        famille = " et ".join(FAMILLES_HYBRIDES[t] for t in sorted(lineaires))
        if config.entrainable and "linear_attention" in lineaires and "mamba" not in lineaires:
            return Controle(
                slug,
                "dense",
                "ok",
                f"hybride Gated DeltaNet entraînable : {nombre} couche(s) {types_hybrides} sur "
                f"{total}, noyaux fla requis à l'entraînement (extra gdn)",
                valeurs,
            )
        if config.entrainable:  # Mamba, seul ou mélangé : inférence et Baseline seulement
            return Controle(
                slug,
                "dense",
                "echec",
                f"{nombre} couche(s) {types_hybrides} sur {total} : hybride {famille} "
                "admis pour l'inférence seulement, inscrire entrainable = false (décision D8)",
                valeurs,
            )
        return Controle(
            slug,
            "dense",
            "ok",
            f"hybride {famille} admis pour l'inférence, non entraînable : {nombre} "
            f"couche(s) {types_hybrides} sur {total} ({', '.join(sources)})",
            valeurs,
        )
    return Controle(
        slug, "dense", "ok", f"{total} couches d'attention ({', '.join(sources)})", valeurs
    )


def _controle_fp8(slug: str, donnees: dict[str, Any]) -> Controle:
    motifs = []
    for prefixe, sous in _sous_configs(donnees):
        if sous.get("quantization_config") is not None:
            methode = sous["quantization_config"]
            if isinstance(methode, dict):
                methode = methode.get("quant_method", methode)
            motifs.append(f"{prefixe}quantization_config présent ({methode})")
        for cle in ("dtype", "torch_dtype"):
            valeur = sous.get(cle)
            if isinstance(valeur, str) and "float8" in valeur.lower():
                motifs.append(f"{prefixe}{cle} = {valeur}")
    dtype = donnees.get("dtype") or donnees.get("torch_dtype")
    if motifs:
        return Controle(
            slug,
            "fp8",
            "echec",
            "; ".join(motifs) + " : poids quantifiés non gérés par la RTX 3050",
            {"dtype": dtype},
        )
    return Controle(slug, "fp8", "ok", f"poids non quantifiés (dtype {dtype})", {"dtype": dtype})


def _controle_vision(slug: str, donnees: dict[str, Any], config: ConfigModele) -> Controle:
    vision = donnees.get("vision_config")
    if vision is None:
        return Controle(slug, "vision", "ok", "aucun vision_config", {"vision_config": False})
    valeurs = {
        "vision_config": True,
        "model_type": vision.get("model_type") if isinstance(vision, dict) else None,
        "exclure_vision": config.exclure_vision,
    }
    if config.exclure_vision:
        return Controle(slug, "vision", "ok", "vision_config présent, exclu", valeurs)
    return Controle(
        slug,
        "vision",
        "echec",
        "vision_config présent : inscrire exclure_vision = true",
        valeurs,
    )


def verifier_config_hf(slug: str, config: ConfigModele, dossier_hf: str | Path) -> list[Controle]:
    """Contrôles `dense`, `fp8` et `vision` sur `<dossier_hf>/config.json`."""
    noms = ("dense", "fp8", "vision")
    if _sans_poids_hf(config):
        motif = "modèle d'embedding" if config.embedding else "aucun poids HF (fichiers = [])"
        return [Controle(slug, nom, "sans-objet", motif) for nom in noms]
    chemin = Path(dossier_hf) / "config.json"
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        motif = f"{chemin} illisible : {type(exc).__name__} : {exc}"
        return [Controle(slug, nom, "echec", motif) for nom in noms]
    if not isinstance(donnees, dict):
        return [Controle(slug, nom, "echec", f"{chemin} : objet JSON attendu") for nom in noms]
    return [
        _controle_dense(slug, donnees, config),
        _controle_fp8(slug, donnees),
        _controle_vision(slug, donnees, config),
    ]


# --- Chat template ---------------------------------------------------------------------------


def template_hf(dossier_hf: str | Path) -> str | None:
    """Template du tokenizer HF : `chat_template.jinja`, sinon `tokenizer_config.json`.

    Dans `tokenizer_config.json`, `chat_template` est une chaîne, ou une liste de
    `{name, template}` dont on prend `name = "default"`. `None` si aucun n'est trouvé.
    """
    dossier = Path(dossier_hf)
    fichier = dossier / NOM_TEMPLATE
    if fichier.is_file():
        return fichier.read_bytes().decode("utf-8")
    config = dossier / "tokenizer_config.json"
    if not config.is_file():
        return None
    valeur = json.loads(config.read_text(encoding="utf-8")).get("chat_template")
    if isinstance(valeur, str):
        return valeur
    if isinstance(valeur, list):
        for element in valeur:
            if isinstance(element, dict) and element.get("name") == "default":
                template = element.get("template")
                return template if isinstance(template, str) else None
    return None


def _sha(texte: str | None) -> str | None:
    return None if texte is None else hashlib.sha256(texte.encode("utf-8")).hexdigest()


def exporter_template(chemin: Path, texte: str) -> Literal["cree", "identique", "conflit"]:
    """Écrit `texte` sous `chemin` (via `.part` puis renommage), sans jamais écraser.

    `identique` si le fichier existe avec ce contenu, `conflit` s'il existe avec un autre
    contenu ou si un `.part` traîne (rien n'est alors touché).
    """
    contenu = texte.encode("utf-8")
    if chemin.exists():
        if not chemin.is_file():
            return "conflit"
        return "identique" if chemin.read_bytes() == contenu else "conflit"
    partiel = chemin.with_name(chemin.name + ".part")
    try:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        flux = open(partiel, "xb")  # noqa: SIM115 (fermé ci-dessous, retiré en cas d'échec)
    except OSError:  # FileExistsError compris : un `.part` traîne, il n'est pas touché
        return "conflit"
    try:
        with flux:
            flux.write(contenu)
        # Comportement propre à Windows (D2 : Windows seul) : `os.rename` n'y remplace
        # jamais une destination existante ; il lève si `chemin` est apparu entre-temps.
        os.rename(partiel, chemin)
    except OSError:
        partiel.unlink(missing_ok=True)  # le `.part` créé par cet appel
        return "conflit"
    return "cree"


def verifier_chat_template(
    slug: str, config: ConfigModele, dossier_modele: str | Path, gguf: str | Path
) -> Controle:
    """Compare le template HF et celui du GGUF ; exporte le template HF s'il le faut."""
    if _sans_poids_hf(config):
        motif = "modèle d'embedding" if config.embedding else "aucun poids HF (fichiers = [])"
        valeurs_gguf: dict[str, Any] = {}
        if not config.embedding:  # GGUF seul : son template est l'attendu du serveur
            try:
                texte = lire_metadonnees_gguf(gguf, [CLE_TEMPLATE_GGUF]).get(CLE_TEMPLATE_GGUF)
            except (OSError, SlmspError):
                texte = None
            valeurs_gguf["sha256_gguf"] = _sha(texte) if isinstance(texte, str) else None
        return Controle(slug, "chat_template", "sans-objet", motif, valeurs_gguf)
    dossier = Path(dossier_modele)
    try:
        texte_hf = template_hf(dossier / "hf")
        texte_gguf = lire_metadonnees_gguf(gguf, [CLE_TEMPLATE_GGUF]).get(CLE_TEMPLATE_GGUF)
    except (OSError, ValueError, SlmspError) as exc:
        return Controle(
            slug, "chat_template", "echec", f"lecture impossible : {type(exc).__name__} : {exc}"
        )
    if not isinstance(texte_gguf, str):
        texte_gguf = None
    export = dossier / NOM_TEMPLATE
    valeurs: dict[str, Any] = {
        "sha256_hf": _sha(texte_hf),
        "sha256_gguf": _sha(texte_gguf),
        "chat_template_force": config.chat_template_force,
    }
    if texte_hf is None:
        return Controle(
            slug, "chat_template", "echec", "aucun template dans le tokenizer HF", valeurs
        )
    identiques = texte_hf == texte_gguf
    if identiques and not config.chat_template_force:
        return Controle(slug, "chat_template", "ok", "templates HF et GGUF identiques", valeurs)
    issue = exporter_template(export, texte_hf)
    valeurs.update(export=str(export), issue_export=issue)
    if issue == "conflit":
        return Controle(
            slug,
            "chat_template",
            "echec",
            f"{export} existe déjà avec un autre contenu (ou un .part traîne) : laissé intact",
            valeurs,
        )
    if identiques:
        detail = "templates identiques ; chat_template_force superflu, template exporté"
        return Controle(slug, "chat_template", "ok", detail, valeurs)
    gguf_decrit = "absent du GGUF" if texte_gguf is None else "différent de celui du GGUF"
    if config.chat_template_force:
        return Controle(
            slug,
            "chat_template",
            "ok",
            f"template HF {gguf_decrit} : exporté sous {export}, chat_template_force = true",
            valeurs,
        )
    return Controle(
        slug,
        "chat_template",
        "echec",
        f"template HF {gguf_decrit} : exporté sous {export} ; inscrire chat_template_force = true",
        valeurs,
    )


# --- Serveur ---------------------------------------------------------------------------------


def _lire_props(port: int) -> dict[str, Any]:
    """`GET /props` du `llama-server` local de `port`."""
    from slmsp.net import client_local

    with client_local(port) as http:
        reponse = http.get(f"http://127.0.0.1:{port}/props", timeout=DELAI_PROPS)
        reponse.raise_for_status()
        props = reponse.json()
    if not isinstance(props, dict):
        raise ValueError("/props : objet JSON attendu")
    return props


def _fabrique_par_defaut() -> Callable[..., Any]:
    from slmsp.inference.serveur import ServeurLlama

    return ServeurLlama


def verifier_serveur(
    slug: str,
    config: ConfigModele,
    fabrique: Callable[..., Any] | None = None,
    *,
    lire_props: Callable[[int], dict[str, Any]] | None = None,
    sha256_hf: str | None = None,
    sha256_gguf: str | None = None,
) -> Controle:
    """Démarre `llama-server` (cpu, sans `--mmproj`) puis relève `/props`.

    `fabrique(config, "cpu", slug=slug)` rend un gestionnaire de contexte qui expose `port`
    et `journal` (par défaut `ServeurLlama`). Le template servi est comparé à l'attendu
    (template HF si `chat_template_force`, sinon celui du GGUF) : un template forcé que le
    serveur ignore (servi = GGUF ≠ HF) écarte le modèle ; toute autre différence (llama.cpp
    réécrit certains templates, ceux de Mistral par exemple) est seulement signalée.
    """
    fabrique = _fabrique_par_defaut() if fabrique is None else fabrique
    lire_props = _lire_props if lire_props is None else lire_props
    serveur = None
    try:
        serveur = fabrique(config, "cpu", slug=slug)
        with serveur:
            props = lire_props(serveur.port)
    except Exception as exc:  # ErreurInference, ConfigurationInvalide, HTTP : signalé
        journal = getattr(serveur, "journal", None)
        return Controle(
            slug,
            "serveur",
            "echec",
            f"{type(exc).__name__} : {exc}",
            {"journal": None if journal is None else str(journal)},
        )
    modalites = props.get("modalities") or {}
    generation = props.get("default_generation_settings") or {}
    template = props.get("chat_template")
    servi = _sha(template) if isinstance(template, str) else None
    attendu = sha256_hf if config.chat_template_force else sha256_gguf
    conforme = servi is not None and servi == attendu
    valeurs = {
        "variante": "cpu",
        "modalities": modalites,
        "n_ctx": generation.get("n_ctx") if isinstance(generation, dict) else None,
        "build_info": props.get("build_info"),
        "sha256_chat_template": servi,
        "sha256_template_attendu": attendu,
        "template_servi_conforme": conforme,
        "journal": None if serveur.journal is None else str(serveur.journal),
    }
    actives = sorted(nom for nom, actif in modalites.items() if actif)
    if config.exclure_vision and modalites.get("vision"):
        return Controle(
            slug, "serveur", "echec", "projecteur vision chargé malgré exclure_vision", valeurs
        )
    if (
        config.chat_template_force
        and servi is not None
        and servi == sha256_gguf
        and sha256_hf != sha256_gguf
    ):
        return Controle(slug, "serveur", "echec", "template forcé ignoré par llama-server", valeurs)
    decrites = ", ".join(actives) if actives else "texte seul"
    detail = f"llama-server (cpu) prêt ; /props : modalités {decrites}"
    if not conforme:
        detail += f" ; template servi transformé par llama-server (sha {servi})"
    return Controle(slug, "serveur", "ok", detail, valeurs)


# --- Ensemble --------------------------------------------------------------------------------


def verifier_modele(
    slug: str,
    config: ConfigModele,
    dossier_modeles: str | Path,
    *,
    sans_serveur: bool = False,
    fabrique: Callable[..., Any] | None = None,
    lire_props: Callable[[int], dict[str, Any]] | None = None,
) -> list[Controle]:
    """Les cinq contrôles de `CONTROLES` pour le modèle `slug`, dans cet ordre."""
    dossier = Path(dossier_modeles) / slug
    gguf = dossier / "gguf" / Path(config.gguf.fichier).name
    controles = verifier_config_hf(slug, config, dossier / "hf")
    template = verifier_chat_template(slug, config, dossier, gguf)
    controles.append(template)
    if sans_serveur:
        controles.append(Controle(slug, "serveur", "sans-objet", "--sans-serveur"))
    else:
        controles.append(
            verifier_serveur(
                slug,
                config,
                fabrique,
                lire_props=lire_props,
                sha256_hf=template.valeurs.get("sha256_hf"),
                sha256_gguf=template.valeurs.get("sha256_gguf"),
            )
        )
    return controles


__all__ = [
    "CANDIDATS",
    "CONTROLES",
    "Controle",
    "GgufInvalide",
    "ecartes",
    "exporter_template",
    "lire_metadonnees_gguf",
    "template_hf",
    "verifier_chat_template",
    "verifier_config_hf",
    "verifier_modele",
    "verifier_serveur",
]
