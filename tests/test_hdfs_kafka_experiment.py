"""Offline coverage for direct-HDFS and JSON-event experimental flow."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from storage.hdfs_raw_direct import iter_files, upload_raw
from storage.kafka_anuncio_consumer import consume_events
from storage.kafka_anuncio_contract import event_from_row
from storage.kafka_anuncio_producer import produce_events


class FakeHDFS:
    def __init__(self):
        self.dirs = []
        self.uploads = []

    def makedirs(self, path):
        self.dirs.append(path)

    def upload(self, hdfs_path, local_path, overwrite=False):
        self.uploads.append((hdfs_path, Path(local_path).read_bytes(), overwrite))


class FakeProducer:
    def __init__(self):
        self.sent = []
        self.flushed = False

    def send(self, topic, key=None, value=None):
        self.sent.append((topic, key, json.loads(value)))
        return SimpleNamespace(get=lambda timeout=None: None)

    def flush(self):
        self.flushed = True


class FakeCollection:
    def __init__(self):
        self.documents = {}

    def replace_one(self, query, document, upsert=False):
        assert upsert is True
        self.documents[query["_id"]] = document


class FakeConsumer:
    def __init__(self, messages):
        self.messages = list(messages)
        self.commits = []
        self.closed = False

    def poll(self, timeout_ms=1000):
        if self.messages:
            msg = self.messages.pop(0)
            return {0: [msg]}
        return {}

    def commit(self, offsets):
        self.commits.append(offsets)


def test_direct_hdfs_uploads_without_kafka(tmp_path):
    root = tmp_path / "raw"
    (root / "nested").mkdir(parents=True)
    (root / "nested" / "ok.csv").write_bytes(b"raw-data")
    (root / "legacy_obsoleto_no_usar").mkdir()
    (root / "legacy_obsoleto_no_usar" / "old.csv").write_bytes(b"old")
    client = FakeHDFS()

    assert [p.name for p in iter_files(root)] == ["ok.csv"]
    assert upload_raw(root, "/raw", client=client) == {"uploaded": 1}
    assert client.uploads == [("/raw/nested/ok.csv", b"raw-data", True)]


def test_event_shape_requires_relationship_key():
    event = event_from_row({"portal": "portal-a", "id_anuncio": "123", "codigo_ine": "1059"})
    assert event["type"] == "anuncio_upsert"
    assert event["event_id"] == "portal-a:123"
    assert event["codigo_ine"] == "01059"
    with pytest.raises(ValueError):
        event_from_row({"portal": "portal-a", "id_anuncio": "123"})


def test_producer_emits_json_events_to_dedicated_topic(tmp_path):
    source = tmp_path / "anuncios.csv"
    source.write_text(
        "portal,id_anuncio,codigo_ine\nportal-a,123,1059\nportal-b,456,48020\n",
        encoding="utf-8",
    )
    producer = FakeProducer()
    assert produce_events(source, limit=1, producer=producer, topic="test-events") == 1
    assert producer.flushed
    topic, key, event = producer.sent[0]
    assert topic == "test-events"
    assert key == b"portal-a:123"
    assert event["codigo_ine"] == "01059"


def test_consumer_upserts_and_commits_after_write():
    payload = {
        "type": "anuncio_upsert", "event_id": "portal-a:123",
        "codigo_ine": "01059", "data": {"portal": "portal-a", "codigo_ine": "1059"},
    }
    msg = SimpleNamespace(topic="anuncios_eventos", partition=0, offset=7,
                          value=json.dumps(payload).encode())
    consumer = FakeConsumer([msg])
    collection = FakeCollection()
    assert consume_events(max_messages=1, consumer=consumer, collection=collection) == {"stored": 1}
    assert collection.documents["portal-a:123"]["codigo_ine"] == "01059"
    assert len(consumer.commits) == 1
