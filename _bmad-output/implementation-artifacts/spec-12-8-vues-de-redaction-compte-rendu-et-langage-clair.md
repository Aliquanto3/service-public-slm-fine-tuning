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

## Revue

Revue Opus 5.5 du commit 8671ba4, avec le second avis (Haiku). Corrections dans le commit de revue.

| Sév. | Source | Constat | Statut |
|---|---|---|---|
| medium | second avis | Sans vraie section, une ligne du corps (« Les termes… ont été conservés ») était prise pour la section et tronquait le corps | Corrigé : la section doit être la dernière partie, introduite par un intitulé (titre, gras ou « … : ») et suivie d'une liste à puces ou numérotée (ou de passages entre guillemets sur la même ligne) ; sinon rien n'est coupé. Tests : phrase du corps, phrase de clôture |
| medium | second avis | Envoi ou régénération LC pendant une génération CR : refus du pont, composeur réactivé et état global à `false` | Corrigé : refus local à la vue (« Une génération est en cours. », `role=status`), aucun appel au pont, état global intact. Détection par `generationEnCours` ajouté au contexte de vue (`app.js`) et par `generation:debut` d'une autre Tâche. 12.7 n'a pas ce cas (le composeur global bloque l'envoi) : aucune règle à reprendre, seul le traitement de `generation:erreur` est aligné. Test ajouté |
| medium | second avis | « Effacer » ignorait le retour `{ok:false}` de `nouvelle_conversation` | Corrigé : arrêt d'abord, puis lecture des deux retours ; un refus affiche « L'effacement n'a pas abouti côté assistant. Réessayez. ». Deux tests (refus, ordre) |
| low | second avis | `arreter` : résultat non lu | Corrigé (`exigerOk`) |
| low | second avis | Régénération refusée après édition : `dernierEnvoi` et `sale` incohérents | Corrigé : rétablis à l'état d'avant tant qu'aucun évènement n'a été reçu. Test ajouté |
| low | second avis | Phrase de clôture prise pour un passage | Corrigé (liste bornée aux puces/numéros ; une clôture après la liste annule la détection) |
| low | second avis | Décalage d'index avec « İ » | Corrigé : recherche par RegExp insensible à la casse, sans `toLowerCase`. Test ajouté |
| low | second avis | Regex `\s+$` quadratiques | Corrigé : `trimEnd` et rognage par boucle |
| low | second avis | `annoncer()` lisait tout le texte | Corrigé : « Rédaction terminée. » (ou interrompue) et nombre de passages signalés |
| low | second avis | `aria-label` sur une div sans rôle | Corrigé : `role="region"` |
| low | second avis | Infobulle lue deux fois | Corrigé : `aria-describedby` retiré (l'infobulle fait partie du contenu du passage) |
| low | second avis | Duplication `el` / `exigerOk` | Rejeté : ces utilitaires sont privés à `conversation.js` (12.7, fusionné) et à chaque vue ; les mutualiser demande un module commun et de toucher au code de 12.7, pour quatre lignes |
| low | second avis | Invite LC (« Les montants et les dates restent identiques. ») | Texte laissé : à valider par Anaël |

Limite connue (reportée) : si une génération d'une autre Tâche démarre avant le montage de la vue LC, la détection repose sur `etat.generation` (via `generationEnCours`), pas sur `generation:debut`. Les autres vues (12.7) n'ont pas ce garde local : leur envoi dépend du composeur global. À vérifier avec le vrai pont : un envoi LC pendant une génération CR doit afficher le refus local, sans réactiver le composeur.
