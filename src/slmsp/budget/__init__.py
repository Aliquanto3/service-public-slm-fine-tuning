"""Registre de budget des API payantes (D1.6, AD-5, AD-26).

- `slmsp.budget.config` : plafonds (`config/budgets.toml`) et tarifs datés (`config/tarifs.toml`).
- `slmsp.budget.tarifs` : coût pire cas et coût réel d'un appel, en euros.
- `slmsp.budget.registre` : `RegistreBudget`, base SQLite unique par machine dans
  `SLMSP_VAR_DIR`, qui réserve le pire cas avant chaque tentative et refuse au plafond
  (`BudgetEpuise`, code 3) ; `releve` le relit sans rien modifier.

Le registre ne connaît aucune remise à zéro ni suppression : changer de `campagne_id`
démarre une nouvelle campagne, les lignes anciennes restent en base.
"""
