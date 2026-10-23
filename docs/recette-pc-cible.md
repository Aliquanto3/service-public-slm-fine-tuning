# Recette sur PC cible (story 12.14)

Protocole manuel, à dérouler par Anaël sur un vrai PC cible : **16 Go de RAM, sans GPU**,
Windows 10 ou 11 x64. Valide SM-5 et la promesse de confidentialité (NFR-1 à NFR-4, NFR-7)
avant de montrer l'outil. Les captures réseau et la liste de contrôle RGAA sont manuelles :
`slmsp measure application` ne mesure que la RAM (en option le débit et la latence), n'ouvre
pas la base SQLite de l'application et ne pilote jamais l'interface.

## 0. Préparation

1. **Installateur.** Récupérer `AssistantSP-Setup-<version>.exe` (story 12.13) et son
   `.sha256` ; vérifier l'empreinte avant d'installer (`docs/installation-dsi.md`,
   section « Vérifier l'installateur ») :
   ```powershell
   Get-FileHash .\AssistantSP-Setup-<version>.exe -Algorithm SHA256
   ```
   Comparer avec le fichier `.sha256` publié. Installer sans droits administrateur
   (`/VERYSILENT` ou double-clic).
2. **Dépôt et outillage** (pour lancer `slmsp measure application`, pas l'application elle-même) :
   installer Git, uv (`winget install Git.Git astral-sh.uv`), cloner le dépôt, puis
   `uv sync` (sans extra : la commande tourne avec les dépendances de base). Voir
   `docs/reprise-deuxieme-pc.md` pour le détail d'un clonage sur un nouveau poste.
3. Noter l'empreinte machine (RAM totale, présence GPU, `git_commit`) : elle est consignée
   automatiquement dans `environnement` du résultat (`empreinte_environnement`) — vérifier
   après la mesure (étape 1) qu'elle correspond bien au PC cible, pas à la machine de
   développement.

## 1. Mesure RAM (NFR-1), en option débit et latence (NFR-2, NFR-3)

1. Lancer la mesure (racine du dépôt, après `uv sync`) :
   ```powershell
   uv run slmsp measure application --exe "<dossier d'installation>\AssistantSP.exe"
   ```
   Durée par défaut : 900 s (`--duree` pour changer). La fenêtre se termine à la fermeture de
   l'Assistant, à la durée écoulée, ou par Ctrl+C — jamais en tuant le processus.
2. Pendant la fenêtre, utiliser l'Assistant normalement : poser au moins une Question, laisser
   la génération se terminer.
3. Dans l'application, ouvrir **Méthode** et exporter les mesures (CSV) vers un fichier.
   Relancer la mesure avec ce fichier pour obtenir débit et latence :
   ```powershell
   uv run slmsp measure application --exe "<dossier>\AssistantSP.exe" --mesures-csv "<export>.csv"
   ```
   (Le premier passage sans `--mesures-csv` donne déjà le critère 1 à lui seul ; refaire la
   mesure avec l'export évite de rouvrir l'application juste pour relire son CSV.)
4. Lire le résumé affiché (`nfr-1`, `nfr-1-cible`, et `nfr-2`/`nfr-3` si un CSV a été fourni) et
   le run écrit sous `runs/measure/<run_id>/resultat.json`.
5. **Si le pic dépasse 5 Go** : le `resultat.json` porte un `repli` avec les leviers de
   l'addendum §D, dans l'ordre (contexte réduit, cache KV en q4, usearch en i8, embedding plus
   léger, corpus restreint) — à **proposer**, jamais à appliquer d'office pendant la recette.

Consigner dans le tableau de la section 4 : `ram_max_go`, `debit_tps_mediane`,
`premier_token_s_mediane`/`p95`, et chaque conformité.

## 2. Capture réseau (NFR-4), critères 2 et 3

Nécessite une invite PowerShell **en administrateur** (pktmon l'exige) : la commande
`measure application` ne lance jamais cette capture elle-même.

### 2.1 Mode hors ligne forcé (critère 2, 10 minutes)

1. Mettre l'Assistant en Mode hors ligne forcé (Paramètres).
2. Relever les PID de l'arbre avant de capturer :
   ```powershell
   Get-Process AssistantSP, msedgewebview2, llama-server -ErrorAction SilentlyContinue |
       Select-Object Id, ProcessName
   ```
3. Démarrer la capture, utiliser l'Assistant pendant 10 minutes (plusieurs Questions, Correction,
   Résumé…), puis arrêter :
   ```powershell
   pktmon start --capture --comp nics
   # ... 10 minutes d'usage ...
   pktmon stop
   pktmon etl2pcapng .\PktMon.etl -o capture-hors-ligne.pcapng
   ```
4. Filtrer la capture par les PID relevés à l'étape 2 (`netstat -ano` donne aussi les PID en
   écoute/connexion locaux de llama-server, attendus en 127.0.0.1 seulement) ou ouvrir
   `capture-hors-ligne.pcapng` dans Wireshark et filtrer par PID (colonne ajoutée par
   l'extension Npcap) ou, à défaut, par IP/port connus du poste.
5. **Lecture :** aucun paquet sortant (hors 127.0.0.1) ne doit provenir de l'arbre de
   processus de l'Assistant. Tout résidu de télémétrie ou de mise à jour du runtime
   WebView2 lui-même (processus `msedgewebview2.exe` ou `MicrosoftEdgeUpdate` hors de
   l'arbre de l'Assistant) est **consigné séparément** (Q1), sans faire échouer le critère.

### 2.2 Mode connecté (critère 3)

1. Mettre l'Assistant en Mode connecté.
2. Même procédure de capture que 2.1 (durée raisonnable pour déclencher au moins une
   Tâche en ligne : FR-7, FR-8 ou FR-12).
3. **Lecture :** chaque hôte distant contacté par l'arbre de l'Assistant doit figurer dans
   `config/liste-blanche.toml` (correspondance exacte, insensible à la casse) :
   `mcp.data.gouv.fr`, `www.data.gouv.fr`, `www.service-public.gouv.fr`,
   `www.service-public.fr`, `www.legifrance.gouv.fr`,
   `entreprendre.service-public.gouv.fr`, `entreprendre.service-public.fr`,
   `lannuaire.service-public.fr`. Toute résolution ou connexion à un autre hôte est un
   échec du critère (consigner le detail : hôte, port, moment).

## 3. Liste de contrôle NFR-7 (critère 4)

RGAA 4.1 visé, v1 limitée à trois exigences. Dérouler à la souris débranchée pour le premier
point.

| # | Vérification | Conforme ? | Écart constaté |
|---|---------------|------------|-----------------|
| 1 | Clavier complet : atteindre chaque Tâche, le champ de saisie, l'envoi, l'historique et les Paramètres uniquement au clavier (Tab, Maj+Tab, Entrée, flèches) | | |
| 2 | Contraste texte/fond ≥ 4,5:1 sur les écrans principaux (bienvenue, conversation, Paramètres) — mesurer au moins un échantillon par écran | | |
| 3 | Libellés accessibles : chaque champ, bouton et région a un nom perçu par un lecteur d'écran (`aria-label`/`<label>`), pas seulement une icône | | |

## 4. Consignation des résultats

| Critère | Mesure / observation | Résultat | Écart / repli |
|---------|----------------------|----------|-----------------|
| 1 — RAM (NFR-1) | `ram_max_go` du run `application` | | repli §D si > 5 Go |
| 1 — débit (NFR-2) | `debit_tps_mediane` (si `--mesures-csv`) | | |
| 1 — latence (NFR-3) | `premier_token_s_mediane` / `p95` (si `--mesures-csv`) | | |
| 2 — hors ligne (NFR-4) | paquets hors `127.0.0.1` depuis l'arbre, 10 min | | résidus WebView2 (Q1) |
| 3 — connecté (NFR-4) | hôtes contactés hors Liste blanche | | |
| 4 — clavier (NFR-7) | ligne 1 de la liste de contrôle | | |
| 4 — contraste (NFR-7) | ligne 2 | | |
| 4 — libellés (NFR-7) | ligne 3 | | |

Joindre le chemin du run (`runs/measure/<run_id>/`) et les captures (`.pcapng`) à ce tableau
une fois rempli.
