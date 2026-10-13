# Revue de code, lots 3c et 4 : lecteur d'items, gabarits, CLI `index` et CLI `mcp`

- **Date** : 2026-10-13
- **Cible** : `3431c35..HEAD` (`bfceaef`), restreinte à `src/slmsp/core/items.py`, `src/slmsp/core/gabarits.py`, `src/slmsp/cli/index.py` (lot 3c) et `src/slmsp/cli/mcp.py` (lot 4). Soit 4 fichiers et 1 582 lignes ajoutées ; les tests sont hors diff.
- **Specs** : stories 5.1, 9.2, 2.3, 3.2 et 3.3, contextes des epics 2, 3, 5 et 9, consignes de nuit (sections du 2026-10-13).
- **Relecteurs** : Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor. Aucun n'a échoué.
- **Bilan** : 2 décisions (tranchées provisoirement, à confirmer par Anaël), 7 correctifs, 2 reports (W7 et W8), 34 constats rejetés (59 constats bruts).
- **Run** : sans humain. Chaque choix suit « la solution la plus simple et la plus réversible ».
- **Hors lot** : socle de l'epic 1 (lot 3a), `fetch/` et `inference/` (lot 3b, voir `revue-code-lot-3b-fetch-inference.md`).

**Aucun constat `high`, et aucun écart à D1.** L'Acceptance Auditor retrouve dans le code les critères des cinq stories pour les quatre fichiers. Sur D1, la cible ne contient que le validateur de gabarits (`core/gabarits.py`), pas les gabarits eux-mêmes. J'ai donc contrôlé les deux niveaux :
- les 11 gabarits de `config/prompts/generateur/` passent `valider_gabarit` (vérifié par exécution) et ne contiennent que des consignes et des emplacements `{nom}`, sans exemple, sans few-shot et sans amorce ; `validation.md` nomme les verdicts FIDELE et INFIDELE, mais il sert l'usage `validation` et ne produit aucune Donnée d'entraînement (accepté au triage de la 9.2) ;
- le validateur est une liste blanche solide, mais sa liste noire de mots se contournait par trois voies (P1). C'est un défaut de robustesse du garde-fou, sans gabarit fautif aujourd'hui, donc `medium`.

Les défauts retenus sont mineurs : un garde-fou D1 contournable, un jeu vide lu en silence, des erreurs JSON non agrégées, une règle RD qui ne se relit pas après un `model_dump`, un fichier d'appels refusé à cause d'un BOM, et deux trous de couverture de tests sur l'API anti-fuite.

## Décisions (tranchées provisoirement, à confirmer par Anaël)

- [ ] **D1. Faut-il durcir le mode strict avec des contrôles de cohérence ?** Story 5.1. Sources : Blind Hunter, Edge Case Hunter.
  - **Constat** : le mode strict accepte aujourd'hui, sans erreur :
    - une liste de référence vide (`criteres: []`), un objet vide (`reponse_reference: {}`) ou une liste de chaînes blanches (`decisions_reference: [""]`) hors des quatre listes de `_LISTES_NON_VIDES` ;
    - un item RD en mode `hors-ligne` ou `repli` avec `cassettes: []` ;
    - un item CO dont `nb_fautes` diffère de `len(fautes)`, ou dont les intervalles de fautes se chevauchent ;
    - un appel attendu sans cassette qui le couvre.
  - **Pourquoi c'est une décision** : chaque contrôle durcit le schéma d'un jeu déjà gelé `relu` (v1.0 et v1.1), qui doit continuer de se lire. `test_strict_listes_vides_permises` fixe en outre `cassettes: []` comme admis (choix de la 5.1). Il faudrait relire les 225 items de v1.0 et le jeu v1.1 avec chaque règle, ce qui sort du périmètre « code seul » du run.
  - **Choix provisoire** : ne rien durcir. C'est la voie la plus simple et la plus réversible. Si Anaël veut ces garde-fous, la commande à lancer est `uv run python -c "from slmsp.core.items import lire_jeu; lire_jeu('v1.1')"` après l'ajout de chaque règle, et le contrôle de `nb_fautes` est le plus sûr à commencer.
- [ ] **D2. Les références de moins de cinq mots sont-elles assez protégées contre la fuite ?** Story 5.1 et pipeline `data` (9.3). Source : Blind Hunter.
  - **Constat** : `empreintes_antifuite` donne, pour un texte de moins de `n = 5` mots, l'empreinte du tuple entier de ses jetons (comportement fixé par la 5.1, testé par `test_texte_court_empreinte_entiere`). Un candidat d'entraînement ne la retrouve que s'il produit exactement la même phrase courte comme n-gramme complet. Une réponse courte reprise dans une phrase plus longue (`elements_cles`, `points_cles_reference`, `criteres`) n'est donc pas repérée par les empreintes.
  - **Pourquoi c'est une décision** : la bonne protection dépend du comparateur de la story 9.3 (sous-chaîne, n-grammes plus courts, ou seuil sur les vecteurs). L'API ne peut pas la choisir seule.
  - **Choix provisoire** : garder le comportement actuel. Les vecteurs (`#reference`) couvrent en partie les références courtes. À trancher en 9.3, au moment d'écrire le contrôle d'anti-fuite côté `data`.

## Correctifs

- [x] **P1. La liste noire du validateur de gabarits se contournait par trois voies** [`src/slmsp/core/gabarits.py:122`]. Story 9.2 (D1.1, AD-3 verrou 6). Sources : Blind Hunter, Edge Case Hunter (×3 : constat et deux affirmations).
  - **Constat** (vérifié par exécution avant correction) :
    - un caractère de format invisible dans un mot (`exem​ple`, `few­shot`) faisait passer le gabarit ;
    - les formes pleine chasse de ``` ` ```, `>`, `{` et `}` passaient les tests de forme, qui portaient sur la ligne brute ;
    - un mot interdit coupé par un retour à la ligne (`few-` puis `shot`, `réponse` puis `type`) passait, car la recherche se fait ligne par ligne.
  - **Gravité** : `medium`. Aucun gabarit actuel n'est touché, mais c'est le garde-fou de D1, et un collage depuis une page web introduit facilement un caractère invisible ou une coupe de ligne.
  - **Correctif** : les tests de forme portent sur la ligne en NFKC ; tout caractère de catégorie Unicode `Cf` est refusé (« caractère de format invisible interdit ») ; un second passage cherche les mots interdits sur le texte aplati, et ne signale que ceux qu'aucune ligne seule ne contient (« coupé par un retour à la ligne »). Les 11 gabarits du générateur et les gabarits de Tâche passent toujours. Tests : `test_contournements_de_la_liste_noire` (9 cas) et `test_mot_entier_sur_une_ligne_n_est_pas_signale_comme_coupe` (`tests/core/test_gabarits.py`).
- [x] **P2. Un JSON trop profond ou un entier démesuré fait échouer `lire_items` par une trace brute** [`src/slmsp/core/items.py:633`]. Story 5.1. Source : Edge Case Hunter (×2 : constat et affirmation « toutes les erreurs sont rassemblées »).
  - **Constat** : `json.loads` lève `RecursionError` (imbrication) ou `ValueError` (entier de plus de 4 300 chiffres), que `except json.JSONDecodeError` ne rattrapait pas. Une seule ligne pareille faisait perdre toute la liste d'erreurs du fichier.
  - **Correctif** : ces deux exceptions sont agrégées comme une ligne illisible (`ligne N : (item) : JSON illisible (RecursionError)`). Test : `test_json_trop_profond_ou_entier_demesure_agrege` (`tests/core/test_items.py`).
- [x] **P3. Un fichier d'items vide donne un `Jeu` vide, lu sans erreur** [`src/slmsp/core/items.py:699`]. Story 5.1. Source : Edge Case Hunter.
  - **Constat** : un `items.jsonl` vide (checkout interrompu, fichier tronqué) donnait un jeu sans item. L'API anti-fuite renvoyait alors des empreintes, des vecteurs et des identifiants protégés vides : elle protégeait « rien » sans le dire. `medium`.
  - **Correctif** : `lire_jeu` lève `ItemInvalide` (« aucun item dans le fichier du jeu »). `lire_items` garde son contrat (liste vide pour un fichier vide). Test : `test_lire_jeu_fichier_vide`.
- [x] **P4. Un `RegleArgument` sérialisé ne se relit pas** [`src/slmsp/core/items.py:192`]. Story 5.1. Sources : Blind Hunter, Edge Case Hunter.
  - **Constat** (vérifié par exécution) : `model_dump()` écrit toujours `exact: null`. Relu avec `contient_un_de`, il posait `exact` dans `model_fields_set` et déclenchait « `exact` exclut `contient_un_de` ». L'export de revue évite le cas par `exclude_none=True`, mais tout autre rechargement d'un dump échouait.
  - **Contrainte** : on ne peut pas retirer `exact` du dump, car `test_model_dump_v1_0_inchange` fixe l'empreinte du dump des 225 items (clé du cache des verdicts).
  - **Correctif** : `a_exact` ne compte plus `exact: null` accolé à une liste. Le validateur et le scoreur (`evaluation/controles.py`) lisent la même propriété. Test : `test_regle_argument_relit_son_propre_dump`.
- [x] **P5. `slmsp mcp record` refuse un fichier d'appels avec BOM, et plante sur un JSON trop profond** [`src/slmsp/cli/mcp.py:84`]. Story 3.3. Sources : Edge Case Hunter, Acceptance Auditor.
  - **Constat** : le fichier était lu en `utf-8`. Windows PowerShell 5.1 (`Set-Content -Encoding utf8`, `Out-File`) écrit un BOM, ce qui donnait « JSON invalide (ligne 1, colonne 1) », message trompeur. Un JSON très imbriqué levait `RecursionError`, hors des cas rattrapés (code 2 attendu, sans trace).
  - **Correctif** : lecture en `utf-8-sig` (comme `core/items.py`), et `RecursionError` et `ValueError` rattrapés en `_FichierAppelsInvalide`. Tests : `test_fichier_d_appels_avec_bom` et un cas `imbrication-excessive` dans `test_fichier_d_appels_fautif`.
- [x] **P6. Aucun test ne vérifie l'appariement clé-texte de `vecteurs_antifuite`** [`src/slmsp/core/items.py:868`]. Story 5.1. Source : Verification Gap.
  - **Constat** : échanger les deux `textes.append(...)`, retirer `amorce_usager` ou changer le séparateur laissait tous les tests verts. Le contrôle sémantique de fuite comparerait alors un candidat à la mauvaise moitié de chaque item.
  - **Correctif** : `test_vecteurs_cle_et_texte_appaires` (`tests/core/test_antifuite.py`) vérifie que la matrice est celle des textes envoyés, que chaque clé `#entree` et `#reference` pointe vers le bon texte, et que l'amorce est du côté `#entree`.
- [x] **P7. Les champs de référence de Q, RD et NR ne sont pas épinglés par les tests d'anti-fuite** [`src/slmsp/core/items.py:310`, `:333`, `:441`]. Story 5.1. Source : Verification Gap.
  - **Constat** : retirer `elements_cles`, `orientation_attendue` (Q), `reponse_reference` sous forme d'objet, `valeurs_attendues`, `criteres` (RD) ou `criteres` (NR) de `champs_texte_reference` laissait tous les tests verts. Les données d'entraînement auraient pu reprendre ces textes sans que le contrôle échoue.
  - **Correctif** : `ITEMS_FACTICES` et `REFERENCES` de `tests/core/test_antifuite.py` couvrent maintenant ces six champs (données factices, test paramétré existant).

## Reports

Consignés dans `deferred-work.md` (section du lot 3c et 4).

- **W7. Le Générateur n'applique pas à l'exécution l'interdiction de `?`, de « » et de `"` dans les gabarits** (`src/slmsp/mistral/generateur.py`, `_gabarit`). Source : Acceptance Auditor. La spec 9.2 (AC4) l'exige des 11 gabarits, et seul `tests/mistral/test_gabarits_generateur.py` la tient. Un gabarit édité avec une réponse citée passerait `valider_gabarit` au runtime, et seul son SHA-256 serait journalisé. `medium`, non vérifié sur un cas réel. Motif du report : le fichier est hors cible (lot 5.5/9.2) et `valider_gabarit` sert aussi aux gabarits de Tâche, qui ont droit à ces caractères. L'ajout se fait dans `Generateur._gabarit`.
- **W8. Trois angles de l'anti-fuite ne sont pas couverts** (`src/slmsp/core/items.py:756`, `:869`, `:930`). Sources : Blind Hunter, Edge Case Hunter.
  - les valeurs numériques (`valeurs_attendues` en entiers ou flottants) ne produisent aucune empreinte, car `_feuilles_texte` ne rend que des chaînes ;
  - les URL protégées sont comparées brutes (casse, `/` final, `http` ou `https`, ordre des paramètres) ;
  - les `dataset_id` et `resource_id` donnés par des règles `contient_un_de` ou `mot_entier_un_de` (ou un `exact` en liste) ne sont pas collectés.
  - Motif du report : l'effet dépend du comparateur de la 9.3 (voir D2) ; sans appelant, rien ne peut être vérifié. `low` à `medium`, non vérifié.

## Rejetés

Sources : BH Blind Hunter, ECH Edge Case Hunter, VG Verification Gap, AA Acceptance Auditor.

1. **Le diff n'est ni câblé ni testé** (BH). `false` : la cible exclut les tests, qui existent (`tests/core/test_items.py`, `test_gabarits.py`, `test_antifuite.py`, `tests/mcp/test_cli_mcp.py`, `tests/index/` et `tests/indexation/`), et les deux sous-commandes sont enregistrées par `cli/__init__.py`. L'égalité de `OUTILS_RD` avec `OUTILS_AUTORISES` est testée (`test_items.py` importe les deux).
2. **`vecteurs_antifuite` dilue le signal en joignant tous les textes** (BH). Choix de la spec 5.1 : un vecteur par item pour l'entrée, un pour la référence.
3. **Le mode strict ne rapporte pas toutes les erreurs d'un même item** (BH, ECH). `low` : la promesse du module vise les erreurs du fichier ; un auteur corrige le schéma puis lit les contrôles stricts à la passe suivante. Fusionner les deux listes changerait la structure de `_erreurs_item`.
4. **Un Q `sans_reponse` exige quand même `reponse_reference`, `sources_attendues` et 3 à 5 `elements_cles`** (BH). `false` : c'est le comportement de v1.0, qui se lit en strict (empreinte du dump épinglée) ; `_present` accepte déjà `sans_reponse: false` écrit explicitement.
5. **`vers_requete` ne transmet pas `amorce_usager`, `mention_obligatoire` ni `verification_absence`** (BH, ECH). `false` : la spec 5.1 fixe `options` à `parametres`, `mode`, `longueur_demandee` et `type_courrier`. L'amorce est une donnée de contrôle (utilisée par `evaluation/gel.py` et l'anti-fuite), pas une entrée du modèle.
6. **Le mode souple devine `fictif` depuis du texte libre, et « non fictif » correspond** (BH, ECH). `low` : le mode souple ne lit que l'échantillon de calibrage, fixe et versionné.
7. **`exempl` refuse « exemplaire(s) », et une ligne `true` ou `null` est refusée comme JSON** (BH). `low` : un faux positif est du bon côté pour D1, et la reformulation est immédiate (« copies »).
8. **Rôles de dialogue et jetons de chat incomplets** (BH, AA). Limite documentée de la liste noire lexicale (triage de la 4.1 et de la 9.2). Les rôles listés sont ceux de la spec.
9. **Le SHA-256 du gabarit dépend des fins de ligne** (BH). `false` : la spec 9.2 le définit comme le SHA des octets du fichier, et `.gitattributes` fixe `* text=auto eol=lf`, ce qui rend l'empreinte indépendante de `core.autocrlf`.
10. **Emplacements de la consigne et emplacements déclarés jamais recoupés** (BH, ECH). `low` : `Generateur` compare les deux ensembles avant tout appel (`mistral/generateur.py:318`), et le Harnais ne substitue rien dans les gabarits de Tâche. Valider `id` et `tache` contre le nom du fichier est le rôle de `harness/taches` (« `id` égal au nom du fichier »).
11. **Codes de sortie et organisation de la CLI** (BH, ECH). `false` ou `low` :
    - `mesurer` sort en 0 quel que soit le verdict : décision 9 de la spec 2.3 ;
    - `valider_appel` et `verifier_item_libre` lèvent des `SlmspError`, convertis en code de sortie par `main` ;
    - `index` exige son action et `mcp` affiche l'aide : deux styles voulus, sans effet ;
    - `mcp` n'a pas de `--racine` : non prévu par la 3.3.
12. **`_mesurer` reconstruit `runs/measure/<run_id>`, `--version` n'est pas validé par argparse, `index build` rouvre l'index pour l'afficher** (BH). `low` : cosmétique, et `ouvrir_index` valide la version.
13. **Constantes publiques absentes de `__all__` ; `base_reglementaire` (CT) hors anti-fuite** (BH). `low` : la liste des champs de texte de référence est fixée par la spec.
14. **`Jeu` n'a pas de garde contre une version fournie deux fois** (ECH). `low` : aucun appelant ne la fournit deux fois.
15. **`contient_un_de` ou `mot_entier_un_de` avec une chaîne vide** (ECH). `low` : les règles sont écrites à la main dans un jeu gelé et relu ; l'ajout d'une garde de plus pour un cas improbable ne se justifie pas.
16. **`version` non `str` avant le test de format** (ECH). `low` : `TypeError` au lieu de `ValueError` pour un appel mal typé.
17. **`resolve()` peut lever `OSError` sur un chemin de cassette à caractères Windows interdits** (ECH). `low` : les chemins viennent du jeu gelé ; `_chemins_relatifs` refuse déjà `:` et `\`.
18. **NaN, Infinity et clés en double acceptés par `json.loads`** (ECH). `low` : le fichier du jeu est gelé et son manifeste le protège (`gel`).
19. **Une ligne `-` seule (soulignement setext) passe** (ECH). `false` : `_RE_SOULIGNEMENT` vise les séparateurs de 2 `-` ou plus ; une puce `-` seule n'est pas un titre pour un modèle, et le gabarit est refusé s'il porte un titre hors liste.
20. **Une faute de titre court-circuite les contrôles de la consigne et des emplacements** (ECH). `low` : on corrige les titres puis on relit les fautes ; le message le dit.
21. **« ex » sans point passe** (ECH). `low` : « ex » est un mot courant (« ex-conjoint ») ; l'interdire créerait des faux positifs.
22. **Un échec d'appel MCP en milieu de session perd les appels réussis avant lui** (ECH). `low` : décision 3.3, rien n'est écrit en cas d'échec et on relance ; une cassette partielle est trompeuse pour le rejeu.
23. **`erreur` JSON-RPC non objet, ou message à caractères de contrôle** (ECH). `low` : le serveur est celui de data.gouv, et le cas n'a jamais été vu.
24. **Une liste vide ou `{}` passe `_present`** (VG, autre constat). `low` : voulu par la 5.1 (`test_strict_listes_vides_permises`).
25. **Le jeton `|>` seul et la limite exacte de 4 000 caractères ne sont pas testés** (VG). `low` : la branche est exercée par `<|im_start|>` et par `test_longueur_maximale`.
26. **Dialogue au pluriel et locuteurs non listés** (AA). Doublon du n° 8.
27. **Docstring de `GabaritValide.consigne` : des lignes d'espaces restent en tête ou en fin** (AA). `low` : la consigne part au modèle telle quelle ; ces lignes ne changent rien et le SHA porte sur les octets.
28. **L'API anti-fuite accepte encore des objets `Jeu`, alors que le triage de la 5.1 parlait de noms de version** (AA). `low` : un `Jeu` est la sortie publique du lecteur unique, et l'API ne rend que des empreintes, des vecteurs et des identifiants. AD-24 limite l'accès côté `data`.
29. **`mot_entier_un_de` dépasse le texte de la 5.1** (AA, observation). Sans écart : la règle vient du jeu v1.1 et est documentée dans le module ; le dump v1.0 reste inchangé (test d'empreinte).

(29 lignes, qui regroupent les 34 constats bruts rejetés. Constats bruts : 20 BH, 28 ECH, 5 VG, 6 AA, soit 59. Retenus : 25, à savoir P1 (BH, ECH ×3), P2 (ECH ×2), P3 (ECH), P4 (BH, ECH), P5 (ECH, AA), P6 et P7 (VG ×2), W7 (AA), W8 (BH ×3, ECH ×2), D1 (BH, ECH ×4) et D2 (BH).)

## Application des correctifs (2026-10-13)

Les 7 correctifs sont appliqués (commit `fix(core): correctifs de la revue de code des lots 3c et 4`). `ruff check` passe, et `ruff format` a été appliqué aux fichiers touchés.

- **`uv run pytest`** (suite complète, une seule fois) : 3 467 succès, 338 sauts, 0 échec. Le `.venv` du worktree a reçu `uv sync --offline --extra fetch --extra data --extra judge`, sans téléchargement.
- **Fichiers touchés** : `src/slmsp/core/gabarits.py`, `src/slmsp/core/items.py`, `src/slmsp/cli/mcp.py`, et les tests `tests/core/test_gabarits.py`, `test_items.py`, `test_antifuite.py` et `tests/mcp/test_cli_mcp.py`. Aucun fichier hors de la cible, de ses tests ou de cette revue.
- **Contrôle par mutation** : avant correction, un script a confirmé les défauts de P1 (mot coupé, caractère invisible et pleine chasse acceptés), P2 (`RecursionError`), P3 (jeu vide lu), P4 (relecture du dump refusée). Les nouveaux tests couvrent chacun de ces cas. P5 repose sur le même constat (BOM refusé en `utf-8`). P6 et P7 comblent des mutations décrites par le Verification Gap.
- **D1 (rappel)** : aucun gabarit du générateur ne contient d'exemple de réponse ; aucune Donnée d'entraînement n'a été rédigée. Les fixtures ajoutées sont des chaînes factices (`"orientation factice bb cc dd ee ff"`).
