---
title: Contrôle de préparation à l'implémentation (J1 à J3)
date: 2026-10-12
mode: headless (run autonome de nuit, phase A.3, `bmad-sprint-planning`)
verdict: CONCERNS (prêt avec réserves)
---

# Contrôle de préparation à l'implémentation

## Verdict

**Prêt avec réserves (CONCERNS).** Sept constats bloquants ont été trouvés dans `epics.md`. Tous ont été corrigés à la marge, par des dépendances, des listes de fichiers et un critère d'acceptation. Les réserves restantes ne bloquent pas le développement : ce sont des décisions déjà consignées que doit valider Anaël, et des points d'outillage. Le fichier `_bmad-output/implementation-artifacts/sprint-status.yaml` a été généré.

## Inventaire

| Artefact | Chemin | État |
|---|---|---|
| Décisions (fait autorité) | `planning-artifacts/decisions.md` | final |
| PRD + addendum | `planning-artifacts/prds/prd-service-public-slm-fine-tuning-2026-10-11/` | final |
| UX (DESIGN, EXPERIENCE) | `planning-artifacts/ux-designs/ux-service-public-slm-fine-tuning-2026-10-11/` | J4 et J5 seulement |
| Architecture (AD-1 à AD-29) | `planning-artifacts/architecture/.../ARCHITECTURE-SPINE.md` | final, après 5 relectures |
| Epics et stories | `planning-artifacts/epics.md` | 13 epics, 53 stories (Epics 1 à 11), vagues V0 à V19 |
| SPEC du jeu, grille, calibrage | `eval/` | référencés, non modifiés |
| Journal de la nuit | `implementation-artifacts/journal-decisions-nuit.md` | D-nuit-1, A1-1 à A1-25, A2-1 à A2-22 |

## Traçabilité

- **FR → stories.** Les 40 FR sont rattachées (carte de couverture d'`epics.md`). FR-4, FR-19 à FR-23 (J4), FR-12 et FR-37 (J5) relèvent des Epics 12 et 13, sans stories par choix de périmètre.
- **Décisions → stories.** Les règles D1, les AD et les décisions D-nuit-A1 sont citées dans les rubriques « Couvre » des stories. Aucune story orpheline.
- **UX.** Aucune story J1 à J3 ne dépend de l'UX. Les UX-DR sont portées par les Epics 12 et 13.

## Constats bloquants corrigés dans `epics.md`

| # | Constat | Où | Correction |
|---|---|---|---|
| B1 | AD-6 réserve à `inference.serveur` le lancement des processus llama.cpp. Or 2.1 lançait `llama-server --version`, 8.1 (repli) et 10.6 lançaient la conversion et `llama-quantize` eux-mêmes. | 2.1 CA1, 2.2, 8.1 CA4, 10.6 | 2.2 porte les lanceurs `version`, `convertir_hf_vers_gguf` et `quantifier`, avec un nouveau CA8. 2.1 ne lance plus aucun binaire. 8.1 et 10.6 passent par ces lanceurs. |
| B2 | Le rapport de Baseline (8.4) charge les schémas `Scores`, `ResultatBench` et `ResultatMesure`, mais il ne dépendait que de 1.3. | 8.4 | Dépendances de développement : 5.6, 6.1, 6.4. |
| B3 | 8.2 modifie `cli/eval.py` et réutilise l'assemblage d'évaluation de 5.3. Rien ne l'empêchait de tourner en parallèle de 5.3 ou de 5.6, en contradiction avec la phrase « toujours séquentielles ». | 8.2 | Dépendance ajoutée : 5.6. |
| B4 | `harness/config.py` appartenait à 4.3. Or 4.2 a besoin de `k` et du seuil, et 4.4, parallèle à 4.3 en V8, a besoin de la réserve de sortie et du chevauchement. Résultat : un conflit de fichier, et `k` et le seuil auraient eu deux sources (avec `config/index.toml`). | 4.2, 4.3, 4.4 | 4.2 crée `harness/config.py` et `config/harnais.toml`. `k` et le seuil restent dans `config/index.toml` (story 2.3, source unique), d'où la nouvelle dépendance 4.2 → 2.3. 4.3 et 4.4 lisent ces fichiers sans les modifier. |
| B5 | 10.3 ajoutait une section `[entrainement]` à `config/mesures.toml` (story 6.4). Les deux stories n'étaient pas séquentielles. `train` ne peut pas importer `measure.config` (couche égale, AD-1), et `extra="forbid"` aurait rejeté la section. | 10.3, 10.4 | 10.3 crée `config/entrainement.toml` et `ConfigCouts` dans `train/config.py`, que 10.4 complète. |
| B6 | Le critère 3 de 10.6 utilise `evaluation.modele_ref` (5.3) et la sonde d'outils (8.2), qui ne figuraient pas dans ses dépendances. | 10.6 | Dépendance ajoutée : 8.2 (5.3 suit par transitivité). |
| B7 | 6.3 utilise le prompt de Tâche TR et `construire_messages` (story 4.1), absents de ses dépendances. 9.4 utilise `harness.recherche_index` (4.2) pour les passages Q, également absent. | 6.3, 9.4 | Dépendances ajoutées : 6.3 → 4.1, 9.4 → 4.2. |

S'y ajoute une précision (non bloquante) : dans 6.4, `cli/measure.py` assemble l'Assistant et le passe à `slmsp.measure`, qui n'importe jamais `slmsp.cli` (AD-1).

Le tableau des dépendances, le graphe mermaid et la rubrique « Validation finale » ont été mis à jour. Ces modifications restent compatibles avec l'ordre des vagues V0 à V19 : chaque nouvelle dépendance est placée dans une vague antérieure à celle de la story qui en dépend. La règle « aucune story ne dépend d'une story de numéro supérieur » est préservée.

## Réserves non bloquantes

1. **Décisions en attente d'Anaël, avec un défaut consigné qui permet d'avancer :**
   - D-nuit-1 : horaire décalé ;
   - A1-5 : Juge sans `temperature`, écart à la SPEC §7 ;
   - A1-10 : prompts de Tâche dans les données ;
   - A1-17 : index PyTorch CUDA ;
   - A2-5 : gel incomplet ;
   - A2-9 : tarifs prudents ;
   - A2-10 : lecture GET des conditions Mistral.
2. **Epic 1 technique.** C'est une exception assumée (D-nuit-A2-1).
3. **Piste 2 (Epic 7).** L'outil `eval/outils/construire_jeu.py` tourne en `uv run --no-project` mais importe en option `slmsp.core.texte`. La façon de rendre le paquet importable (par exemple `--with-editable .`) est laissée à la story 7.1. C'est sans risque, car l'import est optionnel, sauf pour Kandel-Moles en 7.4.
4. **Stories d'exécution** (8.3, 9.8, 11.2). Leur preuve est faite d'artefacts et non de tests. Elles dépendent du GPU, des budgets et du gel : il faut prévoir la sérialisation par `gpu.lock`.
5. **Clés du sprint-status.** Elles contiennent des caractères accentués (UTF-8) et sont tronquées par le script. L'orchestrateur doit cibler une story par son préfixe numérique `<epic>-<story>-`, qui est unique.
6. **Epics 12 et 13 (J4 et J5).** Elles sont classées `backlog`, hors sprint de la nuit, sans stories.

## Étape suivante

Développement par vagues (V0 : stories 1.1 et 7.1) avec `bmad-build-auto`. Il faut relancer `bmad-sprint-planning` si `epics.md` change.
