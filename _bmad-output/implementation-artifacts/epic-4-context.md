# Epic 4 Context: Harnais en ligne de commande

<!-- Generated from planning artifacts. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Livrer le Harnais de l'Assistant (`AssistantService`) et la commande `slmsp ask`. Anaël peut alors poser une Question fondée sur l'Index local, chercher des données data.gouv ou faire rédiger un texte (compte rendu, langage clair, correction, résumé, courrier type, traduction) depuis la ligne de commande. Les réponses citent leurs sources, respectent le Mode (connecté ou hors ligne), basculent sur l'Index local quand data.gouv échoue, et le journal des Requêtes sortantes prouve qu'aucun texte collé ne quitte le poste. Ce service est la pièce centrale du projet : le banc d'évaluation (Epic 5), les mesures (Epic 6), le pipeline de données (Epic 9, pour la construction des prompts), l'entraînement (Epic 10, rendu et masque) et l'application J4 le réutilisent tel quel. Tout écart de forme d'entrée entre ces usages fausserait l'entraînement et l'évaluation.

## Stories

- Story 4.1 : Table des Tâches, prompts de Tâche et construction unique des messages
- Story 4.2 : `AssistantService` : flux d'évènements, Question fondée sur l'Index local, Tâches de rédaction
- Story 4.3 : Recherche de données : boucle d'outils, Modes et repli
- Story 4.4 : Comptes rendus longs : découpage et fusion
- Story 4.5 : Commande `slmsp ask` et test du document témoin

## Requirements & Constraints

**Règle D1.1 (bloquante, sans exception) : les prompts système de Tâche sont des instructions sans aucun exemple.**
- `config/prompts/taches/*.md` ne contient que des consignes rédigées par le projet : aucun exemple de sortie, aucune réponse type, aucun few-shot, aucune amorce. Ces prompts entrent tels quels dans les Données d'entraînement (comme entrée, hors perte), donc un exemple glissé dedans serait une Donnée d'entraînement produite par Claude, ce qui est interdit.
- Format imposé, vérifié par la liste blanche structurelle de `core.gabarits` : front-matter (`id`, `version`, `tache`), sections « Consigne » et « Emplacements » seulement, longueur maximale, aucun bloc de code, aucun JSON, aucune section ni ligne « Exemple ». Le validateur renvoie le SHA-256 du fichier.
- Les tests et fixtures ne contiennent aucun texte rédigé qui ressemble à un exemple : les sorties de `FakeLlm` et les textes de test sont des chaînes ou mots aléatoires générés dans le test.
- L'usage de ces prompts comme entrée d'entraînement reste à valider par Anaël. S'il le refuse, il les réécrit lui-même.

**Comportement attendu :**
- Service sans état : l'appelant fournit et conserve toute la conversation. « Nouvelle conversation » revient à vider la liste côté appelant.
- Tâche choisie explicitement, Question par défaut. Chaque Tâche applique son prompt système et son format.
- Question : réponse fondée sur les passages de l'Index local au-dessus du seuil de pertinence, sources numérotées (titre, URL, date du snapshot, extrait), puis avertissement « Ne vaut pas avis juridique. ». Sans passage pertinent, la réponse le dit et oriente l'Agent, sans erreur. Une URL absente des passages et des résultats d'outils est signalée dans `Fin.urls_inventees`, sans réécrire le texte.
- Tâches de rédaction (CR, LC, CO, RE, CT, NR, TR) : aucun outil passé au modèle, aucun appel à `ToolPort` ni à `NetGate`, pas d'avertissement juridique. Un texte collé ne déclenche jamais de Requête sortante (test du document témoin).
- Recherche de données : seuls des appels d'outils conformes au schéma sont envoyés. Les jeux de données cités proviennent d'un résultat d'outil ou de l'Index. Les valeurs de tableau sont rendues depuis `ResultatOutil`, jamais depuis le texte généré. Hors ligne, on renvoie au Mode connecté avec le lien de la ressource. Si un appel MCP échoue ou dépasse le délai (10 s par défaut), on bascule sur l'Index local avec un message « non vérifié en ligne ».
- Modes : sonde `GET /health` en moins de 3 s, au démarrage, toutes les 5 min et avant chaque appel d'outil. Si la sonde échoue ou laisse un doute, le Mode reste hors ligne. En hors ligne forcé, aucune requête n'est émise, sonde comprise.
- Comptes rendus : une entrée de 6 000 mots ou plus est acceptée sans troncature silencieuse. Au-delà du contexte, elle est traitée par morceaux puis fusionnée.
- Le journal des Requêtes sortantes ne contient que les arguments d'outil (`termes`), jamais la phrase de l'Agent.
- Hors ligne, toutes les Tâches fonctionnent, sauf la recherche en ligne et l'interrogation de ressources.

## Technical Decisions

**AD-7 : `harness.prompts.construire_messages` est la seule construction de prompt.**
- `construire_messages(tache, entree, passages, outils)` est une fonction pure : même entrée, même sortie à l'octet près en JSON canonique. **Aucun autre module ne compose de prompt** : ni le service, ni les traitements de Tâche, ni le banc, ni `data`, ni `train`. Ils appellent tous cette fonction.
- Le résultat est au format OpenAI (`system`, `user`, `assistant` avec `tool_calls` structurés, `tool` avec `tool_call_id`), valide pour `valider_conversation`. `messages[0]` est le prompt système de la Tâche.
- Les passages sont formatés uniquement par `formater_passages`, numérotés `[1]`, `[2]`… avec titre, URL et date. Une entrée objet (CR, LC, CO, RE, CT) a ses clés nommées (`notes`/`transcription`, `texte`, `objet`, `elements_connus`, `type_courrier`, `longueur_demandee`) rendues par une seule règle, documentée dans le module.
- Les prompts de morceau et de fusion des comptes rendus (`CR-morceau`, `CR-fusion`) sont aussi des fichiers de `config/prompts/taches/`, soumis à la même règle D1.1.
- `tools` vient toujours de `config/outils-mcp.toml`. Le rendu en tokens est fait par le chat template officiel uniquement (`llama-server --jinja` à l'inférence) : jamais de template réécrit à la main.

**AD-14 : Harnais sans état.**
- `AssistantService.repondre(tache, messages, options)` renvoie un itérateur d'évènements typés de `core.evenements` : `Jeton`, `AppelOutil`, `ResultatOutil`, `AppelNonConforme`, `Sources`, `Avertissement`, `Progression`, `Repli`, `Fin`, `Erreur`.
- `config/taches.toml` contient 9 codes (Q, RD, CR, LC, CO, RE, CT, NR, TR), un champ `actif` et `outils_autorises` (les 5 outils pour RD, une liste vide pour la rédaction). Un registre paresseux associe chaque code à son module de traitement.
- En Mode connecté, le Harnais interroge le MCP d'abord, puis l'Index local en repli. Une seule fonction, `harness.citations`, vérifie les URL ; le banc la réutilise.

**Hexagonal (AD-1)** : le service ne connaît que les ports de `core.ports` (`LlmPort`, `EmbedderPort`, `VectorStore`, `ToolPort`, `NetGate`, `ModePort`, `JournalRequetes`), injectés par la racine de composition `cli/_assemblage.py`. `harness` est en couche 2 et n'importe que des couches inférieures. La fermeture runtime n'importe ni `anthropic`, ni `mistralai`, ni `torch`, etc. (AD-2).

**Outils (AD-8)** : 5 outils au plus, aux schémas figés. Chaque appel est validé par `mcp.outils.valider_appel` avant envoi ; un appel invalide devient un évènement `AppelNonConforme` et n'est jamais envoyé. Au passage en connecté, le schéma serveur est comparé au schéma figé : un outil inconnu est ignoré ; un outil absent ou modifié déclenche `Repli` et une entrée de journal. Quand le modèle a `protocole_outils = "json-generique"`, les appels passent par la voie JSON contrainte de l'adaptateur, sans autre changement dans la boucle.

**Réseau (AD-4)** : toute requête passe par `slmsp.net`, profil `assistant` (Liste blanche, correspondance exacte du nom d'hôte, journal). `ModeSonde` vit dans `harness.modes`, `ModeFixe` sert au banc. Le hors ligne forcé est une entrée fournie par l'appelant (`--hors-ligne`).

**Configuration** :
- `harness/config.py` (`ConfigHarnais`) et `config/harnais.toml` portent les itérations maximales de la boucle d'outils, la période de sonde, la réserve de sortie et le chevauchement CR. La story 4.2 les crée ; les stories 4.3 et 4.4 les lisent sans les modifier.
- `k` et le seuil de pertinence sont lus via `slmsp.index.config`, source unique.
- Pour les comptes rendus, la longueur se compte avec `LlmPort.compter_tokens`. Le découpage suit les limites de paragraphe et c'est une fonction pure.
- Options d'évaluation (`temperature = 0`, `seed`) transmises à `LlmPort`. `Fin` porte l'usage et le délai au premier token.

**Erreurs et journaux** : en cas d'erreur, l'évènement `Erreur` ne contient aucun détail technique. Le détail part dans le journal technique, sans le texte saisi. Les erreurs héritent de `SlmspError`. Codes de sortie de la CLI : 0 à 5.

## UX & Interaction Patterns

Cet epic ne livre que la CLI. Sorties attendues de `slmsp ask --modele base:<slug> [--tache] [--hors-ligne] [--conversation f.json] [--json] [--journal]` :
- réponse au fil de l'eau, puis sources numérotées (titre, URL, date de l'Index), avertissement pour Q, tableaux RD rendus depuis les résultats d'outils ;
- `--conversation` ajoute l'échange au fichier ;
- `--json` émet les évènements bruts ;
- `--journal` affiche heure, hôte, termes et statut ;
- progression « Partie i sur n » pour les comptes rendus longs.

Les libellés fixes servent ensuite à l'application J4 : « Ne vaut pas avis juridique. », « non vérifié en ligne ».

## Cross-Story Dependencies

- Ordre : 4.1 (après 1.3) → 4.2 (après 2.3, pour `slmsp.index.config`) → 4.3 (après 3.2, Bac à sable) et 4.4 en parallèle → 4.5 (après 4.3, 4.4, 2.3, 3.3).
- Propriété des fichiers : chaque story ne modifie que ses propres modules. `harness/config.py` appartient à la story 4.2.
- Consommateurs en aval :
  - 5.3 (banc, qui dépend de 4.3 et 4.4) ;
  - 6.3 (prompt TR et `construire_messages`) ;
  - 6.4 (mesures, après 4.5) ;
  - 8.2 (sonde outils) ;
  - 9.2 et 9.4 (`construire_messages`, `harness.recherche_index`) ;
  - 10.2 (rendu et masque alignés sur `construire_messages`).

  Toute modification de la signature ou de la sortie de `construire_messages` les impacte tous.
- Fixtures de test : cassettes R-001 et R-002 de `eval/calibrage/` en lecture seule ; cassettes de simulation dans `tmp_path`.
