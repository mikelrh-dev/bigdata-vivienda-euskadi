"""Bordes Kafka con fakes (storage/kafka_hdfs_uploader.py, kafka_raw_producer.py).

- consume con SHA mismatch aborta con SystemExit y no commitea;
- JSON corrupto se descarta (skipped, commiteado, sin subir);
- produce con un Future que nunca invoca errback/callback no bloquea:
  retorna el conteo y hace flush;
- poll vacio hasta idle_ms termina con uploaded=0.
Sin red: KafkaConsumer/KafkaProducer/InsecureClient sustituidos.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storage.kafka_hdfs_uploader import DEFAULT_DEST, DEFAULT_TOPIC  # noqa: E402
from storage.kafka_raw_producer import produce  # noqa: E402


# --- fakes (mismo contrato que test_kafka_pipeline.py) --------------------

class FakeHDFS:
    def __init__(self) -> None:
        self.writes: list[tuple] = []
        self.dirs: list[str] = []

    def makedirs(self, path, **kwargs):  # noqa: ANN001
        self.dirs.append(path)

    def write(self, path, data=None, overwrite=False, **kwargs):  # noqa: ANN001
        self.writes.append((path, data, overwrite))


class FakeConsumer:
    def __init__(self, batches=None) -> None:
        self.batches = list(batches or [])
        self.commits: list = []
        self.closed = False

    def poll(self, timeout_ms=1000, **kwargs):  # noqa: ANN001
        return self.batches.pop(0) if self.batches else {}

    def commit(self, offsets):  # noqa: ANN001
        self.commits.append(offsets)

    def close(self) -> None:
        self.closed = True


class LazyFuture:
    """Future que nunca invoca callbacks: produce no debe bloquearse esperandolo."""

    def __init__(self) -> None:
        self.callbacks: list = []
        self.errbacks: list = []

    def add_callback(self, fn):  # noqa: ANN001
        self.callbacks.append(fn)
        return self

    def add_errback(self, fn):  # noqa: ANN001
        self.errbacks.append(fn)
        return self


class FakeProducerLazy:
    def __init__(self) -> None:
        self.sent: list[dict] = []
        self.flushed = False
        self.closed = False

    def send(self, topic, key=None, value=None):  # noqa: ANN001
        self.sent.append({"topic": topic, "key": key, "value": value})
        return LazyFuture()

    def flush(self) -> None:
        self.flushed = True

    def close(self) -> None:
        self.closed = True


def _msg(payload, offset=0, partition=0, raw=None):  # noqa: ANN001
    value = raw if raw is not None else json.dumps(payload).encode("utf-8")
    return SimpleNamespace(topic=DEFAULT_TOPIC, partition=partition,
                           offset=offset, value=value)


def _raw(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "a.csv").write_bytes(b"x,y\n1,2\n")
    return raw


def _payload(raw: Path, rel="a.csv") -> dict:
    data = (raw / rel).read_bytes()
    return {"type": "raw_manifest", "rel": rel, "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def _instalar(monkeypatch, cliente, consumidor):  # noqa: ANN001
    monkeypatch.setattr("hdfs.InsecureClient", lambda *a, **k: cliente)
    monkeypatch.setattr("kafka.KafkaConsumer", lambda *a, **k: consumidor)


def test_consume_sha_mismatch_aborta_systemexit(monkeypatch, tmp_path):
    """kafka_hdfs_uploader: SHA/size que no cuadra -> SystemExit, sin commit ni subida."""
    from storage.kafka_hdfs_uploader import consume

    raw = _raw(tmp_path)
    roto = {**_payload(raw), "sha256": "0" * 64}
    cliente, consumidor = FakeHDFS(), FakeConsumer(
        batches=[{"p0": [_msg(roto, offset=3)]}, {}])
    _instalar(monkeypatch, cliente, consumidor)

    with pytest.raises(SystemExit, match="ABORT SHA/SIZE MISMATCH"):
        consume(raw_dir=raw, idle_ms=1000)
    assert cliente.writes == []
    assert consumidor.commits == []
    assert consumidor.closed is True


def test_consume_json_corrupto_se_descarta(monkeypatch, tmp_path):
    """JSON corrupto: skipped+commiteado, sin subida, sin abortar."""
    from storage.kafka_hdfs_uploader import consume

    raw = _raw(tmp_path)
    cliente, consumidor = FakeHDFS(), FakeConsumer(batches=[
        {"p0": [_msg(None, offset=5, raw=b"{no-es-json")]}, {}])
    _instalar(monkeypatch, cliente, consumidor)

    res = consume(raw_dir=raw, idle_ms=1000)
    assert res["uploaded"] == 0
    assert res["skipped"] == 1
    assert cliente.writes == []
    assert len(consumidor.commits) == 1
    assert consumidor.closed is True


def test_produce_sin_errback_no_bloquea(monkeypatch, tmp_path, capsys):
    """Future perezoso (sin invocar errback): produce retorna y hace flush."""
    raw = _raw(tmp_path)
    monkeypatch.setattr("storage.kafka_raw_producer.DEFAULT_RAW_DIR", raw)
    fake = FakeProducerLazy()

    enviados = produce(producer=fake)

    assert enviados == 1
    assert fake.flushed is True
    assert fake.closed is False  # productor inyectado no se cierra
    assert len(fake.sent) == 1
    salida = capsys.readouterr().out
    assert "ADAPTER_RAW_PUBLICADOS 1" in salida


def test_poll_vacio_timeout_termina(monkeypatch, tmp_path):
    """poll siempre vacio: tras idle_ms el consumidor termina con 0 subidos."""
    from storage.kafka_hdfs_uploader import consume

    raw = _raw(tmp_path)
    cliente, consumidor = FakeHDFS(), FakeConsumer(batches=[{}, {}])
    _instalar(monkeypatch, cliente, consumidor)

    # POLL_MS=1000 e idle_ms=1000 -> un poll vacio basta para terminar
    res = consume(raw_dir=raw, idle_ms=1000)
    assert res == {"uploaded": 0, "skipped": 0, "offsets": []}
    assert cliente.writes == []
    assert consumidor.closed is True
    assert DEFAULT_DEST.endswith("/data/raw")
