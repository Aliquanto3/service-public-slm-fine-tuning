---
title: 'Liste --candidats alignée sur le registre D8'
type: 'feature'
created: '2026-10-17'
status: 'review'
baseline_commit: '012f7f6'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/planning-artifacts/decisions.md (D4, D8)'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-hybrides-baseline.md'
warnings: []
deferred:
  - 'minicpm5-1b (candidat au fine-tuning) : masque refusé (`ErreurMasque`), donc Run refusé par `pretokeniser`. Cause (établie en revue, tokenizer local sur CPU) : l''amorce de génération se termine par `<think>\n\n</think>\n\n` avec `enable_thinking = false`, bloc que le template ne rend jamais dans un tour `assistant` ; ce n''est pas une réécriture de l''historique. Décision à confirmer par Anaël (section Revue) avant la story 11.2.'
  - 'Test réseau `test_candidat_reel_conforme` étendu aux slugs du registre D8 (tailles GGUF des fiches) mais non exécuté en revue (pas d''appel réseau) : à lancer avec `-m reseau`.'
---

## Intent
Décision d'Anaël du 2026-10-17 : `verifications.CANDIDATS` (utilisée par `slmsp fetch modeles --candidats`) suit le registre des Modèles de base de D8. Elle listait encore l'ordre D4 (ministral-3-3b, smollm3-3b, qwen-4b, ministral-3-8b, écartés) et aurait téléchargé des modèles écartés.

## Approach
- `CANDIDATS = (granite-4.0-1b, minicpm5-1b, eurollm-1.7b, qwen3.5-0.8b, qwen3.5-2b)` : les candidats au fine-tuning, puis les Qwen « Baseline seulement ». Les statuts et slugs du registre D8 correspondent à cette liste, sans écart.
- `--candidats` n'implique rien d'autre : le téléchargement et les contrôles (`dense`, `fp8`, `vision`, `chat_template`, `serveur`) parcourent la même liste, les Qwen passent `dense` grâce à `entrainable = false`, `--f16` avertit si la fiche n'a pas de `gguf_f16`, l'export d'état suit `config.slugs`. Aucun code à changer hors la constante ; pas de doc qui cite l'ancienne liste.
- `decisions.md` : une ligne sous le registre de D8, D4 non réécrite.

## Tests
`tests/fetch/test_verifications.py` : `test_candidats_alignes_sur_le_registre_d8` (égalité, aucun écarté, entraînable pour les trois premiers et pas pour les Qwen) et `test_candidat_registre_epingle` (révisions, SHA). Les assertions propres aux anciens candidats (GGUF Q4_K_M, contexte 8192, tailles réseau) passent sur `ANCIENS_CANDIDATS`. `tests/train/test_masque.py` : `eurollm-1.7b` ajouté à sa liste (tokenizer local présent, test lent passé) ; sans poids le test saute déjà (`_dossier_hf`).

## Auto Run Result
- Statut : review. Pas de fusion. `decisions.md` modifié sur demande de l'orchestrateur.
- `minicpm5-1b` n'est pas ajouté à `test_masque.py` : son template réécrit l'historique, le masque échoue (voir `deferred`). Report, pas de correctif ici. (Diagnostic corrigé en revue : c'est l'amorce, voir ci-dessous.)
- Tests ciblés : 264 passés (`tests/fetch`, `tests/cli`, `tests/train/test_masque.py`).

## Revue
Revue du 2026-10-17 (reviewer, une passe, avec la liste du second avis).

- medium, second avis 6, **reporté (décision de conception)**, diagnostic corrigé. Exécuté sur le tokenizer local de minicpm5-1b (CPU) : avec `chat_template_kwargs = { enable_thinking = false }`, l'amorce (`add_generation_prompt=True`) finit par `<|im_start|>assistant\n<think>\n\n</think>\n\n`, alors que le template rend un tour `assistant` passé ou final sans aucun bloc `<think>` (il n'en écrit un que si le contenu ou `reasoning_content` en porte, et le vide est éliminé). `texte.startswith(amorce)` échoue au premier tour assistant ; sur une conversation à tours courts, le refus sortait à tort en « ne produit aucun texte ». Sans `enable_thinking`, le masque passe. Impact : le défaut est dans le vrai chemin d'entraînement (`chargement.pretokeniser` → `masque.calculer_masque`), qui propage `ErreurMasque` : aucun faux masque, mais **tout Run sur minicpm5-1b est refusé**, ce qui bloque la story 11.2 pour ce candidat. La correction n'est pas locale : il y a un écart réel entre l'inférence (prompt terminé par le bloc vide) et ce que le template officiel sait rendre à l'entraînement ; la variante `generation` prévue par H-MASQUE ne le traite pas seule. **À confirmer par Anaël**, options :
  1. Variante d'entraînement du template (repli H-MASQUE élargi) qui écrit `<think>\n\n</think>\n\n` en tête de chaque tour `assistant` rendu, testée par égalité avec l'amorce officielle ; le masque commence après l'amorce, comme à l'inférence. Écart à AD-7 (« template officiel seul ») à consigner.
  2. Masque borné à l'amorce sans le bloc (préfixe commun) : le modèle s'entraîne sans le bloc vide qu'il voit à l'inférence. Simple, mais écart train/inférence silencieux ; déconseillé.
  3. Retirer `enable_thinking = false` pour minicpm5-1b (amorce `<|im_start|>assistant\n` seule, le masque passe) : change le mode de raisonnement de la Baseline déjà mesurée (AD-6), donc re-mesure de sa Baseline, et risque que le modèle ouvre un `<think>` à l'inférence.
  4. Sortir minicpm5-1b des candidats entraînables (`entrainable = false`, Baseline seulement).
- low, revue (même cause), **corrigé** : `intervalles_assistant` distingue désormais l'amorce non préfixe du tour rendu (message explicite, cas MiniCPM5) de la réécriture d'historique et du tour vide ; l'ensemble des cas acceptés est inchangé. Test rapide sans poids `test_amorce_absente_du_tour_rendu_refusee` (tour long et tour court).
- low, revue, **noté** (non bloquant, `entrainable = false`) : qwen3.5-0.8b passe le masque sur la conversation du test (le bloc vide est rendu après la dernière question), mais échoue sur une conversation à deux questions, avec ou sans `enable_thinking` : son template retire le bloc des tours antérieurs à la dernière question (vraie réécriture de l'historique). Même conclusion probable pour qwen3.5-2b. À traiter si un Qwen redevient entraînable.
- low, second avis 1, **corrigé** : `CANDIDATS` de `test_masque.py` = candidats entraînables du registre (granite-4.0-1b, eurollm-1.7b, minicpm5-1b en `xfail(strict=True)` tant que la décision n'est pas prise ; le xfail strict forcera la mise à jour une fois corrigé). Test lent exécuté : 2 passés, 1 xfail.
- low, second avis 2, **corrigé** : aide et docstring de `--candidats` (`cli/fetch.py`) citent le registre D8.
- low, second avis 3, **corrigé** : note datée dans `spec-modeles-octobre-2026.md` (Intent), historique non réécrit.
- low, second avis 4, **corrigé, vérification reportée** : `TAILLES_GGUF` complété depuis les commentaires `[gguf]` des fiches ; `test_candidat_reel_conforme` couvre anciens et nouveaux slugs. Non lancé (réseau) : `pytest -m reseau -k candidat_reel_conforme`.
- Complexité : 0 constat (aucune structure qui grossit pendant l'exécution dans le diff ; `intervalles_assistant` reste quadratique en nombre de tours par rendus incrémentaux, inchangé et borné par la taille d'une conversation).
- Second avis, points « sans écart » confirmés : aucune assertion perdue, `--candidats --f16` n'échoue pas, statuts `entrainable` conformes à D8.
- Tests : `tests/fetch tests/train tests/cli` 479 passés ; lent `test_candidat_reel_masque_sur_les_tours_assistant` 2 passés, 1 xfail ; contrôle rapide OK.
