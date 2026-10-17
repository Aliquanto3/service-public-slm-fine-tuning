---
title: "Découpage par tour du masque de perte (minicpm5-1b)"
type: 'feature'
created: '2026-10-17'
status: 'review'
baseline_commit: '18ad3ea'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-service-public-slm-fine-tuning-2026-10-12/ARCHITECTURE-SPINE.md (AD-7, H-MASQUE)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-candidats-registre.md (section Revue)'
  - '{project-root}/_bmad-output/implementation-artifacts/journal-decisions-nuit.md (D-nuit-A1-22, D-2026-10-17-M1)'
warnings:
  - "Écart à AD-7, consigné au journal (D-2026-10-17-M1) : le texte d'un exemple est l'historique officiel suivi de l'amorce officielle, identique à l'inférence. AD-7 n'est pas réécrit."
  - "Hors périmètre, bloquant pour la story 11.2 sur minicpm5-1b : 147 `tool_calls` de data/train/v1 portent des `arguments` en chaîne JSON, sur lesquels le template de minicpm5-1b appelle `.items()` (UndefinedError). Voir R7."
---

## Intent
Avec `chat_template_kwargs = { enable_thinking = false }`, l'amorce de génération de minicpm5-1b se termine par `<think>\n\n</think>\n\n`. Le template n'écrit jamais ce bloc dans un tour `assistant` rendu. Le masque de conversation refusait donc tout Run sur ce modèle, en SFT comme en ORPO, ce qui bloquait la story 11.2.

Anaël a d'abord retenu l'option 1 (insérer le bloc dans chaque tour), puis l'a remplacée le 2026-10-17 par le **découpage par tour**. Chaque tour `assistant` devient un exemple :
- l'historique est rendu par le template officiel et n'est pas supervisé ;
- l'amorce officielle suit (`add_generation_prompt=True`, mêmes kwargs, donc avec le bloc vide) ;
- le corps du tour vient en dernier, et c'est la seule partie supervisée.

Le texte et les tokens sont ainsi ceux de l'inférence à chaque tour. Le bloc n'apparaît que dans l'amorce du tour supervisé, jamais dans un historique.

## Approach
- **Déclaration générique dans la fiche** (`core/schemas/config_modele.py`) :
  - `decoupage_masque: "conversation" | "par-tour"`, avec `conversation` par défaut ;
  - `bloc_amorce: str | None`, non vide, admis seulement en `par-tour` (validateur) : la fin de l'amorce que le template n'écrit pas dans un tour rendu.

  Aucun slug n'est codé en dur. `config/modeles/minicpm5-1b.toml` déclare `par-tour` et `bloc_amorce = "<think>\n\n</think>\n\n"`. Toutes les autres fiches restent au défaut.
- **`train/masque.py`** (aucune insertion dans un rendu) :
  - `amorce_et_corps(messages, k)` :
    - l'amorce est `rendu(messages[:k], add_generation_prompt=True)` ;
    - le corps est la suite de `rendu(messages[:k+1])` après l'ouverture du tour ;
    - l'ouverture est l'amorce entière si le rendu la prolonge (cas Qwen), sinon l'amorce privée de `bloc_amorce`. Dans tout autre cas, `ErreurMasque`.
  - Refus explicites : un `reasoning_content` non vide, ou un contenu qui porte une balise du bloc déclaré (`<think>`, `</think>`). On n'ajoute jamais un second bloc.
  - `masque_du_tour` : `texte = amorce + corps`, labels à `IGNORE` sur l'amorce et égaux aux ids sur le corps.
  - `calculer_masques` : en `conversation`, `[calculer_masque(...)]`, sans changement ; en `par-tour`, un exemple par message `assistant`.
  - `empreinte_decoupage(config)` : `None` en `conversation`, sinon `{mode, bloc_amorce}`.
- **`train/chargement.py`** :
  - `pretokeniser` appelle `calculer_masques` et aplatit le résultat. `retenus` compte des exemples. La troncature et l'écartement des exemples sans supervision s'appliquent par exemple.
  - ORPO (`preparer_preferences`) en `par-tour` : le prompt est l'amorce officielle, c'est-à-dire l'historique officiel suivi de l'amorce avec le bloc. `chosen` et `rejected` sont le seul corps du tour, calculé par `amorce_et_corps`. Une réponse de plus d'un message, ou qui n'est pas `assistant`, lève `ManifesteInvalide`. Ni le bloc ni un tour suivant n'entrent dans la perte. En `conversation`, rien ne change.
- **Empreinte** (`train/run.py`) :
  - `invariants(..., decoupage_masque=empreinte_decoupage(config_modele))` ajoute la clé `decoupage_masque` à `CLES_INVARIANTS` ;
  - la même valeur est archivée sous `resolue["modele"]["decoupage_masque"]` dans `run.json` ;
  - la valeur `None` reste comparable aux runs antérieurs, qui n'ont pas la clé ;
  - `VERSION_MASQUE` reste à 1 et `chat_template_sha256` reste le SHA officiel ;
  - l'amorce se déduit du template, des kwargs (déjà archivés) et de `bloc_amorce`.
- **Inférence et export inchangés** :
  - `inference/serveur.py` ne lit que des champs nommés ; `--jinja`, `--reasoning` et `--chat-template-kwargs` ne bougent pas.
  - Le tokenizer n'est jamais modifié. `train/export.fusionner` sauvegarde le tokenizer de base : le GGUF embarque donc le template officiel, et le contrôle bloquant CA2 compare son SHA à `chat_template_sha256` (officiel).
  - AD-7 n'impose aucun export de variante.
- **Pas de cache de pré-tokenisation** :
  - `pretokeniser` tourne à chaque `train run` ;
  - SFT et Unsloth reçoivent ses `input_ids` et `labels` (`variante_unsloth` ne rend aucun template) ;
  - ORPO passe par `preparer_preferences`.
- **Qwen3.5** : le mécanisme le couvre sans toucher à ses fiches, qui restent `entrainable = false`.
  - Son template retire le bloc des anciens tours. En `par-tour`, chaque exemple n'utilise que le rendu officiel de son propre préfixe, et le dernier tour rendu prolonge l'amorce : `bloc_amorce` est inutile.
  - Démontré sur faux tokenizer (`test_par_tour_accepte_un_template_qui_reecrit_l_historique`), non vérifié sur le tokenizer réel de Qwen.
- **Écart à AD-7** : consigné au journal (D-2026-10-17-M1) et dans le commentaire de la fiche. Il se réduit à ceci : le texte d'un exemple est l'historique officiel suivi de l'amorce officielle, identique à l'inférence, au lieu du rendu de la conversation entière. AD-7, H-MASQUE et `decisions.md` ne sont pas modifiés.

### Garanties, contrôlées pour chaque exemple et testées
- **G1, amorce exacte** : `texte[:debut]` est égal octet pour octet à `rendu(messages[:k], add_generation_prompt=True)`, sans rien retirer.
- **G2, texte exact** : `texte == amorce + corps`, où le corps est le rendu officiel du tour après son ouverture. L'historique ne contient aucun bloc ajouté.
- **G3, supervision** : le texte décodé des labels supervisés est égal au corps.
- **G4, tokens (bloquante)** : `tokenizer(amorce, add_special_tokens=False)` est exactement le début des `input_ids` de l'exemple, et aucun token ne chevauche la fin de l'amorce. Sinon, `ErreurMasque`.

### Coût mesuré sur data/train/v1 (503 lignes, tokenizer minicpm5-1b, CPU)
| | Exemples | Tokens |
|---|---|---|
| Avant (conversation, rendu entier) | 503 | 1 014 568 |
| Après (par tour) | 617 (+22,7 %) | 1 202 229 (+18,5 %), dont 268 559 supervisés |

Répartition des lignes par nombre de tours `assistant` : 412 à 1 tour, 73 à 2, 13 à 3 et 5 à 4.

Constats sur le même jeu :
- aucun corps ne commence par `\n` ;
- aucun `reasoning_content` ;
- aucun refus du masque.

La règle la plus prudente est donc conservée : un masque non prouvé refuse le Run. L'autre règle possible, refuser l'exemple seul et le journaliser, n'est pas mise en œuvre tant qu'aucun cas n'existe. La mesure vient d'un script ponctuel, hors du chemin d'entraînement : ce script convertissait les `arguments` des `tool_calls` en objets avant le rendu, ce que `_messages_rendus` ne fait pas (R7). Sur minicpm5-1b, le chemin réel `pretokeniser` refuse aujourd'hui le Run dès la première ligne qui porte l'un de ces 147 `tool_calls` (« aucun refus du masque » ne vaut donc qu'après conversion).

## Tests
Les fixtures sont factices (D1). Tests rapides, dans `tests/train/test_masque.py` :
- `test_par_tour_amorce_officielle_et_corps_seul`, sur 5 conversations, vérifie G1 à G4 et la présence du bloc une seule fois, dans l'amorce :
  - système et 1 tour ;
  - 2 tours ;
  - système et 3 tours avec appel d'outil ;
  - tour vide ;
  - appel d'outil à contenu vide, puis `tool`, puis réponse.
- `test_par_tour_tour_historique_d_appel_d_outil` : le tour `tool_calls` est supervisé dans son propre exemple, puis n'est plus que du contexte, sans bloc.
- Cas sans bloc, réécriture de l'historique (cas Qwen), transmission des outils et des kwargs.
- Refus : `reasoning_content`, balise du bloc dans le contenu, bloc absent ou faux, token à cheval, tokens de l'amorce différents (G4).
- ORPO : prompt égal à l'amorce officielle, `chosen` et `rejected` égaux au seul corps, réponse à plusieurs messages refusée.
- Schéma : `bloc_amorce` exige `par-tour` et n'est jamais vide ; la fiche minicpm5-1b est chargée ; granite et eurollm restent en `conversation`.
- Défaut inchangé : pour granite, `calculer_masques` donne `[calculer_masque]`.

Tests lents (marqueur `lent`, lancés à la main, jamais dans la suite par défaut) :
- `test_candidat_reel_masque_sur_les_tours_assistant` passe maintenant pour minicpm5-1b (xfail strict retiré), en plus de granite et eurollm ;
- `test_minicpm5_reel_par_tour_egal_a_l_amorce_officielle` vérifie G1 à G4 sur les 5 conversations, avec le tokenizer réel ;
- ces 8 tests passent ;
- minicpm5-1b est ajouté à `test_rendu_identique_a_llama_server_jinja`, lancé en revue sur CPU (R2).

## Risques et points non vérifiés
- **R2, vérifié en revue (2026-10-17, CPU)** : `test_rendu_identique_a_llama_server_jinja[minicpm5-1b]` passe : `/apply-template` de llama-server rend exactement l'amorce HF (`add_generation_prompt=True`, `enable_thinking = false`, bloc vide compris) sur une conversation avec outil qui se termine par le message `tool`. granite passe aussi ; smollm3-3b est sauté (GGUF absent).
- **R3, non vérifié** : l'égalité entre le template du GGUF officiel et le template HF n'a pas été recontrôlée. L'export a été lu dans le code, pas exécuté.
- **R5** : le coût en tokens augmente de 18,5 % (mesuré).
- **R7, hors périmètre, bloquant pour la story 11.2 sur minicpm5-1b** :
  - dans data/train/v1, 147 `tool_calls` ont des `arguments` en chaîne JSON (format OpenAI) ;
  - le template de minicpm5-1b appelle `.items()` sur ces arguments, et `apply_chat_template` lève alors `UndefinedError` ;
  - à l'inférence, llama-server convertit les arguments en objets pour les templates qui l'exigent ; à l'entraînement, `_messages_rendus` ne le fait pas, quel que soit le découpage ;
  - à traiter dans une story dédiée : décoder les arguments selon les capacités du template, comme llama.cpp, sans changer granite. La forme exacte que llama-server passe au template à l'inférence est à établir dans cette story ;
  - depuis la revue, l'échec est une `ErreurMasque` qui cite R7 (vérifié sur le tokenizer réel), et non plus une `UndefinedError` brute ;
  - **eurollm-1.7b** : son template n'a aucune gestion des outils (ni `tool_calls` ni rôle `tool`). Les appels d'outils disparaissent du rendu sans erreur, à l'entraînement, et probablement aussi à l'inférence, où le template HF est forcé. Perte silencieuse, à remonter à Anaël.

## Auto Run Result
- Statut : review. Pas de fusion ni de push ; `sprint-status.yaml` n'est pas touché.
- Décision prise seul (la plus simple et la plus réversible) : `bloc_amorce` est déclaré dans la fiche, pas déduit. Le plus long préfixe commun entre l'amorce et le tour est ambigu, car le corps commence souvent par `<`.
- Décision prise seul : en `par-tour`, une réponse ORPO de plus d'un message est refusée.
- À confirmer par Anaël : R7, avant la story 11.2.

## Revue
Une passe (reviewer, 2026-10-17), avec la liste du second avis.

| # | Sévérité | Source | Décision | Motif |
|---|---|---|---|---|
| 1 | high | second avis (R7) | reporté, message corrigé | `arguments` en chaîne JSON non convertis : hors périmètre (story dédiée). L'échec sur minicpm5-1b est désormais une `ErreurMasque` qui cite R7 (vérifié sur le tokenizer réel). Cas eurollm consigné dans R7. Bloquant pour l'entraînement de minicpm5-1b, à remonter à Anaël. |
| 2 | medium | second avis | corrigé | La spec attribuait la mesure à une conversion absente du code. Elle précise maintenant qu'elle vient d'un script hors du chemin d'entraînement. |
| 3 | medium | second avis, confirmé | corrigé | Les clés `decoupage_masque` (valeur `None`) entraient dans `invariants` et `resolue["modele"]`, donc `--reprendre` d'un run antérieur échouait (`_rouvrir` compare la config résolue entière). Les clés sont maintenant absentes au défaut : la config résolue des modèles par défaut est celle d'avant le commit. Tests ajoutés : `test_decoupage_par_defaut_absent_de_la_config_resolue` et `test_invariants_portent_le_decoupage_par_tour`. |
| 4 | low | second avis | corrigé | Le second `apply_chat_template` est maintenant dans le `try` et lève `ErreurMasque`. |
| 5 | low | second avis | corrigé | Garde en production : un corps qui contient `bloc_amorce` est refusé. |
| 6 | low | second avis | corrigé | Un `reasoning_content` non vide est refusé quel que soit son type. `bloc_amorce` entièrement blanc est refusé par le schéma. Tests ajoutés. |
| 7 | low | second avis | corrigé | Oracle G2 en partie tautologique : ajout de `test_par_tour_textes_litteraux` (textes attendus écrits à la main). G1 était déjà contrôlé de façon indépendante (rendu officiel de `messages[:k]` égal au préfixe de l'exemple). |
| 8 | info | reviewer | vérifié | R2 levé : llama-server (CPU) rend la même amorce que HF pour minicpm5-1b. |
| 9 | info | reviewer, complexité | rejeté | Le découpage par tour rend `O(t)` préfixes par conversation (`O(t²)` en texte), comme le masque de conversation. Au plus 4 tours sur data/train/v1 : aucun impact réel. Complexité : 0 constat à corriger. |
| 10 | info | reviewer | noté | `verifier_campagne` traite une clé absente comme `None` (`.get`). Un run `par-tour` et un run `conversation` d'une même campagne sont donc refusés ensemble, ce qui est voulu. |
