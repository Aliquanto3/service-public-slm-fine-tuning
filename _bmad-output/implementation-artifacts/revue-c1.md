# Revue C1

## Revue C1
- medium, corrigé : `config/mistral.toml` `duree_totale_max_appel` 900 -> 1800. Avec `delai_appel` 600, tout Retry-After > 300 s n'était jamais attendu (écoulé + attente + 600 > 900). Test ajouté `test_retry_after_plausible_attendu_avec_la_config_reelle` (config réelle, Retry-After 400 s attendu).
- low, corrigé : `test_generateur.py` `marge > 0` -> `marge >= 0` (invariant « préversion seulement » conservé, plus de dépendance à la valeur de campagne).
- low, corrigé : `test_claude.py` (timeout lu dans `charger_juges().principal.delai_appel`), `test_second.py` ligne 234 (max_tokens lu de la config) et 511 (`> 0`, valeur de campagne non figée).
- low, rejeté : `tests/mistral/test_client.py:103` : le 4000 est l'argument `max_tokens` passé par le test lui-même (ligne 55), pas une valeur de config.
- low, rejeté : `tests/budget/test_tarifs.py:85` `<=`, acceptable.
