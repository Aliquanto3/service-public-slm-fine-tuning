---
title: 'Story 12.9 — Indicateur de Mode et journal des Requêtes sortantes'
type: 'feature'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-5-pont-js-api-et-flux-d-evenements.md'
warnings: []
deferred: []
---

## Intent

**Problem:** l'Agent doit voir en permanence le Mode, pouvoir forcer le hors ligne et consulter ce qui est parti sur le réseau (FR-10, FR-11, FR-38).

**Approach:** `PontMode(mode, stockage, pousser)` enveloppe le `ModePort` (forçage via `forcer`) et `JournalApplication` ; `vues/mode.js` rend la pastille, son menu à trois éléments (état, « Rester hors ligne », « Journal des requêtes sortantes ») et le dialogue du journal.

## Contrat final (pour 12.7 et 12.10)

- `mode.etat()` -> `{ok, mode: "connecte"|"hors_ligne", hors_ligne: bool, force: bool, detail: "connecte"|"hors-ligne-detecte"|"hors-ligne-force"}`. Peut déclencher la sonde (période échue), jamais en hors ligne forcé.
- `mode.forcer_hors_ligne(actif)` -> même forme ; persiste `hors_ligne_force` (stockage), appliqué au démarrage par le constructeur.
- `mode.journal(limite)` -> `{ok, entrees: [{horodatage ISO, profil, hote, methode, outil, termes, statut, mode}]}`, du plus récent au plus ancien ; `mode.effacer_journal()` -> `{ok}`.
- Poussée Python -> JS : `{"type": "mode", mode, hors_ligne, force}` à chaque changement observé (lecture, forçage, `PontMode.rafraichir()`). L'interface l'émet sur le bus `evenement:mode`.
- Bus JS : `mode:change {hors_ligne}` émis par la vue au premier état connu puis à chaque bascule connecté/hors ligne (pas au seul passage détecté -> choisi). Une seule annonce `Mode : <libellé>` par changement.
- La vue relit `mode.etat` toutes les 30 s (déclenche la sonde si échue) ; la sonde n'a pas de rappel propre.

## Code Map

- `src/slmsp/app/pont/mode.py`, `src/slmsp/app/pont/__init__.py` (`Pont(..., *, stockage=None)` ; `PontMode(service.mode, stockage, self._pousser)`)
- `src/slmsp/app/ui/js/vues/mode.js`, `src/slmsp/app/ui/css/mode.css`
- `tests/app/test_pont_mode.py`, `tests/app/ui/test_vue_mode.py` (`ui`)
- Hors zone, minimal : `tests/app/test_pont.py` (le bouchon testé devient `mode.inconnue`), `tests/app/ui/test_socle.py` (ordre de tabulation : `mode-pastille` après `bouton-nouvelle`), `tests/app/ui/test_socle_statique.py` (`VUES_REALISEES`).

## Auto Run Result

Décisions prises seul :
- Statut `echouee` du journal libellé « Échouée » ; `bloquee-liste` « Bloquée (hôte hors liste) ».
- Sans `stockage`, le forçage ne vaut que pour la session et le journal est vide.
- Menu à trois éléments retenu : ligne d'état, case « Rester hors ligne », « Journal des requêtes sortantes ».
- Journal limité à 200 lignes côté vue.
- Les tests d'interface simulent `window.pywebview.api` (pas le pont factice, trop pauvre pour le Mode).

## À confirmer

- Anaël : libellés (« Connecté », « Hors ligne », « Hors ligne (choisi) »), texte du menu et de l'aide du journal.
- 12.6 : doit construire `Pont(service, fenetre, stockage=stockage)` avec le même `Stockage` que `JournalApplication` passé à `assembler`, sinon le forçage n'est pas persisté.
- 12.7 : consommer `mode:change` (ou `mode.etat`) ; conflits probables sur `test_socle.py` / `test_socle_statique.py` (une ligne chacun) avec 12.6 et 12.7.
- Le sondage JS toutes les 30 s est une simplification ; un rappel Python après sonde (`rafraichir`) pourrait le remplacer.
- Test `-m ui` `test_arreter_pendant_la_generation` intermittent (course avec le `pret` du pont factice, préexistant, déjà noté en 12.5).

## Revue

- high, second avis : journal de la passerelle différent de celui lu par la vue Mode. Corrigé : sur main, `Demarrage` passe `JournalApplication(stockage)` à l'assemblage et `Pont(..., stockage=stockage)` ; test de bout en bout `test_lancer_la_requete_de_la_passerelle_apparait_dans_la_vue_mode` (vraie `Passerelle`, `lancer()` réel, `mode.journal()` puis `effacer_journal()` sur le même journal).
- medium, second avis : purge de 30 jours sur le journal écrit. Confirmé : `JournalApplication.inscrire` purge à chaque écriture, le `Stockage` à l'ouverture ; testé (`purger()` supprime l'entrée expirée).
- medium, second avis : `lister()` sans fenêtre. Corrigé : filtre glissant `horodatage >= maintenant - 30 j` (horloge du `Stockage`) ; test avec horloge injectée.
- low, second avis : `rafraichir()` hors verrou. Corrigé : lecture et poussée sous le verrou.
- low, second avis : `{ok:false}` de `forcer_hors_ligne` ignoré. Corrigé : annonce de l'échec, interrupteur rétabli ; test `ui`.
- Intégration (rebase) : `service.mode` ajouté aux doublures de `test_principal.py` ; ordre de tabulation `mode-pastille` avant les exemples de 12.7.
- Reporté : sonde réelle et rendu dans la vraie WebView2 (non couverts : Edge/Playwright seulement).
