---
title: "Story 9.10 — Réponses cibles courtes, sans titre de tête"
type: 'feature'
created: '2026-10-19'
status: review
baseline_revision: '1fa6bca'
---

# Story 9.10 — Réponses cibles courtes, sans titre de tête (régénération Mistral)

Décision d'Anaël du 19 octobre 2026 (après-midi) : régénérer par Mistral les réponses cibles du jeu d'entraînement, avec une consigne de longueur, plutôt que tronquer. La qualité prime sur le coût. Budget Mistral : 10 € autorisés, que la session principale inscrit dans `budgets.toml`, pas cette story.

Constats (fichier d'état du 19) : après fine-tuning, MiniCPM5-2B produit des réponses deux fois plus longues que la Baseline. Il ouvre par un titre en gras (144 sorties sur 225 pour M1 v4) et tronque ses CR. Les cibles v4 sont trop longues : en médiane, Q fait 237 mots, contre 116 pour les références du jeu d'évaluation, et CT 234 mots. v4 n'a plus aucun CR, parce que toutes les cibles CR dépassaient 1 024 tokens.

Révision 2, après la relecture adversariale de la spec : la réutilisation des transcriptions CR est **retirée**. Le `session_id` hache toute la chaîne de gabarits, et le build exige les deux appels de la session ; la réutilisation aurait demandé un remaniement risqué. Les transcriptions sont donc régénérées, pour environ 1 € de plus.

## D1 (bloquant)
Claude n'écrit aucune donnée d'entraînement : ni exemple de réponse, ni amorce, ni few-shot. Les seuls changements de gabarit admis sont des **consignes** (longueur, forme), un emplacement, et le `max_tokens` du front matter, qui est une borne technique. Les fixtures de test restent manifestement factices (`"<réponse-factice-1>"`). La consigne de longueur n'entre jamais dans les messages SFT (`build.py`, `construire_messages`) : le vérifier par un test.

## Périmètre

### 1. Plafond de mots par tâche dans les gabarits du générateur
- Nouvelle table `[generateur.plafonds_mots]` dans `config/donnees.toml`, **avec son modèle pydantic** dans `src/slmsp/data/config.py`. `ModeleConfig` est en `extra="forbid"` : sans modèle, toute commande `data` casse. Valeurs : clé = code de tâche, entier > 0.
  - `Q = 160`, soit environ le p90 des références d'évaluation (165 mots) ;
  - `RD = 120` (p90 des références : 108) ;
  - `CR = 400`, pour rester sous les 1 024 tokens du plafond de nettoyage (`data/nettoyage.py`) ;
  - `LC = 150`, `CT = 150`, `generique = 200` : pas de référence mesurable, estimation de l'orchestrateur, valeurs à ajuster.
  
  Un commentaire indique la source de chaque valeur. CO, la correction d'un texte donné, n'a pas de plafond, car sa longueur suit le texte.
- **Nouvel emplacement `plafond_mots_tache`**, distinct de `plafond_mots`, qui reste réservé à RE (`generateur.py:693-701`, résolu depuis `longueur_demandee`). Il est résolu par le générateur depuis la table, selon la tâche du gabarit, et déclaré dans `## Emplacements` de chaque gabarit qui l'utilise. Une tâche sans valeur dans la table lève `GabaritInvalide` **au pré-vol** : avant le premier appel, quand le plan est construit, et non au premier appel.
- Les gabarits `traces-q.md`, `traces-rd.md`, `cr.md`, `lc.md`, `ct.md` et `generique.md` reçoivent deux consignes, rédigées **sans guillemets français ni citation**, car le test `test_gabarit_sans_texte_redige` interdit certains motifs (`tests/mistral/test_gabarits_generateur.py:34`) :
  - longueur : par exemple « Ta réponse ne dépasse pas {plafond_mots_tache} mots. » Pour RD, la consigne étant unique et envoyée à chaque tour, formuler « Ta réponse finale à l'Agent ne dépasse pas … mots » ;
  - forme : commencer directement par le contenu, sans titre ni intertitre en première ligne, et sans phrase d'annonce ou d'introduction.
  
  Les autres consignes existantes ne changent pas. Le `version` du front matter de chaque gabarit modifié est incrémenté.
- `max_tokens` des gabarits modifiés : 1 600 pour CR et 800 pour les autres. Une réponse coupée (`length`) devient un abandon payé. Le plafond dur doit donc garder une marge large ; seuls les tokens générés sont facturés.

### 2. Nettoyage : titre de tête
- La règle vit dans `core/nettoyage.py`, dans `nettoyer_cible`, la fonction unique que `verifier_nettoyage` revérifie dans `data/nettoyage.py` et `train/chargement`. `VERSION_NETTOYAGE` passe à **2** ; le MANIFEST trace la version appliquée.
- Nouvelle règle : retirer une **première ligne** qui n'est qu'un titre, c'est-à-dire `**…**` seul sur la ligne ou une ligne `#…`, ainsi que la ligne vide qui suit. Jamais au-delà de la première ligne. Le retrait est compté par tâche au rapport (`titres_retires`).
- Un jeu nettoyé en version 1 (v4) doit rester chargeable et vérifiable, avec la règle de sa version. Si ce n'est pas possible simplement, consigner pourquoi et proposer l'alternative.

### 3. Estimation avant dépense
- `data generate` affiche, avant le premier appel :
  - le nombre d'appels prévus par gabarit ;
  - un coût pire cas, au tarif Mistral, avec le `max_tokens` de chaque gabarit. Pour RD, compter `TOURS_OUTILS_MAX` appels par session (`sessions.py:76`). En reprise, déduire les appels déjà journalisés.
  
  Le registre de budget reste le garde-fou réel.

## Tests
- Modèle de config : table valide, clé inconnue ou valeur ≤ 0 refusée.
- Résolution de `{plafond_mots_tache}` par tâche ; erreur au pré-vol si une valeur manque ; `plafond_mots` de RE inchangé.
- Les gabarits modifiés passent les tests D1 existants (`test_gabarit_sans_texte_redige`), contiennent les deux consignes, et leur emplacement est déclaré.
- La consigne de longueur n'apparaît pas dans les messages SFT construits.
- Nettoyage v2 : `**Titre**` puis ligne vide est retiré ; `# Titre` aussi ; un gras au milieu du texte est gardé ; une seule ligne au plus ; un jeu v4 (version 1) se vérifie encore.
- Estimation : comptes d'appels, RD à `TOURS_OUTILS_MAX`, reprise.
- Aucun appel payant dans les tests.

## Hors périmètre
Les points suivants reviennent à la session principale :
- vérifier les conditions Mistral (D1.2), qui lève `PrealableNonSatisfait` si `conditions_verifiees_le` n'est pas la date du jour ;
- inscrire le budget ;
- lancer la génération réelle.

Le gel du jeu d'évaluation ne change pas.

## Implémentation

2026-10-19, Opus (dev-story). Aucun appel payant, aucun réseau, aucune génération réelle.

- **Config** : `[generateur.plafonds_mots]` dans `config/donnees.toml` (valeurs de la spec, une source commentée par clé) ; modèle `GenerateurDonnees` dans `data/config.py` (clés limitées à `TACHES_PLAFONNABLES` = Q, RD, CR, LC, CT, generique ; entier strict > 0 ; table optionnelle, vide par défaut).
- **Générateur** (`mistral/generateur.py`) : `charger_plafonds_mots` relit la table (le module `mistral` ne peut pas importer `data`, couches AD-1 : lecture tolérante, clés limitées aux Tâches générables, la validation stricte reste celle de `data.config`, appelée par la CLI). Emplacement réservé `plafond_mots_tache`, jamais rempli par une amorce. `GabaritInvalide` levé dans `_gabarit`, donc au pré-vol (`_gabarits` de `lancer_generation`, avant tout run ni appel). Nouvelle méthode `max_tokens(gabarit_id, tache)`. `plafond_mots` (RE) inchangé.
- **Gabarits** `traces-q`, `traces-rd`, `cr`, `lc`, `ct`, `generique` : version 2, `max_tokens` 1 600 (cr) ou 800, emplacement déclaré, deux consignes ajoutées en fin de liste (libellé exact) :
  - `- Ta réponse ne dépasse pas {plafond_mots_tache} mots.` (RD : `- Ta réponse finale à l'Agent ne dépasse pas {plafond_mots_tache} mots.`) ;
  - `- Commence directement par le contenu : pas de titre ni d'intertitre en première ligne, pas de phrase d'annonce ou d'introduction.`
- **Plan** (`data/generate.py`) : les emplacements réservés (`EMPLACEMENTS_RESERVES`) ne demandent pas d'amorce.
- **Nettoyage** (`core/nettoyage.py`) : `VERSION_NETTOYAGE = 2`, `VERSIONS_NETTOYAGE = {1, 2}`. `analyser_titre` (première ligne non vide seulement : `**…**` seul ou `#…`, ôtée avec les lignes vides qui l'entourent, si du texte suit) ; `analyser_cible(texte, version)` = préambule (v1) puis titre (v2). `nettoyer_cible`, `ligne_nettoyee` et `verifier_nettoyage` prennent la version ; `train/chargement.controler_nettoyage` rejoue la règle de la version du MANIFEST. Rapport : `titres_retires` par tâche.
- **Estimation** (`data/generate.py`, `estimer_plan`) : affichée par `consigner` après le plan et avant le premier appel : appels au plus, `max_tokens` et coût pire cas par gabarit, puis total.
- **Tests** : `tests/mistral/test_generateur.py` (résolution par tâche, pré-vol, table invalide, amorce refusée), `test_gabarits_generateur.py` (consignes, version, `max_tokens`), `tests/data/test_config_donnees.py`, `test_nettoyage.py` (titre, v1/v2, jeu v1 vérifiable), `test_generate.py` (estimation, reprise), `test_build.py` (consignes absentes des messages SFT). Fixtures `DONNEES` des tests complétées par la table ; `test_budget_epuise_arret_propre` recalé (plafond 0,0015 € pour `max_tokens` 800).
- Tests ciblés (data, mistral, core, train, cli/test_data, architecture) : 1 935 passés. Ruff, format et contrôle rapide verts. Suite complète non lancée (consigne).

## Auto Run Result

Décisions prises seul (solution la plus simple et la plus réversible) :
1. **Jeu v4 nettoyé en version 1** : reste chargeable et vérifiable. La version est un paramètre de la règle, et `charger_jeu` rejoue celle du MANIFEST (`nettoyage.version`). Un jeu v1 vérifié avec la règle v2 est refusé (test). Aucun MANIFEST existant n'est modifié.
2. **Ordre en version 2** : préambule « Voici » d'abord, puis titre sur le texte restant. Une cible « Voici … :\n\n**Titre**\n\nCorps » perd donc deux lignes. Le titre seul n'examine jamais que la première ligne non vide. Comme pour le préambule, toutes les lignes vides qui suivent sont ôtées, pas seulement une. Un titre seul, sans texte après, est gardé.
3. **RD au pire cas** : l'estimation compte `TOURS_OUTILS_MAX + 1` appels par session (4 tours plus l'appel de réponse finale ou de dépassement, `sessions._trace_outils`), et non `TOURS_OUTILS_MAX` comme écrit dans la spec : c'est le vrai maximum. À confirmer par Anaël.
4. **Coût pire cas** : sortie au `max_tokens`, entrée estimée (caractères de la consigne, des amorces et des passages divisés par 3, plus les sorties pire cas des appels précédents de la session), au tarif et avec la majoration du registre. Les résultats d'outils RD ne sont pas comptés, ce qui est signalé à l'affichage. En reprise, les sessions closes sont exclues, et les N premiers appels `ok` journalisés d'une session ouverte sont déduits. Tarif inconnu : « tarif inconnu », sans erreur.
5. **CO dans la table** : refusé par `data.config`, toléré par le Générateur (Tâche générable, simple lecture). La CLI `data generate` charge `data.config` avant de construire le Générateur, la règle stricte s'applique donc en réel.

Points ouverts :
- Le libellé des deux consignes est une **décision de fond** (formulation envoyée à Mistral). Elle est à confirmer par Anaël avant la génération réelle.
- Les `session_id` changent avec les gabarits : la génération repart de zéro sur ces Tâches, comme prévu par la révision 2.
