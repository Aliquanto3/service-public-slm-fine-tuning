"""Table des Tâches et prompts de Tâche (story 4.1, AD-14, D1.1)."""

from __future__ import annotations

import re
import shutil
import unicodedata
from pathlib import Path

import pytest

from slmsp.core.config import racine_projet
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.core.gabarits import valider_gabarit
from slmsp.harness.taches import (
    CODES_TACHES,
    EMPLACEMENTS,
    TableTaches,
    TacheInconnue,
    VarianteInconnue,
    charger_taches,
)
from slmsp.mcp.outils import OUTILS_AUTORISES

CONFIG = racine_projet() / "config"
DOSSIER_PROMPTS = CONFIG / "prompts" / "taches"
PROMPTS_ATTENDUS = {
    "Q", "RD", "CR", "CR-morceau", "CR-fusion", "LC", "CO", "RE", "CT", "NR", "TR",
}  # fmt: skip


@pytest.fixture(scope="module")
def table() -> TableTaches:
    return charger_taches()


def test_neuf_codes_et_defaut(table: TableTaches) -> None:
    assert table.codes == CODES_TACHES
    assert len(table.codes) == 9
    assert table.code_defaut == "Q"
    assert table.defaut.code == "Q"
    assert all(table.tache(code).actif for code in CODES_TACHES)


def test_outils_autorises(table: TableTaches) -> None:
    assert table.tache("RD").outils_autorises == OUTILS_AUTORISES
    for code in ("Q", "CR", "LC", "CO", "RE", "CT", "NR", "TR"):
        assert table.tache(code).outils_autorises == ()


def test_avertissement_et_variantes(table: TableTaches) -> None:
    assert table.tache("Q").avertissement == "Ne vaut pas avis juridique."
    assert table.tache("TR").avertissement == "Traduction automatique, à vérifier."
    assert all(table.tache(c).avertissement is None for c in CODES_TACHES if c not in ("Q", "TR"))
    cr = table.tache("CR")
    assert set(cr.variantes) == {"morceau", "fusion"}
    assert cr.prompt_pour().id == "CR"
    assert cr.prompt_pour("morceau").id == "CR-morceau"
    assert cr.prompt_pour("fusion").id == "CR-fusion"
    assert all(not table.tache(c).variantes for c in CODES_TACHES if c != "CR")
    with pytest.raises(VarianteInconnue, match="inconnue"):
        cr.prompt_pour("autre")
    with pytest.raises(VarianteInconnue):
        table.tache("LC").prompt_pour("morceau")


def test_tache_inconnue(table: TableTaches) -> None:
    with pytest.raises(TacheInconnue, match="ZZ"):
        table.tache("ZZ")


def test_prompts_charges(table: TableTaches) -> None:
    emplacements = {
        "Q": ("question", "passages"),
        "RD": ("demande", "passages"),
        "NR": ("demande",),
        "CR": ("consigne", "notes", "transcription"),
        "LC": ("consigne", "texte"),
        "CO": ("consigne", "texte"),
        "RE": ("consigne", "texte", "document", "longueur_demandee"),
        "CT": ("consigne", "type_courrier", "objet", "elements_connus"),
        "TR": ("consigne", "langue_source", "langue_cible", "texte"),
    }
    for code, attendus in emplacements.items():
        prompt = table.tache(code).prompt
        assert prompt.emplacements == attendus
        assert prompt.tache == code
        assert prompt.version == 1
        assert prompt.consigne and "## " not in prompt.consigne
        assert len(prompt.sha256) == 64
    cr = table.tache("CR")
    assert cr.prompt_pour("morceau").emplacements == (
        "consigne",
        "partie",
        "notes",
        "transcription",
    )
    assert cr.prompt_pour("fusion").emplacements == ("consigne", "parties")


def test_tous_les_prompts_reels_passent_le_validateur() -> None:
    fichiers = sorted(DOSSIER_PROMPTS.glob("*.md"))
    assert {f.stem for f in fichiers} == PROMPTS_ATTENDUS
    for fichier in fichiers:
        gabarit = valider_gabarit(fichier)
        assert gabarit.id == fichier.stem
        assert set(gabarit.emplacements) <= set(EMPLACEMENTS)


# --- D1.1 : aucun exemple, aucune réponse type, aucune amorce, aucun dialogue ------------------

_MOTIFS_D11 = re.compile(
    r"exempl|exampl|\bpar ex\b|\be\.g\b|few.?shot|reponses? types?|modeles? de reponse|"
    r"\bvoici\b|\bi\.e\b|<\||\[inst\]|```|\bsortie attendue\b|\breponse attendue\b"
)
_DIALOGUE = re.compile(
    r"^\s*(?:[-*+]\s+)?(?:question|reponse|q|r|utilisateur|assistant|agent|usager|systeme|"
    r"system|entree|sortie|user|input|output)\s*:",
    re.MULTILINE,
)


def _sans_accent(texte: str) -> str:
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c)).casefold()


@pytest.mark.parametrize("nom", sorted(PROMPTS_ATTENDUS))
def test_d11_prompts_sans_exemple_ni_dialogue(nom: str) -> None:
    texte = (DOSSIER_PROMPTS / f"{nom}.md").read_text(encoding="utf-8")
    consigne = texte.split("## Consigne", 1)[1].split("## Emplacements", 1)[0]
    normalise = _sans_accent(texte)
    assert not _MOTIFS_D11.search(normalise)
    assert not _DIALOGUE.search(_sans_accent(consigne))
    assert "«" not in consigne and '"' not in consigne, "aucune citation de texte modèle"
    assert "[" not in consigne and "{" not in consigne, "aucun emplacement rempli"
    assert len(texte) <= 4000


# --- Chargement fautif ------------------------------------------------------------------------


@pytest.fixture
def copie(tmp_path: Path) -> Path:
    shutil.copy(CONFIG / "taches.toml", tmp_path / "taches.toml")
    shutil.copytree(DOSSIER_PROMPTS, tmp_path / "prompts" / "taches")
    return tmp_path


def _fautes_chargement(dossier: Path) -> str:
    with pytest.raises(ConfigurationInvalide) as info:
        charger_taches(dossier / "taches.toml")
    return str(info.value)


def _remplacer(chemin: Path, ancien: str, nouveau: str) -> None:
    texte = chemin.read_text(encoding="utf-8")
    assert ancien in texte
    chemin.write_text(texte.replace(ancien, nouveau, 1), encoding="utf-8")


def test_copie_valide_avec_dossier_par_defaut(copie: Path) -> None:
    assert charger_taches(copie / "taches.toml").codes == CODES_TACHES
    autre = copie / "ailleurs"
    shutil.move(copie / "prompts" / "taches", autre)
    assert charger_taches(copie / "taches.toml", autre).defaut.code == "Q"


def test_code_manquant(copie: Path) -> None:
    toml = copie / "taches.toml"
    texte = toml.read_text(encoding="utf-8")
    debut = texte.index("[taches.TR]")
    toml.write_text(texte[:debut], encoding="utf-8")
    assert "manquant(s) : TR" in _fautes_chargement(copie)


def test_code_en_trop(copie: Path) -> None:
    toml = copie / "taches.toml"
    with toml.open("a", encoding="utf-8") as flux:
        flux.write('\n[taches.ZZ]\nlibelle = "x"\nactif = true\nprompt = "NR.md"\n')
    assert "inconnu(s) : ZZ" in _fautes_chargement(copie)


def test_defaut_inconnu(copie: Path) -> None:
    _remplacer(copie / "taches.toml", 'defaut = "Q"', 'defaut = "ZZ"')
    assert "« defaut »" in _fautes_chargement(copie)


def test_outil_non_autorise(copie: Path) -> None:
    _remplacer(copie / "taches.toml", '"get_resource_info",', '"get_resource_info", "outil_x",')
    assert "outil_x" in _fautes_chargement(copie)


def test_outil_en_double(copie: Path) -> None:
    _remplacer(
        copie / "taches.toml", '"get_resource_info",', '"get_resource_info", "search_datasets",'
    )
    assert "en double" in _fautes_chargement(copie)


def test_cle_inconnue(copie: Path) -> None:
    _remplacer(copie / "taches.toml", 'prompt = "TR.md"', 'prompt = "TR.md"\nautre = 1')
    assert "autre" in _fautes_chargement(copie)


def test_prompt_absent_ou_avec_dossier(copie: Path) -> None:
    (copie / "prompts" / "taches" / "TR.md").unlink()
    assert "illisible" in _fautes_chargement(copie)
    _remplacer(copie / "taches.toml", 'prompt = "TR.md"', 'prompt = "../TR.md"')
    assert "sans dossier" in _fautes_chargement(copie)


def test_id_et_tache_incoherents(copie: Path) -> None:
    prompts = copie / "prompts" / "taches"
    _remplacer(prompts / "LC.md", "id: LC", "id: LX")
    _remplacer(prompts / "CR-fusion.md", "tache: CR", "tache: LC")
    message = _fautes_chargement(copie)
    assert "« id » doit valoir « LC »" in message
    assert "« tache » doit valoir « CR »" in message


def test_emplacement_hors_vocabulaire(copie: Path) -> None:
    _remplacer(copie / "prompts" / "taches" / "LC.md", "- texte :", "- inconnu :")
    assert "hors vocabulaire : inconnu" in _fautes_chargement(copie)


def test_emplacements_incoherents(copie: Path) -> None:
    prompts = copie / "prompts" / "taches"
    _remplacer(prompts / "NR.md", "- demande :", "- texte : <d>\n- demande :")
    _remplacer(prompts / "LC.md", "- texte :", "- passages : <d>\n- texte :")
    message = _fautes_chargement(copie)
    assert "Tâche NR" in message and "un seul emplacement" in message
    assert "« passages » n'est admis qu'avec une entrée texte" in message


def test_prompt_fautif_refuse_au_chargement(copie: Path) -> None:
    _remplacer(
        copie / "prompts" / "taches" / "CO.md", "## Emplacements", "Voici <x>\n\n## Emplacements"
    )
    message = _fautes_chargement(copie)
    assert "Tâche CO" in message and "voici" in message
