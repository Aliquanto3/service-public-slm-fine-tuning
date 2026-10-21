---
title: 'Story 17.4 — Mode hybride dans l''application : modèle externe réglable, modèle local en secours'
type: 'feature'
created: '2026-10-21'
status: ready-for-dev
context:
  - '{project-root}/_bmad-output/planning-artifacts/stories-epic-17-modele-distant.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-17-1-modele-distant.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-2026-10-20.md'
---

## Intention
Demande d'Anaël du 21/10 : tester depuis le PC cible, dans l'application installée (release v0.3.0), un modèle plus gros servi par un endpoint externe compatible OpenAI (OpenRouter et Qwen3.6-27B pour la démonstration, puis un endpoint sur infrastructure qualifiée SecNumCloud). L'Index local, l'embedding bge-m3, les outils et l'interface restent sur le poste ; seule la génération part vers l'endpoint. Le modèle local reste démarré et sert de secours.

## Carte du code (relevé du 21/10)
- Démarrage : `src/slmsp/app/principal.py` (`lancer` l.523, `Demarrage._executer` l.397) → `harness/assemblage.py:assembler` (l.124) → `ServeurLlama("base:<modele>")` puis `serveur.client()` → `ClientLlama` (`inference/client.py:359`).
- Flux d'une vue : `app/pont/__init__.py:envoyer` (l.101) → `app/pont/conversation.py:95` → `harness/service.py:224` `AssistantService.repondre` ; évènements poussés par lots vers `slmspRecevoir`.
- Réglages : table SQLite `reglages` de `%LOCALAPPDATA%\AssistantSP\assistant.sqlite` (`app/stockage.py`, `REGLAGES_DEFAUT`) ; pont `app/pont/reglages.py` ; front `src/slmsp/app/ui/js/vues/parametres.js` (l.42), `src/slmsp/app/ui/css/parametres.css`, `src/slmsp/app/ui/index.html` l.96. Le choix de modèle s'applique au démarrage suivant (`modele_actif.py`).
- Réseau : profil `assistant`, Liste blanche fermée (`config/liste-blanche.toml`, contrôle `net/profils.py:224-227`), Passerelle `net/client.py:172`, hôtes calculés au lancement ; Mode hors ligne `harness/modes.py` (`ModeSonde`, réglage `hors_ligne_force`) ; journal `JournalApplication` (`app/stockage.py:354`).
- Secrets : aucun stockage utilisateur ; `core/secrets.py` lit le `.env` de développement.
- Client de flux distant : `src/slmsp/evaluation/client_distant.py` (story 17.1, `ClientDistant`, `generer(messages, *, tools, options)` → `Jeton` / `AppelOutil` / `AppelNonConforme` / `Fin`), lié au registre budgétaire et à la fiche `modele_distant`.

## Exigences
1. **Client de flux sans budget** : extraire de `ClientDistant` un cœur réutilisable (requête compatible OpenAI en flux SSE, commentaires ignorés, `tool_calls` réassemblés, `finish_reason: error`, relances avant le premier octet) qui ne dépend ni du registre ni de la fiche ; `ClientDistant` (évaluation) l'enveloppe avec le budget et les contrôles d'hébergeur, **sans changement de comportement** (tests de 17.1 verts). L'application utilise le cœur directement.
2. **Réglages** (table `reglages`, valeurs JSON) : `modele_externe = {actif: false, url_base: "https://openrouter.ai/api/v1", modele: "qwen/qwen3.6-27b"}` par défaut, inactif. `url_base` en **https** seulement (refus sinon), sans identifiants dans l'URL. Appliqué au démarrage suivant, comme le choix de modèle (message « relancer l'application »).
3. **Clé** : saisie dans Paramètres (champ masqué), stockée **chiffrée par DPAPI** de l'utilisateur Windows (`CryptProtectData` / `CryptUnprotectData` par `ctypes`, portée utilisateur courant) dans un fichier dédié du dossier de données (pas dans la table `reglages`, jamais dans un journal, jamais renvoyée au front : le front ne reçoit que « clé enregistrée : oui/non ») ; bouton « Effacer la clé ». Hors Windows (tests) : implémentation factice injectée.
4. **Réseau** : quand le modèle externe est actif, l'hôte de `url_base` est ajouté **au lancement** aux hôtes autorisés du profil `assistant` pour POST `<url_base>/chat/completions` seulement (port 443) ; la Liste blanche configurée reste fermée pour tout le reste. En Mode hors ligne (forcé ou détecté), le modèle externe n'est pas appelé (génération locale, Mode affiché). Chaque appel passe par la Passerelle et apparaît dans le journal des Requêtes sortantes (hôte, chemin, statut, durée ; ni prompt ni réponse ni clé).
5. **Corps de requête** : mêmes messages, outils et options que pour le modèle local (température, `max_tokens` du Harnais) ; si l'hôte est `openrouter.ai`, ajouter `provider = {data_collection: "deny", require_parameters: true}` et `reasoning = {enabled: false}` (même fonction isolée que 17.1). Délais : connexion 10 s, premier octet 60 s.
6. **Secours** : le llama-server local de génération est toujours démarré. Si l'endpoint échoue **avant le premier jeton** (connexion, délai, HTTP 4xx/5xx après relances, clé absente ou refusée), la réponse est générée par le modèle local et la vue affiche un bandeau « Modèle externe indisponible (<motif court>) : réponse du modèle local ». Après le premier jeton, une coupure termine la réponse en erreur avec le bouton « Réessayer avec le modèle local ». Le motif est journalisé sans contenu.
7. **Interface** :
   - Paramètres : section « Modèle externe (expérimental) » : case Activer, URL, modèle, clé (masquée), bouton « Tester la connexion » (requête de 1 token de sortie, résultat : OK + latence, ou motif d'échec), rappel en une phrase : « Le texte de vos demandes est envoyé à cet hôte ; l'Index et l'historique restent sur le poste. »
   - Indicateur de Mode (story 12.9) : « Modèle externe : <hôte> » quand il est actif, sinon l'affichage actuel.
   - À propos : version, modèle local, modèle externe (hôte et identifiant) s'il est actif.
   - Accessibilité et styles comme les autres sections (jetons de `ui/css`).
8. **Traçabilité** : chaque échange de l'Historique consigne le modèle qui a répondu (`local:<slug>` ou `externe:<hôte>/<modèle>`), visible dans le détail de l'échange et dans l'export des Retours (anonymisé comme le reste).
9. **Non-régression** : modèle externe inactif = comportement actuel octet pour octet (aucun réseau supplémentaire, aucune requête externe, mêmes démarrages).

## Tests (aucun appel réel)
Réglages par défaut et validation (https seul) ; DPAPI factice : chiffrement, lecture, effacement, jamais renvoyée au front ; hôte ajouté au profil seulement si actif, chemin limité, Liste blanche inchangée sinon ; Mode hors ligne → local ; corps de requête (OpenRouter et hôte générique) ; secours avant premier jeton (connexion, 401, 500, délai) → réponse locale + bandeau ; coupure après premier jeton → erreur + réessai local ; journal sans contenu ni clé ; Historique consigne le modèle ; test de connexion ; tests JS de la vue Paramètres si le projet en a (sinon test du pont) ; tests de 17.1 et de l'app existants verts.

## Hors story
Construction de l'installateur et release v0.3.0 (orchestrateur) ; endpoints souverains réels ; budget côté application (la limite de crédit est réglée sur la clé chez le fournisseur).

## Amendements après relecture de la spec (2026-10-21, second avis ; décisions de l'orchestrateur)
Ils priment sur les exigences ci-dessus. **Dépend de 17.1 fusionnée dans main** (profil à chemins, `ClientDistant`).
1. **Profil dédié** `modele-externe` (ajouté au `Literal` `ProfilReseau`, `core/schemas/journal_requetes.py:20`) : une seule règle, hôte de `url_base`, méthode POST, chemin `<chemin de url_base>/chat/completions`, port 443 — sur le modèle d'`eval-distant` (17.1). Le profil `assistant` et `ConfigListeBlanche` ne sont **jamais modifiés** (sinon `outillage` hériterait de l'hôte, `net/profils.py:231-233`, `net/client.py:191`).
2. **Journal** : le schéma `EntreeJournalRequetes` reste tel quel (pas de chemin ni de durée) ; le motif d'échec et la durée vont dans `JournalApplication`, sans contenu.
3. **Garde WebView** : inchangée, elle lit le fichier de Liste blanche (`principal.py:549`) ; l'hôte externe n'est jamais navigable dans la WebView.
4. **Hors ligne** : en Mode hors ligne (forcé ou détecté), ou si la Passerelle lève `HoteBloque`, aucun appel externe : secours local avec motif `hors-ligne` (pas une erreur fatale).
5. **Traçabilité** : pas de changement de `Fin` (`core/evenements.py:121-131`) ; l'échange de l'Historique reçoit une colonne additive `modele_repondant` (migration SQLite additive, valeur nulle pour les échanges existants), renseignée par le service à partir du client qui a répondu. La coupure après le premier jeton utilise le chemin d'erreur existant du Harnais (même évènement que `ErreurInference` aujourd'hui).
6. **Périmètre des appels** : quand le modèle externe est actif, **tous** les appels LLM d'un échange (réponse, boucle d'outils, vérification `harness/verification.py:450`) partent vers l'externe. La décision de secours se prend au **premier appel de l'échange** : échec avant son premier jeton → tout l'échange en local (bandeau). Une fois l'externe utilisé dans l'échange, un échec ultérieur termine l'échange en erreur avec « Réessayer avec le modèle local ». Le client composite expose la `taille_contexte` du modèle local (`harness/budget.py:76`), pour que les passages soient bornés comme aujourd'hui.
7. **Motifs** : un échec est réduit à un code court (`http-401`, `http-500`, `delai`, `connexion`, `cle-absente`, `hors-ligne`, `reponse-invalide`) ; **jamais** le corps de la réponse (ni dans le bandeau, ni dans le test de connexion, ni dans les journaux, ni dans l'export des Retours).
8. **Test de connexion** : construit un client ponctuel à partir des valeurs du formulaire (URL validée https, clé du champ ou clé enregistrée), avec un profil `modele-externe` ponctuel limité à cette requête ; pas besoin de relancer pour tester ; l'activation, elle, s'applique au démarrage suivant.
9. **Emplacement du cœur** : `src/slmsp/inference/client_openai.py` (embarqué par `packaging/assistantsp.spec:17-22`, qui ne collecte pas `slmsp.evaluation`) ; le cœur n'importe ni `slmsp.budget` ni `slmsp.evaluation` ; `ClientDistant` l'importe.
10. **Réglages** : `modele_externe` ajouté à `REGLAGES_DEFAUT` (`app/stockage.py:37-43`) et exposé par `app/pont/reglages.py:130`.
11. **Délais** : connexion 10 s, lecture 60 s, total 300 s (`DelaisAppel`).
12. **DPAPI** : tout échec de `CryptUnprotectData` (fichier corrompu, autre utilisateur) = « clé absente » (secours local, motif `cle-absente`), jamais une exception remontée au front.
13. **Autres hôtes compatibles OpenAI** (essai OVHcloud AI Endpoints du 21/10, `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1`, modèles `Qwen3.6-27B`, `Mistral-Small-3.2-24B-Instruct-2506`…) : hors `openrouter.ai`, aucun paramètre additionnel n'est envoyé (OVH refuse `chat_template_kwargs` en HTTP 400). Les deltas de raisonnement (`reasoning`, `reasoning_content`) renvoyés à part sont ignorés pour l'affichage mais comptent comme activité pour le délai de lecture ; seul `content` est montré. Un réglage facultatif `parametres_supplementaires` (objet JSON validé, ≤ 2 Ko, clés `model`, `messages`, `tools`, `stream` interdites) permet d'ajouter un paramètre propre à l'hôte (par ex. `reasoning_effort`) sans changer le code.
