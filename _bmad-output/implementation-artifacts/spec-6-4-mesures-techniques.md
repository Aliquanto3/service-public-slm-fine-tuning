---
title: 'Story 6.4 — Mesures techniques FR-26 (slmsp measure)'
type: 'feature'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: []
deferred:
  - summary: >-
      Registre des PID absent du dépôt : l'exclusivité repose sur le seul verrou `gpu.lock` (`verrou_gpu`, sans attente, code 5). Une autre commande `slmsp` qui ne prend pas ce verrou (CPU seul) n'est pas détectée.
    evidence: src/slmsp/core/var.py (pas de `pids/`).
    location: src/slmsp/measure/protocole.py `verrou_mesure`
    severity: medium
  - summary: >-
      `--quantification` est seulement consignée dans le run ; le GGUF mesuré est celui de `config/modeles/<slug>.toml`. Les tokens viennent de `Fin.usage` s'il existe, sinon du nombre de `Jeton` (approximation).
    evidence: cli/measure.py, measure/debit.py
    location: src/slmsp/cli/measure.py
    severity: low
---

<intent-contract>

## Intent

**Problem:** NFR-1 à NFR-3 et NFR-6 n'ont aucune mesure reproductible sur l'Assistant complet.

**Approach:** `slmsp measure run --modele base:<slug>` assemble l'Assistant comme `slmsp ask` (`assembler`, variante `cpu`, threads plafonnés), pose `echauffement + repetitions` Questions avec recherche dans l'Index sous un échantillonneur RAM, et écrit `runs/measure/<run_id>/resultat.json` (`ResultatMesure`, slug `h-ram`).

## Boundaries & Constraints

**Always:** `slmsp.measure` ne reçoit que `repondre(question)` et n'importe jamais `slmsp.cli` ; exclusivité par `verrou_gpu` sans attente avant tout démarrage de serveur ; provenance des serveurs par `ServeurLlama.description()` ; questions de `config/mesures.toml`, distinctes du Jeu d'évaluation.

**Never:** aucune mesure réelle lancée, aucun téléchargement, aucun appel d'API ; le rapport rappelle que la machine de développement n'est pas le PC cible.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Verrou tenu | autre commande en cours | refus immédiat | `RessourceOccupee`, code 5 |
| Mesure nominale | N répétitions | RAM max (pic des working sets de l'arbre, 100 ms), débit médian/min, premier token médiane/p95, taille GGUF+Index+binaires, empreinte machine | — |
| Hors seuil | un NFR non tenu | verdict `infirmee`, repli listant les NFR en échec | run `complet` |
| Erreur de génération | `Erreur` ou aucun jeton | `MesureEchouee` | run `partiel-erreur` |
| Modèle mal formé | `--modele granite` | message d'usage | code 2 |

</intent-contract>

## Code Map

- `src/slmsp/measure/{config,ram,debit,taille,protocole}.py` -- seuils/questions, échantillonneur psutil, chronométrage, tailles, orchestration du run.
- `src/slmsp/cli/measure.py` -- `measure run` ; `cli/_assemblage.py` : paramètre `threads` (plafond) et `Assemblage.serveurs`.
- `src/slmsp/core/schemas/mesure.py` -- champs optionnels `conformite`, `environnement`, `avertissement`.
- `config/mesures.toml` -- 5 questions, 10 répétitions + 1 échauffement, 4 threads, 100 ms, seuils NFR.
- `tests/measure/test_ram.py`, `test_debit.py` (protocole sur flux et RAM factices), `test_exclusivite.py`.

## Auto Run Result

Statut : done. Tests ciblés et suite complète verts, ruff propre.

Décisions (à confirmer par Anaël) :
- NFR-3 jugé sur le **p95** du délai au premier token (plus strict que la médiane) ; NFR-2 sur le débit **médian** ; NFR-1 sur le pic ≤ 5 Go (cible 4 Go consignée dans `nfr-1-cible`).
- NFR-6 : taille = GGUF de génération + GGUF d'embedding + Index de la version la plus récente + `vendor/llama.cpp/<tag>/bin-cpu`.
- Plafond de threads 4, 10 répétitions + 1 échauffement : valeurs de départ, non calibrées sur le PC cible.
- Le délai au premier token inclut l'embedding de la requête et la recherche dans l'Index.

Commande réelle à lancer plus tard (verrou libre, modèle et Index présents, `SLMSP_MODELS_DIR`/`SLMSP_VENDOR_DIR` du dépôt principal) :
`uv run slmsp measure run --modele base:granite-4.0-1b [--quantification q4_k_m]`

## Revue

- medium, corrigé : NFR-6 ne comptait que `bin-cpu` ; tous les `bin-*` installés sont maintenant comptés (surestimation prudente si `bin-cuda` est présent).
- medium, corrigé : `--quantification` est refusée (code 2) si le nom du GGUF de génération configuré ne la porte pas ; plus d'étiquette trompeuse.
- medium, consigné (deferred) : `gpu.lock` pris aussi en CPU, mais un `slmsp ask` CPU concurrent qui ne prend pas le verrou n'est pas détecté ; correctif non simple, laissé.
- low, corrigé : débit = (N-1)/durée (N jetons, N-1 intervalles) ; test et horloge factice ajustés.
- low, corrigé : composant à mesurer absent lève `FileNotFoundError` (run `partiel-erreur`) au lieu de compter 0.
- low, consigné : RAM = working set, non USS (surestime légèrement, prudent) ; le pic du chargement du modèle est capté seulement si l'échantillonneur couvre le démarrage (non) ; p95 sur 10 valeurs = quasi le maximum.
- low, consigné : code de sortie 0 si un NFR est infirmé, cohérent avec `index mesurer` ; le verdict est dans le résultat.
- low, corrigé : tests ajoutés pour `_conformite` (bornes, valeurs None), la taille absente et `plafonner_threads` (extrait de `assembler`).
