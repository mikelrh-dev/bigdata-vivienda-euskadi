"""Consume announcement JSON events into the isolated MongoDB test database."""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv

from storage.kafka_anuncio_contract import DEFAULT_BOOTSTRAP, DEFAULT_GROUP, get_topic

load_dotenv()


def consume_events(
    max_messages: int | None = None,
    consumer=None,
    collection=None,
    idle_ms: int = 10_000,
) -> dict[str, int]:
    """Upsert events by stable event_id; commit the Kafka offset after Mongo write."""
    from kafka import KafkaConsumer, OffsetAndMetadata
    from kafka.structs import TopicPartition
    from pymongo import MongoClient

    own_consumer = consumer is None
    mongo_client = None
    if own_consumer:
        consumer = KafkaConsumer(
            get_topic(),
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS") or DEFAULT_BOOTSTRAP,
            group_id=os.getenv("KAFKA_EVENTS_GROUP") or DEFAULT_GROUP,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
        )
    if collection is None:
        uri = os.getenv("MONGO_URI", "").strip()
        if uri:
            mongo_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        else:
            mongo_client = MongoClient(
                os.getenv("MONGO_HOST", "localhost"),
                int(os.getenv("MONGO_PORT", "27017")),
                serverSelectionTimeoutMS=5000,
            )
        database = os.getenv("MONGO_TEST_DB", "vivienda_euskadi_test")
        collection = mongo_client[database]["anuncios_eventos"]

    stored = 0
    idle = 0
    try:
        while idle < idle_ms:
            batches = consumer.poll(timeout_ms=1000)
            if not batches:
                idle += 1000
                continue
            idle = 0
            for records in batches.values():
                for msg in records:
                    event = json.loads(msg.value.decode("utf-8"))
                    if event.get("type") != "anuncio_upsert":
                        raise ValueError("Tipo de evento Kafka desconocido")
                    event_id = event.get("event_id")
                    code = event.get("codigo_ine")
                    data = event.get("data")
                    if not event_id or not code or not isinstance(data, dict):
                        raise ValueError("Evento incompleto; offset no confirmado")
                    document = {**data, "_id": event_id, "codigo_ine": code}
                    collection.replace_one({"_id": event_id}, document, upsert=True)
                    consumer.commit({
                        TopicPartition(msg.topic, msg.partition):
                            OffsetAndMetadata(msg.offset + 1, "")
                    })
                    stored += 1
                    if max_messages is not None and stored >= max_messages:
                        return {"stored": stored}
        return {"stored": stored}
    finally:
        if own_consumer:
            consumer.close()
        if mongo_client is not None:
            mongo_client.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Consume anuncios_eventos y guarda en Mongo de test")
    parser.add_argument("--max-messages", type=int, default=None)
    parser.add_argument("--idle-ms", type=int, default=10_000)
    args = parser.parse_args()
    print(consume_events(max_messages=args.max_messages, idle_ms=args.idle_ms))
