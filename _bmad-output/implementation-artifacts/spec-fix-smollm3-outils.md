---
title: 'Outils SmolLM3 : protocole balises-tool-call côté client (RD à 0,0)'
type: 'bugfix'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred:
  - 'Entraînement SmolLM3 sur RD : `train.chargement` ne transmet `tools` et ne réécrit les `tool_calls` qu''en protocole `natif` (à confirmer par Anaël).'
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
- Report (à confirmer par Anaël) : le fine-tuning de SmolLM3 sur des exemples RD. `train/chargement.py` ne transmet `tools` qu'en `natif`, et le template ignore `tool_calls`. Il faudrait réutiliser `messages_balises` (et donc le déplacer dans `core`) et transmettre `tools` pour ce protocole. Le code d'entraînement n'est pas touché ici.
