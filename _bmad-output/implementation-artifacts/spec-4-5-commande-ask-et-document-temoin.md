---
title: 'Story 4.5 — Commande `slmsp ask` et test du document témoin'
type: 'feature'
created: '2026-10-13'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: []
deferred:
  - summary: "Contrôle de schéma serveur (`controle_schema` de `ModeSonde`) non câblé dans la racine de composition."
    evidence: "`ModeSonde(controle_schema=None)` : un schéma MCP modifié n'est détecté qu'à l'appel (`McpEnDirect`), pas au passage en connecté."
  - summary: "Adaptateurs d'entraînement (`--modele adaptateur:<run>`) : seule la forme `base:<slug>` est acceptée."
    evidence: "Les adaptateurs arrivent avec l'Epic 10."
---

<intent-contract>

## Intent

**Problem:** le Harnais (4.1 à 4.4) n'a pas d'entrée en ligne de commande, et la promesse FR-38 (un texte collé ne produit aucune Requête sortante) n'est vérifiée qu'avec des espions de ports, pas avec la vraie passerelle.

**Approach:** une racine de composition `cli/_assemblage.py` (serveurs, Index, journal, `ModeSonde`, `Passerelle`, outils MCP paresseux) et la commande `slmsp ask` qui affiche le flux d'évènements ; le test du document témoin passe par cet assemblage avec le vrai `NetGate` et un transport interne espion.

## Boundaries & Constraints

**Always:** `harness` ne connaît que les ports ; seule la racine de composition crée les adaptateurs. Hors ligne forcé : aucun outil fourni, donc ni sonde ni requête. Les textes des tests sont des mots aléatoires (D1.1).

**Never:** aucun appel d'API payant ni réseau ; aucun prompt composé hors `construire_messages` ; pas de modification de `harness/`, `net/` ni de la config.

</intent-contract>

## Code Map

- `src/slmsp/cli/_assemblage.py` -- `assembler(modele, tache, …)` (context manager), `Assemblage`, `OutilsParesseux`, `slug_modele`.
- `src/slmsp/cli/ask.py` -- sous-commande `ask` (`--modele`, `--tache`, `--hors-ligne`, `--conversation`, `--json`, `--journal`, `--variante`).
- `tests/cli/test_ask.py`, `tests/harness/test_document_temoin.py`.

## Tasks & Acceptance

- [x] Critère 1 : réponse en flux, puis sources numérotées (titre, URL, date), avertissement de la Tâche, résultats d'outils RD rendus par `contenu_resultat`.
- [x] Critère 2 : `--conversation` relit puis complète le fichier (échange `user`/`assistant`, sans tours d'outil) ; `--json` émet un évènement par ligne.
- [x] Critère 3 : `--journal` liste les Requêtes sortantes de l'exécution (heure, hôte, méthode, termes, statut).
- [x] Critère 4 : CR, LC, CO, RE, CT, NR, TR en connecté, vrai `ModeSonde` et `Passerelle`, transport espion : 0 requête, journal vide.
- [x] Critère 5 : RD connecté : une seule entrée `search_datasets` avec `termes` = arguments canoniques ; la phrase de l'Agent n'apparaît dans aucune entrée.
- [x] Critère 6 : `--hors-ligne` (RD) : transport espion jamais appelé, journal vide.
- [x] Test bout en bout (`lent`) : Granite 1B réel, BGE-M3 et Index réel ; non exécuté ici.

## Design Notes

`--modele` n'accepte que `base:<slug>`. Le serveur d'embedding et l'Index ne démarrent que si le prompt de la Tâche a un emplacement `passages`. La sonde a lieu à la première lecture du Mode, donc jamais pour une Tâche de rédaction. Le test RD fait passer l'appel d'outil par `Passerelle.client("assistant")` (même garde que `McpEnDirect`), faute de serveur MCP factice.

## Verification

- `uv run pytest -q tests/cli/test_ask.py tests/harness/test_document_temoin.py` ; `uv run ruff check` ; `uv run ruff format --check`.
- À lancer plus tard : `uv run pytest tests/cli/test_ask.py -m lent -s` avec `SLMSP_VENDOR_DIR`, `SLMSP_MODELS_DIR`, `SLMSP_INDEX_RACINE`.

## Auto Run Result

Statut : review. Décisions prises seul (solution la plus simple et réversible) :
- `--variante cpu|cuda` ajoutée (défaut cpu) pour le serveur de génération ; l'embedding reste en CPU.
- `--conversation` ne stocke que les messages `user` et `assistant` finaux ; `--json --journal` écrit le journal sur stderr.
- Tâche Q/RD sans Index local : l'erreur `ManifesteInvalide` de `ouvrir_index` est affichée telle quelle (code 4).
- À confirmer par Anaël : forme de `--modele` (seul `base:<slug>` accepté avant l'Epic 10).
Reports : voir `deferred` (contrôle de schéma au passage en connecté ; adaptateurs).

## Revue

- Medium, corrigé : `--conversation` dans un dossier absent ou non inscriptible levait une `OSError` non interceptée (trace Python après la réponse) ; erreur propre, code 1, test ajouté.
- Low, rejeté : un `ResultatOutil` en erreur n'est pas rendu en mode texte (l'erreur reste visible en `--json`).
- Aucun autre défaut : critères 4 à 6 et FR-38 conformes (rédaction sans lecture du Mode donc sans sonde ; hors ligne sans outils ni sonde ; journal limité aux `termes`) ; couches respectées, aucun réseau dans les tests.
