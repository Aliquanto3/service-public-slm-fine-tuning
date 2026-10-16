---
title: 'Story 12.12 — Exécutable PyInstaller avec Modèle embarqué et Index local'
type: 'feature'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-1-racine-de-composition-partagee.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-6-lancement-de-l-application.md'
warnings: []
deferred: []
---

## Intent
Construire en une commande le dossier `onedir` de l'Assistant (Q3) : application, `llama-server` CPU, Modèle embarqué (slug lu dans `config/application.toml`, Q13), BGE-M3 et Index local. Aucune dépendance à `uv` ni à Python chez l'Agent.

## Approach
- `outils/construire_application.py` : plan de fichiers, vérification des ressources et des empreintes **avant** PyInstaller (GGUF, `llama-server.exe`, fichiers de l'Index via `MANIFEST.json`), génération de `licences-tierces.json`, lancement de PyInstaller, contrôle de fermeture (AD-2), taille ≤ 4 Go (détail par composant sinon), `empreinte-application.txt` (SHA-256 de `AssistantSP.exe`, Q4), `manifeste-application.json`.
- `packaging/assistantsp.spec` (onedir, `console=False`) lit la liste de données dans le JSON désigné par `SLMSP_PLAN_BUILD` et les exclusions dans le script. `packaging/lanceur.py` est le point d'entrée.
- Données : `config/` (sans `benchmarks`, `runs`, `prompts/generateur`), `app/ui` **sans** `pont-factice.js`, `app/ressources`, `bin-cpu` de llama.cpp (`llama-server.exe` et ses DLL, sans les autres outils), GGUF du Modèle et de BGE-M3, dernière version de l'Index. Destinations sous `_internal` = `sys._MEIPASS` = `racine_projet()` gelée.
- `.gitignore` : `/build/`, `/dist/`.

Commande de build complet (depuis le dépôt principal, où vivent `vendor/`, `models/`, `index/`) :
`uv run --extra app python outils/construire_application.py` ; depuis un worktree, ajouter `--vendor <principal>\vendor --modeles <principal>\models --index <principal>\index`. Sans Modèle ni Index : `--sans-modele`.

## Mesures (build réel `--sans-modele`, CPU chargé)
- Runtime seul : **149 Mio (153 Mo)**, 50 s. Dont llama.cpp `bin-cpu` filtré 48 Mo. Le runtime est donc d'environ 105 Mo.
- Estimation du build complet : 153 Mo + GGUF Granite Q4_K_M 1 024 Mo + BGE-M3 635 Mo + Index 457 Mo ≈ **2,3 Go** (budget 4 Go). Non construit (RAM/CPU pris par les benchmarks) ; le contrôle de taille échoue de toute façon avec le détail par composant.
- L'exécutable gelé démarre (fenêtre WebView2 ouverte, base `assistant.sqlite` et profil WebView créés sous `%LOCALAPPDATA%\AssistantSP` seulement). Sans Index, l'assemblage échoue proprement (« démarrage : ManifesteInvalide », attendu). Rien n'est écrit dans le dossier construit. Non vérifié : réponse à une Question hors ligne (AC1), faute de Modèle.

## Tests
`tests/packaging/test_spec.py` (17) : plan et exclusions (pont factice, benchmarks, gabarits Générateur, `.env`, autres exécutables llama.cpp), mode `--sans-modele`, ressource manquante et empreintes fausses (GGUF, Index) avant PyInstaller, limite de taille et détail, fermeture runtime, empreinte de l'application, manifeste, licences, spec statique (onedir), chemins gelés simulés cohérents avec le plan, écritures hors `_MEIPASS`, destinations `slmsp/app/{ui,ressources}`. Suite complète : 4338 passés, 345 ignorés.

## Décisions prises seul
- Limite de 4 Go prise en décimal (4 000 000 000 o), la lecture la plus stricte.
- `licences-tierces.json` : généré au build dans `build/ressources/` ; le fichier versionné reste la base. Une licence n'est affirmée que si un fichier local l'atteste (`LICENSE` des sources llama.cpp : MIT ; métadonnées de pywebview : BSD ; PyInstaller : GPL-2.0+ avec exception). Granite, BGE-M3 et WebView2 restent « à vérifier » et sont listés dans le manifeste (`licences_a_verifier`).
- L'empreinte est celle de `AssistantSP.exe`, écrite après PyInstaller dans `_internal/slmsp/app/ressources/` (impossible de l'embarquer dans le fichier qu'elle hache).
- Les DLL de llama.cpp sont aussi copiées au premier niveau par l'analyse PyInstaller (doublon d'environ 10 Mo), laissé tel quel.

## À confirmer par Anaël
- Granite, BGE-M3 et WebView2 : licences à vérifier avant diffusion (pas de source locale).
- Limite 4 Go décimale ou binaire.
- Le dossier d'état machine (`SLMSP_VAR_DIR`, défaut `%LOCALAPPDATA%\slmsp\var`) n'est pas sous `%LOCALAPPDATA%\AssistantSP` : l'application ne le redirige pas. Hors du dossier d'installation, donc conforme à AD-23, mais à unifier si on veut une seule désinstallation (12.13).
- AC1 (réponse hors ligne) à vérifier au premier build complet, GPU et CPU libres.
- Premier build complet à lancer : empreintes réelles, taille mesurée, `DiskSpanning` si un fichier dépasse 2 Go (12.13).

## Auto Run Result
Statut : done (hors build complet). Revue conseillée sur `fermeture_runtime` (premier niveau seulement) et sur les `hiddenimports` du `.spec` (`collect_submodules` sur les couches runtime).
