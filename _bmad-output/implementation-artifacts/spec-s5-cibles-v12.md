# Story S5 — Cibles v12 conformes à la grille (CR, CT, LC), Mistral Large 4

Décision d'Anaël (19/10/2026, 21 h 40) : réécrire les données d'entraînement ; Mistral Large 4 possible. L'entraînement sur v12 attend sa relecture.

## Constat (M1 v11, MiniCPM5-2B et Qwen3.5-2B, contre la Baseline)
- **CR** (50,1 → 21,7) : le score = couverture des `decisions_reference` et `actions_reference` (une action sans responsable ou échéance connus compte pour moitié) + absence d'invention. Verdicts : éléments absents (168), inventions (30). Les 79 cibles CR v11 sont en prose : aucune n'a les sections Participants / Points abordés / Décisions / Actions. (La structure est rapportée par la grille, non comptée, mais des sections Décisions et Actions forcent l'énumération complète.)
- **CT** (50,0 → 13,3) : la conformité exige le format administratif français complet (expéditeur, destinataire, objet, références, formule d'appel, corps, formule de politesse, signature) et les champs inconnus en `[Emplacement]` sans valeur inventée. Les 35 cibles commencent par « Objet ».
- **LC** (24,0 → 4,0 / 0,0) : fidélité à 0 sur 25 items sur 30 (ajouts d'informations). Le score exige Fidélité = 2 et Termes = 1, et un gain de Kandel-Moles moyen ≥ +10, sinon plafond à 50.
Grille : `eval/grille-juge-v1.md` (CR l. 42, LC l. 52, CT l. 83).

## D1 (bloquant)
Claude n'écrit **aucun exemple** de cible, ni few-shot, ni amorce : les gabarits ne contiennent que des **instructions** (contraintes de forme et de fond). Le générateur reste Mistral. Pas de texte d'item du jeu d'évaluation dans les gabarits.

## Périmètre
1. **Gabarits du générateur** (`config/prompts/generateur/`, `config/prompts/taches/{CR,CR-morceau,CR-fusion,CT,LC}.md`, selon où la consigne de réponse est rédigée) :
   - CR : quatre sections, titres exacts `Participants`, `Points abordés`, `Décisions`, `Actions` ; toutes les décisions et actions des notes, chaque action avec son responsable et son échéance quand les notes les donnent ; rien qui ne figure pas dans les notes ; un point discuté sans décision n'est jamais présenté comme décidé. Garder le plafond de mots de `[generateur.plafonds_mots]` ; relever celui de CR si les quatre sections ne tiennent pas (vérifier sur les longueurs de CR v11 : médiane 396 mots).
   - CT : format administratif français complet, dans l'ordre : expéditeur, destinataire, lieu et date, objet, références, formule d'appel, corps, formule de politesse, signature ; toute valeur inconnue de la demande en `[Emplacement]` explicite (ex. `[Nom du destinataire]`), jamais inventée.
   - LC : conserver tous les montants, dates, conditions et obligations ; n'ajouter aucune information ; conserver les termes juridiques (les expliquer sans les remplacer) ; phrases courtes et mots courants.
2. **Nettoyage** (`core/nettoyage.py:133`, `data/nettoyage.py:162`) : la règle qui retire un titre ou intertitre de tête ne doit retirer ni le titre de section `Participants` d'un CR, ni le bloc expéditeur d'un CT. Exempter CR et CT de cette règle (le retrait du préambule « Voici » reste).
3. **Validateur** (`data validate`, `data/validate.py` : `:114`, `:119`, `:602`) : contrôles de structure, avec motif d'écart : CR sans l'une des quatre sections ; CT sans objet, sans formule de politesse ou sans emplacement entre crochets quand la demande en laisse ; LC dont un nombre ou une date de l'entrée manque à la sortie, ou qui contient un nombre absent de l'entrée (réutiliser l'extraction de fidélité existante).
4. **Mistral Large 4** : `mistral-large-4` dans `modeles_autorises` (`config/mistral.toml`) et dans `modeles_stables` (`config/donnees.toml:24`) **si** la règle de stabilité l'admet (c'est une préversion ; sinon, expliquer et proposer un drapeau) ; entrée `config/tarifs.toml` (1,36 $ / 4,18 $ par Mtok d'après des sources secondaires, commentaire « à vérifier »). Modèle du générateur choisi par la config ou une option, et **identifiant exact renvoyé par l'API** consigné au MANIFEST.
5. **Régénération des seules tâches CR, CT, LC** (comme RD seul en 9.12) : la commande existe-t-elle ? Sinon, la plus petite option qui la permet. Estimation du coût avant dépense.

## Tests
Gabarits : instructions présentes, aucune amorce de réponse. Nettoyage : CR et CT gardent leur tête, Q garde la règle. Validateur : chaque motif d'écart sur un cas fabriqué, et un cas conforme. Config : `mistral-large-4` accepté ; modèle inconnu refusé.

## Hors périmètre
Lancer la génération (session principale, après fusion, avec estimation) ; Q, RD, RE, CO, generique ; l'entraînement sur v12.

## Révision 1 (relecture de la spec, 19/10 22 h) — prime sur ce qui précède
1. **Ne pas toucher `config/prompts/taches/{CR,CT,LC}.md`** : ils servent aussi au prompt de la tâche évaluée (`evaluation/generation.py:113`) et au SFT (`data/build.py`). Seuls les gabarits du **générateur** (`config/prompts/generateur/`) changent. Retirer de `generateur/cr.md:18` l'interdiction de titre en première ligne pour CR (contradiction avec les sections).
2. **D1 et gabarits** : pas de « ex. », pas d'emplacement d'exemple (`core/gabarits.py:64`, `tests/mistral/test_gabarits_generateur.py:34`). Décrire la forme attendue en mots (« chaque information inconnue remplacée par un emplacement entre crochets qui nomme le champ »).
3. **Plafonds de mots** (`config/donnees.toml:101-105`) : CT relevé pour tenir le format complet (proposer une valeur et la justifier, ~250) ; CR inchangé à 400 tant qu'il tient sous la borne de 1 024 tokens du nettoyage.
4. **Modèle du générateur distinct** : `config/mistral.toml` `modele` sert aussi au second juge (`judge/second.py:112`). Ajouter un champ distinct (`modele_generateur`, défaut = valeur actuelle) avec son schéma, utilisé par `data generate` seul ; option CLI `--modele-generateur` si simple.
5. **Préversion** : `mistral-large-4` est une préversion, exclue par la règle des modèles stables (`config/mistral.toml:14-15`, `config/donnees.toml:23-24`, motif « preview »). Décision d'Anaël (19/10) : autorisé **pour le générateur seulement**, par une liste distincte `modeles_preversion_generateur = ["mistral-large-4"]` ; le MANIFEST du jeu porte `generateur_preversion = true` et l'identifiant exact renvoyé par l'API. Le second juge reste sur la liste stable.
6. **Validateur** : nouveaux motifs ajoutés à `MotifValidation` (`core/schemas/rejet_donnees.py:15-28`).
7. **Nettoyage** : passer la tâche à `analyser_cible`, `cible_nettoyable`, `ligne_nettoyee` (`core/nettoyage.py:116-149`) et à tous les appelants (`train/chargement.py`, `data/nettoyage.py`) ; `VERSION_NETTOYAGE` passe à 3 et s'ajoute à `VERSIONS_NETTOYAGE`, les jeux v4 à v12 restant vérifiés avec leur version d'origine (spec 9.10 l. 85).
8. **Régénération par tâche** : `data generate` n'a pas d'option par tâche. Ajouter `--taches CR,CT,LC` à `data generate` (seules ces sessions sont générées, le reste du jeu est repris du build source au build), ou le mécanisme le plus simple qui le permet ; le décrire.
9. **Budget** : ne touche pas `config/budgets.toml` (nouvelle campagne ouverte par la session principale, poste `mistral.generation` à 10 €). `config/tarifs.toml` : entrée `mistral-large-4` près des entrées Mistral existantes.
