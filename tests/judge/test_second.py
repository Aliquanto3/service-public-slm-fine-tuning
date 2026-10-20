"""Second juge Mistral (`JugeMistral`) : une ligne de la matrice « second juge » par test.

Faux serveur Mistral en `httpx2.MockTransport` derrière la garde réseau ; registre, tarifs,
cache et journaux dans `tmp_path`. Aucun appel réel.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx2  # noqa: TID251 (tests du second juge : transport factice)
import pytest

pytest.importorskip("anthropic")
pytest.importorskip("mistralai")

from slmsp.budget.config import charger_budgets, charger_tarifs  # noqa: E402
from slmsp.budget.registre import RegistreBudget  # noqa: E402
from slmsp.core.erreurs import BudgetEpuise, ConfigurationInvalide  # noqa: E402
from slmsp.core.items import Item  # noqa: E402
from slmsp.judge.cache import CacheVerdicts, cle_verdict  # noqa: E402
from slmsp.judge.claude import DemandeJugement  # noqa: E402
from slmsp.judge.config import charger_juges  # noqa: E402
from slmsp.judge.grille import Grille  # noqa: E402
from slmsp.judge.prompt import ItemNonJugeable, construire_prompt, valider_sortie  # noqa: E402
from slmsp.judge.second import JugeMistral  # noqa: E402
from slmsp.mistral.client import ClientMistral, ModeleMistralRefuse, fabriquer_sdk  # noqa: E402
from slmsp.mistral.config import charger_mistral  # noqa: E402
from slmsp.net.journal import JournalMemoire  # noqa: E402

MODELE = "mistral-large-latest"
USAGE = (1000, 200)
COUT = (1000 + 200) / 1_000_000  # 1 $/M en entrée et en sortie, taux 1
TARIFS = f"""
schema_version = 1

[taux_usd_eur]
valeur = 1.0
date = 2026-10-12
source = "test"

[modeles."{MODELE}"]
devise = "USD"
date = 2026-10-12
source = "test"

[modeles."{MODELE}".modes.direct]
entree = 1.0
sortie = 1.0
"""


@dataclass
class FauxMistral:
    """Faux serveur : verdict conforme au schéma reçu, sauf réponse imposée par item."""

    verdict_conforme: Callable[[dict[str, Any]], dict[str, Any]]
    reponses: dict[str, list[Any]] = field(default_factory=dict)
    """Par item : statut HTTP (`int`) ou {"texte", "finish_reason", "model"}."""
    requetes: list[dict[str, Any]] = field(default_factory=list)

    def items(self) -> list[str]:
        return [_item_du_corps(c) for c in self.requetes]

    def __call__(self, requete: Any) -> Any:
        corps = json.loads(requete.content)
        self.requetes.append(corps)
        item_id = _item_du_corps(corps)
        file = self.reponses.get(item_id) or []
        spec = file.pop(0) if file else {}
        if isinstance(spec, int):
            return httpx2.Response(spec, json={"object": "error", "message": "<erreur>"})
        texte = spec.get("texte")
        if texte is None:
            schema = corps["response_format"]["json_schema"]["schema"]
            texte = json.dumps(self.verdict_conforme(schema), ensure_ascii=False)
        return httpx2.Response(
            200,
            json={
                "id": "cmpl-factice",
                "object": "chat.completion",
                "model": spec.get("model", "mistral-large-2512"),
                "created": 1760227200,
                "usage": {
                    "prompt_tokens": USAGE[0],
                    "completion_tokens": USAGE[1],
                    "total_tokens": sum(USAGE),
                },
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": spec.get("finish_reason", "stop"),
                        "message": {"role": "assistant", "content": texte},
                    }
                ],
            },
        )


SANS_SCHEMA = "<sans-schema>"
"""Clé des réponses imposées quand la requête ne porte pas de schéma (`json_object`)."""


def _item_du_corps(corps: dict[str, Any]) -> str:
    format_reponse = corps["response_format"]
    if format_reponse.get("type") != "json_schema":
        return SANS_SCHEMA
    return format_reponse["json_schema"]["schema"]["properties"]["id"]["const"]


class RegistreBorne(RegistreBudget):
    """Registre qui lève `BudgetEpuise` à partir de la réservation `epuise_a` (1 = première)."""

    epuise_a: int | None = None
    reservations = 0

    def reserver(self, *args: Any, **kwargs: Any) -> int:
        self.reservations += 1
        if self.epuise_a is not None and self.reservations >= self.epuise_a:
            raise BudgetEpuise("budget épuisé (test)")
        return super().reserver(*args, **kwargs)


@dataclass
class Banc:
    dossier: Path
    faux: FauxMistral
    grille: Grille
    doublures: SimpleNamespace
    registre: RegistreBorne
    cache: CacheVerdicts

    def juge(self, **config_juge: Any) -> JugeMistral:
        # Sans réessai : une erreur simulée est vue telle quelle (relances : tests/mistral).
        config_mistral = charger_mistral().model_copy(update={"reessais_max": 0})
        sdk = fabriquer_sdk(
            config_mistral,
            transport_interne=httpx2.MockTransport(self.faux),
            journal_requetes=JournalMemoire(),
            fichier_env=self.dossier / ".env",
        )
        client = ClientMistral(
            config_mistral,
            self.registre,
            sdk,
            dossier_journaux=self.dossier,
            dormir=lambda _: None,
        )
        config = charger_juges().second.model_copy(update=config_juge)
        return JugeMistral(config, client, self.cache, self.grille)

    def lignes_registre(self) -> list[dict[str, Any]]:
        with closing(sqlite3.connect(self.registre.chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            return [dict(r) for r in connexion.execute("SELECT * FROM reservations ORDER BY id")]

    def lignes_journal(self, nom: str) -> list[dict[str, Any]]:
        chemin = self.dossier / nom
        if not chemin.exists():
            return []
        with closing(sqlite3.connect(chemin)) as connexion:
            connexion.row_factory = sqlite3.Row
            return [dict(r) for r in connexion.execute("SELECT * FROM appels ORDER BY rowid")]


@pytest.fixture
def banc(tmp_path: Path, grille: Grille, doublures: SimpleNamespace) -> Banc:
    dossier = tmp_path / "banc"
    dossier.mkdir()
    (dossier / ".env").write_text("MISTRAL_API_KEY=cle-mistral-factice\n", encoding="utf-8")
    budgets = dossier / "budgets.toml"
    budgets.write_text(doublures.texte_budgets(), encoding="utf-8")
    tarifs = dossier / "tarifs.toml"
    tarifs.write_text(TARIFS, encoding="utf-8")
    registre = RegistreBorne(
        charger_budgets(budgets), charger_tarifs(tarifs), dossier / "budget.sqlite"
    )
    return Banc(
        dossier=dossier,
        faux=FauxMistral(doublures.verdict_conforme),
        grille=grille,
        doublures=doublures,
        registre=registre,
        cache=CacheVerdicts(dossier / "verdicts.sqlite"),
    )


def demandes(items: dict[str, Item], doublures: SimpleNamespace, *ids: str) -> list[Any]:
    return [DemandeJugement(items[i], doublures.sortie_factice()) for i in ids]


# --- Matrice ----------------------------------------------------------------------------------


def test_nominal(banc: Banc, items: dict[str, Item]) -> None:
    lot = demandes(items, banc.doublures, "Q-002", "CR-001")
    rapport = banc.juge().juger(lot, {"Q-002", "CR-001"})

    assert [r.item_id for r in rapport.resultats] == ["Q-002", "CR-001"]
    assert not rapport.budget_epuise
    for resultat, demande in zip(rapport.resultats, lot, strict=True):
        assert resultat.statut == "juge" and resultat.mode == "direct"
        assert not resultat.depuis_cache
        assert resultat.cout_eur == pytest.approx(COUT)
        assert resultat.tokens is not None and resultat.tokens.entree == USAGE[0]
        # verdict au schéma du Juge principal
        prompt = construire_prompt(demande.item, demande.sortie, banc.grille)
        assert resultat.verdict is not None
        attendu = valider_sortie(
            demande.item, json.dumps(banc.doublures.verdict_conforme(prompt.schema)), prompt.schema
        )
        assert resultat.verdict == attendu
        assert resultat.cle == cle_verdict(
            demande.item, demande.sortie, prompt, MODELE, "temperature-0+json_schema"
        )
    assert rapport.cout_total_eur == pytest.approx(2 * COUT)


def test_corps_envoye(banc: Banc, items: dict[str, Item]) -> None:
    lot = demandes(items, banc.doublures, "Q-002", "CR-001")
    banc.juge().juger(lot, {"Q-002", "CR-001"})
    assert len(banc.faux.requetes) == 2
    for corps, demande in zip(banc.faux.requetes, lot, strict=True):
        prompt = construire_prompt(demande.item, demande.sortie, banc.grille)
        assert corps["model"] == MODELE
        assert corps["temperature"] == 0
        assert corps["max_tokens"] == charger_juges().second.max_tokens
        assert corps["messages"] == [{"role": "user", "content": prompt.texte}]
        assert corps["response_format"] == {
            "type": "json_schema",
            "json_schema": {"name": "verdict", "schema": prompt.schema, "strict": True},
        }
        brut = json.dumps(corps, ensure_ascii=False)
        assert all(s not in brut for s in banc.doublures.SENTINELLES)  # même cécité


def test_session_unique_par_appel(banc: Banc, items: dict[str, Item]) -> None:
    banc.juge().juger(demandes(items, banc.doublures, "Q-002", "CR-001"), {"Q-002", "CR-001"})
    lignes = banc.lignes_journal("appels-mistral-juge.sqlite")
    assert len(lignes) == 2
    (session,) = {ligne["session_id"] for ligne in lignes}
    assert session.startswith("juge-second-") and len(session) == len("juge-second-") + 32


def test_imputation_et_journaux(banc: Banc, items: dict[str, Item]) -> None:
    banc.juge().juger(demandes(items, banc.doublures, "Q-002"), {"Q-002"})
    (reservation,) = banc.lignes_registre()
    assert (reservation["poste"], reservation["sous_poste"]) == ("mistral", "juge")
    assert reservation["etat"] == "regularisee"
    (ligne,) = banc.lignes_journal("appels-mistral-juge.sqlite")
    assert ligne["usage"] == "juge-second" and ligne["reservation_id"] == reservation["id"]
    assert banc.lignes_journal("appels-mistral.sqlite") == []


def test_hors_echantillon_ignore(banc: Banc, items: dict[str, Item]) -> None:
    lot = demandes(items, banc.doublures, "Q-001", "Q-002", "CO-001", "CR-001")
    rapport = banc.juge().juger(lot, ["CR-001", "Q-001", "NR-001"])
    assert [r.item_id for r in rapport.resultats] == ["Q-001", "CR-001"]  # ordre des demandes
    assert banc.faux.items() == ["Q-001", "CR-001"]


def test_cache_plein(banc: Banc, items: dict[str, Item]) -> None:
    lot = demandes(items, banc.doublures, "Q-002", "CR-001")
    premier = banc.juge().juger(lot, {"Q-002", "CR-001"})
    requetes, reservations = len(banc.faux.requetes), len(banc.lignes_registre())

    second = banc.juge().juger(lot, {"Q-002", "CR-001"})
    assert len(banc.faux.requetes) == requetes
    assert len(banc.lignes_registre()) == reservations
    for avant, apres in zip(premier.resultats, second.resultats, strict=True):
        assert apres.depuis_cache and apres.cout_eur == 0 and apres.statut == "juge"
        assert apres.verdict == avant.verdict
    assert second.cout_total_eur == 0


def test_cache_distinct_du_juge_principal(banc: Banc, items: dict[str, Item]) -> None:
    """La clé porte le modèle Mistral et `temperature-0` : aucun verdict Claude n'est repris."""
    demande = demandes(items, banc.doublures, "Q-002")[0]
    prompt = construire_prompt(demande.item, demande.sortie, banc.grille)
    cle_claude = cle_verdict(demande.item, demande.sortie, prompt, "claude-opus-5-5", "medium")
    (resultat,) = banc.juge().juger([demande], {"Q-002"}).resultats
    assert resultat.cle != cle_claude


def test_doublon_une_seule_requete(banc: Banc, items: dict[str, Item]) -> None:
    lot = demandes(items, banc.doublures, "Q-002", "Q-002")
    rapport = banc.juge().juger(lot, {"Q-002"})
    assert len(banc.faux.requetes) == 1
    assert [r.statut for r in rapport.resultats] == ["juge", "juge"]
    assert [r.cout_eur for r in rapport.resultats] == [pytest.approx(COUT), 0.0]


@pytest.mark.parametrize(
    "mauvaise",
    [
        {"texte": "pas du JSON"},
        {"texte": json.dumps({"id": "Q-002"})},  # hors schéma
        {"finish_reason": "length"},
    ],
)
def test_sortie_non_conforme_deux_fois(
    banc: Banc, items: dict[str, Item], mauvaise: dict[str, Any]
) -> None:
    banc.faux.reponses["Q-002"] = [dict(mauvaise), dict(mauvaise)]
    rapport = banc.juge().juger(demandes(items, banc.doublures, "Q-002"), {"Q-002"})
    (resultat,) = rapport.resultats
    assert resultat.statut == "invalide" and resultat.verdict is not None
    assert resultat.verdict.invalide
    assert len(banc.faux.requetes) == 2
    assert resultat.cout_eur == pytest.approx(2 * COUT)
    en_cache = banc.cache.lire(resultat.cle)
    assert en_cache is not None and en_cache.verdict.invalide
    assert en_cache.cout_eur == pytest.approx(2 * COUT)
    issues = [a["issue"] for a in banc.cache.appels()]
    assert issues == ["non-conforme", "invalide"]


def test_sortie_non_conforme_puis_conforme(banc: Banc, items: dict[str, Item]) -> None:
    banc.faux.reponses["Q-002"] = [{"texte": "pas du JSON"}]
    (resultat,) = banc.juge().juger(demandes(items, banc.doublures, "Q-002"), {"Q-002"}).resultats
    assert resultat.statut == "juge" and len(banc.faux.requetes) == 2
    assert resultat.cout_eur == pytest.approx(2 * COUT)


def test_budget_epuise_en_cours(banc: Banc, items: dict[str, Item]) -> None:
    banc.registre.epuise_a = 2
    lot = demandes(items, banc.doublures, "Q-001", "Q-002", "CR-001")
    rapport = banc.juge().juger(lot, {"Q-001", "Q-002", "CR-001"})
    assert rapport.budget_epuise
    assert [(r.statut, r.motif) for r in rapport.resultats] == [
        ("juge", None),
        ("non-juge", "budget"),
        ("non-juge", "budget"),
    ]
    assert banc.faux.items() == ["Q-001"]


def test_budget_epuise_reel_au_sous_poste(banc: Banc, items: dict[str, Item]) -> None:
    """Plafond `mistral.juge` réel trop bas : aucune requête, items non rejugés."""
    budgets = banc.dossier / "budgets-bas.toml"
    budgets.write_text(
        banc.doublures.texte_budgets().replace("juge = 5.0", "juge = 0.001"), encoding="utf-8"
    )
    banc.registre = RegistreBorne(
        charger_budgets(budgets), banc.registre.tarifs, banc.dossier / "budget-bas.sqlite"
    )
    rapport = banc.juge().juger(demandes(items, banc.doublures, "Q-002"), {"Q-002"})
    assert rapport.budget_epuise and rapport.resultats[0].motif == "budget"
    assert banc.faux.requetes == []


def test_erreur_serveur_puis_item_suivant(banc: Banc, items: dict[str, Item]) -> None:
    banc.faux.reponses["Q-001"] = [500]
    rapport = banc.juge().juger(
        demandes(items, banc.doublures, "Q-001", "Q-002"), {"Q-001", "Q-002"}
    )
    premier, second = rapport.resultats
    assert (premier.statut, premier.motif) == ("non-juge", "erreur-api")
    assert premier.cout_eur == 0  # 5xx non facturée : réglée à 0
    assert second.statut == "juge"
    assert banc.faux.items() == ["Q-001", "Q-002"]  # aucune relance
    pire = banc.lignes_registre()[0]
    assert pire["etat"] == "regularisee"
    assert premier.cout_eur == pytest.approx(pire["montant_reel_eur"])
    (appel,) = [a for a in banc.cache.appels() if a["item_id"] == "Q-001"]
    assert appel["issue"] == "erreur-api" and appel["tokens_entree"] is None
    assert appel["tokens_sortie"] is None
    assert appel["cout_eur"] == pytest.approx(pire["montant_reel_eur"])
    assert banc.cache.lire(premier.cle) is None


@pytest.mark.parametrize("statut", [401, 403])
def test_refus_d_authentification_arrete_tout(
    banc: Banc, items: dict[str, Item], statut: int
) -> None:
    banc.faux.reponses["Q-001"] = [statut]
    rapport = banc.juge().juger(
        demandes(items, banc.doublures, "Q-001", "Q-002"), {"Q-001", "Q-002"}
    )
    assert [(r.statut, r.motif) for r in rapport.resultats] == [
        ("non-juge", "erreur-api"),
        ("non-juge", "erreur-api"),
    ]
    assert banc.faux.items() == ["Q-001"]
    assert rapport.resultats[0].cout_eur == 0
    assert banc.lignes_registre()[0]["montant_reel_eur"] == 0
    (appel,) = banc.cache.appels()
    assert appel["issue"] == "erreur-api" and appel["cout_eur"] == 0
    assert (appel["tokens_entree"], appel["tokens_sortie"]) == (0, 0)


def test_limite_de_debit_arrete_tout(banc: Banc, items: dict[str, Item]) -> None:
    banc.faux.reponses["Q-001"] = [429]
    rapport = banc.juge().juger(
        demandes(items, banc.doublures, "Q-001", "Q-002"), {"Q-001", "Q-002"}
    )
    assert [(r.statut, r.motif) for r in rapport.resultats] == [
        ("non-juge", "limite-debit"),
        ("non-juge", "limite-debit"),
    ]
    assert banc.faux.items() == ["Q-001"]  # aucune relance, aucun appel suivant
    assert banc.lignes_registre()[0]["montant_reel_eur"] == 0


def test_refus_400_item_suivant_juge(banc: Banc, items: dict[str, Item]) -> None:
    banc.faux.reponses["Q-001"] = [400]
    rapport = banc.juge().juger(
        demandes(items, banc.doublures, "Q-001", "Q-002"), {"Q-001", "Q-002"}
    )
    assert [r.statut for r in rapport.resultats] == ["non-juge", "juge"]
    (appel,) = [a for a in banc.cache.appels() if a["item_id"] == "Q-001"]
    assert appel["issue"] == "erreur-api" and appel["cout_eur"] == 0
    assert (appel["tokens_entree"], appel["tokens_sortie"]) == (0, 0)


def test_cout_cumule_non_conforme_erreur_puis_juge(banc: Banc, items: dict[str, Item]) -> None:
    """Non conforme puis 500 au premier run, jugé au second : le coût en cache est la somme
    des tentatives journalisées."""
    banc.faux.reponses["Q-002"] = [{"texte": "{"}, 500]
    (premier,) = banc.juge().juger(demandes(items, banc.doublures, "Q-002"), {"Q-002"}).resultats
    assert (premier.statut, premier.motif) == ("non-juge", "erreur-api")
    (second,) = banc.juge().juger(demandes(items, banc.doublures, "Q-002"), {"Q-002"}).resultats
    assert second.statut == "juge" and second.cle == premier.cle
    appels = [a for a in banc.cache.appels() if a["cle"] == second.cle]
    assert [a["issue"] for a in appels] == ["non-conforme", "erreur-api", "juge"]
    en_cache = banc.cache.lire(second.cle)
    assert en_cache is not None
    assert en_cache.cout_eur == pytest.approx(sum(a["cout_eur"] for a in appels))
    assert en_cache.usage.entree == 2 * USAGE[0] and en_cache.usage.sortie == 2 * USAGE[1]


def test_item_co_non_jugeable(banc: Banc, items: dict[str, Item]) -> None:
    with pytest.raises(ItemNonJugeable):
        banc.juge().juger(demandes(items, banc.doublures, "Q-001", "CO-001"), {"Q-001", "CO-001"})
    assert banc.faux.requetes == []
    assert banc.lignes_registre() == []


def test_modele_resolu_refuse_remonte(banc: Banc, items: dict[str, Item]) -> None:
    banc.faux.reponses["Q-002"] = [{"model": "labs-mistral-large"}]
    with pytest.raises(ModeleMistralRefuse):
        banc.juge().juger(demandes(items, banc.doublures, "Q-002"), {"Q-002"})
    (ligne,) = banc.lignes_journal("appels-mistral-juge.sqlite")
    assert ligne["statut"] == "modele-refuse"


def test_modeles_incoherents_refuses(banc: Banc) -> None:
    with pytest.raises(ConfigurationInvalide):
        banc.juge(modele="mistral-large-2411")


def test_format_json_object(banc: Banc, items: dict[str, Item]) -> None:
    demande = demandes(items, banc.doublures, "Q-002")[0]
    prompt = construire_prompt(demande.item, demande.sortie, banc.grille)
    texte = json.dumps(banc.doublures.verdict_conforme(prompt.schema))
    banc.faux.reponses[SANS_SCHEMA] = [{"texte": texte}]
    (resultat,) = banc.juge(format_reponse="json_object").juger([demande], {"Q-002"}).resultats
    assert resultat.statut == "juge"
    assert banc.faux.requetes[0]["response_format"] == {"type": "json_object"}


def test_format_dans_la_cle_du_cache(banc: Banc, items: dict[str, Item]) -> None:
    """Un verdict obtenu en `json_schema` n'est pas repris en `json_object` (et inversement)."""
    demande = demandes(items, banc.doublures, "Q-002")[0]
    (schema,) = banc.juge().juger([demande], {"Q-002"}).resultats
    prompt = construire_prompt(demande.item, demande.sortie, banc.grille)
    texte = json.dumps(banc.doublures.verdict_conforme(prompt.schema))
    banc.faux.reponses[SANS_SCHEMA] = [{"texte": texte}]
    juge_objet = banc.juge(format_reponse="json_object")
    (objet,) = juge_objet.juger([demande], {"Q-002"}).resultats
    assert schema.cle != objet.cle
    assert not objet.depuis_cache and len(banc.faux.requetes) == 2
    assert banc.cache.lire(objet.cle) is not None


@pytest.mark.parametrize(
    ("cle", "valeur"),
    [
        ("usage_budget", '"validation"'),
        ("usage_budget", '"generation"'),
        ("temperature", "0.5"),
        ("format_reponse", '"texte"'),
    ],
)
def test_config_second_juge_refusee(tmp_path: Path, cle: str, valeur: str) -> None:
    source = Path(__file__).resolve().parents[2] / "config" / "juges.toml"
    lignes = source.read_text(encoding="utf-8").splitlines()
    debut = lignes.index("[second]")
    remplacees = [
        f"{cle} = {valeur}" if rang > debut and ligne.startswith(f"{cle} =") else ligne
        for rang, ligne in enumerate(lignes)
    ]
    assert remplacees != lignes
    chemin = tmp_path / "juges.toml"
    chemin.write_text("\n".join(remplacees) + "\n", encoding="utf-8")
    with pytest.raises(ConfigurationInvalide):
        charger_juges(chemin)


def test_config_second_juge() -> None:
    second = charger_juges().second
    assert second.modele == MODELE
    assert second.temperature == 0
    assert second.max_tokens > 0
    assert second.usage_budget == "juge-second"
    assert second.effort_cache == "temperature-0"
    assert second.format_reponse == "json_schema"
    assert second.effort_cle == "temperature-0+json_schema"
