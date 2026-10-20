# Spec O6 — Génération Mistral vérifiée et régénérée (étage 1)

Méthodologie v2 (`plan-methodo-2026-10-20.md` §4 bis, §7 bis). Story à risque (D1, verrous AD-3 du Générateur, budget, données) : relue avant code. Dépend de **O1** (juge de données, `juger_candidat`) et de **C2** (clé de réutilisation, réponses tronquées). Pour LC, **O5** passe avant le run réel si elle change le seed (voir § Réutilisation).

## Découpage (deux stories, dans cet ordre)
- **O6a — Vérification** (sans régénération, sans changement du Générateur) : module `data/verification.py`, branchement du juge O1, `verification.jsonl`, `ecartees.jsonl`, rapport, échantillon. Une cible refusée est écartée. Livrable seul : il mesure déjà le taux de refus des cibles v14.
- **O6b — Régénération** : gabarits de correction, amorce de corrections, extension du Générateur (verrou 3/5), boucle d'essais. Touche AD-3 : relue avec ses tests de verrous (`tests/data/test_verrous_ad3*.py`).

## But
Que chaque cible CR, LC, CT d'entraînement soit **juste au sens de la grille** avant d'entrer dans un jeu : tests déterministes, puis juge DeepSeek (O1), puis (O6b) régénération par Mistral avec le motif du refus, au plus 2 nouveaux essais, puis écart.

## Flux par session (CR, LC, CT)
1. Cible de l'essai 1 = réponse finale de la session générée normalement (réutilisée du journal si elle existe : voir § Réutilisation) → **tests déterministes**.
2. Tests passés → **juge O1**. Accepté → cible retenue.
3. Refus (tests ou juge) → (O6b) **régénération Mistral** de la **dernière étape seulement** (CR : le compte rendu, la transcription est gardée ; LC, CT : l'appel unique) avec le gabarit de correction de la tâche ; l'essai suivant repasse 1-2. Au plus `essais_max = 3` au total (`[verification] essais_max` de `donnees.toml`).
4. Toujours refusé → session **écartée** (consignée avec ses motifs).

## Tests déterministes (`src/slmsp/data/verification.py`, fonctions pures)
Règle commune : **réutiliser les contrôles existants de `validate`** (`valeur_absente`, `url_inventee`, `cr_sections_manquantes`, `ct_format_incomplet`, `lc_valeur_perdue`, `core.texte.extraire_nombres`, nombres en lettres) en les factorisant dans `verification.py`, appelé ensuite par `validate` (comportement de `validate` inchangé, `tests/data/test_validate*.py` verts). Une cible acceptée par O6 ne doit pas être rejetée ensuite par `validate`.
Chaque contrôle rend `Motif(code, critere, bloquant, message, extraits)` ; extraits = sous-chaînes exactes de la cible ou de la source. Un motif **non bloquant** n'entraîne pas de refus : il est transmis au juge et au rapport.
- **CR** (source = transcription) :
  - quatre sections dans l'ordre (bloquant) ; plafond de mots `[generateur.plafonds_mots] CR` (bloquant) ;
  - nombres et dates absents de la transcription (bloquant, contrôle `valeur_absente` existant) ;
  - **noms propres** : mot capitalisé de la cible absent de la transcription **sans tenir compte de la casse ni des accents**, hors premier mot de ligne, hors mot après `.`, `!`, `?`, `:`, puce ou numéro, hors liste d'exceptions (`[verification.exceptions_noms]` : titres de section, civilités et abréviations « M. », « Mme », « Madame », « Monsieur », mois, jours, « État », « République »…) → **bloquant** seulement après calibrage (voir § Calibrage), sinon non bloquant ;
  - responsable et échéance des actions : **pas de test déterministe** (un responsable « le service juridique » ou une échéance « avant la prochaine réunion » échappent aux regex) ; laissé au juge (couverture, actions `partielle`). Seul contrôle : section Actions non vide (une action ou une phrase disant qu'il n'y en a pas).
- **LC** (source = texte) :
  - **classes** de modalité et de condition, chacune présente dans la source doit rester présente dans la cible (bloquant, extrait de la source) : condition {si, sauf, à condition, sous réserve, en cas de, lorsque}, restriction {uniquement, seulement, exclusivement, ne … que}, obligation {formes de *devoir* (doit, doivent, devez, devra, devrez…), obligatoire, obligation, être tenu de, il faut}, permission {formes de *pouvoir* (peut, peuvent, pouvez, pourra…), possible, avoir le droit}, interdiction {interdit, ne … pas + *pouvoir*/*devoir*, il est défendu}, échéance {au plus tard, avant le, dans un délai de}. Le français clair change la personne et la construction (« le demandeur doit » → « vous devez ») : on compare des **classes lemmatisées par liste**, pas des chaînes, et la **présence** de la classe, pas son nombre ; une baisse du nombre est un motif non bloquant transmis au juge. Listes dans `[verification.lc_marqueurs]` ;
  - modalité inversée : laissée au juge ;
  - aucun nombre, montant, date ni référence nouveaux (bloquant, `valeur_absente`) ; valeurs de la source conservées (bloquant, `lc_valeur_perdue`) ;
  - formule de conseil absente de la source (« nous vous conseillons », « n'hésitez pas », « pensez à », « il est recommandé ») (bloquant) ;
  - pas de titre en première ligne (bloquant) ;
  - **lisibilité** : gain de Kandel-Moles (`core.texte.kandel_moles`, cible − source) ≥ `[verification] gain_km_min` (défaut 10, valeur de `gain_km_min` d'`evaluation.toml` recopiée, le paquet `data` ne lisant pas la config d'évaluation) : bloquant. Le score LC du test est plafonné à 50 sous ce gain moyen.
- **CT** (source = amorces `type_courrier`, `objet`, `elements_connus`) :
  - blocs **détectables** dans l'ordre (bloquant) : lieu et date, ligne `Objet :`, références, formule d'appel, formule de politesse, signature ; motifs dans `[verification.ct_blocs]` (expressions régulières). Expéditeur et destinataire (non détectables de façon fiable) : laissés au juge (conformité) ;
  - au moins un emplacement entre crochets : non bloquant (comme `ct_sans_emplacement` de `validate`) ;
  - nombres, dates et références absents des amorces hors crochets (bloquant) ; noms propres : même règle que CR, appliquée hors crochets.

## Calibrage (avant tout appel payant)
Commande sans appel : `--verifiee --sans-juge --essais-max 1` sur les cibles v14 (réutilisées du journal) : taux de refus par code et par tâche dans `rapport.json`, et 20 refus tirés (graine fixe) dans `calibrage.md` du run. L'orchestrateur relit ces 20 refus ; un code dont plus de 20 % des refus relus sont des faux positifs passe non bloquant (config) avant le run payant. Consigné au journal du run autonome.

## Régénération (O6b) et D1
- **Gabarits de correction** : `config/prompts/generateur/{cr,lc,ct}-correction.md` (nouveaux identifiants, versionnés, validés par `core.gabarits`, verrou 6) = consigne du gabarit de la tâche + emplacement `{corrections}`. Le gabarit d'origine reste inchangé (ses `session_id` et ses réponses journalisées restent réutilisables).
- **Bloc de corrections** : composé **uniquement** (a) de phrases fixes de l'outillage, une par `code` de motif, dans `config/prompts/generateur/corrections.md` (versionné ; des consignes, jamais un exemple de réponse ni une formulation attendue), (b) des **extraits** vérifiés comme sous-chaînes de la cible refusée ou de la source, (c) du champ `motif` de DeepSeek (≤ 300 caractères) dont tout segment entre guillemets ou chevrons absent de la cible et de la source est retiré (empêche le juge de glisser une réécriture). Rendu déterministe : mêmes motifs → mêmes octets.
- **Provenance (verrous 3 et 5 du Générateur)** : `Generateur.generer` refuse tout texte libre et toute amorce hors seed ou dérivée d'une réponse Mistral. Le bloc entre donc comme **amorce de corrections** : nouvel `auteur_contenu = "verification"` (`AuteurAmorce`, pas `AuteurContenu` : ce n'est pas une source du Registre), emplacement `corrections` seul admis, créée par une méthode du Générateur `amorce_corrections(session_id, essai, motifs)` qui **re-rend elle-même** le texte depuis les motifs structurés (codes, extraits revérifiés contre le journal et les amorces, motif filtré) ; aucune chaîne fournie par l'appelant n'est admise telle quelle. Consignée dans `amorces-derivees.jsonl` du run avec ses motifs structurés.
- Jamais de texte rédigé par Claude, jamais de « réponse attendue », jamais la sortie d'un autre modèle comme exemple. Seul Mistral rédige ; DeepSeek ne fait que noter.
- **Jeu d'entraînement** : le bloc de corrections n'entre jamais dans un exemple. `brut.jsonl` cite la chaîne retenue seulement (CR : `[appel transcription, appel CR retenu]`, `build` exige 2 appels ; LC, CT : `[appel retenu]`) ; l'amorce de corrections n'est **pas** dans `amorce_ids` (sinon `build` la mettrait dans l'entrée CT) ; `validate` (`amorce_verifiee`) et `build` admettent l'appel de correction (gabarit journalisé `*-correction`) comme dernier appel. Test : l'exemple `train.jsonl` d'une session régénérée a la même entrée que celui de la même session sans régénération.

## Identifiants et réutilisation
- Les essais gardent le **`session_id` de la session** (motif `^[a-z0-9]+-[0-9a-f]{24}$` imposé par `SessionBrute` et les cassettes ; `session_id#essai2` est refusé par le schéma). L'essai se distingue par le gabarit (`*-correction`) et l'`amorce_id` de corrections (`corr-<session_id>-e<n>-<sha12 du texte>`).
- Réutilisation : la règle existante de `sessions._reutilisable` (même session, gabarit, amorces, messages précédents) plus C2 (réponse `length` jamais réutilisée, `max_tokens` dans la clé) suffit : un rejeu avec les mêmes verdicts (cache O1) reproduit les mêmes amorces de corrections et ne repaie rien.
- Cibles v14 comme essai 1 **sans repayer** : nouveau run `data generate --depuis <SEED v14> --verifiee` ; mêmes gabarits et même seed → mêmes `session_id` → réponses réutilisées du journal (`--depuis` de `generate` désigne le **seed**, pas un run generate). Si O5 change le seed ou le gabarit LC, les LC sont regénérées (coût compté dans l'estimation).
- Autres tâches du jeu complet : `--taches CR,LC,CT --completer-depuis <GENERATE_RUN_ID v14>` (mécanisme existant, sans appel).

## Commande et sorties
`slmsp data generate --depuis SEED_RUN_ID --verifiee [--taches CR,LC,CT] [--completer-depuis GENERATE_RUN_ID] [--essais-max 3] [--sans-juge] [--plafond-estime-mistral EUR] [--plafond-estime-openrouter EUR]` ou `--reprendre RUN_ID`.
- Run `runs/data-generate/<id>/` (type inchangé, lisible par `validate`) : `brut.jsonl` au **format `SessionBrute` inchangé** (cibles retenues seulement ; le schéma refuse un champ `verification`) ; `verification.jsonl` (une ligne par session : essais, appel_ids de chaque essai, motifs par essai, `candidat_id` et clé du verdict O1, issue) ; `verdicts.jsonl` (verdicts O1, index du cache) ; `ecartees.jsonl` ; `rapport.json` (par tâche : acceptées d'emblée, après 1 ou 2 régénérations, écartées ; motifs les plus fréquents ; part des refus par tests vs juge ; coûts Mistral et OpenRouter de ce run).
- Session écartée : ligne dans `ecartees.jsonl` **et** `AbandonSession` (nouveau motif `verification_refusee` dans `MotifAbandon`) pour que la reprise ne la rejoue pas.
- La suite (validate → filter → build → nettoyage) est inchangée et lit `brut.jsonl`.
- **Échantillon** : 5 cibles retenues par tâche (graine fixe) et 5 écartées, avec motifs, dans `echantillon.md` du run (relecture d'Anaël levée sous condition de consigner, §7 bis).

## Budget
Mistral → `mistral.generation` (sous-plafond 8 €) ; DeepSeek → `openrouter` via O1 (`juge-donnees-openrouter`). Campagne `methodo-v2-2026-10-20`, aucun nouveau poste ni plafond. Estimation **pire cas** affichée avant lancement (essais réutilisés à 0 ; régénérations comptées pour `essais_max − 1` par session refusable, au taux de refus du calibrage, borne haute = toutes) ; refus si elle dépasse le plafond donné. Ordre de grandeur : ~195 sessions (CR 80, LC 80, CT 35) ; DeepSeek ~1 € pour 3 essais ; Mistral ~1 € (réponses v14 réutilisées).

## Critères de fin
- O6a : tests unitaires de chaque contrôle (cas passant, cas refusant, **cas piège** : « Vous devez » pour « Le demandeur doit », « Mme » pour « Madame », mot capitalisé après puce, nom présent en minuscule dans la transcription) ; `validate` inchangé ; calibrage sans appel ; écart et `AbandonSession` ; reprise sans double appel ; budget refusé au-delà du plafond.
- O6b : boucle avec clients simulés (refus test → régénération ; refus juge → idem ; 3 refus → écartée) ; **test D1** : le prompt de régénération = gabarit de correction + amorces de la session + bloc rendu des seuls phrases fixes, extraits vérifiés et motif filtré (toute autre chaîne fait échouer) ; amorce de corrections à texte fourni par l'appelant refusée ; `validate` et `build` acceptent une session régénérée, et son exemple d'entraînement ne contient pas le bloc ; réutilisation sans coût au rejeu ; tests de verrous AD-3 verts.
- Aucun appel réel ; ruff ; contrôle rapide.

## Revue de la spec
Relecture du 2026-10-20 (reviewer, avant code), contre `data/{generate,sessions,validate,build}.py`, `mistral/generateur.py`, `core/schemas/{session_donnees,amorce}.py`, `cli/data.py`, `config/prompts/generateur/{cr,lc,ct}.md`, `eval/grille-juge-v1.md`.

| # | Gravité | Constat | Changement |
|---|---|---|---|
| 1 | high | Le Générateur refuse tout texte libre (verrou 3) et toute amorce hors seed ou réponse Mistral (verrou 5) : le bloc « Corrections exigées » n'avait aucun chemin d'entrée. | Gabarits `*-correction`, amorce de corrections `auteur_contenu = "verification"` rendue par le Générateur lui-même depuis des motifs structurés. |
| 2 | high | `session_id#essai2` viole le motif `SessionId` (`SessionBrute`, cassettes). | Même `session_id`, essai distingué par gabarit et `amorce_id` de corrections. |
| 3 | high | `brut.jsonl` « avec champ `verification` » : `SessionBrute` ne porte aucun texte et refuse les champs inconnus ; `build` exige 2 appels pour CR et prend toutes les amorces de `amorce_ids` comme entrée CT, donc le bloc de corrections fuirait dans l'exemple. | `brut.jsonl` inchangé (chaîne retenue seule), `verification.jsonl` à part, amorce de corrections hors `amorce_ids`, test d'absence dans `train.jsonl`. |
| 4 | medium | `--depuis <run generate>` contredit la CLI (`--depuis` = run seed). | Essai 1 gratuit par réutilisation du journal avec le même seed ; `--completer-depuis` pour les autres tâches. |
| 5 | medium | Faux positifs : marqueurs LC comptés en chaînes (« doit » → « vous devez » est la réécriture attendue) ; « responsable et échéance » par regex ; mots capitalisés sans comparaison insensible à la casse. | Classes lemmatisées, présence plutôt que nombre ; responsable et échéance au juge ; règle des noms durcie ; étape de calibrage gratuite avant le run payant. |
| 6 | medium | Contrôles en doublon de `validate` (valeurs, sections, objet, politesse) : risque de divergence et de cibles acceptées puis rejetées. | Factorisation dans `verification.py`, appelée par `validate`. |
| 7 | medium | LC : gain de Kandel-Moles absent, alors que le test plafonne LC à 50 sans gain ≥ +10. | Contrôle bloquant ajouté. |
| 8 | medium | CT : liste de blocs « lue depuis la config de la tâche » inexistante ; expéditeur et destinataire non détectables. | `[verification.ct_blocs]` pour les blocs détectables ; le reste au juge. |
| 9 | medium | Story trop large et touchant AD-3. | Découpage O6a (vérification) / O6b (régénération). |
| 10 | low | Session écartée rejouée à la reprise. | `AbandonSession` motif `verification_refusee`. |
| 11 | low | Motif DeepSeek libre dans le prompt : risque d'y glisser une réécriture. | Segments cités absents de la cible et de la source retirés. |
