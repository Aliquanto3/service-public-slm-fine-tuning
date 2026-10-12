---
title: Spécification du Jeu d'évaluation maison
version: 1.0
status: validé par Anaël le 2026-10-12 (v1.0) ; items à challenger plus tard par un agent public réel
sources:
  - _bmad-output/planning-artifacts/prds/prd-service-public-slm-fine-tuning-2026-10-11/prd.md (FR-24, FR-25, FR-39, FR-40, §8, §10.1)
---

# Spécification du Jeu d'évaluation maison

## 1. Rôle et règles absolues

Le Jeu d'évaluation maison mesure l'Assistant (Harnais + modèle) sur les Tâches du domaine. Il décide du go ou du no-go du fine-tuning (SM-1) et du choix du Modèle embarqué.

1. **Jamais utilisé pour l'entraînement.** Aucun item, aucun quasi-doublon et aucune paraphrase ne doit figurer dans les Données d'entraînement. Le contrôle anti-fuite est automatique (FR-24).
2. **Figé avant toute génération de Données d'entraînement.** Le gel se fait par une version et un manifeste d'empreintes SHA-256 (§6).
3. **Références vérifiées sur source réelle.** Toute référence factuelle (fait, montant, URL, valeur de données) provient d'une source officielle effectivement consultée, dont la date de consultation est notée. Les références ne sont jamais écrites de mémoire.
4. **Claude peut rédiger les items.** Ce jeu n'entre jamais dans l'entraînement (§8 du PRD). Les contenus fictifs (notes de réunion, textes à fautes, demandes de courrier) sont autorisés et marqués `fictif: true`.

## 2. Composition (v1)

| Tâche | Code | Items | Répartition de difficulté (facile / moyen / difficile) |
|---|---|---|---|
| Question | Q | 60 | 20 / 25 / 15, dont 8 sans réponse dans les sources |
| Recherche de données | RD | 40 | 15 / 15 / 10, dont 5 demandes de valeurs (FR-8) et 4 cas de repli |
| Compte rendu | CR | 25 | 8 / 10 / 7, dont 5 transcriptions de plus de 4 000 mots |
| Langage clair | LC | 25 | 8 / 10 / 7 |
| Correction | CO | 15 | 5 / 5 / 5 |
| Résumé | RE | 15 | 5 / 5 / 5 |
| Courrier type | CT | 15 | 5 / 5 / 5 |
| Non-régression générale | NR | 30 | 10 / 10 / 10 |
| **Total** | | **225** | |

### Couverture thématique (Q, RD, LC, RE)

Les thèmes reflètent les deux profils de la démo :

| Domaine | Part des items |
|---|---|
| Social et autonomie (APA, RSA, PCH, aide sociale à l'enfance, logement) | 30 % |
| État civil et papiers | 15 % |
| Travail et emploi | 15 % |
| Collectivités (organisation, compétences du département, marchés publics) | 15 % |
| Famille, éducation et santé | 15 % |
| Fiscalité locale | 10 % |

La Recherche de données couvre au moins 6 producteurs de données différents (INSEE, DREES, ministères, collectivités…).

### Profil des amorces
- **Q** : au moins 50 % des items viennent d'amorces réelles (`AgentPublic/sp_questions_corpus`, `assistant_ia_questions_corpus`), reformulées comme un Agent les poserait.
- **NR** : pour moitié des questions de culture générale et de raisonnement simple, pour moitié des consignes de rédaction courtes (courriel, reformulation, liste), en français.

## 3. Schéma d'un item (JSONL, UTF-8)

Champs communs :

```json
{
  "id": "Q-001",
  "tache": "Question",
  "difficulte": "facile | moyen | difficile",
  "theme": "social-autonomie",
  "entree": "…texte saisi par l'Agent ou collé…",
  "parametres": {"longueur": "courte"},
  "provenance": [{"type": "service-public", "url": "…", "consulte_le": "2026-10-12"}],
  "licence_source": "Etalab-2.0",
  "fictif": false,
  "version_item": 1
}
```

Champs de référence propres à chaque Tâche :

| Tâche | Champs de référence |
|---|---|
| Q | `reponse_reference`, `elements_cles` (3 à 5 faits indispensables), `sources_attendues` (URL), `sans_reponse` (booléen), `orientation_attendue` si `sans_reponse` |
| RD | `appels_attendus` (outil + arguments clés, sous-ensemble de l'addendum §B), `cassettes` (chemins des réponses enregistrées), `reponse_reference`, `valeurs_attendues` si la demande porte sur des valeurs, `mode` (connecté / hors ligne / repli) |
| CR | `decisions_reference`, `actions_reference` (avec responsable et échéance), `pieges` (éléments évoqués mais non décidés) |
| LC | `informations_a_conserver` (montants, dates, obligations), `termes_juridiques_a_conserver`, `kandel_moles_entree` |
| CO | `fautes` (position, erreur, correction, type), `texte_corrige_reference` |
| RE | `points_cles_reference`, `longueur_demandee` |
| CT | `type_courrier`, `elements_obligatoires`, `champs_a_laisser_en_emplacement` |
| NR | `reponse_reference` ou `criteres` |

## 4. Bac à sable MCP (FR-40)

Chaque item RD s'accompagne des réponses réelles des outils, enregistrées sous forme de cassettes JSON dans `eval/cassettes/RD-xxx/`. Une cassette contient la requête, la réponse, la date et la version du schéma de l'outil.

L'évaluation rejoue ces cassettes. Si le modèle fait un appel qui ne correspond à aucune cassette, le banc :
1. le note « appel non prévu » ;
2. rejoue la cassette la plus proche si elle existe ;
3. sinon, renvoie une réponse vide normalisée.

Les cas de repli (délai dépassé, erreur) sont simulés par des cassettes d'erreur.

## 5. Construction du jeu complet (run autonome)

1. **Génération par lots, Tâche par Tâche**, selon les §2 et §3. Chaque item est écrit à partir de la source réelle consultée.
2. **Double vérification.** Un second agent, indépendant, relit chaque item contre ses sources et rejette les items suivants :
   - un fait de référence absent de la source ;
   - une URL morte ou différente ;
   - un item ambigu, c'est-à-dire avec plusieurs réponses justes non prévues ;
   - un doublon thématique trop proche d'un autre item.
3. **Remplacement.** Les items rejetés sont remplacés jusqu'à atteindre les volumes du §2. Le taux de rejet est consigné.
4. **Échantillon de relecture.** Un échantillon stratifié de 20 % (au moins 1 item par Tâche et par niveau de difficulté) est exporté dans `eval/revue/echantillon-revue-v1.0.md`, pour la relecture d'Anaël.

## 6. Gel et versions

- **Gel provisoire.** Une fois construit, le jeu est figé en version `v1.0-provisoire` :
  - `eval/jeu/v1.0/items.jsonl` ;
  - `eval/jeu/v1.0/MANIFEST.json`, qui contient le SHA-256 de chaque fichier, de chaque cassette et de la grille du juge, ainsi que la date ;
  - un commit git dédié.
- **Contrôle à chaque évaluation.** Le banc vérifie le manifeste avant chaque évaluation et refuse de s'exécuter en cas d'écart.
- **Pas de génération avant le gel.** Aucune génération de Données d'entraînement ne commence avant le commit de gel. Le pipeline de données vérifie la présence du manifeste.
- **Relecture d'Anaël.** Après relecture, les items corrigés incrémentent `version_item` et le jeu passe en `v1.1`. Toutes les évaluations sont alors relancées. Les scores obtenus sur `v1.0-provisoire` restent archivés, marqués « non relus ».

## 7. Juges

| Rôle | Modèle | Périmètre |
|---|---|---|
| Juge principal | Claude Opus 5.5 (`claude-opus-5-5`) | Tous les items notés par un Juge |
| Second juge | Mistral Large (version stable, hors « Labs ») | 20 % des items, tirés au hasard avec une graine fixe |

- **Accord entre juges.** Il est mesuré par le kappa de Cohen pondéré, rapporté par Tâche. Si kappa < 0,6 sur une Tâche, la grille de cette Tâche est à revoir. Ses scores restent publiés, mais marqués « fragiles ».
- **Conditions de jugement.**
  - Température 0.
  - Le juge ne voit ni l'identité du modèle évalué ni la méthode utilisée.
  - Pour les comparaisons, l'ordre de présentation est aléatoire.
  - Le juge reçoit l'entrée, la sortie, les champs de référence et la section de la grille correspondant à la Tâche.
  - Il répond en JSON validé par schéma.
- **Relecture humaine.** 20 % des items notés par le Juge sont exportés. Les scores sont marqués « non relus » jusqu'à la validation d'Anaël (FR-25).

## 7 bis. Codes d'identifiants

Les codes du §2 font foi : Q, RD, CR, LC, CO, RE, CT, NR. L'échantillon de calibrage utilise encore R- (Recherche de données) et RS- (Résumé). Le jeu complet utilise RD- et RE-.

## 8. Fichiers

```
eval/
  SPEC-jeu-evaluation.md        ← ce document
  grille-juge-v1.md             ← barème du Juge (FR-39)
  calibrage/                    ← échantillon de 16 items validé avec Anaël
  jeu/v1.0/items.jsonl, MANIFEST.json
  cassettes/RD-xxx/*.json       ← Bac à sable MCP
  revue/                        ← échantillons de relecture humaine
```
