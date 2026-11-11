"""Publish announcement JSON events from the silver CSV to Kafka."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from storage.kafka_anuncio_contract import (
    DEFAULT_BOOTSTRAP,
    DEFAULT_SOURCE,
    event_from_row,
    get_topic,
)

load_dotenv()

def produce_events(
    source: Path | str = DEFAULT_SOURCE,
    limit: int | None = None,
    producer=None,
    admin=None,
    topic: str | None = None,
) -> int:
    if limit is not None and limit <= 0:
        return 0
    rows: list[dict[str, str]] = []
    with Path(source).open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            rows.append(row)
            if limit is not None and len(rows) >= limit:
                break

    selected_topic = topic or get_topic()
    own = producer is None
    if own:
        from storage.kafka_topic import ensure_topic

        ensure_topic(
            topic=selected_topic,
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS") or DEFAULT_BOOTSTRAP,
            admin=admin,
        )
        from kafka import KafkaProducer

        producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS") or DEFAULT_BOOTSTRAP
        )
    try:
        for row in rows:
            event = event_from_row(row)
            future = producer.send(
                selected_topic,
                key=event["event_id"].encode("utf-8"),
                value=json.dumps(event, ensure_ascii=False).encode("utf-8"),
            )
            if hasattr(future, "get"):
                future.get(timeout=30)
        producer.flush()
    finally:
        if own:
            producer.close()
    return len(rows)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Publica eventos JSON de anuncios en Kafka")
    parser.add_argument("--limit", type=int, default=10, help="Número máximo de anuncios (defecto: 10)")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    args = parser.parse_args()
    count = produce_events(source=args.source, limit=args.limit)
    print(f"eventos_publicados={count} topic={get_topic()}")
