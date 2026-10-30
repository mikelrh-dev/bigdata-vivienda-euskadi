#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""transform/generar_cert_energetico_moda_municipio.py

Genera data/procesado/cert_energetico_moda_municipio.csv a partir de
data/procesado/cert_energetico_municipal_252.csv (columnas codigo_ine,
cert_energetico_moda). Determinista, solo lectura de silver existente.
"""
from __future__ import annotations

import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(BASE, "data", "procesado")


def main() -> int:
    src = os.path.join(PROC, "cert_energetico_municipal_252.csv")
    if not os.path.exists(src):
        print(f"[ERROR] No existe {src}; ejecuta generar_cert_energetico_municipal.py primero")
        return 1
    df = pd.read_csv(src, dtype=str)
    if "codigo_ine" not in df.columns or "cert_moda" not in df.columns:
        print("[ERROR] Columnas esperadas (codigo_ine, cert_moda) no encontradas")
        return 1
    out = df[["codigo_ine", "cert_moda"]].copy()
    out.columns = ["codigo_ine", "cert_energetico_moda"]
    out_path = os.path.join(PROC, "cert_energetico_moda_municipio.csv")
    out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[OK] {out_path}: {len(out)} filas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
