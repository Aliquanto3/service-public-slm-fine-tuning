"""Lance `slmsp <args>` dans ce processus, sous garde mémoire.

Un fil surveille la RAM utilisée du PC (psutil) toutes les 5 s. Au-delà du seuil
(GARDE_RAM_GO, défaut 28), il lève KeyboardInterrupt dans le fil principal : `train run`
clôt alors son run en `interrompu` (« arrêt demandé »), comme un Ctrl+C.
Le pic est écrit sur stderr à la fin.
"""

import _thread
import os
import sys
import threading
import time

import psutil

SEUIL = float(os.environ.get("GARDE_RAM_GO", "28")) * 1024**3
pic = 0
declenche = False


def surveiller() -> None:
    global pic, declenche
    while True:
        utilise = psutil.virtual_memory().used
        pic = max(pic, utilise)
        if utilise > SEUIL and not declenche:
            declenche = True
            print(f"GARDE RAM : {utilise / 1024**3:.1f} Go > seuil, arrêt demandé", file=sys.stderr)
            _thread.interrupt_main()
        time.sleep(5)


threading.Thread(target=surveiller, daemon=True).start()
from slmsp.cli import main  # noqa: E402

sys.argv = ["slmsp", *sys.argv[1:]]
try:
    code = main()
finally:
    print(f"GARDE RAM : pic {pic / 1024**3:.1f} Go, déclenché={declenche}", file=sys.stderr)
sys.exit(code)
