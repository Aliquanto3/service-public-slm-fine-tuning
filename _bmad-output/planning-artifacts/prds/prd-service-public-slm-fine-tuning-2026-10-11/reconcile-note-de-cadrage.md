# Réconciliation : note de cadrage contre PRD et addendum

Entrée : `Note de cadrage — SLM secteur public français.md`. Documents comparés : `prd.md` et `addendum.md` (même dossier que ce fichier). Les reformulations fidèles sont ignorées. Statuts : absent, contredit, affaibli. Priorité : P1 (à corriger avant l'architecture), P2 (utile), P3 (détail).

## A. Lots, jalons, priorités, périmètre

| # | Élément de la note | Statut | Où intégrer | Correction proposée | Prio |
|---|---|---|---|---|---|
| A1 | Plan en 5 lots (0 Cadrage, 1 Baseline, 2 Données, 3 Fine-tuning, 4 Packaging) avec livrables et charge (3–5, 5–8, 5–10, 5–10, 3–5 j) | absent | PRD §9 (ou nouvelle §9.3), détail dans addendum (nouvelle section « Plan de réalisation ») | Recopier la table des lots, livrables et charges, et rattacher chaque lot aux FR concernés. | P1 |
| A2 | Charge totale 21 à 38 jours, soit 3 à 6 mois en side project | absent | PRD §9 | Ajouter l'enveloppe de charge comme contrainte de projet. | P1 |
| A3 | Jalon clé = fin du lot 1 : la Baseline « décide de ce que le fine-tuning doit corriger » et porte le go / no-go | affaibli | PRD §9 et SM-1, glossaire « Baseline » | Dire que le go / no-go est pris à la fin du lot 1 et que la Baseline désigne les faiblesses ciblées par les Données d'entraînement. SM-1 ne fixe aujourd'hui qu'un seuil chiffré. | P1 |
| A4 | Périmètre : 4 cas d'usage, classés par priorité (1 Questions sourcées, 2 data.gouv, 3 compte rendu, 4 langage clair) | affaibli | PRD §1, §4 et §9 | Reprendre l'ordre de priorité ; il sert d'ordre de coupe si la charge dérape. Le PRD liste 8 Tâches sans hiérarchie. | P1 |
| A5 | Seuls 4 cas d'usage dans la note ; Courrier type, Résumé, Correction et Traduction (5 langues dont l'arabe) viennent du PRD | contredit (élargissement) | PRD §9.1 et §11, addendum F | Marquer ces 4 Tâches comme extension hors note, `[ASSUMPTION]` sur l'effort, et dire qu'elles passent après les 4 cas prioritaires. Les volumes d'entraînement ne sont pas chiffrés dans l'enveloppe de 21–38 j. | P1 |
| A6 | Objectif secondaire = monter en compétence de bout en bout (données, fine-tuning, évaluation, packaging) | contredit | PRD §1 | Le PRD dit que le Comparatif est un objectif « d'égale importance » ; remettre la montée en compétence comme objectif secondaire et le Comparatif comme livrable de ce second objectif, ou assumer le changement. | P2 |
| A7 | Fine-tuning par QLoRA avec Unsloth, 3 à 5 itérations, puis fusion et quantification GGUF | contredit / absent | Addendum E, FR-32 | La note retient Unsloth comme outil de lot 3 ; l'addendum met TRL + PEFT en socle et Unsloth en mesure parallèle. Trancher et noter la raison du changement. « 3 à 5 itérations » est perdu. | P2 |
| A8 | Lot 3 = 5–10 j pour QLoRA seul ; le PRD ajoute LoRA 16 bits, DoRA, rsLoRA, PiSSA, ORPO/DPO et un socle de 7 benchmarks | contredit (charge) | PRD §9 et addendum A1 | Le Comparatif de 4 méthodes n'est pas dans l'estimation. Réestimer les lots 3 et 1 ou prioriser (QLoRA d'abord). | P1 |
| A9 | En ligne, la note ne prévoit que le serveur MCP data.gouv (3 briques) ; le PRD ajoute la consultation de pages web de 5 domaines (FR-11, FR-12) | contredit (élargissement) | PRD FR-11/FR-12, addendum A | Soit retirer FR-12 de la v1, soit l'ajouter explicitement à l'architecture comme 4e brique avec son risque (outil supplémentaire, voir B1). | P2 |

## B. Risques et parades

La note a un tableau de 7 risques avec parades. Le PRD n'a pas de section risques ; les parades sont dispersées ou perdues.

| # | Élément de la note | Statut | Où intégrer | Correction proposée | Prio |
|---|---|---|---|---|---|
| B1 | Tool calling instable à 3B : « peu d'outils aux schémas simples » | absent | Addendum A et B, NFR-9 | L'addendum B liste 10 outils sans les restreindre. Définir le sous-ensemble minimal d'outils exposés au modèle (5 au plus, schémas simples). | P1 |
| B2 | Même risque : traces d'entraînement dédiées au tool calling | présent en FR-29, mais sans lien | Addendum (section risques) | Lier FR-29/FR-30 à ce risque dans une table de risques. | P3 |
| B3 | Oubli des capacités générales : LoRA de rang modéré | absent | Addendum E | Ajouter « rang LoRA modéré » comme réglage par défaut et variable de la campagne. | P2 |
| B4 | Oubli : mélange de 10 à 20 % de données génériques en français | affaibli (volumes dans addendum F, aucune exigence) | FR-29 | Ajouter dans FR-29 l'inclusion de 10 à 20 % de données génériques françaises. | P2 |
| B5 | Données synthétiques fausses : « vérification contre le corpus source » + relecture d'échantillon | affaibli | FR-30 | FR-30 ne rejoue que les traces d'outils ; ajouter la vérification contre le corpus source pour les réponses sourcées, comptes rendus et réécritures. | P2 |
| B6 | Index RAG trop lourd : sous-ensemble ciblé (service-public + catalogue data.gouv), vecteurs quantifiés, embedding plus léger | présent (addendum C) | — | Rien, sauf noter dans la section risques que c'est la parade de ce risque. | P3 |
| B7 | Réponses juridiques erronées : citation systématique + mention | présent (FR-3) | — | Rien. | — |
| B8 | Aucun registre de risques dans PRD ni addendum | absent | Addendum (nouvelle section « Risques et parades ») | Recopier les 7 risques, impacts et parades avec renvoi aux FR/NFR. | P2 |

## C. Choix des modèles

| # | Élément de la note | Statut | Où intégrer | Correction proposée | Prio |
|---|---|---|---|---|---|
| C1 | Shortlist de baseline : Ministral 3 3B, Granite 4.0 1B, SmolLM3 3B ; Ministral 3 8B = plafond de qualité ; témoin non européen Qwen ~4B | absent (le glossaire renvoie à la note) | Addendum (nouvelle section « Modèles candidats »), PRD §11 Q1 | Reprendre la shortlist, le rôle de chaque modèle et le témoin Qwen, car l'aval ne lit pas forcément la note. | P1 |
| C2 | Tableau des 9 modèles : paramètres, licence (Apache 2.0, « ouverte » pour CroissantLLM et Lucie), données publiées ou non, atouts, limites | absent | Addendum | Ajouter le tableau, y compris CroissantLLM, OLMo 2 1B, EuroLLM 1.7B, Lucie-7B (écartés : trop gros ou en retrait). | P2 |
| C3 | Règle de décision : choix final sur le jeu d'évaluation et le débit mesuré sur le PC cible, pas sur les benchmarks publics | affaibli | PRD §11 Q1 et SM-C1 | Le PRD dit « baseline et mesures » ; ajouter explicitement que les benchmarks publics ne tranchent pas. | P2 |
| C4 | Vérifications ouvertes : support Unsloth et llama.cpp de Ministral 3 3B (encodeur vision) ; qualité du français de Granite (12 langues) ; tool calling et données de post-entraînement de SmolLM3 | affaibli (encodeur vision en addendum E ; vérifications perdues) | Addendum E, PRD §11 | Ajouter ces vérifications comme questions ouvertes de la Baseline. | P2 |
| C5 | Ministral 3 8B : QLoRA à la limite des 8 Go de VRAM, lent sur CPU | absent | Addendum E | Noter la limite : le 8B sert de plafond d'évaluation, pas de cible d'entraînement. | P3 |
| C6 | Critère de souveraineté et d'auditabilité dans le choix du modèle (modèle entièrement ouvert = sources et licences traçables, contrôle de fuite du jeu d'évaluation) | absent | PRD §6.1 et §11 Q1 | Ajouter un critère de sélection « degré d'ouverture des données » ; la fuite du jeu d'évaluation dans le préentraînement n'est vérifiable que sur modèle entièrement ouvert. | P1 |
| C7 | Limite assumée : audit exhaustif de milliers de milliards de tokens hors de portée | absent | PRD §6.1 | Le noter pour ne pas sur-promettre l'auditabilité. | P3 |
| C8 | Granite : certification ISO 42001 de l'AIMS d'IBM, qui ne couvre ni le modèle ni l'application | absent | PRD §6.1, fiche modèle FR-37 | Interdire tout message commercial ou fiche modèle qui prête cette certification au modèle ou à l'Assistant. | P1 |
| C9 | Nuance sur la souveraineté culturelle : Mistral est français, mais le corpus de Ministral n'est pas publié ; l'ancrage vient du RAG et du fine-tuning sur données françaises | absent | PRD §1 (posture) et §6 | Ajouter la nuance : ne pas présenter le modèle de base comme garant de souveraineté culturelle. | P1 |
| C10 | Contraintes matérielles : entraînement QLoRA 4 bits sur RTX 3050 8 Go, séquences de 2 à 4k tokens | affaibli (RTX 3050 présente, longueur de séquence perdue) | Addendum E, §6.3 | Ajouter la longueur de séquence d'entraînement de 2 à 4k tokens. | P3 |

## D. Sources de données, licences, règles sur les générateurs

| # | Élément de la note | Statut | Où intégrer | Correction proposée | Prio |
|---|---|---|---|---|---|
| D1 | Claire French Dialogue (~160 M mots, CC BY-NC-SA) comme source d'entrées de transcriptions pour générer des comptes rendus | absent (FR-31 ne cite Claire que pour l'exclure) | Addendum F, FR-31, §11 | Dire d'où viennent les transcriptions de la version diffusée si Claire (NC) est exclue ; sinon les Données d'entraînement du compte rendu n'ont plus de source. Mentionner aussi la clause « share alike ». | P1 |
| D2 | Conditions Mistral (en vigueur au 25 septembre 2026) : §3.3 ne restreint que les sorties image ; sorties texte utilisables pour l'entraînement | affaibli (conclusion gardée, fondement perdu) | PRD §8, addendum | Ajouter la référence (§3.3, date de vérification) et exiger de revérifier avant chaque campagne de génération. | P1 |
| D3 | Éviter les modèles « Labs » / préversion « dont les données servent à l'entraînement de Mistral » | affaibli (interdiction gardée, motif perdu) | PRD §8 | Ajouter le motif : confidentialité des prompts et des sources. | P3 |
| D4 | Justification de l'exclusion de Claude : les sorties ne peuvent servir de cibles d'entraînement d'un modèle de génération de texte ouverte sans autorisation écrite (support Anthropic + Commercial Terms) ; ce SLM entre dans ce cas | affaibli | PRD §8 | Ajouter les deux références juridiques et la condition « sans autorisation écrite » (la levée de l'exclusion passe par un accord écrit). | P2 |
| D5 | Justification de l'exclusion de Gemini (Additional Terms : pas de développement de modèles concurrents) et usage possible comme juge | affaibli | PRD §8, FR-25 | §8 autorise Gemini comme Juge mais FR-25 ne liste que « Claude ou open-weight » ; harmoniser. | P2 |
| D6 | Repli local Qwen3.6-35B-A3B (Apache 2.0) et témoin Qwen ~4B « hors objectif de souveraineté » | affaibli | PRD §8 | Noter que ce repli est non européen, donc un compromis de souveraineté assumé. | P3 |
| D7 | AgentPublic : `sp_questions_corpus`, `MCQ-eval`, `piaf`, `retriever_dataset` ; licence « à vérifier par jeu » | affaibli | Addendum F, Registre FR-31 | `retriever_dataset` est perdu ; l'addendum cite `assistant_ia_questions_corpus`, absent de la note. Aligner la liste et noter la vérification de licence par jeu. | P3 |
| D8 | MediaTech : DOLE dans la liste des corpus ; licence Etalab 2.0 | affaibli | PRD §4.2, FR-31 | Ajouter DOLE à la liste (ou l'écarter explicitement) ; inscrire Etalab 2.0 et son obligation d'attribution au registre. | P3 |
| D9 | french_simplified : 333 paires, évaluation du langage clair uniquement, licence à vérifier | présent en partie (« évaluation seulement ») | Addendum F | Ajouter la taille (333) et la licence à vérifier ; elle limite la robustesse de l'évaluation langage clair. | P3 |
| D10 | Retour d'expérience llama-falc : projet FALC sur un 3B échoué faute de paires alignées (~22) ; qualité et volume du jeu priment sur le modèle | absent | Addendum F ou risques | Ajouter comme risque : volume et qualité du jeu de langage clair avant le choix du modèle. | P2 |
| D11 | Les traces de tool calling reposent sur les réponses réelles du serveur MCP (« Données Etalab ») | présent (FR-30) | — | Rien. | — |

## E. Critères d'évaluation

| # | Élément de la note | Statut | Où intégrer | Correction proposée | Prio |
|---|---|---|---|---|---|
| E1 | Recherche data.gouv : métriques = taux d'appels valides **et réponse exacte** | affaibli | SM-3, FR-24 | SM-3 ne mesure que l'appel valide ; ajouter « réponse exacte ». | P2 |
| E2 | Compte rendu : « couverture des décisions et actions » et absence d'invention | affaibli | SM-4, FR-13 | Seule l'absence d'invention est mesurée ; ajouter un critère de couverture (rappel des décisions et actions). | P1 |
| E3 | Questions : exactitude, présence et justesse de la source citée | présent (SM-2) | — | Rien. | — |
| E4 | Non-régression : « écart avec le modèle de base » | présent (SM-1, perte ≤ 3 points) | — | Rien. | — |
| E5 | Le fine-tuning n'est justifié que s'il bat la baseline (base + RAG + prompt système) | présent | — | Rien. | — |
| E6 | Le jeu d'évaluation vient des amorces AgentPublic + questions rédigées | affaibli | FR-24 | Le PRD dit seulement que Claude le rédige ; ajouter les amorces AgentPublic (hors Données d'entraînement). | P3 |
| E7 | Contrôle de fuite du jeu d'évaluation dans l'entraînement du modèle de base (permis par un modèle entièrement ouvert) | absent | FR-24 | FR-24 ne contrôle que les Données d'entraînement ; ajouter la contamination du préentraînement comme limite connue. | P2 |

## F. Idées qualitatives

| # | Élément de la note | Statut | Où intégrer | Correction proposée | Prio |
|---|---|---|---|---|---|
| F1 | Principe d'architecture : fine-tuning = comportement, RAG = savoir, MCP = fraîcheur ; « rien de data.gouv n'est mémorisé dans les poids » | présent en non-objectif et addendum A | — | Rien. | — |
| F2 | Posture souveraineté : modèle local, hors ligne, ancrage sur sources officielles, sans fournisseur d'IA externe | affaibli | PRD §1 | Le PRD défend la confidentialité mais pas la souveraineté ; ajouter un principe explicite, avec la nuance C9. | P2 |
| F3 | Le vrai travail porte sur les données comportementales (qui n'existent pas), pas sur le corpus RAG (qui existe déjà) | affaibli | PRD §4.12 | Ajouter la phrase pour cadrer l'effort des lots 1 et 2 et la priorité de FR-29/FR-30. | P3 |
| F4 | Le jeu d'évaluation « n'est jamais utilisé pour l'entraînement » | présent | — | Rien. | — |

## Synthèse

Nombre d'écarts à traiter : 43 lignes d'analyse, dont 36 écarts réels (hors lignes « présent », marquées « — »). Par priorité : 14 P1, 14 P2, 8 P3.

Les plus importants :
1. A1/A2/A3/A8 : les lots, la charge totale (21–38 j), le jalon go / no-go de la fin du lot 1 sont absents du PRD, alors que le périmètre a grossi (8 Tâches, 4 méthodes, 7 benchmarks).
2. C6/C8/C9 : la dimension souveraineté et auditabilité est absente, ainsi que les garde-fous sur l'ISO 42001 de Granite et sur la nuance de souveraineté culturelle de Ministral.
3. D1 : Claire (CC BY-NC-SA) est la source des transcriptions de comptes rendus ; le PRD l'exclut de la version diffusée sans remplaçant.
4. B1/B8 : le registre de risques et la parade « peu d'outils aux schémas simples » ont disparu (l'addendum expose 10 outils).
5. C1 : la shortlist de modèles et le rôle de chaque candidat (3B, 1B, SmolLM3, plafond 8B, témoin Qwen) ne figurent que dans la note.
