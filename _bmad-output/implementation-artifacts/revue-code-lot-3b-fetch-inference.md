# Revue de code, lot 3b : téléchargeur et inférence

- **Date** : 2026-10-13
- **Cible** : `3431c35..HEAD` (`a32093f`), restreinte à `src/slmsp/fetch/`, `src/slmsp/inference/` et `src/slmsp/cli/fetch.py` (13 fichiers, 3 854 lignes, tests hors diff).
- **Specs** : stories 2.1, 2.2 et 8.1, contexte de l'epic 2, consignes de nuit (sections du 2026-10-13).
- **Relecteurs** : Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor. Aucun n'a échoué.
- **Bilan** : 1 décision (tranchée provisoirement, à confirmer par Anaël), 5 correctifs, 1 report (plus 1 relevé pendant l'application), 46 constats rejetés (58 constats bruts).
- **Run** : sans humain. Chaque choix suit « la solution la plus simple et la plus réversible ».
- **Hors lot** : socle de l'epic 1 (lot 3a) ; `core/items.py`, `core/gabarits.py` et `cli/index.py` (lot 3c) ; `cli/mcp.py` (lot 4).

Aucun constat ne bloque. Le téléchargeur et l'inférence tiennent leurs critères d'acceptation : l'Acceptance Auditor retrouve dans le code les 22 critères des trois stories et toutes les lignes de leurs matrices. Le seul défaut de code est un écart de chemin du GGUF entre `fetch` et `ServeurLlama` (P1). Il est latent, car aucun TOML actuel ne range son GGUF dans un sous-dossier. Une bonne part des constats répète des points déjà tranchés au triage des stories 2.1, 2.2 et 8.1. Ils sont rejetés avec un renvoi à ce triage.

## Décision (tranchée provisoirement, à confirmer par Anaël)

- [ ] **D1. `slmsp fetch modeles` lance `llama-server`, alors que le contexte de l'epic 2 dit « `fetch` ne lance jamais de binaire llama.cpp ».** Stories 2.1 et 8.1, AD-6. Source : Acceptance Auditor.
  - **Constat** : `cli/fetch.py` `_modeles` appelle `_controler`, puis `verifications.verifier_serveur`, qui démarre `ServeurLlama` pour tout slug de génération (`--candidats` ou slug explicite). Seul `--sans-serveur` l'évite.
  - **Pourquoi c'est une décision** : la spec 8.1 exige ce contrôle (Boundaries : « `llama-server` n'est lancé que par `ServeurLlama`, en variante `cpu` »). La règle de l'epic, écrite pour la 2.1, n'a pas été amendée, et les deux textes se contredisent. AD-6 (un seul lanceur) reste tenu : c'est `ServeurLlama` qui lance. Deux voies sont possibles :
    1. **Confirmer l'existant** : le contrôle `serveur` de la 8.1 est une exception assumée à la règle de l'epic, et on amende `epic-2-context.md` à la prochaine régénération.
    2. **Sortir les contrôles de `fetch`** : une commande distincte (par exemple `slmsp modeles verifier`) lance le serveur, et `fetch` redevient un pur téléchargeur.
  - **Choix provisoire** : option 1, sans aucun changement de code. C'est la voie la plus simple et la plus réversible. Les documents de planification ne sont pas modifiés (consignes, règle 6).

## Correctifs

- [x] **P1. Le GGUF est rangé sous un chemin et cherché sous un autre quand `gguf.fichier` désigne un sous-dossier** [`src/slmsp/inference/serveur.py:393`]. Stories 2.1, 2.2 et 8.1. Sources : Blind Hunter, Edge Case Hunter, Verification Gap (écart de test et défaut d'origine), Acceptance Auditor.
  - **Constat** :
    - `fetch modeles` écrit le GGUF sous `gguf/<nom de base>` (`fetch/modeles.py:53`, `PurePosixPath(chemin).name`), et `verifier_modele` le lit au même endroit (`fetch/verifications.py:530`).
    - `ServeurLlama.gguf` joint la valeur complète : `gguf/<sous-dossier>/<nom>`.
    - Le schéma admet un `/` (`test_gguf_d_un_autre_depot` valide `"q/b.gguf"`). Un tel modèle se télécharge bien, puis le serveur refuse de démarrer (« GGUF absent ») et le contrôle `serveur` l'écarte pour une raison de chemin.
    - Le triage de la 8.1 l'avait rejeté comme « antérieur ; aucun TOML concerné ». Quatre relecteurs le relèvent ici, et le correctif est direct.
  - **Correctif** : `ServeurLlama.gguf` prend `PurePosixPath(config.gguf.fichier).name`. Nouveau test `test_gguf_en_sous_dossier_meme_chemin_pour_fetch_controles_et_serveur` (`tests/fetch/test_verifications.py`) : il vérifie que la destination de `fetch`, le chemin du serveur et le GGUF lu par les contrôles coïncident.
- [x] **P2. Le chemin du journal du serveur est perdu justement quand le démarrage échoue** [`src/slmsp/inference/serveur.py:502`]. Story 8.1 (matrice, ligne « Serveur »). Sources : Blind Hunter, Acceptance Auditor.
  - **Constat** : `ServeurLlama._journal` n'était renseigné qu'après un `/health` réussi. Dans la branche d'échec de `verifier_serveur`, `getattr(serveur, "journal")` valait donc `None`. Le cas est concerné quand le serveur meurt au démarrage, ou n'est pas prêt après 180 s, c'est-à-dire précisément quand le journal sert. `controles.jsonl` inscrivait `"journal": null`, et le chemin ne survivait que dans le texte de l'exception.
  - **Correctif** : le journal est retenu dès qu'il est choisi, avant le lancement. Les deux tests de démarrage raté de `tests/inference/test_serveur.py` vérifient que `instance.journal` désigne le fichier, et pour le processus mort, qu'il contient sa sortie.
- [x] **P3. Aucun test ne couvre l'export d'un template identique quand `chat_template_force = true`** [`src/slmsp/fetch/verifications.py:393`]. Story 8.1. Source : Verification Gap.
  - **Constat** : simplifier la ligne 393 en `if identiques:` laisserait tous les tests verts. `ServeurLlama` refuserait alors de démarrer (« chat template forcé absent »), et le modèle serait écarté avec un motif trompeur.
  - **Correctif** : `test_template_identique_avec_force_exporte` (statut `ok`, mention « superflu », `issue_export = cree`, fichier écrit).
- [x] **P4. Aucun test ne vérifie que `compter_tokens` transmet `chat_template_kwargs` à `/apply-template`** [`src/slmsp/inference/client.py:214`]. Story 2.2. Source : Verification Gap.
  - **Constat** : supprimer les lignes 214 à 216 laisserait tous les tests verts. Pour SmolLM3 (`enable_thinking = false`), le compte de tokens porterait alors sur un autre rendu que celui de la génération, et le découpage des comptes rendus longs (Harnais, story 4.4) reposerait sur un budget faux.
  - **Correctif** : `test_compter_tokens_transmet_les_kwargs` et `test_compter_tokens_sans_kwargs` (`tests/inference/test_client.py`).
- [x] **P5. Aucun test n'exerce les contrôles de type de `EntreePid.depuis_dict`** [`src/slmsp/inference/processus.py:237`]. Story 2.2. Source : Verification Gap.
  - **Constat** : le seul test d'entrée illisible écrit du JSON invalide, qui échoue avant `depuis_dict`. Retirer le contrôle des entiers laisserait passer `{"pid": "12"}` jusqu'à `psutil.Process("12")`, qui lève une `TypeError` non rattrapée. Une seule entrée corrompue ferait alors échouer tout `ServeurLlama.demarrer`.
  - **Correctif** : `test_nettoyer_entree_mal_typee` (4 cas paramétrés) et `test_nettoyer_entree_incomplete` (`tests/inference/test_processus.py`). Chaque entrée finit en `illisible` et son fichier est retiré.

## Reports

Consignés dans `deferred-work.md` (section du lot 3b).

- **W5. `fetch llamacpp` et `ServeurLlama` ne regardent pas le même `vendor/`** [`src/slmsp/fetch/llamacpp.py:72`, `src/slmsp/inference/serveur.py:73`]. Source : Blind Hunter.
  - **Constat** : `fetch llamacpp` écrit sous `<--racine ou racine du projet>/vendor`, alors que le serveur lit `SLMSP_VENDOR_DIR` en priorité. Dans un worktree où `SLMSP_VENDOR_DIR` est défini, un `fetch llamacpp` lancé sans `--racine` retélécharge le tag dans le worktree, et le serveur continue de lire l'autre copie. `models/` suit déjà `SLMSP_MODELS_DIR` dans les deux sens.
  - **Motif du report** : aligner `fetch` sur `dossier_vendor()` change le sens de `--racine` pour `vendor/`. C'est un choix d'interface, sans urgence, puisque les consignes imposent `--racine` sur le dépôt principal.
- **W6. Même écart que P1 dans `evaluation/modele_ref.py:74`.** Il a été relevé pendant l'application des correctifs, et non par un relecteur. Le fichier est hors cible (lot 2).

## Rejetés

Sources : BH Blind Hunter, ECH Edge Case Hunter, VG Verification Gap, AA Acceptance Auditor.

1. **Les pannes d'environnement (llama.cpp absent, SHA d'un binaire, port pris) sont présentées comme des modèles écartés** (BH). `low` : le motif imprimé et consigné cite l'exception (`ConfigurationInvalide : fichier llama.cpp absent…`), et le code 1 reste juste. Les distinguer ajouterait une catégorie de statut.
2. **Le compteur d'échecs n'est pas remis à zéro après une reprise qui progresse** (BH). Déjà rejeté au triage de la 2.1 : 6 essais suffisent, et les liens instables sont rares.
3. **Un serveur qui répond 200 à une reprise bloque toutes les relances** (BH). Déjà différé dans le frontmatter de la 2.1 (`medium`, non vérifié : support de `Range` par codeload).
4. **Les poids ne sont pas rangés par révision** (BH). La disposition `models/<slug>/{hf,hf-bf16,gguf}/` est fixée par le contexte de l'epic 2. Un changement de révision est un acte humain, et le refus `ShaInvalide` est le comportement voulu (rien n'est écrasé).
5. **Un GGUF non épinglé déjà présent est consigné avec la révision `main`** (BH). Déjà différé par la 2.1. La 8.1 a ajouté `gguf.revision`, et tous les candidats l'épinglent.
6. **`AccessDenied` est traité comme « processus disparu »** (BH). Déjà rejeté au triage de la 2.2 : seuls nos propres processus, du même utilisateur, sont inscrits.
7. **Chargeurs de config et contrôle du slug dupliqués entre `serveur.py` et `fetch/config.py`** (BH). C'est voulu : `inference` (couche 2) ne doit pas importer `fetch` (couche 4), selon le Code Map de la 2.2.
8. **Le diff ne contient ni tests, ni branchement CLI, ni dépendances** (BH). `false` : la cible exclut les tests (`tests/fetch/`, `tests/inference/`), `fetch` est déclaré dans `cli/__init__.py:28`, et `psutil`, `numpy` et l'extra `fetch` sont épinglés dans `pyproject.toml`.
9. **Une coupure de flux perd sa cause** (BH). Déjà rejeté au triage de la 2.2. La matrice impose `Fin(interrompue)`.
10. **`run.json` ne porte ni le SHA du GGUF ni le build réel** (BH). Déjà rejeté au triage de la 2.2 (décision 7). Le tag est inscrit, et la config archivée porte le SHA.
11. **Un binaire non listé dans `binaires` est lancé sans contrôle** (BH). Déjà rejeté au triage de la 2.2. `config/llamacpp.toml` liste bien `llama-server` pour `cpu` et `cuda` (vérifié par l'AA).
12. **`template_hf` plante sur un `tokenizer_config.json` qui n'est pas un objet** (BH). Déjà rejeté au triage de la 8.1 : les fichiers sont épinglés par SHA.
13. **Course sur le port libre** (BH). Déjà rejeté au triage de la 2.2.
14. **`fetch benchmarks` ignore `--reutiliser`, n'ouvre pas de run et sort en code `USAGE`** (BH). Déjà rejeté au triage de la 2.1 : l'interface appartient à la story 6.1.
15. **Dimension d'embedding codée en dur (1024)** (BH). `low` : seul BGE-M3 est servi en embedding, et la spec fixe 1024. Il faudrait ajouter un champ au schéma core.
16. **Fichiers temporaires (`.tmp`, `.copie-`, `.extraction-`) jamais nettoyés** (BH). Déjà rejeté aux triages des stories 2.1 et 2.2 : cas rare, rien n'est effacé par conception, et une copie tronquée échoue au SHA.
17. **Révision `main` d'un GGUF déjà présent** (VG, autre constat). Doublon du n° 5.
18. **Dépassement de flottant quand `essais` vaut 1026 ou plus** (ECH). `low` : la config versionnée fixe `essais = 6`.
19. **Contrôle d'espace groupé par ancre plutôt que par volume** (ECH). `low` : sous Windows (D2), les volumes ont chacun leur lettre. Aucun dossier monté n'est utilisé.
20. **Une destination qui est un dossier lève une erreur brute** (ECH). `low` : l'échec est bruyant, et il faut une erreur de manipulation.
21. **`.copie-` orphelin après un échec de copie** (ECH). Doublon du n° 16.
22. **Reprise refusée sur une réponse 200** (ECH). Doublon du n° 3.
23. **Membres `a` et `a/b` dans une même archive** (ECH). `low` : les archives sont épinglées par SHA (motif du triage de la 2.1).
24. **`.extraction-` orphelin** (ECH). Doublon du n° 16.
25. **Membre chiffré ou compression non gérée : `RuntimeError` brute** (ECH). `low` : archives épinglées par SHA.
26. **Marqueur d'extraction présent, cible vidée depuis** (ECH). `low` : il faut une suppression manuelle dans `vendor/`, et `verifier_binaires` échoue alors bruyamment.
27. **`assets.*.nom` avec `/` ou `..`** (ECH). Déjà rejeté au triage de la 2.1 : config versionnée.
28. **Révision `main` consignée** (ECH). Doublon du n° 5.
29. **`template_hf` sur un JSON qui n'est pas un objet** (ECH). Doublon du n° 12.
30. **`layer_types` qui n'est pas une liste** (ECH). Déjà rejeté au triage de la 8.1.
31. **`modalities` de `/props` qui n'est pas un objet** (ECH). Déjà rejeté au triage de la 8.1 : llama-server b11429 rend un objet.
32. **`chat_template_force` sans template HF : modèle écarté à tort** (ECH). `low` : aucune config ne combine `chat_template_force` et `fichiers = []`, et `ServeurLlama` échouerait déjà sur « chat template forcé absent ».
33. **Chunk SSE mal typé ou `index` nul** (ECH). Déjà rejeté au triage de la 2.2 : serveur épinglé, format relevé.
34. **Corps 200 qui n'est pas du JSON** (ECH). Déjà rejeté au triage de la 2.2.
35. **Dimension d'embedding** (ECH). Doublon du n° 15.
36. **NaN dans une entrée `pids/`** (ECH). `low` : les entrées sont écrites par `inscrire` à partir de dates psutil. Il faudrait une modification manuelle du fichier.
37. **`AccessDenied`** (ECH). Doublon du n° 6.
38. **Hors Windows, `arreter` ne tue pas les petits-enfants** (ECH). `false` : le projet vise Windows seul (D2), où le Job Object tue l'arbre (`test_arreter_tue_les_petits_enfants`).
39. **Course sur le port** (ECH). Doublon du n° 13.
40. **Un redémarrage de la même instance réutilise l'ancien journal** (ECH). `low` : aucun appelant ne redémarre une instance, et l'ajout en fin de fichier ne perd rien.
41. **Si `fermer()` lève, le serveur et le verrou GPU fuient** (ECH). `low` : la fermeture d'un client httpx ne lève pas en pratique.
42. **Template identique exporté malgré la matrice (« aucun export »)** (AA). `false` : la ligne de la matrice vise le cas sans `chat_template_force`, et l'export est exigé par `ServeurLlama` quand le forçage est actif (décision 4 de la 8.1). Le comportement est désormais fixé par P3.
43. **`exporter_template` supprime un fichier sous `models/`** (AA). Déjà accepté au triage de la 8.1 : seul le `.part` créé par ce même appel est retiré.
44. **`quantifier(variante="cuda")` ne prend pas `gpu.lock`** (AA). `low` : aucun appelant aujourd'hui, et `llama-quantize` calcule sur CPU. `verrou_gpu` n'étant pas réentrant, c'est à l'appelant (story 10.6) de le prendre.
45. **`commande_conversion` utilise un interpréteur hors du tag** (AA). Déjà rejeté au triage de la 2.2 : l'appelant passe `python=`.
46. **`net.client_local` accepte tout port, pas seulement ceux des serveurs gérés** (AA). Hors cible (`net/`, lot 3a), et c'est l'interface fixée par la 1.4.

(46 lignes. Constats bruts : 19 BH, 25 ECH, 6 VG, 8 AA, soit 58. Retenus : 12, à savoir P1 (BH, ECH, VG ×2, AA), P2 (BH, AA), P3 à P5 (VG), D1 (AA) et W5 (BH).)

## Application des correctifs (2026-10-13)

Les 5 correctifs sont appliqués (commit `fix(inference): correctifs de la revue de code du lot 3b`). `ruff check` et `ruff format --check` passent.

- **`uv run pytest`** (suite complète) : 3 033 succès, 359 sauts et 3 échecs, tous hors de la zone du lot et dus à l'environnement du worktree.
  - `test_ouvrir_juges_surcharge_le_mode` et `test_generation_sans_jeton_refusee[options1]` : les extras `judge` et `data` n'étaient pas installés dans le `.venv` du worktree. Après un `uv sync --offline --extra fetch --extra data --extra judge`, fait depuis le cache sans téléchargement, les deux tests passent.
  - `test_v1_1_export_des_changements` : `eval/revue/changements-v1.0-v1.1.jsonl` n'est pas versionné, donc absent du worktree. Ce dossier est hors du périmètre du run (consigne du 2026-10-13).
- **`tests/inference` et `tests/fetch`** : 219 succès.
- **Tests réels** (`-m integration`, avec `SLMSP_VENDOR_DIR` et `SLMSP_MODELS_DIR` sur le dépôt principal) : 6 succès en 22 s (`version` cpu et cuda, Granite 1B, `json-generique`, BGE-M3, deux instances).

- **Contrôle par mutation** :
  - Remettre le chemin complet dans `ServeurLlama.gguf` fait échouer le test de P1.
  - Retenir le journal seulement après `/health` fait échouer les deux tests de P2.
  - Les tests de P3 à P5 couvrent des branches existantes, dont les mutations sont décrites par le Verification Gap.
- **Constat en cours d'application** : `src/slmsp/evaluation/modele_ref.py:74` construit lui aussi `gguf/<gguf.fichier>` avec le chemin complet. Ce fichier est hors cible (lot 2), donc reporté (W6 de `deferred-work.md`).
- **Test instable** : `test_demarrage_rate_sante` a échoué une fois sous la charge de la suite complète. Le serveur factice n'avait rien écrit dans son journal avant l'expiration du délai de démarrage de 2 s. Seul, il passe trois fois sur trois. Le délai du test passe à 5 s.
