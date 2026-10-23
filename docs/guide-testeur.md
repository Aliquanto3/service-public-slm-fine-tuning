# Assistant SP : guide du testeur (v0.3.1)

Merci de tester l'Assistant SP. C'est un assistant pour les agents du service public : il tourne **sur le poste, hors ligne**, avec un petit modèle (MiniCPM5-2B). Les modèles cloud sont optionnels. Durée conseillée : 30 à 45 minutes.

## 1. Installer (5 min)
- Depuis la [version 0.3.1](https://github.com/Aliquanto3/service-public-slm-fine-tuning/releases/tag/v0.3.1), télécharger les **trois fichiers** `.exe`, `-1.bin` et `-2.bin` dans le même dossier, puis lancer le `.exe`. Aucun droit administrateur n'est demandé.
- SmartScreen : « Informations complémentaires », puis « Exécuter quand même » (installateur non signé).
- Prérequis : Windows 10 ou 11 64 bits, environ 6 Go de disque libre, 16 Go de RAM recommandés.

## 2. Parcours à tester
Pour chaque tâche, noter : la réponse est-elle **juste**, **utile**, **assez rapide** ? Le comportement est-il clair ?

| # | Tâche | À essayer |
|---|---|---|
| 1 | **Question** | Une démarche courante (changer d'adresse, renouveler une carte d'identité). Vérifier que les sources citées existent et répondent à la question. |
| 2 | **Recherche de données** | Une recherche de chiffres ou de jeux de données publics. |
| 3 | **Rédaction / Compte rendu** | Coller des notes de réunion **fictives** et demander un compte rendu. |
| 4 | **Langage clair** | Coller un paragraphe administratif et le faire simplifier. |
| 5 | **Correction**, **Résumé**, **Courrier type**, **Traduction** | Un texte court à chaque fois : vérifier les différences affichées en Correction et les trois longueurs du Résumé. |
| 6 | **Historique** | Retrouver, rouvrir, supprimer puis restaurer une conversation. |
| 7 | **Retours** | Donner un avis sur une réponse (pouce, commentaire). |
| 8 | **Mode hors ligne** | Couper le réseau (ou forcer le mode hors ligne dans les Paramètres) : l'assistant doit continuer à répondre. |
| 9 | **Paramètres** | Taille du texte, choix du modèle, « À propos ». En option : ajouter un fournisseur cloud (OVHcloud gratuit, sans clé) et comparer les réponses. |
| 10 | **Détails, Modèles, Observabilité** | Ligne « Détails » sous une réponse (durée, tokens, énergie) et onglets destinés à la DSI. |

**Ne jamais coller de données réelles ou personnelles** : utiliser des textes inventés.

## 3. Points d'attention
- **Accessibilité** : tout se fait-il **au clavier** (Tab, Entrée, Échap) ? Le texte est-il lisible (contraste, taille) ? Les boutons ont-ils des libellés compréhensibles ?
- **Performance** : délai avant le premier mot, vitesse d'écriture, poste qui ralentit.
- **Robustesse** : question très longue, texte vide, arrêt d'une réponse en cours, fermeture et réouverture de l'application.
- **Confiance** : réponses inventées, sources hors sujet, mélange de langues, répétitions.

## 4. Remonter un retour
Pour chaque constat, une ligne :

| Tâche | Ce que j'ai fait | Ce que j'attendais | Ce qui s'est passé | Gravité (bloquant / gênant / mineur) |
|---|---|---|---|---|

Joindre si possible une capture d'écran et la ligne « Détails » de la réponse concernée. Préciser le poste : Windows 10 ou 11, mémoire vive, processeur.

## 5. Désinstaller
Paramètres Windows, Applications, « Assistant SP ». L'assistant demande s'il faut conserver l'historique et les retours.
