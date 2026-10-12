---
title: 'Story 1.5 — Registre de budget persistant avec arrêt au plafond'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '543afad58f698ef9cf26e78eaec4b64d301828d9'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** Les budgets durs de D1.6 (Mistral 30 € dont génération 25 et juge 5, Anthropic 10 €) ne sont encore tenus par aucun code : deux processus, deux worktrees, une relance, un crash ou un lot batch pourraient les dépasser.

**Approach:** Un `RegistreBudget` SQLite unique par machine (`SLMSP_VAR_DIR/budget.sqlite`) réserve le coût pire cas de chaque tentative en `BEGIN IMMEDIATE`, refuse au plafond (`BudgetEpuise`, code 3), régularise au coût réel, gère réservations orphelines et lots batch, et se relit par `slmsp budget etat [--json]` sans rien modifier.

## Boundaries & Constraints

**Always:**
- Plafonds, `campagne_id`, marge (EUR), majoration des tokens d'entrée et imputations des usages dans `config/budgets.toml` ; tarifs datés en USD par million de tokens, par modèle et par mode (`direct`, `batch`, chacun avec `entree`, `sortie`, `ecriture_cache`, `lecture_cache`) et taux USD → EUR daté dans `config/tarifs.toml`. Modèles pydantic `ModeleConfig` (`extra="forbid"`) dans `budget/config.py`, lus par `charger_toml`.
- Tarifs de départ : `claude-opus-5-5` direct 4 / 20 $, cache écriture 8 $ (TTL 1 h, le plus cher), lecture 0,20 $ ; batch −50 % (2 / 10 / 4 / 0,10) — source skill `claude-api`, relevé 2026-10-06. `mistral-large-latest` prudent 2 / 6 $ direct, 1 / 3 $ batch, mention « à vérifier par Anaël » (D-nuit-A2-9). Taux 1 USD = 1 EUR, prudent, daté 2026-10-12.
- Toutes les sommes dépensées, réservées et plafonds sont en euros. Contrôle à deux niveaux : sous-poste (s'il existe) puis poste ; refus si dépensé + réservé + coût nouveau + marge > plafond, sans rien écrire.
- Chaque réservation porte `campagne_id`, poste, sous-poste, modèle, mode, PID et date de création du processus (psutil), `batch_id` éventuel ; les totaux sont filtrés par le `campagne_id` courant.
- Connexion par opération via `core.var.ouvrir_sqlite` (WAL, 30 s) ; écritures en `BEGIN IMMEDIATE`.
- `budget` reste couche 1a : n'importe que `slmsp.core`, la bibliothèque standard, pydantic et psutil.

**Never:**
- Aucune fonction, méthode ni commande de remise à zéro, de suppression de ligne ou d'effacement de fichier.
- Aucun tarif par défaut : modèle, mode ou composante de cache absents → `TarifInconnu`.
- Aucun appel d'API ni réseau dans le code ou les tests ; aucun SDK payant importé.
- Ne pas toucher hors de `src/slmsp/budget/`, `config/{budgets,tarifs}.toml`, `src/slmsp/cli/budget.py`, `tests/budget/`, `tests/cli/`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Réservation acceptée | reste suffisant | ligne `reservee`, montant pire cas = ⌈entrée × majoration⌉ × tarif entrée (`ecriture_cache` si `avec_cache`) + `max_tokens` × tarif sortie, × taux | — |
| Plafond sous-poste | `mistral.juge` presque plein, `mistral` non | `BudgetEpuise`, aucune ligne ajoutée | message cite poste/sous-poste, plafond, reste |
| Régularisation | `regulariser(id, usage)` | état `regularisee`, montant réel calculé des 4 compteurs | id inconnu ou déjà réglé → `SlmspError` |
| Échec sans usage | `compter_pire_cas(id)` | état `pire-cas`, réel = réservé | — |
| Tarif inconnu | modèle/mode absent, ou usage de cache sans tarif de cache | `TarifInconnu` | rien n'est réservé |
| Sous-poste requis | poste à sous-postes sans sous-poste, ou poste/sous-poste inconnu | `ConfigurationInvalide` | — |
| Orpheline | ligne `reservee` sans lot, PID mort | à l'ouverture : `pire-cas`, motif `orpheline` | — |
| Lot vivant | ligne avec `batch_id`, PID mort | reste `reservee` ; listée par `lots_ouverts()` | — |
| Lot | `reserver_lot(batch_id, …, nb_requetes=N)` | réserve au tarif batch min(N, taille max) requêtes, renvoie le nombre retenu | 0 retenu → `BudgetEpuise` ; `batch_id` déjà utilisé → `SlmspError` |
| Relances | `executer_avec_relances(appel, 3, …)`, 2 échecs puis succès | 3 réservations : 2 `pire-cas`, 1 `regularisee` | dernière exception relancée ; `SlmspError` jamais relancée |
| Relevé | `slmsp budget etat --json`, base absente | plafonds, 0 dépensé/réservé ; la base n'est pas créée | — |

</intent-contract>

## Code Map

- `src/slmsp/core/erreurs.py` -- lecture seule ; `BudgetEpuise` (code 3), `TarifInconnu`, `ConfigurationInvalide`, `SlmspError` existent.
- `src/slmsp/core/config.py` -- `ModeleConfig`, `charger_toml(chemin, modele)`, `racine_projet()` (défaut des TOML).
- `src/slmsp/core/var.py` -- `dossier_var()`, `ouvrir_sqlite(chemin)` ; passer `isolation_level = None` puis `BEGIN IMMEDIATE` explicite.
- `src/slmsp/inference/processus.py:286` -- modèle de `processus_identique(pid, creation)` (psutil, tolérance 0,01 s) à reproduire dans `budget` (couche 1b non importable).
- `src/slmsp/net/journal.py` -- modèle de base SQLite par opération (`PRAGMA user_version`).
- `src/slmsp/cli/__init__.py` -- lecture seule ; `budget` déjà déclarée ; le module expose `enregistrer(sous_parseurs)` ; `SlmspError` → code.
- `src/slmsp/cli/index.py` -- modèle de sous-commande à actions.
- `tests/conftest.py` -- `SLMSP_VAR_DIR` temporaire par test, garde réseau.
- `tests/core/test_var.py:153` -- modèle de second processus réel (`subprocess.Popen([sys.executable, "-c", …])`).
- `tests/test_cli.py:82` -- saute `budget` dès que `cli/budget.py` existe.
- `tests/test_architecture.py` -- `budget` couche 1a ; doit continuer à passer.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/budget/config.py` -- `ConfigBudgets` (`schema_version`, `campagne_id`, `marge_eur ≥ 0`, `majoration_entree ≥ 1`, `postes: {nom: Poste(plafond_eur, sous_postes: {nom: float})}`, `imputations: {usage: "poste[.sous_poste]"}` validées contre les postes) ; `ConfigTarifs` (`taux_usd_eur` daté, `modeles: {id: TarifModele(devise, date, source, note, modes: direct/batch → TarifMode)}`) ; `charger_budgets(chemin=None)`, `charger_tarifs(chemin=None)`.
- `src/slmsp/budget/tarifs.py` -- `UsageTokens(entree, sortie, ecriture_cache=0, lecture_cache=0)` ; `tarif(config, modele, mode)` → `TarifInconnu` ; `cout_pire_cas(...)`, `cout_reel(...)` en EUR.
- `src/slmsp/budget/registre.py` -- `NOM_REGISTRE = "budget.sqlite"`, `RegistreBudget(config=None, tarifs=None, chemin=None)` : schéma, régularisation des orphelines à l'ouverture, `imputer(usage)`, `reserver`, `regulariser`, `compter_pire_cas`, `executer_avec_relances`, `taille_max_lot`, `reserver_lot`, `collecter_lot`, `annuler_lot(batch_id, usage=None)`, `lots_ouverts`, `etat()` ; fonction `releve(chemin=None, config=None)` en lecture seule (`mode=ro`, base absente → zéros, aucune régularisation).
- `src/slmsp/budget/__init__.py` -- docstring du paquet (sans réexport lourd).
- `config/budgets.toml`, `config/tarifs.toml` -- valeurs ci-dessus, commentées, datées.
- `src/slmsp/cli/budget.py` -- `slmsp budget etat [--json]` : tableau texte ou JSON canonique (liste de lignes `poste`, `sous_poste`, `plafond_eur`, `depense_eur`, `reserve_eur`, `reste_eur`) plus `campagne_id`.
- `tests/budget/test_registre.py` -- critères 1, 2, 3, 7 (orpheline par un sous-processus qui réserve et sort), 9, 10, matrice.
- `tests/budget/test_tarifs.py` -- critères 4, 5 sur les vrais TOML et sur des TOML de `tmp_path`.
- `tests/budget/test_concurrence.py` -- critère 6 : deux sous-processus synchronisés par fichier, plafond bas, exactement un `BudgetEpuise`, total ≤ plafond.
- `tests/budget/test_lots.py` -- critère 8 et cycle `reserver_lot` / `collecter_lot` / `annuler_lot`.
- `tests/cli/test_budget.py` -- critère 11 : sortie JSON, base non créée ni modifiée (octets identiques).

**Acceptance Criteria:**
- Given la story terminée, when `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`, then tout passe, y compris `tests/test_architecture.py`.
- Given le paquet `slmsp.budget`, when on inspecte ses attributs publics et `slmsp budget --help`, then aucun nom ni action ne contient « reset », « remise », « zero », « vider » ni « supprimer ».
- Given les critères 1 à 11 de la story 1.5 d'`epics.md`, when les tests de `tests/budget` et `tests/cli/test_budget.py` tournent, then chacun est couvert par au moins un test nommé.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 38 findings — high 0, medium 11, low 24, false 3, maybe-false 0
- findings:
  - `[medium]` `[patch]` (vérification) Aucun test d'un `regulariser` qui échoue dans `executer_avec_relances` — groupe « relances » : capture élargie à `Exception`, comptage pire cas gardé, test `test_critere_9_regularisation_impossible_comptee_au_pire_cas` ajouté.
  - `[low]` `[patch]` (vérification) Aucun test de taille de lot bornée par le poste parent — `test_critere_8_taille_max_bornee_par_le_poste` ajouté (28 €, 24 € engagés : 8 requêtes, lot de 10 réduit à 8).
  - `[low]` `[patch]` (vérification) Aucun test de `lots_ouverts()` sur une campagne antérieure — `test_lots_ouverts_toutes_campagnes` ajouté.
  - `[low]` `[patch]` (vérification, autre) `AccessDenied` tenu pour mort — groupe « vivant » : `AccessDenied` tenu pour vivant, test monkeypatché ajouté.
  - `[medium]` `[patch]` (vérification, autre) Coût réel au-delà de la réservation quand l'usage compte du cache non annoncé — groupe « dépassement » : motif `depassement-reservation` posé, test ajouté.
  - `[low]` `[reject]` (intention a) Changer `campagne_id` équivaut à une remise à zéro — AD-5 fixe `campagne_id` dans `budgets.toml` ; c'est une décision humaine sur un fichier versionné, rien n'est effacé ; à confirmer par Anaël (Auto Run Result).
  - `[low]` `[reject]` (intention b) Plafonds lus par copie de travail — `config/budgets.toml` est versionné, identique d'un worktree à l'autre au même commit ; le spine place les plafonds dans ce fichier.
  - `[medium]` `[patch]` (intention c) Coût réel non plafonné après l'appel — groupe « dépassement » ; un appel déjà payé ne peut être refusé, le dépassement est signalé et compté, l'appel suivant est refusé.
  - `[low]` `[patch]` (intention d) `max_retries=0` non porté — règle écrite dans la docstring d'`executer_avec_relances` ; la construction des clients SDK relève de 5.4 et du paquet `mistral`.
  - `[low]` `[reject]` (intention e) Imputation séparée de `reserver` — `imputer` est testé enchaîné à `reserver` ; une API de plus ajouterait une surface sans consommateur.
  - `[low]` `[reject]` (intention f) `batch_id` choisi par l'appelant — choix consigné dans les Design Notes ; le corriger reviendrait à modifier la spec.
  - `[low]` `[reject]` (intention g) « reste » affiché sans la marge — la marge est affichée en tête et dans le JSON ; la colonne suit la définition du critère 11.
  - `[false]` `[reject]` (intention h) Pas de consommateur de `partiel-budget` — le marquage du run revient aux commandes payantes des stories suivantes ; aucun run n'existe dans cette story.
  - `[medium]` `[patch]` (aveugle 1) Coût réel supérieur à la réservation accepté sans signal — groupe « dépassement ».
  - `[false]` `[reject]` (aveugle 2) Orphelines balayées seulement à l'ouverture — une orpheline reste comptée au même montant, réservée ou au pire cas : la balayer ne libère aucun budget, le refus est identique.
  - `[medium]` `[patch]` (aveugle 3) Résultat payé perdu et exception masquée quand `regulariser` échoue — groupe « relances » : erreur d'origine toujours levée, comptage gardé ; lever reste le comportement prévu (tarif inconnu = erreur).
  - `[low]` `[patch]` (aveugle 4) `AccessDenied` tenu pour mort — groupe « vivant ».
  - `[low]` `[patch]` (aveugle 5) Cache de date de création non lié au PID — cache `(pid, creation)` recalculé si le PID change.
  - `[low]` `[reject]` (aveugle 6) Changements de campagne et de plafonds sans trace — même cause que intention a.
  - `[medium]` `[patch]` (aveugle 7) `releve` laisse fuir `sqlite3.DatabaseError` — groupe « relevé » : toute la lecture sous `except sqlite3.Error` → `SlmspError` ; test CLI sur base corrompue (code 1, sans trace). Fichiers `-wal`/`-shm` : rejeté, gérés par SQLite, base principale inchangée.
  - `[low]` `[reject]` (aveugle 8) Pas d'action CLI pour les lots ouverts — le critère 11 ne demande que `etat` ; `lots_ouverts()` sert la relance (AD-26) côté code.
  - `[low]` `[reject]` (aveugle 9) Toute `Exception` retentée sans attente — coût borné à `tentatives` × pire cas ; un prédicat ajouterait un paramètre ; la matrice fixe « SlmspError jamais relancée ».
  - `[low]` `[patch]` (aveugle 10) Alias flottant `mistral-large-latest` — note et commentaire ajoutés dans `tarifs.toml` (« à vérifier par Anaël » conservé).
  - `[low]` `[patch]` (aveugle 11) Tests faibles — paramétrage du cas cache corrigé, scan de suppression étendu à `cli/budget.py` ; assertion de contention par processus rejetée (le premier test de concurrence prouve déjà la course).
  - `[low]` `[reject]` (aveugle 12) Arrondi flottant entre `_taille_max` et `_controler` — tolérance de 1e-9 €, cas limite improbable ; le corriger ajouterait une boucle.
  - `[medium]` `[patch]` (bord 1) `slmsp budget etat` plante sur base corrompue — groupe « relevé ».
  - `[low]` `[patch]` (bord 2) `AccessDenied` tenu pour mort — groupe « vivant ».
  - `[medium]` `[patch]` (bord 3) Retour non couple d'`appel()` retenté et repayé — groupe « relances » : déballage hors du `try`, pire cas, `TypeError` sans relance ; test ajouté.
  - `[medium]` `[patch]` (bord 4) `compter_pire_cas` masque l'exception d'origine — groupe « relances » : `_compter_pire_cas_garde`, erreur d'origine chaînée ; test ajouté.
  - `[medium]` `[patch]` (bord 5) Échec non-`SlmspError` de `regulariser` laisse la réservation ouverte — groupe « relances ».
  - `[low]` `[reject]` (bord 6) Réponse payée jetée sur `TarifInconnu` — lever est le comportement fixé (aucun tarif par défaut) ; la tentative est comptée au pire cas.
  - `[medium]` `[patch]` (bord 7) Dépensé au-delà du plafond après régularisation — groupe « dépassement ».
  - `[false]` `[reject]` (bord 8) Lot impossible à régler si le tarif disparaît — `annuler_lot(batch_id)` sans usage règle au pire cas sans consulter les tarifs.
  - `[low]` `[patch]` (bord 9) `ROLLBACK` sans transaction active masque l'erreur — rollback conditionné à `in_transaction`.
  - `[low]` `[patch]` (bord 10) Cache de création après fork — même correctif qu'aveugle 5.
  - `[low]` `[reject]` (bord 11) Arrondi de `reserver_lot` — même cause qu'aveugle 12.
  - `[low]` `[patch]` (bord 12) Prix d'écriture de cache inférieur à l'entrée sous-estime le pire cas — `max(entree, ecriture_cache)` ; test ajouté.
  - `[low]` `[patch]` (bord 13) `campagne_id` blanc ou entouré d'espaces — `strip_whitespace` et longueur minimale ; tests ajoutés.

## Design Notes

- **Modes.** Les modes tarifaires sont `direct` et `batch` ; l'écriture et la lecture de cache sont des composantes de chaque mode, car un même appel mêle entrée simple, cache et sortie. Le pire cas prend `ecriture_cache` au lieu d'`entree` quand l'appelant annonce `avec_cache=True`.
- **Modèle résolu.** Le tarif est cherché par l'identifiant exact passé à `reserver` ; la régularisation reprend le tarif de la réservation. Aucun alias en v1.
- **Campagne.** Changer `campagne_id` démarre une nouvelle campagne sans rien effacer : les lignes anciennes restent en base, hors des totaux.
- **Lots.** `batch_id` est l'identifiant choisi par l'appelant, réservé avant toute soumission et toute attente ; la correspondance avec l'identifiant du fournisseur reste au Juge (5.4).
- **Usages.** `imputer("juge-second") == ("mistral", "juge")` ; `generation` et `validation` → `("mistral", "generation")` ; `juge-principal` → `("anthropic", None)`.

## Verification

**Commands:**
- `uv run pytest tests/budget tests/cli` -- expected: tout passe.
- `uv run pytest` -- expected: tout passe (sautés préexistants autorisés).
- `uv run ruff check` et `uv run ruff format --check` -- expected: aucun écart.
- `uv run slmsp budget etat --json` -- expected: JSON des postes, code 0.

## Auto Run Result

Status: done

**Résumé.** Le paquet `slmsp.budget` fournit `RegistreBudget`, une base SQLite unique par machine (`SLMSP_VAR_DIR/budget.sqlite`, campagne `nuit-2026-10-12`). Il réserve le coût pire cas de chaque tentative en `BEGIN IMMEDIATE` et refuse au plafond du sous-poste puis du poste (`BudgetEpuise`, code 3). Il régularise ensuite au coût réel, ou compte le pire cas. Les orphelines (PID mort) passent au pire cas à l'ouverture. Les lots batch sont réservés au tarif batch, avec réduction au reste disponible. Les relances se font une réservation par tentative. `slmsp budget etat [--json]` lit le registre sans le modifier. Le code ne contient aucune remise à zéro ni suppression.

**Fichiers.**
- `config/budgets.toml` : plafonds (anthropic 10, mistral 30, dont generation 25 et juge 5), marge de 0,50 €, majoration d'entrée de 1,25, imputations des usages.
- `config/tarifs.toml` : `claude-opus-5-5` à 4 / 20 $ en direct et 2 / 10 $ en batch, cache 8 / 0,20 $ en direct et 4 / 0,10 $ en batch (skill `claude-api`, 2026-10-06). `mistral-large-latest` à 2 / 6 $ en direct et 1 / 3 $ en batch, prudent, alias flottant, « à vérifier par Anaël ». 1 USD = 1 EUR, daté.
- `src/slmsp/budget/config.py` : modèles pydantic stricts et chargeurs.
- `src/slmsp/budget/tarifs.py` : `UsageTokens`, coût pire cas et coût réel, `TarifInconnu` sans défaut.
- `src/slmsp/budget/registre.py` : `RegistreBudget` et `releve` en lecture seule.
- `src/slmsp/budget/__init__.py` : docstring du paquet.
- `src/slmsp/cli/budget.py` : `slmsp budget etat [--json]`.
- `tests/budget/{conftest,test_registre,test_tarifs,test_concurrence,test_lots}.py` et `tests/cli/test_budget.py` : critères 1 à 11 et matrice.

**Revue.** 38 remarques : 0 haute, 11 moyennes, 24 basses, 3 fausses.
- Correctifs regroupés par cause :
  - relances robustes : retour non couple, comptage gardé, échec de régularisation ;
  - signalement d'un coût réel supérieur à la réservation (motif `depassement-reservation`) ;
  - relevé tolérant à une base corrompue ;
  - `AccessDenied` tenu pour vivant ;
  - cache de création lié au PID ;
  - `ROLLBACK` conditionnel ;
  - pire cas au maximum d'entrée et d'écriture de cache ;
  - `campagne_id` sans blanc ;
  - note d'alias Mistral ;
  - règle `max_retries=0` en docstring ;
  - 6 tests ajoutés ou renforcés.
- Patchés par verdict : 11 moyennes (en 3 groupes), 16 basses.
- Rejets et leurs raisons :
  - campagne comme remise à zéro : décision humaine sur un fichier versionné, conforme à AD-5 ;
  - plafonds par copie de travail : fichier versionné ;
  - imputation séparée de `reserver` : surface sans consommateur ;
  - `batch_id` de l'appelant : Design Notes ;
  - « reste » sans marge : la marge est affichée ;
  - `partiel-budget` : stories suivantes ;
  - balayage des orphelines : faux, le montant compté est identique ;
  - action CLI des lots : hors critère 11 ;
  - prédicat de relance : paramètre en plus, coût borné ;
  - arrondi des lots : tolérance de 1e-9 € ;
  - `TarifInconnu` après l'appel : lever est le comportement fixé ;
  - lot sans tarif : faux, `annuler_lot` sans usage le règle ;
  - fichiers `-wal`/`-shm` : gérés par SQLite.
- Aucun report.

**Relecture de suivi recommandée : oui.** Trois groupes moyens ont été patchés. Le risque non vérifié est le chemin d'erreur réécrit d'`executer_avec_relances` face à de vrais SDK : ordre des exceptions chaînées, et comptage quand la base est verrouillée au-delà de 30 s. Ce chemin n'est éprouvé que par des appels factices.

**Vérification.**
- `uv run pytest tests/budget tests/cli` : 108 réussis.
- `uv run pytest` : 1780 réussis, 133 sautés, 14 désélectionnés.
- `uv run ruff check` et `ruff format --check` : propres.
- `uv run slmsp budget etat [--json]` : code 0, tout à zéro, base non créée.
- Aucun appel d'API.

**Décisions prises seul.**
- Marge de 0,50 € appliquée aux deux niveaux, majoration de 1,25.
- Écriture de cache Opus au tarif du TTL 1 h (8 $).
- Batch Mistral à −50 % du tarif prudent.
- Tarif Mistral gardé à 2 / 6 $ (D-nuit-A2-9) : la page de tarifs de Mistral est hors D1.5. De mémoire, le tarif public de Mistral Large 3 est d'environ 0,5 / 1,5 $, donc la valeur prudente le couvre.
- Modes `direct` et `batch`, le cache étant une composante de chaque mode.
- Totaux filtrés par `campagne_id`.
- `batch_id` choisi par l'appelant.

**Risques résiduels.**
- Un coût réel supérieur à l'estimation peut dépasser le plafond d'au plus l'écart d'un appel. Il est signalé et bloque la suite.
- Les tarifs Mistral et le taux de change restent à confirmer par Anaël.
- `budget etat` laisse `-shm` et `-wal` à côté d'une base WAL existante.
