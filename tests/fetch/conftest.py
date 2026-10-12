"""Doublures du téléchargeur : serveur factice (`httpx2.MockTransport`), réglages, zips.

Aucune requête ne sort : le transport interne du client gardé est un `MockTransport` qui
sert des octets en mémoire (Range et 206, 429 et 5xx scriptés, redirections, coupures).
"""

from __future__ import annotations

import hashlib
import os
import zipfile
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx2  # noqa: TID251 (tests : transport factice de la passerelle)
import pytest

from slmsp import net
from slmsp.fetch.config import ConfigTelechargement
from slmsp.fetch.hf import Telechargeur
from slmsp.net.journal import JournalMemoire


def sha(donnees: bytes) -> str:
    return hashlib.sha256(donnees).hexdigest()


class FluxCoupe(httpx2.SyncByteStream):
    """Corps qui livre `donnees` puis lève `httpx2.ReadError` (coupure de connexion)."""

    def __init__(self, donnees: bytes) -> None:
        self.donnees = donnees

    def __iter__(self) -> Iterator[bytes]:
        if self.donnees:
            yield self.donnees
        raise httpx2.ReadError("connexion coupée")


@dataclass
class Fichier:
    """Ressource servie : contenu, en-têtes en plus, comportement."""

    contenu: bytes = b""
    en_tetes: dict[str, str] = field(default_factory=dict)
    en_tetes_head: dict[str, str] = field(default_factory=dict)
    statut_head: int = 200
    ignorer_range: bool = False
    pannes: list[Any] = field(default_factory=list)
    """Réponses à rendre d'abord, une par requête GET : statut (int), `("coupe", n)` pour
    livrer n octets puis couper, ou `("statut", code, en-têtes)`."""
    redirection: str | None = None
    json: Any = None


@dataclass
class ServeurFactice:
    """Gestionnaire de `MockTransport` : URL → `Fichier`, requêtes reçues."""

    fichiers: dict[str, Fichier] = field(default_factory=dict)
    requetes: list[Any] = field(default_factory=list)

    def servir(self, url: str, contenu: bytes = b"", **options: Any) -> Fichier:
        fichier = Fichier(contenu=contenu, **options)
        self.fichiers[url] = fichier
        return fichier

    def requetes_vers(self, motif: str, methode: str | None = None) -> list[Any]:
        return [
            r
            for r in self.requetes
            if motif in str(r.url) and (methode is None or r.method == methode)
        ]

    def __call__(self, requete: Any) -> Any:
        self.requetes.append(requete)
        fichier = self.fichiers.get(str(requete.url))
        if fichier is None:
            return httpx2.Response(404, request=requete)
        if fichier.redirection is not None:
            return httpx2.Response(302, headers={"Location": fichier.redirection}, request=requete)
        if requete.method == "HEAD":
            return httpx2.Response(
                fichier.statut_head, headers=fichier.en_tetes_head, request=requete
            )
        if fichier.json is not None:
            return httpx2.Response(200, json=fichier.json, request=requete)
        debut = 0
        plage = requete.headers.get("Range")
        if plage and not fichier.ignorer_range:
            debut = int(plage.removeprefix("bytes=").rstrip("-"))
        if fichier.pannes:
            panne = fichier.pannes.pop(0)
            if isinstance(panne, int):
                return httpx2.Response(panne, request=requete)
            if panne[0] == "statut":
                return httpx2.Response(panne[1], headers=panne[2], request=requete)
            morceau = fichier.contenu[debut : debut + panne[1]]
            statut, en_tetes = self._statut(fichier, debut)
            return httpx2.Response(
                statut, headers=en_tetes, stream=FluxCoupe(morceau), request=requete
            )
        statut, en_tetes = self._statut(fichier, debut)
        return httpx2.Response(
            statut, headers=en_tetes, content=fichier.contenu[debut:], request=requete
        )

    @staticmethod
    def _statut(fichier: Fichier, debut: int) -> tuple[int, dict[str, str]]:
        en_tetes = dict(fichier.en_tetes)
        if debut:
            total = len(fichier.contenu)
            en_tetes["Content-Range"] = f"bytes {debut}-{total - 1}/{total}"
            return 206, en_tetes
        return 200, en_tetes


def reglages(**valeurs: Any) -> ConfigTelechargement:
    defaut = {
        "essais": 4,
        "attente_initiale": 1.0,
        "attente_max": 8.0,
        "taille_bloc": 7,
        "seuil_verification_espace": 0,
        "marge_espace": 0,
        "facteur_extraction": 1.0,
    }
    return ConfigTelechargement(**{**defaut, **valeurs})


def ecrire_zip(chemin: Path, membres: dict[str, bytes]) -> bytes:
    """Écrit un zip de `membres` (nom → contenu) et renvoie ses octets."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(chemin, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for nom, contenu in membres.items():
            zf.writestr(nom, contenu)
    return chemin.read_bytes()


@dataclass
class Banc:
    """Serveur factice, journal et fabrique de clients gardés `outillage`."""

    serveur: ServeurFactice
    journal: JournalMemoire
    attentes: list[float]

    def client(self, **options: Any) -> Any:
        return net.client(
            "outillage",
            journal=self.journal,
            transport_interne=httpx2.MockTransport(self.serveur),
            follow_redirects=True,
            **options,
        )

    def telechargeur(
        self, config: ConfigTelechargement | None = None, **options: Any
    ) -> Telechargeur:
        return Telechargeur(
            self.client(),
            config or reglages(),
            attendre=self.attentes.append,
            **options,
        )


@pytest.fixture
def banc() -> Banc:
    return Banc(ServeurFactice(), JournalMemoire(), [])


@pytest.fixture(autouse=True)
def _hf_isole(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Restaure l'environnement HF et la fabrique de `huggingface_hub` après chaque test."""
    for nom in ("HF_HOME", "HF_HUB_DISABLE_TELEMETRY", "WANDB_MODE", "DO_NOT_TRACK"):
        if nom in os.environ:
            monkeypatch.setenv(nom, os.environ[nom])
        else:
            monkeypatch.delenv(nom, raising=False)
    try:
        from huggingface_hub.utils import _http
    except ImportError:
        yield
        return
    monkeypatch.setattr(_http, "_GLOBAL_CLIENT_FACTORY", _http._GLOBAL_CLIENT_FACTORY)
    monkeypatch.setattr(_http, "_GLOBAL_ASYNC_CLIENT_FACTORY", _http._GLOBAL_ASYNC_CLIENT_FACTORY)
    monkeypatch.setattr(_http, "_GLOBAL_CLIENT", None)
    yield


FETCH_TOML = """
[telechargement]
essais = 3
attente_initiale = 0.0
attente_max = 0.0
taille_bloc = 64
seuil_verification_espace = 0
marge_espace = 0
facteur_extraction = 1.0
"""


@pytest.fixture
def cli(banc: Banc, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> SimpleNamespace:
    """Prépare `slmsp fetch` de bout en bout : clients `net` branchés sur le serveur
    factice et le journal du banc, configuration lue sous `tmp_path/config`, poids sous
    `tmp_path/models`, `.env` avec un `HF_TOKEN` factice."""
    import slmsp.fetch.config as module_config

    transport = httpx2.MockTransport(banc.serveur)
    client_original = net.client
    fabrique_originale = net.fabrique_hf

    def client(profil: str, *args: Any, **options: Any) -> Any:
        options.update(journal=banc.journal, transport_interne=transport)
        return client_original(profil, *args, **options)

    def fabrique_hf(**options: Any) -> Any:
        options.update(journal=banc.journal, transport_interne=transport)
        return fabrique_originale(**options)

    monkeypatch.setattr(net, "client", client)
    monkeypatch.setattr(net, "fabrique_hf", fabrique_hf)
    dossier = tmp_path / "config"
    (dossier / "modeles").mkdir(parents=True)
    (dossier / "fetch.toml").write_text(FETCH_TOML, encoding="utf-8")
    monkeypatch.setattr(module_config, "dossier_config", lambda: dossier)
    monkeypatch.setenv("SLMSP_MODELS_DIR", str(tmp_path / "models"))
    env = tmp_path / ".env"
    env.write_text("HF_TOKEN=jeton-factice\n", encoding="utf-8")
    monkeypatch.setenv("SLMSP_ENV_FILE", str(env))
    return SimpleNamespace(
        config=dossier, racine=tmp_path / "racine", models=(tmp_path / "models").resolve()
    )


def lire_run(racine: Path) -> SimpleNamespace:
    """Seul run `fetch` sous `racine` : manifeste, lignes de fichiers, statuts."""
    import json

    (dossier,) = (racine / "runs" / "fetch").iterdir()

    def jsonl(nom: str) -> list[Any]:
        chemin = dossier / nom
        if not chemin.exists():
            return []
        return [json.loads(ligne) for ligne in chemin.read_text(encoding="utf-8").splitlines()]

    return SimpleNamespace(
        dossier=dossier,
        manifeste=json.loads((dossier / "run.json").read_text(encoding="utf-8")),
        fichiers=jsonl("fichiers.jsonl"),
        extractions=jsonl("extractions.jsonl"),
        statuts=[ligne["statut"] for ligne in jsonl("etat.jsonl")],
    )


@pytest.fixture(scope="session")
def outils() -> SimpleNamespace:
    """Aides importables par les modules de test (mode d'import `importlib`)."""
    return SimpleNamespace(sha=sha, reglages=reglages, ecrire_zip=ecrire_zip, lire_run=lire_run)
