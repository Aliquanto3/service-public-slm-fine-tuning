# Revue O4d — corrections des 37 items rejetés de dev1

Commit relu : `a98328e` (branche `story/o4d-dev1-remplacements`). Second avis : Haiku. Reviewer : Opus. Aucun appel payant.

## Constats

| # | Sévérité | Item | Constat | Suite |
|---|---|---|---|---|
| 1 | high | CO-516 | La licence et la note justifiaient `fictif` auprès des juges (« d'où fictif : true »). | Corrigé. Note de provenance d'origine. La licence décrit l'origine de chaque texte : référence F642, entrée fautive créée pour l'évaluation. `fictif` reste vrai (arbitrage G4 de v1.1, comme CO-501 à 503, 510, 511 et 515, tous retenus). |
| 2 | high | CR-518 | Le 2 avril 2027 figurait à la fois dans les décisions et, comme bonne date, dans un piège. | Corrigé. Les pièges visent les dates remplacées en séance : « 26 mars, annoncé puis corrigé » et « 8 décembre, proposé puis remplacé ». |
| 3 | medium | CR-511 | Grief DeepSeek non traité : seule la consigne avait changé. | Corrigé. Ajout de la décision « prochaine réunion du comité en février 2027, date fixée par courriel », absente de la référence. L'action de M. Ba reprend la transcription : service communication, lettre d'information, réseaux sociaux. |
| 4 | medium | Q-520 | L'orientation était justifiée par un plaidoyer (« simple conseil pratique, non tiré de ces sources »). | Corrigé autrement. L'orientation reste exigée : la grille la demande (critère « Cas sans réponse ») et dev1 doit garder au moins 3 Q sans réponse, il en a exactement 3. Elle vise désormais le service des impôts indiqué sur l'avis de taxe foncière, que l'entrée mentionne. Commune et intercommunalité sont retirées. |
| 5 | medium | RD-519 | Une parenthèse plaidante expliquait l'URL « entreprises ». | Corrigé. Parenthèse retirée. L'URL `fiscalite-locale-des-entreprises` est vérifiée dans `eval/cassettes/RD-519/s1.json` et citée dans l'extrait de provenance. |
| 6 | medium | 20 CR | La consigne avait perdu les « points abordés », alors que le critère Structure de la grille les exige (comparabilité avec v1.1). | Corrigé. Consigne d'origine sur les 20 CR. Les 12 retenus sont restaurés à l'identique, avec leur empreinte et leur verdict retenu ; leurs verdicts de construction O4d sont retirés. |
| 6b | medium | CR-501, 502, 503, 506, 508, 512 | Le grief DeepSeek (« points abordés sans référence ») ne peut pas se traiter dans l'item : le schéma CR n'a pas de clé pour les points abordés, et un ajout serait un plaidoyer. | **Décision de l'orchestrateur.** Les 6 items passent en `version_item` 2 sans autre changement. Deux options : préciser le format dans la consigne du juge (« CR : les points abordés ne sont contrôlés que comme section présente », `VERSION_PROMPT` 4, revérification des 160 items, environ 1,7 $), ou relancer ces 6 items en l'état. |
| 7 | low | NR-503 | Critères retirés sans grief explicite. | Corrigé. Les critères de langue et de calcul sont rétablis. Ils n'exigent ni phrase complète ni détail du calcul : c'était le grief DeepSeek. |

## Contrôles

- `construire_jeu.py assembler --version dev1` : 160 items, SHA-256 `1f78dfd7…`, 0 exclu.
- `slmsp eval gel --version dev1 --verifier-seulement` : 0 erreur, 0 écart.
- Disjonction des items du worktree contre le dépôt principal (v1.0, v1.1, `data/train/v*`, amorces seed) : disjoint.
- Tests `tests/eval_outils` et `tests/evaluation` : 1097 passés, 300 ignorés. `test_items_dev1.py` sur les instantanés réels : 97 passés. Ruff et contrôle rapide : OK.
- Revérification à lancer : 37 items à empreinte nouvelle, soit 74 appels (environ 0,4 $). Les 123 retenus sont repris.
