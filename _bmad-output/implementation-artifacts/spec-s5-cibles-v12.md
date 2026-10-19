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
