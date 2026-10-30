"""Descarga de datos geográficos de municipios (b5m Gipuzkoa).

Fuentes:
  https://b5m.gipuzkoa.eus/api/2.0/datasets
  https://b5m.gipuzkoa.eus/datasets/GFA_DSET_MB.geojson
  https://b5m.gipuzkoa.eus/datasets/GFA_DSET_DISTM_CSV.zip

  - GFA_DSET_MB.geojson  → límites municipales con CODMUNIINE
  - GFA_DSET_DISTM_CSV.zip → distancias entre municipios (en km)

Nota: b5m solo cubre Gipuzkoa. Para Álava y Bizkaia, la lista de
municipios con su código INE se obtiene de Eustat (ver 01_eustat_api.py).

Uso:
  python extract/04_b5m_geo.py
"""

from __future__ import annotations

import csv
import io
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("b5m_geo")

DATASETS_API = "https://b5m.gipuzkoa.eus/api/2.0/datasets"
MUNICIPIOS_URL = "https://b5m.gipuzkoa.eus/datasets/GFA_DSET_MB.geojson"
DISTANCIAS_URL = "https://b5m.gipuzkoa.eus/datasets/GFA_DSET_DISTM_CSV.zip"


def main() -> int:
    cliente = Cliente("b5m_geo", delay=0.5)
    resumen = {}

    # 1. Catálogo de datasets (referencia de qué existe)
    try:
        catalogo = cliente.get(DATASETS_API).json()
        _docs = (
            catalogo.get("response", {}).get("docs", [])
            if isinstance(catalogo.get("response"), dict)
            else []
        )
        guardar_json(
            RAW_DIR / "b5m_catalogo.json",
            catalogo.get("response", catalogo),
            metadata={
                "fuente": "b5m Gipuzkoa (catalogo de datasets)",
                "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
                "url": DATASETS_API,
                "n_registros": len(_docs),
            },
        )
        resumen["catalogo"] = len(_docs)
    except Exception as exc:  # noqa: BLE001
        log.error("Catálogo: %s", exc)

    # 2. Límites municipales (GeoJSON)
    try:
        destino = cliente.descargar(MUNICIPIOS_URL, RAW_DIR / "municipios_gipuzkoa.geojson")
        geo = json.loads(destino.read_text(encoding="utf-8-sig"))
        propiedades = [
            f.get("properties", {}) for f in geo.get("features", [])
        ]
        codigos = {
            p.get("CODMUNIINE") for p in propiedades if p.get("CODMUNIINE")
        }
        log.info(
            "Municipios en el GeoJSON: %d (con código INE: %d)",
            len(propiedades), len(codigos),
        )
        guardar_json(
            RAW_DIR / "municipios_gipuzkoa_lista.json",
            [
                {
                    "nombre": p.get("NAME_ES") or p.get("NAME"),
                    "nombre_eu": p.get("NAME_EU"),
                    "codigo_ine": p.get("CODMUNIINE"),
                    "codigo_b5m": p.get("CODMUNI"),
                }
                for p in propiedades
            ],
            metadata={
                "fuente": "b5m Gipuzkoa (GFA_DSET_MB.geojson)",
                "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
                "url": MUNICIPIOS_URL,
                "n_registros": len(propiedades),
                "n_municipios": len(propiedades),
            },
        )
        resumen["municipios_gipuzkoa"] = len(propiedades)
    except Exception as exc:  # noqa: BLE001
        log.error("GeoJSON: %s", exc)

    # 3. Distancias entre municipios
    try:
        destino = cliente.descargar(
            DISTANCIAS_URL, RAW_DIR / "distancias_municipios.zip"
        )
        with zipfile.ZipFile(destino) as zf:
            nombre = zf.namelist()[0]
            texto = zf.read(nombre).decode("utf-8", errors="replace")
            filas = list(csv.DictReader(io.StringIO(texto), delimiter=","))
            guardar_json(
                RAW_DIR / "distancias_b5m_gipuzkoa.json",
                filas,
                metadata={
                    "fuente": "b5m Gipuzkoa (GFA_DSET_DISTM_CSV.zip)",
                    "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
                    "url": DISTANCIAS_URL,
                    "n_registros": len(filas),
                    "n_pares_total": len(filas),
                    "n_pares_guardados": len(filas),
                    "nota": "Distancias viarias reales Gipuzkoa (no truncado).",
                },
            )
            log.info("Pares de distancias: %d (guardados todos)", len(filas))
            resumen["pares_distancias"] = len(filas)
    except Exception as exc:  # noqa: BLE001
        log.error("Distancias: %s", exc)

    log.info("Resumen: %s", resumen)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
