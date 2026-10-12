---
title: 'Story 7.1 — Outil de construction du Jeu d''évaluation et instantanés des sources réelles'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: 'bd1ad853716d87db72c4b359c2f47bc9f0422e92'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/eval/SPEC-jeu-evaluation.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-7-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Instantanés réels incomplets : LEGI CGCT, code civil, commande publique et les deux xlsx de questions manquent.
    evidence: |-
      Téléchargement arrêté à 07h54 sur consigne d'Anaël (pas d'internet avant 08h30). Le .part de CGCT est conservé ; relancer `sources --dest <dépôt principal>/data/raw/eval-sources`, qui ne retélécharge pas les fichiers présents.
    location: >-
      data/raw/eval-sources/INDEX.json (dépôt principal)
    severity: medium
---

<intent-contract>

## Intent

**Problem:** La piste 2 doit rédiger 225 items sur sources réelles. Il lui manque un outil reproductible, hors du paquet `slmsp`, pour figer les sources consultées, lire une fiche, assembler les brouillons et mesurer la composition et les rejets par rapport à SPEC §2.

**Approach:** Un script autonome `eval/outils/construire_jeu.py` (stdlib + dépendances en ligne PEP 723 : `duckdb`, `openpyxl`). Il a cinq sous-commandes : `sources`, `fiche`, `assembler`, `composition` et `rejets`. Son client HTTP est en lecture seule et vérifie l'hôte, y compris à chaque redirection, contre une liste codée issue de D1.5. Les instantanés sont épinglés sur la révision du dépôt HF et inventoriés dans `INDEX.json`.

## Boundaries & Constraints

**Always:**
- Le script tourne par `uv run --no-project --python 3.12 --with duckdb --with openpyxl python -I eval/outils/construire_jeu.py <cmd>` ou par `uv run --script`.
- Il n'importe que la stdlib au niveau module. `duckdb` et `openpyxl` sont importés à l'usage.
- Il n'importe aucun module `slmsp`. L'import optionnel autorisé (`slmsp.core.texte`, `slmsp.core.items`) n'est pas utilisé en 7.1.
- Toute requête passe par une fonction unique qui vérifie le schéma `https`, la méthode (GET ou HEAD) et l'hôte **avant** la connexion et à chaque saut de redirection.
- Hôtes autorisés : `huggingface.co` et ses CDN (`*.hf.co`, `*.huggingface.co`), `www.data.gouv.fr`, `mcp.data.gouv.fr` et les hôtes de la Liste blanche (addendum §B).
- Reprises sur 429, 5xx et erreurs réseau (3 tentatives au minimum, attente exponentielle). Écriture dans `.part`, puis renommage.
- Un fichier déjà présent n'est jamais retéléchargé sans `--force`. Rien n'est jamais supprimé.
- Chaque fichier écrit est ajouté à `<dest>/INDEX.json` avec son chemin relatif, son URL, `consulte_le` (date ISO), sa révision, sa taille et son SHA-256.
- Sorties JSONL en UTF-8 et LF ; rapports en Markdown sur stdout (UTF-8).

**Never:**
- Écrire dans `src/`, `config/` ou `eval/jeu/` (sauf `assembler`), ni dans `tests/` hors de `tests/eval_outils/`.
- Faire une requête POST ou contacter l'API MCP : les cassettes relèvent de `slmsp mcp record`.
- Écrire le manifeste : il relève de `slmsp eval gel`.
- Laisser duckdb ouvrir une connexion réseau : on télécharge d'abord, puis on interroge localement.
- Faire un appel réseau dans les tests.
- Supprimer ou modifier les instantanés existants (`hf/*.json`, `*.xlsx`).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Hôte refusé | URL `https://example.com/x`, ou une redirection vers cet hôte | Aucune connexion ouverte vers l'hôte | `HoteRefuse`, code de sortie ≠ 0 |
| Reprise | 2 réponses 503, puis 200 | Fichier écrit, entrée INDEX ajoutée | Attentes croissantes ; échec après N tentatives |
| Déjà présent | Fichier cible existant, sans `--force` | Aucun téléchargement ; entrée INDEX conservée ou ajoutée | — |
| Assemblage OK | `Q.jsonl` et `NR.jsonl` dans `tmp_path` | `items.jsonl` trié (code, numéro), UTF-8, LF | — |
| ID dupliqué | Même `id` dans deux brouillons | Aucun fichier écrit | Erreur listant le doublon, sortie ≠ 0 |
| ID mal formé | `id` `R-001`, ou préfixe ≠ fichier | Aucun fichier écrit | Erreur explicite |
| Item rejeté | Dernier verdict `rejete` dans `verification/Q.jsonl` | Item exclu et signalé | — |
| Composition | Brouillons partiels | Tableau Tâche × difficulté (cible, réel, écart), thèmes, producteurs RD, Q sans réponse, part d'amorces, anomalies de structure (champs manquants, positions CO fausses) | — |
| Rejets | `verification/*.jsonl` | Taux de rejet par Tâche et par motif | Ligne illisible signalée, sans plantage |
| Fiche | `fiche F1344` | Titre, URL, puis les chunks numérotés | Fiche absente : sortie ≠ 0 |

</intent-contract>

## Code Map

- `eval/calibrage/build_calibrage.py` -- référence (lecture seule) :
  - `cmd_fetch` (l. 811) : URL HF, liste des fiches, filtres LEGI ;
  - `sp_doc` (l. 52) : format des chunks (`doc_id`, `chunk_index`, `title`, `url`, `text`) ;
  - `question_seeds` (l. 78) : lecture xlsx.
- `eval/calibrage/echantillon-calibrage.jsonl` -- format des items (champs par Tâche, `provenance[].consulte_le`, `amorce_usager`, `reponse_reference.jeu_principal.producteur` pour RD).
- `eval/SPEC-jeu-evaluation.md` §2 (cibles), §3 (champs), §5.2 (motifs de rejet), §7 bis (codes).
- `<dépôt principal>/data/raw/eval-sources/hf/` -- instantanés existants du calibrage (`sp_*.json`, `legi_crpa.json`, `assistant_ia_questions.xlsx`, `sp_index.csv`), à ne pas toucher. Le chemin par défaut `--dest` du worktree est relatif ; la story utilise le chemin absolu du dépôt principal.
- Sources HF vérifiées le 2026-10-12 (tree API) :
  - `AgentPublic/service-public` : `latest/train/0000.parquet` sur `refs/convert/parquet`, 197 Mo ;
  - `AgentPublic/data-gouv-datasets-catalog` : `data/data-gouv-datasets-catalog-latest/*.parquet`, 3 fichiers, 467 Mo ;
  - `AgentPublic/legi` : `data/legi-latest/legi_<code>/*.parquet`, un dossier par code (CRPA 4 Mo, CASF 65 Mo, CGCT 111 Mo, code civil 33 Mo, commande publique 15 Mo) ;
  - `AgentPublic/sp_questions_corpus` : `gpt_corpus-20kq&A.xlsx`, 56 Mo ;
  - `AgentPublic/assistant_ia_questions_corpus` : `evaluation_qo_assistant_ia_v1.xlsx`.
- Le dossier `data/raw/` est ignoré par git (`.gitignore`).

## Tasks & Acceptance

**Execution:**
- `eval/outils/construire_jeu.py` -- créer le script :
  - en-tête PEP 723 ;
  - constantes : cibles de SPEC §2, thèmes, codes, hôtes ;
  - client `telecharger()`, avec contrôle d'hôte par saut et reprises ;
  - `cmd_sources` : révision HF épinglée, sélection `--quoi`, `--legi-codes`, `--page URL` pour une page d'un hôte de la Liste blanche ; met à jour INDEX ;
  - `cmd_fiche` : parquet local via duckdb, repli sur `hf/sp_<id>.json` ;
  - `cmd_assembler` ;
  - `cmd_composition` ;
  - `cmd_rejets`.
- `eval/construction/v1.0/README.md` -- créer le dossier des brouillons. Ce fichier documente le format des brouillons et de `verification/<CODE>.jsonl` (`id`, `verdict` ∈ {`accepte`, `rejete`}, `motif` ∈ {`fait_absent_source`, `url_morte_ou_differente`, `ambigu`, `doublon_thematique`, `autre`}, `detail`, `verifie_le`).
- `eval/construction/v1.0/verification/.gitkeep` -- réserver le dossier des vérifications.
- `tests/eval_outils/test_construire_jeu.py` -- tester la matrice ci-dessus. L'outil est importé par son chemin (`importlib`). Le réseau est remplacé par un faux ouvreur, et tout vrai réseau est interdit par monkeypatch. Un test AST contrôle les imports.
- Exécution réelle de `sources` vers `<dépôt principal>/data/raw/eval-sources/` (non versionné).

**Acceptance Criteria:**
- Given l'outil, when on inspecte ses imports (AST), then aucun module `slmsp`, ni aucun autre module du projet, n'est importé ; et une requête vers un hôte hors liste lève `HoteRefuse` sans ouvrir de connexion.
- Given `sources` lancé sur le dépôt principal, when il se termine, then les parquet et xlsx sont présents sous `data/raw/eval-sources/` et `INDEX.json` liste chaque fichier avec son URL, sa date de consultation et son SHA-256.
- Given des brouillons, when on lance `assembler --version v1.0`, then `eval/jeu/v1.0/items.jsonl` est trié par identifiant ; un doublon fait échouer l'assemblage.
- Given `composition` et `rejets`, when on les lance, then ils affichent en Markdown les écarts avec SPEC §2 et les taux de rejet.

## Design Notes

- **Pourquoi télécharger des fichiers entiers.** duckdb `httpfs` ouvrirait ses propres connexions, sans contrôle d'hôte. Des fichiers entiers épinglés par révision (`resolve/<sha>/<chemin>`) sont aussi de vrais instantanés, rejouables.
- **Tri.** Le tri est naturel : préfixe de code, puis numéro entier. `RD-010` vient donc après `RD-009`.
- **Thèmes.** Ce sont des slugs SPEC : `social-autonomie`, `etat-civil-papiers`, `travail-emploi`, `collectivites`, `famille-education-sante`, `fiscalite-locale`. Ils sont comptés sur Q, RD, LC et RE.
- **Producteurs RD.** On lit `producteurs` (liste), sinon `producteur`, sinon `reponse_reference.jeu_principal.producteur`.

## Verification

**Commands:**
- `uv run --no-project --python 3.12 --with pytest --with duckdb pytest tests/eval_outils -q` -- expected: tous verts, sans réseau.
- `uvx ruff check eval/outils tests/eval_outils` -- expected: aucun écart.
- `uv run --no-project --python 3.12 --with duckdb --with openpyxl python -I eval/outils/construire_jeu.py fiche F1344 --dest <dépôt principal>/data/raw/eval-sources` -- expected: texte de la fiche.

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts : 55 constats ; high 0, medium 26, low 23, false 6, maybe-false 0
- constats :
  - **Blind Hunter (14)**
    - `medium` `patch` Un verdict inconnu écrase un `rejete`. Corrigé : `derniers_verdicts` ignore et signale ces lignes.
    - `medium` `patch` Des `id` de verdict ne correspondent à aucun brouillon. Corrigé : listés par `assembler` et `composition`.
    - `medium` `patch` Des items jamais vérifiés sont assemblés en silence. Corrigé : ils sont listés, avec leur nombre et leurs identifiants.
    - `false` `reject` `assembler` ne contrôle pas la structure. Ce contrôle relève de `slmsp eval gel --verifier-seulement` (AD-11, D-nuit-A2-2) ; `composition` fait le contrôle de structure.
    - `medium` `patch` Une ligne de vérification illisible ne bloque pas l'assemblage. Corrigé : l'assemblage est refusé et rien n'est écrit.
    - `medium` `patch` Une entrée INDEX peut attester une révision qui ne correspond pas au fichier présent. Corrigé : contrôle de la taille et du SHA, révision reprise de l'entrée existante, refus des collisions de pages.
    - `medium` `patch` `--force` écrasait l'instantané précédent (D1.7). Corrigé : l'ancien fichier est archivé en `.ancien-<sha12>` et son entrée INDEX est conservée.
    - `low` `patch` Un BOM UTF-8 rend la ligne 1 illisible. Corrigé : lecture en `utf-8-sig`.
    - `low` `reject` `composition` sort toujours en 0. C'est un rapport, pas une porte : la porte est `eval gel`. Le correctif ajouterait une option pour un usage peu probable.
    - `medium` `patch` Contrôle CO incomplet (bool ou valeurs négatives, chevauchements, liste vide, cohérence avec `texte_corrige_reference`). Corrigé.
    - `low` `patch` Champs non contrôlés (`version_item`, date ISO de `consulte_le`, booléen `sans_reponse`, `amorce_reelle` par sous-chaîne). Corrigé. Les hôtes de `provenance[].url` ne sont pas restreints : Hugging Face est une provenance légitime.
    - `low` `patch` `fiche` : repli non documenté et erreur duckdb affichée en traceback brut. Corrigé : erreur encapsulée et README complété.
    - `low` `patch` README incomplet. Corrigé : options et comportements documentés.
    - `medium` `patch` Tests manquants (verdict inconnu, `Retry-After`, `--force`, BOM, etc.). Ajoutés : 100 tests.
  - **Edge Case Hunter (22)**
    - `low` `patch` `RE_ID` accepte un `\n` final et des chiffres Unicode. Corrigé : `fullmatch` avec `[0-9]`.
    - `low` `patch` `Q-001` et `Q-0001` ne sont pas vus comme doublons. Corrigé : doublon détecté sur (code, entier).
    - `medium` `patch` Verdict inconnu, même cause que le constat BH correspondant. Corrigé.
    - `medium` `patch` Items sans verdict, même cause que le constat BH correspondant. Corrigé.
    - `low` `patch` Tous les items rejetés produisent un `items.jsonl` vide. Corrigé : l'assemblage est refusé.
    - `low` `reject` `id` non hachable : cas improbable, le correctif ajouterait une garde.
    - `low` `reject` `difficulte` ou `theme` en liste : cas improbable, le correctif ajouterait une garde.
    - `low` `reject` `sources_attendues` en chaîne : cas improbable, le correctif ajouterait une garde.
    - `medium` `patch` Positions CO négatives ou booléennes, même cause que le constat BH correspondant. Corrigé.
    - `low` `patch` Chemin `..` dans l'arbre HF. Corrigé : une cible hors de `--dest` est refusée.
    - `medium` `patch` Fichier présent non vérifié, même cause que le constat BH correspondant. Corrigé.
    - `low` `patch` Le rapport affiche la mauvaise révision, même cause que le constat BH correspondant. Corrigé.
    - `low` `patch` Collision de chemins de pages, même cause que le constat BH correspondant. Corrigé.
    - `low` `patch` JSON invalide (HF, INDEX) affiché en traceback brut. Corrigé : `ErreurOutil`.
    - `low` `patch` Lien `rel="next"` relatif. Corrigé : `urljoin`.
    - `low` `patch` `fiche` plante sur un titre ou une URL NULL. Corrigé.
    - `low` `reject` Lignes `sp_*.json` incomplètes : ce sont les fichiers existants du calibrage, déjà valides.
    - `medium` `patch` Les variables de proxy contournent la liste d'hôtes. Corrigé : `ProxyHandler({})`.
    - `false` `reject` Réponse 3xx sans en-têtes : les réponses urllib ont toujours un objet `headers`.
    - `low` `patch` `rejets` produit une table mal formée quand aucun verdict n'est valide. Corrigé : message « Aucun verdict valide. ».
    - `low` `patch` Assertion « doublon » (`Q-0001`), même cause qu'un constat précédent. Corrigé.
    - `medium` `patch` Assertion « épinglé sur la révision », même cause que le constat BH correspondant. Corrigé.
  - **Intent Alignment (10)**
    - `medium` `defer` Instantanés réels incomplets : le réseau est interdit jusqu'à 08h30 par consigne d'Anaël. Voir `deferred`.
    - `medium` `patch` `fiche` non démontrée sur les données réelles. Vérifié : `fiche F1344` lit le parquet réel.
    - `false` `reject` Destination `data/raw` au lieu de `var/`. L'orchestrateur et l'AC2 de la story désignent explicitement `data/raw/eval-sources/`.
    - `medium` `patch` `parametres` non exigé. Corrigé : ajouté aux champs communs.
    - `medium` `patch` `regles` RD non contrôlé. Corrigé.
    - `low` `reject` Hôte `www.service-public.gouv.fr` imposé aux Q. Les fiches `entreprendre.service-public.gouv.fr` sont légitimes (RS-002 du calibrage) ; le contrôle reste sur la Liste blanche.
    - `low` `reject` Partage moitié-moitié des NR non rapporté : la SPEC ne définit aucun champ de sous-type.
    - `false` `reject` Champs exigés au-delà de SPEC §3 : ils viennent des AC des stories 7.4 et 7.5.
    - `false` `reject` Définitions laissées ouvertes : choix documentés dans la section Auto Run Result, sans effet indésirable.
    - `false` `reject` Absence de `pyproject` : ruff applique la configuration du dépôt principal (line-length 100, TID251). Conformité vérifiée.
  - **Verification Gap (9)**
    - `medium` `patch` Ouvreur réel et redirections 3xx. Test ajouté : cinq codes.
    - `medium` `patch` Statut 429 et `Retry-After`. Test ajouté.
    - `medium` `patch` SHA-256 inattendu. Test ajouté.
    - `medium` `patch` `--force` dans `sources` et `assembler`. Tests ajoutés.
    - `medium` `patch` `composition` exclut les rejetés. Test ajouté.
    - `medium` `patch` Lignes RD et CR de `composition`, ordre des producteurs. Tests ajoutés.
    - `medium` `patch` Branches de `anomalies_item`. Test paramétré ajouté.
    - `medium` `patch` Garde `--version`. Test ajouté.
    - `low` `reject` Pagination `Link`. Les dossiers visés comptent quelques fichiers, très en dessous de la taille de page HF ; le `urljoin` est corrigé.

## Auto Run Result

Implémenté par le sous-agent de story le 2026-10-12 (commit `feat(eval): outil de construction du jeu et instantanés des sources (story 7.1)`).

Décisions prises seul (règle « la plus simple et la plus réversible ») :
- **Disposition des instantanés** : `<dest>/hf/<propriétaire>/<dépôt>/<chemin dans le dépôt>` (ex. `hf/AgentPublic/service-public/latest/train/0000.parquet`) ; pages de la Liste blanche sous `<dest>/pages/<hôte>/<chemin>.html`. Les fichiers du calibrage (`hf/*.json`, `*.xlsx`, `sp_index.csv`) ne sont ni lus ni modifiés par `sources`.
- **Intégrité** : la taille et le SHA-256 LFS annoncés par la tree API sont vérifiés avant le renommage du `.part` ; en cas d'écart, le `.part` est conservé (rien n'est supprimé) et la commande échoue.
- **Fichier présent sans entrée INDEX** : entrée ajoutée avec le SHA-256 local, `consulte_le` = date de modification du fichier et une `note` l'expliquant.
- **`url_finale`** n'est consignée que pour les pages (les URL signées des CDN HF ne le sont pas).
- **`--page`** n'accepte que les hôtes de la Liste blanche (addendum §B), pas Hugging Face. Sans `--quoi`, `--page` seul ne télécharge que les pages.
- **`--legi-codes`** : alias `crpa`, `casf`, `cgct`, `civil`, `ccp` (défaut : les cinq) ou nom de dossier LEGI brut (`code_du_travail`).
- **Tri d'assemblage** : préfixe de code par ordre alphabétique (CO, CR, CT, LC, NR, Q, RD, RE), puis numéro entier.
- **Dernier verdict** : la dernière ligne de `verification/<CODE>.jsonl` l'emporte (ordre du fichier, pas `verifie_le`).
- **Garde de gel** : `assembler` refuse d'écraser `eval/jeu/<version>/items.jsonl` si `MANIFEST.json` existe (`--force` pour passer outre).
- **Taux de rejet** = verdicts `rejete` / verdicts, par Tâche ; un motif inconnu est signalé et compté en `autre`.
- **Amorce réelle (Q)** = `amorce_usager` non vide et une provenance citant `sp_questions_corpus` ou `assistant_ia_questions_corpus`.
- **Libellé NR** : « Non-régression » (calibrage) et « Non-régression générale » (SPEC §2) acceptés.
- `openpyxl` est déclaré dans l'en-tête PEP 723 comme demandé, mais n'est pas utilisé en 7.1.
- Après la revue, `--force` archive l'ancien instantané (`<nom>.ancien-<sha12><suffixe>`, entrée INDEX conservée) au lieu de l'écraser (D1.7). Un verdict inconnu bloque l'assemblage.

État de l'exécution réelle de `sources` (partielle, arrêtée par l'orchestrateur : réseau coupé jusqu'à 08h30) :
- Présents et indexés, avec taille et SHA-256 revérifiés hors ligne : service-public `0000.parquet` (rév. `29f236f8a5`), les 3 parquet du catalogue data.gouv (rév. `11f3d3c948`), LEGI CRPA et CASF (rév. `68b01fbbe0`).
- Manquants : LEGI CGCT (`.part` de 100 Mo laissé en place), code civil et commande publique, puis les deux xlsx de questions. Pour les obtenir, relancer `sources --dest <dépôt principal>/data/raw/eval-sources` : les fichiers déjà présents ne sont pas retéléchargés.
- `fiche F1344` sur le dépôt principal : OK, lu depuis le parquet.

### Finalisation (revue du 2026-10-12)

- **Changement** : outil autonome `eval/outils/construire_jeu.py` avec cinq sous-commandes : `sources`, `fiche`, `assembler`, `composition` et `rejets`. Le client HTTP est en lecture seule et vérifie l'hôte à chaque saut. Les instantanés sont épinglés par révision et inventoriés dans `INDEX.json`.
- **Fichiers** :
  - `eval/outils/construire_jeu.py` : l'outil.
  - `eval/construction/v1.0/README.md` : formats des brouillons et des vérifications, options.
  - `eval/construction/v1.0/verification/.gitkeep` : dossier des vérifications.
  - `tests/eval_outils/test_construire_jeu.py` : 100 tests, sans réseau.
- **Revue** : 55 constats.
  - Correctifs : 41 constats corrigés en un passage (commit `8107268`), puis mise en conformité ruff avec la configuration du dépôt (format, E501, B905, TID251 dans les tests).
  - Reportés : 1 (instantanés réels restants, réseau interdit).
  - Rejetés : 13, motifs dans le journal de triage.
- **Revue de suivi recommandée** : `true`. 20 constats medium corrigés et aucun high. Le lot de correctifs (environ 700 lignes) n'a pas été relu par une seconde revue, en particulier l'archivage `--force` et la vérification CO par application des corrections.
- **Vérifications** (toutes hors ligne) :
  - `uv run --offline --no-project --python 3.12 --with pytest --with duckdb pytest tests/eval_outils -q` → 100 passed.
  - `uvx --offline ruff format --check` → ok.
  - `ruff check` → ok, avec la configuration du dépôt principal. La seule exception, TID251 sur `eval/outils/**`, est déjà exclue par `pyproject.toml` ; elle n'apparaît dans le worktree qu'à cause du chemin.
  - `fiche F1344` sur le dépôt principal → ok, lu depuis le parquet.
- **Risques résiduels** :
  - Instantanés incomplets : LEGI CGCT, code civil, commande publique, et les deux xlsx de questions.
  - Après fusion avec la story 1.1, `uv run pytest` collectera ces tests ; si duckdb manque dans l'environnement du projet, le test parquet est ignoré.
