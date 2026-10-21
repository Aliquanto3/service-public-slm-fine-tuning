---
title: 'Story 17.1 — Modèle distant dans `eval run` (OpenRouter d''abord)'
type: 'feature'
created: '2026-10-21'
status: ready-for-dev
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
