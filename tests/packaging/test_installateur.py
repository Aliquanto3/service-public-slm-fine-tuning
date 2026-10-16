"""Tests de l'installateur Inno Setup (story 12.13) : script `.iss`, commande, empreintes.

Aucun ISCC réel : le compilateur est factice.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

import pytest

from slmsp.core.canonique import sha256_fichier

DEPOT = Path(__file__).resolve().parents[2]
ISS = (DEPOT / "packaging" / "assistantsp.iss").read_text(encoding="utf-8")


def _charger():
    chemin = DEPOT / "outils" / "construire_installateur.py"
    spec = importlib.util.spec_from_file_location("construire_installateur", chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules["construire_installateur"] = module
    spec.loader.exec_module(module)
    return module


CI = _charger()


def test_iss_par_utilisateur_sans_admin() -> None:
    assert "PrivilegesRequired=lowest" in ISS
    assert "DefaultDirName={localappdata}\\Programs\\AssistantSP" in ISS
    for interdit in ("{pf}", "{commonappdata}", "{autopf}", "{commonpf}"):
        assert interdit not in ISS


def test_iss_appid_stable_et_unique() -> None:
    ids = re.findall(r"^AppId=\{\{([0-9A-F-]{36})\}", ISS, re.M)
    assert ids == ["6F3A1C52-8B4E-4D7A-9C21-5E0B7D4A3F18"]


def test_iss_trois_ecrans_et_lancement_coche() -> None:
    for ligne in ("DisableDirPage=yes", "DisableProgramGroupPage=yes", "DisableReadyPage=yes"):
        assert ligne in ISS
    run = next(ln for ln in ISS.splitlines() if 'Description: "Lancer l\'assistant"' in ln)
    assert "postinstall" in run and "unchecked" not in run


def test_iss_detection_webview2() -> None:
    assert "F3017226-FE2A-4295-8BDF-00C3A9A7E4C5" in ISS
    assert "EdgeUpdate\\Clients" in ISS and "'pv'" in ISS
    for racine in ("HKLM32", "HKLM64", "HKCU"):
        assert racine in ISS
    assert "DSI" in ISS and "Result := False" in ISS


def test_iss_desinstallation_une_question() -> None:
    assert "Conserver l'historique et les retours sur ce poste ?" in ISS.replace("''", "'")
    assert "DelTree(ExpandConstant('{#DossierDonnees}')" in ISS
    assert '#define DossierDonnees "{localappdata}\\AssistantSP"' in ISS
    assert "MB_YESNO or MB_DEFBUTTON1" in ISS and "IDNO" in ISS  # « Non » supprime


def test_iss_decoupage_et_pack_complet_conditionnels() -> None:
    assert re.search(r"#ifdef Decoupage\s+DiskSpanning=yes", ISS)
    assert "#ifdef PackComplet" in ISS and "#ifndef PackComplet" in ISS


def _paquet(tmp_path: Path, extra: int = 0) -> Path:
    source = tmp_path / "AssistantSP"
    source.mkdir()
    (source / "AssistantSP.exe").write_bytes(b"<factice>")
    if extra:
        with (source / "gros.bin").open("wb") as f:
            f.truncate(extra)
    return source


def _args(tmp_path: Path, source: Path, iscc: Path, **kw) -> argparse.Namespace:
    base = {
        "source": str(source),
        "sortie": str(tmp_path / "sortie"),
        "iscc": str(iscc),
        "version": "1.2.3",
        "pack_complet": None,
    }
    return argparse.Namespace(**{**base, **kw})


def _iscc_factice(tmp_path: Path) -> Path:
    iscc = tmp_path / "ISCC.exe"
    iscc.write_bytes(b"<factice>")
    return iscc


def test_commande_iscc() -> None:
    cmd = CI.commande_iscc(
        Path("ISCC.exe"),
        source=Path("S"),
        sortie=Path("O"),
        version="1.2.3",
        decoupage=True,
        pack_complet=Path("wv2.exe"),
    )
    assert cmd[0] == "ISCC.exe" and cmd[-1].endswith("assistantsp.iss")
    attendus = {"/DVersionApp=1.2.3", "/DDossierSource=S", "/DDossierSortie=O", "/DDecoupage=1"}
    assert attendus <= set(cmd)
    assert "/DPackComplet=wv2.exe" in cmd
    simple = CI.commande_iscc(
        Path("I"), source=Path("S"), sortie=Path("O"), version="1", decoupage=False
    )
    assert not any(a.startswith(("/DDecoupage", "/DPackComplet")) for a in simple)


def test_decoupage_selon_taille(tmp_path: Path) -> None:
    assert not CI.decoupage_necessaire(_paquet(tmp_path))
    gros = tmp_path / "gros"
    gros.mkdir()
    assert CI.decoupage_necessaire(_paquet(gros, extra=2_000_000_001))


def test_construire_avec_compilateur_factice(tmp_path: Path) -> None:
    source, iscc = _paquet(tmp_path), _iscc_factice(tmp_path)
    appels: list[list[str]] = []

    def factice(cmd: list[str]) -> int:
        appels.append(cmd)
        sortie = Path(next(a for a in cmd if a.startswith("/DDossierSortie=")).split("=", 1)[1])
        (sortie / "AssistantSP-Setup-1.2.3.exe").write_bytes(b"<installateur-factice>")
        return 0

    empreintes = CI.construire(_args(tmp_path, source, iscc), factice)
    exe = tmp_path / "sortie" / "AssistantSP-Setup-1.2.3.exe"
    assert len(appels) == 1
    assert empreintes.name == "AssistantSP-Setup-1.2.3.exe.sha256"
    assert empreintes.read_text(encoding="utf-8") == f"{sha256_fichier(exe)} *{exe.name}\n"


def test_empreintes_des_tranches(tmp_path: Path) -> None:
    noms = ("AssistantSP-Setup-1.exe", "AssistantSP-Setup-1-1.bin", "AssistantSP-Setup-1-2.bin")
    for nom in noms:
        (tmp_path / nom).write_bytes(nom.encode())
    fichiers = CI.fichiers_installateur(tmp_path, "1")
    assert [f.name for f in fichiers] == list(noms)
    lignes = CI.ecrire_empreintes(fichiers).read_text(encoding="utf-8").splitlines()
    assert len(lignes) == 3
    assert all(re.fullmatch(r"[0-9a-f]{64} \*\S+", s) for s in lignes)


def test_echec_du_compilateur(tmp_path: Path) -> None:
    args = _args(tmp_path, _paquet(tmp_path), _iscc_factice(tmp_path))
    with pytest.raises(CI.ErreurInstallateur, match="ISCC a échoué"):
        CI.construire(args, lambda _c: 1)


def test_sortie_non_produite(tmp_path: Path) -> None:
    args = _args(tmp_path, _paquet(tmp_path), _iscc_factice(tmp_path))
    with pytest.raises(CI.ErreurInstallateur, match="non produit"):
        CI.construire(args, lambda _c: 0)


def test_paquet_absent_et_iscc_introuvable(tmp_path: Path) -> None:
    with pytest.raises(CI.ErreurInstallateur, match="paquet absent"):
        CI.construire(_args(tmp_path, tmp_path / "rien", _iscc_factice(tmp_path)), lambda _c: 0)
    env = {"PATH": str(tmp_path / "vide"), "LOCALAPPDATA": str(tmp_path / "x")}
    if not (DEPOT / "vendor" / "innosetup" / "ISCC.exe").is_file():
        with pytest.raises(CI.ErreurInstallateur, match="ISCC.exe introuvable"):
            CI.trouver_iscc(None, env)


def test_trouver_iscc_ordre(tmp_path: Path) -> None:
    iscc = _iscc_factice(tmp_path)
    assert CI.trouver_iscc(str(iscc), {}) == iscc
    assert CI.trouver_iscc(None, {"SLMSP_ISCC": str(iscc)}) == iscc


def test_pack_complet_introuvable(tmp_path: Path) -> None:
    args = _args(
        tmp_path, _paquet(tmp_path), _iscc_factice(tmp_path), pack_complet=str(tmp_path / "x")
    )
    with pytest.raises(CI.ErreurInstallateur, match="pack WebView2"):
        CI.construire(args, lambda _c: 0)


def test_version_depuis_pyproject() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", CI.version_application())
