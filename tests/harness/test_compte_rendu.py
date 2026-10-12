"""Comptes rendus longs : découpage, synthèses de morceau et fusion (story 4.4, FR-13).

Règle D1.1 : aucun texte rédigé. Notes, transcriptions, synthèses et comptes rendus sont
des mots aléatoires (`mots`). `LlmCR` est un `FakeLlm` doté de `taille_contexte`, qui
choisit sa sortie selon le prompt système reçu (CR, CR-morceau ou CR-fusion).
"""

from __future__ import annotations

import random
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import pytest
from harness_factices import (
    USAGE,
    FakeEmbedder,
    FakeLlm,
    FakeVectorStore,
    SpyModePort,
    SpyNetGate,
    SpyToolPort,
    mots,
    script,
    url_factice,
)

from slmsp.core.evenements import AppelNonConforme, AppelOutil, Erreur, Fin, Jeton, Progression
from slmsp.harness.config import ConfigCompteRendu
from slmsp.harness.decoupage import paragraphes
from slmsp.harness.prompts import construire_messages
from slmsp.harness.service import CODE_ERREUR, MESSAGE_ERREUR, AssistantService
from slmsp.harness.taches import compte_rendu

CONTEXTE = 3000
RESERVE = 500
BUDGET = CONTEXTE - RESERVE


class LlmCR(FakeLlm):
    """`FakeLlm` avec `taille_contexte`, routé par prompt système.

    `morceau(i)` donne le script de la i-ème synthèse de morceau, `fusion(j)` celui du
    j-ème appel de fusion (intermédiaire ou final), `unique` celui de l'appel unique.
    """

    def __init__(
        self,
        table,
        taille_contexte: int | None = CONTEXTE,
        *,
        morceau: Callable[[int], list[Any]] | None = None,
        fusion: Callable[[int], list[Any]] | None = None,
        unique: list[Any] | None = None,
    ) -> None:
        super().__init__()
        if taille_contexte is not None:
            self.taille_contexte = taille_contexte
        cr = table.tache("CR")
        self.systemes = {
            cr.prompt.consigne: "unique",
            cr.prompt_pour("morceau").consigne: "morceau",
            cr.prompt_pour("fusion").consigne: "fusion",
        }
        self.morceau = morceau or (lambda i: script(mots(20, f"synthese-{i}")))
        self.fusion = fusion or (lambda j: script(mots(30, f"fusion-{j}")))
        self.unique = unique or script(mots(30, "unique"))
        self.genres: list[str] = []

    def generer(self, messages, *, tools=None, options=None):
        genre = self.systemes[messages[0]["content"]]
        rang = self.genres.count(genre) + 1
        self.genres.append(genre)
        if genre == "morceau":
            self.scripts = [self.morceau(rang)]
        elif genre == "fusion":
            self.scripts = [self.fusion(rang)]
        else:
            self.scripts = [self.unique]
        return super().generer(messages, tools=tools, options=options)

    def appels_de(self, genre: str) -> list[dict[str, Any]]:
        return [a for a, g in zip(self.appels, self.genres, strict=True) if g == genre]


@pytest.fixture
def config_cr(config_harnais):
    return config(config_harnais, RESERVE, 1)


def config(base, reserve: int, chevauchement: int):
    return base.model_copy(
        update={
            "compte_rendu": ConfigCompteRendu(
                reserve_sortie_tokens=reserve, chevauchement_paragraphes=chevauchement
            )
        }
    )


def service(table, config, llm) -> AssistantService:
    gate = SpyNetGate()
    return AssistantService(
        llm,
        FakeEmbedder(),
        FakeVectorStore(),
        SpyToolPort(gate),
        SpyModePort(),
        config,
        taches=table,
    )


def blocs_aleatoires(nb_mots: int, graine: str, taille: tuple[int, int] = (20, 80)) -> list[str]:
    hasard = random.Random(graine)
    blocs: list[str] = []
    total = 0
    while total < nb_mots:
        k = hasard.randint(*taille)
        blocs.append(mots(k, f"{graine}-{len(blocs)}"))
        total += k
    return blocs


def user(texte: str) -> dict[str, str]:
    return {"role": "user", "content": texte}


def contenu_de(appel: Mapping[str, Any], libelle: str) -> str:
    """Section « <libellé> : » du message user d'un appel (dernière section)."""
    return appel["messages"][-1]["content"].split(f"{libelle} :\n", 1)[1]


def sans_chevauchement(morceaux: Sequence[str]) -> list[str]:
    resultat: list[str] = []
    precedent: list[str] = []
    for morceau in morceaux:
        blocs = paragraphes(morceau)
        while blocs and precedent and blocs[0] in precedent:
            blocs = blocs[1:]
        resultat.extend(" ".join(blocs).split())
        precedent = paragraphes(morceau)
    return resultat


# --- Chemin court ----------------------------------------------------------------------------


def test_cr_court_un_seul_appel(table, config_cr) -> None:
    llm = LlmCR(table)
    notes = mots(300, "court")
    evenements = list(service(table, config_cr, llm).repondre("CR", [user(notes)]))

    assert llm.genres == ["unique"]
    assert llm.appels[0]["messages"] == construire_messages(table.tache("CR"), {"notes": notes})
    assert llm.appels[0]["messages"][0]["content"] == table.tache("CR").prompt.consigne
    types = [type(e) for e in evenements]
    nb = types.count(Jeton)
    assert types == [Jeton] * nb + [Fin]
    assert "".join(e.texte for e in evenements[:nb]) == mots(30, "unique")


def test_cr_sans_taille_contexte_un_seul_appel(table, config_cr) -> None:
    llm = FakeLlm(script(mots(10, "r")))
    assert not hasattr(llm, "taille_contexte")
    notes = "\n\n".join(blocs_aleatoires(9000, "sans-taille"))
    evenements = list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
    assert len(llm.appels) == 1
    assert llm.appels[0]["messages"] == construire_messages(table.tache("CR"), {"notes": notes})
    assert not any(isinstance(e, Progression) for e in evenements)
    assert isinstance(evenements[-1], Fin)


def test_cr_budget_nul_un_seul_appel(table, config_harnais) -> None:
    llm = LlmCR(table, taille_contexte=400)
    notes = "\n\n".join(blocs_aleatoires(2000, "budget-nul"))
    list(service(table, config(config_harnais, 500, 1), llm).repondre("CR", [user(notes)]))
    assert llm.genres == ["unique"]


def test_cr_consigne_trop_longue_un_seul_appel(table, config_cr) -> None:
    """Même un mot ne tient pas avec la consigne : découper ne servirait à rien."""
    llm = LlmCR(table)
    entree = {"consigne": mots(BUDGET, "consigne"), "notes": mots(50, "n")}
    list(
        service(table, config_cr, llm).repondre(
            "CR", [user(entree["notes"])], options={"entree": entree}
        )
    )
    assert llm.genres == ["unique"]


# --- Chemin long -----------------------------------------------------------------------------


def test_cr_long_morceaux_puis_fusion(table, config_cr) -> None:
    blocs = blocs_aleatoires(9000, "long")
    notes = "\n\n".join(blocs)
    consigne = mots(12, "consigne")
    entree = {"consigne": consigne, "notes": notes, "nb_mots": 9000}
    llm = LlmCR(table)
    evenements = list(
        service(table, config_cr, llm).repondre(
            "CR", [user(notes)], options={"entree": entree, "seed": 3}
        )
    )

    morceaux_appels = llm.appels_de("morceau")
    n = len(morceaux_appels)
    assert n >= 4
    assert llm.genres == ["morceau"] * n + ["fusion"]
    cr = table.tache("CR")
    morceaux = []
    for i, appel in enumerate(morceaux_appels, start=1):
        morceau = contenu_de(appel, "Notes")
        morceaux.append(morceau)
        attendu = construire_messages(
            cr,
            {"consigne": consigne, "partie": f"{i} sur {n}", "notes": morceau},
            variante="morceau",
        )
        assert appel["messages"] == attendu
        assert llm.compter_tokens(appel["messages"]) <= BUDGET
        assert appel["tools"] is None
        assert appel["options"] == {"seed": 3, "max_tokens": RESERVE}  # plafond : la réserve
        assert all(bloc in blocs for bloc in paragraphes(morceau))  # coupé entre paragraphes
    for avant, apres in zip(morceaux, morceaux[1:], strict=False):  # chevauchement de 1
        assert paragraphes(apres)[0] == paragraphes(avant)[-1]
    assert sans_chevauchement(morceaux) == notes.split()  # aucune troncature

    (fusion,) = llm.appels_de("fusion")
    syntheses = [mots(20, f"synthese-{i}") for i in range(1, n + 1)]
    assert fusion["messages"] == construire_messages(
        cr, {"consigne": consigne, "parties": syntheses}, variante="fusion"
    )

    progressions = [e for e in evenements if isinstance(e, Progression)]
    assert progressions == [
        *(Progression(etape=f"Partie {i} sur {n}", fait=i - 1, total=n) for i in range(1, n + 1)),
        Progression(etape="Fusion des parties", fait=n, total=n),
    ]
    types = [type(e) for e in evenements]
    nb = types.count(Jeton)
    assert types == [Progression] * (n + 1) + [Jeton] * nb + [Fin]
    assert "".join(e.texte for e in evenements if isinstance(e, Jeton)) == mots(30, "fusion-1")
    fin = evenements[-1]
    assert fin.raison == "terminee" and fin.urls_inventees == []
    for cle, valeur in USAGE.items():
        assert fin.usage[cle] == valeur * (n + 1)
    assert "delai_premier_token_ms" in fin.usage


def test_cr_long_deterministe(table, config_cr) -> None:
    notes = "\n\n".join(blocs_aleatoires(7000, "stable"))
    appels = []
    for _ in range(2):
        llm = LlmCR(table)
        list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
        appels.append([a["messages"] for a in llm.appels])
    assert appels[0] == appels[1]


def test_cr_long_historique_seulement_dans_la_fusion_finale(table, config_cr) -> None:
    notes = "\n\n".join(blocs_aleatoires(6000, "historique"))
    historique = [user(mots(5, "avant")), {"role": "assistant", "content": mots(5, "rep")}]
    llm = LlmCR(table)
    list(service(table, config_cr, llm).repondre("CR", [*historique, user(notes)]))
    for appel in llm.appels_de("morceau"):
        assert [m["role"] for m in appel["messages"]] == ["system", "user"]
    (fusion,) = llm.appels_de("fusion")
    assert [m["role"] for m in fusion["messages"]] == ["system", "user", "assistant", "user"]
    assert fusion["messages"][1:3] == historique


def test_cr_notes_puis_transcription_decoupees_separement(table, config_cr) -> None:
    notes = "\n\n".join(blocs_aleatoires(3000, "notes"))
    transcription = "\n\n".join(blocs_aleatoires(6000, "transcription"))
    entree = {"transcription": transcription, "notes": notes}
    llm = LlmCR(table)
    list(service(table, config_cr, llm).repondre("CR", [user(notes)], options={"entree": entree}))
    users = [a["messages"][1]["content"] for a in llm.appels_de("morceau")]
    sections = ["Notes" if "\nNotes :\n" in u else "Transcription" for u in users]
    assert sections[0] == "Notes" and sections[-1] == "Transcription"
    assert sections == sorted(sections)  # toutes les notes d'abord (ordre de ORDRE_CLES)
    assert not any("\nNotes :\n" in u and "\nTranscription :\n" in u for u in users)
    appels = llm.appels_de("morceau")
    par_cle = {
        cle: [contenu_de(a, cle) for a, s in zip(appels, sections, strict=True) if s == cle]
        for cle in ("Notes", "Transcription")
    }
    assert sans_chevauchement(par_cle["Notes"]) == notes.split()
    assert sans_chevauchement(par_cle["Transcription"]) == transcription.split()


def test_cr_paragraphe_enorme(table, config_harnais) -> None:
    notes = mots(7000, "enorme")  # un seul bloc, sans saut de ligne ni ponctuation
    llm = LlmCR(table)
    list(service(table, config(config_harnais, RESERVE, 0), llm).repondre("CR", [user(notes)]))
    morceaux = [contenu_de(a, "Notes") for a in llm.appels_de("morceau")]
    assert len(morceaux) >= 3
    assert all(llm.compter_tokens(a["messages"]) <= BUDGET for a in llm.appels_de("morceau"))
    assert " ".join(morceaux).split() == notes.split()


# --- Fusion ----------------------------------------------------------------------------------


def test_fusions_intermediaires_quand_les_syntheses_debordent(table, config_cr) -> None:
    notes = "\n\n".join(blocs_aleatoires(9000, "intermediaire"))
    llm = LlmCR(table, morceau=lambda i: script(mots(900, f"grosse-{i}")))
    evenements = list(service(table, config_cr, llm).repondre("CR", [user(notes)]))

    n = len(llm.appels_de("morceau"))
    fusions = llm.appels_de("fusion")
    assert len(fusions) >= 3  # au moins 2 fusions intermédiaires, puis la finale
    assert llm.genres[:n] == ["morceau"] * n
    for appel in fusions:
        assert llm.compter_tokens(appel["messages"]) <= BUDGET
    finale = fusions[-1]
    intermediaires = [mots(30, f"fusion-{j}") for j in range(1, len(fusions))]
    assert all(s in finale["messages"][1]["content"] for s in intermediaires)
    etapes = [e.etape for e in evenements if isinstance(e, Progression)]
    m = len(fusions) - 1
    assert etapes[n:] == [
        *(f"Fusion intermédiaire {j} sur {m}" for j in range(1, m + 1)),
        ("Fusion des parties"),
    ]
    intermediaires_p = [
        e
        for e in evenements
        if isinstance(e, Progression) and e.etape.startswith("Fusion intermédiaire")
    ]
    assert [(p.fait, p.total) for p in intermediaires_p] == [(j - 1, m) for j in range(1, m + 1)]
    texte = "".join(e.texte for e in evenements if isinstance(e, Jeton))
    assert texte == mots(30, f"fusion-{len(fusions)}")  # seule la fusion finale est diffusée
    assert evenements[-1].usage["prompt_tokens"] == USAGE["prompt_tokens"] * (n + len(fusions))


def test_aucun_regroupement_possible_fusion_finale_tentee(table, config_cr) -> None:
    notes = "\n\n".join(blocs_aleatoires(6000, "sans-regroupement"))
    llm = LlmCR(table, morceau=lambda i: script(mots(2000, f"enorme-{i}")))
    evenements = list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
    n = len(llm.appels_de("morceau"))
    assert llm.genres == ["morceau"] * n + ["fusion"]
    (finale,) = llm.appels_de("fusion")
    assert llm.compter_tokens(finale["messages"]) > BUDGET  # dépassement visible côté serveur
    assert isinstance(evenements[-1], Fin)


def test_synthese_vide_ignoree(table, config_cr) -> None:
    notes = "\n\n".join(blocs_aleatoires(6000, "vide"))
    llm = LlmCR(table, morceau=lambda i: script("  \n " if i == 1 else mots(20, f"s-{i}")))
    list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
    n = len(llm.appels_de("morceau"))
    (fusion,) = llm.appels_de("fusion")
    attendues = [mots(20, f"s-{i}") for i in range(2, n + 1)]
    assert fusion["messages"] == construire_messages(
        table.tache("CR"), {"parties": attendues}, variante="fusion"
    )


def test_toutes_syntheses_vides_erreur(table, config_cr, caplog) -> None:
    notes = "\n\n".join(blocs_aleatoires(6000, "toutes-vides"))
    llm = LlmCR(table, morceau=lambda i: script(" "))
    evenements = list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
    assert evenements[-1] == Erreur(code=CODE_ERREUR, message=MESSAGE_ERREUR)
    assert "fusion" not in llm.genres
    assert not any(isinstance(e, Jeton) for e in evenements)
    assert "SynthesesVides" in caplog.text


def test_erreur_du_modele_sur_un_morceau(table, config_cr) -> None:
    notes = "\n\n".join(blocs_aleatoires(6000, "panne"))

    def morceau(i: int) -> list[Any]:
        if i == 2:
            return [Jeton(texte=mots(3, "debut")), RuntimeError(mots(2, "detail"))]
        return script(mots(20, f"s-{i}"))

    llm = LlmCR(table, morceau=morceau)
    evenements = list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
    assert evenements[-1] == Erreur(code=CODE_ERREUR, message=MESSAGE_ERREUR)
    assert [type(e) for e in evenements] == [Progression, Progression, Erreur]
    assert llm.genres == ["morceau", "morceau"]


def test_appel_non_conforme_d_un_morceau_relaye(table, config_cr) -> None:
    notes = "\n\n".join(blocs_aleatoires(6000, "outil"))

    def morceau(i: int) -> list[Any]:
        appel = AppelOutil(id="c1", nom="search_datasets", arguments={"q": mots(1, "q")})
        return [appel, *script(mots(20, f"s-{i}"))] if i == 1 else script(mots(20, f"s-{i}"))

    llm = LlmCR(table, morceau=morceau)
    evenements = list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
    (non_conforme,) = [e for e in evenements if isinstance(e, AppelNonConforme)]
    assert non_conforme.nom == "search_datasets"
    assert isinstance(evenements[-1], Fin)


def test_traitement_enregistre() -> None:
    from slmsp.harness.taches import traitement

    assert traitement("CR") is compte_rendu.traiter


# --- Revue : options, raison, usage, URL, fusions intermédiaires blanches -------------------


@pytest.mark.parametrize(("demande", "attendu"), [(None, RESERVE), (2000, RESERVE), (120, 120)])
def test_max_tokens_plafonne_a_la_reserve(table, config_cr, demande, attendu) -> None:
    notes = "\n\n".join(blocs_aleatoires(6000, "plafond"))
    options = {} if demande is None else {"max_tokens": demande}
    llm = LlmCR(table)
    list(service(table, config_cr, llm).repondre("CR", [user(notes)], options=options))
    assert len(llm.appels) >= 3
    assert all(a["options"] == {"max_tokens": attendu} for a in llm.appels)


def test_max_tokens_inchange_sur_le_chemin_court(table, config_cr) -> None:
    llm = LlmCR(table)
    list(
        service(table, config_cr, llm).repondre(
            "CR", [user(mots(50, "court"))], options={"max_tokens": 2000}
        )
    )
    assert llm.genres == ["unique"] and llm.appels[0]["options"] == {"max_tokens": 2000}


def test_raison_la_plus_grave_de_tous_les_appels(table, config_cr) -> None:
    notes = "\n\n".join(blocs_aleatoires(6000, "raison"))

    def morceau(i: int) -> list[Any]:
        texte = mots(20, f"s-{i}")
        if i == 1:
            return [Jeton(texte=texte), Fin(raison="longueur", usage=dict(USAGE))]
        return script(texte)

    llm = LlmCR(table, morceau=morceau)
    evenements = list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
    assert evenements[-1].raison == "longueur"

    llm = LlmCR(table, morceau=lambda i: script(mots(20, f"s-{i}")) if i > 1 else [])
    evenements = list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
    assert evenements[-1].raison == "interrompue"  # flux coupé sans Fin


def test_delai_premier_token_non_cumule(table, config_cr) -> None:
    notes = "\n\n".join(blocs_aleatoires(6000, "delai"))
    usage = {**USAGE, "delai_premier_token_ms": 1000}
    llm = LlmCR(
        table,
        morceau=lambda i: script(mots(20, f"s-{i}"), usage=usage),
        fusion=lambda j: [Fin(raison="terminee", usage=dict(usage))],  # aucun Jeton
    )
    evenements = list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
    fin = evenements[-1]
    assert not any(isinstance(e, Jeton) for e in evenements)
    assert "delai_premier_token_ms" not in fin.usage
    assert fin.usage["prompt_tokens"] == USAGE["prompt_tokens"] * len(llm.appels)


def test_urls_inventees_chemin_long(table, config_cr) -> None:
    connue = url_factice("connue")
    inventee = url_factice("inventee")
    blocs = blocs_aleatoires(6000, "urls")
    blocs[3] = f"{blocs[3]} {connue}"
    notes = "\n\n".join(blocs)
    llm = LlmCR(
        table, fusion=lambda j: script(f"{mots(5, 'r')} {connue} {mots(3, 's')} {inventee}")
    )
    evenements = list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
    assert "morceau" in llm.genres
    assert evenements[-1].urls_inventees == [inventee]


def test_fusion_intermediaire_blanche_exclue(table, config_cr) -> None:
    notes = "\n\n".join(blocs_aleatoires(9000, "inter-blanche"))
    llm = LlmCR(
        table,
        morceau=lambda i: script(mots(900, f"grosse-{i}")),
        fusion=lambda j: script(" " if j == 1 else mots(30, f"fusion-{j}")),
    )
    list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
    fusions = llm.appels_de("fusion")
    m = len(fusions) - 1
    assert m >= 2
    attendues = [mots(30, f"fusion-{j}") for j in range(2, m + 1)]
    assert fusions[-1]["messages"] == construire_messages(
        table.tache("CR"), {"parties": attendues}, variante="fusion"
    )


def test_fusions_intermediaires_toutes_blanches_erreur(table, config_cr, caplog) -> None:
    notes = "\n\n".join(blocs_aleatoires(9000, "inter-vides"))
    llm = LlmCR(
        table, morceau=lambda i: script(mots(900, f"grosse-{i}")), fusion=lambda j: script(" ")
    )
    evenements = list(service(table, config_cr, llm).repondre("CR", [user(notes)]))
    assert evenements[-1] == Erreur(code=CODE_ERREUR, message=MESSAGE_ERREUR)
    assert "SynthesesVides" in caplog.text
    etapes = [e.etape for e in evenements if isinstance(e, Progression)]
    assert "Fusion des parties" not in etapes  # aucune fusion finale
    assert not any(isinstance(e, Jeton) for e in evenements)


def test_notes_en_liste_au_dela_du_budget_un_seul_appel(table, config_cr) -> None:
    notes = blocs_aleatoires(6000, "liste")
    llm = LlmCR(table)
    list(
        service(table, config_cr, llm).repondre(
            "CR", [user(notes[0])], options={"entree": {"notes": notes}}
        )
    )
    assert llm.compter_tokens(llm.appels[0]["messages"]) > BUDGET
    assert llm.genres == ["unique"]
