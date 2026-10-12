"""Registre de budget : réservation, plafonds, régularisation, orphelines, relances (story 1.5).

Critères d'`epics.md` couverts : 1, 2, 3, 7, 9, 10 (le 4 et le 5 dans `test_tarifs.py`,
le 6 dans `test_concurrence.py`, le 8 dans `test_lots.py`, le 11 dans
`tests/cli/test_budget.py`). Aucun appel d'API.
"""

from __future__ import annotations

import ast
import inspect
import math
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import psutil
import pytest

import slmsp.budget
import slmsp.budget.config
import slmsp.budget.registre
import slmsp.budget.tarifs
from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.registre import NOM_REGISTRE, RegistreBudget
from slmsp.budget.tarifs import UsageTokens
from slmsp.cli import main
from slmsp.core.erreurs import (
    BudgetEpuise,
    CodeSortie,
    ConfigurationInvalide,
    SlmspError,
    TarifInconnu,
)
from slmsp.core.var import dossier_var

MILLION = 1_000_000
INTERDITS = ("reset", "remise", "zero", "vider", "supprimer")
SOURCES_BUDGET = Path(slmsp.budget.__file__).parent

SCRIPT_RESERVE_ET_SORT = """
import sys
from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.registre import RegistreBudget

registre = RegistreBudget(charger_budgets(sys.argv[1]), charger_tarifs(sys.argv[2]))
unitaire = registre.reserver("mistral", "juge", "m-test", "direct", 0, 1_000_000)
registre.reserver_lot("lot-du-mort", "anthropic", None, "m-test", 0, 1_000_000, 2)
print(unitaire)
"""


def reserver_euros(registre: RegistreBudget, euros: float, poste="mistral", sous_poste="juge"):
    """Réserve `euros` en direct sur `m-test` (1 € par million de tokens de sortie)."""
    return registre.reserver(poste, sous_poste, "m-test", "direct", 0, round(euros * MILLION))


def total(registre: RegistreBudget, poste: str, sous_poste: str | None) -> tuple[float, float]:
    for ligne in registre.etat().lignes:
        if (ligne.poste, ligne.sous_poste) == (poste, sous_poste):
            return ligne.depense_eur, ligne.reserve_eur
    raise AssertionError(f"ligne {poste}.{sous_poste} absente du relevé")


# --- critère 1 : emplacement, campagne, aucune remise à zéro ------------------------------


def test_critere_1_registre_dans_var_dir_avec_campagne(registre, lignes) -> None:
    assert registre.chemin == dossier_var() / NOM_REGISTRE
    assert Path(os.environ["SLMSP_VAR_DIR"]).resolve() / "budget.sqlite" == registre.chemin
    assert registre.chemin.is_file()
    assert registre.campagne_id == "campagne-test"
    reserver_euros(registre, 1)
    assert [ligne["campagne_id"] for ligne in lignes(registre)] == ["campagne-test"]


def test_critere_1_campagne_par_defaut_de_budgets_toml() -> None:
    registre = RegistreBudget()
    assert registre.campagne_id == charger_budgets().campagne_id
    assert registre.chemin == dossier_var() / NOM_REGISTRE


def _noms_publics() -> list[str]:
    noms = []
    for module in (slmsp.budget, slmsp.budget.config, slmsp.budget.tarifs, slmsp.budget.registre):
        for nom, objet in vars(module).items():
            if nom.startswith("_"):
                continue
            noms.append(nom)
            if inspect.isclass(objet) and objet.__module__ == module.__name__:
                noms.extend(attribut for attribut in vars(objet) if not attribut.startswith("_"))
    return noms


def test_critere_1_aucune_remise_a_zero_exposee(capsys: pytest.CaptureFixture[str]) -> None:
    noms = _noms_publics()
    assert "RegistreBudget" in noms and "reserver" in noms
    fautifs = [nom for nom in noms if any(mot in nom.lower() for mot in INTERDITS)]
    assert fautifs == []
    for arguments in (["budget", "--help"], ["budget", "etat", "--help"]):
        assert main(arguments) == CodeSortie.SUCCES
        aide = capsys.readouterr().out.lower()
        assert "etat" in aide or "json" in aide
        assert [mot for mot in INTERDITS if mot in aide] == []


def test_critere_1_aucune_suppression_dans_le_code() -> None:
    cli_budget = SOURCES_BUDGET.parent / "cli" / "budget.py"
    assert cli_budget.is_file()
    for fichier in [*SOURCES_BUDGET.glob("*.py"), cli_budget]:
        source = fichier.read_text(encoding="utf-8")
        majuscules = source.upper()
        for motif in ("DELETE ", "DROP ", "TRUNCATE"):
            assert motif not in majuscules, f"{fichier.name} : {motif}"
        for noeud in ast.walk(ast.parse(source)):
            if isinstance(noeud, ast.Attribute):
                assert noeud.attr not in {"unlink", "remove", "rmtree", "rmdir"}, fichier.name


# --- critère 2 : réservation au pire cas, BEGIN IMMEDIATE, plafonds ------------------------


def test_critere_2_montant_pire_cas_majore(config_test, lignes) -> None:
    registre = config_test(majoration=1.25).ouvrir()
    identifiant = registre.reserver("mistral", "juge", "m-test", "direct", 1001, 10)
    (ligne,) = lignes(registre)
    # ⌈1001 × 1,25⌉ = 1252 tokens d'entrée à 1 $ + 10 tokens de sortie à 1 $, 1 USD = 1 EUR.
    assert ligne["id"] == identifiant
    assert ligne["montant_reserve_eur"] == pytest.approx((1252 + 10) / MILLION)
    assert (ligne["etat"], ligne["poste"], ligne["sous_poste"]) == ("reservee", "mistral", "juge")
    assert (ligne["modele"], ligne["mode"], ligne["batch_id"]) == ("m-test", "direct", None)
    assert ligne["pid"] == os.getpid()
    assert ligne["creation_processus"] > 0


def test_critere_2_pire_cas_avec_cache_au_tarif_d_ecriture(registre, lignes) -> None:
    registre.reserver("anthropic", None, "m-test", "direct", 1000, 10, avec_cache=True)
    (ligne,) = lignes(registre)
    assert ligne["montant_reserve_eur"] == pytest.approx((1000 * 2.0 + 10 * 1.0) / MILLION)


def test_critere_2_tarifs_reels_mistral(lignes) -> None:
    registre = RegistreBudget(charger_budgets(), charger_tarifs())
    sous_poste = registre.imputer("juge-second")[1]
    registre.reserver("mistral", sous_poste, "mistral-large-latest", "direct", 1000, 500)
    (ligne,) = lignes(registre)
    entree = math.ceil(1000 * charger_budgets().majoration_entree)
    assert ligne["montant_reserve_eur"] == pytest.approx((entree * 2 + 500 * 6) / MILLION)


def test_critere_2_reservation_en_begin_immediate(
    registre, monkeypatch: pytest.MonkeyPatch
) -> None:
    instructions: list[str] = []
    ouvrir = slmsp.budget.registre.ouvrir_sqlite

    def ouvrir_trace(chemin):
        connexion = ouvrir(chemin)
        connexion.set_trace_callback(instructions.append)
        return connexion

    monkeypatch.setattr(slmsp.budget.registre, "ouvrir_sqlite", ouvrir_trace)
    reserver_euros(registre, 1)
    debut = instructions.index("BEGIN IMMEDIATE")
    insertion = next(i for i, texte in enumerate(instructions) if texte.startswith("INSERT"))
    selection = next(i for i, texte in enumerate(instructions) if texte.startswith("SELECT"))
    assert debut < selection < insertion < instructions.index("COMMIT")


def test_critere_2_plafond_du_sous_poste(registre, lignes) -> None:
    reserver_euros(registre, 4.5)
    avant = lignes(registre)
    with pytest.raises(BudgetEpuise) as info:
        reserver_euros(registre, 0.6)
    assert info.value.code_sortie == CodeSortie.BUDGET_EPUISE == 3
    message = str(info.value)
    assert "mistral.juge" in message
    assert "plafond 5.00" in message
    assert "reste 0.5000" in message
    assert lignes(registre) == avant
    # Le poste mistral (30 €) et le sous-poste generation restent disponibles.
    reserver_euros(registre, 10, sous_poste="generation")


def test_critere_2_plafond_du_poste(config_test, lignes) -> None:
    registre = config_test(mistral=28.0).ouvrir()
    reserver_euros(registre, 24, sous_poste="generation")
    avant = lignes(registre)
    with pytest.raises(BudgetEpuise) as info:
        reserver_euros(registre, 4.5, sous_poste="juge")
    assert "pour mistral (" in str(info.value)
    assert "plafond 28.00" in str(info.value)
    assert lignes(registre) == avant
    reserver_euros(registre, 4, sous_poste="juge")


def test_critere_2_marge_comptee(config_test) -> None:
    registre = config_test(marge=0.5).ouvrir()
    reserver_euros(registre, 4.5)
    with pytest.raises(BudgetEpuise, match="marge 0.50"):
        reserver_euros(registre, 0.01)


def test_critere_2_plafond_atteint_exactement(registre) -> None:
    for _ in range(5):
        reserver_euros(registre, 1)
    assert total(registre, "mistral", "juge") == (0.0, pytest.approx(5.0))
    with pytest.raises(BudgetEpuise):
        registre.reserver("mistral", "juge", "m-test", "direct", 0, 1)


def test_critere_2_depense_et_reserve_comptes_ensemble(registre) -> None:
    premiere = reserver_euros(registre, 2)
    registre.compter_pire_cas(premiere)
    reserver_euros(registre, 2)
    assert total(registre, "mistral", "juge") == (pytest.approx(2.0), pytest.approx(2.0))
    with pytest.raises(BudgetEpuise):
        reserver_euros(registre, 1.5)


@pytest.mark.parametrize(
    ("poste", "sous_poste"),
    [("mistral", None), ("inconnu", None), ("mistral", "autre"), ("anthropic", "juge")],
)
def test_sous_poste_requis_ou_inconnu(registre, lignes, poste, sous_poste) -> None:
    with pytest.raises(ConfigurationInvalide):
        registre.reserver(poste, sous_poste, "m-test", "direct", 0, 10)
    assert lignes(registre) == []


@pytest.mark.parametrize(
    ("modele", "mode", "avec_cache"),
    [
        ("inconnu", "direct", False),
        ("m-test", "flex", False),
        ("m-sans-cache", "batch", False),
        ("m-sans-cache", "direct", True),
    ],
)
def test_tarif_inconnu_rien_reserve(registre, lignes, modele, mode, avec_cache) -> None:
    with pytest.raises(TarifInconnu):
        registre.reserver("anthropic", None, modele, mode, 0, 10, avec_cache=avec_cache)
    assert lignes(registre) == []


# --- critère 3 : régularisation et échec sans usage ----------------------------------------


def test_critere_3_regularisation_au_cout_reel(registre, lignes) -> None:
    identifiant = reserver_euros(registre, 1)
    usage = UsageTokens(entree=100_000, sortie=200_000, ecriture_cache=1_000, lecture_cache=10_000)
    cout = registre.regulariser(identifiant, usage)
    attendu = (100_000 * 1 + 200_000 * 1 + 1_000 * 2 + 10_000 * 0.1) / MILLION
    assert cout == pytest.approx(attendu)
    (ligne,) = lignes(registre)
    assert ligne["etat"] == "regularisee"
    assert ligne["montant_reel_eur"] == pytest.approx(attendu)
    assert ligne["montant_reserve_eur"] == pytest.approx(1.0)
    compteurs = [ligne[f"tokens_{nom}"] for nom in ("entree", "sortie")]
    assert compteurs == [100_000, 200_000]
    assert ligne["tokens_ecriture_cache"] == 1_000 and ligne["tokens_lecture_cache"] == 10_000
    assert total(registre, "mistral", "juge") == (pytest.approx(attendu), 0.0)
    assert total(registre, "mistral", None) == (pytest.approx(attendu), 0.0)


def test_critere_3_echec_sans_usage_compte_au_pire_cas(registre, lignes) -> None:
    identifiant = reserver_euros(registre, 1.5)
    assert registre.compter_pire_cas(identifiant) == pytest.approx(1.5)
    (ligne,) = lignes(registre)
    assert (ligne["etat"], ligne["motif"]) == ("pire-cas", "echec")
    assert ligne["montant_reel_eur"] == ligne["montant_reserve_eur"]
    assert total(registre, "mistral", "juge") == (pytest.approx(1.5), 0.0)


def test_regularisation_inconnue_ou_deja_reglee(registre) -> None:
    identifiant = reserver_euros(registre, 1)
    with pytest.raises(SlmspError, match="inconnue"):
        registre.regulariser(identifiant + 100, UsageTokens(1, 1))
    registre.regulariser(identifiant, UsageTokens(1, 1))
    with pytest.raises(SlmspError, match="déjà réglée"):
        registre.regulariser(identifiant, UsageTokens(1, 1))
    with pytest.raises(SlmspError, match="déjà réglée"):
        registre.compter_pire_cas(identifiant)


def test_regularisation_au_dela_de_la_reservation_signalee(registre, lignes) -> None:
    identifiant = reserver_euros(registre, 1)
    assert registre.regulariser(identifiant, UsageTokens(MILLION, MILLION)) == pytest.approx(2.0)
    (ligne,) = lignes(registre)
    assert (ligne["etat"], ligne["motif"]) == ("regularisee", "depassement-reservation")
    assert ligne["montant_reel_eur"] == pytest.approx(2.0)
    assert total(registre, "mistral", "juge") == (pytest.approx(2.0), 0.0)


def test_regularisation_cache_sans_tarif_laisse_ouvert(registre, lignes) -> None:
    identifiant = registre.reserver("anthropic", None, "m-sans-cache", "direct", 10, 10)
    with pytest.raises(TarifInconnu):
        registre.regulariser(identifiant, UsageTokens(10, 10, lecture_cache=5))
    assert lignes(registre)[0]["etat"] == "reservee"


# --- critère 7 : réservations orphelines ----------------------------------------------------


def test_critere_7_orpheline_d_un_processus_mort(config_test, lignes) -> None:
    fichiers = config_test()
    resultat = subprocess.run(
        [sys.executable, "-c", SCRIPT_RESERVE_ET_SORT, str(fichiers.budgets), str(fichiers.tarifs)],
        capture_output=True,
        encoding="utf-8",
        env=dict(os.environ),  # même SLMSP_VAR_DIR que le test
        timeout=120,
        check=False,
    )
    assert resultat.returncode == 0, resultat.stderr
    identifiant = int(resultat.stdout.strip())

    registre = fichiers.ouvrir()
    assert registre.orphelines_regularisees == (identifiant,)
    unitaire, lot = lignes(registre)
    assert (unitaire["etat"], unitaire["motif"]) == ("pire-cas", "orpheline")
    assert unitaire["montant_reel_eur"] == pytest.approx(1.0)
    assert unitaire["pid"] != os.getpid()
    # La réservation liée à un lot reste ouverte malgré la mort de son processus.
    assert (lot["etat"], lot["batch_id"]) == ("reservee", "lot-du-mort")
    assert [ouvert.batch_id for ouvert in registre.lots_ouverts()] == ["lot-du-mort"]
    assert total(registre, "mistral", "juge") == (pytest.approx(1.0), 0.0)
    assert total(registre, "anthropic", None) == (0.0, pytest.approx(1.0))
    # Une seconde ouverture ne régularise plus rien.
    assert fichiers.ouvrir().orphelines_regularisees == ()


def test_critere_7_pid_recycle_traite_comme_mort(registre, lignes, modifier) -> None:
    identifiant = reserver_euros(registre, 1)
    modifier(
        registre,
        "UPDATE reservations SET creation_processus = creation_processus - 3600 WHERE id = ?",
        (identifiant,),
    )
    rouvert = RegistreBudget(registre.config, registre.tarifs)
    assert rouvert.orphelines_regularisees == (identifiant,)
    assert lignes(rouvert)[0]["motif"] == "orpheline"


def test_critere_7_acces_refuse_tenu_pour_vivant(
    registre, lignes, monkeypatch: pytest.MonkeyPatch
) -> None:
    reserver_euros(registre, 1)

    class ProcessusInaccessible:
        def __init__(self, pid: int) -> None:
            raise psutil.AccessDenied(pid)

    monkeypatch.setattr(slmsp.budget.registre.psutil, "Process", ProcessusInaccessible)
    rouvert = RegistreBudget(registre.config, registre.tarifs)
    assert rouvert.orphelines_regularisees == ()
    assert lignes(rouvert)[0]["etat"] == "reservee"


def test_critere_7_reservation_vivante_reste_ouverte(registre, lignes) -> None:
    reserver_euros(registre, 1)
    rouvert = RegistreBudget(registre.config, registre.tarifs)
    assert rouvert.orphelines_regularisees == ()
    assert lignes(rouvert)[0]["etat"] == "reservee"


# --- critère 9 : relances, une réservation par tentative ------------------------------------


class AppelFactice:
    def __init__(self, echecs: int, exception: type[BaseException] = RuntimeError) -> None:
        self.echecs = echecs
        self.exception = exception
        self.appels = 0

    def __call__(self) -> tuple[str, UsageTokens | None]:
        self.appels += 1
        if self.appels <= self.echecs:
            raise self.exception(f"échec {self.appels}")
        return "<réponse-factice-1>", UsageTokens(entree=1_000, sortie=1_000)


def _relancer(registre: RegistreBudget, appel, tentatives: int = 3, euros: float = 1.0):
    return registre.executer_avec_relances(
        appel, tentatives, "mistral", "juge", "m-test", "direct", 0, round(euros * MILLION)
    )


def test_critere_9_chaque_tentative_reserve(registre, lignes) -> None:
    appel = AppelFactice(echecs=2)
    assert _relancer(registre, appel) == "<réponse-factice-1>"
    assert appel.appels == 3
    etats = [(ligne["etat"], ligne["motif"]) for ligne in lignes(registre)]
    assert etats == [("pire-cas", "echec"), ("pire-cas", "echec"), ("regularisee", None)]
    assert total(registre, "mistral", "juge") == (pytest.approx(2 + 2_000 / MILLION), 0.0)


def test_critere_9_derniere_exception_relevee(registre, lignes) -> None:
    appel = AppelFactice(echecs=10)
    with pytest.raises(RuntimeError, match="échec 3"):
        _relancer(registre, appel)
    assert [ligne["etat"] for ligne in lignes(registre)] == ["pire-cas"] * 3


def test_critere_9_slmsp_error_jamais_retentee(registre, lignes) -> None:
    appel = AppelFactice(echecs=10, exception=SlmspError)
    with pytest.raises(SlmspError, match="échec 1"):
        _relancer(registre, appel)
    assert appel.appels == 1
    assert [ligne["etat"] for ligne in lignes(registre)] == ["pire-cas"]


def test_critere_9_interruption_comptee_et_propagee(registre, lignes) -> None:
    appel = AppelFactice(echecs=10, exception=KeyboardInterrupt)
    with pytest.raises(KeyboardInterrupt):
        _relancer(registre, appel)
    assert [ligne["etat"] for ligne in lignes(registre)] == ["pire-cas"]


def test_critere_9_plafond_atteint_pendant_les_relances(registre, lignes) -> None:
    appel = AppelFactice(echecs=10)
    with pytest.raises(BudgetEpuise):
        _relancer(registre, appel, tentatives=5, euros=2.0)
    assert appel.appels == 2
    assert [ligne["etat"] for ligne in lignes(registre)] == ["pire-cas", "pire-cas"]


def test_critere_9_succes_sans_usage_au_pire_cas(registre, lignes) -> None:
    assert _relancer(registre, lambda: ("<réponse-factice-2>", None)) == "<réponse-factice-2>"
    assert [ligne["etat"] for ligne in lignes(registre)] == ["pire-cas"]


def test_critere_9_regularisation_impossible_comptee_au_pire_cas(registre, lignes) -> None:
    appels = []

    def appel() -> tuple[str, UsageTokens]:
        appels.append(1)
        return "<réponse-factice-3>", UsageTokens(10, 10, lecture_cache=5)

    with pytest.raises(TarifInconnu):
        registre.executer_avec_relances(
            appel, 3, "anthropic", None, "m-sans-cache", "direct", 10, 10
        )
    assert len(appels) == 1
    assert [(ligne["etat"], ligne["motif"]) for ligne in lignes(registre)] == [
        ("pire-cas", "echec")
    ]


def test_critere_9_retour_non_couple_sans_relance(registre, lignes) -> None:
    appels = []

    def appel():
        appels.append(1)
        return "<réponse-factice-4>"

    with pytest.raises(TypeError, match="couple"):
        _relancer(registre, appel)
    assert len(appels) == 1
    assert [(ligne["etat"], ligne["motif"]) for ligne in lignes(registre)] == [
        ("pire-cas", "echec")
    ]


def test_critere_9_echec_du_comptage_ne_masque_pas_l_erreur(
    registre, monkeypatch: pytest.MonkeyPatch
) -> None:
    def comptage_impossible(_identifiant: int) -> float:
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr(registre, "compter_pire_cas", comptage_impossible)
    with pytest.raises(RuntimeError, match="échec 1") as info:
        _relancer(registre, AppelFactice(echecs=10))
    assert isinstance(info.value.__cause__, sqlite3.OperationalError)


def test_critere_9_tentatives_invalides(registre) -> None:
    with pytest.raises(ValueError):
        _relancer(registre, AppelFactice(0), tentatives=0)


# --- critère 10 : imputation des usages -----------------------------------------------------


def test_critere_10_imputations(registre) -> None:
    assert registre.imputer("juge-second") == ("mistral", "juge")
    assert registre.imputer("generation") == ("mistral", "generation")
    assert registre.imputer("validation") == ("mistral", "generation")
    assert registre.imputer("juge-principal") == ("anthropic", None)
    with pytest.raises(ConfigurationInvalide):
        registre.imputer("inconnu")


def test_critere_10_imputations_de_budgets_toml() -> None:
    registre = RegistreBudget()
    assert registre.imputer("juge-second") == ("mistral", "juge")
    assert registre.imputer("generation") == ("mistral", "generation")
    assert registre.imputer("validation") == ("mistral", "generation")


def test_critere_10_juge_second_s_impute_au_sous_poste_juge(registre) -> None:
    poste, sous_poste = registre.imputer("juge-second")
    reserver_euros(registre, 1, poste=poste, sous_poste=sous_poste)
    assert total(registre, "mistral", "juge")[1] == pytest.approx(1.0)
    assert total(registre, "mistral", "generation")[1] == 0.0


# --- campagne, schéma -----------------------------------------------------------------------


def test_nouvelle_campagne_sans_rien_effacer(config_test, lignes) -> None:
    ancienne = config_test(campagne="ancienne").ouvrir()
    reserver_euros(ancienne, 4)
    nouvelle = config_test(campagne="nouvelle").ouvrir()
    assert nouvelle.etat().campagne_id == "nouvelle"
    assert total(nouvelle, "mistral", "juge") == (0.0, 0.0)
    reserver_euros(nouvelle, 4)
    assert [ligne["campagne_id"] for ligne in lignes(nouvelle)] == ["ancienne", "nouvelle"]
    assert total(ancienne, "mistral", "juge") == (0.0, pytest.approx(4.0))


def test_etat_reste_par_poste(registre) -> None:
    reserver_euros(registre, 2)
    reserver_euros(registre, 3, sous_poste="generation")
    releve = {(ligne.poste, ligne.sous_poste): ligne for ligne in registre.etat().lignes}
    assert list(releve) == [
        ("anthropic", None),
        ("mistral", None),
        ("mistral", "generation"),
        ("mistral", "juge"),
    ]
    assert releve[("mistral", None)].reserve_eur == pytest.approx(5.0)
    assert releve[("mistral", None)].reste_eur == pytest.approx(25.0)
    assert releve[("mistral", "juge")].reste_eur == pytest.approx(3.0)
    assert releve[("anthropic", None)].reste_eur == pytest.approx(10.0)


def test_version_de_schema_inattendue(registre) -> None:
    with sqlite3.connect(registre.chemin) as connexion:
        connexion.execute("PRAGMA user_version = 99")
    connexion.close()
    with pytest.raises(SlmspError, match="version de schéma 99"):
        RegistreBudget(registre.config, registre.tarifs)
