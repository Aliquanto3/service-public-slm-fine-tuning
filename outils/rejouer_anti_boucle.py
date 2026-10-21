"""Rejoue le garde-fou anti-boucle (story 16.3) sur les sorties d'un run `eval-generation`.

Lecture seule : lit `generations.jsonl` du run, rejoue chaque sortie (texte des `Jeton` de la
trace, dans l'ordre) dans `harness.anti_boucle.DetecteurBoucle` avec la section
`[anti_boucle]` de `config/harnais.toml`, et affiche par Tâche le nombre de sorties coupées et
la raison de fin d'origine des sorties coupées. Aucun appel de modèle.

    uv run python outils/rejouer_anti_boucle.py runs/eval-generation/<run_id> [--detail]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from slmsp.harness.anti_boucle import DetecteurBoucle
from slmsp.harness.config import charger_config_harnais


def rejouer(dossier: Path, *, detail: bool = False) -> dict[str, Counter[str]]:
    """Comptes par Tâche : `sorties`, `coupees`, et `coupees:<raison d'origine>`."""
    config = charger_config_harnais().anti_boucle
    comptes: dict[str, Counter[str]] = {}
    with (dossier / "generations.jsonl").open(encoding="utf-8") as fichier:
        for texte in fichier:
            if not texte.strip():
                continue
            generation = json.loads(texte)
            trace = generation.get("trace") or []
            raisons = [e.get("raison") for e in trace if e.get("type") == "fin"]
            detecteur = DetecteurBoucle(config)
            coupure = None
            recu = 0
            for evenement in trace:
                if evenement.get("type") == "jeton":
                    recu += len(evenement["texte"])
                    coupure = detecteur.ajouter(evenement["texte"])
                    if coupure is not None:
                        break
            compte = comptes.setdefault(str(generation.get("tache")), Counter())
            compte["sorties"] += 1
            if coupure is not None:
                compte["coupees"] += 1
                compte[f"coupees:{raisons[-1] if raisons else 'sans-fin'}"] += 1
                if detail:
                    print(f"{generation['item_id']} : coupée à {coupure} sur {recu} caractères")
    return comptes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path, help="dossier du run eval-generation")
    parser.add_argument("--detail", action="store_true", help="une ligne par sortie coupée")
    args = parser.parse_args(argv)
    for tache, compte in sorted(rejouer(args.run, detail=args.detail).items()):
        autres = ", ".join(f"{k}={v}" for k, v in sorted(compte.items()) if ":" in k)
        print(f"{tache} : {compte['coupees']}/{compte['sorties']} coupées {autres}".rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
