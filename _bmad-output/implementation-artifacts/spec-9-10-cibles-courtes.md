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
