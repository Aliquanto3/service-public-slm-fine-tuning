---
title: 'Story 13.1 — Vue Correction avec différences visibles'
type: 'feature'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-8-vues-de-redaction-compte-rendu-et-langage-clair.md'
warnings: []
deferred: []
---

## Intent

**Problem:** la vue Correction (CO) affiche « non disponible » (FR-17, UX-DR13).

**Approach:** `correction.js` réutilise `monterRedaction` (12.8). À la fin d'une génération terminée, il demande les différences au pont (`redaction_outils.differences`, calcul Python par mots) et les rend par `textContent` (`<ins class="diff-insert">`, `<del class="diff-delete">`). Le presse-papiers reçoit toujours le texte corrigé brut.

## Code Map

- `src/slmsp/app/differences.py` -- `calculer(avant, apres)` : segments `egal|ajout|suppression`, NFC, `difflib` sans autojunk. Coût borné : préfixe et suffixe communs retirés, puis si le produit des tailles dépasse 4 000 000 le milieu devient un bloc supprimé + un bloc ajouté.
- `src/slmsp/app/pont/redaction_outils.py` -- domaine `redaction_outils` (`differences`, refus `requete-invalide` au-delà de 500 000 caractères) ; branché dans `pont/__init__.py` (une ligne d'import, une entrée de domaine, le docstring).
- `js/vues/correction.js`, `css/correction.css` -- marques lisibles sans la couleur : soulignement (ajout), barré (suppression), texte `sr-only` « [ajout : … ] » / « [suppression : … ] », résumé `role=status` (« N ajouts, M suppressions. » ou « Aucune correction »).
- `js/vues/redaction.js` -- extension minimale : `rendreResultat(brut, zone, envoi, fin)` reçoit deux arguments de plus (compatible, LC les ignore).
- Tests : `tests/app/test_differences.py` (8), `tests/app/test_pont.py` (+1), `tests/app/ui/test_vue_correction.py` (7, `ui`) ; `test_socle*.py` ajustés (CO n'est plus « non disponible »).

## Acceptation (état)

1. `diff-insert` / `diff-delete` lisibles sans la couleur. Fait (test des `text-decoration-line` calculés).
2. « Copier » : texte corrigé brut. Fait.
3. Textes identiques : « Aucune correction ». Fait.

## Auto Run Result

**Décisions prises seul :**
- Le bouchon `redaction_outils` est créé ici (13.1) et branché dans `Pont` : la spec 12.5 ne le déclarait pas encore (§3 à compléter).
- Les textes sont normalisés en NFC avant comparaison : les segments reconstruisent la forme NFC des textes, pas leur octets d'origine.
- Texte interrompu (`fin.raison != terminee`) : pas de différences (le reste de l'original apparaîtrait à tort supprimé). Texte brut seul.
- Échec du calcul : texte corrigé brut + « Les différences n'ont pas pu être affichées : voici le texte corrigé. »
- Libellés « Corriger », « Texte corrigé » et phrase d'aide : proposés par moi, sans exemple de texte (D1).
- Le texte d'origine vient de l'envoi mémorisé de la vue (`dernierEnvoi`), donc Régénérer compare au bon texte même si l'entrée a été modifiée.

## À confirmer

- Anaël : phrase d'aide, bouton « Corriger », libellés des résumés.
- Anaël : ajout de deux arguments à `rendreResultat` dans `redaction.js` (zone de 12.8, changement rétro-compatible).
- Anaël : seuil de repli grossier (4 000 000 = environ 2 000 mots par côté après retrait du préfixe/suffixe) ; au-delà, un seul bloc supprimé et un seul ajouté.
- Format réel des sorties de CO (le modèle ajoute-t-il un préambule ?) : à vérifier sur une sortie réelle ; hors périmètre (aucune génération).
- Ajouter `pont/redaction_outils.py` à la liste de la spec 12.5 §3.
