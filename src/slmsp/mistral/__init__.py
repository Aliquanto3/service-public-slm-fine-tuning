"""Adaptateur Mistral : point d'appel unique de l'API Mistral (AD-3, D1.2, AD-24).

- `config` : `config/mistral.toml` (modèle demandé, liste stable, motifs interdits, journaux).
- `journal` : journaux SQLite des appels, en ajout seul.
- `client` : `fabriquer_sdk` et `ClientMistral.appeler`.

AD-3 verrou 1 : `mistralai` n'est importé que dans ce paquet, et seulement par `client`.
AD-3 verrou 3 : chaque appel réserve au budget le sous-poste de son usage, part une seule
fois (aucune relance) et laisse une ligne de journal : requête, réponse brute, SHA-256,
référence budget, modèle résolu (vérifié contre la liste stable).

Séparation des journaux (AD-24) : les usages `generation` et `validation` vont dans
`SLMSP_VAR_DIR/appels-mistral.sqlite`, lisible par les pipelines `data` et `train` ;
l'usage `juge-second` va dans `SLMSP_VAR_DIR/appels-mistral-juge.sqlite`, que la liste
d'accès de `slmsp.core.artefacts` leur refuse : les textes d'évaluation envoyés au second juge
ne leur sont jamais lisibles. L'usage `generation` est réservé au Générateur (story 9.2).

Ce module n'importe rien : `import slmsp.mistral` ne charge pas `mistralai`.
"""
