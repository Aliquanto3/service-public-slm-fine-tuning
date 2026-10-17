---
title: "Rendu des appels d'outils à l'entraînement, aligné sur l'inférence (R7)"
type: 'bugfix'
created: '2026-10-17'
status: 'draft'
baseline_commit: '62831f8'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-service-public-slm-fine-tuning-2026-10-12/ARCHITECTURE-SPINE.md (AD-6, AD-7, AD-13)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-masque-minicpm5.md (R2, R3, R7)'
warnings:
  - "oversized : spec d'enquête, mesures comprises."
  - "INFÉRENCE INCORRECTE pour eurollm-1.7b (touche la Baseline) : llama-server b11429 reçoit les `tools` mais ne les rend pas. Le prompt ne les décrit pas, aucun format d'appel n'est imposé, et le modèle ne peut pas appeler d'outil en Mode connecté. Mesuré, voir §4."
  - "Écart train/inférence nouveau, hors arguments, pour granite-4.0-1b et minicpm5-1b : l'ordre des clés de `tools`. train.jsonl stocke les outils en JSON canonique (clés triées), l'inférence les envoie dans l'ordre de config/outils-mcp.toml. 0 rendu égal sur 205 avec les outils de train.jsonl."
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

## Mesures (CPU, llama-server b11429 bin-cpu, GGUF Q4_K_M, un serveur à la fois)
Méthode. Le côté inférence est `/apply-template` avec le corps du client : `messages`, `tools = charger_outils()`, et `chat_template_kwargs` de la fiche ; les lancements passent par `ServeurLlama`, comme pour l'inférence. Le côté entraînement est `train.rendu.apply_chat_template` (tokenizer HF local), avec `add_generation_prompt=True`. On compare chaque préfixe qui précède un tour `assistant`, c'est-à-dire chaque prompt d'inférence.

Échantillon détaillé : les lignes 92, 93 et 99 de train.jsonl (un appel ; trois appels dans un même tour ; appel avec texte). La vérification complète porte sur les 91 lignes RD, soit 205 préfixes par modèle.

| Rendus égaux à llama-server, sur 205 préfixes | granite-4.0-1b | minicpm5-1b | eurollm-1.7b |
|---|---|---|---|
| outils de train.jsonl, arguments en objet (rendu actuel corrigé des seuls arguments) | **0** | **0** | 205 |
| outils `charger_outils()`, arguments en chaîne (rendu actuel) | 205 | **91** (114 `UndefinedError`) | 205 |
| outils `charger_outils()`, arguments en objet (**proposé**) | **205** | **205** | **205** |

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

**Q3, mécanisme proposé** (dans `train/chargement.py`, appliqué avant `calculer_masques` et dans `preparer_preferences`) :
- `_tools_rendus(tools_ligne)` :
  - rend `[o for o in charger_outils() if nom(o) in noms(tools_ligne)]` ;
  - lève `ManifesteInvalide` si un outil de la ligne est inconnu, ou si sa définition diffère de celle du fichier (comparaison de dicts) ;
  - option conseillée : vérifier aussi `sha_outils_mcp` du MANIFEST contre le SHA de `config/outils-mcp.toml`.
- `_messages_rendus`, hors `balises-tool-call` (inchangé) : `arguments` en chaîne passe par `json.loads`, qui garde l'ordre des clés. Le résultat doit être un dict, sinon `ManifesteInvalide`. Le message est copié, jamais modifié. Un `arguments` déjà en objet n'est pas touché.
- **Pas de sonde du template ni de champ de fiche.** llama-server rend la même chose quelle que soit la forme des arguments, et le décodage systématique égale son rendu sur les trois templates (615 préfixes). Une sonde à la llama.cpp (rendre un appel en chaîne et en objet, puis garder la forme qui ne lève pas) ajouterait du code sans cas qui la distingue. Elle reste la solution de repli si le test lent trouve un template qui rend la chaîne autrement que `tojson(objet)`.
- **Empreinte** : le texte rendu change pour les lignes RD. Il faut ajouter un invariant (par exemple `rendu_outils: 1` dans `CLES_INVARIANTS`), sans toucher à `VERSION_MASQUE` : le fichier `masque.py` est en revue sur une autre branche. **À confirmer par Anaël.**
- **Test lent** : `test_rendu_identique_a_llama_server_jinja` est étendu ainsi (marqueur `lent`, CPU, saute si le GGUF manque) :
  - slugs : les candidats entraînables du registre (granite-4.0-1b, minicpm5-1b, eurollm-1.7b) ;
  - conversation factice (D1) avec deux tours d'appel, dont un appel à deux clés dans un ordre non trié et une valeur entière, et des arguments en chaîne ;
  - côté entraînement, les outils sont donnés triés, comme dans train.jsonl, et passent par le vrai chemin (`_messages_rendus`, `_tools_rendus`) ;
  - côté inférence, `ClientLlama._messages` et `charger_outils()` ;
  - égalité exigée sur chaque préfixe qui précède un tour `assistant`.

  On y ajoute `test_jeu_v1_rendu_identique_a_llama_server`, qui reprend la mesure ci-dessus sur data/train/v1 et saute si le jeu est absent. Ce test lit les données mais n'en génère aucune.
- **Tests rapides** :
  - décodage : ordre conservé, entrée non modifiée, JSON illisible ou non-objet refusé, balises inchangées ;
  - `_tools_rendus` : ordre du fichier, outil inconnu ou divergent refusé ;
  - minicpm5 sans poids : faux tokenizer dont le template appelle `.items()`.

**Q5, effet sur le masque et sur le jeu v1.**
- Sur les 503 lignes, 91 (RD) ont des outils, avec 114 tours d'appel portant 147 `tool_calls` (123 à 1 clé, 19 à 2 clés, 5 à 3 clés ; 11 dans un ordre non trié ; 2 valeurs entières).
- **granite-4.0-1b et eurollm-1.7b** (masque `conversation`) : 91 exemples sur 503 contiennent des outils. Pour granite, seul le bloc `<tools>` du prompt change (non supervisé). Les tours d'appel supervisés sont identiques (chaîne et objet donnent le même texte). Pour EuroLLM, le texte ne change pas.
- **minicpm5-1b** (`par-tour`) : 205 exemples sur 617 contiennent des outils, dont 114 qui supervisent un tour d'appel et 91 une réponse finale. Aujourd'hui, tout Run échoue sur ces lignes. Après correctif, le corps des 114 tours d'appel est le format `<function …>` que llama-server rend dans l'historique. Les comptes de tokens de spec-masque-minicpm5 (1 202 229) ont été mesurés avec les outils triés : il faut les remesurer.
- Le découpage lui-même ne change pas : la normalisation précède le masque.

## §4. EuroLLM : ce que fait l'inférence et options (décision d'Anaël)
**Constat.** En Mode connecté sur RD, EuroLLM ne voit jamais les outils et ne peut pas en appeler. Le Harnais ne reçoit aucun appel valide et termine sur la réponse texte du premier tour, sans passages de l'Index : en Mode connecté, le premier tour n'en contient pas (AD-14). Si la Baseline d'EuroLLM a été mesurée sur RD en Mode connecté, elle l'a été dans ces conditions.

À l'entraînement, le rendu est identique à celui de l'inférence. Mais 91 des 114 tours d'appel n'ont pas de texte, et leur corps supervisé se réduit à `<|im_end|>` : le modèle apprendrait à rendre une réponse vide au premier tour de RD.

| Option | Ce que cela demande | Coût et risque |
|---|---|---|
| A. Statu quo aligné | Rien, ou écarter de la supervision les tours d'appel vides. | L'égalité est déjà vraie. RD n'a pas d'outils pour EuroLLM. Sans filtre, l'entraînement enseigne une réponse vide sur RD. Le filtre demande une règle générique (« tour supervisé sans texte rendu ») à concevoir. |
| B. Exclure EuroLLM des Tâches à outils | Champ de fiche (par exemple `outils = false`). Le Harnais passe alors en Mode local (Index, sans `tools`) et l'entraînement retire les 91 lignes RD, ou les reconstruit sans outils. | Code dans le Harnais et dans le chargement. Baseline RD d'EuroLLM à remesurer en Mode local. RD n'est plus comparable entre candidats. Les données ne sont pas régénérées. |
| C. Template dérivé qui déclare les outils | `chat_template.jinja` dérivé (description des `tools` dans le système, appels en balises `<tool_call>`), imposé aux deux côtés, avec le protocole `balises-tool-call` (AD-13 : réécriture de l'historique et analyse des balises par le client, déjà en place). | Écart à AD-7 (template non officiel) à consigner. Le texte du template est à rédiger (consigne d'outil, pas une Donnée d'entraînement, mais D1 à vérifier). Le modèle de base ne connaît pas le format, donc Baseline RD faible et à remesurer. Le tokenizer d'entraînement devra recevoir le même template. Coût moyen. |
| D. Retirer EuroLLM du fine-tuning | `entrainable = false` (Baseline seulement), comme les Qwen. | Aucun code. On perd le seul candidat européen de moins de 2B. Le défaut d'inférence sur RD reste dans sa Baseline (à documenter). |

La « reproduction du format générique de llama-server » n'est pas une option : b11429 n'en applique aucun à ce template (mesuré).

## Boundaries
- **Toujours** : la référence est le rendu de llama-server sur les messages du client. Les données ne sont jamais modifiées. Les normalisations ne s'appliquent qu'au rendu.
- **Jamais** : de slug en dur, de régénération de data/train/v1, de changement du client d'inférence ni de `balises-tool-call`. On ne touche pas aux fichiers de feat/masque-minicpm5 avant sa fusion. Le correctif s'implémente après elle, sur `chargement.py` et `run.py`.

## Risques et points non vérifiés
- La règle interne de llama.cpp n'est pas connue : seul son comportement sur trois templates est observé. Un template futur qui rend une chaîne autrement que `tojson(objet)` casserait l'égalité. Le test lent le détectera, sans le prévenir.
- `content: null` : llama-server le rend comme une absence, mais le rendu HF n'a pas été isolé avec les outils de l'inférence. Pour EuroLLM avec les outils triés, HF écrit `None`. Le jeu v1 ne contient aucun `null`. Il est conseillé d'ajouter au correctif une suppression des `content` nuls, couverte par le test.
- Non mesuré :
  - l'analyse, à l'inférence, des appels générés par minicpm5-1b (`<function …>`) et granite (`<tool_call>`) : seul le rendu est comparé ;
  - les GGUF F16 et le GGUF exporté après fine-tuning (contrôle CA2) ;
  - les données ORPO (aucune n'existe encore).
- `data/preferences.py` génère les réponses rejetées avec les outils triés de la ligne : leur prompt diffère légèrement de celui de l'inférence. Effet faible, non mesuré.
- Les prompts système et utilisateur de train.jsonl ne sont pas comparés à ceux du Harnais : seul le rendu des messages fournis l'est.

## Auto Run Result
- Statut : draft. Spec seule, sans code. Aucun appel payant, aucun téléchargement, aucune donnée générée ni modifiée.
- Mesures : 4 lancements CPU de llama-server, un à la fois. Scripts dans le scratchpad, non versionnés ; leur logique devient le test lent proposé.
- À confirmer par Anaël :
  - l'option EuroLLM (§4) ;
  - l'invariant d'empreinte `rendu_outils` ;
  - la question de la Baseline d'EuroLLM sur RD en Mode connecté.
