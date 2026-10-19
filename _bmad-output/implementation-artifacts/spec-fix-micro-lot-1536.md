---
title: 'Embedder : micro-lot passage à 1536, troncature de la requête signalée'
type: 'bugfix'
created: '2026-10-19'
status: 'review'
review_loop_iteration: 0
followup_review_recommended: false
context: []
warnings: []
deferred: []
---

## Intent

**Problème :** le micro-lot `passage` de bge-m3 (2048) coûte 2 402 Mo de pic de RAM, alors que le plus long passage de l'Index fait 1 165 tokens (1536 : 1 935 Mo). La requête utilisateur n'a pas de borne côté harnais, et sa troncature par le serveur n'est pas visible de la recherche.

**Approche :** `micro_lot.passage` passe à 1536 (limite effective 1 520 tokens, `texte_long` reste 8192). `RechercheIndex` relève le compteur `textes_tronques` de l'embedder et signale toute requête tronquée.

## Boundaries & Constraints

**Always :** aucune réindexation ; la requête tronquée ne lève jamais d'erreur ; pas de logique de troncature dupliquée.

**Never :** toucher `texte_long` (`data filter`), `eval/*`, l'Index construit.

## Acceptance Criteria

- Given `bge-m3.toml` et `bge-m3-f16.toml`, when chargés, then `micro_lot_pour("passage") == 1536` et `texte_long == 8192`.
- Given une requête plus longue que la limite de l'embedder, when `rechercher`, then la recherche aboutit, `requetes_tronquees` augmente et un avertissement est journalisé.
- Given un embedder sans `textes_tronques`, when `rechercher`, then comportement inchangé.

## Implémentation

- **Réindexation inutile :** `EmbedderLlama` ne refuse pas un passage trop long, il le tronque (compteur + avertissement). Tous les passages (max 1 165 tokens) tiennent sous 1 520 : les vecteurs sont identiques à ceux du micro-lot 2048. Seuls les textes entre 1 521 et 2 032 tokens changeraient, et il n'y en a pas dans l'Index. Aucun autre code ne suppose 2048 (le `2048` de `budget.py` et des runs concerne le contexte du générateur).
- **Point 2, choix :** la troncature existe déjà dans `EmbedderLlama._tronquer` (comptage exact par `/tokenize`, début conservé, `textes_tronques`, avertissement), contrairement à ce que laissait croire le brouillon. Plutôt qu'une seconde borne en caractères (approximative, dupliquée), `RechercheIndex.rechercher` compare `textes_tronques` avant et après `vectoriser` (`getattr`, donc sans changer `EmbedderPort`), incrémente `requetes_tronquees` et journalise (`slmsp.harness.recherche_index`). Déterministe (même requête, même coupe) et observable. Limite : l'information reste un compteur et un journal, pas un champ de la réponse du Harnais.
- **Point 3 :** `harness/assemblage.py:201` appelle `embedder()` d'un `ServeurLlama` créé sans `usage` : défaut `"passage"`, donc micro-lot 1536 pour la requête. C'est le bon usage (`texte_long` est réservé à `data filter`) ; aucune correction. `cli/index.py` (indexation) utilise aussi `passage`.

## Auto Run Result

- Tests : `tests/harness`, `tests/inference`, `tests/index` : 566 passés ; ruff check et format propres. Suite complète non lancée (consigne).
- Non vérifié : mesure de RAM réelle à 1536 (reprise de la mesure du 2026-10-17).
- À confirmer par Anaël : surfacer `requetes_tronquees` dans le journal d'exécution du Harnais (hors périmètre).
