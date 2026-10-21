"""Dédoublonnage du préfixe commun des passages d'une même page (story 16.2)."""

from __future__ import annotations

import dataclasses

from harness_factices import passage

from slmsp.core.ports import Passage
from slmsp.harness.citations import sources_citees
from slmsp.harness.config import VERSION_HARNAIS, charger_config_harnais
from slmsp.harness.dedoublonnage import dedoublonner_prefixes
from slmsp.index.config import charger_config_index

PREFIXE = "<titre-factice> <introduction-factice> " * 3 + "\n"


def _page(doc_id: str, numero: int, texte: str) -> Passage:
    return dataclasses.replace(passage(numero, 0.9), doc_id=doc_id, texte=texte)


def test_prefixe_retire_des_seuls_passages_suivants() -> None:
    passages = [
        _page("P1", 1, PREFIXE + "<corps-factice-1>"),
        _page("P2", 2, "<autre-page-factice>"),
        _page("P1", 3, PREFIXE + "<corps-factice-2>"),
        _page("P1", 4, PREFIXE + "<corps-factice-3>"),
    ]
    sortie = dedoublonner_prefixes(passages, 20)
    assert [p.texte for p in sortie] == [
        PREFIXE + "<corps-factice-1>",
        "<autre-page-factice>",
        "<corps-factice-2>",
        "<corps-factice-3>",
    ]
    assert [p.chunk_id for p in sortie] == [p.chunk_id for p in passages]


def test_page_a_un_seul_passage_intacte() -> None:
    passages = [_page("P1", 1, PREFIXE + "<corps-factice-1>")]
    assert dedoublonner_prefixes(passages, 20) == passages


def test_prefixe_trop_court_ignore() -> None:
    passages = [_page("P1", 1, "<court> <corps-1>"), _page("P1", 2, "<court> <corps-2>")]
    assert dedoublonner_prefixes(passages, 80) == passages


def test_passage_reduit_au_prefixe_reste_intact() -> None:
    passages = [_page("P1", 1, PREFIXE + "<corps-1>"), _page("P1", 2, PREFIXE)]
    assert dedoublonner_prefixes(passages, 20)[1].texte == PREFIXE


def test_extrait_propre_a_chaque_passage() -> None:
    passages = [
        _page("P1", 1, PREFIXE + "<corps-factice-1>"),
        _page("P1", 2, PREFIXE + "<corps-factice-2>"),
    ]
    sources = sources_citees("[1] [2]", dedoublonner_prefixes(passages, 20))
    assert sources[1].extrait == "<corps-factice-2>"
    assert sources[0].extrait != sources[1].extrait


def test_coupe_au_mot_quand_un_texte_est_prefixe_de_l_autre() -> None:
    base = "<mot-factice> " * 10
    passages = [_page("P1", 1, base + "ABCDE"), _page("P1", 2, base + "ABCDEF fin")]
    sortie = dedoublonner_prefixes(passages, 20)
    assert sortie[1].texte == "ABCDEF fin"
    assert sortie[0] == passages[0]


def test_k_de_q_distinct_de_l_index_et_version_du_harnais() -> None:
    # Q seule passe à 8 passages ; Recherche de données et génération de données gardent 5.
    assert charger_config_index().k == 5
    assert charger_config_harnais().recherche.k == 5
    assert charger_config_harnais().question.passages == 8
    assert VERSION_HARNAIS == 2
