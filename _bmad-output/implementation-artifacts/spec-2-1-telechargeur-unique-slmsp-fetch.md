---
title: 'Story 2.1 : téléchargeur unique slmsp fetch (llama.cpp, corpus MediaTech, BGE-M3)'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '8c7ebcc8d630dfac5420f4f64e1e01ea0a3d7608'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred:
  - summary: >-
      La branche « copie au mauvais SHA » de la réutilisation (lien dur impossible) n'a pas de test.
    evidence: |-
      test_reutilisation_par_copie ne couvre que la copie conforme ; atteindre la branche exige une source modifiée entre l'indexation et la copie (rare).
    location: >-
      src/slmsp/fetch/hf.py (Telechargeur._reutiliser)
    severity: low
  - summary: >-
      Un GGUF d'un autre dépôt que depot_hf n'est épinglé que par son SHA ; à la relance (fichier présent) le run inscrit la révision « main ».
    evidence: |-
      FichierGguf (core/schemas/config_modele.py, story 1.3) n'a pas de champ revision ; modeles._gguf court-circuite la résolution du commit si la destination existe. Sans effet pour bge-m3 (même dépôt), à traiter par la story 8.1 (granite, ministral, smollm3, qwen).
    location: >-
      src/slmsp/fetch/modeles.py (_gguf)
    severity: medium
  - summary: >-
      Les fichiers HF de `fichiers` déclenchent un HEAD à chaque relance et les fichiers non LFS (config.json, tokenizer) sont refusés faute de SHA-256.
    evidence: |-
      modeles._fichier_hf ne teste pas la présence locale avant metadonnees_hf et exige X-Linked-Etag ; bge-m3 a `fichiers = []`, la story 8.1 devra fournir un SHA en config ou accepter l'OID git.
    location: >-
      src/slmsp/fetch/modeles.py (_fichier_hf)
    severity: low
  - summary: >-
      Un `.part` partiel de l'archive des sources (taille inconnue) bloque toute relance si codeload.github.com répond 200 à une requête Range.
    evidence: |-
      La matrice impose « 200 sur une reprise : erreur, .part gardé » ; non vérifié : le support de Range par codeload pour les archives générées. Si absent, il faut écarter le `.part` à la main (renommage).
    location: >-
      src/slmsp/fetch/hf.py (Telechargeur._transferer)
    severity: medium (unverified)
---

<intent-contract>

## Intent

**Problem:** Aucun téléchargement n'est encore reproductible : les binaires llama.cpp, le corpus MediaTech et le GGUF de BGE-M3 doivent arriver à des révisions épinglées, vérifiés par SHA-256, et uniquement par le profil réseau `outillage`.

**Approach:** Un moteur de téléchargement unique (`fetch/hf.py`) écrit dans `<fichier>.part`, reprend par `Range`, relance sur 429/5xx, vérifie le SHA-256 puis renomme. Trois pilotes (`llamacpp`, `sources`, `modeles`) l'alimentent depuis `config/`, et chaque exécution écrit un run `runs/fetch/<run_id>/` qui liste chaque fichier (dépôt, fichier, révision, octets, SHA).

## Boundaries & Constraints

**Always:**
- Tout client HTTP vient de `slmsp.net` : `net.fabrique_hf()` pour Hugging Face (token `HF_TOKEN` en `Authorization` seulement sur ce client, s'il est non vide), `net.client("outillage", follow_redirects=True)` pour GitHub (sans token). `huggingface_hub.set_client_factory(net.fabrique_hf)` est posé dès que le paquet est importable ; `HF_HOME=<models>/.cache-hf` et télémétrie coupée sont posés avant tout import de `huggingface_hub`.
- Révisions épinglées par commit (40 hex) ; SHA-256 attendu dans la config ou, pour un fichier LFS de HF sans SHA en config, celui du `X-Linked-Etag`.
- Aucun fichier n'est supprimé ni écrasé : fichier final présent avec le bon SHA = sauté ; présent avec un autre SHA = erreur ; `.part` repris ; `.part` complet au mauvais SHA renommé `<nom>.sha-invalide-<horodatage>` (jamais effacé) et erreur levée, fichier final non créé.
- Espace disque vérifié par `core.artefacts.verifier_espace` avant tout téléchargement dont le total dépasse le seuil de config (1 Go), et avant chaque extraction.
- Racine des écritures `vendor/`, `data/`, `runs/` = option `--racine` (défaut `racine_projet()`) ; poids sous `dossier_modeles()` (`SLMSP_MODELS_DIR`).
- Option `--reutiliser DOSSIER` (répétable) : un fichier local de même taille et de même SHA-256 est lié en dur (copie à défaut) au lieu d'être téléchargé ; statut `reutilise` au run.

**Never:**
- Lancer un binaire llama.cpp (AD-6, story 2.2), utiliser le datasets-server, `hf_hub_download`/`snapshot_download`, importer un client HTTP hors de `net`, toucher aux modèles candidats (story 8.1), faire un appel réseau dans les tests non marqués `reseau`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Nominal | fichier absent | `.part` écrit, SHA OK, renommé ; ligne `telecharge` au run | — |
| Idempotence | fichier final au bon SHA | aucune requête ; ligne `deja-present` | — |
| Reprise | `.part` de N octets | requête `Range: bytes=N-`, 206, ajout | 200 sur une reprise : erreur, `.part` gardé |
| Relance | 429 / 500-504 / erreur de transport | attente exponentielle (`Retry-After` respecté), reprise depuis la taille du `.part` | après `essais` : `TelechargementEchoue` |
| SHA faux | octets reçus ≠ SHA attendu | `.part` renommé `.sha-invalide-*`, pas de fichier final | `ShaInvalide` |
| Conflit | fichier final au mauvais SHA | rien n'est écrit | `ShaInvalide` |
| Hôte refusé | redirection hors règles `outillage` | rien n'est écrit | `HoteBloque` remonte |
| Zip hostile | membre absolu ou `..` | extraction refusée | `ArchiveInvalide` |
| Espace | total > seuil et disque plein | aucune requête de téléchargement | `EspaceInsuffisant` |

</intent-contract>

## Code Map

- `src/slmsp/net/client.py` -- `client(profil, transport_interne=..., journal=..., follow_redirects=...)`, `fabrique_hf(...)` : seuls clients permis ; `transport_interne` sert aux tests (`httpx2.MockTransport`).
- `config/reseau.toml` -- profil `outillage` : HF (suffixes `huggingface.co`, `hf.co`, couvre `cas-bridge.xethub.hf.co`), GitHub (`github.com`, `api.github.com`, `codeload.github.com`, `*.githubusercontent.com`) en GET/HEAD.
- `src/slmsp/core/schemas/config_llamacpp.py` -- `ConfigLlamacpp` (tag, depot, assets cpu/cuda/cudart, sources, binaires) : schéma imposé de `config/llamacpp.toml`.
- `src/slmsp/core/schemas/config_modele.py` -- `ConfigModele` (depot_hf, revision, fichiers, gguf{depot,fichier,sha256}, embedding, pooling, protocole_outils requis) : schéma de `config/modeles/<slug>.toml`. `FichierGguf` n'a pas de révision propre.
- `src/slmsp/core/config.py` -- `charger_toml`, `ModeleConfig`, `racine_projet`, `dossier_modeles`, `appliquer_environnement_impose`.
- `src/slmsp/core/secrets.py` -- `secret("HF_TOKEN")` (lève `SecretManquant` si vide : HF anonyme alors).
- `src/slmsp/core/artefacts.py` -- `nouveau_run(type, slug, config, racine=...)`, `Run.ajouter_jsonl`, `Run.terminer`, `verifier_espace`, `EspaceInsuffisant`.
- `src/slmsp/core/canonique.py` -- `sha256_fichier`.
- `src/slmsp/cli/__init__.py` -- contrat `enregistrer(sous_parseurs)` + `func(args) -> int` ; `SlmspError` converti en code de sortie.
- `tests/net/conftest.py` -- modèle de doublure `MockTransport` ; `tests/conftest.py` bloque le réseau et isole `SLMSP_VAR_DIR`.
- Valeurs relevées le 2026-10-12 par la passerelle : release `b11429` (commit `d81235049384534c167caea52b85a694f6103d14`) ; `llama-b11429-bin-win-cpu-x64.zip` 19 398 918 o `1283323272b04cd07905816a597a0da810918102de958f4ff6f7bbaa70ed2efe` ; `llama-b11429-bin-win-cuda-12.4-x64.zip` 264 478 423 o `dd6df685c1024e6aa55ca55ad35038692d5e284d4dc895e7a646c3245d3d14ff` ; `cudart-llama-bin-win-cuda-12.4-x64.zip` 391 443 627 o `8c79a9b226de4b3cacfd1f83d24f962d0773be79f1e7b75c6af4ded7e32ae1d6` ; sources `https://github.com/ggml-org/llama.cpp/archive/refs/tags/b11429.zip` 39 712 933 o `2c14039274aaf94ad0e4cbdeb575b32cc3d75c3b8bae28b052c9ff9c20ffea46` (racine `llama.cpp-b11429/`). `AgentPublic/service-public` @ `7ddda096b33d48dbda8143fc8c349a8b0e031a3a` : `data/service-public-latest/service_public_part_0.parquet` 196 640 948 o `e92ddb136dd1312f1b515124aea554646207fcb42112be8e6250196022a86d30`. `AgentPublic/data-gouv-datasets-catalog` @ `11f3d3c9481ad478dbcff52e85d73b7fd10533ce` : `data/data-gouv-datasets-catalog-latest/data_gouv_datasets_catalog_part_{0,1,2}.parquet` (208 708 497 o `32a8c96a…d891`, 223 345 448 o `7fb33b76…c5476`, 34 698 180 o `2174d151…2479`, SHA complets dans `data/raw/eval-sources/INDEX.json` du dépôt principal). `ggml-org/bge-m3-Q8_0-GGUF` @ `9eba04c5d75ba5a1595e45de734d36bef4e5cb98` : `bge-m3-q8_0.gguf` 634 553 760 o `aa473d51f451a22f0fcf39ba3330c14bed38a385712b1113440f69df4047a173`.
- Lecture seule : `<dépôt principal>/data/raw/eval-sources/hf/AgentPublic/` contient déjà les 4 parquet aux mêmes SHA (réutilisables par `--reutiliser`).

## Tasks & Acceptance

**Execution:**
- `config/fetch.toml` -- créer `[telechargement]` : `essais`, `attente_initiale`, `attente_max`, `taille_bloc`, `seuil_verification_espace` (1 Go), `marge_espace`, `facteur_extraction` -- AD-22 (aucune valeur codée en dur).
- `src/slmsp/fetch/config.py` -- modèles `ConfigTelechargement`, `ConfigSources` (`jeux[]` : `nom`, `depot`, `revision` 40 hex, `licence`, `fichiers[]` : `chemin`, `sha256`, `taille`) et chargeurs (`charger_config_fetch`, `charger_config_sources`, `charger_config_llamacpp`, `charger_config_modele(slug)`), chemins par défaut sous `racine_projet()/config`.
- `src/slmsp/fetch/hf.py` -- moteur : `Telechargeur` (client injecté, config, `reutiliser`), `telecharger(url, destination, sha256, taille, ...) -> ResultatFichier`, relances, reprise, contrôle SHA, réutilisation locale, `verifier_espace_total` ; partie HF : `preparer_hf()` (env + `set_client_factory`), `url_hf`, `metadonnees_hf` (HEAD sans redirection : taille, `X-Linked-Etag`, `X-Repo-Commit`), en-têtes avec token ; erreurs `TelechargementEchoue`, `ShaInvalide`, `ArchiveInvalide` (sous-classes de `SlmspError`).
- `src/slmsp/fetch/llamacpp.py` -- lit la release par l'API GitHub (taille, `digest` recoupé avec la config), télécharge les 4 archives dans `vendor/llama.cpp/<tag>/archives/`, extrait `cpu`→`bin-cpu`, `cuda`+`cudart`→`bin-cuda`, sources→`src` (dossier racine unique retiré), sans écraser ni lancer de binaire ; vérifie `binaires` s'il est renseigné ; marqueur `<archive>.extrait.json`.
- `src/slmsp/fetch/sources.py` -- pour chaque jeu, écrit sous `data/raw/mediatech/<nom>/<revision>/<nom de fichier>` (refus si deux fichiers ont le même nom).
- `src/slmsp/fetch/modeles.py` -- pour `config/modeles/<slug>.toml` : GGUF sous `models/<slug>/gguf/`, `fichiers` HF sous `models/<slug>/hf/` (révision `revision` ; GGUF d'un autre dépôt : révision `main` + SHA obligatoire).
- `src/slmsp/cli/fetch.py` -- `slmsp fetch {llamacpp, sources [--jeu], modeles SLUG..., benchmarks ...}` avec `--racine` et `--reutiliser` ; ouvre un run `fetch` (slug = sous-commande), inscrit `fichiers.jsonl`, termine `complet` ou `partiel-erreur` ; `benchmarks` appelle `slmsp.fetch.benchmarks.executer(arguments, racine)` ou répond « commande non implémentée : fetch benchmarks » (code 2).
- `config/llamacpp.toml`, `config/sources.toml`, `config/modeles/bge-m3.toml` -- valeurs relevées ci-dessus (BGE-M3 : `embedding = true`, `pooling = "cls"`, `contexte = 8192`, `fichiers = []`).
- `tests/fetch/test_hf.py`, `test_llamacpp.py`, `test_sources.py`, `test_modeles.py`, `tests/fetch/conftest.py` -- serveur factice `httpx2.MockTransport` (Range, 206, 429/500, redirection) ; archives zip générées dans `tmp_path` ; cas de la matrice ; test CLI de bout en bout ; un test `reseau` par pilote (exclu par défaut).

**Acceptance Criteria:**
- Given `config/llamacpp.toml`, when `uv run slmsp fetch llamacpp` s'exécute, then `vendor/llama.cpp/b11429/{bin-cpu,bin-cuda,src}` existent, chaque archive est vérifiée par SHA-256, et aucun sous-processus n'est lancé.
- Given `config/sources.toml`, when `uv run slmsp fetch sources` s'exécute, then les parquet sont sous `data/raw/mediatech/<jeu>/<revision>/`, obtenus par l'URL `resolve/<revision>` (jamais le datasets-server).
- Given `config/modeles/bge-m3.toml`, when `uv run slmsp fetch modeles bge-m3` s'exécute, then `models/bge-m3/gguf/bge-m3-q8_0.gguf` a le SHA de la config.
- Given toute exécution, when elle se termine, then `runs/fetch/<run_id>/fichiers.jsonl` liste chaque fichier (dépôt ou URL, fichier, révision, octets transférés, SHA-256, statut) et chaque requête figure au journal des requêtes du profil `outillage`.
- Given `huggingface_hub` installé, when `preparer_hf()` est appelé, then `HF_HOME` vaut `<models>/.cache-hf`, `HF_HUB_DISABLE_TELEMETRY=1`, et la fabrique de client de `huggingface_hub` est `net.fabrique_hf`.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 48 findings — high 0, medium 12, low 30, false 5, maybe-false 1
- findings:
  - `[medium]` `[patch]` (VG) `--reutiliser` jamais testé par la CLI — ajouté : test CLI `sources --reutiliser` (statut `reutilise`, aucune requête, config du run).
  - `[medium]` `[patch]` (VG) contrôle d'espace avant téléchargement non testé pour `llamacpp` et `modeles` — ajouté : un test par pilote (aucun GET de fichier).
  - `[low]` `[patch]` (VG) branche `KeyboardInterrupt` → `interrompu` non testée — ajouté : test CLI d'interruption.
  - `[medium]` `[patch]` (VG) reprise 416 et `Content-Range` incohérent non testés — ajouté : deux tests moteur.
  - `[low]` `[patch]` (VG) noms ambigus Windows et doublons de casse dans un zip non testés — ajouté : cas hostiles et doublon `A.dll`/`a.dll`.
  - `[low]` `[defer]` (VG) copie de réutilisation au mauvais SHA non testée — différé (frontmatter), cas rare.
  - `[medium]` `[patch]` (VG) erreur locale (`OSError`) relancée comme erreur de transport — `erreur_transport` limité à `ConnectionError`, `TimeoutError`, `TransportError` httpx.
  - `[medium]` `[patch]` (BH) même cause : `OSError` disque relancée 6 fois — même correctif.
  - `[medium]` `[patch]` (BH) `Retry-After` non borné, `inf` → `OverflowError` — valeurs non finies ignorées, attente plafonnée à `attente_max`.
  - `[low]` `[reject]` (BH) 403 de limite GitHub non relancé — un appel d'API par run (60/h), une relance de 2 min ne couvrirait pas la remise à zéro horaire.
  - `[medium]` `[defer]` (BH) GGUF d'un autre dépôt : révision « main » inscrite à la relance, pas de révision propre en config — schéma core (1.3), différé à 8.1.
  - `[low]` `[defer]` (BH) `fichiers` HF : HEAD à chaque relance — différé à 8.1 avec le cas non LFS.
  - `[low]` `[reject]` (BH) fichiers `.copie-`/`.extraction-` orphelins après interruption — rare, jamais effacés par conception, correctif ajouterait du suivi.
  - `[medium]` `[patch]` (BH) binaires extraits jamais vérifiés (`[binaires]` vide) — 4 SHA épinglés (llama-server cpu/cuda, ggml-cuda.dll, convert_hf_to_gguf.py), relance réelle conforme.
  - `[low]` `[patch]` (BH) lien dur qui couple les deux copies, non documenté — aide de `--reutiliser` complétée.
  - `[low]` `[reject]` (BH) `--reutiliser` sans effet quand la taille est inconnue — seule l'archive des sources est concernée, ajout de branche non justifié.
  - `[low]` `[patch]` (BH) run en échec sans chemin affiché — `run <id> : <dossier>` imprimé sur stderr.
  - `[low]` `[reject]` (BH) noms réservés Windows (CON, NUL) non refusés — archives épinglées par SHA, garde supplémentaire sans bénéfice.
  - `[low]` `[patch]` (BH) liste de branches non testées et garde AST hors `cli/fetch.py` — tests ajoutés (cf. VG) et garde étendue à `cli/fetch.py` ; recouvrement cuda/cudart déjà vérifié par l'extraction réelle.
  - `[low]` `[reject]` (BH) re-hachage complet à chaque `deja-present` — contrôle d'intégrité voulu (AC4).
  - `[false]` `[reject]` (BH) course au renommage sous POSIX — projet Windows seul (D2) : `os.rename` y échoue si la cible existe.
  - `[low]` `[reject]` (BH) cohérence interne de `ConfigTelechargement` — config versionnée et relue, garde sans usage réel.
  - `[low]` `[reject]` (IA) tests `reseau` limités aux en-têtes — les téléchargements réels ont été faits une fois par la CLI ; un test qui retélécharge violerait « ne jamais télécharger deux fois ».
  - `[medium]` `[patch]` (IA) AC5 : le contrôle avant téléchargement de `llamacpp` ignore l'extraction (> 1 Go au total) — estimation d'extraction ajoutée au contrôle préalable.
  - `[false]` `[reject]` (IA) téléchargements lourds lancés depuis le worktree — demandés explicitement par l'orchestrateur, vers le dépôt principal (`--racine`).
  - `[low]` `[patch]` (IA) fabrique asynchrone de `huggingface_hub` non injectée — `set_async_client_factory(net.fabrique_hf_async)` ajouté et testé.
  - `[false]` `[reject]` (IA) `gguf-py` non branché dans `pyproject.toml` — hors liste de fichiers de la story 2.1.
  - `[false]` `[reject]` (IA) `--racine` ne déplace pas `models/` — voulu : `models/` suit `SLMSP_MODELS_DIR` (consignes 1.2).
  - `[maybe-false]` `[defer]` (EC) `.part` des sources + réponse 200 à Range bloque les relances — dépend du support Range de codeload, différé (medium non vérifié).
  - `[medium]` `[patch]` (EC) `OSError` locale relancée — même correctif que VG.
  - `[low]` `[reject]` (EC) compteur d'échecs non remis à zéro sur progression — lien instable rare, 6 essais suffisent pour 200 Mo.
  - `[medium]` `[patch]` (EC) `Retry-After` `inf` ou énorme — même correctif que BH.
  - `[low]` `[patch]` (EC) dossier `--reutiliser` inexistant ignoré — `ConfigurationInvalide` avant ouverture du run.
  - `[false]` `[reject]` (EC) lien dur sans re-hachage — le candidat vient d'être haché par `trouver_local` juste avant le lien.
  - `[low]` `[reject]` (EC) copie interrompue laisse `.copie-*` — rare, rien n'est effacé par conception.
  - `[low]` `[reject]` (EC) deux `fetch` concurrents sur le même `.part` — un seul opérateur, verrou non justifié.
  - `[low]` `[patch]` (EC) marqueur présent mais fichiers disparus — couvert par les `[binaires]` épinglés (contrôle à chaque exécution).
  - `[low]` `[reject]` (EC) archive des sources vide après retrait de la racine — archive épinglée par SHA.
  - `[low]` `[reject]` (EC) `asset.nom` avec `/` ou `..` — config versionnée, schéma core.
  - `[low]` `[reject]` (EC) dépôts non validés dans les schémas core — hors zone (1.3), config versionnée.
  - `[low]` `[reject]` (EC) nom de membre invalide sous Windows → `OSError` brute — archives épinglées par SHA.
  - `[low]` `[reject]` (EC) 403 de limite GitHub — même motif que BH.
  - `[medium]` `[defer]` (EC) GGUF d'un autre dépôt présent : révision « main » — même entrée différée que BH.
  - `[low]` `[reject]` (EC) dépôts égaux à la casse près — cas théorique.
  - `[low]` `[reject]` (EC) `fetch benchmarks` : `--reutiliser` et arguments à tiret — l'interface appartient à la story 6.1.
  - `[low]` `[reject]` (EC) fichier en échec absent de `fichiers.jsonl` — le motif est inscrit dans `etat.jsonl` (`partiel-erreur`).
  - `[low]` `[reject]` (EC) 501 et 505+ non relancés — erreurs non transitoires, conforme à « 429, 500 à 504 ».
  - `[low]` `[reject]` (EC) `fetch benchmarks` n'ouvre pas de run — à la charge de `slmsp.fetch.benchmarks` (story 6.1).

## Design Notes

- Pas de `hf_hub_download` : il écrit le fichier final avant tout contrôle de SHA et transfère par hf-xet hors du client gardé. Le moteur maison passe tout par la passerelle et journalise chaque transfert au niveau de l'appel (`fichiers.jsonl`), ce qui couvre l'exigence hf-xet.
- `fetch` ne peut pas importer `httpx2` (TID251) : une erreur de transport se reconnaît à une classe `TransportError` d'un module `httpx*` dans le MRO, ou à `ConnectionError`/`TimeoutError` (une autre `OSError`, locale, n'est pas relancée).
- `--racine` permet de lancer le code d'un worktree en écrivant dans le dépôt principal (`uv run --project <worktree> slmsp fetch ... --racine <dépôt principal>`).

## Verification

**Commands:**
- `uv run pytest tests/fetch` -- expected: tout passe, sans réseau.
- `uv run pytest` et `uv run ruff check` -- expected: aucun nouvel échec.

## Auto Run Result

Status: done
Blocking condition: aucune

**Résumé.** `slmsp fetch {llamacpp, sources, modeles, benchmarks}` : moteur unique (`.part`, reprise `Range`, relances 429/5xx, SHA-256 avant renommage, rien d'effacé ni d'écrasé), clients de `slmsp.net` (profil `outillage`), run `runs/fetch/<run_id>/` avec `fichiers.jsonl`. Commits `f7fe636` (implémentation) et `93cb39d` (correctifs de revue).

**Revue (1 passe, 4 couches).** 48 constats : 18 lignes corrigées (patch), 5 différées (frontmatter `deferred`), 25 rejetées avec motif (triage ci-dessus). Patchs à leur verdict d'entrée : 7 medium (relance des `OSError` locales, `Retry-After`, `[binaires]`, espace d'extraction dans le contrôle préalable, tests CLI `--reutiliser`, tests d'espace par pilote, tests 416/Content-Range), 0 high, le reste low. Relecture complémentaire recommandée (`followup_review_recommended: true`) : la reprise réelle d'un `.part` de l'archive des sources par codeload.github.com (support de `Range` non vérifié) et l'estimation d'espace d'extraction n'ont été éprouvées que sur serveur factice.

**Vérification finale.** `uv run pytest` : 1025 passés, 116 sautés ; `tests/fetch` : 85 passés ; `ruff check` et `ruff format --check` propres. Relance réelle `fetch llamacpp --racine <dépôt principal>` après correctifs : 4 archives `deja-present`, 0 octet, 4 binaires vérifiés par SHA (run `20261012-094538-llamacpp-fb69`).

**Risques résiduels.** Liens durs entre `data/raw/mediatech/` et `data/raw/eval-sources/` (contenu partagé) ; story 8.1 : fichiers HF non LFS refusés et GGUF tiers épinglés par SHA seul ; `runs/fetch/` du dépôt principal non commités (6 runs).

**Fichiers.**
- `config/fetch.toml`, `config/llamacpp.toml`, `config/sources.toml`, `config/modeles/bge-m3.toml`.
- `src/slmsp/fetch/{config,hf,llamacpp,sources,modeles}.py`, `src/slmsp/cli/fetch.py`.
- `tests/fetch/{conftest,test_hf,test_llamacpp,test_sources,test_modeles}.py` (72 tests hors réseau, 3 tests `reseau`).

**Vérification** (2026-10-12) :
- `uv run pytest tests/fetch` : 72 passés. `uv run pytest` : 1012 passés, 116 sautés (dont `test_commande_declaree_sans_module_non_implementee[fetch]`, sauté puisque `cli/fetch.py` existe). `ruff check` et `ruff format --check` propres.
- `uv run pytest tests/fetch -m reseau` : 3 passés. Les en-têtes publiés (release GitHub, HEAD des 4 parquet et du GGUF) concordent avec la config.
- Exécutions réelles depuis le worktree, avec `--racine <dépôt principal>`, `SLMSP_MODELS_DIR=<dépôt principal>/models` et `SLMSP_ENV_FILE=<dépôt principal>/.env` :
  - `fetch sources --reutiliser data/raw/eval-sources/hf/AgentPublic` : 4 fichiers `reutilise` (liens durs), 0 octet transféré.
  - `fetch modeles bge-m3` : 634 553 760 octets, SHA conforme.
  - `fetch llamacpp` : 715 033 901 octets, `bin-cpu` (51 fichiers), `bin-cuda` (55 fichiers) et `src` (avec `gguf-py`) extraits.
  - Relances : tout est `deja-present`, aucun octet transféré. Les runs sont sous `<dépôt principal>/runs/fetch/`.

**Décisions prises seul** (à reporter au journal) :
1. Un fichier HF de `fichiers` sans `X-Linked-Etag` (fichier non LFS : `config.json`, tokenizer) est refusé (`ShaInvalide`), faute de SHA-256 attendu. La story 8.1 devra fournir un SHA en config ou accepter l'OID git.
2. `sources.nom` est le nom du fichier local (`llama.cpp-b11429-sources.zip`). L'URL est dérivée du tag (`archive/refs/tags/<tag>.zip`), sa taille est inconnue.
3. Espace avant extraction : au moins max(somme des tailles décompressées, taille de l'archive × `facteur_extraction`), plus `marge_espace`. Avant téléchargement : total restant par volume (taille moins `.part`), une taille inconnue compte pour 0.
4. Extraction : un fichier présent au même contenu (taille et CRC-32) est sauté, un fichier différent lève `ArchiveInvalide`. L'écriture passe par `<nom>.extraction-<horodatage>`, renommé ensuite. Sans marqueur, l'extraction est rejouée sans risque.
5. L'API GitHub n'est pas appelée si les trois archives binaires sont déjà présentes : une relance marche hors ligne.
6. Le run se termine `complet`, `partiel-erreur` (toute exception, relevée ensuite) ou `interrompu` (Ctrl-C). Les extractions sont inscrites dans `extractions.jsonl`. Une config invalide n'ouvre pas de run.
7. Un GGUF venant d'un autre dépôt : `main` est résolu en commit par `X-Repo-Commit`, puis le fichier est téléchargé à ce commit (révision inscrite au run).
8. Réponse 416 sur une reprise : le `.part` est tenu pour complet et le SHA tranche. `Content-Range` est contrôlé sur chaque 206.
9. Réutilisation par copie (lien dur impossible) : écriture dans `<nom>.copie-<horodatage>`, vérification, puis renommage.
10. `bge-m3.toml` : `protocole_outils = "natif"` (exigé par le schéma, sans objet pour l'embedding) ; licence des jeux `etalab-2.0`.
