---
title: "Variante d'entraînement du chat template de minicpm5-1b (option 1)"
type: 'feature'
created: '2026-10-17'
status: 'draft'
baseline_commit: '18ad3ea'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-service-public-slm-fine-tuning-2026-10-12/ARCHITECTURE-SPINE.md (AD-7, H-MASQUE)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-candidats-registre.md (section Revue, options 1 à 4)'
  - '{project-root}/_bmad-output/implementation-artifacts/journal-decisions-nuit.md (D-nuit-A1-22)'
warnings:
  - "Écart à AD-7 (« rendu par le template officiel et par lui seul ») : à consigner, AD-7 n'est pas réécrit."
  - "Écart résiduel entre entraînement et inférence sur l'historique des conversations à plusieurs tours assistant : voir Risques, R1. À confirmer par Anaël."
---

## Intent
Décision d'Anaël du 2026-10-17 : option 1 de la revue de `spec-candidats-registre.md`. Avec `chat_template_kwargs = { enable_thinking = false }`, l'amorce de génération de minicpm5-1b (`add_generation_prompt=True`) se termine par `<|im_start|>assistant\n<think>\n\n</think>\n\n`. Le template officiel n'écrit jamais ce bloc dans un tour `assistant` rendu. `masque.intervalles_assistant` refuse donc dès le premier tour, et `chargement.pretokeniser` refuse tout Run sur minicpm5-1b (story 11.2 bloquée). ORPO est bloqué de la même façon : `preparer_preferences` exige que le rendu complet prolonge l'amorce.

À l'entraînement, chaque tour `assistant` est rendu avec le bloc vide en tête. Le masque supervisé commence après le bloc, comme à l'inférence, où le modèle génère après l'amorce. L'inférence ne change pas.

Faits vérifiés sur le tokenizer local (CPU, révision `87179e5`), pour une conversation avec système, 3 tours, un tour vide et un appel d'outil à contenu vide :
- pour chaque tour `k`, `rendu(messages[:k])` est un préfixe de l'amorce et du rendu `rendu(messages[:k+1])` ;
- l'amorce vaut toujours `rendu(messages[:k]) + "<|im_start|>assistant\n" + "<think>\n\n</think>\n\n"` ;
- le tour rendu vaut `"<|im_start|>assistant\n" + corps + "<|im_end|>\n"`, et le corps commence souvent par `<` (`<function …`, `<|im_end|>` pour un tour vide). On ne peut donc pas déduire le bloc du plus long préfixe commun : il doit être déclaré ;
- tokenisation de `…</think>\n\n` suivi du corps : frontière nette (`\n\n` | `R`, `<function`, `<|im_end|>`). Exception : un corps qui commence par `\n` donne un token `\n\n\n` à cheval sur la frontière, et le masque le refuse (voir R4).

## Approach

### Où vit la variante : dérivée par programme, déclarée dans la fiche
Il n'y a pas de fichier Jinja de variante. La variante est le rendu officiel, dans lequel un bloc déclaré est inséré en tête de chaque tour `assistant`. Ce mécanisme est générique : il dépend seulement de la fiche, pas du slug.

- **Schéma** (`core/schemas/config_modele.py`) : sous-schéma `VarianteEntrainement(SousSchema)` avec `bloc_amorce: str` (non vide), et champ `variante_entrainement: VarianteEntrainement | None = None` dans `ConfigModele`. Un validateur refuse la variante sur un modèle `embedding` ou `entrainable = false`. Le sous-schéma pourra recevoir d'autres options plus tard (voir Qwen3.5).
- **Fiche** `config/modeles/minicpm5-1b.toml` : table `[variante_entrainement]` avec `bloc_amorce = "<think>\n\n</think>\n\n"` (chaîne TOML de base, `\n` échappés). Un commentaire renvoie à cette spec et à l'écart à AD-7.
- **Rendu** (`train/masque.intervalles_assistant`, seul point de calcul). Si `config.variante_entrainement` est absent, le code reste inchangé. Sinon, avec `B = bloc_amorce`, pour chaque message `assistant` d'indice `k` :
  1. `amorce = rendu(messages[:k], add_generation_prompt=True)` et `jusque = rendu(messages[:k+1])`, comme aujourd'hui (mêmes `tools` et mêmes kwargs) ;
  2. `amorce` doit se terminer par `B`, sinon `ErreurMasque` (« bloc d'amorce absent de l'amorce : kwargs ou template changés ») ;
  3. `ouverture = amorce[:-len(B)]` doit être un préfixe de `jusque`, sinon `ErreurMasque` ;
  4. si `jusque[len(ouverture):]` commence déjà par `B`, c'est un `ErreurMasque` (bloc déjà rendu, par exemple par un `reasoning_content`). On n'insère jamais deux fois ;
  5. `texte_officiel.startswith(jusque)` est contrôlé, comme aujourd'hui (une réécriture de l'historique reste refusée) ;
  6. la position d'insertion dans le texte officiel est `len(ouverture)`. Le tour officiel couvre `[len(ouverture), len(jusque))`.

  Le texte final est le texte officiel complet, avec `B` inséré à chaque position (décalage cumulé). Les intervalles des tours commencent après `B` : le bloc est hors de la perte, comme l'amorce à l'inférence. Le bloc du tour `k` occupe `[debut_k - len(B), debut_k)` du texte rendu, ce qui permet aux tests de le retirer sans champ supplémentaire. `RenduMasque` et la tokenisation (texte complet tokenisé d'un coup, contrôle des chevauchements) ne changent pas.
- **Tour vide** : avec la variante, un tour `assistant` vide rend `B + "<|im_end|>\n"`, donc du texte. Il est accepté et supervisé sur la fin de tour, comme ce que le modèle produirait à l'inférence. Le filtrage des réponses vides relève des données, hors périmètre.
- **ORPO** (`chargement.preparer_preferences`) : un seul chemin, avec ou sans variante. Il appelle `masque.intervalles_assistant(debut + suite)`. `prompt` est le texte jusqu'au début du premier tour de `suite`, et la réponse est le reste. Un `ErreurMasque` devient `ManifesteInvalide` avec le numéro de paire. Sans variante, le résultat est identique à aujourd'hui : `prompt = amorce`, et la réponse vaut `complet[len(amorce):]`.

Rejeté : un fichier versionné `config/modeles/minicpm5-1b/chat_template.entrainement.jinja`, copie modifiée du template officiel de 9 Ko. AD-7 veut éviter justement un « chat template réécrit à la main ». Cette copie dériverait sans bruit à chaque changement de révision, et son équivalence ne serait prouvée que sur des conversations d'exemple. Avec la dérivation par programme, le texte produit est le même que celui de la variante Jinja de l'option 1, et l'équivalence est contrôlée à l'exécution sur chaque conversation. **À confirmer par Anaël** : « variante de template » s'entend ici au sens du texte rendu, pas d'un fichier.

### Garantie d'équivalence (contrôlée à l'exécution, puis testée)
Pour toute conversation acceptée :
- **G1** : en retirant les blocs insérés du texte de la variante, on retrouve, octet pour octet, le rendu officiel complet (mêmes `tools` et mêmes kwargs). C'est vrai par construction.
- **G2** : pour chaque tour `assistant` `k`, `texte[:debut_k]` privé des blocs des tours antérieurs est égal à l'amorce officielle `rendu(messages[:k], add_generation_prompt=True)`. Pour le premier tour `assistant`, l'égalité est exacte, octet pour octet, sans rien retirer.
- **G3** : le texte supervisé du tour `k` (`texte[debut_k:fin_k]`) est égal au corps officiel `jusque_k[len(ouverture_k):]`.

Limite : la demande vise un préfixe de chaque tour égal à l'amorce officielle. G2 ne la satisfait pas au-delà du premier tour. Avec l'option 1, les tours `assistant` antérieurs portent le bloc dans le texte d'entraînement, alors que l'amorce officielle, rendue par le template, n'en porte pas. Voir R1.

### Inférence et export : inchangés
- `inference/serveur.py` lit des champs nommés (`chat_template_kwargs`, `reasoning`, `chat_template_force`) et ignore `variante_entrainement`. `--chat-template-kwargs` et `--jinja` ne changent pas. `inference/`, `evaluation/` et `benchmarks/` ne lisent pas le nouveau champ.
- Le tokenizer n'est jamais modifié : la variante n'est pas posée sur `tokenizer.chat_template`. `sha_chat_template(tokenizer)` reste le SHA du template officiel, inscrit dans `run.json` (`chat_template_sha256`).
- Export (`train/export.fusionner`) : le tokenizer est rechargé depuis `dossier_base` et sauvegardé tel quel, puis `convert_hf_to_gguf` embarque `tokenizer.chat_template`, donc le template officiel. Le contrôle bloquant CA2 (`cli/export.controler_format`) compare le SHA embarqué à `run.manifeste.chat_template_sha256`, qui est le SHA officiel. Rien à changer. La variante n'est jamais exportée, et AD-7 ne l'impose pas : la revue technique d'AD-7 (`review-verification-tech.md`) prévoit au contraire un GGUF qui embarque le template officiel.

### Empreinte (provenance)
- `train/run.py` : `CLES_INVARIANTS` reçoit `"variante_template"`, qui vaut `config_modele.variante_entrainement.model_dump()` ou `None`. `invariants(...)` le reçoit en paramètre. Deux Runs d'une campagne doivent avoir la même variante. Un ancien run sans la clé lit `None` et reste comparable pour granite et eurollm.
- `resolue["modele"]["variante_entrainement"]` est archivé dans `run.json`, à côté de `chat_template_kwargs`.
- La provenance du texte d'entraînement est donc : SHA du template officiel, kwargs, `variante_template` et `VERSION_MASQUE`. `VERSION_MASQUE` reste à 1, car le calcul ne change pas sans variante. La variante est identifiée par son propre invariant.

### Granite et eurollm
Aucun effet. Leurs fiches n'ont pas de `variante_entrainement`, donc le chemin de `intervalles_assistant` est inchangé, leur texte et leurs labels sont identiques, et l'invariant vaut `None`. Leurs tests rapides et lents passent sans modification. Un test vérifie que la sortie est identique à celle de la base sans variante.

### Consignation de l'écart à AD-7
- Nouvelle entrée datée dans `journal-decisions-nuit.md`, au format des entrées D-nuit (Décision, Justification), qui prolonge D-nuit-A1-22. Elle dit que le rendu d'entraînement de minicpm5-1b insère `bloc_amorce`, et elle rappelle l'écart à AD-7, les garanties G1 à G3, l'export inchangé, la décision d'Anaël du 2026-10-17 et le renvoi vers cette spec.
- Commentaire dans `config/modeles/minicpm5-1b.toml` et docstrings de `masque.py` et de `rendu.py` : le repli H-MASQUE « balises `generation` » devient « variante déclarée dans la fiche ».
- Ni AD-7, ni H-MASQUE, ni `decisions.md` ne sont modifiés. **À confirmer par Anaël** : faut-il une ligne dans `decisions.md` (sous D8 ou dans une nouvelle décision) ? Ce document de décision n'est pas touché sans son accord.

### Qwen3.5 (hors périmètre)
Le mécanisme ne le couvre pas. Le template de Qwen3.5 retire le bloc des tours antérieurs à la dernière question : `rendu(messages[:k+1])` n'est plus un préfixe du rendu complet, et l'étape 5 refuse. Le sous-schéma pourra le couvrir sans cas particulier, avec une option `decoupage = "par-tour"` : un exemple par tour `assistant`, dont le contexte est l'amorce officielle `rendu(messages[:k], add_generation_prompt=True)` et dont seul le corps du tour `k` est supervisé. Ce découpage traite à la fois la réécriture de l'historique de Qwen et l'écart R1 de minicpm5. En contrepartie, il multiplie les tokens par le nombre de tours `assistant` de chaque conversation. Report.

## Tests
Les fixtures sont des chaînes factices (`"<réponse-factice-1>"`, `"<question-factice-2>"`, etc.), conformément à D1.

**Rapides, sans poids** (`tests/train/test_masque.py`), avec le faux tokenizer `AmorceRaisonnementVide` existant (amorce `+ "<think></think>"`) et une `ConfigModele` de test qui déclare `bloc_amorce = "<think></think>"` :
- conversations à 1, 2 et 3 tours `assistant`, avec et sans message système, un tour vide et un tour avec `tool_calls` suivi d'un message `tool`. Pour chacune, G1, G2 (égalité exacte au premier tour) et G3, labels non masqués égaux aux corps ;
- `test_amorce_absente_du_tour_rendu_refusee` reste valable sans variante. L'ensemble des cas refusés sans variante ne change pas ;
- refus avec la variante : amorce qui ne se termine pas par le bloc (kwargs changés), ouverture qui n'est pas un préfixe du tour, bloc déjà présent dans le tour, réécriture de l'historique (`reecrit_historique=True`) ;
- sans variante : texte, tours et labels identiques à la base sur `conversation()` et sur les conversations aléatoires existantes.

**Schéma** (test de `config_modele` existant ou voisin) : `bloc_amorce` vide refusé, variante refusée sur `embedding` ou `entrainable = false`, fiche minicpm5-1b chargée avec le bloc exact `"<think>\n\n</think>\n\n"`.

**ORPO** (`tests/train/test_chargement.py` ou équivalent) : paire factice avec la variante. `prompt` est égal à l'amorce officielle, `chosen` et `rejected` commencent par le corps (sans le bloc). Sans variante, la sortie est identique à aujourd'hui.

**Run** (`tests/train/test_run.py` ou équivalent) : `variante_template` est présent dans les invariants. Une campagne mélangeant `None` et la variante est refusée, et un ancien run sans la clé est comparable à `None`.

**Lents** (`-m lent`, tokenizer local sur CPU, sans GPU) :
- `test_candidat_reel_masque_sur_les_tours_assistant` : le `xfail(strict=True)` de minicpm5-1b est retiré, et le test doit passer ;
- nouveau test paramétré sur minicpm5-1b (tokenizer réel, `enable_thinking = false`), avec : système et 1 tour ; 2 tours ; système et 3 tours ; tour vide ; appel d'outil à contenu vide, puis `tool`, puis réponse ; `conversation_outils()`. Il contrôle G1, G2 et G3 sur chaque tour et vérifie qu'aucun token n'est à cheval. Le template gère les outils, qui sont passés par `tools=[OUTIL]` ;
- `test_rendu_identique_a_llama_server_jinja` : minicpm5-1b est ajouté. Il vérifie que l'amorce officielle HF, référence de G2, est bien celle que `llama-server --jinja --reasoning off --chat-template-kwargs` envoie à l'inférence. Il tourne en variante CPU de llama.cpp, à lancer quand le GPU est libre, ou en CPU s'il est disponible.

Commandes : `uv run --no-sync pytest -q --tb=short tests/train tests/core`, puis `uv run --no-sync pytest -q -m lent -k "minicpm5 or candidat_reel" tests/train/test_masque.py`, puis la suite complète, `ruff check` et `ruff format --check`.

## Risques et points non vérifiés
- **R1 (à confirmer par Anaël)** : écart résiduel sur l'historique. À l'inférence, les tours `assistant` passés, renvoyés par le Harnais (boucle d'outils RD), sont rendus par le template officiel, donc sans bloc. Un contenu préfixé par le bloc n'y change rien : le template le retire, car le raisonnement est vide. Avec l'option 1, ces mêmes tours portent le bloc dans le texte d'entraînement. Le texte supervisé et l'amorce du premier tour sont exacts. Le contexte des tours suivants diffère de quelques tokens. Les conversations à un seul tour `assistant` (la plupart des Tâches) ne sont pas touchées. Seule l'option `decoupage = "par-tour"` (voir Qwen3.5) donne une égalité exacte pour tous les tours.
- **R2, non vérifié** : je n'ai pas vérifié que llama-server b11429 (`--reasoning off` et `enable_thinking = false`) envoie exactement l'amorce HF de minicpm5-1b. Le test lent `/apply-template` le vérifiera, mais il n'a pas tourné (pas de llama-server lancé pour cette spec).
- **R3, non vérifié** : je n'ai pas vérifié non plus que le template embarqué par le GGUF officiel est identique au template HF. Le contrôle `chat_template` de `fetch` (avec `chat_template_force = false`) l'affirme, mais je ne l'ai pas relancé. L'embarquement du template officiel par l'export a été établi à la lecture du code, sans export réel.
- **R4** : un corps de tour qui commence par `\n` produit un token `\n\n\n` à cheval sur la frontière. `ErreurMasque` s'en suit et `pretokeniser` refuse alors le Run entier, pas seulement la ligne. Le risque existe déjà pour les autres modèles, mais il est plus probable ici, puisque l'amorce finit par `\n\n`. Normaliser ces corps à la construction des données est hors périmètre (report).
- **R5** : je ne connais pas l'effet sur le modèle d'un bloc vide écrit dans l'historique, une forme que le template officiel ne produit jamais.
- **R6** : un message portant `reasoning_content`, ou un contenu avec `</think>`, est refusé par l'étape 4 (bloc déjà présent) ou rendu autrement par le template. Les données du projet n'en portent pas (`enable_thinking = false`), mais ce n'est pas vérifié sur `train.jsonl`, qui n'est pas lu ici.

## Fichiers (implémentation)
`src/slmsp/core/schemas/config_modele.py`, `config/modeles/minicpm5-1b.toml`, `src/slmsp/train/masque.py`, `src/slmsp/train/chargement.py` (ORPO), `src/slmsp/train/run.py`, docstring de `src/slmsp/train/rendu.py`, `tests/train/test_masque.py` et les tests voisins de schéma, de chargement et de run, `_bmad-output/implementation-artifacts/journal-decisions-nuit.md`.

## Auto Run Result
- Spec seule, en `draft`, pour relecture avant le code (story à risque).
- Décision prise seul, selon la règle « la plus simple et la plus réversible » : variante dérivée par programme, avec le bloc déclaré dans la fiche, plutôt qu'un fichier Jinja (à confirmer par Anaël).
- Points « à confirmer par Anaël » : R1 (option 1 telle quelle ou découpage par tour), sens de « variante de template », ligne éventuelle dans `decisions.md`.
