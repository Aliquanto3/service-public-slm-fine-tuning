---
title: 'Décodage spéculatif de llama-server mesurable par `slmsp measure run`'
type: 'feature'
created: '2026-10-18'
status: done
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

## Échantillonnage de la mesure

`measure run` n'envoie aucune option d'échantillonnage : le serveur applique ses défauts (température 0,8, top-k 40, top-p 0,95, min-p 0,05, graine aléatoire), avec ou sans décodage spéculatif. Le débit spéculatif est donc comparé **à méthode identique** à la mesure de référence (`aucun`), qui reste comparable aux mesures déjà faites. Le spéculatif de llama.cpp conserve la distribution de la cible ; les sorties diffèrent d'un run à l'autre dans les deux cas, et le taux d'acceptation consigné (plus bas qu'à température 0) dit ce que le brouillon apporte dans les conditions réelles de service. Forcer la température 0 en spéculatif seulement aurait mesuré une autre méthode que la référence.

## Revue

Revue Opus du 2026-10-18 sur 437ee38 (main non avancé : pas de rebase).

- low, second avis 1 : corrigé. `_speculatif` vérifie la fiche et le vocabulaire du brouillon avant l'assemblage, ce qui donne le code USAGE (tests `test_cli_vocabulaire_different_sort_en_usage`, `test_cli_fiche_du_brouillon_absente_sort_en_usage`).
- low, second avis 2 : corrigé, avec une précision. Mesuré sur le vrai llama-server b11429 CPU, `ngram-simple` n'a renvoyé aucun `draft_n` (25 et 111 tokens, sortie répétitive, température 0) : le serveur omet le champ quand aucun token n'est proposé. Le détail devient « taux-non-expose (… aucun token proposé, ou serveur qui ne l'expose pas) », et « taux-expose, aucun token propose » quand `draft_n` vaut 0.
- medium, second avis 3 : corrigé. `mesurer_question(exiger_usage=True)` en spéculatif refuse le repli sur le nombre de morceaux (`MesureEchouee`) ; la référence garde l'approximation consignée. Constat réel, mais l'écart observé est faible : 24 morceaux pour 25 `completion_tokens`, car llama-server envoie un morceau par token accepté.
- medium, second avis 4 : traité par la documentation (section Échantillonnage), sans changer la méthode de la référence. Motif : méthode identique, taux consigné.
- low, second avis 5 : corrigé. `ServeurLlama` refuse le spéculatif hors variante `cpu` (VRAM du brouillon non budgétée).
- info, second avis 6 : confirmé, sans défaut. Seul `measure run` passe `speculatif` à `assembler`.
- info, second avis 7 : vérifié. `test_reel_demarrage_avec_brouillon` passe sur `bin-cpu` (MiniCPM5-2B + 1B, `draft_n` 20, 20 acceptés), et `--spec-type ngram-simple` est accepté par le serveur.
- Complexité : aucun constat (agrégation linéaire, une seule fois en fin de mesure).
- Reporté : `ngram-simple` ne propose rien dans nos essais courts. Il faut voir à la mesure réelle si le débit ngram diffère de `aucun`, sinon essayer `ngram-mod` ou `ngram-map-k`.
