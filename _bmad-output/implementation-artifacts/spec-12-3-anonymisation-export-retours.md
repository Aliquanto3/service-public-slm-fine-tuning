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

## Revue

- medium, second avis : espaces insécables (U+00A0, U+202F) non reconnues (NIR, IBAN, téléphone, adresse, civilité, Prénom Nom) : corrigé. `anonymiser` ramène ces espaces à l'espace ASCII avant détection (même longueur, positions conservées) ; le texte exporté contient donc des espaces ordinaires. Tests ajoutés pour chaque motif.
- medium, second avis : `prenoms.txt` sans prénoms, donc détection Prénom Nom inactive en production : corrigé côté visibilité. `Export.avertissements` et l'aperçu portent « détection des prénoms inactive : fichier INSEE absent » ; le fichier écrit n'est pas modifié. Testé (liste vide, liste présente, fichier embarqué du dépôt). Rien n'est téléchargé. Décision à prendre par Anaël : ajouter la sous-commande `fetch prenoms` et inscrire l'hôte data.gouv/INSEE à la liste blanche (voir « À confirmer », point 1).
- low, second avis : numéro de dossier `00…` pris pour un téléphone : corrigé. Un `00` sans séparateur n'est masqué que si un indicatif pays plausible suit (liste courte, longueur bornée ; `001`/`007` exigent 13 chiffres). Avec séparateurs, le motif international est inchangé.
- low, second avis : « 2 place … 12345 euros » pris pour une adresse : corrigé. Un code postal suivi d'une unité monétaire (€, $, %, euro, EUR, dollar) n'est plus accepté.
- low, second avis : IBAN avec insécables : corrigé par la normalisation du premier point (testé).
- low, second avis : corpus de faux positifs trop étroit : corrigé. Cas insécables dans les montants, dossiers `00…`, « n place … euros » (200 phrases aléatoires, 0 modifiée hors normalisation des espaces).
- Limite connue, reportée : un `00` collé avec un indicatif rare hors liste n'est pas masqué ; l'aperçu reste le filet.

## Suite du 2026-10-17 : `slmsp fetch prenoms` (décision d'Anaël)

- Le point 1 de « À confirmer » est tranché : accord. `slmsp fetch prenoms` télécharge `https://www.insee.fr/fr/statistiques/fichier/7633685/nat2022_csv.zip` (fichier national 1900-2022, Licence Ouverte 2.0, fiche data.gouv `5bf42c958b4c4144b0110ce8`), par la passerelle, profil `outillage`, règle `insee-prenoms` (GET seul, ce chemin seul, `config/reseau.toml`).
- URL, SHA-256 (`c13b45e7…b81d`) et taille (2 571 727 octets) sont épinglés dans `config/outillage.toml` `[prenoms-insee]` ; le SHA a été calculé à la première lecture (l'INSEE n'en publie pas). Source inscrite au registre des licences (`insee/fichier-des-prenoms`).
- `prenoms.txt` est généré par `fetch/prenoms.py` avec `prenoms_depuis_csv_insee` (au moins 20 naissances, au moins 3 lettres) : 36 905 prénoms, environ 285 Ko, versionné. Aucun prénom écrit à la main. La détection Prénom Nom est donc active (l'avertissement ne s'affiche plus).
- `fetch` ne peut pas importer `app` (règle de couche) : la CLI injecte `prenoms_depuis_csv_insee`.
- Report : la liste contient des prénoms rares qui sont aussi des mots courants (seuil de 20 naissances) ; la règle « prénom suivi d'un mot capitalisé » limite les faux positifs, l'aperçu reste le filet.
