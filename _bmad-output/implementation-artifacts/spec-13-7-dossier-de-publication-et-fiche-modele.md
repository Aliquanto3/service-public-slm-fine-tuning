---
title: 'Story 13.7 — Dossier de publication et fiche modèle (FR-37)'
type: 'feature'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: []
deferred: []
---

## Intent

**Problem:** publier un Modèle embarqué sans envoi automatique ni allégation trompeuse (FR-37, Q8).

**Approach:** `slmsp publication preparer` assemble hors ligne un dossier vérifié (fiche gabarit, licence, GGUF, Comparatif, `SHA256SUMS`) ; Anaël le téléverse lui-même (`docs/procedure-publication.md`). Aucune sous-commande d'envoi, interdiction d'upload d'AD-4 intacte.

## Boundaries & Constraints

**Always:** profil réseau `aucun` (test avec `socket.connect` interdit) ; fiche = gabarit, faits tirés des artefacts, le reste en `<À COMPLÉTER PAR ANAËL : …>` ; dossier en échec renommé `<sortie>.refuse` ; jeu d'entraînement non publié.

**Never:** fichier de `eval/` ou `data/train/` dans le dossier ou en source ; texte du Jeu d'évaluation (n-grammes AD-11) ; secret ; formulation de certification hors phrase de non-certification ; import d'upload.

## Code Map

- `src/slmsp/publication/` -- `config.py`, `fiche.py` (gabarit), `controles.py`, `preparer.py` (couche 4).
- `src/slmsp/cli/publication.py` -- `publication preparer --modele --export --comparatif --sortie [--quantification] [--racine]`.
- `config/publication.toml`, `config/licences/apache-2.0.txt`, `docs/procedure-publication.md`.
- `tests/publication/` (runs factices), `tests/test_architecture.py` (`COUCHES`), `tests/test_cli.py`.

## Auto Run Result

- Licence : première de `ordre_permissivite` présente dans `licences_compatibles` du Modèle de base ; échec sinon, ou si `verifie_le` est absent (licence non relue). Seul le texte Apache 2.0 est fourni (copie du fichier LICENSE d'un paquet du venv, texte canonique).
- Registre des licences lu directement en TOML (`publication` ne peut pas importer `data`, même couche) ; sa validation complète reste celle de `data`.
- Fuite : 3 empreintes de 5-grammes communes avec `jeux_proteges` (config, `v1.0` et `v1.1`) suffisent à refuser un fichier texte. `_empreintes_texte` de `core.items` est importé (privé).
- Section « Données utilisées » : liste tout le Registre, la sélection réelle est un emplacement (le run d'export ne consigne pas les sources).
- Résultats chiffrés : portés par `COMPARATIF.md` joint, pas recopiés dans la fiche.
- Aucun test réel ni GGUF réel : non lancé sur un export réel.

## À confirmer

- Licences des Modèles de base (`licences_compatibles = ["apache-2.0"]`, `verifie_le` absent) : à relire sur chaque fiche HF par Anaël ; tant que `verifie_le` manque, la commande refuse.
- Seuil de fuite (3 empreintes) et liste des formulations interdites : choix de départ.
- Commandes `hf` de la procédure (`hf repo create`, `hf upload`) : à vérifier avec la version installée.
- Texte de la mention de non-certification (`config/publication.toml`).
- Les sources réellement utilisées à l'entraînement ne sont pas lisibles dans le run d'export : à préciser à la main, ou à consigner dans le run d'entraînement (report).
