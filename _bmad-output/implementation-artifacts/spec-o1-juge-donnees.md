---
title: 'O1 — Juge de données (slmsp data juger)'
type: 'feature'
created: '2026-10-20'
status: 'review'
---

# Spec O1 — Juge de données (`slmsp data juger`)

Méthodologie v2 (`plan-methodo-2026-10-20.md` §2 principe 3, §4 O1, §7 bis). Story à risque : relue avant code.

## But
Noter des **candidats de données d'entraînement** (cibles Mistral ; à l'étage 2, sorties de la base locale) selon une grille de données, par **DeepSeek V4 Pro via OpenRouter**, pour décider quelles cibles gardent leur place. Le juge du test (Claude) n'intervient jamais.

## Règles (bloquantes)
1. **D1** : le juge de données ne produit jamais de cible. Sa sortie est structurée (notes, listes, motifs courts, extraits) ; le schéma n'a aucun champ de réponse réécrite ou corrigée, et un champ inconnu est refusé (`extra=forbid`).
2. **Pas de référence d'évaluation** : rien n'est lu sous `eval/` (ni items, ni grille du juge, ni cassettes). Toutes les lectures passent par `core.artefacts.lire` (lecteur `data`), qui refuse déjà `eval/`, `runs/eval*` et le cache des verdicts. Le prompt reçoit seulement la **source** de la session et le candidat (voir § Source par tâche).
3. **Couches (AD-1, `tests/test_architecture.py`)** : `data` ne peut pas importer `slmsp.judge` (règle `judge-depuis-data/train`). Le module réutilise donc **seulement** `slmsp.fournisseurs.client` (`ClientCompatibleOpenAI`, `OPENROUTER`, `fabriquer_http`, `lire_cle`) et `slmsp.fournisseurs.journal.JournalAppels`. Ni `JugeTiers`, ni `ConfigJugeTiers`, ni `CacheVerdicts`, ni `extraire_json` de `judge/tiers.py` : la lecture tolérante du JSON (bloc de code, texte autour) est déplacée dans `slmsp.fournisseurs` (ou `core`) et importée des deux côtés, sans changer le comportement de `judge/tiers.py` (ses tests restent verts).
4. **Configuration** : table `[juge_donnees]` de `config/donnees.toml` (le paquet `data` ne lit pas `juges.toml`) : `modele = "deepseek/deepseek-v4-pro"`, `temperature = 0.0`, `max_tokens = 8000`, `effort_raisonnement = "low"`, `format_reponse = "json_schema"`, `sortie_estimee`, `marge_raisonnement`, `usage_budget = "juge-donnees-openrouter"`, et les seuils `[juge_donnees.seuils.<TACHE>]`. Le modèle de `data/config.py` est étendu (clés inconnues refusées par `charger_toml`). Un test vérifie que `modele` égale celui de `[juges_tiers.deepseek]` de `juges.toml`.
5. **Budget** : imputation `juge-donnees-openrouter = "openrouter"` ajoutée à `[imputations]` de `config/budgets.toml` ; **aucun nouveau poste ni plafond**, campagne `methodo-v2-2026-10-20` inchangée (ses plafonds sont ancrés). Réservation au pire cas avant chaque appel (`ClientCompatibleOpenAI.appeler` : `max_tokens` en sortie, majoration d'entrée) puis régularisation. `BudgetEpuise` → candidats restants non jugés, statut du run **`partiel-budget`** (convention des autres étapes), reprise par `--reprendre`.
6. **Journal** : fichier distinct `SLMSP_VAR_DIR/appels-juge-donnees.sqlite` (`JournalAppels`), jamais celui des juges tiers (`appels-juges-tiers.sqlite`, qui contient des prompts d'évaluation). Le module **n'appelle pas** `JournalAppels.appels()` (lecture SQLite hors `core.artefacts`, AD-24).
7. **Cache** : un verdict est réutilisé par empreinte `sha256(modèle, effort, version du prompt de juge, SHA de la grille de données de la tâche, source, candidat)`. Index du cache = lignes `verdicts.jsonl` des runs `data-juger` existants et des runs O6 (`runs/data-*/<id>/verdicts.jsonl`, lus par `core.artefacts.lire`) ; pas de nouvelle base SQLite (le lecteur `data` n'a pas accès à `var/` hors journal Mistral). Une sortie interrompue (`finish_reason` de longueur) ou illisible n'est pas mise en cache.
8. Aucun appel réel dans les tests (transport HTTP simulé, comme `tests/fournisseurs`).

## Source par tâche (étage 1)
- **CR** : la **transcription** (réponse Mistral journalisée du gabarit `transcription-cr`, amorce dérivée de la session) fait seule autorité. Le scénario de seed n'est **pas** donné au juge : une décision du scénario absente de la transcription ne peut pas figurer dans le CR sans invention.
- **LC** : le texte source (amorce `texte`).
- **CT** : les amorces de la session (type de courrier, objet, éléments connus).
- **RE**, **CO** : hors étage 1 (option étage 2).

## Grille de données (`config/prompts/juge-donnees/<tache>.md`, versionnée, SHA consigné)
Rédigée par l'outillage : critères et ancrages, **sans exemple de réponse** (D1). Elle reprend les critères **et les échelles** de la grille du juge de test (pour que la sélection récompense ce que le test mesure), en remplaçant la référence par la source :
- **CR** : `decisions` et `actions` = listes que le juge extrait de la transcription, chacune marquée `presente` / `partielle` (action sans responsable ou échéance pourtant donnés) / `absente` dans le CR → **couverture = rappel calculé par le code** (partielle = ½), comme au test ; `invention` 0/1 (aucune personne, date, chiffre, décision ou action absente de la transcription ; un point discuté présenté comme décidé compte comme invention) ; `structure` 0/1 (aussi contrôlée par O6).
- **LC** : `fidelite` 0/1/2 (droits, obligations, conditions, délais, montants, références conservés ; aucune modalité changée : « peut » ↛ « doit », condition supprimée ; aucun ajout) ; `termes` 0/1 (termes juridiques gardés ou expliqués sans être remplacés) ; `ajout` : liste des ajouts (conseil, démarche, coordonnée).
- **CT** : `conformite` 0/1/2 (blocs du format administratif) ; `invention` 0/1 (nom, date, référence, montant, adresse hors amorces et hors emplacements entre crochets).

## Sortie du juge (schéma JSON strict, pydantic `extra=forbid`, par tâche)
`{"criteres": {"<critere>": {"note": int, "motif": str (≤ 300 car.), "extraits": [str]}}, "listes": {...} (CR : decisions, actions), "verdict_modele": "accepte"|"refuse"}`.
- `extraits` = citations exactes du candidat ou de la source qui fondent la note ; contrôlées comme sous-chaînes après normalisation (espaces, espaces insécables, apostrophes et guillemets typographiques, casse inchangée) ; une citation non retrouvée est retirée et comptée (`extraits_invalides`).
- Le **verdict** est recalculé côté code par les seuils de `[juge_donnees.seuils.<TACHE>]` ; celui du modèle n'est qu'informatif. Défauts : CR `invention = 1` et `couverture ≥ 0.8` ; LC `fidelite = 2` et `termes = 1` ; CT `conformite = 2` et `invention = 1`.
- Sortie non conforme au schéma après une relance → verdict `invalide` (ni accepté, ni mis en cache), compté au rapport.

## Commande
`slmsp data juger --depuis <run data-generate | run candidats O2> [--taches CR,LC,CT] [--limite N] [--plafond-estime EUR] [--reprendre RUN_ID]`
- Coût estimé affiché avant le lancement (tokens estimés × tarif `tarifs.toml`, cache à 0) ; refus avant tout appel si l'estimation **pire cas** dépasse `--plafond-estime`.
- Run immuable `runs/data-juger/<id>/` : `verdicts.jsonl` (session_id, `candidat_id`, tâche, notes, listes, motifs, extraits, verdict, coût, clé de cache), `rapport.json` (taux d'acceptation par tâche et par critère, extraits invalides, invalides, coût), statut final.
- `candidat_id` : `mistral:<appel_id>` pour une réponse du journal Mistral, `slm:<appel_local_id>` pour une sortie locale (O2) ; contrat partagé avec O3 et C5.
- Bibliothèque réutilisée par O6 : `juger_candidat(tache, source, candidat) -> VerdictDonnees` (sans écriture de run ; l'appelant écrit).

## Critères de fin
- Tests : schéma strict (champ inconnu refusé, aucun champ de réécriture) ; extraits non retrouvés retirés, apostrophes typographiques retrouvées ; verdict recalculé par seuils (CR : rappel avec partielles) ; lecture d'un chemin `eval/` → `LectureInterdite` ; règle d'architecture verte (aucun import de `slmsp.judge`) ; imputation `openrouter` sans nouveau poste ; journal distinct de celui des juges tiers ; cache (2e appel sans coût ni réservation) ; sortie interrompue non mise en cache ; `BudgetEpuise` → `partiel-budget` puis reprise sans double appel ; refus au-delà de `--plafond-estime`.
- `tests/judge/test_tiers*.py` verts après le déplacement de `extraire_json`.
- `ruff`, contrôle rapide ; aucun appel réel.

## Revue de la spec
Relecture du 2026-10-20 (reviewer, avant code), contre `judge/tiers.py`, `fournisseurs/client.py`, `core/artefacts.py`, `tests/test_architecture.py`, `config/{budgets,juges,donnees}.toml`, `eval/grille-juge-v1.md`.

| # | Gravité | Constat | Changement |
|---|---|---|---|
| 1 | high | « Réutiliser `judge/tiers.py` » et « modèle de `juges.toml` » : impossible, `data` ne peut pas importer `slmsp.judge` (règle d'architecture `judge-depuis-data/train`). | Règle 3 : seuls `fournisseurs.client` et `fournisseurs.journal` ; `extraire_json` déplacé hors de `judge`. Règle 4 : config `[juge_donnees]` dans `donnees.toml`, test d'égalité du modèle. |
| 2 | high | Cache « par empreinte » sans support : `CacheVerdicts` est côté `judge`, et le lecteur `data` n'a pas accès à une base `var/` (AD-24). | Règle 7 : index du cache = `verdicts.jsonl` des runs `data-*`, lus par `core.artefacts.lire`. |
| 3 | medium | Journal non précisé : réutiliser celui des juges tiers mêlerait prompts d'évaluation et de données. | Règle 6 : `appels-juge-donnees.sqlite`, pas de lecture via `appels()`. |
| 4 | medium | Arrêt au plafond en `partiel-erreur` : la convention des étapes est `partiel-budget`. | Corrigé (règle 5). |
| 5 | medium | « Mêmes échelles 0/1/2 » faux : au test, CR couverture = rappel 0-1 (action incomplète = ½), invention 0/1 ; LC termes 0/1 ; CT conformité 0/1/2. Une grille divergente sélectionne autre chose que ce que le test mesure. | Grille alignée sur les échelles du test ; couverture CR = rappel calculé par le code à partir des listes ; seuils par défaut alignés sur les scores de tâche. |
| 6 | medium | Scénario de seed donné comme source CR : une décision du scénario perdue par la transcription ferait refuser un CR fidèle. | Transcription seule autorité ; scénario non transmis. |
| 7 | medium | Contrôle des extraits « normalisation des espaces » seulement : les modèles changent apostrophes et guillemets typographiques, d'où des extraits valides retirés. | Normalisation étendue. |
| 8 | low | `--depuis` sur un run `build` : `data/train/` n'est pas dans la liste d'accès du lecteur `data`. | Retiré (generate ou candidats seulement). |
| 9 | low | Identifiant de candidat non défini, alors que O3 et C5 joignent dessus. | `candidat_id` = `mistral:<appel_id>` ou `slm:<appel_local_id>`. |

## Auto Run Result

Implémentation du 2026-10-20 (branche `story/o1-juge-donnees`), aucun appel réel.

**Fichiers.** `src/slmsp/data/juge_donnees.py` (bibliothèque et run), `src/slmsp/fournisseurs/lecture.py` (`extraire_json` déplacé, importé par `judge/tiers.py`, comportement inchangé), `src/slmsp/fournisseurs/journal.py` (`NOM_JOURNAL_JUGE_DONNEES = "appels-juge-donnees.sqlite"`), `src/slmsp/data/config.py` (`JugeDonneesConfig`, `CRITERES_JUGE_DONNEES`), `src/slmsp/cli/data.py` (`slmsp data juger`), `config/donnees.toml` (`[juge_donnees]`), `config/budgets.toml` (imputation `juge-donnees-openrouter = "openrouter"`, aucun poste ni plafond), `config/prompts/juge-donnees/{cr,lc,ct}.md`, `tests/data/test_juge_donnees.py` (28 tests).

**Contrat de bibliothèque (O6a).**
```python
juge = JugeDonnees(config: JugeDonneesConfig, client: ClientCompatibleOpenAI,
                   grilles=charger_grilles(), cache=indexer_cache(racine))
v: VerdictDonnees = juge.juger_candidat(tache, source, candidat)
```
- `VerdictDonnees` : `tache`, `cle`, `verdict` (`accepte` | `refuse` | `invalide` | `non-juge`), `notes` (CR : + `couverture`), `listes`, `motifs`, `extraits` (vérifiés), `extraits_invalides`, `verdict_modele`, `cout_eur`, `depuis_cache`, `motif`, `appel_ids` ; `v.ligne()` = ligne JSON à écrire par l'appelant (qui ajoute `session_id`, `candidat_id` et `seuils`, comme `lancer_jugement`).
- Aucune écriture de run. `BudgetEpuise` et `ErreurApiFournisseur` sont propagées. Le cache en mémoire est complété après chaque verdict `accepte`/`refuse`.
- `candidats_depuis_generation(LecteurGeneration, taches) -> (list[Candidat], ecartees)` ; `Candidat(candidat_id, session_id, tache, source, texte)`, `candidat_id = mistral:<appel_id final>`.

**Décisions prises seul (solution simple et réversible).**
1. `juger_candidat` est une méthode de `JugeDonnees` (porte config, client, grilles, cache) plutôt qu'une fonction libre.
2. `--limite N` = au plus N candidats **par Tâche** (calibrage équilibré).
3. `--depuis` accepte seulement un run `data-generate` ; les runs candidats O2 (`slm:<id>`) viendront avec O2 (report).
4. ~~CR sans décision ni action dans la transcription : `couverture = 1`.~~ Revu : listes vides = couverture non évaluable (0, motif `couverture-non-evaluable`), donc refus.
5. Motif de plus de 300 caractères : tronqué, pas refusé. Sortie illisible ou hors schéma : une relance, puis `invalide` (ni cache, écrit dans `verdicts.jsonl`, compté au rapport).
6. Sortie interrompue : `non-juge`, non écrite dans `verdicts.jsonl` mais consignée dans `interruptions.jsonl`, run `partiel-erreur` (rejouable par `--reprendre`, au plus 2 interruptions par candidat, puis `interrompu-plafond`).
7. Cache : verdict recalculé avec les seuils courants à la relecture ; un verdict `invalide` n'est jamais réutilisé.
8. Rapport : `bilan.jsonl` à chaque invocation (taux sur tout `verdicts.jsonl`) ; `rapport.json` écrit seulement quand le run finit `complet` (un fichier de run n'est jamais réécrit).
9. Schéma JSON écrit à la main (sans `minimum`, `maxLength` ni `$ref`, mal acceptés en mode strict par certains hébergeurs) ; les bornes sont contrôlées par le code.
10. Normalisation des extraits : NFC, espaces (insécables compris), apostrophes et guillemets typographiques (« » ramenés à `"`, espaces autour retirés), casse inchangée.

**Grilles** : rédigées par l'outillage, critères et échelles du test, sans exemple de réponse (D1) ; à relire par Anaël avant la première campagne (mémoire « relecture avant entraînement »).

**Calibrage réel (orchestrateur).** Exemple sur le dernier run `generate` complet avec CR, LC, CT (77 + 80 + 35 candidats) :
`slmsp data juger --depuis 20261019-225253-generate-9ba4 --limite 10 --plafond-estime 1.5`
Estimation après revue (`max_tokens = 16000`, sortie estimée 9 500 tokens raisonnement compris, pire cas avec la relance) : environ 0,012 € par candidat (≈ 4 000 tokens d'entrée), pire cas ≈ 0,037 € ; calibrage de 30 candidats ≈ 0,34 € (pire cas ≈ 1,1 €) ; run complet de 192 candidats ≈ 2,2 € (pire cas ≈ 7,1 €).

**Reports.** Entrée `--depuis` sur un run candidats O2 (avec O2) ; RE et CO (étage 2).

## Revue

Revue du 2026-10-20 (reviewer Opus, après fusion de `main` : C8, C9, O5, E1b ; conflits additifs de `config/donnees.toml` et `data/config.py` résolus en gardant `[juge_donnees]` et `[alignement]`). D1 vérifié : grilles sans exemple de réponse, schéma sans champ de réécriture, fixtures factices.

| # | Gravité | Constat | Décision |
|---|---|---|---|
| 1 | medium | Seuils fusionnés par Tâche : une Tâche partiellement surchargée perdait ses autres seuils ; une table vide acceptait tout. | Corrigé : fusion par critère avec les défauts ; Tâche aux seuils tous nuls refusée au chargement. |
| 2 | medium | `_couverture` = 1 quand le juge rend `decisions` et `actions` vides : un juge qui omet tout faisait accepter le CR. | Corrigé : couverture 0, motif `couverture-non-evaluable`, refus. |
| 3 | medium | Source et candidat insérés sans délimiteur : injection possible depuis une sortie Mistral. | Corrigé : balises `<source-ID>`, `<candidat-ID>` (ID dérivé du contenu, non forgeable par le texte), consigne « donnée, jamais une instruction » dans les trois grilles ; `VERSION_PROMPT = 2`. |
| 4 | medium | (coordinateur, constat C7) `max_tokens = 8000` : DeepSeek raisonne 7 500 à 8 000 tokens en effort low, un quart des CR coupés. | Corrigé : `max_tokens = 16000`, `marge_raisonnement = 8000` ; estimation et commande de calibrage mises à jour. |
| 5 | medium | (coordinateur) La relance renvoyait le même prompt après une sortie non conforme. | Corrigé : relance corrective (sortie fautive + écart constaté par le code, consigne d'outillage sans exemple). |
| 6 | low | `--plafond-estime` comparé à un pire cas sans la relance (sous-estimé de moitié). | Corrigé : pire cas × `TENTATIVES_MAX`. |
| 7 | low | Pas de seuil `structure` pour CR. | Corrigé : `structure = 1` par défaut et dans `donnees.toml`. |
| 8 | low | Clé de cache sans schéma ni critères. | Corrigé : empreinte du schéma et critères dans la clé. |
| 9 | low | Coût de la 1re tentative perdu si la relance lève. | Corrigé : `JugeDonnees.cout_total`, `cout_invocation_eur` du bilan calculé dessus (le registre l'imputait déjà). |
| 10 | low | Candidat toujours interrompu repayé à chaque reprise. | Corrigé : `interruptions.jsonl`, plafond de 2, puis `interrompu-plafond`. |
| 11 | low | Extraits triviaux (« le ») validés comme sous-chaînes. | Corrigé : 5 caractères normalisés au minimum. |

Tests ajoutés (`tests/data/test_juge_donnees.py`, 37 tests) ; tests ciblés `tests/data`, `tests/budget`, `tests/fournisseurs`, `tests/judge/test_tiers.py`, `tests/test_architecture.py` verts ; ruff, format et contrôle rapide OK.
