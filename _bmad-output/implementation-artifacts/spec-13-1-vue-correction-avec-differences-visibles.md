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

- `src/slmsp/app/differences.py` -- `calculer(avant, apres)` : segments `egal|ajout|suppression`, NFC, `difflib` sans autojunk, approche hiérarchique : phrases et lignes d'abord, puis mots (avec l'espace qui les précède) dans les seuls blocs modifiés. Marques combinantes, séquences emoji ZWJ et drapeaux restent collés. Espaces horizontales (dont NBSP) ignorées à la comparaison, un segment « égal » garde l'espacement de `avant` ; les retours à la ligne comptent. Coût borné : par bloc, préfixe et suffixe communs retirés, puis si le produit des tailles dépasse 25 000 000 (~5 000 éléments par côté) le bloc devient un bloc supprimé + un bloc ajouté.
- `src/slmsp/app/pont/redaction_outils.py` -- domaine `redaction_outils` (`differences`, refus `requete-invalide` au-delà de 500 000 caractères) ; branché dans `pont/__init__.py` (une ligne d'import, une entrée de domaine, le docstring).
- `js/vues/correction.js`, `css/correction.css` -- marques lisibles sans la couleur : soulignement (ajout), barré (suppression), texte `sr-only` « [ajout : … ] » / « [suppression : … ] », résumé `role=status` (« N ajouts, M suppressions. » ou « Aucune correction »).
- `js/vues/redaction.js` -- extension minimale : `rendreResultat(brut, zone, envoi, fin)` reçoit deux arguments de plus (compatible, LC les ignore).
- Tests : `tests/app/test_differences.py` (12), `tests/app/test_pont.py` (+1), `tests/app/ui/test_vue_correction.py` (7, `ui`) ; `test_socle*.py` ajustés (CO n'est plus « non disponible »).

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
- Anaël : seuil de repli grossier (25 000 000 par bloc modifié, environ 5 000 mots par côté sans ponctuation) ; au-delà, un seul bloc supprimé et un seul ajouté.
- Format réel des sorties de CO (le modèle ajoute-t-il un préambule ?) : à vérifier sur une sortie réelle ; hors périmètre (aucune génération).
- Ajouter `pont/redaction_outils.py` à la liste de la spec 12.5 §3.

## Revue

Commit relu : 49cf346. Second avis (Haiku) puis relecture Opus.

- medium, second avis : repli grossier dès ~1 000 mots, corrections dispersées noyées. Confirmé (mesuré), corrigé : diff hiérarchique phrases puis mots, limite portée à 25 000 000 par bloc. Mesures (30 corrections dispersées) : 3 000 mots 0,004 s avec ponctuation, 0,03 s sans ; 5 000 mots 0,005 s et 0,05 s ; 30 ajouts isolés dans chaque cas.
- medium, second avis : test de précision trivial. Confirmé, corrigé : test de 30 corrections dispersées sur 3 000 et 5 000 mots (ajouts isolés, reconstruction exacte, moins de 1 s) et test de latence sur un pire cas répétitif (6 000 mots, 5 mots distincts, moins de 3 s).
- low, second avis : marques combinantes et emoji ZWJ séparés. Corrigé : regroupement en graphèmes simples via `unicodedata` (`regex` n'est pas une dépendance du projet), avec test.
- low, second avis : NBSP remplacée par une espace vue comme correction. Corrigé : comparaison sans espaces horizontales, affichage inchangé, avec test.
- low, second avis : `.sr-only` dans `correction.css`. Écarté : absent du socle (seule définition du dépôt), conservé.
- low, relecture : le pire cas adversarial reste borné par `LIMITE_PRODUIT` (0,15 s à 2 000 éléments, 2,7 s à 7 000 avec 5 mots distincts) ; accepté.
