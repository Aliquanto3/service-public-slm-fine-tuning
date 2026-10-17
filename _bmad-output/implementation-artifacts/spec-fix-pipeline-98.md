---
title: 'Correctifs campagne 9.8 : embedding borné (filter) et faux positifs valeur_absente (validate)'
type: 'bugfix'
created: '2026-10-17'
status: review
warnings: []
deferred: []
---

## Contexte
Campagne 9.8, run generate `20261017-073544-generate-3741`. Deux défauts bloquaient la chaîne validate, filter, build.

## Correctifs
1. **filter / embedding** (`inference/embedding.py`) : `EmbedderLlama` borne chaque texte à `contexte_max - 16` tokens (8192, le `-b`/`-ub` du serveur, voir `ServeurLlama.arguments`) avant `/v1/embeddings`. Un texte de moins de 8176 caractères ne coûte aucun appel ; sinon `/tokenize` compte, le texte est coupé au prorata (début conservé) puis revérifié. Choix : tronquer plutôt que découper et agréger (un seul vecteur par exemple, pas de changement de contrat) ou toucher à `-b` (déjà au contexte du modèle). Test : `test_texte_trop_long_tronque`.
2. **validate / valeur_absente** (`data/validate.py`, `_controler_sources`) :
   - RE : les plafonds de `[re.longueurs]` (80, 200, 400) sont des valeurs connues, et les annotations « (N mots…) » sont retirées avant l'extraction des nombres.
   - Dates (ISO, jj/mm/aaaa, « 20 avril 2021 », « 1er ») : normalisées en (année, mois, jour) des deux côtés. Une date de la sortie présente dans les sources sous une autre forme est écartée du contrôle ; sinon ses nombres sont contrôlés comme avant (pas de relâchement). La règle `infidele` de CO compare toujours les nombres bruts.
   - Gabarit `re.md` inchangé (les `session_id` RE ne bougent pas) ; le texte de sortie conservé garde son en-tête (limite assumée, nettoyage non fait).
   Tests : plafond et annotation admis, montant inventé rejeté, 80 refusé hors RE, 4 formes de dates, date inventée rejetée.

## Auto Run Result
- Rejets `valeur_absente` RE : 29/35 vers 1/35. RD inchangé (38/139) : les dates de « mise à jour » écrites par le générateur ne figurent dans aucun résultat d'outil rejoué (vérifié sur des exemples) ; ce sont des valeurs inventées, le rejet reste justifié.
- Annotation de longueur : non retirée du texte conservé. À confirmer par Anaël : nettoyage de forme ou consigne au gabarit (qui ferait repayer les 35 sessions RE).
