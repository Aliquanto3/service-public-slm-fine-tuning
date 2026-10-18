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

## Revue
Revue Opus du 2026-10-18 (commit d'implémentation rebasé sur `62a109a`, sans conflit).

| Sévérité | Source | Constat | Suite | Motif |
|---|---|---|---|---|
| medium | second avis 1 | `tools` restait `if brut.tache == "RD"` et prenait tout `ctx.outils`, sans filtre `outils_autorises` ni la condition de la composition. | corrigé | `build.outils_de_ligne` : outils de `outils_autorises`, ordre du fichier (règle de `recherche.traiter`), vide pour `generique` et les Tâches sans outils. v2 re-dérivée en mémoire (`verifier_octets`, journal en lecture seule) : 503 lignes identiques à l'octet, aucun changement de v2. Test `test_outils_de_ligne_filtre_outils_autorises` (outil intrus, ordre inversé). |
| medium | second avis 2 | `outils/verifier_rd_connecte.py` ne vérifiait que le delta v1→v2. | corrigé | Ajouts : lignes modifiées = compte MANIFEST des Tâches à outils (et le reste identique), chaque ligne à outils réellement changée, `tools` = filtre `outils_autorises`, chaque ligne valide à `LigneEntrainement`, `sha256_train` de v1 et de v2 égal au SHA-256 de leur `train.jsonl`. Résultat sur v1 (dépôt principal, lecture seule) et v2 : « 503 lignes : 91 modifiées (message user), 412 identiques à l'octet ; sha256_train c6a7cb72… ; conforme », code 0. |
| low | second avis 3 | Docstring de `mode_outils` : « fait partie de l'empreinte » faux. | corrigé | Texte rectifié : champ informatif ; l'entraînement contrôle `sha256_train` au chargement et distingue le jeu par `jeu_version`/`jeu_build`. `CLES_INVARIANTS` non touché (conflit avec feat/outils-rendu). |
| low | second avis 4 | `MODE_OUTILS` constant étiquette tout build « connecte ». | rejeté | Exact par construction : la règle s'applique sans condition à tout build depuis ce commit ; un ancien MANIFEST sans le champ se relit `local` (défaut). |
| low | second avis 5 | `VERSION_EXTRACTEUR` non incrémenté. | rejeté | Elle versionne `data/extraction.py` (extraction des réponses Mistral), inchangé ici ; l'incrémenter changerait `meta.version_extracteur` des 503 lignes (412 lignes ne seraient plus identiques) sans motif. Le changement de composition est tracé par `mode_outils`, la version `v2` et `sha256_train`. |
| low | revue | Les tours d'outils (`_tours_outils`) restent conditionnés à `brut.tache == "RD"`. | reporté | Seule RD a des outils aujourd'hui ; à généraliser si une autre Tâche reçoit des `outils_autorises` (sinon `tools` non vide sans tour d'appel). |

Complexité : 0 constat (build et vérificateur linéaires en nombre de lignes).
