---
title: 'Régularisation KL vers la base (auto-distillation) dans l entraîneur'
type: 'feature'
created: '2026-10-21'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: ['{project-root}/_bmad-output/planning-artifacts/stories-epic-16-derive-et-confirmation.md']
warnings: []
deferred: []
---

<intent-contract>

## Intent
Retenir l'adaptateur QLoRA près de la base pendant l'entraînement : perte = entropie croisée + `kl_base` × KL(élève ‖ base) par token de réponse. Validé par Anaël le 21/10 (0 €, aucune donnée nouvelle, D1 inchangé).

## Boundaries
- `kl_base = 0` (défaut) : `SFTTrainer` tel quel, arguments et `run.json` identiques aux runs d'avant.
- QLoRA seulement : `RunConfig` refuse `kl_base > 0` pour toute autre méthode (Unsloth, ORPO compris), `creer_entraineur` aussi (défense en profondeur).
- Aucun entraînement réel dans la story : l'essai de 5 pas est lancé par l'orchestrateur.

</intent-contract>

## Réalisation
- `train/config.py` : `HyperParametres.kl_base` (≥ 0, défaut 0) et `kl_temperature` (> 0, défaut 1) ; refus hors `qlora`.
- `train/kl_base.py` : `somme_kl` (positions t → label t + 1, labels ≠ `IGNORE`, float32 sur ces seules positions, `kl_div(log_q, log_p, log_target=True)` × T²) ; `classe_entraineur_kl(SFTTrainer, torch)` : `compute_loss` = entropie croisée de `super()` + passe de la base sous `torch.no_grad()` et `disable_adapter()` (aucune copie de poids) ; KL normalisée comme l'entropie croisée du `Trainer` (`num_items_in_batch` si `model_accepts_loss_kwargs`, sinon tokens du micro-lot) ; `log` ajoute `entropie_croisee` et `kl` (moyennes par token des micro-lots depuis le dernier log) et écrit `{"evenement": "perte", "pas", "perte", "entropie_croisee", "kl", "kl_base"}` dans `metriques.jsonl`.
- `train/methodes.py` : `creer_entraineur(kl=, kl_temperature=, journal=)` ; arguments d'entraînement identiques avec ou sans KL (revue : plus de bascule vers `nll`).
- `train/run.py` : passage des hyperparamètres et du journal ; `_toml_resolu` retire `kl_base`/`kl_temperature` au défaut (reprise des runs d'avant), les garde toutes deux sinon (manifeste `run.json`).
- `compare` : `Entrainement.kl_base` lu du TOML résolu ; `compare comparatif` affiche « (qlora, KL base 0.1, T 1, run …) », rendu inchangé sans KL.
- `config/runs/m1-qlora-minicpm5-2b-v18-kl-essai.toml` : essai de 5 pas, campagne à part.

## Tests
`tests/train/test_kl_base.py` (14, dont 1 `lent` : vrai `SFTTrainer` de TRL, 2 pas CPU, KL nulle au pas 1 avec adaptateur neuf) : KL nulle élève = base et adaptateur neuf, masque et décalage causal, T², perte = CE + poids × KL, gradient sur LoRA seul, normalisation `num_items_in_batch`, journal, `kl_base = 0` → `SFTTrainer` exact et arguments identiques, refus hors QLoRA (config, entraîneur, run Unsloth), manifeste. `tests/compare/test_comparatif.py::test_kl_vers_la_base_affichee`. Ciblés : `tests/train tests/compare tests/core` verts (1194).

## Auto Run Result
- Décision : facteur T² sur la KL (convention de distillation ; sans effet à T = 1). Réversible.
- Décision : la passe de la base garde le mode `train` du modèle (dropout LoRA désactivé avec l'adaptateur ; dropout de la base nul dans les modèles visés).
- Décision : « QLoRA seulement » lu strictement (`methode = "qlora"`) ; dora, rslora, lora, pissa refusés aussi (pissa modifie la base : `disable_adapter` n'y rendrait pas la base). Extension possible plus tard.
- Décision : l'entropie croisée journalisée est ramenée à une moyenne par token du micro-lot (`perte_ce × dénominateur / n`), puis moyennée entre micro-lots : diagnostic, pas la perte optimisée.
- Surcoût attendu (après revue) : une passe avant du tronc de la base sans gradient, et une seconde projection `lm_head` de l'élève sur les tokens de réponse (KL par tranches, recalculée au backward). Plus de logits pleins : voir § Revue.
- Effet de bord : un `.venv` vide créé par erreur dans le worktree (`uv run --no-sync`), ignoré par git, suppression refusée par le classifieur : à supprimer à la fin du run.

## Revue
- high, corrigé : mémoire. `kl_base > 0` basculait la perte en `nll` (logits pleins élève et base, 8192 × 130 560, plus copies float32 et `log_softmax` gardées pour le backward : ~9 Go au minimum, jusqu'à ~25 Go si toute la séquence est réponse). Désormais l'entropie croisée reste celle du `SFTTrainer` (`chunked_nll`, chemin de `kl_base = 0`), les états cachés de l'élève sont capturés par un crochet sur le tronc pendant cette passe, la base passe par le seul tronc (`no_grad`, `disable_adapter`), et la KL se calcule par tranches de 256 tokens de réponse sous `torch.utils.checkpoint` (`somme_kl_par_tranches`, `projection_logits` : `lm_head` du modèle puis `logit_scale`, `logits_scaling`, `final_logit_softcapping`). Estimation sans GPU (minicpm5-2b, 8192 tokens, V = 130 560) : surcoût persistant ~0,1 Go (états cachés de la base 34 Mo, positions de réponse rassemblées ≤ 67 Mo) ; transitoire par tranche ~0,7 à 0,9 Go (tenseurs 256 × V float32 de 134 Mo, avant ou recalcul arrière), non simultané avec les tranches de l'entropie croisée ; plus la passe avant de la base, sans activations gardées. Choix : la projection de l'élève est faite deux fois (entropie croisée de TRL, puis KL) pour garder intacts l'entropie croisée et les métriques de TRL ; coût en calcul ~2·N·H·V par passe, de l'ordre de 10 à 20 % d'un pas. Tests : équivalence valeur et gradient avec `somme_kl` non découpée (tranches de 3, dernière incomplète, T = 2), aucune réponse, mises à l'échelle de la config, arguments identiques avec et sans KL, vrai `SFTTrainer` en `chunked_nll` (test `lent`).
- low, corrigé : la KL n'est plus accumulée pour le journal hors entraînement (`self.model.training`) ; test `test_pas_de_journal_kl_en_evaluation`.
- Reste à mesurer : VRAM et temps réels sur l'essai de 5 pas (orchestrateur).
