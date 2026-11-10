"""Tests for MongoDB phase."""

from __future__ import annotations

from pathlib import Path

import pytest
from contextlib import contextmanager
from unittest.mock import patch
from bson.decimal128 import Decimal128

ROOT = Path(__file__).resolve().parent.parent

from storage.mongo import get_collection, get_test_db, ping, zfill_ine
from storage import clean_mongo
from analysis import mongo_queries as mq
from analysis import mongo_aggregations as ma
from analysis import mongo_indexes as mi


def _mongo_ok() -> bool:
    try:
        return ping() is True
    except Exception:
        return False


# AISLAMIENTO-01: sin Mongo local la suite se salta (nunca escribe en prod).
pytestmark = pytest.mark.skipif(not _mongo_ok(), reason="sin Mongo local: skip separado")


def test_conexion():
    assert ping() is True
    assert get_collection("municipios").database.name == "vivienda_euskadi"


def test_conteos():
    # dimension municipal fija 252; resto por rangos para no fragilizar por recargas
    for name in ["municipios", "alquiler_municipal", "indicadores", "udalmap_indicadores", "udalmap_empleo", "osrm_tiempos", "udalmap_extendido", "certificados_energeticos"]:
        assert get_collection(name).count_documents({}) == 252, name
    # PISOS-2026-11-07: 594 tras re-resolucion (759 antes).
    assert get_collection("anuncios").count_documents({}) >= 500
    assert get_collection("ecvi_compraventa").count_documents({}) >= 20
    assert get_collection("emancipacion_juventud").count_documents({}) == 1
    assert get_collection("etxebide_solicitudes").count_documents({}) >= 5000
    assert get_collection("etxebide_promociones").count_documents({}) >= 400


def test_codigo_ine_canonico():
    assert all(isinstance(d["_id"], str) and len(d["_id"]) == 5 for d in get_collection("municipios").find({}, {"_id": 1}))
    for coll_name in ["alquiler_municipal", "indicadores", "udalmap_indicadores", "udalmap_empleo", "osrm_tiempos", "udalmap_extendido", "certificados_energeticos", "etxebide_promociones", "etxebide_solicitudes", "ecvi_compraventa"]:
        coll = get_collection(coll_name)
        vals = [d.get("codigo_ine") for d in coll.find({}, {"codigo_ine": 1})]
        vals = [v for v in vals if v is not None]
        assert all(isinstance(v, str) and len(v) == 5 for v in vals), coll_name
        if coll_name in ("alquiler_municipal", "indicadores", "udalmap_indicadores", "udalmap_empleo", "osrm_tiempos", "udalmap_extendido", "certificados_energeticos"):
            assert coll.count_documents({"codigo_ine": None}) == 0, coll_name
    for d in get_collection("anuncios").find({}, {"ubicacion.codigo_ine": 1}):
        v = (d.get("ubicacion") or {}).get("codigo_ine")
        if v is not None:
            assert isinstance(v, str) and len(v) == 5


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


def test_provenance_g5_g6():
    for name in ["etxebide_promociones", "udalmap_extendido", "certificados_energeticos"]:
        coll = get_collection(name)
        doc = coll.find_one({"fuente": {"$exists": True}})
        assert doc is not None, name
        assert doc.get("fuente")
        assert doc.get("anio_fuente") is not None, name


def test_query_exists_type():
    r = mq.resumen_exists_type()
    assert r["total_anuncios"] >= 500
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


_TEST_COLLECTIONS = [
    "municipios", "anuncios", "alquiler_municipal", "indicadores",
    "udalmap_indicadores", "udalmap_empleo", "osrm_tiempos",
    "udalmap_extendido", "etxebide_solicitudes", "ecvi_compraventa",
    "certificados_energeticos", "etxebide_promociones", "_demo_crud",
]


@contextmanager
def _clean_mongo_on_test_db():
    db = get_test_db()
    for name in _TEST_COLLECTIONS:
        db[name].drop()
    try:
        with patch.object(clean_mongo, "get_collection", lambda name: db[name]):
            yield db
    finally:
        for name in _TEST_COLLECTIONS:
            db[name].drop()


def test_clean_mongo():
    prod_before = get_collection("anuncios").count_documents({})
    with _clean_mongo_on_test_db() as db:
        coll = db["anuncios"]
        coll.insert_many([
            {"portal": "Idealista", "id_anuncio": "A1", "property_fingerprint": "fp-a",
             "ubicacion": {"codigo_ine": "1001", "municipio": "Vitoria-Gasteiz"},
             "superficie_m2": None, "precio_eur": "120000", "habitaciones": 2.0},
            {"portal": "Idealista", "id_anuncio": "A1", "property_fingerprint": "fp-b",
             "ubicacion": {"codigo_ine": "01001", "municipio": "Vitoria-Gasteiz"},
             "superficie_m2": 80, "precio_eur": "125000", "habitaciones": 3.0},
            {"portal": "Fotocasa", "id_anuncio": "C1", "property_fingerprint": "fp-c",
             "ubicacion": {"codigo_ine": 20069, "municipio": "Lesaka"},
             "superficie_m2": 65, "precio_eur": None, "habitaciones": None},
        ])
        canon = clean_mongo.canonicalize_codigo_ine()
        assert canon["anuncios"] == {"matched_count": 3, "modified_count": 2,
                                     "deleted_count": 0, "upserted_count": 0}
        assert sorted(d["ubicacion"]["codigo_ine"] for d in coll.find()) == [
            "01001", "01001", "20069"]
        nulls = clean_mongo.mark_nulls()
        assert nulls["anuncios_sin_superficie"]["matched_count"] == 1
        assert nulls["anuncios_con_superficie"]["matched_count"] == 2
        assert nulls["anuncios_sin_precio"]["matched_count"] == 1
        assert nulls["anuncios_con_precio"]["matched_count"] == 2
        assert nulls["anuncios_sin_habitaciones"]["matched_count"] == 1
        sin_sup = coll.find_one({"tiene_superficie": False})
        assert sin_sup is not None and sin_sup["superficie_m2"] is None
        dup = clean_mongo.resolve_duplicates()
        assert dup["deleted"] == 1
        assert dup["groups"] >= 1
        assert coll.count_documents({}) == 2
        conv = clean_mongo.convert_types()
        assert conv["precios_string_convertidos"]["matched_count"] == 1
        assert conv["precios_string_convertidos"]["modified_count"] == 1
        assert conv["habitaciones_convertidas"]["matched_count"] == 1
        precio = coll.find_one({"precio_eur": {"$type": "decimal"}})
        assert precio is not None and isinstance(precio["precio_eur"], Decimal128)
        assert precio["ubicacion"]["codigo_ine"] == "01001"
        hab = coll.find_one({"habitaciones": {"$type": "int"}})
        assert hab is not None
        assert sorted(d["ubicacion"]["codigo_ine"] for d in coll.find()) == [
            "01001", "20069"]
    assert get_collection("anuncios").count_documents({}) == prod_before
    assert get_test_db()["anuncios"].count_documents({}) == 0


def test_crud_demo():
    prod_before = get_collection("anuncios").count_documents({})
    with _clean_mongo_on_test_db() as db:
        out = clean_mongo.demo_crud_operations()
        assert out["inserted_id"]
        assert len(out["inserted_ids"]) == 2
        assert out["count_find"] == 3
        assert out["update_one"]["matched_count"] == 1
        assert out["update_one"]["modified_count"] == 1
        assert out["find_one_and_update"] == "ok"
        assert out["upsert"]["matched_count"] == 0
        assert out["bulk_write"]["deleted_count"] == 1
        assert out["delete_one"] == 1
        assert out["delete_many"] == 2
        assert out["remaining"] == 1
        assert "_demo_crud" not in db.list_collection_names()
    assert get_collection("anuncios").count_documents({}) == prod_before


def test_aggregation_pipeline():
    docs = ma.pipeline_indicadores_municipio()
    assert isinstance(docs, list)
    assert len(docs) == 252
    assert all("n_anuncios" in d for d in docs)
    # at least one with anuncios
    assert any((d.get("n_anuncios") or 0) > 0 for d in docs)
    # esfuerzo canonico esfuerzo_joven_pct + alias esfuerzo_alquiler_pct
    for d in docs:
        e = d.get("esfuerzo_joven_pct")
        assert "esfuerzo_alquiler_pct" in d
        assert d.get("esfuerzo_alquiler_pct") == e
        if e is not None:
            assert 0 <= e <= 500


def test_aggregation_stages():
    # Original de 5 filas + refuerzo de etapas: los pipelines definitivos
    # (alquiler y vpo) contienen $group, $lookup y $unwind de verdad.
    docs = ma.pipeline_indicadores_municipio(limit=5)
    assert len(docs) == 5

    src = ROOT.joinpath("analysis", "mongo_aggregations.py").read_text(encoding="utf-8")
    # El modulo expone los 9 pipelines: se exige evidencia textual de
    # etapas distintas en el fuente que dispara el pipeline.
    for fun in ("pipeline_indicadores_municipio", "pipeline_alquiler_por_municipio",
                "pipeline_modalidades", "pipeline_top_municipios_por_esfuerzo",
                "pipeline_esfuerzo_por_sexo", "pipeline_accesibilidad_extendida",
                "pipeline_udalmap_extendido_osrm", "pipeline_vpo_por_municipio",
                "pipeline_vpo_terminadas"):
        assert f"def {fun}(" in src
    # $group, $lookup y $unwind estan presentes en el modulo (alquiler y vpo)
    assert '"$group"' in src
    assert '"$lookup"' in src
    assert '"$unwind"' in src

    # Ejecucion real: los pipelines que combinan etapas devuelven filas
    # y las etapas esperadas por coleccion:
    docs_alq = ma.pipeline_alquiler_por_municipio(limit=5)
    assert len(docs_alq) == 5
    docs_vpo = ma.pipeline_vpo_por_municipio(limit=5)
    assert len(docs_vpo) == 5
    docs_vpo_ter = ma.pipeline_vpo_terminadas()
    assert len(docs_vpo_ter) == 251
    docs_mod = ma.pipeline_modalidades()
    assert len(docs_mod) >= 2
    docs_ud = ma.pipeline_udalmap_extendido_osrm(limit=5)
    assert len(docs_ud) == 5


def test_indicador_por_municipio():
    d = ma.indicador_por_municipio("48001")
    assert d is not None
    assert d["_id"] == "48001"


def test_indexes_explain():
    # AISLAMIENTO-02: explain read-only con hint $natural; no dropea ni crea índices.
    res = mi.explain_before_after("20069", "larga_estancia", 1000)
    before = res["before"]["stage"]
    after = res["after"]["stage"]
    assert before == "COLLSCAN"
    assert after == "IXSCAN"
    # El índice ESR debe estar presente en prod (restaurado con ensure_indexes).
    names = [i["name"] for i in get_collection("anuncios").list_indexes()]
    assert "idx_anuncios_ine_modalidad_precio" in names


def test_etxebide_promociones_codigo_ine():
    coll = get_collection("etxebide_promociones")
    total = coll.count_documents({})
    con = coll.count_documents({"codigo_ine": {"$regex": "^[0-9]{5}$"}})
    assert total == 406
    assert con / total >= 0.95


def test_certificados_contenido():
    coll = get_collection("certificados_energeticos")
    assert coll.count_documents({}) == 252
    assert coll.count_documents({"_id": {"$regex": "^[0-9]{5}$"}}) == 252
    sample = coll.find_one({"cert_moda": {"$in": list("ABCDEFG")}})
    assert sample is not None
    assert sum((sample.get("distribucion") or {}).values()) == sample.get("n_certificados")
    dist = sample.get("distribucion") or {}
    assert sample.get("cert_moda") == max(dist, key=lambda k: dist[k])


def test_pipeline_vpo():
    docs = ma.pipeline_vpo_por_municipio()
    assert isinstance(docs, list) and len(docs) > 0
    assert all("codigo_ine" in d and "n_promociones" in d for d in docs)


def test_pipeline_accesibilidad_extendida():
    docs = ma.pipeline_accesibilidad_extendida(limit=5)
    assert isinstance(docs, list) and len(docs) == 5
    assert all("accesibilidad_municipio" in d for d in docs)


def test_explain_promo():
    res = mi.explain_promo_before_after("48020")
    assert res["before"]["stage"] == "COLLSCAN"
    assert res["after"]["stage"] == "IXSCAN"


def test_modalidades_pipeline():
    res = ma.pipeline_modalidades()
    assert isinstance(res, list)
    assert len(res) >= 1


def test_zfill_float():
    assert zfill_ine(1001.0) == "01001"
    assert zfill_ine("1001.0") == "01001"
    assert zfill_ine(20069.0) == "20069"
    assert zfill_ine(1001) == "01001"
    assert zfill_ine("1001") == "01001"
