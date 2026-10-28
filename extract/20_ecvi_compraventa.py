"""Descarga las tablas de la Estadística de Compraventa de Inmuebles (ECVI)
del Observatorio Vasco de la Vivienda (Open Data Euskadi).

La página del dataset lista los enlaces XLSX disponibles (viviendas
trimestrales, cifras interanuales, otros inmuebles). El script:
  1. Scrapea la página para descubrir los enlaces .xlsx actuales.
  2. Descarga cada uno a data/raw/.
  3. Genera un CSV por hoja (sanitizado) para facilitar el análisis.

Salida: data/raw/ECVI_*.xlsx + data/raw/ecvi_*_{hoja}.csv
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import RAW_DIR, get_logger  # noqa: E402

log = get_logger("ecvi_compraventa")

PAGE_URL = (
    "https://observatoriovivienda.euskadi.eus/estadistica/"
    "tablas-estadisticas-estadistica-de-compraventa-de-inmuebles-ecvi/"
    "webovv00-content/es/"
)


def _descubrir_enlaces() -> list[str]:
    import requests

    r = requests.get(PAGE_URL, timeout=60)
    r.raise_for_status()
    links = set(re.findall(r'href="([^"]+\.xlsx)"', r.text))
    urls = [urljoin(PAGE_URL, l) for l in links]
    return sorted(urls)


def _sanitizar(nombre: str) -> str:
    import re as _re

    s = _re.sub(r"[^a-zA-Z0-9]+", "_", nombre).strip("_").lower()
    return s or "hoja"


def main() -> int:
    try:
        urls = _descubrir_enlaces()
    except Exception as exc:  # noqa: BLE001
        log.error("No se pudo scrapear la página ECVI: %s", exc)
        return 1
    if not urls:
        log.warning("No se encontraron enlaces XLSX en la página.")
        return 1
    log.info("Enlaces descubiertos: %d", len(urls))

    import requests

    for url in urls:
        nombre = url.split("/")[-1]
        destino = RAW_DIR / nombre
        log.info("Descargando %s ...", nombre)
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            destino.write_bytes(r.content)
            log.info("Guardado %s (%.1f KB)", destino.name, len(r.content) / 1024)
        except Exception as exc:  # noqa: BLE001
            log.error("Error descargando %s: %s", url, exc)
            continue

        # Intentar generar CSV por hoja
        try:
            import pandas as pd

            xl = pd.ExcelFile(destino, engine="openpyxl")
            for sheet in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet, header=None)
                csv_name = f"ecvi_{_sanitizar(nombre.replace('.xlsx',''))}_{_sanitizar(sheet)}.csv"
                csv_path = RAW_DIR / csv_name
                df.to_csv(csv_path, index=False, header=False, encoding="utf-8-sig")
                log.info("  hoja '%s' -> %s (%s)", sheet, csv_path.name, df.shape)
        except Exception as exc:  # noqa: BLE001
            log.warning("No se pudo parsear %s: %s", nombre, exc)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
