"""Calcula indice de tension social de demanda de vivienda (Etxebide + esfuerzo).

Lee data/procesado/dim_municipios_renta.csv y genera la tabla de features
de un solo escritor data/procesado/dim_municipios_tension.csv:
- etxebide_solicitudes_por_mil_2024
- tension_demanda_social (0-100)
- tension_categoria (baja/media/alta)

La tabla final la construye construir_dim_gold.py. No reescribir nunca
dim_municipios_enriquecido.csv desde aqui.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW = PROJECT_ROOT / "data" / "raw"
PROC = PROJECT_ROOT / "data" / "procesado"


def _percentil(series: pd.Series) -> pd.Series:
    return series.rank(pct=True) * 100


def main() -> int:
    dim = pd.read_csv(PROC / "dim_municipios_renta.csv", dtype=str, encoding="utf-8-sig")
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    etx = pd.read_csv(RAW / "etxebide_solicitudes.csv", dtype=str, encoding="utf-8-sig")
    # WP-10: anio leido como str; comparar como str.
    etx24 = etx[etx["anio"].astype(str) == "2024"][["codigo_ine", "etxebide_solicitudes_por_mil"]].copy()
    etx24 = etx24.rename(columns={"etxebide_solicitudes_por_mil": "etxebide_solicitudes_por_mil_2024"})
    etx24["codigo_ine"] = etx24["codigo_ine"].astype(str).str.zfill(5)
    # WP-10: lectura tipada como str; medidas a numerico explicito.
    etx24["etxebide_solicitudes_por_mil_2024"] = pd.to_numeric(
        etx24["etxebide_solicitudes_por_mil_2024"], errors="coerce")
    for _c in ["esfuerzo_joven_pct_18_34", "esfuerzo_max_pct"]:
        if _c in dim.columns:
            dim[_c] = pd.to_numeric(dim[_c], errors="coerce")

    # imputar nulo con mediana con flag explícito (INDICADORES-01: sin fillna silencioso)
    med = etx24["etxebide_solicitudes_por_mil_2024"].median()
    etx24["etx_imputado"] = etx24["etxebide_solicitudes_por_mil_2024"].isna()
    etx24["etxebide_solicitudes_por_mil_2024"] = etx24["etxebide_solicitudes_por_mil_2024"].fillna(med)

    dim = dim.merge(etx24, on="codigo_ine", how="left")
    dim["etx_imputado"] = dim["etxebide_solicitudes_por_mil_2024"].isna()
    dim["etxebide_solicitudes_por_mil_2024"] = dim["etxebide_solicitudes_por_mil_2024"].fillna(med)

    # percentiles
    # Esfuerzo canonico 18-34 (NO el legacy 16-29, que es un denominador distinto).
    # esfuerzo_ovj_referencia_pct usa un denominador autonomico constante y
    # solo refleja diferencias de alquiler, no de renta: no se usa aqui.
    # Fallback fiscal (mismo numerador, ratio CAE) donde el municipal falta.
    dim["esf_fallback"] = dim["esfuerzo_joven_pct_18_34"].isna()
    esf = dim["esfuerzo_joven_pct_18_34"].fillna(dim["esfuerzo_max_pct"])
    n_fb = int(dim["esf_fallback"].sum())
    print(f"esfuerzo canonico: {int(esf.notna().sum())} mun., fallback fiscal: {n_fb}")
    p_sol = _percentil(dim["etxebide_solicitudes_por_mil_2024"])
    p_esf = _percentil(esf)
    dim["tension_demanda_social"] = ((p_sol + p_esf) / 2).round(1)

    def cat(v):
        if v < 33:
            return "baja"
        if v < 66:
            return "media"
        return "alta"

    dim["tension_categoria"] = dim["tension_demanda_social"].map(cat)

    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    tension = dim[["codigo_ine", "etxebide_solicitudes_por_mil_2024",
                   "tension_demanda_social", "tension_categoria",
                   "etx_imputado", "esf_fallback"]].copy()
    out_path = PROC / "dim_municipios_tension.csv"
    tension.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"OK: {out_path} ({len(dim)} filas, {len(dim.columns)} cols)")
    print(dim["tension_categoria"].value_counts().to_string())
    print(f"tension media={dim['tension_demanda_social'].median():.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
