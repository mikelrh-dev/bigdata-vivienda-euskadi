"""TIER-CONFIANZA: tiers A/B/C/D derivados solo de n_anuncios real en Mongo.

- Conteos 4/3/57/188 = 252 desde Mongo (pipeline_tier_por_municipio).
- Tier C/D con n_precio=0 y min/max nulos, sin precio municipal.
- n_precio_temporal != n_precio_larga en los 3 Tier B (Sopela/Zarautz/Santurtzi).
- Sin promocion comarcal/IDW: n<30 nunca sube a Tier A.
- Doble ejecucion con SHA identico.
"""

from __future__ import annotations

import hashlib
import inspect
import json

import pytest


def _mongo_ok() -> bool:
    try:
        from storage.mongo import ping
        return ping() is True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _mongo_ok(), reason="sin Mongo local: skip separado")

from analysis.mongo_aggregations import pipeline_tier_por_municipio  # noqa: E402


@pytest.fixture(scope="module")
def tier():
    return pipeline_tier_por_municipio()


def _conteo(filas, t):
    return sum(1 for f in filas if f.get("tier") == t)


def test_conteos_4_3_57_188_total_252(tier):
    counter = {"A": _conteo(tier, "A"), "B": _conteo(tier, "B"),
               "C": _conteo(tier, "C"), "D": _conteo(tier, "D")}
    assert counter == {"A": 4, "B": 3, "C": 57, "D": 188}, counter
    assert len(tier) == 252
    assert sum(counter.values()) == 252
    # Unico tier por municipio: 252 codigo_ine distintos.
    assert len({f["codigo_ine"] for f in tier}) == 252


def test_tier_a_son_bilbao_donostia_getxo_vitoria(tier):
    a = sorted((f["nombre"], f["n_anuncios"]) for f in tier if f["tier"] == "A")
    assert a == [("Bilbao", 204), ("Donostia / San Sebastián", 126),
                 ("Getxo", 50), ("Vitoria-Gasteiz", 39)], a
    assert all(f["n_anuncios"] >= 30 for f in tier if f["tier"] == "A")
    assert all(f["tier_etiqueta"] == "fuerte" for f in tier if f["tier"] == "A")


def test_tier_b_son_sopela_zarautz_santurtzi(tier):
    b = sorted((f["nombre"], f["n_anuncios"]) for f in tier if f["tier"] == "B")
    assert b == [("Santurtzi", 11), ("Sopela", 19), ("Zarautz", 15)], b
    for f in tier:
        if f["tier"] == "B":
            assert f["tier_etiqueta"] == "indicativo"
            assert f["n_precio"] > 0
            assert f["min_precio"] is not None
            assert f["max_precio"] is not None


def test_tier_c_d_sin_precio_municipal(tier):
    for f in tier:
        if f["tier"] in ("C", "D"):
            assert int(f["n_precio"]) == 0, f
            assert f["min_precio"] is None, f
            assert f["max_precio"] is None, f
            assert f["mediana_precio"] is None, f
            assert int(f["n_precio_temporal"]) == 0, f
            assert int(f["n_precio_larga"]) == 0, f
    c = [f for f in tier if f["tier"] == "C"]
    d = [f for f in tier if f["tier"] == "D"]
    assert all(1 <= int(f["n_anuncios"]) <= 9 for f in c)
    assert all(int(f["n_anuncios"]) == 0 for f in d)
    assert all(f["tier_etiqueta"] == "sin precio municipal" for f in c)
    assert all(f["tier_etiqueta"] == "sin dato (+ contexto oficial)" for f in d)


def test_tier_b_temporal_no_igual_larga(tier):
    b = [f for f in tier if f["tier"] == "B"]
    assert len(b) == 3
    for f in b:
        assert int(f["n_precio_temporal"]) != int(f["n_precio_larga"]), f
        assert int(f["n_precio_temporal"]) > 0 and int(f["n_precio_larga"]) > 0, f


def test_sin_promocion_comarcal_ni_idw(tier):
    # n<30 nunca sube a Tier A: B/C/D todos con n<30.
    for f in tier:
        if f["tier"] in ("B", "C", "D"):
            assert int(f["n_anuncios"]) < 30, f
    # La pipeline no imputa: solo lee anuncios + municipios.
    from analysis import mongo_aggregations
    src = inspect.getsource(mongo_aggregations.pipeline_tier_por_municipio)
    assert '"from": "anuncios"' in src
    assert 'get_collection("municipios")' in src
    assert 'get_collection("alquiler' not in src
    assert 'get_collection("comarca' not in src


def test_doble_ejecucion_sha_identico(tier):
    otra = pipeline_tier_por_municipio()
    def _huella(rows):
        def _jsonable(v):
            from bson.decimal128 import Decimal128
            if isinstance(v, Decimal128):
                return str(v.to_decimal())
            if isinstance(v, dict):
                return {str(k): _jsonable(x) for k, x in v.items()}
            if isinstance(v, (list, tuple)):
                return [_jsonable(x) for x in v]
            return v
        texto = json.dumps(_jsonable(rows), sort_keys=True, default=str,
                           ensure_ascii=False)
        return hashlib.sha256(texto.encode("utf-8")).hexdigest()
    assert _huella(tier) == _huella(otra)
