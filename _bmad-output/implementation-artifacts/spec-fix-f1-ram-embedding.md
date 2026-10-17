---
title: 'Serveur d''embedding : micro-lot par usage, RAM bornée'
type: 'bugfix'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred:
  - summary: "`data filter` garde le micro-lot 8192, soit jusqu'à 8,5 Go sur un texte de 7 900 tokens. Passer à 4096 changerait la troncature, donc les vecteurs et les verdicts du filtre : à confirmer par Anaël."
    location: config/modeles/bge-m3.toml
  - summary: "La RAM reste au pic après l'appel (le serveur garde ses tampons). Une question collée très longue coûte 2,4 Go jusqu'à l'arrêt du serveur. Pas de relance du serveur prévue."
    location: src/slmsp/inference/serveur.py
---

<intent-contract>

## Intent

**Problem:** `ServeurLlama.arguments` lance le serveur d'embedding BGE-M3 avec `-c`, `-b` et `-ub` à 8192 pour tous les usages. Pendant `slmsp data filter`, on a relevé environ 8 Go de RAM. La cible est un PC de 16 Go, sans GPU, avec Teams, Edge et Outlook ouverts. Ce PC embarque l'embedding des questions et des passages de l'Index.

**Approach:** Le micro-lot (`-c`, `-b`, `-ub`) se règle par usage dans `config/modeles/<slug>.toml` (`micro_lot`). `ServeurLlama(usage=...)` le passe au serveur. La limite de troncature d'`EmbedderLlama` en découle (`contexte_max` devient obligatoire, `ServeurLlama.embedder()` y passe le micro-lot), si bien que les deux ne peuvent pas diverger.

## Boundaries & Constraints

**Always :**
- Une entrée doit tenir dans un micro-lot : `EmbedderLlama` tronque à `micro_lot - 16` tokens.
- Un usage absent de `micro_lot` prend `contexte` : le comportement antérieur.
- `micro_lot` est réservé aux modèles d'embedding, avec des valeurs comprises entre 1 et `contexte`.
- Les modèles de génération ne changent pas : `-c` vaut `contexte`, sans `-b`/`-ub` (défauts de llama.cpp, 2048/512).

**Never :** aucun changement des vecteurs de l'Index. Ils viennent de MediaTech (`embeddings_bge-m3`) et ne sont jamais recalculés (`indexation/construction.py`).

## Mesures (CPU, BGE-M3 Q8_0, llama.cpp b11429, 2026-10-17)

Working set de `llama-server --embedding --pooling cls --parallel 1`, avec `-c = -b = -ub`. Chaque réglage tourne dans un processus neuf ; les étapes s'enchaînent dans l'ordre (pic croissant).

| `-c`/`-b`/`-ub` | Repos | Question (15 tokens) | Plus long chunk (1 163 tokens) | Micro-lot plein | Durée, micro-lot plein |
|---|---|---|---|---|---|
| 8192 | 498 Mo | 514 Mo | 1 675 Mo | 8 466 Mo (7 892 tokens) | 33,8 s |
| 2048 | 498 Mo | 513 Mo | 1 660 Mo | 2 402 Mo (1 901 tokens) | 4,4 s |
| 1536 | 498 Mo | 513 Mo | 1 658 Mo | 1 935 Mo (1 435 tokens) | 3,5 s |

- **Cause :** la RAM ne dépend ni de `-c` ni du cache (BGE-M3 est un encodeur, sans cache KV). Elle suit la plus longue entrée traitée, puisque les tampons de calcul croissent avec le nombre de tokens d'un micro-lot. Le micro-lot borne donc le pire cas. Les 8 Go de `data filter` viennent de textes d'environ 8 000 tokens. Le pic reste acquis jusqu'à l'arrêt du serveur.
- Vecteur du plus long chunk : cosinus 1,0 entre 8192, 2048 et 1536. Le micro-lot ne change pas le vecteur d'une entrée non tronquée.
- **Taille des chunks de l'Index** (`chunk_text`) :
  - service-public : 35 758 chunks, p99 de 4 354 caractères, maximum de 5 012 caractères, soit 1 163 tokens au plus parmi les 30 plus longs ;
  - data-gouv : 1 000 caractères au maximum.
- Contrôle réel par `ServeurLlama` (usage `passage`) : un texte de 126 889 caractères est tronqué à 13 088, sans erreur 500, avec un pic de 2 336 Mo.

## Réglages choisis

`config/modeles/bge-m3.toml` et `bge-m3-f16.toml` : `micro_lot = { passage = 2048, texte_long = 8192 }`.
- `passage` (défaut de `ServeurLlama`) sert à l'application, au Harnais, à l'évaluation, à la recherche de `data generate` et à H-EMB. Le plus long chunk fait 1 163 tokens, la marge est de 869 tokens, et le pire cas passe de 8,5 Go à 2,4 Go.
- `texte_long` sert à `data filter` (`cli/data.py`) : 8192, c'est-à-dire la troncature antérieure, inchangée.
- Génération : aucun changement. La mesure ne porte que sur l'embedding, aucun gain n'y est établi.

## Code Map

- `src/slmsp/core/schemas/config_modele.py` : `UsageEmbedding`, `micro_lot`, `micro_lot_pour()` et validation.
- `src/slmsp/inference/serveur.py` : `usage`, `micro_lot`, `contexte` (`-c`), arguments, `description()` (`usage`, `micro_lot`) et `embedder()`.
- `src/slmsp/inference/embedding.py` : `contexte_max` obligatoire, supérieur à 16 ; `CONTEXTE_MAX` supprimé.
- `src/slmsp/cli/data.py` : `data filter` passe en `usage="texte_long"`.
- `tests/inference/test_serveur.py` : arguments par usage, cohérence entre troncature et micro-lot, validation, configurations BGE-M3 réelles.

## Verification

- `uv run pytest -q --tb=short tests/inference tests/indexation tests/data tests/cli tests/core tests/harness`
- Suite complète, `ruff check`, `ruff format --check` et `outils/controle_rapide.py`.

## Auto Run Result

- Deux usages seulement (`passage`, `texte_long`) : la solution la plus simple, puisque l'application et l'Index ont la même borne.
- En embedding, `-c` vaut le micro-lot (avec `--parallel 1`, un contexte plus grand ne sert à rien). `run.json` archive donc `contexte` = micro-lot.
- `data filter` reste à 8192 pour ne pas changer ses verdicts : voir `deferred`, **à confirmer par Anaël**.
- 2048 plutôt que 1536 pour `passage` : la marge couvre une réindexation avec titre préfixé (H-EMB infirmée, réindexation à décider). L'écart de pic n'est que de 0,5 Go.

</intent-contract>
