# Diagnostic D0 (lecture seule, 0 appel d'API, 0 génération)

Runs dev1 utilisés (juge GLM, un seul juge, graine 42, max_tokens 1024, contexte 8192) :
- Baseline `base:minicpm5-2b` : génération `20261020-163743-minicpm5-2b-f9fc`, notation `20261020-165745-minicpm5-2b-afd3`.
- v18 (export `20261020-132636-ft-minicpm5-2b-3479`) : génération `20261020-175424-ft-minicpm5-2b-35b9`, notation `20261020-181808-ft-minicpm5-2b-213f`.
Scripts : `a1.py`, `a3.py` (a), `b1.py`, `b6.py` (b), `c2.py`, `c3.py`, `c5.py` (c), dans le même dossier.
Le seul calcul hors fichiers existants est l'embedding local bge-m3 (llama-server CPU, 0 €) pour rejouer la recherche des 20 items Q ; la reproduction est exacte (59/59 sources citées de la trace identiques à mes passages).

## (a) Pertes CR et RE par critère

Formules (scores.json) : CR = moyenne(couverture, sans_invention) ; RE = moyenne(couverture, fideles). La structure CR n'entre que dans les rapportés.

| | Baseline | v18 | écart |
|---|---|---|---|
| CR couverture | 84,0 | 70,3 | -13,7 |
| CR sans_invention | 66,7 (12/18) | 10,5 (2/19) | -56,1 |
| CR score | 75,3 | 40,4 | -34,9 |
| RE couverture | 52,1 | 66,5 | +14,4 |
| RE fideles (absence d'invention) | 65,0 (13/20) | 15,0 (3/20) | -50,0 |
| RE score | 58,5 | 40,7 | -17,8 |

Constat : l'invention explique l'essentiel. CR : -28,1 de -34,9 pts viennent de sans_invention (80 %), -6,9 de la couverture. RE : l'invention coûte -25,0 pts et la couverture en rend +7,2 (v18 couvre MIEUX que la base : 11 items meilleurs, 5 pires, 4 égaux). Structure CR : 17/18 contre 17/19, sans effet (les 2 zéros de v18, CR-517 et CR-518, sont des sorties tronquées).

Item par item (paires jugées : CR 18, RE 20) :
- CR : verdict invention base 1 -> v18 0 sur 10 items ; 0 -> 0 sur 6 ; 1 -> 1 sur 2 ; jamais l'inverse. Inventions signalées par item : 0,72 (base) contre 2,39 (v18). Couverture moyenne 0,840 -> 0,742 (10 items pires, 2 meilleurs, 6 égaux) ; hors sorties tronquées 0,909 -> 0,850. Les 3 sorties v18 tronquées (CR-515, CR-517, CR-518 ; base 4 : CR-515, 516, 519 et 517 non jugé) valent 0/20, 0/13 et 0/21 éléments.
- RE : mêmes transitions (10 items 1 -> 0, 7 stables 0, 3 stables 1) ; inventions par item 0,60 -> 2,05.

Exemples (verdicts GLM) :
- CR-503 : v18 attribue au chef d'équipe une formation qui concerne Mme Lacroix ; présente une simple correction de date comme décision. Base : 0 invention, 7/7 éléments.
- CR-507 : « Direction générale des services publics » (les notes disent DGS) ; action « La DGS donne son avis sur l'élargissement du télétravail » alors que rien n'est décidé (piège du jeu). Base : 0 invention.
- CR-501 : décision D3 déformée (« et dans le bureau du service » alors que les notes disent « plus dans le bureau ») ; action inventée pour M. Fontaine, absent. CR-513 : 8 inventions. Au moins 4 items CR contiennent un piège du jeu (rectificatif, correction) traité comme décision ou action : 7 inventions de ce type au total.
- RE-501 : durée de la tutelle « renouvelable 1 an » (c'est la sauvegarde de justice, la tutelle est de 5 ans max) ; RE-502 : « le squatteur peut demander l'évacuation » ; RE-515 : C2S « gratuite pour RSA, ASI, AAH, Aspa » (contredit le document) et « frais de dossier » inexistants ; RE-514 : « CFE déclarée dans les 6 mois » (absent du document).
Catégories des 3 types d'invention (CR+RE, v18, mots-clés, approximatif) : actions/décisions inventées ou rectificatifs promus (~19), déformations ou attributions erronées (~11), ajouts non vérifiables (~56 dont « autre »).

Lecture : v18 a appris de la cible Mistral un style plus riche (sections, attributions, précisions) que le juge compte comme inventions ; la couverture n'est pas le problème. Comme les verdicts viennent du même juge GLM, strict sur tout ajout, la perte est réelle au sens de la grille.

## (b) Troncatures CT de v18

- 13/20 CT terminent en `raison=longueur` (1024 tokens exactement), 7/20 en `terminee` (EOS présent). Baseline : 20/20 `terminee`, 137 à 348 tokens (519 à 1 320 caractères). Les autres tâches v18 : CR 3/19, NR 2/20, RD 1/20 tronquées ; base : CR 4/19 seulement.
- Ce n'est pas un problème de plafond : les cibles CT de `data/train/v18/train.jsonl` (30 items) font 282 à 482 tokens (médiane 409 ; 1 017 à 1 769 caractères), la base finit à 137-348. max_tokens=1024 est 2 à 3 fois la cible. Les 13 sorties tronquées sont des boucles : proportion de 4-grammes répétés 0,85 à 0,97 (base 0,00 à 0,06), 48 à 129 lignes, une même ligne d'emplacement répétée 12 à 125 fois.
- La boucle démarre dans le bloc d'en-tête : première ligne répétée à la ligne 4 à 9 ; aucune des 13 n'atteint « Madame, Monsieur, » ni le corps du courrier. Exemples : CT-501 (« **[Référence du dossier]** » x15, 77 lignes, 3 079 caractères), CT-506 (« [Référence du dossier] » x125), CT-508 (« [Élèves et élèves] » x110), CT-510 (« **[Référence]** » x121). Seules les 7 sorties terminées ont un corps (6 sur 7 ; CT-507 boucle brièvement, x5, puis s'arrête).
- Cause probable : décalage entre le prompt d'évaluation et celui d'entraînement. 20/20 consignes CT du jeu dev1 imposent des libellés (3 à 7, par exemple « avec exactement ces libellés : [Adresse du café], [Commune], [Date du courrier], [Référence du dossier]... ») ; 0/30 prompts CT de v18 contiennent cette consigne, et les cibles Mistral emploient leurs propres libellés (`[Références]`, `[Signature]`, `[Expéditeur]`, `[Destinataire]`, `[Lieu et date]`...), en gras (29/30), tous avec « Objet ». Le modèle ajusté empile les libellés imposés dans le style du bloc d'en-tête appris, et en décodage glouton (température 0, sans pénalité de répétition) la liste boucle. La base, qui n'a pas ce style, pose les libellés puis rédige.
- Impact mesuré nul sur le score : CT = 45,0 pour les deux (emplacements 90, conformité 0/20 pour les DEUX modèles, car le critère exige tous les éléments obligatoires : en-tête, destinataire, objet, date de réception, formule d'appel ; même la base est à 0). La mesure CT est donc saturée à 0 en conformité et ne détecte pas la régression ; le défaut est réel en usage.

## (c) Q : les passages fournis contiennent-ils les éléments clés ?

Méthode : rejeu de la recherche (bge-m3 q8 CPU, `RechercheIndex` k=5, seuil 0,5, requête = champ `entree` de l'item, comme le harnais) ; couverture lexicale d'un élément clé = au moins 75 % de ses mots pleins présents dans le texte des passages (proxy prudent : un élément reformulé ou chiffré autrement sous-compte). Les 3 items `sans_reponse` (Q-506, Q-514, Q-520) sont traités à part.

Items à réponse (17) :
- Page attendue dans les 5 passages : 15/17 (manquantes : Q-510, rang 6 ; Q-515, rang 15). En top-20 : 16/17.
- Éléments clés présents dans les 5 passages : 49/69 (71 %) ; dans la page attendue entière (tous ses chunks) : 59/69 (86 %). Items dont tous les éléments sont dans les passages : 6/17 ; dans la page entière : 10/17.
- Où l'information se perd (par ordre d'importance) :
  1. Nombre de passages / concurrence entre pages : les 5 passages viennent de 1 à 3 pages ; 6 items ont les 5 chunks de la MÊME page (Q-501, Q-502, Q-509, Q-515, Q-516, Q-518) alors que la page attendue a 8 à 20 chunks (Q-501 : 8 chunks, 4 éléments sur 4 couverts ; Q-504 : 10 chunks, 1/4 éléments complets dans les passages contre 3/4 dans la page). Q-507 : 4 passages sur 5 viennent de F21089, le bon (F10619) n'est qu'au rang 4. Passer k de 5 à 8 donne 57/69 éléments et 9/17 items complets, 16/17 pages ; k=10 : 59/69, 10/17 (= la page entière).
  2. Mauvaise page malgré un bon chunk : Q-510 (période d'essai CDI, F1643 absente ; les passages portent sur le particulier employeur F37731 -> le modèle répond « 1 mois »), Q-515 (F32817 au rang 15 ; les passages F2310).
  3. Chunking : chaque chunk reprend le titre et l'introduction de la page (même préfixe de ~200 caractères dans les 8 chunks de F17317, et le champ `extrait` des Sources est identique pour les 5) : de l'ordre de 10 à 15 % de contexte répété par chunk, qui occupe les cinq emplacements sans apporter d'information nouvelle. Chunk moyen service-public 1 433 caractères (max 5 012).
  4. Troncature du contexte : non. Prompts de 1 248 à 4 563 tokens (médiane ~1 900) pour un budget de 7 168 (8 192 - 1 024) ; `borner_passages` n'a rien retiré.
- Ce n'est pas qu'une question de passages : sur les 6 items à couverture complète, 1 seul réussit (Q-501) ; Q-507 (v18 oublie 2 éléments sur 5 alors que le passage [4] les portait), Q-517 (v18 : « 30 € » et « 16,10 € » au lieu de 35 € et 24,50 € alors que F10874 est au rang 0), Q-513 et Q-516 (tous les éléments, mais ajouts non vérifiables, note 1 sur 2), Q-519 (note 1). La Baseline a le même profil que v18 : exactitude 0/1/2 = 10/7/3 contre 11/6/3, pertinence de source 14 contre 16 sur 20 : 3 réussites (note 2) chacun. Le plafond Q = 15 % n'est donc pas un effet du fine-tuning.
- Items sans réponse (3/20, 15 % du score) : les 3 sont à 0 pour les deux modèles. Le seuil 0,5 ne déclenche jamais `AUCUN_PASSAGE` : les scores de la hors-corpus (0,55-0,67 : Q-506 registre canicule -> jeu de données `registre-des-personnes-vulnerables-nombre-dinscrits`, Q-514 budget participatif -> jeux de données d'Avignon, Q-520 0,59-0,60) sont dans la même plage que ceux des items à réponse (0,60-0,79). Le modèle invente alors (Q-514 : « 1 500 000 euros (5 % du budget d'investissement) », « à partir de 7 ans »). Q-ceiling : 17/20 = 85 %, hors abstention.

## Leviers (gain attendu / coût)

1. **CR et RE : ne plus entraîner sur les cibles qui inventent** (0 à ~2 €). Faire noter par le juge d'invention (DeepSeek, déjà autorisé) les 64 cibles CR et 34 cibles RE de v18 et écarter celles avec invention (ou, comme prévu en E2/E4, prendre la sortie de la base comme candidate). Gain attendu : l'invention explique ~80 % de la perte CR et plus de 100 % de la perte RE ; récupérer la base sur ces deux critères = +20 à +35 pts CR, +15 à +25 pts RE, soit environ +5 à +6 pts sur la moyenne des 8 tâches (en gardant le gain de couverture RE).
2. **Interpolation de l'adaptateur (E7, échelles 0,25 et 0,5)** (~0,3 € par génération + notation GLM). Un adaptateur dilué garde CO/RD sans les 3 inventions par item ; test direct de l'hypothèse « la perte est du style Mistral » ; le gain dépend du point d'équilibre, mais le coût est quasi nul.
3. **Q : k=8 au lieu de 5, avec dédoublonnage du préfixe titre+introduction des chunks** (0 €, harnais seul). Rejeu : éléments dans les passages 49 -> 57/69, items complets 6 -> 9/17, page 15 -> 16/17 ; coût contexte 2 k -> ~3,3 k tokens (budget 7 168 OK, latence CPU à mesurer). Gain attendu sur Q modeste (+5 à +10 pts), car le goulot est aussi la génération ; à appliquer à tous les modèles pour rester comparable (nouvelle version de harnais).
4. **Q : abstention** (0 € pour la mesure ; données d'entraînement ensuite). 3/20 items valent 15 pts maximum aujourd'hui à 0 chez tous. Le score de recherche ne sépare pas hors-corpus et en-corpus ; il faut une consigne ou des exemples d'abstention (« aucune source ne traite... ») et vérifier que les 95 traces Q de v18 en contiennent. Gain attendu : jusqu'à +15 pts Q, rarement atteint par un modèle de 2 Md.
5. **CT : aligner les prompts d'entraînement sur le prompt d'évaluation et ajouter une protection anti-boucle** (0 €). Mettre dans les prompts CT d'entraînement la consigne « avec exactement ces libellés : [...] » et des cibles qui les emploient ; en décodage, `repeat_penalty` ou arrêt sur ligne répétée (à appliquer aussi à la base). Gain sur le score : nul aujourd'hui (conformité 0/20 pour tous, mesure saturée) ; gain en usage : suppression de 13/20 boucles. À traiter après 1 et 2.
6. **Rendre la mesure CT utile avant de décider** (0 €). La conformité est à 0/20 y compris pour la base : relire le critère et ses justifications (par exemple « 2 éléments obligatoires manquants » comme seuil) et, si la grille est bien celle-là, ne pas utiliser CT pour trancher entre modèles ; le rapporter comme saturé.
