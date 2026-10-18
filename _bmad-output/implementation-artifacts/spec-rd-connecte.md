---
title: "Début de conversation des lignes RD normalisé sur le Mode connecté (jeu v2)"
type: 'bugfix'
created: '2026-10-18'
status: 'review'
baseline_commit: 'c16fb39'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-outils-rendu.md (§0, option A, décision d''Anaël du 2026-10-18)'
---

## Intent
Les 91 lignes RD de `data/train/v1` commençaient par « Passages de l'Index local : / Aucun passage… / Demande : … » (rendu `construire_messages(tache, entree, None)`), alors que leurs outils et tours d'appel sont ceux du Mode connecté, qui envoie la demande seule. Aucun mode du Harnais ne produit cet hybride (0/91 égal au Mode connecté).

## Décision
- `data/build.py` (`construire_conversation`, donc aussi `validate`) : toute Tâche qui a des `outils_autorises` compose son début par `harness.taches.recherche.messages_connecte`, la fonction de l'inférence. Règle fondée sur la propriété de la Tâche, sans slug. Les autres Tâches ne changent pas d'un octet.
- Nouvelle version `data/train/v2` (v1 intacte, convention `vN` de `_creer_version`). Le MANIFEST porte `mode_outils: "connecte"` (champ du schéma, défaut `"local"` pour v1) : l'empreinte change, avec `sha256_train`.
- Aucune régénération : le build est déterministe depuis le journal Mistral (SQLite partagé de `%LOCALAPPDATA%\slmsp\var`, ouvert en lecture seule), les cassettes et le run `data-filter` 20261017-151827-filter-e914 (déjà dans le worktree).

## Vérification
`python outils/verifier_rd_connecte.py <v1> <v2>` : 503 lignes ; 91 modifiées (RD, seul `messages[1]`, égal à la demande seule de `messages_connecte`), 412 identiques à l'octet ; système, outils, tours d'appel, résultats et réponses identiques ; `sha256_train`, `nb_lignes` et comptes par Tâche cohérents. Tests rapides sur faux journal : `tests/data/test_build.py` (RD en Mode connecté, Q inchangée, `mode_outils`, version jamais réécrite).

## Points à confirmer par Anaël
- Les réponses de Mistral ont été générées avec l'ancien prompt (« Aucun passage… ») ; elles restent cohérentes avec les résultats d'outils, mais le contexte de génération diffère du prompt d'entraînement v2.
- `train.jsonl` est ignoré par git (AD-21) : seuls MANIFEST.json et le script sont versionnés ; v2 se reconstruit avec la commande `slmsp data build --depuis 20261017-151827-filter-e914 --variante diffusable`.
- Le `tools` des lignes reste `if brut.tache == "RD"` (inchangé) ; l'ordre des clés de `tools` relève de spec-outils-rendu.

## Auto Run Result
status: review. SHA du jeu : voir MANIFEST de `data/train/v2`.
