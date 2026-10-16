---
title: 'Story 10.5 — Variante QLoRA Unsloth en environnement isolé'
type: 'feature'
created: '2026-10-16'
status: 'review'
baseline_revision: '6dba304'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-10-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
deferred: []
---

## Intent

**Problème :** mesurer le gain de vitesse d'Unsloth avec les mêmes données et le même masque que M1, sans que `slmsp` importe `unsloth` et sans compter la variante parmi les méthodes comparées.

**Approche :** `slmsp.train.variante_unsloth` écrit le jeu pré-tokenisé (`input_ids` et `labels` déjà produits par `train.rendu` et `train.masque` dans `chargement.pretokeniser`, jamais recalculés) et une configuration JSON, lance `envs/unsloth/entrainer.py` par `uv run --frozen --project envs/unsloth` (sous-processus, `env_sous_processus()`), puis archive adaptateur, coûts et pertes dans le run comme pour les autres méthodes. `entrainer.py` n'a aucune dépendance sur `slmsp`.

## Décisions

- **AC1** : H-WIN-TRAIN est confirmée pour Unsloth (spec 10.1, 844 tokens/s à 2048) : la story n'est pas bloquée.
- **Intégration 10.4 (fusionnée, câblée)** : `PLANS["qlora-unsloth"]` (`entraineur="unsloth"`), refus retiré de `plan_methode`, `run._entrainer` délègue à `_entrainer_unsloth` juste après le calcul des `arguments` (donc après vérification de campagne, `gpu.lock` pris, run créé, statut `partiel-erreur` si le sous-processus échoue). `arguments`, `RunConfig`, `chargement.pretokeniser` et `ecrire_mesures(..., contexte)` sont réutilisés. `--reprendre` est refusé pour cette méthode. Test bout en bout `train run` avec sous-processus factice dans `tests/train/test_unsloth.py`.
- **Coûts** : durée, débit hors padding après `pas_chauffe` pas et VRAM torch viennent du sous-processus ; énergie et VRAM NVML sont relevées par le parent (`EchantillonneurNvml`) sur la fenêtre d'entraînement. Même `MesuresCout`, même `ecrire_mesures`.
- **W4.5** : gradient checkpointing standard (`True`) par défaut, au lieu de `"unsloth"` qui déporte les activations en RAM CPU et fausse la VRAM ; `checkpointing = "unsloth"` reste accessible dans la configuration. Le débordement WDDM est contrôlé (`environnement.deborde`) et consigné. La quantification réellement appliquée (`modele.config.quantization_config`) est relevée ; si elle n'est pas nf4 avec double quantification, un avertissement est ajouté aux coûts (non vérifiable sans GPU ici).
- **W4.6** : sortie JSON en ASCII (`ensure_ascii=True`) dans `sonde.py` et `entrainer.py`, plus `stdout.reconfigure(utf-8)` : plus d'erreur cp1252.
- **Reprise sur checkpoint** non supportée pour cette variante (mesure de vitesse courte) ; les checkpoints sont écrits sous `checkpoints/`, jamais supprimés.
- Hors périmètre, reporté : `--longueur-unsloth`, test réel (marqué `gpu` et `lent`, commande ci-dessous).

## Vérification

`tests/train/test_unsloth.py` : sous-processus remplacé par un script factice, helpers de `entrainer.py` testés avec des doubles. Test réel (non lancé) : `uv run --extra train slmsp train run --config config/runs/v-qlora-unsloth-granite-4.0-1b.toml` (après intégration 10.4, venv `envs/unsloth` à créer par `uv sync --frozen --project envs/unsloth`).

## Auto Run Result

**Statut : review.** Tests de la story : 20 verts (1 test réel `gpu`/`lent` non lancé). Aucun GPU, venv Unsloth ni modèle utilisé.

**Décisions prises seul :**
- Module séparé `variante_unsloth.py` pour garder `methodes.py` mince et éviter tout faux positif du test « jamais d'import unsloth ».
- `arguments` (SFTConfig) est construit par `methodes.arguments_entrainement` de 10.4, non dupliqué.
- W4.5 : `checkpointing=True` par défaut. À confirmer par Anaël : comparer à `"unsloth"` si l'on veut chiffrer le gain maximal d'Unsloth, au prix d'une VRAM non comparable.
- La quantification réelle d'Unsloth (nf4 et double quantification) n'est pas vérifiable sans lancer le modèle : elle est relevée et un avertissement est consigné si elle diffère de M1. À confirmer au premier run réel.

**Reports :** `--longueur-unsloth` (W4.6) ; reprise sur checkpoint ; autres points de W4.5 (fp32 de `prepare_model_for_kbit_training` côté TRL) relèvent de 10.4.

## Revue

- medium, corrigé : `entrainer.py` sans `set_seed` avant chargement et init LoRA ; `set_seed(graine)` ajouté comme M1 (W4.4).
- low, corrigé : adaptateur sauvegardé avant le contrôle de perte ; la sauvegarde n'a plus lieu si la perte est NaN ou absente (plus d'`adaptateur/` bloquant).
- low, corrigé : garde `--reprendre` déplacée dans `executer` avant toute réouverture (test ajouté) ; le statut d'un run complet n'est plus réécrit.
- low, rejeté : `controler_quantification` reste un avertissement ; il est déjà consigné dans `mesures.avertissements` (couts.json) pour le chiffrage.
- low, corrigé : `_SUFFIXES_SECRET` étendu à `_KEY`, `_PASSWORD` et `PASSWORD` ; test ajouté dans `test_config.py`.
- D1 : aucune donnée, exemple ni amorce rédigés par Claude dans le diff (le test réel utilise des tokens aléatoires). Aucun constat.
