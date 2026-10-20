---
title: 'Candidats multiples et juge croisé Kimi (story 15.2, O2)'
type: 'feature'
created: '2026-10-20'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: ['{project-root}/_bmad-output/implementation-artifacts/spec-o3-selection.md']
warnings: []
deferred:
  - 'Premier appel réel Kimi K2.6 : vérifier que le schéma JSON strict de O1 (`response_format`) est accepté par le provider OpenRouter (revue : non vérifiable sans appel payant).'
---

<intent-contract>

## Intent

**Problem:** la sélection de cibles (O3) a besoin de plusieurs candidats par entrée, jugés par un juge d'une autre famille que le générateur.

**Approach:** `slmsp data candidats` produit `candidats.jsonl` (Mistral existant, base locale par température, DeepSeek pour LC) ; `slmsp data juger --candidats RUN --juge {deepseek,kimi}` note chaque candidat.

## Boundaries & Constraints

**Always:** contrat de sortie de `spec-o3-selection.md` (aucun texte dans `candidats.jsonl`, texte relu dans son journal) ; conversation d'entraînement exacte pour les candidats locaux et DeepSeek ; sortie tronquée journalisée mais jamais candidate (C2) ; run idempotent et reprenable ; budget OpenRouter réservé avant chaque appel (usage `generateur-openrouter`) ; D1 (aucun texte rédigé).

**Never:** appel payant ou génération réelle en test ; modifier le format de verdict O1 au-delà de l'ajout du champ `juge` ; implémenter la sélection (15.3).

</intent-contract>

## Contrat de sortie (pour 15.3)

`runs/data-candidats/<run_id>/candidats.jsonl`, une ligne par candidat : `session_id`, `candidat_id` (`mistral:<appel_id>`, `slm:<appel_local_id>`, `openrouter:<appel_id>`), `source` (`mistral`, `slm:<slug>`, `openrouter:<modèle>`), `tache`, `temperature`, `graine` (nuls pour Mistral), `cle` (clé de reprise), `rang`. `ecartes.jsonl` : candidats exclus (`tronquee`, `interrompue` avec `finish_reason`, `vide`, `non_texte`, `contexte`, `longueur`) avec `appel_local_id`/`appel_id`. `run.json` : `generate_run_id`, `build_run_id`, `jeu_sft_version`, `base`, `temperatures`, `graine`, `nettoyage` (règle : `version`, `plafond_tokens`, `modele`, `appliquee`), `tokenizer_sha256`.
Texte d'un candidat (jugement et cible de 15.3) : `cible_apprise(texte brut du journal, tache, RegleCible.depuis_config(run.json["nettoyage"]))`, la même fonction pour Mistral, slm et openrouter (vérifié sur le build `20261020-125334-nettoyage-440e` : la cible Mistral ainsi nettoyée égale la cible v18 sur les 103 lignes CR, LC et RE).
Tâches : CR et LC (RE refusée : pas de grille de jugement de données). Juge croisé : `data juger --candidats R --juge kimi` ne note par défaut que les sources `openrouter:deepseek/*` (`SOURCES_JUGE_CROISE`, `--toutes-sources` pour tout noter) ; la règle du minimum des deux juges reste à 15.3.
Verdicts : `runs/data-juger/<run_id>/verdicts.jsonl`, jointure par `(session_id, candidat_id)` ; chaque ligne porte `juge` (identifiant du modèle) ; `run.json` porte `juge_nom` et `origine: candidats`. Un même candidat jugé par deux juges donne deux runs.

## Code Map

- `src/slmsp/data/candidats.py` : `lancer_candidats`, `candidats_depuis_run`, `texte_candidat` (relecture SHA-256 du journal local ou OpenRouter, lecteur `data`).
- `src/slmsp/data/juge_donnees.py` : `lancer_jugement(config_run=…)`, champ `juge` des verdicts.
- `src/slmsp/data/config.py`, `config/donnees.toml` : `[candidats]`, `[juge_donnees.juges.kimi]`, `JugeDonneesConfig.pour_juge`.
- `src/slmsp/core/artefacts.py` : le lecteur `data` lit `generations-locales.sqlite` et `appels-generateur-openrouter.sqlite` (lecture seule, AD-24 ; pris sur le périmètre de 15.3 règle 6 car `data juger` en a besoin).
- `src/slmsp/cli/data.py` : `data candidats`, `data juger --candidats --juge`.
- `config/tarifs.toml`, `config/juges.toml` : entrée `moonshotai/kimi-k2.6` (juge tiers `kimi`, 0,65 / 3,41 $/Mtok, relevé OpenRouter du 20/10).
- `src/slmsp/fournisseurs/journal.py` : `JournalAppels.reussis` (reprise sans second paiement).
- Tests : `tests/data/test_candidats.py`.

## Auto Run Result

- Décisions prises seul : (1) Kimi : remplacé en revue par `moonshotai/kimi-k2.6` (décision de l'orchestrateur) ; pas de `reasoning` envoyé, et le schéma JSON strict de O1 (`response_format`) est à valider au premier appel réel (provider Kimi sur OpenRouter). (2) Accès `data` aux deux journaux ajouté ici (avancé de 15.3). (3) Défaut `--variante cuda` (qualité des candidats). (4) Aucune génération DeepSeek si la ligne a des outils (LC n'en a pas).
- Reports : RE et texte jugé tranchés en revue (voir `## Revue`).

## Commandes du run réel (orchestrateur)

```
slmsp data candidats --build 20261020-125334-nettoyage-440e --base minicpm5-2b --temperatures 0.3,0.7 --taches CR,LC --deepseek-taches LC --plafond-estime 2
slmsp data juger --candidats <RUN_CANDIDATS> --juge deepseek --taches CR,LC --plafond-estime 5
slmsp data juger --candidats <RUN_CANDIDATS> --juge kimi --taches CR,LC --plafond-estime 1
```
Reprise : `slmsp data candidats --reprendre <RUN_CANDIDATS>` (réglages relus du run) ; `slmsp data juger --reprendre <RUN_JUGER>`.
Le build v18 n'a que 5 lignes LC (64 CR) : 5 appels DeepSeek au plus.

## Revue

Revue Opus du 2026-10-20 sur 7fe729a (base en retard sur main, 15.1 fusionnée sans conflit d'après merge-tree, non rebasée sur consigne).

| Sévérité | Source | Constat | Suite |
|---|---|---|---|
| high | second avis 1 | Exception dans la boucle de consommation OpenRouter : le pool attendait toute la file (appels payés, journalisés, non écrits) et la reprise les repayait. | Corrigé : écriture dès l'arrivée (`as_completed`), annulation des appels non lancés sur toute exception, reprise qui relit dans le journal un appel `ok` de même SHA de requête (`JournalAppels.reussis`) sans le repayer ; test `test_interruption_annule_les_appels_en_file_et_reprise_sans_repayer` (6 requêtes payées une fois chacune). |
| medium | second avis 2 | Texte jugé différent du texte appris (cible Mistral brute du journal, candidats slm et openrouter non nettoyés, pas de plafond). | Corrigé : `cible_apprise` (règle du build `nettoyage`, sinon règle courante) pour toutes les sources, avant écriture (motifs `vide`, `longueur`, tokenizer réel) et au jugement ; prouvé sur le build réel 440e. |
| medium | second avis 3 | Aucun garde de famille : `--juge kimi` notait tout. | Corrigé : sources `openrouter:deepseek/*` par défaut, `--toutes-sources` sinon, filtre consigné dans `run.json` (`sources`) et relu à la reprise. |
| medium | second avis 4 | `--reprendre` ne relisait pas base, températures, `deepseek_taches`. | Corrigé : CLI relit les réglages du run ; `lancer_candidats` refuse toute divergence (build, Tâches, base, températures, graine, max_tokens, réglages OpenRouter, règle de nettoyage, SHA du tokenizer). |
| low | second avis 5 | Seul `length` était écarté ; `content_filter`, `error`, vide passaient. | Corrigé : tout `finish_reason` autre que `stop` est écarté (`interrompue`, `finish_reason` consigné). |
| low | second avis 6 | `etat["cout"]` ignorait le coût des appels échoués. | Corrigé : `ErreurApiFournisseur.cout_eur` ajouté (dernière tentative seulement, limite du client). |
| low | second avis 7 | Kimi provisoire `moonshotai/kimi-k2` 1,0/3,0. | Corrigé : `moonshotai/kimi-k2.6`, 0,65 / 3,41 $/Mtok. |
| medium | second avis 8 | RE produisait des candidats non jugeables. | Corrigé : RE refusée (CLI et `lancer_candidats`) avec message clair ; défaut CR, LC. |
| low | revue | Run réel : 5 lignes LC seulement dans v18 ; l'estimation et le gain DeepSeek sont minces. | Signalé à l'orchestrateur, sans correctif. |
| — | revue | Complexité : 0 constat (relecture du journal OpenRouter une fois par reprise, ensembles de clés en O(1), aucun parcours complet par événement). | — |

