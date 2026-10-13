# /// script
# requires-python = ">=3.12"
# dependencies = ["duckdb>=1.1", "openpyxl>=3.1"]
# ///
"""Outil de construction du Jeu d'évaluation maison (piste 2, story 7.1).

Script autonome, hors du paquet `slmsp` (D-nuit-A2-2, A2-20). Lancement :

    uv run --no-project --python 3.12 --with duckdb --with openpyxl \
        python -I eval/outils/construire_jeu.py <commande> [options]

Sous-commandes :

- `sources`     : instantanés des sources réelles (parquet et xlsx Hugging Face épinglés
                  sur une révision, pages des hôtes de la Liste blanche) sous `--dest`,
                  inventoriés dans `<dest>/INDEX.json` ;
- `fiche <id>`  : texte d'une fiche service-public, lu localement (parquet via duckdb,
                  sinon `hf/sp_<id>.json`) ;
- `assembler`   : concatène `eval/construction/<version>/<CODE>.jsonl` dans
                  `eval/jeu/<version>/items.jsonl` (tri par identifiant, UTF-8, LF) ;
- `composition` : écarts des brouillons avec SPEC §2, en Markdown ;
- `rejets`      : taux de rejet par Tâche et par motif, en Markdown ;
- `revue`       : exporte l'échantillon de relecture du manifeste gelé dans `eval/revue/`
                  (JSONL pour les outils, Markdown lisible champ par champ) ;
- `changements` : avant le gel d'une nouvelle version, exporte dans `eval/revue/` les items
                  nouveaux, modifiés (ancienne et nouvelle valeur de chaque champ changé) et
                  retirés par rapport au `items.jsonl` d'une version de référence.

Garde-fous : le client HTTP est en lecture seule (GET, HEAD), en `https` uniquement, et
vérifie l'hôte contre une liste codée (D1.5) avant chaque connexion, y compris à chaque
redirection. duckdb n'ouvre jamais de connexion réseau : on télécharge d'abord des fichiers
entiers, puis on les interroge localement. Rien n'est jamais supprimé ; un fichier présent
n'est pas retéléchargé sans `--force`. Le manifeste relève de `slmsp eval gel`, les
cassettes de `slmsp mcp record`.

Seule la bibliothèque standard est importée au niveau du module ; `duckdb` est importé
à l'usage.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from collections.abc import Callable
from itertools import pairwise
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constantes : SPEC §2, §3, §5.2, §7 bis
# ---------------------------------------------------------------------------
CODES = ("Q", "RD", "CR", "LC", "CO", "RE", "CT", "NR")
TACHES = {
    "Q": "Question",
    "RD": "Recherche de données",
    "CR": "Compte rendu",
    "LC": "Langage clair",
    "CO": "Correction",
    "RE": "Résumé",
    "CT": "Courrier type",
    "NR": "Non-régression",
}
# Libellés acceptés en plus de TACHES (SPEC §2 écrit « Non-régression générale »).
ALIAS_TACHES = {"NR": {"Non-régression générale"}}
DIFFICULTES = ("facile", "moyen", "difficile")
CIBLES = {  # SPEC §2 : (facile, moyen, difficile)
    "Q": (20, 25, 15),
    "RD": (15, 15, 10),
    "CR": (8, 10, 7),
    "LC": (8, 10, 7),
    "CO": (5, 5, 5),
    "RE": (5, 5, 5),
    "CT": (5, 5, 5),
    "NR": (10, 10, 10),
}
CIBLE_Q_SANS_REPONSE = 8
CIBLE_Q_PART_AMORCES = 0.5
CIBLE_RD_VALEURS = 5
CIBLE_RD_REPLI = 4
CIBLE_RD_PRODUCTEURS = 6
CIBLE_CR_LONGUES = 5
SEUIL_CR_LONGUE_MOTS = 4000
THEMES = {  # slug SPEC -> part cible
    "social-autonomie": 0.30,
    "etat-civil-papiers": 0.15,
    "travail-emploi": 0.15,
    "collectivites": 0.15,
    "famille-education-sante": 0.15,
    "fiscalite-locale": 0.10,
}
CODES_THEMATIQUES = ("Q", "RD", "LC", "RE")
VERDICTS = ("accepte", "rejete")
MOTIFS = ("fait_absent_source", "url_morte_ou_differente", "ambigu", "doublon_thematique", "autre")
MODES_RD = ("connecte", "hors-ligne", "repli")
OUTILS_RD = (
    "search_datasets",
    "get_dataset_info",
    "list_dataset_resources",
    "query_resource_data",
    "get_resource_info",
)
LONGUEURS_RE = ("courte", "moyenne", "detaillee")
CORPUS_AMORCES = ("sp_questions_corpus", "assistant_ia_questions_corpus")

CHAMPS_COMMUNS = (
    "id",
    "tache",
    "difficulte",
    "entree",
    "parametres",
    "provenance",
    "licence_source",
    "fictif",
    "version_item",
)
CHAMPS_TACHE: dict[str, tuple[str, ...]] = {
    "Q": ("reponse_reference", "elements_cles", "sources_attendues", "sans_reponse"),
    "RD": ("appels_attendus", "mode", "cassettes", "reponse_reference"),
    "CR": ("participants_reference", "decisions_reference", "actions_reference", "pieges"),
    "LC": ("informations_a_conserver", "termes_juridiques_a_conserver", "kandel_moles_entree"),
    "CO": ("fautes", "texte_corrige_reference"),
    "RE": ("points_cles_reference", "longueur_demandee"),
    "CT": (
        "type_courrier",
        "elements_obligatoires",
        "champs_a_laisser_en_emplacement",
        "valeurs_interdites",
    ),
    "NR": (),  # `reponse_reference` ou `criteres`, contrôlé à part
}
CODES_ENTREE_TEXTE = ("Q", "RD", "NR")
RE_ID = re.compile(r"([A-Z]+)-([0-9]{3,})")  # toujours avec fullmatch

# ---------------------------------------------------------------------------
# Réseau : hôtes autorisés (decisions.md D1.5, addendum §B)
# ---------------------------------------------------------------------------
HF = "https://huggingface.co"
LISTE_BLANCHE = frozenset(
    {
        "mcp.data.gouv.fr",
        "www.data.gouv.fr",
        "www.service-public.gouv.fr",
        "www.service-public.fr",
        "www.legifrance.gouv.fr",
        "entreprendre.service-public.gouv.fr",
        "entreprendre.service-public.fr",
        "lannuaire.service-public.fr",
    }
)
HOTES_EXACTS = frozenset({"huggingface.co"}) | LISTE_BLANCHE
SUFFIXES_AUTORISES = (".hf.co", ".huggingface.co")  # CDN et hôtes Xet de Hugging Face
METHODES_AUTORISEES = frozenset({"GET", "HEAD"})
STATUTS_REDIRECTION = frozenset({301, 302, 303, 307, 308})
MAX_REDIRECTIONS = 10
DELAI_S = 60.0
TAILLE_BLOC = 1 << 20
USER_AGENT = "construire_jeu/1.0 (jeu d'evaluation slmsp ; lecture seule)"

# Sources Hugging Face (vérifiées le 2026-10-12, tree API).
LEGI_CODES = {
    "crpa": "code_des_relations_entre_le_public_et_l_administration",
    "casf": "code_de_l_action_sociale_et_des_familles",
    "cgct": "code_general_des_collectivites_territoriales",
    "civil": "code_civil",
    "ccp": "code_de_la_commande_publique",
}
QUOI = ("service-public", "catalogue", "legi", "questions")


class ErreurOutil(Exception):
    """Erreur attendue, rapportée sur stderr avec un code de sortie non nul."""


class RequeteRefusee(ErreurOutil):
    """Requête refusée avant toute connexion (méthode, schéma ou hôte)."""


class HoteRefuse(RequeteRefusee):
    """Hôte (ou schéma, port) hors de la liste codée D1.5."""


class ErreurHTTP(ErreurOutil):
    def __init__(self, statut: int, url: str, retry_after: str | None = None):
        super().__init__(f"HTTP {statut} sur {url}")
        self.statut = statut
        self.url = url
        self.retry_after = retry_after

    @property
    def reessayable(self) -> bool:
        return self.statut == 429 or self.statut >= 500


class ErreurTelechargement(ErreurOutil):
    pass


def hote_autorise(hote: str) -> bool:
    hote = hote.lower().rstrip(".")
    return hote in HOTES_EXACTS or any(hote.endswith(s) for s in SUFFIXES_AUTORISES)


def verifier_requete(url: str, methode: str) -> None:
    """Contrôle unique, appelé avant chaque connexion et à chaque saut de redirection."""
    if methode not in METHODES_AUTORISEES:
        raise RequeteRefusee(f"méthode refusée : {methode} (lecture seule : GET, HEAD)")
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        raise HoteRefuse(f"schéma refusé (https uniquement) : {url}")
    try:
        port = parts.port
    except ValueError as exc:
        raise HoteRefuse(f"port invalide : {url}") from exc
    if port not in (None, 443) or parts.username or parts.password:
        raise HoteRefuse(f"URL refusée (port ou identifiants) : {url}")
    if not parts.hostname or not hote_autorise(parts.hostname):
        raise HoteRefuse(f"hôte refusé (hors liste D1.5) : {parts.hostname or url}")


class _SansRedirection(urllib.request.HTTPRedirectHandler):
    """Rend la réponse 3xx telle quelle : les redirections sont suivies à la main."""

    def http_error_302(self, req, fp, code, msg, headers):
        return fp

    http_error_301 = http_error_303 = http_error_307 = http_error_308 = http_error_302


def _ouvreur_urllib(req: urllib.request.Request, delai: float):
    # ProxyHandler({}) : les variables HTTP(S)_PROXY sont ignorées (aucun hôte hors liste).
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _SansRedirection)
    try:
        return opener.open(req, timeout=delai)
    except urllib.error.HTTPError as exc:  # réponse 4xx/5xx : traitée comme une réponse
        return exc


def _decoder_json(corps: bytes | str, origine: Any) -> Any:
    try:
        return json.loads(corps.decode("utf-8-sig") if isinstance(corps, bytes) else corps)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ErreurOutil(f"JSON illisible ({origine}) : {exc}") from exc


def _statut(rep: Any) -> int:
    statut = getattr(rep, "status", None)
    return int(statut if statut is not None else rep.getcode())


def _fermer(rep: Any) -> None:
    fermer = getattr(rep, "close", None)
    if fermer:
        fermer()


class ClientHTTP:
    """Client en lecture seule. `ouvreur(Request, delai)` est remplaçable dans les tests."""

    def __init__(
        self,
        ouvreur: Callable | None = None,
        dormir: Callable[[float], None] = time.sleep,
        tentatives: int = 4,
        attente: float = 2.0,
        attente_max: float = 60.0,
    ):
        if tentatives < 1:
            raise ValueError("tentatives >= 1")
        self.ouvreur = ouvreur or _ouvreur_urllib
        self.dormir = dormir
        self.tentatives = tentatives
        self.attente = attente
        self.attente_max = attente_max

    # -- point de passage unique -------------------------------------------------
    def ouvrir(self, url: str, methode: str = "GET") -> tuple[Any, str]:
        """Ouvre `url` en suivant les redirections ; renvoie (réponse 2xx, URL finale)."""
        for _ in range(MAX_REDIRECTIONS + 1):
            verifier_requete(url, methode)
            req = urllib.request.Request(url, method=methode, headers={"User-Agent": USER_AGENT})
            rep = self.ouvreur(req, DELAI_S)
            statut = _statut(rep)
            if statut in STATUTS_REDIRECTION:
                cible = rep.headers.get("Location")
                _fermer(rep)
                if not cible:
                    raise ErreurHTTP(statut, url)
                url = urllib.parse.urljoin(url, cible)
                continue
            if 200 <= statut < 300:
                return rep, url
            retry_after = rep.headers.get("Retry-After") if rep.headers else None
            _fermer(rep)
            raise ErreurHTTP(statut, url, retry_after)
        raise ErreurOutil(f"trop de redirections depuis {url}")

    def _avec_reprises(self, action: Callable[[], Any], description: str) -> Any:
        for essai in range(1, self.tentatives + 1):
            try:
                return action()
            except RequeteRefusee:
                raise
            except (ErreurHTTP, OSError, http.client.HTTPException) as exc:
                if isinstance(exc, ErreurHTTP) and not exc.reessayable:
                    raise
                if essai == self.tentatives:
                    raise ErreurTelechargement(
                        f"{description} : échec après {essai} tentatives ({exc})"
                    ) from exc
                attente = min(self.attente_max, self.attente * 2 ** (essai - 1))
                if isinstance(exc, ErreurHTTP) and exc.retry_after and exc.retry_after.isdigit():
                    attente = max(attente, min(float(exc.retry_after), self.attente_max))
                print(
                    f"[reprise] {description} : {exc} ; nouvelle tentative dans {attente:.0f} s",
                    file=sys.stderr,
                )
                self.dormir(attente)
        raise AssertionError("inaccessible")

    # -- lectures ------------------------------------------------------------------
    def lire(self, url: str) -> tuple[bytes, Any]:
        def action():
            rep, _ = self.ouvrir(url)
            try:
                return rep.read(), rep.headers
            finally:
                _fermer(rep)

        return self._avec_reprises(action, url)

    def lire_json(self, url: str) -> Any:
        return _decoder_json(self.lire(url)[0], url)

    def telecharger(
        self,
        url: str,
        cible: Path,
        *,
        force: bool = False,
        taille: int | None = None,
        sha256: str | None = None,
        avant_remplacement: Callable[[], None] | None = None,
    ) -> dict | None:
        """Écrit `url` dans `cible` (via `.part` puis renommage). None si déjà présent.

        `avant_remplacement` est appelé après la vérification du `.part`, juste avant le
        renommage (archivage de l'ancien instantané)."""
        if cible.exists() and not force:
            return None
        cible.parent.mkdir(parents=True, exist_ok=True)
        part = cible.with_name(cible.name + ".part")

        def action():
            rep, finale = self.ouvrir(url)
            empreinte, n = hashlib.sha256(), 0
            try:
                with open(part, "wb") as f:
                    while bloc := rep.read(TAILLE_BLOC):
                        f.write(bloc)
                        empreinte.update(bloc)
                        n += len(bloc)
            finally:
                _fermer(rep)
            return n, empreinte.hexdigest(), finale

        n, sha, finale = self._avec_reprises(action, url)
        if taille is not None and n != taille:
            raise ErreurTelechargement(f"{url} : taille {n} ≠ {taille} attendue ({part} conservé)")
        if sha256 is not None and sha != sha256:
            raise ErreurTelechargement(f"{url} : SHA-256 inattendu ({part} conservé)")
        if avant_remplacement:
            avant_remplacement()
        os.replace(part, cible)
        return {"taille": n, "sha256": sha, "url_finale": finale}


# ---------------------------------------------------------------------------
# INDEX.json
# ---------------------------------------------------------------------------
def _ecrire_texte(chemin: Path, texte: str) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    part = chemin.with_name(chemin.name + ".part")
    part.write_text(texte, encoding="utf-8", newline="\n")
    os.replace(part, chemin)


def charger_index(dest: Path) -> dict:
    chemin = dest / "INDEX.json"
    if chemin.exists():
        index = _decoder_json(chemin.read_bytes(), chemin)
        if not (
            isinstance(index, dict)
            and isinstance(index.get("fichiers"), list)
            and all(isinstance(e, dict) and "chemin" in e for e in index["fichiers"])
        ):
            raise ErreurOutil(
                f"{chemin} : forme inattendue (objet avec une liste `fichiers` attendu)"
            )
        return index
    return {
        "description": "Instantanés des sources du Jeu d'évaluation (construire_jeu.py sources)",
        "fichiers": [],
    }


def enregistrer_index(dest: Path, index: dict) -> None:
    index["fichiers"].sort(key=lambda e: e["chemin"])
    _ecrire_texte(dest / "INDEX.json", json.dumps(index, ensure_ascii=False, indent=1) + "\n")


def _entree_index(index: dict, chemin: str) -> dict | None:
    return next((e for e in index["fichiers"] if e["chemin"] == chemin), None)


def _maj_index(index: dict, entree: dict) -> None:
    index["fichiers"] = [e for e in index["fichiers"] if e["chemin"] != entree["chemin"]]
    index["fichiers"].append(entree)


def sha256_fichier(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        while bloc := f.read(TAILLE_BLOC):
            h.update(bloc)
    return h.hexdigest()


def instantane(
    client: ClientHTTP,
    dest: Path,
    index: dict,
    url: str,
    cible: Path,
    *,
    depot: str | None,
    revision: str | None,
    force: bool,
    taille: int | None = None,
    sha256: str | None = None,
) -> tuple[str, str | None]:
    """Télécharge un fichier (sauf s'il est présent) et met INDEX à jour.

    Renvoie (statut, révision de l'instantané conservé). Avec `force`, l'ancien fichier est
    archivé sous `<nom>.ancien-<sha12><suffixe>` (jamais supprimé, D1.7), avec son entrée INDEX.
    """
    if not cible.resolve().is_relative_to(dest.resolve()):
        raise ErreurOutil(f"chemin cible hors de --dest refusé : {cible}")
    rel = cible.relative_to(dest).as_posix()
    existante = _entree_index(index, rel)
    if depot is None and existante is not None and existante.get("url") != url:
        raise ErreurOutil(
            f"{rel} est déjà l'instantané d'une autre URL ({existante.get('url')}) ; "
            f"collision avec {url}"
        )
    base = {"chemin": rel, "url": url, "depot": depot, "revision": revision}
    if cible.exists() and not force:
        taille_locale = cible.stat().st_size
        if taille is not None and taille_locale != taille:
            raise ErreurOutil(
                f"{rel} présent mais de taille {taille_locale} ≠ {taille} attendue "
                f"(révision {revision}) ; relancer avec --force (l'ancien fichier est archivé)"
            )
        if existante is None:
            sha_local = sha256_fichier(cible)
            if sha256 is not None and sha_local != sha256:
                raise ErreurOutil(
                    f"{rel} présent mais de SHA-256 différent de la révision {revision} ; "
                    "relancer avec --force (l'ancien fichier est archivé)"
                )
            mtime = dt.date.fromtimestamp(cible.stat().st_mtime).isoformat()
            _maj_index(
                index,
                {
                    **base,
                    "consulte_le": mtime,
                    "taille": taille_locale,
                    "sha256": sha_local,
                    "note": "fichier déjà présent, non retéléchargé ; "
                    "consulte_le = date de modification du fichier",
                },
            )
            enregistrer_index(dest, index)
            return "déjà présent (ajouté à l'INDEX)", revision
        return "déjà présent", existante.get("revision")

    def archiver() -> None:
        if not cible.exists():
            return
        sha_ancien = sha256_fichier(cible)
        archive = cible.with_name(f"{cible.stem}.ancien-{sha_ancien[:12]}{cible.suffix}")
        if not archive.exists():  # sinon : même contenu déjà archivé, rien n'est perdu
            os.replace(cible, archive)
        ancienne = (
            dict(existante)
            if existante
            else {
                "url": None,
                "depot": depot,
                "revision": None,
                "taille": archive.stat().st_size,
                "consulte_le": dt.date.fromtimestamp(archive.stat().st_mtime).isoformat(),
                "sha256": sha_ancien,
                "note": "fichier non indexé avant son archivage",
            }
        )
        _maj_index(
            index,
            {
                **ancienne,
                "chemin": archive.relative_to(dest).as_posix(),
                "archive_le": dt.date.today().isoformat(),
                "remplace_par": rel,
            },
        )
        enregistrer_index(dest, index)

    info = client.telecharger(
        url, cible, force=True, taille=taille, sha256=sha256, avant_remplacement=archiver
    )
    entree = {
        **base,
        "consulte_le": dt.date.today().isoformat(),
        "taille": info["taille"],
        "sha256": info["sha256"],
    }
    if depot is None and info["url_finale"] != url:  # page redirigée (les URL signées des CDN HF
        entree["url_finale"] = info["url_finale"]  # ne sont pas consignées)
    _maj_index(index, entree)
    enregistrer_index(dest, index)
    return "téléchargé", revision


# ---------------------------------------------------------------------------
# Sous-commande `sources`
# ---------------------------------------------------------------------------
def _q(chemin: str) -> str:
    return urllib.parse.quote(chemin, safe="/")


def revision_hf(client: ClientHTTP, depot: str, ref: str) -> str:
    donnees = client.lire_json(
        f"{HF}/api/datasets/{depot}/revision/{urllib.parse.quote(ref, safe='')}"
    )
    sha = donnees.get("sha") if isinstance(donnees, dict) else None
    if not sha or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ErreurOutil(f"révision introuvable pour {depot}@{ref}")
    return sha


def _lien_suivant(entetes: Any) -> str | None:
    lien = entetes.get("Link") if entetes else None
    m = re.search(r'<([^>]+)>;\s*rel="next"', lien or "")
    return m.group(1) if m else None


def arbre_hf(client: ClientHTTP, depot: str, sha: str, dossier: str) -> list[dict]:
    url = f"{HF}/api/datasets/{depot}/tree/{sha}"
    if dossier:
        url += f"/{_q(dossier)}?recursive=true"
    entrees: list[dict] = []
    while url:
        corps, entetes = client.lire(url)
        page = _decoder_json(corps, url)
        if not isinstance(page, list) or not all(isinstance(e, dict) for e in page):
            raise ErreurOutil(f"arbre HF de forme inattendue : {url}")
        entrees += page
        suivant = _lien_suivant(entetes)
        url = urllib.parse.urljoin(url, suivant) if suivant else None
    fichiers = [e for e in entrees if e.get("type") == "file"]
    if not all(isinstance(e.get("path"), str) for e in fichiers):
        raise ErreurOutil(f"arbre HF sans `path` : {depot}@{sha[:10]}/{dossier}")
    return fichiers


def selections(
    quoi: list[str], legi_codes: list[str]
) -> list[tuple[str, str, str, Callable[[str], bool]]]:
    """(dépôt, ref, dossier listé, filtre sur le chemin) pour chaque source demandée."""

    def parquet(p: str) -> bool:
        return p.endswith(".parquet")

    out: list[tuple[str, str, str, Callable[[str], bool]]] = []
    if "service-public" in quoi:
        out.append(("AgentPublic/service-public", "refs/convert/parquet", "latest/train", parquet))
    if "catalogue" in quoi:
        out.append(
            (
                "AgentPublic/data-gouv-datasets-catalog",
                "main",
                "data/data-gouv-datasets-catalog-latest",
                parquet,
            )
        )
    if "legi" in quoi:
        for code in legi_codes:
            nom = LEGI_CODES.get(code, code)
            if not re.fullmatch(r"[a-z0-9_]+", nom):
                raise ErreurOutil(f"code LEGI invalide : {code}")
            out.append(("AgentPublic/legi", "main", f"data/legi-latest/legi_{nom}", parquet))
    if "questions" in quoi:
        out.append(
            ("AgentPublic/sp_questions_corpus", "main", "", lambda p: p == "gpt_corpus-20kq&A.xlsx")
        )
        out.append(
            (
                "AgentPublic/assistant_ia_questions_corpus",
                "main",
                "",
                lambda p: p == "evaluation_qo_assistant_ia_v1.xlsx",
            )
        )
    return out


def chemin_page(dest: Path, url: str) -> Path:
    parts = urllib.parse.urlsplit(url)
    segments = [
        re.sub(r"[^A-Za-z0-9._-]", "_", s)
        for s in parts.path.split("/")
        if s not in ("", ".", "..")
    ]
    if not segments:
        segments = ["index"]
    if parts.query:
        segments[-1] += "_" + hashlib.sha256(parts.query.encode()).hexdigest()[:10]
    if not Path(segments[-1]).suffix:
        segments[-1] += ".html"
    return dest.joinpath("pages", parts.hostname or "_", *segments)


def cmd_sources(
    client: ClientHTTP,
    dest: Path,
    quoi: list[str] | None,
    legi_codes: list[str],
    pages: list[str],
    force: bool,
) -> int:
    for url in pages:  # contrôle préalable : pages de la Liste blanche uniquement
        verifier_requete(url, "GET")
        if (urllib.parse.urlsplit(url).hostname or "") not in LISTE_BLANCHE:
            raise HoteRefuse(f"--page : hôte hors Liste blanche : {url}")
    if quoi is None:
        quoi = [] if pages else list(QUOI)
    dest.mkdir(parents=True, exist_ok=True)
    index = charger_index(dest)
    lignes = ["| Fichier | Révision | Statut |", "|---|---|---|"]
    for depot, ref, dossier, filtre in selections(quoi, legi_codes):
        sha = revision_hf(client, depot, ref)
        fichiers = [e for e in arbre_hf(client, depot, sha, dossier) if filtre(e["path"])]
        if not fichiers:
            raise ErreurOutil(f"aucun fichier trouvé : {depot}@{sha[:10]}/{dossier}")
        for e in fichiers:
            url = f"{HF}/datasets/{depot}/resolve/{sha}/{_q(e['path'])}"
            cible = dest.joinpath("hf", *depot.split("/"), *e["path"].split("/"))
            lfs = e.get("lfs") or {}
            statut, rev = instantane(
                client,
                dest,
                index,
                url,
                cible,
                depot=depot,
                revision=sha,
                force=force,
                taille=e.get("size"),
                sha256=lfs.get("oid"),
            )
            lignes.append(
                f"| `{cible.relative_to(dest).as_posix()}` | `{(rev or '?')[:10]}` | {statut} |"
            )
            print(f"{statut} : {cible}", file=sys.stderr)
    for url in pages:
        cible = chemin_page(dest, url)
        statut, _ = instantane(
            client, dest, index, url, cible, depot=None, revision=None, force=force
        )
        lignes.append(f"| `{cible.relative_to(dest).as_posix()}` | — | {statut} |")
    print(f"# Instantanés des sources\n\nDossier : `{dest}` ; inventaire : `INDEX.json`.\n")
    print("\n".join(lignes))
    return 0


# ---------------------------------------------------------------------------
# Sous-commande `fiche`
# ---------------------------------------------------------------------------
def _fiche_parquet(parquets: list[Path], doc_id: str) -> list[dict]:
    import duckdb  # dépendance déclarée dans l'en-tête PEP 723

    for p in parquets:  # fichiers locaux uniquement : jamais d'URL transmise à duckdb
        if not p.is_file():
            raise ErreurOutil(f"parquet local introuvable : {p}")
    con = duckdb.connect(
        ":memory:",
        config={"autoinstall_known_extensions": False, "autoload_known_extensions": False},
    )
    try:
        liste = ", ".join("'" + str(p.resolve()).replace("'", "''") + "'" for p in parquets)
        cur = con.execute(
            f"SELECT doc_id, chunk_index, title, url, text FROM read_parquet([{liste}]) "
            "WHERE doc_id = ? ORDER BY chunk_index",
            [doc_id],
        )
        noms = [d[0] for d in cur.description]
        return [dict(zip(noms, r, strict=True)) for r in cur.fetchall()]
    except duckdb.Error as exc:
        raise ErreurOutil(f"lecture parquet impossible ({exc})") from exc
    finally:
        con.close()


def lire_fiche(dest: Path, doc_id: str) -> tuple[list[dict], str]:
    parquets = sorted((dest / "hf" / "AgentPublic" / "service-public").rglob("*.parquet"))
    if parquets:
        lignes = _fiche_parquet(parquets, doc_id)
        if lignes:
            return lignes, ", ".join(p.relative_to(dest).as_posix() for p in parquets)
    repli = dest / "hf" / f"sp_{doc_id}.json"
    if repli.is_file():
        d = _decoder_json(repli.read_bytes(), repli)
        rows = d.get("rows") if isinstance(d, dict) else None
        if not isinstance(rows, list):
            raise ErreurOutil(f"{repli} : liste `rows` attendue")
        lignes = sorted(
            (r for r in rows if isinstance(r, dict) and r.get("doc_id") == doc_id),
            key=lambda r: r.get("chunk_index") or 0,
        )
        if lignes:
            return lignes, repli.relative_to(dest).as_posix()
    return [], ""


def cmd_fiche(dest: Path, doc_id: str) -> int:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", doc_id):
        raise ErreurOutil(f"identifiant de fiche invalide : {doc_id!r}")
    lignes, origine = lire_fiche(dest, doc_id)
    if not lignes:
        print(f"Fiche absente des instantanés locaux : {doc_id} (dossier {dest})", file=sys.stderr)
        return 1
    out = [
        f"# {lignes[0].get('title') or doc_id}",
        "",
        lignes[0].get("url") or "",
        "",
        f"`{doc_id}` ; source locale : `{origine}`",
        "",
    ]
    for r in lignes:
        out += [f"## Chunk {r.get('chunk_index')}", "", (r.get("text") or "").strip(), ""]
    print("\n".join(out))
    return 0


# ---------------------------------------------------------------------------
# Brouillons, vérifications
# ---------------------------------------------------------------------------
def cle_id(identifiant: str) -> tuple[str, int]:
    """Tri naturel : préfixe de code, puis numéro entier (RD-010 après RD-009)."""
    m = RE_ID.fullmatch(identifiant)
    if not m:
        return (identifiant, -1)
    return (m.group(1), int(m.group(2)))


def lire_jsonl(chemin: Path) -> tuple[list[tuple[int, Any]], list[str]]:
    """Renvoie [(numéro de ligne, objet)] et la liste des lignes illisibles."""
    objets, erreurs = [], []
    with open(chemin, encoding="utf-8-sig") as f:  # tolère un BOM (éditeurs Windows)
        for n, ligne in enumerate(f, start=1):
            if not ligne.strip():
                continue
            try:
                objets.append((n, json.loads(ligne)))
            except json.JSONDecodeError as exc:
                erreurs.append(f"{chemin.name}:{n} : JSON illisible ({exc.msg})")
    return objets, erreurs


def lire_brouillons(construction: Path) -> tuple[list[tuple[str, int, Any]], list[str]]:
    """Lit `<construction>/<CODE>.jsonl`. Renvoie [(code du fichier, ligne, item)], erreurs."""
    items, erreurs = [], []
    if not construction.is_dir():
        return items, [f"dossier des brouillons introuvable : {construction}"]
    for chemin in sorted(construction.glob("*.jsonl")):
        if chemin.stem not in CODES:
            erreurs.append(f"{chemin.name} : fichier inattendu (codes admis : {', '.join(CODES)})")
            continue
        objets, illisibles = lire_jsonl(chemin)
        erreurs += illisibles
        items += [(chemin.stem, n, o) for n, o in objets]
    return items, erreurs


def erreurs_identifiants(items: list[tuple[str, int, Any]]) -> list[str]:
    erreurs, vus = [], defaultdict(list)
    for code, n, it in items:
        lieu = f"{code}.jsonl:{n}"
        identifiant = it.get("id") if isinstance(it, dict) else None
        if not isinstance(identifiant, str):
            erreurs.append(f"{lieu} : `id` absent ou non textuel")
            continue
        m = RE_ID.fullmatch(identifiant)
        if not m or m.group(1) not in CODES or int(m.group(2)) < 1:
            erreurs.append(
                f"{lieu} : `id` mal formé : {identifiant!r} (attendu <CODE>-NNN, "
                f"codes {', '.join(CODES)})"
            )
        elif m.group(1) != code:
            erreurs.append(f"{lieu} : préfixe de `{identifiant}` différent du fichier {code}.jsonl")
        # Doublon sur (code, numéro entier) : Q-001 et Q-0001 désignent le même item.
        cle = (m.group(1), int(m.group(2))) if m else (identifiant, -1)
        vus[cle].append(f"{identifiant} en {lieu}")
    for cle, lieux in sorted(vus.items(), key=lambda x: (str(x[0][0]), x[0][1])):
        if len(lieux) > 1:
            erreurs.append(
                f"`id` dupliqué : {cle[0]}-{cle[1]:03d} ({', '.join(lieux)})"
                if cle[1] >= 0
                else f"`id` dupliqué : {cle[0]} ({', '.join(lieux)})"
            )
    return erreurs


def derniers_verdicts(construction: Path) -> tuple[dict[str, dict], list[str]]:
    """Dernier verdict par identifiant (ordre du fichier : la dernière ligne l'emporte)."""
    verdicts: dict[str, dict] = {}
    erreurs: list[str] = []
    dossier = construction / "verification"
    if not dossier.is_dir():
        return verdicts, erreurs
    for chemin in sorted(dossier.glob("*.jsonl")):
        objets, illisibles = lire_jsonl(chemin)
        erreurs += illisibles
        for n, v in objets:
            if not isinstance(v, dict) or not isinstance(v.get("id"), str):
                erreurs.append(f"{chemin.name}:{n} : ligne sans `id`")
                continue
            if v.get("verdict") not in VERDICTS:  # ignorée : ne doit pas masquer un `rejete`
                erreurs.append(
                    f"{chemin.name}:{n} : verdict inconnu {v.get('verdict')!r} "
                    f"(attendu : {', '.join(VERDICTS)})"
                )
                continue
            verdicts[v["id"]] = v
    return verdicts, erreurs


def _couverture_verdicts(ids_brouillons: list[str], verdicts: dict[str, dict]) -> list[str]:
    """Lignes Markdown : brouillons sans verdict et verdicts sans brouillon (non bloquant)."""
    sans_verdict = sorted((i for i in ids_brouillons if i not in verdicts), key=cle_id)
    orphelins = sorted((i for i in verdicts if i not in set(ids_brouillons)), key=cle_id)
    return [
        f"- Items sans verdict : {len(sans_verdict)}"
        + (" (" + ", ".join(f"`{i}`" for i in sans_verdict) + ")" if sans_verdict else ""),
        f"- Verdicts sans brouillon : {len(orphelins)}"
        + (" (" + ", ".join(f"`{i}`" for i in orphelins) + ")" if orphelins else ""),
    ]


def _ecart(reel: int, cible: int) -> str:
    d = reel - cible
    return f"+{d}" if d > 0 else str(d)


# ---------------------------------------------------------------------------
# Sous-commande `assembler`
# ---------------------------------------------------------------------------
def cmd_assembler(racine: Path, version: str, force: bool = False) -> int:
    construction = racine / "eval" / "construction" / version
    sortie_dir = racine / "eval" / "jeu" / version
    if (sortie_dir / "MANIFEST.json").exists() and not force:
        raise ErreurOutil(
            f"{sortie_dir / 'MANIFEST.json'} existe : jeu gelé, assemblage refusé "
            "(--force pour passer outre)"
        )
    items, erreurs = lire_brouillons(construction)
    erreurs += erreurs_identifiants(items)
    verdicts, err_verif = derniers_verdicts(construction)
    erreurs += err_verif
    if not items and not erreurs:
        erreurs.append(f"aucun brouillon dans {construction}")
    retenus, exclus = [], []
    if not erreurs:
        for _, _, it in items:
            v = verdicts.get(it["id"])
            (exclus if v and v.get("verdict") == "rejete" else retenus).append(it)
        if not retenus:
            erreurs.append("aucun item retenu (tous rejetés)")
    if erreurs:
        print("Assemblage refusé, aucun fichier écrit :", file=sys.stderr)
        for e in erreurs:
            print(f"- {e}", file=sys.stderr)
        return 2
    retenus.sort(key=lambda it: cle_id(it["id"]))
    texte = "".join(json.dumps(it, ensure_ascii=False) + "\n" for it in retenus)
    _ecrire_texte(sortie_dir / "items.jsonl", texte)
    sha = hashlib.sha256(texte.encode("utf-8")).hexdigest()
    out = [
        f"# Assemblage {version}",
        "",
        f"- Fichier : `eval/jeu/{version}/items.jsonl`",
        f"- Items écrits : {len(retenus)}",
        f"- SHA-256 : `{sha}`",
        f"- Items exclus (dernier verdict `rejete`) : {len(exclus)}",
    ]
    for it in sorted(exclus, key=lambda i: cle_id(i["id"])):
        v = verdicts[it["id"]]
        out.append(f"  - `{it['id']}` : {v.get('motif', '?')} — {v.get('detail', '')}".rstrip(" —"))
    out += _couverture_verdicts([it["id"] for _, _, it in items], verdicts)
    print("\n".join(out))
    return 0


# ---------------------------------------------------------------------------
# Sous-commande `composition`
# ---------------------------------------------------------------------------
def _nb_mots(valeur: Any) -> int:
    if isinstance(valeur, str):
        return len(valeur.split())
    if isinstance(valeur, dict):
        return sum(_nb_mots(v) for k, v in valeur.items() if k != "consigne")
    if isinstance(valeur, list):
        return sum(_nb_mots(v) for v in valeur)
    return 0


def producteurs_rd(it: dict) -> list[str]:
    if isinstance(it.get("producteurs"), list):
        return [str(p) for p in it["producteurs"] if p]
    if it.get("producteur"):
        return [str(it["producteur"])]
    rr = it.get("reponse_reference")
    jp = rr.get("jeu_principal") if isinstance(rr, dict) else None
    if isinstance(jp, dict) and jp.get("producteur"):
        return [str(jp["producteur"])]
    return []


def amorce_reelle(it: dict) -> bool:
    if not (isinstance(it.get("amorce_usager"), str) and it["amorce_usager"].strip()):
        return False
    prov = it.get("provenance")
    if not isinstance(prov, list):
        return False
    return any(
        isinstance(p, dict) and isinstance(p.get(champ), str) and corpus in p[champ]
        for p in prov
        for champ in ("source", "url", "depot")
        for corpus in CORPUS_AMORCES
    )


RE_DATE_ISO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def _anomalies_co(it: dict) -> list[str]:
    a: list[str] = []
    texte = it["entree"].get("texte") if isinstance(it.get("entree"), dict) else None
    fautes = it.get("fautes")
    if "fautes" in it and not (isinstance(fautes, list) and fautes):
        return ["`fautes` doit être une liste non vide"]
    if not isinstance(texte, str):
        return ["`entree.texte` absent : positions des fautes invérifiables"] if fautes else []
    valides: list[dict] = []
    for i, f in enumerate(fautes or []):
        ok = (
            isinstance(f, dict)
            and type(f.get("debut")) is int
            and type(f.get("fin")) is int
            and 0 <= f["debut"] < f["fin"] <= len(texte)
            and texte[f["debut"] : f["fin"]] == f.get("erreur")
            and isinstance(f.get("correction"), str)
        )
        if ok:
            valides.append(f)
        else:
            a.append(
                f"`fautes[{i}]` : position fausse (`0 <= debut < fin <= len(texte)` et "
                "`entree.texte[debut:fin] == erreur` attendus)"
            )
    valides.sort(key=lambda f: f["debut"])
    for f1, f2 in pairwise(valides):
        if f2["debut"] < f1["fin"]:
            a.append(
                f"`fautes` qui se chevauchent : [{f1['debut']}, {f1['fin']}) "
                f"et [{f2['debut']}, {f2['fin']})"
            )
    if not a and isinstance(it.get("texte_corrige_reference"), str):
        corrige = texte
        for f in reversed(valides):  # depuis la fin : les positions restent valables
            corrige = corrige[: f["debut"]] + f["correction"] + corrige[f["fin"] :]
        if corrige != it["texte_corrige_reference"]:
            a.append(
                "appliquer les `fautes` à `entree.texte` ne donne pas `texte_corrige_reference`"
            )
    return a


def anomalies_item(code: str, it: dict) -> list[str]:
    a: list[str] = []
    manquants = [c for c in CHAMPS_COMMUNS + CHAMPS_TACHE[code] if c not in it]
    if code in CODES_THEMATIQUES and "theme" not in it:
        manquants.append("theme")
    if code == "NR" and "reponse_reference" not in it and "criteres" not in it:
        manquants.append("reponse_reference|criteres")
    if manquants:
        a.append("champs manquants : " + ", ".join(f"`{c}`" for c in manquants))
    tache = it.get("tache")
    if "tache" in it and tache != TACHES[code] and tache not in ALIAS_TACHES.get(code, ()):
        a.append(f"`tache` = {tache!r}, attendu {TACHES[code]!r}")
    if "difficulte" in it and it["difficulte"] not in DIFFICULTES:
        a.append(f"`difficulte` invalide : {it['difficulte']!r}")
    if code in CODES_THEMATIQUES and "theme" in it and it["theme"] not in THEMES:
        a.append(f"`theme` hors SPEC : {it['theme']!r}")
    if "entree" in it:
        attendu = str if code in CODES_ENTREE_TEXTE else dict
        if not isinstance(it["entree"], attendu):
            a.append(f"`entree` doit être {'un texte' if attendu is str else 'un objet'}")
    if "fictif" in it and not isinstance(it["fictif"], bool):
        a.append("`fictif` doit être un booléen")
    if "version_item" in it and (type(it["version_item"]) is not int or it["version_item"] < 1):
        # 1 à la création ; incrémenté quand un item relu est corrigé (SPEC §6, v1.1).
        a.append(f"`version_item` doit être un entier >= 1 : {it['version_item']!r}")
    prov = it.get("provenance")
    if "provenance" in it:
        if not isinstance(prov, list) or not prov:
            a.append("`provenance` doit être une liste non vide")
        elif any(
            not isinstance(p, dict)
            or not isinstance(p.get("consulte_le"), str)
            or not RE_DATE_ISO.match(p["consulte_le"])
            for p in prov
        ):
            a.append("`provenance[]` sans `consulte_le` au format ISO (AAAA-MM-JJ)")
    if code == "Q":
        cles = it.get("elements_cles")
        if "elements_cles" in it and not (isinstance(cles, list) and 3 <= len(cles) <= 5):
            a.append("`elements_cles` : 3 à 5 éléments attendus")
        if "sans_reponse" in it and not isinstance(it["sans_reponse"], bool):
            a.append("`sans_reponse` doit être un booléen")
        if it.get("sans_reponse") is True and not it.get("orientation_attendue"):
            a.append("`sans_reponse` sans `orientation_attendue`")
        for u in it.get("sources_attendues") or []:
            hote = urllib.parse.urlsplit(u).hostname if isinstance(u, str) else None
            if hote not in LISTE_BLANCHE:
                a.append(f"`sources_attendues` hors Liste blanche : {u!r}")
        if it.get("amorce_usager") and not amorce_reelle(it):
            a.append("`amorce_usager` sans provenance d'un corpus AgentPublic")
    if code == "RD":
        if "mode" in it and it["mode"] not in MODES_RD:
            a.append(f"`mode` invalide : {it['mode']!r}")
        for appel in it.get("appels_attendus") or []:
            outil = appel.get("outil") if isinstance(appel, dict) else None
            if outil not in OUTILS_RD:
                a.append(f"`appels_attendus` : outil hors des 5 outils figés : {outil!r}")
            if not (isinstance(appel, dict) and isinstance(appel.get("regles"), dict)):
                a.append(f"`appels_attendus` : appel {outil!r} sans objet `regles`")
    if code == "RE":
        longueur = it.get("longueur_demandee")
        if "longueur_demandee" in it and longueur not in LONGUEURS_RE:
            a.append(f"`longueur_demandee` invalide : {longueur!r}")
    if code == "CO":
        a += _anomalies_co(it)
    return a


def cmd_composition(racine: Path, version: str) -> int:
    construction = racine / "eval" / "construction" / version
    brouillons, erreurs = lire_brouillons(construction)
    erreurs += erreurs_identifiants(brouillons)
    verdicts, err_verif = derniers_verdicts(construction)
    erreurs += err_verif
    retenus: list[tuple[str, dict]] = []
    nb_rejetes = 0
    for code, n, it in brouillons:
        if not isinstance(it, dict):
            erreurs.append(f"{code}.jsonl:{n} : l'item n'est pas un objet JSON")
            continue
        v = verdicts.get(it.get("id"))
        if v and v.get("verdict") == "rejete":
            nb_rejetes += 1
            continue
        retenus.append((code, it))

    out = [
        f"# Composition du jeu {version} (brouillons)",
        "",
        (
            f"Source : `eval/construction/{version}/` ; {len(retenus)} items retenus, "
            f"{nb_rejetes} exclus (dernier verdict `rejete`)."
        ),
        "",
    ]
    ids_brouillons = [
        it["id"]
        for _, _, it in brouillons
        if isinstance(it, dict) and isinstance(it.get("id"), str)
    ]
    out += _couverture_verdicts(ids_brouillons, verdicts) + [""]

    # Tâche × difficulté
    comptes = Counter((c, it.get("difficulte")) for c, it in retenus)
    par_code = Counter(c for c, _ in retenus)
    out += [
        "## Tâche × difficulté (réel / cible, écart)",
        "",
        "| Tâche | Total | Facile | Moyen | Difficile |",
        "|---|---|---|---|---|",
    ]
    tot_reel = tot_cible = 0
    for code in CODES:
        cibles = CIBLES[code]
        cellules = [
            f"{comptes[(code, d)]} / {c} ({_ecart(comptes[(code, d)], c)})"
            for d, c in zip(DIFFICULTES, cibles, strict=True)
        ]
        reel, cible = par_code[code], sum(cibles)
        tot_reel += reel
        tot_cible += cible
        out.append(
            f"| {code} ({TACHES[code]}) | {reel} / {cible} ({_ecart(reel, cible)}) | "
            + " | ".join(cellules)
            + " |"
        )
    out += [
        f"| **Total** | **{tot_reel} / {tot_cible} ({_ecart(tot_reel, tot_cible)})** | | | |",
        "",
    ]

    # Contraintes particulières
    q = [it for c, it in retenus if c == "Q"]
    rd = [it for c, it in retenus if c == "RD"]
    cr = [it for c, it in retenus if c == "CR"]
    sans_rep = [it for it in q if it.get("sans_reponse") is True]
    avec_orient = [it for it in sans_rep if it.get("orientation_attendue")]
    amorces = sum(amorce_reelle(it) for it in q)
    part = amorces / len(q) if q else 0.0
    cible_amorces = int(CIBLE_Q_PART_AMORCES * sum(CIBLES["Q"]))
    producteurs = Counter(p for it in rd for p in producteurs_rd(it))
    valeurs = sum(bool(it.get("valeurs_attendues")) for it in rd)
    repli = sum(it.get("mode") == "repli" for it in rd)
    longues = sum(_nb_mots(it.get("entree")) > SEUIL_CR_LONGUE_MOTS for it in cr)
    out += [
        "## Contraintes particulières",
        "",
        "| Contrainte | Cible | Réel | Écart |",
        "|---|---|---|---|",
        (
            f"| Q sans réponse | {CIBLE_Q_SANS_REPONSE} | {len(sans_rep)} | "
            f"{_ecart(len(sans_rep), CIBLE_Q_SANS_REPONSE)} |"
        ),
        (
            f"| Q sans réponse avec `orientation_attendue` | {len(sans_rep)} | "
            f"{len(avec_orient)} | "
            f"{_ecart(len(avec_orient), len(sans_rep))} |"
        ),
        (
            f"| Q issus d'amorces réelles | ≥ 50 % (≥ {cible_amorces} sur 60) | {amorces} "
            f"({part:.0%} des Q présents) | {_ecart(amorces, cible_amorces)} |"
        ),
        (
            f"| RD demandes de valeurs | {CIBLE_RD_VALEURS} | {valeurs} | "
            f"{_ecart(valeurs, CIBLE_RD_VALEURS)} |"
        ),
        f"| RD cas de repli | {CIBLE_RD_REPLI} | {repli} | {_ecart(repli, CIBLE_RD_REPLI)} |",
        (
            f"| RD producteurs distincts | ≥ {CIBLE_RD_PRODUCTEURS} | {len(producteurs)} | "
            f"{_ecart(len(producteurs), CIBLE_RD_PRODUCTEURS)} |"
        ),
        (
            f"| CR transcriptions > {SEUIL_CR_LONGUE_MOTS} mots | {CIBLE_CR_LONGUES} | {longues} | "
            f"{_ecart(longues, CIBLE_CR_LONGUES)} |"
        ),
        "",
    ]

    # Thèmes
    thematiques = [(c, it) for c, it in retenus if c in CODES_THEMATIQUES]
    total_cible_theme = sum(sum(CIBLES[c]) for c in CODES_THEMATIQUES)
    themes = Counter(
        (c, it.get("theme") if it.get("theme") in THEMES else None) for c, it in thematiques
    )
    out += [
        f"## Thèmes ({', '.join(CODES_THEMATIQUES)})",
        "",
        "| Thème | " + " | ".join(CODES_THEMATIQUES) + " | Total | Part réelle | Part cible | "
        f"Cible (sur {total_cible_theme}) | Écart |",
        "|---|" + "---|" * (len(CODES_THEMATIQUES) + 5),
    ]
    for theme, part_cible in list(THEMES.items()) + [(None, None)]:
        n = [themes[(c, theme)] for c in CODES_THEMATIQUES]
        total = sum(n)
        if theme is None and not total:
            continue
        part_reelle = f"{total / len(thematiques):.0%}" if thematiques else "—"
        if part_cible is None:
            out.append(
                "| (absent ou hors SPEC) | " + " | ".join(map(str, n)) + f" | {total} | "
                f"{part_reelle} | — | — | — |"
            )
        else:
            cible_n = round(part_cible * total_cible_theme)
            out.append(
                f"| `{theme}` | " + " | ".join(map(str, n)) + f" | {total} | {part_reelle} | "
                f"{part_cible:.0%} | {cible_n} | {_ecart(total, cible_n)} |"
            )
    out.append("")

    # Producteurs RD
    out += ["## Producteurs de données (RD)", ""]
    if producteurs:
        out += ["| Producteur | Items |", "|---|---|"]
        out += [
            f"| {p} | {n} |" for p, n in sorted(producteurs.items(), key=lambda x: (-x[1], x[0]))
        ]
    else:
        out.append("Aucun producteur renseigné.")
    sans_prod = [it.get("id") for it in rd if not producteurs_rd(it)]
    if sans_prod:
        out += ["", "RD sans producteur : " + ", ".join(f"`{i}`" for i in sans_prod)]
    out.append("")

    # Anomalies de structure
    out += ["## Anomalies de structure", ""]
    lignes = [f"- {e}" for e in erreurs]
    for code, it in sorted(retenus, key=lambda x: cle_id(str(x[1].get("id")))):
        for a in anomalies_item(code, it):
            lignes.append(f"- `{it.get('id')}` : {a}")
    out += lignes or ["Aucune anomalie."]
    print("\n".join(out))
    return 0


# ---------------------------------------------------------------------------
# Sous-commande `rejets`
# ---------------------------------------------------------------------------
def cmd_rejets(racine: Path, version: str) -> int:
    dossier = racine / "eval" / "construction" / version / "verification"
    out = [f"# Rejets de la double vérification ({version})", ""]
    fichiers = sorted(dossier.glob("*.jsonl")) if dossier.is_dir() else []
    if not fichiers:
        print("\n".join(out + [f"Aucune vérification dans `{dossier}`."]))
        return 0
    signalements: list[str] = []
    verdicts = Counter()
    rejets = Counter()
    ids = defaultdict(set)
    motifs = Counter()
    for chemin in fichiers:
        objets, illisibles = lire_jsonl(chemin)
        signalements += illisibles
        for n, v in objets:
            lieu = f"{chemin.name}:{n}"
            if not isinstance(v, dict) or not isinstance(v.get("id"), str):
                signalements.append(f"{lieu} : ligne sans `id`")
                continue
            m = RE_ID.fullmatch(v["id"])
            code = m.group(1) if m and m.group(1) in CODES else chemin.stem
            verdict = v.get("verdict")
            if verdict not in VERDICTS:
                signalements.append(f"{lieu} : verdict inconnu {verdict!r}")
                continue
            verdicts[code] += 1
            ids[code].add(v["id"])
            if verdict == "rejete":
                rejets[code] += 1
                motif = v.get("motif")
                if motif not in MOTIFS:
                    signalements.append(f"{lieu} : motif inconnu {motif!r} (compté en `autre`)")
                    motif = "autre"
                motifs[(code, motif)] += 1
    codes = [c for c in CODES if verdicts[c]] + sorted(c for c in verdicts if c not in CODES)
    if not codes:
        out += ["Aucun verdict valide.", "", "## Lignes signalées", ""] + [
            f"- {s}" for s in signalements
        ]
        print("\n".join(out))
        return 0
    out += [
        "## Par Tâche",
        "",
        "| Tâche | Items vérifiés | Verdicts | Rejets | Taux de rejet |",
        "|---|---|---|---|---|",
    ]
    for c in codes:
        out.append(
            f"| {c} | {len(ids[c])} | {verdicts[c]} | {rejets[c]} | {rejets[c] / verdicts[c]:.1%} |"
        )
    tv, tr = sum(verdicts.values()), sum(rejets.values())
    out += [
        (
            f"| **Total** | {sum(len(s) for s in ids.values())} | {tv} | {tr} | "
            f"{(tr / tv if tv else 0):.1%} |"
        ),
        "",
    ]
    out += [
        "## Par motif",
        "",
        "| Motif | " + " | ".join(codes) + " | Total |",
        "|---|" + "---|" * (len(codes) + 1),
    ]
    for motif in MOTIFS:
        n = [motifs[(c, motif)] for c in codes]
        out.append(f"| `{motif}` | " + " | ".join(map(str, n)) + f" | {sum(n)} |")
    out.append("")
    out += ["## Lignes signalées", ""] + ([f"- {s}" for s in signalements] or ["Aucune."])
    print("\n".join(out))
    return 0


# ---------------------------------------------------------------------------
# Sous-commande `revue`
# ---------------------------------------------------------------------------
CHAMPS_TITRE_REVUE = ("id", "tache", "difficulte", "theme")


def _cloture(texte: str) -> str:
    """Barrière de bloc de code plus longue que toute suite d'accents graves du texte."""
    plus_longue = max((len(m) for m in re.findall(r"`+", texte)), default=0)
    return "`" * max(3, plus_longue + 1)


def _bloc_texte(texte: str, retrait: str) -> list[str]:
    cloture = _cloture(texte)
    return (
        [f"{retrait}{cloture}text"]
        + [f"{retrait}{ligne}" if ligne else "" for ligne in texte.split("\n")]
        + [f"{retrait}{cloture}"]
    )


def _scalaire(valeur: Any) -> str:
    return valeur if isinstance(valeur, str) else json.dumps(valeur, ensure_ascii=False)


def _simple(valeur: Any) -> bool:
    """Valeur rendue sur la ligne de sa puce (scalaire sans saut de ligne, conteneur vide)."""
    if isinstance(valeur, str):
        return "\n" not in valeur
    if isinstance(valeur, dict | list):
        return not valeur
    return True


def _rendre_valeur(valeur: Any, retrait: str) -> list[str]:
    """Rend une valeur composée sous sa puce : listes en puces, objets en sous-puces,
    texte multiligne en bloc. `retrait` est la colonne du contenu de la puce parente."""
    if isinstance(valeur, str):
        return _bloc_texte(valeur, retrait)
    lignes: list[str] = []
    paires = valeur.items() if isinstance(valeur, dict) else ((None, v) for v in valeur)
    for cle, v in paires:
        puce = f"{retrait}- **{cle}** :" if cle is not None else f"{retrait}-"
        if _simple(v):
            lignes.append(f"{puce} {_scalaire(v)}".rstrip())
        else:
            lignes.append(puce)
            lignes += _rendre_valeur(v, retrait + "  ")
    return lignes


def _titre_fiche(it: dict) -> str:
    return (
        f"## {it['id']} — {it.get('tache', '?')} "
        f"({it.get('difficulte', '?')}, thème `{it.get('theme', '?')}`)"
    )


def _rendre_champs(it: dict) -> list[str]:
    """Champs d'un item hors titre : scalaire sur une ligne, sinon sous-titre et rendu."""
    lignes: list[str] = []
    for cle, valeur in it.items():
        if cle in CHAMPS_TITRE_REVUE:
            continue
        if _simple(valeur):
            lignes += [f"**{cle}** : {_scalaire(valeur)}".rstrip(), ""]
        else:
            lignes += [f"### {cle}", ""] + _rendre_valeur(valeur, "") + [""]
    return lignes


def rendre_lecture(version: str, items: list[dict]) -> str:
    """Markdown de lecture : une fiche par item, chaque champ rendu lisiblement."""
    lignes = [
        f"# Échantillon de relecture du Jeu d'évaluation {version} — lecture",
        "",
        f"- Items : {len(items)}, dans l'ordre du manifeste "
        f"(`eval/jeu/{version}/MANIFEST.json`, `echantillons.relecture`).",
        f"- Document officiel : `eval/revue/echantillon-revue-{version}.md` (export du gel) ; "
        "même contenu, rendu ici champ par champ.",
        "",
    ]
    for it in items:
        lignes += [_titre_fiche(it), "", "- [ ] Relu", "- Remarques :", ""]
        lignes += _rendre_champs(it)
    return "\n".join(lignes).rstrip("\n") + "\n"


def _ecrire_exclusifs(sorties: tuple[Path, ...], contenus: tuple[str, ...]) -> None:
    """Écrit chaque sortie par création exclusive (UTF-8, LF) ; aucun export partiel.

    Lève `ErreurOutil` si une sortie existe déjà (rien n'est écrit) ou si une écriture
    échoue (les fichiers créés par l'appel sont retirés)."""
    existants = [s for s in sorties if s.exists()]
    if existants:
        raise ErreurOutil(
            "export déjà présent, rien n'est écrit : " + ", ".join(str(s) for s in existants)
        )
    sorties[0].parent.mkdir(parents=True, exist_ok=True)
    ecrits: list[Path] = []
    try:
        for chemin, contenu in zip(sorties, contenus, strict=True):
            with open(chemin, "x", encoding="utf-8", newline="\n") as f:  # création exclusive
                ecrits.append(chemin)
                f.write(contenu)
    except OSError as exc:  # existant, disque plein, droits… : aucun export partiel
        for chemin in ecrits:  # n'efface que ce que cet appel vient de créer
            chemin.unlink(missing_ok=True)
        if isinstance(exc, FileExistsError):
            raise ErreurOutil(f"export déjà présent, rien n'est écrit : {exc.filename}") from None
        raise ErreurOutil(f"écriture de l'export impossible, rien n'est écrit : {exc}") from None


def cmd_revue(racine: Path, version: str) -> int:
    jeu = racine / "eval" / "jeu" / version
    chemin_manifeste = jeu / "MANIFEST.json"
    chemin_items = jeu / "items.jsonl"
    revue = racine / "eval" / "revue"
    sorties = (
        revue / f"echantillon-revue-{version}.jsonl",
        revue / f"echantillon-revue-{version}-lecture.md",
    )
    if not chemin_manifeste.is_file():
        raise ErreurOutil(f"manifeste absent : {chemin_manifeste} (geler d'abord le jeu)")
    manifeste = _decoder_json(chemin_manifeste.read_bytes(), chemin_manifeste)
    echantillons = manifeste.get("echantillons") if isinstance(manifeste, dict) else None
    ids = echantillons.get("relecture") if isinstance(echantillons, dict) else None
    if not isinstance(ids, list) or not all(isinstance(i, str) for i in ids):
        raise ErreurOutil(f"{chemin_manifeste} : `echantillons.relecture` absent ou invalide")
    if not chemin_items.is_file():
        raise ErreurOutil(f"items absents : {chemin_items}")
    brutes: dict[str, str] = {}
    objets: dict[str, dict] = {}
    with open(chemin_items, encoding="utf-8-sig", newline="") as f:
        for n, ligne in enumerate(f, start=1):
            ligne = ligne.rstrip("\r\n")
            if not ligne.strip():
                continue
            try:
                it = json.loads(ligne)
            except json.JSONDecodeError as exc:
                raise ErreurOutil(f"{chemin_items.name}:{n} : JSON illisible ({exc.msg})") from None
            if isinstance(it, dict) and isinstance(it.get("id"), str):
                brutes[it["id"]] = ligne
                objets[it["id"]] = it
    inconnus = [i for i in ids if i not in brutes]
    if inconnus:
        raise ErreurOutil(
            f"identifiant(s) de l'échantillon absent(s) de {chemin_items.name} : "
            + ", ".join(inconnus)
        )
    contenus = (
        "".join(brutes[i] + "\n" for i in ids),
        rendre_lecture(version, [objets[i] for i in ids]),
    )
    _ecrire_exclusifs(sorties, contenus)
    print(
        "\n".join(
            [
                f"# Revue {version}",
                "",
                f"- Items de l'échantillon : {len(ids)}",
                *(f"- Écrit : `{s.relative_to(racine).as_posix()}`" for s in sorties),
            ]
        )
    )
    return 0


# ---------------------------------------------------------------------------
# Sous-commande `changements`
# ---------------------------------------------------------------------------
STATUTS_CHANGEMENT = ("nouveau", "modifie", "retire")
_ABSENT: Any = object()


def lire_items_jeu(chemin: Path) -> dict[str, dict]:
    """Items d'un `items.jsonl` assemblé, par identifiant ; lève `ErreurOutil` si absent,
    illisible, ou si un item n'a pas d'`id` ou le répète."""
    if not chemin.is_file():
        raise ErreurOutil(f"items absents : {chemin} (assembler d'abord la version)")
    objets, erreurs = lire_jsonl(chemin)
    if erreurs:
        raise ErreurOutil("; ".join(erreurs))
    items: dict[str, dict] = {}
    for n, it in objets:
        if not isinstance(it, dict) or not isinstance(it.get("id"), str):
            raise ErreurOutil(f"{chemin.name}:{n} : item sans `id`")
        if it["id"] in items:
            raise ErreurOutil(f"{chemin.name}:{n} : `id` dupliqué : {it['id']}")
        items[it["id"]] = it
    return items


def diff_champs(ancien: Any, nouveau: Any, chemin: str = "") -> list[dict]:
    """Champs changés entre deux items. Un objet est comparé clé par clé (chemin pointé,
    `entree.transcription`) ; une liste ou un scalaire, en bloc. Chaque entrée porte
    `champ`, `changement` (`ajoute`, `retire` ou `modifie`) et les valeurs `ancien` et
    `nouveau` présentes."""
    if isinstance(ancien, dict) and isinstance(nouveau, dict):
        diffs: list[dict] = []
        for cle in list(ancien) + [c for c in nouveau if c not in ancien]:
            sous = f"{chemin}.{cle}" if chemin else str(cle)
            diffs += diff_champs(ancien.get(cle, _ABSENT), nouveau.get(cle, _ABSENT), sous)
        return diffs
    if (
        ancien is not _ABSENT
        and nouveau is not _ABSENT
        and json.dumps(ancien, sort_keys=True) == json.dumps(nouveau, sort_keys=True)
    ):
        return []
    entree: dict[str, Any] = {"champ": chemin}
    if ancien is _ABSENT:
        entree.update(changement="ajoute", nouveau=nouveau)
    elif nouveau is _ABSENT:
        entree.update(changement="retire", ancien=ancien)
    else:
        entree.update(changement="modifie", ancien=ancien, nouveau=nouveau)
    return [entree]


def comparer_jeux(
    reference: dict[str, dict], version: dict[str, dict], verdicts: dict[str, dict]
) -> list[dict]:
    """Lignes de l'export, dans l'ordre des Tâches puis des numéros : `nouveau` (item),
    `modifie` (champs changés, puis item), `retire` (ancien item). Chaque ligne porte aussi
    le dernier verdict de l'item dans la version (`verdict`), s'il existe."""

    def ordre(identifiant: str) -> tuple[int, str, int]:  # ordre des Tâches de SPEC §2
        code, numero = cle_id(identifiant)
        return (CODES.index(code) if code in CODES else len(CODES), code, numero)

    lignes: list[dict] = []
    for identifiant in sorted(set(reference) | set(version), key=ordre):
        ancien, nouveau = reference.get(identifiant), version.get(identifiant)
        ligne: dict[str, Any]
        if ancien is None:
            ligne = {"id": identifiant, "statut": "nouveau", "item": nouveau}
        elif nouveau is None:
            ligne = {"id": identifiant, "statut": "retire", "item": ancien}
        else:
            champs = diff_champs(ancien, nouveau)
            if not champs:
                continue
            ligne = {"id": identifiant, "statut": "modifie", "champs": champs, "item": nouveau}
        if identifiant in verdicts:
            ligne["verdict"] = verdicts[identifiant]
        lignes.append(ligne)
    return lignes


def _bloc_diff(ancien: str, nouveau: str) -> list[str]:
    import difflib

    corps = list(
        difflib.unified_diff(
            ancien.split("\n"), nouveau.split("\n"), "ancien", "nouveau", n=1, lineterm=""
        )
    )
    cloture = _cloture("\n".join(corps))
    return [f"{cloture}diff", *corps, cloture]


def _rendre_valeur_bloc(valeur: Any) -> list[str]:
    if _simple(valeur):
        return [_scalaire(valeur) if valeur != "" else "(texte vide)"]
    return _rendre_valeur(valeur, "")


def _rendre_champ_change(changement: dict) -> list[str]:
    nature = {"ajoute": "ajouté", "retire": "retiré", "modifie": "modifié"}
    lignes = [f"### `{changement['champ']}` ({nature[changement['changement']]})", ""]
    ancien = changement.get("ancien", _ABSENT)
    nouveau = changement.get("nouveau", _ABSENT)
    if isinstance(ancien, str) and isinstance(nouveau, str) and ("\n" in ancien or "\n" in nouveau):
        lignes += ["Différences, ligne à ligne :", ""] + _bloc_diff(ancien, nouveau) + [""]
        for libelle, valeur in (("Ancienne valeur", ancien), ("Nouvelle valeur", nouveau)):
            lignes += [f"<details><summary>{libelle} complète</summary>", ""]
            lignes += _bloc_texte(valeur, "") + ["", "</details>", ""]
        return lignes
    if changement["changement"] == "modifie" and not (
        isinstance(ancien, str) and isinstance(nouveau, str)
    ):
        avant, apres = (
            json.dumps(v, ensure_ascii=False, indent=1, sort_keys=True) for v in (ancien, nouveau)
        )
        lignes += ["Différences, ligne à ligne (JSON) :", ""] + _bloc_diff(avant, apres) + [""]
    for libelle, valeur in (("Ancienne valeur", ancien), ("Nouvelle valeur", nouveau)):
        if valeur is not _ABSENT:
            lignes += [f"**{libelle}** :", ""] + _rendre_valeur_bloc(valeur) + [""]
    return lignes


def _lignes_verdict(verdict: dict | None) -> list[str]:
    if not verdict:
        return ["**Dernier verdict** : aucun", ""]
    return [
        f"**Dernier verdict** : `{verdict.get('verdict')}` "
        f"({verdict.get('motif', '-')}, {verdict.get('verifie_le', '?')}) : "
        + _scalaire(verdict.get("detail", "")).replace("\n", " "),
        "",
    ]


def rendre_changements(reference: str, version: str, lignes: list[dict]) -> str:
    """Markdown de relecture des changements : items nouveaux, modifiés, retirés."""
    par_statut = {s: [lg for lg in lignes if lg["statut"] == s] for s in STATUTS_CHANGEMENT}
    sortie = [
        f"# Changements du Jeu d'évaluation {version} par rapport à {reference}",
        "",
        f"- Comparaison : `eval/jeu/{reference}/items.jsonl` (référence gelée) et "
        f"`eval/jeu/{version}/items.jsonl` (assemblé, non gelé).",
        f"- Items nouveaux : {len(par_statut['nouveau'])} ; modifiés : "
        f"{len(par_statut['modifie'])} ; retirés : {len(par_statut['retire'])}.",
        f"- Valeurs complètes : `eval/revue/changements-{reference}-{version}.jsonl`.",
        "",
    ]
    titres = {"nouveau": "Items nouveaux", "modifie": "Items modifiés", "retire": "Items retirés"}
    for statut in STATUTS_CHANGEMENT:
        sortie += [f"# {titres[statut]} ({len(par_statut[statut])})", ""]
        if not par_statut[statut]:
            sortie += ["Aucun.", ""]
        for ligne in par_statut[statut]:
            it = ligne["item"]
            sortie += [_titre_fiche(it), "", "- [ ] Relu", "- Remarques :", ""]
            sortie += _lignes_verdict(ligne.get("verdict"))
            if statut == "modifie":
                noms = ", ".join(f"`{c['champ']}`" for c in ligne["champs"])
                sortie += [f"Champs changés : {noms}.", ""]
                for changement in ligne["champs"]:
                    sortie += _rendre_champ_change(changement)
                continue
            if statut == "retire":
                sortie += ["Ancien item :", ""]
            sortie += _rendre_champs(it)
    return "\n".join(sortie).rstrip("\n") + "\n"


def cmd_changements(racine: Path, version: str, reference: str) -> int:
    if version == reference:
        raise ErreurOutil(f"version et référence identiques : {version}")
    items_reference = lire_items_jeu(racine / "eval" / "jeu" / reference / "items.jsonl")
    items_version = lire_items_jeu(racine / "eval" / "jeu" / version / "items.jsonl")
    verdicts, erreurs = derniers_verdicts(racine / "eval" / "construction" / version)
    if erreurs:
        raise ErreurOutil("verdicts illisibles, rien n'est écrit : " + "; ".join(erreurs))
    lignes = comparer_jeux(items_reference, items_version, verdicts)
    revue = racine / "eval" / "revue"
    sorties = (
        revue / f"changements-{reference}-{version}.jsonl",
        revue / f"changements-{reference}-{version}.md",
    )
    contenus = (
        "".join(json.dumps(lg, ensure_ascii=False) + "\n" for lg in lignes),
        rendre_changements(reference, version, lignes),
    )
    _ecrire_exclusifs(sorties, contenus)
    out = [f"# Changements {version} / {reference}", ""]
    for statut in STATUTS_CHANGEMENT:
        ids = [lg["id"] for lg in lignes if lg["statut"] == statut]
        out.append(f"- {statut} : {len(ids)}" + (f" ({', '.join(ids)})" if ids else ""))
    out += [f"- Écrit : `{s.relative_to(racine).as_posix()}`" for s in sorties]
    print("\n".join(out))
    return 0


# ---------------------------------------------------------------------------
# Entrée
# ---------------------------------------------------------------------------
def analyser(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        prog="construire_jeu.py", description=(__doc__ or "").split("\n")[0]
    )
    sous = ap.add_subparsers(dest="cmd", required=True)

    s = sous.add_parser("sources", help="instantanés des sources réelles")
    s.add_argument("--dest", type=Path, default=Path("data/raw/eval-sources"))
    s.add_argument(
        "--quoi",
        nargs="+",
        choices=QUOI,
        default=None,
        help=f"sources à figer (défaut : toutes, sauf si --page seul) : {', '.join(QUOI)}",
    )
    s.add_argument(
        "--legi-codes",
        nargs="+",
        default=list(LEGI_CODES),
        help=f"alias ({', '.join(LEGI_CODES)}) ou nom de dossier LEGI (code_...)",
    )
    s.add_argument(
        "--page",
        action="append",
        default=[],
        metavar="URL",
        help="page d'un hôte de la Liste blanche (répétable)",
    )
    s.add_argument("--force", action="store_true", help="retélécharger un fichier déjà présent")

    f = sous.add_parser("fiche", help="texte d'une fiche service-public")
    f.add_argument("doc_id")
    f.add_argument("--dest", type=Path, default=Path("data/raw/eval-sources"))

    for nom, aide in (
        ("assembler", "brouillons -> eval/jeu/<version>/items.jsonl"),
        ("composition", "écarts avec SPEC §2 (Markdown)"),
        ("rejets", "taux de rejet par Tâche et par motif (Markdown)"),
        ("revue", "échantillon de relecture du manifeste -> eval/revue/ (JSONL et Markdown)"),
        ("changements", "items nouveaux, modifiés et retirés -> eval/revue/ (JSONL et Markdown)"),
    ):
        p = sous.add_parser(nom, help=aide)
        p.add_argument("--version", default="v1.0")
        p.add_argument("--racine", type=Path, default=Path("."), help="racine du dépôt")
        if nom == "assembler":
            p.add_argument("--force", action="store_true", help="assembler malgré un MANIFEST.json")
        if nom == "changements":
            p.add_argument(
                "--reference", default="v1.0", help="version de référence gelée (défaut : v1.0)"
            )
    return ap.parse_args(argv)


def main(argv: list[str] | None = None, client: ClientHTTP | None = None) -> int:
    for flux in (sys.stdout, sys.stderr):
        try:
            flux.reconfigure(encoding="utf-8", newline="\n")
        except (AttributeError, ValueError, OSError):
            pass
    a = analyser(argv)
    for option in ("version", "reference"):
        valeur = getattr(a, option, "v1")
        if not re.fullmatch(r"v\d+(\.\d+)*", valeur):
            print(f"{option} invalide : {valeur!r}", file=sys.stderr)
            return 2
    try:
        if a.cmd == "sources":
            return cmd_sources(
                client or ClientHTTP(), a.dest, a.quoi, a.legi_codes, a.page, a.force
            )
        if a.cmd == "fiche":
            return cmd_fiche(a.dest, a.doc_id)
        if a.cmd == "assembler":
            return cmd_assembler(a.racine, a.version, a.force)
        if a.cmd == "composition":
            return cmd_composition(a.racine, a.version)
        if a.cmd == "revue":
            return cmd_revue(a.racine, a.version)
        if a.cmd == "changements":
            return cmd_changements(a.racine, a.version, a.reference)
        return cmd_rejets(a.racine, a.version)
    except ErreurOutil as exc:
        print(f"Erreur ({type(exc).__name__}) : {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
