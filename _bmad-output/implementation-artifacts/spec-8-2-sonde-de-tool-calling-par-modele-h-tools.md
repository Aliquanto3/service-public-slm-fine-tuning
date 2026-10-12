---
title: 'Story 8.2 — Sonde de tool calling par modèle (H-TOOLS)'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '7cea13f6b14e9ff5bc652f3eb6147801e5d7a5f6'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: ['oversized']
deferred:
  - summary: >-
      SmolLM3 3B n'a aucun protocole d'outils valide (0/5 en natif comme en json-generique) ; protocole_outils = natif est inscrit par égalité.
    evidence: |-
      Run runs/eval-sonde/20261012-165530-smollm3-3b-80cc : en natif, les <tool_call> sortent en texte, non analysés par llama-server b11429 --jinja ; en json-generique, réponse en texte. Sa Baseline RD mesurera ce défaut de format. Rien dans la config ne le signale aux runs suivants.
    location: >-
      config/modeles/smollm3-3b.toml
    severity: medium
---

<intent-contract>

## Intent

**Problem:** `protocole_outils = "natif"` est provisoire dans les cinq `config/modeles/<slug>.toml` (8.1). Rien ne vérifie qu'un candidat produit des appels d'outils exploitables par le parseur `--jinja` de `llama-server` b11429, qui réécrit en plus les templates Mistral. La Baseline RD risquerait de mesurer un défaut de format plutôt que le modèle.

**Approach:** `slmsp eval sonde-outils --modele base:<slug>` passe les items RD-001 et RD-002 du calibrage (R-001 et R-002 de H-TOOLS) par le Harnais d'évaluation de la 5.3, d'abord en `natif`. Si ce protocole échoue, la sonde relance en `json-generique`. Elle écrit `runs/eval-sonde/<run_id>/` et recommande un protocole. La story inscrit ensuite à la main le protocole retenu dans les TOML.

## Boundaries & Constraints

**Always:**
- Même voie que la phase génération : `generation.generer_item`, `assemblage.ouvrir_harnais` (injectable en `fabrique`), `sans_reseau()`, `OPTIONS_LLM`, `verrou_gpu` en `cuda`. Le protocole est imposé par `modele.config.model_copy(update={"protocole_outils": p})`, avec un Harnais rouvert par protocole.
- La validité se calcule avec `controles.controle_rd`, sans formule parallèle. Les appels non conformes sont lus dans la trace (`type = "appel-non-conforme"`).
- Les fichiers sont écrits via `Run` (`nouveau_run`, `ajouter_jsonl`, `ecrire_json`, `terminer`), en ajout seul.
- Fixtures de test factices (D1.1) : aucun texte réaliste rédigé.

**Never:** réécrire un TOML versionné depuis le code ; aucune API payante ni réseau ; aucun Juge ni notation ; pas de `--reprendre` (la sonde est courte et se relance).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| natif valide | chaque item : ≥ 1 appel attendu apparié, 0 non conforme | une seule passe `natif` ; recommandé `natif` | code 0 |
| natif invalide | un item sans appel apparié ou avec un appel non conforme | seconde passe `json-generique` ; recommandé `json-generique` s'il est valide | code 0 |
| aucun valide | les deux protocoles échouent | recommandé : meilleur taux (égalité → `natif`), `valide = false`, motif | code 1 |
| item en erreur | exception ou `Erreur` dans le flux | ligne `statut = erreur`, item invalide, run `partiel-erreur` | sonde poursuivie |
| usage | référence invalide, item inconnu, item non RD | message `slmsp : eval sonde-outils : …` | code 2, aucun run |

</intent-contract>

## Code Map

- `src/slmsp/evaluation/generation.py` -- à réutiliser : `generer_item(harnais, jeu, item) -> Generation`, `OPTIONS_LLM`, `GRAINE`, `_selection`, `_entrees`, `_verrou` (motif de verrou), `Fabrique`, `_racine`.
- `src/slmsp/evaluation/assemblage.py` -- `ouvrir_harnais(modele, variante, racine)`, `sans_reseau()`, `PROFIL_RESEAU`, `HarnaisEvaluation.chat_template_sha256 / description / index_version / llamacpp_tag`.
- `src/slmsp/evaluation/modele_ref.py` -- `resoudre(ref, "q4_k_m", racine=)` → `ModeleResolu` (dataclass figée : `dataclasses.replace(modele, config=…)`).
- `src/slmsp/evaluation/controles.py:200` -- `controle_rd(item, generation)` → `appels_attendus`, `appels_valides`, `appariement`. Sur le calibrage (sans `regles`), seul le nom d'outil compte.
- `src/slmsp/inference/client.py:36` -- `PROTOCOLES = ("natif", "json-generique")`. `ServeurLlama.client()` lit `config.protocole_outils` (`serveur.py:575`).
- `src/slmsp/core/items.py` -- `VERSION_CALIBRAGE`, `lire_jeu`, `ItemRD`. Ids du calibrage : `RD-001` (R-001), `RD-002` (R-002), cassettes `eval/calibrage/cassettes/R-00x.json`.
- `src/slmsp/core/artefacts.py:332` -- `nouveau_run(type, slug, config, entrees=, graine=, racine=, **champs)`.
- `src/slmsp/cli/eval.py:377` -- remplacer le stub `sonde-outils` (`_remplacement`, `_non_implementee`) ; le style suit `_generation` / `_usage_run`.
- `tests/evaluation/conftest.py` -- `Fabrique` (enregistre `modele`, donc `modele.config.protocole_outils`), `harnais_factice`, `FakeLlmDeterministe`, `depot_eval`, `modeles`.
- `tests/evaluation/test_generation_reel.py` -- `prerequis()` et `racine_index()`, à réutiliser pour le test réel.
- `tests/evaluation/test_gel.py:743` -- test « sonde-outils non implémentée », à retirer (hors zone, une ligne).

## Tasks & Acceptance

**Execution:**
- `src/slmsp/evaluation/sonde_outils.py` -- `TYPE_RUN = "eval-sonde"`, `FICHIER_SONDE = "sonde.jsonl"`, `FICHIER_RECOMMANDATION = "recommandation.json"`, `ITEMS_SONDE = ("RD-001", "RD-002")`. `evaluer(item, generation, protocole) -> dict` (ligne de sonde). `sonder(modele_ref, *, jeu="calibrage", items=None, variante="cpu", racine=None, fabrique=ouvrir_harnais, rapporter=None) -> RapportSonde` : passe `natif`, puis `json-generique` si `natif` échoue, `recommandation.json`, statut final -- AC1, AC2.
- `src/slmsp/cli/eval.py` -- `eval sonde-outils --modele base:<slug> [--jeu] [--items] [--variante] [--racine]` : une ligne par item, puis le tableau par protocole, le protocole recommandé et le chemin du run ; codes 0, 1 ou 2 -- AC1, AC2.
- `tests/evaluation/test_sonde_outils.py` -- matrice I/O avec un `FakeLlm` qui émet un `AppelNonConforme` en natif et des `AppelOutil` attendus en json ; contenu du run ; CLI ; test réel `lent` + `integration` (Granite, RD-001).
- `tests/evaluation/test_gel.py` -- retirer `sonde-outils` du test « non implémentée ».
- Exécution réelle (arrière-plan, `--racine <principal>`) : Granite 1B et Ministral 3B, puis SmolLM3 et Qwen 4B si chacun prend moins de 10 min. Les runs sont copiés dans `runs/eval-sonde/` du worktree.
- `config/modeles/*.toml` -- `protocole_outils` retenu, avec un commentaire qui cite le run. Un modèle non sondé reste `natif`, marqué « non sondé » -- AC3.

**Acceptance Criteria:**
- Given un candidat, when on lance `eval sonde-outils --modele base:<slug>`, then RD-001 et RD-002 du calibrage passent par le Harnais (Bac à sable, `ModeFixe` connecté, profil `aucun`) en `natif`. `runs/eval-sonde/<run_id>/sonde.jsonl` donne par item les appels produits (nom, arguments ou arguments bruts, conformité) et leur validité au regard des `appels_attendus`.
- Given des appels invalides ou absents en `natif`, when la sonde se termine, then une passe `json-generique` existe dans `sonde.jsonl`. `recommandation.json` désigne le protocole valide et donne, par protocole, les taux et le verdict.
- Given le résultat réel, when la story se termine, then chaque `config/modeles/<slug>.toml` candidat porte le `protocole_outils` retenu, et le choix est consigné dans `## Auto Run Result`.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 12 findings — high 0, medium 1, low 10, false 1, maybe-false 0
- findings:
  - `[low]` `[reject]` (blind) Le départage de `recommander` ne regarde que le taux (non conformes et erreurs ignorés). — Règle fixée par la spec (« meilleur taux, égalité → natif ») ; la changer reviendrait à éditer la spec. Les items du calibrage ont toujours des appels attendus : un taux `None` n'arrive pas.
  - `[low]` `[reject]` (blind) `--jeu v1.0` permettrait de choisir un protocole sur des items du jeu gelé. — Le défaut est `calibrage` (AC1), et `--jeu` figure dans la spec. Le cas suppose un choix explicite de l'opérateur ; un garde-fou ajouterait une branche.
  - `[low]` `[patch]` (blind) `connexions_bloquees` est collecté mais jamais persisté. — Ajouté à `recommandation.json`, avec une assertion de test. Les quatre runs réels, antérieurs au correctif, ne le portent pas.
  - `[low]` `[reject]` (blind) Critère indulgent (nom d'outil seul, un appel par item) ; arrêt après le premier protocole valide. — Comportement voulu par la spec (Design Notes, AC2) ; le changer reviendrait à éditer la spec.
  - `[medium]` `[defer]` (blind) SmolLM3 garde un protocole sans appel valide, et aucun champ lisible par machine ne le signale. — Défaut de format du modèle sous llama.cpp b11429 (`<tool_call>` en texte), révélé par la sonde et non causé par le code. Ce qu'il faut en faire (parseur texte, exclusion RD, champ de config) relève de la 8.3 ou d'Anaël : différé.
  - `[low]` `[reject]` (blind) Ministral 8B « non sondé », sans suivi. — Le 8B est un plafond en évaluation seulement, première coupe de la 8.3 (epic 8) ; le commentaire du TOML le dit.
  - `[low]` `[reject]` (blind) Import des fonctions privées de `generation.py`. — Réutilisation voulue (Code Map) ; les rendre publiques toucherait `generation.py` hors zone. Le risque se limite à une divergence future, détectée par les tests.
  - `[low]` `[reject]` (blind) `run.json` liste les deux protocoles même si seul `natif` a tourné. — `config.protocoles` donne l'ordre des candidats ; les passes réellement faites, avec leur serveur et leur template, sont dans `recommandation.json`. Cosmétique.
  - `[low]` `[reject]` (blind) Tests manquants : cuda et verrou, échec de la seconde passe, taux `None`, code 4 en CLI, ligne `Motif`. — La voie cuda et le verrou reprennent ceux de la génération, déjà testés ; l'interruption hors item est testée ; le taux `None` est impossible sur le calibrage ; le code 4 passe par le `main` commun.
  - `[low]` `[reject]` (blind) La CLI recopie la liste des variantes au lieu d'utiliser `VARIANTES`. — Même motif que `eval run` : l'import paresseux évite de charger `inference.serveur` à l'enregistrement, et `sonder` revalide.
  - `[low]` `[reject]` (blind) `tableau_sonde(bilans: Any)`. — Même convention que `tableau_scores(scores: Any)` (imports paresseux). Cosmétique.
  - `[false]` `[reject]` (blind) Les chiffres des commentaires TOML ne sont pas vérifiables dans le diff. — Recoupés avec les `recommandation.json` des quatre runs : 4/5, 5/5, 0/5 et 0/5, 1/5 et 2/5, tous conformes.

## Design Notes

Le critère de validité d'un protocole est une décision prise seul, la plus simple : chaque item sondé a au moins un appel attendu apparié et aucun appel non conforme. Le taux d'appels valides vaut Σ `appels_valides` ÷ Σ `appels_attendus` (`controle_rd`). Il départage les protocoles quand aucun n'est valide. Ligne de `sonde.jsonl` :
```json
{"protocole": "natif", "item_id": "RD-001", "statut": "ok", "appels_produits": [{"nom": "search_datasets", "arguments": {...}, "conforme": true}], "non_conformes": 0, "appels_attendus": 2, "appels_valides": 1, "appariement": [0, null], "valide": true, "duree_ms": 8123, "generation": {...}}
```

## Verification

**Commands:**
- `uv run pytest tests/evaluation` -- expected : tout passe.
- `uv run pytest`, puis `uv run ruff check` et `uv run ruff format --check` -- expected : vert.
- `uv run slmsp eval sonde-outils --modele base:<slug> --racine <principal>` (avec `SLMSP_VENDOR_DIR` et `SLMSP_MODELS_DIR`, en arrière-plan) -- expected : run `complet` ou `partiel-erreur`, puis protocole recommandé.

## Auto Run Result

Sondes réelles du 2026-10-12 (`--racine` = dépôt principal, variante `cpu`, llama.cpp b11429, items RD-001 et RD-002 du calibrage). Runs copiés dans `runs/eval-sonde/` du worktree.

| Candidat | Run | natif (items / appels appariés / non conformes) | json-generique | Recommandé | Durée | `protocole_outils` retenu |
|---|---|---|---|---|---|---|
| Granite 4.0 1B | `20261012-165007-granite-4.0-1b-0543` | 2/2, 4/5, 0 : valide | non lancé | `natif` (valide) | 76 s | `natif` |
| Ministral 3 3B | `20261012-165214-ministral-3-3b-e1a5` | 2/2, 5/5, 0 : valide | non lancé | `natif` (valide) | 185 s | `natif` |
| SmolLM3 3B | `20261012-165530-smollm3-3b-80cc` | 0/2, 0/5, 0 : invalide | 0/2, 0/5, 0 : invalide | `natif` (égalité, aucun valide, code 1) | 60 s | `natif` |
| Qwen 4B | `20261012-165641-qwen-4b-1940` | 1/2, 1/5, 0 : invalide | 2/2, 2/5, 0 : valide | `json-generique` (valide) | 223 s | `json-generique` |
| Ministral 3 8B | non sondé | — | — | — | — | `natif` (« non sondé ») |

Observations :
- SmolLM3 : en `natif`, les appels sortent en texte (`<tool_call>{…}</tool_call>`) sans être analysés par le parseur `--jinja` de b11429 : c'est le défaut de format visé par H-TOOLS. En `json-generique`, le modèle choisit la branche `content` et répond sans appel. Aucun protocole n'est exploitable en l'état ; `natif` est inscrit par égalité. La Baseline RD de SmolLM3 mesurera ce défaut tant qu'il n'est pas traité.
- Qwen 4B : l'échec `natif` vient de RD-002, où le modèle répond sans tenter d'appel ; RD-001 produit un appel natif bien analysé. Le critère (une décision simple, sur un seul tirage glouton de deux items) bascule donc vers `json-generique` sur un comportement plutôt que sur un défaut de format. À revoir si la Baseline RD de Qwen en `json-generique` déçoit.

Status: done
Blocking condition: aucune

**Résumé.** `slmsp eval sonde-outils --modele base:<slug>` passe RD-001 et RD-002 du calibrage par le Harnais d'évaluation de la 5.3 : Bac à sable, `ModeFixe` connecté, profil `aucun`, décodage glouton. La sonde commence en `natif`, puis passe en `json-generique` si `natif` échoue. Elle écrit `runs/eval-sonde/<run_id>/sonde.jsonl` (appels produits, conformité, appariement `controle_rd`) et `recommandation.json` (bilan par protocole, protocole recommandé, connexions bloquées). Le `protocole_outils` retenu est inscrit à la main dans chaque TOML candidat.

**Fichiers.**
- `src/slmsp/evaluation/sonde_outils.py` (nouveau) : `evaluer`, `recommander`, `sonder`.
- `src/slmsp/cli/eval.py` : sous-commande `eval sonde-outils`, à la place du stub ; codes de sortie 0, 1 et 2.
- `tests/evaluation/test_sonde_outils.py` (nouveau) : 21 tests rapides, plus un test réel `lent` + `integration` (Granite, RD-001).
- `tests/evaluation/test_gel.py` (hors zone, une suppression) : retrait du test « sonde-outils non implémentée ».
- `config/modeles/{granite-4.0-1b,ministral-3-3b,smollm3-3b,qwen-4b,ministral-3-8b}.toml` : `protocole_outils` retenu, avec le run cité.
- `runs/eval-sonde/` : les quatre runs réels, copiés depuis le dépôt principal.

**Revue** (une passe, Blind Hunter seul, mode économe ; 12 constats) :
- 1 corrigé (low) : `connexions_bloquees` persisté dans `recommandation.json`.
- 1 différé (medium) : SmolLM3 n'a aucun protocole valide.
- 10 rejetés avec motif (9 low, 1 false) : voir le Review Triage Log.

Relecture complémentaire recommandée : `false` (aucun high ni medium corrigé).

**Vérification.**
- `uv run pytest` : 2653 passés, 177 sautés. Un seul échec, préexistant et hors zone : `tests/mistral/test_journal.py::test_generation_sans_jeton_refusee[options1]`, dû à `ModuleNotFoundError: mistralai` (extra non installé dans le venv du worktree).
- `tests/evaluation` après le correctif : 212 passés.
- `ruff check` et `ruff format --check` : propres.
- Test réel Granite RD-001 : passé.
- Les chiffres des TOML ont été recoupés avec les `recommandation.json`.

**Décisions prises seul** (à reporter au journal) :
1. Critère de validité d'un protocole : chaque item est `ok`, avec au moins un appel attendu apparié et aucun appel non conforme. Sans protocole valide, le meilleur taux l'emporte, et `natif` en cas d'égalité.
2. Granite et Ministral 3B : `natif`. Qwen 4B : `json-generique`. SmolLM3 : `natif` par égalité (aucun valide). Ministral 8B : non sondé, reste `natif`.
3. Sonde en variante `cpu`, pour ne pas prendre `gpu.lock` ; aucun TOML n'est réécrit par le code.
4. Code 1 si le run est `partiel-erreur`, même quand un protocole est valide.

**Risques résiduels.**
- Réécriture des templates Mistral par b11429 : sans effet visible sur le 3B (5/5 en natif). Le 8B n'est pas sondé.
- SmolLM3 : défaut de format non traité (différé).
- Qwen : la bascule tient à un seul tirage glouton sur deux items, et à un comportement (RD-002 sans appel) plutôt qu'à un défaut de format.
- Les quatre runs réels ont été produits avant le correctif `connexions_bloquees` : ce champ est absent de leur `recommandation.json`.
