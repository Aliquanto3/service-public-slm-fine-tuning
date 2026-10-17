"""Étape `seed` (story 9.3, FR-29, AD-3 verrou 5) : amorces publiques ou Mistral, anti-fuite.

Les jeux sont factices et écrits dans `tmp_path` : chaque « fichier parquet » est un fichier de
lignes JSON que le décodeur injecté relit (le vrai décodeur pyarrow est testé dans
`tests/cli/test_data.py`). Tous les textes sont des chaînes manifestement artificielles
(`<question-factice-1>`, `<scenario-factice-1>`) produites par le code de test (D1.1).
Aucun appel d'API : la fabrique de scénarios est une doublure.
"""

from __future__ import annotations

import json
import secrets
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import pytest

from slmsp.core.artefacts import ouvrir_run
from slmsp.core.canonique import json_canonique, sha256_hex
from slmsp.core.config import racine_projet
from slmsp.core.erreurs import (
    BudgetEpuise,
    ConfigurationInvalide,
    ProvenanceInvalide,
    ReponseTronquee,
    SourceSansLicence,
)
from slmsp.core.items import empreintes_antifuite, textes_entree, textes_reference
from slmsp.core.items import lire_jeu as lire_jeu_evaluation
from slmsp.core.schemas.amorce import Amorce
from slmsp.core.texte import normaliser
from slmsp.data import seed as seed_module
from slmsp.data.config import ConfigDonnees, SeedDonnees, charger_config_donnees
from slmsp.data.licences import RegistreLicences, UsageInterdit
from slmsp.data.seed import (
    COLONNES_IDENTIFIANTS,
    MOTIFS_EXCLUSION,
    REGLES,
    SANS_SOURCE_PUBLIQUE,
    FichierJeu,
    JeuPublic,
    Protection,
    RegleAmorce,
    construire_protection,
    executer_seed,
    verifier_amorces,
    versions_protegees,
)

REV_SP = "a" * 40
REV_PIAF = "b" * 40

REGLES_TEST = (
    RegleAmorce("service-public", "related_questions", "Q", "question", 5, 100, "question"),
    RegleAmorce("service-public", "title", "CR", "theme", 5, 100),
    RegleAmorce("service-public", "text", "LC", "texte", 5, 100),
    RegleAmorce("piaf", "question", "generique", "demande", 5, 100),
)

TOML_REGISTRE = """schema_version = 1

[[sources]]
id = "Org/service-public"
licence = "licence-factice"
usage = "diffusable"
auteur_contenu = "public"
genere_par = "humain"

[[sources]]
id = "Org/piaf"
licence = "licence-factice"
usage = "recherche"
auteur_contenu = "public"
genere_par = "humain"

[[sources]]
id = "Org/eval-seulement"
licence = "licence-factice"
usage = "evaluation_seulement"
auteur_contenu = "public"
genere_par = "humain"

[[sources]]
id = "mistral/reponses-generateur"
licence = "licence-factice"
usage = "diffusable"
auteur_contenu = "mistral"
genere_par = "mistral"
"""


# --- Doublures et fixtures ----------------------------------------------------------------


def decodeur_json(octets: bytes, colonnes: Sequence[str]) -> Iterable[Mapping[str, Any]]:
    """Décodeur factice : une ligne JSON par ligne ; seules les colonnes demandées existent
    (une colonne inconnue lève `KeyError`, comme pyarrow)."""
    for ligne in octets.decode("utf-8").splitlines():
        valeurs = json.loads(ligne)
        yield {colonne: valeurs[colonne] for colonne in colonnes}


def config_petite(**volumes: int) -> ConfigDonnees:
    """Config réelle, volumes réduits (2 par Tâche) ; `generique` reste dans [10 %, 20 %]."""
    donnees = charger_config_donnees().model_dump()
    metier = {"Q": 2, "RD": 2, "CR": 2, "LC": 2, "CO": 2, "RE": 2, "CT": 2} | volumes
    metier.pop("generique", None)
    generique = volumes.get("generique", max(2, round(sum(metier.values()) * 0.15 / 0.85)))
    donnees["volumes"] = metier | {"generique": generique}
    return ConfigDonnees.model_validate(donnees)


def ligne_sp(i: int, **champs: Any) -> dict[str, Any]:
    """Ligne factice du jeu `service-public` (toutes les colonnes lues)."""
    questions = [
        {
            "sid": f"s{i}-{k}",
            "url": f"https://exemple.invalide/{i}/{k}",
            "question": f"<question-factice-{i}-{k}>",
        }
        for k in range(2)
    ]
    valeurs = {
        "title": f"<theme-factice-{i}>",
        "text": f"<texte-factice-{i}>",
        "related_questions": json.dumps(questions),
        "url": f"https://exemple.invalide/fiche-{i}",
        "doc_id": f"doc-factice-{i}",
        "chunk_id": f"chunk-factice-{i}",
    }
    return valeurs | champs


def ligne_piaf(i: int) -> dict[str, Any]:
    return {"question": f"<demande-factice-{i}>"}


class Monde:
    """Racine temporaire : jeux, registre, protection et exécution de `seed`."""

    def __init__(self, racine: Path) -> None:
        self.racine = racine
        (racine / "data").mkdir(parents=True, exist_ok=True)
        (racine / "data" / "registre-licences.toml").write_text(TOML_REGISTRE, encoding="utf-8")
        self.registre = RegistreLicences.charger(racine=racine)

    def jeu(
        self,
        nom: str,
        depot: str,
        revision: str,
        fichiers: Sequence[Sequence[Mapping[str, Any]]],
    ) -> JeuPublic:
        dossier = self.racine / "data" / "raw" / "mediatech" / nom / revision
        dossier.mkdir(parents=True, exist_ok=True)
        resultat = []
        for numero, lignes in enumerate(fichiers):
            contenu = "\n".join(json.dumps(ligne) for ligne in lignes).encode("utf-8")
            chemin = dossier / f"part_{numero}.bin"
            chemin.write_bytes(contenu)
            resultat.append(FichierJeu(chemin, sha256_hex(contenu)))
        return JeuPublic(nom, depot, revision, tuple(resultat))

    def jeux_standard(self, nb_sp: int = 4, nb_piaf: int = 3) -> list[JeuPublic]:
        moitie = nb_sp // 2
        return [
            self.jeu(
                "service-public",
                "Org/service-public",
                REV_SP,
                [
                    [ligne_sp(i) for i in range(moitie)],
                    [ligne_sp(i) for i in range(moitie, nb_sp)],
                ],
            ),
            self.jeu("piaf", "Org/piaf", REV_PIAF, [[ligne_piaf(i) for i in range(nb_piaf)]]),
        ]

    def executer(self, jeux: Sequence[JeuPublic] | None = None, **options: Any):
        valeurs: dict[str, Any] = {
            "racine": self.racine,
            "jeux": jeux if jeux is not None else self.jeux_standard(),
            "registre": self.registre,
            "config": config_petite(),
            "protection": Protection.vide(),
            "decodeur": decodeur_json,
            "regles": REGLES_TEST,
            "facteur": 1,
        }
        return executer_seed(**(valeurs | options))

    def amorces(self, run_id: str) -> list[dict[str, Any]]:
        chemin = self.racine / "runs" / "data-seed" / run_id / "amorces.jsonl"
        return [json.loads(ligne) for ligne in chemin.read_text("utf-8").splitlines() if ligne]

    def comptes(self, run_id: str) -> dict[str, Any]:
        chemin = self.racine / "runs" / "data-seed" / run_id / "comptes.json"
        return json.loads(chemin.read_text("utf-8"))

    def statut(self, run_id: str) -> str:
        return ouvrir_run(run_id, racine=self.racine).statut_courant()

    def ecrire_amorces(self, lignes: Iterable[Mapping[str, Any]], run_id: str) -> None:
        dossier = self.racine / "runs" / "data-seed" / run_id
        dossier.mkdir(parents=True, exist_ok=True)
        contenu = b"".join(json_canonique(dict(ligne)) + b"\n" for ligne in lignes)
        (dossier / "amorces.jsonl").write_bytes(contenu)


@pytest.fixture
def monde(tmp_path: Path) -> Monde:
    return Monde(tmp_path)


def protection_de(
    textes: Mapping[str, str] | None = None,
    *,
    amorces: Iterable[str] = (),
    urls: Iterable[str] = (),
    dataset_ids: Iterable[str] = (),
    resource_ids: Iterable[str] = (),
    n: int = 5,
    seuil: float = 0.5,
) -> Protection:
    """Protection fabriquée à la main : `textes` = textes d'items `<version>/<id>` factices."""
    par_item = {
        cle: frozenset(seed_module._empreintes_texte(texte, n))
        for cle, texte in (textes or {}).items()
    }
    index: dict[str, list[str]] = {}
    for cle, empreintes in par_item.items():
        for empreinte in empreintes:
            index.setdefault(empreinte, []).append(cle)
    return Protection(
        versions=("v1.0",),
        n_ngrammes=n,
        seuil=seuil,
        amorces_sha256=frozenset(sha256_hex(normaliser(a)) for a in amorces),
        urls=frozenset(urls),
        dataset_ids=frozenset(dataset_ids),
        resource_ids=frozenset(resource_ids),
        par_item=par_item,
        index={e: tuple(c) for e, c in index.items()},
    )


def phrase(prefixe: str, nombre: int) -> str:
    """`nombre` jetons artificiels distincts (`m0 m1 ...`) : n-grammes contrôlables."""
    return " ".join(f"{prefixe}{i}" for i in range(nombre))


# --- Nominal ------------------------------------------------------------------------------


def test_nominal_public(monde: Monde) -> None:
    jeux = monde.jeux_standard()
    resultat = monde.executer(jeux)
    assert resultat.statut == "complet"
    assert monde.statut(resultat.run_id) == "complet"
    assert resultat.dossier == monde.racine / "runs" / "data-seed" / resultat.run_id
    assert {p.name for p in resultat.dossier.iterdir()} >= {"amorces.jsonl", "comptes.json"}

    amorces = monde.amorces(resultat.run_id)
    # facteur 1 x volume 2 : deux amorces par groupe (Q/question, CR/theme, LC/texte, generique).
    par_groupe: dict[tuple[str, str], list[dict]] = {}
    for amorce in amorces:
        par_groupe.setdefault((amorce["tache"], amorce["emplacement"]), []).append(amorce)
    assert {cle: len(valeur) for cle, valeur in par_groupe.items()} == {
        ("Q", "question"): 2,
        ("CR", "theme"): 2,
        ("LC", "texte"): 2,
        ("generique", "demande"): 2,
    }
    depots = {jeu.nom: jeu.depot for jeu in jeux}
    for amorce in amorces:
        Amorce.model_validate(amorce)
        assert amorce["auteur_contenu"] == "public"
        assert amorce["sha_texte"] == sha256_hex(amorce["texte"])
        nom = "piaf" if amorce["tache"] == "generique" else "service-public"
        assert amorce["jeu"] == depots[nom]
        assert amorce["revision"] == (REV_PIAF if nom == "piaf" else REV_SP)
        assert amorce["amorce_id"].startswith(
            f"{amorce['tache'].lower()}.{amorce['emplacement']}.{nom}."
        )
        assert "appel_id" not in amorce
    assert len({a["amorce_id"] for a in amorces}) == len(amorces)

    # Chaque amorce publique est relue sur disque, dans le jeu.
    relues = verifier_amorces(
        monde.racine, resultat.run_id, jeux, decodeur_json, regles=REGLES_TEST
    )
    assert [a.amorce_id for a in relues] == [a["amorce_id"] for a in amorces]


def test_comptes_et_manifeste(monde: Monde) -> None:
    resultat = monde.executer(config=config_petite(Q=3, LC=5))
    comptes = monde.comptes(resultat.run_id)
    assert comptes == json.loads(json.dumps(resultat.comptes))
    assert comptes["statut"] == "complet"
    assert comptes["facteur"] == 1
    assert comptes["protection"]["nb_items"] == 0
    q = comptes["taches"]["Q"]["question"]
    assert q["cible"] == 3
    assert q["conservees"] == 3
    assert q["manque"] == 0
    assert q["candidats"] == 8  # 4 fiches x 2 questions
    assert set(q["exclusions"]) == set(MOTIFS_EXCLUSION)
    lc = comptes["taches"]["LC"]["texte"]
    assert (lc["cible"], lc["conservees"], lc["manque"], lc["candidats"]) == (5, 4, 1, 4)
    assert comptes["scenarios"]["demandes"] == 0
    assert comptes["sans_source_publique"] == [
        {"tache": t, "emplacement": e} for t, e in SANS_SOURCE_PUBLIQUE
    ]
    manifeste = ouvrir_run(resultat.run_id, racine=monde.racine).manifeste
    assert manifeste.type == "data-seed"
    assert manifeste.config["facteur"] == 1
    assert "registre-licences" in manifeste.entrees
    assert set(manifeste.entrees) >= {"service-public-0", "service-public-1", "piaf-0"}
    assert manifeste.config["registre_sha256"] == monde.registre.sha256


def test_numero_de_ligne_traverse_les_fichiers(monde: Monde) -> None:
    resultat = monde.executer(config=config_petite(LC=10))
    lignes = {a["ligne"] for a in monde.amorces(resultat.run_id) if a["tache"] == "LC"}
    assert lignes == {0, 1, 2, 3}  # 2 fichiers de 2 lignes : numérotation continue


def test_sous_cle_ids_et_json_ou_liste(monde: Monde) -> None:
    liste = [{"url": "https://exemple.invalide/u", "question": "<question-factice-liste>"}]
    jeu = monde.jeu(
        "service-public",
        "Org/service-public",
        REV_SP,
        [
            [
                ligne_sp(0, related_questions=liste),  # liste déjà décodée
                ligne_sp(1, related_questions="pas du json"),  # JSON invalide : ignoré
                ligne_sp(2, related_questions=json.dumps({"question": "x"})),  # pas une liste
                ligne_sp(3, related_questions=json.dumps([{"question": 3}, "texte", {"url": "u"}])),
            ]
        ],
    )
    resultat = monde.executer(
        [jeu],
        regles=(REGLES_TEST[0],),
        config=config_petite(Q=10),
    )
    amorces = monde.amorces(resultat.run_id)
    assert [a["texte"] for a in amorces] == ["<question-factice-liste>"]
    assert amorces[0]["amorce_id"] == "q.question.service-public.0.0"
    assert amorces[0]["ligne"] == 0


def test_bornes_de_longueur_et_deduplication(monde: Monde) -> None:
    lignes = [
        ligne_sp(0, title="<c>"),  # trop court
        ligne_sp(1, title="<theme-factice-commun>"),
        ligne_sp(2, title="  <THEME-factice-commun> !! "),  # même texte normalisé : doublon
        ligne_sp(3, title="<t>" + "x" * 200),  # trop long
        ligne_sp(4, title=None),
        ligne_sp(5, title="   "),
        ligne_sp(6, title="<theme-factice-autre>"),
    ]
    jeu = monde.jeu("service-public", "Org/service-public", REV_SP, [lignes])
    regle = RegleAmorce("service-public", "title", "CR", "theme", 5, 100)
    resultat = monde.executer([jeu], regles=(regle,), config=config_petite(CR=10))
    comptes = monde.comptes(resultat.run_id)["taches"]["CR"]["theme"]
    assert comptes["candidats"] == 2
    textes = {a["texte"] for a in monde.amorces(resultat.run_id)}
    assert textes == {"<theme-factice-commun>", "<theme-factice-autre>"}


def test_selection_deterministe_triee_par_sha(monde: Monde) -> None:
    jeux = monde.jeux_standard(nb_sp=6)
    config = config_petite(LC=3)
    premier = monde.executer(jeux, config=config)
    second = monde.executer(jeux, config=config)
    textes = [a["texte"] for a in monde.amorces(premier.run_id) if a["tache"] == "LC"]
    assert textes == [a["texte"] for a in monde.amorces(second.run_id) if a["tache"] == "LC"]
    toutes = [f"<texte-factice-{i}>" for i in range(6)]
    attendu = sorted(toutes, key=lambda t: sha256_hex(f"LC.texte\0{normaliser(t)}"))[:3]
    assert textes == attendu


def test_facteur_multiplie_la_cible(monde: Monde) -> None:
    jeux = monde.jeux_standard(nb_sp=8)
    resultat = monde.executer(jeux, facteur=3, config=config_petite(LC=2))
    assert monde.comptes(resultat.run_id)["taches"]["LC"]["texte"]["cible"] == 6
    assert monde.comptes(resultat.run_id)["taches"]["LC"]["texte"]["conservees"] == 6
    with pytest.raises(ValueError, match="facteur"):
        monde.executer(jeux, facteur=0)


# --- Licences et jeux ---------------------------------------------------------------------


def test_source_evaluation_seulement_refusee(monde: Monde) -> None:
    jeu = monde.jeu("service-public", "Org/eval-seulement", REV_SP, [[ligne_sp(0)]])
    with pytest.raises(UsageInterdit):
        monde.executer([jeu], regles=(REGLES_TEST[1],))
    assert not (monde.racine / "runs").exists()


def test_source_hors_registre_refusee(monde: Monde) -> None:
    jeu = monde.jeu("service-public", "Org/inconnue", REV_SP, [[ligne_sp(0)]])
    with pytest.raises(SourceSansLicence):
        monde.executer([jeu], regles=(REGLES_TEST[1],))
    assert not (monde.racine / "runs").exists()


def test_jeu_non_telecharge(monde: Monde) -> None:
    jeux = monde.jeux_standard()
    jeux[0].fichiers[1].chemin.unlink()
    with pytest.raises(ConfigurationInvalide, match="non téléchargé"):
        monde.executer(jeux)
    assert not (monde.racine / "runs").exists()


def test_sha_different_run_partiel(monde: Monde) -> None:
    jeux = monde.jeux_standard()
    jeux[0].fichiers[0].chemin.write_bytes(b'{"title": "<contenu-modifie>"}\n')
    with pytest.raises(ProvenanceInvalide, match="SHA-256"):
        monde.executer(jeux)
    [dossier] = list((monde.racine / "runs" / "data-seed").iterdir())
    assert monde.statut(dossier.name) == "partiel-erreur"
    assert not (dossier / "amorces.jsonl").exists()


def test_regle_sur_jeu_inconnu(monde: Monde) -> None:
    with pytest.raises(ConfigurationInvalide, match="absent"):
        monde.executer([monde.jeux_standard()[0]], regles=REGLES_TEST)
    with pytest.raises(ConfigurationInvalide, match="sans volume"):
        monde.executer(
            regles=(RegleAmorce("piaf", "question", "TR", "demande", 5, 10),),
        )


def test_lecture_hors_data_raw_refusee(monde: Monde, tmp_path: Path) -> None:
    contenu = json.dumps(ligne_piaf(0)).encode()
    dehors = tmp_path / "hors-liste.bin"
    dehors.write_bytes(contenu)
    jeu = JeuPublic("piaf", "Org/piaf", REV_PIAF, (FichierJeu(dehors, sha256_hex(contenu)),))
    from slmsp.core.erreurs import LectureInterdite

    with pytest.raises(LectureInterdite):
        monde.executer([jeu], regles=(REGLES_TEST[3],))


def test_aucun_parametre_ne_designe_un_fichier_d_amorces() -> None:
    import inspect

    parametres = set(inspect.signature(executer_seed).parameters)
    assert not {p for p in parametres if "amorce" in p or "fichier" in p or "chemin" in p}


# --- Anti-fuite ---------------------------------------------------------------------------


def test_fuite_par_texte_amorce_usager(monde: Monde) -> None:
    protection = protection_de(amorces=["<Question-factice-0-0>"])
    resultat = monde.executer(
        protection=protection, regles=(REGLES_TEST[0],), config=config_petite(Q=100)
    )
    comptes = monde.comptes(resultat.run_id)["taches"]["Q"]["question"]
    assert comptes["exclus"] == 1
    assert comptes["exclusions"]["amorce_usager"] == 1
    textes = {a["texte"] for a in monde.amorces(resultat.run_id)}
    assert "<question-factice-0-0>" not in textes
    assert len(textes) == 7


def test_fuite_par_identifiants(monde: Monde) -> None:
    protection = protection_de(
        urls=["https://exemple.invalide/fiche-1", "https://exemple.invalide/2/1"],
        dataset_ids=["doc-factice-2"],
        resource_ids=["chunk-factice-3"],
    )
    resultat = monde.executer(
        protection=protection,
        regles=(REGLES_TEST[1], REGLES_TEST[0]),
        config=config_petite(CR=100, Q=100),
    )
    comptes = monde.comptes(resultat.run_id)["taches"]
    # CR/theme : fiche 1 (url), fiche 2 (doc_id -> dataset_id), fiche 3 (chunk_id -> resource_id).
    theme = comptes["CR"]["theme"]
    assert theme["exclusions"] == {
        "amorce_usager": 0,
        "provenance_url": 1,
        "dataset_id": 1,
        "resource_id": 1,
        "recouvrement_ngrammes": 0,
    }
    assert theme["exclus"] == 3
    assert {a["texte"] for a in monde.amorces(resultat.run_id) if a["tache"] == "CR"} == {
        "<theme-factice-0>"
    }
    # Q/question : l'URL de l'élément (2/1) et celle de la fiche (fiche-1) comptent ;
    # doc_id 2 et chunk_id 3 excluent leurs deux questions.
    q = comptes["Q"]["question"]
    assert q["exclusions"]["provenance_url"] == 3  # 1/0, 1/1 (fiche-1) et 2/1
    assert q["exclusions"]["dataset_id"] == 2
    assert q["exclusions"]["resource_id"] == 2
    assert q["exclus"] == 6  # fiches 1, 2 et 3 : toutes leurs questions
    assert q["conservees"] == 2  # fiche 0


def test_fuite_par_ngrammes(monde: Monde) -> None:
    item = phrase("m", 10)  # 6 n-grammes de 5 mots
    protection = protection_de({"v1.0/Q-001": item})
    lignes = [
        ligne_sp(0, title=phrase("m", 7)),  # 3 n-grammes, tous dans l'item : inclusion 1.0
        ligne_sp(1, title="m0 m1 m2 m3 m4 q1 q2 q3 q4 q5 q6 q7"),  # 1 / min(8, 6) < seuil
        ligne_sp(2, title=phrase("m", 5) + " q1 q2 q3 q4 q5"),  # 1 / min(6, 6) : 0.17
        ligne_sp(3, title=phrase("z", 8)),  # aucun recouvrement
        ligne_sp(4, title="m0 m1 m2 m3 m4 m5 q1 q2"),  # 2 / min(4, 6) = 0.5 : au seuil
    ]
    jeu = monde.jeu("service-public", "Org/service-public", REV_SP, [lignes])
    regle = RegleAmorce("service-public", "title", "CR", "theme", 5, 200)
    resultat = monde.executer(
        [jeu], protection=protection, regles=(regle,), config=config_petite(CR=100)
    )
    comptes = monde.comptes(resultat.run_id)["taches"]["CR"]["theme"]
    assert comptes["exclusions"]["recouvrement_ngrammes"] == 2
    assert comptes["exclus"] == 2
    assert {a["ligne"] for a in monde.amorces(resultat.run_id)} == {1, 2, 3}


def test_recouvrement_texte_court_sous_n_mots() -> None:
    protection = protection_de({"v1.0/Q-001": "m0 m1 m2"})  # moins de 5 mots : tuple entier
    assert protection.recouvrement("M0, m1 m2") == 1.0
    assert protection.recouvrement("m0 m1") == 0.0
    assert protection.recouvrement("") == 0.0
    assert protection.motifs("m0 m1 m2") == ["recouvrement_ngrammes"]
    assert protection.motifs("autre texte factice") == []


def test_motifs_sont_independants_et_ordonnes() -> None:
    protection = protection_de(
        {"v1.0/Q-001": phrase("m", 8)},
        amorces=[phrase("m", 8)],
        urls=["https://exemple.invalide/x"],
        dataset_ids=["id-1"],
        resource_ids=["id-1"],
    )
    motifs = protection.motifs(phrase("m", 8), urls=["https://exemple.invalide/x"], ids=["id-1"])
    assert motifs == list(MOTIFS_EXCLUSION)
    assert protection.motifs("neutre factice", urls=["https://exemple.invalide/y"], ids=["z"]) == []


def test_url_comparee_sans_barre_finale_fragment_ni_casse() -> None:
    protection = protection_de({"v1.0/Q-001": phrase("m", 8)}, urls=["https://exemple.invalide/x"])
    for variante in ("https://exemple.invalide/x/", "HTTPS://Exemple.invalide/x#ancre"):
        assert protection.motifs("neutre factice", urls=[variante]) == ["provenance_url"]


def test_construire_protection_sur_les_vrais_jeux() -> None:
    config = charger_config_donnees()
    racine = racine_projet()
    protection = construire_protection(("v1.0", "v1.1"), config, racine)
    cles = list(protection.par_item)
    assert any(c.startswith("v1.0/") for c in cles)
    assert any(c.startswith("v1.1/") for c in cles)
    assert protection.n_ngrammes == config.anti_fuite.n_ngrammes
    assert protection.seuil == config.anti_fuite.seuil_jaccard
    assert protection.urls
    assert protection.amorces_sha256
    assert protection.index
    # Mêmes empreintes que l'API de core.items pour un item : texte d'entrée et références.
    jeu = lire_jeu_evaluation("v1.1", racine)
    reference = empreintes_antifuite("v1.1", config.anti_fuite.n_ngrammes, racine=racine)
    item = jeu.items[0]
    attendu = reference.par_item[jeu.cle(item)]
    obtenu = {
        empreinte
        for texte in textes_entree(item) + textes_reference(item)
        for empreinte in seed_module._empreintes_texte(texte, config.anti_fuite.n_ngrammes)
    }
    assert frozenset(obtenu) == attendu
    assert protection.par_item[jeu.cle(item)] == attendu
    # Un item du jeu gelé est reconnu comme fuite par ses propres n-grammes.
    texte_item = textes_entree(item)[0]
    assert (
        "recouvrement_ngrammes" in protection.motifs(texte_item)
        or len(normaliser(texte_item).split()) < config.anti_fuite.n_ngrammes
    )


def test_versions_protegees(tmp_path: Path) -> None:
    assert versions_protegees(racine_projet()) == ("v1.0", "v1.1", "calibrage")
    assert versions_protegees(tmp_path) == ("v1.0", "v1.1")
    with pytest.raises(ConfigurationInvalide, match="v1.0"):
        construire_protection(("v1.0", "v1.1"), charger_config_donnees(), tmp_path)


# --- Scénarios Mistral --------------------------------------------------------------------


class FabriqueFactice:
    def __init__(self, monde: Monde, *, budget: int | None = None) -> None:
        self.monde = monde
        self.budget = budget
        self.appels: list[tuple[str, str, str]] = []
        self.textes: list[str] = []
        self.ids: list[str] = []

    def __call__(self, seed_run_id: str, theme_id: str, session_id: str) -> tuple[str, str]:
        deja = {a["amorce_id"] for a in self.monde.amorces(seed_run_id)}
        assert theme_id in deja  # le thème est écrit avant l'appel
        if self.budget is not None and len(self.appels) >= self.budget:
            raise BudgetEpuise("plafond factice")
        self.appels.append((seed_run_id, theme_id, session_id))
        self.textes.append(f"<scenario-factice-{len(self.appels)}>")
        self.ids.append(secrets.token_hex(16))
        return self.ids[-1], self.textes[-1]


def test_scenarios_mistral(monde: Monde) -> None:
    fabrique = FabriqueFactice(monde)
    resultat = monde.executer(
        nb_scenarios=2, fabrique_scenarios=fabrique, config=config_petite(CR=5)
    )
    assert resultat.statut == "complet"
    amorces = monde.amorces(resultat.run_id)
    themes = [a for a in amorces if a["emplacement"] == "theme"]
    scenarios = [a for a in amorces if a["emplacement"] == "scenario"]
    assert [a["texte"] for a in scenarios] == fabrique.textes
    assert [a["appel_id"] for a in scenarios] == fabrique.ids
    for scenario, theme in zip(scenarios, themes, strict=False):
        Amorce.model_validate(scenario)
        assert scenario["tache"] == "CR"
        assert scenario["auteur_contenu"] == "mistral"
        assert scenario["sha_texte"] == sha256_hex(scenario["texte"])
        suffixe = theme["amorce_id"].removeprefix("cr.theme.")
        assert scenario["amorce_id"] == f"cr.scenario.{suffixe}"
        assert "jeu" not in scenario and "ligne" not in scenario
    assert [appel[1] for appel in fabrique.appels] == [t["amorce_id"] for t in themes[:2]]
    assert len({appel[2] for appel in fabrique.appels}) == 2
    assert all(appel[0] == resultat.run_id for appel in fabrique.appels)
    assert monde.comptes(resultat.run_id)["scenarios"]["produits"] == 2
    # La vérification relit les amorces publiques et accepte les amorces Mistral à appel_id.
    relues = verifier_amorces(
        monde.racine, resultat.run_id, monde.jeux_standard(), decodeur_json, regles=REGLES_TEST
    )
    assert len(relues) == len(amorces)


def test_scenarios_limites_par_les_themes(monde: Monde) -> None:
    fabrique = FabriqueFactice(monde)
    resultat = monde.executer(
        monde.jeux_standard(nb_sp=2),
        nb_scenarios=5,
        fabrique_scenarios=fabrique,
        config=config_petite(CR=2),
    )
    scenarios = monde.comptes(resultat.run_id)["scenarios"]
    assert (scenarios["demandes"], scenarios["themes_disponibles"], scenarios["produits"]) == (
        5,
        2,
        2,
    )


def test_scenarios_budget_epuise_run_partiel(monde: Monde) -> None:
    fabrique = FabriqueFactice(monde, budget=1)
    resultat = monde.executer(
        nb_scenarios=3, fabrique_scenarios=fabrique, config=config_petite(CR=5)
    )
    assert resultat.statut == "partiel-budget"
    assert monde.statut(resultat.run_id) == "partiel-budget"
    amorces = monde.amorces(resultat.run_id)
    assert sum(a["emplacement"] == "scenario" for a in amorces) == 1
    assert sum(a["emplacement"] == "theme" for a in amorces) == 4  # amorces publiques conservées
    comptes = monde.comptes(resultat.run_id)
    assert comptes["statut"] == "partiel-budget"
    assert comptes["scenarios"]["produits"] == 1
    assert "budget_epuise" not in comptes["scenarios"]


def test_scenario_qui_recoupe_le_jeu_d_evaluation_est_exclu(monde: Monde) -> None:
    fabrique = FabriqueFactice(monde)
    protection = protection_de(amorces=["<scenario-factice-1>"])
    resultat = monde.executer(
        protection=protection,
        nb_scenarios=2,
        fabrique_scenarios=fabrique,
        config=config_petite(CR=5),
    )
    scenarios = monde.comptes(resultat.run_id)["scenarios"]
    assert (scenarios["produits"], scenarios["exclus"]) == (1, 1)
    assert scenarios["exclusions"]["amorce_usager"] == 1


def test_sans_scenario_aucun_appel(monde: Monde) -> None:
    fabrique = FabriqueFactice(monde)
    resultat = monde.executer(nb_scenarios=0, fabrique_scenarios=fabrique)
    assert fabrique.appels == []
    assert not any(a["emplacement"] == "scenario" for a in monde.amorces(resultat.run_id))
    with pytest.raises(ValueError, match="fabrique"):
        monde.executer(nb_scenarios=1)


def test_scenarios_exigent_la_source_mistral_au_registre(tmp_path: Path) -> None:
    monde = Monde(tmp_path)
    texte = TOML_REGISTRE.split('[[sources]]\nid = "mistral')[0]
    (tmp_path / "data" / "registre-licences.toml").write_text(texte, encoding="utf-8")
    monde.registre = RegistreLicences.charger(racine=tmp_path)
    with pytest.raises(SourceSansLicence, match="mistral"):
        monde.executer(nb_scenarios=1, fabrique_scenarios=FabriqueFactice(monde))
    assert not (tmp_path / "runs").exists()


def test_fabrique_non_conforme(monde: Monde) -> None:
    def fabrique(_seed: str, _theme: str, _session: str) -> tuple[str, str]:
        return "pas-un-appel-id", "<scenario-factice-1>"

    with pytest.raises(ProvenanceInvalide, match="non conforme"):
        monde.executer(nb_scenarios=1, fabrique_scenarios=fabrique)
    [dossier] = list((monde.racine / "runs" / "data-seed").iterdir())
    assert monde.statut(dossier.name) == "partiel-erreur"


# --- verifier_amorces ---------------------------------------------------------------------

RUN_FACTICE = "20261013-000000-seed-0a1b"


def amorce_publique(monde: Monde, **champs: Any) -> dict[str, Any]:
    texte = champs.pop("texte", "<theme-factice-1>")
    valeurs = {
        "schema_version": 1,
        "amorce_id": "cr.theme.service-public.1",
        "tache": "CR",
        "emplacement": "theme",
        "texte": texte,
        "sha_texte": sha256_hex(texte),
        "auteur_contenu": "public",
        "jeu": "Org/service-public",
        "revision": REV_SP,
        "ligne": 1,
    }
    return valeurs | champs


def verifier(monde: Monde, lignes: list[dict[str, Any]], jeux: Sequence[JeuPublic] | None = None):
    monde.ecrire_amorces(lignes, RUN_FACTICE)
    return verifier_amorces(
        monde.racine,
        RUN_FACTICE,
        jeux if jeux is not None else monde.jeux_standard(),
        decodeur_json,
        regles=REGLES_TEST,
    )


def test_verifier_accepte_une_amorce_relue(monde: Monde) -> None:
    [amorce] = verifier(monde, [amorce_publique(monde)])
    assert amorce.ligne == 1


def test_verifier_refuse_une_amorce_ecrite_a_la_main(monde: Monde) -> None:
    sans_provenance = {
        "schema_version": 1,
        "amorce_id": "q.question.main.0",
        "tache": "Q",
        "emplacement": "question",
        "texte": "<question-factice-main>",
        "sha_texte": sha256_hex("<question-factice-main>"),
        "auteur_contenu": "public",
    }
    with pytest.raises(ProvenanceInvalide, match="schéma"):
        verifier(monde, [sans_provenance])
    mistral_sans_appel = sans_provenance | {"auteur_contenu": "mistral"}
    with pytest.raises(ProvenanceInvalide, match="schéma"):
        verifier(monde, [mistral_sans_appel])
    avec_les_deux = amorce_publique(monde) | {"appel_id": secrets.token_hex(16)}
    with pytest.raises(ProvenanceInvalide, match="schéma"):
        verifier(monde, [avec_les_deux])


def test_verifier_refuse_un_texte_qui_n_est_pas_a_la_ligne(monde: Monde) -> None:
    with pytest.raises(ProvenanceInvalide, match="différent de la ligne"):
        verifier(monde, [amorce_publique(monde, texte="<theme-factice-2>")])
    with pytest.raises(ProvenanceInvalide, match="introuvable"):
        verifier(monde, [amorce_publique(monde, ligne=99)])


def test_verifier_refuse_jeu_regle_sha_et_doublon(monde: Monde) -> None:
    with pytest.raises(ProvenanceInvalide, match="aucun jeu"):
        verifier(monde, [amorce_publique(monde, jeu="Org/autre")])
    with pytest.raises(ProvenanceInvalide, match="aucun jeu"):
        verifier(monde, [amorce_publique(monde, revision="c" * 40)])
    with pytest.raises(ProvenanceInvalide, match="aucun jeu"):
        verifier(monde, [amorce_publique(monde, emplacement="autre")])
    with pytest.raises(ProvenanceInvalide, match="sha_texte"):
        verifier(monde, [amorce_publique(monde) | {"sha_texte": "0" * 64}])
    with pytest.raises(ProvenanceInvalide, match="double"):
        verifier(monde, [amorce_publique(monde)] * 2)
    anael = {
        "schema_version": 1,
        "amorce_id": "q.question.anael.0",
        "tache": "Q",
        "emplacement": "question",
        "texte": "<question-factice-anael>",
        "sha_texte": sha256_hex("<question-factice-anael>"),
        "auteur_contenu": "anael",
    }
    with pytest.raises(ProvenanceInvalide, match="anael"):
        verifier(monde, [anael])


def test_verifier_refuse_un_run_illisible(monde: Monde) -> None:
    with pytest.raises(ProvenanceInvalide, match="illisible"):
        verifier_amorces(monde.racine, RUN_FACTICE, [], decodeur_json)
    with pytest.raises(ProvenanceInvalide, match="invalide"):
        verifier_amorces(monde.racine, "../..", [], decodeur_json)


def test_verifier_relit_le_jeu_et_son_sha(monde: Monde) -> None:
    jeux = monde.jeux_standard()
    monde.ecrire_amorces([amorce_publique(monde)], RUN_FACTICE)
    jeux[0].fichiers[0].chemin.write_bytes(b"{}\n")
    with pytest.raises(ProvenanceInvalide, match="SHA-256"):
        verifier_amorces(monde.racine, RUN_FACTICE, jeux, decodeur_json, regles=REGLES_TEST)


# --- Table de règles ----------------------------------------------------------------------


def test_regles_reelles_coherentes_avec_les_sources_et_les_volumes() -> None:
    from slmsp.fetch.config import charger_config_sources

    jeux = {jeu.nom: jeu for jeu in charger_config_sources().jeux}
    volumes = charger_config_donnees().volumes.par_tache()
    registre = RegistreLicences.charger()
    attendu = {
        ("service-public", "related_questions", "Q", "question"),
        ("data-gouv-datasets-catalog", "title", "RD", "demande"),
        ("service-public", "title", "CR", "theme"),
        ("service-public", "text", "LC", "texte"),
        ("service-public", "text", "CO", "texte"),
        ("service-public", "text", "RE", "texte"),
        ("piaf", "question", "generique", "demande"),
        ("service-public", "title", "CT", "sujet"),
    }
    assert {(r.jeu, r.colonne, r.tache, r.emplacement) for r in REGLES} == attendu
    for regle in REGLES:
        assert regle.jeu in jeux
        assert regle.tache in volumes
        assert 1 <= regle.longueur_min <= regle.longueur_max
        registre.exiger(jeux[regle.jeu].depot, "recherche")
    assert set(COLONNES_IDENTIFIANTS) <= set(jeux)


def test_regles_sans_texte_d_amorce() -> None:
    """Les règles ne portent que des noms de colonnes, de Tâches et d'emplacements (D1.1)."""
    for regle in REGLES:
        for valeur in (regle.jeu, regle.colonne, regle.tache, regle.emplacement, regle.sous_cle):
            assert valeur is None or len(valeur) <= 40
            assert valeur is None or " " not in valeur


# --- Amorces CT par Mistral (décision A2b) et longueurs RE ---------------------------------

REGLES_CT_RE = (
    RegleAmorce("service-public", "title", "CT", "sujet", 5, 100),
    RegleAmorce("service-public", "text", "RE", "texte", 5, 100),
)


def contenu_ct(i: int, **champs: Any) -> str:
    """Contenu JSON factice d'une réponse Mistral (aucun texte réaliste, D1.1)."""
    valeurs = {
        "type_courrier": f"<type-factice-{i}>",
        "objet": f"<objet-factice-{i}>",
        "elements_connus": f"<elements-connus-factice-{i}>",
    } | champs
    return json.dumps({k: v for k, v in valeurs.items() if v is not None})


class FabriqueCT:
    def __init__(self, contenus: Sequence[str] | None = None, *, budget: int | None = None):
        self.contenus = list(contenus or [])
        self.budget = budget
        self.appels: list[tuple[str, str, str]] = []
        self.ids: list[str] = []

    def __call__(self, seed_run_id: str, sujet_id: str, session_id: str) -> tuple[str, str]:
        if self.budget is not None and len(self.appels) >= self.budget:
            raise BudgetEpuise("plafond factice")
        self.appels.append((seed_run_id, sujet_id, session_id))
        self.ids.append(secrets.token_hex(16))
        rang = len(self.appels)
        contenu = self.contenus[rang - 1] if rang <= len(self.contenus) else contenu_ct(rang)
        return self.ids[-1], contenu


def executer_ct(monde: Monde, **options: Any):
    return monde.executer(regles=REGLES_CT_RE, config=config_petite(CT=5, RE=5), **options)


def test_courriers_mistral_trois_amorces_par_appel(monde: Monde) -> None:
    fabrique = FabriqueCT()
    resultat = executer_ct(monde, nb_courriers=2, fabrique_courriers=fabrique)
    assert resultat.statut == "complet"
    amorces = monde.amorces(resultat.run_id)
    sujets = [Amorce.model_validate(a) for a in amorces if a["emplacement"] == "sujet"]
    ct = [a for a in amorces if a["auteur_contenu"] == "mistral"]
    assert len(ct) == 6
    for rang, (sujet, appel_id) in enumerate(zip(sujets, fabrique.ids, strict=False), start=1):
        suffixe = sujet.amorce_id.removeprefix("ct.sujet.")
        groupe = [a for a in ct if a["appel_id"] == appel_id]
        assert {a["amorce_id"] for a in groupe} == {
            f"ct.type_courrier.{suffixe}",
            f"ct.objet.{suffixe}",
            f"ct.elements_connus.{suffixe}",
        }
        assert {a["emplacement"]: a["texte"] for a in groupe} == json.loads(contenu_ct(rang))
        assert all(a["tache"] == "CT" and a["sha_texte"] == sha256_hex(a["texte"]) for a in groupe)
    # Session stable d'un run à l'autre : la fabrique peut réutiliser le journal.
    assert [a[2] for a in fabrique.appels] == [seed_module.session_courrier(s) for s in sujets[:2]]
    comptes = monde.comptes(resultat.run_id)["courriers"]
    assert (comptes["appels"], comptes["produits"]) == (2, 2)
    assert verifier_amorces(
        monde.racine, resultat.run_id, monde.jeux_standard(), decodeur_json, regles=REGLES_CT_RE
    )


def test_courriers_session_stable_entre_deux_runs(monde: Monde) -> None:
    premiere, seconde = FabriqueCT(), FabriqueCT()
    executer_ct(monde, nb_courriers=2, fabrique_courriers=premiere)
    executer_ct(monde, nb_courriers=2, fabrique_courriers=seconde)
    assert [a[2] for a in premiere.appels] == [a[2] for a in seconde.appels]
    assert premiere.appels[0][0] != seconde.appels[0][0]  # deux runs distincts


@pytest.mark.parametrize(
    "contenu",
    [
        "<pas-du-json-factice>",
        "[1, 2]",
        contenu_ct(1, objet=None),
        contenu_ct(1, objet="<court>"),
        contenu_ct(1, elements_connus=["<liste-factice>"]),
        "",  # réponse sans texte (vide ou appels d'outil seuls) : chaîne vide de la fabrique
        contenu_ct(1, signature="<cle-en-trop-factice>"),  # exactement trois clés
    ],
)
def test_courrier_hors_schema_compte_sans_amorce(monde: Monde, contenu: str) -> None:
    resultat = executer_ct(monde, nb_courriers=1, fabrique_courriers=FabriqueCT([contenu]))
    assert not any(a["auteur_contenu"] == "mistral" for a in monde.amorces(resultat.run_id))
    assert monde.comptes(resultat.run_id)["courriers"]["schema_invalide"] == 1


def test_courrier_en_cloture_de_code_admis(monde: Monde) -> None:
    contenu = "```json\n" + contenu_ct(1) + "\n```"
    resultat = executer_ct(monde, nb_courriers=1, fabrique_courriers=FabriqueCT([contenu]))
    assert monde.comptes(resultat.run_id)["courriers"]["produits"] == 1


def test_courrier_doublon_par_objet(monde: Monde) -> None:
    contenus = [contenu_ct(1), contenu_ct(2, objet="<OBJET-factice-1>")]
    resultat = executer_ct(monde, nb_courriers=2, fabrique_courriers=FabriqueCT(contenus))
    comptes = monde.comptes(resultat.run_id)["courriers"]
    assert (comptes["produits"], comptes["doublons"]) == (1, 1)


def test_courrier_qui_recoupe_le_jeu_d_evaluation_est_exclu(monde: Monde) -> None:
    protection = protection_de(amorces=["<elements-connus-factice-1>"])
    resultat = executer_ct(
        monde, protection=protection, nb_courriers=2, fabrique_courriers=FabriqueCT()
    )
    comptes = monde.comptes(resultat.run_id)["courriers"]
    assert (comptes["produits"], comptes["exclus"]) == (1, 1)
    assert comptes["exclusions"]["amorce_usager"] == 1
    textes = {a["texte"] for a in monde.amorces(resultat.run_id)}
    assert "<objet-factice-1>" not in textes  # tout le courrier est écarté


def test_courrier_sans_texte_n_interrompt_pas_les_suivants(monde: Monde) -> None:
    fabrique = FabriqueCT(["", contenu_ct(2)])
    resultat = executer_ct(monde, nb_courriers=2, fabrique_courriers=fabrique)
    assert resultat.statut == "complet"
    comptes = monde.comptes(resultat.run_id)["courriers"]
    assert (comptes["appels"], comptes["schema_invalide"], comptes["produits"]) == (2, 1, 1)


def test_anti_fuite_des_courriers_avec_la_provenance_du_sujet(
    monde: Monde, monkeypatch: pytest.MonkeyPatch
) -> None:
    vus: dict[str, tuple[list[str], list[str]]] = {}
    origine = seed_module.Protection.motifs

    def espion(self: Any, texte: str, *, urls: Iterable[str] = (), ids: Iterable[str] = ()):
        vus[texte] = (list(urls), list(ids))
        return origine(self, texte, urls=urls, ids=ids)

    monkeypatch.setattr(seed_module.Protection, "motifs", espion)
    resultat = executer_ct(monde, nb_courriers=1, fabrique_courriers=FabriqueCT())
    sujet = next(a for a in monde.amorces(resultat.run_id) if a["emplacement"] == "sujet")
    urls, ids = vus["<objet-factice-1>"]
    assert urls and ids  # mêmes URL et identifiants que la ligne source du sujet
    assert vus[sujet["texte"]] == (urls, ids)
    assert vus["<type-factice-1>"] == vus["<elements-connus-factice-1>"] == (urls, ids)


def test_courriers_budget_epuise_run_partiel(monde: Monde) -> None:
    resultat = executer_ct(monde, nb_courriers=3, fabrique_courriers=FabriqueCT(budget=1))
    assert resultat.statut == "partiel-budget"
    assert monde.statut(resultat.run_id) == "partiel-budget"
    amorces = monde.amorces(resultat.run_id)
    assert sum(a["auteur_contenu"] == "mistral" for a in amorces) == 3
    assert sum(a["emplacement"] == "sujet" for a in amorces) == 4  # publiques conservées


def test_courriers_limites_par_nb_et_par_les_sujets(monde: Monde) -> None:
    fabrique = FabriqueCT()
    resultat = executer_ct(monde, nb_courriers=50, fabrique_courriers=fabrique)
    assert len(fabrique.appels) == 4  # 4 sujets disponibles
    assert monde.comptes(resultat.run_id)["courriers"]["sujets_disponibles"] == 4


def test_courriers_exigent_fabrique_et_source_mistral(tmp_path: Path) -> None:
    monde = Monde(tmp_path)
    resultat = executer_ct(monde, nb_courriers=0, fabrique_courriers=FabriqueCT())
    assert not any(a["auteur_contenu"] == "mistral" for a in monde.amorces(resultat.run_id))
    with pytest.raises(ValueError, match="fabrique"):
        executer_ct(monde, nb_courriers=1)
    texte = TOML_REGISTRE.split('[[sources]]\nid = "mistral')[0]
    (tmp_path / "data" / "registre-licences.toml").write_text(texte, encoding="utf-8")
    monde.registre = RegistreLicences.charger(racine=tmp_path)
    with pytest.raises(SourceSansLicence, match="mistral"):
        executer_ct(monde, nb_courriers=1, fabrique_courriers=FabriqueCT())


def jeux_re(monde: Monde, nb: int) -> list[JeuPublic]:
    lignes = [ligne_sp(i, text=f"<texte-re-factice-{i}>") for i in range(nb)]
    return [monde.jeu("service-public", "Org/service-public", REV_SP, [lignes])]


def test_longueurs_re_tirees_dans_la_configuration(monde: Monde) -> None:
    jeux = jeux_re(monde, 6)
    config = config_petite(RE=6)
    resultat = monde.executer(jeux, regles=REGLES_CT_RE, config=config)
    amorces = monde.amorces(resultat.run_id)
    textes = {a["amorce_id"] for a in amorces if a["emplacement"] == "texte"}
    longueurs = [Amorce.model_validate(a) for a in amorces if a["auteur_contenu"] == "config"]
    assert len(longueurs) == len(textes) == 6
    admises = set(config.seed.re_longueurs)
    for longueur in longueurs:
        assert longueur.lie_a in textes
        assert longueur.texte in admises
        assert longueur.amorce_id == longueur.lie_a.replace("re.texte.", "re.longueur_demandee.")
    assert monde.comptes(resultat.run_id)["longueurs_re"]["produites"] == 6
    # Tirage reproductible : un second run donne les mêmes longueurs.
    autre = monde.amorces(monde.executer(jeux, regles=REGLES_CT_RE, config=config).run_id)
    assert [a for a in autre if a["auteur_contenu"] == "config"] == [
        a for a in amorces if a["auteur_contenu"] == "config"
    ]
    verifier_amorces(monde.racine, resultat.run_id, jeux, decodeur_json, regles=REGLES_CT_RE)


def test_verifier_refuse_une_longueur_sans_amorce_liee(monde: Monde) -> None:
    longueur = {
        "schema_version": 1,
        "amorce_id": "re.longueur_demandee.x",
        "tache": "RE",
        "emplacement": "longueur_demandee",
        "texte": "courte",
        "sha_texte": sha256_hex("courte"),
        "auteur_contenu": "config",
        "lie_a": "re.texte.absente",
    }
    monde.ecrire_amorces([longueur], RUN_FACTICE)
    with pytest.raises(ProvenanceInvalide, match="liée"):
        verifier_amorces(monde.racine, RUN_FACTICE, [], decodeur_json)


@pytest.mark.parametrize(
    ("champs", "admis"),
    [
        ({}, True),
        ({"texte": "<longueur-factice>"}, False),
        ({"texte": "80 mots"}, False),
        ({"texte": "détaillée"}, False),
        ({"emplacement": "texte"}, False),
        ({"lie_a": None}, False),
        ({"appel_id": "a" * 32}, False),
    ],
)
def test_schema_amorce_config(champs: dict[str, Any], admis: bool) -> None:
    valeurs = {
        "schema_version": 1,
        "amorce_id": "re.longueur_demandee.x",
        "tache": "RE",
        "emplacement": "longueur_demandee",
        "texte": "moyenne",
        "auteur_contenu": "config",
        "lie_a": "re.texte.x",
    } | champs
    valeurs["sha_texte"] = sha256_hex(valeurs["texte"])
    if admis:
        Amorce.model_validate(valeurs)
    else:
        with pytest.raises(ValueError):
            Amorce.model_validate(valeurs)


def test_lie_a_reserve_aux_amorces_config() -> None:
    with pytest.raises(ValueError, match="lie_a"):
        Amorce.model_validate(
            {
                "schema_version": 1,
                "amorce_id": "q.question.x",
                "tache": "Q",
                "emplacement": "question",
                "texte": "<q-factice>",
                "sha_texte": sha256_hex("<q-factice>"),
                "auteur_contenu": "public",
                "jeu": "j",
                "revision": "r",
                "ligne": 0,
                "lie_a": "q.question.y",
            }
        )


def test_texte_de_reponse_et_conformite() -> None:
    from slmsp.core.schemas.amorce import texte_de_reponse, texte_mistral_conforme

    contenu = contenu_ct(3, objet="  <objet-factice-3>  ")
    assert texte_de_reponse(contenu, "objet") == "<objet-factice-3>"
    assert texte_de_reponse("```\n" + contenu + "\n```", "objet") == "<objet-factice-3>"
    assert texte_de_reponse(contenu, "absente") is None
    assert texte_de_reponse(None, "objet") is None
    amorce = Amorce.model_validate(
        {
            "schema_version": 1,
            "amorce_id": "ct.objet.x",
            "tache": "CT",
            "emplacement": "objet",
            "texte": "<objet-factice-3>",
            "sha_texte": sha256_hex("<objet-factice-3>"),
            "auteur_contenu": "mistral",
            "appel_id": "a" * 32,
        }
    )
    assert texte_mistral_conforme(contenu, amorce)
    assert texte_mistral_conforme("<objet-factice-3>", amorce)
    assert not texte_mistral_conforme(contenu_ct(4), amorce)


def test_generate_groupe_longueur_avec_son_texte_et_courrier_par_appel(monde: Monde) -> None:
    from slmsp.data.generate import _groupes

    resultat = monde.executer(
        jeux_re(monde, 3),
        regles=REGLES_CT_RE,
        config=config_petite(RE=3, CT=3),
        nb_courriers=2,
        fabrique_courriers=FabriqueCT(),
    )
    amorces = [Amorce.model_validate(a) for a in monde.amorces(resultat.run_id)]
    re_ = [a for a in amorces if a.tache == "RE"]
    complets, incomplets, _ = _groupes(re_, ["longueur_demandee", "texte"])
    assert (len(complets), incomplets) == (3, 0)
    assert all(g[0].lie_a == g[1].amorce_id for g in complets)
    ct = [a for a in amorces if a.tache == "CT"]
    complets, incomplets, ignorees = _groupes(ct, ["type_courrier", "objet", "elements_connus"])
    assert (len(complets), incomplets, ignorees) == (2, 0, 3)  # sujets publics ignorés
    assert all(len({a.appel_id for a in g}) == 1 for g in complets)


def test_longueurs_re_hors_evaluation_refusees() -> None:

    assert SeedDonnees().re_longueurs == ["courte", "moyenne", "detaillee"]
    for invalide in (["détaillée"], ["80 mots"], []):
        with pytest.raises(ValueError):
            SeedDonnees(re_longueurs=invalide)


def test_mots_admis_de_l_amorce_egaux_a_evaluation_toml() -> None:
    """Une seule vérité pour les mots admis : le motif de l'amorce `config` et
    `[re.longueurs]` de `config/evaluation.toml` doivent rester égaux."""
    import re

    from slmsp.core.config import plafonds_re_evaluation
    from slmsp.core.schemas.amorce import MOTIF_TEXTE_CONFIG

    assert set(MOTIF_TEXTE_CONFIG.split("|")) == set(plafonds_re_evaluation())
    assert all(re.fullmatch(MOTIF_TEXTE_CONFIG, mot) for mot in plafonds_re_evaluation())
    assert set(SeedDonnees().re_longueurs) == set(plafonds_re_evaluation())


@pytest.mark.parametrize("contenu", [None, b"\xff\xfe\x00", b"[re\n"])
def test_evaluation_toml_illisible_rejette_la_configuration_seed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, contenu: bytes | None
) -> None:
    (tmp_path / "config").mkdir()
    if contenu is not None:
        (tmp_path / "config" / "evaluation.toml").write_bytes(contenu)
    monkeypatch.setattr("slmsp.core.config.racine_projet", lambda: tmp_path)
    with pytest.raises(ValueError, match="illisible"):
        SeedDonnees(re_longueurs=["courte"])


class FabriqueTronquee(FabriqueFactice):
    """Fabrique dont le premier appel renvoie une réponse tronquée (`length`)."""

    def __call__(self, seed_run_id: str, theme_id: str, session_id: str) -> tuple[str, str]:
        if not self.appels:
            self.appels.append((seed_run_id, theme_id, session_id))
            raise ReponseTronquee("appel factice : réponse tronquée (length)")
        return super().__call__(seed_run_id, theme_id, session_id)


def test_scenario_tronque_ecarte_et_compte(monde: Monde) -> None:
    resultat = monde.executer(
        nb_scenarios=2, fabrique_scenarios=FabriqueTronquee(monde), config=config_petite(CR=5)
    )
    scenarios = monde.comptes(resultat.run_id)["scenarios"]
    assert (scenarios["demandes"], scenarios["produits"], scenarios["tronques"]) == (2, 1, 1)
    produits = [a for a in monde.amorces(resultat.run_id) if a["emplacement"] == "scenario"]
    assert len(produits) == 1
