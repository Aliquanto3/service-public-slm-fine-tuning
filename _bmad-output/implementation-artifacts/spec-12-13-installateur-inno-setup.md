---
title: 'Story 12.13 — Installateur Inno Setup par utilisateur et désinstallation'
type: 'feature'
created: '2026-10-17'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-12-12-executable-pyinstaller.md'
warnings: []
deferred: []
---

## Intent
Installer l'Assistant sans droits administrateur (Q3), le réinstaller par-dessus (Q6), le désinstaller en une question avec suppression optionnelle des données (FR-22). Pas de signature : empreinte SHA-256 publiée (Q4). WebView2 détecté (Q2).

## Approach
- `packaging/assistantsp.iss` : `PrivilegesRequired=lowest`, `{localappdata}\Programs\AssistantSP`, `AppId` fixe, pages dossier/groupe/récapitulatif désactivées (accueil, progression, fin), raccourci du menu Démarrer, case « Lancer l'assistant » cochée. Paramètres passés par ISCC (`/DVersionApp`, `/DDossierSource`, `/DDossierSortie`, `/DDecoupage=1`, `/DPackComplet`).
- WebView2 : valeur `pv` de `EdgeUpdate\Clients\{F3017226-…}` en HKLM32, HKLM64 et HKCU (vide ou `0.0.0.0` = absent). Absent : message pour la DSI et arrêt. Avec `/DPackComplet`, l'installateur autonome WebView2 est embarqué et lancé à la place (option prévue, paquet **non** téléchargé).
- Désinstallation : « Conserver l'historique et les retours sur ce poste ? » ; « Non » supprime `%LOCALAPPDATA%\AssistantSP\` (données et `var`, 12.12). En silencieux, données conservées sauf `/SupprimerDonnees=1`. Le dossier d'installation est toujours retiré.
- `outils/construire_installateur.py` : recherche d'ISCC (`--iscc`, `SLMSP_ISCC`, `vendor/innosetup`, `%LOCALAPPDATA%\Programs\Inno Setup 6`, PATH), `DiskSpanning` si le paquet dépasse 2 000 000 000 o (tranches de 2 Go), commande ISCC, `AssistantSP-Setup-<v>.exe.sha256` (format `sha256sum`, une ligne par fichier, tranches comprises).
- `docs/installation-dsi.md` : une page (pas d'admin, hôtes, SmartScreen, empreinte, silencieux, build).

Commande de build (après `construire_application.py`) :
`uv run --no-sync python outils/construire_installateur.py [--iscc <chemin>\ISCC.exe] [--pack-complet <webview2>.exe]`

## Tests
`tests/packaging/test_installateur.py` (16) : valeurs du `.iss` (privilèges, dossier, AppId, écrans, lancement coché, WebView2, question de désinstallation, découpage et pack conditionnels), commande ISCC, seuil de découpage, build avec compilateur factice, empreintes des tranches, échecs (ISCC, sortie, paquet, pack), ordre de recherche d'ISCC.

## État d'Inno Setup
**Non téléchargé** : `jrsoftware.org` n'est dans aucun profil de `config/reseau.toml`, rien n'a été contourné. Donc `.iss` jamais compilé, installation et désinstallation silencieuses non essayées (AC1 à AC4 non vérifiés). L'étape manuelle est dans `docs/installation-dsi.md`.

## Décisions prises seul
- `AppId` : GUID généré pour le projet, à ne plus changer.
- Éditeur affiché « Assistant SP », nom du programme « Assistant SP » (dossier `AssistantSP`).
- Langue de l'installateur : français seul (`compiler:Languages\French.isl`).
- Seuil de `DiskSpanning` sur la taille non compressée du paquet (les GGUF se compressent peu) ; compression `lzma2/fast`, non solide.
- Silencieux : la désinstallation conserve les données par défaut (le plus réversible).

## À confirmer
- **Téléchargement d'Inno Setup** : ajouter `jrsoftware.org` (et son CDN de téléchargement) au profil `outillage` de la passerelle, ou télécharger à la main ; épingler alors la version et consigner son SHA-256 (non inventé ici).
- Syntaxe du `.iss` (`x64compatible`, `{param:…}`, `French.isl` livrée avec Inno Setup 6.3+) à valider au premier `ISCC`.
- Premier build : taille réelle, nécessité du `DiskSpanning`, lancement depuis un partage réseau sans élévation, hors ligne, réinstallation par-dessus conservant `assistant.sqlite`.
- Le prompt de désinstallation propose « Oui = conserver » par défaut : conforme à la formulation de la story.
- Variante « pack complet » : seulement si un poste pilote manque de WebView2 (licence de redistribution à vérifier).
- Publication de l'empreinte avec l'installateur (emplacement de diffusion).

## Auto Run Result
Statut : partiel (script, outillage et tests faits ; compilation et essais d'installation non réalisés faute d'ISCC).
