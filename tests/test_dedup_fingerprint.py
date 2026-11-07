"""M6 DEDUP-01: dedup dura por `property_fingerprint` (cross-portal).

- Dos anuncios de portales distintos con identico fingerprint -> 1 fila.
- La salida unificada real no contiene duplicados (0).
- Sin dos documentos de `anuncios` con el mismo fingerprint en Mongo
  (skip-separado si no hay Mongo local).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "transform"))


def _mongo_ok() -> bool:
    try:
        from storage.mongo import ping
        return ping() is True
    except Exception:
        return False


def _recs_cross_portal():
    from unificar_anuncios import _property_fingerprint
    base = {
        "precio_eur": 900,
        "superficie_m2": 80,
        "habitaciones": 3,
        "ubicacion": {"codigo_ine": "48020"},
    }
    r1 = dict(base, portal="fotocasa", id_anuncio="F1", _source_order=0)
    r2 = dict(base, portal="pisos", id_anuncio="P1", _source_order=1)
    r1["_fingerprint"] = _property_fingerprint(r1)
    r2["_fingerprint"] = _property_fingerprint(r2)
    return r1, r2


def test_dedup_fingerprint_dos_portales_una_fila():
    from unificar_anuncios import deduplicar_fingerprint
    r1, r2 = _recs_cross_portal()
    assert r1["_fingerprint"] == r2["_fingerprint"]
    conservados, descartados = deduplicar_fingerprint([r2, r1])
    assert len(conservados) == 1
    assert len(descartados) == 1
    assert descartados[0]["fingerprint"] == r1["_fingerprint"]


def test_unificados_sin_duplicados_fingerprint():
    d = pd.read_csv(ROOT / "data" / "procesado" / "anuncios_unificados.csv", dtype=str)
    assert "property_fingerprint" in d.columns
    assert int(d["property_fingerprint"].duplicated().sum()) == 0


@pytest.mark.skipif(not _mongo_ok(), reason="sin Mongo local: skip separado")
def test_mongo_sin_duplicados_fingerprint():
    from storage.mongo import get_collection
    coll = get_collection("anuncios")
    # 0 grupos con >1 documento con el mismo fingerprint.
    grupos = list(coll.aggregate([
        {"$match": {"property_fingerprint": {"$ne": None}}},
        {"$group": {"_id": "$property_fingerprint", "n": {"$sum": 1}}},
        {"$match": {"n": {"$gt": 1}}},
        {"$limit": 5},
    ]))
    assert grupos == []
