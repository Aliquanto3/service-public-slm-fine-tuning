"""Story O6a : génération vérifiée branchée sur `generate` (`slmsp.data.generation_verifiee`).

Doublures de `tests/data/conftest.py` (Mistral) et de `tests/fournisseurs` (OpenRouter), aucun
appel réel ; textes factices (D1).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("mistralai")

from slmsp.budget.config import charger_budgets, charger_tarifs  # noqa: E402
from slmsp.budget.registre import RegistreBudget  # noqa: E402
from slmsp.core.artefacts import ouvrir_run  # noqa: E402
from slmsp.core.erreurs import ManifesteInvalide  # noqa: E402
from slmsp.data.config import VerificationConfig  # noqa: E402
from slmsp.data.generation_verifiee import Verificateur  # noqa: E402
from slmsp.data.juge_donnees import PlafondEstimeDepasse  # noqa: E402
from slmsp.fournisseurs.journal import JournalAppels  # noqa: E402

from .test_build import pub  # noqa: E402
from .test_filter import valider  # noqa: E402
from .test_juge_donnees import BUDGETS, F, _tache_du_schema, juge, sortie  # noqa: E402

SOURCE = "Le demandeur doit <x-factice>."
BONNE = "Vous devez <x-factice>."
CONFIG = VerificationConfig(gain_km_min=-1e9)


@pytest.fixture
def banc(tmp_path: Path) -> Any:
    """Faux OpenRouter du juge de données (même banc que `test_juge_donnees`)."""
    dossier = tmp_path / "banc"
    dossier.mkdir()
    (dossier / ".env").write_text(f"OPENROUTER_API_KEY={F.CLE_FACTICE}\n", encoding="utf-8")
    (dossier / "budgets.toml").write_text(BUDGETS.format(plafond=10.0), encoding="utf-8")
    (dossier / "tarifs.toml").write_text(F.TARIFS, encoding="utf-8")
    registre = RegistreBudget(
        charger_budgets(dossier / "budgets.toml"),
        charger_tarifs(dossier / "tarifs.toml"),
        dossier / "budget.sqlite",
    )
    banc = F.Banc(dossier, F.FauxOpenRouter(), registre, JournalAppels(dossier / "journal.sqlite"))
    banc.faux.texte_defaut = lambda corps: sortie(_tache_du_schema(corps))
    return banc


def verificateur(j: Any = None, **kw: Any) -> Verificateur:
    return Verificateur(CONFIG, plafonds_mots={"LC": 150}, juge=j, **kw)


def lancer(monde: Any, cible: str | None, v: Verificateur | None, **kw: Any) -> Any:
    seed = kw.pop("seed", None) or monde.ecrire_seed([pub(monde, "LC", "texte", texte=SOURCE)])
    if cible is not None:
        monde.faux.reponses = [{"texte": cible}]
    return monde.lancer({"LC": 1}, seed=seed, verificateur=v, **kw)


def test_cible_retenue_sans_juge_et_fichiers_du_run(monde: Any) -> None:
    resultat = lancer(monde, BONNE, verificateur())
    run = resultat.run
    assert resultat.statut == "complet"
    assert len(run.lire_jsonl("brut.jsonl")) == 1
    [ligne] = run.lire_jsonl("verification.jsonl")
    assert ligne["issue"] == "retenue" and ligne["essais"][0]["refus_par"] is None
    assert run.manifeste.config["verification"]["sans_juge"] is True
    rapport = json.loads((run.dossier / "rapport.json").read_bytes())
    assert rapport["taches"]["LC"]["acceptees_emblee"] == 1
    for nom in ("echantillon.md", "calibrage.md"):
        assert (run.dossier / nom).is_file()
    assert BONNE in (run.dossier / "echantillon.md").read_text(encoding="utf-8")
    validation = valider(monde, resultat)
    assert validation.run.lire_jsonl("rejets.jsonl") == []


def test_cible_refusee_par_les_tests_ecartee_et_close(monde: Any) -> None:
    resultat = lancer(monde, f"{BONNE} 98765 euros.", verificateur())
    run = resultat.run
    assert resultat.statut == "complet" and run.lire_jsonl("brut.jsonl") == []
    [abandon] = run.lire_jsonl("abandons.jsonl")
    assert abandon["motif"] == "verification_refusee"
    [ecartee] = run.lire_jsonl("ecartees.jsonl")
    assert ecartee["codes"] == ["valeur_absente"] and ecartee["refus_par"] == "tests"
    calibrage = (run.dossier / "calibrage.md").read_text(encoding="utf-8")
    assert abandon["session_id"] in calibrage and "`valeur_absente`" in calibrage
    rapport = json.loads((run.dossier / "rapport.json").read_bytes())
    assert rapport["taches"]["LC"]["codes_bloquants"] == {"valeur_absente": 1}
    assert rapport["taches"]["LC"]["refus_tests"] == 1 and rapport["cout_openrouter_eur"] == 0


def test_juge_accepte_puis_refuse(monde: Any, banc: Any) -> None:
    resultat = lancer(monde, BONNE, verificateur(juge(banc)))
    assert len(resultat.run.lire_jsonl("brut.jsonl")) == 1
    assert [v["verdict"] for v in resultat.run.lire_jsonl("verdicts.jsonl")] == ["accepte"]

    banc.faux.reponses.append({"texte": sortie("LC", notes={"fidelite": 0, "termes": 1})})
    seed = monde.ecrire_seed([pub(monde, "LC", "texte", ligne=2, texte=f"{SOURCE} <autre>")])
    refuse = lancer(monde, BONNE, verificateur(juge(banc)), seed=seed)
    [ecartee] = refuse.run.lire_jsonl("ecartees.jsonl")
    assert ecartee["refus_par"] == "juge" and ecartee["codes"] == ["juge_fidelite"]
    [ligne] = refuse.run.lire_jsonl("verification.jsonl")
    assert ligne["essais"][0]["verdict"] == "refuse" and ligne["essais"][0]["cle_verdict"]


def test_tests_refusent_avant_le_juge(monde: Any, banc: Any) -> None:
    lancer(monde, f"{BONNE} 98765 euros.", verificateur(juge(banc)))
    assert banc.faux.corps() == []


def test_juge_non_conclusif_puis_reprise_sans_double_appel_mistral(monde: Any, banc: Any) -> None:
    banc.faux.reponses.append({"finish_reason": "length"})
    premier = lancer(monde, BONNE, verificateur(juge(banc)))
    assert premier.statut == "partiel-erreur"
    assert premier.run.lire_jsonl("brut.jsonl") == []
    assert len(premier.run.lire_jsonl("interruptions-juge.jsonl")) == 1
    with pytest.raises(ManifesteInvalide):
        monde.lancer({"LC": 1}, reprendre=premier.run.run_id)
    appels_mistral = len(monde.faux.corps)
    repris = monde.lancer(
        {"LC": 1}, reprendre=premier.run.run_id, verificateur=verificateur(juge(banc))
    )
    assert repris.statut == "complet" and len(monde.faux.corps) == appels_mistral
    assert len(repris.run.lire_jsonl("brut.jsonl")) == 1
    assert len(banc.faux.corps()) == 2


def test_plafonds_estimes_refusent_avant_tout_run(monde: Any, banc: Any) -> None:
    seed = monde.ecrire_seed([pub(monde, "LC", "texte", texte=SOURCE)])
    with pytest.raises(PlafondEstimeDepasse):
        lancer(monde, BONNE, verificateur(), seed=seed, plafond_estime_mistral=0.0)
    with pytest.raises(PlafondEstimeDepasse):
        lancer(monde, BONNE, verificateur(juge(banc), plafond_estime_openrouter=1e-9), seed=seed)
    assert not (monde.racine / "runs" / "data-generate").exists()
    assert monde.faux.corps == [] and banc.faux.corps() == []


def test_rejeu_gratuit_sous_plafond_mistral_nul(monde: Any) -> None:
    seed = monde.ecrire_seed([pub(monde, "LC", "texte", texte=SOURCE)])
    lancer(monde, BONNE, None, seed=seed)
    appels = len(monde.faux.corps)
    calibrage = lancer(monde, None, verificateur(), seed=seed, plafond_estime_mistral=0.0)
    assert calibrage.statut == "complet" and len(monde.faux.corps) == appels
    assert ouvrir_run(calibrage.run.run_id, racine=monde.racine).statut_courant() == "complet"


# --- Revue O6a -----------------------------------------------------------------------------


def test_essais_max_au_dela_de_un_refuse_avant_o6b() -> None:
    with pytest.raises(ValueError, match="O6b"):
        verificateur(essais_max=3)
    assert VerificationConfig().essais_max == 1


def test_completer_depuis_refuse_les_taches_verifiees_non_regenerees(monde: Any) -> None:
    seed = monde.ecrire_seed(
        [pub(monde, "LC", "texte", texte=SOURCE), pub(monde, "CO", "question", ligne=2)]
    )
    monde.faux.reponses = [{"texte": BONNE}, {"texte": "<co-factice>"}]
    source = monde.lancer({"LC": 1, "CO": 1}, seed=seed)
    assert source.statut == "complet"
    with pytest.raises(ManifesteInvalide, match="LC"):
        monde.lancer(
            {"LC": 1, "CO": 1},
            seed=seed,
            taches=["CO"],
            completer_depuis=source.run.run_id,
            verificateur=verificateur(),
        )


def test_jugements_en_parallele_ecrits_dans_l_ordre_du_plan(
    monde: Any, banc: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    import threading
    import time

    seed = monde.ecrire_seed(
        [pub(monde, "LC", "texte", ligne=i, texte=f"{SOURCE} <s{i}>") for i in range(1, 6)]
    )
    monde.faux.reponses = [{"texte": BONNE}] * 5
    j = juge(banc, appels_paralleles=4)
    appeler, actifs, pic = j.client.appeler, [0], [0]
    verrou = threading.Lock()

    def lent(*args: Any, **kwargs: Any) -> Any:
        with verrou:
            actifs[0] += 1
            pic[0] = max(pic[0], actifs[0])
        time.sleep(0.2)
        try:
            return appeler(*args, **kwargs)
        finally:
            with verrou:
                actifs[0] -= 1

    monkeypatch.setattr(j.client, "appeler", lent)
    resultat = monde.lancer({"LC": 5}, seed=seed, verificateur=verificateur(j))
    assert resultat.statut == "complet" and pic[0] > 1
    plan = [s["session_id"] for s in resultat.run.lire_jsonl("plan.jsonl")]
    assert [b["session_id"] for b in resultat.run.lire_jsonl("brut.jsonl")] == plan
    assert [v["session_id"] for v in resultat.run.lire_jsonl("verdicts.jsonl")] == plan
    assert len(banc.faux.corps()) == 5
