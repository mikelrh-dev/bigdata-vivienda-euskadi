"""Tests HDFS-01 con fake en memoria (sin red ni bronce productivo).

Cubre: URL por defecto e ignore de localhost:9870, get_client con overrides,
subida temporal a HDFS fake con exclusion de legacy y recuperacion SHA
byte-identica (mismo contenido y mismo tamano en bytes), mas helpers
get_status, ping y delete_recursive.
"""

from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path

import pytest

from storage.hdfs_utils import (
    DEFAULT_HDFS_RAW,
    DEFAULT_HDFS_URL,
    DEFAULT_HDFS_USER,
    delete_recursive,
    get_client,
    get_hdfs_url,
    get_hdfs_user,
    get_status,
    ping,
    read_file_sha256,
    upload_raw_excluding_legacy,
)


class FakeHDFSClient:
    """Fake en memoria con la misma superficie que InsecureClient usada aqui."""

    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}

    def write(self, hdfs_path: str, data: bytes | None = None, overwrite: bool = False, **kwargs):
        if data is None:
            raise ValueError("data requerida en fake")
        payload = data.encode() if isinstance(data, str) else bytes(data)
        if hasattr(data, "read"):
            payload = data.read()  # type: ignore[no-any-return]
            if isinstance(payload, str):
                payload = payload.encode()
        self.store[hdfs_path] = payload
        return None

    def read(self, hdfs_path: str) -> io.BytesIO:
        if hdfs_path not in self.store:
            raise FileNotFoundError(hdfs_path)
        return io.BytesIO(self.store[hdfs_path])

    def status(self, hdfs_path: str, strict: bool = True) -> dict | None:
        if hdfs_path in self.store:
            return {"path": hdfs_path, "type": "FILE", "length": len(self.store[hdfs_path])}
        prefix = hdfs_path.rstrip("/") + "/"
        if any(k.startswith(prefix) for k in self.store):
            return {"path": hdfs_path, "type": "DIRECTORY"}
        if strict:
            raise FileNotFoundError(hdfs_path)
        return None

    def delete(self, hdfs_path: str, recursive: bool = False) -> bool:
        if hdfs_path in self.store:
            del self.store[hdfs_path]
            return True
        prefix = hdfs_path.rstrip("/") + "/"
        keys = [k for k in self.store if k.startswith(prefix)]
        if not keys:
            return False
        if not recursive:
            raise ValueError("directorio no vacio")
        for k in keys:
            del self.store[k]
        return True


def _sha_local(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def test_get_hdfs_url_default(monkeypatch):
    monkeypatch.delenv("HDFS_URL", raising=False)
    assert get_hdfs_url() == "http://10.22.87.215:50070"
    assert DEFAULT_HDFS_URL == "http://10.22.87.215:50070"
    assert DEFAULT_HDFS_USER == "iabd-user15"
    assert get_hdfs_user() == "iabd-user15"


def test_get_hdfs_url_ignora_localhost_9870(monkeypatch):
    monkeypatch.setenv("HDFS_URL", "http://localhost:9870/webhdfs/v1")
    assert get_hdfs_url() == DEFAULT_HDFS_URL
    monkeypatch.setenv("HDFS_URL", "http://127.0.0.1:9870/webhdfs/v1")
    # 127.0.0.1 no contiene localhost, se respeta tal cual.
    assert get_hdfs_url() == "http://127.0.0.1:9870/webhdfs/v1"
    monkeypatch.setenv("HDFS_URL", "http://10.22.87.215:50070")
    assert get_hdfs_url() == "http://10.22.87.215:50070"


def test_get_client_con_overrides(monkeypatch):
    monkeypatch.setenv("HDFS_URL", "http://localhost:9870/webhdfs/v1")
    monkeypatch.setenv("HDFS_USER", "iabd-user15")
    c = get_client()
    assert c.url == DEFAULT_HDFS_URL
    assert c._session.params.get("user.name") == "iabd-user15"
    c2 = get_client(url="http://10.22.87.215:50070", user="iabd-user15")
    assert c2.url == "http://10.22.87.215:50070"
    assert c2._session.params.get("user.name") == "iabd-user15"


def test_upload_temporal_y_recuperacion_sha(tmp_path):
    raw = tmp_path / "raw"
    (raw / "legacy_obsoleto_no_usar").mkdir(parents=True)
    (raw / ".FROZEN").write_bytes(b"frozen")
    (raw / ".gitkeep").write_bytes(b"")
    (raw / "a.csv").write_bytes(b"col1,col2\n1,2\n")
    (raw / "b.json").write_bytes(b'{"k": 1}')
    (raw / "c.zip").write_bytes(b"PK\x03\x04fake")
    (raw / "d.xlsx").write_bytes(b"PK fake xlsx")
    (raw / "e.geojson").write_bytes(b'{"type":"FeatureCollection"}')
    (raw / "html_fotocasa").mkdir()
    (raw / "html_fotocasa" / "x.html").write_bytes(b"<html>fotocasa</html>")
    (raw / "gtfs").mkdir()
    (raw / "gtfs" / "gt.zip").write_bytes(b"gtfs-bytes")
    (raw / "shp_euskadi").mkdir()
    (raw / "shp_euskadi" / "m.shp").write_bytes(b"shp-bytes")
    (raw / "legacy_obsoleto_no_usar" / "old.csv").write_bytes(b"legacy-no-subir")

    state_dir = tmp_path / "_hdfs_state"
    dest = "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw"
    fake = FakeHDFSClient()
    res = upload_raw_excluding_legacy(fake, raw_dir=raw, hdfs_path=dest, state_dir=state_dir)
    assert res["uploaded"] == 10
    assert res["deduped"] == 0
    assert all("legacy_obsoleto_no_usar" not in k for k in fake.store)
    assert f"{dest}/.FROZEN" in fake.store
    assert f"{dest}/.gitkeep" in fake.store
    assert f"{dest}/a.csv" in fake.store
    assert f"{dest}/b.json" in fake.store
    assert f"{dest}/c.zip" in fake.store
    assert f"{dest}/d.xlsx" in fake.store
    assert f"{dest}/e.geojson" in fake.store
    assert f"{dest}/html_fotocasa/x.html" in fake.store
    assert f"{dest}/gtfs/gt.zip" in fake.store
    assert f"{dest}/shp_euskadi/m.shp" in fake.store

    # Recuperacion: SHA igual y mismo tamano en bytes que el fichero local.
    for local in raw.rglob("*"):
        if not local.is_file() or "legacy_obsoleto_no_usar" in local.parts:
            continue
        rel = local.relative_to(raw).as_posix()
        hdfs_file = f"{dest}/{rel}"
        sha_local = _sha_local(local)
        sha_remote = read_file_sha256(fake, hdfs_file)
        assert sha_remote == sha_local
        assert len(fake.store[hdfs_file]) == local.stat().st_size

    # Estado resumible por fichero en JSON.
    state_file = state_dir / "hdfs_upload_raw.json"
    assert state_file.exists()
    done = json.loads(state_file.read_text(encoding="utf-8"))
    assert "a.csv" in done
    assert "legacy_obsoleto_no_usar/old.csv" not in done

    # Segunda llamada no re-sube (dedup por estado).
    res2 = upload_raw_excluding_legacy(fake, raw_dir=raw, hdfs_path=dest, state_dir=state_dir)
    assert res2 == {"uploaded": 0, "deduped": 10}


def test_helpers_status_ping_delete(tmp_path):
    fake = FakeHDFSClient()
    assert ping(fake) is False  # base vacia en fake
    fake.store["/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw/a.csv"] = b"hola"
    assert ping(fake) is True
    st = get_status(fake, "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw")
    assert st is not None and st["type"] == "DIRECTORY"
    st2 = get_status(fake, "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw/a.csv")
    assert st2 == {"path": "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw/a.csv", "type": "FILE", "length": 4}
    assert delete_recursive(fake, "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw") is True
    assert fake.store == {}


def test_real_raw_incluye_dotfiles_y_excluye_legacy(tmp_path):
    # Sin tocar bronce productivo: usa tmp_path con .FROZEN/.gitkeep simulados.
    raw = tmp_path / "raw"
    (raw / "legacy_obsoleto_no_usar").mkdir(parents=True)
    (raw / ".FROZEN").write_bytes(b"x")
    (raw / "legacy_obsoleto_no_usar" / "y.csv").write_bytes(b"legacy")
    fake = FakeHDFSClient()
    res = upload_raw_excluding_legacy(fake, raw_dir=raw, hdfs_path="/tmp/raw", state_dir=tmp_path / "st")
    assert res["uploaded"] == 1
    assert "/tmp/raw/.FROZEN" in fake.store
    assert not any("legacy" in k for k in fake.store)
    with pytest.raises(FileNotFoundError):
        upload_raw_excluding_legacy(fake, raw_dir=tmp_path / "no-existe", state_dir=tmp_path / "st")
