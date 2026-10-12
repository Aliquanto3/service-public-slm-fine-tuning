---
title: Revue adversariale du spine d'architecture slmsp
cible: ARCHITECTURE-SPINE.md (2026-10-12, status draft)
contexte: decisions.md (D1), eval/SPEC-jeu-evaluation.md, eval/grille-juge-v1.md, eval/calibrage/
lentille: deux stories, deux agents qui ne se parlent pas, chacun respecte chaque AD à la lettre ; où divergent-ils ? Voies de contournement de D1.1 et D1.6.
date: 2026-10-12
---

# Revue adversariale du spine `slmsp`

## Verdict

Le spine est solide sur les dépendances entre paquets (AD-1, AD-2) et sur l'isolement des SDK. Il est faible sur ce qui circule **entre** les paquets : les fichiers, les journaux et les bases SQLite partagées. Les verrous D1.1 contrôlent les *imports*, pas les *lectures de fichiers* ni le *contenu des entrées* envoyées à Mistral. Une sortie de Claude peut donc atteindre les Données d'entraînement sans enfreindre un seul AD à la lettre. Le budget D1.6 a aussi au moins six voies de dépassement que AD-5 ne ferme pas. Il faut un AD nouveau sur les entrées autorisées des pipelines, un AD-3.2 resserré (provenance de la requête, pas seulement de la réponse) et un AD-5 resserré, avant toute story J2.

Sévérités : **CRITIQUE** (viole D1 sans enfreindre d'AD), **ÉLEVÉ** (deux stories incompatibles, ou un rapport ou score faux en silence), **MOYEN** (retravail probable), **FAIBLE** (nommage, ambiguïté locale).

---

## Partie A — Voies de contournement de D1.1 (Claude dans les Données d'entraînement)

### A1. Blanchiment par Mistral : la provenance prouve la réponse, pas la requête — CRITIQUE

**Les deux stories.**
- *Story « Générateur Mistral »* (agent 1) implémente `slmsp.mistral.Generateur`. Elle respecte AD-3.3 : uniquement des rôles `system` et `user`, sans marqueur « Exemple de réponse » dans le gabarit. Chaque appel est journalisé avec `appel_id`, modèle résolu et SHA-256 de la réponse.
- *Story « Génération Comptes rendus »* (agent 2) a besoin de scénarios de réunions fictives (addendum §G : « transcriptions générées par Mistral, réunions fictives »). Aucune source publique ne fournit ces scénarios. L'agent 2 (Claude Code) en écrit 80 dans `config/prompts/generateur/scenarios-cr.toml` (« Conseil départemental, révision du plan APA, 6 participants, décision de… ») et les injecte comme valeurs des emplacements du gabarit. Ou bien, pour les paires en langage clair, il réutilise comme « texte administratif à simplifier » des `entree` du jeu d'évaluation, qui sont rédigées par Claude (SPEC §1.4).

**Pourquoi c'est conforme à la lettre.** AD-3.2 vérifie que la *réponse* a traversé `slmsp.mistral`. AD-3.3 vérifie les *rôles* et une liste noire de marqueurs dans le *gabarit*, pas l'origine des *valeurs* des emplacements. AD-17 rattache chaque amorce « à une entrée du Registre », mais rien n'empêche d'inscrire au Registre une source « scenarios-internes ». Résultat : un contenu écrit par Claude, reformulé par Mistral, porte un `appel_id` valide. C'est exactement l'« amorce rédigée par Claude » que le PRD §8 interdit.

**Variante 1 : `appel_id` de second juge.** Le second juge Mistral (AD-12) passe lui aussi par `slmsp.mistral` (seul importeur de `mistralai`). Il est donc journalisé dans le même `var/appels-mistral.sqlite`, avec le même modèle `mistral-large-latest`. Un exemple qui pointe vers un `appel_id` de jugement passe le contrôle d'AD-3.2. Or ce prompt contenait un item du Jeu d'évaluation, ses références (écrites par Claude) et la sortie du SLM.

**Variante 2 : liste noire de marqueurs.** Le test d'AD-3.3 refuse « Exemple de réponse », « Réponse attendue » et `assistant:`. Il laisse passer « Voici le format à suivre : », « Par exemple : » ou un squelette JSON complet. Un gabarit écrit par Claude peut contenir une sortie modèle sans aucun marqueur interdit.

**Correctif (AD-3.2 resserré, AD-3.3 resserré).**
- Le journal Mistral enregistre la **requête complète**, pas seulement la réponse : SHA du gabarit et sa version, liste des `amorce_id`, réponse brute intégrale et un champ `usage` ∈ {`generation`, `juge-second`, `validation`}. `build` n'accepte que `usage = generation`.
- `Generateur` ne reçoit pas de texte libre. Il reçoit un `gabarit_id` et des `amorce_id`, qu'il résout lui-même dans l'artefact de `seed`.
- Chaque amorce a une `source` inscrite au Registre des licences, qui porte un champ obligatoire `auteur_contenu` ∈ {`public`, `anael`, `mistral`}. `claude` et `inconnu` sont refusés.
- `seed` refuse tout chemin sous `eval/`, `tests/` ou `config/prompts/`.
- Les gabarits passent par une **liste blanche structurelle** (front-matter, sections « Consigne » et « Emplacements », longueur maximale, aucun bloc de code ni JSON) au lieu d'une liste noire. Leur SHA est validé par Anaël et consigné au Registre, et `build` refuse un gabarit dont le SHA n'est pas validé.
- Les scénarios fictifs de CR sont eux-mêmes générés par Mistral à partir d'amorces publiques (thèmes MediaTech), avec leur propre `appel_id`.

### A2. Les verrous portent sur les imports, pas sur les lectures de fichiers — CRITIQUE

**Les deux stories.**
- *Story « Banc d'évaluation »* écrit `runs/eval/<run_id>/generations.jsonl` et `verdicts.jsonl`. Ce dernier contient les justifications de Claude.
- *Story « ORPO »* (AD-18 : `orpo` est une méthode de `slmsp.train`) doit fabriquer des paires de préférence « dérivées du jeu SFT ». L'agent a besoin de réponses « rejetées ». La source la plus évidente sur disque est `runs/eval/*/generations.jsonl` (sorties de la Baseline), triées par `verdicts.jsonl` : note basse = rejetée. Il lit ces fichiers avec `json.loads`, sans aucun import de `slmsp.judge`.

**Pourquoi c'est conforme à la lettre.** AD-1 impose que les pipelines échangent *par artefacts*, et c'est justement ce que fait cette story. AD-3.1 et le test AST ne voient que les imports. AD-3.4 interdit l'usage des verdicts, mais aucun test ne le vérifie, et la story ORPO peut ne pas l'avoir lu (AD-3 ne lie pas `runs/eval/`). Le même chemin permet de lire `eval/jeu/*/items.jsonl` et d'utiliser `reponse_reference` (écrite par Claude) comme réponse « choisie ». AD-10 n'interdit au pipeline de données que `eval/cassettes/`, pas `eval/jeu/` ni `runs/eval/`.

**Variante : fixture de secours.** D5 prescrit : « après deux tentatives, contourner (stub, mock ou fixture) ». Si `slmsp data build` n'a pas abouti, la story « Environnement d'entraînement » (H-WIN-TRAIN) ou l'essai M1 (D4 : « entraîne sur le jeu disponible ») tourne sur `data/train/v0-smoke/train.jsonl`, écrit à la main par l'agent, donc par Claude. AD-18 dit seulement « version du jeu » : `slmsp.train` ne revérifie rien.

**Variante : exception `source:<jeu>`.** AD-3.2 accepte tout exemple « rejoué de sources publiques inscrites au Registre ». Beaucoup de jeux d'instructions français sur Hugging Face sont distillés de GPT ou de Claude, et le Registre ne vérifie que la licence. Un agent peut aussi inscrire `source:calibrage` au Registre.

**Correctif (nouvel AD-24 « Entrées autorisées des pipelines de données et d'entraînement »).**
- `slmsp.data` ne lit que `data/raw/`, `data/seeds/`, `data/cassettes/`, `var/appels-mistral.sqlite` et le Registre. Le Jeu d'évaluation n'est accessible que par une API anti-fuite de `slmsp.core.items`, qui expose des empreintes et des n-grammes, jamais des textes à copier.
- `slmsp.train` ne lit que `data/train/<version>/` et `models/`.
- Toute ouverture de fichier passe par `slmsp.core.artefacts.lire(chemin, lecteur=...)`, qui applique la liste. Un test unitaire et un test AST interdisent `open`, `Path.read_*` et `json.load` hors de ce module dans `data/` et `train/`.
- `slmsp train run` revérifie au chargement que le `MANIFEST.json` a été produit par un run de `slmsp data build` (`build_run_id` présent dans `runs/data-build/`). Il recontrôle aussi les `appel_id` contre le journal.
- Les paires ORPO sont produites par `slmsp data build --preferences`, sous le même contrôle de provenance. L'exemple « rejeté » vient d'un générateur explicite (`mistral` dégradé par consigne, ou `slm-local:<slug>` journalisé dans un journal local équivalent), jamais de `runs/eval/`.
- Le Registre des licences porte un champ `genere_par` obligatoire. Une source dont la fiche déclare une génération synthétique par un modèle non autorisé ou inconnu est refusée.
- Les fixtures d'entraînement des tests sont générées aléatoirement (tokens aléatoires, lorem) sous `tests/fixtures/`, et `train` refuse tout chemin hors `data/train/`.

### A3. SHA de la réponse contre exemple post-traité : un contrôle intenable ou vidé de sa substance — CRITIQUE (rattaché à A1)

Une réponse Mistral ne *devient* jamais telle quelle un exemple. Il faut au minimum parser le JSON, découper N exemples par appel, insérer les résultats d'outils et le prompt système de la Tâche. L'agent `data` ne peut donc pas comparer le SHA de l'exemple à celui de la réponse. Sous la pression de la nuit, il réduira le contrôle à « l'`appel_id` existe dans le journal ». Dès lors, **n'importe quel texte collé à un `appel_id` valide passe**.

**Correctif (AD-3.2).** Le journal conserve la réponse brute. `build` **re-dérive** chaque exemple avec une fonction pure et versionnée, `slmsp.data.extraction.extraire(reponse_brute, version_extracteur)`, puis compare octet par octet. Les seules transformations postérieures autorisées sont énumérées : injection du prompt système de la Tâche depuis `config/prompts/taches/` (SHA au MANIFEST), et messages `tool` issus de cassettes de `data/cassettes/` de la même session (SHA vérifié).

### A4. Traces multi-tours contre verrou 3 : incompatibles, donc contournées — ÉLEVÉ

- *Story « Client Mistral »* : `Generateur` refuse tout message `assistant` (AD-3.3).
- *Story « Traces de tool calling »* (FR-29, 1 500 à 3 000 traces visées) : une trace réaliste demande une boucle question → `tool_calls` de Mistral → exécution MCP en direct (AD-17) → résultat → réponse finale. Au deuxième tour, il faut renvoyer à Mistral son propre message `assistant` avec `tool_calls`, et `Generateur` le refuse.

Les deux stories sont incompatibles. L'agent 2 a trois issues, toutes mauvaises :
- assouplir le verrou, auquel cas un message `assistant` peut contenir n'importe quoi ;
- générer toute la trace en un seul appel, auquel cas Mistral invente les résultats d'outils et la validation par rejeu devient vide ;
- créer un second client hors `Generateur`.

**Correctif (AD-3.3 resserré).** Un message `assistant` est accepté seulement si son `(content, tool_calls)` canonique a le même SHA qu'une réponse journalisée de la **même** `session_id`. Un message `tool` est accepté seulement s'il correspond à une interaction de cassette enregistrée dans cette session.

### A5. Prompts système des Tâches écrits par Claude dans chaque exemple — MOYEN (déjà signalé, à durcir)

Le spine le signale comme question ouverte (D-nuit-A1-10). Le risque concret : un prompt de Tâche contient un squelette de sortie (« Réponds ainsi : ## Participants… ## Décisions… »), écrit par Claude, présent dans 100 % des exemples. Même si ce texte est hors perte, appliquer à `config/prompts/taches/` la même liste blanche structurelle que pour les gabarits (A1), et faire valider leur SHA par Anaël.

---

## Partie B — Voies de dépassement de D1.6 (budget)

### B1. Ledger par copie de travail — CRITIQUE

`var/budget.sqlite` est un chemin relatif au dépôt, et `var/` est hors git. Deux agents qui travaillent dans deux *worktrees* (pratique courante des agents BMAD et de `isolation: worktree`), ou un clone de secours, ont chacun un registre vide. Chacun dispose donc de 30 € et de 10 €. AD-5 dit « partagé entre processus », pas « unique par machine ». Même défaut pour `var/appels-mistral.sqlite` : un `appel_id` d'un worktree est introuvable dans l'autre, et les exemples sont rejetés, ou bien le contrôle est désactivé « temporairement ».

**Correctif (AD-5).** Le chemin de `var/` vient de `SLMSP_VAR_DIR` (par défaut `%LOCALAPPDATA%\slmsp\var\`, hors dépôt). Le registre porte un `campagne_id` (fixé dans `budgets.toml`) et refuse de démarrer si le fichier est absent alors qu'un marqueur de campagne existe. Aucune commande de remise à zéro.

### B2. Relances des SDK et erreurs sans `usage` — ÉLEVÉ

Le SDK `anthropic` relance par défaut (`max_retries=2`) et `mistralai` a sa propre configuration de relance. Une requête facturée côté serveur mais en délai dépassé côté client est renvoyée sous **une seule** réservation. Ensuite, « la réservation est remplacée par le coût réel (champ `usage`) » : sur une erreur, `usage` n'existe pas. L'agent naturel libère la réservation à 0 €, alors que le serveur a peut-être facturé.

**Correctif.** `max_retries=0` imposé sur tous les clients payants. Les relances se font dans `slmsp.budget`, une réservation par tentative. Une tentative sans `usage` est **comptée au pire cas** et jamais libérée.

### B3. Réservation sous-estimée — ÉLEVÉ

« Tokens d'entrée comptés », mais comptés comment ? Une heuristique locale (caractères ÷ 4) sous-estime sur du français accentué et du JSON.

Autres causes de sous-estimation :
- La prime d'écriture du cache de prompt (préfixe grille, H-JUGE-COUT) n'est pas au tarif d'entrée simple.
- Le tarif est cherché par alias (`mistral-large-latest`) alors que le journal stocke le modèle *résolu*. Faute de correspondance, l'agent prend une valeur par défaut, parfois 0.
- Un repli batch → synchrone garde le tarif batch (−50 %).

Le dépassement est alors l'écart cumulé de tous les appels concurrents.

**Correctif.**
- Comptage par l'endpoint officiel de comptage de tokens, ou majoration fixe de 30 % en config.
- Tarifs indexés par modèle résolu **et** par mode (batch ou synchrone, écriture ou lecture de cache).
- Un tarif inconnu lève une erreur (aucune valeur par défaut).
- Contrôle `dépensé + réservé + marge_securite ≤ plafond`.

### B4. Batch API : réservation intenable ou orpheline — ÉLEVÉ

Réserver le pire cas (`max_tokens` × 170 items × tarif de sortie Opus) pour un lot entier peut dépasser seul le plafond de 10 €. Le banc lève alors `BudgetEpuise` à chaque fois. Deux agents divergeront : l'un réserve le coût *attendu* (dépassement possible), l'autre découpe en petits lots (réservations éparpillées).

Si le processus meurt entre l'envoi et la collecte, un agent « nettoie les réservations périmées » au démarrage, alors que le lot tourne encore et sera facturé.

**Correctif.** Réservation par lot au pire cas, au tarif batch. La taille des lots se calcule pour tenir sous le reste disponible, et l'estimation « attendue » est interdite. Une réservation de lot vit jusqu'à la collecte ou l'annulation confirmée (`batch_id` stocké). Elle n'expire jamais d'elle-même.

### B5. Clés d'API transmises aux outils tiers — MOYEN

python-dotenv charge `ANTHROPIC_API_KEY` et `MISTRAL_API_KEY` dans l'environnement, hérité par les sous-processus `lm_eval` et `bfcl-eval`. `bfcl-eval` sait viser des modèles Claude ou Mistral comme cibles, et lm-eval a des modèles API. Une config `config/benchmarks/*.toml` mal visée dépense hors du registre, et contacte en plus un hôte hors du profil `outillage` (AD-4 ne contrôle que *nos* modules).

**Correctif (AD-22).** Les secrets ne sont lus que par `slmsp.budget` ou les fabriques de clients payants, jamais injectés dans `os.environ`. `slmsp.inference` et `slmsp.benchmarks` lancent leurs sous-processus avec un environnement filtré, sans `*_API_KEY`. Un test le vérifie.

### B6. Poste Mistral partagé sans sous-plafond — MOYEN (famine, pas dépassement)

Les 30 € couvrent la génération **et** le second juge. Selon l'ordre de la nuit, `data generate` peut tout consommer, et le kappa (AD-12) n'est jamais calculé. Inversement, des évaluations multiples peuvent réduire les 600 exemples de D4.

**Correctif.** Sous-postes dans `budgets.toml` (par exemple `mistral.generation = 26`, `mistral.juge = 4`), avec le plafond global toujours vérifié.

---

## Partie C — Paires de stories incompatibles (formes partagées, propriétaires, mutations)

### C1. Le Mode pendant l'évaluation et l'interblocage de la sonde — ÉLEVÉ

- *Story « Modes »* : `GestionnaireDeMode` sonde `GET /health` du **vrai** serveur au démarrage, toutes les 5 min et **avant chaque appel d'outil** (AD-4). En Mode hors ligne détecté, `slmsp.net` refuse toute requête « avant toute connexion ».
- *Story « Banc »* : AD-13 branche `AssistantService` + `BacASable`. Le Harnais complet sonde donc le réseau réel avant chaque appel d'outil rejoué.

Conséquences :
- Les scores RD dépendent de la disponibilité de `mcp.data.gouv.fr` pendant la nuit, ce qui casse la reproductibilité NFR-8.
- Le champ d'item `mode` (connecté, hors ligne, repli) n'a aucun moyen d'être imposé.
- **Interblocage** : en hors ligne *détecté*, la sonde est elle-même une requête sortante, donc refusée. L'Assistant ne repasse jamais en connecté.
- `slmsp.net` (couche 1) « consulte » `slmsp.harness.modes` (couche 2), ce qu'AD-1 interdit. Un agent créera un état global dans `core`, un autre passera un rappel.
- Le réglage « Rester hors ligne » appartient à `app.stockage` (AD-23) : il y a deux propriétaires du Mode forcé.

**Correctif (AD-4 resserré).**
- Un `ModePort` (défini dans `core`) est injecté dans `net` et dans le Harnais. Il a deux implémentations : `ModeSonde` (réel) et `ModeFixe(mode)`, utilisé par le banc à partir de `item.mode`.
- Le banc tourne avec un profil réseau `aucun`.
- La sonde est exemptée du blocage en hors ligne *détecté* seulement (jamais en *forcé*) et journalisée.
- Le Mode forcé est une donnée d'entrée de `GestionnaireDeMode`, fournie par l'appelant : CLI via option, app via `stockage`.

### C2. Le journal des Requêtes sortantes a deux propriétaires — ÉLEVÉ

- AD-4 : `slmsp.net` (couche 1) inscrit chaque requête du profil `assistant`.
- AD-23 : `slmsp.app.stockage` (couche 4) est « le seul propriétaire » du journal (SQLite dans `%LOCALAPPDATA%\AssistantSP\`, 30 jours glissants).

`net` ne peut pas importer `app`. En J1, l'agent `net` crée son propre fichier (`var/requetes.sqlite` ou `log.jsonl`) avec son schéma, et en J4 l'agent `app` en crée un second. Le test FR-38 (« document témoin absent de toute Requête sortante journalisée ») ne lit qu'un des deux.

Plusieurs points restent indéfinis :
- le format des « termes envoyés » (arguments d'outil en JSON canonique ? URL complète pour FR-12 ?) ;
- le propriétaire de la purge à 30 jours ;
- la compatibilité de cette purge avec D1.7. Elle est compatible, mais il faut le dire.

**Correctif.** Un port `JournalRequetes` est défini dans `slmsp.core`, avec un schéma d'entrée figé : `horodatage`, `profil`, `hote`, `methode`, `outil`, `termes` (JSON canonique des arguments), `statut` ∈ {envoyee, echouee, bloquee-liste, bloquee-mode}, `mode`. Il est injecté dans `net`. Implémentation SQLite par défaut dans `core` ou `net`, remplacée par `app.stockage` en J4 sur le **même** schéma. Purge par `app.stockage` seulement.

### C3. Cassettes : trois conventions de chemin et deux propriétaires de l'enregistrement — ÉLEVÉ

- Les items du calibrage portent `"cassette": "cassettes/R-001.json"` (chaîne, un fichier par item, plusieurs interactions).
- La SPEC §3 exige `cassettes` (liste de chemins), et la SPEC §4 `eval/cassettes/RD-xxx/*.json` (plusieurs fichiers).
- AD-10 dit `eval/cassettes/<item>/` (dossier).

L'agent `core.items` validera la SPEC (liste), l'agent `BacASable` chargera par glob de dossier, et l'agent des fixtures lira la chaîne du calibrage.

Par ailleurs :
- La SPEC §4 exige « la version du schéma de l'outil » dans chaque cassette, et le format du calibrage « adopté tel quel » ne l'a pas.
- **Enregistrement** : AD-10 dit « uniquement par `slmsp mcp record` », alors qu'AD-17 dit que `data generate` exécute en direct et enregistre dans `data/cassettes/`. Deux stories, deux propriétaires.
- AD-11 interdit au code de réécrire `eval/`, alors que `mcp record` doit y écrire.
- `data/cassettes/` est plat, sans clé de rangement définie (par `session_id` ? par `appel_id` ?).

**Correctif (AD-10 resserré).**
- Une cassette est un fichier par session (format du calibrage), avec deux champs ajoutés : `tools_list_sha256` et `schema_version`.
- Le champ d'item `cassettes` est une liste de chemins relatifs à `eval/`, et c'est la seule source de vérité. Le calibrage est converti à la lecture.
- Une seule API d'enregistrement, `slmsp.mcp.enregistrer(session, magasin)`, appelée par `mcp record` (magasin `eval`, refusé si l'item est déjà dans un manifeste gelé) et par `data generate` (magasin `data`, chemin `data/cassettes/<session_id>.json`).

### C4. Clé du cache de verdicts : forme de la « sortie » non définie et références oubliées — ÉLEVÉ

AD-12 indexe par (`item_id`, SHA de la sortie, version de grille, modèle, effort).
- *Agent « Banc »* : la « sortie » est le texte final.
- *Agent « Juge »* : il hache le prompt rendu, ou texte + appels d'outils.

Pour RD, deux traces aux appels différents et au texte final identique partagent un verdict. Plus grave : **la clé ignore le contenu de l'item**. Au passage en v1.1 (SPEC §6 : références corrigées, `version_item` incrémentée), le cache renvoie des verdicts jugés contre l'**ancienne** référence. La SPEC demande pourtant de relancer *toutes* les évaluations. Même problème si le gabarit du prompt du Juge change sans changer la version de la grille.

Le format du verdict hésite aussi : la grille utilise `"id"` et `criteres` en dictionnaire. L'agent Mistral (second juge) produira son propre schéma via `response_format`. Le kappa pondéré exige des échelles ordinales communes, et AD-12 ne dit pas qui le calcule (`judge` ou `evaluation.scores`).

**Correctif.**
- `sortie_canonique` = JSON canonique `{texte, appels_outils, sources}`.
- Clé = SHA(`sortie_canonique`) + SHA(item complet) + SHA(section de grille) + SHA(gabarit du prompt Juge) + modèle + effort.
- Un modèle pydantic `Verdict` dans `slmsp.core.verdicts`, généré depuis la grille et commun aux deux juges.
- Le kappa est calculé dans `evaluation.scores`.
- L'échantillon de 20 % = f(graine, `item_id` triés, version du jeu), calculé par `core.items` et identique pour tous les modèles. Préciser s'il s'agit du même tirage pour le second juge et pour la relecture humaine.

### C5. Identité d'un run d'évaluation, relance d'une phase seule, runs partiels — ÉLEVÉ

- AD-13 : « chaque phase peut être relancée seule ».
- AD-21 : chaque exécution écrit un **nouveau** `runs/<type>/<run_id>/` et « une reprise écrit à côté ».

L'agent `evaluation` met donc la notation relancée dans un nouveau dossier qui ne contient pas `generations.jsonl`. L'agent `compare` attend `generations`, `verdicts` et `scores` dans le même dossier, ou prend le dernier dossier par ordre alphabétique.

Sur `BudgetEpuise` (AD-5 : « écrit l'état et rend la main »), `scores.json` couvre 60 % des items, et le Comparatif le traite comme complet. Le schéma de `run.json` n'est fixé qu'en prose (« config résolue, graine… »), sans noms de champs.

**Correctif (AD-21 resserré).**
- Modèle pydantic `RunManifest` dans `core.artefacts`, avec : `schema_version`, `type` (`eval-generation`, `eval-notation`, `bench`, `measure`, `data-<etape>`, `train`, `export`, `compare`), `run_id`, `parents` (liste de `run_id`), `modele_ref`, `jeu_version`, `index_version`, `statut` ∈ {complet, partiel-budget, partiel-erreur, interrompu}, `couverture` (items traités / total).
- `compare` exclut ou marque tout statut ≠ complet. Pour une génération donnée, il retient la notation complète la plus récente (règle déterministe).

### C6. Format d'un exemple d'entraînement contre format d'inférence (RAG, protocole d'outils, prompt système) — ÉLEVÉ (qualité, invalide le Comparatif)

AD-7 fixe les messages, mais pas trois choses :

1. **L'injection des passages retrouvés.** L'agent Harnais met les passages dans le `system`, l'agent `data` les met dans le `user` (ou les omet, puisque Mistral reçoit la fiche source en entier). Le modèle est entraîné sur une forme qu'il ne voit jamais à l'inférence.
2. **Le protocole d'outils par modèle.** Le repli H-TOOLS (« JSON générique contraint par `response_format` ») change le rendu en tokens. `train` utilise `apply_chat_template(tools=...)` natif, le Harnais du même modèle produit du JSON dans `content`.
3. **Le message `system` de l'exemple.** L'agent `data` y laisse le gabarit *générateur* (le `system` envoyé à Mistral) au lieu du prompt de Tâche.

Il manque aussi :
- le champ `tools`, qui doit contenir exactement les schémas simplifiés de `config/outils-mcp.toml`. AD-8 ne lie pas `data`, et `generate` présentera à Mistral les schémas du `tools/list` en direct ;
- les sous-tâches de découpage et de fusion de FR-13 pour les CR longs.

**Correctif (AD-7 resserré).**
- Ligne de `train.jsonl` = `{messages, tools, tache, meta:{generateur, appel_id, session_id, version_gabarit, version_extracteur, source, licence, date}}`.
- `messages[0]` est toujours le prompt de Tâche, injecté par `build`.
- Les passages sont formatés par une fonction unique, `slmsp.harness.contexte.formater_passages`, que `data` importe (couche 3 → 2, autorisé). Les exemples Q sont construits par la même recherche (`VectorStore`, version d'index consignée).
- `tools` est figé par SHA de `outils-mcp.toml`.
- `config/modeles/<slug>.toml` porte `protocole_outils = "natif" | "json-generique"`, lu par le Harnais **et** par `train`.

### C7. Identité d'un modèle fine-tuné et chat template de la Baseline — MOYEN

- L'agent `eval` attend `--modele <slug>` résolu dans `config/modeles/<slug>.toml`.
- L'agent `export` écrit `models/gguf/<run_id>-q4_k_m.gguf` sans slug. Écrire un TOML dans `config/` depuis un pipeline violerait l'esprit d'AD-22 (config humaine).

Par ailleurs, la Baseline utilise des GGUF téléchargés (dont l'officiel Ministral 3B), dont le template embarqué peut différer de celui du tokenizer HF qu'AD-19 impose aux GGUF exportés. La comparaison Baseline contre fine-tuné mélange alors deux templates.

**Correctif.** `ModeleRef` = `base:<slug>` ou `ft:<export_run_id>`. Le second se résout par le `run.json` d'export, qui pointe vers le slug de base pour les paramètres d'exécution. Le SHA du chat template est consigné dans `run.json`. La Baseline force `--chat-template-file` extrait du tokenizer HF si les SHA diffèrent.

### C8. Cycle de vie de llama-server et du GPU — MOYEN

AD-6 limite à deux instances « côté Assistant », mais rien n'est dit côté pipelines. `eval run` (CUDA), `bench` (CUDA), le contrôle anti-fuite de `data` (embedding) et `train` peuvent tourner ensemble sur 8 Go de VRAM. `measure` peut tourner pendant un entraînement et fausser FR-26. Chaque story lance ses propres serveurs, avec ses propres ports et son propre arrêt, et des processus orphelins restent si le parent meurt.

**Correctif.** `slmsp.inference.serveur` tient un registre `var/llama-servers.json`, avec PID et ports, et un nettoyage au démarrage. Un verrou exclusif `var/gpu.lock` est pris par `train`, `eval` (CUDA), `bench` et `export`. `measure` exige un verrou machine (aucun autre `llama-server` ni `train` actif) et le consigne dans `run.json`.

### C9. Artefacts intermédiaires du pipeline de données — MOYEN

AD-17 nomme les étapes `seed`, `generate`, `validate`, `filter` et `build`, mais pas l'emplacement de leurs sorties. AD-21 impose `runs/<type>/<run_id>/`. L'agent `generate` écrit `data/generated/…`, l'agent `validate` cherche `runs/data/…`. Qui attribue `<version>` de `data/train/` ?

Point lié : la validation par rejeu (FR-30) rejoue la trace contre les cassettes enregistrées *pendant* cette même trace. Elle ne peut pas échouer et ne vérifie que la cohérence du stockage.

**Correctif.** `runs/data-<etape>/<run_id>/`, chaque étape prenant `--depuis <run_id>` du parent. `build` attribue `vN` par incrément et refuse un dossier existant. Le rejeu FR-30 doit comparer les *arguments* de la trace aux réponses enregistrées et contrôler que les valeurs citées dans la réponse finale figurent dans les résultats d'outils. Sinon, il faut le déclarer vide.

### C10. Fuite par les amorces communes — MOYEN

Au moins 50 % des items Q viennent de `AgentPublic/sp_questions_corpus` (SPEC §2), dont l'`amorce_usager` est stockée dans l'item. Le `seed` des données puise dans les mêmes corpus. Une amorce identique, reformulée deux fois (par Claude pour l'item, par Mistral pour l'exemple), peut passer sous les seuils Jaccard et cosinus du filtre final.

**Correctif (AD-17).** Exclusion **à l'étape `seed`** de toute amorce dont le texte normalisé ou l'identifiant source correspond à une `amorce_usager` ou une `provenance` du jeu gelé. Pour RD, exclusion des `dataset_id` et `resource_id` présents dans les `appels_attendus` du jeu.

### C11. Le contrôle du gel est trop large ou trop étroit — MOYEN

AD-11 vérifie le gel avec `git ls-files` + `git diff --quiet`. Sans périmètre, `git diff --quiet` échoue dès qu'un `runs/eval/.../run.json` versionné (AD-21) n'est pas commité. C'est le cas en pleine nuit : `data generate` refusera de démarrer, et un agent « corrigera » en retirant la vérification. Inversement, limité au seul `MANIFEST.json`, le contrôle laisse passer des items modifiés.

**Correctif.** `git diff --quiet HEAD -- eval/jeu/<version>/ <cassettes listées> eval/grille-juge-v1.md` plus une revérification des SHA du manifeste. Le commit de gel doit être un ancêtre de HEAD.

### C12. Nommage et fermeture runtime — FAIBLE à MOYEN

- **Commande de gel absente** de la liste CLI (`index`, `ask`, `mcp`, `eval`…) alors qu'AD-11 en suppose une. Deux agents créeront `slmsp eval gel` et un script `eval/jeu/build_jeu.py` sur le modèle de `build_calibrage.py`. Le format de `eval/jeu/<v>/MANIFEST.json` n'est pas fixé. **Correctif :** `slmsp eval gel --version v1.0` et un schéma pydantic `ManifesteJeu`.
- **« Registre » homonyme** : `slmsp.budget.Registre` contre le Registre des licences. **Correctif :** `RegistreBudget` et `RegistreLicences`.
- **Deux sources de vérité du coût** : `var/budget.sqlite` contre `usage` dans `var/appels-mistral.sqlite`, et le rapport de nuit (« dépense par API ») lira l'une ou l'autre. **Correctif :** le registre de budget fait foi, et le journal Mistral référence l'entrée du registre.
- **AD-2 et `index build`** : `slmsp.index` fait partie de la fermeture runtime, mais construire l'index lit le parquet MediaTech (duckdb ou pyarrow, extra `data`). La liste bannie d'AD-2 n'inclut ni `duckdb` ni `pyarrow`, donc un import au niveau module dans `slmsp.index` gonfle l'exécutable ou casse en J4. **Correctif :** séparer `slmsp.index` (lecture) d'un pipeline de couche 3 `slmsp.indexation` (construction), et ajouter `duckdb` et `pyarrow` à la liste bannie du runtime.
- **`run_id`** : préciser le `<slug>` par type (modèle pour `eval`, `bench` et `measure` ; nom du TOML pour `train` ; version pour `data-build`) et l'unicité (suffixe court en cas de collision dans la même seconde).

---

## Synthèse des correctifs d'AD proposés

| # | AD | Sévérité | Correctif en une ligne |
|---|---|---|---|
| A1, A3 | AD-3.2 et AD-3.3 resserrés | CRITIQUE | Journal Mistral = requête (gabarit SHA validé + `amorce_id`) + réponse brute + `usage` ; re-dérivation versionnée ; liste blanche structurelle des gabarits ; `auteur_contenu` au Registre |
| A2 | **AD-24 nouveau** (entrées autorisées) | CRITIQUE | Liste de lecture par pipeline, appliquée et testée ; `train` revérifie la provenance ; ORPO dans `data build` ; `genere_par` au Registre ; fixtures aléatoires |
| A4 | AD-3.3 | ÉLEVÉ | `assistant` et `tool` acceptés seulement s'ils sont chaînés par SHA à la même session (journal, cassettes) |
| B1 à B5 | AD-5, AD-22 | CRITIQUE à MOYEN | `var/` unique par machine ; `max_retries=0` ; erreur sans `usage` = pire cas ; tarif inconnu = refus ; réservation de lot jusqu'à la collecte ; environnement des sous-processus sans clés |
| B6 | AD-5 | MOYEN | Sous-plafonds Mistral génération et juge |
| C1 | AD-4 | ÉLEVÉ | `ModePort` injecté, `ModeFixe` pour le banc, sonde exemptée en hors ligne détecté |
| C2 | AD-4, AD-23 | ÉLEVÉ | Port `JournalRequetes` et schéma d'entrée dans `core` |
| C3 | AD-10, AD-11, AD-17 | ÉLEVÉ | Une convention de cassette (champ d'item = liste), une API d'enregistrement, version du schéma dans la cassette |
| C4 | AD-12 | ÉLEVÉ | `sortie_canonique` + SHA de l'item et du prompt Juge dans la clé ; `Verdict` commun ; propriétaire du kappa |
| C5 | AD-13, AD-21 | ÉLEVÉ | `RunManifest` pydantic avec `parents`, `statut`, `couverture` |
| C6 | AD-7, AD-8 | ÉLEVÉ | Ligne `train.jsonl` figée ; `formater_passages` partagé ; `protocole_outils` par modèle |
| C7 à C12 | AD-6, AD-9, AD-11, AD-17, AD-19, conventions | MOYEN à FAIBLE | `ModeleRef`, verrou GPU, emplacements des étapes de données, exclusion des amorces dès le seed, périmètre du `git diff`, noms |

Aucune modification n'a été faite au spine ni aux autres fichiers. Les correctifs ci-dessus sont à arbitrer par l'architecte, et par Anaël pour ceux qui touchent à D1.1 (A1, A2, A5).
