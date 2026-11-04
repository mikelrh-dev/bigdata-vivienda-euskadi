"""Tests for real GeoJSON Point in anuncios."""

from __future__ import annotations

import math

from storage.load_mongo import load_anuncios
from storage.mongo import get_collection, ping


def test_anuncios_geojson_real():
    assert ping() is True
    n = load_anuncios()
    assert n >= 700
    coll = get_collection("anuncios")
    total = coll.count_documents({})
    assert total >= 700
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
