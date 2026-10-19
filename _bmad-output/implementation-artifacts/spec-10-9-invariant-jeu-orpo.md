---
title: 'Story 10.9 — Invariant de campagne du jeu pour les runs ORPO'
type: 'bugfix'
created: '2026-10-19'
status: 'done'
baseline_revision: '79e95f9'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-10-4-runs-d-entrainement-configurables.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
---

## Intent

`slmsp data build --preferences --depuis <BUILD_SFT>` écrit les paires dans une nouvelle version (`vN`, build `-preferences-`). Les invariants `jeu_version` et `jeu_build` d'un run ORPO prenaient cette version et ce build, donc un M4 sur v3 ne pouvait pas rejoindre la campagne d'un M1 sur v2. Les invariants d'un run ORPO sont désormais ceux du jeu SFT d'origine des paires.

## Boundaries

- Hors périmètre : `data/preferences.py`, schéma des MANIFEST, `verifier_campagne` (inchangé), runs SFT.
- Pas de migration des `run.json` existants.

## Décisions

- Source : `jeu_sft_version` et `build_run_id` du MANIFEST des préférences (déjà écrits par `data build --preferences`). Absents, `ConfigurationInvalide` explicite.
- Traçabilité : la version, le build et le SHA des paires restent dans le bloc `jeu` de la configuration résolue (`version`, `run_build`) et dans `jeu.json`. Rien n'est perdu.
- Cohérence : si `sft_run_id` est donné, le build SFT d'origine doit égaler `invariants.jeu_build` du run SFT, sinon `ConfigurationInvalide` citant les deux builds. Le contrôle a lieu avant le verrou GPU, sans créer de run. Un run SFT sans `invariants.jeu_build` est refusé (`ConfigurationInvalide`), décision de revue.
- Reprise (`--reprendre`) : `_rouvrir` compare la configuration résolue entière, invariants compris. Un run ORPO créé avant cette story a consigné la version et le build des paires. Choix : si les invariants consignés valent ceux des paires, la reprise les reprend tels quels (`_invariants_jeu_reprise`), donc ces runs restent reprenables sans modification de `run.json`. Alternative écartée : migrer les `run.json` (réécrit des artefacts, irréversible). Un run créé après la story consigne l'origine SFT et se reprend normalement.
- Un ORPO ancien (invariants = paires) ne peut pas rejoindre une campagne SFT d'une autre version : constat inchangé, hors périmètre.

## Acceptance Criteria

- ORPO sur paires v2 dérivées du build SFT v1 : invariants identiques à ceux du M1 v1 ; `jeu.version` = v2 tracée.
- Build source différent de celui du run SFT : refus avant création de run, deux builds cités.
- MANIFEST de préférences sans origine SFT : refus explicite.
- `--reprendre` d'un run ORPO à invariants « paires » : accepté. Runs SFT inchangés (suite `tests/train` verte).

## Auto Run Result

Fait : `src/slmsp/train/run.py` (`jeu_sft_origine`, `_exiger_build_sft_coherent`, `_invariants_jeu_reprise`, docstrings) ; tests dans `tests/train/test_run.py` ; la fixture `ecrire_jeu` écrit désormais `jeu_sft_version` et `build_run_id` dans les MANIFEST de préférences. Tests ciblés `tests/train` et `tests/data/test_preferences.py` verts, ruff et contrôle rapide OK.

## Limites connues

- Une campagne dont un ancien run ORPO a consigné la version et le build des paires (ex. `minicpm5-2b-v3-orpo-4096`) refuse un nouveau M4 : invariants différents. Pas de correction : ces campagnes sont closes, les campagnes v4 partent neuves (décision de l'orchestrateur, 2026-10-19).

## Revue

- medium · second avis 1 · corrigé : run SFT sans `invariants.jeu_build`, le contrôle de cohérence passait en silence ; désormais `ConfigurationInvalide` avant création de run (test `test_orpo_refuse_un_run_sft_sans_jeu_build`).
- medium · second avis 2 · rejeté (limite consignée) : nouveau M4 refusé dans une campagne à ancien ORPO « paires » ; campagnes mortes, voir Limites connues.
- low · second avis 3 · corrigé : tests de reprise d'un run postérieur à la story et de refus d'invariants consignés inconnus.
- low · second avis 4 · corrigé : `pytest.raises(SlmspError)` avec type exact vérifié (`reprendre` lève `SlmspError` « déjà complet »).
- low · second avis 5 · rejeté : `jeu_sft_origine` lève `ConfigurationInvalide` explicite si les champs manquent ; voulu (critère « refus explicite »), le schéma les rend obligatoires.
- low · second avis 6 · rejeté : un run `data-build` détermine sa version ; comparer le build suffit.
- info · reviewer · reporté hors story : `tests/train/test_config.py::test_campagne_v2_invariants[granite-4.0-1b-v2]` échoue déjà sur main (9d492c9 ; 3072 contre 8192 attendu, après 93f32d6) ; à réaligner dans une PR de config.
- Complexité : 0 constat (lectures ponctuelles de `run.json`, pas de structure qui grossit).
