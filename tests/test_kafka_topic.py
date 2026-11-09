"""Tests offline de storage/kafka_topic.py (sin red ni broker).

Se inyecta FakeAdmin en ensure_topic() para verificar particiones,
replicacion, nombre vivienda_euskadi y que TopicAlreadyExistsError
se trate como ya existe.
"""

from __future__ import annotations

import pytest
from kafka.errors import TopicAlreadyExistsError

from storage.kafka_topic import (
    DEFAULT_BOOTSTRAP_SERVERS,
    DEFAULT_NUM_PARTITIONS,
    DEFAULT_REPLICATION_FACTOR,
    DEFAULT_TOPIC,
    ensure_topic,
    get_bootstrap_servers,
    get_num_partitions,
    get_replication_factor,
    get_topic,
)


class FakeAdmin:
    def __init__(self, raise_exists: bool = False) -> None:
        self.created: list = []
        self.closed = False
        self.raise_exists = raise_exists

    def create_topics(self, configs):
        self.created.extend(configs)
        if self.raise_exists:
            raise TopicAlreadyExistsError("ya existe")

    def close(self) -> None:
        self.closed = True


def test_defaults_nuevo_topic_centro(monkeypatch) -> None:
    for var in (
        "KAFKA_BOOTSTRAP_SERVERS",
        "KAFKA_TOPIC",
        "KAFKA_NUM_PARTITIONS",
        "KAFKA_REPLICATION_FACTOR",
    ):
        monkeypatch.delenv(var, raising=False)
    assert DEFAULT_TOPIC == "vivienda_euskadi"
    assert DEFAULT_BOOTSTRAP_SERVERS == "10.22.87.215:9092"
    assert DEFAULT_NUM_PARTITIONS == 1
    assert DEFAULT_REPLICATION_FACTOR == 1
    assert get_topic() == "vivienda_euskadi"
    assert get_bootstrap_servers() == "10.22.87.215:9092"
    assert get_num_partitions() == 1
    assert get_replication_factor() == 1


def test_getters_leen_entorno(monkeypatch) -> None:
    monkeypatch.setenv("KAFKA_TOPIC", "otro_topic")
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "broker.test:9092")
    monkeypatch.setenv("KAFKA_NUM_PARTITIONS", "3")
    monkeypatch.setenv("KAFKA_REPLICATION_FACTOR", "2")
    assert get_topic() == "otro_topic"
    assert get_bootstrap_servers() == "broker.test:9092"
    assert get_num_partitions() == 3
    assert get_replication_factor() == 2


def test_ensure_crea_con_1_particion_rf1_capy() -> None:
    fake = FakeAdmin()
    res = ensure_topic(admin=fake, topic="vivienda_euskadi")

    assert res == "vivienda_euskadi"
    assert len(fake.created) == 1
    topic = fake.created[0]
    assert topic.name == "vivienda_euskadi"
    assert topic.num_partitions == 1
    assert topic.replication_factor == 1
    assert fake.closed is False


def test_ensure_ya_existe_no_falla() -> None:
    fake = FakeAdmin(raise_exists=True)
    res = ensure_topic(admin=fake, topic="vivienda_euskadi")
    assert res == "vivienda_euskadi"
    assert len(fake.created) == 1
    assert fake.closed is False


def test_ensure_respeta_topic_y_bootstrap_inyectados() -> None:
    fake = FakeAdmin()
    res = ensure_topic(
        topic="otro_topic",
        bootstrap_servers="broker.test:9092",
        admin=fake,
        num_partitions=3,
        replication_factor=2,
    )
    assert res == "otro_topic"
    assert fake.created[0].name == "otro_topic"
    assert fake.created[0].num_partitions == 3
    assert fake.created[0].replication_factor == 2
    assert fake.closed is False


def test_ensure_cierra_admin_propio(monkeypatch) -> None:
    instantes = []

    class Factory:
        def create_topics(self, configs):
            instantes.extend(configs)

        def close(self):
            pass

    monkeypatch.setattr("kafka.admin.KafkaAdminClient", lambda **kwargs: Factory())
    res = ensure_topic(topic="vivienda_euskadi")
    assert res == "vivienda_euskadi"
    assert instantes[0].name == "vivienda_euskadi"
