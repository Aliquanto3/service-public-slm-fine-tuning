# Run autonome de nuit du 20-21 octobre 2026 : routage, interpolation, sélection de candidats

Plan : `plan-nuit-2026-10-20.md` (version 2, réponses d'Anaël au §9 : Kimi juge croisé, usage recherche pour la sélection, mesure CPU de qwen-4b). Stories : `../planning-artifacts/stories-epic-15-nuit-2026-10-20.md`. Consignes des sous-agents : `consignes-sous-agents-2026-10-20.md`. Run précédent : `archive/run-autonome-2026-10-20.md`.
Garde-fous : D1 ; v1.1 = mesure finale seulement ; aucun push ; appels payants lancés par l'orchestrateur ; qualité sur GPU, charge sur CPU (machine au calme) ; bloqueur de veille pendant le GPU.
Budget : campagne `nuit-2026-10-20` (plafonds durs du registre) — openrouter 20 €, anthropic 50 € (relevé de 10 à 50 € par Anaël à 22 h 50), mistral 7,85 € (reste, non prévu).

## Périmètre
| Périmètre | Epics | Note |
|---|---|---|
| Dans le run | Epics 15 à 15 | 15.1 N1 `eval composer`, 15.2 N2 candidats, 15.3 N3 sélection, 15.4 N4 second juge dev*, 15.5 N5 dev2, 15.6 N6 LoRA GGUF ; expériences D0, E5, E7, témoin, test de déploiement, qwen-4b CPU, E2/E4 |
| Hors run | C5, E3, E6 (non numérotées) | paires notées seulement après une recette SFT gagnante |

Au plus 4 stories en développement à la fois.

## Sprint 1 — nuit du 20-21/10
| Vague | Stories en parallèle | Après |
|---|---|---|
| V0 | 15.1 · 15.2 · 15.6 · 15.5 | |
| V1 | 15.4 · 15.3 ★ | 15.3 ← 15.2 (amendements de spec relus avant code) |

## Règles de décision (écrites avant tout calcul)
- **E5, routage** : un adaptateur est routé sur la tâche t seulement si la borne basse de l'IC95 apparié (bootstrap, `eval comparer`) sur dev1 est > 0 pour t contre la Baseline, et jamais sur une tâche où NR baisse significativement (borne haute < 0). Candidats : M1 v14 et v18 de MiniCPM5-2B, puis le témoin sous-ensemble. Composition v1.1 marquée `deja-consulte` ; confirmation sur dev2. Le routage n'est retenu que si le test de déploiement LoRA le valide.
- **E7, interpolation** : échelle s retenue si, sur dev1 contre la Baseline, aucune tâche n'a une borne basse < −10 (non-infériorité par tâche) et Qualité ≥ Baseline − 2.
- **v20 (sélection, = « v19 » du plan)** : retenue si sa Qualité dev1 ≥ meilleure composition routée − 2 ; décision définitive après dev2.
- **Mesure finale v1.1 (Claude)** : seulement pour une configuration qui passe sa règle sur dev1 ; 3 au plus (défaut annoncé à Anaël).

## Journal
- 2026-10-20 22:41 · run · décision · campagne de budget `nuit-2026-10-20` ouverte (méthodo-v2-2026-10-20b close : mistral 1,63 €, openrouter 8,18 €) ; ancien run archivé (`archive/run-autonome-2026-10-20.md`) · —
- 2026-10-20 22:50 · run · décision · Anaël relève le plafond de nuit Anthropic à 50 € ; questions laissées avant son départ (3 mesures v1.1 au plus, `export purger --tous-notes` sous 25 Go libres, dev2 rédigé par agent) avec choix par défaut « oui » · —
- 2026-10-20 22:43 · témoin · décision · jeu **v19** = v18 sans CR, LC, RE (365 lignes ; NR absent de v18), `runs/data-build/20261020-224334-sous-ensemble-6d33` ; le jeu de sélection du plan (« v19 ») s'appellera **v20** · —
- 2026-10-20 22:55 · témoin · M1 MiniCPM5-2B v19 lancé (bloqueur de veille actif ; train + export cuda puis génération dev1 cuda + GLM, plafond 3 €), `config/runs/m1-qlora-minicpm5-2b-v19-sous-ensemble.toml` · —
