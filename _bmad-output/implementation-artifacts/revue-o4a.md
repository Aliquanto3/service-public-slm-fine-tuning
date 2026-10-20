# Revue O4a — jeu de développement dev1 (2026-10-20)

Reviewer (Opus), après fusion de main (E1b, C8, C9, O5 : sans conflit) dans `story/o4a-jeu-dev`, avec la liste du second avis (Haiku). D1 : aucun contenu d'entraînement, d'exemple ni d'amorce rédigé ; fixtures factices ; le prompt de contre-vérification ne contient aucun exemple de verdict. Décision d'Anaël : GLM-5.3 juge du jeu dev (confirmée, commentaire de `config/juges.toml` mis à jour).

| # | Gravité | Constat | Suite |
|---|---|---|---|
| 1 | medium | `urls_item` ignore `sources_attendues` des Q : une même source attendue passerait la disjonction. | Corrigé : URL de `sources_attendues` (niveau item ou `reference`) incluses ; test. |
| 2 | medium | Disjonction sans les amorces des runs seed (spec règle 2). | Corrigé : `runs/data-seed/*/amorces.jsonl` indexé (texte identique et n-grammes) ; test. |
| 3 | medium | `eval run --phase toutes --reprendre X --jeu v1.1` ouvrait les juges du jeu donné, pas de celui du run (refus seulement ensuite par `reprendre_generation`). | Corrigé : jeu lu dans le run repris, `--jeu` différent refusé (usage) avant l'ouverture des juges ; test. |
| 4 | medium | `eval comparer` (E1b) comparait des runs de jeux ou de juges principaux différents avec un simple avertissement. | Corrigé : refus (code usage) si jeu ou `juge_principal` diffèrent, sauf `--autoriser-jeux-differents` (avertissement) ; jeu `relu-llm` signalé ; tests. |
| 5 | medium | Verdicts croisés en ajout seul indexés par `item_id` seul : un item corrigé gardait son ancien verdict. | Corrigé : `item_sha256` (JSON canonique) dans chaque ligne ; un item modifié ou sans empreinte est revérifié, le rapport ne compte que les verdicts à jour ; test. |
| 6 | low | Textes identiques de moins de 40 caractères (questions courtes, amorces) non détectés. | Corrigé : égalité exacte normalisée dès 3 mots ; test. |
| 7 | low | `--mode-juge` ignoré en silence avec un juge principal tiers ; commentaire « plafond Anthropic » signalé. | Corrigé : `--mode-juge` refusé pour un jeu à juge tiers (test). Commentaire fautif non retrouvé dans le diff : rejeté. |
| 8 | low | Tests dépendant des extras judge/data. | Rejeté : venv principal (extras présents) ; tests verts. |
| 9 | low | Clé de cache des verdicts sans nom du juge. | Rejeté : la clé porte déjà le modèle et l'effort (distincts par juge) ; ajouter le nom invaliderait le cache existant des juges tiers. |

Tests : `tests/evaluation`, `tests/eval_outils`, `tests/compare`, `tests/judge`, `tests/data/test_seed.py`, `tests/test_architecture.py`, `tests/cli` verts ; ruff, format et contrôle rapide OK.
