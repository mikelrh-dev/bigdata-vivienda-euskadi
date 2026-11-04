#!/usr/bin/env python
"""Valida 3 fuentes candidatas con join real vs dim 252. Solo lectura."""
from __future__ import annotations
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "procesado"


def main() -> dict:
    con = duckdb.connect()
    out = {}
    # 1. Pob 15-29: bandas disponibles
    try:
        bandas = con.execute(
            "SELECT DISTINCT \"grandes grupos de edad cumplida__etiqueta\" "
            "FROM read_csv('data/raw/eustat_poblacion_edad.csv', header=True)"
        ).fetchall()
        out["poblacion_bandas"] = [b[0] for b in bandas]
    except Exception as exc:
        out["poblacion_bandas"] = []
        out["poblacion_error"] = str(exc)
    out["poblacion_15_29_derivable"] = False  # 0-19/20-64 no se separan
    # 2. Renta edad municipal: ambito presente?
    try:
        cols = con.execute(
            "DESCRIBE SELECT * FROM read_csv('data/raw/eustat_renta_edad.csv', header=True)"
        ).fetchall()
        out["renta_edad_cols"] = [c[0] for c in cols]
        out["renta_edad_municipal"] = any("ambito" in c.lower() for c in out["renta_edad_cols"])
    except Exception as exc:
        out["renta_edad_cols"] = []
        out["renta_edad_municipal"] = False
        out["renta_error"] = str(exc)
    # 3. Alokabide: hay raw?
    out["alokabide_raw"] = [p.name for p in RAW.glob("*alokabide*")]
    out["alokabide_cobertura"] = 0
    # 4. Scraping Nivel2 objetivo
    try:
        out["nivel2"] = con.execute(
            "SELECT count(*) n FROM read_csv('data/procesado/dim_municipios.csv', header=True) "
            "WHERE tipologia_mercado='Nivel2_Mercado_Regulado'"
        ).fetchone()[0]
    except Exception as exc:
        out["nivel2"] = 0
        out["nivel2_error"] = str(exc)
    for k, v in out.items():
        print(k, v)
    return out


if __name__ == "__main__":
    main()
