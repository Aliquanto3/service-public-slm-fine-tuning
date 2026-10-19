---
title: "Story 9.9 — Nettoyage déterministe du jeu SFT (v4)"
type: 'feature'
created: '2026-10-19'
status: review
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

1. **Préambule retiré.** La cible est le dernier message (`assistant`), quel que soit le rôle de `messages[0]` ; si son `content` n'est pas une chaîne ou s'il porte `tool_calls`, rien ne change. Découpage sur `\n` seul ; une ligne est vide si `ligne.strip()` est vide (`\r` compris). Soit la première ligne non vide ; une fois retirés les marqueurs de tête (`#`, `*`, `_`, espaces), elle commence par `Voici` (casse exacte). Elle est **retirée**, avec les lignes vides qui la précèdent et la suivent, si les trois conditions tiennent : (a) il reste du texte non vide après elle ; (b) elle finit par `:` une fois retirés `*`, `_` et espaces de fin, **ou** elle est entièrement en gras (`**…**` ou `__…__`, titre LC) ; (c) elle ne contient ni `](` ni `http` (en RD, la ligne cite souvent le jeu de données avec son lien : c'est du contenu). Sinon elle reste, comptée `preambule_garde` (ou `preambule_seul` si rien ne la suit). Rien d'autre n'est modifié : pas de réécriture, pas de capitalisation. Formes observées dans v2 : « Voici la réponse fondée uniquement sur les passages fournis : » (Q, RD, LC, generique) et « **Voici votre … : ce que vous devez savoir** » (LC, 13 titres en gras qui ne finissent pas par `:`). Décision d'Anaël : retirer les préambules « en gras ou non ».
2. **Longueur bornée : écarter, pas tronquer.** Après l'étape 1, une cible dont le nombre de tokens (`tokenizers.Tokenizer.from_file("models/<slug>/hf/tokenizer.json").encode(texte, add_special_tokens=False)`, slug du `--modele`) dépasse `max_tokens` de l'évaluation (lu dans `config/evaluation.toml`, pas recopié) est **écartée** avec le motif `longueur` ; une cible d'exactement `max_tokens` tokens est gardée (la fin de séquence n'est pas comptée). Le run écrit `ecartes.jsonl {rang, session_id, tache, tokens}`. Le build **refuse** si une tâche autre que CR tombe à 0 exemple. Justification : tronquer produirait des cibles coupées en pleine phrase suivies d'une fin de séquence, ce qui apprend au modèle à s'arrêter au hasard ; écarter est la règle la plus simple, ne crée aucun texte nouveau (D1) et se défait en changeant d'option. Conséquence connue : **toutes les CR sortent du jeu** ; le modèle garde sur CR le comportement de la base (Baseline CR 50,1, M1 v2 24,5). À consigner dans le fichier d'état. Vérifier que le lecteur d'artefacts AD-24 (`core/artefacts.py`) autorise la lecture de `models/` pour cet usage.
3. **Fidélité LC signalée, pas corrigée.** Source d'un LC : `messages[1].content.removeprefix("Texte :\n")`. On compare la cible à la source sur des éléments vérifiables sans jugement : nombres (`\d[\d\s.,]*\d|\d`, en ignorant ceux d'un seul chiffre), références juridiques (`article` + numéro, `L.`/`R.`/`D.` + numéro), sigles en majuscules de 2 lettres ou plus. Normalisation des deux côtés avant comparaison : NFKC, suppression de tous les espaces (U+00A0 et U+202F compris), retrait de `,00`, apostrophe `’` → `'`. Un élément de la source absent de la cible est un écart. Le rapport liste, par exemple LC : rang, `session_id`, éléments manquants. Ces exemples **restent** dans le jeu ; le MANIFEST porte le compte `lc_signales`. Faux positifs attendus (nombre écrit en lettres, sigle développé) : c'est un signalement à relire par Anaël, pas un filtre.

## Boundaries & Constraints

**Always:**
- D1 : aucun texte n'est rédigé ni réécrit. Les seules transformations sont la suppression de la ligne de préambule et l'écart d'exemples. Fixtures de test : jetons factices, pas de texte administratif inventé.
- Provenance par chaîne (relecture Opus) : la transformation est une fonction pure versionnée (`nettoyer_cible(texte) -> texte`, constante `VERSION_NETTOYAGE = 1`). Le SHA de v2 est revérifié contre son MANIFEST (comme `preferences._jeu_sft`), puis `verifier_nettoyage(octets_v4, octets_v2)` contrôle que chaque ligne v4 est identique à sa ligne v2 (même rang d'origine), à l'octet près en JSON canonique, sauf le `content` du dernier message, qui doit valoir `nettoyer_cible(content_v2)`. Elle lève `ProvenanceInvalide` sinon et tourne avant l'écriture du MANIFEST. `charger_jeu` (`train/chargement.py`) refait cette vérification quand le MANIFEST porte `nettoyage`. Aucun autre contrôle n'est modifié (`recontroler_appel_ids` ne compare pas de texte ; `verifier_octets` du build v2 reste la preuve Mistral).
- MANIFEST : `nettoyage: Nettoyage | None = None` est ajouté à `ManifesteJeuEntrainement` (`core/schemas/entrainement.py`, `extra="forbid"`), avec `{version, depuis_build, depuis_version, sha256_train_source, plafond_tokens, tokenizer_sha256, lc_signales}`. Les autres champs sont recopiés de v2 (`filter_run_id`, `validate_run_id`, `generate_run_id`…), sauf `version`, `run_id`, `sha256_train`, `nb_lignes`, `comptes_par_tache` et `cree_le`. Le run est de type `data-build` (`TYPE_RUN_BUILD`), pour que `_jeu_sft` (`data/preferences.py`) l'accepte.
- CLI : `--nettoyage` exclut `--variante` et `--preferences` ; `--modele base:<slug>` y est obligatoire (`cli/data.py`, comme `_preferences`).
- Aucune version existante n'est réécrite ; numérotation `vN` par `_creer_version` comme les builds existants. Aucun appel réseau, aucun appel payant.
- Rapport du run et sortie console : comptes **avant / après par tâche** (exemples, préambules retirés, `preambule_seul`, écartés `longueur`, LC signalés), écrits aussi dans `rapport.json`.
- Les autres messages (system, user, appels d'outils, réponses intermédiaires) sont recopiés à l'octet près.
- `data build --preferences --depuis <run du build v4>` doit fonctionner sur le jeu nettoyé et produira v5 (test : `lancer_preferences` sur un v4 de fixture, puis `charger_jeu("v5", fichier="preferences.jsonl")`). Une campagne v2 ne se reprend pas sur v4 (l'invariant `jeu_build` les sépare ; test).
- Tests ciblés, `uv run --no-sync`, contrôle rapide vert.

**Ask First:** changer `max_tokens` de l'évaluation ; retirer d'autres formules que « Voici » ; retirer une ligne « Voici » qui contient un lien ; écarter les LC signalés.

**Never:** tronquer une cible ; réécrire une phrase ; appeler Mistral ou Claude ; modifier `data/train/v2` ou `v3`.

## Acceptance Criteria

- Given le build v2, when `data build --nettoyage --depuis 20261018-115927-build-424c --modele base:minicpm5-2b`, then une version v4 est créée ; attendu sur v2 : 0 CR, RD = 91 moins les cibles de plus de 1 024 tokens après retrait (mesuré, consigné), plus aucune ligne « Voici » retirable ; comptes avant/après par tâche (dont `preambule_garde`) dans le rapport et à la console.
- Given « **Voici X**\n\nCorps », then « Corps ». Given « Voici X :\n\nCorps », then « Corps ». Given « **Voici X :**\r\n\r\nCorps », then « Corps ». Given « \n\nVoici X :\nCorps », then « Corps ». Given « Voici X : » seule, then inchangée, `preambule_seul`. Given « Voici le jeu [Y](https://…) :\n\nCorps », then inchangée, `preambule_garde`. Given « Voici ce que dit le texte, en bref.\nCorps » (ni `:` final ni gras), then inchangée, `preambule_garde`. Given « Le texte. Voici la suite », then inchangée.
- Given une cible de `max_tokens + 1` tokens, then écartée `longueur` ; de `max_tokens` tokens, then gardée.
- Given un LC dont la source contient « 1 500 € » et « article L. 123-4 » absents de la cible, then l'exemple reste et figure au rapport avec ces deux éléments.
- Given le MANIFEST v4, then `verifier_nettoyage` et `charger_jeu` passent sur v4 ; une ligne v4 dont un octet diffère hors de `nettoyer_cible` (cible ou autre message) est refusée par `ProvenanceInvalide`.

## Relecture de la spec
2026-10-19, Opus, avant le code : provenance par chaîne SHA + `verifier_nettoyage` (au lieu d'assouplir des contrôles qui ne comparent pas de texte), schéma du MANIFEST, garde des lignes « Voici » à lien (RD), cas limites, normalisation LC. Intégrés ci-dessus.

</intent-contract>

## Implémentation

2026-10-19, Opus (dev-story). Fichiers : `core/nettoyage.py` (`nettoyer_cible`, `analyser_preambule`, `verifier_nettoyage`, `VERSION_NETTOYAGE = 1` ; dans `core` pour être partagé par `data` et `train`, couches AD-1), `data/nettoyage.py` (`lancer_nettoyage`, `tokeniseur_du_modele`, `elements_manquants`), `core/schemas/entrainement.py` (`Nettoyage`, champ `nettoyage` omis du JSON quand il vaut `None` : les MANIFEST des builds existants ne changent pas), `train/chargement.py` (`controler_nettoyage` dans `charger_jeu`), `cli/data.py` (`--nettoyage`), `tests/data/test_nettoyage.py` (29 tests).

Essai réel (copie de v2 et du run 424c dans le scratchpad, tokenizer minicpm5-2b, plafond 1 024) : 503 → 425 lignes, v4 relu par `charger_jeu`, plus aucune ligne « Voici » retirable.

| Tâche | avant | après | préambules retirés | gardés | seuls | écartés longueur | LC signalés |
|---|---|---|---|---|---|---|---|
| CO | 34 | 34 | 0 | 0 | 0 | 0 | 0 |
| CR | 76 | 0 | 0 | 0 | 0 | 76 | 0 |
| CT | 34 | 34 | 0 | 0 | 0 | 0 | 0 |
| LC | 69 | 69 | 65 | 0 | 0 | 0 | 2 (sigles CB, CPH) |
| Q | 92 | 92 | 59 | 0 | 0 | 0 | 0 |
| RD | 91 | 89 | 57 | 2 (lien) | 0 | 2 (1 248 et 1 277 tokens) | 0 |
| RE | 34 | 34 | 0 | 0 | 0 | 0 | 0 |
| generique | 73 | 73 | 4 | 0 | 0 | 0 | 0 |

## Auto Run Result

- ~~`verifier_nettoyage` vérifie une sous-suite ordonnée~~ (remplacé en revue : rangs écartés déclarés au MANIFEST, appariement rang par rang).
- Plafond lu par la CLI (`evaluation.config.charger_evaluation`, couche `cli`) et passé à `lancer_nettoyage` : `data` ne peut pas importer `evaluation` (même couche).
- Un jeu déjà nettoyé est refusé comme source (`ManifesteInvalide`) : la chaîne vérifiée au chargement n'a qu'un niveau.
- Fidélité LC (remplacé en revue : comparaison d'éléments extraits des deux côtés) : un élément est cherché dans la cible normalisée entière (sous-chaîne), les références « article N » sans tenir compte de la casse ; les nombres sont cherchés hors des références. Seulement 2 LC signalés sur 69, tous deux pour un sigle : à relire par Anaël.
- Statut de run : `complet` ; type `data-build`, slug `nettoyage`. Le fichier d'état n'est pas modifié (hors zone) : la sortie des CR du jeu est à y consigner par l'orchestrateur.

## Revue

2026-10-19, Opus (reviewer), une passe, rebasée sur main 9e330f4 (story 10.9). Constats du second avis (Haiku) repris un par un.

- medium · second avis · corrigé : `verifier_nettoyage` acceptait une sous-suite, donc une ligne retirée en silence. Le MANIFEST porte désormais `nettoyage.ecartes: [{rang, motif: "longueur", tokens}]` (schéma `Ecart` : rangs strictement croissants, `tokens > plafond_tokens`) ; `verifier_nettoyage(nettoyé, source, rangs_ecartes)` apparie rang par rang (compte exact, rangs uniques et dans la source) ; `charger_jeu` passe les rangs du MANIFEST. Le recomptage des tokens reste au build (pas au chargement).
- medium · second avis · corrigé : fidélité LC par sous-chaîne (« 1 500 » trouvé dans « 11 500 », « article 1 » dans « article 12 », « CB » dans « CBX »). Éléments extraits des deux côtés puis comparés en ensemble ; nombres à milliers groupés par espace ou point, jamais deux nombres reliés (« 2023. 15 ») ; « Articles » → « article », point de milliers retiré à la normalisation.
- medium · second avis · corrigé : `tokenizers` vient de l'extra `train` (via transformers), absent de `data`. Pas de CI dans le dépôt (Windows seul) ; `ConfigurationInvalide` « installer l'extra train » si le paquet manque, test `importorskip` pour le test qui l'utilise, test de l'erreur.
- low · second avis · corrigé : BOM U+FEFF en tête de cible ignoré comme marqueur de tête (aucun dans v2, vérifié).
- low · second avis · corrigé : regex de nombres qui reliait « 2023. 15 » (voir medium LC).
- low · second avis · corrigé : ordre d'écriture, `rapport.json` avant `MANIFEST.json` (le MANIFEST signale une version complète).
- low · second avis · corrigé : tests ajoutés (CLI nominale avec plafond lu dans `config/evaluation.toml`, ligne retirée en silence, écart déclaré sous le plafond, rangs invalides, faux négatifs de sous-chaîne, version de nettoyage 2 refusée, tokenizers absent).
- low · second avis · rejeté : paires v5 non rattachées à la v4 au chargement. Les préférences ont leur propre chaîne (`jeu_sft_version`, SHA du jeu SFT, story 9.7) ; hors périmètre de 9.9.
- low · second avis · rejeté : tokenizer lu sous `racine_projet()/models` et non `--racine`. Même règle que les autres lecteurs de poids (`dossier_modeles`, `SLMSP_MODELS_DIR`) ; `--racine` désigne data/eval/runs.
- Complexité : 0 constat. `verifier_nettoyage` est linéaire (ensemble des rangs, un zip) ; `ecartes` au MANIFEST croît avec le jeu (78 entrées sur v2), sans parcours répété.

Essai réel refait (copie de v2 et du run 424c dans le scratchpad, tokenizer minicpm5-2b, plafond 1 024) : comptes par tâche identiques au tableau ci-dessus, 503 → 425 lignes, 78 écarts déclarés au MANIFEST, `lc_signales` = 2 (CB, CPH), v4 relu par `charger_jeu`. Tests : `tests/data tests/core tests/train tests/cli` 1521 passés ; ruff, format, contrôle rapide verts.
