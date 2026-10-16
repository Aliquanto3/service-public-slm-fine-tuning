# Préparation des benchmarks réels, 2026-10-16

Branche `prep/benchmarks`. Aucun appel payant, aucun GPU. Tout ce qui est à confirmer par Anaël est marqué ainsi.

## Jeux épinglés et téléchargés (dépôt principal)
`slmsp fetch benchmarks` : `data/raw/benchmarks/<jeu>/<révision>/<chemin du dépôt>` (les chemins sont désormais conservés).

| Benchmark | Jeu (révision) | Fichiers, taille | Remarque |
|---|---|---|---|
| mcq_eval | AgentPublic/MCQ-eval `d104aa4f` | classeur xlsx, 320 Ko | feuille `QCM_version_albert_dedup` : 42 questions (21 ont « E : aucune » pour bonne réponse) |
| bfcl | gorilla-llm/Berkeley-Function-Calling-Leaderboard `61fc0608` | 3 questions + 2 `possible_answer`, 850 Ko | BFCL_v3, 400 simple, 200 multiple, 240 irrelevance, 50 tirés par catégorie |
| traduction (WMT14) | wmt/wmt14 `b199e406` | `fr-en/test-…parquet`, 536 Ko | 3003 phrases, sert les deux sens ; 500 par sens |
| traduction (FLORES) | facebook/flores `71abf77d` | **non téléchargé** | accès conditionnel, 401 |

Jeux lm-eval (hors `fetch`, figés par le cache HF, révisions dans `[options.jeux_hf]` de chaque toml) : IFEval `966cd895`, Belebele `7899cdfa`, CrowS-Pairs `3550adcf`, Global-MMLU-Lite `36c2fd75` (le moteur lit **Lite**, pas Global-MMLU complet), cais/mmlu `c30699e8`, french_bench (arc `25a80534`, hellaswag `f9f7e441`, grammar-vocab `dcbe950e`). Cache : 61 Mo.

## Variables d'environnement
- `HF_HOME` est imposé par `env_sous_processus` à `<models>/.cache-hf` : le cache est dans `models/.cache-hf` (dépôt principal, ignoré par git). Ne pas le fixer ailleurs.
- `HF_HUB_OFFLINE=1` et `HF_DATASETS_OFFLINE=1` sont posés par le moteur ; `PYTHONUTF8=1` aussi (voir correctifs).
- `NLTK_DATA=C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning\data\cache\nltk_data` (punkt_tab, requis par IFEval ; `data/cache/` est ignoré). À poser avant `bench run`.
- `HF_TOKEN` dans `.env` (jamais lu ici) : seulement pour FLORES.

## Correctifs de code (tests ajoutés)
- `fetch benchmarks` conservait seulement le nom du fichier : `BFCL_v3_simple.json` et `possible_answer/BFCL_v3_simple.json` se seraient écrasés. Le chemin relatif est conservé.
- BFCL : le moteur lisait `<cat>.jsonl` et `reponses/` (devinés) ; format réel `BFCL_v3_<cat>.json` (lignes JSON) et `possible_answer/`.
- `ast_checker` : signature confirmée sur bfcl-eval 2026.3.23, mais `model_name="slmsp"` levait KeyError (clé de `MODEL_CONFIG_MAPPING`) : tout simple/multiple aurait compté faux. Remplacé par `gorilla-openfunctions-v2`. Vérifié sur 40 items réels (réponses attendues rejouées) : 100 % hors 2 artefacts du script de test. `envs/bfcl` : ajout de `soundfile==0.14.0` (import transitif de qwen_agent) et `uv.lock` créé.
- Traduction : lecture des parquet WMT14 (colonne `translation`) et FLORES (`sentence`, **format non vérifié**, jeu inaccessible) ; score agrégé `moyenne.chrf`.
- MCQ-eval : le jeu est un xlsx ; lecteur en bibliothèque standard.
- lm-eval plantait sous Windows (`UnicodeEncodeError` sur ↑↓ en tube) après avoir écrit ses résultats, d'où un code non nul : `PYTHONUTF8=1` dans `env_outil`.
- `french_bench_mc` est un tag sans score agrégé : groupe `french_bench_mc_agrege` (moyenne simple de `acc`), `tache` du toml changée.
- BFCL : score agrégé `moyenne.precision`.

## Comparatif
`config/comparatif.toml` renseigné pour les 9 benchmarks (clés vérifiées par un passage `lm_eval --model dummy --limit 2` sur chaque tâche, CPU) : à confirmer par Anaël (métrique, agrégats, `crows_pairs_french` en sens bas alors que l'idéal est 50 %).

## Commande de `bench run` (orchestrateur, depuis le dépôt principal après intégration, GPU libre)
```
$env:NLTK_DATA = "C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning\data\cache\nltk_data"
uv run --extra bench slmsp bench run --modele base:<slug> --socle
```
Durée estimée (non mesurée), par modèle : QCM sur poids HF 30 à 60 min (MMLU : `--limit` est par sous-tâche, donc `limite = 500` ne coupe presque rien et ~14 000 questions tournent ; à confirmer par Anaël), IFEval et traduction contre llama-server 1 à 2 h par variante, BFCL moins de 15 min. FLORES sauté tant que non obtenu.

## Reste bloqué
- FLORES-200 : accepter les conditions sur https://huggingface.co/datasets/facebook/flores et mettre `HF_TOKEN` dans `.env`, puis épingler les 5 fichiers (voir commentaire de `traduction.toml`) et relancer `fetch`. Sans cela, la traduction ne mesure que WMT14.
- Modèles GGUF seuls (ex. ministral-3-8b) : QCM sautés, sans poids HF.

## Revue
- medium, corrigé (documenté) : `limite` de mmlu.toml s'applique par sous-tâche (comportement lm-eval, pas de limite globale possible sans relancer par sous-tâche) ; description et commentaire du toml le disent (≈ 14 000 questions, durée déjà indiquée ci-dessus). Choix d'une vraie limite à confirmer par Anaël.
- medium, corrigé : `[options.jeux_hf]` est vérifié avant tout run lm-eval (`verifier_cache_hf`) ; erreur `ConfigurationInvalide` listant les révisions présentes si écart ; test ajouté.
- medium, corrigé : traduction publie `moyenne_wmt.chrf` (paires WMT14 mesurées) ; `moyenne.chrf` n'existe que si aucune paire demandée n'est sautée ; `details.paires_mesurees` et `paires_demandees` consignent la composition. Le Comparatif lit `moyenne_wmt.chrf` ; tests ajoutés.
- medium, corrigé : `moyenne.precision` de BFCL exige toutes les catégories configurées avec une précision (sinon pas d'agrégat) ; composition documentée (simple, multiple, irrelevance, moyenne simple) ; test ajouté.
- medium, corrigé : sens `cible` ajouté au Comparatif (champ `cible`, validé) ; crows_pairs_french à 50 % ; test ajouté.
- low, corrigé : parquet illisible ou colonne absente (traduction) et classeur xlsx illisible (MCQ-eval, avec fichier et numéro de ligne) lèvent une erreur explicite ; test ajouté pour le parquet et la ligne xlsx.
- low, corrigé : description de Global-MMLU-Lite (le jeu lu est Lite, ≈ 400 questions).
- low, constaté : aucun test réel de `bfcl_eval` dans la suite (absent de l'environnement de test) ; la vérification réelle a été faite à la main sur 40 items, voir ci-dessus. Pas de test automatisé ajouté.
