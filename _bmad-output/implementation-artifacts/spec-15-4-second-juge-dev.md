# Spec 15.4 — Second juge désactivé pour tout jeu `dev*`

## Cause
Défaut réel établi : `ouvrir_juges` ne coupait le second juge que via `[jeux.<jeu>] second_juge = false` ; un jeu `dev*` sans section (dev2, dev10…) gardait Mistral. **Cause non reproduite pour dev1** : aucun verdict ni appel Mistral sur les notations dev1 du 20/10 ; le constat du plan est probablement antérieur à la section `[jeux.dev1]`. Le test « échoue avant correctif » ne vaut que pour dev2/dev10.

## Correctif
- `gel.jeu_sans_second_juge(jeu)` (préfixe `dev`), utilisé par `ouvrir_juges` (aucun client Mistral construit), par `noter` (avant `nouveau_run` : manifeste sans second juge, y compris `--reprendre` avec des juges déjà ouverts) et par `_noter_dans` (défense en profondeur ; `demandes_second` = 0 sans second juge).
- Gels futurs d'un jeu `dev*` : échantillon `second_juge` vide (MANIFEST gelé de dev1 inchangé). Schéma inchangé.
- `eval comparer`/tableau : statut « kappa non calculé » pour une Tâche à kappa sans kappa ; `fragile` garde son sens (kappa calculable sous seuil), schéma lu par v1.1 inchangé.
- `composition._empreintes` compare la présence du second juge.

## Revue
- MEDIUM, second avis : cause dev1 non établie : consigné ci-dessus, corrigé (défaut dev* sans section).
- LOW, second avis : manifeste écrit avant retrait du second juge : corrigé (`noter`, test avec second injecté).
- LOW, second avis : gel tirait l'échantillon second juge pour dev* : corrigé pour les gels futurs ; `fragile=False` laissé (sémantique du schéma), indicateur « kappa non calculé » ajouté en CLI.
- LOW, second avis : `_empreintes` sans présence du second juge : corrigé (test de refus).
