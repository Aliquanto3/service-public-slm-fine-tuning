---
title: 'Outils SmolLM3 : protocole balises-tool-call côté client (RD à 0,0)'
type: 'bugfix'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** SmolLM3-3B obtient RD 0,0 sur le jeu v1.1 (génération `eval-generation/20261016-193650-smollm3-3b-8a06`, notation `eval-notation/20261016-205054-smollm3-3b-5b25`) et 0/5 à la sonde H-TOOLS. Ses 40 sorties RD contiennent toutes `\n<tool_call>\n{"name": "search_datasets", "arguments": {...}}\n</tool_call>` en texte, parfois suivi d'un résultat inventé. Le template du tokenizer prescrit ce format mais ne lit pas `message.tool_calls`. Depuis la PR #18675, llama.cpp b11429 ne construit donc aucun parseur d'outils, et `natif` ne remonte aucun `delta.tool_calls`.

**Approach:** nouveau protocole `balises-tool-call` dans `ClientLlama`. `tools` est transmis comme en `natif`, et le template HF officiel le rend (AD-13 respecté, aucun template modifié). Un `LecteurBalises` incrémental analyse le flux de texte : le texte hors balises sort en `Jeton` au fil de l'eau (seul un début possible de `<tool_call>` est retenu), et chaque balise donne un `AppelOutil` ou un `AppelNonConforme`. Pour l'historique, `messages_balises` réécrit les `tool_calls` des tours `assistant` en balises dans `content`, sans quoi le template les ferait disparaître. `config/modeles/smollm3-3b.toml` passe à `protocole_outils = "balises-tool-call"`. La sonde 8.2 essaie ce protocole en troisième passe, puisqu'elle parcourt `PROTOCOLES`.

## Boundaries & Constraints

**Always:** les protocoles `natif` et `json-generique` restent inchangés. Une balise non fermée (arrêt ou longueur) est analysée quand même : un JSON complet donne un appel, un JSON coupé donne un `AppelNonConforme` (« non fermée »).

**Never:** aucun `--chat-template-file` modifié (voie (a) écartée, contraire à AD-13). Aucune génération réelle, aucun appel payant. `eval/jeu`, `eval/revue` et `eval/construction` restent intacts.

</intent-contract>

## Code Map

- `src/slmsp/inference/client.py` : `PROTOCOLES`, `LecteurBalises`, `_appel_balise`, `messages_balises`, `ClientLlama._messages`, branche `balises` de `_flux`.
- `src/slmsp/core/schemas/config_modele.py` : `Literal` de `protocole_outils`.
- `config/modeles/smollm3-3b.toml` : protocole et provenance du constat.
- `src/slmsp/evaluation/sonde_outils.py`, `src/slmsp/cli/eval.py` : textes (trois passes).
- Tests : `tests/inference/test_client.py` (flux découpé en 1, 3 et 7 caractères, plusieurs appels, arguments en chaîne, non conformes, balise non fermée, historique réécrit), `tests/evaluation/test_sonde_outils.py` (troisième passe recommandée), `tests/fetch/test_verifications.py`.

## Verification

- Tests ciblés : `uv run pytest -q --tb=short tests/inference/test_client.py tests/evaluation/test_sonde_outils.py`.
- Réel, à lancer plus tard (GPU libre) :
  - sonde 8.2 : `uv run slmsp eval sonde-outils --modele base:smollm3-3b --variante cuda`. Attendu : `balises-tool-call` valide, ou au moins des appels appariés.
  - RD v1.1 : `uv run slmsp eval run --modele base:smollm3-3b --jeu v1.1 --variante cuda --items RD-001,RD-002,RD-003,RD-004,RD-005,RD-006,RD-007,RD-008,RD-009,RD-010,RD-011,RD-012,RD-013,RD-014,RD-015,RD-016,RD-017,RD-018,RD-019,RD-020,RD-021,RD-022,RD-023,RD-024,RD-025,RD-026,RD-027,RD-028,RD-029,RD-030,RD-031,RD-032,RD-033,RD-034,RD-035,RD-036,RD-037,RD-038,RD-039,RD-040 --phase generation`, puis `--phase notation --depuis <run>`.

## Auto Run Result

- Constat (lecture du run, sans regénération) : 40/40 items RD au format `<tool_call>` avec un JSON valide, et 0 `appels_outils` canoniques.
- Décision : voie (b), le parsing côté client (couche `inference`, à côté de `json-generique`), plutôt qu'un template modifié. AD-13 est tenu, la provenance du template reste inchangée, et c'est réversible : il suffit de remettre `natif` dans le TOML.
- La sonde passe désormais jusqu'à trois protocoles : `natif`, puis `json-generique`, puis `balises-tool-call`.
- Entraînement : traité en revue (`core.balises`, voir ci-dessous).

## Revue

Revue Opus du 2026-10-16, après rebase sur `main` (22600ab), avec les constats du second avis (Haiku).

- **medium**, second avis 1 : texte après `</tool_call>` émis et second appel exécuté. **Corrigé.** `LecteurBalises` passe à l'état « après appel » : seuls d'autres appels séparés par des blancs sont lus (le template de SmolLM3 dit « For each function call… », plusieurs appels sont légitimes), et le premier texte non blanc arrête le tour, sans rien émettre ni exécuter. Le client ajoute aussi `</tool_call>` aux `stop` de la requête (avec des `tools`, en fusionnant les `stop` demandés) : llama-server s'arrête au premier appel fermé, la balise est retirée, et `finir` analyse l'appel non fermé (`terminee`). Tests : `test_balises_appel_et_texte` (résultat inventé puis second appel ignorés), `test_balises_mots_d_arret`, `test_balises_arret_serveur`, `test_balises_appels_consecutifs`.
- **medium**, second avis 2 : ordre texte/appel perdu dans `messages_balises`. **Corrigé par construction et documenté** : avec le point 1, un tour `assistant` n'a jamais de texte après ses appels, donc « contenu, puis appels » est l'ordre réel.
- **medium**, second avis 3 : appel tronqué suivi d'un appel valide. **Corrigé.** Un `<tool_call>` rouvert avant `</tool_call>` clôt le premier en `AppelNonConforme` (« balise non fermée avant la suivante »), puis lit le second. Test : `test_balises_appel_tronque_puis_appel_valide`.
- **medium**, second avis 4 : `</tool_call>` dans une chaîne JSON coupe l'appel. **Corrigé côté client** (`_balise_dans_appel` suit guillemets et échappements ; un `<tool_call>` reste reconnu partout, pour le point 3). Test : `test_balises_fermante_dans_une_chaine_json`. Limite : le mot d'arrêt de llama-server coupe, lui, sans tenir compte des chaînes ; un tel argument donnerait un `AppelNonConforme`, cas jugé bien plus rare que le résultat inventé que le `stop` évite.
- **medium**, second avis 5 : `train` ne rendait ni `tools` ni `tool_calls` en `balises-tool-call`. **Corrigé.** `messages_balises` passe dans `core/balises.py` (couche 0, importé par `inference.client` et `train.chargement`) ; `pretokeniser` et `preparer_preferences` réécrivent les messages et transmettent `tools` pour ce protocole. Tests : `test_pretokenisation_balises_garde_les_appels`, `test_preferences_balises_reecrit_les_appels`. Prouvé sur le vrai tokenizer de SmolLM3 (CPU, sans génération) : en `natif`, le tour d'appel supervisé se réduit à `<|im_end|>` ; en `balises-tool-call`, il contient `<tool_call>\n{"name": "chercher", …}\n</tool_call><|im_end|>`, masque accepté.
- **low**, second avis 6 : JSON complet sans `</tool_call>` exécuté sur un flux `interrompue`. **Corrigé.** `finir(raison)` ne l'analyse qu'en `terminee` ou `longueur` ; sinon `AppelNonConforme` (« flux interrompu »). Test : `test_balise_non_fermee_flux_interrompu`.
- **low**, revue : sans `tools`, le lecteur de balises était actif et aurait pu produire des appels. **Corrigé** : lecteur et `stop` seulement avec des `tools`.
- **report**, revue : effet réel du `stop` `</tool_call>` sur le flux. llama-server retient le texte qui pourrait commencer un mot d'arrêt (un `<` ou `</…` en fin de morceau) jusqu'à le lever ; l'effet attendu sur le délai du premier token est nul, l'économie de tokens est celle du résultat inventé. À vérifier avec la sonde 8.2 et le RD v1.1 ci-dessus (GPU libre) : appels appariés, `finish_reason` `stop`, `completion_tokens` en baisse par rapport au run 20261016-193650.
