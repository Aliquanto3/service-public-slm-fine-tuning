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

## Revue

Sources : S = second avis (Haiku), R = relecteur.

- medium, S, corrigé : une mention admise court-circuitait toute la phrase. Seules les occurrences des mentions sont désormais retirées (avec un « ISO 42001 » qui les suit) avant la recherche ; test « certifié ISO 42001, non certifié par un tiers » (2 constats).
- medium, S, corrigé : titres `#` désormais contrôlés ; motifs élargis (certifie, conformité, attesté/attestation, homologué, labellisé, certified) ; mentions admises complétées (« aucune attestation de conformité », « non-certification ») pour que la mention de la fiche et son titre passent ; tests paramétrés.
- medium, S, corrigé : un `.refuse` existant n'est plus bloquant ni écrasé ; le suivant prend le suffixe `.refuse.2`, `.refuse.3`. Testé.
- medium, S, corrigé : écriture dans `<sortie>.part`, renommé seulement si tout passe ; une exception supprime le `.part` (testé en forçant une erreur) ; un `.part` résiduel est purgé.
- medium, S, corrigé : `jeux_proteges` vide refusé (préparation et `controle_fuite` sur liste vide) ; toutes les versions de `eval/jeu/` et le calibrage (lecture seule) doivent figurer dans la liste, sinon refus ; `calibrage` ajouté à `config/publication.toml`. Testé, dont sur le dépôt réel.
- low, S, corrigé : tout fichier est lu s'il est du texte (sonde : pas d'octet nul, UTF-8 valide), sauf `.gguf`.
- low, S, corrigé : seuil calculé sur le fichier entier (n-grammes toujours pris ligne par ligne).
- low, S, corrigé : `verifie_le` futur refusé.
- low, S, corrigé : `empreintes_texte` publique dans `core.items`, alias `_empreintes_texte` conservé.
- low, S, corrigé : assertions précisées (constat exact, noms de fichiers, exceptions typées). Les 13 skips sont les 13 gardes de `tests/test_cli.py:88` pour les modules de sous-commandes déjà présents (« le module … existe ») : attendus, sans lien avec cette story.
- low, S, corrigé : fuite contre `data/train/` contrôlée quand le dossier existe ; il n'existe pas encore dans le dépôt, donc non exercé en réel (test sur dossier factice).
- Report : exécution sur un export et un GGUF réels (service indisponible) ; la formulation exacte des motifs reste un choix de départ à relire par Anaël (faux positifs possibles sur « conformité » dans un texte légitime).
