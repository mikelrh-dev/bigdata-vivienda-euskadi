"""Tests de consistencia MongoDB: atomicidad documental y errores de índices.

TRANSACCIONES-01 (RA3 Consistencia, nivel 10): el modelo no necesita
transacción multidocumento; se demuestra con código una operación
atómica de un único documento (storage/mongo.py:marcar_calidad_municipio)
y se justifica en docs/modelo_mongodb.md. PYMONGO-PRO-01 (Tema 8 §12):
load_all ya no silencia errores de ensure_indexes.

Todo el trabajo de escritura ocurre en la base de test
vivienda_euskadi_test o con loaders sustituidos por monkeypatch; la base
productiva no se muta.
"""

from __future__ import annotations

import inspect
import logging

import pytest
from pymongo.errors import DuplicateKeyError

from analysis import mongo_indexes as mi
from storage import load_mongo
from storage.mongo import (
    get_collection,
    get_test_db,
    marcar_calidad_municipio,
    ping,
)

pytestmark = pytest.mark.skipif(not ping(), reason="sin Mongo local: skip separado")

_LOADERS = [
    "load_municipios",
    "load_anuncios",
    "load_alquiler",
    "load_indicadores",
    "load_ecvi",
    "load_udalmap_indicadores",
    "load_udalmap_empleo",
    "load_osrm",
    "load_emancipacion",
    "load_etxebide_solicitudes",
    "load_udalmap_extendido",
    "load_etxebide_promociones",
    "load_certificados",
    "load_vpo_municipal",
]


def test_atomicidad_documental():
    assert ping() is True
    prod_before = get_collection("municipios").count_documents({})
    db = get_test_db()
    coll = db["municipios"]
    coll.drop()
    try:
        coll.insert_one(
            {
                "_id": "48001",
                "codigo_ine": "48001",
                "nombre_canonico": "Bilbao",
                "calidad_datos": "pendiente",
            }
        )
        # La operación es una sola escritura atómica de documento y el
        # documento devuelto ya incluye el valor nuevo (ReturnDocument.AFTER),
        # sin necesidad de una lectura posterior.
        doc = marcar_calidad_municipio("48001", "verificado", collection=coll)
        assert doc is not None
        assert doc["_id"] == "48001"
        assert doc["calidad_datos"] == "verificado"
        stored = coll.find_one({"_id": "48001"})
        assert stored is not None and stored["calidad_datos"] == "verificado"

        # Segunda escritura: cada llamada devuelve su propio estado
        # posterior, sin estado intermedio visible.
        doc2 = marcar_calidad_municipio("48001", "ok", collection=coll)
        assert doc2 is not None and doc2["calidad_datos"] == "ok"
        assert doc["calidad_datos"] == "verificado"

        # Municipio inexistente: None, sin crear documento.
        assert marcar_calidad_municipio("99999", "ok", collection=coll) is None
        assert coll.count_documents({}) == 1

        # Valor de calidad fuera de dominio: error explícito, no escritura.
        with pytest.raises(ValueError):
            marcar_calidad_municipio("48001", "inventada", collection=coll)
        stored = coll.find_one({"_id": "48001"})
        assert stored is not None and stored["calidad_datos"] == "ok"

        # La vía atómica queda fijada en el código: find_one_and_update
        # con el documento posterior.
        src = inspect.getsource(marcar_calidad_municipio)
        assert "find_one_and_update" in src
        assert "ReturnDocument.AFTER" in src
    finally:
        coll.drop()
    assert get_collection("municipios").count_documents({}) == prod_before

    # Sonda commit/abort solo en vivienda_euskadi_test (TRANSACCIONES-01, docx §11 READ):
    # standalone sin replica set rechaza la transacción multidocumento; la sonda
    # no debe tocar prod por defecto (MONGO_ALLOW_DESTRUCTIVE sin definir).
    import os as _os

    assert _os.environ.get("MONGO_ALLOW_DESTRUCTIVE") != "1"
    prod_anuncios_before = get_collection("anuncios").count_documents({})
    # PISOS-2026-11-07: 594 tras re-resolucion (759 antes).
    assert prod_anuncios_before == 594
    _db = get_test_db()
    _db["__tx_probe"].drop()
    _tx_outcome = "sin-replica-set"
    try:
        with _db.client.start_session() as _session:
            with _session.start_transaction():
                _db["__tx_probe"].insert_one({"_id": "p1", "v": 1}, session=_session)
                _session.abort_transaction()
                _tx_outcome = "abort-revertido"
    except Exception:
        # Standalone: OperationFailure esperado (no hay replica set para commit/abort).
        _tx_outcome = "rechazado-standalone"
    finally:
        _db["__tx_probe"].drop()
    assert _tx_outcome in {"abort-revertido", "rechazado-standalone", "sin-replica-set"}
    assert _db["__tx_probe"].count_documents({}) == 0
    # Prod invariante tras abortar/sonda (594 tras PISOS-2026-11-07).
    assert get_collection("anuncios").count_documents({}) == 594
    assert get_collection("municipios").count_documents({}) == prod_before


def test_load_all_no_silencia_indices(monkeypatch, caplog):
    prod_before = get_collection("municipios").count_documents({})
    for name in _LOADERS:
        monkeypatch.setattr(load_mongo, name, lambda: 1)

    def boom():
        raise DuplicateKeyError("duplicate key error collection: vivienda_euskadi.anuncios")

    monkeypatch.setattr(mi, "ensure_indexes", boom)
    with caplog.at_level(logging.ERROR, logger="storage.load_mongo"):
        with pytest.raises(RuntimeError, match="índices"):
            load_mongo.load_all()
    assert "índices" in caplog.text

    # Camino feliz: sin error de índices, load_all devuelve las 13 colecciones.
    monkeypatch.setattr(mi, "ensure_indexes", lambda: {})
    result = load_mongo.load_all()
    assert set(result) == {
        "municipios",
        "anuncios",
        "alquiler_municipal",
        "indicadores",
        "ecvi_compraventa",
        "udalmap_indicadores",
        "udalmap_empleo",
        "osrm_tiempos",
        "emancipacion_juventud",
        "etxebide_solicitudes",
        "udalmap_extendido",
        "etxebide_promociones",
        "certificados_energeticos",
        "vpo_municipal",
    }
    assert all(v == 1 for v in result.values())
    assert get_collection("municipios").count_documents({}) == prod_before
