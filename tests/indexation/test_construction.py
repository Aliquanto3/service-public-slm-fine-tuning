"""Construction de l'Index local et `slmsp index build` (story 2.3)."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

import numpy as np
import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.artefacts import ArtefactExistant, EspaceInsuffisant
from slmsp.core.canonique import sha256_fichier
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.schemas.manifeste_index import ManifesteIndex
from slmsp.index.config import (
    NOM_CHUNKS,
    NOM_MANIFESTE,
    NOM_VECTEURS,
    charger_config_index,
)
from slmsp.index.lecture import IndexLocal, ouvrir_index
from slmsp.indexation import construction
from slmsp.indexation.construction import (
    construire_index,
    dossier_parquet,
    ecrire_index,
    lire_source_parquet,
    vecteur_depuis_json,
)

DIMENSION = 1024
VERSION = "20260926"


# --- Vecteurs JSON ---------------------------------------------------------------------


def test_vecteur_valide_renormalise_en_float32() -> None:
    valeurs = [0.0] * DIMENSION
    valeurs[0], valeurs[5] = 3.0, 4
    vecteur = vecteur_depuis_json(json.dumps(valeurs), DIMENSION)
    assert vecteur is not None and vecteur.dtype == np.float32
    assert vecteur[0] == pytest.approx(0.6) and vecteur[5] == pytest.approx(0.8)
    assert float(np.linalg.norm(vecteur)) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "texte",
    [
        None,
        "",
        "pas du json",
        "{}",
        json.dumps([0.1] * (DIMENSION - 1)),
        json.dumps([0.1] * (DIMENSION + 1)),
        json.dumps([[0.1]] * DIMENSION),
        json.dumps(["0.1"] * DIMENSION),
        json.dumps([True] * DIMENSION),
        json.dumps([None] * DIMENSION),
        json.dumps([0.0] * DIMENSION),
        "[" + ",".join(["NaN"] + ["0.1"] * (DIMENSION - 1)) + "]",
        "[" + ",".join(["Infinity"] + ["0.1"] * (DIMENSION - 1)) + "]",
        json.dumps([1e39] + [0.1] * (DIMENSION - 1)),
        b"[0.1]",
    ],
    ids=[
        "nul",
        "vide",
        "illisible",
        "objet",
        "1023",
        "1025",
        "imbrique",
        "chaines",
        "booleens",
        "nuls",
        "norme-nulle",
        "nan",
        "infini",
        "hors-float32",
        "octets",
    ],
)
def test_vecteur_invalide_ecarte(texte) -> None:
    assert vecteur_depuis_json(texte, DIMENSION) is None


# --- Parquet minuscules ----------------------------------------------------------------


def _vecteur_json(graine: int) -> str:
    rng = np.random.default_rng(graine)
    return json.dumps([float(x) for x in rng.standard_normal(DIMENSION) * 0.03])


def _ecrire_parquet(chemin: Path, lignes: list[dict], *, sans: str | None = None) -> None:
    pa = pytest.importorskip("pyarrow")
    pq = pytest.importorskip("pyarrow.parquet")
    colonnes = ["chunk_id", "doc_id", "title", "url", "chunk_text", "embeddings_bge-m3", "autre"]
    colonnes = [c for c in colonnes if c != sans]
    table = pa.table({c: [ligne.get(c) for ligne in lignes] for c in colonnes})
    chemin.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, chemin)


def _ligne(prefixe: str, i: int, vecteur: str | None) -> dict:
    return {
        "chunk_id": f"{prefixe}-c{i}",
        "doc_id": f"{prefixe}-d{i}",
        "title": f"<titre {prefixe} {i}>" if i != 1 else None,
        "url": f"https://exemple.invalid/{prefixe}/{i}",
        "chunk_text": f"<texte factice {prefixe} {i}>",
        "embeddings_bge-m3": vecteur,
        "autre": "ignoré",
    }


def _corpus(racine: Path) -> dict[str, list[dict]]:
    """Parquet des deux sources v1 ; renvoie les lignes valides attendues par source."""
    config = charger_config_index()
    sp, cat = config.sources
    invalide = json.dumps([0.1] * 3)
    sp_b = [_ligne("sp", i, _vecteur_json(100 + i)) for i in range(3)]
    sp_a = [_ligne("sp", 10 + i, _vecteur_json(200 + i)) for i in range(4)]
    sp_a.insert(2, _ligne("sp", 90, None))
    sp_a.append(_ligne("sp", 91, invalide))
    cat_0 = [_ligne("cat", i, _vecteur_json(300 + i)) for i in range(5)]
    cat_0.insert(0, _ligne("cat", 92, "illisible"))
    # Noms choisis pour vérifier l'ordre de lecture : a.parquet avant b.parquet.
    _ecrire_parquet(dossier_parquet(racine, sp) / "b.parquet", sp_b)
    _ecrire_parquet(dossier_parquet(racine, sp) / "a.parquet", sp_a)
    _ecrire_parquet(dossier_parquet(racine, cat) / "part_0.parquet", cat_0)
    (dossier_parquet(racine, sp) / "notes.txt").write_text("ignoré", encoding="utf-8")

    def valides(lignes: list[dict]) -> list[dict]:
        return [ligne for ligne in lignes if ligne["chunk_id"][-2:] not in ("90", "91", "92")]

    return {sp.nom: valides(sp_a) + valides(sp_b), cat.nom: valides(cat_0)}


def _contenu_dossier(dossier: Path) -> dict[str, str]:
    return {
        str(chemin.relative_to(dossier)): sha256_fichier(chemin)
        for chemin in sorted(dossier.rglob("*"))
        if chemin.is_file()
    }


def test_build_nominal_puis_refus(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    attendues = _corpus(tmp_path)
    assert main(["index", "build", "--racine", str(tmp_path)]) == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert f"Index {VERSION}" in sortie and "service-public : 7 chunks, 2 écartés" in sortie

    dossier = tmp_path / "index" / VERSION
    assert sorted(p.name for p in (tmp_path / "index").iterdir()) == [VERSION]
    assert sorted(p.name for p in dossier.iterdir()) == sorted(
        [NOM_VECTEURS, NOM_CHUNKS, NOM_MANIFESTE]
    )

    manifeste = ManifesteIndex.model_validate_json((dossier / NOM_MANIFESTE).read_bytes())
    assert (dossier / NOM_MANIFESTE).read_bytes().endswith(b"}\n")
    assert manifeste.version == VERSION and manifeste.date_snapshot.isoformat() == "2026-09-26"
    assert manifeste.modele_embedding == "BAAI/bge-m3" and manifeste.dtype == "float16"
    assert manifeste.chunks_par_source() == {
        "service-public": 7,
        "data-gouv-datasets-catalog": 5,
    }
    assert [s.nb_ecartes for s in manifeste.sources] == [2, 1]
    assert manifeste.nb_chunks == 12
    sp_dossier = dossier_parquet(tmp_path, charger_config_index().sources[0])
    assert manifeste.sources[0].parquet == {
        "a.parquet": sha256_fichier(sp_dossier / "a.parquet"),
        "b.parquet": sha256_fichier(sp_dossier / "b.parquet"),
    }
    assert manifeste.fichiers == {
        NOM_VECTEURS: sha256_fichier(dossier / NOM_VECTEURS),
        NOM_CHUNKS: sha256_fichier(dossier / NOM_CHUNKS),
    }

    vecteurs = np.load(dossier / NOM_VECTEURS)
    assert vecteurs.shape == (12, DIMENSION) and vecteurs.dtype == np.float16
    np.testing.assert_allclose(
        np.linalg.norm(vecteurs.astype(np.float32), axis=1), 1.0, rtol=0, atol=2e-3
    )
    connexion = sqlite3.connect(dossier / NOM_CHUNKS)
    lignes = connexion.execute(
        "SELECT rang, chunk_id, doc_id, source, titre, url, texte, date_snapshot "
        "FROM chunks ORDER BY rang"
    ).fetchall()
    connexion.close()
    attendu = [("service-public", "2026-09-25", ligne) for ligne in attendues["service-public"]]
    attendu += [
        ("data-gouv-datasets-catalog", "2026-09-26", ligne)
        for ligne in attendues["data-gouv-datasets-catalog"]
    ]
    assert [ligne[0] for ligne in lignes] == list(range(12))
    for (rang, chunk_id, doc_id, source, titre, url, texte, jour), (nom, date, brute) in zip(
        lignes, attendu, strict=True
    ):
        assert (chunk_id, doc_id, source, jour) == (brute["chunk_id"], brute["doc_id"], nom, date)
        assert (titre, url, texte) == (brute["title"] or "", brute["url"], brute["chunk_text"])
        reference = vecteur_depuis_json(brute["embeddings_bge-m3"], DIMENSION)
        np.testing.assert_array_equal(vecteurs[rang], reference.astype(np.float16))

    with ouvrir_index(tmp_path) as index:
        index.verifier()
        passages = index.rechercher(vecteurs[8].astype(np.float32), 1)
        assert passages[0].chunk_id == attendu[8][2]["chunk_id"]

    avant = _contenu_dossier(tmp_path)
    assert main(["index", "build", "--racine", str(tmp_path)]) == CodeSortie.ERREUR
    assert "existe déjà" in capsys.readouterr().err
    assert _contenu_dossier(tmp_path) == avant
    assert sorted(p.name for p in (tmp_path / "index").iterdir()) == [VERSION]


def test_version_existante_refusee_avant_toute_lecture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "index" / VERSION).mkdir(parents=True)

    def interdit(*_args, **_kwargs):
        raise AssertionError("aucune lecture attendue")

    monkeypatch.setattr(construction, "lire_source_parquet", interdit)
    monkeypatch.setattr(construction, "fichiers_parquet", interdit)
    with pytest.raises(ArtefactExistant, match="jamais reconstruit"):
        construire_index(charger_config_index(), tmp_path)
    assert list((tmp_path / "index" / VERSION).iterdir()) == []


@pytest.mark.parametrize("cas", ["dossier-absent", "dossier-vide"])
def test_parquet_absent(tmp_path: Path, capsys: pytest.CaptureFixture[str], cas: str) -> None:
    config = charger_config_index()
    sp, cat = config.sources
    _ecrire_parquet(
        dossier_parquet(tmp_path, sp) / "a.parquet", [_ligne("sp", 0, _vecteur_json(1))]
    )
    if cas == "dossier-vide":
        dossier_parquet(tmp_path, cat).mkdir(parents=True)
    assert main(["index", "build", "--racine", str(tmp_path)]) == CodeSortie.ERREUR
    erreur = capsys.readouterr().err
    assert "aucun fichier parquet" in erreur
    assert str(dossier_parquet(tmp_path, cat)) in erreur
    assert not (tmp_path / "index").exists()


def test_colonne_absente(tmp_path: Path) -> None:
    config = charger_config_index()
    sp = config.sources[0]
    _ecrire_parquet(
        dossier_parquet(tmp_path, sp) / "a.parquet",
        [_ligne("sp", 0, _vecteur_json(1))],
        sans="chunk_text",
    )
    with pytest.raises(ConfigurationInvalide, match="chunk_text"):
        lire_source_parquet(sp, tmp_path, config)


def test_lecture_par_petits_lots(tmp_path: Path) -> None:
    config = charger_config_index().model_copy(update={"taille_lot_lecture": 2})
    sp = config.sources[0]
    lignes = [_ligne("sp", i, _vecteur_json(i) if i % 3 else None) for i in range(9)]
    _ecrire_parquet(dossier_parquet(tmp_path, sp) / "a.parquet", lignes)
    lue = lire_source_parquet(sp, tmp_path, config)
    assert lue.nb_chunks == 6 and lue.nb_ecartes == 3
    assert [ligne[0] for ligne in lue.lignes] == [f"sp-c{i}" for i in range(9) if i % 3]
    assert lue.vecteurs.shape == (6, DIMENSION) and lue.vecteurs.dtype == np.float16


def test_ecrire_index_refus(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = charger_config_index()
    sp = config.sources[0]
    _ecrire_parquet(
        dossier_parquet(tmp_path, sp) / "a.parquet", [_ligne("sp", 0, _vecteur_json(1))]
    )
    lue = lire_source_parquet(sp, tmp_path, config)
    dossier = tmp_path / "index"
    with pytest.raises(ValueError, match="AAAAMMJJ"):
        ecrire_index(dossier, "2026-09-25", [lue], config)
    with pytest.raises(ValueError, match="date de snapshot"):
        ecrire_index(dossier, "20260926", [lue], config)
    vide = construction.SourceLue(
        source=sp, vecteurs=np.empty((0, DIMENSION), dtype=np.float16), lignes=[]
    )
    with pytest.raises(ConfigurationInvalide, match="aucun chunk"):
        ecrire_index(dossier, "20260925", [vide], config)

    def plein(chemin, octets, **_kwargs):
        raise EspaceInsuffisant(f"espace disque insuffisant sous {chemin}")

    monkeypatch.setattr(construction, "verifier_espace", plein)
    with pytest.raises(EspaceInsuffisant):
        ecrire_index(dossier, "20260925", [lue], config)
    assert not dossier.exists()


def test_rename_concurrent_laisse_le_dossier_en_cours(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = charger_config_index()
    sp = config.sources[0]
    _ecrire_parquet(
        dossier_parquet(tmp_path, sp) / "a.parquet", [_ligne("sp", 0, _vecteur_json(1))]
    )
    lue = lire_source_parquet(sp, tmp_path, config)

    def concurrent(source, cible):
        Path(cible).mkdir()
        raise FileExistsError(cible)

    monkeypatch.setattr(construction.os, "rename", concurrent)
    with pytest.raises(ArtefactExistant, match="pendant la construction"):
        ecrire_index(tmp_path / "index", "20260925", [lue], config)
    restes = sorted(p.name for p in (tmp_path / "index").iterdir())
    assert restes[0].startswith(".20260925.en-cours-") and restes[1] == "20260925"
    assert sorted(p.name for p in (tmp_path / "index" / restes[0]).iterdir()) == sorted(
        [NOM_VECTEURS, NOM_CHUNKS, NOM_MANIFESTE]
    )


# --- Construction réelle (lent) ----------------------------------------------------------


def racine_reelle() -> Path:
    """Racine du dépôt qui porte `data/raw/mediatech` : `SLMSP_RACINE_REELLE` ou le projet.

    Depuis un worktree `.claude/worktrees/<nom>`, le dépôt principal est pris par défaut.
    """
    valeur = os.environ.get("SLMSP_RACINE_REELLE", "").strip()
    if valeur:
        return Path(valeur).resolve()
    racine = racine_projet()
    parties = racine.parts
    if ".claude" in parties and "worktrees" in parties:
        return Path(*parties[: parties.index(".claude")])
    return racine


@pytest.mark.lent
def test_reel_build_et_index(tmp_path: Path) -> None:
    """Lit les vrais parquet MediaTech et construit l'Index dans un dossier temporaire."""
    racine = racine_reelle()
    config = charger_config_index()
    for source in config.sources:
        if not dossier_parquet(racine, source).is_dir():
            pytest.skip(f"parquet absents sous {dossier_parquet(racine, source)}")
    lues = [lire_source_parquet(source, racine, config) for source in config.sources]
    totaux = {lue.source.nom: lue.nb_chunks + lue.nb_ecartes for lue in lues}
    assert totaux == {"service-public": 35_758, "data-gouv-datasets-catalog": 107_679}
    dossier = ecrire_index(tmp_path / "index", config.version(), lues, config)
    assert dossier.name == VERSION
    with IndexLocal(dossier) as index:
        index.verifier()
        for rang in (0, 35_757, index.nb_chunks - 1):
            rangs, _ = index.classer(index.vecteurs()[rang].astype(np.float32), 1)
            assert np.array_equal(index.vecteurs()[rangs[0]], index.vecteurs()[rang])


@pytest.mark.lent
def test_reel_index_principal_coherent() -> None:
    """Index réel du dépôt principal (construit par `slmsp index build`) : SHA et comptes."""
    racine = racine_reelle()
    if not (racine / "index" / VERSION).is_dir():
        pytest.skip(f"Index {VERSION} absent sous {racine / 'index'}")
    with ouvrir_index(racine, VERSION) as index:
        index.verifier()
        comptes = index.manifeste.chunks_par_source()
        ecartes = {s.nom: s.nb_ecartes for s in index.manifeste.sources}
        assert comptes["service-public"] + ecartes["service-public"] == 35_758
        assert (
            comptes["data-gouv-datasets-catalog"] + ecartes["data-gouv-datasets-catalog"] == 107_679
        )


# --- Configuration ---------------------------------------------------------------------


def test_sources_index_alignees_sur_sources_toml() -> None:
    """`config/index.toml` reprend le nom et la révision des jeux de `config/sources.toml`."""
    from slmsp.fetch.config import charger_config_sources

    jeux = {jeu.nom: jeu for jeu in charger_config_sources().jeux}
    racine = Path("racine-factice")
    for source in charger_config_index().sources:
        assert source.jeu in jeux, f"jeu {source.jeu} absent de config/sources.toml"
        jeu = jeux[source.jeu]
        assert source.revision == jeu.revision
        # Même disposition que `slmsp.fetch.sources.dossier_jeu` (data/raw/mediatech/<jeu>/<rev>).
        attendu = racine / "data" / "raw" / "mediatech" / jeu.nom / jeu.revision
        assert dossier_parquet(racine, source) == attendu


def _config_toml(tmp_path: Path, remplacer: tuple[str, str]) -> Path:
    texte = (racine_projet() / "config" / "index.toml").read_text(encoding="utf-8")
    assert remplacer[0] in texte
    chemin = tmp_path / "index.toml"
    chemin.write_text(texte.replace(*remplacer, 1), encoding="utf-8")
    return chemin


def test_config_sources_homonymes_refusees(tmp_path: Path) -> None:
    chemin = _config_toml(
        tmp_path, ('nom = "data-gouv-datasets-catalog"', 'nom = "service-public"')
    )
    with pytest.raises(ConfigurationInvalide, match="même nom"):
        charger_config_index(chemin)


@pytest.mark.parametrize("valeur", ["1.5", "-1.5"])
def test_config_seuil_pertinence_borne(tmp_path: Path, valeur: str) -> None:
    chemin = _config_toml(tmp_path, ("seuil_pertinence = 0.5", f"seuil_pertinence = {valeur}"))
    with pytest.raises(ConfigurationInvalide, match="seuil_pertinence"):
        charger_config_index(chemin)
