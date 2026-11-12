"""Calibra el premium oferta-vs-registrado y elige el factor k por municipio.

El precio de anuncio 2026 y el alquiler registrado 2024 no son el mismo concepto.
Este paso estima, alli donde hay ambos, el factor

    k = alquiler_oficial_2024 / precio_anuncio_2026

para poder expresar el anuncio en "equivalente oficial" y separar nivel de
movimiento. No es una medicion oficial: es un supuesto declarado.

Regla de estimacion (anti-circularidad):
  - k municipal si el municipio tiene n >= 5 anuncios;
  - si no, k del area funcional calculado con **leave-one-out** (se excluye el
    propio municipio del calculo), para no usar la misma observacion dos veces;
  - si el area no tiene ningun otro municipio con k, queda no aplicable.

Lee:
  - data/procesado/esfuerzo_mercado_2026.csv
  - data/procesado/dim_municipios_enriquecido.csv
  - data/raw/areas_funcionales_municipios.csv

Guarda:
  - data/resultados/premium_oferta_2026.csv

NO toca raw ni el esfuerzo canonico 2024.

Uso:
    python analysis/calibrar_premium_oferta.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
PROC = PROJECT_ROOT / "data" / "procesado"
RES = PROJECT_ROOT / "data" / "resultados"

MERCADO_2026 = PROC / "esfuerzo_mercado_2026.csv"
DIM = PROC / "dim_municipios_enriquecido.csv"
AREAS = RAW / "areas_funcionales_municipios.csv"
# Capa de analisis (gold), no silver: data/procesado es solo transform.
OUT = RES / "premium_oferta_2026.csv"

K_MIN_N = 5  # muestra minima para estimar el premium con el propio municipio


def _mediana(valores: list[float]) -> float:
    vals = [v for v in valores if v == v]
    return float(np.median(vals)) if vals else float("nan")


def main() -> int:
    for ruta in (MERCADO_2026, DIM, AREAS):
        if not ruta.exists():
            print(f"Falta {ruta.name}.")
            return 1

    m26 = pd.read_csv(MERCADO_2026, dtype=str, encoding="utf-8-sig")
    m26["codigo_ine"] = m26["codigo_ine"].astype(str).str.zfill(5)
    for col in ["n_anuncios_2026", "precio_mediana_anuncio_2026_eur_mes",
                "mediana_m2_winsorizada_2026_eur_m2"]:
        m26[col] = pd.to_numeric(m26[col], errors="coerce")

    dim = pd.read_csv(DIM, dtype=str, encoding="utf-8-sig")
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    for col in ["cuantia_media_eur_mes_mediana", "renta_media_eur_m2_media"]:
        dim[col] = pd.to_numeric(dim.get(col), errors="coerce")

    areas = pd.read_csv(AREAS, dtype=str, encoding="utf-8-sig")
    areas["codigo_ine"] = areas["codigo_ine"].astype(str).str.zfill(5)

    df = m26[["codigo_ine", "nombre_canonico", "n_anuncios_2026",
              "precio_mediana_anuncio_2026_eur_mes",
              "mediana_m2_winsorizada_2026_eur_m2"]].merge(
        dim[["codigo_ine", "cuantia_media_eur_mes_mediana", "renta_media_eur_m2_media"]],
        on="codigo_ine", how="left",
    ).merge(
        areas[["codigo_ine", "area_funcional", "cod_area_funcional"]],
        on="codigo_ine", how="left",
    )

    con_ambos = df["precio_mediana_anuncio_2026_eur_mes"].notna() & df[
        "cuantia_media_eur_mes_mediana"].notna()
    df["k_municipal"] = np.where(
        con_ambos & (df["n_anuncios_2026"] >= K_MIN_N),
        df["cuantia_media_eur_mes_mediana"] / df["precio_mediana_anuncio_2026_eur_mes"],
        np.nan,
    )
    df["k_m2_municipal"] = np.where(
        con_ambos & (df["n_anuncios_2026"] >= K_MIN_N)
        & df["mediana_m2_winsorizada_2026_eur_m2"].notna()
        & (df["mediana_m2_winsorizada_2026_eur_m2"] > 0),
        df["renta_media_eur_m2_media"] / df["mediana_m2_winsorizada_2026_eur_m2"],
        np.nan,
    )

    # k por area funcional y leave-one-out.
    k_area, k_area_loo = [], []
    for _, row in df.iterrows():
        grupo = df[df["cod_area_funcional"] == row["cod_area_funcional"]]
        valores = grupo["k_municipal"].dropna().tolist()
        propios = grupo.loc[grupo["codigo_ine"] == row["codigo_ine"], "k_municipal"]
        propios = propios.dropna().tolist()
        k_area.append(_mediana(valores))
        resto = list(valores)
        for v in propios:
            resto.remove(v)
        k_area_loo.append(_mediana(resto))

    df["k_area"] = k_area
    df["k_area_loo"] = k_area_loo

    def _elegir(row) -> tuple[float, str]:
        if row["k_municipal"] == row["k_municipal"]:
            return row["k_municipal"], "municipal"
        if row["k_area_loo"] == row["k_area_loo"]:
            return row["k_area_loo"], "area_loo"
        return float("nan"), "no_aplicable"

    elegido = df.apply(_elegir, axis=1)
    df["k_aplicado"] = [e[0] for e in elegido]
    df["origen_k"] = [e[1] for e in elegido]

    df["alquiler_equivalente_2026_eur_mes"] = (
        df["precio_mediana_anuncio_2026_eur_mes"] * df["k_aplicado"]
    ).round(2)

    cols = [
        "codigo_ine", "nombre_canonico", "area_funcional", "cod_area_funcional",
        "n_anuncios_2026", "precio_mediana_anuncio_2026_eur_mes",
        "alquiler_oficial_2024_eur_mes", "k_municipal", "k_m2_municipal",
        "k_area", "k_area_loo", "k_aplicado", "origen_k",
        "alquiler_equivalente_2026_eur_mes",
    ]
    out = df.rename(columns={
        "cuantia_media_eur_mes_mediana": "alquiler_oficial_2024_eur_mes",
        "mediana_m2_winsorizada_2026_eur_m2": "mediana_m2_winsorizada_2026_eur_m2",
    })[cols].sort_values("codigo_ine").reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")

    n_mun = int((out["origen_k"] == "municipal").sum())
    n_area = int((out["origen_k"] == "area_loo").sum())
    n_na = int((out["origen_k"] == "no_aplicable").sum())
    print(
        f"OK: {OUT.name} ({len(out)} filas; k municipal {n_mun}, area_loo {n_area}, "
        f"no aplicable {n_na}; k mediana municipal="
        f"{out['k_municipal'].median():.3f})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
