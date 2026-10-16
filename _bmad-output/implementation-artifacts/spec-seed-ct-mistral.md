---
title: 'Étape seed : amorces CT par Mistral (A2b) et longueurs RE de configuration'
type: 'feature'
created: '2026-10-16'
status: review
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/consignes-sous-agents-nuit.md'
  - '{project-root}/_bmad-output/implementation-artifacts/spec-9-3-etape-seed-amorces-publiques-ou-mistral-exclusion-anti-fuite.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** Les gabarits CT et RE ont des emplacements sans source publique (`CT/type_courrier`, `CT/objet`, `CT/elements_connus`, `RE/longueur_demandee`) : `generate` planifie 0 session CT et 0 session RE, d'où un déficit égal à la cible.

**Approach:** (A2b) `seed` fait produire les amorces CT par Mistral, une réponse JSON par sujet public, découpée en trois amorces `mistral` du même appel. La longueur RE devient un paramètre de `config/donnees.toml` (`[seed].re_longueurs_mots`), tiré par graine pour chaque texte RE, sous une provenance `config` sans contenu.

## Boundaries & Constraints

**Always:**
- D1.1 : le méta-prompt `config/prompts/generateur/amorces-ct.md` ne décrit que la forme attendue (aucun exemple, aucune valeur) et passe `valider_gabarit`. Les fixtures sont des chaînes factices (`<objet-factice-1>`).
- Appel via `Generateur` et `ClientMistral` (poste `mistral.generation`, réservation avant l'appel, journal). La session `seed-ct-<sha>` est stable d'un run à l'autre : une réponse déjà journalisée est réutilisée sans nouvel appel (`Generateur.reponse_journalisee`).
- Chaque courrier passe le schéma (trois clés chaînes non vides, bornées), la déduplication (objet normalisé) et l'anti-fuite (`Protection.motifs` sur chaque valeur) ; un rejet écarte les trois amorces.
- Traçabilité : `auteur_contenu = "mistral"` et `appel_id` sur chaque amorce CT (le Registre l'impute à `mistral/reponses-generateur`, `genere_par = "mistral"`). Le Générateur et `build` acceptent une amorce Mistral égale au contenu entier ou à la valeur de la clé `emplacement` de son objet JSON (`texte_mistral_conforme`).

**Never:** aucun appel d'API dans les tests ; Mistral seulement si `--courriers > 0` et le gel v1.1 est commité ; aucune valeur d'amorce dans le code, la config ou les tests.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Nominal CT | `--courriers N`, fabrique factice JSON | 3 amorces `ct.<champ>.<suffixe du sujet>` par appel, même `appel_id` | — |
| JSON invalide | non-JSON, liste, clé absente, valeur courte ou non chaîne | aucune amorce, `schema_invalide` +1 | — |
| Clôture de code | contenu entre trois accents graves | admis (même découpe au Générateur et à `build`) | — |
| Doublon | objet normalisé déjà vu | `doublons` +1 | — |
| Fuite | une valeur recoupe le Jeu d'évaluation | courrier écarté, motif compté | — |
| Budget | `BudgetEpuise` pendant les appels | run `partiel-budget`, amorces écrites conservées, code 3 | — |
| Reprise | même sujet, nouveau run | même `session_id`, réponse journalisée réutilisée | — |
| Sans gel | `--courriers > 0`, v1.1 non commité | aucun run, code 4 | `ManifesteInvalide` |
| RE | texte RE conservé | amorce `config` `<n> mots`, `lie_a` = texte, `n` dans la liste | `ProvenanceInvalide` si `lie_a` absent |

</intent-contract>

## Code Map

- `src/slmsp/core/schemas/amorce.py` -- provenance `config` (`lie_a`, emplacements `EMPLACEMENTS_CONFIG`, forme `<n> mots`), `texte_de_reponse`, `texte_mistral_conforme`.
- `src/slmsp/data/seed.py` -- règle `service-public/title -> CT/sujet`, `_courriers`, `_longueurs_re`, `session_courrier`, comptes `courriers` et `longueurs_re`.
- `src/slmsp/mistral/generateur.py` -- vérification JSON des amorces Mistral, `lie_a` présent dans l'appel, `reponse_journalisee`.
- `src/slmsp/data/generate.py` -- `_origine` : une amorce `config` rejoint le groupe de son amorce liée.
- `src/slmsp/data/build.py` -- accepte `config` (aucune source au Registre) et la découpe JSON.
- `src/slmsp/data/config.py`, `config/donnees.toml` -- table `[seed]` (`re_longueurs_mots = [80, 150, 250]`, `graine = 42`).
- `src/slmsp/cli/data.py` -- `seed --courriers {N,auto}` (auto = volume CT x facteur), fabrique avec reprise par le journal.
- `config/prompts/generateur/amorces-ct.md` -- méta-prompt.

## Méta-prompt (`amorces-ct`, version 1, tâche CT, max_tokens 800)

> Tu prépares la demande qu'un Agent du service public adresserait à un assistant pour faire rédiger un courrier administratif. La demande porte sur une situation plausible en lien avec le sujet de démarche indiqué ci-dessous. Tu ne rédiges pas le courrier lui-même.
>
> - type_courrier : la nature du courrier, en quelques mots.
> - objet : l'objet du courrier, en une phrase courte.
> - elements_connus : les faits que l'Agent connaît déjà, en deux à six phrases ou lignes. Ils doivent suffire à rédiger le courrier sans le compléter entièrement : certaines informations peuvent manquer.
> - Varie la nature du courrier, le destinataire et la situation d'une demande à l'autre.
> - Tous les noms de personnes, d'organismes locaux, d'adresses, de dates et de références sont manifestement fictifs. N'utilise aucune donnée personnelle réelle.
> - Écris en français, dans un registre administratif.
> - Réponds par un seul objet JSON, sans texte avant ni après et sans bloc de code. Il contient exactement les trois clés type_courrier, objet et elements_connus, dont chaque valeur est une chaîne de caractères non vide.
>
> Sujet de démarche.
>
> {sujet}

## Campagne 9.8 : séquence des commandes

À lancer depuis le dépôt principal, sur `main` à jour, le jour même :

1. Relecture des conditions Mistral (critère 1), puis report de la date et du SHA dans `config/donnees.toml` (`conditions_verifiees_le`, `conditions_sha256`) et au journal ; si la page est inaccessible, arrêt et blocage consigné :
   `uv run python -c "import hashlib, datetime; from slmsp.net.client import client; r = client('outillage').get('https://legal.mistral.ai/terms/commercial-terms-of-service'); r.raise_for_status(); print(datetime.date.today().isoformat(), hashlib.sha256(r.content).hexdigest())"`
2. `uv run slmsp budget etat` (relevé de départ).
3. `uv run slmsp data seed --courriers auto` (ajouter `--scenarios N` si la chaîne CR le demande) : noter `SEED_RUN_ID`. Code 3 : relancer la même commande, les courriers déjà journalisés sont réutilisés sans dépense.
4. `uv run slmsp data generate --depuis SEED_RUN_ID` : noter `GEN_RUN_ID` (reprise : `--reprendre GEN_RUN_ID`).
5. `uv run slmsp data validate --depuis GEN_RUN_ID` (`--controle-mistral` en option, payant) : noter `VAL_RUN_ID`.
6. `uv run slmsp data filter --depuis VAL_RUN_ID` : noter `FIL_RUN_ID`.
7. `uv run slmsp data build --depuis FIL_RUN_ID --variante diffusable`.
8. `uv run slmsp budget etat` (dépense `mistral.generation` sous 25 €).

## Coût estimé (tarif prudent `mistral-large-latest` : 2 $/Mtok en entrée, 6 $/Mtok en sortie)

- Amorces CT, `--courriers auto` = 35 x 3 = 105 appels, environ 450 tokens en entrée et 250 en sortie par appel : environ 0,25 $. Réservation maximale (800 tokens de sortie) : environ 0,60 $.
- Campagne entière (environ 600 sessions, plus la transcription CR et les tours RD) : de 8 à 12 $ à vue de nez, sous le plafond de 25 €. À remesurer après les 50 premières sessions (`budget etat`).

## À confirmer par Anaël

1. Les deux extensions de schéma : provenance d'amorce `config` (avec `lie_a`), et amorce Mistral égale à une clé de l'objet JSON de la réponse. Le Registre des licences n'est pas modifié.
2. Les longueurs RE `[80, 150, 250]` mots et la graine 42.
3. Les sujets CT tirés des titres `service-public` (règle `CT/sujet`), qui ancrent et diversifient les demandes.
4. Volume `auto` = volume CT x facteur (105 appels) : la marge couvre les rejets de schéma, de doublon et d'anti-fuite, puis ceux des étapes suivantes.
5. Pas de mode JSON forcé (`response_format`) : le gabarit n'accepte que `max_tokens`. Un écart de format se compte en `schema_invalide`. À ajouter si ce taux dépasse 10 %.
6. La déduplication se fait sur l'objet normalisé seul.

## Verification

- `uv run pytest -q --tb=short tests/data/test_seed.py tests/cli/test_data.py tests/mistral` -- tous passent.
- `uv run --no-sync python outils/controle_rapide.py`, `uv run ruff check`, `uv run ruff format --check` -- aucune erreur.

## Auto Run Result

**Statut :** review (2026-10-16). Décisions prises seul (« la plus simple et la plus réversible ») : les points 1 à 6 ci-dessus. Touché hors de `seed` : `core/schemas/amorce.py`, `mistral/generateur.py`, `data/generate.py`, `data/build.py` (acceptation des deux nouvelles formes d'amorce).
