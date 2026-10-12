# Revue qualité du PRD : Assistant IA local pour le secteur public français (SLM fine-tuné)

- **PRD :** `prd.md` + `addendum.md` (même dossier)
- **Grille :** `.claude/skills/bmad-prd/assets/prd-validation-checklist.md`
- **Date :** 2026-10-11
- **Enjeu retenu :** démonstrateur avec ambition de déploiement réel ; le PRD alimente cette nuit une architecture et des stories réalisées par des agents autonomes. Les ambiguïtés qui feraient caler un agent (ou le pousseraient à trancher seul un choix produit) sont classées critique ou haut.

## Verdict global

Le PRD est solide sur le fond : une thèse claire (local, hors ligne, sourcé, plus un Comparatif chiffré), un glossaire réellement utilisé, des FR numérotées et des contre-indicateurs rares et pertinents. Ce qui menace l'exécution autonome cette nuit tient à trois choses. La promesse de confidentialité (« rien ne quitte le poste ») contredit le Mode connecté. Les métriques de score par Tâche, sur lesquelles reposent SM-1 à SM-4 et le go/no-go, ne sont pas définies. Le MVP est très large et sans ordre de priorité ni arbitrage entre les deux objectifs « d'égale importance ». Plusieurs critères d'acceptation restent non testables en l'état (FR-15, FR-16, FR-17, FR-20), ce qui produira des stories au « done » flou.

## Decision-readiness — adéquat

Les décisions structurantes sont posées comme des décisions : exclusion de Claude et Gemini comme générateurs (§8), Liste blanche de cinq domaines (FR-11), Baseline comme référence à battre (§3), publication jamais automatique (FR-37). Les tensions réelles portent des `[NOTE FOR PM]` au bon endroit (NFR-1 sur la RAM, §9.2 sur les corpus de collectivité). Les questions ouvertes du §11 sont réellement ouvertes.

Ce qui manque : aucune règle de décision quand les deux objectifs entrent en conflit (§1 : « second objectif, d'égale importance »), et aucun scénario « no-go » explicite pour SM-1. Le glossaire laisse entendre que la Baseline peut gagner (« Modèle embarqué… peut être un Modèle de base »), mais le PRD ne dit pas ce qui se passe alors pour FR-35, FR-37 et le calendrier.

### Constats
- **haut** Pas d'arbitrage entre les deux objectifs (§1, §9.1) — « d'égale importance » ne dit pas quoi sacrifier quand le temps ou la VRAM manquent (ex. : 4 méthodes du Comparatif contre 8 Tâches de l'Assistant). Un agent autonome n'a aucun critère pour prioriser. *Correction :* ajouter une règle d'arbitrage explicite (ex. : « en cas de conflit, la chaîne Baseline → évaluation → Assistant installable passe avant le Comparatif complet ») et un ordre de livraison (voir constat Scope).
- **moyen** Chemin « no-go » non décrit (SM-1, glossaire « Modèle embarqué ») — si aucun Modèle fine-tuné ne bat la Baseline, que livre-t-on (Baseline embarquée, Comparatif publié quand même, fiche HF sur quel modèle) ? *Correction :* ajouter sous SM-1 : « Si no-go : la Baseline devient le Modèle embarqué ; le Comparatif est publié avec ce résultat ; FR-37 publie le Comparatif seul. »

## Substance over theater — fort

Peu de remplissage. Les personas en JTBD (§2.1) pilotent des décisions : le DSI justifie FR-21/NFR-6, l'agent non francophone justifie FR-18. Les non-utilisateurs (§2.2) sont utiles. Les NFR sont chiffrées (5 Go, 8 tokens/s, 5 s). La vision est spécifique au produit, elle ne se transposerait pas telle quelle à un autre PRD. Cinq profils en JTBD dépassent légèrement le seuil de quatre, mais chacun sert.

### Constats
- **bas** NFR-9 en partie adjective (§5) — « tolère l'évolution des outils… sans planter » n'est pas borné. *Correction :* préciser le comportement attendu : « un outil inconnu est ignoré ; un outil attendu absent déclenche le repli FR-9 ; le schéma des outils est versionné et comparé au démarrage du Mode connecté ».
- **bas** NFR-7 accessibilité (§5) : « vise la conformité » sans critère vérifiable en v1. *Correction :* lister 2 ou 3 critères testables (navigation complète au clavier, contraste ≥ 4,5:1, libellés ARIA sur les contrôles).

## Cohérence stratégique — adéquat

La thèse est nette : le fine-tuning porte le comportement, le RAG porte le savoir, le MCP porte la fraîcheur (addendum §A). Les métriques valident cette thèse (SM-1 contre la Baseline, SM-2 exactitude sourcée), et les contre-indicateurs SM-C1 à C4 sont bien choisis. Le type de MVP (résolution de problème + démonstration de capacité) est cohérent.

Le point faible est l'étendue : huit Tâches, cinq langues, quatre méthodes, sept familles de benchmarks, un installateur et un pipeline de données, sans séquencement. Le PRD se lit par endroits comme un backlog complet plutôt que comme un MVP.

### Constats
- **haut** MVP sans ordre de livraison (§9.1) — tout est « dans le périmètre » au même niveau. Pour des agents autonomes qui découpent en epics, cela produit un ordre arbitraire. Or la chaîne de dépendances est forte : Jeu d'évaluation figé (FR-24) → Baseline → données → Runs → quantification → embarquement. *Correction :* ajouter un §9.3 « Ordre de livraison » en jalons (ex. : J1 Jeu d'évaluation + banc + Baseline ; J2 Assistant hors ligne Question + Index local + installateur ; J3 Mode connecté + MCP ; J4 Données + Runs + Comparatif ; J5 Tâches de rédaction et Traduction), en marquant ce qui est coupable si le temps manque.
- **moyen** Tâches secondaires non hiérarchisées (§4.5 à §4.7) — seule la Traduction est dite « secondaire ». Courrier type, Résumé et Correction ont été ajoutés (FR-24 : « volume ajouté pour couvrir les nouvelles Tâches ») mais ne figurent dans aucune SM. *Correction :* les marquer « secondaires v1 », ou leur rattacher une SM.

## Clarté du « done » — mince

C'est la dimension la plus faible et celle qui pèse le plus sur les stories. Plusieurs FR ont de bons critères (FR-5 : testé carte réseau désactivée ; FR-10 : capture réseau ; FR-24 : empreinte vérifiée ; FR-29 : arrêt au plafond ; FR-31 : échec si source absente du registre). Mais les métriques qui jugent la qualité sont soit non définies, soit renvoyées au Juge sans grille.

### Constats
- **critique** Métriques de score par Tâche non définies (FR-25, SM-1 à SM-4) — FR-25 produit « un rapport de scores par Tâche » et SM-1 exige « au moins 10 points ». On ne sait pas sur quelle échelle (0–100 ? exactitude ? note Juge 1–5 normalisée ?), ni comment chaque Tâche est notée : exactitude d'une Question, validité d'un appel d'outil, « absence d'invention » d'un compte rendu. La « grille versionnée » du Juge n'existe pas. Un agent devra l'inventer, et le go/no-go reposera sur son invention. *Correction :* ajouter un tableau « Métrique par Tâche » (Tâche → métrique → méthode : automatique ou Juge → échelle 0–100), et faire de la rédaction de la grille du Juge v1 une exigence explicite (FR-25bis) livrée avec FR-24, avant toute Baseline.
- **critique** Reproductibilité de l'évaluation du tool calling contre un serveur vivant (FR-24 « Recherche de données : 40 », FR-30, NFR-8, addendum §B) — le serveur MCP est expérimental et ses données changent. Évaluer ou rejouer des traces contre la production rend les scores non reproductibles, ce qui contredit NFR-8 et FR-36 (« régénérable à l'identique »). Le PRD ne dit pas s'il faut un instantané figé des réponses d'outils ou un serveur auto-hébergé versionné. *Correction :* exiger un « bac à sable MCP » : réponses d'outils enregistrées (cassettes) ou instance auto-hébergée à version figée, utilisées pour l'évaluation et la validation FR-30 ; le serveur réel ne sert qu'aux tests d'intégration.
- **haut** FR-16 « indice de lisibilité » non nommé — plusieurs indices français existent (Kandel-Moles, Scolarius, Flesch adapté), avec des résultats divergents. *Correction :* nommer l'indice et le seuil (ex. : « Kandel-Moles de la sortie ≥ entrée + 10 en moyenne »).
- **haut** FR-15, FR-17 non testables — « aucune information absente du document source » et « ne modifie pas le fond » ne disent pas comment c'est mesuré. *Correction :* rattacher chaque critère à une mesure du Jeu d'évaluation maison (ex. : FR-15 noté par le Juge sur l'axe « fidélité », seuil SM-4 ; FR-17 : similarité sémantique entrée/sortie ≥ seuil, et corrections présentées en diff).
- **haut** FR-13 : critère à double issue — « l'Assistant le dit, ou traite le texte par morceaux ». Un agent choisira la voie la plus simple. Par ailleurs 6 000 mots font environ 8 000 à 9 000 tokens, ce qui contredit le levier « fenêtre de contexte limitée à 4k » de l'addendum §C. *Correction :* trancher : « traitement par morceaux obligatoire au-delà de la fenêtre » (ou l'inverse), et indiquer que la fenêtre minimale est un arbitrage d'architecture sous contrainte FR-13.
- **haut** Règle de détection du mode non définie (FR-10, UJ-1) — l'indicateur affiche « Hors ligne » automatiquement, mais rien ne dit comment le Mode connecté est détecté (sonde `GET /health` du MCP ? connectivité générale ?), à quelle fréquence, ni si le passage en connecté est automatique ou demande une action. *Correction :* ajouter à FR-10 : « Mode connecté si la sonde vers [endpoint de la Liste blanche] répond en moins de N s ; vérification au lancement et toutes les X min ; Mode hors ligne par défaut en cas de doute ».
- **moyen** FR-3 : « réponses de droits et de démarches » — rien ne dit qui classe une réponse dans cette catégorie. *Correction :* appliquer l'avertissement à toute réponse de la Tâche Question (règle simple, testable).
- **moyen** FR-20 : anonymisation vague — « noms propres et identifiants détectés » sans liste. *Correction :* lister les motifs v1 (NIR, e-mail, téléphone, IBAN, noms via NER) et le critère : un export de test contenant ces motifs n'en contient plus aucun.
- **moyen** FR-34 : « à tokens vus égaux et à durée égale » — deux normalisations simultanées, la règle de comparaison n'est pas claire. *Correction :* préciser « deux vues rapportées : (a) à tokens vus égaux, (b) à budget de temps égal ».
- **moyen** FR-8 sans repli défini — FR-9 se replie sur l'Index local, mais l'Index local ne contient pas les valeurs des ressources. Le comportement attendu pour une demande de valeurs hors ligne n'est pas écrit. *Correction :* « hors ligne, l'Assistant indique que les valeurs ne sont disponibles qu'en Mode connecté et donne le lien de la ressource ».
- **bas** FR-22, FR-23 sans critère explicite — acceptables mais un critère d'un ligne aiderait (ex. : « aucun fichier résiduel dans le profil hors choix de conservation »).

## Honnêteté du périmètre — adéquat

Les non-objectifs (§7) et le hors-MVP (§9.2) font un vrai travail. Les hypothèses sont tagguées et indexées. La densité d'éléments ouverts est élevée pour un feu vert de construction : 6 questions ouvertes, 13 hypothèses, 2 notes PM. La plupart se résolvent toutefois par la mesure (Baseline, PC cible), ce qui est acceptable si l'architecture les traite comme des points de décision mesurés.

Le vrai problème d'honnêteté est la promesse de confidentialité.

### Constats
- **critique** Contradiction confidentialité / Mode connecté (§1 « Rien de ce que l'agent saisit ne quitte son poste », NFR-4, UJ-2, FR-7, FR-12) — en UJ-2, la question de Thomas (« places en EHPAD par commune ») est forcément transmise, sous une forme ou une autre, au serveur MCP. NFR-4 dit à la fois « aucune donnée saisie ne quitte le poste » et « seules les requêtes formulées par le Harnais… sont émises ». Le PRD ne précise pas ce qu'une requête formulée a le droit de contenir. Un agent d'architecture devra trancher seul une question de sécurité et de communication DSI. *Correction :* reformuler : « En Mode connecté, seuls des termes de recherche et des identifiants générés par le Harnais sont envoyés aux domaines de la Liste blanche ; jamais le texte collé pour les Tâches de rédaction, ni la conversation brute » ; ajouter un critère testable (journal des requêtes sortantes consultable par l'Agent) et corriger la phrase de la Vision.
- **moyen** Rôle humain dans les boucles de relecture (FR-25 « 20 % exportés pour relecture humaine », FR-30, SM-4) — un pipeline lancé par des agents autonomes ne peut pas attendre une relecture. Il faut dire si elle bloque ou non. *Correction :* « l'export est produit ; les scores sont marqués "non relus" tant qu'Anaël n'a pas validé ; seule la décision SM-1/SM-4 finale exige la relecture ».
- **moyen** Licence Apache 2.0 du Modèle embarqué (FR-37, FR-31) — la licence de publication dépend de la licence du Modèle de base (certains candidats n'autorisent pas une rediffusion sous Apache 2.0). *Correction :* « publié sous la licence compatible la plus permissive ; Apache 2.0 si le Modèle de base le permet », et ajouter la licence comme critère de la shortlist.
- **bas** Budget d'API sans montant (§6.3 « Montant fixé dans le document de décisions ») — le document n'est pas nommé ni lié. *Correction :* donner le chemin du document ou une valeur par défaut dans l'addendum.

## Utilisabilité en aval — adéquat

Le glossaire est présent et appliqué avec rigueur (majuscules sur les termes définis). Les ID sont contigus et uniques : FR-1 à FR-37, NFR-1 à NFR-9, SM-1 à SM-8, SM-C1 à C4, UJ-1 à UJ-6. Chaque UJ a un protagoniste nommé, sauf UJ-5 (« un technicien »), ce qui reste acceptable. Les FR renvoient aux UJ et les SM aux FR.

Principal frein pour les agents : des informations nécessaires sont hors du dossier (shortlist des Modèles de base « dans la note de cadrage », document de décisions). Le format interne de certaines FR est aussi ambigu.

### Constats
- **haut** Shortlist des Modèles de base hors PRD et addendum (§3 « La shortlist est dans la note de cadrage ») — l'addendum cite Granite 4 H, Ministral 3 et SmolLM3 dans les pièges, mais pas la liste elle-même. Un agent qui ne lit que le PRD et l'addendum ne sait pas quels modèles évaluer en Baseline. *Correction :* recopier la shortlist (nom, taille, licence) dans l'addendum §E.
- **moyen** Correspondance Liste blanche / sous-domaines (FR-11, addendum §B) — la Liste blanche dit `data.gouv.fr`, mais le serveur est `mcp.data.gouv.fr`. La règle de correspondance (domaine exact ou sous-domaines) n'est pas définie, et c'est un point de sécurité. *Correction :* « correspondance exacte d'hôte ; la liste v1 contient `mcp.data.gouv.fr`, `www.service-public.fr`, … ».
- **moyen** Comparatif à 4 méthodes et protocole équitable (FR-32, FR-34, SM-6) — « DoRA ou rsLoRA » et « ORPO ou DPO » rendent le compte de 4 ambigu. Une méthode par préférence exige des données de préférence, ce qui contredit « mêmes données » de FR-34. *Correction :* fixer la liste des 4 méthodes comptées pour SM-6 et déclarer la méthode par préférence comme dérogation documentée au protocole (données de préférence dérivées du même jeu SFT).
- **bas** FR-25 vs §8 sur les Juges — FR-25 cite « Claude ou un grand modèle open-weight », §8 autorise aussi Gemini comme Juge. *Correction :* aligner FR-25 sur §8.

## Adéquation de la forme — fort

Le PRD est en tête de chaîne (UX → architecture → stories) et combine un produit à usage métier (UJ utiles, protagonistes nommés) et un outil interne pour un seul opérateur (banc d'évaluation, Comparatif), décrit en spécification de capacités. Les deux formes sont bien employées : UJ pour l'Assistant, FR plus techniques pour §4.10 à §4.14. Le report des noms d'outils et des benchmarks vers l'addendum est juste.

### Constats
- aucun constat bloquant.

## Notes mécaniques

- **Index des hypothèses :** aller-retour complet (13 tags inline, tous indexés). En revanche, SM-3, SM-4 et SM-7 portent un `[ASSUMPTION]` sans contenu : l'index les regroupe sous « seuils à confirmer après la Baseline », mais l'inline ne le dit pas.
- **Hypothèse de l'addendum non indexée :** addendum §F « 200 à 500 exemples chacune » n'est pas reprise dans l'index du PRD (acceptable si l'index ne couvre que le PRD, mais à signaler).
- **FR-27 :** la liste de couverture et les critères d'acceptation sont dans la même liste à puces (« les biais. » puis « Le socle complet s'exécute… »), ce qui brouille l'extraction. Séparer les deux listes.
- **FR-29 / FR-30 :** même mélange entre description et critères dans les listes à puces.
- **Terminologie :** « LoRA 16 bits sur le plus petit modèle » (FR-32) contre « LoRA bf16 sur le 1B » (addendum §E) ; harmoniser.
- **« Harnais » :** le terme désigne à la fois la logique applicative (glossaire) et le « harnais d'évaluation standard » (glossaire « Benchmark standardisé »). Renommer le second en « outil d'évaluation » (lm-evaluation-harness) pour éviter la confusion dans les stories.
- **NFR-5 :** cite FR-8 comme « interrogation fraîche de data.gouv » alors que FR-7 (recherche via MCP) dépend aussi du réseau dans sa forme fraîche. À compléter.
- **UJ-5 :** protagoniste non nommé (« un technicien ») ; mineur.
- **Titre :** « Nom de travail, à confirmer » ; sans impact en aval.
