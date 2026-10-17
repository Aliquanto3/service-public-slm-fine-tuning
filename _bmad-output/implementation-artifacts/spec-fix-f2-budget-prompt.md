---
title: 'Harnais : budget de prompt, erreur de contexte dédiée et max_tokens par défaut'
type: 'bugfix'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred:
  - summary: "Pas de test dédié du budget sur la Recherche de données (RD) : `_messages_index` appelle la même `borner_passages`, couverte par les tests de Q."
    location: src/slmsp/harness/taches/recherche.py
  - summary: "La mesure ne consigne pas le nombre de passages retenus : à `--contexte 2048`, la Question mesurée peut porter moins de 5 passages (journal INFO seulement)."
    location: src/slmsp/measure/protocole.py
  - summary: "Pour un modèle à raisonnement (`reasoning_content`), le raisonnement consomme le même `max_tokens` : 1024 peut couper la réponse si le raisonnement n'est pas désactivé par le chat template."
  - summary: "`taille_contexte` vaut le contexte du serveur (`--ctx-size`) ; avec plusieurs slots (`--parallel` > 1), le contexte par slot serait plus petit. Non traité (un slot en v1)."
---

<intent-contract>

## Intent

**Problem:** Mesure du 2026-10-17 (`slmsp measure run --contexte 2048`) : granite-4.0-1b échoue dès la première question. Le prompt de Q (système + 5 passages) fait 1668 tokens et la sortie n'a plus de place ; aucun garde-fou ne borne les passages. Le HTTP 400 de llama-server est masqué en `erreur-interne`, donc `est_erreur_de_contexte` ne se déclenche pas, et la cause part dans un logger non configuré en CLI. Enfin, aucune `max_tokens` n'est posée hors CR : MiniCPM5-1B produit jusqu'à 2428 tokens.

**Approach:** Le Harnais réserve une sortie (`max_tokens`, par défaut en config) et mesure le prompt complet par `LlmPort.compter_tokens` (déjà `/apply-template` + `/tokenize`). Il retire les passages les moins bien classés jusqu'à tenir. Un dépassement de contexte, qu'il vienne du budget ou du serveur, devient `ContexteDepasse`, rendue en `Erreur(contexte-depasse)`.

## Boundaries & Constraints

**Always :**
- Contexte connu (`llm.taille_contexte`) : budget = `taille_contexte − max_tokens effectif` ; la mesure porte sur les messages envoyés (système, historique, passages, entrée).
- Éviction : on retire les passages un à un, en partant de la fin, la recherche les rendant par score décroissant. La numérotation `[n]` et les `Sources` suivent la liste retenue.
- En dernier recours, si aucun passage complet ne tient mais que le prompt sans passage tient, le premier passage est tronqué à une frontière de mot, suivi de « […] ». On fait au plus 4 mesures ; à défaut, aucun passage n'est fourni.
- Si même le prompt sans passage ne tient pas, `ContexteDepasse` est levée et le serveur n'est pas appelé.
- Sans `max_tokens` de l'appelant, le service en pose un : `compte_rendu.reserve_sortie_tokens` (1024) pour CR, et `generation.max_tokens` (1024) pour toutes les autres Tâches. Un `max_tokens` explicite (évaluation, bancs) est conservé.
- `Erreur(contexte-depasse)` est journalisée en WARNING, sans pile, avec les textes saisis masqués. Les autres exceptions restent `erreur-interne`, journalisées en ERROR avec la pile.
- La CLI ajoute au logger `slmsp.harness` un gestionnaire WARNING sur le `sys.stderr` courant, une seule fois, sans toucher au logger racine.

**Never :** On ne tronque pas l'entrée de l'utilisateur ni l'historique. Aucune estimation des tokens : le serveur compte. On ne modifie ni `inference/serveur.py` ni `inference/embedding.py`.

## I/O & Edge-Case Matrix

| Scénario | Entrée / état | Comportement attendu |
|---|---|---|
| Tout tient (4096/8192) | prompt + 1024 ≤ contexte | Messages identiques à avant ; une seule mesure |
| Contexte inconnu | `taille_contexte` absent | Aucune mesure, passages inchangés |
| Contexte serré | 5 passages ne tiennent pas | Passages 4 et 5 retirés, ou plus si nécessaire |
| Aucun passage complet | seul le prompt nu tient | Passage 1 tronqué, terminé par « […] » |
| Prompt nu trop long | historique ou entrée trop longs | `Erreur(contexte-depasse)`, aucun appel de génération |
| Refus du serveur | HTTP 400 `exceed_context_size_error`, ou erreur en flux | `ContexteServeurDepasse` → `Erreur(contexte-depasse)` |
| Mesure | `Erreur(contexte-depasse)` avec `--contexte` | `ContexteInsuffisant` (« augmenter --contexte ») |

</intent-contract>

## Code Map

- `src/slmsp/core/erreurs.py` : `ContexteDepasse(SlmspError)`.
- `src/slmsp/inference/client.py` : `ContexteServeurDepasse(ErreurInference, ContexteDepasse)` et `est_depassement_contexte`, qui reconnaît `exceed_context_size` ou `context size`. Elle est levée sur un HTTP non-200 et sur une erreur en flux de `/v1/chat/completions`.
- `src/slmsp/harness/budget.py` (nouveau) : `reserve_sortie`, `budget_prompt`, `borner_passages`.
- `src/slmsp/harness/taches/question.py` et `recherche.py` (`_messages_index`) : passages bornés.
- `src/slmsp/harness/service.py` : `max_tokens` par défaut, `CODE_CONTEXTE` et `MESSAGE_CONTEXTE`, et le `except ContexteDepasse`.
- `src/slmsp/harness/config.py` et `config/harnais.toml` : section `[generation]`, avec `max_tokens = 1024`. Elle est facultative.
- `src/slmsp/measure/protocole.py` : `est_erreur_de_contexte` reconnaît `contexte-depasse` ; la docstring de `_verifier_contexte` est mise à jour.
- `src/slmsp/cli/__init__.py` : `_journal_harnais()`.

## Valeurs par défaut

- **`generation.max_tokens = 1024`** : environ 700 mots en français, soit plusieurs paragraphes. C'est assez pour une réponse administrative, qui en compte trois ou quatre. C'est aussi la valeur de l'évaluation (`config/evaluation.toml`) et de la réserve de CR : la réponse en production a le même plafond que la réponse notée. Les sorties de 2428 tokens de MiniCPM5-1B sont coupées (`Fin.raison = "longueur"`). À contexte 2048, le prompt de Q dispose de 1024 tokens, soit environ 3 passages sur 5 pour granite.
- **Message** de `contexte-depasse` : « La demande est trop longue pour le modèle. Raccourcissez le texte ou commencez une nouvelle conversation. Votre texte est conservé. »

## Verification

- `uv run pytest -q --tb=short tests/harness tests/measure tests/inference tests/cli tests/app -m "not ui"` : 728 passés.
- Nouveaux tests :
  - `tests/harness/test_budget.py` (7) ;
  - `tests/inference/test_client.py` : dépassement en HTTP 400 et en flux, plus l'heuristique ;
  - `tests/measure/test_contexte.py` (2) ;
  - `tests/cli/test_journal_harnais.py` ;
  - `tests/harness/test_service.py` : `max_tokens` par défaut, pour CR et pour une valeur explicite.
- Suite complète : 4620 passés, 347 ignorés ; ruff et `outils/controle_rapide.py` OK.
- À lancer plus tard, sur CPU : `slmsp measure run --modele base:granite-4.0-1b --contexte 2048`.

## Auto Run Result

- La troncature d'un passage est implémentée, mais seulement en dernier recours : un passage tronqué vaut mieux que zéro passage quand le contexte est très serré.
- Le `max_tokens` par défaut est posé dans le service (point unique) et pour toutes les Tâches hors CR, y compris RE, CT et TR. Une traduction ou une rédaction longue peut désormais s'arrêter en `longueur` à 1024 tokens. **À confirmer par Anaël** : un plafond par Tâche (par exemple plus haut pour TR) reste possible.
- `_verifier_contexte` est inchangée. Le budget garantit `prompt + réponse ≤ contexte`, et le cas d'égalité, ambigu, reste refusé, ce qui est prudent.
- `est_erreur_de_contexte` garde son repli sur la sous-chaîne `context`, pour les textes bruts du serveur.
- Le budget ajoute une mesure, soit deux requêtes locales `/apply-template` et `/tokenize`, avant chaque Q et chaque RD sur l'Index quand le contexte est connu. Le surcoût est de quelques millisecondes, et il entre dans le délai au premier token mesuré.
