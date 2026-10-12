# Revue de code, lot 1 : verrous D1.1 et juges

- **Date** : 2026-10-12
- **Cible** : `3431c35..nuit/2026-10-12`, restreinte à `src/slmsp/judge/`, `src/slmsp/mistral/`, `tests/test_architecture.py` et `pyproject.toml` (14 fichiers, 4 300 lignes).
- **Specs** : stories 5.4, 5.5 et 9.2 ; AD-3 ; contexte des epics 5 et 9.
- **Relecteurs** : Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor. Aucun n'a échoué.
- **Bilan** : 11 correctifs (dont 2 issus de décisions tranchées), 0 report, 27 constats rejetés.
- **Hors lot** : évaluation (lot 2), socle de l'epic 1 (lot 3), MCP et outils d'items (lot 4).

Aucun constat ne bloque la fusion dans `main` à lui seul. Les paquets `data` et `train` sont encore vides, donc les trous des verrous D1.1 (D1, P2, P3, P4) ne sont pas exploitables aujourd'hui. Il faut les fermer avant d'écrire le code des stories 9.3 et suivantes.

## Décisions (tranchées par Anaël le 2026-10-12)

Ces deux décisions deviennent les correctifs P10 et P11 :
- **D1 → P10, contrôle à l'exécution.** Les lectures de `JournalMistral` passent par `core.artefacts.ouvrir_sqlite_lecture(chemin, lecteur)`, avec un `lecteur` obligatoire. Une règle AST interdit à `data` et `train` de nommer `USAGES_JUGE`. La docstring est corrigée.
- **D2 → P11, arrêt du run.** Un 429 arrête les appels restants du run (motif `limite-debit`), dans `claude.py` comme dans `second.py`. L'appel est réglé à 0, sans relance.

- [x] **D1. Le journal du second juge reste lisible depuis `data` et `train` (AD-24).** Story 5.5. Sources : Blind Hunter, Verification Gap.
  - **Constat** : la docstring de `src/slmsp/mistral/journal.py:8` affirme que la liste d'accès de `slmsp.core.artefacts` refuse ce journal à `data` et `train`. En pratique, `JournalMistral` lit par `ouvrir_sqlite` et ne consulte jamais `artefacts`.
  - **Conséquence** : un futur module `slmsp.data` peut appeler `journal_pour("juge-second", cfg).appels()` et lire les textes d'évaluation envoyés au juge. Aucune règle d'architecture ne le détecte.
  - **Pourquoi c'est une décision** : `data` doit lui-même lire le journal `generation`, pour le verrou 3 au build. On ne peut donc pas lui interdire tout import de `slmsp.mistral.journal`.
- [x] **D2. Un 429 (ou un 408 ou 409) est traité comme un refus définitif.** Stories 5.4 et 5.5. Sources : Blind Hunter, Edge Case Hunter.
  - **Constat** : `src/slmsp/judge/claude.py:614` et `src/slmsp/judge/second.py:215` classent tout 4xx en refus non facturé. Il n'y a ni nouvel essai ni arrêt, et l'item passe `non-juge` (`erreur-api`).
  - **Conséquence** : une rafale de limitation de débit rend une partie de la notation silencieusement non jugée. Les items seront rejugés au run suivant, sans surcoût.

## Correctifs

- [x] **P1. Échec de `batches.create` : un refus 4xx est compté au pire cas et 401/403 n'arrêtent pas la boucle** [`src/slmsp/judge/claude.py:405`]. Story 5.4. Sources : les 4 relecteurs.
  - **Constat** : le `except Exception` générique traite un 4xx confirmé (rien n'a été créé ni facturé) comme une création incertaine. Il appelle `annuler_lot` sans usage, donc au pire cas, et ne lève pas `arret_api`.
  - **Conséquence** : avec une clé révoquée, en mode batch (le mode par défaut), chaque lot suivant est réservé puis brûlé au pire cas dans le registre, jusqu'à épuisement du budget affiché, sans aucune dépense réelle.
  - **Correctif** : sur un `anthropic.APIStatusError` 4xx, appeler `annuler_lot(lot_id, UsageTokens(0, 0))`. Pour un 401 ou un 403, lever `arret_api`, puis sortir de la boucle. Garder le pire cas pour les autres exceptions.
- [x] **P2. Le jeton de preuve du Générateur peut être importé et `_appeler` appelé hors de `generateur.py`** [`src/slmsp/mistral/generateur.py:62`]. Story 9.2, AD-3 verrou 3. Source : Blind Hunter.
  - **Constat** : un `from slmsp.mistral.generateur import _JETON` suivi de `client._appeler(..., jeton=_JETON)` suffit à écrire des lignes `generation`. Aucune règle de `tests/test_architecture.py` ne l'interdit.
  - **Correctif** : ajouter une règle AST. Seuls `slmsp.mistral.generateur` et `slmsp.mistral.journal` peuvent nommer `_JETON`, et seuls `slmsp.mistral.client` et `slmsp.mistral.generateur` peuvent accéder à `._appeler`.
- [x] **P3. La règle `lecture-data/train` laisse passer les lecteurs du pipeline de données** [`tests/test_architecture.py:89`]. Story 1.1, AD-24. Sources : Blind Hunter, Edge Case Hunter.
  - **Constat** : la règle ne voit que `open`, `read_text`, `read_bytes` et `json.load`. Elle laisse passer `sqlite3.connect`, `duckdb.connect`, `duckdb.read_*`, `pyarrow.parquet.read_table`, `numpy.load`, `pickle.load` et `tomllib.load`, alors que l'extra `data` épingle `duckdb` et `pyarrow`.
  - **Correctif** : étendre `IMPORTS_LECTURE` et `ATTRIBUTS_LECTURE`, avec un cas de test pour chaque lecteur ajouté.
- [x] **P4. `eval/outils/**` échappe aux deux gardes d'imports (AD-3 verrou 1)** [`pyproject.toml:110`]. Story 1.1. Sources : Blind Hunter, Edge Case Hunter, Acceptance Auditor.
  - **Constat** : ruff y ignore TID251, et `analyser()` ne parcourt que `src/slmsp`. Un `import anthropic` ou `import mistralai` dans `eval/outils/` passerait donc ruff et `tests/test_architecture.py` sans alerte. Aucun import de ce type n'existe aujourd'hui.
  - **Correctif** : ajouter à `tests/test_architecture.py` un test qui refuse `anthropic` et `mistralai` sous `eval/outils/`.
- [x] **P5. Un échec après une réponse 200 (le SDK n'arrive pas à la lire) est journalisé sans le corps brut déjà capturé** [`src/slmsp/mistral/client.py:335`]. Story 5.5 AC 1, AD-3 verrou 3. Source : Acceptance Auditor.
  - **Correctif** : `reponse_brute=self._capture.reponse`.
- [x] **P6. Un `KeyboardInterrupt` pendant `chat.complete` laisse un appel réglé au pire cas sans ligne de journal** [`src/slmsp/mistral/client.py:335`]. Story 5.5. Source : Blind Hunter.
  - **Constat** : la condition `isinstance(exc, Exception)` saute `inscrire`, à l'encontre de la règle « tout appel laisse une ligne ».
  - **Correctif** : journaliser aussi les `BaseException`, puis relever l'exception.
- [x] **P7. Aucun test ne couvre l'appel à `valider_conversation(requete)` du Générateur** [`tests/mistral/test_generateur.py`]. Story 9.2. Source : Verification Gap, avec mutation démontrée : les 93 tests passent même quand l'appel est neutralisé.
  - **Correctif** : ajouter les cas `cle-en-plus` (message `tool` avec une clé en trop) et `reponse-en-double` (même `tool_call_id` répondu deux fois) à `test_precedent_tool_refuse`. Chacun attend `ProvenanceInvalide` et `rien_n_est_parti()`.
- [x] **P8. La garde `_lot_ouvert_au_registre` de `_achever_lot` n'est pas testée sur un lot déjà réglé au registre** [`tests/judge/test_claude.py`]. Story 5.4. Source : Verification Gap, avec mutation démontrée.
  - **Correctif** : ajouter `test_reprise_apres_crash_apres_la_collecte`. Le test provoque un crash juste après `collecter_lot`, sur `cache.changer_statut`, puis vérifie qu'à la reprise le lot finit `collecte` avec une seule ligne `regularisee` au registre.
- [x] **P9. Le coût pire cas d'une création de lot ratée n'est pas vérifié dans `cout_total_eur`** [`tests/judge/test_claude.py:320`]. Story 5.4. Source : Verification Gap, avec mutation démontrée.
  - **Correctif** : ajouter l'assertion `rapport.cout_total_eur == approx(montant_reel_eur)` dans `test_creation_de_lot_en_erreur`.

## Rejetés

1. **La clé de cache omet `max_tokens`** (BH). `low`. Avec `max_tokens = 6000` pour au plus 969 tokens observés, une troncature est improbable. Corriger invaliderait tout le cache payé.
2. **La clé de cache inclut `appels_outils`** (BH). La projection `{texte, appels_outils, sources}` est le choix d'AD-12, revu en 5.4. Corriger reviendrait à modifier la spec.
3. **Les lots ouverts ne sont pas liés à un processus** (BH). `low`. Ce constat a déjà été rejeté en 5.4 : une seule notation tourne à la fois.
4. **Deux `juger` concurrents reprennent les mêmes lots** (ECH). Même motif que le n° 3.
5. **Le nom `batch_id` a deux sens** (BH). `low`, cosmétique : la comparaison est correcte.
6. **Le verrou 1 est appliqué par paquet, pas par module** (BH). AD-3 lie le verrou au dossier `slmsp/judge/`, et `slmsp.judge.claude` est le seul import réel.
7. **Le second juge importe `anthropic` par `claude.py`** (BH). `false` : le paquet `judge` a le droit d'importer `anthropic`.
8. **`_Preparee`, `_Issue` et `_rapport` sont dupliqués entre `claude.py` et `second.py`** (BH). `low`. Le correctif serait une refonte, sans défaut constaté.
9. **`usage_budget` accepte une chaîne libre** (BH). `false` : `RegistreBudget.imputer` refuse tout usage inconnu de `budgets.toml`.
10. **La grille n'est pas contrôlée à la lecture (espace insécable, section manquante)** (BH, ECH). `low` : la grille v1 est figée dans le dépôt et a été lue sans erreur pendant la Baseline.
11. **Les items de l'échantillon absents des demandes sont ignorés en silence** (BH). `false` : `notation.py:435` ne garde exprès que les items au verdict principal valide.
12. **`echantillon` passé sous forme de `str`** (ECH). `false` : le seul appelant passe une liste.
13. **`ModeleMistralRefuse` fait perdre le rapport partiel** (BH). `low` : les verdicts sont déjà en cache item par item, et l'appel est journalisé.
14. **Le Générateur sous-réserve son budget (`ceil(chars / 3)`)** (BH). `low` : le ratio est déjà prudent pour du français.
15. **Le client dépend des hooks internes du SDK** (BH). `low` : `mistralai==3.2.0` est épinglé, et tout changement de l'attribut fait échouer bruyamment la construction.
16. **Le patch n'ajoute aucun test** (BH). `false` : les tests sont hors du lot. `tests/judge`, `tests/mistral` et `tests/test_architecture.py` passent : 430 réussis.
17. **Les limites d'un lot Anthropic (100 000 requêtes, 256 Mo)** (ECH). `false` : le jeu compte 225 items.
18. **Un lot repris non terminé rend `non-juge` des items déjà en cache** (ECH). `low` : il faut un crash puis plus de 3 erreurs de relevé à la suite, et le run suivant corrige.
19. **Un crash entre `journaliser_appel(ISSUE_JUGE)` et la mise en cache fait racheter le verdict** (ECH). `low` : fenêtre de quelques microsecondes, surcoût d'un seul appel.
20. **Un crash entre `compter_echec` et `journaliser_appel` compte l'échec deux fois** (ECH). `low` : même fenêtre.
21. **Un verdict en cache devenu illisible lève une `ValidationError` brute** (ECH). `low` : l'échec est bruyant, et aucun changement de schéma n'est prévu.
22. **Un import dynamique (`importlib`) contourne les règles d'architecture** (ECH). `low` : il faudrait un contournement délibéré.
23. **Les résultats d'un doublon ne sont plus identiques** (AA). C'est un choix de la revue 5.4 (le coût est porté une fois). Corriger reviendrait à modifier la spec.
24. **L'`effort_cle` du second juge diffère de la spec** (AA). L'écart est documenté dans l'Auto Run Result. Corriger reviendrait à modifier la spec.
25. **Le client Mistral utilise `httpx2` et non `httpx`** (AA). C'est imposé par `mistralai` 3.2.0 et documenté. Corriger reviendrait à modifier la spec.
26. **Un modèle hors liste est refusé au chargement, pas à l'appel** (AA). Le garde-fou est plus strict que la spec, sans défaut.
27. **L'ordre des étapes de `juger` diffère de la spec** (AA). Écart bénin, imposé par la règle `ItemNonJugeable` avant tout GET.

## Application des correctifs (2026-10-12)

Les 11 correctifs sont appliqués sur `nuit/2026-10-12`, sans commit pour l'instant.

- **P1 et P11** (`judge/claude.py`, `judge/second.py`) :
  - Nouvelle fonction `motif_arret(statut)` : 401 et 403 donnent `erreur-api`, 429 donne `limite-debit`.
  - `_Etat.arret` (le motif d'arrêt) remplace le booléen `arret_api`.
  - Un refus 4xx de `batches.create` est réglé à 0 par `annuler_lot(lot_id, UsageTokens(0, 0))`. Un motif d'arrêt interrompt la boucle de lots, et les items restants prennent ce motif au lieu de `budget`.
- **P2, P3, P4 et la règle de P10** (`tests/test_architecture.py`) :
  - Nouvelles règles `jeton-generateur` et `journal-juge-depuis-data/train`.
  - La table `LECTEURS_INTERDITS` résout les alias d'import : `sqlite3`, `duckdb`, `pyarrow.*`, `numpy`, `pickle`, `tomllib`, `pandas` et `slmsp.core.var.ouvrir_sqlite`.
  - `analyser_outils()` couvre `eval/outils/`.
  - Chaque nouvelle règle a ses cas fautifs synthétiques.
- **P5 et P6** (`mistral/client.py`) : toute exception, interruption comprise, laisse désormais une ligne de journal, avec le corps brut capturé s'il existe.
  - **Précision sur P5** : une réponse 200 que le SDK ne sait pas lire lève `ResponseValidationError`, une sous-classe de `MistralError`. Ce cas passait déjà par la branche `MistralError`, qui journalise le corps. Le correctif ne couvre donc que les autres exceptions survenues après la réponse.
- **P10** (`mistral/journal.py`) :
  - `JournalMistral(..., lecteur=)` et `journal_pour(..., lecteur=)` ouvrent le journal en lecture seule.
  - À l'ouverture, `chemin_autorise` est appelé : le journal du juge lève `LectureInterdite`. Ensuite, les lectures passent par `ouvrir_sqlite_lecture`, et `inscrire` est refusé.
  - La docstring est corrigée.
- **Tests ajoutés** :
  - P1 : 4 tests de refus à la création d'un lot.
  - P11 : un test 429 pour chacun des deux juges.
  - P8 : la reprise après un crash survenu après la collecte.
  - P9 : l'assertion sur `cout_total_eur`.
  - P7 : les cas `cle-en-plus` et `reponse-en-double`.
  - P6 et P5 : l'interruption journalisée, et le corps brut conservé après une réponse 200.
  - P10 : 5 tests du journal.
  - Les nouveaux tests de P1, P7 et P11 échouent sur l'ancien code (mutation vérifiée).
