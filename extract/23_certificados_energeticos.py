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
import os
import sys

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")

URLS = {
    "araba": "https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_araba.csv",
    "bizkaia": "https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_bizkaia.csv",
    "gipuzkoa": "https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_gipuzkoa.csv",
    "bilbao": "https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_bizkaia_bilbao.csv",
    "donostia": "https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_gipuzkoa_donostia.csv",
    "vitoria": "https://opendata.euskadi.eus/contenidos/ds_registros/certificados_eficie_energetica/opendata/certificados_araba_vitoria.csv",
}

def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    for territorio, url in URLS.items():
        dest = os.path.join(RAW_DIR, f"certificados_energeticos_{territorio}_completo.csv")
        if os.path.exists(dest):
            print(f"[SKIP] {dest} ya existe (no se sobrescribe)")
            continue
        print(f"[DESCARGA] {territorio} (completo) -> {dest}")
        try:
            urllib.request.urlretrieve(url, dest)
            size = os.path.getsize(dest)
            print(f"  OK: {size:,} bytes")
        except Exception as e:
            print(f"  ERROR: {e}")
            sys.exit(1)
    print("\n[OK] Descarga completada.")

if __name__ == "__main__":
    main()
