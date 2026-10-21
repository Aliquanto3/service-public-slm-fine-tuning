"""Modèle distant dans `eval run` (story 17.1) : fournisseur mocké, aucun appel réel.

Faux OpenRouter en `httpx2.MockTransport` derrière la garde réseau du profil
`eval-distant` ; registre et tarifs dans `tmp_path`. Textes factices seulement (D1).
"""

from __future__ import annotations

import json
import socket
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any

import httpx2  # noqa: TID251 (tests : transport factice)
import pytest
from evaluation_factices import harnais_factice
from pydantic import SecretStr, TypeAdapter, ValidationError

from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.registre import RegistreBudget
from slmsp.cli import main
from slmsp.core.artefacts import ouvrir_run
from slmsp.core.config import charger_toml
from slmsp.core.erreurs import (
    BudgetEpuise,
    CodeSortie,
    ConfigurationInvalide,
    HoteBloque,
    SecretManquant,
)
from slmsp.core.evenements import AppelNonConforme, AppelOutil, Fin, Jeton
from slmsp.core.schemas.run import ModeleRef
from slmsp.evaluation import assemblage
from slmsp.evaluation.assemblage import sans_reseau
from slmsp.evaluation.client_distant import (
    ClientDistant,
    ErreurDistante,
    PlafondGenerationAtteint,
)
from slmsp.evaluation.generation import (
    FICHIER_APPELS_DISTANTS,
    FICHIER_GENERATIONS,
    lancer_generation,
    reprendre_generation,
)
from slmsp.evaluation.modele_distant import FicheDistante, resoudre_distant
from slmsp.evaluation.modele_ref import resoudre
from slmsp.net.config import charger_config_reseau, charger_liste_blanche
from slmsp.net.journal import JournalMemoire
from slmsp.net.profils import evaluer, hote_de

REF = "distant:qwen3.6-27b"
MODELE_ID = "qwen/qwen3.6-27b"
HEBERGEUR = "DeepInfra"
CLE = "sk-or-factice-0000"
URL = "https://openrouter.ai/api/v1/chat/completions"
ITEMS = ("Q-001", "CR-001", "RD-001")
OUTIL = {"type": "function", "function": {"name": "search_datasets", "parameters": {}}}

TARIFS = f"""
schema_version = 1

[taux_usd_eur]
valeur = 1.0
date = 2026-10-21
source = "test"

[modeles."{MODELE_ID}"]
devise = "USD"
date = 2026-10-21
source = "test"

[modeles."{MODELE_ID}".modes.direct]
entree = 0.25
sortie = 2.0
"""


def texte_budgets(plafond: float) -> str:
    return f"""
schema_version = 1
campagne_id = "campagne-test-distant"
marge_eur = 0.0
majoration_entree = 1.25

[postes.openrouter]
plafond_eur = {plafond}

[imputations]
eval-distant = "openrouter"
"""


def registre(dossier: Path, plafond: float = 10.0) -> RegistreBudget:
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "budgets.toml").write_text(texte_budgets(plafond), encoding="utf-8")
    (dossier / "tarifs.toml").write_text(TARIFS, encoding="utf-8")
    return RegistreBudget(
        charger_budgets(dossier / "budgets.toml"),
        charger_tarifs(dossier / "tarifs.toml"),
        dossier / "budget.sqlite",
    )


def reservations(reg: RegistreBudget) -> list[dict[str, Any]]:
    with closing(sqlite3.connect(reg.chemin)) as connexion:
        connexion.row_factory = sqlite3.Row
        return [dict(r) for r in connexion.execute("SELECT * FROM reservations ORDER BY id")]


# --- Faux OpenRouter en SSE ---------------------------------------------------------------------


def sse(
    texte: str = "<réponse-factice-1>",
    *,
    provider: str | None = HEBERGEUR,
    model: str = MODELE_ID,
    finish: str | None = "stop",
    usage: tuple[int, int] | None = (100, 20),
    outils: list[dict[str, Any]] | None = None,
    done: bool = True,
) -> list[str]:
    """Lignes SSE : commentaire, jetons en deux morceaux, fragments d'outils, usage."""
    base: dict[str, Any] = {"id": "gen-factice", "model": model}
    if provider is not None:
        base["provider"] = provider
    lignes = [": OPENROUTER PROCESSING", ""]
    for morceau in (texte[:5], texte[5:]):
        if morceau:
            choix = {"index": 0, "delta": {"content": morceau}}
            lignes += [f"data: {json.dumps({**base, 'choices': [choix]})}", ""]
    for fragment in outils or []:
        choix = {"index": 0, "delta": {"tool_calls": [fragment]}}
        lignes += [f"data: {json.dumps({**base, 'choices': [choix]})}", ""]
    if finish is not None:
        fin: dict[str, Any] = {
            **base,
            "choices": [{"index": 0, "delta": {}, "finish_reason": finish}],
        }
        lignes += [f"data: {json.dumps(fin)}", ""]
    if usage is not None:
        u = {"prompt_tokens": usage[0], "completion_tokens": usage[1], "total_tokens": sum(usage)}
        lignes += [f"data: {json.dumps({**base, 'choices': [], 'usage': u})}", ""]
    if done:
        lignes += ["data: [DONE]", ""]
    return lignes


class FauxOpenRouter:
    """File de réponses : `int` (statut HTTP), `(int, entêtes)`, liste de lignes SSE, ou
    `("coupe", lignes)` pour un flux coupé après ces lignes. File vide : `sse()`."""

    def __init__(self, *reponses: Any) -> None:
        self.reponses = list(reponses)
        self.requetes: list[Any] = []

    def corps(self) -> list[dict[str, Any]]:
        return [json.loads(r.content) for r in self.requetes]

    def __call__(self, requete: Any) -> Any:
        self.requetes.append(requete)
        spec = self.reponses.pop(0) if self.reponses else sse()
        if isinstance(spec, int):
            return httpx2.Response(spec, json={"error": {"message": "<erreur-factice>"}})
        if isinstance(spec, tuple) and isinstance(spec[0], int):
            return httpx2.Response(spec[0], headers=spec[1], json={"error": {}})
        if isinstance(spec, tuple) and spec[0] == "coupe":
            lignes = spec[1]

            def flux() -> Iterator[bytes]:
                for ligne in lignes:
                    yield (ligne + "\n").encode("utf-8")
                raise httpx2.ReadError("coupure factice")

            return httpx2.Response(200, content=flux())
        return httpx2.Response(200, content="\n".join(spec).encode("utf-8"))


@pytest.fixture
def reg(tmp_path: Path) -> RegistreBudget:
    return registre(tmp_path / "budget")


def client(
    reg: RegistreBudget, faux: FauxOpenRouter, *, plafond: float = 5.0, dormir: Any = None
) -> ClientDistant:
    from slmsp.net import client as client_reseau

    http = client_reseau(
        "eval-distant",
        transport_interne=httpx2.MockTransport(faux),
        journal=JournalMemoire(),
    )
    return ClientDistant(
        resoudre_distant(REF),
        reg,
        http,
        SecretStr(CLE),
        plafond_eur=plafond,
        dormir=dormir or (lambda _s: None),
    )


def consommer(llm: ClientDistant, **kw: Any) -> list[Any]:
    messages = [{"role": "user", "content": "<question-factice>"}]
    return list(
        llm.generer(messages, options={"temperature": 0.0, "seed": 42, "max_tokens": 64}, **kw)
    )


# --- Référence et fiche --------------------------------------------------------------------------


def test_reference_distante_et_fiches() -> None:
    TypeAdapter(ModeleRef).validate_python(REF)
    with pytest.raises(ValidationError):
        TypeAdapter(ModeleRef).validate_python("distant:Qwen/3")
    qwen = resoudre_distant(REF)
    assert (qwen.fiche.modele_id, qwen.fiche.hebergeur, qwen.fiche.quantification) == (
        MODELE_ID,
        HEBERGEUR,
        "fp8",
    )
    assert qwen.slug_run == "distant-qwen3.6-27b" and len(qwen.sha256) == 64
    mistral = resoudre_distant("distant:mistral-small-4")
    assert (mistral.fiche.modele_id, mistral.fiche.hebergeur) == (
        "mistralai/mistral-small-2603",
        "Mistral",
    )
    with pytest.raises(ConfigurationInvalide):
        resoudre_distant("distant:inconnu")
    with pytest.raises(ValueError, match="modèle distant"):
        resoudre(REF, "q4_k_m")


@pytest.mark.parametrize(
    "ligne",
    [
        'fournisseur = "autre"',
        'reasoning = "on"',
        'protocole_outils = "json-generique"',
        "contexte = 0",
        'cle_inconnue = "x"',
    ],
)
def test_fiche_invalide_refusee(tmp_path: Path, ligne: str) -> None:
    valeurs = {
        "schema_version": "1",
        "fournisseur": '"openrouter"',
        "modele_id": f'"{MODELE_ID}"',
        "hebergeur": f'"{HEBERGEUR}"',
        "quantification": '"fp8"',
        "protocole_outils": '"natif"',
        "reasoning": '"off"',
        "contexte": "1000",
    }
    cle, _, valeur = ligne.partition(" = ")
    valeurs[cle] = valeur
    fiche = tmp_path / "fiche.toml"
    fiche.write_text("\n".join(f"{k} = {v}" for k, v in valeurs.items()), encoding="utf-8")
    with pytest.raises(ConfigurationInvalide):
        charger_toml(fiche, FicheDistante)


# --- Corps et flux -------------------------------------------------------------------------------


def test_corps_de_requete(reg: RegistreBudget) -> None:
    faux = FauxOpenRouter()
    llm = client(reg, faux)
    consommer(llm, tools=[OUTIL])
    (corps,) = faux.corps()
    assert corps["model"] == MODELE_ID
    assert (corps["temperature"], corps["seed"], corps["max_tokens"]) == (0.0, 42, 64)
    assert corps["stream"] is True and corps["tools"] == [OUTIL]
    assert corps["provider"] == {
        "order": [HEBERGEUR],
        "allow_fallbacks": False,
        "require_parameters": True,
        "data_collection": "deny",
        "quantizations": ["fp8"],
    }
    assert corps["reasoning"] == {"enabled": False}
    assert corps["usage"] == {"include": True}
    requete = faux.requetes[0]
    assert str(requete.url) == URL and requete.headers["Authorization"] == f"Bearer {CLE}"
    with pytest.raises(ValueError, match="options inconnues"):
        llm.generer([], options={"inconnue": 1})


def test_flux_jetons_commentaires_outils_fragmentes(reg: RegistreBudget) -> None:
    fragments = [
        {"index": 0, "id": "call-1", "function": {"name": "search_datasets", "arguments": '{"qu'}},
        {"index": 0, "function": {"arguments": 'ery": "<terme-factice>"}'}},
        {"index": 1, "function": {"name": "search_datasets", "arguments": "{illisible"}},
    ]
    llm = client(reg, FauxOpenRouter(sse(outils=fragments, finish="tool_calls")))
    evenements = consommer(llm, tools=[OUTIL])
    assert "".join(e.texte for e in evenements if isinstance(e, Jeton)) == "<réponse-factice-1>"
    appels = [e for e in evenements if isinstance(e, AppelOutil | AppelNonConforme)]
    assert appels[0] == AppelOutil(
        id="call-1", nom="search_datasets", arguments={"query": "<terme-factice>"}
    )
    assert isinstance(appels[1], AppelNonConforme)
    fin = evenements[-1]
    assert isinstance(fin, Fin) and fin.raison == "terminee"
    assert fin.usage is not None and fin.usage["prompt_tokens"] == 100
    releves, code = llm.vider()
    (releve,) = releves
    assert code is None and releve["statut"] == "ok"
    assert releve["hebergeur_effectif"] == HEBERGEUR and releve["quantification"] == "fp8"
    assert releve["finish_reason"] == "tool_calls" and releve["usage"]["completion_tokens"] == 20
    assert releve["cout_eur"] == pytest.approx((100 * 0.25 + 20 * 2.0) / 1e6)
    assert releve["delai_premier_token_ms"] is not None


def test_troncature_length(reg: RegistreBudget) -> None:
    evenements = consommer(client(reg, FauxOpenRouter(sse(finish="length"))))
    assert isinstance(evenements[-1], Fin) and evenements[-1].raison == "longueur"


@pytest.mark.parametrize(
    ("reponse", "code"),
    [
        (sse(provider="AutreHebergeur"), "hebergeur_inattendu"),
        (sse(provider=None), "hebergeur_inattendu"),
        (sse(model="qwen/autre-modele"), "modele_inattendu"),
        (sse(finish="error"), "erreur_flux"),
        (sse(finish=None, done=False), "flux_coupe"),
        (("coupe", sse(finish=None, usage=None, done=False)[:4]), "flux_coupe"),
        (400, "http-400"),
    ],
)
def test_erreurs_d_item(reg: RegistreBudget, reponse: Any, code: str) -> None:
    llm = client(reg, FauxOpenRouter(reponse))
    with pytest.raises(ErreurDistante) as erreur:
        consommer(llm)
    assert erreur.value.code == code
    releves, code_vu = llm.vider()
    assert code_vu == code and releves[-1]["erreur"] == code
    assert llm.erreur_fatale is None
    (ligne,) = reservations(reg)
    assert ligne["etat"] != "reservee"  # toujours réglée


def test_hebergeur_inattendu_coute_au_pire_cas_sans_usage(reg: RegistreBudget) -> None:
    llm = client(reg, FauxOpenRouter(sse(provider="AutreHebergeur", usage=None)))
    with pytest.raises(ErreurDistante):
        consommer(llm)
    (ligne,) = reservations(reg)
    assert ligne["etat"] == "pire-cas"


def test_relances_429_avant_premier_octet(reg: RegistreBudget) -> None:
    attentes: list[float] = []
    faux = FauxOpenRouter((429, {"Retry-After": "7"}), 503, sse())
    llm = client(reg, faux, dormir=attentes.append)
    evenements = consommer(llm)
    assert isinstance(evenements[-1], Fin) and len(faux.requetes) == 3
    assert attentes[0] == 7.0 and len(attentes) == 2
    lignes = reservations(reg)
    assert len(lignes) == 3
    assert [round(ligne["montant_reel_eur"] or 0.0, 9) for ligne in lignes[:2]] == [0.0, 0.0]
    assert llm.vider()[0][0]["relances"] == 2


def test_relances_epuisees(reg: RegistreBudget) -> None:
    llm = client(reg, FauxOpenRouter(429, 429, 429, 429))
    with pytest.raises(ErreurDistante, match="http-429"):
        consommer(llm)
    assert len(reservations(reg)) == 4


@pytest.mark.parametrize(
    "delta",
    [
        "texte-nu",
        {"tool_calls": ["fragment-non-objet"]},
        {"tool_calls": [{"index": "zero", "function": {"name": "f"}}]},
        {"tool_calls": [{"index": 0, "function": "non-objet"}]},
    ],
)
def test_morceau_sse_mal_forme(reg: RegistreBudget, delta: Any) -> None:
    lignes = sse()
    morceau = {"model": MODELE_ID, "provider": HEBERGEUR, "choices": [{"delta": delta}]}
    lignes.insert(2, f"data: {json.dumps(morceau)}")
    llm = client(reg, FauxOpenRouter(lignes))
    with pytest.raises(ErreurDistante) as erreur:
        consommer(llm)
    assert erreur.value.code == "flux_invalide"
    assert llm.vider()[0][-1]["erreur"] == "flux_invalide"
    (ligne,) = reservations(reg)
    assert ligne["etat"] != "reservee"


def test_retry_after_plafonne(reg: RegistreBudget) -> None:
    attentes: list[float] = []
    faux = FauxOpenRouter((429, {"Retry-After": "86400"}), sse())
    consommer(client(reg, faux, dormir=attentes.append))
    assert attentes == [60.0]


def test_lecture_abandonnee_reglee_au_pire_cas(reg: RegistreBudget) -> None:
    llm = client(reg, FauxOpenRouter(sse()))
    flux = llm.generer([{"role": "user", "content": "<question-factice>"}])
    assert isinstance(next(flux), Jeton)
    flux.close()
    (ligne,) = reservations(reg)
    assert ligne["etat"] == "pire-cas"
    assert llm.vider()[0][-1]["erreur"] == "abandon"


def test_budget_epuise_fatal(tmp_path: Path) -> None:
    petit = registre(tmp_path / "petit", plafond=0.0001)
    faux = FauxOpenRouter()
    llm = client(petit, faux)
    with pytest.raises(BudgetEpuise):
        consommer(llm)
    assert isinstance(llm.erreur_fatale, BudgetEpuise) and not faux.requetes


def test_plafond_de_generation_fatal(reg: RegistreBudget) -> None:
    faux = FauxOpenRouter()
    llm = client(reg, faux, plafond=0.0001)
    with pytest.raises(PlafondGenerationAtteint):
        consommer(llm)
    assert isinstance(llm.erreur_fatale, PlafondGenerationAtteint)
    assert not faux.requetes and not reservations(reg)


def test_client_distant_verifie_cle_avant_tout(tmp_path: Path, reg: RegistreBudget) -> None:
    with pytest.raises(SecretManquant):
        assemblage.client_distant(
            resoudre_distant(REF), 1.0, registre=reg, fichier_env=tmp_path / "absent.env"
        )
    env = tmp_path / ".env"
    env.write_text(f"OPENROUTER_API_KEY={CLE}\n", encoding="utf-8")
    llm = assemblage.client_distant(resoudre_distant(REF), 1.0, registre=reg, fichier_env=env)
    assert llm.plafond_eur == 1.0


# --- Réseau --------------------------------------------------------------------------------------


def test_profil_eval_distant() -> None:
    config, liste = charger_config_reseau(), charger_liste_blanche()

    def verdict(profil: str, methode: str, url: str) -> bool:
        return evaluer(profil, methode, url, mode=None, config=config, liste_blanche=liste).autorise

    assert verdict("eval-distant", "POST", URL)
    assert not verdict("eval-distant", "GET", "https://openrouter.ai/api/v1/models")
    assert not verdict("aucun", "POST", URL)


def test_sans_reseau_hote_du_fournisseur_seulement(monkeypatch: pytest.MonkeyPatch) -> None:
    resolus: list[Any] = []

    def resolution(hote: Any, *args: Any, **kwargs: Any) -> Any:
        resolus.append(hote)
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("198.51.100.7", 443))]

    monkeypatch.setattr(socket, "getaddrinfo", resolution)
    tentees: list[Any] = []
    monkeypatch.setattr(socket.socket, "connect", lambda self, adresse: tentees.append(adresse))
    with sans_reseau(("openrouter.ai",), "eval-distant") as bloquees:
        socket.getaddrinfo("openrouter.ai", 443)
        with socket.socket() as s:
            s.connect(("198.51.100.7", 443))
            with pytest.raises(HoteBloque, match="eval-distant"):
                s.connect(("192.0.2.1", 443))
        with pytest.raises(HoteBloque):
            socket.getaddrinfo("api.mistral.ai", 443)
    assert tentees == [("198.51.100.7", 443)] and len(bloquees) == 2
    with sans_reseau() as bloquees:  # référence locale : aucun hôte admis
        with pytest.raises(HoteBloque, match="aucun"):
            socket.getaddrinfo("openrouter.ai", 443)


# --- Run de génération ---------------------------------------------------------------------------


class FabriqueDistante:
    """Harnais factice (embedding et Index factices) avec un vrai `ClientDistant` mocké."""

    def __init__(self, reg: RegistreBudget, faux: FauxOpenRouter) -> None:
        self.reg = reg
        self.faux = faux
        self.appels: list[tuple[Any, ...]] = []

    @contextmanager
    def __call__(
        self, modele: Any, racine: Path, plafond: float, cout_deja: float
    ) -> Iterator[Any]:
        self.appels.append((modele.ref, plafond, cout_deja))
        llm = client(self.reg, self.faux, plafond=plafond)
        llm.cout_cumule_eur = cout_deja
        harnais = harnais_factice(llm)
        harnais.chat_template_sha256 = None
        harnais.llamacpp_tag = None
        harnais.profil_reseau = "eval-distant"
        harnais.hotes_autorises = ("openrouter.ai",)
        harnais.distant = llm
        harnais.description = {"generation": {"modele_id": MODELE_ID}, "embedding": {}}
        yield harnais


def lancer(depot: Path, fabrique: FabriqueDistante, plafond: float = 5.0) -> Any:
    return lancer_generation(
        REF,
        None,
        "v1.0",
        items=ITEMS,
        racine=depot,
        fabrique_distante=fabrique,
        plafond_generation_eur=plafond,
    )


def test_run_distant_manifeste_et_releves(depot_eval: Path, reg: RegistreBudget) -> None:
    fabrique = FabriqueDistante(reg, FauxOpenRouter())
    rapport = lancer(depot_eval, fabrique)
    assert rapport.statut == "complet" and rapport.ok == len(ITEMS)
    run = rapport.run
    brut = json.loads((run.dossier / "run.json").read_text(encoding="utf-8"))
    assert brut["modele_ref"] == REF
    for champ in ("quantification", "variante_llamacpp", "llamacpp_tag", "chat_template_sha256"):
        assert brut[champ] is None
    assert brut["config"]["profil_reseau"] == "eval-distant"
    assert brut["config"]["modele_distant"]["sha256"] == brut["entrees"]["modele"]
    assert brut["config"]["modele_distant"]["hebergeur"] == HEBERGEUR
    assert run.run_id.split("-", 2)[2].startswith("distant-qwen3.6-27b")
    releves = run.lire_jsonl(FICHIER_APPELS_DISTANTS)
    assert {r["item_id"] for r in releves} == set(ITEMS)
    assert all(r["hebergeur_effectif"] == HEBERGEUR and r["cout_eur"] > 0 for r in releves)
    assert reservations(reg) and all(r["etat"] == "regularisee" for r in reservations(reg))


def test_hebergeur_inattendu_puis_reprise(depot_eval: Path, reg: RegistreBudget) -> None:
    faux = FauxOpenRouter(sse(provider="AutreHebergeur"))
    fabrique = FabriqueDistante(reg, faux)
    rapport = lancer(depot_eval, fabrique)
    assert rapport.statut == "partiel-erreur" and rapport.erreur == 1
    run_id = rapport.run.run_id
    lignes = rapport.run.lire_jsonl(FICHIER_GENERATIONS)
    en_erreur = [g for g in lignes if g["statut"] == "erreur"]
    (premier,) = [g["item_id"] for g in en_erreur]
    assert en_erreur[0]["trace"][-1]["code"] == "hebergeur_inattendu"

    with pytest.raises(ValueError, match="plafond-generation"):
        reprendre_generation(run_id, racine=depot_eval, fabrique_distante=fabrique)
    reprise = reprendre_generation(
        run_id, racine=depot_eval, fabrique_distante=fabrique, plafond_generation_eur=5.0
    )
    assert reprise.statut == "complet" and (reprise.ok, reprise.sautes) == (1, 2)
    toutes = ouvrir_run(run_id, racine=depot_eval).lire_jsonl(FICHIER_GENERATIONS)
    assert [g["item_id"] for g in toutes].count(premier) == 2 and toutes[-1]["statut"] == "ok"
    assert fabrique.appels[-1][2] > 0  # coût déjà réglé transmis au plafond


def test_plafond_interrompt_puis_reprise(depot_eval: Path, reg: RegistreBudget) -> None:
    fabrique = FabriqueDistante(reg, FauxOpenRouter())
    with pytest.raises(PlafondGenerationAtteint):
        lancer(depot_eval, fabrique, plafond=0.0001)
    (dossier,) = (depot_eval / "runs" / "eval-generation").iterdir()
    run = ouvrir_run(dossier.name, racine=depot_eval)
    assert run.statut_courant() == "interrompu"
    assert run.lire_jsonl(FICHIER_GENERATIONS) == []
    reprise = reprendre_generation(
        run.run_id, racine=depot_eval, fabrique_distante=fabrique, plafond_generation_eur=5.0
    )
    assert reprise.statut == "complet" and reprise.ok == len(ITEMS)


def test_budget_epuise_interrompt(depot_eval: Path, tmp_path: Path) -> None:
    fabrique = FabriqueDistante(registre(tmp_path / "petit", plafond=0.0001), FauxOpenRouter())
    with pytest.raises(BudgetEpuise):
        lancer(depot_eval, fabrique)
    (dossier,) = (depot_eval / "runs" / "eval-generation").iterdir()
    assert ouvrir_run(dossier.name, racine=depot_eval).statut_courant() == "interrompu"


def test_reprise_refuse_fiche_modifiee(
    depot_eval: Path, reg: RegistreBudget, monkeypatch: pytest.MonkeyPatch
) -> None:
    from slmsp.core.erreurs import ManifesteInvalide
    from slmsp.evaluation import generation

    fabrique = FabriqueDistante(reg, FauxOpenRouter(sse(provider="Autre")))
    run_id = lancer(depot_eval, fabrique).run.run_id
    monkeypatch.setattr(generation, "sha256_fichier", lambda _chemin: "0" * 64)
    with pytest.raises(ManifesteInvalide, match="modifiée"):
        reprendre_generation(
            run_id, racine=depot_eval, fabrique_distante=fabrique, plafond_generation_eur=5.0
        )


@pytest.mark.parametrize(
    ("options", "motif"),
    [
        ({}, "plafond-generation"),
        ({"plafond_generation_eur": 1.0, "quantification": "q4_k_m"}, "quantification"),
        ({"plafond_generation_eur": 1.0, "variante": "cuda"}, "variante"),
    ],
)
def test_usage_distant(depot_eval: Path, options: dict[str, Any], motif: str) -> None:
    quantification = options.pop("quantification", None)
    with pytest.raises(ValueError, match=motif):
        lancer_generation(REF, quantification, "v1.0", racine=depot_eval, **options)


def test_plafond_generation_refuse_en_local(depot_eval: Path) -> None:
    with pytest.raises(ValueError, match="réservé"):
        lancer_generation(
            "base:granite-4.0-1b", "q4_k_m", "v1.0", racine=depot_eval, plafond_generation_eur=1.0
        )


def test_cli_distant(depot_eval: Path, capsys: pytest.CaptureFixture[str]) -> None:
    base = ["eval", "run", "--modele", REF, "--jeu", "v1.0", "--phase", "generation"]
    racine = ["--racine", str(depot_eval)]
    assert main([*base, *racine]) == int(CodeSortie.USAGE)
    assert "--plafond-generation" in capsys.readouterr().err
    code = main([*base, "--quantification", "q4_k_m", "--plafond-generation", "1", *racine])
    assert code == int(CodeSortie.USAGE)
    assert "--quantification" in capsys.readouterr().err
    code = main(
        ["eval", "run", "--modele", "base:granite-4.0-1b", "--quantification", "q4_k_m",
         "--jeu", "v1.0", "--phase", "generation", "--plafond-generation", "1", *racine]
    )  # fmt: skip
    assert code == int(CodeSortie.USAGE)


def test_bench_refuse_distant(tmp_path: Path) -> None:
    from slmsp.benchmarks.orchestrateur import lancer as lancer_bench

    with pytest.raises(ConfigurationInvalide, match="distant"):
        lancer_bench(REF, [], racine=tmp_path)


# --- Fournisseurs mistral et ovh (story 17.1b) ---------------------------------------------------

MISTRAL_ID = "mistral-small-2603"
OVH_ID = "Qwen3.6-27B"
URL_MISTRAL = "https://api.mistral.ai/v1/chat/completions"
URL_OVH = "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1/chat/completions"

BUDGETS_MULTI = """
schema_version = 1
campagne_id = "campagne-test-fournisseurs"
marge_eur = 0.0
majoration_entree = 1.25

[postes.openrouter]
plafond_eur = 10.0

[postes.mistral]
plafond_eur = 10.0

[postes.mistral.sous_postes]
generation = 8.0
juge = 2.0
"""


def registre_multi(dossier: Path, *, ovh: bool = False) -> RegistreBudget:
    """Postes openrouter, mistral (sous-postes) et, si `ovh`, un poste ovh de test."""
    dossier.mkdir(parents=True, exist_ok=True)
    budgets = BUDGETS_MULTI
    if ovh:
        budgets += "\n[postes.ovh]\nplafond_eur = 10.0\n"
    budgets += '\n[imputations]\neval-distant = "openrouter"\n'
    budgets += 'eval-distant-mistral = "mistral.generation"\n'
    if ovh:
        budgets += 'eval-distant-ovh = "ovh"\n'
    tarifs = TARIFS
    for modele in (MISTRAL_ID, OVH_ID):
        tarifs += (
            f'\n[modeles."{modele}"]\ndevise = "USD"\ndate = 2026-10-21\nsource = "test"\n'
            f'\n[modeles."{modele}".modes.direct]\nentree = 0.15\nsortie = 0.6\n'
        )
    (dossier / "budgets.toml").write_text(budgets, encoding="utf-8")
    (dossier / "tarifs.toml").write_text(tarifs, encoding="utf-8")
    return RegistreBudget(
        charger_budgets(dossier / "budgets.toml"),
        charger_tarifs(dossier / "tarifs.toml"),
        dossier / "budget.sqlite",
    )


def client_ref(ref: str, reg: RegistreBudget, faux: FauxOpenRouter) -> ClientDistant:
    from slmsp.net import client as client_reseau

    http = client_reseau(
        "eval-distant", transport_interne=httpx2.MockTransport(faux), journal=JournalMemoire()
    )
    return ClientDistant(resoudre_distant(ref), reg, http, SecretStr(CLE), plafond_eur=5.0)


def consommer_options(llm: ClientDistant) -> list[Any]:
    options = {"temperature": 0.0, "seed": 42, "max_tokens": 64, "top_k": 20}
    messages = [{"role": "user", "content": "<question-factice>"}]
    return list(llm.generer(messages, tools=[OUTIL], options=options))


def test_fiches_mistral_et_ovh() -> None:
    mistral = resoudre_distant("distant:mistral-small-mistral")
    assert (mistral.fiche.fournisseur, mistral.fiche.modele_id) == ("mistral", MISTRAL_ID)
    assert "latest" not in mistral.fiche.modele_id and mistral.fiche.hebergeur is None
    assert mistral.fiche.hebergeur_consigne == "mistral" and not mistral.fiche.epingle
    assert mistral.fournisseur.url("chat/completions") == URL_MISTRAL
    assert mistral.fournisseur.nom_secret == "MISTRAL_API_KEY"
    ovh = resoudre_distant("distant:qwen3.6-27b-ovh")
    assert (ovh.fiche.fournisseur, ovh.fiche.modele_id) == ("ovh", OVH_ID)
    assert ovh.fournisseur.url("chat/completions") == URL_OVH
    assert ovh.fournisseur.nom_secret == "OVH_AI_ENDPOINTS_ACCESS_TOKEN"
    assert resoudre_distant(REF).fiche.epingle


@pytest.mark.parametrize(
    "valeurs",
    [
        {"fournisseur": '"mistral"', "modele_id": f'"{MISTRAL_ID}"', "hebergeur": '"Mistral"'},
        {"fournisseur": '"mistral"', "modele_id": '"mistral-small-latest"'},
        {"fournisseur": '"ovh"', "modele_id": '"Qwen3.6-27B-latest"'},
        {"fournisseur": '"openrouter"', "modele_id": f'"{MODELE_ID}"'},
        {
            "fournisseur": '"openrouter"',
            "modele_id": f'"{MISTRAL_ID}"',
            "hebergeur": '"Mistral"',
            "quantification": '"fp8"',
        },
    ],
)
def test_fiche_selon_fournisseur_refusee(tmp_path: Path, valeurs: dict[str, str]) -> None:
    lignes = {"schema_version": "1", "contexte": "1000", **valeurs}
    fiche = tmp_path / "fiche.toml"
    fiche.write_text("\n".join(f"{k} = {v}" for k, v in lignes.items()), encoding="utf-8")
    with pytest.raises(ConfigurationInvalide):
        charger_toml(fiche, FicheDistante)


def test_corps_mistral_et_imputation(tmp_path: Path) -> None:
    reg = registre_multi(tmp_path / "budget")
    faux = FauxOpenRouter(sse(provider=None, model=MISTRAL_ID))
    llm = client_ref("distant:mistral-small-mistral", reg, faux)
    evenements = consommer_options(llm)
    (corps,) = faux.corps()
    assert str(faux.requetes[0].url) == URL_MISTRAL
    assert corps["model"] == MISTRAL_ID and corps["random_seed"] == 42
    assert (corps["temperature"], corps["max_tokens"], corps["tools"]) == (0.0, 64, [OUTIL])
    for absent in ("seed", "top_k", "provider", "reasoning", "usage", "stream_options"):
        assert absent not in corps
    assert isinstance(evenements[-1], Fin)
    (releve,), code = llm.vider()
    assert code is None and releve["hebergeur_effectif"] == "mistral"
    assert releve["hebergeur_epingle"] is None
    assert releve["cout_eur"] == pytest.approx((100 * 0.15 + 20 * 0.6) / 1e6)
    (reservation,) = reservations(reg)
    assert (reservation["poste"], reservation["sous_poste"]) == ("mistral", "generation")


def test_mistral_modele_renvoye_controle(tmp_path: Path) -> None:
    reg = registre_multi(tmp_path / "budget")
    faux = FauxOpenRouter(sse(provider=None, model="mistral-small-autre"))
    llm = client_ref("distant:mistral-small-mistral", reg, faux)
    with pytest.raises(ErreurDistante, match="modele_inattendu"):
        consommer_options(llm)


def test_corps_ovh(tmp_path: Path) -> None:
    reg = registre_multi(tmp_path / "budget", ovh=True)
    faux = FauxOpenRouter(sse(provider=None, model=OVH_ID))
    llm = client_ref("distant:qwen3.6-27b-ovh", reg, faux)
    consommer_options(llm)
    (corps,) = faux.corps()
    assert str(faux.requetes[0].url) == URL_OVH and corps["model"] == OVH_ID
    assert corps["stream_options"] == {"include_usage": True}
    for absent in ("seed", "random_seed", "top_k", "provider", "reasoning", "usage"):
        assert absent not in corps
    (reservation,) = reservations(reg)
    assert reservation["poste"] == "ovh"


def test_ovh_sans_poste_refuse_avant_tout(tmp_path: Path) -> None:
    reg = registre_multi(tmp_path / "budget")
    ovh = resoudre_distant("distant:qwen3.6-27b-ovh")
    with pytest.raises(ConfigurationInvalide, match="poste budgétaire ovh absent"):
        assemblage.client_distant(ovh, 1.0, registre=reg, fichier_env=tmp_path / "absent.env")
    faux = FauxOpenRouter()
    with pytest.raises(ConfigurationInvalide, match="à approuver par Anaël"):
        client_ref("distant:qwen3.6-27b-ovh", reg, faux)
    assert not faux.requetes and not reservations(reg)


def test_budgets_du_depot_imputent_par_fournisseur() -> None:
    imputations = charger_budgets().imputations
    assert imputations["eval-distant"] == "openrouter"
    assert imputations["eval-distant-mistral"].partition(".")[0] == "mistral"
    assert "eval-distant-ovh" not in imputations
    assert MISTRAL_ID in charger_tarifs().modeles


def test_profil_eval_distant_par_fournisseur() -> None:
    config, liste = charger_config_reseau(), charger_liste_blanche()

    def verdict(methode: str, url: str) -> bool:
        return evaluer(
            "eval-distant", methode, url, mode=None, config=config, liste_blanche=liste
        ).autorise

    assert verdict("POST", URL_MISTRAL) and verdict("POST", URL_OVH)
    assert not verdict("GET", "https://api.mistral.ai/v1/models")
    assert not verdict("POST", "https://api.mistral.ai/v1/agents/completions")
    assert not verdict("POST", "https://api.anthropic.com/v1/messages")
    hotes = {
        ref: hote_de(resoudre_distant(ref).fournisseur.base_url)
        for ref in (REF, "distant:mistral-small-mistral", "distant:qwen3.6-27b-ovh")
    }
    assert hotes == {
        REF: "openrouter.ai",
        "distant:mistral-small-mistral": "api.mistral.ai",
        "distant:qwen3.6-27b-ovh": "oai.endpoints.kepler.ai.cloud.ovh.net",
    }
