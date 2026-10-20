# Revue de la story C8 (purge des intermédiaires d'export)

Commit revu : `a46530e` (branche `story/c8-purge-export`). Second avis Haiku, puis revue Opus.

| # | Sévérité | Décision | Constat et correctif |
|---|---|---|---|
| 1 | high | corrigé | `exports_notes` comptait toute notation, même `en_cours` ou `partiel-erreur`. Seules les notations au statut courant `complet` comptent (`statut_courant()`). Tests : notation sans statut final, `partiel-erreur`, `interrompu` → refus. |
| 2 | medium | corrigé | `--purger-intermediaires` purgeait sans notation, contre la décision d'Anaël (runs notés seulement). Option retirée (réversible : rien n'est supprimé à l'export) ; un export réussi rappelle `slmsp export purger --tous-notes`, à lancer après notation. |
| 3 | medium | corrigé | Liens symboliques et jonctions : tout intermédiaire qui est un lien, ou qui en contient un, est refusé (`PurgeRefusee`) ; la taille ne compte que les fichiers réels (`os.walk` sans suivre les liens, `lstat`) ; le `chmod` de `rmtree` refuse un chemin lien ou hors du dossier de l'export. Test avec un lien vers un dossier externe gardé. |
| 4 | medium | corrigé | Export au statut `complet` exigé, même avec `--forcer-non-note`. Q4_K_M : fichier réel, ≥ 1 Kio et entre 10 % et 100 % du GGUF F16. L'en-tête GGUF n'est pas relu ici (règle d'architecture : pas de lecture de fichier hors `core.artefacts` dans `train`) ; l'export `complet` a déjà relu le chat template du Q4_K_M (`controler_format`). |
| 5 | medium | corrigé | Échec de suppression : événement `purge` avec `partiel: true`, ce qui a été supprimé et l'erreur, puis `PurgePartielle` ; `--tous-notes` poursuit les autres exports et sort en erreur. Test avec un `unlink` qui échoue. |
| 6 | low | corrigé | `espace_libre_go` < 1 Gio désactivait le contrôle : la valeur fixe est toujours contrôlée. |
| 7 | low | corrigé en partie | Config `[export]` lue sous `config/` du projet, comme les autres configs (`llamacpp.toml`, modèles) ; fichier absent → valeurs par défaut. |
| 8 | low | corrigé | Test du Q4_K_M paramétré sans effet : chaque cas (vide, absent, trop petit, ≥ F16) est maintenant distinct. |
| 9 | low | corrigé | `--dry-run`, `--tous-notes`, `--forcer-non-note` (et `--base` avec `purger`) hors de leur contexte : refus d'usage au lieu d'être ignorés. |
| 10 | low | corrigé | Lien cassé : détecté par `os.path.lexists` puis refusé comme lien. |

Contrôles : tests ciblés `tests/train`, `tests/cli`, `tests/test_architecture.py` (579 réussis), ruff, format, contrôle rapide OK. D1 : fixtures factices (octets sans contenu), aucun exemple ni donnée d'entraînement.
