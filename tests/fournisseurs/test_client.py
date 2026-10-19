"""Client compatible OpenAI (OpenRouter) : budget, journal, relances, vérification, réseau.

Faux serveur `httpx2.MockTransport` derrière la garde réseau ; aucun appel réel.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import httpx2  # noqa: TID251 (tests : transport factice)
import pytest

from slmsp.core.artefacts import chemin_autorise
from slmsp.core.erreurs import BudgetEpuise, LectureInterdite, SecretManquant
from slmsp.fournisseurs.client import (
    OPENROUTER,
    ErreurApiFournisseur,
    retenu,
    verifier,
)
from slmsp.fournisseurs.journal import NOM_JOURNAL_JUGES_TIERS
from slmsp.net.config import charger_config_reseau, charger_liste_blanche
from slmsp.net.journal import JournalMemoire
from slmsp.net.profils import evaluer


def _factices() -> ModuleType:
    nom = "openrouter_factices"
    if nom not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            nom, Path(__file__).with_name("factices_openrouter.py")
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[nom] = module
        spec.loader.exec_module(module)
    return sys.modules[nom]


F = _factices()
MESSAGES = [{"role": "user", "content": "<prompt-factice>"}]


@pytest.fixture
def banc(tmp_path: Path) -> Any:
    return F.banc(tmp_path / "banc")


def appeler(client: Any, **options: Any) -> Any:
    return client.appeler(
        "juge-tiers-openrouter",
        "session-test",
        MESSAGES,
        modele=F.MODELE,
        max_tokens=500,
        tokens_entree_estimes=1000,
        **options,
    )


def test_nominal_budget_et_journal(banc: Any) -> None:
    banc.faux.reponses.append({"cost": 0.0042})
    reponse = appeler(banc.client(), parametres={"temperature": 0.0})

    assert reponse.texte == "<réponse-factice-1>"
    assert reponse.usage.entree == 1000 and reponse.usage.sortie == 200
    assert reponse.cout_eur == pytest.approx(F.COUT)
    assert reponse.cout_fournisseur_usd == pytest.approx(0.0042)
    (requete,) = banc.faux.requetes
    assert str(requete.url) == "https://openrouter.ai/api/v1/chat/completions"
    assert requete.headers["Authorization"] == f"Bearer {F.CLE_FACTICE}"
    corps = json.loads(requete.content)
    assert corps == {
        "model": F.MODELE,
        "messages": MESSAGES,
        "max_tokens": 500,
        "temperature": 0.0,
    }
    (reservation,) = banc.reservations()
    assert reservation["poste"] == "openrouter"
    assert reservation["montant_reel_eur"] == pytest.approx(F.COUT)
    (ligne,) = banc.journal.appels()
    assert ligne["statut"] == "ok" and ligne["cout_fournisseur_usd"] == pytest.approx(0.0042)
    assert ligne["fournisseur"] == "openrouter" and ligne["modele_resolu"] == F.MODELE
    assert F.CLE_FACTICE not in json.dumps(ligne, default=str)  # la clé n'est jamais journalisée


def test_cout_fournisseur_absent(banc: Any) -> None:
    assert appeler(banc.client()).cout_fournisseur_usd is None


def test_relance_sur_429_puis_succes(banc: Any) -> None:
    banc.faux.reponses.extend([429, {}])
    reponse = appeler(banc.client(reessais_max=2))

    assert reponse.texte == "<réponse-factice-1>"
    premiere, seconde = banc.reservations()
    assert premiere["montant_reel_eur"] == 0  # réponse d'erreur HTTP : non facturée
    assert seconde["montant_reel_eur"] == pytest.approx(F.COUT)
    assert [ligne["statut_http"] for ligne in banc.journal.appels()] == [429, 200]


def test_refus_400_regle_a_zero(banc: Any) -> None:
    banc.faux.reponses.append(400)
    with pytest.raises(ErreurApiFournisseur) as exc:
        appeler(banc.client(reessais_max=3))
    assert exc.value.statut_http == 400 and exc.value.cout_eur == 0
    assert len(banc.faux.requetes) == 1  # pas de relance d'un refus
    (reservation,) = banc.reservations()
    assert reservation["montant_reel_eur"] == 0


def test_reponse_illisible_au_pire_cas(banc: Any) -> None:
    client = banc.client()
    client.http = F.fabriquer_http(
        F.OPENROUTER,
        transport_interne=httpx2.MockTransport(lambda r: httpx2.Response(200, content=b"<html>")),
        journal_requetes=JournalMemoire(),
    )
    with pytest.raises(ErreurApiFournisseur):
        appeler(client)
    (reservation,) = banc.reservations()
    assert reservation["montant_reel_eur"] == pytest.approx(reservation["montant_reserve_eur"])


def test_secret_absent_avant_toute_reservation(banc: Any) -> None:
    with pytest.raises(SecretManquant) as exc:
        appeler(banc.client(avec_cle=False))
    assert "OPENROUTER_API_KEY" in str(exc.value)
    assert banc.reservations() == [] and banc.faux.requetes == []


def test_lire_cle_absente_message_sans_valeur(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text("AUTRE_CLE=valeur-secrete-factice\n", encoding="utf-8")
    with pytest.raises(SecretManquant) as exc:
        F.lire_cle(OPENROUTER, env)
    assert "valeur-secrete-factice" not in str(exc.value)


def test_budget_epuise_rien_n_est_envoye(tmp_path: Path) -> None:
    banc = F.banc(tmp_path / "petit", plafond=0.0001)
    with pytest.raises(BudgetEpuise):
        appeler(banc.client())
    assert banc.faux.requetes == [] and banc.reservations() == []


def test_parametres_reserves_refuses(banc: Any) -> None:
    with pytest.raises(ValueError, match="réservés"):
        appeler(banc.client(), parametres={"model": "autre"})


def test_usage_generateur_impute_au_meme_poste(banc: Any) -> None:
    banc.client().appeler(
        "generateur-openrouter",
        "s",
        MESSAGES,
        modele=F.MODELE,
        max_tokens=10,
        tokens_entree_estimes=10,
    )
    assert banc.reservations()[0]["poste"] == "openrouter"


# --- Vérification sans dépense -------------------------------------------------------------------


MODELES = [
    {
        "id": "deepseek/deepseek-factice",
        "pricing": {"prompt": "0.0000005", "completion": "0.000002"},
    },
    {"id": "openai/gpt-factice", "pricing": {}},
    {"id": "google/gemini-factice", "pricing": {}},
    {"id": "z-ai/glm-factice", "pricing": {}},
    {"id": "thudm/zhipu-factice", "pricing": {}},
    {"id": "moonshotai/kimi-factice", "context_length": 128000},
]


def test_verifier_sans_cle(tmp_path: Path) -> None:
    faux = F.FauxOpenRouter(modeles=MODELES)
    env = tmp_path / ".env"
    env.write_text("", encoding="utf-8")
    bilan = verifier(
        OPENROUTER,
        fichier_env=env,
        transport_interne=httpx2.MockTransport(faux),
        journal_requetes=JournalMemoire(),
    )
    assert not bilan.cle_presente and bilan.erreur is None
    assert [m["id"] for m in bilan.modeles] == [
        "deepseek/deepseek-factice",
        "moonshotai/kimi-factice",
        "thudm/zhipu-factice",
        "z-ai/glm-factice",
    ]
    assert bilan.modeles[0]["entree_usd_mtok"] == pytest.approx(0.5)
    assert bilan.modeles[0]["sortie_usd_mtok"] == pytest.approx(2.0)
    (requete,) = faux.requetes
    assert requete.method == "GET" and "Authorization" not in requete.headers


def test_verifier_avec_cle_et_erreur(tmp_path: Path) -> None:
    env = tmp_path / ".env"
    env.write_text(f"OPENROUTER_API_KEY={F.CLE_FACTICE}\n", encoding="utf-8")
    bilan = verifier(
        OPENROUTER,
        fichier_env=env,
        transport_interne=httpx2.MockTransport(lambda r: httpx2.Response(503)),
        journal_requetes=JournalMemoire(),
    )
    assert bilan.cle_presente and "503" in (bilan.erreur or "")
    assert F.CLE_FACTICE not in bilan.erreur


def test_familles_retenues() -> None:
    assert retenu("mistralai/x") and retenu("xiaomi/x") and not retenu("openai/x")
    assert not retenu("google/x")


# --- Réseau et accès -----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("methode", "url", "permis"),
    [
        ("POST", "https://openrouter.ai/api/v1/chat/completions", True),
        ("GET", "https://openrouter.ai/api/v1/models", True),
        ("POST", "https://openrouter.ai/api/v1/autre", False),
        ("POST", "https://api.openai.com/v1/chat/completions", False),
        ("POST", "https://generativelanguage.googleapis.com/v1beta/openai/chat", False),
    ],
)
def test_profil_outillage(methode: str, url: str, permis: bool) -> None:
    verdict = evaluer(
        "outillage",
        methode,
        url,
        mode=None,
        config=charger_config_reseau(),
        liste_blanche=charger_liste_blanche(),
    )
    assert verdict.autorise is permis


def test_profil_assistant_inchange() -> None:
    liste = charger_liste_blanche()
    assert "openrouter.ai" not in liste.hotes
    verdict = evaluer(
        "assistant",
        "POST",
        "https://openrouter.ai/api/v1/chat/completions",
        mode="connecte",
        config=charger_config_reseau(),
        liste_blanche=liste,
    )
    assert verdict.statut is not None and "Liste blanche" in (verdict.motif or "")


@pytest.mark.parametrize("lecteur", ["data", "train"])
def test_journal_des_juges_tiers_illisible(
    lecteur: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SLMSP_VAR_DIR", str(tmp_path))
    with pytest.raises(LectureInterdite):
        chemin_autorise(tmp_path / NOM_JOURNAL_JUGES_TIERS, lecteur)


def test_liste_des_modeles_data_nulle(tmp_path: Path) -> None:
    bilan = verifier(
        OPENROUTER,
        fichier_env=tmp_path / ".env",
        transport_interne=httpx2.MockTransport(lambda r: httpx2.Response(200, json={"data": None})),
        journal_requetes=JournalMemoire(),
    )
    assert bilan.erreur is not None and "illisible" in bilan.erreur


def test_corps_illisible_reservation_reglee(banc: Any) -> None:
    class Reponse:
        status_code = 200
        headers: dict[str, str] = {}

        @property
        def content(self) -> bytes:
            raise OSError("<lecture-factice>")

    class Http:
        def post(self, *args: Any, **kwargs: Any) -> Reponse:
            return Reponse()

    client = banc.client()
    client.http = Http()
    with pytest.raises(ErreurApiFournisseur):
        appeler(client)
    (reservation,) = banc.reservations()
    assert reservation["etat"] != "RESERVEE"
    assert reservation["montant_reel_eur"] == pytest.approx(reservation["montant_reserve_eur"])
