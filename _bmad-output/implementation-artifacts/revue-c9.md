# Revue story C9 (conditions Mistral)

- high, corrigé : `test_conditions_mistral_d_hier_code_1` (tests/data/test_prealables.py) cassé par C9 (la vérification automatique s'exécutait avant le préalable) ; vérification neutralisée dans ce test, nouveau test d'intégration `_generate` bloqué avant tout appel Mistral.
- medium, corrigé : journal hors convention `runs/<type>/<run_id>/` ; déplacé sous `<SLMSP_VAR_DIR>/mistral-conditions.jsonl` (état machine).
- medium, corrigé : regex de date non bornée à `[mistral]` ; bornée à la table (en-tête CRLF géré), dates entre guillemets simples ou doubles traitées.
- medium, corrigé : écriture non atomique et conversion CRLF en LF ; lecture `newline=""`, fichier temporaire puis `os.replace`.
- medium, corrigé : `TOMLDecodeError`/`OSError` avalés dans `_conditions_perimees` ; bloque désormais (`ConditionsAVerifier`). Clé absente : laissée à `charger_prealables`.
- low, corrigé : tests HTTP 404/500, page différente (déjà couverte), CRLF et autre table intacte.
- low, rejeté : HTTP 200 avec page différente sous `--verifier-seulement` : comportement identique, couvert.
