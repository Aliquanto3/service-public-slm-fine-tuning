# Story 9.11 : consigne de forme dans le gabarit RE

Gabarit `config/prompts/generateur/re.md` en version 2 : pas de titre ni d'intertitre en première ligne, pas de phrase d'annonce. Test `test_consigne_de_forme_re`.

## Revue

- low · second avis · rejeté · diff limité au gabarit et au test, D1 respecté.
- low · second avis · rejeté · seules les sessions RE changent de session_id, pas de fuite dans les messages SFT.
- low · second avis · rejeté · un run data-generate partiel ne se reprend pas avec le nouveau gabarit : nouveau run prévu.
- Reviewer : aucun défaut medium ou high. Rebase sur main (8f0edb9) propre, 165 tests ciblés verts, ruff vert.
- Report : la disparition effective du préfixe « Résumé (80 mots max.) : » dépend de Mistral réel ; à vérifier sur le nouveau run RE (compter les sorties commençant par « ** » ou « Résumé »).
