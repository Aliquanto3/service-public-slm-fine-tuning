"""Contrôles du jeu de développement `devN` (story O4a, spec O4). Hors paquet `slmsp`.

Lancement (venv du dépôt, `slmsp` importable) :

    python eval/outils/verifier_jeu_croise.py disjonction --version dev1
    python eval/outils/verifier_jeu_croise.py verifier --version dev1 --juges deepseek,glm

Sous-commandes :

- `disjonction` : aucun item de `devN` ne partage une URL, un texte source ou un recouvrement
  de n-grammes (seuils de `config/donnees.toml`, `[anti_fuite]`) avec v1.0, v1.1 ni avec les
  jeux d'entraînement `data/train/v*/train.jsonl` ni les amorces `runs/data-seed/*/amorces.jsonl`.
  Lecture seule, aucun réseau ; code de
  sortie 1 au moindre conflit. Le cosinus d'embeddings n'est pas recalculé ici : `seed` et
  `filter` l'appliquent aux versions protégées (dont `devN`).
- `verifier` : contre-vérification croisée (cohérence item / référence / grille, ambiguïté,
  fait de référence absent de la source) par des juges tiers OpenRouter (`juges.toml`,
  `[juges_tiers.<nom>]`, usage `juge-tiers-openrouter`, journal des juges tiers). Un item jugé
  incohérent ou ambigu par l'un des juges est écarté. Les verdicts s'ajoutent à
  `eval/construction/<version>/verdicts-croises.jsonl` (ajout seul) et le taux de rejet est
  écrit dans `rapport-verification-croisee.json`. Appels payants : lancés par l'orchestrateur ;
  les tests injectent un faux appelant.

Aucun contenu d'entraînement n'est produit : les juges ne reçoivent que des items d'évaluation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

MOTIF_DEV = re.compile(r"^dev[0-9]+$")
VERSIONS_REFERENCE = ("v1.0", "v1.1")
SEUIL_DEFAUT = 0.5
N_DEFAUT = 5
MOTS_TEXTE_MIN = 3
"""Une valeur texte de moins de mots n'est pas retenue comme « texte » identique (« oui »)."""
NOM_VERDICTS = "verdicts-croises.jsonl"
NOM_RAPPORT = "rapport-verification-croisee.json"
USAGE_BUDGET = "juge-tiers-openrouter"
DEFAUT_JUGES = ("deepseek", "glm")

Appelant = Callable[[str, str], str]
"""`appeler(nom_du_juge, prompt) -> texte brut de la réponse` (injecté dans les tests)."""


class ErreurOutil(Exception):
    """Erreur d'usage ou de données, affichée sans trace."""


# --- Lecture ---------------------------------------------------------------------------------


def lire_jsonl(chemin: Path) -> list[dict[str, Any]]:
    """Lignes JSON d'un fichier (UTF-8) ; une ligne illisible lève `ErreurOutil`."""
    lignes: list[dict[str, Any]] = []
    for rang, ligne in enumerate(chemin.read_text(encoding="utf-8").splitlines(), 1):
        if not ligne.strip():
            continue
        try:
            valeur = json.loads(ligne)
        except json.JSONDecodeError as exc:
            raise ErreurOutil(f"{chemin} ligne {rang} : JSON invalide ({exc.msg})") from None
        if not isinstance(valeur, dict):
            raise ErreurOutil(f"{chemin} ligne {rang} : objet JSON attendu")
        lignes.append(valeur)
    return lignes


def _textes(valeur: Any) -> Iterator[str]:
    if isinstance(valeur, str):
        yield valeur
    elif isinstance(valeur, Mapping):
        for cle, sous in valeur.items():
            if cle != "consigne":
                yield from _textes(sous)
    elif isinstance(valeur, list):
        for sous in valeur:
            yield from _textes(sous)


def _normaliser(texte: str) -> str:
    from slmsp.core.texte import normaliser

    return normaliser(texte)


def url_canonique(url: str) -> str:
    """URL sans fragment, requête ni barre finale, en minuscules (hôte et chemin)."""
    morceaux = urlsplit(url.strip())
    return f"{morceaux.netloc}{morceaux.path.rstrip('/')}".lower()


def urls_item(item: Mapping[str, Any]) -> set[str]:
    """URL de provenance d'un item (`url` de chaque entrée de `provenance`) et
    `sources_attendues` des Q (comme `slmsp.core.items`)."""
    urls: set[str] = set()
    for source in item.get("provenance") or []:
        if isinstance(source, Mapping) and isinstance(source.get("url"), str):
            urls.add(url_canonique(source["url"]))
    reference = item.get("reference")
    for conteneur in (item, reference if isinstance(reference, Mapping) else {}):
        for url in conteneur.get("sources_attendues") or []:
            if isinstance(url, str) and url.strip():
                urls.add(url_canonique(url))
    return urls


def textes_item(item: Mapping[str, Any]) -> list[str]:
    """Textes de `entree` (hors `consigne`), normalisés."""
    return [t for t in (_normaliser(x) for x in _textes(item.get("entree"))) if t]


def textes_exemple(exemple: Mapping[str, Any]) -> tuple[list[str], set[str]]:
    """Textes normalisés et URL d'un exemple d'entraînement (`messages`, `meta.source`)."""
    brut: list[str] = []
    urls: set[str] = set()
    for message in exemple.get("messages") or []:
        contenu = message.get("content") if isinstance(message, Mapping) else None
        if isinstance(contenu, str):
            brut.append(contenu)
    meta = exemple.get("meta")
    source = meta.get("source") if isinstance(meta, Mapping) else None
    if isinstance(source, str) and source.startswith("http"):
        urls.add(url_canonique(source))
    return [t for t in (_normaliser(x) for x in brut) if t], urls


def _ngrammes(texte: str, n: int) -> set[tuple[str, ...]]:
    jetons = texte.split()
    if len(jetons) < n:
        return {tuple(jetons)} if jetons else set()
    return {tuple(jetons[i : i + n]) for i in range(len(jetons) - n + 1)}


def seuils(racine: Path) -> tuple[int, float]:
    """`(n_ngrammes, seuil)` de `config/donnees.toml` `[anti_fuite]` (défauts 5 et 0,5)."""
    chemin = racine / "config" / "donnees.toml"
    if not chemin.is_file():
        return N_DEFAUT, SEUIL_DEFAUT
    section = tomllib.loads(chemin.read_text(encoding="utf-8")).get("anti_fuite", {})
    return int(section.get("n_ngrammes", N_DEFAUT)), float(
        section.get("seuil_jaccard", SEUIL_DEFAUT)
    )


# --- Disjonction -----------------------------------------------------------------------------


class _Reference:
    """Index des jeux déjà existants : URL, textes identiques et n-grammes."""

    def __init__(self, n: int) -> None:
        self.n = n
        self.urls: dict[str, str] = {}
        self.textes: dict[str, str] = {}
        self.ids: dict[str, str] = {}
        self.grammes: dict[tuple[str, ...], list[int]] = {}
        self.tailles: list[int] = []
        self.noms: list[str] = []

    def ajouter(self, nom: str, textes: Iterable[str], urls: Iterable[str]) -> None:
        for url in urls:
            self.urls.setdefault(url, nom)
        ensemble: set[tuple[str, ...]] = set()
        for texte in textes:
            if len(texte.split()) >= MOTS_TEXTE_MIN:
                self.textes.setdefault(texte, nom)
            ensemble |= _ngrammes(texte, self.n)
        rang = len(self.noms)
        self.noms.append(nom)
        self.tailles.append(len(ensemble))
        for gramme in ensemble:
            self.grammes.setdefault(gramme, []).append(rang)

    def recouvrement(self, textes: Iterable[str]) -> tuple[float, str | None]:
        """Plus grand coefficient d'inclusion `|A ∩ B| / min(|A|, |B|)` et la référence."""
        ensemble: set[tuple[str, ...]] = set()
        for texte in textes:
            ensemble |= _ngrammes(texte, self.n)
        if not ensemble:
            return 0.0, None
        communs: Counter[int] = Counter()
        for gramme in ensemble:
            for rang in self.grammes.get(gramme, ()):
                communs[rang] += 1
        meilleur, nom = 0.0, None
        for rang, nombre in communs.items():
            valeur = nombre / min(len(ensemble), self.tailles[rang])
            if valeur > meilleur:
                meilleur, nom = valeur, self.noms[rang]
        return meilleur, nom


def construire_reference(racine: Path, n: int) -> tuple[_Reference, list[str]]:
    """Index de v1.0, v1.1, `data/train/v*/train.jsonl` et des amorces des runs seed
    (`runs/data-seed/*/amorces.jsonl`) ; liste des jeux lus."""
    reference = _Reference(n)
    lus: list[str] = []
    for version in VERSIONS_REFERENCE:
        chemin = racine / "eval" / "jeu" / version / "items.jsonl"
        if not chemin.is_file():
            continue
        lus.append(version)
        for item in lire_jsonl(chemin):
            nom = f"{version}/{item.get('id', '?')}"
            reference.ids.setdefault(str(item.get("id")), nom)
            reference.ajouter(nom, textes_item(item), urls_item(item))
    train = racine / "data" / "train"
    if train.is_dir():
        for dossier in sorted(train.glob("v*")):
            chemin = dossier / "train.jsonl"
            if not chemin.is_file():
                continue
            lus.append(f"data/train/{dossier.name}")
            for rang, exemple in enumerate(lire_jsonl(chemin), 1):
                textes, urls = textes_exemple(exemple)
                reference.ajouter(f"data/train/{dossier.name}#{rang}", textes, urls)
    seeds = racine / "runs" / "data-seed"
    if seeds.is_dir():
        for chemin in sorted(seeds.glob("*/amorces.jsonl")):
            nom_run = chemin.parent.name
            lus.append(f"runs/data-seed/{nom_run}")
            for amorce in lire_jsonl(chemin):
                texte = amorce.get("texte")
                textes = [t for t in [_normaliser(texte)] if t] if isinstance(texte, str) else []
                reference.ajouter(
                    f"runs/data-seed/{nom_run}/{amorce.get('amorce_id', '?')}", textes, ()
                )
    return reference, lus


def controler_disjonction(
    items: Sequence[Mapping[str, Any]],
    racine: Path,
    *,
    n: int | None = None,
    seuil: float | None = None,
) -> list[str]:
    """Conflits des `items` avec les jeux existants (liste vide : disjoints)."""
    n_cfg, seuil_cfg = seuils(racine)
    n = n or n_cfg
    seuil = seuil if seuil is not None else seuil_cfg
    reference, _ = construire_reference(racine, n)
    conflits: list[str] = []
    vus: dict[str, str] = {}
    for item in items:
        identifiant = str(item.get("id"))
        if identifiant in reference.ids:
            conflits.append(
                f"{identifiant} : identifiant déjà pris par {reference.ids[identifiant]}"
            )
        if identifiant in vus:
            conflits.append(f"{identifiant} : identifiant en double dans le jeu")
        vus[identifiant] = identifiant
        for url in sorted(urls_item(item)):
            if url in reference.urls:
                conflits.append(
                    f"{identifiant} : URL source déjà utilisée par {reference.urls[url]}"
                )
        textes = textes_item(item)
        for texte in textes:
            if texte in reference.textes:
                conflits.append(f"{identifiant} : texte identique à {reference.textes[texte]}")
                break
        valeur, nom = reference.recouvrement(textes)
        if valeur >= seuil:
            conflits.append(f"{identifiant} : recouvrement {valeur:.2f} avec {nom} (seuil {seuil})")
    return conflits


# --- Contre-vérification croisée -------------------------------------------------------------

CRITERES = ("coherent", "ambigu", "fait_absent_de_la_source")


def prompt_verification(item: Mapping[str, Any]) -> str:
    """Consigne de contre-vérification d'un item d'évaluation (aucun exemple de réponse)."""
    corps = json.dumps(item, ensure_ascii=False, indent=2, sort_keys=True)
    return (
        "Tu contre-vérifies un item d'un jeu d'évaluation. Lis l'item ci-dessous (entrée, "
        "référence, grille, provenance) et réponds par un seul objet JSON de clés : "
        '"coherent" (booléen : l\'item, sa référence et sa grille sont cohérents entre eux), '
        '"ambigu" (booléen : plusieurs réponses justes non prévues par la référence sont '
        'possibles), "fait_absent_de_la_source" (booléen : un fait de la référence ne figure '
        'pas dans la source fournie), "remarque" (texte court).\n\nITEM :\n' + corps
    )


def lire_verdict(texte: str) -> dict[str, Any] | None:
    """Premier objet JSON de `texte` s'il porte les trois critères booléens, sinon `None`."""
    debut = texte.find("{")
    fin = texte.rfind("}")
    if debut < 0 or fin <= debut:
        return None
    try:
        valeur = json.loads(texte[debut : fin + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(valeur, dict) or not all(isinstance(valeur.get(c), bool) for c in CRITERES):
        return None
    return {**{c: valeur[c] for c in CRITERES}, "remarque": str(valeur.get("remarque", ""))[:500]}


def decision(verdicts: Mapping[str, dict[str, Any] | None]) -> tuple[str, list[str]]:
    """`(retenu | rejete | incomplet, motifs)` : un juge sans verdict valide laisse l'item
    `incomplet` (rejouable, non retenu) ; sinon un seul grief d'un juge suffit à écarter."""
    motifs: list[str] = []
    for juge, verdict in sorted(verdicts.items()):
        if verdict is None:
            return "incomplet", [f"{juge} : pas de verdict valide"]
        if not verdict["coherent"]:
            motifs.append(f"{juge} : incohérent")
        if verdict["ambigu"]:
            motifs.append(f"{juge} : ambigu")
        if verdict["fait_absent_de_la_source"]:
            motifs.append(f"{juge} : fait absent de la source")
    return ("rejete" if motifs else "retenu"), motifs


def verifier_items(
    items: Sequence[Mapping[str, Any]], juges: Sequence[str], appeler: Appelant
) -> list[dict[str, Any]]:
    """Une ligne de verdict par item : verdict de chaque juge, décision et motifs."""
    lignes: list[dict[str, Any]] = []
    for item in items:
        prompt = prompt_verification(item)
        verdicts: dict[str, dict[str, Any] | None] = {}
        for juge in juges:
            try:
                verdicts[juge] = lire_verdict(appeler(juge, prompt))
            except Exception as exc:  # noqa: BLE001 - un échec d'appel laisse l'item rejouable
                verdicts[juge] = None
                print(f"{item.get('id')} : {juge} : {type(exc).__name__}", file=sys.stderr)
        etat, motifs = decision(verdicts)
        lignes.append(
            {
                "item_id": item.get("id"),
                "item_sha256": empreinte_item(item),
                "tache": item.get("tache"),
                "juges": verdicts,
                "decision": etat,
                "motifs": motifs,
            }
        )
    return lignes


def rapport_rejets(lignes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Taux de rejet global et par Tâche (les `incomplet` comptent à part)."""
    par_tache: dict[str, Counter[str]] = {}
    for ligne in lignes:
        par_tache.setdefault(str(ligne.get("tache")), Counter())[str(ligne["decision"])] += 1

    def _bilan(c: Counter[str]) -> dict[str, Any]:
        total = sum(c.values())
        return {
            "total": total,
            "retenus": c["retenu"],
            "rejetes": c["rejete"],
            "incomplets": c["incomplet"],
            "taux_rejet": round(c["rejete"] / total, 4) if total else None,
        }

    global_ = Counter[str]()
    for compte in par_tache.values():
        global_.update(compte)
    return {
        "global": _bilan(global_),
        "par_tache": {t: _bilan(c) for t, c in sorted(par_tache.items())},
    }


def empreinte_item(item: Mapping[str, Any]) -> str:
    """SHA-256 du JSON canonique de l'item : un item modifié est revérifié."""
    canonique = json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonique.encode("utf-8")).hexdigest()


def verdicts_courants(chemin: Path) -> dict[str, dict[str, Any]]:
    """Dernier verdict de chaque item (le fichier est en ajout seul)."""
    if not chemin.is_file():
        return {}
    return {str(ligne["item_id"]): ligne for ligne in lire_jsonl(chemin)}


def ouvrir_appelant(juges: Sequence[str], racine: Path) -> Appelant:
    """Appelant réel : clients OpenRouter des `juges` (`juges.toml`), usage de budget dérivé.

    Lève `SecretManquant` / `ValueError` comme `ouvrir_juge_tiers`. Jamais utilisé en test.
    """
    from slmsp.evaluation.juges_tiers import ouvrir_juge_tiers
    from slmsp.fournisseurs.client import nouvelle_session

    ouverts = {nom: ouvrir_juge_tiers(nom, racine) for nom in juges}
    session = nouvelle_session("jeu-croise-")

    def appeler(nom: str, prompt: str) -> str:
        juge = ouverts[nom]
        reponse = juge.client.appeler(
            juge.config.usage_budget,
            session,
            [{"role": "user", "content": prompt}],
            modele=juge.config.modele,
            max_tokens=juge.config.max_tokens,
            tokens_entree_estimes=max(1, len(prompt) // 3),
            parametres={
                "response_format": {"type": "json_object"},
                "provider": {"require_parameters": True},
            },
        )
        return reponse.texte

    return appeler


# --- Commandes -------------------------------------------------------------------------------


def _version(valeur: str) -> str:
    if not MOTIF_DEV.fullmatch(valeur):
        raise ErreurOutil(f"version invalide : {valeur!r} (attendu : devN)")
    return valeur


def charger_items(racine: Path, version: str) -> list[dict[str, Any]]:
    """Items de `eval/jeu/<version>/items.jsonl`, sinon des brouillons `eval/construction/`."""
    assemble = racine / "eval" / "jeu" / version / "items.jsonl"
    if assemble.is_file():
        return lire_jsonl(assemble)
    construction = racine / "eval" / "construction" / version
    fichiers = sorted(
        p for p in construction.glob("*.jsonl") if re.fullmatch(r"[A-Z]{1,2}", p.stem)
    )
    if not fichiers:
        raise ErreurOutil(f"aucun item pour {version} ({assemble} ni {construction}/<CODE>.jsonl)")
    return [item for fichier in fichiers for item in lire_jsonl(fichier)]


def cmd_disjonction(racine: Path, version: str) -> int:
    items = charger_items(racine, _version(version))
    _, lus = construire_reference(racine, seuils(racine)[0])
    conflits = controler_disjonction(items, racine)
    print(f"{len(items)} item(s) de {version} contre : {', '.join(lus) or 'aucun jeu'}")
    for conflit in conflits:
        print(f"CONFLIT {conflit}")
    if not conflits:
        print("disjoint")
    return 1 if conflits else 0


def cmd_verifier(
    racine: Path, version: str, juges: Sequence[str], appeler: Appelant | None = None
) -> int:
    items = charger_items(racine, _version(version))
    construction = racine / "eval" / "construction" / version
    chemin = construction / NOM_VERDICTS
    deja = verdicts_courants(chemin)

    def _a_jour(item: Mapping[str, Any], ligne: Mapping[str, Any] | None) -> bool:
        return ligne is not None and ligne.get("item_sha256") == empreinte_item(item)

    a_faire = [
        i
        for i in items
        if not _a_jour(i, deja.get(str(i.get("id"))))
        or deja[str(i.get("id"))].get("decision") == "incomplet"
    ]
    if appeler is None:
        appeler = ouvrir_appelant(juges, racine)
    lignes = verifier_items(a_faire, juges, appeler)
    construction.mkdir(parents=True, exist_ok=True)
    with chemin.open("a", encoding="utf-8", newline="\n") as sortie:
        for ligne in lignes:
            sortie.write(json.dumps(ligne, ensure_ascii=False, sort_keys=True) + "\n")
    courants = verdicts_courants(chemin)
    rapport = rapport_rejets(
        [courants[str(i.get("id"))] for i in items if _a_jour(i, courants.get(str(i.get("id"))))]
    )
    rapport["juges"] = list(juges)
    (construction / NOM_RAPPORT).write_text(
        json.dumps(rapport, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    bilan = rapport["global"]
    print(
        f"{len(lignes)} item(s) vérifié(s) ; retenus {bilan['retenus']}, rejetés "
        f"{bilan['rejetes']}, incomplets {bilan['incomplets']} "
        f"(taux de rejet {bilan['taux_rejet']})"
    )
    return 1 if bilan["incomplets"] else 0


def main(argv: Sequence[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sous = parseur.add_subparsers(dest="commande", required=True)
    for nom in ("disjonction", "verifier"):
        p = sous.add_parser(nom)
        p.add_argument("--version", required=True, help="version du jeu de développement (devN)")
        p.add_argument("--racine", type=Path, default=Path(__file__).resolve().parents[2])
        if nom == "verifier":
            p.add_argument("--juges", default=",".join(DEFAUT_JUGES), help="noms de juges tiers")
    args = parseur.parse_args(argv)
    try:
        if args.commande == "disjonction":
            return cmd_disjonction(args.racine, args.version)
        juges = [j for j in args.juges.split(",") if j]
        if len(juges) < 2:
            raise ErreurOutil("la contre-vérification croisée exige au moins deux juges")
        return cmd_verifier(args.racine, args.version, juges)
    except ErreurOutil as exc:
        print(f"verifier_jeu_croise : {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
