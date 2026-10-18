---
title: 'Qwen3.5 entraînables sous Windows natif, tour vision gelée et export multimodal'
type: 'feature'
created: '2026-10-18'
status: 'draft'
baseline_commit: 'c578310'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/enquete-entrainement-hybrides-2026-10-18.md'
  - '{project-root}/_bmad-output/planning-artifacts/decisions.md (D2, D7, D8, registre)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-masque-minicpm5.md (G1 à G4)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-outils-rendu.md (R7)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-6-export-gguf-et-controle-apres-quantification.md'
warnings:
  - 'oversized : spec de cadrage de trois stories (B1, B2, B3) ; chaque story reste livrable seule'
  - 'dépend de la story A (precision_base = "bf16", branche feat/precision-base), non fusionnée au 2026-10-18'
deferred: []
---

## Intent

**Problème.** Qwen3.5-2B et Qwen3.5-0.8B sont des hybrides Gated DeltaNet (`linear_attention`) et des VLM (`vision_config`). D8 les limite à la Baseline (`entrainable = false`). La sonde et `train run` refusent tout `vision_config` ou le retirent : ils chargent `AutoModelForCausalLM` et posent un LoRA `all-linear`. L'export ne produit qu'un GGUF texte. L'enquête du 2026-10-18 montre que l'entraînement tient sous Windows natif avec triton-windows 3.8.0.post29 et flash-linear-attention 0.5.2 : 1 042 tokens/s à 2048 et 1 054 tokens/s à 4096 pour Qwen3.5-2B, 3,6 Gio réservés, base en bf16 sans cast fp32. Seule `causal_conv1d` reste en repli torch.

**Approche.** On met les noyaux GDN dans un extra optionnel du projet principal, avec un contrôle du chemin rapide qui est consigné. On charge la classe multimodale, on gèle la tour vision et on la vérifie, et le LoRA ne cible que `language_model`. On valide le masque sur le tokenizer réel. La fusion se fait sur la classe multimodale, puis on produit un GGUF texte et un `mmproj`. Les fiches Qwen3.5 passent `entrainable = true`, et D8 est révisé. Ministral 3 reste hors périmètre : sa fiche ne déclare pas `multimodal`, donc il est toujours refusé.

## Décisions

1. **Environnement : extra `gdn` du projet principal, pas un `envs/` séparé.**
   - `[project.optional-dependencies] gdn = ["triton-windows==3.8.0.post29 ; sys_platform == 'win32'", "flash-linear-attention==0.5.2"]`. On ajoute `{ extra = "fetch" }, { extra = "gdn" }` à `conflicts`, car fla tire `transformers`, qui est en conflit avec `huggingface-hub` 2.2.0. Le lock est régénéré par `uv lock`. Installation : `uv sync --extra train --extra gdn`.
   - Raisons :
     1. transformers choisit les noyaux au moment de l'import, dans le processus même de l'entraînement. Un sous-processus comme `envs/unsloth` obligerait à dupliquer `run.py`, le masque et le collateur.
     2. `fla-core` 0.5.2 ne déclare que `einops` : il ne demande ni `triton` ni `torch`, donc aucun `override-dependencies` n'est nécessaire (contrairement à unsloth).
     3. `triton-windows==3.8.0.post29` se résout déjà avec torch 2.14.1+cu130 dans `envs/unsloth/uv.lock`.
     4. Un extra séparé de `train` laisse intact l'environnement des runs déjà mesurés (MiniCPM5, Granite), et il s'annule en retirant une ligne.
2. **Chemin rapide contrôlé, refus par défaut.** Un modèle à couches `linear_attention` est refusé par `train run` dans deux cas :
   - avant le verrou GPU, si `fla` ou `triton` n'est pas importable (le message indique `uv sync --extra train --extra gdn`) ;
   - après le chargement, si le contrôle des noyaux montre que `chunk_gated_delta_rule` est en repli torch.

   Le repli n'est admis que de façon explicite : `repli_torch = true` dans le TOML du run, avec une alerte consignée (≈ 600 tokens/s jusqu'à 4096 tokens, enquête piste 2). `train sonde-env` ne refuse jamais : il mesure et consigne. Seul `causal_conv1d` en repli est attendu et admis.
3. **Fiche : nouveau champ `multimodal: Literal["geler-vision"] | None = None`.** Il est orthogonal à `exclure_vision`, qui ne règle plus que l'inférence du Harnais (pas de `--mmproj`) et reste `true`. `multimodal = "geler-vision"` exige un `vision_config` dans `config.json`. Il fait charger `AutoModelForImageTextToText` et cibler le LoRA sur `language_model` seul.
4. **Contrôle `dense` (fetch).** `linear_attention` est admis avec `entrainable = true` comme avec `false`. La présence de fla ne se vérifie pas au fetch : les extras `fetch` et `train`/`gdn` sont en conflit, et la garde vit dans `train`. `mamba` exige toujours `entrainable = false`, et un type inconnu écarte toujours le modèle. `exiger_entrainable` ne change pas.
5. **mmproj produit par conversion, pas épinglé.** `convert_hf_to_gguf.py --mmproj` de b11429 enregistre `Qwen3_5ForConditionalGeneration` (`conversion/qwen3vl.py`, `Qwen3VLVisionModel`), ce qui a été vérifié dans `vendor/llama.cpp/b11429/src`. L'export le produit depuis le dossier fusionné, avec le même tag llama.cpp que le GGUF texte. Un `[gguf_mmproj]` communautaire épinglé n'est pas nécessaire et il est reporté : il ne servirait qu'à une Baseline vision, sans cas d'usage aujourd'hui.
6. **Exemples d'entraînement texte seul.** Le tokenizer reste `AutoTokenizer` (pas d'`AutoProcessor`), sans `pixel_values`.

## Découpage

| Ordre | Story | Dépend de | Livrable seul |
|---|---|---|---|
| 0 | A : `precision_base = "bf16"` (autre branche) | — | oui |
| 1 | **B1** : extra `gdn` et contrôle du chemin rapide | — (parallélisable avec A) | oui : aucune fiche ne change |
| 2 | **B2** : chargement multimodal, vision gelée, sonde, `train run` (SFT et ORPO), masque, fiches, D8 | A, B1 | oui : les Qwen3.5 s'entraînent et produisent un adaptateur |
| 3 | **B3** : export multimodal (GGUF texte, mmproj, Q4_K_M, sondes) | B2 (champ `multimodal`, cibles regex) | oui : les tests unitaires utilisent des fixtures ; le bout en bout réel attend un run de B2 |

Sans A, Qwen3.5-2B déborde dès 1024 tokens (5,78 Gio avec le cast fp32, enquête piste 1). B2 utilise le mode bf16 de A sans le réécrire. Si A règle `precision_base` par fiche, les deux fiches Qwen3.5 portent `"bf16"`.

## Story B1 : extra `gdn` et contrôle du chemin rapide

**Critères d'acceptation**
1. `pyproject.toml` porte l'extra `gdn` de la décision 1 et la ligne de `conflicts`. `uv lock` passe, et `uv.lock` contient `triton-windows` 3.8.0.post29 (win32), `flash-linear-attention` et `fla-core` 0.5.2, et `einops`. torch reste en 2.14.1+cu130 et transformers en 5.17.0.
2. `train.environnement.noyaux_gdn_disponibles() -> dict` répond sans importer torch : `find_spec` de `fla` et de `triton`, et les versions de `triton-windows`, `fla-core` et `flash-linear-attention`. `versions_pile()` ajoute ces versions, ou `None` quand un paquet manque.
3. `train.environnement.controler_noyaux_gdn(modele, avertissements) -> dict` renvoie `{"chunk_gated_delta_rule": "fla" | "torch", "causal_conv1d": "fla" | "torch", "replis": [...]}`. Il combine deux sources :
   - le module de l'implémentation effective (préfixe `fla.`) ;
   - les avertissements « is falling back to its reference PyTorch implementation », capturés sur le logger `transformers` pendant le chargement et le premier pas.

   Un modèle sans couche `linear_attention` donne `None`.
4. `train.environnement.exiger_noyaux_gdn(config_poids, slug, *, repli_torch)` lève `ConfigurationInvalide` quand des couches `linear_attention` sont présentes et que fla ou triton manque, sauf `repli_torch = true`. Le message cite `uv sync --extra train --extra gdn`. Il est appelé par `train run` et par `train sonde-env`, avant le verrou GPU. `sonde-env` passe toujours `repli_torch=True` et consigne le résultat.
5. `RunConfig` reçoit `repli_torch: bool = False`. Après le chargement, `train run` refuse le run (statut `bloque`, motif consigné) quand `chunk_gated_delta_rule` vaut `torch` sans `repli_torch`.
6. Le résultat du contrôle des noyaux est écrit dans `sonde.json`, par longueur, et dans `run.json`, hors `CLES_INVARIANTS` : une campagne compare des modèles denses et hybrides. L'emplacement le plus simple est la config résolue du run. L'alerte « repli torch » va dans `log.jsonl` quand `repli_torch` sert.
7. `fetch/verifications.py` : `linear_attention` avec `entrainable = true` donne `ok` (« hybride Gated DeltaNet entraînable, noyaux fla requis à l'entraînement (extra gdn) »). `mamba` avec `entrainable = true` reste en `echec`.

**Tests** (mocks, sans GPU ni fla)
- `tests/train/test_environnement.py` :
  - `test_noyaux_gdn_disponibles_sans_fla`, `test_noyaux_gdn_disponibles_avec_fla` (`find_spec` simulé) ;
  - `test_controler_noyaux_gdn_chemin_rapide`, `test_controler_noyaux_gdn_repli_detecte` (module simulé et avertissement « falling back ») ;
  - `test_exiger_noyaux_gdn_refuse_sans_fla`, `test_exiger_noyaux_gdn_repli_explicite`, `test_exiger_noyaux_gdn_modele_dense_sans_objet`.
- `tests/train/test_run.py` : `test_run_hybride_refuse_si_repli_sans_option`, `test_run_noyaux_consignes_hors_invariants`.
- `tests/fetch/test_verifications.py` : `test_dense_gated_deltanet_entrainable_admis`, `test_dense_mamba_exige_toujours_entrainable_false`. On réaligne `test_dense_gated_deltanet_exige_entrainable_false`, qui est inversé.
- Mesure réelle, non lancée par la story (pas de GPU) : `uv run slmsp train sonde-env qwen3.5-2b --longueurs 2048,4096`, après B2. Commande consignée.

**Fichiers** : `pyproject.toml`, `uv.lock`, `src/slmsp/train/environnement.py`, `src/slmsp/train/config.py`, `src/slmsp/train/run.py`, `src/slmsp/cli/train.py`, `src/slmsp/fetch/verifications.py`, et les tests cités.

## Story B2 : chargement multimodal, vision gelée, sonde, `train run`, masque, fiches

**Critères d'acceptation**
1. **Schéma** : `ConfigModele.multimodal: Literal["geler-vision"] | None = None`. `multimodal` sans `vision_config` dans `config.json` est refusé au chargement des poids par `controler_config_modele`, avec un message clair.
2. **Refus de la sonde** : `controler_config_modele` reçoit `multimodal`. Un `vision_config` passe si `multimodal == "geler-vision"`, et le résumé vaut alors `vision_config: "gelee"`. Sinon le message actuel reste (« modèle multimodal … ne charge pas l'encodeur vision »), ce qui garde Ministral 3 refusé. `chargement.controler_contraintes` garde le `vision_config` dans ce cas, au lieu de le retirer.
3. **Classe** : un seul point de choix, `train.environnement.classe_modele(pile, config_modele)`, qui renvoie `AutoModelForImageTextToText` pour `geler-vision` et `AutoModelForCausalLM` sinon. Il est utilisé par `environnement.charger_modele` (sonde) et par `methodes.charger_modele` (run, ORPO compris), en nf4 comme en bf16, avec la préparation sans cast de la story A.
4. **Cibles LoRA** : `methodes.cibles_lora(modele, config_modele)` renvoie `"all-linear"` sans `multimodal`. Avec `geler-vision`, elle renvoie la regex `.*language_model.*\.(<noms des Linear et Linear4bit sous language_model>)$`, comme la sonde de l'enquête. Elle ne cible ni `lm_head`, ni `embed_tokens`, ni la tête MTP (TRL `chunked_nll` refuse `lm_head`). `sonder` et `config_lora` l'utilisent, et `sonde.json` consigne la cible réelle.
5. **Vision gelée et vérifiée** : `train.environnement.verifier_gel_vision(modele) -> dict` renvoie `{parametres_entrainables, vision_parametres, vision_entrainables}`. Il lève `ConfigurationInvalide` si un paramètre entraînable a un nom sans `language_model`. Il est appelé après la pose de l'adaptateur (neuf ou SFT rechargé pour ORPO), avant `train()`. Le résultat est écrit dans `sonde.json` et dans `run.json`. Valeurs attendues pour Qwen3.5-2B : 16,8 M paramètres entraînables, 0 en vision.
6. **ORPO** : avant toute reprise, une préparation de `ORPOTrainer` avec un modèle ConditionalGeneration et un tokenizer (pas un processor) est vérifiée sur un faux modèle. Si TRL traite le modèle comme vision et exige un processor ou des images, ORPO est refusé explicitement pour `multimodal` (`ConfigurationInvalide` : « ORPO non pris en charge pour un modèle multimodal, story à venir »). Ce report est consigné dans `deferred`. On ne contourne pas TRL.
7. **Unsloth** : `qlora-unsloth` est refusé pour `multimodal` (hors périmètre).
8. **Masque et rendu** : on ajoute `qwen3.5-2b` et `qwen3.5-0.8b` aux tests lents sur le tokenizer réel. Template Qwen3.5 avec `chat_template_kwargs = { enable_thinking = false }` de la fiche.
   - Le découpage par défaut (`conversation`) est essayé d'abord.
   - S'il lève `ErreurMasque`, ou si G1 à G4 échouent, la fiche passe `decoupage_masque = "par-tour"`. On s'attend à ce cas, car le template réécrit l'historique (spec-masque-minicpm5). `bloc_amorce` est ajouté seulement si le test le montre nécessaire.
   - Le résultat mesuré (découpage retenu, exemples, tokens supervisés) est consigné dans `## Auto Run Result`.
9. **R7** : le rendu d'entraînement des préfixes RD est égal à `/apply-template` de llama-server (`chat_template_force = true`). Le résultat attendu est 205/205 sur v1 pour les deux modèles. Un écart bloque le passage `entrainable = true` du modèle en cause, et il est consigné.
10. **Fiches** :
    - `qwen3.5-2b.toml` et `qwen3.5-0.8b.toml` : `entrainable = true`, `multimodal = "geler-vision"`, `exclure_vision = true` (inchangé : le Harnais reste en texte), et `decoupage_masque` selon le critère 8. Les commentaires d'en-tête sont réécrits (D8 révisé, extra `gdn`, vision gelée).
    - `config/publication.toml` : l'entrée `qwen3.5-2b` reste sans `verifie_le` jusqu'à la relecture d'Anaël (Apache-2.0 lue sur la fiche HF).
11. **decisions.md** (sur demande expresse, comme dans spec-hybrides-baseline) :
    - D8 reçoit le paragraphe ci-dessous ;
    - le registre passe les deux Qwen3.5 en « candidat au fine-tuning ».
    - Texte proposé :
      > **Révision du 2026-10-18 (Qwen3.5 entraînables)**, décision d'Anaël. Les hybrides Gated DeltaNet (`linear_attention`) sont entraînables sous Windows natif avec les noyaux Triton de flash-linear-attention : extra `gdn` (triton-windows 3.8.0.post29, flash-linear-attention 0.5.2). La mesure donne environ 1 050 tokens/s pour Qwen3.5-2B jusqu'à 4096 tokens, base en bf16 (enquête du 2026-10-18, piste 3). `train run` refuse un tel modèle quand le chemin rapide n'est pas actif, sauf `repli_torch = true` dans le run. `qwen3.5-2b` et `qwen3.5-0.8b` passent `entrainable = true` et `multimodal = "geler-vision"` : la tour vision est conservée et gelée, et le LoRA ne porte que sur le modèle de langage. Le modèle exporté reste multimodal (GGUF texte et `mmproj`). La vision est servie par llama.cpp avec `--mmproj`, mais l'application ne l'utilise pas encore. Les hybrides Mamba (Granite H) restent en Baseline seulement. Cette révision remplace la phrase « L'entraînement sera rouvert seulement si un Qwen3.5 sort bien de la Baseline ».

**Tests**
- `tests/train/test_environnement.py` :
  - `test_controler_config_modele_multimodal_admis_si_geler_vision`, `test_controler_config_modele_ministral_toujours_refuse` ;
  - `test_classe_modele_multimodal` ;
  - `test_cibles_lora_regex_language_model_sans_lm_head` (faux modèle à modules `model.visual.*`, `model.language_model.*` et `lm_head`) ;
  - `test_verifier_gel_vision_refuse_parametre_vision_entrainable`, `test_sonde_consigne_gel_vision`.
- `tests/train/test_run.py` :
  - `test_run_multimodal_charge_classe_conditionnelle_et_verifie_gel` ;
  - `test_orpo_multimodal_admis_ou_refuse_explicitement` (selon le critère 6) ;
  - `test_unsloth_multimodal_refuse` ;
  - on réaligne `test_hybrides_gated_deltanet_refuses`, qui devient `test_hybrides_gated_deltanet_entrainables` (fiches réelles).
- `tests/core/` (schéma) : `test_config_modele_multimodal_valeurs`.
- `tests/train/test_masque.py` (lents, tokenizer réel, ignorés si absent) : Qwen ajouté au paramétrage de `test_candidat_reel_masque_sur_les_tours_assistant`, de `test_rendu_identique_a_llama_server_jinja` et de `test_jeu_v1_rendu_identique_a_llama_server`. On ajoute `test_qwen35_reel_par_tour_g1_g4` si le découpage `par-tour` est retenu. Les fixtures restent factices (`"<réponse-factice-1>"`).
- `tests/fetch/test_verifications.py` : `test_toml_modeles_moins_2b` est réaligné sur `entrainable = true` des deux Qwen.
- Mesures réelles (GPU, après fusion, par l'orchestrateur) :
  - `slmsp train sonde-env qwen3.5-2b` et `qwen3.5-0.8b`, longueurs 2048, 4096 et 8192 : on attend `chunk_gated_delta_rule = fla` et `vision_entrainables = 0` ;
  - un `train run` SFT court sur v1.

**Fichiers** : `src/slmsp/core/schemas/config_modele.py`, `src/slmsp/train/environnement.py`, `src/slmsp/train/methodes.py`, `src/slmsp/train/chargement.py`, `src/slmsp/train/run.py`, `src/slmsp/cli/train.py`, `config/modeles/qwen3.5-2b.toml`, `config/modeles/qwen3.5-0.8b.toml`, `_bmad-output/planning-artifacts/decisions.md`, et les tests cités.

## Story B3 : export multimodal

**Critères d'acceptation**
1. **Fusion** : `export.fusionner` charge la base avec la classe de `classe_modele` (ConditionalGeneration pour `geler-vision`), en fp32 sur CPU (environ 9 Gio de RAM pour 2B, et le portable en a 32). Elle applique l'adaptateur, fait `merge_and_unload` et enregistre en F16.
   - Le dossier `hf-f16/` reçoit aussi, depuis la base et sans modification, le tokenizer, `chat_template.jinja`, `preprocessor_config.json` et `video_preprocessor_config.json`. La conversion `--mmproj` en a besoin.
2. **Vision inchangée** : `export.controler_vision_inchangee(base, fusionne)` vérifie que chaque tenseur hors `language_model` et hors `lm_head` est égal à celui de la base, après passage dans le dtype écrit. Un écart est bloquant. Le résultat est consigné dans `export.json`.
3. **Adaptateur** : `controler_adaptateur` accepte une `target_modules` en chaîne (regex). Il refuse un adaptateur dont un module LoRA, relevé sur le modèle PEFT chargé, est hors `language_model` ou sur `embed_tokens` ou `lm_head`. Aujourd'hui, seule une liste est contrôlée, et une regex passerait sans contrôle.
4. **Conversion** :
   - `inference.serveur.convertir_hf_vers_gguf` accepte `mmproj: bool` et `sans_mtp: bool`, qui ajoutent `--mmproj` et `--no-mtp`. L'option `--no-mtp` sert parce que transformers ne recharge pas la tête MTP, et le fusionné ne l'a donc plus.
   - L'export produit `modele-f16.gguf`, puis `modele-q4_k_m.gguf` (Q4_K_M, inchangé) et `mmproj-f16.gguf` (`--outtype f16`, sans quantification).
   - `export.json` consigne les trois GGUF, leurs SHA-256, `multimodal` et le tag llama.cpp. `FACTEUR_ESPACE` tient compte du mmproj (environ 0,4 Gio pour 2B).
5. **Sondes** :
   - La sonde d'outils (RD-001 et RD-002 sur Q4_K_M) ne change pas : l'inférence du Harnais reste en texte, sans `--mmproj`.
   - On ajoute une sonde vision, `cli/export.py` : `ServeurLlama` reçoit une option `mmproj: Path | None` (`--mmproj`), que le Harnais ne passe jamais. Elle démarre llama-server (cpu) sur le Q4_K_M avec le mmproj, et vérifie que `/props` annonce la modalité vision. Elle envoie ensuite une image synthétique, un PNG uni généré par le test, et exige une réponse non vide, sans juger son contenu.
   - Le bilan est écrit dans `sonde-vision.json`. Un échec fait passer le run en `degrade`, comme la sonde d'outils. `--sans-sonde` saute les deux sondes.
6. **Contrôle `serveur` du fetch** : il ne change pas (cpu, sans `--mmproj`, `exclure_vision` respecté).

**Tests**
- `tests/train/test_export.py` :
  - `test_fusion_multimodale_classe_conditionnelle` ;
  - `test_fusion_copie_preprocessor` ;
  - `test_vision_inchangee_ok`, `test_vision_modifiee_bloquante` (petits tenseurs factices) ;
  - `test_adaptateur_regex_hors_language_model_refuse` ;
  - `test_export_multimodal_produit_mmproj` (convertisseur et quantificateur injectés).
- `tests/inference/test_serveur.py` : `test_convertir_options_mmproj_et_no_mtp`, `test_arguments_serveur_mmproj`, et `test_arguments_serveur_sans_mmproj_par_defaut` (non-régression du Harnais).
- `tests/cli/test_export.py` : `test_sonde_vision_valide`, `test_sonde_vision_echec_degrade`.
- Lent et `integration`, non lancé par la story : `test_mmproj_b11429_qwen35_reel`, sur la base qwen3.5-0.8b (convert `--mmproj`, puis llama-server `--mmproj` et `/props`). La commande réelle est consignée : `slmsp export --depuis <run SFT de B2>`.

**Fichiers** : `src/slmsp/train/export.py`, `src/slmsp/inference/serveur.py`, `src/slmsp/cli/export.py`, et les tests cités.

## Hors périmètre
- Ministral 3, Gemma, et tout autre VLM sans `multimodal = "geler-vision"`.
- Exemples d'entraînement avec image, et utilisation de la vision par l'application (cas d'usage à venir).
- Entraînement des Granite H (Mamba), WSL2, `causal-conv1d` (non compilable sans nvcc, repli torch admis), noyaux du hub HF (`use_kernels`, plus lents).
- `lm_eval` HF accéléré par fla (l'extra `bench` n'est pas touché).
- Ordre de `verifications.CANDIDATS` (ordre D4, décision d'Anaël).

## Risques
- **Stabilité en bf16 sans cast fp32** : porté par la story A. Il faut le vérifier sur un vrai run (perte, normes) avant toute campagne Qwen.
- **`causal_conv1d` en repli torch** : coût faible mesuré. Un futur fla ou une roue Windows pourrait le lever ; rien n'est prévu.
- **8192 tokens sous Windows** : 516 tokens/s, mesuré une seule fois, contre 1 090 sous WSL. Cause inconnue (autotune, température ou WDDM). La mesure est à refaire par `sonde-env` après B2, avant de fixer `longueur_max` au-delà de 4096. Le premier pas compile les noyaux Triton (80 à 100 s, une fois).
- **ORPO sur ConditionalGeneration** : TRL peut le traiter comme un modèle vision (critère B2.6). Repli : refus explicite et report.
- **Tête MTP** : perdue à la fusion, d'où `--no-mtp`. Pas d'effet sur le Harnais, qui ne fait pas de décodage spéculatif.
- **mmproj communautaire et mmproj converti** : une Baseline vision future devra servir le mmproj converti par b11429, et non celui d'unsloth, pour comparer à l'identique.
- **Licence Qwen** : Apache-2.0 lue sur la fiche HF. `verifie_le` reste absent de `publication.toml` jusqu'à la relecture d'Anaël.
- **Lock** : l'ajout de triton dans le lock principal peut faire changer de chemin d'autres paquets (bitsandbytes ou accelerate, s'ils détectent triton). L'extra séparé limite ce risque aux environnements où il est installé.

## Questions ouvertes pour Anaël
1. Repli torch : faut-il le refuser par défaut avec l'option `repli_torch` (proposé), ou l'admettre en alerte seule ? Faut-il aussi borner le repli à 4096 tokens ?
2. ORPO multimodal : un refus explicite et un report suffisent-ils si TRL l'exige (B2.6) ?
3. Faut-il épingler un `[gguf_mmproj]` communautaire pour une Baseline vision de base, ou attendre le cas d'usage (proposé : attendre) ?
4. Faut-il placer les deux Qwen3.5 dans la partie « entraînables d'abord » de `CANDIDATS`, et à quel rang ?
5. Relecture de la licence Apache-2.0 de Qwen3.5-2B et de Qwen3.5-0.8B (`verifie_le`).
