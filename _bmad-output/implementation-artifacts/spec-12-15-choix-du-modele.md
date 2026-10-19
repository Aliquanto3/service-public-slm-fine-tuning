# Story 12.15 — Plusieurs modèles embarqués, choix manuel dans les Paramètres

Demande d'Anaël du 19 octobre 2026 : pouvoir changer de modèle à la main. Les tests d'UI et d'UX se font avec un modèle très rapide sur CPU et peu gourmand en RAM (Granite 4.0 350M), les tests sur le fond avec MiniCPM5-2B, qui a la meilleure Baseline sous le plafond de RAM. Aujourd'hui, `config/application.toml` fixe un seul `modele`, embarqué à la construction (`outils/construire_application.py:172-219`) et lu au démarrage (`app/principal.py:370-374`).

## Périmètre

### 1. Configuration
- `config/application.toml` :
  - nouvelle clé `modeles_embarques`, une liste non vide de slugs, chacun validé comme `modele` aujourd'hui (`core/schemas/config_application.py:28-37`) ;
  - `modele` reste le modèle **par défaut**, et doit figurer dans la liste ;
  - valeurs livrées : `modele = "minicpm5-2b"` et `modeles_embarques = ["minicpm5-2b", "granite-4.0-350m"]`.
- Rétrocompatibilité : sans `modeles_embarques`, la liste vaut `[modele]`.

### 2. Construction
- `construire_application.py` embarque le GGUF de chaque slug de `modeles_embarques`, avec contrôle du SHA comme aujourd'hui, plus bge-m3. Le plan et le manifeste de build listent tous les modèles. `--sans-modele` reste valable.
- Aucun téléchargement : un GGUF absent est une `ErreurBuild` claire, comme aujourd'hui.

### 3. Choix à l'exécution
- Le modèle actif est le réglage `modele` du stockage local (`app/stockage.py`, `lire_reglage` et son pendant d'écriture) s'il figure dans `modeles_embarques` **et** si son GGUF est présent dans l'installation ; sinon c'est le `modele` par défaut. Un réglage invalide est ignoré et consigné au journal, sans faire planter l'application.
- `principal.py` démarre l'assemblage avec ce modèle actif ; `pont/reglages.py` (`_modele`, à propos) affiche le modèle actif.
- Vue Paramètres (`app/ui/js/vues/parametres.js`) :
  - une liste « Modèle » des modèles embarqués, avec pour chacun son nom affiché (depuis `config/modeles/<slug>.toml` s'il existe un champ adapté, sinon le slug) ;
  - le choix est enregistré par le pont, avec un message clair : « Le changement sera appliqué au prochain démarrage de l'assistant. » ;
  - pas de redémarrage à chaud : c'est la solution la plus simple et la plus sûre (serveurs llama.cpp, verrous).
- Le journal de l'application note le modèle actif au démarrage.

### 4. Documentation
- `docs/installation-dsi.md` : une ligne sur les modèles embarqués et le choix dans les Paramètres. Taille de l'installateur : environ 1,8 Go avec les deux modèles, contre environ 1,6 Go.

## Tests
- Schéma : liste valide ; défaut absent de la liste refusé ; slug inconnu refusé ; clé absente → `[modele]`.
- Construction (plan, sans copie réelle de gros fichiers) : deux modèles plus bge-m3 au plan ; GGUF manquant → `ErreurBuild`.
- Résolution du modèle actif : réglage valide, réglage absent, réglage hors liste, GGUF absent.
- Pont : écriture du réglage, refus d'un slug non embarqué.
- Tests JS ou E2E existants de la vue Paramètres réalignés s'ils vérifient sa structure. Les nommer dans le compte rendu.

## Hors périmètre
La recette sur le PC cible (12.14, 13.8), la signature de l'installateur, le redémarrage à chaud.

## Auto Run Result
status: review

- Fait : schéma (`modeles_embarques`, défaut `[modele]`, doublons refusés), `app/modele_actif.py` (résolution), construction multi-modèles (`Plan.slugs`, manifeste `modeles`), pont (`reglages.modeles`, `ecrire("modele")`), vue Paramètres (liste « Modèle »), doc DSI.
- Décisions seul : nom affiché = slug (aucun champ de nom dans `config/modeles/*.toml`) ; le journal de démarrage est une ligne `LOGGER.info` ; « À propos » affiche le modèle réellement lancé (passé au pont), pas le réglage en attente ; `modele` ajouté à `REGLAGES_DEFAUT` ; la liste du schéma refuse les doublons.
- Tests réalignés : `test_pont_reglages` (slug À propos), `tests/packaging/test_spec.py` (fixture à deux modèles). Construction réelle non lancée.

## Revue
- high · second avis · corrigé : `construire_plan` n'embarquait pas `models/minicpm5-2b/chat_template.jinja` (`chat_template_force = true`) ; `ServeurLlama._verifier_fichiers` aurait refusé de démarrer le modèle par défaut. `fichiers_requis` (app/modele_actif.py) liste GGUF et template forcé avec leur SHA-256, utilisé par le build (`ErreurBuild` si absent) ; test `test_plan_embarque_le_chat_template_force`.
- high · second avis · corrigé : un modèle choisi qui échoue au démarrage bloquait l'application. `Demarrage._travail` efface le réglage, journalise et relance l'assemblage sur `config.modele` (seulement avant l'assemblage prêt) ; échec du défaut inchangé. Tests sur doublure dans `test_principal.py`.
- low · second avis · corrigé : `resoudre_modele_actif` exige les mêmes fichiers que le build (template forcé compris) ; test `test_template_force_absent`.
- low · second avis · corrigé : fixtures de `test_spec.py` avec template ; test « GGUF manquant » paramétré sur les deux modèles.
- low · revue · reporté : taille annoncée (1,8 Go) à confirmer par la construction réelle (orchestrateur) ; plan vérifié sur les vrais `models/` (GGUF et template trouvés, SHA du template conforme à la fiche).
- Complexité : 0 constat (aucune structure qui grossit à l'exécution).
