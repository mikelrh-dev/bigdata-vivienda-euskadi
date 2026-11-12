"""Compara esfuerzo 2024 y 2026 con el mismo denominador y la misma muestra.

El titular 26,61 % (2024) vs 79,3 % (2026) mezcla tres cosas: numerador
(alquiler registrado vs precio de oferta), denominador (renta joven estimada vs
salario neto) y muestra (159 vs 50 municipios). Este paso aisla cada una:

  - esfuerzo_2024_canonico: la cifra oficial y publicada, sin tocar.
  - esfuerzo_2024_base_salario: alquiler oficial 2024 sobre salario OVJ 2024.
  - esfuerzo_2026_base_salario: anuncio 2026 sobre salario OVJ 2024 x IPC.
  - esfuerzo_2026_base_renta2024: anuncio 2026 sobre renta joven 2024 (el
    denominador canonico), para medir cuanto del salto es solo denominador.

Lee:
  - data/procesado/dim_municipios_enriquecido.csv
  - data/procesado/esfuerzo_mercado_2026.csv

Guarda:
  - data/resultados/comparacion_esfuerzo_2024_2026.csv       (por municipio)
  - data/resultados/comparacion_esfuerzo_2024_2026_resumen.csv (medianas)

NO modifica el esfuerzo canonico ni raw.

Uso:
    python analysis/comparar_esfuerzo_2024_2026_misma_base.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROC = PROJECT_ROOT / "data" / "procesado"
RES = PROJECT_ROOT / "data" / "resultados"

DIM = PROC / "dim_municipios_enriquecido.csv"
MERCADO_2026 = PROC / "esfuerzo_mercado_2026.csv"
# Capa de analisis (gold), no silver.
OUT = RES / "comparacion_esfuerzo_2024_2026.csv"
OUT_RESUMEN = RES / "comparacion_esfuerzo_2024_2026_resumen.csv"

SALARIO_18_34_2024 = 1564.0  # OVJ, neto mensual


def main() -> int:
    for ruta in (DIM, MERCADO_2026):
        if not ruta.exists():
            print(f"Falta {ruta.name}.")
            return 1

    dim = pd.read_csv(DIM, dtype=str, encoding="utf-8-sig")
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    for col in ["esfuerzo_joven_pct_18_34", "cuantia_media_eur_mes_mediana",
                "renta_joven_estimada_18_34"]:
        dim[col] = pd.to_numeric(dim.get(col), errors="coerce")

    m26 = pd.read_csv(MERCADO_2026, dtype=str, encoding="utf-8-sig")
    m26["codigo_ine"] = m26["codigo_ine"].astype(str).str.zfill(5)
    for col in ["n_anuncios_2026", "precio_mediana_anuncio_2026_eur_mes",
                "esfuerzo_mercado_2026_pct_18_34",
                "esfuerzo_renta_joven_2024_pct_18_34"]:
        m26[col] = pd.to_numeric(m26.get(col), errors="coerce")

    df = dim[[
        "codigo_ine", "nombre_canonico", "territorio",
        "esfuerzo_joven_pct_18_34", "cuantia_media_eur_mes_mediana",
        "renta_joven_estimada_18_34",
    ]].merge(
        m26[[
            "codigo_ine", "n_anuncios_2026", "precio_mediana_anuncio_2026_eur_mes",
            "esfuerzo_mercado_2026_pct_18_34", "esfuerzo_renta_joven_2024_pct_18_34",
        ]],
        on="codigo_ine", how="inner",
    )

    # Solo municipios con dato 2026: la comparacion justa se hace sobre esa muestra.
    df = df[df["esfuerzo_mercado_2026_pct_18_34"].notna()].copy()

    df["esfuerzo_2024_base_salario_pct_18_34"] = (
        df["cuantia_media_eur_mes_mediana"] / SALARIO_18_34_2024 * 100
    ).round(2)
    df["esfuerzo_2024_canonico_pct_18_34"] = df["esfuerzo_joven_pct_18_34"].round(2)
    df["esfuerzo_2026_base_salario_pct_18_34"] = df["esfuerzo_mercado_2026_pct_18_34"]
    df["esfuerzo_2026_base_renta2024_pct_18_34"] = df[
        "esfuerzo_renta_joven_2024_pct_18_34"]

    df["delta_pp_misma_base"] = (
        df["esfuerzo_2026_base_salario_pct_18_34"]
        - df["esfuerzo_2024_base_salario_pct_18_34"]
    ).round(2)
    df["ratio_2026_2024_misma_base"] = (
        df["esfuerzo_2026_base_salario_pct_18_34"]
        / df["esfuerzo_2024_base_salario_pct_18_34"]
    ).round(3)
    df["efecto_denominador_pp"] = (
        df["esfuerzo_2026_base_salario_pct_18_34"]
        - df["esfuerzo_2026_base_renta2024_pct_18_34"]
    ).round(2)
    df["efecto_nivel_precio_pp"] = (
        df["esfuerzo_2026_base_renta2024_pct_18_34"]
        - df["esfuerzo_2024_canonico_pct_18_34"]
    ).round(2)

    cols = [
        "codigo_ine", "nombre_canonico", "territorio", "n_anuncios_2026",
        "cuantia_media_eur_mes_mediana", "precio_mediana_anuncio_2026_eur_mes",
        "esfuerzo_2024_canonico_pct_18_34", "esfuerzo_2024_base_salario_pct_18_34",
        "esfuerzo_2026_base_salario_pct_18_34",
        "esfuerzo_2026_base_renta2024_pct_18_34",
        "delta_pp_misma_base", "ratio_2026_2024_misma_base",
        "efecto_denominador_pp", "efecto_nivel_precio_pp",
    ]
    out = df[cols].sort_values(
        "esfuerzo_2026_base_salario_pct_18_34", ascending=False
    ).reset_index(drop=True)

    resumen = pd.DataFrame([
        {"metrica": "esfuerzo_2024_canonico_pct_18_34",
         "descripcion": "oficial publicado: alquiler registrado / renta joven",
         "mediana": round(float(out["esfuerzo_2024_canonico_pct_18_34"].median()), 2)},
        {"metrica": "esfuerzo_2024_base_salario_pct_18_34",
         "descripcion": "alquiler registrado 2024 / salario OVJ 2024",
         "mediana": round(float(out["esfuerzo_2024_base_salario_pct_18_34"].median()), 2)},
        {"metrica": "esfuerzo_2026_base_salario_pct_18_34",
         "descripcion": "anuncio 2026 / salario OVJ 2024 x IPC",
         "mediana": round(float(out["esfuerzo_2026_base_salario_pct_18_34"].median()), 2)},
        {"metrica": "esfuerzo_2026_base_renta2024_pct_18_34",
         "descripcion": "anuncio 2026 / renta joven 2024 (denominador canonico)",
         "mediana": round(float(out["esfuerzo_2026_base_renta2024_pct_18_34"].median()), 2)},
    ])
    resumen["n_municipios"] = len(out)
    resumen["n_anuncios"] = int(out["n_anuncios_2026"].sum())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    resumen.to_csv(OUT_RESUMEN, index=False, encoding="utf-8-sig")

    print(f"OK: {OUT.name} ({len(out)} municipios, {int(out['n_anuncios_2026'].sum())} anuncios)")
    print(resumen[["metrica", "mediana"]].to_string(index=False))
    print(f"OK: {OUT_RESUMEN.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
