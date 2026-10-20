# Diagnostic C4 : M4 ORPO Qwen3.5-0.8B, « CUDA driver error: device not ready »

## Cause
`ORPOTrainer` (TRL 1.13) ne borne pas la longueur des séquences : le prompt n'est jamais coupé et la découpe de la réponse (`[: max_length - longer_response_length]`) est fausse quand la réponse dépasse la limite. Sur les paires v16 avec `longueur_max = 2048`, 177 des 505 paires dépassent 2048 jetons (médiane 1662, p90 3607, max 5506). Le lot ORPO concatène chosen et rejected, et le vocabulaire de Qwen3.5 (248 320) donne des logits de plusieurs Gio par pas : la VRAM (6 Gio) déborde, d'abord en mémoire partagée WDDM (`vram_max_allocated` 15,4 Gio), puis le pilote échoue (`device not ready`, `Failed to create GPU mapping`) ou PyTorch lève `OutOfMemoryError` (reproduit : 2,88 Gio demandés, backward du premier pas). Même échec avec `longueur_max = 1024` : `max_length` n'est pas une borne effective dans ORPOTrainer (troncature défectueuse), pas une preuve que le réglage est ignoré.
Hors de cause (écartés) : chargement 4 bits de la base, adaptateur SFT (rechargé sans erreur), pin_memory (déjà `false`), noyaux fla (actifs), pilote 617.42. M1 et M3 n'échouent pas : leur jeu est pré-tokenisé et tronqué par le projet.

## Correctif (stabilité, pas fin du débordement)
`chargement.preparer_preferences(..., longueur_max=)` écarte les paires dont prompt + plus longue réponse + 2 jetons dépasse `longueur_max` (`exclus_trop_longues` dans les stats, consigné dans `jeu.json`). Le filtre rend le run stable ; il ne supprime pas le débordement en mémoire partagée. Le réglage `longueur_max` du TOML reste l'option. La reprise (`--reprendre`) compare `filtre_longueur` (longueur_max, marge, paires retenues et exclues) de la configuration résolue : un run d'avant le correctif est refusé. Test : `tests/train/test_chargement.py::test_preferences_ecarte_les_paires_trop_longues`.

## Preuve
Run diagnostic (config temporaire `pas_max = 5`, campagne jetable, racine hors dépôt) : 328 paires retenues sur 505, 5 pas faits, statut `complet`, 383 s (~77 s par pas), pic nvml 6,43 Go. `vram_max_allocated` reste à 15,4 Gio : le run déborde encore en mémoire partagée (lent, mais stable).

## Conséquences et points à confirmer par Anaël
- Le M4 v14-orpo-2048 s'entraîne sur 328 paires au lieu de 505 (35 % écartées, biais vers les cas courts) : à confirmer. Le run complet fait ~41 pas, soit ~50 min.
- Piste suivante si le débordement (15,4 Gio, ~77 s par pas) gêne, non codée : `longueur_max` 1536 ou 1024, gradient checkpointing, calcul des logits par morceaux.
- Alternative si ce biais gêne ou si la lenteur gêne : `longueur_max = 1536` (plus de paires écartées mais moins de débordement), ou une troncature maison de la réponse (non faite : décision de fond sur les cibles).
