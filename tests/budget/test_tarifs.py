"""Tarifs et configuration du budget (story 1.5, critères 4 et 5).

Vérifie les vrais `config/budgets.toml` et `config/tarifs.toml`, puis des TOML écrits dans
`tmp_path`. Aucun appel d'API.
"""

from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import pytest

from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.tarifs import UsageTokens, cout_pire_cas, cout_reel, tarif
from slmsp.core.erreurs import ConfigurationInvalide, TarifInconnu

MILLION = 1_000_000

TARIFS_MINIMAUX = """
schema_version = 1

[taux_usd_eur]
valeur = {taux}
date = 2026-10-12
source = "test"

[modeles."m-direct"]
devise = "USD"
date = 2026-10-12
source = "test"

[modeles."m-direct".modes.direct]
entree = 3.0
sortie = 15.0
{cache}
"""


def ecrire_tarifs(dossier: Path, *, taux: float = 1.0, cache: str = "") -> Path:
    chemin = dossier / "tarifs.toml"
    chemin.write_text(TARIFS_MINIMAUX.format(taux=taux, cache=cache), encoding="utf-8")
    return chemin


# --- critère 5 : tarifs et budgets de départ ------------------------------------------------


def test_critere_5_claude_opus_direct_et_batch() -> None:
    config = charger_tarifs()
    opus = config.modeles["claude-opus-5-5"]
    assert opus.devise == "USD"
    assert opus.date == date(2026, 10, 6)
    assert "claude-api" in opus.source
    direct, batch = opus.modes["direct"], opus.modes["batch"]
    assert (direct.entree, direct.sortie) == (4.0, 20.0)
    assert (direct.ecriture_cache, direct.lecture_cache) == (8.0, 0.20)
    for composante in ("entree", "sortie", "ecriture_cache", "lecture_cache"):
        assert getattr(batch, composante) == pytest.approx(getattr(direct, composante) / 2)


def test_critere_5_mistral_prudent_date_a_verifier() -> None:
    mistral = charger_tarifs().modeles["mistral-large-latest"]
    assert "à vérifier par Anaël" in mistral.note
    assert mistral.date == date(2026, 10, 12)
    assert (mistral.modes["direct"].entree, mistral.modes["direct"].sortie) == (2.0, 6.0)
    assert (mistral.modes["batch"].entree, mistral.modes["batch"].sortie) == (1.0, 3.0)
    # Aucun tarif de cache connu : aucun n'est inventé.
    assert mistral.modes["direct"].ecriture_cache is None
    assert mistral.modes["direct"].lecture_cache is None


def test_critere_5_taux_usd_eur_prudent_et_date() -> None:
    taux = charger_tarifs().taux_usd_eur
    assert taux.valeur == 1.0
    assert taux.date == date(2026, 10, 12)
    assert "prudent" in taux.source or "prudent" in taux.note


def test_budgets_de_depart() -> None:
    config = charger_budgets()
    assert config.campagne_id
    # Les plafonds changent à chaque campagne : on vérifie leur cohérence, pas leurs valeurs.
    assert set(config.postes) == {"anthropic", "mistral"}
    assert config.postes["anthropic"].plafond_eur > 0
    assert config.postes["anthropic"].sous_postes == {}
    mistral = config.postes["mistral"]
    assert set(mistral.sous_postes) == {"generation", "juge"}
    assert all(v > 0 for v in mistral.sous_postes.values())
    assert sum(mistral.sous_postes.values()) <= mistral.plafond_eur + 1e-9
    assert config.marge_eur >= 0
    assert config.majoration_entree >= 1


# --- critère 4 : tarif inconnu, aucune valeur par défaut ------------------------------------


@pytest.mark.parametrize(
    ("modele", "mode"),
    [
        ("mistral-small-latest", "direct"),
        ("claude-opus-5", "direct"),  # aucun alias : identifiant exact seulement
        ("claude-opus-5-5", "flex"),
        ("claude-opus-5-5", "ecriture_cache"),  # le cache est une composante, pas un mode
    ],
)
def test_critere_4_modele_ou_mode_inconnu(modele: str, mode: str) -> None:
    config = charger_tarifs()
    with pytest.raises(TarifInconnu):
        tarif(config, modele, mode)
    with pytest.raises(TarifInconnu):
        cout_pire_cas(config, modele, mode, 100, 100, 1.0)
    with pytest.raises(TarifInconnu):
        cout_reel(config, modele, mode, UsageTokens(100, 100))


def test_critere_4_mode_absent_du_modele(tmp_path: Path) -> None:
    config = charger_tarifs(ecrire_tarifs(tmp_path))
    assert tarif(config, "m-direct", "direct").entree == 3.0
    with pytest.raises(TarifInconnu, match="mode batch"):
        tarif(config, "m-direct", "batch")


def test_critere_4_cache_sans_tarif(tmp_path: Path) -> None:
    config = charger_tarifs(ecrire_tarifs(tmp_path))
    with pytest.raises(TarifInconnu, match="ecriture_cache"):
        cout_pire_cas(config, "m-direct", "direct", 100, 100, 1.0, avec_cache=True)
    with pytest.raises(TarifInconnu, match="ecriture_cache"):
        cout_reel(config, "m-direct", "direct", UsageTokens(1, 1, ecriture_cache=1))
    with pytest.raises(TarifInconnu, match="lecture_cache"):
        cout_reel(config, "m-direct", "direct", UsageTokens(1, 1, lecture_cache=1))
    # Sans cache, le même modèle se calcule.
    assert cout_reel(config, "m-direct", "direct", UsageTokens(1, 1)) > 0


def test_critere_4_mistral_reel_avec_cache_inconnu() -> None:
    config = charger_tarifs()
    with pytest.raises(TarifInconnu):
        cout_pire_cas(config, "mistral-large-latest", "direct", 10, 10, 1.0, avec_cache=True)


@pytest.mark.parametrize("composante", ["entree", "sortie"])
def test_critere_4_composante_obligatoire(tmp_path: Path, composante: str) -> None:
    chemin = ecrire_tarifs(tmp_path)
    texte = chemin.read_text(encoding="utf-8")
    lignes = [ligne for ligne in texte.splitlines() if not ligne.startswith(f"{composante} =")]
    chemin.write_text("\n".join(lignes), encoding="utf-8")
    with pytest.raises(ConfigurationInvalide, match=composante):
        charger_tarifs(chemin)


# --- formules -------------------------------------------------------------------------------


def test_cout_pire_cas_formule(tmp_path: Path) -> None:
    config = charger_tarifs(ecrire_tarifs(tmp_path, taux=0.9))
    cout = cout_pire_cas(config, "m-direct", "direct", 1001, 2000, 1.25)
    attendu = (math.ceil(1001 * 1.25) * 3.0 + 2000 * 15.0) / MILLION * 0.9
    assert cout == pytest.approx(attendu)


def test_cout_pire_cas_avec_cache(tmp_path: Path) -> None:
    cache = "ecriture_cache = 6.0\nlecture_cache = 0.3"
    config = charger_tarifs(ecrire_tarifs(tmp_path, cache=cache))
    cout = cout_pire_cas(config, "m-direct", "direct", 1000, 10, 1.0, avec_cache=True)
    assert cout == pytest.approx((1000 * 6.0 + 10 * 15.0) / MILLION)


def test_cout_pire_cas_avec_cache_moins_cher_que_l_entree(tmp_path: Path) -> None:
    cache = "ecriture_cache = 1.0\nlecture_cache = 0.3"
    config = charger_tarifs(ecrire_tarifs(tmp_path, cache=cache))
    cout = cout_pire_cas(config, "m-direct", "direct", 1000, 10, 1.0, avec_cache=True)
    assert cout == pytest.approx((1000 * 3.0 + 10 * 15.0) / MILLION)


def test_cout_reel_quatre_compteurs(tmp_path: Path) -> None:
    cache = "ecriture_cache = 6.0\nlecture_cache = 0.3"
    config = charger_tarifs(ecrire_tarifs(tmp_path, taux=0.5, cache=cache))
    usage = UsageTokens(entree=1000, sortie=200, ecriture_cache=300, lecture_cache=4000)
    attendu = (1000 * 3.0 + 200 * 15.0 + 300 * 6.0 + 4000 * 0.3) / MILLION * 0.5
    assert cout_reel(config, "m-direct", "direct", usage) == pytest.approx(attendu)


def test_cout_reel_opus_batch() -> None:
    config = charger_tarifs()
    usage = UsageTokens(entree=MILLION, sortie=MILLION)
    assert cout_reel(config, "claude-opus-5-5", "batch", usage) == pytest.approx(12.0)
    assert cout_reel(config, "claude-opus-5-5", "direct", usage) == pytest.approx(24.0)


@pytest.mark.parametrize(
    ("entree", "max_tokens", "majoration"), [(-1, 10, 1.0), (10, 0, 1.0), (10, 10, 0.9)]
)
def test_cout_pire_cas_parametres_invalides(entree: int, max_tokens: int, majoration: float):
    with pytest.raises(ValueError):
        cout_pire_cas(charger_tarifs(), "claude-opus-5-5", "direct", entree, max_tokens, majoration)


def test_usage_tokens() -> None:
    assert UsageTokens(1, 2, 3, 4) + UsageTokens(10, 20) == UsageTokens(11, 22, 3, 4)
    with pytest.raises(ValueError):
        UsageTokens(-1, 0)
    with pytest.raises(ValueError):
        UsageTokens(1.5, 0)  # type: ignore[arg-type]


# --- validation de budgets.toml -------------------------------------------------------------

BUDGETS_VALIDE = """
schema_version = 1
campagne_id = "c"
marge_eur = 0.1
majoration_entree = 1.2

[postes.anthropic]
plafond_eur = 10

[postes.mistral]
plafond_eur = 30

[postes.mistral.sous_postes]
generation = 25
juge = 5

[imputations]
juge-second = "mistral.juge"
"""


@pytest.mark.parametrize(
    ("ancien", "nouveau", "cle"),
    [
        ('juge-second = "mistral.juge"', 'juge-second = "openai"', "imputations"),
        ('juge-second = "mistral.juge"', 'juge-second = "mistral.autre"', "imputations"),
        ('juge-second = "mistral.juge"', 'juge-second = "mistral"', "imputations"),
        ("juge = 5", "juge = 31", "postes.mistral"),
        ("majoration_entree = 1.2", "majoration_entree = 0.8", "majoration_entree"),
        ("marge_eur = 0.1", "marge_eur = -0.1", "marge_eur"),
        ('campagne_id = "c"', 'campagne_id = ""', "campagne_id"),
        ('campagne_id = "c"', 'campagne_id = "   "', "campagne_id"),
        ("marge_eur = 0.1", "marge_eur = 0.1\ninconnue = 1", "inconnue"),
    ],
)
def test_budgets_invalides(tmp_path: Path, ancien: str, nouveau: str, cle: str) -> None:
    chemin = tmp_path / "budgets.toml"
    chemin.write_text(BUDGETS_VALIDE, encoding="utf-8")
    assert charger_budgets(chemin).imputations == {"juge-second": "mistral.juge"}
    chemin.write_text(BUDGETS_VALIDE.replace(ancien, nouveau), encoding="utf-8")
    with pytest.raises(ConfigurationInvalide, match=cle):
        charger_budgets(chemin)


def test_campagne_id_sans_espaces_autour(tmp_path: Path) -> None:
    chemin = tmp_path / "budgets.toml"
    texte = BUDGETS_VALIDE.replace('campagne_id = "c"', 'campagne_id = "  c "')
    chemin.write_text(texte, encoding="utf-8")
    assert charger_budgets(chemin).campagne_id == "c"


def test_tarifs_cle_inconnue_refusee(tmp_path: Path) -> None:
    chemin = ecrire_tarifs(tmp_path, cache="flex = 1.0")
    with pytest.raises(ConfigurationInvalide, match="flex"):
        charger_tarifs(chemin)


def test_tarifs_absents(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide):
        charger_tarifs(tmp_path / "absent.toml")
