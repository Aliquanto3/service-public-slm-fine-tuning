---
title: 'O4c — suite de dev1 après la contre-vérification croisée'
type: 'bugfix'
created: '2026-10-20'
status: 'review'
context: ['{project-root}/_bmad-output/implementation-artifacts/spec-o4-jeu-dev.md']
warnings: []
deferred: []
---

## Intent

**Problème :** la contre-vérification croisée de dev1 (DeepSeek V4 Pro, GLM-5.3) a laissé 54 items `incomplet` (52 « glm : pas de verdict valide », 2 erreurs d'appel DeepSeek sur CR-509 et CR-516) et 30 `rejete`. Règles 3 et 4 de `spec-o4-jeu-dev.md` : un item jugé ambigu ou incohérent par l'un des deux juges est écarté, ou corrigé puis revérifié par les deux.

**Approche :** diagnostiquer les verdicts manquants dans le journal des juges tiers et corriger l'outil ; trier les 30 rejets (corriger l'item ou contester un rejet infondé, avec justification) ; réassembler, contrôler le gel et la disjonction. Aucun appel payant : l'orchestrateur relance la vérification.

## Diagnostic GLM (journal `appels-juges-tiers.sqlite`, sessions `jeu-croise-*`)

`ouvrir_appelant` n'envoyait ni `reasoning`, ni `temperature`, ni le schéma : seulement `response_format: json_object`. Sans borne d'effort, GLM a raisonné jusqu'à `max_tokens` : 50 sorties vides, `finish_reason: length`, 8 000 tokens. Les 2 autres sont des sorties `stop` illisibles : `{}` et du texte incohérent. Les 4 erreurs DeepSeek (CR-509, CR-516, deux tentatives chacune) sont des dépassements du délai de lecture, à 5 minutes d'intervalle. Le juge tiers de notation (`JugeTiers._parametres`, effort `low`, `json_schema`) n'a été coupé que 4 fois sur 620 appels GLM.

## Livré

- `eval/outils/verifier_jeu_croise.py` :
  - `parametres_appel(config)` reprend la configuration de `juges.toml`, comme `JugeTiers._parametres` : température, `reasoning.effort`, schéma strict `SCHEMA_VERDICT` (ou `json_object` selon `format_reponse`) et `require_parameters`.
  - Une relance corrective (`RELANCES_MAX = 1`) après une sortie sans verdict valide.
  - Consigne neutre, la même pour tous les items (`VERSION_PROMPT = 3` après revue, champ `version_prompt` des verdicts) : seules deux précisions factuelles sur le format, où se trouve la grille (clés de notation de chaque Tâche, dont `points_cles_reference`) et ce qu'est la source (provenance, texte fourni en entrée ; pour un item fictif, son entrée). La version 2, qui disait qu'une rédaction ouverte « ne rend pas l'item ambigu », est retirée (revue).
  - Un verdict n'est repris qu'à empreinte et consigne égales : tous les items sont revérifiés avec la consigne 3. Pour un item `incomplet` inchangé, seuls les juges sans verdict valide sont rappelés.
  - Plus de voie d'appel (revue) : `contestations.jsonl` reste une trace du raisonnement de l'auteur, sans effet sur les outils. Un rejet n'est levé que par une correction de l'item (`version_item` + 1, verdict de construction) retenue ensuite par les deux juges.
- `eval/outils/construire_jeu.py` : `assembler` et `composition` lisent `verdicts-croises.jsonl` ; un item dont le dernier verdict croisé, sur son empreinte et avec la consigne courantes, est `rejete` est retiré de `items.jsonl` (revue). `contestations.jsonl` est un fichier annexe, jamais lu comme brouillon.
- `slmsp eval gel --statut relu-llm` exige pour chaque item d'`items.jsonl` un dernier verdict croisé `retenu` par au moins deux juges sans grief, sur son `item_sha256` courant et avec la consigne courante (`cfg.VERSION_CONSIGNE_CROISEE`, alignée sur l'outil par un test). Une Tâche passée sous 20 items fait échouer le gel par l'écart de composition (revue).
- Items, en `version_item` 2, chacun avec un verdict de construction O4c dans `verification/` :
  - 13 rejets corrigés : Q-502, Q-503, Q-507, Q-518 et Q-519 (extraits complétés des passages élidés qui portent les faits de la référence, relus dans les chunks) ; NR-505 (parenthèse sans source retirée) ; NR-511 (signature inventée) ; CR-504 (responsable « non précisé ») ; CT-503 (élément « prévenir en cas d'empêchement » ajouté à l'entrée) ; LC-520 (informations à conserver complétées) ; RE-503 et RE-515 (public de la consigne rendu cohérent avec les points clés) ; CO-516 (coquille de la source « délais de prescriptions » corrigée hors faute, positions recalculées).
  - 4 items `incomplet` dont le grief DeepSeek était fondé, corrigés aussi : Q-504, Q-511 et Q-512 (extraits complétés) ; CT-510 (éléments obligatoires alignés sur l'entrée).
- 17 rejets contestés par l'auteur et laissés tels quels, justification dans `contestations.jsonl` (trace sans effet : ils sont revérifiés comme les autres et écartés si l'un des juges les rejette encore) : CR-506, CR-507, CR-513, CT-513, CT-515, LC-504, LC-506, NR-506, NR-512, NR-516, NR-517, NR-519, NR-520, RE-504, RE-513, RE-516 et RE-518. Ce sont des « ambigu » attribués à une rédaction ouverte, une « grille absente » alors qu'elle est portée par `points_cles_reference`, un fait présent dans l'entrée ou le chunk cité, et un décompte de dates juste.
- `eval/jeu/dev1/items.jsonl` réassemblé (SHA-256 `256a26ce…`). `eval gel --version dev1 --verifier-seulement` : 0 erreur, 0 écart. Disjonction (items du worktree contre les données du dépôt principal) : 0 conflit.

## Auto Run Result

Statut : review. Tests ciblés : `tests/eval_outils`, `tests/judge`, `tests/evaluation`.

À revérifier après revue : les 160 items, par les deux juges, avec la consigne 3 (aucun verdict v1 ou v2 repris). Commande de l'orchestrateur : `python eval/outils/verifier_jeu_croise.py verifier --version dev1 --juges deepseek,glm`, puis `python eval/outils/construire_jeu.py assembler --version dev1` (retire les rejetés) et `slmsp eval gel --version dev1 --statut relu-llm --graine <g>`. Coût estimé : 320 appels, DeepSeek à environ 0,0075 $ et GLM à environ 0,002-0,004 $ par appel avec un effort `low`, soit environ 1,7 $ ; pire cas avec une relance par appel : environ 4 $.

Décisions :
- Consigne (orchestrateur, revue) : une seule consigne neutre pour tous les items (version 3), sans phrase qui pousse à l'acceptation ; tous les items sont revérifiés.
- Contestations (orchestrateur, revue) : aucune voie d'appel ; un item rejeté par l'un des juges est écarté, sauf correction retenue ensuite par les deux.
- Quand l'extrait d'une Q élidait un fait présent dans la fiche, il a été complété plutôt que la référence amputée. Q-518 (chunk 6 de F24569) : ajout de « L'eau et le pain sont disponibles en libre accès. Le sel et les sauces sont servis en fonction des plats. » et de la note « (À noter: il n'y a pas de collation au collège et au lycée.) » ; restent élidés, marqués par « […] », « Ils ne sont pas librement accessibles. Les menus de l'établissement scolaire sont généralement disponibles sur son site internet. » et « Selon l'établissement, les repas sont préparés sur place ou en cuisine centrale. ».
- LC-509, LC-516, LC-517 et CO-514 (`incomplet`, griefs DeepSeek infondés ou erronés : « lieu de résistance » et « passeport » sont absents de l'item) n'ont pas été modifiés : ils sont revérifiés avec la consigne 3.

Reports : gel `relu-llm` après la revérification ; chaque Tâche compte 20 items, donc tout rejet fait échouer le gel tant que l'item n'est pas corrigé ou remplacé. Le rapport de vérification croisée n'est pas intégré au MANIFEST (report O4b toujours ouvert).

## Revue

Détail : `revue-o4c.md`.
- high, corrigé : consigne v2 orientée vers l'acceptation et réservée aux items à refaire ; consigne neutre v3 pour les 160 items.
- high, corrigé : retenus de la consigne v1 jamais revérifiés ; tout verdict d'une autre consigne est refait.
- high, corrigé : voie d'appel par `contestations.jsonl` retirée (trace sans effet).
- high, corrigé : verdicts croisés sans effet sur l'assemblage et le gel ; rejet courant retiré à l'assemblage, « retenu » courant exigé au gel `relu-llm`.
- medium, corrigé : traçabilité de Q-518.
- medium, corrigé : budget de revérification (environ 1,7 $, pire cas environ 4 $).
- low, rejeté : constante de consigne en trois endroits, égalité testée.
