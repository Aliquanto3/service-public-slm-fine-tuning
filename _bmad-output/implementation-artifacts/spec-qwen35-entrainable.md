---
title: 'Qwen3.5 entraînables sous Windows natif, tour vision gelée et export multimodal'
type: 'feature'
created: '2026-10-18'
status: 'ready-for-dev'
baseline_commit: 'c578310'
review_loop_iteration: 1
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/enquete-entrainement-hybrides-2026-10-18.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-precision-base.md (story A, branche feat/precision-base)'
  - '{project-root}/_bmad-output/planning-artifacts/decisions.md (D2, D7, D8, registre)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-masque-minicpm5.md (G1 à G4)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-outils-rendu.md (R7)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-6-export-gguf-et-controle-apres-quantification.md'
  - '{project-root}/docs/reprise-deuxieme-pc.md (deux phases d''installation)'
warnings:
  - 'oversized : spec de cadrage de trois stories (B1, B2, B3) ; chaque story reste livrable seule'
  - 'dépend de la story A (`precision_base`, clé de run, branche feat/precision-base), non fusionnée au 2026-10-18 : B1 et B2 partent de main après la fusion de A (mêmes fichiers touchés)'
deferred:
  - 'mmproj de base épinglé (`[gguf_mmproj]` communautaire) : pas tant qu''il n''y a pas de cas d''usage vision (décision d''Anaël du 2026-10-18)'
  - 'publication du mmproj dans le dossier de publication : B3 ne publie que le GGUF texte'
  - 'ORPO sur un modèle multimodal, si TRL ne le prend pas en charge (B2.6) : story dédiée'
---

## Intent

**Problème.** Qwen3.5-2B et Qwen3.5-0.8B sont des hybrides Gated DeltaNet (`linear_attention`, déclarées sous `text_config.layer_types`) et des VLM (`vision_config`, architecture `Qwen3_5ForConditionalGeneration`). D8 les limite à la Baseline (`entrainable = false`). La sonde refuse tout `vision_config`, et `train run` le retire du contrôle quand `exclure_vision = true`, puis charge `AutoModelForCausalLM` et pose un LoRA `all-linear`. L'export ne produit qu'un GGUF texte. L'enquête du 2026-10-18 (piste 3) montre que l'entraînement tient sous Windows natif avec triton-windows 3.8.0.post29 et flash-linear-attention 0.5.2 : 1 042 tokens/s à 2048 et 1 054 tokens/s à 4096 pour Qwen3.5-2B (3,55 et 3,70 Gio réservés), base en bf16 sans cast fp32, tour vision gelée. Seul `causal_conv1d_fn` reste en repli torch.

**Approche.** On met les noyaux GDN dans un extra optionnel du projet principal, avec un contrôle du chemin rapide qui est consigné. On charge la classe multimodale, on gèle la tour vision et on la vérifie, et le LoRA ne cible que `language_model`. On valide le masque sur le tokenizer réel. La fusion se fait sur la classe multimodale, puis on produit un GGUF texte et un `mmproj`. Les fiches Qwen3.5 passent `entrainable = true`, et D8 est révisé. Ministral 3 reste hors périmètre : sa fiche ne déclare pas `multimodal`, donc la sonde le refuse toujours, et `train run` garde son comportement actuel (vision exclue retirée du contrôle).

## Décisions

1. **Environnement : extra `gdn` du projet principal, pas un `envs/` séparé.**
   - `[project.optional-dependencies] gdn = ["triton-windows==3.8.0.post29 ; sys_platform == 'win32'", "flash-linear-attention==0.5.2"]`, sans extra `[cuda]` ni `[cpu]` : ceux de `fla-core` tirent `triton>=3.3` (paquet Linux). On ajoute `[{ extra = "fetch" }, { extra = "gdn" }]` à `conflicts` : `flash-linear-attention` 0.5.2 déclare `transformers>=4.45.0` (non épinglé), et transformers 5.17.0 est en conflit avec `huggingface-hub` 2.2.0 de `fetch`.
   - Faisabilité vérifiée en relecture (copie de `pyproject.toml` et `uv.lock` dans un dossier temporaire, `uv lock`) : la résolution ajoute exactement `einops` 0.8.2, `fla-core` 0.5.2, `flash-linear-attention` 0.5.2 et `triton-windows` 3.8.0.post29 ; torch reste en 2.14.1+cu130, transformers en 5.17.0, accelerate en 1.15.0 et bitsandbytes en 0.50.2. Le lock du dépôt est en `revision = 5` ; le uv 0.11.7 du portable le réécrit en `revision = 3` avec des marqueurs différents (654 lignes de diff). Le lock se régénère donc avec un uv au moins aussi récent que celui qui l'a écrit, et son diff ne doit porter que sur ces quatre paquets et la ligne de conflit.
   - Installation : phase 2 de `docs/reprise-deuxieme-pc.md` complétée par `--extra gdn` (`uv sync --extra data --extra judge --extra bench --extra train --extra gdn --extra app`). La phase 1 (`fetch`) ne change pas : `gdn` n'y figure pas, et le conflit déclaré l'interdit. Toutes les commandes de cette spec passent par `uv run --no-sync`, car un `uv run` simple resynchronise sans extras et retirerait torch et fla.
   - Raisons :
     1. transformers choisit les noyaux à l'import du module de modélisation, dans le processus même de l'entraînement (`use_kernel_func_from_hub_with_fallback`, `transformers/integrations/hub_kernels.py`). Un sous-processus comme `envs/unsloth` obligerait à dupliquer `run.py`, le masque et le collateur.
     2. `fla-core` 0.5.2 ne déclare que `einops` hors extras, et `flash-linear-attention` 0.5.2 ne déclare que `fla-core` et `transformers` : aucun `override-dependencies` n'est nécessaire (contrairement à unsloth).
     3. `triton-windows==3.8.0.post29` se résout déjà avec torch 2.14.1+cu130 dans `envs/unsloth/uv.lock`.
     4. Un extra séparé de `train` laisse intact l'environnement des runs déjà mesurés (MiniCPM5, Granite), et il s'annule en retirant une ligne.
2. **Chemin rapide contrôlé, refus par défaut (décision d'Anaël du 2026-10-18).**
   - Sans fla, `train run` refuse par défaut un modèle à couches `linear_attention`. La seule échappatoire est `repli_torch = true` dans le TOML du run, bornée à `longueur_max <= 4096` : au-delà, le repli n'a pas été mesuré sous Windows (enquête piste 2 : 536 à 633 tokens/s jusqu'à 4096, 375 à 8192 près du seuil de VRAM).
   - `train sonde-env` mesure toujours et ne refuse jamais pour cette raison : il consigne le résultat du contrôle.
   - Mécanisme du contrôle : transformers résout l'implémentation une fois, à l'import du module de modélisation, et la garde dans la fermeture de la fonction décorée. La source fiable est donc cette fermeture (implémentation dont le module commence par `fla.`), lisible dès que la pile est importée, avant tout chargement de poids. L'avertissement « `X` is falling back to its reference PyTorch implementation » n'est qu'un complément : il part au premier appel (premier forward), par `logger.warning_once`, donc une seule fois par processus. Il ne peut pas servir seul à un contrôle par longueur ni par variante (sonde `les-deux` de la story A).
   - Seul `causal_conv1d` en repli est attendu et admis (`causal-conv1d` ne se compile pas sans nvcc).
3. **Fiche : nouveau champ `multimodal: Literal["geler-vision"] | None = None`.** Il est orthogonal à `exclure_vision`, qui ne règle plus que l'inférence du Harnais (pas de `--mmproj`) et reste `true`. `multimodal = "geler-vision"` exige un `vision_config` dans `config.json`. Il fait charger `AutoModelForImageTextToText` et cibler le LoRA sur `language_model` seul.
4. **Contrôle `dense` (fetch).** `linear_attention` est admis avec `entrainable = true` comme avec `false`. La présence de fla ne se vérifie pas au fetch : les extras `fetch` et `gdn` sont en conflit, et la garde vit dans `train`. `mamba` exige toujours `entrainable = false`, y compris mélangé à `linear_attention`, et un type inconnu écarte toujours le modèle. `exiger_entrainable` ne change pas.
5. **mmproj produit par conversion, pas épinglé (décision d'Anaël du 2026-10-18).** `convert_hf_to_gguf.py --mmproj` de b11429 enregistre `Qwen3_5ForConditionalGeneration` (`conversion/qwen3vl.py`, `Qwen3VLVisionModel`), ce qui a été vérifié dans `vendor/llama.cpp/b11429/src`. B3 produit le mmproj du modèle fine-tuné depuis le dossier fusionné, avec le même tag llama.cpp que le GGUF texte. Aucun `[gguf_mmproj]` de base n'est épinglé tant qu'il n'y a pas de cas d'usage vision (reporté, `deferred`).
6. **Exemples d'entraînement texte seul.** Le tokenizer reste `AutoTokenizer` (pas d'`AutoProcessor`), sans `pixel_values`.
7. **ORPO multimodal (décision d'Anaël du 2026-10-18).** Si TRL ne prend pas en charge ORPO sur un modèle ConditionalGeneration avec un tokenizer, ORPO est refusé explicitement pour `multimodal`, avec un message clair, et reporté à une story dédiée. Ce n'est pas bloquant pour B2 : SFT suffit à livrer.
8. **Ordre de `verifications.CANDIDATS` (décision d'Anaël du 2026-10-18), changé par B2.** Les entraînables sont rangés par score de Baseline : `minicpm5-2b` (41,1), `qwen3.5-2b` (36,0), `granite-4.0-1b` (33,4), `minicpm5-1b` (24,4), `granite-4.0-350m` (15,9), puis `qwen3.5-0.8b` (27,5) en dernier des entraînables, par choix d'Anaël. Viennent ensuite les « Baseline seulement », dans leur ordre actuel : `eurollm-1.7b`, `granite-4.0-h-350m`, `granite-4.0-h-1b`. Les scores sont ceux qu'a donnés Anaël ; la spec ne les recalcule pas.

## Découpage

| Ordre | Story | Dépend de | Livrable seul |
|---|---|---|---|
| 0 | A : `precision_base` (clé de run, option `--precision-base` de la sonde) | — | oui |
| 1 | **B1** : extra `gdn` et contrôle du chemin rapide | A fusionnée (mêmes fichiers : `config.py`, `run.py`, `environnement.py`, `cli/train.py`, `docs/reprise-deuxieme-pc.md`) | oui : aucune fiche ne change |
| 2 | **B2** : chargement multimodal, vision gelée, sonde, `train run` (SFT, ORPO), masque, fiches, CANDIDATS, D8 | A, B1 | oui : les Qwen3.5 s'entraînent et produisent un adaptateur |
| 3 | **B3** : export multimodal (GGUF texte, mmproj, Q4_K_M, sondes) | B2 (champ `multimodal`, `classe_modele`, cibles regex) | oui : les tests unitaires utilisent des fixtures ; le bout en bout réel attend un run de B2 |

**Dépendance à la story A.** A règle la précision par run (`RunConfig.precision_base`, défaut `"fp32-kbit"`) et par option de sonde (`--precision-base {fp32-kbit,bf16,les-deux}`), pas par fiche. B2 ne la réécrit pas. B2 en dépend en quatre points :
1. `classe_modele` s'insère dans `environnement.charger_modele` et `methodes.charger_modele` tels que A les laisse (paramètre `precision_base`). Le choix de la classe est orthogonal à la précision.
2. Les runs Qwen3.5 portent `precision_base = "bf16"`, et les sondes réelles passent `--precision-base bf16`. Avec le cast fp32, Qwen3.5-2B déborde dès 1024 tokens (5,78 Gio, mesuré sous WSL avec fla, enquête piste 1 ; non mesuré sous Windows natif). B2 ne refuse pas `fp32-kbit` : la sonde le constate.
3. Avec `--precision-base les-deux`, A recharge le modèle une fois par variante : `verifier_gel_vision` et le contrôle des noyaux sont consignés pour chaque chargement.
4. B1 suit la règle de A pour `repli_torch` : la clé n'est écrite dans le `toml` résolu de `run.json` que hors défaut (A le fait pour `precision_base`), sinon `train run --reprendre` refuserait tout run créé avant B1.

## Story B1 : extra `gdn` et contrôle du chemin rapide

**Critères d'acceptation**
1. `pyproject.toml` porte l'extra `gdn` de la décision 1 et la ligne de `conflicts`. `uv lock` passe ; `uv.lock` ajoute `triton-windows` 3.8.0.post29, `flash-linear-attention` et `fla-core` 0.5.2, et `einops`, sans autre changement de version (torch 2.14.1+cu130, transformers 5.17.0) et sans changement de `revision` du lock. `docs/reprise-deuxieme-pc.md` ajoute `--extra gdn` à la phase 2 et dit pourquoi.
2. `train.environnement.noyaux_gdn_disponibles() -> dict` répond sans importer torch : `find_spec` de `fla` et de `triton`, et les versions de `triton-windows`, `fla-core` et `flash-linear-attention` (`None` quand un paquet manque). `versions_pile()` ajoute ces trois versions. Dans `run.json`, elles figurent déjà dans `environnement.paquets` (`core.artefacts._paquets_installes`).
3. `train.environnement.a_couches_gdn(config_poids) -> bool` cherche `linear_attention` dans `layer_types` de toutes les sous-configurations (`_sous_configs` : racine et `text_config`, où Qwen3.5 les déclare).
4. `train.environnement.controler_noyaux_gdn(pile, config_poids, *, avertissements=()) -> dict | None` renvoie `None` sans couche `linear_attention`. Sinon il renvoie `{"chunk_gated_delta_rule": "fla" | "torch", "causal_conv1d": "fla" | "torch", "replis": [...], "avertissements": [...]}`.
   - Source principale : la fermeture des fonctions décorées du module de modélisation (`chunk_gated_delta_rule`, `causal_conv1d_fn`), module trouvé par `architectures[0]` de `config.json`. `fla` si le module de l'implémentation commence par `fla.`.
   - Complément : les avertissements « is falling back to its reference PyTorch implementation » capturés sur le logger `transformers` au premier pas, passés par `avertissements`. Un avertissement qui contredit la fermeture fait retenir `torch`.
5. `RunConfig.repli_torch: bool = False`. Un validateur refuse `repli_torch = true` avec `longueur_max > 4096`. La clé n'est écrite dans le `toml` résolu de `run.json` que si elle vaut `true` (règle de A).
6. `train run`, pour un modèle à couches `linear_attention`, refuse (`ConfigurationInvalide`, avant le verrou GPU, sans créer de run) :
   - si `fla` ou `triton` n'est pas importable, sauf `repli_torch = true`, avant le chargement de la pile ; le message cite la commande de la phase 2 avec `--extra gdn` ;
   - si, après `charger_pile`, `controler_noyaux_gdn` donne `chunk_gated_delta_rule = "torch"`, sauf `repli_torch = true`.
   La fonction de refus s'appelle `exiger_noyaux_gdn(config_poids, slug, *, repli_torch, controle=None)`. Elle n'est appelée que par `train run`, `--reprendre` compris.
7. Consignation, hors `run.json` : ce fichier est écrit une fois, à la création du run, et sa config résolue est comparée par `--reprendre`.
   - `train run` écrit `noyaux.json` dans le dossier du run (contrôle avant entraînement, puis complété des avertissements du premier pas), et ajoute un événement `noyaux` à `log.jsonl`. Avec `repli_torch` actif, il ajoute un événement `alerte` « repli torch » à `log.jsonl`.
   - `train sonde-env` ne refuse jamais : `sonde.json` reçoit `noyaux_gdn` (contrôle après import de la pile) et, par mesure, les avertissements capturés pendant cette longueur (souvent vides après la première, à cause de `warning_once`).
   - Rien de cela n'entre dans `CLES_INVARIANTS` : une campagne compare des modèles denses et hybrides.
8. `fetch/verifications.py` : `linear_attention` avec `entrainable = true` donne `ok` (« hybride Gated DeltaNet entraînable, noyaux fla requis à l'entraînement (extra gdn) »). `mamba`, seul ou mélangé à `linear_attention`, avec `entrainable = true`, reste en `echec` (libellé « … inscrire entrainable = false (décision D8) »).

**Tests** (mocks, sans GPU ni fla ; aucun n'est lent)
- `tests/test_pyproject.py` : `test_extra_gdn_en_conflit_avec_fetch` (extra `gdn` aux deux épinglages, sans `[cuda]`, ligne `[fetch, gdn]` dans `conflicts`). `test_extras_et_torch_dans_train_seulement` reste vrai : `gdn` ne déclare pas torch.
- `tests/train/test_environnement.py` :
  - `test_noyaux_gdn_disponibles_sans_fla`, `test_noyaux_gdn_disponibles_avec_fla` (`find_spec` et `importlib.metadata.version` simulés) ;
  - `test_a_couches_gdn_sous_text_config` (forme réelle de Qwen3.5 : `layer_types` sous `text_config` seulement) ;
  - `test_controler_noyaux_gdn_chemin_rapide` (fermeture dont l'implémentation vient d'un faux module `fla.ops…`), `test_controler_noyaux_gdn_repli_detecte` (fermeture torch), `test_controler_noyaux_gdn_avertissement_l_emporte`, `test_controler_noyaux_gdn_modele_dense_none` ;
  - `test_exiger_noyaux_gdn_refuse_sans_fla`, `test_exiger_noyaux_gdn_repli_explicite`, `test_exiger_noyaux_gdn_modele_dense_sans_objet` ;
  - `test_sonde_consigne_noyaux_sans_refuser` (fermeture torch : la sonde mesure et `sonde.json` porte `noyaux_gdn`).
- `tests/train/test_config.py` : `test_repli_torch_borne_a_4096`.
- `tests/train/test_run.py` :
  - `test_run_hybride_refuse_sans_fla_avant_verrou` et `test_run_hybride_refuse_si_repli_sans_option` : aucun dossier `runs/` créé, pile non chargée dans le premier cas ;
  - `test_run_hybride_repli_torch_alerte` (`noyaux.json` et événement `alerte` dans `log.jsonl`) ;
  - `test_run_noyaux_hors_run_json_et_invariants` ;
  - `test_reprise_run_anterieur_sans_repli_torch` (un `run.json` sans la clé reste reprenable).
  Les fiches de test sont des modèles factices à `layer_types` `linear_attention` : les fiches Qwen3.5 restent `entrainable = false` jusqu'à B2.
- `tests/fetch/test_verifications.py` : `test_dense_gated_deltanet_entrainable_admis` remplace `test_dense_gated_deltanet_exige_entrainable_false`, qui est inversé. On réaligne `test_dense_melange_gated_deltanet_et_mamba` (cas `entrainable = true` : `echec`, libellé Mamba). `test_mamba_ecarte_sans_entrainable_false` et `test_hybride_ecarte_en_nommant_les_couches` ne changent pas.
- Mesure réelle, non lancée par la story (GPU) : après B2, `uv run --no-sync slmsp train sonde-env --modele qwen3.5-2b --precision-base bf16 --longueurs 2048,4096`. Commande consignée.

**Fichiers** : `pyproject.toml`, `uv.lock`, `docs/reprise-deuxieme-pc.md`, `tests/test_pyproject.py`, `src/slmsp/train/environnement.py`, `src/slmsp/train/config.py`, `src/slmsp/train/run.py`, `src/slmsp/cli/train.py`, `src/slmsp/fetch/verifications.py`, et les tests cités.

## Story B2 : chargement multimodal, vision gelée, sonde, `train run`, masque, fiches

**Critères d'acceptation**
1. **Schéma** : `ConfigModele.multimodal: Literal["geler-vision"] | None = None`. `multimodal` sans `vision_config` dans `config.json` est refusé au contrôle des poids (`controler_config_modele`), avec un message clair.
2. **Contrôle de la config** : `environnement.controler_config_modele(config, slug, *, multimodal=None)`. Un `vision_config` passe si `multimodal == "geler-vision"`, et le résumé vaut alors `vision_config: "gelee"`. Sinon le message actuel reste (« modèle multimodal … ne charge pas l'encodeur vision »), ce qui garde Ministral 3 refusé par la sonde. Le résumé lit `couches` aussi sous `text_config`. Trois appelants passent `multimodal` de la fiche :
   - `cli/train._sonde_env`, avant le verrou ;
   - `environnement.sonder`, qui reçoit `multimodal` en paramètre : il ne lit aujourd'hui que `config.json` ;
   - `chargement.controler_contraintes`, qui garde le `vision_config` pour `multimodal` au lieu de le retirer. Sans `multimodal`, son comportement actuel ne change pas.
3. **Classe** : un seul point de choix, `train.environnement.classe_modele(pile, multimodal: str | None)`. Il renvoie `AutoModelForImageTextToText` pour `geler-vision`, et `AutoModelForCausalLM` sinon. On lui passe la valeur de la fiche et non un dict, car `config_modele` désigne `config.json` dans `environnement` et la fiche dans `run`. Il est utilisé par `environnement.charger_modele` (sonde), par `methodes.charger_modele` (run, ORPO et `--reprendre` compris), en nf4 comme en bf16, avec la `precision_base` de la story A, et par `export.fusionner` (B3).
4. **Cibles LoRA** : `methodes.cibles_lora(modele, multimodal)` renvoie `"all-linear"` sans `multimodal`. Avec `geler-vision`, elle renvoie la regex `.*language_model.*\.(<noms des Linear et Linear4bit sous language_model>)$`, comme la sonde de l'enquête. Elle ne cible ni `lm_head`, ni `embed_tokens` (TRL `chunked_nll` refuse `lm_head`). La tête MTP n'est pas chargée : transformers 5.17.0 ignore `^mtp.*` (`Qwen3_5PreTrainedModel._keys_to_ignore_on_load_unexpected`), alors que les poids de base en contiennent 15 tenseurs. Appelants :
   - `environnement.poser_lora(pile, modele, multimodal)` (sonde) ;
   - `methodes.poser_adaptateur`, qui a le modèle et passe la cible à `config_lora` (nouveau paramètre `cibles`) ;
   - `sonde.json["lora"]["target_modules"]`, aujourd'hui écrit en dur `"all-linear"`, consigne la cible réelle.
5. **Vision gelée et vérifiée** : `train.environnement.verifier_gel_vision(modele) -> dict` renvoie `{parametres_entrainables, vision_parametres, vision_entrainables}`. Il lève `ConfigurationInvalide` si un paramètre entraînable a un nom sans `language_model`. Il est appelé après la pose de l'adaptateur (neuf, ou SFT rechargé pour ORPO) et avant `train()`. Le résultat va dans `sonde.json` (`gel_vision`, à chaque chargement) et, pour `train run`, dans `gel-vision.json` du dossier du run et un événement de `log.jsonl` (pas dans `run.json`, écrit avant le chargement). Valeur attendue pour Qwen3.5-2B au rang 16 par défaut : 16,8 M paramètres entraînables, 0 en vision (enquête).
6. **ORPO** (décision 7) : une préparation de `ORPOTrainer` (`trl.experimental.orpo`) avec un modèle ConditionalGeneration factice et un tokenizer (pas un processor) est vérifiée par un test. Si TRL traite le modèle comme vision et exige un processor ou des images, ORPO est refusé pour `multimodal` avant le verrou (`ConfigurationInvalide` : « ORPO non pris en charge pour un modèle multimodal, story à venir »), et le report reste dans `deferred`. On ne contourne pas TRL. Le résultat (admis ou refusé) est consigné dans `## Auto Run Result`.
7. **Unsloth** : refusé pour `multimodal`, avant le verrou, à deux endroits : `train run` en `qlora-unsloth`, et `train sonde-env --unsloth` (`envs/unsloth/sonde.py` charge `AutoModelForCausalLM`). `methodes_disponibles` marque `qlora-unsloth` indisponible pour `multimodal`, avec ce motif.
8. **Masque et rendu** : template Qwen3.5 avec `chat_template_kwargs = { enable_thinking = false }` de la fiche, tokenizer réel (`models/<slug>/hf/`, présent sur le portable).
   - Le découpage par défaut (`conversation`) est essayé d'abord.
   - S'il lève `ErreurMasque`, ou si G1 à G4 échouent, la fiche passe `decoupage_masque = "par-tour"`. On s'attend à ce cas, car le template réécrit l'historique (spec-masque-minicpm5). `bloc_amorce` est ajouté seulement si le test le montre nécessaire.
   - Le résultat mesuré (découpage retenu, exemples, tokens supervisés) est consigné dans `## Auto Run Result`.
9. **R7** : le rendu d'entraînement des préfixes RD est égal à `/apply-template` de llama-server (`chat_template_force = true`). Le résultat attendu est 205/205 préfixes sur v1 pour chacun des deux modèles. Un écart bloque le passage `entrainable = true` du modèle en cause, et il est consigné.
10. **Fiches** :
    - `qwen3.5-2b.toml` et `qwen3.5-0.8b.toml` : `entrainable = true`, `multimodal = "geler-vision"`, `exclure_vision = true` (inchangé : le Harnais reste en texte), et `decoupage_masque` selon le critère 8. Les commentaires d'en-tête sont réécrits (D8 révisé, extra `gdn`, vision gelée, `precision_base = "bf16"` dans les runs).
    - `config/publication.toml` : les entrées `qwen3.5-2b` et `qwen3.5-0.8b` restent sans `verifie_le` jusqu'à la relecture d'Anaël (question ouverte).
11. **CANDIDATS** (décision 8) : `fetch/verifications.CANDIDATS` = `minicpm5-2b`, `qwen3.5-2b`, `granite-4.0-1b`, `minicpm5-1b`, `granite-4.0-350m`, `qwen3.5-0.8b`, `eurollm-1.7b`, `granite-4.0-h-350m`, `granite-4.0-h-1b`. Le commentaire et la docstring citent la décision. Les six premiers sont `entrainable = true`, les trois derniers `false`.
12. **decisions.md** (sur demande expresse, comme dans spec-hybrides-baseline) :
    - D8 reçoit le paragraphe ci-dessous ;
    - le registre passe les deux Qwen3.5 en « candidat au fine-tuning », dans l'ordre de CANDIDATS.
    - Texte proposé :
      > **Révision du 2026-10-18 (Qwen3.5 entraînables)**, décision d'Anaël. Les hybrides Gated DeltaNet (`linear_attention`) sont entraînables sous Windows natif avec les noyaux Triton de flash-linear-attention : extra `gdn` (triton-windows 3.8.0.post29, flash-linear-attention 0.5.2). La mesure donne 1 042 tokens/s à 2048 et 1 054 à 4096 pour Qwen3.5-2B, base en bf16 (enquête du 2026-10-18, piste 3). `train run` refuse un tel modèle quand le chemin rapide n'est pas actif, sauf `repli_torch = true` dans le run, borné à 4096 tokens. `qwen3.5-2b` et `qwen3.5-0.8b` passent `entrainable = true` et `multimodal = "geler-vision"` : la tour vision est conservée et gelée, et le LoRA ne porte que sur le modèle de langage. Le modèle exporté reste multimodal (GGUF texte et `mmproj`). La vision est servie par llama.cpp avec `--mmproj`, mais l'application ne l'utilise pas encore. Les hybrides Mamba (Granite H) restent en Baseline seulement. Cette révision remplace la phrase « L'entraînement sera rouvert seulement si un Qwen3.5 sort bien de la Baseline ».

**Tests rapides** (mocks, fiches réelles, sans GPU ni tokenizer réel)
- `tests/fetch/test_verifications.py` (section Schéma, où vivent les tests de `ConfigModele`) : `test_config_modele_multimodal_valeurs`.
- `tests/train/test_environnement.py` :
  - `test_controler_config_modele_multimodal_admis_si_geler_vision`, `test_controler_config_modele_multimodal_sans_vision_config_refuse`, `test_controler_config_modele_ministral_toujours_refuse` ;
  - `test_classe_modele_multimodal` ;
  - `test_cibles_lora_regex_language_model_sans_lm_head` (faux modèle à modules `model.visual.*`, `model.language_model.*` et `lm_head` : la regex ne correspond qu'aux seconds) ;
  - `test_verifier_gel_vision_refuse_parametre_vision_entrainable`, `test_sonde_consigne_gel_vision_et_cible_reelle` ;
  - `test_cli_unsloth_multimodal_refuse` ;
  - on réaligne `test_cli_modele_non_entrainable_refuse` : Qwen3.5 retirés du paramétrage, `bonsai-2-4b` reste.
- `tests/train/test_chargement.py` : `test_contraintes_multimodal_garde_vision_config`. `test_vision_exclue_acceptee` ne change pas.
- `tests/train/test_run.py` :
  - `test_run_multimodal_charge_classe_conditionnelle_et_verifie_gel` (`gel-vision.json` écrit) ;
  - `test_orpo_multimodal_admis_ou_refuse_explicitement` (selon le critère 6) ;
  - `test_unsloth_multimodal_refuse` ;
  - on réaligne `test_hybrides_gated_deltanet_refuses`, qui devient `test_hybrides_gated_deltanet_entrainables` (fiches réelles, pile simulée, contrôle des noyaux simulé en `fla`).
- `tests/fetch/test_verifications.py`, à réaligner :
  - `test_candidats_alignes_sur_le_registre_d8` : nouvel ordre ; `CANDIDATS[:6]` entraînables et `CANDIDATS[6:]` non ;
  - `test_toml_modeles_octobre` (`entrainable` : seul `bonsai-2-4b` reste à `false`) et `test_toml_modeles_moins_2b` (seul `eurollm-1.7b` reste à `false`).

**Tests lents** (`@pytest.mark.lent`, tokenizer réel ou llama-server, ignorés si absents ; hors suite par défaut)
- `tests/train/test_masque.py` :
  - on ajoute `qwen3.5-2b` et `qwen3.5-0.8b` à la liste locale `CANDIDATS` qui paramètre `test_candidat_reel_masque_sur_les_tours_assistant` ;
  - `test_rendu_identique_a_llama_server_jinja` et `test_jeu_v1_rendu_identique_a_llama_server` sont paramétrés par `candidats_entrainables()` (CANDIDATS du registre filtrés sur `entrainable`) : ils incluent les Qwen3.5 dès que les fiches passent `entrainable = true`, sans modification ;
  - on ajoute `test_qwen35_reel_par_tour_g1_g4` si le découpage `par-tour` est retenu.
  Les fixtures restent factices (`"<réponse-factice-1>"`). L'implémenteur lance ces tests lents ciblés (CPU, sans GPU) avant de passer les fiches à `entrainable = true`.
- Mesures réelles (GPU, après fusion, par l'orchestrateur) :
  - `uv run --no-sync slmsp train sonde-env --modele qwen3.5-2b --precision-base bf16 --longueurs 2048,4096,8192`, puis de même pour `qwen3.5-0.8b` : on attend `chunk_gated_delta_rule = fla` et `vision_entrainables = 0` ;
  - un `train run` SFT court sur v1, TOML avec `precision_base = "bf16"`.

**Fichiers** : `src/slmsp/core/schemas/config_modele.py`, `src/slmsp/train/environnement.py`, `src/slmsp/train/methodes.py`, `src/slmsp/train/chargement.py`, `src/slmsp/train/run.py`, `src/slmsp/cli/train.py`, `src/slmsp/fetch/verifications.py` (CANDIDATS), `config/modeles/qwen3.5-2b.toml`, `config/modeles/qwen3.5-0.8b.toml`, `_bmad-output/planning-artifacts/decisions.md`, et les tests cités.

## Story B3 : export multimodal

**Critères d'acceptation**
1. **Fusion** : `export.fusionner(pile, dossier_base, adaptateurs, sortie, *, multimodal)` charge la base avec la classe de `classe_modele` (ConditionalGeneration pour `geler-vision`), en fp32 sur CPU (environ 9 Gio de RAM pour 2B, estimé à 4 octets par paramètre ; le portable en a 32). Elle applique l'adaptateur, fait `merge_and_unload` et enregistre en F16. `exporter` lit `multimodal` dans la fiche du slug (`source.slug`), pour un run comme pour un témoin (`source_temoin`).
   - Le dossier `hf-f16/` reçoit aussi, depuis la base et sans modification, `chat_template.jinja`, `preprocessor_config.json` et `video_preprocessor_config.json`. Le tokenizer y est déjà enregistré. La conversion `--mmproj` en a besoin.
2. **Vision inchangée** : `export.controler_vision_inchangee(base, fusionne)` compare chaque tenseur `model.visual.*` de la base à celui du fusionné, après passage dans le dtype écrit (F16). Un écart ou un tenseur `model.visual.*` absent est bloquant. Les tenseurs `mtp.*` de la base sont absents du fusionné, ce qui est attendu (critère B2.4) : ils ne sont pas comparés. Le résultat est consigné dans `export.json`.
3. **Adaptateur** : `controler_adaptateur` accepte une `target_modules` en chaîne (regex). Il refuse un adaptateur dont un module LoRA, relevé sur le modèle PEFT chargé, est hors `language_model`, ou sur `embed_tokens` ou `lm_head`. Aujourd'hui, seule une liste est contrôlée : une regex passerait sans contrôle.
4. **Conversion** :
   - `inference.serveur.convertir_hf_vers_gguf` (et `commande_conversion`) acceptent `mmproj: bool` et `sans_mtp: bool`, qui ajoutent `--mmproj` et `--no-mtp`. Les deux sont exclusifs (`ConfigurationInvalide`). b11429 quitte en erreur sur `--mmproj --no-mtp` : `Qwen3VLVisionModel` est un `MmprojModel` sans `supports_mtp_export`, d'où le message « --mtp / --no-nextn are not supported ».
   - Texte : `--no-mtp` est nécessaire, car la config déclare `mtp_num_hidden_layers = 1` (le convertisseur allonge alors `block_count` et attend des tenseurs `mtp.*`), alors que le fusionné n'a plus la tête MTP (B2.4).
   - L'export produit `modele-f16.gguf` (texte, `--no-mtp`), puis `modele-q4_k_m.gguf` (Q4_K_M, inchangé) et `mmproj-f16.gguf` (`--mmproj --outtype f16`, sans `--no-mtp` ni quantification). Avec `--outfile`, b11429 n'ajoute pas de préfixe au nom, donc le passage par `.part` reste valable.
   - `export.json` consigne les trois GGUF dans `fichiers` (clé `mmproj` en plus de `f16` et `q4_k_m`), leurs SHA-256, `multimodal` et le tag llama.cpp. `FACTEUR_ESPACE` tient compte du mmproj (environ 0,34 Gio pour 2B : 168 M paramètres de vision en F16, enquête).
   - Les lecteurs de `export.json` ne changent pas : `publication/preparer._lire_export` lit `fichiers[quantification]` et ne publie que le GGUF texte (publication du mmproj reportée) ; `ft:<export>` de lm_eval lit `modele-f16.gguf`.
5. **Sondes** :
   - La sonde d'outils (RD-001 et RD-002 sur Q4_K_M) ne change pas : l'inférence du Harnais reste en texte, sans `--mmproj`.
   - On ajoute une sonde vision dans `cli/export.py`, lancée après la sonde d'outils. `ServeurLlama` reçoit une option `mmproj: Path | None` (`--mmproj`), que le Harnais ne passe jamais. La sonde démarre llama-server (cpu) sur le Q4_K_M avec le mmproj, et vérifie que `/props` annonce la modalité vision. Elle envoie ensuite une image synthétique, un PNG uni produit en mémoire par la sonde (zlib et struct, sans Pillow), et exige une réponse non vide, sans juger son contenu.
   - Le bilan est écrit dans `sonde-vision.json`. Un échec fait passer le run en `degrade`, comme la sonde d'outils. `--sans-sonde` saute les deux sondes.
6. **Contrôle `serveur` du fetch** : il ne change pas (cpu, sans `--mmproj`, `exclure_vision` respecté).

**Tests rapides** (convertisseur, quantificateur et serveur injectés ou factices)
- `tests/train/test_export.py` (où vivent déjà les tests de `cli/export.py`) :
  - `test_fusion_multimodale_classe_conditionnelle`, `test_fusion_temoin_multimodal` ;
  - `test_fusion_copie_preprocessor` ;
  - `test_vision_inchangee_ok`, `test_vision_modifiee_bloquante`, `test_vision_absente_bloquante`, `test_mtp_absent_admis` (petits tenseurs factices) ;
  - `test_adaptateur_regex_hors_language_model_refuse` ;
  - `test_export_multimodal_produit_mmproj` (trois GGUF dans `fichiers`, options passées à chaque conversion) ;
  - `test_sonde_vision_valide`, `test_sonde_vision_echec_degrade`.
- `tests/inference/test_serveur.py` : `test_convertir_options_mmproj_et_no_mtp`, `test_convertir_mmproj_et_no_mtp_exclusifs`, `test_arguments_serveur_mmproj`, et `test_arguments_serveur_sans_mmproj_par_defaut` (non-régression du Harnais).
- `tests/publication/` : le test existant de `_lire_export` passe avec un `export.json` qui contient la clé `mmproj` (à vérifier, pas de changement attendu).

**Tests lents** (`integration`, non lancés par la story)
- `test_mmproj_b11429_qwen35_reel`, sur la base qwen3.5-0.8b : convert `--mmproj`, puis llama-server `--mmproj` et `/props`.
- Commande réelle consignée : `uv run --no-sync slmsp export --depuis <run SFT de B2>`.

**Fichiers** : `src/slmsp/train/export.py`, `src/slmsp/inference/serveur.py`, `src/slmsp/cli/export.py`, et les tests cités.

## Hors périmètre
- Ministral 3, Gemma, et tout autre VLM sans `multimodal = "geler-vision"`.
- Exemples d'entraînement avec image, et utilisation de la vision par l'application (cas d'usage à venir).
- Entraînement des Granite H (Mamba), WSL2, `causal-conv1d` (non compilable sans nvcc, repli torch admis), noyaux du hub HF (`use_kernels`, plus lents : 835 contre 1 104 tokens/s à 4096 sous WSL).
- `lm_eval` HF accéléré par fla (l'extra `bench` n'est pas touché).
- mmproj de base épinglé, et publication du mmproj (`deferred`).

## Risques
- **Stabilité en bf16 sans cast fp32** : porté par la story A. Il faut le vérifier sur un vrai run (perte, normes) avant toute campagne Qwen.
- **`causal_conv1d` en repli torch** : coût faible mesuré. Un futur fla ou une roue Windows pourrait le lever ; rien n'est prévu.
- **8192 tokens sous Windows** : 516 tokens/s, mesuré une seule fois, contre 1 090 sous WSL. Cause inconnue (autotune, température ou WDDM). La mesure est à refaire par `sonde-env` après B2, avant de fixer `longueur_max` au-delà de 4096. Le premier pas compile les noyaux Triton (80 à 100 s, une fois, mesuré sous WSL).
- **ORPO sur ConditionalGeneration** : TRL peut le traiter comme un modèle vision (critère B2.6). Repli décidé : refus explicite et report.
- **Tête MTP** : perdue à la fusion, d'où `--no-mtp` sur la conversion texte. Pas d'effet sur le Harnais, qui ne fait pas de décodage spéculatif.
- **mmproj communautaire et mmproj converti** : une Baseline vision future devra servir le mmproj converti par b11429, et non celui d'unsloth, pour comparer à l'identique.
- **Licence Qwen** : Apache-2.0 lue sur la fiche HF. `verifie_le` reste absent de `publication.toml` jusqu'à la relecture d'Anaël.
- **Lock** : l'ajout de triton dans le lock principal peut faire changer de chemin d'autres paquets (bitsandbytes ou accelerate, s'ils détectent triton). L'extra séparé limite ce risque aux environnements où il est installé. Un uv plus ancien que celui du lock réécrit tout le fichier (décision 1).
- **Contrôle par la fermeture** : il lit un détail interne de transformers 5.17.0 (`use_kernel_func_from_hub_with_fallback`). Une montée de version de transformers doit relancer `test_controler_noyaux_gdn_*` sur la vraie pile ; si la fermeture n'est plus lisible, le contrôle renvoie `torch` (refus par défaut), jamais `fla` par erreur.

## Questions ouvertes pour Anaël
1. Relecture de la licence Apache-2.0 de Qwen3.5-2B et de Qwen3.5-0.8B (`verifie_le` dans `config/publication.toml`). Ce point ne bloque pas le développement : sans `verifie_le`, la préparation du dossier de publication échoue (« non relue »), comme pour les autres slugs non relus.

## Relecture

Relecture de la spec du 2026-10-18 (Opus), avant développement, contre l'enquête, le code de `main` (c578310), la spec et le diff en cours de la story A, `pyproject.toml`, `vendor/llama.cpp/b11429/src` et transformers 5.17.0 du venv. Toutes les corrections sont faites dans cette spec.

| Gravité | Constat | Suite |
|---|---|---|
| haute | B1.5 et B1.6 écrivaient le contrôle des noyaux « dans `run.json` » et visaient un statut `bloque`. Or `run.json` est écrit une fois, à la création du run, avant le chargement (`core/schemas/run.py`), et sa config résolue est comparée par `--reprendre`. Le statut `bloque` n'existe pas. | Corrigé : refus `ConfigurationInvalide` avant le verrou, sans run ; consignation dans `noyaux.json` et `log.jsonl` (B1.6, B1.7). Même correction pour le gel de la vision (`gel-vision.json`, B2.5). |
| haute | B3.4 combinait `--mmproj` et `--no-mtp`. b11429 quitte en erreur sur cette combinaison (`MmprojModel` sans `supports_mtp_export`). | Corrigé : options exclusives, `--no-mtp` sur la conversion texte seule, et test `test_convertir_mmproj_et_no_mtp_exclusifs`. |
| moyenne | Le contrôle par avertissement « falling back » ne tient pas seul : `warning_once`, émis au premier forward, une fois par processus. La consignation « par longueur » et la sonde `les-deux` de A auraient donné `fla` à tort. | Corrigé : la fermeture du décorateur est la source principale, et l'avertissement un complément (décision 2, B1.4). |
| moyenne | `RunConfig.repli_torch` écrit par défaut dans le `toml` résolu aurait empêché `--reprendre` de tout run antérieur. | Corrigé : clé écrite hors défaut seulement, règle de A ; test `test_reprise_run_anterieur_sans_repli_torch`. |
| moyenne | Les commandes de mesure étaient fausses : `sonde-env qwen3.5-2b` (l'option est `--modele`), `uv run` sans `--no-sync` (qui resynchronise sans extras), et l'absence de `--precision-base bf16` (avec le cast, Qwen3.5-2B déborde). Le message de B1 (`uv sync --extra train --extra gdn`) aurait retiré `data`, `judge`, `bench` et `app`. | Corrigé : commandes réécrites ; message et phase 2 de `docs/reprise-deuxieme-pc.md` complétés par `--extra gdn`. |
| moyenne | La dépendance à A visait une `precision_base` « par fiche ». A la règle par run et par option de sonde. | Corrigé : section « Dépendance à la story A », avec les quatre points où B2 en dépend. B1 part aussi de main après A (mêmes fichiers). |
| moyenne | Appelants oubliés : `cli/train._sonde_env` et `environnement.sonder` (qui ne reçoit pas la fiche) pour `controler_config_modele` ; `environnement.poser_lora` (sonde) et `poser_adaptateur` pour les cibles ; `sonde-env --unsloth` et `methodes_disponibles` pour le refus d'Unsloth ; `source_temoin` pour la fusion ; les lecteurs de `export.json` (publication, lm_eval). | Corrigé : critères B2.2, B2.4, B2.7, B3.1 et B3.4. |
| moyenne | Les `layer_types` de Qwen3.5 sont sous `text_config` (vérifié sur `models/qwen3.5-2b/hf/config.json`). Une détection à la racine n'aurait rien trouvé, et le refus sans fla ne se serait jamais déclenché. | Corrigé : `a_couches_gdn` sur toutes les sous-configurations, test sur la forme réelle (B1.3). |
| moyenne | Le contrôle de la vision inchangée aurait comparé les 15 tenseurs `mtp.*` de la base, absents du fusionné : un faux bloquant. | Corrigé : comparaison limitée à `model.visual.*` ; `mtp.*` absent admis (B3.2). |
| moyenne | Tests à réaligner non cités : `test_candidats_alignes_sur_le_registre_d8`, `test_toml_modeles_octobre`, `test_cli_modele_non_entrainable_refuse` et `test_dense_melange_gated_deltanet_et_mamba`. | Corrigé : listés dans B1 et B2. |
| moyenne | Uv : il fallait vérifier la faisabilité de l'extra `gdn`. `uv lock` dans une copie temporaire ajoute exactement les quatre paquets, sans changer torch ni transformers. Le uv 0.11.7 du portable réécrit cependant le lock (`revision` 5 vers 3). | Vérifié et consigné dans la décision 1 ; critère B1.1 sans changement de `revision`. |
| basse | « Sans A, Qwen3.5-2B déborde dès 1024 tokens » présenté sans lieu : la mesure vient de WSL avec fla, et elle n'a pas été faite sous Windows natif. Le débit de 1 050 tokens/s de la révision de D8 arrondissait 1 042 et 1 054. | Corrigé : lieu de la mesure précisé, chiffres exacts. |
| basse | « Ministral 3 toujours refusé » était faux pour `train run`, qui retire la vision exclue du contrôle. | Corrigé : refus par la sonde, `train run` inchangé (Intent, B2.2). |
| basse | `classe_modele(pile, config_modele)` était ambigu : `config_modele` désigne `config.json` dans `environnement` et la fiche dans `run`. | Corrigé : `classe_modele(pile, multimodal)`. |
| basse | Emplacement des tests : le schéma `ConfigModele` est testé dans `tests/fetch/test_verifications.py`, et les tests de `cli/export.py` dans `tests/train/test_export.py` (`tests/cli/test_export.py` n'existe pas). Deux des trois tests lents R7 incluent les Qwen sans modification. | Corrigé. |
| basse | Faits non mesurés par l'enquête, vérifiés en relecture : transformers ignore `^mtp.*` au chargement, et `flash-linear-attention` déclare `transformers>=4.45.0` (métadonnées du cache uv). « Environ 9 Gio de RAM » est une estimation (4 octets par paramètre), pas une mesure. | Sources citées dans la spec. |
| décision | Décisions d'Anaël du 2026-10-18 intégrées : refus par défaut et `repli_torch` borné à 4096, ORPO multimodal refusé et reporté, pas de mmproj de base épinglé, ordre de CANDIDATS (B2.11). Questions 1 à 4 retirées. | Fait. La licence reste la seule question ouverte. |

Statut : `ready-for-dev`. La seule question ouverte (licence) ne bloque pas le développement. B1 et B2 partent de main après la fusion de la story A.
