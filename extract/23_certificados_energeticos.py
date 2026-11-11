#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
extract/23_certificados_energeticos.py
Descarga certificados de eficiencia energética de Open Data Euskadi (3 territorios).
NO modifica ningún archivo existente en data/raw/.
Añade 3 CSVs nuevos: certificados_energeticos_{araba,bizkaia,gipuzkoa}.csv

Fuente: https://opendata.euskadi.eus/catalogo/-/registro-de-certificados-de-eficiencia-energetica-de-euskadi/
"""
import urllib.request
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import RAW_DIR  # noqa: E402

URLS = {
    "araba": "https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_araba.csv",
    "bizkaia": "https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_bizkaia.csv",
    "gipuzkoa": "https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_gipuzkoa.csv",
    "bilbao": "https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_bizkaia_bilbao.csv",
    "donostia": "https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_gipuzkoa_donostia.csv",
    "vitoria": "https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_araba_vitoria.csv",
}

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for territorio, url in URLS.items():
        dest = RAW_DIR / f"certificados_energeticos_{territorio}_completo.csv"
        print(f"[DESCARGA] {territorio} (completo) -> {dest}")
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"  OK: {dest.stat().st_size:,} bytes")
        except Exception as e:
            print(f"  ERROR: {e}")
            sys.exit(1)
    print("\n[OK] Descarga completada.")

if __name__ == "__main__":
    main()
