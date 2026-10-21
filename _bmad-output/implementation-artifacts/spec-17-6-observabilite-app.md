---
title: 'Story 17.6 — Observabilité dans l''application : tokens, coût, impact environnemental, plafond de dépense'
type: 'feature'
created: '2026-10-21'
status: ready-for-dev
context:
  - '{project-root}/_bmad-output/implementation-artifacts/spec-17-4-mode-hybride-app.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-2026-10-20.md'
---

## Intention
Demandes d'Anaël du 21/10 (session principale) : (1) « voir l'impact environnemental et le coût (à 0 si on edge) des modèles, ainsi que les tokens en input/output. Important pour la démo afin de rassurer la DSI sur l'observabilité, quitte à modifier l'interface pour l'utilisateur final ensuite » ; (2) accord pour un plafond de dépense déterministe côté application (la v0.3.0 n'en a pas : seules les limites des fournisseurs s'appliquent). Les deux reposent sur le même compteur.

## Exigences
1. **Mesure par appel LLM** (local et externe, y compris boucle d'outils et vérification) : tokens d'entrée, tokens de sortie (usage renvoyé par le serveur ; llama-server local : `usage`/`timings`), durée, premier token, modèle (`modele_repondant`), fournisseur. Si un fournisseur ne renvoie pas d'usage : estimation (caractères ÷ 3) marquée `estime = true`.
2. **Coût** : externe = tokens × tarif du couple (preset, modèle) ; local = **0 €** (champ explicite, mention « pas de coût d'API ; matériel et énergie du poste non facturés »). Tarifs embarqués dans `config/` de l'application (preset `openrouter` : `qwen/qwen3.6-27b` 0,25 / 2,00 USD, `mistralai/mistral-small-2603` 0,15 / 0,60 USD ; `mistral` : `mistral-small-latest` 0,15 / 0,60 ; `ovh` : `Qwen3.6-27B` 0,40 / 2,70 EUR, `Mistral-Small-3.2-24B-Instruct-2506` 0,09 / 0,28 EUR ; date et source du relevé) ; modèle sans tarif : coût « inconnu » (jamais 0 par défaut), tarif saisissable dans Paramètres pour le preset `generique`. Devise affichée en euros (taux fixe documenté).
3. **Impact environnemental** (estimation, toujours présentée comme telle, avec fourchette) : énergie (Wh) et émissions (g CO₂e), méthodologie **EcoLogits** (GenAI Impact) :
   - externe : bibliothèque `ecologits` si elle s'embarque proprement dans l'exécutable PyInstaller (licence à vérifier et consigner), sinon réimplémentation documentée de ses formules (paramètres actifs du modèle, tokens de sortie, latence, PUE, mix électrique de la zone de l'hébergeur : DeepInfra → États-Unis, Mistral → France/UE, OVH → France) ; paramètres de chaque modèle dans la table des tarifs (paramètres totaux et actifs, zone) ;
   - local : énergie = puissance CPU moyenne configurable (défaut documenté, par ex. 25 W) × durée de génération, mix électrique France (valeur et source consignées) ; mention « estimation, poste non instrumenté ».
   - Hypothèses et sources visibles dans l'interface (lien « méthode »).
4. **Plafond de dépense** (déterministe, côté application) : pour chaque fournisseur externe, un plafond mensuel en euros réglable dans Paramètres (défaut **2 €**, 0 = fournisseur désactivé). Avant chaque appel, le coût **pire cas** (tokens d'entrée estimés + `max_tokens`, au tarif) est comparé au cumul du mois + pire cas ; s'il dépasse, l'appel n'est pas envoyé : le fournisseur est sauté (motif court `plafond-atteint`) et la cascade passe au suivant, puis au local. Après l'appel, cumul au coût réel. Modèle sans tarif connu : plafond inapplicable → fournisseur sauté (`tarif-inconnu`) sauf si l'Agent coche explicitement « autoriser sans tarif ». Cumul persistant en SQLite (par fournisseur et mois civil), remis à zéro au changement de mois.
5. **Stockage** : table additive `mesures_appels` dans `assistant.sqlite` (une ligne par appel : horodatage, échange, vue/tâche, modèle, fournisseur, tokens, estime, durée, premier token, coût, énergie, CO₂e, motif de saut éventuel) ; **jamais** de texte de demande ou de réponse ni de clé.
6. **Interface** :
   - Sous chaque réponse : une ligne discrète repliable « Détails » : modèle, tokens entrée/sortie, durée, coût (0 € en local), énergie et CO₂e estimés.
   - Nouvel onglet **« Observabilité »** (menu « Plus », pour la DSI) : totaux du jour et du mois par modèle et par fournisseur (appels, tokens entrée/sortie, coût, énergie, CO₂e, débit moyen), consommation de chaque plafond (barre), derniers appels (sans contenu), et **export CSV** des mesures (sans contenu). Avertissement « estimations » et lien vers la méthode.
   - Paramètres : plafond mensuel par fournisseur, puissance CPU moyenne du poste (impact local), tarif du preset `generique`.
7. **Non-régression** : sans fournisseur externe, seules les mesures locales s'ajoutent (aucun réseau) ; le comportement de génération est inchangé.

## Tests (aucun réseau)
Mesure par appel (usage présent, absent → estimé) ; coût externe et local ; impact (valeurs de référence calculées à la main pour un cas, ou tests de la bibliothèque si elle est utilisée) ; plafond : pire cas qui dépasse → saut et motif, cascade, cumul réel, changement de mois, tarif inconnu ; stockage sans contenu ; agrégats de l'onglet ; export CSV ; vue (pont, ligne Détails, onglet) ; non-régression.

## Hors story
Instrumentation matérielle réelle de la consommation (RAPL, etc.) ; tarifs mis à jour en ligne.

## Amendements après relecture de la spec (2026-10-21, second avis ; décisions de l'orchestrateur)
Ils priment sur les exigences ci-dessus.
1. **Usage demandé par preset** : `openrouter` → `usage = {include: true}` ; `ovh` → `stream_options = {include_usage: true}` ; `mistral` → rien d'ajouté (l'API renvoie l'usage en fin de flux, constaté le 21/10 ; schéma strict) ; `generique` → `stream_options` seulement si l'Agent le coche. Usage absent → estimation marquée `estime` partout (Détails, Observabilité, cumul du plafond).
2. **Instrumentation au niveau client**, pas sur `Fin` : un observateur par appel (interface unique) branché dans `ClientOpenAI._appel` et dans le flux de `ClientLlama`, pour couvrir réponse, boucle d'outils (`harness/taches/__init__.py:406-431`) et vérification (`harness/verification.py:450`). Ligne de mesure écrite dans un `finally` : un appel interrompu (erreur après jetons, arrêt par l'Agent, flux fermé) est compté à l'estimation (entrée estimée + caractères émis ÷ 3), marqué `interrompu` et `estime`.
3. **Plafond dans `ClientOpenAI`**, avant **chaque tentative HTTP** (y compris relances, `pour()`, boucle d'outils, vérification) : réservation du pire cas sous verrou (verrou de processus + transaction SQLite), régularisation au coût mesuré ou estimé. Pire cas = (entrée estimée : caractères ÷ 3 × 1,25) × tarif d'entrée + `max_tokens` effectif × tarif de sortie, × (1 + `relances_max`). `n` et `max_tokens` sont **interdits** dans `parametres_supplementaires`. Plafond atteint au premier appel d'un échange → fournisseur suivant puis local (bandeau `plafond-atteint`) ; en cours d'échange → erreur explicite `plafond-atteint` avec « Réessayer avec le modèle local ».
4. **Test de connexion** : compté (mesure et plafond, tâche `test-connexion`, `max_tokens` 1) ; refusé si le plafond est atteint.
5. **Clé du cumul** : (hôte, modèle), table `cumuls_depense` distincte, **jamais effacée** par l'effacement de l'historique ; supprimer ou renommer une entrée ne remet pas le cumul à zéro. Mois civil en **UTC**. L'horloge système n'est pas infalsifiable : écrit dans l'aide.
6. **Tarifs** : une seule source, `config/tarifs.toml` (même schéma, USD, `taux_usd_eur` au pair et prudent), étendue aux modèles des presets de l'application (`mistral-small-latest` chez Mistral, modèles OVH déjà présents) ; vérifier qu'elle est embarquée par `outils/construire_application.py`, sinon l'embarquer. Pas de seconde table de prix.
7. **Impact environnemental : pas de dépendance `ecologits`.** Réimplémentation documentée des formules d'EcoLogits (version et source citées dans le code et dans l'aide « Méthode »), paramètres par modèle (paramètres totaux et actifs, zone de l'hébergeur, PUE) dans `config/impacts.toml` embarqué ; fourchette basse-haute affichée. Local : puissance CPU moyenne réglable (défaut 25 W) × durée × mix électrique France (valeur et source consignées).
8. **Défauts et lisibilité** : plafond par défaut 2 € par mois et par fournisseur, **lu à chaque appel** (un changement s'applique tout de suite) ; tout saut pour plafond est visible (bandeau, Observabilité). **Pas** de case « autoriser sans tarif » : un modèle sans tarif est sauté (`tarif-inconnu`) ; pour le preset `generique`, le tarif est un champ obligatoire.
9. **Export CSV** : cellules commençant par `=`, `+`, `-`, `@` préfixées d'une apostrophe ; aucun champ de contenu ; le nom de modèle est conservé (préfixé si besoin).
