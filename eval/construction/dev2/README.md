# Brouillons du jeu de développement dev2

Jeu de **développement** (spec O4, story 15.5) : 160 items, 20 par Tâche (difficultés 7 / 7 / 6), identifiants 601 à 620. Il double dev1 pour les décisions (hyperparamètres, mélange, routage) ; v1.1 reste réservé à la mesure finale. Il n'est jamais utilisé pour l'entraînement (SPEC §1.1) : Claude a rédigé des items d'**évaluation** (SPEC §1.4), aucune donnée d'entraînement. Les items ont été écrits sans consulter de run de génération ni de notation.

Même schéma et même procédé que dev1 (`eval/construction/dev1/README.md`) : brouillons `<CODE>.jsonl`, verdicts du second passage dans `verification/<CODE>.jsonl`, assemblage par `construire_jeu.py assembler --version dev2`. Statut : **brouillon**, non gelé.

## Sources (consultées les 20 et 21 octobre 2026)

- **Q, LC, RE, CO (textes réels), NR (questions)** : MediaTech `AgentPublic/service-public` (rév. 29f236f8a5), fiches non citées par v1.0, v1.1 ni dev1, et dont les chunks recouvrent peu les jeux d'entraînement et les amorces seed ; chaque fiche n'est utilisée qu'une fois dans dev2. Extraits, documents et textes recopiés du champ `text` des chunks.
- **Amorces Q** : 10 questions de `AgentPublic/sp_questions_corpus` (rév. 495a22cf7b, lignes Excel), non citées par v1.x ni dev1. Q sans réponse (3) : absence revérifiée par recherche plein texte, motifs consignés dans `verification_absence`.
- **LC difficiles, CT** : MediaTech `AgentPublic/legi` (rév. 68b01fbbe0), articles en vigueur du CASF, du code civil, du CGCT et du CRPA non cités par v1.x ni dev1 ; texte des articles fourni verbatim (`elements_connus.texte_applicable` pour les CT).
- **RD** : cassettes `eval/cassettes/RD-601` à `RD-620`, enregistrées le 2026-10-20 par `slmsp mcp record` (MCP data.gouv) ; RD-602 et RD-613 : cassettes de panne (`delai_depasse`), référence tirée du catalogue local `AgentPublic/data-gouv-datasets-catalog` (rév. 11f3d3c948). Jeux distincts de ceux de v1.x et dev1 ; les faits de chaque référence figurent dans l'extrait de cassette cité en provenance.
- **CR, CT, CO (6 textes fictifs), NR (consignes)** : contenus fictifs rédigés pour l'évaluation (`fictif: true`). Les CO réels sont aussi `fictif: true` (fautes injectées), ponctuation et espaces normalisés.

## Précautions tirées des rejets de dev1

- CR : consigne commune conservée (participants, points abordés, décisions, actions) ; aucune décision n'est aussi un piège ; dates contrôlées (jour de la semaine, année) et toute date ou année d'une référence figure dans le texte.
- NR : une seule réponse juste (ordre, format, casse, absence d'ajout imposés par la consigne et repris dans les critères).
- Q, RE : chaque fait de la référence ou des points clés figure dans l'extrait ou le document ; consignes RE nommant les sujets attendus et le public.
- CT : expéditeur fourni dans `elements_connus`, éléments obligatoires alignés sur les éléments connus.
- Aucun plaidoyer adressé aux juges, ni dans les items ni dans un fichier annexe.

## Composition

`slmsp eval gel --version dev2 --verifier-seulement` : 160 items stricts, 0 erreur, 0 écart avec `CIBLES_JEU_DEV_COMPLET` (Q sans réponse 3, amorces réelles 10, RD valeurs 5 et repli 2, 16 producteurs, 4 CR de plus de 4 000 mots).

## Disjonction

`verifier_jeu_croise.py disjonction --version dev2 --reference <dépôt principal>` : disjoint de v1.0, v1.1, dev1, `data/train/v*/train.jsonl` et `preferences.jsonl` (dont v18), et des amorces des runs seed (dont `20261020-093126-seed-4fcf`). Corrections faites pendant la construction : LC-616 (article remplacé, recouvrement avec une amorce seed courte), CR-617 (expression reprise d'une amorce seed), CT (dates, heures et intitulés identiques à v1.0 ou dev1).

## Second passage

Contrôles automatiques sur les 160 items (`tests/eval_outils/test_items_dev1.py`, étendu à dev2) et relecture contre les sources : 160 verdicts `accepte` dans `verification/`.

## Contre-vérification croisée et corrections 15.5b

DeepSeek + GLM, consigne 3 : 130 retenus, 26 rejetés, 4 incomplets (LC-615 à LC-618, erreurs de transport, non modifiés). Sur les 26 rejets, sans plaidoyer :
- 19 corrigés (`version_item` 2, verdict de construction 15.5b dans `verification/`) : 6 RD dont l'extrait de provenance ne citait que le dernier appel (il cite désormais aussi `search_datasets`), Q-609, Q-612, Q-613, NR-606, LC-619, CO-618, CR-619 et 6 RE (points clés alignés sur la consigne et le document).
- 2 remplacés par des textes fictifs neufs de même Tâche, difficulté et thème : CO-606 → CO-621, CO-613 → CO-622 (textes déjà fictifs, griefs factuellement inexacts) ; les remplacés gardent un verdict `rejete` dans `verification/`.
- 5 laissés tels quels pour la décision d'Anaël (signalés à l'orchestrateur) : CO-615 (texte réel, Licence Ouverte, convention G4 : grief inexact, « prévoire » est bien corrigé) ; CO-609 (`fictif` vrai pour un texte réel à fautes injectées, arbitrage G4) ; CT-602, CT-612 et CT-614 (formules d'appel et de politesse, rédaction ouverte, communes aux 20 CT).

Détail : `_bmad-output/implementation-artifacts/spec-15-5b-dev2-corrections.md`.

Revérification ciblée : 152 retenus, 3 LC rejetés (615, 616, 619 : grille trop résumée). Corrigés en 15.5c, grille au plus près des articles ; détail : `_bmad-output/implementation-artifacts/spec-15-5c-dev2-lc.md`.

## Reste à faire (orchestrateur)

Contre-vérification croisée DeepSeek + GLM (`verifier_jeu_croise.py verifier --version dev2 --juges deepseek,glm`, 320 appels), réassemblage, puis gel `relu-llm` (hors story 15.5).
