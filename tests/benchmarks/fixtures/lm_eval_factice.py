"""Faux `lm_eval` : écrit la sortie JSON de fixture sous --output_path et journalise l'appel."""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

argv = sys.argv[1:]
sortie = Path(argv[argv.index("--output_path") + 1])
journal = {
    "argv": argv,
    "env": {
        nom: os.environ.get(nom)
        for nom in ("HF_HUB_OFFLINE", "HF_DATASETS_OFFLINE", "OPENAI_API_KEY", "SLMSP_MCQ_EVAL_DIR")
    },
}
Path(os.environ["LM_EVAL_FACTICE_JOURNAL"]).write_text(json.dumps(journal), encoding="utf-8")
if os.environ.get("LM_EVAL_FACTICE_ECHEC"):
    print("echec factice", file=sys.stderr)
    sys.exit(3)
if not os.environ.get("LM_EVAL_FACTICE_SANS_SORTIE"):
    cible = sortie / "modele-factice" / "results_2026-01-01T00-00-00.json"
    cible.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(__file__).with_name("sortie_lm_eval.json"), cible)
