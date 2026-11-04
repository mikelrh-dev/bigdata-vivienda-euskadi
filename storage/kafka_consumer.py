"""Consumidor Kafka de anuncios unificados (KAFKA-01).

Consume el topic anuncios_inmobiliarios en el grupo anuncios con
auto-commit desactivado, inserta cada mensaje en la colección anuncios
de vivienda_euskadi mediante upsert por portal e id_anuncio (sin
duplicar en reintento) y reporta cuántos ha procesado.
"""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv

from storage.mongo import get_collection

load_dotenv()

DEFAULT_BOOTSTRAP_SERVERS = "192.168.201.162:9094"
DEFAULT_TOPIC = "anuncios_inmobiliarios"
DEFAULT_GROUP_ID = "anuncios"


def get_bootstrap_servers() -> str:
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS") or DEFAULT_BOOTSTRAP_SERVERS


def get_topic() -> str:
    return os.getenv("KAFKA_TOPIC") or DEFAULT_TOPIC


def decode_message(value: bytes) -> dict[str, Any]:
    """Decodifica el valor de un mensaje Kafka (JSON utf-8) a dict."""
    return json.loads(value.decode("utf-8"))


def upsert_anuncio(collection: Any, anuncio: dict[str, Any]) -> bool:
    """Inserta o actualiza un anuncio por portal e id_anuncio.

    Devuelve True si el mensaje es válido y se ha aplicado el upsert.
    Un reintento del mismo (portal, id_anuncio) actualiza el documento
    existente en lugar de duplicarlo.
    """
    portal = anuncio.get("portal")
    id_anuncio = anuncio.get("id_anuncio")
    if portal is None or id_anuncio is None:
        print(f"Mensaje sin portal/id_anuncio, se descarta: {anuncio!r}")
        return False
    collection.update_one(
        {"portal": portal, "id_anuncio": id_anuncio},
        {"$set": dict(anuncio)},
        upsert=True,
    )
    return True


def process_value(collection: Any, value: bytes) -> bool:
    """Decodifica un valor Kafka y lo aplica con upsert idempotente."""
    try:
        anuncio = decode_message(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"Mensaje no JSON, se descarta: {exc}")
        return False
    return upsert_anuncio(collection, anuncio)


def consume(
    topic: str | None = None,
    bootstrap_servers: str | None = None,
    group_id: str = DEFAULT_GROUP_ID,
    collection: Any | None = None,
    max_messages: int | None = None,
) -> int:
    """Consume anuncios, hace upsert en Mongo y devuelve procesados.

    Con enable_auto_commit=False el commit es manual tras cada upsert
    correcto, de modo que un fallo no marca como consumido el mensaje.
    """
    from kafka import KafkaConsumer

    coll = collection if collection is not None else get_collection("anuncios")
    consumer = KafkaConsumer(
        topic or get_topic(),
        bootstrap_servers=bootstrap_servers or get_bootstrap_servers(),
        group_id=group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )
    procesados = 0
    try:
        for message in consumer:
            if process_value(coll, message.value):
                procesados += 1
                consumer.commit()
            if max_messages is not None and procesados >= max_messages:
                break
    except KeyboardInterrupt:
        print("Consumo interrumpido por el usuario")
    finally:
        consumer.close()
    print(f"Procesados: {procesados}")
    return procesados


if __name__ == "__main__":
    consume()
