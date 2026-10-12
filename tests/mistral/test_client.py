"""`ClientMistral` : contrôles, réservation, appel unique, journal et modèle résolu.

Une ligne de la matrice « client » de la story 5.5 par test, sur le faux serveur Mistral
(`httpx2.MockTransport` derrière la garde réseau). Aucun appel réel.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx2  # noqa: TID251 (tests de l'adaptateur : transport factice)
import pytest

pytest.importorskip("mistralai")

from slmsp.budget.tarifs import UsageTokens  # noqa: E402
from slmsp.core.canonique import json_canonique, sha256_hex  # noqa: E402
from slmsp.core.erreurs import BudgetEpuise, SecretManquant  # noqa: E402
from slmsp.mistral.client import (  # noqa: E402
    ErreurApiMistral,
    ModeleMistralRefuse,
    ReponseMistral,
    UsageInterdit,
    fabriquer_sdk,
)

JOURNAL_JUGE = "appels-mistral-juge.sqlite"
JOURNAL_DONNEES = "appels-mistral.sqlite"
MESSAGES = [{"role": "user", "content": "<prompt-factice>"}]
FORMAT = {
    "type": "json_schema",
    "json_schema": {"name": "verdict", "schema": {"type": "object"}, "strict": True},
}
COUT_FACTICE = (1000 + 200) / 1_000_000  # tarifs de test : 1 $/M, taux 1


def appeler(client: Any, usage: str = "juge-second", **options: Any) -> ReponseMistral:
    valeurs: dict[str, Any] = {
        "max_tokens": 4000,
        "tokens_entree_estimes": 2000,
        "temperature": 0.0,
        "response_format": FORMAT,
    }
    return client.appeler(usage, "session-test", MESSAGES, **{**valeurs, **options})


def test_appel_nominal_juge_second(banc: Any, doublures: SimpleNamespace) -> None:
    client = banc.client()
    reponse = appeler(client)

    assert reponse.texte == "<verdict-factice>"
    assert reponse.modele_resolu == doublures.MODELE_RESOLU
    assert reponse.finish_reason == "stop"
    assert reponse.usage == UsageTokens(*doublures.USAGE_FACTICE)
    assert reponse.cout_eur == pytest.approx(COUT_FACTICE)

    (requete,) = banc.faux.requetes
    assert requete[:2] == ("POST", "/v1/chat/completions")
    (ligne,) = banc.lignes_journal(JOURNAL_JUGE)
    assert ligne["appel_id"] == reponse.appel_id
    assert ligne["usage"] == "juge-second" and ligne["session_id"] == "session-test"
    assert ligne["statut"] == "ok" and ligne["statut_http"] == 200
    assert ligne["modele_demande"] == doublures.MODELE
    assert ligne["modele_resolu"] == doublures.MODELE_RESOLU
    assert ligne["reponse_brute"] == banc.faux.servis[0]  # octet pour octet
    assert ligne["sha256_reponse"] == sha256_hex(banc.faux.servis[0])
    assert ligne["requete"] == json_canonique(json.loads(requete[2])).decode("utf-8")
    assert ligne["reservation_id"] == reponse.reservation_id
    assert banc.lignes_journal(JOURNAL_DONNEES) == []

    (reservation,) = banc.lignes_registre()
    assert reservation["id"] == reponse.reservation_id
    assert (reservation["poste"], reservation["sous_poste"]) == ("mistral", "juge")
    assert reservation["modele"] == doublures.MODELE and reservation["mode"] == "direct"
    assert reservation["etat"] == "regularisee"
    assert reservation["montant_reel_eur"] == pytest.approx(COUT_FACTICE)
    assert (reservation["tokens_entree"], reservation["tokens_sortie"]) == (1000, 200)


def test_corps_envoye(banc: Any, doublures: SimpleNamespace) -> None:
    appeler(banc.client())
    (corps,) = banc.faux.corps()
    assert corps["model"] == doublures.MODELE
    assert corps["temperature"] == 0
    assert corps["response_format"] == FORMAT
    assert corps["messages"] == MESSAGES
    assert corps["max_tokens"] == 4000


def test_validation_va_au_journal_des_donnees(banc: Any) -> None:
    reponse = appeler(banc.client(), "validation")
    (ligne,) = banc.lignes_journal(JOURNAL_DONNEES)
    assert ligne["appel_id"] == reponse.appel_id and ligne["usage"] == "validation"
    assert banc.lignes_journal(JOURNAL_JUGE) == []
    (reservation,) = banc.lignes_registre()
    assert (reservation["poste"], reservation["sous_poste"]) == ("mistral", "generation")


def test_cle_absente_du_journal(banc: Any, doublures: SimpleNamespace) -> None:
    appeler(banc.client())
    appeler(banc.client(), "validation")
    banc.faux.reponses.append(500)
    with pytest.raises(ErreurApiMistral):
        appeler(banc.client())
    cle = doublures.CLE_FACTICE.encode()
    for nom in (JOURNAL_JUGE, JOURNAL_DONNEES):
        for fichier in banc.dossier.glob(f"{nom}*"):
            assert cle not in fichier.read_bytes()
        for ligne in banc.lignes_journal(nom):
            assert all(cle not in str(valeur).encode() for valeur in ligne.values())


def _rien_n_est_parti(banc: Any) -> None:
    assert banc.faux.requetes == []
    assert banc.lignes_registre() == []
    assert banc.lignes_journal(JOURNAL_JUGE) == []
    assert banc.lignes_journal(JOURNAL_DONNEES) == []


def test_usage_generation_refuse(banc: Any) -> None:
    client = banc.client()
    with pytest.raises(UsageInterdit):
        appeler(client, "generation")
    _rien_n_est_parti(banc)


def test_jeton_de_generation_refuse(banc: Any) -> None:
    client = banc.client()
    with pytest.raises(UsageInterdit):
        client._appeler(
            "generation",
            "session-test",
            MESSAGES,
            max_tokens=10,
            tokens_entree_estimes=10,
            jeton=object(),
        )
    with pytest.raises(UsageInterdit):  # `None` ne vaut pas jeton, même sans Générateur
        client._appeler(
            "generation", "session-test", MESSAGES, max_tokens=10, tokens_entree_estimes=10
        )
    _rien_n_est_parti(banc)


def test_usage_inconnu_refuse(banc: Any) -> None:
    with pytest.raises(UsageInterdit):
        appeler(banc.client(), "juge-principal")
    _rien_n_est_parti(banc)


@pytest.mark.parametrize("modele", ["labs-x", "mistral-large-2512-preview", "mistral-small"])
def test_modele_demande_hors_liste(banc: Any, modele: str) -> None:
    config = banc.config.model_copy(update={"modele": modele})
    client = banc.client(config)
    with pytest.raises(ModeleMistralRefuse):
        appeler(client)
    _rien_n_est_parti(banc)


@pytest.mark.parametrize("modele_resolu", ["labs-mistral-large", "mistral-medium-2505"])
def test_modele_resolu_refuse(banc: Any, modele_resolu: str) -> None:
    banc.faux.modele_resolu = modele_resolu
    with pytest.raises(ModeleMistralRefuse):
        appeler(banc.client())
    assert len(banc.faux.requetes) == 1
    (ligne,) = banc.lignes_journal(JOURNAL_JUGE)
    assert ligne["statut"] == "modele-refuse" and ligne["modele_resolu"] == modele_resolu
    assert ligne["reponse_brute"] == banc.faux.servis[0]
    (reservation,) = banc.lignes_registre()
    assert reservation["etat"] == "regularisee"
    assert reservation["montant_reel_eur"] == pytest.approx(COUT_FACTICE)


def test_modele_resolu_autorise(banc: Any) -> None:
    banc.faux.modele_resolu = "mistral-large-2411"
    assert appeler(banc.client()).modele_resolu == "mistral-large-2411"


def test_budget_epuise(banc: Any) -> None:
    banc.plafond_juge = 0.001  # pire cas d'un appel : (2000 + 4000) / 1e6 = 0,006 €
    with pytest.raises(BudgetEpuise):
        appeler(banc.client())
    _rien_n_est_parti(banc)


@pytest.mark.parametrize("statut", [500, 502, 503])
def test_erreur_serveur_comptee_au_pire_cas(banc: Any, statut: int) -> None:
    banc.faux.reponses.append(statut)
    with pytest.raises(ErreurApiMistral) as erreur:
        appeler(banc.client())
    assert len(banc.faux.requetes) == 1  # aucune relance du SDK
    (ligne,) = banc.lignes_journal(JOURNAL_JUGE)
    assert ligne["statut"] == "erreur" and ligne["statut_http"] == statut
    assert ligne["reponse_brute"] == banc.faux.servis[0]
    (reservation,) = banc.lignes_registre()
    assert reservation["etat"] == "pire-cas"
    assert erreur.value.cout_eur == pytest.approx(reservation["montant_reserve_eur"])
    assert erreur.value.statut_http == statut


def test_erreur_reseau(banc: Any) -> None:
    banc.faux.reponses.append(httpx2.ConnectError("connexion refusée (factice)"))
    with pytest.raises(ErreurApiMistral) as erreur:
        appeler(banc.client())
    assert erreur.value.statut_http is None
    (ligne,) = banc.lignes_journal(JOURNAL_JUGE)
    assert ligne["statut"] == "erreur" and ligne["statut_http"] is None
    assert ligne["reponse_brute"] is None
    (reservation,) = banc.lignes_registre()
    assert reservation["etat"] == "pire-cas"
    assert reservation["id"] == ligne["reservation_id"]


@pytest.mark.parametrize("statut", [400, 401, 403, 422, 429])
def test_refus_4xx_non_facture(banc: Any, statut: int) -> None:
    banc.faux.reponses.append(statut)
    with pytest.raises(ErreurApiMistral) as erreur:
        appeler(banc.client())
    assert erreur.value.statut_http == statut and erreur.value.cout_eur == 0
    assert len(banc.faux.requetes) == 1
    (ligne,) = banc.lignes_journal(JOURNAL_JUGE)
    assert ligne["statut"] == "erreur" and ligne["statut_http"] == statut
    (reservation,) = banc.lignes_registre()
    assert reservation["etat"] == "regularisee" and reservation["montant_reel_eur"] == 0


def test_sdk_sans_relance_ni_url_externe(banc: Any) -> None:
    sdk = banc.sdk()
    assert sdk.sdk_configuration.retry_config is None
    assert sdk.sdk_configuration.server_url == "https://api.mistral.ai"
    assert sdk.sdk_configuration.timeout_ms == round(banc.config.delai_appel * 1000)


def test_sdk_sans_cle(banc: Any, tmp_path: Path) -> None:
    vide = tmp_path / "vide.env"
    vide.write_text("AUTRE=1\n", encoding="utf-8")
    with pytest.raises(SecretManquant) as erreur:
        fabriquer_sdk(banc.config, fichier_env=vide)
    assert "MISTRAL_API_KEY" in str(erreur.value)


def test_hote_refuse_par_la_garde(banc: Any) -> None:
    """Le SDK passe par la garde `outillage` : une requête refusée ne part pas, n'est pas
    facturée (réservation réglée à 0) et laisse une ligne `erreur`."""
    from slmsp.core.erreurs import HoteBloque

    sdk = banc.sdk()
    with pytest.raises(HoteBloque):
        sdk.sdk_configuration.client.get("https://api.mistral.ai/v1/models")
    assert banc.faux.requetes == []

    client = banc.client()
    client.sdk.sdk_configuration.server_url = "https://hote-inconnu.example"
    with pytest.raises(HoteBloque):
        appeler(client)
    assert banc.faux.requetes == []
    (ligne,) = banc.lignes_journal(JOURNAL_JUGE)
    assert ligne["statut"] == "erreur" and ligne["statut_http"] is None
    (reservation,) = banc.lignes_registre()
    assert reservation["etat"] == "regularisee" and reservation["montant_reel_eur"] == 0


def test_message_mal_forme_sans_reservation(banc: Any) -> None:
    client = banc.client()
    with pytest.raises(TypeError, match="not iterable"):  # `dict(42)` : message mal formé
        client.appeler("juge-second", "session-test", [42], max_tokens=10, tokens_entree_estimes=10)
    _rien_n_est_parti(banc)


def test_jeton_du_generateur_accepte(banc: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    """Avec un module `slmsp.mistral.generateur` (story 9.2), son `_JETON` ouvre `generation`."""
    jeton = object()
    module = types.ModuleType("slmsp.mistral.generateur")
    module._JETON = jeton  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "slmsp.mistral.generateur", module)
    client = banc.client()
    with pytest.raises(UsageInterdit):  # un autre objet ne vaut pas jeton
        client._appeler(
            "generation", "s", MESSAGES, max_tokens=10, tokens_entree_estimes=10, jeton=object()
        )
    reponse = client._appeler(
        "generation", "session-gen", MESSAGES, max_tokens=10, tokens_entree_estimes=10, jeton=jeton
    )
    (ligne,) = banc.lignes_journal(JOURNAL_DONNEES)
    assert ligne["appel_id"] == reponse.appel_id and ligne["usage"] == "generation"
    assert banc.lignes_journal(JOURNAL_JUGE) == []
    (reservation,) = banc.lignes_registre()
    assert (reservation["poste"], reservation["sous_poste"]) == ("mistral", "generation")


def test_import_du_generateur_en_echec_releve(banc: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    """Un `ModuleNotFoundError` sur un autre nom (dépendance du Générateur) est relevé."""
    from slmsp.mistral import client as module_client

    def importer(nom: str) -> Any:
        raise ModuleNotFoundError("No module named 'dependance_absente'", name="dependance_absente")

    monkeypatch.setattr(module_client.importlib, "import_module", importer)
    client = banc.client()
    with pytest.raises(ModuleNotFoundError) as erreur:
        client._appeler(
            "generation", "s", MESSAGES, max_tokens=10, tokens_entree_estimes=10, jeton=object()
        )
    assert erreur.value.name == "dependance_absente"
    _rien_n_est_parti(banc)


def test_import_du_paquet_sans_mistralai() -> None:
    import subprocess
    import sys

    code = "import sys, slmsp.mistral, slmsp.mistral.journal; print('mistralai' in sys.modules)"
    sortie = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    ).stdout
    assert sortie.strip() == "False"
