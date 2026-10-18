"""Compare deux jeux `data/train/vN` : seul le premier message `user` des lignes RD change.

Usage : python outils/verifier_rd_connecte.py <ancien-dossier> <nouveau-dossier>

Contrôle (lecture seule, sans réseau) : mêmes lignes dans le même ordre ; pour les lignes
des Tâches à outils, seul `messages[1]` diffère et vaut la demande seule du Mode connecté
(`messages_connecte`) ; tout le reste (système, outils, tours d'appel, résultats, réponses,
meta) est identique ; les autres lignes sont identiques à l'octet ; MANIFEST cohérent.
Aussi : nombre de lignes modifiées égal au compte des Tâches à outils du MANIFEST (et le
reste identique) ; `tools` de chaque ligne nouvelle égal aux outils de `config/outils-mcp.toml`
filtrés par `outils_autorises` (ordre du fichier) ; chaque ligne nouvelle valide au schéma
`LigneEntrainement` ; `sha256_train` de chaque MANIFEST égal au SHA-256 de son train.jsonl.
Code de sortie 0 si tout est conforme.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from pydantic import ValidationError

from slmsp.core.config import racine_projet
from slmsp.core.schemas.entrainement import LigneEntrainement
from slmsp.harness.taches import charger_taches
from slmsp.harness.taches.recherche import messages_connecte
from slmsp.mcp.outils import charger_outils

DEMANDE = re.compile(r"\nDemande :\n(.*)\Z", re.DOTALL)


def lire(dossier: Path) -> tuple[list[bytes], dict]:
    octets = (dossier / "train.jsonl").read_bytes()
    return octets.split(b"\n")[:-1], json.loads((dossier / "MANIFEST.json").read_bytes())


def verifier(ancien: Path, nouveau: Path) -> list[str]:
    erreurs: list[str] = []
    brutes_a, man_a = lire(ancien)
    brutes_n, man_n = lire(nouveau)
    taches = charger_taches()
    outils = charger_outils(racine_projet() / "config" / "outils-mcp.toml")
    for nom, dossier, man in (("ancien", ancien, man_a), ("nouveau", nouveau, man_n)):
        sha = hashlib.sha256((dossier / "train.jsonl").read_bytes()).hexdigest()
        if man["sha256_train"] != sha:
            erreurs.append(f"sha256_train du MANIFEST {nom} incohérent")
    if len(brutes_a) != len(brutes_n):
        return [f"{len(brutes_a)} lignes contre {len(brutes_n)}"]
    comptes = {"identiques": 0, "modifiees": 0}
    for rang, (a, n) in enumerate(zip(brutes_a, brutes_n, strict=True)):
        la, ln = json.loads(a), json.loads(n)
        tache = taches.tache(la["tache"]) if la["tache"] != "generique" else None
        try:
            LigneEntrainement.model_validate(ln)
        except ValidationError as exc:
            erreurs.append(f"ligne {rang} : non conforme au schéma : {exc}")
        autorises = set(tache.outils_autorises) if tache is not None else set()
        attendus = [o for o in outils if (o.get("function") or {}).get("name") in autorises]
        if ln["tools"] != attendus:
            erreurs.append(f"ligne {rang} ({la['tache']}) : tools différents de outils_autorises")
        if tache is None or not tache.outils_autorises:
            if a != n:
                erreurs.append(
                    f"ligne {rang} ({la['tache']}) : modifiée alors qu'elle devait rester"
                )
            comptes["identiques"] += 1
            continue
        comptes["modifiees"] += 1
        if a == n:
            erreurs.append(f"ligne {rang} ({la['tache']}) : inchangée alors qu'elle devait changer")
        ma, mn = la["messages"], ln["messages"]
        trouve = DEMANDE.search(ma[1]["content"])
        if trouve is None:
            erreurs.append(f"ligne {rang} : ancien message user sans « Demande : »")
            continue
        attendu = messages_connecte(tache, trouve.group(1), None)[1]
        if mn[1] != attendu:
            erreurs.append(f"ligne {rang} : message user différent du Mode connecté")
        la["messages"] = [ma[0], None, *ma[2:]]
        ln["messages"] = [mn[0], None, *mn[2:]]
        if la != ln:
            erreurs.append(f"ligne {rang} : autre différence que le message user")
    sha = man_n["sha256_train"]
    a_outils = sum(
        nombre
        for code, nombre in man_n["comptes_par_tache"].items()
        if code != "generique" and taches.tache(code).outils_autorises
    )
    if comptes["modifiees"] != a_outils or comptes["identiques"] != len(brutes_n) - a_outils:
        erreurs.append(
            f"{comptes['modifiees']} lignes à outils et {comptes['identiques']} autres, "
            f"attendu {a_outils} et {len(brutes_n) - a_outils} (MANIFEST)"
        )
    if man_n["nb_lignes"] != len(brutes_n) or sum(man_n["comptes_par_tache"].values()) != len(
        brutes_n
    ):
        erreurs.append("comptes du MANIFEST nouveau incohérents")
    if man_a["comptes_par_tache"] != man_n["comptes_par_tache"]:
        erreurs.append("comptes par Tâche différents de l'ancien jeu")
    if man_n.get("mode_outils") != "connecte":
        erreurs.append("mode_outils absent ou différent de « connecte »")
    print(
        f"{len(brutes_n)} lignes : {comptes['modifiees']} modifiées (message user), "
        f"{comptes['identiques']} identiques à l'octet ; sha256_train {sha}"
    )
    return erreurs


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    erreurs = verifier(Path(argv[1]), Path(argv[2]))
    for erreur in erreurs:
        print("ERREUR :", erreur)
    print("conforme" if not erreurs else f"{len(erreurs)} erreur(s)")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
