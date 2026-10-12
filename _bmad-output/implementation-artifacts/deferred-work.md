# Travail reporté

## Deferred from: code review of lot 2, évaluation (2026-10-12)

- **W1. `eval run --phase toutes` après une génération `partiel-erreur` : aucun test n'atteint la notation** (`src/slmsp/cli/eval.py:309`). Ajouter un cas paramétré à `test_cli_toutes`, avec un `FakeLlm` qui échoue sur un item. Il vérifie qu'un run `eval-notation` est créé et que la commande sort en code 1.
- **W2. Les réglages de décodage (`GRAINE`, `MAX_TOKENS`, `OPTIONS_LLM`) restent des constantes de `generation.py`, et une sortie tronquée reste `ok`.** Les déplacer dans `config/evaluation.toml`, comme le prévoyaient les Design Notes de la 5.3. Ajouter à `Generation` un indicateur de troncature (`finish_reason`) pour les CR longs et les RE `detaillee`.
- **W3. Jeu v1.1 : déclarer `valeurs_attendues.colonnes` sur les 5 items RD de la méthode `valeurs`, puis geler** (issu de D1, option 1). Le correctif P8 lit la liste. Sans elle, le jeu v1.0 garde un biais : RD-017, RD-010 et RD-039 peuvent être notés faux sur une réponse exacte. Colonnes proposées : RD-010 `Nbre_bailleurs` et `Nbre_logements` ; RD-017 `Nombre` ; RD-023 `Année` et `Note Index` ; RD-030 `REG` et `CHEFLIEU` ; RD-039 `Effectifs` et `IPS`. Il faut une nouvelle version, l'export de revue, une relecture humaine et `gel --statut relu`, à faire avant la Baseline complète.
