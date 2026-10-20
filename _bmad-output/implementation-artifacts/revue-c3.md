# Revue C3 : fusion DoRA sûre (commit 810a911)

Relecture après fusion de main, avec la liste du second avis (Haiku).

## Revue
- high (second avis 2) : rejeté. Le NaN vient du forward non fusionné sur une base bf16, qui n'est pas le modèle entraîné. Aucun texte ne prétend que les deux sont identiques. Le vrai sujet est le point 3.
- medium (3, Q(W_i) en nf4) : mesuré sur le vrai modèle. `Q(W_i) ≠ 0` (norme de 0,0015 à 0,031), mais `lora_B` est nul et la magnitude n'a pas bougé depuis l'initialisation sur ces lignes : rien n'a été appris. La fusion à 0 rend la base bf16, comme une fusion QLoRA standard. Le code ne change pas et l'export e69a est conservé. Détail dans diagnostic-c3.md.
- medium (4, test lignes vivantes) : corrigé. Ajout de `test_fusion_dora_lignes_vivantes_egales_au_forward_non_fusionne`, avec un adaptateur entraîné simulé : `lora_B` et magnitude aléatoires, et une ligne morte au même état que sur 1f18. Fusion égale au forward non fusionné sur les lignes vivantes. Lignes vivantes identiques avec et sans garde.
- low (5, convolutions DoRA) : documenté dans la docstring. Les modules ne sont pas ciblés, donc sans effet.
- low (6, monkeypatch non thread-safe) : documenté. L'export est séquentiel.
- low (7, normes subnormales) : rejeté. Une norme non nulle donne `m/‖V‖ · V`, fini. Une garde par epsilon modifierait des lignes légitimes.
- low (8, non-régression des lignes non nulles) : couvert par le test du point 4.
