# Revue de code, lot 3a : socle de l'epic 1

- **Date** : 2026-10-12
- **Cible** : `3431c35..nuit/2026-10-12`, restreinte à `src/slmsp/core/` (hors `texte.py`, `items.py`, `gabarits.py`), `src/slmsp/budget/`, `src/slmsp/net/`, `src/slmsp/cli/__init__.py` et `src/slmsp/cli/budget.py` (35 fichiers, 4 564 lignes, tests hors diff).
- **Specs** : stories 1.1 à 1.5, contexte de l'epic 1, consignes de nuit.
- **Relecteurs** : Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor. Aucun n'a échoué.
- **Bilan** : 1 décision (tranchée), 5 correctifs (dont 1 issu de la décision), 0 report, 46 constats rejetés (52 constats bruts).
- **Découpage du lot 3** :
  - 3a : socle de l'epic 1 (ce rapport) ;
  - 3b : `fetch/`, `inference/` et `cli/fetch.py` (stories 2.1, 2.2 et 8.1) ;
  - 3c : `core/items.py`, `core/gabarits.py` et `cli/index.py` (stories 5.1, 9.2 et 2.3) ;
  - lot 4 : `cli/mcp.py`.
- **Hors lot** : juges et Mistral (lot 1), évaluation et `core/texte.py` (lot 2).

Aucun constat ne bloque la fusion. Les relecteurs n'ont trouvé aucun défaut grave dans le socle : registre de budget, passerelle réseau, runs immuables et lecteur contrôlé tiennent leurs critères d'acceptation. La seule question de fond porte sur la notion de campagne du registre de budget (D1). Elle était restée « à confirmer par Anaël » dans le journal de nuit (`journal-decisions-nuit.md:366`).

## Décision (tranchée par Anaël le 2026-10-12)

**D1 → option 2 : ancrer la campagne dans la base.** Le code devient le correctif P5.

- [x] **D1. Un changement de `campagne_id` ou de plafond, dans n'importe quelle copie de travail, remet de fait le budget à zéro.** Story 1.5, D1.6, AD-5. Sources : Acceptance Auditor, Blind Hunter.
  - **Constat** : `RegistreBudget` et `releve()` lisent les plafonds et le `campagne_id` dans `config/budgets.toml` de la copie de travail courante (`charger_budgets()`). Ensuite, `_totaux` filtre sur ce `campagne_id` (`src/slmsp/budget/registre.py:213`). La base ne garde ni les plafonds ni l'historique des campagnes.
  - **Conséquences** :
    - un worktree qui modifie `campagne_id` (même sans commit) repart de 0 € dépensé sur la base partagée de la machine, sans laisser aucune trace dans `budget.sqlite` ;
    - un lot batch encore ouvert sous l'ancienne campagne ne compte plus dans les totaux de la nouvelle (Blind Hunter).
  - **Pourquoi c'est une décision** : la spec 1.5 fait de `campagne_id` le moyen voulu de démarrer une nouvelle campagne. Le triage de nuit a rejeté le constat comme « décision humaine sur un fichier versionné », mais en le laissant à confirmer. Les budgets durs de D1.6 (Mistral 30 €, Anthropic 10 €) sont-ils par campagne ou pour tout le projet ? Trois voies sont possibles :
    1. **Confirmer l'existant** : une campagne = un budget, et changer `campagne_id` est un acte humain assumé. On le documente dans `budgets.toml` et dans le rapport, sans toucher au code.
    2. **Ancrer la campagne dans la base** : à la première réservation d'une campagne, le registre inscrit ses plafonds dans une table `campagnes`. Il refuse ensuite deux cas : un plafond différent pour la même campagne, et une nouvelle campagne tant qu'un lot de l'ancienne reste ouvert. Les changements restent possibles, mais ils laissent une trace et ne peuvent plus être silencieux.
    3. **Plafonds globaux** : les totaux de contrôle portent sur toutes les campagnes. `campagne_id` ne sert plus qu'au relevé, et D1.6 devient un plafond de projet, sans aucune remise à zéro possible.

## Correctifs

- [x] **P1. Le refus explicite du cache des verdicts vise un fichier qui n'existe pas** [`src/slmsp/core/artefacts.py:60`]. Story 1.3, critère 5. Source : Acceptance Auditor.
  - **Constat** : `NOM_CACHE_VERDICTS` vaut `cache-verdicts.sqlite`, alors que le Juge écrit `SLMSP_VAR_DIR/verdicts.sqlite` (`src/slmsp/judge/cache.py:39`). Les tests (`tests/core/test_lecteur.py:45`, `:101`, `:131`) vérifient le refus sur ce faux nom. Le vrai cache n'est refusé à `data` et `train` que parce qu'il n'est pas dans la liste d'accès. Le garde-fou explicite exigé par la spec ne protège donc rien.
  - **Correctif** : passer la constante à `verdicts.sqlite`. Mettre à jour les trois tests. Ajouter une règle à `tests/test_architecture.py` (ou un test) qui vérifie l'égalité avec `slmsp.judge.cache.NOM_CACHE`, puisque `core` ne peut pas importer `judge`.
- [x] **P2. Deux branches de `releve()` ne sont pas testées : version de schéma inattendue et table `reservations` absente** [`src/slmsp/budget/registre.py:254`]. Story 1.5, critère 11. Source : Verification Gap (mutation démontrée : supprimer la ligne 254, ou remplacer `connexion if table else None` par `connexion` à la ligne 258, laisse tous les tests verts).
  - **Correctif** : ajouter deux tests à `tests/cli/test_budget.py`.
    - Après `PRAGMA user_version = 99`, `budget etat` sort en code 1 avec « version de schéma ».
    - Sur une base SQLite valide mais vide, `budget etat` réussit avec des sommes nulles et laisse le fichier inchangé.
- [x] **P3. Aucun test ne fait échouer le journal dans les transports gardés** [`src/slmsp/net/transport.py:222`]. Story 1.4. Source : Verification Gap (mutation démontrée : supprimer `reponse.close()`, ou avaler l'échec de `consigner(..., "envoyee")`, laisse tous les tests verts).
  - **Correctif** : ajouter à `tests/net/test_journal.py` un test paramétré (synchrone et asynchrone), avec un journal dont `inscrire` lève et `httpx2.MockTransport`. Il vérifie trois points :
    - l'erreur du journal remonte à l'appelant ;
    - la réponse interne est fermée ;
    - dans le cas `echouee`, l'exception du transport reste dans la chaîne (`__context__`).
- [x] **P4. Aucun test ne vérifie que `Releve.en_dict` supprime `-0.0`** [`src/slmsp/budget/registre.py:119`]. Story 1.5. Source : Verification Gap (mutation démontrée : retirer `+ 0.0` laisse tous les tests verts).
  - **Correctif** : ajouter `test_en_dict_sans_zero_negatif` à `tests/budget/test_registre.py`. Le test construit un `LigneEtat` avec `reste_eur = -1e-12`, puis vérifie que `json_canonique(releve.en_dict())` ne contient pas `-0.0`.

- [x] **P5. Ancrer chaque campagne et ses plafonds dans `budget.sqlite`** [`src/slmsp/budget/registre.py:276`]. Story 1.5, D1.6. Issu de D1 (option 2).
  - **Correctif** :
    - Passer le schéma en version 2. Ajouter une table `campagnes` (`campagne_id` en clé, `plafonds` en JSON canonique des postes et sous-postes, `cree_le`). Migrer une base en version 1 sans toucher aux lignes existantes.
    - À l'ouverture, dans la transaction `BEGIN IMMEDIATE` de `RegistreBudget.__init__`, traiter les deux cas suivants.
    - **Campagne inconnue** : refuser tant qu'un lot d'une autre campagne est encore `reservee` (`ConfigurationInvalide`, avec les `batch_id` cités). Sinon, inscrire la campagne et ses plafonds.
    - **Campagne connue** : refuser tout plafond différent de celui inscrit (`ConfigurationInvalide`, qui cite la clé et les deux valeurs). Pour changer un plafond, il faut changer de campagne.
    - Une base existante qui contient déjà des réservations de la campagne courante est ancrée sur la config lue à la migration.
    - `releve()` reste en lecture seule : il signale un écart entre `budgets.toml` et les plafonds ancrés, sans rien écrire.
  - **Tests** : ancrage à la première ouverture, plafond modifié refusé, nouvelle campagne refusée tant qu'un lot reste ouvert puis acceptée après collecte, migration d'une base en version 1, écart signalé par `budget etat`.

## Reports

Aucun.

## Rejetés

Sources : BH Blind Hunter, ECH Edge Case Hunter, VG Verification Gap, AA Acceptance Auditor.

1. **Le « reste » du relevé ne déduit pas la marge, et rien ne vérifie que la marge reste sous chaque plafond** (BH, AA). Déjà tranché au triage de la 1.5 (g) : la marge est affichée dans l'en-tête de `budget etat`. Une marge supérieure à un plafond est un cas `low`, que la config actuelle (0,50 € face à 5 € au plus petit plafond) n'atteint pas.
2. **Les orphelines ne sont régularisées qu'à l'ouverture du registre** (BH). C'est la spec 1.5 (« à l'ouverture »). L'effet est prudent : le budget est sous-utilisé, jamais dépassé.
3. **Lot ouvert d'une campagne précédente** (BH). Repris dans D1.
4. **Aucune commande ne liste les lots ouverts** (BH). AD-26 demande une relecture par le programme, et le Juge relit les lots avant toute relance (`src/slmsp/judge/claude.py:357`, `:362`). Rien ne l'exige de la CLI.
5. **`executer_avec_relances` relance sans pause** (BH, ECH). Seul appelant : `judge/claude.py:645`, avec une seule tentative. Aucune relance n'a donc lieu aujourd'hui.
6. **Un échec du journal transforme un appel facturé en échec** (BH). `low` : le registre compte alors le pire cas (prudent), et l'appelant ne fait qu'une tentative. Échouer fermé respecte « une entrée par requête » (AD-4). Le trou de test est repris en P3.
7. **Le sens des compteurs de `UsageTokens` n'est pas documenté, d'où un risque de double comptage** (BH). `false` : Claude reprend `input_tokens`, qui exclut le cache, et les compteurs de cache à part (`judge/claude.py:222`). Mistral ne reprend que `prompt_tokens` et `completion_tokens` (`mistral/client.py:184`).
8. **`annuler_lot` ne signale pas un dépassement** (BH, ECH). `low` : le montant réel est bien compté, et seul le drapeau `motif` manque. Le correctif changerait le format du motif.
9. **`reprendre` et `terminer` ne protègent pas contre deux écrivains** (BH, ECH). `low`, comme au lot 2 (n° 20) : un seul opérateur, et la règle « un seul écrivain » est documentée.
10. **`valider_conversation` accepte des `tool_calls` sans réponse et un message `tool` qui ne suit pas son appel** (BH, ECH). `low` : c'est le Harnais qui construit ces conversations, et le correctif ajoute des règles au validateur.
11. **`NoteCritere.note` accepte NaN et n'a pas de bornes** (BH). `maybe-false` qui ne serait que `low` : les notes viennent d'une sortie du Juge validée par son schéma (lot 1). Une NaN échouerait bruyamment à l'écriture (`json_canonique`, `allow_nan=False`).
12. **`ManifesteIndex` et `ManifesteJeu` ne vérifient pas tous leurs invariants (clés de `fichiers`, `nb_items` contre la somme de `composition`, doublons d'échantillons)** (BH, ECH). `low` : le code qui calcule ces valeurs écrit aussi ces manifestes, en une seule fois.
13. **`_est_secret` laisse passer `*_PASSWORD`, `*_KEY`, `*_PAT`…** (BH, ECH). `low` : le critère de la spec (`*_API_KEY`, `HF_TOKEN`) est tenu, et les secrets du projet ne passent jamais par `os.environ`.
14. **`termes` (arguments MCP) est conservé sans durée de rétention** (BH). Le schéma du journal, `termes` compris, est fixé par AD-4. Corriger reviendrait à modifier la spec. À reprendre dans la conception de l'application (durée de conservation RGPD).
15. **La date des tarifs et du taux de change n'est jamais comparée à la date du jour** (BH). `low`, d'autant que les tarifs Mistral sont déjà marqués « à vérifier ».
16. **`releve()` crée `SLMSP_VAR_DIR` s'il manque** (BH, ECH). `low` : il crée le dossier, pas la base (critère 11). Le dossier est partagé par toute la machine.
17. **Le plafond peut être dépassé après une régularisation au coût réel** (AA). C'est le risque résiduel inscrit dans la spec 1.5 (« d'au plus l'écart d'un appel »). Le Juge n'utilise pas le cache de prompt, donc le cas `avec_cache` ne se présente pas. Corriger reviendrait à modifier la spec.
18. **Plafonds et `campagne_id` lus dans chaque copie de travail** (AA). Repris dans D1.
19. **L'imputation d'un usage n'est pas imposée à la réservation** (AA). Déjà rejeté au triage de la 1.5 (e).
20. **Cache des verdicts** (AA). Repris en P1.
21. **`Run.ajouter_jsonl` peut compléter un fichier créé par `ecrire`** (AA). `low` : il faudrait une erreur du développeur, et le correctif demande de typer les fichiers du run.
22. **`budget etat` peut créer `budget.sqlite-wal` et `-shm`** (AA). C'est un risque résiduel déjà consigné dans l'Auto Run Result de la 1.5 : le fichier principal reste identique à l'octet.
23. **Les tarifs portent sur l'identifiant exact, pas sur le « modèle résolu »** (AA). C'est une décision de conception de la 1.5 (« aucun alias en v1 »), et `ClientMistral` vérifie déjà le modèle résolu.
24. **Le profil `outillage` ignore le Mode** (AA). Le critère 3 de la 1.4 ne vise que le profil `assistant`. Déjà rejeté au triage de la 1.4 (B2).
25. **Le reste ignore la marge** (AA). Doublon du n° 1.
26. **Relances sans pause** (ECH). Doublon du n° 5.
27. **L'échec d'origine est perdu quand la réservation suivante lève** (ECH). `low` : l'unique appelant ne fait qu'une tentative.
28. **Dépassement non signalé sur un lot annulé** (ECH). Doublon du n° 8.
29. **`budget etat` avec un `SLMSP_VAR_DIR` non inscriptible** (ECH). `low`, avec le même motif que le n° 16.
30. **Une exception hors `SlmspError` affiche une trace dans la CLI** (ECH). `low` : la convention vise les `SlmspError`. Attraper `OSError` en bloc masquerait des bogues.
31. **Une `AttributeError` à l'import d'un module de sous-commande donne une trace** (ECH). `low` : il faut une dépendance incompatible, déjà couverte par le lock.
32. **Une écriture interrompue laisse un artefact tronqué définitif** (ECH). `low`, comme au lot 2 (n° 25) : il faut un disque plein, et `verifier_espace` existe.
33. **Un arrêt brutal entre `mkdir` et l'écriture de `run.json` laisse un run illisible** (ECH). `low`, même motif. Le run reste ignoré : `ouvrir_run` lève `ManifesteInvalide`.
34. **Une entrée absente de `entrees` lève `FileNotFoundError` brute** (ECH). `low` : c'est une erreur d'appel.
35. **Deux reprises concurrentes** (ECH). Doublon du n° 9.
36. **`_est_secret`** (ECH). Doublon du n° 13.
37. **Un `.env` encodé avec BOM rend la première clé introuvable** (ECH). `false` : python-dotenv retire le BOM. Vérifié : `﻿MISTRAL_API_KEY=abc` est lu sous la clé `MISTRAL_API_KEY`.
38. **`tool_calls` sans réponse** (ECH). Doublon du n° 10.
39. **Une simulation `erreur_http` sans `statut` est admise** (ECH). `false` : le statut est facultatif par conception (`{type, statut?}`), et `mcp/bac_a_sable.py:210` passe `statut=None` à `ErreurHttp`.
40. **Chemins de `ManifesteJeu` qui ne diffèrent que par la casse ou un point final** (ECH). `low` : ces chemins sont produits par le gel, pas saisis à la main.
41. **`nb_items` contre la somme de `composition`** (ECH). Doublon du n° 12.
42. **NaN dans `ResultatMesure` et `Scores`** (ECH). `low` : l'échec est bruyant à l'écriture (`allow_nan=False`), jamais silencieux.
43. **`gguf.depot` et `depot_hf` qui ne diffèrent que par la casse** (ECH). `low`.
44. **Un suffixe multi-locataire (`github.io`, `gouv.fr`) ouvrirait tous ses sous-domaines** (ECH). `false` sur la configuration : les suffixes sont `huggingface.co`, `hf.co` et `githubusercontent.com`, et un TLD seul est refusé.
45. **Un chemin encodé en pourcentage contourne la restriction de chemin** (ECH). `low` : seule la règle `conditions-mistral` restreint un chemin, en GET seul sur `legal.mistral.ai`, et l'hôte reste fixé.
46. **`analyser_url` lève `AttributeError` sur un argument qui n'est pas une URL** (ECH). `false` : tous les appelants passent une chaîne ou `request.url`.
47. **L'échec de journalisation `echouee` remplace l'exception réseau** (ECH). `low` : l'exception d'origine reste dans la chaîne (`__context__`), et l'avaler casserait « une entrée par requête ». Le trou de test est repris en P3.
48. **Le transport asynchrone écrit en SQLite de façon bloquante** (ECH). `low` : il s'agit d'une insertion courte par requête, et la contention est rare.

(48 lignes, dont 2 renvois vers D1 et 2 vers P1 et P3. Constats bruts : 16 BH, 24 ECH, 3 VG, 9 AA, soit 52. Il en reste 46 rejetés une fois retirés les 6 retenus en D1 et P1 à P4 : BH 3, AA 2, AA 4, VG 1, VG 2 et VG 3.)

## Application des correctifs (2026-10-12)

Les 5 correctifs sont appliqués. `ruff check` et `ruff format --check` passent, et `pytest` donne 3 016 succès et 95 sauts, sans aucun échec.

- **P1** :
  - `NOM_CACHE_VERDICTS` vaut `verdicts.sqlite` (`src/slmsp/core/artefacts.py`).
  - Les tests du lecteur vérifient le motif « cache des verdicts » pour `data` comme pour `train`.
  - Le nouveau test `test_nom_du_cache_verdicts_aligne_sur_le_juge` garde la constante alignée sur `slmsp.judge.cache.NOM_CACHE`.
- **P2** : deux tests de `tests/cli/test_budget.py` couvrent la version de schéma 99 (code 1, sans trace, fichier inchangé) et une base valide sans table (sommes nulles, fichier inchangé).
- **P3** : deux tests paramétrés (synchrone et asynchrone) de `tests/net/test_journal.py` couvrent un journal en panne.
  - Après l'envoi, l'erreur remonte et la réponse est fermée.
  - Sur un échec réseau, l'exception d'origine reste en `__context__`.
  - Contrôle par mutation : quand on retire `reponse.close()` et `await reponse.aclose()`, les deux tests échouent.
- **P4** : `test_en_dict_sans_zero_negatif` (`tests/budget/test_registre.py`).
- **P5** :
  - Le schéma de `budget.sqlite` passe en version 2, avec une table `campagnes`. Les versions 0 et 1 sont migrées sans réécrire `reservations`.
  - `RegistreBudget.__init__` ancre la campagne. Il refuse un plafond modifié ou une nouvelle campagne tant qu'un lot d'une autre campagne reste ouvert (`ConfigurationInvalide`). Une campagne qui a déjà des réservations est ancrée telle quelle.
  - `Releve` porte `ecarts`, que `budget etat` affiche en texte et en JSON (clé `ecarts`, liste vide par défaut).
  - Tests : ancrage, deux plafonds modifiés refusés, nouvelle campagne avec un plafond différent permise, lot ouvert puis collecte, migration d'une base en version 1, écart signalé par la CLI.
  - `test_lots_ouverts_toutes_campagnes` inscrit désormais les deux campagnes avant le lot.
  - Contrôle sur la machine : `slmsp budget etat` relit le vrai registre de la campagne `nuit-2026-10-12`, encore en version 1. Il sera migré à la prochaine ouverture d'un `RegistreBudget`, et ancré sur les plafonds actuels de `budgets.toml`.
