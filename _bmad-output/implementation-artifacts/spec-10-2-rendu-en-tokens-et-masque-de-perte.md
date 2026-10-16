---
title: 'Story 10.2 — Rendu en tokens et masque de perte (H-MASQUE)'
type: 'feature'
created: '2026-10-13'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-10-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: []
deferred:
  - summary: 'Variante d''entraînement du template (balises `generation`) non produite'
    evidence: 'critère 2 : à produire seulement si le test lent échoue pour un candidat ; les tokenizers réels n''ont pas pu tourner (extra `train` absent)'
---

<intent-contract>

## Intent

**Problem:** tous les Runs d'une campagne doivent apprendre exactement sur les tours `assistant`, avec le même rendu qu'à l'inférence (FR-34, H-MASQUE), sans `assistant_only_loss` de TRL (pas de balises `generation` dans Granite ni Ministral).

**Approach:** `train/rendu.py` rend par `tokenizer.apply_chat_template` officiel avec les `chat_template_kwargs` de `ConfigModele` ; `train/masque.py` calcule les intervalles de caractères des tours `assistant` par rendu incrémental, tokenise avec les offsets et met −100 hors de ces tours.

## Boundaries & Constraints

**Always:** `transformers` importé seulement dans `charger_tokenizer` ; dossier du tokenizer validé par `chemin_autorise(..., "train")` ; `tools` et `chat_template_kwargs` transmis à chaque rendu (prefixes compris) ; refus (`ErreurMasque`) plutôt que masque approximatif.

**Never:** aucune donnée d'entraînement (fixtures factices `<réponse-factice-1>`) ; pas de modification de `cli/train.py`, `config/` ni de `sprint-status.yaml` ; pas de lancement de `llama-server` dans la suite par défaut.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Conversation avec `tool_calls` et messages `tool` | tokenizer factice ou réel | tokens non masqués = tours `assistant` du rendu (contenu, appels sérialisés, fin de tour) ; reste à −100 | — |
| Aucun tour `assistant` | user seulement | tous les labels à −100 | — |
| Template qui réécrit l'historique | rendu partiel non préfixe du rendu complet | — | `ErreurMasque` (variante `generation` requise) |
| Token à cheval sur une frontière de tour | tokenizer qui colle balise et texte | — | `ErreurMasque` |
| Tour `assistant` sans texte | rendu incrémental identique à l'amorce | — | `ErreurMasque` |

</intent-contract>

## Code Map

- `src/slmsp/train/rendu.py` -- `apply_chat_template`, `kwargs_template`, `charger_tokenizer`.
- `src/slmsp/train/masque.py` -- `intervalles_assistant`, `calculer_masque` (`RenduMasque`), `texte_non_masque`, `IGNORE`, `VERSION_MASQUE`, `ErreurMasque`.
- `tests/train/test_masque.py` -- 7 tests unitaires (tokenizer factice, conversations aléatoires à graine fixe) ; tests `lent` : 4 candidats réels (`importorskip("transformers")`, sautés sans `tokenizer_config.json`), égalité avec `/apply-template` de `llama-server --jinja` (Granite, SmolLM3 ; sauté sans GGUF).

## Tasks & Acceptance

**Execution:**
- `src/slmsp/train/rendu.py`, `src/slmsp/train/masque.py` -- implémentation ci-dessus.
- `tests/train/test_masque.py` -- unitaires et lents.

**Acceptance Criteria:**
- Given une conversation multi-tours avec `tool_calls` et messages `tool`, when on calcule le masque, then les tokens non masqués décodés égalent les tours `assistant` du rendu et le reste vaut −100 (vérifié sur tokenizer factice ; sur tokenizers réels en `lent`).
- Given chaque candidat, when le test lent tourne, then le résultat est affiché (`H-MASQUE <slug> : ok`) ou le test échoue avec la cause (critère 2 : à consigner).
- Given le rendu d'entraînement, when on le compare à `/apply-template` de `llama-server --jinja` (`lent`), then les textes sont identiques.

## Spec Change Log

## Review Triage Log

## Design Notes

Le tour `assistant` va de la fin du rendu `messages[:k]` avec amorce de génération à la fin du rendu `messages[:k+1]`, soit ce que le template écrit après la balise de fin de tour (souvent un saut de ligne) : décision la plus simple, réversible dans `intervalles_assistant`. Chaque rendu incrémental doit être un préfixe du rendu complet : les templates qui retirent le raisonnement des tours passés (Qwen) lèvent `ErreurMasque` plutôt que de produire un masque décalé.

## Verification

**Commands:**
- `uv run pytest -q tests/train/test_masque.py` -- expected: 7 verts.
- `uv run pytest -m lent tests/train/test_masque.py` (avec `uv sync --extra train`, `SLMSP_MODELS_DIR`, `SLMSP_VENDOR_DIR`) -- à lancer plus tard.

## Auto Run Result

**Statut : review.** Code seul, sans API ni GPU ; les tests lents n'ont pas tourné (extra `train` absent).

**Reports :**
- Critère 2 : résultats par candidat non consignés (tokenizers réels non exécutés). Si un candidat échoue (Qwen probable à cause du retrait du raisonnement), produire la variante de template limitée aux balises `generation` et la prouver par égalité de rendu. Commande : `uv run pytest -m lent tests/train/test_masque.py -s`.
- Critère 3 : test écrit (`test_rendu_identique_a_llama_server_jinja`), non exécuté.
- Intégration de `VERSION_MASQUE` dans `run.json` : story 10.4.

**Décisions prises seul :** fin de tour = jusqu'à la fin du rendu incrémental (saut de ligne final inclus) ; refus plutôt que repli silencieux ; `tools` non transmis avec `json-generique` laissé à l'appelant (10.4). Aucune décision de fond à confirmer par Anaël.

## Revue

Edge Case Hunter, une passe, commit `b3f225e`. Aucun constat high ni medium.

- low, rejeté : conversation sans tour `assistant` ou `tool_calls` vides, couverts (tout à −100 ; template rendu tel quel, `tools=[]` normalisé en `None`).
- low, rejeté : token à cheval sur une frontière de tour et rendu non préfixe, refusés par `ErreurMasque` (tests présents) ; refus plutôt que masque approximatif, conforme à la spec.
- low, rejeté : tokens d'offset nul (spéciaux sans position) tombent à −100 hors tour ; sans effet sur les templates visés, à revérifier avec les tests `lent`.
- low, rejeté : critères 2 et 3 non exécutés faute de l'extra `train` ; déjà consigné dans le Auto Run Result.
- Règles du projet vérifiées : aucune donnée générée (D1), `transformers` importé dans `charger_tokenizer` seulement, `train` n'importe pas `measure`.

### Seconde passe (second avis Haiku, vérifié par le reviewer Sonnet)

- medium, corrigé : conversation commençant par `assistant` (`masque.py`, `debut = 0` si k = 0) : le préambule injecté par le template (system par défaut) entrait dans le tour non masqué. L'amorce est désormais toujours calculée par rendu de `messages[:k]` (liste vide comprise) ; un template qui échoue ou dont le rendu complet ne commence pas par l'amorce lève `ErreurMasque`. Tests ajoutés.
- medium, consigné (non corrigeable sans réseau ni extra `train`) : critères 2 et 3 non prouvés. À lancer plus tard : `uv sync --extra train` puis `SLMSP_MODELS_DIR=<dossier> SLMSP_VENDOR_DIR=<dossier> uv run pytest -m lent tests/train/test_masque.py -s -q`. Aucun téléchargement fait ici.
- low, corrigé : l'amorce est maintenant vérifiée comme préfixe exact du texte complet (`texte.startswith(amorce)`), pas seulement par sa longueur.
- low, corrigé : tokenizer lent sans offsets (NotImplementedError, KeyError, ValueError) : `ErreurMasque` explicite.
- low, consigné pour 10.4 : pas de troncature (longueur maximale) dans le masque ; à traiter avec la longueur de séquence en 10.4.
