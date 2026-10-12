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

## En cours
- Story 1.3 : noyau runs et ports.
- Story 7.2 : items Question et Non-régression (piste 2).
- Story 7.4 : items Compte rendu et Langage clair (piste 2).

## Bloqué
Rien pour l'instant. Le réseau a été limité de 07h47 à 08h15 à la demande d'Anaël (D-nuit-B-3) ; la limite est levée.

## Dépense API
| Service | Dépensé | Plafond |
|---|---|---|
| Mistral | 0 € | 30 € |
| Anthropic (Juge) | 0 € | 10 € |
