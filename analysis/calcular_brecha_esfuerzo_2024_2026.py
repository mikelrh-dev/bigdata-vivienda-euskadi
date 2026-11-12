"""Calcula brecha de esfuerzo de mercado 2024 vs 2026 por municipio.

Lee:
  - data/procesado/dim_municipios_enriquecido.csv  (esfuerzo canonico 2024:
    esfuerzo_joven_pct_18_34, esfuerzo_joven_pct_16_29)
  - data/procesado/esfuerzo_mercado_2026.csv        (esfuerzo mercado 2026:
    esfuerzo_mercado_2026_pct_18_34, esfuerzo_mercado_2026_pct_16_29)

Hace inner join por codigo_ine y calcula:
  brecha_pp = esfuerzo_2026 - esfuerzo_2024
  direccion_cambio: "aumenta" / "disminuye" / "estable"

NO toca raw ni esfuerzo canonico 2024 (calcular_renta_joven.py, dim_municipios_enriquecido.csv).

Guarda:
    data/procesado/brecha_esfuerzo_2024_2026.csv

Uso:
    python analysis/calcular_brecha_esfuerzo_2024_2026.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC = PROJECT_ROOT / "data" / "procesado"

DIM = PROC / "dim_municipios_enriquecido.csv"
MERCADO_2026 = PROC / "esfuerzo_mercado_2026.csv"
OUT = PROC / "brecha_esfuerzo_2024_2026.csv"


def main() -> int:
    if not DIM.exists():
        print(f"Falta {DIM.name}.")
        return 1
    if not MERCADO_2026.exists():
        print(f"Falta {MERCADO_2026.name}. Ejecuta primero calcular_esfuerzo_mercado_2026.py")
        return 1

    dim = pd.read_csv(DIM, dtype=str, encoding="utf-8-sig")
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    dim = dim.rename(columns={
        "esfuerzo_joven_pct_18_34": "esfuerzo_2024_pct_18_34",
        "esfuerzo_joven_pct_16_29": "esfuerzo_2024_pct_16_29",
    })
    dim = dim[["codigo_ine", "nombre_canonico", "territorio",
               "esfuerzo_2024_pct_18_34", "esfuerzo_2024_pct_16_29"]].copy()

    m26 = pd.read_csv(MERCADO_2026, dtype=str, encoding="utf-8-sig")
    m26["codigo_ine"] = m26["codigo_ine"].astype(str).str.zfill(5)
    m26 = m26.rename(columns={
        "esfuerzo_mercado_2026_pct_18_34": "esfuerzo_2026_pct_18_34",
        "esfuerzo_mercado_2026_pct_16_29": "esfuerzo_2026_pct_16_29",
    })
    m26 = m26[["codigo_ine", "esfuerzo_2026_pct_18_34", "esfuerzo_2026_pct_16_29"]].copy()

    for col in ["esfuerzo_2024_pct_18_34", "esfuerzo_2024_pct_16_29"]:
        dim[col] = pd.to_numeric(dim[col], errors="coerce")
    for col in ["esfuerzo_2026_pct_18_34", "esfuerzo_2026_pct_16_29"]:
        m26[col] = pd.to_numeric(m26[col], errors="coerce")

    df = dim.merge(m26, on="codigo_ine", how="inner")

    # Solo municipios con datos en ambos (esfuerzo_2026 no nulo).
    df = df.dropna(subset=["esfuerzo_2026_pct_18_34", "esfuerzo_2026_pct_16_29"])

    df["brecha_pp_18_34"] = (df["esfuerzo_2026_pct_18_34"] - df["esfuerzo_2024_pct_18_34"]).round(2)
    df["brecha_pp_16_29"] = (df["esfuerzo_2026_pct_16_29"] - df["esfuerzo_2024_pct_16_29"]).round(2)

    def _direccion(v: float) -> str:
        if v > 0:
            return "aumenta"
        if v < 0:
            return "disminuye"
        return "estable"

    df["direccion_cambio"] = df["brecha_pp_18_34"].map(_direccion)
    df["vintage_numerador"] = 2026
    df["vintage_denominador"] = 2024

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df_out = df[[
        "codigo_ine", "nombre_canonico", "territorio",
        "esfuerzo_2024_pct_18_34", "esfuerzo_2024_pct_16_29",
        "esfuerzo_2026_pct_18_34", "esfuerzo_2026_pct_16_29",
        "brecha_pp_18_34", "brecha_pp_16_29", "direccion_cambio",
        "vintage_numerador", "vintage_denominador",
    ]].sort_values("codigo_ine").reset_index(drop=True)
    df_out.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"OK: {OUT.name} ({len(df_out)} municipios con datos en 2024 y 2026)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
