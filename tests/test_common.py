"""Contrato de los helpers de escritura y lectura de extract/transform."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import load_module


@pytest.fixture(scope="module")
def transform_common():
    return load_module("transform_common_test", "transform/_common.py")


@pytest.fixture(scope="module")
def extract_common():
    return load_module("extract_common_test", "extract/_common.py")


def test_guardar_json_estructura_y_metadata(transform_common, tmp_path: Path) -> None:
    destino = tmp_path / "salida.json"
    transform_common.guardar_json(
        destino,
        [{"a": 1}, {"a": 2}],
        metadata={"fuente": "fixture", "url": "https://example.test"},
    )
    data = json.loads(destino.read_text(encoding="utf-8"))
    assert set(data) == {"metadata", "datos"}
    assert data["datos"] == [{"a": 1}, {"a": 2}]
    assert data["metadata"]["n_registros"] == 2
    assert data["metadata"]["fuente"] == "fixture"
    assert "fecha_extraccion" in data["metadata"]


def test_guardar_json_respeta_n_registros_explicito(transform_common, tmp_path: Path) -> None:
    destino = tmp_path / "salida.json"
    transform_common.guardar_json(destino, [1], metadata={"n_registros": 99})
    assert json.loads(destino.read_text(encoding="utf-8"))["metadata"]["n_registros"] == 99


def test_guardar_json_crea_directorios_padre(transform_common, tmp_path: Path) -> None:
    destino = tmp_path / "a" / "b" / "salida.json"
    transform_common.guardar_json(destino, [])
    assert destino.is_file()


def test_extract_guardar_json_misma_estructura(extract_common, tmp_path: Path) -> None:
    destino = tmp_path / "salida.json"
    extract_common.guardar_json(destino, [{"x": 1}], metadata={"fuente": "fixture"})
    data = json.loads(destino.read_text(encoding="utf-8"))
    assert data["metadata"]["n_registros"] == 1
    assert data["datos"] == [{"x": 1}]


def test_metadata_minima_son_cuatro_campos(extract_common) -> None:
    assert extract_common.METADATA_MINIMA == (
        "fuente",
        "url",
        "fecha_extraccion",
        "n_registros",
    )


def test_guardar_meta_escribe_sidecar(extract_common, tmp_path: Path) -> None:
    ruta_datos = tmp_path / "tabla.csv"
    ruta_datos.write_text("a\n1\n", encoding="utf-8")
    sidecar = extract_common.guardar_meta(
        ruta_datos,
        {"fuente": "fixture", "url": "https://example.test", "n_registros": 1},
    )
    assert sidecar == tmp_path / "tabla.meta.json"
    meta = json.loads(sidecar.read_text(encoding="utf-8"))
    assert meta["fuente"] == "fixture"
    assert "fecha_extraccion" in meta


def test_write_raw_relativo_usa_raw_dir(extract_common, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(extract_common, "RAW_DIR", tmp_path / "raw")
    destino = extract_common.write_raw("dato.bin", b"contenido")
    assert destino == tmp_path / "raw" / "dato.bin"
    assert destino.read_bytes() == b"contenido"
    assert not (tmp_path / "raw" / "dato.bin.tmp").exists()


def test_write_raw_sobrescribe_de_forma_atomica(extract_common, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(extract_common, "RAW_DIR", tmp_path / "raw")
    extract_common.write_raw("dato.bin", b"primero")
    destino = extract_common.write_raw("dato.bin", b"segundo")
    assert destino.read_bytes() == b"segundo"
    assert sorted(p.name for p in destino.parent.iterdir()) == ["dato.bin"]


@pytest.mark.parametrize(
    ("valor", "esperado"),
    [("1", "00001"), ("020", "00020"), ("48020", "48020"), (" 7 ", "00007")],
)
def test_leer_csv_seguro_normaliza_codigo_ine(
    transform_common, tmp_path: Path, valor: str, esperado: str
) -> None:
    ruta = tmp_path / "tabla.csv"
    ruta.write_text(f"codigo_ine,nombre\n{valor},Bilbao\n", encoding="utf-8-sig")
    df = transform_common.leer_csv_seguro(ruta)
    assert df.loc[0, "codigo_ine"] == esperado
    assert df["nombre"].dtype == object


def test_extract_leer_csv_seguro_normaliza_codigo_ine(extract_common, tmp_path: Path) -> None:
    ruta = tmp_path / "tabla.csv"
    ruta.write_text("codigo_ine,nombre\n1,Bilbao\n", encoding="utf-8-sig")
    df = extract_common.leer_csv_seguro(ruta)
    assert df.loc[0, "codigo_ine"] == "00001"
