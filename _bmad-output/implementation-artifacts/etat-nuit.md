# État du run autonome — 2026-10-12

> Horaire décalé (voir journal D-nuit-1) : phase F à 14h00, arrêt dur à 14h30, seuil DoRA à 13h00.

## Phase en cours
Phase B : socle J1 et jeu d'évaluation (démarrée à 07h30)

## Fait
- 08h00 : story 7.1 terminée (outil de construction du jeu, 100 tests) et fusionnée (b14abcf). Sources manquantes, à compléter après 08h30 : LEGI CGCT, code civil, commande publique, xlsx de questions.
- 08h00 : story 1.1 terminée (squelette, 129 tests) et fusionnée (abceddd). Modèles préchargés : Granite 1B, Ministral 3B et SmolLM3 3B, environ 22 Go. Qwen 4B et le GGUF Ministral 8B reprennent à 08h31.
- 06h26 : commit de cadrage sur `main` (3431c35), puis branche `nuit/2026-10-12`.
- 06h56 : A.1 architecture terminée, commit a25c83b. Points à trancher par Anaël : D-nuit-A1-5, A1-10 et A1-17.
- 07h23 : A.2 epics et stories terminés (53 stories, 13 epics), commit 91827ea.
- 07h29 : A.3 sprint planning terminé (verdict : prêt avec réserves), commit 51a6d2f. **Phase A terminée.**

## En cours
- Stories 1.2 (noyau config) et 5.2 (fonctions de texte), en worktrees
- Story 7.2 : items Question et Non-régression (piste 2, worktree)
- Préchargement des modèles candidats sous `models/` (D-nuit-B-2)

## Bloqué
- 07h47 à 08:15 : réseau limité à la demande d'Anaël (D-nuit-B-3). Limite levée à 08:15.
(rien)

## Dépense API
| Service | Dépensé | Plafond |
|---|---|---|
| Mistral | 0 € | 30 € |
| Anthropic (Juge) | 0 € | 10 € |
