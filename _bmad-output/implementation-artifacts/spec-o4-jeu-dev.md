# Spec O4 — Jeu de développement (`eval run --jeu dev1`)

Méthodologie v2 (`plan-methodo-2026-10-20.md` §2 principe 5, §4 O4, §7 bis). Story à risque (jeu d'évaluation, gel) : relue avant code.

## But
Un jeu de **développement** pour toutes les décisions (hyperparamètres, mélange, routage), afin que v1.1 ne serve qu'à la mesure finale, une fois par configuration retenue.

## Règles
1. **Nom** : version `dev1` (`eval/jeu/dev1/`). `MOTIF_VERSION` de `core/items.py` (aujourd'hui `^v[0-9]+(\.[0-9]+)?$`) est étendu à `dev[0-9]+` ; `--jeu` et `eval gel --version` l'acceptent. Identifiants d'items au format existant (`<CODE>-<nnn>`) numérotés **à partir de 501** (`RD-501`…), pour ne heurter ni les identifiants ni les dossiers de cassettes `eval/cassettes/RD-xxx/` de v1.0/v1.1.
2. **Disjoint** :
   - de v1.0 et v1.1 : aucun item ni source identique (même URL, même texte source, même transcription), et recouvrement n-grammes / cosinus sous les seuils de `[anti_fuite]` ;
   - des **jeux d'entraînement existants** (`data/train/v*/train.jsonl`, dont v14 et v16) et des amorces des runs seed qui les ont produits, avec les mêmes seuils : contrôle fait par l'outil de construction (`eval/outils/`, hors paquet, qui peut lire `data/`) ;
   - des **jeux futurs** : `dev1` est ajouté aux versions protégées de l'anti-fuite (`data/seed.py`, `versions_protegees`, comme `calibrage` : si son fichier existe), pour que `seed` et `filter` excluent ses sources et quasi-doublons.
3. **Construction** : même procédé et même schéma d'item que v1.1 (`eval/SPEC-jeu-evaluation.md` §2-§5) : items écrits depuis des sources réelles par des agents Claude (autorisé pour l'évaluation, SPEC §1.4, jamais pour l'entraînement), puis **contre-vérification croisée** par DeepSeek V4 Pro et GLM-5.3 (OpenRouter) : cohérence item / référence / grille, ambiguïté (plusieurs réponses justes non prévues), fait de référence absent de la source. Un item jugé ambigu ou incohérent par l'un des deux est écarté, ou corrigé puis revérifié par les deux. Taux de rejet consigné. Outil `eval/outils/verifier_jeu_croise.py` (hors paquet, comme `construire_jeu.py`), client `slmsp.fournisseurs.client`, usage `juge-tiers-openrouter`, journal des juges tiers.
4. **Gel `relu-llm`** : nouveau statut dans `STATUTS_GEL` (`evaluation/config.py`), dans `ManifesteJeu.statut` (`core/schemas/manifeste_jeu.py`, `Literal`), dans les choix de `eval gel --statut` (`cli/eval.py`) et dans le message d'erreur de `gel`. Comme `relu`, les écarts de composition sont **bloquants**, mais mesurés contre les **cibles du jeu de développement** (règle 5), pas contre `CIBLES` de v1.1 (225 items), qui rendraient le gel impossible.
5. **Composition** : `CIBLES_DEV` dans `evaluation/config.py` : 20 items par tâche (Q, RD, CR, LC, CO, RE, CT, NR ; 160), difficultés (7, 7, 6) ; contraintes secondaires au prorata de v1.1, arrondies au supérieur : Q sans réponse ≥ 3 et part d'amorces réelles ≥ ½, RD producteurs ≥ 3 et repli ≥ 2, CR longues (> 4 000 mots) ≥ 4 ; thèmes répartis comme v1.1 (parts `PARTS_THEMES`). La vérification de composition (`verifier_jeu`) prend ses cibles selon la version (`dev*` → `CIBLES_DEV`). RD exige des cassettes enregistrées (`slmsp mcp record`, profil réseau de la liste blanche) : si l'enregistrement échoue, RD est réduit et l'écart consigné au MANIFEST (écart accepté explicitement par une option `--ecart-admis RD`, journalisée).
6. **Jamais mesure finale** : le Comparatif (`compare`) et toute sortie marquée « finale » **refusent une notation dont `jeu_statut` vaut `relu-llm`** (message explicite). Les notations v1.0 `provisoire` existantes restent lisibles comme aujourd'hui (pas de régression). Le gel `relu` reste réservé à Anaël (règle de procédure, consignée dans le MANIFEST : `gele_par`).
7. Fichiers : `eval/jeu/dev1/items.jsonl`, `eval/jeu/dev1/MANIFEST.json` (statut `relu-llm`, SHA-256, rapport de vérification croisée), `eval/construction/dev1/` (sources, verdicts DeepSeek/GLM, rejets), `eval/cassettes/RD-5xx/`.

## Notation du jeu dev
- Juge principal **configurable par jeu** : table `[jeux.dev1] juge_principal = "<nom de [juges_tiers]>"` dans `juges.toml` ; défaut et v1.1 inchangés (Claude). `ouvrir_juges(jeu=…)` construit alors un `JugeTiers` (même interface `juger(demandes) -> RapportJugement`, même grille et même prompt que le principal) à la place de `JugeClaude` ; usage de budget dérivé existant `juge-tiers-openrouter` (poste `openrouter`, aucune nouvelle imputation ni plafond). Le second juge Mistral est désactivé pour un jeu à juge tiers (`[jeux.dev1] second_juge = false`).
- `scores.json` porte `juge_principal` (nouveau champ du schéma `Scores`, défaut `"claude"` pour relire les scores existants) ; les scores dev ne se comparent qu'entre eux, à juge égal.
- **Choix du juge du jeu dev** : le plan dit DeepSeek. Mais DeepSeek sélectionne aussi les données (O1) : un jeu dev noté par lui récompense les données qu'il a choisies (le biais que le principe 3 évite pour Claude). Recommandation : **GLM-5.3** comme juge du jeu dev (famille distincte du juge de sélection et du juge de test). La config par jeu rend le choix réversible ; **décision d'Anaël** (défaut provisoire : `glm`).
- Baselines sur `dev1` (MiniCPM5-2B, Qwen3.5-2B, Qwen3.5-0.8B) lancées par l'orchestrateur après le gel.

## Découpage
- **O4a (code)** : `MOTIF_VERSION`, statut `relu-llm` (config, schéma, CLI), `CIBLES_DEV` et composition par version, refus `relu-llm` au Comparatif, `--jeu dev1`, juge principal par jeu, `juge_principal` dans les scores, `dev*` dans les versions protégées de l'anti-fuite, outil de vérification croisée et contrôle de disjonction (sur fixtures). Tests sur fixtures, aucun appel réel.
- **O4b (construction)** : agents Claude écrivent les items par tâche depuis les sources (réseau limité à la liste blanche) ; contrôle de disjonction ; l'orchestrateur lance la contre-vérification payante DeepSeek + GLM (~1-2 €, `openrouter`), l'enregistrement des cassettes RD, puis le gel `relu-llm` et le commit.

## Critères de fin
Tests : `dev1` admis par `MOTIF_VERSION`, `v1.1` inchangé ; `relu-llm` accepté par le gel et le contrôle de manifeste, composition jugée contre `CIBLES_DEV` (fixture conforme → gel, fixture à 19 items CR → refus) ; Comparatif refuse une notation `relu-llm`, accepte toujours v1.0 `provisoire` et v1.1 `relu` ; disjonction (fixture avec item dupliqué de v1.1 → refus ; fixture recouvrant un `train.jsonl` → refus) ; `seed` exclut une amorce recouvrant `dev1` ; `--jeu dev1` route vers le juge configuré, sans second juge ; `scores.json` porte `juge_principal`, anciens scores relus ; v1.1 inchangé (SHA du MANIFEST v1.1 identique avant/après) ; `tests/evaluation/test_gel.py`, `tests/eval_outils/test_jeu_v1.py`, `tests/compare/` verts.

## Revue de la spec
Relecture du 2026-10-20 (reviewer, avant code), contre `evaluation/{config,gel,notation}.py`, `core/items.py`, `core/schemas/{manifeste_jeu,scores}.py`, `data/seed.py`, `cli/eval.py`, `judge/config.py`, `eval/SPEC-jeu-evaluation.md`, `eval/jeu/v1.1/MANIFEST.json`.

| # | Gravité | Constat | Changement |
|---|---|---|---|
| 1 | high | Gel `relu-llm` « bloquant comme `relu` » alors que la composition est vérifiée contre `CIBLES` de v1.1 (225 items, Q 60, RD 40…) : un jeu de 160 items ne pourrait jamais être gelé. | `CIBLES_DEV` et contraintes secondaires au prorata ; composition choisie selon la version. |
| 2 | high | Disjonction « dans les deux sens » sans mécanisme : `seed` ne protège que v1.0, v1.1 et calibrage, et rien ne compare le jeu dev aux jeux d'entraînement existants (v14, v16), sur lesquels on va justement mesurer. | `dev*` dans les versions protégées ; contrôle contre `data/train/v*` et leurs amorces à la construction. |
| 3 | medium | `--jeu dev` refusé par `MOTIF_VERSION` ; identifiants `RD-001`… en conflit avec les cassettes de v1.1. | Version `dev1`, motif étendu, items numérotés à partir de 501. |
| 4 | medium | « Le Comparatif refuse un jeu autre que `relu` » casserait la lecture des notations v1.0 `provisoire`. | Refus ciblé sur `relu-llm`. |
| 5 | medium | Statut `relu-llm` à ajouter en plusieurs endroits non listés (`Literal` du schéma de manifeste, choix CLI, message). | Liste explicite. |
| 6 | medium | Juge principal par jeu : `ouvrir_juges` ne construit que Claude et Mistral ; nouvelle imputation inutile (le juge tiers a déjà l'usage `juge-tiers-openrouter`) ; second juge non précisé. | `JugeTiers` en principal par config, usage existant, second juge désactivé, champ `juge_principal` dans les scores. |
| 7 | medium | Jeu dev noté par DeepSeek, aussi juge de sélection des données : biais de sélection. | Recommandation GLM-5.3, config par jeu ; **décision d'Anaël**. |
| 8 | low | Contre-vérification croisée sans outil désigné. | `eval/outils/verifier_jeu_croise.py`. |

## Auto Run Result (O4a, code)

Statut : review. Livré : `MOTIF_VERSION` `dev[0-9]+` (items, manifeste), statut `relu-llm` (config, schéma, CLI, message), `CIBLES_DEV` / `CiblesJeu` et composition selon la version (`ecarts_composition(items, version)`), refus `relu-llm` au Comparatif (`JeuDeveloppement`), juge principal par jeu (`[jeux.dev1]`, `ouvrir_juges(jeu=…)`, `jeu_du_run`), `juge_principal` dans `Scores` (défaut `claude`), `dev*` dans `versions_protegees`, outil `eval/outils/verifier_jeu_croise.py` (`disjonction`, `verifier`).

Décisions prises seul :
- Les contraintes secondaires de `CIBLES_DEV` sont des **minimums** (spec : « ≥ »), alors que v1.1 garde des égalités ; RD demandes de valeurs : 3 (prorata arrondi au supérieur, non listé par la spec).
- `relu` et `relu-llm` sont tous deux bloquants ; les cibles dépendent de la version, pas du statut (`gel dev1 --statut relu` jugerait donc aussi contre `CIBLES_DEV`). Réservation de `relu` à Anaël : règle de procédure, non codée.
- `[jeux.<nom>]` n'accepte que `dev[0-9]+`. `second_juge = true` avec un juge tiers reconstruit le second juge Mistral ; jamais construit quand `false`.
- Le Comparatif refuse toute notation `relu-llm` retenue, même avec `--jeu dev1`.
- Disjonction : URL canonique, texte identique (valeurs ≥ 40 caractères), inclusion de n-grammes aux seuils de `[anti_fuite]`, identifiants ; **cosinus d'embeddings non recalculé** par l'outil (porté par `seed` / `filter` via les versions protégées).
- Vérification croisée : un juge sans verdict valide laisse l'item `incomplet` (rejouable, non retenu) ; verdicts en ajout seul dans `eval/construction/dev1/verdicts-croises.jsonl`, rapport de rejet dans `rapport-verification-croisee.json`.
- Juge du jeu dev : `glm` par défaut provisoire (**à confirmer par Anaël**).

Reports pour O4b : intégration du rapport de vérification croisée au MANIFEST (`gel` n'a pas de champ pour lui), option `--ecart-admis RD` du gel, `eval/construction/dev1/`, cassettes `RD-5xx`.

## Revue
Revue du 2026-10-20 (détail : `revue-o4a.md`) : 5 medium corrigés (`sources_attendues` et amorces seed dans la disjonction, `--jeu` cohérent avec le run repris, `eval comparer` refuse jeux ou juges différents sauf option, verdicts croisés indexés par SHA d'item), 2 low corrigés (textes courts identiques, `--mode-juge` refusé avec juge tiers), 2 low rejetés (extras présents dans le venv ; clé de cache déjà propre au modèle). Juge du jeu dev : GLM-5.3, décision d'Anaël confirmée.
