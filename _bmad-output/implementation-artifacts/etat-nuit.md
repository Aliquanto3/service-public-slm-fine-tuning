# État du run autonome — 2026-10-12

> Horaire décalé (voir journal D-nuit-1) : phase F à 14h00, arrêt dur à 14h30, seuil DoRA à 13h00.
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

## En cours (10h26)
- Story 2.3 : Index local et mesure H-VEC.
- Story 7.3 : 40 items RD et leurs cassettes (piste 2).
- Story 7.5 : 15 items CO, 15 RE et 15 CT (piste 2).
- Ensuite : la story 7.6, qui gèle le jeu, puis le chemin du banc (4.1 à 4.5, 1.5, 5.3 à 5.6). Priorisation : D-nuit-B-4.

## Bloqué
Rien pour l'instant. Le réseau a été limité de 07h47 à 08h15 à la demande d'Anaël (D-nuit-B-3) ; la limite est levée.

## Dépense API
| Service | Dépensé | Plafond |
|---|---|---|
| Mistral | 0 € | 30 € |
| Anthropic (Juge) | 0 € | 10 € |
