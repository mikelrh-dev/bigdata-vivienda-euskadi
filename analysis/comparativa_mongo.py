"""Comparativa de los 3 municipios mas robustos desde MongoDB.

CONCLUSION-01 (nivel 10 de Respuesta): comparar 3 municipios con conclusion
vinculada a indicadores calculados en Mongo. Solo 4 municipios tienen
n>=30 anuncios; aqui se toman los top 3 por n_anuncios con su esfuerzo
joven, precio medio, cuantia de alquiler y paro Lanbide. Ningun valor se
inventa: si falta, queda None.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from analysis.mongo_aggregations import pipeline_indicadores_municipio
from storage.mongo import get_collection

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "data" / "resultados" / "comparativa_3_municipios_mongo.csv"

COLUMNAS = [
    "codigo_ine",
    "nombre",
    "n_anuncios",
    "esfuerzo_joven_pct_18_34",
    "esfuerzo_joven_pct_16_29",
    "precio_medio_eur",
    "cuantia_alquiler_mes",
    "tasa_paro_lanbide_pct",
]


def _float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        try:
            return float(str(value))
        except (TypeError, ValueError):
            return None


def _paro_lanbide(codigo_ine: str) -> float | None:
    doc = get_collection("municipios").find_one(
        {"_id": codigo_ine}, {"empleo.tasa_paro_lanbide_pct": 1}
    )
    if not doc:
        return None
    empleo = doc.get("empleo") or {}
    return _float(empleo.get("tasa_paro_lanbide_pct"))


def comparativa_tres_robustos(
    min_n: int = 30,
    top_n: int = 3,
    output_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Top `top_n` municipios por n_anuncios con n>=`min_n`, con paro.

    Toma el orden de `pipeline_indicadores_municipio` (n_anuncios
    descendente), filtra n>=min_n, toma los primeros `top_n` y hace lookup
    de `empleo.tasa_paro_lanbide_pct` en `municipios` por codigo.
    """
    filas: list[dict[str, Any]] = []
    for doc in pipeline_indicadores_municipio():
        n = doc.get("n_anuncios")
        if n is None or int(n) < min_n:
            continue
        codigo = str(doc.get("_id"))
        filas.append(
            {
                "codigo_ine": codigo,
                "nombre": doc.get("nombre"),
                "n_anuncios": int(n),
                "esfuerzo_joven_pct_18_34": _float(doc.get("esfuerzo_joven_pct_18_34")),
                "esfuerzo_joven_pct_16_29": _float(
                    doc.get("esfuerzo_joven_pct_16_29", doc.get("esfuerzo_joven_pct"))
                ),
                "precio_medio_eur": _float(doc.get("precio_medio_eur")),
                "cuantia_alquiler_mes": _float(doc.get("cuantia_alquiler_mes")),
                "tasa_paro_lanbide_pct": _paro_lanbide(codigo),
            }
        )
        if len(filas) >= top_n:
            break
    if output_path is not None:
        escribir_csv(filas, Path(output_path))
    return filas


def escribir_csv(filas: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNAS)
        writer.writeheader()
        for fila in filas:
            writer.writerow(
                {
                    col: (
                        "" if fila.get(col) is None
                        else round(fila[col], 2) if isinstance(fila[col], float)
                        else fila[col]
                    )
                    for col in COLUMNAS
                }
            )


def main() -> int:
    filas = comparativa_tres_robustos(output_path=DEFAULT_CSV)
    for fila in filas:
        print(fila)
    print(f"csv: {DEFAULT_CSV} ({len(filas)} filas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
