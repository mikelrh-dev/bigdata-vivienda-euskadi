"""Extractor 26 (VPO terminadas): validación en memoria y escritura única en raw.

No toca ``data/raw``: ``test_escribir_raw`` monkeypatchea el destino y la
guarda. Fija el contrato que sustituyó al staging + copia redundante.
"""

from __future__ import annotations

import csv
import importlib.util
import io
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "vpo_terminadas", ROOT / "extract" / "26_vpo_terminadas.py")
assert _spec is not None and _spec.loader is not None
vpo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vpo)


def _csv_bytes(n: int = 252) -> bytes:
    buf = io.StringIO(newline="")
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(["Entidad", "2024"])
    for i in range(n):
        writer.writerow([f"{i:05d}", f"{i / 10:.1f}".replace(".", ",")])
    return buf.getvalue().encode("latin-1")


def test_validar_en_memoria() -> None:
    n, minimo, maximo = vpo.validar(_csv_bytes())
    assert n == vpo.MIN_MUNICIPIOS
    assert 0 <= minimo <= maximo <= 100


def test_validar_rechaza_origen_incompleto() -> None:
    with pytest.raises(ValueError):
        vpo.validar(_csv_bytes(3))


def test_sin_staging_ni_flags_redundantes() -> None:
    src = (ROOT / "extract" / "26_vpo_terminadas.py").read_text(encoding="utf-8")
    for prohibido in ("data/staging", "--promote", "--sin-descargar",
                      "shutil.copyfile"):
        assert prohibido not in src, f"resto de staging: {prohibido}"


def test_escribir_raw_guarda_y_escribe_una_vez(tmp_path, monkeypatch) -> None:
    destino = tmp_path / "udalmap_vpo_terminadas.csv"
    monkeypatch.setattr(vpo, "RAW_CSV", destino)

    llamadas: list[str] = []
    import transform._raw_guard as guard
    monkeypatch.setattr(guard, "assert_raw_writable",
                        lambda reason: llamadas.append(reason))

    contenido = _csv_bytes()
    salida = vpo.escribir_raw(contenido)

    assert salida == destino
    assert destino.read_bytes() == contenido
    assert llamadas and llamadas[0].strip()
