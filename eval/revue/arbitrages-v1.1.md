# Arbitrages pour le Jeu d'évaluation v1.1

- **Objet** : trancher les points laissés ouverts par la construction du jeu v1.0 (stories 7.2 à 7.6) et par la revue de code du lot 2. Chaque décision devient une correction de la v1.1, gelée ensuite avec `slmsp eval gel --statut relu`.
- **Mode d'emploi** : cocher une option par point. La recommandation est en tête et marquée ✅. Ajouter une remarque si besoin. Les points A à F demandent ton avis. Le point G et la section H sont des corrections par défaut : ne cocher « refusé » que si tu n'es pas d'accord.
- **Préparé le** : 2026-10-13, à partir de `eval/jeu/v1.0/items.jsonl`, du calibrage (`eval/calibrage/echantillon-calibrage.jsonl`) et de l'Index local `index/20260926`.
- **Hors échantillon** : la plupart des items ci-dessous ne figurent pas dans les 47 items de `echantillon-revue-v1.0-lecture.md`. Seul CR-023 y est.

---

## A. Q-042 : le plafond de l'indemnité de rupture conventionnelle est faux

**Constat.** L'item fixe le plafond à **1/24e** de la rémunération brute annuelle par année d'ancienneté, ce qui donne 36 000 € / 24 × 12 = **18 000 €**. Le décret dit **un douzième** :

> « Le montant maximum de l'indemnité […] ne peut pas excéder une somme équivalente à un douzième de la rémunération brute annuelle perçue par l'agent par année d'ancienneté, dans la limite de vingt-quatre ans d'ancienneté. » Décret n° 2019-1596 du 31 décembre 2019, article 3 ([Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000039728021/)), lu le 2026-10-13.

Le bon plafond est donc 36 000 € / 12 × 12 = **36 000 €**. La fiche F31094 de l'Index local (révision MediaTech `29f236f8a5`) écrit pourtant « au 24 e » : l'erreur vient de la fiche, que l'item a recopiée. Le dilemme est le suivant. Un modèle fidèle à l'Index répondra 18 000 € et sera noté juste. Un modèle qui répond 36 000 € sera noté faux, alors qu'il a raison en droit.

**Options**
- [x] **1. ✅ Retirer le montant de l'item.** On garde la question sur le calendrier (entretien, signature, rétractation, cessation) et le remboursement, et l'on supprime la demande de plafond dans l'entrée et dans `elements_cles`. L'item ne mesure plus qu'une chose : la fidélité à la fiche.
- [ ] **2. Corriger selon le décret.** Plafond 1/12e, soit 36 000 €, avec le décret ajouté dans `sources_attendues`. Le Juge devra alors pénaliser une réponse fidèle à la fiche de l'Index : l'item mesurerait une connaissance que le modèle ne peut pas tirer de ses sources.
- [ ] **3. Remplacer l'item** par une autre question du domaine travail-emploi.
- Remarque :

---

## B. Items trop proches du calibrage (SPEC §1.1)

Le calibrage (16 items) a servi à mettre au point la grille et le Juge. Un item du jeu qui lui ressemble trop affaiblit l'indépendance de la mesure. Les quatre constats sont mineurs.

| Item | Ressemblance avec le calibrage | Recommandation |
|---|---|---|
| **Q-045** | Accusé de réception d'une demande envoyée par courriel (fiche F33312). LC-002 du calibrage porte sur l'article L. 112-3 du CRPA (accusé de réception), mais c'est une autre Tâche (Langage clair), avec un autre texte | ✅ Garder |
| **Q-048** | Sigle inconnu (« NEC ») sans source : même gabarit « absence de source » que Q-002 du calibrage (« PPG ») | ✅ Garder : c'est le comportement attendu (SM-C3), et le sigle diffère |
| **CT-005**, **CT-007** | Même type de courrier (« demande de pièces ») que CT-001 du calibrage. Les situations diffèrent (bourse communale ; aide énergie du CCAS, avec L. 114-5 du CRPA) | ✅ Garder les deux |
| **CR-023** | Une action reprend CR-001 du calibrage : « Envoyer le sondage pour fixer la date du prochain COPIL » (1 action sur 10, générique) | ✅ Garder |

- [x] **1. ✅ Garder les cinq items tels quels.**
- [ ] **2. Remplacer** (préciser les items) : …
- Remarque :

---

## C. Paires Langage clair × Question qui portent sur la même fiche

**Constat.** Dans ces paires, l'entrée de l'item LC contient la réponse de l'item Q :

| LC | Q | Fiche commune |
|---|---|---|
| LC-008 | Q-031 (taxe foncière en indivision) | F263 |
| LC-006 | Q-044 (siège d'association en mairie) | F1174 |
| LC-011 | Q-016 (ASH en Ehpad) | F2444 |
| LC-002 (Apa, F11678) | Q-016 | même thème : Apa et ASH |

Il n'y a pas de fuite entre items, puisque chaque item est évalué seul. Le risque est double : deux items mesurent le même contenu, et le jeu en devient moins varié.

- [x] **1. ✅ Garder.** L'effet est faible sur 225 items, et les Tâches mesurées diffèrent : réécriture d'un côté, recherche et réponse de l'autre.
- [ ] **2. Remplacer les LC concernés** par des textes d'autres fiches. Il faut alors refaire leur vérification et leur Kandel-Moles.
- Remarque :

Le même raisonnement vaut pour **LC-002 et RE-010**, qui portent tous deux sur l'Apa : ✅ garder, sauf avis contraire.

---

## D. Courrier type : CT-016 et les libellés imposés

**D1. CT-016 (accusé de réception d'une demande de dossier médical).** Le centre hospitalier public relève aussi du CRPA, dont l'article R. 112-5 fixe les mentions de l'accusé de réception (date de réception, délai, silence, voies de recours). L'item ne les exige pas, car la consigne impose de s'appuyer « uniquement sur l'extrait de la fiche fourni » (F12210).
- [x] **1. ✅ Garder.** La consigne est explicite. Des mentions CRPA exactes ne sont pas des inventions : préciser dans `pieges` qu'elles ne sont pas pénalisées.
- [ ] **2. Exiger les mentions CRPA.** Il faut alors ajouter l'extrait du CRPA dans l'entrée.
- Remarque :

**D2. Libellés d'emplacement listés dans la consigne (tous les CT).** La consigne donne la liste exacte des emplacements, par exemple `[Référence du dossier]`, ce qui rend la Tâche plus facile.
- [x] **1. ✅ Garder.** Le contrôle automatique « aucune valeur inventée » a besoin de libellés exacts. On le documente comme une limite du score CT.
- [ ] **2. Retirer les listes.** Le contrôle des emplacements passe alors au Juge, et le coût du Juge augmente.
- Remarque :

---

## E. Couverture : aucun item sur les marchés publics

**Constat.** SPEC §2 cite les marchés publics dans le thème « collectivités ». Les fiches sont sur `entreprendre.service-public.gouv.fr`, hôte que la story 7.2 excluait des `sources_attendues`. Or l'Index local `20260926` contient bien ces fiches (9 333 chunks `entreprendre`), et l'hôte figure dans la Liste blanche. Rien ne bloque donc techniquement.

- [x] **1. ✅ Ajouter 3 items Question sur les marchés publics** (seuils de procédure, publicité, délais), tirés de fiches `entreprendre`, avec cet hôte permis dans `sources_attendues`. Ils remplacent 3 Q d'un thème surreprésenté, pour garder la composition de 60 Q.
- [ ] **2. Ajouter les 3 items en plus** (63 Q). La composition s'écarte alors de SPEC §2, ce qui est acceptable en `relu` seulement si SPEC §2 est mise à jour.
- [ ] **3. Garder l'écart** et le documenter comme une limite.
- Remarque :

---

## F. Compte rendu : aucune transcription d'au moins 6 000 mots (FR-13)

**Constat.** FR-13 exige qu'une entrée d'au moins 6 000 mots soit acceptée, avec découpage et fusion au-delà du contexte du Modèle embarqué. La plus longue transcription du jeu, CR-006, compte 5 480 mots. La SPEC (5 transcriptions de plus de 4 000 mots) est respectée, mais le cas limite de FR-13 n'est jamais évalué.

- [x] **1. ✅ Allonger 2 transcriptions existantes** (les plus longues, CR-006 et CR-021) au-delà de 6 500 mots, en ajoutant des échanges sans nouvelle décision ni action, puis revérifier leurs références.
- [ ] **2. Créer 2 nouveaux items CR** de plus de 6 500 mots, à la place de 2 items courts.
- [ ] **3. Laisser FR-13 à un test technique** (story 4.4, découpage et fusion), hors jeu.
- Remarque :

---

## G. Corrections par défaut (à refuser seulement en cas de désaccord)

**G1. RD, colonnes vérifiées (report W3, issu de la décision D1 du lot 2).** Colonnes proposées pour `valeurs_attendues.colonnes`, en ne gardant que ce que la question demande :

| Item | Question (résumé) | Colonnes vérifiées |
|---|---|---|
| RD-010 | Nombre de bailleurs et de logements sociaux de l'Essonne | `Nbre_bailleurs`, `Nbre_logements` |
| RD-017 | CNI payantes délivrées à Caen, janvier à mars 2020 | `Nombre` |
| RD-023 | Note Index égalité du SIREN 479766842, 2018 à 2020 | `Année`, `Note Index` |
| RD-030 | Code région et chef-lieu d'un département (COG 2026) | `REG`, `CHEFLIEU` |
| RD-039 | IPS du collège 0010005A, rentrée 2022 | `Effectifs`, `IPS` |

- [ ] Refusé (préciser) :

**G2. RD, fragments de contrôle trop larges.** La correspondance se fait en début de mot, mais certains fragments restent trop courts. Correction proposée :
  - RD-017 : retirer « cni », qui laisse passer « CNIL », et garder « identité », « passeport » et « carte nationale ».
  - RD-031 : remplacer « rei » par « REI » en mot entier, et retirer « recensement », trop général.
  - RD-019 : retirer « répertoire » seul, et garder « répertoire opérationnel », « rome » et « métier ».
- [ ] Refusé :

**G3. Ancre de date.** Les montants et dates du jeu suivent le droit au 2026-10-12. Correction proposée : inscrire `date_reference: 2026-10-12` dans le manifeste et la rappeler dans la grille du Juge (« la référence fait foi à cette date »), sans modifier les entrées.
- [ ] Refusé :

**G4. Métadonnées.**
  - Harmoniser `consulte_le` et `licence_source`, qui sont hétérogènes.
  - Passer les CO à `fictif: true` : ce sont des textes réels dans lesquels des fautes ont été injectées, donc modifiés.
- [ ] Refusé :

---

## H. Pour information (aucune décision demandée)

- **Items « sans réponse »** : leur absence de source n'est prouvée que sur l'Index `20260926`. Il faudra les revérifier à chaque nouvel Index.
- **Verdicts** : ils ne sont pas liés au contenu de l'item par une empreinte. C'est un choix de la spec 5.6, rejeté en revue de code (lot 2, n° 11). Le cache des verdicts, lui, est indexé sur le contenu de chaque item et de la sortie (`judge/cache.py:119`), pas sur le manifeste. Un item inchangé en v1.1, avec une sortie identique, réutilise donc son verdict sans nouvel appel au Juge.
- **Kappa entre juges quasi nul** (0 à 0,21) : il ne se règle pas par cette relecture. Un diagnostic séparé comparera, critère par critère, les verdicts des deux juges sur les 34 items de l'échantillon.

---

## Ajustements validés (2026-10-13)

En préparant la construction, quatre décisions ont été précisées. Anaël les a validées :

1. **E. Marchés publics.** Aucun thème n'est surreprésenté : les 60 Q suivent exactement les parts de SPEC §2. Les 3 items sur les marchés publics remplacent donc 3 items « collectivités » : Q-044 (facile), Q-046 (moyen) et Q-050 (difficile). Les nouveaux items sont Q-061 à Q-063, aux mêmes difficultés. Aucun des trois items remplacés n'est un « sans réponse » ni dans un échantillon. Le remplacement de Q-044 retire aussi la paire Q-044/LC-006 du point C.
2. **G4. Métadonnées.** Seuls les CO passent à `fictif: true`. `consulte_le` et `licence_source` restent tels quels, et leur hétérogénéité est documentée. En les modifiant, on changerait presque tous les items, donc toute la clé du cache des verdicts, et il faudrait rejuger la Baseline (environ 6 €, pour 3,94 € restants).
3. **D1. CT-016.** L'item reste inchangé : le schéma CT n'a pas de champ `pieges`. La tolérance aux mentions exactes du CRPA est documentée dans les limites du jeu.
4. **G3. Ancre de date.** Un champ `date_reference` est ajouté à `ManifesteJeu` et à `slmsp eval gel`, avec ses tests. La grille du Juge n'est pas modifiée, car elle est figée par le manifeste v1.0.

**Ordre de travail.** Construire les brouillons v1.1, puis faire la double vérification indépendante des items modifiés ou nouveaux, assembler et lancer `gel --verifier-seulement`. Exporter ensuite les items modifiés pour la relecture d'Anaël, et seulement après, faire le gel `--statut relu`. Relancer enfin la Baseline réduite sur la v1.1 : seuls les items modifiés repassent au Juge.

## Validation

- [x] J'ai tranché les points A à G. La v1.1 peut être construite puis gelée avec `--statut relu`.
- Date et nom : 2026-10-13, Anaël (toutes les recommandations retenues)
