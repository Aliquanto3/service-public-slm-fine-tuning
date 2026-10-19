# Campagne de fine-tuning v11 : point de reprise après `/clear`

Suite de `etat-run-2026-10-19-portable.md` (journal du 19, décisions d'Anaël) et de `dossier-relecture-v9.md` (jeu et protocole).

## Autorisation d'Anaël (19 octobre 2026, vers 18 h)
« Quand le point autour de RD sera réglé, je t'autorise à lancer l'entraînement avec les modèles validés selon le protocole défini plus tôt. »
- Le point RD est réglé par la story 9.12 (producteur et date seulement s'ils figurent au résultat d'outil), puis par la régénération de RD seul, le build v10 et le nettoyage v11.
- Modèles validés : **MiniCPM5-2B, Qwen3.5-2B, Qwen3.5-0.8B**. Granite 4.0 1B est en réserve, hors campagne.
- Budget : campagne `finetune-v9-2026-10-19` de `config/budgets.toml`, 30 € pour Anthropic. Le registre la garde après le passage à v11, inutile d'en ouvrir une autre. Chaque notation passe par `--plafond-estime 4.5`.

## Protocole
1. **M1 QLoRA sur les trois modèles, en série sur le GPU** : MiniCPM5-2B, puis Qwen3.5-2B, puis Qwen3.5-0.8B.
   - Configs `config/runs/m1-qlora-<slug>-v11.toml` (prêtes et validées par `charger_run_config` ; campagne `<slug>-v11`, `jeu_version = "v11"`).
   - Hyperparamètres : bf16, 8 192 tokens, rang 16, lr 2e-4, 1 époque, lot 1 × 8, graine 1234.
2. Pour chaque M1 : export cuda, génération q4_k_m sur le jeu v1.1 en cuda, puis notation avec `--plafond-estime 4.5`.
   - Script : `C:\Users\Anael\dev\slmsp-wt\scripts-campagne\campagne-run.ps1 -Toml <toml>`. Il tourne sous garde RAM à 28 Go, avec `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`.
   - La notation d'un run peut tourner pendant l'entraînement suivant.
3. **Règle de suite** : M3 DoRA (`m3-dora-<slug>-v11.toml`, prêtes) et M4 ORPO seulement pour un modèle dont M1 dépasse **sa** Baseline.
   - Baselines : MiniCPM5-2B 41,1 ; Qwen3.5-2B 36,0 ; Qwen3.5-0.8B 27,5.
   - M4 : paires locales `data build --preferences --depuis <nettoyage v11> --modele base:<slug> --llama cuda`, puis TOML ORPO à 2 048 tokens, avec `sft_run_id` = M1 du modèle, dans une campagne à part.
4. **Benchmarks de non-régression** (`bench run --variante-llamacpp cuda --parallele 4`) sur le meilleur run de chaque modèle qui passe le critère de gain : +10 points contre la meilleure Baseline sur au moins 2 tâches parmi Q, RD, CR et LC.
5. **Mesures CPU** (`measure run`) des runs retenus, à la fin et machine au repos.

## Règles
- Bloqueur de veille : `C:\Users\Anael\dev\slmsp-wt\scripts-campagne\veille.ps1`, à lancer en tâche de fond pendant la campagne et à arrêter à la fin.
- Toujours `uv run --no-sync`, ou `python -m slmsp` pour les tâches longues : `slmsp.exe` verrouillé empêche de réinstaller.
- Journaliser chaque étape ci-dessous, avec l'heure prise par `date`, puis commiter. Ne rien pousser sans demande.
- Arrêt : si une notation dépasse 4,5 €, ou si la RAM dépasse le seuil de la garde. Un blocage ne suspend que ses suites.

## Journal de la campagne
- 2026-10-19 19:46 · v11 prêt : `data/train/v11` (552 lignes, SHA-256 `3b193710…`), nettoyage `runs/data-build/20261019-194543-nettoyage-c782` (build v10 `20261019-194535-build-ba68`, filtre `20261019-193107-filter-9026`, validation `20261019-190452-validate-b064`, génération `20261019-180544-generate-bd87`). Médianes en mots : Q 106, RD 46 (132 lignes), CR 396, LC 113, CT 152, RE 112, generique 96 ; titres en tête : RD 5, CT 2, autres 0. Configs M1 et M3 en v11 pour les trois modèles, prêtes. Prochaine étape : bloqueur de veille, puis M1 MiniCPM5-2B.
- 2026-10-19 19:53 · M1 · bloqueur de veille actif (PID 33152), GPU libre, Anthropic 0 € dépensé sur 30. M1 lancés en chaîne (`scratchpad/m1-chaine.ps1`) : pour chaque modèle, `campagne-run.ps1 -SansNotation` (train sous garde RAM + export cuda), génération q4_k_m v1.1 cuda, puis notation `--phase notation --plafond-estime 4.5` en tâche de fond pendant l'entraînement suivant. Ordre : MiniCPM5-2B, Qwen3.5-2B, Qwen3.5-0.8B.
- 2026-10-19 20:15 · M1 MiniCPM5-2B · entraînement **complet** en 21 min (`runs/train/20261019-195316-m1-qlora-minicpm5-2b-v11-e3e4`, pic RAM 15,9 Go). Export `20261019-201400-ft-minicpm5-2b-35a0` en `partiel-erreur` : conversion réussie, mais `WinError 32` au renommage de `modele-f16.gguf.part` (fichier verrouillé par un autre processus, sans doute l'antivirus sur le fichier de 5 Go). Export relancé après les entraînements Qwen (`campagne-run.ps1 -RunId`) : en parallèle, ses 22 Go de RAM feraient déclencher la garde. Qwen3.5-2B lancé à 20:14.
- 2026-10-19 20:19 · correctif export · `os.rename` du `.part` réessayé sur `PermissionError` (borne 60 s, sans remplacement) : dev Sonnet (0b9c417), second avis Haiku (1 medium : borne dépassée de 8 s ; 5 low), revue Sonnet (36b78d5 : borne exacte, test du câblage). Fusion 8f3d906, tests ciblés verts. Les exports suivants en profitent (venv éditable).
- 2026-10-19 20:46 · M1 Qwen3.5-2B · entraînement **complet** en 29 min (`runs/train/20261019-201519-m1-qlora-qwen3.5-2b-v11-af61`, pic RAM 14,8 Go).
- 2026-10-19 20:46 · **blocked** · au début de l'export Qwen3.5-2B (`runs/export/20261019-204454-ft-qwen3.5-2b-e730`, resté `en_cours`, vide), **Claude Code a tué ses tâches de fond pour mémoire système insuffisante** : la chaîne M1 et le bloqueur de veille. Ce n'est pas la garde RAM (seuil 28 Go non atteint) : le harnais récupère les shells de fond quand la mémoire manque pendant que la session est inactive, et interdit de les relancer sans accord d'Anaël. Aucune notation lancée, Anthropic 0 €. Restent : export + génération + notation de M1 MiniCPM5-2B (`-RunId 20261019-195316-m1-qlora-minicpm5-2b-v11-e3e4`) et M1 Qwen3.5-2B (`-RunId 20261019-201519-m1-qlora-qwen3.5-2b-v11-af61`), puis M1 Qwen3.5-0.8B. **Pour Anaël** : relancer Claude Code avec `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1` (l'export monte à ~22 Go sur 32), puis demander la reprise ; le bloqueur de veille est à relancer aussi.
- 2026-10-19 20:48 · reprise · Anaël a relancé Claude Code avec `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1`. Bloqueur de veille relancé ; chaîne `scratchpad/m1-reprise.ps1` : export + génération des M1 MiniCPM5-2B et Qwen3.5-2B déjà entraînés (`-RunId`), puis M1 Qwen3.5-0.8B ; notations en fond (`--plafond-estime 4.5`).
- 2026-10-19 20:50 · M1 MiniCPM5-2B · export **complet** `runs/export/20261019-204901-ft-minicpm5-2b-ad30` (pic RAM 20,6 Go, renommage sans incident). Génération q4_k_m v1.1 cuda lancée.
