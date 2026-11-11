"""Descarga un subconjunto de indicadores Udalmap de alto valor y los guarda en raw.

Indicadores seleccionados (id, nombre corto):
  123 accesibilidad_municipio
  150 tiempo_acceso_capital_th
   30 densidad_comercial_minorista
   38 deuda_viva_municipal_pc
   67 densidad_viviendas_suelo_residencial
   15 rotacion_contractual

Fuente: API Euskadi (https://api.euskadi.eus/udalmap/indicators/{id})
Genera:
  - data/raw/udalmap_extendido.csv
  - data/raw/udalmap_extendido.json
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("udalmap_extendido")

INDICADORES = {
    "123": "accesibilidad_municipio",
    "150": "tiempo_acceso_capital_th",
    "30": "densidad_comercial_minorista",
    "38": "deuda_viva_municipal_pc",
    "67": "densidad_viviendas_suelo_residencial",
    "15": "rotacion_contractual",
}
BASE = "https://api.euskadi.eus/udalmap/indicators/{}"
JSON_PATH = RAW_DIR / "udalmap_extendido.json"


def _ultimo_valor(years):
    if not years:
        return None
    # years is list of dict {year: value}
    # take last year with non-null
    for y in reversed(years):
        for k, v in y.items():
            if v is not None:
                return v, k
    return None, None


def main() -> int:
    cliente = Cliente("udalmap_extendido", delay=0.5)
    filas = []
    metadata_indicadores = {}
    for ind_id, short in INDICADORES.items():
        url = BASE.format(ind_id)
        resp = cliente.get(url)
        data = resp.json()
        metadata_indicadores[ind_id] = data.get("name")
        for m in data.get("municipalities", []):
            val, anio = _ultimo_valor(m.get("years", []))
            filas.append({
                "codigo_ine": str(m.get("id")).zfill(5),
                "municipio": m.get("name"),
                "indicador_id": ind_id,
                "indicador": short,
                "valor": val,
                "anio": anio,
            })

    # pivot a ancho por municipio
    pivot = {}
    for r in filas:
        ci = r["codigo_ine"]
        pivot.setdefault(ci, {"codigo_ine": ci, "municipio": r["municipio"]})
        pivot[ci][r["indicador"]] = r["valor"]
        pivot[ci][f"{r['indicador']}_anio"] = r["anio"]

    filas_salida = list(pivot.values())
    filas_salida.sort(key=lambda x: x["codigo_ine"])

    metadata = {
        "fuente": "Eustat Udalmap (API)",
        "url": "https://api.euskadi.eus/udalmap/indicators",
        "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
        "n_registros": len(filas_salida),
        "indicadores": INDICADORES,
        "nombres_api": metadata_indicadores,
    }
    guardar_json(JSON_PATH, filas_salida, metadata=metadata)
    log.info("JSON -> %s", JSON_PATH.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())