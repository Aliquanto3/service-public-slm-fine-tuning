"""Gabarit de la fiche modèle (`README.md`) du dossier de publication.

Le texte est un gabarit : les faits viennent des artefacts (config du Modèle de base, run
d'export, Registre des licences) ; tout le reste est un emplacement
`<À COMPLÉTER PAR ANAËL : …>`. Aucune affirmation sur les capacités du modèle n'est
rédigée par le code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

MARQUE = "À COMPLÉTER PAR ANAËL"
MOTIF_EMPLACEMENT = re.compile(r"<À COMPLÉTER PAR ANAËL[^>]*>")


def emplacement(consigne: str) -> str:
    return f"<{MARQUE} : {consigne}>"


@dataclass(frozen=True)
class SourceRegistre:
    id: str
    licence: str
    usage: str


@dataclass(frozen=True)
class ContexteFiche:
    nom_modele: str
    depot_base: str
    revision_base: str
    licence: str
    quantification: str
    gguf_nom: str
    gguf_octets: int
    gguf_sha256: str
    export_run: str
    llamacpp_tag: str | None
    chat_template_sha256: str | None
    registre_sha256: str
    mention_non_certification: str
    comparatif_nom: str
    sources: tuple[SourceRegistre, ...] = field(default_factory=tuple)


def rendre_fiche(c: ContexteFiche) -> str:
    """README.md complet : front matter Hugging Face, faits sourcés et emplacements."""
    lignes = [
        "---",
        f"license: {c.licence}",
        f"base_model: {c.depot_base}",
        "language:",
        "- fr",
        "---",
        "",
        f"# {c.nom_modele}",
        "",
        emplacement("présentation en deux phrases, rédigée et relue par Anaël"),
        "",
        "## Modèle de base et fichier fourni",
        "",
        f"- Modèle de base : `{c.depot_base}`, révision `{c.revision_base}`.",
        f"- Licence de ce dépôt : `{c.licence}` (voir `LICENSE`).",
        f"- Fichier : `{c.gguf_nom}` ({c.quantification}), {c.gguf_octets} octets, "
        f"SHA-256 `{c.gguf_sha256}`.",
        f"- Run d'export : `{c.export_run}`.",
    ]
    if c.llamacpp_tag:
        lignes.append(f"- llama.cpp : `{c.llamacpp_tag}`.")
    if c.chat_template_sha256:
        lignes.append(f"- SHA-256 du modèle de conversation : `{c.chat_template_sha256}`.")
    lignes += [
        "- Les empreintes de tous les fichiers sont dans `SHA256SUMS`.",
        "",
        "## Données utilisées et Registre des licences",
        "",
        emplacement("préciser quelles sources ci-dessous ont servi à l'entraînement"),
        "",
        "Le jeu d'entraînement n'est pas publié. Registre des licences "
        f"(SHA-256 `{c.registre_sha256}`) :",
        "",
        "| Source | Licence | Usage |",
        "|---|---|---|",
    ]
    lignes += [f"| `{s.id}` | {s.licence} | {s.usage} |" for s in c.sources]
    lignes += [
        "",
        "## Résultats d'évaluation",
        "",
        f"Les résultats chiffrés (Baselines, gains, coûts, Benchmarks) sont dans "
        f"`{c.comparatif_nom}`, généré à partir des runs archivés.",
        "",
        emplacement("commentaire sur les résultats, avec la version du jeu d'évaluation citée"),
        "",
        "## Limites et usages déconseillés",
        "",
        emplacement("limites connues, usages déconseillés, langues et domaines non couverts"),
        "",
        "## Non-certification",
        "",
        c.mention_non_certification,
        "",
    ]
    return "\n".join(lignes)


def emplacements_restants(texte: str) -> list[str]:
    """Emplacements `<À COMPLÉTER PAR ANAËL : …>` encore présents dans `texte`."""
    return MOTIF_EMPLACEMENT.findall(texte)
