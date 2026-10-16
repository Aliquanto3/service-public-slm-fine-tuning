---
title: 'Story 12.1 — Racine de composition partagée et ressources en mode installé'
type: 'feature'
created: '2026-10-16'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: []
deferred: []
---

## Intent

**Problem:** l'application (Epic 12) et la CLI doivent assembler l'Assistant par la même fonction, et les chemins `config/`, `vendor/`, `models/` doivent se résoudre dans un exécutable installé (AD-1, AD-6, AD-14, AD-23 ; Q10, Q13).

**Approach:** `assembler`, `Assemblage`, `OutilsParesseux`, `plafonner_threads`, `slug_modele` déplacés tels quels vers `harness/assemblage.py` ; `cli/_assemblage.py` les ré-exporte (plus `JournalSqlite`, que `test_ask` remplace par un espion). `racine_projet()` suit `SLMSP_RACINE`, puis le processus gelé (`sys._MEIPASS`, sinon dossier de `sys.executable`), puis le dépôt. `config/application.toml` + `core/schemas/config_application.py` (`modele`, `variante`, `threads`, `dossier_donnees`, `langues_traduction`) ; un slug absent de `config/modeles/` est refusé.

## Boundaries & Constraints

**Always:** corps de `assembler` inchangé ; `cli/ask.py`, `cli/data.py`, `cli/measure.py` gardent `from slmsp.cli._assemblage import …` (le ré-export permet aux tests de patcher `assemblage.assembler` côté CLI).

**Never:** aucune logique nouvelle dans `assembler` ; pas de base créée par l'assemblage quand `journal` est injecté.

## Tests

`tests/harness/test_assemblage.py` (journal injecté utilisé par Mode et Passerelle, aucun SQLite sous `SLMSP_VAR_DIR`, hors ligne sans SQLite, ré-export identique) ; `tests/core/test_config_racine.py` (gelé, priorité des `SLMSP_*`, `application.toml`, slug inconnu). `test_ask`, `test_document_temoin`, `test_architecture` passent sans modification.

## Auto Run Result

Fait. Décisions seul :
- Racine gelée = `sys._MEIPASS` (PyInstaller embarque `config/`, `vendor/`, `models/` dedans) ; à défaut dossier de l'exécutable.
- `SLMSP_RACINE` ajoutée comme surcharge de `racine_projet()` (utile aux tests et à l'installateur).
- `ask.py` : imports **non** modifiés (la consigne « import mis à jour seulement » casserait le patch de `cli._assemblage.assembler` dans `test_ask`, qui doit rester sans modification).
- `dossier_donnees` stocké tel quel (`%LOCALAPPDATA%\AssistantSP`, chaîne littérale TOML) : l'expansion revient à `app.stockage` (12.2).

## À confirmer

- **AD-23 / entorse AD-1 (Q10)** : `ARCHITECTURE-SPINE.md` est un document de décision, non modifié ici (consigne). L'entorse (racine de composition en `harness`, couche 3, partagée par `cli` et `app`) est consignée dans le docstring de `harness/assemblage.py` ; **à reporter par Anaël dans AD-23**.
- **Modèle par défaut** de `application.toml` : `granite-4.0-1b` (le plus léger, CPU seul), provisoire en attendant le choix D4 ; une seule ligne à changer.
- **Langues** `["en","es","ar","pt","de"]` (Q9) : déclarées d'avance, lues par 13.4.
- `threads = 4` : valeur de départ, à mesurer sur le PC cible (12.14).

## Revue

Revue Opus (2026-10-16), avec la liste du second avis (Haiku).

- **medium**, second avis 1, **corrigé** : `test_hors_ligne_n_ouvre_pas_le_journal_sqlite` (`tests/cli/test_ask.py`) était inerte pour deux raisons : le patch visait `cli._assemblage` alors qu'`assembler` lit `JournalSqlite` dans `harness.assemblage`, et la fixture `banc` injecte déjà un journal (aucun journal n'était donc construit, même avant la story). Le test patche désormais `harness.assemblage.JournalSqlite` et appelle l'`assembler` d'origine sans journal. Preuve par mutation (`JournalSqlite()` forcé en hors ligne) : ce test et `tests/harness/test_assemblage.py::test_hors_ligne_sans_journal_n_ouvre_pas_sqlite` échouent. Entorse assumée au critère 1 (« test_ask sans modification ») : le test d'origine ne vérifiait plus rien.
- **medium**, second avis 2, **corrigé** : `core.config.racine_ecriture()` sépare la racine d'écriture de `racine_projet()` (ressources, lecture seule en mode gelé). Ordre : `SLMSP_RACINE`, puis en mode gelé `dossier_donnees` de `application.toml` étendu, sinon le dépôt. Appelants branchés : `core.artefacts._racine` (création et lecture de `runs/`, garde de lecture AD-24), `measure.protocole.mesurer`, `cli measure run` (Index lu sous les ressources, run écrit sous la racine d'écriture), `cli index build`. `index.config.dossier_index()` reste sur `racine_projet()` : l'Index est livré en lecture dans l'exécutable (story 12.12). Tests : source, `SLMSP_RACINE`, mode gelé (jamais sous `_MEIPASS`).
- **low**, second avis 3, **corrigé** : le slug doit correspondre à `^[a-z0-9]+([.-][a-z0-9]+)*$`, ce qui exclut `..`, `/`, `\` et `base:`. Le message d'une forme invalide ne reprend pas la valeur. `charger_toml` n'affiche déjà pas l'entrée pydantic.
- **low**, second avis 4, **corrigé** : `ConfigApplication.chemin_donnees()` et `core.config.etendre_chemin()` étendent `%VAR%`, `$VAR` et `~`. Une variable non définie ou un chemin relatif lèvent `ConfigurationInvalide`.
- **low**, second avis 5, **corrigé** : `langues_traduction` est non vide, sans doublon, avec des codes ISO 639 (`en`, `pt-BR`).
- **low**, revue, **reporté** : `cli index info/measure/verify-embedding` et `indexation.mesure_vec` / `verification_embedding` utilisent une seule `racine` pour lire l'Index et écrire `runs/`. Ces commandes de développement ne tournent pas dans l'exécutable gelé. Si l'une y est un jour embarquée, il faudra séparer lecture et écriture comme pour `measure run`. À vérifier en 12.12, avec un exécutable réel : aucun fichier créé sous `_MEIPASS` après une Question et une mesure.
