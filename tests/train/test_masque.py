"""Rendu et masque de perte (story 10.2, H-MASQUE).

Les tests unitaires utilisent un tokenizer factice (aucun `transformers`). Les tests sur les
tokenizers réels des candidats (`models/`) et sur `llama-server --jinja` sont marqués `lent`
et sautés si les fichiers ou `transformers` manquent. Les contenus sont factices.
"""

from __future__ import annotations

import json
import os
import random
import re
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from slmsp.core.config import dossier_modeles
from slmsp.core.erreurs import ManifesteInvalide
from slmsp.core.schemas.config_modele import ConfigModele
from slmsp.fetch.config import charger_config_modele
from slmsp.train import chargement
from slmsp.train.masque import (
    IGNORE,
    ErreurMasque,
    calculer_masque,
    calculer_masques,
    empreinte_decoupage,
    intervalles_assistant,
    texte_non_masque,
)
from slmsp.train.rendu import apply_chat_template, kwargs_template

JETON = re.compile(r"<\|[a-z_]+\|>|\w+|\s+|[^\w\s]")


class TokenizerFactice:
    """Template de type ChatML ; un token = balise, mot, espaces ou ponctuation."""

    def __init__(self, *, reecrit_historique: bool = False, jeton_colle: bool = False) -> None:
        self.vocab: dict[str, int] = {}
        self.appels: list[dict[str, Any]] = []
        self.reecrit_historique = reecrit_historique
        self.jeton_colle = jeton_colle

    def apply_chat_template(
        self, messages, *, tools=None, tokenize=False, add_generation_prompt=False, **kwargs
    ):
        self.appels.append({"tools": tools, "kwargs": kwargs})
        sortie = ""
        if tools:
            sortie += "<|tools|>" + json.dumps(tools) + "<|end|>\n"
        if kwargs.get("avec_amorce"):
            sortie += "<|amorce|>\n"
        dernier = len(messages) - 1
        for i, m in enumerate(messages):
            contenu = m.get("content") or ""
            if self.reecrit_historique and m["role"] == "assistant" and i < dernier:
                contenu = ""
            sortie += f"<|{m['role']}|>" + contenu
            for appel in m.get("tool_calls") or []:
                sortie += "<|call|>" + json.dumps(appel["function"], sort_keys=True)
            sortie += "<|end|>\n"
        if add_generation_prompt:
            sortie += "<|assistant|>"
        return sortie

    def __call__(self, texte, *, add_special_tokens=False, return_offsets_mapping=False):
        ids, offsets = [], []
        for m in JETON.finditer(texte):
            fin = m.end() + 1 if self.jeton_colle and m.group() == "<|assistant|>" else m.end()
            offsets.append((m.start(), fin))
            ids.append(self.vocab.setdefault(texte[m.start() : fin], len(self.vocab)))
        return {"input_ids": ids, "offset_mapping": offsets}

    def decode(self, ids):
        inverse = {v: k for k, v in self.vocab.items()}
        return "".join(inverse[i] for i in ids)


def conversation() -> list[dict[str, Any]]:
    appel = {"id": "c1", "type": "function", "function": {"name": "outil", "arguments": {"q": "x"}}}
    return [
        {"role": "system", "content": "<système-factice>"},
        {"role": "user", "content": "<question-factice-1>"},
        {"role": "assistant", "content": "", "tool_calls": [appel]},
        {"role": "tool", "tool_call_id": "c1", "content": "<résultat-factice>"},
        {"role": "assistant", "content": "<réponse-factice-1>"},
        {"role": "user", "content": "<question-factice-2>"},
        {"role": "assistant", "content": "<réponse-factice-2>"},
    ]


def attendu(tok: TokenizerFactice, messages) -> str:
    """Tours assistant d'après le rendu : de l'amorce à la fin de tour incluse."""
    sortie = ""
    for k, m in enumerate(messages):
        if m["role"] == "assistant":
            debut = len(apply_chat_template(tok, messages[:k], add_generation_prompt=True))
            sortie += apply_chat_template(tok, messages[: k + 1])[debut:]
    return sortie


def test_labels_seulement_sur_les_tours_assistant() -> None:
    tok = TokenizerFactice()
    messages = conversation()
    rendu = calculer_masque(tok, messages)
    assert len(rendu.input_ids) == len(rendu.labels)
    assert all(e in (IGNORE, i) for e, i in zip(rendu.labels, rendu.input_ids, strict=True))
    gardes = texte_non_masque(tok, rendu)
    assert gardes == attendu(tok, messages)
    assert "<|call|>" in gardes  # appels d'outils sérialisés
    assert gardes.count("<|end|>") == 3  # fin de tour incluse
    assert "<résultat-factice>" not in gardes
    assert "<question-factice-2>" not in gardes
    assert tok.decode(rendu.input_ids) == rendu.texte


def test_aucun_tour_assistant_tout_masque() -> None:
    rendu = calculer_masque(TokenizerFactice(), conversation()[:2])
    assert set(rendu.labels) == {IGNORE}
    assert rendu.tours == []


def test_conversations_aleatoires() -> None:
    tok = TokenizerFactice()
    alea = random.Random(7)
    for n in range(40):
        messages: list[dict[str, Any]] = [{"role": "user", "content": "<question-factice>"}]
        for _ in range(alea.randint(0, 5)):
            role = alea.choice(["assistant", "assistant", "user", "tool"])
            msg: dict[str, Any] = {
                "role": role,
                "content": f"<contenu-factice-{n}-{alea.random()}>",
            }
            if role == "assistant" and alea.random() < 0.5:
                msg["tool_calls"] = [
                    {"function": {"name": "o", "arguments": {"a": alea.randint(0, 9)}}}
                ]
            messages.append(msg)
        rendu = calculer_masque(tok, messages)
        assert texte_non_masque(tok, rendu) == attendu(tok, messages)
        assert rendu.texte == apply_chat_template(tok, messages)


def test_kwargs_et_outils_transmis_au_template() -> None:
    tok = TokenizerFactice()
    config = charger_config_modele("smollm3-3b")
    assert kwargs_template(config) == {"enable_thinking": False}
    assert kwargs_template(None) == {}
    outils = [{"type": "function", "function": {"name": "outil"}}]
    config2 = config.model_copy(update={"chat_template_kwargs": {"avec_amorce": True}})
    rendu = calculer_masque(tok, conversation(), tools=outils, config=config2)
    assert rendu.texte.startswith("<|tools|>")
    assert all(a["kwargs"] == {"avec_amorce": True} and a["tools"] == outils for a in tok.appels)
    assert rendu.labels[0] == IGNORE  # outils et amorce masqués


def test_template_qui_reecrit_l_historique_est_refuse() -> None:
    with pytest.raises(ErreurMasque, match="préfixe"):
        intervalles_assistant(TokenizerFactice(reecrit_historique=True), conversation())


def test_token_a_cheval_sur_une_frontiere_est_refuse() -> None:
    with pytest.raises(ErreurMasque, match="déborde|chevauche"):
        calculer_masque(TokenizerFactice(jeton_colle=True), conversation())


def test_conversation_commencant_par_assistant_refusee() -> None:
    class SansListeVide(TokenizerFactice):
        def apply_chat_template(self, messages, **kw):
            if not messages:
                raise ValueError("liste vide")
            return super().apply_chat_template(messages, **kw)

    with pytest.raises(ErreurMasque, match="amorce"):
        calculer_masque(SansListeVide(), [{"role": "assistant", "content": "<réponse-factice-1>"}])


def test_amorce_non_prefixe_du_rendu_complet_refusee() -> None:
    class Preambule(TokenizerFactice):
        def apply_chat_template(self, messages, *, add_generation_prompt=False, **kw):
            sortie = super().apply_chat_template(
                messages, add_generation_prompt=add_generation_prompt, **kw
            )
            return "<|system|>défaut<|end|>\n" + sortie if not messages else sortie

    with pytest.raises(ErreurMasque, match="préfixe"):
        intervalles_assistant(
            Preambule(), [{"role": "assistant", "content": "<réponse-factice-1>"}]
        )


def test_tokenizer_sans_offsets_refuse() -> None:
    class Lent(TokenizerFactice):
        def __call__(self, texte, **kw):
            raise NotImplementedError("offsets indisponibles")

    with pytest.raises(ErreurMasque, match="positions"):
        calculer_masque(Lent(), conversation())


def test_tour_assistant_vide_refuse() -> None:
    class Vide(TokenizerFactice):
        def apply_chat_template(self, messages, *, add_generation_prompt=False, **kw):
            return "<|user|>x<|end|>\n" + ("<|assistant|>" if add_generation_prompt else "")

    with pytest.raises(ErreurMasque, match="aucun texte"):
        intervalles_assistant(Vide(), [{"role": "user", "content": "x"}, {"role": "assistant"}])


class AmorceRaisonnementVide(TokenizerFactice):
    """Comme MiniCPM5 avec `enable_thinking = false` : l'amorce de génération ajoute un bloc
    de raisonnement vide que le rendu des tours `assistant` n'écrit pas."""

    def apply_chat_template(self, messages, *, add_generation_prompt=False, **kw):
        sortie = super().apply_chat_template(
            messages, add_generation_prompt=add_generation_prompt, **kw
        )
        return sortie + "<think></think>" if add_generation_prompt else sortie


@pytest.mark.parametrize("court", [False, True])  # tour court : « aucun texte » trompeur avant
def test_amorce_absente_du_tour_rendu_refusee(court: bool) -> None:
    messages = (
        [{"role": "user", "content": "q"}, {"role": "assistant", "content": "r"}]
        if court
        else conversation()
    )
    with pytest.raises(ErreurMasque, match="amorce de génération du message .* préfixe"):
        intervalles_assistant(AmorceRaisonnementVide(), messages)


# ---- découpage par tour (spec-masque-minicpm5) ----

BLOC = "<think></think>"


def config_par_tour(bloc: str | None = BLOC) -> ConfigModele:
    return charger_config_modele("minicpm5-1b").model_copy(
        update={"chat_template_kwargs": {}, "bloc_amorce": bloc, "decoupage_masque": "par-tour"}
    )


def appel_factice() -> dict[str, Any]:
    return {"id": "c1", "type": "function", "function": {"name": "outil", "arguments": {}}}


CONVERSATIONS_PAR_TOUR = {
    "systeme-1-tour": [
        {"role": "system", "content": "<système-factice>"},
        {"role": "user", "content": "<question-factice-1>"},
        {"role": "assistant", "content": "<réponse-factice-1>"},
    ],
    "2-tours": [
        {"role": "user", "content": "<question-factice-1>"},
        {"role": "assistant", "content": "<réponse-factice-1>"},
        {"role": "user", "content": "<question-factice-2>"},
        {"role": "assistant", "content": "<réponse-factice-2>"},
    ],
    "systeme-3-tours-outil": conversation(),
    "tour-vide": [
        {"role": "user", "content": "<question-factice-1>"},
        {"role": "assistant", "content": ""},
    ],
    "appel-puis-reponse": [
        {"role": "user", "content": "<question-factice-1>"},
        {"role": "assistant", "content": "", "tool_calls": [appel_factice()]},
        {"role": "tool", "tool_call_id": "c1", "content": "<résultat-factice>"},
        {"role": "assistant", "content": "<réponse-factice-1>"},
    ],
}


def verifier_par_tour(tok: Any, messages, rendus, *, config, bloc: str | None, tools=None):
    """G1 à G4 sur chaque exemple : amorce officielle exacte, corps officiel seul supervisé."""
    tours = [k for k, m in enumerate(messages) if m["role"] == "assistant"]
    assert len(rendus) == len(tours)
    options: dict[str, Any] = {"tools": tools, "config": config}
    for k, rendu in zip(tours, rendus, strict=True):
        amorce = apply_chat_template(tok, messages[:k], add_generation_prompt=True, **options)
        jusque = apply_chat_template(tok, messages[: k + 1], **options)
        ouverture = amorce[: -len(bloc)] if bloc and not jusque.startswith(amorce) else amorce
        corps = jusque[len(ouverture) :]
        assert rendu.texte == amorce + corps  # G1, G2 : égalité exacte, sans retrait
        assert rendu.tours == [(len(amorce), len(rendu.texte))]
        ids_amorce = list(tok(amorce, add_special_tokens=False)["input_ids"])
        n = len(ids_amorce)
        assert rendu.input_ids[:n] == ids_amorce  # G4
        assert set(rendu.labels[:n]) == {IGNORE}
        assert rendu.labels[n:] == rendu.input_ids[n:]
        assert texte_non_masque(tok, rendu) == corps  # G3
        if bloc:
            assert bloc not in corps


@pytest.mark.parametrize("nom", sorted(CONVERSATIONS_PAR_TOUR))
def test_par_tour_amorce_officielle_et_corps_seul(nom: str) -> None:
    tok, config = AmorceRaisonnementVide(), config_par_tour()
    messages = CONVERSATIONS_PAR_TOUR[nom]
    rendus = calculer_masques(tok, messages, config=config)
    verifier_par_tour(tok, messages, rendus, config=config, bloc=BLOC)
    for rendu in rendus:
        assert rendu.texte.count(BLOC) == 1  # seulement dans l'amorce du tour supervisé


def test_par_tour_tour_historique_d_appel_d_outil() -> None:
    """Le tour `tool_calls` est supervisé dans son exemple, et seulement contexte ensuite."""
    tok, config = AmorceRaisonnementVide(), config_par_tour()
    premier, deuxieme, troisieme = calculer_masques(tok, conversation(), config=config)
    assert "<|call|>" in texte_non_masque(tok, premier)
    for rendu in (deuxieme, troisieme):
        debut = rendu.tours[0][0]
        assert "<|call|>" in rendu.texte[:debut]
        assert "<|call|>" not in texte_non_masque(tok, rendu)
        assert BLOC not in rendu.texte[: debut - len(BLOC)]  # historique officiel, sans bloc


def test_par_tour_sans_bloc_quand_le_rendu_prolonge_l_amorce() -> None:
    tok, config = TokenizerFactice(), config_par_tour(None)
    rendus = calculer_masques(tok, conversation(), config=config)
    verifier_par_tour(tok, conversation(), rendus, config=config, bloc=None)


def test_par_tour_accepte_un_template_qui_reecrit_l_historique() -> None:
    """Cas Qwen3.5 : chaque exemple n'utilise que le rendu officiel de son propre préfixe."""
    tok, config = TokenizerFactice(reecrit_historique=True), config_par_tour(None)
    rendus = calculer_masques(tok, conversation(), config=config)
    verifier_par_tour(tok, conversation(), rendus, config=config, bloc=None)


def test_par_tour_outils_et_kwargs_transmis() -> None:
    tok = AmorceRaisonnementVide()
    config = config_par_tour().model_copy(update={"chat_template_kwargs": {"avec_amorce": True}})
    outils = [{"type": "function", "function": {"name": "outil"}}]
    rendus = calculer_masques(tok, conversation(), tools=outils, config=config)
    verifier_par_tour(tok, conversation(), rendus, config=config, bloc=BLOC, tools=outils)
    assert all(a["kwargs"] == {"avec_amorce": True} and a["tools"] == outils for a in tok.appels)


def test_conversation_par_defaut_inchangee() -> None:
    config = charger_config_modele("granite-4.0-1b")
    assert config.decoupage_masque == "conversation" and config.bloc_amorce is None
    (rendu,) = calculer_masques(TokenizerFactice(), conversation(), config=config)
    assert rendu == calculer_masque(TokenizerFactice(), conversation(), config=config)
    assert empreinte_decoupage(config) is None


@pytest.mark.parametrize(
    ("modif", "motif"),
    [
        ({"reasoning_content": "<raisonnement-factice>"}, "reasoning_content"),
        ({"content": "<think>x"}, "balise du bloc"),
        ({"content": "x</think>"}, "balise du bloc"),
    ],
)
def test_par_tour_raisonnement_refuse(modif: dict[str, Any], motif: str) -> None:
    messages = [{"role": "user", "content": "q"}, {"role": "assistant", "content": "r", **modif}]
    config = config_par_tour("<think>\n\n</think>\n\n")
    with pytest.raises(ErreurMasque, match=motif):
        calculer_masques(AmorceRaisonnementVide(), messages, config=config)


@pytest.mark.parametrize("bloc", [None, "<autre-bloc>"])
def test_par_tour_bloc_absent_ou_faux_refuse(bloc: str | None) -> None:
    with pytest.raises(ErreurMasque, match="ouverture du tour introuvable"):
        calculer_masques(AmorceRaisonnementVide(), conversation(), config=config_par_tour(bloc))


def test_par_tour_jeton_a_cheval_refuse() -> None:
    tok = TokenizerFactice(jeton_colle=True)
    with pytest.raises(ErreurMasque, match="chevauche la fin de l'amorce"):
        calculer_masques(tok, conversation(), config=config_par_tour(None))


class DernierJetonMarque(AmorceRaisonnementVide):
    """Le dernier token d'un texte a un identifiant propre : l'amorce seule se tokenise
    autrement qu'au début de l'exemple (G4)."""

    def __call__(self, texte, **kw):
        sortie = super().__call__(texte, **kw)
        sortie["input_ids"][-1] += 10_000
        return sortie


def test_par_tour_tokens_de_l_amorce_differents_refuse() -> None:
    with pytest.raises(ErreurMasque, match="tokens de l'amorce"):
        calculer_masques(DernierJetonMarque(), conversation(), config=config_par_tour())


def test_par_tour_preferences_prompt_officiel_et_corps_seul(factices) -> None:
    tok, config = AmorceRaisonnementVide(), config_par_tour()
    paire = chargement._Paire.model_validate(factices.paire(1))
    (exemple,), _ = chargement.preparer_preferences(tok, [paire], config_modele=config)
    officiel = apply_chat_template(
        tok, paire.prompt, tools=paire.tools, config=config, add_generation_prompt=True
    )
    assert exemple["prompt"] == officiel and officiel.endswith(BLOC)
    assert exemple["chosen"] == "<retenue-factice-1><|end|>\n"
    assert exemple["rejected"] == "<rejetee-factice-1><|end|>\n"


def test_par_tour_preferences_reponse_a_plusieurs_messages_refusee(factices) -> None:
    brut = factices.paire(1)
    brut["chosen"] = [
        {"role": "assistant", "content": "", "tool_calls": [appel_factice()]},
        {"role": "tool", "tool_call_id": "c1", "content": "<résultat-factice>"},
        {"role": "assistant", "content": "<retenue-factice-1>"},
    ]
    paire = chargement._Paire.model_validate(brut)
    with pytest.raises(ManifesteInvalide, match="un seul message assistant"):
        chargement.preparer_preferences(
            AmorceRaisonnementVide(), [paire], config_modele=config_par_tour()
        )


def test_schema_bloc_amorce_exige_par_tour() -> None:
    brut = charger_config_modele("granite-4.0-1b").model_dump()
    with pytest.raises(ValidationError, match="bloc_amorce"):
        ConfigModele.model_validate({**brut, "bloc_amorce": BLOC})
    with pytest.raises(ValidationError):
        ConfigModele.model_validate({**brut, "decoupage_masque": "par-tour", "bloc_amorce": ""})
    fiche = charger_config_modele("minicpm5-1b")
    assert fiche.decoupage_masque == "par-tour"
    assert fiche.bloc_amorce == "<think>\n\n</think>\n\n"
    assert empreinte_decoupage(fiche) == {"mode": "par-tour", "bloc_amorce": fiche.bloc_amorce}
    for slug in ("granite-4.0-1b", "eurollm-1.7b"):
        assert charger_config_modele(slug).decoupage_masque == "conversation"


# ---- tests lents : tokenizers réels et llama-server (jamais dans la suite par défaut) ----

CANDIDATS = [
    "granite-4.0-1b",
    "eurollm-1.7b",
    "minicpm5-1b",  # découpage par tour (spec-masque-minicpm5)
]
"""Candidats au fine-tuning du registre D8 (`entrainable = true`)."""
OUTIL = {
    "type": "function",
    "function": {
        "name": "rechercher",
        "description": "<description-factice>",
        "parameters": {"type": "object", "properties": {"requete": {"type": "string"}}},
    },
}


def conversation_outils() -> list[dict[str, Any]]:
    appel = {
        "id": "call00001",
        "type": "function",
        "function": {"name": "rechercher", "arguments": {"requete": "<q-factice>"}},
    }
    return [
        {"role": "system", "content": "<système-factice>"},
        {"role": "user", "content": "<question-factice-1>"},
        {"role": "assistant", "content": "<réponse-factice-0>", "tool_calls": [appel]},
        {"role": "tool", "tool_call_id": "call00001", "content": "<résultat-factice>"},
        {"role": "assistant", "content": "<réponse-factice-1>"},
    ]


def _dossier_hf(slug: str) -> Path:
    dossier = Path(os.environ.get("SLMSP_MODELS_DIR") or dossier_modeles()) / slug / "hf"
    if not (dossier / "tokenizer_config.json").is_file():
        pytest.skip(f"tokenizer absent : {dossier}")
    return dossier


@pytest.mark.lent
@pytest.mark.parametrize("slug", CANDIDATS)
def test_candidat_reel_masque_sur_les_tours_assistant(slug: str) -> None:
    pytest.importorskip("transformers")
    from slmsp.train.rendu import charger_tokenizer

    tok = charger_tokenizer(_dossier_hf(slug))
    config = charger_config_modele(slug)
    try:
        rendus = calculer_masques(tok, conversation_outils(), tools=[OUTIL], config=config)
    except ErreurMasque as e:  # critère 2 : à consigner, découpage à déclarer dans la fiche
        pytest.fail(f"{slug} : masque impossible avec le template officiel ({e})")
    gardes = "".join(texte_non_masque(tok, rendu) for rendu in rendus)
    assert "<réponse-factice-0>" in gardes
    assert "<réponse-factice-1>" in gardes
    assert "<résultat-factice>" not in gardes
    assert "<question-factice-1>" not in gardes
    assert "<système-factice>" not in gardes
    supervises = sum(e != IGNORE for rendu in rendus for e in rendu.labels)
    print(f"H-MASQUE {slug} : ok, {len(rendus)} exemple(s), {supervises} tokens supervisés")


@pytest.mark.lent
@pytest.mark.parametrize("nom", sorted(CONVERSATIONS_PAR_TOUR))
def test_minicpm5_reel_par_tour_egal_a_l_amorce_officielle(nom: str) -> None:
    """G1 à G4 sur le tokenizer réel de minicpm5-1b (CPU), `enable_thinking = false`."""
    pytest.importorskip("transformers")
    from slmsp.train.rendu import charger_tokenizer

    tok = charger_tokenizer(_dossier_hf("minicpm5-1b"))
    config = charger_config_modele("minicpm5-1b")
    messages = CONVERSATIONS_PAR_TOUR[nom]
    rendus = calculer_masques(tok, messages, tools=[OUTIL], config=config)
    verifier_par_tour(tok, messages, rendus, config=config, bloc=config.bloc_amorce, tools=[OUTIL])
    for rendu in rendus:
        assert rendu.texte.count("<think>") == 1
        assert rendu.texte.endswith("<|im_end|>\n")


@pytest.mark.lent
@pytest.mark.parametrize("slug", ["granite-4.0-1b", "smollm3-3b", "minicpm5-1b"])
def test_rendu_identique_a_llama_server_jinja(slug: str) -> None:
    """Critère 3 : `/apply-template` de `llama-server --jinja` rend le même texte."""
    pytest.importorskip("transformers")
    from slmsp.inference.serveur import ServeurLlama
    from slmsp.train.rendu import charger_tokenizer

    gguf = next((dossier_modeles() / slug / "gguf").glob("*.gguf"), None)
    if gguf is None:
        pytest.skip(f"GGUF absent pour {slug}")
    tok = charger_tokenizer(_dossier_hf(slug))
    config = charger_config_modele(slug)
    messages = conversation_outils()[:4]  # se termine par le message `tool`
    local = apply_chat_template(
        tok, messages, tools=[OUTIL], config=config, add_generation_prompt=True
    )
    with ServeurLlama(config, slug=slug, gguf=gguf) as serveur, serveur.client() as client:
        corps: dict[str, Any] = {"messages": messages, "tools": [OUTIL]}
        if config.chat_template_kwargs:
            corps["chat_template_kwargs"] = config.chat_template_kwargs
        distant = client._post("/apply-template", corps)["prompt"]
    assert local == distant
