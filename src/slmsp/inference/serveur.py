"""Seul lanceur llama.cpp (AD-6) : `llama-server`, `llama-quantize`, `convert_hf_to_gguf.py`.

Binaires : `<vendor>/llama.cpp/<tag>/bin-<variante>/`, avec `<vendor>` =
`SLMSP_VENDOR_DIR` s'il est défini (une copie de travail pointe le `vendor/` du dépôt
principal), sinon `<racine du projet>/vendor`. Le tag et les empreintes viennent de
`config/llamacpp.toml` ; un fichier listé dans `binaires` est vérifié par son SHA-256
avant son premier lancement (une fois par processus). Rien n'est jamais téléchargé ici.

`ServeurLlama` lance un serveur de génération (`--jinja`) ou d'embedding (`--embedding`)
sur `127.0.0.1` et un port libre, avec les paramètres de `config/modeles/<slug>.toml`,
dans un Job Object (`processus.lancer`). La variante `cuda` tient `verrou_gpu()` pendant
toute la vie du serveur, sauf si l'appelant le détient déjà (`prendre_verrou_gpu=False`).
"""

from __future__ import annotations

import json
import os
import re
import socket
import sys
import time
from contextlib import ExitStack
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Final, Literal, get_args

from slmsp.core.artefacts import ArtefactExistant
from slmsp.core.canonique import sha256_fichier
from slmsp.core.config import charger_toml, dossier_modeles, env_sous_processus, racine_projet
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas.config_llamacpp import ConfigLlamacpp
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.core.var import dossier_var, verrou_gpu
from slmsp.inference import processus
from slmsp.inference.client import ClientLlama
from slmsp.inference.embedding import EmbedderLlama
from slmsp.inference.processus import ErreurInference, lire_fin
from slmsp.net import client_local

Variante = Literal["cpu", "cuda"]
VARIANTES: Final = get_args(Variante)

HOTE: Final = "127.0.0.1"

DELAI_DEMARRAGE: Final = 180.0
"""Attente maximale de `/health` = 200 après le lancement (secondes) : un gros GGUF sur
disque lent se charge en plusieurs dizaines de secondes (Granite 1B : 1,7 s)."""

DELAI_ARRET: Final = 10.0
"""Attente maximale de la fin du serveur après sa terminaison (secondes)."""

INTERVALLE_SONDE: Final = 0.25
"""Pause entre deux sondes de `/health` pendant le démarrage (secondes)."""

DELAI_SONDE: Final = 5.0
"""Délai d'une requête `/health` (secondes)."""

DELAI_VERSION: Final = 60.0
"""Délai de `llama-server --version` (secondes)."""

_MOTIF_BUILD = re.compile(r"\(build (\d+)")
_SLUG = re.compile(r"[a-z0-9.-]+")

_empreintes_verifiees: set[tuple[str, str]] = set()
"""(chemin résolu, SHA attendu) déjà vérifiés par ce processus."""


# --- Configuration et binaires ---------------------------------------------------------------


def dossier_vendor() -> Path:
    """`SLMSP_VENDOR_DIR` s'il est défini, sinon `<racine du projet>/vendor`."""
    valeur = os.environ.get("SLMSP_VENDOR_DIR", "").strip()
    dossier = Path(valeur).expanduser() if valeur else racine_projet() / "vendor"
    return dossier.resolve()


def charger_config_llamacpp() -> ConfigLlamacpp:
    """`config/llamacpp.toml` (lève `ConfigurationInvalide`)."""
    return charger_toml(racine_projet() / "config" / "llamacpp.toml", ConfigLlamacpp)


def charger_config_modele(slug: str) -> ConfigModele:
    """`config/modeles/<slug>.toml` (lève `ConfigurationInvalide`)."""
    _verifier_slug(slug)
    return charger_toml(racine_projet() / "config" / "modeles" / f"{slug}.toml", ConfigModele)


def _verifier_slug(slug: str) -> None:
    if not isinstance(slug, str) or not _SLUG.fullmatch(slug) or slug.strip(".") != slug:
        raise ConfigurationInvalide(f"slug de modèle invalide : {slug!r}")


def _verifier_variante(variante: str) -> None:
    if variante not in VARIANTES:
        raise ValueError(f"variante inconnue : {variante!r} (attendu : {', '.join(VARIANTES)})")


def dossier_llamacpp(config: ConfigLlamacpp | None = None) -> Path:
    """`<vendor>/llama.cpp/<tag>/`."""
    config = charger_config_llamacpp() if config is None else config
    return dossier_vendor() / "llama.cpp" / config.tag


def verifier_fichier(relatif: str, config: ConfigLlamacpp | None = None) -> Path:
    """Chemin de `<vendor>/llama.cpp/<tag>/<relatif>`, vérifié s'il est listé.

    Lève `ConfigurationInvalide` si le fichier manque ou si son SHA-256 diffère de celui
    de `config.binaires` (vérifié une seule fois par processus).
    """
    config = charger_config_llamacpp() if config is None else config
    chemin = dossier_llamacpp(config) / relatif
    if not chemin.is_file():
        raise ConfigurationInvalide(
            f"fichier llama.cpp absent : {chemin} (installer le tag {config.tag} par "
            "`slmsp fetch llamacpp`, ou définir SLMSP_VENDOR_DIR)"
        )
    attendu = config.binaires.get(relatif)
    if attendu is not None:
        _verifier_empreinte(chemin, attendu)
    return chemin


def _verifier_empreinte(chemin: Path, attendu: str) -> None:
    cle = (str(chemin.resolve()), attendu)
    if cle in _empreintes_verifiees:
        return
    if not chemin.is_file():
        raise ConfigurationInvalide(f"fichier llama.cpp absent : {chemin} ; aucun lancement")
    obtenu = sha256_fichier(chemin)
    if obtenu != attendu:
        raise ConfigurationInvalide(
            f"{chemin} : SHA-256 inattendu ({obtenu}, attendu {attendu}) ; aucun lancement"
        )
    _empreintes_verifiees.add(cle)


def binaire(nom: str, variante: Variante = "cpu", *, config: ConfigLlamacpp | None = None) -> Path:
    """Chemin vérifié de `bin-<variante>/<nom>.exe` (ex. `binaire("llama-server", "cuda")`).

    Les autres fichiers de `config.binaires` sous `bin-<variante>/` (DLL chargées par le
    binaire, ex. `bin-cuda/ggml-cuda.dll`) sont vérifiés eux aussi, une fois par processus.
    """
    _verifier_variante(variante)
    if sys.platform == "win32" and not nom.lower().endswith(".exe"):
        nom += ".exe"
    config = charger_config_llamacpp() if config is None else config
    chemin = verifier_fichier(f"bin-{variante}/{nom}", config)
    base = dossier_llamacpp(config)
    for relatif, attendu in sorted(config.binaires.items()):
        if relatif.startswith(f"bin-{variante}/"):
            _verifier_empreinte(base / relatif, attendu)
    return chemin


def version(variante: Variante = "cpu", *, config: ConfigLlamacpp | None = None) -> str:
    """Tag du binaire `llama-server` (`b<build>`), lu par `llama-server --version`."""
    executable = binaire("llama-server", variante, config=config)
    code, sortie = processus.executer(
        [executable, "--version"], delai=DELAI_VERSION, role="version"
    )
    trouve = _MOTIF_BUILD.search(sortie)
    if trouve is None:
        raise ErreurInference(
            f"{executable} --version (code {code}) : numéro de build introuvable dans :\n"
            f"{sortie[-processus.TAILLE_FIN_JOURNAL :]}"
        )
    return f"b{trouve.group(1)}"


# --- Conversion et quantification ------------------------------------------------------------


@dataclass(frozen=True)
class Commande:
    """Ligne de commande et environnement d'un outil llama.cpp."""

    arguments: list[str]
    env: dict[str, str]


def commande_conversion(
    dossier_hf: str | os.PathLike[str],
    sortie: str | os.PathLike[str],
    *,
    type_sortie: str = "bf16",
    python: str | os.PathLike[str] | None = None,
    config: ConfigLlamacpp | None = None,
) -> Commande:
    """`convert_hf_to_gguf.py` de `src/` du tag, `PYTHONPATH` préfixé par `src/gguf-py`.

    `python` vaut l'interpréteur courant par défaut (il doit disposer des dépendances du
    script : torch, transformers…).
    """
    config = charger_config_llamacpp() if config is None else config
    script = verifier_fichier("src/convert_hf_to_gguf.py", config)
    gguf_py = dossier_llamacpp(config) / "src" / "gguf-py"
    if not gguf_py.is_dir():
        raise ConfigurationInvalide(f"paquet gguf-py absent : {gguf_py}")
    env = env_sous_processus()
    existant = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(p for p in (str(gguf_py), existant) if p)
    arguments = [
        os.fspath(python) if python is not None else sys.executable,
        str(script),
        os.fspath(dossier_hf),
        "--outfile",
        os.fspath(sortie),
        "--outtype",
        type_sortie,
    ]
    return Commande(arguments, env)


def commande_quantification(
    entree: str | os.PathLike[str],
    sortie: str | os.PathLike[str],
    type_quantification: str,
    *,
    variante: Variante = "cpu",
    config: ConfigLlamacpp | None = None,
) -> Commande:
    """`llama-quantize <entree> <sortie> <type>` de `bin-<variante>/`."""
    executable = binaire("llama-quantize", variante, config=config)
    arguments = [str(executable), os.fspath(entree), os.fspath(sortie), type_quantification]
    return Commande(arguments, env_sous_processus())


def _chemin_partiel(sortie: Path) -> Path:
    return sortie.with_name(sortie.name + ".part")


def _verifier_sortie_libre(sortie: Path) -> Path:
    partiel = _chemin_partiel(sortie)
    for chemin in (sortie, partiel):
        if chemin.exists():
            raise ArtefactExistant(f"{chemin} existe déjà : un artefact n'est jamais réécrit")
    sortie.parent.mkdir(parents=True, exist_ok=True)
    return partiel


def _executer_vers(
    nom: str,
    commande: Commande,
    sortie: Path,
    partiel: Path,
    *,
    delai: float | None,
    journal: Path | None,
) -> Path:
    code, texte = processus.executer(
        commande.arguments, delai=delai, role="outil", journal=journal, env=commande.env
    )
    if code != 0 or not partiel.is_file():
        raise ErreurInference(
            f"{nom} : échec (code {code}) ; {partiel} laissé en place s'il existe ; "
            "fin de la sortie :\n"
            f"{texte[-processus.TAILLE_FIN_JOURNAL :]}"
        )
    os.rename(partiel, sortie)  # sans remplacement : `sortie` absente a été vérifiée
    return sortie


def convertir_hf_vers_gguf(
    dossier_hf: str | os.PathLike[str],
    sortie: str | os.PathLike[str],
    *,
    type_sortie: str = "bf16",
    python: str | os.PathLike[str] | None = None,
    delai: float | None = None,
    journal: str | os.PathLike[str] | None = None,
    config: ConfigLlamacpp | None = None,
) -> Path:
    """Convertit un dossier Hugging Face en GGUF `sortie` (écrit d'abord en `.part`).

    Lève `ArtefactExistant` si `sortie` ou `sortie.part` existe, `ErreurInference` si la
    conversion échoue.
    """
    sortie = Path(sortie)
    partiel = _verifier_sortie_libre(sortie)
    commande = commande_conversion(
        dossier_hf, partiel, type_sortie=type_sortie, python=python, config=config
    )
    return _executer_vers(
        "convert_hf_to_gguf.py",
        commande,
        sortie,
        partiel,
        delai=delai,
        journal=None if journal is None else Path(journal),
    )


def quantifier(
    entree: str | os.PathLike[str],
    sortie: str | os.PathLike[str],
    type_quantification: str,
    *,
    variante: Variante = "cpu",
    delai: float | None = None,
    journal: str | os.PathLike[str] | None = None,
    config: ConfigLlamacpp | None = None,
) -> Path:
    """Quantifie le GGUF `entree` en `sortie` (écrit d'abord en `.part`).

    Lève `ArtefactExistant` si `sortie` ou `sortie.part` existe, `ErreurInference` si
    `llama-quantize` échoue.
    """
    sortie = Path(sortie)
    partiel = _verifier_sortie_libre(sortie)
    commande = commande_quantification(
        entree, partiel, type_quantification, variante=variante, config=config
    )
    return _executer_vers(
        "llama-quantize",
        commande,
        sortie,
        partiel,
        delai=delai,
        journal=None if journal is None else Path(journal),
    )


# --- Serveur ---------------------------------------------------------------------------------


def port_libre() -> int:
    """Port TCP libre de `127.0.0.1`, choisi par le système."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as prise:
        prise.bind((HOTE, 0))
        return int(prise.getsockname()[1])


class ServeurLlama:
    """`llama-server` géré, en génération ou en embedding selon `config.embedding`.

    Le GGUF est `gguf` s'il est donné, sinon `<dossier_modeles()>/<slug>/gguf/<fichier>`.
    `chat_template_force` exige `slug` (`<dossier_modeles()>/<slug>/chat_template.jinja`).
    """

    def __init__(
        self,
        config: ConfigModele,
        variante: Variante = "cpu",
        *,
        slug: str | None = None,
        gguf: str | os.PathLike[str] | None = None,
        config_llamacpp: ConfigLlamacpp | None = None,
        prendre_verrou_gpu: bool = True,
        delai_demarrage: float = DELAI_DEMARRAGE,
        journal: str | os.PathLike[str] | None = None,
    ) -> None:
        _verifier_variante(variante)
        if slug is None and gguf is None:
            raise ValueError("slug ou gguf requis")
        if slug is not None:
            _verifier_slug(slug)
        if config.chat_template_force and slug is None:
            raise ValueError("chat_template_force exige le slug du modèle")
        self.config = config
        self.variante: Variante = variante
        self.slug = slug
        self._gguf = None if gguf is None else Path(gguf)
        self._config_llamacpp = config_llamacpp
        self.prendre_verrou_gpu = prendre_verrou_gpu
        self.delai_demarrage = delai_demarrage
        self._journal = None if journal is None else Path(journal)
        self._processus: processus.ProcessusGere | None = None
        self._pile: ExitStack | None = None
        self._port: int | None = None
        self._client: ClientLlama | None = None
        self._embedder: EmbedderLlama | None = None

    # -- Paramètres --

    @property
    def role(self) -> str:
        return "embedding" if self.config.embedding else "generation"

    @property
    def config_llamacpp(self) -> ConfigLlamacpp:
        if self._config_llamacpp is None:
            self._config_llamacpp = charger_config_llamacpp()
        return self._config_llamacpp

    @property
    def gguf(self) -> Path:
        if self._gguf is not None:
            return self._gguf
        assert self.slug is not None
        return dossier_modeles() / self.slug / "gguf" / self.config.gguf.fichier

    @property
    def chat_template(self) -> Path | None:
        if not self.config.chat_template_force:
            return None
        assert self.slug is not None
        return dossier_modeles() / self.slug / "chat_template.jinja"

    def programme(self) -> list[str]:
        """Début de la ligne de commande : le binaire `llama-server` vérifié."""
        return [str(binaire("llama-server", self.variante, config=self.config_llamacpp))]

    def arguments(self, port: int) -> list[str]:
        """Ligne de commande complète de `llama-server` pour `port`."""
        config = self.config
        arguments = [
            *self.programme(),
            "--host",
            HOTE,
            "--port",
            str(port),
            "-m",
            str(self.gguf),
            "-c",
            str(config.contexte),
            "-ctk",
            config.cache_kv,
            "-ctv",
            config.cache_kv,
            "--parallel",
            "1",
            "--no-webui",
        ]
        if config.threads is not None:
            arguments += ["-t", str(config.threads)]
        if config.embedding:
            assert config.pooling is not None
            # Lot et micro-lot à la taille du contexte : sinon llama-server refuse une entrée
            # de plus de 512 tokens (micro-lot par défaut).
            contexte = str(config.contexte)
            arguments += ["--embedding", "--pooling", config.pooling]
            arguments += ["-b", contexte, "-ub", contexte]
        else:
            arguments += ["--jinja", "--reasoning", config.reasoning]
            if config.chat_template_kwargs:
                arguments += [
                    "--chat-template-kwargs",
                    json.dumps(config.chat_template_kwargs, ensure_ascii=False),
                ]
            if config.chat_template_force:
                arguments += ["--chat-template-file", str(self.chat_template)]
        return arguments

    # -- Cycle de vie --

    @property
    def demarre(self) -> bool:
        return self._processus is not None

    @property
    def port(self) -> int:
        if self._port is None:
            raise ErreurInference("serveur non démarré")
        return self._port

    @property
    def pid(self) -> int:
        if self._processus is None:
            raise ErreurInference("serveur non démarré")
        return self._processus.pid

    @property
    def journal(self) -> Path | None:
        return self._journal

    def _chemin_journal(self, port: int) -> Path:
        horodatage = datetime.now().strftime("%Y%m%d-%H%M%S")
        return dossier_var() / "journaux" / f"llama-server-{self.role}-{horodatage}-{port}.log"

    def _verifier_fichiers(self) -> None:
        if not self.gguf.is_file():
            raise ConfigurationInvalide(f"GGUF absent : {self.gguf}")
        modele = self.chat_template
        if modele is not None and not modele.is_file():
            raise ConfigurationInvalide(f"chat template forcé absent : {modele}")

    def demarrer(self) -> ServeurLlama:
        """Lance le serveur et attend `/health` = 200 ; lève `ErreurInference` sinon."""
        if self._processus is not None:
            raise ErreurInference(f"serveur déjà démarré (PID {self._processus.pid})")
        processus.nettoyer_orphelins()
        self._verifier_fichiers()
        port = port_libre()
        arguments = self.arguments(port)  # vérifie le binaire avant tout verrou
        pile = ExitStack()
        try:
            if self.variante == "cuda" and self.prendre_verrou_gpu:
                nom = self.slug or self.gguf.name
                pile.enter_context(verrou_gpu(commande=f"llama-server {nom} (cuda)"))
            journal = self._journal or self._chemin_journal(port)
            gere = processus.lancer(
                arguments, role=self.role, port=port, journal=journal, env=env_sous_processus()
            )
            pile.callback(gere.arreter, DELAI_ARRET)
            self._attendre_sante(gere, port, journal)
        except BaseException:
            pile.close()
            raise
        self._journal = journal
        self._processus, self._pile, self._port = gere, pile, port
        return self

    def _attendre_sante(self, gere: processus.ProcessusGere, port: int, journal: Path) -> None:
        echeance = time.monotonic() + self.delai_demarrage
        url = f"http://{HOTE}:{port}/health"
        with client_local(port) as http:
            while True:
                if not gere.vivant:
                    raise ErreurInference(
                        f"llama-server ({self.role}) mort au démarrage (code {gere.code_retour}) "
                        f"; fin du journal {journal} :\n{lire_fin(journal)}"
                    )
                try:
                    if http.get(url, timeout=DELAI_SONDE).status_code == 200:
                        return
                except Exception:  # connexion refusée pendant le chargement
                    pass
                if time.monotonic() >= echeance:
                    raise ErreurInference(
                        f"llama-server ({self.role}) pas prêt après {self.delai_demarrage:g} s, "
                        f"arrêté ; fin du journal {journal} :\n{lire_fin(journal)}"
                    )
                time.sleep(INTERVALLE_SONDE)

    def arreter(self) -> None:
        """Arrête le serveur, ferme les clients et rend le verrou GPU (idempotent)."""
        for ressource in (self._client, self._embedder):
            if ressource is not None:
                ressource.fermer()
        self._client = self._embedder = None
        pile, self._pile = self._pile, None
        self._processus = None
        self._port = None
        if pile is not None:
            pile.close()

    def __enter__(self) -> ServeurLlama:
        return self.demarrer()

    def __exit__(self, *exc: object) -> None:
        self.arreter()

    def description(self) -> dict[str, Any]:
        """Paramètres du serveur pour `run.json` (variante, tag, GGUF, ligne de commande)."""
        description: dict[str, Any] = {
            "role": self.role,
            "variante": self.variante,
            "tag_llamacpp": self.config_llamacpp.tag,
            "slug": self.slug,
            "gguf": self.gguf.name,
            "contexte": self.config.contexte,
            "cache_kv": self.config.cache_kv,
            "threads": self.config.threads,
            "parallel": 1,
        }
        if self.config.embedding:
            description["pooling"] = self.config.pooling
        else:
            description.update(
                reasoning=self.config.reasoning,
                chat_template_kwargs=dict(self.config.chat_template_kwargs),
                chat_template_force=self.config.chat_template_force,
                protocole_outils=self.config.protocole_outils,
            )
        if self._port is not None:
            programme = len(self.programme())
            description["arguments"] = self.arguments(self._port)[programme:]
        return description

    # -- Adaptateurs --

    def client(self) -> ClientLlama:
        """`LlmPort` de ce serveur de génération."""
        if self.config.embedding:
            raise ValueError("serveur d'embedding : utiliser embedder()")
        if self._client is None:
            self._client = ClientLlama(
                self.port,
                protocole_outils=self.config.protocole_outils,
                chat_template_kwargs=self.config.chat_template_kwargs,
                taille_contexte=self.config.contexte,
            )
        return self._client

    def embedder(self) -> EmbedderLlama:
        """`EmbedderPort` de ce serveur d'embedding."""
        if not self.config.embedding:
            raise ValueError("serveur de génération : utiliser client()")
        if self._embedder is None:
            self._embedder = EmbedderLlama(self.port)
        return self._embedder


__all__ = [
    "Commande",
    "DELAI_ARRET",
    "DELAI_DEMARRAGE",
    "ErreurInference",
    "INTERVALLE_SONDE",
    "ServeurLlama",
    "Variante",
    "binaire",
    "charger_config_llamacpp",
    "charger_config_modele",
    "commande_conversion",
    "commande_quantification",
    "convertir_hf_vers_gguf",
    "dossier_llamacpp",
    "dossier_vendor",
    "port_libre",
    "quantifier",
    "verifier_fichier",
    "version",
]
