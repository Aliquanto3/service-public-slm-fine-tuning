# Epic 5 Context: Banc d'évaluation reproductible

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Cet epic livre la commande unique `slmsp eval run`, qui évalue un modèle (base ou fine-tuné, F16 ou Q4_K_M) sur le Jeu d'évaluation maison. Elle tourne en deux phases sans réseau : la génération par le Harnais complet contre le Bac à sable MCP, puis la notation par contrôles automatiques, Juge Claude, second juge Mistral sur un échantillon et formules de la grille. Elle produit des Scores de Tâche reproductibles et marqués de leurs statuts, plus un export de relecture. L'epic pose aussi le lecteur unique d'items, le gel du jeu par manifeste SHA-256 et l'API anti-fuite. Ce sont les préalables de la Baseline, du go/no-go et de toute génération de Données d'entraînement.

## Stories

- Story 5.1 : Lecteur unique d'items, API anti-fuite et gel du Jeu d'évaluation
- Story 5.2 : Fonctions de texte partagées (normalisation, mots, nombres, Kandel-Moles)
- Story 5.3 : Évaluation, phase génération, sans réseau
- Story 5.4 : Juge principal Claude : prompt, Batch API et cache de verdicts
- Story 5.5 : Adaptateur Mistral et second juge sur l'échantillon de 20 %
- Story 5.6 : Évaluation, phase notation : contrôles automatiques, Scores de Tâche, kappa et relecture

## Requirements & Constraints

- **Jeu intact** : toute évaluation revérifie les SHA du manifeste et refuse de tourner en cas d'écart (`ManifesteInvalide`, code 4). Aucune Donnée d'entraînement n'est générée avant un gel commité, ancêtre de `HEAD`. Une version gelée n'est jamais modifiée. Seuls `eval gel` (nouvelle version) et `mcp record` (nouveaux fichiers) écrivent sous `eval/`. Aucun fichier de `eval/calibrage/` n'est modifié.
- **Anti-fuite** : aucun item, quasi-doublon ou paraphrase ne doit atteindre l'entraînement. Le pipeline `data` ne voit le jeu (v1.0 et calibrage) que par des empreintes de n-grammes hachés, des vecteurs et des identifiants protégés, jamais par du texte d'item.
- **Composition cible** (contrôlée au gel, écarts inscrits au manifeste si le gel est provisoire) : 225 items. Q 60 (dont 8 sans réponse), RD 40 (5 demandes de valeurs, 4 replis, au moins 6 producteurs), CR 25 (5 de plus de 4 000 mots), LC 25, CO 15, RE 15, CT 15, NR 30, chacun réparti par difficulté. Codes faisant foi : Q, RD, CR, LC, CO, RE, CT, NR (le calibrage utilise encore R et RS).
- **Échantillons tirés une seule fois au gel, avec une graine, identiques pour tous les modèles** : second juge (au moins 3 items par Tâche jugée) et relecture (20 % stratifié Tâche × difficulté, au moins 1 par strate).
- **Reproductibilité** : à `FakeLlm` constant, les `sortie_canonique` sont identiques à l'octet près. Relancer la notation avec un cache rempli ne fait aucun appel payant et produit un `scores.json` identique à l'octet près.
- **Sans réseau** : aucune requête ne sort pendant une évaluation (profil `aucun`), et un test le vérifie.
- **Budget** : Juge Claude dans le poste `anthropic` (10 €), second juge dans `mistral.juge` (5 €). Sur `BudgetEpuise`, les items restants sont marqués « non jugés » ou « non rejugés », le run passe en `partiel-budget`, et le kappa est calculé sur l'effectif disponible. Aucun test n'appelle une API payante. Les tokens et le coût par item sont journalisés (la mesure H-JUGE-COUT se fait plus tard, à la Baseline).
- **Relecture humaine** : tous les scores restent « non relus » tant qu'un `relecture-validee.json` daté n'existe pas.

## Technical Decisions

- **Lecteur unique `core.items`** : c'est la seule voie de lecture et de rendu (`vers_requete(item)`). Il adapte le calibrage à la lecture : `R`→`RD`, `RS`→`RE`, `cassette`→`cassettes` (liste), `comportement_attendu="absence_de_source"`→`sans_reponse=true`, `entree.longueur_demandee` et `entree.type` remontés, défauts `mode="connecte"`, `version_item=0`, `theme="non-classe"`, `fictif` déduit de la provenance. Le mode strict (v1.0) exige `theme`, `parametres`, `fictif`, `version_item` et, pour RD, les `appels_attendus[].regles` lisibles par machine (`exact`, `contient_un_de`, `optionnel` par argument ; `optionnel`, `ordre_libre` par appel). `entree` est un texte pour Q, RD et NR, un objet pour CR, LC, CO, RE et CT, et les fautes CO sont repérées par `debut`/`fin`. Les chemins de cassettes sont relatifs au dossier du jeu (`../../cassettes/RD-xxx/<session>.json`).
- **Manifeste `ManifesteJeu`** (`eval/jeu/<v>/MANIFEST.json`, écrit par `eval gel` seulement, refus s'il existe) : SHA de `items.jsonl`, des cassettes et de la grille, `statut` (`provisoire`/`relu`), date, écarts de composition et les deux échantillons. `jeu_gele_et_commite` vérifie les SHA, `git diff --quiet HEAD --` sur les seuls chemins du manifeste et l'ascendance du commit de gel. Le `tools_list_sha256` des cassettes doit correspondre à `config/outils-mcp.toml`.
- **Phase génération** (run `eval-generation`) : Harnais complet avec `BacASable` par item, `ModeFixe(item.mode)`, profil réseau `aucun`, décodage glouton, graine fixe, `llama-server --parallel 1`. Le modèle est désigné par un `ModeleRef` : `base:<slug>` ou `ft:<export_run_id>`, avec `quantification` ∈ {`f16`, `q4_k_m`}. `run.json` porte `modele_ref`, `quantification`, `variante_llamacpp`, `jeu_version`, `index_version` et le SHA du chat template. Si le template du GGUF diffère de celui du tokenizer HF, `--chat-template-file` impose celui du tokenizer. La variante `cuda` prend le verrou `gpu.lock`. `generations.jsonl` contient une ligne `Generation` par item (`item_id`, `sortie_canonique` = `{texte, appels_outils, sources}`, trace d'évènements), sans les durées dans `sortie_canonique`. Un item en erreur reçoit un évènement `Erreur` et le run continue (`complet` ou `partiel-erreur`).
- **Phase notation** (run `eval-notation`, parent = génération) : écrit `verdicts.jsonl`, `scores.json` et `relecture.md`. Le Juge ne calcule jamais de score : les formules vivent uniquement dans `evaluation.scores`.
- **Juge principal** : `claude-opus-5-5`, sans `temperature` ni `top_p` (le modèle les refuse : écart assumé à la température 0 de la SPEC), effort et `mode_appel="batch"` lus dans `juges.toml`, `max_retries=0`, `http_client` du profil `outillage`, sortie structurée. Le Juge est aveugle : ni modèle évalué ni méthode, et pas de comparaison par paires en v1. Il reçoit l'entrée rendue, le texte final, les sources citées (URL, titre), les références de l'item et la section de grille de la Tâche, dans le gabarit « Prompt du Juge » de la grille. En batch : réservation au pire cas au tarif batch avant l'envoi, `batch_id` persisté avant toute attente, et relecture des lots en cours avant d'en créer un nouveau. Au-delà de `delai_max_lot`, le lot est annulé (annulation confirmée) et les items restants passent en appels directs. Deux sorties non conformes au schéma rendent le verdict `invalide` : l'item est exclu du score et compté à part.
- **Schéma `Verdict`** commun aux deux juges (`id`, `criteres` avec note et justification, `inventions`, `confiance`, `invalide`), fermé par Tâche :
  - Q : `exactitude` {0,1,2}, `pertinence_source` {0,1}, `cas_sans_reponse` {0,1} si `sans_reponse` ;
  - CR : `presence_elements[{ref, present ∈ {0,0.5,1}}]`, `absence_invention`, `structure` ;
  - LC : `fidelite` {0,1,2}, `termes_juridiques`, `clarte_percue` {1..5} ;
  - RE : `fidelite`, `presence_elements` {0,1} ;
  - CT : `conformite` {0,1,2} ;
  - NR : `exactitude` {0,1} ;
  - RD (litige seulement) : `libelle_correct`.
- **Cache de verdicts** (`SLMSP_VAR_DIR/verdicts.sqlite`) : la clé combine le SHA de l'item canonique, de la `sortie_canonique`, de la section de grille, du gabarit et du schéma, plus le modèle et l'effort. Un verdict n'est jamais redemandé ni réservé deux fois.
- **Mistral** : `slmsp.mistral` est le seul importeur de `mistralai`, et `slmsp.judge` le seul importeur d'`anthropic`. Les clients sont injectés par `net`, sans relance automatique. Le modèle résolu est vérifié contre une liste stable (Labs et préversions refusés). Le journal `appels-mistral.sqlite` enregistre `appel_id`, `session_id`, `usage` ∈ {`generation`, `juge-second`, `validation`}, le modèle résolu, la requête complète, la réponse brute, son SHA, la référence budget et l'horodatage. L'appel générique refuse `usage="generation"`, réservé au futur `Generateur` (story 9.2) par un jeton de preuve. Le second juge reprend le même prompt et le même schéma, avec `temperature=0` et `response_format` JSON.
- **Scores (une seule implémentation)** :
  - Q : % d'items réussis (exactitude 2, pertinence 1, aucune URL inventée via `harness.citations` ; pour un item sans réponse, `cas_sans_reponse`=1).
  - RD : moyenne de l'« appel valide » (micro-moyenne contre `regles`, items sans appel attendu exclus du dénominateur) et de la « réponse exacte » (identifiants de jeux, valeurs numériques).
  - CR : moyenne du rappel ×100 (action sans responsable ou échéance comptée pour moitié) et du % sans invention.
  - LC : % avec fidélité 2 et termes 1, plafonné à 50 et marqué `plafonne_lc` si le gain moyen de Kandel-Moles < +10.
  - CO : rappel × (1 − taux hors faute), tolérances en config.
  - RE : moyenne du % fidèles et du rappel ×100 (longueurs 80/200/400 mots rapportées seulement).
  - CT : moyenne de conformité ÷2 ×100 et du % d'emplacements réussis (libellé exact entre crochets, absence des `valeurs_interdites`).
  - NR : % exacts.
  - Kappa : quadratique pour les critères ordinaux, simple pour les binaires, aucun sur les rappels ; CO et RD sont exclus ; une Tâche est marquée `fragile` sous 0,6.
  - Chaque Tâche porte score, composantes, effectifs (notés, jugés, invalides, non jugés), statuts (`jeu_statut`, `verdicts_relus`, `fragile`, `plafonne_lc`), kappa, coût du Juge et SHA du manifeste.
- **`core.texte`** : versionné (`VERSION_TEXTE`, à incrémenter à tout changement de règle). Il fournit la normalisation (NFKC, minuscules, sans ponctuation, espaces uniques, idempotente), le comptage de mots, le découpage en phrases, l'extraction de nombres à la française (espace insécable, virgule décimale, €, %), les n-grammes et Kandel-Moles (207 − 1,015 × mots/phrase − 73,6 × syllabes/mot, syllabation par groupes vocaliques avec e muet final). Ces fonctions servent au banc, à l'anti-fuite et à la construction du jeu.
- **Configs** : `config/juges.toml` (sections `principal` et `second`), `config/mistral.toml` (`mistral-large-latest`, liste stable), `config/evaluation.toml` (tolérances, longueurs, seuils). La CLI `slmsp eval` porte les options `gel [--verifier-seulement | --statut --graine]` et `run --modele --quantification --jeu [--variante] [--phase generation|notation|toutes] [--items] [--reprendre <run_id>] [--depuis <run_id>]`. `--reprendre` complète le même dossier en ajout seul.

## Cross-Story Dependencies

- Ordre interne : 5.1 → 5.3 et 5.4 ; 5.4 → 5.5 ; 5.2, 5.3 et 5.5 → 5.6. La story 5.2 est pure et ne dépend que de 1.1 : elle peut démarrer très tôt, et l'Epic 7 l'utilise.
- Dépendances externes : 5.1 dépend de 1.3 (runs, lecteur contrôlé) et de 3.1 (outils MCP, cassettes, `BacASable`). 5.3 dépend de 4.3, 4.4 (Harnais, `ModeFixe`, `harness.citations`) et 2.2 (inférence `llama-server`). 5.4 dépend de 1.4 (passerelle `net`) et de 1.5 (`RegistreBudget`).
- `cli/eval.py` est modifié par 5.1, 5.3, 5.6, puis 8.2, toujours en séquence, jamais en parallèle. Avant 5.3, la sous-commande `run` répond « non implémentée », et `sonde-outils` aussi jusqu'à 8.2.
- En aval : l'Epic 7 gèle le jeu v1.0 complet avec `eval gel`. La Baseline (8.3) exige le jeu gelé et commité (seul un essai de fumée sur le calibrage est permis avant, étiqueté `jeu_version = calibrage`), et mesure H-JUGE-COUT et H-BATCH. `data generate` (Epic 9) appelle `jeu_gele_et_commite("v1.0")` et l'API anti-fuite. `Generateur` (9.2) réutilise l'adaptateur et le journal Mistral. Le Comparatif (8.4, 11.1) charge `Scores`.
- Tests : calibrage réel en lecture seule (16 items) derrière un manifeste factice dans `tmp_path`, dépôt git de fixture pour le gel, `FakeLlm`, transports factices injectés par `net` pour Anthropic et Mistral, aucun appel d'API.
