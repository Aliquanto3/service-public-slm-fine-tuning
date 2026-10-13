# Note de conception, story 10.6 : export GGUF et contrôle après quantification

> Rédigée le 2026-10-13 pendant le test comparatif des modèles (version Opus, classée première par un juge en aveugle : 8,5 sur 10).
> À compléter par la synthèse du juge en fin de fichier. **Points à trancher par Anaël avant tout code** : voir la section Synthèse.

# Note de conception, story 10.6 : export GGUF et contrôle après quantification
Sources : epics.md §10.6, spine AD-6/13/16/19/24/27/28, decisions.md D1 à D7, `inference/serveur.py`, `fetch/verifications.py`, `evaluation/modele_ref.py`, spec 10.1 (H-WIN-TRAIN confirmée), baseline-rapport, llama.cpp b11429 (`src/`, `bin-cpu/`). Les seuils chiffrés sont des ordres de grandeur, à recalibrer sur le premier export.

## 1. Chaîne d'export
**C1. Fusion.** *Reco* : sur CPU, charger la base `models/<slug>/hf-bf16` (ou `hf/`) en **fp32**, appliquer l'adaptateur PEFT (`merge_and_unload`), contrôler la plage (aucun NaN ni inf, max |w| < 65 504), puis enregistrer en **F16** (safetensors) avec le tokenizer d'entraînement (`save_pretrained`) et le `generation_config.json` de la base. DoRA fusionne de la même façon (la norme est calculée en fp32). Pour ORPO, fusionner en chaîne l'adaptateur SFT puis l'adaptateur ORPO. Pour PiSSA, appliquer AD-19 (modèle résiduel) ; plus simple, la conversion PEFT de l'adaptateur en LoRA relatif à la base d'origine.
- *Écarté* : la fusion en bf16 (mantisse de 8 bits : un ΔW inférieur à environ 0,4 % du poids est arrondi à zéro, et le F16 ne le récupère pas) ; la fusion sur GPU (un 3B en bf16 pèse 6,9 Go, au-delà des 7,7 Go réservables sous WDDM une fois le surcoût compté) ; la fusion sur la base nf4 déquantifiée (le bruit nf4 s'ajoute puis le modèle est requantifié en Q4, et AD-19 l'exclut) ; l'adaptateur gardé à part en GGUF LoRA (`convert_lora_to_gguf.py` et `--lora` : deux fichiers dans l'application, de la RAM en plus, une précision mixte, contraire à AD-19).
- *Conséquences* : **10.4** ne retaille jamais l'embedding et n'ajoute aucun token (le pad est un token existant) ; LoRA ne cible ni `embed_tokens` ni `lm_head` (les embeddings de Granite sont liés) ; `run.json` consigne la chaîne d'adaptateurs et le SHA du tokenizer. **AD-24** : le lecteur `train` doit pouvoir lire `runs/train/<id>/adaptateur/`, ce que le CA7 de la 10.4 interdit aujourd'hui (liste à étendre). La fusion se fait sur CPU, mais l'export garde `gpu.lock` de bout en bout (CA4), car les contrôles utilisent `llama-server` en CUDA.

**C2. Conversion.** *Reco* : `inference.serveur.convertir_hf_vers_gguf(..., type_sortie="f16")`. Il faut passer `f16` **explicitement**, car la valeur par défaut du lanceur est `bf16`. L'interpréteur est celui de l'environnement `train` (torch, transformers 5.17), et `PYTHONPATH` pointe déjà vers le `gguf-py` du tag. Ajouter `PYTHONUTF8=1` au sous-processus.
- *Écarté* : `--outtype bf16` (le nom diffère du `f16` d'AD-13, la précision est moindre et le CPU est lent sans AVX512-BF16) ; `q8_0` produit directement par le convertisseur (on perd la référence F16 conservée par le CA1) ; `--mistral-format` (il exige `mistral_common` ; le format HF suffit).
- *Conséquences* : la dépendance `gguf` par chemin (`pyproject.toml`) sert au contrôle des métadonnées en Python. Le lecteur sans dépendance `fetch.verifications.lire_metadonnees_gguf` suffit déjà pour le CA2 : à réutiliser plutôt qu'à dupliquer.

**C3. Quantification.** *Reco* : `quantifier(f16, q4_k_m, "Q4_K_M", variante="cpu")`, **sans imatrix** en v1. Formats : F16 (référence, conservé) et Q4_K_M (format de l'Assistant).
- *Écarté pour la v1, gardé comme remède (§2)* : imatrix (il faut un corpus de calibrage ; calibré sur les données d'entraînement, il favorise le modèle fine-tuné face à des GGUF officiels de recette inconnue) ; Q5_K_M, Q6_K et Q8_0 (absents de `ModeleRef`) ; IQ4_XS (imatrix requis, plus lent sur CPU).
- *Conséquences* : **12.x** embarque le `modele-q4_k_m.gguf` de l'export, et non le GGUF officiel ; la mesure RAM de la 6.4 doit porter sur ce fichier.

**C4. Export témoin de la base.** *Reco* : `slmsp export --base <slug>` fait passer la base, sans adaptateur, par la **même chaîne** (F16, puis Q4_K_M). Sans lui, aucun F16 de base n'existe (`modele_ref` : `base:` est en `q4_k_m` seulement), et l'effet de la quantification ne peut pas être isolé.
- *Écarté* : comparer le modèle fine-tuné au GGUF officiel seul, car la chaîne diffère (version du convertisseur, imatrix éventuel, template).
- *Conséquences* : **5.3** (`modele_ref`) accepte un run d'export sans adaptateur (`adaptateur: null`). **11.1** l'étiquette « base, chaîne maison » et présente un tableau 2×2.

**C5. Contrôles de format (CA2 élargi), bloquants.** Le SHA du template embarqué (`tokenizer.chat_template`) est égal à celui du tokenizer d'entraînement. Les métadonnées sont égales à celles du GGUF officiel du même slug : architecture, nombre de couches, taille du vocabulaire, `tokenizer.ggml.pre`, identifiants bos, eos et eot, paramètres RoPE, nombre de tenseurs. Les tokens sont identiques : `/tokenize` de `llama-server` et HF sur 20 conversations rendues par `train.rendu`. Enfin, une génération de fumée vérifie que le token de fin est atteint (indicateur de troncature W2). Le contrôle des tokens complète le test d'égalité de texte de la 10.2 (CA3).

## 2. Contrôle après quantification
**Corpus de contrôle.** *Reco* : environ 40 conversations de `data/train/vN` réservées par hachage de leur identifiant, jamais entraînées, puis rendues par `train.rendu` avec les outils (50 à 80 k tokens). Le même corpus sert à toute la campagne et à l'export témoin, et son SHA est inscrit dans `run.json`.
- *Écarté* : le jeu d'évaluation et le calibrage (fuite ; AD-24 les interdit à `train`) ; des exemples vus à l'entraînement (le modèle fine-tuné y est plus « piqué », ce qui baisse artificiellement sa KLD face à la base) ; un corpus web générique (lecture hors liste, hors domaine).
- *Conséquences* : **10.4** exclut ce sous-ensemble (`reserve_controle`), qui devient un invariant de campagne comme la graine ; **9.8** fournit environ 7 % de données en moins à l'entraînement.

**Niveau 1, intrinsèque, sans juge (quelques minutes).** `llama-perplexity --kl-divergence-base` est lancé sur le F16, puis `--kl-divergence` sur le Q4_K_M (`n_ctx` 2048, même variante). Mesures : KLD moyenne, KLD au 99e centile, accord du token de rang 1, écart de perplexité. Il faut un nouveau lanceur `inference.serveur.kl_divergence` (AD-6 : `train` ne lance aucun processus llama.cpp). Limite : la mesure porte sur tous les tokens, passages compris, et pas seulement sur les tours `assistant`.
- *Seuils* : ils sont **relatifs à l'export témoin**. Alerte si KLD(ft) > 1,5 × KLD(base) ou si l'accord de rang 1 perd plus de 2 points face à la base. Repères absolus indicatifs : KLD ≤ 0,10 et accord ≥ 88 % pour le 1B ; KLD ≤ 0,06 et accord ≥ 92 % pour un 3B.

**Niveau 2, Tâches.** Le Jeu maison est évalué en F16 et en Q4_K_M (11.2, CA3), en décodage glouton, avec la même variante et le même `-ngl`. Le cache des verdicts est indexé par le couple (item, sortie), donc une sortie identique en F16 et en Q4 ne coûte rien. Le rapport donne, par Tâche, le taux de sorties identiques et les bascules appariées (réussi → échoué, et l'inverse). On impute la dégradation à la quantification si la perte atteint au moins 3 points (seuil NR de SM-1) **et** si le test des signes sur les bascules nettes donne p < 0,05. Avec 15 à 60 items par Tâche, un item vaut 2 à 7 points, d'où le test apparié plutôt qu'un simple écart.

**Tool calling.** Les sondes R-001 **et R-002** (le critère d'H-TOOLS utilise les deux, alors que le CA3 ne cite que R-001) tournent en F16 et en Q4. On les complète par le score RD automatique et le nombre d'`AppelNonConforme`. Un échec en Q4 seul relève de la quantification ; un échec dès le F16 relève du fine-tuning ou de l'export (template, tokens).

**Imputation (tableau 2×2).** Effet du fine-tuning = ft_F16 − base_F16 (témoin). Coût de la quantification = ft_Q4 − ft_F16. **Interaction** = (ft_Q4 − ft_F16) − (base_Q4 − base_F16). Une interaction inférieure à −3 points, ou un rapport de KLD supérieur à 1,5, signifie que la quantification efface le gain du fine-tuning. Remèdes, dans l'ordre : imatrix calibrée sur la réserve de contrôle, puis Q5_K_M ou Q6_K, puis Q8_0 pour le 1B (environ 1,7 Go, compatible a priori avec NFR-1). Contrôle de dérive de la chaîne : base_Q4 (témoin) contre le GGUF officiel, sur RD, CO et NR (sans juge) ; au-delà de 3 points d'écart, **11.1** compare au témoin et non à la Baseline officielle.
- *Conséquences* : **11.1** ajoute les colonnes F16, Q4 et interaction, ainsi que la KLD ; un niveau 1 en alerte fait passer l'export au statut `degrade` (sans blocage). **11.2** : le juge ne tourne que sur ft F16 et ft Q4 ; les témoins se limitent au niveau 1 et aux Tâches sans juge (environ 3 € par évaluation complète).

## 3. Risques
**Windows.** Le convertisseur tourne dans l'environnement `train`, en conflit avec `fetch` : c'est sans effet, car la conversion n'utilise pas le Hub. Les journaux en cp1252 imposent `PYTHONUTF8=1`. Le renommage `.part` peut échouer pendant l'analyse de Defender sur un fichier de 7 Go, ou si un `llama-server` mappe le fichier en mémoire : prévoir de nouvelles tentatives avec un délai croissant dans `_executer_vers` (zone `inference`), et ne jamais quantifier un fichier en cours de service. `llama-perplexity` tourne dans un Job Object, comme `llama-server`. Pour MAX_PATH, garder des noms courts sous `runs/export/<run_id>/`.
**RAM et disque.** La fusion en fp32 d'un 3B atteint un pic d'environ 14 à 16 Go sur 31 Go (`low_cpu_mem_usage`, aucune évaluation en parallèle : voir l'incident de mémoire critique du 2026-10-12). Un export 3B occupe environ 16 Go (HF F16, GGUF F16 et Q4), un export 1B environ 7,5 Go. Rien n'est supprimé (D1.7) : une campagne de 4 méthodes plus le témoin occupe environ 80 Go pour un 3B, sur 404 Go libres. Vérifier l'espace disque avant chaque écriture (CA4).
**VRAM de 8 Go.** Un F16 de 3B (6,9 Go, plus le cache KV en 8k) ne tient pas dans les 7,7 Go réservables. Il passe en déchargement partiel ou sur CPU, et Qwen 4B en F16 tourne sur CPU seulement. La variante et `-ngl` sont consignés ; les F16 et Q4 comparés tournent dans la même variante.
**Granite 4.0 1B.** `granitemoehybrid` sans couche SSM devient l'architecture `granite` dans le convertisseur : vérifier qu'elle est égale à celle du GGUF officiel. Les multiplicateurs muP (`embedding_multiplier`, `residual_multiplier`, `logits_scaling`) doivent survivre au `save_pretrained` de la configuration fusionnée. Les embeddings sont liés. C'est le modèle le plus sensible au Q4.
**Ministral 3 3B.** Enregistrer le modèle fusionné en `Ministral3ForCausalLM` (classe enregistrée dans le convertisseur), sans la tour vision. Le convertisseur vérifie (`assert`) le RoPE YaRN et `llama_4_scaling_beta` dans `rope_parameters`. **Template** : `gguf-py` lit `tokenizer_config.json["chat_template"]` **avant** `chat_template.jinja` (`vocab.py:335`), et le GGUF officiel diffère déjà du template HF. C'est le risque principal pour le CA2. Remède : enregistrer un tokenizer qui n'a qu'une source de template ; sinon, réécrire la métadonnée par `gguf-py` (`gguf_new_metadata.py --chat-template`). Jamais de `--chat-template-file` au service, puisque `modele_ref` force `chat_template_force = false` pour `ft:`.
**SmolLM3 3B.** La sonde d'outils a échoué à 0/5 à la Baseline, car `llama-server` n'analyse pas les `<tool_call>` : le fine-tuning ne corrige pas un analyseur. Les chat_template_kwargs `enable_thinking=false` doivent être identiques au service et à l'entraînement. Les couches NoPE (`no_rope_layer_interval`) sont à préserver. L'entraînement plafonne à 1 024 tokens sans débordement : un écart de distribution sur les longs prompts RAG n'est pas imputable à la quantification.
**Qwen3 4B.** C'est un témoin, exclu de l'essai par la règle D4 (plus de 3B). Exporté, il tourne en F16 sur CPU seulement, avec `json-generique` et le template HF.

## 4. Points de décision pour Anaël
1. Valider la fusion en fp32 puis l'enregistrement en F16. Cette lecture d'AD-19 entend « 16 bits » comme le format écrit, et non comme la précision de calcul.
2. Valider l'export témoin de la base (C4), l'extension de `modele_ref` qu'il implique, et le choix de la référence du Comparatif : témoin Q4 ou GGUF officiel.
3. Valider la réserve de contrôle d'environ 40 conversations, retirée de l'entraînement, comme invariant de campagne de la 10.4.
4. Fixer les seuils de KLD et de bascules, et dire s'ils sont bloquants ou seulement signalés (`degrade` proposé).
5. Accepter une quantification supplémentaire (Q8_0 ou Q6_K pour le 1B, imatrix) comme remède, au prix d'une extension de `ModeleRef.quantification`.
6. Répartir le budget du juge : ft F16 et Q4 seulement, ou aussi les témoins.
7. Choisir la rétention : garder le dossier HF fusionné (CA1, environ 7 Go par export d'un 3B) ou le régénérer depuis l'adaptateur.
8. Ajouter R-002 au CA3 et étendre AD-24 (lecture de `runs/train/*/adaptateur/` par le lecteur `train`).

## Synthèse du juge (compléments issus des deux autres notes)

1. **Ossature : cette note.**
   - Fusion de l'adaptateur en fp32, puis export F16, sur CPU et sous `gpu.lock`.
   - `type_sortie="f16"` explicite, puis Q4_K_M sans imatrix.
   - Témoin de base produit par la même chaîne.
   - Extension de `modele_ref` (5.3).
   - Réserve d'environ 40 conversations, invariant de 10.4.
2. **Contrôles à ajouter :**
   - PPL(ft F16) < PPL(base F16) sur la tranche domaine, pour détecter une fusion sans effet ;
   - comparaison `/tokenize` et `/apply-template` ;
   - remède `--token-embedding-type/--output-tensor-type q8_0` avant imatrix ;
   - dossier HF d'export écrit à la main : `chat_template` retiré de `tokenizer_config.json` et une seule source de template, écrite en octets.
3. **À trancher par Anaël :**
   - amendement d'AD-24 et du CA7 de 10.4 (lecture de l'adaptateur sous `runs/train/<id>/adaptateur/`) ;
   - interprétation « fp16 » d'AD-19 ;
   - ajout de R-002 au CA3.
4. **Confronter tout remède au-delà de Q4_K_M à NFR-1** (cible 4 Go, plafond 5 Go). La conversion de la base devient un test préalable à 10.4.
