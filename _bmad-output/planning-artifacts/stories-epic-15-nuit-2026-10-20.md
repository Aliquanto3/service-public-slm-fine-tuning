# Epic 15 — Run de nuit du 20-21/10 : routage, interpolation, sélection de candidats

Source : `../implementation-artifacts/plan-nuit-2026-10-20.md` (version 2, réponses d'Anaël au §9). Consignes des sous-agents : `../implementation-artifacts/consignes-sous-agents-2026-10-20.md` (inchangées : worktrees, D1, aucun appel payant, pas de suite complète locale).

| Story | Plan | Titre |
|---|---|---|
| 15.1 | N1 | `eval composer` : routage par tâche à partir de runs existants |
| 15.2 | N2 | Candidats multiples (O2) : base locale échantillonnée + DeepSeek pour LC |
| 15.3 ★ | N3 | Sélection (O3) : `data build --selection` |
| 15.4 | N4 | Second juge désactivé pour tout jeu `dev*` |
| 15.5 | N5 | dev2 : +20 items par tâche |
| 15.6 | N6 | Adaptateur en LoRA GGUF, génération et mesure avec `--lora-scaled` |

## 15.1 (N1) — `eval composer`
`slmsp eval composer --route TACHE=NOTATION_RUN_ID ... --defaut NOTATION_RUN_ID [--marque deja-consulte]` crée un run de notation **composé** (lecture seule des runs sources, aucun appel) : pour chaque tâche, les verdicts et Scores de Tâche du run routé, sinon du run par défaut.
- Refus (erreur claire, aucun run écrit) si les runs sources diffèrent par : jeu et sa version (même liste d'items par tâche), grille du juge (SHA), juge principal (modèle), version des prompts de tâche, ou s'ils ne sont pas `ok`.
- Le run composé porte la provenance (route par tâche, runs sources, marque `deja-consulte` le cas échéant) et des scores au **même format** que ceux d'un run de notation, pour que `eval comparer` le lise sans changement (bootstrap apparié composé contre base).
- Fini quand : tests sur fixtures (composition, chaque motif de refus, lecture par `eval comparer`, marque consignée) ; aide CLI ; aucune modification des runs sources.

## 15.2 (N2) — Candidats multiples (O2)
Contrat de sortie : `spec-o3-selection.md` §« Contrat attendu de O2 » (`candidats.jsonl`, aucun texte, texte relu dans son journal).
- `slmsp data candidats --build BUILD_RUN_ID --taches CR,RE,LC --base SLUG --temperatures 0.3,0.7 [--deepseek-taches LC] [--variante cuda] [--plafond-estime EUR]`.
- Candidats de la base : llama-server local (GGUF Q4_K_M de la base, comme `preferences.py`), **exactement la conversation d'entraînement** de chaque ligne (prompt de tâche + entrée), une sortie par température, graine consignée ; journal `generations-locales.sqlite` (même schéma et même contrôle d'octets que les paires ORPO) ; une sortie tronquée (`finish_reason=length`) est journalisée mais marquée et exclue des candidats (C2).
- Candidat Mistral : la cible existante de la ligne (`mistral:<appel_id>`), sans nouvel appel.
- Candidat DeepSeek (LC seulement) : générateur OpenRouter existant (usage `generateur-openrouter`, budget réservé avant appel, plafond), même conversation, journal OpenRouter des générateurs.
- Idempotent et reprenable (un candidat déjà journalisé n'est pas regénéré). Les verdicts restent produits par `data juger` (O1), qui doit accepter `candidats.jsonl` en entrée et un juge choisi (`--juge deepseek|kimi`, Kimi = juge croisé, troisième famille, décision d'Anaël du 20/10) ; ajouter `kimi` (modèle OpenRouter Kimi courant, tarifs dans `tarifs.toml`) si absent.
- D1 : aucun texte rédigé par Claude dans les gabarits ; fixtures factices.
- Fini quand : tests sur fixtures (base mockée, OpenRouter mocké) : contrat de `candidats.jsonl`, conversation identique à celle du build, tronqués exclus, reprise, budget réservé, `data juger` sur candidats avec les deux juges.

## 15.3 ★ (N3) — Sélection (O3)
Spec : `../implementation-artifacts/spec-o3-selection.md` (relue le 20/10), avec ces amendements de la nuit (à relire avant code) :
- Règle 5 : le juge croisé des candidats DeepSeek est **Kimi** (OpenRouter), pas GLM (GLM note dev1 ; il ne doit pas juger ce qui sera appris). Score retenu = minimum des deux ; sans verdict Kimi valide, le candidat DeepSeek est ignoré et compté.
- Règle 7 : usage **recherche** pour les sorties de la base MiniCPM5-2B (décision d'Anaël du 20/10) ; entrée de Registre `slm:minicpm5-2b` (licence du Modèle de base, à lire dans sa fiche) en usage `recherche` ; le jeu produit est marqué `recherche`.
- Règle 9 (paires) : **reportée** avec C5 ; ne pas l'implémenter.
- Mode de build : v20 = v18 où **CR et LC** sont les gagnants de la sélection ; **RE est exclue** de v20 (ni gagnante, ni copiée : pas de grille de jugement de données pour RE, et ses cibles Mistral inventent d'après D0) ; les autres tâches (CO, RD, CT, Q, générique) gardent la ligne du build d'origine telle quelle.

### Amendements après relecture de la spec (2026-10-20, 23 h 40 ; décisions de l'orchestrateur)
1. **Sources de cible cette nuit : `mistral` et `slm:minicpm5-2b` seulement.** Pas de cible DeepSeek (5 lignes LC en jeu ; évite le recontrôle d'un journal OpenRouter par `train`, la question des conditions de l'API, et le schéma Kimi non vérifié). Les candidats `openrouter:*` présents dans `candidats.jsonl` sont ignorés et comptés ; le code de juge croisé (règle 5) reste possible plus tard mais n'est pas requis.
2. **Registre** : le format d'identifiant (`org/nom`, `licences.py:75`) et `genere_par` n'admettent pas une sortie de modèle local. Ajouter une valeur `genere_par = "modele-base"` réservée aux sorties d'un Modèle de base local, avec un identifiant au format admis (par ex. `openbmb/minicpm5-2b`, l'id HF de la fiche) ; licence relue dans la fiche du modèle et la carte HF locale (`models/`), `revision` et `verifie_le` renseignés ; usage `recherche` (décision d'Anaël du 20/10). Sans entrée valide, le build échoue avant tout run.
3. **Ligne CR ou LC sans candidat accepté : écartée** (pas de repli sur la ligne v18), motif compté au MANIFEST ; build refusé si moins de 30 lignes CR sont retenues ; LC à 0 ligne = avertissement au MANIFEST, pas un refus.
4. **CLI** : `slmsp data build --selection --candidats RUN_CANDIDATS --verdicts RUN_JUGE[,RUN_JUGE...] --taches-selection CR,LC --retirer RE --variante recherche`. Chaque run de jugement a `depuis == RUN_CANDIDATS` ; juges distincts ; grille, seuils et version de prompt identiques entre runs d'un même juge ; deux runs du même juge : refus.
5. **Acceptation** = verdict `accepte` du juge de données (DeepSeek, règle O1, tous les seuils) ; score = somme pondérée des critères normalisés sur [0, 1] avec min et max explicites par critère tirés de la grille ; `verdict_modele` du juge jamais lu.
6. **Égalité** : base d'abord, puis Mistral ; entre deux candidats base, la température la plus basse puis le rang.
7. **Schémas** : `LigneEntrainement.schema_version` 1 ou 2 ; en v2, `meta.cible = {source, appel_local_id | appel_id}`, `meta.source`, `meta.licence`, `meta.generateur` = ceux du gagnant (vérifiés contre le Registre), `appel_ids` (Mistral, entrée) facultatif quand `cible` est présent ; MANIFEST v2 (règle 8) ; `controler_nettoyage`, `controler_sous_ensemble` et `train run` (`recontroler_appel_ids`, lecteur `generations-locales.sqlite` en lecture seule) acceptent la v2 et relisent la v1.
8. **Provenance** : une cible `slm:` relue dans `generations-locales.sqlite` est recoupée avec `session_id`, `generateur` et le SHA du candidat ; statut `ok` exigé.
9. **Texte de la cible** = `cible_apprise` de 15.2 appelée **avec** `tokeniseur.compter` (même nettoyage que le jugement).

## 15.4 (N4) — Second juge désactivé pour `dev*`
Constat du plan : le second juge Mistral a tourné sur dev1 malgré `[jeux.dev1] second_juge = false` (`config/juges.toml`). Trouver la cause (lecture de la clé, échantillon `second_juge` du manifeste de gel, chemin de reprise), la corriger, et appliquer la règle à tout jeu dont l'identifiant commence par `dev` (dev2 compris) sans section dédiée. Aucun appel Mistral pour un jeu dev*, y compris en `--reprendre`.
- Fini quand : test de non-régression qui échoue avant le correctif ; test dev2 sans section ; v1.1 inchangé (second juge actif).

## 15.5 (N5) — dev2 : +20 items par tâche
Même procédé que dev1 (`spec-o4-jeu-dev.md`, consigne de vérification v3 neutre, exclusion stricte) : 20 items par tâche (160), disjoints de v1.1, de dev1, du jeu d'entraînement (v18) et du seed LC `20261020-093126-seed-4fcf` (contrôle de fuite de `data filter` / O4a). Les items d'évaluation ne sont pas des données d'entraînement (D1 respecté : ils n'entrent dans aucun générateur). Rédigés **sans regarder** les sorties ni les faiblesses des modèles (ne lire aucun run de génération ni de notation). Consigne CR commune conservée (participants, décisions, actions, points abordés), comme dev1.
- Livrable : items en brouillon dans `eval/` au format de dev1, contrôle de fuite vert, prêt pour la vérification DeepSeek + GLM (lancée par l'orchestrateur). Pas de gel cette nuit.

## 15.6 (N6) — LoRA GGUF et `--lora-scaled`
- `slmsp export lora --depuis TRAIN_RUN_ID` : conversion de l'adaptateur en LoRA GGUF (`convert_lora_to_gguf.py` du tag llama.cpp de `config/llamacpp.toml`), contrôle de compatibilité avec la base Q4_K_M, run d'export immuable. Refus clair si l'adaptateur n'est pas convertible (DoRA, par exemple).
- Évaluation : `eval run --modele lora:<EXPORT_LORA_RUN_ID> --echelle-lora 0.5` lance llama-server sur la base Q4_K_M + `--lora-scaled <gguf> <échelle>` ; l'échelle et l'adaptateur sont consignés dans le run et dans la référence du modèle (scores comparables par `eval comparer`).
- Charge : `measure run` accepte la même référence (RAM et latence CPU, avec le serveur d'embedding).
- Fini quand : tests (commande llama-server construite, échelle par défaut 1.0, refus DoRA, référence de modèle sérialisée) ; un essai réel de conversion est lancé par l'orchestrateur.
