# Méthodologie v2 : faire réellement progresser les SLM sur les tâches secteur public

Rédigé le 2026-10-20 au matin, après la campagne v11 et le run autonome de nuit (`etat-campagne-v11.md`, `run-autonome.md`, bilan en fin de fichier). À valider par Anaël avant toute exécution.

## 1. Ce que les expériences établissent

| Constat | Preuve |
|---|---|
| Le juge principal (Claude Opus) est fiable sur les critères du score. | Juges tiers DeepSeek V4 Pro et GLM-5.3 sur 6 notations : accord avec le principal 94-98 % (CR invention), 98-99 % (CT), 74-85 % (LC fidélité), 89-93 % (LC termes), 76-86 % (RE). Le kappa 0,00 venait du second juge Mistral sur 3 à 5 items. |
| Les cibles d'entraînement font le résultat, pas la méthode. | v11 → v14 (cibles alignées sur la grille) : CT 13 → 47, CR 22 → 34 (MiniCPM). lr 2e-4 → 1e-4 : 36,7 → 35,4 (bruit). |
| Une cible « plausible » n'est pas une cible « juste au sens de la grille ». | LC : 4 cibles v14 sur 8 relues violent la fidélité (obligation reformulée, condition supprimée, conseil ajouté) ; LC reste à 0 dans tous les fine-tunings. |
| On apprend au modèle des choses que la base fait déjà mieux. | Baseline > fine-tuné sur CR, LC, NR, Q dans tous les runs ; gains seulement en RD, CO (et CT avec v14). |
| Les paires ORPO actuelles vont dans le mauvais sens pour certaines tâches. | `--preferences` prend la sortie de la base comme *rejetée* ; or la base est meilleure en LC, CR, NR. |
| Écart entraînement / évaluation. | LC : la consigne de l'Agent est présente à l'évaluation, absente à l'entraînement ; entrées 2-3 fois plus courtes. |
| Le jeu d'évaluation est petit : 15 à 60 items par tâche. | Des écarts de 1 à 2 points de qualité ne sont pas interprétables ; nous n'avons aucune mesure de variance. |
| Choisir sur le jeu de test le surajuste. | L'« adaptateur par tâche » (≈ 45,2) est calculé en choisissant la meilleure source par tâche sur v1.1 lui-même. |
| Générateur : Mistral Large 3 suffit pour la forme ; Large 4 (préversion) est lent, coûteux en raisonnement, limité en débit. | 4 000-5 600 tokens de raisonnement par CR, ReadTimeout à 180 s, puis 429. |

## 2. Principes de la méthodologie v2

1. **Générer, vérifier, sélectionner** (rejection sampling / RFT) au lieu de « générer et nettoyer » : chaque entrée d'entraînement reçoit plusieurs candidats, notés par un juge selon la grille, et seul le meilleur, s'il passe un seuil, devient cible.
2. **Ne jamais entraîner à faire moins bien que la base** : la base locale est un candidat comme les autres (auto-distillation). Si sa sortie gagne, c'est elle la cible : on garde son style là où il est bon (moins d'oubli) et on corrige seulement là où elle échoue.
3. **Juge de sélection ≠ juge de test** : la sélection des données utilise DeepSeek V4 Pro (85 à 98 % d'accord avec le principal, ~10 fois moins cher), pour ne pas sur-apprendre le juge qui note le test (Claude). Claude reste juge du test seulement (D1 : Claude ne génère jamais de données).
4. **Préférences notées par le juge** : paires ORPO/DPO = meilleur candidat (choisi) contre moins bon candidat noté (rejeté), quelle que soit leur source. Plus de « base = rejetée » par principe.
5. **Séparer développement et test** : un jeu de développement (validation), construit hors v1.1 et noté par DeepSeek, sert à toutes les décisions (hyperparamètres, mélange, routage) ; v1.1 (gelé) ne sert qu'à la mesure finale, une fois par configuration retenue.
6. **Décider sur des écarts significatifs** : mesurer la variance (deux générations de la même configuration) et exiger un gain supérieur à ce bruit.
7. **Aligner entraînement et évaluation** : mêmes gabarits, mêmes consignes d'Agent, mêmes longueurs d'entrée.

## 3. Correctifs (stories, avant toute expérience)

| # | Story | Gravité |
|---|---|---|
| C1 | Réaligner les 4 tests cassés par la config de nuit (`test_budgets_de_depart`, `test_critere_11_base_absente_non_creee`, `test_marge_raisonnement_preversion_seulement`, `test_attente_totale_bornee`) : lire les valeurs de la config au lieu de les figer. | haute (main rouge) |
| C2 | Ne jamais réutiliser une réponse journalisée tronquée (`finish_reason=length`) ; inclure `max_tokens` dans la clé de réutilisation. | haute |
| C3 | Export M3 DoRA de Qwen3.5 : « valeur non finie » à la fusion de `linear_attn.in_proj_qkv` (export `20261020-053854-ft-qwen3.5-0.8b-f4f4`). | moyenne |
| C4 | ORPO sur Qwen3.5-0.8B : « CUDA driver error: device not ready » au démarrage (`runs/train/20261020-061248-…-a0b4`), reproductible. | moyenne |
| C5 | `--preferences` : paires construites depuis des candidats notés (choisi = meilleur, rejeté = moins bon), au lieu de « cible vs base ». Remplacée par l'outillage de §4 si E2 est retenue. | moyenne |
| C6 | Coût « de cette session » faux quand deux notations se chevauchent (lire le registre par run). | basse |
| C7 | Juges tiers : items CR en échec (61-64 paires sur 150) ; rejouer et diagnostiquer (prompts longs ?). | basse |
| C8 | Export : option de purge des intermédiaires (`hf-f16`, `modele-f16.gguf`) après succès, et contrôle d'espace disque avant chaque export (le disque a saturé deux fois). | moyenne |
| C9 | Conditions Mistral : vérification quotidienne automatique (GET + SHA ; si inchangé, mise à jour de la date ; sinon blocage et alerte). | basse |

## 4. Outillage nouveau (stories)

| # | Story | Contenu |
|---|---|---|
| O1 | **Juge de données** (`data juger`) | Noter des candidats d'entraînement avec la grille, par DeepSeek V4 Pro (client OpenRouter de S3), sans référence d'évaluation : la grille est adaptée aux champs connus du scénario de seed (décisions, actions, informations à conserver, éléments obligatoires). Sortie : notes par critère, journal, budget `openrouter`. |
| O2 | **Candidats multiples** (`data candidats`) | Pour chaque entrée d'entraînement : K sorties de la base locale (llama.cpp cuda, températures variées), la cible Mistral existante, et en option une cible d'un second générateur. |
| O3 | **Sélection** (`data build --selection`) | Cible = meilleur candidat noté s'il passe le seuil de la tâche, sinon ligne écartée ; MANIFEST : source du gagnant, notes, part de la base. Paires de préférence = meilleur contre moins bon (écart minimal de note). |
| O4 | **Jeu de développement** | ~150 items (≈20 par tâche) construits comme le jeu v1.1 mais disjoints, notés par DeepSeek ; commande `eval run --jeu dev`. Gel par Anaël. |
| O5 | **Alignement LC** | Consigne d'Agent dans les entrées LC d'entraînement ; entrées de longueur comparable à l'évaluation. |

## 4 bis. Ordre retenu après échange avec Anaël (20/10) : deux étages
**Étage 1 (d'abord) : génération Mistral vérifiée et régénérée** — une story « O6 » qui regroupe :
- tests déterministes étendus, nourris par les faits du scénario de seed : CR, chaque décision et action présente avec responsable et échéance connus, aucun nom ni date hors des notes ; LC, marqueurs de condition et d'obligation de l'entrée conservés (si, sauf, uniquement, au plus tard, doit, peut, ne peut pas), aucun nombre ni date nouveaux, pas de formule de conseil ; CT, blocs du format administratif dans l'ordre, emplacements pour les informations inconnues ;
- juge DeepSeek V4 Pro (grille adaptée aux faits du scénario) pour le fond que les tests ne voient pas (O1) ;
- boucle : cible refusée → régénérée par Mistral avec le motif du refus en consigne (2 à 3 essais), puis écartée. D1 respecté : les motifs viennent des tests ou de DeepSeek, jamais de Claude.
Coût estimé : ~1 € OpenRouter + ~1 € Mistral pour CR, CT, LC. Puis M1 MiniCPM5-2B sur ce jeu vérifié, aligné (O5).
**Étage 2 (si la base reste meilleure sur certaines tâches)** : candidats de la base locale (O2), sélection (O3), paires notées (C5), soit E2 et E3.

## 5. Expériences proposées (ordre, coût, décision attendue)

| # | Expérience | Coût estimé | Question |
|---|---|---|---|
| E1 | Variance : 2 générations (graines différentes) de la Baseline MiniCPM et de M1 v14, notées par Claude. | ~12 € Anthropic | Quel écart de qualité est du bruit ? (fixe le seuil de décision) |
| E2 | **RFT / auto-distillation** sur MiniCPM5-2B : candidats = 4 sorties de la base + cible Mistral v14 ; sélection par DeepSeek ; M1 sur les gagnants. | ~6-8 € OpenRouter, GPU ~3 h, 1 notation ~3 € | Gagne-t-on sans perdre LC, CR, NR ? |
| E3 | ORPO sur paires notées (meilleur vs moins bon) après le SFT de E2. | ~3 € (notation) | La préférence ajoute-t-elle au SFT ? |
| E4 | Générateur : DeepSeek V4 Pro vs Mistral Large 3 comme candidat supplémentaire dans E2 (part des gagnants par source). | ~2-4 € OpenRouter | Faut-il changer de générateur ? (décision d'Anaël sur la provenance) |
| E5 | Routage par tâche (Baseline ou adaptateur) choisi **sur le jeu de développement**, puis mesuré une fois sur v1.1. | ~3 € | Le gain du routage tient-il hors sélection sur le test ? |
| E6 | Report sur Qwen3.5-0.8B et Qwen3.5-2B de la meilleure recette. | ~3 € par modèle | La recette se généralise-t-elle ? |

Budget total indicatif : Anthropic ~25-30 €, OpenRouter ~10-15 €, Mistral ~0-5 €.

## 6. Règles de décision révisées (à valider)
- Une configuration n'est retenue que si son gain de qualité dépasse le bruit mesuré en E1, sur le jeu de développement, sans baisse supérieure à ce bruit sur NR (non-régression).
- Mesure finale sur v1.1 une seule fois par configuration retenue.
- M3/M4 ne sont lancés qu'après une recette SFT gagnante (E2) ; M4 utilise les paires notées (C5/O3).
- Benchmarks et mesures CPU : inchangés (critère de gain, puis machine au repos).

## 7. Décisions qui reviennent à Anaël
1. Valider les principes 1 à 7, en particulier l'usage de DeepSeek comme juge de sélection des données (provenance chinoise, sortie non utilisée comme cible) et l'auto-distillation depuis la base.
2. Autoriser un générateur non Mistral comme candidat (E4) ou rester sur Mistral.
3. Budgets : Anthropic (rechargé de 36 €), OpenRouter (+10 € ?).
4. Purge des intermédiaires d'export (C8) et pratique de la nuit (suppressions faites, consignées dans `run-autonome.md`).
5. Relecture du jeu de développement (O4) avant gel.
