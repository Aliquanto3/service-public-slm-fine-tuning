---
title: 'Story 13.2 — Vue Résumé à trois longueurs'
type: 'feature'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-8-vues-de-redaction-compte-rendu-et-langage-clair.md'
warnings: []
deferred: []
---

## Intent

**Problem:** la vue Résumé (RE) affiche « non disponible » (FR-15).

**Approach:** `resume.js` réutilise `monterRedaction` (12.8, sans le modifier) avec trois boutons radio de longueur (« Court », « Moyen », « Détaillé », défaut « Moyen »). L'envoi porte `options.entree = {document, longueur_demandee}` avec les valeurs du Jeu gelé v1.1 : `courte`, `moyenne`, `detaillee`. Le pont transmis au volet est enveloppé : un refus du Harnais (hors `generation-en-cours`) affiche le message d'entrée trop longue (UX-DR19). Les textes longs acceptés passent par le découpage et « Partie i sur n » de 12.8.

## Code Map

- `js/vues/resume.js`, `css/resume.css` ; `tests/app/ui/test_vue_resume.py` (8, `ui`) ; `test_socle_statique.py` : `resume` ajouté à `VUES_REALISEES`.

## Auto Run Result

**Décisions prises seul :**
- Valeurs `courte|moyenne|detaillee` (Jeu gelé, plafonds 80/200/400 de `[re.longueurs]` dans `config/evaluation.toml`), et non `re_longueurs_mots = [80, 150, 250]` de l'entraînement : le critère 1 impose la valeur du jeu gelé. Aucune entrée `consigne` envoyée (pas de texte rédigé).
- Aucun nombre de mots affiché dans l'interface, pour ne pas dupliquer deux jeux de valeurs divergents.
- Libellés proposés : « Résumer », « Longueur du résumé », « Court / Moyen / Détaillé », titre de résultat « Résumé », invite « Collez le document à résumer, puis choisissez la longueur. Je ne rapporte que ce qui figure dans le texte. », message « Ce document est trop long pour être résumé tel quel. Raccourcissez-le, ou résumez-le en plusieurs parties. »

## À confirmer

- Alignement des longueurs d'entraînement (80/150/250) sur celles du jeu gelé (80/200/400) : écart existant, hors périmètre de la vue.
- Les libellés ci-dessus (à valider par Anaël).
- Le Harnais découpe plutôt qu'il ne refuse un texte long : le message UX-DR19 ne s'affiche que sur un refus `requete-invalide` (toute cause).
