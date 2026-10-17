---
title: 'Client Mistral : relances bornées sur 429/5xx et délais explicites'
type: 'bugfix'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred:
  - summary: "Pas de test d'intégration generate/seed avec relance réussie (fixtures data et juge en reessais_max = 0) ; couvert au niveau du client."
    location: tests/data/conftest.py
  - summary: "Cause exacte du blocage de deux heures non établie (aucun journal) : l'échéance totale borne désormais chaque tentative, mais un blocage hors HTTP (verrou SQLite, etc.) resterait possible."
---

<intent-contract>

## Intent

**Problem:** Campagne 9.8, run `20261017-014259-generate-101b` : après environ 15 appels, Mistral renvoie un HTTP 429. Le client lève `ErreurApiMistral` sans réessayer et le run passe en `partiel-erreur`. Une reprise est restée bloquée deux heures sans écrire, faute d'échéance totale par appel : un délai `httpx` unique (300 s) se réarme à chaque lecture.

**Approach:** Ajouter dans `ClientMistral` une boucle de tentatives bornée, sur 429, 500, 502, 503, 504 et les erreurs de transport. L'attente suit `Retry-After`, ou à défaut un backoff exponentiel avec gigue. Côté passerelle `net`, un transport impose à chaque requête des délais explicites de connexion et de lecture, ainsi qu'une échéance totale.

## Boundaries & Constraints

**Always :**
- Chaque tentative a sa réservation, réglée avant la suivante : un 429 à 0, une 5xx ou une erreur de transport au pire cas (règle existante). Une réservation n'est donc jamais comptée deux fois.
- Chaque tentative laisse sa ligne au journal Mistral.
- Au-delà des bornes, la même `ErreurApiMistral` est levée (suffixe « après N réessai(s) »), et le pipeline passe en `partiel-erreur`, avec possibilité de reprise.
- Chaque relance est consignée (logger `slmsp.mistral.client` : horodatage, code, réessai, attente, source), sans corps, en-tête ni clé.

**Never :**
- Aucune relance du SDK (`retries=None`) ni du transport (`retries=0`).
- Aucun appel réel.
- Pas de changement de la réutilisation des réponses journalisées : la reprise filtre `statut = ok`.

## I/O & Edge-Case Matrix

| Scénario | Entrée | Comportement |
|---|---|---|
| 429 + `Retry-After: 3` ou date HTTP | 429, 429, 200 | attentes 3 s puis l'écart à la date, succès, 3 réservations (0, 0, coût réel) |
| 429 sans en-tête, toujours | 6 × 429 | attentes 2, 4, 8, 16, 32 s (gigue ∈ [½, 1]), erreur après 5 réessais |
| Attente cumulée dépassée | `Retry-After: 400` ×3, total 600 | 1 réessai puis erreur |
| 5xx passagère | 503, 200 | pire cas puis coût réel |
| Échec définitif | 400, 401, 403, 404, 422, 501 | aucune relance |
| Appel bloqué | `ReadTimeout` (délai total ou de lecture) | transitoire, relancé puis borné |
| Plafond d'une seule réservation | 429 ×3, 200 | succès (réservations libérées une à une) |

</intent-contract>

## Code Map

- `src/slmsp/net/relances.py` (nouveau) : `lire_retry_after` et `erreur_transport` (déplacés de `fetch/hf.py`, qui les réimporte), `statut_transitoire`, `attente_exponentielle`, `DelaisAppel`, `transport_echeance`. Ce transport impose `extensions["timeout"]` et vérifie l'échéance avant les en-têtes et à chaque morceau du corps.
- `src/slmsp/net/client.py` : paramètre `delais_appel`, dans `client()` et dans `Passerelle.client()`.
- `src/slmsp/mistral/config.py`, `config/mistral.toml` : `delai_connexion`, `delai_lecture`, `reessais_max`, `attente_totale_max`, `attente_base`, `attente_plafond`, avec des valeurs par défaut. `delai_appel` devient l'échéance totale.
- `src/slmsp/mistral/client.py` : `_appeler` contient la boucle, `_tentative` l'ancien appel unique, `_attente` les bornes. `dormir` et `alea` sont injectables, et `ErreurApiMistral` gagne `transitoire`, `attente_serveur` et `reessais`.

## Valeurs par défaut

`delai_connexion = 10`, `delai_lecture = 300`, `delai_appel = 300` (total), `reessais_max = 5`, `attente_totale_max = 600`, `attente_base = 2`, `attente_plafond = 60`.

`delai_lecture` reste à 300 s : l'API ne renvoie les en-têtes qu'une fois la génération finie, donc la première lecture couvre toute la génération. Une tentative dure au plus environ `total + lecture`.

## Verification

- `uv run pytest -q tests/mistral tests/net tests/data tests/budget tests/judge tests/fetch` : vert.
- Nouveaux tests : `tests/mistral/test_relances.py` et `tests/net/test_relances.py`.
- Suite complète : 4461 passés, 347 ignorés. Contrôle rapide OK.

## Auto Run Result

- Les tentatives en 5xx ou en erreur de transport restent comptées au pire cas, selon la règle existante. Avec 5 réessais, une panne serveur prolongée peut donc immobiliser jusqu'à 6 pires cas sur le sous-poste. **À confirmer par Anaël** : régler plutôt les 5xx à 0.
- L'attente totale compte le seul temps d'attente entre les tentatives, pas la durée des appels eux-mêmes, que l'échéance totale borne déjà.
- Un `Retry-After` qui ferait dépasser `attente_totale_max` provoque un abandon immédiat, sans attente tronquée.
- Le journal des relances passe par `logging`, sans fichier dédié dans le run. Le journal Mistral garde déjà une ligne par tentative.
- Les fixtures `tests/data` et `tests/judge/test_second.py` passent en `reessais_max = 0`, pour garder leur sémantique d'échec immédiat.
