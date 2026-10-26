# Transfert depuis slm-quality-bench : calibrer le Juge sur des étiquettes humaines

Note du 2026-10-26. Source : [slm-quality-bench](https://github.com/Aliquanto3/slm-quality-bench), calibration du juge sur la campagne `pilot-20261017` (décision consignée dans `docs/spec/juge-et-calibration.md` de ce dépôt).

## Ce qui se transfère, et ce qui ne se transfère pas

- **Pas les données.** Les 100 étiquettes de slm-quality-bench portent sur des tâches de rédaction générales (consignes de forme, faits à mentionner), pas sur le service public. Trop peu nombreuses et trop éloignées pour un entraînement (SFT, ORPO, KTO), et le fine-tuning est arrêté depuis le 2026-10-22 (`docs/bilan-fine-tuning.md`).
- **La méthode, oui.** Ici, le Juge (Claude v1.1, GLM-5.3) note selon `eval/grille-juge-v1.md`, mais aucun humain n'a validé ses notes : l'échantillon `eval/calibrage/echantillon-calibrage.md` (16 items) sert à l'évaluation, sans étiquette de référence. Tant que l'accord du Juge avec un humain n'est pas mesuré, un Score de Tâche ne dit pas si l'écart vient du modèle ou du Juge.
- **Les constats, comme hypothèses à vérifier ici** (ils ne valent que pour les tâches de slm-quality-bench).

## Constats de slm-quality-bench (100 étiquettes d'Anaël, critères binaires en français)

| Juge | Accord | IC 95 % (Wilson) | Défauts humains repérés |
|---|---|---|---|
| Opus 5.5 | 100 % | [96,3 ; 100] | 12 / 12 |
| MiMo | 97 % | [91,5 ; 99,0] | 9 / 12 |
| Haiku 5.5 | 90 % | [82,6 ; 94,5] | 5 / 12 |

- **Taux de base.** 88 des 100 critères étaient satisfaits : un juge qui répondrait toujours « oui » aurait 88 % d'accord. Un accord brut ne vaut qu'à côté de ce taux ; compter aussi les défauts repérés.
- **Indulgence plutôt que sévérité.** Les erreurs de Haiku sont surtout des défauts acceptés (7 sur 12). Pour un assistant de service public, l'indulgence est l'erreur coûteuse.
- **La stabilité n'est pas la justesse.** Haiku rejoué donne 99,7 % de verdicts identiques tout en manquant plus d'un défaut sur deux (7 sur 12).
- **Critère à deux exigences = désaccord.** Le seul écart initial humain/Opus venait d'un critère qui combinait deux éléments (« cause X au-delà d'environ 29 degrés ») : écrire « à la fois … et … » ou scinder le critère.
- **Défauts hors grille.** Les notes libres d'Anaël relèvent surtout des **infidélités au document** (montant, durée, acteur mal compris, phrase inventée), des **fautes de langue** et des **réponses en anglais**. La grille d'ici couvre déjà l'exactitude et les inventions (« Doute = note basse ») ; les fautes et la langue de réponse sont des contrôles automatiques candidats.

## Démarche à reprendre

1. **Tirage stratifié** d'au moins ~50 items par grille de Tâche notée par le Juge, au hasard (jamais seulement les cas où deux juges divergent : l'accord mesuré ne vaudrait plus pour l'ensemble), en parts égales par modèle évalué.
2. **Étiquetage humain hors ligne**, critère par critère, avec la même échelle que le Juge (0/1/2 ici), plus une note libre facultative et un choix « indécidable ». slm-quality-bench l'a fait avec une page HTML locale (sauvegarde dans le navigateur, export JSONL).
3. **Format d'étiquette** : une ligne JSONL par critère, clé identique à celle du verdict du Juge, par exemple `{"key": "<run>|<modele>|<item>|<critere>", "label": 2, "author": "…", "labeled_at": "AAAA-MM-JJ", "note": null}`. Fichier en ajout seul, clé en double refusée.
4. **Mesures** : accord avec intervalle de Wilson, indulgence (Juge plus favorable que l'humain) et sévérité séparées, accord par Tâche, défauts repérés ; pour l'échelle 0/1/2, accord exact et accord à un point près.
5. **Seuils fixés avant de lire les résultats** (slm-quality-bench : accord ≥ 0,95), puis choix du Juge consigné.

Les exemples d'items à étiqueter restent sous le régime du registre `data/registre-licences.toml` (usage `evaluation_seulement` pour l'échantillon de calibrage).
