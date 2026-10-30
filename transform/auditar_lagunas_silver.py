"""Auditoría de lagunas (nulos/cobertura) de los CSV silver.

Genera data/resultados/auditoria_lagunas_silver.csv con, por cada CSV curado:
filas, nulos por columna vital, cobertura municipal sobre 252 (solo archivos
con codigo_ine) y min/max/mediana de superficie y precio (mapeando nombres
inconsistentes; N/A cuando no aplica).
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = ROOT / "data" / "procesado"
OUT_DIR = ROOT / "data" / "resultados"
OUT_FILE = OUT_DIR / "auditoria_lagunas_silver.csv"

MUNS_TOTAL = 252

# CSVs silver considerados vitales (curados). Se auditan todos los CSV del dir
# procesado (silver) para no dejar lagunas sin detectar.
CURATED_VITAL_CSVS = sorted(p.name for p in CSV_DIR.glob("*.csv"))

SUPERFICIE_CANDIDATES = [
    "superficie_m2",
    "superficie_media_m2",
    "superficie_media_m2_media",
    "superficie_media_m2_mediana",
    "superficie_media_m2_p25",
    "superficie_media_m2_p75",
]

PRECIO_CANDIDATES = [
    "precio_eur",
    "precio_medio_total_eur",
    "precio_medio_eur",
    "cuantia_media_eur_mes_media",
    "cuantia_media_eur_mes_mediana",
]


def pick_column(columns: list[str], candidates: list[str]) -> str | None:
    colset = set(columns)
    for c in candidates:
        if c in colset:
            return c
    # fallback: primera columna que contenga la palabra clave
    for c in columns:
        low = c.lower()
        if "superficie" in low:
            return c
    return None


def pick_precio(columns: list[str]) -> str | None:
    colset = set(columns)
    for c in PRECIO_CANDIDATES:
        if c in colset:
            return c
    for c in columns:
        low = c.lower()
        if "precio" in low and "m2" not in low:
            return c
    return None


def stats_series(df: pd.DataFrame, col: str | None) -> tuple[str, str, str]:
    if col is None or col not in df.columns:
        return "N/A", "N/A", "N/A"
    s = pd.to_numeric(df[col], errors="coerce")
    s = pd.Series(s).dropna()
    if s.empty:
        return "N/A", "N/A", "N/A"
    return f"{s.min():.2f}", f"{s.max():.2f}", f"{s.median():.2f}"


def nulls_por_columna(df: pd.DataFrame) -> str:
    partes = []
    for col in df.columns:
        n = int(df[col].isna().sum())
        # contar también strings vacíos / 'N/A' literales
        if df[col].dtype == object:
            vacios = int((df[col].astype(str).str.strip().isin(["", "N/A", "n/a", "NA", "NaN", "nan", "None"])).sum())
            n = max(n, vacios)
        if n > 0:
            partes.append(f"{col}={n}")
    return "; ".join(partes) if partes else "sin_nulos"


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    filas_out = []
    for nombre in CURATED_VITAL_CSVS:
        ruta = CSV_DIR / nombre
        try:
            df = pd.read_csv(ruta, encoding="utf-8-sig")
        except Exception as exc:  # noqa: BLE001
            filas_out.append({
                "archivo": nombre,
                "filas": 0,
                "columnas_total": 0,
                "nulos_por_columna_vital": f"ERROR_LECTURA={exc}",
                "nulos_vitales_total": 0,
                "tiene_codigo_ine": "no",
                "municipios_unicos": 0,
                "cobertura_municipios_pct": "N/A",
                "superficie_col": "N/A",
                "superficie_min": "N/A",
                "superficie_max": "N/A",
                "superficie_mediana": "N/A",
                "precio_col": "N/A",
                "precio_min": "N/A",
                "precio_max": "N/A",
                "precio_mediana": "N/A",
            })
            continue

        tiene_ci = "codigo_ine" in df.columns
        if tiene_ci:
            muns = int(df["codigo_ine"].dropna().astype(str).str.strip().nunique())
            cov = round(100.0 * muns / MUNS_TOTAL, 2)
            cov_str = f"{cov:.2f}"
        else:
            muns = 0
            cov_str = "N/A"

        sup_col = pick_column(list(df.columns), SUPERFICIE_CANDIDATES)
        # asegurar que sea superficie y no otra cosa
        if sup_col is None:
            for c in df.columns:
                if "superficie" in c.lower():
                    sup_col = c
                    break
        precio_col = pick_precio(list(df.columns))

        smin, smax, smed = stats_series(df, sup_col)
        pmin, pmax, pmed = stats_series(df, precio_col)

        nulos_total = 0
        for col in df.columns:
            n = int(df[col].isna().sum())
            if df[col].dtype == object:
                vacios = int((df[col].astype(str).str.strip().isin(["", "N/A", "n/a", "NA", "NaN", "nan", "None"])).sum())
                n = max(n, vacios)
            nulos_total += n

        filas_out.append({
            "archivo": nombre,
            "filas": int(len(df)),
            "columnas_total": int(len(df.columns)),
            "nulos_por_columna_vital": nulls_por_columna(df),
            "nulos_vitales_total": nulos_total,
            "tiene_codigo_ine": "si" if tiene_ci else "no",
            "municipios_unicos": muns,
            "cobertura_municipios_pct": cov_str,
            "superficie_col": sup_col if sup_col else "N/A",
            "superficie_min": smin,
            "superficie_max": smax,
            "superficie_mediana": smed,
            "precio_col": precio_col if precio_col else "N/A",
            "precio_min": pmin,
            "precio_max": pmax,
            "precio_mediana": pmed,
        })

    out_df = pd.DataFrame(filas_out)
    out_df.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")
    print(f"CSVs auditados: {len(filas_out)}")
    print(f"Salida: {OUT_FILE}")


if __name__ == "__main__":
    main()
