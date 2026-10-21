---
title: 'CT : prompts d''entraînement alignés et garde-fou anti-boucle (story 16.3)'
type: 'feature'
created: '2026-10-21'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/planning-artifacts/stories-epic-16-derive-et-confirmation.md'
  - '{project-root}/_bmad-output/implementation-artifacts/diagnostic-d0.md'
warnings: []
deferred:
  - summary: 'Build v21 non produit : aucune formulation de consigne de libellés d''origine non-Claude vérifiable (D1)'
    evidence: 'config/prompts/ (taches, generateur, juge-donnees) sans consigne de libellés ; « avec exactement ces libellés » vient des items dev1/v1.x rédigés par Claude (eval/construction/dev1/README.md) et serait de plus une fuite du Jeu ; [alignement.consignes_agent] de config/donnees.toml est rédigé par Claude'
    severity: 'bloquant pour 16.6'
  - summary: 'Application : pas d''avertissement affiché pour Fin(raison="boucle")'
    evidence: 'src/slmsp/app/ui/js/composants/reponse.js ne traite que « longueur » ; texte d''interface à valider par Anaël'
---

<intent-contract>

## Intent

**Problem:** 13/20 sorties CT de v18 bouclent dans le bloc d'en-tête jusqu'à 1024 tokens (D0 (b)) ; 20/20 consignes CT d'évaluation imposent des libellés, 0/30 prompts CT d'entraînement.

**Approach:** (1) garde-fou anti-boucle déterministe dans le Harnais (`[anti_boucle]` de `config/harnais.toml`), commun à l'évaluation et à l'application ; (2) commande `data build --aligner-ct` qui ajoute aux prompts CT une consigne de libellés fournie de l'extérieur, libellés extraits de la cible Mistral de chaque ligne.

## Boundaries & Constraints

**Always:** aucune pénalité de répétition ; sortie non bouclante relayée à l'identique (mêmes `Jeton`, même ordre) ; coupure avant la ligne de trop, `Fin(raison="boucle")` ; cibles jamais réécrites ; formulation et origine consignées au MANIFEST et revérifiées au chargement.

**Never:** formulation rédigée par Claude dans le code, la config ou les tests (fixtures `<formulation-factice>`) ; incrément de la version du harnais (porté par 16.2) ; build v21 réel par un sous-agent.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ligne répétée | même ligne non vide > `repetitions_ligne_max` | texte jusqu'au début de la ligne de trop, `Fin(boucle)` | flux amont fermé |
| Boucle sans saut de ligne | part de 4-grammes répétés > seuil sur la fenêtre | coupure au début de la ligne en cours (jamais avant l'émis) | — |
| Lignes sans alphanumérique | `| --- |`, `***` répétés | ignorées | — |
| Section absente | `[anti_boucle]` absent | garde-fou inactif | — |
| Alignement | ligne CT avec libellés | `Consigne :\n<consigne> <formulation rendue>\n\n…` | ligne CT sans « Consigne : » → `ManifesteInvalide` |
| Refus | formulation sans `{libelles}`, multi-lignes, origine vide, jeu déjà aligné/restreint/sélectionné, aucune ligne CT | aucune version créée | `ManifesteInvalide` (CLI : USAGE) |

</intent-contract>

## Code Map

- `src/slmsp/harness/anti_boucle.py` -- `DetecteurBoucle` (incrémental, pur), `borner_boucles` (flux), `point_de_coupure` (rejeu)
- `src/slmsp/harness/config.py` -- `ConfigAntiBoucle`, champ `anti_boucle`
- `src/slmsp/harness/service.py` -- `_flux` enveloppe le traitement dans `borner_boucles`
- `src/slmsp/core/evenements.py` -- `Fin.raison` admet `boucle` ; `taches/compte_rendu.py` : gravité 1
- `config/harnais.toml` -- section `[anti_boucle]` (actif, 12 lignes, fenêtre 300 mots, 4-grammes, 0,8 ; seuils de la revue)
- `src/slmsp/core/alignement_ct.py` -- extraction des libellés, alignement, vérification
- `src/slmsp/data/alignement_ct.py`, `src/slmsp/cli/data.py` -- `data build --aligner-ct`
- `src/slmsp/core/schemas/entrainement.py`, `src/slmsp/train/chargement.py` -- bloc `alignement_ct`, `controler_alignement_ct`
- `outils/rejouer_anti_boucle.py` -- rejeu hors ligne sur un run `eval-generation`

## Verification

- `tests/harness/test_anti_boucle.py` (33), `tests/data/test_alignement_ct.py` (24).
- Rejeu (lecture seule) : `uv run python outils/rejouer_anti_boucle.py <run>`.

## Auto Run Result

- **Statut : partiel.** Garde-fou livré et calé ; commande de build livrée et testée sur fixtures. **Build v21 non produit** (D1) : aucun gabarit d'origine non-Claude vérifiable ne porte une consigne de libellés (recherche : `config/prompts/taches`, `generateur`, `juge-donnees`, `config/donnees.toml`, items du Jeu). La formulation des items (« avec exactement ces libellés : … ») est rédigée par Claude et appartient au Jeu d'évaluation. **À confirmer par Anaël** : fournir la formulation (une ligne avec `{libelles}`) et son origine.
- Contrôle à blanc en mémoire (rien écrit) sur v18 avec une formulation factice : 30/468 lignes modifiées, toutes CT.
- **Rejeu** (seuils retenus) : v18 `20261020-175424-ft-minicpm5-2b-35b9` : CT 13/20 coupées (les 13 `longueur`), plus CR-517, CR-518, NR-518 (toutes `longueur`) ; Baseline `20261020-163743-minicpm5-2b-f9fc` : 0/160.
- **Décision (à confirmer par Anaël)** : seuils 8 lignes et 0,95, remplacés à la revue par 12 lignes, 300 mots, 0,8 (voir Revue). Avec 6 lignes ou 0,6, la Baseline CR-515 (vraie boucle à 1024 tokens : deux lignes répétées 8 et 7 fois) serait coupée aussi ; le critère « aucune sortie de la Baseline » a été appliqué à la lettre.
- Décision : sur coupure, `Fin` sans `usage` ni `urls_inventees` (le `Fin` du modèle n'est pas reçu) ; `generation.tronquee` vrai pour `longueur` et `boucle` (revue).
- Décision : un évènement non `Jeton` (Sources, appel d'outil) libère les jetons retenus sans contrôle de la ligne en cours.
- Commande à lancer par l'orchestrateur, formulation validée par Anaël : `slmsp.exe data build --aligner-ct --depuis 20261020-125334-nettoyage-440e --formulation-fichier <fichier> --origine-formulation "<origine>"`.

## Revue

Rebase sur main (16.2 fusionnée, 1428794) : conflits de `config/harnais.toml` et `harness/config.py` résolus en gardant `[dedoublonnage]`, `[question]` et `[anti_boucle]` ; version du harnais inchangée (2).

- high · corrigé · Seuils (8 lignes, 120 mots, 0,95) : faux positifs sur les emplacements répétés d'un courrier ou d'un formulaire (10 × un champ d'adresse, 12 × un champ à pointillés). Recalés : 12 lignes, fenêtre 300 mots, 4-grammes, part 0,8. Rejeu (lecture seule) : v18 `20261020-175424-ft-minicpm5-2b-35b9` 13/13 boucles CT coupées (CT-511 et CT-518, lignes vues 12 fois, par les n-grammes à 0,90 et 0,88), plus CR-517, CR-518, NR-518 (toutes `longueur`) ; Baseline `20261020-163743-minicpm5-2b-f9fc` 0/159 ; Qwen3.6-27B `20261021-092032-distant-qwen3.6-27b-3ae2` 0/161 ; Mistral Small `20261021-112139-distant-mistral-small-mistral-0b86` 0/160. Aucune fenêtre de 120 à 250 mots ne sépare CT-518 de la boucle CR-515 de la Baseline (0,74 contre 0,68 sur 120 mots) ; sur 300 mots, CR-515 tombe à 0,72. Formulaire factice (emplacements, pointillés, tableau) non coupé avec la config du projet : test. Limite : avec `max_tokens = 400` de l'application, la fenêtre de 300 mots est rarement remplie ; seul le critère des lignes y agit.
- medium · corrigé · Séparateurs de tableaux Markdown, lignes de `-`, de `|` ou de points comptés par les n-grammes : les mots sans caractère alphanumérique sont ignorés (les lignes l'étaient déjà) ; tests.
- medium · corrigé · Interface : `Fin(raison="boucle")` sans avertissement ; `reponse.js` et `vues/redaction.js` affichent « Réponse coupée : répétitions détectées », comme pour `longueur`. Pas de test d'interface : aucun n'existe pour `longueur`.
- medium · corrigé · `evaluation.generation.tronquee` vrai pour `longueur` et `boucle` (`RAISONS_TRONQUEES`), docstrings alignées ; test.
- medium · corrigé · Alignement CT : origine de la formulation libre. Liste fermée `[alignement_ct] origines_admises = []` de `config/donnees.toml` (`AlignementCtDonnees`) ; refus (`ManifesteInvalide`, CLI : USAGE, aucune version) tant qu'Anaël n'y a rien inscrit ; tests (liste vide, origine absente, config du projet, CLI).
- medium · corrigé · Ligne de trop émise quand la ligne finit par des blancs ou par `\r` (CRLF) : la ligne partielle n'était comparée aux clés saturées que sans ses blancs de tête. Comparée sans blancs de bord : la coupure est désormais exacte au début de la ligne ; la docstring dit le comportement réel (coupure exacte pour les lignes ; pour les n-grammes, au plus tôt au texte déjà émis, ce critère ne retenant aucun jeton) ; tests CRLF et espaces.
- low · corrigé · Flux épuisé sans `Fin` ni `Erreur` : les jetons retenus étaient perdus ; rendus en fin de flux ; test.
- low · corrigé · Périmètre documenté dans le module : Harnais seul (évaluation et application), pas `data/candidats.py`, `data/preferences.py`, `benchmarks/moteurs/llm.py` (appels directs au `LlmPort`, raison `boucle` jamais reçue).
- low · rejeté · Évènement non `Jeton` (Sources, appel d'outil) qui libère les jetons retenus sans contrôle : décision consignée, sans cas réel (les Sources précèdent le texte).
- D1 · rien à corriger · Fixtures en jetons factices (`<…-factice>`), y compris le formulaire de test (structure seule, aucun texte rédigé) ; aucune formulation dans le code ni la config ; build v21 toujours bloqué (formulation et origine à fournir par Anaël, puis à inscrire dans `origines_admises`).
