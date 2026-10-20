---
title: 'Purge des intermédiaires d''export et contrôle d''espace (story C8)'
type: 'feature'
status: 'review'
---

## Intent

Le disque a saturé deux fois : chaque export garde `hf-f16/` et `modele-f16.gguf` (7 à 10 Go) en plus du Q4_K_M. Purge autorisée par Anaël pour les runs notés ; Q4_K_M, `mmproj-f16.gguf` et runs d'entraînement gardés.

## Réalisé

- Pas de purge immédiate à l'export (revue) : un export réussi rappelle de lancer `slmsp export purger --tous-notes` après notation. Événement `purge` ajouté à `log.jsonl` (runs immuables), `partiel` si une suppression échoue.
- `slmsp export purger --depuis <export_run_id> [--forcer-non-note]` : refus sans notation au statut `complet` (`runs/eval-notation/*` avec `modele_ref = ft:<export_run_id>`), si l'export n'est pas `complet`, si le Q4_K_M est absent ou de taille incohérente, ou si un intermédiaire contient un lien symbolique ou une jonction ; affiche l'espace libéré. `--tous-notes [--dry-run]` : tous les exports notés.
- Contrôle d'espace avant export : `[export]` de `config/entrainement.toml` (`facteur_espace`, défaut 3 ; `espace_libre_go` fixe, prioritaire). Refus `EspaceInsuffisant` avec la commande de purge suggérée.
- Fichiers : `src/slmsp/train/purge.py`, `train/config.py`, `train/export.py`, `cli/export.py`, `tests/train/test_purge.py`, `tests/train/test_export.py`.

## Auto Run Result

- Décisions : facteur par défaut passé de 2,4 à 3 (test réaligné 240 vers 300) ; `export purger` est une action positionnelle de `export` (`--depuis` y désigne l'export, pas le run d'entraînement). À confirmer par Anaël : le facteur 3.
- Report : après purge, `ft:<id>` en `f16` n'est plus résoluble (seul le Q4_K_M reste évaluable) ; le SHA du F16 reste dans `export.json`.

## Revue

Détail : `revue-c8.md`. high 1 corrigé (notation non complète comptée) ; medium 4 corrigés (purge immédiate retirée, liens refusés, export complet et Q4 cohérent exigés, échec partiel journalisé) ; low 5 corrigés.
