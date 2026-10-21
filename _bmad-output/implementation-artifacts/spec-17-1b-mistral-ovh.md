---
title: 'Story 17.1b — Fournisseurs `mistral` (API directe) et `ovh` dans `eval run`'
type: 'feature'
created: '2026-10-21'
status: review
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-17-1-modele-distant.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-2026-10-20.md'
---

## Intention
Demande d'Anaël (21/10) : évaluer Mistral Small par l'API Mistral directe (OpenRouter → Mistral renvoie des 429) et préparer OVH AI Endpoints (clé à venir), avec le `ClientDistant` de la story 17.1.

## Périmètre
- **Fiche** (`evaluation/modele_distant.py`) : `fournisseur` ∈ `openrouter`, `mistral`, `ovh`. OpenRouter exige `famille/modèle`, `hebergeur` et `quantification` ; `mistral` et `ovh` refusent `hebergeur` (l'hébergeur est le fournisseur, consigné tel quel via `hebergeur_consigne`), `quantification` facultative. `FOURNISSEURS_DISTANTS` : bases des presets 17.4, secrets `OPENROUTER_API_KEY`, `MISTRAL_API_KEY`, `OVH_AI_ENDPOINTS_ACCESS_TOKEN` (`fournisseurs.client.FOURNISSEURS` inchangé, donc pas de `eval fournisseurs --verifier` sur ces deux-là).
- **Corps** (`client_distant.py`) : OpenRouter inchangé. Mistral et OVH passent par `inference.fournisseurs.ajouts_requete` (options du preset, `random_seed` chez Mistral, aucune graine chez OVH, `top_k` omis), sans `provider`, `reasoning` ni `usage`. OVH reçoit `stream_options.include_usage` ; Mistral ne le reçoit pas.
- **Contrôles du flux** : `provider` contrôlé chez OpenRouter seulement ; `model` contrôlé s'il est renvoyé ; hébergeur effectif consigné = nom du fournisseur.
- **Budget** : usage `eval-distant` (OpenRouter) ou `eval-distant-<fournisseur>`. `budgets.toml` : `eval-distant-mistral = "mistral.generation"`. Sans imputation (ovh) : `ConfigurationInvalide` « poste budgétaire ovh absent : à approuver par Anaël », avant la clé et avant tout appel. Aucun poste créé, aucun plafond changé.
- **Coût** : régularisation tarif × usage (registre existant). Tarif `mistral-small-2603` (0,15 / 0,60 USD par Mtok, source et note de reconfirmation). Aucun tarif OVH.
- **Réseau** : `reseau.toml` profil `eval-distant`, une règle POST `…/chat/completions` par hôte (openrouter.ai, api.mistral.ai, oai.endpoints.kepler.ai.cloud.ovh.net). `sans_reseau` n'admet que l'hôte de la fiche du run (`hote_de(base_url)`, déjà en place).
- **Fiches** : `mistral-small-mistral.toml` (`mistral-small-2603`, alias daté) et `qwen3.6-27b-ovh.toml` (`Qwen3.6-27B`).

## Hors périmètre
`src/slmsp/app/` et l'UI ; poste budgétaire OVH ; appels réels.

## Critères d'acceptation (tests mockés, `tests/evaluation/test_modele_distant.py`)
- Corps Mistral : `random_seed`, pas de `seed`, `top_k`, `provider`, `reasoning`, `usage`, `stream_options` ; URL Mistral ; réservation sur `mistral.generation` ; coût = tarif × usage.
- Corps OVH (registre de test avec poste ovh) : ni graine ni champ OpenRouter, `stream_options` présent, URL OVH.
- Modèle renvoyé différent → `modele_inattendu`.
- OVH sans poste : refus clair, aucune requête, aucune réservation.
- Profil réseau par hôte ; hôte de `sans_reseau` par fiche ; fiches invalides selon le fournisseur refusées.
- Non-régression : tests de 17.1 verts.

## Auto Run Result
- Statut : review. Tests ciblés : `tests/evaluation/test_modele_distant.py` (51) et répertoires net, budget, fournisseurs, inference, evaluation, app/test_modele_externe (1375 verts). Ruff, format et contrôle rapide OK.
- Décisions prises seul :
  - Mistral imputé au sous-poste `mistral.generation` (le poste mistral exige un sous-poste ; `juge` réservé au second juge). **À confirmer par Anaël.**
  - `stream_options.include_usage` envoyé à OVH (champ OpenAI standard, sinon pas d'usage en flux), pas à Mistral (schéma strict, 422 possible ; Mistral renvoie l'usage dans le dernier morceau). À vérifier au premier appel réel : sans usage, l'appel est réglé au pire cas (prudent).
  - `contexte = 262144` pour la fiche OVH, repris de la fiche OpenRouter : ce n'est qu'une borne de l'estimation des tokens d'entrée. À vérifier sur la fiche OVH.
  - `--verifier` des fournisseurs (`eval fournisseurs`) n'inclut pas Mistral ni OVH (registre `FOURNISSEURS` inchangé, solution la plus réversible).
- Reports : poste budgétaire et tarif OVH (approbation d'Anaël) ; reconfirmation du prix Mistral Small sur la page de prix Mistral.

## Revue
- low, corrigé : alias `latest` refusé pour `mistral` et `ovh` (validateur de fiche, test) ; reproductibilité des runs.
- low, rejeté : `top_k` non transmis à Mistral et OVH, sans effet à température 0 (consigné, pas de changement de code).
- low, rejeté : imputation `eval-distant-mistral` → `mistral.generation` conservée sur décision de l'orchestrateur (consigne d'Anaël de passer par l'API Mistral ; dépense estimée ~0,06 €).
- low, corrigé : commentaire de `config/reseau.toml` (cloisonnement par hôte fait par `sans_reseau`).
- low, rejeté : tarif `mistral-small-2603` laissé « à reconfirmer ».
- low, rejeté : `stream_options` OVH vérifié au premier appel réel.
- low, corrigé : `OVH_AI_ENDPOINTS_ACCESS_TOKEN=` ajouté à `.env.example`.
