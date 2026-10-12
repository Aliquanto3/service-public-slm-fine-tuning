# Recherche : benchmarks standardisés publics (2026-10-11)

Légende : [V] vérifié pendant la recherche, [M] cité de mémoire et à vérifier.

## Socle recommandé (< 2 h sur RTX 3050, modèle en 4 bits, temps à calibrer avec `--limit`)
1. `french_bench_mc` [V], lm-evaluation-harness, 3-shot : arc_challenge, hellaswag, grammar, vocab, xnli, boolqa. Environ 25 min.
2. `belebele_fra_Latn` [V], dataset `facebook/belebele`. Environ 5 min.
3. Global-MMLU fr [M] (`CohereLabs/Global-MMLU`, ou la version Lite), avec `--limit` à 2 000. Environ 20 min.
4. **AgentPublic/MCQ-eval** [V] : QCM sur le périmètre France services, licence Etalab 2.0. Demande un YAML lm-eval personnalisé, car le format des colonnes n'est pas vérifié. Environ 5 min. C'est le seul benchmark public proche du domaine.
5. **BFCL** [M] (`ShishirPatil/gorilla`, `pip install bfcl-eval`), catégories simple + multiple + irrelevance, sous-échantillonné. Hors lm-eval. Environ 25 min.
6. Traduction : `wmt14-en-fr` / `wmt14-fr-en` [V], limités à environ 500 phrases et mesurés en chrF, ou FLORES-200 via sacrebleu. Environ 15 min.
7. Non-régression : `ifeval` + `mmlu` anglais (limite 1 000) + `crows_pairs_french` [V] pour les biais. Environ 20 min.

## Autres ressources
- FrenchBench génératif : fquadv2, orangesum, trivia (plus lent ; FQuAD sous licence non commerciale [M]).
- AgentPublic : `sp_questions_corpus` et `assistant_ia_questions_corpus` (MIT, sans réponses de référence confirmées), `piaf` (QA extractive), `service-public` (corpus), `evalap-*` (plateforme EvalAP de l'Etalab).
- Sécurité : TruthfulQA, BBQ, XSTest, HarmBench [M].

## Lacunes, à couvrir par des jeux maison
Aucun benchmark public n'existe pour :
- le tool calling en français ;
- le langage clair / FALC ;
- le RAG administratif.

Ces trois capacités sont couvertes par le jeu d'évaluation maison du lot 0.

Aucun leaderboard français actif n'a été confirmé.

## Points non vérifiés
- Noms exacts des tâches Global-MMLU et FLORES dans le harnais.
- Licences des jeux de données.
- Colonnes de MCQ-eval.
- Tâches françaises de lighteval.
- Temps d'exécution réels.

## Sources
- github.com/EleutherAI/lm-evaluation-harness/tree/main/lm_eval/tasks/french_bench
- huggingface.co/datasets/AgentPublic/MCQ-eval
- arxiv.org/abs/2402.00786
- github.com/ShishirPatil/gorilla
- huggingface.co/datasets/CohereLabs/Global-MMLU
- huggingface.co/datasets/facebook/belebele
