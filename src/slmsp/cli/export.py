"""`slmsp export` : export GGUF d'un Run d'entraînement (story 10.6, FR-35).

    slmsp export --depuis <train_run_id> [--variante cpu|cuda] [--sans-sonde]
    slmsp export --base <slug>            # export témoin : la base par la même chaîne

`train.export.exporter` fusionne, convertit (F16) et quantifie (Q4_K_M) sous `gpu.lock`.
Ce module lui fournit les contrôles de format (`train` ne lit pas les GGUF, AD-24) :

- **bloquant** (CA2) : SHA de `tokenizer.chat_template` embarqué dans chaque GGUF égal à
  celui du tokenizer d'entraînement ;
- **alertes** (note 10.6, C5) : métadonnées différentes du GGUF officiel du même slug
  (architecture, nombre de couches, `tokenizer.ggml.pre`, identifiants bos et eos).

Une fois le run `complet` (CA3) : `ft:<run_id>` est résolu par `evaluation.modele_ref` pour
`f16` et `q4_k_m`, puis la sonde d'outils (items RD-001 et RD-002, soit R-001 et R-002
d'H-TOOLS) passe sur le Q4_K_M ; son bilan va dans `sonde-outils.json` du run d'export.
La sonde reprend `gpu.lock` elle-même en variante `cuda`, après la libération par l'export.

Pour une fiche `multimodal`, une sonde vision suit (`sonde-vision.json`) : llama-server (cpu)
sur le Q4_K_M avec le `mmproj`, modalité vision annoncée par `/props`, puis une image
synthétique et une réponse non vide (son contenu n'est pas jugé).

Une sonde non valide fait passer le run d'export en `degrade` (motif consigné) :
`evaluation.modele_ref` refuse alors `ft:<run_id>`, sauf `accepter_degrade=True` explicite.

Codes : 0 export complet et sonde valide (ou `--sans-sonde`), 1 contrôle bloquant ou sonde
non valide, 5 GPU occupé.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import struct
import sys
import zlib
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any, Final

from slmsp.core.artefacts import Run
from slmsp.core.canonique import json_canonique
from slmsp.core.config import dossier_modeles, racine_ecriture
from slmsp.core.erreurs import CodeSortie
from slmsp.fetch.verifications import GgufInvalide, lire_metadonnees_gguf
from slmsp.inference.serveur import VARIANTES, Lora, ServeurLlama, charger_config_modele
from slmsp.net.client import client_local
from slmsp.train import export as train_export
from slmsp.train import purge

CLE_TEMPLATE: Final = "tokenizer.chat_template"
CLE_ARCHITECTURE: Final = "general.architecture"
CLES_TOKENIZER: Final = (
    "tokenizer.ggml.pre",
    "tokenizer.ggml.bos_token_id",
    "tokenizer.ggml.eos_token_id",
)
SUFFIXES_ARCHITECTURE: Final = ("block_count", "embedding_length", "attention.head_count")
NOM_SONDE: Final = "sonde-outils.json"
NOM_SONDE_VISION: Final = "sonde-vision.json"
DELAI_REQUETE_VISION: Final = 600.0
"""Délai (s) d'une requête de la sonde vision (CPU, première image)."""


def enregistrer(sous_parseurs: argparse._SubParsersAction) -> None:
    """Ajoute `export`."""
    p = sous_parseurs.add_parser(
        "export",
        help="export GGUF des adaptateurs",
        description="Fusionne l'adaptateur d'un Run d'entraînement en 16 bits, convertit en "
        "GGUF F16 puis quantifie en Q4_K_M (outils du tag de config/llamacpp.toml), contrôle "
        "le chat template embarqué et re-teste le tool calling sur le Q4_K_M.",
    )
    p.add_argument(
        "action",
        nargs="?",
        choices=["purger", "lora"],
        help="`purger` : supprime hf-f16/ et modele-f16.gguf d'un export noté "
        "(--depuis EXPORT_RUN_ID, ou --tous-notes) ; `lora` : convertit l'adaptateur du run "
        "d'entraînement --depuis en LoRA GGUF (sans fusion) pour `eval run --modele lora:<id>`",
    )
    source = p.add_mutually_exclusive_group()
    source.add_argument("--depuis", metavar="TRAIN_RUN_ID", help="run d'entraînement complet")
    source.add_argument("--base", metavar="SLUG", help="export témoin de la base, sans adaptateur")
    p.add_argument(
        "--tous-notes", action="store_true", help="avec `purger` : tous les exports notés"
    )
    p.add_argument(
        "--forcer-non-note",
        action="store_true",
        help="avec `purger --depuis` : purge même sans notation référençant l'export",
    )
    p.add_argument("--dry-run", action="store_true", help="avec `purger` : liste sans supprimer")
    p.add_argument(
        "--variante",
        choices=VARIANTES,
        default="cpu",
        help="variante llama.cpp de la sonde (outils ; chargement du LoRA pour `lora`) "
        "(défaut : cpu)",
    )
    p.add_argument(
        "--sans-sonde",
        action="store_true",
        help="ne pas lancer les sondes (outils, vision ; chargement du LoRA pour `lora`)",
    )
    p.add_argument(
        "--python",
        type=Path,
        default=None,
        help="interpréteur du convertisseur (défaut : le courant, environnement train)",
    )
    p.add_argument(
        "--delai",
        type=float,
        default=None,
        metavar="SECONDES",
        help="délai de la conversion et de la quantification, chacune (défaut : "
        "proportionné aux poids de la base, 30 min au moins)",
    )
    p.add_argument(
        "--racine",
        type=Path,
        default=None,
        help="racine des runs (défaut : racine d'écriture du projet)",
    )
    p.set_defaults(func=_exporter)


def sha_template(chemin: Path) -> str | None:
    """SHA-256 de `tokenizer.chat_template` embarqué dans le GGUF `chemin` (`None` : absent)."""
    valeur = lire_metadonnees_gguf(chemin, [CLE_TEMPLATE]).get(CLE_TEMPLATE)
    if not isinstance(valeur, str):
        return None
    return hashlib.sha256(valeur.encode("utf-8")).hexdigest()


def metadonnees(chemin: Path) -> dict[str, Any]:
    """Métadonnées comparées au GGUF officiel (architecture, couches, tokenizer)."""
    architecture = lire_metadonnees_gguf(chemin, [CLE_ARCHITECTURE]).get(CLE_ARCHITECTURE)
    cles = [*CLES_TOKENIZER]
    if isinstance(architecture, str):
        cles += [f"{architecture}.{suffixe}" for suffixe in SUFFIXES_ARCHITECTURE]
    return {CLE_ARCHITECTURE: architecture, **lire_metadonnees_gguf(chemin, cles)}


def gguf_officiel(slug: str) -> Path | None:
    """GGUF Q4_K_M officiel du slug (`config/modeles/<slug>.toml`), s'il est présent."""
    fichier = charger_config_modele(slug).gguf_pour("q4_k_m")
    if fichier is None:
        return None
    chemin = dossier_modeles() / slug / "gguf" / PurePosixPath(fichier.fichier).name
    return chemin if chemin.is_file() else None


def controler_format(slug: str) -> Any:
    """Contrôles de format injectés dans `train.export.exporter` (CA2 et note 10.6, C5)."""

    def controler(run: Run, export: Mapping[str, Any]) -> dict[str, Any]:
        attendu = export["chat_template_sha256_attendu"]
        bloquants: list[str] = []
        alertes: list[str] = []
        templates: dict[str, str | None] = {}
        for quantification, nom in export["fichiers"].items():
            if quantification in ("hf", "mmproj"):  # ni GGUF texte ni chat template
                continue
            try:
                templates[quantification] = sha_template(run.dossier / nom)
            except GgufInvalide as exc:
                bloquants.append(f"{nom} illisible : {exc}")
                continue
            if templates[quantification] != attendu:
                bloquants.append(
                    f"{nom} : chat template embarqué {templates[quantification]} ≠ "
                    f"tokenizer d'entraînement {attendu}"
                )
        officiel = gguf_officiel(slug)
        comparaison: dict[str, Any] = {"officiel": officiel.name if officiel else None}
        if officiel is None:
            alertes.append(f"GGUF officiel de {slug} absent : métadonnées non comparées")
        elif not bloquants:
            try:
                exporte = metadonnees(run.dossier / export["fichiers"]["q4_k_m"])
                reference = metadonnees(officiel)
            except (GgufInvalide, OSError) as exc:
                alertes.append(f"métadonnées non comparées au GGUF officiel ({exc})")
                return {
                    "bloquants": bloquants,
                    "alertes": alertes,
                    "templates": templates,
                    "metadonnees": comparaison,
                }
            ecarts = {
                cle: {"export": exporte.get(cle), "officiel": reference.get(cle)}
                for cle in sorted(exporte.keys() | reference.keys())
                if exporte.get(cle) != reference.get(cle)
            }
            comparaison["ecarts"] = ecarts
            if ecarts:
                alertes.append(f"métadonnées différentes du GGUF officiel : {', '.join(ecarts)}")
        return {
            "bloquants": bloquants,
            "alertes": alertes,
            "templates": templates,
            "metadonnees": comparaison,
        }

    return controler


def _racine(args: argparse.Namespace) -> Path:
    return (args.racine if args.racine is not None else racine_ecriture()).resolve()


def _exporter(args: argparse.Namespace) -> int:
    # Import différé : `evaluation` (harnais, juge) n'est chargé qu'après l'export.
    from slmsp.evaluation import modele_ref  # noqa: PLC0415

    racine = _racine(args)
    if args.action == "purger":
        return _purger(args, racine)
    if args.action == "lora":
        return _exporter_lora(args, racine)
    if args.tous_notes or args.forcer_non_note or args.dry_run:
        print("slmsp : export : --tous-notes, --forcer-non-note et --dry-run vont avec `purger`")
        return int(CodeSortie.USAGE)
    if args.depuis is None and args.base is None:
        print("slmsp : export : --depuis ou --base requis (ou `export purger`)")
        return int(CodeSortie.USAGE)
    if args.depuis is not None:
        source = train_export.source_depuis_run(args.depuis, racine=racine)
    else:
        charger_config_modele(args.base)  # slug connu (ConfigurationInvalide)
        source = train_export.source_temoin(args.base)
    run = train_export.exporter(
        source,
        racine=racine,
        python=args.python,
        controles=controler_format(source.slug),
        delai=args.delai,
    )
    statut = run.statut_courant()
    print(f"export : run {run.run_id} {statut}")
    if statut != "complet":
        print(f"slmsp : export {run.run_id} non complet (voir export.json)")
        return int(CodeSortie.ERREUR)
    ref = f"ft:{run.run_id}"
    for quantification in modele_ref.QUANTIFICATIONS:
        resolu = modele_ref.resoudre(ref, quantification, racine=racine)
        print(f"{ref} {quantification} : {resolu.gguf.name} (précision {resolu.precision})")
    if args.sans_sonde:
        code = int(CodeSortie.SUCCES)
    else:
        code = _sonder(run, ref, args.variante, racine)
        if code == int(CodeSortie.SUCCES) and charger_config_modele(source.slug).multimodal:
            code = _sonder_vision(run, source.slug)
    if code == int(CodeSortie.SUCCES):
        print(
            "intermédiaires (hf-f16/, modele-f16.gguf) gardés : après notation, "
            "`slmsp export purger --tous-notes` les supprime"
        )
    return code


CLES_LORA: Final = ("general.type", CLE_ARCHITECTURE, "adapter.type", "adapter.lora.alpha")
NOM_SONDE_LORA: Final = "sonde-lora.json"


def controler_lora(slug: str) -> Any:
    """Contrôles de compatibilité injectés dans `train.export.exporter_lora` : le GGUF est un
    adaptateur LoRA, de la même architecture que la base Q4_K_M officielle de `slug`."""

    def controler(run: Run, export: Mapping[str, Any]) -> dict[str, Any]:
        bloquants: list[str] = []
        alertes: list[str] = []
        nom = export["fichiers"]["lora"]
        try:
            lora = lire_metadonnees_gguf(run.dossier / nom, CLES_LORA)
        except (GgufInvalide, OSError) as exc:
            return {"bloquants": [f"{nom} illisible : {exc}"], "alertes": [], "metadonnees": {}}
        if lora.get("general.type") != "adapter" or lora.get("adapter.type") != "lora":
            bloquants.append(
                f"{nom} n'est pas un adaptateur LoRA GGUF "
                f"(general.type {lora.get('general.type')!r}, adapter.type "
                f"{lora.get('adapter.type')!r})"
            )
        base = gguf_officiel(slug)
        comparaison: dict[str, Any] = {"base_q4_k_m": base.name if base else None}
        if base is None:
            alertes.append(f"GGUF q4_k_m de {slug} absent : compatibilité non vérifiée")
        else:
            try:
                architecture = metadonnees(base).get(CLE_ARCHITECTURE)
            except (GgufInvalide, OSError) as exc:
                alertes.append(f"GGUF de base illisible ({exc}) : compatibilité non vérifiée")
            else:
                comparaison["architecture_base"] = architecture
                if lora.get(CLE_ARCHITECTURE) != architecture:
                    bloquants.append(
                        f"architecture du LoRA ({lora.get(CLE_ARCHITECTURE)!r}) différente de "
                        f"celle de la base q4_k_m ({architecture!r})"
                    )
            attendu = run.manifeste.chat_template_sha256
            alertes += _comparer_template(slug, base, attendu, comparaison)
        return {
            "bloquants": bloquants,
            "alertes": alertes,
            "metadonnees": {**comparaison, "lora": lora},
        }

    return controler


def _comparer_template(
    slug: str, base: Path, attendu: str | None, comparaison: dict[str, Any]
) -> list[str]:
    """Le LoRA est servi avec le gabarit de la base (`chat_template.jinja` imposé, sinon celui
    du GGUF q4_k_m) : alerte s'il diffère du gabarit du tokenizer d'entraînement."""
    try:
        if charger_config_modele(slug).chat_template_force:
            texte = (dossier_modeles() / slug / "chat_template.jinja").read_text(encoding="utf-8")
            servi: str | None = hashlib.sha256(texte.encode("utf-8")).hexdigest()
        else:
            servi = sha_template(base)
    except (GgufInvalide, OSError) as exc:
        return [f"gabarit servi de la base illisible ({exc}) : non comparé à l'entraînement"]
    comparaison["chat_template_sha256_servi"] = servi
    comparaison["chat_template_sha256_entrainement"] = attendu
    if attendu is None or servi != attendu:
        return [
            f"gabarit servi de la base ({servi}) différent de celui du tokenizer "
            f"d'entraînement ({attendu}) : scores à lire avec ce biais"
        ]
    return []


def _alertes_export(run: Run) -> list[str]:
    try:
        export = json.loads((run.dossier / train_export.NOM_EXPORT).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [str(a) for a in export.get("controles", {}).get("alertes", [])]


def sonder_lora(
    base: Path,
    lora: Path,
    slug: str,
    variante: str,
    *,
    fabrique: Any = ServeurLlama,
    http: Any = client_local,
) -> dict[str, Any]:
    """Démarre llama-server sur `base` + `--lora-scaled lora:1` et lit `/lora-adapters`.

    Un LoRA incompatible avec la base fait échouer le chargement. Renvoie
    `{"valide", "echelle", "motif"}` ; ne lève pas.
    """
    bilan: dict[str, Any] = {"echelle": None, "motif": None}
    try:
        config = charger_config_modele(slug)
        with fabrique(
            config, variante, slug=slug, gguf=base, lora=Lora(lora, 1.0), prendre_verrou_gpu=True
        ) as serveur:
            client = http(serveur.port)
            try:
                url = f"http://127.0.0.1:{serveur.port}/lora-adapters"
                reponse = client.get(url, timeout=60)
                adaptateurs = reponse.json() if reponse.status_code == 200 else []
                if isinstance(adaptateurs, list) and adaptateurs:
                    bilan["echelle"] = adaptateurs[0].get("scale")
                else:
                    bilan["motif"] = f"aucun adaptateur servi (HTTP {reponse.status_code})"
            finally:
                client.close()
    except Exception as exc:  # démarrage, réseau, JSON : l'échec est le résultat de la sonde
        bilan["motif"] = f"{type(exc).__name__} : {exc}"[:300]
    bilan["valide"] = bilan["echelle"] == 1.0
    if bilan["motif"] is None and not bilan["valide"]:
        bilan["motif"] = f"échelle servie {bilan['echelle']!r} au lieu de 1.0"
    return bilan


def _exporter_lora(args: argparse.Namespace, racine: Path) -> int:
    if args.depuis is None or args.base is not None:
        print("slmsp : export lora : --depuis TRAIN_RUN_ID requis (pas --base)")
        return int(CodeSortie.USAGE)
    if args.tous_notes or args.forcer_non_note or args.dry_run:
        print("slmsp : export lora : --tous-notes, --forcer-non-note, --dry-run vont avec `purger`")
        return int(CodeSortie.USAGE)
    source = train_export.source_depuis_run(args.depuis, racine=racine)
    run = train_export.exporter_lora(
        source,
        racine=racine,
        python=args.python,
        controles=controler_lora(source.slug),
        delai=args.delai,
    )
    statut = run.statut_courant()
    print(f"export lora : run {run.run_id} {statut}")
    if statut != "complet":
        print(f"slmsp : export lora {run.run_id} non complet (voir export.json)")
        return int(CodeSortie.ERREUR)
    ref = f"lora:{run.run_id}"
    print(f"{ref} : {train_export.NOM_LORA} ; échelle au choix : eval run --echelle-lora")
    for alerte in _alertes_export(run):
        print(f"slmsp : alerte : {alerte}", file=sys.stderr)
    base = gguf_officiel(source.slug)
    if args.sans_sonde or base is None:
        motif = "--sans-sonde" if args.sans_sonde else f"GGUF q4_k_m de {source.slug} absent"
        # Consigné dans le run : un export sans sonde se distingue d'un export sondé valide.
        sans = {"lancee": False, "valide": None, "motif": motif, "variante": args.variante}
        run.ecrire(NOM_SONDE_LORA, json_canonique(sans) + b"\n")
        print(f"slmsp : sonde de chargement non lancée ({motif}) : voir {NOM_SONDE_LORA}")
        return int(CodeSortie.SUCCES)
    bilan = sonder_lora(base, run.dossier / train_export.NOM_LORA, source.slug, args.variante)
    bilan = {"lancee": True, **bilan, "variante": args.variante}
    run.ecrire(NOM_SONDE_LORA, json_canonique(bilan) + b"\n")
    etat = "valide" if bilan["valide"] else f"non valide ({bilan['motif']})"
    print(f"sonde de chargement {ref} : {etat}")
    if not bilan["valide"]:
        run.terminer("degrade", f"chargement du LoRA non valide ({bilan['motif']})"[:500])
        print(f"slmsp : export lora {run.run_id} degrade : {ref} refusé par l'évaluation")
        return int(CodeSortie.ERREUR)
    return int(CodeSortie.SUCCES)


def _go(octets: int) -> str:
    return f"{octets / 1024**3:.2f} Gio"


def _purger(args: argparse.Namespace, racine: Path) -> int:
    if args.base is not None or args.tous_notes == (args.depuis is not None):
        print("slmsp : export purger : exactement un de --depuis ou --tous-notes")
        return int(CodeSortie.USAGE)
    suffixe = " (dry-run)" if args.dry_run else ""
    try:
        if args.depuis is not None:
            liberes = purge.purger_depuis(
                args.depuis,
                racine=racine,
                forcer_non_note=args.forcer_non_note,
                dry_run=args.dry_run,
            )
            print(f"purge{suffixe} : {args.depuis} : {_go(liberes)} libérés")
            return int(CodeSortie.SUCCES)
    except (purge.PurgeRefusee, purge.PurgePartielle) as exc:
        print(f"slmsp : {exc}")
        return int(CodeSortie.ERREUR)
    total = 0
    echecs = 0
    for export_id, _octets in purge.exports_a_purger(racine):
        try:
            octets = purge.purger_depuis(export_id, racine=racine, dry_run=args.dry_run)
        except (purge.PurgeRefusee, purge.PurgePartielle) as exc:
            echecs += 1
            print(f"slmsp : {exc}")
            continue
        total += octets
        print(f"purge{suffixe} : {export_id} : {_go(octets)}")
    print(f"purge{suffixe} : total {_go(total)} libérés")
    return int(CodeSortie.ERREUR if echecs else CodeSortie.SUCCES)


def png_uni(
    largeur: int = 64, hauteur: int = 64, rvb: tuple[int, int, int] = (200, 60, 60)
) -> bytes:
    """PNG uni en mémoire (zlib et struct, sans Pillow) pour la sonde vision."""

    def bloc(type_: bytes, donnees: bytes) -> bytes:
        crc = zlib.crc32(type_ + donnees) & 0xFFFFFFFF
        return struct.pack(">I", len(donnees)) + type_ + donnees + struct.pack(">I", crc)

    ligne = b"\x00" + bytes(rvb) * largeur
    entete = struct.pack(">IIBBBBB", largeur, hauteur, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + bloc(b"IHDR", entete)
        + bloc(b"IDAT", zlib.compress(ligne * hauteur))
        + bloc(b"IEND", b"")
    )


def sonder_vision(
    gguf: Path, mmproj: Path, slug: str, *, fabrique: Any = ServeurLlama, http: Any = client_local
) -> dict[str, Any]:
    """Démarre llama-server (cpu) sur `gguf` avec `mmproj`, contrôle `/props` puis une image.

    Renvoie `{"valide", "modalite_vision", "reponse_non_vide", "motif"}` ; ne lève pas.
    """
    bilan: dict[str, Any] = {"modalite_vision": False, "reponse_non_vide": False, "motif": None}
    try:
        config = charger_config_modele(slug)
        with fabrique(
            config, "cpu", slug=slug, gguf=gguf, mmproj=mmproj, prendre_verrou_gpu=False
        ) as serveur:
            client = http(serveur.port)
            try:
                base = f"http://127.0.0.1:{serveur.port}"
                props = client.get(base + "/props", timeout=60).json()
                bilan["modalite_vision"] = bool((props.get("modalities") or {}).get("vision"))
                if not bilan["modalite_vision"]:
                    bilan["motif"] = "/props n'annonce pas la modalité vision"
                else:
                    image = base64.b64encode(png_uni()).decode("ascii")
                    corps = {
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Décris cette image."},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": f"data:image/png;base64,{image}"},
                                    },
                                ],
                            }
                        ],
                        "max_tokens": 32,
                        "temperature": 0,
                    }
                    reponse = client.post(
                        base + "/v1/chat/completions", json=corps, timeout=DELAI_REQUETE_VISION
                    )
                    if reponse.status_code != 200:
                        bilan["motif"] = f"HTTP {reponse.status_code} : {reponse.text[:200]}"
                    else:
                        message = reponse.json()["choices"][0]["message"]
                        texte = message.get("content") or message.get("reasoning_content") or ""
                        bilan["reponse_non_vide"] = bool(str(texte).strip())
                        if not bilan["reponse_non_vide"]:
                            bilan["motif"] = "réponse vide à l'image"
            finally:
                client.close()
    except Exception as exc:  # démarrage, réseau, JSON : l'échec est le résultat de la sonde
        bilan["motif"] = f"{type(exc).__name__} : {exc}"[:300]
    bilan["valide"] = bilan["modalite_vision"] and bilan["reponse_non_vide"]
    return bilan


def _sonder_vision(run: Run, slug: str) -> int:
    bilan = sonder_vision(
        run.dossier / "modele-q4_k_m.gguf", run.dossier / train_export.NOM_MMPROJ, slug
    )
    run.ecrire(NOM_SONDE_VISION, json_canonique(bilan) + b"\n")
    etat = "valide" if bilan["valide"] else f"non valide ({bilan['motif']})"
    print(f"sonde vision sur ft:{run.run_id} q4_k_m + mmproj : {etat}")
    if not bilan["valide"]:
        run.terminer("degrade", f"sonde vision non valide ({bilan['motif']})"[:500])
        print(f"slmsp : export {run.run_id} degrade : ft:{run.run_id} refusé par l'évaluation")
        return int(CodeSortie.ERREUR)
    return int(CodeSortie.SUCCES)


def _sonder(run: Run, ref: str, variante: str, racine: Path) -> int:
    from slmsp.evaluation import sonde_outils  # noqa: PLC0415

    rapport = sonde_outils.sonder(ref, variante=variante, racine=racine)
    bilan = {
        "sonde_run_id": rapport.run.run_id,
        "items": list(sonde_outils.ITEMS_SONDE),
        "quantification": sonde_outils.QUANTIFICATION,
        "variante": variante,
        "valide": rapport.valide,
        "protocole_recommande": rapport.protocole_recommande,
        "statut": rapport.statut,
        "motif": rapport.motif,
    }
    run.ecrire(NOM_SONDE, json_canonique(bilan) + b"\n")
    etat = "valide" if rapport.valide else f"non valide ({rapport.motif})"
    print(f"sonde d'outils sur {ref} q4_k_m : {etat} ; run {rapport.run.run_id}")
    if not rapport.valide:
        # Un Q4 dont le tool calling échoue ne doit pas être évalué par mégarde.
        run.terminer("degrade", f"sonde d'outils non valide sur q4_k_m ({rapport.motif})"[:500])
        print(f"slmsp : export {run.run_id} degrade : ft:{run.run_id} refusé par l'évaluation")
        return int(CodeSortie.ERREUR)
    return int(CodeSortie.SUCCES)


__all__ = [
    "controler_format",
    "controler_lora",
    "enregistrer",
    "gguf_officiel",
    "metadonnees",
    "png_uni",
    "sha_template",
    "sonder_lora",
    "sonder_vision",
]
