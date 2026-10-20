---
title: 'O4e — remplacement des 5 items de dev1 rejetés deux fois'
type: 'bugfix'
created: '2026-10-20'
status: 'review'
context: ['{project-root}/_bmad-output/implementation-artifacts/spec-o4-jeu-dev.md', '{project-root}/_bmad-output/implementation-artifacts/spec-o4d-dev1-remplacements.md']
warnings: []
deferred: []
---

## Intent

**Problème :** après les corrections O4d, la revérification croisée (consigne 3) retient 155 items et en rejette 5 une seconde fois : CR-512, NR-511, NR-516, NR-517 et RD-501. Le gel `relu-llm` exige 20 items retenus par Tâche.

**Approche :** remplacer chaque item, déjà corrigé une fois, par un item neuf. Le neuf garde la Tâche, la difficulté et le thème de l'item remplacé ; il suit le même procédé et le même schéma qu'O4b et prend les identifiants libres suivants (521). L'item remplacé reste dans les brouillons et est écarté par le mécanisme existant, un verdict `rejete` dans `verification/`. Aucun plaidoyer, aucun appel payant.

## Boundaries & Constraints

**Always :** items d'évaluation seulement ; faits RD tirés de la cassette enregistrée ; consigne CR d'origine conservée (comparabilité avec v1.1).

**Never :** donnée d'entraînement (D1), modification de v1.0 ou v1.1, note adressée aux juges, réécriture des verdicts croisés.

## Livré

| Remplacé | Neuf | Difficulté, thème | Contenu |
|---|---|---|---|
| CR-512 | CR-521 | moyen, collectivites | Notes fictives (402 mots) d'une commission des marchés de plein air. Pièges : un chiffre corrigé en séance, un tarif voté entre deux propositions, une action reprise par une autre personne, deux propositions sans décision. Jours et dates vérifiés. |
| NR-511 | NR-521 | facile, non-classe | Tri alphabétique de 5 noms, un par ligne, sans puce ni introduction. |
| NR-516 | NR-522 | moyen, non-classe | Relevé de 4 dates, dans l'ordre, au format JJ/MM/AAAA, sans autre texte. |
| NR-517 | NR-523 | moyen, non-classe | Remplacement de « Monsieur le maire » par « Madame la maire » avec les accords, sans autre changement. |
| RD-501 | RD-521 | facile, social-autonomie | Cassette `eval/cassettes/RD-521/s1.json` (`slmsp mcp record`, 2026-10-20T14:15:32Z, `search_datasets`). Jeu « Bénéficiaires du minimum vieillesse » (5369963ca3a729239d20493a, Ministère des Solidarités et de la Santé). L'entrée ne nomme pas de producteur, car le grief de RD-501 portait sur « la DREES ». |

Les NR neufs n'ont qu'une réponse juste : l'ordre, le format, la casse et l'absence d'ajout sont imposés par la consigne et repris dans les critères. Cela répond à la cause commune relevée en O4d.

- Les items remplacés restent dans les brouillons. Chacun reçoit un verdict `rejete` (motif `autre`, « remplacé par … ») dans `verification/`, et `construire_jeu.py assembler` l'exclut. Chaque item neuf reçoit un verdict de second passage `accepte`. `verdicts-croises.jsonl` n'est pas modifié.
- Tests réalignés :
  - `test_items_dev1.py` : les cassettes RD-501 à RD-521 sont toutes citées ;
  - `tests/mcp/test_bac_a_sable.py` : 61 cassettes et 115 appels rejoués.
- README de construction : nouvelle section O4e.
- Contrôles :
  - `construire_jeu.py assembler --version dev1` : 160 items, SHA-256 `9ec383b8…`, 5 exclus ;
  - `slmsp eval gel --version dev1 --verifier-seulement` : 0 erreur, 0 écart ;
  - disjonction des items du worktree contre les données du dépôt principal (v1.0, v1.1, `data/train/v*`, amorces seed ; 25 jeux) : 0 conflit.

## Auto Run Result

Statut : review. Tests ciblés `tests/eval_outils`, `tests/evaluation` et `tests/mcp/test_bac_a_sable.py`, avec `SLMSP_EVAL_SOURCES` : 1438 passés.

Suite pour l'orchestrateur, la seule étape payante :
1. `python eval/outils/verifier_jeu_croise.py verifier --version dev1 --juges deepseek,glm`. Seuls les 5 items neufs sont appelés, soit 10 appels, environ 0,06 $.
2. `construire_jeu.py assembler --version dev1`.
3. `slmsp eval gel --version dev1 --statut relu-llm --graine <g>`.

Décisions :
- Pour écarter un item, on ajoute un verdict `rejete` dans `verification/`. C'est le mécanisme existant, et on ne supprime ni ligne de brouillon ni verdict croisé. C'est la solution la plus réversible.
- Le RD neuf est enregistré en mode connecté, avec un seul appel. La requête n'apparaît ni dans v1.0, ni dans v1.1, ni dans dev1.
- La consigne du CR neuf garde la forme commune aux 20 CR (« participants, points abordés, décisions, actions »). Le risque d'un grief « points abordés » reste ouvert (décision de l'orchestrateur en O4d).

Reports : si un item neuf est rejeté, il faudra le remplacer de nouveau (identifiants 522 et suivants, ou 524 pour NR).
