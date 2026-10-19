"""Pilote `slmsp bench cache-hf` : cache HF des jeux de `lm_eval` (AD-28).

`lm_eval` tourne hors ligne (`HF_HUB_OFFLINE=1`, `HF_DATASETS_OFFLINE=1`) et lit le cache de
`<models>/.cache-hf`. Chaque jeu de `[options.jeux_hf]` (`config/benchmarks/*.toml`, dépôt ->
révision épinglée) y est installé en trois étapes, idempotentes :

1. `snapshot_download(depot, repo_type="dataset", revision=<épinglée>)` ;
2. `refs/main` du dépôt écrit sur la révision épinglée (le mode hors ligne résout `main`) ;
3. `load_dataset(depot, <configuration>, revision=<épinglée>)` en ligne, pour chaque
   configuration du dépôt : cela crée le cache `datasets` (hors ligne, datasets 5 ne lit pas
   les seuls snapshots).

Un contrôle relit chaque jeu dans un sous-processus hors ligne (`verifier_hors_ligne`). Avant
tout téléchargement, il sert à sauter un jeu déjà complet ; à la fin, il échoue clairement
(`CacheHorsLigneInvalide`) si un jeu n'est pas lisible hors ligne. Les dépendances lourdes
(`huggingface_hub`, `datasets`) sont importées à l'appel, et injectables pour les tests.

Cette commande vit sous `bench` et non sous `fetch` : `snapshot_download` et le sous-processus
de contrôle sont interdits au paquet `fetch` (tests/fetch/test_hf.py). Elle demande le réseau :
`preparer()` pose `HF_HOME`, coupe la télémétrie et branche la passerelle `net` sur
`huggingface_hub`, comme `fetch`.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from slmsp import net
from slmsp.core.config import appliquer_environnement_impose, dossier_modeles, env_sous_processus
from slmsp.core.erreurs import ConfigurationInvalide, SlmspError

ENV_HORS_LIGNE = {"HF_HUB_OFFLINE": "1", "HF_DATASETS_OFFLINE": "1"}

Consigner = Callable[[dict[str, Any]], None]
Verifier = Callable[[Mapping[str, str]], dict[str, str | None]]


class CacheHorsLigneInvalide(SlmspError):
    """Un jeu n'est pas relisible hors ligne dans le cache HF."""


def dossier_cache() -> Path:
    """`<models>/.cache-hf`, le `HF_HOME` de `lm_eval`."""
    return dossier_modeles() / ".cache-hf"


def preparer() -> Path:
    """`HF_HOME`, télémétrie coupée, passerelle `net` sur `huggingface_hub` ; rend `HF_HOME`."""
    import os

    cache = dossier_cache()
    os.environ["HF_HOME"] = str(cache)
    appliquer_environnement_impose()
    try:
        import huggingface_hub
    except ImportError:
        return cache
    huggingface_hub.set_client_factory(net.fabrique_hf)
    huggingface_hub.set_async_client_factory(net.fabrique_hf_async)
    return cache


def lire_pins(dossier: str | Path, depots: Sequence[str] = ()) -> dict[str, str]:
    """Dépôt -> révision, pour `[options.jeux_hf]` de `<dossier>/*.toml` (ceux de `depots`
    si non vide). `ConfigurationInvalide` pour un dépôt absent de la configuration, un
    fichier illisible ou un dépôt épinglé à deux révisions différentes."""
    base = Path(dossier)
    if not base.is_dir():
        raise ConfigurationInvalide(f"dossier des benchmarks introuvable : {base}")
    pins: dict[str, str] = {}
    for chemin in sorted(base.glob("*.toml")):
        try:
            donnees = tomllib.loads(chemin.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise ConfigurationInvalide(f"{chemin} : {type(exc).__name__}") from None
        for depot, revision in donnees.get("options", {}).get("jeux_hf", {}).items():
            if pins.setdefault(depot, str(revision)) != str(revision):
                raise ConfigurationInvalide(f"{chemin} : {depot} épinglé à deux révisions")
    inconnus = [depot for depot in depots if depot not in pins]
    if inconnus:
        raise ConfigurationInvalide(
            f"jeu absent de [options.jeux_hf] : {', '.join(inconnus)} "
            f"(connus : {', '.join(sorted(pins)) or 'aucun'})"
        )
    return {depot: pins[depot] for depot in depots} if depots else pins


def dossier_depot(hf_home: str | Path, depot: str) -> Path:
    """`<HF_HOME>/hub/datasets--<org>--<nom>`."""
    return Path(hf_home) / "hub" / f"datasets--{depot.replace('/', '--')}"


def ecrire_refs_main(hf_home: str | Path, depot: str, revision: str) -> bool:
    """Pointe `refs/main` sur `revision` ; vrai si le fichier a changé."""
    refs = dossier_depot(hf_home, depot) / "refs" / "main"
    if refs.is_file() and refs.read_text(encoding="utf-8").strip() == revision:
        return False
    refs.parent.mkdir(parents=True, exist_ok=True)
    refs.write_text(revision, encoding="utf-8")
    return True


def _snapshot_present(hf_home: str | Path, depot: str, revision: str) -> bool:
    snapshot = dossier_depot(hf_home, depot) / "snapshots" / revision
    return snapshot.is_dir() and any(snapshot.iterdir())


_SCRIPT_CONTROLE = """
import json, sys
from datasets import get_dataset_config_names, load_dataset
resultat = {}
for depot, revision in json.loads(sys.argv[1]).items():
    try:
        for nom in get_dataset_config_names(depot, revision=revision):
            load_dataset(depot, nom, revision=revision)
        resultat[depot] = None
    except Exception as exc:
        lignes = str(exc).splitlines()
        resultat[depot] = f"{type(exc).__name__} : {lignes[0] if lignes else ''}"
print("RESULTAT=" + json.dumps(resultat))
"""


def verifier_hors_ligne(pins: Mapping[str, str]) -> dict[str, str | None]:
    """Relit chaque jeu dans un sous-processus hors ligne : dépôt -> erreur, ou `None`."""
    if not pins:
        return {}
    env = {**env_sous_processus(), **ENV_HORS_LIGNE, "PYTHONUTF8": "1"}
    fin = subprocess.run(
        [sys.executable, "-c", _SCRIPT_CONTROLE, json.dumps(dict(pins))],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    for ligne in reversed(fin.stdout.splitlines()):
        if ligne.startswith("RESULTAT="):
            return dict(json.loads(ligne.removeprefix("RESULTAT=")))
    motif = (fin.stderr.strip().splitlines() or ["aucune sortie"])[-1]
    return {depot: f"contrôle hors ligne impossible : {motif}" for depot in pins}


def _telecharger(depot: str, revision: str) -> None:
    from huggingface_hub import snapshot_download

    snapshot_download(depot, repo_type="dataset", revision=revision)


def _charger(depot: str, revision: str) -> int:
    """Charge chaque configuration en ligne ; rend leur nombre."""
    from datasets import get_dataset_config_names, load_dataset

    noms = get_dataset_config_names(depot, revision=revision)
    for nom in noms:
        load_dataset(depot, nom, revision=revision)
    return len(noms)


def executer(
    pins: Mapping[str, str],
    hf_home: str | Path,
    *,
    consigner: Consigner = lambda _ligne: None,
    telecharger: Callable[[str, str], Any] | None = None,
    charger: Callable[[str, str], int] | None = None,
    verifier: Verifier | None = None,
) -> None:
    """Installe les jeux de `pins` dans le cache de `hf_home`, puis les contrôle hors ligne.

    Une ligne `consigner` par jeu : `deja-present` (lisible hors ligne, `refs/main` à la
    bonne révision, rien retéléchargé) ou `telecharge`. `CacheHorsLigneInvalide` si un jeu
    n'est pas relisible hors ligne à la fin.
    """
    telecharger = telecharger or _telecharger
    charger = charger or _charger
    verifier = verifier or verifier_hors_ligne
    avant = verifier(pins)
    a_faire: dict[str, str] = {}
    for depot, revision in pins.items():
        refs = dossier_depot(hf_home, depot) / "refs" / "main"
        complet = (
            avant.get(depot) is None
            and _snapshot_present(hf_home, depot, revision)
            and refs.is_file()
            and refs.read_text(encoding="utf-8").strip() == revision
        )
        if complet:
            consigner(_ligne(depot, revision, "deja-present", hf_home))
        else:
            a_faire[depot] = revision
    for depot, revision in a_faire.items():
        if not _snapshot_present(hf_home, depot, revision):
            telecharger(depot, revision)
        ecrire_refs_main(hf_home, depot, revision)
        charger(depot, revision)
        consigner(_ligne(depot, revision, "telecharge", hf_home))
    apres = verifier(a_faire)
    echecs = {depot: erreur for depot, erreur in apres.items() if erreur is not None}
    if echecs:
        detail = "; ".join(f"{d} ({pins[d][:8]}) : {e}" for d, e in echecs.items())
        raise CacheHorsLigneInvalide(f"cache HF illisible hors ligne : {detail}")


def _ligne(depot: str, revision: str, statut: str, hf_home: str | Path) -> dict[str, Any]:
    return {
        "depot": depot,
        "revision": revision,
        "statut": statut,
        "octets": 0,
        "destination": str(dossier_depot(hf_home, depot)),
    }


__all__ = ["CacheHorsLigneInvalide", "executer", "lire_pins", "verifier_hors_ligne"]
