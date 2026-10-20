---
title: 'O6b — Génération vérifiée, régénération avec les motifs de refus'
type: 'feature'
created: '2026-10-20'
status: 'review'
---

# Spec O6b — Génération vérifiée, régénération

Partie O6b de `spec-o6-generation-verifiee.md` (fait autorité, revue incluse ; règles D1) : une cible CR, LC, CT refusée (contrôles déterministes ou juge O1) est régénérée par Mistral avec le motif du refus, au plus `essais_max − 1` fois, puis écartée. Touche AD-3 (verrous 3, 5, 6 du Générateur).

## Critères de fin (O6b)
- Boucle avec clients simulés : refus des tests → régénération ; refus du juge → idem ; 3 refus → écartée.
- Test D1 : la requête de régénération est exactement le gabarit de correction rempli par les amorces de la session et le bloc rendu des seules phrases fixes et extraits vérifiés (aucun texte libre du juge, revue) ; amorce de corrections fournie par l'appelant refusée.
- `validate` et `build` acceptent une session régénérée ; son exemple d'entraînement ne contient pas le bloc et garde l'entrée de la session non régénérée.
- Réutilisation sans coût au rejeu ; estimation et plafond Mistral incluant les essais ; verrous AD-3 verts.
- Aucun appel réel ; ruff ; contrôle rapide.

## Auto Run Result

Implémentation du 2026-10-20 (branche `story/o6b-regeneration`), aucun appel réel.

**Fichiers.** `config/prompts/generateur/{cr,lc,ct}-correction.md` (consigne de la Tâche inchangée + paragraphe fixe + `{corrections}`, v1) et `corrections.md` (une phrase fixe par code, un libellé ; validé par `core.gabarits`) ; `src/slmsp/core/schemas/amorce.py` (provenance `verification`, emplacement `corrections` qui lui est réservé) ; `src/slmsp/mistral/generateur.py` (`MotifCorrection`, `phrases_corrections`, `amorce_corrections` ; amorce `verification` refusée dans un seed ; corrections d'une autre session refusées) ; `src/slmsp/data/sessions.py` (`ExecuteurSessions.regenerer`) ; `src/slmsp/data/generation_verifiee.py` (`Regeneration`, boucle d'essais, `abandonner`) ; `src/slmsp/data/generate.py` (régénération dans `_executer_plan`, estimation, entrées du run, complément entre seeds) ; `src/slmsp/data/seed.py` + `src/slmsp/cli/data.py` (seed partiel) ; `config/donnees.toml` et `data/config.py` (`essais_max = 3`). Tests : `tests/data/test_regeneration.py` (18 après revue), `tests/data/test_seed_partiel.py` (2), `tests/mistral/test_gabarits_generateur.py` et `tests/data/test_generation_verifiee.py` réalignés.

**Flux.** Refus bloquant à l'essai n < `essais_max` → `Regeneration` (motifs bloquants structurés : code et extraits). `generate` appelle `ExecuteurSessions.regenerer` : le Générateur rend l'amorce de corrections (`corr-<session_id>-e<n>-<sha12>`, consignée dans `amorces-derivees.jsonl`), puis l'appel `*-correction` (CR : transcription gardée). La nouvelle cible est resoumise (contrôles, juge). `verification.jsonl` porte tous les essais ; `ecartees.jsonl` leur nombre ; `brut.jsonl` la seule chaîne retenue, sans l'amorce de corrections (ni `amorce_ids`, ni `amorces_derivees`).

**Bloc de corrections (D1, revu).** Pour chaque motif : `- <phrase fixe du code>` ; `Passages concernés : « … »` (extraits sous-chaînes exactes, d'une ligne, de la réponse refusée journalisée ou des amorces de la session, 5 au plus, 200 caractères). Le `motif` (texte libre) du juge et le `message` des contrôles ne sont jamais envoyés : ils restent dans `verification.jsonl`. Code sans phrase : `ProvenanceInvalide`. Les quatre codes du calibrage v14 (`lc_gain_lisibilite`, `lc_modalite_perdue`, `valeur_absente`, `url_inventee`) et tous les codes des contrôles et du juge ont leur phrase (test).

**Décisions prises seul (solution simple et réversible).**
1. `corrections.md` est un gabarit validé (verrou 6) dont la section Emplacements porte les phrases (`- code : phrase`) ; sa Consigne documente, n'est pas rendue.
2. Seuls les motifs **bloquants** entrent dans le bloc ; le `message` des contrôles déterministes n'y entre jamais (phrase fixe seule).
3. Pas de conversation multi-tour : la requête est un message unique (gabarit de correction), la réponse refusée n'y figure que par ses extraits vérifiés.
4. Motifs consignés dans `verification.jsonl` (essai précédent), pas dans `amorces-derivees.jsonl` (schéma `Amorce` strict, relu par `validate`).
5. Une régénération sans cible (réponse tronquée, provenance) écarte la session (`refus_par = regeneration`, abandon de son motif) ; `cible_illisible` et `juge-non-conclusif` ne sont pas régénérés.
6. La session régénérée est réécrite en fin de file (l'ordre de `brut.jsonl` n'est plus strictement celui du plan pour elle).
7. Estimation Mistral pire cas : chaque session CR, LC, CT compte `essais_max − 1` appels de correction (toutes refusées), entrée majorée de 3 000 caractères ; OpenRouter : pire cas × `essais_max`. Un rejeu complet ne paie rien, mais l'estimation reste au pire cas (ne pas passer `--plafond-estime-mistral 0` avec `essais_max` > 1 sur un run qui peut régénérer).
8. Gabarits de correction et `corrections.md` ajoutés aux entrées du run seulement si `essais_max` > 1 : un run O6a (essais 1) se reprend sans écart d'entrées.
9. `--verifiee --completer-depuis` admet les CR, LC, CT d'un run source **vérifié avec juge** (avant : toujours refusé).
10. **Jeu v17** (hors O6b strict, petit outillage) : `data seed --taches LC --completer-depuis SEED` tire seulement LC (filtre O5) et recopie à l'identique les autres amorces ; `generate --completer-depuis` admet un run d'un autre seed si les amorces de ses sessions reprises sont identiques dans le seed courant. **À confirmer par Anaël** : procédure ci-dessous.

**Procédure v17 (revue O6b, remplace la première version).** `--taches LC` seul recopiait les CR (40) et CT (9) refusées du run 1402 comme écartées. Les trois Tâches vérifiées vont donc dans `--taches` : leurs sessions sont replanifiées avec les mêmes identifiants (amorces recopiées, gabarits identiques à ceux du run 1402, vérifié), l'essai 1 est relu du journal Mistral sans appel, le verdict du juge vient du cache, et seules les refusées sont régénérées (essais 2 et 3) ; les 4 sessions non jugées du run 1402 sont jugées. Les autres Tâches (CO, Q, RD, RE, générique) sont recopiées du run 1402 sans appel (même Générateur et mêmes gabarits exigés depuis un autre seed). Test : `test_v17_regenere_les_refusees_d_un_run_essais_un_sans_repayer`.
1. `slmsp data seed --taches LC --completer-depuis 20261017-111645-seed-b335` (aucun appel).
2. Estimation à blanc (aucun run créé, aucun appel) : `slmsp data generate --depuis <SEED_LC> --verifiee --taches CR,LC,CT --completer-depuis 20261020-082915-generate-1402 --essais-max 3 --plafond-estime-mistral 8 --plafond-estime-openrouter 0`.
3. `slmsp data generate --depuis <SEED_LC> --verifiee --taches CR,LC,CT --completer-depuis 20261020-082915-generate-1402 --essais-max 3 --plafond-estime-mistral 8 --plafond-estime-openrouter 30` (plafonds à ajuster au chiffre affiché à l'étape 2).
4. `slmsp data validate --depuis <GEN>`, `slmsp data filter --depuis <VAL>`, `slmsp data build --depuis <FILTER> --variante recherche` (v17), puis le nettoyage habituel.
Coûts (ordres de grandeur, tarifs prudents de la spec). Estimations affichées, pire cas sans cache : Mistral ~4 à 6 € (80 LC + 2 corrections × 195 sessions CR, LC, CT, entrée majorée) ; DeepSeek ~24 € (195 sessions × 3 essais, cache non compté). Attendu : Mistral ~2 € (80 LC + ~150 à 200 corrections), DeepSeek ~5 à 8 € (80 LC à l'essai 1, CR et CT en cache, ~120 essais 2 puis ~60 essais 3). Le pire cas DeepSeek dépasse la règle des 10 € par tâche : décision d'Anaël (plafond 30 € pour l'estimation, registre de budget comme garde-fou réel).

**À confirmer par Anaël.** `lc_gain_lisibilite` bloquant (47 refus v14) : il pilote l'essentiel des régénérations LC et du coût. Procédure v17 et plafonds ci-dessus.

**Reports.** Taux de refus du calibrage non utilisé pour l'estimation (pire cas seulement). Mise à jour de `spec-o6-generation-verifiee.md` (document de décision) laissée à l'orchestrateur.

## Revue

Revue du 2026-10-20 (Opus, après second avis Haiku), sur la branche fusionnée avec main.
- HIGH (D1) corrigé : le motif libre du juge (hors guillemets, ex. « écrire plutôt … ») passait à Mistral via `filtrer_motif`. Supprimés : champ `MotifCorrection.motif`, `filtrer_motif`, libellé `libelle_motif` ; le bloc ne porte que phrases fixes et extraits sous-chaînes exactes d'une ligne (≤ 200 caractères, 5 au plus). Test octet par octet sur toutes les requêtes.
- HIGH corrigé (procédure) : `--taches LC` laissait écartées les CR et CT refusées du run 1402 ; procédure v17 avec `--taches CR,LC,CT` (essai 1 relu du journal, cache du juge), test `test_v17_…`.
- MEDIUM corrigé : complément depuis un autre seed sans contrôle du Générateur ni des gabarits ; `_exiger_meme_generation` refuse un autre `modele_generateur` ou des gabarits (id, version, SHA) différents ; test.
- LOW rejeté : essais écrits au fil de l'eau dans `verification.jsonl` ; une ligne par session close est le contrat lu par `validate`, et un essai interrompu se rejoue sans coût (journal Mistral, cache des verdicts).
- LOW rejeté : `appel_refuse` est par construction le dernier appel du brut refusé, et `amorce_corrections` exige un appel `ok` de la même session.
- LOW corrigé (spec) : estimation pire cas v17 incluant CR et CT, plafonds cohérents (étape d'estimation à blanc).
