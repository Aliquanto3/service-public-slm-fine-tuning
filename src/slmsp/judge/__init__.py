"""Juges du banc d'évaluation (AD-3, AD-12).

Le Juge principal Claude note une sortie critère par critère selon la grille v1, à l'aveugle :
il ne reçoit que l'entrée rendue de l'item, le texte final, les sources citées (titre, URL),
les références de l'item et la section de grille de la Tâche, jamais le modèle évalué ni la
méthode. Sa sortie suit un schéma JSON fermé par Tâche (AD-12) ; il ne calcule aucun score
(`slmsp.evaluation.scores`).

- `slmsp.judge.config` : `config/juges.toml` ;
- `slmsp.judge.grille` : lecture de la grille (sections, gabarit, empreintes) ;
- `slmsp.judge.prompt` : schéma de sortie, rendu du prompt, validation d'un verdict ;
- `slmsp.judge.cache` : cache des verdicts, journal des appels et lots (`verdicts.sqlite`) ;
- `slmsp.judge.claude` : `JugeClaude` (Batch API par défaut, sous `RegistreBudget`).

AD-3 verrou 1 : ce paquet est le seul importeur d'`anthropic`, et seulement dans
`slmsp.judge.claude` ; aucun réexport ici, pour que `import slmsp.judge` n'importe pas le SDK.
AD-3 verrou 6 : les verdicts ne servent qu'au banc d'évaluation, jamais à `data` ni `train`.
"""
