---
title: 'Story S5 — Cibles v12 conformes à la grille (CR, CT, LC), Mistral Large 4'
type: 'feature'
created: '2026-10-19'
status: review
baseline_revision: '224c51d'
---

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

## Implémentation

2026-10-19, Opus (dev-story). Aucun appel payant, aucun réseau ; `.env` non lu.

- **Gabarits du générateur** (seuls `cr.md`, `ct.md`, `lc.md` passent en version 3 ; `config/prompts/taches/` intact) : consignes seules, sans exemple, sans crochet ni emplacement d'exemple, sans guillemets.
  - CR : quatre sections dans l'ordre, titre seul sur sa ligne (Participants, Points abordés, Décisions, Actions) ; toutes les décisions et actions, une par ligne, responsable et échéance quand la transcription les donne, sinon « non précisé » dit en mots ; un point sans décision n'est jamais présenté comme décidé ; section gardée même vide. L'interdiction de titre en première ligne est remplacée par « commence par le titre de la section Participants ».
  - CT : neuf blocs dans l'ordre de la grille ; ligne d'objet commençant par le mot Objet ; chaque information absente des éléments connus remplacée par un emplacement entre crochets qui nomme le champ ; références en emplacement si inconnues ; formule de politesse complète puis signature ; commence par le bloc expéditeur.
  - LC : tous les montants, dates, durées et références repris avec leurs valeurs exactes ; aucune information ajoutée (ni fait, chiffre, date, démarche, coordonnée, conseil) ; termes juridiques gardés et expliqués sans remplacement. La consigne « signale le passage gardé après le texte réécrit » est retirée (elle ajoutait du texte hors source et doublait la règle des termes juridiques).
- **Plafonds** (`config/donnees.toml`) : CT 150 → 250 (neuf blocs : ~60 mots d'en-tête et de formules plus un corps de 150 à 190 mots ; v11 au format incomplet : médiane 152). CR inchangé à 400 (≈ 650 tokens, sous la borne de 1 024).
- **Nettoyage** (`core/nettoyage.py`) : `VERSION_NETTOYAGE = 3`, `VERSIONS_NETTOYAGE = {1, 2, 3}`, `TACHES_TETE_GARDEE = {CR, CT}`. `analyser_cible` et `nettoyer_cible` prennent `tache` ; `ligne_nettoyee` lit le champ `tache` de la ligne SFT (nouvelle aide `tache_de`), donc `verifier_nettoyage` et `train/chargement.controler_nettoyage` n'ont pas changé de signature ; `data/nettoyage._nettoyer` passe la tâche. Les jeux v4 à v11 restent vérifiés avec leur version (1 ou 2).
- **Validateur** (`data/validate.py`, `_controler_structure`, après les contrôles de valeurs) : motifs `cr_sections_manquantes` (titre en tête de ligne, seul ou suivi de `:`, marques Markdown et casse ignorées), `ct_format_incomplet` (ligne `Objet :`, formule de politesse par mots-clés agréer, salutations, considération, sentiments, cordialement, respectueusement, et au moins un `[…]` contenant une lettre, hors lien Markdown), `lc_valeur_perdue` (nombre notable ou date de l'entrée absent de la sortie, extraction `_nombres_notables` et `_dates` existante ; le nombre ajouté reste `valeur_absente`). Motifs ajoutés à `MotifValidation`.
- **Modèle du Générateur** : `config/mistral.toml` gagne `modele_generateur` (défaut `mistral-large-latest`) et `modeles_preversion_generateur = ["mistral-large-4"]` (schéma `ConfigMistral` : disjointe de la liste stable, `modele` ne peut pas être une préversion). `ConfigMistral.pour_generateur(modele)` rend la copie du client du Générateur ; `refus_modele` d'une copie en préversion admet la préversion et ses identifiants résolus `<préversion>-<suffixe>`. Le second juge garde `charger_mistral()` non modifié. `PrealablesGeneration.admet` remplace les quatre tests `in modeles_stables` (générateur, sessions). `config/tarifs.toml` : `mistral-large-4`, direct 1,36 $ / 4,18 $ par Mtok, « à vérifier par Anaël ».
- **MANIFEST** : le run `data-generate` consigne `modele_generateur`, `generateur_preversion`, `taches`, `completer_depuis` ; le MANIFEST du jeu porte `generateur_preversion = true` (omis quand faux : MANIFEST existants inchangés) quand un identifiant de `modeles_generateurs` (exact, renvoyé par l'API) est hors de `modeles_stables`. Le nettoyage le recopie (`model_copy`).
- **Régénération par Tâche** (`data generate`) : `--taches CR,CT,LC` ne planifie que ces Tâches ; `--completer-depuis GENERATE_RUN_ID` (même seed, run terminé) recopie sans appel les lignes `plan`, `brut`, `abandons` et amorces dérivées des sessions closes des autres Tâches. Le run produit est un run `data-generate` ordinaire : `validate`, `filter`, `build` et le nettoyage n'ont pas changé. `--modele-generateur MODELE` remplace la config ; à la reprise, le modèle du run est repris, un autre est refusé.
- **Réutilisation du journal** : une réponse journalisée n'est réutilisée que si elle a été demandée au modèle du client (`reponse_journalisee`, `sessions._reutilisable`, `appels_journalises` de l'estimation). Sans ce filtre, un Générateur sur `mistral-large-4` avec des gabarits inchangés aurait repris les réponses de `mistral-large-latest`. Les amorces Mistral du seed restent admises (`_ligne_admise` inchangé hors préversion).
- **Tests** : `tests/data/test_validate_structure.py`, `test_nettoyage_v3.py`, `test_generate_s5.py` (plan limité, composition sans appel puis validate → filter → build, préversion au MANIFEST, autre seed refusé, reprise sur un autre modèle refusée, modèle résolu hors préversion refusé), `tests/mistral/test_config_generateur.py` (config, préalables, tarif), gabarits (`test_consignes_s5`, versions). Réalignés : `test_build.py` (réponses CR et CT factices structurées), `test_validate.py` (CR conforme), `test_nettoyage.py` (version 3), `test_config_donnees.py` (CT 250), `conftest.py` (tarif et option `modele_generateur` du faux client).
- Tests ciblés `tests/data tests/train tests/mistral tests/core tests/cli/test_data.py tests/test_architecture.py` : verts (857 + 1 150). Ruff et format verts. `outils/controle_rapide.py` non exécutable dans le worktree (`uv run` sans venv local) ; ses deux étapes lancées à la main (ruff, test d'architecture). Suite complète non lancée (consigne).

### Commandes de la régénération v12 (session principale, après fusion)

Prérequis : conditions Mistral du jour (`conditions_verifiees_le`, D1.2), campagne et poste `mistral.generation` ouverts dans `config/budgets.toml`, tarif `mistral-large-4` vérifié. Seed et génération source : ceux de v11 (`etat-campagne-v11.md`).

```
uv run slmsp data generate --depuis 20261017-111645-seed-b335 --modele-generateur mistral-large-4 --taches CR,CT,LC --completer-depuis 20261019-180544-generate-bd87
uv run slmsp data validate --depuis <GENERATE_RUN_ID>
uv run slmsp data filter --depuis <VALIDATE_RUN_ID>
uv run slmsp data build --depuis <FILTER_RUN_ID> --variante diffusable
uv run slmsp data build --nettoyage --depuis <BUILD_RUN_ID> --modele base:minicpm5-2b
```

`data generate` affiche l'estimation par gabarit avant le premier appel ; l'arrêter si elle dépasse le budget. Les sessions Q, RD, generique, RE et CO sont reprises de v11 (aucun appel, ni Index ni MCP sollicités). Les transcriptions CR sont régénérées aussi : le `session_id` de CR hache toute la chaîne de gabarits (même constat que 9.10). Le jeu nettoyé est en `nettoyage.version = 3` ; il prend le numéro **v13** (v12 est le sous-ensemble de S2). Le run source `20261019-180544-generate-bd87` (seed `b335`, statut `complet`) et le slug `base:minicpm5-2b` sont ceux du nettoyage v11 (`20261019-194543-nettoyage-c782`). La sortie de `generate` signale les sessions non closes du run source, et `validate` affiche `observations` (CT sans emplacement).

### Estimation du coût (avant dépense)

Volumes v11 : CR 80 sessions (2 appels : transcription puis compte rendu), LC 80, CT 35 ; 275 appels. Tarif `mistral-large-4` 1,36 $ / 4,18 $ par Mtok, dollar au pair.

| Appel | Entrée (tokens) | Sortie (tokens) | Sessions |
|---|---|---|---|
| Transcription CR | 800 | 1 500 | 80 |
| Compte rendu CR | 2 000 | 800 | 80 |
| LC | 800 | 300 | 80 |
| CT | 700 | 450 | 35 |

Total ≈ 310 k tokens d'entrée (0,42 $) et 225 k de sortie (0,94 $) : **≈ 1,4 €** ; avec 30 % de marge (relances, abandons) **≈ 1,8 €**. Pire cas au `max_tokens` des gabarits (4 000, 1 600, 800, 800) : ≈ 0,4 $ d'entrée + 80 × 5 600 + 115 × 800 = 540 k tokens de sortie (2,3 $), **≈ 2,7 €**. Le contrôle de fidélité optionnel (`validate --controle-mistral`) s'ajoute, au tarif de `mistral-large-latest`.

## Auto Run Result

Décisions prises seul (solution la plus simple et la plus réversible) :
1. **Préversion admise par préfixe** : le modèle résolu est admis s'il vaut `mistral-large-4` ou `mistral-large-4-<suffixe>`, motifs interdits non appliqués à la préversion déclarée (l'identifiant réel renvoyé par l'API n'est pas connu). Un autre identifiant est refusé après l'appel (journalisé). **À confirmer par Anaël.**
2. **Mécanisme par Tâche** : composition au niveau de `generate` (`--completer-depuis`) plutôt qu'au `build` : un seul run aval, aucune modification de `validate`, `filter`, `build` ni du MANIFEST du jeu au-delà de `generateur_preversion`.
3. **Réutilisation filtrée par modèle demandé** (voir Implémentation) : changement de comportement limité à un Générateur dont le modèle diffère des lignes journalisées ; les runs existants (toujours `mistral-large-latest`) ne changent pas.
4. **CT sans emplacement rejeté sans condition** : le gabarit `amorces-ct` demande des éléments connus incomplets, la demande laisse donc toujours au moins un champ inconnu. **À confirmer par Anaël** (rejets possibles si Mistral juge une demande complète).
5. **Formule de politesse** reconnue par mots-clés ; **sections CR** reconnues en tête de ligne, seules ou suivies de `:` (plus tolérant qu'un titre seul sur sa ligne, pour éviter des rejets payés sur une mise en forme).
6. **LC** : consigne de signalement des passages gardés retirée (décision de fond sur la formulation envoyée à Mistral). **À confirmer par Anaël**, comme le libellé de toutes les consignes CR, CT, LC avant la génération réelle.
7. **CT 250 mots** : valeur proposée, à ajuster sur le jeu régénéré.

Reports :
- `data seed` (scénarios, courriers) reste sur le modèle stable `modele` ; l'option `--modele-generateur` ne vaut que pour `data generate`.
- Mesurer sur le run réel le taux de rejet des trois nouveaux motifs et l'écart entre l'estimation affichée et le registre.

## Revue

2026-10-19, Opus (reviewer), une passe, après rebase sur main (conflit `config/tarifs.toml` : entrées juges tiers S3 et `mistral-large-4` gardées). Aucun appel payant, `.env` non lu.

- [medium] Préversion admise par préfixe libre (`mistral-large-4-preview-beta` admis) : **corrigé**. `preversion_admise` n'admet que le nom exact ou un suffixe de version numérique (`-0`, `-2610`, `-4-0`), et les `motifs_interdits` s'appliquent hors nom exact (`refus_modele` du client et `PrealablesGeneration.admet`). L'identifiant exact résolu reste consigné au MANIFEST (`modeles_generateurs`).
- [medium] Sections CR au libellé exact (faux rejets « Décisions prises », « Actions à mener ») : **corrigé**. Titre en tête de ligne qui commence par le libellé de section (casse, `#`, `*`, `_`, numérotation ignorés), suite libre.
- [medium] « Objet du courrier : » non reconnu : **corrigé** (`objet` suivi d'au plus 40 caractères puis `:`).
- [low] LC : valeur reprise en lettres tenue pour perdue : **corrigé**. Nombres en lettres courants (0 à 99, centaines simples, mille) acceptés à la sortie pour `lc_valeur_perdue` ; `valeur_absente` (aucun nombre nouveau) inchangé.
- [low] Sessions non closes du run source abandonnées sans signal : **corrigé**. Comptées par Tâche (`comptes_plan.<T>.non_closes_source`, bilan) et signalées à la sortie.
- [low] CT rejeté sans emplacement entre crochets sans condition : **corrigé**. La demande CT ne dit pas quels champs sont inconnus (`amorces-ct` : « certaines informations peuvent manquer ») : plus de rejet pour ce seul motif, observation `ct_sans_emplacement` comptée dans `rapport.json` (`observations`) et affichée. Remplace la décision 4 de l'Auto Run Result.
- Gabarits `cr`, `ct`, `lc` contre `eval/grille-juge-v1.md` : conformes (CR : quatre sections, toutes décisions et actions, responsable et échéance ; CT : neuf blocs, emplacements ; LC : fidélité stricte, termes juridiques, phrases courtes). D1 : aucune amorce, aucun exemple, aucun crochet ni guillemet : **rien à signaler**.
- `config/prompts/taches/` intact ; nettoyage v3 : la Tâche ne compte qu'en version 3, v4 à v12 (versions 1 et 2) inchangés : **rien à signaler**.
- Tests ciblés (`tests/data tests/mistral tests/core tests/train tests/cli/test_data.py tests/test_architecture.py`) : 2 033 verts ; ruff et format verts. `outils/controle_rapide.py` non exécutable dans le worktree (`uv run` sans venv local), ses étapes lancées à la main.
