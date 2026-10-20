# Échantillon de relecture du Jeu d'évaluation dev1

- Statut du gel : `relu-llm`
- Gelé le : 2026-10-20T16:37:12.264555+02:00
- Graine : 42
- Items : 48 sur 159 (20 % stratifié Tâche × difficulté, au moins 1 par strate)

Les scores restent « non relus » tant que la relecture n'est pas validée (FR-25).

## CO-504 — Correction (facile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CO-504",
 "tache": "Correction",
 "difficulte": "facile",
 "theme": "collectivites",
 "entree": {
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "texte": "Avis aux habitants du quartier des Tilleuls. Des travaux de réfection de la chaussée aura lieu rue des Écoles du lundi 9 au vendredi 20 novembre, de 8 heures à 17 heures. Pendant cette période, la circulation sera interdit entre la place de la Mairie et le carrefour du Moulin. Une déviation sera mis en place par l'avenue Jean-Moulin. Le stationnement sera également interdit des deux côtés de la rue. Les riverains pourront accédé à leur garage en dehors des heures de travaux. La collecte des ordures ménagères est maintenue : les bacs devront être déposé la veille au soir à l'angle de la rue du Stade. Les services techniques de la commune vous prient de les excuser pour la gêne occasionné et restent à votre disposition pour toute question au numéro indiqué sur le panneau de chantier.",
  "nb_mots": 137
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Avis aux habitants sur des travaux de voirie (texte fictif rédigé pour l'évaluation)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "fautes": [
  {
   "debut": 85,
   "fin": 89,
   "erreur": "aura",
   "correction": "auront",
   "type": "accord sujet-verbe",
   "contexte_fautif": "Des travaux de réfection de la chaussée aura lieu"
  },
  {
   "debut": 214,
   "fin": 222,
   "erreur": "interdit",
   "correction": "interdite",
   "type": "accord du participe passé",
   "contexte_fautif": "la circulation sera interdit entre"
  },
  {
   "debut": 297,
   "fin": 300,
   "erreur": "mis",
   "correction": "mise",
   "type": "accord du participe passé",
   "contexte_fautif": "Une déviation sera mis en place"
  },
  {
   "debut": 426,
   "fin": 432,
   "erreur": "accédé",
   "correction": "accéder",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "Les riverains pourront accédé à leur garage"
  },
  {
   "debut": 552,
   "fin": 558,
   "erreur": "déposé",
   "correction": "déposés",
   "type": "accord du participe passé",
   "contexte_fautif": "les bacs devront être déposé la veille"
  },
  {
   "debut": 685,
   "fin": 695,
   "erreur": "occasionné",
   "correction": "occasionnée",
   "type": "accord du participe passé",
   "contexte_fautif": "vous prient de les excuser pour la gêne occasionné"
  }
 ],
 "texte_corrige_reference": "Avis aux habitants du quartier des Tilleuls. Des travaux de réfection de la chaussée auront lieu rue des Écoles du lundi 9 au vendredi 20 novembre, de 8 heures à 17 heures. Pendant cette période, la circulation sera interdite entre la place de la Mairie et le carrefour du Moulin. Une déviation sera mise en place par l'avenue Jean-Moulin. Le stationnement sera également interdit des deux côtés de la rue. Les riverains pourront accéder à leur garage en dehors des heures de travaux. La collecte des ordures ménagères est maintenue : les bacs devront être déposés la veille au soir à l'angle de la rue du Stade. Les services techniques de la commune vous prient de les excuser pour la gêne occasionnée et restent à votre disposition pour toute question au numéro indiqué sur le panneau de chantier.",
 "nb_fautes": 6,
 "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte"
}
```

## CO-505 — Correction (facile, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CO-505",
 "tache": "Correction",
 "difficulte": "facile",
 "theme": "etat-civil-papiers",
 "entree": {
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "texte": "Madame, votre demande de copie intégrale d'acte de mariage a bien été reçu par le service de l'état civil le 12 octobre. L'acte demandé a été établi dans notre commune en 1998 ; nous pouvons donc vous le délivré. Le document vous sera adresser par courrier à l'adresse indiquée dans votre demande, dans un délai de dix jours ouvrés. Nous vous rappelons que la copie intégrale ne peut être délivré qu'aux personnes mentionnés dans l'acte, à leurs ascendants ou descendants, ou sur autorisation du procureur de la République. Si vous avez besoin d'un extrait plutôt que d'une copie intégrale, merci de nous le préciser par retour de courriel. Nous restont à votre disposition pour tout renseignement complémentaire. Le service de l'état civil",
  "nb_mots": 121
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Courriel du service de l'état civil à une usagère (texte fictif rédigé pour l'évaluation)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "fautes": [
  {
   "debut": 70,
   "fin": 74,
   "erreur": "reçu",
   "correction": "reçue",
   "type": "accord du participe passé",
   "contexte_fautif": "a bien été reçu par le service"
  },
  {
   "debut": 204,
   "fin": 211,
   "erreur": "délivré",
   "correction": "délivrer",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "nous pouvons donc vous le délivré"
  },
  {
   "debut": 235,
   "fin": 243,
   "erreur": "adresser",
   "correction": "adressé",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "Le document vous sera adresser par courrier"
  },
  {
   "debut": 389,
   "fin": 396,
   "erreur": "délivré",
   "correction": "délivrée",
   "type": "accord du participe passé",
   "contexte_fautif": "la copie intégrale ne peut être délivré"
  },
  {
   "debut": 414,
   "fin": 424,
   "erreur": "mentionnés",
   "correction": "mentionnées",
   "type": "accord du participe passé",
   "contexte_fautif": "aux personnes mentionnés dans l'acte"
  },
  {
   "debut": 646,
   "fin": 653,
   "erreur": "restont",
   "correction": "restons",
   "type": "conjugaison",
   "contexte_fautif": "Nous restont à votre disposition"
  }
 ],
 "texte_corrige_reference": "Madame, votre demande de copie intégrale d'acte de mariage a bien été reçue par le service de l'état civil le 12 octobre. L'acte demandé a été établi dans notre commune en 1998 ; nous pouvons donc vous le délivrer. Le document vous sera adressé par courrier à l'adresse indiquée dans votre demande, dans un délai de dix jours ouvrés. Nous vous rappelons que la copie intégrale ne peut être délivrée qu'aux personnes mentionnées dans l'acte, à leurs ascendants ou descendants, ou sur autorisation du procureur de la République. Si vous avez besoin d'un extrait plutôt que d'une copie intégrale, merci de nous le préciser par retour de courriel. Nous restons à votre disposition pour tout renseignement complémentaire. Le service de l'état civil",
 "nb_fautes": 6,
 "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte"
}
```

## CO-510 — Correction (moyen, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CO-510",
 "tache": "Correction",
 "difficulte": "moyen",
 "theme": "collectivites",
 "entree": {
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "texte": "L'attestation de vigilance délivré par l'Urssaf certifit que l'entreprise est en règle lorsqu'elle se trouve dans une des situations suivantes :\n- Elle a payer ses cotisations et contributions à la date à laquelle elles doivent être payés.\n- Elle a souscris un plan d'apurement des cotisations et contributions et elle respecte ce plan.\n- Elle a payé ses cotisations et ses contributions, mais n'ait pas à jour dans le paiement des majorations et pénalités.\n- Elle n'a pas payé ses cotisations et contributions, mais en contestent le montant par recours contentieux.\nLorsque le marché public est supérieur ou égal à 5 000 € hors taxes, l'entreprise doit fournir cette attestation de vigilance tous les 6 mois jusqu'à la fin de l'exécution du marché. La demande doit être fait avant l’expiration de l'attestation précédente.",
  "nb_mots": 128
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F23384 « Fournir des attestations de régularité fiscale et de vigilance dans un marché public » (chunks 4)",
   "url": "https://entreprendre.service-public.gouv.fr/vosdroits/F23384",
   "type": "service-public",
   "doc_id": "F23384",
   "chunks": [
    4
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
   "debut": 27,
   "fin": 34,
   "erreur": "délivré",
   "correction": "délivrée",
   "type": "accord du participe passé",
   "contexte_fautif": "L'attestation de vigilance délivré par l'Urssaf"
  },
  {
   "debut": 48,
   "fin": 56,
   "erreur": "certifit",
   "correction": "certifie",
   "type": "conjugaison",
   "contexte_fautif": "certifit que l'entreprise est en règle"
  },
  {
   "debut": 154,
   "fin": 159,
   "erreur": "payer",
   "correction": "payé",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "Elle a payer ses cotisations et contributions à la date"
  },
  {
   "debut": 233,
   "fin": 238,
   "erreur": "payés",
   "correction": "payées",
   "type": "accord du participe passé",
   "contexte_fautif": "à laquelle elles doivent être payés"
  },
  {
   "debut": 249,
   "fin": 257,
   "erreur": "souscris",
   "correction": "souscrit",
   "type": "accord du participe passé",
   "contexte_fautif": "Elle a souscris un plan d'apurement"
  },
  {
   "debut": 394,
   "fin": 399,
   "erreur": "n'ait",
   "correction": "n'est",
   "type": "homophone grammatical (est / ait)",
   "contexte_fautif": "mais n'ait pas à jour dans le paiement"
  },
  {
   "debut": 520,
   "fin": 530,
   "erreur": "contestent",
   "correction": "conteste",
   "type": "accord sujet-verbe",
   "contexte_fautif": "mais en contestent le montant par recours contentieux"
  },
  {
   "debut": 771,
   "fin": 775,
   "erreur": "fait",
   "correction": "faite",
   "type": "accord du participe passé",
   "contexte_fautif": "La demande doit être fait avant"
  }
 ],
 "texte_corrige_reference": "L'attestation de vigilance délivrée par l'Urssaf certifie que l'entreprise est en règle lorsqu'elle se trouve dans une des situations suivantes :\n- Elle a payé ses cotisations et contributions à la date à laquelle elles doivent être payées.\n- Elle a souscrit un plan d'apurement des cotisations et contributions et elle respecte ce plan.\n- Elle a payé ses cotisations et ses contributions, mais n'est pas à jour dans le paiement des majorations et pénalités.\n- Elle n'a pas payé ses cotisations et contributions, mais en conteste le montant par recours contentieux.\nLorsque le marché public est supérieur ou égal à 5 000 € hors taxes, l'entreprise doit fournir cette attestation de vigilance tous les 6 mois jusqu'à la fin de l'exécution du marché. La demande doit être faite avant l’expiration de l'attestation précédente.",
 "nb_fautes": 8,
 "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte"
}
```

## CO-512 — Correction (moyen, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CO-512",
 "tache": "Correction",
 "difficulte": "moyen",
 "theme": "collectivites",
 "entree": {
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "texte": "Compte rendu de la commission urbanisme du 3 février. Était présents les membres de la commission ainsi que le responsable du service urbanisme. La commission a examiné les demandes de permis de construire déposés depuis la dernière réunion. Huit dossiers ont été étudié : six ont reçu un avis favorable, deux ont été ajourné dans l'attente de pièces complémentaires. Les membres ont ensuite abordé la révision du règlement de voirie. Plusieurs élus ont souhaités que les règles applicables aux clôtures soit précisées, notamment leur hauteur maximale. Le service urbanisme proposerat une rédaction lors de la prochaine séance. Enfin, la commission a pris connaissance des remarques formulés par les riverains du lotissement des Peupliers sur l'éclairage public. Une réponse leur sera adressée par le maire. La prochaine réunion est fixée au 2 mars à 18 heures.",
  "nb_mots": 134
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Compte rendu d'une commission municipale d'urbanisme (texte fictif rédigé pour l'évaluation)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "fautes": [
  {
   "debut": 54,
   "fin": 59,
   "erreur": "Était",
   "correction": "Étaient",
   "type": "accord sujet-verbe",
   "contexte_fautif": "Était présents les membres"
  },
  {
   "debut": 206,
   "fin": 213,
   "erreur": "déposés",
   "correction": "déposées",
   "type": "accord du participe passé",
   "contexte_fautif": "les demandes de permis de construire déposés"
  },
  {
   "debut": 264,
   "fin": 270,
   "erreur": "étudié",
   "correction": "étudiés",
   "type": "accord du participe passé",
   "contexte_fautif": "Huit dossiers ont été étudié"
  },
  {
   "debut": 318,
   "fin": 325,
   "erreur": "ajourné",
   "correction": "ajournés",
   "type": "accord du participe passé",
   "contexte_fautif": "deux ont été ajourné dans l'attente"
  },
  {
   "debut": 454,
   "fin": 463,
   "erreur": "souhaités",
   "correction": "souhaité",
   "type": "accord du participe passé",
   "contexte_fautif": "Plusieurs élus ont souhaités que les règles"
  },
  {
   "debut": 504,
   "fin": 508,
   "erreur": "soit",
   "correction": "soient",
   "type": "accord sujet-verbe",
   "contexte_fautif": "applicables aux clôtures soit précisées"
  },
  {
   "debut": 574,
   "fin": 584,
   "erreur": "proposerat",
   "correction": "proposera",
   "type": "conjugaison",
   "contexte_fautif": "Le service urbanisme proposerat une rédaction"
  },
  {
   "debut": 683,
   "fin": 691,
   "erreur": "formulés",
   "correction": "formulées",
   "type": "accord du participe passé",
   "contexte_fautif": "formulés par les riverains du lotissement"
  }
 ],
 "texte_corrige_reference": "Compte rendu de la commission urbanisme du 3 février. Étaient présents les membres de la commission ainsi que le responsable du service urbanisme. La commission a examiné les demandes de permis de construire déposées depuis la dernière réunion. Huit dossiers ont été étudiés : six ont reçu un avis favorable, deux ont été ajournés dans l'attente de pièces complémentaires. Les membres ont ensuite abordé la révision du règlement de voirie. Plusieurs élus ont souhaité que les règles applicables aux clôtures soient précisées, notamment leur hauteur maximale. Le service urbanisme proposera une rédaction lors de la prochaine séance. Enfin, la commission a pris connaissance des remarques formulées par les riverains du lotissement des Peupliers sur l'éclairage public. Une réponse leur sera adressée par le maire. La prochaine réunion est fixée au 2 mars à 18 heures.",
 "nb_fautes": 8,
 "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte"
}
```

## CO-515 — Correction (difficile, thème `travail-emploi`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CO-515",
 "tache": "Correction",
 "difficulte": "difficile",
 "theme": "travail-emploi",
 "entree": {
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "texte": "Les agents publics bénéficie de la liberté de conscience, comme tous citoyen. Un agent public est libres d'appartenir ou de ne pas appartenir à une religion et d'exercé une pratique religieuse à titre privé en vertu de la liberté d’opinion. En contrepartie, il doit respecté une obligation de neutralité en application de laquelle il ne doit pas, dans l’exercice de ses fonctions, avoir les comportements suivants :\n- Manifester ses convictions qu’elle soient religieuses, philosophiques ou politiques, à l’égard des usagers et de ses collègues,\n- Faire prévalloir sa préférence pour une religion.\nAinsi, l’agent public ne doit porter aucun signe religieux destiné à marquer son appartenance à une religion. Il ne doit pas fait preuve de prosélytisme, c'est-à-dire avoir une attitude ayants pour but de diffuser ses convictions religieuses auprès des usagers et de ses collègues. De manière plus générale, l’agent public doit traiter toute les personnes de façon égale et respecter leur liberté de conscience et leur dignité. Exemple: Le fait d’utiliser ses fonctions de guichetier pour remettre aux usagers du service public des imprimés à caractère religieux a été considérés comme constitutif d'un manquemant à l'obligation de neutralité.",
  "nb_mots": 188
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F530 « Devoirs de réserve, de discrétion, de neutralité et secret professionnels dans la fonction publique » (chunks 5)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F530",
   "type": "service-public",
   "doc_id": "F530",
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
   "debut": 19,
   "fin": 28,
   "erreur": "bénéficie",
   "correction": "bénéficient",
   "type": "accord sujet-verbe",
   "contexte_fautif": "Les agents publics bénéficie de la liberté"
  },
  {
   "debut": 64,
   "fin": 68,
   "erreur": "tous",
   "correction": "tout",
   "type": "accord du déterminant",
   "contexte_fautif": "comme tous citoyen"
  },
  {
   "debut": 98,
   "fin": 104,
   "erreur": "libres",
   "correction": "libre",
   "type": "accord de l'adjectif",
   "contexte_fautif": "Un agent public est libres d'appartenir"
  },
  {
   "debut": 160,
   "fin": 168,
   "erreur": "d'exercé",
   "correction": "d'exercer",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "et d'exercé une pratique religieuse à titre privé"
  },
  {
   "debut": 266,
   "fin": 274,
   "erreur": "respecté",
   "correction": "respecter",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "il doit respecté une obligation de neutralité"
  },
  {
   "debut": 445,
   "fin": 452,
   "erreur": "qu’elle",
   "correction": "qu’elles",
   "type": "homophone grammatical (qu'elles / qu'elle)",
   "contexte_fautif": "Manifester ses convictions qu’elle soient religieuses"
  },
  {
   "debut": 554,
   "fin": 564,
   "erreur": "prévalloir",
   "correction": "prévaloir",
   "type": "orthographe lexicale",
   "contexte_fautif": "Faire prévalloir sa préférence pour une religion"
  },
  {
   "debut": 723,
   "fin": 727,
   "erreur": "fait",
   "correction": "faire",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "Il ne doit pas fait preuve de prosélytisme"
  },
  {
   "debut": 784,
   "fin": 790,
   "erreur": "ayants",
   "correction": "ayant",
   "type": "accord du participe présent",
   "contexte_fautif": "avoir une attitude ayants pour but de diffuser"
  },
  {
   "debut": 934,
   "fin": 939,
   "erreur": "toute",
   "correction": "toutes",
   "type": "accord du déterminant",
   "contexte_fautif": "traiter toute les personnes de façon égale"
  },
  {
   "debut": 1167,
   "fin": 1177,
   "erreur": "considérés",
   "correction": "considéré",
   "type": "accord du participe passé",
   "contexte_fautif": "des imprimés à caractère religieux a été considérés"
  },
  {
   "debut": 1201,
   "fin": 1211,
   "erreur": "manquemant",
   "correction": "manquement",
   "type": "orthographe lexicale",
   "contexte_fautif": "constitutif d'un manquemant à l'obligation"
  }
 ],
 "texte_corrige_reference": "Les agents publics bénéficient de la liberté de conscience, comme tout citoyen. Un agent public est libre d'appartenir ou de ne pas appartenir à une religion et d'exercer une pratique religieuse à titre privé en vertu de la liberté d’opinion. En contrepartie, il doit respecter une obligation de neutralité en application de laquelle il ne doit pas, dans l’exercice de ses fonctions, avoir les comportements suivants :\n- Manifester ses convictions qu’elles soient religieuses, philosophiques ou politiques, à l’égard des usagers et de ses collègues,\n- Faire prévaloir sa préférence pour une religion.\nAinsi, l’agent public ne doit porter aucun signe religieux destiné à marquer son appartenance à une religion. Il ne doit pas faire preuve de prosélytisme, c'est-à-dire avoir une attitude ayant pour but de diffuser ses convictions religieuses auprès des usagers et de ses collègues. De manière plus générale, l’agent public doit traiter toutes les personnes de façon égale et respecter leur liberté de conscience et leur dignité. Exemple: Le fait d’utiliser ses fonctions de guichetier pour remettre aux usagers du service public des imprimés à caractère religieux a été considéré comme constitutif d'un manquement à l'obligation de neutralité.",
 "nb_fautes": 12,
 "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte"
}
```

## CO-517 — Correction (difficile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CO-517",
 "tache": "Correction",
 "difficulte": "difficile",
 "theme": "social-autonomie",
 "entree": {
  "consigne": "Corrige l'orthographe et la grammaire de ce texte. Ne modifie rien d'autre.",
  "texte": "Note à l'attention de Monsieur le Maire. Objet : bilan du service de portage de repas à domicile. Le service de portage de repas, gérer par le centre communal d'action sociale, a livrés l'an dernier 14 200 repas à 96 bénéficiaires, contre 12 800 repas l'année précédente. La hausse s'expliquent principalement par l'arrivée de nouveaux bénéficiaires sorti d'hospitalisation, que les services sociaux de l'hôpital nous ont orienté. Les repas sont préparé par la cuisine centrale et livré en liaison froide, cinq jours par semaine. Les deux agents chargés des tournées ont parcourus environ 21 000 kilomètres. Les retours receuillis lors de l'enquête de satisfaction sont globalement positifs, même si plusieurs personnes ont regrettées que les menus ne soient pas assez variées. Le véhicule utilisé pour la tournée du secteur nord, acquis il y a douze ans, présente des pannes de plus en plus fréquents. Je vous propose donc d'inscrire son remplacement au budget de l'année prochaine. Je me tiens à votre disposition pour en discuter. La directrice du CCAS",
  "nb_mots": 168
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Note de la directrice du CCAS au maire (texte fictif rédigé pour l'évaluation)"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "fautes": [
  {
   "debut": 130,
   "fin": 135,
   "erreur": "gérer",
   "correction": "géré",
   "type": "confusion infinitif / participe passé",
   "contexte_fautif": "gérer par le centre communal"
  },
  {
   "debut": 179,
   "fin": 185,
   "erreur": "livrés",
   "correction": "livré",
   "type": "accord du participe passé",
   "contexte_fautif": "a livrés l'an dernier 14 200 repas"
  },
  {
   "debut": 282,
   "fin": 294,
   "erreur": "s'expliquent",
   "correction": "s'explique",
   "type": "accord sujet-verbe",
   "contexte_fautif": "La hausse s'expliquent principalement"
  },
  {
   "debut": 350,
   "fin": 355,
   "erreur": "sorti",
   "correction": "sortis",
   "type": "accord du participe passé",
   "contexte_fautif": "de nouveaux bénéficiaires sorti d'hospitalisation"
  },
  {
   "debut": 422,
   "fin": 429,
   "erreur": "orienté",
   "correction": "orientés",
   "type": "accord du participe passé",
   "contexte_fautif": "les services sociaux de l'hôpital nous ont orienté"
  },
  {
   "debut": 446,
   "fin": 453,
   "erreur": "préparé",
   "correction": "préparés",
   "type": "accord du participe passé",
   "contexte_fautif": "Les repas sont préparé par la cuisine centrale"
  },
  {
   "debut": 481,
   "fin": 486,
   "erreur": "livré",
   "correction": "livrés",
   "type": "accord du participe passé",
   "contexte_fautif": "et livré en liaison froide"
  },
  {
   "debut": 571,
   "fin": 580,
   "erreur": "parcourus",
   "correction": "parcouru",
   "type": "accord du participe passé",
   "contexte_fautif": "Les deux agents chargés des tournées ont parcourus"
  },
  {
   "debut": 620,
   "fin": 630,
   "erreur": "receuillis",
   "correction": "recueillis",
   "type": "orthographe lexicale",
   "contexte_fautif": "Les retours receuillis lors de l'enquête"
  },
  {
   "debut": 724,
   "fin": 734,
   "erreur": "regrettées",
   "correction": "regretté",
   "type": "accord du participe passé",
   "contexte_fautif": "plusieurs personnes ont regrettées que les menus"
  },
  {
   "debut": 769,
   "fin": 776,
   "erreur": "variées",
   "correction": "variés",
   "type": "accord de l'adjectif",
   "contexte_fautif": "ne soient pas assez variées"
  },
  {
   "debut": 892,
   "fin": 901,
   "erreur": "fréquents",
   "correction": "fréquentes",
   "type": "accord de l'adjectif",
   "contexte_fautif": "des pannes de plus en plus fréquents"
  }
 ],
 "texte_corrige_reference": "Note à l'attention de Monsieur le Maire. Objet : bilan du service de portage de repas à domicile. Le service de portage de repas, géré par le centre communal d'action sociale, a livré l'an dernier 14 200 repas à 96 bénéficiaires, contre 12 800 repas l'année précédente. La hausse s'explique principalement par l'arrivée de nouveaux bénéficiaires sortis d'hospitalisation, que les services sociaux de l'hôpital nous ont orientés. Les repas sont préparés par la cuisine centrale et livrés en liaison froide, cinq jours par semaine. Les deux agents chargés des tournées ont parcouru environ 21 000 kilomètres. Les retours recueillis lors de l'enquête de satisfaction sont globalement positifs, même si plusieurs personnes ont regretté que les menus ne soient pas assez variés. Le véhicule utilisé pour la tournée du secteur nord, acquis il y a douze ans, présente des pannes de plus en plus fréquentes. Je vous propose donc d'inscrire son remplacement au budget de l'année prochaine. Je me tiens à votre disposition pour en discuter. La directrice du CCAS",
 "nb_fautes": 12,
 "note_positions": "debut/fin = indices de caractères (Python, 0-indexé, fin exclue) dans entree.texte"
}
```

## CR-501 — Compte rendu (facile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CR-501",
 "tache": "Compte rendu",
 "difficulte": "facile",
 "theme": "collectivites",
 "entree": {
  "consigne": "Rédige le compte rendu de cette réunion de service : participants, points abordés, décisions, actions (responsable, échéance).",
  "notes": "Réunion de service Urbanisme – jeudi 8 octobre 2026 – 14 h – salle 2, mairie de Saint-Aubin-des-Prés\nPrésents : M. Delmas (responsable du service, anime), Mme Ortega et M. Vidal (instructeurs), Mme Kerbrat (assistante, prend les notes)\nAbsent excusé : M. Fontaine (adjoint au maire chargé de l'urbanisme), en déplacement\nNotes : Kerbrat\n\n1. Délais d'instruction\n- 41 dossiers en cours, dont 9 permis de construire et 32 déclarations préalables. Vidal signale 3 dossiers proches de la date limite (risque de permis tacite).\n- DÉCISION : point hebdo de 15 min le lundi à 9 h pour suivre les dossiers proches de l'échéance, à partir du lundi 12 octobre.\n→ Vidal prépare un tableau de suivi des échéances pour le premier point du 12/10.\n- Ortega demande un 3e instructeur à mi-temps. Delmas : à voir avec la DGS lors du budget 2027, rien de décidé.\n\n2. Dématérialisation des demandes\n- Hausse des dépôts en ligne : 64 % en septembre contre 48 % en mars.\n- Les usagers appellent souvent pour savoir quelles pièces joindre. DÉCISION : mise à jour de la page « Urbanisme » du site avec la liste des pièces par type de demande.\n→ Kerbrat rédige le texte et l'envoie au service communication avant le vendredi 23 octobre.\n- Vidal propose un atelier mensuel pour aider les habitants à déposer en ligne. Delmas trouve l'idée intéressante mais veut l'avis de M. Fontaine : en suspens.\n\n3. Affichage des autorisations\n- Plusieurs riverains ont demandé les dates d'affichage en mairie. DÉCISION : le registre d'affichage sera tenu dans un classeur unique à l'accueil, et plus dans le bureau du service.\n→ Ortega transfère le registre à l'accueil d'ici le vendredi 16 octobre.\n\n4. Questions diverses\n- Formation au nouveau logiciel d'instruction : la date du 3 novembre annoncée la semaine dernière était une erreur, c'est le mardi 10 novembre (toute la journée).\n- Mme Ortega en congé du 26 au 30 octobre ; Vidal reprend ses dossiers urgents.\nFin 15 h 10.",
  "nb_mots": 307
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
 "version_item": 2,
 "type_reunion": "réunion de service urbanisme",
 "participants_reference": [
  "M. Delmas (responsable du service urbanisme, anime)",
  "Mme Ortega (instructrice)",
  "M. Vidal (instructeur)",
  "Mme Kerbrat (assistante, prise de notes)",
  "Absent excusé : M. Fontaine (adjoint au maire chargé de l'urbanisme)"
 ],
 "decisions_reference": [
  "Point hebdomadaire de 15 minutes le lundi à 9 h, à partir du lundi 12 octobre, pour suivre les dossiers proches de leur échéance",
  "Mise à jour de la page « Urbanisme » du site avec la liste des pièces par type de demande",
  "Registre d'affichage des autorisations tenu dans un classeur unique à l'accueil"
 ],
 "actions_reference": [
  {
   "action": "Préparer un tableau de suivi des échéances",
   "responsable": "M. Vidal",
   "echeance": "pour le point du lundi 12 octobre 2026"
  },
  {
   "action": "Rédiger le texte de la page Urbanisme et l'envoyer au service communication",
   "responsable": "Mme Kerbrat",
   "echeance": "avant le vendredi 23 octobre 2026"
  },
  {
   "action": "Transférer le registre d'affichage à l'accueil",
   "responsable": "Mme Ortega",
   "echeance": "d'ici le vendredi 16 octobre 2026"
  },
  {
   "action": "Reprendre les dossiers urgents de Mme Ortega pendant son congé",
   "responsable": "M. Vidal",
   "echeance": "du 26 au 30 octobre 2026"
  }
 ],
 "pieges": [
  "Troisième instructeur à mi-temps : demandé par Mme Ortega, NON décidé (budget 2027)",
  "Atelier mensuel d'aide au dépôt en ligne : proposé, en suspens (avis de M. Fontaine attendu)",
  "Formation au logiciel : mardi 10 novembre et non le 3 novembre (erratum)",
  "M. Fontaine était absent"
 ]
}
```

## CR-507 — Compte rendu (facile, thème `travail-emploi`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CR-507",
 "tache": "Compte rendu",
 "difficulte": "facile",
 "theme": "travail-emploi",
 "entree": {
  "consigne": "Rédige le compte rendu de cette réunion du service des ressources humaines : participants, points abordés, décisions, actions (responsable, échéance).",
  "notes": "Réunion du service Ressources humaines – jeudi 7 janvier 2027 – 10 h – direction des ressources humaines, mairie de Roncières\nPrésents : Mme Perrin (DRH, anime), M. Collet et Mme Faivre (gestionnaires carrière-paie), M. Ndiaye (chargé de formation, notes)\nAbsente : Mme Leclerc (DGS), excusée\n\n1. Campagne des entretiens professionnels 2026\n- 214 agents concernés. DÉCISION : entretiens à réaliser entre le lundi 18 janvier et le vendredi 26 mars 2027.\n→ Mme Faivre envoie la note de cadrage et les supports aux encadrants avant le vendredi 15 janvier.\n- M. Collet propose de passer à un formulaire entièrement en ligne : pas cette année (logiciel non prêt), à revoir en 2028.\n\n2. Plan de formation\n- 63 demandes de formation reçues. DÉCISION : priorité aux formations obligatoires (hygiène et sécurité) et aux préparations aux concours.\n→ M. Ndiaye présente le projet de plan de formation au comité social territorial du jeudi 18 février.\n\n3. Paie\n- Erreur sur 4 bulletins de décembre (prime de fin d'année). DÉCISION : régularisation sur la paie de janvier.\n→ M. Collet corrige les 4 dossiers avant le vendredi 15 janvier.\n\n4. Divers\n- Télétravail : Mme Faivre demande d'élargir à 2 jours par semaine ; la DGS doit donner son avis, rien de décidé.\n- Rectificatif : la réunion avec les encadrants est le mardi 12 janvier, pas le mercredi 13.\nFin 11 h 20.",
  "nb_mots": 212
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
 "type_reunion": "réunion du service des ressources humaines",
 "participants_reference": [
  "Mme Perrin (DRH, anime)",
  "M. Collet (gestionnaire carrière-paie)",
  "Mme Faivre (gestionnaire carrière-paie)",
  "M. Ndiaye (chargé de formation, prise de notes)",
  "Absente excusée : Mme Leclerc (DGS)"
 ],
 "decisions_reference": [
  "Entretiens professionnels entre le lundi 18 janvier et le vendredi 26 mars 2027",
  "Priorité du plan de formation aux formations obligatoires (hygiène et sécurité) et aux préparations aux concours",
  "Régularisation des 4 bulletins de décembre erronés sur la paie de janvier"
 ],
 "actions_reference": [
  {
   "action": "Envoyer la note de cadrage et les supports aux encadrants",
   "responsable": "Mme Faivre",
   "echeance": "avant le vendredi 15 janvier 2027"
  },
  {
   "action": "Présenter le projet de plan de formation au comité social territorial",
   "responsable": "M. Ndiaye",
   "echeance": "jeudi 18 février 2027"
  },
  {
   "action": "Corriger les 4 dossiers de paie",
   "responsable": "M. Collet",
   "echeance": "avant le vendredi 15 janvier 2027"
  }
 ],
 "pieges": [
  "Formulaire d'entretien entièrement en ligne : pas cette année, à revoir en 2028",
  "Télétravail à 2 jours par semaine : demandé, avis de la DGS attendu, rien de décidé",
  "Réunion avec les encadrants le mardi 12 janvier, pas le mercredi 13 (rectificatif)"
 ]
}
```

## CR-509 — Compte rendu (moyen, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CR-509",
 "tache": "Compte rendu",
 "difficulte": "moyen",
 "theme": "famille-education-sante",
 "entree": {
  "consigne": "Rédige le compte rendu de ce conseil d'école : participants, points abordés, décisions, actions (responsable, échéance).",
  "transcription": "Transcription du conseil d'école – école élémentaire Paul-Éluard, Lussan-sur-Gers – jeudi 5 novembre 2026 – 18 h\n\nMme Vasseur (directrice) : Bonsoir à toutes et à tous, merci d'être là. Je déclare ouverte la séance du premier conseil d'école de l'année. Sont présents les sept enseignants de l'école, Mme Leroux, adjointe au maire chargée des affaires scolaires, M. Garcia et Mme Picard pour les parents d'élèves élus, et Mme Okafor, déléguée départementale de l'Éducation nationale. M. Marchand, l'inspecteur de circonscription, est excusé. Mme Benali, enseignante de CE1, accepte d'être secrétaire de séance.\nMme Benali : Oui, je prends les notes.\nMme Vasseur : Premier point, le règlement intérieur. Vous avez reçu le projet. La seule modification porte sur l'utilisation des téléphones portables, qui doivent rester éteints dans le cartable, conformément aux règles en vigueur. Y a-t-il des remarques ?\nM. Garcia : Les parents demandent ce qu'il en est des montres connectées.\nMme Vasseur : Même règle : elles doivent être désactivées pendant le temps scolaire. Je propose d'ajouter les montres connectées au texte. Qui est pour ? Unanimité. Le règlement intérieur est adopté avec cet ajout.\nMme Vasseur : Deuxième point, les effectifs. Nous avons 168 élèves répartis en sept classes. Le CM2 compte 27 élèves, c'est la classe la plus chargée.\nMme Picard : Certains parents s'inquiètent pour le CE2 à double niveau.\nMme Vasseur : Le CE2-CM1 compte 23 élèves, ce qui reste raisonnable. Je n'ai pas d'annonce sur une ouverture de classe pour l'an prochain : c'est l'inspection qui décide, en fonction des prévisions d'effectifs que nous transmettrons en janvier.\nMme Leroux : La mairie transmettra de son côté les chiffres des nouvelles constructions du lotissement des Vignes.\nMme Vasseur : Merci. Troisième point, les travaux et l'entretien. Le chauffage de la classe 4 tombe en panne régulièrement.\nMme Leroux : Je l'ai signalé aux services techniques. La réparation de la chaudière est programmée pendant les vacances de Noël. C'est décidé et le devis est signé.\nM. Garcia : Et la cour ? Les parents parlent depuis longtemps d'un préau plus grand.\nMme Leroux : Le préau ne figure pas au budget 2027. Je ne peux pas m'engager. Nous en reparlerons lors du débat budgétaire, mais je préfère ne rien promettre.\nMme Okafor : Je signale aussi que le marquage au sol du passage piéton devant l'école est effacé.\nMme Leroux : Je le note. Le marquage sera refait avant la fin du mois de novembre, je m'en charge auprès des services techniques.\nMme Vasseur : Quatrième point, les projets pédagogiques. Nous proposons une classe de découverte à la mer pour les deux classes de CM1 et CM2, du lundi 10 au vendredi 14 mai 2027.\nMme Picard : Quel serait le coût pour les familles ?\nMme Vasseur : Nous attendons les devis définitifs. La coopérative scolaire et la mairie pourraient participer, mais rien n'est arrêté. Je propose que le conseil donne un avis favorable au principe du projet, sans engagement financier pour l'instant.\nMme Leroux : La mairie étudiera une participation lors du budget, je ne peux pas donner de montant ce soir.\nMme Vasseur : Qui est favorable au principe ? Unanimité. Avis favorable au principe de la classe de découverte, le financement reste à définir.\nM. Garcia : Les parents élus peuvent organiser une vente de gâteaux pour aider.\nMme Vasseur : Avec plaisir. La première vente aura lieu le vendredi 4 décembre à la sortie de l'école ; M. Garcia et Mme Picard l'organisent.\nMme Vasseur : Cinquième point, la sécurité. Le premier exercice d'évacuation incendie a eu lieu le 22 septembre, en 2 minutes 40. L'exercice du plan particulier de mise en sûreté sera fait avant les vacances de Noël.\nMme Okafor : Je souhaiterais que la date soit communiquée aux familles à l'avance.\nMme Vasseur : Non, l'exercice n'est pas annoncé aux familles à l'avance, mais elles seront informées après. Je ferai un mot dans les cahiers le jour même.\nMme Vasseur : Sixième point, le périscolaire. Mme Leroux ?\nMme Leroux : La cantine sert en moyenne 142 repas par jour. Une enquête de satisfaction sera envoyée aux familles en janvier. Certains parents demandent une option végétarienne quotidienne ; c'est à l'étude avec le prestataire, aucune décision n'est prise.\nM. Garcia : Il y a aussi un problème de bruit au restaurant scolaire.\nMme Leroux : Des panneaux absorbants pourraient être posés, mais il faut d'abord un diagnostic acoustique. Je demanderai un devis pour ce diagnostic d'ici la fin de l'année.\nMme Vasseur : Merci. Questions diverses ? Non. Je rappelle que le prochain conseil d'école se tiendra le jeudi 11 mars 2027 à 18 h. Ah, pardon, je me corrige : c'est le jeudi 18 mars, la salle n'est pas libre le 11. La séance est levée à 19 h 25.",
  "nb_mots": 759
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
 "type_reunion": "conseil d'école",
 "participants_reference": [
  "Mme Vasseur (directrice, préside)",
  "Les sept enseignants de l'école, dont Mme Benali (CE1, secrétaire de séance)",
  "Mme Leroux (adjointe au maire chargée des affaires scolaires)",
  "M. Garcia et Mme Picard (parents d'élèves élus)",
  "Mme Okafor (déléguée départementale de l'Éducation nationale)",
  "Absent excusé : M. Marchand (inspecteur de circonscription)"
 ],
 "decisions_reference": [
  "Règlement intérieur adopté à l'unanimité, avec l'ajout des montres connectées (désactivées pendant le temps scolaire)",
  "Réparation de la chaudière de la classe 4 pendant les vacances de Noël (devis signé)",
  "Avis favorable unanime au principe d'une classe de découverte à la mer pour les CM1 et CM2, du lundi 10 au vendredi 14 mai 2027, financement à définir",
  "Vente de gâteaux le vendredi 4 décembre à la sortie de l'école",
  "Exercice du plan particulier de mise en sûreté avant les vacances de Noël, sans annonce préalable aux familles (information le jour même)"
 ],
 "actions_reference": [
  {
   "action": "Faire refaire le marquage du passage piéton devant l'école",
   "responsable": "Mme Leroux",
   "echeance": "avant la fin novembre 2026"
  },
  {
   "action": "Organiser la vente de gâteaux",
   "responsable": "M. Garcia et Mme Picard",
   "echeance": "vendredi 4 décembre 2026"
  },
  {
   "action": "Transmettre les prévisions d'effectifs",
   "responsable": "Mme Vasseur",
   "echeance": "janvier 2027"
  },
  {
   "action": "Transmettre les chiffres des nouvelles constructions du lotissement des Vignes",
   "responsable": "Mme Leroux (mairie)",
   "echeance": "non fixée"
  },
  {
   "action": "Informer les familles par un mot dans les cahiers après l'exercice de mise en sûreté",
   "responsable": "Mme Vasseur",
   "echeance": "le jour de l'exercice"
  },
  {
   "action": "Envoyer l'enquête de satisfaction sur la cantine",
   "responsable": "Mme Leroux (mairie)",
   "echeance": "janvier 2027"
  },
  {
   "action": "Demander un devis de diagnostic acoustique du restaurant scolaire",
   "responsable": "Mme Leroux",
   "echeance": "d'ici la fin de l'année 2026"
  }
 ],
 "pieges": [
  "Ouverture de classe : aucune annonce, décision de l'inspection",
  "Agrandissement du préau : non budgété, aucune promesse",
  "Participation financière de la mairie à la classe de découverte : non chiffrée, non décidée",
  "Option végétarienne quotidienne : à l'étude, non décidée",
  "Panneaux absorbants : seulement envisagés après diagnostic",
  "Prochain conseil d'école le jeudi 18 mars 2027, pas le 11 (correction en séance)",
  "M. Marchand absent"
 ]
}
```

## CR-511 — Compte rendu (moyen, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CR-511",
 "tache": "Compte rendu",
 "difficulte": "moyen",
 "theme": "social-autonomie",
 "entree": {
  "consigne": "Rédige le compte rendu de ce comité de suivi : participants, points abordés, décisions, actions (responsable, échéance).",
  "transcription": "Transcription – réunion du comité de suivi de l'aide alimentaire – CCAS de Marsigny – mardi 17 novembre 2026 – 14 h\n\nM. Fabre (vice-président du CCAS) : Bonjour à tous. Nous sommes réunis pour le comité de suivi de l'aide alimentaire. Autour de la table : Mme Lopez, directrice du CCAS, Mme Kone, travailleuse sociale, M. Ricard, président de l'épicerie solidaire « Le Panier », Mme Huet, bénévole responsable de la collecte, et M. Ba, agent du CCAS, qui prend les notes. Mme Durand, de la Banque alimentaire départementale, nous a prévenus qu'elle serait en retard.\nMme Lopez : Je commence par les chiffres. Depuis janvier, 214 foyers ont été orientés vers l'épicerie solidaire, contre 176 sur toute l'année dernière. La hausse concerne surtout des retraités et des familles monoparentales.\nM. Ricard : Nous le voyons aussi au magasin. Le mardi après-midi, il y a la queue jusque dans la rue.\nMme Kone : Les orientations sont valables trois mois, renouvelables une fois. Certaines familles auraient besoin de plus.\nM. Fabre : Le règlement prévoit trois mois renouvelables une fois. On ne peut pas le changer aujourd'hui, il faudra une délibération du conseil d'administration. Mais on peut le mettre à l'ordre du jour du prochain conseil, le 8 décembre.\nMme Lopez : Je prépare une note pour le conseil d'administration du 8 décembre proposant une durée de six mois renouvelable une fois. C'est une proposition, ce n'est pas acté.\nM. Fabre : C'est bien cela.\nMme Huet : Pour la collecte nationale de la fin du mois, nous avons besoin de bénévoles dans les deux supermarchés, le vendredi 27 et le samedi 28 novembre.\nM. Fabre : Combien vous en manque-t-il ?\nMme Huet : Une dizaine pour le samedi.\nMme Lopez : Nous pouvons relayer l'appel dans la lettre d'information de la mairie et sur les réseaux sociaux. M. Ba, vous vous en occupez ?\nM. Ba : Oui, je l'envoie au service communication dès demain, mercredi 18 novembre.\n(Arrivée de Mme Durand à 14 h 25.)\nMme Durand : Excusez-moi pour le retard. Je voulais vous dire que la Banque alimentaire va réduire de 10 % les volumes de produits frais livrés à partir de janvier, faute de dons suffisants.\nM. Ricard : C'est un coup dur. Les produits frais sont ce qui part le plus vite.\nMme Kone : Est-ce qu'on pourrait passer un partenariat avec les maraîchers du marché ?\nM. Fabre : C'est une piste intéressante, mais il faut voir les conditions sanitaires et la logistique. Je propose qu'on n'engage rien aujourd'hui. Mme Huet, pourriez-vous simplement rencontrer deux ou trois maraîchers pour savoir s'ils seraient intéressés ?\nMme Huet : Oui, je peux faire ça avant la fin de l'année.\nM. Fabre : Très bien. Deuxième sujet : le véhicule frigorifique. Il a encore été en panne la semaine dernière.\nM. Ricard : Trois pannes depuis la rentrée. Nous avons dû jeter des yaourts.\nMme Lopez : Le remplacement coûterait environ 38 000 euros. Ce n'est pas prévu au budget 2026. Je peux demander une subvention à la fondation d'entreprise du supermarché, mais je n'ai aucune garantie.\nM. Fabre : Je préfère qu'on dépose la demande. Mme Lopez, vous la préparez ?\nMme Lopez : Oui, je dépose la demande avant le 15 décembre, c'est la date limite de la fondation.\nM. Fabre : En attendant, on décide de faire réviser le véhicule par le garage. C'est une dépense d'entretien, elle est dans le budget.\nM. Ricard : D'accord. Je l'amène au garage lundi prochain, le 23.\nM. Fabre : Troisième sujet : les horaires de l'épicerie.\nM. Ricard : Nous proposons d'ouvrir aussi le jeudi matin, de 9 h à 12 h, pour désengorger le mardi.\nMme Kone : Ce serait très utile pour les personnes qui travaillent l'après-midi.\nM. Fabre : Avez-vous assez de bénévoles pour le jeudi ?\nM. Ricard : Oui, quatre bénévoles se sont proposés.\nM. Fabre : Alors on décide l'ouverture du jeudi matin, de 9 h à 12 h, à partir du jeudi 7 janvier 2027.\nMme Lopez : Il faudra prévenir les familles. Mme Kone, pouvez-vous mettre à jour la fiche d'orientation ?\nMme Kone : Oui, avant les fêtes.\nMme Durand : Une dernière information : la Banque alimentaire organise une formation à l'hygiène alimentaire pour les bénévoles. La date n'est pas encore fixée.\nM. Fabre : Nous attendrons la date. Y a-t-il d'autres questions ? Non. Merci à tous. La prochaine réunion du comité aura lieu en février, la date sera fixée par courriel. Fin de la réunion à 15 h 30.",
  "nb_mots": 715
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
 "version_item": 2,
 "type_reunion": "comité de suivi de l'aide alimentaire d'un CCAS",
 "participants_reference": [
  "M. Fabre (vice-président du CCAS, préside)",
  "Mme Lopez (directrice du CCAS)",
  "Mme Kone (travailleuse sociale)",
  "M. Ricard (président de l'épicerie solidaire « Le Panier »)",
  "Mme Huet (bénévole responsable de la collecte)",
  "M. Ba (agent du CCAS, prise de notes)",
  "Mme Durand (Banque alimentaire départementale), arrivée à 14 h 25"
 ],
 "decisions_reference": [
  "Révision du véhicule frigorifique par le garage (dépense d'entretien budgétée)",
  "Ouverture de l'épicerie solidaire le jeudi matin, de 9 h à 12 h, à partir du jeudi 7 janvier 2027",
  "Dépôt d'une demande de subvention auprès de la fondation d'entreprise du supermarché pour le remplacement du véhicule",
  "Prochaine réunion du comité en février 2027, date fixée par courriel"
 ],
 "actions_reference": [
  {
   "action": "Préparer une note pour le conseil d'administration proposant une orientation de 6 mois renouvelable une fois",
   "responsable": "Mme Lopez",
   "echeance": "conseil d'administration du 8 décembre 2026"
  },
  {
   "action": "Transmettre au service communication l'appel à bénévoles pour la collecte, à relayer dans la lettre d'information de la mairie et sur les réseaux sociaux",
   "responsable": "M. Ba",
   "echeance": "mercredi 18 novembre 2026"
  },
  {
   "action": "Rencontrer deux ou trois maraîchers du marché pour sonder leur intérêt",
   "responsable": "Mme Huet",
   "echeance": "avant la fin de l'année 2026"
  },
  {
   "action": "Déposer la demande de subvention auprès de la fondation",
   "responsable": "Mme Lopez",
   "echeance": "avant le 15 décembre 2026"
  },
  {
   "action": "Amener le véhicule frigorifique au garage",
   "responsable": "M. Ricard",
   "echeance": "lundi 23 novembre 2026"
  },
  {
   "action": "Mettre à jour la fiche d'orientation (nouveaux horaires)",
   "responsable": "Mme Kone",
   "echeance": "avant les fêtes de fin d'année 2026"
  }
 ],
 "pieges": [
  "Durée d'orientation de 6 mois : simple proposition au conseil d'administration, non actée",
  "Partenariat avec les maraîchers : piste, rien d'engagé",
  "Subvention de la fondation : aucune garantie",
  "Remplacement du véhicule (38 000 €) : non budgété, non décidé",
  "Formation à l'hygiène : date non fixée",
  "Baisse de 10 % des produits frais : annonce de la Banque alimentaire, pas une décision du comité",
  "Mme Durand arrivée en retard (14 h 25)"
 ]
}
```

## CR-515 — Compte rendu (difficile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CR-515",
 "tache": "Compte rendu",
 "difficulte": "difficile",
 "theme": "collectivites",
 "entree": {
  "consigne": "Rédige le compte rendu de cette séance du conseil municipal : participants, points abordés, décisions, actions (responsable, échéance).",
  "transcription": "Transcription de la séance du conseil municipal de Saint-Florent-sur-Lèze – jeudi 10 décembre 2026 – 19 h – salle du conseil\n\nM. Mercier (maire) : Bonsoir à toutes et à tous. Il est 19 heures, je vous propose d'ouvrir la séance. Je salue les conseillers municipaux, le public, assez nombreux ce soir, ce qui fait plaisir, ainsi que le correspondant de La Dépêche du Val. Je vais d'abord faire l'appel. Le conseil compte dix-neuf membres. Sont présents : Mme Garnier, première adjointe, M. Leclerc, Mme Hamon, M. Ruiz, Mme Delattre, M. Benoît, Mme Ferrand, M. Picard, Mme Nguyen, M. Lambert, Mme Rossi, M. Caron, Mme Lemoine, M. Diallo, Mme Vincent, M. Joly et moi-même, soit dix-sept présents. M. Barbier a donné pouvoir à Mme Garnier et Mme Colin a donné pouvoir à M. Ruiz. Le quorum est atteint. Mme Dubois, directrice générale des services, assiste à la séance sans prendre part aux votes.\nM. Mercier : Il nous faut un secrétaire de séance. Mme Nguyen, vous êtes candidate ? Pas d'opposition ? Mme Nguyen est désignée secrétaire de séance.\nMme Nguyen : Merci, je prends les notes avec l'aide de Mme Dubois.\nM. Mercier : Premier point, l'approbation du procès-verbal de la séance du 22 octobre. Vous l'avez reçu avec la convocation. Y a-t-il des remarques ?\nM. Joly : Oui, monsieur le maire. Page 4, il est écrit que j'ai voté contre la vente du terrain des Garrigues. Ce n'est pas exact : je me suis abstenu.\nMme Dubois : Je vérifie… M. Joly a raison, la feuille de vote indique une abstention. Nous corrigerons.\nM. Mercier : Très bien, avec cette correction, je mets le procès-verbal aux voix. Qui est pour ? Qui est contre ? Qui s'abstient ? Le procès-verbal est approuvé à l'unanimité, avec la correction demandée par M. Joly.\nM. Mercier : Avant de passer à l'ordre du jour, je vous rends compte, comme la loi m'y oblige, des décisions que j'ai prises par délégation depuis la dernière séance. J'ai signé trois décisions : le renouvellement du contrat d'entretien des chaudières des écoles, pour 4 800 euros par an, la location d'un logement communal au-dessus de l'ancienne poste, et l'acceptation d'un don de livres anciens pour la médiathèque. Ces décisions n'appellent pas de vote, je vous en donne simplement connaissance.\nM. Caron : Pour le logement, à combien est fixé le loyer ?\nM. Mercier : À 520 euros par mois, hors charges, conformément au barème voté l'an dernier.\nM. Mercier : Point 2 de l'ordre du jour : le débat d'orientation budgétaire pour 2027. Je rappelle que ce débat n'est pas suivi d'un vote sur le budget lui-même. Le conseil prend acte de la tenue du débat. Le budget primitif sera voté lors de la séance de mars. Mme Garnier, chargée des finances, va vous présenter le rapport.\nMme Garnier : Merci, monsieur le maire. Je vais aller à l'essentiel, le rapport complet vous a été envoyé. Le contexte d'abord : nos dotations de l'État sont stables en valeur, ce qui veut dire qu'elles baissent en euros constants avec l'inflation. Nos dépenses de personnel augmentent mécaniquement d'environ 3 % sous l'effet des avancements et des revalorisations. Les dépenses d'énergie ont baissé de 12 % grâce aux travaux d'isolation de l'école et au changement des lanternes de l'éclairage public, mais elles restent supérieures de 30 % à leur niveau de 2021.\nMme Garnier : Côté recettes, nous proposons de ne pas augmenter les taux de la taxe foncière en 2027. Les bases augmenteront selon la revalorisation forfaitaire fixée par la loi de finances, nous ne la connaissons pas encore précisément. Notre épargne brute devrait se situer autour de 410 000 euros, ce qui nous permet de maintenir un programme d'investissement raisonnable.\nMme Garnier : Pour les investissements, trois projets sont envisagés pour 2027 : la fin de la rénovation de l'école élémentaire, environ 380 000 euros, la réfection de la rue des Écoles, environ 150 000 euros, et l'aménagement du parc de la Lèze, pour lequel nous n'avons encore qu'une estimation très large, entre 200 000 et 300 000 euros. J'insiste : ce sont des orientations. Les montants définitifs seront arrêtés au budget.\nM. Mercier : Merci. Le débat est ouvert.\nM. Joly : Je vous remercie pour la présentation. Notre groupe partage l'objectif de ne pas augmenter les impôts. En revanche, nous nous interrogeons sur l'endettement. Vous prévoyez un emprunt de combien ?\nMme Garnier : Un emprunt d'environ 250 000 euros est envisagé, ce qui porterait notre capacité de désendettement à un peu moins de six ans. Le seuil d'alerte habituellement retenu est de douze ans, nous en sommes loin.\nM. Joly : Le parc de la Lèze ne nous paraît pas prioritaire. Nous préférerions que l'argent aille à la voirie des hameaux, qui est dans un état lamentable. Le chemin de Bellevue, par exemple.\nM. Leclerc : Je me permets de répondre, en tant qu'adjoint aux travaux. Le chemin de Bellevue est inscrit dans le plan pluriannuel, pour 2028. On ne peut pas tout faire la même année.\nM. Joly : 2028, c'est loin pour les riverains.\nMme Rossi : Je voudrais parler du parc, justement. Les familles du centre n'ont aucun espace vert digne de ce nom. Le parc de la Lèze, c'est aussi un projet pour la santé et pour les enfants.\nM. Caron : Je rejoins M. Joly sur un point : avant de lancer le parc, il faudrait une vraie concertation avec les habitants. On ne connaît même pas le programme.\nM. Mercier : Je l'entends. Je vous propose que le programme du parc fasse l'objet d'une réunion publique au premier trimestre. Ce n'est pas une décision du conseil ce soir, c'est un engagement de ma part, et nous fixerons la date en commission.\nMme Vincent : Et pour la cantine ? Le rapport ne dit rien des tarifs.\nMme Garnier : Les tarifs font l'objet du point suivant, madame Vincent.\nM. Diallo : Une question sur le personnel. Est-ce que vous prévoyez des recrutements ?\nMme Garnier : Un seul poste supplémentaire est envisagé, un agent pour l'entretien des espaces verts, compte tenu de l'ouverture du parc si elle a lieu. Là encore, ce sera arrêté au budget.\nM. Joly : Donc si le parc ne se fait pas, pas de recrutement ?\nMme Garnier : C'est la logique, oui.\nM. Mercier : D'autres interventions ? Non. Je vous propose donc de prendre acte de la tenue du débat d'orientation budgétaire. Il n'y a pas de vote sur le fond. Le conseil prend acte. Merci.\nM. Mercier : Point 3 : les tarifs municipaux pour 2027. Mme Hamon, vous rapportez ?\nMme Hamon : Oui. Nous proposons d'abord les tarifs de la restauration scolaire. Le prix du repas pour les familles passerait de 3,40 euros à 3,47 euros, soit une hausse de 2 %, alors que le coût réel d'un repas pour la commune est de 8,90 euros. Le tarif social, pour les familles dont le quotient familial est inférieur à 700, resterait à 1 euro, dans le cadre du dispositif de la cantine à 1 euro.\nMme Vincent : C'est justement ce que je voulais demander. Merci pour le maintien du tarif à 1 euro, c'est important.\nMme Hamon : Pour la salle des fêtes, la location le week-end pour les habitants passerait de 280 à 300 euros. Pour les associations de la commune, elle reste gratuite une fois par an, puis 100 euros. Pour les personnes extérieures à la commune, 550 euros. La caution reste fixée à 800 euros.\nM. Picard : Pourquoi augmenter la salle des fêtes plus que la cantine ?\nMme Hamon : Le tarif n'avait pas bougé depuis quatre ans et le coût du ménage a augmenté. Mais c'est un choix politique, j'en conviens.\nM. Picard : Je proposerais 290 euros plutôt que 300.\nM. Mercier : Je soumets d'abord l'amendement de M. Picard, à 290 euros. Qui est pour ? Quatre voix : M. Picard, M. Joly, M. Caron et Mme Vincent. Qui est contre ? Quatorze. Abstention : une, Mme Lemoine. L'amendement est rejeté.\nM. Mercier : Je mets maintenant aux voix l'ensemble des tarifs tels que proposés, avec la cantine à 3,47 euros, le tarif social à 1 euro, la salle des fêtes à 300 euros pour les habitants, 550 euros pour les extérieurs et 100 euros pour les associations au-delà de la première utilisation. Qui est pour ? Quinze. Qui est contre ? Trois : M. Picard, M. Joly, M. Caron. Abstention : Mme Vincent. Les tarifs 2027 sont adoptés.\nMme Hamon : Les nouveaux tarifs s'appliqueront à partir du 1er janvier 2027. Le service scolaire informera les familles par le portail et un courrier.\nM. Mercier : Merci. Mme Dubois, vous veillerez à ce que l'information parte avant les vacances ?\nMme Dubois : Oui, le courrier aux familles partira avant le vendredi 18 décembre.\nM. Mercier : Point 4 : les subventions aux associations pour 2027. M. Benoît.\nM. Benoît : Merci. La commission vie associative s'est réunie le 25 novembre et a examiné 22 demandes. L'enveloppe totale proposée est de 48 500 euros, contre 46 000 euros en 2026. Le tableau détaillé vous a été remis. Je signale les principales évolutions : le club de football passe de 6 000 à 6 500 euros, en raison de la création d'une équipe féminine ; l'association des parents d'élèves reçoit 1 200 euros pour la classe de découverte ; le comité des fêtes reçoit 5 000 euros ; et nous proposons une subvention nouvelle de 800 euros pour l'association « Lèze Nature », qui entretient les berges.\nMme Ferrand : Je dois préciser que je suis présidente du comité des fêtes. Je ne participerai donc ni au débat ni au vote sur cette subvention.\nM. Mercier : Merci, madame Ferrand, c'est la bonne démarche. Je propose de voter la subvention du comité des fêtes à part, puis le reste du tableau.\nM. Lambert : Je voudrais savoir pourquoi le club de tennis n'a rien cette année.\nM. Benoît : Le club de tennis n'a pas déposé de dossier dans les délais. La commission a proposé qu'il puisse déposer une demande au printemps, qui serait examinée lors d'une prochaine séance. Rien n'est attribué ce soir.\nM. Lambert : Ils vont être déçus.\nM. Benoît : Je les ai prévenus et je les recevrai.\nM. Mercier : Nous passons au vote. Subvention de 5 000 euros au comité des fêtes, Mme Ferrand ne prenant pas part au vote. Qui est pour ? Dix-huit. Contre ? Aucun. Abstention ? Aucune. Adopté, avec dix-huit votants.\nM. Mercier : Ensuite, le reste du tableau, soit 43 500 euros répartis entre les vingt et une autres associations. Qui est pour ? Unanimité. Adopté.\nM. Benoît : Les associations recevront une notification. Je m'en occupe avec le service vie associative avant la fin du mois de janvier.\nM. Mercier : Point 5 : la convention avec la communauté de communes pour l'instruction des autorisations d'urbanisme. M. Ruiz.\nM. Ruiz : Depuis 2017, c'est le service commun de la communauté de communes qui instruit nos permis de construire et nos déclarations préalables. La convention arrive à échéance le 31 décembre. La nouvelle convention prévoit un coût par acte : 180 euros par permis de construire, 90 euros par déclaration préalable et 60 euros par certificat d'urbanisme opérationnel. Sur la base de l'activité de 2026, cela représente environ 14 000 euros par an, contre 12 500 euros avec l'ancien mode de calcul.\nM. Caron : Pourquoi une telle hausse ?\nM. Ruiz : Le service commun a recruté un instructeur supplémentaire, parce que les délais étaient trop longs. Les délais d'instruction moyens sont passés de 2 mois et demi à moins de 2 mois. Je pense que c'est un progrès.\nM. Joly : Avons-nous envisagé de reprendre l'instruction en interne ?\nM. Ruiz : Nous l'avons étudié. Il faudrait recruter un agent formé à temps plein pour environ 80 dossiers par an, ce serait plus cher et nous perdrions l'expertise juridique du service commun.\nMme Lemoine : La convention est signée pour combien de temps ?\nM. Ruiz : Trois ans, du 1er janvier 2027 au 31 décembre 2029, avec une clause de révision annuelle des tarifs.\nM. Mercier : Je soumets la convention au vote et je vous demande de m'autoriser à la signer. Qui est pour ? Dix-huit. Contre ? Aucun. Abstention ? Une, M. Caron. La convention est adoptée.\nM. Mercier : Je la signerai dès réception de la version définitive. Mme Dubois, vous la renverrez à la communauté de communes avant le 31 décembre ?\nMme Dubois : Oui, c'est prévu.\nM. Mercier : Point 6 : l'extinction nocturne de l'éclairage public. M. Leclerc.\nM. Leclerc : Comme vous le savez, nous avons remplacé l'an dernier 310 lanternes par des LED. Nous proposons maintenant d'éteindre l'éclairage public de minuit à 5 heures du matin, sauf sur la route départementale et devant la gendarmerie. L'économie attendue est d'environ 9 000 euros par an et les études montrent un bénéfice pour la biodiversité. L'extinction s'appliquerait à partir du lundi 1er février 2027. La délibération fixe le principe ; ensuite, je rappelle que c'est un arrêté du maire qui fixera précisément les horaires et les voies concernées.\nMme Rossi : Il y a des inquiétudes chez les habitants sur la sécurité, notamment des personnes âgées qui rentrent tard en bus.\nM. Leclerc : Le dernier bus arrive à 23 h 10. L'extinction commence à minuit.\nM. Picard : Et les cambriolages ?\nM. Leclerc : J'ai interrogé le commandant de la brigade de gendarmerie. Dans les communes voisines qui ont éteint, il n'a pas constaté d'augmentation des cambriolages. Je ne peux pas vous donner de chiffres officiels ce soir, mais c'est ce qu'il m'a dit.\nM. Joly : Nous aurions souhaité une période d'essai, par exemple six mois, avec un bilan.\nM. Mercier : Je retiens l'idée d'un bilan. Je vous propose qu'un bilan soit présenté au conseil après un an d'extinction. Mais il n'y aura pas de période d'essai au sens d'une décision provisoire : la délibération est définitive, elle pourra bien sûr être modifiée plus tard.\nMme Delattre : Et pour les fêtes de fin d'année, est-ce qu'on éclaire toute la nuit ?\nM. Leclerc : Les illuminations de Noël sont sur un circuit séparé, elles ne sont pas concernées. Et de toute façon, l'extinction ne commencera qu'en février.\nM. Mercier : Je soumets au vote le principe de l'extinction de l'éclairage public de minuit à 5 heures, à partir du 1er février 2027, sauf route départementale et abords de la gendarmerie, avec un bilan présenté au conseil après un an. Qui est pour ? Quinze. Qui est contre ? Quatre : M. Picard, M. Joly, M. Caron, Mme Rossi. Abstention ? Aucune. La délibération est adoptée.\nM. Leclerc : Une réunion d'information pour les habitants aura lieu en janvier. Je propose le mercredi 13 janvier à 18 h 30, à la salle des fêtes.\nM. Mercier : Pardon, monsieur Leclerc, la salle des fêtes est réservée ce jour-là pour les vœux des associations. Ce sera le jeudi 14 janvier à 18 h 30.\nM. Leclerc : Très bien, le jeudi 14 janvier. Je préparerai l'information avec le service communication pour le bulletin de janvier.\nM. Mercier : Merci. Avant le point 7, je vous présente, comme annoncé dans l'envoi complémentaire joint à la convocation, le rapport annuel sur le prix et la qualité du service public de l'eau potable, présenté par le syndicat intercommunal des eaux de la Lèze. Ce rapport n'appelle pas de vote : le conseil en prend acte. M. Benoît, vous siégez au comité syndical, voulez-vous le présenter ?\nM. Benoît : Volontiers. Le syndicat dessert onze communes et un peu plus de 9 400 abonnés. Pour notre commune, cela représente 1 270 abonnés. Le prix de l'eau, pour une facture de référence de 120 mètres cubes, s'établit à 2,31 euros le mètre cube toutes taxes comprises au 1er janvier 2026, contre 2,18 euros l'année précédente. La hausse s'explique principalement par la redevance de l'agence de l'eau et par le programme de renouvellement des canalisations.\nM. Benoît : Le rendement du réseau, c'est-à-dire la part de l'eau produite qui arrive effectivement chez les abonnés, est de 78 %. L'objectif réglementaire pour notre syndicat est atteint, mais nous perdons encore plus d'un mètre cube sur cinq dans les fuites. Le syndicat a renouvelé 4,2 kilomètres de canalisations en 2025. La qualité de l'eau distribuée a été conforme dans 100 % des analyses bactériologiques et dans 98 % des analyses physico-chimiques ; les deux non-conformités concernaient un dépassement ponctuel de la limite pour un métabolite de pesticide, sans restriction de consommation, sur le captage de la Borde.\nMme Lemoine : Est-ce que les habitants ont été informés de ces dépassements ?\nM. Benoît : L'agence régionale de santé a été informée, et l'information figure sur la facture annuelle. Il n'y a pas eu de restriction, car les valeurs restaient sous le seuil sanitaire.\nM. Caron : Le prix augmente chaque année. Est-ce qu'il y a une tarification sociale de l'eau ?\nM. Benoît : Le syndicat étudie la question pour 2028. Rien n'est décidé, et ce n'est pas une compétence du conseil municipal : c'est le comité syndical qui décidera.\nM. Joly : Et le captage de la Borde, il va être fermé ?\nM. Benoît : Une étude est en cours pour une interconnexion avec le syndicat voisin. Je n'ai pas d'information sur une fermeture. Je préfère ne pas faire de pronostic.\nMme Delattre : Où peut-on consulter le rapport complet ?\nM. Benoît : Le rapport sera tenu à la disposition du public en mairie, et publié sur le site de la commune dans les quinze jours.\nM. Mercier : Je vous remercie. Le conseil prend acte de la présentation du rapport annuel sur le prix et la qualité du service de l'eau potable. Mme Dubois, vous ferez publier le rapport sur le site avant la fin du mois ?\nMme Dubois : Oui, avant le jeudi 24 décembre.\nM. Mercier : Toujours avant le point 7, il nous faut délibérer sur une modification du tableau des effectifs. Mme Garnier.\nMme Garnier : Il s'agit de transformer un poste d'adjoint administratif à temps non complet, 28 heures par semaine, en poste à temps complet, 35 heures, au service de l'accueil de la mairie, à compter du 1er janvier 2027. L'agent concerné effectue déjà de nombreuses heures complémentaires du fait de la hausse des demandes de titres d'identité. Le coût supplémentaire est d'environ 7 500 euros par an, charges comprises, mais il est en partie compensé par la baisse des heures complémentaires. Le comité social territorial a été consulté le 26 novembre et a rendu un avis favorable.\nM. Diallo : Est-ce que l'accueil sera ouvert plus longtemps ?\nMme Garnier : L'objectif est de rouvrir l'accueil le jeudi jusqu'à 19 heures. Mais les horaires d'ouverture relèvent d'un arrêté du maire ; nous ne les votons pas ce soir.\nM. Mercier : Je le confirme, je prendrai l'arrêté sur les horaires plus tard, après en avoir parlé avec les agents.\nM. Picard : Nous sommes favorables. L'accueil est souvent saturé le lundi matin.\nMme Vincent : Pourquoi pas un deuxième poste, alors ?\nMme Garnier : Nous ne l'envisageons pas. Ce n'est pas prévu dans le débat d'orientation budgétaire que nous venons d'avoir.\nM. Mercier : Je mets aux voix la transformation du poste d'adjoint administratif de 28 heures en poste à temps complet, à compter du 1er janvier 2027. Qui est pour ? Unanimité. Adopté. Mme Dubois, vous transmettrez la délibération au centre de gestion ?\nMme Dubois : Oui, et je prépare l'arrêté individuel de l'agent avant la fin du mois.\nM. Mercier : Merci. Point 7 : la dénomination de la nouvelle voie du lotissement du Moulin. Mme Garnier.\nMme Garnier : Le lotissement du Moulin, quatorze maisons, sera livré au printemps. La voie de desserte doit recevoir un nom avant que La Poste et les services de secours puissent l'enregistrer. La commission a proposé « rue Simone-Veil ». Lors de la commission, une autre proposition avait été faite par M. Lambert, « allée des Tilleuls », en raison des arbres plantés le long de la voie.\nM. Lambert : Je maintiens ma proposition. Les habitants préfèrent souvent des noms simples, liés au lieu.\nMme Rossi : Nous n'avons qu'une seule rue portant le nom d'une femme dans la commune. Je soutiens « rue Simone-Veil ».\nM. Mercier : Je mets d'abord aux voix « rue Simone-Veil ». Qui est pour ? Seize. Contre ? Deux. Abstention ? Une. La voie s'appellera rue Simone-Veil. La proposition « allée des Tilleuls » n'est donc pas retenue.\nMme Garnier : Je transmettrai la délibération au service du cadastre et à La Poste avant la fin du mois de janvier, et je ferai commander les plaques.\nM. Mercier : Point 8 : une motion relative à la fermeture envisagée d'une classe à l'école élémentaire Jean-Jaurès. Je vous lis le texte qui vous a été remis sur table. « Le conseil municipal de Saint-Florent-sur-Lèze, informé du projet de fermeture d'une classe à l'école élémentaire Jean-Jaurès à la rentrée 2027, exprime son opposition à cette mesure, rappelle la croissance attendue des effectifs liée au lotissement du Moulin et demande à la direction académique de maintenir la classe. »\nMme Hamon : Je précise que les effectifs prévus pour la rentrée sont de 131 élèves pour six classes. Avec cinq classes, la moyenne dépasserait 26 élèves par classe.\nM. Joly : Nous voterons cette motion. Sur ce sujet, il n'y a ni majorité ni opposition.\nM. Mercier : Je soumets la motion. Qui est pour ? Unanimité. La motion est adoptée et sera transmise à la directrice académique et au député. Mme Dubois, vous l'envoyez dès demain ?\nMme Dubois : Oui, dès demain, vendredi 11 décembre.\nM. Mercier : Nous arrivons aux questions diverses. M. Diallo avait demandé à intervenir.\nM. Diallo : Merci. Je voudrais savoir où en est le projet de maison de santé. Plusieurs habitants m'en parlent, nous n'avons plus de médecin depuis le départ du docteur Sanchez.\nM. Mercier : C'est une préoccupation majeure. Nous avons rencontré deux médecins et une infirmière intéressés, mais rien n'est signé. Un bureau d'études pourrait réaliser une étude de faisabilité, mais nous ne l'avons pas encore commandée. Je ne veux pas créer de faux espoirs : il n'y a aucune décision ce soir. J'espère pouvoir revenir vers vous au printemps.\nM. Diallo : Est-ce que la communauté de communes peut aider ?\nM. Mercier : J'ai sollicité le président de la communauté de communes, une réunion est prévue en janvier, je n'ai pas encore la date.\nMme Lemoine : J'ai une question sur le terrain de football. Le club demande un terrain synthétique.\nM. Leclerc : Un terrain synthétique coûte autour de 800 000 euros. Ce n'est pas envisageable dans le programme d'investissement présenté ce soir. Nous ne l'avons pas inscrit.\nMme Lemoine : Donc c'est non ?\nM. Mercier : Ce n'est pas au programme. Je ne dis pas jamais, mais pas dans les années qui viennent.\nM. Caron : Une dernière question : le marché de Noël. Où en est-on de la sécurité ?\nMme Ferrand : Les barrières seront installées le vendredi 18 décembre, le marché a lieu le samedi 19 et le dimanche 20. La gendarmerie a validé le dispositif.\nM. Mercier : Merci. Je rappelle que la prochaine séance du conseil municipal est prévue le jeudi 4 février 2027. Euh, non, pardon, je relis mon agenda : le jeudi 11 février 2027, à 19 heures, parce que le 4 tombe pendant le congrès des maires du département. Je vous souhaite de très bonnes fêtes. La séance est levée à 21 h 35.\n\n(Après la levée de séance, échanges avec le public.)\nUn habitant : Monsieur le maire, pour l'extinction, est-ce que le chemin des Pradets est concerné ?\nM. Mercier : Oui, monsieur, toutes les voies sauf la route départementale et les abords de la gendarmerie. Venez à la réunion du jeudi 14 janvier, M. Leclerc vous expliquera tout.\nUne habitante : Et pour la maison de santé, on peut écrire à quelqu'un ?\nM. Mercier : Vous pouvez écrire à la mairie, toutes les contributions sont les bienvenues.\nUn autre habitant : Monsieur le maire, j'habite au lotissement des Cèdres. On parle du parc de la Lèze depuis des années. Est-ce qu'il y aura des jeux pour les enfants ?\nM. Mercier : Je ne peux pas vous répondre aujourd'hui, monsieur. Le programme n'est pas arrêté. C'est justement l'objet de la réunion publique que j'organiserai au premier trimestre. Vous pourrez y faire vos propositions.\nL'habitant : Et les travaux commenceraient quand ?\nM. Mercier : Je ne veux pas donner de date. Il faut d'abord le programme, puis les études, puis le budget. Vous savez, j'ai été adjoint aux travaux pendant six ans avant d'être maire, et j'ai appris qu'il vaut mieux ne pas annoncer une date qu'on ne tiendra pas.\nUne habitante : Pour la cantine, est-ce que les menus vont changer avec la hausse du tarif ?\nMme Hamon : Non, madame. La hausse correspond à l'augmentation du prix des denrées. Les menus restent préparés par la cuisine centrale, avec les mêmes exigences : au moins la moitié de produits de qualité et durables. La commission des menus se réunit chaque trimestre, les parents y sont représentés.\nL'habitante : On peut y participer ?\nMme Hamon : Les représentants sont désignés par les associations de parents d'élèves. Vous pouvez vous rapprocher d'elles.\nUn habitant : Une dernière chose : l'extinction de l'éclairage, est-ce que ça concerne aussi le parking de la gare ?\nM. Leclerc : Le parking de la gare appartient à la région, pas à la commune. Nous allons interroger la région, mais je ne peux pas vous répondre ce soir. Je vous propose de laisser vos coordonnées à Mme Dubois et je vous répondrai par écrit.\nM. Mercier : Merci à tous, bonne soirée et bonnes fêtes.",
  "nb_mots": 4119
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
  "M. Mercier (maire, préside)",
  "17 conseillers présents sur 19 dont Mme Garnier (1re adjointe, finances), M. Leclerc (adjoint aux travaux), Mme Hamon, M. Ruiz, M. Benoît, Mme Ferrand, M. Picard, M. Joly, M. Caron, Mme Rossi, Mme Lemoine, M. Diallo, Mme Vincent, Mme Delattre, M. Lambert",
  "Mme Nguyen (secrétaire de séance)",
  "Pouvoirs : M. Barbier à Mme Garnier, Mme Colin à M. Ruiz",
  "Mme Dubois (DGS), sans voix délibérative"
 ],
 "decisions_reference": [
  "Procès-verbal du 22 octobre approuvé à l'unanimité, avec la correction demandée par M. Joly (abstention et non vote contre)",
  "Le conseil prend acte de la tenue du débat d'orientation budgétaire 2027 (pas de vote sur le budget)",
  "Amendement de M. Picard (salle des fêtes à 290 €) rejeté ; tarifs 2027 adoptés (15 pour, 3 contre, 1 abstention) : repas à 3,47 €, tarif social à 1 €, salle des fêtes 300 € habitants, 550 € extérieurs, 100 € associations au-delà de la première utilisation",
  "Subvention de 5 000 € au comité des fêtes adoptée (Mme Ferrand ne prenant pas part au vote) et 43 500 € aux autres associations à l'unanimité (enveloppe totale 48 500 €)",
  "Convention 2027-2029 avec la communauté de communes pour l'instruction des autorisations d'urbanisme adoptée (18 pour, 1 abstention)",
  "Extinction de l'éclairage public de minuit à 5 h à partir du 1er février 2027, sauf route départementale et abords de la gendarmerie, avec bilan après un an (15 pour, 4 contre)",
  "Prise d'acte du rapport annuel sur le prix et la qualité du service de l'eau potable",
  "Transformation d'un poste d'adjoint administratif de 28 h en temps complet au 1er janvier 2027 (unanimité)",
  "Dénomination « rue Simone-Veil » pour la voie du lotissement du Moulin (16 pour, 2 contre, 1 abstention)",
  "Motion contre la fermeture d'une classe à l'école Jean-Jaurès adoptée à l'unanimité"
 ],
 "actions_reference": [
  {
   "action": "Envoyer le courrier d'information sur les nouveaux tarifs aux familles",
   "responsable": "Mme Dubois (service scolaire)",
   "echeance": "avant le vendredi 18 décembre 2026"
  },
  {
   "action": "Notifier les subventions aux associations",
   "responsable": "M. Benoît avec le service vie associative",
   "echeance": "avant la fin janvier 2027"
  },
  {
   "action": "Renvoyer la convention signée à la communauté de communes",
   "responsable": "Mme Dubois",
   "echeance": "avant le 31 décembre 2026"
  },
  {
   "action": "Organiser la réunion d'information sur l'extinction de l'éclairage",
   "responsable": "M. Leclerc",
   "echeance": "jeudi 14 janvier 2027 à 18 h 30"
  },
  {
   "action": "Préparer l'information sur l'extinction pour le bulletin de janvier",
   "responsable": "M. Leclerc avec le service communication",
   "echeance": "bulletin de janvier 2027"
  },
  {
   "action": "Publier le rapport sur l'eau sur le site de la commune",
   "responsable": "Mme Dubois",
   "echeance": "avant le jeudi 24 décembre 2026"
  },
  {
   "action": "Transmettre la délibération au centre de gestion et préparer l'arrêté individuel de l'agent",
   "responsable": "Mme Dubois",
   "echeance": "avant la fin décembre 2026"
  },
  {
   "action": "Transmettre la délibération de dénomination au cadastre et à La Poste et commander les plaques",
   "responsable": "Mme Garnier",
   "echeance": "avant la fin janvier 2027"
  },
  {
   "action": "Envoyer la motion à la directrice académique et au député",
   "responsable": "Mme Dubois",
   "echeance": "vendredi 11 décembre 2026"
  },
  {
   "action": "Organiser une réunion publique sur le programme du parc de la Lèze",
   "responsable": "M. Mercier (date fixée en commission)",
   "echeance": "premier trimestre 2027"
  }
 ],
 "pieges": [
  "Le DOB n'est pas un vote du budget : les montants d'investissement (école, rue des Écoles, parc) sont des orientations",
  "Emprunt d'environ 250 000 € et recrutement d'un agent espaces verts : envisagés, non décidés",
  "Chemin de Bellevue : prévu en 2028 dans le plan pluriannuel, pas en 2027",
  "Subvention au club de tennis : rien attribué (dossier non déposé)",
  "Période d'essai de l'extinction : non retenue (délibération définitive, bilan après un an)",
  "« Allée des Tilleuls » non retenue",
  "Maison de santé : aucune décision, étude non commandée",
  "Terrain synthétique : non inscrit au programme",
  "Tarification sociale de l'eau : compétence du syndicat, rien de décidé",
  "Horaires de l'accueil (jeudi jusqu'à 19 h) : relèvent d'un arrêté du maire, non votés",
  "Réunion d'information le jeudi 14 janvier et non le mercredi 13 ; prochaine séance le jeudi 11 février 2027 et non le 4",
  "Mme Ferrand n'a pas pris part au vote sur le comité des fêtes"
 ]
}
```

## CR-517 — Compte rendu (difficile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CR-517",
 "tache": "Compte rendu",
 "difficulte": "difficile",
 "theme": "collectivites",
 "entree": {
  "consigne": "Rédige le compte rendu de cette réunion publique de concertation : participants, points abordés, décisions, actions (responsable, échéance).",
  "transcription": "Transcription de la réunion publique de concertation sur la révision du plan local d'urbanisme – commune de Villars-sur-Drôme – mercredi 18 novembre 2026 – 19 h – salle polyvalente\n\nM. Lacroix (maire) : Bonsoir à toutes et à tous, et merci d'être venus si nombreux. Nous avons compté un peu plus de quatre-vingts personnes, ce qui montre l'intérêt que vous portez à l'avenir de notre commune. Je suis accompagné de Mme Benoist, adjointe chargée de l'urbanisme, de Mme Garcia, directrice générale des services, et de M. Viala, urbaniste du bureau d'études Territoires et Paysages, qui accompagne la commune dans la révision de son plan local d'urbanisme. Mme Paulin, du service urbanisme, prend des notes et un compte rendu sera établi. Je vais d'abord rappeler le cadre de la soirée, puis M. Viala présentera le diagnostic et les premières orientations, et nous laisserons ensuite une large place à vos questions.\nM. Lacroix : Je veux être clair dès le départ : ce soir, aucune décision n'est prise sur le zonage. Nous sommes au stade de la concertation. Le projet de plan local d'urbanisme sera arrêté plus tard par le conseil municipal, puis soumis à l'avis des personnes publiques associées et à une enquête publique. C'est lors de l'enquête publique que chacun pourra faire valoir ses observations sur le projet arrêté, devant un commissaire enquêteur.\nMme Benoist : Je rappelle aussi pourquoi nous révisons le PLU. Notre document actuel date de 2012. Depuis, la loi a beaucoup évolué, notamment avec l'objectif de réduire l'artificialisation des sols. Le schéma de cohérence territoriale du Val de Drôme a été approuvé en 2024 et notre PLU doit être compatible avec lui. Enfin, le conseil municipal souhaite mieux protéger les terres agricoles et le patrimoine des hameaux.\nM. Viala : Merci. Je vais commencer par le diagnostic. Villars-sur-Drôme compte 2 940 habitants au dernier recensement, contre 2 610 il y a dix ans. La croissance est donc d'environ 1,2 % par an, ce qui est assez soutenu pour une commune rurale. Elle est surtout portée par l'arrivée de jeunes ménages qui travaillent dans l'agglomération de Valence. La taille moyenne des ménages diminue, elle est passée de 2,5 à 2,3 personnes. Cela veut dire qu'à population égale, il faut plus de logements.\nM. Viala : Le parc compte 1 380 logements, dont 87 % de maisons individuelles et 6 % de logements vacants. Les logements locatifs sociaux représentent 4 % du parc. Je précise que la commune n'est pas soumise à l'obligation légale de 20 ou 25 % de logements sociaux, qui ne concerne que les communes de plus de 3 500 habitants dans certaines agglomérations. Le SCoT fixe toutefois un objectif de diversification.\nM. Viala : Sur la consommation d'espace, entre 2011 et 2021, la commune a consommé 18 hectares d'espaces naturels, agricoles et forestiers, principalement pour de l'habitat. La loi impose de réduire de moitié ce rythme sur la période 2021-2031. Concrètement, cela signifie que la commune ne pourra pas ouvrir plus de 9 hectares environ à l'urbanisation sur la décennie, et encore, ce chiffre doit être confirmé par la déclinaison du SCoT.\nM. Viala : J'en viens aux premières orientations du projet d'aménagement et de développement durables, ce qu'on appelle le PADD. Il y en a quatre. Premièrement, conforter le centre-bourg, en privilégiant la construction dans les dents creuses et la réhabilitation des logements vacants. Deuxièmement, préserver les terres agricoles et les continuités écologiques, notamment le long de la rivière. Troisièmement, limiter fortement le développement des hameaux, où l'on autoriserait seulement l'extension mesurée des constructions existantes. Quatrièmement, développer les mobilités douces, avec un projet de liaison piétonne et cyclable entre le centre-bourg et le collège.\nM. Viala : Le PADD fera l'objet d'un débat au conseil municipal. Ce débat n'est pas un vote, c'est une étape obligatoire. Il est prévu en février 2027, la date exacte n'est pas fixée.\nM. Lacroix : Merci, monsieur Viala. Je vous propose maintenant de prendre les questions. Je vous demande de vous présenter et d'être bref pour que tout le monde puisse s'exprimer. Mme Paulin vous passera le micro.\nM. Roux (habitant du hameau des Granges) : Bonsoir. J'habite aux Granges depuis trente ans. Si je comprends bien, on ne pourra plus construire dans les hameaux. Mon fils voudrait construire sur le terrain que je lui ai donné. Ce terrain est constructible aujourd'hui. Est-ce qu'il le restera ?\nM. Viala : Je ne peux pas répondre pour une parcelle précise ce soir. Le zonage n'est pas encore dessiné. Ce que je peux dire, c'est que l'orientation est de limiter fortement les constructions nouvelles dans les hameaux.\nM. Roux : Donc c'est non.\nM. Lacroix : Ce n'est ni oui ni non, monsieur Roux. Aucune décision n'est prise. Je vous invite à écrire votre demande dans le registre de concertation, qui est en mairie, ou à l'envoyer par courrier. Toutes les demandes seront étudiées. Je ne veux pas vous faire de promesse que je ne pourrais pas tenir.\nM. Roux : C'est ce qu'on dit toujours.\nMme Benoist : Je comprends votre inquiétude. Beaucoup de familles sont dans votre cas. C'est pour cela que nous voulons organiser un atelier spécifique sur les hameaux.\nM. Lacroix : Oui, je vous l'annonce : un atelier de travail sur l'avenir des hameaux aura lieu le samedi 16 janvier 2027, de 9 h 30 à 12 h, ici même. Les habitants des hameaux y seront invités par courrier. Mme Paulin, vous enverrez les invitations ?\nMme Paulin : Oui, je préparerai le courrier avec la liste des adresses des hameaux, pour un envoi avant le 18 décembre.\nMme Hassan (habitante du centre-bourg) : Bonsoir. Moi, c'est l'inverse qui m'inquiète. Si on densifie le centre-bourg, qu'est-ce qui va se passer pour la circulation et le stationnement ? Le matin, devant l'école, c'est déjà impossible.\nM. Viala : C'est un vrai sujet. La densification doit s'accompagner d'une réflexion sur le stationnement. Le PLU peut imposer des places de stationnement pour les nouvelles constructions. Il peut aussi prévoir des emplacements réservés pour un parking.\nMme Hassan : Il y a un projet de parking ?\nM. Lacroix : Pas à ce stade. On pourrait envisager un emplacement réservé près de l'école, mais je ne veux pas l'annoncer comme acquis. Nous allons l'étudier.\nM. Fabre (agriculteur) : Bonsoir. Je suis éleveur, j'exploite 70 hectares sur la commune. Je voulais d'abord vous remercier de vouloir protéger les terres agricoles, c'est essentiel. Mais je voudrais aussi pouvoir construire un nouveau bâtiment d'élevage. Est-ce que la zone agricole le permettra ?\nM. Viala : En zone agricole, les constructions nécessaires à l'exploitation agricole sont autorisées. Il faudra simplement vérifier la compatibilité avec les règles de distance et de paysage. Mais le principe est oui pour les bâtiments agricoles.\nM. Fabre : Et pour un logement pour mon fils, qui va reprendre l'exploitation ?\nM. Viala : Le logement de l'exploitant peut être autorisé s'il est nécessaire à l'exploitation, c'est-à-dire si une présence permanente est indispensable, par exemple pour l'élevage. Cela s'apprécie au cas par cas.\nM. Fabre : Donc ce n'est pas automatique.\nM. Viala : Non, ce n'est pas automatique.\nMme Morel (association Drôme Nature) : Bonsoir. L'association se réjouit de l'orientation sur les continuités écologiques. Nous souhaitons que la ripisylve, c'est-à-dire la végétation le long de la rivière, soit protégée par une bande inconstructible d'au moins 20 mètres. Est-ce que c'est prévu ?\nM. Viala : Le principe d'une protection des berges est prévu. La largeur de la bande n'est pas fixée. Nous travaillons avec le syndicat de rivière. Je ne peux pas vous donner de chiffre ce soir.\nMme Morel : Nous déposerons une contribution écrite.\nM. Lacroix : Elle sera la bienvenue. Toutes les contributions écrites seront annexées au bilan de la concertation.\nM. Blanc (habitant) : Bonsoir. On parle beaucoup d'environnement, mais il y a un projet d'éoliennes sur le plateau, non ? Est-ce que le PLU va les autoriser ?\nM. Lacroix : Il n'y a aucun projet d'éoliennes déposé à ma connaissance. Un développeur a pris contact avec la mairie il y a deux ans, nous n'avons pas donné suite. Le PLU ne prévoit rien de spécifique à ce sujet, et je ne veux pas lancer une rumeur.\nM. Blanc : Mais si un développeur revient ?\nM. Lacroix : Les projets éoliens relèvent d'une autorisation environnementale délivrée par le préfet. La commune serait consultée. Mais je le répète : il n'y a pas de projet.\nMme Leblanc (habitante, présidente de l'association des parents d'élèves) : Bonsoir. Avec l'arrivée de nouvelles familles, l'école est pleine. Est-ce que le PLU prévoit un terrain pour agrandir l'école ou en construire une nouvelle ?\nMme Benoist : L'école peut être agrandie sur son terrain actuel, il reste de la place côté cour. Une nouvelle école n'est pas envisagée. En revanche, nous réfléchissons à un emplacement réservé pour un futur équipement public, sans savoir encore ce qu'il accueillera.\nMme Leblanc : Il faudrait quand même anticiper.\nM. Lacroix : Je vous entends. Les effectifs scolaires seront étudiés dans le diagnostic complémentaire. M. Viala, vous pourrez intégrer les prévisions d'effectifs ?\nM. Viala : Oui, je les intégrerai au diagnostic, à condition que la commune me transmette les chiffres de l'inspection.\nMme Garcia : Je les transmettrai à M. Viala avant la fin de l'année.\nM. Perrin (habitant) : Bonsoir. Je suis propriétaire d'une grange dans le hameau des Combes. Je voudrais la transformer en habitation. Est-ce que ce sera possible ?\nM. Viala : Le PLU peut identifier des bâtiments agricoles qui pourront changer de destination, à condition de ne pas compromettre l'activité agricole et la qualité paysagère. Il faudra un inventaire. Votre grange pourra éventuellement en faire partie, mais je ne peux pas le garantir.\nM. Perrin : Comment on fait pour qu'elle soit dans l'inventaire ?\nM. Viala : Le mieux est de la signaler dans le registre de concertation, avec une photo et la référence cadastrale.\nM. Lacroix : Je précise que M. Viala tiendra une permanence en mairie pour recevoir individuellement les habitants qui le souhaitent. Elle aura lieu le mardi 8 décembre, de 14 h à 18 h, sur rendez-vous auprès du service urbanisme.\nM. Perrin : Très bien, je prendrai rendez-vous.\nMme Dupuis (habitante) : Bonsoir. Je voudrais savoir quand l'enquête publique aura lieu. Certains disent que le PLU sera approuvé l'an prochain.\nM. Lacroix : Non, madame. Le calendrier prévisionnel prévoit l'arrêt du projet par le conseil municipal à l'été 2027, puis la consultation des personnes publiques associées pendant trois mois, puis l'enquête publique. L'enquête pourrait avoir lieu à la fin de 2027, mais la date n'est pas fixée. L'approbation n'interviendra pas avant 2028. Je préfère vous donner un calendrier prudent.\nMme Dupuis : Et d'ici là, est-ce que les permis sont bloqués ?\nM. Viala : Non, d'ici là, c'est le PLU actuel qui s'applique. Toutefois, une fois le débat sur le PADD tenu, la commune pourra, dans certains cas, opposer un sursis à statuer à une demande qui compromettrait le futur plan. C'est une possibilité, pas une obligation.\nMme Dupuis : Ça veut dire que mon voisin pourrait être bloqué ?\nM. Viala : Seulement si son projet compromet ou rend plus onéreuse l'exécution du futur plan. C'est apprécié au cas par cas, et la décision doit être motivée.\nM. Lacroix : Je veux rassurer : nous n'avons pas l'intention de bloquer les projets de manière systématique.\nM. Roux : Ça, c'est vous qui le dites.\nM. Lacroix : C'est moi qui le dis, et je l'assume, monsieur Roux.\nM. Garnier (commerçant) : Bonsoir. Je tiens la boulangerie de la place. Je voudrais savoir si le PLU va protéger les commerces du centre. Il y a deux ans, un local commercial a été transformé en logement, et on a perdu la mercerie.\nM. Viala : Le PLU peut interdire le changement de destination des rez-de-chaussée commerciaux dans certaines rues, ce qu'on appelle un linéaire commercial protégé. C'est un outil intéressant pour Villars-sur-Drôme.\nM. Garnier : Vous allez le faire ?\nMme Benoist : C'est une piste que nous étudions sérieusement. Je ne peux pas dire que c'est décidé.\nMme Hassan : Et pour les logements vacants, qu'est-ce que vous allez faire concrètement ?\nMme Benoist : Le PLU ne peut pas obliger un propriétaire à louer. Mais la commune peut accompagner les propriétaires, avec l'aide de l'intercommunalité, qui conduit une opération d'amélioration de l'habitat. Les aides de l'Anah peuvent financer une partie des travaux. Nous pourrons organiser une réunion d'information avec l'intercommunalité, mais je n'ai pas de date.\nM. Blanc : Et la liaison cyclable vers le collège, c'est pour quand ?\nM. Lacroix : Le PLU peut réserver le tracé. Les travaux, eux, dépendent du budget et des subventions. Je ne peux pas donner de date de travaux. Le département a été sollicité pour cofinancer, sans réponse à ce jour.\nMme Morel : Une question sur l'eau : avec la sécheresse de l'été dernier, est-ce que la ressource en eau permettra d'accueillir de nouveaux habitants ?\nM. Viala : C'est un point que nous devons étudier avec le syndicat des eaux. Le PLU doit justifier que la ressource est suffisante. Le syndicat nous a indiqué qu'elle l'était pour la croissance envisagée, mais une étude complémentaire est en cours. J'attends ses conclusions.\nMme Morel : Ce serait bien que les résultats soient rendus publics.\nM. Lacroix : Ils seront intégrés au dossier du PLU, qui sera public.\nUne habitante (sans se présenter) : Est-ce qu'on pourra voir les cartes du futur zonage avant l'enquête ?\nM. Lacroix : Oui. Je m'engage à ce qu'une première version de la carte de zonage soit présentée lors d'une seconde réunion publique, avant l'arrêt du projet. La date sera fixée au printemps. Et dès maintenant, la carte du diagnostic présentée ce soir sera mise en ligne sur le site de la commune.\nMme Paulin : Je la mettrai en ligne avec la présentation de M. Viala d'ici le vendredi 27 novembre.\nM. Fabre : Est-ce qu'on peut avoir aussi la carte des zones agricoles ?\nM. Viala : Elle n'existe pas encore sous forme définitive. Celle du diagnostic montre l'occupation actuelle des sols. Elle sera en ligne.\nM. Chevalier (habitant du quartier du Pré-Long) : Bonsoir. J'ai entendu dire que le terrain du Pré-Long, derrière la salle polyvalente, allait devenir un lotissement de quarante maisons. Est-ce vrai ?\nM. Viala : Le Pré-Long est effectivement identifié dans le diagnostic comme un secteur stratégique, car il est proche du centre et des équipements. Mais aucun programme n'est arrêté. Si le secteur est ouvert à l'urbanisation, le PLU comprendra une orientation d'aménagement et de programmation, qui fixera des principes : densité, accès, espaces verts, part éventuelle de logements aidés. Le chiffre de quarante maisons ne vient pas de nous.\nM. Chevalier : On craint surtout pour la circulation dans notre rue, qui est étroite.\nM. Viala : L'accès au secteur est justement l'une des questions à étudier. Plusieurs options existent, dont une desserte par la route de la salle polyvalente. Rien n'est tranché.\nM. Lacroix : Je vous propose, monsieur Chevalier, d'inscrire vos remarques dans le registre. Les riverains du Pré-Long seront associés si le secteur est retenu. Mais je ne peux pas vous dire aujourd'hui s'il le sera.\nMme Rivière (habitante) : Bonsoir. Je suis âgée et je vis seule dans une grande maison. Je voudrais rester à Villars, mais dans un logement plus petit. Est-ce que le PLU prévoit des logements adaptés aux personnes âgées ?\nMme Benoist : C'est une vraie préoccupation. Le PLU peut favoriser des petits logements dans le centre, près des commerces et du médecin. Nous avons aussi été contactés par un bailleur pour un projet d'habitat inclusif, mais c'est très préliminaire et il n'y a aucun engagement.\nMme Rivière : Ça prendra combien de temps ?\nMme Benoist : Je ne peux pas vous le dire, madame. Ce serait plusieurs années dans le meilleur des cas.\nM. Lambert (artisan) : Bonsoir. Je suis artisan menuisier. La petite zone d'activités des Sables est pleine. Est-ce que le PLU va l'agrandir ? Plusieurs artisans cherchent un terrain.\nM. Viala : La compétence en matière de zones d'activités économiques appartient à l'intercommunalité. Le PLU peut prévoir une extension si elle est cohérente avec la stratégie économique intercommunale et avec le SCoT. Pour l'instant, l'intercommunalité n'a pas exprimé de besoin d'extension aux Sables. Il faut aussi tenir compte de la limitation de la consommation d'espace dont j'ai parlé.\nM. Lambert : Donc il faut voir avec l'intercommunalité.\nM. Lacroix : Oui, et je peux relayer votre demande auprès du vice-président chargé de l'économie. Je m'engage à le faire, mais la décision ne m'appartient pas.\nMme Tissier (habitante du quartier de la Plaine) : Bonsoir. Mon quartier a été inondé en 2019. Est-ce que le PLU va tenir compte du risque d'inondation ?\nM. Viala : Oui, obligatoirement. La commune est couverte par un plan de prévention du risque inondation approuvé par le préfet. Il s'impose au PLU. Les zones rouges du plan de prévention restent inconstructibles, et les règles des zones bleues s'appliqueront en plus des règles du PLU. Le PLU ne peut pas être moins strict.\nMme Tissier : Est-ce que le plan de prévention va être révisé ? On nous a dit que la carte allait changer.\nM. Viala : Une révision du plan de prévention est en effet évoquée par les services de l'État, mais elle n'est pas engagée. Je n'ai pas d'information sur la date ni sur le contenu.\nM. Lacroix : Si l'État révise ce plan, il y aura une enquête publique spécifique. Nous vous tiendrons informés.\nM. Aubert (habitant du hameau de Saint-Pierre) : Bonsoir. Dans notre hameau, il y a une chapelle classée, et l'architecte des bâtiments de France donne son avis sur tous les travaux dans un rayon de 500 mètres. Est-ce que le PLU va changer ça ?\nM. Viala : Le périmètre de protection autour d'un monument historique est une servitude qui ne dépend pas du PLU. Il peut toutefois être adapté, par un périmètre délimité des abords, sur proposition de l'architecte des bâtiments de France et après enquête publique. Cela peut être mené en même temps que le PLU. La commune n'a pas encore décidé de le demander.\nM. Aubert : Ce serait bien, parce que le périmètre actuel englobe des maisons qu'on ne voit même pas depuis la chapelle.\nMme Benoist : Nous étudierons l'opportunité de cette démarche avec l'architecte des bâtiments de France. Je ne peux pas aller plus loin ce soir.\nMme Collin (habitante) : Bonsoir. Est-ce que le PLU va imposer des panneaux solaires sur les toits ou au contraire les interdire ? Dans le lotissement, on nous a refusé des panneaux il y a quelques années.\nM. Viala : Le PLU ne peut pas imposer des panneaux solaires à une maison individuelle existante. Il peut en revanche faciliter leur installation et fixer des règles d'insertion paysagère. Dans le centre ancien et dans les abords de la chapelle, des précautions resteront nécessaires. L'idée est plutôt de les autoriser largement ailleurs.\nMme Collin : Et le refus d'il y a quelques années, il venait de quoi ?\nM. Viala : Je ne connais pas votre dossier. Il venait peut-être du règlement du lotissement ou de l'avis de l'architecte des bâtiments de France. Je vous invite à venir à la permanence avec les documents.\nM. Blanc : Une question sur la fibre : est-ce que le PLU peut obliger à amener la fibre dans les hameaux ?\nM. Viala : Le PLU peut imposer que les nouvelles constructions prévoient les fourreaux nécessaires au raccordement. Mais le déploiement de la fibre relève de l'opérateur et du syndicat départemental du numérique, pas du PLU.\nM. Lacroix : Je peux vous dire que le syndicat départemental annonce l'achèvement du déploiement pour 2027 sur la commune, mais c'est son calendrier, pas le nôtre.\nMme Hassan : Encore une question : est-ce que la taxe d'aménagement va augmenter avec le nouveau PLU ?\nMme Garcia : La taxe d'aménagement est fixée par une délibération du conseil municipal, distincte du PLU. Le taux communal est aujourd'hui de 4 %. Le conseil peut le modifier chaque année, avant le 1er juillet pour une application l'année suivante. Aucune modification n'est envisagée à ce jour.\nM. Roux : Vous dites « à ce jour » ?\nMme Garcia : Je dis « à ce jour », parce que je ne peux pas engager les choix futurs du conseil municipal.\nUn jeune habitant : Bonsoir. J'ai 26 ans, je travaille à Valence et je voudrais acheter ici, mais tout est trop cher. Est-ce que le PLU peut faire baisser les prix ?\nM. Viala : Le PLU ne fixe pas les prix. Il peut favoriser une offre plus diversifiée, avec des terrains plus petits, des logements groupés, de l'accession aidée. Mais les prix dépendent aussi du marché régional.\nMme Benoist : Nous réfléchissons à un dispositif d'accession aidée avec l'intercommunalité. Ce n'est qu'une réflexion.\nM. Lacroix : Bien. Je voudrais faire le point sur ce que nous retenons ce soir. Premièrement, la concertation se poursuit. Le registre devait être clos le 31 décembre ; compte tenu des nombreuses demandes, je décide de prolonger la concertation et le registre jusqu'au 31 janvier 2027. Mme Garcia, vous ferez publier l'avis de prolongation ?\nMme Garcia : Oui, l'avis sera affiché en mairie et publié sur le site la semaine prochaine.\nM. Lacroix : Deuxièmement, l'atelier sur les hameaux le samedi 16 janvier. Troisièmement, la permanence de M. Viala le mardi 8 décembre. Quatrièmement, la mise en ligne de la présentation et de la carte du diagnostic. Cinquièmement, un compte rendu de cette réunion sera publié sur le site dans les quinze jours.\nMme Paulin : Je rédige le compte rendu et je le soumets à M. le maire avant le mercredi 2 décembre.\nM. Roux : Et nos demandes de constructibilité, vous les traitez quand ?\nM. Lacroix : Elles seront étudiées au fur et à mesure de l'élaboration du zonage, et vous aurez une réponse globale lors de la présentation du projet. Aucune réponse individuelle ne sera donnée avant, pour être juste avec tout le monde.\nM. Garnier : Une dernière chose : est-ce que les commerçants pourront être associés au travail sur le linéaire commercial ?\nMme Benoist : Oui, je propose qu'on organise une rencontre avec les commerçants du centre. Je vous contacterai, monsieur Garnier, pour trouver une date en janvier.\nM. Lacroix : Merci à tous pour la qualité des échanges, même quand ils ont été vifs. Je sais que le sujet touche chacun personnellement. Je vous rappelle que tous les documents sont consultables en mairie aux heures d'ouverture. La réunion est terminée, il est 21 h 20. Nous restons quelques minutes si vous souhaitez échanger individuellement.\n\n(Échanges informels après la réunion, enregistrés à la demande du maire.)\nUne habitante : Monsieur le maire, l'atelier du 16 janvier, c'est seulement pour les gens des hameaux ?\nM. Lacroix : Les habitants des hameaux seront invités par courrier, mais l'atelier est ouvert à tous ceux qui s'inscrivent en mairie, dans la limite des places. Disons une quarantaine de personnes.\nMme Paulin : J'ouvre les inscriptions dès demain à l'accueil.\nUn habitant : Et pour la permanence de l'urbaniste, il reste de la place ?\nMme Paulin : Il y a seize créneaux d'un quart d'heure. Je ne peux pas vous dire combien sont déjà pris, appelez demain le service urbanisme.\nM. Viala : Si les créneaux sont tous pris, je pourrai éventuellement proposer une seconde permanence, mais je dois d'abord vérifier mon planning avec la mairie.\nM. Lacroix : Ne promettons rien de plus ce soir.\nM. Fabre : Monsieur le maire, un mot encore sur les chemins ruraux. Avec les nouvelles maisons, il y a de plus en plus de voitures sur les chemins agricoles, et nos tracteurs ont du mal à passer. Est-ce que le PLU peut régler ça ?\nM. Lacroix : Le PLU peut prévoir des emplacements réservés pour élargir certaines voies, mais la circulation sur les chemins ruraux relève surtout de mes pouvoirs de police. Je peux prendre un arrêté pour réglementer la circulation sur un chemin. Je vous propose de m'indiquer les chemins concernés, et j'en parlerai avec la commission des travaux. Je ne décide rien ce soir.\nM. Fabre : Je vous envoie la liste par écrit.\nMme Morel : Monsieur Viala, l'association aimerait aussi être associée au travail sur la trame verte et bleue. Est-ce possible ?\nM. Viala : C'est la commune qui pilote la concertation. Je n'ai pas d'objection, au contraire, vos inventaires de terrain peuvent être très utiles.\nM. Lacroix : L'association sera invitée à l'atelier sur les hameaux, qui abordera aussi les continuités écologiques autour des Granges et des Combes. Pour un travail plus spécifique, nous verrons après l'atelier.\nMme Leblanc : Et pour l'école, on aura une réponse quand ?\nMme Benoist : Les chiffres d'effectifs seront intégrés au diagnostic complémentaire, présenté lors de la seconde réunion publique au printemps. Je vous propose aussi d'en parler au prochain conseil d'école.\nMme Leblanc : Le conseil d'école est le 11 février.\nMme Benoist : Alors j'y viendrai, si la directrice m'y invite.\nM. Lacroix : Merci à tous. Bonne soirée.",
  "nb_mots": 4032
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
 "type_reunion": "réunion publique de concertation sur la révision du PLU",
 "participants_reference": [
  "M. Lacroix (maire)",
  "Mme Benoist (adjointe à l'urbanisme)",
  "Mme Garcia (DGS)",
  "M. Viala (urbaniste, bureau d'études Territoires et Paysages)",
  "Mme Paulin (service urbanisme, prise de notes)",
  "Environ quatre-vingts habitants, dont MM. Roux, Fabre, Blanc, Perrin, Garnier, Chevalier, Lambert, Aubert et Mmes Hassan, Morel (association Drôme Nature), Leblanc (parents d'élèves), Dupuis, Rivière, Tissier, Collin"
 ],
 "decisions_reference": [
  "Prolongation de la concertation et du registre jusqu'au 31 janvier 2027 (au lieu du 31 décembre)",
  "Atelier sur l'avenir des hameaux le samedi 16 janvier 2027, de 9 h 30 à 12 h, à la salle polyvalente",
  "Permanence individuelle de l'urbaniste en mairie le mardi 8 décembre, de 14 h à 18 h, sur rendez-vous",
  "Mise en ligne de la présentation et de la carte du diagnostic ; compte rendu publié sur le site dans les quinze jours",
  "Présentation d'une première version de la carte de zonage lors d'une seconde réunion publique au printemps, avant l'arrêt du projet"
 ],
 "actions_reference": [
  {
   "action": "Envoyer les invitations à l'atelier aux habitants des hameaux",
   "responsable": "Mme Paulin",
   "echeance": "avant le 18 décembre 2026"
  },
  {
   "action": "Transmettre les prévisions d'effectifs scolaires à l'urbaniste",
   "responsable": "Mme Garcia",
   "echeance": "avant la fin de l'année 2026"
  },
  {
   "action": "Mettre en ligne la présentation et la carte du diagnostic",
   "responsable": "Mme Paulin",
   "echeance": "d'ici le vendredi 27 novembre 2026"
  },
  {
   "action": "Faire publier l'avis de prolongation de la concertation",
   "responsable": "Mme Garcia",
   "echeance": "la semaine suivante (semaine du 23 novembre 2026)"
  },
  {
   "action": "Rédiger le compte rendu et le soumettre au maire",
   "responsable": "Mme Paulin",
   "echeance": "avant le mercredi 2 décembre 2026"
  },
  {
   "action": "Contacter M. Garnier pour une rencontre avec les commerçants du centre",
   "responsable": "Mme Benoist",
   "echeance": "janvier 2027"
  },
  {
   "action": "Relayer la demande d'extension de la zone d'activités auprès du vice-président de l'intercommunalité",
   "responsable": "M. Lacroix",
   "echeance": "non fixée"
  },
  {
   "action": "Ouvrir les inscriptions à l'atelier à l'accueil",
   "responsable": "Mme Paulin",
   "echeance": "le lendemain de la réunion (jeudi 19 novembre 2026)"
  }
 ],
 "pieges": [
  "Aucune décision de zonage ; aucune réponse sur la constructibilité de parcelles individuelles",
  "Débat sur le PADD prévu en février 2027 (date non fixée), sans vote",
  "Calendrier : arrêt du projet à l'été 2027, enquête publique fin 2027 non fixée, approbation pas avant 2028",
  "Parking près de l'école, linéaire commercial protégé, emplacement réservé pour un équipement : pistes à l'étude, non décidées",
  "Pas de projet éolien ; lotissement de quarante maisons au Pré-Long : chiffre non confirmé, rien d'arrêté",
  "Largeur de la bande de protection des berges non fixée",
  "Extension de la zone d'activités : compétence intercommunale",
  "Périmètre délimité des abords de la chapelle : non demandé à ce stade",
  "Taux de la taxe d'aménagement (4 %) : aucune modification envisagée à ce jour",
  "Seconde permanence de l'urbaniste : non promise",
  "Date de la seconde réunion publique non fixée (printemps)"
 ]
}
```

## CT-501 — Courrier type (facile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CT-501",
 "tache": "Courrier type",
 "difficulte": "facile",
 "theme": "collectivites",
 "entree": {
  "type": "accusé de réception",
  "objet": "Demande d'autorisation d'installer une terrasse sur le trottoir",
  "elements_connus": {
   "demandeur": "M. Julien Morel, gérant du café « Le Bon Coin »",
   "date_reception": "lundi 5 octobre 2026",
   "service": "Service du domaine public de la mairie",
   "suite_donnee": "la demande sera instruite par le service, qui pourra se rendre sur place avant de rendre sa décision"
  },
  "consigne": "Rédige l'accusé de réception de cette demande au format administratif français. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse du café], [Commune], [Date du courrier], [Référence du dossier], [Téléphone et courriel du service], [Nom et qualité du signataire]."
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
  "En-tête de l'expéditeur (mairie, service du domaine public)",
  "Bloc destinataire (M. Julien Morel, gérant du café « Le Bon Coin »)",
  "Lieu et date (en emplacement)",
  "Objet",
  "Référence du dossier (en emplacement)",
  "Formule d'appel « Monsieur, »",
  "Date de réception de la demande : lundi 5 octobre 2026",
  "Instruction par le service, visite possible sur place avant décision",
  "Coordonnées du service (en emplacement)",
  "Formule de politesse",
  "Signature : nom et qualité du signataire (en emplacement)"
 ],
 "champs_a_laisser_en_emplacement": [
  "[Adresse du café]",
  "[Commune]",
  "[Date du courrier]",
  "[Référence du dossier]",
  "[Téléphone et courriel du service]",
  "[Nom et qualité du signataire]"
 ],
 "valeurs_interdites": [
  "toute autorisation accordée (la demande n'est pas encore instruite)",
  "tout montant de redevance inventé",
  "toute adresse, tout numéro de téléphone ou courriel inventé",
  "tout nom de signataire inventé"
 ]
}
```

## CT-505 — Courrier type (facile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CT-505",
 "tache": "Courrier type",
 "difficulte": "facile",
 "theme": "social-autonomie",
 "entree": {
  "type": "accusé de réception",
  "objet": "Demande de logement social",
  "elements_connus": {
   "demandeur": "Mme Fatou Diallo",
   "date_reception": "14 octobre 2026",
   "service": "Service logement de la mairie",
   "information": "la demande a été enregistrée et un numéro unique d'enregistrement lui sera communiqué ; elle devra renouveler sa demande chaque année"
  },
  "consigne": "Rédige l'accusé de réception de cette demande au format administratif français. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse de la demandeuse], [Commune], [Numéro unique d'enregistrement], [Date du courrier], [Téléphone et courriel du service], [Nom et qualité du signataire]."
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
  "En-tête de l'expéditeur (mairie, service logement)",
  "Bloc destinataire (Mme Fatou Diallo)",
  "Lieu et date (en emplacement)",
  "Objet",
  "Formule d'appel « Madame, »",
  "Date de réception : 14 octobre 2026",
  "Enregistrement de la demande, numéro unique d'enregistrement (en emplacement)",
  "Obligation de renouveler la demande chaque année",
  "Coordonnées du service (en emplacement)",
  "Formule de politesse",
  "Signature : nom et qualité du signataire (en emplacement)"
 ],
 "champs_a_laisser_en_emplacement": [
  "[Adresse de la demandeuse]",
  "[Commune]",
  "[Numéro unique d'enregistrement]",
  "[Date du courrier]",
  "[Téléphone et courriel du service]",
  "[Nom et qualité du signataire]"
 ],
 "valeurs_interdites": [
  "toute promesse ou date d'attribution d'un logement",
  "tout numéro unique inventé",
  "toute adresse, tout numéro de téléphone ou courriel inventé",
  "tout nom de signataire inventé"
 ]
}
```

## CT-509 — Courrier type (moyen, thème `fiscalite-locale`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CT-509",
 "tache": "Courrier type",
 "difficulte": "moyen",
 "theme": "fiscalite-locale",
 "entree": {
  "type": "accusé de réception",
  "objet": "Réclamation sur le montant de la taxe foncière, transmise au service compétent",
  "elements_connus": {
   "demandeur": "M. Bernard Lucas",
   "date_reception": "vendredi 2 octobre 2026",
   "objet_reclamation": "contestation du montant de sa taxe foncière 2026",
   "situation": "la réclamation a été adressée à la mairie, qui n'est pas compétente pour en connaître ; elle a été transmise le mardi 6 octobre 2026 au service des impôts des particuliers dont relève le contribuable",
   "texte_applicable": "CRPA, Article L114-2 : « Lorsqu'une demande est adressée à une administration incompétente, cette dernière la transmet à l'administration compétente et en avise l'intéressé. »"
  },
  "consigne": "Rédige l'accusé de réception de cette réclamation au format administratif français, en respectant l'article fourni. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse du demandeur], [Commune], [Adresse du service des impôts des particuliers], [Date du courrier], [Référence du dossier], [Téléphone et courriel du service], [Nom et qualité du signataire]."
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Demande d'agent rédigée pour l'évaluation (scénario fictif)"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/legi, code des relations entre le public et l'administration, article L114-2",
   "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031367394",
   "type": "legi",
   "code": "legi_code_des_relations_entre_le_public_et_l_administration",
   "articles": [
    "L114-2"
   ],
   "legiarti": "LEGIARTI000031367394",
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
  "En-tête de l'expéditeur (mairie)",
  "Bloc destinataire (M. Bernard Lucas)",
  "Lieu et date (en emplacement)",
  "Objet",
  "Référence (en emplacement)",
  "Formule d'appel « Monsieur, »",
  "Date de réception : vendredi 2 octobre 2026",
  "La mairie n'est pas compétente pour traiter la réclamation",
  "Transmission le mardi 6 octobre 2026 au service des impôts des particuliers compétent (adresse en emplacement)",
  "Information de l'intéressé de cette transmission (avis prévu par l'article L. 114-2 du CRPA)",
  "Coordonnées du service (en emplacement)",
  "Formule de politesse",
  "Signature : nom et qualité du signataire (en emplacement)"
 ],
 "champs_a_laisser_en_emplacement": [
  "[Adresse du demandeur]",
  "[Commune]",
  "[Adresse du service des impôts des particuliers]",
  "[Date du courrier]",
  "[Référence du dossier]",
  "[Téléphone et courriel du service]",
  "[Nom et qualité du signataire]"
 ],
 "valeurs_interdites": [
  "toute appréciation sur le bien-fondé de la réclamation",
  "tout montant de taxe ou de dégrèvement inventé",
  "toute adresse, tout numéro de téléphone ou courriel inventé",
  "tout nom de signataire inventé"
 ],
 "base_reglementaire": {
  "article": "CRPA L. 114-2",
  "legiarti": "LEGIARTI000031367394",
  "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031367394",
  "texte": "Article L114-2 : « Lorsqu'une demande est adressée à une administration incompétente, cette dernière la transmet à l'administration compétente et en avise l'intéressé. »",
  "extrait": "article(s) complet(s), texte verbatim, fourni à l'Assistant dans elements_connus.texte_applicable"
 }
}
```

## CT-511 — Courrier type (moyen, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CT-511",
 "tache": "Courrier type",
 "difficulte": "moyen",
 "theme": "collectivites",
 "entree": {
  "type": "demande de pièces",
  "objet": "Demande de subvention de l'association « Les Jardins partagés » incomplète",
  "elements_connus": {
   "association": "association « Les Jardins partagés », représentée par son président, M. Lucien Faure",
   "date_depot": "mercredi 30 septembre 2026",
   "montant_sollicite": "1 500 euros",
   "pieces_manquantes": "le budget prévisionnel de l'action, le relevé d'identité bancaire de l'association et le dernier rapport d'activité",
   "date_limite": "15 décembre 2026",
   "consequence": "un dossier incomplet à cette date ne pourra pas être présenté au conseil municipal de janvier 2027",
   "expediteur": "la mairie, service vie associative"
  },
  "consigne": "Rédige le courrier demandant les pièces manquantes au format administratif français. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse de l'association], [Commune], [Date du courrier], [Référence du dossier], [Téléphone et courriel du service], [Nom et qualité du signataire]."
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
 "version_item": 2,
 "type_courrier": "demande de pièces",
 "elements_obligatoires": [
  "En-tête de l'expéditeur (mairie, service vie associative)",
  "Bloc destinataire (association « Les Jardins partagés », à l'attention de M. Lucien Faure, président)",
  "Lieu et date (en emplacement)",
  "Objet",
  "Référence du dossier (en emplacement)",
  "Formule d'appel « Monsieur le Président, »",
  "Rappel du dépôt du mercredi 30 septembre 2026 et du montant sollicité de 1 500 euros",
  "Pièces manquantes : budget prévisionnel de l'action, RIB, dernier rapport d'activité",
  "Date limite : 15 décembre 2026",
  "Conséquence : pas de présentation au conseil municipal de janvier 2027 si le dossier est incomplet",
  "Coordonnées du service (en emplacement)",
  "Formule de politesse",
  "Signature : nom et qualité du signataire (en emplacement)"
 ],
 "champs_a_laisser_en_emplacement": [
  "[Adresse de l'association]",
  "[Commune]",
  "[Date du courrier]",
  "[Référence du dossier]",
  "[Téléphone et courriel du service]",
  "[Nom et qualité du signataire]"
 ],
 "valeurs_interdites": [
  "toute décision d'attribution ou de refus de la subvention",
  "tout autre montant que 1 500 euros",
  "toute adresse, tout numéro de téléphone ou courriel inventé",
  "tout nom de signataire inventé"
 ]
}
```

## CT-517 — Courrier type (difficile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CT-517",
 "tache": "Courrier type",
 "difficulte": "difficile",
 "theme": "social-autonomie",
 "entree": {
  "type": "convocation",
  "objet": "Invitation à présenter ses observations avant le retrait d'une aide facultative",
  "elements_connus": {
   "destinataire": "Mme Sandrine Collin",
   "aide": "aide municipale facultative au transport, attribuée le 15 janvier 2026",
   "motif_envisage": "absence de transmission, malgré deux relances, du justificatif de ressources demandé pour le réexamen annuel",
   "decision_envisagee": "retrait de l'aide à compter du 1er janvier 2027",
   "date_entretien": "mercredi 25 novembre 2026",
   "heure": "15 h 00",
   "lieu": "CCAS, bureau 3",
   "observations_ecrites": "possibles jusqu'au 25 novembre 2026",
   "texte_applicable": "CRPA, Article L122-1 : « Les décisions mentionnées à l'article L. 211-2 n'interviennent qu'après que la personne intéressée a été mise à même de présenter des observations écrites et, le cas échéant, sur sa demande, des observations orales. Cette personne peut se faire assister par un conseil ou représenter par un mandataire de son choix. L'administration n'est pas tenue de satisfaire les demandes d'audition abusives, notamment par leur nombre ou leur caractère répétitif ou systématique. »"
  },
  "consigne": "Rédige la convocation de Mme Collin au format administratif français, en respectant l'article fourni. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse de la destinataire], [Commune], [Date du courrier], [Référence du dossier], [Téléphone et courriel du service], [Nom et qualité du signataire]."
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Demande d'agent rédigée pour l'évaluation (scénario fictif)"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/legi, code des relations entre le public et l'administration, article L122-1",
   "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031367431",
   "type": "legi",
   "code": "legi_code_des_relations_entre_le_public_et_l_administration",
   "articles": [
    "L122-1"
   ],
   "legiarti": "LEGIARTI000031367431",
   "depot": "AgentPublic/legi",
   "revision": "68b01fbbe0cdaf5fe7b8a6befe4b8acab41530f8",
   "role": "base réglementaire du courrier"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce. Articles cités : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face).",
 "fictif": true,
 "version_item": 1,
 "type_courrier": "convocation",
 "elements_obligatoires": [
  "En-tête de l'expéditeur (CCAS)",
  "Bloc destinataire (Mme Sandrine Collin)",
  "Lieu et date (en emplacement)",
  "Objet",
  "Référence du dossier (en emplacement)",
  "Formule d'appel « Madame, »",
  "Exposé du motif : absence de justificatif de ressources malgré deux relances, pour le réexamen annuel",
  "Décision envisagée (non encore prise) : retrait de l'aide au transport à compter du 1er janvier 2027",
  "Possibilité de présenter des observations écrites jusqu'au 25 novembre 2026 et des observations orales lors de l'entretien du mercredi 25 novembre 2026, 15 h 00, CCAS, bureau 3",
  "Possibilité de se faire assister par un conseil ou représenter par un mandataire de son choix",
  "Coordonnées du service (en emplacement)",
  "Formule de politesse",
  "Signature : nom et qualité du signataire (en emplacement)"
 ],
 "champs_a_laisser_en_emplacement": [
  "[Adresse de la destinataire]",
  "[Commune]",
  "[Date du courrier]",
  "[Référence du dossier]",
  "[Téléphone et courriel du service]",
  "[Nom et qualité du signataire]"
 ],
 "valeurs_interdites": [
  "présentation du retrait comme déjà décidé",
  "tout montant de l'aide inventé",
  "tout autre motif que celui fourni",
  "toute adresse, tout numéro de téléphone ou courriel inventé",
  "tout nom de signataire inventé"
 ],
 "base_reglementaire": {
  "article": "CRPA L. 122-1",
  "legiarti": "LEGIARTI000031367431",
  "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031367431",
  "texte": "Article L122-1 : « Les décisions mentionnées à l'article L. 211-2 n'interviennent qu'après que la personne intéressée a été mise à même de présenter des observations écrites et, le cas échéant, sur sa demande, des observations orales. Cette personne peut se faire assister par un conseil ou représenter par un mandataire de son choix. L'administration n'est pas tenue de satisfaire les demandes d'audition abusives, notamment par leur nombre ou leur caractère répétitif ou systématique. »",
  "extrait": "article(s) complet(s), texte verbatim, fourni à l'Assistant dans elements_connus.texte_applicable"
 }
}
```

## CT-519 — Courrier type (difficile, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

```json
{
 "id": "CT-519",
 "tache": "Courrier type",
 "difficulte": "difficile",
 "theme": "famille-education-sante",
 "entree": {
  "type": "réponse d'information",
  "objet": "Communication des motifs d'un refus implicite de dérogation scolaire",
  "elements_connus": {
   "demandeurs": "M. et Mme Fabre",
   "demande_initiale": "dérogation au secteur scolaire pour leur fils Hugo vers l'école du Centre, déposée le 3 mars 2026, restée sans réponse (refus implicite)",
   "demande_de_motifs": "reçue le 2 juin 2026",
   "motifs": "l'école du Centre avait atteint sa capacité d'accueil en CE2 ; le motif invoqué (garde par les grands-parents) ne figure pas parmi les critères prioritaires fixés par la commission",
   "voie_de_recours": "recours devant le tribunal administratif",
   "texte_applicable": "CRPA, Article L232-4 : « Une décision implicite intervenue dans les cas où la décision explicite aurait dû être motivée n'est pas illégale du seul fait qu'elle n'est pas assortie de cette motivation.Toutefois, à la demande de l'intéressé, formulée dans les délais du recours contentieux, les motifs de toute décision implicite de rejet devront lui être communiqués dans le mois suivant cette demande. Dans ce cas, le délai du recours contentieux contre ladite décision est prorogé jusqu'à l'expiration de deux mois suivant le jour où les motifs lui auront été communiqués. »",
   "expediteur": "la mairie, service des affaires scolaires"
  },
  "consigne": "Rédige la réponse communiquant les motifs du refus au format administratif français, en respectant l'article fourni, notamment pour le délai de recours. Laisse les informations non fournies en emplacement, avec exactement ces libellés : [Adresse des demandeurs], [Commune], [Date du courrier], [Référence du dossier], [Nom du tribunal administratif], [Nom et qualité du signataire]."
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Demande d'agent rédigée pour l'évaluation (scénario fictif)"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/legi, code des relations entre le public et l'administration, article L232-4",
   "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031367639",
   "type": "legi",
   "code": "legi_code_des_relations_entre_le_public_et_l_administration",
   "articles": [
    "L232-4"
   ],
   "legiarti": "LEGIARTI000031367639",
   "depot": "AgentPublic/legi",
   "revision": "68b01fbbe0cdaf5fe7b8a6befe4b8acab41530f8",
   "role": "base réglementaire du courrier"
  }
 ],
 "licence_source": "Création originale du projet (contenu fictif rédigé pour l'évaluation) ; pas de source tierce. Articles cités : Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face).",
 "fictif": true,
 "version_item": 2,
 "type_courrier": "réponse d'information",
 "elements_obligatoires": [
  "En-tête de l'expéditeur (mairie, service des affaires scolaires)",
  "Bloc destinataire (M. et Mme Fabre)",
  "Lieu et date (en emplacement)",
  "Objet",
  "Référence du dossier (en emplacement)",
  "Formule d'appel « Madame, Monsieur, »",
  "Rappel de la demande du 3 mars 2026 restée sans réponse (décision implicite de rejet) et de la demande de motifs reçue le 2 juin 2026",
  "Motifs : capacité d'accueil atteinte en CE2 à l'école du Centre ; motif invoqué hors des critères prioritaires de la commission",
  "Délai de recours contentieux prorogé jusqu'à deux mois après la communication des motifs",
  "Voie de recours : tribunal administratif (nom en emplacement)",
  "Formule de politesse",
  "Signature : nom et qualité du signataire (en emplacement)"
 ],
 "champs_a_laisser_en_emplacement": [
  "[Adresse des demandeurs]",
  "[Commune]",
  "[Date du courrier]",
  "[Référence du dossier]",
  "[Nom du tribunal administratif]",
  "[Nom et qualité du signataire]"
 ],
 "valeurs_interdites": [
  "tout autre motif que ceux fournis",
  "toute nouvelle décision favorable",
  "tout délai de recours autre que celui de l'article",
  "toute adresse, tout numéro de téléphone ou courriel inventé",
  "tout nom de signataire inventé"
 ],
 "base_reglementaire": {
  "article": "CRPA L. 232-4",
  "legiarti": "LEGIARTI000031367639",
  "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031367639",
  "texte": "Article L232-4 : « Une décision implicite intervenue dans les cas où la décision explicite aurait dû être motivée n'est pas illégale du seul fait qu'elle n'est pas assortie de cette motivation.Toutefois, à la demande de l'intéressé, formulée dans les délais du recours contentieux, les motifs de toute décision implicite de rejet devront lui être communiqués dans le mois suivant cette demande. Dans ce cas, le délai du recours contentieux contre ladite décision est prorogé jusqu'à l'expiration de deux mois suivant le jour où les motifs lui auront été communiqués. »",
  "extrait": "article(s) complet(s), texte verbatim, fourni à l'Assistant dans elements_connus.texte_applicable"
 }
}
```

## LC-502 — Langage clair (facile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "LC-502",
 "tache": "Langage clair",
 "difficulte": "facile",
 "theme": "social-autonomie",
 "entree": {
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "texte": "L'absence de réponse de votre CPAM ou votre MSA dans le délai de 15 jours à partir de la réception de la demande vaut accord. Ce délai peut être porté à une durée maximale de 21 jours lorsque la prestation concernée justifie un délai supérieur (exemple : complexité de l'analyse de la demande d'accord). (À savoir: Depuis le 1 er décembre 2025, les fauteuils roulants sont pris en charge intégralement. Des ajouts ou des options spécifiques peuvent être pris en charge sur devis, en envoyant une demande d'accord préalable à l'Assurance Maladie. Cette dernière dispose de 2 mois pour vous répondre une fois reçue la demande complète.)\nEn cas de refus de prise en charge, vous recevez une réponse écrite. Dans ce cas, l'Assurance maladie vous indique les voies et délai de recours dont vous disposez pour contester la décision.",
  "nb_mots": 139
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F168 « Accord préalable de l'Assurance maladie » (chunks 4)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F168",
   "type": "service-public",
   "doc_id": "F168",
   "chunks": [
    4
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "informations_a_conserver": [
  "Sans réponse de la CPAM ou de la MSA dans les 15 jours suivant la réception de la demande, l'accord préalable est acquis",
  "Ce délai peut aller jusqu'à 21 jours si la prestation le justifie (par exemple une demande complexe)",
  "Depuis le 1er décembre 2025, les fauteuils roulants sont pris en charge intégralement",
  "Les ajouts ou options spécifiques peuvent être pris en charge sur devis, par une demande d'accord préalable ; l'Assurance maladie a alors 2 mois pour répondre après réception de la demande complète",
  "Un refus de prise en charge est notifié par écrit, avec les voies et délais de recours"
 ],
 "termes_juridiques_a_conserver": [
  "accord préalable",
  "CPAM",
  "MSA",
  "voies et délai de recours"
 ],
 "kandel_moles_entree": 70.89,
 "version_texte": 1
}
```

## LC-505 — Langage clair (facile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "LC-505",
 "tache": "Langage clair",
 "difficulte": "facile",
 "theme": "collectivites",
 "entree": {
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "texte": "La commune bénéficie d'un droit de préemption commercial pour acheter en priorité un bail commercial, un fonds de commerce, un fonds artisanal ou un terrain situé dans une zone de sauvegarde du commerce de proximité. Elle peut déléguer ce droit aux personnes et entités suivantes :\n- EPCI dont elle fait partie\n\n- Établissement public\n- Société d'économie mixte (SEM)\n- Concessionnaire d'une opération d'aménagement\n- Personne titulaire d'un contrat portant sur la réalisation d'actions ou d'opérations de redynamisation commerciale ou artisanale\nSi le fonds artisanal, le fonds de commerce, le bail commercial ou le terrain est situé dans un périmètre de sauvegarde du commerce et de l'artisanat de proximité, le vendeur (ou cédant) du fonds de commerce, du bail commercial ou du terrain remplit le formulaire Cerfa suivant : Ce formulaire est à adresser au maire de la commune concernée : Ce formulaire doit être rempli en 4 exemplaires et adressé de l'une des façons suivantes :\n- Par lettre recommandée avec AR\n- Par voie électronique\n- Par dépôt en mairie contre récépissé\n(À savoir: La déclaration préalable de cession doit obligatoirement être effectuée auprès de la mairie. En cas d'absence de déclaration préalable à la commune, la vente peut être annulée.)",
  "nb_mots": 192
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F22552 « Qu'est-ce que le droit de préemption commercial de la commune ? » (chunks 3, 4)",
   "url": "https://entreprendre.service-public.gouv.fr/vosdroits/F22552",
   "type": "service-public",
   "doc_id": "F22552",
   "chunks": [
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
 "informations_a_conserver": [
  "La commune a un droit de préemption commercial : elle peut acheter en priorité un bail commercial, un fonds de commerce, un fonds artisanal ou un terrain situé dans une zone de sauvegarde du commerce de proximité",
  "Elle peut déléguer ce droit à un EPCI dont elle fait partie, un établissement public, une société d'économie mixte, un concessionnaire d'aménagement ou le titulaire d'un contrat de redynamisation commerciale ou artisanale",
  "Dans le périmètre de sauvegarde, le vendeur remplit un formulaire Cerfa adressé au maire, en 4 exemplaires",
  "Envoi par lettre recommandée avec accusé de réception, par voie électronique ou par dépôt en mairie contre récépissé",
  "La déclaration préalable de cession à la mairie est obligatoire ; sans elle, la vente peut être annulée"
 ],
 "termes_juridiques_a_conserver": [
  "droit de préemption",
  "bail commercial",
  "fonds de commerce",
  "EPCI",
  "société d'économie mixte (SEM)",
  "déclaration préalable de cession"
 ],
 "kandel_moles_entree": 58.23,
 "version_texte": 1
}
```

## LC-509 — Langage clair (moyen, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "LC-509",
 "tache": "Langage clair",
 "difficulte": "moyen",
 "theme": "social-autonomie",
 "entree": {
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "texte": "Le retrait-gonflement des argiles est un phénomène naturel qui provoque des variations de volume du sol argileux situé sous les fondations d'une maison. En période sèche, le sol se rétracte. En période humide, il gonfle. Ces mouvements peuvent fragiliser les constructions (fissures, distorsion des portes et fenêtres, rupture de canalisations...). Pour prévenir ces risques, l’État a mis en place, à titre expérimental, l’aide RGA dans 11 départements pour :\n- Financer un diagnostic de vulnérabilité du logement\n- Accompagner les propriétaires\n- Et réaliser des travaux de prévention avant l’apparition de dommages.\nIl faut être propriétaire occupant d’une maison individuelle. Le logement doit remplir toutes les conditions suivantes :\n- Être situé dans une zone d’exposition forte au RGA\n- Être achevé depuis plus de 15 ans\n- Être non mitoyen\n- Être occupé en tant que résidence principale\n- Être couvert par une assurance habitation\n- Comporter au maximum 3 niveaux (le sous-sol et les combles aménagés pour l’habitation comptent pour chacun 1 niveau).\nEn revanche, le logement ne doit pas :\n- Avoir subi des dommages affectant sa solidité ou entravant son usage normal\n- Faire l’objet d’une demande d’indemnisation, en cours d’instruction, dans le cadre du régime d’indemnisation des catastrophes naturelles\n- Avoir été indemnisé pour un sinistre lié aux mouvements de terrain différentiels consécutifs à la sécheresse et à la réhydratation des sols, reconnu dans le cadre du régime d’indemnisation des catastrophes naturelles, soit lorsque cette indemnisation est intervenue après le 30 juin 2025 , soit lorsque cette indemnisation est intervenue entre le 1 er juillet 2015 et le 30 juin 2025 et que l'indemnisation reçue a été supérieure à 10 000 € toutes taxes comprises (TTC).",
  "nb_mots": 264
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F39682 « Aide au retrait-gonflement des argiles (RGA) pour les maisons individuelles » (chunks 2, 4)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F39682",
   "type": "service-public",
   "doc_id": "F39682",
   "chunks": [
    2,
    4
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 2,
 "informations_a_conserver": [
  "Le retrait-gonflement des argiles fait varier le volume du sol sous les fondations et peut fragiliser la maison (fissures, portes et fenêtres déformées, canalisations rompues)",
  "L'aide RGA est expérimentale, dans 11 départements : diagnostic de vulnérabilité, accompagnement et travaux de prévention avant les dommages",
  "Il faut être propriétaire occupant d'une maison individuelle, en zone d'exposition forte, achevée depuis plus de 15 ans, non mitoyenne, résidence principale, assurée, de 3 niveaux au plus (sous-sol et combles aménagés comptent chacun pour 1 niveau)",
  "Le logement ne doit pas avoir subi de dommages touchant sa solidité ou son usage normal, ni faire l'objet d'une demande d'indemnisation catastrophe naturelle en cours",
  "Exclusion en cas d'indemnisation catastrophe naturelle sécheresse versée après le 30 juin 2025, ou entre le 1er juillet 2015 et le 30 juin 2025 si elle a dépassé 10 000 € TTC"
 ],
 "termes_juridiques_a_conserver": [
  "retrait-gonflement des argiles",
  "diagnostic de vulnérabilité",
  "propriétaire occupant",
  "résidence principale",
  "régime d'indemnisation des catastrophes naturelles"
 ],
 "kandel_moles_entree": 59.23,
 "version_texte": 1
}
```

## LC-511 — Langage clair (moyen, thème `travail-emploi`)

- [ ] Relu
- Remarques :

```json
{
 "id": "LC-511",
 "tache": "Langage clair",
 "difficulte": "moyen",
 "theme": "travail-emploi",
 "entree": {
  "consigne": "Réécris ce texte en langage clair pour un usager, sans perdre d'information.",
  "texte": "Un salarié en arrêt de travail doit s'abstenir d'exercer toute activité non autorisée, sous peine d'avoir à restituer les IJ qui vous ont été versées. Si le salarié est en arrêt de travail (pour cause de maladie ou accident de travail ou maladie professionnelle ), il doit s'abstenir d'exercer toute activité non autorisée par le médecin. Si le salarié exerce plusieurs activités, le médecin doit déterminer les activités qu'il n'a pas le droit de pratiquer. Exemple: Le salarié est formateur à temps partiel et travaille également dans une société de nettoyage. Si le médecin met en arrêt le salarié pour cause d'allergie à un produit de ménage, le salarié peut néanmoins continuer son activité de formateur si le médecin l'autorise. Ainsi, si le salarié travaille à temps plein pour une seule activité et qu'il est en arrêt maladie, il ne sera pas possible de cumuler l'arrêt maladie avec une autre activité professionnelle. L'interdiction s'applique à toute activité, rémunérée ou non, même si elle est limitée et si elle a lieu pendant les heures de sortie autorisées. Même si le poste du salarié permet de télétravailler, le salarié ne peut pas continuer à travailler pendant un arrêt de travail. Mais le salarié peut le faire s'il en a été expressément autorisé par le médecin. Si le salarié exerce une activité interdite pendant l'arrêt maladie, il devra restituer les indemnités journalières versées par l'organisme de sécurité sociale : CPAM, MSA. Si l'employeur a laissé travailler le salarié alors qu'il était au courant de l'arrêt maladie, le salarié peut lui demander le versement de dommages et intérêts d'un montant correspondant aux sommes restituées à la CPAM ou à la MSA. En cas de litige, c'est le juge qui se charge d'établir si l'activité constatée lors d'un contrôle médical est tolérée ou non. Exemple: Les activités suivantes, constatées lors d'un contrôle médical, ont été considérées comme contrevenant aux obligations de l'assuré malade :\n- Activités liées au mandat de représentant du personnel\n- Travaux de peinture sur une maison\n- Réparation d'une voiture\n- Travaux de jardinage.\n(À savoir: Pendant un arrêt maladie, le salarié peut suivre une action de formation mais uniquement si elle est autorisée par le médecin et si elle est compatible avec son état de santé.)",
  "nb_mots": 369
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F18724 « Un salarié peut-il travailler pendant un arrêt de travail ? » (chunks 1)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F18724",
   "type": "service-public",
   "doc_id": "F18724",
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
 "informations_a_conserver": [
  "En arrêt de travail (maladie, accident du travail, maladie professionnelle), le salarié doit s'abstenir de toute activité non autorisée par le médecin",
  "S'il a plusieurs activités, le médecin détermine celles qui sont interdites (exemple : formateur à temps partiel autorisé à continuer malgré une allergie à un produit ménager)",
  "L'interdiction vise toute activité, rémunérée ou non, même limitée et même pendant les heures de sortie autorisées ; le télétravail n'est permis qu'avec l'autorisation expresse du médecin",
  "Une activité interdite oblige à restituer les indemnités journalières à la CPAM ou à la MSA",
  "Si l'employeur l'a laissé travailler en connaissant l'arrêt, le salarié peut lui demander des dommages et intérêts égaux aux sommes restituées",
  "En cas de litige, le juge apprécie ; exemples d'activités sanctionnées : mandat de représentant du personnel, peinture d'une maison, réparation d'une voiture, jardinage",
  "Une formation reste possible si le médecin l'autorise et si elle est compatible avec l'état de santé"
 ],
 "termes_juridiques_a_conserver": [
  "arrêt de travail",
  "accident de travail",
  "maladie professionnelle",
  "indemnités journalières",
  "dommages et intérêts",
  "CPAM",
  "MSA"
 ],
 "kandel_moles_entree": 52.36,
 "version_texte": 1
}
```

## LC-516 — Langage clair (difficile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "LC-516",
 "tache": "Langage clair",
 "difficulte": "difficile",
 "theme": "social-autonomie",
 "entree": {
  "consigne": "Réécris cet article en langage clair pour un usager, sans perdre d'information. Signale les termes juridiques que tu ne simplifies pas.",
  "texte": "Des recours sont exercés, selon le cas, par l'Etat ou le département : \n1° Contre le bénéficiaire revenu à meilleure fortune ou contre la succession du bénéficiaire ; \n2° Contre le donataire, lorsque la donation est intervenue postérieurement à la demande d'aide sociale ou dans les dix ans qui ont précédé cette demande ; \n3° Contre le légataire ;\n4° A titre subsidiaire, contre le bénéficiaire d'un contrat d'assurance-vie souscrit par le bénéficiaire de l'aide sociale, à concurrence de la fraction des primes versées après l'âge de soixante-dix ans. Quand la récupération concerne plusieurs bénéficiaires, celle-ci s'effectue au prorata des sommes versées à chacun de ceux-ci. \nEn ce qui concerne les prestations d'aide sociale à domicile, de soins de ville prévus par l'article L. 111-2 et la prise en charge du forfait journalier, les conditions dans lesquelles les recours sont exercés, en prévoyant, le cas échéant, l'existence d'un seuil de dépenses supportées par l'aide sociale, en deçà duquel il n'est pas procédé à leur recouvrement, sont fixées par voie réglementaire. \nLe recouvrement sur la succession du bénéficiaire de l'aide sociale à domicile ou de la prise en charge du forfait journalier s'exerce sur la partie de l'actif net successoral, défini selon les règles de droit commun, qui excède un seuil fixé par voie réglementaire.",
  "nb_mots": 210
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/legi, Code de l'action sociale et des familles, article L132-8 (en vigueur depuis 2015-12-30)",
   "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000031728913",
   "type": "legi",
   "code": "legi_code_de_l_action_sociale_et_des_familles",
   "articles": [
    "L132-8"
   ],
   "legiarti": "LEGIARTI000031728913",
   "note": "URL construite à partir de l'identifiant LEGIARTI (Légifrance non consulté en lecture automatique)",
   "depot": "AgentPublic/legi",
   "revision": "68b01fbbe0cdaf5fe7b8a6befe4b8acab41530f8"
  }
 ],
 "licence_source": "Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face)",
 "fictif": false,
 "version_item": 1,
 "informations_a_conserver": [
  "L'État ou le département peut exercer des recours contre le bénéficiaire revenu à meilleure fortune ou contre sa succession",
  "Recours contre le donataire si la donation a eu lieu après la demande d'aide sociale ou dans les 10 ans qui la précèdent",
  "Recours contre le légataire",
  "À titre subsidiaire, recours contre le bénéficiaire d'une assurance-vie souscrite par l'allocataire, pour les primes versées après 70 ans, au prorata entre bénéficiaires",
  "Pour l'aide sociale à domicile, les soins de ville et le forfait journalier, les conditions des recours (avec un éventuel seuil de dépenses) sont fixées par voie réglementaire",
  "Pour l'aide à domicile et le forfait journalier, la récupération sur succession ne porte que sur la part de l'actif net successoral au-dessus d'un seuil réglementaire"
 ],
 "termes_juridiques_a_conserver": [
  "revenu à meilleure fortune",
  "succession",
  "donataire",
  "légataire",
  "assurance-vie",
  "à titre subsidiaire",
  "forfait journalier",
  "actif net successoral",
  "voie réglementaire"
 ],
 "kandel_moles_entree": 59.95,
 "version_texte": 1
}
```

## LC-517 — Langage clair (difficile, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "LC-517",
 "tache": "Langage clair",
 "difficulte": "difficile",
 "theme": "etat-civil-papiers",
 "entree": {
  "consigne": "Réécris cet article en langage clair pour un usager, sans perdre d'information. Signale les termes juridiques que tu ne simplifies pas.",
  "texte": "Toute personne dont l'acte de naissance est détenu par un officier de l'état civil français peut demander à l'officier de l'état civil à changer de prénom. La demande est remise à l'officier de l'état civil du lieu de résidence ou du lieu où l'acte de naissance a été dressé. S'il s'agit d'un mineur, la demande est remise par son représentant légal. L'adjonction, la suppression ou la modification de l'ordre des prénoms peut également être demandée.\nSi l'enfant est âgé de plus de treize ans, son consentement personnel est requis.\nLa décision de changement de prénom est inscrite sur le registre de l'état civil.\nS'il estime que la demande ne revêt pas un intérêt légitime, en particulier lorsqu'elle est contraire à l'intérêt de l'enfant ou aux droits des tiers à voir protéger leur nom de famille, l'officier de l'état civil saisit sans délai le procureur de la République. Il en informe le demandeur. Si le procureur de la République s'oppose à ce changement, le demandeur, ou son représentant légal, peut alors saisir le juge aux affaires familiales.",
  "nb_mots": 176
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/legi, Code civil, article 60 (en vigueur depuis 2026-07-29)",
   "url": "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000054527338",
   "type": "legi",
   "code": "legi_code_civil",
   "articles": [
    "60"
   ],
   "legiarti": "LEGIARTI000054527338",
   "note": "URL construite à partir de l'identifiant LEGIARTI (Légifrance non consulté en lecture automatique)",
   "depot": "AgentPublic/legi",
   "revision": "68b01fbbe0cdaf5fe7b8a6befe4b8acab41530f8"
  }
 ],
 "licence_source": "Licence Ouverte / Etalab 2.0 (etalab-2.0, déclarée sur la carte du dataset Hugging Face)",
 "fictif": false,
 "version_item": 1,
 "informations_a_conserver": [
  "Toute personne dont l'acte de naissance est détenu par un officier de l'état civil français peut demander à changer de prénom",
  "La demande est déposée auprès de l'officier de l'état civil du lieu de résidence ou du lieu où l'acte de naissance a été dressé ; pour un mineur, par son représentant légal",
  "On peut aussi demander l'ajout, la suppression ou le changement d'ordre des prénoms",
  "Au-delà de 13 ans, l'enfant doit consentir personnellement ; la décision est inscrite sur le registre de l'état civil",
  "En l'absence d'intérêt légitime (notamment contraire à l'intérêt de l'enfant ou au droit des tiers sur leur nom), l'officier saisit sans délai le procureur de la République et en informe le demandeur",
  "Si le procureur s'oppose, le demandeur ou son représentant légal peut saisir le juge aux affaires familiales"
 ],
 "termes_juridiques_a_conserver": [
  "officier de l'état civil",
  "acte de naissance",
  "représentant légal",
  "intérêt légitime",
  "procureur de la République",
  "juge aux affaires familiales",
  "registre de l'état civil"
 ],
 "kandel_moles_entree": 63.79,
 "version_texte": 1
}
```

## NR-502 — Non-régression (facile, thème `non-classe`)

- [ ] Relu
- Remarques :

```json
{
 "id": "NR-502",
 "tache": "Non-régression",
 "difficulte": "facile",
 "theme": "non-classe",
 "entree": "Une mairie reçoit 360 courriers par mois ; 25 % sont des demandes d'actes d'état civil. Combien de courriers ne sont pas des demandes d'actes d'état civil ? Explique ton calcul.",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Question rédigée pour l'évaluation (raisonnement, aucune source factuelle)"
  }
 ],
 "licence_source": "Création originale du projet (contenu rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 2,
 "sous_type": "question",
 "reponse_reference": "25 % de 360 = 90 demandes d'actes d'état civil ; 360 − 90 = 270 courriers ne sont pas des demandes d'actes d'état civil (ou directement : 75 % de 360 = 270).",
 "criteres": [
  "Conclut à 270 courriers",
  "Calcul juste et expliqué : 25 % de 360 = 90 puis 360 − 90, ou directement 75 % de 360"
 ]
}
```

## NR-505 — Non-régression (moyen, thème `non-classe`)

- [ ] Relu
- Remarques :

```json
{
 "id": "NR-505",
 "tache": "Non-régression",
 "difficulte": "moyen",
 "theme": "non-classe",
 "entree": "Quels sont les échelons de la médaille d'honneur du travail, et après combien d'années de services chacun est-il accordé, dans le cas général ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F10 « Médaille d'honneur du travail »",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F10",
   "chunks": [
    5
   ],
   "extrait": "La médaille d'honneur du travail comprend 4 échelons. Ils dépendent de l'ancienneté des services effectués : - Médaille d'argent, accordée après 20 ans de services - Médaille de vermeil, accordée après 30 ans de services - Médaille d'or, accordée après 35 ans de services - Grande médaille d'or, accordée après 40 ans de services.",
   "role": "fiche de référence"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 3,
 "sous_type": "question",
 "reponse_reference": "La médaille d'honneur du travail compte 4 échelons : médaille d'argent après 20 ans de services, médaille de vermeil après 30 ans, médaille d'or après 35 ans et grande médaille d'or après 40 ans.",
 "criteres": [
  "4 échelons",
  "Argent : 20 ans",
  "Vermeil : 30 ans",
  "Or : 35 ans",
  "Grande médaille d'or : 40 ans"
 ]
}
```

## NR-509 — Non-régression (difficile, thème `non-classe`)

- [ ] Relu
- Remarques :

```json
{
 "id": "NR-509",
 "tache": "Non-régression",
 "difficulte": "difficile",
 "theme": "non-classe",
 "entree": "Un abonnement coûte 12 € par mois sans engagement, ou 120 € pour un an payé d'avance. À partir de combien de mois d'utilisation dans l'année la formule annuelle devient-elle strictement plus avantageuse ? Quelle économie fait-on avec la formule annuelle si l'on utilise le service les 12 mois ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "Question rédigée pour l'évaluation (raisonnement, aucune source factuelle)"
  }
 ],
 "licence_source": "Création originale du projet (contenu rédigé pour l'évaluation) ; pas de source tierce",
 "fictif": true,
 "version_item": 1,
 "sous_type": "question",
 "reponse_reference": "Pour n mois, la formule mensuelle coûte 12 × n € : 10 mois coûtent 120 € (égalité), 11 mois coûtent 132 €. La formule annuelle est donc strictement plus avantageuse à partir de 11 mois. Sur 12 mois : 12 × 12 = 144 €, soit une économie de 144 − 120 = 24 €.",
 "criteres": [
  "Égalité à 10 mois (120 €)",
  "Strictement plus avantageuse à partir de 11 mois",
  "Coût mensuel sur 12 mois : 144 €",
  "Économie de 24 €"
 ]
}
```

## NR-518 — Non-régression (difficile, thème `non-classe`)

- [ ] Relu
- Remarques :

```json
{
 "id": "NR-518",
 "tache": "Non-régression",
 "difficulte": "difficile",
 "theme": "non-classe",
 "entree": "Rédige un courriel de réponse à M. Perret, qui demande à emprunter la salle des fêtes le samedi 5 décembre pour un anniversaire. Informations : la salle est déjà réservée ce jour-là ; elle est libre le samedi 12 et le dimanche 13 décembre ; la réservation se fait auprès du service vie locale, au plus tard un mois avant la date. Le ton doit être courtois ; n'ajoute aucun tarif ni aucune autre information.",
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
 "reponse_reference": "Objet : Votre demande de réservation de la salle des fêtes\n\nMonsieur,\n\nNous avons bien reçu votre demande de réservation de la salle des fêtes pour le samedi 5 décembre. Malheureusement, la salle est déjà réservée ce jour-là. Elle est en revanche disponible le samedi 12 et le dimanche 13 décembre. Si l'une de ces dates vous convient, nous vous invitons à effectuer votre réservation auprès du service vie locale, au plus tard un mois avant la date choisie.\n\nNous vous prions d'agréer, Monsieur, nos salutations distinguées.\n\nLe service vie locale",
 "criteres": [
  "Refus courtois pour le samedi 5 décembre (salle déjà réservée)",
  "Propose le samedi 12 et le dimanche 13 décembre",
  "Réservation auprès du service vie locale, au plus tard un mois avant la date",
  "Délai d'un mois appliqué correctement (pas de date limite inventée erronée)",
  "Objet, formule d'appel et de politesse",
  "Aucun tarif ni information inventés",
  "Ton courtois"
 ]
}
```

## NR-521 — Non-régression (facile, thème `non-classe`)

- [ ] Relu
- Remarques :

```json
{
 "id": "NR-521",
 "tache": "Non-régression",
 "difficulte": "facile",
 "theme": "non-classe",
 "entree": "Recopie ces cinq noms dans l'ordre alphabétique, un nom par ligne, sans puce, sans numéro, sans phrase d'introduction et sans rien modifier dans les noms : Mairie annexe ; Bibliothèque ; Crèche ; Accueil de loisirs ; Gymnase.",
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
 "reponse_reference": "Accueil de loisirs\nBibliothèque\nCrèche\nGymnase\nMairie annexe",
 "criteres": [
  "Cinq lignes, un nom par ligne",
  "Ordre exact : Accueil de loisirs, Bibliothèque, Crèche, Gymnase, Mairie annexe",
  "Noms recopiés à l'identique (orthographe, accents et majuscules de la liste)",
  "Ni puce, ni numéro, ni phrase d'introduction ou de conclusion"
 ]
}
```

## NR-522 — Non-régression (moyen, thème `non-classe`)

- [ ] Relu
- Remarques :

```json
{
 "id": "NR-522",
 "tache": "Non-régression",
 "difficulte": "moyen",
 "theme": "non-classe",
 "entree": "Relève toutes les dates de ce texte, dans l'ordre où elles apparaissent, une par ligne, au format JJ/MM/AAAA, sans aucun autre texte : « Les inscriptions à l'accueil de loisirs ouvrent le 2 mars 2027 et se terminent le 19 mars 2027. Les familles seront informées des places attribuées le 26 mars 2027 ; le premier accueil aura lieu le 7 avril 2027. »",
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
 "reponse_reference": "02/03/2027\n19/03/2027\n26/03/2027\n07/04/2027",
 "criteres": [
  "Quatre dates, une par ligne, dans l'ordre du texte",
  "Format JJ/MM/AAAA, zéros compris : 02/03/2027, 19/03/2027, 26/03/2027, 07/04/2027",
  "Aucun autre texte (ni libellé, ni puce, ni phrase)"
 ]
}
```

## Q-503 — Question (moyen, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "Q-503",
 "tache": "Question",
 "difficulte": "moyen",
 "theme": "social-autonomie",
 "entree": "Une fille veut demander la mise sous tutelle de sa mère. Elle me demande quelles pièces joindre à la requête et où l'envoyer. Que lui répondre ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "AgentPublic/sp_questions_corpus (gpt_corpus-20kq&A.xlsx)",
   "depot": "AgentPublic/sp_questions_corpus",
   "revision": "495a22cf7b572621a85d2f3e97783b2f4189c47e",
   "fichier": "gpt_corpus-20kq&A.xlsx",
   "ligne": 12113,
   "role": "amorce de question usager, reformulée par un agent"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F2120 « Tutelle d'un majeur »",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F2120",
   "chunks": [
    5,
    6
   ],
   "extrait": "Il faut au préalable faire constater l’état des facultés de la personne à protéger par un médecin agréé par le procureur de la République. Le certificat médical circonstancié du médecin agréé est obligatoire sinon la demande est irrecevable. […] Le demandeur peut utiliser le formulaire de requête en vue d'une protection juridique d'un majeur pour faire sa demande. La requête doit être accompagnée des documents suivants : - Certificat médical circonstancié - Copie intégrale de l’acte de naissance de la personne à protéger - Copie (recto-verso) de la pièce d’identité de la personne à protéger - Copie (recto-verso) de la pièce d’identité de la personne qui fait la demande - Documents ou renseignements, dont le demandeur à connaissance, sur la situation personnelle et financière de la personne à protéger. La requête est transmise au juge des tutelles du tribunal de proximité ou du tribunal judiciaire du lieu de résidence de la personne à protéger.",
   "role": "fiche de référence"
  }
 ],
 "licence_source": "Amorce : corpus AgentPublic/sp_questions_corpus (Hugging Face). Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 3,
 "amorce_usager": "Quels sont les documents nécessaires pour faire une demande d'ouverture de tutelle pour une personne majeure ?",
 "reponse_reference": "La requête (un formulaire de requête en vue d'une protection juridique d'un majeur peut être utilisé) doit être accompagnée du certificat médical circonstancié d'un médecin agréé par le procureur de la République (obligatoire, sinon la demande est irrecevable), de la copie intégrale de l'acte de naissance de la personne à protéger, de la copie recto-verso de sa pièce d'identité et de celle de la personne qui fait la demande, ainsi que des documents ou renseignements connus sur la situation personnelle et financière de la personne à protéger. Elle est transmise au juge des tutelles du tribunal de proximité ou du tribunal judiciaire du lieu de résidence de la personne à protéger. Ne vaut pas avis juridique.",
 "elements_cles": [
  "Certificat médical circonstancié d'un médecin agréé par le procureur (obligatoire, sinon irrecevable)",
  "Copie intégrale de l'acte de naissance de la personne à protéger",
  "Copies recto-verso des pièces d'identité de la personne à protéger et du demandeur",
  "Documents ou renseignements sur la situation personnelle et financière de la personne à protéger",
  "Envoi au juge des tutelles du tribunal de proximité ou judiciaire du lieu de résidence de la personne à protéger"
 ],
 "sources_attendues": [
  "https://www.service-public.gouv.fr/particuliers/vosdroits/F2120"
 ],
 "sans_reponse": false,
 "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

## Q-509 — Question (facile, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "Q-509",
 "tache": "Question",
 "difficulte": "facile",
 "theme": "etat-civil-papiers",
 "entree": "Un électeur inscrit de longue date n'a pas reçu sa carte électorale à l'approche du scrutin. Quand aurait-il dû la recevoir et que peut-il faire ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F1962 « Carte électorale »",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1962",
   "chunks": [
    3
   ],
   "extrait": "La carte électorale est envoyée par courrier à votre domicile au plus tard 3 jours avant le 1 er tour de l'élection (ou référendum). Si votre carte électorale ne vous a pas été distribuée avant l'élection ou le référendum, elle est conservée au bureau de vote. Vous pourrez la récupérer en y présentant une pièce d'identité .",
   "role": "fiche de référence"
  }
 ],
 "licence_source": "Question rédigée pour l'évaluation. Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "reponse_reference": "La carte électorale est envoyée par courrier au domicile au plus tard 3 jours avant le 1er tour de l'élection ou du référendum. Si elle n'a pas été distribuée avant le scrutin, elle est conservée au bureau de vote, où l'électeur peut la récupérer en présentant une pièce d'identité. Ne vaut pas avis juridique.",
 "elements_cles": [
  "Envoi par courrier au plus tard 3 jours avant le 1er tour",
  "Carte non distribuée : conservée au bureau de vote",
  "Récupération au bureau de vote sur présentation d'une pièce d'identité"
 ],
 "sources_attendues": [
  "https://www.service-public.gouv.fr/particuliers/vosdroits/F1962"
 ],
 "sans_reponse": false,
 "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

## Q-514 — Question (difficile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "Q-514",
 "tache": "Question",
 "difficulte": "difficile",
 "theme": "collectivites",
 "entree": "Le maire veut lancer un budget participatif dans notre commune de 8 000 habitants. Quelle part du budget d'investissement la loi impose-t-elle d'y consacrer, et qui peut voter pour les projets ?",
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
 "reponse_reference": "Je ne trouve pas de fiche officielle, dans les sources dont je dispose, qui traite des budgets participatifs des communes : je ne peux donc indiquer de manière sourcée ni une part du budget qui serait imposée, ni les règles de vote. Je conseille de s'adresser au service juridique ou financier de la commune, ou à la préfecture (contrôle de légalité), avant d'arrêter le dispositif. Ne vaut pas avis juridique.",
 "elements_cles": [
  "Dit explicitement qu'aucune source disponible ne traite des budgets participatifs communaux",
  "N'invente ni pourcentage imposé du budget d'investissement, ni règle de vote (âge, résidence…)",
  "Oriente vers le service juridique ou financier de la commune ou la préfecture"
 ],
 "sources_attendues": [],
 "sans_reponse": true,
 "orientation_attendue": "Dire qu'aucune source officielle disponible ne traite des budgets participatifs, ne donner ni part de budget ni règle de vote, et orienter vers les services juridiques ou financiers de la commune ou la préfecture.",
 "mention_obligatoire": "Ne vaut pas avis juridique",
 "verification_absence": {
  "corpus": "AgentPublic/service-public (rév. 29f236f8a5)",
  "motifs_recherches_regex_insensible_casse": [
   "budget participatif",
   "budgets participatifs",
   "participatif"
  ],
  "resultat": "0 fiche pour les 2 premiers motifs ; « participatif » : 7 fiches, toutes sur le financement participatif d'entreprises ou d'artistes (F35939, F35930, F23749, F22388, F36831…), hors sujet.",
  "date": "2026-10-20"
 }
}
```

## Q-516 — Question (facile, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

```json
{
 "id": "Q-516",
 "tache": "Question",
 "difficulte": "facile",
 "theme": "famille-education-sante",
 "entree": "Un parent me demande contre quelles maladies protège le vaccin DTP et à quels âges son bébé doit obligatoirement le recevoir. Que lui répondre ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "AgentPublic/sp_questions_corpus (gpt_corpus-20kq&A.xlsx)",
   "depot": "AgentPublic/sp_questions_corpus",
   "revision": "495a22cf7b572621a85d2f3e97783b2f4189c47e",
   "fichier": "gpt_corpus-20kq&A.xlsx",
   "ligne": 1499,
   "role": "amorce de question usager, reformulée par un agent"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F704 « Vaccination : diphtérie, tétanos, poliomyélite (DTP) »",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F704",
   "chunks": [
    2
   ],
   "extrait": "La primo-vaccination (2 injections suivies d'un rappel) est obligatoire pour tous les enfants nés à compter du 1 er janvier 2018. […] 1 re injection à 2 mois (8 semaines) 2 e injection à 4 mois | À 11 mois | À 6 ans Entre 11 et 13 ans À 25 ans À 45 ans À 65 ans Puis tous les 10 ans",
   "role": "fiche de référence"
  }
 ],
 "licence_source": "Amorce : corpus AgentPublic/sp_questions_corpus (Hugging Face). Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "amorce_usager": "Quelles sont les maladies contre lesquelles le vaccin diphtérie, tétanos, poliomyélite protège ?",
 "reponse_reference": "Le vaccin DTP protège contre la diphtérie, le tétanos et la poliomyélite. Pour les enfants nés à compter du 1er janvier 2018, la primo-vaccination est obligatoire : une injection à 2 mois, une à 4 mois, puis un rappel obligatoire à 11 mois. Des rappels sont ensuite recommandés à 6 ans, entre 11 et 13 ans, à 25, 45 et 65 ans, puis tous les 10 ans. Ne vaut pas avis juridique.",
 "elements_cles": [
  "Protège contre la diphtérie, le tétanos et la poliomyélite",
  "Obligatoire pour les enfants nés depuis le 1er janvier 2018",
  "Injections à 2 mois et 4 mois, rappel obligatoire à 11 mois",
  "Rappels recommandés ensuite (6 ans, 11-13 ans, 25, 45, 65 ans, puis tous les 10 ans)"
 ],
 "sources_attendues": [
  "https://www.service-public.gouv.fr/particuliers/vosdroits/F704"
 ],
 "sans_reponse": false,
 "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

## Q-517 — Question (moyen, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

```json
{
 "id": "Q-517",
 "tache": "Question",
 "difficulte": "moyen",
 "theme": "famille-education-sante",
 "entree": "Une mère emmène son enfant de 4 ans chez un médecin généraliste de secteur 1, en métropole. Combien coûte la consultation et combien l'assurance maladie rembourse-t-elle ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "AgentPublic/sp_questions_corpus (gpt_corpus-20kq&A.xlsx)",
   "depot": "AgentPublic/sp_questions_corpus",
   "revision": "495a22cf7b572621a85d2f3e97783b2f4189c47e",
   "fichier": "gpt_corpus-20kq&A.xlsx",
   "ligne": 16250,
   "role": "amorce de question usager, reformulée par un agent"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public (rév. 29f236f8a5), fiche F10874 « Remboursement d'une consultation médicale pour un enfant de moins de 16 ans »",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F10874",
   "chunks": [
    2
   ],
   "extrait": "Le taux de remboursement ( 70 % du trarif conventionnel) est identique pour tout enfant de moins de 16 ans, avec ou sans médecin traitant identifié. […] | Secteur 1 | Moins de 6 ans | 35 € | 35 € | 24,50 € | […] (À noter: Les consultations obligatoires (8 e jour, 9 e et 24 e mois) sont au tarif de 54 € et remboursées à 100 % .)",
   "role": "fiche de référence"
  }
 ],
 "licence_source": "Amorce : corpus AgentPublic/sp_questions_corpus (Hugging Face). Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "amorce_usager": "Quelles sont les règles spécifiques de remboursement pour les consultations médicales pour un enfant de moins de 16 ans ?",
 "reponse_reference": "En métropole, le taux de remboursement est de 70 % du tarif conventionnel pour tout enfant de moins de 16 ans, avec ou sans médecin traitant. Chez un généraliste de secteur 1, pour un enfant de moins de 6 ans, la consultation coûte 35 € et l'assurance maladie rembourse 24,50 €. Les consultations obligatoires (8e jour, 9e et 24e mois) sont à 54 € et remboursées à 100 %. Ne vaut pas avis juridique.",
 "elements_cles": [
  "Taux de 70 % du tarif conventionnel pour les moins de 16 ans, avec ou sans médecin traitant",
  "Généraliste secteur 1, enfant de moins de 6 ans : tarif 35 €",
  "Montant remboursé : 24,50 €",
  "Consultations obligatoires (8e jour, 9e et 24e mois) : 54 €, remboursées à 100 %"
 ],
 "sources_attendues": [
  "https://www.service-public.gouv.fr/particuliers/vosdroits/F10874"
 ],
 "sans_reponse": false,
 "mention_obligatoire": "Ne vaut pas avis juridique"
}
```

## Q-520 — Question (difficile, thème `fiscalite-locale`)

- [ ] Relu
- Remarques :

```json
{
 "id": "Q-520",
 "tache": "Question",
 "difficulte": "difficile",
 "theme": "fiscalite-locale",
 "entree": "Un propriétaire conteste la ligne « GEMAPI » de son avis de taxe foncière. Il veut savoir à quoi elle correspond, qui en fixe le montant et s'il peut en être exonéré. Que lui répondre ?",
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
 "version_item": 2,
 "reponse_reference": "Je ne trouve pas de fiche officielle, dans les sources dont je dispose, qui traite de la taxe GEMAPI : je ne peux donc indiquer de manière sourcée ni son objet exact, ni qui en fixe le montant, ni d'éventuelles exonérations. Je conseille au propriétaire de poser la question au service des impôts indiqué sur son avis de taxe foncière. Ne vaut pas avis juridique.",
 "elements_cles": [
  "Dit explicitement qu'aucune source disponible ne traite de la taxe GEMAPI",
  "N'invente ni plafond, ni taux, ni cas d'exonération",
  "Oriente vers le service des impôts indiqué sur l'avis de taxe foncière"
 ],
 "sources_attendues": [],
 "sans_reponse": true,
 "orientation_attendue": "Dire qu'aucune source officielle disponible ne traite de la taxe GEMAPI, ne donner ni montant ni exonération, et orienter vers le service des impôts indiqué sur l'avis de taxe foncière.",
 "mention_obligatoire": "Ne vaut pas avis juridique",
 "verification_absence": {
  "corpus": "AgentPublic/service-public (rév. 29f236f8a5)",
  "motifs_recherches_regex_insensible_casse": [
   "gemapi",
   "taxe (pour la )?gestion des milieux",
   "milieux aquatiques",
   "pr[ée]vention des inondations"
  ],
  "resultat": "0 fiche pour les 2 premiers motifs ; « milieux aquatiques » : 3 fiches hors sujet (F2117 pêche, F1127 partie civile, F37901 autorisation environnementale) ; « prévention des inondations » : 1 fiche hors sujet (F38538, risques pour les entreprises).",
  "date": "2026-10-20"
 }
}
```

## RD-502 — Recherche de données (facile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RD-502",
 "tache": "Recherche de données",
 "difficulte": "facile",
 "theme": "social-autonomie",
 "entree": "Je cherche sur data.gouv.fr les données mensuelles sur les prestations de solidarité (minima sociaux, prime d'activité, aides au logement). Donne-moi le titre du jeu, son producteur et le lien.",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20T05:47:20Z",
   "source": "Serveur MCP data.gouv (search_datasets)",
   "serveur": "https://mcp.data.gouv.fr/mcp",
   "role": "échec simulé (Bac à sable MCP, cassette de panne écrite sans requête)",
   "cassette": "../../cassettes/RD-502/s1.json"
  },
  {
   "consulte_le": "2026-10-20",
   "source": "Catalogue data.gouv local (Index local v1)",
   "depot": "AgentPublic/data-gouv-datasets-catalog",
   "revision": "11f3d3c9481ad478dbcff52e85d73b7fd10533ce",
   "role": "référence de repli"
  }
 ],
 "licence_source": "Métadonnées data.gouv.fr (catalogue local AgentPublic/data-gouv-datasets-catalog).",
 "fictif": false,
 "version_item": 2,
 "appels_attendus": [
  {
   "outil": "search_datasets",
   "arguments": {
    "query": "données mensuelles prestations de solidarité",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "query": {
      "contient_un_de": [
       "prestations de solidarite",
       "prestations de solidarité",
       "solidarite",
       "solidarité"
      ],
      "optionnel": false
     }
    }
   },
   "regle": "query contient « prestations de solidarite » ou « prestations de solidarité » ou « solidarite » ou « solidarité » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres"
  }
 ],
 "cassettes": [
  "../../cassettes/RD-502/s1.json"
 ],
 "reponse_reference": {
  "jeu_principal": {
   "id": "6226330d44bec80dc83e0c4a",
   "titre": "Données mensuelles sur les prestations de solidarité",
   "producteur": "Ministère des Solidarités et de la Santé",
   "url": "https://www.data.gouv.fr/datasets/donnees-mensuelles-sur-les-prestations-de-solidarite"
  },
  "comportement_attendu": "L'Assistant signale que data.gouv.fr n'a pas répondu (délai dépassé), répond depuis le catalogue de l'Index local et précise que les informations n'ont pas été vérifiées en ligne",
  "texte": "data.gouv.fr n'a pas répondu à temps (délai dépassé) ; d'après le catalogue local, le jeu est « Données mensuelles sur les prestations de solidarité » (identifiant 6226330d44bec80dc83e0c4a), produit par le Ministère des Solidarités et de la Santé : https://www.data.gouv.fr/datasets/donnees-mensuelles-sur-les-prestations-de-solidarite (information non vérifiée en ligne)."
 },
 "mode": "repli",
 "criteres": [
  "Signale l'échec de data.gouv.fr (délai dépassé) sans le masquer",
  "Cite le jeu « Données mensuelles sur les prestations de solidarité » depuis le catalogue local et précise que l'information n'est pas vérifiée en ligne"
 ],
 "producteurs": [
  "Ministère des Solidarités et de la Santé"
 ]
}
```

## RD-509 — Recherche de données (difficile, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RD-509",
 "tache": "Recherche de données",
 "difficulte": "difficile",
 "theme": "etat-civil-papiers",
 "entree": "Combien de bureaux de vote compte la commune d'Ambérieu-en-Bugey (code commune 01004) d'après le jeu de l'Insee « Bureaux de vote et adresses de leurs électeurs », et quels sont leurs libellés ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20T05:47:37Z",
   "source": "Serveur MCP data.gouv (search_datasets, list_dataset_resources, query_resource_data)",
   "serveur": "https://mcp.data.gouv.fr/mcp",
   "role": "réponses enregistrées (Bac à sable MCP)",
   "cassette": "../../cassettes/RD-509/s1.json"
  }
 ],
 "licence_source": "Métadonnées et données data.gouv.fr (catalogue public), enregistrées le 2026-10-20.",
 "fictif": false,
 "version_item": 1,
 "appels_attendus": [
  {
   "outil": "search_datasets",
   "arguments": {
    "query": "bureaux de vote adresses électeurs",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "query": {
      "contient_un_de": [
       "bureaux de vote",
       "bureau de vote"
      ],
      "optionnel": false
     }
    }
   },
   "regle": "query contient « bureaux de vote » ou « bureau de vote » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres"
  },
  {
   "outil": "list_dataset_resources",
   "arguments": {
    "dataset_id": "649998d50f6f27459dc6cf5b"
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "dataset_id": {
      "exact": "649998d50f6f27459dc6cf5b",
      "optionnel": false
     }
    }
   },
   "regle": "dataset_id exact de « Bureaux de vote et adresses de leurs électeurs »"
  },
  {
   "outil": "query_resource_data",
   "arguments": {
    "resource_id": "3a321a06-9e05-4de9-8dd3-421da6abd4c5",
    "filter_column": "code_commune",
    "filter_value": "01004",
    "filter_operator": "exact",
    "page_size": 20
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "resource_id": {
      "exact": "3a321a06-9e05-4de9-8dd3-421da6abd4c5",
      "optionnel": false
     },
     "filter_column": {
      "exact": "code_commune",
      "optionnel": false
     },
     "filter_value": {
      "exact": "01004",
      "optionnel": false
     },
     "filter_operator": {
      "exact": "exact",
      "optionnel": true
     }
    }
   },
   "regle": "resource_id exact de table-bv-reu.csv, filtre exact sur « code_commune » = 01004 ; page_size libre"
  }
 ],
 "cassettes": [
  "../../cassettes/RD-509/s1.json"
 ],
 "reponse_reference": {
  "jeu_principal": {
   "id": "649998d50f6f27459dc6cf5b",
   "titre": "Bureaux de vote et adresses de leurs électeurs",
   "producteur": "Institut national de la statistique et des études économiques (Insee)",
   "url": "https://www.data.gouv.fr/datasets/bureaux-de-vote-et-adresses-de-leurs-electeurs"
  },
  "texte": "D'après « Bureaux de vote et adresses de leurs électeurs » (identifiant 649998d50f6f27459dc6cf5b), publié par Institut national de la statistique et des études économiques (Insee) : https://www.data.gouv.fr/datasets/bureaux-de-vote-et-adresses-de-leurs-electeurs, fichier table-bv-reu.csv filtré sur code_commune = 01004 : 8 bureaux de vote — b1 espace 1500, b2 espace 1500, b3 chateau des echelles, b4 espace 1500, b5 espace 1500, b6 groupe scolaire jules ferry, b7 ecole maternelle de tiret, b8 ecole maternelle de tiret."
 },
 "valeurs_attendues": {
  "ressource_id": "3a321a06-9e05-4de9-8dd3-421da6abd4c5",
  "filtre": {
   "colonne": "code_commune",
   "operateur": "exact",
   "valeur": "01004"
  },
  "total_lignes": 8,
  "lignes": [
   {
    "code": "1",
    "libelle_reu": "b1 espace 1500"
   },
   {
    "code": "2",
    "libelle_reu": "b2 espace 1500"
   },
   {
    "code": "3",
    "libelle_reu": "b3 chateau des echelles"
   },
   {
    "code": "4",
    "libelle_reu": "b4 espace 1500"
   },
   {
    "code": "5",
    "libelle_reu": "b5 espace 1500"
   },
   {
    "code": "6",
    "libelle_reu": "b6 groupe scolaire jules ferry"
   },
   {
    "code": "7",
    "libelle_reu": "b7 ecole maternelle de tiret"
   },
   {
    "code": "8",
    "libelle_reu": "b8 ecole maternelle de tiret"
   }
  ],
  "colonnes": [
   "code",
   "libelle_reu"
  ]
 },
 "mode": "connecte",
 "criteres": [
  "Donne 8 bureaux de vote pour Ambérieu-en-Bugey, sans en inventer",
  "Cite les libellés des bureaux tels que dans le fichier (espace 1500, château des Échelles, groupe scolaire Jules Ferry, école maternelle de Tiret)"
 ],
 "producteurs": [
  "Institut national de la statistique et des études économiques (Insee)"
 ]
}
```

## RD-515 — Recherche de données (difficile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RD-515",
 "tache": "Recherche de données",
 "difficulte": "difficile",
 "theme": "collectivites",
 "entree": "D'après le jeu « Pari-scores des communes françaises (élections municipales 2020) » sur data.gouv.fr, quelle est la population totale de Rennes (code 35238), la taille de la liste municipale et le pari-score attribué à la commune ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20T05:47:50Z",
   "source": "Serveur MCP data.gouv (search_datasets, list_dataset_resources, query_resource_data)",
   "serveur": "https://mcp.data.gouv.fr/mcp",
   "role": "réponses enregistrées (Bac à sable MCP)",
   "cassette": "../../cassettes/RD-515/s1.json"
  }
 ],
 "licence_source": "Métadonnées et données data.gouv.fr (catalogue public), enregistrées le 2026-10-20.",
 "fictif": false,
 "version_item": 1,
 "appels_attendus": [
  {
   "outil": "search_datasets",
   "arguments": {
    "query": "pari-score communes élections municipales 2020",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "query": {
      "contient_un_de": [
       "pari-score",
       "pari score",
       "pariscore",
       "pari-scores"
      ],
      "optionnel": false
     }
    }
   },
   "regle": "query contient « pari-score » ou « pari score » ou « pariscore » ou « pari-scores » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres"
  },
  {
   "outil": "list_dataset_resources",
   "arguments": {
    "dataset_id": "69baa78ffb29d1c59d89b45f"
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "dataset_id": {
      "exact": "69baa78ffb29d1c59d89b45f",
      "optionnel": false
     }
    }
   },
   "regle": "dataset_id exact de « Pari-scores des communes françaises (élections municipales 2020) »"
  },
  {
   "outil": "query_resource_data",
   "arguments": {
    "resource_id": "82f21052-a189-4406-bd96-297bbdf1d52c",
    "filter_column": "code_circo",
    "filter_value": "35238",
    "filter_operator": "exact",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "resource_id": {
      "exact": "82f21052-a189-4406-bd96-297bbdf1d52c",
      "optionnel": false
     },
     "filter_column": {
      "exact": "code_circo",
      "optionnel": false
     },
     "filter_value": {
      "exact": "35238",
      "optionnel": false
     },
     "filter_operator": {
      "exact": "exact",
      "optionnel": true
     }
    }
   },
   "regle": "resource_id exact de pariscore-muni-2020.csv, filtre exact sur « code_circo » = 35238 ; page_size libre"
  }
 ],
 "cassettes": [
  "../../cassettes/RD-515/s1.json"
 ],
 "reponse_reference": {
  "jeu_principal": {
   "id": "69baa78ffb29d1c59d89b45f",
   "titre": "Pari-scores des communes françaises (élections municipales 2020)",
   "producteur": "Démocratiser la politique",
   "url": "https://www.data.gouv.fr/datasets/pari-scores-des-communes-francaises-elections-municipales-2020"
  },
  "texte": "D'après « Pari-scores des communes françaises (élections municipales 2020) » (identifiant 69baa78ffb29d1c59d89b45f), publié par Démocratiser la politique : https://www.data.gouv.fr/datasets/pari-scores-des-communes-francaises-elections-municipales-2020, fichier pariscore-muni-2020.csv filtré sur code_circo = 35238 (1 ligne) : Rennes, population_totale = 216815, taille_liste = 61, pariscore = F- (type de commune : Grands centres urbains)."
 },
 "valeurs_attendues": {
  "ressource_id": "82f21052-a189-4406-bd96-297bbdf1d52c",
  "filtre": {
   "colonne": "code_circo",
   "operateur": "exact",
   "valeur": "35238"
  },
  "total_lignes": 1,
  "lignes": [
   {
    "nom": "Rennes",
    "population_totale": "216815",
    "taille_liste": "61",
    "pariscore": "F-"
   }
  ],
  "colonnes": [
   "population_totale",
   "taille_liste",
   "pariscore"
  ]
 },
 "mode": "connecte",
 "criteres": [
  "Donne population totale 216 815, taille de liste 61 et pari-score F-, sans valeur inventée",
  "Filtre sur le code 35238 (Rennes) dans la ressource CSV, pas dans la note PDF"
 ],
 "producteurs": [
  "Démocratiser la politique"
 ]
}
```

## RD-517 — Recherche de données (moyen, thème `famille-education-sante`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RD-517",
 "tache": "Recherche de données",
 "difficulte": "moyen",
 "theme": "famille-education-sante",
 "entree": "Pour une carte des crèches, je veux le fichier CSV des établissements d'accueil des jeunes enfants publié par le Conseil départemental de la Mayenne sur data.gouv.fr. Donne le nom du fichier CSV et son lien.",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20T05:47:55Z",
   "source": "Serveur MCP data.gouv (search_datasets, list_dataset_resources)",
   "serveur": "https://mcp.data.gouv.fr/mcp",
   "role": "réponses enregistrées (Bac à sable MCP)",
   "cassette": "../../cassettes/RD-517/s1.json"
  }
 ],
 "licence_source": "Métadonnées et données data.gouv.fr (catalogue public), enregistrées le 2026-10-20.",
 "fictif": false,
 "version_item": 1,
 "appels_attendus": [
  {
   "outil": "search_datasets",
   "arguments": {
    "query": "établissements d'accueil des jeunes enfants Mayenne",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "query": {
      "contient_un_de": [
       "accueil des jeunes enfants",
       "jeunes enfants",
       "petite enfance",
       "creches",
       "crèches",
       "mayenne"
      ],
      "optionnel": false
     }
    }
   },
   "regle": "query contient « accueil des jeunes enfants » ou « jeunes enfants » ou « petite enfance » ou « creches » ou « crèches » ou « mayenne » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres"
  },
  {
   "outil": "list_dataset_resources",
   "arguments": {
    "dataset_id": "64a51dd12129cd19d5c92212"
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "dataset_id": {
      "exact": "64a51dd12129cd19d5c92212",
      "optionnel": false
     }
    }
   },
   "regle": "dataset_id exact de « Etablissements d'accueil des jeunes enfants en Mayenne »"
  }
 ],
 "cassettes": [
  "../../cassettes/RD-517/s1.json"
 ],
 "reponse_reference": {
  "jeu_principal": {
   "id": "64a51dd12129cd19d5c92212",
   "titre": "Etablissements d'accueil des jeunes enfants en Mayenne",
   "producteur": "Le Conseil Départemental de la Mayenne",
   "url": "https://www.data.gouv.fr/datasets/etablissements-daccueil-des-jeunes-enfants-en-mayenne"
  },
  "texte": "Dans « Etablissements d'accueil des jeunes enfants en Mayenne » (identifiant 64a51dd12129cd19d5c92212), publié par Le Conseil Départemental de la Mayenne : https://www.data.gouv.fr/datasets/etablissements-daccueil-des-jeunes-enfants-en-mayenne, le fichier CSV est 225300011_mayenne_etablissement_accueil_petite_enfance.csv (ressource bb2c7d98-bdac-485a-8f45-0df7d8427baa) : https://data.lamayenne.fr/api/explore/v2.1/catalog/datasets/225300011_mayenne_etablissement_accueil_petite_enfance/exports/csv?use_labels=true. Le jeu propose aussi d'autres formats (JSON, GeoJSON, shapefile…)."
 },
 "mode": "connecte",
 "criteres": [
  "Donne le fichier 225300011_mayenne_etablissement_accueil_petite_enfance.csv et son lien data.lamayenne.fr",
  "Ne choisit pas un format non CSV (JSON, GeoJSON…) comme réponse principale"
 ],
 "producteurs": [
  "Le Conseil Départemental de la Mayenne"
 ]
}
```

## RD-520 — Recherche de données (moyen, thème `fiscalite-locale`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RD-520",
 "tache": "Recherche de données",
 "difficulte": "moyen",
 "theme": "fiscalite-locale",
 "entree": "La Région Île-de-France publie sur data.gouv.fr la liste des communes franciliennes selon le zonage de la taxe sur les logements vacants (TLV). Quel est l'article du code général des impôts cité, en quelles catégories le zonage classe-t-il les communes, et de quand date la dernière mise à jour ?",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20T05:48:01Z",
   "source": "Serveur MCP data.gouv (search_datasets, get_dataset_info)",
   "serveur": "https://mcp.data.gouv.fr/mcp",
   "role": "réponses enregistrées (Bac à sable MCP)",
   "cassette": "../../cassettes/RD-520/s1.json"
  }
 ],
 "licence_source": "Métadonnées et données data.gouv.fr (catalogue public), enregistrées le 2026-10-20.",
 "fictif": false,
 "version_item": 1,
 "appels_attendus": [
  {
   "outil": "search_datasets",
   "arguments": {
    "query": "zonage TLV communes franciliennes",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "query": {
      "contient_un_de": [
       "tlv",
       "logements vacants",
       "zonage"
      ],
      "optionnel": false
     }
    }
   },
   "regle": "query contient « tlv » ou « logements vacants » ou « zonage » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres"
  },
  {
   "outil": "get_dataset_info",
   "arguments": {
    "dataset_id": "6a34bf96a2c3822723467387"
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "dataset_id": {
      "exact": "6a34bf96a2c3822723467387",
      "optionnel": false
     }
    }
   },
   "regle": "dataset_id exact de « Liste des communes franciliennes selon le zonage TLV »"
  }
 ],
 "cassettes": [
  "../../cassettes/RD-520/s1.json"
 ],
 "reponse_reference": {
  "jeu_principal": {
   "id": "6a34bf96a2c3822723467387",
   "titre": "Liste des communes franciliennes selon le zonage TLV",
   "producteur": "Région Île-de-France",
   "url": "https://www.data.gouv.fr/datasets/liste-des-communes-franciliennes-selon-le-zonage-tlv"
  },
  "texte": "Le jeu est « Liste des communes franciliennes selon le zonage TLV » (identifiant 6a34bf96a2c3822723467387), publié par Région Île-de-France : https://www.data.gouv.fr/datasets/liste-des-communes-franciliennes-selon-le-zonage-tlv. Sa description cite l'article 232 du code général des impôts ; le zonage TLV, créé en 2013 et refondu le 25 août 2023, classe les communes en deux catégories : tendues et non tendues. Dernière mise à jour : 18 juin 2026 ; licence lov2."
 },
 "mode": "connecte",
 "criteres": [
  "Cite l'article 232 du code général des impôts",
  "Deux catégories : communes tendues et non tendues",
  "Dernière mise à jour du 18 juin 2026, sans date inventée"
 ],
 "producteurs": [
  "Région Île-de-France"
 ]
}
```

## RD-521 — Recherche de données (facile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RD-521",
 "tache": "Recherche de données",
 "difficulte": "facile",
 "theme": "social-autonomie",
 "entree": "Pour une note sur les retraités aux faibles ressources, je cherche sur data.gouv.fr le jeu de données sur les bénéficiaires du minimum vieillesse (allocation de solidarité aux personnes âgées). Donne-moi son titre, son producteur et le lien.",
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20T14:15:32Z",
   "source": "Serveur MCP data.gouv (search_datasets)",
   "serveur": "https://mcp.data.gouv.fr/mcp",
   "role": "réponses enregistrées (Bac à sable MCP)",
   "cassette": "../../cassettes/RD-521/s1.json",
   "extrait": "1. Bénéficiaires du minimum vieillesse ID: 5369963ca3a729239d20493a Organization: Ministère des Solidarités et de la Santé […] URL: https://www.data.gouv.fr/datasets/http-www-drees-sante-gouv-fr-donnees-relatives-au-minimum-vieillesse-10467-html"
  }
 ],
 "licence_source": "Métadonnées et données data.gouv.fr (catalogue public), enregistrées le 2026-10-20.",
 "fictif": false,
 "version_item": 1,
 "appels_attendus": [
  {
   "outil": "search_datasets",
   "arguments": {
    "query": "allocation de solidarité aux personnes âgées minimum vieillesse",
    "page_size": 5
   },
   "regles": {
    "optionnel": false,
    "ordre_libre": false,
    "arguments": {
     "query": {
      "contient_un_de": [
       "minimum vieillesse",
       "aspa",
       "allocation de solidarite",
       "allocation de solidarité"
      ],
      "optionnel": false
     }
    }
   },
   "regle": "query contient « minimum vieillesse » ou « aspa » ou « allocation de solidarite » ou « allocation de solidarité » (après normalisation (casse, ponctuation), en début de mot ; variantes accentuée et non accentuée admises) ; autres paramètres libres"
  }
 ],
 "cassettes": [
  "../../cassettes/RD-521/s1.json"
 ],
 "reponse_reference": {
  "jeu_principal": {
   "id": "5369963ca3a729239d20493a",
   "titre": "Bénéficiaires du minimum vieillesse",
   "producteur": "Ministère des Solidarités et de la Santé",
   "url": "https://www.data.gouv.fr/datasets/http-www-drees-sante-gouv-fr-donnees-relatives-au-minimum-vieillesse-10467-html"
  },
  "texte": "Le jeu est « Bénéficiaires du minimum vieillesse » (identifiant 5369963ca3a729239d20493a), publié par Ministère des Solidarités et de la Santé : https://www.data.gouv.fr/datasets/http-www-drees-sante-gouv-fr-donnees-relatives-au-minimum-vieillesse-10467-html."
 },
 "mode": "connecte",
 "criteres": [
  "Cite le jeu « Bénéficiaires du minimum vieillesse » (identifiant 5369963ca3a729239d20493a)",
  "Donne le producteur (Ministère des Solidarités et de la Santé) et le lien data.gouv.fr",
  "Ne retient pas l'un des jeux « Allocataires des minima sociaux »"
 ],
 "producteurs": [
  "Ministère des Solidarités et de la Santé"
 ]
}
```

## RE-502 — Résumé (facile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RE-502",
 "tache": "Résumé",
 "difficulte": "facile",
 "theme": "social-autonomie",
 "entree": {
  "consigne": "Résume ce document en 200 mots au plus, pour un propriétaire dont la maison est squattée, reçu en mairie : ce qu'est un squat, les sanctions et la procédure d'évacuation.",
  "document": "Squatter un lieu d’habitation est le fait d'entrer dans un domicile par effraction , tromperie, menace ou violence, pour l'occuper sans autorisation du propriétaire. Il peut aussi s’agir de réserver un meublé de tourisme et d’y rester malgré la fin de la location. Il est interdit de forcer par soi-même les squatteurs à quitter les lieux : vous devez engager des démarches pour obtenir leur expulsion ou évacuation forcée. Nous vous expliquons comment faire. (Attention: Le locataire qui se maintient dans le logement après la fin du bail et sans l'accord du propriétaire, la personne qui refuse de quitter le logement après y avoir été hébergée par la personne qui y vit, le sous-locataire qui se maintient dans le logement après la fin du contrat de sous-location non autorisé par le propriétaire ne sont pas considérés comme squatteurs .)\nNous vous présentons les 2 cas de figure : entrée par effraction (ou menace ou contrainte) et maintien dans un meublé de tourisme.\nLe fait de squatter une résidence principale ou une résidence secondaire meublée est puni :\n- Pour être entré dans le logement, de 3 ans d'emprisonnement et de 45 000 € d'amende\n- Et, pour avoir occupé ce logement, de 3 ans d'emprisonnement et de 45 000 € d'amende.\nLe fait de dégrader le logement est puni de 2 ans d'emprisonnement et de 30 000 € d'amende. (À savoir: En cas de squat, la trêve hivernale ne s'applique pas. L’expulsion ou l’évacuation forcée du squatteur peut avoir lieu quelle que soit la période de l'année.)\nPour obtenir l’expulsion ou l’évacuation forcée du squatteur, 2 types de démarches sont possibles : la procédure accélérée ou, sinon, la procédure devant le juge.\nCas Procédure accélérée: La personne dont le domicile est squatté (locataire ou propriétaire occupant) ou une personne agissant pour son compte ou le propriétaire du logement squatté peut demander l'évacuation forcée des squatteurs. Pour cela, le demandeur doit d’abord : \n- Porter plainte pour violation de domicile au commissariat de police ou à la gendarmerie\n- Prouver que le logement est son domicile ou sa propriété , par exemple à l'aide de factures, de documents fiscaux, d'une attestation fournie par un voisin\n- Faire constater par un officier de police judiciaire ou par le maire ou par un commissaire de justice (anciennement huissier de justice), que le logement est squatté (introduction par manoeuvres, menaces, voies de fait ou contrainte, et maintien dans les lieux).\n Avant de lancer la procédure : \n- Il est possible de prendre conseil gratuitement auprès d'un avocat .\n- Il est possible de contacter un commissaire de justice pour qu'il donne des conseils et aide dans cette procédure. Ses honoraires sont libres et sont à la charge du demandeur. Il doit lui remettre un devis personnalisé avant d'intervenir.\n (À savoir: Si le propriétaire ne peut pas prouver son droit de propriété du fait qu'il n'a plus accès à son logement, le préfet de département, dans un délai de 72 heures, demande à l'administration fiscale de lui indiquer à qui appartient le logement squatté.)\n Ensuite , le demandeur doit s’adresser au préfet de département pour que celui-ci mette en demeure les squatteurs de quitter le logement. Le demandeur peut charger un avocat de rédiger la demande au préfet de département. Le préfet de département prend sa décision en tenant compte de la situation personnelle et familiale du squatteur. Il doit rendre sa décision dans un délai de 48 heures, à partir de la réception de la demande. (À savoir: En cas de refus, le préfet de département doit indiquer le motif de ce refus.)\n La mise en demeure indique le délai dans lequel les squatteurs ont l’obligation de quitter le logement. Dans le cas d’un domicile squatté, le délai est d’au moins 24 heures, mais dans les autres cas, le délai est de 7 jours minimum. La mise en demeure est : \n- notifiée aux squatteurs,\n- affichée en mairie et sur l'immeuble concerné,\n- notifiée au demandeur (facultatif).\n Si les squatteurs ne libèrent pas les lieux dans le délai prévu, le préfet de département doit faire évacuer le logement sans délai par la force publique, sauf si le demandeur s'y est opposé. (Rappel: Dans le cas de squatteurs, la trêve hivernale ne s'applique pas. Leur évacuation forcée peut avoir lieu tout au long de l'année.)",
  "nb_mots": 696
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F35254 « Que faire quand des squatteurs occupent un logement ? » (chunks 1, 2)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F35254",
   "type": "service-public",
   "doc_id": "F35254",
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
 "version_item": 2,
 "points_cles_reference": [
  "Squatter, c'est entrer dans un domicile par effraction, tromperie, menace ou violence (ou rester dans un meublé de tourisme après la location) ; il est interdit d'expulser soi-même",
  "Ne sont pas des squatteurs : le locataire en fin de bail, l'ancien hébergé, le sous-locataire non autorisé qui se maintiennent",
  "Sanctions : 3 ans de prison et 45 000 € pour l'entrée, autant pour l'occupation ; 2 ans et 30 000 € pour les dégradations ; pas de trêve hivernale",
  "Procédure accélérée : plainte pour violation de domicile, preuve du domicile ou de la propriété, constat (OPJ, maire ou commissaire de justice), puis demande au préfet",
  "Le préfet décide sous 48 heures et met en demeure de partir (au moins 24 heures pour un domicile, 7 jours sinon), puis fait évacuer par la force publique"
 ],
 "longueur_demandee": "moyenne"
}
```

## RE-503 — Résumé (facile, thème `etat-civil-papiers`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RE-503",
 "tache": "Résumé",
 "difficulte": "facile",
 "theme": "etat-civil-papiers",
 "entree": {
  "consigne": "Résume ce document en 80 mots au plus, pour un agent d'accueil de mairie qui renseigne les jeunes sur le recensement.",
  "document": "À partir de 16 ans, vous devez faire votre votre recensement citoyen (parfois appelé par erreur recensement militaire ). Votre recensement citoyen fait, une attestation de recensement vous est remise. Pour vous inscrire avant vos 18 ans à certains examens (BEP, baccalauréat, permis de conduire...) ou concours administratifs français, vous devez présenter votre attestation de recensement. Nous vous expliquons. Les règles sont différentes selon que vous avez fait votre recensement citoyen en France ou depuis l'étranger :\n\nVoici une liste de différentes questions ou thématiques relatives à ce sujet :\n- Comment obtenir l'attestation de recensement citoyen ?\n- Que faire en cas de perte ou de vol de l'attestation de recensement ?\n- Faut-il l'attestation de recensement pour s'inscrire à un concours ou examen (BEP, bac...) ?\n- Comment obtenir l'attestation du recensement citoyen fait depuis l'étranger ?\n- Que faire en cas de perte ou vol de l'attestation de recensement fait depuis l’étranger ?\nL'attestation de recensement vous sert à prouver que vous avez fait votre recensement citoyen.\nLes règles sont différentes selon que vous avez fait le recensement citoyen en ligne, ou en mairie :\nCas Recensement en ligne: Votre attestation de recensement peut : \n- Soit se trouver dans le porte-document de votre compte personnel en ligne\n- Soit vous être envoyée par la mairie, par courrier et dans les 10 jours\n- Soit vous être remise par la mairie.\nCas Recensement en mairie: La mairie vous remet votre attestation de recensement le jour-même de votre recensement citoyen.\nLes règles sont différentes selon votre âge :\nCas Avant l’âge de 25 ans: Vous pouvez demander une attestation de situation administrative à votre CSNJ . Vous pouvez la demander : \n- Soit par mail, avec une copie de votre carte d'identité ou de votre passeport (en cours de validité)\n- Soit par courrier, avec une copie de votre carte d'identité ou de votre passeport (en cours de validité).\nCas À partir de 25 ans: Vous ne pouvez pas obtenir de document en remplacement de votre attestation de recensement.\nPour vous inscrire à un examen (BEP, baccalauréat...) ou concours administratif français, vous devez fournir soit un justificatif de votre recensement citoyen, soit un justificatif de votre Journée défense et citoyenneté (JDC). Tout dépend de votre âge :\nCas Avant 18 ans: Vous devez présenter 1 des justificatifs suivants : \n- Attestation de recensement\n- Certificat individuel de participation à la JDC ,\n- Attestation individuelle d'exemption à la JDC\n- Attestation de situation administrative (délivrée sur demande en cas de détérioration, perte ou vol de votre attestation de recensement, ou de certificat de JDC, ou de votre attestation d'exemption de la JDC).\nCas De 18 à 24 ans: Vous devez présenter 1 des justificatifs suivants : \n- Certificat individuel de participation à la JDC\n- Attestation individuelle d'exemption à la JDC\n- Attestation de situation administrative (délivrée sur demande en cas de perte ou de vol de certificat ou attestation d'exemption de la JDC)\n- Attestation provisoire \"instance de convocation\" (en cas d'attente de convocation à la JDC).\nCas À partir de 25 ans: Vous n'avez pas à fournir de justificatif.\nL'attestation de recensement vous sert à prouver que vous avez fait votre recensement citoyen. À la suite du recensement citoyen fait depuis l'étranger, votre ambassade ou votre autorité consulaire vous remet une attestation de recensement.\nLes règles sont différentes selon votre âge :\nCas Moins de 25 ans: Vous pouvez demander une attestation de situation administrative au CSNJ de Perpignan. Vous pouvez la demander : \n- Soit par mail, avec une copie votre carte d'identité valide ou de votre passeport (en cours de validité)\n- Soit par courrier, avec une copie de votre carte d'identité valide ou de votre passeport (en cours de validité).\nCas 25 ans ou plus: Vous ne pouvez pas obtenir de document en remplacement de votre attestation de recensement.",
  "nb_mots": 607
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F1844 « Recensement citoyen : comment prouver la régularité de sa situation ? » (chunks 1, 2, 3, 4, 5, 6, 7)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1844",
   "type": "service-public",
   "doc_id": "F1844",
   "chunks": [
    1,
    2,
    3,
    4,
    5,
    6,
    7
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 2,
 "points_cles_reference": [
  "Dès 16 ans, le recensement citoyen est obligatoire et donne lieu à une attestation (remise en mairie le jour même, ou en ligne / par courrier sous 10 jours si recensement en ligne)",
  "Avant 18 ans, un justificatif (attestation de recensement, certificat ou exemption de JDC, attestation de situation administrative) est exigé pour s'inscrire aux examens et concours",
  "En cas de perte ou de vol avant 25 ans, on demande une attestation de situation administrative au CSNJ par mail ou courrier avec une copie d'une pièce d'identité valide",
  "À partir de 25 ans, aucun document de remplacement ni justificatif n'est nécessaire ; depuis l'étranger, l'attestation est remise par l'ambassade ou le consulat"
 ],
 "longueur_demandee": "courte"
}
```

## RE-509 — Résumé (moyen, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RE-509",
 "tache": "Résumé",
 "difficulte": "moyen",
 "theme": "social-autonomie",
 "entree": {
  "consigne": "Fais un résumé détaillé de ce document, en 400 mots au plus, pour le conseil syndical d'une copropriété construite avant l'interdiction de l'amiante.",
  "document": "Voici une liste de différentes questions ou thématiques relatives à ce sujet :\n- Quels sont les immeubles pouvant être concernés par la présence d'amiante ?\n- Qui prend l'initiative de faire réaliser les vérifications de la présence d'amiante dans l'immeuble ?\n- Qui doit réaliser les vérifications de la présence d'amiante dans l'immeuble ?\n- Comment sont réalisées les vérifications de la présence d'amiante dans l'immeuble ?\n- Quelles sont les actions à mettre en œuvre en fonction des résultats du repérage d'amiante dans l'immeuble ?\n- Qui doit réaliser le retrait et le confinement des matériaux et produits amiantés ?\n- Comment sont informés les occupants d'un immeuble contenant de l'amiante ?\n- Quelles sont les obligations liées au repérage d'amiante en cas de démolition d'un immeuble  ?\n- Quelles sont les sanctions en l'absence de vérification de la présence d'amiante dans l'immeuble ?\nLe diagnostiqueur doit rechercher la présence d'amiante dans certains matériaux et produits énumérés dans des listes (A et B). Pour la liste A, il s'agit des matériaux et produits suivants :\n- Flocages (revêtement présentant un aspect fibreux)\n- Calorifugeages (revêtement servant d'isolant thermique)\n- Faux plafonds (revêtement généralement constitué d'une armature suspendue et d'un remplissage de panneaux légers).\nPour la liste B, il s'agit des matériaux et produits suivants :\n- Parois verticales intérieures (murs et cloisons en dur et poteaux périphériques et intérieurs, cloisons légères et préfabriquées)\n- Planchers et plafonds (y compris poutres et charpentes, gaines et coffres)\n- Conduits, canalisations et équipements intérieurs (conduits de fluides air, eau, autres fluides..., clapets/volets coupe-feu, portes coupe-feu, vide-ordures)\n- Éléments extérieurs (bardages et façades légères, conduits en toiture et façade).\nDes précisions sont à connaître concernant la nature des matériaux et produits de la liste A et B à vérifier. Dans les parties communes de l'immeuble, ce sont les matériaux et produits mentionnés sur les listes A et B qui doivent faire l'objet d'une vérification. Dans les parties privatives, ce sont uniquement ceux mentionnés sur la liste A. Après les vérifications, le diagnostiqueur réalise un rapport. Ce rapport est transmis au propriétaire de l'immeuble ou au syndicat des copropriétaires par lettre recommandée avec avis de réception. (À savoir: En cas de préconisation de travaux de confinement ou de retrait d'amiante, le diagnostiqueur doit transmettre une copie de son rapport au préfet du département du lieu de situation de l'immeuble.)\n\nCas Cas général: \nCas À Paris:\nLes actions diffèrent selon la liste des matériaux et produits vérifiés (liste A et B).\nCas Liste A: Selon les résultats du repérage, il y a 3 niveaux d'action : \n- Niveau 1 Le propriétaire ou le syndicat des copropriétaires doit faire réaliser par un diagnostiqueur une surveillance de l'état des matériaux ou produits tous les 3 ans , car ils peuvent se dégrader.\n- Niveau 2 Le propriétaire ou le syndicat des copropriétaires doit faire réaliser une mesure de la concentration en fibres d'amiante dans l'air par un organisme accrédité par le Cofrac . Lorsque le niveau mesuré est supérieur à 5 fibres par litre dans l'air , des travaux doivent être engagés.\n- Niveau 3 Le propriétaire ou le syndicat des copropriétaires doit faire réaliser des travaux de retrait ou de confinement des matériaux amiantés. Ces travaux doivent être terminés dans les 3 ans à partir de la date de la réception du diagnostic. Dans l'attente des travaux, des mesures conservatoires doivent être mises en œuvre dans un délai de 2 mois pour assurer un niveau d'empoussièrement inférieur ou égal à 5 fibres par litre dans l'air. Ces mesures conservatoires peuvent être par exemple l'isolation de la zone contaminée, la pose d'une bâche sur le matériaux amianté pour empêcher les fibres de se disperser dans l'air.\n (Attention: En cas de niveau 3 , le propriétaire ou le syndicat des copropriétaires doit transmettre au préfet du département, dans un délai de 2 mois , les mesures conservatoires mises en œuvre dans l'attente des travaux définitifs. Par ailleurs, dans les 12 mois , le propriétaire ou le syndicat des copropriétaires doit également lui transmettre le calendrier des travaux définitifs à réaliser.)\nCas Liste B: Selon les résultats du repérage, il y a 3 niveaux d'action : \n- Niveau 1 Le propriétaire ou le syndicat des copropriétaires doit faire réaliser une évaluation périodique lorsque les matériaux ou produits contenant de l'amiante, la nature et l'étendue des dégradations ne conduisent pas à conclure à la nécessité d'une action de protection immédiate.\n- Niveau 2 Le propriétaire ou le syndicat des copropriétaires doit faire réaliser une action corrective de 1 er niveau lorsque le repérage des matériaux et produits contenant de l'amiante conclut à la nécessité d'une action de remise en état limitée au remplacement, au recouvrement ou à la protection des seuls éléments dégradés.\n- Niveau 3 Le propriétaire ou le syndicat des copropriétaires doit mettre en place une action corrective de 2 nd niveau sur l'ensemble d'une zone déterminée pour que les matériaux ou produits ne soient plus soumis à aucune agression ni dégradation.",
  "nb_mots": 793
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F288 « Habitat contenant de l'amiante » (chunks 1, 5, 6)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F288",
   "type": "service-public",
   "doc_id": "F288",
   "chunks": [
    1,
    5,
    6
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 1,
 "points_cles_reference": [
  "Le diagnostiqueur recherche l'amiante dans les matériaux de la liste A (flocages, calorifugeages, faux plafonds) et de la liste B (parois, planchers, conduits, éléments extérieurs)",
  "Parties communes : listes A et B ; parties privatives : liste A seulement",
  "Le rapport est envoyé en recommandé au propriétaire ou au syndicat des copropriétaires, et au préfet en cas de travaux de retrait ou de confinement préconisés",
  "Liste A, niveau 1 : surveillance de l'état des matériaux tous les 3 ans",
  "Liste A, niveau 2 : mesure de l'empoussièrement par un organisme accrédité Cofrac ; travaux au-delà de 5 fibres par litre",
  "Liste A, niveau 3 : retrait ou confinement dans les 3 ans, mesures conservatoires sous 2 mois, information du préfet sous 2 mois et calendrier des travaux sous 12 mois",
  "Liste B : évaluation périodique, action corrective de 1er niveau sur les éléments dégradés, ou de 2nd niveau sur toute une zone"
 ],
 "longueur_demandee": "detaillee"
}
```

## RE-514 — Résumé (moyen, thème `fiscalite-locale`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RE-514",
 "tache": "Résumé",
 "difficulte": "moyen",
 "theme": "fiscalite-locale",
 "entree": {
  "consigne": "Résume ce document en 200 mots au plus, pour un créateur d'entreprise reçu par le service développement économique de l'intercommunalité.",
  "document": "Voici une liste de différentes questions ou thématiques relatives à ce sujet :\n- Qui doit payer la CFE ?\n- Quelles sont les exonérations de CFE ?\n- Quand réaliser la déclaration CFE ?\n- Quel est le montant de la CFE ?\n- Comment payer la CFE ?\n- Quelle démarche en cas de changement d'exploitant ?\nLa cotisation foncière des entreprises (CFE) peut être due, lorsque les conditions sont réunies, notamment par toute société, toute entité non dotée de la personnalité morale ou encore tout entrepreneur individuel (dont les micro-entrepreneurs), y compris s’il exerce son activité à domicile ou chez ses clients. Exemple: Les entités non dotées de la personnalité morale peuvent par exemple être des régies (régies municipales...), certaines fondations universitaires, des indivisions, ou encore des fonds communs de placement: Il existe un certain nombre de conditions générales pour être soumis à la CFE. Toutefois, en matière de location et sous-location d'immeubles, des conditions supplémentaires sont exigées.\nCas Cas général: Quels que soient la nature de l’activité, le régime d'imposition ou la nationalité d’un contribuable, la CFE est due lorsque les conditions suivantes sont remplies : \n- L'activité est exercée en France\n- L'activité présente un caractère habituel : elle est exercée de manière répétée\n- L'activité est exercée à titre professionnel : cela exclut les activités sans but lucratif et les personnes qui se limitent à la gestion de leur patrimoine privé\n- L'activité est non salariée : les salariés ne sont pas concernés par la CFE.\nCas Location et sous-location d'immeubles: Quels que soient la nature de l’activité, le régime d'imposition ou la nationalité d’un contribuable, la CFE est due lorsque les conditions suivantes sont remplies : \n- L'activité est exercée en France .\n- L'activité présente un caractère habituel : elle est exercée de manière répétée.\n- L'activité est exercée à titre professionnel : cela exclut les activités sans but lucratif et les personnes qui se limitent à la gestion de leur patrimoine privé.\n- L'activité est non salariée : les salariés ne sont pas concernés par la CFE.\n Lorque l’activité porte sur de la location ou sous-location d'immeubles, la CFE est due dans les situations suivantes : \n- Location ou sous-location d'immeubles nus : le chiffre d'affaires ou les recettes brutes hors taxes doivent être au moins égaux à 100 000 € . En revanche, la CFE ne concerne pas la location et sous-location d'immeubles nus à usage d'habitation .\n- Location ou sous-location d'immeubles meublés : le chiffre d'affaires ou les recettes brutes hors taxes doivent être supérieurs à 5 000 € . Cependant, la CFE n’est pas due lorsque la location meublée porte sur un logement inclus dans la résidence principale du propriétaire.\nRéférence : Code général des impôts : article 1447:\nL’exonération de plein droit est en général permanente bien qu’il existe certaines exceptions. Les personnes et organismes bénéficiant de cette exonération de plein droit sont les suivants : Exonération de plein droit permanente:\n- Artisans et façonniers travaillant soit pour les particuliers avec des matériaux fournis, soit pour leur compte avec des matières leur appartenant, qu'ils aient ou non une enseigne ou une boutique, lorsqu'ils utilisent uniquement le concours d'apprenti(s)sous contrat. Ils peuvent se faire aider de leur conjoint, de leur partenaire Pacs et de leurs enfants.\n- Chauffeurs de taxis ou d'ambulances, propriétaires ou locataires d'1 ou 2 voitures, de 7 places maximum (sans compter la place du chauffeur), qu'ils conduisent ou gèrent eux-mêmes, à condition que les 2 voitures ne soient pas en service en même temps et qu'ils respectent les tarifs réglementaires\n- Vendeurs à domicile indépendants (VDI) , pour leur rémunération brute totale inférieure à 7 930 €\n- Coopératives et unions de sociétés coopératives d'artisans, sociétés coopératives et unions de sociétés coopératives de patrons bateliers, sociétés coopératives maritimes\n- Grands ports maritimes, ports autonomes, ports gérés par des collectivités territoriales, des établissements publics ou des sociétés d'économie mixte (à l'exception des ports de plaisance)\n- Certains pêcheurs, sociétés de pêche artisanale et inscrits maritimes\n- Exploitants agricoles, certains groupements d'employeurs et certains GIE\n- Certaines coopératives agricoles et leurs unions\n- Établissements zoologiques pour leur activité agricole (soins donnés aux animaux ainsi que les spectacles et animations pédagogiques)\n- Sociétés coopératives et participatives (Scop)\n- Établissements privés d'enseignement du premier et second degré sous contrat avec l'État et d'enseignement supérieur sous convention ou reconnus d'utilité publique\n- Professeurs de lettres, sciences et arts d'agrément et instituteurs primaires qui dispensent leur enseignement personnellement, soit à leur domicile ou au domicile de leurs élèves, soit dans un local dépourvu d'enseigne et ne comportant pas un aménagement spécial\n- Peintres, sculpteurs, graveurs et dessinateurs considérés comme artistes et ne vendant que le produit de leur art. Cela inclut les graphistes à condition que leur activité soit limitée à la création d'œuvres graphiques.\n- Photographes auteurs, pour leur activité relative à la réalisation de prises de vues et à la cession de leurs œuvres d'art ou de droits d'auteur\n- Auteurs, compositeurs, chorégraphes, traducteurs percevant des droits d'auteur, et certaines catégories d'entrepreneurs de spectacles (spectacles vivants)\n- Artistes lyriques et dramatiques\n- Activités de presse : éditeurs de publications périodiques, services de presse en ligne, diffuseurs de presse spécialiste\n- Sages-femmes et garde-malades (sauf s'ils relèvent de la profession d'infirmière)\n- Sportifs pour la seule pratique d'un sport\n- Syndicats professionnels, quelle que soit leur forme juridique, et leurs unions pour leurs activités portant sur l'étude et la défense des droits et des intérêts collectifs matériels ou moraux de leurs membres ou des personnes qu'ils représentent\n- Organismes HLM et les propriétaires ou locataires louant ou sous-louant une partie de leur habitation personnelle de façon occasionnelle à un prix raisonnable (ou en meublé, à condition que le logement constitue la résidence principale du sous-locataire)\n- Exploitants de meublé de tourisme classé ou de chambre d'hôtes (sauf délibération contraire de la commune), à condition que ces locaux fassent partie de leur habitation personnelle (résidence principale ou secondaire en dehors des périodes de location) et ne constituent pas l'habitation principale ou secondaire du locataire",
  "nb_mots": 947
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F23547 « Cotisation foncière des entreprises (CFE) » (chunks 1, 2, 4)",
   "url": "https://entreprendre.service-public.gouv.fr/vosdroits/F23547",
   "type": "service-public",
   "doc_id": "F23547",
   "chunks": [
    1,
    2,
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
  "La CFE peut être due par toute société, entité sans personnalité morale ou entrepreneur individuel, y compris micro-entrepreneur, même à domicile",
  "Conditions : activité exercée en France, habituelle, à titre professionnel et non salariée",
  "Location ou sous-location : immeubles nus à partir de 100 000 € de recettes (hors habitation), meublés au-delà de 5 000 € (sauf logement dans la résidence principale)",
  "Exonérations de plein droit, en général permanentes, pour de nombreuses activités : artisans travaillant seuls ou avec apprentis, taxis, VDI sous 7 930 €, exploitants agricoles, artistes, auteurs, sportifs, presse, sages-femmes…",
  "Location occasionnelle d'une partie de son habitation et meublés de tourisme classés ou chambres d'hôtes dans sa propre habitation sont aussi exonérés (sauf délibération contraire de la commune pour ces derniers)"
 ],
 "longueur_demandee": "moyenne"
}
```

## RE-515 — Résumé (difficile, thème `social-autonomie`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RE-515",
 "tache": "Résumé",
 "difficulte": "difficile",
 "theme": "social-autonomie",
 "entree": {
  "consigne": "Fais un résumé détaillé de ce document, en 400 mots au plus, pour un agent d'accueil du centre communal d'action sociale.",
  "document": "Voici une liste de différentes questions ou thématiques relatives à ce sujet :\n- À quoi sert la complémentaire santé solidaire ?\n- Quelles sont les conditions de ressources pour avoir droit à la complémentaire santé solidaire ?\n- Quelles sont les conditions de résidence en France pour avoir droit à la complémentaire santé solidaire ?\n- Comment savoir si l'on peut bénéficier de la complémentaire santé solidaire ?\n- Comment faire la demande de complémentaire santé solidaire ?\n- Comment l'Assurance maladie étudie la demande de complémentaire santé solidaire ?\n- Combien de temps dure la complémentaire santé solidaire ?\n- Faut-il renouveler la complémentaire santé solidaire ?\n- Comment est étudiée la demande de complémentaire santé solidaire ?\n- Faut-il renouveler la complémentaire santé solidaire  ?\n- Par messagerie ou courrier postal\n- Via un rendez-vous téléphonique\nPour obtenir la complémentaire santé solidaire, vos revenus ne doivent pas dépasser un certain montant. La complémentaire santé solidaire est gratuite ou payante selon le niveau de vos revenus. En savoir plus si vous percevez le RSA, l’ASI, l’AAH, l’Aspa, l’ASS ou l’ACEJ:\nCas Revenu de solidarité active (RSA): Si vous percevez le RSA , vous avez droit à la complémentaire santé solidaire gratuite . Cette attribution est automatique sauf opposition de votre part.\nCas Allocation supplémentaire d'invalidité (Asi): Depuis le 1 er juillet 2024 , lorsque l’ Asi vous est attribuée, votre caisse d'assurance maladie vous propose systématiquement la C2S payante. Cette proposition se fait par courrier. Cette présomption ne s'applique pas si le titulaire de l'Asi et, éventuellement, son époux, concubin ou partenaire auquel il est lié par un Pacs , a exercé une activité salariée ou indépendante pendant les 3 mois civils précédant le dépôt de leur demande d'attribution de la complémentaire santé solidaire.\nCas Allocation de solidarité aux personnes âgées (Aspa): Vous et votre conjoint bénéficiez d’un accès facilité à la C2S payante à condition de ne pas avoir travaillé au cours des 3 mois précédant votre demande de C2S .\nCas Allocation aux adultes handicapés (AAH): Vous avez droit à la C2S payante si vous : \n- Vivez seul et sans enfant à charge\n- N’avez pas exercé une activité professionnelle au cours des 3 mois précédant la date de demande de la C2S\n- Percevez le montant maximum d’AAH ou vous la percevez en complément d’une pension d’invalidité, d’une pension de retraite ou d’une rente accident du travail - maladie professionnelle.\nCas Allocation de solidarité spécifique (ASS): Depuis le 1 er juillet 2026 , lorsque l’ ASS vous est attribuée et que vous vivez seul sans enfant à charge, votre caisse d'Assurance maladie vous propose systématiquement la C2S payante. En cas de doute sur votre éligibilité, vous pouvez effectuer une simulation en ligne, mais aussi demander la C2S pour que votre dossier soit étudié en détail par votre caisse d'Assurance maladie de rattachement. Un simulateur vous permet de savoir si vous pouvez bénéficier de la complémentaire santé solidaire :\nCas Allocation contrat d’engagement jeune (ACEJ): Depuis le 1 er juillet 2026 , lorsque l’ACEJ vous est attribuée et que vous constituez un foyer non imposable ou que vous êtes rattaché à un tel foyer, votre caisse d'Assurance maladie vous propose systématiquement la C2S payante. En cas de doute sur votre éligibilité, vous pouvez effectuer une simulation en ligne, mais aussi demander la C2S pour que votre dossier soit étudié en détail par votre caisse d'Assurance maladie de rattachement. Un simulateur vous permet de savoir si vous pouvez bénéficier de la complémentaire santé solidaire :\nLes règles diffèrent selon s'il s'agit d'une 1 re demande ou non.\nCas 1re demande: Selon vos revenus, la complémentaire santé solidaire (C2S) sera gratuite ou payante (avec participation). Si vos revenus ne dépassent pas le plafond annuel indiqué, la C2S est gratuite : \nPlafond de ressources pour l'attribution de la C2S gratuite:\n| Nombre de personnes au foyer | Plafond annuel de ressources | \n| - | - | \n| 1 personne | 10 421 € | \n| 2 personnes | 15 632 € | \n| 3 personnes | 18 758 € | \n| 4 personnes | 21 885 € | \n| Par personne en + | 4 169 € | \n Elle est payante si vos revenus sont compris dans la fourchette suivante : \nPlafond de ressources pour l'attribution de la C2S payante:\n| Nombre de personnes au foyer | Plafond annuel de ressources | \n| - | - | \n| \n| \n| 1 personne | Entre 10 421 € et 14 069 € | \n| 2 personnes | Entre 15 632 € et 21 103 € | \n| 3 personnes | Entre 18 758 € et 25 324 € | \n| 4 personnes | Entre 21 885 € et 29 544 € | \n| Par personne supplémentaire | 5 628 € | \n Les ressources prises en compte sont celles perçues au cours d'une période de 12 mois. Cette période va du 13 e mois jusqu'au 2 e mois civil qui précède le mois de la demande. Exemple: Vous avez fait une demande le 15 février 2026. Le mois de la demande est donc le mois de février. La période prise en compte (entre le 13 e et 2 e mois avant) est donc la période qui va du 1 er janvier 2025 au 31 décembre 2025. Si vous avez des revenus de placements soumis à l'impôt sur le revenu (compte épargne, livret d'épargne bancaire, compte à terme, Perp...), les revenus pris en compte sont ceux du dernier avis d'imposition connu. Si vous percevez une aide au logement , un montant forfaitaire est ajouté à vos ressources . Ce forfait dépend du nombre de personnes au foyer. \nForfait logement en fonction du nombre de personnes au foyer:\n| Nombre de personnes au foyer | Forfait logement | \n| - | - | \n| 1 | 78,20 € | \n| 2 | 156,41 € | \n| 3 ou + | 193,55 € | \n Si vous êtes hébergé gratuitement ou propriétaire de votre logement, un montant forfaitaire est ajouté à vos ressources . Ce forfait dépend du nombre de personnes au foyer. \nForfait logement en fonction du nombre de personnes au foyer:\n| Nombre de personnes au foyer | Forfait logement | \n| - | - | \n| 1 | 78,20 € | \n| 2 | 136,86 | \n| 3 ou + | 164,23 |\nCas Renouvellement de la demande: Vous devez remplir les mêmes conditions liées aux conditions de ressources que lors de la 1ère demande. Si vos revenus ne dépassent pas le plafond annuel indiqué, la C2S est gratuite : \nPlafond de ressources pour l'attribution de la C2S gratuite:\n| Nombre de personnes au foyer | Plafond annuel de ressources | \n| - | - | \n| 1 personne | 10 421 € | \n| 2 personnes | 15 632 € | \n| 3 personnes | 18 758 € | \n| 4 personnes | 21 885 € | \n| Par personne en + | 4 169 € | \n Elle est payante si vos revenus sont compris dans la fourchette suivante : \nPlafond de ressources pour l'attribution de la C2S payante:\n| Nombre de personnes au foyer | Plafond annuel de ressources | \n| - | - | \n| \n| \n| 1 personne | Entre 10 421 € et 14 069 € | \n| 2 personnes | Entre 15 632 € et 21 103 € | \n| 3 personnes | Entre 18 758 € et 25 324 € | \n| 4 personnes | Entre 21 885 € et 29 544 € | \n| Par personne supplémentaire | 5 628 € |\nIl faut distinguer selon que vous avez ou non la nationalité française.\nCas Vous êtes français: Vous devez être dans l'une des situations suivantes : \n- Vous devez résider en France sans interruption depuis plus de 3 mois\n- Vous bénéficiez d'un régime obligatoire de sécurité sociale car vous avez une activité professionnelle en France qui dure plus de 3 mois\n- Vous êtes inscrit dans un établissement d'enseignement en France\n- Vous faites un stage en France dans le cadre d'accords de coopération ou un stage de formation professionnelle pour une durée de plus de 3 mois\n- Vous percevez certaines prestations (prestations familiales, allocations aux personnes âgées, allocations logement, aide sociale, revenu de remplacement, allocation aux adultes handicapés, etc.)\n- Vous avez fait un volontariat international à l'étranger et n'avez pas droit à l'assurance maladie d'une autre façon.\n (À noter: Si vous êtes sans domicile stable, vous pouvez obtenir une adresse administrative .)\n Un Français établi hors de France peut-il prétendre à la C2S ? Si vous êtes un Français établi à l'étranger, vous pouvez demander à être pris en charge par la C2S si vous répondez aux conditions suivantes : \n- Vous avez le droit à la Puma\n- Vous recevez des soins en France\n- Vos ressources sont inférieures au plafond.\nCas Vous êtes étranger: Il faut distinguer selon la durée depuis laquelle vous êtes en France. \nCas En France depuis plus de 3 mois: Vous devez remplir les 2 conditions suivantes : \n- Avoir un titre de séjour valide pour séjourner en France\n- Résider en France de manière ininterrompue depuis plus de 3 mois.\n Si vous êtes sans domicile stable, vous pouvez obtenir une adresse administrative auprès d'un centre communal d'action sociale (CCAS) ou d'une association agréée. (À savoir: si vous êtes en situation irrégulière (c'est-à-dire que nous n'avez pas de papiers ou de droit d'être en France), vous pouvez demander à bénéficier de l'aide médicale de l'État (AME).)\nCas En France depuis moins de 3 mois: Vous devez être dans l'une des situations suivantes : \n- Vous bénéficiez d'un régime obligatoire de sécurité sociale car vous avez une activité professionnelle en France qui dure plus de 3 mois\n- Vous êtes Inscrit dans un établissement d'enseignement ou effectuez un stage en France dans le cadre d'accords de coopération ou vous êtes inscrit à un stage de formation professionnelle pour une durée de plus de 3 mois\n- Vous bénéficiez de certaines prestations (prestations familiales, allocations aux personnes âgées, de logement, d'aide sociale, revenu de remplacement, allocation aux adultes handicapés, etc.)\n- Vous avez fait un volontariat international à l'étranger et n'avez pas droit à l'assurance maladie d'une autre façon.\n Si vous êtes sans domicile stable, vous pouvez obtenir une adresse administrative auprès d'un centre communal d'action sociale (CCAS) ou d'une association agréée. (À savoir: si vous êtes en situation irrégulière (c'est-à-dire que nous n'avez pas de papiers ou de droit d'être en France), vous pouvez demander à bénéficier de l'aide médicale de l'État (AME).)",
  "nb_mots": 1540
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F10027 « Complémentaire santé solidaire (ex-CMU-C) » (chunks 1, 3, 4, 5)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F10027",
   "type": "service-public",
   "doc_id": "F10027",
   "chunks": [
    1,
    3,
    4,
    5
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 3,
 "points_cles_reference": [
  "La complémentaire santé solidaire (C2S) est gratuite ou payante selon les revenus",
  "Attribution automatique et gratuite pour les bénéficiaires du RSA ; C2S payante proposée ou facilitée pour l'Asi, l'Aspa (sans activité dans les 3 mois), l'AAH (sous conditions), l'ASS et l'ACEJ (depuis le 1er juillet 2026)",
  "C2S gratuite jusqu'à 10 421 € par an pour 1 personne, 15 632 € pour 2 ; payante entre 10 421 € et 14 069 € pour 1 personne, entre 15 632 € et 21 103 € pour 2",
  "Ressources des 12 mois allant du 13e au 2e mois avant la demande ; revenus de placement du dernier avis d'imposition",
  "Un forfait logement est ajouté aux ressources si l'on perçoit une aide au logement, ou si l'on est propriétaire ou hébergé gratuitement",
  "Français : résider en France depuis plus de 3 mois ou être dans une situation assimilée (activité, études, stage, prestations…)",
  "Étrangers : titre de séjour valide et résidence ininterrompue de plus de 3 mois ; en situation irrégulière, aide médicale de l'État (AME)",
  "Sans domicile stable : possibilité d'obtenir une adresse administrative (pour les étrangers, le document précise : auprès d'un CCAS ou d'une association agréée)"
 ],
 "longueur_demandee": "detaillee"
}
```

## RE-519 — Résumé (difficile, thème `collectivites`)

- [ ] Relu
- Remarques :

```json
{
 "id": "RE-519",
 "tache": "Résumé",
 "difficulte": "difficile",
 "theme": "collectivites",
 "entree": {
  "consigne": "Résume ce document en 80 mots au plus, pour le directeur général des services d'une commune qui prépare un projet d'aménagement.",
  "document": "Voici une liste de différentes questions ou thématiques relatives à ce sujet :\n- Qu’est-ce que l’expropriation ?\n- Quels sont les biens concernés par l’expropriation ?\n- Qui peut décider de recourir à l’expropriation ?\n- Quelles sont les conditions pour recourir à l’expropriation ?\n- Quelles sont les étapes de la procédure d’expropriation ?\nL’expropriation est un mécanisme qui permet de contraindre un propriétaire à céder (transférer la propriété) son bien (appartement, maison, immeuble, terrain etc.), dans un but d’utilité publique et contre une indemnité juste et préalable. L’expropriation est mise en œuvre lorsqu’aucun accord amiable n’a pu être conclu, pour permettre aux personnes publiques (État, collectivités territoriales etc.) ou privées d’acquérir les biens nécessaires à la réalisation de leurs missions, notamment la réalisation d’ouvrages publics et d’aménagements urbains. C’est ce qu’on appelle une prérogative de puissance publique. Il s’agit ainsi d’un mode de cession forcée de la propriété qui peut être utilisée à l’encontre d’un particulier ou d’une personne morale. (À savoir: L’expropriation ne doit pas être confondue avec le droit de préemption urbain , qui est un droit d’achat prioritaire exercé par une commune sur un bien mis en vente dans une zone urbaine. La préemption respecte la volonté initiale du propriétaire de céder son bien , tandis que l’expropriation permet, à l’inverse, d’obliger le propriétaire à vendre malgré son refus.)\nLa procédure d’expropriation débute par une phase administrative qui se déroule en 4 étapes :\n- L’enquête préalable\n- La déclaration d’utilité publique\n- L’enquête parcellaire\n- L’arrêté de cessibilité.\nEnquête préalable: L’enquête préalable à l’expropriation a pour objectif d’ informer le public sur le projet envisagé. Elle permet à toute personne intéressée de formuler ses observations ou ses remarques sur l’opération d’expropriation. Cette étape de consultation vise ainsi à recueillir le plus grand nombre d’avis afin d’éclairer l’administration sur l’ utilité publique du projet avant toute décision. (À savoir: Avant la mise en place de l’enquête préalable, l’administration peut, de façon facultative, consulter le public en organisant un débat public ou un référendum.)\nL’enquête préalable se déroule en plusieurs étapes :\n- L’ expropriant doit d’abord envoyer un dossier au préfet du département où l’opération doit être réalisée. Ce dossier doit notamment contenir une notice explicative du projet, un plan de situation, un plan général des travaux, les caractéristiques principales des ouvrages les plus importants et l’appréciation sommaire des dépenses. Dans l’hypothèse où le projet a des incidences importantes sur l’environnement ou la santé humaine, il est également obligatoire de fournir une étude d’impact.\n- Un commissaire enquêteur est ensuite nommé par le tribunal administratif. C’est lui qui effectuera l’enquête publique préalable.\n- Un arrêté préfectoral est alors pris par le préfet, ordonnant l’ouverture de l’enquête. Cette ouverture est mentionnée dans les journaux locaux diffusés dans le département et fait l'objet d'un affichage en mairie où le projet doit avoir lieu. Il y est indiqué les heures et le lieu où le public peut prendre connaissance du dossier et formuler des observations sur un registre ouvert à cet effet.\n- Par la suite, le commissaire enquêteur réalise l’enquête publique préalable. Cela consiste, principalement, à mettre en place un registre d’enquête destiné à recueillir les informations/observations du public et à étudier les documents techniques du projet.\n- À la fin de l’enquête, le commissaire enquêteur examine les observations recueillies, il rédige un rapport avec ses conclusions motivées sur le projet, précisant s’il est ou non favorable à l’opération envisagée . Le commissaire enquêteur transmet le dossier d’enquête et ses conclusions au Préfet. La copie de ce rapport est consultable par le public.\n(À savoir: Dès l’ouverture de l’enquête préalable, l’ expropriant peut notifier aux propriétaires concernés une offre d’indemnité et les inviter à indiquer le montant de leur propre demande.)\nDéclaration d’utilité publique: Au vu des résultats de l'enquête du commissaire-enquêteur, si l'utilité publique du projet est identifiée, le préfet prononce, par un arrêté, une déclaration d'utilité publique (DUP). (À savoir: Pour certains domaines, la DUP peut être prise par un arrêté en Conseil d’État. C’est le cas, par exemple, pour des travaux de création d’autoroute, d’aérodrome ou de canaux de navigation d’une longueur supérieure à 5 km.)\nLa DUP doit indiquer :\n- Le but d’utilité publique de l’opération\n- Les textes sur lesquels elle est fondée\n- Les travaux éventuels nécessaires à sa réalisation\n- Le bénéficiaire de l’expropriation\n- Le délai accordé pour réaliser l’expropriation (5 ans maximum).\nL’acte déclaratif d’utilité publique doit être publié au Journal officiel s’il a la forme d’un décret ou par voie d’affichage dans les communes concernés s’il a été pris par arrêté préfectoral. Il n’y a donc pas de notification individuelle aux personnes concernées. (À noter: L'acte déclarant l'utilité publique doit intervenir au plus tard 1 an après la clôture de l'enquête préalable . Ce délai peut être prolongé dans certains cas.)\nEnquête parcellaire: L’enquête parcellaire a pour but de :\n- Déterminer contradictoirement les parcelles à exproprier par l’établissement des caractéristiques cadastrales et des adresses postales, l’identification des servitudes et des hypothèques, la mesure des surfaces et la recherche de l’origine de propriété. L’identification des biens à exproprier se fait en présence et avec la participation des propriétaires concernés.\n- Rechercher les propriétaires, titulaires de droits réels et de tout intéressé.\n(À savoir: L’enquête parcellaire peut être menée postérieurement à la déclaration d’utilité publique (DUP) ou parallèlement à l’enquête publique préalable.)\nL ’expropriant adresse ainsi au préfet un dossier contenant un plan parcellaire des terrains et des bâtiments à exproprier ainsi que la liste des propriétaires. Le dépôt du dossier doit être notifié individuellement aux propriétaires figurant sur la liste contenue dans le dossier ou à leurs mandataires, gérants, administrateurs, par lettre recommandée avec accusé de réception. Cette notification intervient à l’ouverture de l’enquête parcellaire afin de permettre aux propriétaires visés par l’expropriation de formuler leurs observations ou remarques durant l’enquête. (À noter: En cas d' indivision , la notification est faite à chaque coïndivisaire. De même, la notification du dépôt du dossier d'enquête parcellaire est faite à l' usufruitier et au nu-propriétaire .)\nLe préfet prend ensuite un arrêté qui ouvre l'enquête parcellaire. Cet arrêté est publié dans un journal diffusé dans le département concerné et par voie d’affichage dans les mairies touchées par l’opération d’expropriation. Dans le même temps, le préfet désigne un commissaire enquêteur ou une commission d’enquête, chargé de l’enquête parcellaire. Le commissaire-enquêteur ou la commission d’enquête donne ensuite un avis sur l’ emprise des ouvrages projetés et établit un procès-verbal de l’opération. Cet avis prend en compte les observations consignées par les propriétaires ou toute personne intéressée par le projet d’expropriation dans les registres mis à leur disposition pendant la durée de l’enquête. Arrêté de cessibilité: Dès qu’il a reçu le procès-verbal du commissaire enquêteur ou de la commission d’enquête, le préfet prend un arrêté de cessibilité. Cet arrêté doit :\n- Désigner les propriétés déclarées cessibles en précisant la nature, la situation, la contenance et la situation cadastrale (section, numéro du plan et lieu-dit)\n- Préciser l’identité des propriétaires.\nLe préfet peut exclure des parcelles du dossier d’enquête parcellaire lorsqu’elles ne sont pas nécessaires ou utiles à la réalisation du projet. (À noter: Le préfet peut augmenter l' emprise de l'opération projetée, si cette augmentation est justifiée par le projet et reste limitée.)\nL’arrêté de cessibilité doit obligatoirement être notifié, par lettre recommandée avec avis de réception, aux propriétaires concernés par le projet d’expropriation. Cette notification doit mentionner les délais et les voies de recours. De même, l’arrêté de cessibilité doit être transmis dans un délai de 6 mois au greffe du juge de l’expropriation. (Attention: L’arrêté de cessibilité constitue le dernier acte de la phase administrative de l’expropriation. Il n’opère toutefois pas de transfert de propriété. À ce stade, les propriétaires conservent leurs droits sur leurs biens . En l’absence d’accord amiable, c’est au juge judiciaire de prononcer la cession (transfert de propriété) du bien par l’ordonnance d’expropriation.)",
  "nb_mots": 1279
 },
 "parametres": {},
 "provenance": [
  {
   "consulte_le": "2026-10-20",
   "source": "MediaTech AgentPublic/service-public, fiche F762 « Procédure d’expropriation » (chunks 1, 2, 7, 8)",
   "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F762",
   "type": "service-public",
   "doc_id": "F762",
   "chunks": [
    1,
    2,
    7,
    8
   ],
   "depot": "AgentPublic/service-public",
   "revision": "29f236f8a534bb599cd82b4f9731307bf5c0dbb1"
  }
 ],
 "licence_source": "Fiche : Licence Ouverte / Etalab 2.0.",
 "fictif": false,
 "version_item": 2,
 "points_cles_reference": [
  "L'expropriation contraint un propriétaire à céder son bien pour un but d'utilité publique, contre une indemnité juste et préalable, en l'absence d'accord amiable (à ne pas confondre avec la préemption)",
  "Phase administrative en 4 étapes : enquête préalable, déclaration d'utilité publique, enquête parcellaire, arrêté de cessibilité",
  "Les propriétaires sont notifiés individuellement par recommandé lors de l'enquête parcellaire et de l'arrêté de cessibilité",
  "L'arrêté de cessibilité ne transfère pas la propriété : sans accord amiable, c'est le juge de l'expropriation qui la transfère"
 ],
 "longueur_demandee": "courte"
}
```
