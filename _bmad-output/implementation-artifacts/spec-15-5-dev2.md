---
title: '15.5 (N5) — jeu de développement dev2, 160 items en brouillon'
type: 'feature'
created: '2026-10-21'
status: 'review'
context: ['{project-root}/_bmad-output/implementation-artifacts/spec-o4-jeu-dev.md', '{project-root}/_bmad-output/planning-artifacts/stories-epic-15-nuit-2026-10-20.md']
warnings: []
deferred: []
---

## Intent

**Problème :** dev1 sert à toutes les décisions et finit par être « appris » des décisions elles-mêmes ; il faut un second jeu de développement de même format, disjoint de tout ce qui existe, pour confirmer les choix sans toucher v1.1.

**Approche :** même procédé que dev1 (spec O4) : 20 items par Tâche (Q, RD, CR, LC, CO, RE, CT, NR ; 7 / 7 / 6), écrits depuis des sources réelles ou fictifs, numérotés 601 à 620, assemblés en brouillon, contrôlés (composition, sources, disjonction), prêts pour la contre-vérification DeepSeek + GLM. Pas de gel.

## Boundaries & Constraints

**Always :** items d'évaluation seulement (D1 : ils n'entrent dans aucun générateur ni jeu d'entraînement) ; faits des références tirés des sources citées (chunks service-public, articles LEGI en vigueur, cassettes MCP, catalogue local) ; consigne CR commune conservée ; disjonction de v1.0, v1.1, dev1, `data/train/v*` (dont v18) et des amorces seed (dont `20261020-093126-seed-4fcf`).

**Never :** lecture d'un run de génération ou de notation ; appel payant (seul le serveur MCP public data.gouv est appelé, pour les cassettes) ; gel ; modification de v1.x ou de dev1 ; plaidoyer adressé aux juges.

## Code Map

- `eval/construction/dev2/` -- brouillons `<CODE>.jsonl`, verdicts `verification/`, README de construction
- `eval/jeu/dev2/items.jsonl` -- assemblage (160 items, SHA-256 `a922c79c…`), sans MANIFEST
- `eval/cassettes/RD-601` à `RD-620` -- cassettes MCP (20, dont 2 pannes)
- `src/slmsp/evaluation/config.py` -- `CIBLES_DEV_COMPLET`, `CIBLES_JEU_DEV_COMPLET`, `cibles_jeu("devN")`
- `eval/outils/verifier_jeu_croise.py` -- disjonction contre les autres jeux `devN`, option `--reference`

## Tasks & Acceptance

**Exécution :**
- `eval/construction/dev2/*.jsonl` -- 160 items + 160 verdicts de second passage -- livrable de la story
- `src/slmsp/evaluation/config.py` -- cibles 20 × 8 pour `devN` autre que dev1 (dev1 garde CR à 19) -- sinon `--verifier-seulement` refuse dev2
- `eval/outils/verifier_jeu_croise.py` -- `versions_reference(racine, exclure)` : v1.x + autres `eval/jeu/devN` ; `controler_disjonction(..., version=)` ; `disjonction --reference` -- dev2 doit être disjoint de dev1, et un worktree se contrôle contre les données du dépôt principal
- tests réalignés : `test_items_dev1.py` (dev1 + dev2, cassettes par plage), `test_bac_a_sable.py` (81 cassettes, 154 appels, 8 pannes), `test_seed.py` (dev2 protégé), `test_jeu_dev.py` et `test_verifier_jeu_croise.py` (nouveaux cas)

**Critères d'acceptation :**
- `slmsp eval gel --version dev2 --verifier-seulement` : 160 items stricts, 0 erreur, 0 écart.
- `verifier_jeu_croise.py disjonction --version dev2 --reference <dépôt principal>` : « disjoint ».
- `tests/eval_outils/test_items_dev1.py` avec `SLMSP_EVAL_SOURCES` : verts (extraits, documents, références CO, articles CT, replis RD).

## Auto Run Result

Statut : review. Tests ciblés (`tests/eval_outils`, `tests/evaluation`, `tests/core`, `tests/compare`, `tests/mcp`, `tests/data/test_seed.py`, `tests/data/test_verrous_ad3.py`, `tests/data/test_alignement_o5.py`, `tests/outils`, `tests/publication`, `tests/harness/test_budget.py`, `tests/harness/test_modes.py`, `tests/judge`) : verts après réalignement ; `ruff check`, `ruff format --check` verts.

Composition : Q 3 sans réponse et 10 amorces réelles ; RD 5 demandes de valeurs, 2 replis, 16 producteurs ; CR 4 transcriptions de plus de 4 000 mots (4 018 à 4 063) ; CT 8 avec base réglementaire ; NR 10 questions sourcées et 10 consignes à réponse unique. Thèmes répartis comme dev1.

Décisions prises seul :
- Identifiants 601 à 620 et cassettes `RD-6xx`, pour ne heurter ni dev1 (501 à 523) ni v1.x.
- `CIBLES_DEV` (dev1, CR à 19) inchangé ; nouvelles cibles complètes pour `devN ≠ dev1` : la plus réversible, sans toucher le gel de dev1.
- La disjonction inclut désormais les autres jeux `devN` assemblés (`eval/jeu/devN/items.jsonl`), le jeu contrôlé exclu ; option `--reference` pour un worktree sans `data/` ni `runs/`.
- `eval/jeu/dev2/items.jsonl` assemblé sans MANIFEST, comme dev1 avant son gel : dev2 entre ainsi dans les versions protégées de `seed` et `filter` (spec O4, règle 2).
- Cassettes RD enregistrées en mode connecté (serveur MCP public, gratuit) ; pannes simulées sans requête.
- Sources : une fiche ou un article par item au plus ; fiches écartées quand le texte contenait une incohérence (seuils contradictoires, exemple chiffré faux).

À confirmer par Anaël : aucune décision de fond.

Suite pour l'orchestrateur (payante, hors story) : `python eval/outils/verifier_jeu_croise.py verifier --version dev2 --juges deepseek,glm` (320 appels, environ 1,7 $, pire cas environ 4 $ avec une relance par appel), puis `python eval/outils/construire_jeu.py assembler --version dev2` (retire les rejetés), puis gel `relu-llm` (non fait cette nuit).

## Revue

- low, second avis, corrigé : `disjonction` sans `--reference` en worktree affichait « disjoint » sans lire `data/train` ni `runs/data-seed` ; elle affiche désormais INCOMPLET et sort en 1 si aucun des deux n'est lu (test).
- low, second avis, corrigé : `eval/calibrage/echantillon-calibrage.jsonl` entre dans la référence de disjonction (seed le protège déjà) (test).
- low, second avis, corrigé : CR-601, « la date retenue par Mme Royer » (absente) devient « la date retenue en séance (confirmée par M. Lebrun) » dans les notes et le brouillon ; piège et consigne CR inchangés ; `nb_mots` 221 -> 224. Le SHA d'assemblage de dev2 change (le jeu n'est pas gelé) ; les verdicts du second passage restent valables (même fait, attribution levée).
- low, second avis, rejeté : dates CR du corps sans année ; en-têtes datés avec année, contrôle OK, laissé tel quel.
- Note : 3 tests de `test_jeu_dev.py` (`ouvrir_juges`) échouent dans ce worktree sur `import anthropic` absent du venv (environnement, sans rapport avec le diff) ; à revérifier depuis le venv principal.
