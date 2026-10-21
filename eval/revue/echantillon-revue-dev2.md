# Échantillon de relecture du Jeu d'évaluation dev2

- Statut du gel : `relu-llm`
- Gelé le : 2026-10-21T22:47:07.493979+02:00
- Graine : 42
- Items : 48 sur 160 (20 % stratifié Tâche × difficulté, au moins 1 par strate)

Les scores restent « non relus » tant que la relecture n'est pas validée (FR-25).

## CO-604 — Correction (facile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CO-604",
 "tache": "Correction",
 "difficulte": "facile",
 "theme": "collectivites",
 "entree": {
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "texte": "Lorsque le vide-greniers ou la brocante génère des recettes, elles sont exonérés d'impôts commerciaux (TVA, impôt sur les sociétés et CET) dans la limite de 6 manifestations de bienfaisance ou de soutien par an. En revanche, lorsque l'association à pour objet l'organisation de brocantes ou de vide-greniers, elle est exonérée d'impôts commerciaux si les 3 conditions suivantes sont réunies :\n- La majorité de ces activités est non lucrative\n- Sa gestion et désintéressée\n- Le montant des recettes générées par l'une des activités accessoires ne doit pas dépasser 78 596 € sur une année civile.\nExemple:\n- Un comité des fêtes, dont l'objet est de promouvoir la vie du village et d'organiser le vide-greniers annuel, doit respecté le seuil de 78 596 € pour être exonéré d'impôts commerciaux.\n- Une association, dont l'objet est de protéger les animaux abandonné, organise un vide-greniers pour financer ses activités. Elle est exonérée de TVA sur les bénéfices du vide-greniers quel que soit le montant collecté, si l'association ne réalise pas plus de 6 manifestations par an.",
  "nb_mots": 166
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F1813 « Vide-greniers ou brocante organisés par une association » (chunks 7)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1813",
   "type": "service-public",
   "doc_id": "F1813",
   "chunks": [
    7
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1",
   "note": "texte réel, ponctuation et espaces normalisés ; fautes injectées pour l'évaluation"
  }
 ],
 "licence_source": "Texte de référence : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face), ponctuation et espaces normalisés. Fautes injectées : création originale du projet (évaluation)",
 "fictif": true,
 "version_item": 1,
 "fautes": [
  {
   "debut": 72,
   "fin": 80,
   "erreur": "exonérés",
   "correction": "exonérées",
   "type": "accord du participe passé",
   "contexte_fautif": "elles sont exonérés"
  },
  {
   "debut": 246,
   "fin": 249,
   "erreur": " à ",
   "correction": " a ",
   "type": "homophone grammatical (a / à)",
   "contexte_fautif": "lorsque l'association à pour objet"
  },
  {
   "debut": 410,
   "fin": 413,
   "erreur": "ces",
   "correction": "ses",
   "type": "homophone grammatical (ses / ces)",
   "contexte_fautif": "La majorité de ces activités"
  },
  {
   "debut": 454,
   "fin": 458,
   "erreur": " et ",
   "correction": " est ",
   "type": "homophone grammatical (et / est)",
   "contexte_fautif": "Sa gestion et désintéressée"
  },
  {
   "debut": 721,
   "fin": 729,
   "erreur": "respecté",
   "correction": "respecter",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "doit respecté le seuil"
  },
  {
   "debut": 851,
   "fin": 860,
   "erreur": "abandonné",
   "correction": "abandonnés",
   "type": "accord de l'adjectif",
   "contexte_fautif": "les animaux abandonné"
  }
 ],
 "texte_corrige_reference": "Lorsque le vide-greniers ou la brocante génère des recettes, elles sont exonérées d'impôts commerciaux (TVA, impôt sur les sociétés et CET) dans la limite de 6 manifestations de bienfaisance ou de soutien par an. En revanche, lorsque l'association a pour objet l'organisation de brocantes ou de vide-greniers, elle est exonérée d'impôts commerciaux si les 3 conditions suivantes sont réunies :\n- La majorité de ses activités est non lucrative\n- Sa gestion est désintéressée\n- Le montant des recettes générées par l'une des activités accessoires ne doit pas dépasser 78 596 € sur une année civile.\nExemple:\n- Un comité des fêtes, dont l'objet est de promouvoir la vie du village et d'organiser le vide-greniers annuel, doit respecter le seuil de 78 596 € pour être exonéré d'impôts commerciaux.\n- Une association, dont l'objet est de protéger les animaux abandonnés, organise un vide-greniers pour financer ses activités. Elle est exonérée de TVA sur les bénéfices du vide-greniers quel que soit le montant collecté, si l'association ne réalise pas plus de 6 manifestations par an.",
 "nb_fautes": 6,
 "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte"
}
```

## CO-605 — Correction (facile, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CO-605",
 "tache": "Correction",
 "difficulte": "facile",
 "theme": "famille-education-sante",
 "entree": {
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "texte": "D'autres documents peuvent aussi être demandé pour la cantine scolaire ou les activités périscolaires. Une fois l'inscription réalisée, la mairie vous délivreras un certificat d'inscription indiquant l'école maternelle ou est affecté votre enfant. Si vous rencontrez des difficultés pour inscrire votre enfant, vous pouvez contacter la direction des services départementaux de l'éducation nationale de votre département. Inscription définitive à l'école: Pour inscrire définitivement votre enfant, vous devez vous présentez à l'école indiquée sur le certificat d'inscription dès que vous l'obtenez. La direction de l'école effectue l'inscription, sur présentation des 2 documents suivants :\n- Certificat d'inscription délivré par la mairie\n- Document attestant que l'enfant a eu les vaccinations obligatoire pour son âge ou justifie d'une contre-indication.\n(À noter: Si l'enfant reste dans la même école durant sa scolarité en maternelle, vous n'aurez pas a renouveler son inscription chaque année.)",
  "nb_mots": 137
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F1866 « École primaire (maternelle ou élémentaire) pour un élève venant de l'étranger » (chunks 3)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1866",
   "type": "service-public",
   "doc_id": "F1866",
   "chunks": [
    3
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1",
   "note": "texte réel, ponctuation et espaces normalisés ; fautes injectées pour l'évaluation"
  }
 ],
 "licence_source": "Texte de référence : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face), ponctuation et espaces normalisés. Fautes injectées : création originale du projet (évaluation)",
 "fictif": true,
 "version_item": 1,
 "fautes": [
  {
   "debut": 38,
   "fin": 45,
   "erreur": "demandé",
   "correction": "demandés",
   "type": "accord du participe passé",
   "contexte_fautif": "peuvent aussi être demandé"
  },
  {
   "debut": 151,
   "fin": 161,
   "erreur": "délivreras",
   "correction": "délivrera",
   "type": "conjugaison",
   "contexte_fautif": "la mairie vous délivreras"
  },
  {
   "debut": 219,
   "fin": 221,
   "erreur": "ou",
   "correction": "où",
   "type": "homophone grammatical (ou / où)",
   "contexte_fautif": "l'école maternelle ou est affecté"
  },
  {
   "debut": 514,
   "fin": 523,
   "erreur": "présentez",
   "correction": "présenter",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "vous devez vous présentez à l'école"
  },
  {
   "debut": 796,
   "fin": 807,
   "erreur": "obligatoire",
   "correction": "obligatoires",
   "type": "accord de l'adjectif",
   "contexte_fautif": "les vaccinations obligatoire pour"
  },
  {
   "debut": 956,
   "fin": 959,
   "erreur": " a ",
   "correction": " à ",
   "type": "homophone grammatical (a / à)",
   "contexte_fautif": "vous n'aurez pas a renouveler"
  }
 ],
 "texte_corrige_reference": "D'autres documents peuvent aussi être demandés pour la cantine scolaire ou les activités périscolaires. Une fois l'inscription réalisée, la mairie vous délivrera un certificat d'inscription indiquant l'école maternelle où est affecté votre enfant. Si vous rencontrez des difficultés pour inscrire votre enfant, vous pouvez contacter la direction des services départementaux de l'éducation nationale de votre département. Inscription définitive à l'école: Pour inscrire définitivement votre enfant, vous devez vous présenter à l'école indiquée sur le certificat d'inscription dès que vous l'obtenez. La direction de l'école effectue l'inscription, sur présentation des 2 documents suivants :\n- Certificat d'inscription délivré par la mairie\n- Document attestant que l'enfant a eu les vaccinations obligatoires pour son âge ou justifie d'une contre-indication.\n(À noter: Si l'enfant reste dans la même école durant sa scolarité en maternelle, vous n'aurez pas à renouveler son inscription chaque année.)",
 "nb_fautes": 6,
 "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte"
}
```

## CO-610 — Correction (moyen, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CO-610",
 "tache": "Correction",
 "difficulte": "moyen",
 "theme": "collectivites",
 "entree": {
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "texte": "Les documents à présenter varie selon la taille de la commune dans lequel vous votez :\nCas Commune de 1 000 habitants et plus: Pour voter, vous devez présenté :\n- Soit une pièce d'identité et votre carte électorale\n- Soit une pièce d'identité seulemment.\n(Attention: Si vous avez été inscrit sur décision du juge (après un refus d'inscription ou une radiation à tort), vous devez fournir la preuve de cette décision.)\nCas Commune de moins de 1 000 habitants: Pour voter, il n'ait pas obligatoire de présenter une pièce d'identité. Mais, en cas de doutte sur votre identité, le président du bureau de vote peux vous demander de prouver votre identité par tout moyen. (Attention: Si vous avez été inscrit sur décision du juge (après un refus d'inscription ou une radiation à tort), vous devez fournir la preuve de cette décision.)\n(Rappel: Pour voter, vous devez vous rendre au bureau de vote indiquer sur votre carte électorale.)",
  "nb_mots": 154
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F16828 « Élections politiques : déroulement du scrutin » (chunks 5)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F16828",
   "type": "service-public",
   "doc_id": "F16828",
   "chunks": [
    5
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1",
   "note": "texte réel, ponctuation et espaces normalisés ; fautes injectées pour l'évaluation"
  }
 ],
 "licence_source": "Texte de référence : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face), ponctuation et espaces normalisés. Fautes injectées : création originale du projet (évaluation)",
 "fictif": true,
 "version_item": 1,
 "fautes": [
  {
   "debut": 26,
   "fin": 31,
   "erreur": "varie",
   "correction": "varient",
   "type": "accord sujet-verbe",
   "contexte_fautif": "présenter varie selon"
  },
  {
   "debut": 67,
   "fin": 73,
   "erreur": "lequel",
   "correction": "laquelle",
   "type": "accord du pronom relatif",
   "contexte_fautif": "dans lequel vous votez"
  },
  {
   "debut": 150,
   "fin": 158,
   "erreur": "présenté",
   "correction": "présenter",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "vous devez présenté :\n- Soit une pièce d'identité et"
  },
  {
   "debut": 243,
   "fin": 253,
   "erreur": "seulemment",
   "correction": "seulement",
   "type": "orthographe d'usage",
   "contexte_fautif": "pièce d'identité seulemment"
  },
  {
   "debut": 474,
   "fin": 479,
   "erreur": "n'ait",
   "correction": "n'est",
   "type": "conjugaison",
   "contexte_fautif": "il n'ait pas obligatoire"
  },
  {
   "debut": 547,
   "fin": 553,
   "erreur": "doutte",
   "correction": "doute",
   "type": "orthographe d'usage",
   "contexte_fautif": "en cas de doutte sur"
  },
  {
   "debut": 605,
   "fin": 609,
   "erreur": "peux",
   "correction": "peut",
   "type": "conjugaison",
   "contexte_fautif": "peux vous demander de prouver"
  },
  {
   "debut": 891,
   "fin": 899,
   "erreur": "indiquer",
   "correction": "indiqué",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "bureau de vote indiquer sur"
  }
 ],
 "texte_corrige_reference": "Les documents à présenter varient selon la taille de la commune dans laquelle vous votez :\nCas Commune de 1 000 habitants et plus: Pour voter, vous devez présenter :\n- Soit une pièce d'identité et votre carte électorale\n- Soit une pièce d'identité seulement.\n(Attention: Si vous avez été inscrit sur décision du juge (après un refus d'inscription ou une radiation à tort), vous devez fournir la preuve de cette décision.)\nCas Commune de moins de 1 000 habitants: Pour voter, il n'est pas obligatoire de présenter une pièce d'identité. Mais, en cas de doute sur votre identité, le président du bureau de vote peut vous demander de prouver votre identité par tout moyen. (Attention: Si vous avez été inscrit sur décision du juge (après un refus d'inscription ou une radiation à tort), vous devez fournir la preuve de cette décision.)\n(Rappel: Pour voter, vous devez vous rendre au bureau de vote indiqué sur votre carte électorale.)",
 "nb_fautes": 8,
 "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte"
}
```

## CO-612 — Correction (moyen, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CO-612",
 "tache": "Correction",
 "difficulte": "moyen",
 "theme": "etat-civil-papiers",
 "entree": {
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "texte": "Les informations vous concernant dépend de votre situation :\nCas Couple hétérosexuel: Les informations vous concernant sont renseignés si les 2 conditions suivantes sont réunies :\n- Vous apparaissez dans l'acte de naissance de votre enfant\n- Votre acte de naissance est enregistré auprès d'un officier d'état civil français.\nSi ce n'est pas le cas, la page du livret qui vous concerne ne sera pas renseigné.\nCas Couple de femmes: Les informations vous concernant sont renseignées si les 3 conditions suivantes sont réuni :\n- Vous avez effectuée une reconnaissance conjointe anticipée\n- Vous apparaissez dans l'acte de naissance de votre enfant\n- Votre acte de naissance est enregistré auprès d'un officier d'état civil français.\nCas Parent seul: La filiation d’un enfant peut être établi à l’égard d’un parent (la mère ou le père) :\nCas Mère: Le livret de famille contient uniquemment l’extrait d’acte de naissance de la mère et l’extrait d’acte de naissance de l’enfant. La rubrique concernant l’autre parent n’est pas complété.\nCas Père: Le livret de famille contient uniquement l’extrait d’acte de naissance du père et l’extrait d’acte de naissance de l’enfant. La rubrique concernant l’autre parent n’est pas complétée.",
  "nb_mots": 185
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F11991 « Livret de famille : délivrance à la naissance du premier enfant » (chunks 3)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F11991",
   "type": "service-public",
   "doc_id": "F11991",
   "chunks": [
    3
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1",
   "note": "texte réel, ponctuation et espaces normalisés ; fautes injectées pour l'évaluation"
  }
 ],
 "licence_source": "Texte de référence : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face), ponctuation et espaces normalisés. Fautes injectées : création originale du projet (évaluation)",
 "fictif": true,
 "version_item": 1,
 "fautes": [
  {
   "debut": 33,
   "fin": 39,
   "erreur": "dépend",
   "correction": "dépendent",
   "type": "accord sujet-verbe",
   "contexte_fautif": "vous concernant dépend de"
  },
  {
   "debut": 124,
   "fin": 134,
   "erreur": "renseignés",
   "correction": "renseignées",
   "type": "accord du participe passé",
   "contexte_fautif": "sont renseignés si les 2"
  },
  {
   "debut": 397,
   "fin": 406,
   "erreur": "renseigné",
   "correction": "renseignée",
   "type": "accord du participe passé",
   "contexte_fautif": "ne sera pas renseigné"
  },
  {
   "debut": 515,
   "fin": 520,
   "erreur": "réuni",
   "correction": "réunies",
   "type": "accord du participe passé",
   "contexte_fautif": "les 3 conditions suivantes sont réuni"
  },
  {
   "debut": 535,
   "fin": 544,
   "erreur": "effectuée",
   "correction": "effectué",
   "type": "accord du participe passé",
   "contexte_fautif": "Vous avez effectuée une reconnaissance"
  },
  {
   "debut": 781,
   "fin": 787,
   "erreur": "établi",
   "correction": "établie",
   "type": "accord du participe passé",
   "contexte_fautif": "peut être établi"
  },
  {
   "debut": 873,
   "fin": 884,
   "erreur": "uniquemment",
   "correction": "uniquement",
   "type": "orthographe d'usage",
   "contexte_fautif": "contient uniquemment l’extrait d’acte de naissance de la mère"
  },
  {
   "debut": 1020,
   "fin": 1028,
   "erreur": "complété",
   "correction": "complétée",
   "type": "accord du participe passé",
   "contexte_fautif": "n’est pas complété.\nCas Père"
  }
 ],
 "texte_corrige_reference": "Les informations vous concernant dépendent de votre situation :\nCas Couple hétérosexuel: Les informations vous concernant sont renseignées si les 2 conditions suivantes sont réunies :\n- Vous apparaissez dans l'acte de naissance de votre enfant\n- Votre acte de naissance est enregistré auprès d'un officier d'état civil français.\nSi ce n'est pas le cas, la page du livret qui vous concerne ne sera pas renseignée.\nCas Couple de femmes: Les informations vous concernant sont renseignées si les 3 conditions suivantes sont réunies :\n- Vous avez effectué une reconnaissance conjointe anticipée\n- Vous apparaissez dans l'acte de naissance de votre enfant\n- Votre acte de naissance est enregistré auprès d'un officier d'état civil français.\nCas Parent seul: La filiation d’un enfant peut être établie à l’égard d’un parent (la mère ou le père) :\nCas Mère: Le livret de famille contient uniquement l’extrait d’acte de naissance de la mère et l’extrait d’acte de naissance de l’enfant. La rubrique concernant l’autre parent n’est pas complétée.\nCas Père: Le livret de famille contient uniquement l’extrait d’acte de naissance du père et l’extrait d’acte de naissance de l’enfant. La rubrique concernant l’autre parent n’est pas complétée.",
 "nb_fautes": 8,
 "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte"
}
```

## CO-615 — Correction (difficile, thème `travail-emploi`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CO-615",
 "tache": "Correction",
 "difficulte": "difficile",
 "theme": "travail-emploi",
 "entree": {
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "texte": "Oui, un salarié peut être licencier durant son arrêt maladie si son absence perturbent le fonctionnement de l’entreprise. Il y à perturbation du fonctionnement de l'entreprise si les 2 conditions cumulative suivantes sont réunies :\n- Absence prolongée ou absences répétés du salarié entraînent une désorganization\n- Obligation pour l'employeur de remplacé le salarié définitivemant par une embauche en CDI.\nUne convention collective ou un accord d'entreprise peuvent prévoire une garantie d'emploi interdisant le licenciement pour un motif liée à la maladie (pendant 3, 6 ou 12 mois par exemple). L'absence prolongée ou les absences répétées ne doivent pas être lié à un manquement de l'employeur à son obligation de sécurité (par exemple, absences liées a un harcèlement moral, surcharge de travail).",
  "nb_mots": 119
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F133 « Licenciement d'un salarié en arrêt maladie dans le secteur privé » (chunks 2)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F133",
   "type": "service-public",
   "doc_id": "F133",
   "chunks": [
    2
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1",
   "note": "texte réel, ponctuation et espaces normalisés ; fautes injectées pour l'évaluation"
  }
 ],
 "licence_source": "Texte de référence : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face), ponctuation et espaces normalisés. Fautes injectées : création originale du projet (évaluation)",
 "fictif": true,
 "version_item": 1,
 "fautes": [
  {
   "debut": 26,
   "fin": 35,
   "erreur": "licencier",
   "correction": "licencié",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "peut être licencier durant"
  },
  {
   "debut": 76,
   "fin": 86,
   "erreur": "perturbent",
   "correction": "perturbe",
   "type": "accord sujet-verbe",
   "contexte_fautif": "son absence perturbent le"
  },
  {
   "debut": 126,
   "fin": 129,
   "erreur": " à ",
   "correction": " a ",
   "type": "homophone grammatical (a / à)",
   "contexte_fautif": "Il y à perturbation"
  },
  {
   "debut": 196,
   "fin": 206,
   "erreur": "cumulative",
   "correction": "cumulatives",
   "type": "accord de l'adjectif",
   "contexte_fautif": "conditions cumulative suivantes"
  },
  {
   "debut": 264,
   "fin": 271,
   "erreur": "répétés",
   "correction": "répétées",
   "type": "accord de l'adjectif",
   "contexte_fautif": "ou absences répétés du salarié"
  },
  {
   "debut": 298,
   "fin": 313,
   "erreur": "désorganization",
   "correction": "désorganisation",
   "type": "orthographe d'usage",
   "contexte_fautif": "une désorganization"
  },
  {
   "debut": 347,
   "fin": 355,
   "erreur": "remplacé",
   "correction": "remplacer",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "de remplacé le salarié"
  },
  {
   "debut": 367,
   "fin": 381,
   "erreur": "définitivemant",
   "correction": "définitivement",
   "type": "orthographe d'usage",
   "contexte_fautif": "définitivemant par une embauche"
  },
  {
   "debut": 467,
   "fin": 475,
   "erreur": "prévoire",
   "correction": "prévoir",
   "type": "orthographe d'usage",
   "contexte_fautif": "peuvent prévoire une garantie"
  },
  {
   "debut": 540,
   "fin": 544,
   "erreur": "liée",
   "correction": "lié",
   "type": "accord du participe passé",
   "contexte_fautif": "un motif liée à la maladie"
  },
  {
   "debut": 662,
   "fin": 665,
   "erreur": "lié",
   "correction": "liées",
   "type": "accord du participe passé",
   "contexte_fautif": "ne doivent pas être lié à un manquement"
  },
  {
   "debut": 754,
   "fin": 757,
   "erreur": " a ",
   "correction": " à ",
   "type": "homophone grammatical (a / à)",
   "contexte_fautif": "absences liées a un harcèlement"
  }
 ],
 "texte_corrige_reference": "Oui, un salarié peut être licencié durant son arrêt maladie si son absence perturbe le fonctionnement de l’entreprise. Il y a perturbation du fonctionnement de l'entreprise si les 2 conditions cumulatives suivantes sont réunies :\n- Absence prolongée ou absences répétées du salarié entraînent une désorganisation\n- Obligation pour l'employeur de remplacer le salarié définitivement par une embauche en CDI.\nUne convention collective ou un accord d'entreprise peuvent prévoir une garantie d'emploi interdisant le licenciement pour un motif lié à la maladie (pendant 3, 6 ou 12 mois par exemple). L'absence prolongée ou les absences répétées ne doivent pas être liées à un manquement de l'employeur à son obligation de sécurité (par exemple, absences liées à un harcèlement moral, surcharge de travail).",
 "nb_fautes": 12,
 "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte"
}
```

## CO-617 — Correction (difficile, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CO-617",
 "tache": "Correction",
 "difficulte": "difficile",
 "theme": "famille-education-sante",
 "entree": {
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "texte": "Lors de la prise en charge, vous êtes informer par le professionnel que celui-ci disposent des diplômes adéquat pour exercé son activité. Cette information peut être aussi communiqué par :\n- Les établissements de santé\n- Les services de santé\n- Ou toute autre personne morale, autre que l’État, exercant des activités de prévention, de diagnostic ou de soins.\nSes professionnels ou personnes vous informent aussi du respect de leurs obligation de s'assurer contre toute responsabilité civile ou administrative. (À noter: Lors de toute hospitalisation dans un établissement de santé, vous pouvez désigné une personne de confiance. Cette personne peut être un parent, un proche ou le médecin traitant. Cette désignation est fait par écrit et cosigné par la personne désignée. Elle et valable sans limitation de durée. Cependant, vous et la personne de confiance pouvez prévoir une durée. La désignation est révisable et révocable à tout moment.)",
  "nb_mots": 144
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F17180 « Information du patient sur son état de santé » (chunks 3)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F17180",
   "type": "service-public",
   "doc_id": "F17180",
   "chunks": [
    3
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1",
   "note": "texte réel, ponctuation et espaces normalisés ; fautes injectées pour l'évaluation"
  }
 ],
 "licence_source": "Texte de référence : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face), ponctuation et espaces normalisés. Fautes injectées : création originale du projet (évaluation)",
 "fictif": true,
 "version_item": 1,
 "fautes": [
  {
   "debut": 38,
   "fin": 46,
   "erreur": "informer",
   "correction": "informé",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "vous êtes informer par le professionnel"
  },
  {
   "debut": 81,
   "fin": 90,
   "erreur": "disposent",
   "correction": "dispose",
   "type": "accord sujet-verbe",
   "contexte_fautif": "que celui-ci disposent des"
  },
  {
   "debut": 104,
   "fin": 111,
   "erreur": "adéquat",
   "correction": "adéquats",
   "type": "accord de l'adjectif",
   "contexte_fautif": "diplômes adéquat pour"
  },
  {
   "debut": 117,
   "fin": 123,
   "erreur": "exercé",
   "correction": "exercer",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "pour exercé son activité"
  },
  {
   "debut": 172,
   "fin": 182,
   "erreur": "communiqué",
   "correction": "communiquée",
   "type": "accord du participe passé",
   "contexte_fautif": "aussi communiqué par"
  },
  {
   "debut": 295,
   "fin": 303,
   "erreur": "exercant",
   "correction": "exerçant",
   "type": "orthographe d'usage",
   "contexte_fautif": "exercant des activités de prévention"
  },
  {
   "debut": 360,
   "fin": 363,
   "erreur": "Ses",
   "correction": "Ces",
   "type": "homophone grammatical (ces / ses)",
   "contexte_fautif": "Ses professionnels ou personnes"
  },
  {
   "debut": 427,
   "fin": 432,
   "erreur": "leurs",
   "correction": "leur",
   "type": "homophone grammatical (leur / leurs)",
   "contexte_fautif": "du respect de leurs obligation"
  },
  {
   "debut": 595,
   "fin": 602,
   "erreur": "désigné",
   "correction": "désigner",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "vous pouvez désigné une personne"
  },
  {
   "debut": 722,
   "fin": 726,
   "erreur": "fait",
   "correction": "faite",
   "type": "accord du participe passé",
   "contexte_fautif": "Cette désignation est fait par écrit"
  },
  {
   "debut": 740,
   "fin": 747,
   "erreur": "cosigné",
   "correction": "cosignée",
   "type": "accord du participe passé",
   "contexte_fautif": "et cosigné par la personne"
  },
  {
   "debut": 779,
   "fin": 781,
   "erreur": "et",
   "correction": "est",
   "type": "homophone grammatical (et / est)",
   "contexte_fautif": "Elle et valable sans"
  }
 ],
 "texte_corrige_reference": "Lors de la prise en charge, vous êtes informé par le professionnel que celui-ci dispose des diplômes adéquats pour exercer son activité. Cette information peut être aussi communiquée par :\n- Les établissements de santé\n- Les services de santé\n- Ou toute autre personne morale, autre que l’État, exerçant des activités de prévention, de diagnostic ou de soins.\nCes professionnels ou personnes vous informent aussi du respect de leur obligation de s'assurer contre toute responsabilité civile ou administrative. (À noter: Lors de toute hospitalisation dans un établissement de santé, vous pouvez désigner une personne de confiance. Cette personne peut être un parent, un proche ou le médecin traitant. Cette désignation est faite par écrit et cosignée par la personne désignée. Elle est valable sans limitation de durée. Cependant, vous et la personne de confiance pouvez prévoir une durée. La désignation est révisable et révocable à tout moment.)",
 "nb_fautes": 12,
 "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte"
}
```

## CR-601 — Compte rendu (facile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CR-601",
 "tache": "Compte rendu",
 "difficulte": "facile",
 "theme": "collectivites",
 "entree": {
  "consigne": "Rédige le compte rendu de cette réunion de service : participants, points abordés, décisions, actions (responsable, échéance).",
  "notes": "Réunion du service voirie – mardi 3 novembre 2026 – 9 h 30 – atelier municipal, Montval-sur-Orne\nPrésents : M. Lebrun (chef du service voirie, anime), M. Costa et Mme Héraud (agents d'entretien), Mme Pajot (assistante, prend les notes)\nAbsente excusée : Mme Royer (adjointe aux travaux), en formation\n\n1. Nids-de-poule après les pluies\n- 27 signalements reçus depuis le 15 octobre, dont 11 rue des Tanneurs.\n- DÉCISION : la rue des Tanneurs est traitée en priorité, avant les autres voies.\n→ Costa et Héraud rebouchent la rue des Tanneurs d'ici le vendredi 6 novembre.\n- Costa propose d'acheter une seconde plaque vibrante. Lebrun : pas de budget cette année, à revoir en 2027. Rien de décidé.\n\n2. Feuilles mortes\n- Le ramassage passe de 2 à 3 matinées par semaine jusqu'à fin novembre. DÉCISION prise en séance.\n→ Lebrun adapte le planning des agents pour le lundi 9 novembre.\n\n3. Signalements des habitants\n- Beaucoup d'appels arrivent directement à l'atelier. DÉCISION : tous les signalements passent désormais par le formulaire en ligne de la mairie.\n→ Pajot prévient l'accueil et met à jour la fiche d'accueil téléphonique avant le jeudi 12 novembre.\n- Héraud suggère une application mobile de signalement : idée notée, pas d'étude lancée.\n\n4. Divers\n- Le salage des routes commencera « vers le 1er décembre » : correction en fin de réunion, la date retenue en séance (confirmée par M. Lebrun) est le lundi 30 novembre.\nFin 10 h 40.",
  "nb_mots": 224
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Notes fictives rédigées pour l'évaluation (collectivité, personnes et chiffres imaginaires)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "type_reunion": "réunion de service voirie",
 "participants_reference": [
  "M. Lebrun (chef du service voirie, anime)",
  "M. Costa (agent d'entretien)",
  "Mme Héraud (agente d'entretien)",
  "Mme Pajot (assistante, prise de notes)",
  "Absente excusée : Mme Royer (adjointe aux travaux)"
 ],
 "decisions_reference": [
  "La rue des Tanneurs est traitée en priorité pour le rebouchage des nids-de-poule",
  "Le ramassage des feuilles passe à 3 matinées par semaine jusqu'à fin novembre",
  "Tous les signalements des habitants passent par le formulaire en ligne de la mairie"
 ],
 "actions_reference": [
  {
   "action": "Reboucher les nids-de-poule de la rue des Tanneurs",
   "responsable": "M. Costa et Mme Héraud",
   "echeance": "d'ici le vendredi 6 novembre"
  },
  {
   "action": "Adapter le planning des agents pour le ramassage des feuilles",
   "responsable": "M. Lebrun",
   "echeance": "pour le lundi 9 novembre"
  },
  {
   "action": "Prévenir l'accueil et mettre à jour la fiche d'accueil téléphonique",
   "responsable": "Mme Pajot",
   "echeance": "avant le jeudi 12 novembre"
  }
 ],
 "pieges": [
  "Seconde plaque vibrante : proposée par M. Costa, non décidée (à revoir en 2027)",
  "Application mobile de signalement : simple idée, aucune étude lancée",
  "Début du salage : lundi 30 novembre et non « vers le 1er décembre »",
  "Mme Royer était absente"
 ]
}
```

## CR-607 — Compte rendu (facile, thème `travail-emploi`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CR-607",
 "tache": "Compte rendu",
 "difficulte": "facile",
 "theme": "travail-emploi",
 "entree": {
  "consigne": "Rédige le compte rendu de cette réunion du service des ressources humaines : participants, points abordés, décisions, actions (responsable, échéance).",
  "notes": "Service des ressources humaines – réunion de service – lundi 16 novembre 2026 – 10 h – communauté de communes du Val de Sèvre\nPrésents : Mme Pichon (directrice des ressources humaines, anime), M. Rocher (gestionnaire carrière), Mme Diallo (gestionnaire paie), Mme Faure (chargée de formation, notes)\n\n1. Entretiens professionnels annuels\n- 112 agents à évaluer ; 37 entretiens déjà faits.\n- DÉCISION : date limite de retour des comptes rendus d'entretien fixée au vendredi 18 décembre.\n→ Rocher envoie un rappel aux encadrants le lundi 23 novembre.\n\n2. Plan de formation 2027\n- Faure a reçu 64 demandes de formation.\n- DÉCISION : priorité aux formations obligatoires (hygiène et sécurité, habilitations électriques).\n→ Faure présente le projet de plan au comité social territorial du jeudi 10 décembre.\n\n3. Paie de décembre\n- La paie de décembre sera versée le mardi 22 décembre.\n- Diallo demande si la prime de fin d'année peut être versée en novembre : Mme Pichon répond que c'est impossible cette année. Pas de changement.\n\n4. Télétravail\n- M. Rocher propose de passer à 2 jours de télétravail par semaine. Sujet renvoyé à la négociation avec les représentants du personnel en 2027 : rien de décidé.\nFin 11 h 05.",
  "nb_mots": 185
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Notes fictives rédigées pour l'évaluation (collectivité, personnes et chiffres imaginaires)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "type_reunion": "réunion du service des ressources humaines (entretiens professionnels)",
 "participants_reference": [
  "Mme Pichon (directrice des ressources humaines, anime)",
  "M. Rocher (gestionnaire carrière)",
  "Mme Diallo (gestionnaire paie)",
  "Mme Faure (chargée de formation, prise de notes)"
 ],
 "decisions_reference": [
  "Date limite de retour des comptes rendus d'entretien professionnel : vendredi 18 décembre",
  "Priorité du plan de formation 2027 aux formations obligatoires (hygiène et sécurité, habilitations électriques)",
  "Paie de décembre versée le mardi 22 décembre"
 ],
 "actions_reference": [
  {
   "action": "Envoyer un rappel aux encadrants sur les entretiens professionnels",
   "responsable": "M. Rocher",
   "echeance": "le lundi 23 novembre"
  },
  {
   "action": "Présenter le projet de plan de formation au comité social territorial",
   "responsable": "Mme Faure",
   "echeance": "jeudi 10 décembre"
  }
 ],
 "pieges": [
  "Prime de fin d'année versée en novembre : demandée, refusée (pas de changement)",
  "Deux jours de télétravail : renvoyé à la négociation de 2027, rien de décidé",
  "37 entretiens faits sur 112"
 ]
}
```

## CR-609 — Compte rendu (moyen, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CR-609",
 "tache": "Compte rendu",
 "difficulte": "moyen",
 "theme": "social-autonomie",
 "entree": {
  "consigne": "Rédige le compte rendu de cette commission permanente du CCAS : participants, points abordés, décisions, actions (responsable, échéance).",
  "transcription": "Transcription de la commission permanente du CCAS de Lussac-sur-Vienne – mardi 8 décembre 2026 – 17 h – salle du CCAS\n\nMme Renaud (vice-présidente du CCAS) : Bonjour à tous. Nous sommes cinq membres présents : Mme Ollivier, M. Kader, Mme Bastide, M. Tran et moi-même. M. Pinel est excusé. Mme Gauthier, directrice du CCAS, présente les dossiers et M. Lemaire, travailleur social, est là pour les situations qu'il suit. C'est Mme Bastide qui prend les notes. Nous avons quatre demandes d'aide et un point sur le colis de Noël.\n\nMme Gauthier : Premier dossier : une mère seule avec deux enfants, facture d'électricité de 412 euros, avec une menace de coupure. Le règlement intérieur permet une aide de 300 euros au maximum pour l'énergie.\n\nM. Lemaire : Je la suis depuis septembre. Elle a repris un travail à temps partiel. Elle a déjà demandé un échelonnement au fournisseur pour le reste.\n\nMme Renaud : Je propose d'accorder le maximum, 300 euros, versés directement au fournisseur. Qui est d'accord ? Unanimité. Monsieur Lemaire, vous l'informez ?\n\nM. Lemaire : Oui, je l'appelle demain, mercredi 9 décembre.\n\nMme Gauthier : Deuxième dossier : un retraité de 78 ans demande 250 euros pour réparer sa chaudière. Mais son dossier est incomplet : il manque l'avis d'imposition et le devis.\n\nM. Kader : On ne peut pas décider sans le devis.\n\nMme Renaud : Dossier ajourné à la prochaine commission. Madame Gauthier, vous lui demandez les pièces ?\n\nMme Gauthier : Je lui écris cette semaine, avant le vendredi 11 décembre.\n\nMme Gauthier : Troisième dossier : une famille demande une aide de 180 euros pour la cantine du premier trimestre. Leur quotient familial est de 480 euros.\n\nMme Ollivier : Le barème prévoit une prise en charge de la moitié pour ce quotient, donc 90 euros, pas 180.\n\nMme Renaud : Je propose d'appliquer le barème : 90 euros, versés à la caisse des écoles. Qui est pour ? Quatre pour. Monsieur Tran ?\n\nM. Tran : Je m'abstiens, je trouve le barème trop strict, mais je ne vote pas contre.\n\nMme Renaud : Accordé, 90 euros, quatre pour et une abstention.\n\nMme Gauthier : Quatrième dossier : un jeune de 22 ans demande un prêt de 600 euros pour passer son permis de conduire.\n\nM. Kader : Est-ce qu'on fait encore des prêts ?\n\nMme Gauthier : Le règlement le permet jusqu'à 800 euros, remboursables sur 12 mois.\n\nMme Bastide : Il a un contrat d'apprentissage qui commence en janvier, c'est un vrai projet.\n\nMme Renaud : Je propose le prêt de 600 euros, remboursable en 12 mensualités de 50 euros à partir de février. Unanimité. Madame Gauthier, vous préparez la convention de prêt ?\n\nMme Gauthier : Oui, pour signature avant le jeudi 17 décembre.\n\nMme Renaud : Dernier point, le colis de Noël des aînés. On en a préparé combien ?\n\nMme Gauthier : 214 colis. La distribution est prévue le samedi 19 décembre à la salle des fêtes, de 9 h à 12 h.\n\nM. Tran : Certains ne peuvent pas se déplacer.\n\nMme Renaud : Les colis des personnes qui ne peuvent pas venir seront livrés à domicile par les membres volontaires du conseil d'administration le lundi 21 décembre. Monsieur Tran, vous faites la liste des volontaires ?\n\nM. Tran : D'accord, je l'envoie à Mme Gauthier d'ici le mardi 15 décembre.\n\nMme Ollivier : Et l'idée d'un repas des aînés en janvier, on en parle ?\n\nMme Renaud : Le budget 2027 n'est pas voté, on en reparlera au conseil d'administration de janvier. Rien de décidé ce soir. La prochaine commission permanente est fixée au mardi 12 janvier 2027 à 17 h. Merci à tous.",
  "nb_mots": 572
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Transcription fictive rédigée pour l'évaluation (collectivité, personnes et chiffres imaginaires)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "type_reunion": "commission permanente du CCAS (aides facultatives)",
 "participants_reference": [
  "Mme Renaud (vice-présidente du CCAS, préside)",
  "Membres présents : Mme Ollivier, M. Kader, Mme Bastide (prise de notes), M. Tran",
  "Mme Gauthier (directrice du CCAS, présente les dossiers)",
  "M. Lemaire (travailleur social)",
  "Excusé : M. Pinel"
 ],
 "decisions_reference": [
  "Aide énergie de 300 euros (maximum du règlement) versée directement au fournisseur, pour une facture de 412 euros (unanimité)",
  "Demande de 250 euros pour la chaudière ajournée à la prochaine commission (dossier incomplet : avis d'imposition et devis manquants)",
  "Aide cantine de 90 euros selon le barème, versée à la caisse des écoles (4 pour, 1 abstention)",
  "Prêt de 600 euros pour le permis de conduire, remboursable en 12 mensualités de 50 euros à partir de février (unanimité)",
  "Distribution des 214 colis de Noël le samedi 19 décembre à la salle des fêtes, de 9 h à 12 h, et livraison à domicile par des membres volontaires le lundi 21 décembre",
  "Prochaine commission permanente le mardi 12 janvier 2027 à 17 h"
 ],
 "actions_reference": [
  {
   "action": "Informer la bénéficiaire de l'aide énergie",
   "responsable": "M. Lemaire",
   "echeance": "mercredi 9 décembre"
  },
  {
   "action": "Demander les pièces manquantes (avis d'imposition, devis) au retraité",
   "responsable": "Mme Gauthier",
   "echeance": "avant le vendredi 11 décembre"
  },
  {
   "action": "Préparer la convention de prêt pour signature",
   "responsable": "Mme Gauthier",
   "echeance": "avant le jeudi 17 décembre"
  },
  {
   "action": "Envoyer la liste des membres volontaires pour la livraison des colis",
   "responsable": "M. Tran, à Mme Gauthier",
   "echeance": "d'ici le mardi 15 décembre"
  }
 ],
 "pieges": [
  "Aide cantine : 90 euros et non les 180 demandés",
  "Aide énergie : 300 euros et non le montant de la facture (412 euros)",
  "Chaudière : pas de refus, dossier ajourné",
  "Repas des aînés en janvier : rien de décidé (budget 2027 non voté)",
  "M. Tran s'est abstenu sur l'aide cantine, il n'a pas voté contre",
  "M. Pinel était excusé"
 ]
}
```

## CR-611 — Compte rendu (moyen, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CR-611",
 "tache": "Compte rendu",
 "difficulte": "moyen",
 "theme": "collectivites",
 "entree": {
  "consigne": "Rédige le compte rendu de cette réunion de chantier : participants, points abordés, décisions, actions (responsable, échéance).",
  "notes": "Réunion de chantier n° 14 – extension du groupe scolaire des Tilleuls – lundi 23 novembre 2026 – 9 h – sur site, Marcy-l'Étoile-sur-Brévenne\nPrésents : M. Barre (adjoint aux travaux, maître d'ouvrage), Mme Lacroix (architecte, maître d'œuvre, anime), M. Vernet (entreprise de gros œuvre Vernet BTP), Mme Fontaine (entreprise de menuiseries Bois & Baies), M. Rami (technicien des services techniques de la commune)\nAbsent : l'électricien (entreprise Elec 69), non excusé\nCompte rendu rédigé par la maîtrise d'œuvre\n\n1. Avancement\n- Gros œuvre : dalle du 1er étage coulée le mardi 17 novembre. Avancement estimé à 78 %.\n- Menuiseries extérieures : livraison prévue la semaine du lundi 7 décembre.\n- Retard global : 9 jours ouvrés, dus aux pluies d'octobre.\n\n2. Planning\n- DÉCISION : le planning est recalé ; la fin du gros œuvre passe du vendredi 4 décembre au jeudi 17 décembre.\n→ Mme Lacroix diffuse le planning recalé à toutes les entreprises avant le vendredi 27 novembre.\n- M. Vernet propose de travailler le samedi pour rattraper le retard. M. Barre refuse en raison du bruit pour les riverains le week-end. Non retenu.\n\n3. Sécurité du chantier\n- Les barrières côté cour de l'école ont été déplacées par le vent.\n- DÉCISION : les barrières sont lestées et vérifiées chaque matin avant l'arrivée des élèves.\n→ M. Vernet installe les lests d'ici le mercredi 25 novembre.\n→ M. Rami contrôle les barrières chaque matin à 8 h.\n\n4. Modifications demandées\n- La directrice de l'école a demandé une prise électrique supplémentaire dans la future salle de classe 3. M. Barre accepte ; le chiffrage sera demandé à l'électricien, absent ce jour.\n→ Mme Lacroix demande le devis à Elec 69 avant le lundi 30 novembre.\n- Mme Fontaine signale que le coloris des menuiseries « gris anthracite » est en rupture : elle propose le « gris ardoise ». M. Barre veut l'avis du conseil municipal : pas de décision.\n\n5. Prochaine réunion\n- Lundi 30 novembre à 9 h sur site.",
  "nb_mots": 302
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Notes fictives rédigées pour l'évaluation (collectivité, personnes et chiffres imaginaires)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "type_reunion": "réunion de chantier de l'extension du groupe scolaire",
 "participants_reference": [
  "M. Barre (adjoint aux travaux, maître d'ouvrage)",
  "Mme Lacroix (architecte, maître d'œuvre, anime)",
  "M. Vernet (entreprise de gros œuvre Vernet BTP)",
  "Mme Fontaine (entreprise de menuiseries Bois & Baies)",
  "M. Rami (technicien des services techniques)",
  "Absent non excusé : l'électricien (entreprise Elec 69)"
 ],
 "decisions_reference": [
  "Planning recalé : fin du gros œuvre le jeudi 17 décembre au lieu du vendredi 4 décembre",
  "Barrières lestées et vérifiées chaque matin avant l'arrivée des élèves",
  "Prise électrique supplémentaire dans la salle de classe 3 acceptée (chiffrage à demander à l'électricien)",
  "Prochaine réunion le lundi 30 novembre à 9 h sur site"
 ],
 "actions_reference": [
  {
   "action": "Diffuser le planning recalé à toutes les entreprises",
   "responsable": "Mme Lacroix",
   "echeance": "avant le vendredi 27 novembre"
  },
  {
   "action": "Installer les lests des barrières",
   "responsable": "M. Vernet",
   "echeance": "d'ici le mercredi 25 novembre"
  },
  {
   "action": "Contrôler les barrières",
   "responsable": "M. Rami",
   "echeance": "chaque matin à 8 h"
  },
  {
   "action": "Demander le devis de la prise supplémentaire à Elec 69",
   "responsable": "Mme Lacroix",
   "echeance": "avant le lundi 30 novembre"
  }
 ],
 "pieges": [
  "Travail le samedi : proposé par M. Vernet, refusé",
  "Coloris « gris ardoise » des menuiseries : pas de décision (avis du conseil municipal attendu)",
  "Retard global de 9 jours ouvrés, dû aux pluies d'octobre",
  "L'électricien était absent, non excusé",
  "Dalle du 1er étage coulée le mardi 17 novembre"
 ]
}
```

## CR-615 — Compte rendu (difficile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CR-615",
 "tache": "Compte rendu",
 "difficulte": "difficile",
 "theme": "collectivites",
 "entree": {
  "consigne": "Rédige le compte rendu de cette séance du conseil municipal : participants, points abordés, décisions, actions (responsable, échéance).",
  "transcription": "Transcription de la séance du conseil municipal de Lanvollon-sur-Leff – jeudi 26 novembre 2026 – 20 h – salle du conseil\n\nMme Le Bihan (maire) : Bonsoir à toutes et à tous. Il est 20 heures, je déclare la séance ouverte. Je salue les conseillers municipaux, les habitants venus nous écouter et la correspondante du journal local. Avant de commencer, je vais procéder à l'appel. Madame la directrice générale des services, vous voulez bien ?\n\nMme Quéré (directrice générale des services) : Merci, Madame la maire. Le conseil compte 23 membres en exercice. Sont présents : Mme Le Bihan, M. Rolland, premier adjoint chargé des finances, Mme Guillou, adjointe aux affaires scolaires, M. Tanguy, adjoint aux travaux, Mme Morvan, adjointe à la vie associative, M. Daniel, Mme Ollivier, M. Le Goff, Mme Prigent, M. Hervé, Mme Jézéquel, M. Kerbrat, Mme Riou, M. Salaün, Mme Corre, M. Allain, Mme Thomas, M. Le Roux, Mme Bothorel et M. Nicolas. Cela fait 20 présents. Pouvoirs : M. Cadiou a donné pouvoir à M. Rolland, et Mme Le Floch a donné pouvoir à Mme Guillou. M. Péron est absent et n'a pas donné de pouvoir. Il y a donc 22 votants.\n\nMme Le Bihan : Merci. Le quorum est atteint. Je vous propose de désigner Mme Prigent comme secrétaire de séance. Pas d'opposition ? Merci, Madame Prigent. Mme Quéré assiste à la séance, sans voix délibérative, comme d'habitude. Nous avons onze points à l'ordre du jour, plus les questions diverses. Je vous rappelle que la séance est enregistrée pour faciliter la rédaction du procès-verbal.\n\nMme Le Bihan : Premier point : l'approbation du procès-verbal de la séance du jeudi 24 septembre. Vous l'avez reçu avec la convocation. Y a-t-il des remarques ?\n\nM. Allain : Oui, Madame la maire. Page 4, sur le vote des tarifs de la piscine, il est écrit que j'ai voté contre. En réalité, je me suis abstenu. Je l'avais dit clairement en séance.\n\nMme Le Bihan : Madame Quéré, vous avez vérifié l'enregistrement ?\n\nMme Quéré : Oui, M. Allain a raison, c'est une abstention. Le décompte reste le même pour l'adoption, mais il faut corriger : 18 pour, 0 contre, 3 abstentions, au lieu de 18 pour, 1 contre, 2 abstentions.\n\nMme Le Bihan : Merci. Avec cette correction, je soumets le procès-verbal au vote. Qui est pour ? Qui est contre ? Qui s'abstient ? Le procès-verbal est approuvé à l'unanimité des 22 votants, avec la correction demandée par M. Allain. Madame Quéré, vous ferez la correction avant la mise en ligne.\n\nMme Quéré : Oui, la version corrigée sera publiée sur le site avant le vendredi 4 décembre.\n\nMme Le Bihan : Deuxième point : la décision modificative n° 3 du budget 2026. Monsieur Rolland, je vous laisse la parole.\n\nM. Rolland : Merci, Madame la maire. Chers collègues, cette décision modificative est la dernière de l'année. Elle porte sur trois ajustements. Le premier, en fonctionnement : nous devons ajouter 22 000 euros au chapitre des charges à caractère général, principalement à cause de la hausse du prix du gaz pour l'école et le gymnase. Le deuxième, toujours en fonctionnement : 6 500 euros de plus pour les charges de personnel, à cause du remplacement d'un agent en congé maladie aux services techniques. Ces deux dépenses sont compensées par des recettes supplémentaires : la taxe additionnelle aux droits de mutation, qui a rapporté 31 000 euros de plus que prévu, grâce à plusieurs ventes immobilières importantes cette année. Le solde, 2 500 euros, vient abonder les dépenses imprévues. Le troisième ajustement est en investissement : nous transférons 15 000 euros de l'opération « réfection du parvis de l'église » vers l'opération « école », pour financer l'étude thermique préalable aux travaux dont nous parlerons au point suivant. Le parvis n'est pas abandonné, il sera réinscrit au budget 2027.\n\nM. Le Roux : Je voudrais savoir si l'on a une idée de la facture de gaz pour l'an prochain. Parce que si on doit encore ajouter 22 000 euros l'an prochain, il faudrait le prévoir dès le budget primitif.\n\nM. Rolland : C'est une bonne question. Le contrat actuel arrive à échéance en juin 2027. Le syndicat départemental d'énergie prépare un groupement de commandes. Nous n'avons pas encore les prix. Pour le budget 2027, je proposerai une hausse prudente de 15 % de la ligne gaz. Mais ce sera discuté au débat d'orientation budgétaire.\n\nMme Thomas : Et le parvis de l'église, il sera vraiment réinscrit ? Ça fait deux ans qu'on le repousse.\n\nM. Rolland : Je m'y engage pour la proposition de budget. Mais c'est le conseil qui votera le budget 2027. Je ne peux pas promettre le résultat du vote.\n\nMme Le Bihan : Merci. S'il n'y a pas d'autre question, je soumets la décision modificative n° 3 au vote. Qui est pour ? 19. Qui est contre ? Personne. Qui s'abstient ? 3 : M. Le Roux, Mme Thomas et M. Nicolas. La décision modificative n° 3 est adoptée par 19 voix pour et 3 abstentions.\n\nMme Le Bihan : Troisième point : le programme de rénovation énergétique de l'école Anne-de-Bretagne et la demande de subvention au titre de la dotation d'équipement des territoires ruraux, la DETR. Monsieur Tanguy ?\n\nM. Tanguy : Merci. Vous savez que l'école a été construite en 1974 et qu'elle est très mal isolée. Le diagnostic réalisé cet été montre que c'est le bâtiment communal qui consomme le plus d'énergie, devant le gymnase. Le programme comprend l'isolation des murs par l'extérieur, le remplacement des menuiseries, et le remplacement de la chaudière gaz par une pompe à chaleur. Le montant estimé des travaux est de 640 000 euros hors taxes. Le plan de financement proposé est le suivant : DETR, 35 %, soit 224 000 euros ; fonds vert, 25 %, soit 160 000 euros ; région, 10 %, soit 64 000 euros ; le reste, 30 %, soit 192 000 euros, à la charge de la commune. Les travaux auraient lieu pendant l'été 2027, pour ne pas gêner les classes, avec une fin prévue avant la rentrée de septembre 2027.\n\nM. Daniel : 192 000 euros pour la commune, on les trouve où ?\n\nM. Rolland : Une partie sur l'autofinancement, une partie sur un emprunt. Mais je précise : ce soir, on ne vote pas d'emprunt. On vote le programme et le plan de financement pour pouvoir déposer les demandes de subvention. L'emprunt éventuel sera examiné lors du budget 2027.\n\nMme Bothorel : Est-ce qu'on a envisagé du bois plutôt qu'une pompe à chaleur ? Il y a une filière bois-énergie dans le département.\n\nM. Tanguy : Oui, l'étude a comparé les deux. La chaufferie bois demandait un local de stockage qu'on n'a pas sur le site. C'est pour ça que l'étude recommande la pompe à chaleur.\n\nMme Bothorel : D'accord, mais je regrette qu'on n'ait pas regardé un réseau de chaleur avec le collège voisin.\n\nMme Guillou : Je voudrais ajouter un mot pour les familles. Pendant les travaux de l'été 2027, le centre de loisirs, qui occupe habituellement deux salles de l'école, sera installé à la salle polyvalente. J'en ai parlé avec la directrice du centre, qui est d'accord. Les enseignants ont aussi été informés lors du conseil d'école du mardi 3 novembre.\n\nM. Nicolas : Et si les travaux prennent du retard, la rentrée de septembre est-elle menacée ?\n\nM. Tanguy : Le bureau d'études prévoit dix semaines de travaux, et les vacances en comptent huit. C'est serré. C'est pour cela que l'isolation extérieure pourra commencer dès le mois de juin, puisqu'elle ne gêne pas les classes. Les menuiseries et la chaufferie, elles, seront faites en juillet et en août.\n\nMme Le Bihan : C'est une piste intéressante, mais le collège dépend du département, et le département ne prévoit rien à court terme. On peut la noter pour l'avenir. Je vous propose de voter le programme et le plan de financement, et de m'autoriser à déposer les demandes de subvention. Qui est pour ? Unanimité. Merci. La date limite de dépôt du dossier DETR est le vendredi 15 janvier 2027. Monsieur Tanguy et Madame Quéré, vous préparez le dossier ?\n\nM. Tanguy : Oui, avec le bureau d'études. Le dossier sera déposé avant le vendredi 15 janvier 2027.\n\nMme Le Bihan : Et pour la région et le fonds vert ?\n\nMme Quéré : Le fonds vert a une date limite au vendredi 29 janvier 2027. La région, au fil de l'eau. Je propose de déposer les deux dossiers en même temps que la DETR.\n\nMme Le Bihan : Très bien. Quatrième point : les tarifs du cimetière pour 2027. Madame Morvan ?\n\nMme Morvan : Merci. Le cimetière n'avait pas vu ses tarifs révisés depuis 2019. Nous proposons : concession de 15 ans, 180 euros au lieu de 150 ; concession de 30 ans, 350 euros au lieu de 300 ; case de columbarium pour 15 ans, 420 euros au lieu de 400. Nous proposons aussi de créer un tarif pour le jardin du souvenir : la dispersion des cendres resterait gratuite, mais la plaque nominative sur la stèle serait facturée 60 euros.\n\nM. Hervé : 60 euros pour une plaque, c'est cher. Je propose un amendement : 40 euros pour la plaque.\n\nMme Morvan : Le prix d'achat de la plaque gravée est de 52 euros pour la commune. À 40 euros, on perdrait de l'argent sur chaque plaque.\n\nM. Hervé : Je maintiens mon amendement.\n\nMme Le Bihan : Je mets d'abord l'amendement de M. Hervé au vote : plaque à 40 euros. Qui est pour ? 4 : M. Hervé, Mme Thomas, M. Le Roux, M. Nicolas. Qui est contre ? 16. Qui s'abstient ? 2. L'amendement est rejeté. Je soumets maintenant les tarifs tels que proposés par Mme Morvan, plaque à 60 euros comprise. Qui est pour ? 18. Qui est contre ? 2 : M. Hervé et M. Nicolas. Abstentions ? 2 : Mme Thomas et M. Le Roux. Les tarifs du cimetière pour 2027 sont adoptés, ils s'appliqueront au 1er janvier 2027.\n\nMme Morvan : Je ferai mettre à jour le règlement du cimetière et l'affichage à l'entrée avant la fin du mois de décembre.\n\nMme Le Bihan : Merci. Cinquième point : la convention avec le syndicat départemental d'énergie pour le remplacement de l'éclairage public par des lampes LED. Monsieur Tanguy, encore vous.\n\nM. Tanguy : Oui. Le syndicat nous propose de remplacer 214 points lumineux, sur les 380 que compte la commune, en priorité ceux qui ont plus de 25 ans. Le coût total est de 186 000 euros. Le syndicat prend en charge 60 %, la commune 40 %, soit 74 400 euros, payables en trois annuités de 24 800 euros, de 2027 à 2029. L'économie attendue sur la facture d'électricité est d'environ 18 000 euros par an.\n\nMme Corre : Les LED, ça éclaire plus blanc. Est-ce qu'on a pensé aux oiseaux et aux insectes ?\n\nM. Tanguy : Le syndicat propose une température de couleur de 3 000 kelvins, qui est la norme recommandée, et nous gardons l'extinction de minuit à 6 heures, déjà votée en 2023.\n\nM. Salaün : Et les 166 points restants ?\n\nM. Tanguy : Ils sont plus récents. On verra dans une seconde tranche, mais rien n'est prévu pour l'instant.\n\nMme Riou : Quand les travaux commenceront-ils ? Certains quartiers seront-ils plongés dans le noir pendant le chantier ?\n\nM. Tanguy : Le syndicat prévoit de commencer par le bourg au printemps 2027, puis les lotissements, et de finir par les hameaux à l'automne. Les coupures se feront rue par rue, pendant la journée uniquement. Les lampes seront remplacées le jour même, donc aucune rue ne restera sans éclairage la nuit. Le calendrier détaillé sera communiqué par le syndicat au début de l'année, et nous le publierons dans le bulletin municipal.\n\nM. Allain : Et les économies de 18 000 euros par an, elles sont garanties ?\n\nM. Tanguy : C'est une estimation du syndicat, calculée sur les prix actuels de l'électricité. Si les prix baissent, l'économie sera plus faible. Si les prix montent, elle sera plus forte. Personne ne peut la garantir.\n\nMme Le Bihan : Je mets la convention au vote. Qui est pour ? Unanimité. Je signerai la convention, et Mme Quéré la retournera au syndicat. Madame Quéré, dans quel délai ?\n\nMme Quéré : Le syndicat demande un retour avant le jeudi 17 décembre. Ce sera fait.\n\nMme Le Bihan : Sixième point : les subventions exceptionnelles aux associations. Madame Morvan ?\n\nMme Morvan : Merci. Trois associations ont déposé une demande de subvention exceptionnelle depuis le vote des subventions annuelles en mars. La première est le club de football, l'Étoile du Leff, qui demande 2 500 euros pour remplacer les filets et les buts mobiles du terrain d'entraînement, abîmés par la tempête d'octobre. La deuxième est l'association des parents d'élèves de l'école Anne-de-Bretagne, qui demande 800 euros pour financer en partie la classe de découverte des CM2 au mois de mai. La troisième est le cercle celtique, qui demande 1 200 euros pour l'achat de costumes. La commission vie associative s'est réunie le mardi 10 novembre et propose : 2 500 euros pour le club de football, compte tenu du caractère accidentel des dégâts ; 800 euros pour l'association des parents d'élèves ; et 600 euros pour le cercle celtique, soit la moitié de la demande, car l'association dispose d'une trésorerie importante.\n\nM. Kerbrat : Pour le football, l'assurance ne rembourse pas ?\n\nMme Morvan : L'assurance du club a refusé, les buts mobiles n'étaient pas couverts. Le courrier de refus est joint au dossier.\n\nMme Jézéquel : Pour le cercle celtique, je trouve dommage de ne donner que la moitié. Ils représentent la commune dans tous les festivals.\n\nMme Morvan : La commission a regardé les comptes : l'association a plus de 9 000 euros de réserves. Nous ne refusons pas, nous accordons la moitié.\n\nM. Le Goff : Je dois préciser que je suis trésorier du club de football. Je ne prendrai donc pas part au vote sur cette subvention.\n\nMme Le Bihan : Merci de le signaler, Monsieur Le Goff. Nous votons séparément. D'abord, la subvention de 2 500 euros au club de football. M. Le Goff ne prend pas part au vote, il y a donc 21 votants. Qui est pour ? 21. Unanimité des votants. Ensuite, 800 euros à l'association des parents d'élèves. Qui est pour ? Unanimité des 22 votants. Enfin, 600 euros au cercle celtique. Qui est pour ? 20. Qui est contre ? Personne. Qui s'abstient ? 2 : Mme Jézéquel et M. Salaün. Les trois subventions sont adoptées, pour un total de 3 900 euros, pris sur l'enveloppe des subventions non affectées.\n\nMme Morvan : Je notifierai les subventions aux trois associations avant le vendredi 11 décembre.\n\nMme Le Bihan : Septième point : la création d'un poste d'adjoint technique à temps complet aux services techniques. Monsieur Rolland ?\n\nM. Rolland : Depuis le départ en retraite de M. Lorand en juin, le poste n'a pas été remplacé, et les services techniques fonctionnent à quatre au lieu de cinq. Nous proposons de créer un poste d'adjoint technique territorial à temps complet, au 1er février 2027. Le coût annuel chargé est estimé à 36 000 euros, il sera inscrit au budget 2027.\n\nM. Kerbrat : Pourquoi ne pas avoir simplement remplacé M. Lorand sur son poste ?\n\nMme Quéré : Parce que le poste de M. Lorand était un poste d'agent de maîtrise, avec un grade différent. Le profil recherché aujourd'hui est un adjoint technique polyvalent, espaces verts et bâtiments. Le poste d'agent de maîtrise sera supprimé après avis du comité social territorial, lors d'une prochaine séance.\n\nMme Le Bihan : Je vous propose donc de créer le poste d'adjoint technique à temps complet au 1er février 2027. Qui est pour ? Unanimité. Madame Quéré, vous lancez le recrutement ?\n\nMme Quéré : Oui, l'offre sera publiée sur le site de l'emploi territorial avant le vendredi 11 décembre.\n\nMme Le Bihan : Huitième point : la désignation d'un délégué suppléant au syndicat intercommunal des eaux, en remplacement de M. Péron, qui a démissionné de ce mandat pour raisons professionnelles. Je rappelle que M. Péron reste conseiller municipal. Y a-t-il des candidats ?\n\nMme Riou : Je suis candidate.\n\nM. Allain : Moi aussi.\n\nMme Le Bihan : Nous avons deux candidats : Mme Riou et M. Allain. Le vote a lieu à bulletin secret, puisque deux candidats se présentent et qu'un conseiller l'a demandé. Je demande à Mme Prigent et à M. Nicolas d'être assesseurs.\n\n(Le vote a lieu.)\n\nMme Prigent : Résultats : 22 votants, 22 bulletins, 1 bulletin blanc, 21 suffrages exprimés. Mme Riou : 14 voix. M. Allain : 7 voix.\n\nMme Le Bihan : Mme Riou est élue déléguée suppléante au syndicat intercommunal des eaux. Félicitations. Madame Quéré, vous notifiez la délibération au syndicat ?\n\nMme Quéré : Oui, avant le vendredi 4 décembre.\n\nMme Le Bihan : Neuvième point : la motion pour le maintien du bureau de poste. Vous savez que La Poste envisage de transformer notre bureau en agence postale communale, ce qui ferait reposer le service sur la mairie. Nous avons appris que les horaires d'ouverture seraient réduits dès janvier. Je vous propose une motion demandant le maintien d'un bureau de plein exercice, avec au moins 24 heures d'ouverture par semaine. Monsieur Daniel, vous avez travaillé sur le texte ?\n\nM. Daniel : Oui. La motion rappelle que le bureau sert 6 000 habitants de la commune et des communes voisines, qu'il n'y a pas d'autre bureau à moins de 12 kilomètres, et que beaucoup de personnes âgées n'utilisent pas internet. Elle demande le maintien du bureau et l'ouverture d'une concertation avec les élus.\n\nMme Jézéquel : Est-ce qu'on ne devrait pas aussi proposer une solution, par exemple une maison France services avec La Poste à l'intérieur ?\n\nMme Le Bihan : C'est une idée que nous avons évoquée en bureau municipal, mais nous n'avons aucune étude. Je préfère ne pas l'inscrire dans la motion ce soir. On pourra en reparler en commission.\n\nM. Le Goff : Je suis d'accord avec la motion telle qu'elle est. J'ajoute que les commerçants du bourg comptent beaucoup sur le bureau de poste : plusieurs d'entre eux y déposent leurs colis tous les jours, et une agence postale ne pourrait pas accepter les envois professionnels en grand nombre. C'est un argument qu'on pourrait faire valoir dans les échanges avec La Poste.\n\nM. Daniel : C'est juste. Je ne l'ai pas mis dans le texte pour qu'il reste court, mais nous pourrons le dire lors de la concertation, si elle a lieu.\n\nMme Thomas : Est-ce qu'on sait quand La Poste doit prendre sa décision ?\n\nMme Le Bihan : Non, nous n'avons reçu aucun calendrier officiel. Nous avons seulement été informés oralement de la réduction des horaires en janvier. C'est pour cela que la motion demande aussi une information écrite.\n\nMme Le Bihan : Je mets la motion au vote. Qui est pour ? Unanimité. La motion sera envoyée à la direction régionale de La Poste, au préfet et aux parlementaires. Monsieur Daniel, vous vous en chargez avec le secrétariat ?\n\nM. Daniel : Oui, envoi dès lundi, le lundi 30 novembre.\n\nMme Le Bihan : Dixième point : le rapport annuel sur le prix et la qualité du service public d'assainissement collectif, pour l'année 2025. Monsieur Tanguy ?\n\nM. Tanguy : Oui. Comme chaque année, la loi nous oblige à présenter ce rapport au conseil. Je résume les chiffres principaux. La station d'épuration traite les eaux de 2 140 abonnés. Le volume facturé est de 182 000 mètres cubes, en légère baisse de 2 % par rapport à 2024. Le prix du service pour une facture type de 120 mètres cubes est de 2,31 euros par mètre cube, toutes taxes comprises, contre 2,24 euros l'an dernier. La conformité des rejets de la station est de 100 %. En revanche, le réseau a connu 6 débordements par temps de pluie, au niveau du poste de relèvement de la rue de la Gare. Des travaux sur ce poste sont prévus par le syndicat en 2027.\n\nMme Corre : Les 6 débordements, ils vont où ?\n\nM. Tanguy : Dans le ruisseau du Moulin. C'est justement pour cela que les travaux sont prioritaires. Le syndicat les a inscrits à son programme, mais c'est le syndicat qui décide, pas la commune.\n\nM. Hervé : Et le prix va encore augmenter ?\n\nM. Tanguy : Le prix est fixé par le syndicat. Je n'ai pas d'information sur les tarifs 2027.\n\nMme Le Bihan : Ce rapport ne donne pas lieu à un vote : le conseil en prend acte. Il sera mis à la disposition du public en mairie et sur le site internet. Madame Quéré, vous pouvez le mettre en ligne ?\n\nMme Quéré : Oui, avant le jeudi 10 décembre.\n\nMme Le Bihan : Onzième point : le compte rendu des décisions prises par la maire par délégation du conseil. Madame Quéré ?\n\nMme Quéré : Depuis la dernière séance, Mme la maire a signé trois décisions : l'attribution du marché d'entretien des espaces verts du lotissement des Hortensias à l'entreprise Jardins d'Armor, pour 12 400 euros par an ; la signature d'un bail pour le cabinet infirmier, rue de la Gare, avec un loyer mensuel de 480 euros ; et l'acceptation d'un don de 1 500 euros d'une habitante pour la bibliothèque.\n\nMme Le Bihan : Ce point ne donne pas lieu à vote, le conseil en prend acte. Passons aux questions diverses.\n\nMme Guillou : Je voudrais faire un point sur le marché de Noël. Il aura lieu le dimanche 13 décembre, de 10 heures à 18 heures, sur la place de la mairie. Nous avons 28 exposants inscrits. Attention, sur l'affiche distribuée la semaine dernière, il est écrit le samedi 12 décembre : c'est une erreur, c'est bien le dimanche 13 décembre.\n\nMme Le Bihan : Est-ce qu'on fait corriger les affiches ?\n\nMme Guillou : Oui, je fais réimprimer les affiches et je préviens les commerçants avant le mercredi 2 décembre.\n\nM. Salaün : J'ai une question sur le city-stade. Des jeunes m'ont demandé quand il serait construit, ils ont vu passer l'information sur les réseaux sociaux.\n\nMme Le Bihan : Je veux être très claire : il n'y a aucune décision sur un city-stade. C'est une idée qui a été évoquée par le conseil municipal des jeunes, et nous allons regarder ce que cela coûterait. Mais rien n'est inscrit au budget, et ce n'est pas à l'ordre du jour.\n\nM. Salaün : Alors il faudrait le dire aux jeunes.\n\nMme Morvan : Je peux rencontrer le conseil municipal des jeunes pour leur expliquer où en est le projet. Leur prochaine réunion est le mercredi 9 décembre.\n\nMme Le Bihan : Très bien, merci Madame Morvan.\n\nM. Kerbrat : J'ai une question sur la fibre optique. Plusieurs habitants du hameau de Kervoas m'ont dit qu'ils n'étaient toujours pas raccordables, alors que le bourg l'est depuis deux ans.\n\nM. Tanguy : Le déploiement est assuré par le syndicat mixte régional, pas par la commune. D'après le dernier point d'avancement, les hameaux de Kervoas et de Pen Ar Hoat devaient être raccordables au premier semestre 2026, mais il y a eu un retard lié aux poteaux téléphoniques à remplacer. Le syndicat parle maintenant du second semestre 2027, sans date précise.\n\nM. Kerbrat : On ne peut pas les relancer ?\n\nMme Le Bihan : Je peux écrire au président du syndicat mixte pour demander un calendrier précis. Je le ferai. Mais je ne peux pas m'engager sur une date à leur place. Je préfère que personne ne promette de date aux habitants.\n\nM. Kerbrat : D'accord. Je transmettrai la réponse aux habitants dès qu'on l'aura.\n\nMme Ollivier : Une dernière chose : des habitants de la rue du Moulin se plaignent du stationnement sur les trottoirs. Les poussettes et les fauteuils roulants doivent descendre sur la chaussée, ce qui est dangereux, surtout aux heures de sortie de l'école.\n\nM. Le Roux : J'habite à côté, je confirme. Ce sont surtout des voitures de clients du garage, le matin.\n\nMme Le Bihan : Monsieur Tanguy, vous pourrez rencontrer le garagiste ?\n\nM. Tanguy : Oui, je le rencontrerai. La police municipale va aussi faire de la prévention, puis des verbalisations. Je propose aussi qu'on étudie un marquage au sol. Mais pour le marquage, je dois d'abord voir avec le département, car c'est une route départementale.\n\nMme Le Bihan : Donc pas de décision ce soir sur le marquage. Avant de lever la séance, je vous annonce la date de la prochaine séance : le jeudi 28 janvier 2027 à 20 heures, avec le débat d'orientation budgétaire. J'avais d'abord parlé du jeudi 21 janvier 2027, mais ce jour-là il y a le conseil communautaire. C'est donc bien le jeudi 28 janvier 2027.\n\nM. Rolland : Je rappelle que les adjoints doivent me transmettre leurs propositions pour le budget 2027 avant le vendredi 18 décembre, pour que je puisse préparer le débat d'orientation budgétaire.\n\nMme Le Bihan : Merci à toutes et à tous. Je vous souhaite une bonne fin de soirée. La séance est levée à 22 h 10.\n\n(Après la levée de séance, une habitante demande la parole.)\n\nUne habitante : Madame la maire, pour le bureau de poste, est-ce que les habitants peuvent signer une pétition ?\n\nMme Le Bihan : La séance est levée, Madame, je ne peux plus donner la parole officiellement, mais venez me voir, nous en parlerons. Il n'y a pas de pétition organisée par la mairie pour l'instant.",
  "nb_mots": 4063
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Transcription fictive rédigée pour l'évaluation (collectivité, personnes et chiffres imaginaires)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "type_reunion": "séance publique du conseil municipal",
 "participants_reference": [
  "Mme Le Bihan (maire, préside)",
  "20 conseillers présents sur 23 en exercice, dont M. Rolland (1er adjoint, finances), Mme Guillou (adjointe aux affaires scolaires), M. Tanguy (adjoint aux travaux), Mme Morvan (adjointe à la vie associative), M. Daniel, Mme Ollivier, M. Le Goff, Mme Prigent, M. Hervé, Mme Jézéquel, M. Kerbrat, Mme Riou, M. Salaün, Mme Corre, M. Allain, Mme Thomas, M. Le Roux, Mme Bothorel, M. Nicolas",
  "Mme Prigent (secrétaire de séance)",
  "Pouvoirs : M. Cadiou à M. Rolland, Mme Le Floch à Mme Guillou (22 votants)",
  "Absent sans pouvoir : M. Péron",
  "Mme Quéré (directrice générale des services), sans voix délibérative"
 ],
 "decisions_reference": [
  "Procès-verbal du jeudi 24 septembre approuvé à l'unanimité, avec la correction demandée par M. Allain (abstention et non vote contre)",
  "Décision modificative n° 3 adoptée (19 pour, 3 abstentions) : +22 000 euros de charges générales (gaz), +6 500 euros de personnel, financés par 31 000 euros de droits de mutation, et 15 000 euros transférés du parvis de l'église vers l'école",
  "Programme de rénovation énergétique de l'école Anne-de-Bretagne (640 000 euros HT) et plan de financement adoptés à l'unanimité (DETR 35 %, fonds vert 25 %, région 10 %, commune 30 %), avec autorisation de déposer les demandes de subvention",
  "Amendement de M. Hervé (plaque à 40 euros) rejeté ; tarifs du cimetière 2027 adoptés (18 pour, 2 contre, 2 abstentions) : concession 15 ans 180 euros, 30 ans 350 euros, case de columbarium 420 euros, plaque du jardin du souvenir 60 euros, au 1er janvier 2027",
  "Convention avec le syndicat départemental d'énergie pour 214 points lumineux en LED adoptée à l'unanimité (part communale de 74 400 euros en trois annuités de 2027 à 2029)",
  "Subventions exceptionnelles adoptées : 2 500 euros au club de football l'Étoile du Leff (21 votants, M. Le Goff ne prenant pas part au vote), 800 euros à l'association des parents d'élèves (unanimité), 600 euros au cercle celtique (20 pour, 2 abstentions), soit 3 900 euros",
  "Création d'un poste d'adjoint technique à temps complet au 1er février 2027 (unanimité)",
  "Mme Riou élue déléguée suppléante au syndicat intercommunal des eaux, à bulletin secret (14 voix contre 7 à M. Allain, 1 blanc)",
  "Motion pour le maintien d'un bureau de poste de plein exercice, avec au moins 24 heures d'ouverture par semaine, adoptée à l'unanimité",
  "Le conseil prend acte du rapport annuel 2025 sur le prix et la qualité du service d'assainissement collectif",
  "Le conseil prend acte des trois décisions prises par la maire par délégation (marché d'espaces verts, bail du cabinet infirmier, don à la bibliothèque)",
  "Prochaine séance le jeudi 28 janvier 2027 à 20 heures, avec le débat d'orientation budgétaire"
 ],
 "actions_reference": [
  {
   "action": "Corriger et publier sur le site le procès-verbal du jeudi 24 septembre",
   "responsable": "Mme Quéré",
   "echeance": "avant le vendredi 4 décembre"
  },
  {
   "action": "Déposer le dossier de subvention DETR, avec le bureau d'études",
   "responsable": "M. Tanguy et Mme Quéré",
   "echeance": "avant le vendredi 15 janvier 2027"
  },
  {
   "action": "Déposer les dossiers du fonds vert et de la région en même temps que la DETR",
   "responsable": "Mme Quéré",
   "echeance": "avant le vendredi 15 janvier 2027 (date limite du fonds vert : vendredi 29 janvier 2027)"
  },
  {
   "action": "Mettre à jour le règlement du cimetière et l'affichage à l'entrée",
   "responsable": "Mme Morvan",
   "echeance": "avant la fin du mois de décembre"
  },
  {
   "action": "Retourner la convention signée au syndicat départemental d'énergie",
   "responsable": "Mme Quéré",
   "echeance": "avant le jeudi 17 décembre"
  },
  {
   "action": "Notifier les subventions exceptionnelles aux trois associations",
   "responsable": "Mme Morvan",
   "echeance": "avant le vendredi 11 décembre"
  },
  {
   "action": "Mettre en ligne le rapport sur l'assainissement",
   "responsable": "Mme Quéré",
   "echeance": "avant le jeudi 10 décembre"
  },
  {
   "action": "Écrire au président du syndicat mixte pour demander un calendrier de raccordement à la fibre",
   "responsable": "Mme Le Bihan",
   "echeance": "sans date fixée"
  },
  {
   "action": "Rencontrer le garagiste au sujet du stationnement rue du Moulin",
   "responsable": "M. Tanguy",
   "echeance": "sans date fixée"
  },
  {
   "action": "Publier l'offre d'emploi d'adjoint technique sur le site de l'emploi territorial",
   "responsable": "Mme Quéré",
   "echeance": "avant le vendredi 11 décembre"
  },
  {
   "action": "Notifier la délibération de désignation au syndicat intercommunal des eaux",
   "responsable": "Mme Quéré",
   "echeance": "avant le vendredi 4 décembre"
  },
  {
   "action": "Envoyer la motion à La Poste, au préfet et aux parlementaires",
   "responsable": "M. Daniel avec le secrétariat",
   "echeance": "lundi 30 novembre"
  },
  {
   "action": "Faire réimprimer les affiches du marché de Noël et prévenir les commerçants",
   "responsable": "Mme Guillou",
   "echeance": "avant le mercredi 2 décembre"
  },
  {
   "action": "Rencontrer le conseil municipal des jeunes au sujet du city-stade",
   "responsable": "Mme Morvan",
   "echeance": "mercredi 9 décembre"
  },
  {
   "action": "Transmettre les propositions pour le budget 2027",
   "responsable": "les adjoints, à M. Rolland",
   "echeance": "avant le vendredi 18 décembre"
  }
 ],
 "pieges": [
  "Aucun emprunt n'est voté pour l'école : seul le programme et le plan de financement sont adoptés",
  "Le parvis de l'église est reporté au budget 2027, sans engagement sur le vote du budget",
  "Chaufferie bois et réseau de chaleur avec le collège : écartés ou simples pistes, rien de décidé",
  "Seconde tranche de LED pour les 166 points restants : rien de prévu",
  "Économie de 18 000 euros par an sur l'électricité : estimation du syndicat, non garantie",
  "Cercle celtique : 600 euros et non les 1 200 euros demandés",
  "M. Le Goff, trésorier du club de football, n'a pas pris part au vote sur sa subvention",
  "Travaux du poste de relèvement et prix de l'assainissement : décidés par le syndicat, pas par la commune",
  "Fibre à Kervoas et Pen Ar Hoat : aucune date promise (second semestre 2027 évoqué par le syndicat, sans date précise)",
  "Maison France services avec La Poste : non inscrite dans la motion, aucune étude",
  "City-stade : aucune décision, rien au budget",
  "Marquage au sol rue du Moulin : pas de décision (route départementale)",
  "Marché de Noël le dimanche 13 décembre et non le samedi 12 décembre",
  "Prochaine séance le jeudi 28 janvier 2027 et non le jeudi 21 janvier 2027",
  "M. Péron reste conseiller municipal : il n'a démissionné que de son mandat au syndicat des eaux",
  "Pétition sur le bureau de poste : aucune pétition organisée par la mairie (échange après la levée de séance)",
  "Les décisions prises par délégation ne sont pas votées : le conseil en prend acte"
 ]
}
```

## CR-617 — Compte rendu (difficile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CR-617",
 "tache": "Compte rendu",
 "difficulte": "difficile",
 "theme": "social-autonomie",
 "entree": {
  "consigne": "Rédige le compte rendu de cette séance de la commission d'attribution des logements : participants, points abordés, décisions, actions (responsable, échéance).",
  "transcription": "Transcription de la séance de la commission d'attribution des logements et d'examen de l'occupation des logements (CALEOL) de l'office public de l'habitat Rance-Émeraude – mercredi 18 novembre 2026 – 14 h – salle de réunion du siège, à Dinan-Lanvallay\n\nM. Hamon (président de la commission, administrateur de l'office) : Bonjour à toutes et à tous. Il est 14 heures, nous pouvons commencer. Je rappelle la composition de la séance d'aujourd'hui. Sont présents avec voix délibérative : moi-même, Mme Rivière et M. Gaudin, administrateurs de l'office, Mme Le Meur, administratrice représentant les locataires, et Mme Costa, représentante de l'association d'insertion La Passerelle. Pour les logements situés à Taden, nous avons M. Botrel, adjoint au maire de Taden, qui représente le maire et qui a voix délibérative pour les logements de sa commune. Le représentant de l'intercommunalité, M. Fournier, s'est excusé. Le représentant du préfet n'est pas présent, comme souvent. Avec voix consultative, Mme Salmon, chargée de clientèle, qui présente les dossiers, et Mme Bréhier, responsable du service gestion locative, qui assure le secrétariat de la commission et rédigera le procès-verbal. Le quorum est atteint, puisque cinq membres avec voix délibérative sont présents, et six pour les logements de Taden.\n\nM. Hamon : Je rappelle aussi les règles. La commission examine au moins trois candidatures par logement, sauf en cas d'insuffisance de candidats, et elle classe les candidats. Elle peut décider une attribution, une attribution sous condition suspensive, une non-attribution motivée ou un rejet pour irrecevabilité. Les dossiers sont présentés de manière anonyme, par leur numéro. Nous avons aujourd'hui onze logements à attribuer et deux dossiers d'examen de l'occupation. Le logement de la rue des Rosiers a été retiré de l'ordre du jour ce matin, parce que les travaux de remise en état ne sont pas terminés. Il sera présenté à la commission de décembre. Il reste donc dix logements à attribuer.\n\nM. Hamon : Avant d'examiner les logements, Madame Bréhier va nous présenter rapidement le bilan des attributions du troisième trimestre, comme nous le faisons à chaque fin de trimestre.\n\nMme Bréhier : Merci. Entre juillet et septembre, la commission a attribué 54 logements. Parmi les ménages entrés dans les lieux, 27 relevaient d'un public prioritaire, soit la moitié. 14 attributions ont bénéficié à des ménages du premier quartile de revenus, c'est-à-dire les 25 % de demandeurs les plus modestes, hors quartiers prioritaires (QPV). L'objectif fixé par la loi est de 25 % des attributions hors quartiers prioritaires, et nous sommes à 26 %. Le délai moyen d'attente des ménages attribués est de 14 mois. Le taux de refus des propositions par les candidats est de 22 %, en légère hausse : les motifs les plus fréquents sont la localisation du logement, l'étage sans ascenseur et le montant des charges.\n\nMme Le Meur : Le montant des charges, c'est surtout le chauffage collectif, je suppose ?\n\nMme Bréhier : Oui, principalement dans les résidences chauffées au gaz. Le conseil d'administration a demandé une étude sur ce sujet, mais aucune décision n'a été prise.\n\nM. Gaudin : Et la cotation de la demande, elle est appliquée depuis quand ?\n\nMme Bréhier : La grille de cotation intercommunale est appliquée depuis le 1er septembre. Elle donne des points selon l'ancienneté de la demande, la situation de logement et la situation sociale. Je rappelle qu'elle aide à présenter les candidats, mais qu'elle ne remplace pas la décision de la commission. La commission reste libre de son classement, à condition de le motiver.\n\nMme Costa : C'est important, parce que certaines situations d'urgence ne se voient pas dans les points.\n\nM. Hamon : Merci pour ce bilan, qui ne demande pas de vote. Nous passons aux logements.\n\nMme Salmon : Merci, Monsieur le président. Premier logement : un T3 de 68 mètres carrés au deuxième étage, résidence Les Champs-Garel, à Dinan. Loyer de 412 euros hors charges, charges estimées à 96 euros. Le logement a un balcon, il n'y a pas d'ascenseur. Trois candidats. Premier dossier, n° 2026-0388 : une mère seule avec deux enfants de 7 et 11 ans, actuellement hébergée chez sa sœur, demande depuis 19 mois, revenus de 1 480 euros par mois, salaire et allocations familiales. Elle est reconnue prioritaire au titre du droit au logement opposable. Deuxième dossier, n° 2026-0102 : un couple avec un enfant de 3 ans, locataire du parc privé, logement trop petit, demande depuis 11 mois, revenus de 2 350 euros. Troisième dossier, n° 2025-1841 : un couple avec deux enfants, revenus de 3 900 euros par mois.\n\nM. Gaudin : Le troisième dossier, 3 900 euros pour quatre personnes, ce n'est pas au-dessus des plafonds ?\n\nMme Salmon : Si, je l'ai vérifié ce matin : le revenu fiscal de référence du ménage dépasse de 8 % le plafond du logement financé en PLUS. Il n'est pas recevable pour ce logement. Je l'avais présenté parce que la demande était enregistrée sur ce secteur, mais il faut le rejeter pour irrecevabilité.\n\nM. Hamon : Bien. Pour les deux autres, je propose de classer en rang 1 le dossier 2026-0388, prioritaire au titre du droit au logement opposable, et en rang 2 le dossier 2026-0102. Qui est d'accord ? Unanimité. Le logement est attribué en rang 1 au dossier 2026-0388, en rang 2 au dossier 2026-0102, et le dossier 2025-1841 est rejeté pour dépassement du plafond de ressources.\n\nMme Le Meur : Pour la famille prioritaire, il n'y a pas d'ascenseur, mais elle n'a pas de problème de mobilité, c'est bien ça ?\n\nMme Salmon : C'est bien ça. Aucun problème signalé.\n\nMme Salmon : Deuxième logement : un T2 de 47 mètres carrés au rez-de-chaussée, rue Victor-Hugo, à Dinan. Loyer de 318 euros, charges de 72 euros. Le logement est adapté aux personnes à mobilité réduite : douche à l'italienne et barres d'appui. Trois candidats. Dossier n° 2025-1207 : un homme de 74 ans, veuf, en fauteuil roulant, qui vit au troisième étage sans ascenseur et ne peut plus sortir de chez lui. Retraite de 1 210 euros. Demande depuis 22 mois. Dossier n° 2026-0455 : une femme de 58 ans, seule, sans problème de mobilité, demande depuis 6 mois. Dossier n° 2026-0521 : un jeune homme de 24 ans, apprenti, demande depuis 4 mois.\n\nMme Costa : Pour le monsieur en fauteuil, c'est vraiment urgent. Notre association le suit, il n'est pas sorti de chez lui depuis l'été.\n\nM. Hamon : Le logement est adapté, il correspond exactement à sa situation. Je propose le rang 1 au dossier 2025-1207. Pour les autres, comme le logement est adapté, je propose de ne pas classer les deux autres candidats, qui n'ont pas de besoin d'adaptation, et de demander au service de rechercher une personne à mobilité réduite en rang 2.\n\nMme Rivière : On ne peut pas laisser le rang 2 vide ? S'il refuse, le logement restera vacant.\n\nMme Bréhier : Si le candidat en rang 1 refuse, le logement repassera en commission. C'est préférable à une attribution à une personne qui n'a pas besoin d'un logement adapté.\n\nM. Hamon : Je mets aux voix : attribution en rang 1 au dossier 2025-1207, sans autre rang, et non-attribution aux dossiers 2026-0455 et 2026-0521, au motif que le logement est réservé à une personne à mobilité réduite. Unanimité.\n\nMme Salmon : Troisième logement : un T4 de 82 mètres carrés, maison individuelle avec jardin, rue des Châtaigniers, à Taden. Loyer de 586 euros, charges de 45 euros. Ce logement relève du contingent de la commune de Taden. Monsieur Botrel ?\n\nM. Botrel : Oui, la commune a proposé trois candidats, et le service en a ajouté un. Je laisse Mme Salmon présenter.\n\nMme Salmon : Dossier n° 2026-0219 : un couple avec trois enfants, locataire d'un T3 du parc de l'office à Dinan, qui demande une mutation pour un logement plus grand. Revenus de 2 780 euros. Dossier n° 2026-0310 : une famille de quatre personnes, dont le père travaille à la mairie de Taden, revenus de 2 450 euros, demande depuis 9 mois. Dossier n° 2026-0347 : un couple avec deux enfants, hébergé dans un mobil-home, revenus de 1 920 euros, demande depuis 14 mois. Dossier n° 2026-0400, proposé par le service : une femme avec quatre enfants, victime de violences conjugales, actuellement en hébergement d'urgence, revenus de 1 650 euros.\n\nM. Botrel : La commune souhaite donner la priorité au dossier 2026-0310, l'agent municipal.\n\nMme Le Meur : Je comprends, mais la situation du dossier 2026-0400 est plus urgente. Les victimes de violences font partie des publics prioritaires définis par la loi.\n\nM. Gaudin : Et la mutation, le dossier 2026-0219, libérerait un T3 à Dinan. C'est aussi un argument.\n\nMme Costa : Pour la famille du dossier 2026-0400, je peux préciser que l'hébergement d'urgence prend fin au mois de janvier. Après, elle n'a aucune solution. Le centre d'hébergement nous a demandé d'appuyer le dossier.\n\nM. Botrel : Je ne conteste pas l'urgence. Mais la commune a un contingent de logements, et elle a le droit de proposer ses candidats. Si la commission ne suit jamais la commune, à quoi sert le contingent ?\n\nMme Bréhier : La commune propose des candidats sur son contingent, et c'est ce qu'elle a fait. Mais la décision d'attribution appartient à la commission, qui doit respecter les priorités fixées par la loi. Le candidat de la commune reste classé, il peut obtenir le logement si les candidats placés avant lui refusent.\n\nMme Rivière : Et pour l'agent municipal, il y a d'autres logements prévus à Taden ?\n\nM. Botrel : Deux logements de la résidence du Bourg doivent se libérer au printemps. La commune proposera de nouveau sa candidature.\n\nM. Hamon : Je vous propose un classement : rang 1 au dossier 2026-0400, public prioritaire en hébergement d'urgence ; rang 2 au dossier 2026-0347 ; rang 3 au dossier 2026-0310. Le dossier 2026-0219, la mutation, sera examiné pour un autre T4 plus proche de Dinan, comme la famille l'a demandé dans son dossier. Monsieur Botrel, vous avez voix délibérative sur ce logement.\n\nM. Botrel : Je vote contre ce classement, la commune voulait le rang 1 pour son agent.\n\nM. Hamon : Je mets aux voix. Qui est pour le classement proposé ? Mme Rivière, M. Gaudin, Mme Le Meur, Mme Costa et moi-même, soit 5. Contre : M. Botrel, 1. Le classement est adopté : rang 1 au dossier 2026-0400, rang 2 au dossier 2026-0347, rang 3 au dossier 2026-0310.\n\nM. Botrel : Je demande que l'avis de la commune figure au procès-verbal.\n\nMme Bréhier : Ce sera noté, Monsieur Botrel.\n\nMme Salmon : Quatrième logement, toujours à Taden : un T2 de 51 mètres carrés au premier étage, résidence du Bourg. Loyer de 344 euros, charges de 68 euros. Il n'y a que deux candidats, malgré l'appel à candidatures du service. Dossier n° 2026-0478 : un homme de 31 ans, en contrat à durée indéterminée, revenus de 1 650 euros, qui vit chez ses parents. Dossier n° 2026-0490 : une jeune femme de 22 ans, étudiante, revenus de 710 euros avec la bourse et l'aide de ses parents.\n\nM. Gaudin : Pour l'étudiante, le reste à vivre est faible.\n\nMme Salmon : Avec l'aide personnalisée au logement, que j'ai simulée à 186 euros, son taux d'effort serait de 31 %, et son reste à vivre de 9 euros par jour et par personne. C'est en dessous du seuil de 12 euros que l'office utilise comme repère.\n\nMme Costa : Ce repère n'est pas un critère d'exclusion.\n\nMme Salmon : C'est exact, c'est un repère pour l'analyse.\n\nM. Hamon : Je propose rang 1 au dossier 2026-0478 et rang 2 au dossier 2026-0490. Qui est d'accord ? Unanimité, y compris M. Botrel. Je rappelle que la commission a pris acte de l'insuffisance de candidatures pour ce logement, puisqu'il n'y a que deux candidats. M. Botrel nous quitte maintenant, puisque les logements suivants ne sont pas situés à Taden.\n\nM. Botrel : Au revoir à tous.\n\nMme Salmon : Cinquième logement : un T1 bis de 34 mètres carrés au quatrième étage avec ascenseur, place Duclos, à Dinan. Loyer de 241 euros, charges de 58 euros. Trois candidats. Dossier n° 2026-0533 : un homme de 45 ans, sortant d'un centre d'hébergement et de réinsertion sociale, accompagné par La Passerelle, revenus de 980 euros, allocation aux adultes handicapés. Dossier n° 2026-0284 : une femme de 63 ans, retraitée, revenus de 1 090 euros, logée dans un appartement du parc privé dont le propriétaire vend le bien. Dossier n° 2026-0561 : un jeune homme de 19 ans, en service civique, revenus de 620 euros.\n\nMme Costa : Je dois dire que je connais personnellement le dossier 2026-0533, puisque notre association l'accompagne. Je préfère ne pas prendre part à la décision pour ce logement.\n\nM. Hamon : C'est noté. Mme Costa ne prend pas part au vote sur ce logement. Pour le dossier 2026-0533, l'accompagnement social est prévu ?\n\nMme Salmon : Oui, La Passerelle a transmis une attestation d'accompagnement vers et dans le logement pour 12 mois.\n\nMme Le Meur : Et pour la dame de 63 ans dont le propriétaire vend, elle a une date de départ ?\n\nMme Salmon : Son congé pour vente prend effet au mois de mars. Elle a donc encore quelques mois, mais elle s'inquiète beaucoup. Elle demande un logement avec ascenseur, ce qui est le cas ici.\n\nM. Gaudin : Le monsieur sortant du centre d'hébergement, il est prêt à vivre seul ?\n\nMme Salmon : Le centre l'estime prêt. Il a déjà vécu seul avant son hospitalisation, et l'accompagnement de La Passerelle prévoit des visites chaque semaine pendant les trois premiers mois.\n\nM. Hamon : Je propose rang 1 au dossier 2026-0533, rang 2 au dossier 2026-0284, et rang 3 au dossier 2026-0561. Qui est d'accord ? Mme Rivière, M. Gaudin, Mme Le Meur et moi-même : unanimité des quatre votants.\n\nMme Salmon : Sixième logement : un T3 de 64 mètres carrés au premier étage, rue de Brest, à Dinan. Dans le document de séance, le loyer est indiqué à 398 euros : c'est une erreur de saisie, le loyer est de 389 euros hors charges, et les charges de 88 euros. Trois candidats. Dossier n° 2026-0157 : un couple avec un enfant de 2 ans et un second enfant attendu en février, locataire d'un T2 du parc privé, revenus de 2 110 euros, demande depuis 13 mois. Dossier n° 2026-0198 : une femme seule avec un enfant de 9 ans, revenus de 1 380 euros. Il manque dans son dossier l'avis d'imposition de 2026 sur les revenus de 2025. Dossier n° 2026-0266 : un couple de retraités, revenus de 1 870 euros, qui souhaite quitter une maison devenue trop grande.\n\nMme Rivière : Pour le dossier incomplet, on peut quand même le classer ?\n\nMme Bréhier : On peut attribuer sous condition suspensive de la production de la pièce manquante dans un délai fixé. Mais si le candidat est en rang 1, cela retarde la signature du bail.\n\nM. Hamon : Je propose rang 1 au dossier 2026-0157, rang 2 au dossier 2026-0266, et rang 3 au dossier 2026-0198, sous condition suspensive de la production de l'avis d'imposition dans un délai de 10 jours. Qui est d'accord ? Unanimité, Mme Costa étant de nouveau votante.\n\nMme Salmon : Septième logement : un T5 de 96 mètres carrés au troisième étage avec ascenseur, quartier de la Fontaine-des-Eaux, à Dinan. Loyer de 612 euros, charges de 124 euros. Deux candidats seulement. Dossier n° 2025-1980 : une famille de sept personnes, dont cinq enfants, qui vit dans un T3 du parc de l'office, en suroccupation. Revenus de 2 960 euros. Dossier n° 2026-0602 : une famille de six personnes, hébergée à l'hôtel par le 115 depuis 3 mois, revenus de 1 540 euros.\n\nMme Le Meur : Les deux familles sont dans une situation difficile.\n\nM. Gaudin : La famille de l'hôtel, avec 1 540 euros pour six personnes, pourra payer le loyer ?\n\nMme Salmon : Avec l'aide personnalisée au logement simulée à 498 euros, le loyer résiduel serait de 238 euros, charges comprises. Le taux d'effort serait de 15 %. Le dossier est soutenable.\n\nMme Costa : Pour la famille en suroccupation, attribuer le T5 libérerait un T3 pour une autre famille.\n\nM. Hamon : C'est un argument, mais la famille à l'hôtel n'a pas de logement du tout. Je propose rang 1 au dossier 2026-0602 et rang 2 au dossier 2025-1980. Je propose aussi que le service propose en priorité à la famille 2025-1980 le prochain T5 ou T4 qui se libérera.\n\nMme Rivière : Je suis d'accord avec le classement, mais la priorité pour le prochain logement, on ne peut pas la voter ce soir, ce n'est pas un logement à l'ordre du jour.\n\nM. Hamon : Vous avez raison. Je retire cette partie : c'est une simple demande au service, pas une décision de la commission. Je mets aux voix le classement : rang 1 au dossier 2026-0602, rang 2 au dossier 2025-1980. Qui est pour ? Unanimité. Madame Salmon, vous pourrez signaler la famille 2025-1980 au service pour les prochains logements ?\n\nMme Salmon : Oui, je mets une alerte dans son dossier dès aujourd'hui.\n\nMme Salmon : Huitième logement : un T3 de 66 mètres carrés au rez-de-chaussée, rue du Port, à Lanvallay. Loyer de 402 euros, charges de 81 euros. Trois candidats. Dossier n° 2026-0144 : un couple avec un enfant de 5 ans, revenus de 2 020 euros, locataire d'un T2 du parc privé humide, avec un certificat médical pour l'asthme de l'enfant. Demande depuis 12 mois. Ce ménage a refusé deux propositions de l'office cette année, l'une parce que le logement était trop loin de l'école de l'enfant, l'autre parce qu'il était au cinquième étage sans ascenseur. Dossier n° 2026-0377 : une femme de 41 ans avec deux enfants, séparée, revenus de 1 560 euros, hébergée chez ses parents. Demande depuis 8 mois. Dossier n° 2026-0512 : un homme de 52 ans, seul, revenus de 1 380 euros.\n\nM. Gaudin : Deux refus en un an, c'est beaucoup. On ne risque pas un troisième refus ?\n\nMme Le Meur : Les deux refus étaient motivés. Un cinquième étage sans ascenseur avec un enfant asthmatique et une poussette, ce n'est pas un caprice.\n\nMme Bréhier : Je précise que les refus antérieurs ne sont pas, en eux-mêmes, un motif pour écarter un candidat. La commission apprécie la situation actuelle.\n\nMme Salmon : J'ajoute que l'école de l'enfant est à 300 mètres du logement de la rue du Port. J'ai appelé la famille hier, elle est très intéressée.\n\nM. Hamon : Pour le dossier 2026-0512, un T3 pour une personne seule serait en sous-occupation dès l'entrée dans les lieux. Je propose donc : rang 1 au dossier 2026-0144, rang 2 au dossier 2026-0377, et non-attribution au dossier 2026-0512, au motif de l'inadéquation de la typologie du logement à la composition du ménage. Qui est d'accord ? Mme Rivière, Mme Le Meur, Mme Costa et moi-même. Monsieur Gaudin ?\n\nM. Gaudin : Je m'abstiens.\n\nM. Hamon : Le classement est adopté par 4 voix pour et 1 abstention.\n\nMme Salmon : Neuvième logement : un T2 de 45 mètres carrés au deuxième étage avec ascenseur, résidence Saint-Sauveur, à Dinan. Loyer de 301 euros, charges de 64 euros. Trois candidats. Dossier n° 2026-0231 : une femme de 37 ans, travailleuse handicapée, en emploi à temps partiel dans un établissement et service d'aide par le travail, revenus de 1 120 euros, qui vit chez sa mère. Dossier n° 2026-0298 : un jeune couple de 23 et 25 ans, revenus de 2 240 euros, demande depuis 7 mois. Dossier n° 2026-0315 : un retraité de 69 ans, revenus de 1 310 euros, actuellement locataire de l'office dans un T3, qui a une dette de loyer de 640 euros, avec un plan d'apurement signé en juin et respecté depuis.\n\nMme Rivière : La dette n'empêche pas l'attribution ?\n\nMme Bréhier : Non, pas quand le plan d'apurement est respecté. L'office regarde la régularité des paiements depuis la signature du plan. Ici, les cinq échéances ont été payées.\n\nMme Costa : Pour la candidate travailleuse handicapée, l'établissement qui l'emploie est à dix minutes à pied de la résidence. Ce serait une vraie autonomie pour elle.\n\nM. Hamon : Je propose rang 1 au dossier 2026-0231, rang 2 au dossier 2026-0315, rang 3 au dossier 2026-0298. Qui est d'accord ? Unanimité.\n\nMme Salmon : Dixième et dernier logement : un T4 de 77 mètres carrés au quatrième étage sans ascenseur, quartier de la Fontaine-des-Eaux, à Dinan. Loyer de 498 euros, charges de 109 euros. Trois candidats. Dossier n° 2026-0089 : une famille de cinq personnes dont un enfant en fauteuil roulant, revenus de 2 640 euros. Dossier n° 2026-0402 : un couple avec deux enfants, revenus de 1 290 euros, sans aide au logement possible car l'un des conjoints n'a pas encore de titre de séjour à jour. Dossier n° 2026-0466 : un couple avec deux adolescents, revenus de 2 380 euros, locataire du parc privé dont le bail a été résilié pour vente.\n\nMme Le Meur : Pour la famille avec l'enfant en fauteuil, un quatrième étage sans ascenseur, ce n'est pas possible.\n\nMme Salmon : Je suis d'accord. Je l'ai présentée parce qu'elle était en tête de l'ancienneté sur ce secteur, mais le logement ne convient pas. Pour le dossier 2026-0402, sans aide au logement, le taux d'effort serait de 47 %. C'est très élevé.\n\nM. Hamon : Je propose donc : rang 1 au dossier 2026-0466 ; non-attribution au dossier 2026-0089, au motif de l'inadaptation du logement au handicap de l'enfant ; et non-attribution au dossier 2026-0402, au motif d'un taux d'effort trop élevé, avec une demande au service de présenter de nouveau la famille quand sa situation administrative sera régularisée. Qui est d'accord ? Unanimité.\n\nMme Costa : Pour la famille 2026-0089, il faudrait vraiment chercher un logement adapté.\n\nMme Salmon : Je la signale au service des logements adaptés, en même temps que la famille 2025-1980, dès aujourd'hui.\n\nM. Hamon : Nous passons maintenant à l'examen de l'occupation des logements. Je rappelle que, dans les zones tendues, la commission examine tous les trois ans la situation de certains locataires : suroccupation, sous-occupation, départ d'un occupant d'un logement adapté, reconnaissance d'un handicap ou dépassement des plafonds de ressources. La commission constate la situation et définit les caractéristiques d'un logement adapté. Elle ne prend pas de décision d'expulsion ni de résiliation du bail.\n\nMme Salmon : Premier dossier d'examen : une locataire de 81 ans, seule depuis le décès de son mari, qui occupe un T4 de 79 mètres carrés à la résidence Les Champs-Garel, au troisième étage sans ascenseur. Elle a fait savoir qu'elle avait de plus en plus de mal à monter les escaliers.\n\nMme Le Meur : Il faut faire très attention, cette dame vit là depuis 40 ans.\n\nM. Hamon : La commission constate une sous-occupation et une inadaptation du logement à la situation de la locataire. Elle propose que le service lui présente un logement de type T2, en rez-de-chaussée ou avec ascenseur, dans le même quartier si possible. La locataire reste libre d'accepter ou de refuser. Qui est d'accord ? Unanimité. Madame Bréhier, qui la rencontre ?\n\nMme Bréhier : La conseillère sociale de l'office, Mme Prigent, prendra rendez-vous avec elle à domicile avant le vendredi 11 décembre.\n\nMme Salmon : Second dossier d'examen : une famille de quatre personnes dans un T2 rue Victor-Hugo, soit une situation de suroccupation. La famille a déjà une demande de mutation enregistrée.\n\nM. Hamon : La commission constate la suroccupation et définit le logement adapté : un T4 au minimum. La demande de mutation sera présentée en priorité lors des prochaines commissions. Unanimité.\n\nMme Rivière : Monsieur le président, une question hors ordre du jour : est-ce qu'on a des nouvelles du projet de résidence pour personnes âgées à Quévert ?\n\nM. Hamon : Le conseil d'administration n'a pris aucune décision sur ce projet. L'étude de besoins est en cours. Ce n'est pas du ressort de la commission d'attribution, et nous n'en parlerons pas davantage aujourd'hui.\n\nM. Hamon : Avant de conclure, je rappelle les suites à donner. Madame Salmon, les notifications aux candidats retenus en rang 1 partent quand ?\n\nMme Salmon : Les propositions de logement seront envoyées aux candidats en rang 1 avant le lundi 23 novembre. Ils ont 10 jours pour répondre. Les candidats non retenus et le candidat rejeté recevront un courrier motivé avant le vendredi 27 novembre.\n\nM. Hamon : Et pour la condition suspensive du dossier 2026-0198 ?\n\nMme Salmon : Je lui écris demain, jeudi 19 novembre, pour lui demander l'avis d'imposition. Le délai de 10 jours court à partir de la réception du courrier.\n\nM. Hamon : Madame Bréhier, le procès-verbal ?\n\nMme Bréhier : Il sera envoyé aux membres de la commission avant le mercredi 2 décembre, avec l'avis de la commune de Taden sur le troisième logement, comme demandé par M. Botrel.\n\nM. Hamon : La prochaine commission aura lieu le mercredi 16 décembre à 14 heures. Le logement de la rue des Rosiers y sera présenté, si les travaux sont terminés. Je vous remercie. La séance est levée à 16 h 20.",
  "nb_mots": 4020
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Transcription fictive rédigée pour l'évaluation (collectivité, personnes et chiffres imaginaires)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "type_reunion": "commission d'attribution des logements et d'examen de l'occupation des logements (CALEOL)",
 "participants_reference": [
  "M. Hamon (président de la commission, administrateur de l'office)",
  "Mme Rivière et M. Gaudin (administrateurs de l'office)",
  "Mme Le Meur (administratrice représentant les locataires)",
  "Mme Costa (représentante de l'association d'insertion La Passerelle)",
  "M. Botrel (adjoint au maire de Taden, voix délibérative pour les logements de Taden, présent jusqu'au quatrième logement)",
  "Mme Salmon (chargée de clientèle, présente les dossiers) et Mme Bréhier (responsable de la gestion locative, secrétariat), voix consultative",
  "Excusé : M. Fournier (intercommunalité) ; représentant du préfet absent"
 ],
 "decisions_reference": [
  "Logement 1 (T3, Les Champs-Garel) : rang 1 au dossier 2026-0388 (prioritaire DALO), rang 2 au dossier 2026-0102 ; dossier 2025-1841 rejeté pour dépassement du plafond de ressources (unanimité)",
  "Logement 2 (T2 adapté, rue Victor-Hugo) : rang 1 au dossier 2025-1207, sans autre rang ; non-attribution aux dossiers 2026-0455 et 2026-0521, logement réservé à une personne à mobilité réduite (unanimité)",
  "Logement 3 (T4, maison rue des Châtaigniers, Taden) : rang 1 au dossier 2026-0400, rang 2 au dossier 2026-0347, rang 3 au dossier 2026-0310 (5 pour, 1 contre : M. Botrel, dont l'avis est noté au procès-verbal)",
  "Logement 4 (T2, résidence du Bourg, Taden) : rang 1 au dossier 2026-0478, rang 2 au dossier 2026-0490 (unanimité), insuffisance de candidatures constatée",
  "Logement 5 (T1 bis, place Duclos) : rang 1 au dossier 2026-0533, rang 2 au dossier 2026-0284, rang 3 au dossier 2026-0561 (unanimité des 4 votants, Mme Costa ne prenant pas part au vote)",
  "Logement 6 (T3, rue de Brest, loyer de 389 euros) : rang 1 au dossier 2026-0157, rang 2 au dossier 2026-0266, rang 3 au dossier 2026-0198 sous condition suspensive de l'avis d'imposition dans un délai de 10 jours (unanimité)",
  "Logement 7 (T5, Fontaine-des-Eaux) : rang 1 au dossier 2026-0602, rang 2 au dossier 2025-1980 (unanimité)",
  "Logement 8 (T3, rue du Port, Lanvallay) : rang 1 au dossier 2026-0144, rang 2 au dossier 2026-0377, non-attribution au dossier 2026-0512 pour inadéquation de la typologie (4 pour, 1 abstention : M. Gaudin)",
  "Logement 9 (T2, résidence Saint-Sauveur) : rang 1 au dossier 2026-0231, rang 2 au dossier 2026-0315, rang 3 au dossier 2026-0298 (unanimité)",
  "Logement 10 (T4 au quatrième étage sans ascenseur, Fontaine-des-Eaux) : rang 1 au dossier 2026-0466 ; non-attribution au dossier 2026-0089 (logement inadapté au handicap de l'enfant) et au dossier 2026-0402 (taux d'effort trop élevé) (unanimité)",
  "Examen de l'occupation : sous-occupation et inadaptation constatées pour la locataire de 81 ans (T4 sans ascenseur), proposition d'un T2 en rez-de-chaussée ou avec ascenseur, la locataire restant libre de refuser (unanimité)",
  "Examen de l'occupation : suroccupation constatée pour la famille de quatre personnes en T2, logement adapté défini comme un T4 au minimum, mutation présentée en priorité (unanimité)",
  "Prochaine commission le mercredi 16 décembre à 14 heures"
 ],
 "actions_reference": [
  {
   "action": "Envoyer les propositions de logement aux candidats en rang 1",
   "responsable": "Mme Salmon",
   "echeance": "avant le lundi 23 novembre"
  },
  {
   "action": "Envoyer un courrier motivé aux candidats non retenus et au candidat rejeté",
   "responsable": "Mme Salmon",
   "echeance": "avant le vendredi 27 novembre"
  },
  {
   "action": "Demander l'avis d'imposition au dossier 2026-0198",
   "responsable": "Mme Salmon",
   "echeance": "jeudi 19 novembre"
  },
  {
   "action": "Mettre une alerte dans le dossier 2025-1980 pour les prochains T4 ou T5",
   "responsable": "Mme Salmon",
   "echeance": "dès le mercredi 18 novembre (jour de la séance)"
  },
  {
   "action": "Signaler la famille 2026-0089 au service des logements adaptés",
   "responsable": "Mme Salmon",
   "echeance": "dès le mercredi 18 novembre (jour de la séance)"
  },
  {
   "action": "Rencontrer à domicile la locataire de 81 ans",
   "responsable": "Mme Prigent (conseillère sociale de l'office)",
   "echeance": "avant le vendredi 11 décembre"
  },
  {
   "action": "Envoyer le procès-verbal aux membres, avec l'avis de la commune de Taden",
   "responsable": "Mme Bréhier",
   "echeance": "avant le mercredi 2 décembre"
  }
 ],
 "pieges": [
  "Le logement de la rue des Rosiers a été retiré de l'ordre du jour : dix logements examinés sur onze prévus",
  "Les deux refus antérieurs du dossier 2026-0144 ne sont pas un motif d'exclusion",
  "La dette du dossier 2026-0315 n'empêche pas l'attribution (plan d'apurement respecté)",
  "Dossier 2026-0402 : non-attribution liée au taux d'effort (47 %), pas un rejet définitif",
  "Logement de la rue de Brest : loyer de 389 euros et non 398 euros",
  "La commune de Taden voulait le rang 1 pour son agent (dossier 2026-0310) : classé en rang 3",
  "Le dossier 2026-0219 (mutation) n'est pas classé pour la maison de Taden",
  "Priorité pour la famille 2025-1980 sur le prochain T5 ou T4 : retirée, simple demande au service, pas une décision",
  "Le reste à vivre de 12 euros est un repère, pas un critère d'exclusion",
  "La cotation de la demande aide à présenter les candidats mais ne remplace pas la décision de la commission",
  "Bilan du troisième trimestre (54 attributions) : présenté pour information, sans vote",
  "L'examen de l'occupation ne décide ni expulsion ni résiliation du bail",
  "Résidence pour personnes âgées de Quévert : aucune décision, hors du ressort de la commission",
  "Mme Costa n'a pas voté pour le logement 5",
  "M. Botrel n'a voté que pour les logements de Taden"
 ]
}
```

## CT-601 — Courrier type (facile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CT-601",
 "tache": "Courrier type",
 "difficulte": "facile",
 "theme": "collectivites",
 "entree": {
  "type": "accusé de réception",
  "objet": "Demande de location de la salle polyvalente pour un mariage",
  "elements_connus": {
   "expediteur": "mairie, service de la vie locale",
   "demandeur": "Mme Inès Garnier",
   "date_reception": "mardi 13 octobre 2026",
   "date_souhaitee": "samedi 19 juin 2027",
   "suite_donnee": "la demande sera examinée selon l'ordre d'arrivée des réservations ; une réponse écrite sera adressée avec le contrat de location si la salle est disponible"
  },
  "consigne": "Rédige l'accusé de réception de cette demande au format administratif français. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse de la demandeuse], [Commune], [Date du courrier], [Référence du dossier], [Téléphone et courriel du service], [Nom et qualité du signataire]."
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Demande d'agent rédigée pour l'évaluation (scénario fictif)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "type_courrier": "accusé de réception",
 "elements_obligatoires": [
  "En-tête de l'expéditeur (mairie, service de la vie locale)",
  "Bloc destinataire (Mme Inès Garnier)",
  "Lieu et date (en emplacement)",
  "Objet",
  "Référence du dossier (en emplacement)",
  "Formule d'appel « Madame, »",
  "Date de réception de la demande : mardi 13 octobre 2026",
  "Date souhaitée : samedi 19 juin 2027",
  "Examen selon l'ordre d'arrivée des réservations ; réponse écrite avec contrat de location si la salle est disponible",
  "Coordonnées du service (en emplacement)",
  "Formule de politesse",
  "Signature : nom et qualité du signataire (en emplacement)"
 ],
 "champs_a_laisser_en_emplacement": [
  "[Adresse de la demandeuse]",
  "[Commune]",
  "[Date du courrier]",
  "[Référence du dossier]",
  "[Téléphone et courriel du service]",
  "[Nom et qualité du signataire]"
 ],
 "valeurs_interdites": [
  "toute confirmation de réservation (la disponibilité n'est pas encore vérifiée)",
  "tout tarif de location inventé",
  "toute adresse, tout numéro de téléphone ou courriel inventé",
  "tout nom de signataire inventé"
 ]
}
```

## CT-605 — Courrier type (facile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CT-605",
 "tache": "Courrier type",
 "difficulte": "facile",
 "theme": "social-autonomie",
 "entree": {
  "type": "accusé de réception",
  "objet": "Demande de téléassistance",
  "elements_connus": {
   "expediteur": "le CCAS de la commune",
   "demandeur": "Mme Odette Rivière",
   "date_reception": "lundi 2 novembre 2026",
   "suite_donnee": "une conseillère du CCAS prendra contact avec elle pour fixer une visite à domicile avant l'installation du boîtier"
  },
  "consigne": "Rédige l'accusé de réception de cette demande au format administratif français. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse de la demandeuse], [Commune], [Date du courrier], [Référence du dossier], [Téléphone et courriel du CCAS], [Nom et qualité du signataire]."
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Demande d'agent rédigée pour l'évaluation (scénario fictif)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "type_courrier": "accusé de réception",
 "elements_obligatoires": [
  "En-tête de l'expéditeur (CCAS)",
  "Bloc destinataire (Mme Odette Rivière)",
  "Lieu et date (en emplacement)",
  "Objet",
  "Référence du dossier (en emplacement)",
  "Formule d'appel « Madame, »",
  "Date de réception de la demande : lundi 2 novembre 2026",
  "Prise de contact par une conseillère du CCAS pour fixer une visite à domicile avant l'installation",
  "Coordonnées du CCAS (en emplacement)",
  "Formule de politesse",
  "Signature : nom et qualité du signataire (en emplacement)"
 ],
 "champs_a_laisser_en_emplacement": [
  "[Adresse de la demandeuse]",
  "[Commune]",
  "[Date du courrier]",
  "[Référence du dossier]",
  "[Téléphone et courriel du CCAS]",
  "[Nom et qualité du signataire]"
 ],
 "valeurs_interdites": [
  "toute date de visite ou d'installation inventée",
  "tout tarif d'abonnement inventé",
  "toute adresse, tout numéro de téléphone ou courriel inventé",
  "tout nom de signataire inventé"
 ]
}
```

## CT-609 — Courrier type (moyen, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CT-609",
 "tache": "Courrier type",
 "difficulte": "moyen",
 "theme": "collectivites",
 "entree": {
  "type": "accusé de réception",
  "objet": "Demande d'autorisation de stationnement d'un camion de déménagement reçue par courriel",
  "elements_connus": {
   "expediteur": "mairie, service de la police municipale",
   "demandeur": "M. Lucas Perrin",
   "date_reception": "lundi 16 novembre 2026, par courriel, après identification sur le portail de la commune",
   "objet_demande": "stationnement d'un camion de déménagement devant le 12 rue Pasteur, le samedi 5 décembre 2026",
   "suite_donnee": "la demande est traitée par le service ; l'arrêté de stationnement sera transmis par courriel",
   "texte_applicable": "CRPA, Article L112-8 : « Toute personne, dès lors qu'elle s'est identifiée préalablement auprès d'une administration, peut, dans des conditions déterminées par décret en Conseil d'Etat, adresser à celle-ci, par voie électronique, une demande, une déclaration, un document ou une information, ou lui répondre par la même voie. Cette administration est régulièrement saisie et traite la demande, la déclaration, le document ou l'information sans lui demander la confirmation ou la répétition de son envoi sous une autre forme. »"
  },
  "consigne": "Rédige l'accusé de réception de cette demande au format administratif français, en respectant l'article fourni. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse du demandeur], [Commune], [Date du courrier], [Référence de la demande], [Téléphone et courriel du service], [Nom et qualité du signataire]."
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Demande d'agent rédigée pour l'évaluation (scénario fictif)"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/legi, code des relations entre le public et l'administration, article L112-8",
   "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031367348",
   "type": "legi",
   "code": "legi_code_des_relations_entre_le_public_et_l_administration",
   "articles": [
    "L112-8"
   ],
   "legiarti": "LEGIARTI000031367348",
   "depot": "AgentPublic/legi",
   "revision": "68b01fbbe0cdaf5fe7b8a6befe4b8acab41530f8",
   "role": "base réglementaire du courrier"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce. Articles cités : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face).",
 "fictif": true,
 "version_item": 1,
 "type_courrier": "accusé de réception",
 "elements_obligatoires": [
  "En-tête de l'expéditeur (mairie, police municipale)",
  "Bloc destinataire (M. Lucas Perrin)",
  "Lieu et date (en emplacement)",
  "Objet",
  "Référence de la demande (en emplacement)",
  "Formule d'appel « Monsieur, »",
  "Réception de la demande par courriel le lundi 16 novembre 2026",
  "Objet : stationnement d'un camion devant le 12 rue Pasteur, le samedi 5 décembre 2026",
  "La demande envoyée par voie électronique est traitée sans exiger de confirmation sous une autre forme (article L. 112-8 du CRPA)",
  "Transmission de l'arrêté de stationnement par courriel",
  "Coordonnées du service (en emplacement)",
  "Formule de politesse",
  "Signature : nom et qualité du signataire (en emplacement)"
 ],
 "champs_a_laisser_en_emplacement": [
  "[Adresse du demandeur]",
  "[Commune]",
  "[Date du courrier]",
  "[Référence de la demande]",
  "[Téléphone et courriel du service]",
  "[Nom et qualité du signataire]"
 ],
 "valeurs_interdites": [
  "toute demande de renvoyer la demande par courrier papier ou de la confirmer",
  "toute autorisation déjà accordée",
  "tout montant de redevance inventé",
  "toute adresse, tout numéro de téléphone ou courriel inventé",
  "tout nom de signataire inventé"
 ],
 "base_reglementaire": {
  "article": "CRPA L. 112-8",
  "legiarti": "LEGIARTI000031367348",
  "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031367348",
  "texte": "Article L112-8 : « Toute personne, dès lors qu'elle s'est identifiée préalablement auprès d'une administration, peut, dans des conditions déterminées par décret en Conseil d'Etat, adresser à celle-ci, par voie électronique, une demande, une déclaration, un document ou une information, ou lui répondre par la même voie. Cette administration est régulièrement saisie et traite la demande, la déclaration, le document ou l'information sans lui demander la confirmation ou la répétition de son envoi sous une autre forme. »",
  "extrait": "article(s) complet(s), texte verbatim, fourni à l'Assistant dans elements_connus.texte_applicable"
 }
}
```

## CT-611 — Courrier type (moyen, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CT-611",
 "tache": "Courrier type",
 "difficulte": "moyen",
 "theme": "social-autonomie",
 "entree": {
  "type": "réponse d'information",
  "objet": "Question sur la prise en charge des frais d'un séjour en Ehpad",
  "elements_connus": {
   "expediteur": "le CCAS de la commune",
   "demandeur": "Mme Martine Lebrun, pour sa mère, Mme Jeanne Lebrun",
   "informations_du_service": "si les ressources de sa mère ne suffisent pas à payer les frais d'hébergement en Ehpad, une demande d'aide sociale à l'hébergement peut être déposée ; le dossier est retiré et déposé au CCAS de la commune de résidence, qui le transmet au conseil départemental ; c'est le président du conseil départemental qui décide",
   "rendez_vous": "une conseillère du CCAS peut l'aider à constituer le dossier sur rendez-vous"
  },
  "consigne": "Rédige la réponse à ce courrier au format administratif français. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse de la demandeuse], [Commune], [Date du courrier], [Téléphone et courriel du CCAS], [Nom et qualité du signataire]."
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Demande d'agent rédigée pour l'évaluation (scénario fictif)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "type_courrier": "réponse d'information",
 "elements_obligatoires": [
  "En-tête de l'expéditeur (CCAS)",
  "Bloc destinataire (Mme Martine Lebrun)",
  "Lieu et date (en emplacement)",
  "Objet",
  "Formule d'appel « Madame, »",
  "Rappel de la question (frais d'Ehpad de sa mère, Mme Jeanne Lebrun)",
  "Possibilité d'une demande d'aide sociale à l'hébergement si les ressources ne suffisent pas",
  "Dossier retiré et déposé au CCAS de la commune de résidence, transmis au conseil départemental",
  "Décision du président du conseil départemental",
  "Aide possible d'une conseillère du CCAS sur rendez-vous",
  "Coordonnées du CCAS (en emplacement)",
  "Formule de politesse",
  "Signature : nom et qualité du signataire (en emplacement)"
 ],
 "champs_a_laisser_en_emplacement": [
  "[Adresse de la demandeuse]",
  "[Commune]",
  "[Date du courrier]",
  "[Téléphone et courriel du CCAS]",
  "[Nom et qualité du signataire]"
 ],
 "valeurs_interdites": [
  "toute décision d'attribution ou tout montant d'aide",
  "toute condition de ressources chiffrée inventée",
  "toute mention d'obligation alimentaire non fournie",
  "toute adresse, tout numéro de téléphone ou courriel inventé",
  "tout nom de signataire inventé"
 ]
}
```

## CT-617 — Courrier type (difficile, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CT-617",
 "tache": "Courrier type",
 "difficulte": "difficile",
 "theme": "famille-education-sante",
 "entree": {
  "type": "réponse d'information",
  "objet": "Question sur un recours gracieux contre un refus de dérogation scolaire",
  "elements_connus": {
   "expediteur": "mairie, service enfance et scolarité",
   "demandeurs": "M. Olivier Masson et Mme Sophie Masson",
   "decision": "refus de dérogation au secteur scolaire pour leur fils, notifié le mardi 3 novembre 2026",
   "question": "peuvent-ils demander au maire de réexaminer sa décision, et cela les empêche-t-il ensuite de saisir le tribunal administratif",
   "information": "ils peuvent former un recours gracieux auprès du maire dans le délai de recours contentieux de deux mois ; ce recours interrompt le délai du recours contentieux",
   "texte_applicable": "CRPA, Article L411-2 : « Toute décision administrative peut faire l'objet, dans le délai imparti pour l'introduction d'un recours contentieux, d'un recours gracieux ou hiérarchique qui interrompt le cours de ce délai.Lorsque dans le délai initial du recours contentieux ouvert à l'encontre de la décision, sont exercés contre cette décision un recours gracieux et un recours hiérarchique, le délai du recours contentieux, prorogé par l'exercice de ces recours administratifs, ne recommence à courir à l'égard de la décision initiale que lorsqu'ils ont été l'un et l'autre rejetés. »"
  },
  "consigne": "Rédige la réponse à ce courrier au format administratif français, en respectant l'article fourni. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse des demandeurs], [Commune], [Date du courrier], [Référence du dossier], [Téléphone et courriel du service], [Nom et qualité du signataire]."
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Demande d'agent rédigée pour l'évaluation (scénario fictif)"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/legi, code des relations entre le public et l'administration, article L411-2",
   "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031367829",
   "type": "legi",
   "code": "legi_code_des_relations_entre_le_public_et_l_administration",
   "articles": [
    "L411-2"
   ],
   "legiarti": "LEGIARTI000031367829",
   "depot": "AgentPublic/legi",
   "revision": "68b01fbbe0cdaf5fe7b8a6befe4b8acab41530f8",
   "role": "base réglementaire du courrier"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce. Articles cités : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face).",
 "fictif": true,
 "version_item": 1,
 "type_courrier": "réponse d'information",
 "elements_obligatoires": [
  "En-tête de l'expéditeur (mairie, service enfance et scolarité)",
  "Bloc destinataires (M. Olivier Masson et Mme Sophie Masson)",
  "Lieu et date (en emplacement)",
  "Objet",
  "Référence du dossier (en emplacement)",
  "Formule d'appel adressée aux deux parents (« Madame, Monsieur, »)",
  "Rappel de la décision de refus notifiée le mardi 3 novembre 2026",
  "Possibilité d'un recours gracieux auprès du maire, dans le délai de recours contentieux de deux mois",
  "Le recours gracieux interrompt le délai du recours contentieux, qui recommence à courir après son rejet (article L. 411-2 du CRPA)",
  "Le recours gracieux n'empêche pas de saisir ensuite le tribunal administratif",
  "Coordonnées du service (en emplacement)",
  "Formule de politesse",
  "Signature : nom et qualité du signataire (en emplacement)"
 ],
 "champs_a_laisser_en_emplacement": [
  "[Adresse des demandeurs]",
  "[Commune]",
  "[Date du courrier]",
  "[Référence du dossier]",
  "[Téléphone et courriel du service]",
  "[Nom et qualité du signataire]"
 ],
 "valeurs_interdites": [
  "toute appréciation sur les chances de succès du recours",
  "toute promesse de dérogation",
  "tout délai de réponse du maire inventé",
  "toute adresse, tout numéro de téléphone ou courriel inventé",
  "tout nom de signataire inventé"
 ],
 "base_reglementaire": {
  "article": "CRPA L. 411-2",
  "legiarti": "LEGIARTI000031367829",
  "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031367829",
  "texte": "Article L411-2 : « Toute décision administrative peut faire l'objet, dans le délai imparti pour l'introduction d'un recours contentieux, d'un recours gracieux ou hiérarchique qui interrompt le cours de ce délai.Lorsque dans le délai initial du recours contentieux ouvert à l'encontre de la décision, sont exercés contre cette décision un recours gracieux et un recours hiérarchique, le délai du recours contentieux, prorogé par l'exercice de ces recours administratifs, ne recommence à courir à l'égard de la décision initiale que lorsqu'ils ont été l'un et l'autre rejetés. »",
  "extrait": "article(s) complet(s), texte verbatim, fourni à l'Assistant dans elements_connus.texte_applicable"
 }
}
```

## CT-619 — Courrier type (difficile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CT-619",
 "tache": "Courrier type",
 "difficulte": "difficile",
 "theme": "social-autonomie",
 "entree": {
  "type": "accusé de réception",
  "objet": "Dossier complet de demande d'allocation personnalisée d'autonomie à domicile",
  "elements_connus": {
   "expediteur": "conseil départemental, direction de l'autonomie",
   "demandeur": "M. Henri Boucher",
   "date_depot_dossier_complet": "lundi 9 novembre 2026",
   "suite": "une équipe médico-sociale prendra contact avec lui pour une visite à domicile afin d'évaluer ses besoins et d'élaborer, le cas échéant, un plan d'aide",
   "delai": "le président du conseil départemental dispose de deux mois à compter du dépôt du dossier complet pour notifier sa décision ; à défaut, l'allocation est réputée accordée pour un montant forfaitaire fixé par décret, jusqu'à la notification de la décision expresse",
   "ouverture_des_droits": "à domicile, les droits sont ouverts à compter de la date de notification de la décision",
   "texte_applicable": "CASF, Article L232-14 : « Lorsqu'il n'y a pas lieu d'élaborer un plan d'aide, un compte rendu de visite comportant des conseils est établi. \nA domicile, les droits à l'allocation personnalisée d'autonomie sont ouverts à compter de la date de la notification de la décision du président du conseil départemental mentionnée au premier alinéa de l'article L. 232-12. \nDans les établissements visés respectivement au I et au II de l'article L. 313-12 en tant qu'ils ne dérogent pas aux règles mentionnées au 1° de l'article L. 314-2, les droits à l'allocation personnalisée d'autonomie sont ouverts à compter de la date du dépôt d'un dossier de demande complet. \nLe président du conseil départemental dispose d'un délai de deux mois à compter de la date du dépôt du dossier de demande complet pour notifier au bénéficiaire sa décision relative à l'allocation personnalisée d'autonomie. \nAu terme de ce délai, à défaut d'une notification, l'allocation personnalisée d'autonomie est réputée accordée pour un montant forfaitaire fixé par décret, à compter de la date d'ouverture des droits mentionnés aux deux alinéas précédents, jusqu'à ce que la décision expresse le concernant soit notifiée à l'intéressé. \nL'allocation personnalisée d'autonomie fait l'objet d'une révision périodique. Elle peut être révisée à tout moment en cas de modification de la situation du bénéficiaire. »"
  },
  "consigne": "Rédige l'accusé de réception de cette demande au format administratif français, en respectant l'article fourni. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse du demandeur], [Date du courrier], [Numéro de dossier], [Téléphone et courriel de la direction de l'autonomie], [Nom et qualité du signataire]."
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Demande d'agent rédigée pour l'évaluation (scénario fictif)"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/legi, code de l'action sociale et des familles, article L232-14",
   "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031727706",
   "type": "legi",
   "code": "legi_code_de_l_action_sociale_et_des_familles",
   "articles": [
    "L232-14"
   ],
   "legiarti": "LEGIARTI000031727706",
   "depot": "AgentPublic/legi",
   "revision": "68b01fbbe0cdaf5fe7b8a6befe4b8acab41530f8",
   "role": "base réglementaire du courrier"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce. Articles cités : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face).",
 "fictif": true,
 "version_item": 1,
 "type_courrier": "accusé de réception",
 "elements_obligatoires": [
  "En-tête de l'expéditeur (conseil départemental, direction de l'autonomie)",
  "Bloc destinataire (M. Henri Boucher)",
  "Lieu et date (date en emplacement)",
  "Objet",
  "Numéro de dossier (en emplacement)",
  "Formule d'appel « Monsieur, »",
  "Dossier complet déposé le lundi 9 novembre 2026",
  "Visite à domicile de l'équipe médico-sociale pour évaluer les besoins et élaborer, le cas échéant, un plan d'aide",
  "Délai de deux mois à compter du dépôt du dossier complet pour la décision du président du conseil départemental",
  "À défaut de notification dans ce délai, allocation réputée accordée pour un montant forfaitaire fixé par décret, jusqu'à la décision expresse (article L. 232-14 du CASF)",
  "À domicile, ouverture des droits à compter de la notification de la décision",
  "Coordonnées de la direction de l'autonomie (en emplacement)",
  "Formule de politesse",
  "Signature : nom et qualité du signataire (en emplacement)"
 ],
 "champs_a_laisser_en_emplacement": [
  "[Adresse du demandeur]",
  "[Date du courrier]",
  "[Numéro de dossier]",
  "[Téléphone et courriel de la direction de l'autonomie]",
  "[Nom et qualité du signataire]"
 ],
 "valeurs_interdites": [
  "tout montant d'allocation ou de forfait chiffré",
  "toute date de visite inventée",
  "toute mention que le silence vaut rejet",
  "toute adresse, tout numéro de téléphone ou courriel inventé",
  "tout nom de signataire inventé"
 ],
 "base_reglementaire": {
  "article": "CASF L. 232-14",
  "legiarti": "LEGIARTI000031727706",
  "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031727706",
  "texte": "Article L232-14 : « Lorsqu'il n'y a pas lieu d'élaborer un plan d'aide, un compte rendu de visite comportant des conseils est établi. \nA domicile, les droits à l'allocation personnalisée d'autonomie sont ouverts à compter de la date de la notification de la décision du président du conseil départemental mentionnée au premier alinéa de l'article L. 232-12. \nDans les établissements visés respectivement au I et au II de l'article L. 313-12 en tant qu'ils ne dérogent pas aux règles mentionnées au 1° de l'article L. 314-2, les droits à l'allocation personnalisée d'autonomie sont ouverts à compter de la date du dépôt d'un dossier de demande complet. \nLe président du conseil départemental dispose d'un délai de deux mois à compter de la date du dépôt du dossier de demande complet pour notifier au bénéficiaire sa décision relative à l'allocation personnalisée d'autonomie. \nAu terme de ce délai, à défaut d'une notification, l'allocation personnalisée d'autonomie est réputée accordée pour un montant forfaitaire fixé par décret, à compter de la date d'ouverture des droits mentionnés aux deux alinéas précédents, jusqu'à ce que la décision expresse le concernant soit notifiée à l'intéressé. \nL'allocation personnalisée d'autonomie fait l'objet d'une révision périodique. Elle peut être révisée à tout moment en cas de modification de la situation du bénéficiaire. »",
  "extrait": "article(s) complet(s), texte verbatim, fourni à l'Assistant dans elements_connus.texte_applicable"
 }
}
```

## LC-602 — Langage clair (facile, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "LC-602",
 "tache": "Langage clair",
 "difficulte": "facile",
 "theme": "etat-civil-papiers",
 "entree": {
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "texte": "Vous pouvez faire votre demande en ligne, par courrier ou sur place :\nCas En ligne: Vous pouvez faire la demande à l’aide de ce téléservice :\nCas Par courrier: Vous pouvez adresser votre demande par courrier auprès de la mairie du lieu du décès . Votre demande sur papier libre doit comprendre les nom et prénoms de la personne décédée, la date du décès et vos coordonnées pour recevoir l'acte chez vous. (À noter: Le délai peut varier en fonction du traitement de votre demande par les services de la mairie et du délai d'acheminement du courrier.)\nCas Sur place: Vous pouvez faire la demande sur place en vous rendant soit auprès de la mairie du lieu de décès, soit auprès de la mairie du dernier domicile de la personne décédée. Vous devrez indiquer au guichet les nom et prénoms de la personne décédée et la date du décès. Aucun document n'est exigé. L'acte de décès vous est remis immédiatement .",
  "nb_mots": 158
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F1444 « Acte de décès : demande de copie intégrale » (chunks 3)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1444",
   "type": "service-public",
   "doc_id": "F1444",
   "chunks": [
    3
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "informations_a_conserver": [
  "La demande d'acte de décès se fait en ligne, par courrier ou sur place",
  "Par courrier : à la mairie du lieu du décès, sur papier libre, avec les nom et prénoms du défunt, la date du décès et ses propres coordonnées ; le délai varie selon la mairie et le courrier",
  "Sur place : à la mairie du lieu du décès ou du dernier domicile du défunt, en indiquant ses nom et prénoms et la date du décès",
  "Sur place, aucun document n'est exigé et l'acte est remis immédiatement"
 ],
 "termes_juridiques_a_conserver": [
  "acte de décès",
  "papier libre"
 ],
 "kandel_moles_entree": 79.25,
 "version_texte": 1
}
```

## LC-605 — Langage clair (facile, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

```json
{
 "id": "LC-605",
 "tache": "Langage clair",
 "difficulte": "facile",
 "theme": "famille-education-sante",
 "entree": {
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "texte": "Contactez le service social du centre régional des œuvres universitaires et scolaires (Crous) dont vous dépendez pour effectuer votre demande. La demande d'aide d'urgence est examinée par une commission. La demande est présentée de façon anonyme. Si nécessaire, un entretien préalable peut avoir lieu avec un(e) assistant(e) social(e) du Crous. Il permet d'évaluer votre situation globale, au regard notamment de votre parcours universitaire et des difficultés que vous rencontrez. Après examen du dossier, la commission émet un avis d'attribution ou de refus d'attribution d'aide et propose au directeur du Crous un montant. Le directeur du Crous décide du montant final de l'aide. Si vous souhaitez contester une décision vous concernant, vous pouvez faire un recours gracieux auprès du directeur du Crous.",
  "nb_mots": 121
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F1024 « Allocation spécifique annuelle pour étudiant en difficulté » (chunks 3)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1024",
   "type": "service-public",
   "doc_id": "F1024",
   "chunks": [
    3
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "informations_a_conserver": [
  "La demande se fait auprès du service social du Crous dont dépend l'étudiant",
  "La demande d'aide d'urgence est examinée par une commission, de façon anonyme",
  "Un entretien préalable avec un assistant social du Crous peut avoir lieu pour évaluer la situation globale (parcours universitaire, difficultés)",
  "La commission donne un avis d'attribution ou de refus et propose un montant ; le directeur du Crous décide du montant final",
  "Pour contester une décision, on peut faire un recours gracieux auprès du directeur du Crous"
 ],
 "termes_juridiques_a_conserver": [
  "Crous",
  "recours gracieux"
 ],
 "kandel_moles_entree": 57.83,
 "version_texte": 1
}
```

## LC-609 — Langage clair (moyen, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "LC-609",
 "tache": "Langage clair",
 "difficulte": "moyen",
 "theme": "etat-civil-papiers",
 "entree": {
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "texte": "L’erreur matérielle dans un acte de l’état civil est une simple erreur de forme ou un oubli. Exemples : erreur sur un nom mal orthographié, erreur dans la date de naissance, erreur sur le domicile, erreur sur la profession. Connaître la procédure de rectification pour un acte de naissance comportant un double tiret entre les 2 noms de famille d'un enfant: Vous pouvez demander la rectification d'un acte de naissance qui comporte un double tiret entre les 2 noms de famille d'un enfant. Après correction, une rubrique est ajoutée après le double nom, sous la forme suivante : (1re partie : ... 2nde partie : ....). Exemple : le double nom Jérémy DUBOIS -- DURAND devient, après correction : DUBOIS DURAND (1ère partie : DUBOIS 2nde partie : DURAND ).\nPréparez les documents suivants :\n- Demande sur papier libre ou sur le formulaire cerfa n°11531 . Une notice, jointe au formulaire, est à lire avant de le remplir.\n- Copie(s) intégrale(s) des actes de l'état civil à rectifier datant de moins de 3 mois\n- Copie intégrale d'un acte sans erreur ou copie de tout document justifiant la rectification. Par exemple, l'acte de naissance d'une personne mariée dont le nom est mal orthographié sur l'acte de mariage.\n- Copie d’un document d'identité. Par exemple, carte nationale d'identité, passeport.\nEn fonction de votre situation, des documents complémentaires pourront vous être demandés. (À noter: Si l'erreur matérielle est contenue dans votre acte de naissance , vous devez d'abord obtenir la correction de cet acte . Par la suite, vous pourrez demander, si nécessaire, la rectification des autres actes de l'état civil .)",
  "nb_mots": 250
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F1177 « Comment corriger un acte d'état civil (erreur, oubli, coquille, double tiret) ? » (chunks 2, 3)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1177",
   "type": "service-public",
   "doc_id": "F1177",
   "chunks": [
    2,
    3
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "informations_a_conserver": [
  "Une erreur matérielle est une simple erreur de forme ou un oubli (nom mal orthographié, date de naissance, domicile, profession)",
  "On peut faire rectifier un acte de naissance qui comporte un double tiret entre les 2 noms de famille ; une rubrique « 1re partie / 2nde partie » est alors ajoutée (exemple DUBOIS -- DURAND devient DUBOIS DURAND)",
  "Documents : demande sur papier libre ou formulaire cerfa n° 11531 (lire la notice), copies intégrales de moins de 3 mois des actes à rectifier, copie d'un acte sans erreur ou d'un document justificatif, copie d'une pièce d'identité",
  "D'autres documents peuvent être demandés selon la situation",
  "Si l'erreur est dans l'acte de naissance, il faut d'abord faire corriger cet acte, puis les autres actes si nécessaire"
 ],
 "termes_juridiques_a_conserver": [
  "erreur matérielle",
  "acte de l'état civil",
  "rectification",
  "copie(s) intégrale(s)",
  "cerfa n°11531"
 ],
 "kandel_moles_entree": 70.19,
 "version_texte": 1
}
```

## LC-611 — Langage clair (moyen, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "LC-611",
 "tache": "Langage clair",
 "difficulte": "moyen",
 "theme": "collectivites",
 "entree": {
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "texte": "La déclaration doit indiquer les éléments suivants :\n- Nom de l'association, tel qu'il figure dans les statuts (250 caractères maximum), et le sigle, s'il en existe un\n- Objet, tel que les fondateurs souhaitent qu'il soit publié au JOAFE\n- Adresse du siège social (et l'adresse de gestion de l'association si elle est différente)\n- Date de l'assemblée lors de laquelle la création de l'association a été décidée\nLa déclaration doit être accompagnée des documents suivants :\n- Copie du procès-verbal de l'assemblée constitutive, signée par au moins un dirigeant, et comportant les nom et prénom du signataire\n- Exemplaire des statuts , daté et signé, par au moins 2 dirigeants et comportant leur nom, prénom et fonction au sein de l'association\n- Liste des dirigeants mentionnant leur nom, profession, domicile et nationalité\n- Liste des associations membres (en cas d'union ou de fédération d'associations)\n- Lorsque la démarche est accomplie par une personne mandatée, du mandat portant signature d'un dirigeant\n- Lorsque la démarche est accomplie par courrier, d'une enveloppe affranchie au tarif en vigueur (20 grammes) libellée au nom et à l'adresse de gestion\n(Attention: La déclaration peut être rejetée si une date de naissance apparaît sur les documents joints (statuts, procès-verbal, mandat). Cette information ne doit pas y figurer.)",
  "nb_mots": 200
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F1119 « Déclaration initiale d'une association » (chunks 2)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1119",
   "type": "service-public",
   "doc_id": "F1119",
   "chunks": [
    2
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "informations_a_conserver": [
  "La déclaration indique le nom de l'association tel que dans les statuts (250 caractères au plus) et le sigle éventuel, l'objet à publier au JOAFE, l'adresse du siège (et de gestion si différente) et la date de l'assemblée constitutive",
  "Documents joints : procès-verbal de l'assemblée constitutive signé par au moins un dirigeant (avec ses nom et prénom), statuts datés et signés par au moins 2 dirigeants (nom, prénom, fonction), liste des dirigeants (nom, profession, domicile, nationalité)",
  "Selon le cas : liste des associations membres (union ou fédération), mandat signé par un dirigeant si une personne mandatée fait la démarche, enveloppe affranchie (20 grammes) si la démarche se fait par courrier",
  "Aucune date de naissance ne doit figurer sur les documents joints, sinon la déclaration peut être rejetée"
 ],
 "termes_juridiques_a_conserver": [
  "déclaration",
  "statuts",
  "JOAFE",
  "siège social",
  "procès-verbal de l'assemblée constitutive",
  "mandat"
 ],
 "kandel_moles_entree": 61.12,
 "version_texte": 1
}
```

## LC-616 — Langage clair (difficile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "LC-616",
 "tache": "Langage clair",
 "difficulte": "difficile",
 "theme": "social-autonomie",
 "entree": {
  "consigne": "Réécris cet article en langage clair pour un usager, sans perdre d'information. Signale les termes juridiques que tu ne simplifies pas.",
  "texte": "L'exercice des droits et libertés individuels est garanti à toute personne accueillie et accompagnée par des établissements et services sociaux et médico-sociaux. Lui sont assurés :\n1° Le respect de sa dignité, de son intégrité, de sa vie privée et familiale, de son intimité, de sa sécurité et de son droit à aller et venir librement ;\n2° Sous réserve des pouvoirs reconnus à l'autorité judiciaire et des nécessités liées à la protection des mineurs en danger et des majeurs protégés, le libre choix entre les prestations adaptées qui lui sont offertes soit dans le cadre d'un service à son domicile, soit dans le cadre d'une admission au sein d'un établissement spécialisé ;\n3° Une prise en charge et un accompagnement individualisé de qualité favorisant son développement, son autonomie et son insertion, adaptés à son âge et à ses besoins, respectant son consentement éclairé qui doit systématiquement être recherché lorsque la personne est apte à exprimer sa volonté et à participer à la décision. A défaut, le consentement de son représentant légal s'il s'agit d'un mineur ou, s'il s'agit d'un majeur faisant l'objet d'une mesure de protection juridique avec représentation relative à la personne, de la personne chargée de cette mesure, qui tient compte de l'avis de la personne protégée, doit être recherché ;\n4° La confidentialité des informations la concernant ;\n5° L'accès à toute information ou document relatif à sa prise en charge, sauf dispositions législatives contraires ;\n6° Une information sur ses droits fondamentaux et les protections particulières légales et contractuelles dont elle bénéficie, ainsi que sur les voies de recours à sa disposition ;\n7° La participation directe de la personne prise en charge à la conception et à la mise en œuvre du projet d'accueil et d'accompagnement qui la concerne. Cette personne bénéficie de l'aide de son représentant légal, s'il s'agit d'un mineur ou, s'il s'agit d'un majeur faisant l'objet d'une mesure de protection juridique à la personne qui n'est pas apte à exprimer sa volonté, de la personne chargée de cette mesure, qui tient compte de son avis.",
  "nb_mots": 337
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/legi, Code de l'action sociale et des familles, article L311-3 (en vigueur depuis 2024-04-10)",
   "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000049391603",
   "type": "legi",
   "code": "legi_code_de_l_action_sociale_et_des_familles",
   "articles": [
    "L311-3"
   ],
   "legiarti": "LEGIARTI000049391603",
   "note": "URL construite à partir de l'identifiant LEGIARTI (Légifrance non consulté en lecture automatique)",
   "depot": "AgentPublic/legi",
   "revision": "68b01fbbe0cdaf5fe7b8a6befe4b8acab41530f8"
  }
 ],
 "licence_source": "Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face)",
 "fictif": false,
 "version_item": 2,
 "informations_a_conserver": [
  "Les droits et libertés individuels sont garantis à toute personne accueillie et accompagnée par un établissement ou service social ou médico-social",
  "Respect de sa dignité, de son intégrité, de sa vie privée et familiale, de son intimité, de sa sécurité et de son droit d'aller et venir librement",
  "Libre choix entre les prestations adaptées qui lui sont proposées, par un service à domicile ou par une admission dans un établissement spécialisé, sous réserve des pouvoirs de l'autorité judiciaire et des nécessités de la protection des mineurs en danger et des majeurs protégés",
  "Prise en charge et accompagnement individualisé de qualité, qui favorisent son développement, son autonomie et son insertion et sont adaptés à son âge et à ses besoins",
  "Recherche systématique de son consentement éclairé si elle est apte à exprimer sa volonté et à participer à la décision ; à défaut, recherche du consentement de son représentant légal (mineur) ou de la personne chargée de la mesure de protection juridique avec représentation relative à la personne (majeur), qui tient compte de l'avis de la personne protégée",
  "Confidentialité des informations la concernant",
  "Accès à toute information ou tout document sur sa prise en charge, sauf dispositions législatives contraires",
  "Information sur ses droits fondamentaux, sur les protections particulières légales et contractuelles dont elle bénéficie et sur les voies de recours à sa disposition",
  "Participation directe à la conception et à la mise en œuvre de son projet d'accueil et d'accompagnement, avec l'aide de son représentant légal (mineur) ou, pour un majeur sous mesure de protection juridique à la personne qui n'est pas apte à exprimer sa volonté, de la personne chargée de cette mesure, qui tient compte de son avis"
 ],
 "termes_juridiques_a_conserver": [
  "établissements et services sociaux et médico-sociaux",
  "autorité judiciaire",
  "majeurs protégés",
  "consentement éclairé",
  "représentant légal",
  "mesure de protection juridique",
  "voies de recours",
  "projet d'accueil et d'accompagnement"
 ],
 "kandel_moles_entree": 45.3,
 "version_texte": 1
}
```

## LC-617 — Langage clair (difficile, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "LC-617",
 "tache": "Langage clair",
 "difficulte": "difficile",
 "theme": "etat-civil-papiers",
 "entree": {
  "consigne": "Réécris cet article en langage clair pour un usager, sans perdre d'information. Signale les termes juridiques que tu ne simplifies pas.",
  "texte": "Les déclarations de naissance sont faites dans les cinq jours de l'accouchement, à l'officier de l'état civil du lieu. \nPar dérogation, ce délai est porté à huit jours lorsque l'éloignement entre le lieu de naissance et le lieu où se situe l'officier de l'état civil le justifie. Un décret en Conseil d'Etat détermine les communes où le présent alinéa s'applique. \nLorsqu'une naissance n'a pas été déclarée dans le délai légal, l'officier de l'état civil ne peut la relater sur ses registres qu'en vertu d'un jugement rendu par le tribunal de l'arrondissement dans lequel est né l'enfant, et mention sommaire en est faite en marge à la date de la naissance. Si le lieu de la naissance est inconnu, le tribunal compétent est celui du domicile du requérant. Le nom de l'enfant est déterminé en application des règles énoncées aux articles 311-21 et 311-23. \nEn pays étranger, les déclarations aux agents diplomatiques ou consulaires sont faites dans les quinze jours de l'accouchement. Toutefois, ce délai peut être prolongé par décret dans certaines circonscriptions consulaires.",
  "nb_mots": 173
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/legi, Code civil, article 55 (en vigueur depuis 2016-11-20)",
   "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033460908",
   "type": "legi",
   "code": "legi_code_civil",
   "articles": [
    "55"
   ],
   "legiarti": "LEGIARTI000033460908",
   "note": "URL construite à partir de l'identifiant LEGIARTI (Légifrance non consulté en lecture automatique)",
   "depot": "AgentPublic/legi",
   "revision": "68b01fbbe0cdaf5fe7b8a6befe4b8acab41530f8"
  }
 ],
 "licence_source": "Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face)",
 "fictif": false,
 "version_item": 1,
 "informations_a_conserver": [
  "La naissance est déclarée dans les 5 jours suivant l'accouchement à l'officier de l'état civil du lieu de naissance",
  "Ce délai passe à 8 jours quand l'éloignement le justifie, dans les communes fixées par décret en Conseil d'État",
  "Hors délai, la naissance ne peut être inscrite qu'en vertu d'un jugement du tribunal de l'arrondissement de naissance (ou du domicile du requérant si le lieu est inconnu), avec une mention en marge",
  "Le nom de l'enfant est alors déterminé selon les articles 311-21 et 311-23",
  "À l'étranger, la déclaration aux agents diplomatiques ou consulaires se fait dans les 15 jours, délai que peut prolonger un décret dans certaines circonscriptions"
 ],
 "termes_juridiques_a_conserver": [
  "déclarations de naissance",
  "officier de l'état civil",
  "décret en Conseil d'Etat",
  "jugement",
  "agents diplomatiques ou consulaires"
 ],
 "kandel_moles_entree": 60.82,
 "version_texte": 1
}
```

## NR-602 — Non-régression (facile, thème `non-classe`)

- [ ] Relu
- Remarques :

```json
{
 "id": "NR-602",
 "tache": "Non-régression",
 "difficulte": "facile",
 "theme": "non-classe",
 "entree": "Un électeur qui vit en France peut-il voter par internet aux élections politiques ? S'il sait qu'il sera absent le jour du vote, que peut-il faire ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F11257 « Peut-on voter par internet pour les élections politiques ? »",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F11257",
   "chunks": [
    1,
    2
   ],
   "extrait": "Voter par internet est uniquement possible si vous vivez à l'étranger et que vous votez depuis l'étranger pour certaines élections. […] Vous ne pouvez pas voter par internet. Pour voter, vous devez vous rendre dans votre bureau de vote avec un justificatif d'identité, le jour du vote. Mais si vous prévoyez d'être absent ce jour-là, vous pouvez faire une procuration de vote.",
   "role": "fiche de référence"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "sous_type": "question",
 "reponse_reference": "Non : en France, on ne peut pas voter par internet, il faut se rendre au bureau de vote avec un justificatif d'identité (le vote par internet n'est possible que depuis l'étranger, pour certaines élections). S'il sera absent, il peut faire une procuration pour qu'un autre électeur vote à sa place.",
 "criteres": [
  "Non, pas de vote par internet pour un électeur qui vote en France",
  "Il peut établir une procuration de vote",
  "Réponse en français correct"
 ]
}
```

## NR-605 — Non-régression (moyen, thème `non-classe`)

- [ ] Relu
- Remarques :

```json
{
 "id": "NR-605",
 "tache": "Non-régression",
 "difficulte": "moyen",
 "theme": "non-classe",
 "entree": "Pour combien d'années les conseillers régionaux et les conseillers départementaux sont-ils élus ? Aux élections régionales, quel score minimal une liste doit-elle avoir obtenu au 1er tour pour se présenter au 2nd tour ? Aux élections départementales, quel seuil un binôme doit-il atteindre pour participer au 2nd tour ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F1958 « Élections régionales et élections départementales (ex-cantonales) »",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1958",
   "chunks": [
    2,
    3
   ],
   "extrait": "Les conseillers régionaux sont élus pour une durée de 6 ans. […] Seules les listes qui ont obtenu au moins 10 % des suffrages exprimés lors du 1 er tour peuvent être candidates au 2 d tour. […] Les conseillers départementaux sont élus pour une durée de 6 ans. […] Seuls les binômes qui ont obtenu un nombre de suffrages au moins égal à 12,5 % des électeurs inscrits peuvent participer au 2 d tour.",
   "role": "fiche de référence"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "sous_type": "question",
 "reponse_reference": "Les conseillers régionaux et les conseillers départementaux sont élus pour 6 ans. Aux régionales, une liste doit avoir obtenu au moins 10 % des suffrages exprimés au 1er tour. Aux départementales, un binôme doit avoir obtenu un nombre de suffrages au moins égal à 12,5 % des électeurs inscrits.",
 "criteres": [
  "6 ans pour les deux mandats",
  "Régionales : au moins 10 % des suffrages exprimés au 1er tour",
  "Départementales : au moins 12,5 % des électeurs inscrits",
  "Réponse en français correct"
 ]
}
```

## NR-609 — Non-régression (difficile, thème `non-classe`)

- [ ] Relu
- Remarques :

```json
{
 "id": "NR-609",
 "tache": "Non-régression",
 "difficulte": "difficile",
 "theme": "non-classe",
 "entree": "Un couple propriétaire de la maison où il vit peut-il en principe obtenir un prêt à taux zéro (PTZ) pour acheter un autre logement ? Citez les cas d'exception mentionnés. Et une personne qui possède seulement une résidence secondaire, sans être propriétaire de sa résidence principale ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F1529 « A-t-on droit au PTZ quand on est déjà propriétaire d'un logement ? »",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1529",
   "chunks": [
    1,
    3
   ],
   "extrait": "Si vous êtes propriétaire de votre résidence principale , vous pouvez obtenir un PTZ dans certains cas seulement ( usufruitier ou nu-propriétaire de ce logement, handicap ou invalidité, logement détruit par une catastrophe naturelle...). Si vous possédez un autre logement, sans être propriétaire de votre résidence principale, vous pouvez obtenir un PTZ. […] Pour obtenir le PTZ, vous devez respecter les autres critères d'attribution du PTZ. Il faut, notamment, que vos ressources ne dépassent pas un montant maximum.",
   "role": "fiche de référence"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "sous_type": "question",
 "reponse_reference": "En principe non : le propriétaire de sa résidence principale ne peut obtenir un PTZ que dans certains cas (usufruitier ou nu-propriétaire de ce logement, handicap ou invalidité, logement détruit par une catastrophe naturelle…). Une personne qui possède une résidence secondaire sans être propriétaire de sa résidence principale peut obtenir un PTZ, à condition de respecter les autres critères, notamment un plafond de ressources.",
 "criteres": [
  "Propriétaire de sa résidence principale : PTZ seulement dans certains cas",
  "Cas cités : usufruitier ou nu-propriétaire, handicap ou invalidité, catastrophe naturelle",
  "Propriétaire d'une seule résidence secondaire : PTZ possible",
  "Sous réserve des autres critères, notamment le plafond de ressources",
  "Réponse en français correct"
 ]
}
```

## NR-613 — Non-régression (facile, thème `non-classe`)

- [ ] Relu
- Remarques :

```json
{
 "id": "NR-613",
 "tache": "Non-régression",
 "difficulte": "facile",
 "theme": "non-classe",
 "entree": "Réponds uniquement par « oui » ou par « non », en minuscules et sans aucun autre texte : la date du 31 avril existe-t-elle ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Consigne rédigée pour l'évaluation"
  }
 ],
 "licence_source": "Création originale du projet (contenu rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "sous_type": "consigne",
 "reponse_reference": "non",
 "criteres": [
  "Répond « non »",
  "Un seul mot, en minuscules, sans autre texte"
 ]
}
```

## NR-616 — Non-régression (moyen, thème `non-classe`)

- [ ] Relu
- Remarques :

```json
{
 "id": "NR-616",
 "tache": "Non-régression",
 "difficulte": "moyen",
 "theme": "non-classe",
 "entree": "Recopie le texte suivant en remplaçant chaque « CCAS » par « centre communal d'action sociale », sans rien changer d'autre et sans guillemets : Le CCAS de la commune ouvre une permanence le mardi. Les dossiers sont à déposer au CCAS avant le 30 novembre.",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Consigne rédigée pour l'évaluation"
  }
 ],
 "licence_source": "Création originale du projet (contenu rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "sous_type": "consigne",
 "reponse_reference": "Le centre communal d'action sociale de la commune ouvre une permanence le mardi. Les dossiers sont à déposer au centre communal d'action sociale avant le 30 novembre.",
 "criteres": [
  "Les deux occurrences de « CCAS » sont remplacées par « centre communal d'action sociale »",
  "Le reste du texte est recopié à l'identique",
  "Pas de guillemets ni d'autre texte"
 ]
}
```

## NR-618 — Non-régression (difficile, thème `non-classe`)

- [ ] Relu
- Remarques :

```json
{
 "id": "NR-618",
 "tache": "Non-régression",
 "difficulte": "difficile",
 "theme": "non-classe",
 "entree": "Une salle municipale coûte 120 € par jour. Les associations de la commune bénéficient d'une réduction de 25 % sur ce tarif. Une association de la commune loue la salle pendant 3 jours. Combien paie-t-elle au total ? Réponds uniquement par le montant, sous la forme d'un nombre entier suivi d'une espace et du symbole €, sans aucun autre texte.",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Consigne rédigée pour l'évaluation"
  }
 ],
 "licence_source": "Création originale du projet (contenu rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "sous_type": "consigne",
 "reponse_reference": "270 €",
 "criteres": [
  "Montant exact : 270 €",
  "Format respecté (nombre entier, puis « € »)",
  "Aucun autre texte (ni calcul ni phrase)"
 ]
}
```

## Q-606 — Question (moyen, thème `travail-emploi`)

- [ ] Relu
- Remarques :

```json
{
 "id": "Q-606",
 "tache": "Question",
 "difficulte": "moyen",
 "theme": "travail-emploi",
 "entree": "Un artisan va embaucher un salarié de 17 ans. On lui a dit qu'il devait lui accorder 2 jours de repos consécutifs par semaine. Est-ce exact, une dérogation est-elle possible, et quel est le repos hebdomadaire minimal d'un salarié majeur ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "AgentPublic/sp_questions_corpus (gpt_corpus-20kq&A.xlsx)",
   "depot": "AgentPublic/sp_questions_corpus",
   "revision": "495a22cf7b572621a85d2f3e97783b2f4189c47e",
   "fichier": "gpt_corpus-20kq&A.xlsx",
   "ligne": 9040,
   "role": "amorce de question usager, reformulée par un agent"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F2327 « Repos hebdomadaire du salarié »",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F2327",
   "chunks": [
    2,
    4
   ],
   "extrait": "Tout salarié doit bénéficier d'un repos hebdomadaire. Le repos hebdomadaire pour chaque salarié, d'une semaine à l'autre, est d'au moins 24 heures consécutives. Il faut ajouter à ces 24 heures légales, l'obligation de repos quotidien de 11 heures consécutives entre 2 jours de travail. […] Le plus souvent, le salarié bénéficie de 2 jours de repos consécutifs. […] Tout salarié âgé de moins de 18 ans a droit à 2 jours de repos consécutifs par semaine (par exemple, le samedi et le dimanche). […] Toutefois, des dispositions conventionnelles ou collectives peuvent prévoir une dérogation, uniquement si le salarié est âgé d'au moins 16 ans. En cas de dérogation, le salarié doit bénéficier d'une période minimale de repos de 36 heures consécutives.",
   "role": "fiche de référence"
  }
 ],
 "licence_source": "Amorce : corpus AgentPublic/sp_questions_corpus (Hugging Face). Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "amorce_usager": "Quelles sont les règles concernant le repos hebdomadaire de 2 jours consécutifs pour un salarié ?",
 "reponse_reference": "Oui : un salarié de moins de 18 ans a droit à 2 jours de repos consécutifs par semaine (par exemple le samedi et le dimanche). Des dispositions conventionnelles ou collectives peuvent prévoir une dérogation, uniquement si le salarié a au moins 16 ans, ce qui est le cas ; il doit alors bénéficier d'au moins 36 heures consécutives de repos. Pour un salarié majeur, le repos hebdomadaire est d'au moins 24 heures consécutives, auxquelles s'ajoute le repos quotidien de 11 heures consécutives entre 2 jours de travail ; le plus souvent, il bénéficie de 2 jours consécutifs, sans que ce soit le minimum légal. Ne vaut pas avis juridique.",
 "elements_cles": [
  "Moins de 18 ans : 2 jours de repos consécutifs par semaine",
  "Dérogation possible par des dispositions conventionnelles ou collectives, seulement à partir de 16 ans",
  "En cas de dérogation : au moins 36 heures consécutives de repos",
  "Salarié majeur : au moins 24 heures consécutives, plus le repos quotidien de 11 heures consécutives"
 ],
 "sources_attendues": [
  "https://www.service-public.gouv.fr/particuliers/vosdroits/F2327"
 ],
 "sans_reponse": false,
 "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

## Q-607 — Question (facile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "Q-607",
 "tache": "Question",
 "difficulte": "facile",
 "theme": "collectivites",
 "entree": "La présidente d'une association de quartier veut la mettre en sommeil pendant un an, sans modifier les statuts. Doit-elle faire une déclaration en préfecture ? Dans quels cas en faudrait-il une ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "AgentPublic/sp_questions_corpus (gpt_corpus-20kq&A.xlsx)",
   "depot": "AgentPublic/sp_questions_corpus",
   "revision": "495a22cf7b572621a85d2f3e97783b2f4189c47e",
   "fichier": "gpt_corpus-20kq&A.xlsx",
   "ligne": 16750,
   "role": "amorce de question usager, reformulée par un agent"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F3116 « Peut-on mettre temporairement une association en sommeil ? »",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F3116",
   "chunks": [
    2,
    4
   ],
   "extrait": "Pour pouvoir procéder à la mise en sommeil d'une association, il faut que cette situation soit envisagée dans les statuts et que l'assemblée générale vote sa réalisation. […] Si la mise en sommeil ne conduit pas à la modification des statuts, aucune déclaration n'est à effectuer à la préfecture. […] Si la mise en sommeil conduit aussi à l'une des modifications suivantes, elle doit également être déclarée en préfecture : - Modification statutaire - Changement d'adresse de gestion - Ouverture ou fermeture d'un établissement - Vente de locaux. La déclaration peut s'effectuer en ligne, par courrier ou sur place au greffe des associations. […] Le procès-verbal de l'assemblée générale sur la décision de la mise en sommeil doit être joint à votre dossier. Le dossier doit être adressé par lettre recommandée avec accusé de réception au greffe des associations du siège social de votre association.",
   "role": "fiche de référence"
  }
 ],
 "licence_source": "Amorce : corpus AgentPublic/sp_questions_corpus (Hugging Face). Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "amorce_usager": "Quelles sont les démarches à effectuer auprès de la préfecture pour la mise en sommeil d'une association ?",
 "reponse_reference": "La mise en sommeil doit être prévue par les statuts et votée par l'assemblée générale. Si elle ne conduit pas à modifier les statuts, aucune déclaration n'est à faire en préfecture. Une déclaration en préfecture est nécessaire si la mise en sommeil entraîne une modification statutaire, un changement d'adresse de gestion, l'ouverture ou la fermeture d'un établissement, ou la vente de locaux ; elle se fait en ligne, par courrier (lettre recommandée avec accusé de réception, avec le procès-verbal de l'assemblée générale) ou sur place au greffe des associations. Ne vaut pas avis juridique.",
 "elements_cles": [
  "La mise en sommeil doit être prévue par les statuts et votée par l'assemblée générale",
  "Sans modification des statuts, aucune déclaration en préfecture",
  "Déclaration obligatoire en cas de modification statutaire, de changement d'adresse de gestion, d'ouverture ou de fermeture d'un établissement, ou de vente de locaux",
  "Déclaration en ligne, par courrier ou sur place au greffe des associations"
 ],
 "sources_attendues": [
  "https://www.service-public.gouv.fr/particuliers/vosdroits/F3116"
 ],
 "sans_reponse": false,
 "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

## Q-611 — Question (facile, thème `fiscalite-locale`)

- [ ] Relu
- Remarques :

```json
{
 "id": "Q-611",
 "tache": "Question",
 "difficulte": "facile",
 "theme": "fiscalite-locale",
 "entree": "Un administré veut le plan cadastral de sa parcelle. Peut-il le consulter et le commander sur internet ? Combien coûte une feuille papier au format A4, et le plan indique-t-il les limites exactes de son terrain ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "AgentPublic/sp_questions_corpus (gpt_corpus-20kq&A.xlsx)",
   "depot": "AgentPublic/sp_questions_corpus",
   "revision": "495a22cf7b572621a85d2f3e97783b2f4189c47e",
   "fichier": "gpt_corpus-20kq&A.xlsx",
   "ligne": 16821,
   "role": "amorce de question usager, reformulée par un agent"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F14226 « Comment consulter le cadastre ? »",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F14226",
   "chunks": [
    1,
    2
   ],
   "extrait": "(Attention: Le plan cadastral a une valeur fiscale . Il ne fixe pas les limites de propriété. Le nom des propriétaires n'y figure pas . Pour délimiter les limites d'un terrain, vous devez faire établir un bornage par un géomètre expert.) […] Vous pouvez consulter des extraits du plan cadastral et les commander sur internet. Vous pouvez utiliser l'outil de recherche du service de consultation du plan cadastral : La tarification de la délivrance du plan cadastral dépend de la forme et de la nature des documents demandés : Cas Sur support papier: L'information cadastrale délivrée sur des feuilles au format A3 ou A4 est gratuite . La reproduction sur une feuille entière au format A0 sur support papier coûte 9,50 € et sur support plastique 18 € .",
   "role": "fiche de référence"
  }
 ],
 "licence_source": "Amorce : corpus AgentPublic/sp_questions_corpus (Hugging Face). Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "amorce_usager": "Comment puis-je consulter en ligne et commander les feuilles parcellaires du cadastre ?",
 "reponse_reference": "Oui, il peut consulter des extraits du plan cadastral et les commander sur internet, avec le service de consultation du plan cadastral. Sur papier, l'information délivrée sur des feuilles au format A3 ou A4 est gratuite (une feuille entière au format A0 coûte 9,50 € sur papier et 18 € sur support plastique). Le plan cadastral a une valeur fiscale : il ne fixe pas les limites de propriété, et le nom des propriétaires n'y figure pas ; pour délimiter le terrain, il faut faire établir un bornage par un géomètre expert. Ne vaut pas avis juridique.",
 "elements_cles": [
  "Consultation et commande d'extraits du plan cadastral possibles sur internet",
  "Feuilles A3 ou A4 sur papier : gratuites",
  "Le plan a une valeur fiscale et ne fixe pas les limites de propriété",
  "Pour délimiter le terrain : bornage par un géomètre expert"
 ],
 "sources_attendues": [
  "https://www.service-public.gouv.fr/particuliers/vosdroits/F14226"
 ],
 "sans_reponse": false,
 "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

## Q-614 — Question (moyen, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "Q-614",
 "tache": "Question",
 "difficulte": "moyen",
 "theme": "etat-civil-papiers",
 "entree": "Un ingénieur qui voyage souvent pour son travail doit laisser son passeport au consulat d'un pays pour un visa, alors qu'il a un autre déplacement professionnel prévu pendant ce temps. Peut-il obtenir un second passeport français ? Est-ce un droit, et où se renseigner en France ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F21517 « Peut-on avoir deux passeports ? »",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F21517",
   "chunks": [
    1
   ],
   "extrait": "Les documents à présenter sont les documents à fournir pour tout renouvellement de passeport , ainsi que les documents attestant de votre situation (attestation de l'employeur, billets d'avion...). Attention : la délivrance d'un second passeport n'est pas un droit, mais une faculté. C'est l'administration qui fixe ses critères d'attribution. […] En principe, vous ne pouvez pas avoir plusieurs passeports français. Toutefois, un second passeport peut exceptionnellement être délivré dans l’une des 2 situations suivantes : - Vous voyagez pour raison professionnelle et votre passeport est immobilisé pendant une période au cours de laquelle vous devez voyager - Votre passeport risque de faire apparaître des destinations incompatibles. […] Pour vérifier si votre demande de second passeport est recevable , vous devez consulter le site internet de la préfecture auprès de laquelle vous souhaitez faire la demande. Vous pourrez connaître le guichet compétent ainsi que les justificatifs demandés. Selon les départements, vous devez vous rendre soit à la préfecture (ou à la sous-préfecture), soit dans une mairie équipée pour faire la demande de passeports biométriques.",
   "role": "fiche de référence"
  }
 ],
 "licence_source": "Question rédigée pour l'évaluation. Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "reponse_reference": "En principe, on ne peut pas avoir plusieurs passeports français. Un second passeport peut toutefois être délivré exceptionnellement dans 2 situations : un voyage pour raison professionnelle alors que le passeport est immobilisé pendant une période où l'on doit voyager (son cas), ou un passeport qui risque de faire apparaître des destinations incompatibles. Ce n'est pas un droit mais une faculté : l'administration fixe les critères d'attribution. Il faut fournir les documents de tout renouvellement de passeport et ceux qui attestent la situation (attestation de l'employeur, billets d'avion…). En France, il doit consulter le site internet de la préfecture auprès de laquelle il veut faire la demande, pour vérifier si elle est recevable, connaître le guichet compétent (préfecture, sous-préfecture ou mairie équipée selon les départements) et les justificatifs. Ne vaut pas avis juridique.",
 "elements_cles": [
  "En principe, pas plusieurs passeports français",
  "Second passeport exceptionnel : voyage professionnel avec passeport immobilisé, ou destinations incompatibles",
  "Ce n'est pas un droit mais une faculté ; l'administration fixe les critères",
  "Documents du renouvellement plus justificatifs de la situation (attestation de l'employeur, billets d'avion)",
  "En France, consulter le site de la préfecture pour la recevabilité, le guichet et les justificatifs"
 ],
 "sources_attendues": [
  "https://www.service-public.gouv.fr/particuliers/vosdroits/F21517"
 ],
 "sans_reponse": false,
 "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

## Q-618 — Question (difficile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "Q-618",
 "tache": "Question",
 "difficulte": "difficile",
 "theme": "social-autonomie",
 "entree": "Une retraitée aux faibles ressources demande si le CCAS de sa commune verse une aide pour payer son fioul de chauffage cet hiver, quel en est le montant et quel plafond de ressources s'applique. Que lui répondre ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Recherche plein texte dans le parquet MediaTech AgentPublic/service-public (rév. 29f236f8a5)",
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1",
   "role": "preuve d'absence de source"
  }
 ],
 "licence_source": "Question rédigée pour l'évaluation. Corpus vérifié : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "reponse_reference": "Je ne trouve pas, dans les sources dont je dispose, d'information sur une aide au chauffage versée par le CCAS d'une commune : je ne peux donc indiquer de manière sourcée ni si cette aide existe dans sa commune, ni son montant, ni un plafond de ressources. Je lui conseille de s'adresser directement au CCAS de sa commune ou à sa mairie. Ne vaut pas avis juridique.",
 "elements_cles": [
  "Dit explicitement qu'aucune source disponible ne décrit une aide au chauffage du CCAS de la commune",
  "N'invente ni l'existence de l'aide, ni un montant, ni un plafond de ressources",
  "Oriente vers le CCAS ou la mairie de la commune",
  "Peut mentionner le chèque énergie (aide nationale) sans en faire la réponse sur l'aide du CCAS"
 ],
 "sources_attendues": [],
 "sans_reponse": true,
 "orientation_attendue": "Dire qu'aucune source officielle disponible ne décrit d'aide au chauffage versée par le CCAS de la commune, ne donner ni montant ni plafond, et orienter vers le CCAS ou la mairie.",
 "mention_obligatoire": "Ne vaut pas avis juridique",
 "verification_absence": {
  "corpus": "AgentPublic/service-public (rév. 29f236f8a5)",
  "motifs_recherches_regex_insensible_casse": [
   "CCAS.{0,120}(chauffage|[ée]nergie|fioul)",
   "aides? (facultatives?|extra-l[ée]gales?)",
   "ch[èe]que [ée]nergie"
  ],
  "resultat": "« CCAS…chauffage/énergie/fioul » : 0 fiche ; « aide facultative / extra-légale » : 0 ; « chèque énergie » : 7 fiches sur l'aide nationale (F33667 et fiches liées), aucune sur une aide communale.",
  "date": "2026-10-20"
 }
}
```

## Q-619 — Question (difficile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "Q-619",
 "tache": "Question",
 "difficulte": "difficile",
 "theme": "collectivites",
 "entree": "Un habitant voudrait cultiver une parcelle dans les jardins familiaux de la commune. Il demande comment les parcelles sont attribuées, pour quelle durée et à quel tarif. Que lui dire ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Recherche plein texte dans le parquet MediaTech AgentPublic/service-public (rév. 29f236f8a5)",
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1",
   "role": "preuve d'absence de source"
  }
 ],
 "licence_source": "Question rédigée pour l'évaluation. Corpus vérifié : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "reponse_reference": "Je ne trouve pas, dans les sources dont je dispose, de fiche officielle sur l'attribution des parcelles de jardins familiaux d'une commune : je ne peux donc indiquer de manière sourcée ni les conditions d'attribution, ni la durée, ni le tarif. Ces règles sont propres à la commune ou à l'organisme gestionnaire : je lui conseille de se renseigner auprès de la mairie. Ne vaut pas avis juridique.",
 "elements_cles": [
  "Dit explicitement qu'aucune source disponible ne décrit l'attribution des jardins familiaux de la commune",
  "N'invente ni conditions d'attribution, ni durée, ni tarif",
  "Oriente vers la mairie (ou l'organisme gestionnaire des jardins)"
 ],
 "sources_attendues": [],
 "sans_reponse": true,
 "orientation_attendue": "Dire qu'aucune source officielle disponible ne décrit l'attribution des parcelles de jardins familiaux de la commune, ne donner ni conditions, ni durée, ni tarif, et orienter vers la mairie.",
 "mention_obligatoire": "Ne vaut pas avis juridique",
 "verification_absence": {
  "corpus": "AgentPublic/service-public (rév. 29f236f8a5)",
  "motifs_recherches_regex_insensible_casse": [
   "jardins? familiaux",
   "jardins? partag",
   "jardins? (ouvriers|collectifs|communaux)"
  ],
  "resultat": "« jardins familiaux » : 3 fiches, sans rapport avec une attribution de parcelle (F13479 et F13881 activités du CSE, F31638 exonération de taxe foncière) ; « jardin partagé » et « jardins ouvriers, collectifs ou communaux » : 0.",
  "date": "2026-10-20"
 }
}
```

## RD-601 — Recherche de données (facile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RD-601",
 "tache": "Recherche de données",
 "difficulte": "facile",
 "theme": "social-autonomie",
 "entree": "Pour un diagnostic territorial en Maine-et-Loire, je cherche sur data.gouv.fr le jeu du département sur les bénéficiaires de l'APA à domicile, détaillé par intercommunalité (EPCI). Donne-moi son titre, son producteur et le lien.",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20T21:08:29Z",
   "source": "Serveur MCP data.gouv (search_datasets)",
   "serveur": "https://mcp.data.gouv.fr/mcp",
   "role": "réponses enregistrées (Bac à sable MCP)",
   "cassette": "../../cassettes/RD-601/s1.json",
   "extrait": "1. Allocation Personnalisée à l'Autonomie (APA) à domicile par EPCI en Maine-et-Loire ID: 5e66dbc506e3e7695a7168cb Organization: Département de Maine-et-Loire […] URL: https://www.data.gouv.fr/datasets/allocation-personnalisee-a-lautonomie-apa-a-domicile-par-epci-en-maine-et-loire"
  }
 ],
 "licence_source": "Métadonnées et données data.gouv.fr (catalogue public), enregistrées le 2026-10-20.",
 "fictif": false,
 "version_item": 1,
 "appels_attendus": [
  {
   "outil": "search_datasets",
   "arguments": {
    "query": "APA à domicile par EPCI Maine-et-Loire",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "query": {
      "contient_un_de": [
       "apa",
       "allocation personnalisee",
       "allocation personnalisée",
       "autonomie"
      ],
      "optionnel": false
     }
    }
   },
   "regle": "query contient « apa » ou « allocation personnalisee » ou « allocation personnalisée » ou « autonomie » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres"
  }
 ],
 "cassettes": [
  "../../cassettes/RD-601/s1.json"
 ],
 "reponse_reference": {
  "jeu_principal": {
   "id": "5e66dbc506e3e7695a7168cb",
   "titre": "Allocation Personnalisée à l'Autonomie (APA) à domicile par EPCI en Maine-et-Loire",
   "producteur": "Département de Maine-et-Loire",
   "url": "https://www.data.gouv.fr/datasets/allocation-personnalisee-a-lautonomie-apa-a-domicile-par-epci-en-maine-et-loire"
  },
  "texte": "Le jeu est « Allocation Personnalisée à l'Autonomie (APA) à domicile par EPCI en Maine-et-Loire » (identifiant 5e66dbc506e3e7695a7168cb), publié par Département de Maine-et-Loire : https://www.data.gouv.fr/datasets/allocation-personnalisee-a-lautonomie-apa-a-domicile-par-epci-en-maine-et-loire."
 },
 "mode": "connecte",
 "criteres": [
  "Cite le jeu « Allocation Personnalisée à l'Autonomie (APA) à domicile par EPCI en Maine-et-Loire » (identifiant 5e66dbc506e3e7695a7168cb)",
  "Donne le producteur (Département de Maine-et-Loire) et le lien data.gouv.fr",
  "Ne retient pas les versions par commune ou départementale du même producteur"
 ],
 "producteurs": [
  "Département de Maine-et-Loire"
 ]
}
```

## RD-609 — Recherche de données (difficile, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RD-609",
 "tache": "Recherche de données",
 "difficulte": "difficile",
 "theme": "etat-civil-papiers",
 "entree": "D'après la liste annuelle des prénoms des nouveau-nés publiée par la ville de Nancy (fichier de tous les prénoms 2016-2018), combien d'enfants ont reçu le prénom Jules en 2016, en 2017 et en 2018 ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20T21:08:54Z",
   "source": "Serveur MCP data.gouv (search_datasets, list_dataset_resources, query_resource_data)",
   "serveur": "https://mcp.data.gouv.fr/mcp",
   "role": "réponses enregistrées (Bac à sable MCP)",
   "cassette": "../../cassettes/RD-609/s1.json",
   "extrait": "query_resource_data : Filter: ENFANT_PRENOM exact Jules Total rows (Tabular API): 3 […] ENFANT_PRENOM: Jules NOMBRE_OCCURENCE: 48 ANNEE: 2016 […] ENFANT_PRENOM: Jules NOMBRE_OCCURENCE: 34 ANNEE: 2017 […] ENFANT_PRENOM: Jules NOMBRE_OCCURENCE: 33 ANNEE: 2018"
  }
 ],
 "licence_source": "Métadonnées et données data.gouv.fr (catalogue public), enregistrées le 2026-10-20.",
 "fictif": false,
 "version_item": 1,
 "appels_attendus": [
  {
   "outil": "search_datasets",
   "arguments": {
    "query": "prénoms nouveau-nés Nancy",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "query": {
      "contient_un_de": [
       "prenoms",
       "prénoms",
       "prenom",
       "prénom"
      ],
      "optionnel": false
     }
    }
   },
   "regle": "query contient « prenoms » ou « prénoms » ou « prenom » ou « prénom » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres"
  },
  {
   "outil": "list_dataset_resources",
   "arguments": {
    "dataset_id": "5d2c2919634f41429aae86ce"
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "dataset_id": {
      "exact": "5d2c2919634f41429aae86ce",
      "optionnel": false
     }
    }
   },
   "regle": "dataset_id exact de « La liste annuelle des prénoms des nouveaux-nés  - ville de Nancy »"
  },
  {
   "outil": "query_resource_data",
   "arguments": {
    "resource_id": "b26a8044-d5bd-40cc-8189-a5d32841e841",
    "filter_column": "ENFANT_PRENOM",
    "filter_value": "Jules",
    "page_size": 20
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "resource_id": {
      "exact": "b26a8044-d5bd-40cc-8189-a5d32841e841",
      "optionnel": false
     },
     "filter_column": {
      "exact": "ENFANT_PRENOM",
      "optionnel": false
     },
     "filter_value": {
      "exact": "Jules",
      "optionnel": false
     },
     "filter_operator": {
      "exact": "exact",
      "optionnel": true
     }
    }
   },
   "regle": "resource_id exact de 20190715-215403957-donnees-liste-prenoms-nancy-2016-2018.csv, filtre exact sur « ENFANT_PRENOM » = Jules ; page_size libre"
  }
 ],
 "cassettes": [
  "../../cassettes/RD-609/s1.json"
 ],
 "reponse_reference": {
  "jeu_principal": {
   "id": "5d2c2919634f41429aae86ce",
   "titre": "La liste annuelle des prénoms des nouveaux-nés  - ville de Nancy",
   "producteur": "Ville de Nancy",
   "url": "https://www.data.gouv.fr/datasets/la-liste-annuelle-des-prenoms-des-nouveaux-nes-ville-de-nancy"
  },
  "texte": "D'après « La liste annuelle des prénoms des nouveaux-nés  - ville de Nancy » (identifiant 5d2c2919634f41429aae86ce), publié par Ville de Nancy : https://www.data.gouv.fr/datasets/la-liste-annuelle-des-prenoms-des-nouveaux-nes-ville-de-nancy, fichier 20190715-215403957-donnees-liste-prenoms-nancy-2016-2018.csv filtré sur ENFANT_PRENOM = Jules (3 lignes, sexe M) : 48 en 2016, 34 en 2017 et 33 en 2018."
 },
 "valeurs_attendues": {
  "ressource_id": "b26a8044-d5bd-40cc-8189-a5d32841e841",
  "filtre": {
   "colonne": "ENFANT_PRENOM",
   "operateur": "exact",
   "valeur": "Jules"
  },
  "total_lignes": 3,
  "lignes": [
   {
    "ENFANT_PRENOM": "Jules",
    "NOMBRE_OCCURENCE": "48",
    "ANNEE": "2016"
   },
   {
    "ENFANT_PRENOM": "Jules",
    "NOMBRE_OCCURENCE": "34",
    "ANNEE": "2017"
   },
   {
    "ENFANT_PRENOM": "Jules",
    "NOMBRE_OCCURENCE": "33",
    "ANNEE": "2018"
   }
  ],
  "colonnes": [
   "NOMBRE_OCCURENCE",
   "ANNEE"
  ]
 },
 "mode": "connecte",
 "criteres": [
  "Donne 48 en 2016, 34 en 2017 et 33 en 2018, sans valeur inventée",
  "Utilise le fichier de tous les prénoms 2016-2018 de la Ville de Nancy (pas une source nationale)"
 ],
 "producteurs": [
  "Ville de Nancy"
 ]
}
```

## RD-615 — Recherche de données (difficile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RD-615",
 "tache": "Recherche de données",
 "difficulte": "difficile",
 "theme": "collectivites",
 "entree": "Un habitant de Pontivy veut se rendre à la France services de sa commune. D'après la liste nationale des structures labellisées France services publiée par l'ANCT sur data.gouv.fr, quelle est son adresse, son code postal, son téléphone, et faut-il prendre rendez-vous ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20T21:09:13Z",
   "source": "Serveur MCP data.gouv (search_datasets, list_dataset_resources, query_resource_data)",
   "serveur": "https://mcp.data.gouv.fr/mcp",
   "role": "réponses enregistrées (Bac à sable MCP)",
   "cassette": "../../cassettes/RD-615/s1.json",
   "extrait": "query_resource_data : Filter: lib_com exact Pontivy Total rows (Tabular API): 1 […] lib_fs: France services Pontivy adresse: 8 Rue François Mitterrand […] code_postal: 56300 lib_com: Pontivy […] telephone: 02 97 84 40 80 […] prise_rdv: True commentaire: Accueil uniquement sur rendez-vous le lundi et mardi"
  }
 ],
 "licence_source": "Métadonnées et données data.gouv.fr (catalogue public), enregistrées le 2026-10-20.",
 "fictif": false,
 "version_item": 1,
 "appels_attendus": [
  {
   "outil": "search_datasets",
   "arguments": {
    "query": "structures labellisées France services",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "query": {
      "contient_un_de": [
       "france services",
       "france service"
      ],
      "optionnel": false
     }
    }
   },
   "regle": "query contient « france services » ou « france service » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres"
  },
  {
   "outil": "list_dataset_resources",
   "arguments": {
    "dataset_id": "62503e25bc0f6370f4a651ce"
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "dataset_id": {
      "exact": "62503e25bc0f6370f4a651ce",
      "optionnel": false
     }
    }
   },
   "regle": "dataset_id exact de « Liste des structures labellisées France services »"
  },
  {
   "outil": "query_resource_data",
   "arguments": {
    "resource_id": "31576dff-fd61-4de9-819f-32c2f880b142",
    "filter_column": "lib_com",
    "filter_value": "Pontivy",
    "page_size": 20
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "resource_id": {
      "exact": "31576dff-fd61-4de9-819f-32c2f880b142",
      "optionnel": false
     },
     "filter_column": {
      "exact": "lib_com",
      "optionnel": false
     },
     "filter_value": {
      "exact": "Pontivy",
      "optionnel": false
     },
     "filter_operator": {
      "exact": "exact",
      "optionnel": true
     }
    }
   },
   "regle": "resource_id exact de Liste des structures France services (liste-fs-20261020.csv), filtre exact sur « lib_com » = Pontivy ; page_size libre"
  }
 ],
 "cassettes": [
  "../../cassettes/RD-615/s1.json"
 ],
 "reponse_reference": {
  "jeu_principal": {
   "id": "62503e25bc0f6370f4a651ce",
   "titre": "Liste des structures labellisées France services",
   "producteur": "Agence nationale de la cohésion des territoires",
   "url": "https://www.data.gouv.fr/datasets/liste-des-structures-labellisees-france-services"
  },
  "texte": "D'après « Liste des structures labellisées France services » (identifiant 62503e25bc0f6370f4a651ce), publié par Agence nationale de la cohésion des territoires : https://www.data.gouv.fr/datasets/liste-des-structures-labellisees-france-services, fichier « Liste des structures France services » filtré sur lib_com = Pontivy (1 ligne) : France services Pontivy, 8 rue François Mitterrand, 56300 Pontivy, téléphone 02 97 84 40 80 ; prise de rendez-vous : oui, avec la mention « Accueil uniquement sur rendez-vous le lundi et mardi »."
 },
 "valeurs_attendues": {
  "ressource_id": "31576dff-fd61-4de9-819f-32c2f880b142",
  "filtre": {
   "colonne": "lib_com",
   "operateur": "exact",
   "valeur": "Pontivy"
  },
  "total_lignes": 1,
  "lignes": [
   {
    "lib_fs": "France services Pontivy",
    "adresse": "8 Rue François Mitterrand",
    "code_postal": "56300",
    "telephone": "02 97 84 40 80",
    "prise_rdv": "True",
    "commentaire": "Accueil uniquement sur rendez-vous le lundi et mardi"
   }
  ],
  "colonnes": [
   "adresse",
   "code_postal",
   "telephone"
  ]
 },
 "mode": "connecte",
 "criteres": [
  "Donne l'adresse 8 rue François Mitterrand, le code postal 56300 et le téléphone 02 97 84 40 80, sans valeur inventée",
  "Indique l'accueil uniquement sur rendez-vous le lundi et le mardi",
  "Utilise la liste nationale de l'Agence nationale de la cohésion des territoires (pas une liste départementale)"
 ],
 "producteurs": [
  "Agence nationale de la cohésion des territoires"
 ]
}
```

## RD-617 — Recherche de données (moyen, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RD-617",
 "tache": "Recherche de données",
 "difficulte": "moyen",
 "theme": "famille-education-sante",
 "entree": "Je veux télécharger le nombre d'assistants maternels agréés par intercommunalité (EPCI) en Loire-Atlantique, publié par le département sur data.gouv.fr. Quel jeu et quel fichier CSV dois-je prendre ? Donne le nom du fichier et son lien.",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20T21:09:21Z",
   "source": "Serveur MCP data.gouv (search_datasets, list_dataset_resources)",
   "serveur": "https://mcp.data.gouv.fr/mcp",
   "role": "réponses enregistrées (Bac à sable MCP)",
   "cassette": "../../cassettes/RD-617/s1.json",
   "extrait": "search_datasets : 1. Assistant-e-s maternel-le-s agréé-e-s en Loire-Atlantique par EPCI ID: 5b6068559ce2e73b3fa40d82 Organization: Département de Loire-Atlantique […] URL: https://www.data.gouv.fr/datasets/assistant-e-s-maternel-le-s-agree-e-s-en-loire-atlantique-par-epci-2 2. Places chez les assistant-e-s maternel-le-s agréé-e-s en Loire-Atlantique par EPCI ID: 5b6067919ce2e73b3fa40d5d […] list_dataset_resources : Total resources: 4 1. 224400028_nb-assistantes-maternelles-agreees-par-epci.csv Resource ID: fccc4492-1a50-4d41-a3f2-ef3190a3a06d Format: csv […] URL: https://data.loire-atlantique.fr/api/explore/v2.1/catalog/datasets/224400028_nb-assistantes-maternelles-agreees-par-epci/exports/csv?use_labels=true 2. 224400028_nb-assistantes-maternelles-agreees-par-epci.json […] 3. 224400028_nb-assistantes-maternelles-agreees-par-epci.geojson […] 4. 224400028_nb-assistantes-maternelles-agreees-par-epci.zip […] URL: https://data.loire-atlantique.fr/api/explore/v2.1/catalog/datasets/224400028_nb-assistantes-maternelles-agreees-par-epci/exports/shp"
  }
 ],
 "licence_source": "Métadonnées et données data.gouv.fr (catalogue public), enregistrées le 2026-10-20.",
 "fictif": false,
 "version_item": 2,
 "appels_attendus": [
  {
   "outil": "search_datasets",
   "arguments": {
    "query": "assistants maternels agréés Loire-Atlantique EPCI",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "query": {
      "contient_un_de": [
       "assistants maternels",
       "assistantes maternelles",
       "assistant maternel",
       "assistante maternelle",
       "assistant-e-s maternel-le-s"
      ],
      "optionnel": false
     }
    }
   },
   "regle": "query contient « assistants maternels » ou « assistantes maternelles » ou « assistant maternel » ou « assistante maternelle » ou « assistant-e-s maternel-le-s » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres"
  },
  {
   "outil": "list_dataset_resources",
   "arguments": {
    "dataset_id": "5b6068559ce2e73b3fa40d82"
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "dataset_id": {
      "exact": "5b6068559ce2e73b3fa40d82",
      "optionnel": false
     }
    }
   },
   "regle": "dataset_id exact de « Assistant-e-s maternel-le-s agréé-e-s en Loire-Atlantique par EPCI »"
  }
 ],
 "cassettes": [
  "../../cassettes/RD-617/s1.json"
 ],
 "reponse_reference": {
  "jeu_principal": {
   "id": "5b6068559ce2e73b3fa40d82",
   "titre": "Assistant-e-s maternel-le-s agréé-e-s en Loire-Atlantique par EPCI",
   "producteur": "Département de Loire-Atlantique",
   "url": "https://www.data.gouv.fr/datasets/assistant-e-s-maternel-le-s-agree-e-s-en-loire-atlantique-par-epci-2"
  },
  "texte": "Le jeu est « Assistant-e-s maternel-le-s agréé-e-s en Loire-Atlantique par EPCI » (identifiant 5b6068559ce2e73b3fa40d82), publié par Département de Loire-Atlantique : https://www.data.gouv.fr/datasets/assistant-e-s-maternel-le-s-agree-e-s-en-loire-atlantique-par-epci-2. Le fichier CSV est 224400028_nb-assistantes-maternelles-agreees-par-epci.csv (ressource fccc4492-1a50-4d41-a3f2-ef3190a3a06d) : https://data.loire-atlantique.fr/api/explore/v2.1/catalog/datasets/224400028_nb-assistantes-maternelles-agreees-par-epci/exports/csv?use_labels=true ; le jeu existe aussi en JSON, GeoJSON et ZIP (shapefile)."
 },
 "mode": "connecte",
 "criteres": [
  "Retient le jeu « Assistant-e-s maternel-le-s agréé-e-s en Loire-Atlantique par EPCI » (identifiant 5b6068559ce2e73b3fa40d82), pas celui des places",
  "Donne le fichier 224400028_nb-assistantes-maternelles-agreees-par-epci.csv et son lien (data.loire-atlantique.fr)",
  "N'invente pas d'autre fichier que les quatre ressources listées"
 ],
 "producteurs": [
  "Département de Loire-Atlantique"
 ]
}
```

## RD-619 — Recherche de données (facile, thème `fiscalite-locale`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RD-619",
 "tache": "Recherche de données",
 "difficulte": "facile",
 "theme": "fiscalite-locale",
 "entree": "Pour une note sur les impôts locaux à Antibes, je cherche le jeu de données publié par la ville sur sa fiscalité locale. Donne-moi son titre, son producteur et le lien data.gouv.fr.",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20T21:09:28Z",
   "source": "Serveur MCP data.gouv (search_datasets)",
   "serveur": "https://mcp.data.gouv.fr/mcp",
   "role": "réponses enregistrées (Bac à sable MCP)",
   "cassette": "../../cassettes/RD-619/s1.json",
   "extrait": "1. Fiscalité locale à Antibes ID: 5e7b688ad0216647b33b1250 Organization: Ville d'Antibes URL: https://www.data.gouv.fr/datasets/fiscalite-locale-a-antibes"
  }
 ],
 "licence_source": "Métadonnées et données data.gouv.fr (catalogue public), enregistrées le 2026-10-20.",
 "fictif": false,
 "version_item": 1,
 "appels_attendus": [
  {
   "outil": "search_datasets",
   "arguments": {
    "query": "fiscalité locale Antibes",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "query": {
      "contient_un_de": [
       "fiscalite locale",
       "fiscalité locale",
       "fiscalite",
       "fiscalité",
       "impots locaux",
       "impôts locaux"
      ],
      "optionnel": false
     }
    }
   },
   "regle": "query contient « fiscalite locale » ou « fiscalité locale » ou « fiscalite » ou « fiscalité » ou « impots locaux » ou « impôts locaux » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres"
  }
 ],
 "cassettes": [
  "../../cassettes/RD-619/s1.json"
 ],
 "reponse_reference": {
  "jeu_principal": {
   "id": "5e7b688ad0216647b33b1250",
   "titre": "Fiscalité locale à Antibes",
   "producteur": "Ville d'Antibes",
   "url": "https://www.data.gouv.fr/datasets/fiscalite-locale-a-antibes"
  },
  "texte": "Le jeu est « Fiscalité locale à Antibes » (identifiant 5e7b688ad0216647b33b1250), publié par Ville d'Antibes : https://www.data.gouv.fr/datasets/fiscalite-locale-a-antibes."
 },
 "mode": "connecte",
 "criteres": [
  "Cite le jeu « Fiscalité locale à Antibes » (identifiant 5e7b688ad0216647b33b1250)",
  "Donne le producteur (Ville d'Antibes) et le lien data.gouv.fr"
 ],
 "producteurs": [
  "Ville d'Antibes"
 ]
}
```

## RD-620 — Recherche de données (moyen, thème `fiscalite-locale`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RD-620",
 "tache": "Recherche de données",
 "difficulte": "moyen",
 "theme": "fiscalite-locale",
 "entree": "Je cherche sur data.gouv.fr un jeu qui donne, commune par commune, le taux voté et le montant prélevé de la majoration de taxe d'habitation sur les résidences secondaires. Qui le publie, combien de communes couvre-t-il, de quel fichier de la DGFiP vient-il, et sous quelle licence ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20T21:09:31Z",
   "source": "Serveur MCP data.gouv (search_datasets, get_dataset_info)",
   "serveur": "https://mcp.data.gouv.fr/mcp",
   "role": "réponses enregistrées (Bac à sable MCP)",
   "cassette": "../../cassettes/RD-620/s1.json",
   "extrait": "get_dataset_info : Full description: Les 1 629 communes, réparties dans 61 départements, pour lesquelles le fichier REI 2025 de la DGFiP renseigne un taux de majoration de la taxe d'habitation sur les résidences secondaires. […] Organization: Emet Expertise […] License: lov2 Update frequency: annual"
  }
 ],
 "licence_source": "Métadonnées et données data.gouv.fr (catalogue public), enregistrées le 2026-10-20.",
 "fictif": false,
 "version_item": 1,
 "appels_attendus": [
  {
   "outil": "search_datasets",
   "arguments": {
    "query": "majoration taxe d'habitation résidences secondaires",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "query": {
      "contient_un_de": [
       "majoration",
       "residences secondaires",
       "résidences secondaires",
       "taxe d'habitation",
       "taxe habitation"
      ],
      "optionnel": false
     }
    }
   },
   "regle": "query contient « majoration » ou « residences secondaires » ou « résidences secondaires » ou « taxe d'habitation » ou « taxe habitation » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres"
  },
  {
   "outil": "get_dataset_info",
   "arguments": {
    "dataset_id": "6ac1638d5d19a7f39f111480"
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "dataset_id": {
      "exact": "6ac1638d5d19a7f39f111480",
      "optionnel": false
     }
    }
   },
   "regle": "dataset_id exact de « Majoration de taxe d'habitation sur les résidences secondaires : taux voté et montant prélevé, par commune »"
  }
 ],
 "cassettes": [
  "../../cassettes/RD-620/s1.json"
 ],
 "reponse_reference": {
  "jeu_principal": {
   "id": "6ac1638d5d19a7f39f111480",
   "titre": "Majoration de taxe d'habitation sur les résidences secondaires : taux voté et montant prélevé, par commune",
   "producteur": "Emet Expertise",
   "url": "https://www.data.gouv.fr/datasets/majoration-de-taxe-dhabitation-sur-les-residences-secondaires-taux-vote-et-montant-preleve-par-commune"
  },
  "texte": "Le jeu est « Majoration de taxe d'habitation sur les résidences secondaires : taux voté et montant prélevé, par commune » (identifiant 6ac1638d5d19a7f39f111480), publié par Emet Expertise : https://www.data.gouv.fr/datasets/majoration-de-taxe-dhabitation-sur-les-residences-secondaires-taux-vote-et-montant-preleve-par-commune. Il couvre 1 629 communes réparties dans 61 départements, pour lesquelles le fichier REI 2025 de la DGFiP renseigne un taux de majoration ; licence lov2 ; mise à jour annuelle."
 },
 "mode": "connecte",
 "criteres": [
  "Donne le producteur (Emet Expertise)",
  "Indique 1 629 communes dans 61 départements, d'après le fichier REI 2025 de la DGFiP",
  "Donne la licence lov2",
  "Ne confond pas avec les jeux « Fiscalité locale des particuliers » ni avec le zonage TLV"
 ],
 "producteurs": [
  "Emet Expertise"
 ]
}
```

## RE-602 — Résumé (facile, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RE-602",
 "tache": "Résumé",
 "difficulte": "facile",
 "theme": "etat-civil-papiers",
 "entree": {
  "consigne": "Résume ce document en 80 mots au plus, pour un agent d'accueil de mairie qui reçoit une personne dont la carte d'identité et le passeport sont périmés depuis plus de 5 ans : les justificatifs de nationalité possibles, dans l'ordre où le document les présente.",
  "document": "La situation varie selon qu’au moins l’un de vos parents est né en France ou que votre nationalité française est inscrite dans les mentions marginales de votre acte de naissance : Quand vous faites une demande de renouvellement d'une carte d'identité ou d'un passeport, la présentation de l'un des documents suivants suffit à prouver votre nationalité française :\n- Carte d'identité valide ou périmée depuis moins de 5 ans\n- Passeport valide ou périmé depuis moins de 5 ans.\nSi ces 2 documents sont périmés depuis plus de 5 ans, vous devez présenter d’autres documents pour prouver votre nationalité française. Nous vous présentons les informations à connaître. Acte de naissance: Si vous ne pouvez pas prouver votre nationalité française par une carte d’identité ou un passeport valide ou périmé depuis moins de 5 ans, vous pouvez utiliser un acte de naissance. La situation varie selon que vous êtes né en France ou à l’étranger :\nCas Vous êtes né en France: Cas Au moins l'un de vos parents est né en France: Vous pouvez fournir un acte de naissance de moins de 3 mois si vous êtes né en France et qu’au moins l’un de vos parents est lui-même né en France pour prouver votre nationalité française. Vous pouvez utiliser ce téléservice :\nCas Votre nationalité française est sur votre acte de naissance (en mention marginale): Votre nationalité française est inscrite en mention marginale sur votre acte de naissance ? Vous pouvez fournir un acte de naissance de moins de 3 mois pour prouver votre nationalité française. Vous pouvez utiliser ce téléservice :\nCas Vous êtes né à l'étranger: Si vous n'avez pas de titre d'identité (carte d’identité ou passeport) récent, la preuve de la nationalité française peut être apportée en présentant un acte de naissance (copie intégrale ou extrait avec filiation) de moins de 3 mois . Cet acte d'état civil peut permettre d'établir votre nationalité française si vous vous trouvez dans l'un des cas suivants : \n- L'acte de naissance (sur papier sécurisé) a été délivré par le service central d'état civil de Nantes (Scec)\n- L'acte de naissance (sur papier ordinaire) a été délivré par un officier de l'état civil consulaire d'une ambassade.\n Vous pouvez utiliser ce téléservice :\nDocuments liés à la nationalité française: Si vous ne pouvez pas prouver votre nationalité française avec un acte de naissance, vous pouvez le faire avec l’un de ces documents :\n- Déclaration d'acquisition de la nationalité française à votre nom, dûment enregistrée ou, si vous n’avez pas ce document, une attestation de cette déclaration\n- Ampliation du décret de naturalisation ou de réintégration dans la nationalité française ou, si vous n’avez pas ce document, une attestation constatant l'existence de ce décret.\nPossession d’État: Si vous ne pouvez pas prouver votre nationalité française avec des documents liés à la nationalité, vous pouvez demander à bénéficier de la « possession d'état de Français ». La possession d'état est établie si les pouvoirs publics vous considèrent comme Français depuis au moins 10 ans. Pour l'établir, il faut fournir au moins 2 documents figurant dans la liste suivante :\n- Carte militaire ou un document attestant de l'accomplissement des obligations militaires\n- Carte d'électeur pour les élections réservées aux Français\n- Document attestant de l'appartenance à la fonction publique française (pour les emplois réservés aux Français, avant l'ouverture de la fonction publique aux ressortissants de l'Union européenne en 1991)\n- Document attestant de l'exercice d'un mandat électif réservé aux seuls Français\n- Titre d'identité non sécurisé (par exemple, carte d’identité cartonnée, passeport Delphine), même périmé.\nCertificat de nationalité: Si vous ne possédez aucun des documents mentionnés précédemment, il faudra présenter un certificat de nationalité française (CNF).",
  "nb_mots": 590
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F18713 « Renouvellement d'une carte d'identité ou d'un passeport périmé depuis plus de 5 ans : comment prouver sa nationalité française ? » (chunks 1)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F18713",
   "type": "service-public",
   "doc_id": "F18713",
   "chunks": [
    1
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 2,
 "points_cles_reference": [
  "Une carte d'identité et un passeport périmés depuis plus de 5 ans ne suffisent plus à prouver la nationalité : il faut présenter d'autres documents",
  "Un acte de naissance de moins de 3 mois peut suffire : personne née en France avec un parent né en France, nationalité en mention marginale, ou certains actes de personnes nées à l'étranger (Scec de Nantes, consulat)",
  "À défaut : déclaration d'acquisition de la nationalité ou décret de naturalisation (ou leur attestation), puis possession d'état de Français (considéré comme Français depuis au moins 10 ans, au moins 2 documents)",
  "En dernier recours : certificat de nationalité française"
 ],
 "longueur_demandee": "courte"
}
```

## RE-603 — Résumé (facile, thème `travail-emploi`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RE-603",
 "tache": "Résumé",
 "difficulte": "facile",
 "theme": "travail-emploi",
 "entree": {
  "consigne": "Résume ce document en 200 mots au plus, pour un salarié dont l'entreprise va fermer trois semaines en août : les règles que doit respecter l'employeur pour fermer l'entreprise et l'indemnisation du salarié selon les congés qu'il a acquis.",
  "document": "Si l'employeur décide de la fermeture de l'entreprise pour une période (par exemple au mois d'août), le salarié peut être indemnisé durant cette période d'inactivité, sous conditions. Cela dépend du nombre de congés payés acquis par le salarié avant la fermeture de l'entreprise. Nous vous présentons les informations à connaître. L'employeur peut décider de la fermeture temporaire de l'entreprise (en période d'été, par exemple). Avant de procéder à la fermeture, le comité social et économique (CSE), s'il en existe un dans l'entreprise, est consulté pour avis. En l'absence de CSE, un accord collectif d'entreprise doit fixer les règles applicables et les formalités à respecter dans le cadre de la fermeture de l’entreprise. En l'absence d'accord collectif, l'employeur peut décider seul de fermer l'entreprise. L'employeur n'est pas dans l'obligation d'obtenir l'accord des salariés. Toutefois, lorsqu’il décide de la fermeture estivale de l’entreprise, l’employeur doit impérativement prévenir les salariés au moins 1 mois avant la date de fermeture par tout moyen (affichage dans l'entreprise, mail, courrier). Si l’employeur ferme l’entreprise sans avertir les salariés dans ce délai, la fermeture de l'entreprise n'est pas considérée comme une période de congés payés et l'employeur doit indemniser les salariés pour les salaires perdus. (Attention: La durée de la fermeture annuelle de l'entreprise ne peut pas être supérieure à 24 jours ouvrables .)\nL'indemnisation du salarié varie selon qu'il a acquis suffisamment de jours de congés ou pas durant la période de fermeture de l'entreprise.\nCas Le salarié a acquis suffisamment de jours de congés avant la fermeture: Si l'employeur décide de la fermeture de l'entreprise pour une période (par exemple au mois d'août), le salarié est indemnisé selon le nombre de ses jours de congés payés acquis. Le salarié perçoit alors l'indemnité de congés payés dans les conditions habituelles, versées par l'entreprise, pendant toute la durée de fermeture de l'entreprise et de la cessation de son activité. (À noter: Lorsque l'entreprise est fermée pendant un nombre de jours dépassant la durée des congés légaux annuels ( 30 jours ouvrables ), l'employeur verse au salarié une indemnité journalière pour chacun des jours ouvrables de fermeture au-delà de la durée légale. Cette indemnité spécifique ne peut être inférieure à l'indemnité journalière de congés payés. Elle est soumise à l'impôt sur le revenu .)\nCas Le salarié n'a pas acquis suffisamment de jours de congés avant la fermeture: Si le salarié n'a pas acquis assez de jours de congés payés pour percevoir l'indemnité de congés payés durant l'intégralité de la fermeture de l'entreprise, France Travail (anciennement Pôle emploi) peut lui verser une aide financière. Cette aide est versée sous conditions , selon que le salarié a perçu ou pas l'allocation d'aide au retour à l'emploi (ARE) ou l'allocation de solidarité spécifique (ASS) avant son embauche. Il convient au salarié en cessation d'activité temporaire de se renseigner auprès de France Travail pour savoir si, selon sa situation personnelle, il peut percevoir l'ARE ou l'ASS. \nCas Perception de l'ARE ou l'ASS avant recrutement: Le salarié conserve des droit acquis non pris à l'ARE ou à l'ASS durant la période de fermeture de l'entreprise. Dans ce cas, le salarié peut faire une demande à l'agence France Travail dont il dépendait en tant que demandeur d'emploi. Le montant de l'aide est alors calculé par France Travail qui tient en compte les éléments suivants : \n- Nombre de jours de fermeture de l'entreprise\n- Et droits à congés payés acquis durant le nouvel emploi.\n(À noter: Lorsque l'entreprise est fermée pendant un nombre de jours dépassant la durée des congés légaux annuels ( 30 jours ouvrables ), l'employeur verse au salarié une indemnité journalière pour chacun des jours ouvrables de fermeture au-delà de la durée légale. Cette indemnité spécifique ne peut être inférieure à l'indemnité journalière de congés payés. Elle est soumise à l'impôt sur le revenu .)\nCas Non-perception de l'ARE ou l'ASS avant recrutement: Le salarié peut demander à son employeur de bénéficier de congés payés par anticipation. L'employeur n'est pas obligé d'accepter la prise de congés payés par anticipation. Si l'employeur refuse le congé par anticipation, le salarié doit prendre alors un congé sans solde . (À noter: Lorsque l'entreprise est fermée pendant un nombre de jours dépassant la durée des congés légaux annuels ( 30 jours ouvrables ), l'employeur verse au salarié une indemnité journalière pour chacun des jours ouvrables de fermeture au-delà de la durée légale. Cette indemnité spécifique ne peut être inférieure à l'indemnité journalière de congés payés. Elle est soumise à l'impôt sur le revenu .)",
  "nb_mots": 735
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F1016 « Fermeture de l'entreprise pour congés annuels : le salarié est-il indemnisé ? » (chunks 1, 2)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1016",
   "type": "service-public",
   "doc_id": "F1016",
   "chunks": [
    1,
    2
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "points_cles_reference": [
  "L'employeur peut décider seul la fermeture temporaire, après avis du CSE s'il existe (ou selon l'accord collectif applicable), sans l'accord des salariés",
  "Il doit prévenir les salariés au moins 1 mois avant ; sinon, la fermeture n'est pas une période de congés payés et il doit indemniser les salaires perdus",
  "La fermeture annuelle ne peut pas dépasser 24 jours ouvrables",
  "Le salarié qui a assez de congés acquis perçoit l'indemnité de congés payés habituelle pendant la fermeture",
  "Sinon, France Travail peut verser une aide s'il avait des droits ARE ou ASS avant son embauche ; à défaut, il peut demander des congés par anticipation (que l'employeur peut refuser), et prend sinon un congé sans solde"
 ],
 "longueur_demandee": "moyenne"
}
```

## RE-609 — Résumé (moyen, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RE-609",
 "tache": "Résumé",
 "difficulte": "moyen",
 "theme": "etat-civil-papiers",
 "entree": {
  "consigne": "Résume ce document en 200 mots au plus, pour un agent d'accueil d'une maison France services qui reçoit un étranger inquiet pour sa carte de séjour : la procédure de retrait, l'exception du chômage involontaire, puis les cas de retrait de la carte temporaire ou pluriannuelle (conditions d'obtention, rupture de la vie commune, travail sans autorisation, ordre public, fraude) et de la carte de résident (rupture de la vie commune, départ de France, ordre public, fraude).",
  "document": "Un étranger peut se faire retirer son titre de séjour s'il ne remplit plus les conditions de délivrance ou s'il commet certains délits. Oui, votre titre de séjour peut vous être retiré pour des raisons qui varient selon le type de titre que vous possédez. Vous êtes alors obligé de quitter la France. La préfecture vous informera qu'elle souhaite vous retirer votre carte de séjour. Vous aurez alors un délai pour présenter vos observations écrites ou orales, afin d'éviter éventuellement le retrait.\nCas Vous avez une carte de séjour temporaire ou pluriannuelle: Pendant sa durée de validité, votre titre de séjour doit ou peut vous être retiré, notamment si vous vous trouvez dans l'un des cas suivants : \n- Vous ne remplissez plus l'une des conditions d'obtention du titre\n- Dans le cadre du regroupement familial, la rupture de vie commune est intervenue durant les 3 années suivant la délivrance de la carte (sauf décès ou violences conjugales)\n- Vous vivez en état de polygamie en France\n- Vous avez commis des faits vous exposant à une condamnation (trafic de drogue, esclavage, traite des humains, proxénétisme, racolage...)\n- Vous avez employé illégalement un travailleur étranger\n- Vous travaillez sans autorisation\n- Vous ne vous êtes pas rendu aux convocations de la préfecture pour vérifier que vous remplissez toujours les conditions de délivrance de votre carte séjour\n- Vous avez fait l'objet d'une mesure d'expulsion ou d'interdiction du territoire français (ITF)\n- Vous constituez une menace pour l'ordre public\n- Vous avez obtenu votre titre de séjour par fraude\n- Vous avez commis des faits de faux et usage de faux\n- Vous avez commis des faits qui vous exposent à une condamnation pénale à l'encontre d'un élu ou d'un agent public\n- Vous n'avez pas respecté le contrat d'engagement à respecter les principes de la République que vous avez signé.\n (À savoir: Votre carte de séjour salarié ou talent ne peut pas vous être retirée si vous vous retrouvez involontairement au chômage.)\nCas Vous avez une carte de résident: Pendant sa durée de validité, votre carte doit ou peut vous être retirée, notamment si vous vous trouvez dans l'un des cas suivants : \n- Vous êtes marié à un Français et la rupture de vie commune est intervenue dans les 4 années qui suivent votre mariage (sauf si un ou plusieurs enfants sont nés de votre union et que vous participez à leur entretien et leur éducation depuis leur naissance, ou en cas de décès de votre époux ou épouse ou de violences conjugales)\n- Dans le cadre du regroupement familial, la vie commune a été rompue pendant les 3 années qui ont suivi la délivrance de la carte (sauf en cas de décès ou de violences conjugales)\n- Vous vivez en état de polygamie en France\n- Vous avez été condamné pour avoir commis sur un enfant de moins de 15 ans certaines violences (mutilations ou violences ayant entraîné une infirmité permanente) ou si vous vous êtes rendu complice de celles-ci\n- Vous avez employé illégalement un travailleur étranger\n- Vous ne vous êtes pas rendu aux convocations de la préfecture pour vérifier que vous remplissez toujours les conditions de délivrance de votre carte de résident\n- Vous avez fait l'objet d'une mesure d'expulsion ou d'interdiction du territoire français (ITF)\n- Vous constituez une menace pour l'ordre public\n- Vous avez quitté la France pendant plus de 3 ans consécutifs\n- Vous avez obtenu votre titre de séjour par fraude\n- Vous n'avez pas respecté le contrat d'engagement à respecter les principes de la République que vous avez signé.",
  "nb_mots": 574
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F11892 « Un étranger peut-il se faire retirer son titre de séjour en cours de validité ? » (chunks 1)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F11892",
   "type": "service-public",
   "doc_id": "F11892",
   "chunks": [
    1
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 2,
 "points_cles_reference": [
  "Un titre de séjour peut être retiré pendant sa validité ; la personne doit alors quitter la France",
  "La préfecture informe d'abord de son intention et laisse un délai pour présenter des observations écrites ou orales",
  "Carte temporaire ou pluriannuelle : notamment si les conditions d'obtention ne sont plus remplies, en cas de rupture de la vie commune dans les 3 ans (regroupement familial, sauf décès ou violences conjugales), de travail sans autorisation, de menace pour l'ordre public ou de fraude",
  "Une carte de séjour salarié ou talent ne peut pas être retirée en cas de chômage involontaire",
  "Carte de résident : notamment en cas de rupture de la vie commune dans les 4 ans du mariage avec un Français (avec des exceptions) ou dans les 3 ans suivant la délivrance (regroupement familial), de départ de France pendant plus de 3 ans consécutifs, de menace pour l'ordre public ou de fraude"
 ],
 "longueur_demandee": "moyenne"
}
```

## RE-614 — Résumé (moyen, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RE-614",
 "tache": "Résumé",
 "difficulte": "moyen",
 "theme": "collectivites",
 "entree": {
  "consigne": "Fais un résumé détaillé de ce document, en 400 mots au plus, pour un agent du service vie associative d'une commune qui renseigne les habitants : les sources d'information en ligne, auprès du greffe, des ministères, des collectivités et de la Miviludes, les frais de copie et les délais de réponse.",
  "document": "Toute personne peut obtenir des informations sur une association déclarée, par internet, par courrier ou sur place. Toute personne peut obtenir des informations sur une association déclarée, par internet, par courrier ou sur place.\nCas Sur le site Journal-officiel.gouv.fr: Le service de consultation des annonces du Journal officiel des associations vous permet d'accéder aux informations suivantes : \n- Nom, adresse du siège social et objet d'une association\n- Comptes et, s'il y a lieu, rapport du commissaire aux comptes d'une association ayant reçu, au cours d'une même année, plus de 153 000 € de dons et/ou de subventions\n- Déclaration de création, de modification statutaire, de changement d'objet, d’adresse du siège social et déclaration de dissolution publiée volontairement.\nCas Sur le site data.gouv.fr: Sur la plateforme ouverte des données publiques data.gouv.fr, vous pouvez consulter les informations suivantes : \n- Répertoire national des associations (RNA) , qui contient l'ensemble des associations loi 1901\n- Liste des associations reconnues d'utilité publique (Arup)\n- Liste des fondations reconnues d'utilité publique .\nPlusieurs organismes peuvent vous apporter des informations.\nCas Auprès du greffe des associations à la préfecture: Toute personne peut consulter gratuitement et/ou demander une copie des documents suivants au greffe des associations du département de son siège social : \n- Statut et leur éventuelle modification\n- Déclaration initiale de l'association\n- Éventuelle déclaration relative au changement survenu dans l'administration de l'association (changement de dirigeant, nouvel établissement, changement d'adresse du siège social, acquisition ou vente d’ immeubles ).\n Le règlement intérieur n'est pas systématiquement transmis au greffe des associations. Cependant, s'il le possède, il peut vous être communiqué. Les documents détenus par le greffe des associations font foi. Vous pouvez demander la copie des documents au guichet, par courrier, ou par mail. Les frais de reproduction des documents sont à votre charge (en tant que demandeur). Ils sont fixés par l’administration concernée et ne peuvent pas dépasser les montants suivants : \nCoût de transmission:\n| Support | Tarif maximum | \n| - | - | \n| Papier | 0,18 € par page A4 (noir et blanc) | \n| Cédérom | 2,75 € | \n Si les documents sont envoyés par courrier, les frais d'envoi peuvent s'ajouter à ces tarifs. Lorsqu'une administration est saisie d'une demande et qu'elle ne possède pas le document demandé, elle le transmet au bon service et en informe le demandeur. Les demandes adressées à une administration doivent être satisfaites dans le mois qui suit. L'absence de réponse dans ce délai vaut refus de communication. Vous pouvez alors saisir la commission d'accès aux documents administratifs (Cada) dans les 2 mois qui suivent.\nCas Auprès des ministères: Les ministères peuvent vous renseigner sur les agréments accordés et sur les subventions attribuées à une association. Ces informations peuvent être diffusées sur les sites internet des ministères ou obtenues par mail ou par courrier. Les frais de reproduction des documents sont à votre charge (en tant que demandeur). Ils sont fixés par l’administration concernée et ne peuvent pas dépasser les montants suivants : \nCoût de transmission:\n| Support | Tarif maximum | \n| - | - | \n| Papier | 0,18 € par page A4 (noir et blanc) | \n| Cédérom | 2,75 € | \n Si les documents sont envoyés par courrier, les frais d'envoi peuvent s'ajouter à ces tarifs. Lorsqu'une administration est saisie d'une demande et qu'elle ne possède pas le document demandé, elle le transmet au bon service et en informe le demandeur. Les demandes adressées à une administration doivent être satisfaites dans le mois qui suit. L'absence de réponse dans ce délai vaut refus de communication. Vous pouvez alors saisir la commission d'accès aux documents administratifs (Cada) dans les 2 mois qui suivent.\nCas Auprès des collectivités territoriales: Les mairies, les établissements intercommunaux, les départements et les régions informent le public de toute aide apportée à une association (subvention, garantie d'emprunt, avantage en nature,...). Cette information doit être disponible sur le site internet de la collectivité ou exister sur un support numérique communicable à toute personne qui la demande. Les frais de reproduction des documents sont à votre charge (en tant que demandeur). Ils sont fixés par l’administration concernée et ne peuvent pas dépasser les montants suivants : \nCoût de transmission:\n| Support | Tarif maximum | \n| - | - | \n| Papier | 0,18 € par page A4 (noir et blanc) | \n| Cédérom | 2,75 € |\nSi les documents sont envoyés par courrier, les frais d'envoi peuvent s'ajouter à ces tarifs. Lorsqu'une administration est saisie d'une demande et qu'elle ne possède pas le document demandé, elle le transmet au bon service et en informe le demandeur. Les demandes adressées à une administration doivent être satisfaites dans le mois qui suit. L'absence de réponse dans ce délai vaut refus de communication. Vous pouvez alors saisir la commission d'accès aux documents administratifs (Cada) dans les 2 mois qui suivent.\nCas Auprès de la mission interministérielle de vigilance et de lutte contre les dérives sectaires (Miviludes): En tant que particuliers, vous pouvez interroger la mission interministérielle de vigilance et de lutte contre les dérives sectaires (Miviludes) pour obtenir son avis sur les risques de dérives sectaires dans telle ou telle association .",
  "nb_mots": 794
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F12104 « Comment se renseigner sur une association ? » (chunks 1, 2, 3, 4)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F12104",
   "type": "service-public",
   "doc_id": "F12104",
   "chunks": [
    1,
    2,
    3,
    4
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "points_cles_reference": [
  "Toute personne peut obtenir des informations sur une association déclarée, par internet, par courrier ou sur place",
  "Le Journal officiel des associations en ligne donne le nom, le siège et l'objet, les déclarations (création, modification, dissolution) et les comptes des associations recevant plus de 153 000 € de dons ou subventions par an",
  "data.gouv.fr donne accès au répertoire national des associations et aux listes des associations et fondations reconnues d'utilité publique",
  "Le greffe des associations de la préfecture permet de consulter gratuitement ou de copier les statuts, la déclaration initiale et les déclarations de changements (le règlement intérieur seulement s'il le possède)",
  "Les ministères renseignent sur les agréments et subventions, et les collectivités informent le public des aides qu'elles accordent aux associations",
  "Les copies sont payantes, au plus 0,18 € la page A4 et 2,75 € le cédérom, plus les frais d'envoi éventuels",
  "L'administration doit répondre dans le mois ; sans réponse, c'est un refus, et la Cada peut être saisie dans les 2 mois",
  "La Miviludes peut donner son avis sur les risques de dérives sectaires d'une association"
 ],
 "longueur_demandee": "detaillee"
}
```

## RE-615 — Résumé (difficile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RE-615",
 "tache": "Résumé",
 "difficulte": "difficile",
 "theme": "social-autonomie",
 "entree": {
  "consigne": "Fais un résumé détaillé de ce document, en 400 mots au plus, pour un conseiller d'un CCAS qui reçoit un demandeur d'emploi arrivant en fin de droits : les conditions, les ressources prises en compte, l'âge et l'AAH, la demande, le montant, le cumul avec une activité, le versement et l'arrêt.",
  "document": "Vous avez épuisé vos droits au chômage ? Sachez que l'allocation de solidarité spécifique (ASS) peut vous être accordée si vos ressources mensuelles ne dépassent pas un certain plafond. Le versement de l'ASS peut être maintenu en cas de reprise d'activité, sous plusieurs conditions. Nous vous présentons les informations à connaître.\n\nVoici une liste de différentes questions ou thématiques relatives à ce sujet :\n- Quelles sont les conditions à remplir pour percevoir l'ASS ?\n- Comment demander l'ASS ?\n- Quel est le montant de l'ASS ?\n- Quand est versée l'ASS ?\n- Quand cesse le versement de l'ASS ?\nVous devez remplir toutes les conditions suivantes :\n- Être apte au travail\n- Effectuer des actes positifs et répétés pour retrouver un emploi ou créer/reprendre une entreprise\n- Avoir épuisé vos droits à l'allocation d'aide au retour à l'emploi (ARE) ou à la rémunération de fin de formation (RFF) .\nVous devez avoir travaillé au moins 5 ans (à temps plein ou à temps partiel) au cours des 10 ans avant la fin de votre dernier contrat de travail. Si vous avez cessé votre activité pour élever un enfant, les 5 ans sont réduits d' 1 an par enfant dans la limite de 3 ans. Les périodes d'activité prises en compte sont les suivantes :\n- Périodes accomplies, quel que soit le type de contrat de travail ( CDI , CDD , contrat en intérim, en alternance, etc.), en France ou en Europe\n- Périodes assimilées à des périodes de travail effectif ( service national , formation professionnelle).\nCas Vous vivez seul: Pour percevoir l'ASS, vos ressources mensuelles ne doivent pas dépasser un plafond de 1 363,60 € . Le montant pris en compte est la moyenne des 12 derniers mois du total des ressources perçues avant le mois de votre demande. \nRessources prises en compte ou non pour le droit à l'ASS:\n| Ressources | Prise en compte | \n| - | - | \n| Ressources mensuelles | Oui, si elles sont supérieures à 1 363,60 € | \n| Allocation de solidarité spécifique (ASS) | Oui | \n| Pension alimentaire | Oui, si vous en êtes bénéficiaire. Non, si c'est vous qui la versez. | \n| Allocation d'assurance chômage précédemment perçue | Non | \n| Prestations familiales | Non | \n| Allocation de logement | Non | \n| Majoration de l'ASS | Non | \n| Gratification versée à l'occasion d'un stage obligatoire en entreprise | Non | \n| Revenus d'activité perçus au cours des 12 mois avant votre demande | Non, si leur perception est interrompue à la date de votre demande et s'ils n'ont pas donné lieu à un revenu de substitution ( indemnités journalières de sécurité sociale , allocations de préretraite, par exemple) | \n| Autres ressources ( revenus des valeurs et capitaux mobiliers, revenus fonciers , plus-values ) | Oui, si ces revenus sont imposables. Non, si ces revenus sont exonérés. |\nCas Vous vivez en couple: Pour percevoir l'ASS, vos ressources mensuelles ne doivent pas dépasser 2 142,80 € si vous vivez en couple . Le montant pris en compte est la moyenne des 12 derniers mois du total des ressources perçues avant le mois de votre demande. \nRessources prises en compte ou non pour le droit à l'ASS:\n| Ressources | Prise en compte | \n| - | - | \n| Ressources mensuelles | Oui, si elles sont supérieures à 2 142,80 € | \n| Allocation de solidarité spécifique (ASS) | Oui | \n| Pension alimentaire | Oui, si vous en êtes bénéficiaire. Non, si c'est vous qui la versez. | \n| Allocation d'assurance chômage précédemment perçue | Non | \n| Prestations familiales | Non | \n| Allocation de logement | Non | \n| Majoration de l'ASS | Non | \n| Gratification versée à l'occasion d'un stage obligatoire en entreprise | Non | \n| Revenus d'activité perçus au cours des 12 mois avant votre demande | Non, si leur perception est interrompue à la date de votre demande et s'ils n'ont pas donné lieu à un revenu de substitution ( indemnités journalières de sécurité sociale , allocations de préretraite, par exemple) | \n| Autres ressources ( revenus des valeurs et capitaux mobiliers, revenus fonciers , plus-values ) | Oui, si ces revenus sont imposables. Non, si ces revenus sont exonérés. |\nIl n'y a pas d'âge minimum. Si vous avez suffisamment de trimestres pour percevoir une retraite à taux plein, vous ne pouvez pas toucher l'ASS après l'âge légal de départ à la retraite.\nDepuis 2017, si vous pouvez percevoir l'AAH, vous ne pouvez plus obtenir l'ASS. Toutefois, si vous avez des droits ouverts à ces 2 aides au 31 décembre 2016, vous continuez à les percevoir tant que les conditions d'éligibilité sont remplies, pendant une durée maximum de 10 ans.\nUne demande d'admission à l'ASS vous est adressée par France Travail (anciennement Pôle emploi) à la fin de vos allocations chômage. Vous n'avez aucune démarche à réaliser pour bénéficier de l'ASS. France Travail (anciennement Pôle emploi) adresse directement les imprimés nécessaires à la constitution du dossier d'ASS aux chômeurs en fin de droits qui peuvent en bénéficier. L'ASS est attribuée par périodes de 6 mois renouvelables. Une demande de renouvellement vous est adressée par France Travail en fin de période d'indemnisation.\nSon montant journalier est de 19,48 € ( 584,40 € pour 1 mois de 30 jours).\nCas Vous êtes sans emploi: Cas Vous vivez seul: Ressources et montant - Personne seule:\n| Ressources mensuelles | Montant mensuel de l'ASS | \n| - | - | \n| Moins de 779,20 € | 584,40 € | \n| Entre 779,20 € et 1 363,60 € | 1 363,60 € moins le montant des ressources | \n| Supérieures à 1 363,60 € | Pas d'allocation |\nCas Vous vivez en couple: Ressources et montant - Couple:\n| Ressources mensuelles | Montant mensuel de l'ASS | \n| - | - | \n| Moins de 1 558,40 € | 584,40 € | \n| Entre 1 558,40 € et 2 142,80 € | 2 142,80 € moins le montant des ressources | \n| Supérieures à 2 142,80 € | Pas d'allocation |\nCas Vous travaillez: L'ASS est intégralement cumulable avec les rémunérations de votre activité professionnelle (salariée ou non) pendant 3 mois (consécutifs ou non) dans la limite des droits restants. (À savoir: Pour calculer la période de cumul autorisé, tout mois civil au cours duquel une activité même occasionnelle ou réduite a été exercée est pris en compte.)\nL'ASS vous est versée mensuellement par France Travail à terme échu (par exemple, début novembre pour l'allocation du mois d'octobre).\nCas Vous êtes sans emploi: Le paiement de l'ASS cesse si vous vous trouvez dans l'un des cas suivants : \n- Ressources supérieures aux plafonds\n- Absence de recherche d'emploi\n- Suivi d'une formation rémunérée\n- Reprise d'une activité non cumulable avec l'ASS\n- Perception d'indemnités journalières pour maladie, maternité ou accident du travail\n- Suppression des allocations par décision du préfet ou suite à une radiation\n- Perception de l'allocation de présence parentale ou l'allocation journalière d'accompagnement d'une personne en fin de vie\n- Possibilité de bénéficier d'une retraite à taux plein ou atteinte de l'âge limite d'activité.\nCas Vous travaillez: Après 3 mois (consécutifs ou non) de cumul avec les rémunérations de votre activité professionnelle : \n- Si votre activité professionnelle se poursuit, le versement de l'ASS est interrompu. À la fin du 6 e mois suivant la reprise d'activité, vous pourrez percevoir la prime d'activité en complément de votre rémunération, sous certaines conditions.\n- Si votre activité professionnelle s'interrompt et que s'en suit une période d'inactivité d'au moins 3 mois civils consécutifs (et non au moins 3 mois consécutifs de date à date), une nouvelle période de cumul est possible.",
  "nb_mots": 1116
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F12484 « Allocation de solidarité spécifique (ASS) » (chunks 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F12484",
   "type": "service-public",
   "doc_id": "F12484",
   "chunks": [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "points_cles_reference": [
  "Conditions : être apte au travail, rechercher activement un emploi, avoir épuisé ses droits à l'ARE (ou à la RFF), et avoir travaillé au moins 5 ans dans les 10 ans avant la fin du dernier contrat (réduits d'1 an par enfant élevé, dans la limite de 3 ans)",
  "Plafond de ressources mensuelles (moyenne des 12 derniers mois) : 1 363,60 € pour une personne seule, 2 142,80 € pour un couple ; certaines ressources ne sont pas comptées (prestations familiales, allocation de logement, allocation chômage précédente…)",
  "Pas d'âge minimum, mais pas d'ASS après l'âge légal de la retraite si l'on a assez de trimestres pour le taux plein ; depuis 2017, pas d'ASS si l'on peut percevoir l'AAH (sauf droits ouverts aux 2 aides au 31 décembre 2016)",
  "Aucune démarche : France Travail envoie la demande à la fin des allocations chômage ; l'ASS est accordée par périodes de 6 mois renouvelables",
  "Montant : 19,48 € par jour (584,40 € pour 30 jours), réduit au-delà de 779,20 € de ressources pour une personne seule ou 1 558,40 € pour un couple",
  "En cas de reprise d'activité, cumul intégral pendant 3 mois (consécutifs ou non) ; ensuite, l'ASS s'arrête si l'activité continue (prime d'activité possible à la fin du 6e mois)",
  "Versement mensuel à terme échu par France Travail ; arrêt notamment en cas de ressources trop élevées, d'absence de recherche d'emploi, de formation rémunérée, d'indemnités journalières ou de droit à la retraite à taux plein"
 ],
 "longueur_demandee": "detaillee"
}
```

## RE-619 — Résumé (difficile, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RE-619",
 "tache": "Résumé",
 "difficulte": "difficile",
 "theme": "famille-education-sante",
 "entree": {
  "consigne": "Fais un résumé détaillé de ce document, en 400 mots au plus, pour une assistante sociale de secteur qui accompagne une famille en difficulté : les conditions d'intervention du juge, qui peut le saisir, les mesures possibles (maintien dans la famille, AEMO, placement, interdiction de sortie du territoire, médiation) et leur modification.",
  "document": "Pour protéger un mineur en danger, le juge des enfants peut prendre des mesures d'assistance éducative (allant de la mesure de suivi et d'aide à la famille à une mesure de placement de l'enfant).\n\nVoici une liste de différentes questions ou thématiques relatives à ce sujet :\n- Dans quels cas et comment le juge des enfants peut intervenir pour protéger un mineur en danger ?\n- Quelles sont les mesures que peut prendre le juge des enfants pour protéger un mineur en danger ?\n- Les mesures prises par le juge des enfants pour protéger un mineur en danger peuvent-elles être modifiées ?\nAvant de saisir le juge, les services du département (notamment l’aide sociale à l’enfance - ASE) proposent des aides aux familles, avec leur accord. Le juge des enfants n’intervient que dans l’un des cas suivants :\n- L’aide apportée n’est pas suffisante\n- L’aide est refusée\n- Ou l’aide est rendue impossible.\nC’est ce qu’on appelle le principe de subsidiarité : cela signifie que le recours au juge est une solution de dernier recours, lorsque les autres dispositifs de protection ne permettent pas de garantir la sécurité ou le bon développement de l’enfant.\nL'intervention du juge doit être sollicitée lorsque l'un des risques graves suivants pèse sur le mineur :\n- Sa santé physique\n\n- Sa santé mentale ou psychologique (par exemple, troubles du comportement)\n\n- Sa sécurité physique (par exemple, violences )\n\n- Sa sécurité matérielle (par exemple, logement précaire)\n\n- Sa moralité (par exemple, exposition à la délinquance)\n\n- Son éducation.\nLes personnes suivantes peuvent recourir au juge des enfants :\n- Enfant lui-même\n- Parents de l'enfant agissant ensemble, ou l'un d'entre eux agissant seul\n- Tuteur ou famille d'accueil du mineur ou tout autre personne ayant la charge de l'enfant\n- Aide sociale à l'enfance (Ase) ou tout autre service ayant la charge de l'enfance\n- Procureur de la République, qui est généralement prévenu par les services du département ou par tout fonctionnaire témoin d'une infraction commise contre ou par l'enfant.\n(À savoir: À titre exceptionnel, le juge peut décider de lui-même d'une mesure d'assistance éducative.)\nLa demande d'intervention du juge des enfants doit être faite via une requête déposée au tribunal judiciaire du domicile des parents ou de la famille d'accueil, du tuteur ou de tout autre personne ou service ayant la charge de l'enfant. (À noter: S'il y a plusieurs enfants d'une même famille habitant à des endroits différents, l'affaire sera centralisée auprès d' un seul juge des enfants.)\nLe juge des enfants essaie, dans la mesure du possible, de maintenir l'enfant dans sa famille. Il peut désigner une personne qualifiée ou un service spécialisé pour aider la famille. La personne qualifiée est chargée d’accompagner l’enfant et sa famille au quotidien. Elle apporte des conseils éducatifs, un soutien personnalisé et peut orienter la famille vers des services adaptés. Le service spécialisé doit mettre en place un accompagnement social et éducatif de la famille pour assurer la santé, la sécurité et l'éducation de l'enfant. L'enfant peut également bénéficier d'un accompagnement psychologique. Quand l'enfant est suivi par un service spécialisé, il peut y être hébergé de façon exceptionnelle ou périodique (1 semaine par mois par exemple). Le juge peut soumettre l'enfant ou ses parents au respect de certaines obligations. Elles peuvent être les suivantes :\n- Suivre une scolarité (être inscrit dans un établissement sanitaire ou d'éducation, y compris en internat)\n- Exercer une activité professionnelle par l'enfant, s'il est en âge de travailler\n- Respecter un suivi psychologique ou médical.\nSi l'enfant est suivi par un service spécialisé, la mesure peut durer 2 ans maximum, renouvelable 1 fois. Si l'enfant est suivi par une personne qualifiée, il n'y a pas de durée maximale. Le juge peut également ordonner une aide à la gestion du budget familial, dont le but est de rétablir l'autonomie financière de la famille ou une aide éducative à domicile dont le but est de restaurer les liens entre les parents et l'enfant.\nLe juge peut également ordonner une assistance éducative en milieu ouvert (AEMO). Cette mesure permet d’intervenir auprès de l’enfant et de ses parents sans les séparer, par un suivi éducatif renforcé à domicile. Elle est mise en œuvre par un service spécialisé et vise à aider les familles à résoudre les difficultés mettant en danger l’enfant. La durée est fixée par le juge (jusqu’à 2 ans, renouvelable), en fonction de la situation.\nLe juge des enfants peut décider d'une mesure de placement dans les cas les plus graves. Cette mesure ne retire pas l'autorité parentale aux parents de l'enfant. Cette mesure est fixée pour une durée de 2 ans maximum, renouvelable 1 fois. Toutefois, il est possible que les mesures soient ordonnées pour une durée supérieure si la situation de la famille l'exige. Les parents peuvent obtenir un droit de visite. Les frais occasionnés par la prise en charge du mineur doivent être payés par les parents, sauf décision contraire du juge.\nDans certaines situations, le juge peut restreindre temporairement la possibilité pour l’enfant de voyager à l’étranger, pour assurer sa sécurité. Le juge des enfants a la faculté d’ordonner une interdiction de sortie du territoire (IST) en parallèle d’une autre mesure d’assistance éducative. Tel peut être le cas par exemple lorsque l'enfant est placé chez l'autre parent. Ainsi, l'enfant ne pourra pas quitter la France sans l'autorisation du juge. L'accord de ses 2 parents ne suffira pas. L’interdiction de sortie du territoire est prise pour une durée maximale de 2 ans.\nLe juge des enfants peut ordonner une médiation familiale dans le cadre de l'assistance éducative. Le juge des enfants doit informer les parents sur les dispositifs d’accompagnement mis en place par le département, et dont ils peuvent bénéficier. Il s'agit notamment :\n- de l'aide à domicile,\n- de l'accueil en centre parental.\nPour que la médiation familiale puisse avoir lieu, les 2 conditions suivantes doivent être réunies :\n- Cette mesure doit obligatoirement accompagner une autre mesure d’assistance éducative (exemple : mesure de placement de l'enfant en famille d'accueil)\n- L'accord des parents est nécessaire.\n(À noter: En cas de violence ou d'emprise d'un parent sur l'autre parent ou l'enfant, le recours à la médiation familiale est impossible, le but étant de protéger la ou les victime(s).)\nLe juge des enfants peut modifier lui-même les mesures d'assistance éducative déjà en place. Cette modification peut également être demandée par les personnes suivantes :\n- Enfant lui-même\n\n- Parents, agissant ensemble ou séparément, ou le tuteur de l'enfant\n- Personne ou service à qui l'enfant a été confié\n- Procureur de la République\nLa demande doit être adressée au juge des enfants, généralement par courrier ou par déclaration au greffe du tribunal judiciaire. Le juge doit systématiquement :\n- Effectuer un entretien individuel avec l’enfant capable de discernement\n- Demander la désignation d’un avocat pour l’enfant capable de discernement ou d’un administrateur ad hoc pour l’enfant non capable de discernement, lorsque l’intérêt de l’enfant l’exige.",
  "nb_mots": 1115
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F17777 « Comment le juge des enfants intervient-il pour protéger un mineur en danger ? » (chunks 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F17777",
   "type": "service-public",
   "doc_id": "F17777",
   "chunks": [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 2,
 "points_cles_reference": [
  "Le juge des enfants n'intervient qu'en dernier recours (principe de subsidiarité), si l'aide du département (aide sociale à l'enfance) est insuffisante, refusée ou impossible",
  "Son intervention est demandée en cas de risque grave pour la santé physique ou mentale, la sécurité physique ou matérielle, la moralité ou l'éducation du mineur",
  "Peuvent saisir le juge : l'enfant, ses parents (ensemble ou séparément), le tuteur ou la personne qui en a la charge, l'aide sociale à l'enfance, le procureur ; le juge peut aussi se saisir lui-même exceptionnellement ; requête au tribunal judiciaire du domicile",
  "Le juge cherche à maintenir l'enfant dans sa famille : personne qualifiée (sans durée maximale) ou service spécialisé (2 ans maximum, renouvelable une fois), obligations (scolarité, activité, suivi médical), aide à la gestion du budget, aide éducative à domicile, assistance éducative en milieu ouvert (AEMO)",
  "Dans les cas les plus graves, placement de l'enfant, pour 2 ans maximum renouvelable une fois (durée supérieure possible si la situation de la famille l'exige), sans retrait de l'autorité parentale ; droit de visite possible ; frais à la charge des parents sauf décision contraire",
  "Le juge peut prononcer une interdiction de sortie du territoire de 2 ans au plus, en complément d'une autre mesure",
  "Une médiation familiale peut accompagner une autre mesure, avec l'accord des parents, sauf en cas de violence ou d'emprise",
  "Les mesures peuvent être modifiées par le juge, d'office ou à la demande de l'enfant, des parents, du tuteur, de la personne qui en a la charge ou du procureur ; le juge doit systématiquement entendre l'enfant capable de discernement et demander la désignation d'un avocat pour l'enfant capable de discernement ou d'un administrateur ad hoc pour l'enfant non capable de discernement, lorsque l'intérêt de l'enfant l'exige"
 ],
 "longueur_demandee": "detaillee"
}
```
