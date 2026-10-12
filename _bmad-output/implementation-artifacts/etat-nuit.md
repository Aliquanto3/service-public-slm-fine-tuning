# État du run autonome — 2026-10-12

> **Run prolongé (journal D-nuit-2, consigne d'Anaël à 12h40)** : il continue jusqu'à la fin du travail planifié, au plus tard le 2026-10-13 à 07h00. Phase F à la fin du travail, ou le 13 à 06h30 au plus tard. Seuil DoRA : le 13 à 05h30. Arrêt anticipé en cas de risque technique ou de problème d'orchestration.
> Organisation : chaque story tourne dans un worktree git et est fusionnée en squash sur `nuit/2026-10-12` (D-nuit-B-1). Le statut des stories est dans `sprint-status.yaml`.

## Phase en cours
Phase B : socle J1 et Jeu d'évaluation, démarrée à 07h30.

## Fait
- 06h26 : commit de cadrage sur `main` (3431c35), puis création de la branche `nuit/2026-10-12`.
- 06h56 : A.1, architecture (a25c83b). Points à trancher par Anaël : D-nuit-A1-5, A1-10 et A1-17.
- 07h23 : A.2, epics et stories (91827ea) : 53 stories réparties en 13 epics.
- 07h29 : A.3, sprint planning (51a6d2f), avec le verdict « prêt avec réserves ». **Fin de la phase A.**
- 08h00 : story 1.1, squelette (abceddd).
- 08h00 : story 7.1, outil de construction du jeu (b14abcf).
- 08h17 : story 5.2, fonctions de texte (6db33d0).
- 08h17 : story 1.2, noyau de configuration (43f25d1). La suite passe : 387 tests.
- 08h17 : instantanés des sources du Jeu d'évaluation complets, dans `data/raw/eval-sources/`.
- 08h26 : modèles candidats préchargés sous `models/` (39 Go) : Granite 1B dense, Ministral 3B (BF16 et GGUF officiels), SmolLM3 3B, Qwen3 4B (GGUF unsloth) et Ministral 8B (GGUF officiel). Détail dans `models/PRECHARGEMENT.md`.

- 08h50 : story 1.3, noyau des runs (b279760).
- 09h08 : story 7.4, 25 items CR et 25 items LC (08766f0).
- 09h10 : story 1.4, passerelle réseau (8c7ebcc).
- 09h24 : story 3.1, outils MCP figés (9de2257).
- 09h33 : story 7.2, 60 items Q et 30 items NR (3e8b5b8). On compte 140 items vérifiés.
- 09h50 : story 2.1, `slmsp fetch` (436a972). llama.cpp b11429, BGE-M3 et MediaTech sont téléchargés.
- 10h01 : story 3.3, client MCP direct et `mcp record` (9e02437).
- 10h17 : story 5.1, lecteur d'items, anti-fuite et gel (fad05df). Les 140 items passent `--verifier-seulement`.
- 10h26 : story 2.2, llama-server géré (5dd6e14). Granite 1B tourne en CPU à environ 42 tokens/s.

- 10h50 : story 7.3, 40 items RD et leurs cassettes.
- 11h19 : story 7.5, 15 items CO, 15 RE et 15 CT.
- 11h35 : stories 2.3 (Index local, H-VEC) et 1.5 (registre de budget).
- 12h05 : **gel du Jeu d'évaluation v1.0-provisoire** (commit 12eef73).
- 12h13 à 13h49 : stories 4.1, 4.2, 5.4, 3.2, 4.4, 5.5, 8.1, 4.3 et 9.2. La suite passe : 2 464 tests sans échec, mesuré à 13h28.

- 15h35 : reprise en **mode économe, sur un périmètre réduit** (D-nuit-4) : une story à la fois, une seule couche de revue.
- 15h55 : story 5.3, génération de l'évaluation.
- 16h37 : story 5.6, notation et Scores de Tâche. **Le banc fonctionne de bout en bout.**
- 17h15 : story 8.2, sonde de tool calling : Granite 4/5 et Ministral 3B 5/5 en `natif`, SmolLM3 0/5, Qwen 2/5 en `json-generique`.

## En cours (17h20)
- **Baseline réduite** (Jeu maison seul) : Granite 1B sur GPU (CUDA), 225 items, puis notation avec le Juge en batch. Run `runs/eval-generation/20261012-171658-granite-4.0-1b-3589`.
- Ensuite : Ministral 3B (meilleur 3B à la sonde), puis le rapport de Baseline.
- Stories en attente, sans fusion : 9.1 et 10.1 (D-nuit-3, D-nuit-4).

## Bloqué
Rien pour l'instant. Le réseau a été limité de 07h47 à 08h15 à la demande d'Anaël (D-nuit-B-3) ; la limite est levée.

## Dépense API
| Service | Dépensé | Plafond |
|---|---|---|
| Mistral | 0,02 € | 30 € |
| Anthropic (Juge) | 0,28 € | 10 € |
