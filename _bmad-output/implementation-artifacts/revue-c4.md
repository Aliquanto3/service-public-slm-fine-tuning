# Revue C4

- medium, corrigé : reprise silencieuse d'un run d'avant le filtre. `filtre_longueur` (longueur_max, marge, retenus, exclus) ajouté à la configuration résolue ORPO, que `--reprendre` compare ; test `test_reprise_orpo_refusee_sans_filtre_de_longueur`.
- medium, rejeté : invariants de campagne. `longueur_max` y figure déjà ; les paires retenues sont propres à ORPO et feraient échouer la comparaison avec les runs SFT de la même campagne (dérogation FR-34). Couvert par la reprise ci-dessus.
- medium, corrigé : `diagnostic-c4.md` (cause = troncature TRL défectueuse, filtre = stabilité, piste suivante documentée non codée).
- low, corrigé : test du tokenizer réel Qwen3.5 (ignoré si absent, sans réseau).
- low, corrigé : frontière -1/0/+1 testée.
- low, corrigé : affirmation « réglage non appliqué par TRL » reformulée.
