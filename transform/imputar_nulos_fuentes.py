"""Imputa nulls en SERPAVI (renta_m2_mes_eur) por mediana de provincia -> regional.

Añade columnas:
  - serpavi_imputado (bool): True si el valor fue imputado
  - metodo_imputacion_serpavi: 'original' | 'provincia_mediana' | 'regional_mediana'

No modifica raw. Escribe data/procesado/serpavi_renta_imputado.csv (BOM).
"""
from __future__ import annotations
import os
import pandas as pd
import numpy as np

RAW = os.path.join("data", "raw")
OUT = os.path.join("data", "procesado")


def main():
    # Load SERPAVI raw
    df = pd.read_csv(os.path.join(RAW, "serpavi_renta_municipal.csv"), encoding="utf-8-sig")
    target = "renta_m2_mes_eur"

    # Ensure codigo_ine is string 5 digits
    df["codigo_ine"] = df["codigo_ine"].astype(str).str.strip().str.zfill(5)

    # Track original nulls
    null_mask = df[target].isna()
    df["serpavi_imputado"] = null_mask
    df["metodo_imputacion_serpavi"] = "original"

    # Impute by provincia_codigo median
    provincia_medians = df.groupby("provincia_codigo")[target].transform("median")
    regional_median = df[target].median()

    # Fill nulls with provincia median where available
    mask_prov = null_mask & provincia_medians.notna()
    df.loc[mask_prov, target] = provincia_medians[mask_prov]
    df.loc[mask_prov, "metodo_imputacion_serpavi"] = "provincia_mediana"

    # Remaining nulls -> regional median
    still_null = df[target].isna()
    df.loc[still_null, target] = regional_median
    df.loc[still_null, "metodo_imputacion_serpavi"] = "regional_mediana"

    # Also impute derived columns (p25, p75, anio, n_declaraciones) with same method flag
    for col in ["renta_m2_p25", "renta_m2_p75", "anio_renta", "n_declaraciones"]:
        if col in df.columns:
            col_null = df[col].isna()
            if col_null.any():
                col_prov_median = df.groupby("provincia_codigo")[col].transform("median")
                col_regional = df[col].median()
                m1 = col_null & col_prov_median.notna()
                df.loc[m1, col] = col_prov_median[m1]
                m2 = df[col].isna()
                df.loc[m2, col] = col_regional

    # Write output
    out_path = os.path.join(OUT, "serpavi_renta_imputado.csv")
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"SERPAVI imputado: {len(df)} filas")
    print(f"  Original nulls: {null_mask.sum()}")
    print(f"  Imputados provincia: {mask_prov.sum()}")
    print(f"  Imputados regional: {still_null.sum()}")
    print(f"  Nulls restantes: {df[target].isna().sum()}")
    print(f"  Regional median: {regional_median:.2f}")


if __name__ == "__main__":
    main()
