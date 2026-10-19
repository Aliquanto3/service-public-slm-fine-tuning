"""Juge tiers OpenRouter (`JugeTiers`) et section `juges_tiers` de `juges.toml` (story S3).

Faux serveur OpenRouter (`tests/fournisseurs/factices_openrouter.py`) ; aucun appel réel.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

pytest.importorskip("anthropic")

from slmsp.core.config import racine_projet  # noqa: E402
from slmsp.core.items import Item  # noqa: E402
from slmsp.judge.cache import CacheVerdicts, cle_verdict  # noqa: E402
from slmsp.judge.claude import DemandeJugement  # noqa: E402
from slmsp.judge.config import ConfigJugeTiers, charger_juges  # noqa: E402
from slmsp.judge.grille import Grille  # noqa: E402
from slmsp.judge.prompt import construire_prompt  # noqa: E402
from slmsp.judge.tiers import MOTIF_INTERROMPUE, JugeTiers  # noqa: E402


def _factices() -> ModuleType:
    nom = "openrouter_factices"
    if nom not in sys.modules:
        chemin = Path(__file__).parents[1] / "fournisseurs" / "factices_openrouter.py"
        spec = importlib.util.spec_from_file_location(nom, chemin)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[nom] = module
        spec.loader.exec_module(module)
    return sys.modules[nom]


F = _factices()


def _config(**options: Any) -> ConfigJugeTiers:
    return ConfigJugeTiers(modele=F.MODELE, max_tokens=500, **options)


@pytest.fixture
def banc(tmp_path: Path, doublures: SimpleNamespace) -> Any:
    banc = F.banc(tmp_path / "banc")

    def conforme(corps: dict[str, Any]) -> str:
        schema = corps["response_format"]["json_schema"]["schema"]
        return json.dumps(doublures.verdict_conforme(schema), ensure_ascii=False)

    banc.faux.texte_defaut = conforme
    banc.cache = CacheVerdicts(tmp_path / "verdicts.sqlite")
    return banc


def juge(banc: Any, grille: Grille, **options: Any) -> JugeTiers:
    return JugeTiers("factice", _config(**options), banc.client(), banc.cache, grille)


def demandes(items: dict[str, Item], doublures: SimpleNamespace, *ids: str) -> list[Any]:
    return [DemandeJugement(items[i], doublures.sortie_factice()) for i in ids]


def test_nominal_meme_prompt_que_le_principal(
    banc: Any, grille: Grille, items: dict[str, Item], doublures: SimpleNamespace
) -> None:
    lot = demandes(items, doublures, "CR-001", "Q-002")
    rapport = juge(banc, grille, effort_raisonnement="low").juger(lot)

    assert [r.statut for r in rapport.resultats] == ["juge", "juge"]
    assert rapport.cout_total_eur == pytest.approx(2 * F.COUT)
    for corps, demande, resultat in zip(banc.faux.corps(), lot, rapport.resultats, strict=True):
        prompt = construire_prompt(demande.item, demande.sortie, grille)
        assert corps["messages"] == [{"role": "user", "content": prompt.texte}]
        assert corps["response_format"]["json_schema"]["schema"] == prompt.schema
        assert corps["reasoning"] == {"effort": "low"}
        assert corps["provider"] == {"require_parameters": True}
        assert "temperature" not in corps  # absente de la config : non envoyée
        assert resultat.cle == cle_verdict(
            demande.item,
            demande.sortie,
            prompt,
            F.MODELE,
            _config(effort_raisonnement="low").effort_cle,
        )


def test_cache_relance_sans_payer(
    banc: Any, grille: Grille, items: dict[str, Item], doublures: SimpleNamespace
) -> None:
    lot = demandes(items, doublures, "CR-001")
    juge(banc, grille).juger(lot)
    rapport = juge(banc, grille).juger(lot)
    assert rapport.resultats[0].depuis_cache and rapport.cout_total_eur == 0
    assert len(banc.faux.corps()) == 1


def test_sortie_interrompue_non_mise_en_cache(
    banc: Any, grille: Grille, items: dict[str, Item], doublures: SimpleNamespace
) -> None:
    lot = demandes(items, doublures, "CR-001")
    banc.faux.reponses.append({"finish_reason": "length"})
    (resultat,) = juge(banc, grille).juger(lot).resultats
    assert resultat.statut == "non-juge" and resultat.motif == MOTIF_INTERROMPUE
    assert banc.cache.lire(resultat.cle) is None and banc.cache.echecs(resultat.cle) == 0
    (rejoue,) = juge(banc, grille).juger(lot).resultats  # rejouable
    assert rejoue.statut == "juge" and len(banc.faux.corps()) == 2


def test_deux_sorties_non_conformes_invalide(
    banc: Any, grille: Grille, items: dict[str, Item], doublures: SimpleNamespace
) -> None:
    banc.faux.reponses.extend([{"texte": "<non-json>"}, {"texte": "{}"}])
    (resultat,) = juge(banc, grille).juger(demandes(items, doublures, "CR-001")).resultats
    assert resultat.statut == "invalide"
    assert banc.cache.lire(resultat.cle) is not None


def test_budget_epuise(
    tmp_path: Path, grille: Grille, items: dict[str, Item], doublures: SimpleNamespace
) -> None:
    banc = F.banc(tmp_path / "petit", plafond=0.0001)
    banc.cache = CacheVerdicts(tmp_path / "v.sqlite")
    rapport = juge(banc, grille).juger(demandes(items, doublures, "CR-001", "Q-002"))
    assert rapport.budget_epuise
    assert [r.motif for r in rapport.resultats] == ["budget", "budget"]
    assert banc.faux.requetes == []


def test_401_arrete_les_appels(
    banc: Any, grille: Grille, items: dict[str, Item], doublures: SimpleNamespace
) -> None:
    banc.faux.reponses.append(401)
    rapport = juge(banc, grille).juger(demandes(items, doublures, "CR-001", "Q-002"))
    assert [r.statut for r in rapport.resultats] == ["non-juge", "non-juge"]
    assert len(banc.faux.corps()) == 1


def test_estimer_sans_appel(
    banc: Any, grille: Grille, items: dict[str, Item], doublures: SimpleNamespace
) -> None:
    lot = demandes(items, doublures, "CR-001", "Q-002")
    tiers = juge(banc, grille, sortie_estimee=100, marge_raisonnement=50)
    estimation = tiers.estimer(lot)
    assert estimation.nb_a_juger == 2 and banc.faux.requetes == []
    entrees = sum(tiers._preparer(d).tokens_estimes for d in lot)
    assert estimation.cout_estime_eur == pytest.approx((entrees + 2 * 150) / 1e6)
    assert estimation.cout_pire_cas_eur == pytest.approx((entrees + 2 * 500) / 1e6)
    tiers.juger(lot[:1])
    assert tiers.estimer(lot).nb_en_cache == 1


# --- Configuration --------------------------------------------------------------------------------


def test_juges_toml_actuel_sans_juge_tiers() -> None:
    config = charger_juges()
    assert config.juges_tiers == {}
    assert config.second.modele and config.principal.modele


def test_juges_toml_avec_juge_tiers(tmp_path: Path) -> None:
    texte = (racine_projet() / "config" / "juges.toml").read_text(encoding="utf-8")
    texte += '\n[juges_tiers.deepseek]\nmodele = "deepseek/x"\nmax_tokens = 8000\n'
    chemin = tmp_path / "juges.toml"
    chemin.write_text(texte, encoding="utf-8")
    config = charger_juges(chemin)
    tiers = config.juges_tiers["deepseek"]
    assert tiers.fournisseur == "openrouter" and tiers.usage_budget == "juge-tiers-openrouter"
    assert tiers.sortie_estimation == 3500
    assert config.principal == charger_juges().principal
