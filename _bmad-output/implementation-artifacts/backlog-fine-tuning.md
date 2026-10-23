# Backlog du fine-tuning (mis en sommeil)

Le 2026-10-22, Anaël a arrêté les tentatives de fine-tuning et donné la priorité au démonstrateur (SLM préexistant et/ou cloud). Bilan : `docs/bilan-fine-tuning.md`.

Les stories ci-dessous sont closes dans `sprint-status.yaml`, où elles restent en commentaire. Pour reprendre le fine-tuning, les remettre dans `development_status` avec le statut indiqué ici, et rouvrir leur epic.

| Story | Statut à l'arrêt | Reste à faire |
|---|---|---|
| 8.3 Exécution de la baseline (jeu maison, benchmarks, mesures) | review | Relecture de la baseline |
| 8.4 Rapport de baseline | review | Relecture du rapport |
| 9.8 Campagne de génération de la nuit (jeu v1) | review | Relecture de la campagne |
| 11.2 Essai M1 QLoRA de la nuit et mini-rapport | backlog | Tout |
| 14.12 Jeu de développement : construction (O4b) | in-progress | Fin de la construction |
| 14.17 Jeu v17 vérifié et M1 MiniCPM5-2B (V17) | in-progress | Entraînement et mesure |
| 14.18 Routage par tâche sur le jeu dev (E5) | backlog | Tout (le routage CO est déjà retenu, voir 16.7) |
| 15.5 dev2 : vingt items par tâche (N5) | review | Clos de fait par 16.1 (dev2 gelé à 160 items) ; reste la relecture |
| 16.3 Prompts CT alignés, anti-boucle | in-progress | Garde-fou anti-boucle livré (v0.3.1) ; jeu v21 bloqué par la décision D1 (formulation d'Anaël) |

Reports notés au journal du run (`run-autonome.md`) : empreinte de grille absente d'un run composé (bloque le regroupement du routage) ; mesures CPU des Qwen3.5 locaux.

Epics clos avec ces stories : 8, 9, 10, 11, 14, 15, 16.
