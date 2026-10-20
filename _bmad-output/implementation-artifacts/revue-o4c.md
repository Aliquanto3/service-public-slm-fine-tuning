# Revue de la story O4c (suite de dev1)

Commits relus : `e98228f`, `dbec22c` (branche `story/o4c-dev1-suite`, rebasée par fusion de `main`). Second avis Haiku et décisions A à D de l'orchestrateur appliqués.

## Constats

| # | Sévérité | Constat | Suite |
|---|---|---|---|
| 1 | high | Consigne v2 orientée vers l'acceptation (« une Tâche de rédaction… ne rend pas l'item ambigu », « l'absence d'une clé grille n'est pas un défaut »), appliquée seulement aux items à refaire : deux consignes pour un même jeu. | Corrigé : consigne neutre v3, deux précisions factuelles de format ; tout verdict d'une autre version est refait (décision A). |
| 2 | high | Les 76 retenus avec la consigne v1 n'étaient jamais revérifiés. | Corrigé par 1 : les 160 items sont revérifiés avec la v3. |
| 3 | high | Voie d'appel par `contestations.jsonl` : un rejet pouvait être relancé sur justification de l'auteur. | Corrigé : mécanisme retiré de l'outil ; le fichier reste une trace sans effet (décision B). |
| 4 | high | Les verdicts croisés n'avaient aucun effet : l'assemblage les ignorait et le gel `relu-llm` ne les lisait pas ; un item rejeté restait dans `items.jsonl`. | Corrigé : `assembler` et `composition` retirent un rejet croisé courant (empreinte et consigne) ; le gel `relu-llm` exige un « retenu » courant par au moins deux juges pour chaque item (décision C). Tests. |
| 5 | medium | Traçabilité de Q-518 fausse dans la spec (une seule phrase omise annoncée ; deux passages restent élidés). | Corrigé : spec détaillée d'après le chunk 6 de F24569 (décision D). |
| 6 | medium | Budget annoncé (1 $, pire cas 2 $) pour 84 items. | Corrigé : 320 appels, environ 1,7 $, pire cas environ 4 $ (décision D). |
| 7 | low | Constante de consigne en trois endroits (outil, assemblage, gel). | Rejeté comme défaut : scripts hors paquet ; égalité testée (`test_version_de_consigne_alignee_sur_l_outil`, `test_assembler_exclut_les_rejets_croises_courants`). |
| 8 | low | D1 : items d'évaluation et justifications relus, aucune donnée d'entraînement ni exemple de réponse ; fixtures factices. | Rien à corriger. |

## Vérifications

- `eval/jeu/dev1/items.jsonl` réassemblé à l'identique (SHA-256 `256a26ce…`, 0 exclu : les verdicts actuels sont de consigne v1).
- Tests ciblés : `tests/eval_outils`, `tests/evaluation`, `tests/judge` ; ruff ; contrôle rapide.

## Suite (orchestrateur)

`python eval/outils/verifier_jeu_croise.py verifier --version dev1 --juges deepseek,glm` (160 items, 320 appels, environ 1,7 $, pire cas environ 4 $), puis `python eval/outils/construire_jeu.py assembler --version dev1`, remplacement des items rejetés (chaque Tâche compte 20 items) et `slmsp eval gel --version dev1 --statut relu-llm --graine <g>`.
