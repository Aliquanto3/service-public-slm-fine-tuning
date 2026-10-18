# État du run, portable, nuit du 2026-10-17 au 18

Reprise sur le PC portable (32 Go, RTX 3060 6 Go) depuis `docs/reprise-deuxieme-pc.md`. Ce fichier est mis à jour par l'orchestrateur ; il sert de point de reprise après `/clear`.

## Intégré dans main (poussé)
- `d24006d` : candidats < 2B (EuroLLM-1.7B, Qwen3.5-0.8B épinglés ; CroissantLLM retiré : licence MIT, contexte 2048).
- `18ad3ea` : D8 (hybrides Gated DeltaNet admis pour la Baseline seulement, `entrainable = false`), registre des Modèles de base dans `decisions.md`, règle « 2B au plus, paramètres texte servis », liste `--candidats` alignée sur D8, garde `exiger_entrainable` (train run et sonde-env), granite `lm_eval_batch_size = 2`.
- `f2f6830` : masque d'entraînement par tour (`decoupage_masque = "par-tour"`, minicpm5-1b), G1 à G4, R2 levé (llama-server rend l'amorce HF).
- Suite complète : 5 028 réussis sur 18ad3ea (avec `SLMSP_EVAL_SOURCES`), 4 811 sur f2f6830 (sans).

## Branches en attente
- `feat/outils-rendu` (worktree `C:\Users\Anael\dev\slmsp-wt\outils-rendu`) : spec R7 `spec-outils-rendu.md`, en draft, relue par le second avis, **sans code**. Elle attend les décisions ci-dessous. À rebaser sur main (part de 62831f8).

## Décisions d'Anaël du 2026-10-17 (à reporter dans decisions.md)
- Règle de taille : ≤ 2B de paramètres texte servis (vision exclue) ; Qwen3.5-2B reste dans la Baseline (remplace la décision de 09h).
- Hybrides : option 2 (Baseline seulement). MiniCPM5-1B : découpage par tour.
- Mesures de Baseline : contexte 4096, `max_tokens` 1024 fixé explicitement ; tous les modèles seront remesurés une fois.
- EuroLLM : contexte 4096 ; outils décidés après sa Baseline. v0.2.0 après la Baseline.
- Notation de la nuit : campagne actuelle, puis nouvelle campagne de 5 € (anthropic) si besoin, pas au-delà.

## Décisions à prendre (point du matin)
1. **Format du premier message RD de data/train/v1** : les 91 lignes sont hybrides (texte du Mode local, outils du Mode connecté). Normaliser au build ou adapter au chargement (spec R7 §0).
2. **EuroLLM** : aucun protocole d'outils ne marche (sonde H-TOOLS : 0/5 en natif et en balises ; json-generique en HTTP 400 sur b11429). Options A à E (spec R7 §4).
3. **Troncature à 4096** : 30 lignes RD sur 91 (granite, minicpm5) dépassent le budget après un résultat d'outil.
4. **micro_lot des passages** : 1536 suffit (passage max de l'Index : 1 165 tokens) ; à faire avec une troncature de la requête utilisateur, aujourd'hui vectorisée sans limite (`recherche_index.py:45`).
5. 9.8 : relecture de l'échantillon de 30 lignes ; `verifie_le` des licences d'EuroLLM et de Qwen3.5-0.8B.
6. Bug llama.cpp b11429 : `json-generique` → « Unexpected empty grammar stack » (touche tout modèle sur ce protocole).

## Résultats de la nuit (commités)
- **Baseline (jeu v1.1, Q4_K_M, CPU)** : EuroLLM `runs/eval-notation/20261018-011522-eurollm-1.7b-5872` (2,63 €), Qwen3.5-0.8B `20261018-025524-qwen3.5-0.8b-3124` (3,08 €).
  | Tâche | EuroLLM-1.7B | Qwen3.5-0.8B |
  |---|---|---|
  | Q | 0,0 | 0,0 |
  | RD | 0,0 | 51,2 |
  | CR | 24,6 | 20,7 |
  | LC | 50,0 | 12,0 |
  | CO | 39,9 | 67,3 |
  | RE | 27,8 | 25,2 |
  | CT | 23,3 | 23,3 |
  | NR | 6,7 | 20,0 |
  Q proche de 0 est la norme sous 2B (minicpm5-1b 0,0, Qwen3.5-2B 1,7 ; Qwen3-4B 11,7). RD à 0 pour EuroLLM : aucun protocole d'outils.
- **Budget** : campagne `baseline-2026-10-17` close (anthropic 7,89 €, reste 2,21 € insuffisant pour une notation) ; campagne `baseline-2026-10-18` ouverte à 5 € anthropic (approuvé), mistral réduit des dépenses. Reste anthropic 1,92 €.
- **Mesures CPU ctx 4096** (`runs/measure/20261018-04*`) : NFR-1, 2, 6 conformes ; NFR-3 (p95 du premier token < 5 s) non conforme pour les quatre (médiane 0,5 s, p95 11 à 26 s), comme sur la tour.
  | Modèle | tok/s méd. | 1er token p95 | RAM max |
  |---|---|---|---|
  | granite-4.0-1b | 14,6 | 26,3 s | 3,88 Go |
  | minicpm5-1b | 36,4 | 12,8 s | 2,18 Go |
  | eurollm-1.7b | 23,2 | 19,7 s | 3,91 Go |
  | qwen3.5-0.8b | 43,3 | 11,5 s | 2,26 Go |
- **Bench socle HF** (`runs/bench/20261018-0*`, batch 2 ; minicpm batch 4) : pics VRAM granite 4 623, eurollm 4 879, qwen 4 511, minicpm 5 063 Mio sur 6 144. Un batch de 4 pour granite tiendrait sans doute (≈ minicpm), non testé.
  | Modèle | belebele | MMLU | Global-MMLU fr | ARC fr | MCQ-eval | CrowS % stéréo |
  |---|---|---|---|---|---|---|
  | granite-4.0-1b | 0,638 | 0,569 | 0,465 | 0,378 | 0,095 | 0,417 |
  | minicpm5-1b | 0,518 | 0,553 | 0,420 | 0,228 | 0,119 | 0,434 |
  | qwen3.5-0.8b | 0,581 | 0,502 | 0,435 | 0,294 | 0,119 | 0,463 |
  | eurollm-1.7b | 0,277 | 0,260 | 0,278 | 0,342 | 0,095 | 0,513 |
  EuroLLM est au niveau du hasard sur belebele et MMLU (4 choix) : à vérifier (template ou modèle base ?).
- **Traduction minicpm5-1b** (F16) : chrF moyen 30,9 ; fr-ar 0,7 (à vérifier : sorties hors langue ?).

## Incident de la nuit : cache HF des jeux lm_eval absent
Aucune commande ne le remplit et `restaurer-etat.ps1` ne le copie pas ; 7 benchmarks HF de minicpm5-1b ont échoué la première fois. Rempli à la main : `snapshot_download` aux révisions de `[options.jeux_hf]`, `refs/main` écrit sur la révision épinglée, puis `load_dataset(..., revision=<épinglée>)` en ligne pour créer le cache `datasets` (hors ligne, datasets 5 ne lit pas les seuls snapshots). 515 Mo. **À outiller** (sous-commande `fetch` ou export d'état) : story à créer.

## En cours (matin du 18)
Bench GGUF CPU, dans l'ordre : ifeval minicpm5-1b ; bfcl et ifeval pour granite, eurollm, qwen3.5-0.8b ; puis traduction (≈ 3 h 40 par précision et par modèle, donc jusqu'en soirée). Il tient `gpu.lock` : à arrêter si le GPU est requis.

## Points d'environnement
- `config/modeles/minicpm5-1b.toml` rétabli (`git restore`) à 04:30.
- Runs de bench en échec (cache HF) non commités : `runs/bench/20261018-0441*`, `0444*`, `0447*`, `0450*` ; à supprimer (avec accord).
- Worktrees fusionnés à retirer (refusé à l'agent) : `slmsp-wt\hybrides-baseline`, `candidats-registre`, `masque-minicpm5`.
- Runs non suivis à commiter : `runs/fetch/` de la phase 1, `runs/bench/`, `runs/eval-sonde/` (dans le worktree outils-rendu).
- Bloqueur de veille actif (processus PowerShell), capot ouvert, sur secteur.
