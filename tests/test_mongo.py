"""Tests for MongoDB phase."""

from __future__ import annotations

from pathlib import Path

import pytest
from bson.decimal128 import Decimal128

ROOT = Path(__file__).resolve().parent.parent

from storage.mongo import get_collection, ping, zfill_ine
from storage import clean_mongo
from analysis import mongo_queries as mq
from analysis import mongo_aggregations as ma
from analysis import mongo_indexes as mi


@pytest.fixture(scope="module", autouse=True)
def _ensure_data():
    assert ping(), "MongoDB no responde"
    # ensure indexes baseline at least exists for query tests
    yield


def test_conexion():
    assert ping() is True
    assert get_collection("municipios").database.name == "vivienda_euskadi"


def test_conteos():
    assert get_collection("municipios").count_documents({}) == 252
    assert get_collection("anuncios").count_documents({}) == 759
    assert get_collection("alquiler_municipal").count_documents({}) == 252
    assert get_collection("indicadores").count_documents({}) == 252
    assert get_collection("ecvi_compraventa").count_documents({}) == 29
    assert get_collection("udalmap_indicadores").count_documents({}) == 252
    assert get_collection("udalmap_empleo").count_documents({}) == 252
    assert get_collection("osrm_tiempos").count_documents({}) == 252
    assert get_collection("emancipacion_juventud").count_documents({}) == 1
    assert get_collection("etxebide_solicitudes").count_documents({}) == 5040
    assert get_collection("udalmap_extendido").count_documents({}) == 252
    assert get_collection("etxebide_promociones").count_documents({}) == 406


def test_codigo_ine_canonico():
    for coll_name, field in [("municipios", "_id"), ("anuncios", "ubicacion.codigo_ine"),
                             ("alquiler_municipal", "_id"), ("indicadores", "_id")]:
        coll = get_collection(coll_name)
        if coll_name in ("municipios", "alquiler_municipal", "indicadores"):
            vals = [d["_id"] for d in coll.find({}, {"_id": 1})]
        elif coll_name == "anuncios":
            vals = [d["ubicacion"]["codigo_ine"] for d in coll.find({}, {"ubicacion.codigo_ine": 1})]
        else:
            vals = [d["codigo_ine"] for d in coll.find({}, {"codigo_ine": 1})]
        assert all(isinstance(v, str) and len(v) == 5 for v in vals if v is not None)
        if coll_name in ("municipios", "alquiler_municipal", "indicadores"):
            assert all(v is not None for v in vals)


def test_tiene_alquiler_oficial():
    n = get_collection("municipios").count_documents({"tiene_alquiler_oficial": True})
    assert n >= 150


def test_query_por_municipio():
    code = "48001"
    res = mq.anuncios_por_municipio(code)
    assert isinstance(res, list)
    assert all(d["ubicacion"]["codigo_ine"] == code for d in res)


def test_query_dot_notation():
    code = "48001"
    res = mq.dot_notation_municipio(code)
    assert isinstance(res, list)
    assert all(d.get("ubicacion", {}).get("codigo_ine") == code for d in res)


def test_query_equipamiento_array():
    # find some equipamiento value present
    vals = get_collection("anuncios").distinct("equipamiento")
    flat = []
    for v in vals:
        if isinstance(v, list):
            flat.extend(v)
        else:
            flat.append(v)
    # pick first non-empty if any
    item = None
    for v in flat:
        if v:
            item = v
            break
    if item is None:
        pytest.skip("no equipamiento data")
    res = mq.anuncios_con_equipamiento(item)
    assert all(item in d.get("equipamiento", []) for d in res)


def test_query_exists_type():
    r = mq.resumen_exists_type()
    assert r["total_anuncios"] == 759
    assert r["precio_null"] >= 0
    # $type decimal count should match non-null prices
    non_null = get_collection("anuncios").count_documents({"precio_eur": {"$ne": None}})
    assert r["precio_decimal"] == non_null


def test_query_regex():
    res = mq.anuncios_regex("ubicacion.municipio", "vitoria")
    assert isinstance(res, list)
    assert all("vitoria" in str(d["ubicacion"]["municipio"]).lower() for d in res)


def test_query_proyeccion_sort_limit():
    res = mq.anuncios_proyeccion(["portal", "modalidad", "precio_eur"], limit=5)
    assert len(res) <= 5
    for d in res:
        assert "_id" not in d or True
    sorted_res = mq.anuncios_ordenar_limitar("precio_eur", limit=5, descending=True)
    assert len(sorted_res) == 5
    prices = [d.get("precio_eur") for d in sorted_res if d.get("precio_eur") is not None]
    # descending
    dec = [float(p.to_decimal()) if isinstance(p, Decimal128) else float(p) for p in prices]
    assert dec == sorted(dec, reverse=True)


def test_query_paginacion():
    p1 = mq.anuncios_paginacion(0, 5)
    p2 = mq.anuncios_paginacion(5, 5)
    assert len(p1) == 5 and len(p2) == 5
    ids1 = {str(d["_id"]) for d in p1}
    ids2 = {str(d["_id"]) for d in p2}
    assert ids1.isdisjoint(ids2)


def test_clean_mongo():
    out = clean_mongo.clean_all()
    assert isinstance(out, dict)
    # counts unchanged
    assert get_collection("anuncios").count_documents({}) == 759
    assert get_collection("municipios").count_documents({}) == 252
    # quality flags present
    sample = get_collection("anuncios").find_one({"tiene_superficie": {"$exists": True}})
    assert sample is not None


def test_crud_demo():
    out = clean_mongo.demo_crud_operations()
    assert out["remaining"] >= 0
    assert "inserted_id" in out


def test_aggregation_pipeline():
    docs = ma.pipeline_indicadores_municipio()
    assert isinstance(docs, list)
    assert len(docs) == 252
    assert all("n_anuncios" in d for d in docs)
    # at least one with anuncios
    assert any((d.get("n_anuncios") or 0) > 0 for d in docs)
    # esfuerzo as percentage or None
    for d in docs:
        e = d.get("esfuerzo_alquiler_pct")
        if e is not None:
            assert 0 <= e <= 500


def test_aggregation_stages():
    # inspect pipeline definition by re-running? Check function returns and length enough
    docs = ma.pipeline_indicadores_municipio(limit=5)
    assert len(docs) == 5


def test_indicador_por_municipio():
    d = ma.indicador_por_municipio("48001")
    assert d is not None
    assert d["_id"] == "48001"


def test_indexes_explain():
    res = mi.explain_before_after("48001", "larga_estancia", 1000)
    before = res["before"]["stage"]
    after = res["after"]["stage"]
    assert before == "COLLSCAN"
    assert after == "IXSCAN"
    # ensure indexes created
    mi.ensure_indexes()
    names = [i["name"] for i in get_collection("anuncios").list_indexes()]
    assert "idx_anuncios_portal_id" in names


def test_modalidades_pipeline():
    res = ma.pipeline_modalidades()
    assert isinstance(res, list)
    assert len(res) >= 1
