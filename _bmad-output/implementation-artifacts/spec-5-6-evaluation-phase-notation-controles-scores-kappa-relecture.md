---
title: "Story 5.6 — Évaluation, phase notation : contrôles automatiques, Scores de Tâche, kappa et relecture"
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: 'b22626fca4fb4aa59e7f8beda1da85f5188ec8aa'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** Le banc sait générer (5.3) et juger (5.4, 5.5), mais rien ne transforme une génération en Scores de Tâche : ni contrôles automatiques (URL, appels RD, fautes CO, emplacements CT, longueur RE, Kandel-Moles LC), ni formules de la grille, ni kappa entre juges, ni export de relecture.

**Approach:** Un run `eval-notation` (parent : le run `eval-generation`) relit `generations.jsonl`, calcule les contrôles (`evaluation.controles`, fonctions pures), envoie au Juge principal les Tâches jugées (RD seulement en litige, CO jamais), au second juge l'échantillon du manifeste, puis applique les formules de la grille (`evaluation.scores`, seule implémentation) et écrit `verdicts.jsonl`, `controles.jsonl`, `scores.json` (déterministe) et `relecture.md`.

## Boundaries & Constraints

**Always:**
- Le Juge ne calcule aucun score ; toutes les formules sont dans `evaluation/scores.py`.
- Manifeste revérifié avant tout appel (`verifier_manifeste`, code 4) ; `calibrage` admis sans manifeste (échantillons tirés par `gel.tirer_echantillons(items, GRAINE)`, `jeu_statut="calibrage"`).
- `scores.json` = `json_canonique(Scores) + LF`, sans run_id de notation, horodatage, `depuis_cache` ni coût de la session : coût du Juge = somme de `cache.cumul_appels(cle)` des clés retenues (identique à cache plein). Scores arrondis à 4 décimales, coûts à 6.
- Juges injectés (`juger(demandes)` principal ; `juger(demandes, echantillon)` second) ; `BudgetEpuise` → items `non-juge`, run `partiel-budget`, kappa sur l'effectif disponible.
- `slmsp.evaluation.controles` et `scores` n'importent ni `anthropic` ni `mistralai` ; `notation.py` n'importe `slmsp.judge.claude` / `second` / `mistral` que dans la fonction d'assemblage des juges réels.
- Tests sans aucun appel payant (juges factices, cache réel dans `tmp_path`).

**Never:** pas de modification de `eval/`, de la grille, de la SPEC ni de `decisions.md` ; pas de `--reprendre` pour la notation (relancer suffit, le cache évite tout double paiement) ; pas de comparaison par paires.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Nominal | génération complète 8 Tâches | run `eval-notation` `complet`, parent = génération, 4 fichiers | — |
| Génération incomplète | run de génération pas `complet` ni `partiel-erreur` | refus | `SlmspError`, aucun run créé |
| Item en erreur | ligne `statut="erreur"` | exclu des scores, compté `en_erreur`, non jugé ; run `partiel-erreur` | — |
| RD sans appel attendu | `appels_attendus` vide/None | exclu du dénominateur « appel valide » | — |
| RD litige | titre du jeu présent, ni id ni URL | envoyé au Juge, `libelle_correct` décide « réponse exacte » | verdict absent → exclu de la composante |
| Verdict invalide | 2 sorties non conformes | exclu du score, compté `invalides` | — |
| Budget épuisé | `budget_epuise=True` | `non_juges`, run `partiel-budget` | — |
| Cache plein | même génération relancée | zéro appel payant, `scores.json` identique à l'octet | — |
| Relecture validée | `relecture-validee.json` daté dans le run | `charger_scores` → `verdicts_relus=True` | fichier sans date valide → `False` |

</intent-contract>

## Code Map

- `src/slmsp/evaluation/generation.py` -- `TYPE_RUN`, `FICHIER_GENERATIONS`, `GRAINE`, `_racine`, `_verifier_jeu`, `_selection` : modèles à suivre. `core/artefacts.py` : `nouveau_run(type, slug, config, parents=, entrees=, graine=, racine=, **champs)`, `ouvrir_run`, `Run.ecrire/ajouter_jsonl/lire_jsonl/terminer/statut_courant` (le `run.json` reste `en_cours`, lire `statut_courant()`). `core/schemas/run.py` : `Statut`.
- `src/slmsp/core/schemas/generation.py` -- `Generation`, `SortieCanonique` (texte, appels_outils[nom, arguments], sources[Source]), `trace` (dicts `vers_dict` ; types `resultat-outil`, `fin` avec `urls_inventees`).
- `src/slmsp/core/items.py` -- `ItemQ…ItemNR` (champs l.277-411), `RegleArgument`/`ReglesAppel`/`AppelAttendu` (l.166-202), `lire_jeu`, `textes_entree(item)`, `VERSION_CALIBRAGE`.
- `src/slmsp/evaluation/gel.py` -- `verifier_manifeste(version, racine) -> ManifesteJeu` (l.492), `tirer_echantillons(items, graine)` (l.319), `sha256_lf`. `evaluation/config.py` : `TACHES_JUGEES`, `chemin_manifeste`.
- `src/slmsp/judge/claude.py` -- `DemandeJugement(item, sortie)`, `ResultatJugement(item_id, cle, statut, verdict, …, motif)`, `RapportJugement(resultats, budget_epuise, cout_total_eur)`, `JugeClaude(config, registre, cache, client, grille)`, `fabriquer_client(config)` ; importe `anthropic`. `judge/second.py` : `JugeMistral(config, client, cache, grille).juger(demandes, echantillon)`. `judge/cache.py` : `CacheVerdicts(chemin=None)`, `cle_verdict`, `cumul_appels(cle) -> (eur, UsageTokens)`, `journaliser_appel`. `judge/prompt.py` : `rendre_entree`, `rendre_sortie`, `construire_prompt`, `schema_sortie`, `CRITERE_ELEMENTS`. `judge/config.py` : `charger_juges()` (`principal.mode_appel`, `chemin_grille(racine)`), `judge/grille.py` : `charger_grille`.
- `src/slmsp/mistral/client.py` + `config.py` -- `ClientMistral(config, registre, fabriquer_sdk(config))`, `charger_mistral()`. `budget/config.py` : `charger_budgets`, `charger_tarifs` ; `budget/registre.py` : `RegistreBudget(budgets, tarifs, chemin)`.
- `src/slmsp/harness/citations.py` -- `urls_inventees(texte, passages=(), resultats_outils=(), textes_fournis=())`, `extraire_urls`, `normaliser_url`.
- `src/slmsp/core/texte.py` -- `normaliser`, `compter_mots`, `extraire_nombres -> list[Decimal]`, `kandel_moles`, `VERSION_TEXTE`.
- `tests/eval_outils/test_items_rd.py:89-112` -- sémantique de référence `contient_un_de` (spec 7.3) : `(?:^| )` + `re.escape(normaliser(fragment))` cherché dans `normaliser(valeur)` ; `exact` = égalité et même type ; argument absent → OK seulement si `optionnel`. À reproduire dans `controles.py` (le test n'est pas importable).
- `src/slmsp/cli/eval.py` -- `executer_run` refuse aujourd'hui `notation`/`toutes` ; `tests/evaluation/test_generation.py::test_cli_phase_non_implementee` (l.587) devra être adapté (fichier hors zone à toucher a minima).
- `tests/evaluation/conftest.py` -- `depot_eval` (copie de `eval/` v1.0 + calibrage), `modeles`, `Fabrique` (Harnais factice, `FakeLlmDeterministe`) ; `tests/judge/test_second_reel.py` : modèle `RegistrePlafonne` et `VAR_REEL` pour le test payant.
- Run réel à noter : `<dépôt principal>/runs/eval-generation/20261012-155024-granite-4.0-1b-0cdc` (v1.0, 8 items, un par Tâche ; échantillon second juge ∩ run = `Q-001` ; relecture ∩ run = `CO-001`, `NR-001`).

## Tasks & Acceptance

**Execution:**
- `config/evaluation.toml` + `src/slmsp/evaluation/config.py` -- `schema_version=1` ; `[co]` `equivalences` (’→', nbsp/fines → espace, «»“”→", …→...) ; `[re.longueurs]` courte 80, moyenne 200, detaillee 400 ; `[seuils]` `kappa_fragile=0.6`, `gain_km_min=10`, `plafond_lc=50` ; `ConfigEvaluation` (`ModeleConfig`, fermé) + `charger_evaluation(chemin=None)`. Chaque valeur commentée.
- `src/slmsp/evaluation/controles.py` -- fonctions pures par Tâche rendant un `dict` JSON : `controle_q` (`urls_inventees` sur le texte, connues = sources de la sortie + résultats `resultat-outil` de la trace + `textes_entree(item)`) ; `controle_rd` (appel valide : appariement glouton des appels attendus aux appels émis — même outil, `regles` satisfaites, ordre de la liste sauf `ordre_libre`, appels `optionnel` hors comptes ; `regles` absentes (calibrage) → outil seul ; réponse exacte : avec `valeurs_attendues`, toutes les valeurs numériques des `lignes` (des seules `valeurs_attendues.colonnes` si la liste est donnée) présentes dans `extraire_nombres(texte)` ; sinon id **ou** URL normalisée de `jeu_principal` (ou d'un `autres_jeux_cites_possibles`) dans le texte ; `litige` si titre normalisé présent sans id ni URL) ; `controle_co` (alignement par mots `difflib.SequenceMatcher(autojunk=False)` après équivalences ; faute corrigée si le segment de sortie aligné sur les mots de `[debut, fin)` égale la `correction` ; taux hors faute = mots source hors faute modifiés ou supprimés + mots insérés non adjacents à une faute, ÷ mots du texte, plafonné à 1) ; `controle_ct` (chaque libellé de `champs_a_laisser_en_emplacement` présent tel quel, crochets compris) ; `controle_re` (mots, plafond, respect) ; `controle_lc` (KM entrée = `kandel_moles_entree` sinon calculé sur `entree["texte"]`, KM sortie, gain).
- `src/slmsp/core/schemas/scores.py` -- `Effectifs` (notes, juges, invalides, non_juges, en_erreur, second_juge), `StatutsTache` (jeu_statut, verdicts_relus, fragile, plafonne_lc), `KappaTache` (valeur, par_critere, effectif), `ScoreTache` (tache, score, composantes, rapportes, effectifs, statuts, kappa, cout_juge_eur, manifeste_sha256), `Scores` (`schema_version=1`, run_generation, modele_ref, quantification, jeu_version, jeu_statut, manifeste_sha256, version_texte, taches: dict, cout_juge_total_eur).
- `src/slmsp/evaluation/scores.py` -- `kappa_cohen(paires, categories, pondere)` (quadratique si pondéré ; `None` si < 2 paires ou accord attendu = 1) ; critères ordinaux Q.exactitude, LC.fidelite, LC.clarte_percue, CT.conformite ; binaires les autres ; `presence_elements` sans kappa ; kappa de Tâche = minimum des kappas calculables ; `fragile` si < `kappa_fragile`. Formules de la grille par Tâche (Design Notes) ; `calculer_scores(...) -> Scores`.
- `src/slmsp/evaluation/relecture.py` -- `rendre_relecture(items, generations, verdicts, controles) -> str` (par item de l'échantillon présent : entrée `rendre_entree`, sortie `rendre_sortie`, contrôles, verdict par critère note + justification, inventions) ; `NOM_VALIDATION="relecture-validee.json"`, `relecture_validee(dossier) -> bool` (JSON objet avec `date` ISO valide) ; `charger_scores(dossier) -> Scores` qui applique `verdicts_relus`.
- `src/slmsp/evaluation/notation.py` -- `TYPE_RUN="eval-notation"` ; `Juges` (principal, second, cache) ; `ouvrir_juges(racine, mode_appel=None) -> Juges` (assemblage réel, imports paresseux) ; `noter(depuis, *, juges, racine=None, rapporter=None) -> RapportNotation` : ouvre le parent (`eval-generation`, statut `complet`/`partiel-erreur`), revérifie le jeu, crée le run (slug du parent, `parents=[depuis]`, champs modèle/jeu recopiés), contrôles, demandes au principal (Tâches jugées + RD en litige ; items `ok` seulement), second juge sur `echantillons.second_juge`, écrit `controles.jsonl`, `verdicts.jsonl` (une ligne par item × juge : statut, motif, verdict, cle), `scores.json`, `relecture.md`, statut final.
- `src/slmsp/cli/eval.py` -- `--phase notation --depuis RUN_ID [--mode-juge batch|direct]` ; `--phase toutes` = génération puis notation du run produit (si génération `complet`/`partiel-erreur`) ; affiche le tableau des Scores (Tâche, score, effectifs, kappa, statuts, « non relu ») ; code 0 `complet`, 1 `partiel-*`, 2 usage, 4 jeu altéré. Docstring mise à jour.
- `tests/evaluation/test_controles.py`, `test_scores.py`, `test_kappa.py`, `test_notation.py`, `test_bout_en_bout.py` -- une ligne de matrice par test ; un test de formule par Tâche à partir de verdicts fabriqués sur les ancrages de la grille ; kappa (accord parfait, désaccord, pondéré à la main, non calculable) ; RD `contient_un_de` en début de mot ; CO (faute corrigée, non corrigée, hors faute) ; bout en bout calibrage FakeLlm + juges factices → 8 Tâches ; relance à cache plein → 0 appel et octets identiques.
- `tests/evaluation/test_notation_reel.py` -- unique test `reseau`+`payant` (désélectionné par défaut) : note le run réel (racine = dépôt principal via `SLMSP_DEPOT_PRINCIPAL`), juges réels, `mode_appel="direct"`, registre réel (`VAR_REEL`) plafonné à **0,50 €** pour les deux API, cache réel ; affiche le tableau et le coût.

**Acceptance Criteria:**
- Given un run de génération complet, when `eval run --phase notation --depuis <id>`, then un run `eval-notation` de parent `<id>` contient `verdicts.jsonl`, `scores.json` et `relecture.md`.
- Given Q, CR, LC, RE, CT, NR, when la notation tourne, then chaque item `ok` est soumis au Juge principal, le second juge ne reçoit que l'échantillon, RD seulement en litige, CO jamais.
- Given des verdicts fabriqués aux ancrages de la grille, when on calcule les scores, then chaque formule donne la valeur attendue et chaque Tâche porte score, composantes, effectifs, statuts, kappa, coût et SHA du manifeste.
- Given le calibrage, `FakeLlm` et des juges factices, when génération puis notation, then `scores.json` couvre les 8 Tâches.
- Given `uv run pytest` et `uv run ruff check`, when on les lance, then tout passe hors échecs préexistants listés.

## Spec Change Log

- **2026-10-12, revue du lot 2 (D1, option 1)** : la méthode `valeurs` exigeait les nombres de toutes les cellules, y compris les colonnes non demandées (RD-017 : mois 1, 2, 3 ; RD-010 : année et bailleurs consolidés ; RD-039 : année de fin et UAI). Une réponse exacte était notée fausse. `valeurs_attendues.colonnes` (liste facultative) restreint désormais le contrôle à ces colonnes ; sans elle, le comportement est inchangé (jeu v1.0). `verifier_jeu` refuse une liste vide ou une colonne absente des lignes. Le jeu v1.1 doit déclarer les colonnes (report W3 de `revue-code-lot-2-evaluation.md`).

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 15 findings — high 0, medium 3, low 9, false 3, maybe-false 0
- findings:
  - `[low]` `[reject]` Résultat de juge manquant ignoré (run `complet`) — les deux juges réels rendent un résultat par demande (contrat de 5.4/5.5) ; ajouter une branche pour une violation de contrat non observée n'en vaut pas la complexité.
  - `[false]` `[reject]` `_argument_conforme` refuse un argument présent sans contrainte — `RegleArgument` refuse une règle sans `exact` ni `contient_un_de` qui n'est pas `optionnel: true` (validateur « règle vide », `core/items.py:179`) : le cas ne peut pas exister.
  - `[low]` `[patch]` Identifiant RD cherché en sous-chaîne brute — recherche bornée `(?<![\w-])id(?![\w-])` ; test `test_rd_identifiant_inclus_dans_un_plus_long_refuse`.
  - `[medium]` `[patch]` Second juge payé pour des items sans verdict principal valide — le second juge ne reçoit plus que les items de l'échantillon au verdict principal `juge` ; test `test_second_juge_seulement_apres_verdict_principal_valide`.
  - `[medium]` `[patch]` `relecture.md` sans les références vues par le Juge, justifications multilignes — bloc « Références (vues par le Juge) » (`judge.prompt.references`, absent pour CO) et justifications ramenées sur une ligne.
  - `[low]` `[reject]` `relecture-validee.json` non lié aux fichiers, pas de commande d'affichage — la story exige un fichier daté (AC6), ce qui est fait ; un lien par empreinte est une évolution.
  - `[low]` `[reject]` Pas de provenance de la config dans `scores.json` — `run.json` du run de notation inscrit déjà le SHA de `config/evaluation.toml`, de `juges.toml` et de la grille (`entrees`).
  - `[low]` `[reject]` `--racine` ne s'applique pas aux configs — même convention que la phase génération (5.3) : la config est celle du code exécuté, et son SHA est inscrit au run.
  - `[low]` `[reject]` CO sans faute ou sans texte exclu — tous les items CO de v1.0 ont des fautes et un texte (mode strict) ; cas inatteignable aujourd'hui.
  - `[medium]` `[patch]` CO : l'espacement typographique de la ponctuation compte comme modification — un jeton fait seulement de ponctuation est recollé au mot voisin (guillemet ouvrant au suivant) ; test `test_co_espacement_de_la_ponctuation_tolere`. Les espaces insécables restent des séparateurs (sans effet, sans dommage).
  - `[low]` `[reject]` Longueurs RE non validées, valeur inconnue silencieuse — les `longueur_demandee` de v1.0 sont courte/moyenne/détaillée ; ajout de garde non justifié.
  - `[low]` `[reject]` Plafond LC non appliqué si aucun gain calculable — Kandel-Moles est calculable pour tout texte non vide ; cas inatteignable en pratique.
  - `[false]` `[reject]` Q sans réponse : URL inventée ignorée — conforme à la grille (« Pour un item sans réponse, il est réussi si le critère Cas sans réponse vaut 1 »).
  - `[low]` `[reject]` Chemins sans test (résultats partiels, `--phase toutes --reprendre`, etc.) — les chemins corrigés ont reçu leurs tests ; les autres relèvent de constats rejetés ci-dessus.
  - `[false]` `[reject]` Schémas lâches (`jeu_statut` libre, clés de `taches`, doublons `setdefault`) — `generations.jsonl` est en ajout seul avec reprise qui saute les items présents : aucun doublon produit ; les champs sont écrits par le seul `calculer_scores`.

## Design Notes

**Formules** (items `ok` avec verdict valide ; sinon exclus et comptés) : Q réussi ⇔ exactitude 2 ∧ pertinence 1 ∧ aucune URL inventée ; sans réponse ⇔ `cas_sans_reponse`=1 ; score = % réussis. RD = moyenne(appel valide % micro, réponse exacte %). CR = moyenne(rappel moyen ×100, % `absence_invention`=1) avec rappel = moyenne des `present` (0,5 = action incomplète, noté par le Juge) ; `structure` rapportée. LC = % (fidélité 2 ∧ termes 1) ; si gain KM moyen < 10 → min(score, 50), `plafonne_lc`. CO = moyenne(rappel × (1 − hors faute)) ×100. RE = moyenne(% fidèles, rappel moyen ×100), longueur rapportée. CT = moyenne(moyenne conformité ÷2 ×100, % emplacements réussis). NR = % exactitude 1. Tâche sans item noté : `score=None`.

**Choix pris seul :** identifiant RD = id **ou** URL du jeu (slug data.gouv) ; `valeurs_interdites` CT descriptives, non vérifiables par programme : laissées au Juge (déjà dans ses références), le contrôle automatique ne vérifie que les libellés ; URL Q recalculées depuis la sortie et la trace (passages complets absents de la génération) ; kappa de Tâche = minimum ; items en erreur exclus et comptés ; `--mode-juge` surcharge `mode_appel` (hors clé de cache).

## Verification

**Commands:**
- `uv sync --extra data --extra judge` -- expected: extras installés
- `uv run pytest tests/evaluation -q` -- expected: tout passe (test réel désélectionné)
- `uv run pytest -q` et `uv run ruff check` + `uv run ruff format --check` -- expected: propre hors échecs préexistants
- `$env:SLMSP_ENV_FILE='<dépôt principal>\.env'; $env:SLMSP_DEPOT_PRINCIPAL='<dépôt principal>'; uv run pytest tests/evaluation/test_notation_reel.py -m "reseau and payant" -s` -- expected: tableau des 8 Tâches « non relu », coût ≤ 0,50 €. Payant : lancé une seule fois par l'orchestrateur après la revue.

## Auto Run Result

**Statut :** done. Revue en une couche (Blind Hunter, mode économe). Le test réel payant a été lancé une fois après la revue et a réussi.

**Résumé :** la phase notation `slmsp eval run --phase notation --depuis <run_id> [--mode-juge batch|direct]` crée un run `eval-notation` (parent : la génération). Ce run contient `controles.jsonl`, `verdicts.jsonl`, `scores.json` (JSON canonique et déterministe, coût du Juge lu au cache) et `relecture.md`. `--phase toutes` enchaîne la génération et la notation. Les formules de la grille et le kappa (quadratique pour les critères ordinaux, simple pour les binaires, kappa de Tâche = minimum, `fragile` sous 0,6) vivent seulement dans `evaluation/scores.py`. Les scores restent « non relus » tant qu'un `relecture-validee.json` daté n'est pas déposé dans le run (`charger_scores`).

**Fichiers :**
- `config/evaluation.toml`, `src/slmsp/evaluation/config.py` : tolérances CO, longueurs RE, seuils ; `ConfigEvaluation`.
- `src/slmsp/evaluation/controles.py` : contrôles Q, RD (règle `contient_un_de` de la spec 7.3), CO, CT, RE, LC.
- `src/slmsp/core/schemas/scores.py` : `Scores`, `ScoreTache` et sous-schémas.
- `src/slmsp/evaluation/scores.py` : formules, kappa, statuts.
- `src/slmsp/evaluation/relecture.py` : export `relecture.md`, validation de la relecture.
- `src/slmsp/evaluation/notation.py` : `noter`, `ouvrir_juges` (seul point d'import des juges réels).
- `src/slmsp/cli/eval.py` : phases `notation` et `toutes`, tableau des Scores.
- Tests : `tests/evaluation/test_controles.py`, `test_scores.py`, `test_kappa.py`, `test_notation.py`, `test_bout_en_bout.py`, `test_notation_reel.py`.
- Hors zone (a minima) : `tests/evaluation/test_generation.py`, `test_gel.py` (la phase notation n'est plus « non implémentée ») et `conftest.py` (juges factices, marqueur `payant`).

**Revue :** 15 constats, soit 3 medium, 9 low et 3 false.
- 4 corrigés :
  - second juge appelé seulement après un verdict principal valide ;
  - références et justifications sur une ligne dans `relecture.md` ;
  - espacement de la ponctuation toléré en CO ;
  - identifiant RD cherché avec bornes.
- 11 rejetés : le motif de chacun est dans le Review Triage Log.
- Aucun différé.

**Relecture complémentaire recommandée :** oui (3 entrées medium corrigées). Deux risques restent non vérifiés :
- l'heuristique d'alignement CO (blocs remplacés touchant une faute, recollage de la ponctuation) n'est éprouvée que sur des cas synthétiques et sur un seul item réel ;
- le chemin batch du Juge dans la notation n'a pas été exercé en réel (test réel en appels directs).

**Vérification :**
- `uv run pytest` : 2858 réussis, 157 ignorés, 27 désélectionnés, aucun échec.
- `uv run ruff check` et `ruff format --check` : propres.

**Test réel** (run `20261012-155024-granite-4.0-1b-0cdc`, Juge Claude en direct, second juge Mistral sur `Q-001`, plafond de 0,50 € via `RegistreBudget`) : run `runs/eval-notation/20261012-163519-granite-4.0-1b-b029` (dépôt principal), `complet`, coût 0,2282 €. Les 8 Tâches sont marquées « provisoire, non relu ».

| Tâche | Score |
|---|---|
| Q | 0,0 |
| RD | 50,0 |
| CR | 2,5 |
| LC | 0,0 (plafonné) |
| CO | 81,5 |
| RE | 12,5 |
| CT | 0,0 |
| NR | 100,0 |

Le kappa n'est pas calculable : une seule paire de verdicts.

**Décisions prises seul :** voir les Design Notes, auxquelles s'ajoutent les choix de l'implémenteur :
- seules les Tâches présentes dans la génération sont notées ;
- le score d'une Tâche est la moyenne de ses composantes disponibles ;
- `partiel-budget` prime sur `partiel-erreur` ;
- CR et RE sans éléments de référence sont marqués `non-juge` (`non-jugeable`) ;
- RD sans jeu de référence : « réponse exacte » vaut `None`.
