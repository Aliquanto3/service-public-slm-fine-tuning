# Story C2 — jamais de réponse tronquée réutilisée

Spec : `_bmad-output/planning-artifacts/sprint-change-proposal-2026-10-20.md` (§ C2). Commit revu : `abc540d`.

## Revue

- high · corrigé · `Generateur.reponse_journalisee` (amorces CT de `seed`) reprenait une réponse tronquée journalisée à chaque relance (`ReponseTronquee` sans nouvel appel) et ignorait `max_tokens` ; filtre commun `reponse_reutilisable` appliqué.
- medium · corrigé · règle en liste noire (`length` seul) : `model_length` ou raison absente réutilisés si `max_tokens` égal ; désormais liste blanche `stop`/`tool_calls` partout (`FINS_REUTILISABLES`, `slmsp.mistral.generateur`).
- medium · corrigé · réponse fraîche `model_length` acceptée puis journalisée dans `_obtenir` ; traitée comme tronquée (`FINS_TRONQUEES`), aussi dans les fabriques du CLI (`_fabrique_depuis`, `_fabrique_courriers_depuis`).
- medium · corrigé · `appels_journalises` (estimation de coût) n'appliquait pas la même règle (sous-estimation) ; même filtre, `max_tokens` courant du gabarit par session.
- medium · corrigé · test « changement de max_tokens » n'exerçait pas le chemin réel ; refait en relançant avec une marge de raisonnement changée (nouvel appel attendu, puis réutilisation au même `max_tokens`).
- low · corrigé · tests ajoutés : `model_length` et raison absente (journalisées et fraîches), `reponse_journalisee` tronquée et autre `max_tokens`, `appels_journalises`, règle unitaire.
- info · rejeté · 3 échecs hors zone (`test_marge_raisonnement_preversion_seulement`, `test_attente_totale_bornee`, `test_critere_11_base_absente_non_creee`) : base antérieure à C1 (`6258ae7`, tests réalignés sur la config), sans lien avec C2.
