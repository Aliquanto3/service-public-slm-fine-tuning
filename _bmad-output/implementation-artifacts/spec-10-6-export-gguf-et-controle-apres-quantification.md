---
title: 'Story 10.6 — Export GGUF et contrôle après quantification'
type: 'feature'
created: '2026-10-16'
status: 'review'
baseline_revision: 'b839f3b'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-10-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/note-conception-10-6-export-gguf.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
deferred:
  - 'Contrôle après quantification niveau 1 (KLD par llama-perplexity, lanceur inference.serveur.kl_divergence) et niveau 2 (Tâches F16 contre Q4, bascules appariées)'
  - 'Réserve de contrôle (~40 conversations exclues de 10.4) et corpus de contrôle'
  - 'Comparaison /tokenize de llama-server contre HF sur 20 conversations, génération de fumée (token de fin)'
  - 'Dépendance gguf par chemin dans pyproject.toml (extra train)'
  - 'Test réel marqué lent (modèle minuscule à poids aléatoires, vendor/ requis)'
---

## Intent

**Problème :** réévaluer le Modèle fine-tuné dans le format de l'Assistant : adaptateur fusionné en 16 bits, GGUF F16 conservé, puis Q4_K_M, produits par les outils du tag llama.cpp, avec le template d'entraînement et le tool calling re-testé après quantification.

**Approche :** `slmsp.train.export` fusionne sur CPU en fp32 (base `models/<slug>/hf/` + adaptateur de `runs/train/<id>/adaptateur/`), contrôle la plage F16, enregistre en F16, puis délègue conversion (`type_sortie="f16"` explicite) et quantification (`Q4_K_M`, CPU, sans imatrix) à `inference.serveur` (AD-6), le tout sous `gpu.lock` dans `runs/export/<run_id>/`. `slmsp.cli.export` injecte les contrôles de format (lecture des GGUF, interdite à `train` par AD-24), résout `ft:<id>` pour `f16` et `q4_k_m`, puis lance la sonde d'outils sur le Q4_K_M.

## Décisions

- **A1 (Anaël, 2026-10-16) : AD-24 étendu.** `core.artefacts.chemin_autorise` autorise au lecteur `train` `runs/train/<run_id>/adaptateur/` et ses fichiers, rien d'autre du run (ni `run.json`, ni checkpoints). Le refus de 10.4 pour ORPO est levé : `train.run` vérifie désormais que l'adaptateur SFT est complet (`ConfigurationInvalide` sinon). Tests : `tests/core/test_lecteur.py`, `tests/train/test_run.py`.
- **AD-19, « 16 bits » (recommandation par défaut de la note, appliquée)** : fusion calculée en fp32, enregistrée en F16. « 16 bits » désigne le format écrit. `export.json` consigne `fusion = {calcul: fp32, ecriture: f16, materiel: cpu}` et les précisions réelles `{f16: f16, q4_k_m: q4_k_m}`, comme `precision_gguf` pour les bases.
- **R-002 ajouté au CA3 (recommandation par défaut, appliquée)** : la sonde de 8.2 passe déjà RD-001 et RD-002 (R-001 et R-002 d'H-TOOLS). `sonder` accepte maintenant `ft:<export_run_id>` (hors zone : `evaluation/sonde_outils.py`, et un paramètre de `tests/evaluation/test_sonde_outils.py`). Le bilan est écrit dans `sonde-outils.json` du run d'export.
- **Export témoin** (`slmsp export --base <slug>`, note C4) : même chaîne, sans adaptateur, référence de template = celle du tokenizer de la base. `modele_ref` le résout tel quel (`modele_ref = base:<slug>`), sans modification.
- **ORPO** : l'adaptateur ORPO continue l'adaptateur SFT (10.4 le charge `is_trainable`). Seul l'adaptateur du run est donc fusionné, et non la chaîne SFT puis ORPO de la note.
- **Refus avant tout run** : PiSSA non converti (`init_lora_weights = pissa`), adaptateur qui cible `embed_tokens` ou `lm_head`, ou qui a des `modules_to_save`.
- **Contrôles** : un SHA de `tokenizer.chat_template` différent dans le F16 ou le Q4 est bloquant (CA2, `partiel-erreur`, donc `ft:` non résolu). Les écarts de métadonnées avec le GGUF officiel (architecture, couches, `tokenizer.ggml.pre`, bos et eos) et un GGUF officiel absent sont de simples alertes, consignées dans `export.json`.
- **Verrou** : `gpu.lock` couvre la fusion, la conversion, la quantification et les contrôles de format. La sonde le reprend elle-même en `cuda`, après sa libération, car un second verrou dans le même processus échoue. Par défaut, la sonde tourne en `cpu`.
- **Espace disque** : `verifier_espace` est appelé si l'écriture prévue (2,4 × les safetensors de la base) dépasse 1 Gio. `PYTHONUTF8=1` est posé pour le convertisseur s'il est absent.
- **Racines (story 12.1, après rebase)** : les runs vont sous `racine_ecriture()`, et le lecteur contrôlé résout `runs/train/...` contre cette même racine.
- **Pas de dépendance `gguf` dans `pyproject.toml`** : le lecteur `fetch.verifications.lire_metadonnees_gguf` suffit (recommandation de la note C2). Un chemin vers `vendor/` casserait `uv lock` dans les worktrees, où `vendor/` est absent.

## À confirmer par Anaël

1. Les écarts de métadonnées avec le GGUF officiel restent une alerte et ne bloquent pas l'export (la note C5 les disait bloquants). Granite (`granitemoehybrid` vers `granite`) pourrait différer légitimement.
2. Une sonde non valide sur le Q4 rend le code 1, mais le run d'export reste `complet` : le résultat est consigné, sans passage en `degrade`.
3. ORPO : un seul adaptateur est fusionné (voir Décisions).
4. Ministral 3 3B : le chargement `AutoModelForCausalLM` de `hf/` (poids multimodaux) et la double source du template (`tokenizer_config.json` et `chat_template.jinja`) restent à vérifier au premier export réel. Le contrôle du CA2 le détectera.
5. Le dossier HF fusionné est conservé (`hf-f16/`, CA1) : il occupe environ 7 Go pour un 3B.

## Vérification

- Tests : `uv run pytest -q --tb=short tests/train/test_export.py tests/core/test_lecteur.py tests/train/test_run.py tests/evaluation/test_sonde_outils.py` (doubles de pile, du convertisseur et de `llama-quantize` ; GGUF minimal v3 écrit par les tests).
- Commande réelle, plus tard, GPU libre, depuis le dépôt principal dans l'environnement `train` :
  `uv sync --extra train` puis `uv run --no-sync slmsp export --depuis <train_run_id> --variante cuda`, et le témoin `uv run --no-sync slmsp export --base granite-4.0-1b --sans-sonde`.

## Auto Run Result

Statut : review. Zone touchée : `train/export.py`, `cli/export.py`, `tests/train/test_export.py`. Hors zone, sur décision ou par nécessité : `core/artefacts.py` (A1), `train/run.py` et `tests/train/test_run.py` (retrait du refus de 10.4), `evaluation/sonde_outils.py` et `tests/evaluation/test_sonde_outils.py` (sonde sur `ft:`), `tests/core/test_lecteur.py`. Aucun appel d'API, aucun téléchargement, aucune conversion réelle.
