---
title: "Story 9.7 — Paires de préférence ORPO"
type: 'feature'
created: '2026-10-16'
status: review
baseline_revision: '63e63bb'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-9-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-6-etape-build.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** M4 (ORPO) n'avait aucune source de paires de préférence, et le chargeur 10.4 n'en lisait qu'un format provisoire.

**Approach:** `slmsp data build --preferences --depuis <build_run> --modele base:<slug>` prend la dernière réponse `assistant` de chaque exemple SFT comme `chosen` et une génération du Modèle de base local comme `rejected`, journalisée dans `SLMSP_VAR_DIR/generations-locales.sqlite` (`generateur = slm:<slug>`). Le résultat est une nouvelle version `data/train/vN/{preferences.jsonl, MANIFEST.json}`.

## Boundaries & Constraints

**Always:**
- D1.1 : aucun texte n'est rédigé ; `chosen` vient du jeu SFT (SHA revérifié), `rejected` du modèle local. Fixtures : jetons factices.
- Aucun verdict du Juge Claude (le MANIFEST porte `utilise_verdicts_juge = false` et la dérogation FR-34).
- Contrat unique avec `train.chargement` : `EntetePaire` (`core.schemas.entrainement`) remplace le schéma provisoire `_Paire` ; `PairePreference` l'étend ; `meta.appel_ids` = appels Mistral de la réponse choisie (recontrôlés par `recontroler_appel_ids`).
- Une version n'est jamais réécrite : les paires forment une nouvelle `vN`.

**Never:** appel d'API, import de `judge`/`anthropic`, import de `slmsp.train` depuis `data` (couches).

## I/O & Edge-Case Matrix

| Scénario | Comportement |
|---|---|
| `chosen` et `rejected` égaux après normalisation (NFKC, casse, espaces) | paire écartée, motif `identique` compté |
| Génération vide / appel d'outil / `chosen` sans texte | écartée (`vide`, `non_texte`, `chosen_sans_texte`) |
| Génération tronquée (`Fin.raison = longueur`) ou interrompue (raison `interrompue`, flux sans `Fin`) | écartée (`tronquee`, `interrompue`), statut du journal local identique |
| `appel_local_id` absent du journal local, d'un autre générateur, ou `rejected` au SHA différent | `ManifesteInvalide` au chargement (`train.chargement.recontroler_rejected`) |
| Aucune paire retenue | `ManifesteInvalide`, run `partiel-erreur`, aucune `vN` |
| SHA de `train.jsonl` différent du MANIFEST | `ProvenanceInvalide` avant tout run |
| Run d'un autre type, en cours, ou sans jeu SFT | `ManifesteInvalide` |

</intent-contract>

## Code Map

- `src/slmsp/data/preferences.py` : `lancer_preferences`, `normaliser`.
- `src/slmsp/inference/journal_local.py` : `JournalLocal` (ajout seul, même forme que le journal Mistral).
- `src/slmsp/core/schemas/entrainement.py` : `EntetePaire`, `PairePreference`, `MetaPaire`, `ManifestePreferences`, `DEROGATION_ORPO`.
- `src/slmsp/train/chargement.py` : `_Paire = EntetePaire`.
- `src/slmsp/data/config.py`, `config/donnees.toml` : table `[preferences]` (graine, température, `max_tokens`).
- `src/slmsp/cli/data.py` : `build --preferences --modele base:<slug> [--llama cpu|cuda]`.
- Tests : `tests/data/test_preferences.py`, `tests/train/test_preferences_chargeur.py` (production → `charger_jeu` → `preparer_preferences`, tokenizer factice).

## Design Notes

- Le lecteur `data` n'a pas accès à `data/train/` (verrou 2) : le jeu SFT est lu avec le lecteur `train`.
- `rejected` est généré avec les `tools` de l'exemple SFT (traités par le client selon le protocole du Modèle, comme au rendu ORPO de `train.chargement`) sur la conversation sans la réponse choisie ; un appel d'outil est écarté (`non_texte`). La graine de la paire de rang `i` est `graine + i`.
- Commande réelle à lancer plus tard (serveur llama.cpp, hors nuit) : `uv run slmsp data build --preferences --depuis <build_run> --modele base:granite-4.0-1b`.

## Verification

- `uv run pytest -q --tb=short tests/data/test_preferences.py tests/train/test_preferences_chargeur.py` : verts.

## Auto Run Result

- Décisions (à confirmer par Anaël) : (1) les paires sont une nouvelle version `vN` (et non un ajout à la version SFT, jamais réécrite) ; M4 vise donc `jeu_version = <vN des paires>` ; (2) `rejected` généré avec les `tools` de l'exemple (revue : aligné sur le rendu) ; (3) lecture du jeu SFT par le lecteur `train` ; (4) `JournalLocal` placé dans `inference/` : le test d'architecture AD-24 (`tests/test_architecture.py`, `LECTEURS_INTERDITS`) interdit à `data` d'importer `core.var.ouvrir_sqlite` et `sqlite3.connect` (règle des lectures contrôlées, qui bloque de fait l'ouverture en écriture) ; aucune règle d'architecture n'interdit explicitement l'écriture SQLite.
- Report : pas de `--nb-max` ni de reprise d'un run interrompu ; test réel avec llama-server non lancé.

## Revue

Revue du 2026-10-16 (second avis Haiku puis reviewer), après rebase sur main (10.5, 11.1).

- medium, corrigé : `Fin.raison` ignorée, une génération tronquée (`longueur`) ou interrompue (ou sans `Fin`) devenait un `rejected`. Écartée avec les motifs `tronquee` et `interrompue`, comptés dans le rapport et le MANIFEST ; statut du journal local identique.
- medium, corrigé : `meta.appel_local_id` jamais recontrôlé au chargement. Ajout de `train.chargement.recontroler_rejected` (existence, `usage = generation-locale`, `statut = ok`, générateur, SHA-256 du texte rejeté), appelé par `train run` pour ORPO ; `generations-locales.sqlite` ajouté à la liste d'accès du lecteur `train` (`core.artefacts.chemin_autorise`, constante `NOM_JOURNAL_LOCAL` déplacée dans `core.artefacts`). Tests rouge/vert : identifiant inventé, texte altéré, autre générateur, journal absent.
- medium, corrigé : `rejected` généré sans `tools` mais rendu avec au chargement (protocole natif). La génération reçoit désormais les `tools` de l'exemple ; ils sont journalisés dans la requête et consignés dans la config du run.
- low, corrigé : `_creer_version` et les écritures hors du `try` laissaient le run `en_cours` et une `vN` sans MANIFEST. Écriture déplacée dans le `try` (`_ecrire_version`), MANIFEST écrit en dernier par renommage d'un fichier temporaire ; test d'échec d'écriture.
- low, corrigé (spec) : la justification « AD-24 interdit à data d'écrire du SQLite » est reformulée : c'est la règle des lectures contrôlées du test d'architecture qui bloque `sqlite3.connect` et `core.var.ouvrir_sqlite` dans `data`.
- low, corrigé : un run de paires passé à `--depuis` (data-build sans `train.jsonl`) levait `FileNotFoundError` ; désormais `ManifesteInvalide` (« jeu SFT attendu »).
- D1 : aucun texte rédigé dans le code ni les fixtures (jetons factices `<…-factice-…>`), aucun appel payant.

Points à confirmer par Anaël :
1. Génération du `rejected` avec les outils : avec le protocole natif, le Modèle de base peut appeler un outil au lieu de répondre ; ces cas sont écartés (`non_texte`) et peuvent réduire le nombre de paires sur les Tâches à outils. Alternative : générer sans outils et rendre sans outils au chargement (mais alors le prompt ORPO diffère de celui du SFT).
2. Une `vN` laissée par un échec d'écriture (dossier sans MANIFEST) n'est pas supprimée : elle reste illisible par `train.chargement`, et la prochaine version prend le numéro suivant.
3. Hors story : sur la branche rebasée, 5 tests échouent avant comme après la revue (`tests/budget/test_tarifs.py` et 3 de `tests/cli/test_budget.py`, plafonds changés par 9f4dc35 sur main ; `tests/evaluation/test_notation.py`, extra `anthropic` retiré par `uv sync --extra data`).

