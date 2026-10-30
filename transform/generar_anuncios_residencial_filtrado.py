#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""transform/generar_anuncios_residencial_filtrado.py

Genera data/procesado/anuncios_vivienda_residencial_filtrado.csv a partir de
data/procesado/anuncios_vivienda_residencial.csv, aplicando el filtrado
heuristico de outliers (precio_m2, superficie, IQR por segmento) de
transform/filtrar_outliers.py. Determinista, solo lectura de silver.
"""
from __future__ import annotations

import os
import math
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(BASE, "data", "procesado")

PRECIO_M2_MIN = 3.0
PRECIO_M2_MAX = 50.0
SUPERFICIE_MIN = 10.0
SUPERFICIE_MAX = 500.0


def _precio_m2(row) -> float | None:
    try:
        p = float(row["precio_eur"])
        s = float(row["superficie_m2"])
    except (ValueError, TypeError):
        return None
    if s <= 0:
        return None
    return round(p / s, 2)


def main() -> int:
    src = os.path.join(PROC, "anuncios_vivienda_residencial.csv")
    if not os.path.exists(src):
        print(f"[ERROR] No existe {src}")
        return 1
    df = pd.read_csv(src, dtype=str, keep_default_na=False)
    # calcular precio_m2
    df["precio_m2_calculado"] = df.apply(_precio_m2, axis=1)

    # tipo_alquiler
    def _tipo(v):
        s = str(v).strip().lower()
        if s in ("true", "1", "temporal", "si", "sí"):
            return "temporal"
        return "larga_estancia"

    df["tipo_alquiler"] = df["alquiler_temporal"].map(_tipo) if "alquiler_temporal" in df.columns else "larga_estancia"

    # IQR por segmento
    limites = {}
    for seg, g in df.groupby("tipo_alquiler"):
        vals = pd.to_numeric(g["precio_m2_calculado"], errors="coerce").dropna().tolist()
        if len(vals) < 4:
            continue
        vals_sorted = sorted(vals)
        n = len(vals_sorted)
        q1 = vals_sorted[n // 4]
        q3 = vals_sorted[(3 * n) // 4]
        iqr = q3 - q1
        if iqr <= 0:
            continue
        limites[seg] = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)

    outliers = []
    motivos_list = []
    iqr_lower_list = []
    iqr_upper_list = []
    for _, row in df.iterrows():
        outlier = False
        motivos = []
        pm2 = row["precio_m2_calculado"]
        if pm2 is not None and pm2 != "":
            try:
                v = float(pm2)
                if v < PRECIO_M2_MIN:
                    outlier = True
                    motivos.append("precio_m2_bajo")
                if v > PRECIO_M2_MAX:
                    outlier = True
                    motivos.append("precio_m2_alto")
                lim = limites.get(row["tipo_alquiler"])
                if lim is not None:
                    lo, hi = lim
                    if v < lo:
                        outlier = True
                        motivos.append("precio_m2_iqr_bajo")
                    if v > hi:
                        outlier = True
                        motivos.append("precio_m2_iqr_alto")
            except (ValueError, TypeError):
                pass
        sup = row.get("superficie_m2", "")
        if sup not in ("", None):
            try:
                s = float(sup)
                if s < SUPERFICIE_MIN:
                    outlier = True
                    motivos.append("superficie_baja")
                if s > SUPERFICIE_MAX:
                    outlier = True
                    motivos.append("superficie_alta")
            except (ValueError, TypeError):
                pass
        outliers.append(bool(outlier))
        motivos_list.append(";".join(motivos))
        lim = limites.get(row["tipo_alquiler"])
        if lim is not None:
            iqr_lower_list.append(round(lim[0], 2))
            iqr_upper_list.append(round(lim[1], 2))
        else:
            iqr_lower_list.append("")
            iqr_upper_list.append("")

    df["outlier"] = outliers
    df["motivo_outlier"] = motivos_list
    df["iqr_lower"] = iqr_lower_list
    df["iqr_upper"] = iqr_upper_list

    # ordenar columnas como en el existente
    cols_existentes = [
        "portal", "modalidad", "codigo_ine", "municipio", "provincia",
        "precio_eur", "superficie_m2", "habitaciones", "banos",
        "alquiler_temporal", "es_outlier_superficie", "url_detalle", "titulo",
        "subtitulo", "precio_m2_calculado", "outlier", "motivo_outlier",
        "iqr_lower", "iqr_upper",
    ]
    # solo las que existan
    cols = [c for c in cols_existentes if c in df.columns]
    # añadir las que falten al final
    for c in df.columns:
        if c not in cols and c != "tipo_alquiler":
            cols.append(c)
    df = df[cols]

    out_path = os.path.join(PROC, "anuncios_vivienda_residencial_filtrado.csv")
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    n_out = sum(1 for o in outliers if o)
    print(f"[OK] {out_path}: {len(df)} filas, {n_out} outliers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
