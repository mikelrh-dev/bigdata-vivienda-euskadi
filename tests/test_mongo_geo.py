"""Tests for real GeoJSON Point in anuncios (aislado de prod).

AISLAMIENTO-01: la carga de anuncios se hace contra ``vivienda_euskadi_test``
(vía ``get_test_db``), nunca contra la base productiva. El test de geo real
sigue leyendo los 594 documentos del silver, pero en la base de test.
"""

from __future__ import annotations

import math

import pytest

from storage import mongo as sm
from storage.load_mongo import load_anuncios
from storage.mongo import get_collection, get_test_db, ping


@pytest.fixture()
def geo_test_db(monkeypatch):
    """Carga los anuncios del silver en ``vivienda_euskadi_test`` (prod intacta)."""
    db = get_test_db()
    monkeypatch.setattr(sm, "get_db", lambda: db)
    return db


@pytest.mark.skipif(not ping(), reason="sin Mongo local: skip separado")
def test_anuncios_geojson_real(geo_test_db):
    n = load_anuncios()
    assert n >= 500
    coll = get_collection("anuncios")
    total = coll.count_documents({})
    assert total >= 500
    puntos = 0
    invalid = 0
    for doc in coll.find({"ubicacion.coordenadas": {"$ne": None}}, {"ubicacion.coordenadas": 1}):
        c = (doc.get("ubicacion") or {}).get("coordenadas")
        if c is None:
            continue
        if (
            isinstance(c, dict)
            and c.get("type") == "Point"
            and isinstance(c.get("coordinates"), list)
            and len(c["coordinates"]) == 2
        ):
            lon, lat = c["coordinates"]
            if (
                isinstance(lon, (int, float))
                and isinstance(lat, (int, float))
                and math.isfinite(lon)
                and math.isfinite(lat)
                and -180 <= lon <= 180
                and -90 <= lat <= 90
            ):
                puntos += 1
            else:
                invalid += 1
        else:
            invalid += 1
    assert invalid == 0
    assert puntos > 0
