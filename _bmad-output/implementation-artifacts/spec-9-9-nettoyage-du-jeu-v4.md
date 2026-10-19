---
title: "Story 9.9 — Nettoyage déterministe du jeu SFT (v4)"
type: 'feature'
created: '2026-10-19'
status: ready-for-dev
baseline_revision: '7b7889b'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-6-etape-build.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-7-paires-de-preference-orpo.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-rd-connecte.md'
  - '{project-root}/_bmad-output/implementation-artifacts/etat-run-2026-10-19-portable.md'
---

<intent-contract>

## Intent

**Problem:** le fine-tuning sur v2 dégrade MiniCPM5-2B (Qualité 41,1 → 35,6 en M1). Cause probable : le style des cibles. 65 réponses LC sur 69, 59 Q sur 92 et 59 RD sur 91 ouvrent par une ligne « Voici… » que le modèle recopie ; et les cibles dépassent le plafond de génération de l'évaluation (`config/evaluation.toml` `[generation].max_tokens = 1024`, le même pour toutes les tâches) : mesuré avec le tokenizer de minicpm5-2b, **76 CR sur 76** et 2 RD sur 91 le dépassent. Le modèle apprend des réponses que l'évaluation coupe.

**Approach:** décision d'Anaël du 19 au matin. Une règle déterministe, sans appel payant ni régénération, appliquée au moment du build, comme R7 §0 (« normaliser au build », `src/slmsp/data/build.py:296-300`). Nouvelle commande :

`slmsp data build --nettoyage --depuis <BUILD_RUN_ID> --modele base:<slug>`

Elle lit le jeu SFT du run `data-build` donné (v2 : `20261018-115927-build-424c`, SHA revérifié contre son MANIFEST, comme `preferences._jeu_sft`), applique trois opérations et écrit une nouvelle version `data/train/vN/{train.jsonl, MANIFEST.json}` (v4, puisque v3 porte les paires ORPO), avec un run `runs/data-build/<run_id>/` qui contient le rapport.

1. **Préambule retiré.** Pour la dernière réponse `assistant` (la cible) : si sa première ligne non vide, une fois retirés les marqueurs Markdown de tête (`#`, `*`, `_`, espaces), commence par `Voici` (casse exacte), **et** qu'il reste du texte non vide après cette ligne, alors cette ligne et les lignes vides qui la suivent sont retirées. Les marqueurs de fin de la ligne (`**`) partent avec elle. Rien d'autre n'est modifié : pas de réécriture, pas de capitalisation. Une cible d'une seule ligne qui commence par « Voici » est laissée telle quelle et comptée (`preambule_seul`). Formes observées dans v2 : « Voici la réponse fondée uniquement sur les passages fournis : » (Q, RD, LC, generique) et « **Voici votre … : ce que vous devez savoir** » (LC, titre en gras).
2. **Longueur bornée : écarter, pas tronquer.** Après l'étape 1, une cible dont le nombre de tokens (tokenizer du `--modele`, `tokenizers.Tokenizer` sur `models/<slug>/hf/tokenizer.json`, sans tokens spéciaux) dépasse `max_tokens` de l'évaluation (lu dans `config/evaluation.toml`, pas recopié) est **écartée** avec le motif `longueur`. Justification : tronquer produirait des cibles coupées en pleine phrase suivies d'une fin de séquence, ce qui apprend au modèle à s'arrêter au hasard ; écarter est la règle la plus simple, ne crée aucun texte nouveau (D1) et se défait en changeant d'option. Conséquence connue : **toutes les CR sortent du jeu** ; le modèle garde sur CR le comportement de la base (Baseline CR 50,1, M1 v2 24,5). À signaler à Anaël.
3. **Fidélité LC signalée, pas corrigée.** Pour chaque exemple LC retenu, comparer la cible au texte source (le texte administratif à réécrire, dans le message `user`) sur des éléments vérifiables sans jugement : nombres (montants, pourcentages, durées, dates), références juridiques (`article`, `L.`/`R.`/`D.` suivi d'un numéro), sigles en majuscules de 2 lettres ou plus. Un élément du source absent de la cible (après normalisation des espaces insécables et des séparateurs de milliers) est un écart. Le rapport liste, par exemple LC : rang, identifiant, éléments manquants. Ces exemples **restent** dans le jeu (pas d'écart de jeu) ; le MANIFEST porte le compte `lc_signales`.

## Boundaries & Constraints

**Always:**
- D1 : aucun texte n'est rédigé ni réécrit. Les seules transformations sont la suppression de la ligne de préambule et l'écart d'exemples. Fixtures de test : jetons factices, pas de texte administratif inventé.
- Provenance : la transformation est une fonction pure versionnée (`nettoyer_cible(texte) -> texte`, constante `VERSION_NETTOYAGE = 1`), inscrite au MANIFEST (`nettoyage = {version, depuis_build, plafond_tokens, tokenizer_sha256}`). Tout contrôle qui compare une cible au journal Mistral (`recontroler_appel_ids`, vérifications de `train.chargement`, reconstruction de 9.6, construction des paires 9.7 sur v4) doit accepter `nettoyer_cible(texte_journal) == cible` quand le MANIFEST porte `nettoyage`, et rester strict sinon. Le dev cherche et liste ces contrôles dans la revue.
- Aucune version existante n'est réécrite ; numérotation `vN` par `_creer_version` comme les builds existants. Aucun appel réseau, aucun appel payant.
- Rapport du run et sortie console : comptes **avant / après par tâche** (exemples, préambules retirés, `preambule_seul`, écartés `longueur`, LC signalés), écrits aussi dans `rapport.json`.
- Les autres messages (system, user, appels d'outils, réponses intermédiaires) sont recopiés à l'octet près.
- `data build --preferences --depuis <run du build v4>` doit fonctionner sur le jeu nettoyé (test).
- Tests ciblés, `uv run --no-sync`, contrôle rapide vert.

**Ask First:** changer `max_tokens` de l'évaluation ; retirer d'autres formules que « Voici » ; écarter les LC signalés.

**Never:** tronquer une cible ; réécrire une phrase ; appeler Mistral ou Claude ; modifier `data/train/v2` ou `v3`.

## Acceptance Criteria

- Given le build v2, when `data build --nettoyage --depuis 20261018-115927-build-424c --modele base:minicpm5-2b`, then une version v4 est créée ; attendu sur v2 : 0 cible commençant par « Voici » sur plusieurs lignes, 0 CR, 89 RD, comptes avant/après par tâche dans le rapport.
- Given une cible « **Voici X**\n\nCorps », then la cible devient « Corps ». Given « Voici X : » seule, then inchangée et comptée `preambule_seul`. Given « Le texte. Voici la suite », then inchangée.
- Given une cible de `max_tokens + 1` tokens, then écartée `longueur` ; de `max_tokens` tokens, then gardée.
- Given un LC dont la source contient « 1 500 € » et « article L. 123-4 » absents de la cible, then l'exemple reste et figure au rapport avec ces deux éléments.
- Given le MANIFEST v4, then les contrôles de provenance passent sur v4 et un texte modifié hors de `nettoyer_cible` est refusé.

</intent-contract>
