"""Contrasta el alquiler oficial 2024 (Eustat) con una fuente fiscal independiente.

SERPAVI/MIVAU publica renta de alquiler por m2 y mes a partir de declaraciones
fiscales, a nivel municipal, para 2024. No sustituye a Eustat: sirve para auditar
el ancla 2024 y, sobre todo, para ver si los 93 municipios sin alquiler oficial
(imputados por comarca) se comportan distinto de los 159 oficiales.

Lee:
  - data/raw/serpavi_renta_municipal.csv
  - data/procesado/dim_municipios_enriquecido.csv

Guarda:
  - data/resultados/validacion_alquiler_2024_serpavi.csv

NO toca raw ni modifica el alquiler canonico.

Uso:
    python analysis/validar_alquiler_serpavi.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
PROC = PROJECT_ROOT / "data" / "procesado"
RES = PROJECT_ROOT / "data" / "resultados"

SERPAVI = RAW / "serpavi_renta_municipal.csv"
DIM = PROC / "dim_municipios_enriquecido.csv"
# Capa de analisis (gold), no silver.
OUT = RES / "validacion_alquiler_2024_serpavi.csv"

TOLERANCIA = 0.25  # +-25 % se considera concordante


def main() -> int:
    for ruta in (SERPAVI, DIM):
        if not ruta.exists():
            print(f"Falta {ruta.name}.")
            return 1

    serp = pd.read_csv(SERPAVI, dtype=str, encoding="utf-8-sig")
    serp["codigo_ine"] = serp["codigo_ine"].astype(str).str.zfill(5)
    for col in ["renta_m2_mes_eur", "n_declaraciones", "renta_m2_p25", "renta_m2_p75"]:
        serp[col] = pd.to_numeric(serp.get(col), errors="coerce")

    dim = pd.read_csv(DIM, dtype=str, encoding="utf-8-sig")
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    dim["eustat_eur_m2"] = pd.to_numeric(dim.get("renta_media_eur_m2_media"), errors="coerce")
    dim["cuantia_actual_eur_mes"] = pd.to_numeric(dim.get("cuantia_media_eur_mes_mediana"), errors="coerce")
    dim["superficie_media_m2"] = pd.to_numeric(dim.get("superficie_media_m2_media"), errors="coerce")
    dim["tiene_alquiler_oficial"] = dim["tiene_alquiler_oficial"].astype(str).str.lower().eq("true")

    df = dim[["codigo_ine", "nombre_canonico", "territorio", "tiene_alquiler_oficial",
              "eustat_eur_m2", "cuantia_actual_eur_mes", "superficie_media_m2"]].merge(
        serp[["codigo_ine", "renta_m2_mes_eur", "n_declaraciones",
              "renta_m2_p25", "renta_m2_p75", "metodo"]],
        on="codigo_ine", how="left",
    ).rename(columns={"metodo": "metodo_serpavi"})

    df["ratio_serpavi_eustat"] = (
        df["renta_m2_mes_eur"] / df["eustat_eur_m2"]
    ).round(3)
    df["diff_eur_m2"] = (df["renta_m2_mes_eur"] - df["eustat_eur_m2"]).round(2)
    df["flag_concordante"] = (
        df["ratio_serpavi_eustat"].notna()
        & (df["ratio_serpavi_eustat"] - 1).abs().le(TOLERANCIA)
    )

    # Auditoria de las imputaciones comarcales: cuantia implicita = m2 fiscal x
    # superficie media municipal, comparada con la cuantia que usa el estudio.
    df["cuantia_implicita_serpavi_eur_mes"] = (
        df["renta_m2_mes_eur"] * df["superficie_media_m2"]
    ).round(2)
    df["ratio_cuantia_serpavi_estudio"] = (
        df["cuantia_implicita_serpavi_eur_mes"] / df["cuantia_actual_eur_mes"]
    ).round(3)

    out = df.rename(columns={
        "renta_m2_mes_eur": "serpavi_eur_m2",
        "eustat_eur_m2": "eustat_eur_m2",
    })[[
        "codigo_ine", "nombre_canonico", "territorio", "tiene_alquiler_oficial",
        "eustat_eur_m2", "serpavi_eur_m2", "diff_eur_m2", "ratio_serpavi_eustat",
        "n_declaraciones", "renta_m2_p25", "renta_m2_p75", "metodo_serpavi",
        "flag_concordante",
        "cuantia_actual_eur_mes", "cuantia_implicita_serpavi_eur_mes",
        "ratio_cuantia_serpavi_estudio",
    ]].sort_values("codigo_ine").reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")

    # Solo declaraciones 2024: `locf_2022` es otro anio y `sin_dato` no aporta.
    ambos = out[(out["metodo_serpavi"] == "declaraciones_2024")].dropna(
        subset=["eustat_eur_m2", "serpavi_eur_m2"])
    n_sin = int((out["metodo_serpavi"] == "sin_dato").sum())
    n_locf = int((out["metodo_serpavi"] == "locf_2022").sum())
    print(f"OK: {OUT.name} ({len(out)} filas, {len(ambos)} comparables 2024; "
          f"SERPAVI sin dato en {n_sin}, locf_2022 en {n_locf})")
    if len(ambos):
        # Spearman = Pearson sobre rangos; evita scipy (no esta en el venv del CI).
        spearman = ambos["eustat_eur_m2"].rank().corr(ambos["serpavi_eur_m2"].rank())
        print(f"   ratio SERPAVI/Eustat mediana: {ambos['ratio_serpavi_eustat'].median():.3f} | "
              f"Spearman: {spearman:.3f} | concordantes +-{TOLERANCIA:.0%}: "
              f"{ambos['flag_concordante'].mean() * 100:.1f}%")
        for etiqueta, grupo in ambos.groupby("tiene_alquiler_oficial"):
            nombre = "oficial (159)" if etiqueta else "imputado comarcal (93)"
            print(f"   {nombre:<24} n={len(grupo):>3} ratio mediana={grupo['ratio_serpavi_eustat'].median():.3f} "
                  f"concordantes={grupo['flag_concordante'].mean() * 100:.1f}%")

    # Contraste de la cuantia usada (oficial o imputada) contra la implicita fiscal.
    cuantia = out.dropna(subset=["cuantia_actual_eur_mes", "cuantia_implicita_serpavi_eur_mes"])
    if len(cuantia):
        print(f"   cuantia: {len(cuantia)} municipios con ambas; ratio mediana="
              f"{cuantia['ratio_cuantia_serpavi_estudio'].median():.3f}")
        for etiqueta, grupo in cuantia.groupby("tiene_alquiler_oficial"):
            nombre = "oficial" if etiqueta else "imputado comarcal"
            print(f"   cuantia {nombre:<18} n={len(grupo):>3} ratio mediana="
                  f"{grupo['ratio_cuantia_serpavi_estudio'].median():.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
