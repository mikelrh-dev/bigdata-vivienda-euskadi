"""Tests PyMongo profesional: MONGO_URI configurable y ObjectId (PYMONGO-PRO-01).

Respaldo Tema 8 §12: MongoClient reutilizable con URI configurable
(fallback a MONGO_HOST/MONGO_PORT) y validación ObjectId.
"""

from __future__ import annotations

from unittest.mock import patch

from bson import ObjectId

from storage import mongo
from storage.mongo import get_collection, is_objectid, ping, to_objectid


def test_mongo_uri_configurable(monkeypatch):
    fake_uri = "mongodb://fake-host:27099/vivienda_euskadi"
    monkeypatch.setenv("MONGO_URI", fake_uri)
    mongo.get_client.cache_clear()
    try:
        assert mongo.get_mongo_uri() == fake_uri
        with patch("storage.mongo.MongoClient") as mock_client:
            mongo.get_client()
            mock_client.assert_called_once()
            args, kwargs = mock_client.call_args
            assert fake_uri in args or kwargs.get("host") == fake_uri
            assert kwargs.get("serverSelectionTimeoutMS") == 5000
    finally:
        mongo.get_client.cache_clear()
    # Fallback sin MONGO_URI: usa host/port
    monkeypatch.delenv("MONGO_URI", raising=False)
    mongo.get_client.cache_clear()
    try:
        assert mongo.get_mongo_uri() is None
        with patch("storage.mongo.MongoClient") as mock_client:
            mongo.get_client()
            mock_client.assert_called_once()
            args, _kwargs = mock_client.call_args
            assert mongo.MONGO_HOST in args
            assert mongo.MONGO_PORT in args
    finally:
        mongo.get_client.cache_clear()


def test_anuncios_objectid():
    assert ping() is True
    coll = get_collection("anuncios")
    doc = coll.find_one()
    assert doc is not None
    assert isinstance(doc.get("_id"), ObjectId)
    assert is_objectid(doc.get("_id")) is True
    assert is_objectid(str(doc.get("_id"))) is True
    assert to_objectid(str(doc.get("_id"))) == doc.get("_id")
    assert is_objectid("no-es-objectid") is False
    assert is_objectid(None) is False
    # Muestra en vivo: todo anuncio tiene _id ObjectId
    for d in coll.find({}, {"_id": 1}).limit(5):
        assert isinstance(d.get("_id"), ObjectId)

    # Bloque 3, LIMPIEZA-01 + PYMONGO-01: función canónica $unset con
    # matched/modified/deleted en test DB (mismo contrato en ambas
    # colecciones) y _money/_to_decimal tipados (None con log, sin propagar).
    import logging as _logging

    from storage.clean_mongo import _to_decimal, clean_obsolete_fields
    from storage.load_mongo import _money
    from storage.mongo import get_test_db as _get_test_db

    _db = _get_test_db()
    for _n in ("_probe_clean", "_probe_mun"):
        _db[_n].drop()
    try:
        _db["_probe_clean"].insert_many(
            [{"_id": 1, "campo_obsoleto": "x", "keep": 1}, {"_id": 2, "keep": 2}]
        )
        _out = clean_obsolete_fields(
            "_probe_clean", fields=["campo_obsoleto"], collection=_db["_probe_clean"]
        )
        assert _out["matched_count"] == 2
        assert _out["modified_count"] == 1
        assert _out["deleted_count"] == 0
        assert _db["_probe_clean"].find_one({"_id": 1}) == {"_id": 1, "keep": 1}
        _db["_probe_mun"].insert_one({"_id": "48001", "campo_obsoleto": "y"})
        _out2 = clean_obsolete_fields(
            "_probe_mun", fields=["campo_obsoleto"], collection=_db["_probe_mun"]
        )
        assert set(_out2) == set(_out)
        assert _out2["deleted_count"] == 0
        # Excepciones tipadas no propagan DuplicateKeyError y devuelven None con log.
        assert _money(None) is None
        assert _money("abc") is None
        assert _to_decimal("abc") is None
        assert _to_decimal(None) is None
        # CRUD con contadores en test DB (demo_crud_operations ya los verifica
        # en test_mongo.py; aquí se acota un insert/update/delete mínimo).
        _db["_probe_crud"].drop()
        _r = _db["_probe_crud"].insert_one({"_id": 1, "v": 10})
        assert _r.inserted_id == 1
        _r = _db["_probe_crud"].update_one({"_id": 1}, {"$set": {"v": 11}})
        assert (_r.matched_count, _r.modified_count) == (1, 1)
        _r = _db["_probe_crud"].delete_one({"_id": 1})
        assert _r.deleted_count == 1
    finally:
        for _n in ("_probe_clean", "_probe_mun", "_probe_crud"):
            _db[_n].drop()
    # Prod sigue en 759 tras limpieza canónica (solo test DB).
    assert get_collection("anuncios").count_documents({}) == 759
