"""Tests de productor/consumidor Kafka (KAFKA-01).

Sin Kafka real: el productor se prueba con un double que registra
send/flush y el consumidor con upsert real en la base de test
vivienda_euskadi_test (colección anuncios). La serialización JSON se
comprueba en bytes con precio y municipio, y la subida es idempotente.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from storage.kafka_consumer import decode_message, process_value, upsert_anuncio
from storage.kafka_producer import (
    DEFAULT_BOOTSTRAP_SERVERS,
    DEFAULT_TOPIC,
    build_message,
    produce,
)
from storage.mongo import get_test_db, ping

FILA_EJEMPLO = {
    "id_anuncio": "131393829",
    "portal": "fotocasa",
    "modalidad": "larga_estancia",
    "precio_eur": "1850.0",
    "superficie_m2": "140.0",
    "habitaciones": "",
    "codigo_ine": "01059",
    "municipio": "Vitoria-Gasteiz",
}


def test_serializacion_json_con_precio_y_municipio():
    assert DEFAULT_BOOTSTRAP_SERVERS == "192.168.201.162:9094"
    assert DEFAULT_TOPIC == "anuncios_inmobiliarios"
    key, value = build_message(FILA_EJEMPLO)
    assert isinstance(key, bytes)
    assert isinstance(value, bytes)
    assert key == b"fotocasa:131393829"
    payload = json.loads(value.decode("utf-8"))
    assert payload["portal"] == "fotocasa"
    assert payload["id_anuncio"] == "131393829"
    assert payload["precio_eur"] == 1850.0
    assert payload["municipio"] == "Vitoria-Gasteiz"


def test_producer_publica_759_con_flush_y_callback():
    fake = MagicMock()
    n = produce(producer=fake)
    assert n == 759
    assert fake.send.call_count == 759
    fake.flush.assert_called_once()
    topic, kwargs = fake.send.call_args_list[0].args[0], fake.send.call_args_list[0].kwargs
    assert topic == "anuncios_inmobiliarios"
    assert kwargs["key"] == b"fotocasa:131393829"
    assert isinstance(kwargs["value"], bytes)
    assert "callback" in kwargs
    payload = json.loads(kwargs["value"].decode("utf-8"))
    assert "precio_eur" in payload
    assert payload["municipio"] == "Vitoria-Gasteiz"


def test_upsert_idempotente_en_base_test():
    assert ping() is True
    coll = get_test_db()["anuncios"]
    coll.delete_many({"portal": "kafka-test"})
    try:
        primero = {
            "portal": "kafka-test",
            "id_anuncio": "999001",
            "precio_eur": 1000.0,
            "municipio": "Bilbao",
        }
        segundo = dict(primero, precio_eur=1200.0)
        assert upsert_anuncio(coll, primero) is True
        assert upsert_anuncio(coll, segundo) is True
        assert coll.count_documents({"portal": "kafka-test", "id_anuncio": "999001"}) == 1
        doc = coll.find_one({"portal": "kafka-test", "id_anuncio": "999001"})
        assert doc is not None
        assert doc["precio_eur"] == 1200.0
        assert doc["municipio"] == "Bilbao"
        # Ida y vuelta: mensaje del productor -> decode -> upsert sin duplicar.
        fila = dict(FILA_EJEMPLO, portal="kafka-test", id_anuncio="999002")
        _key, value = build_message(fila)
        assert decode_message(value)["municipio"] == "Vitoria-Gasteiz"
        assert process_value(coll, value) is True
        assert process_value(coll, value) is True
        assert coll.count_documents({"portal": "kafka-test", "id_anuncio": "999002"}) == 1
    finally:
        coll.delete_many({"portal": "kafka-test"})
