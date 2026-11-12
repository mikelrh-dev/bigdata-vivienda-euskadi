"""Calcula la diferencia de esfuerzo 2024 (oficial) vs 2026 (oferta).

Lee:
  - data/procesado/dim_municipios_enriquecido.csv  (esfuerzo canonico 2024:
    esfuerzo_joven_pct_18_34, esfuerzo_joven_pct_16_29; renta joven 2024)
  - data/procesado/esfuerzo_mercado_2026.csv        (esfuerzo mercado 2026)
  - data/resultados/premium_oferta_2026.csv         (k oferta/registrado)

Calcula:
  - brecha_pp = esfuerzo_2026 - esfuerzo_2024 (diferencia de NIVEL, no variacion
    temporal: numerador y denominador no son el mismo concepto)
  - esfuerzo_equivalente_2026_pct_18_34: anuncio 2026 x k (equivalente oficial)
    sobre renta joven 2024, es decir el mismo concepto que el canonico. Permite
    una comparacion homogenea y declarada.
  - metadatos de trazabilidad: tipo_diferencia, k_aplicado, origen_k, ratio, IC.

NO toca raw ni el esfuerzo canonico 2024.

Guarda:
    data/resultados/brecha_esfuerzo_2024_2026.csv

Uso:
    python analysis/calcular_brecha_esfuerzo_2024_2026.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROC = PROJECT_ROOT / "data" / "procesado"

DIM = PROC / "dim_municipios_enriquecido.csv"
MERCADO_2026 = PROC / "esfuerzo_mercado_2026.csv"
PREMIUM = PROJECT_ROOT / "data" / "resultados" / "premium_oferta_2026.csv"
OUT = PROJECT_ROOT / "data" / "resultados" / "brecha_esfuerzo_2024_2026.csv"

CAVEAT = (
    "diferencia de nivel entre alquiler registrado 2024 y precio de oferta 2026; "
    "no es una variacion temporal. Con k municipal el equivalente calibrado es "
    "identico por construccion: no identifica cambio 2024-2026"
)


def main() -> int:
    for ruta in (DIM, MERCADO_2026):
        if not ruta.exists():
            print(f"Falta {ruta.name}.")
            return 1
    if not PREMIUM.exists():
        print(f"Falta {PREMIUM.name}. Ejecuta primero analysis/calibrar_premium_oferta.py")
        return 1

    dim = pd.read_csv(DIM, dtype=str, encoding="utf-8-sig")
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    dim = dim.rename(columns={
        "esfuerzo_joven_pct_18_34": "esfuerzo_2024_pct_18_34",
        "esfuerzo_joven_pct_16_29": "esfuerzo_2024_pct_16_29",
    })
    for col in ["esfuerzo_2024_pct_18_34", "esfuerzo_2024_pct_16_29",
                "renta_joven_estimada_18_34", "cuantia_media_eur_mes_mediana"]:
        dim[col] = pd.to_numeric(dim.get(col), errors="coerce")
    dim = dim[[
        "codigo_ine", "nombre_canonico", "territorio",
        "esfuerzo_2024_pct_18_34", "esfuerzo_2024_pct_16_29",
        "renta_joven_estimada_18_34", "cuantia_media_eur_mes_mediana",
    ]].copy()

    m26 = pd.read_csv(MERCADO_2026, dtype=str, encoding="utf-8-sig")
    m26["codigo_ine"] = m26["codigo_ine"].astype(str).str.zfill(5)
    m26 = m26.rename(columns={
        "esfuerzo_mercado_2026_pct_18_34": "esfuerzo_2026_pct_18_34",
        "esfuerzo_mercado_2026_pct_16_29": "esfuerzo_2026_pct_16_29",
    })
    for col in ["esfuerzo_2026_pct_18_34", "esfuerzo_2026_pct_16_29",
                "n_anuncios_2026", "precio_mediana_anuncio_2026_eur_mes",
                "mediana_m2_winsorizada_2026_eur_m2",
                "ic95_lo_pct_18_34", "ic95_hi_pct_18_34",
                "esfuerzo_sin_ajuste_pct_18_34"]:
        m26[col] = pd.to_numeric(m26.get(col), errors="coerce")
    m26 = m26[[
        "codigo_ine", "n_anuncios_2026", "precio_mediana_anuncio_2026_eur_mes",
        "mediana_m2_winsorizada_2026_eur_m2", "esfuerzo_2026_pct_18_34",
        "esfuerzo_2026_pct_16_29", "ic95_lo_pct_18_34", "ic95_hi_pct_18_34",
        "esfuerzo_sin_ajuste_pct_18_34",
    ]].copy()

    prem = pd.read_csv(PREMIUM, dtype=str, encoding="utf-8-sig")
    prem["codigo_ine"] = prem["codigo_ine"].astype(str).str.zfill(5)
    for col in ["k_aplicado", "k_m2_municipal"]:
        prem[col] = pd.to_numeric(prem.get(col), errors="coerce")
    prem = prem[[
        "codigo_ine", "k_aplicado", "origen_k", "alquiler_equivalente_2026_eur_mes",
    ]].copy()
    prem["alquiler_equivalente_2026_eur_mes"] = pd.to_numeric(
        prem["alquiler_equivalente_2026_eur_mes"], errors="coerce")

    df = dim.merge(m26, on="codigo_ine", how="inner").merge(prem, on="codigo_ine", how="left")

    # Solo municipios con datos en ambos (esfuerzo_2026 no nulo).
    df = df.dropna(subset=["esfuerzo_2026_pct_18_34", "esfuerzo_2026_pct_16_29"]).copy()

    df["brecha_pp_18_34"] = (df["esfuerzo_2026_pct_18_34"] - df["esfuerzo_2024_pct_18_34"]).round(2)
    df["brecha_pp_16_29"] = (df["esfuerzo_2026_pct_16_29"] - df["esfuerzo_2024_pct_16_29"]).round(2)

    # Equivalente oficial: quita el premium de oferta y usa el denominador canonico.
    df["esfuerzo_equivalente_2026_pct_18_34"] = (
        df["alquiler_equivalente_2026_eur_mes"] * 12
        / df["renta_joven_estimada_18_34"] * 100
    ).round(2)
    df["brecha_equivalente_pp_18_34"] = (
        df["esfuerzo_equivalente_2026_pct_18_34"] - df["esfuerzo_2024_pct_18_34"]
    ).round(2)

    df["ratio_precio_anuncio_vs_oficial"] = (
        df["precio_mediana_anuncio_2026_eur_mes"] / df["cuantia_media_eur_mes_mediana"]
    ).round(3)

    def _direccion(v: float) -> str:
        if v > 0:
            return "aumenta"
        if v < 0:
            return "disminuye"
        return "estable"

    df["direccion_cambio"] = df["brecha_pp_18_34"].map(_direccion)
    df["tipo_diferencia"] = "nivel_oferta_vs_registrado"
    df["vintage_numerador"] = 2026
    df["vintage_denominador"] = 2024
    df["caveat"] = CAVEAT

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df_out = df[[
        "codigo_ine", "nombre_canonico", "territorio",
        "esfuerzo_2024_pct_18_34", "esfuerzo_2024_pct_16_29",
        "esfuerzo_2026_pct_18_34", "esfuerzo_2026_pct_16_29",
        "brecha_pp_18_34", "brecha_pp_16_29", "direccion_cambio",
        "esfuerzo_equivalente_2026_pct_18_34", "brecha_equivalente_pp_18_34",
        "ratio_precio_anuncio_vs_oficial", "k_aplicado", "origen_k",
        "alquiler_equivalente_2026_eur_mes",
        "n_anuncios_2026", "ic95_lo_pct_18_34", "ic95_hi_pct_18_34",
        "esfuerzo_sin_ajuste_pct_18_34", "tipo_diferencia",
        "vintage_numerador", "vintage_denominador", "caveat",
    ]].sort_values("codigo_ine").reset_index(drop=True)
    df_out.to_csv(OUT, index=False, encoding="utf-8-sig")

    n_eq = int(df_out["esfuerzo_equivalente_2026_pct_18_34"].notna().sum())
    print(
        f"OK: {OUT.name} ({len(df_out)} municipios con datos en 2024 y 2026; "
        f"{n_eq} con equivalente oficial calibrado)"
    )
    print(
        f"   brecha nivel 2026-2024 mediana: {df_out['brecha_pp_18_34'].median():.2f} pp | "
        f"equivalente calibrado mediana: {df_out['brecha_equivalente_pp_18_34'].median():.2f} pp"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
