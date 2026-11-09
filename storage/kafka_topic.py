"""Creacion idempotente del topic Kafka del centro (sin red en tests).

El topic vigente es vivienda_euskadi en 10.22.87.215:9092 con 1 particion
y RF 1. La creacion se hace desde el productor via ensure_topic(), que
captura TopicAlreadyExistsError como ya existe para que sea seguro
re-ejecutarla. Los tests inyectan FakeAdmin, sin red.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_BOOTSTRAP_SERVERS = "10.22.87.215:9092"
DEFAULT_TOPIC = "vivienda_euskadi"
DEFAULT_NUM_PARTITIONS = 1
DEFAULT_REPLICATION_FACTOR = 1


def get_bootstrap_servers() -> str:
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS") or DEFAULT_BOOTSTRAP_SERVERS


def get_topic() -> str:
    return os.getenv("KAFKA_TOPIC") or DEFAULT_TOPIC


def get_num_partitions() -> int:
    return int(os.getenv("KAFKA_NUM_PARTITIONS") or DEFAULT_NUM_PARTITIONS)


def get_replication_factor() -> int:
    return int(os.getenv("KAFKA_REPLICATION_FACTOR") or DEFAULT_REPLICATION_FACTOR)


def ensure_topic(
    topic: str | None = None,
    bootstrap_servers: str | None = None,
    admin=None,
    num_partitions: int | None = None,
    replication_factor: int | None = None,
) -> str:
    """Asegura que el topic exista. Idempotente y sin red si se inyecta admin."""
    from kafka.admin import KafkaAdminClient, NewTopic
    from kafka.errors import TopicAlreadyExistsError

    resolved_topic = topic or get_topic()
    resolved_bootstrap = bootstrap_servers or get_bootstrap_servers()
    partitions = num_partitions if num_partitions is not None else get_num_partitions()
    rf = replication_factor if replication_factor is not None else get_replication_factor()

    own = admin is None
    if own:
        admin = KafkaAdminClient(bootstrap_servers=resolved_bootstrap)
    try:
        admin.create_topics(
            [
                NewTopic(
                    name=resolved_topic,
                    num_partitions=partitions,
                    replication_factor=rf,
                )
            ]
        )
    except TopicAlreadyExistsError:
        pass
    finally:
        if own:
            admin.close()
    print(f"TOPIC_ENSURADO {resolved_topic}")
    return resolved_topic


if __name__ == "__main__":
    ensure_topic()
