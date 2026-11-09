"""Reintentos/fallos HDFS con fake que inyecta errores (storage/hdfs_utils.py).

Extiende FakeHDFSClient de test_hdfs.py con fallos programables:
- read_file_sha256 con red caida propaga la excepcion (no devuelve
  un hash silenciosamente incorrecto);
- upload con un 500 en write propaga, no marca el fichero como hecho
  en el estado, y un reintento posterior del llamante sube OK;
- status de un path inexistente (404): cliente no-estricto devuelve
  None y get_status lo propaga como None; cliente estricto lanza.
Sin red real ni HDFS centro.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from test_hdfs import FakeHDFSClient  # noqa: E402
from storage.hdfs_utils import (  # noqa: E402
    get_status,
    read_file_sha256,
    upload_raw_excluding_legacy,
)


class FlakyHDFSClient(FakeHDFSClient):
    """Fake con fallos programables: write/read/status pueden fallar N veces."""

    def __init__(self, *, fallos_write: int = 0, fallos_read: int = 0,
                 strict: bool = True) -> None:
        super().__init__()
        self.fallos_write = fallos_write
        self.fallos_read = fallos_read
        self.strict = strict
        self.write_intentos = 0

    def write(self, hdfs_path, data=None, overwrite=False, **kwargs):  # noqa: ANN001
        self.write_intentos += 1
        if self.fallos_write > 0:
            self.fallos_write -= 1
            raise ConnectionError("500 Internal Server Error (fake)")
        return super().write(hdfs_path, data=data, overwrite=overwrite, **kwargs)

    def read(self, hdfs_path):  # noqa: ANN001
        if self.fallos_read > 0:
            self.fallos_read -= 1
            raise ConnectionError("red caida (fake)")
        return super().read(hdfs_path)

    def status(self, hdfs_path, strict=None):  # noqa: ANN001
        return super().status(hdfs_path,
                              strict=self.strict if strict is None else strict)


def test_read_file_sha256_red_caida_lanza():
    """read_file_sha256 no traga la caida: propaga ConnectionError."""
    fake = FlakyHDFSClient(fallos_read=1)
    fake.store["/raw/a.csv"] = b"hola"
    with pytest.raises(ConnectionError):
        read_file_sha256(fake, "/raw/a.csv")
    # Tras el fallo, la siguiente lectura (sin fallos) devuelve el sha correcto
    import hashlib
    assert read_file_sha256(fake, "/raw/a.csv") == hashlib.sha256(b"hola").hexdigest()


def test_upload_500_propaga_y_reintento_luego_ok(tmp_path):
    """Un 500 en write no marca done; reintentar sube y deduplica despues."""
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "a.csv").write_bytes(b"col\n1\n")
    state_dir = tmp_path / "st"
    fake = FlakyHDFSClient(fallos_write=1)

    with pytest.raises(ConnectionError):
        upload_raw_excluding_legacy(fake, raw_dir=raw, hdfs_path="/raw",
                                    state_dir=state_dir)
    # El fallo no dejo el fichero marcado como hecho ni subido
    assert fake.write_intentos == 1
    assert "/raw/a.csv" not in fake.store
    estado = state_dir / "hdfs_upload_raw.json"
    if estado.exists():
        assert "a.csv" not in estado.read_text(encoding="utf-8")

    # Reintento del llamante: ahora sube OK
    res = upload_raw_excluding_legacy(fake, raw_dir=raw, hdfs_path="/raw",
                                      state_dir=state_dir)
    assert res == {"uploaded": 1, "deduped": 0}
    assert fake.store["/raw/a.csv"] == b"col\n1\n"
    # Tercera llamada deduplica por estado
    res2 = upload_raw_excluding_legacy(fake, raw_dir=raw, hdfs_path="/raw",
                                       state_dir=state_dir)
    assert res2 == {"uploaded": 0, "deduped": 1}


def test_status_404_no_estricto_es_none():
    """Cliente no-estricto: status de path inexistente (404) -> None via get_status."""
    fake = FlakyHDFSClient(strict=False)
    assert get_status(fake, "/raw/no_existe.csv") is None


def test_status_404_estricto_lanza():
    """Cliente estricto (WebHDFS real): status inexistente lanza FileNotFoundError."""
    fake = FlakyHDFSClient(strict=True)
    with pytest.raises(FileNotFoundError):
        get_status(fake, "/raw/no_existe.csv")
    # Y un path existente devuelve FILE
    fake.store["/raw/a.csv"] = b"x"
    st = get_status(fake, "/raw/a.csv")
    assert st is not None and st["type"] == "FILE"
