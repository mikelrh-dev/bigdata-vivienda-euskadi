"""Tests for INDICES-01 con explain read-only (sin mutar prod).

Triada RA3 nivel 10: explain antes y despues con hint $natural,
comparando COLLSCAN e IXSCAN con nReturned, totalDocsExamined
y totalKeysExamined segun Tema 8 seccion 9. AISLAMIENTO-02: el
explain NO dropea ni crea índices; el "antes" fuerza COLLSCAN con
hint $natural y el "después" usa el índice ESR presente.
"""

from __future__ import annotations

import pytest

from analysis import mongo_indexes as mi
from storage.mongo import ping

pytestmark = pytest.mark.skipif(not ping(), reason="sin Mongo local: skip separado")


def test_indexes_explain_totalDocsExamined():
    res = mi.explain_before_after()
    before = res["before"]
    after = res["after"]

    assert before["stage"] == "COLLSCAN", before
    assert after["stage"] == "IXSCAN", after

    for stats in (before, after):
        assert stats["nReturned"] is not None, stats
        assert stats["totalDocsExamined"] is not None, stats
        assert stats["totalKeysExamined"] is not None, stats

    assert before["totalDocsExamined"] > after["totalDocsExamined"], (before, after)
    assert after["totalDocsExamined"] <= after["nReturned"] + after["totalKeysExamined"], (before, after)
    assert before["nReturned"] == after["nReturned"], (before, after)
    # Filtro canónico 20069 -> 1 documento (IXSCAN demostrable).
    assert after["nReturned"] == 1, after

    promo = mi.explain_promo_before_after()
    p_before = promo["before"]
    p_after = promo["after"]

    assert p_before["stage"] == "COLLSCAN", p_before
    assert p_after["stage"] == "IXSCAN", p_after

    for stats in (p_before, p_after):
        assert stats["nReturned"] is not None, stats
        assert stats["totalDocsExamined"] is not None, stats
        assert stats["totalKeysExamined"] is not None, stats

    assert p_before["totalDocsExamined"] > p_after["totalDocsExamined"], (p_before, p_after)
    assert p_after["totalDocsExamined"] <= p_after["nReturned"] + p_after["totalKeysExamined"], (p_before, p_after)
    assert p_before["nReturned"] == p_after["nReturned"], (p_before, p_after)

