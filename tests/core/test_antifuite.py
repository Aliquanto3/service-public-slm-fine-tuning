"""API anti-fuite : empreintes, vecteurs, identifiants protégés, sans texte d'item (story 5.1)."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from slmsp.core.items import (
    LIBELLES,
    Jeu,
    empreintes_antifuite,
    identifiants_proteges,
    lire_jeu,
    textes_entree,
    textes_reference,
    vecteurs_antifuite,
)
from slmsp.core.ports import EmbedderPort
from slmsp.core.texte import VERSION_TEXTE, ngrammes, normaliser

RACINE = Path(__file__).resolve().parents[2]
PROVENANCE_URL = "https://www.service-public.gouv.fr/particuliers/vosdroits/F0000"
VERSIONS = ("v1.0", "calibrage")


def _item(code: str, numero: int = 1, **champs: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "id": f"{code}-{numero:03d}",
        "tache": LIBELLES[code],
        "difficulte": "moyen",
        "theme": "collectivites" if code in ("Q", "RD", "LC", "RE") else "non-classe",
        "parametres": {},
        "provenance": [{"source": "<source>", "url": PROVENANCE_URL, "consulte_le": "2026-10-12"}],
        "fictif": True,
        "version_item": 1,
    }
    base.update(champs)
    return base


ITEMS_FACTICES = [
    _item(
        "Q",
        entree="question factice alpha bravo charlie delta echo foxtrot",
        amorce_usager="amorce factice golf hotel india juliett",
        reponse_reference="reponse factice kilo lima mike november oscar",
        elements_cles=["element factice papa quebec romeo sierra", "<b>", "<c>"],
        sources_attendues=["https://www.service-public.gouv.fr/particuliers/vosdroits/F9999"],
        sans_reponse=False,
        mention_obligatoire="mention factice jamais hachee tango uniform victor",
    ),
    _item(
        "RD",
        entree="demande factice whiskey xray yankee zulu un deux",
        appels_attendus=[
            {
                "outil": "get_dataset_info",
                "arguments": {"dataset_id": "dataset-factice-1", "drapeau": True},
                "regles": {"arguments": {"dataset_id": {"exact": "dataset-factice-2"}}},
            },
            {
                "outil": "query_resource_data",
                "arguments": {"resource_id": "ressource-factice-1", "page_size": 5},
                "regles": {"arguments": {"resource_id": {"exact": True}}},
            },
        ],
        cassettes=["../../cassettes/RD-001/s.json"],
        reponse_reference={"texte": "reference factice trois quatre cinq six sept"},
        mode="connecte",
    ),
    _item(
        "CR",
        entree={
            "consigne": "consigne factice huit neuf dix onze",
            "notes": "notes factices a b c d e f",
        },
        decisions_reference=["decision factice douze treize quatorze quinze seize"],
        actions_reference=[
            {
                "action": "action factice vingt-et-un vingt-deux vingt-trois",
                "responsable": "<r>",
                "echeance": "<e>",
            }
        ],
        pieges=["piege factice dix-sept dix-huit dix-neuf vingt"],
    ),
    _item(
        "LC",
        entree={"consigne": "<consigne>", "texte": "texte lc factice aa bb cc dd"},
        informations_a_conserver=["information factice ee ff gg hh ii"],
        termes_juridiques_a_conserver=["terme juridique factice jj kk ll"],
        kandel_moles_entree=40.0,
    ),
    _item(
        "CO",
        entree={"consigne": "<consigne>", "texte": "un textte factice"},
        fautes=[
            {
                "debut": 3,
                "fin": 9,
                "erreur": "textte",
                "correction": "correction mm",
                "type": "o",
            }
        ],
        texte_corrige_reference="texte corrige factice nn oo pp qq",
    ),
    _item(
        "RE",
        entree={"consigne": "<consigne>", "document": "document re factice rr ss tt uu"},
        points_cles_reference=["point cle factice vv ww xx yy"],
        longueur_demandee="courte",
    ),
    _item(
        "CT",
        entree={"consigne": "<consigne>", "objet": "<objet>"},
        type_courrier="<type>",
        elements_obligatoires=["element obligatoire factice zz ab ac"],
        champs_a_laisser_en_emplacement=["[Champ factice ad ae af ag]"],
        valeurs_interdites=["valeur interdite factice ah ai aj"],
    ),
    _item("NR", entree="consigne nr factice g h i j k l", criteres=["critere factice m n o p q"]),
    _item("NR", 2, entree="Capitale du Pérou ?", reponse_reference="Lima."),
    _item(
        "Q",
        2,
        entree="question factice sans amorce utile a b",
        amorce_usager=" ?! ",
        reponse_reference="<r>",
        elements_cles=["<a>", "<b>", "<c>"],
        sources_attendues=[],
        sans_reponse=False,
    ),
]

# Une phrase de référence par champ : (item, texte).
REFERENCES = [
    ("CR-001", "decision factice douze treize quatorze quinze seize"),
    ("CR-001", "action factice vingt-et-un vingt-deux vingt-trois"),
    ("CR-001", "piege factice dix-sept dix-huit dix-neuf vingt"),
    ("LC-001", "information factice ee ff gg hh ii"),
    ("LC-001", "terme juridique factice jj kk ll"),
    ("CO-001", "texte corrige factice nn oo pp qq"),
    ("CO-001", "correction mm"),
    ("RE-001", "point cle factice vv ww xx yy"),
    ("CT-001", "element obligatoire factice zz ab ac"),
    ("CT-001", "Champ factice ad ae af ag"),
    ("CT-001", "valeur interdite factice ah ai aj"),
]


def _empreinte(gramme: tuple[str, ...]) -> str:
    return hashlib.sha256(" ".join(gramme).encode("utf-8")).hexdigest()[:16]


def _premiere(texte: str, n: int = 5) -> str:
    grammes = ngrammes(texte, n) or [tuple(normaliser(texte).split())]
    return _empreinte(grammes[0])


class EmbedderFactice:
    """Embedder déterministe : vecteur = (longueur, nb de mots, 1, 0), normalisé L2."""

    dimension = 4

    def __init__(self, forme: tuple[int, ...] | None = None) -> None:
        self.appels: list[list[str]] = []
        self.forme = forme

    def vectoriser(self, textes: Sequence[str]) -> np.ndarray:
        self.appels.append(list(textes))
        if self.forme is not None:
            return np.zeros(self.forme, dtype=np.float32)
        brut = np.array(
            [[len(t), len(t.split()), 1.0, 0.0] for t in textes], dtype=np.float32
        ).reshape(len(textes), self.dimension)
        return brut / np.linalg.norm(brut, axis=1, keepdims=True)


@pytest.fixture
def racine(tmp_path: Path) -> Path:
    """Racine factice : jeu v1.0 factice et copie du calibrage réel (lu en lecture seule)."""
    chemin = tmp_path / "eval" / "jeu" / "v1.0" / "items.jsonl"
    chemin.parent.mkdir(parents=True)
    chemin.write_text(
        "".join(json.dumps(i, ensure_ascii=False) + "\n" for i in ITEMS_FACTICES),
        encoding="utf-8",
    )
    shutil.copytree(RACINE / "eval" / "calibrage", tmp_path / "eval" / "calibrage")
    return tmp_path


def _textes_items(racine: Path) -> list[str]:
    textes: list[str] = []
    for version in VERSIONS:
        for item in lire_jeu(version, racine).items:
            textes += textes_entree(item) + textes_reference(item)
            textes += [getattr(item, "mention_obligatoire", None) or ""]
    return [t for t in textes if len(t.strip()) >= 12]


def test_embedder_factice_conforme_au_port() -> None:
    assert isinstance(EmbedderFactice(), EmbedderPort)


def test_empreintes_par_item_hachees(racine: Path) -> None:
    empreintes = empreintes_antifuite(VERSIONS, racine=racine)
    calibrage = lire_jeu("calibrage", racine)
    assert empreintes.n == 5 and empreintes.version_texte == VERSION_TEXTE
    assert set(empreintes.par_item) == {f"v1.0/{i['id']}" for i in ITEMS_FACTICES} | {
        f"calibrage/{i.id}" for i in calibrage.items
    }
    assert "calibrage/RD-001" in empreintes.par_item
    for valeurs in empreintes.par_item.values():
        assert valeurs
        assert all(len(v) == 16 and int(v, 16) >= 0 for v in valeurs)
    # Un 5-gramme de l'entrée de Q-001 est retrouvé par son empreinte.
    assert (
        _premiere("question factice alpha bravo charlie delta") in empreintes.par_item["v1.0/Q-001"]
    )
    # Amorce et référence sont couvertes ; la mention obligatoire et la provenance non.
    for texte, present in [
        ("amorce factice golf hotel india juliett", True),
        ("reponse factice kilo lima mike november oscar", True),
        ("mention factice jamais hachee tango uniform victor", False),
    ]:
        assert (_premiere(texte) in empreintes.par_item["v1.0/Q-001"]) is present


def test_jeu_deja_lu_accepte(racine: Path) -> None:
    jeu = lire_jeu("v1.0", racine)
    assert empreintes_antifuite(jeu) == empreintes_antifuite("v1.0", racine=racine)
    assert identifiants_proteges([jeu]) == identifiants_proteges(["v1.0"], racine=racine)


@pytest.mark.parametrize(("identifiant", "texte"), REFERENCES)
def test_empreintes_des_champs_de_reference(racine: Path, identifiant: str, texte: str) -> None:
    empreintes = empreintes_antifuite("v1.0", racine=racine)
    assert _premiere(texte) in empreintes.par_item[f"v1.0/{identifiant}"]


def test_texte_court_empreinte_entiere(racine: Path) -> None:
    empreintes = empreintes_antifuite("v1.0", racine=racine)
    nr2 = empreintes.par_item["v1.0/NR-002"]
    assert _empreinte(("capitale", "du", "pérou")) in nr2
    assert _empreinte(("lima",)) in nr2
    # Une copie mot pour mot, même retouchée en ponctuation, est détectée.
    copie = tuple(normaliser("CAPITALE du Pérou").split())
    assert _empreinte(copie) in nr2


def test_empreintes_detectent_un_quasi_doublon(racine: Path) -> None:
    empreintes = empreintes_antifuite(VERSIONS, racine=racine)
    candidat = "Bonjour ! Reponse factice : KILO, lima mike November oscar et la suite."
    hachees = {_empreinte(g) for g in ngrammes(candidat, empreintes.n)}
    assert hachees & empreintes.par_item["v1.0/Q-001"]
    assert not hachees & empreintes.par_item["v1.0/NR-001"]


def test_empreintes_n_parametrable(racine: Path) -> None:
    assert empreintes_antifuite(VERSIONS, n=3, racine=racine).n == 3
    with pytest.raises(ValueError):
        empreintes_antifuite(VERSIONS, n=0, racine=racine)


def test_vecteurs_entree_et_reference(racine: Path) -> None:
    embedder = EmbedderFactice()
    vecteurs = vecteurs_antifuite(VERSIONS, embedder, racine=racine)
    assert len(embedder.appels) == 1
    assert vecteurs.matrice.shape == (len(vecteurs.cles), 4)
    assert vecteurs.matrice.dtype == np.float32
    for identifiant in ("Q-001", "RD-001", "CR-001", "LC-001", "CO-001", "RE-001", "CT-001"):
        assert f"v1.0/{identifiant}#entree" in vecteurs.cles
        assert f"v1.0/{identifiant}#reference" in vecteurs.cles
    assert "calibrage/CR-001#entree" in vecteurs.cles
    assert all(c.endswith(("#entree", "#reference")) for c in vecteurs.cles)


@pytest.mark.parametrize("forme", [(3,), (3, 4, 1), (2, 4), (11, 3)])
def test_vecteurs_forme_verifiee(racine: Path, forme: tuple[int, ...]) -> None:
    with pytest.raises(ValueError, match="matrice"):
        vecteurs_antifuite("v1.0", EmbedderFactice(forme), racine=racine)


def test_vecteurs_jeu_vide() -> None:
    vide = Jeu("v0", RACINE, RACINE, RACINE / "x", True, ())
    vecteurs = vecteurs_antifuite(vide, EmbedderFactice())
    assert vecteurs.cles == () and vecteurs.matrice.shape == (0, 4)


def test_identifiants_proteges(racine: Path) -> None:
    ids = identifiants_proteges(VERSIONS, racine=racine)
    attendu = hashlib.sha256(normaliser("amorce factice golf hotel india juliett").encode("utf-8"))
    assert attendu.hexdigest() in ids.amorces_sha256
    assert hashlib.sha256(b"").hexdigest() not in ids.amorces_sha256  # amorce « ?! » ignorée
    assert PROVENANCE_URL in ids.urls
    assert "https://www.service-public.gouv.fr/particuliers/vosdroits/F9999" in ids.urls
    assert ids.dataset_ids >= {"dataset-factice-1", "dataset-factice-2"}
    assert "ressource-factice-1" in ids.resource_ids
    assert "True" not in ids.resource_ids | ids.dataset_ids  # booléens exclus
    # Calibrage réel : identifiants du jeu Géo'DAE, URL de la fiche F1344.
    assert "61556e1e9d6adb2df86eb0fc" in ids.dataset_ids
    assert "edb6a9e1-2f16-4bbf-99e7-c3eb6b90794c" in ids.resource_ids
    assert "https://www.service-public.gouv.fr/particuliers/vosdroits/F1344" in ids.urls
    assert len(ids.amorces_sha256) == 3  # Q-001 factice, Q-001 et Q-002 du calibrage


def test_aucun_texte_d_item_renvoye(racine: Path) -> None:
    textes = _textes_items(racine)
    assert len(textes) > 30
    empreintes = empreintes_antifuite(VERSIONS, racine=racine)
    ids = identifiants_proteges(VERSIONS, racine=racine)
    # Les empreintes ne sont que de l'hexadécimal : aucun texte ne peut y figurer.
    assert all(re.fullmatch(r"[0-9a-f]{16}", e) for e in empreintes.toutes())
    assert all(re.fullmatch(r"[0-9a-f]{64}", e) for e in ids.amorces_sha256)
    # Les autres chaînes (clés, URL, identifiants) ne contiennent aucun texte d'item.
    autres = [
        *empreintes.par_item,
        empreintes.algorithme,
        *ids.urls,
        *ids.dataset_ids,
        *ids.resource_ids,
        *vecteurs_antifuite(VERSIONS, EmbedderFactice(), racine=racine).cles,
    ]
    normalisees = [normaliser(c) for c in autres]
    for texte in textes:
        forme = normaliser(texte)
        assert not any(texte in c for c in autres), texte
        assert len(forme) < 12 or not any(forme in c for c in normalisees), texte
