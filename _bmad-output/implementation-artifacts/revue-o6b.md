# Revue O6b — régénération (2026-10-20)

Relecteur : Opus 5.5, sur `story/o6b-regeneration` fusionnée avec main (O4b, C3, C4). Second avis : Haiku (liste de 6 constats).

| # | Sévérité | Constat | Suite |
|---|---|---|---|
| 1 | HIGH (D1) | Le motif libre du juge DeepSeek hors guillemets passait à Mistral (`filtrer_motif`). | Corrigé : plus aucun texte libre du juge ni des contrôles dans la requête ; bloc = phrases fixes de `corrections.md` + extraits sous-chaînes exactes d'une ligne (≤ 200 car., 5 au plus). `MotifCorrection.motif`, `filtrer_motif` et `libelle_motif` supprimés. Test octet par octet sur toutes les requêtes Mistral. |
| 2 | HIGH | Procédure v17 `--taches LC` : CR (40) et CT (9) refusées du run 1402 recopiées écartées. | Corrigé (procédure) : `--taches CR,LC,CT` ; essai 1 relu du journal, verdicts du cache, refusées régénérées, autres Tâches recopiées sans appel. Test `test_v17_regenere_les_refusees_d_un_run_essais_un_sans_repayer`. |
| 3 | MEDIUM | Complément depuis un autre seed sans contrôle du Générateur ni des gabarits. | Corrigé : `_exiger_meme_generation` (modèle et gabarits id/version/SHA des sessions reprises) ; test. Gabarits courants identiques à ceux du run 1402 (vérifié). |
| 4 | LOW | Essais écrits seulement à la clôture de la session. | Rejeté : contrat d'une ligne par session close lu par `validate` ; rejeu sans coût (journal, cache). |
| 5 | LOW | `appel_refuse` = dernier essai refusé ? | Rejeté : dernier appel du brut refusé par construction, même session et `ok` exigés. |
| 6 | LOW | Estimation pire cas et plafond suggéré incohérents (LC seul). | Corrigé dans la spec : pire cas affiché ~4–6 € Mistral, ~24 € DeepSeek ; estimation à blanc avant le run. |

Procédure v17 et coûts : section « Procédure v17 » de `spec-o6b-regeneration.md`.
