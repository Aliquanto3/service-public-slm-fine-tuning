---
status: review
---

# Story S3 — Juges tiers OpenAI et Google (fiabilisation des verdicts)

Décision d'Anaël (19/10/2026, 21 h 40) : ajouter un juge d'une autre famille, OpenAI ou Google, **tout de suite** ; plafond **10 € par fournisseur** pour l'ensemble du run. Constat : kappa principal (Claude) / second juge (Mistral) à 0,00 sur CR, LC, RE, CT (`config/evaluation.toml` : fragile si < 0,6).

## Principe
- Les juges tiers **ne changent pas le score officiel** (juge principal, grille `eval/grille-juge-v1.md`, jeu v1.1 gelé). Ils produisent un **avis comparatif** : verdicts par critère et accord avec le principal et le second juge.
- Ils notent **les items de l'échantillon du second juge** (part 1/5, `evaluation/gel.py:360`, `judge/second.py:133`), avec le même gabarit de prompt et le même schéma de verdict que le second juge, pour une comparaison à trois ou quatre sur les mêmes items.
- Nouveau run, jamais de réécriture d'un run de notation : `slmsp eval juges-tiers --depuis <run eval-notation> --fournisseur openai|google [--plafond-estime EUR]` → `runs/eval-juges-tiers/<id>/` (`run.json`, `etat.jsonl`, `verdicts.jsonl`, `accords.json`).

## Périmètre
1. **Client compatible OpenAI** (`src/slmsp/fournisseurs/` ou à côté de `mistral/`, au plus proche des conventions) : Chat Completions, `base_url` par fournisseur dans la config (`openai` : `https://api.openai.com/v1` ; `google` : `https://generativelanguage.googleapis.com/v1beta/openai/`), température 0, sortie JSON. Réessais par `net/relances.py` (429, 5xx). Journal sqlite des appels comme `mistral/journal.py` (usage, tokens, coût, modèle renvoyé par l'API).
2. **Secrets** par `core/secrets.py` (jamais dans `os.environ`, jamais journalisés) : `OPENAI_API_KEY` ; `GEMINI_API_KEY`, sinon `GOOGLE_API_KEY`.
3. **Réseau** : ajouter `api.openai.com` et `generativelanguage.googleapis.com` en POST (et GET pour la liste des modèles) au seul profil `outillage` de `config/reseau.toml`. Pas au profil assistant.
4. **Vérification sans dépense** : `slmsp eval juges-tiers --verifier [--fournisseur …]` affiche, par fournisseur, clé présente / absente, et la liste des modèles disponibles (`GET /models`, gratuit) filtrée sur `gpt-`, `gemini-`. Aucune génération.
5. **Config** `config/juges.toml`, section `[juges_tiers.<fournisseur>]` : `modele`, `base_url`, `temperature`, `max_tokens`. Le modèle par défaut reste à confirmer par `--verifier` : la session principale l'écrira. Les tests utilisent des faux.
6. **Budget** : postes `openai` et `google` de la campagne `finetune-v9-2026-10-19` à 10 € chacun dans `config/budgets.toml`, avec leurs imputations ; entrées `config/tarifs.toml` pour les modèles retenus (prix en USD/Mtok, avec commentaire de source et « à vérifier sur la page officielle »). Estimation avant dépense, refus si elle dépasse `--plafond-estime`, réservation au pire cas par item (pas par le max du lot, cf. INC-2), libération après l'appel, comme pour le juge principal.
7. **Accords** (`accords.json`, et affichage en fin de commande) : par tâche et par critère, kappa de Cohen (`evaluation/scores.py:114`) et taux d'accord brut, tiers/principal, tiers/second, principal/second, sur les mêmes items. Signale les items où trois juges ou plus ne s'accordent pas.
8. **Cache** : clé modèle + gabarit + item (`judge/cache.py`), pour qu'une relance ne repaie pas.

## Tests (faux client, aucun réseau)
Parsing du verdict ; refus par `--plafond-estime` ; réservation puis libération ; secret absent → erreur claire sans valeur affichée ; `--verifier` sans clé ; calcul des accords sur un mini-run ; aucune écriture dans le run de notation source ; profil réseau assistant inchangé.

## Hors périmètre
Changer le juge principal ou la grille ; renoter les items hors échantillon ; utiliser un juge tiers dans le score officiel (décision d'Anaël après son audit).

## Après fusion (session principale)
`--verifier`, choix des modèles (le plus récent modèle « Pro » ou équivalent de chaque fournisseur), tarifs, puis juges tiers sur les notations des 3 Baselines et des 3 M1 v11.

## Révision 1 (relecture de la spec, 19/10 22 h) — prime sur ce qui précède
1. **Effectif** : l'échantillon du second juge ne compte que 3 à 5 items par tâche (`eval/jeu/v1.1/MANIFEST.json`, `echantillons.second_juge`) ; un kappa dessus n'est pas interprétable. Les juges tiers notent donc **tous les items jugés des tâches CR, LC, CT, RE** (option `--taches`, défaut `CR,LC,CT,RE`), et non l'échantillon du second juge. `accords.json` donne pour chaque paire de juges l'effectif commun ; en dessous de 10 paires, statut « non concluant » au lieu d'un kappa.
2. **Schéma** : `ConfigJuges` (`judge/config.py:65`) est `extra="forbid"` ; ajouter un champ `juges_tiers` optionnel (modèle pydantic par fournisseur), sans changer le chargement du principal ni du second juge. Test : `juges.toml` actuel et `juges.toml` avec `[juges_tiers.openai]` se chargent.
3. **Budget** : une campagne ancrée refuse un nouveau poste (`budget/registre.py:350-366`). **Ne touche pas `config/budgets.toml`** : la session principale ouvre une nouvelle campagne avec les postes `openai` et `google` (10 € chacun) après la fin des notations en cours. Le code s'appuie sur les noms de poste `openai` et `google` et leurs imputations (`juge-tiers-openai`, `juge-tiers-google`) ; les tests fabriquent leur propre `budgets.toml`.
4. **Journal** : fichier distinct `appels-juges-tiers.sqlite`, hors de la liste d'accès de data et train (`core/artefacts.py:517`, AD-24), comme `appels-mistral-juge.sqlite`.
5. **Modèles de raisonnement** : paramètres par fournisseur dans la config (`max_completion_tokens` pour OpenAI, effort de raisonnement bas si disponible, pas de `temperature` si le modèle la refuse). Une sortie interrompue (longueur) **n'est pas mise en cache** : elle reste rejouable. L'estimation de coût compte une marge de tokens de raisonnement (paramètre de config).
6. **Secrets** : `core/secrets.py` lit un seul nom ; ajouter une lecture « premier présent parmi » pour `GEMINI_API_KEY` puis `GOOGLE_API_KEY`. `--verifier` affiche présent / absent sans lever.
7. **Tarifs** : entrées `config/tarifs.toml` regroupées dans un bloc commenté « juges tiers » **en fin de fichier** (S5 ajoute `mistral-large-4` près des entrées Mistral : pas de chevauchement).
8. **Gabarit** : même gabarit de prompt et même schéma de verdict que le **juge principal** pour la tâche (c'est lui qu'on audite), afin que l'accord mesure le juge et non le prompt.

## Révision 2 (décision d'Anaël, 19/10 ~22 h 10) — prime sur ce qui précède
1. GPT et Gemini sont retirés (risque de licence) : ni config, ni hôtes, ni secrets, ni postes, ni tarifs OpenAI ou Google ; le repli « premier secret présent parmi » est abandonné.
2. Seul fournisseur : **OpenRouter** (`https://openrouter.ai/api/v1`, `OPENROUTER_API_KEY`, hôte `openrouter.ai` au profil `outillage`, poste `openrouter`, imputations `juge-tiers-openrouter` et `generateur-openrouter` pour S4) ; client générique « messages → texte + usage » réutilisable hors juge ; `usage.cost` journalisé.
3. Juges tiers d'autres familles servis par OpenRouter ; `--verifier` filtre `deepseek/`, `z-ai/` ou `zhipu`, `mistralai/`, `moonshotai/`, `xiaomi/`.

## Implémentation
- **Fichiers** : `src/slmsp/fournisseurs/` (nouveau paquet, couche 2 : `client.py` client compatible OpenAI + `verifier`, `journal.py` journal sqlite en ajout seul), `src/slmsp/judge/tiers.py` (`JugeTiers`), `src/slmsp/judge/config.py` (`ConfigJugeTiers`, champ `juges_tiers`), `src/slmsp/evaluation/juges_tiers.py` (phase, accords, assemblage réel), `src/slmsp/cli/eval.py` (`eval juges-tiers`), `config/reseau.toml` (2 règles OpenRouter, chemins exacts), `config/juges.toml` et `config/tarifs.toml` (modèles commentés seulement), `tests/test_architecture.py` (couche `fournisseurs`). Tests : `tests/fournisseurs/`, `tests/judge/test_tiers.py`, `tests/evaluation/test_juges_tiers.py`.
- **Commandes** : `slmsp eval juges-tiers --verifier` ; `slmsp eval juges-tiers --depuis <run eval-notation> --juge <nom> [--taches CR,LC,CT,RE] [--plafond-estime EUR]`.
- **Choix** : section `[juges_tiers.<nom>]` (plusieurs modèles OpenRouter possibles) et option `--juge <nom>` au lieu de `--fournisseur` ; clé de cache = `cle_verdict` (modèle, gabarit, schéma, item, sortie) + `effort_cle` (`tiers-temperature-…+effort-…+format`) ; paramètres envoyés : `max_tokens`, `temperature` seulement si configurée, `reasoning.effort` si configuré, `response_format` json_schema strict (ou json_object), `provider.require_parameters = true` ; jetons de sortie = max(`completion_tokens`, `total − prompt`) ; registre réglé au tarif de `tarifs.toml` (pire cas réservé par item), `usage.cost` seulement journalisé ; journal `appels-juges-tiers.sqlite` dans `SLMSP_VAR_DIR`, refusé à `data` et `train` par la liste d'accès existante (testé) ; `--verifier` affiche les prix `/models` d'OpenRouter pour écrire `tarifs.toml`.
- **Limites** : aucune entrée de tarif réelle (modèles à choisir après `--verifier`) : sans elle, `TarifInconnu` avant toute dépense ; la comparaison à quatre (deux juges tiers ensemble) n'est pas faite, chaque run compare un tiers au principal et au second ; le coût réglé au registre suit notre tarif prudent, pas `usage.cost`.

## Auto Run Result
- Statut : review. Décisions prises seul (solution simple et réversible) : `--juge <nom>` plutôt que `--fournisseur` ; tarifs laissés en modèle commenté ; registre réglé au tarif local et non à `usage.cost` (**à confirmer par Anaël**) ; `provider.require_parameters` toujours envoyé.
- Reports : comparaison simultanée de plusieurs juges tiers dans `accords.json` ; règlement du registre au coût annoncé par OpenRouter.
