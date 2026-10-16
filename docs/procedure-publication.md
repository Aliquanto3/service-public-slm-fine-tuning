# Procédure de publication d'un modèle (téléversement manuel)

Décision Q8 : `slmsp` prépare et vérifie un dossier **hors ligne** ; Anaël le téléverse lui-même. Aucune commande `slmsp` n'envoie quoi que ce soit (AD-4).

## 1. Préparer le dossier

Prérequis : un run `export` complet (story 10.6) et un Comparatif (`slmsp compare comparatif`, story 11.1). La licence du Modèle de base doit avoir été relue sur sa fiche Hugging Face, puis `verifie_le` renseigné dans `config/publication.toml`.

```
uv run slmsp publication preparer --modele <slug> --export <run_id_export> ^
  --comparatif runs/compare/<run_id>/comparatif.md --sortie publication/<nom>
```

Le dossier contient `README.md` (fiche), `LICENSE`, le GGUF, `COMPARATIF.md` et `SHA256SUMS`. Si un contrôle échoue (formulation de certification, texte du Jeu d'évaluation, secret, fichier de `eval/` ou `data/train/`), le dossier est renommé `<sortie>.refuse` et la commande échoue.

## 2. Compléter la fiche

Remplacer chaque emplacement `<À COMPLÉTER PAR ANAËL : …>` du `README.md` (présentation, sources réellement utilisées, commentaire des résultats, limites et usages déconseillés). Ne rien affirmer que le Comparatif ne montre pas. Aucune certification n'est revendiquée (PRD §6.1). Relancer ensuite la commande dans un nouveau dossier pour revérifier, ou vérifier à la main `SHA256SUMS` : `sha256sum -c SHA256SUMS`.

## 3. Téléverser en privé

Interface web, ou CLI `hf` (hors de `slmsp`) :

```
hf auth login
hf repo create <organisation>/<nom> --private
hf upload <organisation>/<nom> publication/<nom> .
```

## 4. Relire, puis rendre public

Relire le dépôt privé tel qu'il s'affiche (fiche, licence, empreintes). Passer ensuite le dépôt en public dans ses paramètres.

## À ne jamais publier

Le jeu d'entraînement (v1) ni le Jeu d'évaluation maison (`eval/`) : le second est exclu pour éviter la contamination.
