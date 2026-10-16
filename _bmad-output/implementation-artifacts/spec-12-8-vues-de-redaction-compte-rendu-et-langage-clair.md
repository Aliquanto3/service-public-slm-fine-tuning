---
title: 'Story 12.8 — Vues de rédaction Compte rendu et Langage clair'
type: 'feature'
created: '2026-10-16'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-7-vues-question-et-recherche-de-donnees.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-service-public-slm-fine-tuning-2026-10-11/DESIGN.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-service-public-slm-fine-tuning-2026-10-11/EXPERIENCE.md'
warnings: []
deferred: []
---

## Intent

**Problem:** les vues Compte rendu (CR) et Langage clair (LC) affichent « non disponible » (FR-13, FR-16, FR-38).

**Approach:** `js/vues/redaction.js` exporte `monterRedaction(conteneur, pont, {bus, tache}, options)`, volet de rédaction générique (Entrée à gauche, Résultat à droite) que l'Epic 13 réutilise avec ses `options` ; `monter` choisit la configuration CR ou LC d'après la Tâche. Le Résultat est rendu par `textContent` (jamais `innerHTML`).

## Boundaries & Constraints

**Always:** CSP `default-src 'self'` ; vouvoiement ; fixtures factices (`<texte-clair-1>`) ; refus du pont lu (`{ok:false}` rejeté puis `generation:erreur`), état rétabli ; annonce `aria-live` en fin de génération ; seule la vue qui a lancé la génération reçoit les évènements.

**Never:** toucher à `index.html`, au socle JS, à `app/pont/`, à `LC.md` (Q11) ni aux documents de décision.

## Code Map

- `js/vues/redaction.js` -- `monterRedaction` : compteur de mots, un seul bouton principal visible (Rédiger / Réécrire, puis Arrêter pendant la génération, puis Copier ; Rédiger revient si l'entrée change), résultat au fil de l'eau, `Progression` (« Texte long : je le traite en plusieurs parties. » puis l'`etape` du Harnais, ex. « Partie 2 sur 4 »), Régénérer (rejoue le dernier envoi), Effacer (`nouvelle`), Copier le texte brut final avec `inline-confirmation` 3 s, `copier-dernier`.
  - Points d'extension pour l'Epic 13 : `controles` (éléments ajoutés au volet Entrée), `construireEnvoi(texte)`, `rendreResultat(brut, zone)` (renvoie le texte à copier), `dir` (RTL), `action`, `invite`, `etiquetteEntree`, `etiquetteResultat`.
- `js/composants/passages-signales.js` -- extraction tolérante (Q11) : dernière ligne d'introduction reconnue (« Passages/Termes/Expressions… conservés/gardés/laissés/signalés/tel quel », avec ou sans `#`, `**`, `:`), passages pris en puces, lignes simples, ou entre « » ; première occurrence de chaque passage surlignée dans le texte réécrit (`flagged-passage`, `tabindex=0`, infobulle `role=tooltip` au survol et au focus, Échap la ferme). La section d'origine reste affichée en note sous le texte.
- `css/redaction.css` -- deux volets égaux, empilés sous 1 200 px.
- `tests/app/ui/test_vue_redaction.py` (18 tests Edge) ; `test_socle.py` et `test_socle_statique.py` ajustés (CR/LC ne sont plus « non disponible »).

## Acceptation (état)

1. Plus de 6 000 mots : l'`etape` de chaque `Progression` s'affiche (« Partie i sur n », « Fusion des parties »), puis le résultat fusionné. Fait (le seuil est celui du Harnais, pas de l'interface).
2. Passages surlignés avec infobulle au survol et au focus ; sans section reconnue, texte normal sans erreur. Fait.
3. « Copier » : texte brut final ; `inline-confirmation` effacée après 3 s. Fait.
4. Volets empilés sous 1 200 px. Fait.

## Auto Run Result

**Décisions prises seul :**
- Copier en Langage clair copie le texte réécrit **sans** la section de signalement, quand elle est reconnue (c'est un commentaire sur le texte, pas du texte à envoyer au destinataire) ; sans section reconnue, le texte entier.
- Phrase d'aide du Compte rendu : celle du document UX. Phrase d'aide du Langage clair, libellés de volets (« Entrée », « Compte rendu », « Texte en langage clair »), « Texte long… » et « Le résultat s'affichera ici. » : proposés par moi (D1 : aucun exemple de texte, seulement des textes d'interface).
- Régénérer rejoue l'envoi mémorisé de cette vue par `envoyer` (pas `regenerer` du pont, qui rejoue le dernier envoi toutes Tâches confondues, cf. 12.7). Un refus du pont laisse le résultat précédent en place.
- Ctrl+Entrée lance le traitement depuis le volet Entrée (Entrée seule garde son sens : retour à la ligne).
- Pas de `Affiner` ni de Retour (pouce) : hors critères de la story ; `.resultat-actions` est prêt à les accueillir.
- Les évènements `Fin(longueur)` et `Avertissement` s'affichent en notes sous le Résultat.

## À confirmer

- Anaël : phrase d'aide du Langage clair et libellés des volets ; texte « Texte long : je le traite en plusieurs parties. » (repris du document UX, flux 3).
- Anaël : la copie du Langage clair exclut-elle bien la section de signalement ?
- Format réel de la section finale de LC : la règle (Q11) est calée sur la consigne de `LC.md`, pas sur des sorties réelles ; à relire sur une sortie du vrai modèle (un test réel est hors périmètre : pas de génération).
- « Affiner » (UX) et le Retour : stories ultérieures.
- Le pont 12.5 transmet le seul dernier message `user` ; pour LC la consigne de l'Agent (emplacement `consigne`) n'a pas de champ dédié dans cette vue.
