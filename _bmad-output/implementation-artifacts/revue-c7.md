# Revue C7 (juges tiers, échecs CR)

Second avis de départ, puis relecture du commit bfba6e5.

| # | Sévérité | Constat | Décision |
|---|---|---|---|
| 1 | medium | `juger` archivait l'invalide avant les tests d'arrêt et de budget | Corrigé : `_en_cache` n'archive plus ; `_liberer` archive après la première réponse exploitable (ni erreur API, ni budget, ni sortie interrompue). Tests 401 et budget épuisé : cache et compteur intacts. |
| 2 | medium | Pire cas estimé à 1 appel par item alors que la relance corrective en fait ECHECS_MAX | Corrigé : pire cas sur ECHECS_MAX appels, le suivant majoré de `max_tokens` + 300 tokens de correction en entrée. Le coût estimé (typique, 1 appel) est inchangé, donc le plafond `--plafond-estime` aussi. |
| 3 | low | `archiver_invalide` réécrit une clé (UPDATE), contre l'invariant append-only | Corrigé par documentation : dérogation unique, inscrite dans le docstring de `cache.py` (la ligne est conservée, seule la clé change). Table d'archives rejetée : touche le schéma pour un usage ponctuel. |
| 4 | low | Plusieurs runs partageant une clé : réarchivage multiple | Corrigé : une archive par clé et par instance de juge (`_rejoues`). Un lancement CLI ne juge qu'un run et dédoublonne déjà les clés. |

D1 : aucune donnée ni amorce rédigée par Claude (fixtures factices seulement).
