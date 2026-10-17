---
title: 'validate aligné sur build hors provenance (F4)'
type: 'bugfix'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: ['spec-9-x-fix-amorces-tronquees.md']
warnings: []
deferred: []
---

## Intent

**Problème :** build pouvait encore refuser une session retenue par validate (entrée refusée par la Tâche, conversation invalide, résultat d'outil hors cassette), ce qui fait échouer tout le build.

**Approche :** la fabrication de la conversation (hors licence) est extraite de `rederiver_ligne` dans `build.construire_conversation(lecteur, taches, brut)`. Validate l'appelle (import différé, `build` importe `validate`) et rejette la session avec le motif de la `DerivationRefusee` levée. Aucune règle dupliquée.

## Tableau des refus de build par session

| Refus | Issue |
|---|---|
| appel absent, usage ≠ generation, statut ≠ ok, gabarit non journalisé, réponse tronquée | validate (déjà fait, 1538cce) |
| amorce introuvable, SHA, texte ≠ réponse journalisée, amorce tronquée | validate (déjà fait) |
| entrée incompatible avec la Tâche (nombre d'amorces, emplacement en double, CR sans 2 appels, CO sans amorce `texte`, generique sans `demande`, `EntreeInvalide`), paramètre `config` sans son amorce liée | validate, `entree_refusee` (nouveau) |
| cassette illisible, requête journalisée illisible, résultat d'outil absent des cassettes | validate, `outil_hors_cassette` (nouveau). Une cassette altérée ou absente reste `trace_divergente` : le rejeu passe avant. |
| appels d'outils sans suite, RD sans réponse finale, `ConversationInvalide` | validate, `conversation_invalide` (nouveau) |
| source absente du Registre, usage interdit pour la variante | build échoue (inchangé) |
| `LigneEntrainement`/`MetaLigne` non conforme (ValidationError) | build échoue (inchangé) |
| octets différents de la re-dérivation (`verifier_octets`) | build échoue (inchangé) |

## Décisions

- **Licence : l'échec en bloc est gardé.** AD-17 : « Il échoue si une source manque au Registre. `--variante diffusable` échoue sur toute source dont l'usage n'est pas `diffusable`. » C'est une contrainte du Registre et de la variante, pas un défaut d'une session ; écarter silencieusement des sessions masquerait un Registre incomplet. Écarter et compter est une décision de fond : **à confirmer par Anaël** si elle la souhaite.
- `lancer_validation` et `valider_session` reçoivent `taches` (défaut `charger_taches()` pour `lancer_validation`) ; la CLI n'est pas modifiée. `valider_session` sans `taches` charge `charger_taches()` (le contrôle de dérivation n'est jamais sauté).
- `ProvenanceInvalide` reste la base : `DerivationRefusee` en dérive, build l'attrape comme avant.

## Auto Run Result

- Fichiers : `src/slmsp/data/build.py`, `src/slmsp/data/validate.py`, `src/slmsp/core/schemas/rejet_donnees.py` (3 motifs), `tests/data/test_validate.py` (3 tests).
- Report : refus `LigneEntrainement`/date et `verifier_octets` non rejoués par validate (non liés à une règle de session ; échec franc voulu).

## Revue

- low | corrigé | `valider_session(taches=None)` sautait `_controler_derivation` en silence : charge désormais `charger_taches()`.
- low | rejeté (documenté) | `outil_hors_cassette` et `conversation_invalide` quasi inatteignables via validate (`_rejouer` lève `trace_divergente` avant) : gardés en défense en profondeur, car la règle partagée `construire_conversation` peut les lever seule.
- low | acté | licence et Registre restent des échecs en bloc de build (AD-17), choix assumé, code inchangé.
- low | rejeté | cassettes RD lues deux fois par session : coût marginal, correctif non trivial.
