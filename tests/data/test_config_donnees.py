"""Configuration du pipeline de données : `config/donnees.toml` (story 9.1, AD-17, D1.2, D4)."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest

from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.items import N_DEFAUT
from slmsp.data.config import ConfigDonnees, charger_config_donnees
from slmsp.mistral.config import charger_mistral

FICHIER_REEL = racine_projet() / "config" / "donnees.toml"
SHA_FACTICE = "0" * 63 + "a"


def _texte_reel() -> str:
    """Fichier réel ramené à sa forme livrée : conditions Mistral vides (la campagne 9.8 les
    renseigne dans le dépôt ; les tests partent toujours de l'état « non vérifié »)."""
    texte = FICHIER_REEL.read_text(encoding="utf-8")
    texte = re.sub(
        r"^conditions_verifiees_le = .*$", 'conditions_verifiees_le = ""', texte, flags=re.M
    )
    return re.sub(r"^conditions_sha256 = .*$", 'conditions_sha256 = ""', texte, flags=re.M)


def _remplacer(texte: str, motif: str, remplacement: str) -> str:
    nouveau, nombre = re.subn(motif, remplacement, texte, count=1, flags=re.MULTILINE)
    assert nombre == 1, motif
    return nouveau


def _variante(tmp_path: Path, *remplacements: tuple[str, str]) -> Path:
    texte = _texte_reel()
    for motif, remplacement in remplacements:
        texte = _remplacer(texte, motif, remplacement)
    chemin = tmp_path / "donnees.toml"
    chemin.write_text(texte, encoding="utf-8")
    return chemin


def _charger(tmp_path: Path, *remplacements: tuple[str, str]) -> ConfigDonnees:
    return charger_config_donnees(_variante(tmp_path, *remplacements))


def _generateur() -> ModuleType:
    """Module du Générateur (story 9.2) ; il importe le SDK `mistralai` (extra `data`)."""
    pytest.importorskip("mistralai")
    from slmsp.mistral import generateur

    return generateur


def _date_du_jour() -> tuple[str, str]:
    return (r"^conditions_verifiees_le = .*$", f"conditions_verifiees_le = {date.today()}")


def _sha_factice() -> tuple[str, str]:
    return (r"^conditions_sha256 = .*$", f'conditions_sha256 = "{SHA_FACTICE}"')


# --- Configuration réelle -----------------------------------------------------------------


def test_config_reelle() -> None:
    config = charger_config_donnees()
    assert config.volumes.par_tache() == {
        "Q": 100,
        "RD": 140,
        "CR": 80,
        "LC": 80,
        "CO": 35,
        "RE": 35,
        "CT": 35,
        "generique": 90,
    }
    assert config.total == config.volumes.total == 595
    # Vides avant la campagne 9.8, renseignés ensemble par elle (date + SHA de la page relue).
    assert (config.mistral.conditions_verifiees_le is None) == (
        config.mistral.conditions_sha256 is None
    )
    assert config.mistral.conditions_url == (
        "https://legal.mistral.ai/terms/commercial-terms-of-service/"
    )
    assert config.mistral.methode_verification
    assert config.deduplication.n_ngrammes == N_DEFAUT
    assert config.deduplication.seuil_jaccard == 0.8
    assert config.anti_fuite.n_ngrammes == N_DEFAUT
    assert config.anti_fuite.seuil_jaccard == 0.5
    assert config.anti_fuite.seuil_cosinus == 0.9
    assert (config.relecture.taille_echantillon, config.relecture.graine) == (30, 42)


def test_modeles_stables_egaux_a_mistral_toml() -> None:
    config = charger_config_donnees()
    assert config.mistral.modeles_stables == charger_mistral().modeles_autorises


def test_url_des_conditions_dans_le_profil_outillage() -> None:
    import tomllib

    reseau = tomllib.loads((racine_projet() / "config" / "reseau.toml").read_text("utf-8"))
    regles = reseau["profils"]["outillage"]["regles"]
    regle = next(r for r in regles if r.get("nom") == "conditions-mistral")
    url = charger_config_donnees().mistral.conditions_url
    hote, chemin = url.removeprefix("https://").split("/", 1)
    assert hote in regle["hotes"]
    assert "/" + chemin in regle["chemins"]


def test_chaque_cle_est_commentee() -> None:
    lignes = _texte_reel().splitlines()
    for indice, ligne in enumerate(lignes):
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]* = ", ligne):
            assert indice > 0 and lignes[indice - 1].startswith("#"), ligne


# --- Prérequis de la story 9.2 ------------------------------------------------------------


def test_fichier_livre_refuse_par_le_generateur(tmp_path: Path) -> None:
    generateur = _generateur()
    with pytest.raises(generateur.PrealableNonSatisfait):
        generateur.charger_prealables(
            _variante(tmp_path), modele="mistral-large-latest", aujourd_hui=date.today()
        )


def test_date_du_jour_acceptee_par_le_generateur(tmp_path: Path) -> None:
    generateur = _generateur()
    chemin = _variante(tmp_path, _date_du_jour(), _sha_factice())
    prealables = generateur.charger_prealables(
        chemin, modele="mistral-large-latest", aujourd_hui=date.today()
    )
    assert prealables.conditions_verifiees_le == date.today()
    assert charger_config_donnees(chemin).mistral.conditions_verifiees_le == date.today()


def test_date_veille_refusee_par_le_generateur(tmp_path: Path) -> None:
    generateur = _generateur()
    chemin = _variante(
        tmp_path,
        (r"^conditions_verifiees_le = .*$", "conditions_verifiees_le = 2026-01-01"),
        _sha_factice(),
    )
    assert charger_config_donnees(chemin).mistral.conditions_verifiees_le == date(2026, 1, 1)
    with pytest.raises(generateur.PrealableNonSatisfait):
        generateur.charger_prealables(
            chemin, modele="mistral-large-latest", aujourd_hui=date(2026, 1, 2)
        )


# --- [mistral] ----------------------------------------------------------------------------


def test_sha_valide(tmp_path: Path) -> None:
    config = _charger(tmp_path, _date_du_jour(), _sha_factice())
    assert config.mistral.conditions_sha256 == SHA_FACTICE


def test_date_sans_sha_refusee(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="tous deux"):
        _charger(tmp_path, _date_du_jour())


def test_sha_sans_date_refuse(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="tous deux"):
        _charger(tmp_path, _sha_factice())


@pytest.mark.parametrize("sha", ["abc", SHA_FACTICE.upper(), "g" * 64, SHA_FACTICE + "0"])
def test_sha_invalide(tmp_path: Path, sha: str) -> None:
    with pytest.raises(ConfigurationInvalide, match="conditions_sha256"):
        _charger(tmp_path, (r"^conditions_sha256 = .*$", f'conditions_sha256 = "{sha}"'))


def test_date_chaine_non_vide_refusee(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="conditions_verifiees_le"):
        _charger(tmp_path, (r"^conditions_verifiees_le = .*$", 'conditions_verifiees_le = "hier"'))


def test_modeles_stables_vides(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="modeles_stables"):
        _charger(tmp_path, (r"^modeles_stables = .*$", "modeles_stables = []"))


def test_url_non_https(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="conditions_url"):
        _charger(tmp_path, (r"^conditions_url = .*$", 'conditions_url = "http://exemple.invalid"'))


def test_cle_inconnue_dans_mistral(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="mistral.cle_inconnue"):
        _charger(tmp_path, (r"^\[mistral\]$", '[mistral]\ncle_inconnue = "x"'))


# --- [volumes] ----------------------------------------------------------------------------


def test_traduction_refusee(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="volumes.TR"):
        _charger(tmp_path, (r"^generique = 90$", "generique = 90\nTR = 10"))


def test_tache_manquante(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="volumes.CT"):
        _charger(tmp_path, (r"^CT = 35$", ""))


@pytest.mark.parametrize("generique", [0, 50, 160, 400])
def test_part_generique_hors_bornes(tmp_path: Path, generique: int) -> None:
    # total hors generique : 505 ; 10 % <=> generique >= 56,1 ; 20 % <=> generique <= 126,25
    with pytest.raises(ConfigurationInvalide, match="part generique"):
        _charger(tmp_path, (r"^generique = 90$", f"generique = {generique}"))


@pytest.mark.parametrize(("q", "generique"), [(495, 100), (395, 200)])
def test_part_generique_bornes_incluses(tmp_path: Path, q: int, generique: int) -> None:
    # 100 / 1000 = 10 % et 200 / 1000 = 20 % exactement
    config = _charger(
        tmp_path, (r"^Q = 100$", f"Q = {q}"), (r"^generique = 90$", f"generique = {generique}")
    )
    assert config.total == 1000


def test_volumes_tous_nuls(tmp_path: Path) -> None:
    texte = re.sub(r"^(Q|RD|CR|LC|CO|RE|CT|generique) = \d+$", r"\1 = 0", _texte_reel(), flags=re.M)
    chemin = tmp_path / "donnees.toml"
    chemin.write_text(texte, encoding="utf-8")
    with pytest.raises(ConfigurationInvalide, match="strictement positif"):
        charger_config_donnees(chemin)


@pytest.mark.parametrize("valeur", ["-1", "1.5", "true", '"10"'])
def test_volume_invalide(tmp_path: Path, valeur: str) -> None:
    with pytest.raises(ConfigurationInvalide, match="volumes.LC"):
        _charger(tmp_path, (r"^LC = 80$", f"LC = {valeur}"))


# --- Seuils et relecture -----------------------------------------------------------------


@pytest.mark.parametrize("valeur", ["0", "0.0", "1.01", "-0.5", "nan", "inf"])
def test_seuil_hors_intervalle(tmp_path: Path, valeur: str) -> None:
    with pytest.raises(ConfigurationInvalide, match="anti_fuite.seuil_cosinus"):
        _charger(tmp_path, (r"^seuil_cosinus = 0.9$", f"seuil_cosinus = {valeur}"))


def test_seuil_un_admis(tmp_path: Path) -> None:
    config = _charger(tmp_path, (r"^seuil_jaccard = 0.8$", "seuil_jaccard = 1.0"))
    assert config.deduplication.seuil_jaccard == 1.0


def test_n_ngrammes_par_defaut(tmp_path: Path) -> None:
    config = _charger(tmp_path, (r"^n_ngrammes = 5\n", ""))
    assert config.deduplication.n_ngrammes == N_DEFAUT


@pytest.mark.parametrize("valeur", ["0", "2.5"])
def test_n_ngrammes_invalide(tmp_path: Path, valeur: str) -> None:
    with pytest.raises(ConfigurationInvalide, match="deduplication.n_ngrammes"):
        _charger(tmp_path, (r"^n_ngrammes = 5$", f"n_ngrammes = {valeur}"))


@pytest.mark.parametrize(
    ("motif", "remplacement", "cle"),
    [
        (r"^taille_echantillon = 30$", "taille_echantillon = 0", "relecture.taille_echantillon"),
        (r"^graine = 42$", "graine = -1", "relecture.graine"),
    ],
)
def test_relecture_invalide(tmp_path: Path, motif: str, remplacement: str, cle: str) -> None:
    with pytest.raises(ConfigurationInvalide, match=cle):
        _charger(tmp_path, (motif, remplacement))


# --- Fichier ------------------------------------------------------------------------------


def test_schema_version(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="schema_version"):
        _charger(tmp_path, (r"^schema_version = 1$", "schema_version = 2"))


def test_table_inconnue(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="traduction"):
        _charger(tmp_path, (r"^\[relecture\]$", "[traduction]\nactif = true\n\n[relecture]"))


def test_fichier_absent(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="illisible"):
        charger_config_donnees(tmp_path / "absent.toml")


def test_longueur_re_inconnue_citee_sans_sa_valeur(tmp_path: Path) -> None:
    secret = "valeur-saisie-factice"
    with pytest.raises(ConfigurationInvalide) as exc:
        _charger(tmp_path, (r"^re_longueurs = .*$", f're_longueurs = ["{secret}"]'))
    assert "re_longueurs" in str(exc.value)
    assert secret not in str(exc.value)


# --- [generateur.plafonds_mots] (story 9.10) ------------------------------------------------


def test_plafonds_mots_reels() -> None:
    plafonds = charger_config_donnees().generateur.plafonds_mots
    assert plafonds == {"Q": 160, "RD": 120, "CR": 400, "LC": 150, "CT": 150, "generique": 200}


def test_plafonds_mots_relus_par_le_generateur() -> None:
    generateur = _generateur()
    attendu = charger_config_donnees().generateur.plafonds_mots
    assert generateur.charger_plafonds_mots(FICHIER_REEL) == attendu


@pytest.mark.parametrize(
    ("ligne", "motif"),
    [
        ("Q = 0", "generateur.plafonds_mots.Q"),
        ("Q = -1", "generateur.plafonds_mots.Q"),
        ('Q = "160"', "generateur.plafonds_mots.Q"),
        ("CO = 100", "generateur.plafonds_mots"),
        ("RE = 100", "generateur.plafonds_mots"),
        ("TR = 100", "generateur.plafonds_mots"),
    ],
)
def test_plafonds_mots_invalides(tmp_path: Path, ligne: str, motif: str) -> None:
    with pytest.raises(ConfigurationInvalide, match=re.escape(motif)):
        _charger(tmp_path, (r"^Q = 160$", ligne))


def test_plafonds_mots_optionnels(tmp_path: Path) -> None:
    texte = _texte_reel().split("[generateur.plafonds_mots]")[0]
    chemin = tmp_path / "donnees.toml"
    chemin.write_text(texte, encoding="utf-8")
    assert charger_config_donnees(chemin).generateur.plafonds_mots == {}
