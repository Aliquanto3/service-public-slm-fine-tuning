# Revue de code, lot 2 : évaluation

- **Date** : 2026-10-12
- **Cible** : `3431c35..nuit/2026-10-12`, restreinte à `src/slmsp/evaluation/`, `src/slmsp/cli/eval.py`, `src/slmsp/core/texte.py`, `tests/evaluation/` et `tests/core/test_texte.py` (30 fichiers, 8 565 lignes).
- **Specs** : stories 5.1, 5.2, 5.3, 5.6 et 8.2 ; contexte de l'epic 5, consignes de nuit, `eval/SPEC-jeu-evaluation.md`.
- **Relecteurs** : Blind Hunter, Edge Case Hunter, Verification Gap, Acceptance Auditor. Aucun n'a échoué.
- **Bilan** : 1 décision (tranchée), 8 correctifs (dont 1 issu de la décision), 3 reports, 29 constats rejetés.
- **Hors lot** : juges et Mistral (lot 1), socle de l'epic 1 (lot 3), MCP et outils d'items (lot 4).

## Items non-juge (point demandé)

Le code traite correctement les motifs `erreur-api`, `limite-debit` et `budget`. En revanche, aucun test ne fixe le cas `erreur-api` ou `limite-debit` (correctif P1).

- **Motifs** : le motif `limite-debit` vient des correctifs du lot 1 (P11), qui ne sont pas encore commités. `notation.py` n'a pas besoin de le connaître : tout `non-juge` dont le motif n'est pas `budget` rend le run `partiel-erreur` (`notation.py:485-495`). `partiel-budget` l'emporte, comme le veut la spec 5.6.
- **Couverture** : les deux juges rendent un résultat par demande, avec le motif `non-traite` par défaut (`judge/claude.py:323`, `judge/second.py:169`). Aucun item ne peut donc échapper au calcul du statut.
- **Scores** : un `non-juge` sort du calcul et entre dans `non_juges` (`scores.py:213`). Pour RD, un litige sans verdict valide est exclu, parce que `reponse_exacte` vaut `None` (`controles.py:250`).
- **Kappa** : il est calculé sur les items jugés valides par les deux juges (`scores.py:160-167`). Le second juge ne reçoit que les items dont le verdict principal est valide (`notation.py:435-442`). Le kappa porte donc sur « l'effectif disponible », comme le prévoit la spec 5.6. `effectifs.second_juge` compte les verdicts valides du second juge.
- **Limite** : les `non-juge` du second juge n'apparaissent dans aucun effectif de `scores.json`. On ne les voit que dans `verdicts.jsonl`. Ce n'est pas un écart à la spec.

## Décision (tranchée par Anaël le 2026-10-12)

**D1 → option 1 : déclarer dans le jeu les colonnes vérifiées.** Le code devient le correctif P8. Le jeu v1.1 et son gel deviennent le report W3, qui demande une relecture humaine.

- [x] **D1. RD, méthode `valeurs` : le contrôle exige tous les nombres de toutes les cellules, y compris celles que la question ne demande pas.** Story 5.6. Sources : Blind Hunter, Edge Case Hunter.
  - **Constat** : `_valeurs_numeriques` (`src/slmsp/evaluation/controles.py:176`) extrait les nombres de toutes les cellules de `valeurs_attendues.lignes`, et `controle_rd` exige que chacun figure dans le texte. Vérifié sur le jeu v1.0 :
    - **RD-017** : les nombres exigés sont `2020, 1, 134, 2020, 2, 137, 2020, 3, 75`. La réponse exacte « janvier 2020 : 134, février : 137, mars : 75 » ne contient ni 1, ni 2, ni 3. Elle reçoit `reponse_exacte = False`.
    - **RD-010** : le contrôle exige aussi `2018` (année de publication) et `26` (bailleurs consolidés), alors que la question ne demande que le nombre de bailleurs et celui des logements.
    - **RD-039** : le contrôle exige `2023` (« 2022-2023 », alors que la question dit « rentrée 2022 ») et `10005`, tiré de l'UAI `0010005A`.
  - **Conséquence** : 3 des 5 items RD de la méthode `valeurs` peuvent être notés faux sur une réponse exacte. Le contrôle sort avant la détection de litige, donc le Juge ne les rattrape jamais. La composante `reponse_exacte` du score RD est biaisée vers le bas, pour tous les modèles comparés.
  - **Pourquoi c'est une décision** : la spec 5.6 dit « toutes leurs valeurs numériques ». Le jeu v1.0 est gelé, avec un SHA dans le manifeste, et ne peut pas être corrigé sur place. Trois voies sont possibles :
    1. ne garder que les colonnes demandées, via un champ du jeu (par exemple `colonnes_verifiees`) : il faut un jeu v1.1 et un nouveau gel ;
    2. ajouter une règle de code (ignorer les colonnes d'année, de mois et d'identifiant, ou n'exiger que les cellules dont la valeur est purement numérique) : le jeu reste intact, mais la règle est heuristique, et `VERSION_TEXTE` ne change pas ;
    3. traiter une valeur manquante comme un litige, que tranche le Juge (`libelle_correct`) : le jeu reste intact, mais cela coûte des appels au Juge et modifie la spec 5.6.

## Correctifs

- [x] **P1. Aucun test ne fait finir une notation en `partiel-erreur` à cause d'un `non-juge` dont le motif n'est pas `budget`** [`tests/evaluation/test_notation.py`]. Story 5.6. Source : Verification Gap, avec mutation démontrée : si l'on retire `or autres_non_juges` ou `principal.jugements.update(non_jugeables)`, tous les tests passent encore.
  - **Correctif** : ajouter à `JugeFactice` une option qui émet des `non-juge` avec un motif donné. Ajouter les tests `erreur-api`, `limite-debit` (sur le principal et sur le second juge) et un item CR ou RE non jugeable. Chacun vérifie `partiel-erreur`, le code 1 de la CLI et le motif dans `verdicts.jsonl`.
- [x] **P2. Un `relecture-validee.json` enregistré avec un BOM UTF-8 est ignoré sans message** [`src/slmsp/evaluation/relecture.py:138`]. Story 5.6. Source : Edge Case Hunter.
  - **Constat** : `read_text(encoding="utf-8")` garde le BOM, `json.loads` lève une erreur, et l'exception est avalée. Les scores restent « non relus ». Sous Windows PowerShell 5.1, `Out-File` et `Set-Content -Encoding utf8` écrivent un BOM.
  - **Correctif** : passer à `encoding="utf-8-sig"`, et ajouter un test avec BOM.
- [x] **P3. Le chemin `interrompu` de `noter` n'a pas de test** [`tests/evaluation/test_notation.py`]. Story 5.6. Source : Verification Gap, avec mutation démontrée.
  - **Correctif** : ajouter `test_juge_qui_leve_interrompt_le_run`. Un juge lève une exception qui n'est pas une `BudgetEpuise`, et le test vérifie `pytest.raises` et le dernier état `interrompu` de `etat.jsonl`.
- [x] **P4. `ouvrir_juges` n'est jamais exécuté : la surcharge `--mode-juge` n'est pas vérifiée** [`src/slmsp/evaluation/notation.py:110`]. Story 5.6. Source : Verification Gap.
  - **Constat** : si l'on retire `model_copy(update={"mode_appel": ...})`, aucun test ne casse. `test_notation_reel.py` reconstruit les juges à la main.
  - **Correctif** : ajouter un test de `ouvrir_juges(racine, "direct")` où `fabriquer_client` et `fabriquer_sdk` sont simulés. Il vérifie `mode_appel` et `description`.
- [x] **P5. Aucun test de reprise de génération ne part d'une ligne déjà en erreur** [`tests/evaluation/test_generation.py`]. Story 5.3. Source : Verification Gap, avec mutation démontrée.
  - **Correctif** : ajouter `test_reprise_garde_les_erreurs_anterieures`. Un item échoue avant l'interruption, et le test vérifie que la reprise finit `partiel-erreur`.
- [x] **P6. Le vrai `ouvrir_harnais` n'est exercé que par des tests `lent`, exclus par défaut** [`src/slmsp/evaluation/assemblage.py:124`]. Story 5.3. Source : Verification Gap.
  - **Correctif** : créer `tests/evaluation/test_assemblage.py`, avec `ServeurLlama`, `ouvrir_index` et `lire_props` simulés. Il vérifie que `chat_template_sha256` est le SHA du template servi, que le serveur d'embeddings tourne sur `cpu` avec `prendre_verrou_gpu=False`, et qu'un template absent lève `ErreurInference`.
- [x] **P7. `verdicts.jsonl` et `controles.jsonl` ne sont pas créés quand aucune ligne ne s'y écrit** [`src/slmsp/evaluation/notation.py:449`]. Story 5.6 AC1. Source : Acceptance Auditor.
  - **Constat** : `ajouter_jsonl` ne crée le fichier qu'à la première ligne. Une génération où tous les items sont en erreur, ou qui ne contient que du RD et du CO sans litige, produit un run sans `verdicts.jsonl`.
  - **Correctif** : créer le fichier vide (`run.ecrire(nom, b"")`) quand aucune ligne n'a été écrite.
- [x] **P8. RD, méthode `valeurs` : ne vérifier que les colonnes déclarées** [`src/slmsp/evaluation/controles.py:176`]. Story 5.6, issu de D1.
  - **Correctif** :
    - Lire `valeurs_attendues.colonnes`, une liste facultative de noms de colonnes. `valeurs_attendues` est déjà de type `Any` et masqué au modèle, donc le schéma d'`ItemRD` ne change pas.
    - Si la liste est présente, `_valeurs_numeriques` ne lit que ces cellules. Si elle est absente, le comportement actuel est conservé, et le jeu v1.0 reste noté comme aujourd'hui.
    - `gel` et `verifier_jeu` refusent une colonne qui n'existe dans aucune ligne.
    - Mettre à jour la docstring du module et la spec 5.6.
    - Ajouter des tests sur RD-017 (une réponse « janvier 2020 : 134 … » est exacte avec `colonnes = ["Nombre"]`) et sur une colonne inconnue.

## Reports

- [x] **W1. `eval run --phase toutes` après une génération `partiel-erreur` : aucun test n'atteint la notation** [`src/slmsp/cli/eval.py:309`]. Source : Verification Gap. Reporté : petite branche de la CLI, qu'un cas paramétré de `test_cli_toutes` couvrira quand la suite sera retouchée.
- [x] **W2. Les réglages de décodage (`GRAINE`, `MAX_TOKENS`, `OPTIONS_LLM`) n'ont pas rejoint `config/evaluation.toml`, et une sortie tronquée reste `ok`** [`src/slmsp/evaluation/generation.py`]. Sources : Blind Hunter, Acceptance Auditor. Reporté : c'est une dérive par rapport aux Design Notes de la 5.3, pas une AC de la 5.6. Signaler la troncature demande un champ de `Generation`. Cela compte pour les CR longs et les RE `detaillee`.

- [x] **W3. Jeu v1.1 : déclarer `valeurs_attendues.colonnes` sur les 5 items RD de la méthode `valeurs`, puis geler** [`eval/construction/`, `eval/jeu/`]. Issu de D1. Reporté : il faut une nouvelle version du jeu, l'export de revue, une relecture humaine et `gel --statut relu`. Ce travail sort d'une revue de code. Il faut le faire avant la Baseline complète : sinon, la composante `reponse_exacte` de RD reste biaisée (RD-010, RD-017 et RD-039). Colonnes proposées : RD-010 `Nbre_bailleurs` et `Nbre_logements` ; RD-017 `Nombre` ; RD-023 `Année` et `Note Index` ; RD-030 `REG` et `CHEFLIEU` ; RD-039 `Effectifs` et `IPS`.

## Rejetés

1. **Les items en erreur, non jugés ou invalides sortent du dénominateur** (BH). C'est la matrice de la 5.6 (« exclu des scores, compté »). Corriger reviendrait à modifier la spec.
2. **Un juge qui rend moins de résultats que de demandes laisse le run `complet`** (BH). `false` : les deux juges rendent un résultat par demande (`non-traite` par défaut, `claude.py:323`, `second.py:169`).
3. **La reprise ne relance jamais les items en erreur** (BH). Déjà reporté dans la spec 5.3 (`deferred`).
4. **La reprise ne compare pas `OPTIONS_LLM` ni `chat_template_force`** (BH). `low` : ce sont des constantes du code. Les changer demande un commit, et le correctif ajouterait des contrôles.
5. **`connexions_bloquees` n'est pas écrit dans le run** (BH). Déjà rejeté à la revue de la 5.3 : un `HoteBloque` apparaît dans la trace.
6. **CO : une faute d'espacement de ponctuation n'est pas mesurable** (BH). `false` sur le jeu v1.0 : aucune des 15 fiches CO ne contient une telle faute. La seule faute d'espacement, « au paravant », est une faute de mot, qui se mesure. La tolérance est documentée.
7. **CO : le retour anticipé sur une source qui n'est pas du texte n'a pas la même forme** (BH). `low` : les scores ne lisent que `rappel` et `taux_hors_faute`, et les 15 items CO ont un texte.
8. **RD : les appels en trop ne sont pas pénalisés** (BH). C'est la formule de la grille (rappel). Corriger reviendrait à modifier la spec.
9. **RE : seule la borne haute est contrôlée** (BH). C'est la spec 5.6 (plafond, respect rapporté). Les trois longueurs du jeu v1.0 sont toutes reconnues.
10. **Un kappa non calculable s'affiche comme un kappa non fragile** (BH). `low` : il vaut `null` dans `scores.json` et `—` dans la CLI. La spec prévoit un kappa sur l'effectif disponible.
11. **`relecture-validee.json` n'est lié à aucun contenu** (BH). C'est la spec 5.6 (fichier daté). Corriger reviendrait à modifier la spec.
12. **`_entrees` hache `config/evaluation.toml` même avec une config injectée** (BH). `false` : aucun appelant de production n'injecte de config (`cli/eval.py` n'en passe pas).
13. **`sonde_outils` importe des fonctions privées de `generation`** (BH). `low`, cosmétique.
14. **La cible « amorces réelles » se calcule sur le nombre prévu de Q** (BH). `low` : c'est une cible de composition fixe, comme les autres `CIBLES`.
15. **Liste de tests manquants divers** (BH). Les cas utiles sont repris en P1 à P6. Les autres (IPv6 mappée, backticks dans `_bloc`) sont `low`.
16. **`charger_scores` rend les Tâches dans l'ordre alphabétique** (VG). `low` : seule la CLI affiche les Tâches, et elle part du `Scores` en mémoire.
17. **Une `ValidationError` pendant un run sort en code 2** (ECH). `low` : `generer_item` capture les erreurs item par item, et le cas est rare.
18. **Une `ValueError` pendant la sonde sort en code 2** (ECH). `low`, même motif.
19. **`toutes --reprendre --items` sans clé d'API : `SecretManquant` masque l'erreur d'usage** (ECH). `low`.
20. **Deux reprises concurrentes d'un même run** (ECH). `low` : un seul opérateur, et la règle « un seul écrivain » est documentée.
21. **CT : `champs_a_laisser_en_emplacement = []` donne une réussite à vide** (ECH). `low` : aucun des 15 items CT du jeu v1.0 n'a de liste vide.
22. **CO : une faute qui chevauche en partie la fenêtre alignée** (ECH, AA). `low` : le cas est rare et la règle stricte est documentée.
23. **CO : un item sans faute sort du score** (ECH). `false` : les 15 items CO du jeu v1.0 ont tous des fautes.
24. **Sonde : un item RD sans appel attendu n'est jamais valide** (ECH). `low` : il faut l'avoir choisi avec `--items`, et le tableau affiche 0/0.
25. **Gel : une écriture ratée laisse un export orphelin** (ECH). `low` : il faut un disque plein, et le correctif ajoute une branche.
26. **`--phase toutes` crée les SQLite de `var/` avant de vérifier le manifeste** (AA). `low` : ces fichiers sont des magasins partagés, créés une fois. Rien ne s'écrit sous `runs/`.
27. **`evaluation` importe `judge.cache` et `judge.prompt`, ce que la 5.3 interdit** (AA). La 5.6 l'autorise, et la contradiction est entre specs. Corriger reviendrait à modifier la spec.
28. **La sonde sort en code 1 alors qu'un protocole valide est recommandé** (AA). C'est la décision 4 de l'Auto Run Result de la 8.2. Corriger reviendrait à modifier la spec.
29. **`recommandation.json` est écrit par `ecrire` et non par `ecrire_json`** (AA). `low` : l'écriture passe par `Run`, en JSON canonique.

## Application des correctifs (2026-10-12)

Les 8 correctifs sont appliqués sur `nuit/2026-10-12`, sans commit pour l'instant.

- **P2** (`evaluation/relecture.py`) : `relecture-validee.json` est lu en `utf-8-sig`.
- **P7** (`evaluation/notation.py`) : `controles.jsonl` et `verdicts.jsonl` sont créés vides quand aucune ligne ne s'y écrit.
- **P8** :
  - `evaluation/controles.py` : `_valeurs_numeriques` ne lit que `valeurs_attendues.colonnes` quand la liste est donnée. Sans elle, le comportement est inchangé.
  - `evaluation/gel.py` : `_erreurs_colonnes` refuse une liste vide, une valeur qui n'est pas une liste de chaînes, ou une colonne absente des lignes.
  - Le Spec Change Log et la règle RD de la spec 5.6 sont mis à jour.
- **Tests ajoutés** :
  - **Doublure** : `JugeFactice(non_juges={item: motif})` rend un `non-juge` sans appel.
  - **P1** : `test_non_juge_hors_budget_partiel_erreur` (`erreur-api`, `limite-debit`), `test_second_juge_limite_debit_hors_kappa`, `test_item_non_jugeable_partiel_erreur` et `test_cli_notation_erreur_api_code_1`.
  - **P2** : un cas avec BOM dans `test_relecture_validee`.
  - **P3** : `test_juge_qui_leve_interrompt_le_run`.
  - **P4** : `test_ouvrir_juges_surcharge_le_mode`. Les fabriques des SDK sont simulées, et les configurations réelles sont utilisées.
  - **P5** : `test_reprise_garde_les_erreurs_anterieures`.
  - **P6** : `tests/evaluation/test_assemblage.py`, 5 tests. `ServeurLlama`, `ouvrir_index` et `lire_props` sont simulés.
  - **P7** : `test_fichiers_presents_sans_controle_ni_verdict`.
  - **P8** : `test_rd_valeurs_des_colonnes_declarees` (RD-017) et `test_colonnes_rd_invalides_bloquantes` (3 cas).
- **Vérifications** :
  - `tests/evaluation`, `tests/core/test_texte.py` et `tests/test_architecture.py` : 434 tests réussis, 3 désélectionnés (`lent`).
  - `ruff check` et `ruff format` passent.
  - Chaque correctif a été vérifié par mutation : sans lui, son nouveau test échoue (P1 deux fois, P8 deux fois, 10 mutations sur 10).
- **Non fait ici** : le jeu v1.1 (W3). Tant qu'il n'est pas gelé, le jeu v1.0 garde le biais RD.
