# Spec : `slmsp bench run --parallele N`

## Objet
`slmsp bench run --parallele N` (défaut 1, comportement inchangé à 1) pour les cibles GGUF :
llama-server `--parallel N` avec `-c = contexte × N` (contexte par requête inchangé),
lm_eval `num_concurrent=N`, bfcl et traduction avec N requêtes en vol, ordre conservé.
Consigné dans `run.json` (`config.parallele`) et, pour chaque résultat GGUF, dans
`details.parallele`.

## Revue
Revue du commit 04d6f40 (Opus, une passe, avec le second avis Haiku).

| Sévérité | Source | Constat | Décision | Motif |
|---|---|---|---|---|
| medium | second avis 1 | `batch_size` valait "1" pour lm_eval GGUF mais `str(N)` pour bfcl et traduction : deux sens pour un même champ | corrigé | `batch_size` revient à "1" (lot d'un appel) ; la concurrence va dans `details.parallele`, posé par l'orchestrateur pour toute cible GGUF (`ConfigurationExecution` n'est pas modifié, pas de changement de schéma) |
| medium | second avis 2 | tests d'ordre de bfcl et traduction muets sur la concurrence : un retour au séquentiel passait | corrigé | tests paramétrés avec compteur d'appels en vol : pic 1 à N=1, 2 à N=2, borné au nombre de questions (3) à N=4 pour bfcl, 4 à N=4 pour la traduction |
| medium | second avis 7 | KV unifié de llama.cpp b11429 | corrigé | `--help` : `-kvu` est « enabled if number of slots is auto » ; avec `--parallel N` explicite le KV est déjà par slot. `--no-kv-unified` est ajouté à N>1 pour figer ce réglage face à un changement de défaut ; ligne de commande identique à N=1 |
| low | second avis 3 | `parallele` consigné dans `run.json` même pour une sélection HF seule | rejeté | `run.json.config` consigne la commande telle que lancée ; `details.parallele` n'est posé que pour les cibles GGUF |
| low | second avis 4 | pas de borne haute sur `--parallele` | rejeté | la limite dépend de la VRAM et du modèle ; llama-server échoue au démarrage s'il ne peut allouer `-c`, avec message |
| low | second avis 5 | `lancer(parallele="4")` lève TypeError | rejeté | API typée `int`, la CLI convertit et valide ; pas d'appelant programmatique hors tests |
| low | second avis 6 | `test_registre_paresseux_n_importe_pas_les_moteurs_reels` dépend de l'ordre des tests | corrigé | pré-existant (reproduit sur 551fa08 avec l'ordre lm_eval, traduction, orchestrateur) ; correctif trivial : contrôle dans un processus neuf |
| low | revue | `tests/cli/test_budget.py` (3) et `tests/budget/test_tarifs.py::test_budgets_de_depart` : 4 échecs | reporté | pré-existants sur 551fa08 (plafonds de `config/budgets.toml` modifiés par la campagne baseline-2026-10-18), sans lien avec la story |
| - | revue | thread-safety du client | vérifié | `ClientLlama` partage un client HTTP (pool de connexions) entre threads, sans état mutable par requête |
| - | revue | Complexité : 0 constat | - | aucune structure qui grossit parcourue à chaque événement ; `appliquer_ordonne` est en O(n) |

Reporté (service réel) : premier bench GPU `--variante-llamacpp cuda --parallele 4` ; vérifier dans
le journal llama-server `n_ctx_slot = <contexte de la fiche>` et des scores égaux à N=1 à la
variance de génération près.
