---
title: 'Story 2.4 : Mesure H-EMB, compatibilité de l''embedding de requête avec les vecteurs MediaTech'
type: 'feature'
created: '2026-10-16'
status: 'review'
baseline_revision: 'a39f199'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
deferred:
  - 'Mesure réelle H-EMB non lancée (consigne du run : code seul).'
  - '`config/modeles/bge-m3-f16.toml` non créé : prévu seulement si la mesure Q8_0 échoue.'
---

## Intent

**Problème :** l'Index local contient les vecteurs MediaTech ; les requêtes sont vectorisées par BGE-M3 GGUF Q8_0 (`llama-server`). Rien ne prouve que les deux espaces coïncident (H-EMB).

**Approche :** `slmsp index verifier-embedding` tire 200 chunks (graine 42), les revectorise via `EmbedderPort`, et consigne dans `runs/measure/<run_id>/` le cosinus par chunk, le minimum, la moyenne et le recall@10 (recherche exacte avec le vecteur recalculé contre celle avec le vecteur MediaTech).

## Critères d'acceptation

- Étant donné un Index et un embedder, la commande écrit `resultat.json` (`ResultatMesure`, slug `h-emb`) et `cosinus.json` (rang, chunk_id, cosinus, recall par chunk).
- `confirmee` si cosinus moyen ≥ 0,99 et recall@10 moyen ≥ 0,98 (baisse ≤ 2 points, référence = 1) ; sinon `infirmee` avec repli : refaire avec `bge-m3-f16`, réindexation = décision d'Anaël.
- Seuils, échantillon, graine, k dans `config/index.toml` `[verification_embedding]` (défauts du schéma identiques).

## Conception

- `indexation/verification_embedding.py` : `verifier_embedding(racine, version, config, embedder, *, modele, echantillon, graine)`, `cosinus_par_ligne`, `recall_a_k`, `verdict_h_emb`, `tirer_rangs`. Embedder injecté (port), run `partiel-erreur` en cas d'exception.
- `index/config.py` : `ConfigVerifEmbedding` (section optionnelle). `indexation/mesure_vec.py` : `_version` renommé `version_index` (réutilisé).
- `cli/index.py` : `verifier-embedding` (`--echantillon`, `--graine`, `--modele`, `--variante`, `--racine`, `--version`) ; `_ouvrir_embedder` démarre `ServeurLlama` (point d'injection des tests).

## Fichiers

`src/slmsp/indexation/verification_embedding.py`, `src/slmsp/cli/index.py`, `src/slmsp/index/config.py`, `src/slmsp/indexation/mesure_vec.py` (renommage), `config/index.toml`, `tests/indexation/test_verification_embedding.py`.

## Vérification

- Tests : `uv run --extra data pytest -q --tb=short tests/indexation/test_verification_embedding.py` (embedder factice = vecteurs MediaTech bruités, cas confirmée et infirmée, CLI par injection ; un test `lent` réel, ignoré sans `SLMSP_RACINE_REELLE`).
- **Commande à lancer plus tard (mesure réelle, CPU, sans API)** :
  `uv run --extra data slmsp index verifier-embedding --echantillon 200 --graine 42 --racine C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning`
  avec `SLMSP_MODELS_DIR` et `SLMSP_VENDOR_DIR` du dépôt principal. En cas d'infirmation : créer `config/modeles/bge-m3-f16.toml`, relancer avec `--modele bge-m3-f16`.

## Auto Run Result

Status: review
- Décisions prises seul : recall@10 comparé à 1 (la référence MediaTech se retrouve elle-même) ; seuils en config plutôt qu'en constantes ; variante `cpu` par défaut (`--variante cuda` prend le verrou GPU) ; code de sortie 0 même si H-EMB est infirmée (comme `mesurer`). À confirmer par Anaël : le critère « baisse de 2 points » lu comme recall moyen ≥ 0,98.
- Mesure réelle non faite : verdict H-EMB inconnu.

## Revue

- medium, corrigé : provenance incomplète (seul le slug `modele` consigné) ; `serveur` (`ServeurLlama.description()` : variante, tag llama.cpp, GGUF, contexte, pooling, plus `gguf_sha256`) est désormais dans `parametres` du run et de `resultat.json`.
- low, corrigé : le chunk figurait dans ses propres voisins (recall@k gonflé) ; `_voisins` l'exclut (k+1 puis retrait).
- low, corrigé : `--modele bge-m3-f16` sans fichier de config renvoie une `ConfigurationInvalide` claire.
- low, rejeté : `_verifier_embedding` « non défini » (Pyright) : défini plus bas dans le module, résolu à l'appel, faux positif.
