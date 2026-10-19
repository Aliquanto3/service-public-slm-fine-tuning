# Stories de l'incident de coût du Juge (19 octobre 2026)

Origine : la notation `runs/eval-notation/20261019-100345-ft-minicpm5-2b-3058` a réservé 8,67 € pour 80 items. La création du lot batch a échoué, l'erreur n'a pas été journalisée, et le lot a été compté au pire cas (`judge/claude.py:420-424`). Le pire cas par requête valait le maximum des `tokens_estimes` du lot (`claude.py:391`), soit 0,109 € par item contre 0,016 € réels en moyenne. Le garde-fou de 4,5 € de l'orchestrateur ne contrôlait qu'après coup. Décision d'Anaël du 19 en fin de matinée : ces trois stories passent avant toute nouvelle notation.

Écart de 0,22 € d'appels `direct` (vérifié par l'orchestrateur le 19 à 12 h 30) : **il n'y a pas d'écart**. Chaque appel direct a sa réservation au registre (36 réservations pour 33 lignes au journal des appels, les 3 de plus sont réglées à 0 €), et les montants sont égaux (0,2268 € et 0,2228 €). Aucune story n'est donc ouverte pour ce point.

Règles communes : aucun appel payant dans les tests (mocks), D1 inchangé, `uv run --no-sync`, tests ciblés puis `uv run ruff check` et `uv run ruff format --check`.

## Story INC-1 — Journaliser l'erreur de création d'un lot

Fichiers : `src/slmsp/judge/claude.py` (bloc `except Exception` de `_juger_par_lots`), `src/slmsp/judge/cache.py` s'il faut y ajouter un champ, tests `tests/judge/`.

- Quand `client.messages.batches.create` lève une exception, consigner le type de l'exception, le statut HTTP s'il existe et le message (tronqué à 500 caractères, sans en-têtes ni clé). On les écrit dans le journal standard (`logging`, niveau WARNING) **et** dans une trace persistante relisible après coup. La trace la plus simple : une ligne dans la table `appels` de `verdicts.sqlite` pour chaque requête du lot, avec `mode="batch"`, `lot_id`, `usage=None`, le coût imputé et une issue explicite (par ex. `erreur-creation-lot`), ou un champ `motif` sur la table `lots`. Choisir la solution la plus simple et rétrocompatible avec les bases existantes (migration additive seulement).
- Le motif de l'issue des items (`_Issue.motif`) distingue un échec de création de lot (`erreur-creation-lot`) de `erreur-api` générique, pour que le rapport de notation le montre.
- Le comportement de budget ne change pas dans cette story (pire cas si l'erreur n'est pas un refus 4xx).
- Tests : erreur 5xx simulée et erreur réseau simulée (exception non `APIStatusError`) : la trace persistante existe et porte le type et le message, le log WARNING est émis, le motif des items vaut `erreur-creation-lot`.

## Story INC-2 — Pire cas estimé par item

Fichiers : `src/slmsp/budget/registre.py` (`reserver_lot`, `taille_max_lot`, `_taille_max`), `src/slmsp/judge/claude.py` (`_juger_par_lots`, ligne `estimes = max(...)`), tests `tests/budget/test_lots.py` et `tests/judge/`.

- `reserver_lot` et `taille_max_lot` acceptent, en plus d'un entier (comportement actuel inchangé : même estimation pour chaque requête), une séquence d'entiers : une estimation d'entrée par requête, dans l'ordre du lot.
- Avec une séquence, le pire cas d'une requête est `cout_pire_cas(..., tokens_i, max_tokens, ...)` ; le nombre retenu est le plus long préfixe dont la somme tient sous le disponible (avec `TOLERANCE_EUR` comme aujourd'hui) ; le montant réservé est la somme de ce préfixe. `BudgetEpuise` si la première requête ne tient pas. Le message d'erreur donne le pire cas de la première requête.
- `_juger_par_lots` passe la liste des `tokens_estimes` des clés restantes, dans l'ordre des requêtes.
- Tests : un lot hétérogène (une requête longue, plusieurs courtes) réserve la somme des pires cas individuels, et non `n × max` ; le préfixe retenu s'arrête au bon rang quand le disponible est juste ; la forme entière garde ses résultats (tests existants inchangés).

## Story INC-3 — Garde-fou de coût estimé avant notation

Fichiers : `src/slmsp/judge/claude.py` (nouvelle méthode publique d'estimation), `src/slmsp/evaluation/notation.py` (`noter`, protocole `JugePrincipal`), `src/slmsp/cli/eval.py` (option), tests `tests/judge/`, `tests/evaluation/`, `tests/cli/`.

- Nouvelle option `slmsp eval run ... --plafond-estime EUR` (réel > 0), valable pour `--phase notation` et `--phase toutes`. Sans l'option, rien ne change.
- `JugeClaude.estimer(demandes) -> EstimationCout` (dataclass gelée : `nb_demandes`, `nb_en_cache`, `nb_a_juger`, `cout_estime_eur`, `cout_pire_cas_eur`). Aucun appel réseau, aucune écriture au registre ni au cache. Les items dont le verdict est en cache coûtent 0. Pour chaque item à juger :
  - entrée : `tokens_estimes` (même estimation que `_preparer`) ;
  - sortie estimée : moyenne des `tokens_sortie` des verdicts en cache pour le même `modele` et le même `effort`, s'il y en a au moins 20 ; sinon `max_tokens` ;
  - tarif du mode configuré (`batch` ou `direct`), par le module `budget.tarifs` (ajouter une fonction de coût estimé à côté de `cout_pire_cas` si besoin, sans majoration d'entrée) ;
  - `cout_pire_cas_eur` : somme des `cout_pire_cas` individuels (même formule que la réservation par item d'INC-2).
- Dans `noter`, quand un plafond est donné : construire les demandes, appeler `estimer` **avant** `nouveau_run` et avant tout appel payant (juge principal comme second juge). Si `cout_estime_eur > plafond`, lever une erreur `SlmspError` dont le message donne l'estimation, le plafond, `nb_a_juger` et `nb_en_cache`. Aucun run n'est créé, aucun appel n'est fait. La CLI sort alors en code 1 avec ce message. Si l'estimation passe, l'afficher (`rapporter`) et poursuivre. Note : les demandes dépendent des contrôles automatiques ; si les construire avant `nouveau_run` impose un gros remaniement, il est admis de créer le run puis de le terminer au statut existant le plus proche (motif `plafond-estime`) sans aucun appel payant. Consigner le choix.
- Un juge principal sans méthode `estimer` (doublures de test, autres juges) : l'option est refusée avec une erreur claire, plutôt qu'ignorée.
- Vérifier et tester qu'une notation relancée sur un run de génération rejuge les items restés `non-juge` (motif `erreur-api` ou `erreur-creation-lot`) au run précédent : ils ne sont pas en cache et sont donc soumis à nouveau.
- Tests : estimation avec cache partiel ; refus au-dessus du plafond sans run créé ni appel (doublure de client qui échoue si appelée) ; passage sous le plafond ; repli sur `max_tokens` quand moins de 20 verdicts en cache ; option CLI (parsage, valeur ≤ 0 refusée en code 2).
