---
title: 'Story 5.2 — Fonctions de texte partagées (normalisation, mots, nombres, Kandel-Moles)'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '18faff3ff57c4ef0cedafe7da348fe3f157c83d1'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-5-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** le banc (scores LC, RE, CO, RD), l'anti-fuite (n-grammes normalisés) et la construction du jeu (`kandel_moles_entree`, Epic 7) ont besoin des mêmes fonctions de texte. Calculées à deux endroits, elles divergeraient (AD-29).

**Approach:** un module pur `slmsp.core.texte`, sans dépendance hors bibliothèque standard, versionné par `VERSION_TEXTE`, avec des règles simples et documentées dans les docstrings. Une empreinte des sorties sur un corpus de référence, liée à la version, verrouille toute modification de règle.

## Boundaries & Constraints

**Always:**
- Le module n'importe que la bibliothèque standard (`re`, `unicodedata`, `decimal`…), jamais `slmsp` ni un paquet tiers : l'outil de l'Epic 7 l'importe en `--no-project`.
- Fonctions pures et déterministes. Signatures : `normaliser(texte: str) -> str` ; `compter_mots(texte: str) -> int` ; `decouper_phrases(texte: str) -> list[str]` ; `extraire_nombres(texte: str) -> list[Decimal]` ; `syllabes(mot: str) -> int` ; `kandel_moles(texte: str) -> float` ; `ngrammes(texte: str, n: int) -> list[tuple[str, ...]]` ; `VERSION_TEXTE: int = 1`.
- Kandel-Moles = 207 − 1,015 × (mots ÷ phrases) − 73,6 × (syllabes ÷ mots), sur les totaux du texte, valeur brute non arrondie.
- Règles (version 1), à recopier dans les docstrings :
  - **normaliser** : NFKC, minuscules, NFKC à nouveau ; tout caractère de catégorie Unicode `P*` devient une espace ; espaces fusionnées et bords supprimés. Idempotente.
  - **mot** : jeton séparé par des blancs (`str.split()`, donc espace insécable comprise) qui contient au moins un caractère alphanumérique. « l'usager » et « porte-monnaie » comptent pour un mot ; « € » ou « – » seuls ne comptent pas.
  - **phrase** : coupure après `.`, `!`, `?` ou `…` (répétés ou non) suivis d'un blanc ou de la fin du texte, et à chaque saut de ligne. Une phrase sans mot est ignorée. Les abréviations (« M. ») coupent : limite assumée.
  - **syllabes(mot)** : le jeton est découpé en segments de lettres (tout non-lettre sépare). Dans chaque segment en minuscules, on compte les groupes maximaux de voyelles `aeiouyàâäéèêëîïôöùûüÿæœ`. Règle du e muet final : si le segment se termine par `e` ou `es` (e sans accent) précédé d'une consonne et compte plus d'un groupe, on retire 1. Total du jeton = somme des segments, minimum 1 (un nombre comme « 2026 » vaut 1).
  - **nombres** : chiffres ASCII ; virgule décimale ; séparateur de milliers = espace, U+00A0, U+202F ou U+2009 entre groupes de 3 chiffres ; point = séparateur de milliers seulement devant une virgule décimale (« 1.234,56 »), sinon point décimal (« 3.5 ») ; signe `-` ou `−` (U+2212) seulement s'il n'est pas collé à un caractère de mot avant (« 2020-2021 » donne 2020 et 2021) ; un nombre collé à une lettre ou à un chiffre avant (« R2 », « m² » non concerné) est ignoré. Ordre du texte conservé.
  - **ngrammes** : n-grammes de mots consécutifs de `normaliser(texte).split()`, doublons conservés, liste vide si moins de `n` mots.

**Never:**
- Aucune dépendance ajoutée à `pyproject.toml`, aucune lecture de fichier, aucune config TOML.
- Aucun fichier hors de `src/slmsp/core/texte.py` et `tests/core/test_texte.py` (pas de `tests/core/__init__.py` : pytest est en `--import-mode=importlib`, et la story 1.2 crée `tests/core/` en parallèle).
- Pas de calcul de score (c'est `evaluation.scores`, story 5.6), pas de hachage d'empreintes anti-fuite (story 5.1).
- Fixtures : phrases courtes et artificielles écrites pour le test, jamais des Données d'entraînement réalistes.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Normalisation | `"  L’Usager,  DOIT payer ! "` | `"l usager doit payer"` ; `normaliser(normaliser(x)) == normaliser(x)` | — |
| Nombres français | `"1 234,56 €"`, `"12,50 €"`, `"25 €"`, `"3,5 %"`, `"1 234,56"`, `"1 000"` | `Decimal("1234.56")`, `12.50`, `25`, `3.5`, `1234.56`, `1000` | — |
| Nombres ambigus | `"2020-2021"`, `"-3,5 %"`, `"R2D2"`, `"1.234,56"`, `"3.5"`, `"25."` | `[2020, 2021]`, `[-3.5]`, `[]`, `[1234.56]`, `[3.5]`, `[25]` | — |
| Syllabes | `porte`, `portes`, `le`, `arrivée`, `administrative`, `porte-monnaie`, `l'usager`, `2026` | 1, 1, 1, 3, 5, 3, 3, 1 | — |
| Kandel-Moles | `"Le chat dort. Il fait beau."` | 6 mots, 2 phrases, 6 syllabes → 207 − 3,045 − 73,6 = 130,355 (± 0,1) | — |
| Texte vide | `""` ou `"  ,; "` | `compter_mots` = 0, `decouper_phrases` = [], `ngrammes` = [] | `kandel_moles` lève `ValueError` (aucun mot) |
| n invalide | `ngrammes(t, 0)` | — | `ValueError` |

</intent-contract>

## Code Map

- `src/slmsp/core/__init__.py` -- vide (story 1.1) ; ne pas modifier. `core` est la couche 0 (AD-1, `tests/test_architecture.py` `COUCHES`).
- `src/slmsp/core/texte.py` -- à créer ; seul fichier de code de la story (zone 5.2, table « Dépendances et zones de fichiers » d'`epics.md`).
- `tests/core/test_texte.py` -- à créer ; `tests/conftest.py` fournit déjà une garde réseau et `SLMSP_VAR_DIR` temporaire (autouse).
- `pyproject.toml` -- lecture seule : ruff (`E,W,F,I,B,UP,TID251`, ligne 100, py312), pytest `--import-mode=importlib --strict-markers`.
- Consommateurs futurs (lecture seule, pour cadrer l'API) : `evaluation/scores.py` (5.6 : gain LC, longueur RE, CO), `core/items.py` (5.1 : anti-fuite par n-grammes), `data/validate.py` (9.x : `extraire_nombres`), `eval/outils/construire_jeu.py` (7.x, en `--no-project`).

## Tasks & Acceptance

**Execution:**
- `src/slmsp/core/texte.py` -- créer le module selon les règles v1 ci-dessus, avec docstring de module (rôle, AD-29, règle de version) et docstring par fonction qui énonce la règle -- source unique des calculs de texte.
- `tests/core/test_texte.py` -- tests paramétrés : chaque ligne de la matrice I/O ; idempotence de `normaliser` sur une dizaine de chaînes (ponctuation, ligatures, majuscules accentuées, NBSP) ; 3 textes de référence de Kandel-Moles avec mots, phrases et syllabes détaillés en commentaire et indice calculé à la main (± 0,1) ; un couple texte administratif / texte simplifié (artificiels) où le simplifié obtient l'indice le plus haut ; un test AST qui vérifie que `texte.py` n'importe que des modules de `sys.stdlib_module_names` ; le test de non-régression de version (voir Design Notes) -- couvre les critères 1 à 4 de la story.

**Acceptance Criteria:**
- Given le module, when on l'importe seul par chemin de fichier (`importlib.util.spec_from_file_location`), then il se charge sans le paquet `slmsp` et expose les huit noms publics.
- Given une règle de texte modifiée sans changer `VERSION_TEXTE`, when on lance `uv run pytest tests/core/test_texte.py`, then le test de non-régression échoue avec un message qui demande d'incrémenter la version et d'ajouter l'empreinte.
- Given toute la suite, when on lance `uv run pytest` et `uv run ruff check`, then tout passe.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts: 28 findings — high 0, medium 5, low 19, false 4, maybe-false 0
- findings:
  - `[medium]` `[patch]` (intent-alignment a) Le verrou ne voit que les sorties du corpus de référence : une règle absente du corpus peut changer sans incrément. — Corpus complété (groupe P1, voir verification-gap 1).
  - `[false]` `[reject]` (intent-alignment b) Les références de Kandel-Moles sont calculées avec la syllabation du module, pas contre un étalon externe. — La story demande un indice « calculé à la main dans le test », et AD-29 exige une syllabation unique, pas exacte : c'est le comportement voulu.
  - `[low]` `[reject]` (intent-alignment c1) Chaque saut de ligne compte comme fin de phrase, ce qui fausse l'indice des textes coupés à la main. — Règle documentée. Les entrées LC sont des chaînes JSON, où un saut de ligne marque un paragraphe ou une puce. Le cas est rare et le corriger ajouterait des branches.
  - `[low]` `[reject]` (intent-alignment c2) Les nombres au format anglais groupé (« 1,234.56 ») ne sont pas lus correctement. — Hors du périmètre (la story parle de nombres « à la française »). Les valeurs de data.gouv sont surtout non groupées (« 1234.56 »), ce qui fonctionne. Les gérer ajouterait une heuristique.
  - `[low]` `[patch]` (intent-alignment c3) Deux unités de mot coexistent (`compter_mots` contre `ngrammes`), sans que ce soit documenté. — La docstring du module explique désormais les deux unités (groupe P5).
  - `[low]` `[reject]` (intent-alignment c4) `normaliser` garde les symboles (€, +). — La règle de la spec ne retire que la ponctuation `P*`. Un symbole dans un n-gramme ne nuit pas à l'anti-fuite.
  - `[false]` `[reject]` (intent-alignment d) Le calcul entre versions (`kandel_moles_entree` contre le recalcul) n'est pas testé. — Cette surface appartient aux stories 5.6 et 7.4. La 5.2 expose bien `VERSION_TEXTE` en `int`.
  - `[low]` `[reject]` (intent-alignment e) Le test d'isolement s'exécute avec le Python du projet, pas en `--no-project`. — Le sous-processus `-I` vérifie qu'aucun module `slmsp` n'est chargé, et le test AST vérifie que seule la bibliothèque standard est importée. Cela suffit à garantir l'isolement.
  - `[false]` `[reject]` (intent-alignment f) Le résultat de l'Auto Run et le commit manquent. — Ils sont produits à l'étape de finalisation de ce même run.
  - `[medium]` `[patch]` (verification-gap 1) Le corpus ne contient ni U+202F ni U+2009, donc les retirer ne fait pas échouer le verrou. — Chaînes ajoutées au corpus et empreinte recalculée (P1).
  - `[medium]` `[patch]` (verification-gap 2) Les voyelles accentuées â, ê, î, ô, û, ë, ï, ü, æ… ne sont fixées par aucun test. — Cas ajoutés à `test_syllabes` (hôpital, forêt, sûr, aiguë, cœur, île) et au corpus (P1).
  - `[low]` `[patch]` (edge-case 1) Un nombre collé à une lettre laisse extraire sa partie décimale (« v2.5 » → 5, « A1,5 » → 5). — Lookbehind `(?<![0-9][.,])` ajouté et tests ajoutés (P2). Le cas « R2 000 » → 0 reste, faute de correctif simple qui n'oblige pas à réécrire le cas « 12 3456 ».
  - `[low]` `[patch]` (edge-case 2) « 1.234.567 » donne [1.234, 567]. — Corrigé en partie par P2 : le nombre fantôme disparaît. La valeur 1.234 est une limite de la règle v1 « point = décimale sans virgule », documentée dans la docstring.
  - `[low]` `[reject]` (edge-case 3) Un guillemet fermant après le point final se retrouve rattaché à la phrase suivante. — Le nombre de phrases ne change pas : la coupure vient du `!` ou du `.`, guillemet ou non, et « » » n'est pas un mot. L'effet est cosmétique.
  - `[low]` `[patch]` (edge-case 4) La version de la base Unicode (`unidata_version`) n'est pas couverte par le verrou. — Elle entre désormais dans l'empreinte (P3). Python 3.12 est épinglé partout (D2).
  - `[medium]` `[patch]` (edge-case 5, claim) Les règles absentes du corpus échappent au verrou. — Même cause que verification-gap 1 (P1).
  - `[low]` `[patch]` (edge-case 6, claim) Un nombre collé avant ne disparaît pas entièrement : sa partie décimale est extraite. — Même cause qu'edge-case 1 (P2).
  - `[low]` `[patch]` (blind 1) Le verrou ignore la base Unicode. — Même cause qu'edge-case 4 (P3).
  - `[medium]` `[patch]` (blind 2) Le corpus ne déclenche pas toutes les règles (U+202F, U+2009, `-es` après une voyelle, n ≥ 4, « 1.234 », « − » en début de ligne). — P1 : corpus complété et n-grammes étendus de 1 à 4.
  - `[low]` `[patch]` (blind 3) Un échec du verrou ne dit pas comment recalculer l'empreinte. — Le message d'assertion décrit maintenant la procédure (P4).
  - `[low]` `[reject]` (blind 4) Les caractères de format Cf (U+00AD, U+200B, U+FEFF) survivent à `normaliser`. — Ce cas ne se présente pas dans les sorties Mistral ni dans les items. L'anti-fuite compare aussi les vecteurs BGE-M3. Retirer les Cf changerait la règle de la spec. Le risque est noté en risque résiduel.
  - `[low]` `[reject]` (blind 5) « « oui ! » puis » est découpé en deux phrases. — Même analyse qu'edge-case 3 : la coupure vient du `!`, et le guillemet n'ajoute aucune phrase.
  - `[low]` `[patch]` (blind 6) « 1.234.567 » et « 3.5.6 » sont mal lus. — Même cause qu'edge-case 2 (P2).
  - `[low]` `[reject]` (blind 7) Le tiret demi-cadratin n'est pas lu comme un signe moins. — La règle documentée ne retient que `-` et `−`. L'ajouter élargirait la règle sans besoin attesté.
  - `[low]` `[reject]` (blind 8) Il manque une API publique `mots` ou `compter_syllabes`. — Les consommateurs prévus (longueur RE, gain LC) utilisent `compter_mots` et `kandel_moles`, qui existent. Seul le test recode la règle.
  - `[low]` `[patch]` (blind 9) La notion de mot n'est pas la même dans `compter_mots` et dans `ngrammes`. — Même cause qu'intent-alignment c3 (P5).
  - `[low]` `[patch]` (blind 10) La docstring du module promet de détecter « la moindre sortie ». — Reformulée (P6).
  - `[false]` `[reject]` (blind 11) `ngrammes` ne valide pas le type de `n` (bool, float). — L'annotation est `n: int`, et `True` est un `int` en Python. Aucun appelant ne passe autre chose. Ce n'est pas un défaut.

## Design Notes

**Verrou de version.** Le test calcule une empreinte SHA-256 du JSON canonique (`sort_keys=True`, `ensure_ascii=False`, séparateurs compacts, `Decimal` et `float` en `str`/`repr`) des sorties de toutes les fonctions sur un corpus de référence fixe défini dans le test. Il la compare à `EMPREINTES = {1: "<sha>"}` indexé par `VERSION_TEXTE`.

```python
assert VERSION_TEXTE in EMPREINTES, "Nouvelle VERSION_TEXTE : ajouter son empreinte."
assert empreinte() == EMPREINTES[VERSION_TEXTE], (
    "Les sorties de core.texte ont changé : incrémenter VERSION_TEXTE et ajouter l'empreinte.")
```

L'empreinte de la version 1 est calculée une fois, après que tous les autres tests passent, puis inscrite en dur.

**Syllabation.** Elle est approximative (pas de règle « qu », ni « -ent » verbal, ni diérèse). Peu importe : AD-29 demande une seule syllabation partout, pas une syllabation parfaite. Le gain LC est une différence entre deux indices calculés de la même façon.

## Verification

**Commands:**
- `uv run pytest tests/core/test_texte.py -q` -- expected: tous les tests passent
- `uv run pytest -q` -- expected: aucun échec (hors échecs préexistants listés)
- `uv run ruff check` -- expected: aucune erreur
- `uv run ruff format --check src/slmsp/core/texte.py tests/core/test_texte.py` -- expected: déjà formaté

## Auto Run Result

Status: done
Blocking condition: aucune

**Changement livré.** `slmsp.core.texte` est un module pur, qui n'utilise que la bibliothèque standard et se charge par chemin de fichier sans le paquet `slmsp`. Il contient :
- `VERSION_TEXTE = 1` ;
- `normaliser`, `compter_mots`, `decouper_phrases`, `extraire_nombres` (en `Decimal`), `syllabes`, `kandel_moles` et `ngrammes`.

Les règles v1 sont recopiées dans les docstrings. Un verrou de version (SHA-256 des sorties sur un corpus de référence, version Unicode comprise) oblige à incrémenter la version à chaque changement de règle.

**Fichiers.**
- `src/slmsp/core/texte.py` : le module (nouveau).
- `tests/core/test_texte.py` : 86 tests (nouveau). Ils couvrent la matrice I/O, l'idempotence, trois références de Kandel-Moles calculées à la main, le couple texte simplifié / texte administratif, l'isolement (AST et sous-processus `-I`) et le verrou de version.
- `_bmad-output/implementation-artifacts/epic-5-context.md` : contexte compilé de l'epic 5.

**Revue (1 passe, 28 constats).** Les détails sont dans le Review Triage Log.
- 4 correctifs regroupant 18 constats :
  - P1 : corpus du verrou complété (U+202F, U+2009, voyelles accentuées, n-grammes de 1 à 4) ;
  - P2 : lookbehind `(?<![0-9][.,])` contre la queue de « v2.5 » et de « 1.234.567 » ;
  - P3 : `unidata_version` dans l'empreinte ;
  - P4, P5 et P6 : message d'échec du verrou, docstring des deux unités de mot, docstring de version reformulée.
- 0 constat différé.
- Rejetés :
  - 4 faux : référence externe de la syllabation, calcul entre versions, finalisation, type de `n` ;
  - 10 mineurs non retenus : sauts de ligne, nombres anglais, symboles conservés, isolement en `--no-project`, guillemet fermant (deux fois), caractères Cf, tiret demi-cadratin, API `mots`. Le motif de chacun est dans le log.

**Revue de suivi recommandée : oui.** Deux entrées `medium` ont été corrigées (P1 et P2 ; 0 `high`, 2 `medium`, 2 `low`). Risque non vérifié : la nouvelle empreinte `EMPREINTES[1]` a été recalculée à partir des sorties du code, sans contrôle à la main. Les effets de bord de P2 sont acceptés et non testés : « 1,2,3 » donne [1.2] et « 25.12.2026 » donne [25.12].

**Vérification.**
- `uv run pytest -q` : 215 passés.
- `uv run pytest tests/core/test_texte.py` : 86 passés.
- `uv run ruff check` : propre.
- `ruff format --check` sur les deux fichiers : propre.
- Audit de la matrice : chaque ligne est couverte par un test qui a tourné.

**Décisions prises seul.**
- Les mots sont des jetons séparés par des blancs, et les n-grammes des jetons normalisés.
- La syllabation est approximative (pas de règle « qu », pas de diérèse) ; elle est la même partout, comme le veut AD-29.
- `kandel_moles` lève `ValueError` sur un texte sans mot.
- Le point est décimal, sauf dans la forme « 1.234,56 ».
- `syllabes` applique NFC.
- Pas de `tests/core/__init__.py`, pour éviter un conflit avec la story 1.2.

**Risques résiduels.**
- Les caractères de format Unicode (U+00AD, U+200B) survivent à `normaliser`, ce qui ouvre un contournement possible des n-grammes anti-fuite. Les vecteurs le couvrent en partie.
- Les abréviations (« M. ») et les sauts de ligne gonflent le nombre de phrases.
- « 1.234 » se lit 1,234.
