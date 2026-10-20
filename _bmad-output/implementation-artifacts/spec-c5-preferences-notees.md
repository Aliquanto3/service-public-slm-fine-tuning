# Spec C5 — Préférences depuis des candidats notés (étage 2)

Méthodologie v2 (`plan-methodo-2026-10-20.md` §1, §2 principe 4, §3 C5). Story à risque : relue avant code. Dépend de **O1** (verdicts) et **O2** (candidats) ; réutilise `data/selection.py` livré par **O3** (C5 après O3, jamais dans la même vague).

## Constat
`slmsp data build --preferences` (`src/slmsp/data/preferences.py`) prend la cible SFT comme *choisie* et la sortie de la base comme *rejetée*. Or la base est meilleure que les cibles en LC, CR, NR : ORPO apprend alors à fuir de bonnes réponses.

## Changement
1. Nouveau mode `--preferences --depuis-verdicts <run data-juger> --candidats <run O2>` : la paire est (meilleur candidat noté, moins bon candidat noté) de la même entrée, **quelles que soient leurs sources**, si l'écart de score agrégé ≥ `ecart_min` et que le choisi passe le seuil de sa tâche (score, seuil et règles de `data/selection.py`, O3). Sans O3 livré, C5 n'est pas lancée.
2. Le mode actuel « cible vs base » reste disponible derrière `--mode cible-contre-base`, comportement et sortie inchangés (traçabilité des runs passés v3, v5, v16). Le défaut sans verdicts devient un **refus explicite** (« fournir --depuis-verdicts ou --mode cible-contre-base »). Tests à réaligner : les appels sans mode de `tests/data/test_preferences.py`, `tests/data/test_nettoyage.py` et `tests/data/test_sous_ensemble.py` passent `--mode cible-contre-base` (ou l'argument équivalent de `lancer_preferences`), sans changer leurs assertions.
3. **Format de paire v2** : `MetaPaire` (v1, `extra=forbid`) suppose « choisi = appels Mistral (`appel_ids` ≥ 1), rejeté = local (`generateur_rejected`, `appel_local_id`) » ; une paire où la base est choisie ou où les deux sont Mistral n'y entre pas. `PairePreference` v2 : `meta.choisi` et `meta.rejete` = `{source, candidat_id, appel_id | appel_local_id}`, `meta.appel_ids` = appels Mistral de l'entrée (facultatif si l'entrée est publique), `source`/`licence` des deux réponses. `ManifestePreferences` v2 : `derogation` = nouveau texte (« paires notées par le juge de données DeepSeek, aucun verdict du Juge Claude ») au lieu de `DEROGATION_ORPO`, runs de verdicts et de candidats, `ecart_min`. `train.chargement` (`EntetePaire`, recontrôle des appels Mistral et du journal local) lit v1 et v2 ; `tests/train/test_preferences_chargeur.py` vert.
4. **Même prompt** : `prompt` de la paire = conversation d'entraînement de l'entrée (celle du jeu SFT de la session) ; choisi et rejeté ont été produits sur ce prompt (contrat O2). Une paire dont les deux réponses sont identiques après normalisation est écartée (`identique`, comme aujourd'hui).
5. **D1** : choisi et rejeté ne viennent que de sources autorisées (`[selection] sources_autorisees`, O3) ; aucune sortie de juge ni de Claude ; juge croisé pour un candidat DeepSeek (O3 règle 5).
6. MANIFEST : sources du choisi et du rejeté, écart de score, compte des entrées sans paire (écart insuffisant, aucun accepté, candidat unique).
7. Pas de code dupliqué avec O3 : C5 n'ajoute que le mode CLI, le format v2 et l'écriture.

## Critères de fin
Tests : base choisie quand elle est mieux notée (paire v2 valide) ; deux candidats Mistral → paire v2 ; écart insuffisant → pas de paire ; choisi sous le seuil → pas de paire ; candidat unique → pas de paire ; défaut sans verdicts ni mode → refus ; `--mode cible-contre-base` produit des octets identiques à l'ancien mode sur la fixture existante ; `train run` charge une version v2 et toujours les versions v1 existantes ; invariant ORPO de 10.9 (prompt commun, dernier message `assistant`, conversations valides) respecté.

## Revue de la spec
Relecture du 2026-10-20 (reviewer, avant code), contre `data/preferences.py`, `core/schemas/entrainement.py` (`MetaPaire`, `PairePreference`, `ManifestePreferences`, `DEROGATION_ORPO`), `train/chargement.py`, `cli/data.py`.

| # | Gravité | Constat | Changement |
|---|---|---|---|
| 1 | high | « Format compatible avec l'invariant ORPO » : `MetaPaire` v1 interdit une paire à choisi local (pas d'`appel_ids` Mistral, `generateur_rejected` obligatoire), et `train.chargement` recontrôle ces champs. Le cœur de C5 (base choisie) serait refusé. | Format de paire et manifeste v2, lus avec la v1 par `train.chargement`. |
| 2 | medium | Défaut devenu refus : les tests qui appellent `--preferences` sans mode cassent. | Tests à réaligner nommés. |
| 3 | medium | `DEROGATION_ORPO` décrit l'ancien procédé (« rejetée = base locale ») : il serait faux dans le MANIFEST v2. | Nouveau texte de dérogation. |
| 4 | medium | Dépendance O3 implicite (« si O3 est livré ») et C5 sans source de candidats. | C5 après O3 ; `--candidats <run O2>` ; contrat de prompt commun. |
| 5 | low | Cas « candidat unique » non couvert. | Ajouté au MANIFEST et aux tests. |
