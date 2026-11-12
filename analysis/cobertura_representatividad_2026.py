"""Mide cobertura y representatividad de la capa 2026.

La capa 2026 no cubre los 252 municipios: cubre los que tienen anuncio. Contar
municipios (50/252) infravalora la cobertura; lo relevante es cuanta poblacion
joven vive en ellos y que sesgo tiene la muestra (tamano de vivienda, precio/m2).

Lee:
  - data/procesado/esfuerzo_mercado_2026.csv
  - data/procesado/dim_municipios_enriquecido.csv
  - data/procesado/poblacion_joven_municipal.csv
  - data/procesado/anuncios_vivienda_residencial_filtrado.csv (via _anuncios_2026)

Guarda:
  - data/resultados/cobertura_representatividad_2026.csv  (formato largo)

NO toca raw ni el esfuerzo canonico 2024.

Uso:
    python analysis/cobertura_representatividad_2026.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "transform"))
from _anuncios_2026 import cargar_anuncios_2026  # noqa: E402

PROC = PROJECT_ROOT / "data" / "procesado"
RES = PROJECT_ROOT / "data" / "resultados"
MERCADO_2026 = PROC / "esfuerzo_mercado_2026.csv"
DIM = PROC / "dim_municipios_enriquecido.csv"
POB = PROC / "poblacion_joven_municipal.csv"
# Capa de analisis (gold), no silver.
OUT = RES / "cobertura_representatividad_2026.csv"


def main() -> int:
    for ruta in (MERCADO_2026, DIM, POB):
        if not ruta.exists():
            print(f"Falta {ruta.name}.")
            return 1

    m26 = pd.read_csv(MERCADO_2026, dtype=str, encoding="utf-8-sig")
    m26["codigo_ine"] = m26["codigo_ine"].astype(str).str.zfill(5)
    for col in ["n_anuncios_2026", "esfuerzo_mercado_2026_pct_18_34",
                "precio_mediana_anuncio_2026_eur_mes",
                "mediana_m2_winsorizada_2026_eur_m2"]:
        m26[col] = pd.to_numeric(m26[col], errors="coerce")

    dim = pd.read_csv(DIM, dtype=str, encoding="utf-8-sig")
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    for col in ["superficie_media_m2_media", "renta_media_eur_m2_media"]:
        dim[col] = pd.to_numeric(dim.get(col), errors="coerce")

    pob = pd.read_csv(POB, dtype=str, encoding="utf-8-sig")
    pob["codigo_ine"] = pob["codigo_ine"].astype(str).str.zfill(5)
    pob["pob1834"] = pd.to_numeric(pob.get("poblacion_18_34_est"), errors="coerce")

    ads, meta = cargar_anuncios_2026()
    ads = ads[ads["anuncio_valido"]]

    df = dim[["codigo_ine", "nombre_canonico", "territorio",
              "superficie_media_m2_media", "renta_media_eur_m2_media"]].merge(
        m26[["codigo_ine", "n_anuncios_2026", "esfuerzo_mercado_2026_pct_18_34",
             "precio_mediana_anuncio_2026_eur_mes",
             "mediana_m2_winsorizada_2026_eur_m2"]],
        on="codigo_ine", how="left",
    ).merge(pob[["codigo_ine", "pob1834"]], on="codigo_ine", how="left")

    df["n_anuncios_2026"] = df["n_anuncios_2026"].fillna(0)
    con_dato = df[df["n_anuncios_2026"] > 0]

    pob_total = float(df["pob1834"].sum())
    pob_cubierta = float(con_dato["pob1834"].sum())
    n_mun_total = len(df)
    n_mun_dato = len(con_dato)
    n_ads = int(df["n_anuncios_2026"].sum())

    filas: list[dict] = []

    def add(seccion: str, metrica: str, valor, unidad: str, n=None) -> None:
        filas.append({"seccion": seccion, "metrica": metrica,
                      "valor": valor, "unidad": unidad, "n": n})

    add("cobertura", "municipios_con_dato", n_mun_dato, "municipios", n_mun_total)
    add("cobertura", "municipios_sin_dato", n_mun_total - n_mun_dato, "municipios", n_mun_total)
    add("cobertura", "pct_municipios_cubiertos", round(n_mun_dato / n_mun_total * 100, 2), "%", n_mun_total)
    add("cobertura", "poblacion_18_34_cubierta", int(pob_cubierta), "personas", int(pob_total))
    add("cobertura", "pct_poblacion_18_34_cubierta", round(pob_cubierta / pob_total * 100, 2), "%", int(pob_total))
    add("cobertura", "anuncios_usados", n_ads, "anuncios", n_ads)
    add("cobertura", "anuncios_excluidos_calidad", meta["n_excluidos_calidad"], "anuncios", meta["n_con_precio"])

    for k in (1, 5, 10, 30):
        sub = con_dato[con_dato["n_anuncios_2026"] >= k]
        add("muestra", f"municipios_con_n_mayor_igual_{k}", len(sub), "municipios", n_mun_dato)
        add("muestra", f"pct_anuncios_en_municipios_n_mayor_igual_{k}",
            round(sub["n_anuncios_2026"].sum() / n_ads * 100, 2), "%", n_ads)

    add("sesgo", "superficie_mediana_anuncios", round(float(ads["superficie_m2"].median()), 1), "m2", len(ads))
    add("sesgo", "superficie_mediana_oficial_2024",
        round(float(dim["superficie_media_m2_media"].median()), 1), "m2", int(dim["superficie_media_m2_media"].notna().sum()))
    add("sesgo", "precio_m2_mediano_anuncios", round(float(ads["precio_m2"].median()), 2), "eur/m2/mes", int(ads["precio_m2"].notna().sum()))
    add("sesgo", "precio_m2_mediano_oficial_2024",
        round(float(dim["renta_media_eur_m2_media"].median()), 2), "eur/m2/mes", int(dim["renta_media_eur_m2_media"].notna().sum()))

    ambos = con_dato.dropna(subset=["mediana_m2_winsorizada_2026_eur_m2", "renta_media_eur_m2_media"])
    ambos = ambos[ambos["renta_media_eur_m2_media"] > 0]
    ratio_m2 = ambos["mediana_m2_winsorizada_2026_eur_m2"] / ambos["renta_media_eur_m2_media"]
    add("sesgo", "ratio_m2_anuncio_vs_oficial_mediana", round(float(ratio_m2.median()), 3), "ratio", len(ambos))

    for terr, grupo in con_dato.groupby("territorio"):
        add("territorio", f"municipios_con_dato_{terr}", len(grupo), "municipios", n_mun_dato)
        add("territorio", f"pct_poblacion_18_34_cubierta_{terr}",
            round(float(grupo["pob1834"].sum())
                  / float(df.loc[df["territorio"] == terr, "pob1834"].sum()) * 100, 2), "%", None)

    out = pd.DataFrame(filas, columns=["seccion", "metrica", "valor", "unidad", "n"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")

    print(f"OK: {OUT.name} ({len(out)} metricas)")
    print(f"   cobertura: {n_mun_dato}/{n_mun_total} municipios = "
          f"{pob_cubierta / pob_total * 100:.1f}% de la poblacion 18-34")
    print(f"   muestra: {(con_dato['n_anuncios_2026'] >= 10).sum()} municipios con n>=10 "
          f"({con_dato.loc[con_dato['n_anuncios_2026'] >= 10, 'n_anuncios_2026'].sum() / n_ads * 100:.1f}% de los anuncios)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
