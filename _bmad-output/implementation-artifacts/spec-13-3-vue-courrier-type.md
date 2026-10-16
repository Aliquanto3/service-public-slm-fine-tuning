---
title: 'Story 13.3 — Vue Courrier type, formulaire et emplacements'
type: 'feature'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-13-1-vue-correction.md'
warnings: []
deferred: []
---

## Intent

**Problem:** la vue Courrier type (CT) affiche « non disponible » (FR-14, UX-DR14).

**Approach:** `courrier.js` réutilise `monterRedaction` (12.8) avec un formulaire : type de courrier (liste), objet (champ texte), éléments connus (zone de saisie du volet). L'entrée CT envoyée au pont est `options.entree = {type_courrier, objet?, elements_connus?}`, champs remplis seulement : la forme du gabarit `config/prompts/taches/CT.md` et de `harness.prompts` (clés `type_courrier`, `objet`, `elements_connus`). À la fin d'une génération terminée, le pont (`redaction_outils.emplacements`) découpe le courrier en segments `texte` / `emplacement` et signale les champs non fournis rendus par une valeur ; la vue rend les emplacements en `<mark class="letter-placeholder" tabindex="0">` (par `textContent`) avec texte `sr-only` « (à compléter) ». Copier donne toujours le courrier brut.

## Code Map

- `src/slmsp/harness/emplacements.py` -- `segmenter`, `detecter` (libellé entre crochets sur une ligne, 1 à 120 caractères, sans imbrication), `libelles_presents` (règle de `controle_ct`, déplacée ici ; `evaluation.controles` l'importe), `champ_rendu_par_une_valeur(texte, intitule)` (ligne « Intitulé : valeur » sans emplacement, intitulé comparé sans casse, accent ni mise en forme).
- `src/slmsp/app/pont/redaction_outils.py` -- méthode `emplacements(texte, champs_non_fournis)` -> `{segments, champs_en_valeur}` ; seul `objet` a une ligne d'intitulé contrôlable (`INTITULES`).
- `js/vues/courrier.js`, `css/courrier.css` -- formulaire, rendu des emplacements (cadre en pointillés, lisible sans la couleur), compte « N emplacements à compléter », `callout-warning` « vérifié automatiquement ».
- `js/vues/redaction.js` -- extension minimale et rétro-compatible : option `peutEnvoyer()` (condition d'envoi) et écoute des `input`/`change` des `controles` (marque l'entrée modifiée).
- Tests : `tests/harness/test_emplacements.py` (6), `tests/app/ui/test_vue_courrier.py` (11, `ui`) ; `VUES_REALISEES` : « courrier » ajouté.

## Acceptation (état)

1. L'entrée CT porte `type_courrier` et les champs remplis seulement. Fait (test sur les arguments de `envoyer`).
2. Emplacements en `letter-placeholder`, au clavier (`tabindex=0`), annoncés « à compléter ». Fait.
3. Champ non fourni rendu par une valeur : `callout-warning`. Fait pour l'objet ; voir « À confirmer » pour les éléments connus.

## Auto Run Result

**Décisions prises seul :**
- Libellés proposés (aucun exemple ni préremplissage, D1) : types « accusé de réception », « demande de pièces », « convocation », « réponse d'information » (ceux de la story) ; titres « Formulaire » et « Courrier » ; étiquettes « Type de courrier », « Objet (facultatif) » ; phrase d'aide « Choisissez le type de courrier, puis renseignez seulement ce que vous savez (objet, éléments connus). Ce qui manque apparaît dans le courrier comme un emplacement à compléter. » ; bouton « Rédiger ».
- Envoi possible si un type est choisi et si l'objet ou les éléments connus sont renseignés (le harnais refuse une entrée sans clé de contenu).
- Le contrôle « valeur à la place d'un champ non fourni » est une heuristique prudente : seule la ligne « Objet : … » est examinée. Sans ligne d'objet, pas d'alerte.
- Courrier interrompu ou coupé : pas de repérage ni de contrôle (texte brut). Échec du pont : courrier brut et mention.
- Le message utilisateur envoyé est un résumé lisible des champs remplis (historique) ; la source de l'entrée est `options.entree`.
- `emplacements` ajouté à `redaction_outils.py` (zone de 13.1) plutôt qu'un nouveau module, pour ne pas toucher `pont/__init__.py`.

## À confirmer

- Anaël : les quatre libellés de type, la phrase d'aide, « Formulaire » / « Courrier », « Objet (facultatif) ».
- Anaël : type de courrier limité à une liste fermée de quatre (pas de saisie libre) ; CT.md parle d'un « type demandé » sans liste.
- Anaël : contrôle FR-14 limité à l'objet. Les éléments connus n'ont pas de ligne propre dans un courrier, un contrôle fiable demanderait un juge ou un jeu de libellés par type.
- Anaël : extension de `redaction.js` (`peutEnvoyer`, écoute des contrôles) et méthode ajoutée à `redaction_outils.py`, fichiers d'autres stories (conflit possible avec 13.2).
- Format réel des emplacements produits par le modèle (crochets bien formés ?) : à vérifier sur une sortie réelle, hors périmètre (aucune génération).
