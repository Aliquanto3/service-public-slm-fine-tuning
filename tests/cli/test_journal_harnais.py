"""Journal `slmsp.harness` de la CLI : WARNING sur stderr (correctif F2)."""

from __future__ import annotations

import logging

import pytest

from slmsp import cli


@pytest.fixture
def journal():
    logger = logging.getLogger("slmsp.harness")
    avant = list(logger.handlers)
    yield logger
    logger.handlers[:] = avant


def test_main_journalise_le_harnais_sur_stderr(journal, capsys) -> None:
    racine = list(logging.getLogger().handlers)
    cli.main([])
    cli.main([])  # un seul gestionnaire, même après plusieurs appels
    capsys.readouterr()
    journal.warning("<cause-factice-1>")
    journal.info("<detail-factice-1>")
    err = capsys.readouterr().err
    assert err.count("<cause-factice-1>") == 1
    assert "slmsp : slmsp.harness : WARNING" in err
    assert "<detail-factice-1>" not in err
    assert logging.getLogger().handlers == racine  # logger racine intact
