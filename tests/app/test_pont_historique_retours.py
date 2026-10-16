"""Story 12.11 : domaines `historique` et `retours` du pont (Stockage réel dans `tmp_path`).

Les textes sont des chaînes factices ou aléatoires (D1) ; aucun appel réseau.
"""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from slmsp.app.pont.erreurs import NonImplementee
from slmsp.app.pont.historique import PontHistorique
from slmsp.app.pont.retours import PontRetours
from slmsp.app.principal import dialogue_enregistrer
from slmsp.app.stockage import Stockage


@pytest.fixture
def stockage(tmp_path: Path) -> Stockage:
    return Stockage(tmp_path / "a.sqlite")


def _messages(marqueur: str) -> list[dict[str, str]]:
    return [
        {"role": "user", "content": f"<question-factice-{marqueur}>"},
        {"role": "assistant", "content": f"<réponse-factice-{marqueur}>"},
    ]


def _code(reponse: dict[str, Any]) -> str:
    assert reponse["ok"] is False
    return str(reponse["erreur"]["code"])


# -- historique ---------------------------------------------------------------------------------


def test_enregistrer_cree_puis_remplace(stockage: Stockage) -> None:
    h = PontHistorique(stockage)
    m = uuid.uuid4().hex
    premier = h.appeler("enregistrer", "Q", _messages(m)[:1], [], None)
    assert premier["ok"] is True
    identifiant = premier["id"]
    suite = [*_messages(m), {"role": "user", "content": "<suite-factice>"}]
    second = h.appeler("enregistrer", "Q", suite, [{"titre": "<source-factice>"}], identifiant)
    assert second["id"] == identifiant
    liste = h.appeler("lister")["conversations"]
    assert [c["id"] for c in liste] == [identifiant]
    assert liste[0]["titre"] == f"<question-factice-{m}>"
    assert liste[0]["tache"] == "Q"
    ouverte = h.appeler("ouvrir", identifiant)["conversation"]
    assert ouverte["messages"] == suite
    assert ouverte["sources"] == [{"titre": "<source-factice>"}]


def test_identifiant_inconnu_cree_une_nouvelle_conversation(stockage: Stockage) -> None:
    h = PontHistorique(stockage)
    r = h.appeler("enregistrer", "Q", _messages("a"), [], "inconnu123")
    assert r["ok"] is True
    assert r["id"] != "inconnu123"


@pytest.mark.parametrize(
    "args",
    [
        ("", _messages("a"), [], None),
        ("XX", _messages("a"), [], None),  # Tâche inconnue
        ("Q", [{"role": "assistant", "content": "x", "sources": "pas-une-liste"}], [], None),
        ("Q", [{"role": "assistant", "content": "x", "interrompue": "oui"}], [], None),
        ("Q", [], [], None),
        ("Q", [{"role": "system", "content": "x"}], [], None),
        ("Q", [{"role": "user", "content": 3}], [], None),
        ("Q", _messages("a"), "pas-une-liste", None),
        ("Q", _messages("a"), [], "../id"),
    ],
)
def test_enregistrer_refuse_le_invalide(stockage: Stockage, args: tuple[Any, ...]) -> None:
    h = PontHistorique(stockage)
    assert _code(h.appeler("enregistrer", *args)) == "conversation-invalide"
    assert h.appeler("lister")["conversations"] == []


def test_supprimer_puis_annuler_sous_5_secondes(stockage: Stockage) -> None:
    h = PontHistorique(stockage)
    identifiant = h.appeler("enregistrer", "Q", _messages("a"), [], None)["id"]
    assert h.appeler("supprimer", identifiant) == {"ok": True, "supprimee": True}
    assert h.appeler("lister")["conversations"] == []
    assert _code(h.appeler("ouvrir", identifiant)) == "conversation-introuvable"
    assert h.appeler("annuler_suppression", identifiant) == {"ok": True, "restauree": True}
    assert [c["id"] for c in h.appeler("lister")["conversations"]] == [identifiant]
    assert h.appeler("supprimer", "absente") == {"ok": True, "supprimee": False}
    for invalide in ("../x", "", None, 3, "a" * 65):
        assert h.appeler("supprimer", invalide) == {"ok": True, "supprimee": False}
        assert h.appeler("annuler_suppression", invalide) == {"ok": True, "restauree": False}
        assert _code(h.appeler("ouvrir", invalide)) == "conversation-introuvable"


def test_enregistrer_garde_sources_par_message_et_marque_interrompue(stockage: Stockage) -> None:
    h = PontHistorique(stockage)
    messages = [
        {"role": "user", "content": "<q>"},
        {"role": "assistant", "content": "<r>", "sources": [{"titre": "<s>"}], "interrompue": True},
    ]
    identifiant = h.appeler("enregistrer", "RD", messages, [{"titre": "<s>"}], None)["id"]
    assert h.appeler("ouvrir", identifiant)["conversation"]["messages"] == messages


def test_annulation_apres_delai_refusee(tmp_path: Path) -> None:
    horloge = [0.0]
    s = Stockage(tmp_path / "b.sqlite", monotone=lambda: horloge[0])
    h = PontHistorique(s)
    identifiant = h.appeler("enregistrer", "Q", _messages("a"), [], None)["id"]
    h.appeler("supprimer", identifiant)
    horloge[0] = 6.0
    assert h.appeler("annuler_suppression", identifiant) == {"ok": True, "restauree": False}
    assert h.appeler("lister")["conversations"] == []


def test_historique_sans_stockage_et_methode_inconnue() -> None:
    assert _code(PontHistorique(None).appeler("lister")) == "stockage-indisponible"
    with pytest.raises(NonImplementee):
        PontHistorique(None).appeler("inconnue")


# -- retours ------------------------------------------------------------------------------------


def _conversation(stockage: Stockage, marqueur: str) -> str:
    return str(
        PontHistorique(stockage).appeler(
            "enregistrer", "Q", _messages(marqueur), [{"titre": "<source-factice>"}], None
        )["id"]
    )


def test_pouce_haut_enregistre_tout_de_suite(stockage: Stockage) -> None:
    m = uuid.uuid4().hex
    identifiant = _conversation(stockage, m)
    r = PontRetours(stockage).appeler("noter", identifiant, 1, "pouce_haut", "ignoré")
    assert r == {"ok": True}
    (retour,) = stockage.lister_retours()
    assert retour["pouce"] == "haut"
    assert retour["commentaire"] is None  # le commentaire ne vaut que pour le pouce bas
    assert retour["question"] == f"<question-factice-{m}>"
    assert retour["reponse"] == f"<réponse-factice-{m}>"
    assert retour["sources"] == [{"titre": "<source-factice>"}]
    assert retour["tache"] == "Q"


def test_pouce_bas_avec_et_sans_commentaire(stockage: Stockage) -> None:
    identifiant = _conversation(stockage, "a")
    retours = PontRetours(stockage)
    retours.appeler("noter", identifiant, 1, "pouce_bas", "  <commentaire-factice>  ")
    retours.appeler("noter", identifiant, 1, "pouce_bas", "   ")
    retours.appeler("noter", identifiant, 1, "pouce_bas", None)
    commentaires = [r["commentaire"] for r in stockage.lister_retours()]
    assert commentaires == ["<commentaire-factice>", None, None]
    liste = retours.appeler("lister")
    assert liste["nombre"] == 3
    assert set(liste["retours"][0]) == {"id", "cree_le", "tache", "pouce", "commentaire"}


def test_noter_refuse_le_invalide(stockage: Stockage) -> None:
    identifiant = _conversation(stockage, "a")
    retours = PontRetours(stockage)
    assert _code(retours.appeler("noter", identifiant, 1, "neutre")) == "jugement-invalide"
    for absente in ("absente", "../x", "", None, 3):
        assert _code(retours.appeler("noter", absente, 1, "pouce_haut")) == (
            "conversation-introuvable"
        )
    for indice in (0, 5, -1, True, "1"):  # 0 est un message de l'Agent
        assert _code(retours.appeler("noter", identifiant, indice, "pouce_haut")) == (
            "message-invalide"
        )
    assert stockage.lister_retours() == []


def test_exporter_exige_l_apercu_puis_ecrit_l_apercu_valide(
    stockage: Stockage, tmp_path: Path
) -> None:
    identifiant = _conversation(stockage, "a")
    cible = tmp_path / "sortie" / "mon-export.json"
    demandes: list[str] = []

    def choisir(nom: str) -> str | None:
        demandes.append(nom)
        return str(cible)

    retours = PontRetours(stockage, choisir)
    assert _code(retours.appeler("exporter")) == "apercu-requis"
    assert _code(retours.appeler("apercu_export")) == "aucun-retour"
    retours.appeler("noter", identifiant, 1, "pouce_bas", "<commentaire-factice>")
    apercu = retours.appeler("apercu_export")
    assert apercu["ok"] is True
    assert apercu["nombre"] == 1
    assert apercu["nom_fichier"].startswith("retours-assistant-")
    assert "<commentaire-factice>" in apercu["apercu"]
    assert not cible.parent.exists()  # rien n'est écrit avant « Enregistrer sous »
    assert retours.appeler("exporter") == {"ok": True, "enregistre": True, "nom": cible.name}
    assert demandes == [apercu["nom_fichier"]]
    assert len(json.loads(cible.read_text(encoding="utf-8"))["retours"]) == 1


def test_un_nouveau_retour_invalide_l_apercu(stockage: Stockage, tmp_path: Path) -> None:
    identifiant = _conversation(stockage, "a")
    retours = PontRetours(stockage, lambda nom: str(tmp_path / nom))
    retours.appeler("noter", identifiant, 1, "pouce_bas", None)
    retours.appeler("apercu_export")
    retours.appeler("noter", identifiant, 1, "pouce_haut")
    assert _code(retours.appeler("exporter")) == "apercu-requis"
    assert list(tmp_path.glob("*.json")) == []


def test_historique_efface_apres_l_apercu_rien_n_est_ecrit(
    stockage: Stockage, tmp_path: Path
) -> None:
    identifiant = _conversation(stockage, "a")
    retours = PontRetours(stockage, lambda nom: str(tmp_path / nom))
    retours.appeler("noter", identifiant, 1, "pouce_bas", "<commentaire-factice>")
    retours.appeler("apercu_export")
    stockage.effacer_historique()  # « Effacer l'historique » des Paramètres (autre domaine)
    assert _code(retours.appeler("exporter")) == "apercu-perime"
    assert _code(retours.appeler("exporter")) == "apercu-requis"
    assert list(tmp_path.glob("*.json")) == []


def test_exporter_n_ecrase_jamais_un_fichier(stockage: Stockage, tmp_path: Path) -> None:
    identifiant = _conversation(stockage, "a")
    cible = tmp_path / "existant.json"
    cible.write_text("<contenu-factice>", encoding="utf-8")
    retours = PontRetours(stockage, lambda nom: str(cible))
    retours.appeler("noter", identifiant, 1, "pouce_haut")
    retours.appeler("apercu_export")
    assert _code(retours.appeler("exporter")) == "fichier-existant"
    assert cible.read_text(encoding="utf-8") == "<contenu-factice>"


def test_noter_prend_les_sources_de_la_reponse_notee(stockage: Stockage) -> None:
    messages = [
        {"role": "user", "content": "<q1>"},
        {"role": "assistant", "content": "<r1>", "sources": [{"titre": "<s1>"}]},
        {"role": "user", "content": "<q2>"},
        {"role": "assistant", "content": "<r2>", "sources": [{"titre": "<s2>"}]},
    ]
    identifiant = PontHistorique(stockage).appeler(
        "enregistrer", "Q", messages, [{"titre": "<s2>"}], None
    )["id"]
    retours = PontRetours(stockage)
    assert retours.appeler("noter", identifiant, 1, "pouce_haut") == {"ok": True}
    assert retours.appeler("noter", identifiant, 3, "pouce_haut") == {"ok": True}
    par_reponse = {r["reponse"]: (r["question"], r["sources"]) for r in stockage.lister_retours()}
    assert par_reponse == {
        "<r1>": ("<q1>", [{"titre": "<s1>"}]),
        "<r2>": ("<q2>", [{"titre": "<s2>"}]),
    }


def test_noter_sans_sources_par_message(stockage: Stockage) -> None:
    """Conversation sans sources par message : seule la dernière réponse prend celles stockées."""
    identifiant = PontHistorique(stockage).appeler(
        "enregistrer", "Q", _messages("a") + _messages("b"), [{"titre": "<s>"}], None
    )["id"]
    retours = PontRetours(stockage)
    retours.appeler("noter", identifiant, 1, "pouce_haut")
    retours.appeler("noter", identifiant, 3, "pouce_haut")
    par_reponse = {r["reponse"]: r["sources"] for r in stockage.lister_retours()}
    assert par_reponse == {"<réponse-factice-a>": [], "<réponse-factice-b>": [{"titre": "<s>"}]}


def test_exporter_annule_ou_dialogue_absent(stockage: Stockage, tmp_path: Path) -> None:
    identifiant = _conversation(stockage, "a")
    PontRetours(stockage).appeler("noter", identifiant, 1, "pouce_haut")
    annule = PontRetours(stockage, lambda nom: None)
    annule.appeler("apercu_export")
    assert annule.appeler("exporter") == {"ok": True, "enregistre": False, "nom": None}
    sans = PontRetours(stockage)
    sans.appeler("apercu_export")
    assert _code(sans.appeler("exporter")) == "dialogue-indisponible"
    impossible = PontRetours(stockage, lambda nom: str(tmp_path / "fichier" / "x.json"))
    (tmp_path / "fichier").write_text("occupé", encoding="utf-8")  # un fichier, pas un dossier
    impossible.appeler("apercu_export")
    assert _code(impossible.appeler("exporter")) == "ecriture-impossible"


def test_exporter_ne_fait_aucune_requete_sortante(
    stockage: Stockage, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import socket

    def interdit(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("accès réseau")

    monkeypatch.setattr(socket, "create_connection", interdit)
    monkeypatch.setattr(socket.socket, "connect", interdit)
    identifiant = _conversation(stockage, "a")
    retours = PontRetours(stockage, lambda nom: str(tmp_path / nom))
    retours.appeler("noter", identifiant, 1, "pouce_haut")
    retours.appeler("apercu_export")
    assert retours.appeler("exporter")["enregistre"] is True


# -- dialogue « Enregistrer sous » (principal.py) -------------------------------------------------


class _Fenetre:
    def __init__(self, choix: Any) -> None:
        self.choix = choix
        self.appels: list[tuple[Any, dict[str, Any]]] = []

    def create_file_dialog(self, type_dialogue: Any, **kwargs: Any) -> Any:
        self.appels.append((type_dialogue, kwargs))
        return self.choix


def _faux_webview(monkeypatch: pytest.MonkeyPatch, *, nouveau: bool) -> None:
    module = ModuleType("webview")
    if nouveau:
        module.FileDialog = type("FileDialog", (), {"SAVE": "SAVE-NEUF"})  # type: ignore[attr-defined]
    else:
        module.SAVE_DIALOG = "SAVE-ANCIEN"  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "webview", module)


@pytest.mark.parametrize(("nouveau", "attendu"), [(True, "SAVE-NEUF"), (False, "SAVE-ANCIEN")])
def test_dialogue_enregistrer_propose_le_nom(
    monkeypatch: pytest.MonkeyPatch, nouveau: bool, attendu: str
) -> None:
    _faux_webview(monkeypatch, nouveau=nouveau)
    fenetre = _Fenetre(("C:/x/retours.json",))
    assert dialogue_enregistrer(fenetre)("retours-assistant-2026-10-17.json") == "C:/x/retours.json"
    type_dialogue, kwargs = fenetre.appels[0]
    assert type_dialogue == attendu
    assert kwargs["save_filename"] == "retours-assistant-2026-10-17.json"


def test_dialogue_enregistrer_annule(monkeypatch: pytest.MonkeyPatch) -> None:
    _faux_webview(monkeypatch, nouveau=True)
    assert dialogue_enregistrer(_Fenetre(None))("x.json") is None
    assert dialogue_enregistrer(_Fenetre(()))("x.json") is None
