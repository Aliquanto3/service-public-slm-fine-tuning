"""`Generateur` : requête prouvée, préalables, jeton et journal (AD-3 verrous 3, 5 et 6, D1.2).

Faux serveur Mistral (`tests/mistral/conftest.py`), racine, artefact `seed`, cassettes et
journaux dans `tmp_path`. Aucun appel réel. Toutes les amorces et réponses sont des chaînes
factices aléatoires (D1.1) : aucun texte de Donnée d'entraînement n'est rédigé ici.
"""

from __future__ import annotations

import inspect
import json
import secrets
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

pytest.importorskip("mistralai")

from slmsp.core.canonique import json_canonique, sha256_hex  # noqa: E402
from slmsp.core.config import plafonds_re_evaluation, racine_projet  # noqa: E402
from slmsp.core.erreurs import ConfigurationInvalide, ProvenanceInvalide  # noqa: E402
from slmsp.core.gabarits import GabaritInvalide, valider_gabarit  # noqa: E402
from slmsp.core.schemas.amorce import Amorce  # noqa: E402
from slmsp.mistral.client import ModeleMistralRefuse  # noqa: E402
from slmsp.mistral.generateur import (  # noqa: E402
    _JETON,
    Generateur,
    PrealableNonSatisfait,
    message_assistant,
)
from slmsp.mistral.journal import JournalMistral, journal_pour  # noqa: E402

JOUR = date(2026, 10, 12)
SEED = "20261012-000000-seed-factice-0a1b"
SEED_2 = "20261012-000001-seed-factice-0a1c"
GABARITS = racine_projet() / "config" / "prompts" / "generateur"
OUTILS_MCP = racine_projet() / "config" / "outils-mcp.toml"
JOURNAL_DONNEES = "appels-mistral.sqlite"
REPONSE = "<réponse-factice-1>"
DONNEES = """
[mistral]
conditions_verifiees_le = 2026-10-12
modeles_stables = ["mistral-large-latest", "mistral-large-2512"]
cle_en_plus = "ignoree"

[autre_table]
seuil = 1

[generateur.plafonds_mots]
Q = 160
RD = 120
CR = 400
LC = 150
CT = 150
generique = 200
"""


def factice(prefixe: str = "amorce") -> str:
    return f"<{prefixe}-factice-{secrets.token_hex(4)}>"


def amorce(
    amorce_id: str,
    tache: str,
    emplacement: str,
    *,
    auteur: str = "public",
    texte: str | None = None,
    **champs: Any,
) -> dict[str, Any]:
    texte = texte if texte is not None else factice()
    valeurs: dict[str, Any] = {
        "schema_version": 1,
        "amorce_id": amorce_id,
        "tache": tache,
        "emplacement": emplacement,
        "texte": texte,
        "sha_texte": sha256_hex(texte),
        "auteur_contenu": auteur,
    }
    if auteur == "public":
        valeurs.update(jeu="jeu-factice", revision="rev-factice", ligne=7)
    valeurs.update(champs)
    return valeurs


@dataclass
class Monde:
    racine: Path
    banc: Any

    def ecrire_seed(self, amorces: list[dict[str, Any]], run_id: str = SEED) -> None:
        dossier = self.racine / "runs" / "data-seed" / run_id
        dossier.mkdir(parents=True, exist_ok=True)
        lignes = b"".join(json_canonique(a) + b"\n" for a in amorces)
        (dossier / "amorces.jsonl").write_bytes(lignes)

    def generateur(self, run_id: str = SEED, **options: Any) -> Generateur:
        valeurs: dict[str, Any] = {
            "client": self.banc.client(),
            "racine": self.racine,
            "dossier_gabarits": GABARITS,
            "fichier_outils": OUTILS_MCP,
            "aujourd_hui": lambda: JOUR,
        }
        return Generateur(run_id, **{**valeurs, **options})

    def journal(self) -> JournalMistral:
        return journal_pour("generation", self.banc.config, self.banc.dossier)

    def journaliser(self, session_id: str, message: dict[str, Any], statut: str = "ok") -> str:
        """Ligne `generation` déjà journalisée (réponse brute au format de l'API)."""
        brut = json.dumps({"choices": [{"index": 0, "message": message}]}).encode()
        return self.journal().inscrire(
            session_id=session_id,
            usage="generation",
            modele_demande="mistral-large-latest",
            modele_resolu="mistral-large-2512",
            requete={"messages": []},
            reponse_brute=brut,
            reservation_id=None,
            statut=statut,  # type: ignore[arg-type]
            statut_http=200,
            jeton=_JETON,
            gabarit_id="generique",
            version_gabarit=1,
            sha256_gabarit="0" * 64,
            amorce_ids=["amorce-anterieure"],
        )

    def cassette(
        self,
        session_id: str,
        resultats: list[tuple[str, Any]],
        arguments: dict[str, Any] | None = None,
    ) -> None:
        interactions = [
            {
                "request": {
                    "jsonrpc": "2.0",
                    "id": i,
                    "method": "tools/call",
                    "params": {"name": nom, "arguments": arguments or {}},
                },
                "response": {"jsonrpc": "2.0", "id": i, "result": resultat},
            }
            for i, (nom, resultat) in enumerate(resultats, start=1)
        ]
        contenu = {
            "schema_version": 1,
            "server": "serveur-factice",
            "recorded_at": "2026-10-12T00:00:00+00:00",
            "initialize": None,
            "tools_list_sha256": "0" * 64,
            "interactions": interactions,
        }
        dossier = self.racine / "data" / "cassettes"
        dossier.mkdir(parents=True, exist_ok=True)
        (dossier / f"{session_id}.json").write_text(json.dumps(contenu), encoding="utf-8")

    def rien_n_est_parti(self) -> None:
        assert self.banc.faux.requetes == []
        assert self.banc.lignes_registre() == []


@pytest.fixture
def monde(banc: Any, tmp_path: Path) -> Monde:
    racine = tmp_path / "racine"
    (racine / "config").mkdir(parents=True)
    (racine / "config" / "donnees.toml").write_text(DONNEES, encoding="utf-8")
    banc.faux.texte_par_defaut = lambda corps: REPONSE
    return Monde(racine=racine, banc=banc)


def consigne(gabarit_id: str) -> str:
    return valider_gabarit(
        GABARITS / f"{gabarit_id}.md", cles_optionnelles=("max_tokens",)
    ).consigne


# --- Signature et requête -------------------------------------------------------------------


def test_signature_sans_texte_libre() -> None:
    parametres = list(inspect.signature(Generateur.generer).parameters)
    assert parametres == [
        "self",
        "gabarit_id",
        "amorce_ids",
        "session_id",
        "tache",
        "messages_precedents",
    ]


def test_appel_nominal(monde: Monde) -> None:
    graine = amorce("demande-1", "generique", "demande")
    monde.ecrire_seed([graine, amorce("autre-1", "Q", "question")])
    generation = monde.generateur().generer("generique", ["demande-1"], "session-1", "generique")

    rendue = (
        consigne("generique")
        .replace("{demande}", graine["texte"])
        .replace("{plafond_mots_tache}", "200")
    )
    (corps,) = monde.banc.faux.corps()
    assert corps["messages"] == [{"role": "user", "content": rendue}]
    assert graine["texte"] in corps["messages"][0]["content"]
    assert corps["max_tokens"] == 800
    assert "tools" not in corps and "tool_choice" not in corps

    (ligne,) = monde.banc.lignes_journal(JOURNAL_DONNEES)
    octets = (GABARITS / "generique.md").read_bytes()
    assert ligne["appel_id"] == generation.appel_id
    assert ligne["session_id"] == "session-1" and ligne["usage"] == "generation"
    assert ligne["statut"] == "ok"
    assert ligne["modele_demande"] == "mistral-large-latest"
    assert ligne["modele_resolu"] == "mistral-large-2512"
    assert json.loads(ligne["requete"]) == corps
    assert ligne["gabarit_id"] == "generique" and ligne["version_gabarit"] == 2
    assert ligne["sha256_gabarit"] == sha256_hex(octets)
    assert json.loads(ligne["amorce_ids"]) == ["demande-1"]
    assert ligne["reponse_brute"] == monde.banc.faux.servis[0]
    assert ligne["sha256_reponse"] == sha256_hex(monde.banc.faux.servis[0])
    assert ligne["reservation_id"] == generation.reponse.reservation_id

    assert generation.reponse.texte == REPONSE
    assert generation.reponse_brute == monde.banc.faux.servis[0]
    assert generation.sha256_gabarit == sha256_hex(octets)
    assert generation.amorce_ids == ("demande-1",)
    assert list(generation.messages) == corps["messages"]
    assert message_assistant(generation.reponse_brute) == {"role": "assistant", "content": REPONSE}
    (reservation,) = monde.banc.lignes_registre()
    assert (reservation["poste"], reservation["sous_poste"]) == ("mistral", "generation")


def test_rendu_groupe_par_emplacement_en_une_passe(monde: Monde) -> None:
    """Amorces jointes par emplacement dans l'ordre demandé ; un `{x}` d'amorce reste tel quel ;
    `{plafond_mots}` est dérivé de la longueur du Jeu, pas écrit par une amorce."""
    piege = f"<amorce-factice-{secrets.token_hex(2)} {{texte}}>"
    graines = [
        amorce("texte-a", "RE", "texte", texte=piege),
        amorce("longueur", "RE", "longueur_demandee", texte="courte"),
        amorce("texte-b", "RE", "texte"),
    ]
    monde.ecrire_seed(graines)
    monde.generateur().generer("re", ["texte-b", "longueur", "texte-a"], "session-re", "RE")
    attendue = (
        consigne("re")
        .replace("{texte}", graines[2]["texte"] + "\n\n" + graines[0]["texte"])
        .replace("{longueur_demandee}", "courte")
        .replace("{plafond_mots}", "80")
    )
    (corps,) = monde.banc.faux.corps()
    assert corps["messages"] == [{"role": "user", "content": attendue}]
    assert "le résumé ne dépasse pas 80 mots" in corps["messages"][0]["content"]
    assert corps["max_tokens"] == 1500  # front-matter du gabarit
    (ligne,) = monde.banc.lignes_journal(JOURNAL_DONNEES)
    assert json.loads(ligne["amorce_ids"]) == ["texte-b", "longueur", "texte-a"]


@pytest.mark.parametrize(("mot", "plafond"), [("courte", 80), ("moyenne", 200), ("detaillee", 400)])
def test_plafond_mots_derive_de_evaluation_toml(monde: Monde, mot: str, plafond: int) -> None:
    attendus = plafonds_re_evaluation()
    assert attendus[mot] == plafond  # [re.longueurs] de config/evaluation.toml
    monde.ecrire_seed(
        [amorce("t", "RE", "texte"), amorce("l", "RE", "longueur_demandee", texte=mot)]
    )
    generation = monde.generateur().generer("re", ["t", "l"], "session-re", "RE")
    contenu = generation.messages[0]["content"]
    assert f"ne dépasse pas {plafond} mots" in contenu
    assert "{plafond_mots}" not in contenu


def test_longueur_inconnue_refusee_avant_l_appel(monde: Monde) -> None:
    monde.ecrire_seed(
        [amorce("t", "RE", "texte"), amorce("l", "RE", "longueur_demandee", texte="80 mots")]
    )
    with pytest.raises(GabaritInvalide, match="plafond_mots"):
        monde.generateur().generer("re", ["t", "l"], "s", "RE")
    monde.rien_n_est_parti()


def test_amorce_sur_l_emplacement_plafond_refusee(monde: Monde) -> None:
    monde.ecrire_seed([amorce("t", "RE", "texte"), amorce("p", "RE", "plafond_mots", texte="9")])
    with pytest.raises(ProvenanceInvalide, match="plafond_mots"):
        monde.generateur().generer("re", ["t", "p"], "s", "RE")
    monde.rien_n_est_parti()


def test_estimation_des_tokens(monde: Monde) -> None:
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    monde.generateur().generer("generique", ["d"], "s", "generique")
    (corps,) = monde.banc.faux.corps()
    caracteres = len(json_canonique(corps["messages"][0]).decode())
    (reservation,) = monde.banc.lignes_registre()
    pire_cas = (-(-caracteres // 3) + corps["max_tokens"]) / 1_000_000  # tarifs de test
    assert reservation["montant_reserve_eur"] == pytest.approx(pire_cas)


# --- Préalables (D1.2) ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "contenu",
    [
        None,  # fichier absent
        "[autre]\ncle = 1\n",  # table absente
        '[mistral]\nmodeles_stables = ["mistral-large-latest"]\n',  # date absente
        DONNEES.replace("2026-10-12", "2026-10-11"),  # date périmée
        DONNEES.replace('"mistral-large-latest", ', ""),  # modèle demandé hors liste stable
        "[mistral\n",  # TOML invalide
    ],
)
def test_prealables_non_satisfaits(monde: Monde, contenu: str | None) -> None:
    fichier = monde.racine / "config" / "donnees.toml"
    if contenu is None:
        fichier.unlink()
    else:
        fichier.write_text(contenu, encoding="utf-8")
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    with pytest.raises(PrealableNonSatisfait):
        monde.generateur()
    monde.rien_n_est_parti()


def test_date_du_jour_injectable(monde: Monde) -> None:
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    with pytest.raises(PrealableNonSatisfait):
        monde.generateur(aujourd_hui=lambda: date(2026, 10, 13))


def test_fichier_donnees_explicite(monde: Monde, tmp_path: Path) -> None:
    autre = tmp_path / "donnees-autres.toml"
    autre.write_text(DONNEES, encoding="utf-8")
    (monde.racine / "config" / "donnees.toml").unlink()
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    generateur = monde.generateur(fichier_donnees=autre)
    assert generateur.prealables.conditions_verifiees_le == JOUR


def test_modele_resolu_hors_liste_stable(monde: Monde) -> None:
    """Autorisé par `mistral.toml` mais absent de `modeles_stables` : refusé, appel journalisé."""
    monde.banc.faux.modele_resolu = "mistral-large-2411"
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    with pytest.raises(ModeleMistralRefuse):
        monde.generateur().generer("generique", ["d"], "s", "generique")
    (ligne,) = monde.banc.lignes_journal(JOURNAL_DONNEES)
    assert ligne["modele_resolu"] == "mistral-large-2411" and ligne["usage"] == "generation"


@pytest.mark.parametrize("reemploi", ["amorce", "precedent"])
def test_appel_refuse_pour_modele_jamais_reutilise(monde: Monde, reemploi: str) -> None:
    """La ligne `ok` d'un appel refusé (modèle hors `modeles_stables`) n'est ni amorce ni
    précédent."""
    monde.banc.faux.modele_resolu = "mistral-large-2411"
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    with pytest.raises(ModeleMistralRefuse):
        monde.generateur().generer("generique", ["d"], "session-g", "generique")
    (ligne,) = monde.banc.lignes_journal(JOURNAL_DONNEES)
    assert ligne["statut"] == "ok"
    monde.banc.faux.modele_resolu = "mistral-large-2512"
    graines = [amorce("d", "generique", "demande")]
    if reemploi == "amorce":
        graines = [
            amorce(
                "d",
                "generique",
                "demande",
                auteur="mistral",
                texte=REPONSE,
                appel_id=ligne["appel_id"],
            )
        ]
    monde.ecrire_seed(graines, SEED_2)
    precedents = [{"role": "assistant", "content": REPONSE}] if reemploi == "precedent" else None
    with pytest.raises(ProvenanceInvalide):
        monde.generateur(SEED_2).generer("generique", ["d"], "session-g", "generique", precedents)
    assert len(monde.banc.faux.requetes) == 1  # rien de plus n'est parti
    assert len(monde.banc.lignes_journal(JOURNAL_DONNEES)) == 1


def test_date_rechecked_a_chaque_generation(monde: Monde) -> None:
    """Un Générateur construit la veille de minuit refuse de générer le lendemain (D1.2)."""
    jours = iter([JOUR, date(2026, 10, 13)])
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    generateur = monde.generateur(aujourd_hui=lambda: next(jours))
    with pytest.raises(PrealableNonSatisfait):
        generateur.generer("generique", ["d"], "s", "generique")
    monde.rien_n_est_parti()


# --- Gabarits ---------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "gabarit_id",
    ["Rédige une demande sur un thème", "../lc", "lc.md", "LC", "absent", "", "tâche"],
)
def test_gabarit_id_libre_refuse(monde: Monde, gabarit_id: str) -> None:
    monde.ecrire_seed([amorce("t", "LC", "texte")])
    with pytest.raises(GabaritInvalide):
        monde.generateur().generer(gabarit_id, ["t"], "s", "LC")
    monde.rien_n_est_parti()


def test_tache_differente_du_gabarit(monde: Monde) -> None:
    monde.ecrire_seed([amorce("t", "LC", "texte"), amorce("t2", "CO", "texte")])
    with pytest.raises(GabaritInvalide):
        monde.generateur().generer("lc", ["t2"], "s", "CO")
    monde.rien_n_est_parti()


def test_gabarit_validation_inutilisable(monde: Monde) -> None:
    monde.ecrire_seed([amorce("s", "validation", "source"), amorce("t", "validation", "texte")])
    with pytest.raises(GabaritInvalide):
        monde.generateur().generer("validation", ["s", "t"], "s", "validation")
    monde.rien_n_est_parti()


def _ecrire_gabarit(dossier: Path, nom: str, corps: str, front: str = "") -> None:
    dossier.mkdir(parents=True, exist_ok=True)
    texte = f"---\nid: {nom}\nversion: 1\ntache: generique\n{front}---\n\n{corps}"
    (dossier / f"{nom}.md").write_text(texte, encoding="utf-8")


@pytest.mark.parametrize(
    ("corps", "front"),
    [
        # mot interdit par la liste blanche de core.gabarits
        ("## Consigne\n\nUn exemple {a}.\n\n## Emplacements\n\n- a : amorce.\n", ""),
        # emplacement déclaré mais absent de la consigne
        ("## Consigne\n\nConsigne {a}.\n\n## Emplacements\n\n- a : amorce.\n- b : autre.\n", ""),
        # emplacement de la consigne non déclaré : accolade hors liste
        ("## Consigne\n\nConsigne {a} {b}.\n\n## Emplacements\n\n- a : amorce.\n", ""),
        # max_tokens non entier
        ("## Consigne\n\nConsigne {a}.\n\n## Emplacements\n\n- a : amorce.\n", "max_tokens: x\n"),
        # clé de front-matter inconnue
        ("## Consigne\n\nConsigne {a}.\n\n## Emplacements\n\n- a : amorce.\n", "libre: x\n"),
    ],
)
def test_gabarit_invalide(monde: Monde, tmp_path: Path, corps: str, front: str) -> None:
    dossier = tmp_path / "gabarits"
    _ecrire_gabarit(dossier, "g", corps, front)
    monde.ecrire_seed([amorce("a", "generique", "a")])
    with pytest.raises(GabaritInvalide):
        monde.generateur(dossier_gabarits=dossier).generer("g", ["a"], "s", "generique")
    monde.rien_n_est_parti()


def test_front_matter_id_different(monde: Monde, tmp_path: Path) -> None:
    dossier = tmp_path / "gabarits"
    _ecrire_gabarit(dossier, "g", "## Consigne\n\nConsigne {a}.\n\n## Emplacements\n\n- a : x.\n")
    (dossier / "h.md").write_bytes((dossier / "g.md").read_bytes())
    monde.ecrire_seed([amorce("a", "generique", "a")])
    with pytest.raises(GabaritInvalide):
        monde.generateur(dossier_gabarits=dossier).generer("h", ["a"], "s", "generique")
    monde.rien_n_est_parti()


def test_emplacement_sans_amorce(monde: Monde) -> None:
    monde.ecrire_seed([amorce("t", "RE", "texte")])
    with pytest.raises(GabaritInvalide):
        monde.generateur().generer("re", ["t"], "s", "RE")
    monde.rien_n_est_parti()


def test_amorce_hors_emplacements(monde: Monde) -> None:
    monde.ecrire_seed([amorce("d", "generique", "demande"), amorce("x", "generique", "theme")])
    with pytest.raises(GabaritInvalide):
        monde.generateur().generer("generique", ["d", "x"], "s", "generique")
    monde.rien_n_est_parti()


def test_tache_inconnue(monde: Monde) -> None:
    monde.ecrire_seed([amorce("d", "TR", "demande")])
    with pytest.raises(GabaritInvalide):
        monde.generateur().generer("generique", ["d"], "s", "TR")
    monde.rien_n_est_parti()


# --- Amorces --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "amorce_ids",
    [
        ["inconnue"],
        ["Rédige une demande sur un thème"],
        "d",  # chaîne nue
        [],
        ["d", "d"],
        [42],
    ],
)
def test_amorce_ids_refuses(monde: Monde, amorce_ids: Any) -> None:
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    with pytest.raises(ProvenanceInvalide):
        monde.generateur().generer("generique", amorce_ids, "s", "generique")
    monde.rien_n_est_parti()


@pytest.mark.parametrize(
    "graine",
    [
        amorce("d", "generique", "demande", sha_texte="f" * 64),
        amorce("d", "generique", "demande", auteur="anael"),
        amorce("d", "Q", "demande"),  # tâche de l'amorce différente
        amorce("d", "generique", "demande", auteur="mistral", appel_id="a" * 32),  # inconnu
    ],
    ids=["sha-faux", "anael", "tache", "mistral-inconnu"],
)
def test_amorce_refusee(monde: Monde, graine: dict[str, Any]) -> None:
    monde.ecrire_seed([graine])
    with pytest.raises(ProvenanceInvalide):
        monde.generateur().generer("generique", ["d"], "s", "generique")
    monde.rien_n_est_parti()


def test_amorce_mistral_journalisee(monde: Monde) -> None:
    """Chaîne `scenario-reunion` puis `transcription-cr` : la réponse journalisée sert d'amorce."""
    monde.ecrire_seed([amorce("theme", "CR", "theme")])
    premiere = monde.generateur().generer("scenario-reunion", ["theme"], "session-cr", "CR")
    monde.ecrire_seed(
        [
            amorce(
                "scenario",
                "CR",
                "scenario",
                auteur="mistral",
                texte=REPONSE,
                appel_id=premiere.appel_id,
            )
        ],
        SEED_2,
    )
    monde.generateur(SEED_2).generer("transcription-cr", ["scenario"], "session-cr", "CR")
    lignes = monde.banc.lignes_journal(JOURNAL_DONNEES)
    assert len(lignes) == 2
    assert REPONSE in monde.banc.faux.corps()[1]["messages"][0]["content"]
    assert json.loads(lignes[1]["amorce_ids"]) == ["scenario"]


@pytest.mark.parametrize("cas", ["texte-different", "statut-erreur", "validation"])
def test_amorce_mistral_refusee(monde: Monde, cas: str) -> None:
    if cas == "validation":
        appel_id = monde.journal().inscrire(
            session_id="s",
            usage="validation",
            modele_demande="mistral-large-latest",
            modele_resolu="mistral-large-2512",
            requete={},
            reponse_brute=json.dumps(
                {"choices": [{"message": {"role": "assistant", "content": REPONSE}}]}
            ).encode(),
            reservation_id=None,
            statut="ok",
            statut_http=200,
        )
    else:
        statut = "erreur" if cas == "statut-erreur" else "ok"
        appel_id = monde.journaliser("s", {"role": "assistant", "content": REPONSE}, statut)
    texte = factice("reponse") if cas == "texte-different" else REPONSE
    monde.ecrire_seed(
        [amorce("d", "generique", "demande", auteur="mistral", texte=texte, appel_id=appel_id)]
    )
    with pytest.raises(ProvenanceInvalide):
        monde.generateur().generer("generique", ["d"], "s", "generique")
    monde.rien_n_est_parti()


# --- Artefact seed --------------------------------------------------------------------------


def test_seed_absent(monde: Monde) -> None:
    with pytest.raises(ProvenanceInvalide):
        monde.generateur()


@pytest.mark.parametrize("run_id", ["seed", "../eval", "20261012-000000-seed-factice-0A1B"])
def test_seed_run_id_invalide(monde: Monde, run_id: str) -> None:
    with pytest.raises(ProvenanceInvalide):
        monde.generateur(run_id)


def test_seed_amorce_en_double(monde: Monde) -> None:
    monde.ecrire_seed([amorce("d", "generique", "demande"), amorce("d", "generique", "demande")])
    with pytest.raises(ProvenanceInvalide):
        monde.generateur()


def test_seed_ligne_non_conforme(monde: Monde) -> None:
    monde.ecrire_seed([{**amorce("d", "generique", "demande"), "auteur_contenu": "claude"}])
    with pytest.raises(ProvenanceInvalide):
        monde.generateur()


# --- Messages précédents ----------------------------------------------------------------------

APPEL_OUTIL = {
    "id": "appelfactice01",
    "type": "function",
    "function": {"name": "outil_factice", "arguments": "{}"},
}


def _seed_rd(monde: Monde) -> None:
    monde.ecrire_seed([amorce("d", "RD", "demande")])


def test_precedents_assistant_et_tool_admis(monde: Monde) -> None:
    _seed_rd(monde)
    resultat = factice("resultat")
    # L'API ajoute `index` aux appels d'outil : réduit par `message_assistant`.
    monde.journaliser(
        "session-rd",
        {"role": "assistant", "content": "", "tool_calls": [{**APPEL_OUTIL, "index": 0}]},
    )
    monde.cassette(
        "session-rd", [("outil_factice", {"content": [{"type": "text", "text": resultat}]})]
    )
    outil = {
        "role": "tool",
        "tool_call_id": "appelfactice01",
        "name": "outil_factice",
        "content": resultat,
    }
    precedents = [{"role": "assistant", "content": None, "tool_calls": [APPEL_OUTIL]}, outil]
    generation = monde.generateur().generer("traces-rd", ["d"], "session-rd", "RD", precedents)
    assert list(generation.messages[1:]) == [
        {"role": "assistant", "tool_calls": [APPEL_OUTIL]},
        outil,
    ]
    (corps,) = monde.banc.faux.corps()  # corps envoyé par le SDK (valeurs par défaut ajoutées)
    assert [m["role"] for m in corps["messages"]] == ["user", "assistant", "tool"]
    assert corps["messages"][1]["tool_calls"][0]["id"] == "appelfactice01"
    assert corps["messages"][2]["content"] == resultat
    (ligne,) = [
        ligne
        for ligne in monde.banc.lignes_journal(JOURNAL_DONNEES)
        if ligne["appel_id"] == generation.appel_id
    ]
    assert json.loads(ligne["requete"]) == corps


def test_precedent_tool_en_json_canonique(monde: Monde) -> None:
    _seed_rd(monde)
    resultat = {"structuredContent": {"valeur": factice("valeur")}}
    monde.journaliser("session-rd", {"role": "assistant", "tool_calls": [APPEL_OUTIL]})
    monde.cassette("session-rd", [("outil_factice", resultat)])
    precedents = [
        {"role": "assistant", "tool_calls": [APPEL_OUTIL]},
        {
            "role": "tool",
            "tool_call_id": "appelfactice01",
            "content": json_canonique(resultat).decode(),
        },
    ]
    monde.generateur().generer("traces-rd", ["d"], "session-rd", "RD", precedents)
    assert len(monde.banc.faux.requetes) == 1


def test_precedent_assistant_texte(monde: Monde) -> None:
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    monde.journaliser("session-g", {"role": "assistant", "content": REPONSE})
    precedents = [{"role": "assistant", "content": REPONSE}]
    generation = monde.generateur().generer(
        "generique", ["d"], "session-g", "generique", precedents
    )
    assert generation.messages[1] == {"role": "assistant", "content": REPONSE}
    (corps,) = monde.banc.faux.corps()
    assert corps["messages"][1]["content"] == REPONSE


@pytest.mark.parametrize(
    "cas",
    [
        "autre-session",
        "contenu-modifie",
        "cle-en-plus",
        "statut-erreur",
        "role-user",
        "role-system",
        "role-inconnu",
        "non-objet",
        "chaine-nue",
        "usage-validation",
    ],
)
def test_precedent_assistant_refuse(monde: Monde, cas: str) -> None:
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    session = "autre" if cas == "autre-session" else "session-g"
    if cas == "usage-validation":  # même session, même contenu, mais usage `validation`
        monde.journal().inscrire(
            session_id="session-g",
            usage="validation",
            modele_demande="mistral-large-latest",
            modele_resolu="mistral-large-2512",
            requete={},
            reponse_brute=json.dumps(
                {"choices": [{"message": {"role": "assistant", "content": REPONSE}}]}
            ).encode(),
            reservation_id=None,
            statut="ok",
            statut_http=200,
        )
    else:
        monde.journaliser(
            session,
            {"role": "assistant", "content": REPONSE},
            "erreur" if cas == "statut-erreur" else "ok",
        )
    message: Any = {"role": "assistant", "content": REPONSE}
    if cas == "contenu-modifie":
        message = {"role": "assistant", "content": factice("reponse")}
    elif cas == "cle-en-plus":
        message = {**message, "prefix": True}
    elif cas == "role-user":
        message = {"role": "user", "content": factice("texte")}
    elif cas == "role-system":
        message = {"role": "system", "content": factice("texte")}
    elif cas == "role-inconnu":
        message = {"content": REPONSE}
    elif cas == "non-objet":
        message = REPONSE
    precedents: Any = REPONSE if cas == "chaine-nue" else [message]
    with pytest.raises(ProvenanceInvalide):
        monde.generateur().generer("generique", ["d"], "session-g", "generique", precedents)
    monde.rien_n_est_parti()


@pytest.mark.parametrize(
    "cas",
    [
        "sans-cassette",
        "autre-session",
        "contenu-different",
        "nom-different",
        "tool-orphelin",
        "arguments-differents",
        "cle-en-plus",
        "reponse-en-double",
    ],
)
def test_precedent_tool_refuse(monde: Monde, cas: str) -> None:
    _seed_rd(monde)
    resultat = factice("resultat")
    monde.journaliser("session-rd", {"role": "assistant", "tool_calls": [APPEL_OUTIL]})
    if cas != "sans-cassette":
        session = "autre-rd" if cas == "autre-session" else "session-rd"
        # `arguments-differents` : même contenu, mais l'interaction répond à un autre appel.
        arguments = {"cle": factice("argument")} if cas == "arguments-differents" else None
        monde.cassette(
            session,
            [("outil_factice", {"content": [{"type": "text", "text": resultat}]})],
            arguments=arguments,
        )
    outil = {
        "role": "tool",
        "tool_call_id": "appelfactice01",
        "name": "autre_outil" if cas == "nom-different" else "outil_factice",
        "content": factice("resultat") if cas == "contenu-different" else resultat,
    }
    if cas == "cle-en-plus":  # texte libre glissé hors des clés admises (verrou 3)
        outil["prefix"] = factice("texte-libre")
    precedents = (
        [outil]
        if cas == "tool-orphelin"
        else [
            {"role": "assistant", "tool_calls": [APPEL_OUTIL]},
            outil,
            *([dict(outil)] if cas == "reponse-en-double" else []),
        ]
    )
    with pytest.raises(ProvenanceInvalide):
        monde.generateur().generer("traces-rd", ["d"], "session-rd", "RD", precedents)
    monde.rien_n_est_parti()


@pytest.mark.parametrize("session_id", ["../eval", "a/b", "", "session id", ".cache"])
def test_session_id_invalide(monde: Monde, session_id: str) -> None:
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    with pytest.raises(ProvenanceInvalide):
        monde.generateur().generer("generique", ["d"], session_id, "generique")
    monde.rien_n_est_parti()


# --- message_assistant et schéma Amorce -------------------------------------------------------


def test_message_assistant() -> None:
    def brut(message: Any) -> bytes:
        return json.dumps({"choices": [{"message": message}]}).encode()

    assert message_assistant(brut({"role": "assistant", "content": REPONSE, "prefix": False})) == {
        "role": "assistant",
        "content": REPONSE,
    }
    assert message_assistant(
        brut({"role": "assistant", "content": "", "tool_calls": [APPEL_OUTIL]})
    ) == {"role": "assistant", "tool_calls": [APPEL_OUTIL]}
    for mauvais in (
        None,
        b"pas du json",
        json.dumps({"choices": []}).encode(),
        brut({"role": "assistant", "content": "", "tool_calls": []}),
        brut({"role": "user", "content": REPONSE}),
    ):
        with pytest.raises(ProvenanceInvalide):
            message_assistant(mauvais)


@pytest.mark.parametrize(
    "champs",
    [
        {"auteur_contenu": "public", "ligne": None},
        {"auteur_contenu": "public", "jeu": None},
        {"auteur_contenu": "public", "appel_id": "a" * 32},
        {"auteur_contenu": "mistral"},
        {"auteur_contenu": "claude"},
        {"amorce_id": "Amorce libre"},
        {"emplacement": "Demande"},
        {"sha_texte": "abc"},
        {"schema_version": 2},
        {"inconnue": 1},
        # une seule provenance : pas de ligne de jeu public sur une amorce Mistral ou anael
        {"auteur_contenu": "mistral", "appel_id": "a" * 32, "revision": None, "ligne": None},
        {"auteur_contenu": "mistral", "appel_id": "a" * 32, "jeu": None, "revision": None},
        {"auteur_contenu": "anael", "jeu": None, "ligne": None},
    ],
)
def test_schema_amorce_refuse(champs: dict[str, Any]) -> None:
    valeurs = {**amorce("d", "generique", "demande"), **champs}
    with pytest.raises(ValidationError):
        Amorce.model_validate(valeurs)


def test_schema_amorce_conforme() -> None:
    Amorce.model_validate(amorce("d", "generique", "demande"))
    Amorce.model_validate(amorce("m", "CR", "scenario", auteur="mistral", appel_id="b" * 32))
    Amorce.model_validate(amorce("n", "CR", "scenario", auteur="anael"))  # refusée au Générateur


# --- Extensions de la story 9.4 : outils, passages, amorce dérivée, cassettes par tour ---------


def test_rd_envoie_les_outils_figes(monde: Monde) -> None:
    from slmsp.mcp.outils import charger_outils

    monde.ecrire_seed([amorce("d", "RD", "demande"), amorce("g", "generique", "demande")])
    generateur = monde.generateur()
    assert generateur.outils() == charger_outils(OUTILS_MCP)
    generateur.generer("traces-rd", ["d"], "session-rd", "RD")
    generateur.generer("generique", ["g"], "session-g", "generique")
    rd, generique = monde.banc.faux.corps()
    assert rd["tools"] == charger_outils(OUTILS_MCP) and rd["tool_choice"] == "auto"
    assert "tools" not in generique and "tool_choice" not in generique
    (ligne, _) = monde.banc.lignes_journal(JOURNAL_DONNEES)
    assert json.loads(ligne["requete"])["tools"] == rd["tools"]  # journalisés avec la requête


def test_rd_fichier_outils_illisible(monde: Monde, tmp_path: Path) -> None:
    from slmsp.core.erreurs import ConfigurationInvalide

    _seed_rd(monde)
    generateur = monde.generateur(fichier_outils=tmp_path / "absent.toml")
    with pytest.raises(ConfigurationInvalide):
        generateur.generer("traces-rd", ["d"], "session-rd", "RD")
    monde.rien_n_est_parti()


def test_passages_rendus_par_le_resolveur(monde: Monde) -> None:
    rendu = factice("passages")
    vus: list[str] = []

    def rendre(session_id: str) -> str:
        vus.append(session_id)
        return rendu

    question = amorce("q", "Q", "question")
    monde.ecrire_seed([question])
    monde.generateur(rendre_passages=rendre).generer("traces-q", ["q"], "session-q", "Q")
    attendu = (
        consigne("traces-q")
        .replace("{question}", question["texte"])
        .replace("{plafond_mots_tache}", "160")
    )
    (corps,) = monde.banc.faux.corps()
    assert corps["messages"][0]["content"] == attendu.replace("{passages}", rendu)
    assert vus == ["session-q"]


def test_passages_sans_resolveur_refuses(monde: Monde) -> None:
    monde.ecrire_seed([amorce("q", "Q", "question")])
    with pytest.raises(ProvenanceInvalide):
        monde.generateur().generer("traces-q", ["q"], "session-q", "Q")
    monde.rien_n_est_parti()


def test_amorce_passages_refusee(monde: Monde) -> None:
    monde.ecrire_seed([amorce("q", "Q", "question"), amorce("p", "Q", "passages")])
    generateur = monde.generateur(rendre_passages=lambda _sid: factice())
    with pytest.raises(ProvenanceInvalide):
        generateur.generer("traces-q", ["q", "p"], "session-q", "Q")
    monde.rien_n_est_parti()


def _journaliser_brut(monde: Monde, corps: dict[str, Any]) -> str:
    return monde.journal().inscrire(
        session_id="session-cr",
        usage="generation",
        modele_demande="mistral-large-latest",
        modele_resolu="mistral-large-2512",
        requete={"messages": []},
        reponse_brute=json.dumps(corps).encode(),
        reservation_id=None,
        statut="ok",
        statut_http=200,
        jeton=_JETON,
        gabarit_id="transcription-cr",
        version_gabarit=1,
        sha256_gabarit="0" * 64,
        amorce_ids=["amorce-anterieure"],
    )


def _corps(message: dict[str, Any], fin: str = "stop") -> dict[str, Any]:
    return {"choices": [{"index": 0, "finish_reason": fin, "message": message}]}


def test_amorce_derivee_puis_utilisee(monde: Monde) -> None:
    monde.ecrire_seed([amorce("s", "CR", "theme")])
    texte = factice("transcription")
    appel_id = _journaliser_brut(monde, _corps({"role": "assistant", "content": texte}))
    generateur = monde.generateur()
    derivee = generateur.deriver_amorce(
        appel_id, amorce_id="session-cr.transcription", tache="CR", emplacement="transcription"
    )
    assert derivee.auteur_contenu == "mistral" and derivee.appel_id == appel_id
    assert derivee.sha_texte == sha256_hex(texte)
    meme = generateur.deriver_amorce(
        appel_id, amorce_id="session-cr.transcription", tache="CR", emplacement="transcription"
    )
    assert meme == derivee
    generateur.generer("cr", ["session-cr.transcription"], "session-cr", "CR")
    (corps,) = monde.banc.faux.corps()
    assert corps["messages"][0]["content"] == consigne("cr").replace(
        "{transcription}", texte
    ).replace("{plafond_mots_tache}", "400")


@pytest.mark.parametrize("cas", ["outil", "tronquee", "inconnu", "autre-texte", "passages"])
def test_amorce_derivee_refusee(monde: Monde, cas: str) -> None:
    monde.ecrire_seed([amorce("s", "CR", "theme")])
    generateur = monde.generateur()
    message = {"role": "assistant", "content": factice()}
    if cas == "outil":
        message["tool_calls"] = [APPEL_OUTIL]
    appel_id = _journaliser_brut(monde, _corps(message, "length" if cas == "tronquee" else "stop"))
    emplacement = "passages" if cas == "passages" else "transcription"
    if cas == "inconnu":
        appel_id = "f" * 32
    if cas == "autre-texte":
        generateur.deriver_amorce(
            appel_id, amorce_id="session-cr.transcription", tache="CR", emplacement=emplacement
        )
        appel_id = _journaliser_brut(monde, _corps({"role": "assistant", "content": factice()}))
    with pytest.raises(ProvenanceInvalide):
        generateur.deriver_amorce(
            appel_id, amorce_id="session-cr.transcription", tache="CR", emplacement=emplacement
        )
    monde.rien_n_est_parti()


def test_precedents_de_plusieurs_cassettes_par_tour(monde: Monde) -> None:
    _seed_rd(monde)
    second_appel = {**APPEL_OUTIL, "id": "appelfactice02"}
    textes = [factice("resultat"), factice("resultat")]
    resultat_2 = factice("resultat")
    monde.journaliser("session-rd", {"role": "assistant", "tool_calls": [APPEL_OUTIL]})
    monde.journaliser("session-rd", {"role": "assistant", "tool_calls": [second_appel]})
    monde.cassette(
        "session-rd.t1",
        [("outil_factice", {"content": [{"type": "text", "text": t} for t in textes]})],
    )
    monde.cassette(
        "session-rd.t2",
        [("outil_factice", {"content": [{"type": "text", "text": resultat_2}]})],
    )
    precedents = [
        {"role": "assistant", "tool_calls": [APPEL_OUTIL]},
        {"role": "tool", "tool_call_id": "appelfactice01", "content": "\n".join(textes)},
        {"role": "assistant", "tool_calls": [second_appel]},
        {"role": "tool", "tool_call_id": "appelfactice02", "content": resultat_2},
    ]
    monde.generateur().generer("traces-rd", ["d"], "session-rd", "RD", precedents)
    assert len(monde.banc.faux.requetes) == 1


# --- Amorces CT tirées d'un objet JSON et longueurs RE de configuration ---------------------


def contenu_json_ct() -> tuple[str, dict[str, str]]:
    valeurs = {
        "type_courrier": factice("type"),
        "objet": factice("objet"),
        "elements_connus": factice("elements"),
    }
    return json.dumps(valeurs), valeurs


def test_amorces_ct_tirees_des_cles_json_de_la_reponse(monde: Monde) -> None:
    contenu, valeurs = contenu_json_ct()
    appel_id = monde.journaliser("s-ct", {"role": "assistant", "content": contenu})
    monde.ecrire_seed(
        [
            amorce(f"ct.{cle}.1", "CT", cle, auteur="mistral", texte=texte, appel_id=appel_id)
            for cle, texte in valeurs.items()
        ]
    )
    generation = monde.generateur().generer(
        "ct", [f"ct.{cle}.1" for cle in valeurs], "session-ct", "CT"
    )
    consigne_envoyee = generation.messages[0]["content"]
    assert all(texte in consigne_envoyee for texte in valeurs.values())


def test_amorce_ct_absente_de_la_reponse_refusee(monde: Monde) -> None:
    contenu, valeurs = contenu_json_ct()
    appel_id = monde.journaliser("s-ct", {"role": "assistant", "content": contenu})
    valeurs["objet"] = factice("autre-objet")
    monde.ecrire_seed(
        [
            amorce(f"ct.{cle}.1", "CT", cle, auteur="mistral", texte=texte, appel_id=appel_id)
            for cle, texte in valeurs.items()
        ]
    )
    with pytest.raises(ProvenanceInvalide, match="réponse journalisée"):
        monde.generateur().generer("ct", [f"ct.{cle}.1" for cle in valeurs], "s", "CT")
    monde.rien_n_est_parti()


def longueur_re(lie_a: str) -> dict[str, Any]:
    return amorce(
        "re.longueur_demandee.1",
        "RE",
        "longueur_demandee",
        auteur="config",
        texte="moyenne",
        lie_a=lie_a,
    )


def test_longueur_re_de_configuration_admise_avec_son_texte(monde: Monde) -> None:
    monde.ecrire_seed([amorce("re.texte.1", "RE", "texte"), longueur_re("re.texte.1")])
    generation = monde.generateur().generer(
        "re", ["re.longueur_demandee.1", "re.texte.1"], "session-re", "RE"
    )
    assert "moyenne" in generation.messages[0]["content"]


def test_longueur_re_sans_son_texte_dans_l_appel_refusee(monde: Monde) -> None:
    monde.ecrire_seed(
        [
            amorce("re.texte.1", "RE", "texte"),
            amorce("re.texte.2", "RE", "texte"),
            longueur_re("re.texte.1"),
        ]
    )
    with pytest.raises(ProvenanceInvalide, match="liée"):
        monde.generateur().generer("re", ["re.longueur_demandee.1", "re.texte.2"], "s", "RE")
    monde.rien_n_est_parti()


def test_reponse_journalisee_reutilisee_par_session(monde: Monde) -> None:
    monde.ecrire_seed([amorce("ct.sujet.1", "CT", "sujet")])
    generateur = monde.generateur()
    assert generateur.reponse_journalisee("amorces-ct", ["ct.sujet.1"], "seed-ct-1", "CT") is None
    generation = generateur.generer("amorces-ct", ["ct.sujet.1"], "seed-ct-1", "CT")
    ligne = generateur.reponse_journalisee("amorces-ct", ["ct.sujet.1"], "seed-ct-1", "CT")
    assert ligne is not None and ligne.appel_id == generation.appel_id
    # Autre session, autres amorces ou autre gabarit : aucune réutilisation.
    assert generateur.reponse_journalisee("amorces-ct", ["ct.sujet.1"], "autre", "CT") is None
    assert generateur.reponse_journalisee("amorces-ct", ["ct.sujet.2"], "seed-ct-1", "CT") is None
    assert generateur.reponse_journalisee("ct", ["ct.sujet.1"], "seed-ct-1", "CT") is None


def test_fabrique_courriers_relance_sans_second_appel(monde: Monde) -> None:
    """Fabrique du CLI sur le vrai Générateur : un nouveau run `seed` réutilise la réponse
    journalisée de la même session (aucune seconde requête, aucune seconde réservation)."""
    from slmsp.cli.data import _fabrique_courriers_depuis

    for run_id in (SEED, SEED_2):
        monde.ecrire_seed([amorce("ct.sujet.1", "CT", "sujet")], run_id=run_id)
    fabrique = _fabrique_courriers_depuis(lambda run_id: monde.generateur(run_id))
    premier = fabrique(SEED, "ct.sujet.1", "seed-ct-1")
    assert len(monde.banc.faux.requetes) == 1
    assert fabrique(SEED_2, "ct.sujet.1", "seed-ct-1") == premier
    assert len(monde.banc.faux.requetes) == 1


# --- Plafond de mots par Tâche (story 9.10) -------------------------------------------------


@pytest.mark.parametrize(
    ("gabarit_id", "tache", "plafond"),
    [("traces-q", "Q", 160), ("traces-rd", "RD", 120), ("cr", "CR", 400), ("lc", "LC", 150)],
)
def test_plafond_mots_tache_resolu_par_tache(
    monde: Monde, gabarit_id: str, tache: str, plafond: int
) -> None:
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    generateur = monde.generateur(rendre_passages=lambda _s: "<passages-factices>")
    assert generateur.plafonds_mots[tache] == plafond
    assert "plafond_mots_tache" in generateur.gabarit(gabarit_id, tache).emplacements
    attendu = 1600 if tache == "CR" else 800
    assert generateur.max_tokens(gabarit_id, tache) == attendu


def test_plafond_mots_tache_manquant_refuse_au_pre_vol(monde: Monde) -> None:
    fichier = monde.racine / "config" / "donnees.toml"
    fichier.write_text(DONNEES.replace("generique = 200\n", ""), encoding="utf-8")
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    generateur = monde.generateur()
    with pytest.raises(GabaritInvalide, match="plafond_mots_tache"):
        generateur.gabarit("generique", "generique")
    with pytest.raises(GabaritInvalide, match="plafond_mots_tache"):
        generateur.generer("generique", ["d"], "s", "generique")
    assert monde.banc.faux.corps() == []
    # Un gabarit sans l'emplacement n'en dépend pas (RE garde plafond_mots).
    assert "plafond_mots_tache" not in generateur.gabarit("re", "RE").emplacements
    assert "plafond_mots" in generateur.gabarit("re", "RE").emplacements


@pytest.mark.parametrize(
    "table",
    ["CO = 100\n", "Q = 0\n", "Q = -5\n", 'Q = "160"\n', "inconnue = 10\n"],
)
def test_plafonds_mots_invalides(monde: Monde, table: str) -> None:
    fichier = monde.racine / "config" / "donnees.toml"
    fichier.write_text(
        DONNEES.split("[generateur.plafonds_mots]")[0] + "[generateur.plafonds_mots]\n" + table,
        encoding="utf-8",
    )
    monde.ecrire_seed([amorce("d", "generique", "demande")])
    if table.startswith("CO"):
        # CO est une Tâche générable : accepté par le Générateur, refusé par data.config.
        assert monde.generateur().plafonds_mots == {"CO": 100}
        return
    with pytest.raises(ConfigurationInvalide, match="plafonds_mots"):
        monde.generateur()


def test_amorce_sur_plafond_mots_tache_refusee(monde: Monde) -> None:
    monde.ecrire_seed(
        [amorce("d", "generique", "demande"), amorce("p", "generique", "plafond_mots_tache")]
    )
    with pytest.raises(ProvenanceInvalide, match="plafond_mots_tache"):
        monde.generateur().generer("generique", ["d", "p"], "s", "generique")
