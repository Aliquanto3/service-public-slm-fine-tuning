---
title: 'O6a — Génération vérifiée, partie vérification'
type: 'feature'
created: '2026-10-20'
status: 'review'
---

# Spec O6a — Génération vérifiée, partie vérification

Partie O6a de `spec-o6-generation-verifiee.md` (fait autorité, revue incluse) : contrôles déterministes CR, LC, CT factorisés avec `validate`, branchement du juge O1, écart des cibles refusées, rapport, échantillon et calibrage. Sans régénération ni changement du Générateur (O6b).

## Critères de fin (O6a)
- Tests unitaires de chaque contrôle, cas passant, refusant et pièges (« Vous devez » pour « Le demandeur doit », « Mme » pour « Madame », mot capitalisé après puce, nom en minuscule dans la transcription).
- `validate` inchangé (`tests/data/test_validate*.py` verts) ; une cible acceptée n'est pas rejetée par `validate`.
- Calibrage sans appel ; écart et `AbandonSession` ; reprise sans double appel ; budget refusé au-delà du plafond.
- Aucun appel réel ; ruff ; contrôle rapide.

## Auto Run Result

Implémentation du 2026-10-20 (branche `story/o6a-verification`), aucun appel réel.

**Fichiers.** `src/slmsp/data/verification.py` (contrôles purs ; règles de valeurs, dates, nombres en lettres et structure déplacées de `validate`, qui les appelle) ; `src/slmsp/data/generation_verifiee.py` (`Verificateur` : contrôles, juge O1, fichiers du run) ; `src/slmsp/data/generate.py` (`verificateur`, `plafond_estime_mistral`, estimations avant toute création de run) ; `src/slmsp/data/validate.py` (factorisation, comportement inchangé) ; `src/slmsp/data/config.py` + `config/donnees.toml` (`[verification]`) ; `src/slmsp/data/juge_donnees.py` (`source_session` rendu public) ; `src/slmsp/core/schemas/session_donnees.py` (motif `verification_refusee`) ; `src/slmsp/cli/data.py` (options de `data generate`) ; `tests/data/test_verification.py` (26 tests), `tests/data/test_generation_verifiee.py` (7 tests).

**Commande.** `slmsp data generate --depuis SEED --verifiee [--sans-juge] [--essais-max N] [--plafond-estime-mistral EUR] [--plafond-estime-openrouter EUR] [--taches CR,LC,CT --completer-depuis GENERATE_RUN_ID]`, ou `--reprendre RUN_ID` (réglages relus du run ; reprise refusée si le run et l'invocation diffèrent sur la vérification). Fichiers ajoutés au run : `verification.jsonl`, `verdicts.jsonl`, `ecartees.jsonl`, `interruptions-juge.jsonl` ; à la fin d'un run `complet` : `rapport.json`, `echantillon.md`, `calibrage.md`.

**Codes.** Partagés avec `validate`, toujours bloquants : `url_inventee`, `valeur_absente`, `cr_sections_manquantes`, `ct_format_incomplet`, `lc_valeur_perdue`. Propres à O6a : `cr_sections_desordre`, `cr_plafond_mots`, `cr_actions_vide`, `lc_modalite_perdue`, `lc_modalite_reduite` (non bloquant), `lc_conseil_ajoute`, `lc_titre`, `lc_gain_lisibilite`, `ct_blocs`, `ct_sans_emplacement` (non bloquant), `nom_absent` (non bloquant par défaut, `[verification] non_bloquants`). Refus du juge : `juge_<critère>`.

**Décisions prises seul (solution simple et réversible).**
1. Deux modules : `verification.py` (fonctions pures, demandé par la spec) et `generation_verifiee.py` (fichiers du run, juge), pour garder `generate.py` lisible ; `generate` n'importe le vérificateur que pour le typage.
2. Estimations Mistral et OpenRouter calculées **avant** la création du run (nouveau run et reprise) : un plafond dépassé ne laisse aucun run (`PlafondEstimeDepasse` d'O1, réutilisée). `--plafond-estime-mistral 0` garantit un rejeu sans appel Mistral nouveau.
3. Pire cas OpenRouter : la cible n'étant pas connue avant la génération, chaque session CR, LC, CT compte `TENTATIVES_MAX` appels, entrée = grille + 6 000 tokens, sortie au `max_tokens` du juge ; le cache n'est pas déduit.
4. Verdict `non-juge` ou `invalide` : session laissée ouverte (rejouée à la reprise, réponse Mistral réutilisée), run `partiel-erreur` ; écartée (`juge-non-conclusif`) après 2 interruptions, comme O1.
5. CT, valeurs : contrôlées sur tout le texte (règle de `validate`), pas seulement hors crochets, pour qu'une cible acceptée ne soit jamais rejetée par `validate` ; noms propres : hors crochets.
6. Ordre des blocs CT : plus longue suite ordonnée des occurrences trouvées (un mot de politesse cité dans le corps ne crée pas de faux désordre).
7. Classes LC élargies à des synonymes de même classe (condition : « quand », « dès que » ; restriction : « seul » ; obligation : « il faut », « nécessaire » ; échéance : « délai », « jusqu'à ») pour limiter les faux positifs de la réécriture en langage clair ; listes dans `[verification.lc_marqueurs]`.
8. `--essais-max` accepté et consigné, mais O6a ne fait qu'un essai (affiché).
9. `rapport.json`, `echantillon.md`, `calibrage.md` écrits seulement à la fin d'un run `complet` (un fichier de run n'est jamais réécrit) ; le CLI affiche le rapport s'il existe.

**Calibrage gratuit (cibles v14, `20261019-225253-generate-9ba4`, contrôles seuls, lecture seule, sans run).** CR 0/77 écartée, CT 0/35, LC 61/80 (76 %). Codes bloquants LC : `lc_gain_lisibilite` 47 (32 sessions refusées par ce seul code), `lc_modalite_perdue` 17, `valeur_absente` 13, `url_inventee` 2. Non bloquants : `nom_absent` CR 22, CT 12 (surtout noms d'institutions : « Direction Départementale… », « Préfet », « Maire ») ; `lc_modalite_reduite` 29. Faux positifs corrigés pendant le calibrage : blocs CT en gras (`**[Références]**`, `**Madame,**`, `**Lyon, le [date]**`) qui faisaient refuser 35/35 CT. **À confirmer par Anaël** : garder `lc_gain_lisibilite` bloquant (il écarte 59 % des LC v14, conforme au critère du test LC mais coûteux en volume) ou le passer non bloquant ; relire les refus `lc_modalite_perdue` (permission et obligation surtout) avant le run payant.

**Reports.** Régénération (O6b). Échantillon `echantillon.md` et `calibrage.md` produits par la commande réelle seulement (le calibrage ci-dessus a été fait hors run, en lecture seule).

## Revue

Détail : `revue-o6a.md`.
- high, corrigé : `--completer-depuis` recopiait des CR, LC, CT non vérifiées (refus avant tout run).
- high, corrigé : délais OpenRouter du juge (900 s de lecture) transmis au client.
- high, corrigé : jugements en parallèle (`appels_paralleles = 8`), écriture ordonnée, budget sûr entre threads.
- medium, corrigé : bloc signature CT « Signature [nom] ».
- medium, rejeté : pire cas × `INTERRUPTIONS_MAX` (borne par invocation, réestimée à la reprise).
- low, corrigés : titre de section CR, clôture du run garantie, `essais_max` limité à 1 avant O6b.
- low, rejetés : `lc_titre` (0 cas au calibrage), double appel de même clé en parallèle (marginal).
