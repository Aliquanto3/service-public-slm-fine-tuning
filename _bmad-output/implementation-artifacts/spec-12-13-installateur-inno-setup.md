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
`tests/packaging/test_installateur.py` (24) : valeurs du `.iss` (privilèges, dossier, AppId, écrans, lancement coché, WebView2, question de désinstallation, découpage et pack conditionnels), commande ISCC, seuil de découpage, build avec compilateur factice, empreintes des tranches, échecs (ISCC, sortie, paquet, pack), ordre de recherche d'ISCC (explicite absent = échec), pack résolu en absolu, nettoyage des tranches obsolètes, OSError de ISCC, /DIR= limité à Programs, aucun `[UninstallDelete]` sur `{app}`.

## État d'Inno Setup
Installé le 2026-10-17 : voir « Exécution réelle ».

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

## Revue
- medium, second avis : `[UninstallDelete]` récursif sur `{app}` : corrigé (entrée retirée) ; `/DIR=` limité à `%LOCALAPPDATA%\Programs` dans `InitializeSetup` ; tests sur le contenu du `.iss`.
- medium, second avis : `--pack-complet` relatif : corrigé (`resolve()`), test.
- medium, second avis : tranches `.bin` obsolètes dans le `.sha256` : corrigé (nettoyage de la version avant ISCC), test.
- low, second avis : `--iscc`/`SLMSP_ISCC` explicite absent : corrigé, échec net, test.
- low, second avis : `OSError` de `subprocess` : corrigé (ECHEC propre, code 2), test.
- low, second avis : silencieux sans WebView2 : corrigé (`Log`, sortie 1 documentée dans `docs/installation-dsi.md`).
- low, second avis : concaténation dans `const` : corrigé (constante littérale), test.
- low, second avis : tests superficiels : complétés (8 tests ajoutés, sans ISCC).
- Reporté : compilation réelle du `.iss` (`{param:DIR|}`, `Copy`/`Lowercase`, `Log`), à valider au premier ISCC ; effet réel du refus de `/DIR=` en silencieux.

## Exécution réelle (2026-10-17, story 12.13b)
- **Inno Setup 6.7.3** (dernière 6 stable), https://github.com/jrsoftware/issrc/releases/download/is-6_7_3/innosetup-6.7.3.exe (lien de https://jrsoftware.org/isdl.php), 10 592 232 o, SHA-256 `9c73c3bae7ed48d44112a0f48e66742c00090bdb5bef71d9d3c056c66e97b732` (calculé à la première lecture, l'éditeur n'en publie pas ; signature Authenticode valide, Pyrsys B.V.). Épinglé dans `config/outillage.toml`, téléchargé par `outils/installer_inno_setup.py` (passerelle `outillage`). Installé par utilisateur (`/CURRENTUSER /VERYSILENT /DIR=vendor\inno-setup`), sans élévation.
- **Compilation** : `construire_application.py --sans-modele` (59 s, 158 Mo) puis `construire_installateur.py` : le `.iss` compile du premier coup, sans correction (`{param:DIR|}`, `Copy`/`Lowercase`, `Log`, `x64compatible` acceptés). Installateur 62 148 145 o (59 Mo, runtime seul, sans modèle), pas de `DiskSpanning`.
- **Essais** (poste réel, données réelles sauvegardées puis restaurées) : installation silencieuse (code 0, `%LOCALAPPDATA%\Programs\AssistantSP`, raccourci du menu Démarrer, clé de désinstallation) ; l'exécutable démarre (fenêtre « Assistant », crée `assistant.sqlite`) ; réinstallation par-dessus (code 0, `assistant.sqlite` et marqueur inchangés) ; désinstallation silencieuse (code 0, programme et raccourci retirés, données conservées) ; réinstallation puis désinstallation `/SupprimerDonnees=1` (code 0, dossier de données supprimé) ; `/DIR=C:\Temp\essai-refus` refusé (code 1, motif au journal, rien créé). Comparaison avant/après de `%LOCALAPPDATA%`, `Programs`, menu Démarrer, Bureau et clés de désinstallation : aucune trace hors des deux dossiers de l'Assistant.
- Non essayé : lancement depuis un partage réseau, WebView2 absent, `DiskSpanning`, build avec modèle (GPU occupé).
- Test `lent` `test_compilation_reelle` (ISCC dans `vendor/inno-setup` ou `SLMSP_VENDOR_DIR`, ignoré sinon).
- Écart : `construire_installateur.py` cherche maintenant `vendor/inno-setup` (et non `innosetup`) et `SLMSP_VENDOR_DIR`. À confirmer par Anaël : SHA-256 non recoupé avec une source de l'éditeur.
