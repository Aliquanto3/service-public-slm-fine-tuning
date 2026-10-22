# Scripts des campagnes d'entraînement (archivés)

Scripts Windows qui ont piloté les campagnes de fine-tuning des 19 au 22 octobre 2026 (entraînement sous garde de RAM, export, notation, blocage de la mise en veille). Le fine-tuning est arrêté depuis le 22/10 ; ils sont gardés pour reproduire ou reprendre les essais décrits dans `docs/bilan-fine-tuning.md`.
- `campagne-run.ps1` : un run d'entraînement (TOML en argument) sous garde RAM, puis export et notation, avec garde-fou de coût.
- `garde_ram.py` : interrompt l'entraînement si la RAM du poste dépasse un seuil (`GARDE_RAM_GO`, 28 par défaut).
- `veille.ps1` : empêche la mise en veille pendant un run long.
Les chemins absolus sont ceux du poste de développement.
