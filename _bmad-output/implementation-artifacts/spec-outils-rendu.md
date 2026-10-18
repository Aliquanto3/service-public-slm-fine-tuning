---
title: "Rendu des appels d'outils à l'entraînement, aligné sur l'inférence (R7)"
type: 'bugfix'
created: '2026-10-17'
status: 'review'
baseline_commit: 'c16fb39'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-service-public-slm-fine-tuning-2026-10-12/ARCHITECTURE-SPINE.md (AD-6, AD-7, AD-13)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-masque-minicpm5.md (R2, R3, R7)'
warnings:
  - "oversized : spec d'enquête, mesures comprises."
deferred: []
---

## Intent
**Problème.** Le texte d'entraînement doit être celui que le modèle voit à l'inférence (AD-6, AD-7). Pour l'inférence, la référence est `/apply-template` de llama-server b11429 (`--jinja`), appelé avec les messages OpenAI du client du projet, où `arguments` est une chaîne JSON. Pour les 91 lignes à outils de data/train/v1 (Tâche RD), le texte d'entraînement s'en écarte de deux façons :
1. il échoue pour minicpm5-1b (`.items()` sur une chaîne) ;
2. il diffère pour granite-4.0-1b et minicpm5-1b, par l'ordre des clés de la déclaration `tools`.

EuroLLM est aligné, mais seulement parce que ni l'entraînement ni l'inférence ne rendent les outils.

**Approche.** Deux normalisations génériques dans `train/chargement.py`, sans slug et sans champ de fiche :
- les `tools` rendus sont les définitions de `config/outils-mcp.toml` (`mcp.outils.charger_outils`), dans l'ordre du fichier, restreintes aux noms que déclare la ligne ;
- les `arguments` en chaîne sont décodés en objets, en gardant l'ordre des clés.

Un test lent d'égalité HF / llama-server, sur des conversations avec outils, garantit les deux. Le cas EuroLLM est une décision d'Anaël (§4).

## §0. Premier message RD : ni Mode connecté ni Mode local (hors outils)
**Décision d'Anaël du 2026-10-18 : normaliser au build, dans une autre story (branche feat/rd-connecte). Traité ailleurs : R7 ne touche pas `data/build.py`.** Le constat ci-dessous reste la référence.

Constat vérifié dans le code et par un rendu du Harnais contre les 91 lignes RD, sans appel :
- **Côté données.** `data/build.py` (l. 291) construit le début de conversation par `construire_messages(tache, entree, None)`. Le prompt RD déclare l'emplacement `passages` ; sans passages, il rend donc `AUCUN_PASSAGE`. Les 91 lignes commencent ainsi : 91 sur 91 égales à ce rendu.
- **Mode connecté** (`recherche.messages_connecte`, l. 396-410). Le prompt perd l'emplacement `passages`, et le message `user` est la demande seule : 0 sur 91 égal. C'est le seul mode qui envoie `tools` (l. 440-451).
- **Mode local** (`_messages_index`). Il donne les passages du catalogue bornés au budget, et la phrase « Aucun passage » seulement si la recherche ne trouve rien. Il **n'envoie pas** `tools` : `offerts` vaut None et la génération n'a qu'un tour.
- Les lignes RD sont donc un hybride qu'aucun mode ne produit : texte du Mode local sans passage, plus outils et tours d'appel du Mode connecté.
- Le prompt système est identique : 91 sur 91 égaux à celui du Harnais (`config/prompts/taches/RD.md`).
- Si les lignes RD étaient lues comme du Mode local, l'écart serait pire, car ce mode n'offre pas d'outils. L'écart le plus petit est avec le Mode connecté : seul le message `user` diffère.

Options (tranchées, voir ci-dessus) :
- **Normaliser au build.** `build.py` compose le début RD par `messages_connecte`, puis `slmsp data build` refabrique les lignes depuis le journal et les cassettes, de façon déterministe, sans appel Mistral, dans une nouvelle version (v1 n'est pas réécrite). Effet de bord : les réponses de Mistral ont été générées avec le prompt « Aucun passage… ». Elles restent cohérentes avec les résultats d'outils, mais le contexte de génération diffère légèrement du prompt d'entraînement.
- **Adapter au chargement.** Pour une ligne qui déclare des outils, `train/chargement.py` remplace le message `user` par celui de `messages_connecte` (la demande est extraite après « Demande :\n »). Les données ne bougent pas, mais la transformation reste cachée et fragile (analyse d'un texte rendu). Elle doit entrer dans l'empreinte.
- **Régénérer** : exclu. D1 interdit à Claude de générer, et une campagne Mistral serait payante.

## Mesures (CPU, llama-server b11429 bin-cpu, GGUF Q4_K_M, un serveur à la fois)
Méthode. Le côté inférence est `/apply-template` avec le corps du client : `messages`, `tools = charger_outils()`, et `chat_template_kwargs` de la fiche ; les lancements passent par `ServeurLlama`, comme pour l'inférence. Le côté entraînement est `train.rendu.apply_chat_template` (tokenizer HF local), avec `add_generation_prompt=True`. On compare chaque préfixe qui précède un tour `assistant`, c'est-à-dire chaque prompt d'inférence.

Échantillon détaillé : les lignes 92, 93 et 99 de train.jsonl (un appel ; trois appels dans un même tour ; appel avec texte). La vérification complète porte sur les 91 lignes RD, soit 205 préfixes par modèle.

| Rendus égaux à llama-server, sur 205 préfixes | granite-4.0-1b | minicpm5-1b | eurollm-1.7b |
|---|---|---|---|
| outils de train.jsonl, arguments en objet (rendu actuel corrigé des seuls arguments) | **0** | **0** | 205 |
| outils `charger_outils()`, arguments en chaîne (rendu actuel) | 205 | **91** (114 `UndefinedError`) | 205 |
| outils `charger_outils()`, arguments en objet (**proposé**) | **205** | **205** | **205** |

Mesure de l'orchestrateur du 2026-10-18 (règle de taille relevée à 2,5B, **minicpm5-2b** candidat entraînable), avec la normalisation proposée : **205 / 205** rendus égaux à `/apply-template` pour minicpm5-2b sur les lignes RD de v1.

Mesure de la story (test lent `test_jeu_v1_rendu_identique_a_llama_server`, chemin réel `_messages_rendus` et `_tools_rendus`, CPU, GGUF Q4_K_M) : granite-4.0-1b 205/205, minicpm5-1b 205/205, minicpm5-2b 205/205. Conversation factice à deux tours d'appel (`test_rendu_identique_a_llama_server_jinja`) : 3/3 préfixes égaux sur les trois.

Autres constats, tous mesurés :
- **llama-server ignore la forme des arguments.** Avec les mêmes messages, arguments en chaîne ou en objet, son rendu est identique pour les trois modèles. `content` absent ou `null` dans un tour d'appel ne change rien non plus. On ne sait donc pas quelle forme il passe au template ; on sait seulement que son rendu est égal au rendu HF avec objets.
- **granite** : l'unique écart porte sur les lignes `<tools>`. HF suit l'ordre trié de train.jsonl (`{"function": {"description", "name", "parameters"}, "type"}`), llama-server écrit `{"type", "function": {"name", "description", "parameters"}}`. llama-server reconstruit l'enveloppe mais garde l'ordre interne de `parameters` : avec les outils triés de train.jsonl, son rendu diffère encore de celui de l'inférence réelle (`llama_train != llama_inf`). On ne peut donc pas retrouver l'ordre de l'inférence à partir de train.jsonl ; il faut relire `config/outils-mcp.toml`. Son SHA, `9517c4c7…`, est celui de `sha_outils_mcp` dans MANIFEST.json.
- **minicpm5-1b** : son template écrit les appels sous la forme `<function name="…"><param name="…">…</param></function>` et les réponses d'outil sous la forme `user` + `<tool_response>`. Une fois les outils et les arguments corrigés, les 205 rendus sont égaux, amorce `<think>\n\n</think>\n\n` comprise. Cela confirme, sur ces prompts, R2 (amorce de llama-server égale à l'amorce HF) et R3 (template du GGUF équivalent au template HF) de spec-masque-minicpm5.
- **eurollm-1.7b** : le template imposé (`models/eurollm-1.7b/chat_template.jinja`) est identique au template HF du tokenizer. Il ne lit ni `tools` ni `tool_calls`. Un tour d'appel sans texte est rendu `<|im_start|>assistant\n<|im_end|>`, et une réponse d'outil `<|im_start|>tool\n<contenu><|im_end|>`. llama-server **ne bascule pas** sur un format générique. Sonde `/v1/chat/completions` (question factice, 5 outils, `max_tokens = 24`) : `prompt_tokens = 24`, donc aucun outil dans le prompt, et la sortie est du texte libre, sans grammaire ni appel.
- **Conversation entière** (`add_generation_prompt = false`, dernier message `assistant`) : llama-server la traite comme un pré-remplissage (amorce, puis contenu, sans `<|im_end|>`). Ce n'est pas un écart d'entraînement : la comparaison se fait sur les préfixes.

## Réponses aux questions
**Q2, origine de `tools` à l'entraînement.** Les 503 lignes ont une clé `tools`. Elle n'est remplie que pour les 91 lignes RD, avec les 5 outils, et vide ailleurs. Elle est écrite par `data/build.py` à partir de `config/outils-mcp.toml`, puis sérialisée en JSON canonique (clés triées). `pretokeniser` et `preparer_preferences` la transmettent au template en `natif`.

À l'inférence, `recherche.py` passe `charger_outils()` filtré par `outils_autorises` de RD (les 5 outils, dans l'ordre du fichier), et `ClientLlama` les envoie tels quels. Les deux côtés ont le même contenu (égalité de dicts) mais pas le même ordre de clés, d'où l'écart.

Les deux côtés déclarent les outils au même moment. À l'inférence, `iterations_max = 5`, et les lignes RD ont au plus 3 tours d'appel : les outils sont donc offerts à chaque tour, comme à l'entraînement.

**Q3, mécanisme (implémenté)** (dans `train/chargement.py`, appliqué avant `calculer_masques` et dans `preparer_preferences`) :
- `_tools_rendus(ligne)` reprend la règle de l'inférence (`recherche.py`, l. 440) :
  - `[o for o in charger_outils() if nom(o) in tache.outils_autorises]`, où la Tâche de la ligne vient de `config/taches.toml`. Les noms de la ligne ne servent pas de source ;
  - pour une ligne sans outils, ou d'une Tâche sans `outils_autorises`, pas de `tools` ;
  - lève `ManifesteInvalide` si les outils de la ligne ne sont pas exactement ceux-là (mêmes noms, définitions égales en dicts) ;
  - option conseillée : vérifier aussi `sha_outils_mcp` du MANIFEST contre le SHA de `config/outils-mcp.toml`.
- `content: null` est supprimé du message rendu (llama-server le rend comme une absence, HF écrit `None` pour EuroLLM). Le jeu v1 n'en contient aucun (0 mesuré sur 503 lignes) : c'est une garde.
- `_messages_rendus`, hors `balises-tool-call` (inchangé) : `arguments` en chaîne passe par `json.loads`, qui garde l'ordre des clés. Le résultat doit être un dict, sinon `ManifesteInvalide`. Le message est copié, jamais modifié. Un `arguments` déjà en objet n'est pas touché.
- **Pas de sonde du template ni de champ de fiche.** llama-server rend la même chose quelle que soit la forme des arguments, et le décodage systématique égale son rendu sur les trois templates (615 préfixes). Une sonde à la llama.cpp (rendre un appel en chaîne et en objet, puis garder la forme qui ne lève pas) ajouterait du code sans cas qui la distingue. Elle reste la solution de repli si le test lent trouve un template qui rend la chaîne autrement que `tojson(objet)`.
- **Où** : la normalisation précède `calculer_masques` dans `pretokeniser`, **et** le rendu du prompt, de `chosen` et de `rejected` dans `preparer_preferences` (ORPO, y compris `_corps_par_tour`). Les deux chemins sont testés.
- **Empreinte** : le texte rendu change pour les lignes RD. On ajoute `rendu_outils: 1` à `CLES_INVARIANTS` (`train/run.py`), archivé dans `run.json`. L'absence de la clé dans un run antérieur vaut « rendu d'avant R7 ». `VERSION_MASQUE` ne change pas (le masque par tour de feat/masque-minicpm5 est fusionné).
- **Test lent** : `test_rendu_identique_a_llama_server_jinja` est étendu ainsi (marqueur `lent`, CPU, saute si le GGUF manque) :
  - slugs : les candidats entraînables du registre, calculés depuis `verifications.CANDIDATS` filtré par `entrainable` (granite-4.0-1b, minicpm5-1b, minicpm5-2b au 2026-10-18) ;
  - conversation factice (D1) avec deux tours d'appel et des arguments en chaîne. Elle comprend un appel à deux clés dans un ordre non trié, et des valeurs qui opposent `tojson` de transformers (`json.dumps(ensure_ascii=False)`) et celui de minja : accent (`"<é-factice>"`), apostrophe (`"<l'apostrophe-factice>"`), guillemet échappé, entier, flottant (`1.5`), booléen et liste. L'égalité n'est prouvée sur le jeu v1 que pour des chaînes accentuées et 2 entiers ;
  - côté entraînement, les outils sont donnés triés, comme dans train.jsonl, et passent par le vrai chemin (`_messages_rendus`, `_tools_rendus`) ;
  - côté inférence, `ClientLlama._messages` et `charger_outils()` ;
  - égalité exigée sur chaque préfixe qui précède un tour `assistant`.

  On y ajoute `test_jeu_v1_rendu_identique_a_llama_server`, qui reprend la mesure ci-dessus sur data/train/v1 et saute si le jeu est absent. Ce test lit les données mais n'en génère aucune.
- **Tests rapides** :
  - décodage : ordre conservé, entrée non modifiée, JSON illisible ou non-objet refusé, balises inchangées, `content: null` retiré ;
  - `_tools_rendus` : outils de `outils_autorises` dans l'ordre du fichier, ligne divergente refusée ;
  - les deux chemins, `pretokeniser` et `preparer_preferences` (SFT et ORPO, `conversation` et `par-tour`), reçoivent les outils et les arguments normalisés ;
  - minicpm5 sans poids : faux tokenizer dont le template appelle `.items()`.

**Q5, effet sur le masque et sur le jeu v1.**
- Sur les 503 lignes, 91 (RD) ont des outils, avec 114 tours d'appel portant 147 `tool_calls` (123 à 1 clé, 19 à 2 clés, 5 à 3 clés ; 11 dans un ordre non trié ; 2 valeurs entières).
- **granite-4.0-1b et eurollm-1.7b** (masque `conversation`) : 91 exemples sur 503 contiennent des outils. Pour granite, seul le bloc `<tools>` du prompt change (non supervisé). Les tours d'appel supervisés sont identiques (chaîne et objet donnent le même texte). Pour EuroLLM, le texte ne change pas.
- **minicpm5-1b** (`par-tour`) : 205 exemples sur 617 contiennent des outils, dont 114 qui supervisent un tour d'appel et 91 une réponse finale. Aujourd'hui, tout Run échoue sur ces lignes. Après correctif, le corps des 114 tours d'appel est le format `<function …>` que llama-server rend dans l'historique. Les comptes de tokens de spec-masque-minicpm5 (1 202 229) ont été mesurés avec les outils triés : il faut les remesurer.
- Le découpage lui-même ne change pas : la normalisation précède le masque.

## §4. EuroLLM : ce que fait l'inférence et options
**Décision d'Anaël du 2026-10-18 : option D, déjà faite sur main (`entrainable = false`). Rien à coder dans R7.**

**Constat.** En Mode connecté sur RD, EuroLLM ne voit jamais les outils et ne peut pas en appeler. Le Harnais ne reçoit aucun appel valide et termine sur la réponse texte du premier tour, sans passages de l'Index : en Mode connecté, le premier tour n'en contient pas (AD-14). Si la Baseline d'EuroLLM a été mesurée sur RD en Mode connecté, elle l'a été dans ces conditions.

À l'entraînement, le rendu est identique à celui de l'inférence. Mais 91 des 114 tours d'appel n'ont pas de texte, et leur corps supervisé se réduit à `<|im_end|>` : le modèle apprendrait à rendre une réponse vide au premier tour de RD.

| Option | Ce que cela demande | Coût et risque |
|---|---|---|
| A. Statu quo aligné | Rien, ou écarter de la supervision les tours d'appel vides. | L'égalité est déjà vraie. RD n'a pas d'outils pour EuroLLM. Sans filtre, l'entraînement enseigne une réponse vide sur RD. Le filtre demande une règle générique (« tour supervisé sans texte rendu ») à concevoir. |
| B. Exclure EuroLLM des Tâches à outils | Champ de fiche (par exemple `outils = false`). Le Harnais passe alors en Mode local (Index, sans `tools`) et l'entraînement retire les 91 lignes RD, ou les reconstruit sans outils. | Code dans le Harnais et dans le chargement. Baseline RD d'EuroLLM à remesurer en Mode local. RD n'est plus comparable entre candidats. Les données ne sont pas régénérées. |
| C. Template dérivé qui déclare les outils | `chat_template.jinja` dérivé (description des `tools` dans le système, appels en balises `<tool_call>`), imposé aux deux côtés, avec le protocole `balises-tool-call` (AD-13 : réécriture de l'historique et analyse des balises par le client, déjà en place). | Écart à AD-7 (template non officiel) à consigner. Le texte du template est à rédiger (consigne d'outil, pas une Donnée d'entraînement, mais D1 à vérifier). Le modèle de base ne connaît pas le format, donc Baseline RD faible et à remesurer. Le tokenizer d'entraînement devra recevoir le même template. Coût moyen. |
| D. Retirer EuroLLM du fine-tuning | `entrainable = false` (Baseline seulement), comme les Qwen. | Aucun code. On perd le seul candidat européen de moins de 2B. Le défaut d'inférence sur RD reste dans sa Baseline (à documenter). |
| E. Protocole `json-generique` au lieu de `natif` (non sondé jusqu'ici) | `protocole_outils = "json-generique"` dans la fiche. `tools` n'est pas transmis ; la sortie est contrainte par `response_format` (`schema_json_generique`, client.py l. 52 et 72-90). À l'entraînement, `_avec_tools` (chargement.py, l. 311) est faux dans ce protocole : il faudrait réécrire les tours d'appel au format de la sortie contrainte (`{"tool_calls": [...]}`), puis décrire les outils dans le prompt. Le Harnais ne le fait pas (`prompts.py` : « les outils ne sont jamais rendus dans le texte »). | **Mesuré, en échec** (voir la sonde ci-dessous) : HTTP 400 sur llama-server b11429, avant toute génération. Il faudrait d'abord diagnostiquer cette erreur de grammaire. |

Pour l'option C, le template dérivé est une Donnée d'entraînement à conserver (AD-7) : il est versionné avec le run et entre dans son empreinte.

**Sonde H-TOOLS sur EuroLLM**, en CPU, sans verrou GPU et sans appel payant : `slmsp eval sonde-outils --modele base:eurollm-1.7b`, items RD-001 et RD-002 du calibrage, avec Bac à sable et cassettes. Run `runs/eval-sonde/20261017-222256-eurollm-1.7b-4554` du worktree, non versionné. Statut `partiel-erreur`, aucun protocole valide.
- `natif` : 0 appel sur 5 attendus. Le modèle répond en texte libre et invente des faits (une date de mise à jour, par exemple).
- `json-generique` : les 2 items en erreur. HTTP 400 `Failed to initialize samplers: Unexpected empty grammar stack after accepting piece: assistant (58406)`, reproduit hors Harnais sur une question factice.
- `balises-tool-call` : 0 appel sur 5, texte libre. Le template ne rend pas les `tools`.

La sonde recommande `natif` « par défaut, faute de protocole valide ». Pour la lancer, il a fallu exposer l'Index : une jonction temporaire `index` vers celui de la tour, en lecture seule, retirée ensuite.

La « reproduction du format générique de llama-server » n'est pas une option : b11429 n'en applique aucun à ce template (mesuré).

## Boundaries
- **Toujours** : la référence est le rendu de llama-server sur les messages du client. Les données ne sont jamais modifiées. Les normalisations ne s'appliquent qu'au rendu.
- **Jamais** : de slug en dur, de régénération de data/train/v1, de changement du client d'inférence ni de `balises-tool-call`. Le correctif porte sur `chargement.py` et `run.py` (la fusion de feat/masque-minicpm5 est faite).

## Risques et points non vérifiés
- La règle interne de llama.cpp n'est pas connue : seul son comportement sur trois templates est observé. Un template futur qui rend une chaîne autrement que `tojson(objet)` casserait l'égalité. Le test lent le détectera, sans le prévenir.
- `content: null` : 0 dans le jeu v1. La suppression est une garde (voir Q3).
- **Troncature des résultats d'outils à l'inférence (second avis, medium, mesuré).** `borner_resultats` (`harness/budget.py`, l. 199) tronque les messages `tool` quand le prompt suivant dépasse `contexte − max_tokens` (1024 dans `config/harnais.toml`). L'entraînement ne tronque jamais. Les messages `tool` du jeu vont jusqu'à 9 963 caractères. On a compté les lignes RD dont au moins un prompt d'après un résultat d'outil dépasse le budget (rendu HF égal à llama-server, outils de l'inférence) :

  | Tokenizer | > 3 072 (contexte 4096) | > 4 096 | > 7 168 (contexte 8192) | Plus grand prompt |
  |---|---|---|---|---|
  | granite-4.0-1b | 30 / 91 | 7 | 2 | 11 599 |
  | minicpm5-1b | 29 / 91 | 7 | 2 | 11 626 |
  | eurollm-1.7b | 12 / 91 | 5 | 2 | 12 575 |

  Avec un contexte de 4096 (EuroLLM, et la Baseline selon la décision du 2026-10-17), un tiers des lignes RD de granite et minicpm5 montrent des résultats d'outils que l'inférence aurait tronqués. Le premier prompt (système, outils, demande) fait déjà 1 377 tokens pour granite, 1 423 pour minicpm5 et 368 pour EuroLLM, qui ne rend pas les outils. Options, à trancher : borner à l'entraînement avec la même règle (mais elle mesure par llama-server, donc il faut un équivalent hors ligne), écarter les lignes qui dépassent, ou accepter l'écart pour le contexte d'entraînement (8192 dans les fiches de granite et minicpm5).
- Non mesuré :
  - l'analyse, à l'inférence, des appels générés par minicpm5-1b (`<function …>`) et granite (`<tool_call>`) : seul le rendu est comparé ;
  - les GGUF F16 et le GGUF exporté après fine-tuning (contrôle CA2) ;
  - les données ORPO (aucune n'existe encore).
- `data/preferences.py` génère les réponses rejetées avec les outils triés de la ligne : leur prompt diffère légèrement de celui de l'inférence. Effet faible, non mesuré.
- Prompts de train.jsonl face au Harnais : le système est vérifié (91 sur 91) et le message `user` est en écart (§0).

## Auto Run Result
- Statut : review. Code et tests faits (commit de la branche feat/outils-rendu), aucun appel payant, aucune donnée générée ni modifiée.
- Code : `train/chargement.py` (`_messages_rendus` décode les `arguments` et retire `content: null` hors `balises-tool-call` ; `_tools_rendus` ; `controler_outils_mcp`, appelé par `charger_jeu` quand le MANIFEST porte `sha_outils_mcp` et que des lignes ont des outils ; `_tools_rendus` dans `pretokeniser` et `preparer_preferences`, donc aussi `_corps_par_tour`) et `train/run.py` (`rendu_outils: 1` dans `CLES_INVARIANTS`, constante `VERSION_RENDU_OUTILS`).
- Tests : `tests/train/test_rendu_outils.py` (18, rapides) ; `tests/train/test_masque.py` : `test_rendu_identique_a_llama_server_jinja` étendu et `test_jeu_v1_rendu_identique_a_llama_server` (lents, trois candidats entraînables). Le second lit `SLMSP_TRAIN_V1` (chemin de train.jsonl) à défaut de `data/train/v1/` de la racine. Les fixtures de `tests/train/conftest.py` prennent la Tâche RD et ses vrais outils, le faux tokenizer n'écrit plus que leurs noms.
- Décisions prises seul :
  - les outils de la ligne sont comparés par nom et par définition (dicts), sans exiger le même ordre dans la ligne ;
  - le contrôle de `sha_outils_mcp` est dans `charger_jeu` (revue : un jeu à outils sans SHA déclaré est refusé ; les paires ORPO le reprennent du jeu SFT source) ;
  - `content: null` n'est retiré, comme le décodage, que hors `balises-tool-call` (chemin inchangé).
- Écart découvert, non corrigé (à confirmer par Anaël) : pour minicpm5-1b et minicpm5-2b, une valeur d'argument `null` est rendue `None` par transformers et vide par llama-server ; une liste, `['…']` contre un texte nu. Granite égale llama-server sur ces cas. Le jeu v1 n'en contient pas, et les schémas de `config/outils-mcp.toml` n'admettent que chaîne, entier et `null` (`anyOf string|null`). Le test lent exclut `null` et les listes. Un `null` émis par un minicpm5 fine-tuné ne serait pas rendu comme à l'inférence : correctif possible, une normalisation propre à ce template, à décider. Revue : à l'entraînement, `null`, liste et objet imbriqué dans des arguments sont refusés (`ManifesteInvalide`), jamais rendus en écart silencieux ; le cas de l'inférence reste à décider.
- Reste à faire hors R7 : §0 (feat/rd-connecte), remesure des comptes de tokens de spec-masque-minicpm5 (1 202 229, mesurés avec les outils triés), troncature des résultats d'outils.

## Revue
Revue Opus du 2026-10-18, une passe, branche rebasée sur main (62a109a, sans conflit). Parité mesurée en CPU (llama-server b11429, GGUF Q4_K_M), après correctifs, sur les 91 lignes RD de v1 :

| Modèle | Préfixes avec amorce | Textes supervisés complets (balise de fin comprise) |
|---|---|---|
| granite-4.0-1b (`conversation`) | 205 / 205 | 91 / 91 |
| minicpm5-1b (`par-tour`) | 205 / 205 | 205 / 205 |
| minicpm5-2b (`conversation`) | 205 / 205 | 91 / 91 |

Conversation factice à deux tours d'appel : 3/3 préfixes et tous les textes supervisés égaux sur les trois.

| Sévérité | Source | Constat | Suite | Motif |
|---|---|---|---|---|
| medium | second avis 1 | `controler_outils_mcp` inopérant sans `sha_outils_mcp`, donc toujours en ORPO (`ManifestePreferences` sans la clé). | Corrigé | `ManifestePreferences.sha_outils_mcp` optionnel (compatible), rempli par `data/preferences.py` depuis le MANIFEST SFT. Au chargement, à défaut de clé, le SHA est lu dans le MANIFEST du jeu `jeu_sft_version`. Un jeu à outils sans SHA déclaré est **refusé** : les outils rendus viennent de la config et non des lignes, rien ne prouverait qu'ils sont ceux du build, et `data build` écrit toujours la clé (seuls des MANIFEST faits main sont touchés). Fixtures de test : la clé est écrite pour un jeu à outils. |
| medium | second avis 2 | `_arguments_decodes` acceptait `null`, listes, objets imbriqués et `arguments` ni chaîne ni objet ; rendus différents de llama-server pour minicpm5. | Corrigé | Valeurs admises : chaîne, entier, flottant, booléen (couvertes par le test lent). `null`, liste, objet imbriqué, `NaN`/`Infinity` et `arguments` non chaîne non objet lèvent `ManifesteInvalide` (message citant R7). v1 n'en contient aucun (suite lente verte). |
| medium | second avis 3 | Le texte supervisé (tour `assistant`, balise de fin) n'était jamais comparé à llama-server. | Corrigé | `_comparer_textes_supervises` (test_masque.py) : pour chaque exemple de `calculer_masques` (chemin de `pretokeniser`), le texte d'entraînement doit être un préfixe exact de `/apply-template` sur la conversation jusqu'au tour, suivie d'un `user` factice ; en `par-tour`, l'amorce privée de `bloc_amorce` suivie du corps (le template n'écrit pas le bloc dans l'historique). Comptes ci-dessus. |
| low | second avis 4 | Tests de parité lents, hors suite par défaut. | Consigné | Voulu : marqueur `lent`, CPU (`ServeurLlama` variante `cpu`), sautés sans GGUF ; à lancer par `pytest -m lent tests/train/test_masque.py -k llama_server` (`SLMSP_TRAIN_V1` pour un worktree). |
| low | second avis 5 | `_messages_rendus` normalise aussi en `json-generique`. | Rejeté | Le « inchangé » de la spec vise `balises-tool-call`. En `json-generique` le client envoie les mêmes messages (`ClientLlama._messages`), et llama-server rend l'historique de la même façon : la normalisation reste la bonne. Aucun candidat entraînable n'est en `json-generique`. |
| low | second avis 6 | `content: None` retiré quel que soit le rôle. | Rejeté | Le contrat des messages (`core.messages`) n'admet `content: null` que pour `assistant` ; ailleurs la ligne est déjà invalide au build. Retirer l'absence reste équivalent à llama-server. |
| low | second avis 7 | Comparaison des outils sans ordre. | Consigné | Correct : le rendu suit l'ordre de `config/outils-mcp.toml`, non celui de la ligne. |
| low | second avis 8 | Un run postérieur à R7 est refusé dans une campagne qui contient un run antérieur (`rendu_outils` absent). | Consigné | Voulu : le texte des lignes RD a changé, les runs ne sont pas comparables. |
| low | second avis 9 | `data/preferences.py` génère `rejected` avec les outils triés de la ligne. | Reporté | Construction des données, hors R7 (déjà dans « Risques »). Vérifier à la première campagne ORPO que le prompt de génération égale celui de l'inférence. |
| — | revue | Complexité : 0 constat. | — | Aucune structure qui grossit à l'exécution n'est parcourue à chaque événement (outils mis en cache par Tâche, contrôle du SHA en un passage). |
