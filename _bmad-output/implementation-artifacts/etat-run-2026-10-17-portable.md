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

## Nuit en cours (ordre)
1. Bench socle minicpm5-1b `runs/bench/20261017-194849-minicpm5-1b-5c8e` : 10 benchmarks HF faits (batch 4, aucun OOM sur 6 Go) ; traduction CPU en cours (F16 puis Q4_K_M). Il tient `gpu.lock` jusqu'à la fin.
2. Génération Baseline eurollm-1.7b (CPU, jeu v1.1), lancée à 22:30 en parallèle. Ensuite qwen3.5-0.8b.
3. À la libération du verrou : bench socle granite (HF, VRAM relevée pour juger un batch de 4), puis socle des deux nouveaux.
4. Machine libre : mesures CPU à ctx 4096 (granite, minicpm5-1b, eurollm, qwen3.5-0.8b).
5. Notation (payante, orchestrateur) des générations.

## Points d'environnement
- **`config/modeles/minicpm5-1b.toml` est remis provisoirement à sa version 18ad3ea dans le dossier de travail** : le bench en cours refuserait le champ `decoupage_masque`. À rétablir (`git restore`) à la fin du bench.
- Worktrees fusionnés à retirer (refusé à l'agent) : `slmsp-wt\hybrides-baseline`, `candidats-registre`, `masque-minicpm5`.
- Runs non suivis à commiter : `runs/fetch/` de la phase 1, `runs/bench/`, `runs/eval-sonde/` (dans le worktree outils-rendu).
- Bloqueur de veille actif (processus PowerShell), capot ouvert, sur secteur.
