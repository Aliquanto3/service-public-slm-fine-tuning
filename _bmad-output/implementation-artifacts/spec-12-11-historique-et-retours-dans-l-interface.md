---
title: 'Story 12.11 — Historique et Retours dans l''interface'
type: 'feature'
created: '2026-10-17'
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

**Problem:** les domaines `historique` et `retours` du pont étaient des bouchons, les vues correspondantes des modules vides, et aucune conversation n'était enregistrée (FR-4, FR-19, FR-20).

**Approach:** `PontHistorique` et `PontRetours` sur `Stockage` (seul propriétaire de la base) ; `historique.js` liste, rouvre, supprime et **enregistre** les conversations ; `retours.js` fournit les pouces et l'export dans l'onglet Retours.

## Contrat

- `historique.{lister, ouvrir, enregistrer, supprimer, annuler_suppression}` : détail dans `pont/historique.py`. `tout_effacer` du bouchon est abandonné : `reglages.effacer_historique` (12.10) existe déjà.
- `retours.{noter, lister, apercu_export, exporter}` : détail dans `pont/retours.py`. `noter(conversation_id, indice du message, jugement, commentaire)` relit la conversation enregistrée pour en tirer question, réponse et sources.
- Export : `apercu_export` construit l'export anonymisé (12.3) et le garde ; `exporter` ouvre « Enregistrer sous » (port `choisir_fichier`, câblé sur pywebview par `principal.dialogue_enregistrer`) et écrit **l'aperçu relu**, via `export_retours.ecrire(confirme=True)`. Aucune Requête sortante.
- Enregistrement : fait côté interface (`historique.js`), à la fin de chaque réponse des Tâches de dialogue (Question, Recherche de données). Première réponse : création ; suivantes : remplacement par `id` ; Régénérer : remplace la dernière réponse. Les enregistrements sont sérialisés.
- Pouces : posés par `historique.js` dans `.reponse-actions` de la réponse enregistrée (sans modifier `reponse.js`), composant `creerPouces` exporté par `retours.js`.
- Rouverture : `window.slmsp.activer(tâche)` puis évènement de bus `historique:rouvrir`, que `composants/conversation.js` consomme pour reconstruire le fil.

## Code Map

- `src/slmsp/app/pont/{historique,retours,__init__}.py` (`__init__` : paramètre `choisir_fichier`)
- `src/slmsp/app/ui/js/vues/{historique,retours}.js`, `src/slmsp/app/ui/css/{historique,retours}.css`
- Hors zone, minimal : `src/slmsp/app/principal.py` (`dialogue_enregistrer`, 1 argument ajouté à `Pont(...)`) ; `src/slmsp/app/ui/js/composants/conversation.js` (+25 lignes : abonné `historique:rouvrir`)
- `tests/app/test_pont_historique_retours.py`, `tests/app/ui/test_vues_historique_retours.py` (`ui`)

## Auto Run Result

Décisions prises seul :
- Seules les Tâches de dialogue (Q, RD) sont enregistrées. Les rédactions (CR, LC…) ne le sont pas : leur texte collé ne doit pas être conservé sans décision explicite (FR-38). EXPERIENCE.md prévoit pourtant une entrée pour elles.
- Pouce bas : le Retour est enregistré au clic sur « Envoyer mon retour » (commentaire facultatif), et non au clic sur le pouce, pour ne pas créer deux lignes (`Stockage` n'a pas de mise à jour). Un pouce bas sans validation n'est pas enregistré.
- Un jugement par réponse affiché ; rouvrir une conversation permet de noter de nouveau (le lien Retour/réponse n'est pas stocké).
- Les `sources` d'une conversation sont celles de sa dernière réponse (le schéma n'en stocke qu'une liste).
- La rouverture rejoue `terminer` de chaque réponse : le lecteur d'écran annonce donc chaque réponse. À affiner avec 12.7.
- Un `id` inconnu à l'enregistrement (supprimée entre-temps) crée une nouvelle conversation au lieu de ressusciter l'ancienne.
- Non couvert, à une story ultérieure : « Annuler » persiste seulement 5 s dans l'interface (une seule suppression annulable affichée à la fois, la précédente reste restaurable côté `Stockage` jusqu'à ses 5 s).

## À confirmer par Anaël

Libellés proposés (D1 : aucun texte présenté comme officiel) :
- Repris d'EXPERIENCE.md : « Vos conversations apparaîtront ici. Elles restent sur ce poste. », « Merci, retour enregistré sur ce poste », « Qu'est-ce qui n'allait pas ? », « Vous n'avez encore donné aucun retour. », « Exporter mes retours », « Enregistrer le fichier », « Supprimer », « Annuler ».
- Inventés ici : « Envoyer mon retour », « Fermer l'aperçu », « Conversation supprimée. », « Conversation rétablie. », « Réponse utile (pouce haut) » / « Réponse à améliorer (pouce bas) », « Votre avis sur cette réponse », « Vos retours restent sur ce poste. Vous pouvez les exporter dans un fichier, que vous transmettez vous-même. », messages d'échec et d'annulation de l'export.
- Décision de fond : enregistrer ou non les rédactions dans l'Historique (EXPERIENCE.md dit oui ; FR-38 invite à la prudence).
- Décision de fond : pouce bas enregistré à la validation (voir ci-dessus).
- Dialogue « Enregistrer sous » : non essayé avec un vrai pywebview (extra absent du poste) ; testé avec un faux module `webview` (ancienne et nouvelle API).
