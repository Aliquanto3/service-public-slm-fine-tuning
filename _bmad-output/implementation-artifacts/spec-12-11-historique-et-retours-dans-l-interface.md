---
title: 'Story 12.11 — Historique et Retours dans l''interface'
type: 'feature'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 1
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
- Enregistrement : fait côté interface (`historique.js`), à la fin de chaque réponse des Tâches de dialogue (Question, Recherche de données), d'après le modèle explicite des tours (question → réponse, raison de fin) que `composants/conversation.js` publie sur le bus (`conversation:tours`). Une session par Tâche garde l'`id` : première réponse, création ; suivantes, remplacement ; Régénérer et Réessayer remplacent la réponse du tour. Les enregistrements sont sérialisés et lisent l'`id` au moment de l'appel. Chaque message de l'Assistant porte ses `sources` ; une réponse interrompue est enregistrée avec `interrompue: true` ; un tour en échec n'est pas enregistré.
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
- Les `sources` de la conversation restent celles de sa dernière réponse ; chaque message de l'Assistant porte en plus les siennes, que `retours.noter` utilise (revue).
- La rouverture n'annonce qu'une fois « Conversation rouverte, N échanges » ; les réponses restaurées ne sont pas lues (revue).
- Un `id` inconnu à l'enregistrement (supprimée entre-temps) crée une nouvelle conversation au lieu de ressusciter l'ancienne.
- Non couvert, à une story ultérieure : « Annuler » persiste seulement 5 s dans l'interface (une seule suppression annulable affichée à la fois, la précédente reste restaurable côté `Stockage` jusqu'à ses 5 s).

## À confirmer par Anaël

Libellés proposés (D1 : aucun texte présenté comme officiel) :
- Repris d'EXPERIENCE.md : « Vos conversations apparaîtront ici. Elles restent sur ce poste. », « Merci, retour enregistré sur ce poste », « Qu'est-ce qui n'allait pas ? », « Vous n'avez encore donné aucun retour. », « Exporter mes retours », « Enregistrer le fichier », « Supprimer », « Annuler ».
- Inventés ici : « Envoyer mon retour », « Fermer l'aperçu », « Conversation supprimée. », « Conversation rétablie. », « Réponse utile (pouce haut) » / « Réponse à améliorer (pouce bas) », « Votre avis sur cette réponse », « Vos retours restent sur ce poste. Vous pouvez les exporter dans un fichier, que vous transmettez vous-même. », messages d'échec et d'annulation de l'export.
- Décision de fond : enregistrer ou non les rédactions dans l'Historique (EXPERIENCE.md dit oui ; FR-38 invite à la prudence).
- Décision de fond : pouce bas enregistré à la validation (voir ci-dessus).
- Dialogue « Enregistrer sous » : non essayé avec un vrai pywebview (extra absent du poste) ; testé avec un faux module `webview` (ancienne et nouvelle API).

## Revue

Revue du commit 8dd4287 (Opus, 2026-10-17), avec la liste du second avis (Haiku).

- **high**, second avis 1 — corrigé. Réessayer/Régénérer après une erreur dépilait la mauvaise question (réponse rattachée à la question précédente) ; au premier échange en erreur puis relancé, rien n'était enregistré. L'enregistrement suit désormais le modèle de tours tenu par `conversation.js` (`conversation:tours`). Tests UI : relance après erreur au premier et au second échange, Régénérer.
- **medium**, second avis 2 — corrigé. Changer de Tâche puis revenir créait une nouvelle entrée : une session par Tâche (`Map`). Tests UI : changement de Tâche, suite d'une conversation rouverte.
- **medium**, revue — corrigé. Deux réponses rapprochées : le second enregistrement partait avec l'`id` lu avant le retour du premier (doublon possible). L'`id` est lu au moment de l'appel.
- **medium**, second avis 3 — corrigé. `noter` prend les sources du message noté (champ `sources` par message), à défaut celles de la conversation pour sa dernière réponse seulement. Tests pont.
- **medium**, second avis 4 — corrigé. Rouverture : une seule annonce, `terminer(…, {annonce: false})` pour les réponses restaurées (`reponse.js`, option ajoutée). Test UI.
- **medium**, revue — corrigé. L'aperçu d'export gardé en mémoire survivait à « Effacer l'historique » (Paramètres) : `exporter` aurait écrit des Retours effacés. `exporter` compare les Retours à ceux de l'aperçu (`apercu-perime`) ; `noter` invalide l'aperçu ; la vue ferme l'aperçu affiché. Tests pont (second avis 7, low, inclus).
- **low**, second avis 5 — corrigé. Réponse interrompue enregistrée avec `interrompue: true`, rouverte avec la mention « Réponse interrompue ». Test UI.
- **low**, second avis 6 — corrigé. Échec d'enregistrement : message discret dans la colonne Historique (`.historique-echec`, `role=status`), masqué au succès suivant. Test UI.
- **low**, second avis 8 — corrigé. `tache` doit appartenir à `core.items.CODES` ; `ouvrir`, `supprimer`, `annuler_suppression` et `noter` exigent `identifiant_valide`. Tests pont.
- **low**, second avis 9 — corrigé par les tests ci-dessus.
- **low**, second avis 10 — corrigé. La confirmation d'écrasement du dialogue pywebview (WinForms `SaveFileDialog`, `OverwritePrompt` par défaut) n'est pas garantie par l'API ni vérifiable ici (extra absent) : `exporter` refuse un fichier existant (`fichier-existant`), message dans la vue. Test pont.
- **low**, revue — reporté. Tour en échec jamais relancé : sa question n'est pas enregistrée (aucune réponse). À trancher avec Anaël si l'Historique doit garder les questions sans réponse.
- Reporté (service réel) : essayer « Enregistrer sous » avec le vrai pywebview sur Windows (nom proposé, dossier Documents, annulation, refus d'un fichier existant).
