# Revue — story 17.4 « Mode hybride dans l'application »

Branche `story/17-4-mode-hybride`, rebasée sur `main` (6162de0). Revue Opus avec la liste du second avis et les décisions de l'orchestrateur ; passe Edge Case Hunter.

## Constats

| # | Sévérité | Constat | Suite |
|---|---|---|---|
| 1 | medium | Clé liée à l'`id` seul : changer l'URL ou le preset d'une entrée renvoyait la clé enregistrée vers le nouvel hôte (démarrage et test de connexion). | Corrigé : la clé est chiffrée avec `{cle, hote, preset}` (`CoffreCle.etat`, `lire(hote=, preset=)`). Le démarrage ne lit que les clés liées (`lecteur_cles`). `ecrire("fournisseurs_externes")` efface la clé d'une entrée dont l'hôte ou le preset a changé, et `cle_enregistree` repasse à faux. `tester_modele_externe` rend `cle-autre-hote` sans requête. `enregistrer_cle(id, cle, valeurs)` lie la clé aux valeurs du formulaire, à défaut à l'entrée enregistrée. |
| 2 | low | `modele_repondant` des Retours non validé. | Corrigé : `^(local\|externe):\S+$`, `MAX_MODELE` caractères au plus, sinon ignoré (`modele_repondant_valide`). |
| 3 | low | La vérification FR-12 relançait une cascade : elle pouvait partir vers un autre fournisseur que celui de la réponse (amendement 6). | Corrigé : le front transmet `modele_repondant` à `verification.verifier`, puis `Verificateur` appelle `ClientHybride.pour(modele)`. Une réponse `local:` est vérifiée en local. Une réponse `externe:` est vérifiée par ce seul fournisseur : s'il échoue, le verdict est « indisponible », sans repli sur un autre hôte. Un modèle inconnu relance la cascade, journalisée sans contenu. C'est la solution propre : le choix suit la réponse, sans état partagé entre échanges. |
| 4 | low | Une clé saisie non enregistrée était perdue au déplacement ou au retrait d'une entrée (liste redessinée). Le JSON des paramètres non enregistré s'affichait périmé alors que la valeur envoyée était la nouvelle. | Corrigé : la saisie est gardée en mémoire de la page (`entree._cle`, `entree._parametres`) et reportée par `id` après un enregistrement. Un retrait n'emporte que la saisie de l'entrée retirée. Les paramètres libres sont vidés quand on passe à un preset qui les refuse. |
| 5 | info | `modele_repondant: local:<slug>` sur chaque Fin, même sans fournisseur externe. | Accepté tel quel (exigence 8). |
| 6 | info | Edge Case Hunter : clé absente des journaux, des exceptions (le pont ne journalise que le type), du front (clé jamais relue), de l'export et du bandeau (codes courts). Profil `modele-externe` sans Liste blanche, Liste blanche intacte, mode hors ligne refusé. Réglage vide : rien n'est construit. Cascade avant le premier jeton. PyInstaller : `slmsp.inference` et `slmsp.app` sont collectés en paquets, et l'app n'importe ni `slmsp.evaluation` ni `slmsp.budget`. Front : `textContent`, HTTPS validé côté pont, identifiants sûrs. | Rien à corriger. |

## Vérifications

- Tests ciblés : `tests/app`, `tests/net`, `tests/harness`, `tests/inference`, `tests/evaluation/test_modele_distant.py`, `tests/test_architecture.py`, `tests/test_garde_reseau.py`, tous verts. Interface (`-m ui`) : paramètres, vérification, mode, réponse et conversation, verts ; un dépassement de délai isolé au montage dans `test_vue_verification`, vert à la relance.
- `ruff check` et `ruff format --check` verts. Le contrôle rapide ne se lance pas dans le worktree, qui n'a pas de venv (`uv` ne trouve ni `ruff` ni `pytest`) ; ses étapes ont été passées à la main avec le venv principal.
