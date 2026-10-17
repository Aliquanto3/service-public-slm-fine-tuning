---
title: 'Liste --candidats alignée sur le registre D8'
type: 'feature'
created: '2026-10-17'
status: 'review'
baseline_commit: '012f7f6'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/planning-artifacts/decisions.md (D4, D8)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-hybrides-baseline.md'
warnings: []
deferred:
  - 'minicpm5-1b (candidat au fine-tuning) : le masque de chat template échoue avec le template officiel (rendu du message 2 non préfixe du rendu complet, variante `generation` requise). Constaté en lançant test_candidat_reel_masque_sur_les_tours_assistant ; à traiter avant tout entraînement.'
---

## Intent
Décision d'Anaël du 2026-10-17 : `verifications.CANDIDATS` (utilisée par `slmsp fetch modeles --candidats`) suit le registre des Modèles de base de D8. Elle listait encore l'ordre D4 (ministral-3-3b, smollm3-3b, qwen-4b, ministral-3-8b, écartés) et aurait téléchargé des modèles écartés.

## Approach
- `CANDIDATS = (granite-4.0-1b, minicpm5-1b, eurollm-1.7b, qwen3.5-0.8b, qwen3.5-2b)` : les candidats au fine-tuning, puis les Qwen « Baseline seulement ». Les statuts et slugs du registre D8 correspondent à cette liste, sans écart.
- `--candidats` n'implique rien d'autre : le téléchargement et les contrôles (`dense`, `fp8`, `vision`, `chat_template`, `serveur`) parcourent la même liste, les Qwen passent `dense` grâce à `entrainable = false`, `--f16` avertit si la fiche n'a pas de `gguf_f16`, l'export d'état suit `config.slugs`. Aucun code à changer hors la constante ; pas de doc qui cite l'ancienne liste.
- `decisions.md` : une ligne sous le registre de D8, D4 non réécrite.

## Tests
`tests/fetch/test_verifications.py` : `test_candidats_alignes_sur_le_registre_d8` (égalité, aucun écarté, entraînable pour les trois premiers et pas pour les Qwen) et `test_candidat_registre_epingle` (révisions, SHA). Les assertions propres aux anciens candidats (GGUF Q4_K_M, contexte 8192, tailles réseau) passent sur `ANCIENS_CANDIDATS`. `tests/train/test_masque.py` : `eurollm-1.7b` ajouté à sa liste (tokenizer local présent, test lent passé) ; sans poids le test saute déjà (`_dossier_hf`).

## Auto Run Result
- Statut : review. Pas de fusion. `decisions.md` modifié sur demande de l'orchestrateur.
- `minicpm5-1b` n'est pas ajouté à `test_masque.py` : son template réécrit l'historique, le masque échoue (voir `deferred`). Report, pas de correctif ici.
- Tests ciblés : 264 passés (`tests/fetch`, `tests/cli`, `tests/train/test_masque.py`).
