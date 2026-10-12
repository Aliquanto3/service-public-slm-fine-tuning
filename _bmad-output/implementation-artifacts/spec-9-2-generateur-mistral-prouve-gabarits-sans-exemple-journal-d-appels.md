---
title: "Story 9.2 — Générateur Mistral prouvé (gabarits sans exemple, journal d'appels)"
type: 'feature'
created: '2026-10-12'
status: 'done'
baseline_revision: '9fe22a0b9342851ed6ba7026e04251a7d0de7870'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-9-context.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-5-5-adaptateur-mistral-et-second-juge-sur-l-echantillon-de-20.md'
warnings: ['oversized']
deferred:
  - summary: >-
      Le gabarit traces-rd peut être appelé sans outils, car le générateur n'envoie encore ni tools ni tool_choice.
    evidence: |-
      La consigne de traces-rd demande d'utiliser les outils mis à disposition. Generateur.generer n'envoie aucun paramètre tools (exclu de 9.2, à la charge de 9.4). Un premier tour RD sans outils pousserait donc Mistral à inventer des jeux de données. La ligne serait journalisée ok et réutilisable. La story 9.4 doit ajouter les outils, ou refuser traces-rd sans outils.
    location: >-
      src/slmsp/mistral/generateur.py:generer ; config/prompts/generateur/traces-rd.md
    severity: medium
  - summary: >-
      Une amorce publique n'est contrôlée que par son propre sha_texte, sans relecture de data/raw.
    evidence: |-
      AD-3 verrou 5 exige que jeu, revision et ligne soient relus et hachés au build. En 9.2, le SHA est recalculé à partir du texte de la ligne amorces.jsonl elle-même. La relecture de la source revient à 9.3 (seed) et à 9.6 (build).
    location: >-
      src/slmsp/mistral/generateur.py:_resoudre_amorces
    severity: medium
  - summary: >-
      Le passage du journal Mistral partagé (SLMSP_VAR_DIR) en schéma v2 peut faire échouer le code v1 d'un worktree plus ancien.
    evidence: |-
      Dès qu'il ouvre un journal, JournalMistral le migre en user_version 2. Le code de la story 5.5 refuse toute version différente de 0 ou 1, et LigneAppel(**ligne) n'accepte pas de colonnes en plus. Un worktree resté sur le code 5.5 qui ouvrirait le journal du juge après une migration lèverait une erreur. Pour trancher : vérifier qu'aucun run réel du second juge ne tourne sur du code antérieur à la fusion de 9.2.
    location: >-
      src/slmsp/mistral/journal.py:JournalMistral.__init__
    severity: medium (unverified)
---

<intent-contract>

## Intent

**Problem:** Le pipeline de données (epic 9) n'a pas de générateur. L'adaptateur Mistral (5.5) refuse l'usage `generation` tant que le module `slmsp.mistral.generateur` et son jeton n'existent pas. Il faut un générateur qui ne reçoit **aucun texte libre**, résout lui-même gabarit et amorces, et laisse au journal `appels-mistral.sqlite` une preuve complète de chaque requête et de chaque réponse brute (D1.1, AD-3 verrous 3 et 6).

**Approach:** `slmsp.mistral.generateur.Generateur(seed_run_id, client=...)` vérifie les préalables (D1.2), charge les amorces de l'artefact `seed` par `core.artefacts.lire`, et `generer(gabarit_id, amorce_ids, session_id, tache, messages_precedents=None)` construit la requête à partir d'un gabarit validé par `core.gabarits`, contrôle la provenance des messages précédents, puis appelle `ClientMistral._appeler(..., jeton=_JETON)`. Le journal passe en schéma v2 (gabarit et `amorce_ids`) et exige le jeton pour `generation`. Onze gabarits sans exemple sont créés.

## Boundaries & Constraints

**Always:**
- **D1.1 absolue.** Aucun texte de Donnée d'entraînement rédigé nulle part : ni dans les gabarits, ni dans les tests, ni dans les fixtures. Les gabarits ne contiennent que des consignes et des emplacements `{nom}`. Les fixtures sont des chaînes manifestement factices et aléatoires, du genre `"<amorce-factice-" + secrets.token_hex(4) + ">"` ou `"<réponse-factice-1>"`.
- Zone : `src/slmsp/mistral/{generateur,journal}.py`, `src/slmsp/core/schemas/amorce.py`, `config/prompts/generateur/*.md`, `tests/mistral/*`. Une seule extension hors zone, minimale : `src/slmsp/mistral/client.py` (paramètre `complements_journal` de `_appeler`, et jeton délégué à `journal`). Ne pas toucher `harness/`, `fetch/`, `config/modeles/` (stories 4.3 et 8.1 en parallèle), ni `config/donnees.toml` (story 9.1).
- Couches AD-1 : `slmsp.mistral` (couche 2) n'importe que `core`, `net`, `budget` et lui-même ; donc pas `mcp`, `harness` ni `data`. La cassette est lue par `core.artefacts.lire` et validée par `core.schemas.cassette.Cassette`.
- Aucun appel réseau réel dans les tests : faux serveur `FauxMistral` de `tests/mistral/conftest.py`, journaux et racine dans `tmp_path`.

**Never:** aucune génération réelle (campagne en 9.8), aucun paramètre `tools`/`tool_choice` (story 9.4), aucune idempotence par clé (9.4), aucun extracteur de build (9.6), aucun `config/donnees.toml` versionné, aucune lecture de `eval/`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Nominal | préalables du jour, gabarit `generique`, amorce publique conforme | une requête `user` unique = consigne rendue ; journal `generation` avec gabarit, SHA, `amorce_ids`, réponse brute ; `Generation` renvoyée | — |
| Préalables | `donnees.toml` absent, date ≠ jour, modèle hors `modeles_stables` | refus à la construction | `PrealableNonSatisfait` |
| Gabarit | id hors `[a-z0-9-]+`, fichier absent, invalide, `tache` ≠ argument, emplacement non couvert | aucun appel | `GabaritInvalide` |
| Amorces | id inconnu, `sha_texte` faux, `auteur_contenu = anael`, amorce `mistral` sans ligne journalisée ou au texte différent | aucun appel | `ProvenanceInvalide` |
| Précédents | `assistant` non journalisé dans la session, `tool` absent de la cassette de la session, rôle `user`/`system` | aucun appel | `ProvenanceInvalide` |
| Journal | `inscrire(usage="generation")` sans jeton ou sans gabarit/`amorce_ids` ; usage autre avec ces champs | rien n'est écrit | `UsageInterdit` |
| Migration | journal existant en `user_version = 1` | colonnes ajoutées, version 2, lignes conservées | — |

</intent-contract>

## Code Map

- `src/slmsp/mistral/client.py` -- `_appeler(..., jeton)` (l. 264) ; `_jeton_generateur()` (l. 125) lit `slmsp.mistral.generateur._JETON` ; `inscrire` local (l. 296). Ajouter `complements_journal: Mapping[str, Any] | None = None` transmis à `journal.inscrire(..., jeton=jeton, **complements)` ; `_jeton_generateur` délègue à `journal.jeton_generateur`.
- `src/slmsp/mistral/journal.py` -- schéma v1 (`VERSION_SCHEMA = 1`, table `appels`, déclencheurs en ajout seul), `LigneAppel`, `inscrire`, `journal_pour`. Passer en v2.
- `src/slmsp/mistral/config.py` -- `ConfigMistral.refus_modele`, `modeles_autorises`.
- `src/slmsp/core/gabarits.py` -- `valider_gabarit(Path, cles_requises, cles_optionnelles)` → `GabaritValide(id, version, front_matter, consigne, emplacements, sha256)`. Accolades admises seulement en `{identifiant}`. Mots et lignes de dialogue interdits (« Question : » refusé).
- `src/slmsp/core/artefacts.py` -- `lire(chemin, "data", racine=)` : lecteur `data` autorisé sur `runs/data-*`, `data/cassettes/`, `config/prompts/`.
- `src/slmsp/core/schemas/__init__.py` -- `SchemaBase`, `Sha256` ; `core/schemas/run.py` : `MOTIF_RUN_ID`.
- `src/slmsp/core/schemas/cassette.py` -- `Cassette.interactions[{request, response}]`.
- `src/slmsp/core/messages.py` -- `valider_conversation` (structure assistant/tool, `tool_call_id`).
- `src/slmsp/core/erreurs.py` -- `ProvenanceInvalide`, `SlmspError`.
- `src/slmsp/core/canonique.py` -- `json_canonique`, `sha256_hex`.
- `tests/mistral/conftest.py` -- `banc` (`FauxMistral`, `BancMistral.client()`, `lignes_journal`), fixtures réutilisables.
- `tests/mistral/test_client.py` l. 125-310 -- tests du jeton `generation` à adapter (méta de journal requise).
- `config/prompts/taches/Q.md` -- forme d'un gabarit conforme.

## Tasks & Acceptance

**Execution:**
- `src/slmsp/core/schemas/amorce.py` -- `Amorce(SchemaBase)` : `schema_version: Literal[1]`, `amorce_id` (`[a-z0-9][a-z0-9._-]*`), `tache`, `emplacement` (`[a-z_]+`), `texte`, `sha_texte: Sha256`, `auteur_contenu: Literal["public","mistral","anael"]`, `jeu`, `revision`, `ligne` (requis si `public`), `appel_id` (requis si `mistral`, interdit sinon) -- contrat de l'artefact `seed` (`amorces.jsonl`) pour la story 9.3.
- `src/slmsp/mistral/journal.py` -- v2 : colonnes `gabarit_id`, `version_gabarit`, `sha256_gabarit`, `amorce_ids` (JSON canonique) ; migration v1→v2 par `ALTER TABLE ADD COLUMN` ; `LigneAppel` étendue ; `jeton_generateur()` ; `inscrire(..., jeton=None, gabarit_id=None, version_gabarit=None, sha256_gabarit=None, amorce_ids=None)` exige jeton et méta pour `generation`, les refuse ailleurs ; `appels_session(session_id)`.
- `src/slmsp/mistral/client.py` -- extension minimale décrite au Code Map.
- `src/slmsp/mistral/generateur.py` -- `_JETON`, `PrealableNonSatisfait`, `PrealablesGeneration`, `charger_prealables`, `message_assistant(brut)`, `Generation`, `Generateur` (voir Design Notes).
- `config/prompts/generateur/{traces-q,traces-rd,scenario-reunion,transcription-cr,cr,lc,co,re,ct,generique,validation}.md` -- consignes seulement, front-matter `id` (= nom du fichier), `version: 1`, `tache`, `max_tokens` optionnel ; chaque `{nom}` de la consigne déclaré en Emplacements et réciproquement.
- `tests/mistral/test_gabarits_generateur.py` -- verrous structurels sur les 11 gabarits.
- `tests/mistral/test_generateur.py` -- matrice I/O, signature, jeton, journal, préalables.
- `tests/mistral/test_journal.py`, `tests/mistral/test_client.py` -- migration v2, exigences du jeton et de la méta ; adapter les tests existants du jeton.

**Acceptance Criteria:**
- Given `inspect.signature(Generateur.generer)`, when on l'inspecte, then ses paramètres sont exactement `gabarit_id, amorce_ids, session_id, tache, messages_precedents` ; une chaîne libre passée comme `gabarit_id` ou `amorce_id` est refusée avant tout appel.
- Given un appel nominal, when on lit `appels-mistral.sqlite`, then la ligne porte `session_id`, `usage = generation`, modèle résolu, requête complète, `gabarit_id`, `version_gabarit`, `sha256_gabarit` (= SHA des octets du fichier), `amorce_ids`, réponse brute intégrale et son SHA, `reservation_id` ; le texte de chaque amorce figure dans la requête et aucun autre texte que la consigne rendue n'y figure.
- Given `ClientMistral.appeler("generation", ...)` ou `JournalMistral.inscrire(usage="generation")` sans `_JETON`, when on appelle, then `UsageInterdit` et aucune ligne.
- Given chaque gabarit de `config/prompts/generateur/`, when il est analysé, then `valider_gabarit` passe et il ne contient ni « ? », ni guillemets « » ou `"`, ni emplacement non déclaré : aucune question, réponse ou amorce rédigée.

### Review Findings

Revue de code du lot 1, le 2026-10-12. Détail et constats rejetés : `revue-code-lot-1-juges-mistral.md`.

- [x] [Review][Patch] P2. Rien n'interdit d'importer `_JETON` ni d'appeler `._appeler` hors de `generateur.py` (verrou 3) [src/slmsp/mistral/generateur.py:62]
- [x] [Review][Patch] P7. Aucun test ne couvre l'appel `valider_conversation(requete)` de `generer` : il manque les cas `cle-en-plus` et `reponse-en-double` [tests/mistral/test_generateur.py]

## Spec Change Log

## Review Triage Log

### 2026-10-12 — Review pass
- verdicts : 43 constats ; high 5, medium 9, low 20, false 9, maybe-false 0.
- constats :
  - **Blind Hunter** (16 constats)
    - `[high]` `[patch]` Une ligne `ok` d'un modèle refusé hors `modeles_stables` reste réutilisable comme amorce ou comme précédent. Correctif : `_ligne_admise` exige `modele_resolu ∈ modeles_stables` ; tests `test_appel_refuse_pour_modele_jamais_reutilise`.
    - `[low]` `[reject]` La ligne du journal ne porte pas `seed_run_id`. Rejeté : le run seed se retrouve par la lignée des runs (`--depuis`, AD-17) et par `brut.jsonl` (9.4), et la requête journalisée contient le texte complet des amorces. Ajouter une colonne élargirait la surface publique.
    - `[medium]` `[patch]` Les préalables ne sont vérifiés qu'à la construction. Correctif : la date est revérifiée au début de `generer` ; test `test_date_rechecked_a_chaque_generation`.
    - `[low]` `[reject]` Les précédents `assistant` sont comparés à un ensemble non ordonné. Rejeté : tout contenu admis reste une réponse Mistral journalisée de la même session (D1.1 respectée). La cohérence de l'ordre relève de la re-dérivation de 9.6, et l'imposer ici demanderait une logique nouvelle.
    - `[medium]` `[patch]` Un résultat `tool` n'est pas lié à l'appel auquel il répond. Correctif : le `tool_call_id` doit désigner un appel admis, et la cassette doit avoir le même nom de fonction et les mêmes arguments ; cas `arguments-differents`.
    - `[low]` `[reject]` Sous Windows, deux `session_id` qui ne diffèrent que par la casse partagent une cassette. Rejeté : les identifiants de 9.4 sont horodatés et aléatoires (`nouvel_identifiant_session`, avec T et Z majuscules), une collision de casse est irréaliste, et passer en minuscules les casserait.
    - `[medium]` `[defer]` `traces-rd` peut tourner sans outils. Les outils appartiennent à la story 9.4, d'où le report (voir `deferred`).
    - `[low]` `[reject]` Les passages de `traces-q` ne sont pas numérotés au rendu. Rejeté : leur mise en forme par `harness.prompts` revient à 9.4, et l'emplacement les décrit déjà comme numérotés.
    - `[low]` `[reject]` `_meta_generation_valide` est trop permissif (hexadécimal, ensemble, générateur). Rejeté : le seul appelant légitime, le Générateur, passe une liste et le SHA de `valider_gabarit`, et les gardes en plus n'apportent rien en usage normal.
    - `[low]` `[patch]` `Generation.reponse_brute` peut valoir `None` sans bruit. Correctif : `ProvenanceInvalide` est levée, et le champ est typé `bytes`.
    - `[low]` `[reject]` `max_tokens` n'a pas de plafond. Rejeté : les gabarits sont versionnés et relus, et un refus 4xx est régularisé à 0. Partie « type » : faux, car `valider_gabarit` rend toujours des chaînes.
    - `[low]` `[reject]` Un appel refusé crée ou migre quand même le journal. Rejeté : l'effet est sans conséquence (fichier vide en ajout seul).
    - `[low]` `[patch]` Le schéma `Amorce` admet deux provenances à la fois. Correctif : `jeu`, `revision` et `ligne` sont interdits hors `public` ; trois cas de test ajoutés.
    - `[low]` `[reject]` Formulation de `ct.md` et `co.md`. Rejeté : la règle des crochets couvre déjà les informations manquantes, et une révision viendra avec une incrémentation de version en 9.4 ou 9.5.
    - `[low]` `[reject]` Le contrôle du jeton est fait trois fois. Rejeté : c'est une défense en profondeur voulue, sans dommage.
    - `[low]` `[reject]` Suggestions de tests diverses. Rejeté pour ce qui n'est pas couvert par les correctifs ci-dessus : ce sont des cas marginaux sans défaut démontré.
  - **Verification Gap** (3 constats)
    - `[medium]` `[patch]` Aucun cas ne refuse un précédent issu d'une ligne `validation`. Cas `usage-validation` ajouté.
    - `[high]` `[patch]` Ligne `ok` d'un modèle refusé réutilisable : même cause que le premier constat du Blind Hunter, même correctif.
    - `[false]` `[reject]` `importorskip("mistralai")`. Faux : l'extra `data` est installé, d'où 198 passés et 0 ignoré ; la remarque est préexistante.
  - **Edge Case Hunter** (14 constats)
    - `[high]` `[patch]` Modèle refusé, statut `ok` : même cause et même correctif que ci-dessus.
    - `[high]` `[patch]` Chaînage d'amorces depuis un modèle instable : même correctif.
    - `[high]` `[patch]` Précédent issu d'un modèle refusé : même correctif.
    - `[medium]` `[patch]` Générateur actif après minuit : même correctif que la revérification de la date.
    - `[low]` `[reject]` Un élément non hachable dans `amorce_ids` lève `TypeError`. Rejeté : c'est un échec bruyant, sur une entrée impossible en usage normal.
    - `[low]` `[reject]` `amorce_ids` peut être un générateur dans `complements_journal`. Rejeté : même raison, le seul appelant passe une liste.
    - `[low]` `[reject]` SHA du gabarit non hexadécimal. Rejeté : il vient toujours de `sha256_hex`.
    - `[low]` `[reject]` `max_tokens` sans plafond : voir la ligne correspondante du Blind Hunter.
    - `[low]` `[reject]` `content` en morceaux. Rejeté : l'échec est bruyant (`ProvenanceInvalide`) et `mistral-large` renvoie une chaîne.
    - `[medium]` `[patch]` `tool_call_id` non lié à son appel : même correctif que le constat du Blind Hunter.
    - `[low]` `[reject]` Précédents terminés par un message `assistant`. Rejeté : l'API répond par un refus 4xx, journalisé et régularisé à 0 €.
    - `[low]` `[reject]` Casse des `session_id` sous Windows : même raison que plus haut.
    - `[medium]` `[defer]` Amorce publique non relue dans `data/raw`. La relecture revient à 9.3 et 9.6, d'où le report (voir `deferred`).
    - `[false]` `[reject]` `dossier_gabarits` hors de la liste AD-24. Faux : AD-24 lie les lecteurs `data` et `train`, pas `slmsp.mistral`, et le chemin par défaut est `config/prompts/generateur`.
  - **Intent Alignment** (10 constats)
    - `[false]` `[reject]` (a) Contrôle du modèle résolu avant l'appel. Faux pour la partie « avant » : le modèle résolu n'est connu qu'avec la réponse, et le modèle demandé est bien vérifié au démarrage. La partie sur la réutilisation est corrigée plus haut.
    - `[false]` `[reject]` (b) Jeton importé par les tests. Faux en tant que défaut : seuls les tests importent `_JETON`, et le refus sans jeton est couvert.
    - `[low]` `[reject]` (c) Requête non reconstructible à partir de la seule ligne : voir le rejet sur `seed_run_id`.
    - `[medium]` `[defer]` (d) `sha_texte` contrôlé seulement dans sa propre ligne : même report que la relecture de `data/raw`.
    - `[false]` `[reject]` (e) FIDELE et INFIDELE comme réponse type. Faux : `validation.md` sert au contrôle (usage `validation`) et ne produit aucune Donnée d'entraînement. Le SHA des gabarits au MANIFEST revient à 9.6.
    - `[false]` `[reject]` (f) Préalables lus avant la story 9.1. Faux en tant que défaut : décision consignée, lecture tolérante de la seule table `[mistral]`.
    - `[false]` `[reject]` (g) `client.py` hors zone. Faux : l'extension est déclarée par la spec et minimale.
    - `[false]` `[reject]` (h) Convention `data/cassettes/<session_id>.json`. Faux : c'est celle de `mcp.enregistrement.chemin_cassette("data", …)`. La partie sur le lien avec l'appel est corrigée plus haut.
    - `[medium]` `[defer]` (i) Journal partagé migré en v2 : report (voir `deferred`).
    - `[false]` `[reject]` (j) Export dans `__init__`, réponse fixe, absence de commit. Faux : `slmsp.mistral/__init__` n'importe rien, par choix, pour ne pas charger `mistralai` ; le commit est fait à la finalisation.

## Design Notes

- **Préalables (décision seule).** `config/donnees.toml` appartient à 9.1, encore en backlog. Le générateur lit seulement la table `[mistral]` de ce fichier, par `tomllib` et un modèle pydantic qui ignore les clés en plus : `conditions_verifiees_le` (date) et `modeles_stables` (liste). Il refuse de démarrer (`PrealableNonSatisfait`) si le fichier ou la table manque, si la date n'est pas `aujourd_hui()` (date locale, injectable), ou si `client.config.modele` n'est pas dans `modeles_stables`. Après l'appel, un modèle résolu hors `modeles_stables` lève `ModeleMistralRefuse` ; l'appel reste journalisé.
- **Constructeur.** `Generateur(seed_run_id, *, client, racine=None, fichier_donnees=None, dossier_gabarits=None, aujourd_hui=date.today)`. Les valeurs par défaut viennent de `racine_projet()`. Il lit `runs/data-seed/<seed_run_id>/amorces.jsonl` par `lire(..., "data", racine=racine)`. Un `amorce_id` en double est refusé.
- **Rendu.** Les amorces sont groupées par `emplacement`, dans l'ordre de `amorce_ids`, et jointes par `"\n\n"`. Chaque emplacement déclaré doit recevoir au moins une amorce, et chaque amorce doit viser un emplacement déclaré. La substitution `{nom}` se fait en une passe par regex (un `{x}` dans une amorce n'est pas réinterprété). La requête vaut `[{"role": "user", "content": consigne_rendue}] + messages_precedents`. `max_tokens` vient du front-matter (2048 par défaut). `tokens_entree_estimes` vaut `ceil(caractères / 3)`.
- **Contrôles des amorces.** `amorce.tache` doit être égale à `tache`. `sha256_hex(texte)` doit être égal à `sha_texte`. `anael` est refusé (décision différée d'Anaël). Pour `mistral`, la ligne journalisée `appel_id` doit exister, avoir le statut `ok`, et `message_assistant(brut)["content"]` doit être égal à `texte`.
- **Tâches.** `tache` ∈ {Q, RD, CR, LC, CO, RE, CT, generique} et doit être égal au `tache` du gabarit. Le gabarit `validation` porte `tache: validation` : il est réservé à l'usage `validation` (story 9.5) et inutilisable ici.
- **Précédents.** Rôles `assistant` et `tool` seulement. `message_assistant(brut)` lit `choices[0].message` et garde `role`, `content` non vide, `tool_calls` non vide. Un `assistant` est accepté si son JSON canonique normalisé est égal à celui d'une ligne `generation`/`ok` de la même `session_id`. Un `tool` est accepté si `data/cassettes/<session_id>.json` contient une interaction `tools/call` dont le `result` donne exactement son `content`, en JSON canonique ou en concaténation des `content[].text`, et dont le nom est le même quand `name` est donné. Ensuite, `valider_conversation` s'applique à la requête entière.

## Verification

**Commands:**
- `uv run pytest tests/mistral -q` -- expected: tout passe, aucun réseau
- `uv run pytest -q` -- expected: tout passe (sinon liste exacte des échecs préexistants hors zone)
- `uv run ruff check` -- expected: aucun écart

## Auto Run Result

Status: done

**Résumé.** `slmsp.mistral.generateur.Generateur` est le seul chemin d'écriture `usage = generation`. Il passe par un jeton de module, plus la méta du gabarit et des amorces, contrôlés avant toute réservation. Il n'accepte aucun texte libre :
- le gabarit est résolu par identifiant et validé par `core.gabarits` ;
- les amorces sont lues dans l'artefact `seed` par `core.artefacts.lire`, et leur `sha_texte` est revérifié ;
- les précédents `assistant` et `tool` doivent figurer au journal et dans la cassette de la session ;
- les préalables D1.2 sont lus dans la table `[mistral]` de `config/donnees.toml` et revérifiés à chaque appel.

Le journal `appels-mistral.sqlite` passe en schéma v2. Onze gabarits sans exemple sont créés. Aucun appel réel n'a été fait (0 €).

**Fichiers.**
- `src/slmsp/mistral/generateur.py` (nouveau) : `Generateur`, `Generation`, `PrealableNonSatisfait`, `charger_prealables`, `message_assistant`.
- `src/slmsp/mistral/journal.py` : schéma v2 avec migration depuis v1 ; `jeton_generateur`, `controler_inscription`, `appels_session`.
- `src/slmsp/mistral/client.py` (extension hors zone, déclarée) : `complements_journal` ; le contrôle du jeton est délégué au journal.
- `src/slmsp/core/schemas/amorce.py` (nouveau) : `Amorce` avec une seule provenance (`public` ou `mistral` ; `anael` refusé par le Générateur).
- `config/prompts/generateur/*.md` : 11 gabarits, consignes et emplacements seulement.
- `tests/mistral/test_generateur.py` et `test_gabarits_generateur.py` (nouveaux) ; `test_journal.py` et `test_client.py` (adaptés).

**Revue.**
- 43 constats.
- 6 correctifs :
  - 1 high : les lignes d'un modèle refusé restaient réutilisables ;
  - 3 medium : date revérifiée à chaque appel, lien entre `tool_call_id` et arguments, test du précédent `validation` ;
  - 2 low : `reponse_brute` obligatoire, provenance unique pour une `Amorce`.
- 3 constats reportés (`deferred`) : `traces-rd` sans outils (9.4), relecture de `data/raw` (9.3 et 9.6), migration v2 du journal partagé.
- Les autres constats sont rejetés, avec leur motif dans le journal de tri.
- Relecture de suivi recommandée (`true`) : un correctif high a été appliqué, et le nouveau rattachement d'un message `tool` à son appel n'a pas encore été confronté aux formes réelles des `tool_calls` Mistral (story 9.4).

**Vérification.**
- `uv run pytest tests/mistral -q` : tout passe.
- `uv run pytest -q` : 2607 réussis, 155 ignorés, 0 échec.
- `uv run ruff check` et `ruff format --check` : propres.

**Décisions prises seul.**
1. Préalables lus dans la table `[mistral]` de `config/donnees.toml` (`conditions_verifiees_le`, `modeles_stables`), les autres clés étant ignorées, parce que 9.1 n'est pas fusionnée. 9.1 doit reprendre ces clés.
2. Forme de la requête : un message `user` unique (la consigne rendue), suivi des précédents prouvés. Les amorces sont groupées par `emplacement` (champ du schéma `Amorce`) et jointes par une ligne vide.
3. Le gabarit `validation` porte `tache: validation` et ne sert pas à la génération.
4. Les `tool_calls` sont normalisés en `id`, `type`, `function{name, arguments}`.
5. Des `arguments` MCP absents valent `{}`.

**Risques résiduels.**
- Le corps HTTP journalisé diffère de `Generation.messages`, car le SDK ajoute `prefix` et `index`. La re-dérivation de 9.6 doit en tenir compte.
- Les gabarits n'ont pas été éprouvés contre l'API.
- Sans `config/donnees.toml` (story 9.1), le Générateur refuse de démarrer.
