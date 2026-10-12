---
title: 'Story 2.3 : Index local — construction, recherche exacte et mesure H-VEC'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '22807566f322de53e4fbf7b045b354e3e30a7d86'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** Aucun Index local n'existe : le Harnais (4.2, 4.5) et la validation des données (9.5) n'ont aucun passage officiel à citer, et l'hypothèse H-VEC (p95 ≤ 300 ms, ≤ 350 Mo résidents) n'est pas mesurée.

**Approach:** `slmsp.indexation.construction` lit les parquet MediaTech (service-public + catalogue data.gouv, D4) et écrit `index/<AAAAMMJJ>/` (`vectors.f16.npy`, `chunks.sqlite`, `MANIFEST.json`) ; `slmsp.index.lecture.IndexLocal` implémente `VectorStore` par produit scalaire exact par blocs sur `numpy.memmap` ; `slmsp.indexation.mesure_vec` mesure latence et RAM dans un run `runs/measure/` ; `slmsp index {build, info, mesurer}` les expose.

## Boundaries & Constraints

**Always:**
- Format AD-9 exact : `vectors.f16.npy` N × 1024 float16 normalisé L2 (renormalisé en float32 puis converti) ; `chunks.sqlite` table `chunks(rang INTEGER PRIMARY KEY, chunk_id, doc_id, source, titre, url, texte, date_snapshot)`, `rang` = indice du vecteur (0-based) ; `MANIFEST.json` validé par `ManifesteIndex` (SHA-256 des deux fichiers, `date_snapshot`, modèle d'embedding, chunks par source, SHA des parquet lus).
- Vecteurs lus depuis la colonne JSON `embeddings_bge-m3`, jamais recalculés. Parquet trouvés sous `<racine>/data/raw/mediatech/<jeu>/<revision>/*.parquet` (ordre des noms), lus par lots `pyarrow` (import paresseux, extra `data`).
- Version = date de snapshot la plus récente des sources (`config/index.toml`, dates des révisions HF épinglées) au format `AAAAMMJJ`. Chaque chunk porte la date de sa source (`AAAA-MM-JJ`).
- Construction dans `index/.<version>.en-cours-<4 hex>/` puis `os.rename` vers `index/<version>/` ; refus (`ArtefactExistant`) si `index/<version>/` existe, avant toute lecture. Espace libre vérifié (`verifier_espace`) avant écriture.
- `config/index.toml` (lu par `slmsp.index.config.charger_config_index`) : `taille_bloc`, `k`, `seuil_pertinence`, sources v1 et colonnes, paramètres et seuils de mesure. Toujours lu depuis `racine_projet()/config`, même avec `--racine`.
- `rechercher(vecteur, k)` : résultats triés par score décroissant puis rang croissant (départage déterministe), égaux à la référence numpy float32 `(vecs.astype(float32) @ q)` ; `Passage` rempli depuis `chunks.sqlite` (lecture seule, `mode=ro&immutable=1`).
- Mesure H-VEC : graine et nombre de requêtes de la config (200, 42), requêtes = vecteurs du corpus tirés sans remise ; RSS (`psutil`) avant ouverture de l'index et après les requêtes ; résultat `ResultatMesure` écrit en `resultat.json` d'un run `measure` (slug `h-vec`, `index_version`) puis `terminer("complet")`. Verdict `confirmee` si p95 ≤ seuil et RAM ajoutée ≤ seuil, sinon `infirmee` avec `repli` = « index usearch HNSW i8 en vue mappée, dérivé du même .npy, derrière VectorStore : à faire ».

**Never:** `slmsp.index` n'importe ni `pyarrow` ni `duckdb` (fermeture runtime) ; aucune bibliothèque vectorielle (usearch, faiss) ; aucun recalcul d'embedding ; aucune suppression ni réécriture d'un index ou d'un run ; aucun téléchargement ; aucune modification hors zone (`indexation/{construction,mesure_vec}.py`, `index/`, `core/schemas/{manifeste_index,mesure}.py`, `cli/index.py`, `config/index.toml`, leurs tests).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Build nominal | parquet des 2 sources | `index/<v>/` complet, N = somme des lignes valides | — |
| Version existante | `index/<v>/` présent | rien n'est lu ni écrit | `ArtefactExistant` (code 1) |
| Parquet absent | dossier `<jeu>/<revision>/` vide ou manquant | aucun dossier final | `ConfigurationInvalide` citant le chemin |
| Vecteur invalide | JSON nul, illisible, dimension ≠ 1024, norme nulle ou non finie | ligne écartée, comptée dans `ecartes` de la source | — |
| Recherche | `k` > N | N résultats | — |
| Recherche invalide | `k` ≤ 0, dimension ≠ 1024, valeur non finie | — | `ValueError` |
| Index absent | aucune version sous `index/` ou version demandée inconnue | — | `ManifesteInvalide` |
| Index incohérent | forme/dtype du `.npy` ≠ manifeste, lignes sqlite ≠ N | — | `ManifesteInvalide` |
| `info --verifier` | fichier modifié | — | `ManifesteInvalide` (SHA) |

</intent-contract>

## Code Map

- `src/slmsp/core/ports.py` -- `Passage(chunk_id, doc_id, source, titre, url, texte, date_snapshot, score)`, `VectorStore.rechercher(vecteur, k) -> list[Passage]` : à implémenter, ne pas modifier.
- `src/slmsp/core/schemas/__init__.py` -- `SchemaBase` (`extra="forbid"`, `schema_version`), `SousSchema`, `Sha256`.
- `src/slmsp/core/config.py` -- `ModeleConfig`, `charger_toml(chemin, Modele)`, `racine_projet()`.
- `src/slmsp/core/artefacts.py` -- `nouveau_run(type, slug, config, entrees=, graine=, racine=, index_version=...)`, `Run.ecrire(nom, contenu)` (création exclusive), `Run.terminer(statut)`, `ArtefactExistant`, `verifier_espace(chemin, octets)`.
- `src/slmsp/core/canonique.py` -- `json_canonique`, `sha256_fichier`.
- `src/slmsp/core/erreurs.py` -- `ConfigurationInvalide`, `ManifesteInvalide`, `SlmspError` (code de sortie porté par l'exception).
- `src/slmsp/cli/__init__.py` -- registre : `slmsp.cli.index.enregistrer(sous_parseurs)` ; `index` déjà déclaré dans `SOUS_COMMANDES`. Le module CLI ne doit pas importer pyarrow au chargement (sinon `index info` devient « indisponible »).
- `src/slmsp/cli/fetch.py` -- modèle de sous-commandes avec `--racine`.
- `tests/test_architecture.py` -- `index` couche 2 runtime, `indexation` couche 4 ; `pyarrow`/`duckdb` interdits dans la fermeture runtime (AC4 déjà vérifié par la règle `lourd-runtime`).
- `config/sources.toml` -- jeux `service-public` (révision `7ddda096b33d48dbda8143fc8c349a8b0e031a3a`) et `data-gouv-datasets-catalog` (`11f3d3c9481ad478dbcff52e85d73b7fd10533ce`) ; non importable depuis `indexation` (même couche que `fetch`).
- Relevés réels (2026-10-12) : service-public 35 758 lignes (1 fichier), catalogue 3 fichiers (≈ 107 679 lignes). Colonnes communes : `chunk_id`, `doc_id`, `title`, `url`, `chunk_text`, `embeddings_bge-m3` (chaîne JSON de 1024 flottants). Pas de colonne `source` dans le catalogue. Dates des révisions HF (`lastModified`) : service-public 2026-09-25, catalogue 2026-09-26 → version `20260926`.
- Fichiers lourds (dépôt principal) : `data/raw/mediatech/...` ; la construction et la mesure réelles tournent avec `--racine C:\Users\Utilisateur\Documents\GitHub\service-public-slm-fine-tuning`.

## Tasks & Acceptance

**Execution:**
- `config/index.toml` -- `schema_version`, `modele_embedding = "BAAI/bge-m3"`, `colonne_vecteurs`, `dimension = 1024`, `taille_bloc = 4096`, `k = 5`, `seuil_pertinence = 0.5`, `taille_lot_lecture`, `[[sources]]` (nom, jeu, revision, date_snapshot, colonnes), `[mesure]` (requetes 200, graine 42, k 10, seuil_p95_ms 300, seuil_ram_mo 350).
- `src/slmsp/index/config.py` -- `ConfigIndex`, `SourceIndex`, `ConfigMesureVec`, `charger_config_index(chemin=None)`, `dossier_index(racine)`, noms de fichiers, `MOTIF_VERSION`.
- `src/slmsp/core/schemas/manifeste_index.py` -- `ManifesteIndex` (`version`, `date_snapshot`, `cree_le`, `modele_embedding`, `colonne_vecteurs`, `dimension`, `dtype="float16"`, `nb_chunks`, `sources: list[SourceManifeste(nom, jeu, revision, date_snapshot, nb_chunks, nb_ecartes, parquet: dict[nom, Sha256])]`, `fichiers: dict[nom, Sha256]`), méthode `chunks_par_source()`.
- `src/slmsp/core/schemas/mesure.py` -- `ResultatMesure` v1 (`mesure`, `hypothese`, `run_id`, `mesure_le`, `index_version`, `parametres`, `valeurs`, `seuils`, `verdict` ∈ {confirmee, infirmee, sans-objet}, `repli`, `details`).
- `src/slmsp/indexation/construction.py` -- `SourceLue`, `lire_source_parquet(source, racine, config)` (pyarrow paresseux), `vecteur_depuis_json`, `ecrire_index(dossier_index, version, sources_lues, config)`, `construire_index(config, racine)`.
- `src/slmsp/index/lecture.py` -- `IndexLocal(dossier)` (`manifeste`, `version`, `date_snapshot`, `nb_chunks`, `rechercher`, `verifier()`, `fermer()`, contexte `with`), `versions_disponibles(racine)`, `ouvrir_index(racine=None, version=None)`.
- `src/slmsp/indexation/mesure_vec.py` -- `mesurer_h_vec(racine, version, config, *, rss=...) -> ResultatMesure`, percentiles, verdict, run `measure`.
- `src/slmsp/cli/index.py` -- `index build|info|mesurer` avec `--racine`, `--version` (info, mesurer), `--verifier` (info).
- `tests/indexation/test_construction.py`, `tests/index/test_lecture.py`, `tests/indexation/test_mesure_vec.py` (+ `tests/index/conftest.py` fabrique d'index factice par `ecrire_index`, vecteurs aléatoires) -- matrice ci-dessus, CLI par `slmsp.cli.main`, tests réels marqués `lent`.

**Acceptance Criteria:**
- Given des parquet minuscules sous `<tmp>/data/raw/mediatech/`, when `slmsp index build --racine <tmp>`, then `index/<v>/` contient les trois fichiers conformes, ligne `i` ↔ vecteur `i`, comptes par source exacts ; when relancé, then refus sans écriture.
- Given un index de fixture, when `rechercher(q, k)`, then indices et scores égaux à la référence numpy float32 (force brute) pour plusieurs `k` et tailles de bloc.
- Given un index, when `slmsp index info`, then version, date du snapshot et comptes par source s'affichent.
- Given un index, when `slmsp index mesurer`, then `runs/measure/<run_id>/` contient `run.json` (`index_version`) et `resultat.json` (p50, p95, RAM ajoutée, verdict H-VEC, repli si infirmée).
- Given l'index v1 réel, when `index build` puis `index mesurer` réels, then les mesures sont consignées dans `## Auto Run Result`.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 37 findings — high 0, medium 3, low 28, false 6, maybe-false 0
- findings:
  - `[low]` `[reject]` (BH) champs texte nuls stockés en `""` sans écarter la ligne — vérifié sur l'index réel : 0 `chunk_id`, `doc_id`, `titre`, `url` ou `texte` vide sur 143 437 lignes ; corpus épinglé, garde supplémentaire sans cas réel.
  - `[low]` `[reject]` (BH) unicité de `chunk_id` non vérifiée, pas d'index SQL sur `chunk_id` — 0 doublon sur l'index réel (requête `GROUP BY chunk_id`) ; aucun consommateur ne cherche encore par `chunk_id`.
  - `[false]` `[reject]` (BH) `os.rename` sous POSIX remplace un dossier vide — projet Windows seul (D2) : `os.rename` y lève `FileExistsError`, traduit en `ArtefactExistant` (test `test_rename_concurrent_laisse_le_dossier_en_cours`).
  - `[low]` `[reject]` (BH) construction échouée : dossier `.en-cours-` laissé sans message — cas rare (espace vérifié avant écriture) ; le dossier est inoffensif et ignoré par `versions_disponibles`.
  - `[medium]` `[patch]` (BH) `index.toml` et `sources.toml` peuvent diverger sans alerte — groupé avec VG1 : test `test_sources_index_alignees_sur_sources_toml` (nom, révision, disposition `data/raw/mediatech/<jeu>/<revision>`).
  - `[low]` `[reject]` (BH) manifeste sans empreinte d'environnement — AD-9 fixe le contenu du manifeste (SHA, snapshot, modèle, comptes) ; la provenance des runs reste dans `run.json`.
  - `[low]` `[reject]` (BH) `passages()` dépasse `SQLITE_MAX_VARIABLE_NUMBER` pour `k` > 32 766 — `k` vaut 5 (Harnais) ou 10 (mesure) ; une découpe par lots ajoute une boucle pour un cas hors usage.
  - `[low]` `[patch]` (BH) tampon partagé `self._tampon` et `check_same_thread=False` : recherches concurrentes corrompues — tampon alloué à chaque appel de `classer` (16 Mo, négligeable devant la latence).
  - `[low]` `[reject]` (BH) logique dupliquée (`_version`, `racine_reelle`, motif `AAAAMMJJ`, contrôle des homonymes) — pas de divergence nommée ; refactorisation sans effet observable.
  - `[low]` `[reject]` (BH) tests liés à la config de production (`VERSION = "20260926"`) — changer le snapshot impose de toute façon une revue de l'index ; une config de test dédiée est un chantier hors de la correction directe.
  - `[low]` `[patch]` (BH) `seuil_pertinence` sans bornes — `Field(ge=-1.0, le=1.0)` et test `test_config_seuil_pertinence_borne` ; « inutilisés » : faux, lus par le Harnais (4.2) selon le journal (source unique).
  - `[low]` `[reject]` (BH) `index mesurer` sort en 0 même si H-VEC est infirmée — le code 0 signifie « mesure faite » ; le verdict est affiché et écrit dans `resultat.json`.
  - `[low]` `[reject]` (BH) construction tout en mémoire, `ParquetFile` non fermés, contrôle des types élément par élément — construction réelle en 45 s, sans erreur ; processus court, fichiers libérés à sa fin.
  - `[low]` `[reject]` (BH) `verifier()` ignore les fichiers en trop, `parquet` peut être vide, NaN d'un `.npy` altéré — index produit par le seul `index build` ; altération manuelle hors usage.
  - `[low]` `[reject]` (EC) `IN (?,…)` au-delà de la limite SQLite — même motif que BH.
  - `[low]` `[reject]` (EC) colonnes manquantes dans `chunks` → `sqlite3.Error` brute — base écrite par `index build` seul.
  - `[low]` `[reject]` (EC) rang hors bornes passé à `passages()` signalé comme index corrompu — appel interne à `rechercher` ; API publique non utilisée ailleurs.
  - `[low]` `[reject]` (EC) `.npy` qui serait un `.npz` → `AttributeError` — fichier écrit par `index build` seul.
  - `[low]` `[patch]` (EC) tampon partagé entre fils — même correctif que BH.
  - `[low]` `[reject]` (EC) dossier `AAAAMMJJ` le plus récent vide ou invalide — `index build` ne crée le dossier final que par `os.rename` d'un dossier complet.
  - `[low]` `[reject]` (EC) source entière écartée silencieusement — `nb_ecartes` figure au manifeste et à `index info` ; 0 écarté sur l'index réel.
  - `[false]` `[reject]` (EC) colonne vecteur en `list<float>` natif — schéma relevé : `embeddings_bge-m3: string` dans les deux jeux épinglés.
  - `[false]` `[reject]` (EC) colonnes texte binaires → `"b'…'"` — schéma relevé : colonnes `string`.
  - `[low]` `[reject]` (EC) `chunk_id` nul, vide ou dupliqué — même vérification que BH (0 sur l'index réel).
  - `[low]` `[reject]` (EC) parquet corrompu → trace brute — parquet vérifiés par SHA au téléchargement (`fetch`) et hachés dans le manifeste.
  - `[false]` `[reject]` (EC) `os.rename` POSIX — même réfutation que BH (Windows seul).
  - `[low]` `[reject]` (EC) collision de `token_hex(2)` avec un dossier en cours laissé — probabilité 1/65 536 par dossier laissé ; relance suffisante.
  - `[low]` `[reject]` (EC) disque plein en cours d'écriture → `OSError` brute — espace vérifié avant écriture (`verifier_espace`, marge 2 Gio).
  - `[low]` `[reject]` (EC) `maintenant` naïf → erreur après écriture — paramètre interne utilisé par les tests seulement.
  - `[low]` `[reject]` (EC) `SystemExit` pendant la mesure → run laissé `en_cours` — aucun chemin de la mesure ne lève `SystemExit`.
  - `[low]` `[reject]` (EC) RSS après < RSS avant → RAM négative — valeur brute consignée telle quelle (pic en détail) ; non observé (297,7 Mio).
  - `[low]` `[reject]` (EC) scores non égaux au bit près à la référence — sommation BLAS dépendante du découpage (≤ 3e-8) ; rangs identiques testés, égalité au bit testée quand les sommes sont exactes, documenté dans `lecture.py`.
  - `[medium]` `[patch]` (VG) alignement `index.toml` / `sources.toml` non testé — test ajouté (voir BH).
  - `[medium]` `[patch]` (VG) validateurs de schéma jamais exercés — tests `test_resultat_infirme_sans_repli_refuse`, `test_manifeste_version_differente_de_la_date_refusee`, `test_manifeste_sources_homonymes_refusees`, `test_config_sources_homonymes_refusees`.
  - `[false]` `[reject]` (VG) `## Auto Run Result` absent — section écrite à la finalisation, avec les mesures réelles.
  - `[false]` `[reject]` (IA) verdict H-VEC réel non consigné — mesure réelle faite (runs `20261012-104817-h-vec-c4eb` puis seconde mesure), consignée ci-dessous ; le report au journal revient à l'orchestrateur (consignes).
  - `[low]` `[reject]` (IA) égalité des scores à l'arrondi float32 près plutôt qu'au bit — même motif que EC.

## Design Notes

- Top-k exact et déterministe par bloc : `seuil = partition(-scores, k-1)[k-1]`, candidats `scores >= -seuil` (ex-aequo inclus), fusion puis `lexsort((rangs, -scores))[:k]`. Tampon float32 de `taille_bloc × 1024` (`np.copyto`) alloué à chaque appel, pour limiter la RAM (4096 → 16 Mo) et permettre des recherches concurrentes.
- Les vecteurs sont accumulés en float16 en mémoire (≈ 294 Mo pour 143 k) puis écrits (en-tête `.npy` puis octets de chaque source) dans un fichier ouvert en `"xb"`.
- RAM ajoutée = RSS après les 200 requêtes − RSS avant ouverture ; les vecteurs de requête sont copiés depuis un memmap fermé avant la mesure de référence. Pic (`peak_wset`) consigné en détail.

## Verification

**Commands:**
- `uv run --extra data pytest tests/indexation tests/index tests/test_architecture.py` -- expected: tout passe.
- `uv run --extra data pytest` puis `uv run ruff check` et `uv run ruff format --check` -- expected: aucun nouvel échec.
- `uv run --extra data slmsp index build --racine <principal>` puis `uv run slmsp index info --racine <principal> --verifier` et `uv run slmsp index mesurer --racine <principal>` (en arrière-plan) -- expected: index `20260926`, mesure consignée.

## Auto Run Result

Status: done
Blocking condition: aucune

**Résumé.** Index local v1 (AD-9, D3, D4) :
- `slmsp index build` lit les parquet MediaTech (service-public et catalogue data.gouv) et écrit `index/<AAAAMMJJ>/` : `vectors.f16.npy`, `chunks.sqlite` et `MANIFEST.json`. La construction passe par un dossier `.en-cours-` puis un renommage, et refuse une version existante.
- `IndexLocal` implémente `VectorStore` : recherche exacte par blocs sur `numpy.memmap`, départage déterministe des ex-aequo.
- `slmsp index info` affiche la version, la date du snapshot et les comptes ; `--verifier` contrôle les SHA-256.
- `slmsp index mesurer` mesure H-VEC dans `runs/measure/<run_id>/resultat.json` (`ResultatMesure` v1).

**Fichiers.**
- `config/index.toml` : sources v1 épinglées, avec la date de leur révision HF ; taille de bloc 4096, `k` 5, seuil 0,5 ; paramètres et seuils de la mesure.
- `src/slmsp/index/config.py` : `ConfigIndex`, chargeur, disposition `index/`.
- `src/slmsp/index/lecture.py` : `IndexLocal`, `ouvrir_index`, `versions_disponibles`, `lire_manifeste`.
- `src/slmsp/core/schemas/manifeste_index.py` : `ManifesteIndex` (cohérence version/date, comptes, sources).
- `src/slmsp/core/schemas/mesure.py` : `ResultatMesure` v1 ; un verdict `infirmee` porte son repli.
- `src/slmsp/indexation/construction.py` : lecture pyarrow paresseuse, vecteurs JSON renormalisés, écriture de l'index.
- `src/slmsp/indexation/mesure_vec.py` : protocole H-VEC, verdict et repli, run `measure`.
- `src/slmsp/cli/index.py` : `index build|info|mesurer`, option `--racine`.
- `tests/index/{conftest,test_lecture}.py`, `tests/indexation/{conftest,test_construction,test_mesure_vec}.py` : 185 tests hors `lent`, et 3 tests `lent` réels.

**Mesures réelles** (dépôt principal, `--racine`) :
- Construction en 45 s : `index/20260926/`, 143 437 chunks (35 758 service-public et 107 679 catalogue, 0 écarté).
  - `vectors.f16.npy` : 293 759 104 octets.
  - `chunks.sqlite` : 183 943 168 octets.
  - Total d'environ 457 Mo.
  - `index info --verifier` : SHA conformes.
- **H-VEC infirmée, de peu et sur la latence seule.** Deux mesures de 200 requêtes, graine 42, k = 10. Le CPU était chargé à environ 60 % par les stories parallèles.
  - Run `20261012-104817-h-vec-c4eb` : p50 275,6 ms, p95 314,3 ms, RAM ajoutée 297,7 Mio, pic du working set 378 Mio.
  - Run `20261012-105506-h-vec-e2a9` : p50 282,6 ms, p95 328,9 ms, RAM ajoutée 282,0 Mio.
  - La RAM tient (≤ 350 Mio), pas le p95 (> 300 ms).
  - Repli consigné **à faire, non implémenté** : index usearch HNSW i8 en vue mappée, dérivé du même `.npy`, derrière `VectorStore`.
  - Sur un poste au repos, le p95 pourrait passer sous le seuil. Une remesure à froid reste à faire avant de trancher le repli.
- Tests `lent` réels (`SLMSP_RACINE_REELLE`) : 3 passés en 102 s.

**Revue (1 passe, 4 couches).** 37 constats : 0 high, 3 medium, 28 low, 6 false.
- Patchs : 2 medium (test d'alignement `index.toml`/`sources.toml`, tests des validateurs de schéma) et 2 low (tampon alloué à chaque appel, bornes de `seuil_pertinence`).
- Aucun report (`deferred` vide). Les autres constats sont rejetés avec leur motif (triage ci-dessus).
- Relecture complémentaire non recommandée : les patchs medium n'ajoutent que des tests, sans risque non vérifié.

**Vérification** (2026-10-12) :
- `uv run --extra data pytest tests/indexation tests/index tests/test_architecture.py` : 185 passés.
- `uv run --extra data pytest` : 1 603 passés, 119 sautés.
- `ruff check` et `ruff format --check` : propres.

**Risques résiduels.**
- Les scores diffèrent de la référence force brute au dernier bit float32 près (≤ 3e-8, ordre de sommation BLAS). Les rangs sont identiques hors quasi ex-aequo.
- `passages()` échoue au-delà d'environ 32 000 résultats (limite des variables SQLite), hors usage.
- La mesure H-VEC est sensible à la charge du poste.

**Décisions prises seul** (à reporter au journal) :
1. Date de snapshot de chaque source = `lastModified` de la révision HF épinglée : service-public 2026-09-25, catalogue 2026-09-26. Version de l'index = la plus récente, `20260926`. Chaque chunk porte la date de sa source.
2. `texte` = colonne `chunk_text` (titre et contexte inclus, c'est le texte vectorisé) ; `source` = nom du jeu.
3. `k = 5` et `seuil_pertinence = 0,5` par défaut. Le seuil est appliqué par le Harnais, pas par `rechercher`.
4. Lignes au vecteur invalide écartées et comptées (`nb_ecartes`) ; champs texte nuls stockés en `""`.
5. Construction dans `index/.<v>.en-cours-<hex>/` puis `os.rename`. Un dossier interrompu reste en place et n'est jamais supprimé.
6. `index build` n'ouvre pas de run : l'index est lui-même l'artefact versionné, avec son manifeste. `index mesurer` ouvre un run `measure` au slug `h-vec`.
7. Mesure : la latence couvre le classement et la lecture sqlite, première requête comprise, sans échauffement. RAM ajoutée = RSS après − RSS avant ouverture, en Mio.
8. Égalité à la référence : rangs exacts ; scores au bit près seulement quand les sommes sont exactes, sinon à 1e-6 près.
9. `index mesurer` sort en 0 quel que soit le verdict.
