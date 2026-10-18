---
title: 'Trois petits Granite en Baseline'
type: 'feature'
created: '2026-10-18'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: ['{project-root}/_bmad-output/planning-artifacts/decisions.md']
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** la Baseline n'a que des modèles de 1B et plus ; Granite 4.0 H était écarté (Mamba, Windows natif).

**Approach:** ajouter `granite-4.0-350m` (dense, entraînable) et `granite-4.0-h-350m`, `granite-4.0-h-1b` (Mamba, `entrainable = false`), et faire admettre `mamba` au contrôle `dense` à cette condition (décisions d'Anaël du 2026-10-18, D8).

## Boundaries & Constraints

**Always:** fiches épinglées (révisions, SHA-256, tailles via l'API HF) ; `lm_eval_batch_size` fixe ; un type de couche inconnu reste écarté ; une fiche à couches `mamba` sans `entrainable = false` reste refusée.

**Never:** téléchargement de poids (`slmsp fetch modeles` après fusion) ; GPU ; entraînement des H.

</intent-contract>

## Code Map

- `config/modeles/granite-4.0-350m.toml`, `granite-4.0-h-350m.toml`, `granite-4.0-h-1b.toml` -- nouvelles fiches
- `src/slmsp/fetch/verifications.py` -- `COUCHES_INFERENCE_SEULE` + `mamba`, `CANDIDATS`
- `tests/fetch/test_verifications.py` -- tests réalignés et `test_toml_granite_petits`
- `_bmad-output/planning-artifacts/decisions.md` -- D8 : registre et décision

## Auto Run Result

Mesures (en-têtes safetensors, BF16) : 350m 352 379 904 (0,35B) ; h-350m 340 332 224 (0,34B) ; h-1b 1 461 538 368 (1,46B).

| Slug | Révision HF | GGUF Q4_K_M (octets) | GGUF bf16 (octets) | batch |
|---|---|---|---|---|
| granite-4.0-350m | bd8a1497 | 236 985 760 | 708 439 456 | 4 |
| granite-4.0-h-350m | 3b17b717 | 222 662 560 | 684 931 200 | 4 |
| granite-4.0-h-1b | d18cca4c | 901 162 208 | 2 928 332 288 | 2 |

Décisions : contexte 8192 pour les trois (comme granite-4.0-1b ; natif 32 768 / 131 072) ; Q4_K_M officiel existe pour les trois ; pas de F16 publié, seulement `bf16` (`[gguf_f16]`, precision bf16) ; `chat_template_force = false` et `protocole_outils = "natif"` non sondés (template identique à celui de granite-4.0-1b, SHA-256 égal), à confirmer par le contrôle `chat_template` et la sonde H-TOOLS. h-1b n'a ni `merges.txt` ni `vocab.json`.

À confirmer par Anaël : message du contrôle `dense` généralisé (« hybride Mamba admis… ») ; mélange `linear_attention` + `mamba` désormais admis si non entraînable.

Report : exécuter `slmsp fetch modeles --candidats` (contrôles `serveur`, `chat_template` sur llama.cpp) après la fusion ; sonde H-TOOLS des trois.
