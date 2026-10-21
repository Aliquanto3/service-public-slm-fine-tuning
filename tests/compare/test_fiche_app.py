"""Données du comparatif des modèles de l'application (story 17.5a) : runs factices."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from slmsp.budget.config import ConfigTarifs
from slmsp.core.config import charger_toml
from slmsp.core.erreurs import ConfigurationInvalide
from slmsp.evaluation import bootstrap, fiche_app
from slmsp.evaluation.fiche_app import (
    ConfigFicheApp,
    EntreeApp,
    ErreurFicheApp,
    FicheApp,
    construire_fiche,
)

from .conftest import ecrire_notation, ecrire_run

REF = "20261020-100000-ref-aaaa"
AUTRE = "20261020-100001-autre-bbbb"
CLOUD = "20261020-100002-cloud-cccc"
GEN = "20261020-090000-distant-dddd"
MESURE = "20261020-110000-h-ram-eeee"
COMMUN = {"licence": "Apache 2.0", "hebergement": "Poste de l'Agent"}


def _tarifs() -> ConfigTarifs:
    return ConfigTarifs.model_validate(
        {
            "schema_version": 1,
            "taux_usd_eur": {"valeur": 1.0, "date": "2026-10-12", "source": "factice"},
            "modeles": {
                "<modele-factice>": {
                    "devise": "USD",
                    "date": "2026-10-21",
                    "source": "factice",
                    "modes": {"direct": {"entree": 0.25, "sortie": 2.0}},
                }
            },
        }
    )


def _entrees() -> list[EntreeApp]:
    return [
        EntreeApp(
            id="ref",
            libelle="Réf",
            emplacement="poste",
            run_notation=REF,
            run_mesure=MESURE,
            **COMMUN,
        ),
        EntreeApp(id="autre", libelle="Autre", emplacement="poste", run_notation=AUTRE, **COMMUN),
        EntreeApp(
            id="cloud",
            libelle="Cloud",
            emplacement="cloud",
            run_notation=CLOUD,
            run_generation=GEN,
            licence="Apache 2.0",
            hebergement="<hébergeur-factice>",
        ),
    ]


def _config(entrees: list[EntreeApp] | None = None) -> ConfigFicheApp:
    return ConfigFicheApp(schema_version=1, reference="ref", modeles=entrees or _entrees())


def _ligne(nom: str, a: float, b: float) -> bootstrap.LigneComparaison:
    ic = bootstrap.Intervalle(b - a - 2, b - a + 2)
    return bootstrap.LigneComparaison(nom, a, b, b - a, ic, 0.9, 100)


def _faux_bootstrap(ids: Any, racine: Path, tirages: int, graine: int) -> Any:
    notes = {REF: 50.0, AUTRE: 40.0, CLOUD: 70.0}
    modeles = [
        fiche_app._QualiteModele(
            observes={"Q": notes[i] + 1, bootstrap.QUALITE: notes[i]},
            bruit=4.5,
            lignes=None
            if rang == 0
            else {
                "Q": _ligne("Q", 51.0, notes[i] + 1),
                bootstrap.QUALITE: _ligne(bootstrap.QUALITE, 50.0, notes[i]),
            },
            non_notes=0,
            items_notes=30,
        )
        for rang, i in enumerate(ids)
    ]
    return fiche_app._Qualites(modeles, {"Q": 20, "RD": 10}, [])


def _appel(item: str, statut: str, cout: float, delai: int | None, debit: float | None) -> str:
    return json.dumps(
        {
            "item_id": item,
            "statut": statut,
            "cout_eur": cout,
            "modele_id": "<modele-factice>",
            "delai_premier_token_ms": delai,
            "debit_tokens_s": debit,
        }
    )


def _depot(racine: Path, *, gen_lie: str = GEN) -> None:
    for identifiant, qualite in ((REF, 50.0), (AUTRE, 40.0)):
        ecrire_notation(racine, identifiant, "base:granite", {"Q": qualite}, jeu="dev1")
    dossier = ecrire_run(
        racine,
        "eval-notation",
        CLOUD,
        config={"run_generation": gen_lie},
        modele_ref="base:granite",
    )
    contenu = json.loads((racine / "runs/eval-notation" / REF / "scores.json").read_text("utf-8"))
    contenu["run_generation"] = gen_lie
    (dossier / "scores.json").write_text(json.dumps(contenu), encoding="utf-8")
    generation = ecrire_run(racine, "eval-generation", GEN)
    lignes = [
        _appel("A", "ok", 0.001, 600, 100.0),
        _appel("B", "ok", 0.003, 800, 60.0),
        _appel("C", "erreur", 0.5, None, None),
    ]
    (generation / fiche_app.NOM_APPELS).write_text("\n".join(lignes) + "\n", encoding="utf-8")
    dossier_mesure = ecrire_run(racine, "measure", MESURE)
    resultat = {
        "valeurs": {
            "debit_tps_mediane": 12.345,
            "premier_token_s_mediane": 0.7084,
            "ram_max_go": 4.1236,
        },
        "environnement": {"cpu": "<cpu-factice>", "nb_coeurs": 8, "os": "<os-factice>"},
        "parametres": {"plafond_threads": 4, "quantification": "q4_k_m"},
    }
    (dossier_mesure / fiche_app.NOM_MESURE).write_text(json.dumps(resultat), encoding="utf-8")


@pytest.fixture
def depot(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    _depot(tmp_path)
    monkeypatch.setattr(fiche_app, "_bootstrap", _faux_bootstrap)
    return tmp_path


def _construire(racine: Path, config: ConfigFicheApp | None = None) -> FicheApp:
    return construire_fiche(
        config or _config(),
        racine,
        tarifs=_tarifs(),
        commit="abc",
        maintenant=lambda: datetime(2026, 10, 21, 12, 0, tzinfo=UTC),
    )


def test_agregats_et_reference(depot: Path) -> None:
    fiche = _construire(depot)
    ref, autre, cloud = fiche.modeles
    assert [m.id for m in (ref, autre, cloud)] == ["ref", "autre", "cloud"]
    assert ref.reference and ref.ecart_reference is None
    assert (ref.qualite.score, autre.qualite.score, cloud.qualite.score) == (50.0, 40.0, 70.0)
    assert autre.qualite.bruit_items == 4.5
    assert autre.ecart_reference is not None
    assert autre.ecart_reference.qualite is not None
    assert autre.ecart_reference.qualite.ecart == -10.0
    assert autre.ecart_reference.qualite.ic_bas == -12.0
    assert fiche.jeu_version == "dev1"
    assert fiche.items_par_tache == {"Q": 20, "RD": 10}
    assert fiche.genere_le == "2026-10-21T12:00:00+00:00"
    assert fiche.commit == "abc"
    assert any("±4,5 à ±4,5" in a for a in fiche.avertissements)


def test_reference_toujours_en_tete(depot: Path) -> None:
    entrees = _entrees()
    config = ConfigFicheApp(
        schema_version=1, reference="ref", modeles=[entrees[1], entrees[0], entrees[2]]
    )
    assert [m.id for m in _construire(depot, config).modeles] == ["ref", "autre", "cloud"]


def test_cout_poste_et_cloud(depot: Path) -> None:
    ref, _, cloud = _construire(depot).modeles
    assert ref.cout.cout_api_eur == 0.0
    assert ref.cout.eur_pour_1000_demandes is None
    assert "non chiffrés" in ref.cout.mention
    # tous les appels facturés, y compris l'appel en erreur : 0,504 € / 30 items notés x 1000
    assert cloud.cout.eur_pour_1000_demandes == 16.8
    assert "relances et appels d'outils compris" in cloud.cout.mention
    assert cloud.cout.prix_mtok is not None
    assert (cloud.cout.prix_mtok.entree, cloud.cout.prix_mtok.sortie) == (0.25, 2.0)
    assert cloud.cout.prix_mtok.date_releve == "2026-10-21"


def test_vitesses_poste_cloud_et_absente(depot: Path) -> None:
    ref, autre, cloud = _construire(depot).modeles
    assert ref.vitesse is not None
    assert (ref.vitesse.debit_tokens_s, ref.vitesse.premier_token_ms) == (12.35, 708.0)
    assert ref.vitesse.ram_max_go == 4.12
    assert ref.vitesse.machine is not None and "<cpu-factice>" in ref.vitesse.machine
    assert autre.vitesse is None
    assert cloud.vitesse is not None
    assert (cloud.vitesse.debit_tokens_s, cloud.vitesse.premier_token_ms) == (80.0, 700.0)
    assert cloud.vitesse.appels == 2  # l'appel en erreur est écarté
    assert "2 appels réussis" in cloud.vitesse.mention
    assert cloud.runs.generation == GEN and ref.runs.mesure == MESURE


def test_json_conforme_au_schema(depot: Path, tmp_path: Path) -> None:
    sortie = tmp_path / "sous" / "comparatif.json"
    fiche_app.ecrire_fiche(_construire(depot), sortie)
    relu = FicheApp.model_validate_json(sortie.read_text(encoding="utf-8"))
    assert len(relu.modeles) == 3


def test_run_manquant_refuse(depot: Path) -> None:
    entrees = _entrees()
    entrees[1] = entrees[1].model_copy(update={"run_notation": "20260101-000000-absent-ffff"})
    with pytest.raises(ErreurFicheApp, match="introuvable"):
        _construire(depot, _config(entrees))


def test_run_incomplet_refuse(depot: Path) -> None:
    etat = {"schema_version": 1, "horodatage": "2026-10-20T10:00:00+00:00", "pid": 1}
    etat["statut"] = "interrompu"
    (depot / "runs/eval-notation" / AUTRE / "etat.jsonl").write_text(
        json.dumps(etat) + "\n", encoding="utf-8"
    )
    with pytest.raises(ErreurFicheApp, match="non complet"):
        _construire(depot)


def test_generation_non_liee_a_la_notation_refusee(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _depot(tmp_path, gen_lie="20260101-000000-autre-gen-ffff")
    monkeypatch.setattr(fiche_app, "_bootstrap", _faux_bootstrap)
    with pytest.raises(ErreurFicheApp, match="porte sur"):
        _construire(tmp_path)


def test_jeu_ou_juge_different_refuse(depot: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*_args: Any, **_kw: Any) -> Any:
        raise ValueError("runs non comparables : jeux dev1, v1.1")

    monkeypatch.undo()  # retour au vrai `_bootstrap` : on exerce la conversion d'erreur
    monkeypatch.setattr(bootstrap, "comparer", refuse)
    monkeypatch.setattr(bootstrap, "charger_run", lambda *_a, **_k: None)
    monkeypatch.setattr(bootstrap, "items_non_notes", lambda _c: set())
    monkeypatch.setattr(
        fiche_app.cfg, "charger_evaluation", lambda: type("C", (), {"seuils": None})()
    )
    with pytest.raises(ErreurFicheApp, match="non comparables"):
        _construire(depot)


def test_config_incoherente_refusee() -> None:
    with pytest.raises(ValueError, match="run_generation"):
        EntreeApp(id="c", libelle="C", emplacement="cloud", run_notation="r", **COMMUN)
    with pytest.raises(ValueError, match="absente"):
        ConfigFicheApp(schema_version=1, reference="zzz", modeles=_entrees())


def test_config_exemple_valide() -> None:
    racine = Path(__file__).resolve().parents[2]
    config = charger_toml(racine / "config" / fiche_app.NOM_CONFIG, ConfigFicheApp)
    assert config.reference in {m.id for m in config.modeles}
    with pytest.raises(ConfigurationInvalide):
        charger_toml(racine / "config" / "absent.toml", ConfigFicheApp)


def test_run_notation_partiel_refuse(depot: Path) -> None:
    """Revue 17.5a : la spec exige un run de notation complet."""
    etat = {"schema_version": 1, "horodatage": "2026-10-20T10:00:00+00:00", "pid": 1}
    etat["statut"] = "partiel-erreur"
    (depot / "runs/eval-notation" / AUTRE / "etat.jsonl").write_text(
        json.dumps(etat) + "\n", encoding="utf-8"
    )
    with pytest.raises(ErreurFicheApp, match="non complet"):
        _construire(depot)


class _Charge:
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self.items = [type("I", (), {"id": f"Q-{n}", "code": "Q"})() for n in range(4)]

    def par_tache(self) -> dict[str, list[Any]]:
        return {"Q": self.items}


def test_appariement_retire_les_items_non_notes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Revue 17.5a : chaque paire exclut les items non notés dans l'un des deux runs."""
    non_notes = {REF: {"Q-0"}, AUTRE: {"Q-1"}, CLOUD: set()}
    appels: list[tuple[list[str], set[str]]] = []

    def comparer(runs: Any, *, tirages: int, graine: int, exclus: Any) -> bootstrap.Resultat:
        appels.append(([r.run_id for r in runs], set(exclus)))
        ids = [r.run_id for r in runs]
        lignes = [_ligne(bootstrap.QUALITE, 50.0, 40.0)] if len(ids) > 1 else []
        comparaisons = [bootstrap.Comparaison(ids[0], ids[1], lignes)] if len(ids) > 1 else []
        return bootstrap.Resultat(
            runs=ids,
            tirages=tirages,
            graine=graine,
            comparaisons=comparaisons,
            bruit_qualite={i: 4.0 for i in ids},
            items_communs={"Q": 4 - len(exclus)},
            observes=[{bootstrap.QUALITE: 50.0}, {bootstrap.QUALITE: 40.0}][: len(ids)],
        )

    monkeypatch.setattr(fiche_app.cfg, "charger_evaluation", lambda: type("C", (), {"seuils": 0}))
    monkeypatch.setattr(bootstrap, "charger_run", lambda i, *_a: _Charge(i))
    monkeypatch.setattr(bootstrap, "items_non_notes", lambda c: non_notes[c.run_id])
    monkeypatch.setattr(bootstrap, "comparer", comparer)
    qualites = fiche_app._bootstrap([REF, AUTRE, CLOUD], Path("."), 10, 7)
    assert appels == [([REF], {"Q-0"}), ([REF, AUTRE], {"Q-0", "Q-1"}), ([REF, CLOUD], {"Q-0"})]
    assert [q.items_notes for q in qualites.modeles] == [3, 3, 4]
    assert any("2 item(s) non noté(s)" in a for a in qualites.avertissements)


@pytest.mark.parametrize(
    "lignes",
    [
        [],
        [json.dumps({"item_id": "A", "statut": "ok", "cout_eur": None, "modele_id": "m"})],
        [json.dumps({"item_id": "A", "statut": "ok", "cout_eur": 0.1})],
        ["[1, 2]"],
    ],
)
def test_appels_mal_formes_refuses(depot: Path, lignes: list[str]) -> None:
    """Revue 17.5a : listes vides, coûts nuls ou clés manquantes donnent ErreurFicheApp."""
    chemin = depot / "runs/eval-generation" / GEN / fiche_app.NOM_APPELS
    chemin.write_text("".join(f"{x}\n" for x in lignes), encoding="utf-8")
    with pytest.raises(ErreurFicheApp):
        _construire(depot)


@pytest.mark.parametrize(
    "modif",
    [
        {"valeurs": {"debit_tps_mediane": None}},
        {"environnement": None},
        {"parametres": {"modele": "base:autre-modele"}},
    ],
)
def test_mesure_mal_formee_ou_d_un_autre_modele_refusee(depot: Path, modif: dict[str, Any]) -> None:
    chemin = depot / "runs/measure" / MESURE / fiche_app.NOM_MESURE
    resultat = json.loads(chemin.read_text(encoding="utf-8"))
    for cle, valeur in modif.items():
        if isinstance(valeur, dict) and isinstance(resultat.get(cle), dict):
            resultat[cle].update(valeur)
        else:
            resultat[cle] = valeur
    chemin.write_text(json.dumps(resultat), encoding="utf-8")
    with pytest.raises(ErreurFicheApp):
        _construire(depot)


def test_run_notation_en_double_refuse() -> None:
    entrees = _entrees()
    entrees[1] = entrees[1].model_copy(update={"run_notation": REF})
    with pytest.raises(ValueError, match="même run de notation"):
        _config(entrees)
