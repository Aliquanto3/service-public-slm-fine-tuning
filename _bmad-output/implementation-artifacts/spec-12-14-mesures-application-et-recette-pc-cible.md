---
title: 'Story 12.14 — Mesures FR-26 de l''application installée et protocole de recette sur PC cible'
type: 'feature'
created: '2026-10-23'
status: 'in-progress'
baseline_commit: 'aa6223f87d3dacdeaa16f89e95ea1968dc8b3c16'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `slmsp measure run` mesure un Assistant assemblé par la CLI, pas l'application installée (pywebview + WebView2 + deux `llama-server`) ; rien ne mesure la RAM réelle de l'arbre installé ni ne décrit la recette sur un PC cible 16 Go sans GPU (NFR-1 à NFR-4, NFR-7, SM-5).

**Approach:** Nouvelle sous-commande `slmsp measure application --exe <AssistantSP.exe>` qui lance l'exécutable, échantillonne la RAM de tout son arbre de processus (WebView2 et `llama-server` compris) pendant qu'Anaël utilise l'application, et écrit un run `runs/measure/<run_id>/resultat.json` comparé aux seuils de `config/mesures.toml`. Débit et premier token viennent, en option, de l'export CSV des mesures de l'application (`--mesures-csv`). Le protocole manuel (captures réseau, NFR-7, consignation) est écrit dans `docs/recette-pc-cible.md` ; la recette elle-même est faite par Anaël.

## Boundaries & Constraints

**Always:**
- `measure/application.py` n'importe ni `slmsp.app` ni `slmsp.cli` (AD-1, couches 4 et 5) ; seulement `psutil`, `core`, `measure.*`. Il n'ouvre jamais la base SQLite de l'application (AD-23) : les mesures d'appels arrivent par le CSV exporté depuis l'interface.
- Réutiliser `EchantillonneurRam` (avec `racine=` le processus lancé) et `somme_arbre` ; le pic de RAM couvre tous les descendants.
- Exclusivité : prendre `verrou_mesure` (paramétrer le libellé de commande) avant de lancer l'exécutable.
- Dépassement de 5 Go : `repli` liste les leviers de l'addendum §D dans l'ordre (contexte réduit, cache KV q4, usearch i8, embedding plus léger, corpus restreint), sans rien appliquer.
- Fin de mesure : à la sortie du processus lancé, à `--duree` écoulée (défaut 900 s) ou sur Ctrl+C ; le run est alors `complet` (Ctrl+C = fin normale de la fenêtre de mesure). Ne jamais tuer l'application à `--duree` : seulement arrêter l'échantillonnage.
- Commande utilisable sur le PC cible avec les dépendances de base (`uv sync` sans extra).

**Never:**
- Pas d'automatisation de l'interface (pas de pilotage WebView2), pas de capture réseau lancée par la commande (pktmon exige l'administrateur : protocole manuel).
- Ne pas modifier `measure run`, `protocole.mesurer` ni le schéma `ResultatMesure`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Nominal | `--exe` valide, Anaël pose une Question puis ferme l'appli | run `application` complet : `ram_max_go`, conformité `nfr-1`/`nfr-1-cible`, répartition du pic par nom de processus (`assistantsp`, `msedgewebview2`, `llama-server`, autres), durée, nb d'échantillons ; résumé à l'écran | — |
| Avec CSV | `--mesures-csv` exporté depuis l'appli | `debit_tps_mediane`, `premier_token_s_mediane`/`p95` sur les lignes `fournisseur` local dans la fenêtre de mesure, conformité `nfr-2`/`nfr-3` | CSV illisible ou sans ligne retenue : USAGE (2), message clair |
| Sans CSV | — | débit et latence `None`, `nfr-2`/`nfr-3` absents de `conformite`, verdict sur NFR-1 seul | — |
| Exe absent | chemin inexistant ou pas un fichier | rien lancé | USAGE (2) |
| Instance déjà ouverte | le processus lancé sort en < 5 s | message « fermer l'Assistant déjà ouvert puis relancer », run `partiel-erreur` | code ECHEC |
| Verrou tenu | autre commande `slmsp` active | — | `RessourceOccupee` (5) |
| Seuil dépassé | pic > `ram_max_go` | verdict `infirmee`, `repli` = leviers §D | — |

</frozen-after-approval>

## Code Map

- `src/slmsp/measure/ram.py` -- `EchantillonneurRam(racine, periode_s, lire)`, `somme_arbre`, `working_set` : à réutiliser ; ajouter si besoin une fonction de répartition par nom (même gestion `NoSuchProcess`/`AccessDenied`).
- `src/slmsp/measure/protocole.py` -- modèle à suivre : `nouveau_run("measure", slug, …)`, `run.ecrire(NOM_RESULTAT, json_canonique(...))`, `run.terminer(...)`, `empreinte_environnement`, `GO`, `_conformite`, `verrou_mesure` (libellé `"slmsp measure run"` en dur → paramètre `commande` avec ce défaut).
- `src/slmsp/measure/config.py` -- `charger_config_mesures()` : seuils et `periode_ms`.
- `src/slmsp/measure/debit.py` -- `mediane_p95` à réutiliser pour le CSV.
- `src/slmsp/core/schemas/mesure.py` -- `ResultatMesure` (slug `mesure` en kebab, `repli` obligatoire si `infirmee`).
- `src/slmsp/cli/measure.py` -- ajouter l'action `application` à côté de `run` ; imports paresseux dans la fonction, codes `CodeSortie`.
- `src/slmsp/app/observabilite.py:517` `exporter_csv` -- format d'entrée du CSV : séparateur `;`, en-tête = `COLONNES_MESURE` (`app/stockage.py:37`), cellules passées par `cellule_sure` (préfixe `'` possible devant `=+-@` : à retirer). `fournisseur` local = `inference.mesures.FOURNISSEUR_LOCAL` (importable : couche `inference`). `horodatage` ISO. Débit = `tokens_sortie / ((duree_ms − premier_token_ms)/1000)` (génération seule, comme NFR-2), lignes `interrompu` ou sans `premier_token_ms` écartées.
- `src/slmsp/app/principal.py` -- instance unique par mutex : un 2ᵉ lancement sort aussitôt.
- `packaging/assistantsp.spec` -- onedir : `AssistantSP.exe` est le processus racine.
- `config/` (liste blanche du profil `assistant`, fichier de la passerelle) et `docs/installation-dsi.md` -- hôtes à citer dans le protocole (relire, ne pas recopier de mémoire).
- `docs/reprise-deuxieme-pc.md` -- installation d'uv et du dépôt, à référencer pour le PC cible.
- `tests/measure/test_ram.py` -- motif d'enfant Python factice qui alloue : réutiliser pour simuler l'exécutable.

## Tasks & Acceptance

**Execution:**
- [ ] `src/slmsp/measure/protocole.py` -- `verrou_mesure(commande: str = "slmsp measure run")` -- libellé juste pour la nouvelle commande.
- [ ] `src/slmsp/measure/application.py` -- `mesurer_application(exe, config, *, duree_s, mesures_csv, racine, lancer=subprocess.Popen, horloge, echantillonneur)` : lance, échantillonne jusqu'à fin, répartition au pic, lecture CSV, conformité, `ResultatMesure` slug `application`, hypothèse `H-RAM`, avertissement « à consigner dans docs/recette-pc-cible.md ; vérifier que la machine est le PC cible (empreinte) » ; exceptions dédiées (`InstanceDejaOuverte`, `CsvInvalide`) -- cœur testable sans GUI.
- [ ] `src/slmsp/cli/measure.py` -- action `application` (`--exe` requis, `--duree`, `--mesures-csv`, `--racine`), affichage du résumé et du chemin du run ; docstring du module mise à jour.
- [ ] `tests/measure/test_application.py` -- matrice ci-dessus avec un faux exécutable Python (enfant qui alloue, petit-enfant, sortie rapide), CSV factices (préfixe `'`, hors fenêtre, non local, interrompu), seuil dépassé → repli §D, verrou tenu, exe absent ; test CLI via `main([...])` ou équivalent existant.
- [ ] `docs/recette-pc-cible.md` -- protocole : préparation (PC 16 Go sans GPU, installateur 12.13 + SHA-256, uv + dépôt + `uv sync`), mesure RAM (commande exacte, une Question, export CSV puis `--mesures-csv`), capture réseau hors ligne forcé 10 min et connecté (pktmon en admin : `pktmon start --capture --comp nics`, `pktmon stop`, `pktmon etl2pcapng`, filtrage par PID de l'arbre relevé via `Get-Process`/`netstat -ano`, alternative Wireshark), lecture : aucun paquet hors ligne, seuls les hôtes de la Liste blanche en connecté, résidus WebView2 consignés (Q1) ; liste de contrôle NFR-7 (clavier, contraste, libellés) ; tableau de consignation des résultats et des écarts ; leviers §D si dépassement.
- [ ] `_bmad-output/implementation-artifacts/sprint-status.yaml` -- 12-14 → `review` (recette Anaël en attente).

**Acceptance Criteria:**
- Given l'application lancée par la commande, when elle tourne avec des descendants, then le pic consigné inclut l'exécutable et tous ses descendants, avec la répartition par nom.
- Given `uv run pytest -q tests/measure tests/test_architecture.py`, when la suite tourne, then tout passe et aucune règle de couche n'est violée.
- Given `docs/recette-pc-cible.md`, when Anaël le suit, then chaque critère 1 à 4 de la story a une étape, une commande ou une case, et un emplacement où consigner le résultat.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

Décisions prises seul : génération déclenchée à la main dans l'interface (pas d'automatisation) ; débit et latence par le CSV de l'appli plutôt que par la base SQLite (propriété d'`app.stockage`) ; slug de run `application` distinct de `h-ram` pour ne pas mélanger avec les mesures CLI ; mesure arrêtée sans tuer l'appli.

## Verification

**Commands:**
- `uv run pytest -q --tb=short tests/measure tests/test_architecture.py` -- expected: vert
- `uv run --no-sync python outils/controle_rapide.py` -- expected: vert
- `uv run slmsp measure application --help` -- expected: options affichées
