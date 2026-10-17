---
title: 'Story 13.6 — Bouton « Vérifier en ligne » dans la vue Question (FR-12, UX-DR24)'
type: 'feature'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-13-5-verification-en-ligne-page-officielle.md'
warnings: []
deferred:
  - 'Qualité réelle du verdict et résistance à une page piégée avec le Modèle embarqué (GPU) : à mesurer (report 13.5).'
  - 'La page vérifiée rejoint le panneau Sources mais n''est pas enregistrée dans l''Historique (la conversation enregistrée garde ses sources d''origine).'
---

## Intent

**Problem:** l'Agent veut lancer lui-même, jamais automatiquement, la vérification d'une réponse Question sur la page officielle citée (FR-12, Q7).

**Approach:** le pont 13.5 est branché dans l'application, et la vue Question affiche sous chaque réponse terminée un bouton secondaire « Vérifier en ligne ». Le bouton n'existe (absent du DOM) qu'en Mode connecté, quand la réponse cite `[n]` une source d'origine `index` à URL https. Le résultat (verdict, date de consultation, extrait) s'affiche sous la réponse et la page rejoint le panneau Sources.

## Code Map

- `src/slmsp/app/principal.py` : `construire_verificateur(assemblage)` rend `Verificateur(passerelle, llm, dans_index=<IndexLocal.contient_url>, config=config.verification)` ; `Demarrage` le passe à `Pont(verificateur=…)`. La passerelle est celle de l'assemblage (Mode inclus) : le hors ligne forcé prime. Sans Index, `dans_index` rend toujours `False` (aucune source retenue, rien ne sort). Sans passerelle ou LLM : `None` (pont `non-implementee`).
- `src/slmsp/app/pont/__init__.py` : paramètre `verificateur` de `Pont`, transmis à `PontVerification`.
- `src/slmsp/app/ui/js/vues/verification.js` : `creerVerification` (bouton, état « en cours », encart, annonce, focus, ajout de la page aux sources de la réponse), `sourceVerifiable`, `texteVerdict`. `monter` (ancre transverse) laisse l'ancre vide.
- `src/slmsp/app/ui/js/composants/conversation.js` : option `verification`, un bloc par tour rafraîchi par `majBoutons` et `appliquerMode` (évènement `mode:change`, état `mode.etat`).
- `src/slmsp/app/ui/js/vues/question.js` : active l'option. `composants/sources.js` : libellé d'origine « Vérifiée en ligne ». `css/verification.css`.
- Tests : `tests/app/test_principal.py` (câblage, dont `lancer()` hors ligne forcé : verdict `indisponible`, journal `bloquee-mode` seul), `tests/app/ui/test_vue_verification.py` (marqué `ui`, 10), `tests/app/ui/test_socle_statique.py` (vue réalisée).

## Comportement

- Pas de bouton : hors ligne (y compris forcé), Mode inconnu, réponse en cours, interrompue ou en échec, aucune source de l'Index citée par `[n]`.
- Clic : bouton désactivé (`aria-busy`), encart `role="status"` « Vérification en cours… », puis verdict. Si le Mode passe hors ligne pendant l'attente, tout est retiré et le résultat tardif est ignoré. Une réponse régénérée efface le résultat.
- `concordant` : « Vérifié sur [titre] le [date] : concordant ». `difference` : callout-warning « Différence relevée : [phrase] » (phrase = libellé fixe côté Harnais) avec l'extrait dans un `details`. `indisponible` : callout-warning avec la phrase fixe. Refus ou exception du pont : callout-warning « La vérification n'a pas pu être lancée. » Aucun cas ne bloque la saisie.
- Accessibilité : verdict annoncé par la région `aria-live` du socle, focus placé sur l'encart (`tabindex=-1`, anneau de focus visible).
- Tout texte passe par `textContent` ; aucun `innerHTML` (test dédié et test d'un contenu piégé).

## Auto Run Result

**Décisions prises seul :**
- Le brouillon de consigne citait `Verificateur(passerelle, llm, mode, …)` : après la revue 13.5, `Verificateur` n'a plus de `mode` (le Mode est celui de la passerelle). Câblage fait avec la signature réelle.
- Sans Index (vector store absent), `dans_index` rend `False` plutôt que `None` : sans recoupement, aucune source n'est retenue.
- Réponse interrompue : pas de bouton (la réponse est partielle).
- Le bloc est monté par la vue Question elle-même (`creerVerification`) ; l'ancre `ancre-verification` du socle reste vide.
- Pas de republication de `conversation:tours` après la vérification, pour ne pas ré-enregistrer l'Historique (voir report).

## À confirmer

- **À confirmer par Anaël :** libellés d'interface proposés, tous des textes fixes d'interface (pas de données d'entraînement) : « Vérifier en ligne » (bouton, repris de la story), « Vérification en cours… », « Vérifié sur [titre] le [date] : concordant » et « Différence relevée : [phrase] » (repris de la story), « Passage de la page » (résumé de l'extrait), « La vérification n'a pas pu être lancée. » (refus du pont), « Vérifiée en ligne » (origine de la source dans le panneau Sources), « la page officielle » (titre absent).
- **À confirmer par Anaël :** une différence est signalée par un callout-warning (pas de style danger), sans icône ; la concordance par un encart à filet vert.
- **À confirmer par Anaël :** la page vérifiée n'entre pas dans l'Historique enregistré.
- Le verdict réel avec le Modèle embarqué n'est pas mesuré (faux LLM, aucun réseau).
