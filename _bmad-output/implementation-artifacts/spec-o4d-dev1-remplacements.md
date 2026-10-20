---
title: 'O4d — correction des items de dev1 rejetés par la revérification croisée'
type: 'bugfix'
created: '2026-10-20'
status: 'review'
context: ['{project-root}/_bmad-output/implementation-artifacts/spec-o4-jeu-dev.md', '{project-root}/_bmad-output/implementation-artifacts/spec-o4c-dev1-suite.md']
warnings: []
deferred: []
---

## Intent

**Problème :** la revérification croisée de dev1 (DeepSeek V4 Pro, GLM-5.3, consigne 3) a retenu 123 items et en a rejeté 37 : CR 8, NR 8, RE 6, Q 5, CT 3, RD 3, CO 2, LC 2. Le gel `relu-llm` exige 20 items par Tâche, chacun retenu par les deux juges sur son `item_sha256` courant.

**Approche :** lire les griefs des deux juges, puis corriger chaque item (`version_item` + 1, verdict de construction O4d dans `verification/`) ou le remplacer. Pour CR et NR, chercher d'abord une cause commune. Ensuite réassembler, contrôler la composition et la disjonction. Aucun appel payant : l'orchestrateur relance la revérification.

## Boundaries & Constraints

**Always :** même schéma et même procédé qu'O4b. Les faits d'une référence restent tirés de la source citée. Les extraits complétés sont relus dans les chunks.

**Never :** donnée d'entraînement (D1), modification de v1.0 ou v1.1, plaidoyer adressé aux juges, que ce soit par une note dans l'item ou par `contestations.jsonl`.

## Livré

Les 37 items rejetés changent d'empreinte, aucun n'est remplacé ; 31 sont corrigés, 6 CR attendent une décision (voir Revue). Composition, difficultés et quotas de `CIBLES_DEV` sont inchangés. Les 123 items retenus gardent leur empreinte.

- **CR, cause commune (6 rejets sur 8 : CR-501, 502, 503, 506, 508, 512) :** la consigne demande les « points abordés », qu'aucune clé du schéma CR ne porte ; seul le critère Structure de la grille (rapporté) contrôle la section. La consigne d'origine est conservée sur les 20 CR (revue : comparabilité avec v1.1). Ces 6 items passent en `version_item` 2 sans autre changement : décision de l'orchestrateur. CR-518 : la décision « prochain comité le vendredi 2 avril 2027 » entre dans `decisions_reference`, et les pièges visent les dates remplacées en séance (8 décembre, 26 mars). CR-511 : décision « prochaine réunion en février » ajoutée, action de M. Ba reprise au plus près de la transcription.
- **NR, cause commune :** la consigne ou les critères laissaient la forme ouverte, et la référence passait pour l'unique réponse. Les cas : ordre des lignes (NR-517), format des puces (NR-512), démarche de calcul imposée (NR-502), notation de l'heure et forme de la réponse (NR-503), titres sans contrainte de contenu (NR-516), critères aux libellés différents de la référence (NR-520), courriel sans interdiction d'ajouts (NR-511). Chaque contrainte est désormais écrite dans la consigne ou dans les critères. NR-505 : la référence reprend le libellé de la fiche, « grande médaille d'or ».
- **Q :** Q-503 et Q-511, extraits complétés : « médecin agréé par le procureur de la République », chunk 5 de F2120 ; poursuite du contrat si l'employeur accepte, chunk 1 de F131. Q-515 : le rôle de l'amorce dit qu'elle est restreinte au mandat local, le seul que traite la fiche (l'amorce reste verbatim). Q-519 : « construction ou aménagement sans autorisation », comme la fiche. Q-520 : l'orientation est ramenée au service des impôts indiqué sur l'avis de taxe foncière, que mentionne l'entrée.
- **CO :** CO-514, « pré-demande » remplace « prédemande » dans l'entrée et dans la référence, positions recalculées. CO-516 : la licence décrit l'origine de chaque texte (référence F642, entrée fautive créée pour l'évaluation) ; `fictif` reste vrai (arbitrage G4).
- **CT :** l'expéditeur est ajouté aux `elements_connus` (CT-507, CT-511, CT-519). CT-507 : la formule d'appel admet « Mesdames, Messieurs, ».
- **LC :** LC-504, la pause est due « soit immédiatement après 6 heures, soit avant ». LC-507 : l'exemple de la piscine dépend de l'impossibilité de la déplacer.
- **RD :** RD-501 et RD-519, la provenance cite l'extrait de la cassette. RD-519 : l'URL « fiscalite-locale-des-entreprises » est celle de la cassette, et les critères situent la variante « Géo ». RD-505 : `filter_operator = contains` devient obligatoire, car sans lui le filtre exact ne trouve pas la ligne. Aucune cassette n'est réenregistrée.
- **RE :** RE-501, le point 4 ne garde que la durée de la sauvegarde de justice : la cellule « tutelle » du tableau est vide. RE-510 : « en ligne » pour une naturalisation, cerfa si la demande était sur papier. RE-515 : CCAS et association agréée sont rattachés aux étrangers, comme dans le document. RE-519 : le point 2 est réduit aux 4 étapes, pour 80 mots. RE-502 : la consigne nomme les sujets attendus. RE-520 : le public devient « collège ou lycée ».
- Contrôles :
  - `construire_jeu.py assembler --version dev1` : 160 items, SHA-256 `1f78dfd7…`, 0 exclu.
  - `slmsp eval gel --version dev1 --verifier-seulement` : 0 erreur, 0 écart.
  - Disjonction des items du worktree contre les données du dépôt principal (v1.0, v1.1, `data/train/v*` dont v17 et v18, amorces seed) : 0 conflit.
  - `tests/eval_outils/test_items_dev1.py` contre les instantanés réels (`SLMSP_EVAL_SOURCES`) : 97 tests passés.

## Auto Run Result

Statut : review. Tests ciblés `tests/eval_outils` et `tests/evaluation` : 1097 passés, 300 ignorés.

Revérification (orchestrateur, payante) : `python eval/outils/verifier_jeu_croise.py verifier --version dev1 --juges deepseek,glm`. Seuls les 37 items à empreinte nouvelle sont rappelés, soit 74 appels : environ 0,4 $, 0,8 $ au pire avec une relance par appel. Suivent `python eval/outils/construire_jeu.py assembler --version dev1`, puis `slmsp eval gel --version dev1 --statut relu-llm --graine <g>`.

Décisions :
- Corriger plutôt que remplacer : chaque grief était corrigeable sans changer la source. Aucun nouvel identifiant, aucune nouvelle cassette.
- Consigne CR d'origine conservée sur les 20 CR (revue O4d, point 6) ; les 12 CR retenus reprennent leur contenu et leur empreinte d'avant O4d.

Reports : si la revérification rejette encore un item, le remplacer par un nouvel item tiré d'une source réelle (identifiants 521 et suivants). Grief « points abordés » (CR-501, 502, 503, 506, 508, 512) : à trancher par l'orchestrateur, soit une précision de format dans la consigne du juge (« CR : les points abordés ne sont contrôlés que comme section présente », `VERSION_PROMPT` 4, revérification des 160 items, environ 1,7 $), soit une relance des 6 items en l'état.

## Revue

Revue O4d (second avis Haiku puis reviewer), détail dans `revue-o4d.md` :
- high · corrigé · CO-516 : justification de `fictif` retirée de la licence et de la note ; la licence décrit l'origine de chaque texte, `fictif` reste vrai (arbitrage G4, comme les 6 CO de même procédé retenus).
- high · corrigé · CR-518 : pièges réécrits sur les dates remplacées (26 mars, 8 décembre) ; le 2 avril reste une décision.
- medium · corrigé · CR-511 : décision « prochaine réunion en février » ajoutée, action de M. Ba au plus près de la transcription.
- medium · corrigé autrement · Q-520 : l'orientation reste exigée (grille, critère « Cas sans réponse » ; quota de 3 Q sans réponse, sans marge) ; elle vise le service de l'avis cité par l'entrée, sans plaidoyer.
- medium · corrigé · RD-519 : parenthèse retirée ; URL vérifiée dans la cassette `RD-519/s1.json`.
- medium · corrigé · consigne CR : consigne d'origine rétablie sur les 20 CR ; 12 retenus restaurés à l'identique (empreinte retenue reprise). Grief des 6 CR « points abordés » non traitable dans l'item sans clé nouvelle ni plaidoyer : décision de l'orchestrateur.
- low · corrigé · NR-503 : critères de langue et de calcul rétablis, sans exiger phrase complète ni détail du calcul (grief DeepSeek).

