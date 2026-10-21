---
title: 'Q : abstention quand aucun passage ne répond (story 16.8)'
type: 'feature'
created: '2026-10-21'
status: 'review'
---

## Intent

**Problem:** les 3 items `sans_reponse` de dev1 sont à 0 pour tous les modèles : la consigne Q demande déjà de dire qu'aucun passage ne répond, mais le modèle répond quand même, et le seuil 0,5 ne sépare pas les passages hors corpus.

**Approach:** un appel de vérification court au même modèle précède la réponse de Q (`harness/abstention.py`). Sur `non`, la réponse est un texte fixe. Activable par `[q_abstention]` dans `config/harnais.toml`, **désactivée par défaut** (décision de l'orchestrateur du 21/10 : la Baseline v2 et les essais de la nuit sont évalués sans abstention).

## Comportement

- `actif = false` (défaut) : Q est inchangée, avec un seul appel et aucun nouvel évènement. Le prompt principal `Q.md` reste en version 1, ce qui garde les runs comparables par `eval composer` et `eval comparer`.
- `actif = true` : Q fait d'abord un appel `generer` avec la consigne de vérification. Le message `user` est construit par `construire_messages`, avec les mêmes passages bornés et dédoublonnés que Q. Les options de décodage de l'appelant sont gardées, et l'appel impose `max_tokens = [q_abstention].max_tokens` (4) et `grammar = 'root ::= "oui" | "non"'`. Les jetons de cet appel ne sont pas diffusés à l'Agent.
- La lecture est stricte : seuls `oui` et `non` sont acceptés, sans tenir compte de la casse, des espaces ni d'un point final. Toute autre sortie vaut `illisible` et est traitée comme `oui`, pour ne jamais s'abstenir à tort.
- L'évènement `VerificationPassages(verdict, abstention, sortie)` (type `verification-passages`) est émis en premier. Avec `oui` ou `illisible`, la suite du flux est identique octet pour octet au flux sans abstention (test). Avec `non`, la réponse est `Jeton(phrase + ligne vide + orientation)`, puis `Sources([])`, l'avertissement juridique et `Fin(terminee, usage de l'appel de vérification)`.
- Sur un serveur local, la grammaire est transmise à llama-server (`grammar` ajouté à `OPTIONS_AUTORISEES`). Un modèle externe la reçoit sans la transmettre : `grammar` figure dans `OPTIONS_IGNOREES` de `client_openai`, que `ClientDistant` partage, et seul le `max_tokens` court part. En mode hybride, la cascade se décide dès l'appel de vérification, qui est le premier appel de l'échange.
- Mesure : l'appel passe par `ctx.llm.generer`. Il reçoit donc une `MesureAppel` de l'observateur (17.6) et le plafond de dépense le réserve sur `max_tokens = 4`. Le délai jusqu'au premier jeton mesuré par le service inclut cet appel.
- Évaluation : `Generation.verdict_passages` (`oui`, `non`, `illisible` ou `None`) recopie l'évènement de la trace. Ce champ est hors de `sortie_canonique` et hors de la clé du cache des verdicts.

## Textes fixes, à relire par Anaël

Ils sont dans `config/prompts/q-abstention.toml`, un fichier séparé avec sa propre version (1). Ce sont des textes de produit : ils n'entrent dans aucune donnée d'entraînement (D1).
- Consigne de vérification : « Tu vérifies si les passages de l'Index local fournis dans le message permettent de répondre à la question d'un Agent du service public. » Suivent quatre puces : oui si au moins un passage répond, même en partie ; non si aucun ne traite la question ; aucune connaissance extérieure ; un seul mot en minuscules, sans ponctuation.
- Phrase d'abstention : « Les passages de l'Index local ne permettent pas de répondre à cette question. »
- Orientation : « Consultez la page officielle de la démarche ou adressez-vous au service compétent. » Elle ne contient volontairement aucune URL, sans quoi le contrôle la compterait comme inventée.

## Auto Run Result

- Tests ajoutés : `tests/harness/test_abstention.py` (14 tests), plus un test chacun dans `test_client.py`, `test_client_openai.py`, `test_modele_distant.py` et `test_generation.py`. Les suites ciblées harness, inference, core, evaluation, app et packaging (hors `integration`) passent : 2272 tests verts.
- Décision simple : l'appel de vérification a lieu même sans aucun passage (le modèle voit `AUCUN_PASSAGE`). Pas de court-circuit, pour garder un seul chemin.
- Décision simple : la conversation (historique) est jointe à l'appel de vérification, comme pour Q.
- Décision simple : le fichier de textes est un TOML (`schema_version`, `version`, `verification`, `phrase`, `orientation`) et non un gabarit `.md`, parce qu'un gabarit n'admet que Consigne et Emplacements. À confirmer par Anaël.
- La section `[q_abstention]` est ajoutée en fin de `config/harnais.toml`, sans changer la version du harnais. 16.3 ajoute `[anti_boucle]` à côté : un conflit de fusion trivial est possible dans `harness/config.py`.
- Reports :
  - mesure de latence sur CPU (`measure run`, cible : 0,5 s au plus ajoutée au premier jeton) ;
  - Baseline dev1 et dev2 sans puis avec abstention (règle de décision de l'epic) ;
  - rejeu des scores bge-m3 ;
  - affichage éventuel du verdict dans l'interface (aujourd'hui, l'évènement est ignoré par le bus).

## Revue

- low, corrigé : `verdict_passages` omis de la ligne `Generation` quand il vaut `None` (abstention désactivée = lignes identiques à avant) ; test.
- low, corrigé : doublon de `VerificationPassages` supprimé de `_TYPES_EVENEMENTS` (service).
- low, corrigé : l'usage de l'appel de vérification est cumulé dans le `Fin` (abstention et réponse) ; sur `non`, `Fin.raison` reflète une vérification coupée (`longueur`) ; tests.
- low, corrigé : `Erreur` ou `AppelOutil` pendant la vérification consigné au journal du harnais (type seul, sans contenu) et traité comme `illisible` (donc `oui`) ; test.
- rejeté : D1, secrets, réseau, budget d'API : rien à signaler (textes fixes dans `q-abstention.toml`, hors données d'entraînement, aucun appel de plus quand `actif = false`).
