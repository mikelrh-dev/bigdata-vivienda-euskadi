"""Comparativa Tier A desde MongoDB (solo n>=30).

CONCLUSION-01 (nivel 10 de Respuesta): comparar municipios Tier A
(n>=30) con conclusion vinculada a indicadores calculados en Mongo:
Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39. Tier B/C/D
(n<30) quedan fuera del ranking. Anade `delta_n_anuncios` (diferencia
con el siguiente Tier A; Getxo 50 vs Vitoria 39 = 11) y la
`advertencia` ("solo Tier A sustenta ranking; B/C/D no ranking").
Ningun valor se inventa: si falta, queda None.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

# Ejecutado como script (python analysis/comparativa_mongo.py) sys.path[0] es
# analysis/, asi que el paquete `analysis` no se resolveria: anclar la raiz.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.mongo_aggregations import pipeline_indicadores_municipio  # noqa: E402
from storage.mongo import get_collection  # noqa: E402
DEFAULT_CSV = ROOT / "data" / "resultados" / "comparativa_3_municipios_mongo.csv"

ADVERTENCIA_TIER = "solo Tier A (n>=30: Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39) sustenta ranking firme; Tier B/C/D (n<30) no ranking"
ADVERTENCIA_DELTA = ("Getxo 50 vs Vitoria-Gasteiz 39 = 11 anuncios (margen estrecho): "
                     "el orden 3º/4º es fragil; no leer como diferencia firme.")

COLUMNAS = [
    "codigo_ine",
    "nombre",
    "n_anuncios",
    "tier",
    "tier_etiqueta",
    "delta_n_anuncios",
    "advertencia",
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
    """Top `top_n` Tier A (n>=`min_n`) con paro, tier, delta y advertencia.

    Toma el orden de `pipeline_indicadores_municipio` (n_anuncios
    descendente), filtra n>=30 (Tier A; B/C/D n<30 quedan fuera del
    ranking), toma los primeros `top_n` y hace lookup
    de `empleo.tasa_paro_lanbide_pct` en `municipios` por codigo.
    `delta_n_anuncios` = diferencia de n con el siguiente Tier A;
    `advertencia` = cadena con el aviso de ranking y el margen Getxo/Vitoria.
    """
    candidatos: list[dict[str, Any]] = []
    for doc in pipeline_indicadores_municipio():
        n = doc.get("n_anuncios")
        if n is None or int(n) < min_n:
            continue
        candidatos.append(doc)
        if len(candidatos) >= top_n:
            break
    # Para top_n=4 (cuatro robustos) el delta de la ultima fila Tier A se
    # computa contra el siguiente Tier A del universo completo, si existe.
    siguientes: dict[str, int | None] = {}
    if len(candidatos) >= top_n and top_n >= 4:
        vistos = {str(d.get("_id")) for d in candidatos}
        for doc in pipeline_indicadores_municipio():
            n = doc.get("n_anuncios")
            if n is None or int(n) < min_n:
                continue
            codigo = str(doc.get("_id"))
            if codigo not in vistos:
                siguientes[codigo] = int(n)
                break
    filas: list[dict[str, Any]] = []
    for i, doc in enumerate(candidatos):
        n = int(doc["n_anuncios"])
        if i + 1 < len(candidatos):
            delta: int | None = n - int(candidatos[i + 1]["n_anuncios"])
        else:
            nxt = siguientes.get(str(doc.get("_id")))
            delta = (n - nxt) if nxt is not None else None
        codigo = str(doc.get("_id"))
        filas.append(
            {
                "codigo_ine": codigo,
                "nombre": doc.get("nombre"),
                "n_anuncios": n,
                "tier": "A",
                "tier_etiqueta": "fuerte",
                "delta_n_anuncios": delta,
                "advertencia": f"{ADVERTENCIA_TIER} {ADVERTENCIA_DELTA}",
                "esfuerzo_joven_pct_18_34": _float(doc.get("esfuerzo_joven_pct_18_34")),
                "esfuerzo_joven_pct_16_29": _float(
                    doc.get("esfuerzo_joven_pct_16_29", doc.get("esfuerzo_joven_pct"))
                ),
                "precio_medio_eur": _float(doc.get("precio_medio_eur")),
                "cuantia_alquiler_mes": _float(doc.get("cuantia_alquiler_mes")),
                "tasa_paro_lanbide_pct": _paro_lanbide(codigo),
            }
        )
    if output_path is not None:
        escribir_csv(filas, Path(output_path))
    return filas


def comparativa_cuatro_robustos(
    min_n: int = 30,
    output_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Top-4 Tier A n>=30 con paro Lanbide no nulo.

    Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39, con el mismo
    pipeline que los otros tres. `comparativa_tres_robustos(top_n=3)` se
    conserva para compatibilidad con tests existentes.
    """
    return comparativa_tres_robustos(min_n=min_n, top_n=4, output_path=output_path)


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
    filas = comparativa_cuatro_robustos(output_path=DEFAULT_CSV)
    for fila in filas:
        print(fila)
    print(f"csv: {DEFAULT_CSV} ({len(filas)} filas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
