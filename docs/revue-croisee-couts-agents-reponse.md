# Réponse du projet slm à la revue croisée sur le coût des agents

> **Statut** : réponse du 2026-10-13 à `wavelocalai/docs/revue-croisee-couts-agents.md`, rédigée depuis `service-public-slm-fine-tuning`.
> **Méthode** : recalcul sur les transcriptions existantes, sans aucun nouvel agent ni banc payant.
> - **Périmètre** : 312 sous-agents, de 8 sessions, du 2026-10-11 au 2026-10-13, sous `~/.claude/projects/<slm>/<session>/subagents/`. Le coût des orchestrateurs (sessions principales) n'est pas compté.
> - **Coût réel** : somme par réponse dédoublonnée (`message.id`). L'écriture du cache est répartie entre 5 minutes et 1 heure d'après `usage.cache_creation`, aux prix du § 7 de wavelocalai. La sortie est réestimée selon W12 quand c'est indiqué.
> - **Expiration** : une écriture de plus de 20 k tokens après une pause de plus de 5 minutes depuis la réponse précédente (définition de S4).
> - **Contrefactuels** :
>   - un agent réellement en TTL de 5 minutes est recalculé en 1 heure : ses écritures après expiration deviennent des lectures, et toutes les écritures sont payées 2 fois l'entrée ;
>   - un agent réellement en TTL d'une heure est recalculé en 5 minutes : le préfixe lu après une pause de plus de 5 minutes devient une écriture.
>
>   L'estimation est grossière, comme chez wavelocalai.
> - **Niveaux de preuve** : ceux du guide, à savoir mesuré, convergent, observé et documenté. « Un essai » signifie une tâche par case.

## 0. Trois corrections préalables au § 1 du document

1. **Le coût d'une story dans slm n'est pas de 4,10 $.**
   - Ce chiffre correspond à une story de correctifs de revue (10.1), et non à une story complète.
   - Le run de nuit du 2026-10-12 est **le même mode A que wavelocalai** : 34 agents de story, tous sur Opus, invoquent `bmad-build-auto`, qui lance un implémenteur et 4 relecteurs, avec 25 agents de profondeur 3.
   - Coût réel d'une story, descendants compris : **médiane de 12,56 $**, quartiles de 10,52 à 17,66 $, extrêmes de 1,69 et 51,13 $.
   - L'écart avec wavelocalai (médiane de 20 $) est donc d'un **facteur 1,6, et non de 5**.
2. **Le pic de contexte n'est pas d'environ 190 k.** Dans le run de nuit, le pic par story a une médiane de 267 k et un maximum de 488 k. Le chiffre de 190 k venait de la story 10.1, qui était courte.
3. **Les coûts des bancs publiés dans le guide de slm sont sous-estimés de 22 à 35 %.**
   - Les agents des bancs tournaient déjà avec un TTL d'une heure.
   - Or `outils/cout_sous_agents.py` applique un seul facteur d'écriture, 1,25 par défaut, et ne lit pas `usage.cache_creation`.
   - Exemple de la spec sur Opus : 2,77 $ publiés, contre **3,47 $** au coût réel et 3,71 $ avec W12.
   - Le classement des modèles ne change pas (voir W12).

## 1. Grille de réponse

| Constat | Verdict (confirmé, nuancé, contredit, non mesurable) | Tes chiffres | Niveau de preuve et nombre d'essais | Trait du projet qui explique l'écart |
|---|---|---|---|---|
| W1 relecture du contexte | **Confirmé** | Sur 312 agents (661 $ avec W12) : écriture du cache 43 %, lecture du cache 39 %, sortie 18 %, entrée 0 %. Sur Sonnet seul (20 $) : 38 / 47 / 14 %. | Mesuré sur 312 agents ; convergent sur les 3 projets | Aucun écart notable. La part de sortie est un peu plus haute (18 % contre 9 %), à cause de la correction W12 et des stories qui rédigent des items d'évaluation. |
| W2 agent intermédiaire | **Confirmé, presque au point près** | Run de nuit en mode A, 34 stories, 510 $ : **agents de story 37 %** (186 $). Enfants directs : implémenteurs 32 % (162 $), relecteurs 15 % (74 $), autres 11 % (55 $ : intentions, compilation, vérifications). Petits-enfants : 6 % (32 $). Après la fin de l'imbrication : une seule story, la 9.4, à 6,30 $ (dev-story Opus en effort high, transverse, 89 appels). | Mesuré sur 34 stories ; convergent avec wavelocalai (39 %). L'effet de la suppression n'est qu'observé, sur un essai et une story différente. | Même structure d'orchestration. Aucune paire avant / après sur une même story, donc la baisse due à la fin de l'imbrication n'est pas isolable. |
| W3 contexte × appels | **Nuancé** : la relation est confirmée, mais l'appel compte plus que le pic | Coût d'une story contre la somme de (pic × appels) de ses agents : **r = 0,978** ; contre les appels seuls : r = 0,978 ; contre le pic seul : r = 0,871. Médiane de **0,31 $ par M de pic × appels** sur Opus. Médianes par story : pic de 267 k, 195 appels. | Mesuré sur 34 stories, un seul run | Le facteur 5 venait d'une mauvaise base de comparaison (§ 0). À structure égale, l'écart restant (×1,6) vient du pic (267 k contre 300 à 500 k), et c'est le nombre d'appels qui explique la variance. |
| W4 cache d'une heure | **Confirmé, et seuil précisé** | 281 agents en 5 minutes : 567 $ réels contre 614 $ en 1 heure (+8 %). Écart selon le nombre d'expirations : **0 → +31 %** (219 agents), **1 → −3 %** (55), **2 → −17 %** (5), **3 ou plus → −30 %** (2). 27 agents en 1 heure : 37,2 $ réels contre 32,2 $ en 5 minutes (+15 %), avec seulement 3 pauses de plus de 5 minutes en tout. Story 9.4 : 6,30 $ contre 5,46 $ (+15 %), sans aucune pause. | Mesuré par contrefactuel sur 312 agents | Les expirations viennent surtout des agents intermédiaires qui attendent leurs enfants (1,06 en moyenne, contre 0,17 pour les feuilles). Sans imbrication, avec une suite de moins de 5 minutes, il n'y en a presque plus, et le TTL d'une heure ne fait que coûter. |
| W5 effort en implémentation | **Non mesurable directement**, mais cohérent | Aucun banc ne fait varier l'effort. En revanche, **toutes les variantes du banc slm portent `"effort":"high"`** dans leurs transcriptions, héritage du réglage de session (`effortLevel: high` pour Opus 5.5). Le « Sonnet équivalent à Opus » de slm était donc **Sonnet en high**, ce qui va dans le sens de W5 (Sonnet en high : 9 sur 10). | Observé dans les transcriptions (15 agents de banc) ; non vérifié que Sonnet applique cette valeur | Effort hérité, non fixé par le banc. Conséquence : l'agent `dev-story` réglé en **medium** est une extrapolation non mesurée. |
| W6 Opus low contre Sonnet high | **Non mesurable** | Aucune variante en low | Aucun essai | |
| W7 revue et défauts liés au réel | **Nuancé** | Commit 793bd33 (10.1, environnement d'entraînement sur GPU, 3 450 lignes). Pas de vérité terrain établie après coup : les 5 défauts connus venaient d'une revue antérieure. **Opus 5/5, Sonnet 5/5, Haiku 4/5** (oubli de `uv --frozen`). Les défauts liés au matériel réel (seuil de débordement de la VRAM sous WDDM, adaptateur LoRA réutilisé) ont été trouvés par les trois. Haiku a apporté **la preuve tirée d'un vrai run GPU** (pertes de 14,90 puis 11,94). Coûts réels : 0,04, 0,66 et 0,91 $. | Mesuré sur un essai, contre une vérité antérieure et non postérieure | Les artefacts du vrai run (sonde, pertes) étaient dans le worktree. Le réel était donc **observable dans le dépôt**, alors que chez wavelocalai le comportement d'Ollama ne l'était pas. Les défauts différés W4.1 à W4.7 de 10.1 serviront de vérité terrain postérieure à la story 10.4. |
| W8 Opus en conception | **Confirmé pour Opus ; divergence expliquée pour Sonnet** | Spec : Haiku 6,2, Sonnet 8,0, Opus 8,4. Architecture : 7,0, 7,5, 8,5. Recherche web : 6,4, 7,8, 8,4. Coûts réels avec le TTL d'une heure : spec 0,08, 2,27 et 3,47 $ ; architecture 0,06, 0,79 et 1,51 $ ; recherche 0,02, 0,69 et 0,88 $. | Mesuré sur un essai par case, juge Opus en aveugle ; convergent pour Opus | Sonnet tournait en **effort high**, ce qui peut expliquer son avance sur Haiku. La spec 9.4 est transverse, avec des règles de couches vérifiées par un test d'architecture que Haiku a violées. |
| W9 nombre de tours | **Nuancé** : vrai sur les tâches longues seulement | Appels Haiku / Sonnet / Opus. Implémentation W2 : 41 / 33 / **57**. Spec : 29 / 27 / **44**. Architecture : 29 / 16 / 19. Recherche web : 12 / 23 / 21. Revue : 11 / 9 / 8. | Mesuré sur un essai par case | Sur les tâches courtes, comme la revue ou la recherche, Opus ne fait pas plus de tours ; Sonnet en fait même plus en recherche web. L'écart vient alors du prix unitaire de l'écriture. |
| W10 variance de Haiku | **Non mesurable** (un essai), nuancé entre tâches | Implémentation : correcte mais minimale. Revue : la plus précise. Spec : 6,2, avec couches violées. Recherche : 6,4, avec des erreurs factuelles. | Observé, un essai par tâche | La variance mesurée ici est **entre tâches** et non entre essais. Haiku est fort en lecture et faible en conception, dans les deux projets. |
| W11 contexte fixe | **Confirmé** | Premier appel : 37 à 40 k pour `general-purpose` (11 au 13 octobre), **32 k pour `dev-story`** après redémarrage (skills claude.ai masqués, 6 MCP désactivés), 30 k pour `claude-code-guide`, 24 k pour `Explore`. Gain sur la 9.4 : environ 6 k × 89 appels, soit 0,53 M de lectures, environ 0,11 $ sur 6,30 $ (**1,7 %**). | Mesuré sur le premier appel ; attribution non isolable | Trois changements simultanés : type d'agent (prompt système propre), skills et MCP. Il faudrait le même agent avant et après pour attribuer le gain. |
| W12 sortie sous-comptée | **Confirmé, ampleur nuancée** | Rapport médian par agent entre sortie comptée et sortie estimée : 0,42 (11 octobre), 0,60 (12 octobre), 0,53 (13 octobre) ; global 0,63. Par réponse, la médiane tombe à 0,03, car la plupart des réponses courtes ne gardent que l'usage du début. Effet sur la facture : **+44,7 $ sur 616 $ (+7 %)**. Bancs : l'écart entre Sonnet et Opus passe de −55 à −58 % en implémentation, de −25 à −29 % en revue, de −33 à −36 % en spec, de −45 à −46 % en architecture et de −17 à −23 % en recherche web. | Mesuré sur 312 agents | Le classement ne change pas. Les tâches de rédaction (spec, architecture, recherche) sont les plus touchées, avec des rapports de 0,24 à 0,54. |

## 2. Réponses aux questions adressées à slm (§ 5)

1. **Implémentation.**
   - La tâche W2 (réglages de décodage en config et indicateur de troncature, 11 fichiers, environ 270 lignes) **ne dépendait d'aucun comportement réel non simulé** : `llama-server` y est simulé.
   - La version fusionnée (Opus, ccccf7e) ajoute environ 125 lignes à `tests/evaluation/test_generation.py`. Les tests ajoutés par Sonnet n'ont pas été comptés séparément.
   - La qualité a été jugée par l'orchestrateur sur le diff et la suite de tests, **sans juge en aveugle**.
   - Surtout, les trois variantes tournaient en **effort high** (voir W5).
2. **Revue.**
   - Le commit ne contient pas de défaut confirmé après coup à ce jour. La vérité utilisée était antérieure : 5 points d'une revue Blind Hunter de la nuit.
   - Résultat : Opus 5/5, Sonnet 5/5, Haiku 4/5.
   - Constats propres à chaque modèle :
     - Opus seul : `router_aux_loss_coef`, la détection Mamba, l'écriture tardive de `sonde.json`, et le débordement dès la première longueur ;
     - Sonnet seul : la conversion en fp32, la graine LoRA, et les gradients d'Unsloth délégués au CPU ;
     - Haiku seul : `use_dora` jamais posé, la réutilisation de l'adaptateur prouvée par les pertes du run, et `prepare_model` hors du `try`.
   - Ces constats sont consignés en W4.1 à W4.7 de `deferred-work.md`. Ils seront confirmés ou infirmés pendant la story 10.4, qui fournira la vérité postérieure.
3. **Spec.** Sonnet tournait en **effort high** (trace `"effort":"high"` dans sa transcription), et non en medium.
4. **Recalcul gratuit.**
   - **Pic de contexte et appels par story** (run de nuit) : médiane de 267 k et de 195 appels, descendants compris. Agent de story seul : de 34 à 175 appels, et un pic de 124 à 488 k.
   - **Expirations** : 1,06 en moyenne par agent intermédiaire, 0,17 par agent feuille. Dans l'organisation actuelle (dev-story sans imbrication), 3 pauses de plus de 5 minutes sur 31 agents, et aucune sur la 9.4.
   - **Contrefactuel du cache** : voir W4.
   - **Le cache d'une heure** apparaît dans les transcriptions le 2026-10-13 vers 07 h 30, heure locale, en cours de session. 4 agents sont mixtes. Le réglage a été versionné à 08 h 40 (commit 4be79bd).
   - **Effet sur le coût par story** : une seule story depuis, la 9.4, à **+15 %** sans aucune expiration évitée. Le réglage coûte donc ici sans rien rapporter.
5. **Sortie sous-comptée** : voir W12. Les écarts entre Sonnet et Opus s'élargissent de 1 à 6 points, sans changer le classement.

## 3. Critique de la proposition de système adaptatif (§ 4)

### Signaux que slm aurait mal classés
- **S2, dépendance au réel non simulé.**
  - slm serait classé « élevé » : GPU de 8 Go, `llama-server`, vrais runs d'entraînement. La table enverrait donc la revue sur Opus.
  - Pourtant, Sonnet et même Haiku ont trouvé les défauts liés au matériel, parce que les artefacts du vrai run étaient dans le dépôt.
  - Proposition : remplacer S2 par « **réel non observable depuis le dépôt** », c'est-à-dire un comportement qui ne laisse ni log, ni artefact, ni sonde lisible par le relecteur.
- **S1, criticité.**
  - La règle bloquante de slm (D1 : aucune donnée d'entraînement générée par Claude) ne relève d'aucune des catégories proposées : mesure, argent, sécurité ou données personnelles.
  - Ajouter « **intégrité ou provenance des données** » : contamination, fuite entre jeux d'entraînement et d'évaluation, licences.
- **S3, pic de contexte.**
  - Le seuil de 250 k pour découper une story aurait déclenché sur plus de la moitié des stories de slm (médiane de 267 k).
  - Or la variance du coût vient surtout du nombre d'appels : r = 0,978, contre 0,871 pour le pic.
  - Mieux vaut suivre **la somme de (pic × appels)**, ou simplement le nombre d'appels.
- **S4, expirations.**
  - Ce n'est pas un trait du projet, mais un effet de S5 (l'imbrication) et du rôle de l'agent.
  - Dans slm, il est passé d'environ 1 par agent intermédiaire à presque 0 avec la fin de l'imbrication.
  - Il faut le mesurer **par rôle**, et le **remesurer après chaque changement de S5**.

### Seuils que nos données permettent de fixer
- **TTL du cache des sous-agents.**
  - Seuil de rentabilité du TTL d'une heure : **1 expiration par agent** (−3 %). C'est franchement rentable à partir de 2 (−17 %) et coûteux à 0 (+31 %).
  - Règle proposée : TTL d'une heure seulement pour les agents qui attendent (intermédiaires, suite de tests de plus de 5 minutes). Sinon, garder 5 minutes.
  - **Pour slm aujourd'hui, `subagentPromptCacheTtl: "1h"` est à retirer** : +15 % sur la 9.4.
- **Modèle de coût d'une story** : environ **0,31 $ par M de (pic × appels)** sur Opus (r = 0,98, 34 stories).
- **Budget d'une story** en mode A sur Opus : médiane de 12,6 $, troisième quartile de 17,7 $. Au-delà de 18 $, regarder S3 et S5 avant le modèle.
- **Agent intermédiaire** : de 37 à 39 % du coût, dans deux projets. C'est le gain maximal à attendre de la fin de l'imbrication, avant le surcoût des relectures faites en double par l'orchestrateur.

### Ce qui manque pour publier
1. **Corriger `cout_sous_agents.py`** :
   - lire `usage.cache_creation` pour séparer les écritures à 5 minutes de celles à 1 heure, au lieu d'appliquer un TTL unique ;
   - ajouter le correctif de W12 ;
   - ajouter les colonnes pic, appels et expirations.

   Republier ensuite les coûts des bancs du guide, sous-estimés de 22 à 35 %.
2. **Compter l'orchestrateur** : les sessions principales ne figurent dans aucun des chiffres ci-dessus.
3. **Fixer l'effort explicitement dans chaque banc**, au lieu de le laisser hériter de la session. Le banc slm compare des variantes en high sans le dire.
4. **Mesurer l'effort de Sonnet, medium contre high, sur une tâche de slm.** L'agent `dev-story` est réglé en medium sans mesure.
   - Coût estimé : environ 3 $ pour 2 variantes sur 1 tâche.
   - Il faut l'accord d'Anaël.
5. **Une paire avant / après la fin de l'imbrication sur une story comparable**, pour isoler l'effet de S5.
6. **Une vérité terrain postérieure pour la revue** : les points W4.1 à W4.7, à vérifier pendant la 10.4.
7. **Trois essais par case** pour W5, W6, W7 et W10, comme le demande le § 8.
