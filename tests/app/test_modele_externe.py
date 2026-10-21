"""Story 17.4 : fournisseurs externes (réglage, clés chiffrées par entrée, profil réseau, pont,
cascade au branchement) et traçabilité.

Aucun appel réel ; chiffreur factice (DPAPI réelle : un aller-retour local sous Windows).
Textes factices seulement (D1).
"""

from __future__ import annotations

import json
import sys
import threading
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import SecretStr

from slmsp.app.cle_externe import CoffreCle, CoffreCles
from slmsp.app.export_retours import construire_export
from slmsp.app.modele_externe import (
    MAX_FOURNISSEURS,
    brancher_hybride,
    lecteur_cles,
    lire_reglage,
    valider_reglage,
)
from slmsp.app.modele_externe import (
    tester_connexion as connexion_testee,
)
from slmsp.app.pont.conversation import Conversation
from slmsp.app.pont.historique import PontHistorique
from slmsp.app.pont.mode import PontMode
from slmsp.app.pont.reglages import PontReglages
from slmsp.app.pont.retours import PontRetours
from slmsp.app.stockage import Stockage
from slmsp.core.evenements import Fin, Jeton
from slmsp.net.client import Passerelle
from slmsp.net.config import avec_modele_externe, charger_config_reseau, charger_liste_blanche
from slmsp.net.journal import JournalMemoire
from slmsp.net.profils import evaluer

CLE = "<cle-factice-secrete>"
OPENROUTER = {"id": "a1", "preset": "openrouter", "actif": True}
MISTRAL = {"id": "b2", "preset": "mistral", "actif": True}
OVH = {"id": "c3", "preset": "ovh", "actif": False}


class ChiffreurFactice:
    def proteger(self, donnees: bytes) -> bytes:
        return b"X" + donnees[::-1]

    def deproteger(self, donnees: bytes) -> bytes:
        if not donnees.startswith(b"X"):
            raise OSError("illisible")
        return donnees[1:][::-1]


@pytest.fixture
def stockage(tmp_path: Path) -> Stockage:
    return Stockage(tmp_path / "assistant.sqlite")


@pytest.fixture
def coffre(tmp_path: Path) -> CoffreCles:
    return CoffreCles(tmp_path, ChiffreurFactice())


# --- Réglage --------------------------------------------------------------------------------


def test_reglage_par_defaut_vide(stockage: Stockage) -> None:
    assert lire_reglage(stockage) == []


def test_preset_preremplit_url_et_modele() -> None:
    entrees = valider_reglage([OPENROUTER, MISTRAL, OVH])
    assert [(e["url_base"], e["modele"]) for e in entrees] == [
        ("https://openrouter.ai/api/v1", "qwen/qwen3.6-27b"),
        ("https://api.mistral.ai/v1", "mistral-small-latest"),
        ("https://oai.endpoints.kepler.ai.cloud.ovh.net/v1", "Qwen3.6-27B"),
    ]
    modifie = valider_reglage([{**OVH, "modele": "Mistral-Small-3.2-24B-Instruct-2506"}])
    assert modifie[0]["modele"] == "Mistral-Small-3.2-24B-Instruct-2506"


@pytest.mark.parametrize(
    "url",
    [
        "http://openrouter.ai/api/v1",
        "https://u:p@openrouter.ai/api/v1",
        "https://1.2.3.4/v1",
        "https://openrouter.ai:8443/v1",
        "https://openrouter.ai/v1?cle=x",
    ],
)
def test_reglage_url_refusee(url: str) -> None:
    with pytest.raises(ValueError):
        valider_reglage([{**OPENROUTER, "url_base": url}])


@pytest.mark.parametrize(
    ("liste", "motif"),
    [
        ([OPENROUTER, MISTRAL, OVH, {**OVH, "id": "d4"}], "au plus"),
        ([OPENROUTER, {**MISTRAL, "id": "a1"}], "double"),
        ([{**OPENROUTER, "id": "../x"}], "identifiant"),
        ([{**OPENROUTER, "preset": "openrouter-eu"}], "preset"),
        ([{"id": "e5", "preset": "generique"}], "URL"),
        ([{**OPENROUTER, "inconnu": 1}], "inconnue"),
    ],
)
def test_reglage_liste_refusee(liste: list[Any], motif: str) -> None:
    with pytest.raises(ValueError, match=motif):
        valider_reglage(liste)


def test_parametres_supplementaires_generique_seulement() -> None:
    generique = {"id": "e5", "preset": "generique", "url_base": "https://h.example/v1"}
    valeur = {**generique, "modele": "m", "parametres_supplementaires": {"reasoning_effort": "low"}}
    assert valider_reglage([valeur])[0]["parametres_supplementaires"] == {"reasoning_effort": "low"}
    with pytest.raises(ValueError, match="generique"):
        valider_reglage([{**OVH, "parametres_supplementaires": {"reasoning_effort": "low"}}])
    with pytest.raises(ValueError, match="interdites"):
        valider_reglage([{**valeur, "parametres_supplementaires": {"model": "x"}}])
    with pytest.raises(ValueError, match="2 Ko"):
        valider_reglage([{**valeur, "parametres_supplementaires": {"a": "x" * 3000}}])


def test_reglage_illisible_vaut_vide(stockage: Stockage) -> None:
    stockage.ecrire_reglage("fournisseurs_externes", [{**OPENROUTER, "url_base": "http://x"}])
    assert lire_reglage(stockage) == []


# --- Clés ---------------------------------------------------------------------------------


def test_coffre_chiffre_lit_efface(tmp_path: Path) -> None:
    coffre = CoffreCle(tmp_path, ChiffreurFactice())
    assert coffre.lire() is None
    coffre.enregistrer(CLE)
    assert CLE.encode() not in coffre.chemin.read_bytes()
    lue = coffre.lire()
    assert isinstance(lue, SecretStr) and lue.get_secret_value() == CLE
    coffre.effacer()
    assert coffre.lire() is None and not coffre.presente()


def test_une_cle_par_fournisseur(coffre: CoffreCles) -> None:
    coffre.enregistrer("a1", CLE)
    coffre.enregistrer("b2", "<autre-cle-factice>")
    assert coffre.lire("a1").get_secret_value() == CLE  # type: ignore[union-attr]
    assert coffre.lire("b2").get_secret_value() == "<autre-cle-factice>"  # type: ignore[union-attr]
    assert coffre.lire("c3") is None and coffre.lire("../x") is None
    with pytest.raises(ValueError):
        coffre.enregistrer("../x", CLE)
    coffre.ne_garder_que(["b2"])
    assert not coffre.presente("a1") and coffre.presente("b2")


def test_coffre_corrompu_vaut_absente(coffre: CoffreCles) -> None:
    coffre.pour("a1").chemin.write_bytes(b"corrompu")
    assert coffre.lire("a1") is None


@pytest.mark.skipif(sys.platform != "win32", reason="DPAPI : Windows seulement")
def test_dpapi_aller_retour(tmp_path: Path) -> None:
    coffre = CoffreCles(tmp_path)
    coffre.enregistrer("a1", CLE)
    assert CLE.encode() not in coffre.pour("a1").chemin.read_bytes()
    lue = coffre.lire("a1")
    assert lue is not None and lue.get_secret_value() == CLE


def test_pont_ne_renvoie_jamais_la_cle(stockage: Stockage, coffre: CoffreCles) -> None:
    pont = PontReglages(stockage, coffre=coffre)
    assert pont.appeler("ecrire", "fournisseurs_externes", [OPENROUTER])["ok"] is True
    assert pont.appeler("fournisseurs_externes")["fournisseurs"][0]["cle_enregistree"] is False
    assert pont.appeler("enregistrer_cle", "a1", CLE) == {"ok": True, "cle_enregistree": True}
    reponse = pont.appeler("fournisseurs_externes")
    assert reponse["fournisseurs"][0]["cle_enregistree"] is True
    assert CLE not in json.dumps(reponse) and CLE not in json.dumps(pont.appeler("lire"))
    assert pont.appeler("effacer_cle", "a1") == {"ok": True, "cle_enregistree": False}
    assert pont.appeler("enregistrer_cle", "a1", "")["ok"] is False
    assert pont.appeler("enregistrer_cle", "../x", CLE)["ok"] is False


def test_pont_liste_presets_et_ordre(stockage: Stockage, coffre: CoffreCles) -> None:
    pont = PontReglages(stockage, coffre=coffre)
    vide = pont.appeler("fournisseurs_externes")
    assert vide["fournisseurs"] == [] and vide["max"] == MAX_FOURNISSEURS
    assert [p["nom"] for p in vide["presets"]] == ["openrouter", "mistral", "ovh", "generique"]
    coffre.enregistrer("a1", CLE)
    r = pont.appeler("ecrire", "fournisseurs_externes", [MISTRAL, OPENROUTER])
    assert [e["id"] for e in r["fournisseurs"]] == ["b2", "a1"]
    assert [e["id"] for e in lire_reglage(stockage)] == ["b2", "a1"]
    # retirer une entrée efface sa clé
    assert pont.appeler("ecrire", "fournisseurs_externes", [MISTRAL])["ok"] is True
    assert not coffre.presente("a1")
    refus = pont.appeler(
        "ecrire", "fournisseurs_externes", [{**MISTRAL, "url_base": "http://a.example"}]
    )
    assert refus["ok"] is False and refus["erreur"]["code"] == "reglage-invalide"
    assert "http://a.example" not in refus["erreur"]["message"]


def test_pont_tester_cle_du_champ_ou_enregistree(stockage: Stockage, coffre: CoffreCles) -> None:
    recus: list[Any] = []

    def tester(entree: dict[str, Any], cle: Any) -> dict[str, Any]:
        recus.append((entree, cle))
        return {"reussi": False, "motif": "http-401", "hote": "openrouter.ai"}

    pont = PontReglages(stockage, coffre=coffre, tester=tester)
    r = pont.appeler("tester_modele_externe", {**OPENROUTER, "cle": CLE})
    assert r == {"ok": True, "reussi": False, "motif": "http-401", "hote": "openrouter.ai"}
    assert recus[-1][1].get_secret_value() == CLE
    coffre.enregistrer("a1", "<autre-cle-factice>", hote="openrouter.ai", preset="openrouter")
    pont.appeler("tester_modele_externe", dict(OPENROUTER))
    assert recus[-1][1].get_secret_value() == "<autre-cle-factice>"
    assert recus[-1][0]["preset"] == "openrouter"
    invalide = {**OPENROUTER, "url_base": "http://a"}
    assert pont.appeler("tester_modele_externe", invalide)["ok"] is False


# --- Revue 17.4 : clé liée à l'hôte et au preset ---------------------------------------


def test_cle_liee_a_l_hote_et_au_preset(coffre: CoffreCles) -> None:
    coffre.enregistrer("a1", CLE, hote="openrouter.ai", preset="openrouter")
    assert CLE.encode() not in coffre.pour("a1").chemin.read_bytes()
    lue = coffre.lire("a1", hote="openrouter.ai", preset="openrouter")
    assert lue is not None and lue.get_secret_value() == CLE
    assert coffre.lire("a1", hote="h.example", preset="openrouter") is None
    assert coffre.lire("a1", hote="openrouter.ai", preset="generique") is None
    assert coffre.etat("a1", "openrouter.ai", "openrouter") == "liee"
    assert coffre.etat("a1", "h.example", "generique") == "autre-hote"
    assert coffre.etat("b2", "openrouter.ai", "openrouter") == "absente"
    with pytest.raises(ValueError):
        coffre.enregistrer("a1", CLE, hote="openrouter.ai")
    coffre.enregistrer("b2", CLE)  # sans liaison : jamais rendue par une lecture liée
    assert coffre.lire("b2", hote="api.mistral.ai", preset="mistral") is None


def test_changement_d_hote_ou_de_preset_efface_la_cle(
    stockage: Stockage, coffre: CoffreCles
) -> None:
    pont = PontReglages(stockage, coffre=coffre)
    assert pont.appeler("ecrire", "fournisseurs_externes", [OPENROUTER, MISTRAL])["ok"] is True
    assert pont.appeler("enregistrer_cle", "a1", CLE)["cle_enregistree"] is True
    assert pont.appeler("enregistrer_cle", "b2", CLE)["cle_enregistree"] is True
    # même id, autre hôte : la clé est effacée, l'interface demande une nouvelle clé
    autre = {**OPENROUTER, "preset": "generique", "url_base": "https://h.example/v1", "modele": "m"}
    r = pont.appeler("ecrire", "fournisseurs_externes", [autre, MISTRAL])
    assert [e["cle_enregistree"] for e in r["fournisseurs"]] == [False, True]
    assert not coffre.presente("a1") and coffre.presente("b2")
    # même hôte, autre preset : effacée aussi
    meme_hote = {**MISTRAL, "preset": "generique", "url_base": "https://api.mistral.ai/v1"}
    r = pont.appeler("ecrire", "fournisseurs_externes", [autre, {**meme_hote, "modele": "m"}])
    assert r["fournisseurs"][1]["cle_enregistree"] is False and not coffre.presente("b2")


def test_cle_enregistree_avec_les_valeurs_du_formulaire(
    stockage: Stockage, coffre: CoffreCles
) -> None:
    pont = PontReglages(stockage, coffre=coffre)
    nouvelle = {
        "id": "e5",
        "preset": "generique",
        "url_base": "https://h.example/v1",
        "modele": "m",
    }
    # entrée pas encore enregistrée : liée aux valeurs du formulaire
    assert pont.appeler("enregistrer_cle", "e5", CLE, nouvelle)["cle_enregistree"] is True
    assert coffre.etat("e5", "h.example", "generique") == "liee"
    assert pont.appeler("enregistrer_cle", "e5", CLE, {**nouvelle, "id": "f6"})["ok"] is False
    assert pont.appeler("enregistrer_cle", "z9", CLE)["ok"] is False  # entrée inconnue
    r = pont.appeler("ecrire", "fournisseurs_externes", [nouvelle])
    assert r["fournisseurs"][0]["cle_enregistree"] is True


def test_test_de_connexion_refuse_une_cle_d_un_autre_hote(
    stockage: Stockage, coffre: CoffreCles
) -> None:
    recus: list[Any] = []

    def tester(entree: dict[str, Any], cle: Any) -> dict[str, Any]:
        recus.append(cle)
        return {"reussi": True, "latence_ms": 1, "hote": "x"}

    pont = PontReglages(stockage, coffre=coffre, tester=tester)
    pont.appeler("ecrire", "fournisseurs_externes", [OPENROUTER])
    pont.appeler("enregistrer_cle", "a1", CLE)
    detourne = {**OPENROUTER, "preset": "generique", "url_base": "https://h.example/v1"}
    r = pont.appeler("tester_modele_externe", {**detourne, "modele": "m"})
    assert r == {"ok": True, "reussi": False, "motif": "cle-autre-hote", "hote": "h.example"}
    assert recus == []  # aucune requête
    assert pont.appeler("tester_modele_externe", dict(OPENROUTER))["reussi"] is True
    assert recus[-1].get_secret_value() == CLE


def test_demarrage_ne_lit_que_les_cles_liees(coffre: CoffreCles) -> None:
    entrees = valider_reglage([OPENROUTER, MISTRAL])
    coffre.enregistrer("a1", CLE, hote="openrouter.ai", preset="openrouter")
    coffre.enregistrer("b2", CLE, hote="openrouter.ai", preset="openrouter")  # autre hôte
    lire = lecteur_cles(coffre)
    assert lire(entrees[0]).get_secret_value() == CLE  # type: ignore[union-attr]
    assert lire(entrees[1]) is None


# --- Réseau -------------------------------------------------------------------------------


def _verdict(config: Any, profil: str, methode: str, url: str) -> bool:
    return evaluer(
        profil,
        methode,
        url,
        mode="connecte",
        config=config,
        liste_blanche=charger_liste_blanche(),
    ).autorise


def test_profil_modele_externe_une_regle_par_fournisseur() -> None:
    base = charger_config_reseau()
    url = "https://openrouter.ai/api/v1/chat/completions"
    mistral = "https://api.mistral.ai/v1/chat/completions"
    assert not _verdict(base, "modele-externe", "POST", url)  # inactif : rien
    config = avec_modele_externe(
        base, ["https://openrouter.ai/api/v1", "https://api.mistral.ai/v1"]
    )
    assert len(config.profils.modele_externe.regles) == 2
    assert _verdict(config, "modele-externe", "POST", url)
    assert _verdict(config, "modele-externe", "POST", mistral)
    assert not _verdict(config, "modele-externe", "GET", url)
    assert not _verdict(config, "modele-externe", "POST", "https://openrouter.ai/api/v1/models")
    assert not _verdict(config, "modele-externe", "POST", "https://api.mistral.ai/v1/models")
    assert not _verdict(
        config, "modele-externe", "POST", "https://openrouter.ai:8443/api/v1/chat/completions"
    )
    # ni l'assistant ni l'outillage n'héritent des hôtes ; la Liste blanche est inchangée
    assert not _verdict(config, "assistant", "POST", url)
    assert not _verdict(config, "outillage", "GET", mistral)
    assert config.profils.outillage == base.profils.outillage
    assert base.profils.modele_externe.regles == []


def test_mode_hors_ligne_refuse_le_profil() -> None:
    config = avec_modele_externe(charger_config_reseau(), "https://openrouter.ai/api/v1")
    verdict = evaluer(
        "modele-externe",
        "POST",
        "https://openrouter.ai/api/v1/chat/completions",
        mode="hors-ligne-force",
        config=config,
        liste_blanche=charger_liste_blanche(),
    )
    assert verdict.statut == "bloquee-mode"


# --- Branchement et test de connexion -----------------------------------------------------


class Mode:
    def mode_courant(self) -> str:
        return "connecte"


def _passerelle(journal: JournalMemoire) -> Passerelle:
    return Passerelle(Mode(), journal)


def _assemblage(llm: Any) -> Any:
    return SimpleNamespace(
        service=SimpleNamespace(llm=llm, mode=Mode()), passerelle=_passerelle(JournalMemoire())
    )


def test_aucun_actif_aucun_changement(stockage: Stockage) -> None:
    llm = object()
    assemblage = _assemblage(llm)
    assert brancher_hybride(assemblage, "slm", lire_reglage(stockage), lambda _i: None) is None
    entrees = valider_reglage([{**OPENROUTER, "actif": False}])
    assert brancher_hybride(assemblage, "slm", entrees, lambda _i: None) is None
    assert assemblage.service.llm is llm


def test_actifs_branches_dans_l_ordre_avec_leur_cle() -> None:
    from slmsp.inference.hybride import ClientHybride

    llm = SimpleNamespace(taille_contexte=2048)
    assemblage = _assemblage(llm)
    entrees = valider_reglage([MISTRAL, OVH, OPENROUTER])
    cles = {"a1": SecretStr(CLE), "b2": SecretStr("<autre-cle-factice>")}
    en_cours = brancher_hybride(assemblage, "slm", entrees, lambda e: cles.get(e["id"]))
    assert en_cours == {
        "tete": "mistral/mistral-small-latest",
        "preset": "mistral",
        "hote": "api.mistral.ai",
        "modele": "mistral-small-latest",
        "secours": 1,
    }
    composite = assemblage.service.llm
    assert isinstance(composite, ClientHybride)
    assert [c.preset.nom for c in composite.externes] == ["mistral", "openrouter"]
    assert composite.local is llm and composite.taille_contexte == 2048
    # la passerelle de l'assemblage n'est pas modifiée
    assert assemblage.passerelle.config.profils.modele_externe.regles == []


def test_tester_connexion_reussite_et_echec() -> None:
    import httpx2  # noqa: TID251 (tests : transport factice)

    entree = valider_reglage([MISTRAL])[0]

    def ok(requete: Any) -> Any:
        corps = json.loads(requete.content)
        assert corps["max_tokens"] == 1 and "seed" not in corps
        assert str(requete.url) == "https://api.mistral.ai/v1/chat/completions"
        fin = {"choices": [{"index": 0, "delta": {}, "finish_reason": "length"}]}
        return httpx2.Response(200, content=f"data: {json.dumps(fin)}\n\ndata: [DONE]\n".encode())

    journal = JournalMemoire()
    r = connexion_testee(
        entree, SecretStr(CLE), _passerelle(journal), transport_interne=httpx2.MockTransport(ok)
    )
    assert r["reussi"] is True and isinstance(r["latence_ms"], int)
    assert [e.profil for e in journal.lister()] == ["modele-externe"]

    def refus(requete: Any) -> Any:
        return httpx2.Response(401, json={"error": {"message": "<corps-erreur-factice>"}})

    r = connexion_testee(
        entree,
        SecretStr(CLE),
        _passerelle(journal),
        transport_interne=httpx2.MockTransport(refus),
    )
    assert r == {"reussi": False, "motif": "http-401", "hote": "api.mistral.ai"}
    r = connexion_testee(entree, None, _passerelle(journal))
    assert r["motif"] == "cle-absente"


# --- Indicateur de Mode et À propos -----------------------------------------------------


def test_mode_et_a_propos_portent_la_tete_et_les_secours() -> None:
    assert "modele_externe" not in PontMode(Mode()).etat()
    etat = PontMode(Mode(), modele_externe="mistral/m", secours_externes=2).etat()
    assert etat["modele_externe"] == "mistral/m" and etat["secours_externes"] == 2
    en_cours = {"tete": "mistral/m", "preset": "mistral", "hote": "h", "modele": "m", "secours": 2}
    pont = PontReglages(modele_externe=en_cours)
    assert pont.a_propos()["modele_externe"] == en_cours
    assert PontReglages().a_propos()["modele_externe"] is None


# --- Traçabilité -------------------------------------------------------------------------


class FluxAvecModele:
    def __init__(self) -> None:
        self._flux = iter([Jeton(texte="<réponse-factice-1>"), Fin(raison="terminee")])
        self.modele_repondant = "externe:openrouter/<modele-factice>"

    def __iter__(self) -> FluxAvecModele:
        return self

    def __next__(self) -> Any:
        return next(self._flux)


class Service:
    def __init__(self, flux: Any) -> None:
        self.flux = flux

    def repondre(self, tache: str, messages: Any, options: Any) -> Any:
        return self.flux


def _pousses(service: Service, modele_local: str | None) -> list[dict[str, Any]]:
    lots: list[dict[str, Any]] = []
    fini = threading.Event()

    def pousser(lot: list[dict[str, Any]]) -> None:
        lots.extend(lot)

    conversation = Conversation(service, pousser, modele_local=modele_local)  # type: ignore[arg-type]
    conversation.envoyer("Q", [{"role": "user", "content": "<question-factice>"}])
    conversation.attendre(5)
    fini.set()
    return lots


def test_fin_porte_le_modele_repondant() -> None:
    lots = _pousses(Service(FluxAvecModele()), "slm")
    assert lots[-1]["modele_repondant"] == "externe:openrouter/<modele-factice>"
    flux = iter([Jeton(texte="<réponse-factice-1>"), Fin(raison="terminee")])
    assert _pousses(Service(flux), "slm")[-1]["modele_repondant"] == "local:slm"
    flux = iter([Fin(raison="terminee")])
    assert "modele_repondant" not in _pousses(Service(flux), None)[-1]


def test_historique_et_retours_consignent_le_modele(stockage: Stockage) -> None:
    messages = [
        {"role": "user", "content": "<question-factice>"},
        {
            "role": "assistant",
            "content": "<réponse-factice-1>",
            "modele_repondant": "externe:openrouter/<modele-factice>",
        },
    ]
    historique = PontHistorique(stockage)
    r = historique.appeler("enregistrer", "Q", messages, [], None)
    assert r["ok"] is True
    lu = historique.appeler("ouvrir", r["id"])["conversation"]["messages"][1]
    assert lu["modele_repondant"] == "externe:openrouter/<modele-factice>"
    invalide = [messages[0], {**messages[1], "modele_repondant": 3}]
    assert historique.appeler("enregistrer", "Q", invalide, [], None)["ok"] is False

    assert PontRetours(stockage).appeler("noter", r["id"], 1, "pouce_haut") == {"ok": True}
    retour = stockage.lister_retours()[0]
    assert retour["modele_repondant"] == "externe:openrouter/<modele-factice>"
    export = json.loads(construire_export(stockage, prenoms=frozenset()).contenu)
    assert export["retours"][0]["modele_repondant"] == "externe:openrouter/<modele-factice>"


@pytest.mark.parametrize(
    ("valeur", "attendu"),
    [
        ("local:slm", "local:slm"),
        ("externe:mistral/m", "externe:mistral/m"),
        ("autre:x", None),
        ("externe:", None),
        ("local:a b", None),
        ("local:" + "x" * 400, None),
        (3, None),
    ],
)
def test_retours_valident_le_modele_repondant(valeur: Any, attendu: Any) -> None:
    from slmsp.app.pont.retours import modele_repondant_valide

    assert modele_repondant_valide(valeur) == attendu


def test_migration_additive_des_retours(tmp_path: Path) -> None:
    import sqlite3
    from contextlib import closing

    chemin = tmp_path / "ancienne.sqlite"
    Stockage(chemin).enregistrer_retour(
        tache="Q", question="<q-factice>", reponse="<r-factice>", sources=[], pouce="haut"
    )
    with closing(sqlite3.connect(chemin)) as connexion, connexion:
        connexion.execute("ALTER TABLE retours DROP COLUMN modele_repondant")
    stockage = Stockage(chemin)
    assert "modele_repondant" not in stockage.lister_retours()[0]
    assert len(stockage.lister_retours()) == 1
