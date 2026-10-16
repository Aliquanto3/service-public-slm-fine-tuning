# Travail reporté

## Deferred from: code review of lot 2, évaluation (2026-10-12)

- **W1. TRAITÉ (dette/lot-1)** : `test_cli_toutes_apres_generation_partiel_erreur` couvre `eval run --phase toutes` après une génération `partiel-erreur` (run `eval-notation` créé, code 1) ; aucun défaut du code.
- **W-ask. `slmsp ask --journal` filtré par horodatage seul** (`cli/ask.py`) : le journal SQLite ne porte aucun identifiant de session ou d'exécution (schéma figé à 8 colonnes, AD-4) ; des `ask` concurrents peuvent se mêler. Un filtre exact demande une colonne `session` (nouvelle version de schéma) : décision à confirmer par Anaël. Les trois autres points mineurs de la 4.5 sont corrigés (AppelNonConforme affiché, Index ouvert avant les serveurs, pas de JournalSqlite en `--hors-ligne`).
- **W3. Jeu v1.1 : déclarer `valeurs_attendues.colonnes` sur les 5 items RD de la méthode `valeurs`, puis geler** (issu de D1, option 1). Le correctif P8 lit la liste. Sans elle, le jeu v1.0 garde un biais : RD-017, RD-010 et RD-039 peuvent être notés faux sur une réponse exacte. Colonnes proposées : RD-010 `Nbre_bailleurs` et `Nbre_logements` ; RD-017 `Nombre` ; RD-023 `Année` et `Note Index` ; RD-030 `REG` et `CHEFLIEU` ; RD-039 `Effectifs` et `IPS`. Il faut une nouvelle version, l'export de revue, une relecture humaine et `gel --statut relu`, à faire avant la Baseline complète.

## Deferred from: revues croisées du commit 793bd33, story 10.1 (2026-10-13)

Trois relectures indépendantes (Haiku, Sonnet et Opus) ont été faites pendant le test comparatif des modèles. Les 5 correctifs du triage ont été appliqués en 10.1 (99e286d). Les constats suivants restent à traiter avant 10.4, ou avec elle :

- **W4.1. Méthodes « deduite » listées comme disponibles sans avoir été exécutées** (`environnement.py:558-572`).
  - `use_dora` n'est jamais posé par `poser_lora`.
  - ORPO passe par un autre entraîneur.
  - PiSSA est incompatible avec une base nf4.
  - LoRA bf16 est déclarée disponible pour SmolLM3 3B.
- **W4.2. Statut du run.**
  - Une longueur en `erreur` ou en `debordement` laisse le run `complet`, avec le code 0 (`:741-749`).
  - Un débordement dès la première longueur marque `qlora` comme indisponible (`:738`).
- **W4.3. Toute exception du chargement 4 bits devient `ErreurQuantification`**, y compris un OOM non typé (`:357`). `prepare_model_for_kbit_training` est hors du `try` (`:361`).
- **W4.4. Reproductibilité.**
  - Les poids LoRA sont posés avant `set_seed`.
  - L'adaptateur est réutilisé d'une longueur à l'autre : sur le run 14bd, la perte passe de 14,90 à 11,94.
  - `--longueurs` n'est ni trié ni dédoublonné.
  - `arguments_entrainement` n'est consigné que pour `longueurs[0]`.
- **W4.5. VRAM non représentative d'un QLoRA de production** : conversion en fp32 par `prepare_model_for_kbit_training`. Côté Unsloth, les gradients sont délégués au CPU, il n'y a pas de contrôle de débordement, et `load_in_4bit` n'est pas nf4 avec double quantification.
- **W4.6. Robustesse.**
  - La détection Mamba ne lit que `layer_types`.
  - `sonde.json` n'est pas écrit sur une exception non OOM.
  - `print` en cp1252 dans `envs/unsloth/sonde.py`.
  - `--longueur-unsloth` n'est ni validé ni consigné.
  - Motif trompeur quand la sonde TRL échoue avec `--unsloth`.
- **W4.7. Tests absents** : longueur en `erreur` après `ok`, débordement à la première longueur, erreur au chargement 4 bits hors bitsandbytes, dépendance entre longueurs, statuts `deduite`.

## Deferred from: code review of lot 3b, téléchargeur et inférence (2026-10-13)

- **W5. `fetch llamacpp` écrit sous `<--racine>/vendor`, alors que `ServeurLlama` lit `SLMSP_VENDOR_DIR` en priorité** (`src/slmsp/fetch/llamacpp.py:72`, `src/slmsp/inference/serveur.py:73`).
  - Conséquence : dans un worktree où `SLMSP_VENDOR_DIR` est défini, un `fetch llamacpp` sans `--racine` retélécharge le tag dans le worktree, et le serveur continue de lire l'autre copie.
  - Piste : quand `--racine` est absent, faire suivre `SLMSP_VENDOR_DIR` à `fetch`, comme `models/` suit `SLMSP_MODELS_DIR`.
  - Motif du report : choix d'interface sur le sens de `--racine`.
- **W6. `evaluation/modele_ref.py` joint `gguf.fichier` complet** (`src/slmsp/evaluation/modele_ref.py:74`). C'est le même écart que P1 du lot 3b : un GGUF rangé dans un sous-dossier du dépôt serait déclaré absent.
  - Piste : reprendre `PurePosixPath(config.gguf.fichier).name`, ou mieux, `ServeurLlama(config, slug=…).gguf`.
  - Motif du report : fichier hors de la cible du lot 3b (lot 2). Aucun TOML actuel n'est concerné.

## Deferred from: code review of lots 3c et 4, lecteur d'items, gabarits, CLI index et mcp (2026-10-13)

- **W7. Le Générateur n'applique pas à l'exécution l'interdiction de `?`, de « » et de `"` dans les gabarits** (`src/slmsp/mistral/generateur.py`, `_gabarit`).
  - Constat : la spec 9.2 (AC4) l'exige des 11 gabarits de `config/prompts/generateur/`, mais seul `tests/mistral/test_gabarits_generateur.py` la tient. Un gabarit édité avec une réponse citée passerait `valider_gabarit` au runtime, et seul son SHA-256 serait journalisé. `medium`, non vérifié sur un cas réel.
  - Piste : appliquer la même liste d'interdits dans `Generateur._gabarit`, après `valider_gabarit`. Elle ne peut pas aller dans `valider_gabarit`, qui sert aussi aux gabarits de Tâche, où ces caractères sont permis.
  - Motif du report : fichier hors de la cible du lot 3c et 4.
- **W8. Trois angles de l'anti-fuite ne sont pas couverts** (`src/slmsp/core/items.py` : `_feuilles_texte`, `identifiants_proteges`).
  - Les valeurs numériques (`valeurs_attendues` en entiers ou flottants) ne produisent aucune empreinte.
  - Les URL protégées sont comparées brutes (casse, `/` final, `http` ou `https`, ordre des paramètres).
  - Les `dataset_id` et `resource_id` donnés par des règles `contient_un_de` ou `mot_entier_un_de`, ou par un `exact` en liste, ne sont pas collectés.
  - `low` à `medium`, non vérifié : l'effet dépend du comparateur de la story 9.3. À traiter avec lui (voir D2 du rapport `revue-code-lots-3c-4.md`).
