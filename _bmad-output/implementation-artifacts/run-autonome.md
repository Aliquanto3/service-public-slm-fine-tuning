# Run autonome de nuit du 20-21 octobre 2026 : routage, interpolation, sélection de candidats

Plan : `plan-nuit-2026-10-20.md` (version 2, réponses d'Anaël au §9 : Kimi juge croisé, usage recherche pour la sélection, mesure CPU de qwen-4b). Stories : `../planning-artifacts/stories-epic-15-nuit-2026-10-20.md`. Consignes des sous-agents : `consignes-sous-agents-2026-10-20.md`. Run précédent : `archive/run-autonome-2026-10-20.md`.
Garde-fous : D1 ; v1.1 = mesure finale seulement ; aucun push ; appels payants lancés par l'orchestrateur ; qualité sur GPU, charge sur CPU (machine au calme) ; bloqueur de veille pendant le GPU.
Budget : campagne `nuit-2026-10-20` (plafonds durs du registre) — openrouter 20 €, anthropic 50 € (relevé de 10 à 50 € par Anaël le 20/10 au soir), mistral 7,85 € (reste, non prévu).

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
- 2026-10-20 · run · décision · Anaël relève le plafond de nuit Anthropic à 50 € ; questions laissées avant son départ (3 mesures v1.1 au plus, `export purger --tous-notes` sous 25 Go libres, dev2 rédigé par agent) avec choix par défaut « oui » · —
- 2026-10-20 22:43 · témoin · décision · jeu **v19** = v18 sans CR, LC, RE (365 lignes ; NR absent de v18), `runs/data-build/20261020-224334-sous-ensemble-6d33` ; le jeu de sélection du plan (« v19 ») s'appellera **v20** · —
- 2026-10-20 22:44 · témoin · M1 MiniCPM5-2B v19 lancé (bloqueur de veille actif ; train + export cuda puis génération dev1 cuda + GLM, plafond 3 €), `config/runs/m1-qlora-minicpm5-2b-v19-sous-ensemble.toml` · —
- 2026-10-20 22:46 · 15.1, 15.2, 15.6, 15.5 · dev · lancés (Sonnet ; 15.5 sur Opus, qualité des items) · —
- 2026-10-20 22:46 · D0 · diagnostics lancés (agent Sonnet, lecture seule : pertes CR et RE par critère, troncatures CT, passages Q) · —
- 2026-10-20 22:46 · E5 · décision (règle ci-dessus, bootstrap 2 000 tirages, `e5/e5-minicpm.md`, `e5/e5-qwen.md`) : MiniCPM5-2B, seul **CO** est routé, vers M1 v18 (+10,4, IC95 [+4,9 ; +16,3] ; v14 +6,4 [+2,6 ; +10,7]) ; NR sans baisse significative (−5, [−25 ; +15]). Qualité attendue de la composition ≈ 54,5 + 10,4/8 ≈ 55,8 (+1,3, dans le bruit de ±4,5). Qwen3.5-0.8B : aucune tâche routée (CT v14 borne basse +0,0, pas > 0) · —
- 2026-10-20 22:47 · run · décision · Anaël valide les trois choix par défaut : 3 mesures finales v1.1 au plus (chacune après sa règle sur dev1), `export purger --tous-notes` sous 25 Go libres, dev2 rédigé par agent et non gelé cette nuit · —
- 2026-10-20 22:49 · 15.1 · dev · fini (10 tests verts ; « ok » = `complet` ; `modele_ref` du composé = celui du run par défaut, routage dans `config.route`) ; second-avis lancé · be32164
- 2026-10-20 22:54 · 15.1 · second-avis · 1 high (le Comparatif prendrait le composé pour la notation du run par défaut), 2 low (effort et mode du juge non comparés ; clés absentes). **Décision** : la Baseline dev1 `afd3` est `partiel-erreur` → source partielle acceptée, statut le moins bon propagé et consigné ; review lancée (Opus) · —
- 2026-10-20 22:58 · D0 · fini (`diagnostic-d0.md`) : (a) les pertes CR et RE de v18 viennent de l'**invention** (CR sans_invention 66,7 → 10,5, ~80 % de la perte ; RE fidèles 13/20 → 3/20, couverture RE en hausse) : argument direct pour la sélection (critère invention du juge de données) ; (b) CT : 13/20 sorties v18 en **boucle** dans l'en-tête (1 024 tokens, 4-grammes répétés à 0,85-0,97), cibles de 282-482 tokens ; cause probable : la consigne « exactement ces libellés » des items dev1 est absente des 30 prompts CT d'entraînement ; conformité CT à 0/20 pour la base aussi (mesure saturée) ; (c) Q : éléments clés présents dans les passages 49/69 (page entière 59/69), 5 passages occupés par 1 à 3 pages ; k=8 + dédoublonnage du préfixe des passages : 49 → 57/69 (0 €) ; les 3 items sans réponse échouent (scores hors corpus 0,55-0,67 au-dessus du seuil 0,5). Leviers Q et CT = changement de harnais ou de données : **proposés à Anaël**, hors du plan de nuit · —
- 2026-10-20 23:04 · 15.1 · review · 1 high et 2 medium corrigés (Comparatif et juges tiers ignorent ou refusent un composé ; source partielle admise, statut propagé), juge comparé sur modèle, fournisseur, effort et mode · 6b0dae6
- 2026-10-20 23:04 · 15.1 · fusion · squash dans main ; tests composition et bootstrap : 26 passés · 91045ea
- 2026-10-20 23:04 · E5 · composition dev1 `20261020-230351-compose-0d5a` (base partout, M1 v18 sur CO) : Qualité 54,5 → **55,8** (+1,3, IC95 [+0,6 ; +2,0]) ; pas de composition v1.1 (M1 v18 n'a pas de notation v1.1, la créer serait une mesure payante hors règle). Reste le test de déploiement LoRA (15.6) · —
- 2026-10-20 23:04 · 15.4 · dev · lancé · —
- 2026-10-20 23:07 · 15.6 · dev · fini (`export lora`, `lora:<id>@<échelle>` dans la référence du modèle, contournement du `:` de `--lora-scaled` par le dossier courant ; essai à blanc de conversion de l'adaptateur v18 OK, 588 tenseurs, 50 Mo ; DoRA, rsLoRA, PiSSA refusés) ; second-avis lancé · 2ce2fdb
- 2026-10-20 23:07 · 15.2 · dev · fini (15 tests ; contrat O2 respecté) ; second-avis lancé · 7fe729a
- 2026-10-20 23:07 · 15.2 · **décision** : juge croisé = `moonshotai/kimi-k2.6` (OpenRouter, sorties structurées, 0,65 / 3,41 $/Mtok relevés le 20/10 ; kimi-k3 écarté : raisonnement, sortie 11,9 $/Mtok). **RE n'a pas de grille de jugement de données** (CR, LC, CT seulement) : pas de candidats RE ; v20 = v18 avec CR et LC sélectionnés et **RE retiré** (D0 : les cibles RE Mistral inventent, la base fait mieux) · —
