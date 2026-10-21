Installe et aide-moi à tester l'Assistant SP v0.3.0, une application Windows avec un SLM local et, en option, des modèles externes, publiée sur https://github.com/Aliquanto3/service-public-slm-fine-tuning/releases/tag/v0.3.0. Je fais les tests moi-même ; toi, tu prépares, tu vérifies et tu me guides. Ne modifie rien d'autre sur ce PC. Ne lis, n'affiche et ne copie jamais mes clés d'API : je les saisis moi-même dans l'application.

1. Prérequis
   - Vérifie que `gh` est installé et connecté (`gh auth status`). Sinon, télécharge depuis la page de la release avec `curl.exe -L`.
   - Vérifie que WebView2 est présent (clé `HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}` ou son équivalent sous HKCU).
   - Relève la RAM totale et libre, le CPU (nombre de cœurs) et l'espace disque libre (il faut 6 Go libres).
   - Si la v0.2.0 est installée, ne la désinstalle pas : la v0.3.0 s'installe par-dessus et garde l'historique.

2. Téléchargement et vérification
   - Dans `%USERPROFILE%\Downloads\AssistantSP-0.3.0\`, exécute `gh release download v0.3.0 -R Aliquanto3/service-public-slm-fine-tuning`. Il faut les 4 fichiers : `AssistantSP-Setup-0.3.0.exe`, `-1.bin`, `-2.bin` et `.exe.sha256`.
   - Vérifie chaque SHA-256 (`certutil -hashfile <fichier> SHA256`) contre le fichier `.sha256` et contre les empreintes des notes de la release. Arrête-toi et préviens-moi au moindre écart.

3. Installation
   - Les deux `.bin` restent dans le même dossier que le `.exe`. Lance l'installateur et laisse-moi cliquer (par utilisateur, sans droits administrateur ; SmartScreen : « Informations complémentaires », puis « Exécuter quand même »).
   - Vérifie `%LOCALAPPDATA%\Programs\AssistantSP\AssistantSP.exe`, puis « Paramètres > À propos » : version 0.3.0.

4. Modèle local seul (rien de configuré)
   - Lance l'application, mesure le temps jusqu'à l'interface utilisable, relève la RAM des processus `llama-server`.
   - Pose 2 questions réalistes (vue Question) et 1 compte rendu court ; relève le temps jusqu'au premier mot et le temps total. Vérifie dans le journal des Requêtes sortantes qu'**aucune** requête vers un modèle externe n'apparaît.

5. Modèles externes (Paramètres > Modèle externe)
   - Fais-moi ajouter, dans cet ordre, les fournisseurs pour lesquels j'ai une clé :
     1. `mistral` (API Mistral, modèle `mistral-small-latest`) ;
     2. `ovh` (OVHcloud AI Endpoints, modèle `Qwen3.6-27B` ou `Mistral-Small-3.2-24B-Instruct-2506`) ;
     3. `openrouter` (modèle `qwen/qwen3.6-27b`).
   - Pour chacun : je colle la clé, j'enregistre, je clique « Tester la connexion » ; relève le résultat (OK et latence, ou code d'échec).
   - Fais-moi relancer l'application. Vérifie l'indicateur de Mode (fournisseur de tête) et « À propos ».
   - Reprends les demandes de l'étape 4 : relève qui a répondu (ligne « Modèle : … » de l'Historique), les temps, et note mon avis sur la qualité par rapport au modèle local.
   - Journal des Requêtes sortantes : une ligne par appel externe, profil `modele-externe`, sans texte de la demande.

6. Résilience
   - Fais-moi désactiver le premier fournisseur (ou mettre une clé fausse puis tester) : la réponse doit venir du suivant, avec un bandeau qui le dit.
   - Mode hors ligne forcé (indicateur de Mode) : la réponse doit venir du modèle local, sans appel externe.
   - Coupe le Wi-Fi pendant une réponse longue si je l'accepte : bandeau ou bouton « Réessayer avec le modèle local ».

7. Onglet « Modèles » (menu « Plus »)
   - Vérifie que le tableau s'affiche, que le tri marche au clavier, que les lignes se déplient et que l'encadré « Comment lire ce tableau » est lisible. Note mes remarques sur ce qu'une équipe technique de collectivité y chercherait en plus.

8. Bilan
   - Consigne tout au fil de l'eau dans `%USERPROFILE%\Documents\recette-assistantsp-0.3.0.md` : matériel, temps, RAM, résultats des tests de connexion, qui a répondu, constats triés par gravité (bloquant, gênant, cosmétique).
   - Ne publie rien, ne pousse rien. Ne recopie jamais une clé dans ce fichier.
   - Désinstallation, seulement si je la demande (Paramètres Windows > Applications).
