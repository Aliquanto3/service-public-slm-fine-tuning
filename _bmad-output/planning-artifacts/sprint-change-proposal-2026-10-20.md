# Sprint Change Proposal — méthodologie v2 (2026-10-20)

Source : `_bmad-output/implementation-artifacts/plan-methodo-2026-10-20.md` (validé par Anaël le 20/10 au matin, §7 bis). Mode : batch, run autonome (Anaël absent). Approbation : décisions du §7 bis ; ce document les transforme en stories sans élargir le périmètre.

## 1. Problème
Cinq fine-tunings MiniCPM5-2B restent sous la Baseline (41,1) ; LC est à 0 partout (fidélité) ; la base fait mieux que les cibles sur CR, LC, NR. Les juges tiers confirment le juge principal : le levier est la justesse des cibles au sens de la grille, pas la méthode (bilan : `archive/run-autonome-2026-10-19.md`).

## 2. Impact
- **Epics** : 9 (données d'entraînement prouvées) et 10/11 (runs, Comparatif) prolongés ; aucun epic clos rouvert. Les stories de ce changement sont hors `epics.md` (comme S1-S5), suivies dans `run-autonome.md`.
- **PRD / architecture** : inchangés sur le fond. Deux ajouts de règles, sans contredire D1 : (a) DeepSeek V4 Pro juge de **sélection** des données (sorties jamais cibles) ; (b) jeu de développement gelé `relu-llm`, jamais mesure finale. Grille du juge et jeu v1.1 : intacts.
- **Code** : `data` (génération vérifiée, juge de données, sélection, préférences), `evaluation` (jeu dev, statut de gel), `train/export` (DoRA Qwen3.5, ORPO CUDA, purge), `mistral` (réutilisation, conditions).
- **Budget** : campagne `methodo-v2-2026-10-20` ouverte (anthropic 40,5 €, mistral 10 €, openrouter 13,5 €).

## 3. Approche retenue
Ajustement direct (stories ajoutées), en deux étages (§4 bis du plan) : étage 1 = génération Mistral vérifiée (O6, avec O1, O5) puis M1 ; étage 2 (O2, O3, C5, E2, E3) seulement si la base reste meilleure sur certaines tâches. Effort : ~10 stories de code, ~15-25 € d'API sur l'étage 1. Risque principal : D1 (aucun texte rédigé par Claude ne doit atteindre un générateur) et sur-apprentissage du juge de test.

## 4. Stories

Convention : chaque story suit dev-story → second-avis → reviewer. ★ = spec relue avant le code. Les specs détaillées sont dans `implementation-artifacts/spec-<id>-*.md`.

### Correctifs
**C1 — Tests figés sur la config** (haute). Les 4 tests (`test_budgets_de_depart`, `test_critere_11_base_absente_non_creee`, `test_marge_raisonnement_preversion_seulement`, `test_attente_totale_bornee`) lisent la config ; invariants conservés. *Fini quand* : suite verte sur ces fichiers, aucune valeur de campagne figée.

**C2 — Jamais de réponse tronquée réutilisée** (haute). Une réponse journalisée `finish_reason=length` n'est jamais réutilisée ; `max_tokens` (et modèle, température, effort) entre dans la clé de réutilisation ; journaux anciens lisibles (réutilisés seulement si `stop`). *Fini quand* : tests sur journaux factices (tronquée → nouvel appel ; marge changée → nouvel appel).

**C3 — Export DoRA Qwen3.5** (moyenne). « Valeur non finie » à la fusion de `linear_attn.in_proj_qkv` (`runs/export/20261020-053854-ft-qwen3.5-0.8b-f4f4`). Diagnostiquer (norme de magnitude DoRA sur une couche fusionnée, dtype de fusion) ; fusion en fp32 ou refus explicite avant l'entraînement si non supporté. *Fini quand* : test de fusion DoRA sur une couche factice de forme `in_proj_qkv` sans NaN, ou refus en amont documenté.

**C4 — ORPO Qwen3.5-0.8B « CUDA device not ready »** (moyenne). Reproduire (`runs/train/20261020-061248-…-a0b4`), isoler (chargement 4 bits + modèle de référence ? pin_memory ? Triton/linear attention ?). Correctif ou contournement configurable. *Fini quand* : cause écrite et M4 Qwen3.5-0.8B qui démarre (essai court par l'orchestrateur, GPU).

**C5 ★ — Préférences depuis des candidats notés** (moyenne, étage 2). `--preferences` construit (choisi = meilleur noté, rejeté = moins bon noté, écart minimal) au lieu de « cible vs base ». Spec : `spec-c5-preferences-notees.md`.

**C6 — Coût « de cette session »** (basse). Lire le registre par run (`run_id` de la réservation) au lieu de la différence de totaux, faux quand deux notations se chevauchent.

**C7 — Juges tiers, items CR en échec** (basse). Rejouer (cache) et diagnostiquer les 61-64 paires CR en échec (longueur de prompt ? schéma ?). *Fini quand* : cause écrite, taux d'échec CR < 5 % sur un rejeu (appel payant par l'orchestrateur).

**C8 — Purge des intermédiaires et contrôle disque** (moyenne). `export --purger-intermediaires` (supprime `hf-f16/` et `modele-f16.gguf` après succès et contrôle du Q4_K_M) et commande `export purger --depuis <export_run_id>` pour les exports déjà notés (refus si aucune notation ne référence l'export) ; contrôle d'espace libre avant export (seuil configurable, défaut estimé depuis la taille du modèle) avec refus clair. Autorisé par Anaël (§7 bis) pour les runs notés ; Q4_K_M et runs d'entraînement gardés.

**C9 — Conditions Mistral, vérification quotidienne** (basse). Commande `mistral conditions verifier` : GET de la page, SHA-256 ; inchangé → `conditions_verifiees_le` mis à la date du jour (`donnees.toml`) ; changé → blocage de la génération et alerte consignée. Appelée automatiquement au démarrage d'une génération si la date n'est pas celle du jour.

### Outillage
**O1 ★ — Juge de données** (`data juger`). DeepSeek V4 Pro via OpenRouter, grille adaptée aux faits du scénario, sans référence d'évaluation. Spec : `spec-o1-juge-donnees.md`.

**O2 — Candidats multiples** (étage 2). K sorties de la base locale (llama.cpp cuda, températures variées) + cible Mistral existante (+ option second générateur OpenRouter, E4) par entrée ; sortie `candidats.jsonl` (entrée, source, texte, paramètres). Aucun texte de Claude.

**O3 ★ — Sélection** (`data build --selection`, étage 2). Spec : `spec-o3-selection.md`.

**O4 ★ — Jeu de développement** (~160 items, 20 par tâche, disjoint de v1.1 et du jeu d'entraînement), fiabilisé par Claude + DeepSeek + GLM, gelé `relu-llm` ; `eval run --jeu dev` noté par DeepSeek. Spec : `spec-o4-jeu-dev.md`.

**O5 — Alignement LC (et entrées)** : même consigne d'Agent qu'à l'évaluation dans les entrées LC d'entraînement (gabarit d'entrée de la tâche, tiré du système de prompts de l'évaluation, pas rédigé au cas par cas) ; longueur des textes sources LC comparable à l'évaluation (filtre ou sélection de sources par longueur, médiane cible = médiane v1.1 ± 30 %). Vérifier aussi CR, CT, RE. *Fini quand* : rapport de comparaison entraînement / évaluation (gabarits, médianes de longueur) et build d'un jeu aligné sur fixture.

**O6 ★ — Génération Mistral vérifiée** (étage 1) : tests déterministes nourris par la source (transcription / texte / amorce), juge DeepSeek (O1), régénération avec motif (2 essais), puis écart. Spec : `spec-o6-generation-verifiee.md`.

### Expériences (lancées par l'orchestrateur)
| # | Expérience | Remarque de cadrage |
|---|---|---|
| E1 | Variance | Le décodage d'évaluation est glouton (graine 42, température 0) : deux générations d'un même GGUF sont identiques. E1 mesure donc (a) la variance d'**entraînement** : M1 MiniCPM5-2B v14 réentraîné avec la graine 4321, noté (~3 €) ; (b) la variance d'**échantillonnage des items** : bootstrap apparié sur les notations existantes (gratuit). Seuil de décision = max des deux. |
| E2 | RFT / auto-distillation MiniCPM5-2B | étage 2 (O2, O3) |
| E3 | ORPO sur paires notées après E2 | étage 2 (C5) |
| E4 | DeepSeek V4 Pro générateur candidat | dans E2 |
| E5 | Routage par tâche choisi sur le jeu dev, mesuré une fois sur v1.1 | après O4 |
| E6 | Report sur Qwen3.5-0.8B et 2B | après la meilleure recette |

## 5. Ordre et passation
1. C1, C2 (main rouge) ; E1 dès que le GPU est libre.
2. Specs O1, O6, O4, O3, C5 relues avant code. Puis O1 → O6 avec O5 ; O4 en parallèle ; C8 tôt (disque à 96 %).
3. Génération vérifiée CR, CT, LC (étage 1, ~1 € Mistral + ~1 € OpenRouter) → jeu v17 → M1 MiniCPM5-2B v17 → notation jeu dev (DeepSeek) et v1.1 (Claude, mesure finale une fois).
4. Étage 2 seulement si la base reste meilleure sur des tâches (E2, E3) ; E5, E6 ensuite.
Portée : **modérée** (réorganisation du backlog, exécution par les agents de dev). Succès : un M1 au-dessus de sa Baseline au-delà du bruit E1, sans baisse de NR supérieure au bruit.
