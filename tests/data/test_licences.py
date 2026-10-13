"""Registre des licences (story 9.1, FR-31, AD-3 verrou 5)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from slmsp.core.canonique import sha256_hex
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import (
    ConfigurationInvalide,
    LectureInterdite,
    ProvenanceInvalide,
    SourceSansLicence,
)
from slmsp.data.licences import (
    GENERE_PAR_ADMIS,
    USAGES,
    VARIANTES,
    RegistreLicences,
    UsageInterdit,
)

RELEVE = date(2026, 10, 12)

REVISIONS_RELEVEES = {
    "AgentPublic/service-public": "7ddda096b33d48dbda8143fc8c349a8b0e031a3a",
    "AgentPublic/data-gouv-datasets-catalog": "11f3d3c9481ad478dbcff52e85d73b7fd10533ce",
    "AgentPublic/sp_questions_corpus": "495a22cf7b572621a85d2f3e97783b2f4189c47e",
    "AgentPublic/assistant_ia_questions_corpus": "62cef57af7cc5fe54862a8118c221246771ad9ea",
    "AgentPublic/retriever_dataset": "aab978b2db590116dadd108f337bfbda036887e1",
    "AgentPublic/piaf": "bda8c063bc7297180796cd835d1974c0bc71c521",
    "AgentPublic/MCQ-eval": "d104aa4fef453abe9716e8866c68778a0804198c",
    "esoria3/french_simplified": "baebde461d0fd28baba32671a9af16826c55ccee",
    "OpenLLM-France/Claire-Dialogue-French-0.1": "2d003b86aff5b622533ecfea29ada554f3e6db03",
}
SOURCES_SANS_REVISION = {"mistral/reponses-generateur", "data.gouv/reponses-outils-mcp"}


# --- Fixtures -----------------------------------------------------------------------------


def _entree(
    ident: str = "org/jeu-a",
    *,
    usage: str = "diffusable",
    auteur: str | None = "public",
    genere_par: str | None = "humain",
    extra: str = "",
) -> str:
    lignes = ["[[sources]]", f'id = "{ident}"', 'licence = "licence-factice"', f'usage = "{usage}"']
    if auteur is not None:
        lignes.append(f'auteur_contenu = "{auteur}"')
    if genere_par is not None:
        lignes.append(f'genere_par = "{genere_par}"')
    if extra:
        lignes.append(extra)
    return "\n".join(lignes) + "\n"


def _ecrire(racine: Path, *entrees: str, entete: str = "schema_version = 1\n") -> Path:
    chemin = racine / "data" / "registre-licences.toml"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(entete + "\n" + "\n".join(entrees), encoding="utf-8")
    return chemin


def _charger(racine: Path, *entrees: str, entete: str = "schema_version = 1\n") -> RegistreLicences:
    _ecrire(racine, *entrees, entete=entete)
    return RegistreLicences.charger(racine=racine)


@pytest.fixture
def registre(tmp_path: Path) -> RegistreLicences:
    return _charger(
        tmp_path,
        _entree("org/diffusable", usage="diffusable"),
        _entree("org/recherche", usage="recherche"),
        _entree("org/evaluation", usage="evaluation_seulement"),
        _entree("org/mistral", auteur="mistral", genere_par="mistral"),
        _entree("org/api", genere_par="api-publique"),
    )


# --- Registre réel ------------------------------------------------------------------------


def test_registre_reel_charge() -> None:
    registre = RegistreLicences.charger()
    assert set(registre.ids) == set(REVISIONS_RELEVEES) | SOURCES_SANS_REVISION
    assert len(registre.ids) == len(set(registre.ids))
    assert registre.chemin == Path("data/registre-licences.toml")


def test_registre_reel_releve_des_jeux() -> None:
    registre = RegistreLicences.charger()
    for ident, revision in REVISIONS_RELEVEES.items():
        source = registre.source(ident)
        assert source.licence
        assert source.verifie_le == RELEVE, ident
        assert source.revision == revision, ident
    for ident in SOURCES_SANS_REVISION:
        source = registre.source(ident)
        assert source.verifie_le is None
        assert source.revision is None


def test_registre_reel_usages() -> None:
    registre = RegistreLicences.charger()
    assert registre.source("AgentPublic/MCQ-eval").usage == "evaluation_seulement"
    assert registre.source("esoria3/french_simplified").usage == "evaluation_seulement"
    assert registre.source("OpenLLM-France/Claire-Dialogue-French-0.1").usage == "recherche"
    assert registre.source("AgentPublic/retriever_dataset").usage == "recherche"
    assert registre.source("AgentPublic/service-public").licence == "etalab-2.0"
    with pytest.raises(UsageInterdit):
        registre.exiger("AgentPublic/MCQ-eval", "recherche")
    with pytest.raises(UsageInterdit):
        registre.exiger("OpenLLM-France/Claire-Dialogue-French-0.1", "diffusable")
    assert registre.exiger("OpenLLM-France/Claire-Dialogue-French-0.1", "recherche")


def test_registre_reel_provenances() -> None:
    registre = RegistreLicences.charger()
    generateur = registre.source("mistral/reponses-generateur")
    assert (generateur.auteur_contenu, generateur.genere_par) == ("mistral", "mistral")
    outils = registre.source("data.gouv/reponses-outils-mcp")
    assert (outils.auteur_contenu, outils.genere_par) == ("public", "api-publique")
    for ident in REVISIONS_RELEVEES:
        source = registre.source(ident)
        assert (source.auteur_contenu, source.genere_par) == ("public", "humain")


def test_revisions_coherentes_avec_sources_toml() -> None:
    """Les jeux MediaTech déjà téléchargés portent la même révision au registre."""
    import tomllib

    sources = tomllib.loads((racine_projet() / "config" / "sources.toml").read_text("utf-8"))
    registre = RegistreLicences.charger()
    for jeu in sources["jeux"]:
        if jeu["depot"] in registre.ids:
            assert registre.source(jeu["depot"]).revision == jeu["revision"]
            assert registre.source(jeu["depot"]).licence == jeu["licence"]


# --- Verrou 5 : provenance ----------------------------------------------------------------


@pytest.mark.parametrize("auteur", ["claude", "inconnu", "humain", "Claude", ""])
def test_auteur_interdit(tmp_path: Path, auteur: str) -> None:
    with pytest.raises(ProvenanceInvalide):
        _charger(tmp_path, _entree(auteur=auteur))


def test_auteur_absent(tmp_path: Path) -> None:
    with pytest.raises(ProvenanceInvalide):
        _charger(tmp_path, _entree(auteur=None))


@pytest.mark.parametrize("genere_par", ["gpt-4o", "claude", "inconnu", "llama", ""])
def test_genere_par_interdit(tmp_path: Path, genere_par: str) -> None:
    with pytest.raises(ProvenanceInvalide):
        _charger(tmp_path, _entree(genere_par=genere_par))


def test_genere_par_absent(tmp_path: Path) -> None:
    with pytest.raises(ProvenanceInvalide):
        _charger(tmp_path, _entree(genere_par=None))


@pytest.mark.parametrize(
    ("auteur", "genere_par"),
    [
        ("public", "mistral"),
        ("anael", "mistral"),
        ("mistral", "humain"),
        ("mistral", "api-publique"),
        ("anael", "api-publique"),
    ],
)
def test_provenance_incoherente(tmp_path: Path, auteur: str, genere_par: str) -> None:
    with pytest.raises(ProvenanceInvalide, match="incohérent"):
        _charger(tmp_path, _entree(auteur=auteur, genere_par=genere_par))


@pytest.mark.parametrize(
    ("auteur", "genere_par"),
    [(a, g) for g, auteurs in GENERE_PAR_ADMIS.items() for a in sorted(auteurs)],
)
def test_provenances_admises(tmp_path: Path, auteur: str, genere_par: str) -> None:
    registre = _charger(tmp_path, _entree(auteur=auteur, genere_par=genere_par))
    assert registre.source("org/jeu-a").genere_par == genere_par


def test_provenance_verifiee_avant_le_schema(tmp_path: Path) -> None:
    """Une entrée à la fois malformée et de provenance interdite lève `ProvenanceInvalide`."""
    with pytest.raises(ProvenanceInvalide):
        _charger(tmp_path, _entree(auteur="claude", usage="hors-liste", extra='cle = "x"'))


def test_provenance_interdite_dans_une_entree_suivante(tmp_path: Path) -> None:
    with pytest.raises(ProvenanceInvalide, match="org/jeu-b"):
        _charger(tmp_path, _entree("org/jeu-a"), _entree("org/jeu-b", genere_par="gpt-4o"))


def test_listes_admises_figees() -> None:
    assert dict(GENERE_PAR_ADMIS) == {
        "humain": frozenset({"public", "anael"}),
        "mistral": frozenset({"mistral"}),
        "api-publique": frozenset({"public"}),
    }
    assert USAGES == ("diffusable", "recherche", "evaluation_seulement")
    assert VARIANTES == ("diffusable", "recherche")
    with pytest.raises(TypeError):
        GENERE_PAR_ADMIS["claude"] = frozenset({"public"})  # type: ignore[index]


# --- exiger -------------------------------------------------------------------------------


def test_source_absente(registre: RegistreLicences) -> None:
    with pytest.raises(SourceSansLicence) as info:
        registre.exiger("x/inconnu", "diffusable")
    assert not isinstance(info.value, UsageInterdit)
    with pytest.raises(SourceSansLicence):
        registre.source("x/inconnu")


def test_usage_interdit_est_une_source_sans_licence() -> None:
    assert issubclass(UsageInterdit, SourceSansLicence)


@pytest.mark.parametrize(
    ("ident", "variante", "admis"),
    [
        ("org/diffusable", "diffusable", True),
        ("org/diffusable", "recherche", True),
        ("org/recherche", "diffusable", False),
        ("org/recherche", "recherche", True),
        ("org/evaluation", "diffusable", False),
        ("org/evaluation", "recherche", False),
        ("org/mistral", "diffusable", True),
        ("org/api", "diffusable", True),
    ],
)
def test_exiger(registre: RegistreLicences, ident: str, variante: str, admis: bool) -> None:
    if admis:
        assert registre.exiger(ident, variante).id == ident
    else:
        with pytest.raises(UsageInterdit):
            registre.exiger(ident, variante)


def test_variante_inconnue(registre: RegistreLicences) -> None:
    with pytest.raises(ValueError, match="variante inconnue"):
        registre.exiger("org/diffusable", "evaluation_seulement")


# --- Registre malformé --------------------------------------------------------------------


def test_toml_invalide(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="TOML invalide"):
        _charger(tmp_path, "[[sources]\nid = ")


def test_cle_inconnue_dans_une_source(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="cle_inconnue"):
        _charger(tmp_path, _entree(extra='cle_inconnue = "x"'))


def test_cle_inconnue_a_la_racine(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="racine_inconnue"):
        _charger(tmp_path, _entree(), entete='schema_version = 1\nracine_inconnue = "x"\n')


def test_id_en_double(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="en double"):
        _charger(tmp_path, _entree("org/jeu-a"), _entree("org/jeu-a", usage="recherche"))


def test_usage_hors_liste_sans_citer_la_valeur(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide) as info:
        _charger(tmp_path, _entree(usage="valeur-saisie-xyz"))
    assert "usage" in str(info.value)
    assert "valeur-saisie-xyz" not in str(info.value)


@pytest.mark.parametrize("entete", ["schema_version = 2\n", "", 'schema_version = "1"\n'])
def test_schema_version(tmp_path: Path, entete: str) -> None:
    with pytest.raises(ConfigurationInvalide):
        _charger(tmp_path, _entree(), entete=entete)


def test_sources_vides(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide):
        _charger(tmp_path, "sources = []\n")


@pytest.mark.parametrize(
    "extra",
    [
        'verifie_le = "2026-10-12"',  # chaîne, pas une date TOML
        'revision = ""',
        "notes = 3",
    ],
)
def test_champs_facultatifs_types(tmp_path: Path, extra: str) -> None:
    with pytest.raises(ConfigurationInvalide):
        _charger(tmp_path, _entree(extra=extra))


@pytest.mark.parametrize("ident", ["sans-organisation", "org/", "/jeu", "org/jeu/x", "org/jeu b"])
def test_id_malforme(tmp_path: Path, ident: str) -> None:
    with pytest.raises(ConfigurationInvalide):
        _charger(tmp_path, _entree(ident))


def test_fichier_absent(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationInvalide, match="illisible"):
        RegistreLicences.charger(racine=tmp_path)


def test_lecture_controlee_hors_liste(tmp_path: Path) -> None:
    autre = tmp_path / "config" / "registre.toml"
    autre.parent.mkdir()
    autre.write_text("schema_version = 1\n" + _entree(), encoding="utf-8")
    with pytest.raises(LectureInterdite):
        RegistreLicences.charger(autre, racine=tmp_path)


def test_chemin_explicite(tmp_path: Path) -> None:
    chemin = _ecrire(tmp_path, _entree())
    registre = RegistreLicences.charger(chemin, racine=tmp_path)
    assert registre.ids == ("org/jeu-a",)


# --- Instantané ---------------------------------------------------------------------------


def test_instantane_et_sha(tmp_path: Path) -> None:
    chemin = _ecrire(
        tmp_path,
        _entree("org/zeta", extra="verifie_le = 2026-10-12"),
        _entree("org/alpha", usage="recherche"),
    )
    registre = RegistreLicences.charger(racine=tmp_path)
    assert registre.sha256 == sha256_hex(chemin.read_bytes())
    assert registre.ids == ("org/alpha", "org/zeta")
    instantane = registre.instantane()
    assert instantane["schema_version"] == 1
    assert instantane["sha256"] == registre.sha256
    assert [s["id"] for s in instantane["sources"]] == ["org/alpha", "org/zeta"]
    assert instantane["sources"][1]["verifie_le"] == "2026-10-12"
    assert instantane["sources"][0]["verifie_le"] is None
    texte = json.dumps(instantane, ensure_ascii=False)
    assert json.dumps(json.loads(texte), sort_keys=True, ensure_ascii=False) == texte
    assert registre.instantane() == instantane


def test_sources_immuables(registre: RegistreLicences) -> None:
    source = registre.source("org/diffusable")
    with pytest.raises(ValidationError):
        source.usage = "recherche"  # type: ignore[misc]
