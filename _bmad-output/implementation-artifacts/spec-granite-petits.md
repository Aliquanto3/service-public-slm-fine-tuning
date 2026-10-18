---
title: 'Trois petits Granite en Baseline'
type: 'feature'
created: '2026-10-18'
status: 'done'
review_loop_iteration: 1
followup_review_recommended: false
context: ['{project-root}/_bmad-output/planning-artifacts/decisions.md']
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** la Baseline n'a que des modèles de 1B et plus ; Granite 4.0 H était écarté (Mamba, Windows natif).

**Approach:** ajouter `granite-4.0-350m` (dense, entraînable) et `granite-4.0-h-350m`, `granite-4.0-h-1b` (Mamba, `entrainable = false`), et faire admettre `mamba` au contrôle `dense` à cette condition (décisions d'Anaël du 2026-10-18, D8).

## Boundaries & Constraints

**Always:** fiches épinglées (révisions, SHA-256, tailles via l'API HF) ; `lm_eval_batch_size` fixe ; un type de couche inconnu reste écarté ; une fiche à couches `mamba` sans `entrainable = false` reste refusée.

**Never:** téléchargement de poids (`slmsp fetch modeles` après fusion) ; GPU ; entraînement des H.

</intent-contract>

## Code Map

- `config/modeles/granite-4.0-350m.toml`, `granite-4.0-h-350m.toml`, `granite-4.0-h-1b.toml` -- nouvelles fiches
- `src/slmsp/fetch/verifications.py` -- `COUCHES_INFERENCE_SEULE` + `mamba`, `CANDIDATS`
- `tests/fetch/test_verifications.py` -- tests réalignés et `test_toml_granite_petits`
- `_bmad-output/planning-artifacts/decisions.md` -- D8 : registre et décision

## Auto Run Result

Mesures (en-têtes safetensors, BF16) : 350m 352 379 904 (0,35B) ; h-350m 340 332 224 (0,34B) ; h-1b 1 461 538 368 (1,46B).

| Slug | Révision HF | GGUF Q4_K_M (octets) | GGUF bf16 (octets) | batch |
|---|---|---|---|---|
| granite-4.0-350m | bd8a1497 | 236 985 760 | 708 439 456 | 4 |
| granite-4.0-h-350m | 3b17b717 | 222 662 560 | 684 931 200 | 4 |
| granite-4.0-h-1b | d18cca4c | 901 162 208 | 2 928 332 288 | 2 |

Décisions : contexte 8192 pour les trois (comme granite-4.0-1b ; natif 32 768 / 131 072) ; Q4_K_M officiel existe pour les trois ; pas de F16 publié, seulement `bf16` (`[gguf_f16]`, precision bf16) ; `chat_template_force = false` et `protocole_outils = "natif"` non sondés (template identique à celui de granite-4.0-1b, SHA-256 égal), à confirmer par le contrôle `chat_template` et la sonde H-TOOLS. h-1b n'a ni `merges.txt` ni `vocab.json`.

À confirmer par Anaël : message du contrôle `dense` généralisé (« hybride Mamba admis… ») ; mélange `linear_attention` + `mamba` désormais admis si non entraînable.

Report : exécuter `slmsp fetch modeles --candidats` (contrôles `serveur`, `chat_template` sur llama.cpp) après la fusion ; sonde H-TOOLS des trois.

## À vérifier au fetch

- **Service des Granite H par llama.cpp non prouvé** (second avis, medium, reporté) : aucune exécution sans GPU ni poids en revue. Après la fusion, l'orchestrateur lance `slmsp fetch modeles --candidats` ; le contrôle `serveur` écarte un modèle que llama.cpp ne sert pas. Vérifier pour `granite-4.0-h-350m` et `granite-4.0-h-1b` : contrôle `serveur` ok (réponse du serveur sur le GGUF Q4_K_M), puis `chat_template` ok. En cas d'échec, sortir le slug de `CANDIDATS` et du registre D8.
- `chat_template_force = false` et `protocole_outils = "natif"` des trois fiches : contrôle `chat_template`, puis sonde H-TOOLS.

## Revue

Vérification par l'API HF (2026-10-18, `model_info(..., files_metadata=True)`, SHA-256 des fichiers non LFS recalculés sur le contenu téléchargé) : révisions de 40 caractères existantes (HF et GGUF) ; SHA-256 et tailles conformes pour tous les fichiers des trois fiches, poids safetensors, GGUF Q4_K_M et bf16 compris ; `fichiers` couvre le dépôt (hors `.gitattributes`, `README.md`, `model.sig`). Types de couche lus dans `config.json` : 350m 28 attention ; h-350m 28 mamba + 4 attention ; h-1b 36 mamba + 4 attention. Licences : apache-2.0 pour les trois.

| Sévérité | Source | Constat | Suite | Motif |
|---|---|---|---|---|
| medium | second avis | Service llama.cpp des Granite H non prouvé | reporté | voulu : contrôle `serveur` au fetch après fusion (section « À vérifier au fetch ») |
| low | reviewer (vérif. HF) | h-1b : « 35 couches mamba » (decisions.md) et « 5 couches d'attention » (fiche) ; le `config.json` réel en a 36 et 4 | corrigé | comptes relus dans `config.json` à la révision épinglée |
| low | second avis | decisions.md : dernier paragraphe « Liste `--candidats` » avec l'ancien ordre | corrigé | ordre réel de `CANDIDATS` ajouté (complète sans réécrire) |
| low | second avis | `famille` étiquette « hybride Mamba » un mélange linear_attention + mamba | corrigé | `FAMILLES_HYBRIDES` : « Gated DeltaNet », « Mamba » ou « Gated DeltaNet et Mamba » |
| low | second avis | `test_dense_toutes_sous_configs_et_cles_connues` affaibli, test du mélange supprimé | corrigé | détails comparés à l'identique, index exact (`llm_config.1`…) vérifié sur un type inconnu ; `test_dense_melange_gated_deltanet_et_mamba` (refusé si entraînable, admis sinon) |
| low | second avis | lm_eval HF ne contrôle pas `entrainable` | rejeté (comportement gardé) | comme pour `linear_attention` : la Baseline HF des H est utile, même lente ; seuls `train run` et `train sonde-env` refusent (`exiger_entrainable`) |
| low | reviewer | `granite-4.0-350m` (entraînable) absent de `config/publication.toml` : `publication preparer` l'aurait refusé | corrigé | entrée apache-2.0 (relevée sur la fiche HF), sans `verifie_le` : relecture d'Anaël attendue |
| — | reviewer | Complexité | aucun constat | `_controle_dense` linéaire en nombre de couches ; aucune structure qui grossit en exécution |
