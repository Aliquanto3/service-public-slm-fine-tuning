"""Candidats multiples de sélection et juge croisé (story 15.2, O2).

Jeu SFT synthétique, `LlmPort` scripté et faux serveur OpenRouter : tous les textes sont des
chaînes artificielles (`<reponse-factice-1>`), jamais du contenu rédigé (D1). Aucun appel d'API,
aucun modèle réel.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections.abc import Iterator, Sequence
from datetime import date
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from slmsp.budget.config import charger_budgets, charger_tarifs
from slmsp.budget.registre import RegistreBudget
from slmsp.cli import CodeSortie, main
from slmsp.core.artefacts import nouveau_run, ouvrir_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import LectureInterdite, ManifesteInvalide
from slmsp.core.evenements import Fin, Jeton
from slmsp.core.schemas.entrainement import LigneEntrainement, MetaLigne
from slmsp.core.var import dossier_var
from slmsp.data.candidats import (
    NOM_CANDIDATS,
    NOM_ECARTES,
    SOURCES_JUGE_CROISE,
    candidats_depuis_run,
    lancer_candidats,
    texte_candidat,
)
from slmsp.data.config import CandidatsDonnees, JugeDonneesConfig, charger_config_donnees
from slmsp.data.juge_donnees import (
    LISTES_PAR_TACHE,
    NOM_VERDICTS,
    JugeDonnees,
    PlafondEstimeDepasse,
    charger_grilles,
    lancer_jugement,
)
from slmsp.data.nettoyage import Tokeniseur

SLUG = "base-factice"
CLES_SANS_TEXTE = {"session_id", "candidat_id", "source", "tache", "temperature", "graine"}


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
CONFIG = CandidatsDonnees(
    graine=7, max_tokens=64, modele_openrouter=F.MODELE, max_tokens_openrouter=500
)


class LlmScripte:
    """`LlmPort` minimal : une réponse (texte ou événements) par appel ; trace des appels."""

    def __init__(self, *reponses: Any, erreur_apres: int | None = None) -> None:
        self.reponses = list(reponses)
        self.erreur_apres = erreur_apres
        self.appels: list[dict[str, Any]] = []

    def generer(
        self, messages: Sequence[Any], *, tools: Any = None, options: Any = None
    ) -> Iterator[Any]:
        if self.erreur_apres is not None and len(self.appels) >= self.erreur_apres:
            raise RuntimeError("<panne-factice>")
        self.appels.append({"messages": list(messages), "tools": tools, "options": dict(options)})
        reponse = self.reponses[min(len(self.appels), len(self.reponses)) - 1]
        if isinstance(reponse, str):
            reponse = [Jeton(texte=reponse), Fin(raison="terminee")]
        yield from reponse

    def compter_tokens(self, messages: Sequence[Any], tools: Any = None) -> int:
        return 0


def ligne_sft(numero: int, tache: str = "LC") -> LigneEntrainement:
    return LigneEntrainement(
        messages=[
            {"role": "system", "content": f"<prompt-{tache}-factice>"},
            {"role": "user", "content": f"<entree-factice-{numero}>"},
            {"role": "assistant", "content": f"<reponse-factice-{numero}>"},
        ],
        tache=tache,
        meta=MetaLigne(
            generateur="<modele-factice>",
            appel_ids=[f"{numero:032x}"],
            session_id=f"s-{numero:024x}",
            version_gabarit={"<gabarit-factice>": 1},
            version_extracteur=1,
            source=["<source-factice>"],
            licence=["<licence-factice>"],
            date=date(2026, 10, 16),
        ),
    )


def ecrire_jeu(racine: Path, taches: Sequence[str] = ("LC", "LC", "CO")) -> str:
    """Run `data-build` (parent `data-generate` factice) et `data/train/v1` ; renvoie le run."""
    run = nouveau_run("data-build", "build", {"generate_run_id": "g-factice"}, racine=racine)
    run.terminer("complet")
    octets = b"".join(
        json_canonique(ligne_sft(i, t).model_dump(mode="json")) + b"\n"
        for i, t in enumerate(taches, start=1)
    )
    dossier = racine / "data" / "train" / "v1"
    dossier.mkdir(parents=True)
    (dossier / "train.jsonl").write_bytes(octets)
    manifeste = {
        "version": "v1",
        "type_run": "data-build",
        "run_id": run.run_id,
        "variante": "diffusable",
        "sha256_train": sha256_hex(octets),
    }
    (dossier / "MANIFEST.json").write_text(json.dumps(manifeste), encoding="utf-8")
    return run.run_id


PLAFOND = 40
TOKENISEUR = Tokeniseur(compter=len, sha256="0" * 64)  # un caractère = un token (factice)


def lancer(racine: Path, build: str, llm: LlmScripte, **options: Any) -> Any:
    options = {
        "taches": ["LC", "CR"],
        "temperatures": [0.3, 0.7],
        "config": CONFIG,
        **options,
    }
    return lancer_candidats(
        racine=racine,
        build_run_id=build,
        slug=SLUG,
        llm=llm,
        plafond_tokens=PLAFOND,
        tokeniseur=TOKENISEUR,
        consigner=lambda _m: None,
        **options,
    )


def lire(run: Any, nom: str) -> list[dict[str, Any]]:
    return run.lire_jsonl(nom)


def _banc(dossier: Path, plafond: float = 10.0) -> Any:
    return F.banc(dossier, plafond)


# --- Contrat et conversation --------------------------------------------------------------


def test_contrat_candidats_et_conversation_identique(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path)
    llm = LlmScripte("<a-1>", "<b-1>", "<a-2>", "<b-2>")
    resultat = lancer(tmp_path, build, llm)

    assert resultat.statut == "complet"
    candidats = lire(resultat.run, NOM_CANDIDATS)
    # 2 lignes LC x (1 Mistral + 2 températures) ; la ligne CO n'est pas demandée.
    assert len(candidats) == 6
    assert all(CLES_SANS_TEXTE <= set(c) for c in candidats)
    assert not any(
        "<a-1>" in json.dumps(c) or "<reponse-factice" in json.dumps(c) for c in candidats
    )
    mistral = [c for c in candidats if c["source"] == "mistral"]
    assert [c["candidat_id"] for c in mistral] == [f"mistral:{i:032x}" for i in (1, 2)]
    assert all(c["temperature"] is None and c["graine"] is None for c in mistral)
    locaux = [c for c in candidats if c["source"] == f"slm:{SLUG}"]
    assert sorted({c["temperature"] for c in locaux}) == [0.3, 0.7]
    assert all(c["candidat_id"].startswith("slm:") and c["tache"] == "LC" for c in locaux)
    # Conversation d'entraînement exacte (avant la cible), graine = graine + rang.
    attendu = [ligne_sft(1).messages[:-1], ligne_sft(1).messages[:-1], ligne_sft(2).messages[:-1]]
    assert [a["messages"] for a in llm.appels[:3]] == attendu[:1] + attendu[:1] + attendu[2:]
    assert [a["options"]["seed"] for a in llm.appels] == [7, 7, 8, 8]
    assert [a["options"]["temperature"] for a in llm.appels] == [0.3, 0.7, 0.3, 0.7]
    # Journal local : chaque candidat local y a son appel, texte relu et revérifié.
    connexions: dict[str, Any] = {}
    try:
        textes = {
            c["candidat_id"]: texte_candidat(connexions, tmp_path, c["candidat_id"]) for c in locaux
        }
    finally:
        for connexion in connexions.values():
            connexion.close()
    assert sorted(t for t in textes.values() if t) == ["<a-1>", "<a-2>", "<b-1>", "<b-2>"]
    assert ouvrir_run(resultat.run.run_id, racine=tmp_path).type == "data-candidats"


def test_sortie_tronquee_journalisee_mais_exclue(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC",))
    llm = LlmScripte([Jeton(texte="<coupee-factice>"), Fin(raison="longueur")], "<ok-factice>")
    resultat = lancer(tmp_path, build, llm)

    locaux = [c for c in lire(resultat.run, NOM_CANDIDATS) if c["source"].startswith("slm:")]
    assert len(locaux) == 1
    ecartes = lire(resultat.run, NOM_ECARTES)
    assert [e["motif"] for e in ecartes] == ["tronquee"]
    assert resultat.rapport["ecartes_par_motif"] == {"tronquee": 1}
    # Journalisée (statut tronquee) : l'appel existe mais n'est jamais relu comme candidat.
    from slmsp.inference.journal_local import JournalLocal

    ligne = JournalLocal().lire(ecartes[0]["appel_local_id"])
    assert ligne is not None and ligne["statut"] == "tronquee"
    assert texte_candidat({}, tmp_path, f"slm:{ecartes[0]['appel_local_id']}") is None


def test_reprise_ne_regenere_pas(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC", "LC"))
    en_panne = LlmScripte("<a>", "<b>", erreur_apres=2)
    with pytest.raises(RuntimeError):
        lancer(tmp_path, build, en_panne)
    run_id = sorted((tmp_path / "runs" / "data-candidats").iterdir())[0].name
    assert ouvrir_run(run_id, racine=tmp_path).statut_courant() == "partiel-erreur"

    llm = LlmScripte("<c>", "<d>")
    resultat = lancer(tmp_path, build, llm, reprendre_run_id=run_id)

    assert len(llm.appels) == 2  # seule la 2e ligne est générée
    assert resultat.statut == "complet"
    cles = [c["cle"] for c in lire(resultat.run, NOM_CANDIDATS)]
    assert len(cles) == len(set(cles)) == 6  # 2 Mistral + 4 locaux, aucun doublon


def test_jeu_sans_les_taches_demandees(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("CO",))
    with pytest.raises(ManifesteInvalide):
        lancer(tmp_path, build, LlmScripte("<x>"))


# --- DeepSeek via OpenRouter ---------------------------------------------------------------


def test_openrouter_lc_seulement_budget_reserve(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC", "CR"))
    banc = _banc(tmp_path / "banc")
    banc.faux.texte_defaut = lambda _corps: "<deepseek-factice>"
    llm = LlmScripte("<x>")
    resultat = lancer(
        tmp_path,
        build,
        llm,
        temperatures=[0.3],
        deepseek_taches=["LC"],
        client=banc.client(),
    )

    candidats = lire(resultat.run, NOM_CANDIDATS)
    distants = [c for c in candidats if c["source"] == f"openrouter:{F.MODELE}"]
    assert [c["tache"] for c in distants] == ["LC"]
    assert distants[0]["candidat_id"].startswith("openrouter:")
    corps = banc.faux.corps()
    assert len(corps) == 1  # un appel : la ligne LC seule
    assert corps[0]["messages"] == ligne_sft(1).messages[:-1]  # même conversation que le build
    assert corps[0]["model"] == F.MODELE
    reservations = banc.reservations()
    assert len(reservations) == 1  # budget réservé avant l'appel
    assert resultat.rapport["cout_openrouter_eur"] == pytest.approx(F.COUT)


def test_openrouter_tronque_exclu_et_reprise_sans_rappel(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC",))
    banc = _banc(tmp_path / "banc")
    banc.faux.reponses = [{"texte": "<coupe-factice>", "finish_reason": "length"}]
    resultat = lancer(
        tmp_path, build, LlmScripte("<x>"), temperatures=[0.3],
        deepseek_taches=["LC"], client=banc.client(),
    )  # fmt: skip
    assert [e["motif"] for e in lire(resultat.run, NOM_ECARTES)] == ["tronquee"]
    assert not [c for c in lire(resultat.run, NOM_CANDIDATS) if c["source"].startswith("open")]


def test_reprise_apres_budget_epuise_appelle_openrouter(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC",))
    vide = _banc(tmp_path / "vide", plafond=0.0)
    premier = lancer(
        tmp_path, build, LlmScripte("<x>"), temperatures=[0.3],
        deepseek_taches=["LC"], client=vide.client(),
    )  # fmt: skip
    assert premier.statut == "partiel-budget"
    plein = _banc(tmp_path / "plein")
    llm = LlmScripte("<y>")
    suite = lancer(
        tmp_path, build, llm, temperatures=[0.3], deepseek_taches=["LC"],
        client=plein.client(), reprendre_run_id=premier.run.run_id,
    )  # fmt: skip
    assert llm.appels == []  # le candidat local déjà journalisé n'est pas regénéré
    assert len(plein.faux.corps()) == 1
    assert suite.statut == "complet"
    sources = [c["source"] for c in lire(suite.run, NOM_CANDIDATS)]
    assert sources.count(f"openrouter:{F.MODELE}") == 1 and sources.count("mistral") == 1


def test_budget_epuise_statut_partiel(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC", "LC"))
    banc = _banc(tmp_path / "banc", plafond=0.0)
    resultat = lancer(
        tmp_path, build, LlmScripte("<x>"), temperatures=[0.3],
        deepseek_taches=["LC"], client=banc.client(),
    )  # fmt: skip
    assert resultat.statut == "partiel-budget"
    assert banc.faux.corps() == []  # rien n'est envoyé
    # Les candidats Mistral et locaux restent écrits.
    assert len(lire(resultat.run, NOM_CANDIDATS)) == 4


def test_plafond_estime_refuse_avant_tout_run(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC",))
    banc = _banc(tmp_path / "banc")
    llm = LlmScripte("<x>")
    with pytest.raises(PlafondEstimeDepasse):
        lancer(
            tmp_path, build, llm, temperatures=[0.3], deepseek_taches=["LC"],
            client=banc.client(), plafond_estime_eur=0.0,
        )  # fmt: skip
    assert llm.appels == [] and banc.faux.corps() == []
    assert not (tmp_path / "runs" / "data-candidats").exists()


def test_deepseek_sans_client_refuse(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC",))
    with pytest.raises(ValueError):
        lancer(tmp_path, build, LlmScripte("<x>"), deepseek_taches=["LC"])


# --- Jugement des candidats (deux juges) -------------------------------------------------


class _Lecteur:
    """`LecteurGeneration` minimal : sessions LC, source en amorce, réponse Mistral."""

    def __init__(self, sessions: list[str]) -> None:
        self._sessions = sessions
        self.amorces = {"a1": SimpleNamespace(emplacement="texte", texte="<source-factice-1>")}

    def sessions(self) -> list[Any]:
        return [
            SimpleNamespace(
                session_id=sid,
                tache="LC",
                appel_ids=[f"{i:032x}"],
                amorce_ids=["a1"],
                amorces_derivees=[],
            )  # fmt: skip
            for i, sid in enumerate(self._sessions, start=1)
        ]

    def reponse_finale(self, brut: Any) -> str:
        return "<mistral-factice>"


def _registre(dossier: Path) -> RegistreBudget:
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / ".env").write_text(f"OPENROUTER_API_KEY={F.CLE_FACTICE}\n", encoding="utf-8")
    budgets = """
schema_version = 1
campagne_id = "campagne-test-candidats"
marge_eur = 0.0
majoration_entree = 1.0

[postes.openrouter]
plafond_eur = 10.0

[imputations]
juge-donnees-openrouter = "openrouter"
"""
    tarifs = (
        F.TARIFS
        + """
[modeles."moonshotai/modele-factice"]
devise = "USD"
date = 2026-10-20
source = "test"

[modeles."moonshotai/modele-factice".modes.direct]
entree = 1.0
sortie = 1.0
"""
    )
    (dossier / "budgets.toml").write_text(budgets, encoding="utf-8")
    (dossier / "tarifs.toml").write_text(tarifs, encoding="utf-8")
    return RegistreBudget(
        charger_budgets(dossier / "budgets.toml"),
        charger_tarifs(dossier / "tarifs.toml"),
        dossier / "budget.sqlite",
    )


def test_juger_candidats_avec_deux_juges(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC", "LC"))
    resultat = lancer(tmp_path, build, LlmScripte("<a>", "<b>"), temperatures=[0.3])
    lecteur = _Lecteur([ligne_sft(1).meta.session_id, ligne_sft(2).meta.session_id])
    candidats, ecartes = candidats_depuis_run(
        resultat.run.run_id, lecteur, ["LC", "CR"], racine=tmp_path
    )
    assert ecartes == {}
    assert len(candidats) == 4 and {c.texte for c in candidats} == {
        "<mistral-factice>",
        "<a>",
        "<b>",
    }
    assert all(c.source == "<source-factice-1>" for c in candidats)

    banc = _banc(tmp_path / "banc")
    registre = _registre(tmp_path / "reg")
    banc.registre = registre
    banc.faux.texte_defaut = lambda _c: json.dumps(
        {
            "criteres": {
                n: {"note": 2 if n == "fidelite" else 1, "motif": "<motif-factice>", "extraits": []}
                for n in ("fidelite", "termes")
            },
            "listes": {n: [] for n in LISTES_PAR_TACHE["LC"]},
            "verdict_modele": "accepte",
        }
    )
    base = charger_config_donnees().juge_donnees
    assert base.pour_juge("deepseek") is base
    kimi = base.pour_juge("kimi")
    assert kimi.modele == "moonshotai/kimi-k2.6" and kimi.effort_raisonnement is None
    assert kimi.seuils == base.seuils
    with pytest.raises(ValueError, match="inconnu"):
        base.pour_juge("gpt")

    lignes_par_juge = {}
    for nom, modele in (("deepseek", F.MODELE), ("kimi", "moonshotai/modele-factice")):
        config = JugeDonneesConfig(modele=modele, max_tokens=500, appels_paralleles=1)
        juge = JugeDonnees(config, banc.client(), charger_grilles(["LC"]), {})
        jugement = lancer_jugement(
            racine=tmp_path, juge=juge, candidats=candidats, depuis_run_id=resultat.run.run_id,
            taches=["LC"], config_run={"juge_nom": nom, "origine": "candidats"},
            consigner=lambda _m: None,
        )  # fmt: skip
        assert jugement.statut == "complet"
        assert ouvrir_run(jugement.run.run_id, racine=tmp_path).manifeste.config["juge_nom"] == nom
        lignes_par_juge[nom] = lire(jugement.run, NOM_VERDICTS)
    for nom, modele in (("deepseek", F.MODELE), ("kimi", "moonshotai/modele-factice")):
        lignes = lignes_par_juge[nom]
        assert len(lignes) == 4  # un verdict par candidat
        assert {ligne["juge"] for ligne in lignes} == {modele}
        assert {ligne["candidat_id"] for ligne in lignes} == {c.candidat_id for c in candidats}
        assert all(ligne["session_id"] for ligne in lignes), lignes
        assert {ligne["verdict"] for ligne in lignes} == {"accepte"}, lignes[0]


def test_candidat_hors_grille_ou_texte_altere_ecarte(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC", "CO"))
    resultat = lancer(tmp_path, build, LlmScripte("<a>"), taches=["LC"], temperatures=[0.3])
    lecteur = _Lecteur([ligne_sft(1).meta.session_id])
    # Altération du journal local (SHA-256 différent) : impossible par déclencheur, donc on
    # redirige le candidat vers un appel inconnu.
    candidats = lire(resultat.run, NOM_CANDIDATS)
    local = next(c for c in candidats if c["source"].startswith("slm:"))
    chemin = resultat.run.dossier / NOM_CANDIDATS
    contenu = chemin.read_text("utf-8").replace(local["candidat_id"], "slm:" + "0" * 32)
    chemin.write_text(contenu, encoding="utf-8")
    sans, ecartes = candidats_depuis_run(resultat.run.run_id, lecteur, ["LC"], racine=tmp_path)
    assert ecartes == {"texte_introuvable": 1}
    assert len(sans) == 1  # la cible Mistral reste
    _, hors = candidats_depuis_run(resultat.run.run_id, lecteur, ["CT"], racine=tmp_path)
    assert hors == {"hors_taches": 2}


def test_lecteur_train_garde_son_acces_et_data_lit_journaux(tmp_path: Path) -> None:
    from slmsp.core.artefacts import chemin_autorise

    var = dossier_var()
    for nom in ("generations-locales.sqlite", "appels-generateur-openrouter.sqlite"):
        assert chemin_autorise(var / nom, "data", racine=tmp_path) == (var / nom).resolve()
    with pytest.raises(LectureInterdite):
        chemin_autorise(var / "verdicts.sqlite", "data", racine=tmp_path)


# --- CLI et configuration ------------------------------------------------------------------


def test_cli_validations(capsys: pytest.CaptureFixture[str]) -> None:
    for argv in (
        ["data", "candidats", "--build", "b", "--base", "x", "--temperatures", "0.3,0.3"],
        ["data", "candidats", "--build", "b", "--base", "x", "--temperatures", "abc"],
        ["data", "candidats", "--build", "b", "--base", "x", "--temperatures", "0.3"]
        + ["--taches", "CT"],
        ["data", "juger", "--depuis", "a", "--candidats", "b"],
        ["data", "juger", "--candidats", "b", "--juge", "gpt"],
        ["data", "candidats", "--base", "x", "--temperatures", "0.3"],  # --build sans reprise
    ):  # fmt: skip
        assert main(argv) == int(CodeSortie.USAGE)
    capsys.readouterr()


def test_config_candidats_et_kimi() -> None:
    config = charger_config_donnees()
    assert config.candidats.modele_openrouter == "deepseek/deepseek-v4-pro"
    assert config.candidats.usage_budget == "generateur-openrouter"
    assert set(config.juge_donnees.juges) == {"kimi"}
    from slmsp.budget.config import charger_tarifs
    from slmsp.core.config import racine_projet

    tarifs = charger_tarifs(racine_projet() / "config" / "tarifs.toml")
    assert "moonshotai/kimi-k2.6" in tarifs.modeles


# --- Revue : reprise sans second paiement, fins anormales, nettoyage, garde de famille ------


def test_interruption_annule_les_appels_en_file_et_reprise_sans_repayer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import slmsp.data.candidats as module

    build = ecrire_jeu(tmp_path, ("LC",) * 6)
    banc = _banc(tmp_path / "banc")
    banc.faux.texte_defaut = lambda _corps: "<deepseek-factice>"
    config = CONFIG.model_copy(update={"appels_paralleles": 1})
    ligne_candidat = module._ligne_candidat

    def panne(*args: Any, **kwargs: Any) -> dict[str, Any]:
        if kwargs["source"].startswith("openrouter:"):
            raise OSError("<disque-plein-factice>")
        return ligne_candidat(*args, **kwargs)

    monkeypatch.setattr(module, "_ligne_candidat", panne)
    options = {"temperatures": [0.3], "deepseek_taches": ["LC"], "config": config}
    with pytest.raises(OSError):
        lancer(tmp_path, build, LlmScripte("<x>"), client=banc.client(), **options)
    payes = len(banc.faux.corps())
    assert payes <= 2  # un seul fil : le premier appel et au plus celui en cours, pas la file
    run_id = sorted((tmp_path / "runs" / "data-candidats").iterdir())[0].name

    monkeypatch.setattr(module, "_ligne_candidat", ligne_candidat)
    suite = lancer(
        tmp_path, build, LlmScripte("<y>"), client=banc.client(), reprendre_run_id=run_id,
        **options,
    )  # fmt: skip
    assert suite.statut == "complet"
    assert len(banc.faux.corps()) == 6  # chaque requête payée une seule fois en tout
    distants = [c for c in lire(suite.run, NOM_CANDIDATS) if c["source"].startswith("open")]
    assert len(distants) == 6 == len({c["cle"] for c in distants})
    assert suite.rapport["cout_openrouter_eur"] == pytest.approx(F.COUT * (6 - payes))


@pytest.mark.parametrize("fin", ["content_filter", "error", None])
def test_openrouter_fin_anormale_ecartee(tmp_path: Path, fin: str | None) -> None:
    build = ecrire_jeu(tmp_path, ("LC",))
    banc = _banc(tmp_path / "banc")
    banc.faux.reponses = [{"texte": "<deepseek-factice>", "finish_reason": fin}]
    resultat = lancer(
        tmp_path, build, LlmScripte("<x>"), temperatures=[0.3],
        deepseek_taches=["LC"], client=banc.client(),
    )  # fmt: skip
    ecartes = lire(resultat.run, NOM_ECARTES)
    assert [(e["motif"], e["finish_reason"]) for e in ecartes] == [("interrompue", fin)]
    assert not [c for c in lire(resultat.run, NOM_CANDIDATS) if c["source"].startswith("open")]


def test_cout_des_appels_echoues_compte(tmp_path: Path) -> None:
    from slmsp.fournisseurs.client import ErreurApiFournisseur

    build = ecrire_jeu(tmp_path, ("LC",))
    client = _banc(tmp_path / "banc").client()

    def echec(*_args: Any, **_kwargs: Any) -> Any:
        raise ErreurApiFournisseur("<echec-factice>", 200, 0.25)

    client.appeler = echec  # type: ignore[method-assign]
    resultat = lancer(
        tmp_path, build, LlmScripte("<x>"), temperatures=[0.3],
        deepseek_taches=["LC"], client=client,
    )  # fmt: skip
    assert resultat.statut == "partiel-erreur"
    assert resultat.rapport["cout_openrouter_eur"] == pytest.approx(0.25)


def test_reprise_aux_reglages_divergents_refusee(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC", "LC"))
    with pytest.raises(RuntimeError):
        lancer(tmp_path, build, LlmScripte("<a>", erreur_apres=1))
    run_id = sorted((tmp_path / "runs" / "data-candidats").iterdir())[0].name
    llm = LlmScripte("<b>")
    for divergence in (
        {"temperatures": [0.5]},
        {"taches": ["LC"]},
        {"config": CONFIG.model_copy(update={"graine": 8})},
    ):
        with pytest.raises(ManifesteInvalide, match="divergents"):
            lancer(tmp_path, build, llm, reprendre_run_id=run_id, **divergence)
    assert llm.appels == []


def test_texte_juge_est_le_texte_appris(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC",))
    trop_long = "<x>" * PLAFOND
    llm = LlmScripte("Voici le texte :\n\n<a-factice>", trop_long, "\n \n")
    resultat = lancer(tmp_path, build, llm, temperatures=[0.3, 0.7, 1.0])
    motifs = sorted(e["motif"] for e in lire(resultat.run, NOM_ECARTES))
    assert motifs == ["longueur", "vide"]  # la sortie trop longue et la sortie blanche
    lecteur = _Lecteur([ligne_sft(1).meta.session_id])
    candidats, _ = candidats_depuis_run(resultat.run.run_id, lecteur, ["LC"], racine=tmp_path)
    assert sorted(c.texte for c in candidats) == ["<a-factice>", "<mistral-factice>"]


def test_re_refuse_et_juge_croise_ne_note_que_deepseek(tmp_path: Path) -> None:
    build = ecrire_jeu(tmp_path, ("LC", "RE"))
    with pytest.raises(ValueError, match="RE"):
        lancer(tmp_path, build, LlmScripte("<x>"), taches=["RE"])
    banc = _banc(tmp_path / "banc")
    banc.faux.texte_defaut = lambda _corps: "<deepseek-factice>"
    resultat = lancer(
        tmp_path, build, LlmScripte("<x>"), taches=["LC"], temperatures=[0.3],
        deepseek_taches=["LC"], client=banc.client(),
    )  # fmt: skip
    lecteur = _Lecteur([ligne_sft(1).meta.session_id])
    # Le journal du banc n'est pas celui de `var/` : seul le filtrage par source est relu ici.
    candidats, ecartes = candidats_depuis_run(
        resultat.run.run_id, lecteur, ["LC"], racine=tmp_path, sources=SOURCES_JUGE_CROISE
    )
    assert ecartes.get("autre_source") == 2  # Mistral et local écartés
    assert ecartes.get("texte_introuvable", 0) + len(candidats) == 1
    assert main(["data", "candidats", "--build", "b", "--base", "x", "--temperatures", "0.3",
                 "--taches", "RE"]) == int(CodeSortie.USAGE)  # fmt: skip
