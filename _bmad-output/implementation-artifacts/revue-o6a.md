# Revue O6a — génération vérifiée, vérification (2026-10-20)

Revue de `491abf2` après fusion de `main` (C4), avec la liste du second avis et les constats du calibrage réel O1 (`runs/data-juger/20261020-072807-juger-85c1`). Aucun appel réel.

| # | Sévérité | Constat | Décision |
|---|---|---|---|
| 1 | high | `--verifiee --completer-depuis` recopiait sans vérification les sessions CR, LC, CT closes du run source (`--taches` partiel). | Corrigé : `ManifesteInvalide` avant tout run si une session reprise appartient à une Tâche vérifiée (`generate.py`) ; test. |
| 2 | medium | Pire cas OpenRouter : une session non conclusive est rejouée jusqu'à `INTERRUPTIONS_MAX`. | Rejeté : chaque invocation juge une session au plus une fois (≤ `TENTATIVES_MAX` appels), et la reprise réestime puis réapplique le plafond sur les sessions restantes ; le cumul sur plusieurs invocations reste borné par le sous-plafond du registre. |
| 3 | medium | `[verification.ct_blocs] signature` refusait « Signature [nom] » et « Signature » (`sign[ée]`). | Corrigé : `sign(?:[ée]\|ature\b)` (toml et défaut du code) ; tests. |
| 4 | low | `lc_titre` sur une première ligne courte sans ponctuation. | Rejeté : aucune occurrence sur les 80 LC v14 du calibrage ; à revoir au calibrage relu si elle apparaît. |
| 5 | low | `cr_sections_desordre` et `cr_actions_vide` prenaient une puce « * Actions … » des Points abordés pour le titre. | Corrigé : `_titre_section` préfère une ligne qui ne porte que le titre ; test. |
| 6 | low | `Verificateur.clore` hors `try` : une erreur d'écriture du rapport laissait le run `en_cours`. | Corrigé : le run est clos `partiel-erreur` puis l'erreur remonte. |
| 7 | low | `essais_max` > 1 accepté (défaut 3) alors qu'O6a ne fait qu'un essai : run annoncé à 3 essais, comportement changé à sa reprise après O6b. | Corrigé : refus au-delà de 1 (`ConfigurationInvalide` en CLI), `[verification] essais_max = 1` jusqu'à O6b ; test. |
| 8 | high | DeepSeek V4 Pro met ~2,8 min par appel ; le délai de lecture du client (300 s) coupait l'appel (ReadTimeout). | Corrigé : `[juge_donnees] delai_lecture = 900`, `delai_appel = 900`, `duree_totale_max_appel = 1800` (validée ≥ `delai_appel`), transmis par `config_openrouter` à `data juger` et à `data generate --verifiee` ; test. |
| 9 | high | 192 jugements en série : ~9 h. | Corrigé : `[juge_donnees] appels_paralleles = 8`, `FileOrdonnee` (threads, résultats rendus et écrits dans l'ordre de soumission par le seul thread appelant) pour `data juger` et `data generate --verifiee` ; registre de budget et journal des appels sûrs entre threads (connexion SQLite par opération, `BEGIN IMMEDIATE`, WAL), `cout_total` et cache du juge sous verrou. Après une erreur de budget ou d'API, les jugements non lancés sont annulés, ceux en cours (payés) écrits. Tests avec client simulé lent (pic de 4 appels simultanés, ordre des verdicts et de `brut.jsonl`). |
| 10 | low | Deux candidats de même clé jugés en même temps paient deux appels (le cache n'est rempli qu'à la fin). | Rejeté : cas marginal (cibles distinctes par session), surcoût borné par l'estimation. |

Tests existants du juge passés en séquentiel (`appels_paralleles = 1` dans l'aide `juge`) : leurs réponses scriptées supposent l'ordre des appels.

## Commande payante finale (orchestrateur)

Calibrage gratuit d'abord (inchangé) : `slmsp data generate --depuis 20261017-111645-seed-b335 --verifiee --sans-juge --essais-max 1 --taches CR,LC,CT --completer-depuis 20261019-225253-generate-9ba4 --plafond-estime-mistral 0`.

Puis : `slmsp data generate --depuis 20261017-111645-seed-b335 --verifiee --taches CR,LC,CT --completer-depuis 20261019-225253-generate-9ba4 --plafond-estime-mistral 0 --plafond-estime-openrouter 9`

Coût estimé (195 sessions CR 80, LC 80, CT 35, tarifs `tarifs.toml` majorés) : juge DeepSeek ~2,3 € attendus, pire cas 8,0 € (2 tentatives, 16 000 tokens de sortie, sans cache) ; Mistral 0 € (réponses v14 réutilisées ; si O5 change le seed ou le gabarit LC, relever `--plafond-estime-mistral`). Durée : ~195 × 2,8 min / 8 ≈ 70 min.
