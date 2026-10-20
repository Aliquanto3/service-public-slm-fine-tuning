# Brouillons du jeu de développement dev1

Jeu de **développement** (spec O4, story O4b) : 160 items, 20 par Tâche (difficultés 7 / 7 / 6), identifiants à partir de 501. Il sert aux décisions (hyperparamètres, mélange, routage) ; v1.1 reste réservé à la mesure finale. Il n'est jamais utilisé pour l'entraînement (SPEC §1.1) : Claude a rédigé les items d'**évaluation** (SPEC §1.4), aucune donnée d'entraînement.

Même schéma et même procédé que v1.1 (`eval/construction/v1.1/README.md`) : brouillons `<CODE>.jsonl`, verdicts du second passage dans `verification/<CODE>.jsonl` (ajout seul, le dernier verdict l'emporte), assemblage par `construire_jeu.py assembler --version dev1`.

## Sources (consultées le 2026-10-20)

- **Q, LC, RE, CO (textes réels), NR (faits)** : MediaTech `AgentPublic/service-public` (rév. 29f236f8a5), fiches non citées par v1.0 ni v1.1 ; extraits vérifiés textuellement dans les chunks. **LC difficiles, CT** : MediaTech `AgentPublic/legi` (rév. 68b01fbbe0), articles du CASF, du code civil, du CGCT et du CRPA non cités par v1.x.
- **Amorces Q** : 12 questions de `AgentPublic/sp_questions_corpus` (rév. 495a22cf7b, lignes Excel), absentes des amorces des runs seed. La provenance cite le dépôt et la révision sans URL de fichier (l'URL du fichier, commune à tout le corpus, est déjà citée par v1.1).
- **RD** : cassettes `eval/cassettes/RD-501` à `RD-520`, enregistrées le 2026-10-20 par `slmsp mcp record` (profil `outillage`, MCP data.gouv) ; RD-502 et RD-513 : cassettes de panne (`delai_depasse`), référence tirée du catalogue local `AgentPublic/data-gouv-datasets-catalog` (rév. 11f3d3c948). La provenance nomme le serveur MCP (`serveur`) sans `url`, commune à tous les items RD de v1.1.
- **CR, CT, CO (textes fictifs), NR (raisonnement, consignes)** : contenus fictifs rédigés pour l'évaluation (`fictif: true`). Les CO réels sont aussi `fictif: true` (fautes injectées), ponctuation normalisée.

## Composition

`slmsp eval gel --version dev1 --verifier-seulement` : 160 items stricts, 0 erreur, 0 écart avec `CIBLES_DEV` (Q sans réponse 3, amorces réelles 12, RD valeurs 5 et repli 2, 12 producteurs, 4 CR de plus de 4 000 mots, thèmes 24 / 12 / 12 / 12 / 12 / 8).

## Disjonction

`verifier_jeu_croise.py disjonction --version dev1` : disjoint de v1.0, v1.1, `data/train/v*/train.jsonl` et `preferences.jsonl`, et des amorces `runs/data-seed/*/amorces.jsonl` (URL, document source : fiche, article LEGI ou ligne de corpus, textes identiques, inclusion de 5-grammes au seuil 0,5). Corrections faites pendant la construction : Q-502, RE-503, RE-505 et RE-518 (titres courts d'amorces seed contenus dans le texte), dates et horaires CT identiques à v1.0. Le type de courrier CT (vocabulaire fermé) n'entre plus dans la comparaison.

## Second passage

Relecture séparée de chaque item contre sa source (nombres des références retrouvés dans la source, calculs refaits, dates et jours de la semaine contrôlés). 2 rejets sur 162 verdicts : RD-519 (glose absente de la source) et CT-520 (dispositions prévoyant la formalité non fournies), corrigés en `version_item` 2 puis acceptés.

## Relecture Claude (revue O4b)

Échantillon de 24 items (3 par Tâche) relu contre les sources, plus des contrôles automatiques des 160 items (`tests/eval_outils/test_items_dev1.py`) : 8 items corrigés en `version_item` 2 (LC-503, LC-508, LC-509, LC-511, LC-512 : termes à conserver absents du texte ; RD-502, RD-513 : identifiant du catalogue ; CO-518 : faute à deux corrections justes). Détail : `_bmad-output/implementation-artifacts/revue-o4b.md`.

## Contre-vérification croisée et suite (O4c)

Premier passage (DeepSeek V4 Pro, GLM-5.3) : 76 retenus, 30 rejetés, 54 incomplets. Les incomplets venaient de l'outil : il n'envoyait pas l'effort de raisonnement, et GLM coupait 50 sorties vides à 8 000 tokens. Les paramètres du juge sont désormais transmis, avec une relance corrective et une consigne neutre unique (version 3, revue O4c). Sur les 30 rejets, 13 sont corrigés en `version_item` 2 ; 17 sont contestés par l'auteur dans `contestations.jsonl`, simple trace sans effet sur les outils. 4 items incomplets, dont le grief DeepSeek était fondé, sont aussi corrigés. Un item rejeté par l'un des juges est retiré à l'assemblage, sauf correction retenue ensuite par les deux ; le gel `relu-llm` exige un verdict croisé « retenu » courant pour chaque item. Détail : `_bmad-output/implementation-artifacts/spec-o4c-dev1-suite.md`.

## Reste à faire (orchestrateur)

Revérification payante des 160 items avec la consigne 3 (`verifier_jeu_croise.py verifier --version dev1 --juges deepseek,glm`, environ 1,7 $, pire cas environ 4 $), réassemblage (`construire_jeu.py assembler --version dev1`), remplacement des items rejetés, puis gel `relu-llm`.
