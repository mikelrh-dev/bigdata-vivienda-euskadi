"""Tests offline de `scripts/hdfs_recuperacion_un_fichero.py` (HDFS-01).

No tocan red ni HDFS: inyectan un cliente doble y comparan contra un fichero
temporal. Verifican los tres desenlaces (igual, difiere, sin conexion) y que la
ruta se valida antes de salir a la red.
"""

from __future__ import annotations

import hashlib
import io
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import hdfs_recuperacion_un_fichero as rec  # noqa: E402


class FakeClient:
    def __init__(self, payload: bytes | None = None, exc: Exception | None = None):
        self.payload = payload
        self.exc = exc
        self.paths: list[str] = []

    def status(self, path: str) -> dict:
        self.paths.append(path)
        if self.exc:
            raise self.exc
        return {"length": len(self.payload or b"")}

    @contextmanager
    def read(self, path: str) -> Iterator[io.BytesIO]:
        if self.exc:
            raise self.exc
        yield io.BytesIO(self.payload or b"")


@pytest.fixture
def raw_dir(tmp_path: Path) -> Path:
    d = tmp_path / "raw"
    d.mkdir()
    (d / "f.csv").write_bytes(b"codigo_ine,precio\n48020,850\n")
    return d


def test_sha_tamano_iguales(raw_dir: Path) -> None:
    payload = (raw_dir / "f.csv").read_bytes()
    code, info = rec.recuperar("f.csv", raw_dir=raw_dir, client=FakeClient(payload))
    assert code == 0
    assert info["local_sha"] == info["remote_sha"] == hashlib.sha256(payload).hexdigest()
    assert info["local_size"] == info["remote_size"]


def test_difiere_en_contenido(raw_dir: Path) -> None:
    code, info = rec.recuperar("f.csv", raw_dir=raw_dir, client=FakeClient(b"otra,csv\n"))
    assert code == 1
    assert info["local_sha"] != info["remote_sha"]


def test_local_inexistente(raw_dir: Path) -> None:
    code, info = rec.recuperar("no_existe.csv", raw_dir=raw_dir, client=FakeClient(b""))
    assert code == 1
    assert info["error"] == "LOCAL_NO_EXISTE"


def test_sin_conexion_no_lanza(raw_dir: Path) -> None:
    code, info = rec.recuperar("f.csv", raw_dir=raw_dir, client=FakeClient(exc=OSError("timed out")))
    assert code == 2
    assert "HDFS_NO_ALCANZABLE" in str(info["error"])


def test_rel_invalida_no_toca_cliente(raw_dir: Path) -> None:
    fake = FakeClient(b"")
    code, info = rec.recuperar("../fuera.csv", raw_dir=raw_dir, client=fake)
    assert code == 2
    assert info["error"] == "REL_INVALIDA"
    assert fake.paths == []


def test_main_devuelve_2_sin_red(raw_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Sin --raw-dir el script apunta a data/raw; se fuerza fallo de red con rel
    # inexistente en local para no salir a la red desde el test.
    code = rec.main(["--raw-dir", str(raw_dir), "no_existe.csv"])
    assert code == 1
    assert "LOCAL_NO_EXISTE" in capsys.readouterr().out
