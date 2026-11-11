"""Descarga promociones de vivienda protegida (Etxebide) y las guarda en raw.

Fuente: Open Data Euskadi (CSV).
Genera:
  - data/raw/etxebide_promociones.csv
  - data/raw/etxebide_promociones.json
"""

from __future__ import annotations

import csv
import io
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, Cliente, get_logger, guardar_json  # noqa: E402

log = get_logger("etxebide_promociones")

URL = "https://opendata.euskadi.eus/contenidos/ds_localizaciones/promociones_etxebide/opendata/promociones.csv"
JSON_PATH = RAW_DIR / "etxebide_promociones.json"


def main() -> int:
    cliente = Cliente("etxebide_promociones", delay=1.0)
    resp = cliente.get(URL)
    texto = resp.content.decode("cp1252")

    reader = csv.DictReader(io.StringIO(texto, newline=""), delimiter=";")
    filas = list(reader)
    metadata = {
        "fuente": "Open Data Euskadi - Promociones Etxebide",
        "url": URL,
        "fecha_extraccion": datetime.now().isoformat(timespec="seconds"),
        "n_registros": len(filas),
        "columnas": reader.fieldnames or [],
    }
    guardar_json(JSON_PATH, filas, metadata=metadata)
    log.info("JSON -> %s (%d registros)", JSON_PATH.name, len(filas))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())