---
title: 'Story 4.4 — Comptes rendus longs : découpage et fusion'
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '747375f7b9e838634e8aa0499292278c8ae5d7e8'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** Un Compte rendu passe aujourd'hui par le repli `redaction` : une transcription plus longue que le contexte du modèle part en un seul appel, qui échoue côté `llama-server` (FR-13 non tenu). En plus, le report de la 4.2 bloque : les items CT gelés portent une clé d'entrée `type` que `construire_messages` refuse (`test_items_reels_passent_construire_messages[CT.jsonl]` échoue).

**Approach:** Le module `harness/taches/compte_rendu.py` compte les tokens de l'entrée par `LlmPort.compter_tokens`. Si elle tient dans `taille_contexte − reserve_sortie_tokens`, il délègue tel quel à `redaction.traiter`. Sinon, il découpe sur des limites de paragraphe (`harness/decoupage.py`, fonction pure) avec le chevauchement configuré, synthétise chaque morceau avec la variante `morceau` (évènements `Progression("Partie i sur n")`), puis fusionne avec la variante `fusion`. Pour CT, la clé `type` devient un synonyme déclaré de `type_courrier`.

## Boundaries & Constraints

**Always:**
- AD-7 : tous les messages (morceau, fusion, appel unique) sont construits par `construire_messages` (variantes `morceau` et `fusion` de la table). Le compte de tokens se fait sur les messages réellement envoyés.
- `reserve_sortie_tokens` et `chevauchement_paragraphes` sont lus dans `ctx.config.compte_rendu`, sans modifier `harness/config.py` ni `config/harnais.toml`.
- La taille du contexte vient de l'attribut optionnel `taille_contexte` (int) du `LlmPort`. `ClientLlama` le reçoit de `ServeurLlama.client()` (`config.contexte`). Sans cet attribut, on fait un seul appel (comportement 4.2 inchangé).
- Aucune troncature silencieuse : tout le texte est couvert par les morceaux. Un paragraphe trop long est redécoupé (lignes, puis phrases, puis mots) ; seul un mot isolé plus grand que le budget est gardé tel quel (dépassement visible côté serveur, jamais tronqué).
- Seuls les `Jeton` de l'appel final (fusion ou appel unique) sont émis ; les synthèses de morceau sont consommées sans être diffusées. `AppelNonConforme` reste relayé.
- Règle D1.1 : aucun texte rédigé dans les tests ; mots aléatoires générés (`harness_factices.mots`).
- Clé `type` (CT) : admise seulement si le prompt la déclare ; rendue exactement comme `type_courrier` (même libellé, même place) ; `type` et `type_courrier` ensemble lèvent `EntreeInvalide`.

**Never:**
- Modifier `eval/` (jeu gelé), `harness/service.py`, `harness/config.py`, `config/harnais.toml`, `core/ports.py` (le `Protocol` ne gagne pas de membre), `sprint-status.yaml`, les documents de décision.
- Toucher `mcp/bac_a_sable`, `judge/` (stories parallèles).
- Composer un prompt hors `construire_messages`, ou modifier la « Consigne » d'un prompt.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| CR court | entrée qui tient (`compter_tokens ≤ contexte − réserve`) | un seul appel, prompt CR, flux identique à la 4.2 | — |
| CR sans `taille_contexte` | `FakeLlm` de base | un seul appel (repli 4.2) | — |
| CR long | 9 000 mots, contexte 3 000, réserve 500 | n morceaux sur limites de paragraphe, n appels `CR-morceau` (partie « i sur n »), `Progression` i/n, puis 1 appel `CR-fusion` dont la sortie est diffusée ; `Fin` final avec usage cumulé | — |
| Chevauchement | `chevauchement_paragraphes = 1` | le dernier paragraphe du morceau i ouvre le morceau i+1 | réduit si nécessaire pour avancer |
| Paragraphe énorme | un seul bloc sans saut de ligne > budget | redécoupé en phrases ou mots ; tous les mots couverts | — |
| Synthèses trop longues pour une fusion | somme des synthèses > budget | fusions intermédiaires par groupes, puis fusion finale | si aucun regroupement possible, fusion finale tentée (erreur serveur visible) |
| Synthèse vide | le modèle rend une chaîne blanche pour un morceau | morceau ignoré dans la fusion | toutes vides → `Erreur` |
| Erreur du modèle sur un morceau | exception dans le flux | `Erreur` sans détail (service) | — |
| CT gelé | entrée `{type, objet, elements_connus, consigne}` | message `user` avec « Type de courrier : » | `type` + `type_courrier` → `EntreeInvalide` |

</intent-contract>

## Code Map

- `src/slmsp/harness/taches/__init__.py:275-291` -- `MODULES_TRAITEMENT["CR"] = "compte_rendu"` ; repli `compte_rendu → redaction` actif tant que le module manque (il existera désormais). `ContexteTache` (l.343 : `tache`, `entree`, `historique`, `textes_saisis`, `llm`, `config`, `options_llm`, `messages_pour`) ; `diffuser(ctx, messages, tools)` (l.387) renvoie `(texte, fin)` et relaie les `Jeton`. `EMPLACEMENTS` (l.50) : vocabulaire fermé, y ajouter `type`.
- `src/slmsp/harness/taches/redaction.py` -- `traiter(ctx)` : chemin court à réutiliser tel quel.
- `src/slmsp/harness/prompts.py` -- `construire_messages(tache, entree, *, variante=…)` ; `ORDRE_CLES` (l.52), `LIBELLES_CLES` (l.69), `_rendre_objet` (l.180, lève `EntreeInvalide` sur clé inconnue à la l.185), `CLES_OPTIONS`/`entree_de_requete` (l.272 : ne pas ajouter `type_courrier` si `type` est présent). Docstring de module = règle unique de rendu, à compléter.
- `config/prompts/taches/CR-morceau.md` (emplacements `consigne`, `partie`, `notes`, `transcription`), `CR-fusion.md` (`consigne`, `parties`) ; `config/taches.toml` (`[taches.CR] variantes = { morceau, fusion }`). Lecture seule.
- `config/prompts/taches/CT.md` -- ajouter la ligne d'emplacement `type` (section Emplacements seulement) ; `config/taches.toml` -- commentaire sous `[taches.CT]`.
- `src/slmsp/harness/config.py:40` -- `ConfigCompteRendu(reserve_sortie_tokens=1024, chevauchement_paragraphes=1)`. Lecture seule.
- `src/slmsp/core/evenements.py:83` -- `Progression(etape, fait, total)` ; `Fin(raison, usage, urls_inventees)` (l.100).
- `src/slmsp/inference/client.py:150` (`ClientLlama.__init__`) et `src/slmsp/inference/serveur.py:575` (`client()`) -- ajout minimal hors zone : attribut `taille_contexte`.
- `src/slmsp/harness/citations.py` -- `urls_inventees(texte, resultats_outils=…, textes_fournis=…)`.
- `tests/harness/factices.py` -- `FakeLlm` (`compter_tokens` = nombre de mots des contenus), `mots`, `script`. Ne pas modifier : sous-classer dans les tests.
- `tests/harness/test_integration_question.py` -- modèle du test réel (`config_generation`, `prerequis`, `ServeurLlama`). Item long : `eval/jeu/v1.0/items.jsonl`, CR-006 (5 480 mots, 195 paragraphes).

## Tasks & Acceptance

**Execution:**
- `src/slmsp/harness/decoupage.py` -- `paragraphes(texte)` (blocs séparés par une ligne vide, blancs retirés) ; `regrouper(unites, mesurer, budget, *, joint)` (empaquetage glouton) ; `decouper(texte, mesurer, budget, chevauchement)` → `list[str]`, pure, redécoupe hiérarchique d'un paragraphe trop grand (lignes, phrases, mots), chevauchement réduit si l'avance l'exige ; `ValueError` si `budget ≤ 0`.
- `src/slmsp/harness/taches/compte_rendu.py` -- `traiter(ctx)` : mesure, chemin court (`redaction.traiter`) ou long (morceaux silencieux, `Progression`, fusions intermédiaires éventuelles, fusion finale diffusée, `Fin` avec usage cumulé et `urls_inventees`). Chaque clé de contenu (`notes`, `transcription`) est découpée séparément, dans l'ordre de `ORDRE_CLES`.
- `src/slmsp/inference/client.py`, `src/slmsp/inference/serveur.py` -- `taille_contexte: int | None` (kwarg et attribut) ; `client()` passe `self.config.contexte`.
- `src/slmsp/harness/prompts.py`, `src/slmsp/harness/taches/__init__.py`, `config/prompts/taches/CT.md`, `config/taches.toml` -- synonyme `type` → `type_courrier` (vocabulaire, déclaration, rendu, conflit, `entree_de_requete`), documenté dans la docstring du module.
- `tests/harness/test_decoupage.py`, `tests/harness/test_compte_rendu.py` -- toute la matrice I/O et les AC ; `tests/harness/test_prompts.py` -- cas `type` (rendu identique, conflit) ; `tests/inference` -- `taille_contexte` transmis.
- `tests/harness/test_integration_compte_rendu.py` -- `lent` + `integration` : Granite 1B CPU, contexte 4096, CR-006 du jeu gelé ; vérifie plusieurs `Progression`, au moins 2 appels morceau et une fusion (espion sur le client réel), `Fin` final, texte non vide.

**Acceptance Criteria:**
- Given une entrée qui tient dans le contexte, when le service la traite, then un seul appel est fait avec le prompt CR (`messages[0]` = consigne CR).
- Given 9 000 mots qui dépassent le contexte, when le service les traite, then chaque morceau ≤ budget (mesuré par `compter_tokens`), coupé entre paragraphes, avec le chevauchement configuré ; chaque morceau passe par `CR-morceau`, des `Progression("Partie i sur n")` sont émis, puis la fusion passe par `CR-fusion`.
- Given une entrée d'au moins 6 000 mots, when elle est soumise, then la concaténation des morceaux (chevauchement retiré) redonne tous les mots dans l'ordre : aucune troncature.
- Given le découpage, when on le relance sur la même entrée, then les morceaux sont identiques.
- Given `uv run pytest tests/harness/test_prompts.py`, when il tourne, then `test_items_reels_passent_construire_messages[CT.jsonl]` passe.

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Passe de revue
- verdicts : 37 constats — high 0, medium 5, low 27, false 5, maybe-false 0.
- constats :
  - **Blind Hunter**
    - `[medium]` `[patch]` Le budget ignore le `max_tokens` de l'appelant : la sortie d'un morceau peut dépasser la réserve. Correctif : sur le chemin long, `max_tokens = min(appelant, reserve_sortie_tokens)` (`_plafonne`). Tests `test_max_tokens_plafonne_a_la_reserve` et `test_max_tokens_inchange_sur_le_chemin_court`.
    - `[medium]` `[patch]` Une synthèse de morceau tronquée (`longueur`) était fusionnée sans signal, et le `Fin` final disait `terminee`. Correctif : le `Fin` final porte la raison la plus grave de tous les appels (`_raison`). Test `test_raison_la_plus_grave_de_tous_les_appels`.
    - `[low]` `[patch]` `_cumuler` additionnait `delai_premier_token_ms`. Correctif : la clé n'est plus cumulée (`CLES_USAGE_NON_CUMULEES`). Test `test_delai_premier_token_non_cumule`.
    - `[low]` `[reject]` Coût quadratique des mesures. Mesuré sur CR-006 : 397 appels `compter_tokens` en 114 s au total. Un cache ou une estimation additive ajouterait de la complexité pour un gain qui n'est pas nécessaire aujourd'hui.
    - `[low]` `[reject]` Un historique long déclenche le chemin long alors que le contenu tiendrait. Cas multi-tour rare, déjà renvoyé à J4 par la 4.2. La garde proposée enverrait de toute façon un appel trop long.
    - `[low]` `[reject]` Les compteurs de progression repartent à zéro entre les étapes. Chaque étape a son libellé (`etape`) : c'est un affichage, sans perte d'information.
    - `[low]` `[reject]` `taille_contexte` est lu par duck typing. Choix assumé de la spec : ajouter un membre au `Protocol` casserait l'`isinstance` des doublures existantes.
    - `[low]` `[reject]` Repli silencieux si la configuration rend le budget ≤ 0. Le serveur renvoie quand même une erreur visible. Un journal ajouterait une branche pour un cas de configuration rare.
    - `[low]` `[reject]` La garde du mot seul ne teste que le premier mot. C'est une garde de surcoût fixe : un mot trop long plus loin dans le texte est l'exception documentée.
    - `[low]` `[reject]` Le synonyme `type` est global. Il ne s'applique que si le prompt déclare `type`, ce que seul CT fait.
    - `[low]` `[reject]` `CT.md` reste en `version: 1`. La Consigne n'a pas changé, et le SHA-256 du fichier trace la modification des Emplacements.
    - `[false]` `[reject]` Le correctif CT serait sans rapport avec la story. Il est exigé explicitement par l'intention de l'invocation.
    - `[low]` `[reject]` Un paragraphe redécoupé est rejoint par des sauts de ligne. C'est un changement de forme sans perte de mot, et seulement au-delà du budget.
    - `[low]` `[reject]` Le découpage en phrases coupe après une abréviation (« M. »). Il ne sert qu'aux paragraphes plus grands que le budget, et aucun mot n'est perdu.
    - `[low]` `[patch]` Branches non testées. Groupé avec les constats Verification Gap : tests ajoutés.
    - `[false]` `[reject]` Le test d'intégration ne tourne que sous Windows. Le projet vise uniquement Windows 11 natif (D2). L'assertion `raison in (terminee, longueur)` est voulue, puisque `max_tokens` vaut 300.
  - **Edge Case Hunter**
    - `[medium]` `[patch]` Morceau terminé en `longueur` ou `interrompue`, fusionné sans signal. Même correctif que la raison la plus grave.
    - `[medium]` `[patch]` Fusion intermédiaire tronquée. Même correctif.
    - `[low]` `[patch]` `delai_premier_token_ms` additionné. Même correctif que Blind Hunter n°3.
    - `[low]` `[reject]` Historique long. Doublon de Blind Hunter n°5.
    - `[medium]` `[patch]` Sortie non plafonnée à la réserve. Même correctif que Blind Hunter n°1.
    - `[low]` `[reject]` Progression des fusions intermédiaires sur plusieurs tours. Doublon de Blind Hunter n°6.
    - `[low]` `[reject]` Jointure `\n` entre des morceaux de phrase. Doublon de Blind Hunter n°13.
    - `[low]` `[patch]` Une ligne vide contenant une espace insécable n'était pas un séparateur. Correctif : `_LIGNE_VIDE = \n[^\S\n]*(?:\n[^\S\n]*)+`. Test `test_ligne_vide_avec_blancs_unicode`.
    - `[low]` `[reject]` Un prompt qui déclarerait `type` sans `type_courrier`. Aucun prompt n'est dans ce cas : CT déclare les deux.
    - `[false]` `[reject]` Un mot isolé dépasse le budget. C'est l'exception écrite dans la spec (« sauf un mot isolé »), et il n'y a aucune troncature.
  - **Verification Gap**
    - `[low]` `[patch]` `urls_inventees` n'était pas observé sur le chemin long. Test `test_urls_inventees_chemin_long` ajouté.
    - `[low]` `[patch]` Fusions intermédiaires blanches non testées. Tests `test_fusion_intermediaire_blanche_exclue` et `test_fusions_intermediaires_toutes_blanches_erreur` ajoutés.
    - `[low]` `[patch]` Contenu non textuel sur le chemin `_plan` non testé. Test `test_notes_en_liste_au_dela_du_budget_un_seul_appel` ajouté.
    - `[low]` `[patch]` `delai_premier_token_ms` cumulé. Même correctif que Blind Hunter n°3.
    - `[low]` `[patch]` `fait` et `total` des fusions intermédiaires non vérifiés. Assertion ajoutée.
  - **Intent Alignment**
    - `[low]` `[reject]` `inference/` modifié, hors de la zone stricte. Décision consignée : ajout minimal de `taille_contexte` (`ClientLlama`, `ServeurLlama.client()`). Sans lui, la garantie de FR-13 ne pourrait pas tenir avec le vrai serveur.
    - `[low]` `[reject]` La garantie dépend de `taille_contexte`. `ServeurLlama` le fournit toujours, et un port sans cet attribut garde le comportement de la 4.2.
    - `[low]` `[reject]` Le test réel est exclu par défaut et porte sur CR-006 (5 480 mots, moins de 6 000). CR-006 est l'item le plus long du jeu gelé. Le seuil de 6 000 à 9 000 mots est couvert par les tests unitaires.
    - `[false]` `[reject]` Étapes de progression en plus de « Partie i sur n ». Elles ne contredisent pas l'AC 2, qui impose les parties puis la fusion.
    - `[false]` `[reject]` Le correctif CT est fait dans `construire_messages` et non à la frontière item → requête. C'est la lettre de l'intention (« fais accepter cette clé par le Harnais »).
    - `[low]` `[reject]` `taches.toml` reçoit un commentaire et non une section « Emplacements ». Ce fichier n'a pas de telle section : la déclaration vit dans la section `## Emplacements` de `CT.md`, et le commentaire de `taches.toml` y renvoie.

## Design Notes

Budget d'un morceau : `taille_contexte − reserve_sortie_tokens`, mesuré sur les messages `CR-morceau` complets, avec la partie rendue « 9999 sur 9999 » pendant la mesure (n inconnu avant le découpage ; borne haute). Les appels de morceau n'incluent pas l'historique de la conversation ; la fusion finale l'inclut (`ctx.messages_pour`), comme l'appel unique.

`Progression(etape="Partie i sur n", fait=i-1, total=n)` est émis avant le morceau i ; `Progression(etape="Fusion des parties", fait=n, total=n)` avant la fusion finale.

## Verification

**Commands:**
- `uv run pytest tests/harness tests/inference -q` -- expected: tout passe.
- `uv run pytest -q` -- expected: aucun échec, y compris CT.jsonl.
- `uv run ruff check` et `uv run ruff format --check` -- expected: propres.
- `SLMSP_VENDOR_DIR=… SLMSP_MODELS_DIR=… uv run pytest tests/harness/test_integration_compte_rendu.py -m integration -s` -- expected: découpage réel puis fusion, test passé.

## Auto Run Result

Status: done

**Résumé.** Le Compte rendu a désormais son propre traitement, `harness/taches/compte_rendu.py`.
- **Entrée qui tient** dans `taille_contexte − reserve_sortie_tokens` (mesurée par `LlmPort.compter_tokens`) : un seul appel avec le prompt CR, par délégation à `redaction.traiter`.
- **Entrée trop longue** :
  1. découpage pur sur des limites de paragraphe, avec le chevauchement configuré (`harness/decoupage.py`) ;
  2. une synthèse silencieuse par morceau (`CR-morceau`), précédée de `Progression("Partie i sur n")` ;
  3. des fusions intermédiaires si les synthèses débordent ;
  4. la fusion finale (`CR-fusion`), seule diffusée en `Jeton`.

  Aucun mot n'est tronqué. Les appels du chemin long sont plafonnés à `max_tokens = min(appelant, réserve)`. Le `Fin` final porte la raison la plus grave de tous les appels, l'usage cumulé (sans `delai_premier_token_ms`) et `urls_inventees`.

Le report de la 4.2 est traité : la clé `type` des items CT gelés est un synonyme déclaré de `type_courrier`, rendu exactement comme lui.

**Fichiers.**
- `src/slmsp/harness/decoupage.py` (nouveau) : `paragraphes`, `empaqueter`, `regrouper` et `decouper`, fonctions pures. Un paragraphe trop grand est redécoupé en lignes, puis en phrases, puis en mots.
- `src/slmsp/harness/taches/compte_rendu.py` (nouveau) : chemins court et long, fusions intermédiaires, `SynthesesVides`.
- `src/slmsp/harness/prompts.py` : `SYNONYMES_CLES` (`type` → `type_courrier`), canonisation, conflit entre les deux clés ; `entree_de_requete` tient compte du synonyme ; règle documentée dans la docstring.
- `src/slmsp/harness/taches/__init__.py` : `type` ajouté au vocabulaire `EMPLACEMENTS`.
- `config/prompts/taches/CT.md` : ligne `type` dans la section Emplacements (Consigne inchangée). `config/taches.toml` : commentaire sous `[taches.CT]`.
- `src/slmsp/inference/client.py` et `serveur.py` (hors zone, ajout minimal) : attribut `ClientLlama.taille_contexte`, rempli par `ServeurLlama.client()` depuis `config.contexte`.
- Tests :
  - `tests/harness/test_decoupage.py` et `test_compte_rendu.py` (nouveaux) ;
  - `test_integration_compte_rendu.py` (nouveau, marqué `lent` et `integration`) ;
  - mis à jour : `test_prompts.py`, `test_taches.py`, `test_service.py` (CR va maintenant vers `compte_rendu`), `tests/inference/test_client.py` et `test_serveur.py`.

**Revue.** 37 constats : 0 high, 5 medium, 27 low, 5 false.
- **Corrigés** (entrées groupées) :
  - medium : plafond `max_tokens` à la réserve sur le chemin long ;
  - medium : raison la plus grave reportée dans le `Fin` final ;
  - low : `delai_premier_token_ms` n'est plus cumulé ;
  - low : ligne vide en blancs Unicode reconnue comme séparateur ;
  - low : tests ajoutés (URL inventées sur le chemin long, fusions intermédiaires blanches, contenu non textuel, `fait`/`total` des fusions intermédiaires).
- **Reportés** : aucun.
- **Rejetés** : les autres, avec leur motif dans le journal de tri. Principaux motifs : coût des mesures acceptable, multi-tour renvoyé à J4, duck typing assumé, et doublons.

**Revue de suivi recommandée : true.** Deux entrées medium ont été corrigées (plafond `max_tokens`, raison la plus grave). Risque non vérifié : la qualité des comptes rendus longs, avec la sortie de chaque morceau plafonnée à la réserve (1 024 tokens), n'est pas mesurée. La Baseline (5.3) devra le regarder.

**Vérification.**
- `uv run ruff check` et `ruff format --check` : propres.
- `uv run pytest -q` : 2 221 passés, 166 sautés, 0 échec. `test_items_reels_passent_construire_messages[CT.jsonl]` passe.
- **Test réel**, relancé après les correctifs : `uv run pytest tests/harness/test_integration_compte_rendu.py -m integration -s`, avec `SLMSP_VENDOR_DIR` et `SLMSP_MODELS_DIR` du dépôt principal. Résultat : 1 passé en 114 s.
  - Configuration : Granite 1B en CPU, contexte 4 096 ; item gelé CR-006 (5 480 mots).
  - Déroulé : 4 appels `CR-morceau` (« Partie 1 sur 4 » à « Partie 4 sur 4 »), puis « Fusion des parties » et 1 appel `CR-fusion`.
  - Mesure : 397 `compter_tokens`.
  - Sortie : compte rendu structuré de 192 mots, `Fin(raison=longueur)` à cause de `max_tokens=300` dans le test, 11 456 tokens de prompt cumulés.
- Aucune dépense d'API.

**Décisions prises seul.**
- La taille du contexte vient d'un attribut optionnel `taille_contexte` du `LlmPort`. Ce n'est pas un membre du `Protocol` ; `ServeurLlama` le fournit. Sans lui, un seul appel est fait, comme dans la 4.2.
- Le budget d'un morceau est mesuré avec la partie rendue « 9999 sur 9999 ».
- Les morceaux sont envoyés sans l'historique ; la fusion finale l'inclut.
- `notes` et `transcription` sont découpées séparément, dans l'ordre de `ORDRE_CLES`.
- Fusions intermédiaires, avec `Progression("Fusion intermédiaire j sur m")`, quand les synthèses débordent.
- Une synthèse blanche est ignorée ; si toutes le sont, `SynthesesVides` est levée (le service émet `Erreur`).
- Appel unique (repli) si le budget est ≤ 0, si le contenu n'est pas textuel, ou si un mot seul ne tient pas avec la consigne. Rien n'est tronqué : l'erreur du serveur reste visible.
- Plafond `max_tokens` à la réserve sur le chemin long seulement.
- `type` est un synonyme de `type_courrier` dans `construire_messages`. Les deux clés présentes ensemble lèvent `EntreeInvalide`.

**Risques résiduels.**
- Le découpage appelle souvent le tokenizer du serveur (397 appels pour CR-006). C'est acceptable aujourd'hui, mais plus coûteux sur de très longues entrées.
- `delai_premier_token_ms` inclut tous les appels de morceau (environ 90 s en CPU), puisque seule la fusion finale diffuse.
- En multi-tour, un historique long peut déclencher le chemin long sans le rendre utile.
- Le découpage en phrases peut couper après une abréviation, mais seulement pour un paragraphe plus grand que le budget, sans perte de mot.
- L'item gelé le plus long (CR-006) fait 5 480 mots, moins que les 6 000 mots de FR-13 : la note de la 7.4 reste à relire par Anaël.
