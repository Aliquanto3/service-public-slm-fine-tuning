# Installation de l'Assistant SP (note pour la DSI)

## En bref
- Installation **par utilisateur, sans droits administrateur** : programme dans `%LOCALAPPDATA%\Programs\AssistantSP`, données (historique, retours, journal, état machine) dans `%LOCALAPPDATA%\AssistantSP\`. Rien n'est écrit ailleurs (ni registre machine, ni `Program Files`).
- Prérequis : **Microsoft Edge WebView2 Runtime** (présent sur Windows 11 et sur la plupart des Windows 10 à jour). S'il manque, l'installateur s'arrête avec un message demandant l'intervention de la DSI. Une variante « pack complet » embarquant l'installateur autonome WebView2 n'est produite que sur demande (`--pack-complet`).
- Trois écrans : accueil, progression, fin (case « Lancer l'assistant » cochée).
- Fonctionne hors ligne : le Modèle et l'Index sont dans l'installateur, aucun téléchargement au premier lancement.

## Hôtes contactés
Seulement en Mode connecté et pour répondre à une question (HTTPS, port 443), ceux de `config/liste-blanche.toml` : `mcp.data.gouv.fr`, `www.data.gouv.fr`, `www.service-public.gouv.fr`, `www.service-public.fr`, `www.legifrance.gouv.fr`, `entreprendre.service-public.gouv.fr`, `entreprendre.service-public.fr`, `lannuaire.service-public.fr`. En Mode hors ligne, aucune connexion.

## Vérifier l'installateur (pas de signature, Q4)
L'installateur n'est pas signé : Windows SmartScreen peut afficher « Windows a protégé votre ordinateur » (Informations complémentaires, puis Exécuter quand même). Comparer l'empreinte avec le fichier `AssistantSP-Setup-<version>.exe.sha256` publié avec lui :

    certutil -hashfile AssistantSP-Setup-<version>.exe SHA256

Si l'installateur est découpé (paquet de plus de 2 Go), les fichiers `.bin` voisins doivent rester dans le même dossier ; leurs empreintes figurent aussi dans le fichier `.sha256`.

## Installation, mise à jour, désinstallation
- Installation : lancer `AssistantSP-Setup-<version>.exe` (depuis un partage réseau possible). Silencieuse : `/VERYSILENT /SUPPRESSMSGBOXES /DIR=<dossier>`.
- Mise à jour : pas de mise à jour automatique (Q6). Lancer le nouvel installateur : il s'installe par-dessus l'ancienne version (même `AppId`), les données sont conservées.
- Désinstallation (Paramètres, Applications) : une question, « Conserver l'historique et les retours sur ce poste ? ». « Non » supprime aussi `%LOCALAPPDATA%\AssistantSP\`. Silencieuse : `unins000.exe /VERYSILENT` conserve les données ; ajouter `/SupprimerDonnees=1` pour les supprimer.

## Construire l'installateur (poste de dev)
1. `uv run --extra app python outils/construire_application.py` (12.12, produit `dist/AssistantSP`).
2. Inno Setup 6.7.3, par utilisateur, sans administrateur : `uv run --no-sync python outils/installer_inno_setup.py` (téléchargement par la passerelle, version, URL et SHA-256 `9c73c3ba…97b732` épinglés dans `config/outillage.toml`, installation dans `vendor\inno-setup` ou `SLMSP_VENDOR_DIR`).
3. `uv run --no-sync python outils/construire_installateur.py [--iscc <chemin>\ISCC.exe] [--pack-complet <installateur WebView2>]` : produit `dist/installateur/AssistantSP-Setup-<version>.exe` et son `.sha256`.

## Codes de sortie en mode silencieux
`/VERYSILENT` : code 1 (échec d'initialisation, motif dans le journal avec `/LOG=<fichier>`) si WebView2 est absent (installateur sans pack complet) ou si `/DIR=` est hors de `%LOCALAPPDATA%\Programs`. Le désinstallateur ne supprime jamais le dossier d'installation en bloc.
