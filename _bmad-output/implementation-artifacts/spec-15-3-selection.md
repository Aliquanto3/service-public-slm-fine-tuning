---
title: 'Sélection des cibles parmi des candidats notés (story 15.3, O3)'
type: 'feature'
created: '2026-10-20'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-o3-selection.md'
  - '{project-root}/_bmad-output/planning-artifacts/stories-epic-15-nuit-2026-10-20.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-15-2-candidats.md'
warnings:
  - 'Licence de MiniCPM5-2B (Apache 2.0) relevée dans config/modeles/minicpm5-2b.toml (fiche HF lue le 2026-10-17) ; la carte du modèle est absente de models/ : à relire sur la fiche avant toute variante diffusable.'
deferred:
  - 'Règle 9 (paires de préférence v2) : avec C5.'
  - 'Cibles DeepSeek et règle 5 (minimum des scores DeepSeek et Kimi) : candidats openrouter ignorés et comptés cette nuit (amendement 1).'
  - 'Poids par Tâche configurables (`[selection.poids.<TACHE>]`) : poids égaux codés en dur.'
  - '`data build --nettoyage` et `--sous-ensemble` refusent un jeu à cibles sélectionnées (chaîne non transposée).'
  - 'Plancher CR (30) sans option CLI.'
---

<intent-contract>

## Intent

**Problem:** la cible de chaque ligne CR et LC doit être le meilleur candidat noté (base locale ou Mistral), jamais une cible moins bonne que la base.

**Approach:** `slmsp data build --selection` lit les candidats (15.2), les verdicts du juge de données et le jeu SFT d'origine, et écrit une nouvelle version : CR et LC gagnants, RE retirée, autres Tâches copiées ; lignes v2 pour les cibles locales, MANIFEST v2 (bloc `selection`), revérifiés par `train run`.

## Boundaries & Constraints

**Always:** spec O3 amendée (9 points du 20/10, qui priment) ; D1 (aucun texte rédigé : cibles relues dans les journaux) ; Registre exigé avant tout run ; v1 relue telle quelle.

**Never:** cible d'un juge, de Claude ou d'OpenRouter ; appel réseau ; `verdict_modele` lu ; repli sur la ligne d'origine d'une ligne sans candidat accepté.

</intent-contract>

## Contrat

- CLI : `slmsp data build --selection --candidats RUN_CANDIDATS --verdicts RUN_JUGE[,RUN_JUGE...] --taches-selection CR,LC --retirer RE --variante recherche` (`--depuis` devient facultatif, toujours exigé hors `--selection`).
- Jeu source : jeu SFT du `build_run_id` du run de candidats (SHA revérifié) ; refus s'il est restreint ou déjà sélectionné. Tokenizer : celui de la règle de nettoyage du run de candidats, SHA identique exigé.
- Verdicts : chaque run `data-juger` a `depuis == RUN_CANDIDATS` ; un run par juge ; le juge principal est `[juge_donnees].modele` (DeepSeek), exactement un run. Acceptation : verdict `accepte` et notes ≥ `seuils` du run (recalculés). Score : moyenne des critères normalisés (note / max de `CRITERES_JUGE_DONNEES`, `couverture` dans [0, 1]) ; note manquante ou hors échelle : candidat ignoré (`notes_invalides`).
- Gagnant : score max ; égalité : base, Mistral, température basse, graine, `candidat_id`. Ligne sans candidat accepté : écartée (`aucun_accepte`). Moins de 30 CR retenues : refus, rien sous `data/train/` ; LC à 0 : avertissement.
- Gagnant Mistral : ligne d'origine copiée (son `candidat_id` doit être le dernier `appel_id`). Gagnant base : journal local recoupé (session, `usage`, `generateur`, statut `ok`, SHA de la réponse, conversation de la requête = entrée), texte `cible_apprise(..., compter)` ; ligne `schema_version = 2`, `meta.cible = {source, appel_local_id}`, `meta.generateur = slm:<slug>`, `appel_ids` = appels Mistral de l'entrée (CR : transcription ; LC : vide), `source` = sources d'origine + entrée `modele-base` du Registre, licences du Registre.
- Registre : `genere_par = "modele-base"` et `auteur_contenu = "modele-base"` ajoutés ; entrée `openbmb/MiniCPM5-2B` (Apache 2.0, usage `recherche`) ; `RegistreLicences.source_modele_base("slm:<slug>")` : unique entrée `modele-base` dont le nom vaut le slug (casse ignorée).
- MANIFEST v2 : bloc `selection` (source et SHA, nettoyage source, run de candidats et SHA, SHA de chaque `verdicts.jsonl`, juge, SHA des grilles, base, version de nettoyage, SHA du tokenizer, bilans par Tâche : gagnants par source, part de la base, score moyen, écartées par motif ; candidats ignorés par motif ; SHA de `selection.jsonl`, détail par ligne avec gagnant, notes et score ; avertissements). `nettoyage` retiré (repris dans `selection.nettoyage_source`).
- `train` : `charger_jeu` revérifie la chaîne (`controler_selection`, `core.selection.verifier_selection`, comptes) ; `train run` (SFT) appelle `recontroler_cibles` (journal local en lecture seule, octets et `nettoyer_cible` de la version du MANIFEST). Jeu v1 : 0 ligne contrôlée, journal non lu.

## Code Map

- `src/slmsp/data/selection.py` : `lancer_selection`, `score`.
- `src/slmsp/core/selection.py` : `verifier_selection` (partagé `data` / `train`).
- `src/slmsp/core/schemas/entrainement.py` : `CibleLigne`, `MetaLigne.cible`, `LigneEntrainement` v1|v2, `Selection`, `BilanSelection`, `ManifesteJeuEntrainement` v1|v2.
- `src/slmsp/train/chargement.py` : `_Meta` v2, `controler_selection`, `recontroler_cibles` ; `src/slmsp/train/run.py` : appel.
- `src/slmsp/data/licences.py`, `src/slmsp/core/schemas/amorce.py`, `data/registre-licences.toml` : `modele-base`.
- `src/slmsp/data/nettoyage.py`, `src/slmsp/data/sous_ensemble.py` : refus d'un jeu sélectionné.
- `src/slmsp/cli/data.py` : `data build --selection`.
- Tests : `tests/data/test_selection.py` (nouveau), `tests/data/test_licences.py` (registre réel, liste figée).

## Auto Run Result

- Statut : implémenté, tests ciblés verts (selection, build, licences, nettoyage, sous-ensemble, candidats, préférences, verrous AD-3, juge de données, train chargement / préférences / run, cli data, core).
- Décisions prises seul (solution la plus simple et réversible) :
  1. Gagnant Mistral = ligne d'origine copiée (sa cible est déjà la cible Mistral nettoyée, prouvé en 15.2) : ligne v1 inchangée.
  2. `auteur_contenu = "modele-base"` ajouté au Registre (aucune valeur existante ne convenait) — **à confirmer par Anaël** (extension du verrou D1.1).
  3. Ligne v2 : la source `mistral/reponses-generateur` est gardée même quand plus aucun appel Mistral n'y figure (LC) : choix conservateur (licence plus restrictive) — **à confirmer par Anaël**.
  4. Recontrôle de provenance strict : journal local non conforme, ou cible que `cible_apprise` refuserait, lève `ProvenanceInvalide` (run `partiel-erreur`) au lieu d'écarter la ligne.
  5. Un run de jugement des autres juges (Kimi) est accepté et consigné, sans effet (ses verdicts ne portent que sur des candidats OpenRouter, ignorés).
  6. Licence MiniCPM5-2B : Apache 2.0 d'après la fiche `config/modeles/minicpm5-2b.toml` (pas de carte HF locale) — **à confirmer par Anaël** avant toute variante diffusable.

## Commande du run réel (orchestrateur, après les jugements DeepSeek)

```
slmsp data build --selection --candidats <RUN_CANDIDATS> --verdicts <RUN_JUGER_DEEPSEEK>[,<RUN_JUGER_KIMI>] --taches-selection CR,LC --retirer RE --variante recherche
```

## Revue

Revue Opus du 2026-10-21 sur d684245 (base 3cae049, non rebasée sur consigne). Complexité : 0 constat (`verifier_selection`, `recontroler_cibles`, détail en ajout seul : linéaires).

| # | Sévérité | Source | Constat | Suite |
|---|---|---|---|---|
| 1 | medium | second avis | `_run_termine` n'exigeait que « pas en cours » : un run de candidats ou de jugement `partiel-erreur` / `interrompu` passait. | Corrigé : `complet` exigé ; `--accepter-partiel` admet un statut final non complet (jamais `en_cours`), consigne `runs_partiels`, `sans_verdict_par_tache` et un avertissement au MANIFEST, `accepter_partiel` au run. |
| 2 | medium | second avis | `data build --preferences` et `data candidats` acceptaient un jeu à cibles sélectionnées (paires ou candidats faux). | Corrigé : `preferences._exiger_sans_selection` appelé par les deux ; test des quatre étapes aval (préférences, candidats, nettoyage, sous-ensemble). |
| 3 | low | second avis | `--retirer` vide par défaut : un oubli réintroduisait RE. | Corrigé : obligatoire avec `--selection` (`--retirer ""` explicite admis) ; refusé sans `--selection`. |
| 4 | low | second avis | `train run` ne comparait pas `meta.cible.source` au modèle entraîné. | Corrigé : `recontroler_cibles(base=...)`, appelé avec `slm:<modele>` ; `selection.base` recoupé aussi. |
| 5 | low | second avis | CLI : `ProvenanceInvalide`, `SourceSansLicence`, `ValueError` remontaient en trace. | Corrigé : message `slmsp : …`, code 2. |
| 6 | low | second avis | Docstring « seuils recalculés » inexacte ; min des critères implicite. | Corrigé : seuils lus dans la config du run de jugement puis réappliqués ; grille de 0 (min explicite) au max de `CRITERES_JUGE_DONNEES`, `couverture` de 0 à 1 (aucune grille n'a d'autre min). |
| 7 | low | second avis | Tests manquants. | Corrigé : refus partiel (2 cas) et `en_cours`, `cible.source ≠ base`, câblage `train run` (espion sur `executer`), gardes aval, motif `sans_candidat` désormais émis (ligne sans aucun candidat), erreur de Registre propre en CLI. |
| 8 | low | second avis | `mistral/reponses-generateur` gardée en source d'une ligne LC v2 sans appel Mistral. | Laissé (prudent : licence la plus restrictive gardée) ; **à confirmer par Anaël**. |

Reports : build réel de v20 après la fin du jugement DeepSeek `20261021-000207-juger-6e70` (en cours lors de la revue) ; vérifier au MANIFEST `par_tache.CR.retenues ≥ 30`, `part_base`, `sans_verdict_par_tache` vide, puis `train run` sur v20 (recontrôle des cibles locales contre `generations-locales.sqlite`).

```
slmsp data build --selection --candidats 20261020-232707-candidats-a5fd --verdicts 20261021-000207-juger-6e70 --taches-selection CR,LC --retirer RE --variante recherche
```
