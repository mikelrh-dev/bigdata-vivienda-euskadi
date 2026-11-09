"""Tests offline del pipeline Kafka (manifiesto raw -> HDFS centro).

Sin red: no hay broker, ni WebHDFS, ni Mongo. Se sustituyen
`KafkaProducer`, `KafkaConsumer` e `InsecureClient` por dobles en memoria,
igual que `tests/test_hdfs.py` hace con el cliente HDFS.

Cubre el contrato que ya se verifico a mano el 2026-11-06 (352 ficheros,
offsets 0:1068..0:1419, lag 0):
- defaults del cluster centro y getters que leen entorno;
- seleccion de `data/raw` sin `legacy_obsoleto_no_usar`;
- forma exacta del manifiesto `{type, rel, size, sha256}`;
- publicacion con `key=rel` y API de `Future` (`add_callback`/`add_errback`,
  nunca `callback=` como kwarg, que es el bug que ya rompio el productor);
- `rel` peligrosa rechazada y SHA/size local exigidos;
- consumidor: descarta lo que no es manifiesto, aborta sin commitear si el
  SHA no cuadra y commitea `offset + 1` solo despues de escribir en HDFS.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from storage.kafka_hdfs_uploader import (
    DEFAULT_BOOTSTRAP,
    DEFAULT_DEST,
    DEFAULT_GROUP,
    get_bootstrap,
    get_group,
    get_idle_ms,
    get_topic,
    is_valid_rel,
    verify_local,
)
from storage.kafka_raw_producer import (
    DEFAULT_BOOTSTRAP_SERVERS,
    DEFAULT_TOPIC,
    get_bootstrap_servers,
    iter_raw_files,
    manifest_entry,
    produce,
)

ROOT = Path(__file__).resolve().parent.parent


# --- dobles ---------------------------------------------------------------


class FakeFuture:
    """Superficie de kafka.future.Future: add_callback / add_errback."""

    def __init__(self, offset: int) -> None:
        self.offset = offset
        self.callbacks: list = []
        self.errbacks: list = []

    def add_callback(self, fn):
        self.callbacks.append(fn)
        fn(SimpleNamespace(topic=DEFAULT_TOPIC, partition=0, offset=self.offset))
        return self

    def add_errback(self, fn):
        self.errbacks.append(fn)
        return self


class FakeProducer:
    """Sin `**kwargs` a proposito: `send(..., callback=...)` debe reventar."""

    def __init__(self) -> None:
        self.sent: list[dict] = []
        self.futures: list[FakeFuture] = []
        self.flushed = False
        self.closed = False

    def send(self, topic, key=None, value=None):  # noqa: ANN001
        self.sent.append({"topic": topic, "key": key, "value": value})
        fut = FakeFuture(len(self.sent) - 1)
        self.futures.append(fut)
        return fut

    def flush(self) -> None:
        self.flushed = True

    def close(self) -> None:
        self.closed = True


class FakeHDFS:
    def __init__(self) -> None:
        self.writes: list[tuple[str, bytes, bool]] = []
        self.dirs: list[str] = []

    def makedirs(self, path, **kwargs):  # noqa: ANN001
        self.dirs.append(path)

    def write(self, path, data=None, overwrite=False, **kwargs):  # noqa: ANN001
        self.writes.append((path, data, overwrite))


class FakeConsumer:
    def __init__(self, batches: list[dict] | None = None) -> None:
        self.batches = list(batches or [])
        self.commits: list[dict] = []
        self.closed = False

    def poll(self, timeout_ms=1000, **kwargs):  # noqa: ANN001
        return self.batches.pop(0) if self.batches else {}

    def commit(self, offsets):  # noqa: ANN001
        self.commits.append(offsets)

    def close(self) -> None:
        self.closed = True


def _msg(payload: dict | None, offset: int = 0, partition: int = 0, raw: bytes | None = None):
    value = raw if raw is not None else json.dumps(payload).encode("utf-8")
    return SimpleNamespace(
        topic=DEFAULT_TOPIC, partition=partition, offset=offset, value=value
    )


def _raw_tree(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    (raw / "legacy_obsoleto_no_usar").mkdir(parents=True)
    (raw / "legacy_obsoleto_no_usar" / "old.csv").write_bytes(b"legacy")
    (raw / ".FROZEN").write_bytes(b"")
    (raw / "b.json").write_bytes(b'{"k": 1}')
    (raw / "a.csv").write_bytes(b"x,y\n1,2\n")
    return raw


# --- productor ------------------------------------------------------------


def test_defaults_apuntan_al_cluster_centro(monkeypatch) -> None:
    for var in (
        "KAFKA_BOOTSTRAP_SERVERS",
        "KAFKA_TOPIC",
        "KAFKA_GROUP_ID",
        "KAFKA_IDLE_MS",
        "HDFS_URL",
    ):
        monkeypatch.delenv(var, raising=False)
    assert DEFAULT_BOOTSTRAP_SERVERS == "10.22.87.215:9092"
    assert DEFAULT_BOOTSTRAP == "10.22.87.215:9092"
    assert DEFAULT_TOPIC == "vivienda_euskadi"
    assert DEFAULT_GROUP == "hdfs_centro"
    assert DEFAULT_DEST == (
        "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw"
    )
    assert get_bootstrap_servers() == "10.22.87.215:9092"
    assert get_bootstrap() == "10.22.87.215:9092"
    assert get_topic() == "vivienda_euskadi"
    assert get_group() == "hdfs_centro"
    assert get_idle_ms() == 10_000


def test_getters_leen_entorno(monkeypatch) -> None:
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "broker.test:19092")
    monkeypatch.setenv("KAFKA_TOPIC", "otro_topic")
    monkeypatch.setenv("KAFKA_GROUP_ID", "grupo_test")
    monkeypatch.setenv("KAFKA_IDLE_MS", "1500")
    assert get_bootstrap_servers() == "broker.test:19092"
    assert get_bootstrap() == "broker.test:19092"
    assert get_topic() == "otro_topic"
    assert get_group() == "grupo_test"
    assert get_idle_ms() == 1500


def test_iter_raw_files_excluye_legacy_y_ordena(tmp_path) -> None:
    raw = _raw_tree(tmp_path)
    rels = [p.relative_to(raw).as_posix() for p in iter_raw_files(raw)]
    assert rels == [".FROZEN", "a.csv", "b.json"]
    assert not any("legacy" in r for r in rels)


def test_manifest_entry_campos_y_sha(tmp_path) -> None:
    raw = _raw_tree(tmp_path)
    entry = manifest_entry(raw / "a.csv", raw_dir=raw)
    assert entry["type"] == "raw_manifest"
    assert entry["rel"] == "a.csv"
    assert entry["size"] == len(b"x,y\n1,2\n") == 8
    assert entry["sha256"] == hashlib.sha256(b"x,y\n1,2\n").hexdigest()
    assert set(entry) == {"type", "rel", "size", "sha256"}


def test_produce_publica_con_key_rel_y_api_future(monkeypatch, tmp_path, capsys) -> None:
    raw = _raw_tree(tmp_path)
    monkeypatch.setattr("storage.kafka_raw_producer.DEFAULT_RAW_DIR", raw)
    fake = FakeProducer()

    enviados = produce(producer=fake)

    assert enviados == 3
    assert fake.flushed is True
    # Productor inyectado: no se cierra desde produce().
    assert fake.closed is False
    claves = [m["key"].decode("utf-8") for m in fake.sent]
    assert claves == [".FROZEN", "a.csv", "b.json"]
    assert all(m["topic"] == DEFAULT_TOPIC for m in fake.sent)
    for mensaje in fake.sent:
        payload = json.loads(mensaje["value"].decode("utf-8"))
        assert payload["type"] == "raw_manifest"
        assert payload["rel"] == mensaje["key"].decode("utf-8")
        assert payload["size"] > 0 or payload["rel"] == ".FROZEN"
        assert len(payload["sha256"]) == 64
    # Cada envio registro exito y error (API de Future, no `callback=`).
    assert all(len(f.callbacks) == 1 and len(f.errbacks) == 1 for f in fake.futures)
    salida = capsys.readouterr().out
    assert "Publicado vivienda_euskadi:0@" in salida
    assert "ADAPTER_RAW_PUBLICADOS 3" in salida


def test_produce_cierra_su_propio_productor_y_respeta_limit(monkeypatch, tmp_path) -> None:
    raw = _raw_tree(tmp_path)
    monkeypatch.setattr("storage.kafka_raw_producer.DEFAULT_RAW_DIR", raw)
    fake = FakeProducer()

    class _FakeAdmin:
        created = []

        def create_topics(self, configs):
            self.created.extend(configs)

        def close(self):
            pass

    monkeypatch.setattr("kafka.KafkaProducer", lambda **kwargs: fake)

    enviados = produce(limit=1, admin=_FakeAdmin())

    assert enviados == 1
    assert len(fake.sent) == 1
    assert fake.closed is True


# --- consumidor -----------------------------------------------------------


def test_is_valid_rel_rechaza_rutas_peligrosas() -> None:
    assert is_valid_rel("a.csv") is True
    assert is_valid_rel("html_fotocasa/x.html") is True
    assert is_valid_rel("") is False
    assert is_valid_rel("../fuera.csv") is False
    assert is_valid_rel("a/../../fuera.csv") is False
    assert is_valid_rel("/etc/passwd") is False
    assert is_valid_rel("\\absoluta.csv") is False
    assert is_valid_rel("legacy_obsoleto_no_usar/old.csv") is False
    assert is_valid_rel("a/legacy_obsoleto_no_usar/old.csv") is False


def test_verify_local_exige_size_y_sha(tmp_path) -> None:
    raw = _raw_tree(tmp_path)
    data = b"x,y\n1,2\n"
    sha = hashlib.sha256(data).hexdigest()
    assert verify_local(raw, "a.csv", len(data), sha) is True
    assert verify_local(raw, "a.csv", len(data) + 1, sha) is False
    assert verify_local(raw, "a.csv", len(data), "0" * 64) is False
    assert verify_local(raw, "no_existe.csv", len(data), sha) is False


def _payload(raw: Path, rel: str) -> dict:
    data = (raw / rel).read_bytes()
    return {
        "type": "raw_manifest",
        "rel": rel,
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def test_consume_sube_y_commitea_tras_verificar(monkeypatch, tmp_path) -> None:
    from storage.kafka_hdfs_uploader import consume

    raw = _raw_tree(tmp_path)
    cliente = FakeHDFS()
    consumidor = FakeConsumer(batches=[{"p0": [_msg(_payload(raw, "a.csv"), offset=7)]}, {}])
    monkeypatch.setattr("hdfs.InsecureClient", lambda *a, **k: cliente)
    monkeypatch.setattr("kafka.KafkaConsumer", lambda *a, **k: consumidor)

    res = consume(raw_dir=raw, idle_ms=1000)

    assert res["uploaded"] == 1
    assert res["skipped"] == 0
    assert res["offsets"] == [(0, 7)]
    assert cliente.writes == [(f"{DEFAULT_DEST}/a.csv", b"x,y\n1,2\n", True)]
    assert len(consumidor.commits) == 1
    (offset,) = consumidor.commits[0].values()
    assert offset.offset == 8  # offset del mensaje + 1
    assert consumidor.closed is True


def test_consume_aborta_sin_commitear_si_sha_no_cuadra(monkeypatch, tmp_path) -> None:
    from storage.kafka_hdfs_uploader import consume

    raw = _raw_tree(tmp_path)
    roto = {**_payload(raw, "a.csv"), "sha256": "0" * 64}
    cliente = FakeHDFS()
    consumidor = FakeConsumer(batches=[{"p0": [_msg(roto, offset=3)]}, {}])
    monkeypatch.setattr("hdfs.InsecureClient", lambda *a, **k: cliente)
    monkeypatch.setattr("kafka.KafkaConsumer", lambda *a, **k: consumidor)

    with pytest.raises(SystemExit, match="ABORT SHA/SIZE MISMATCH a.csv"):
        consume(raw_dir=raw, idle_ms=1000)

    assert cliente.writes == []
    assert consumidor.commits == []
    assert consumidor.closed is True


def test_consume_descarta_mensajes_que_no_son_manifiesto(monkeypatch, tmp_path) -> None:
    from storage.kafka_hdfs_uploader import consume

    raw = _raw_tree(tmp_path)
    cliente = FakeHDFS()
    consumidor = FakeConsumer(
        batches=[
            {
                "p0": [
                    _msg({"precio": 850, "municipio": "Bilbao"}, offset=1),
                    _msg(None, offset=2, raw=b"no-es-json"),
                ]
            },
            {},
        ]
    )
    monkeypatch.setattr("hdfs.InsecureClient", lambda *a, **k: cliente)
    monkeypatch.setattr("kafka.KafkaConsumer", lambda *a, **k: consumidor)

    res = consume(raw_dir=raw, idle_ms=1000)

    assert res["uploaded"] == 0
    assert res["skipped"] == 2
    assert res["offsets"] == []
    assert cliente.writes == []
    # Los descartes si se commitean para no repetirlos.
    assert len(consumidor.commits) == 2
