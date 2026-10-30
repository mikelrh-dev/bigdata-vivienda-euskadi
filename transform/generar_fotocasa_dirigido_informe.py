#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""transform/generar_fotocasa_dirigido_informe.py

Genera data/procesado/fotocasa_dirigido_informe.csv (codigo_ine, municipio, n)
a partir de los raw data/raw/anuncios_fotocasa_dirigido_*.json (contando
anuncios por codigo_ine_forzado). Si no hay raw dirigido, genera filas con n=0
a partir de data/procesado/f4_pisos_objetivo.json (lista de objetivos).
Determinista, solo lectura de raw/procesado existente.
"""
from __future__ import annotations

import glob
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
PROC = os.path.join(BASE, "data", "procesado")


def main() -> int:
    dim_path = os.path.join(RAW, "dim_municipios.json")
    nombres = {}
    if os.path.exists(dim_path):
        dim = json.loads(open(dim_path, encoding="utf-8").read())
        regs = dim.get("datos", dim) if isinstance(dim, dict) else dim
        nombres = {r["codigo_ine"]: r["nombre_canonico"] for r in regs}

    # contar anuncios por codigo_ine_forzado desde raw dirigido
    counts: dict[str, int] = {}
    for path in sorted(glob.glob(os.path.join(RAW, "anuncios_fotocasa_dirigido_*.json"))):
        try:
            data = json.loads(open(path, encoding="utf-8").read())
        except Exception:
            continue
        anuncios = data.get("datos", data) if isinstance(data, dict) else data
        if not isinstance(anuncios, list):
            continue
        for a in anuncios:
            cod = a.get("codigo_ine_forzado") or a.get("codigo_ine")
            if cod:
                counts[cod] = counts.get(cod, 0) + 1

    # si no hay raw dirigido, usar lista de objetivos con n=0
    objetivos = []
    obj_path = os.path.join(PROC, "f4_pisos_objetivo.json")
    if os.path.exists(obj_path):
        try:
            objetivos = json.loads(open(obj_path, encoding="utf-8").read())
        except Exception:
            objetivos = []

    if not counts and objetivos:
        for cod in objetivos:
            counts.setdefault(cod, 0)
    elif objetivos:
        # asegurar que todos los objetivos aparezcan (n=0 si no hay raw dirigido)
        for cod in objetivos:
            counts.setdefault(cod, 0)

    # si no hay objetivos ni counts, vacio
    if not counts:
        print("[WARN] Sin raw dirigido ni objetivos; informe vacio")
        rows = []
    else:
        rows = [{"codigo_ine": cod, "municipio": nombres.get(cod, cod), "n": counts.get(cod, 0)}
                for cod in sorted(counts.keys())]

    out_path = os.path.join(PROC, "fotocasa_dirigido_informe.csv")
    import csv
    with open(out_path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["codigo_ine", "municipio", "n"])
        w.writeheader()
        w.writerows(rows)
    print(f"[OK] {out_path}: {len(rows)} filas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
