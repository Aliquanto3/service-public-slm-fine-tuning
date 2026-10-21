---
title: '15.5c — corrections des 3 LC de dev2 rejetés à la revérification croisée'
type: 'bugfix'
created: '2026-10-21'
status: 'review'
context: ['{project-root}/_bmad-output/implementation-artifacts/spec-15-5b-dev2-corrections.md']
warnings: []
deferred: []
---

## Intent

**Problème :** la revérification croisée ciblée de dev2 (DeepSeek + GLM, consigne 3, commit c2d09ec) retient 152 items et rejette 3 LC : LC-615, LC-616 et LC-619.

**Approche :** même procédé que 15.5b (sans plaidoyer, grief traité et non contourné, consigne commune conservée). Les trois griefs sont fondés et se traitent honnêtement : la grille `informations_a_conserver` résumait ou interprétait le texte. Elle est réécrite au plus près de la lettre des articles, alinéa par alinéa (`version_item` + 1, verdict de construction 15.5c dans `verification/LC.jsonl`). Texte, consigne et termes juridiques sont inchangés. Aucun remplacement.

## Livré

| Item | Juge, motif | Traitement |
|---|---|---|
| LC-615 | GLM, fait absent : « dès 60 ans » pour « plus de soixante ans » ; « taux fixé pour l'AAH » et « mêmes prestations » non littéraux | Corrigé (v2) : « plus de 60 ans », pourcentage du décret de l'article L. 821-1 CSS, prestations du chapitre Ier du titre III ; repris aussi : conditions précisées par décret, article L. 231-2, établissements publics et privés nommés. 7 informations au lieu de 5 |
| LC-616 | DeepSeek, incohérent : « favorisant son développement, son autonomie et son insertion » absent de la grille | Corrigé (v2) : ajouté ; grille détaillée alinéa par alinéa (autorité judiciaire, apte à participer à la décision, représentation relative à la personne, dispositions législatives contraires, protections légales et contractuelles). 9 informations au lieu de 6 |
| LC-619 | DeepSeek, incohérent : « pour chaque poste à pourvoir », « après appel de candidatures », « dans l'ordre de la liste le cas échéant » omis | Corrigé (v3) : ajoutés ; repris aussi : présentations, disposition législative ou réglementaire, infirmité certaine, article L. 2121-16, moyens de communication audiovisuelle. 8 informations au lieu de 6 |

Contrôles :
- `construire_jeu.py assembler --version dev2` : 155 items, SHA-256 `165840ee…`. Le diff de `eval/jeu/dev2/items.jsonl` ne touche que les 3 lignes LC. Mêmes 7 exclusions qu'en 15.5b.
- `slmsp eval gel --version dev2 --verifier-seulement` : 155 items stricts, 0 erreur bloquante. Les 4 écarts de composition CO et CT d'avant restent (items laissés à la décision d'Anaël en 15.5b).
- `verifier_jeu_croise.py disjonction --version dev2 --reference <dépôt principal>` : disjoint.

## Auto Run Result

Statut : review. Tests ciblés `tests/eval_outils` et `tests/evaluation` avec `SLMSP_EVAL_SOURCES` : 1571 passés.

Revérification par l'orchestrateur (payante, environ 6 appels) : `verifier_jeu_croise.py verifier --version dev2 --juges deepseek,glm`. Seuls les 3 LC ont une empreinte nouvelle.

Décision prise seul : les imprécisions de même nature que le grief (paraphrases non littérales) ont été corrigées dans tout l'item, pas seulement le passage cité, pour éviter un nouveau rejet sur la phrase voisine. Ce n'est pas un changement anodin : chaque ajout reprend un fait de l'article.

À confirmer par Anaël : rien de nouveau (CO-609, CO-615, CT-602, CT-612 et CT-614 restent en attente depuis 15.5b).
