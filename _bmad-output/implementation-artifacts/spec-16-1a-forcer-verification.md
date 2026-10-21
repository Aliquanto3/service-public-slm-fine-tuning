---
title: 'Revérification forcée d''items de dev2 (story 16.1a)'
type: 'feature'
created: '2026-10-21'
status: 'review'
---

## Intent

**Problem:** `verifier_jeu_croise.py verifier` reprend les verdicts à empreinte et consigne égales : relancer « en l'état » CO-609, CO-615, CT-602, CT-612, CT-614 (décision d'Anaël du 21/10 05:41) ne rappelait aucun juge.

**Approach:** option `--forcer ITEM_ID[,...]` de `verifier`.

## Comportement

- Pour les items forcés seulement, tous les juges sont rappelés ; sans `--forcer`, rien ne change.
- Le nouveau verdict s'ajoute au journal `verdicts-croises.jsonl` (ajout seul) avec `force: true` et `horodatage` (UTC, ISO) ; l'ancien reste. Le dernier fait foi (`verdicts_courants`, rapport).
- Identifiant inconnu de la version : `ErreurOutil` avant tout appel (code 2).

## Auto Run Result

- Tests : 2 nouveaux (forcer/reprise/plus récent/ancien conservé ; inconnu refusé), `tests/eval_outils/test_verifier_jeu_croise.py` 41 verts.
- Décision simple : les lignes non forcées n'ont pas d'horodatage (format inchangé).
- Report : exclusion des items qui restent rejetés après relance = story 16.1, hors de ce périmètre.
- Commande : `uv run python eval/outils/verifier_jeu_croise.py verifier --version dev2 --juges deepseek,glm --forcer CO-609,CO-615,CT-602,CT-612,CT-614` (appels OpenRouter payants, lancés par l'orchestrateur).

## Revue

- MEDIUM, corrigé : une relance forcée `incomplet` écrasait un verdict `rejete`/`retenu` (dernier verdict = `incomplet`, item réintégré dans le jeu). Elle n'est plus écrite ; item signalé sur stderr, code de sortie 1 ; test.
- MEDIUM, corrigé : écriture en fin de lot, une interruption perdait les appels payés. Écriture et flush par item (`sur_ligne`) ; test d'interruption.
- MEDIUM, corrigé : relance de `--forcer` après succès rappelait les juges. Dernière ligne `force` à jour = 0 appel, sauf `--forcer-encore` ; test.
- LOW, corrigé : `.strip()` sur chaque identifiant de `--forcer` ; test.
- Note : `construire_jeu.py` lit le dernier verdict ; inchangé, correct puisque le dernier n'est plus un `incomplet` forcé.
