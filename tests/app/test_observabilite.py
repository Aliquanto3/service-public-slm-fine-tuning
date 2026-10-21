"""Story 17.6 : observabilité de l'application (stockage, coût, impact, plafond, pont, CSV).

Aucun réseau : transports factices ; textes factices seulement (D1).
"""

from __future__ import annotations

import csv
import io
import json
import threading
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from pydantic import SecretStr

from slmsp.app.modele_externe import Observabilite, valider_reglage
from slmsp.app.modele_externe import tester_connexion as connexion_testee
from slmsp.app.observabilite import (
    CompteurDepense,
    ObservateurApplication,
    agreger,
    cellule_sure,
    charger_impacts,
    details_echange,
    energie_gpu_par_token,
    exporter_csv,
    impact_externe,
    impact_local,
    latence_par_token,
    nombre_gpu,
    resolveur_tarifs,
    tarif_config,
)
from slmsp.app.pont import Pont
from slmsp.app.pont.conversation import Conversation
from slmsp.app.pont.observabilite import PontObservabilite
from slmsp.app.pont.reglages import PontReglages
from slmsp.app.stockage import COLONNES_MESURE, Stockage
from slmsp.budget.config import charger_tarifs
from slmsp.core.evenements import Fin, Jeton
from slmsp.inference.mesures import MesureAppel, Tarif, contexte_mesure, notifier
from slmsp.net.client import Passerelle
from slmsp.net.config import avec_modele_externe, charger_config_reseau, charger_liste_blanche
from slmsp.net.journal import JournalMemoire


class Horloge:
    def __init__(self, instant: datetime) -> None:
        self.instant = instant

    def __call__(self) -> datetime:
        return self.instant


@pytest.fixture
def horloge() -> Horloge:
    return Horloge(datetime(2026, 10, 31, 23, 0, tzinfo=UTC))


@pytest.fixture
def stockage(tmp_path: Path, horloge: Horloge) -> Stockage:
    return Stockage(tmp_path / "assistant.sqlite", horloge=horloge)


def mesure(**champs: Any) -> MesureAppel:
    valeurs: dict[str, Any] = {
        "fournisseur": "ovh",
        "hote": "oai.endpoints.kepler.ai.cloud.ovh.net",
        "modele": "Qwen3.6-27B",
        "tokens_entree": 100,
        "tokens_sortie": 50,
        "estime": False,
        "interrompu": False,
        "duree_ms": 2000,
        "premier_token_ms": 300,
        "cout_eur": 0.001,
    }
    valeurs.update(champs)
    return MesureAppel(**valeurs)


def test_energie_gpu_ecologits_pour_27_milliards() -> None:
    """f_E d'EcoLogits (relevé du 2026-10-21) : 1,17e-6 × exp(-1,12e-2 × 64) × 27 + 4,05e-5."""
    g = charger_impacts().gpu
    assert energie_gpu_par_token(g, 27) == pytest.approx(5.5926e-5, rel=1e-4)
    assert latence_par_token(g, 27) == pytest.approx(0.057674, rel=1e-6)
    assert [nombre_gpu(g, p) for p in (24, 27, 70, 119, 400)] == [1, 1, 4, 4, 16]


def test_impacts_valeurs_calculees_a_la_main() -> None:
    impacts = charger_impacts()
    # Qwen3.6-27B (dense 27 Md, 1 GPU : 1,2 × 27 × 2 = 64,8 Go), OpenRouter (USA, PUE 1,2),
    # 300 tokens de sortie, 3 s mesurées :
    # E_gpu = 300 × 5,59258e-5 = 0,0167777 Wh ; hors GPU = 3 / 3600 × 1200 × 1/8 / 64
    # = 0,00195313 Wh ; E = 1,2 × (0,00195313 + 0,0167777) = 0,0224770 Wh ;
    # CO2e = 0,0224770 / 1000 × 369 = 0,00829403 g.
    i = impact_externe(impacts, "openrouter", "qwen/qwen3.6-27b", 300, 3000)
    assert i is not None
    assert i.energie_wh == pytest.approx(0.0224770, rel=1e-5)
    assert i.co2e_g == pytest.approx(0.00829403, rel=1e-5)
    # Bas : PUE 1,1, 3 s ; haut : PUE 1,4, latence modélisée 300 × 0,057674 = 17,30 s.
    assert i.energie_wh_bas == pytest.approx(0.0206039, rel=1e-5)
    assert i.energie_wh_haut == pytest.approx(0.0392591, rel=1e-5)
    assert impact_externe(impacts, "ovh", "<modele-inconnu>", 100, 5000) is None
    # Mistral Small 4 : 119 Md au total (4 GPU), actifs inconnus 6 à 24 Md (centre 15),
    # API Mistral (FRA, PUE 1,16) : la fourchette porte l'incertitude des paramètres actifs.
    m = impact_externe(impacts, "mistral", "mistral-small-latest", 300, 3000)
    assert m is not None
    assert m.energie_wh == pytest.approx(0.0773678, rel=1e-5)
    assert m.energie_wh_bas == pytest.approx(0.0665786, rel=1e-5)
    assert m.energie_wh_haut == pytest.approx(0.151932, rel=1e-5)
    assert m.co2e_g == pytest.approx(0.0773678 / 1000 * 52, rel=1e-5)
    # Local : 25 W × 10 s = 0,069444 Wh, mix France.
    local = impact_local(impacts, 25, 10_000)
    assert local is not None and local.energie_wh == pytest.approx(25 * 10 / 3600)
    assert local.energie_wh_bas == pytest.approx(local.energie_wh * 0.5)


def test_tarifs_une_seule_source() -> None:
    tarifs = charger_tarifs()
    assert tarif_config(tarifs, "Qwen3.6-27B") == Tarif(0.40, 2.70)
    assert tarif_config(tarifs, "mistral-small-latest") == Tarif(0.15, 0.6)
    assert tarif_config(tarifs, "<modele-inconnu>") is None
    resoudre = resolveur_tarifs(tarifs)
    assert resoudre({"preset": "openrouter", "modele": "qwen/qwen3.6-27b"}) == Tarif(0.25, 2.0)
    generique = {"preset": "generique", "modele": "Qwen3.6-27B", "tarif": None}
    assert resoudre(generique) is None  # tarif obligatoire pour le preset generique
    assert resoudre({**generique, "tarif": {"entree": 1.0, "sortie": 3.0}}) == Tarif(1.0, 3.0)


def test_stockage_sans_contenu_et_observateur(stockage: Stockage) -> None:
    assert not {"question", "reponse", "messages", "contenu", "cle", "texte"} & set(COLONNES_MESURE)
    obs = ObservateurApplication(stockage, charger_impacts())
    obs.mesurer(mesure(echange="<e1>", tache="Q"))
    obs.mesurer(mesure(fournisseur="local", hote=None, modele="<slug>", cout_eur=0.0))
    obs.mesurer(mesure(motif="plafond-atteint", tokens_entree=0, tokens_sortie=0, cout_eur=0.0))
    lignes = stockage.lister_mesures()
    assert len(lignes) == 3 and lignes[-1]["echange"] == "<e1>"
    assert lignes[1]["energie_wh"] == pytest.approx(25 * 2 / 3600)  # local, 25 W par défaut
    assert lignes[0]["energie_wh"] is None  # saut : aucun impact
    stockage.ecrire_reglage("puissance_cpu_w", 50)
    assert obs.puissance_cpu() == 50
    with pytest.raises(KeyError):
        stockage.inscrire_mesure({"question": "<texte-factice>"})


def test_plafond_cumul_par_hote_mois_utc_et_jamais_efface(
    stockage: Stockage, horloge: Horloge
) -> None:
    compteur = CompteurDepense(stockage)
    hote = "api.mistral.ai"
    jeton = compteur.reserver(hote, "m1", 1.5)
    assert jeton is not None
    assert compteur.reserver(hote, "m2", 0.6) is None  # 1,5 + 0,6 > 2 € (défaut)
    compteur.regulariser(jeton, 0.1)
    assert stockage.cumuls_depense("2026-10") == {hote: pytest.approx(0.1)}
    assert compteur.reserver(hote, "m2", 0.6) is not None  # même hôte, autre modèle
    stockage.effacer_historique()
    assert stockage.cumuls_depense("2026-10")[hote] == pytest.approx(0.7)
    # Plafond lu à chaque appel ; 0 = fournisseur désactivé.
    stockage.ecrire_reglage("plafonds_depense", {hote: 0})
    assert compteur.reserver(hote, "m1", 0.0001) is None
    stockage.ecrire_reglage("plafonds_depense", {hote: 5})
    assert compteur.reserver(hote, "m1", 3.0) is not None
    # Changement de mois (UTC) : nouveau cumul.
    horloge.instant = datetime(2026, 11, 1, 0, 30, tzinfo=UTC)
    assert compteur.reserver(hote, "m1", 4.9) is not None
    assert stockage.cumuls_depense("2026-11") == {hote: pytest.approx(4.9)}


def test_plafond_concurrent_sous_verrou(stockage: Stockage) -> None:
    compteur = CompteurDepense(stockage)
    resultats: list[Any] = []

    def reserver() -> None:
        resultats.append(compteur.reserver("h", "m", 0.5))

    fils = [threading.Thread(target=reserver) for _ in range(8)]
    for f in fils:
        f.start()
    for f in fils:
        f.join()
    assert sum(r is not None for r in resultats) == 4  # 4 × 0,5 € = 2 €


def test_agregats_et_details() -> None:
    lignes = [
        {**mesure(cout_eur=0.001).__dict__, "energie_wh": 0.5},
        {**mesure(cout_eur=None, estime=True).__dict__, "energie_wh": 0.25},
        {**mesure(motif="plafond-atteint", cout_eur=0.0).__dict__, "energie_wh": None},
    ]
    (ligne,) = agreger(lignes)
    assert (ligne["appels"], ligne["sauts"], ligne["tokens_entree"]) == (2, 1, 200)
    assert ligne["cout_eur"] is None and ligne["estime"]  # un coût inconnu : total inconnu
    assert ligne["energie_wh"] == pytest.approx(0.75)
    assert ligne["debit_tokens_s"] == pytest.approx(100 / 4)
    local = details_echange([{**mesure(fournisseur="local", cout_eur=0.0).__dict__}])
    assert local is not None and local["local"] and local["cout_eur"] == 0.0
    assert "pas de coût d'API" in local["mention_cout"]
    assert details_echange([]) is None
    # Story 17.4b : accès gratuit OVH, 0 € mentionné ; un saut `debit-limite` n'est pas un appel
    gratuit = details_echange(
        [
            {**mesure(fournisseur="ovh-gratuit", cout_eur=0.0).__dict__},
            {**mesure(fournisseur="ovh-gratuit", cout_eur=0.0, motif="debit-limite").__dict__},
        ]
    )
    assert gratuit is not None and gratuit["cout_eur"] == 0.0 and not gratuit["local"]
    assert gratuit["mention_cout"] == "accès gratuit OVH" and gratuit["sauts"] == 1


def test_export_csv_protege_et_sans_contenu() -> None:
    assert cellule_sure("=1+1") == "'=1+1" and cellule_sure("@x") == "'@x"
    assert cellule_sure("-a") == "'-a" and cellule_sure("+a") == "'+a"
    assert cellule_sure("\t=1") == "'\t=1" and cellule_sure("\r=1") == "'\r=1"
    assert cellule_sure("Qwen3.6-27B") == "Qwen3.6-27B" and cellule_sure(3) == 3
    texte = exporter_csv([{**mesure(modele="=HYPERLINK()").__dict__}], COLONNES_MESURE)
    lignes = list(csv.reader(io.StringIO(texte), delimiter=";"))
    assert lignes[0] == list(COLONNES_MESURE)
    assert lignes[1][COLONNES_MESURE.index("modele")] == "'=HYPERLINK()"


def test_pont_observabilite(stockage: Stockage, tmp_path: Path) -> None:
    fournisseurs = [{"hote": "api.mistral.ai", "libelle": "mistral/mistral-small-latest"}]
    obs = ObservateurApplication(stockage, charger_impacts())
    cible = tmp_path / "export.csv"
    pont = PontObservabilite(
        stockage,
        Observabilite(observateur=obs),
        lambda nom: str(cible),
        fournisseurs=lambda: fournisseurs,
    )
    obs.mesurer(mesure(hote="api.mistral.ai", fournisseur="mistral"))
    r = pont.appeler("reglages")
    assert r["plafonds"][0]["plafond_eur"] == 2.0 and r["puissance_cpu_w"] == 25
    assert pont.appeler("ecrire_plafond", "api.mistral.ai", 3.5)["ok"]
    assert pont.appeler("ecrire_plafond", "<hote-inconnu>", 1)["ok"] is False
    assert pont.appeler("ecrire_plafond", "api.mistral.ai", -1)["ok"] is False
    assert pont.appeler("ecrire_puissance", 40)["ok"]
    assert pont.appeler("ecrire_puissance", True)["ok"] is False
    s = pont.appeler("synthese")["synthese"]
    assert s["mois"] == "2026-10" and s["totaux_mois"]["appels"] == 1
    assert s["plafonds"][0]["plafond_eur"] == 3.5
    assert s["derniers"][0]["modele"] == "Qwen3.6-27B"
    assert pont.appeler("methode")["methode"]["disponible"] is True
    assert pont.appeler("exporter_csv") == {"ok": True, "enregistre": True, "nom": "export.csv"}
    assert cible.read_text(encoding="utf-8-sig").startswith("horodatage;")
    assert pont.appeler("exporter_csv")["erreur"]["code"] == "fichier-existant"


class Service:
    """Service factice : chaque réponse fait deux appels mesurés (boucle d'outils)."""

    mode = None

    def __init__(self, obs: ObservateurApplication) -> None:
        self.obs = obs

    def repondre(self, tache: str, messages: Any, options: Any) -> Iterator[Any]:
        def flux() -> Iterator[Any]:
            notifier(self.obs, mesure(fournisseur="local", hote=None, cout_eur=0.0))
            notifier(self.obs, mesure(fournisseur="local", hote=None, cout_eur=0.0))
            yield Jeton(texte="<réponse-factice-1>")
            yield Fin(raison="terminee")

        return flux()


def test_conversation_details_sous_la_reponse(stockage: Stockage) -> None:
    obs = ObservateurApplication(stockage, charger_impacts())
    poussees: list[dict[str, Any]] = []
    conversation = Conversation(
        Service(obs),  # type: ignore[arg-type]
        lambda lot: poussees.extend(lot),
        modele_local="<slug>",
        details=PontObservabilite(stockage).details,
    )
    assert conversation.envoyer("Q", [{"role": "user", "content": "<q>"}])["ok"]
    conversation.attendre(5)
    fin = next(e for e in poussees if e["type"] == "fin")
    assert fin["details"]["appels"] == 2 and fin["details"]["local"] is True
    assert fin["details"]["tokens_sortie"] == 100 and fin["details"]["cout_eur"] == 0.0
    assert {m["tache"] for m in stockage.lister_mesures()} == {"Q"}


def test_pont_expose_le_domaine(stockage: Stockage) -> None:
    class Fenetre:
        def evaluate_js(self, script: str) -> None:
            pass

    pont = Pont(Service(ObservateurApplication(stockage, None)), Fenetre(), stockage=stockage)  # type: ignore[arg-type]
    assert pont.appeler("observabilite.synthese")["ok"]
    assert pont.appeler("observabilite.inconnue")["ok"] is False


def test_generique_actif_sans_tarif_refuse(stockage: Stockage) -> None:
    entree = {
        "id": "g1",
        "preset": "generique",
        "url_base": "https://h.example/v1",
        "modele": "<m>",
        "actif": True,
    }
    r = PontReglages(stockage).appeler("ecrire", "fournisseurs_externes", [entree])
    assert r["ok"] is False and "tarif" in r["erreur"]["message"]
    avec = {**entree, "tarif": {"entree": 1, "sortie": 2}, "usage_flux": True}
    r = PontReglages(stockage).appeler("ecrire", "fournisseurs_externes", [avec])
    assert r["ok"] and r["fournisseurs"][0]["tarif"] == {"entree": 1.0, "sortie": 2.0}
    with pytest.raises(ValueError):
        valider_reglage([{**avec, "preset": "mistral", "url_base": ""}])


def test_test_de_connexion_compte_et_refuse(stockage: Stockage) -> None:
    import httpx2  # noqa: TID251 (tests : transport factice)

    entree = valider_reglage([{"id": "b2", "preset": "mistral", "actif": True}])[0]
    appels: list[Any] = []

    def ok(requete: Any) -> Any:
        appels.append(requete)
        fin = {
            "choices": [{"index": 0, "delta": {}, "finish_reason": "length"}],
            "usage": {"prompt_tokens": 8, "completion_tokens": 1},
        }
        return httpx2.Response(200, content=f"data: {json.dumps(fin)}\n\ndata: [DONE]\n".encode())

    passerelle = Passerelle(
        type("Mode", (), {"mode_courant": lambda self: "connecte"})(),
        JournalMemoire(),
        config=avec_modele_externe(charger_config_reseau(), []),
        liste_blanche=charger_liste_blanche(),
    )
    suivi = Observabilite(
        observateur=ObservateurApplication(stockage, charger_impacts()),
        plafond=CompteurDepense(stockage),
        tarif=resolveur_tarifs(charger_tarifs()),
    )
    r = connexion_testee(
        entree,
        SecretStr("<cle-factice>"),
        passerelle,
        transport_interne=httpx2.MockTransport(ok),
        observabilite=suivi,
    )
    assert r["reussi"] is True
    (ligne,) = stockage.lister_mesures()
    assert ligne["tache"] == "test-connexion" and ligne["tokens_entree"] == 8
    assert stockage.cumuls_depense("2026-10")["api.mistral.ai"] > 0
    stockage.ecrire_reglage("plafonds_depense", {"api.mistral.ai": 0})
    with contexte_mesure(tache="<autre>"):
        r = connexion_testee(
            entree,
            SecretStr("<cle-factice>"),
            passerelle,
            transport_interne=httpx2.MockTransport(ok),
            observabilite=suivi,
        )
    assert r["motif"] == "plafond-atteint" and len(appels) == 1
