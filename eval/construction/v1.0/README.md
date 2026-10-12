# Brouillons du Jeu d'évaluation v1.0

Ce dossier contient les brouillons des items et les verdicts de la double vérification (SPEC §5). Il n'est jamais lu par le banc : seul `eval/jeu/v1.0/items.jsonl`, produit par `assembler`, fait foi après le gel par `slmsp eval gel`.

Outil : `eval/outils/construire_jeu.py` (lancé depuis la racine du dépôt).

```
uv run --no-project --python 3.12 --with duckdb --with openpyxl python -I eval/outils/construire_jeu.py <commande>
```

| Commande | Rôle |
|---|---|
| `sources --dest <dépôt principal>/data/raw/eval-sources` | instantanés des sources (HF épinglé par révision, pages de la Liste blanche avec `--page URL`), inventoriés dans `INDEX.json` |
| `fiche F1344 --dest …` | texte d'une fiche service-public (chunks numérotés) |
| `composition` | écarts des brouillons avec SPEC §2 et anomalies de structure (Markdown) |
| `rejets` | taux de rejet par Tâche et par motif (Markdown) |
| `assembler --version v1.0` | écrit `eval/jeu/v1.0/items.jsonl` |

Options et comportements :
- `assembler`, `composition` et `rejets` acceptent `--racine <dossier>` (racine du dépôt, défaut `.`) et `--version` (`vN` ou `vN.M`).
- `assembler` refuse d'écrire (code 2, aucun fichier) si un brouillon ou une ligne de vérification est illisible, si un `id` est mal formé ou dupliqué (`Q-001` et `Q-0001` comptent comme doublons), si un verdict est inconnu, ou si aucun item n'est retenu. Il refuse aussi si `eval/jeu/<version>/MANIFEST.json` existe (jeu gelé) ; `--force` passe outre.
- Les items sans verdict sont assemblés mais listés (comme les verdicts sans brouillon) par `assembler` et `composition`.
- `sources --quoi service-public catalogue legi questions` choisit les sources (défaut : toutes) ; `--legi-codes crpa casf cgct civil ccp` (défaut) accepte aussi un nom de dossier LEGI brut (`code_du_travail`) ; `--page URL` (répétable) fige une page d'un hôte de la Liste blanche. `--page` seul, sans `--quoi`, ne télécharge aucune donnée Hugging Face.
- Un fichier déjà présent n'est pas retéléchargé ; sa taille (et son SHA-256 s'il n'est pas encore dans l'INDEX) est comparée à la révision courante, et un écart fait échouer la commande. Après un écart de taille ou de SHA-256 au téléchargement, le `.part` est conservé.
- `sources --force` retélécharge ; l'ancien fichier n'est jamais supprimé : il est archivé sous `<nom>.ancien-<sha12><suffixe>`, avec son entrée INDEX (`archive_le`, `remplace_par`).
- `fiche` lit le parquet local de service-public, puis, à défaut, les instantanés du calibrage `hf/sp_<id>.json`.

## Brouillons : `<CODE>.jsonl`

- Un fichier par Tâche : `Q.jsonl`, `RD.jsonl`, `CR.jsonl`, `LC.jsonl`, `CO.jsonl`, `RE.jsonl`, `CT.jsonl`, `NR.jsonl`. Tout autre fichier `.jsonl` à ce niveau fait échouer l'assemblage.
- Un item JSON par ligne, en UTF-8. Les lignes vides sont ignorées.
- `id` = `<CODE>-NNN` (au moins trois chiffres, à partir de `001`), avec le code du fichier. Jamais `R-` ni `RS-` : utiliser `RD-` et `RE-` (SPEC §7 bis).
- Un item rejeté est soit corrigé sous le même `id` puis revérifié (le dernier verdict l'emporte), soit remplacé par un nouvel item au numéro libre suivant. Un `id` rejeté n'est jamais réattribué à un item d'un autre sujet.
- Champs communs : `id`, `tache`, `difficulte` (`facile`, `moyen`, `difficile`), `theme` (Q, RD, LC, RE), `entree`, `parametres`, `provenance` (liste, chaque entrée avec `consulte_le`), `licence_source`, `fictif`, `version_item` (= 1).
- `entree` est un texte pour Q, RD et NR, et un objet à clés nommées pour CR, LC, CO, RE et CT.
- Thèmes (slugs SPEC §2) : `social-autonomie`, `etat-civil-papiers`, `travail-emploi`, `collectivites`, `famille-education-sante`, `fiscalite-locale`.
- Champs propres à chaque Tâche : SPEC §3 et contexte de l'epic 7. Le format de référence est `eval/calibrage/echantillon-calibrage.jsonl`.
- Q issu d'une amorce réelle : `amorce_usager` non vide, et une entrée de `provenance` qui cite `sp_questions_corpus` ou `assistant_ia_questions_corpus`.
- RD : le producteur est lu dans `producteurs` (liste), sinon `producteur`, sinon `reponse_reference.jeu_principal.producteur`.

## Vérifications : `verification/<CODE>.jsonl`

Une ligne JSON par verdict du vérificateur indépendant. Le fichier est en ajout seul : on n'efface ni ne modifie une ligne. Pour un même `id`, **la dernière ligne valide du fichier l'emporte** ; une ligne au verdict inconnu (`rejeté`, absent…) est ignorée, signalée, et bloque l'assemblage.

| Champ | Valeurs |
|---|---|
| `id` | identifiant de l'item vérifié (`Q-001`) |
| `verdict` | `accepte` ou `rejete` |
| `motif` | si `rejete` : `fait_absent_source`, `url_morte_ou_differente`, `ambigu`, `doublon_thematique` ou `autre` |
| `detail` | texte libre : le fait manquant, l'URL fautive, l'item jumeau… |
| `verifie_le` | date ISO de la vérification (`2026-10-12`) |

Exemple :

```json
{"id": "Q-007", "verdict": "rejete", "motif": "url_morte_ou_differente", "detail": "F1234 redirige vers une autre fiche", "verifie_le": "2026-10-12"}
```

Un item dont le dernier verdict est `rejete` est exclu par `assembler` et par `composition`, et signalé. Les taux de rejet de `rejets` se calculent sur l'ensemble des verdicts (rejets / verdicts).
