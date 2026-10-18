"""Compare deux jeux `data/train/vN` : seul le premier message `user` des lignes RD change.

Usage : python outils/verifier_rd_connecte.py <ancien-dossier> <nouveau-dossier>

Contrôle (lecture seule, sans réseau) : mêmes lignes dans le même ordre ; pour les lignes
des Tâches à outils, seul `messages[1]` diffère et vaut la demande seule du Mode connecté
(`messages_connecte`) ; tout le reste (système, outils, tours d'appel, résultats, réponses,
meta) est identique ; les autres lignes sont identiques à l'octet ; MANIFEST cohérent.
Code de sortie 0 si tout est conforme.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from slmsp.harness.taches import charger_taches
from slmsp.harness.taches.recherche import messages_connecte

DEMANDE = re.compile(r"\nDemande :\n(.*)\Z", re.DOTALL)


def lire(dossier: Path) -> tuple[list[bytes], dict]:
    octets = (dossier / "train.jsonl").read_bytes()
    return octets.split(b"\n")[:-1], json.loads((dossier / "MANIFEST.json").read_bytes())


def verifier(ancien: Path, nouveau: Path) -> list[str]:
    erreurs: list[str] = []
    brutes_a, man_a = lire(ancien)
    brutes_n, man_n = lire(nouveau)
    taches = charger_taches()
    if len(brutes_a) != len(brutes_n):
        return [f"{len(brutes_a)} lignes contre {len(brutes_n)}"]
    comptes = {"identiques": 0, "modifiees": 0}
    for rang, (a, n) in enumerate(zip(brutes_a, brutes_n, strict=True)):
        la, ln = json.loads(a), json.loads(n)
        tache = taches.tache(la["tache"]) if la["tache"] != "generique" else None
        if tache is None or not tache.outils_autorises:
            if a != n:
                erreurs.append(
                    f"ligne {rang} ({la['tache']}) : modifiée alors qu'elle devait rester"
                )
            comptes["identiques"] += 1
            continue
        comptes["modifiees"] += 1
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
    sha = hashlib.sha256((nouveau / "train.jsonl").read_bytes()).hexdigest()
    if man_n["sha256_train"] != sha:
        erreurs.append("sha256_train du MANIFEST nouveau incohérent")
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
