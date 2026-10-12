# Epic 7 Context: Jeu d'évaluation maison complet v1.0-provisoire (piste à part)

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Construire le Jeu d'évaluation maison complet (225 items, 8 Tâches) à partir de sources officielles réellement consultées, le faire relire par un vérificateur indépendant, puis le geler en `v1.0-provisoire` avec un manifeste SHA-256 et un commit dédié. Ce jeu décide du go/no-go du fine-tuning et du choix du modèle embarqué. Son gel débloque la Baseline et autorise la génération des Données d'entraînement, interdite avant ce commit. La piste est isolée : elle ne modifie pas le paquet `slmsp`.

## Stories

- Story 7.1 : Outil de construction et instantanés des sources réelles
- Story 7.2 : Items Question (60) et Non-régression (30)
- Story 7.3 : Items Recherche de données (40) et cassettes
- Story 7.4 : Items Compte rendu (25) et Langage clair (25)
- Story 7.5 : Items Correction, Résumé et Courrier type (3 × 15)
- Story 7.6 : Double vérification finale, échantillon de revue et gel v1.0-provisoire

## Requirements & Constraints

- **Isolement strict.** Ne modifier aucun fichier de `src/`, `config/` ni `tests/`, sauf `tests/eval_outils/`. Le paquet `slmsp` n'est utilisé qu'en lecture, par trois points d'entrée : `slmsp mcp record`, `slmsp eval gel` et l'import de `slmsp.core.texte` (et, en option, de `slmsp.core.items`).
- **Références jamais écrites de mémoire.** Chaque fait, montant, URL ou valeur de données vient d'une source officielle consultée, avec sa date (`provenance[].consulte_le`). Claude peut rédiger les items, car ils n'entrent jamais dans l'entraînement. Les contenus fictifs (réunions, textes à fautes, demandes de courrier) portent `fictif: true`.
- **Composition cible** (facile / moyen / difficile) :
  - Q : 60 (20/25/15), dont 8 `sans_reponse` avec `orientation_attendue`, et au moins 50 % issus d'amorces réelles des corpus AgentPublic (`sp_questions_corpus`, `assistant_ia_questions_corpus`).
  - RD : 40 (15/15/10), dont 5 demandes de valeurs et 4 cas de repli, et au moins 6 producteurs de données.
  - CR : 25 (8/10/7), dont 5 transcriptions de plus de 4 000 mots.
  - LC : 25 (8/10/7).
  - CO, RE et CT : 15 chacun (5/5/5).
  - NR : 30 (10/10/10), pour moitié culture générale et raisonnement, pour moitié consignes de rédaction courtes.
- **Thèmes** (Q, RD, LC, RE) : social et autonomie 30 % ; état civil 15 % ; travail et emploi 15 % ; collectivités 15 % ; famille, éducation et santé 15 % ; fiscalité locale 10 %.
- **Codes d'identifiants** : Q, RD, CR, LC, CO, RE, CT, NR. Utiliser RD- et RE-, jamais R- ni RS-. Numérotation à partir de 001.
- **Double vérification.** Un second sous-agent indépendant relit chaque item contre ses sources. Il rejette un item pour l'un de ces motifs : fait absent de la source, URL morte ou différente, item ambigu, doublon thématique trop proche. Les rejets et leurs motifs sont écrits dans `eval/construction/v1.0/verification/<CODE>.jsonl`. Les items rejetés sont remplacés jusqu'aux volumes cibles, et le taux de rejet est consigné.
- **Échantillon de relecture** : 20 % stratifié, avec au moins un item par Tâche × difficulté, écrit dans `eval/revue/echantillon-revue-v1.0.md`.
- **Gel borné dans le temps.** Si les volumes ne sont pas atteints à l'heure prévue du gel (vague V9), geler quand même. Les écarts de composition sont inscrits dans le manifeste et le journal, et ajoutés aux « points à trancher par Anaël ».
- **Réseau** : seuls les hôtes autorisés pour la nuit sont acceptés (Hugging Face, `mcp.data.gouv.fr`, `www.data.gouv.fr`, hôtes de la Liste blanche, dont `www.service-public.gouv.fr`). Légifrance refuse la lecture automatique (HTTP 403) : passer par LEGI MediaTech. Lire directement les parquet HF, avec des reprises (le datasets-server est instable).
- Aucune publication, aucun push, aucune suppression de données téléchargées.

## Technical Decisions

- **Outil dédié** `eval/outils/construire_jeu.py`, hors paquet, lancé par `uv run --no-project --python 3.12 --with <deps> python -I eval/outils/construire_jeu.py`. Il est exclu de la règle TID251, comme `build_calibrage.py`, et porte sa propre liste codée d'hôtes autorisés, vérifiée avant chaque requête. Sous-commandes : `sources`, `fiche <id>`, `assembler --version v1.0`, `composition` et `rejets` (ces deux dernières sortent du Markdown). La logique de téléchargement est reprise de `eval/calibrage/build_calibrage.py`.
- **Flux des fichiers.** Les brouillons sont écrits dans `eval/construction/v1.0/<CODE>.jsonl`. `assembler` les concatène dans `eval/jeu/v1.0/items.jsonl` (UTF-8, LF, tri par identifiant ; un identifiant dupliqué fait échouer l'assemblage). Les instantanés des sources vont sous `data/raw/eval-sources/`, non versionné, chaque fichier étant listé avec son URL et sa date.
- **Lecteur unique et manifeste.** L'outil ne réimplémente ni la validation stricte ni le manifeste. `slmsp eval gel --version v1.0 --verifier-seulement` valide l'assemblage. `slmsp eval gel --version v1.0 --statut provisoire --graine <n>` est le seul producteur de `MANIFEST.json`. Le manifeste contient les SHA des items, des cassettes et de la grille, le statut, la date, l'échantillon du second juge (au moins 3 items par Tâche) et l'échantillon de relecture.
- **Schéma des items** (JSONL). Champs communs : `id`, `tache`, `difficulte`, `theme`, `entree`, `parametres`, `provenance`, `licence_source`, `fictif`, `version_item = 1`. `entree` est du texte pour Q, RD et NR, et un objet à clés nommées pour CR, LC, CO, RE et CT. Champs propres à chaque Tâche :
  - Q : `reponse_reference`, 3 à 5 `elements_cles`, `sources_attendues` sur `www.service-public.gouv.fr`.
  - RD : `appels_attendus` limités aux 5 outils figés, avec `regles` lisibles par machine (par argument : `exact`, `contient_un_de`, `optionnel` ; par appel : `optionnel`, `ordre_libre`) ; `mode` ∈ {`connecte`, `hors-ligne`, `repli`} ; `cassettes` ; `valeurs_attendues` pour les demandes de valeurs.
  - CR : `participants_reference`, `decisions_reference`, `actions_reference` (avec responsable et échéance), `pieges`.
  - LC : `informations_a_conserver`, `termes_juridiques_a_conserver`, `kandel_moles_entree` calculé par `slmsp.core.texte`, avec sa version inscrite dans l'item.
  - CO : `fautes[]` (`debut`, `fin`, `erreur`, `correction`, `type`), avec `entree.texte[debut:fin] == erreur`, et `texte_corrige_reference`.
  - RE : `points_cles_reference`, `longueur_demandee` ∈ {`courte`, `moyenne`, `detaillee`}.
  - CT : `type_courrier` (quatre types), `elements_obligatoires`, `champs_a_laisser_en_emplacement`, `valeurs_interdites`.
  - NR : `reponse_reference` ou `criteres`.
- **Cassettes RD.** Elles sont écrites uniquement par `slmsp mcp record --item RD-xxx --appels …`, sous `eval/cassettes/RD-xxx/<session>.json`. Les cas de repli passent par `--simulation <type>`. Dans l'item, `cassettes` liste des chemins relatifs au dossier du jeu : `../../cassettes/RD-xxx/<session>.json`. `reponse_reference` et `valeurs_attendues` sont tirées des réponses enregistrées. L'enregistrement est refusé pour un item déjà présent dans un manifeste gelé.
- **Calibrage non repris.** Les 16 items de `eval/calibrage/` restent des fixtures de développement et la référence de format. Ils n'entrent pas dans v1.0, mais l'anti-fuite les couvre aussi.
- **Commit de gel** : `eval: gel du jeu d'évaluation v1.0-provisoire`, avec la ligne d'attribution. Il ne contient que `eval/jeu/v1.0/`, `eval/cassettes/`, `eval/revue/` et `eval/construction/v1.0/`. Le taux de rejet par Tâche est consigné dans le journal et dans `etat-nuit.md`.
- **Tests** : `tests/eval_outils/` importe l'outil par son chemin, utilise des brouillons synthétiques dans `tmp_path`, sans aucun réseau.

## Cross-Story Dependencies

- 7.1 (outil) précède toutes les autres stories de l'epic.
- 7.3 dépend de la story 3.3 (`slmsp mcp record`, Bac à sable MCP).
- 7.4 dépend de la story 5.2 (`slmsp.core.texte`, Kandel-Moles avec syllabation).
- 7.2 à 7.5 utilisent `slmsp eval gel --verifier-seulement` si la story 5.1 est faite ; sinon, elles se limitent au contrôle de structure de l'outil.
- 7.6 dépend de 7.2 à 7.5 et de la story 5.1 (`slmsp eval gel`).
- En aval, le commit de gel conditionne la Baseline (epic 8) et la génération de données (epic 9) : celle-ci vérifie le manifeste, l'absence de modification et l'ascendance du commit de gel.
