---
title: 'Story 13.4 — Vue Traduction (cinq langues, arabe en RTL)'
type: 'feature'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-13-2-vue-resume-a-trois-longueurs.md'
warnings: []
deferred: []
---

## Intent

**Problem:** la vue Traduction (TR) affiche « non disponible » (FR-18, UX-DR15, Q9).

**Approach:** `traduction.js` réutilise `monterRedaction` (12.8, non modifié) avec deux sélecteurs (langue source, langue cible) et un bouton « Inverser ». L'entrée envoyée est `{langue_source, langue_cible, texte}` avec les noms français du banc (`benchmarks/moteurs/traduction.py`, `LANGUES`), clés du gabarit `TR.md`. Les langues viennent de `config/application.toml` via la nouvelle méthode `reglages.langues_traduction` du pont ; le français est toujours proposé en plus. Retirer l'arabe = une ligne de config. Pont en échec : français seul, message d'erreur, « Traduire » désactivé (revue). Les deux sélecteurs ne sont jamais identiques (choisir la langue de l'autre les échange). Un changement de langue après un résultat ramène « Traduire » (Régénérer rejouerait les anciennes langues). Arabe : saisie (langue source) et sortie (langue cible) portent `lang="ar"` `dir="rtl"`, `unicode-bidi: isolate`, contenu par `textContent`. Mention affichée et ajoutée à la copie après toute traduction terminée.

## Code Map

- `js/vues/traduction.js`, `css/traduction.css` ; `app/pont/reglages.py` (+ `langues_traduction`) ; `tests/app/ui/test_vue_traduction.py` (8, `ui`), `tests/app/test_pont_reglages.py` (+1) ; `test_socle.py` et `test_socle_statique.py` : `TR` marqué réalisé.

## Auto Run Result

**Décisions prises seul :**
- Noms de langue en français (« anglais », « arabe »…) dans l'entrée, comme le banc, plutôt que des codes ISO : mêmes conditions que la mesure.
- Ajout minimal d'une méthode au pont `reglages` (aucun autre canal ne livre la config à l'interface).
- Pas de « détecter la langue » (le gabarit le permet, non demandé).
- Libellés proposés : « Traduire », « Langue source », « Langue cible », « Inverser » (aria « Inverser les langues »), titre « Traduction », invite « Collez le texte à traduire, puis choisissez les langues. La traduction est automatique : relisez-la avant de l'envoyer. », mention « Traduction automatique, à vérifier avant envoi » (imposée par la story).

## À confirmer

- Les libellés ci-dessus (à valider par Anaël).
- Noms français vs codes dans l'entrée TR : aligné sur le banc ; le jeu gelé n'a pas de TR à vérifier ici.
- (Résolu en revue : plus de repli sur les cinq langues.)
- Conflit probable avec 13.3 sur `VUES_REALISEES` et la tuple de `test_socle.py` (ajout d'un élément chacun).
- Rendu RTL réel (WebView2 avec police arabe) et décision Q9 à la Baseline : non vérifiés ici (Edge, chaînes factices).

## Revue

- medium, second avis : repli codé en dur (arabe revenait si le pont échouait) ; corrigé : français seul, message, « Traduire » désactivé (`peutEnvoyer`), aucune liste avant la réponse du pont ; `test_echec_du_pont_...`.
- medium, second avis : la configuration acceptait tout code ISO ; corrigé : `LANGUES` déplacé dans `core/langues.py` (source unique, le banc l'importe), validation de `langues_traduction` restreinte ; tests `["it"]`, `["en","zh"]`.
- low, second avis : configuration `["fr"]` sans cible ; corrigé : message et « Traduire » désactivé.
- low, second avis : filtre `langues.filter` sans contrôle ; corrigé : seules les langues connues (`NOMS`) sont retenues.
- Reporté : `NOMS` (libellés) reste dupliqué côté JS (table d'affichage) ; à aligner si une langue est ajoutée à `core/langues.py`.
