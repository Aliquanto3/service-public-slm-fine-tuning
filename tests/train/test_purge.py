"""Purge des intermédiaires d'export et contrôle d'espace (story C8).

Dossiers temporaires factices : aucun vrai export, aucun GPU.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from slmsp.cli import main
from slmsp.core.artefacts import nouveau_run, ouvrir_run
from slmsp.core.erreurs import CodeSortie
from slmsp.train import purge
from slmsp.train.config import charger_config_export

Q4: bytes = b"q" * 6000


def faux_export(
    racine: Path, *, q4: bytes | None = Q4, slug: str = "ft-test", statut: str = "complet"
) -> str:
    run = nouveau_run("export", slug, {"source": "train"}, racine=racine)
    (run.dossier / "hf-f16").mkdir()
    (run.dossier / "hf-f16" / "model.safetensors").write_bytes(b"x" * 1000)
    (run.dossier / "modele-f16.gguf").write_bytes(b"y" * 20000)
    (run.dossier / "mmproj-f16.gguf").write_bytes(b"m" * 10)
    if q4 is not None:
        (run.dossier / "modele-q4_k_m.gguf").write_bytes(q4)
    if statut:
        run.terminer(statut)
    return run.run_id


def fausse_notation(racine: Path, export_id: str, statut: str = "complet") -> str:
    run = nouveau_run("eval-notation", "ft-test", {}, racine=racine, modele_ref=f"ft:{export_id}")
    if statut:
        run.terminer(statut)
    return run.run_id


def args(racine: Path, *reste: str) -> list[str]:
    return ["export", "purger", *reste, "--racine", str(racine)]


def test_purge_export_note(tmp_path: Path, capsys) -> None:
    export_id = faux_export(tmp_path)
    notation = fausse_notation(tmp_path, export_id)
    assert main(args(tmp_path, "--depuis", export_id)) == CodeSortie.SUCCES
    dossier = tmp_path / "runs" / "export" / export_id
    assert not (dossier / "hf-f16").exists() and not (dossier / "modele-f16.gguf").exists()
    assert (dossier / "modele-q4_k_m.gguf").read_bytes() == Q4
    assert (dossier / "mmproj-f16.gguf").exists()
    assert "Gio libérés" in capsys.readouterr().out
    (evenement,) = [e for e in ouvrir_run(export_id, racine=tmp_path).lire_jsonl("log.jsonl")]
    assert evenement["evenement"] == "purge" and evenement["octets_liberes"] == 21000
    assert evenement["notations"] == [notation] and evenement["supprimes"] == [
        "hf-f16",
        "modele-f16.gguf",
    ]


def test_purge_refusee_sans_notation(tmp_path: Path, capsys) -> None:
    export_id = faux_export(tmp_path)
    assert main(args(tmp_path, "--depuis", export_id)) == CodeSortie.ERREUR
    assert "aucune notation" in capsys.readouterr().out
    assert (tmp_path / "runs" / "export" / export_id / "modele-f16.gguf").exists()


def test_purge_forcee_non_note(tmp_path: Path) -> None:
    export_id = faux_export(tmp_path)
    code = main(args(tmp_path, "--depuis", export_id, "--forcer-non-note"))
    assert code == CodeSortie.SUCCES
    assert not (tmp_path / "runs" / "export" / export_id / "hf-f16").exists()


@pytest.mark.parametrize("q4", [b"", None, b"q4", b"q" * 1500, b"q" * 25000])
def test_purge_refusee_sans_q4_valide(tmp_path: Path, q4) -> None:
    export_id = faux_export(tmp_path, q4=q4)
    fausse_notation(tmp_path, export_id)
    assert main(args(tmp_path, "--depuis", export_id, "--forcer-non-note")) == CodeSortie.ERREUR
    assert (tmp_path / "runs" / "export" / export_id / "hf-f16").exists()


def test_tous_notes_dry_run_puis_reel(tmp_path: Path, capsys) -> None:
    note = faux_export(tmp_path)
    fausse_notation(tmp_path, note)
    non_note = faux_export(tmp_path, slug="ft-autre")
    assert main(args(tmp_path, "--tous-notes", "--dry-run")) == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert note in sortie and non_note not in sortie and "dry-run" in sortie
    assert (tmp_path / "runs" / "export" / note / "modele-f16.gguf").exists()
    assert main(args(tmp_path, "--tous-notes")) == CodeSortie.SUCCES
    assert not (tmp_path / "runs" / "export" / note / "modele-f16.gguf").exists()
    assert (tmp_path / "runs" / "export" / non_note / "modele-f16.gguf").exists()


def test_purger_usage(tmp_path: Path) -> None:
    assert main(args(tmp_path)) == CodeSortie.USAGE
    assert main(args(tmp_path, "--depuis", "x", "--tous-notes")) == CodeSortie.USAGE


def test_purge_idempotente(tmp_path: Path) -> None:
    export_id = faux_export(tmp_path)
    fausse_notation(tmp_path, export_id)
    assert purge.purger_depuis(export_id, racine=tmp_path) == 21000
    assert purge.purger_depuis(export_id, racine=tmp_path) == 0


@pytest.mark.parametrize("statut", ["", "partiel-erreur", "interrompu"])
def test_notation_non_complete_ne_compte_pas(tmp_path: Path, statut: str, capsys) -> None:
    export_id = faux_export(tmp_path)
    fausse_notation(tmp_path, export_id, statut=statut)
    assert purge.exports_notes(tmp_path) == {}
    assert main(args(tmp_path, "--depuis", export_id)) == CodeSortie.ERREUR
    assert "aucune notation" in capsys.readouterr().out
    assert (tmp_path / "runs" / "export" / export_id / "modele-f16.gguf").exists()


@pytest.mark.parametrize("statut", ["", "partiel-erreur"])
def test_export_non_complet_refuse_meme_force(tmp_path: Path, statut: str) -> None:
    export_id = faux_export(tmp_path, statut=statut)
    assert main(args(tmp_path, "--depuis", export_id, "--forcer-non-note")) == CodeSortie.ERREUR
    assert (tmp_path / "runs" / "export" / export_id / "hf-f16").exists()


def test_lien_symbolique_refuse(tmp_path: Path) -> None:
    export_id = faux_export(tmp_path)
    fausse_notation(tmp_path, export_id)
    externe = tmp_path / "externe"
    externe.mkdir()
    (externe / "precieux.bin").write_bytes(b"z" * 10)
    lien = tmp_path / "runs" / "export" / export_id / "hf-f16" / "lien"
    try:
        lien.symlink_to(externe, target_is_directory=True)
    except OSError:
        pytest.skip("liens symboliques non autorisés sur ce poste")
    with pytest.raises(purge.PurgeRefusee, match="lien"):
        purge.purger_depuis(export_id, racine=tmp_path)
    assert (externe / "precieux.bin").exists()
    assert (tmp_path / "runs" / "export" / export_id / "modele-f16.gguf").exists()


def test_purge_partielle_journalisee_et_tous_notes_continue(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    premier = faux_export(tmp_path)
    second = faux_export(tmp_path, slug="ft-autre")
    for export_id in (premier, second):
        fausse_notation(tmp_path, export_id)
    dossier_premier = (tmp_path / "runs" / "export" / premier).resolve()
    vrai_unlink = Path.unlink

    def unlink(self: Path, *a, **k) -> None:
        if self.name == "modele-f16.gguf" and self.parent.resolve() == dossier_premier:
            raise PermissionError("fichier verrouillé")
        vrai_unlink(self, *a, **k)

    monkeypatch.setattr(Path, "unlink", unlink)
    assert main(args(tmp_path, "--tous-notes")) == CodeSortie.ERREUR
    assert "purge partielle" in capsys.readouterr().out
    (evenement,) = ouvrir_run(premier, racine=tmp_path).lire_jsonl("log.jsonl")
    assert evenement["partiel"] is True and evenement["supprimes"] == ["hf-f16"]
    assert evenement["octets_liberes"] == 1000
    assert not (tmp_path / "runs" / "export" / second / "modele-f16.gguf").exists()


def test_options_purge_hors_purger(tmp_path: Path) -> None:
    for option in ("--dry-run", "--tous-notes", "--forcer-non-note"):
        assert main(["export", option, "--racine", str(tmp_path)]) == CodeSortie.USAGE


# --- Contrôle d'espace -------------------------------------------------------------------


def test_config_export_defaut_et_fichier(tmp_path: Path) -> None:
    (tmp_path / "entrainement.toml").write_text(
        "[couts]\npas_chauffe = 1\nperiode_echantillonnage = 0.1\nindice_gpu = 0\n",
        encoding="utf-8",
    )
    config = charger_config_export(tmp_path)
    assert config.facteur_espace == 3.0 and config.espace_libre_go is None
    assert charger_config_export().facteur_espace == 3.0  # config/ du projet
    assert charger_config_export(tmp_path / "absent") == type(config)()  # défauts
