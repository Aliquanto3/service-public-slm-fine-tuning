# Spec O3 — Sélection des cibles parmi des candidats notés (`data build --selection`, étage 2)

Méthodologie v2 (`plan-methodo-2026-10-20.md` §2 principes 1, 2, 4 ; §4 O3). Story à risque : relue avant code. Lancée seulement si l'étage 2 est déclenché. Dépend de **O1** (verdicts, `candidat_id`) et **O2** (candidats). Partage le module `data/selection.py` avec **C5** : O3 et C5 sont développées en séquence (O3 d'abord, C5 réutilise), jamais dans la même vague.

## But
Cible de chaque entrée = **meilleur candidat noté** (base locale, Mistral, ou second générateur autorisé), s'il passe le seuil de sa tâche ; sinon ligne écartée. Ne jamais entraîner à faire moins bien que la base.

## Contrat attendu de O2 (`candidats.jsonl`, à respecter par O2)
Une ligne par candidat : `session_id` (session `data-generate` d'origine), `candidat_id` (`mistral:<appel_id>`, `slm:<appel_local_id>`, `openrouter:<appel_id>`), `source` (`mistral`, `slm:<slug>`, `openrouter:<modele>`), `tache`, paramètres (température, graine). Aucun texte : le texte est relu dans son journal (Mistral, `generations-locales.sqlite`, journal OpenRouter des générateurs). Les candidats locaux sont générés sur **exactement la conversation d'entraînement** de la session (prompt de tâche + entrée, comme `preferences.py`), pour que cible et entrée soient cohérentes.

## Règles
1. Entrées : `candidats.jsonl` (O2) + `verdicts.jsonl` (O1, `data juger`) ; jointure par `(session_id, candidat_id)` ; un candidat sans verdict, ou au verdict `invalide`, est ignoré et compté.
2. **Score agrégé** d'un candidat = somme pondérée des critères de la grille de données (poids dans `donnees.toml` `[selection.poids.<TACHE>]`, par défaut égaux après normalisation de chaque échelle sur [0, 1]) ; **seuil** = règle d'acceptation de O1 (critères bloquants). Fonctions dans `data/selection.py`, partagées avec C5.
3. Gagnant = score max parmi les acceptés ; égalité → préférence à la **base locale** (moins d'oubli), puis à Mistral, puis ordre stable par `candidat_id`.
4. **D1 et sources** : seules des sorties de la base locale ou de générateurs autorisés deviennent cibles : Mistral ; DeepSeek comme **candidat** en E4 (autorisé par Anaël le 20/10, §7 bis, licence MIT) ; jamais une sortie d'un **juge** ni de Claude. Liste `[selection] sources_autorisees` (défaut `["mistral", "slm:<base du run>"]`, `openrouter:deepseek/deepseek-v4-pro` ajouté pour E4) ; le build refuse un candidat dont `source` n'y est pas.
5. **Biais d'auto-préférence (E4)** : quand un candidat vient de la même famille que le juge de sélection (DeepSeek jugé par DeepSeek), le verdict d'un juge d'une autre famille (GLM-5.3, même grille O1) est exigé pour cette entrée et le score retenu est le minimum des deux. Option `[selection] juge_croise`, active dès qu'une source `openrouter:deepseek/*` est autorisée.
6. **Provenance des cibles non Mistral** : aujourd'hui `build` refabrique chaque ligne depuis le journal Mistral seul (`LigneEntrainement.meta.appel_ids` ≥ 1, `verifier_octets`), et `train run` revérifie ces `appel_ids` (`train.chargement.recontroler_appel_ids`). Une cible de la base ou de DeepSeek n'y a pas sa place. Il faut donc :
   - `LigneEntrainement` v2 : `meta.cible = {source, appel_id | appel_local_id}` en plus des `appel_ids` Mistral de l'**entrée** (CR : transcription ; LC, CT : aucun appel Mistral si l'entrée est publique, d'où `appel_ids` facultatif en v2 quand `cible` est présent) ;
   - re-dérivation et revérification des octets depuis le journal de la cible (`generations-locales.sqlite` : `generateur`, `statut ok`, SHA, comme les paires ORPO actuelles) ;
   - `recontroler_appel_ids` et `EnteteMetaPaire` acceptent la v2 ; la v1 reste lue telle quelle ;
   - lecteur `data` : `generations-locales.sqlite` ajouté à sa liste d'accès (`core/artefacts.py`, AD-24), en lecture seule.
7. **Licences** : chaque source de cible a une entrée au Registre (`data/registre-licences.toml`) : sorties `slm:<slug>` (licence du Modèle de base) et `openrouter:deepseek/deepseek-v4-pro` (MIT). Sans entrée, le build échoue avant tout run. L'usage (`diffusable` ou `recherche`) d'une sortie de Modèle de base suit sa licence ; à confirmer par Anaël pour chaque base avant une variante `diffusable`.
8. MANIFEST du jeu : source du gagnant par ligne, notes, part de la base par tâche, nombre d'écartées par motif, empreintes des runs de candidats et de verdicts, SHA des grilles de données.
9. **Paires de préférence** (pour C5/E3) produites dans le même run par `data/selection.py` : (meilleur accepté, moins bon noté) si l'écart de score ≥ `ecart_min` (config) ; au plus une paire par entrée ; écrites au format de paires **v2** défini par C5 (le format v1 suppose « choisi Mistral, rejeté local »).

## Critères de fin
Tests sur fixtures : gagnant ; égalité → base ; aucun accepté → écartée ; candidat sans verdict ignoré ; source non autorisée → refus ; juge jamais cible ; juge croisé exigé pour un candidat DeepSeek ; cible locale re-dérivée de `generations-locales.sqlite` et octets revérifiés ; `train run` charge un jeu v2 (recontrôle des cibles locales) et toujours un jeu v1 existant ; source absente du Registre → refus ; paires avec écart minimal ; MANIFEST complet. `tests/data/test_build.py`, `tests/train/test_preferences_chargeur.py` et les tests de `train.chargement` verts.

## Revue de la spec
Relecture du 2026-10-20 (reviewer, avant code), contre `data/{build,preferences}.py`, `core/schemas/entrainement.py`, `train/chargement.py`, `core/artefacts.py`, `data/registre-licences.toml`.

| # | Gravité | Constat | Changement |
|---|---|---|---|
| 1 | high | « Jeu SFT au format existant lisible par `train run` » est impossible pour une cible de la base : `build` ne refabrique que depuis le journal Mistral, `meta.appel_ids` exige au moins un appel Mistral, `train run` les revérifie. | Règle 6 : `LigneEntrainement` v2 (`meta.cible`), re-dérivation depuis `generations-locales.sqlite`, recontrôle étendu, v1 relue. |
| 2 | high | Aucune entrée de Registre pour les sorties de la base ni pour DeepSeek : le build échouerait (verrou 5), ou passerait sans licence. | Règle 7 ; usage des sorties de base : **décision d'Anaël** par modèle. |
| 3 | medium | E4 : DeepSeek note des candidats DeepSeek (auto-préférence connue des juges LLM). | Règle 5 : juge croisé GLM, minimum des deux scores. |
| 4 | medium | Le lecteur `data` n'a pas accès à `generations-locales.sqlite` (AD-24). | Ajout explicite à sa liste d'accès. |
| 5 | medium | Contrat de `candidats.jsonl` (O2 sans spec) et `candidat_id` non définis. | Contrat minimal ; conversation d'entraînement exacte pour les candidats locaux. |
| 6 | medium | Échelles hétérogènes (rappel 0-1, 0/1, 0/1/2) sommées telles quelles. | Normalisation sur [0, 1] avant pondération. |
| 7 | low | « DeepSeek seulement en E4, décision d'Anaël » : déjà autorisée le 20/10. | Formulation mise à jour. |
| 8 | low | O3 et C5 dans le même module sans ordre. | O3 d'abord, C5 réutilise ; vagues distinctes. |
