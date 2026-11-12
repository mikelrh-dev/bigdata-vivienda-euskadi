"""Tests del orquestador de analisis MongoDB (sin teclear valores).

`test_orquestador_analisis_exporta_tres_conjuntos` ejecuta el orquestador
en `tmp_path`, aserta la existencia de los 3 ficheros y la
reproducibilidad de `n` entre dos ejecuciones.
`test_preparacion_visualizacion_tres_conjuntos` aserta cabeceras y la
coincidencia de cada CSV con los pipelines en memoria.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from analysis import mongo_aggregations as ma
from analysis.run_analisis_mongo import (
    EXPORTS_3,
    PIPELINE_ORDER,
    conteos,
    exportar_tres_csv,
    huella_resultados,
    run_all_estandar,
)


def _mongo_ok() -> bool:
    try:
        from storage.mongo import ping
        return ping() is True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _mongo_ok(), reason="sin Mongo local: skip separado")


def _leer_csv(ruta: Path) -> tuple[list[str], list[dict[str, str]]]:
    with ruta.open(newline="", encoding="utf-8-sig") as fh:
        lector = csv.DictReader(fh)
        assert lector.fieldnames is not None
        return list(lector.fieldnames), list(lector)


def test_orquestador_analisis_exporta_tres_conjuntos(tmp_path: Path) -> None:
    primera = run_all_estandar()
    assert list(primera) == list(PIPELINE_ORDER)
    assert len(primera) == 11
    rutas = exportar_tres_csv(primera, tmp_path)
    assert len(rutas) == 3
    assert sorted(rutas) == sorted(fichero for fichero, _ in EXPORTS_3)
    for ruta in rutas.values():
        assert ruta.exists()
        assert ruta.stat().st_size > 0
    # Reproducibilidad: segunda ejecucion, misma huella y mismo n.
    segunda = run_all_estandar()
    assert huella_resultados(primera) == huella_resultados(segunda)
    assert conteos(primera) == conteos(segunda)
    # Conteos medidos de la base real.
    n = conteos(primera)
    assert n["pipeline_indicadores_municipio"] == 252
    assert n["pipeline_alquiler_por_municipio"] == 252
    assert n["pipeline_modalidades"] == 2
    assert n["pipeline_vpo_terminadas"] == 251
    assert n["pipeline_tier_por_municipio"] == 252
    # Exportar la segunda ejecucion en otro directorio reproduce los conteos.
    tmp2 = tmp_path / "segunda"
    rutas2 = exportar_tres_csv(segunda, tmp2)
    for fichero, _nombre in EXPORTS_3:
        _cab, filas = _leer_csv(rutas2[fichero])
        assert len(filas) == n[dict(EXPORTS_3)[fichero]]


def test_preparacion_visualizacion_tres_conjuntos(tmp_path: Path) -> None:
    resultados = run_all_estandar()
    rutas = exportar_tres_csv(resultados, tmp_path)
    # Cabeceras: las del pipeline en memoria, sin valores tecleados.
    cab_esfuerzo, filas_esfuerzo = _leer_csv(
        rutas["mongo_esfuerzo_por_municipio.csv"]
    )
    cab_alquiler, filas_alquiler = _leer_csv(
        rutas["mongo_alquiler_por_municipio.csv"]
    )
    cab_modalidades, filas_modalidades = _leer_csv(rutas["mongo_modalidades.csv"])
    assert cab_esfuerzo == list(
        ma.pipeline_indicadores_municipio()[0].keys()
    ) or set(cab_esfuerzo) == set(
        ma.pipeline_indicadores_municipio()[0].keys()
    )
    assert set(cab_alquiler) == set(
        ma.pipeline_alquiler_por_municipio()[0].keys()
    )
    assert set(cab_modalidades) == set(ma.pipeline_modalidades()[0].keys())
    assert {
        "modalidad", "n", "precio_medio", "n_precio", "mediana_precio_eur",
        "n_eur_m2", "mediana_eur_m2",
    } <= set(cab_modalidades)
    # Coincidencia con los pipelines en memoria: conteos y una fila clave.
    assert len(filas_esfuerzo) == len(resultados["pipeline_indicadores_municipio"])
    assert len(filas_alquiler) == len(resultados["pipeline_alquiler_por_municipio"])
    assert len(filas_modalidades) == len(resultados["pipeline_modalidades"])
    assert len(filas_esfuerzo) == 252
    assert len(filas_alquiler) == 252
    assert len(filas_modalidades) == 2
    assert "esfuerzo_joven_pct" in cab_esfuerzo
    assert "cuantia_media" in cab_alquiler
    modalidades_memoria = {
        str(f["modalidad"]): str(f["n"])
        for f in resultados["pipeline_modalidades"]
    }
    assert {f["modalidad"]: f["n"] for f in filas_modalidades} == modalidades_memoria
    # Regenerar en un segundo directorio reproduce cabeceras y conteos.
    tmp2 = tmp_path / "re"
    rutas2 = exportar_tres_csv(resultados, tmp2)
    for fichero, _nombre in EXPORTS_3:
        cab1, filas1 = _leer_csv(rutas[fichero])
        cab2, filas2 = _leer_csv(rutas2[fichero])
        assert cab1 == cab2
        assert len(filas1) == len(filas2)
