---
title: 'LoRA GGUF et --lora-scaled (story 15.6, N6)'
type: 'feature'
created: '2026-10-20'
status: 'review'
review_loop_iteration: 1
followup_review_recommended: false
context: ['{project-root}/_bmad-output/planning-artifacts/stories-epic-15-nuit-2026-10-20.md']
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** l'évaluation d'un adaptateur passe par une fusion F16 puis un Q4_K_M (30 min, 3 Gio) : impossible de comparer vite plusieurs échelles d'adaptateur sur la base Q4_K_M officielle.

**Approach:** convertir l'adaptateur PEFT en LoRA GGUF (`convert_lora_to_gguf.py` du tag b11429) sans fusion, et servir la base Q4_K_M avec `--lora-scaled`, l'échelle étant choisie à l'évaluation et à la mesure.

## Boundaries & Constraints

**Always:** run d'export immuable (`runs/export-lora/<id>`, `adaptateur-lora.gguf`, `export.json`, SHA-256) ; échelle (défaut 1.0) et adaptateur consignés dans la référence du modèle (`lora:<id>@<échelle>`), dans `run.json` (`config.lora`, `serveur.lora`) et dans `measure` ; template et GGUF de la base inchangés (`base:<slug>` q4_k_m).

**Never:** DoRA, rsLoRA (échelle alpha/sqrt(r)), PiSSA non converti, `modules_to_save` ou embeddings : refus clair avant tout run. Pas de LoRA sur `f16`, ni au banc (`bench`). Aucune conversion réelle lancée ici.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Export | `export lora --depuis <train>` | run `export-lora` complet, contrôles `general.type = adapter` et architecture = base Q4_K_M, sonde de chargement (`--lora-scaled`, `/lora-adapters`) | non convertible : `ConfigurationInvalide`, aucun run ; sonde non valide : `degrade` |
| Évaluation | `eval run --modele lora:<id> --echelle-lora 0.5` | `modele_ref = lora:<id>@0.5`, serveur base Q4_K_M + `--lora-scaled adaptateur-lora.gguf:0.5` | échelle contradictoire, <= 0, ou hors `lora:` : usage (code 2) |
| Sans échelle | `--modele lora:<id>` | `@1` normalisé | n/a |
| Mesure | `measure run --modele lora:<id> --echelle-lora 0.5` | RAM/latence base + LoRA, composant `lora` compté | idem |

</intent-contract>

## Code Map

- `src/slmsp/inference/serveur.py` -- `Lora`, `ServeurLlama(lora=)`, `commande_conversion_lora`, `convertir_lora_vers_gguf`.
- `src/slmsp/train/export.py` -- `controler_lora_convertible`, `exporter_lora`.
- `src/slmsp/cli/export.py` -- `export lora`, `controler_lora`, `sonder_lora`.
- `src/slmsp/evaluation/modele_ref.py` -- `lora:`, `composer_lora`, `echelle_lora_de`.
- `src/slmsp/core/schemas/run.py` -- motif `ModeleRef`. `cli/eval.py`, `cli/measure.py`, `harness/assemblage.py`, `evaluation/assemblage.py|generation.py` -- échelle et adaptateur transmis.
- `config/llamacpp.toml` -- SHA-256 de `src/convert_lora_to_gguf.py`.

## Auto Run Result

Tests ciblés : `tests/inference`, `tests/train`, `tests/evaluation`, `tests/measure`, `tests/harness`, `tests/benchmarks`, `tests/core`, `tests/compare`, `tests/cli`, architecture : verts ; ruff, format, contrôle rapide verts.

Vérifié dans les sources b11429 : script `src/convert_lora_to_gguf.py` (`--base`, `--outfile`, `--outtype f32|f16|bf16|q8_0|auto`, `lora_path` positionnel) ; `--lora-scaled FNAME:SCALE` coupe sur `:`. Dépendances du script (torch, transformers, numpy) présentes dans le venv ; `gguf` vient de `src/gguf-py` via `PYTHONPATH`. `--dry-run` du script validé sur `20261020-125424-m1-qlora-minicpm5-2b-v18-82ef` (588 tenseurs, 50,2 Mo).

Décisions : (1) un chemin Windows contient `:` : le serveur est lancé avec `cwd` = dossier du LoRA et `--lora-scaled <nom>:<échelle>` ; (2) l'échelle fait partie de la référence (`lora:<id>@<échelle>`) pour que reprise, notation et `eval comparer` voient deux échelles comme deux modèles ; (3) LoRA F16 ; (4) sonde de chargement en variante `--variante` (échelle 1.0), non valide : run `degrade`. À confirmer par Anaël : la forme `lora:<id>@<échelle>` du `modele_ref` (schéma `ModeleRef` étendu).

Reports : `bench` (`slmsp bench` refuse `lora:`), `eval comparer` regroupe par run (pas de regroupement par adaptateur), `compare/chargement.py` ignore les refs `lora:`.

## Revue

Revue du 2026-10-20 (commit 2ce2fdb, base non rebasée : main a avancé de 15.1 sans conflit).

| Sévérité | Source | Constat | Suite |
|---|---|---|---|
| medium | second avis 1 | `alpha_pattern` ignoré par `convert_lora_to_gguf.py` (alpha global seul) : échelle fausse en silence | corrigé : refus avant tout run (`controler_lora_convertible`). `rank_pattern` accepté : llama.cpp divise par le rang de chaque tenseur, comme PEFT (vérifié dans le script b11429, `set_gguf_parameters`) |
| medium | second avis 2 | tests de `cli/export`, `_modele_et_lora`, `eval --echelle-lora` absents | rejeté pour l'essentiel : déjà couverts (`test_cli_export_lora_*`, `test_sonder_lora_*`, `test_measure_*`, `test_cli_eval_run_echelle_lora`) ; ajouté le composant `lora` de `measure` et les cas sans sonde |
| low | second avis 3 | `composer_lora` en `:g` : 1e-05 refusé par `ModeleRef`, 0.12345 arrondi en silence | corrigé : 0 < échelle <= 4, 4 décimales au plus (refus d'usage sinon) |
| low | second avis 4 | gabarit d'entraînement jamais comparé au gabarit servi de la base | corrigé : comparaison (`chat_template.jinja` imposé, sinon GGUF q4_k_m) ; écart = alerte dans `export.json`, affichée par la CLI (pas bloquant : le LoRA est servi avec le gabarit de la base par construction) |
| low | second avis 5 | sans GGUF q4_k_m de la base, sonde non lancée mais run `complet` sans trace | corrigé : `sonde-lora.json` écrit avec `lancee: false` et le motif (aussi pour `--sans-sonde`), alertes affichées ; `lora:` reste inutilisable sans la base (résolution refusée) |
| low | second avis 6 | tokenizer non comparé | rejeté : le LoRA GGUF ne porte aucun tokenizer (`set_vocab` vide dans le convertisseur) ; la base de conversion est `models/<slug>/hf`, même slug que la base servie ; architecture et gabarit comparés |
| low | reviewer | `cwd` = dossier du LoRA au lancement de llama-server : un `-m` relatif casserait | rejeté : tous les chemins passés sont absolus (`dossier_modeles()`, racines résolues) |
| — | reviewer | Complexité : 0 constat (aucune structure qui grossit pendant l'exécution) | — |

Reporté (service réel, GPU occupé) : conversion réelle de `20261020-125424-m1-qlora-minicpm5-2b-v18-82ef`, puis `export lora` avec sonde (vérifier `sonde-lora.json` `valide: true`, `scale` 1.0 lu sur `/lora-adapters`) et un `eval run --modele lora:<id> --echelle-lora 0.5` sur un item (vérifier `--lora-scaled adaptateur-lora.gguf:0.5` dans `run.json` `serveur.lora`). Vérifier aussi que l'alerte de gabarit est absente sur MiniCPM5-2B.
