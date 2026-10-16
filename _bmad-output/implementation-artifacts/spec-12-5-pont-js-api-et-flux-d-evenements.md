---
title: 'Story 12.5 — Pont js_api et flux d''évènements'
type: 'feature'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-4-socle-de-l-interface.md'
warnings: []
deferred: []
---

## Intent

**Problem:** l'interface ne peut pas parler à `AssistantService` sans contourner le Harnais (AD-23).

**Approach:** `app/pont/` : `Pont` (exposé en `js_api`, FR-1, FR-2) délègue à `Conversation` (un fil de travail par génération, évènements `vers_dict` poussés par lots via le port `Fenetre.evaluate_js` -> `window.slmspRecevoir`) et à un bouchon par domaine (`mode`, `reglages`, `historique`, `retours`, `verification`) dont le docstring porte le contrat JSON.

## Contrat

- Toute méthode rend `{"ok": true, ...}` ou `{"ok": false, "erreur": {"code", "message"}}` (message sans texte saisi, masqué par `harness.service.masquer`).
- `envoyer(tache, messages, options)` rend la main aussitôt. Refus : `generation-en-cours`, `requete-invalide`. `arreter()` -> `{"ok": true, "en_cours": bool}`. `regenerer()` rejoue le dernier envoi (`rien-a-regenerer`). `nouvelle_conversation()`.
- `signaler_pret()` pousse `{"type": "pret"}`. `appeler("envoyer"|"arreter"|"regenerer"|"nouvelle_conversation"|"<domaine>.<methode>", *args)` ; un bouchon répond `non-implementee`.
- Côté JS (`pont-client.js`) : une réponse `{ok: false}` de `envoyer` devient un rejet, ce qui déclenche déjà `generation:erreur` du composer (texte conservé). Seul ajout au contrat de 12.4.

## Code Map

- `src/slmsp/app/pont/{__init__,conversation,erreurs,mode,reglages,historique,retours,verification}.py`
- `src/slmsp/app/ui/js/socle/pont-client.js` (rejet sur `ok: false`)
- `tests/app/{conftest,test_pont,test_document_temoin_app}.py`

## Auto Run Result

Décisions prises seul :
- `arreter()` ne ferme pas l'itérateur lui-même (un générateur en cours d'exécution ne peut pas être fermé d'un autre fil) : il lève un drapeau, le fil ferme au prochain évènement puis pousse `Fin(interrompue)`. Latence : un évènement du LLM.
- Lots : un `Jeton` s'accumule jusqu'à 16 ou 40 ms ; tout autre évènement vide le lot.
- Ajout hors liste : `pont/erreurs.py` (`NonImplementee`, sous-classe de `SlmspError`) et `tests/app/conftest.py` (charge les doublures du Harnais).
- Les tests assemblent via `slmsp.harness.assemblage.assembler` (`app` ne peut pas importer `cli`).

Reports / à confirmer par Anaël :
- Propriétaires des bouchons supposés : `mode` 12.9, `reglages` 12.10, `historique` et `retours` 12.11, `verification` 13.5. Les noms de méthodes des contrats sont des propositions.
- `Pont` ne persiste rien (historique) : l'enregistrement des conversations dans `Stockage` revient à 12.11.
- 12.6 doit appeler `Pont.signaler_pret()` après `pywebviewready` et fournir la `Window` comme `Fenetre`.
- Relecture de la fermeture : `arreter` pendant un LLM bloqué n'est effectif qu'au prochain jeton ; le délai de première tokenisation n'est pas interruptible.
