"""Sélection des cibles parmi des candidats notés (`data build --selection`, story 15.3, O3).

Jeu SFT, candidats, verdicts et journal local synthétiques : tous les textes sont des jetons
artificiels (`<reponse-factice-1>`), jamais du contenu rédigé (D1). Aucun appel réseau, aucun
modèle réel.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from slmsp.cli import CodeSortie, main
from slmsp.core.artefacts import nouveau_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.erreurs import ManifesteInvalide, ProvenanceInvalide, SourceSansLicence
from slmsp.core.nettoyage import nettoyer_cible
from slmsp.core.schemas.entrainement import LigneEntrainement, MetaLigne
from slmsp.core.selection import verifier_selection
from slmsp.data.licences import RegistreLicences, UsageInterdit
from slmsp.data.nettoyage import Tokeniseur
from slmsp.data.selection import NOM_DETAIL, lancer_selection, score
from slmsp.inference.journal_local import JournalLocal
from slmsp.train.chargement import charger_jeu, recontroler_cibles

from .test_nettoyage import ecrire_source

BASE = "slm:base-factice"
JUGE = "org/juge-factice"
SOURCE = "org-factice/source-a"
SHA_TOK = "b" * 64
TOKENISEUR = Tokeniseur(compter=len, sha256=SHA_TOK)
SEUILS = {
    "CR": {"invention": 1, "structure": 1, "couverture": 0.8},
    "LC": {"fidelite": 2, "termes": 1},
}
REGLE = {"version": 3, "plafond_tokens": 200, "modele": "base:base-factice", "appliquee": True}
REGISTRE = f"""schema_version = 1

[[sources]]
id = "{SOURCE}"
licence = "licence-factice"
usage = "diffusable"
auteur_contenu = "public"
genere_par = "humain"

[[sources]]
id = "mistral/reponses-generateur"
licence = "licence-mistral-factice"
usage = "diffusable"
auteur_contenu = "mistral"
genere_par = "mistral"
"""
ENTREE_BASE = """
[[sources]]
id = "org-factice/Base-Factice"
licence = "licence-base-factice"
usage = "recherche"
auteur_contenu = "modele-base"
genere_par = "modele-base"
"""


def ligne(numero: int, tache: str, *, appels: int = 1) -> dict[str, Any]:
    return LigneEntrainement(
        messages=[
            {"role": "system", "content": f"<prompt-{tache}-factice>"},
            {"role": "user", "content": f"<entree-factice-{numero}>"},
            {"role": "assistant", "content": f"<reponse-factice-{numero}>"},
        ],
        tache=tache,
        meta=MetaLigne(
            generateur="<modele-factice>",
            appel_ids=[f"{numero:030x}{i:02x}" for i in range(appels)],
            session_id=f"s-{numero:024x}",
            version_gabarit={"<gabarit-factice>": 1},
            version_extracteur=1,
            source=["mistral/reponses-generateur", SOURCE],
            licence=["licence-mistral-factice", "licence-factice"],
            date=date(2026, 10, 16),
        ),
    ).model_dump(mode="json")


JEU = [
    ligne(1, "Q"),
    ligne(2, "CR", appels=2),
    ligne(3, "CR", appels=2),
    ligne(4, "RE"),
    ligne(5, "LC"),
    ligne(6, "CO"),
]


class Banc:
    """Racine de test : jeu source, registre, run de candidats, journal local, verdicts."""

    def __init__(self, racine: Path, *, base_au_registre: bool = True) -> None:
        self.racine = racine
        self.build, self.octets = ecrire_source(racine, JEU)
        chemin = racine / "data" / "registre-licences.toml"
        chemin.write_text(REGISTRE + (ENTREE_BASE if base_au_registre else ""), "utf-8")
        self.registre = RegistreLicences.charger(chemin, racine=racine)
        self.journal = JournalLocal()
        self.candidats: list[dict[str, Any]] = []
        self.verdicts: list[dict[str, Any]] = []

    def mistral(self, numero: int, notes: dict[str, float], verdict: str = "accepte") -> str:
        source = JEU[numero - 1]
        cid = f"mistral:{source['meta']['appel_ids'][-1]}"
        self._candidat(source, cid, "mistral", None, None)
        self.verdict(source, cid, notes, verdict)
        return cid

    def slm(
        self,
        numero: int,
        texte: str,
        notes: dict[str, float] | None,
        *,
        temperature: float = 0.3,
        verdict: str = "accepte",
        session: str | None = None,
        source: str = BASE,
    ) -> str:
        ligne_src = JEU[numero - 1]
        appel = self.journal.inscrire(
            session_id=session or ligne_src["meta"]["session_id"],
            slug="base-factice",
            requete={"messages": ligne_src["messages"][:-1], "tools": [], "options": {}},
            reponse=texte,
        )
        cid = f"slm:{appel}"
        self._candidat(ligne_src, cid, source, temperature, 7)
        if notes is not None:
            self.verdict(ligne_src, cid, notes, verdict)
        return cid

    def _candidat(
        self, src: dict[str, Any], cid: str, source: str, temperature: Any, graine: Any
    ) -> None:
        self.candidats.append(
            {
                "session_id": src["meta"]["session_id"],
                "candidat_id": cid,
                "source": source,
                "tache": src["tache"],
                "temperature": temperature,
                "graine": graine,
                "cle": cid,
                "rang": 0,
            }
        )

    def verdict(
        self, src: dict[str, Any], cid: str, notes: dict[str, float], verdict: str = "accepte"
    ) -> None:
        self.verdicts.append(
            {
                "session_id": src["meta"]["session_id"],
                "candidat_id": cid,
                "juge": JUGE,
                "tache": src["tache"],
                "verdict": verdict,
                "notes": notes,
                "verdict_modele": "refuse",
            }
        )

    def runs(
        self,
        *,
        juges: tuple[str, ...] = (JUGE,),
        depuis: str | None = None,
        statut_candidats: str = "complet",
        statut_juge: str = "complet",
    ) -> list[str]:
        run = nouveau_run(
            "data-candidats",
            "candidats",
            {
                "build_run_id": self.build,
                "base": BASE,
                "taches": ["CR", "LC"],
                "nettoyage": REGLE,
                "tokenizer_sha256": SHA_TOK,
            },
            racine=self.racine,
        )
        for candidat in self.candidats:
            run.ajouter_jsonl("candidats.jsonl", candidat)
        run.terminer(statut_candidats)
        self.candidats_id = run.run_id
        ids = []
        for juge in juges:
            jugement = nouveau_run(
                "data-juger",
                "juger",
                {
                    "depuis": depuis or run.run_id,
                    "juge": {"modele": juge, "seuils": SEUILS, "grilles": {"CR": "c" * 64}},
                },
                racine=self.racine,
            )
            for v in self.verdicts if juge == JUGE else []:
                jugement.ajouter_jsonl("verdicts.jsonl", v)
            jugement.terminer(statut_juge)
            ids.append(jugement.run_id)
        return ids

    def selection(self, verdicts: list[str], **options: Any) -> Any:
        reglages: dict[str, Any] = {
            "taches": ["CR", "LC"],
            "retirer": ["RE"],
            "variante": "recherche",
            "cr_min": 1,
            "tokeniseur": TOKENISEUR,
            **options,
        }
        return lancer_selection(
            racine=self.racine,
            candidats_run_id=self.candidats_id,
            verdicts_run_ids=verdicts,
            registre=self.registre,
            juge=JUGE,
            consigner=lambda _m: None,
            **reglages,
        )


CR_PLEIN = {"invention": 1, "structure": 1, "couverture": 1.0}
CR_MOINS = {"invention": 1, "structure": 1, "couverture": 0.8}
LC_PLEIN = {"fidelite": 2, "termes": 1}


def lignes(chemin: Path) -> list[dict[str, Any]]:
    return [json.loads(t) for t in chemin.read_text("utf-8").splitlines()]


def scenario(tmp_path: Path) -> tuple[Banc, dict[str, str], list[str]]:
    banc = Banc(tmp_path)
    ids = {
        "m2": banc.mistral(2, CR_MOINS),
        "s2": banc.slm(2, "Voici <x> :\n\n<reponse-factice-slm-2>", CR_PLEIN, temperature=0.7),
        "m3": banc.mistral(3, CR_PLEIN),
        "s3b": banc.slm(3, "<reponse-factice-slm-3b>", CR_PLEIN, temperature=0.7),
        "s3a": banc.slm(3, "<reponse-factice-slm-3a>", CR_PLEIN, temperature=0.3),
        "m5": banc.mistral(5, LC_PLEIN, verdict="refuse"),
        "s5": banc.slm(5, "<reponse-factice-slm-5>", None),  # sans verdict
    }
    banc._candidat(JEU[4], "openrouter:<appel-factice>", "openrouter:org/modele", 0.3, None)
    verdicts = banc.runs(juges=(JUGE, "org/juge-croise-factice"))
    return banc, ids, verdicts


# --- Sélection ----------------------------------------------------------------------------


def test_gagnant_egalite_base_ecartee_et_manifeste(tmp_path: Path) -> None:
    banc, ids, verdicts = scenario(tmp_path)
    resultat = banc.selection(verdicts)

    sortie = lignes(resultat.dossier / "train.jsonl")
    assert [x["tache"] for x in sortie] == ["Q", "CR", "CR", "CO"]
    source = banc.octets.split(b"\n")
    brutes = (resultat.dossier / "train.jsonl").read_bytes().split(b"\n")
    assert brutes[0] == source[0] and brutes[3] == source[5]  # copiées à l'octet près
    # CR 2 : la base l'emporte au score ; cible nettoyée, entrée inchangée, v2.
    assert sortie[1]["schema_version"] == 2
    assert sortie[1]["messages"][:-1] == JEU[1]["messages"][:-1]
    attendu = nettoyer_cible("Voici <x> :\n\n<reponse-factice-slm-2>", 3, "CR")
    assert sortie[1]["messages"][-1]["content"] == attendu
    meta = sortie[1]["meta"]
    assert meta["cible"] == {"source": BASE, "appel_local_id": ids["s2"].removeprefix("slm:")}
    assert meta["appel_ids"] == JEU[1]["meta"]["appel_ids"][:1]  # entrée seulement
    assert meta["generateur"] == BASE
    assert meta["source"] == ["mistral/reponses-generateur", "org-factice/Base-Factice", SOURCE]
    assert meta["licence"][1] == "licence-base-factice"
    # CR 3 : égalité Mistral / base → base, et entre deux bases, la température la plus basse.
    assert sortie[2]["meta"]["cible"]["appel_local_id"] == ids["s3a"].removeprefix("slm:")

    manifeste = json.loads((resultat.dossier / "MANIFEST.json").read_text("utf-8"))
    assert manifeste["schema_version"] == 2 and manifeste["variante"] == "recherche"
    assert "nettoyage" not in manifeste
    bloc = manifeste["selection"]
    assert bloc["taches"] == ["CR", "LC"] and bloc["retirees"] == ["RE"]
    assert set(bloc["verdicts"]) == set(verdicts)
    assert bloc["par_tache"]["CR"]["gagnants"] == {BASE: 2}
    assert bloc["par_tache"]["CR"]["part_base"] == 1.0
    assert bloc["par_tache"]["LC"]["ecartees"] == {"aucun_accepte": 1}
    assert bloc["candidats_ignores"] == {"refuse": 1, "sans_verdict": 1, "source_openrouter": 1}
    assert bloc["avertissements"] == ["Tâche LC : aucune ligne retenue"]
    assert bloc["sans_verdict_par_tache"] == {"LC": 1} and "runs_partiels" not in bloc
    detail = resultat.run.lire_jsonl(NOM_DETAIL)
    assert bloc["sha256_detail"] == sha256_hex((resultat.run.dossier / NOM_DETAIL).read_bytes())
    assert [d.get("gagnant") for d in detail] == [ids["s2"], ids["s3a"], None]
    assert detail[0]["notes"] == CR_PLEIN and detail[0]["score"] == 1.0

    # train run : chaîne relue, cibles locales recontrôlées dans le journal.
    jeu = charger_jeu(resultat.version, racine=tmp_path)
    assert recontroler_cibles(jeu, racine=tmp_path) == 2
    jeu.lignes[1].messages[-1]["content"] = "<reponse-factice-alteree>"
    with pytest.raises(ManifesteInvalide, match="non conforme"):
        recontroler_cibles(jeu, racine=tmp_path)


def test_gagnant_mistral_copie_et_seuils_recalcules(tmp_path: Path) -> None:
    banc = Banc(tmp_path)
    banc.mistral(2, CR_PLEIN)
    # « accepte » annoncé mais sous le seuil de couverture : non accepté (seuils recalculés).
    banc.slm(2, "<reponse-factice-slm-2>", {**CR_PLEIN, "couverture": 0.5})
    banc.mistral(3, CR_PLEIN)
    banc.slm(3, "<reponse-factice-slm-3>", CR_PLEIN, verdict="invalide")
    resultat = banc.selection(banc.runs())

    brutes = (resultat.dossier / "train.jsonl").read_bytes().split(b"\n")
    source = banc.octets.split(b"\n")
    assert brutes[1:3] == source[1:3]
    bloc = json.loads((resultat.dossier / "MANIFEST.json").read_text("utf-8"))["selection"]
    assert bloc["par_tache"]["CR"]["gagnants"] == {"mistral": 2}
    assert bloc["par_tache"]["CR"]["part_base"] == 0.0
    assert bloc["candidats_ignores"]["refuse"] == 1
    assert bloc["candidats_ignores"]["verdict_invalide"] == 1
    assert bloc["par_tache"]["LC"]["ecartees"] == {"sans_candidat": 1}
    jeu = charger_jeu(resultat.version, racine=tmp_path)
    assert recontroler_cibles(jeu, racine=tmp_path) == 0


def test_moins_de_cr_min_refuse_sans_rien_ecrire(tmp_path: Path) -> None:
    banc = Banc(tmp_path)
    banc.mistral(2, CR_PLEIN)
    verdicts = banc.runs()
    with pytest.raises(ManifesteInvalide, match="CR retenue"):
        banc.selection(verdicts, cr_min=30)
    assert sorted(p.name for p in (tmp_path / "data" / "train").iterdir()) == ["v1"]


def test_source_non_autorisee_refusee_avant_tout_run(tmp_path: Path) -> None:
    banc = Banc(tmp_path)
    banc.slm(2, "<reponse-factice-slm-2>", CR_PLEIN, source="juge:org/juge-factice")
    verdicts = banc.runs()
    with pytest.raises(ManifesteInvalide, match="non autorisée"):
        banc.selection(verdicts)
    assert not list((tmp_path / "runs" / "data-build").glob("*-selection-*"))


def test_registre_sans_base_ou_variante_diffusable_refuse(tmp_path: Path) -> None:
    banc = Banc(tmp_path, base_au_registre=False)
    banc.mistral(2, CR_PLEIN)
    verdicts = banc.runs()
    with pytest.raises(SourceSansLicence, match="modele-base"):
        banc.selection(verdicts)
    chemin = tmp_path / "data" / "registre-licences.toml"
    chemin.write_text(REGISTRE + ENTREE_BASE, "utf-8")
    banc.registre = RegistreLicences.charger(chemin, racine=tmp_path)
    with pytest.raises(UsageInterdit):
        banc.selection(verdicts, variante="diffusable")
    assert not list((tmp_path / "runs" / "data-build").glob("*-selection-*"))


def test_journal_local_non_conforme_refuse(tmp_path: Path) -> None:
    banc = Banc(tmp_path)
    banc.slm(2, "<reponse-factice-slm-2>", CR_PLEIN, session="s-autre-session-factice")
    with pytest.raises(ProvenanceInvalide, match="journal local"):
        banc.selection(banc.runs())
    assert sorted(p.name for p in (tmp_path / "data" / "train").iterdir()) == ["v1"]


def test_runs_de_jugement_incoherents(tmp_path: Path) -> None:
    banc = Banc(tmp_path)
    banc.mistral(2, CR_PLEIN)
    with pytest.raises(ManifesteInvalide, match="même juge"):
        banc.selection(banc.runs(juges=(JUGE, JUGE)))
    with pytest.raises(ManifesteInvalide, match="aucun run de jugement"):
        banc.selection(banc.runs(juges=("org/juge-croise-factice",)))
    with pytest.raises(ManifesteInvalide, match="jugement de"):
        banc.selection(banc.runs(depuis="20261020-000000-candidats-0000"))
    with pytest.raises(ManifesteInvalide, match="sélectionnée et retirée"):
        banc.selection(banc.runs(), retirer=["CR"])
    with pytest.raises(ManifesteInvalide, match="parmi"):
        banc.selection(banc.runs(), taches=["RE"])


def test_tokenizer_different_refuse(tmp_path: Path) -> None:
    banc = Banc(tmp_path)
    banc.mistral(2, CR_PLEIN)
    verdicts = banc.runs()
    with pytest.raises(ManifesteInvalide, match="tokenizer"):
        banc.selection(verdicts, tokeniseur=Tokeniseur(compter=len, sha256="e" * 64))


# --- Score et preuve ------------------------------------------------------------------------


def test_score_normalise_sur_l_echelle_de_la_grille() -> None:
    assert score("CR", {"invention": 1, "structure": 0, "couverture": 0.5}) == 0.5
    assert score("LC", {"fidelite": 1, "termes": 1}) == 0.75
    assert score("LC", {"fidelite": 3, "termes": 1}) is None
    assert score("CR", {"invention": 1, "structure": 1}) is None
    assert score("LC", {"fidelite": True, "termes": 1}) is None


def test_verifier_selection_refuse_entree_modifiee_ou_tache_retiree(tmp_path: Path) -> None:
    banc, _, verdicts = scenario(tmp_path)
    resultat = banc.selection(verdicts)
    octets = (resultat.dossier / "train.jsonl").read_bytes()
    verifier_selection(octets, banc.octets, ["CR", "LC"], ["RE"])
    sortie = lignes(resultat.dossier / "train.jsonl")
    sortie[1]["messages"][1]["content"] = "<entree-factice-modifiee>"
    altere = b"".join(json_canonique(x) + b"\n" for x in sortie)
    with pytest.raises(ProvenanceInvalide, match="même entrée"):
        verifier_selection(altere, banc.octets, ["CR", "LC"], ["RE"])
    avec_re = banc.octets.split(b"\n")
    with pytest.raises(ProvenanceInvalide, match="retirée"):
        verifier_selection(avec_re[3] + b"\n", banc.octets, ["CR", "LC"], ["RE"])
    with pytest.raises(ProvenanceInvalide, match="absente"):
        verifier_selection(avec_re[1] + b"\n", banc.octets, ["CR", "LC"], ["RE"])


def test_ligne_v2_exige_sa_cible() -> None:
    brut = ligne(9, "CR")
    with pytest.raises(ValueError, match="schema_version"):
        LigneEntrainement.model_validate({**brut, "schema_version": 2})
    with pytest.raises(ValueError, match="appel_ids"):
        LigneEntrainement.model_validate({**brut, "meta": {**brut["meta"], "appel_ids": []}})
    v1 = LigneEntrainement.model_validate(brut)
    assert "cible" not in v1.model_dump(mode="json")["meta"]  # sérialisation v1 inchangée


# --- CLI ----------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "options",
    [
        ["--selection", "--candidats", "x", "--variante", "recherche"],
        ["--selection", "--verdicts", "y", "--variante", "recherche"],
        ["--selection", "--candidats", "x", "--verdicts", "y"],
        ["--selection", "--candidats", "x", "--verdicts", "y", "--variante", "recherche"],
        ["--retirer", "RE", "--depuis", "z", "--variante", "recherche"],
        [
            "--selection",
            "--candidats",
            "x",
            "--verdicts",
            "y",
            "--variante",
            "recherche",
            "--retirer",
            "",
            "--depuis",
            "z",
        ],
        ["--candidats", "x", "--depuis", "z", "--variante", "recherche"],
        ["--variante", "recherche"],
    ],
)
def test_cli_validations(options: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["data", "build", *options]) == CodeSortie.USAGE
    assert "slmsp :" in capsys.readouterr().err


def test_cli_selection(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    banc, _, verdicts = scenario(tmp_path)
    juge = SimpleNamespace(juge_donnees=SimpleNamespace(modele=JUGE))
    monkeypatch.setattr("slmsp.cli.data.charger_config_donnees", lambda: juge)
    monkeypatch.setattr("slmsp.data.selection.tokeniseur_du_modele", lambda *_a, **_k: TOKENISEUR)
    code = main(
        [
            "data",
            "build",
            "--selection",
            "--candidats",
            banc.candidats_id,
            "--verdicts",
            ",".join(verdicts),
            "--taches-selection",
            "CR,LC",
            "--retirer",
            "RE",
            "--variante",
            "recherche",
            "--racine",
            str(tmp_path),
        ]
    )
    # Deux lignes CR seulement : sous le plancher de 30 (amendement 3), refus sans écriture.
    assert code == CodeSortie.USAGE
    assert "au moins 30" in capsys.readouterr().err
    assert sorted(p.name for p in (tmp_path / "data" / "train").iterdir()) == ["v1"]


def test_cli_erreur_de_registre_propre(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    banc = Banc(tmp_path, base_au_registre=False)
    banc.mistral(2, CR_PLEIN)
    verdicts = banc.runs()
    juge = SimpleNamespace(juge_donnees=SimpleNamespace(modele=JUGE))
    monkeypatch.setattr("slmsp.cli.data.charger_config_donnees", lambda: juge)
    monkeypatch.setattr("slmsp.data.selection.tokeniseur_du_modele", lambda *_a, **_k: TOKENISEUR)
    options = ["--candidats", banc.candidats_id, "--verdicts", ",".join(verdicts)]
    code = main(
        ["data", "build", "--selection", *options, "--retirer", "", "--variante", "recherche"]
        + ["--racine", str(tmp_path)]
    )
    assert code == CodeSortie.USAGE
    erreur = capsys.readouterr().err
    assert "modele-base" in erreur and "Traceback" not in erreur


# --- Revue : runs partiels, base, gardes ------------------------------------------------------


@pytest.mark.parametrize(
    ("candidats", "juge"), [("partiel-erreur", "complet"), ("complet", "interrompu")]
)
def test_run_source_non_complet_refuse_sauf_accepter_partiel(
    tmp_path: Path, candidats: str, juge: str
) -> None:
    banc = Banc(tmp_path)
    banc.mistral(2, CR_PLEIN)
    banc.mistral(3, CR_PLEIN)
    banc.slm(3, "<reponse-factice-slm-3>", None)  # sans verdict (jugement interrompu)
    verdicts = banc.runs(statut_candidats=candidats, statut_juge=juge)
    with pytest.raises(ManifesteInvalide, match="complet"):
        banc.selection(verdicts)
    assert not list((tmp_path / "runs" / "data-build").glob("*-selection-*"))

    resultat = banc.selection(verdicts, accepter_partiel=True)
    bloc = json.loads((resultat.dossier / "MANIFEST.json").read_text("utf-8"))["selection"]
    partiel = banc.candidats_id if candidats != "complet" else verdicts[0]
    assert bloc["runs_partiels"] == [partiel]
    assert bloc["sans_verdict_par_tache"] == {"CR": 1}
    assert any("--accepter-partiel" in a for a in bloc["avertissements"])
    assert resultat.run.manifeste.config["accepter_partiel"] is True
    charger_jeu(resultat.version, racine=tmp_path)  # MANIFEST relu par train


def test_run_source_en_cours_refuse_meme_avec_accepter_partiel(tmp_path: Path) -> None:
    banc = Banc(tmp_path)
    banc.mistral(2, CR_PLEIN)
    verdicts = banc.runs()
    nouveau = nouveau_run("data-juger", "juger", {"depuis": banc.candidats_id}, racine=tmp_path)
    with pytest.raises(ManifesteInvalide, match="en cours"):
        banc.selection([*verdicts, nouveau.run_id], accepter_partiel=True)


def test_cible_d_une_autre_base_refusee_par_train(tmp_path: Path) -> None:
    banc, _, verdicts = scenario(tmp_path)
    resultat = banc.selection(verdicts)
    jeu = charger_jeu(resultat.version, racine=tmp_path)
    assert recontroler_cibles(jeu, racine=tmp_path, base=BASE) == 2
    with pytest.raises(ManifesteInvalide, match="autre Modèle de base"):
        recontroler_cibles(jeu, racine=tmp_path, base="slm:autre-base-factice")


def test_jeu_selectionne_refuse_par_les_etapes_aval(tmp_path: Path) -> None:
    from slmsp.data.candidats import lancer_candidats
    from slmsp.data.nettoyage import lancer_nettoyage
    from slmsp.data.preferences import lancer_preferences
    from slmsp.data.sous_ensemble import lancer_sous_ensemble

    banc, _, verdicts = scenario(tmp_path)
    build = banc.selection(verdicts).run.run_id
    commun: dict[str, Any] = {"racine": tmp_path, "build_run_id": build}
    appels = [
        lambda: lancer_preferences(**commun, modele="base:base-factice", llm=None, config=None),
        lambda: lancer_candidats(
            **commun,
            taches=["CR"],
            slug="base-factice",
            temperatures=[0.3],
            llm=None,
            config=None,
            plafond_tokens=200,
        ),
        lambda: lancer_nettoyage(**commun, modele="base:base-factice", plafond_tokens=200),
        lambda: lancer_sous_ensemble(**commun, taches=["CR"]),
    ]
    for appel in appels:
        with pytest.raises(ManifesteInvalide, match="sélectionnées"):
            appel()
