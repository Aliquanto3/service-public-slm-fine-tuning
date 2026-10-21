---
title: 'Story 17.1 — Modèle distant dans `eval run` (OpenRouter d''abord)'
type: 'feature'
created: '2026-10-21'
status: review
context:
  - '{project-root}/_bmad-output/planning-artifacts/stories-epic-17-modele-distant.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-2026-10-20.md'
---

## Intention
Évaluer avec le banc existant un modèle à poids ouverts servi par un fournisseur compatible OpenAI (OpenRouter dans cette story), pour comparer sa qualité à MiniCPM5-2B sur les jeux `dev*`. Les sorties ne servent qu'à la mesure (jamais à l'entraînement).

## Carte du code (relevé du 21/10)
- `--modele` : `src/slmsp/cli/eval.py:686` → `modele_ref.resoudre` (`src/slmsp/evaluation/modele_ref.py:240`, regex `_MOTIF_REF`, préfixes `base:`, `ft:`, `lora:`).
- Schéma : `ModeleRef` (`src/slmsp/core/schemas/run.py:30-37`).
- Run de génération : `src/slmsp/evaluation/generation.py:~229` (garde-fou `sans_reseau()`), `~300-330` (config du run, `profil_reseau`).
- Serveurs : `src/slmsp/evaluation/assemblage.py:63` (`PROFIL_RESEAU = "aucun"`), `:151` (llama-server de génération), `:162` (embedding bge-m3 CPU), `:231` (`sans_reseau`).
- Client local : `src/slmsp/inference/client.py` (`ClientLlama`, `corps_generation` l.440, `generer` l.482, évènements `Jeton` / `AppelOutil` / `AppelNonConforme` / `Fin`).
- Fournisseurs : `src/slmsp/fournisseurs/client.py` (`OPENROUTER`, secret `OPENROUTER_API_KEY`, `lire_cle` l.158 ; registre `src/slmsp/budget/registre.py` : `imputer`, `reserver`, `regulariser`).
- Réseau : `config/reseau.toml` (profils `outillage`, `aucun`), passerelle `slmsp.net.client`.
- Tarifs : `config/tarifs.toml` (aucune entrée Qwen3.6 ni Mistral Small 4).
- `src/slmsp/compare/chargement.py:205-208, 277, 299, 367` distingue `base:` et `ft:`.

## Exigences
1. **Référence** `distant:<slug>` : `ModeleRef` et `_MOTIF_REF` l'acceptent ; `<slug>` désigne une fiche `config/modeles-distants/<slug>.toml` (schéma validé, `schema_version = 1`) : `fournisseur` (`openrouter` seul admis), `modele_id` (ex. `qwen/qwen3.6-27b`), `hebergeur` épinglé (nom renvoyé par OpenRouter, ex. `DeepInfra`), `quantification` annoncée, `protocole_outils` (`natif` par défaut), `reasoning` (`off` seul admis ici), `contexte`. Créer les fiches `qwen3.6-27b` (hébergeur DeepInfra, fp8) et `mistral-small-4` (`mistralai/mistral-small-2603`, hébergeur Mistral). `--quantification` et `--variante` sont refusés ou ignorés avec message pour `distant:`.
2. **Requête** : même conversation, mêmes outils et mêmes options (température 0, graine 42, `max_tokens` du harnais) que pour un modèle local ; corps OpenRouter complété par `provider = {order = [hebergeur], allow_fallbacks = false, data_collection = "deny", quantizations = [quantification]}`, `reasoning = {enabled = false}` (ou l'équivalent documenté par OpenRouter, vérifié dans la doc et consigné), `usage = {include = true}`. Streaming SSE : les lignes de commentaire (`: OPENROUTER PROCESSING`) sont ignorées. Les évènements produits sont les mêmes que ceux de `ClientLlama.generer` (le reste de la boucle d'évaluation ne change pas). Implémentation au choix (client dédié ou `ClientLlama` paramétré par URL de base, en-têtes et corps additionnel) ; aucun `ClientLlama` local modifié dans son comportement pour `base:`/`ft:`/`lora:`.
3. **Hébergeur effectif** : le champ `provider` de la réponse est lu ; s'il diffère de l'hébergeur épinglé, l'item passe en erreur (`hebergeur_inattendu`) sans être retenu.
4. **Réseau** : nouveau profil `eval-distant` dans `config/reseau.toml` : POST `https://openrouter.ai/api/v1/chat/completions` seulement. Pour `distant:`, la génération utilise ce profil et `sans_reseau()` n'autorise que l'hôte du fournisseur (paramètre explicite, liste fermée) ; pour toute autre référence, comportement actuel inchangé (aucun réseau). Le run consigne `profil_reseau = "eval-distant"`. Aucun llama-server de génération n'est démarré ; le serveur d'embedding local l'est toujours (recherche Q inchangée), le Bac à sable rejouable RD aussi.
5. **Budget** : avant chaque appel, réservation au pire cas (tokens du prompt comptés ou majorés + `max_tokens`, au tarif de `config/tarifs.toml`) dans le registre, campagne courante, usage `eval-distant` (l'ajouter s'il existe une liste fermée d'usages) ; régularisation au coût réel (usage renvoyé). `--plafond-estime` **obligatoire** pour `distant:` ; arrêt propre au plafond de campagne, run reprenable par `--reprendre`. Tarifs ajoutés pour les deux modèles (prix OpenRouter du 21/10 : Qwen3.6-27B 0,25 $ / 2 $ par Mtok ; Mistral Small 2603 0,15 $ / 0,60 $), avec la date de relevé.
6. **Traçabilité** : chaque génération consigne `modele_id`, hébergeur effectif, quantification, `finish_reason`, usage, coût réel ; le run consigne la fiche distante (SHA du TOML). Temps au premier token et débit mesurés côté client (les `timings` de llama-server n'existent pas).
7. **Lecteurs** : la notation et `eval comparer` acceptent ces runs sans branche spéciale (vérifier) ; `compare/chargement.py` refuse proprement une référence `distant:` (message clair) au lieu d'un cas non couvert.
8. **D1** : aucune commande `data` n'accepte un run d'évaluation en entrée (vérifier ; ne rien ajouter qui le permette).

## Tests (fournisseur mocké, aucun appel réel)
Parsing et schéma `distant:` ; fiche invalide refusée ; corps de requête (provider, reasoning, options, outils natifs) ; flux SSE avec commentaires, jetons, appel d'outil RD, `finish_reason=length` ; hébergeur inattendu → erreur d'item ; réservation et régularisation au registre, refus sans `--plafond-estime`, arrêt au plafond puis reprise ; `sans_reseau` : hôte du fournisseur autorisé seulement pour `distant:`, toujours bloqué pour `base:` ; `compare/chargement.py` : refus clair ; non-régression du chemin local (tests existants verts).

## Hors story
Appels réels (l'orchestrateur lance un essai sur 2 items puis la mesure dev1) ; autres fournisseurs (Cloud Temple, Albert) ; intégration à l'application (17.4).

## Amendements après relecture de la spec (2026-10-21, second avis ; décisions de l'orchestrateur)
Ils priment sur les exigences ci-dessus en cas d'écart.
1. **Erreurs fatales** : `BudgetEpuise`, `SecretManquant`, `ConfigurationInvalide` et le dépassement du plafond de génération **interrompent** le run (statut interrompu, reprenable), au lieu d'être avalés en erreur d'item par `generer_item` (`generation.py:149`) et `_boucle` (l.229-236). Clé et budget sont vérifiés avant la première requête.
2. **Reprise** : pour `distant:`, `--reprendre` rejoue les items dont le statut n'est pas `ok` (429/5xx épuisés, hébergeur ou modèle inattendu, flux coupé, erreur SSE) ; le chemin local garde son comportement actuel (`core/artefacts.py:456-460`, `generation.py:411`). Test de reprise exigé.
3. **Manifeste distant** : `quantification`, `variante_llamacpp`, template GGUF et version llama.cpp de génération à `null` pour `distant:`, des deux côtés du contrôle de cohérence de reprise (`generation.py` ~370-400) ; la fiche distante (SHA du TOML) et `profil_reseau = "eval-distant"` y figurent.
4. **CLI** : `--quantification` n'est plus requis pour `distant:` (branche distincte dans `cli/eval.py:215` et `resoudre`) ; nouvelle option `--plafond-generation EUR`, **obligatoire** pour `distant:` (refus sinon), refusée pour les autres références : le run s'interrompt dès que le coût réel cumulé plus la réservation de l'appel suivant la dépasserait. `--plafond-estime` garde son sens actuel (juge).
5. **Poste budgétaire** : imputation `eval-distant` → poste `openrouter` existant de la campagne courante (plafond approuvé par Anaël, partagé avec juge-tiers et générateur ; aucun changement de plafond). Le plafond par run (point 4) borne la dépense.
6. **Client SSE** : client de flux dédié réutilisant `reserver` / `regulariser` / `_regler_echec` du registre. Relances (au plus 3, `Retry-After` respecté) seulement sur 429/5xx **avant le premier octet du flux** ; chaque relance libère puis refait sa réservation. Flux coupé après le début, ou `finish_reason: error` en HTTP 200 : item en erreur, régularisé au coût réel si l'usage est connu, sinon au pire cas réservé.
7. **Profil réseau** : `eval-distant` ajouté au `Literal` `ProfilReseau` (`core/schemas/journal_requetes.py:20`) et aux tests de `net/profils.py`.
8. **Résolution** : `distant:` est traité avant le repli `_resoudre_ft` (`modele_ref.py:56`, l.262-263) ; `bench`, `measure` et `export` refusent une référence `distant:` avec un message clair (`benchmarks/orchestrateur.py:216` notamment).
9. **Comparatif** : `compare/chargement.py` (l.277, 299, 367) ajoute un `Exclu` explicite (motif `modele-distant`) au lieu d'un écart silencieux.
10. **Profil du run** : `PROFIL_RESEAU` (`assemblage.py:63`, l.245 ; `generation.py:314`) devient un paramètre (défaut `aucun`) ; `sans_reseau(hotes_autorises=...)` à liste fermée, vide par défaut.
11. **Estimation des tokens d'entrée** : caractères de la requête sérialisée ÷ 3, multipliés par la majoration d'entrée du registre, bornés par le `contexte` de la fiche ; la sortie au pire cas = `max_tokens`.
12. **Corps OpenRouter** : `provider.require_parameters = true` en plus de `order`, `allow_fallbacks = false`, `data_collection = "deny"`, `quantizations`.
13. **Flux** : `tool_calls` fragmentés réassemblés par index (comme `inference/client.py:579`) ; le modèle renvoyé est contrôlé contre `modele_id` (item en erreur sinon, tarif du `modele_id`).

## Auto Run Result (2026-10-21, dev-story)
Livré : `distant:<slug>` (`ModeleRef`), fiches `config/modeles-distants/` (`FicheDistante`), `evaluation/client_distant.py` (SSE, budget, relances, contrôles), `assemblage.ouvrir_harnais_distant` / `client_distant`, `sans_reseau(hotes_autorises, profil)`, branches distantes de `generation.py` (manifeste à `null`, `appels-distants.jsonl`, fatales, reprise des items non `ok`), CLI `--plafond-generation`, profil `eval-distant`, usage `eval-distant` → `openrouter`, tarifs du 21/10, refus `bench`/`measure`/`resoudre`, `Exclu` `modele-distant` au comparatif. Tests : `tests/evaluation/test_modele_distant.py` (35), `tests/compare/test_comparatif.py` (+1) ; non-régression ciblée verte (evaluation, net, fournisseurs, budget, core, inference, benchmarks, cli, measure, architecture).

Décisions prises seul (simples, réversibles) :
- Erreurs fatales : le Harnais avale toute exception en `Erreur` ; le client mémorise l'erreur fatale (`erreur_fatale`) et la boucle la relève après l'item (ligne non écrite, run `interrompu`, exception propagée). Liste : `BudgetEpuise` (dont `PlafondGenerationAtteint`), `SecretManquant`, `ConfigurationInvalide`, `TarifInconnu`, `HoteBloque`. Le chemin local n'est pas touché.
- Code d'erreur d'item (`hebergeur_inattendu`, `modele_inattendu`, `erreur_flux`, `flux_coupe`, `http-<n>`, `transport`) reporté dans l'`Erreur` finale de la trace ; relevé complet par appel dans `appels-distants.jsonl` (pas dans `Generation`, pour ne pas toucher la clé du cache des verdicts).
- Reprise : la dernière ligne d'un item fait foi (`_boucle` et `notation._generations`, ex-`setdefault`) ; sans effet en local (une ligne par item). Le coût déjà réglé (somme de `appels-distants.jsonl`) compte dans le plafond du run repris ; `--plafond-generation` est redemandé à la reprise (peut être relevé) ; fiche modifiée depuis le run → refus.
- `provider` absent du flux → `hebergeur_inattendu` (prudence) ; modèle renvoyé comparé à `modele_id` à l'égalité stricte.
- `taille_contexte = None` pour le client distant (passages sans découpage) ; `compter_tokens` = caractères ÷ 3 (plafond des réécritures CO/TR). Estimation réservée : `min(ceil(caractères ÷ 3), contexte)`, la majoration du registre s'applique ensuite.
- Pas de `JournalAppels` (corps et réponses bruts) pour le flux : le relevé du run suffit à la mesure.
- `chat_template_kwargs` ignoré pour l'API ; `max_tokens` absent → 1024.
- Fiche `mistral-small-4` : `quantification = "unknown"` et contextes (262144, 131072) posés sans relevé : **à vérifier sur l'essai réel**.

Points à vérifier sur l'essai réel (orchestrateur) : nom du paramètre `reasoning` (`corps_reasoning`, `{"enabled": false}`) ; présence de `provider` et forme exacte de `model` dans les morceaux SSE ; valeur `quantizations` pour l'hébergeur Mistral ; refus éventuel de `require_parameters` avec `seed`.

## Revue
Revue du 2026-10-21 (Opus, avec la liste du second avis), branche rebasée sur main 7e8f564.
- MEDIUM, corrigé : morceau SSE mal formé (`delta`, fragment `tool_calls`, `function` non objet, `index` non entier) levait `AttributeError` hors d'`ErreurDistante`, réservation ouverte et coût absent du relevé. Lecture du flux protégée, contrôles `isinstance`, item en erreur `flux_invalide` réglé au coût réel ou au pire cas ; test `test_morceau_sse_mal_forme`.
- MEDIUM, corrigé (passe propre) : lecture abandonnée (générateur fermé par le consommateur, interruption) laissait la réservation ouverte ; réglée au pire cas, relevé `abandon` ; test `test_lecture_abandonnee_reglee_au_pire_cas`.
- LOW, corrigé : `Retry-After` non plafonné, désormais `min(attente, 60 s)` ; test `test_retry_after_plafonne`.
- LOW, corrigé : `BaseException` à l'ouverture du flux sans relevé ; relevé écrit avant de relancer, et `_boucle` écrit dans `appels-distants.jsonl` les relevés de l'item en cours quand le run s'interrompt (coût repris par `_cout_deja`).
- LOW, corrigé (passe propre) : échec de lecture du corps d'une réponse non 200 laissait la réservation ouverte ; réglée avant la lecture, lecture protégée.
- LOW, rejeté : `reasoning: {"enabled": false}` non vérifié ; isolé dans `corps_reasoning`, à confirmer par l'orchestrateur sur l'essai réel.
- LOW, rejeté : fiche lue sous `racine_projet()` et non sous `--racine` ; même convention que les fiches locales (`config/modeles`) et que `_entrees` : la configuration vient du projet, `--racine` porte les données et les runs.
- Passe propre sans autre constat : garde réseau (`sans_reseau` admet le seul hôte du fournisseur et ses adresses résolues ; profil `eval-distant` POST sur le chemin exact), budget et reprise, chemin local inchangé, `notation.py` (dernière ligne fait foi, sans effet en local), clé jamais journalisée, D1 respecté (textes factices seulement).
