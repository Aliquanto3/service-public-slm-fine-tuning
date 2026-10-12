# Rapport de Baseline (réduite) — 2026-10-12

> **Ce rapport ne prend pas la décision go/no-go.** Il rassemble les éléments qui permettront à Anaël de trancher.
> Tous les scores sont **provisoires et non relus** : le jeu est `v1.0-provisoire`, et l'échantillon de relecture humaine de 20 % n'est pas encore validé. Le statut « fragile » signale un accord insuffisant entre les deux juges.

## 1. Périmètre réellement couvert

| Élément prévu (phase C) | Fait ? | Remarque |
|---|---|---|
| Jeu d'évaluation maison (225 items), Juge Claude, 20 % rejugés par Mistral | ✅ pour 2 modèles | Granite 4.0 1B et Ministral 3 3B |
| SmolLM3 3B, témoin Qwen 4B, Ministral 8B | ❌ | Exclus de la Baseline réduite pour tenir le budget (D-nuit-4). SmolLM3 a échoué à la sonde d'outils (0/5) |
| Benchmarks standardisés (lm-eval, BFCL, sacrebleu) | ❌ | Epic 6 non développé, hors du périmètre réduit |
| Mesures FR-26 (RAM de l'Assistant complet, débit, latence) | ⚠️ partiel | Seules des mesures en passant sont disponibles (§4) ; la story 6.4 n'est pas faite |

**Runs**, tous versionnés :

| Modèle | Génération | Notation | Coût du Juge |
|---|---|---|---|
| Granite 4.0 1B Q4_K_M | `runs/eval-generation/20261012-171658-granite-4.0-1b-3589` | `runs/eval-notation/20261012-172922-granite-4.0-1b-be1d` | 2,95 € |
| Ministral 3 3B Q4_K_M | `runs/eval-generation/20261012-173832-ministral-3-3b-5531` | `runs/eval-notation/20261012-180710-ministral-3-3b-0756` | 3,28 € |

**Conditions communes** :
- jeu `v1.0`, SHA-256 du manifeste `70c42fb5…43dc` ;
- llama.cpp b11429 en CUDA (RTX 3050), génération sans réseau contre le Bac à sable MCP ;
- Juge principal `claude-opus-5-5` en Batch API, second juge `mistral-large-latest` sur 34 items.

## 2. Scores de Tâche (sur 100)

| Tâche | Granite 4.0 1B | Ministral 3 3B | Composantes (Granite / Ministral) |
|---|---|---|---|
| Q : Question fondée | **0,0** | **5,0** | réussis 0 / 5 ; URL inventées : 0 / 11 items |
| RD : Recherche de données | **73,3** | **72,8** | appel valide 66,7 / 70,7 ; réponse exacte 80 / 75 |
| CR : Compte rendu | 32,9 | 37,7 | couverture 45,7 / 63,3 ; sans invention 20 / 12 |
| LC : Langage clair | **0,0** (plafonné) | **0,0** | fidélité et termes 0 / 0 ; gain Kandel-Moles 4,0 / 10,3 |
| CO : Correction | **79,3** | 40,7 | rappel × hors faute |
| RE : Résumé | 31,9 | 34,6 | couverture 37,1 / 69,2 ; fidèles 26,7 / 0 |
| CT : Courrier type | 30,0 | 20,0 | conformité 0 / 0 ; emplacements 60 / 40 |
| NR : Non-régression | 20,0 | **46,7** | exacts |

Le kappa entre le Juge Claude et le second juge Mistral vaut entre −0,00 et 0,21 selon les Tâches. **Toutes les Tâches jugées sont marquées « fragile »**, à l'exception de RD et de CO, qui sont notées par contrôles automatiques.

## 3. Faiblesses principales, par Tâche

Ces observations viennent des justifications du Juge et des stories 4.2 et 8.2.

- **Q : Question fondée.** C'est la faiblesse la plus nette, pour les deux modèles.
  - L'exactitude est notée 0 sur 45 des 60 items pour Ministral, et sur 56 des 60 pour Granite.
  - Granite ne produit **aucun renvoi `[n]`** : la pertinence de la source vaut 0 sur 53 des 60 items (constat de la story 4.2).
  - Ministral cite mieux (pertinence 1 sur 46 items sur 60), mais **invente des URL sur 11 items**.
  - Les cas « sans réponse » sont presque tous manqués : 0 sur 8 pour Granite, 2 sur 8 pour Ministral.
- **LC : Langage clair.** La fidélité vaut 0 sur 24 ou 25 des 25 items pour les deux modèles. Les réécritures ajoutent ou déforment des conditions juridiques. Exemple sur LC-001 : « au moins 2 ans consécutifs » au lieu de « 2 ans à temps plein ». Le gain de lisibilité est réel pour Ministral (+10,3 de Kandel-Moles), mais il se paie en exactitude.
- **CT : Courrier type.** La conformité vaut 0 sur 15 items pour les deux modèles. Il manque des éléments obligatoires (en-tête de l'expéditeur, bloc destinataire, lieu et date), et des informations fournies sont remplacées par des emplacements.
- **RE : Résumé.** Ministral couvre bien (69 %), mais n'a **aucun** résumé jugé fidèle : il généralise des restrictions et confond des dispositifs. Granite couvre moins mais reste plus fidèle (27 %).
- **CR : Compte rendu.** La couverture est correcte chez Ministral (63 %), mais la Tâche souffre d'inventions : les pièges du jeu sont présentés comme des décisions.
- **CO : Correction.** Granite 1B dépasse nettement Ministral 3B : 79 contre 41.
- **RD : Recherche de données.** C'est le point fort des deux modèles (environ 73), avec un appel d'outil natif valide 2 fois sur 3.
- **NR : Non-régression.** Ministral garde mieux ses connaissances générales : 47 contre 20.

**Lecture d'ensemble.** Les deux modèles de base maîtrisent les outils (RD) et la correction (CO). En revanche, ils échouent sur toutes les Tâches qui exigent une **fidélité stricte à une source administrative** (Q, LC, RE, CT). C'est précisément ce que le fine-tuning doit améliorer. La grille du Juge est volontairement binaire : un seul contresens met le critère à 0. Les scores bas sont donc en partie l'effet de cette sévérité, à confirmer par la relecture humaine.

## 4. Mesures techniques et conformité aux NFR

Seules des mesures prises en passant sont disponibles. Le protocole FR-26 (story 6.4) n'est pas développé.

| Mesure | Granite 4.0 1B | Ministral 3 3B | NFR |
|---|---|---|---|
| Durée moyenne par item, CUDA, Harnais complet | 3,3 s | 6,4 s | — |
| Débit en génération, CPU (story 2.2) | environ 42 tokens/s (26 à 42) | non mesuré | NFR-2 : au moins 8 tokens/s ✅ pour Granite, en CPU sur le poste de dev |
| Premier token, CPU (story 2.2) | 164 ms (sans recherche) | non mesuré | NFR-3 : moins de 5 s, non mesuré avec recherche |
| Taille du GGUF Q4_K_M | 1,0 Go | 2,1 Go | — |
| Index local (story 2.3) | 457 Mo, RAM ajoutée 282 à 298 Mio, p95 de recherche 314 à 329 ms | idem | — |
| RAM de l'Assistant complet | **non mesurée** | **non mesurée** | NFR-1 (5 Go au plus, cible 4) : **à mesurer** (story 6.4) |

**Estimation, à vérifier**, et non une mesure : GGUF de 1 Go + index d'environ 0,3 Go + BGE-M3 d'environ 0,7 Go + contexte, soit environ 2,5 à 3 Go pour Granite et environ 3,5 à 4 Go pour Ministral 3B. Les deux tiendraient donc a priori dans les 5 Go de NFR-1.

Ces mesures ont été prises sur le poste de développement, et non sur un PC cible.

## 5. Éléments pour la décision d'Anaël (go/no-go)

1. **Écart à combler** : il est important sur Q, LC, RE et CT, qui sont les Tâches cœur du produit. Le fine-tuning a donc une marge de progression mesurable. À l'inverse, RD et CO sont déjà acceptables.
2. **Choix du modèle pour l'essai QLoRA** (règle D4 : le meilleur score moyen parmi les modèles de 3B au plus qui tiennent dans 5 Go).
   - Score moyen sur les 8 Tâches : Granite **33,4**, Ministral **32,2**.
   - L'écart n'est pas significatif vu la fragilité des juges.
   - Ministral cite ses sources et garde mieux ses connaissances générales. Granite est deux fois plus rapide et n'invente pas d'URL.
   - Par la règle D4 appliquée strictement, **Granite 4.0 1B**.
3. **Fiabilité de la mesure**
   - Le kappa entre juges est quasi nul : avant de comparer finement des modèles, il faut relire l'échantillon de 47 items (`eval/revue/echantillon-revue-v1.0-lecture.md`) et décider s'il faut ajuster la grille ou le Juge.
   - Coût d'une évaluation complète : environ 3 € de Juge par modèle.
4. **Reste à faire pour une Baseline complète** :
   - Benchmarks standardisés (epic 6) ;
   - mesures FR-26 (6.4) ;
   - SmolLM3, en réglant d'abord le format d'outils, et Qwen 4B ;
   - Ministral 8B comme plafond de qualité.
