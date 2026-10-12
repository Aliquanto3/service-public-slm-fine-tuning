---
title: Revue du spine — réconciliation avec le Jeu d'évaluation
cible: ARCHITECTURE-SPINE.md (AD-10, AD-11, AD-12, AD-13 ; aussi AD-4, AD-14, AD-17)
date: 2026-10-12
mode: lecture seule
sources_lues:
  - eval/SPEC-jeu-evaluation.md (v1.0)
  - eval/grille-juge-v1.md (v1.0)
  - eval/calibrage/build_calibrage.py (build_items, inject, _mcp_session, cmd_record)
  - eval/calibrage/echantillon-calibrage.jsonl (16 items, clés inspectées une par une)
  - eval/calibrage/cassettes/R-001.json, R-002.json, tools-list.json
  - _bmad-output/planning-artifacts/decisions.md (D6)
---

# Revue : réconciliation du spine avec le Jeu d'évaluation

## Verdict

Le spine est **compatible dans ses grandes lignes** : deux phases génération/notation, Juge qui ne calcule pas les scores, format de cassette du calibrage, gel par manifeste, kappa par Tâche, 20 % de second juge. Il **n'est pas encore suffisant pour que deux développeurs produisent des unités compatibles**. Il manque cinq contrats : la correspondance calibrage → SPEC, la clé du cache de verdicts, le schéma de sortie du Juge par Tâche, la sémantique du Bac à sable (cassettes d'erreur, réponse vide, portée de « la plus proche », appel non prévu ou non) et le schéma de `scores.json`. Un point contredit directement une source : `decisions.md` D6 fait du calibrage « la référence de format », alors qu'AD-11 prend la SPEC §3 comme modèle et se contente de « tolérer » les champs en plus du calibrage. Or le calibrage n'a pas seulement des champs en plus : il lui manque des champs exigés par la SPEC et il en renomme d'autres.

Sévérités : **Bloquant** (casse un test, un score ou une comparaison entre modèles), **Majeur** (deux implémentations divergentes probables), **Mineur** (précision utile).

## 1. Schéma des items (AD-11)

### C1. Le calibrage ne valide pas contre un modèle pydantic « SPEC §3 » [Bloquant]

Le spine dit : un modèle pydantic par Tâche, avec les champs communs et de référence de la SPEC §3, et les champs supplémentaires du calibrage tolérés (AD-11). Les conventions de test disent : « fixtures tirées de `eval/calibrage/` ». H-JUGE-COUT et H-TOOLS se mesurent sur le calibrage. En réalité, les 16 items du calibrage ont, par rapport à la SPEC §3 :

| Écart | SPEC §3 | Calibrage (constaté) | Conséquence si non traité |
|---|---|---|---|
| Champs communs absents | `theme`, `parametres`, `fictif`, `version_item` | absents des 16 items | validation en échec, ou valeurs par défaut implicites différentes d'un dev à l'autre |
| `provenance[]` | `{type, url, consulte_le}` | `{source, url?, role?, note?, consulte_le}` ; pas de `type` ; `url` absent pour les items fictifs | échec de validation |
| `licence_source` | identifiant (`"Etalab-2.0"`) | phrase libre (« Amorce : MIT. Fiche : … ») | pas de contrôle automatique possible |
| `entree` | texte | texte (Q, R, NR) **ou** objet (`consigne`, `texte`/`document`/`notes`, `nb_mots`, `longueur_demandee`, `type`, `objet`, `elements_connus`) | le rendu en message utilisateur n'est défini nulle part (voir C4) |
| Q « sans réponse » | `sans_reponse` (booléen) + `orientation_attendue` | `comportement_attendu: "absence_de_source"`, pas de `sans_reponse` ; orientation dans `elements_cles` | avec `sans_reponse` absent = faux, Q-002 est jugé comme une question normale : la grille Q applique alors le mauvais critère |
| RD cassettes | `cassettes` (liste de chemins) | `cassette` (chaîne, relative à `eval/calibrage/`) | deux résolveurs de chemin différents |
| RD `mode` | connecté / hors ligne / repli | absent | valeur par défaut implicite |
| RD `valeurs_attendues` | champ dédié | dans `reponse_reference.nombre_total` / `cinq_premiers` (objet, pas texte) | le contrôle « valeurs identiques » n'a pas d'entrée fixée |
| RD `reponse_reference` | texte, d'après l'exemple | objet (`jeu_principal`, `texte`…) | type de champ variable selon la Tâche |
| LC `kandel_moles_entree` | champ de référence | absent | calculé à la volée par certains, lu dans l'item par d'autres |
| RE `longueur_demandee` | champ de référence de niveau 1 (et `parametres.longueur`) | dans `entree`, en texte libre (« courte (3 à 5 phrases) », « moyenne (150 à 200 mots) ») | ne correspond pas aux seuils de la grille (80 / 200 / 400 mots) |
| CT `type_courrier` | champ de référence | `entree.type` | idem |
| CO `fautes[]` | `position, erreur, correction, type` | `debut, fin, erreur, correction, type, contexte_fautif` + `nb_fautes`, `note_positions` | « position » n'a pas de définition dans la SPEC ; le calibrage la précise (indices de caractères 0-indexés, fin exclue, dans `entree.texte`) |
| `tache` | libellé (« Question ») | libellé, y compris pour R-/RS- (« Recherche de données », « Résumé ») | aucune table libellé ↔ code dans le spine |

**Correctif proposé pour AD-11.** Trancher explicitement entre D6 et la SPEC. Proposition : le format cible est la SPEC §3, **complétée** par les précisions utiles du calibrage (`debut`/`fin` pour CO ; `entree` objet par Tâche ; `appels_attendus[].regle`). Ajouter dans `slmsp.core.items` :
1. une **table de correspondance calibrage → SPEC**, appliquée uniquement quand le préfixe est R- ou RS- ou que la source est `eval/calibrage/` : `R→RD`, `RS→RE`, `cassette→cassettes=[…]`, `comportement_attendu=="absence_de_source" → sans_reponse=true`, `entree.longueur_demandee → longueur_demandee`, `entree.type → type_courrier`, et des valeurs par défaut **écrites** (`mode="connecte"`, `fictif` déduit de `licence_source`/`provenance`, `version_item=0`, `theme="non-classe"`) ;
2. le **type d'`entree` par Tâche** (texte pour Q, RD, NR ; objet avec des clés nommées pour CR, LC, CO, RE, CT) ;
3. la **table libellé ↔ code** de Tâche, avec un discriminant fondé sur le préfixe d'`id` ;
4. une règle de résolution des chemins de cassettes (relatifs au dossier du jeu ou du calibrage qui contient le JSONL).

Le code ne réécrivant jamais `eval/` (AD-11), l'adaptation doit se faire à la lecture. Sinon, le calibrage doit être regénéré au format SPEC par `build_calibrage.py`, ce qui revient à une décision d'Anaël.

### C2. Les règles d'appels attendus sont en prose [Bloquant pour le score RD]

`appels_attendus[].regle` contient du texte libre : « query contient « défibrillateur » ou « DAE » (insensible à la casse et aux accents) ; autres paramètres optionnels », « peut être omis si… », « page_size >= 5 ». La grille RD calcule « Appel valide » automatiquement d'après `appels_attendus`. Aucun programme ne peut appliquer cette prose de façon déterministe.

**Correctif.** Ajouter à AD-11 (ou à un AD « Scores ») un mini-langage de règles, par argument : `exact`, `contient_un_de[…]` (après normalisation casse et accents), `min`, `optionnel`, et par appel : `optionnel`, `ordre_libre`. La prose reste en `regle` pour l'humain. Le calibrage est traduit par la table de correspondance de C1.

### C3. Le manifeste ne fige pas tout ce qui fait le score [Majeur]

La SPEC §6 demande le SHA-256 de chaque fichier, de chaque cassette, de la grille et la date. AD-11 reprend items, cassettes et grille. Ce qui manque :
- le **schéma du manifeste** (clés, chemins relatifs, statut `provisoire`) ; la SPEC nomme la version `v1.0-provisoire` mais le dossier `eval/jeu/v1.0/` ;
- les éléments qui changent la note sans changer les items : le gabarit de prompt du Juge, le schéma JSON de sortie du Juge, les prompts système des Tâches (`config/prompts/taches/`), la fonction de rendu des entrées (C4). Ils peuvent aller dans `run.json` (AD-21), mais il faut le dire ;
- la commande de gel elle-même (« seule la commande de gel crée une nouvelle version ») n'est pas nommée dans la liste CLI ; la construction du jeu (SPEC §5 : double vérification, remplacement, échantillon `eval/revue/echantillon-revue-v1.0.md`) n'a pas de propriétaire dans le spine ;
- la SPEC place `eval/cassettes/` hors du dossier versionné `eval/jeu/v1.0/`. Une v1.1 qui corrige une cassette **réécrit** donc `eval/cassettes/`, ce qui contredit « le code ne réécrit jamais `eval/` » et l'immuabilité d'AD-21.

**Correctif.** Nommer `slmsp eval gel` (et `slmsp eval construire` si la construction est outillée), fixer le schéma de `MANIFEST.json` (`version`, `statut: provisoire|relu`, `date`, `fichiers: {chemin_relatif: sha256}`, `grille: {chemin, version, sha256}`, `echantillon_second_juge`, voir C9). Soit versionner les cassettes sous `eval/jeu/<version>/cassettes/`, soit déclarer qu'une cassette n'est jamais modifiée et qu'une correction crée un nouveau fichier.

### C4. Rendu de l'entrée en messages : non défini [Majeur]

AD-13 fait passer chaque item dans `AssistantService.repondre(tache, messages, options)`. Rien ne dit comment un `entree` objet (CR : `consigne` + `notes` ; CT : `type`, `objet`, `elements_connus` imbriqué) devient un message `user`, ni comment `parametres` (longueur) devient `options`. Deux développeurs écriront deux rendus différents, et les scores dépendront de celui retenu. De plus, AD-7 exige le même format à l'entraînement et à l'inférence : le générateur de données doit produire des entrées rendues de la même façon.

Autre trou : quelle Tâche du Harnais (et quel prompt système) sert pour **NR**, qui n'est pas une Tâche de l'Assistant ?

**Correctif.** Une fonction unique `slmsp.core.items.vers_messages(item) -> (tache_harnais, messages, options)`, partagée par `evaluation` et `data`, versionnée et hachée dans `run.json`. Ajouter une table code d'item → Tâche du Harnais, NR compris.

## 2. Cassettes et rejeu (AD-10)

### C5. Le format adopté « tel quel » ne porte pas la version du schéma d'outil [Majeur]

La SPEC §4 dit qu'une cassette contient « la requête, la réponse, la date et la version du schéma de l'outil ». Les cassettes du calibrage ont `server`, `recorded_at` et `initialize` (version du protocole 2025-06-18, serveur 1.28.1), plus les `interactions`. Elles n'ont pas d'empreinte du schéma d'outil : le `tools/list` est dans une cassette séparée, `tools-list.json`. AD-10 adopte ce format sans le compléter, alors qu'AD-8 calcule déjà l'empreinte du `tools/list`.

**Correctif.** Ajouter un champ facultatif en lecture, obligatoire en écriture par `slmsp mcp record` : `tools_list_sha256` (empreinte AD-8 au moment de l'enregistrement). Le banc refuse une cassette dont l'empreinte diffère de `config/outils-mcp.toml`. Préciser aussi l'emplacement de la cassette `tools/list` du jeu (par exemple `eval/jeu/<v>/cassettes/tools-list.json`).

### C6. Nommage, portée et appariement des cassettes : ambigus [Majeur]

- **Un fichier ou plusieurs par item ?** La SPEC prévoit `eval/cassettes/RD-xxx/*.json` (plusieurs fichiers), le calibrage un fichier par item contenant toute la session, et AD-10 `eval/cassettes/<item>/`. Le nom des fichiers dans le dossier n'est pas fixé.
- **Portée de « la cassette la plus proche ».** Cherche-t-on dans les cassettes de l'item seulement, ou dans tout le magasin ? Exemple concret : le modèle appelle `get_dataset_info` sur R-002. Cet appel n'est enregistré que dans R-001 : avec une portée par item, il reçoit la réponse vide ; avec une portée globale, il reçoit les métadonnées de Géo'DAE. Les scores diffèrent.
- **« Partage le plus d'arguments ».** Faut-il compter les clés seules, ou les paires clé-valeur ? Après quelle normalisation ? Que faire en cas d'égalité ?
- **Appel prévu et appariement exact ne coïncident pas.** La cassette enregistre `search_datasets {query, page_size: 5}`, alors que `appels_attendus` ne demande que `query`. Un modèle qui appelle correctement `search_datasets {"query": "défibrillateurs"}` ne trouve pas de correspondance exacte et sera noté « appel non prévu ». Le spine ne dit pas si ce marqueur entre dans le score (la grille calcule « Appel valide » d'après `appels_attendus`, pas d'après les cassettes).
- **Appels répétés et pagination.** Rien ne dit si le rejeu est sans état (même réponse à chaque appel identique) ni comment l'`id` JSON-RPC de la réponse est réécrit.

**Correctif pour AD-10.** (a) Portée : les cassettes de l'item seulement. (b) Appariement : outil identique, puis nombre de paires (clé, valeur canonique) égales, égalité départagée par l'ordre dans la cassette. (c) « Appel non prévu » : évènement de trace, **sans effet sur le score**. Le score « Appel valide » se calcule uniquement contre `appels_attendus` (C2). (d) Rejeu sans état, `id` de la réponse remplacé par celui de la requête. (e) Nommage : `eval/jeu/<v>/cassettes/<ID>.json`, une session par fichier, au format du calibrage. Une variante d'erreur se nomme `<ID>.<cas>.json`.

### C7. Réponse vide normalisée et cassettes d'erreur : non spécifiées [Bloquant pour FR-9 et pour les 4 items de repli]

- La **charge exacte** de la « réponse vide normalisée » n'est pas donnée (`content: []` ? un texte « Aucun résultat » ? `isError: true` ?). Elle change ce que lit le modèle, donc la note.
- **Cassette d'erreur.** Le format du calibrage n'a qu'un champ `response` en JSON-RPC. Il ne sait représenter ni un délai dépassé (pas de réponse), ni une erreur HTTP, ni un serveur injoignable. Il faut aussi choisir entre deux formes d'erreur : JSON-RPC `error` ou résultat MCP `isError: true`.
- **Mode de l'item.** Le champ `mode` de la SPEC (connecté / hors ligne / repli) suppose que le banc fixe le Mode. Or, d'après AD-4, le seul propriétaire du Mode est `GestionnaireDeMode`, qui sonde `GET /health`, une vraie requête réseau. Le spine ne dit pas comment le banc force le Mode ni comment cette sonde est simulée sous `BacASable`.

**Correctif.** (a) Fixer la réponse vide : `{"result": {"content": [{"type": "text", "text": "<texte en config>"}], "isError": false}}`. (b) Étendre l'interaction d'un champ facultatif `simulation: {"type": "delai_depasse" | "erreur_http" | "injoignable", "statut"?: int}`. Quand ce champ est présent, `response` peut être nul. `BacASable` lève alors la même exception que `McpEnDirect` dans ce cas, ce qui déclenche `Repli`. (c) `GestionnaireDeMode` accepte une sonde injectée. Le banc la règle d'après `item.mode`.

### C8. `build_calibrage.py record` contourne la passerelle réseau [Mineur]

`_mcp_session` utilise `urllib.request` directement, alors qu'AD-4 bannit `urllib.request` par la règle TID251. Si ruff s'applique à tout le dépôt, le script échoue au lint. Le spine prévoit `slmsp mcp record` sans dire que ce script historique en est exclu.

**Correctif.** Exclure `eval/calibrage/` de TID251 (script figé, hors paquet) et écrire que `slmsp mcp record` produit le même format, avec `tools_list_sha256` en plus (C5).

## 3. Juges (AD-12)

### C9. Clé du cache de verdicts : un verdict périmé peut être réutilisé [Bloquant]

La clé du cache est (`item_id`, SHA de la sortie, version de la grille, modèle juge, effort). Quand un item passe en v1.1 (SPEC §6 : `version_item` incrémenté, références corrigées), son `item_id` et la sortie du modèle peuvent rester identiques. Le cache rend alors le **verdict jugé contre l'ancienne référence**. Le gabarit de prompt du Juge et son schéma JSON ne font pas non plus partie de la clé.

**Correctif.** Clé = (`item_id`, SHA-256 du JSON canonique de l'item, SHA de la sortie, SHA de la section de grille envoyée, SHA du gabarit et du schéma, modèle, effort).

### C10. Le schéma de sortie du Juge n'est pas fixé par Tâche [Bloquant]

La grille donne `{"id", "criteres": {"<nom>": {"note", "justification"}}, "inventions", "confiance"}`. AD-12 reprend `criteres`, `inventions` et `confiance`, mais **oublie `id`**. Surtout, il ne fixe ni les **clés de critère** par Tâche, ni le **type de valeur** de chacune : des entiers 0/1/2 ou 0/1, une échelle 1 à 5 pour la clarté perçue, mais aussi un **rappel de 0 à 1** pour la couverture en CR et RE. Sans liste fermée, les scores, le kappa entre Juge principal et second juge, et le Comparatif lisent des clés différentes.

Deux autres ambiguïtés :
- Pour la couverture en CR et RE, la grille parle d'un critère « rappel de 0 à 1 ». Si le Juge rend directement le rappel, c'est lui qui calcule une partie du score, ce que la règle « le Juge ne calcule pas les scores » d'AD-12 interdit. Si le Juge rend une présence élément par élément (avec la règle de la moitié en CR pour une action sans responsable ou sans échéance), c'est le banc qui calcule. Le spine doit choisir.
- Le critère « Cas sans réponse » ne s'applique que si `sans_reponse` est vrai. Faut-il alors l'omettre ou le mettre à null dans les autres cas ?

**Correctif.** Ajouter à AD-12 une table des critères fermés, par exemple `Q: exactitude{0,1,2}, pertinence_source{0,1}, cas_sans_reponse{0,1}|absent` ; `CR: couverture_elements[{ref_index, present: 0|0.5|1}], absence_invention{0,1}, structure{0,1}` ; `LC: fidelite{0,1,2}, termes_juridiques{0,1}, clarte_percue{1..5}` ; `RE: fidelite{0,1}, couverture_elements[...]` ; `CT: conformite{0,1,2}` ; `NR: exactitude{0,1}` ; `RD (litige): libelle_correct{0,1}`. Le schéma JSON de chaque Tâche est généré à partir de cette table (enums), ce qui sert à la fois pour `output_config.format` côté Claude et pour la validation de la sortie Mistral.

### C11. Conditions de la SPEC §7 incomplètement transposées [Majeur]

| Condition SPEC §7 | Spine | Écart |
|---|---|---|
| Température 0 | non envoyée à Claude (signalé en question ouverte) | Le second juge Mistral accepte `temperature=0`, mais le spine ne le prévoit pas. La SPEC devra être amendée pour Claude. |
| Juge aveugle | oui | Ce que contient la « sortie » n'est pas défini. Pour Q, le critère « Pertinence de la source » exige que le Juge voie les sources citées (URL et titre, voire le passage). Faut-il envoyer le texte final seul, ou aussi les évènements `Sources` et `AppelOutil` ? |
| Ordre aléatoire pour les comparaisons | absent | La grille v1 ne prévoit que des notes absolues. Il faut écrire : « pas de comparaison par paires en v1 ; si on en ajoute, l'ordre est tiré avec une graine et consigné dans le verdict ». |
| Le Juge reçoit la section de grille de la Tâche | « au format de la grille » | Le contenu envoyé n'est pas défini : section seule, ou « Principes communs » + section ? Le découpage du Markdown (par titre `## <code> :`) non plus. Proposition : principes communs + section, extraits par le titre, et hachés (C9). |
| JSON validé par schéma | oui (Claude) | Rien n'est prévu pour la validation de la sortie Mistral, ni pour un échec de validation : relance (combien de fois ?) ou verdict « invalide » exclu du score ? |
| Kappa de Cohen pondéré par Tâche | oui | La pondération (linéaire ou quadratique) n'est pas fixée, ni les critères concernés. Un kappa sur un rappel continu n'a pas de sens. Le kappa est non calculable pour CO, entièrement automatique, et pour RD, où le Juge n'intervient que sur litige. |
| 20 % second juge, graine fixe | oui | Le tirage n'est pas stratifié : sur environ 170 items, une Tâche de 15 items peut n'en recevoir que 1 ou 2. On ne sait pas non plus si le même échantillon sert pour tous les modèles, ce qui est nécessaire pour comparer les kappas. |
| Relecture humaine de 20 % | « export de relecture de 20 % » (AD-13) | La stratification, la graine, l'emplacement et le format de l'export ne sont pas fixés. Le mécanisme qui consigne la « validation d'Anaël » non plus : aucun artefact ne lève le statut « non relu ». |

**Correctif.** (a) `temperature=0` pour Mistral. (b) Charge du Juge = entrée rendue + texte final + liste des sources citées (URL, titre) + références de l'item. (c) Pondération quadratique sur les critères ordinaux 0/1/2 ou 1 à 5, kappa simple sur les critères binaires, aucun kappa sur les rappels, Tâches CO et RD exclues du kappa. (d) Échantillon du second juge stratifié par Tâche (au moins 3 items par Tâche), tiré **une fois au gel** et inscrit dans le manifeste, donc identique pour tous les modèles. (e) Relecture : 20 % stratifié Tâche × difficulté, au moins un item par case, graine fixe, export dans `runs/eval/<run_id>/relecture.md`, validation consignée dans un fichier `relecture-validee.json` daté, lu par `scores`. (f) Après deux échecs de validation, le verdict est marqué `invalide`, l'item est exclu du score et compté à part.

### C12. Deux statuts « non relu » confondus [Majeur]

La SPEC §6 parle des scores obtenus sur un **jeu** `v1.0-provisoire`, dont les items n'ont pas été relus. La SPEC §7 parle des **verdicts** du Juge non relus (FR-25). AD-12 n'a qu'un statut, « non relu », levé « par validation d'Anaël ». Il faut distinguer `jeu_statut: provisoire|relu` et `verdicts_relus: bool`. Le statut « fragile » (kappa < 0,6) et le plafond à 50 de LC sont deux marques de plus à porter.

## 4. Calcul des Scores de Tâche (AD-12, AD-13)

### C13. Répartition automatique / Juge : implicite [Majeur]

Le spine liste les contrôles automatiques (URL, schéma, Kandel-Moles, fautes, emplacements) sans dire **quelles Tâches passent par le Juge**. D'après la grille, ce sont Q, CR, LC, RE, CT et NR (environ 170 items, ce qui recoupe H-JUGE-COUT), plus RD en cas de litige ; CO jamais. Points précis à fixer :

- **Q** : item réussi si exactitude = 2, pertinence = 1 et aucune URL inventée. Le contrôle des URL est `harness.citations` (AD-14). Il faut dire que le banc le réutilise sur la sortie **et** les `Sources` de la trace.
- **RD** : la grille ne précise pas si « Appel valide » se calcule en micro (tous les appels confondus) ou en macro (moyenne par item). Pour « Réponse exacte », rien ne dit comment extraire les nombres d'une sortie en français (« 208 », « 1 234,5 »), ni comment détecter le cas « libellé correct mais identifiant absent » qui déclenche le Juge. Pour les items en mode hors ligne ou repli, sans appel attendu, il faut savoir ce que vaut « Appel valide ».
- **LC** : `kandel_moles_entree` est une référence figée dans l'item d'après la SPEC, et absente du calibrage. Le spine renvoie l'algorithme de syllabation au Deferred, avec la mention « sans impact entre unités ». C'est faux : le constructeur du jeu et `evaluation.scores` doivent appliquer **la même** fonction, sinon le gain de +10 compare deux indices calculés différemment. Il faut une fonction unique, avec une version, et le calcul des deux indices au moment de la notation.
- **RE** : les seuils de longueur de la grille (80 / 200 / 400 mots) ne correspondent pas aux consignes du calibrage (« 3 à 5 phrases », « 150 à 200 mots »). Il faut fixer l'énumération `courte|moyenne|detaillee` et la source des seuils (config).
- **CT** : la grille dit « apparaît comme [Emplacement] ». On ne sait pas si cela veut dire le libellé exact entre crochets de `champs_a_laisser_en_emplacement`, ou n'importe quel texte entre crochets à l'endroit du champ. Et « aucune valeur n'est inventée », qui s'appuie sur `valeurs_interdites` du calibrage, n'est pas vérifiable automatiquement tel quel.
- **CO** : la liste des « reformulations de ponctuation typographique tolérées » doit vivre en config (AD-22).

**Correctif.** Une table « Tâche → contrôles automatiques → critères du Juge → formule », dans AD-12 ou dans un nouvel AD-12 bis. Sortir la syllabation du Deferred. Écrire que les formules de la grille sont implémentées dans le seul `slmsp.evaluation.scores`.

### C14. `scores.json` est un contrat entre unités sans schéma [Majeur]

AD-20 (Comparatif) lit `scores.json`, produit par AD-13. Aucun schéma n'est donné : score par Tâche, composantes (par exemple rappel et taux hors faute pour CO), nombre d'items notés, jugés ou invalides, statuts (`jeu_statut`, `verdicts_relus`, `fragile`, `plafonne_lc`), kappa par Tâche, version du jeu, empreinte du manifeste, coût du Juge. Le test octet par octet d'AD-20 repose sur des fixtures de ce fichier.

**Correctif.** Fixer le schéma pydantic de `scores.json` dans `slmsp.core` (couche 0), seul type partagé par `evaluation` et `compare`, ce qui est conforme à AD-1.

## 5. Points compatibles (rien à changer)

- Format de session de cassette (`server`, `recorded_at`, `initialize`, `interactions[{request, response}]`, JSON-RPC) : identique aux trois fichiers du calibrage.
- Enregistrement seulement par commande explicite : cohérent avec `build_calibrage.py`, qui ne lance jamais `record` par défaut.
- Codes Q, RD, CR, LC, CO, RE, CT, NR, avec R- et RS- tolérés en lecture du calibrage : conforme à la SPEC §7 bis.
- Contrôle du manifeste avant chaque évaluation et refus en cas d'écart ; pas de génération de données avant le gel commité : conforme à la SPEC §6, et même plus strict (`git diff --quiet`).
- Juge aveugle, kappa par Tâche, mention « fragile » sous 0,6, 20 % de second juge avec graine fixe, Juge qui ne calcule pas les scores : conforme à la SPEC §7 et à la grille.
- Le format de sortie `criteres` / `inventions` / `confiance` est conforme à la grille, sauf l'oubli d'`id` (C10).
- Deux phases (génération, puis notation) relançables séparément : compatible avec la SPEC §6 (« toutes les évaluations sont relancées »), à condition que la clé du cache soit corrigée (C9).

## 6. Hors périmètre strict, mais lié

- **Anti-fuite (AD-17)** : le contrôle porte sur « toutes les entrées et références du Jeu d'évaluation ». Il faut écrire qu'il inclut `eval/calibrage/`, puisque ses 16 items sont des items d'évaluation. Par ailleurs, `data` ne doit lire ni `eval/cassettes/` ni `eval/calibrage/cassettes/`. Les traces d'entraînement enregistrées en direct dans `data/cassettes/` peuvent contenir les mêmes réponses (Géo'DAE, Lorient) que les cassettes d'évaluation : il faut décider si l'anti-fuite s'applique aussi aux réponses d'outils.
- **Budget du second juge** : il puise dans le plafond Mistral de 30 € (AD-5), qu'il partage avec la génération de données. Il faudrait un sous-poste.

## 7. Synthèse des correctifs à porter dans le spine

| # | AD | Correctif | Sévérité |
|---|---|---|---|
| C1 | AD-11 | Table de correspondance calibrage → SPEC, valeurs par défaut écrites, type d'`entree` par Tâche, table libellé ↔ code ; arbitrer D6 / SPEC | Bloquant |
| C2 | AD-11 | Règles d'appels attendus lisibles par machine | Bloquant |
| C7 | AD-10, AD-4 | Réponse vide fixée, champ `simulation` pour les erreurs, sonde de Mode injectable | Bloquant |
| C9 | AD-12 | Clé du cache avec SHA de l'item, de la section de grille, du gabarit et du schéma | Bloquant |
| C10 | AD-12 | Table fermée des critères par Tâche, `id` dans la sortie, présence élément par élément au lieu d'un rappel rendu par le Juge | Bloquant |
| C3 | AD-11 | Schéma du manifeste, commande de gel nommée, cassettes versionnées avec le jeu | Majeur |
| C4 | AD-11, AD-7 | `vers_messages(item)` unique ; Tâche du Harnais pour NR | Majeur |
| C5 | AD-10, AD-8 | `tools_list_sha256` dans les cassettes | Majeur |
| C6 | AD-10 | Portée par item, appariement par paires, « appel non prévu » sans effet sur le score, rejeu sans état, nommage | Majeur |
| C11 | AD-12, AD-13 | Mistral à température 0, contenu envoyé au Juge, pondération du kappa, échantillons stratifiés tirés au gel, artefact de validation | Majeur |
| C12 | AD-12 | Deux statuts : `jeu_statut` et `verdicts_relus` | Majeur |
| C13 | AD-12 | Table Tâche → automatique / Juge / formule ; syllabation sortie du Deferred | Majeur |
| C14 | AD-13, AD-20 | Schéma de `scores.json` dans `slmsp.core` | Majeur |
| C8 | AD-4 | Exclure `eval/calibrage/` de TID251 | Mineur |
