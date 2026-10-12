---
title: 'Story 7.2 — Items Question (60) et Non-régression (30)'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: 'b14abcfb3b5dac0f442c69199a06f1a2942484c9'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/eval/SPEC-jeu-evaluation.md'
  - '{project-root}/eval/grille-juge-v1.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-7-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Aucun item Question ne couvre les marchés publics, sous-domaine « collectivités » cité par SPEC §2.
    evidence: |-
      Les fiches « marchés publics » sont sur entreprendre.service-public.gouv.fr, alors que l'AC 2 de la story impose des sources_attendues sur www.service-public.gouv.fr. Les 9 items « collectivites » couvrent élus locaux, élections, actes, associations et subventions. À trancher par Anaël (accepter l'hôte entreprendre pour v1.1, ou garder l'écart).
    location: >-
      eval/construction/v1.0/Q.jsonl (thème collectivites)
    severity: medium
  - summary: >-
      Les montants et dates des items dépendent de l'état du droit au 2026-10-12, sans ancre de date dans l'entrée.
    evidence: |-
      16 items Q contiennent des montants revalorisés chaque année ; Q-025 et Q-058 dépendent de fenêtres de 2026. Après le gel, un modèle aux connaissances plus récentes, ou un harnais qui injecte la date du jour, pourrait diverger de la référence. À décider au gel (7.6) ou en v1.1 : ancre « nous sommes le … » dans l'entrée, ou champ de validité.
    location: >-
      eval/construction/v1.0/Q.jsonl
    severity: medium
  - summary: >-
      Q-042 : plafond de l'indemnité de rupture conventionnelle (1/24e par année d'ancienneté selon la fiche F31094) à recouper avec le décret.
    evidence: |-
      Un relecteur se souvient d'un plafond « un douzième » (décret n° 2019-1596). La fiche en parquet et la page en ligne (GET du 2026-10-12) disent toutes deux « 24e ». Pour trancher : lire le décret sur Légifrance (inaccessible en lecture automatique, HTTP 403).
    location: >-
      eval/construction/v1.0/Q.jsonl (Q-042)
    severity: medium (unverified)
  - summary: >-
      Les items « sans réponse » sont prouvés sur l'Index local v1 (service-public + catalogue) ; l'extension LEGI pourrait y répondre.
    evidence: |-
      Le mariage posthume (Q-027) relève du code civil, présent dans LEGI. Si l'extension LEGI de l'Index local est activée (D4), refaire les preuves d'absence sur LEGI ou lier `sans_reponse` à la version de l'index.
    location: >-
      eval/construction/v1.0/Q.jsonl (items sans_reponse)
    severity: low
  - summary: >-
      `assembler` n'échoue pas quand un item n'a pas de verdict : il le signale seulement.
    evidence: |-
      Comportement de l'outil livré en 7.1 (`cmd_assembler`, items sans verdict retenus et listés). Ici, « Items sans verdict : 0 » a été contrôlé à la main. À durcir dans l'outil, ou à contrôler au gel (7.6).
    location: >-
      eval/outils/construire_jeu.py (cmd_assembler)
    severity: low
  - summary: >-
      La validation stricte `slmsp eval gel --verifier-seulement` n'a pas pu être lancée (story 5.1 non faite).
    evidence: |-
      Le contrôle de structure de l'outil en tient lieu, comme le prévoit la stratégie de test de la story. À relancer en 7.6.
    location: >-
      eval/construction/v1.0/
    severity: low
---

<intent-contract>

## Intent

**Problem:** Le Jeu d'évaluation v1.0 n'a encore aucun item. La Tâche Question (60) mesure l'exactitude sourcée, la Non-régression (30) le français général ; sans eux, ni Baseline ni gel.

**Approach:** Rédiger les brouillons `eval/construction/v1.0/Q.jsonl` et `NR.jsonl` à partir des instantanés réels (`<dépôt principal>/data/raw/eval-sources/`, parquet service-public rév. `29f236f8a5`, corpus de questions AgentPublic), puis les faire relire par un vérificateur indépendant qui écrit `verification/Q.jsonl` et `verification/NR.jsonl`. Les rejetés sont corrigés ou remplacés puis revérifiés.

## Boundaries & Constraints

**Always:**
- Format : SPEC §3 complétée par le calibrage (D-nuit-A1-19) et le README de `eval/construction/v1.0/`. Champs communs : `id`, `tache`, `difficulte`, `theme`, `entree` (texte), `parametres` (`{}`), `provenance[]` avec `consulte_le`, `licence_source`, `fictif`, `version_item = 1`.
- Q : `reponse_reference`, 3 à 5 `elements_cles`, `sources_attendues` uniquement sur `www.service-public.gouv.fr`, `sans_reponse` (booléen), `orientation_attendue` si sans réponse, `mention_obligatoire` « Ne vaut pas avis juridique ». Chaque fait vient d'une fiche lue dans le parquet ; la provenance cite la fiche, les chunks et un `extrait` verbatim.
- Q sans réponse : `sources_attendues = []` et `verification_absence` (motifs regex, résultat, date), comme Q-002 du calibrage.
- Q issu d'une amorce : `amorce_usager` verbatim et une provenance qui cite le corpus (`sp_questions_corpus` ou `assistant_ia_questions_corpus`) avec le numéro de `ligne`.
- NR : `reponse_reference` et/ou `criteres`, `sous_type` ∈ {`question`, `consigne`}, `theme = "non-classe"`. Faits de culture générale tirés d'une fiche service-public ; raisonnement vérifiable par calcul ; consignes de rédaction `fictif: true`.
- Vérificateur : sous-agent indépendant, sans le contexte du rédacteur ; verdicts au format du README (`accepte` / `rejete` + motif SPEC §5.2), en ajout seul.

**Never:**
- Toucher `src/`, `config/`, `eval/jeu/`, `eval/calibrage/`, les documents de décision.
- Reprendre un item du calibrage (D-nuit-A2-3) ni un sujet trop proche de Q-001 (CNI perdue) ou Q-002 (PPG).
- Écrire un fait de mémoire ; citer Légifrance comme source attendue.
- Réseau avant 08h30 ; après, seulement des GET légers vers les hôtes autorisés.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Composition | Brouillons complets | `composition` : Q 20/25/15, 8 sans réponse, ≥ 30 amorces réelles ; NR 10/10/10 ; aucune anomalie | Écart corrigé avant la fin |
| Rejet | Verdict `rejete` | Item corrigé sous le même `id` ou remplacé au numéro libre suivant, puis revérifié | Taux de rejet consigné |
| Sans réponse | Amorce hors corpus | `sans_reponse: true`, `orientation_attendue`, preuve d'absence | — |

</intent-contract>

## Code Map

- `eval/outils/construire_jeu.py` -- `anomalies_item` (l. 1005) : contrôles de structure Q (3 à 5 `elements_cles`, hôtes de `sources_attendues`, `amorce_reelle` l. 945) et NR (`reponse_reference|criteres`) ; `composition`, `rejets`.
- `eval/construction/v1.0/README.md` -- format des brouillons et des verdicts.
- `eval/calibrage/echantillon-calibrage.jsonl` -- Q-001, Q-002, NR-001, NR-002 : référence de format.
- `<dépôt principal>/data/raw/eval-sources/hf/AgentPublic/service-public/latest/train/0000.parquet` -- 3 569 fiches (`doc_id`, `chunk_index`, `title`, `url`, `text`, `context`).
- `<dépôt principal>/data/raw/eval-sources/hf/assistant_ia_questions.xlsx` -- 46 amorces (colonne `query`, lignes 2 à 47).
- `<dépôt principal>/data/raw/eval-sources/hf/AgentPublic/sp_questions_corpus/gpt_corpus-20kq&A.xlsx` -- rév. `495a22cf7b`, 20 692 questions (feuille `results`, colonne `question`).

## Tasks & Acceptance

**Execution:**
- `eval/construction/v1.0/Q.jsonl` -- 60 items. Thèmes : social-autonomie 18, état civil 9, travail-emploi 9, collectivités 9, famille-éducation-santé 9, fiscalité locale 6.
- `eval/construction/v1.0/NR.jsonl` -- 30 items, 10/10/10 : 15 `question` (culture générale civique sourcée, raisonnement), 15 `consigne` (courriel, reformulation, liste).
- `eval/construction/v1.0/verification/Q.jsonl`, `verification/NR.jsonl` -- verdicts du vérificateur indépendant ; remplacements revérifiés.

**Acceptance Criteria:**
- Given les brouillons, when on lance `construire_jeu.py composition`, then Q et NR sont aux cibles de SPEC §2, sans anomalie de structure.
- Given `construire_jeu.py rejets`, when on le lance, then le taux de rejet par Tâche est affiché, et chaque item a un dernier verdict `accepte`.
- Given `construire_jeu.py assembler --version v1.0` lancé dans un dossier temporaire, when il se termine, then il réussit sans doublon ni item non vérifié.

## Design Notes

- Champs ajoutés au-delà de SPEC §3 (lisibles, ignorés par le banc) : `amorce_usager`, `mention_obligatoire`, `verification_absence`, `provenance[].extrait`, `provenance[].chunks`, `provenance[].ligne`, NR `sous_type`.
- `regles` (D-nuit-A1-19) ne concerne que les items RD : sans objet ici.
- Les collectivités sont couvertes par les fiches `www` (élus locaux, élections, actes et décisions, associations et subventions). Les fiches « marchés publics » sont sur `entreprendre.service-public.gouv.fr`, exclu par l'AC 2 de la story : écart thématique consigné.

## Lots d'exécution

La rédaction est découpée en lots confiés à des sous-agents distincts. Chacun écrit **seulement** son fichier de lot `<SCRATCH>/lots/<LOT>.jsonl` ; l'agent de story fusionne les lots dans `Q.jsonl` et `NR.jsonl`, puis lance le vérificateur.

`<SCRATCH>` = `C:\Users\UTILIS~1\AppData\Local\Temp\claude\C--Users-Utilisateur-Documents-GitHub-service-public-slm-fine-tuning\2b525399-9658-4abc-ae6d-dabcdbffc874\scratchpad`. Outils (lancés par `uv run --offline --no-project --python 3.12 --with duckdb python -I <script> …`) :
- `<SCRATCH>/fiches.py F10009 F12006 …` exporte le texte des fiches dans `<SCRATCH>/fiches/<ID>.txt` (chunks numérotés), à lire ensuite avec l'outil Read.
- `<SCRATCH>/recherche.py "motif" …` : recherche regex insensible à la casse dans le parquet (preuve d'absence, choix des fiches).
- `<SCRATCH>/titres.txt` : `doc_id | url | titre | nb chunks | surtitre` des 3 569 fiches (UTF-8).
- Amorces : `<SCRATCH>/assistant_ia.jsonl` (`ligne`, `query`, `output_true`) et `<SCRATCH>/sp_questions.jsonl` (20 692 lignes : `ligne` = numéro de ligne Excel, `question`, `fiches_contexte` = fiches récupérées par le RAG d'origine, simple indice). Chercher dans ces fichiers avec l'outil Grep. `output_true` (et les réponses GPT du corpus) n'est **jamais** une source de fait.

| Lot | Identifiants | Thème (slug) | facile / moyen / difficile | Sans réponse | Amorces réelles (min.) | Lignes `assistant_ia` réservées |
|---|---|---|---|---|---|---|
| QA | Q-001 à Q-018 | `social-autonomie` | 6 / 8 / 4 | 2 | 10 | 2, 4, 5 |
| QB | Q-019 à Q-027 ; Q-028 à Q-033 | `etat-civil-papiers` (9 : 3/4/2, 1 SR) ; `fiscalite-locale` (6 : 2/2/2, 1 SR) | 5 / 6 / 4 | 2 | 8 | 11, 12 |
| QC | Q-034 à Q-042 ; Q-043 à Q-051 | `travail-emploi` (9 : 3/4/2, 1 SR) ; `collectivites` (9 : 3/4/2, 2 SR) | 6 / 8 / 4 | 3 | 9 | 3, 7, 8, 13, 14, 16, 20, 31 |
| QD | Q-052 à Q-060 | `famille-education-sante` | 3 / 3 / 3 | 1 | 5 | 19, 23, 28, 29 |
| NR | NR-001 à NR-030 | `non-classe` | 10 / 10 / 10 (questions 5/5/5, consignes 5/5/5) | — | — | aucune |

Règles communes aux lots Q :
- Une fiche différente par item, sauf deux questions vraiment distinctes ; pas de quasi-doublon entre items. Ne pas réutiliser F1344 (calibrage Q-001), ni le sujet « PPG » (Q-002), ni les fiches déjà prises par le lot NR : F1940, F1944, F780, F1540, F21088, F24496.
- Les lignes `assistant_ia` non réservées sont interdites. Dans `sp_questions.jsonl`, ne prendre que des lignes du thème du lot.
- L'`entree` reformule l'amorce comme un agent public la poserait (cas d'usager, contexte de guichet). Difficulté : facile = un fait d'une fiche ; moyen = plusieurs conditions ou un cas particulier ; difficile = combinaison de cas, de seuils ou de deux fiches.
- Sans réponse : la question porte sur un sujet que **aucune** fiche ne traite. Le prouver avec `recherche.py` (au moins deux motifs, plus un contrôle positif), et l'écrire dans `verification_absence`. `orientation_attendue` désigne un interlocuteur plausible sans inventer de fait.
- Chaque `elements_cles` est vérifiable mot pour mot ou presque dans un `extrait` de la provenance. Les montants et dates sont recopiés tels quels.

Gabarit Q (une ligne JSON, UTF-8, `ensure_ascii=False`) :

```json
{"id": "Q-001", "tache": "Question", "difficulte": "facile", "theme": "social-autonomie",
 "entree": "…question de l'agent…", "amorce_usager": "…texte verbatim de la ligne…",
 "parametres": {}, "reponse_reference": "… Ne vaut pas avis juridique.",
 "elements_cles": ["…", "…", "…"], "sources_attendues": ["https://www.service-public.gouv.fr/particuliers/vosdroits/F10009"],
 "sans_reponse": false, "mention_obligatoire": "Ne vaut pas avis juridique",
 "provenance": [
  {"source": "AgentPublic/sp_questions_corpus (gpt_corpus-20kq&A.xlsx)", "url": "https://huggingface.co/datasets/AgentPublic/sp_questions_corpus/resolve/495a22cf7b572621a85d2f3e97783b2f4189c47e/gpt_corpus-20kq%26A.xlsx", "ligne": 1234, "role": "amorce de question usager, reformulée par un agent", "consulte_le": "2026-10-12"},
  {"source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F10009 « Allocation personnalisée d'autonomie (Apa) »", "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F10009", "chunks": [3, 4], "extrait": "…citation verbatim…", "role": "fiche de référence", "consulte_le": "2026-10-12"}],
 "licence_source": "Amorce : MIT (carte du dataset). Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false, "version_item": 1}
```

Pour `assistant_ia` : `"source": "AgentPublic/assistant_ia_questions_corpus (evaluation_qo_assistant_ia_v1.xlsx)"`, `"url": "https://huggingface.co/datasets/AgentPublic/assistant_ia_questions_corpus/resolve/main/evaluation_qo_assistant_ia_v1.xlsx"`. Sans amorce : pas de champ `amorce_usager` ni d'entrée corpus. Sans réponse : `"sources_attendues": []`, `"sans_reponse": true`, `"orientation_attendue": "…"`, `"verification_absence": {"corpus": "AgentPublic/service-public (rév. 29f236f8a5)", "motifs_recherches_regex_insensible_casse": [...], "resultat": "…", "date": "2026-10-12"}`, et une provenance « Recherche plein texte dans le parquet MediaTech service-public » (`url` du parquet HF, `role` « preuve d'absence de source »).

Gabarit NR :

```json
{"id": "NR-001", "tache": "Non-régression", "difficulte": "facile", "theme": "non-classe", "sous_type": "question",
 "entree": "…", "parametres": {}, "reponse_reference": "…", "criteres": ["…"],
 "provenance": [{"source": "Question rédigée pour l'évaluation (raisonnement, vérifiable par calcul)", "consulte_le": "2026-10-12"}],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true, "version_item": 1}
```

- Questions NR (15) : environ 9 de raisonnement (calcul, logique, durées, pourcentages, ordre), dont la réponse se recalcule ; environ 6 de culture générale civique tirée d'une fiche service-public (`fictif: false`, provenance avec `url`, `chunks` et `extrait`), sans reprendre un sujet de Question (éviter F1952, F1958). Réponse unique et non ambiguë.
- Consignes NR (15) : courriel court, reformulation (registre, simplification), liste ou plan, en contexte d'administration ; `criteres` vérifiables (forme, contenu à conserver, interdits comme l'ajout de faits). Pas de reprise de NR-002 du calibrage.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts : 37 constats ; high 0, medium 9, low 24, false 3, maybe-false 1
- constats :
  - **Intent Alignment (8)**
    - `medium` `defer` Pas d'item sur les marchés publics (SPEC §2). Les fiches sont sur `entreprendre`, que l'AC 2 exclut. Reporté pour arbitrage par Anaël.
    - `low` `reject` NR-011 (QPC) et NR-012 (jours fériés FP) sont proches du domaine. Ce sont des faits civiques sourcés, faute de culture générale « de mémoire » (SPEC §1.3) ; ils ne recoupent aucun item Q.
    - `low` `reject` Le motif `autre` est hors des quatre cas de SPEC §5.2. Le README et l'outil 7.1 le prévoient pour les cas non couverts (faux « sans réponse », calcul de fiche erroné).
    - `false` `reject` « Exactitude vérifiée seulement par le vérificateur ». SPEC §5.2 prévoit exactement ce mécanisme, et la couche Verification Gap a refait tous les contrôles (288 extraits, 50 amorces, URL) sans écart.
    - `low` `defer` `slmsp eval gel --verifier-seulement` n'a pas été exercé (story 5.1 non faite). Reporté à 7.6.
    - `low` `reject` La provenance suit le calibrage (`source`, `role`) et non l'exemple de SPEC §3 (`type`). D6 impose le format du calibrage, et l'adaptation à la lecture est prévue par D-nuit-A1-19.
    - `false` `reject` « Pas de `## Auto Run Result`, statut `in-review` ». Ce sont les étapes de finalisation, faites après la revue.
    - `low` `reject` Les fichiers comptent 61 et 32 lignes, contre 60 et 30. Convention du README : un item rejeté reste dans le brouillon, et `composition` comme `assembler` l'excluent.
  - **Verification Gap (3)**
    - `low` `reject` L'AC 2 dit « chaque item a un dernier verdict `accepte` », alors que les remplacés gardent `rejete`. Le correctif consisterait à éditer la spec.
    - `low` `patch` Le titre de référence de NR-032 est à la limite de 8 mots. Raccourci à « Coupure d'eau mardi 9 juin » (5 mots), puis revérifié.
    - `medium` `patch` Les preuves d'absence sont fragiles (Q-039). Elles ont été refaites par un vérificateur sur les textes, les titres et le catalogue ; voir EC1.
  - **Blind Hunter (14)**
    - `low` `reject` AC 2 : même constat que la couche Verification Gap (le correctif édite la spec).
    - `low` `defer` `assembler` ne bloque pas les items sans verdict. C'est un comportement de l'outil 7.1, et le compte « Items sans verdict : 0 » a été contrôlé. Reporté.
    - `false` `reject` « Résultats non consignés ». Ils sont consignés dans `## Auto Run Result` à la finalisation, et `rejets` les recalcule.
    - `low` `reject` Les outils du brouillon sont restés dans le dossier temporaire. Les items sont autoportants : révision du parquet, chunks, extraits verbatim, motifs regex, lignes de corpus. L'outil `fiche` est versionné. Versionner les scripts ajouterait du code et des tests pour un usage ponctuel.
    - `low` `patch` URL non épinglées. 21 URL corrigées : `assistant_ia` sur la révision `62cef57af7` (SHA identique à la copie du calibrage), et le parquet sur `29f236f8a5` au lieu de `refs/convert/parquet`.
    - `low` `patch` Notation incohérente des « sans réponse ». L'élément « présentés comme non sourcés » a été ajouté partout (gabarit de Q-002 du calibrage).
    - `medium` `patch` La règle de preuve d'absence est trop faible. Les 8 « sans réponse » ont été refaits sur textes, titres et catalogue. Q-018, Q-033 et Q-061 ont été rejetés comme faux « sans réponse », puis leurs remplaçants Q-064 (Transco, F13516) et Q-065 (clause Molière, F1642). Les remplaçants retenus sont Q-062, Q-063 et Q-066, chacun accepté après une preuve renforcée sur les deux corpus.
    - `medium` `patch` Réserves des vérificateurs non appliquées. Faits de la fiche ajoutés à Q-003, Q-025 et Q-030, puis revérifiés. Pour Q-006, la réserve est écartée : l'échéancier et la résiliation ne figurent dans le parquet que pour le cas Île-de-France.
    - `medium` `defer` Pas d'ancre de date pour les montants annuels. La décision touche tout le jeu (7.6 ou v1.1).
    - `maybe-false` `defer` Q-042 : 1/24e (fiche) ou 1/12e (souvenir du relecteur, décret 2019-1596). La fiche et la page en ligne disent 24e ; pour trancher, il faut lire le décret sur Légifrance.
    - `medium` `patch` Les consignes NR ne mesuraient pas l'orthographe. Le critère « Orthographe, grammaire et ponctuation correctes » a été ajouté aux 15 consignes retenues, puis revérifié.
    - `low` `patch` Pas de convention de comptage des longueurs. Précisions ajoutées à NR-016 (lignes hors formules) et NR-029 (corps avant la formule de politesse) ; NR-032 raccourci.
    - `low` `patch` NR-031 introduisait un seuil absent de la consigne. La référence a été réécrite.
    - `low` `patch` Q-057 changeait de registre et demandait des sources. L'entrée a été réécrite côté agent.
  - **Edge Case Hunter (12)**
    - `medium` `patch` Les preuves d'absence ignoraient le catalogue data.gouv, alors que l'Index local v1 le contient. Ajout de `controle_catalogue_data_gouv` sur tous les « sans réponse ». Rejets et remplacements : voir Blind Hunter.
    - `low` `defer` Extension LEGI (code civil, CASF) : les « sans réponse » sont prouvés sur l'index v1. Reporté.
    - `low` `patch` URL flottante du parquet : même cause que le constat Blind Hunter sur les URL ; corrigé.
    - `medium` `patch` Réserves non appliquées : même cause que le constat Blind Hunter ; corrigé.
    - `low` `patch` Le critère de NR-013 acceptait 93,33 %. Il exige maintenant 93,3 %, l'arrondi demandé.
    - `low` `patch` Comptage des lignes de NR-016 et NR-029 : même cause que le constat Blind Hunter ; corrigé.
    - `low` `patch` La référence de NR-027 déformait le délai (« envoyez avant » au lieu de « doit parvenir au plus tard »). Réécrite.
    - `medium` `defer` Fenêtres de dates de Q-025 et Q-058 : même cause que le constat Blind Hunter sur l'ancre de date ; reporté.
    - `low` `patch` URL `assistant_ia` sur `main` : même cause que le constat Blind Hunter ; corrigé.
    - `low` `reject` AC 2 : même constat que la couche Verification Gap.
    - `low` `patch` Preuves d'absence flottantes : même cause que le constat Blind Hunter ; corrigé.
    - `low` `reject` 61 lignes dans Q.jsonl : convention du README (voir Intent Alignment).

## Verification

**Commands:**
- `uv run --offline --no-project --python 3.12 --with duckdb --with openpyxl python -I eval/outils/construire_jeu.py composition` -- expected: cibles Q et NR atteintes, aucune anomalie.
- `uv run --offline --no-project --python 3.12 --with duckdb --with openpyxl python -I eval/outils/construire_jeu.py rejets` -- expected: taux de rejet Q et NR.
- `uv run --offline --no-project --python 3.12 --with pytest --with duckdb pytest tests/eval_outils -q` -- expected: verts (non-régression de l'outil).

## Auto Run Result

Story réalisée par le sous-agent de story 7.2 le 2026-10-12 (bmad-build-auto, mode autonome, sans push).

**Résumé.** 60 items Question et 30 items Non-régression ont été rédigés à partir des instantanés réels, puis vérifiés un par un par des sous-agents indépendants, sans le contexte du rédacteur. Les items rejetés ont été corrigés ou remplacés, puis revérifiés.
- Rédaction en 5 lots parallèles (NR, QA, QB, QC, QD), à partir du parquet service-public (rév. `29f236f8a5`) et des corpus `sp_questions_corpus` (rév. `495a22cf7b`) et `assistant_ia_questions_corpus` (rév. `62cef57af7`).
- Pour chaque fait : fiche, chunks et extrait verbatim ; amorces citées avec leur numéro de ligne.
- « Sans réponse » : preuve d'absence sur les deux corpus de l'Index local v1 (fiches service-public et catalogue data.gouv).

**Fichiers.**
- `eval/construction/v1.0/Q.jsonl` : 66 lignes, dont 60 items retenus et 6 remplacés (Q-018, Q-033, Q-039, Q-061, Q-064, Q-065), gardés en `rejete` selon la convention du README.
- `eval/construction/v1.0/NR.jsonl` : 32 lignes, dont 30 retenues ; NR-025 et NR-030 ont été remplacés.
- `eval/construction/v1.0/verification/Q.jsonl` (85 verdicts) et `verification/NR.jsonl` (50 verdicts), en ajout seul, lignes recopiées telles quelles depuis la sortie des vérificateurs.
- Le présent fichier de story.

**Composition** (`composition`) :
- Q : 60 items (20/25/15), dont 8 sans réponse, tous avec `orientation_attendue` (Q-014, Q-027, Q-048, Q-051, Q-057, Q-062, Q-063, Q-066).
- 49 amorces réelles, soit 82 % (cible : 50 %).
- Thèmes : 18/9/9/9/9/6, conformes à SPEC §2.
- NR : 30 items (10/10/10), dont 15 questions (9 de raisonnement, 6 de culture civique sourcée) et 15 consignes. Aucune anomalie de structure.

**Taux de rejet** (`rejets`, rejets ÷ verdicts) :
- Q : 11 rejets sur 85 verdicts (12,9 %) ; NR : 3 sur 50 (6,0 %) ; total : 14 sur 135 (10,4 %).
- Par motif : `ambigu` 7, `autre` 5 (faux « sans réponse », calcul erroné d'une fiche), `doublon_thematique` 2.
- Au premier passage, avant la revue : 6 rejets sur 60 pour Q (10 %), 3 sur 30 pour NR (10 %).

**Revue** (4 couches, 37 constats : high 0, medium 9, low 24, false 3, maybe-false 1) :
- Correctifs : URL épinglées ; réserves des vérificateurs appliquées ; notation des « sans réponse » harmonisée ; preuve d'absence étendue au catalogue, avec 4 faux « sans réponse » détectés et remplacés ; critère d'orthographe ajouté aux consignes NR ; conventions de comptage précisées ; NR-013, NR-027, NR-031, NR-032 et Q-057 corrigés.
- Reportés (frontmatter `deferred`) : marchés publics, ancre de date, Q-042, extension LEGI, `assembler` non bloquant, `eval gel --verifier-seulement`.
- Rejetés : 12, motifs dans le journal de triage.
- Constats corrigés par niveau : 3 entrées medium (réserves, preuves d'absence, orthographe NR) et 7 entrées low.

**Revue de suivi recommandée : `true`.** Trois entrées medium ont été corrigées. Les dernières corrections (Q-057 et ses éléments, critères NR ajoutés) n'ont été relues que par un vérificateur à chaque fois. Le risque principal reste un faux « sans réponse » non détecté : 4 des 12 sujets proposés ont été rejetés au fil des passes.

**Vérifications :**
- `composition` : cibles atteintes, aucune anomalie, aucun item sans verdict.
- `rejets` : voir ci-dessus.
- `assembler --version v1.0` sur une copie temporaire : 90 items écrits, 8 exclus, code 0.
- `pytest tests/eval_outils` : 100 passed.
- `ruff check eval/outils tests/eval_outils` : OK.
- `slmsp eval gel --verifier-seulement` : non disponible (story 5.1 non faite).

**Décisions prises seul** (règle « la plus simple et la plus réversible ») :
- Rédaction par lots parallèles confiés à des sous-agents.
- NR : thème `non-classe` (valeur par défaut du spine) et champ `sous_type` ∈ {`question`, `consigne`} pour rendre visible la répartition moitié-moitié.
- La culture générale NR est tirée de fiches service-public, et non écrite de mémoire.
- Q-013 : l'exemple chiffré de F21615, faux, n'est pas demandé.
- Un « sans réponse » doit être absent des fiches **et** du catalogue data.gouv, puisque l'Index local v1 contient les deux.
- `regles` (D-nuit-A1-19) est sans objet : il concerne les items RD.
- Le contexte de l'epic 7 a été jugé valide malgré les dates de fichier : elles viennent de la création du worktree.

**Écarts à la SPEC et risques résiduels :**
- Aucun item sur les marchés publics : les fiches sont sur `entreprendre`, que l'AC 2 exclut. Point à trancher par Anaël.
- Les montants annuels et les dates de 2026 ne portent pas d'ancre de date.
- Q-042 (plafond 1/24e) est à recouper avec le décret.
- Les « sans réponse » sont prouvés sur l'index v1 seulement, pas sur LEGI.
- Quelques réserves mineures restent dans les `detail` des verdicts (Q-006, Q-014, Q-062, NR-016, NR-026, NR-027).
- La validation stricte par `slmsp eval gel` reste à faire en 7.6.
