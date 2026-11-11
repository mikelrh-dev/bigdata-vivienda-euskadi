"""Indices de metadata que emite transform/quality/normalizar_metadata.py.

Cubre con tmp_path (sin tocar data/):
- ``_csv_index``: inventario de CSV de raw con ``n_csvs``.
- ``_normalizados_map``: cada ``*_normalizado.json`` con timestamp heredado
  apunta a su raw de origen y solo se registran los que casan con el patron.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "normalizar_metadata",
    ROOT / "transform" / "quality" / "normalizar_metadata.py")
assert _spec is not None and _spec.loader is not None
nm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nm)


def test_csv_index_cuenta_y_relativiza(tmp_path):
    raw = tmp_path / "raw"
    (raw / "sub").mkdir(parents=True)
    (raw / "a.csv").write_bytes(b"x,y\n1,2\n")
    (raw / "sub" / "b.csv").write_bytes(b"z\n")
    (raw / "ignorado.json").write_bytes(b"{}")

    idx = nm._csv_index(raw)

    assert idx["n_csvs"] == 2
    assert {c["fichero"] for c in idx["csvs"]} == {"a.csv", "sub/b.csv"}
    assert all(c["bytes"] > 0 for c in idx["csvs"])


def test_normalizados_map_solo_con_timestamp(tmp_path):
    raw = tmp_path / "raw"
    proc = tmp_path / "procesado"
    raw.mkdir()
    proc.mkdir()
    (raw / "anuncios_20261029.json").write_bytes(b"{}")
    (proc / "anuncios_20261029_normalizado.json").write_bytes(b"{}")
    (proc / "otro_normalizado.json").write_bytes(b"{}")

    mapa = nm._normalizados_map(proc, raw)

    entradas = mapa["ficheros_con_timestamp_heredado"]
    assert [e["nombre_actual"] for e in entradas] == [
        "anuncios_20261029_normalizado.json"]
    assert entradas[0]["origen_raw"] == "anuncios_20261029.json"
    assert entradas[0]["origen_raw_existe"] is True


def test_normalizados_map_marca_origen_ausente(tmp_path):
    raw = tmp_path / "raw"
    proc = tmp_path / "procesado"
    raw.mkdir()
    proc.mkdir()
    (proc / "huerfano_20260101_normalizado.json").write_bytes(b"{}")

    mapa = nm._normalizados_map(proc, raw)

    entrada = mapa["ficheros_con_timestamp_heredado"][0]
    assert entrada["origen_raw"] == "huerfano_20260101.json"
    assert entrada["origen_raw_existe"] is False
