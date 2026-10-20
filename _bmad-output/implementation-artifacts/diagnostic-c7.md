# Diagnostic C7 — échecs des juges tiers sur les paires CR

Source : journal brut des appels OpenRouter (`%LOCALAPPDATA%\slmsp\var\appels-juges-tiers.sqlite`, 1 158 appels, 4,91 USD, tous HTTP 200) relu par la fonction de validation du projet ; aucun appel payant lancé pour ce diagnostic.

## Constat par juge et par Tâche (appels)

| Juge | Tâche | conforme | références manquantes | coupé (`length`) |
|---|---|---|---|---|
| deepseek | CR | 61 | 125 | 38 |
| deepseek | RE | 71 | 9 | 18 |
| deepseek | LC | 149 | 0 | 1 |
| deepseek | CT | 90 | 0 | 0 |
| glm | CR | 64 | 200 | 1 |
| glm | RE | 87 | 1 | 3 |
| glm | LC / CT | 150 / 90 | 0 | 0 |

Dans les `verdicts.jsonl` des runs, par juge : CR deepseek = 61 jugés, 51 `invalide`, 38 `sortie-interrompue` ; CR glm = 64 jugés, 85 `invalide`, 1 interrompue (150 paires CR chacun).

## Deux causes distinctes

1. **Références d'éléments manquantes (cause dominante, 51 puis 85 invalides CR).** Le schéma impose une entrée `presence_elements` par référence (D1…D8, A1…A20 selon l'item) mais n'a pas de `minItems` (non pris en charge en sortie structurée). Les juges renvoient 3 à 4 entrées pour 13 à 15 attendues (deepseek CR : 3,8 renvoyées pour 15,1 attendues sur les échecs ; glm CR : 3,5 pour 15,0, dont 105 réponses avec liste **vide**). Les entrées groupent plusieurs éléments en une. Les CR réussis ont en moyenne moins de références (12,8). Le second essai redonnait le même prompt : à température 0 le résultat ne change pas (1 paire identique sur 160 seulement, mais le même type d'écart), d'où 2 échecs puis verdict `invalide` mis en cache.
2. **Sortie coupée à `max_tokens` = 8000 (deepseek : 38 CR, 18 RE, 1 LC).** DeepSeek V4 Pro dépense 7 500 à 8 000 tokens en raisonnement malgré `effort = low` (CR conformes : 5 100 en moyenne, jusqu'à 7 976) ; le contenu est vide ou tronqué. Pour glm, les 4 coupures sont des boucles de répétition (contenu de 25 000 à 27 000 caractères, raisonnement faible) : un `max_tokens` plus grand ne les guérit pas.

Écartés : délai d'attente (aucun statut non 200), longueur de contexte (4 000 tokens d'entrée en moyenne), JSON illisible (0), schéma refusé par le fournisseur (0).

## Correctifs (story C7)

- `judge/tiers.py` : une sortie non conforme est renvoyée au juge dans une conversation prolongée (sa réponse, puis l'écart et la liste exacte des références dues). Le prompt initial et la clé de cache sont inchangés (l'accord mesure toujours le même prompt). Réponse vide : nouvel essai simple.
- `config/juges.toml` : `max_tokens` de deepseek 8000 → 16000 (la clé de cache ne dépend pas de `max_tokens` : les verdicts valides restent en cache). glm inchangé.
- `--rejouer-invalides` (`slmsp eval juges-tiers`, `JugeTiers(rejouer_invalides=True)`) : un verdict `invalide` en cache est archivé (`cache.archiver_invalide`, aucune suppression) puis rejugé ; sans l'option, le cache fait foi. Nécessaire : sans elle, le rejeu relirait les 136 `invalide` du cache.
- Tests : `tests/judge/test_tiers.py` (liste tronquée à 0 ou 1 entrée corrigée au second tour ; rejeu d'un `invalide` en cache).

## Rejeu (par le cache, les 12 runs partagent `verdicts.sqlite`)

Pour chaque juge `J` (`deepseek`, `glm`) et chaque run de notation parent `R` parmi `20261017-075708-qwen3.5-2b-d3bc`, `20261018-025524-qwen3.5-0.8b-3124`, `20261018-112201-minicpm5-2b-e6f2`, `20261019-210303-ft-minicpm5-2b-d267`, `20261019-212007-ft-qwen3.5-2b-5069`, `20261019-214119-ft-qwen3.5-0.8b-802f` :

`slmsp eval juges-tiers --depuis R --juge J --taches CR,LC,RE --rejouer-invalides --plafond-estime 1`

Les verdicts valides sont relus en cache (0 €). Items à rejuger : environ 109 (deepseek : 51 + 1 invalides, 38 + 18 + 1 coupés) et 89 (glm : 85 + 1 invalides, 3 coupées). Coût estimé : deepseek 1,5 à 2 USD (≈ 0,0095 USD l'appel à 16 000 tokens, 1 à 2 appels par item), glm 0,2 à 0,3 USD ; au total environ 2 à 2,5 USD (≈ 2 €), pire cas réservé plus élevé (`--plafond-estime` le borne avant tout appel). Les 4 coupures glm par répétition peuvent rester `sortie-interrompue`.
