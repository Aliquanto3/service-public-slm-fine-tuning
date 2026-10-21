# Revue de la story 17.6 (2026-10-21, reviewer Opus)

Base : branche rebasée sur main (1dacc17) ; conflit `config/tarifs.toml` résolu en gardant
les deux ajouts (Qwen3.8-27B et `mistral-small-latest`).

## Constats

| # | Sévérité | Constat | Suite |
|---|---|---|---|
| 1 | medium | `max_completion_tokens` et `max_output_tokens` admis dans `parametres_supplementaires` : contournent le `max_tokens` du pire cas | corrigé (`CLES_INTERDITES`, test) |
| 2 | medium | Sans usage, le raisonnement reçu (jamais émis) n'entrait pas dans l'estimation de sortie ; outils non comptés si le flux est coupé | corrigé (`EtatFlux.caracteres_raisonnement`, `_Suivi.total_sortie()`, test) |
| 3 | low | Estimation des tokens à ÷ 3, peu prudente pour le plafond | corrigé : ÷ 2,5 (majoration 1,25 du pire cas conservée) |
| 4 | low | CSV : tabulation et retour chariot en tête de cellule non protégés | corrigé (test) |
| 5 | low | `client_externe` sans observabilité (ou sans plafond) : appel externe sans plafond | corrigé : fail-closed, `tarif-inconnu`, aucune requête (test) |
| 6 | medium | Impact : coefficients écrits de mémoire, non conformes à EcoLogits (f_E linéaire, serveur non partagé par le lot, GPU non arrondi en puissance de 2) ; Mistral Small 4 traité comme un dense 24 Md | corrigé : méthode réalignée sur ecologits.ai/latest/methodology/llm_inference (relevé du 2026-10-21), cité dans le code, `impacts.toml` et l'aide « Méthode » ; Mistral Small 4 à 119 Md, actifs 6 à 24 Md (centre 15, à vérifier) ; tests f_E(27) et cas complet |
| 7 | info | PUE OVH 1,26 non sourcé | remplacé par 1,20 (défaut EcoLogits) ; Mistral 1,16 |
| 8 | info | Edge cases relus sans défaut : réservation rendue entre relances, régularisation sur le mois de la réservation, mesure dans `finally`, aucune colonne de contenu, local sans réseau, `config/` embarqué en entier par `construire_application.py` | rejeté (pas de défaut) |
| 9 | info | `tests/evaluation/test_modele_distant.py::test_budgets_du_depot_imputent_par_fournisseur` échoue aussi sur main (1dacc17) | hors story, à traiter à part |

## Valeurs d'impact (méthode réalignée)

- Qwen3.6-27B via OpenRouter (USA, PUE 1,2), 2 000 tokens d'entrée, 300 de sortie, 3 s :
  f_E = 5,593e-5 Wh/token, 1 GPU ; énergie 0,0225 Wh (0,0206 à 0,0393), 0,0083 g CO2e
  (0,0076 à 0,0145) ; coût 0,0011 € (0,25 et 2,00 USD par million, taux 1).
- Local, 3 s à 25 W : 0,0208 Wh (0,0104 à 0,0313), 0,0011 g CO2e (mix France 52 g/kWh), 0 €.
