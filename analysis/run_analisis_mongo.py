"""Orquestador de analisis MongoDB: ejecuta los 8 pipelines y exporta 3 CSV.

Nivel 10 de Automatizacion del analisis (RETO 1Evaluacion SBD-BDAv2):
un script ejecuta todos los analisis principales y devuelve resultados
preparados para representacion, generados desde PyMongo sin valores
tecleados.

Uso:
  python analysis/run_analisis_mongo.py [--salida data/resultados]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bson.decimal128 import Decimal128

from analysis.mongo_aggregations import (
    pipeline_accesibilidad_extendida,
    pipeline_alquiler_por_municipio,
    pipeline_esfuerzo_por_sexo,
    pipeline_indicadores_municipio,
    pipeline_modalidades,
    pipeline_top_municipios_por_esfuerzo,
    pipeline_udalmap_extendido_osrm,
    pipeline_vpo_por_municipio,
)

RESULTADOS_DIR = ROOT / "data" / "resultados"

# Orden fijo de ejecucion de los 8 pipelines principales.
PIPELINE_ORDER: tuple[str, ...] = (
    "pipeline_indicadores_municipio",
    "pipeline_alquiler_por_municipio",
    "pipeline_modalidades",
    "pipeline_top_municipios_por_esfuerzo",
    "pipeline_esfuerzo_por_sexo",
    "pipeline_accesibilidad_extendida",
    "pipeline_udalmap_extendido_osrm",
    "pipeline_vpo_por_municipio",
)

# Los 3 conjuntos preparados para visualizacion: fichero -> pipeline origen.
EXPORTS_3: tuple[tuple[str, str], ...] = (
    ("mongo_esfuerzo_por_municipio.csv", "pipeline_indicadores_municipio"),
    ("mongo_alquiler_por_municipio.csv", "pipeline_alquiler_por_municipio"),
    ("mongo_modalidades.csv", "pipeline_modalidades"),
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal128):
        return str(value.to_decimal())
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def _clave_fila(fila: dict[str, Any]) -> str:
    return json.dumps(
        _jsonable(fila), sort_keys=True, default=str, ensure_ascii=False
    )


def _orden_canonico(filas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ordena filas por su serializacion ordenada (clave canonica).

    Varios pipelines usan `$sort` con una sola clave y MongoDB no garantiza
    el orden entre empates: sin este orden canonico, dos ejecuciones
    reproducibles darian huellas y CSV distintos en orden de filas.
    """
    return sorted(filas, key=_clave_fila)


def run_all_estandar() -> dict[str, list[dict[str, Any]]]:
    """Ejecuta en orden fijo los 8 pipelines de `mongo_aggregations`.

    Devuelve un dict con las 8 claves en el orden de `PIPELINE_ORDER` y
    filas en orden canonico (ver `_orden_canonico`), para que la huella y
    los CSV sean reproducibles entre ejecuciones.
    Las funciones se resuelven por nombre desde el espacio de nombres del
    modulo en tiempo de llamada, para que un test pueda sustituirlas con
    monkeypatch sin tocar MongoDB.
    """
    resultados: dict[str, list[dict[str, Any]]] = {}
    for nombre in PIPELINE_ORDER:
        funcion = globals()[nombre]
        resultados[nombre] = _orden_canonico(list(funcion()))
    return resultados


def huella_resultados(resultados: dict[str, list[dict[str, Any]]]) -> str:
    """SHA-256 hex de la serializacion ordenada de los resultados.

    `sort_keys=True` hace la huella independiente del orden de claves de
    MongoDB; dos ejecuciones reproducibles producen la misma huella.
    """
    texto = json.dumps(
        _jsonable(resultados), sort_keys=True, default=str, ensure_ascii=False
    )
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def conteos(resultados: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    """Numero de filas por pipeline."""
    return {nombre: len(filas) for nombre, filas in resultados.items()}


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, Decimal128):
        return str(value.to_decimal())
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, (dict, list)):
        return json.dumps(_jsonable(value), sort_keys=True, ensure_ascii=False)
    return value


def _cabecera(filas: list[dict[str, Any]]) -> list[str]:
    cabecera: list[str] = []
    vistos: set[str] = set()
    for fila in filas:
        for clave in fila:
            if clave not in vistos:
                vistos.add(clave)
                cabecera.append(clave)
    return cabecera


def exportar_tres_csv(
    resultados: dict[str, list[dict[str, Any]]],
    out_dir: Path | str,
) -> dict[str, Path]:
    """Escribe los 3 CSV preparados para visualizacion en `out_dir`.

    Sin valores tecleados: cada fila procede de los pipelines en memoria.
    Encoding `utf-8-sig`, cabecera = union de claves en orden de aparicion.
    Devuelve dict fichero -> ruta escrita.
    """
    destino = Path(out_dir)
    destino.mkdir(parents=True, exist_ok=True)
    rutas: dict[str, Path] = {}
    for fichero, nombre_pipeline in EXPORTS_3:
        filas = resultados[nombre_pipeline]
        ruta = destino / fichero
        cabecera = _cabecera(filas)
        with ruta.open("w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=cabecera,
                extrasaction="ignore",
                lineterminator="\n",
            )
            writer.writeheader()
            for fila in filas:
                writer.writerow(
                    {k: _csv_value(fila.get(k)) for k in cabecera}
                )
        rutas[fichero] = ruta
    return rutas


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Orquestador de analisis MongoDB: 8 pipelines + 3 CSV"
    )
    parser.add_argument(
        "--salida",
        default=str(RESULTADOS_DIR),
        help="Directorio de salida de los 3 CSV (defecto: data/resultados)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    primera = run_all_estandar()
    huella1 = huella_resultados(primera)
    segunda = run_all_estandar()
    huella2 = huella_resultados(segunda)
    n1 = conteos(primera)
    n2 = conteos(segunda)
    if huella1 != huella2 or n1 != n2:
        print(f"reproducibilidad: FALLA huella1={huella1} huella2={huella2}")
        print(f"n1={n1}")
        print(f"n2={n2}")
        return 1
    rutas = exportar_tres_csv(primera, Path(args.salida))
    for fichero, ruta in rutas.items():
        nombre_pipeline = dict(EXPORTS_3)[fichero]
        print(f"{fichero}: {len(primera[nombre_pipeline])} filas -> {ruta}")
    print(f"pipelines: {list(primera)}")
    print(f"n={n1}")
    print(f"huella: {huella1}")
    print("reproducibilidad: ok (dos ejecuciones con la misma huella)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
