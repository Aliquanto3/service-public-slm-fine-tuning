# Dossier de relecture : jeu v9 et campagne minicpm5-2b-v9

Préparé le 19 octobre 2026 en fin d'après-midi, pour Anaël. **Aucun entraînement n'a été lancé** : il attend ta relecture.

## 1. Le jeu v9 en bref
- `data/train/v9/train.jsonl` (484 lignes, SHA-256 `0c0af966…`). Il vient de trois générations Mistral au total, dont les deux dernières n'ont repayé que ce qui avait changé.
- Filiation :
  - seed `20261017-111645-seed-b335` (le même que v2) ;
  - génération `20261019-170036-generate-d2ae` : la plupart des sessions sont réutilisées de `…140413-generate-9b48` (cibles courtes, 9.10) ; seul RE est régénéré (9.11) ;
  - validation `…170331-validate-638b`, filtre anti-fuite `20261019-172346-filter-2d63`, build v8 `…173854-build-0328` ;
  - nettoyage v9 `…173901-nettoyage-3ed6`, règle de nettoyage version 2.
- Coût Mistral : environ 4,3 € au total (génération 8,75 € au plafond de la campagne).
- Ce qui a changé par rapport à v4 :
  - consignes de longueur par tâche et de forme (pas de titre ni de phrase d'annonce en tête) dans les gabarits Q, RD, CR, LC, CT, generique et RE ;
  - `max_tokens` du générateur abaissés ;
  - retrait déterministe d'un vrai titre de tête au nettoyage.

## 2. Comptes et longueurs (mots de la cible)

| Tâche | v4 : lignes | v4 : médiane | v9 : lignes | v9 : médiane | v9 : p90 | v9 : max | Plafond demandé | Référence d'éval (médiane) | Titre en tête v4 → v9 |
|---|---|---|---|---|---|---|---|---|---|
| Q | 92 | 237 | 95 | **106** | 137 | 184 | 160 | 116 | 34 → 0 |
| RD | 89 | 122 | **64** | **47** | 62 | 113 | 120 | 80 | 5 → 4 |
| CR | **0** | — | **79** | 396 | 447 | 505 | 400 | — | 0 → 0 |
| LC | 69 | 166 | 69 | 113 | 156 | 199 | 150 | — | 6 → 0 |
| CT | 34 | 234 | 35 | 152 | 176 | 185 | 150 | — | 34 → 2 |
| RE | 34 | 132 | 34 | 112 | 205 | 308 | selon la longueur demandée | — | 34 → 0 |
| CO | 34 | 83 | 34 | 83 | 105 | 138 | — (correction) | — | 0 → 0 |
| generique | 73 | 111 | 74 | 96 | 136 | 163 | 200 | — | 1 → 0 |
| **Total** | **425** | | **484** | | | | | | |

Rejets en amont (validation) : 110 sur 594, dont `valeur_absente` 89 (73 en RD) et `url_inventee` 21 (16 en generique). Le filtre anti-fuite n'écarte rien. Le nettoyage ne retire que 18 préambules (RD 13, LC 5) et n'écarte aucune cible pour sa longueur : toutes tiennent sous 1 024 tokens.

## 3. Points à relire en priorité
1. **RD est devenu court et maigre.** Médiane de 47 mots, contre 80 pour les références, et seulement 64 exemples, contre 91 en v2. Les réponses courtes omettent plus souvent la valeur renvoyée par l'outil, et la validation les écarte (`valeur_absente`). Trois options :
   - relever le plafond RD à 160 mots et régénérer RD seul, environ 1 € ;
   - garder v9 tel quel ;
   - réutiliser les RD de v2 (longs, avec préambules, mais 91 exemples).
2. **CR revient (79 exemples)**, avec une médiane de 396 mots, donc au plafond de 400. Le CR de M1 v4 était remonté à 37,5 sans aucun CR à l'entraînement : à vérifier qu'un CR de 400 mots n'est pas encore trop long pour la grille.
3. **Notes en fin de cible LC.** 65 cibles LC sur 69 se terminent par « *Passage non simplifié (termes juridiques obligatoires) : …* ». Le gabarit LC le demande, ce n'est pas un défaut de génération. Mais le modèle l'apprendra : vérifier que la grille LC ne le pénalise pas. LC est à 4,0 pour M1 v4.
4. **Le gras reste fréquent dans le corps** (Q 55 sur 95, RD 59 sur 64), mais plus en première ligne.
5. **CT** : 2 titres de tête restent. Ce sont des lignes « Objet : … » de courrier, que la règle garde volontairement.
6. **LC signalés par le nettoyage** (3), sur des sigles : liste dans `runs/data-build/20261019-173901-nettoyage-3ed6/rapport.json`.

Un échantillon de deux cibles par tâche est dans `dossier-relecture-v9-echantillon.json` (même dossier). Une cible par tâche, en extrait :
- **Q** (69 mots) : « Un micro-entrepreneur n'est pas systématiquement obligé de s'assurer, mais cela dépend de son activité [1][2]. Si son activité est réglementée… »
- **RD** (48 mots) : « Aucun jeu de données récent ne correspond directement à votre demande sur le déploiement FTTH en Corse. **Piste alternative** : … »
- **CR** (403 mots) : « La réunion avait pour objet de clarifier le cadre juridique et pratique… Étaient présents… »
- **RE** (275 mots) : « Ce texte précise les documents à fournir pour une demande de carte de séjour… »

## 4. Protocole proposé (configs prêtes, non commitées avant ton accord)
- `config/runs/m1-qlora-minicpm5-2b-v9.toml` et `config/runs/m3-dora-minicpm5-2b-v9.toml` : campagne `minicpm5-2b-v9`, jeu v9, bf16, **8 192 tokens**, graine 1234.
- Hyperparamètres identiques à v2 et v4 : rang 16, alpha 32, dropout 0, lr 2e-4 en cosinus, échauffement 3 %, **1 époque**, lot 1 × accumulation 8. Une seule variable change donc : le jeu.
- **Point d'attention** : avec 484 exemples, une époque ne fait qu'environ 60 pas d'optimisation. Une seconde campagne à 2 époques serait un levier distinct. Je ne la propose qu'après M1 v9, pour ne pas mélanger deux variables.
- Garde mémoire : `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` et arrêt propre au-delà de 28 Go de RAM.
- Ordre proposé :
  1. M1 v9 : 25 min d'entraînement, export, génération ;
  2. notation avec `--plafond-estime 4.5`, environ 3 € ;
  3. M3 v9 seulement si M1 v9 dépasse la Baseline (41,1).
- M4 ORPO demanderait de nouvelles paires depuis v9 : génération locale sur GPU, sans appel payant.
- **Budget Anthropic restant : 5,66 €**, soit environ 2 notations.

### Ajout du 19 à 17 h 50 : Qwen3.5 dans la campagne (décision d'Anaël)
- Configs `m1-qlora-` et `m3-dora-` pour `qwen3.5-2b` et `qwen3.5-0.8b`, sur v9. Une campagne par modèle (`<slug>-v9`), mêmes hyperparamètres, 8 192 tokens. Les sondes du 19 tiennent sur 6 Go : 4,15 Gio et 2,42 Gio.
- Mesures CPU (q4_k_m) :
  - qwen3.5-2b : 3,39 Go de RAM, 23,2 tokens/s, Baseline 36,0, RD 86,9 ;
  - qwen3.5-0.8b : 2,26 Go, 43,3 tokens/s, Baseline ~27,5.
  
  Les deux restent sous 5 Go.
- Budget : six runs M1 et M3 sur trois modèles demanderaient environ 18 € de notation, pour 5,66 € restants. Il faut prioriser, par exemple M1 sur chacun des trois modèles (environ 9 €), ou relever le budget.

## 5. Ce que j'attends de toi
- Valider v9 ou demander un correctif. Le plus probable : RD, point 3.1.
- Valider le protocole et l'ordre M1 puis M3 ; dire si l'on teste 2 époques.
- Dire s'il faut relever le budget Anthropic pour noter plus de deux runs.
