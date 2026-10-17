"""`slmsp budget etat [--json]` : relevé en lecture seule (story 1.5, critère 11).

Le registre vit dans le `SLMSP_VAR_DIR` temporaire du test ; les configurations sont les
vrais `config/budgets.toml` et `config/tarifs.toml`. Aucun appel d'API.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path

import pytest

from slmsp.budget.config import charger_budgets
from slmsp.budget.registre import NOM_REGISTRE, RegistreBudget
from slmsp.budget.tarifs import UsageTokens
from slmsp.cli import CodeSortie, main
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.var import dossier_var

INTERDITS = ("reset", "remise", "zero", "vider", "supprimer")


def _json(capsys: pytest.CaptureFixture[str]) -> dict:
    assert main(["budget", "etat", "--json"]) == CodeSortie.SUCCES
    return json.loads(capsys.readouterr().out)


def _par_ligne(releve: dict) -> dict[tuple[str, str | None], dict]:
    return {(ligne["poste"], ligne["sous_poste"]): ligne for ligne in releve["lignes"]}


def test_critere_11_base_absente_non_creee(capsys: pytest.CaptureFixture[str]) -> None:
    chemin = dossier_var() / NOM_REGISTRE
    releve = _json(capsys)
    assert not chemin.exists()
    assert list(dossier_var().iterdir()) == []
    assert releve["campagne_id"] == charger_budgets().campagne_id
    lignes = _par_ligne(releve)
    assert list(lignes) == [
        ("anthropic", None),
        ("mistral", None),
        ("mistral", "generation"),
        ("mistral", "juge"),
    ]
    plafonds = {cle: ligne["plafond_eur"] for cle, ligne in lignes.items()}
    assert plafonds == {
        ("anthropic", None): 18.6,
        ("mistral", None): 30.0,
        ("mistral", "generation"): 25.0,
        ("mistral", "juge"): 5.0,
    }
    for ligne in releve["lignes"]:
        assert set(ligne) == {
            "poste",
            "sous_poste",
            "plafond_eur",
            "depense_eur",
            "reserve_eur",
            "reste_eur",
        }
        assert (ligne["depense_eur"], ligne["reserve_eur"]) == (0, 0)
        assert ligne["reste_eur"] == ligne["plafond_eur"]


def test_critere_11_lecture_seule_octets_identiques(capsys: pytest.CaptureFixture[str]) -> None:
    registre = RegistreBudget()
    regle = registre.reserver("mistral", "juge", "mistral-large-latest", "direct", 1000, 500)
    cout = registre.regulariser(regle, UsageTokens(entree=900, sortie=300))
    ouverte = registre.reserver("anthropic", None, "claude-opus-5-5", "direct", 2000, 1000)
    # Simule un processus mort : le relevé ne doit pas régulariser l'orpheline.
    with closing(sqlite3.connect(registre.chemin)) as connexion, connexion:
        connexion.execute(
            "UPDATE reservations SET pid = 999999999, creation_processus = 1.0 WHERE id = ?",
            (ouverte,),
        )
    reserve = registre.etat().lignes[0].reserve_eur
    avant = registre.chemin.read_bytes()

    releve = _json(capsys)

    assert registre.chemin.read_bytes() == avant
    with closing(sqlite3.connect(registre.chemin)) as connexion:
        etats = connexion.execute("SELECT etat FROM reservations ORDER BY id").fetchall()
    assert etats == [("regularisee",), ("reservee",)]
    lignes = _par_ligne(releve)
    assert lignes[("mistral", "juge")]["depense_eur"] == pytest.approx(cout, abs=1e-6)
    assert lignes[("mistral", None)]["depense_eur"] == pytest.approx(cout, abs=1e-6)
    assert lignes[("anthropic", None)]["reserve_eur"] == pytest.approx(reserve, abs=1e-6)
    assert lignes[("anthropic", None)]["reste_eur"] == pytest.approx(18.6 - reserve, abs=1e-6)
    assert lignes[("mistral", "generation")]["depense_eur"] == 0


def test_critere_11_json_canonique_en_sous_processus() -> None:
    resultat = subprocess.run(
        [sys.executable, "-m", "slmsp", "budget", "etat", "--json"],
        capture_output=True,
        encoding="utf-8",
        env=dict(os.environ),
        timeout=120,
        check=False,
    )
    assert resultat.returncode == 0, resultat.stderr
    sortie = resultat.stdout.strip()
    contenu = json.loads(sortie)
    assert sortie == json.dumps(contenu, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    assert not (Path(os.environ["SLMSP_VAR_DIR"]) / NOM_REGISTRE).exists()


def test_registre_corrompu_erreur_sans_trace(capsys: pytest.CaptureFixture[str]) -> None:
    chemin = dossier_var() / NOM_REGISTRE
    chemin.write_bytes(b"ceci n'est pas une base SQLite" * 200)
    avant = chemin.read_bytes()
    assert main(["budget", "etat"]) == CodeSortie.ERREUR
    capture = capsys.readouterr()
    assert capture.out == ""
    assert "registre de budget illisible" in capture.err
    assert "Traceback" not in capture.err
    assert chemin.read_bytes() == avant


def test_etat_texte(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["budget", "etat"]) == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert charger_budgets().campagne_id in sortie
    for nom in ("anthropic", "mistral.generation", "mistral.juge", "plafond", "reste"):
        assert nom in sortie


def test_budget_sans_action_erreur_d_usage(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["budget"]) == CodeSortie.USAGE
    assert main(["budget", "remise-a-zero"]) == CodeSortie.USAGE
    capsys.readouterr()


def test_aide_sans_action_de_remise_a_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["budget", "--help"]) == CodeSortie.SUCCES
    aide = capsys.readouterr().out
    assert "etat" in aide
    assert [mot for mot in INTERDITS if mot in aide.lower()] == []


def test_releve_version_de_schema_inattendue(capsys: pytest.CaptureFixture[str]) -> None:
    registre = RegistreBudget()
    with closing(sqlite3.connect(registre.chemin)) as connexion, connexion:
        connexion.execute("PRAGMA user_version = 99")
    avant = registre.chemin.read_bytes()
    assert main(["budget", "etat"]) == CodeSortie.ERREUR
    capture = capsys.readouterr()
    assert capture.out == ""
    assert "version de schéma 99" in capture.err
    assert "Traceback" not in capture.err
    assert registre.chemin.read_bytes() == avant


def test_releve_base_sans_table_sommes_nulles(capsys: pytest.CaptureFixture[str]) -> None:
    # Base SQLite valide mais sans `reservations` (ex. initialisation interrompue).
    chemin = dossier_var() / NOM_REGISTRE
    with closing(sqlite3.connect(chemin)) as connexion, connexion:
        connexion.execute("CREATE TABLE autre (x INTEGER)")
    avant = chemin.read_bytes()
    releve = _json(capsys)
    assert chemin.read_bytes() == avant
    assert releve["ecarts"] == []
    for ligne in releve["lignes"]:
        assert (ligne["depense_eur"], ligne["reserve_eur"]) == (0, 0)
        assert ligne["reste_eur"] == ligne["plafond_eur"]


def test_releve_signale_un_ecart_avec_les_plafonds_inscrits(
    capsys: pytest.CaptureFixture[str],
) -> None:
    registre = RegistreBudget()
    # Simule un `budgets.toml` modifié après l'ancrage : le plafond inscrit était de 4 €.
    with closing(sqlite3.connect(registre.chemin)) as connexion, connexion:
        (plafonds,) = connexion.execute(
            "SELECT plafonds FROM campagnes WHERE campagne_id = ?", (registre.campagne_id,)
        ).fetchone()
        inscrits = json.loads(plafonds) | {"mistral.juge": 4.0}
        connexion.execute(
            "UPDATE campagnes SET plafonds = ? WHERE campagne_id = ?",
            (json.dumps(inscrits), registre.campagne_id),
        )
    avant = registre.chemin.read_bytes()
    ecart = "mistral.juge : 4 € inscrit, 5 € dans budgets.toml"

    assert _json(capsys)["ecarts"] == [ecart]
    assert main(["budget", "etat"]) == CodeSortie.SUCCES
    sortie = capsys.readouterr().out
    assert "attention" in sortie and ecart in sortie
    assert registre.chemin.read_bytes() == avant
    with pytest.raises(ConfigurationInvalide, match="nouveau campagne_id"):
        RegistreBudget()
