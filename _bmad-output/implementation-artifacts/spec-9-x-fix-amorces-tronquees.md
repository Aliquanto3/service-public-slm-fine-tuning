---
title: 'Amorces issues de réponses tronquées : seed et validate'
type: 'bugfix'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred:
  - summary: "max_tokens du gabarit scenario-reunion (1500) trop bas : les 240 scénarios du seed 20261017-060802-seed-fedd sont tous en finish_reason=length (moyenne 5867 caractères). Décision de budget, valeur inchangée."
---

<intent-contract>

## Intent

**Problem:** le seed fabriquait des amorces CR depuis des réponses Mistral tronquées (`length`), et validate ne revérifiait pas leur provenance ; `build` refusait ensuite ces sessions.

**Approach:** le seed écarte et compte tout scénario tronqué ; validate rejette (`amorce_tronquee`) une session dont une amorce `mistral` ne passe pas `extraire_contenu`, l'extracteur de build.

## Boundaries & Constraints

**Always:** une seule logique d'extraction (`data.extraction.extraire_contenu`) pour build et validate.

**Never:** modifier `max_tokens`, `eval/`, les données de `runs/`.

</intent-contract>

## Auto Run Result

- `core.erreurs.ReponseTronquee` (sous-classe de `ProvenanceInvalide`) levée par la fabrique CLI ; `seed._scenarios` la capte, incrémente `scenarios.tronques` (comptes.json, sortie CLI).
- `LecteurGeneration.controler_provenance_amorces`, appelé en tête de `valider_session` ; nouveau motif `amorce_tronquee` dans `MotifValidation` (couvre aussi un appel introuvable du journal).
- Tests : seed (scénario `length` écarté), validate (amorce tronquée rejetée, amorce saine inchangée), fabrique CLI.
- Les 74 sessions CR du filter 20261017-102523-filter-accf sont toutes concernées : validate, à relancer, les rejettera.
- À confirmer par Anaël : relever `max_tokens` de `scenario-reunion` (budget), puis refaire seed, generate, validate.

## Revue

- medium | corrigé | Réponse de session tronquée non rejetée par validate alors que build la refuse : `controler_provenance` passe chaque appel de la session à `extraire_message`, motif `reponse_tronquee` (défense en profondeur : generate abandonne déjà ces sessions).
- low | corrigé | Validate ne vérifiait ni `usage = generation`, ni `statut = ok`, ni SHA et texte des amorces : règles factorisées dans `LecteurGeneration.appel_generation` et `amorce_verifiee`, appelées par build (`_appel`, `_amorce`) et validate ; gabarit non journalisé contrôlé aussi.
- low | corrigé | Amorce ou appel introuvable : session rejetée (`amorce_invalide`, `appel_invalide`) au lieu d'un run `partiel-erreur`.
- low | corrigé | Libellé `amorce_tronquee` trop large : `ReponseTronquee` levée par `extraire_message` (comportement et `VERSION_EXTRACTEUR` inchangés) ; `amorce_tronquee` pour `length` seul, `amorce_invalide` pour le reste.
- low | corrigé | Courrier CT tronqué compté `schema_invalide` (et un JSON complet tronqué aurait été admis) : la fabrique CT lève `ReponseTronquee`, journalisée ou non ; seed compte `courriers.tronques`.
- low | écarté | Réutilisation de `reponse_journalisee` pour les scénarios : leur `session_id` contient le `run_id` du seed, donc aucune reprise possible sans changer l'identité des sessions ; gain nul, risque de reprendre une réponse tronquée.
- Reste hors champ : les refus de build non liés à la provenance (entrée refusée par la Tâche, conversation invalide, licence) ne sont pas rejoués par validate.
