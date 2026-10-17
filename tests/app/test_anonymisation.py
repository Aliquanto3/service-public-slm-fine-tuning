"""Anonymisation (story 12.3) : motifs générés au hasard, aucune donnée réelle (D1)."""

from __future__ import annotations

import random

import pytest

from slmsp.app.anonymisation import (
    MASQUE,
    anonymiser,
    iban_valide,
    lire_prenoms,
    nir_valide,
)
from slmsp.core.prenoms_insee import prenoms_depuis_csv_insee

PRENOMS = frozenset({"alphaprenom", "betaprenom", "gammaprenom"})


def _chiffres(rng: random.Random, n: int) -> str:
    return "".join(rng.choice("0123456789") for _ in range(n))


def _nir(rng: random.Random, *, corse: bool = False) -> str:
    base = rng.choice("12") + _chiffres(rng, 2) + f"{rng.randint(1, 12):02d}"
    base += "2A" if corse else f"{rng.randint(1, 95):02d}"
    base += _chiffres(rng, 6)
    cle = 97 - int(base.replace("2A", "19")) % 97
    return f"{base[0]} {base[1:3]} {base[3:5]} {base[5:7]} {base[7:10]} {base[10:13]} {cle:02d}"


def _iban(rng: random.Random) -> str:
    bban = _chiffres(rng, 23)
    cle = 98 - int(bban + "152700") % 97  # FR = 15 27, puis 00
    brut = f"FR{cle:02d}{bban}"
    return " ".join(brut[i : i + 4] for i in range(0, len(brut), 4))


def _tel_fr(rng: random.Random) -> str:
    return "0" + str(rng.randint(1, 9)) + "".join(f" {_chiffres(rng, 2)}" for _ in range(4))


def _tel_int(rng: random.Random) -> str:
    return f"+44 {_chiffres(rng, 4)} {_chiffres(rng, 6)}"


def _email(rng: random.Random) -> str:
    return f"zz{_chiffres(rng, 4)}.qq@exemple-factice.invalid"


def _adresse(rng: random.Random) -> str:
    return f"{rng.randint(1, 99)} rue Factice {rng.randint(10000, 95999)} Villefactice"


def test_clefs_de_controle():
    rng = random.Random(1)
    assert nir_valide(_nir(rng)) and nir_valide(_nir(rng, corse=True))
    assert not nir_valide("1 23 45 67 890 123 00")
    assert iban_valide(_iban(rng))
    assert not iban_valide("FR00 0000 0000 0000 0000 0000 000")


def test_chaque_motif_est_masque():
    """Critère 1 : aucune occurrence en clair, comptes par motif."""
    rng = random.Random(2)
    valeurs = {
        "nir": _nir(rng),
        "iban": _iban(rng),
        "email": _email(rng),
        "telephone": _tel_fr(rng),
        "adresse": _adresse(rng),
        "nom": "Mme Zorglubar",
    }
    texte = " ; ".join(f"voici {v}" for v in valeurs.values())
    texte += f" ; {_tel_int(rng)} ; Alphaprenom Zorglub ; DURANDAL Betaprenom"
    masque, comptes = anonymiser(texte, prenoms=PRENOMS)
    for valeur in [*valeurs.values(), "Zorglub", "DURANDAL"]:
        assert valeur not in masque
    assert "+44" not in masque
    assert comptes["nir"] == 1 and comptes["iban"] == 1 and comptes["email"] == 1
    assert comptes["telephone"] == 2 and comptes["adresse"] == 1 and comptes["nom"] == 3
    assert masque.count(MASQUE) == sum(comptes.values())


def test_formes_sans_espaces_et_corse():
    rng = random.Random(3)
    nir, iban = _nir(rng, corse=True), _iban(rng)
    masque, _ = anonymiser(f"{nir.replace(' ', '')} / {iban.replace(' ', '')}")
    assert masque == f"{MASQUE} / {MASQUE}"


def test_invalides_conserves_et_suite_apres_iban():
    rng = random.Random(4)
    iban = _iban(rng)
    texte = f"2 12 34 56 789 012 00 et FR76 1234 5678 9012 3456 789 puis {iban} AGENT"
    masque, comptes = anonymiser(texte)
    assert masque.startswith("2 12 34 56 789 012 00 et FR76")  # clés fausses : conservés
    assert masque.endswith(f"puis {MASQUE} AGENT")
    assert comptes["iban"] == 1 and comptes["nir"] == 0


def test_sans_prenoms_embarques_seules_les_civilites():
    masque, comptes = anonymiser("M. Zorglubar écrit à alphaprenom Zorglub", prenoms=frozenset())
    assert masque == f"{MASQUE} écrit à alphaprenom Zorglub"
    assert comptes["nom"] == 1


def test_prenom_seul_ou_mot_suivant_minuscule_conserve():
    texte = "alphaprenom est parti ; Alphaprenom, puis alphaprenom dossier"
    assert anonymiser(texte, prenoms=PRENOMS)[0] == texte


def test_faux_positifs_corpus_aleatoire():
    """Critère 2 : montants, dates, articles, numéros de dossier restent inchangés."""
    rng = random.Random(5)
    phrases = []
    for _ in range(500):
        jour, mois, annee = rng.randint(1, 28), rng.randint(1, 12), rng.randint(2010, 2029)
        phrases.append(
            f"Le montant de {rng.randint(1, 99)} {_chiffres(rng, 3)},{_chiffres(rng, 2)} € "
            f"est dû avant le {jour:02d}/{mois:02d}/{annee} "
            f"selon l'article L. {rng.randint(1, 999)}-{rng.randint(1, 9)} du code, "
            f"dossier n° {annee}-{_chiffres(rng, 6)}, "
            f"référence {_chiffres(rng, 5)} et {rng.randint(1, 99)} jours."
        )
    modifies = [p for p in phrases if anonymiser(p, prenoms=PRENOMS)[0] != p]
    taux = len(modifies) / len(phrases)
    print(f"faux positifs : {len(modifies)}/{len(phrases)} ({taux:.1%})")
    assert taux == 0


def test_prenoms_depuis_csv_et_lecture(tmp_path):
    csv = [
        "sexe;preusuel;annais;nombre",
        "1;ALPHAPRENOM;1990;30",
        "1;ALPHAPRENOM;1991;10",
        "2;RAREPRENOM;1990;5",
        "1;_PRENOMS_RARES;1990;900",
        "1;XY;1990;900",
    ]
    prenoms = prenoms_depuis_csv_insee(csv)
    assert prenoms == ["alphaprenom"]
    fichier = tmp_path / "prenoms.txt"
    fichier.write_text("# licence\nÉlodietest\n" + "\n".join(prenoms), encoding="utf-8")
    assert lire_prenoms(fichier) == {"elodietest", "alphaprenom"}
    assert lire_prenoms(tmp_path / "absent.txt") == frozenset()


@pytest.mark.parametrize("texte", ["", "Rien à masquer."])
def test_texte_vide_ou_neutre(texte):
    assert anonymiser(texte)[0] == texte


@pytest.mark.parametrize("espace", [" ", " "])
def test_espaces_insecables(espace):
    """Espaces insécables et fines : NIR, IBAN, téléphone, adresse, civilité, Prénom Nom."""
    rng = random.Random(6)
    nir, iban, tel = _nir(rng), _iban(rng), _tel_fr(rng)
    texte = " ; ".join(
        [
            nir.replace(" ", espace),
            iban.replace(" ", espace),
            tel.replace(" ", espace),
            "12 rue des Tests 75001 Villefictive".replace(" ", espace),
            f"Mme{espace}Zorglubar",
            f"Alphaprenom{espace}Zorglub",
        ]
    )
    masque, comptes = anonymiser(texte, prenoms=PRENOMS)
    assert masque == " ; ".join([MASQUE] * 6)
    assert sum(comptes.values()) == 6


def test_numero_de_dossier_00_n_est_pas_un_telephone():
    for texte in ("dossier 0012345678", "dossier n° 00123456789", "réf 004521987"):
        assert anonymiser(texte, prenoms=PRENOMS)[0] == texte
    # Un 00 avec indicatif pays plausible reste masqué, collé ou séparé.
    assert anonymiser("0044791112345", prenoms=PRENOMS)[0] == MASQUE
    assert anonymiser("0017025550123", prenoms=PRENOMS)[0] == MASQUE
    assert anonymiser("0044 7911 123456", prenoms=PRENOMS)[0] == MASQUE


def test_adresse_code_postal_suivi_d_une_unite_monetaire():
    for texte in ("2 place de la gare 12345 euros", "3 rue Test, 10 000 € ou 4 avenue X 54321 EUR"):
        assert anonymiser(texte, prenoms=PRENOMS)[0] == texte
    assert anonymiser("2 place de la gare 12345 Ville", prenoms=PRENOMS)[0] == MASQUE


def test_faux_positifs_cas_complementaires():
    """Critère 2 élargi : insécables dans les montants et dates, dossiers 00…, « n place … »."""
    rng = random.Random(7)
    for _ in range(200):
        texte = (
            f"Montant de {rng.randint(1, 99)} {_chiffres(rng, 3)},{_chiffres(rng, 2)} € "
            f"dossier 00{rng.choice('5689')}{_chiffres(rng, rng.randint(4, 8))} ; "
            f"{rng.randint(1, 9)} place{' '}à réserver pour {_chiffres(rng, 5)} euros"
        )
        masque = anonymiser(texte, prenoms=PRENOMS)[0]
        assert masque == texte.replace(" ", " ").replace(" ", " ")  # seules les espaces
