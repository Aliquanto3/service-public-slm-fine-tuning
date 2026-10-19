"""Rendu des appels d'outils à l'entraînement, aligné sur l'inférence (spec-outils-rendu, R7).

Tests rapides, sans modèle. Les contenus sont factices (D1) ; les outils sont ceux de
`config/outils-mcp.toml`, qui ne sont pas des Données d'entraînement.
"""

from __future__ import annotations

import copy
import json
from typing import Any

import pytest

from slmsp.core.erreurs import ManifesteInvalide
from slmsp.fetch.config import charger_config_modele
from slmsp.mcp.outils import charger_outils
from slmsp.train import chargement, run

ARGUMENTS = '{"zeta": "<é-factice>", "alpha": 1}'  # ordre non trié, accent, entier


def appel(arguments: Any = ARGUMENTS) -> dict[str, Any]:
    return {"id": "c1", "type": "function", "function": {"name": "outil", "arguments": arguments}}


def messages_avec_appel(arguments: Any = ARGUMENTS, **extra: Any) -> list[dict[str, Any]]:
    return [
        {"role": "system", "content": "<système-factice>"},
        {"role": "user", "content": "<question-factice>"},
        {"role": "assistant", "content": "<réponse-factice-0>", "tool_calls": [appel(arguments)]}
        | extra,
        {"role": "tool", "tool_call_id": "c1", "content": "<résultat-factice>"},
        {"role": "assistant", "content": "<réponse-factice-1>"},
    ]


# ---- décodage des messages -------------------------------------------------------------------


def test_arguments_decodes_dans_l_ordre_sans_modifier_l_entree() -> None:
    config = charger_config_modele("granite-4.0-1b")
    entree = messages_avec_appel()
    copie = copy.deepcopy(entree)
    rendus = chargement._messages_rendus(entree, config)
    arguments = rendus[2]["tool_calls"][0]["function"]["arguments"]
    assert arguments == {"zeta": "<é-factice>", "alpha": 1}
    assert list(arguments) == ["zeta", "alpha"]  # ordre du texte, non trié
    assert entree == copie  # message copié, jamais modifié
    assert rendus[2]["tool_calls"][0] is not entree[2]["tool_calls"][0]


def test_arguments_deja_en_objet_non_touches() -> None:
    config = charger_config_modele("granite-4.0-1b")
    objet = {"b": 1, "a": 2}
    rendus = chargement._messages_rendus(messages_avec_appel(objet), config)
    assert rendus[2]["tool_calls"][0]["function"]["arguments"] == objet


@pytest.mark.parametrize("arguments", ["{pas du json", "[1, 2]", '"texte"', "null"])
def test_arguments_illisibles_ou_non_objet_refuses(arguments: str) -> None:
    config = charger_config_modele("granite-4.0-1b")
    with pytest.raises(ManifesteInvalide, match="arguments d'appel d'outil"):
        chargement._messages_rendus(messages_avec_appel(arguments), config)


def test_content_null_retire() -> None:
    config = charger_config_modele("granite-4.0-1b")
    rendus = chargement._messages_rendus(messages_avec_appel(content=None), config)
    assert "content" not in rendus[2] and rendus[1]["content"] == "<question-factice>"


def test_balises_tool_call_inchange() -> None:
    config = charger_config_modele("smollm3-3b")
    assert config.protocole_outils == "balises-tool-call"
    entree = messages_avec_appel("{}")
    rendus = chargement._messages_rendus(entree, config)
    assert "tool_calls" not in rendus[2] and "<tool_call>" in rendus[2]["content"]


# ---- _tools_rendus ---------------------------------------------------------------------------


def ligne_rd(factices, **champs: Any) -> Any:
    ligne = factices.ligne(1) | champs
    return chargement._Ligne.model_validate(ligne)


def test_tools_rendus_dans_l_ordre_du_fichier(factices) -> None:
    triees = [json.loads(json.dumps(o, sort_keys=True)) for o in charger_outils()]
    assert list(triees[0]) != list(charger_outils()[0])  # clés triées ≠ ordre du fichier
    ligne = ligne_rd(factices, tools=list(reversed(triees)))
    rendus = chargement._tools_rendus(ligne)
    assert rendus == charger_outils()
    assert list(rendus[0]) == list(charger_outils()[0])
    assert list(rendus[0]["function"]) == ["name", "description", "parameters"]


def test_tools_rendus_sans_outils_ou_tache_sans_outils(factices) -> None:
    assert chargement._tools_rendus(ligne_rd(factices, tools=[])) is None
    assert chargement._tools_rendus(ligne_rd(factices, tools=None)) is None
    with pytest.raises(ManifesteInvalide, match="diffèrent"):
        chargement._tools_rendus(ligne_rd(factices, tache="Q"))


def test_tools_rendus_ligne_divergente_refusee(factices) -> None:
    outils = charger_outils()
    modifie = copy.deepcopy(outils)
    modifie[0]["function"]["description"] += " <modifiée>"
    for tools in (modifie, outils[1:], [*outils, outils[0]]):
        with pytest.raises(ManifesteInvalide, match="diffèrent"):
            chargement._tools_rendus(ligne_rd(factices, tools=tools))
    with pytest.raises(ManifesteInvalide, match="inconnue"):
        chargement._tools_rendus(ligne_rd(factices, tache="XX"))


def test_sha_outils_mcp_controle(factices) -> None:
    ligne = ligne_rd(factices)
    with pytest.raises(ManifesteInvalide, match="sans « sha_outils_mcp »"):
        chargement.controler_outils_mcp({}, [ligne])  # clé absente : jeu à outils refusé
    chargement.controler_outils_mcp({}, [ligne_rd(factices, tools=[])])  # sans outils : rien
    chargement.controler_outils_mcp({"sha_outils_mcp": "0" * 64}, [ligne_rd(factices, tools=[])])
    with pytest.raises(ManifesteInvalide, match="sha_outils_mcp"):
        chargement.controler_outils_mcp({"sha_outils_mcp": "0" * 64}, [ligne])
    from slmsp.core.canonique import sha256_fichier
    from slmsp.core.config import racine_projet

    sha = sha256_fichier(racine_projet() / "config" / "outils-mcp.toml")
    chargement.controler_outils_mcp({"sha_outils_mcp": sha}, [ligne])


def test_sha_outils_mcp_herite_du_jeu_sft_pour_les_paires(projet, factices) -> None:
    """Paires ORPO : MANIFEST sans la clé, SHA lu dans celui du jeu SFT (`jeu_sft_version`)."""
    projet.ecrire_jeu("v1", manifeste={"sha_outils_mcp": "0" * 64})
    paires = [factices.paire(1)]
    projet.ecrire_jeu(
        "v2",
        paires,
        fichier="preferences.jsonl",
        manifeste={"sha_outils_mcp": None, "jeu_sft_version": "v1"},
    )
    with pytest.raises(ManifesteInvalide, match="a changé"):
        chargement.charger_jeu("v2", racine=projet.racine, fichier="preferences.jsonl")
    projet.ecrire_jeu("v1")  # SHA du projet
    jeu = chargement.charger_jeu("v2", racine=projet.racine, fichier="preferences.jsonl")
    assert len(jeu.lignes) == 1
    projet.ecrire_jeu(
        "v3",
        paires,
        fichier="preferences.jsonl",
        manifeste={"sha_outils_mcp": None, "jeu_sft_version": None},
    )
    with pytest.raises(ManifesteInvalide, match="sans « sha_outils_mcp »"):
        chargement.charger_jeu("v3", racine=projet.racine, fichier="preferences.jsonl")


@pytest.mark.parametrize(
    "arguments",
    [
        '{"query": null}',
        '{"query": ["<a-factice>"]}',
        '{"query": {"x": 1}}',
        '{"query": NaN}',
        None,
        ["<a-factice>"],
        3,
    ],
)
def test_arguments_sans_rendu_prouve_refuses(arguments: Any) -> None:
    """`null`, liste, objet imbriqué, constante non JSON, `arguments` ni chaîne ni objet."""
    config = charger_config_modele("minicpm5-1b")
    with pytest.raises(ManifesteInvalide, match="arguments d'appel d'outil"):
        chargement._messages_rendus(messages_avec_appel(arguments), config)


# ---- les deux chemins : pretokeniser et preparer_preferences --------------------------------


def conversation_rd(factices) -> dict[str, Any]:
    ligne = factices.ligne(1)
    ligne["messages"][2:2] = [
        {"role": "assistant", "content": "<texte-factice>", "tool_calls": [appel()]},
        {"role": "tool", "tool_call_id": "c1", "content": "<résultat-factice>"},
    ]
    return ligne


def verifier(messages: list[dict[str, Any]], tools: Any) -> None:
    appels = [m["tool_calls"][0] for m in messages if m.get("tool_calls")]
    assert appels and all(isinstance(a["function"]["arguments"], dict) for a in appels)
    assert list(appels[0]["function"]["arguments"]) == ["zeta", "alpha"]
    assert tools == charger_outils() and list(tools[0]["function"]) == [
        "name",
        "description",
        "parameters",
    ]


def test_pretokeniser_normalise(factices) -> None:
    ligne = conversation_rd(factices)
    ligne["tools"] = [json.loads(json.dumps(o, sort_keys=True)) for o in ligne["tools"]]
    tok = factices.Tokenizer()
    vus: list[tuple[Any, Any]] = []
    rendre = tok.apply_chat_template

    def espion(messages, *, tools=None, **kwargs):
        vus.append((messages, tools))
        return rendre(messages, tools=tools, **kwargs)

    tok.apply_chat_template = espion
    chargement.pretokeniser(
        tok,
        [chargement._Ligne.model_validate(ligne)],
        longueur_max=10_000,
        config_modele=charger_config_modele("granite-4.0-1b"),
    )
    assert vus
    for messages, tools in vus:
        if any(m.get("tool_calls") for m in messages):
            verifier(messages, tools)
        assert tools == charger_outils()


def test_pretokeniser_par_tour_normalise(factices, monkeypatch) -> None:
    ligne = conversation_rd(factices)
    vus: list[tuple[Any, Any]] = []

    def faux(tokenizer, messages, *, tools, config):
        vus.append((messages, tools))
        return []

    monkeypatch.setattr(chargement, "calculer_masques", faux)
    chargement.pretokeniser(
        factices.Tokenizer(),
        [chargement._Ligne.model_validate(ligne)],
        longueur_max=10_000,
        config_modele=charger_config_modele("minicpm5-1b"),
    )
    ((messages, tools),) = vus
    verifier(messages, tools)


@pytest.mark.parametrize("slug", ["granite-4.0-1b", "minicpm5-1b"])
def test_preferences_normalisent_prompt_chosen_et_rejected(factices, monkeypatch, slug) -> None:
    config = charger_config_modele(slug)
    paire = factices.paire(1)
    paire["tools"] = [json.loads(json.dumps(o, sort_keys=True)) for o in paire["tools"]]
    paire["prompt"] = conversation_rd(factices)["messages"][:-1]
    paire["chosen"] = [{"role": "assistant", "content": "<c-factice>", "tool_calls": [appel()]}]
    paire["rejected"] = [{"role": "assistant", "content": "<r-factice>", "tool_calls": [appel()]}]
    vus: list[tuple[Any, Any]] = []
    tok = factices.Tokenizer()
    rendre = tok.apply_chat_template

    def espion(messages, *, tools=None, **kwargs):
        vus.append((messages, tools))
        return rendre(messages, tools=tools, **kwargs)

    tok.apply_chat_template = espion
    if config.decoupage_masque == "par-tour":

        def faux(tokenizer, messages, debut, *, tools, config):
            vus.append((messages, tools))
            return "<amorce-factice>", "<corps-factice>"

        monkeypatch.setattr(chargement, "amorce_et_corps", faux)
        monkeypatch.setattr(chargement, "apply_chat_template", lambda *a, **k: "<amorce-factice>")
    chargement.preparer_preferences(
        tok, [chargement._Paire.model_validate(paire)], config_modele=config
    )
    avec_appels = [(m, t) for m, t in vus if any(x.get("tool_calls") for x in m)]
    assert len(avec_appels) >= 2  # chosen et rejected
    for messages, tools in avec_appels:
        verifier(messages, tools)


def test_minicpm5_template_qui_lit_items_sur_les_arguments(factices) -> None:
    """Sans poids : un template qui appelle `.items()` échouait sur une chaîne JSON."""

    class TokenizerItems(type(factices.Tokenizer())):
        def apply_chat_template(self, messages, **kwargs):
            for m in messages:
                for a in m.get("tool_calls") or []:
                    list(a["function"]["arguments"].items())  # AttributeError sur une chaîne
            return super().apply_chat_template(messages, **kwargs)

    chargement.pretokeniser(
        TokenizerItems(),
        [chargement._Ligne.model_validate(conversation_rd(factices))],
        longueur_max=10_000,
        config_modele=charger_config_modele("granite-4.0-1b"),
    )


def test_rendu_outils_dans_les_invariants() -> None:
    assert "rendu_outils" in run.CLES_INVARIANTS and run.VERSION_RENDU_OUTILS == 1
