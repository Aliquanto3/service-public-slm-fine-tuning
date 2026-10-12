"""Serveur llama factice (stdlib `http.server`), en thread ou en script.

Routes : `/health`, `/v1/chat/completions` (SSE), `/tokenize`, `/apply-template`,
`/v1/embeddings`. Chaque requête est enregistrée (`requetes` : méthode, chemin, corps).

En script, pour les tests de `ServeurLlama` :
`python serveur_factice.py --port N [--mourir] [--sante CODE] [arguments llama ignorés]`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

DIMENSION = 1024


def morceau(
    contenu: str | None = None,
    *,
    tool_calls: list[dict[str, Any]] | None = None,
    finish_reason: str | None = None,
) -> dict[str, Any]:
    """Chunk SSE OpenAI d'un seul choix."""
    delta: dict[str, Any] = {}
    if contenu is not None:
        delta["content"] = contenu
    if tool_calls is not None:
        delta["tool_calls"] = tool_calls
    return {"choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}]}


def morceau_usage(prompt: int = 7, completion: int = 3) -> dict[str, Any]:
    """Dernier chunk (`choices` vide) porteur de l'usage."""
    return {
        "choices": [],
        "usage": {
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "total_tokens": prompt + completion,
        },
    }


def flux_texte(*jetons: str, raison: str = "stop", done: bool = True) -> list[Any]:
    """Scénario SSE : jetons, `finish_reason`, usage, puis `[DONE]`."""
    morceaux: list[Any] = [morceau(jeton) for jeton in jetons]
    morceaux.append(morceau(finish_reason=raison))
    morceaux.append(morceau_usage(completion=len(jetons)))
    if done:
        morceaux.append("[DONE]")
    return morceaux


def vecteur(texte: str, dimension: int = DIMENSION) -> list[float]:
    """Vecteur déterministe, non normalisé, tiré du SHA-256 de `texte`."""
    graine = hashlib.sha256(texte.encode("utf-8")).digest()
    return [((graine[i % 32] + i) % 17) - 8.0 + 0.5 for i in range(dimension)]


@dataclass
class Scenario:
    """Réponses du serveur, modifiables entre deux requêtes."""

    sante: int = 200
    statut_chat: int = 200
    corps_erreur: str = '{"error":{"code":400,"message":"requête refusée"}}'
    chat: list[Any] = field(default_factory=lambda: flux_texte("Bon", "jour"))
    """Morceaux SSE : dict (JSON), chaîne brute (`[DONE]`)."""
    corps_tronque: bool = False
    """Annonce un `Content-Length` plus grand que le flux envoyé (corps coupé)."""
    embeddings: Callable[[list[str]], list[Any]] | None = None
    """`textes -> data` ; défaut : `vecteur(texte)` par texte, index dans l'ordre inverse."""
    tokens: Callable[[str], list[int]] = lambda texte: list(range(len(texte.split())))


class ServeurFactice:
    """Serveur HTTP en thread sur `127.0.0.1` ; `requetes` enregistre les appels."""

    def __init__(self, port: int = 0, scenario: Scenario | None = None) -> None:
        self.scenario = scenario or Scenario()
        self.requetes: list[tuple[str, str, Any]] = []
        self._serveur = ThreadingHTTPServer(("127.0.0.1", port), _fabrique(self))
        self._serveur.daemon_threads = True
        self._thread: threading.Thread | None = None

    @property
    def port(self) -> int:
        return int(self._serveur.server_address[1])

    def demarrer(self) -> ServeurFactice:
        self._thread = threading.Thread(
            target=self._serveur.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True
        )
        self._thread.start()
        return self

    def arreter(self) -> None:
        self._serveur.shutdown()
        self._serveur.server_close()

    def corps(self, chemin: str) -> list[Any]:
        """Corps JSON des requêtes reçues sur `chemin`."""
        return [corps for _, c, corps in self.requetes if c == chemin]

    def __enter__(self) -> ServeurFactice:
        return self.demarrer()

    def __exit__(self, *exc: object) -> None:
        self.arreter()


def _fabrique(serveur: ServeurFactice) -> type[BaseHTTPRequestHandler]:
    class Gestionnaire(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
            return None

        def _json(self, statut: int, objet: Any) -> None:
            donnees = json.dumps(objet).encode("utf-8")
            self.send_response(statut)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(donnees)))
            self.end_headers()
            self.wfile.write(donnees)

        def do_GET(self) -> None:
            serveur.requetes.append(("GET", self.path, None))
            if self.path == "/health":
                code = serveur.scenario.sante
                self._json(code, {"status": "ok" if code == 200 else "loading"})
            else:
                self._json(404, {"error": "inconnu"})

        def do_POST(self) -> None:
            longueur = int(self.headers.get("Content-Length") or 0)
            corps = json.loads(self.rfile.read(longueur) or b"null")
            serveur.requetes.append(("POST", self.path, corps))
            scenario = serveur.scenario
            if self.path == "/v1/chat/completions":
                if scenario.statut_chat != 200:
                    donnees = scenario.corps_erreur.encode("utf-8")
                    self.send_response(scenario.statut_chat)
                    self.send_header("Content-Length", str(len(donnees)))
                    self.end_headers()
                    self.wfile.write(donnees)
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                if scenario.corps_tronque:
                    # Longueur annoncée jamais atteinte : coupure du corps en plein flux.
                    self.send_header("Content-Length", "1000000")
                self.end_headers()
                for element in scenario.chat:
                    texte = element if isinstance(element, str) else json.dumps(element)
                    self.wfile.write(f"data: {texte}\n\n".encode())
                    self.wfile.flush()
            elif self.path == "/apply-template":
                rendu = "".join(
                    f"<|{m.get('role')}|>{m.get('content')}\n" for m in corps["messages"]
                )
                if corps.get("tools"):
                    rendu += f"<|outils|>{json.dumps(corps['tools'])}\n"
                self._json(200, {"prompt": rendu})
            elif self.path == "/tokenize":
                self._json(200, {"tokens": scenario.tokens(corps["content"])})
            elif self.path == "/v1/embeddings":
                textes = corps["input"]
                if scenario.embeddings is not None:
                    data = scenario.embeddings(textes)
                else:
                    data = [{"index": i, "embedding": vecteur(t)} for i, t in enumerate(textes)][
                        ::-1
                    ]
                self._json(200, {"data": data, "model": "factice"})
            else:
                self._json(404, {"error": "inconnu"})

    return Gestionnaire


def principal(arguments: list[str]) -> int:
    analyseur = argparse.ArgumentParser(allow_abbrev=False)
    analyseur.add_argument("--port", type=int, required=True)
    analyseur.add_argument("--mourir", action="store_true")
    analyseur.add_argument("--sante", type=int, default=200)
    options, ignores = analyseur.parse_known_args(arguments)
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    print(f"serveur factice : arguments ignorés {ignores}", flush=True)
    if options.mourir:
        print("serveur factice : mort volontaire au démarrage", flush=True)
        return 3
    serveur = ServeurFactice(options.port, Scenario(sante=options.sante))
    print(f"serveur factice : écoute sur {options.port}", flush=True)
    serveur._serveur.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
