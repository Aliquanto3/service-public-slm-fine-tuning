---
title: 'Story 13.5 — Vérification en ligne d''une page officielle, côté Harnais (FR-12)'
type: 'feature'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-5-pont-js-api-et-flux-d-evenements.md'
warnings: []
deferred:
  - 'Câblage de PontVerification dans Pont (Assemblage : passerelle, llm, mode) : story 13.6.'
---

## Intent

**Problem:** FR-12 (gardée par Q7) : l'Agent veut contrôler une réponse Question sur la page officielle qu'elle cite, sans qu'aucun texte saisi ne sorte du poste.

**Approach:** `harness.verification.verifier(reponse, sources, mode, passerelle, llm)` choisit la source de l'Index la mieux classée (plus petit `numero`) que la réponse cite par `[n]`. Il fait un GET de cette URL seule, par la passerelle (`net.client`, profil `assistant`, redirections suivies et recontrôlées à chaque saut, délai et taille bornés, aucune relance). Il extrait le texte avec `html.parser` (rien n'est exécuté ; scripts, styles et `head` sont ignorés ; `<main>`/`<article>` est préféré). Le Modèle embarqué compare ensuite la réponse à la page avec `VE.md`. Toute impossibilité rend le verdict `indisponible`, sans lever d'exception.

## Code Map

- `src/slmsp/harness/verification.py` (nouveau) : `verifier`, `choisir_source`, `extraire_texte`, `lire_comparaison`, `charger_prompt`, `Verificateur` (dépendances liées, pour le pont).
- `src/slmsp/core/evenements.py` : évènement `Verification` (`url`, `titre`, `date_consultation` ISO UTC, `verdict`, `phrase`, `extrait`) ; `Source.origine` admet `"verification"`.
- `config/prompts/taches/VE.md` : consignes seulement (emplacements `texte`, `document`), validé par `core.gabarits`.
- `config/harnais.toml` + `harness/config.py` : section `[verification]` facultative (`active`, `delai_s`, `taille_max_octets`, `caracteres_max_page`, `max_tokens`).
- `src/slmsp/app/pont/verification.py` : contrat du pont, avec un vérificateur injectable.
- `tests/harness/test_verification.py` (20) ; `tests/harness/test_taches.py` : `VE` ajouté à `PROMPTS_ATTENDUS` (garde D1.1).

## Contrat du pont (pour 13.6)

`appeler("verification.verifier", reponse: str, sources: list[dict])` rend `{"ok": true, "evenements": [<verification>, <sources>?]}`.
- `sources` : la liste `sources` de l'évènement `Sources` de la réponse.
- Le second évènement n'est présent que si la page a été lue. Il porte la page, avec `origine = "verification"` et `date` égale à la date de consultation.
- En cas d'arguments mal typés, le pont rend `requete-invalide`.
- Sans vérificateur branché (comportement actuel de `Pont`), il rend `non-implementee`.
- Pour le câblage en 13.6 : `PontVerification(Verificateur(assemblage.passerelle, service.llm, service.mode, service.config.verification))`.

## Auto Run Result

**Décisions prises seul :**
- Journal : `net` ne relève `outil`/`termes` que sur un POST. Un journal enveloppe (`_JournalEtiquete`) pose donc `outil = "verification-page"` et `termes = {"url": …}` sur les entrées de la vérification, redirections comprises. `slmsp.net` n'est pas modifié.
- La source choisie n'est pas filtrée par la Liste blanche avant l'envoi. La passerelle la refuse (`bloquee-liste`, AC3), et le refus est journalisé.
- Page trop grande, statut autre que 200, type autre que HTML ou texte vide : verdict `indisponible`, sans troncature.
- Le texte transmis au modèle est coupé à `caracteres_max_page` (8000), avec `temperature = 0`.
- Format de sortie demandé au modèle : 1re ligne `CONCORDANT`/`DIFFERENCE`, 2e ligne une phrase, 3e ligne le passage qui diffère. Toute autre forme donne `indisponible`. L'extrait n'est retenu que s'il figure dans la page, pour qu'aucun extrait inventé n'apparaisse.
- `VE` n'est pas une Tâche de `taches.toml` : `charger_prompt` construit une `Tache` interne et passe par `construire_messages` (AD-7).
- Le résultat est une liste synchrone d'évènements, sans flux poussé par `evaluate_js`. C'est plus simple, et pywebview appelle `js_api` hors du fil d'interface.

## À confirmer

- **À confirmer par Anaël :** l'URL vérifiée (publique, déjà citée) figure dans `termes` du journal, comme le demande la story. Le schéma du journal disait jusqu'ici « ni URL complète ».
- **À confirmer par Anaël :** le contrat du pont change par rapport au bouchon 12.5 (`verifier(url)`) et devient `verifier(reponse, sources)`. Ces deux valeurs restent locales : elles servent au choix de l'URL et à la comparaison.
- **À confirmer par Anaël :** les libellés des phrases d'`indisponible` (`PHRASES`) et le nouveau `origine = "verification"` des sources. `sources.js` l'affiche « Consultée le … » sans libellé d'origine propre, ce qui reste à traiter en 13.6.
- La qualité réelle du verdict avec le Modèle embarqué n'a pas été mesurée : GPU occupé, tests faits avec un faux LLM.

## Revue
