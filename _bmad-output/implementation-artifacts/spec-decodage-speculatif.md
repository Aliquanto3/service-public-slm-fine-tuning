---
title: 'Décodage spéculatif de llama-server mesurable par `slmsp measure run`'
type: 'feature'
created: '2026-10-18'
status: review
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: []
deferred:
  - 'Mesure réelle (MiniCPM5-2B + brouillon MiniCPM5-1B, ngram) : à lancer par l''orchestrateur, hors de cette story.'
---

<intent-contract>

## Intent

**Problem:** Décision d'Anaël du 2026-10-18 : accélérer la génération CPU (MiniCPM5-2B : 16,7 tokens/s) par décodage spéculatif. Rien ne permet de le mesurer.

**Approach:** `ServeurLlama(speculatif=...)` ajoute les options de llama-server b11429 ; `measure run` les expose et consigne la configuration et le taux d'acceptation. La qualité ne change pas (le texte reste celui du modèle cible).

## Boundaries & Constraints

**Always:**
- Défaut : aucun décodage spéculatif, ligne de commande strictement identique, aucun autre appelant modifié.
- Options retenues (noms de `llama-server --help`) :
  - `brouillon` : `-md <gguf>`, `--spec-type draft-simple`, `-ctkd`/`-ctvd` (= `cache_kv` de la cible), `--spec-draft-n-max N` (défaut 3), `-td` (= `threads` de la cible, si défini) ;
  - `ngram` : `--spec-type ngram-simple` seul.
- Brouillon : GGUF de la fiche `config/modeles/<slug>.toml`. Même vocabulaire exigé : SHA-256 de `tokenizer.json` des deux fiches (obligatoire) et `vocab_size` des `config.json` locaux (si présents), sinon `ConfigurationInvalide`.
- Pas d'option de contexte du brouillon dans b11429 (pas de `-cd`) : il suit le contexte de la cible.
- CLI : `--speculatif {aucun,brouillon,ngram}`, `--brouillon <slug>` (implique `brouillon`), `--brouillon-n-max N`. Incohérence : code USAGE.

## Code Map

- `src/slmsp/inference/serveur.py` : `Speculatif`, `verifier_vocabulaire_brouillon`, `ServeurLlama.gguf_brouillon`, `_arguments_speculatifs`, `description()` (clés `speculatif`, `gguf_brouillon` seulement si actif).
- `src/slmsp/inference/client.py` : `timings.draft_n` et `draft_n_accepted` du flux rejoignent `Fin.usage`.
- `src/slmsp/measure/debit.py`, `protocole.py` : lecture, agrégation, consignation.
- `src/slmsp/harness/assemblage.py` : paramètre `speculatif` (seul serveur de génération). `src/slmsp/cli/measure.py` : options, `composants["brouillon"]` (taille installée).
- Tests : `tests/inference/test_speculatif.py` (dont un test `lent` réel, `bin-cpu`), `tests/measure/test_speculatif.py`.

## Taux d'acceptation

Exposé par llama-server b11429 dans `timings` du dernier morceau du flux `/v1/chat/completions` : `draft_n` (proposés) et `draft_n_accepted` (acceptés) ; vérifié par le test réel. `resultat.json` : `valeurs.speculatif_tokens_proposes`, `speculatif_tokens_acceptes`, `speculatif_taux_acceptation` (sommes sur les répétitions mesurées, échauffement exclu) ; `parametres.speculatif` (aussi `run.json` > `config`) ; `details.speculatif` = `taux-expose` ou `taux-non-expose…`. Valeurs plates, car `ResultatMesure.valeurs` n'admet pas de dict imbriqué.

## Auto Run Result

- Statut : done. Le RAM est mesuré tel quel ; la taille installée ajoute le GGUF du brouillon (`tailles_octets.brouillon`).
- Décisions seul : `ngram-simple` (demandé, valeurs par défaut de llama-server) ; `--brouillon-n-max` refusé hors mode `brouillon` ; GGUF du brouillon = celui de la fiche (Q4_K_M), pas de choix de quantification.
- À confirmer par Anaël : `draft-simple` explicite alors que `-md` seul suffit peut-être ; `ngram-mod` / `ngram-map-k` non essayés.
