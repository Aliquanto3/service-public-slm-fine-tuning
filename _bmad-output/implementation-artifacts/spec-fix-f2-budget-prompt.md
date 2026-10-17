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

## Revue

Revue du commit 6ff7c4e (Opus, avec la liste du second avis Haiku). La spec n'avait pas changé sur disque depuis le commit (arbre propre, même horodatage) : rien à intégrer.

- **medium, corrigé (1).** Les résultats d'outils MCP n'étaient pas bornés. `budget.borner_resultats` les mesure maintenant avec le schéma `tools`, avant le tour suivant de la RD. Chaque résultat est tronqué en proportion, puis remplacé par « […] » si cela ne suffit pas. `ContexteDepasse` est levée si même alors le prompt dépasse. Le comptage des `tools` dans `_messages_index` est sans objet : ces messages partent toujours sans `tools`. Le premier tour connecté n'est pas mesuré, et un dépassement y est rendu par le refus du serveur (`ContexteServeurDepasse`).
- **medium, corrigé (2).** `mesurer(max_tokens=…)` consigne `parametres.max_tokens`, et la CLI passe `service.max_tokens_par_defaut(fiche)`. Les runs `h-ram` d'après F2 sont plafonnés à 1024 tokens de sortie. Leur débit et leurs tokens ne se comparent pas aux runs antérieurs, qui n'avaient pas de plafond. **Décision d'Anaël attendue** : soit on accepte la rupture et on remesure les modèles retenus, soit la mesure passe un `max_tokens` explicite.
- **medium, corrigé (3).** Ajouts à `[generation]` :
  - `par_tache`, un plafond fixe par code, prioritaire ;
  - `reecriture = ["CO", "TR"]`, avec `facteur_reecriture = 1.5` et `marge_reecriture = 256`.
  
  Pour CO et TR, `redaction` pose `max(max_tokens, ceil(1,5 × prompt mesuré) + 256)`, borné par `contexte − prompt`. On lève `ContexteDepasse` si le prompt remplit déjà le contexte. Le prompt mesuré majore l'entrée. Si la mesure échoue, la valeur retombe sur 1024. Les autres Tâches (Q, RD, RE, CT, NR, LC) gardent 1024, et CR garde sa réserve.
- **low, corrigé (4).** Le dépassement de contexte n'est plus reconnu que par `error.type == "exceed_context_size_error"`. Quand l'erreur n'a pas de `type`, le message précis « exceeds the available context size » est aussi reconnu. L'objet `error` est lu dans le corps HTTP (JSON) et dans le flux. La sous-chaîne « context size » ne suffit plus, et un autre `type` n'est jamais reconnu. La docstring de `TAILLE_EXTRAIT`, mal placée, est corrigée.
- **low, corrigé (5).** `budget_prompt` lève `ContexteDepasse` avec un message explicite (« max_tokens N laisse B tokens au prompt… ») quand la sortie réservée laisse moins de `BUDGET_MIN = 64` tokens au prompt. Aucune mesure n'est alors faite.
- **low, rejeté pour l'algorithme, documenté (6).** Le retrait linéaire est conservé. Pour 5 passages dont 1 ou 2 à retirer, il fait 2 ou 3 mesures, contre 3 ou 4 pour une dichotomie. Une estimation suivie d'une vérification coûterait 3 mesures. Chaque mesure est locale et prend quelques ms. La docstring de `budget` et celle de `mesurer` indiquent que le délai au premier token inclut ces mesures.
- **low, corrigé (7).** Si `compter_tokens` échoue, on revient au comportement d'avant F2 : passages ou résultats envoyés sans budget. Un avertissement est journalisé avec la classe de l'exception, sans son message, qui pourrait citer le prompt.
- **low, documenté (8).** Modèles à raisonnement : le raisonnement consomme le même `max_tokens`. Le point est déjà consigné dans `deferred`, et rien n'est changé.
- **Tests ajoutés.** Dans `tests/harness/test_budget.py` (9) :
  - repli de la mesure ;
  - `max_tokens` trop grand ;
  - nombre de mesures ;
  - réécriture proportionnelle, puis courte, puis bornée par le contexte ;
  - `par_tache` ;
  - `borner_resultats` ;
  - boucle RD avec troncature du résultat.

  Ailleurs : `tests/inference/test_client.py` (cas stricts et HTTP 400 d'un autre type) et `tests/measure/test_contexte.py` (consignation de `max_tokens` par l'API et par la CLI).
- **Vérification de bout en bout (9).** llama-server CPU, granite-4.0-1b q4_k_m, `--contexte 2048`, run `20261017-122434-h-ram-abe4` sous la racine principale. Les répétitions sont réduites à 3 dans un `config/mesures.toml` temporaire, non commité, car l'option n'est pas exposée et l'outil limite une commande à 10 min ; l'échauffement est resté à 1.
  - Résultat : aucun plantage, verdict `confirmee`, `verification_contexte = verifie`.
  - Valeurs : RAM max 2,94 Go, débit médian 33,3 tok/s (minimum 31,1), premier token médian 2,89 s (p95 3,20 s), tokens par répétition [311, 37, 172].
  - **Éviction : 1 passage sur 5** à chaque Question (budget 1024). C'est moins que les 3 passages estimés plus haut. À 2048, réserver 1024 tokens à la sortie laisse un seul passage. Si Anaël veut mesurer avec plus de passages, il faudra un `max_tokens` plus bas à contexte 2048.
