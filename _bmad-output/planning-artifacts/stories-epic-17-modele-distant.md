# Epic 17 — Modèle distant : mesure de qualité et mode hybride

Sources : D9 de `decisions.md` (option hybride souveraine, à l'étude) ; échanges du 21/10 avec Anaël. Indépendant de l'epic 16 (aucun fichier partagé avec le harnais v2, sauf la référence de modèle dans les runs d'évaluation).

But : montrer à la collectivité ce qu'un modèle plus gros apporte sur les mêmes tâches, avec le même banc, puis permettre à l'application d'appeler un endpoint externe (cible : GPU loué sur une infrastructure qualifiée SecNumCloud 3.2), MiniCPM5-2B local restant en mode dégradé.

Constat du 21/10 : aucune API LLM n'est elle-même qualifiée SecNumCloud (catalogue ANSSI du 15/09/2026, d'après une synthèse secondaire) ; Cloud Temple LLMaaS et Outscale LLMaaS tournent sur une infrastructure qualifiée mais sans libre-service. La démonstration se fait donc d'abord via OpenRouter, sur les jeux `dev*` (items fictifs, aucune donnée réelle), avec des modèles à poids ouverts que ces hébergeurs proposent aussi (Qwen3.6-27B, Mistral Small 4).

| Story | Titre | Nature |
|---|---|---|
| 17.1 ★ | `eval run --modele distant:<fournisseur>/<modèle>` : génération via une API compatible OpenAI | code (spec relue avant code : réseau, secrets, budget) |
| 17.2 | Mesure de qualité : Qwen3.6-27B puis Mistral Small 4 sur dev1 (puis dev2 après gel) | runs |
| 17.3 | Fiche de démonstration pour la collectivité (palier 1 local, palier 2 hybride, chiffres mesurés) | document |
| 17.4 | Application : mode hybride (fournisseurs externes en cascade, MiniCPM5-2B local en secours) | code (avancée au 21/10 pour la release v0.3.0) |
| 17.1b | Fournisseurs `mistral` (API directe) et `ovh` dans `eval run`, via les presets de 17.4 | code, après 17.4 |
| 17.5a | Données du comparatif des modèles (`slmsp compare fiche-app`) | code |
| 17.5b | Onglet « Modèles » de l'application (qualité, coût, vitesse) | code, après 17.4 |

## Règles
- Les sorties d'un modèle distant **n'entrent dans aucun jeu d'entraînement** (CGU des fournisseurs, D1) ; elles ne servent qu'à la mesure.
- Un seul fournisseur épinglé par modèle (pas de repli automatique d'OpenRouter vers un autre hébergeur), quantification consignée, collecte de données refusée (`data_collection = "deny"`) ; raisonnement désactivé, comme pour les modèles locaux (`reasoning = "off"`).
- Même harnais, mêmes prompts de tâche, même décodage (température 0, graine 42, `max_tokens` 1024) et même index local (bge-m3 sur le poste) que les modèles locaux, pour que `eval comparer` reste valable.
- Budget : campagne courante du registre (OpenRouter), réservation avant chaque appel, `--plafond-estime` obligatoire pour un modèle distant.

## 17.1 ★ — Modèle distant dans `eval run`
- Référence `distant:<fournisseur>/<modèle>` (fournisseur `openrouter` seulement dans cette story ; la table des fournisseurs admet ensuite un endpoint compatible OpenAI quelconque, par exemple Cloud Temple ou Albert, sans changer le code d'évaluation). Fiche de modèle distant dans `config/modeles-distants/<slug>.toml` : identifiant chez le fournisseur, hébergeur épinglé, quantification annoncée, protocole d'outils, `reasoning`, tarif (`config/tarifs.toml`).
- Génération : aucun llama-server de génération ; le serveur d'embedding local reste démarré (recherche Q inchangée). Les requêtes passent par la Passerelle réseau unique avec un profil dédié (`eval-distant`, POST vers l'hôte du fournisseur seulement), clé lue dans les secrets ; le garde-fou « génération sans réseau » est levé **seulement** pour une référence `distant:`, et consigné dans le run.
- Budget : réservation par appel dans le registre (usage `eval-distant`), plafond estimé exigé, arrêt propre au plafond (run reprenable par `--reprendre`).
- Le run consigne : référence, hébergeur effectif renvoyé par le fournisseur (refus si différent de l'hébergeur épinglé), quantification, coût réel, `finish_reason`, usage. `eval comparer` lit ces runs comme les autres.
- Fini quand : tests sur fixtures (fournisseur mocké : génération, outils RD, troncature, hébergeur inattendu refusé, budget réservé et plafond, reprise, aucun réseau pour `base:`/`ft:`/`lora:`) ; essai réel sur 2 items par l'orchestrateur.

## 17.2 — Mesures de qualité
- Qwen3.6-27B (OpenRouter, ~0,3 $ de génération + ~0,3 € de notation GLM sur dev1), puis Mistral Small 4 (aussi proposé par Cloud Temple et Outscale). dev2 après son gel (16.1).
- Comparaison par `eval comparer` contre la Baseline MiniCPM5-2B (54,5) et Qwen3.5-4B (54,6), par tâche, avec IC95 ; indicateurs D0 en plus (inventions CR/RE par item, abstention Q).
- Latence vue depuis le poste (premier token, débit) consignée, à titre indicatif : elle ne préjuge pas d'un endpoint souverain.

## 17.3 — Fiche de démonstration
Document court pour la collectivité : palier 1 (local, MiniCPM5-2B, pilote v1), palier 2 (hybride, endpoint sur infrastructure qualifiée), écarts mesurés par tâche, exemples réels d'items de dev1 côte à côte, conditions (périmètre de la qualification, sous-traitance RGPD, journalisation, mode dégradé, licence des poids). Les chiffres viennent des runs, cités par identifiant.

## 17.4 — Mode hybride dans l'application (après accord)
Endpoint externe configurable dans les Paramètres (URL, clé, modèle), Mode indiqué à l'écran, journal des Requêtes sortantes (FR existants), bascule automatique vers MiniCPM5-2B local si l'endpoint ne répond pas. Spec à écrire quand la collectivité aura choisi le palier 2.

## Vagues
| Vague | Stories en parallèle | Après |
|---|---|---|
| V0 | 17.1 ★ | spec relue avant code |
| V1 | 17.2 | 17.1 |
| V2 | 17.3 | 17.2 |
| — | 17.4 | décision de la collectivité |
