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
