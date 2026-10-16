"""Point d'entrée de l'exécutable gelé (story 12.12)."""

import multiprocessing

from slmsp.app.principal import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
