"""load_mongo con mongomock (storage/load_mongo.py).

CSV vacio, nulos, idempotencia (dos cargas, mismo conteo) y
geo_point invalida -> None. Sin Mongo real: se parchea
storage.mongo.get_db con mongomock y storage.load_mongo.PROC con
tmp_path. Si mongomock no esta, skip (como test_integracion_mongo).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

mongomock = pytest.importorskip(
    "mongomock", reason="mongomock no instalado: skip offline")

import storage.load_mongo as lm  # noqa: E402
import storage.mongo as sm  # noqa: E402

COLUMNAS = [
    "portal", "id_anuncio", "property_fingerprint", "modalidad",
    "precio_eur", "superficie_m2", "habitaciones", "es_outlier_superficie",
    "codigo_ine", "municipio", "equipamiento", "precio_m2_calc",
    "es_outlier_iqr", "motivo_exclusion", "precio_m2_fuera_3_50",
    "superficie_fuera_10_500", "iqr_excluido", "origen_resolucion",
    "geo_invalida",
]


@pytest.fixture()
def mongo_tmp(monkeypatch, tmp_path):
    client = mongomock.MongoClient()
    db = client["load_test"]
    monkeypatch.setattr(sm, "get_db", lambda: db)
    monkeypatch.setattr(lm, "PROC", tmp_path)
    return db


def _escribir_csv(path: Path, filas: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNAS)
        writer.writeheader()
        for fila in filas:
            writer.writerow({c: fila.get(c, "") for c in COLUMNAS})


def _fila(**kw) -> dict:
    base = {
        "portal": "pisos", "id_anuncio": "1", "property_fingerprint": "fp1",
        "modalidad": "larga_estancia", "precio_eur": "900",
        "superficie_m2": "80", "habitaciones": "2",
        "es_outlier_superficie": "false", "codigo_ine": "48020",
        "municipio": "Bilbao", "equipamiento": "", "precio_m2_calc": "11.25",
        "es_outlier_iqr": "false", "motivo_exclusion": "",
        "precio_m2_fuera_3_50": "false", "superficie_fuera_10_500": "false",
        "iqr_excluido": "false", "origen_resolucion": "subtitulo",
        "geo_invalida": "false",
    }
    base.update(kw)
    return base


def test_csv_vacio_no_toca_coleccion(mongo_tmp, tmp_path):
    """CSV solo con cabecera -> load_anuncios retorna 0 y no crea docs."""
    _escribir_csv(tmp_path / "anuncios_unificados.csv", [])
    assert lm.load_anuncios() == 0
    assert mongo_tmp["anuncios"].count_documents({}) == 0


def test_nulos_se_cargan_como_none(mongo_tmp, tmp_path):
    """Fila con precio/superficie/habitaciones vacios -> None, no 0."""
    _escribir_csv(tmp_path / "anuncios_unificados.csv", [
        _fila(precio_eur="", superficie_m2="", habitaciones="",
              precio_m2_calc=""),
    ])
    assert lm.load_anuncios() == 1
    doc = mongo_tmp["anuncios"].find_one({})
    assert doc is not None
    assert doc["precio_eur"] is None
    assert doc["superficie_m2"] is None
    assert doc["habitaciones"] is None
    assert doc["precio_m2"] is None
    assert doc["ubicacion"]["codigo_ine"] == "48020"


def test_idempotente_dos_cargas_mismo_conteo(mongo_tmp, tmp_path):
    """Cargar dos veces deja el mismo conteo (replace idempotente)."""
    _escribir_csv(tmp_path / "anuncios_unificados.csv", [
        _fila(id_anuncio="1"),
        _fila(id_anuncio="2", property_fingerprint="fp2"),
    ])
    n1 = lm.load_anuncios()
    assert n1 == 2
    assert mongo_tmp["anuncios"].count_documents({}) == 2
    n2 = lm.load_anuncios()
    assert n2 == 2
    assert mongo_tmp["anuncios"].count_documents({}) == 2


@pytest.mark.parametrize("lat,lon", [
    ("999", "-2.93"),      # lat fuera de rango
    ("43.26", "999"),      # lon fuera de rango
    ("abc", "-2.93"),      # no numerico
    ("", ""),              # vacios
    (None, None),          # nulos
    ("nan", "inf"),        # no finitos / basura
])
def test_geo_point_invalida_es_none(lat, lon):
    """_geo_point devuelve None ante coordenadas invalidas."""
    assert lm._geo_point(lat, lon) is None


def test_geo_point_valida():
    """_geo_point valida devuelve Point [lon, lat]."""
    assert lm._geo_point("43.26", "-2.93") == {
        "type": "Point", "coordinates": [-2.93, 43.26]}


def test_fila_sin_codigo_ine_se_omite(mongo_tmp, tmp_path):
    """Fila sin codigo_ine no se carga (code None -> continue)."""
    _escribir_csv(tmp_path / "anuncios_unificados.csv", [
        _fila(codigo_ine=""),
        _fila(id_anuncio="2"),
    ])
    assert lm.load_anuncios() == 1
    assert mongo_tmp["anuncios"].count_documents({}) == 1
