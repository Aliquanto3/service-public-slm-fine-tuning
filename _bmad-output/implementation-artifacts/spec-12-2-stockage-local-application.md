---
title: "Story 12.2 — Stockage local de l'application"
type: 'feature'
created: '2026-10-16'
status: review
baseline_revision: 'bb3fbe6'
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

**Problem:** l'application n'a aucun stockage : conversations, Retours, réglages et journal de ses Requêtes sortantes doivent rester sur le poste, dans le profil, et être supprimables (FR-4, NFR-4).

**Approach:** `app.stockage` ouvre un unique SQLite (`%LOCALAPPDATA%\AssistantSP\assistant.sqlite`, WAL, `user_version = 1`) via `core.var.ouvrir_sqlite`. `Stockage` porte conversations, Retours et réglages ; `JournalApplication` implémente le port `JournalRequetes` (purge à 30 jours glissants).

## Boundaries & Constraints

**Always:**
- `app.stockage` est le seul propriétaire de la base (AD-23). Aucun import de `cli` ni de pipeline.
- Suppression : ligne effacée tout de suite ; contenu gardé en mémoire 5 s pour `annuler_suppression` ; `PRAGMA secure_delete = ON` pour que l'effacement soit physique.
- Version de schéma inconnue : `SlmspError`, base non modifiée.
- D1 : aucun contenu rédigé ; tests avec chaînes aléatoires.

**Never:** réseau, appel d'API, écriture de réglage hors liste (`hors_ligne_force`, `taille_texte`, `fenetre`, `plus_deplie`).

## I/O & Edge-Case Matrix

| Scénario | Comportement |
|---|---|
| `annuler_suppression` à moins de 5 s | conversation restaurée |
| idem après 5 s, ou conversation inconnue | `False`, rien n'existe |
| Journal : entrée de plus de 30 jours | purgée à l'ouverture et à chaque `inscrire` |
| `effacer_historique` | conversations et Retours supprimés, annulations en attente oubliées, `VACUUM` ; réglages et journal conservés |
| `user_version` inconnue | `SlmspError`, aucune table créée |
| Réglage inconnu | `KeyError` |

</intent-contract>

## Code Map

- `src/slmsp/app/stockage.py` : `Stockage`, `JournalApplication`, `dossier_donnees`, `REGLAGES_DEFAUT`.
- `tests/app/test_stockage.py` : critères 1 à 6 (le 6 par l'assemblage réel, `assembler(journal=JournalApplication)`, tâche CR du document témoin).

## Verification

- `uv run pytest -q --tb=short tests/app` : verts.

## Auto Run Result

- Décisions : (1) le contenu supprimé n'est conservé qu'en mémoire du processus pendant 5 s (pas de table de corbeille) : une fermeture de l'application dans ces 5 s rend la suppression définitive ; (2) horodatages stockés en UTC ISO ; (3) messages et sources stockés en JSON sans re-validation (la validation AD-7 reste à la charge de l'appelant, 12.5) ; (4) `effacer_historique` conserve réglages et journal (le journal a son propre « Effacer »).
- Reports : l'injection dans l'assemblage de l'application dépend de 12.1 (`harness/assemblage.py`) ; le test 6 utilise `cli._assemblage.assembler` qui accepte déjà `journal=`.

Points à confirmer par Anaël :
1. Annulation en mémoire seulement (décision 1) : acceptable, ou corbeille persistée 5 s ?
2. `effacer_historique` ne touche pas au journal ni aux réglages.
3. Pas de chiffrement de la base (profil Windows de l'Agent).

## Revue

- medium, second avis (stockage.py:243) : contenu supprimé gardé en mémoire au-delà de 5 s, docstring fausse. Corrigé : purge à chaque lecture/liste, minuteur démon à l'échéance, annulé par `effacer_historique` ; docstring corrigée ; test d'oubli sans nouvelle suppression.
- medium, second avis (test effacement) : `identifiant` jamais supprimé, assertion vide. Corrigé : la conversation à annulation en attente est celle testée, et son contenu est absent de tous les fichiers après effacement.
- medium, second avis (test critère 6) : journal toujours vide quoi qu'il arrive. Corrigé : test RD connecté, la requête autorisée vers `mcp.data.gouv.fr` figure dans `JournalApplication.lister()` (termes compris) et est relue après réouverture ; le test CR garde l'assertion « journal vide ».
- low (WAL avant contrôle de version) : confirmé mais inévitable (`ouvrir_sqlite` du noyau active le WAL avant toute lecture) ; test précisé (`user_version` toujours 99, aucune table). Rejeté côté code, test corrigé.
- low (INSERT OR REPLACE) : corrigé, `ON CONFLICT DO NOTHING`, `annuler_suppression` renvoie `False` et garde la version réenregistrée ; test ajouté.
- low (lecture puis suppression hors verrou) : corrigé, `BEGIN IMMEDIATE` dans une seule connexion.
- low (AD-23 non testé) : corrigé, test de `dossier_donnees` et du chemin par défaut avec `LOCALAPPDATA` simulé (local à ce module, pas de duplication de 12.1).
- low (VACUUM non vérifié) : corrigé, test de réduction de taille du fichier.
- low (non-ASCII, troncature du titre) : corrigé, test ajouté.
- Reporté : l'annulation reste en mémoire seulement (points à confirmer par Anaël, inchangé).
