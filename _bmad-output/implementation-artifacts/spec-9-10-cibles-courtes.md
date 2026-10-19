# Story 9.10 — Réponses cibles courtes, sans titre de tête (régénération Mistral)

Décision d'Anaël du 19 octobre 2026 (après-midi) : régénérer par Mistral les réponses cibles du jeu d'entraînement, avec une consigne de longueur, plutôt que tronquer. La qualité prime sur le coût. Budget Mistral : 10 € autorisés, que la session principale inscrit dans `budgets.toml`, pas cette story.

Constats (fichier d'état du 19) : après fine-tuning, MiniCPM5-2B produit des réponses deux fois plus longues que la Baseline. Il ouvre par un titre en gras (144 sorties sur 225 pour M1 v4) et tronque ses CR. Les cibles v4 sont trop longues : en médiane, Q fait 237 mots, contre 116 pour les références du jeu d'évaluation, et CT 234 mots. v4 n'a plus aucun CR, parce que toutes les cibles CR dépassaient 1 024 tokens.

## D1 (bloquant)
Claude n'écrit aucune donnée d'entraînement : ni exemple de réponse, ni amorce, ni few-shot. Les seuls changements de gabarit admis sont des **consignes** (longueur, forme) et des emplacements. Les fixtures de test restent manifestement factices (`"<réponse-factice-1>"`).

## Périmètre

### 1. Plafond de mots par tâche dans les gabarits du générateur
- Nouvelle table `[generateur.plafonds_mots]` dans `config/donnees.toml`, avec ces valeurs par défaut :
  - `Q = 160`, soit environ le p90 des références d'évaluation (165 mots) ;
  - `RD = 120` (p90 des références : 108) ;
  - `CR = 450`, ce qui laisse de la marge sous les 1 024 tokens du `max_tokens` d'évaluation ;
  - `LC = 150`, `CT = 150`, `generique = 200` : pas de référence mesurable, estimation de l'orchestrateur, valeurs à ajuster.
  
  Un commentaire indique la source de chaque valeur. RE garde son mécanisme actuel (`plafond_mots` dérivé de `longueur_demandee`). CO, la correction d'un texte donné, n'a pas de plafond, car sa longueur suit le texte.
- Les gabarits `traces-q.md`, `traces-rd.md` (message final seulement), `cr.md`, `lc.md`, `ct.md` et `generique.md` reçoivent deux consignes :
  - « Ta réponse ne dépasse pas {plafond_mots} mots. » ;
  - « Commence directement par le contenu : pas de titre, pas d'intertitre en première ligne, pas de phrase d'introduction (« Voici… »). »

  Les autres consignes existantes ne changent pas. `{plafond_mots}` est résolu par le générateur depuis la nouvelle table. Une tâche sans valeur dans la table mais avec l'emplacement dans son gabarit lève `GabaritInvalide`. Le `version` du front matter de chaque gabarit modifié est incrémenté.
- `max_tokens` des gabarits modifiés : le ramener à environ 2 × le plafond en tokens, par exemple CR à 1 200 et les autres à 600. C'est une borne dure qui évite de payer des réponses trop longues ; une réponse coupée par ce plafond est déjà écartée par le filtre (`tronquee`).

### 2. Réutiliser les transcriptions CR d'un run antérieur
- Nouvelle option `slmsp data generate --depuis SEED_RUN_ID --transcriptions-depuis GENERATE_RUN_ID`. Elle relit `amorces-derivees.jsonl` du run désigné, et, pour chaque session CR dont l'amorce a déjà une transcription, saute l'appel `transcription-cr` et réutilise le texte (`sessions.py:270`, `_deux_temps`). Le MANIFEST du nouveau run trace le run source et le SHA de son `amorces-derivees.jsonl`.
- Garde-fous :
  - la transcription n'est réutilisée que si l'amorce source est identique (même identifiant et même SHA d'amorce) ;
  - sans correspondance, la transcription est générée normalement ;
  - un run source introuvable ou d'un autre type est une erreur d'usage (code 2).
- Le gabarit `transcription-cr.md` ne change pas.

### 3. Nettoyage : titre en gras de tête
- La règle déterministe de `data build --nettoyage` (story 9.9) retire aussi une **première ligne** qui n'est qu'un titre en gras (`**…**` seul sur la ligne, ou ligne de titre markdown `#…`), suivie d'une ligne vide. Le retrait est compté au rapport (`titres_retires`) par tâche. Il ne s'applique jamais au-delà de la première ligne.

### 4. Estimation avant dépense
- `data generate` affiche, avant le premier appel, le nombre d'appels prévus par gabarit (transcriptions réutilisées déduites) et un coût pire cas (`cout_pire_cas` au tarif Mistral avec `max_tokens` de chaque gabarit). Le registre de budget reste le garde-fou réel.

## Tests
- Résolution de `{plafond_mots}` par tâche, erreur si la valeur manque.
- Les gabarits modifiés contiennent les deux consignes et aucun exemple de réponse : un test lit le corps des gabarits et vérifie l'absence de bloc d'exemple, comme les tests D1 existants.
- Réutilisation des transcriptions : correspondance, absence, SHA différent ; client Mistral doublé qui échoue si `transcription-cr` est appelé pour une amorce réutilisable.
- Nettoyage du titre de tête : `**Titre**` puis ligne vide est retiré ; un gras au milieu du texte est gardé ; une seule ligne au plus.
- Estimation : comptes d'appels avec et sans réutilisation.
- Aucun appel payant dans les tests.

## Hors périmètre
Lancer la génération réelle : c'est la session principale qui le fera, sous budget. Le gel du jeu d'évaluation ne change pas.
