# Brouillons du Jeu d'évaluation v1.1

Ce dossier contient les brouillons des items et les verdicts de la double vérification (SPEC §5). Il n'est jamais lu par le banc : seul `eval/jeu/v1.1/items.jsonl`, produit par `assembler --version v1.1`, fait foi après le gel par `slmsp eval gel`.

## Origine de la v1.1

- **Base.** Copie intégrale de `eval/construction/v1.0/` (brouillons, `verification/`, ce README), puis corrections arbitrées par Anaël dans `eval/revue/arbitrages-v1.1.md` (options cochées et section « Ajustements validés (2026-10-13) », qui fait foi). Les verdicts v1.0 restent valables pour les items inchangés ; `verification/` n'est modifié qu'en ajout.
- **Items modifiés** (même `id`, `version_item: 2`, revérifiés par un vérificateur indépendant) :
  - Q-042 (A) : plus de demande de plafond de l'indemnité de rupture (la fiche F31094 de l'Index écrit « au 24e », le décret dit un douzième) ; l'item garde le calendrier et le remboursement, `difficile`.
  - CR-006 et CR-021 (F) : transcriptions allongées au-delà de 6 500 mots (6 621 et 6 571 selon `slmsp.core.texte.compter_mots`), par des échanges sans nouvelle décision, action ni piège ; références inchangées (cas limite de FR-13).
  - RD-010, RD-017, RD-023, RD-030, RD-039 (G1) : `valeurs_attendues.colonnes` selon le tableau G1.
  - RD-017, RD-019, RD-031 (G2) : fragments de contrôle resserrés ; « REI » en mot entier par la nouvelle règle `mot_entier_un_de` (combinée en « ou » avec `contient_un_de`).
  - CO-001, CO-002, CO-006, CO-007, CO-011, CO-012 (G4) : `fictif: true` (textes réels dont les fautes ont été injectées), rien d'autre.
- **Remplacements (E).** Q-044 (facile), Q-046 (moyen) et Q-050 (difficile), trois items `collectivites`, sont rejetés (motif `autre`, arbitrage E) et remplacés par Q-068, Q-069 et Q-070, aux mêmes difficultés, sur les marchés publics (publicité, seuils de procédure, délais ; fiches F23371 et F32049 de `entreprendre.service-public.gouv.fr`). Les numéros Q-061 à Q-063 cités par l'arbitrage étaient déjà pris (Q-061 rejeté en v1.0) : décision d'Anaël du 2026-10-13, numéros libres suivants.
- **Inchangés.** Tous les autres items, y compris CT-016, `consulte_le` et `licence_source` : la clé du cache des verdicts (`judge/cache.py`) dépend du contenu de chaque item, seuls les items modifiés ou nouveaux repassent au Juge.

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
| `assembler --version v1.1` | écrit `eval/jeu/v1.1/items.jsonl` (toujours passer `--version` : le défaut est `v1.0`) |
| `changements --version v1.1 [--reference v1.0]` | avant le gel : compare `eval/jeu/v1.0/items.jsonl` (gelé) et `eval/jeu/v1.1/items.jsonl` (assemblé) ; écrit `eval/revue/changements-v1.0-v1.1.jsonl` (une ligne par item nouveau, modifié ou retiré ; pour un modifié, `champs` donne l'ancienne et la nouvelle valeur de chaque champ changé, objets comparés clé par clé, et un retiré porte son dernier verdict) et `eval/revue/changements-v1.0-v1.1.md` (une fiche par item, différences ligne à ligne pour les textes longs) ; refuse (code 2, aucun fichier) si l'un des deux `items.jsonl` manque ou est illisible, si les versions sont identiques ou si un export existe déjà |
| `revue --version v1.0` | après le gel : exporte l'échantillon `echantillons.relecture` du manifeste dans `eval/revue/echantillon-revue-v1.0.jsonl` (lignes de `items.jsonl` telles quelles) et `eval/revue/echantillon-revue-v1.0-lecture.md` (une fiche par item, champs rendus lisiblement) ; refuse (code 2, aucun fichier) si le manifeste manque, si un `id` est absent de `items.jsonl` ou si un export existe déjà |

Options et comportements :
- `assembler`, `composition`, `rejets`, `revue` et `changements` acceptent `--racine <dossier>` (racine du dépôt, défaut `.`) et `--version` (`vN` ou `vN.M`).
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
- Champs communs : `id`, `tache`, `difficulte` (`facile`, `moyen`, `difficile`), `theme` (Q, RD, LC, RE), `entree`, `parametres`, `provenance` (liste, chaque entrée avec `consulte_le`), `licence_source`, `fictif`, `version_item` (1 à la création, incrémenté quand un item relu est corrigé : 2 pour les items modifiés en v1.1).
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

## Clôture de la v1.1

1. `construire_jeu.py assembler --version v1.1`, puis `uv run slmsp eval gel --version v1.1 --verifier-seulement` (225 items stricts, 0 erreur, 0 écart).
2. `construire_jeu.py changements --version v1.1` : export pour la relecture d'Anaël, **avant** tout gel.
3. Après la relecture seulement : `uv run slmsp eval gel --version v1.1 --statut relu --graine 20261013 --date-reference 2026-10-12`, puis `construire_jeu.py revue --version v1.1` et `tests/eval_outils/test_jeu_v1.py` ; commit de gel limité à `eval/jeu/v1.1/`, `eval/revue/` et `eval/construction/v1.1/`.

`--date-reference` inscrit dans `MANIFEST.json` l'ancre de date des références (`date_reference`, arbitrage G3) : montants et dates du jeu font foi au 2026-10-12. Elle est refusée si elle est mal formée, postérieure à la date du gel ou donnée avec `--verifier-seulement`. La grille du Juge n'est pas modifiée (figée par le manifeste v1.0).

## Limites documentées (v1.1)

- **Métadonnées hétérogènes (G4).** `consulte_le` mêle dates et dates-heures, et `licence_source` compte de nombreuses formulations. Elles ne sont pas harmonisées : les modifier changerait presque tous les items, donc toute la clé du cache des verdicts, et imposerait de rejuger la Baseline. Les CO réels sont `fictif: true` avec une provenance de fiche réelle : `fictif` signifie ici « contenu modifié pour l'évaluation », pas « contenu inventé ».
- **CT-016 et le CRPA (D1).** L'item reste inchangé (le schéma CT n'a pas de champ `pieges`). Un centre hospitalier public relève aussi du CRPA : des mentions exactes de l'article R. 112-5 (date de réception, délai, silence, voies de recours) ajoutées à l'accusé de réception ne sont pas des inventions et ne doivent pas être pénalisées, même si la consigne demande de s'appuyer sur le seul extrait de la fiche F12210.
- **Libellés CT listés (D2).** Chaque consigne CT donne la liste exacte des libellés d'emplacement, ce qui rend la Tâche plus facile : le contrôle automatique « aucune valeur inventée » exige le libellé exact. C'est une limite du score CT.
- **Items « sans réponse » (H).** Leur absence de source n'est prouvée que sur l'Index `20260926` ; il faut les revérifier à chaque nouvel Index.
- **Plafond de Q-042 (A).** La fiche F31094 de l'Index reste fausse sur le plafond (« au 24e ») : l'item ne l'évalue plus, mais un modèle fidèle à l'Index peut toujours citer ce plafond hors de la question posée.
