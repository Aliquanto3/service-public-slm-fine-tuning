"""Assemblage et vérification du dossier de publication (story 13.7, FR-37).

Entrées : Modèle de base (`config/modeles/<slug>.toml`), run `export` complet (GGUF),
Comparatif (`comparatif.md`), Registre des licences. Sortie : un dossier local avec
`README.md`, `LICENSE`, le GGUF, `COMPARATIF.md` et `SHA256SUMS`. Aucun réseau, aucun envoi.
Écriture dans `<sortie>.part`, renommé en `<sortie>` si tout passe, sinon en `<sortie>.refuse`
(suffixe numéroté si un refus existe déjà) ; une erreur supprime le dossier partiel.
"""

from __future__ import annotations

import json
import re
import shutil
import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from slmsp.core.artefacts import ouvrir_run
from slmsp.core.canonique import sha256_fichier, sha256_hex
from slmsp.core.config import charger_toml
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.publication import controles, fiche
from slmsp.publication.config import ConfigPublication, charger_config

NOM_COMPARATIF = "COMPARATIF.md"
NOM_LICENCE = "LICENSE"
NOM_FICHE = "README.md"
QUANTIFICATIONS = ("q4_k_m", "f16")


@dataclass
class Rapport:
    dossier: Path
    licence: str = ""
    bloquants: list[str] = field(default_factory=list)
    emplacements: list[str] = field(default_factory=list)

    @property
    def publiable(self) -> bool:
        return not self.bloquants


def choisir_licence(slug: str, config: ConfigPublication) -> str:
    """Licence compatible la plus permissive (AC2) ; échec si aucune ou non relue."""
    modele = config.modeles.get(slug)
    if modele is None or not modele.licences_compatibles:
        raise ConfigurationInvalide(
            f"publication : aucune licence compatible déclarée pour {slug} "
            "(config/publication.toml, section [modeles])"
        )
    if modele.verifie_le is None:
        raise ConfigurationInvalide(
            f"publication : licence du Modèle de base {slug} non relue "
            "(renseigner verifie_le dans config/publication.toml après lecture de sa fiche)"
        )
    if modele.verifie_le > date.today():
        raise ConfigurationInvalide(
            f"publication : verifie_le de {slug} est dans le futur ({modele.verifie_le})"
        )
    for licence in config.ordre_permissivite:
        if licence in modele.licences_compatibles:
            return licence
    raise ConfigurationInvalide(
        f"publication : aucune licence de sortie admise pour {slug} "
        f"(compatibles : {', '.join(modele.licences_compatibles)})"
    )


def _texte_licence(racine: Path, licence: str) -> Path:
    chemin = racine / "config" / "licences" / f"{licence}.txt"
    if not chemin.is_file():
        raise ConfigurationInvalide(f"publication : texte de licence absent : {chemin}")
    return chemin


def _lire_export(racine: Path, export_run: str, quantification: str) -> tuple[Path, str, str]:
    """GGUF, tag llama.cpp et SHA du modèle de conversation d'un export complet."""
    run = ouvrir_run(export_run, racine=racine)
    if run.type != "export" or run.statut_courant() != "complet":
        raise ConfigurationInvalide(f"publication : {export_run} n'est pas un export complet")
    try:
        export = json.loads((run.dossier / "export.json").read_text(encoding="utf-8"))
        nom = export["fichiers"][quantification]
    except (OSError, KeyError, ValueError):
        raise ConfigurationInvalide(
            f"publication : export.json de {export_run} illisible"
        ) from None
    if export.get("controles", {}).get("bloquants"):
        raise ConfigurationInvalide(f"publication : export {export_run} avec contrôles bloquants")
    gguf = run.dossier / nom
    if not gguf.is_file():
        raise ConfigurationInvalide(f"publication : GGUF absent : {gguf}")
    return gguf, run.manifeste.llamacpp_tag or "", run.manifeste.chat_template_sha256 or ""


def _lire_registre(racine: Path) -> tuple[tuple[fiche.SourceRegistre, ...], str]:
    """Sources du Registre des licences (lecture seule) et SHA-256 du fichier.

    `publication` ne dépend pas de `data` (même couche) : le fichier est lu directement,
    sa validation complète reste celle de `RegistreLicences` à la construction des données.
    """
    chemin = racine / "data" / "registre-licences.toml"
    try:
        octets = chemin.read_bytes()
        brut = tomllib.loads(octets.decode("utf-8"))["sources"]
        sources = tuple(
            fiche.SourceRegistre(str(s["id"]), str(s["licence"]), str(s["usage"]))
            for s in sorted(brut, key=lambda s: str(s["id"]))
        )
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, KeyError, TypeError):
        raise ConfigurationInvalide(
            f"publication : Registre des licences illisible : {chemin}"
        ) from None
    return sources, sha256_hex(octets)


def versions_du_jeu(racine: Path) -> list[str]:
    """Toutes les versions présentes sous `eval/jeu/` (`vN[.M]`), plus le calibrage s'il existe."""
    jeu = racine / "eval" / "jeu"
    versions = (
        sorted(
            d.name for d in jeu.iterdir() if d.is_dir() and re.fullmatch(r"v\d+(\.\d+)?", d.name)
        )
        if jeu.is_dir()
        else []
    )
    if (racine / "eval" / "calibrage" / "echantillon-calibrage.jsonl").is_file():
        versions.append("calibrage")
    return versions


def _empreintes_protegees(racine: Path, config: ConfigPublication) -> frozenset[str]:
    """Empreintes de `jeux_proteges` ; refuse une liste vide ou qui omet une version présente."""
    if not config.jeux_proteges:
        raise ConfigurationInvalide(
            "publication : jeux_proteges est vide (config/publication.toml) ; "
            "le contrôle de fuite ne protégerait rien"
        )
    omises = [v for v in versions_du_jeu(racine) if v not in config.jeux_proteges]
    if omises:
        raise ConfigurationInvalide(
            "publication : jeux_proteges ne couvre pas " + ", ".join(omises)
        )
    from slmsp.core.items import empreintes_antifuite

    return empreintes_antifuite(config.jeux_proteges, racine=racine).toutes()


def preparer(
    *,
    racine: Path,
    modele: str,
    export_run: str,
    comparatif: Path,
    sortie: Path,
    quantification: str = "q4_k_m",
    empreintes: frozenset[str] | None = None,
) -> Rapport:
    """Prépare `sortie` ; lève `ConfigurationInvalide` si une entrée manque ou est refusée."""
    racine, sortie, comparatif = racine.resolve(), sortie.resolve(), comparatif.resolve()
    if quantification not in QUANTIFICATIONS:
        raise ConfigurationInvalide(f"publication : quantification inconnue : {quantification}")
    if sortie.exists() and any(sortie.iterdir()):
        raise ConfigurationInvalide(f"publication : dossier de sortie non vide : {sortie}")
    config = charger_config(racine)
    licence = choisir_licence(modele, config)
    texte_licence = _texte_licence(racine, licence)
    config_modele = charger_toml(racine / "config" / "modeles" / f"{modele}.toml", ConfigModele)
    gguf, tag, sha_gabarit = _lire_export(racine, export_run, quantification)
    if not comparatif.is_file():
        raise ConfigurationInvalide(f"publication : Comparatif introuvable : {comparatif}")
    interdits = [
        c for s in (gguf, comparatif, sortie) for c in controles.controle_chemin_source(s, racine)
    ]
    if interdits:
        raise ConfigurationInvalide("\n".join(interdits))
    if empreintes is None:
        empreintes = _empreintes_protegees(racine, config)
    sources, sha_registre = _lire_registre(racine)
    train = racine / "data" / "train"
    empreintes_train = controles.empreintes_dossier(train) if train.is_dir() else None

    partiel = sortie.with_name(sortie.name + ".part")
    if partiel.exists():
        shutil.rmtree(partiel)  # reste d'une préparation interrompue
    partiel.mkdir(parents=True)
    try:
        rapport = _assembler(
            partiel,
            config,
            empreintes,
            empreintes_train,
            gguf,
            comparatif,
            texte_licence,
            licence,
            modele,
            config_modele,
            export_run,
            quantification,
            tag,
            sha_gabarit,
            sources,
            sha_registre,
        )
    except BaseException:
        shutil.rmtree(partiel, ignore_errors=True)
        raise
    if rapport.bloquants:
        cible = _nom_refuse(sortie)
    else:
        if sortie.exists():
            sortie.rmdir()  # dossier vide, vérifié plus haut
        cible = sortie
    partiel.replace(cible)
    rapport.dossier = cible
    return rapport


def _nom_refuse(sortie: Path) -> Path:
    """`<sortie>.refuse`, ou `<sortie>.refuse.N` si un dossier refusé précédent existe."""
    cible = sortie.with_name(sortie.name + ".refuse")
    n = 1
    while cible.exists():
        n += 1
        cible = sortie.with_name(f"{sortie.name}.refuse.{n}")
    return cible


def _assembler(
    sortie: Path,
    config: ConfigPublication,
    empreintes: frozenset[str],
    empreintes_train: frozenset[str] | None,
    gguf: Path,
    comparatif: Path,
    texte_licence: Path,
    licence: str,
    modele: str,
    config_modele: ConfigModele,
    export_run: str,
    quantification: str,
    tag: str,
    sha_gabarit: str,
    sources: tuple[fiche.SourceRegistre, ...],
    sha_registre: str,
) -> Rapport:
    shutil.copyfile(gguf, sortie / gguf.name)
    shutil.copyfile(comparatif, sortie / NOM_COMPARATIF)
    shutil.copyfile(texte_licence, sortie / NOM_LICENCE)
    contexte = fiche.ContexteFiche(
        nom_modele=modele,
        depot_base=config_modele.depot_hf,
        revision_base=config_modele.revision,
        licence=licence,
        quantification=quantification,
        gguf_nom=gguf.name,
        gguf_octets=(sortie / gguf.name).stat().st_size,
        gguf_sha256=sha256_fichier(sortie / gguf.name),
        export_run=export_run,
        llamacpp_tag=tag or None,
        chat_template_sha256=sha_gabarit or None,
        registre_sha256=sha_registre,
        mention_non_certification=config.mention_non_certification,
        comparatif_nom=NOM_COMPARATIF,
        sources=sources,
    )
    texte_fiche = fiche.rendre_fiche(contexte)
    (sortie / NOM_FICHE).write_text(texte_fiche, encoding="utf-8", newline="\n")
    sommes = controles.lister_sommes(sortie)
    (sortie / controles.NOM_SOMMES).write_text(
        "".join(f"{sha}  {nom}\n" for nom, sha in sommes.items()), encoding="utf-8", newline="\n"
    )

    rapport = Rapport(dossier=sortie, licence=licence)
    rapport.bloquants += controles.controle_fichiers(sortie)
    rapport.bloquants += controles.controle_sections(texte_fiche, config)
    rapport.bloquants += controles.controle_formulations(texte_fiche, config, NOM_FICHE)
    comparatif_texte = (sortie / NOM_COMPARATIF).read_text(encoding="utf-8", errors="replace")
    rapport.bloquants += controles.controle_formulations(comparatif_texte, config, NOM_COMPARATIF)
    rapport.bloquants += controles.controle_secrets(sortie, config)
    rapport.bloquants += controles.controle_fuite(sortie, empreintes)
    if empreintes_train is not None:
        rapport.bloquants += controles.controle_fuite(
            sortie, empreintes_train, "jeu d'entraînement (data/train/)"
        )
    rapport.bloquants += controles.controle_sommes(sortie)
    rapport.emplacements = fiche.emplacements_restants(texte_fiche)
    return rapport
