"""Verificador de reproducibilidad y guarda del pipeline de habitaciones.

Los checks de raw y DAG son offline y deterministas; el de colecciones usa
Mongo real, asi que solo se prueba el parseo del dict de load_all.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.run_analisis_mongo import exportar_habitaciones_csv  # noqa: E402
from scripts import verificar_reproducibilidad as vr  # noqa: E402


def test_raw_manifest_cuadra():
    if not (vr.RAW_DIR / ".FROZEN").exists():
        pytest.skip("data/raw no esta en este clon (raw no versionado)")
    estado, detalle = vr.check_raw()
    if estado == vr.NO_VERIFICABLE:
        pytest.skip(detalle)
    assert estado == vr.OK, detalle
    assert "355" in detalle


def test_dag_cerrado_sin_huerfanos():
    estado, detalle = vr.check_dag()
    if estado == vr.NO_VERIFICABLE:
        pytest.skip(detalle)
    assert estado == vr.OK, detalle
    assert "sin" not in detalle.lower() or "productor" not in detalle.lower()


def test_colecciones_cargadas_cubre_las_17():
    nombres = vr.colecciones_cargadas()
    assert len(nombres) == 17
    assert "anuncios_habitaciones_unificados" in nombres
    assert "anuncios_habitaciones_unificados_bigdata" in nombres


def test_habitaciones_vacio_falla_en_vez_de_csv_vacio(tmp_path):
    with pytest.raises(ValueError, match="anuncios_habitaciones_unificados"):
        exportar_habitaciones_csv(
            {"pipeline_habitaciones_por_municipio": []}, tmp_path)
    assert not (tmp_path / "mongo_habitaciones_por_municipio.csv").exists()


def test_habitaciones_con_filas_escribe_csv(tmp_path):
    filas = [{"codigo_ine": "48020", "municipio": "Bilbao", "n": 1}]
    rutas = exportar_habitaciones_csv(
        {"pipeline_habitaciones_por_municipio": filas}, tmp_path)
    ruta = rutas["mongo_habitaciones_por_municipio.csv"]
    assert ruta.is_file()
    assert len(ruta.read_text(encoding="utf-8-sig").splitlines()) == 2
