# Assistant SP : fiche de démonstration pour la collectivité

Version du 21/10/2026 (story 17.3). Document de travail pour élus, DSI et équipes techniques. Les chiffres viennent de mesures du projet ; quand une valeur manque, elle est écrite « non mesuré ».

## 1. Le besoin et l'outil

Les agents d'accueil et les services passent du temps à retrouver une règle sur service-public.fr, à rédiger un compte rendu ou un courrier, à simplifier un texte. **Assistant SP** est une application installée sur le poste de l'agent. Elle sait :
- répondre à une question en citant les pages de service-public.fr ;
- chercher des jeux de données sur data.gouv.fr ;
- rédiger un compte rendu de réunion, un courrier type, un résumé ;
- passer un texte en langage clair, corriger l'orthographe, traduire.

Le texte produit est toujours un **brouillon à relire**. L'application affiche ses sources et peut vérifier une réponse en ligne.

## 2. Deux paliers

| | Palier 1 : tout sur le poste | Palier 2 : hybride |
|---|---|---|
| Où tourne le modèle | Sur le PC de l'agent (MiniCPM5-2B, licence Apache 2.0) | Sur un serveur GPU loué, hors du poste |
| Ce qui reste sur le poste | Tout | L'application, l'index des pages publiques, l'historique |
| Ce qui sort du poste | Rien. Fonctionne hors ligne | La demande et les extraits utiles, envoyés au modèle distant |
| Coût d'API | 0 € | Au volume (voir §3) ; plafond de dépense réglable |
| Cible | Pilote v1 | Infrastructure qualifiée SecNumCloud 3.2, mutualisée avec d'autres usages de la collectivité |
| Si le réseau tombe | Sans objet | Bascule automatique sur le modèle local ; plusieurs fournisseurs peuvent être mis en cascade avant ce secours |

Le palier 2 n'est **pas décidé** : c'est une option si le palier 1 se révèle insuffisant après le pilote. L'application sait déjà fonctionner en mode hybride (version 0.3.0).

## 3. Chiffres mesurés

**Ce que mesure la Qualité.** C'est la moyenne de 8 scores de tâche (0 à 100), calculée sur le jeu de développement « dev1 » : 159 items fictifs, notés par un modèle-juge (GLM). Le bruit de mesure est d'environ ±5 points : un écart plus petit que son intervalle de confiance à 95 % (IC95) ne se distingue pas du hasard.

| Modèle | Où | Qualité | Écart à MiniCPM5-2B [IC95] | Coût pour 1 000 demandes | Débit (tokens/s) | Premier token |
|---|---|---|---|---|---|---|
| MiniCPM5-2B (référence) | Poste | 54,3 | | 0 € d'API | 12,1 | 0,71 s |
| Mistral Small 4 | API Mistral (France) | 58,8 | +4,5 [−0,5 ; +10,8] | 0,43 € | 197 | 0,57 s |
| Qwen3.6-27B | OpenRouter, hébergeur aux États-Unis | 71,6 | +17,4 [+12,0 ; +23,9] | 1,16 € | 90 | 0,56 s |
| Qwen3.8-27B | OpenRouter, hébergeur aux États-Unis | 74,1 | +19,9 [+15,0 ; +25,6] | 1,02 € | 38 | 0,72 s |

Par tâche (Q question, RD recherche de données, CR compte rendu, LC langage clair, CO correction, RE résumé, CT courrier type, NR non-régression) :

| Modèle | Q | RD | CR | LC | CO | RE | CT | NR |
|---|---|---|---|---|---|---|---|---|
| MiniCPM5-2B | 15,0 | 74,8 | 73,6 | 50,0 | 72,1 | 58,5 | 45,0 | 45,0 |
| Mistral Small 4 | 15,0 | 88,6 | 79,9 | 10,0 | 90,5 | 68,5 | 32,5 | 85,0 |
| Qwen3.6-27B | 35,0 | 87,4 | 86,5 | 30,0 | 96,9 | 89,6 | 52,5 | 95,0 |
| Qwen3.8-27B | 40,0 | 88,6 | 88,3 | 50,0 | 98,9 | 78,5 | 58,8 | 90,0 |

À retenir :
- Un modèle de 27 milliards de paramètres écrit nettement mieux que MiniCPM5-2B sur les comptes rendus, les résumés, la correction et la recherche de données. L'écart global (+17 à +20 points) dépasse largement le bruit.
- Les questions (Q) restent faibles partout (15 à 40 sur 100) ; le langage clair (LC) n'est pas amélioré par les modèles distants (50,0 pour MiniCPM5-2B, Qwen3.8-27B ; 10,0 à 30,0 pour les deux autres). Avec 20 items par tâche, un écart par tâche reste fragile.
- Mistral Small 4 n'est pas distinguable de MiniCPM5-2B au niveau global (l'IC95 inclut 0).
- Traduction : non mesuré (aucune tâche de traduction dans dev1).
- Énergie du poste et matériel : non mesurés. Coût d'un serveur GPU loué à la durée (hors API à la requête) : non mesuré.

**Limites, à dire clairement.**
- dev1 est un jeu **rédigé par le projet**, fictif, relu par un modèle de langage (statut `relu-llm`) et **non relu par un humain**. Ce n'est pas une mesure sur de vraies demandes.
- Le juge est un modèle : ses notes ne se comparent qu'entre modèles notés par lui sur le même jeu.
- Les vitesses ont été prises sur le **PC de développement** (MiniCPM5-2B : processeur seul, 4 threads, quantifié q4_k_m) et, pour le cloud, depuis ce même poste via Internet. Elles ne préjugent ni du PC cible ni d'un serveur souverain.
- Les modèles distants ont été mesurés chez des hébergeurs **qui ne sont pas qualifiés SecNumCloud** (États-Unis pour Qwen). Le modèle et l'hébergeur d'un éventuel palier 2 ne sont pas encore mesurés. Les sorties de ces modèles ne servent qu'à la mesure ; elles n'entrent dans aucune donnée d'entraînement.

<sub>Sources : `src/slmsp/app/ui/donnees/comparatif-modeles.json` (généré le 21/10/2026, jeu dev1, juge GLM). Notations : MiniCPM5-2B `20261021-095813-minicpm5-2b-47d5` ; Mistral Small `20261021-113707-distant-mistral-small-mistral-938a` ; Qwen3.6-27B `20261021-094134-distant-qwen3.6-27b-fc13` ; Qwen3.8-27B `20261021-224856-distant-qwen3.8-27b-1834`. Générations distantes : `20261021-112139-distant-mistral-small-mistral-0b86`, `20261021-092032-distant-qwen3.6-27b-3ae2`, `20261021-191924-distant-qwen3.8-27b-4ab7` ; vitesse du poste : mesure `20261021-023836-h-ram-f89e`. Journal : `_bmad-output/implementation-artifacts/run-autonome.md`. Coûts : génération seule (juge non compris), relances et appels d'outils compris, tarifs relevés le 21/10/2026.</sub>

## 4. Exemples côte à côte (jeu dev1)

Le premier item de chaque tâche (Q-501, CR-501), choisi sans tri. Génération MiniCPM5-2B : `20261020-163743-minicpm5-2b-f9fc` ; Qwen3.8-27B : `20261021-191924-distant-qwen3.8-27b-4ab7`.

**Question Q-501** (« Un homme sans domicile stable est domicilié au CCAS depuis bientôt un an. Il demande combien de temps vaut sa domiciliation et s'il peut la prolonger. »)

| MiniCPM5-2B (poste) | Qwen3.8-27B (distant) |
|---|---|
| « La domiciliation est accordée pour une durée de 1 an, renouvelable. […] il est recommandé de faire votre demande de renouvellement au moins 2 mois avant la fin de validité […] [1] » (327 caractères) | Réponse structurée en trois parties (durée, renouvellement, obligations), 1 221 caractères, qui ajoute notamment : « au moins 1 fois tous les 3 mois » de contact avec le CCAS [4] |
| Juge : exactitude 2, source 1 (notes maximales) ; aucune invention relevée. | Juge : mêmes notes sur l'exactitude et la source, mais **4 inventions relevées** (dont l'obligation de contact tous les 3 mois et la mention « Ne vaut pas avis juridique » absente). |

Lecture : ici, le petit modèle est plus court et suffisant ; le grand modèle en dit plus, et le juge lui reproche des ajouts. Plus de texte n'est pas toujours mieux.

**Compte rendu CR-501** (réunion de service Urbanisme du 8 octobre 2026, notes brutes en entrée)

| MiniCPM5-2B (poste) | Qwen3.8-27B (distant) |
|---|---|
| Sections Objet, Participants, Points abordés, Décisions, Actions, « Points ambigus ou incomplets » (3e instructeur, atelier en suspens, date corrigée de la formation). 1 567 caractères. | Compte rendu rédigé en phrases, avec date, lieu, absent excusé, décisions et actions par point. 2 968 caractères. |
| Juge : les 7 éléments attendus présents (3 décisions, 4 actions), aucune invention, structure conforme. | Juge : les 7 éléments attendus présents, aucune invention, structure conforme. |

Lecture : sur cet item, les deux sont jugés complets. L'écart moyen de la tâche CR (73,6 contre 88,3) vient d'autres items, pas de celui-ci. Les verdicts : `runs/eval-notation/20261021-095813-minicpm5-2b-47d5` et `runs/eval-notation/20261021-224856-distant-qwen3.8-27b-1834`.

## 5. Observabilité et maîtrise

L'application (version 0.3.0 et suivantes) rend visible ce que fait le modèle. Un onglet « Observabilité » est destiné à la DSI.
- **Par réponse** : une ligne « Détails » donne le modèle, les tokens d'entrée et de sortie, la durée, le coût (0 € en local), l'énergie et le CO₂e estimés.
- **Totaux** du jour et du mois par modèle et par fournisseur, derniers appels, **export CSV**. Ni le texte des demandes, ni celui des réponses, ni les clés ne sont enregistrés dans ces mesures.
- **Plafond de dépense** par fournisseur externe, réglable dans les Paramètres (2 € par mois par défaut, 0 pour désactiver). Avant chaque appel, le coût maximal possible est comparé au cumul du mois : s'il dépasse le plafond, l'appel n'est pas envoyé, la cascade passe au fournisseur suivant, puis au modèle local. Un modèle sans tarif connu est sauté.
- **Journal des requêtes sortantes** : tout appel vers l'extérieur est tracé, et le mode en cours est indiqué à l'écran.
- **Énergie et CO₂e** : estimations selon la méthode EcoLogits (version relevée le 21/10/2026), toujours présentées avec une fourchette. Exemple de calcul de la revue : 2 000 tokens en entrée, 300 en sortie, 3 s, Qwen3.6-27B : 0,0225 Wh et 0,0083 g CO₂e (fourchette 0,0206 à 0,0393 Wh). En local : puissance du poste supposée à 25 W (réglable), mix électrique France de 52 g/kWh ; poste non instrumenté. Les paramètres de certains modèles (Mistral Small 4) sont à vérifier.

Limites : les coûts sont des calculs à partir des tarifs relevés, non des factures ; l'horloge du poste fixe le mois du plafond et n'est pas infalsifiable.

## 6. Conditions avant le palier 2

1. **Périmètre de la qualification.** SecNumCloud qualifie une offre d'hébergement, pas un modèle. Il faut vérifier que l'offre **GPU elle-même** est dans le périmètre qualifié. D'après une synthèse secondaire, **aucune API de modèle de langage n'était qualifiée SecNumCloud au 15/09/2026** : à confirmer auprès de l'ANSSI et du fournisseur avant toute décision.
2. **RGPD.** Contrat de sous-traitance signé, localisation des données, et **absence de journalisation des demandes** (prompts) côté fournisseur, par écrit.
3. **Isolation** entre les cas d'usage de la collectivité sur le serveur mutualisé (mémoire, journaux, clés).
4. **Licence des poids.** Modèle à poids ouverts sous licence compatible (les modèles mesurés ici sont sous Apache 2.0) ; vérifier celle du modèle retenu.
5. **Mode dégradé.** Bascule sur le modèle local si le réseau ou le fournisseur tombe : prévue dans l'application. La qualité retombe alors au niveau du palier 1 ; à tester en conditions réelles.
6. **Mesure du modèle retenu** avec le même banc, sur dev1 puis sur le second jeu dev2 (160 items, gelé le 21/10), avant tout engagement. Les chiffres du §3 sont ceux de modèles testés chez d'autres hébergeurs ; ils ne valent pas pour le futur endpoint.

## 7. Recommandation

- **Lancer le pilote v1 en palier 1** (tout sur le poste), avec les garde-fous : sources affichées, vérification en ligne, brouillons toujours relus par l'agent.
- **Décider du palier 2 sur mesures** : modèle et hébergeur retenus, mesurés avec le même banc, et conditions du §6 levées par écrit.
- Relire par des agents de la collectivité un échantillon de réponses du pilote : c'est la seule mesure qui comptera vraiment.
