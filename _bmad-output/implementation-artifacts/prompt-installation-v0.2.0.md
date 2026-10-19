Installe et aide-moi à tester l'Assistant SP v0.2.0, une application Windows avec SLM local, publiée sur https://github.com/Aliquanto3/service-public-slm-fine-tuning/releases/tag/v0.2.0. Je fais les tests moi-même ; toi, tu prépares, tu vérifies et tu me guides. Ne modifie rien d'autre sur ce PC que l'installation de l'application.

1. Prérequis
   - Vérifie que `gh` est installé et connecté (`gh auth status`). Sinon, télécharge depuis la page de la release avec `curl.exe -L`.
   - Vérifie que WebView2 est présent : clé `HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}` ou son équivalent sous HKCU. Il l'est normalement sur Windows 11.
   - Relève la RAM totale et libre, le CPU (nombre de cœurs) et l'espace disque libre. Il faut 6 Go libres : 2,7 Go à télécharger et 3,1 Go installés.

2. Téléchargement et vérification
   - Dans `%USERPROFILE%\Downloads\AssistantSP-0.2.0\`, exécute `gh release download v0.2.0 -R Aliquanto3/service-public-slm-fine-tuning`. Il faut les 4 fichiers : `AssistantSP-Setup-0.2.0.exe`, `-1.bin`, `-2.bin` et `.exe.sha256`.
   - Vérifie chaque SHA-256 (`certutil -hashfile <fichier> SHA256`) contre le fichier `.sha256`. Attendus :
     - `.exe` : 85329cfa9501d7942a635f4d0ebf8b9756571760afd5d4e19d003e895537c699
     - `-1.bin` : cf725c3fa17d98bff3173414db33b94d22bf5db65ebe043a009d0aa224f09ecd
     - `-2.bin` : 0db81dee1aca10204136568c56fa0f9218c8d7e8202a15edf961c23449640d2f
   - Arrête-toi et préviens-moi au moindre écart.

3. Installation
   - Les deux `.bin` doivent rester dans le même dossier que le `.exe`.
   - Lance l'installateur et laisse-moi cliquer. L'installation se fait par utilisateur, sans droits administrateur. SmartScreen peut demander « Informations complémentaires », puis « Exécuter quand même », car l'installateur n'est pas signé.
   - Variante silencieuse si je te le demande : `AssistantSP-Setup-0.2.0.exe /VERYSILENT /SUPPRESSMSGBOXES /LOG=%TEMP%\assistantsp-install.log`.
   - Vérifie ensuite `%LOCALAPPDATA%\Programs\AssistantSP\AssistantSP.exe` et le raccourci du menu Démarrer.

4. Premier lancement (MiniCPM5-2B, modèle par défaut)
   - Lance l'application et mesure le temps jusqu'à ce que l'interface soit utilisable.
   - Pendant ce temps, relève la RAM des processus `llama-server` (Get-Process), et vérifie dans `%LOCALAPPDATA%\AssistantSP\var\journaux\llama-server-generation-*.log` la ligne `model loaded` et le chemin du modèle `minicpm5-2b`.
   - Vérifie « Paramètres > À propos » : version 0.2.0, modèle `minicpm5-2b`.

5. Tests d'interface avec Granite 4.0 350M (rapide, réponses de faible qualité, c'est normal)
   - Fais-moi choisir « Paramètres > Modèle > granite-4.0-350m », puis fermer et relancer l'application. Vérifie dans le journal que c'est bien granite-4.0-350m qui est chargé.
   - Guide-moi vue par vue, avec une courte liste de contrôle pour chacune (affichage, boutons, copier, historique, retours, messages d'erreur, clavier, redimensionnement de la fenêtre) :
     - Question ;
     - Recherche de données ;
     - Rédaction ;
     - Compte rendu (coller une courte transcription fictive) ;
     - Langage clair ;
     - Correction (différences visibles) ;
     - Résumé (trois longueurs) ;
     - Courrier type ;
     - Traduction (cinq langues, l'arabe de droite à gauche) ;
     - Historique et retours (export anonymisé) ;
     - Paramètres ;
     - indicateur de mode hors ligne / connecté et journal des requêtes sortantes ;
     - bouton « Vérifier en ligne » de la vue Question.
   - Note mes remarques au fur et à mesure dans `%USERPROFILE%\Documents\recette-assistantsp-0.2.0.md` : vue, constat, gravité (bloquant, gênant, cosmétique), capture si je t'en donne une.

6. Tests sur le fond avec MiniCPM5-2B
   - Fais-moi revenir à `minicpm5-2b`, puis relancer l'application.
   - Propose-moi 2 ou 3 demandes réalistes par vue principale : Question, Recherche de données, Compte rendu, Langage clair, Résumé. Pour chacune, relève le temps jusqu'au premier mot, le temps total et la RAM maximale.
   - Je juge la qualité ; tu consignes dans le même fichier.

7. Bilan
   - Résume le fichier de recette : matériel, temps de démarrage, RAM, débit, liste des constats triés par gravité.
   - Ne publie rien, ne pousse rien : je rapporterai ce fichier au projet moi-même.
   - Désinstallation, seulement si je la demande : Paramètres Windows > Applications ; la question « Conserver l'historique et les retours ? » apparaît.
