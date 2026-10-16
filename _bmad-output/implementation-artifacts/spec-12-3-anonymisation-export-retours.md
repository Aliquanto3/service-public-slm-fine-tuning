---
title: "Story 12.3 — Anonymisation de l'export des Retours"
type: 'feature'
created: '2026-10-16'
status: review
baseline_revision: 'b839f3b'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/planning-artifacts/epics.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** l'Agent doit pouvoir transmettre ses Retours sans exposer d'usager (FR-20).

**Approach:** `app.anonymisation.anonymiser(texte) -> (texte_masque, comptes)` (regex et heuristique, bibliothèque standard seule, Q5) ; `app.export_retours` construit le JSON `retours-assistant-AAAA-MM-JJ.json` depuis `Stockage.lister_retours()`, fournit l'aperçu, et n'écrit qu'avec `confirme=True`.

## Boundaries & Constraints

**Always:** remplacement par `[masqué]` ; NIR et IBAN masqués seulement si la clé (NIR) ou le modulo 97 (IBAN) est valide ; l'identifiant interne du Retour n'est pas exporté ; D1 : fixtures aléatoires ou factices.

**Never:** réseau, modèle (spaCy, GLiNER), nouvelle dépendance, écriture avant confirmation, liste de prénoms écrite à la main.

## I/O & Edge-Case Matrix

| Scénario | Comportement |
|---|---|
| Clé NIR ou IBAN invalide | texte conservé |
| IBAN suivi d'un mot en majuscules | seul l'IBAN valide est masqué |
| `prenoms.txt` vide ou absent | civilités seules ; pas d'erreur |
| Prénom suivi d'un mot en minuscules, ou prénom seul | conservé |
| Export sans confirmation | `SlmspError`, dossier non créé |

</intent-contract>

## Code Map

- `src/slmsp/app/anonymisation.py` : motifs, `nir_valide`, `iban_valide`, `lire_prenoms`, `prenoms_depuis_csv_insee`.
- `src/slmsp/app/export_retours.py` : `construire_export`, `apercu`, `ecrire`.
- `src/slmsp/app/ressources/prenoms.txt` : **commentaires seulement** (voir « À confirmer »).
- `tests/app/test_anonymisation.py`, `tests/app/test_export_retours.py`.

## Verification

- `uv run pytest -q --tb=short tests/app` : verts. Faux positifs mesurés sur 500 phrases aléatoires (montants, dates, articles, dossiers) : 0/500.

## Auto Run Result

- Décisions : (0) l entrée au registre des licences est reportée à l ajout du fichier (le test `test_registre_reel_charge` fige la liste des identifiants) ; (1) la passerelle `fetch` n'accepte aujourd'hui que des dépôts Hugging Face (`url_hf`) : le CSV INSEE n'est pas téléchargé et `prenoms.txt` ne contient que des commentaires, sans erreur ; (2) l'heuristique des noms masque « Prénom Nom » (prénom capitalisé suivi d'un mot à majuscule initiale) et « NOM Prénom » ; la civilité masque les 1 à 3 mots capitalisés qui suivent ; (3) téléphone international : `+` ou `00`, 8 à 15 chiffres ; (4) l'export masque question, réponse, commentaire et sources (récursif) ; (5) `prenoms_depuis_csv_insee` ne retient que les prénoms de plus de 2 lettres et d'au moins 20 naissances cumulées, pour limiter les faux positifs.
- Reports : branchement dans la vue Retours (aperçu, choix de l'emplacement) en 12.x.

## À confirmer (par Anaël)

1. **Téléchargement du fichier INSEE** : il faut étendre la passerelle `fetch` (sous-commande `prenoms`, URL data.gouv/INSEE + SHA-256 épinglés dans `config/`), puis générer `prenoms.txt` via `prenoms_depuis_csv_insee` et inscrire le SHA-256 au registre. Aucune commande de fetch n'existe encore pour cela. Accord pour l'ajouter ?
2. Seuil de 20 naissances et exclusion des prénoms de moins de 3 lettres (compromis rappel / faux positifs).
3. L'heuristique laisse passer un prénom isolé et un nom sans prénom ni civilité : l'aperçu reste le filet (Q5).
